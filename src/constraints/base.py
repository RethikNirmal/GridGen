"""Base classes for connection constraints in the grid system."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.grid import Grid
    from src.models.point import Point


class ConnectionConstraint(ABC):
    """Abstract base class for connection constraints.

    This allows for flexible validation of connections between points
    in the grid. Different constraints can be easily added, removed,
    or configured independently.
    """

    def __init__(self, name: str, enabled: bool = True) -> None:
        """Initialize the constraint.

        Args:
            name: Human-readable name for this constraint
            enabled: Whether this constraint is currently active
        """
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def validate(self, grid: "Grid", point1: "Point", point2: "Point") -> bool:
        """Validate whether a connection between two points is allowed.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if the connection is valid according to this constraint,
            False otherwise
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of this constraint.

        Returns:
            Description of what this constraint validates
        """
        pass

    def enable(self) -> None:
        """Enable this constraint."""
        self.enabled = True

    def disable(self) -> None:
        """Disable this constraint."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if this constraint is enabled.

        Returns:
            True if constraint is enabled, False otherwise
        """
        return self.enabled

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.__class__.__name__}(name='{self.name}', {status})"


class ValidationResult:
    """Result of a constraint validation operation."""

    def __init__(self, is_valid: bool, constraint_name: str, reason: str = "") -> None:
        """Initialize validation result.

        Args:
            is_valid: Whether the validation passed
            constraint_name: Name of the constraint that was checked
            reason: Optional reason for failure
        """
        self.is_valid = is_valid
        self.constraint_name = constraint_name
        self.reason = reason

    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean contexts."""
        return self.is_valid

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "PASS" if self.is_valid else "FAIL"
        reason_part = f", reason: {self.reason}" if self.reason else ""
        return f"ValidationResult({status}, {self.constraint_name}{reason_part})"
