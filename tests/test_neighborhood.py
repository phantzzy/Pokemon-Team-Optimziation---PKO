from __future__ import annotations

import random
import unittest

from pokemon_opt.data_loader import load_pokemon
from pokemon_opt.neighborhood import generate_neighbor


class NeighborhoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = load_pokemon()[:12]
        cls.team = cls.candidates[:6]

    def test_neighbor_preserves_all_solution_invariants(self) -> None:
        neighbor = generate_neighbor(
            self.team, self.candidates, random.Random(2026)
        )
        neighbor_ids = {pokemon.id for pokemon in neighbor}
        candidate_ids = {pokemon.id for pokemon in self.candidates}

        self.assertEqual(len(neighbor), 6)
        self.assertEqual(len(neighbor_ids), 6)
        self.assertTrue(neighbor_ids.issubset(candidate_ids))

    def test_neighbor_removes_and_adds_exactly_one_pokemon(self) -> None:
        neighbor = generate_neighbor(
            self.team, self.candidates, random.Random(2026)
        )
        original_ids = {pokemon.id for pokemon in self.team}
        neighbor_ids = {pokemon.id for pokemon in neighbor}

        self.assertEqual(len(original_ids - neighbor_ids), 1)
        self.assertEqual(len(neighbor_ids - original_ids), 1)

    def test_fixed_seed_is_reproducible(self) -> None:
        first = generate_neighbor(
            self.team, self.candidates, random.Random(42)
        )
        second = generate_neighbor(
            self.team, self.candidates, random.Random(42)
        )
        self.assertEqual(first, second)

    def test_input_team_is_not_modified(self) -> None:
        mutable_team = list(self.team)
        original = list(mutable_team)
        generate_neighbor(mutable_team, self.candidates, random.Random(7))
        self.assertEqual(mutable_team, original)

    def test_team_member_outside_candidate_set_is_rejected(self) -> None:
        invalid_candidates = self.candidates[1:]
        with self.assertRaises(ValueError):
            generate_neighbor(
                self.team, invalid_candidates, random.Random(1)
            )

    def test_duplicate_candidates_are_rejected(self) -> None:
        invalid_candidates = self.candidates[:-1] + (self.candidates[0],)
        with self.assertRaises(ValueError):
            generate_neighbor(
                self.team, invalid_candidates, random.Random(1)
            )

    def test_swap_requires_an_outside_candidate(self) -> None:
        with self.assertRaises(ValueError):
            generate_neighbor(self.team, self.team, random.Random(1))


if __name__ == "__main__":
    unittest.main()

