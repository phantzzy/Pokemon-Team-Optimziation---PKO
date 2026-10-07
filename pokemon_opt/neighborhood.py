"""Neighborhood operations for candidate Pokemon teams."""

from __future__ import annotations

import random
from collections.abc import Sequence

from .evaluation import TEAM_SIZE, validate_team
from .models import Pokemon


def generate_neighbor(
    team: Sequence[Pokemon],
    candidates: Sequence[Pokemon],
    rng: random.Random,
) -> tuple[Pokemon, ...]:
    """Create a neighboring team with one member removed and one added.

    The input sequences are not modified. Randomness is supplied explicitly so
    the same team, candidate ordering, and seeded generator produce the same
    neighbor.
    """
    validate_team(team)
    if len(candidates) <= TEAM_SIZE:
        raise ValueError(
            f"At least {TEAM_SIZE + 1} candidates are required to make a swap"
        )

    candidate_ids = [pokemon.id for pokemon in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Candidate Pokemon must be unique")

    team_ids = {pokemon.id for pokemon in team}
    if not team_ids.issubset(candidate_ids):
        raise ValueError("Every team member must belong to the candidate set")

    outside_candidates = [
        pokemon for pokemon in candidates if pokemon.id not in team_ids
    ]
    if not outside_candidates:
        raise ValueError("The candidate set has no Pokemon outside the team")

    remove_index = rng.randrange(TEAM_SIZE)
    added_pokemon = rng.choice(outside_candidates)
    neighbor = list(team)
    neighbor[remove_index] = added_pokemon
    result = tuple(neighbor)

    # Keep the invariant check close to the move that is responsible for it.
    validate_team(result)
    return result

