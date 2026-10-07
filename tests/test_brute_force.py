from __future__ import annotations

import math
import unittest

from pokemon_opt.brute_force import brute_force
from pokemon_opt.evaluation import team_cost
from pokemon_opt.models import Pokemon


def make_pokemon(identifier: int, multiplier: float) -> Pokemon:
    return Pokemon(
        id=identifier,
        name=f"Pokemon {identifier}",
        api_name=f"pokemon-{identifier}",
        type1="Normal",
        type2=None,
        defensive_vector=(multiplier,) * 18,
    )


class BruteForceTests(unittest.TestCase):
    def test_returns_manually_verifiable_optimum(self) -> None:
        candidates = tuple(
            make_pokemon(identifier, multiplier)
            for identifier, multiplier in enumerate(
                (0.0, 0.25, 0.5, 0.5, 1.0, 1.0, 4.0), start=1
            )
        )
        result = brute_force(candidates, max_candidates=7)

        self.assertEqual(
            {pokemon.id for pokemon in result.best_team}, {1, 2, 3, 4, 5, 6}
        )
        self.assertEqual(result.best_cost, team_cost(result.best_team))
        self.assertEqual(result.combinations_evaluated, math.comb(7, 6))
        self.assertGreaterEqual(result.runtime_ms, 0.0)

    def test_exactly_six_candidates_produces_one_combination(self) -> None:
        candidates = tuple(make_pokemon(index, 1.0) for index in range(1, 7))
        result = brute_force(candidates, max_candidates=6)
        self.assertEqual(result.best_team, candidates)
        self.assertEqual(result.combinations_evaluated, 1)

    def test_configurable_threshold_is_enforced(self) -> None:
        candidates = tuple(make_pokemon(index, 1.0) for index in range(1, 8))
        with self.assertRaises(ValueError):
            brute_force(candidates, max_candidates=6)

        result = brute_force(candidates, max_candidates=None)
        self.assertEqual(result.combinations_evaluated, 7)

    def test_duplicate_candidates_are_rejected(self) -> None:
        candidates = tuple(make_pokemon(index, 1.0) for index in range(1, 7))
        with self.assertRaises(ValueError):
            brute_force(candidates + (candidates[0],), max_candidates=7)


if __name__ == "__main__":
    unittest.main()

