"""Chain class representing a connected sequence of points."""

from typing import List

from src.models.point import Point


class Chain:
    """Represents a linear chain of connected points."""

    def __init__(self, chain_id: int, max_connection_count: int) -> None:
        """Initialize a chain with the given constraints.

        Args:
            chain_id: Unique identifier for this chain
            max_connection_count: Maximum number of connections in this chain
                                (chain length = connections, points = connections + 1)

        Raises:
            ValueError: If max_connection_count is less than 0
        """
        if max_connection_count < 0:
            raise ValueError("Chain max_connection_count must be at least 0")

        self.chain_id = chain_id
        self.max_connection_count = max_connection_count
        self.points: List[Point] = []

    def can_add_point(self, point: Point) -> bool:
        """Check if a point can be added to this chain.

        Args:
            point: The point to potentially add

        Returns:
            True if point can be added, False otherwise
        """
        if point.connected:
            return False

        # Check if adding this point would exceed connection limit
        if self.connection_count >= self.max_connection_count:
            return False

        # Check if point can accept a connection (max 2 per point)
        if not point.can_accept_connection():
            return False

        if not self.points:
            return True  # First point in chain

        # Check if we can connect to an endpoint of the chain
        return self._can_connect_to_endpoint(point)

    def _can_connect_to_endpoint(self, point: Point) -> bool:
        """Check if point can connect to an endpoint of this chain.

        Args:
            point: The point to potentially connect

        Returns:
            True if point can connect to a chain endpoint
        """
        endpoints = self.get_endpoints()
        for endpoint in endpoints:
            if endpoint.can_accept_connection() and point.is_adjacent_to(endpoint):
                return True
        return False

    def add_point(self, point: Point) -> bool:
        """Add a point to this chain.

        Args:
            point: The point to add

        Returns:
            True if point was successfully added

        Raises:
            ValueError: If the point cannot be added to this chain
        """
        if not self.can_add_point(point):
            raise ValueError(f"Cannot add point {point} to chain {self.chain_id}")

        if not self.points:
            # First point in chain
            point.connected = True
            point.chain_id = self.chain_id
            self.points.append(point)
            return True

        # Find which endpoint to connect to
        endpoints = self.get_endpoints()
        connected = False

        for endpoint in endpoints:
            if endpoint.can_accept_connection() and point.is_adjacent_to(endpoint):
                # Create the direct connection
                endpoint.add_direct_connection(point)
                point.connected = True
                point.chain_id = self.chain_id
                self.points.append(point)
                connected = True
                break

        if not connected:
            raise ValueError(f"Could not connect point {point} to any endpoint")

        return True

    def remove_point(self, point: Point) -> bool:
        """Remove a point from the chain.

        Args:
            point: The point to remove

        Returns:
            True if point was successfully removed
        """
        if point not in self.points:
            return False

        # Reset the point's state
        point.reset_connections()
        self.points.remove(point)
        return True

    def get_endpoints(self) -> List[Point]:
        """Get the endpoint(s) of the chain.

        For a linear chain, this returns the first and last points.
        For a single point, returns that point.

        Returns:
            List of endpoint points
        """
        if not self.points:
            return []
        if len(self.points) == 1:
            return [self.points[0]]
        return [self.points[0], self.points[-1]]

    def is_valid_chain(self) -> bool:
        """Validate that this chain forms a valid linear path.

        Returns:
            True if chain is valid, False otherwise
        """
        if not self.points:
            return True

        if self.connection_count > self.max_connection_count:
            return False

        # Check that the chain forms a valid linear path using direct connections
        if len(self.points) == 1:
            # Single point is valid
            return True

        # For multiple points, verify they form a linear path
        # Count endpoints (1 connection) and middle points (2 connections)
        endpoints = 0
        middle_points = 0

        for point in self.points:
            if point.is_endpoint():
                endpoints += 1
            elif point.is_middle_point():
                middle_points += 1
            else:
                # Point has 0 connections or invalid connection count
                return False

        # Valid linear chain should have exactly 2 endpoints
        # and (len(points) - 2) middle points
        expected_middle_points = len(self.points) - 2
        if not (endpoints == 2 and middle_points == expected_middle_points):
            return False

        # Check that all points have correct chain_id
        for point in self.points:
            if point.chain_id != self.chain_id or not point.connected:
                return False

        return True

    @property
    def point_count(self) -> int:
        """Get the current number of points in the chain."""
        return len(self.points)

    @property
    def connection_count(self) -> int:
        """Get the current number of connections in the chain."""
        return max(0, len(self.points) - 1)

    @property
    def length(self) -> int:
        """Get the chain length (number of connections)."""
        return self.connection_count

    @property
    def is_full(self) -> bool:
        """Check if the chain has reached maximum capacity."""
        return self.connection_count >= self.max_connection_count

    @property
    def is_empty(self) -> bool:
        """Check if the chain has no points."""
        return len(self.points) == 0

    def __repr__(self) -> str:
        """String representation for debugging."""
        points_repr = [f"({p.x},{p.y})" for p in self.points]
        return (
            f"Chain(id={self.chain_id}, "
            f"connections={self.connection_count}/{self.max_connection_count}, "
            f"points={self.point_count}, path={points_repr})"
        )
