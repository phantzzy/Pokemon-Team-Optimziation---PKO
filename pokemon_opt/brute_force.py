"""Exact brute-force solver used to verify small problem instances."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from time import perf_counter

from .evaluation import TEAM_SIZE
from .models import Pokemon


DEFAULT_MAX_CANDIDATES = 30


@dataclass(frozen=True, slots=True)
class BruteForceResult:
    """Proven optimum and execution metadata from exhaustive search."""

    best_team: tuple[Pokemon, ...]
    best_cost: float
    combinations_evaluated: int
    runtime_ms: float


def _validate_input(
    candidates: Sequence[Pokemon], max_candidates: int | None
) -> None:
    if len(candidates) < TEAM_SIZE:
        raise ValueError(
            f"At least {TEAM_SIZE} candidates are required to form a team"
        )
    candidate_ids = [pokemon.id for pokemon in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Candidate Pokemon must be unique")
    if max_candidates is not None:
        if (
            isinstance(max_candidates, bool)
            or not isinstance(max_candidates, int)
            or max_candidates < TEAM_SIZE
        ):
            raise ValueError(
                f"max_candidates must be at least {TEAM_SIZE} or None"
            )
        if len(candidates) > max_candidates:
            raise ValueError(
                f"Brute force is limited to {max_candidates} candidates; "
                f"received {len(candidates)}"
            )


def brute_force(
    candidates: Sequence[Pokemon],
    *,
    max_candidates: int | None = DEFAULT_MAX_CANDIDATES,
) -> BruteForceResult:
    """Enumerate every six-Pokemon team and return the proven optimum.

    Each Pokémon's contribution to the specified objective is independent, so
    its 18-value vector is summed once before enumeration. The algorithm still
    visits every combination, as required for exact brute-force verification.
    """
    _validate_input(candidates, max_candidates)
    prepared_candidates = tuple(candidates)
    individual_costs = {
        pokemon.id: sum(pokemon.defensive_vector)
        for pokemon in prepared_candidates
    }

    best_team: tuple[Pokemon, ...] | None = None
    best_cost = float("inf")
    combinations_evaluated = 0
    start = perf_counter()

    for team in combinations(prepared_candidates, TEAM_SIZE):
        cost = sum(individual_costs[pokemon.id] for pokemon in team)
        combinations_evaluated += 1
        if cost < best_cost:
            best_team = team
            best_cost = cost

    runtime_ms = (perf_counter() - start) * 1000
    if best_team is None:  # Guarded by the candidate-count validation above.
        raise RuntimeError("No valid team was generated")
    return BruteForceResult(
        best_team=best_team,
        best_cost=best_cost,
        combinations_evaluated=combinations_evaluated,
        runtime_ms=runtime_ms,
    )

