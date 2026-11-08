"""Offline integration tests; every checkout, command and receipt is synthetic."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import readiness_next2 as gate


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="readiness-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.write("launch.py", """import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({'status':'armed_synthetic', 'gate':True}))
""")
        self.write("kit.py", "print('synthetic kit checked')\n")
        self.write("kit.json", json.dumps({"R0": {"effort": "medium"}}))
        self.write("agreement.md", "AGREED synthetic route\n")
        self.write("scripts/align_v4_prequal.py", """import argparse, json, pathlib
p = argparse.ArgumentParser()
p.add_argument('--output'); p.add_argument('--only'); p.add_argument('--stage'); p.add_argument('--offline', action='store_true')
a=p.parse_args(); out=pathlib.Path(a.output); out.mkdir()
(out/'prequal.json').write_text(json.dumps({'checks':[{'check':c,'status':'pass'} for c in a.only.split(',')]}))
raise SystemExit(3) # A deliberately selected PREQUAL subset is incomplete overall.
""")
        self.write("checks.py", """import os, unittest
class Default(unittest.TestCase):
    def test_default(self): self.assertEqual(2+2,4)
@unittest.skipUnless(os.getenv('JW_SYNTHETIC_FULL') == '1', 'set JW_SYNTHETIC_FULL=1')
class OptIn(unittest.TestCase):
    def test_full(self): self.assertTrue(True)
