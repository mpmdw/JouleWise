"""WP10 fence decisions, real CLI, and launchd handoff with synthetic jobs only."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from scripts import launch_align_r0 as launcher
from scripts import magistrate_watchdog as wd
from tests.test_magistrate_watchdog import WatchdogTestCase


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/launch_align_r0.py"


class DeskFenceTests(WatchdogTestCase):
    def fence(self, *, pid=400, deadline=None):
        record = {"purpose": "align-r0:fixture", "pid": pid,
                  "deadline": self.base.timestamp() + 3600 if deadline is None else deadline}
        self.harness.storage.atomic_json(self.harness.storage.root / launcher.FENCE_NAME, record)
        return record

    def test_active_fence_skips_network_and_fork(self):
        self.fence()
        self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", "desk job")]
        with mock.patch.object(self.harness.deps, "git_probe") as network, \
             mock.patch.object(wd.os, "fork") as fork:
            decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("FENCED", decision.state)
        self.assertFalse(decision.launch)
        network.assert_not_called()
        fork.assert_not_called()
        self.assertTrue((self.harness.storage.root / launcher.FENCE_NAME).exists())

    def test_dead_pid_and_expired_deadline_clear_and_allow_launch(self):
        for pid, command, deadline in ((401, "desk job", self.base.timestamp() + 10),
                                       (400, "desk job", self.base.timestamp()),
                                       (400, "desk job <defunct>", self.base.timestamp() + 10)):
            with self.subTest(pid=pid, command=command, deadline=deadline):
                self.fence(pid=pid, deadline=deadline)
                self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", command)]
                decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
                self.assertTrue(decision.launch)
                self.assertFalse((self.harness.storage.root / launcher.FENCE_NAME).exists())

    def test_no_fence_preserves_stop_backoff_owner_and_plan(self):
        self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).launch)
        self.assertFalse((self.harness.storage.root / ".desk-fence.lock").exists())
        self.harness.stop = wd.StopObservation("STOPPED", "fixture stop")
        self.assertEqual("STOPPED", wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)
        self.harness.stop = wd.StopObservation("CLEAR", "clear")
        state = wd.initial_state()
        state["next_eligible_epoch_s"] = self.base.timestamp() + 100
        state["backoff_boot_id"] = wd.current_boot_id()
        self.assertEqual("BACKOFF", wd.decide(self.harness.storage, self.harness.deps, state).state)
        self.write_live_lock()
        self.harness.processes.rows = [wd.ProcessInfo(100, 99, "token-a", "session")]
        self.assertEqual("ACTIVE", wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)
        self.make_plan(t0=self.base.timestamp())
        self.assertEqual("STANDDOWN_KILL", wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)

    def test_plan_standdown_still_wins_during_desk_fence(self):
        self.make_plan(t0=self.base.timestamp() + wd.TERM_LEAD_S)
        self.write_live_lock()
        self.fence()
        self.harness.processes.rows = [wd.ProcessInfo(100, 99, "token-a", "session"),
                                       wd.ProcessInfo(400, 1, "start", "desk job")]
        decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
        self.assertEqual("STANDDOWN_TERM", decision.state)
        self.assertTrue(decision.adopt)

    def test_malformed_and_unreadable_fences_fail_closed(self):
        for value in ([], {}, {"purpose": "r0", "pid": True, "deadline": 10},
                      {"purpose": "r0", "pid": 400, "deadline": float("nan")}):
            with self.subTest(value=value):
                self.harness.storage.atomic_json(self.harness.storage.root / launcher.FENCE_NAME, value)
                decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
                self.assertEqual("HOLD_DESK_FENCE", decision.state)
        self.fence()
        with mock.patch.object(wd, "read_desk_fence", side_effect=PermissionError("fixture")):
            self.assertEqual("HOLD_UNSAFE", wd._launch_fence(
                self.harness.storage, self.harness.deps, wd.initial_state()).state)

    def test_stale_dry_run_reports_removal_without_writing(self):
        self.fence()
        self.harness.storage.dry_run = True
        self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).launch)
        self.assertTrue((self.harness.storage.root / launcher.FENCE_NAME).exists())
        self.assertTrue(any(action.startswith("unlink ") for action in self.harness.storage.would_write))
        self.assertFalse((self.harness.storage.root / ".desk-fence.lock").exists())

    def test_boundary_recheck_and_resident_remote_probe_obey_fence(self):
        self.fence()
        self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", "desk job")]
        self.assertEqual("FENCED", wd._launch_fence(self.harness.storage, self.harness.deps, wd.initial_state()).state)
        self.assertFalse(wd._remote_probe_allowed(self.harness.storage, self.harness.deps, wd.initial_state()))

    def test_stale_removal_by_decide_records_event_and_notice(self):
        for pid, deadline, why in ((401, self.base.timestamp() + 10, "owner pid dead before deadline"),
                                   (400, self.base.timestamp(), "deadline passed")):
            with self.subTest(why=why):
                record = self.fence(pid=pid, deadline=deadline)
                self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", "desk job")]
                state = wd.initial_state()
                self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, state).launch)
                notices = [n for n in state["notice_pending"] if n["kind"] == "desk_fence_stale"]
                self.assertEqual(1, len(notices))
                self.assertIn(why, notices[0]["reason"])
                self.assertIn("spotlight", notices[0]["reason"].lower())
                events = [json.loads(line) for line in
                          (self.harness.storage.root / "events.jsonl").read_text().splitlines()]
                self.assertIn({"kind": "desk_fence_stale_removed", "why": why, "fence": record},
                              [{k: e.get(k) for k in ("kind", "why", "fence")} for e in events])

    def test_active_fence_and_no_fence_queue_no_notice(self):
        state = wd.initial_state()
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.fence()
        self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", "desk job")]
        wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual([], state["notice_pending"])

    def test_boundary_rechecks_treat_stale_as_inactive_without_removal(self):
        self.fence(pid=401)
        self.harness.processes.rows = []
        self.assertIsNone(wd._launch_fence(self.harness.storage, self.harness.deps, wd.initial_state()))
        self.assertTrue(wd._remote_probe_allowed(self.harness.storage, self.harness.deps, wd.initial_state()))
        self.assertTrue((self.harness.storage.root / launcher.FENCE_NAME).exists())

    def test_fence_published_during_version_probe_prevents_spawn(self):
        binary = self.temp / "binary"
        binary.write_text("fixture")
        binary.chmod(0o755)
        link = self.temp / "session-link"
        link.symlink_to(binary)
        def version(_path):
            self.fence()
            self.harness.processes.rows = [wd.ProcessInfo(400, 1, "start", "desk job")]
            return "fixture"
        self.harness.deps.version_probe = version
        self.assertIsNone(wd.start_session(self.harness.storage, self.harness.deps,
                                          wd.initial_state(), binary_path=link))
        self.assertEqual([], self.harness.spawn_calls)
        self.assertFalse((self.harness.storage.root / "magistrate.lock").exists())


class DeskFenceCliTests(unittest.TestCase):
    def test_real_entrypoint_active_fence(self):
        """D-172: real parser, service lock, dependencies; process/network seams only.

        JW_WP10_WATCHDOG_SOURCE admits a local source copy for the recorded
        deadline-test mutation. It is not a production override.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custody = root / "magistrate"
            custody.mkdir()
            launcher.write_fence(custody, {"purpose": "align-r0:cli", "pid": os.getpid(),
                                          "deadline": time.time() + 600})
            source = os.environ.get("JW_WP10_WATCHDOG_SOURCE", str(REPO / "scripts/magistrate_watchdog.py"))
            code = (
                "import importlib.util, os, sys\n"
                "spec=importlib.util.spec_from_file_location('wp10_wd',sys.argv[1])\n"
                "wd=importlib.util.module_from_spec(spec); sys.modules[spec.name]=wd; spec.loader.exec_module(wd)\n"
                "wd.RealProcessTable.snapshot=lambda self:[wd.ProcessInfo(os.getppid(),1,'fixture','synthetic desk owner')]\n"
                "wd.remote_stop_probe=lambda **kwargs:wd.StopObservation('STOPPED','fixture network seam')\n"
                "raise SystemExit(wd.main(sys.argv[2:]))\n"
            )
            result = subprocess.run([sys.executable, "-B", "-c", code, source, "tick", "--custody-root", str(custody)],
                                    cwd=REPO, env={**os.environ, "HOME": str(root / "home")},
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((custody / "watchdog.lock").exists())
            state = json.loads((custody / "state.json").read_text())
            self.assertEqual("FENCED", state["state"], state.get("reason"))
            self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])
            self.assertFalse((custody / "attempts").exists())


