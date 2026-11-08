"""Exercise the real offline CLI against temporary synthetic JSON only."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "interp_energy" / "behaviour_energy.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="interp-energy-synthetic-")
        self.addCleanup(self.directory.cleanup)
        self.input = Path(self.directory.name) / "input.json"
        self.data = {"base_model": {
            "prefill_j_per_token": 0.02, "decode_j_per_token": 0.1,
            "context_j_per_token_squared": 0.0000005, "coefficient_basis": "above_idle",
            "source": "synthetic CLI fixture; opaque provenance only",
        }}

    def run_cli(self, command, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), command,
                               str(self.input), *args], cwd=ROOT, text=True,
                              capture_output=True, timeout=20)

    def write(self):
        self.input.write_text(json.dumps(self.data), encoding="utf-8")

    def add_answers(self):
        self.data["base"] = [{"problem_id": str(i), "prefill_tokens": 20,
                              "decode_tokens": 100 + i, "correct": i % 2 == 0} for i in range(6)]
        self.data["edited"] = [{**row, "decode_tokens": 60} for row in self.data["base"]]

    def test_scenario_cli_has_three_projections_and_never_changes_input(self):
        self.write()
        before = self.input.read_bytes()
        process = self.run_cli("scenario", "--prefill-tokens", "256")
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(len(report["scenarios"]), 3)
        self.assertIn("not_measurement", report["status"])
        self.assertLess(report["scenarios"][0]["per_answer"]["delta_j"], 0)
        self.assertEqual(self.input.read_bytes(), before)

    def test_compare_cli_supports_distinct_models_and_seeded_output(self):
        self.add_answers()
        self.data["edited_model"] = {**self.data["base_model"], "decode_j_per_token": 0.11}
        self.write()
        process = self.run_cli("compare", "--bootstrap-samples", "100", "--seed", "17")
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report["base"]["n_correct"], 3)
        self.assertEqual(report["inference"]["seed"], 17)
        self.assertGreater(report["per_answer"]["rate_j"]["estimate"], 0)
        again = self.run_cli("compare", "--bootstrap-samples", "100", "--seed", "17")
        self.assertEqual(process.stdout, again.stdout)

    def test_sparse_correctness_is_valid_json_without_nan_or_infinity(self):
        self.add_answers()
        for row in self.data["base"]:
            row["correct"] = False
        self.write()
        process = self.run_cli("compare", "--bootstrap-samples", "100")
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout, parse_constant=lambda x: self.fail(x))
        self.assertIsNone(report["per_correct"]["delta_j"]["estimate"])

    def test_unpaired_flag_accepts_independent_rosters(self):
        self.add_answers()
        for row in self.data["edited"]:
            row["problem_id"] = "other-" + row["problem_id"]
        self.write()
        paired = self.run_cli("compare", "--bootstrap-samples", "100")
        self.assertEqual(paired.returncode, 2)
        unpaired = self.run_cli("compare", "--bootstrap-samples", "100", "--unpaired")
        self.assertEqual(unpaired.returncode, 0, unpaired.stderr)
        self.assertFalse(json.loads(unpaired.stdout)["inference"]["paired"])

    def test_malformed_inputs_refuse_cleanly(self):
        self.add_answers()
        invalid = [
            {"base_model": {"prefill_j_per_token": 0, "decode_j_per_token": 0.1}},
            {**self.data, "typo": 1},
            {**self.data, "base": [{**self.data["base"][0], "correct": "true"}]},
            {**self.data, "base": [{**self.data["base"][0], "decode_tokens": -1}]},
            {**self.data, "base_model": {**self.data["base_model"], "idle_w": 2}},
            {**self.data, "base_model": {**self.data["base_model"], "decode_j_per_token": float("nan")}},
        ]
        for data in invalid:
            with self.subTest(data=data):
                self.input.write_text(json.dumps(data), encoding="utf-8")
                process = self.run_cli("compare", "--bootstrap-samples", "100")
                self.assertEqual(process.returncode, 2)
                self.assertIn("error:", process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_duplicate_json_fields_are_rejected(self):
        self.input.write_text('{"base_model": {}, "base_model": {}}', encoding="utf-8")
        process = self.run_cli("scenario")
        self.assertEqual(process.returncode, 2)
        self.assertIn("duplicate JSON key", process.stderr)

    def test_duration_is_required_when_scenario_idle_power_is_nonzero(self):
        self.data["base_model"]["idle_w"] = 2
        self.write()
        failed = self.run_cli("scenario")
        self.assertEqual(failed.returncode, 2)
        process = self.run_cli("scenario", "--base-duration-s", "200", "--edited-duration-s", "100")
        self.assertEqual(process.returncode, 0, process.stderr)


if __name__ == "__main__":
    unittest.main()
