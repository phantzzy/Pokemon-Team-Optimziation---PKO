# Defensive Pokémon Team Optimization with Simulated Annealing

**Course:** Practical Combinatorial Optimization<br>
**Repository:** https://github.com/phantzzy/Pokemon-Team-Optimziation---PKO<br>
**Student:** Raivis Randohs<br>
**Date:** 11 October 2026

> The 30-run benchmark values below were generated on 11 October 2026. The
> student should review the results before submission.

## 1. Problem formulation

The problem is to choose a team of exactly six unique Pokémon from a fixed set
of N candidates. Only defensive typing is considered. Moves, statistics,
abilities, items, EVs, IVs, Tera types, usage data, and battle simulation are
outside the model.

Let P be the candidate set and T be a solution. A valid solution satisfies
T being a subset of P and the size of T being six. Team order is irrelevant,
so the number of possible solutions is C(N, 6). This grows from 924 teams for
N=12 to 1,192,052,400 teams for N=100, which motivates a metaheuristic for
larger instances.

For attacking type t and Pokémon p, m(t,p) is the standard type-effectiveness
multiplier. A single defending type has multiplier 0, 0.5, 1, or 2. For a
dual-type Pokémon, the multipliers for both defending types are multiplied,
so the final value can also be 0.25 or 4.

The cost of a team is:

    f(T) = sum over every p in T and every attacking type t of m(t,p)

The objective is to minimize f(T). A lower value represents better average
defensive typing. For interpretation, the program also reports:

    AverageMultiplier = f(T) / 108

because six Pokémon are evaluated against all 18 attacking types.

## 2. Implemented solution

### a) Domain

A solution is represented as six unique Pokémon from the active instance.
Five fixed instances contain 12, 20, 30, 50, and 100 candidates. Their
possible team counts are respectively 924; 38,760; 593,775; 15,890,700; and
1,192,052,400. The program validates instance membership, size, and
uniqueness.

The local dataset contains 100 species and a complete 18 by 18 type chart
derived from PokéAPI. Every Pokémon has an 18-value defensive vector
precomputed before optimization. Therefore, the inner search loop performs no
file or type-chart lookups.

### b) Evaluation

The evaluation function sums the six precomputed defensive vectors. It is
deterministic and independent of team order. The optimizer minimizes the raw
cost directly; average multiplier is only a reporting metric.

This criterion intentionally evaluates only individual defensive typing. It
does not model roles, offensive coverage, or battle synergy. This makes the
assignment mathematically clear and reproducible.

### c) Move and neighborhood

A neighboring solution is produced with a 1-out / 1-in swap:

1. randomly choose one current team member;
2. randomly choose one candidate not currently in the team;
3. replace the selected member.

The move always produces another valid six-member team with no duplicates.
All random choices use a local seeded random generator.

### d) Algorithm

Simulated Annealing was implemented manually without an optimization library.
The algorithm starts from a random valid team and stores it as both the
current and best solution. At every iteration, it creates one neighbor and
computes delta as candidate cost minus current cost.

If delta is zero or negative, the candidate is accepted. If delta is positive,
it is accepted with probability exp(-delta / temperature). This allows early
movement away from local optima. The temperature is multiplied by alpha after
each iteration. The run ends when the iteration limit is reached or the
temperature falls below the minimum. The best solution seen during the entire
run is returned separately from the final current solution.

The default parameters are initial temperature 10.0, alpha 0.995, minimum
temperature 0.0001, and at most 20,000 iterations. With the default cooling
schedule, the temperature condition currently ends a run after 2,297
iterations. The same seed, instance, and parameters reproduce the same team
and cost.

An exact solver separately enumerates all C(N, 6) combinations for small
instances. It proves the optimum and provides a comparison target; it is not
the main optimization algorithm.

## 3. Testing process and results

The implementation has 48 automated unit and integration tests. They cover
known single- and dual-type matchups, data validation, cost determinism,
neighborhood invariants, SA validity and reproducibility, stopping rules,
exact-solver correctness, CLI behavior, fixed instances, benchmark gaps, and
CSV output. All tests pass on Python 3.11.9.

For benchmarking, SA must be run 30 times on every instance with seeds 0
through 29. Execution time, cost, average multiplier, team, and gap are stored
for every run. For N up to 30, gap is computed against the proven optimum:

    Gap(%) = (SA - OPT) / OPT * 100

For N=50 and N=100, the lowest cost observed across the 30 SA runs is labeled
best-known rather than optimal.

The exact solver has already verified these costs:

| Instance | N | Possible teams | Proven optimum |
|---|---:|---:|---:|
| small_12 | 12 | 924 | 108.75 |
| medium_20 | 20 | 38,760 | 104.50 |
| medium_30 | 30 | 593,775 | 103.50 |

| Instance | Reference | SA best | SA average | SA worst | Average gap | Average runtime |
|---|---:|---:|---:|---:|---:|---:|
| small_12 | 108.75 optimal | 108.75 | 108.75 | 108.75 | 0.0000% | 9.418 ms |
| medium_20 | 104.50 optimal | 104.50 | 104.50 | 104.50 | 0.0000% | 11.242 ms |
| medium_30 | 103.50 optimal | 103.50 | 103.50 | 103.50 | 0.0000% | 12.652 ms |
| large_50 | 101.75 best-known | 101.75 | 101.75 | 101.75 | 0.0000% | 14.534 ms |
| xlarge_100 | 93.75 best-known | 93.75 | 93.75 | 93.75 | 0.0000% | 24.019 ms |

SA reached the proven optimum in all 30 runs for each of the 12-, 20-, and
30-candidate instances. Consequently, their best, average, and worst gaps
were all zero. Every run also returned the same cost for N=50 and N=100.
Those values are still only best-known because exhaustive search was not
performed at those sizes. Average runtime increased from 9.418 ms for N=12
to 24.019 ms for N=100, remaining practical for interactive use. The strong
consistency is plausible for this deliberately simple additive defensive-cost
model, but it does not prove that the two large-instance references are global
optima.

## 4. Conclusion

The project demonstrates a complete combinatorial optimization workflow:
formal domain definition, deterministic evaluation, a validity-preserving
neighborhood, manually implemented Simulated Annealing, exact verification on
small cases, reproducible experiments, and CSV reporting. The final results
should show whether the chosen default SA parameters consistently find exact
or near-exact defensive teams as the search space grows.
