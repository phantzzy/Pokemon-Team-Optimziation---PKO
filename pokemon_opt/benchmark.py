"""Repeatable benchmarking, comparison, and CSV reporting."""

from __future__ import annotations

import csv
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .instances import load_instance, predefined_instance_paths
from .simulated_annealing import (
    DEFAULT_ALPHA,
    DEFAULT_INITIAL_TEMPERATURE,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MIN_TEMPERATURE,
)
from .solver import SolveSummary, solve_problem

CSV_COLUMNS = (
    "instance", "n", "algorithm", "run", "seed", "cost",
    "average_multiplier", "runtime_ms", "optimal_cost",
    "best_known_cost", "gap_pct", "team",
)


@dataclass(frozen=True, slots=True)
class BenchmarkRecord:
    """One row in the benchmark CSV."""

    instance: str
    n: int
    algorithm: str
    run: int
    seed: int | None
    cost: float
    average_multiplier: float
    runtime_ms: float
    optimal_cost: float | None
    best_known_cost: float | None
    gap_pct: float
    team: str


@dataclass(frozen=True, slots=True)
class InstanceBenchmarkSummary:
    """Aggregate SA statistics for one problem instance."""

    instance: str
    n: int
    runs: int
    reference_label: str
    reference_cost: float
    sa_best: float
    sa_average: float
    sa_worst: float
    average_gap_pct: float
    best_gap_pct: float
    average_runtime_ms: float


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """Complete benchmark records, summaries, and output location."""

    records: tuple[BenchmarkRecord, ...]
    summaries: tuple[InstanceBenchmarkSummary, ...]
    output_path: Path


def optimality_gap(cost: float, reference_cost: float) -> float:
    """Return the minimization gap percentage relative to a reference cost."""
    if reference_cost <= 0:
        raise ValueError("Reference cost must be positive")
    return (cost - reference_cost) / reference_cost * 100.0


def _record(
    summary: SolveSummary,
    *,
    run: int,
    optimal_cost: float | None,
    best_known_cost: float | None,
    reference_cost: float,
) -> BenchmarkRecord:
    return BenchmarkRecord(
        instance=summary.instance_name,
        n=summary.n,
        algorithm=summary.algorithm,
        run=run,
        seed=summary.seed,
        cost=summary.cost,
        average_multiplier=summary.average_multiplier,
        runtime_ms=summary.runtime_ms,
        optimal_cost=optimal_cost,
        best_known_cost=best_known_cost,
        gap_pct=optimality_gap(summary.cost, reference_cost),
        team="; ".join(pokemon.name for pokemon in summary.team),
    )


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10f}".rstrip("0").rstrip(".")
    return value


def write_benchmark_csv(
    path: str | Path, records: tuple[BenchmarkRecord, ...]
) -> Path:
    """Write benchmark records using the assignment's required columns."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {key: _csv_value(value) for key, value in asdict(record).items()}
            )
    return output_path


def run_benchmark(
    *,
    runs: int = 30,
    output_path: str | Path = "results/benchmark.csv",
    exact_max_candidates: int = 30,
    instance_paths: tuple[Path, ...] | None = None,
    initial_temperature: float = DEFAULT_INITIAL_TEMPERATURE,
    alpha: float = DEFAULT_ALPHA,
    min_temperature: float = DEFAULT_MIN_TEMPERATURE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> BenchmarkResult:
    """Benchmark SA on every instance and exact search on configured sizes."""
    if isinstance(runs, bool) or not isinstance(runs, int) or runs <= 0:
        raise ValueError("runs must be a positive integer")
    if (
        isinstance(exact_max_candidates, bool)
        or not isinstance(exact_max_candidates, int)
        or (exact_max_candidates != 0 and exact_max_candidates < 6)
    ):
        raise ValueError("exact_max_candidates must be 0 or at least 6")
    paths = predefined_instance_paths() if instance_paths is None else instance_paths
    if not paths:
        raise ValueError("At least one benchmark instance is required")

    all_records: list[BenchmarkRecord] = []
    summaries: list[InstanceBenchmarkSummary] = []
    for path in paths:
        instance = load_instance(path)
        exact: SolveSummary | None = None
        if exact_max_candidates and instance.n <= exact_max_candidates:
            exact = solve_problem(
                instance,
                "brute-force",
                brute_force_max_candidates=exact_max_candidates,
            )
        sa_runs = [
            solve_problem(
                instance,
                "sa",
                seed=seed,
                initial_temperature=initial_temperature,
                alpha=alpha,
                min_temperature=min_temperature,
                max_iterations=max_iterations,
            )
            for seed in range(runs)
        ]

        if exact is not None:
            reference_cost = exact.cost
            optimal_cost: float | None = exact.cost
            best_known_cost: float | None = None
            reference_label = "Optimal"
            all_records.append(
                _record(
                    exact,
                    run=0,
                    optimal_cost=exact.cost,
                    best_known_cost=None,
                    reference_cost=exact.cost,
                )
            )
        else:
            reference_cost = min(result.cost for result in sa_runs)
            optimal_cost = None
            best_known_cost = reference_cost
            reference_label = "Best known"

        sa_records = [
            _record(
                result,
                run=index,
                optimal_cost=optimal_cost,
                best_known_cost=best_known_cost,
                reference_cost=reference_cost,
            )
            for index, result in enumerate(sa_runs, start=1)
        ]
        all_records.extend(sa_records)
        costs = [record.cost for record in sa_records]
        gaps = [record.gap_pct for record in sa_records]
        runtimes = [record.runtime_ms for record in sa_records]
        summaries.append(
            InstanceBenchmarkSummary(
                instance=instance.name,
                n=instance.n,
                runs=runs,
                reference_label=reference_label,
                reference_cost=reference_cost,
                sa_best=min(costs),
                sa_average=statistics.fmean(costs),
                sa_worst=max(costs),
                average_gap_pct=statistics.fmean(gaps),
                best_gap_pct=min(gaps),
                average_runtime_ms=statistics.fmean(runtimes),
            )
        )

    records_tuple = tuple(all_records)
    written_path = write_benchmark_csv(output_path, records_tuple)
    return BenchmarkResult(records_tuple, tuple(summaries), written_path)


def format_benchmark_summary(result: BenchmarkResult) -> str:
    """Format concise per-instance benchmark statistics for the console."""
    blocks: list[str] = []
    for summary in result.summaries:
        blocks.append(
            "\n".join(
                (
                    f"Instance: {summary.instance} (N={summary.n})",
                    f"Runs: {summary.runs}",
                    f"{summary.reference_label}: {summary.reference_cost:g}",
                    f"SA best: {summary.sa_best:g}",
                    f"SA average: {summary.sa_average:.4f}",
                    f"SA worst: {summary.sa_worst:g}",
                    f"Average gap: {summary.average_gap_pct:.4f}%",
                    f"Best gap: {summary.best_gap_pct:.4f}%",
                    f"Average runtime: {summary.average_runtime_ms:.3f} ms",
                )
            )
        )
    blocks.append(f"CSV: {result.output_path}")
    return "\n\n".join(blocks)
