"""Point class representing a single position in the grid."""

from typing import List, Optional


class Point:
    """Represents a single point in the grid with connection state."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize a point at the given coordinates.

        Args:
            x: Row coordinate
            y: Column coordinate
        """
        self.x = x
        self.y = y
        self.connected = False
        self.chain_id: Optional[int] = None
        self.direct_connections: List["Point"] = []  # Max 2 direct connections

    def __eq__(self, other: object) -> bool:
        """Check equality based on coordinates."""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Hash based on coordinates for use in sets and dictionaries."""
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Point({self.x}, {self.y}, "
            f"connected={self.connected}, chain_id={self.chain_id}, "
            f"connections={len(self.direct_connections)})"
        )

    def distance_to(self, other: "Point") -> int:
        """Calculate Manhattan distance to another point.

        Args:
            other: The other point

        Returns:
            Manhattan distance as integer
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def is_adjacent_to(self, other: "Point") -> bool:
        """Check if this point is adjacent to another (8-directional).

        Args:
            other: The other point to check

        Returns:
            True if points are adjacent, False otherwise
        """
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0

    def can_accept_connection(self) -> bool:
        """Check if this point can accept another direct connection.

        Each point can have at most 2 direct connections for linear chains.

        Returns:
            True if point has less than 2 direct connections
        """
        return len(self.direct_connections) < 2

    def add_direct_connection(self, other: "Point") -> bool:
        """Add a direct connection to another point.

        Args:
            other: The point to connect to

        Returns:
            True if connection was added successfully

        Raises:
            ValueError: If connection cannot be made
        """
        if not self.can_accept_connection():
            raise ValueError(f"Point {self} already has 2 connections")
        if not other.can_accept_connection():
            raise ValueError(f"Point {other} already has 2 connections")
        if not self.is_adjacent_to(other):
            raise ValueError(f"Points {self} and {other} are not adjacent")
        if other in self.direct_connections:
            return False  # Already connected

        # Add bidirectional connection
        self.direct_connections.append(other)
        other.direct_connections.append(self)
        return True

    def remove_direct_connection(self, other: "Point") -> bool:
        """Remove a direct connection to another point.

        Args:
            other: The point to disconnect from

        Returns:
            True if connection was removed successfully
        """
        if other not in self.direct_connections:
            return False

        # Remove bidirectional connection
        self.direct_connections.remove(other)
        other.direct_connections.remove(self)
        return True

    def get_connection_count(self) -> int:
        """Get the number of direct connections.

        Returns:
            Number of direct connections (0, 1, or 2)
        """
        return len(self.direct_connections)

    def is_endpoint(self) -> bool:
        """Check if this point is a chain endpoint (exactly 1 connection).

        Returns:
            True if point has exactly 1 connection
        """
        return len(self.direct_connections) == 1

    def is_middle_point(self) -> bool:
        """Check if this point is in the middle of a chain (exactly 2 connections).

        Returns:
            True if point has exactly 2 connections
        """
        return len(self.direct_connections) == 2

    def reset_connections(self) -> None:
        """Reset all connection state."""
        # Remove all direct connections
        for connected_point in self.direct_connections.copy():
            self.remove_direct_connection(connected_point)

        self.connected = False
        self.chain_id = None
