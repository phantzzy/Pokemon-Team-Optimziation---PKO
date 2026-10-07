# Pokémon Team Optimization — TODO

This checklist tracks the complete practical-assignment scope. Checked items
have been implemented and verified locally unless stated otherwise.

## 1. Repository and project setup

- [x] Create the GitHub repository.
- [x] Initialize the local Git repository with the `main` branch.
- [x] Connect the local repository to GitHub over HTTPS.
- [x] Add a Python-focused `.gitignore`.
- [x] Push the initial data/importer commit to GitHub.
- [ ] Commit and push the latest model, evaluation, tests, and this checklist.
- [ ] Add the complete final project structure.

## 2. Pokémon data and type chart

- [x] Select PokéAPI as the development-time data source.
- [x] Implement a standard-library-only PokéAPI importer.
- [x] Use a local `User-Agent`, retries, timeouts, and concurrent fetching.
- [x] Retrieve the full species index exposed by PokéAPI.
- [x] Select a reproducible 100-species sample with seed `2026`.
- [x] Keep one default form per species.
- [x] Retrieve English names and one or two defensive types.
- [x] Store the local dataset in `data/pokemon.json`.
- [x] Generate the complete standard 18×18 type chart.
- [x] Store the chart in `data/type_chart.json`.
- [x] Verify that all 18 standard types are represented in the dataset.
- [x] Verify that all 100 Pokémon names and IDs are unique.
- [x] Document the data source, format, seed, and regeneration command.
- [x] Include the PokéAPI BSD 3-Clause license.
- [x] Ensure the optimizer will not require internet access at runtime.

## 3. Domain model and data loading

- [x] Create the `pokemon_opt` Python package.
- [x] Define the canonical ordering of the 18 Pokémon types.
- [x] Add an immutable, typed `Pokemon` model.
- [x] Implement validated loading of `pokemon.json`.
- [x] Implement validated loading of `type_chart.json`.
- [x] Reject missing, malformed, duplicate, and invalid data.
- [x] Precompute an 18-value defensive vector for every Pokémon.
- [x] Keep JSON and type-chart work outside optimization loops.

## 4. Type effectiveness and objective function

- [x] Implement single-type defensive effectiveness.
- [x] Implement dual-type effectiveness by multiplying both type multipliers.
- [x] Implement six-member team validation.
- [x] Reject duplicate Pokémon in a team.
- [x] Implement the required team cost function.
- [x] Implement average multiplier reporting as `cost / 108`.
- [x] Confirm that team cost is deterministic.
- [x] Confirm that team order does not affect cost.

## 5. Tests completed so far

- [x] Test that the type chart is a complete 18×18 matrix.
- [x] Test `Electric -> Ground = 0`.
- [x] Test `Fire -> Grass = 2`.
- [x] Test `Fire -> Water = 0.5`.
- [x] Test `Normal -> Ghost = 0`.
- [x] Test `Fighting -> Normal = 2`.
- [x] Test `Ice -> Dragon = 2`.
- [x] Test `Electric -> Water/Ground = 0`.
- [x] Test `Grass -> Water/Ground = 4`.
- [x] Test `Fire -> Bug/Steel = 4`.
- [x] Test `Rock -> Fire/Flying = 4`.
- [x] Test dataset loading and defensive-vector construction.
- [x] Test deterministic and order-independent team evaluation.
- [x] Test average multiplier calculation.
- [x] Test invalid team size and duplicate-team rejection.
- [x] Run the current suite successfully: 42 tests passing.
- [x] Compile the current package and tests successfully.

## 6. Neighborhood move

- [x] Implement the separate `generate_neighbor(team, candidates, rng)` function.
- [x] Randomly select one current team member to remove.
- [x] Randomly select one outside candidate to add.
- [x] Preserve a team size of exactly six.
- [x] Prevent duplicate Pokémon.
- [x] Ensure every member belongs to the active instance.
- [x] Test that exactly one member is removed and one is added.
- [x] Test deterministic neighbor generation with a fixed random seed.

## 7. Simulated Annealing

- [x] Implement Simulated Annealing manually without optimization libraries.
- [x] Generate a random valid initial team using a local `random.Random(seed)`.
- [x] Use the required 1-out/1-in neighborhood.
- [x] Always accept candidates with `delta <= 0`.
- [x] Accept worse candidates with probability `exp(-delta / temperature)`.
- [x] Track the current solution separately from the best solution.
- [x] Apply geometric cooling with `temperature *= alpha`.
- [x] Stop at the iteration limit or minimum temperature.
- [x] Use the default initial temperature `10.0`.
- [x] Use the default cooling rate `0.995`.
- [x] Use the default minimum temperature `0.0001`.
- [x] Use the default maximum iteration count `20000`.
- [x] Make all important parameters configurable.
- [x] Return the best team, cost, iterations, and relevant run metadata.
- [x] Test that SA always returns a valid team.
- [x] Test fixed-seed reproducibility.
- [x] Test that the best result is not worse than the initial solution.
- [x] Test that the reported cost matches a fresh evaluation.

