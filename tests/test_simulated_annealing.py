from __future__ import annotations

import unittest

from pokemon_opt.data_loader import load_pokemon
from pokemon_opt.evaluation import team_cost
from pokemon_opt.simulated_annealing import simulated_annealing


class SimulatedAnnealingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = load_pokemon()[:20]
        cls.parameters = {
            "initial_temperature": 5.0,
            "alpha": 0.98,
            "min_temperature": 0.01,
            "max_iterations": 500,
        }

    def run_sa(self, seed: int = 123):
        return simulated_annealing(
            self.candidates, seed=seed, **self.parameters
        )

    def test_returns_a_valid_six_pokemon_team(self) -> None:
        result = self.run_sa()
        candidate_ids = {pokemon.id for pokemon in self.candidates}
        result_ids = {pokemon.id for pokemon in result.best_team}

        self.assertEqual(len(result.best_team), 6)
        self.assertEqual(len(result_ids), 6)
        self.assertTrue(result_ids.issubset(candidate_ids))

    def test_fixed_seed_and_parameters_are_reproducible(self) -> None:
        first = self.run_sa(seed=777)
        second = self.run_sa(seed=777)

        self.assertEqual(first, second)

    def test_best_is_never_worse_than_initial_solution(self) -> None:
        result = self.run_sa()
        self.assertLessEqual(result.best_cost, result.initial_cost)

    def test_all_reported_costs_match_fresh_evaluation(self) -> None:
        result = self.run_sa()
        self.assertEqual(result.best_cost, team_cost(result.best_team))
        self.assertEqual(result.initial_cost, team_cost(result.initial_team))
        self.assertEqual(result.final_cost, team_cost(result.final_team))

    def test_explicit_initial_team_is_preserved_in_metadata(self) -> None:
        initial_team = self.candidates[:6]
        result = simulated_annealing(
            self.candidates,
            seed=50,
            initial_team=initial_team,
            **self.parameters,
        )
        self.assertEqual(result.initial_team, initial_team)
        self.assertEqual(result.initial_cost, team_cost(initial_team))

    def test_iteration_limit_stops_the_run(self) -> None:
        result = simulated_annealing(
            self.candidates,
            seed=1,
            initial_temperature=10.0,
            alpha=0.999,
            min_temperature=0.0001,
            max_iterations=7,
        )
        self.assertEqual(result.iterations, 7)
        self.assertAlmostEqual(result.final_temperature, 10.0 * 0.999**7)

    def test_minimum_temperature_stops_the_run(self) -> None:
        result = simulated_annealing(
            self.candidates,
            seed=1,
            initial_temperature=1.0,
            alpha=0.5,
            min_temperature=0.2,
            max_iterations=100,
        )
        self.assertEqual(result.iterations, 3)
        self.assertLess(result.final_temperature, 0.2)

    def test_invalid_parameters_are_rejected(self) -> None:
        invalid_cases = (
            {"initial_temperature": 0.0},
            {"alpha": 0.0},
            {"alpha": 1.0},
            {"min_temperature": 0.0},
            {"initial_temperature": 1.0, "min_temperature": 1.0},
            {"max_iterations": 0},
            {"max_iterations": 1.5},
        )
        for overrides in invalid_cases:
            parameters = dict(self.parameters)
            parameters.update(overrides)
            with self.subTest(parameters=parameters):
                with self.assertRaises(ValueError):
                    simulated_annealing(
                        self.candidates, seed=1, **parameters
                    )

    def test_candidate_pool_must_allow_a_swap(self) -> None:
        with self.assertRaises(ValueError):
            simulated_annealing(self.candidates[:6], seed=1)


if __name__ == "__main__":
    unittest.main()
