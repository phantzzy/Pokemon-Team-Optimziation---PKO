from __future__ import annotations

import unittest

from pokemon_opt.data_loader import load_type_chart
from pokemon_opt.type_chart import TYPE_NAMES, defensive_multiplier


class TypeChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chart = load_type_chart()

    def test_chart_is_complete(self) -> None:
        self.assertEqual(set(self.chart), set(TYPE_NAMES))
        self.assertTrue(
            all(set(row) == set(TYPE_NAMES) for row in self.chart.values())
        )

    def test_known_single_type_matchups(self) -> None:
        cases = (
            ("Electric", "Ground", 0.0),
            ("Fire", "Grass", 2.0),
            ("Fire", "Water", 0.5),
            ("Normal", "Ghost", 0.0),
            ("Fighting", "Normal", 2.0),
            ("Ice", "Dragon", 2.0),
        )
        for attack, defense, expected in cases:
            with self.subTest(attack=attack, defense=defense):
                self.assertEqual(
                    defensive_multiplier(self.chart, attack, defense), expected
                )

    def test_known_dual_type_matchups(self) -> None:
        cases = (
            ("Electric", "Water", "Ground", 0.0),
            ("Grass", "Water", "Ground", 4.0),
            ("Fire", "Bug", "Steel", 4.0),
            ("Rock", "Fire", "Flying", 4.0),
        )
        for attack, type1, type2, expected in cases:
            with self.subTest(attack=attack, type1=type1, type2=type2):
                self.assertEqual(
                    defensive_multiplier(self.chart, attack, type1, type2),
                    expected,
                )

    def test_unknown_type_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            defensive_multiplier(self.chart, "Unknown", "Water")


if __name__ == "__main__":
    unittest.main()

