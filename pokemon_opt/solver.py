"""Shared application service used by both command-line and visual interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .brute_force import DEFAULT_MAX_CANDIDATES, brute_force
from .evaluation import average_multiplier
from .instances import ProblemInstance
from .models import Pokemon
from .simulated_annealing import (
    DEFAULT_ALPHA,
    DEFAULT_INITIAL_TEMPERATURE,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MIN_TEMPERATURE,
    simulated_annealing,
)


@dataclass(frozen=True, slots=True)
class SolveSummary:
    """Interface-neutral result for one optimization run."""

    instance_name: str
    n: int
    algorithm: str
    seed: int | None
    team: tuple[Pokemon, ...]
    cost: float
    average_multiplier: float
    runtime_ms: float
    iterations: int | None
    combinations_evaluated: int | None


def solve_problem(
    instance: ProblemInstance,
    algorithm: str,
    *,
    seed: int = 1,
    initial_temperature: float = DEFAULT_INITIAL_TEMPERATURE,
    alpha: float = DEFAULT_ALPHA,
    min_temperature: float = DEFAULT_MIN_TEMPERATURE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    brute_force_max_candidates: int | None = DEFAULT_MAX_CANDIDATES,
) -> SolveSummary:
    """Solve one validated instance using the selected algorithm."""
    start = perf_counter()
    if algorithm == "sa":
        result = simulated_annealing(
            instance.candidates,
            seed=seed,
            initial_temperature=initial_temperature,
            alpha=alpha,
            min_temperature=min_temperature,
            max_iterations=max_iterations,
        )
        team = result.best_team
        cost = result.best_cost
        iterations: int | None = result.iterations
        combinations_evaluated: int | None = None
        reported_seed: int | None = seed
    elif algorithm == "brute-force":
        result = brute_force(
            instance.candidates, max_candidates=brute_force_max_candidates
        )
        team = result.best_team
        cost = result.best_cost
        iterations = None
        combinations_evaluated = result.combinations_evaluated
        reported_seed = None
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    runtime_ms = (perf_counter() - start) * 1000
    return SolveSummary(
        instance_name=instance.name,
        n=instance.n,
        algorithm=algorithm,
        seed=reported_seed,
        team=team,
        cost=cost,
        average_multiplier=average_multiplier(cost),
        runtime_ms=runtime_ms,
        iterations=iterations,
        combinations_evaluated=combinations_evaluated,
    )


def format_solve_summary(summary: SolveSummary) -> str:
    """Format a solve result consistently for terminal and desktop output."""
    algorithm_name = (
        "Simulated Annealing"
        if summary.algorithm == "sa"
        else "Brute Force"
    )
    lines = [
        f"Instance: {summary.instance_name}",
        f"Candidates: {summary.n}",
        f"Algorithm: {algorithm_name}",
    ]
    if summary.seed is not None:
        lines.append(f"Seed: {summary.seed}")
    lines.extend(
        (
            f"Best cost: {summary.cost:g}",
            f"Average multiplier: {summary.average_multiplier:.6f}",
            f"Runtime: {summary.runtime_ms:.3f} ms",
        )
    )
    if summary.iterations is not None:
        lines.append(f"Iterations: {summary.iterations}")
    if summary.combinations_evaluated is not None:
        lines.append(
            f"Combinations evaluated: {summary.combinations_evaluated}"
        )
    lines.append("Team:")
    lines.extend(f"- {pokemon.name}" for pokemon in summary.team)
    return "\n".join(lines)

