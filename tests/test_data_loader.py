from __future__ import annotations

import unittest

from pokemon_opt.data_loader import load_pokemon, load_type_chart
from pokemon_opt.type_chart import TYPE_NAMES


class DataLoaderTests(unittest.TestCase):
    def test_local_snapshot_loads_and_precomputes_vectors(self) -> None:
        chart = load_type_chart()
        pokemon = load_pokemon(chart=chart)

        self.assertEqual(len(pokemon), 100)
        self.assertEqual(len({item.id for item in pokemon}), 100)
        self.assertEqual(len({item.name for item in pokemon}), 100)
        self.assertTrue(
            all(len(item.defensive_vector) == len(TYPE_NAMES) for item in pokemon)
        )

    def test_precomputed_vector_uses_canonical_attack_order(self) -> None:
        chart = load_type_chart()
        pokemon = load_pokemon(chart=chart)[0]
        normal_index = TYPE_NAMES.index("Normal")
        expected = chart["Normal"][pokemon.type1]
        if pokemon.type2 is not None:
            expected *= chart["Normal"][pokemon.type2]
        self.assertEqual(pokemon.defensive_vector[normal_index], expected)


if __name__ == "__main__":
    unittest.main()

