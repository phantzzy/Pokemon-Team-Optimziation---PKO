# Final student checklist

Deadline: **11 October 2026 at 23:59 (Europe/Riga)**

## Run and verify

- [ ] Open PowerShell in the repository.
- [ ] Run all tests:

      python -m unittest discover -s tests -v

- [ ] Run the final experiment personally:

      python main.py benchmark --runs 30 --output results/benchmark.csv

- [ ] Open results/benchmark.csv and confirm it contains 153 rows:
      150 SA rows and 3 exact-solver rows.
- [ ] Check that small instances say optimal and large instances say
      best-known.
- [ ] Check for unreasonable costs, missing teams, missing seeds, or empty
      runtimes.
- [ ] Commit and push the final benchmark.csv.

## Finish the report

- [ ] Copy REPORT_DRAFT.md into the preferred editor.
- [ ] Insert your name and date.
- [ ] Replace every bracketed result placeholder using benchmark.csv.
- [ ] Add one short paragraph interpreting the results.
- [ ] Keep the final report within 2–3 pages.
- [ ] Keep this repository link in the report:
      https://github.com/phantzzy/Pokemon-Team-Optimziation---PKO
- [ ] Export and reopen the PDF to inspect layout and readability.

## Be ready to explain

- [ ] Domain: every six-element subset of the candidate set.
- [ ] Cost: sum of 108 defensive multipliers; lower is better.
- [ ] Move: one current member out and one outside candidate in.
- [ ] SA: better moves accepted; worse moves may be accepted according to
      exp(-delta / temperature); temperature decreases over time.
- [ ] Exact versus best-known: exact search proves an optimum, while the best
      large-instance SA result is only a reference.

## Submit

- [ ] Confirm the lecturer accepts the chosen defensive criterion if this is
      still uncertain.
- [x] Confirm the GitHub repository is accessible.
- [ ] Upload the final PDF to e-studies before 23:59.
- [ ] Verify that the submission is visible after upload.
