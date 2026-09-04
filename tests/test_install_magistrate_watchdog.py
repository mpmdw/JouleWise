"""Behavioral tests for the magistrate LaunchAgent installer."""

from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "install_magistrate_watchdog.sh"
TEMPLATE_PATH = (
    REPO_ROOT
    / "configs"
    / "launchd"
    / "com.joulewise.magistrate.plist.template"
)
CANONICAL_REPO = Path("/Users/edr/code/JouleWise")


class InstallMagistrateWatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        (self.bin_dir / "python3").symlink_to(Path(sys.executable))

        session_target = self.bin_dir / "session-target"
        session_target.write_text(
            "#!/bin/zsh\nprint '2.1.260 (Claude Code)'\n", encoding="utf-8"
        )
        session_target.chmod(0o755)
        self.session_bin = self.bin_dir / "session-bin"
        self.session_bin.symlink_to(session_target)

        self.launch_log = self.root / "launchctl.log"
        launchctl = self.bin_dir / "launchctl"
        launchctl.write_text(
            "#!/bin/zsh\n"
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            '[[ "${LAUNCHCTL_FAIL_COMMAND:-}" == "$1" ]] && exit 19\n'
            "exit 0\n",
            encoding="utf-8",
        )
        launchctl.chmod(0o755)

        self.environment = os.environ.copy()
        self.environment.update(
            {
                "HOME": str(self.home),
                "PATH": f"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin",
                "LAUNCH_LOG": str(self.launch_log),
                "MAGISTRATE_SESSION_BIN": str(self.session_bin),
                "MAGISTRATE_WATCHDOG_CUSTODY_ROOT": str(
                    self.home / "night-custody" / "magistrate"
                ),
            }
        )

        self.shadow_repo = self.root / "canonical-shadow"
        (self.shadow_repo / "scripts").mkdir(parents=True)
        shadow_template = (
            self.shadow_repo
            / "configs"
            / "launchd"
            / TEMPLATE_PATH.name
        )
        shadow_template.parent.mkdir(parents=True)
        shutil.copyfile(TEMPLATE_PATH, shadow_template)
        ps_stub = self.bin_dir / "ps-stub"
        ps_stub.write_text(
            "#!/bin/zsh\n"
            "case \"$*\" in\n"
            "  *command=*) print 'claude' ;;\n"
            "  *lstart=*) print 'Thu Sep  4 01:02:03 2026' ;;\n"
            "  *ppid=*) print '1' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        ps_stub.chmod(0o755)
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        source = source.replace(
            'canonical_repo="/Users/edr/code/JouleWise"',
            f'canonical_repo="{self.shadow_repo}"',
        )
        source = source.replace('("/bin/ps",', f'("{ps_stub}",')
        self.shadow_script = self.shadow_repo / "scripts" / SCRIPT_PATH.name
        self.shadow_script.write_text(source, encoding="utf-8")
        self.shadow_script.chmod(0o755)
        subprocess.run(
            ["/usr/bin/git", "init", "-q", str(self.shadow_repo)], check=True
        )

        self.noncanonical_repo = self.root / "noncanonical-copy"
        self.noncanonical_script = (
            self.noncanonical_repo / "scripts" / SCRIPT_PATH.name
        )
        self.noncanonical_script.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT_PATH, self.noncanonical_script)
        self.noncanonical_script.chmod(0o755)
        noncanonical_template = (
            self.noncanonical_repo
            / "configs"
            / "launchd"
            / TEMPLATE_PATH.name
        )
        noncanonical_template.parent.mkdir(parents=True)
        shutil.copyfile(TEMPLATE_PATH, noncanonical_template)
        subprocess.run(
            ["/usr/bin/git", "init", "-q", str(self.noncanonical_repo)],
            check=True,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _run(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        argv = ["/bin/zsh", str(script), *args]
        return subprocess.run(
            argv,
            env=self.environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_rendered_plist_pins_canonical_checkout(self) -> None:
        render_dir = self.root / "rendered"

        completed = self._run(SCRIPT_PATH, "--render-only", str(render_dir))

        self.assertEqual(0, completed.returncode, completed.stderr)
        plist_path = render_dir / "com.joulewise.magistrate.plist"
        payload = plist_path.read_bytes()
        plist = plistlib.loads(payload)
        self.assertEqual(str(CANONICAL_REPO), plist["WorkingDirectory"])
        self.assertEqual(
            str(CANONICAL_REPO / "scripts" / "magistrate_watchdog.py"),
            plist["ProgramArguments"][1],
        )

    def test_rendered_plist_pins_test_interpreter(self) -> None:
        render_dir = self.root / "interpreter-render"

        completed = self._run(SCRIPT_PATH, "--render-only", str(render_dir))

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = (render_dir / "com.joulewise.magistrate.plist").read_bytes()
        plist = plistlib.loads(payload)
        rendered = Path(plist["ProgramArguments"][0])
        self.assertTrue(rendered.is_absolute(), rendered)
        # CPython reports the invoked symlink on some platforms and its target on
        # others; the pin is the same executable either way.
        self.assertEqual(Path(sys.executable).resolve(), rendered.resolve())
        self.assertNotIn(b"/usr/bin/env", payload)

    def test_render_refuses_system_python_without_repository_dependencies(self) -> None:
        environment = dict(self.environment)
        environment["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"

        completed = subprocess.run(
            [
                "/bin/zsh",
                str(SCRIPT_PATH),
                "--render-only",
                str(self.root / "system-python-render"),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(3, completed.returncode, completed.stderr)
        self.assertIn("unacceptable_system_python", completed.stderr)

    def test_install_from_noncanonical_checkout_refuses_before_writing(self) -> None:
        completed = self._run(self.noncanonical_script, "--install")

        self.assertEqual(3, completed.returncode, completed.stderr)
        self.assertIn("noncanonical_checkout", completed.stderr)
        self.assertFalse(
            (self.home / "Library/LaunchAgents/com.joulewise.magistrate.plist").exists()
        )
        self.assertFalse(self.launch_log.exists())

    def test_real_install_flow_seeds_lock_renders_plist_and_calls_launchctl(self) -> None:
        completed = self._run(self.shadow_script, "--install")

        self.assertEqual(0, completed.returncode, completed.stderr)
        lock_path = self.home / "night-custody/magistrate/magistrate.lock"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertTrue(lock["first_install_adoption"])
        self.assertEqual("joulewise.magistrate_lock.v1", lock["schema"])
        plist_path = self.home / "Library/LaunchAgents/com.joulewise.magistrate.plist"
        plist = plistlib.loads(plist_path.read_bytes())
        self.assertEqual(str(self.shadow_repo.resolve()), plist["WorkingDirectory"])
        calls = self.launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(3, len(calls))
        self.assertTrue(any(" bootstrap " in f" {call} " for call in calls))
        self.assertTrue(any(" print " in f" {call} " for call in calls))

    def test_failed_lock_seed_restores_exact_preexisting_plist_and_lock(self) -> None:
        plist_path = self.home / "Library/LaunchAgents/com.joulewise.magistrate.plist"
        plist_path.parent.mkdir(parents=True)
        plist_path.write_bytes(b"pre-existing plist\x00bytes\n")
        lock_path = self.home / "night-custody/magistrate/magistrate.lock"
        lock_path.parent.mkdir(parents=True)
        lock_path.write_bytes(b"pre-existing lock\x00bytes\n")
        before = {plist_path: plist_path.read_bytes(), lock_path: lock_path.read_bytes()}

        completed = self._run(self.shadow_script, "--install")

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual(before[plist_path], plist_path.read_bytes())
        self.assertEqual(before[lock_path], lock_path.read_bytes())
        self.assertFalse(self.launch_log.exists())

    def test_failed_bootstrap_restores_exact_preexisting_plist_and_absent_lock(
        self,
    ) -> None:
        plist_path = self.home / "Library/LaunchAgents/com.joulewise.magistrate.plist"
        plist_path.parent.mkdir(parents=True)
        plist_path.write_bytes(b"pre-bootstrap plist\x00bytes\n")
        lock_path = self.home / "night-custody/magistrate/magistrate.lock"
        before = {plist_path: plist_path.read_bytes(), lock_path: None}
        self.environment["LAUNCHCTL_FAIL_COMMAND"] = "bootstrap"

        completed = self._run(self.shadow_script, "--install")

        self.assertEqual(3, completed.returncode, completed.stderr)
        self.assertEqual(before[plist_path], plist_path.read_bytes())
        self.assertFalse(lock_path.exists(), before[lock_path])
        self.assertIn("failed to bootstrap", completed.stderr)

    def test_failed_post_load_verification_restores_exact_preexisting_plist_and_absent_lock(
        self,
    ) -> None:
        plist_path = self.home / "Library/LaunchAgents/com.joulewise.magistrate.plist"
        plist_path.parent.mkdir(parents=True)
        plist_path.write_bytes(b"pre-verification plist\x00bytes\n")
        lock_path = self.home / "night-custody/magistrate/magistrate.lock"
        before = {plist_path: plist_path.read_bytes(), lock_path: None}
        self.environment["LAUNCHCTL_FAIL_COMMAND"] = "print"

        completed = self._run(self.shadow_script, "--install")

        self.assertEqual(3, completed.returncode, completed.stderr)
        self.assertEqual(before[plist_path], plist_path.read_bytes())
        self.assertFalse(lock_path.exists(), before[lock_path])
        self.assertIn("launch agent verification failed", completed.stderr)


if __name__ == "__main__":
    unittest.main()
