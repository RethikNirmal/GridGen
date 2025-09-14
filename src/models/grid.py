"""Grid class representing the N×M grid of points."""

from typing import List, Optional

from src.constraints.manager import ConstraintManager
from src.constraints.non_crossing import NonCrossingConstraint
from src.models.point import Point


class Grid:
    """Represents an N×M grid of points for the chain connection game."""

    def __init__(self, rows: int, cols: int) -> None:
        """Initialize a grid with the specified dimensions.

        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid

        Raises:
            ValueError: If rows or cols are less than 1
        """
        if rows < 1 or cols < 1:
            raise ValueError("Grid dimensions must be at least 1x1")

        self.rows = rows
        self.cols = cols
        self.points = [[Point(i, j) for j in range(cols)] for i in range(rows)]

        # Initialize constraint system
        self.constraint_manager = ConstraintManager()
        self._setup_default_constraints()

    def get_point(self, x: int, y: int) -> Optional[Point]:
        """Get the point at the specified coordinates.

        Args:
            x: Row coordinate
            y: Column coordinate

        Returns:
            The Point at (x, y) or None if coordinates are invalid
        """
        if self.is_valid_position(x, y):
            return self.points[x][y]
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if the given coordinates are within the grid bounds.

        Args:
            x: Row coordinate
            y: Column coordinate

        Returns:
            True if coordinates are valid, False otherwise
        """
        return 0 <= x < self.rows and 0 <= y < self.cols

    def get_neighbors(self, point: Point) -> List[Point]:
        """Get all valid neighboring points (8-directional adjacency).

        Args:
            point: The point to find neighbors for

        Returns:
            List of neighboring points
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor_x = point.x + dx
                neighbor_y = point.y + dy
                if self.is_valid_position(neighbor_x, neighbor_y):
                    neighbors.append(self.points[neighbor_x][neighbor_y])
        return neighbors

    def get_all_points(self) -> List[Point]:
        """Get all points in the grid as a flat list.

        Returns:
            List of all points in the grid
        """
        points = []
        for row in self.points:
            points.extend(row)
        return points

    def get_unconnected_points(self) -> List[Point]:
        """Get all points that are not yet connected to any chain.

        Returns:
            List of unconnected points
        """
        return [point for point in self.get_all_points() if not point.connected]

    def validate_connection(self, point1: Point, point2: Point) -> bool:
        """Validate if a connection between two points is allowed.

        Args:
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if connection is valid according to all enabled constraints
        """
        return self.constraint_manager.validate_connection_fast(self, point1, point2)

    def add_connection(self, point1: Point, point2: Point) -> bool:
        """Add a connection between two points with constraint validation.

        Args:
            point1: First point of the connection
            point2: Second point of the connection

        Returns:
            True if connection was successfully added
        """
        # Validate constraints first
        if not self.validate_connection(point1, point2):
            return False

        # Add the direct connection
        try:
            success = point1.add_direct_connection(point2)
            if success:
                # Notify constraint system about the new connection
                self._notify_connection_added(point1, point2)
            return success
        except ValueError:
            return False

    def remove_connection(self, point1: Point, point2: Point) -> bool:
        """Remove a connection between two points.

        Args:
            point1: First point of the connection
            point2: Second point of the connection

        Returns:
            True if connection was successfully removed
        """
        success = point1.remove_direct_connection(point2)
        if success:
            # Notify constraint system about the removed connection
            self._notify_connection_removed(point1, point2)
        return success

    def _setup_default_constraints(self) -> None:
        """Set up default constraints for the grid."""
        # Add non-crossing constraint (enabled by default)
        non_crossing = NonCrossingConstraint(enabled=True)
        self.constraint_manager.add_constraint(non_crossing)

    def _notify_connection_added(self, point1: Point, point2: Point) -> None:
        """Notify constraint system that a connection was added.

        Args:
            point1: First point of the connection
            point2: Second point of the connection
        """
        # Update non-crossing constraint tracking
        for constraint in self.constraint_manager.get_all_constraints():
            if isinstance(constraint, NonCrossingConstraint):
                constraint.add_connection(point1, point2)

    def _notify_connection_removed(self, point1: Point, point2: Point) -> None:
        """Notify constraint system that a connection was removed.

        Args:
            point1: First point of the connection
            point2: Second point of the connection
        """
        # Update non-crossing constraint tracking
        for constraint in self.constraint_manager.get_all_constraints():
            if isinstance(constraint, NonCrossingConstraint):
                constraint.remove_connection(point1, point2)

    def reset_connections(self) -> None:
        """Reset all points to unconnected state."""
        for point in self.get_all_points():
            point.reset_connections()

        # Clear constraint tracking
        for constraint in self.constraint_manager.get_all_constraints():
            if isinstance(constraint, NonCrossingConstraint):
                constraint.clear_connections()

    def get_connected_points(self) -> List[Point]:
        """Get all points that are connected to a chain.

        Returns:
            List of connected points
        """
        return [point for point in self.get_all_points() if point.connected]

    @property
    def total_points(self) -> int:
        """Get the total number of points in the grid."""
        return self.rows * self.cols

    @property
    def connection_progress(self) -> float:
        """Get the percentage of points that are connected.

        Returns:
            Percentage (0.0 to 1.0) of connected points
        """
        connected_count = len(self.get_connected_points())
        return connected_count / self.total_points if self.total_points > 0 else 0.0

    def __repr__(self) -> str:
        """String representation for debugging."""
        connected_count = len(self.get_connected_points())
        return (
            f"Grid({self.rows}x{self.cols}, "
            f"{connected_count}/{self.total_points} connected)"
        )