class DisplayDwellTests(unittest.TestCase):
    def test_production_dwell_is_the_300_s_constant(self):
        self.assertEqual(launcher.DISPLAY_SLEEP_DWELL_S, 300)
        with mock.patch.dict(os.environ, {}, clear=False) as env:
            env.pop(launcher.DISPLAY_DWELL_TEST_ENV, None)
            self.assertEqual(launcher.display_dwell_seconds(), 300)

    def test_deadline_without_room_for_the_dwell_refuses_before_sleeping(self):
        args = SimpleNamespace(deadline=time.time() + 100, runner_spec=Path("/nonexistent"),
                               pmset_bin="/usr/bin/false")
        with mock.patch.dict(os.environ, {launcher.DISPLAY_DWELL_TEST_ENV: "300"}), \
                mock.patch.object(launcher.time, "sleep") as sleep, \
                mock.patch.object(launcher.subprocess, "run") as run, \
                mock.patch.object(launcher.signal, "signal"):
            with self.assertRaisesRegex(TimeoutError, "display dwell"):
                launcher.run_until_deadline(args)
        sleep.assert_not_called()
        run.assert_not_called()


class LaunchAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.custody = self.root / "magistrate"
        self.repo = self.root / "measurement"
        (self.repo / "scripts").mkdir(parents=True)
        self.config = self.root / "config.json"
        self.config.write_text(json.dumps({"root": str(self.root), "case": "normal"}))
        # The R0 display dwell is 300 s; the harness shortens it through the
        # launcher's documented test seam so the synthetic job stays fast.
        self.env = {**os.environ, "HOME": str(self.root / "home"), "WP10_FIXTURE_ROOT": str(self.root),
                    launcher.DISPLAY_DWELL_TEST_ENV: "0.5"}
        self.output = self.root / "new-record"
        self.owner = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(120)"])
        self.addCleanup(self.stop, self.owner)
        self.worker_pid = None
        self.addCleanup(self.stop_worker)
        self.launchctl = self.script("launchctl", '''
import json, os, plistlib, signal, subprocess, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
with (root/'launchctl.log').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
if sys.argv[1]=='bootstrap':
    if (root/'fail-bootstrap').exists(): sys.exit(19)
    job=plistlib.loads(Path(sys.argv[3]).read_bytes())
    (root/'service.loaded').write_text(sys.argv[2]+'/'+job['Label'])
    # A small synthetic launchd reaps the worker and records its exit status.
    # The test does not signal a completed job's potentially recycled PID.
    subprocess.Popen([sys.executable, str(root/'fake-launchd'), sys.argv[3]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
else:
    if (root/'fail-bootout').exists():
        print('fixture bootout denied', file=sys.stderr); sys.exit(5)
    if not (root/'service.loaded').exists():
        if (root/'bootout-esrch').exists():
            print('Boot-out failed: 3: No such process', file=sys.stderr); sys.exit(3)
        print('Could not find service', file=sys.stderr); sys.exit(113)
    assert (root/'service.loaded').read_text()==sys.argv[2]
    (root/'bootout-signals.log').write_text((root/'signals.log').read_text() if (root/'signals.log').exists() else '')
    (root/'service.loaded').unlink()
    if (root/'worker.pid').exists() and not (root/'worker.done').exists():
        try: os.kill(int((root/'worker.pid').read_text()), signal.SIGTERM)
        except ProcessLookupError: pass
''')
        self.script("fake-launchd", '''
import os, plistlib, subprocess, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
job=plistlib.loads(Path(sys.argv[1]).read_bytes())
with open(job['StandardOutPath'],'w') as out, open(job['StandardErrorPath'],'w') as err:
    p=subprocess.Popen(job['ProgramArguments'], cwd=job['WorkingDirectory'],
                       env={**os.environ, **job['EnvironmentVariables']},
                       stdout=out, stderr=err, start_new_session=True)
(root/'worker.pid').write_text(str(p.pid))
(root/'worker.done').write_text(str(p.wait()))
''')
        self.pmset = self.script("pmset", '''
import os, sys
from pathlib import Path
import time
root=Path(os.environ['WP10_FIXTURE_ROOT'])
if sys.argv[1:]==['displaysleepnow']:
    with (root/'display.log').open('a') as f: f.write(f"{time.time()}\\n")
    if (root/'display-fail').exists():
        print('fixture display sleep denied', file=sys.stderr); sys.exit(1)
    sys.exit(0)
(root/'pmset.argv').write_text(' '.join(sys.argv[1:]))
print("Now drawing from 'Battery Power'" if (root/'battery').exists() else "Now drawing from 'AC Power'")
''')
        self.pgrep = self.script("pgrep", '''
import json, os, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
with (root/'pgrep.log').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
if (root/'pgrep-error').exists() and sys.argv[-1]=='spotlightknowledged': sys.exit(2)
print(900000001 if sys.argv[-1]=='corespotlightd' else 900000002)
''')
        self.kill = self.script("kill", '''
import os, signal, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
with (root/'signals.log').open('a') as f: f.write(' '.join(sys.argv[1:])+'\\n')
pid=int(sys.argv[2])
if sys.argv[1]=='-CONT' and (root/'cont-fail').exists(): sys.exit(1)
if pid not in (900000001,900000002):
    try: os.kill(pid, getattr(signal,'SIG'+sys.argv[1][1:]))
    except ProcessLookupError: pass
''')
        (self.repo / "scripts/align_r0_checks.py").write_text('''
import argparse, json, sys, time
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--config'); p.add_argument('--output')
p.add_argument('--checks'); p.add_argument('--keep-going', action='store_true'); a=p.parse_args()
c=json.loads(Path(a.config).read_text()); root=Path(c['root'])
Path(a.output).mkdir(); (root/'runner.started').write_text(str(time.time()))
import os; (root/'runner.display').write_text(os.environ.get('JOULEWISE_R0_DISPLAY_PREP', ''))
(root/'runner.args').write_text(json.dumps({'checks': a.checks, 'keep_going': a.keep_going}))
if c['case']=='term': time.sleep(120)
sys.exit(7 if c['case']=='error' else 0)
''')

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def stop_worker(self):
        path = self.root / "worker.pid"
        if path.exists() and not (self.root / "worker.done").exists():
            try:
                os.killpg(int(path.read_text()), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                # macOS reports EPERM for a group whose leader is a zombie.
                pass
            self.wait_for(lambda: (self.root / "worker.done").exists())

    def script(self, name, code):
        path = self.root / name
        path.write_text(f"#!{sys.executable}\n" + code)
        path.chmod(0o755)
        return path

    def wait_for(self, predicate, timeout=8):
        until = time.monotonic() + timeout
        while time.monotonic() < until:
            if predicate():
                return
            time.sleep(0.03)
        self.fail("timed out waiting for synthetic LaunchAgent; " + self.logs())

    def logs(self):
        return "\n".join(p.read_text() for p in self.custody.glob("r0-launches/*/stderr.log"))

    def launch(self, *extra):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "launch", "--repo", str(self.repo),
                               "--config", str(self.config), "--output", str(self.output),
                               "--python-bin", sys.executable, "--custody-root", str(self.custody),
                               "--disk-path", str(self.root), "--magistrate-pid", str(self.owner.pid),
                               "--deadline", str(time.time() + 120), "--start-wait-seconds", "3",
                               "--launchctl-bin", str(self.launchctl), "--pmset-bin", str(self.pmset),
                               "--pgrep-bin", str(self.pgrep), "--kill-bin", str(self.kill), *extra],
                              cwd=REPO, env=self.env, capture_output=True, text=True, timeout=15)

    def watchdog(self):
        from tests.test_magistrate_watchdog import Harness
        harness = Harness(self.custody, dt.datetime.now().astimezone())
        pid = int((self.root / "worker.pid").read_text())
        record = launcher.read_fence(self.custody)
        harness.processes.rows = [wd.ProcessInfo(pid, 1, "fixture", "LaunchAgent wrapper")] if record else []
        with mock.patch.object(wd.os, "fork", return_value=123) as fork:
            decision = wd.tick(harness.storage, harness.deps)
        self.assertEqual(decision.launch, fork.called)
        return decision

    def test_launchagent_handoff_fences_until_magistrate_exits_and_is_one_shot(self):
        result = self.launch()
        self.assertEqual(0, result.returncode, result.stderr + self.logs())
        record = launcher.read_fence(self.custody)
        self.assertEqual({"purpose", "pid", "deadline"}, set(record))
        self.assertNotEqual(self.owner.pid, record["pid"])
        self.assertEqual("FENCED", self.watchdog().state)
        self.assertFalse((self.root / "runner.started").exists())
        job = plistlib.loads(next(self.custody.glob("r0-launches/*/*.plist")).read_bytes())
        self.assertTrue(job["RunAtLoad"])
        self.assertNotIn("KeepAlive", job)
        self.assertNotIn("StartInterval", job)
        self.assertNotIn("align_r0_checks.py", " ".join(job["ProgramArguments"]))
        self.assertNotIn("nohup", " ".join(job["ProgramArguments"]))
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "runner.started").exists())
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertTrue(self.watchdog().launch)
        self.assertEqual("-g batt", (self.root / "pmset.argv").read_text())
        stdout = next(self.custody.glob("r0-launches/*/stdout.log")).read_text()
        self.assertIn('"disk_check": "report_only"', stdout)
        self.assert_resumed()
        self.assert_unloaded(0)

    def assert_unloaded(self, exit_status):
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertEqual(str(exit_status), (self.root / "worker.done").read_text())
        calls = [json.loads(row) for row in (self.root / "launchctl.log").read_text().splitlines()]
        job = plistlib.loads(next(self.custody.glob("r0-launches/*/*.plist")).read_bytes())
        self.assertEqual(["bootstrap", "bootout"], [call[0] for call in calls])
        self.assertEqual(["bootout", f"gui/{os.getuid()}/{job['Label']}"], calls[1])
        self.assertFalse((self.root / "service.loaded").exists())
        snapshot = self.root / "bootout-signals.log"
        if snapshot.exists():
            self.assertEqual((self.root / "signals.log").read_text(), snapshot.read_text())

    def assert_resumed(self):
        lines = (self.root / "signals.log").read_text().splitlines()
        for pid in (900000001, 900000002):
            self.assertIn(f"-STOP {pid}", lines)
            self.assertIn(f"-CONT {pid}", lines)
            self.assertLess(lines.index(f"-STOP {pid}"), lines.index(f"-CONT {pid}"))

    def assert_no_spotlight_signals(self):
        path = self.root / "signals.log"
        lines = path.read_text() if path.exists() else ""
        self.assertNotIn("-STOP ", lines)
        self.assertNotIn("-CONT ", lines)

    def test_spotlight_resumes_on_runner_error(self):
        self.config.write_text(json.dumps({"root": str(self.root), "case": "error"}))
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assert_resumed()
        self.assertTrue(self.watchdog().launch)
        self.assert_unloaded(7)

    def test_spotlight_resumes_on_sigterm(self):
        self.config.write_text(json.dumps({"root": str(self.root), "case": "term"}))
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "runner.started").exists())
        os.kill(int((self.root / "worker.pid").read_text()), signal.SIGTERM)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assert_resumed()
        self.assert_unloaded(143)

    def test_bootout_tolerates_service_already_gone(self):
        self.assertEqual(0, self.launch().returncode)
        (self.root / "service.loaded").unlink()
        self.stop(self.owner)
        self.assert_unloaded(0)
        self.assertIsNone(launcher.read_fence(self.custody))
        self.assert_resumed()
        self.assertNotIn("bootout failed", self.logs())

    def test_bootout_tolerates_no_such_process(self):
        (self.root / "bootout-esrch").touch()
        self.test_bootout_tolerates_service_already_gone()

    def test_bootout_failure_reports_error_after_spotlight_cleanup(self):
        (self.root / "fail-bootout").touch()
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertEqual("2", (self.root / "worker.done").read_text())
        self.assertIsNone(launcher.read_fence(self.custody))
        self.assert_resumed()
        self.assertTrue((self.root / "service.loaded").exists())
        self.assertIn("LaunchAgent bootout failed", self.logs())

    def test_spotlight_census_scopes_exact_names_to_current_uid(self):
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.assert_unloaded(0)
        calls = [json.loads(row) for row in (self.root / "pgrep.log").read_text().splitlines()]
        self.assertEqual([["-U", str(os.getuid()), "-x", name]
                          for name in ("corespotlightd", "spotlightknowledged")], calls)

    def test_sigterm_during_magistrate_wait_clears_fence_without_pausing(self):
        self.assertEqual(0, self.launch().returncode)
        os.kill(int((self.root / "worker.pid").read_text()), signal.SIGTERM)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertFalse((self.root / "runner.started").exists())
        self.assert_no_spotlight_signals()

    def test_magistrate_exit_timeout_refuses_without_pausing(self):
        self.assertEqual(0, self.launch("--exit-wait-seconds", "0.5").returncode)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertFalse((self.root / "runner.started").exists())
        self.assert_no_spotlight_signals()
        self.assertIn("magistrate did not exit", self.logs())

    def test_spotlight_resumes_and_runner_is_reaped_before_deadline(self):
        self.config.write_text(json.dumps({"root": str(self.root), "case": "term"}))
        # Ten seconds are reserved for cleanup; the synthetic runner times out
        # after approximately three seconds, with no long-running native work.
        self.assertEqual(0, self.launch("--deadline", str(time.time() + 13)).returncode)
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "runner.started").exists())
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assert_resumed()
        self.assertIn("timed out", self.logs())

    def test_expired_fence_is_cleared_and_relaunch_allowed_even_with_live_job(self):
        self.assertEqual(0, self.launch().returncode)
        with launcher.fence_lock(self.custody):
            record = launcher.read_fence(self.custody)
            launcher.write_fence(self.custody, {**record, "deadline": time.time() - 1})
        self.assertTrue(self.watchdog().launch)
        self.assertIsNone(launcher.read_fence(self.custody))

    def test_dead_job_fence_is_cleared_and_relaunch_allowed(self):
        self.assertEqual(0, self.launch().returncode)
        self.stop_worker()
        from tests.test_magistrate_watchdog import Harness
        harness = Harness(self.custody, dt.datetime.now().astimezone())
        self.assertTrue(wd.decide(harness.storage, harness.deps, wd.initial_state()).launch)
        self.assertIsNone(launcher.read_fence(self.custody))

    def test_battery_refuses_before_pausing_spotlight(self):
        (self.root / "battery").touch()
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertFalse((self.root / "runner.started").exists())
        self.assertFalse((self.root / "signals.log").exists())
        self.assertIn("requires AC power", self.logs())

    def test_partial_pause_error_resumes_already_stopped_process(self):
        (self.root / "pgrep-error").touch()
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        lines = (self.root / "signals.log").read_text()
        self.assertIn("-STOP 900000001", lines)
        self.assertIn("-CONT 900000001", lines)
        self.assertFalse((self.root / "runner.started").exists())

    def test_venv_interpreter_symlink_is_kept_unresolved(self):
        venv_bin = self.root / "venv" / "bin"
        venv_bin.mkdir(parents=True)
        link = venv_bin / "python"
        link.symlink_to(sys.executable)
        result = self.launch("--python-bin", str(link))
        self.assertEqual(0, result.returncode, result.stderr + self.logs())
        (job,) = self.custody.glob("r0-launches/*")
        self.assertEqual(str(link), json.loads((job / "runner.json").read_text())[0])
        (plist,) = job.glob("*.plist")
        self.assertIn(str(link), plistlib.loads(plist.read_bytes())["ProgramArguments"])

    def test_r0l3_runner_spec_defaults_to_keep_going_and_passes_checks(self):
        # R0-L3 item 3: desk runs keep going; a subset run (R0-L1) is headless.
        self.assertEqual(0, self.launch().returncode, self.logs())
        (job,) = self.custody.glob("r0-launches/*")
        spec = json.loads((job / "runner.json").read_text())
        self.assertEqual(spec[-1], "--keep-going")
        self.assertNotIn("--checks", spec)
        self.stop(self.owner)  # the magistrate exits; the runner starts
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertEqual(json.loads((self.root / "runner.args").read_text()),
                         {"checks": None, "keep_going": True})

    def test_r0l3_checks_subset_and_no_keep_going_reach_the_runner(self):
        subset = "host,disk,load,template,generated,memory,ladder,long-decode"
        self.assertEqual(0, self.launch("--checks", subset, "--no-keep-going").returncode, self.logs())
        (job,) = self.custody.glob("r0-launches/*")
        spec = json.loads((job / "runner.json").read_text())
        self.assertEqual(spec[spec.index("--checks") + 1], subset)
        self.assertNotIn("--keep-going", spec)
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertEqual(json.loads((self.root / "runner.args").read_text()),
                         {"checks": subset, "keep_going": False})

    def test_r0l3_display_sleeps_and_dwells_before_the_runner_and_is_recorded(self):
        # RUN_STATE 206: menu-bar redraws with the display on trip the census.
        self.assertEqual(0, self.launch().returncode, self.logs())
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        slept = float((self.root / "display.log").read_text().split()[0])
        started = float((self.root / "runner.started").read_text())
        self.assertGreaterEqual(started - slept, 0.5)
        prep = json.loads((self.root / "runner.display").read_text())
        self.assertEqual(prep["displaysleepnow"]["exit_code"], 0)
        self.assertEqual(prep["dwell_s"], 0.5)
        self.assertEqual(prep["dwell_constant_s"], launcher.DISPLAY_SLEEP_DWELL_S)

    def test_r0l3_display_sleep_failure_is_recorded_not_refused(self):
        (self.root / "display-fail").touch()
        self.assertEqual(0, self.launch().returncode, self.logs())
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.assertTrue((self.root / "runner.started").exists())
        prep = json.loads((self.root / "runner.display").read_text())
        self.assertEqual(prep["displaysleepnow"]["exit_code"], 1)
        self.assertIn("denied", prep["displaysleepnow"]["stderr"])

    def test_r0l3_malformed_checks_refuse_before_publication(self):
        for value in ("", "host;rm -rf /", "host,,ladder", "Host"):
            with self.subTest(value=value):
                result = self.launch("--checks", value)
                self.assertEqual(2, result.returncode)
                self.assertIn("R0 launch refused: --checks", result.stderr)
                self.assertIsNone(launcher.read_fence(self.custody))
                self.assertEqual([], list(self.custody.glob("r0-launches/*")))

    def test_bootstrap_failure_clears_only_its_own_fence(self):
        (self.root / "fail-bootstrap").touch()
        self.assertEqual(2, self.launch().returncode)
        self.assertIsNone(launcher.read_fence(self.custody))
        calls = [json.loads(row) for row in (self.root / "launchctl.log").read_text().splitlines()]
        self.assertEqual(["bootstrap", "bootout"], [call[0] for call in calls])

    def test_existing_fence_and_output_are_preserved(self):
        self.assertEqual(0, self.launch().returncode)
        original = launcher.read_fence(self.custody)
        self.assertEqual(2, self.launch().returncode)
        self.assertEqual(original, launcher.read_fence(self.custody))
        launcher.clear_owned(self.custody, "different-purpose")
        self.assertEqual(original, launcher.read_fence(self.custody))
        self.output.mkdir()
        self.assertEqual(2, self.launch().returncode)
        self.assertEqual(original, launcher.read_fence(self.custody))

    def stale_notice(self):
        from tests.test_magistrate_watchdog import Harness
        harness = Harness(self.custody, dt.datetime.now().astimezone())
        state = wd.initial_state()
        decision = wd.decide(harness.storage, harness.deps, state)
        return decision, [n for n in state["notice_pending"] if n["kind"] == "desk_fence_stale"]

    def test_normal_exit_removes_spotlight_record_and_queues_no_notice(self):
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: launcher.read_fence(self.custody) is None)
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertEqual([], list(self.custody.glob("r0-launches/*/spotlight-stopped")))
        self.assertEqual([], self.stale_notice()[1])

    def test_sigkill_leaves_record_and_watchdog_queues_stale_notice(self):
        self.config.write_text(json.dumps({"root": str(self.root), "case": "term"}))
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "runner.started").exists())
        # launchd SIGKILLs the job's process group; no trap can run.
        os.killpg(int((self.root / "worker.pid").read_text()), signal.SIGKILL)
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertNotIn("-CONT ", (self.root / "signals.log").read_text())
        record = next(self.custody.glob("r0-launches/*/spotlight-stopped")).read_text().split()
        self.assertEqual(["900000001", "corespotlightd", "900000002", "spotlightknowledged"], record)
        decision, notices = self.stale_notice()
        self.assertTrue(decision.launch)
        self.assertIsNone(launcher.read_fence(self.custody))
        self.assertEqual(1, len(notices))
        self.assertIn("owner pid dead", notices[0]["reason"])

    def test_resume_failure_keeps_fence_for_stale_notice(self):
        (self.root / "cont-fail").touch()
        self.assertEqual(0, self.launch().returncode)
        self.stop(self.owner)
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertEqual("2", (self.root / "worker.done").read_text())
        self.assertIsNotNone(launcher.read_fence(self.custody))
        self.assertTrue(list(self.custody.glob("r0-launches/*/spotlight-stopped")))
        self.assertIn("Spotlight resume failed", self.logs())
        decision, notices = self.stale_notice()
        self.assertTrue(decision.launch)
        self.assertEqual(1, len(notices))

    def test_far_future_deadline_is_refused_before_publication(self):
        result = self.launch("--deadline", str(time.time() + launcher.MAX_DESK_SECONDS + 60))
        self.assertEqual(2, result.returncode)
        self.assertIn("more than", result.stderr)
        self.assertIsNone(launcher.read_fence(self.custody))
        self.assertFalse((self.root / "launchctl.log").exists())

    def test_disk_is_report_only_at_66_gb(self):
        args = SimpleNamespace(pmset_bin=str(self.pmset), disk_path=self.root)
        with mock.patch.dict(os.environ, self.env), \
             mock.patch("shutil.disk_usage", return_value=SimpleNamespace(free=66_000_000_000)), \
             mock.patch("builtins.print") as output:
            launcher.preflight(args)
        self.assertEqual(66_000_000_000, json.loads(output.call_args.args[0])["free_bytes"])

    def test_disk_query_error_refuses(self):
        args = SimpleNamespace(pmset_bin=str(self.pmset), disk_path=self.root)
        with mock.patch.dict(os.environ, self.env), \
             mock.patch("shutil.disk_usage", side_effect=OSError("fixture disk unavailable")):
            with self.assertRaisesRegex(OSError, "fixture disk unavailable"):
                launcher.preflight(args)


if __name__ == "__main__":
    unittest.main()
