"""Unpatched production subprocess coverage of live-registry STOP paths."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_results_fills.py"
FIXTURES = ROOT / "tests" / "fixtures" / "results_prose_render"


class LiveResultsFillTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True, check=False)

    def test_stale_row_from_real_loader_exits_two_without_traceback(self):
        # Both JSON loading and the registry lookup run in the actual script.
        result = self.run_cli(FIXTURES / "synthetic_absent_artifact_manifest.json")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("unknown Results fill registry row", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_json_and_missing_file_refuse_in_production(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.json"
            bad.write_text('{"schema_version":', encoding="utf-8")
            for path in (bad, Path(directory) / "absent.json"):
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_and_nonfinite_json_are_refused_by_real_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for raw in ('{"a": 1, "a": 2}', '{"a": NaN}'):
                path.write_text(raw, encoding="utf-8")
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_adapter_manifest_reaches_real_consumer_and_refuses_stale_vocabulary(self):
        from joulewise.results_fill_adapter import adapt_claim_verdicts
        from joulewise.analysis_engine.artifact import render_claim_verdicts
        from tests.test_results_fill_adapter import produced_verdict
        campaigns = json.loads((FIXTURES / "synthetic_absent_artifact_manifest.json").read_text())["campaigns"]
        for campaign in campaigns.values():
            for key in ("verdict", "floor_artifact", "extraction"):
                if isinstance(campaign.get(key), str):
                    campaign[key] = str(FIXTURES / campaign[key])
        output = adapt_claim_verdicts(render_claim_verdicts(produced_verdict()), campaigns=campaigns)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(output), encoding="utf-8")
            result = self.run_cli(path)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("unknown Results fill registry row", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