""")
        self.git("add", ".")
        self.git("-c", "user.name=Readiness", "-c", "user.email=readiness@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "synthetic readiness fixture")
        self.head = self.git("rev-parse", "HEAD").strip()
        self.git("update-ref", "refs/remotes/origin/lane/synthetic", self.head)
        self.step = {
            "id": "R1", "branch": "lane/synthetic", "commit": self.head,
            "minimum_duration_hours": 18,
            "arm": {"live_command": ["python", "launch.py", "LIVE_ONLY_NEVER_RUN"],
                    "exercises": ["launch.py", "synthetic gate"],
                    "route_files": ["launch.py"],
                    "synthetic": {"argv": ["{python}", "-B", "launch.py", "{scratch}/arm.json"],
                                  "assert_json": {"path": "arm.json", "equals": {"status": "armed_synthetic", "gate": True}}}},
            "kit": {"path": "kit.json", "required_fields": ["R0.effort"],
                    "check": {"argv": ["{python}", "-B", "kit.py"]}},
            "evidence": [{"name": "agreement", "path": "agreement.md", "contains": ["AGREED"]}],
            "prequal": {"stage": "r1", "checks": ["kit", "w1-plan"]},
            "tests": [{"module": "checks.Default"}, {"module": "checks.OptIn", "env": {"JW_SYNTHETIC_FULL": "1"}}],
        }
        self.manifest = {"schema": gate.SCHEMA, "mbp_available_at": None,
                         "steps": [self.step, {**deepcopy(self.step), "id": "W1"}]}

    def git(self, *args):
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        return subprocess.run(["git", *args], cwd=self.repo, env=env, check=True,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, path, text):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    def evaluate(self):
        return gate.evaluate(self.repo, self.manifest, now=datetime(2026, 11, 8, tzinfo=timezone.utc))

    def row(self, report, name):
        return next(r for r in report["steps"][0]["prerequisites"] if r["prerequisite"] == name)

    def test_all_present_green_and_exact_tree_cleaned_up(self):
        # The third step must never be fetched or run.
        self.manifest["steps"].append({"id": "D1", "branch": "missing"})
        report = self.evaluate()
        self.assertEqual(report["status"], "GREEN", report)
        self.assertEqual(len(report["steps"]), 2)
        self.assertEqual(report["steps"][1]["earliest_mbp_hour"], 18)
        self.assertEqual(report["steps"][0]["commit"], self.head)
        self.assertEqual(self.git("worktree", "list", "--porcelain").count("worktree "), 1)
        self.assertFalse((self.repo / "LIVE_ONLY_NEVER_RUN").exists())
        self.assertFalse((self.repo / "arm.json").exists())

    def test_missing_arm_route_red_with_exact_reason(self):
        self.step["arm"]["synthetic"] = None
        report = self.evaluate()
        self.assertEqual(report["status"], "RED")
        self.assertIn("no arm route", self.row(report, "arm/launch")["reason"])
        self.assertTrue(report["critical_path_alarm"])
        self.assertEqual(self.row(report, "kit --check")["status"], "GREEN")

    def test_required_opt_in_skip_is_red(self):
        self.step["tests"][1]["env"] = {"JW_SYNTHETIC_FULL": "0"}
        report = self.evaluate()
        row = self.row(report, "tests:checks.OptIn")
        self.assertEqual(row["status"], "RED")
        self.assertIn("required test skipped", row["reason"])
        self.assertIn("set JW_SYNTHETIC_FULL=1", row["reason"])

    def test_missing_route_file_red_even_if_unrelated_synthetic_script_passes(self):
        self.step["arm"]["route_files"] = ["missing-launcher.py"]
        row = self.row(self.evaluate(), "arm/launch")
        self.assertEqual(row["status"], "RED")
        self.assertIn("no arm route: missing-launcher.py", row["reason"])

    def test_nonzero_launch_preserves_refusal_reason(self):
        self.step["arm"]["synthetic"]["argv"] = ["{python}", "-c", "import sys; sys.exit('refused: registration missing')"]
        row = self.row(self.evaluate(), "arm/launch")
        self.assertEqual(row["status"], "RED")
        self.assertIn("refused: registration missing", row["reason"])

    def test_zero_exit_refused_record_is_red(self):
        self.step["arm"]["synthetic"]["assert_json"]["equals"]["status"] = "GO"
        row = self.row(self.evaluate(), "arm/launch")
        self.assertEqual(row["status"], "RED")
        self.assertIn("expected 'GO'", row["reason"])

    def test_missing_branch_gives_red_and_unexercised_unknown(self):
        self.step["branch"] = "lane/not-pushed"
        report = self.evaluate()
        self.assertEqual(report["status"], "RED")
        self.assertEqual(self.row(report, "kit --check")["status"], "UNKNOWN")
        self.assertIn("no arm route", self.row(report, "arm/launch")["reason"])

    def test_pinned_commit_not_branch_tip_is_exercised(self):
        self.write("later.txt", "unreviewed branch advancement")
        self.git("add", ".")
        self.git("-c", "user.name=Readiness", "-c", "user.email=readiness@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "later branch tip")
        self.git("update-ref", "refs/remotes/origin/lane/synthetic", "HEAD")
        self.assertEqual(self.evaluate()["steps"][0]["commit"], self.head)

    def test_pending_kit_missing_ruling_and_missing_prequal_check_red(self):
        self.step["kit"]["required_fields"] = ["R1.T_dead"]
        self.step["evidence"][0]["path"] = "missing.md"
        report = self.evaluate()
        self.assertEqual(self.row(report, "kit:R1.T_dead")["status"], "RED")
        self.assertEqual(self.row(report, "evidence:agreement")["status"], "RED")
        self.assertTrue(gate.pending({"x": "PENDING_R1"}))
        self.assertFalse(gate.pending({"fan_keys": [], "mode": 0}))

    def test_outside_and_restricted_receipt_paths_refused(self):
        for path in ("/never/open", "../outside", "restricted/data"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                gate.confined(self.repo, path)
        (self.repo / "link").symlink_to("/never/open")
        with self.assertRaisesRegex(ValueError, "symlink"):
            gate.confined(self.repo, "link/data")

    def test_required_prequal_not_run_is_red(self):
        real_run = gate.run

        def incomplete(argv, cwd, env=None, timeout=600):
            result = real_run(argv, cwd, env, timeout)
            if any(str(arg).endswith("align_v4_prequal.py") for arg in argv):
                out = Path(argv[argv.index("--output") + 1]) / "prequal.json"
                out.write_text(json.dumps({"checks": [{"check": "kit", "status": "not_run", "reason": "fixture missing"}]}))
            return result
        with patch.object(gate, "run", incomplete):
            report = self.evaluate()
        self.assertEqual(self.row(report, "PREQUAL:kit")["status"], "RED")
        self.assertIn("fixture missing", self.row(report, "PREQUAL:kit")["reason"])
        self.assertEqual(self.row(report, "PREQUAL:w1-plan")["status"], "RED")

    def test_defaults_do_not_erase_explicit_missing_route(self):
        defaults = deepcopy(self.step)
        self.manifest["defaults"] = defaults
        self.manifest["steps"] = [{"id": "R1", "arm": {"synthetic": None}}, {"id": "W1"}]
        report = self.evaluate()
        self.assertEqual(report["steps"][0]["status"], "RED")
        self.assertEqual(report["steps"][1]["status"], "GREEN")

    def test_passing_prequal_row_stays_green_when_sibling_fails(self):
        real_run = gate.run

        def failed_sibling(argv, cwd, env=None, timeout=600):
            result = real_run(argv, cwd, env, timeout)
            if any(str(arg).endswith("align_v4_prequal.py") for arg in argv):
                out = Path(argv[argv.index("--output") + 1]) / "prequal.json"
                out.write_text(json.dumps({"checks": [{"check": "kit", "status": "pass"},
                                                      {"check": "w1-plan", "status": "fail"}]}))
                result["returncode"] = 1
            return result
        with patch.object(gate, "run", failed_sibling):
            report = self.evaluate()
        self.assertEqual(self.row(report, "PREQUAL:kit")["status"], "GREEN")
        self.assertEqual(self.row(report, "PREQUAL:w1-plan")["status"], "RED")

    def test_budget_exhaustion_does_not_hide_required_checks(self):
        report = gate.evaluate(self.repo, self.manifest, budget_s=0.001)
        row = self.row(report, "tests:checks.OptIn")
        self.assertEqual(row["status"], "RED")
        self.assertIn("budget exhausted", row["reason"])

    def test_fetches_named_branch_from_synthetic_local_remote(self):
        # Local repository transport only: no network or data outside TMPDIR.
        self.git("branch", "lane/synthetic", self.head)
        self.git("remote", "add", "origin", str(self.repo))
        self.git("update-ref", "-d", "refs/remotes/origin/lane/synthetic")
        report = gate.evaluate(self.repo, self.manifest, fetch=True)
        self.assertEqual(report["status"], "GREEN", report)
        self.assertEqual(report["refs"], "fetched from origin")

    def test_critical_alarm_uses_lower_bounds_and_absolute_availability(self):
        self.step["arm"] = {}
        self.manifest["mbp_available_at"] = "2026-11-09T01:00:00+00:00"
        report = self.evaluate()
        self.assertFalse(report["critical_path_alarm"])
        self.assertEqual(self.row(report, "arm/launch")["earliest_mbp_hour"], 25)
        self.manifest["mbp_available_at"] = "2026-11-07T00:00:00+00:00"
        report = self.evaluate()
        self.assertTrue(report["critical_path_alarm"])
        self.assertEqual(self.row(report, "arm/launch")["earliest_mbp_at"], "2026-11-08T00:00:00+00:00")

    def test_cli_writes_both_status_files_and_fails_visibly(self):
        self.step["arm"] = {}
        config = self.root / "next.json"
        config.write_text(json.dumps(self.manifest))
        output = self.root / "status.json"
        with patch("builtins.print"):
            rc = gate.main(["--repo", str(self.repo), "--config", str(config), "--output", str(output)])
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(output.read_text())["status"], "RED")
        self.assertIn("no arm route", output.with_suffix(".md").read_text())


if __name__ == "__main__":
    unittest.main()
