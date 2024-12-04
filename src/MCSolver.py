from typing import List, Set, Optional
from dataclasses import dataclass


@dataclass
class SolverConfig:
    """Configuration for the set cover solver."""

    missing_weight: float = 1.0  # Weight for elements missing from parent
    extra_weight: float = 1.0  # Weight for extra elements not in parent
    max_iterations: int = 1000  # Maximum iterations to prevent infinite loops


class SetCoverSolver:
    """
    Optimized implementation of the set cover problem solver.
    Utilizes a greedy approach with cost-based optimization and set merging.
    """

    def __init__(self, config: Optional[SolverConfig] = None):
        """
        Initialize the SetCoverSolver with an optional configuration.

        Args:
            config (Optional[SolverConfig]): Configuration settings for the solver.
        """
        self.config = config or SolverConfig()
        self.original_parent: Optional[Set[int]] = None

    def solve(self, parent: Set[int], sets: List[Set[int]]) -> List[Set[int]]:
        """
        Solve the set cover problem to find minimal sets covering the parent set.

        Args:
            parent (Set[int]): The set that needs to be covered.
            sets (List[Set[int]]): List of available sets to use for covering.

        Returns:
            List[Set[int]]: List of sets that optimally cover the parent set.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If a solution cannot be found within the maximum iterations.
        """
        self._validate_inputs(parent, sets)

        # Initialize variables
        self.original_parent = parent.copy()
        results: List[Set[int]] = []
        union_result: Set[int] = set()
        available_sets: List[Set[int]] = sets.copy()
        remaining_parent: Set[int] = parent.copy()
        iteration: int = 0

        while not self.original_parent.issubset(union_result):
            if iteration >= self.config.max_iterations:
                raise RuntimeError("Failed to find solution within iteration limit.")

            best_set = self._select_best_set(remaining_parent, available_sets)

            if best_set is None:
                break  # No suitable set found; exit loop.

            # Update results and coverage
            results.append(best_set)
            union_result |= best_set
            remaining_parent -= best_set
            available_sets.remove(best_set)
            iteration += 1

        if not self.original_parent.issubset(union_result):
            raise RuntimeError("Unable to find solution: incomplete coverage.")

        return self._optimize_solution(results)

    def _validate_inputs(self, parent: Set[int], sets: List[Set[int]]) -> None:
        """
        Validate the solver inputs.

        Args:
            parent (Set[int]): The set to be covered.
            sets (List[Set[int]]): List of available sets.

        Raises:
            ValueError: If any input is invalid.
        """
        if not isinstance(parent, set):
            raise ValueError("Parent must be a set.")
        if not isinstance(sets, list) or not all(isinstance(s, set) for s in sets):
            raise ValueError("Sets must be a list of sets.")
        if not sets:
            raise ValueError("Sets list cannot be empty.")
        if not parent:
            raise ValueError("Parent set cannot be empty.")

    def _calculate_cost(
        self, remaining_parent: Set[int], candidate_set: Set[int]
    ) -> float:
        """
        Calculate the cost of using a candidate set based on missing and extra elements.

        Args:
            remaining_parent (Set[int]): Remaining elements to cover.
            candidate_set (Set[int]): The candidate set being evaluated.

        Returns:
            float: The calculated cost.
        """
        missing_elements = len(remaining_parent - candidate_set)
        extra_elements = len(candidate_set - self.original_parent)
        return (
            self.config.missing_weight * missing_elements
            + self.config.extra_weight * extra_elements
        )

    def _select_best_set(
        self, remaining_parent: Set[int], sets: List[Set[int]]
    ) -> Optional[Set[int]]:
        """
        Select the best candidate set based on minimal cost.

        Args:
            remaining_parent (Set[int]): Remaining elements to cover.
            sets (List[Set[int]]): Available sets to choose from.

        Returns:
            Optional[Set[int]]: The best set or None if no valid set is found.
        """
        best_set: Optional[Set[int]] = None
        best_cost: float = float("inf")

        for candidate_set in sets:
            cost = self._calculate_cost(remaining_parent, candidate_set)

            if cost < best_cost:
                best_cost = cost
                best_set = candidate_set

        return best_set

    def _optimize_solution(self, results: List[Set[int]]) -> List[Set[int]]:
        """
        Optimize the solution by removing redundant sets to minimize the number of sets used.

        Args:
            results (List[Set[int]]): Current list of selected sets.

        Returns:
            List[Set[int]]: Optimized list of sets.
        """
        optimized_results: List[Set[int]] = results.copy()
        for candidate_set in results:
            temp_results = optimized_results.copy()
            temp_results.remove(candidate_set)

            # Check if removing this set breaks coverage
            union_result = set().union(*temp_results)
            if not self.original_parent.issubset(union_result):
                continue  # Keep the candidate set

            optimized_results = temp_results  # Remove the redundant set

        return optimized_results


def solve_set_cover(
    parent: Set[int], sets: List[Set[int]], config: Optional[SolverConfig] = None
) -> List[Set[int]]:
    """
    Convenience function to solve the set cover problem.

    Args:
        parent (Set[int]): The set that needs to be covered.
        sets (List[Set[int]]): List of available sets to use for covering.
        config (Optional[SolverConfig]): Optional solver configuration.

    Returns:
        List[Set[int]]: List of sets that optimally cover the parent set.
    """
    solver = SetCoverSolver(config)
    return solver.solve(parent, sets)
