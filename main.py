"""Command-line entry point for Pokemon team optimization."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from pokemon_opt.brute_force import DEFAULT_MAX_CANDIDATES
from pokemon_opt.instances import load_instance
from pokemon_opt.simulated_annealing import (
    DEFAULT_ALPHA,
    DEFAULT_INITIAL_TEMPERATURE,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MIN_TEMPERATURE,
)
from pokemon_opt.solver import format_solve_summary, solve_problem


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optimize six-Pokemon teams by defensive typing."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="solve one instance")
    solve_parser.add_argument("--instance", required=True, help="instance JSON path")
    solve_parser.add_argument(
        "--algorithm", required=True, choices=("sa", "brute-force")
    )
    solve_parser.add_argument("--seed", type=int, default=1)
    solve_parser.add_argument(
        "--initial-temperature", type=float, default=DEFAULT_INITIAL_TEMPERATURE
    )
    solve_parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    solve_parser.add_argument(
        "--min-temperature", type=float, default=DEFAULT_MIN_TEMPERATURE
    )
    solve_parser.add_argument(
        "--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS
    )
    solve_parser.add_argument(
        "--brute-force-max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
    )

    subparsers.add_parser("gui", help="open the visual desktop interface")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "gui":
        from pokemon_opt.gui import launch_gui

        try:
            launch_gui()
        except RuntimeError as error:
            parser.error(str(error))
        return 0

    try:
        instance = load_instance(args.instance)
        summary = solve_problem(
            instance,
            args.algorithm,
            seed=args.seed,
            initial_temperature=args.initial_temperature,
            alpha=args.alpha,
            min_temperature=args.min_temperature,
            max_iterations=args.max_iterations,
            brute_force_max_candidates=args.brute_force_max_candidates,
        )
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    print(format_solve_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

