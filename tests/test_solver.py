from __future__ import annotations

import unittest

from pokemon_opt.evaluation import team_cost
from pokemon_opt.instances import load_instance, predefined_instance_paths
from pokemon_opt.solver import format_solve_summary, solve_problem


class SolverServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.instance = load_instance(predefined_instance_paths()[0])

    def test_sa_summary_contains_a_freshly_validated_cost(self) -> None:
        summary = solve_problem(
            self.instance,
            "sa",
            seed=5,
            initial_temperature=2.0,
            alpha=0.9,
            min_temperature=0.1,
            max_iterations=100,
        )
        self.assertEqual(summary.cost, team_cost(summary.team))
        self.assertEqual(summary.seed, 5)
        self.assertIsNotNone(summary.iterations)
        self.assertIsNone(summary.combinations_evaluated)

    def test_brute_force_summary_contains_exact_metadata(self) -> None:
        summary = solve_problem(self.instance, "brute-force")
        self.assertEqual(summary.cost, team_cost(summary.team))
        self.assertIsNone(summary.seed)
        self.assertIsNone(summary.iterations)
        self.assertEqual(summary.combinations_evaluated, 924)

    def test_summary_format_contains_required_output(self) -> None:
        summary = solve_problem(
            self.instance,
            "sa",
            seed=9,
            max_iterations=5,
        )
        output = format_solve_summary(summary)
        for expected in (
            "Instance: small_12",
            "Algorithm: Simulated Annealing",
            "Seed: 9",
            "Best cost:",
            "Average multiplier:",
            "Runtime:",
            "Team:",
        ):
            self.assertIn(expected, output)

    def test_unknown_algorithm_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_problem(self.instance, "unknown")


if __name__ == "__main__":
    unittest.main()

