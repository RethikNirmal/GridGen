"""ChainBuilder algorithm for connecting points into chains."""

import random
from typing import List, Optional, Set

from src.models.chain import Chain
from src.models.grid import Grid
from src.models.point import Point


class ChainBuilder:
    """Algorithm for building chains that cover all points in the grid."""

    def __init__(self, grid: Grid, max_chain_length: int) -> None:
        """Initialize the chain builder.

        Args:
            grid: The grid to build chains on
            max_chain_length: Maximum number of connections allowed per chain
                            (chain length = connections, points = connections + 1)

        Raises:
            ValueError: If max_chain_length is less than 0
        """
        if max_chain_length < 0:
            raise ValueError("max_chain_length must be at least 0")

        self.grid = grid
        self.max_chain_length = max_chain_length
        self.chains: List[Chain] = []
        self.next_chain_id = 0
        
        # Animation state
        self.current_chain: Optional[Chain] = None
        self.animation_step = 0
        self.is_building = False

    def build_chains(self) -> List[Chain]:
        """Build chains to cover all points in the grid.

        Returns:
            List of chains that cover all points

        Raises:
            RuntimeError: If unable to connect all points
        """
        self.grid.reset_connections()
        self.chains = []
        self.next_chain_id = 0

        max_attempts = 1000
        attempts = 0

        while self.grid.get_unconnected_points() and attempts < max_attempts:
            attempts += 1
            unconnected = self.grid.get_unconnected_points()

            if not unconnected:
                break

            # Start a new chain from a random unconnected point
            start_point = self._select_start_point(unconnected)
            chain = self._create_new_chain()
            chain.add_point(start_point)

            # Extend the chain as much as possible
            self._extend_chain(chain)

            if chain.length > 0:
                self.chains.append(chain)

        # Verify all points are connected
        if self.grid.get_unconnected_points():
            unconnected_count = len(self.grid.get_unconnected_points())
            raise RuntimeError(
                f"Failed to connect all points. "
                f"{unconnected_count} points remain unconnected."
            )

        return self.chains

    def start_animated_build(self) -> None:
        """Start the animated chain building process."""
        self.grid.reset_connections()
        self.chains = []
        self.next_chain_id = 0
        self.current_chain = None
        self.animation_step = 0
        self.is_building = True

    def build_step(self) -> bool:
        """Perform one step of the chain building animation.
        
        Returns:
            True if there are more steps to perform, False if complete
        """
        if not self.is_building:
            return False
            
        unconnected = self.grid.get_unconnected_points()
        if not unconnected:
            self.is_building = False
            return False
            
        # If no current chain, start a new one
        if self.current_chain is None:
            start_point = self._select_start_point(unconnected)
            self.current_chain = self._create_new_chain()
            self.current_chain.add_point(start_point)
            return True
            
        # Try to extend current chain
        next_point = self._find_best_next_point(self.current_chain)
        if next_point is not None and not self.current_chain.is_full:
            success = self._add_point_to_chain(self.current_chain, next_point)
            if success:
                return True
                
        # Current chain is complete, add it and start a new one
        if self.current_chain.length > 0:
            self.chains.append(self.current_chain)
        self.current_chain = None
        
        # Check if we still have unconnected points
        return len(self.grid.get_unconnected_points()) > 0

    def is_animation_complete(self) -> bool:
        """Check if the animation is complete.
        
        Returns:
            True if all points are connected
        """
        return not self.is_building and len(self.grid.get_unconnected_points()) == 0

    def _select_start_point(self, unconnected_points: List[Point]) -> Point:
        """Select the best starting point for a new chain.

        Args:
            unconnected_points: List of available unconnected points

        Returns:
            The selected starting point
        """
        # Strategy: prefer points with fewer unconnected neighbors
        # This helps avoid creating isolated points
        best_point = unconnected_points[0]
        min_unconnected_neighbors = float("inf")

        for point in unconnected_points:
            neighbors = self.grid.get_neighbors(point)
            unconnected_neighbors = [n for n in neighbors if not n.connected]
            if len(unconnected_neighbors) < min_unconnected_neighbors:
                min_unconnected_neighbors = len(unconnected_neighbors)
                best_point = point

        return best_point

    def _create_new_chain(self) -> Chain:
        """Create a new chain with a unique ID.

        Returns:
            A new empty chain
        """
        chain = Chain(self.next_chain_id, self.max_chain_length)
        self.next_chain_id += 1
        return chain

    def _extend_chain(self, chain: Chain) -> None:
        """Extend a chain as far as possible.

        Args:
            chain: The chain to extend
        """
        while not chain.is_full:
            next_point = self._find_best_next_point(chain)
            if next_point is None:
                break

            try:
                # Use Grid's connection method to properly handle constraints
                if self._add_point_to_chain(chain, next_point):
                    pass  # Success
                else:
                    # Could not connect due to constraints
                    break
            except ValueError:
                # Could not connect (shouldn't happen if validation worked)
                break

    def _find_best_next_point(self, chain: Chain) -> Optional[Point]:
        """Find the best next point to add to a chain.

        Args:
            chain: The chain to extend

        Returns:
            The best next point, or None if no valid point exists
        """
        if chain.is_empty:
            return None

        # Get all valid candidates that can be added to this chain
        valid_candidates = []
        for point in self.grid.get_unconnected_points():
            if chain.can_add_point(point):
                # Check if adding this point would violate constraints
                if self._would_connection_be_valid(chain, point):
                    valid_candidates.append(point)

        if not valid_candidates:
            return None

        # Strategy: prefer points that don't create isolated regions
        return self._select_best_neighbor(valid_candidates)

    def _select_best_neighbor(self, candidates: List[Point]) -> Point:
        """Select the best neighbor from a list of candidates.

        Args:
            candidates: List of valid neighbor points

        Returns:
            The selected point
        """
        if len(candidates) == 1:
            return candidates[0]

        # Score each candidate based on how many unconnected neighbors it has
        best_point = candidates[0]
        best_score = self._score_point(best_point)

        for point in candidates[1:]:
            score = self._score_point(point)
            if score > best_score:
                best_score = score
                best_point = point

        return best_point

    def _score_point(self, point: Point) -> float:
        """Score a point based on strategic value.

        Args:
            point: The point to score

        Returns:
            Score (higher is better)
        """
        neighbors = self.grid.get_neighbors(point)
        unconnected_neighbors = [n for n in neighbors if not n.connected]

        # Prefer points with more unconnected neighbors
        # This helps create more compact chains
        base_score = len(unconnected_neighbors)

        # Add small random component to break ties
        random_component = random.random() * 0.1

        return base_score + random_component

    def _would_connection_be_valid(self, chain: Chain, point: Point) -> bool:
        """Check if connecting a point to the chain would satisfy constraints.

        Args:
            chain: The chain to potentially extend
            point: The point to potentially add

        Returns:
            True if connection would be valid according to constraints
        """
        if chain.is_empty:
            return True  # First point in chain, no connections to validate

        # Find which endpoint this point would connect to
        endpoints = chain.get_endpoints()

        for endpoint in endpoints:
            if endpoint.can_accept_connection() and point.is_adjacent_to(endpoint):
                # Check if this specific connection would be valid
                if self.grid.validate_connection(endpoint, point):
                    return True

        return False

    def _add_point_to_chain(self, chain: Chain, point: Point) -> bool:
        """Add a point to a chain using Grid's constraint-aware methods.

        Args:
            chain: The chain to extend
            point: The point to add

        Returns:
            True if point was successfully added
        """
        if not chain.can_add_point(point):
            return False

        if chain.is_empty:
            # First point in chain - no connections needed
            point.connected = True
            point.chain_id = chain.chain_id
            chain.points.append(point)
            return True

        # Find which endpoint to connect to
        endpoints = chain.get_endpoints()

        for endpoint in endpoints:
            if endpoint.can_accept_connection() and point.is_adjacent_to(endpoint):
                # Use Grid's connection method which handles constraints
                if self.grid.add_connection(endpoint, point):
                    # Connection successful, update chain state
                    point.connected = True
                    point.chain_id = chain.chain_id
                    chain.points.append(point)
                    return True

        return False

    def get_coverage_stats(self) -> dict:
        """Get statistics about the current coverage.

        Returns:
            Dictionary with coverage statistics
        """
        total_points = self.grid.total_points
        connected_points = len(self.grid.get_connected_points())
        unconnected_points = len(self.grid.get_unconnected_points())

        return {
            "total_points": total_points,
            "connected_points": connected_points,
            "unconnected_points": unconnected_points,
            "coverage_percentage": (
                (connected_points / total_points * 100) if total_points > 0 else 0
            ),
            "total_chains": len(self.chains),
            "average_chain_length": (
                sum(chain.length for chain in self.chains) / len(self.chains)
                if self.chains
                else 0
            ),
        }

    def validate_solution(self) -> bool:
        """Validate that the current solution is correct.

        Returns:
            True if solution is valid, False otherwise
        """
        # Check that all points are connected
        if self.grid.get_unconnected_points():
            return False

        # Check that all chains are valid
        for chain in self.chains:
            if not chain.is_valid_chain():
                return False

        # Check that no point belongs to multiple chains
        seen_points: Set[Point] = set()
        for chain in self.chains:
            for point in chain.points:
                if point in seen_points:
                    return False
                seen_points.add(point)

        return True
