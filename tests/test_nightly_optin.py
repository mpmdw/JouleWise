"""Exercise the nightly's actual shell steps with tiny synthetic unittest modules."""
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).absolute().parents[1]
WORKFLOW = ROOT / ".github/workflows/nightly-optin.yml"


def step_script(name, values=None):
    step = WORKFLOW.read_text().split(f"      - name: {name}\n", 1)[1]
    step = step.split("      - name:", 1)[0]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1])
    for key, value in (values or {}).items():
        script = script.replace("${{ " + key + " }}", value)
    return script


@unittest.skipUnless(shutil.which("bash"), "workflow execution requires bash")
class NightlyOptinTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="nightly-optin-test-")
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        # Isolate imports to stdlib + the temporary probe module. No dependencies,
        # real fixture extraction, model weights, or repository test discovery.
        python = bin_dir / "python"
        python.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -S \"$@\"\n")
        python.chmod(0o755)
        self.env = dict(os.environ,
                        PATH=str(bin_dir) + os.pathsep + os.environ.get("PATH", ""),
                        PYTHONPATH=str(self.root), PYTHONNOUSERSITE="1",
                        PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1", OPTIN_NAME="NIGHTLY_PROBE",
                        MODULE="probe", MAX_SKIPS="0", LOG=str(self.root / "probe.log"))

    def run_probe(self, body, expected):
        (self.root / "probe.py").write_text(textwrap.dedent(body))
        result = subprocess.run(
            [shutil.which("bash"), "-e", "-c", step_script("Run the opt-in suite")],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=15,
        )
        if expected is None:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        log = (self.root / "probe.log").read_text()
        self.assertTrue(log, "tee must retain output even when the command fails")
        return log

    def test_pass_enables_optin_and_runs_one_selected_module(self):
        # A neighboring failing module would fail discovery; only probe may run.
        (self.root / "test_unselected.py").write_text("raise RuntimeError('not selected')\n")
        log = self.run_probe('''
            import os, unittest
            class Probe(unittest.TestCase):
                def test_enabled(self):
                    self.assertEqual(os.environ['NIGHTLY_PROBE'], '1')
        ''', 0)
        self.assertIn("Ran 1 test", log)

    def test_assertion_failure_is_red(self):
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                def test_failure(self): self.fail('synthetic failure')
        ''', 1)

    def test_import_error_is_red(self):
        self.run_probe("raise ImportError('synthetic import failure')\n", 1)

    def test_arbitrary_nonzero_exit_is_preserved(self):
        self.run_probe("print('synthetic exit'); raise SystemExit(7)\n", 7)

    def test_zero_tests_are_red(self):
        # Python 3.13+ itself returns 5; older interpreters need the shell guard.
        self.assertIn("Ran 0 tests", self.run_probe("import unittest\n", None))

    def test_zero_summary_with_exit_zero_is_red(self):
        self.run_probe("print('Ran 0 tests in 0.000s'); raise SystemExit(0)\n", 1)

    def test_missing_summary_is_red(self):
        self.run_probe("print('no tests'); raise SystemExit(0)\n", 1)

    def test_method_skip_is_red(self):
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                @unittest.skip('synthetic skip')
                def test_skipped(self): pass
        ''', 1)

    def test_class_setup_skip_is_red(self):
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                @classmethod
                def setUpClass(cls): raise unittest.SkipTest('synthetic setup skip')
                def test_skipped(self): pass
        ''', 1)

    def test_subtest_skip_is_red(self):
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                def test_partial(self):
                    with self.subTest(value=1): self.skipTest('synthetic subtest skip')
                    with self.subTest(value=2): self.assertTrue(True)
        ''', 1)

    def test_expected_failure_is_accepted(self):
        # WP22 explicitly carries an accepted collector-death divergence.
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                @unittest.expectedFailure
                def test_known_divergence(self): self.fail('accepted divergence')
        ''', 0)

    def test_unexpected_success_is_red(self):
        self.run_probe('''
            import unittest
            class Probe(unittest.TestCase):
                @unittest.expectedFailure
                def test_fixed_divergence(self): pass
        ''', 1)

    def test_dispatch_ref_is_logged_literally(self):
        marker = self.root / "injected"
        ref = 'review/$(touch${IFS}' + str(marker) + ')'
        env = dict(self.env, REQUESTED_REF=ref)
        values = {"matrix.ref": ref, "matrix.name": "probe",
                  "matrix.optin": "NIGHTLY_PROBE", "matrix.module": "probe"}
        result = subprocess.run(
            [shutil.which("bash"), "-e", "-c",
             step_script("Record the tree under test", values)],
            cwd=self.root, env=env, text=True, capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), "dispatch input was executed as shell source")
        header = (self.root / "nightly-logs/probe.header.txt").read_text()
        self.assertIn("requested_ref=" + ref, header)
        self.assertIn("REQUESTED_REF: ${{ matrix.ref }}", WORKFLOW.read_text())

    def test_workflow_has_only_nightly_and_manual_triggers(self):
        source = WORKFLOW.read_text()
        triggers = source.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
        self.assertEqual(re.findall(r"^  ([a-z_]+):", triggers, re.MULTILINE),
                         ["schedule", "workflow_dispatch"])
        self.assertIn("        if: always()\n        uses: actions/upload-artifact@", source)


if __name__ == "__main__":
    unittest.main()
