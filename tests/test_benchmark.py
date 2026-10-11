from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from pokemon_opt.benchmark import CSV_COLUMNS, optimality_gap, run_benchmark
from pokemon_opt.instances import predefined_instance_paths


class BenchmarkTests(unittest.TestCase):
    def test_optimality_gap(self) -> None:
        self.assertEqual(optimality_gap(100.0, 100.0), 0.0)
        self.assertAlmostEqual(optimality_gap(110.0, 100.0), 10.0)
        with self.assertRaises(ValueError):
            optimality_gap(1.0, 0.0)

    def test_exact_instance_records_optimum_and_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "benchmark.csv"
            result = run_benchmark(
                runs=3,
                output_path=output,
                exact_max_candidates=12,
                instance_paths=(predefined_instance_paths()[0],),
                max_iterations=10,
            )
            self.assertTrue(output.exists())
            self.assertEqual(len(result.records), 4)
            exact = result.records[0]
            self.assertEqual(exact.algorithm, "brute-force")
            self.assertEqual(exact.gap_pct, 0.0)
            self.assertEqual(exact.optimal_cost, exact.cost)
            for record in result.records[1:]:
                self.assertEqual(record.optimal_cost, exact.cost)
                self.assertIsNone(record.best_known_cost)
                self.assertGreaterEqual(record.gap_pct, 0.0)

    def test_large_instance_uses_best_known_not_optimum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_benchmark(
                runs=3,
                output_path=Path(directory) / "benchmark.csv",
                exact_max_candidates=0,
                instance_paths=(predefined_instance_paths()[1],),
                max_iterations=10,
            )
            self.assertEqual(len(result.records), 3)
            best = min(record.cost for record in result.records)
            self.assertTrue(all(record.optimal_cost is None for record in result.records))
            self.assertTrue(all(record.best_known_cost == best for record in result.records))
            self.assertEqual(min(record.gap_pct for record in result.records), 0.0)
            self.assertEqual(result.summaries[0].reference_label, "Best known")

    def test_csv_has_required_columns_and_complete_teams(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "benchmark.csv"
            run_benchmark(
                runs=2,
                output_path=output,
                exact_max_candidates=0,
                instance_paths=(predefined_instance_paths()[0],),
                max_iterations=5,
            )
            with output.open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(tuple(rows[0]), CSV_COLUMNS)
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(len(row["team"].split("; ")) == 6 for row in rows))
            self.assertEqual([row["seed"] for row in rows], ["0", "1"])

    def test_invalid_run_count_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_benchmark(runs=0)
        with self.assertRaises(ValueError):
            run_benchmark(runs=1, instance_paths=())
        with self.assertRaises(ValueError):
            run_benchmark(runs=1, exact_max_candidates=5)


if __name__ == "__main__":
    unittest.main()