## 8. Exact brute-force solver

- [x] Implement a separate solver using `itertools.combinations`.
- [x] Enumerate every possible six-Pokémon team in an instance.
- [x] Return the proven optimal team and cost.
- [x] Measure brute-force runtime.
- [x] Add a configurable maximum instance-size threshold.
- [x] Avoid brute force on large instances by default.
- [x] Add a small synthetic instance with a manually verifiable optimum.
- [x] Test that brute force returns the expected optimum.

## 9. Fixed problem instances

- [x] Create `instances/small_12.json`.
- [x] Create `instances/medium_20.json`.
- [x] Create `instances/medium_30.json`.
- [x] Create `instances/large_50.json`.
- [x] Create `instances/xlarge_100.json`.
- [x] Keep every instance fixed and reproducible.
- [x] Validate instance names, sizes, uniqueness, and dataset membership.
- [x] Add a reproducible instance-generation script.

## 10. Command-line interface

- [x] Create `main.py`.
- [x] Add the `solve` command.
- [x] Support `--algorithm sa`.
- [x] Support `--algorithm brute-force`.
- [x] Support `--instance`.
- [x] Support `--seed`.
- [x] Expose relevant SA parameters as CLI options.
- [x] Print the instance, algorithm, seed, team, cost, average multiplier, and runtime.
- [x] Add clear validation and user-friendly error messages.

### Visual interface

- [x] Add a Tkinter desktop interface without third-party dependencies.
- [x] Add predefined-instance selection and custom JSON browsing.
- [x] Support Simulated Annealing and brute force.
- [x] Expose seeds, SA parameters, and the brute-force size limit.
- [x] Run optimization in a background thread to keep the window responsive.
- [x] Display the selected team, cost, average multiplier, runtime, and run metadata.
- [x] Reuse the same validated loading and solving service as the CLI.
- [x] Add the `python main.py gui` launch command.

## 11. Benchmarking and CSV results

- [ ] Implement the `benchmark` command.
- [ ] Run SA 30 times per instance with seeds `0..29` by default.
- [ ] Measure every run's execution time.
- [ ] Record every returned team and cost.
- [ ] Run exact brute force for configured small instances.
- [ ] Record the proven optimal cost and team where available.
- [ ] Compute exact optimality gaps where an optimum is known.
- [ ] Compute and clearly label best-known results for large instances.
- [ ] Never label a best-known solution as a proven optimum.
- [ ] Write `results/benchmark.csv` with all required columns.
- [ ] Print concise per-instance summaries.
- [ ] Add tests for benchmark records, gaps, and CSV output.

Required CSV columns:

- [ ] `instance`
- [ ] `n`
- [ ] `algorithm`
- [ ] `run`
- [ ] `seed`
- [ ] `cost`
- [ ] `average_multiplier`
- [ ] `runtime_ms`
- [ ] `optimal_cost`
- [ ] `best_known_cost`
- [ ] `gap_pct`
- [ ] `team`

## 12. Final verification

- [ ] Run the complete unit-test suite.
- [ ] Run a standalone SA solve through the CLI.
- [ ] Run a standalone brute-force solve through the CLI.
- [ ] Confirm identical seeds and parameters reproduce identical SA results.
- [ ] Run at least one smoke benchmark.
- [ ] Check that benchmark CSV output opens correctly.
- [ ] Check all documented commands on Python 3.11+.
- [ ] Review the repository for unnecessary dependencies or features.
- [ ] Confirm no ready-made optimization implementation is used.
- [ ] Fix all discovered bugs.
- [ ] Commit and push the finished implementation.

## 13. README and report support

- [ ] Create the main project `README.md`.
- [ ] Explain the project goal and exact problem formulation.
- [ ] Explain the domain and solution-space size.
- [ ] Explain the cost function and average multiplier.
- [ ] Explain the 1-out/1-in neighborhood.
- [ ] Explain the custom Simulated Annealing implementation.
- [ ] State explicitly that no ready-made optimizer is used.
- [ ] Document installation, solve, test, and benchmark commands.
- [ ] Document the project structure and data source.
- [ ] Include verified example output.
- [ ] Explain optimality gap and best-known results.
- [ ] Prepare concise report-ready summaries and result tables.
- [ ] Do not fabricate benchmark results.

## 14. Student responsibilities

- [ ] Confirm the final optimization criterion with the lecturer if necessary.
- [ ] Run the completed code on the student's computer.
- [ ] Run and inspect the final benchmark.
- [ ] Verify that all results are reasonable.
- [ ] Keep the final `benchmark.csv` in the repository.
- [ ] Select representative results for the report.
- [ ] Prepare the final 2–3 page PDF report.
- [ ] Insert the GitHub repository link into the report.
- [ ] Be able to explain the domain, cost, neighborhood, and SA algorithm.
- [ ] Submit the PDF in e-studies by 11 October at 23:59.
