"""Distance-based constraints for connection validation."""

import math
from typing import TYPE_CHECKING

from src.constraints.base import ConnectionConstraint

if TYPE_CHECKING:
    from src.models.grid import Grid
    from src.models.point import Point


class MaxDistanceConstraint(ConnectionConstraint):
    """Constraint that limits the maximum distance between connected points.

    This constraint can be used to prevent very long connections
    that might visually clutter the grid or violate design requirements.
    """

    def __init__(self, max_distance: float = 2.0, enabled: bool = False) -> None:
        """Initialize the maximum distance constraint.

        Args:
            max_distance: Maximum allowed distance between points
            enabled: Whether this constraint is initially enabled
        """
        super().__init__("Max Distance", enabled)
        self.max_distance = max_distance

    def validate(self, grid: "Grid", point1: "Point", point2: "Point") -> bool:
        """Validate that connection distance is within limit.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if distance is within the maximum limit
        """
        if not self.enabled:
            return True

        distance = self._calculate_distance(point1, point2)
        return distance <= self.max_distance

    def get_description(self) -> str:
        """Get description of this constraint.

        Returns:
            Human-readable description
        """
        return f"limits connections to maximum distance of {self.max_distance}"

    def set_max_distance(self, max_distance: float) -> None:
        """Update the maximum distance limit.

        Args:
            max_distance: New maximum distance limit
        """
        self.max_distance = max_distance

    def get_max_distance(self) -> float:
        """Get the current maximum distance limit.

        Returns:
            Current maximum distance
        """
        return self.max_distance

    def _calculate_distance(self, point1: "Point", point2: "Point") -> float:
        """Calculate Euclidean distance between two points.

        Args:
            point1: First point
            point2: Second point

        Returns:
            Euclidean distance between the points
        """
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        return math.sqrt(dx * dx + dy * dy)

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "enabled" if self.enabled else "disabled"
        return f"MaxDistanceConstraint({status}, max_dist={self.max_distance})"


class MinDistanceConstraint(ConnectionConstraint):
    """Constraint that enforces a minimum distance between connected points.

    This constraint can prevent very short connections that might not
    be visually distinct or meaningful.
    """

    def __init__(self, min_distance: float = 1.0, enabled: bool = False) -> None:
        """Initialize the minimum distance constraint.

        Args:
            min_distance: Minimum required distance between points
            enabled: Whether this constraint is initially enabled
        """
        super().__init__("Min Distance", enabled)
        self.min_distance = min_distance

    def validate(self, grid: "Grid", point1: "Point", point2: "Point") -> bool:
        """Validate that connection distance meets minimum requirement.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if distance meets the minimum requirement
        """
        if not self.enabled:
            return True

        distance = self._calculate_distance(point1, point2)
        return distance >= self.min_distance

    def get_description(self) -> str:
        """Get description of this constraint.

        Returns:
            Human-readable description
        """
        return f"requires connections to be at least distance {self.min_distance}"

    def set_min_distance(self, min_distance: float) -> None:
        """Update the minimum distance requirement.

        Args:
            min_distance: New minimum distance requirement
        """
        self.min_distance = min_distance

    def get_min_distance(self) -> float:
        """Get the current minimum distance requirement.

        Returns:
            Current minimum distance
        """
        return self.min_distance

    def _calculate_distance(self, point1: "Point", point2: "Point") -> float:
        """Calculate Euclidean distance between two points.

        Args:
            point1: First point
            point2: Second point

        Returns:
            Euclidean distance between the points
        """
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        return math.sqrt(dx * dx + dy * dy)

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "enabled" if self.enabled else "disabled"
        return f"MinDistanceConstraint({status}, min_dist={self.min_distance})"
