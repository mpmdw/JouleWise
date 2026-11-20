"""Air LaunchAgent installer, notifier and main-CI check. Mocked gh/launchctl/osascript;
temp HOME; nothing is installed, loaded or signalled."""
from __future__ import annotations

import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import types
import unittest
from unittest import mock

from scripts.air import air_watch_agent as agent
from scripts.air import main_ci_watch as ci

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/air/install_air_watch.sh"
RED_JOBS = {"jobs": [{"name": "fences", "conclusion": "failure"}, {"name": "build", "conclusion": "failure"},
                     {"name": "test (3.13, 6)", "conclusion": "failure"}, {"name": "quick", "conclusion": "success"}]}
GREEN_JOBS = {"jobs": [{"name": "fences", "conclusion": "success"}, {"name": "quick", "conclusion": "success"}]}


def fake_gh(runs, jobs):
    def runner(argv, **_):
        if argv[1:3] == ["run", "list"]:
            out = runs
        elif argv[1:3] == ["run", "view"]:
            out = jobs[int(argv[3])]
        else:
            raise AssertionError(argv)
        return subprocess.CompletedProcess(argv, 0, json.dumps(out).encode(), b"")
    return runner


def run_doc(run_id, status="completed"):
    return {"databaseId": run_id, "status": status, "conclusion": "failure", "headSha": "a" * 40, "event": "push"}


class MainCiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def check(self, state, runs, jobs):
        with mock.patch.object(ci.subprocess, "run", side_effect=fake_gh(runs, jobs)):
            return ci.check(state)

    def test_red_fires_once_per_run(self):
        state = ci.load(self.tmp / "s.json")
        events = self.check(state, [run_doc(7)], {7: RED_JOBS})
        self.assertEqual([(e.level, e.code) for e in events], [("ALARM", "MAIN_CI_RED")])
        self.assertIn("run=7", events[0].fields)
        self.assertIn("jobs=fences,test(3.13,6)", events[0].fields)
        self.assertNotIn("build", events[0].fields)
        ci.save_state(self.tmp / "s.json", state)
        reloaded = ci.load(self.tmp / "s.json")
        self.assertEqual(self.check(reloaded, [run_doc(7)], {7: RED_JOBS}), [])
        self.assertEqual(len(self.check(reloaded, [run_doc(8), run_doc(7)], {8: RED_JOBS})), 1)

    def test_green_and_in_progress_quiet(self):
        state = ci.load(self.tmp / "s.json")
        self.assertEqual(self.check(state, [run_doc(9)], {9: GREEN_JOBS}), [])
        # Newest completed run is green even though an older one was red.
        self.assertEqual(self.check(state, [run_doc(11, "in_progress"), run_doc(10), run_doc(7)],
                                    {10: GREEN_JOBS, 7: RED_JOBS}), [])
        self.assertEqual(self.check(state, [], {}), [])

    def test_gh_unavailable_is_one_info(self):
        state = ci.load(self.tmp / "s.json")
        for failure in (FileNotFoundError(), subprocess.CompletedProcess([], 4, b"", b"auth")):
            state = ci.load(self.tmp / "missing.json")
            outcome = {"side_effect": failure} if isinstance(failure, Exception) else {"return_value": failure}
            with mock.patch.object(ci.subprocess, "run", **outcome):
                first, second = ci.check(state), ci.check(state)
            self.assertEqual([(e.level, e.code) for e in first], [("INFO", "GH_UNAVAILABLE")])
            self.assertEqual(second, [])
        status = None
        with mock.patch.object(ci.subprocess, "run", side_effect=FileNotFoundError()):
            status = ci.run_once(self.tmp / "s2.json")
        self.assertEqual(status, ci.EXIT_CODES["quiet"])

    def test_corrupt_state_resets(self):
        (self.tmp / "s.json").write_text("not json")
        self.assertEqual(ci.load(self.tmp / "s.json")["raised"], [])


class NotifyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.log = self.tmp / "Logs/air-watch.log"

    def test_alarm_notifies_structural_fields_only(self):
        line = '2026-11-12 22:00:00 ALARM RESULT_NOT_MEASURED refs/heads/night-results/p1 outcome="x" secret'
        with mock.patch.object(agent.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], 0)) as run:
            self.assertTrue(agent.notify(line, self.log))
        script = run.call_args.args[0][2]
        self.assertIn("ALARM RESULT_NOT_MEASURED refs/heads/night-results/p1", script)
        self.assertNotIn("secret", script)
        self.assertNotIn("outcome", script)
        self.assertIn("NOTIFY ok ALARM RESULT_NOT_MEASURED", self.log.read_text())

    def test_info_skipped_and_failure_logged(self):
        with mock.patch.object(agent.subprocess, "run") as run:
            self.assertFalse(agent.notify("2026-11-12 22:00:00 INFO RESULT ref x", self.log))
        run.assert_not_called()
        with mock.patch.object(agent.subprocess, "run", side_effect=FileNotFoundError()):
            self.assertFalse(agent.notify("2026-11-12 22:00:00 NOTICE RESULT_WITH_FLAGS ref", self.log))
            self.assertEqual(agent.main(["notify", "--log", str(self.log), "2026-11-12 22:00:00 ALARM X y"]), 0)
        self.assertIn("NOTIFY failed NOTICE RESULT_WITH_FLAGS", self.log.read_text())

    def test_quote_injection_stripped(self):
        _, text = agent.structural_text('2026-11-12 22:00:00 ALARM A"b\\c sub"j')
        self.assertNotIn('"', text)
        self.assertNotIn("\\", text)

    def test_run_supervises_child_and_ci(self):
        child = mock.Mock()
        child.poll.side_effect = [None, None, 20]
        popen = mock.Mock(return_value=child)
        args = types.SimpleNamespace(python="/py", log=self.log, interval=120, hours=24, watch_arg=[],
                                     ci_interval=900, ci_state=self.tmp / "ci.json", gh="gh", repo=None,
                                     exit_state=self.tmp / "exit.json")
        ticks = iter(range(0, 10000, 1000))
        with mock.patch.object(agent.main_ci_watch, "run_once", return_value=0) as once:
            status = agent.run(args, popen=popen, sleep=lambda _: None, clock=lambda: next(ticks))
        self.assertEqual(status, 20)
        argv = popen.call_args.args[0]
        self.assertEqual(argv[2:4], ["--loop", "--keep-going"])
        self.assertEqual(argv[argv.index("--notify-cmd") + 1:][-3:], ["notify", "--log", str(self.log)])
        self.assertEqual(once.call_count, 2)
        self.assertIn("--current-from-origin", argv)
        self.assertFalse((self.tmp / "exit.json").exists())

    def test_watcher_failure_posts_rate_limited_watcher_exit(self):
        args = types.SimpleNamespace(python="/py", log=self.log, interval=120, hours=24, watch_arg=[],
                                     ci_interval=0, ci_state=self.tmp / "ci.json", gh="gh", repo=None,
                                     exit_state=self.tmp / "exit.json")
        with mock.patch.object(agent.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], 0)) as osa:
            for _ in range(2):
                child = mock.Mock()
                child.poll.return_value = 2
                self.assertEqual(agent.run(args, popen=mock.Mock(return_value=child), sleep=lambda _: None), 2)
            self.assertEqual(osa.call_count, 1)
            self.assertEqual(osa.call_args.args[0][0], "/usr/bin/osascript")
            self.assertIn("ALARM WATCHER_EXIT agent", osa.call_args.args[0][2])
            # A different status, or the same one after an hour, notifies again.
            self.assertTrue(agent.watcher_exit(3, args.exit_state, self.log))
            self.assertTrue(agent.watcher_exit(2, args.exit_state, self.log, now=agent.time.time() + 3700))
            # Spawn failure (e.g. python missing) also notifies.
            self.assertEqual(agent.run(args, popen=mock.Mock(side_effect=FileNotFoundError())), 2)
        self.assertEqual(osa.call_count, 4)
        self.assertIn("WATCHER_EXIT_SUPPRESSED", self.log.read_text())


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.home)
        self.calls = self.home / "launchctl.calls"
        fake = self.home / "fake-launchctl"
        fake.write_text(f'#!/bin/sh\necho "$@" >> "{self.calls}"\n[ "$1" != print ]\n')
        fake.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), JW_LAUNCHCTL=str(fake),
                        JW_AIR_PYTHON="/opt/example/python3.13")

    def sh(self, *flags):
        return subprocess.run(["sh", str(INSTALLER), *flags], env=self.env, capture_output=True,
                              text=True, timeout=30)

    def test_dry_run_renders_and_changes_nothing(self):
        done = self.sh("--dry-run")
        self.assertEqual(done.returncode, 0, done.stderr)
        xml = done.stdout[:done.stdout.index("</plist>") + len("</plist>")]
        plist = plistlib.loads(xml.encode())
        self.assertEqual(plist["Label"], "com.joulewise.air-watch")
        self.assertTrue(plist["KeepAlive"])
        statedir = str(self.home / "Library/Application Support/JouleWise/air-watch")
        self.assertEqual(plist["ProgramArguments"][:2], ["/bin/sh", statedir + "/air-watch-run.sh"])
        log = str(self.home / "Library/Logs/JouleWise/air-watch.log")
        self.assertEqual(plist["StandardOutPath"], log)
        self.assertEqual(plist["WorkingDirectory"], statedir)
        self.assertIn(f"REPO='{ROOT}'", done.stdout)
        self.assertIn("PYTHON='/opt/example/python3.13'", done.stdout)
        self.assertIn("bootout gui/", done.stdout)
        self.assertNotRegex(done.stdout, r"@[A-Z]+@")
        self.assertIn("bootstrap gui/", done.stdout)
        self.assertFalse((self.home / "Library").exists())
        self.assertFalse(self.calls.exists())

    def test_uninstall_idempotent(self):
        for _ in range(2):
            done = self.sh("--uninstall")
            self.assertEqual(done.returncode, 0, done.stderr)
        # bootout always runs: a loaded job whose plist was removed by hand is still stopped.
        self.assertEqual(self.calls.read_text().count("bootout"), 2)
        self.calls.unlink()
        agents = self.home / "Library/LaunchAgents"
        agents.mkdir(parents=True)
        (agents / "com.joulewise.air-watch.plist").write_text("x")
        for _ in range(2):
            self.assertEqual(self.sh("--uninstall").returncode, 0)
        self.assertFalse((agents / "com.joulewise.air-watch.plist").exists())
        self.assertEqual(self.calls.read_text().count("bootout"), 2)
        self.assertEqual(self.sh("--uninstall", "--dry-run").returncode, 0)

    def test_install_in_temp_home_with_fake_launchctl(self):
        done = self.sh()
        self.assertEqual(done.returncode, 0, done.stderr)
        plist = self.home / "Library/LaunchAgents/com.joulewise.air-watch.plist"
        self.assertEqual(plistlib.loads(plist.read_bytes())["Label"], "com.joulewise.air-watch")
        self.assertIn("bootstrap gui/", self.calls.read_text())
        wrapper = self.home / "Library/Application Support/JouleWise/air-watch/air-watch-run.sh"
        self.assertTrue(os.access(wrapper, os.X_OK))

    def test_missing_repo_wrapper_posts_watcher_exit_once(self):
        statedir = self.home / "state"
        log = self.home / "Logs/air-watch.log"
        text = (ROOT / "scripts/air/air-watch-run.sh.template").read_text()
        for key, value in (("@REPO@", str(self.home / "unmounted/JouleWise")), ("@PYTHON@", "/opt/example/py"),
                           ("@LOG@", str(log)), ("@STATEDIR@", str(statedir))):
            text = text.replace(key, value)
        wrapper = self.home / "run.sh"
        wrapper.write_text(text)
        osa_calls = self.home / "osa.calls"
        osa = self.home / "fake-osascript"
        osa.write_text(f'#!/bin/sh\necho "$@" >> "{osa_calls}"\n')
        osa.chmod(0o755)
        env = dict(self.env, JW_OSASCRIPT=str(osa))
        for _ in range(2):
            done = subprocess.run(["sh", str(wrapper)], env=env, capture_output=True, timeout=30)
            self.assertEqual(done.returncode, 78)
        self.assertEqual(osa_calls.read_text().count("WATCHER_EXIT"), 1)
        self.assertIn("NOTIFY ok ALARM WATCHER_EXIT agent repo_missing", log.read_text())
        self.assertIn("WATCHER_EXIT_SUPPRESSED", log.read_text())

    def test_bad_flag(self):
        self.assertEqual(self.sh("--bogus").returncode, 2)


