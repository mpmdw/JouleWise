"""Regression tests for the test-side sampler launch fence.

No test here can start the real ``sudo`` or ``/usr/bin/powermetrics``: every
refused launch targets a stand-in script in a temporary directory whose base
name is ``sudo`` or ``powermetrics`` and which would write a sentinel file if it
ever ran, and the ``PATH`` checks only resolve names, never execute them.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.sampler_launch_fence import (
    FENCE,
    FencedSuite,
    SamplerLaunchRefused,
    fenced_load_tests,
    fenced_program,
)


TESTS_DIR = Path(__file__).resolve().parent
FENCED_MODULES = (
    "test_whole_window.py",
    "test_run_campaign.py",
    "test_window_duration_margins.py",
)


class FencedProgramTests(unittest.TestCase):
    def test_fenced_names_match_by_base_name_in_any_token(self) -> None:
        cases = {
            ("sudo", "-n", "/usr/bin/powermetrics", "-n", "2"): "sudo",
            ("/usr/bin/powermetrics", "-i", "500"): "/usr/bin/powermetrics",
            ("/bin/sh", "-c", "sudo -n /usr/bin/powermetrics -n 1"): "sudo",
            "sudo -n true": "sudo",
        }
        for argv, expected in cases.items():
            with self.subTest(argv=argv):
                self.assertEqual(fenced_program(argv), expected)
        self.assertEqual(fenced_program(["x"], executable="/usr/bin/sudo"), "/usr/bin/sudo")

    def test_fixture_samplers_and_mentions_are_not_fenced(self) -> None:
        for argv in (
            [sys.executable, "tests/fixtures/fake_powermetrics_process.py", "-n", "1"],
            ["/usr/bin/pgrep", "-lf", "powermetrics.*night-probe-"],
            ["python3", "scripts/replay_powermetrics_frames.py"],
            ["git", "status"],
        ):
            with self.subTest(argv=argv):
                self.assertIsNone(fenced_program(argv))


class SamplerLaunchFenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertFalse(FENCE.installed, "fence must not leak into this module")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.sentinel = self.root / "stand-in-ran"
        self.stand_ins = {}
        for name in ("sudo", "powermetrics"):
            path = self.root / "bin" / name
            path.parent.mkdir(exist_ok=True)
            path.write_text(f"#!/bin/sh\ntouch '{self.sentinel}'\n", encoding="utf-8")
            path.chmod(0o755)
            self.stand_ins[name] = str(path)

    def _hold(self) -> None:
        FENCE.acquire()
        self.addCleanup(self._release_expecting_findings)
        self._expect_findings = False

    def _release_expecting_findings(self) -> None:
        if not FENCE.installed:
            return
        if self._expect_findings:
            with self.assertRaises(AssertionError):
                FENCE.release()
        else:
            FENCE.release()

    def test_every_launch_api_is_refused_before_a_process_exists(self) -> None:
        sudo, powermetrics = self.stand_ins["sudo"], self.stand_ins["powermetrics"]
        attempts = {
            "Popen": lambda: subprocess.Popen([sudo, "-n", powermetrics, "-n", "2"]),
            "run": lambda: subprocess.run([powermetrics, "-n", "1"], check=False),
            "shell": lambda: subprocess.run(f"{sudo} -n true", shell=True, check=False),
            "executable": lambda: subprocess.run(["x"], executable=sudo, check=False),
            "system": lambda: os.system(f"{powermetrics} -n 1"),
            "posix_spawn": lambda: os.posix_spawn(sudo, [sudo, "-n"], dict(os.environ)),
            "spawnv": lambda: os.spawnv(os.P_WAIT, powermetrics, [powermetrics]),
        }
        self._hold()
        self._expect_findings = True
        for label, attempt in attempts.items():
            with self.subTest(api=label):
                with self.assertRaises(SamplerLaunchRefused):
                    attempt()
        self.assertFalse(self.sentinel.exists(), "a stand-in process was started")
        with self.assertRaises(AssertionError) as caught:
            FENCE.release()
        report = str(caught.exception)
        self.assertIn(self.id(), report)
        self.assertEqual(report.count(self.id()), len(attempts))
        self.assertFalse(FENCE.installed)

    def test_unrelated_launches_still_run_under_the_fence(self) -> None:
        self._hold()
        completed = subprocess.run(
            [sys.executable, "-c", "print('fixture')"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(completed.stdout.strip(), "fixture")

    def test_children_resolve_fenced_names_to_logging_stand_ins(self) -> None:
        self._hold()
        resolved = subprocess.run(
            # The names are assembled by the shell so the in-process wrapper
            # sees no fenced token and the child really resolves them.
            ["/bin/sh", "-c", "a=su; b=power; command -v ${a}do; command -v ${b}metrics"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        self.assertEqual(
            resolved,
            [str(FENCE.shim_dir / "sudo"), str(FENCE.shim_dir / "powermetrics")],
        )
        # Run the resolved stand-in by its own path (never the name), as a
        # child that does not carry the in-process wrapper would reach it.
        script = self.root / "child.sh"
        script.write_text(f"exec '{resolved[0]}' -n /usr/bin/powermetrics -n 2\n")
        child = subprocess.run(
            ["/bin/sh", str(script)], capture_output=True, text=True, check=False
        )
        self.assertEqual(child.returncode, 1)
        self.assertIn("stand-in sudo refused", child.stderr)
        self._expect_findings = True
        with self.assertRaises(AssertionError) as caught:
            FENCE.release()
        self.assertIn(f"{self.id()}: child process ran stand-in sudo", str(caught.exception))

    def test_release_restores_every_patched_surface(self) -> None:
        before = (
            subprocess.Popen.__init__,
            os.system,
            os.posix_spawn,
            os.execv,
            unittest.TestCase.run,
            os.environ.get("PATH"),
        )
        FENCE.acquire()
        FENCE.acquire()
        shim_dir = FENCE.shim_dir
        FENCE.release()
        self.assertTrue(FENCE.installed)
        FENCE.release()
        after = (
            subprocess.Popen.__init__,
            os.system,
            os.posix_spawn,
            os.execv,
            unittest.TestCase.run,
            os.environ.get("PATH"),
        )
        self.assertEqual(before, after)
        self.assertFalse(shim_dir.exists())

    def test_fenced_suite_reports_a_swallowed_refusal_as_an_error(self) -> None:
        sudo = self.stand_ins["sudo"]

        class Swallowing(unittest.TestCase):
            def test_swallows(inner) -> None:
                try:
                    subprocess.run([sudo, "-n", "true"], check=False)
                except SamplerLaunchRefused:
                    pass  # production code catches broadly, as the cooldown does

        suite = fenced_load_tests(
            unittest.defaultTestLoader,
            unittest.defaultTestLoader.loadTestsFromTestCase(Swallowing),
            None,
        )
        self.assertIsInstance(suite, FencedSuite)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("test_swallows", result.errors[0][1])
        self.assertFalse(self.sentinel.exists())
        self.assertFalse(FENCE.installed)

    def test_exec_family_is_wrapped_while_held(self) -> None:
        # exec* would replace this process, so it is checked by identity only.
        originals = {name: getattr(os, name) for name in ("execv", "execve", "execvp")}
        self._hold()
        for name, original in originals.items():
            with self.subTest(name=name):
                self.assertIsNot(getattr(os, name), original)


class FenceWiringTests(unittest.TestCase):
    def test_item_124_modules_install_the_fence_both_ways(self) -> None:
        for filename in FENCED_MODULES:
            with self.subTest(module=filename):
                tree = ast.parse((TESTS_DIR / filename).read_text(encoding="utf-8"))
                load_tests = [
                    node for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(getattr(t, "id", None) == "load_tests" for t in node.targets)
                ]
                self.assertEqual(len(load_tests), 1)
                self.assertEqual(getattr(load_tests[0].value, "id", None), "fenced_load_tests")
                set_up = [
                    node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "setUpModule"
                ]
                self.assertEqual(len(set_up), 1)
                first = set_up[0].body[0]
                self.assertIsInstance(first, ast.Expr)
                self.assertEqual(getattr(first.value.func, "id", None), "install_module_fence")


if __name__ == "__main__":
    unittest.main()
