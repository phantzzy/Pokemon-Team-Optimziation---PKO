# Pokémon Team Defensive Typing Optimization

A Python 3.11+ combinatorial optimization project that selects exactly six
unique Pokémon with the lowest total defensive type-effectiveness cost. The
main optimizer is Simulated Annealing implemented manually from scratch. No
ready-made optimization or metaheuristic library is used.

Repository:
[Pokemon-Team-Optimziation---PKO](https://github.com/phantzzy/Pokemon-Team-Optimziation---PKO)

## Quick start

The project uses only the Python standard library. No installation is needed.

~~~powershell
python --version
python -m unittest discover -s tests -v
~~~

Open the responsive Pokédex-style interface:

~~~powershell
python main.py gui
~~~

Solve one instance with Simulated Annealing:

~~~powershell
python main.py solve --instance instances/medium_20.json --algorithm sa --seed 1
~~~

Solve a small instance exactly:

~~~powershell
python main.py solve --instance instances/medium_20.json --algorithm brute-force
~~~

Run the final benchmark:

~~~powershell
python main.py benchmark --runs 30 --output results/benchmark.csv
~~~

Brute force is enabled through 30 candidates by default. If necessary:

~~~powershell
python main.py benchmark --runs 30 --exact-max-candidates 20 --output results/benchmark.csv
~~~

## Problem formulation

Let P be the candidate set. A solution is an unordered subset T of P with
exactly six unique members. The search space contains C(N, 6) teams.

For attacking type t and Pokémon p, m(t,p) is the standard defensive
effectiveness multiplier. For dual types, both single-type multipliers are
multiplied. The objective is:

    minimize f(T) = sum over p in T and t in Types of m(t,p)

Lower cost means better average defensive typing. The reporting metric is:

    AverageMultiplier = f(T) / (6 * 18) = f(T) / 108

Only names and defensive types are modeled. Moves, stats, abilities, items,
EVs, IVs, Tera, weather, usage data, and battle simulation are excluded.

## Domain and instances

| Instance | Candidates | Possible teams |
|---|---:|---:|
| small_12 | 12 | 924 |
| medium_20 | 20 | 38,760 |
| medium_30 | 30 | 593,775 |
| large_50 | 50 | 15,890,700 |
| xlarge_100 | 100 | 1,192,052,400 |

Each Pokémon has a precomputed vector of 18 defensive multipliers. Team
evaluation sums the six vectors, so data files are never read in an
optimization loop.

## Neighborhood

A neighbor uses a 1-out / 1-in move:

1. choose one current team member uniformly at random;
2. choose one candidate outside the team uniformly at random;
3. replace the selected member.

The result always contains six unique candidates from the active instance.

## Simulated Annealing

The algorithm starts from a seeded random team. Better or equal-cost neighbors
are always accepted. A worse neighbor with difference delta greater than zero
is accepted with probability:

    P = exp(-delta / temperature)

Temperature is cooled geometrically with temperature = temperature * alpha.
The best solution is tracked separately from the current solution.

Default parameters:

- initial temperature: 10.0
- cooling rate: 0.995
- minimum temperature: 0.0001
- maximum iterations: 20000

The same instance, seed, and parameters reproduce the same result.

## Exact verification and benchmarking

The exact solver enumerates all six-member teams with
itertools.combinations. It is used to verify smaller instances, not as the
main optimizer.

For a proven optimum:

    Gap(%) = (SA - OPT) / OPT * 100

A zero-percent gap is optimal. For larger instances, the lowest cost observed
across all SA runs is labeled best-known, never proven optimal.

The benchmark uses seeds 0 through 29 by default and writes these columns:

    instance,n,algorithm,run,seed,cost,average_multiplier,runtime_ms,
    optimal_cost,best_known_cost,gap_pct,team

Unavailable values are left empty.

## Verified example

The following commands were verified on Python 3.11.9:

~~~powershell
python main.py solve --instance instances/small_12.json --algorithm sa --seed 17
python main.py solve --instance instances/small_12.json --algorithm brute-force
~~~

Both returned cost 108.75 and average multiplier 1.006944. The exact solver
evaluated all 924 teams. Runtime is deliberately omitted because it depends on
the computer.

The full automated suite currently contains 48 passing tests covering:

- standard single- and dual-type matchups;
- data loading and defensive vectors;
- deterministic, order-independent evaluation;
- neighborhood validity and reproducibility;
- SA validity, stopping rules, costs, and reproducibility;
- exact brute-force correctness;
- fixed instances;
- CLI solving;
- benchmark gaps, labels, records, and CSV output.

## Data

The local dataset contains 100 unique default-form species sampled
reproducibly with seed 2026. It includes every standard type. The 18 by 18
chart and Pokémon typings were obtained during development from
[PokéAPI](https://pokeapi.co/) and committed locally. Normal solving,
benchmarking, testing, and the GUI require no internet.

Regenerate the snapshot or instances with:

~~~powershell
python scripts/fetch_pokemon_data.py --count 100 --seed 2026
python scripts/create_instances.py
~~~

See [data/README.md](data/README.md) and
[data/POKEAPI_LICENSE.txt](data/POKEAPI_LICENSE.txt).

## Project structure

~~~text
main.py                         CLI and GUI entry point
pokemon_opt/
  benchmark.py                  repeated runs, gaps, CSV output
  brute_force.py                exact exhaustive verification
  data_loader.py                validated local JSON loading
  evaluation.py                 team cost and average multiplier
  gui.py                        responsive Pokédex-style interface
  instances.py                  fixed-instance loading
  models.py                     immutable Pokémon model
  neighborhood.py               1-out / 1-in move
  simulated_annealing.py        custom SA implementation
  solver.py                     shared CLI and GUI solve service
  type_chart.py                 type-effectiveness calculations
data/                           offline Pokémon data and type chart
instances/                      fixed 12, 20, 30, 50, and 100 sets
scripts/                        reproducible data-generation tools
tests/                          unittest suite
results/                        benchmark output location
~~~

## Scope and interpretation

This objective measures the sum of individual defensive typing multipliers. It
does not reward offensive coverage, roles, moves, or subjective team synergy.
That narrow scope is intentional: it keeps the combinatorial optimization
model precise, reproducible, and explainable in a short practical report.
