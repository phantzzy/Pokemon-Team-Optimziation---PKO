"""Objective function for defensive team typing."""

from __future__ import annotations

from collections.abc import Sequence

from .models import Pokemon
from .type_chart import TYPE_NAMES


TEAM_SIZE = 6
TEAM_MATCHUP_COUNT = TEAM_SIZE * len(TYPE_NAMES)


def validate_team(team: Sequence[Pokemon]) -> None:
    """Ensure a solution contains exactly six unique Pokemon."""
    if len(team) != TEAM_SIZE:
        raise ValueError(f"A team must contain exactly {TEAM_SIZE} Pokemon")
    ids = [pokemon.id for pokemon in team]
    if len(ids) != len(set(ids)):
        raise ValueError("A team cannot contain duplicate Pokemon")


def team_cost(team: Sequence[Pokemon]) -> float:
    """Sum all 108 attack-type/Pokemon defensive multipliers."""
    validate_team(team)
    return sum(sum(pokemon.defensive_vector) for pokemon in team)


def average_multiplier(cost: float) -> float:
    """Convert a six-Pokemon team cost into its human-readable mean."""
    if cost < 0:
        raise ValueError("Team cost cannot be negative")
    return cost / TEAM_MATCHUP_COUNT

