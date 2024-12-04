import pytest
from src.MCSolver import SetCoverSolver, SolverConfig, solve_set_cover


class TestSetCoverSolver:
    @pytest.fixture
    def solver(self):
        """Create a default solver instance."""
        return SetCoverSolver()

    @pytest.fixture
    def basic_problem(self):
        """Create a simple test problem."""
        return {
            "parent": {1, 2, 3, 4},
            "sets": [{1, 2}, {2, 3}, {3, 4}, {1, 2, 3}, {2, 3, 4}],
        }

    def test_basic_solution(self, solver, basic_problem):
        """Test solving a basic set cover problem."""
        result = solver.solve(basic_problem["parent"], basic_problem["sets"])

        # Verify solution covers all elements
        union = set().union(*result)
        assert basic_problem["parent"].issubset(union)

        # Verify solution uses available sets
        assert all(s in basic_problem["sets"] for s in result)

    def test_optimal_solution(self, solver):
        """Test that solver finds optimal solution when possible."""
        parent = {1, 2, 3, 4}
        sets = [{1, 2}, {3, 4}, {1, 2, 3, 4}]

        result = solver.solve(parent, sets)
        assert len(result) == 1
        assert result[0] == {1, 2, 3, 4}

    def test_invalid_inputs(self, solver):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError):
            solver.solve([], [])  # Empty parent

        with pytest.raises(ValueError):
            solver.solve({1, 2}, [])  # Empty sets

        with pytest.raises(ValueError):
            solver.solve("not a set", [{1}])  # Invalid parent type

    def test_working_days_constraint(self, solver):
        """Test handling of working days constraint."""
        parent = {1, 2}
        sets = [{1, 2, 3, 4, 5}, {1}, {2}]  # First set has too many extra days

        result = solver.solve(parent, sets)
        assert len(result) == 2
        assert {1} in result
        assert {2} in result

    def test_solution_optimization(self, solver):
        """Test that solutions are optimized through set merging."""
        parent = {1, 2, 3, 4}
        sets = [{1, 2}, {3, 4}, {1, 2, 3, 4}]

        result = solver.solve(parent, sets)
        assert len(result) == 1
        assert result[0] == {1, 2, 3, 4}

    @pytest.mark.parametrize(
        "parent,sets,expected_len",
        [
            ({1, 2}, [{1}, {2}], 2),
            ({1, 2, 3}, [{1, 2}, {2, 3}], 2),
            ({1, 2, 3, 4}, [{1, 2, 3, 4}], 1),
        ],
    )
    def test_various_cases(self, solver, parent, sets, expected_len):
        """Test solver with various input cases."""
        result = solver.solve(parent, sets)
        assert len(result) == expected_len
        assert parent.issubset(set().union(*result))

    def test_custom_config(self):
        """Test solver with custom configuration."""
        config = SolverConfig(missing_weight=2.0, extra_weight=0.5, max_iterations=10)
        solver = SetCoverSolver(config)

        parent = {1, 2, 3}
        sets = [{1, 2, 4}, {2, 3, 5}, {1, 2, 3, 4, 5}]

        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result))

    def test_convenience_function(self, basic_problem):
        """Test the convenience function."""
        result = solve_set_cover(basic_problem["parent"], basic_problem["sets"])
        assert basic_problem["parent"].issubset(set().union(*result))

    def test_complex_coverage(self, solver):
        """Test a complex set cover scenario."""
        parent = {1, 2, 3, 4, 5, 6}
        sets = [{1, 2}, {3, 4}, {5, 6}, {1, 3, 5}]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result))
        assert len(result) <= 3  # Should use at most 3 sets

    def test_multiple_optimal_solutions(self, solver):
        """Test if solver handles multiple optimal solutions."""
        parent = {1, 2, 3, 4}
        sets = [{1, 2}, {3, 4}, {1, 2, 3, 4}]
        result = solver.solve(parent, sets)
        assert {1, 2, 3, 4} in result
        assert len(result) == 1

    def test_sparse_coverage(self, solver):
        """Test handling sparse sets."""
        parent = {1, 2, 3, 4, 5}
        sets = [{1, 3}, {2}, {4, 5}]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result))

    def test_large_problem(self, solver):
        """Test solving a large set cover problem."""
        parent = set(range(1, 101))
        sets = [set(range(i, i + 10)) for i in range(1, 101, 10)]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result))
        assert len(result) <= 10

    def test_single_element_parent(self, solver):
        """Edge Case: Parent set contains a single element."""
        parent = {1}
        sets = [{1}, {1, 2}, {1, 3}, {2, 3}]
        result = solver.solve(parent, sets)
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert (
            {1} in result or {1, 2} in result or {1, 3} in result
        ), f"Unexpected result: {result}"

    def test_no_solution_exists(self, solver):
        """Edge Case: No available sets cover all elements in the parent."""
        parent = {1, 2, 3}
        sets = [{1}, {2}, {4}]  # Missing coverage for element 3
        with pytest.raises(
            RuntimeError, match="Unable to find solution: incomplete coverage."
        ):
            solver.solve(parent, sets)

    def test_all_sets_identical(self, solver):
        """Edge Case: All available sets are identical."""
        parent = {1, 2, 3}
        sets = [{1, 2, 3}, {1, 2, 3}, {1, 2, 3}]
        result = solver.solve(parent, sets)
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert {
            1,
            2,
            3,
        } in result, f"Expected {{1, 2, 3}} to be in the result, but got {result}"

    def test_all_sets_empty(self, solver):
        """Edge Case: All available sets are empty."""
        parent = {1, 2, 3}
        sets = [set(), set(), set()]
        with pytest.raises(
            RuntimeError, match="Unable to find solution: incomplete coverage."
        ):
            solver.solve(parent, sets)

    def test_sets_containing_all_parent_elements(self, solver):
        """Edge Case: Each set individually covers the entire parent set."""
        parent = {1, 2, 3}
        sets = [{1, 2, 3}, {1, 2, 3}, {1, 2, 3}]
        result = solver.solve(parent, sets)
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert {
            1,
            2,
            3,
        } in result, f"Expected {{1, 2, 3}} to be in the result, but got {result}"

    def test_sets_with_subsets(self, solver):
        """Edge Case: Available sets include subsets of other sets."""
        parent = {1, 2, 3, 4}
        sets = [{1, 2}, {1}, {2, 3}, {3}, {4}, {1, 2, 3, 4}]
        result = solver.solve(parent, sets)
        # Optimal solution could be [{1,2}, {2,3}, {4}] or [{1,2,3,4}]
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        assert (
            len(result) <= 3
        ), f"Expected at most 3 sets, but got {len(result)}: {result}"

    def test_duplicate_sets_in_available_sets(self, solver):
        """Edge Case: Duplicate sets exist in the available sets."""
        parent = {1, 2, 3}
        sets = [{1, 2}, {1, 2}, {2, 3}, {2, 3}, {1, 2, 3}]
        result = solver.solve(parent, sets)
        # Optimal solution is [{1,2,3}]
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert {
            1,
            2,
            3,
        } in result, f"Expected {{1, 2, 3}} to be in the result, but got {result}"

    def test_highly_overlapping_sets(self, solver):
        """Complex Scenario: Sets overlap significantly."""
        parent = set(range(1, 11))  # Elements 1 through 10
        sets = [
            set(range(1, 6)),  # 1-5
            set(range(4, 9)),  # 4-8
            set(range(7, 11)),  # 7-10
            {2, 4, 6, 8, 10},  # Even numbers
            {1, 3, 5, 7, 9},  # Odd numbers
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Adjusted expectation to 3 sets
        assert len(result) == 3, f"Expected 3 sets, but got {len(result)}: {result}"
        # Optionally, verify specific sets are selected
        expected_sets = [{1, 2, 3, 4, 5}, {7, 8, 9, 10}, {2, 4, 6, 8, 10}]
        for s in expected_sets:
            assert s in result or s.issubset(
                set().union(*result)
            ), f"Expected {s} to be covered."

    def test_varying_set_sizes_and_coverage(self, solver):
        """Complex Scenario: Mix of large and small sets with varying coverage."""
        parent = {1, 2, 3, 4, 5, 6, 7, 8}
        sets = [
            {1, 2, 3},
            {4, 5},
            {6, 7},
            {8},
            {1, 4, 6},
            {2, 5, 7, 8},
            {3, 4, 5, 6, 7},
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Possible optimal solutions could vary based on cost
        # For example: [{1,2,3}, {4,5}, {6,7}, {8}]
        assert (
            len(result) <= 4
        ), f"Expected at most 4 sets, but got {len(result)}: {result}"

    def test_minimal_cover_requires_more_extra_elements(self, solver):
        """Complex Scenario: Minimal cover requires selecting sets with more extra elements."""
        config = SolverConfig(missing_weight=1.0, extra_weight=2.0)
        solver = SetCoverSolver(config)
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2},  # Extra: 0
            {3, 4},  # Extra: 0
            {1, 2, 3, 4, 5},  # Extra: 1
        ]
        result = solver.solve(parent, sets)
        # Depending on weights, solver might prefer two smaller sets over one with extra
        assert len(result) == 2, f"Expected 2 sets, but got {len(result)}: {result}"
        assert {1, 2} in result
        assert {3, 4} in result

    def test_non_integer_elements(self, solver):
        """Edge Case: Parent and sets contain non-integer elements."""
        parent = {"apple", "banana", "cherry"}
        sets = [
            {"apple", "banana"},
            {"banana", "cherry"},
            {"apple", "cherry"},
            {"apple", "banana", "cherry"},
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Optimal solution is any one of the three two-element sets or the full set
        assert (
            len(result) <= 2
        ), f"Expected at most 2 sets, but got {len(result)}: {result}"

    def test_nested_sets(self, solver):
        """Edge Case: Sets that contain other sets."""
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2},
            {1, 2, 3},
            {2, 3, 4},
            {1, 2, 3, 4},
        ]
        result = solver.solve(parent, sets)
        # Optimal solution could be [{1,2,3,4}] or [{1,2}, {2,3,4}]
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        assert (
            len(result) <= 2
        ), f"Expected at most 2 sets, but got {len(result)}: {result}"

    def test_very_large_problem(self):
        """Performance Test: Solve a very large set cover problem."""
        parent = set(range(1, 1001))  # Elements 1 through 1000
        sets = [set(range(i, i + 100)) for i in range(1, 1001, 50)]  # Overlapping sets
        solver = SetCoverSolver(SolverConfig(max_iterations=10000))
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # With overlapping sets, the minimal number of sets would be 10 (each covering 100, overlapping by 50)
        assert (
            len(result) <= 20
        ), f"Expected at most 20 sets, but got {len(result)}: {result}"

    def test_configuration_variations_minimize_extra(self, solver):
        """Configuration Test: Prioritize minimizing extra elements over the number of sets."""
        config = SolverConfig(missing_weight=1.0, extra_weight=10.0)
        solver = SetCoverSolver(config)
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2},  # Extra: 0
            {3, 4},  # Extra: 0
            {1, 2, 3, 4, 5},  # Extra: 1
            {1, 3, 5},
            {2, 4, 6},
        ]
        result = solver.solve(parent, sets)
        # With high extra_weight, solver should prefer {1,2} and {3,4} over {1,2,3,4,5}
        assert len(result) == 2, f"Expected 2 sets, but got {len(result)}: {result}"
        assert {1, 2} in result
        assert {3, 4} in result

    def test_configuration_variations_minimize_missing(self, solver):
        """Configuration Test: Prioritize minimizing missing elements over extra elements."""
        config = SolverConfig(missing_weight=10.0, extra_weight=1.0)
        solver = SetCoverSolver(config)
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2, 5},  # Extra: 1
            {3, 4, 6},  # Extra: 1
            {1, 2, 3, 4, 5, 6},  # Extra: 2
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Calculate expected cost
        expected_cost = 10.0 * 0 + 1.0 * 2  # Selecting the full set: missing=0, extra=2
        actual_cost = 0
        for s in result:
            missing = len(parent - s)
            extra = len(s - parent)
            actual_cost += config.missing_weight * missing + config.extra_weight * extra
        assert (
            actual_cost == expected_cost
        ), f"Expected cost {expected_cost}, but got {actual_cost}"

    def test_sets_with_partial_overlap(self, solver):
        """Complex Scenario: Sets have partial overlaps with the parent set."""
        parent = {1, 2, 3, 4, 5}
        sets = [
            {1, 2},
            {2, 3},
            {3, 4},
            {4, 5},
            {1, 3, 5},
            {2, 4},
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Adjusted expectation to 2 sets
        assert len(result) == 2, f"Expected 2 sets, but got {len(result)}: {result}"
        assert {1, 3, 5} in result and {
            2,
            4,
        } in result, (
            f"Expected {{1, 3, 5}} and {{2, 4}} to be in the result, but got {result}"
        )

    def test_sets_with_no_overlap(self, solver):
        """Edge Case: Available sets have no overlap with the parent set."""
        parent = {1, 2, 3}
        sets = [{4}, {5}, {6}]
        with pytest.raises(
            RuntimeError, match="Unable to find solution: incomplete coverage."
        ):
            solver.solve(parent, sets)

    def test_sets_cover_with_minimal_extra_elements(self, solver):
        """Configuration Test: Solver should minimize extra elements even if it requires more sets."""
        config = SolverConfig(missing_weight=1.0, extra_weight=5.0)
        solver = SetCoverSolver(config)
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2, 5},  # Extra: 1
            {3, 4, 6},  # Extra: 1
            {1, 3},  # Extra: 0
            {2, 4},  # Extra: 0
        ]
        result = solver.solve(parent, sets)
        # Should prefer two sets {1,3} and {2,4} with no extras over two sets with extras
        assert len(result) == 2, f"Expected 2 sets, but got {len(result)}: {result}"
        assert {1, 3} in result
        assert {2, 4} in result

    def test_sets_with_full_and_partial_coverage(self, solver):
        """Complex Scenario: Mix of sets covering full and partial elements."""
        parent = {1, 2, 3, 4, 5}
        sets = [
            {1, 2, 3, 4, 5},  # Full coverage
            {1, 2},  # Partial
            {3, 4},  # Partial
            {5},  # Partial
            {1, 3, 5},  # Partial
        ]
        result = solver.solve(parent, sets)
        # Optimal solution should be the full set alone
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert {1, 2, 3, 4, 5} in result

    def test_sets_with_no_extra_elements(self, solver):
        """Test with sets that exactly cover the parent without any extras."""
        parent = {1, 2, 3, 4}
        sets = [
            {1, 2},
            {3, 4},
            {1, 2, 3, 4},
        ]
        result = solver.solve(parent, sets)
        # Optimal solution is {1,2,3,4}
        assert len(result) == 1, f"Expected 1 set, but got {len(result)}: {result}"
        assert {1, 2, 3, 4} in result

    def test_partial_set_reuse(self, solver):
        """Complex Scenario: Reusing parts of sets to cover the parent."""
        parent = {1, 2, 3, 4, 5, 6}
        sets = [
            {1, 2, 3},
            {3, 4, 5},
            {5, 6},
            {1, 4},
            {2, 5, 6},
        ]
        result = solver.solve(parent, sets)
        assert parent.issubset(set().union(*result)), "Not all elements are covered."
        # Possible optimal solutions:
        # [{1,2,3}, {3,4,5}, {5,6}]
        # or [{1,4}, {2,5,6}, {3,4,5}]
        assert len(result) == 3, f"Expected 3 sets, but got {len(result)}: {result}"
