"""Subprocess CLI checks read only temporary synthetic JSON."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.interp_energy.edit_frontier import synthetic_demo


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "interp_energy" / "edit_frontier.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="edit-frontier-synthetic-")
        self.addCleanup(self.directory.cleanup)
        self.input = Path(self.directory.name) / "input.json"
        self.data = synthetic_demo()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args),
                               "--bootstrap-samples", "100"], cwd=ROOT, text=True,
                              capture_output=True, timeout=20)

    def write(self):
        self.input.write_text(json.dumps(self.data), encoding="utf-8")

    def test_demo_outputs_strict_json_and_repeats_exactly(self):
        run = self.run_cli("--demo", "--seed", "11")
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(report["model_id"], "synthetic-only")
        self.assertEqual(len(report["variants"]), 4)
        self.assertEqual(report["frontiers"]["predicted_per_answer"]["members"],
                         ["base_off", "length_lower", "length_raise"])
        self.assertNotIn("observed_per_answer", report["frontiers"])
        self.assertEqual(run.stdout, self.run_cli("--demo", "--seed", "11").stdout)

    def test_explicit_input_remains_immutable_and_sources_are_opaque(self):
        # A nonexistent path is just provenance; no source file is accessed.
        for variant in self.data["variants"]:
            variant["model"]["source"] = "opaque://not-a-file-or-network-request"
        self.write()
        before = self.input.read_bytes()
        run = self.run_cli(self.input)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(before, self.input.read_bytes())

    def test_unknown_fields_and_missing_provenance_fail(self):
        for mutate in (
            lambda d: d.update(unknown=1),
            lambda d: d["variants"][0].update(unknown=1),
            lambda d: d["variants"][0]["model"].pop("source"),
            lambda d: d["variants"][0]["model"].pop("coefficient_basis"),
            lambda d: d["variants"][0]["answers"][0].update(unknown=1),
        ):
            self.data = synthetic_demo()
            mutate(self.data)
            self.write()
            with self.subTest(data=self.data):
                run = self.run_cli(self.input)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")

    def test_duplicate_keys_nonfinite_and_overflow_fail(self):
        for text in ('{"variants": [], "variants": []}', '{"x": NaN}', '{"x": Infinity}'):
            self.input.write_text(text, encoding="utf-8")
            run = self.run_cli(self.input)
            self.assertEqual(run.returncode, 2)
        self.data["variants"][0]["model"]["decode_j_per_token"] = 1e308
        self.write()
        run = self.run_cli(self.input)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")

    def test_requires_exactly_one_input(self):
        self.write()
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.run_cli(self.input, "--demo").returncode, 2)


if __name__ == "__main__":
    unittest.main()
