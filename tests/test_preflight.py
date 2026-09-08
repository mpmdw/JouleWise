"""Routing regressions execute the preflight prefix, never hardware checks."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = REPO_ROOT / "docs/process_traces/2026-08-28-live-smoke/preflight.sh"
ROUTING_END = 'if [ -n "${SMOKE_CHECKOUT:-}" ] && [ -e "$SMOKE_CHECKOUT" ]; then'
HEAD = "a" * 40


@unittest.skipUnless(Path("/usr/bin/jq").is_file(), "system jq required by preflight")
class PreflightRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "measurement with spaces"
        (self.root / ".git").mkdir(parents=True)
        self.python = self.root / ".venv/bin/python"
        self.python.parent.mkdir(parents=True)
        self.python.write_text("#!/bin/sh\necho UNEXPECTED_INTERPRETER_EXECUTION >&2\nexit 99\n")
        self.python.chmod(0o755)
        self.fake_bin = Path(self.temporary.name) / "bin"
        self.fake_bin.mkdir()
        git = self.fake_bin / "git"
        git.write_text(f'#!/bin/sh\n[ "$1" = -C ] && [ "$2" = "$EXPECTED_ROOT" ] || exit 99\n'
                       'case "$3" in\nstatus) exit 0 ;;\nbranch) printf "%s\\n" "$CHECKED_BRANCH" ;;\n'
                       f'*) printf "%s\\n" "{HEAD}" ;;\nesac\n')
        git.chmod(0o755)
        self.checked_branch = ""
        self.plan = {
            "schema": "joulewise.night_plan.v2", "schema_version": 2,
            "measurement_root": str(self.root), "measurement_head": HEAD,
        }

    def run_routing(self, *, checkout_checks: bool = False) -> subprocess.CompletedProcess[str]:
        source = PREFLIGHT.read_text()
        self.assertEqual(source.count(ROUTING_END), 1)
        routing = (source.split("  lock_path=")[0] + "fi\n"
                   if checkout_checks else source.split(ROUTING_END)[0])
        routing += '\n[ "$failures" -eq 0 ] || exit 1\nprintf "%s\\n" "$SMOKE_CHECKOUT" "$PY"\n'
        plan_path = Path(self.temporary.name) / "night plan.json"
        plan_path.write_text(json.dumps(self.plan))
        result = subprocess.run(
            ["/bin/bash", "-c", routing, "preflight.sh", str(plan_path)],
            env={**os.environ, "PATH": f"{self.fake_bin}:/usr/bin:/bin",
                 "CHECKED_BRANCH": self.checked_branch, "EXPECTED_ROOT": str(self.root), "MEASUREMENT_ROOT": "/inherited/wrong",
                 "MEASUREMENT_HEAD": "b" * 40, "PY": "/inherited/python",
                 "PYTHONPATH": "/inherited/pythonpath"},
            text=True, capture_output=True,
        )
        self.assertNotIn("UNEXPECTED_INTERPRETER_EXECUTION", result.stderr)
        return result

    def test_program_refuses_missing_argument_and_mismatched_head(self) -> None:
        env = {**os.environ, "PATH": f"{self.fake_bin}:/usr/bin:/bin",
               "EXPECTED_ROOT": str(self.root)}
        result = subprocess.run([str(PREFLIGHT)], env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)
        self.assertIn("/absolute/path/to/night_plan.json", result.stderr)
        self.plan["measurement_head"] = "b" * 40
        plan_path = Path(self.temporary.name) / "night plan.json"
        plan_path.write_text(json.dumps(self.plan))
        result = subprocess.run([str(PREFLIGHT), str(plan_path)], env=env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL checkout HEAD does not equal measurement_head", result.stdout)
        self.assertNotIn("UNEXPECTED_INTERPRETER_EXECUTION", result.stderr)

    def test_plan_routes_root_head_and_interpreter_over_inherited_values(self) -> None:
        result = self.run_routing()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"{self.root}\n{self.python}\n", result.stdout)
        self.assertIn("PASS checkout HEAD equals measurement_head", result.stdout)

    def test_counterfactual_preflight_passes_with_mismatched_head(self) -> None:
        self.plan["measurement_head"] = "b" * 40
        result = self.run_routing()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL checkout HEAD does not equal measurement_head", result.stdout)
        self.assertNotIn("PASS checkout HEAD", result.stdout)

    def test_counterfactual_missing_measurement_root_not_refused(self) -> None:
        del self.plan["measurement_root"]
        result = self.run_routing()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL measurement_root must be a non-empty absolute path", result.stdout)

    def test_relative_or_invalid_root_refused(self) -> None:
        for value in ("relative/root", "", None, 3, True, "/root\n", "/root\x00"):
            with self.subTest(value=value):
                self.plan["measurement_root"] = value
                result = self.run_routing()
                self.assertEqual(result.returncode, 1)
                self.assertIn("FAIL measurement_root must be a non-empty absolute path", result.stdout)

    def test_missing_or_invalid_head_refused(self) -> None:
        for value in (None, "", "abc", "A" * 40, 3, HEAD + "\n"):
            with self.subTest(value=value):
                self.plan["measurement_head"] = value
                result = self.run_routing()
                self.assertEqual(result.returncode, 1)
                self.assertIn("FAIL measurement_head must be a full 40-character lowercase SHA-1", result.stdout)
        del self.plan["measurement_head"]
        self.assertEqual(self.run_routing().returncode, 1)

    def test_missing_interpreter_refused(self) -> None:
        self.python.unlink()
        result = self.run_routing()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL measurement venv Python is missing or not executable", result.stdout)

    def test_detached_clone_passes_but_checked_out_branch_refuses(self) -> None:
        result = self.run_routing(checkout_checks=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS measurement checkout is detached at measurement_head", result.stdout)
        self.checked_branch = "main"
        result = self.run_routing(checkout_checks=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL measurement checkout must be detached at measurement_head", result.stdout)

    def test_retired_plan_refused(self) -> None:
        self.plan["schema"] = "joulewise.night_plan.v1"
        result = self.run_routing()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL night plan must use joulewise.night_plan.v2 with schema_version 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
