"""Constraint manager for handling multiple connection constraints."""

from typing import TYPE_CHECKING, Dict, List

from src.constraints.base import ConnectionConstraint, ValidationResult

if TYPE_CHECKING:
    from src.models.grid import Grid
    from src.models.point import Point


class ConstraintManager:
    """Manages multiple connection constraints for the grid system.

    This class provides a flexible way to add, remove, enable, and disable
    different types of connection constraints. It acts as a central
    coordinator for all constraint validation.
    """

    def __init__(self) -> None:
        """Initialize the constraint manager."""
        self._constraints: Dict[str, ConnectionConstraint] = {}
        self._constraint_order: List[str] = []

    def add_constraint(self, constraint: ConnectionConstraint) -> None:
        """Add a constraint to the manager.

        Args:
            constraint: The constraint to add

        Raises:
            ValueError: If a constraint with the same name already exists
        """
        if constraint.name in self._constraints:
            raise ValueError(f"Constraint '{constraint.name}' already exists")

        self._constraints[constraint.name] = constraint
        self._constraint_order.append(constraint.name)

    def remove_constraint(self, name: str) -> bool:
        """Remove a constraint by name.

        Args:
            name: Name of the constraint to remove

        Returns:
            True if constraint was removed, False if it didn't exist
        """
        if name not in self._constraints:
            return False

        del self._constraints[name]
        self._constraint_order.remove(name)
        return True

    def get_constraint(self, name: str) -> ConnectionConstraint:
        """Get a constraint by name.

        Args:
            name: Name of the constraint

        Returns:
            The constraint object

        Raises:
            KeyError: If constraint doesn't exist
        """
        return self._constraints[name]

    def enable_constraint(self, name: str) -> bool:
        """Enable a constraint by name.

        Args:
            name: Name of the constraint to enable

        Returns:
            True if constraint was enabled, False if it didn't exist
        """
        if name not in self._constraints:
            return False

        self._constraints[name].enable()
        return True

    def disable_constraint(self, name: str) -> bool:
        """Disable a constraint by name.

        Args:
            name: Name of the constraint to disable

        Returns:
            True if constraint was disabled, False if it didn't exist
        """
        if name not in self._constraints:
            return False

        self._constraints[name].disable()
        return True

    def is_constraint_enabled(self, name: str) -> bool:
        """Check if a constraint is enabled.

        Args:
            name: Name of the constraint

        Returns:
            True if constraint exists and is enabled, False otherwise
        """
        if name not in self._constraints:
            return False

        return self._constraints[name].is_enabled()

    def validate_connection(
        self, grid: "Grid", point1: "Point", point2: "Point"
    ) -> ValidationResult:
        """Validate a connection against all enabled constraints.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            ValidationResult indicating if connection is valid.
            If any constraint fails, returns the first failure.
        """
        # Check each constraint in order
        for constraint_name in self._constraint_order:
            constraint = self._constraints[constraint_name]

            if not constraint.is_enabled():
                continue

            try:
                is_valid = constraint.validate(grid, point1, point2)
                if not is_valid:
                    return ValidationResult(
                        is_valid=False,
                        constraint_name=constraint_name,
                        reason=f"Connection violates {constraint.get_description()}",
                    )
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    constraint_name=constraint_name,
                    reason=f"Constraint validation error: {str(e)}",
                )

        return ValidationResult(
            is_valid=True, constraint_name="all", reason="All constraints passed"
        )

    def validate_connection_fast(
        self, grid: "Grid", point1: "Point", point2: "Point"
    ) -> bool:
        """Fast validation that returns boolean result only.

        Args:
            grid: The grid containing the points
            point1: First point of the proposed connection
            point2: Second point of the proposed connection

        Returns:
            True if connection is valid, False otherwise
        """
        result = self.validate_connection(grid, point1, point2)
        return result.is_valid

    def get_enabled_constraints(self) -> List[ConnectionConstraint]:
        """Get all currently enabled constraints.

        Returns:
            List of enabled constraints in order
        """
        return [
            self._constraints[name]
            for name in self._constraint_order
            if self._constraints[name].is_enabled()
        ]

    def get_all_constraints(self) -> List[ConnectionConstraint]:
        """Get all constraints (enabled and disabled).

        Returns:
            List of all constraints in order
        """
        return [self._constraints[name] for name in self._constraint_order]

    def get_constraint_names(self) -> List[str]:
        """Get names of all constraints.

        Returns:
            List of constraint names in order
        """
        return self._constraint_order.copy()

    def clear_constraints(self) -> None:
        """Remove all constraints."""
        self._constraints.clear()
        self._constraint_order.clear()

    def get_constraint_count(self) -> int:
        """Get total number of constraints.

        Returns:
            Number of constraints (enabled and disabled)
        """
        return len(self._constraints)

    def get_enabled_constraint_count(self) -> int:
        """Get number of enabled constraints.

        Returns:
            Number of enabled constraints
        """
        return sum(
            1 for constraint in self._constraints.values() if constraint.is_enabled()
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        enabled_count = self.get_enabled_constraint_count()
        total_count = self.get_constraint_count()
        return f"ConstraintManager({enabled_count}/{total_count} constraints enabled)"