if __name__ == "__main__":
    unittest.main()


class CurrentFromOriginTest(unittest.TestCase):
    def test_private_ref_then_local_fallback(self):
        from scripts.air import night_results_watch as w
        from tests.git_fixture import init_git_fixture
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        bare, source, air = (root / n for n in ("origin", "source", "air"))
        for path in (bare, source, air):
            path.mkdir()
            init_git_fixture(path, *(("--bare",) if path == bare else ()))

        def git(path, *args):
            return subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True).stdout

        for path in (source, air):
            git(path, "remote", "add", "origin", str(bare))
        remote_doc = {"armed": {"plan_id": "fresh-plan", "t0_epoch_s": 1, "latest_end_epoch_s": 2}}
        (source / "docs/process").mkdir(parents=True)
        (source / "docs/process/CURRENT.json").write_text(json.dumps(remote_doc))
        git(source, "add", ".")
        git(source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "c")
        git(source, "push", "origin", "HEAD:refs/heads/main")
        local = root / "local-CURRENT.json"
        local.write_text(json.dumps({"armed": {"plan_id": "stale-plan"}}))
        transport = w.Git(air)
        doc, stale = w.fresh_current(transport, local)
        self.assertFalse(stale)
        self.assertEqual(doc["armed"]["plan_id"], "fresh-plan")
        self.assertTrue(git(air, "rev-parse", "refs/air-watch/main").strip())
        self.assertFalse((air / "docs").exists())  # working tree untouched
        self.assertFalse((air / ".git/FETCH_HEAD").exists())
        git(air, "remote", "set-url", "origin", str(root / "unmounted"))
        doc, stale = w.fresh_current(transport, local)
        self.assertTrue(stale)
        self.assertEqual(doc["armed"]["plan_id"], "stale-plan")

    def test_cli_reports_current_stale_once(self):
        from scripts.air import night_results_watch as w
        import contextlib
        import io

        class Offline:
            def check_origin(self):
                pass

            def fetch_main(self):
                raise w.WatchError("GIT_FAILED")

            def ls_remote(self, _):
                return {}

        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        out = io.StringIO()
        with mock.patch.object(w, "Git", return_value=Offline()), \
                mock.patch.object(w, "optional_exit_module", return_value=None), \
                mock.patch.object(w.time, "sleep", side_effect=[None, None, KeyboardInterrupt]), \
                contextlib.redirect_stdout(out), self.assertRaises(KeyboardInterrupt):
            w.main(["--loop", "--keep-going", "--current-from-origin",
                    "--state", str(root / "s"), "--current", str(root / "absent")])
        self.assertEqual(out.getvalue().count("INFO CURRENT_STALE"), 1)
