import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests import host_command_guard as guard


class HostCommandGuardTests(unittest.TestCase):
    def test_refused_subprocess_forms_never_reach_exec(self):
        forms = [
            (["/usr/bin/sudo", "-n", "true"], {}), (["sudo", "true"], {}),
            (["env", "A=b", "sudo", "true"], {}),
            (["/bin/sh", "-c", "x; sudo y"], {}),
            (["zsh", "-c", "true && pmset -g || nvram x | shutdown -h now"], {}),
            ("true; sudo y", {"shell": True}),
            ("true; sudo y", {"shell": True, "executable": "/bin/bash"}),
            ("true", {"shell": True, "executable": "/usr/bin/sudo"}),
            (["innocent"], {"executable": "/usr/bin/sudo"}),
            (["sudo"] + ["synthetic"] * 8, {}),
        ]
        forms += [([name], {}) for name in guard._DENIED]
        forms += [(["launchctl", sub, "gui/501/fake"], {}) for sub in guard._LAUNCH_WRITES]
        forms += [(["networksetup", "-setairportpower", "en0", "off"], {}),
                  (["scutil", "--set", "HostName", "fake"], {})]
        with guard.expect_refusals() as records, patch("subprocess._fork_exec") as fork:
            for command, kwargs in forms:
                with self.subTest(command=command), self.assertRaises(guard.HostCommandRefused):
                    subprocess.run(command, **kwargs)
            fork.assert_not_called()
        self.assertGreaterEqual(len(records), len(forms))
        self.assertTrue(all(r["test_id"] == self.id() for r in records))
        self.assertTrue(all(len(r["argv"]) <= 6 and r["caller"] for r in records))
        self.assertTrue(any(len(r["argv"]) == 6 for r in records))

    def test_os_entry_points_never_call_original(self):
        with guard.expect_refusals() as records, patch.object(guard, "_invoke") as original:
            calls = [(os.system, ("true; sudo y",))]
            for name in ("posix_spawn", "posix_spawnp", "execv", "execve", "execvp", "execvpe"):
                if hasattr(os, name):
                    argv = ("sudo", ["sudo", "true"])
                    if name in ("posix_spawn", "posix_spawnp", "execve", "execvpe"):
                        argv += ({},)
                    calls.append((getattr(os, name), argv))
            for name in ("execl", "execlp", "execle", "execlpe"):
                argv = ("sudo", "sudo", "true") + (({},) if name.endswith("e") else ())
                calls.append((getattr(os, name), argv))
            for call, args in calls:
                with self.subTest(call=call.__name__), self.assertRaises(guard.HostCommandRefused):
                    call(*args)
            original.assert_not_called()
        self.assertEqual(len(records), len(calls))

    def test_classifier_policy_and_symlink(self):
        denied = [[name] for name in ("sudo", "systemsetup", "pmset", "caffeinate", "shutdown", "nvram")]
        denied += [["launchctl", sub] for sub in guard._LAUNCH_WRITES]
        denied += [["networksetup", "-setairportpower", "en0", "off"], ["scutil", "--set", "HostName", "x"]]
        allowed = [["git", "--version"], ["networksetup", "-listallhardwareports"]]
        allowed += [["launchctl", sub, "gui/501"] for sub in ("print", "list", "blame")]
        allowed += [[name, "write"] for name in ("defaults", "kill", "killall", "pgrep", "ps")]
        for command in denied:
            self.assertTrue(guard.classify(command), command)
        for command in allowed:
            self.assertEqual(guard.classify(command), [], command)
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "innocent"
            link.symlink_to("/usr/bin/sudo")
            self.assertEqual(guard.classify([str(link)])[0][0], "sudo")
            with guard.expect_refusals() as records, patch("subprocess._fork_exec") as fork:
                with self.assertRaises(guard.HostCommandRefused):
                    subprocess.run([str(link), "true"])
                fork.assert_not_called()
            self.assertEqual(records[0]["command"], "sudo")
        self.assertEqual(subprocess.run(["git", "--version"], capture_output=True).returncode, 0)

    def test_child_interpreter_reports_even_swallowed_refusal(self):
        class Leaky(unittest.TestCase):
            def runTest(self):
                child = subprocess.run([sys.executable, "-B", "-c", "import subprocess\nfrom unittest.mock import patch\nwith patch('subprocess._fork_exec') as fork:\n try: subprocess.run(['pmset', '-g'])\n except Exception: pass\n fork.assert_not_called()"], capture_output=True, text=True)
                self.assertEqual(child.returncode, 0, child.stderr)
        with guard.expect_refusals() as records:
            result = unittest.TestResult()
            Leaky().run(result)
            self.assertEqual(len(result.failures), 1)
            self.assertIn("pmset", result.failures[0][1])
        self.assertEqual([r["command"] for r in records], ["pmset"])
        self.assertNotEqual(records[0]["pid"], os.getpid())

    def test_swallowed_in_process_refusal_fails_test(self):
        class Leaky(unittest.TestCase):
            def runTest(self):
                try:
                    subprocess.run(["sudo", "true"])
                except Exception:
                    pass
        with guard.expect_refusals() as records, patch("subprocess._fork_exec") as fork:
            result = unittest.TestResult()
            Leaky().run(result)
            self.assertEqual(len(result.failures), 1)
            self.assertIn("sudo", result.failures[0][1])
            fork.assert_not_called()
        self.assertEqual(len(records), 1)

    def test_expect_refusals_rejected_outside_own_module(self):
        namespace = {"__name__": "tests.other", "guard": guard}
        exec("def misuse():\n    with guard.expect_refusals(): pass", namespace)
        with self.assertRaisesRegex(RuntimeError, "reserved"):
            namespace["misuse"]()

    def test_install_idempotent_and_uninstall_restores(self):
        before = subprocess.Popen.__init__
        guard.install()
        self.assertIs(subprocess.Popen.__init__, before)
        guard.uninstall()
        try:
            self.assertIsNot(subprocess.Popen.__init__, before)
        finally:
            guard.install()

    def test_sitecustomize_chains_existing_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "sitecustomize.py").write_text("import os; os.environ['CHAIN_WITNESS'] = 'yes'\n")
            env = dict(os.environ)
            env["PYTHONPATH"] += os.pathsep + tmp
            child = subprocess.run([sys.executable, "-B", "-c", "import os; print(os.environ.get('CHAIN_WITNESS'))"], env=env, capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertEqual(child.stdout.strip(), "yes")

    def test_shard_and_quick_launch_import_guard_before_body(self):
        root = Path(__file__).resolve().parents[1]
        source = """
import sys, types, unittest
sys.path.insert(0, sys.argv[1])
assert 'tests' not in sys.modules
from scripts import shard_tests, quick_suite
assert 'run_shard' in quick_suite.module_job('tests.synthetic')[1][2]
module = types.ModuleType('synthetic')
class Witness(unittest.TestCase):
    def runTest(self):
        self.assertIn('tests', sys.modules)
        from tests import host_command_guard
        self.assertTrue(host_command_guard._originals)
module.Witness = Witness
sys.modules['synthetic'] = module
sys.exit(shard_tests.run_shard(['tests.synthetic'], 1, 1))
"""
        child = subprocess.run([sys.executable, "-B", "-S", "-c", source, str(root)], capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stdout + child.stderr)

    def test_guard_environment_is_test_only(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(["git", "grep", "-l", "-e", "JW_TEST_HOST_GUARD_REPORT", "-e", "PYTHONPATH", "--", "scripts/", "joulewise/"], cwd=root, capture_output=True, text=True)
        # PYTHONPATH already has legitimate production uses; prohibit guard-specific
        # references and the guard site directory in either production tree.
        for name in result.stdout.splitlines():
            source = (root / name).read_text()
            self.assertNotIn("JW_TEST_HOST_GUARD_REPORT", source)
            self.assertNotIn("_host_guard_site", source)


if __name__ == "__main__":
    unittest.main()
