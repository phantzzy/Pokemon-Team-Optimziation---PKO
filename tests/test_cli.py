from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "main.py", *arguments],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sa_solve_command(self) -> None:
        result = self.run_cli(
            "solve",
            "--instance",
            "instances/small_12.json",
            "--algorithm",
            "sa",
            "--seed",
            "3",
            "--max-iterations",
            "10",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Algorithm: Simulated Annealing", result.stdout)
        self.assertIn("Seed: 3", result.stdout)
        self.assertEqual(result.stdout.count("\n- "), 6)

    def test_brute_force_solve_command(self) -> None:
        result = self.run_cli(
            "solve",
            "--instance",
            "instances/small_12.json",
            "--algorithm",
            "brute-force",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Algorithm: Brute Force", result.stdout)
        self.assertIn("Combinations evaluated: 924", result.stdout)

    def test_missing_instance_has_user_friendly_error(self) -> None:
        result = self.run_cli(
            "solve",
            "--instance",
            "instances/missing.json",
            "--algorithm",
            "sa",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Instance file not found", result.stderr)


if __name__ == "__main__":
    unittest.main()

