"""A from-scratch Simulated Annealing solver for Pokemon teams."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from .evaluation import TEAM_SIZE, team_cost, validate_team
from .models import Pokemon
from .neighborhood import generate_neighbor


DEFAULT_INITIAL_TEMPERATURE = 10.0
DEFAULT_ALPHA = 0.995
DEFAULT_MIN_TEMPERATURE = 0.0001
DEFAULT_MAX_ITERATIONS = 20_000


@dataclass(frozen=True, slots=True)
class SimulatedAnnealingResult:
    """Best solution and diagnostic information from one SA run."""

    best_team: tuple[Pokemon, ...]
    best_cost: float
    initial_team: tuple[Pokemon, ...]
    initial_cost: float
    final_team: tuple[Pokemon, ...]
    final_cost: float
    iterations: int
    final_temperature: float
    accepted_moves: int


def _validate_candidates(candidates: Sequence[Pokemon]) -> None:
    if len(candidates) <= TEAM_SIZE:
        raise ValueError(
            f"Simulated Annealing requires at least {TEAM_SIZE + 1} candidates"
        )
    candidate_ids = [pokemon.id for pokemon in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Candidate Pokemon must be unique")


def _validate_parameters(
    initial_temperature: float,
    alpha: float,
    min_temperature: float,
    max_iterations: int,
) -> None:
    if not math.isfinite(initial_temperature) or initial_temperature <= 0:
        raise ValueError("initial_temperature must be a positive finite number")
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if not math.isfinite(min_temperature) or min_temperature <= 0:
        raise ValueError("min_temperature must be a positive finite number")
    if min_temperature >= initial_temperature:
        raise ValueError("min_temperature must be below initial_temperature")
    if (
        isinstance(max_iterations, bool)
        or not isinstance(max_iterations, int)
        or max_iterations <= 0
    ):
        raise ValueError("max_iterations must be a positive integer")


def _prepare_initial_team(
    candidates: Sequence[Pokemon],
    rng: random.Random,
    initial_team: Sequence[Pokemon] | None,
) -> tuple[Pokemon, ...]:
    if initial_team is None:
        return tuple(rng.sample(list(candidates), TEAM_SIZE))

    prepared = tuple(initial_team)
    validate_team(prepared)
    candidate_ids = {pokemon.id for pokemon in candidates}
    if any(pokemon.id not in candidate_ids for pokemon in prepared):
        raise ValueError("Every initial team member must belong to the candidates")
    return prepared


def simulated_annealing(
    candidates: Sequence[Pokemon],
    *,
    seed: int | None = None,
    initial_temperature: float = DEFAULT_INITIAL_TEMPERATURE,
    alpha: float = DEFAULT_ALPHA,
    min_temperature: float = DEFAULT_MIN_TEMPERATURE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    initial_team: Sequence[Pokemon] | None = None,
) -> SimulatedAnnealingResult:
    """Minimize defensive team cost with manually implemented SA.

    Better and equal-cost neighbors are always accepted. A worse neighbor with
    cost difference ``delta`` is accepted when a uniform random value is less
    than ``exp(-delta / temperature)``. The best solution seen during the
    entire run is retained independently from the current solution.
    """
    _validate_candidates(candidates)
    _validate_parameters(
        initial_temperature, alpha, min_temperature, max_iterations
    )

    rng = random.Random(seed)
    current_team = _prepare_initial_team(candidates, rng, initial_team)
    current_cost = team_cost(current_team)
    initial_team_snapshot = current_team
    initial_cost = current_cost
    best_team = current_team
    best_cost = current_cost
    temperature = float(initial_temperature)
    iterations = 0
    accepted_moves = 0

    while iterations < max_iterations and temperature >= min_temperature:
        candidate_team = generate_neighbor(current_team, candidates, rng)
        candidate_cost = team_cost(candidate_team)
        delta = candidate_cost - current_cost

        accepted = delta <= 0
        if not accepted:
            acceptance_probability = math.exp(-delta / temperature)
            accepted = rng.random() < acceptance_probability

        if accepted:
            current_team = candidate_team
            current_cost = candidate_cost
            accepted_moves += 1
            if current_cost < best_cost:
                best_team = current_team
                best_cost = current_cost

        temperature *= alpha
        iterations += 1

    return SimulatedAnnealingResult(
        best_team=best_team,
        best_cost=best_cost,
        initial_team=initial_team_snapshot,
        initial_cost=initial_cost,
        final_team=current_team,
        final_cost=current_cost,
        iterations=iterations,
        final_temperature=temperature,
        accepted_moves=accepted_moves,
    )
