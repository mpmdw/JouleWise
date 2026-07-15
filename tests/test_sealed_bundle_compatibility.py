"""Regression tests for the canonical WO-003 sealed-corpus gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_sealed_bundle_compatibility.py"


class SealedBundleCompatibilityTests(unittest.TestCase):
    def run_gate(self, runs_root: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--runs-root",
                str(runs_root),
                "--output",
                str(output),
                "--verify",
                "exact,replay,ratio",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_absent_runs_root_is_a_loud_named_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "not-mounted"
            output = root / "receipt.json"
            completed = self.run_gate(missing, output)
            receipt = json.loads(output.read_text())

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("BOUNDARY retained_runs_root_absent", completed.stderr)
            self.assertEqual(receipt["result"], "boundary")
            self.assertEqual(receipt["boundary"]["name"], "retained_runs_root_absent")
            self.assertNotIn(str(root), json.dumps(receipt, sort_keys=True))

    def test_present_but_empty_corpus_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "runs"
            runs.mkdir()
            output = root / "receipt.json"
            completed = self.run_gate(runs, output)
            receipt = json.loads(output.read_text())

            self.assertEqual(completed.returncode, 2)
            self.assertIn("FAIL empty_corpus", completed.stderr)
            self.assertEqual(receipt["result"], "fail")
            self.assertEqual(receipt["failure_reasons"], ["empty_corpus"])
            self.assertEqual(receipt["corpus"]["bundle_count"], 0)
            self.assertNotIn(str(root), json.dumps(receipt, sort_keys=True))

    def test_incomplete_only_corpus_fails_and_reports_the_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "runs"
            incomplete = runs / "config-only"
            incomplete.mkdir(parents=True)
            (incomplete / "config.json").write_text("{}\n")
            output = root / "receipt.json"
            completed = self.run_gate(runs, output)
            receipt = json.loads(output.read_text())

            self.assertEqual(completed.returncode, 2)
            self.assertIn("FAIL empty_corpus", completed.stderr)
            self.assertEqual(receipt["result"], "fail")
            self.assertEqual(receipt["failure_reasons"], ["empty_corpus"])
            self.assertEqual(receipt["corpus"]["bundle_count"], 0)
            self.assertEqual(receipt["corpus"]["incomplete_directory_count"], 1)
            self.assertEqual(receipt["incomplete_directories"], ["config-only"])
            self.assertNotIn(str(root), json.dumps(receipt, sort_keys=True))

    def test_each_bundle_gets_explicit_selected_gate_dispositions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "runs"
            bundle = runs / "sealed-fixture"
            bundle.mkdir(parents=True)
            (bundle / "config.json").write_text("{}\n")
            (bundle / "metadata.json").write_text(
                json.dumps({"run_id": "sealed-fixture"}) + "\n"
            )
            (bundle / "summary_metrics.json").write_text(
                json.dumps(
                    {
                        "status": "failed",
                        "failure_reason": "unknown_error",
                        "failure_message": "compatibility fixture",
                    }
                )
                + "\n"
            )
            output = root / "receipt.json"
            completed = self.run_gate(runs, output)
            receipt = json.loads(output.read_text())

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(receipt["result"], "pass")
            self.assertEqual(
                receipt["corpus"],
                {
                    "logical_root": "runs",
                    "bundle_count": 1,
                    "incomplete_directory_count": 0,
                },
            )
            self.assertEqual(receipt["incomplete_directories"], [])
            gates = receipt["bundles"][0]["gates"]
            for gate_name in ("exact", "replay", "ratio"):
                self.assertIs(gates[gate_name]["eligible"], False)
                self.assertTrue(gates[gate_name]["revocation_reasons"])
            self.assertNotIn(str(root), json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
