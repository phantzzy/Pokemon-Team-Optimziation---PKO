from __future__ import annotations

import unittest

from pokemon_opt.data_loader import load_pokemon
from pokemon_opt.instances import load_instance, predefined_instance_paths


class ProblemInstanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_pokemon()

    def test_predefined_instances_have_expected_names_and_sizes(self) -> None:
        expected = (
            ("small_12", 12),
            ("medium_20", 20),
            ("medium_30", 30),
            ("large_50", 50),
            ("xlarge_100", 100),
        )
        loaded = [
            load_instance(path, self.dataset)
            for path in predefined_instance_paths()
        ]
        self.assertEqual(
            [(instance.name, instance.n) for instance in loaded], list(expected)
        )

    def test_predefined_instances_are_unique_and_in_dataset(self) -> None:
        dataset_ids = {pokemon.id for pokemon in self.dataset}
        for path in predefined_instance_paths():
            with self.subTest(path=path):
                instance = load_instance(path, self.dataset)
                instance_ids = {pokemon.id for pokemon in instance.candidates}
                self.assertEqual(len(instance_ids), instance.n)
                self.assertTrue(instance_ids.issubset(dataset_ids))

    def test_predefined_instances_are_nested(self) -> None:
        loaded = [
            load_instance(path, self.dataset)
            for path in predefined_instance_paths()
        ]
        for smaller, larger in zip(loaded, loaded[1:]):
            with self.subTest(smaller=smaller.name, larger=larger.name):
                self.assertTrue(
                    {pokemon.id for pokemon in smaller.candidates}.issubset(
                        {pokemon.id for pokemon in larger.candidates}
                    )
                )


if __name__ == "__main__":
    unittest.main()

