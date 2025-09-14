"""Non-crossing constraint implementation for connection validation."""

from typing import TYPE_CHECKING, Set, Tuple

from src.constraints.base import ConnectionConstraint

if TYPE_CHECKING:
    from src.models.grid import Grid
    from src.models.point import Point


class NonCrossingConstraint(ConnectionConstraint):
    """Constraint that prevents chains from crossing each other.

    This constraint ensures that no two connection line segments
    intersect geometrically, maintaining clear separation between
    different chains in the grid.
    """

    def __init__(self, enabled: bool = True) -> None:
        """Initialize the non-crossing constraint.

        Args:
            enabled: Whether this constraint is initially enabled
        """
        super().__init__("Non-Crossing", enabled)
        self._active_connections: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()

    def validate(self, grid: "Grid", point1: "Point", point2: "Point") -> bool:
        """Validate that a connection doesn't cross existing connections.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if connection doesn't cross any existing connections
        """
        if not self.enabled:
            return True

        # Convert points to coordinate tuples for comparison
        new_connection = self._normalize_connection(
            (point1.x, point1.y), (point2.x, point2.y)
        )

        # Check against all existing connections
        for existing_connection in self._active_connections:
            if self._connections_intersect(new_connection, existing_connection):
                return False

        return True

    def add_connection(self, point1: "Point", point2: "Point") -> None:
        """Register a new connection in the tracking system.

        Args:
            point1: First point of the connection
            point2: Second point of the connection
        """
        connection = self._normalize_connection(
            (point1.x, point1.y), (point2.x, point2.y)
        )
        self._active_connections.add(connection)

    def remove_connection(self, point1: "Point", point2: "Point") -> bool:
        """Remove a connection from the tracking system.

        Args:
            point1: First point of the connection
            point2: Second point of the connection

        Returns:
            True if connection was found and removed
        """
        connection = self._normalize_connection(
            (point1.x, point1.y), (point2.x, point2.y)
        )
        if connection in self._active_connections:
            self._active_connections.remove(connection)
            return True
        return False

    def clear_connections(self) -> None:
        """Clear all tracked connections."""
        self._active_connections.clear()

    def get_connection_count(self) -> int:
        """Get the number of tracked connections.

        Returns:
            Number of active connections
        """
        return len(self._active_connections)

    def get_description(self) -> str:
        """Get description of this constraint.

        Returns:
            Human-readable description
        """
        return "prevents chains from crossing each other geometrically"

    def _normalize_connection(
        self, p1: Tuple[int, int], p2: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Normalize connection so that comparison is order-independent.

        Args:
            p1: First point coordinates
            p2: Second point coordinates

        Returns:
            Normalized connection tuple with smaller point first
        """
        if p1 <= p2:
            return (p1, p2)
        else:
            return (p2, p1)

    def _connections_intersect(
        self,
        conn1: Tuple[Tuple[int, int], Tuple[int, int]],
        conn2: Tuple[Tuple[int, int], Tuple[int, int]],
    ) -> bool:
        """Check if two connections intersect.

        Args:
            conn1: First connection as ((x1,y1), (x2,y2))
            conn2: Second connection as ((x3,y3), (x4,y4))

        Returns:
            True if the connections intersect
        """
        p1, p2 = conn1
        p3, p4 = conn2

        # Skip if connections share endpoints
        if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
            return False

        # Quick bounding box check for early elimination
        if not self._bounding_boxes_overlap(p1, p2, p3, p4):
            return False

        # Full geometric intersection test
        return self._segments_intersect(p1, p2, p3, p4)

    def _bounding_boxes_overlap(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        p3: Tuple[int, int],
        p4: Tuple[int, int],
    ) -> bool:
        """Check if bounding boxes of two line segments overlap.

        Args:
            p1, p2: Endpoints of first segment
            p3, p4: Endpoints of second segment

        Returns:
            True if bounding boxes overlap
        """
        min_x1, max_x1 = min(p1[0], p2[0]), max(p1[0], p2[0])
        min_y1, max_y1 = min(p1[1], p2[1]), max(p1[1], p2[1])
        min_x2, max_x2 = min(p3[0], p4[0]), max(p3[0], p4[0])
        min_y2, max_y2 = min(p3[1], p4[1]), max(p3[1], p4[1])

        return not (
            max_x1 < min_x2 or max_x2 < min_x1 or max_y1 < min_y2 or max_y2 < min_y1
        )

    def _segments_intersect(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        p3: Tuple[int, int],
        p4: Tuple[int, int],
    ) -> bool:
        """Check if two line segments intersect using parametric equations.

        Args:
            p1, p2: Endpoints of first segment
            p3, p4: Endpoints of second segment

        Returns:
            True if segments intersect
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # Direction vectors
        dx1, dy1 = x2 - x1, y2 - y1
        dx2, dy2 = x4 - x3, y4 - y3

        # Calculate determinant
        det = dx1 * dy2 - dy1 * dx2

        # Lines are parallel (or coincident)
        if abs(det) < 1e-10:
            # Check if segments are collinear and overlapping
            return self._collinear_segments_intersect(p1, p2, p3, p4)

        # Calculate parametric intersection parameters
        dx3, dy3 = x1 - x3, y1 - y3
        t1 = (dx2 * dy3 - dy2 * dx3) / det
        t2 = (dx1 * dy3 - dy1 * dx3) / det

        # Check if intersection point is within both segments
        return 0 <= t1 <= 1 and 0 <= t2 <= 1

    def _collinear_segments_intersect(
        self,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        p3: Tuple[int, int],
        p4: Tuple[int, int],
    ) -> bool:
        """Check if two collinear segments overlap.

        Args:
            p1, p2: Endpoints of first segment
            p3, p4: Endpoints of second segment

        Returns:
            True if collinear segments overlap
        """
        # Use the coordinate with larger range for projection
        if abs(p2[0] - p1[0]) >= abs(p2[1] - p1[1]):
            # Project onto x-axis
            min1, max1 = min(p1[0], p2[0]), max(p1[0], p2[0])
            min2, max2 = min(p3[0], p4[0]), max(p3[0], p4[0])
        else:
            # Project onto y-axis
            min1, max1 = min(p1[1], p2[1]), max(p1[1], p2[1])
            min2, max2 = min(p3[1], p4[1]), max(p3[1], p4[1])

        # Check for overlap
        return max1 >= min2 and max2 >= min1

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "enabled" if self.enabled else "disabled"
        conn_count = len(self._active_connections)
        return f"NonCrossingConstraint({status}, {conn_count} connections tracked)"
