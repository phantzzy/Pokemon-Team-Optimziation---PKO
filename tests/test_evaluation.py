from __future__ import annotations

import unittest

from pokemon_opt.data_loader import load_pokemon
from pokemon_opt.evaluation import (
    TEAM_MATCHUP_COUNT,
    average_multiplier,
    team_cost,
)


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.team = load_pokemon()[:6]

    def test_cost_is_deterministic(self) -> None:
        self.assertEqual(team_cost(self.team), team_cost(self.team))

    def test_team_order_does_not_change_cost(self) -> None:
        self.assertEqual(team_cost(self.team), team_cost(tuple(reversed(self.team))))

    def test_cost_equals_sum_of_precomputed_vectors(self) -> None:
        expected = sum(sum(item.defensive_vector) for item in self.team)
        self.assertEqual(team_cost(self.team), expected)

    def test_average_multiplier_is_cost_divided_by_108(self) -> None:
        cost = team_cost(self.team)
        self.assertEqual(TEAM_MATCHUP_COUNT, 108)
        self.assertEqual(average_multiplier(cost), cost / 108)

    def test_wrong_team_size_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            team_cost(self.team[:5])

    def test_duplicate_team_member_is_rejected(self) -> None:
        invalid_team = self.team[:5] + (self.team[0],)
        with self.assertRaises(ValueError):
            team_cost(invalid_team)


if __name__ == "__main__":
    unittest.main()
