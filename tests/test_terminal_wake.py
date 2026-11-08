"""Synthetic notification tests; no launchd, agents or measurements."""

import datetime as dt
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from scripts import magistrate_watchdog as wd, run_night
from tests import test_magistrate_watchdog as twd


class TerminalWakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_marker_is_atomic_advisory_and_bound_to_plan(self):
        from joulewise.terminal_wake import publish, MARKER
        path = publish(self.root, "synthetic-plan", "HAZARD_PACK", now=100)
        self.assertEqual(path, self.root / MARKER)
        self.assertEqual(json.loads(path.read_bytes())["plan_id"], "synthetic-plan")
        self.assertEqual([MARKER], sorted(p.name for p in self.root.iterdir()))
        publish(self.root, "next-plan", "HAZARD_PACK", now=101)
        self.assertEqual(json.loads(path.read_bytes())["plan_id"], "next-plan")

    def test_no_notification_without_explicit_destination(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(run_night._notify_terminal(mock.Mock()))

    def test_reporting_starts_exit_observer_with_driver_pid_and_no_inherited_locks(self):
        from joulewise import terminal_wake as wake
        plan = mock.Mock(plan_id="synthetic", receipt_class="HAZARD_PACK")
        with mock.patch.dict(os.environ, {wake.DESTINATION_ENV: str(self.root)}), \
                mock.patch.object(wake.subprocess, "Popen") as spawn, \
                mock.patch.object(wake, "publish") as publish:
            run_night._notify_terminal(plan)
        argv = spawn.call_args.args[0]
        self.assertEqual(str(os.getpid()), argv[argv.index("--wait-pid") + 1])
        self.assertEqual(str(self.root), argv[argv.index("--root") + 1])
        self.assertTrue(spawn.call_args.kwargs["close_fds"])
        self.assertTrue(spawn.call_args.kwargs["start_new_session"])
        publish.assert_not_called()

    def test_exit_observer_never_publishes_for_a_live_driver(self):
        from joulewise import terminal_wake as wake
        with mock.patch.object(wake.os, "kill") as probe, \
                mock.patch.object(wake.time, "monotonic", side_effect=[0, 61]), \
                mock.patch.object(wake, "publish") as publish:
            self.assertIsNone(wake.publish_after_exit(self.root, "plan", "HAZARD_PACK", 4242))
        probe.assert_called_once_with(4242, 0)
        publish.assert_not_called()

    def test_exit_observer_requires_proven_absence(self):
        from joulewise import terminal_wake as wake
        for error in (PermissionError("denied"), OSError("unknown")):
            with self.subTest(error=error), mock.patch.object(wake.os, "kill", side_effect=error), \
                    mock.patch.object(wake, "publish") as publish:
                self.assertIsNone(wake.publish_after_exit(self.root, "plan", "HAZARD_PACK", 4242))
                publish.assert_not_called()

    def test_real_helper_publishes_only_after_synthetic_driver_exits(self):
        """Use real PID absence, argv parsing and publication, with no night work."""
        from joulewise import terminal_wake as wake
        repo = Path(__file__).resolve().parents[1]
        with subprocess.Popen([sys.executable, "-B", "-c", "input()"],
                              stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) as driver:
            with subprocess.Popen([
                sys.executable, "-B", "-m", "joulewise.terminal_wake", "--wait-pid", str(driver.pid),
                "--root", str(self.root), "--plan-id", "synthetic", "--receipt-class", "HAZARD_PACK"],
                cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as helper:
                try:
                    time.sleep(0.3)
                    self.assertIsNone(helper.poll())
                    self.assertFalse((self.root / wake.MARKER).exists())
                    driver.communicate(b"exit\n", timeout=5)
                    _, error = helper.communicate(timeout=5)
                    self.assertEqual(0, helper.returncode, error)
                    event = wake.read_event(self.root / wake.MARKER)
                    self.assertEqual("synthetic", event[1]["plan_id"])
                finally:
                    if driver.poll() is None:
                        driver.kill()
                        driver.wait(timeout=5)
                    if helper.poll() is None:
                        helper.kill()
                        helper.wait(timeout=5)

    def test_symlinked_tmpdir_resolves_but_publish_stays_strict(self):
        from joulewise.terminal_wake import publish
        link = self.root / "var"
        real = self.root / "private-var"
        real.mkdir()
        link.symlink_to(real, target_is_directory=True)
        with tempfile.TemporaryDirectory(dir=link) as directory:
            with self.assertRaisesRegex(ValueError, "unsymlinked"):
                publish(Path(directory), "synthetic", "HAZARD_PACK")
            self.assertTrue(publish(Path(directory).resolve(), "synthetic", "HAZARD_PACK").is_file())

    def test_finish_reporting_notifies_after_durable_courier_outcome(self):
        events = []
        plan = mock.Mock(plan_id="synthetic-plan", receipt_class="HAZARD_PACK")
        with mock.patch.object(run_night, "run_courier", return_value={"sent": True}), \
                mock.patch.object(run_night, "_write_courier_outcome", side_effect=lambda *a: events.append("outcome")), \
                mock.patch.object(run_night, "_durable_record", side_effect=lambda *a: events.append("durable")), \
                mock.patch.object(run_night, "_notify_terminal", side_effect=lambda *a: events.append("wake")):
            rc = run_night._finish_reporting(self.root, self.root, plan, 5, Path("synthetic-courier"))
        self.assertEqual(5, rc)
        self.assertEqual(["outcome", "durable", "wake"], events)

    def test_event_rechecks_existing_fence_after_driver_exits_and_dedupes(self):
        from joulewise.terminal_wake import publish
        publish(self.root, "synthetic-plan", "HAZARD_PACK", now=100)
        deps = mock.Mock()
        deps.wall_now.return_value = dt.datetime.fromtimestamp(101, dt.timezone.utc)
        storage = wd.Storage(self.root)
        fenced = wd.Decision("FENCED", "driver still exiting")
        launched = wd.Decision("READY", "existing gates passed", launch=True)
        deps.driver_probe.side_effect = [wd.CensusObservation(False, 0, "driver", ""),
                                         wd.CensusObservation(True, 1, "", "")]
        with mock.patch.object(wd, "tick", return_value=launched) as tick:
            self.assertEqual(launched, wd.tick_on_terminal_event(storage, deps))
        self.assertEqual(1, tick.call_count)
        deps.sleep.assert_called_once_with(1)
        with mock.patch.object(wd, "tick", return_value=fenced) as tick:
            wd.tick_on_terminal_event(storage, deps)
        self.assertEqual(1, tick.call_count)

    def test_missing_stale_malformed_events_and_other_holds_do_not_retry(self):
        from joulewise.terminal_wake import publish, MARKER
        storage, deps = wd.Storage(self.root), mock.Mock()
        deps.wall_now.return_value = dt.datetime.fromtimestamp(1000, dt.timezone.utc)
        for payload in (None, b"bad json", b"{}"):
            (self.root / MARKER).unlink(missing_ok=True)
            if payload is not None:
                (self.root / MARKER).write_bytes(payload)
            with mock.patch.object(wd, "tick", return_value=wd.Decision("FENCED", "held")) as tick:
                wd.tick_on_terminal_event(storage, deps)
            self.assertEqual(1, tick.call_count)
        publish(self.root, "stale", "HAZARD_PACK", now=100)
        with mock.patch.object(wd, "tick", return_value=wd.Decision("FENCED", "held")) as tick:
            wd.tick_on_terminal_event(storage, deps)
        self.assertEqual(1, tick.call_count)
        publish(self.root, "fresh", "HAZARD_PACK", now=1000)
        with mock.patch.object(wd, "tick", return_value=wd.Decision("NETWORK_UNCERTAIN", "held")) as tick:
            wd.tick_on_terminal_event(storage, deps)
        self.assertEqual(1, tick.call_count)

    def test_notification_failure_preserves_reporting_exit_code(self):
        with mock.patch.object(run_night, "run_courier", return_value={"sent": True}), \
                mock.patch.object(run_night, "_write_courier_outcome"), \
                mock.patch.object(run_night, "_durable_record"), \
                mock.patch.object(run_night, "_append_log"), \
                mock.patch.object(run_night, "_notify_terminal", side_effect=OSError("synthetic failure")):
            self.assertEqual(5, run_night._finish_reporting(self.root, self.root, mock.Mock(), 5, Path("courier")))

    def test_event_ack_failure_still_runs_ordinary_tick(self):
        from joulewise.terminal_wake import publish
        publish(self.root, "synthetic", "HAZARD_PACK", now=100)
        storage, deps = wd.Storage(self.root), mock.Mock()
        decision = wd.Decision("FENCED", "still gated")
        with mock.patch.object(storage, "atomic_json", side_effect=OSError("full disk")), \
                mock.patch.object(wd, "tick", return_value=decision) as tick:
            self.assertEqual(decision, wd.tick_on_terminal_event(storage, deps))
        tick.assert_called_once_with(storage, deps)

    def test_retry_budget_produces_one_tick_and_preserves_real_hold(self):
        from joulewise.terminal_wake import publish
        publish(self.root, "synthetic", "HAZARD_PACK", now=100)
        storage, deps = wd.Storage(self.root), mock.Mock()
        deps.wall_now.return_value = dt.datetime.fromtimestamp(100, dt.timezone.utc)
        deps.driver_probe.return_value = wd.CensusObservation(False, 0, "live driver", "")
        held = wd.Decision("HOLD_CENSUS", "driver still present")
        with mock.patch.object(wd, "tick", return_value=held) as tick:
            self.assertEqual(held, wd.tick_on_terminal_event(storage, deps))
        tick.assert_called_once_with(storage, deps)
        self.assertEqual(30, deps.sleep.call_count)
        self.assertEqual(31, deps.driver_probe.call_count)

    def test_no_courier_uses_documented_timer_fallback(self):
        with mock.patch.object(run_night, "_durable_record"), \
                mock.patch.object(run_night, "_write_courier_outcome"), \
                mock.patch.object(run_night, "_notify_terminal") as notify:
            self.assertEqual(run_night.EXIT_COURIER_FAILED, run_night._finish_reporting(
                self.root, self.root, mock.Mock(), 5, None))
        notify.assert_not_called()
        self.test_watchpaths_keeps_watchdog_fallback()

    def test_watchpaths_keeps_watchdog_fallback(self):
        template = Path("configs/launchd/com.joulewise.magistrate.plist.template").read_bytes()
        plist = plistlib.loads(template)
        self.assertEqual(300, plist["StartInterval"])
        self.assertEqual(["@@CUSTODY_ROOT@@/terminal-wake.json"], plist["WatchPaths"])
        self.assertNotIn("KeepAlive", plist)

    def test_night_render_binds_destination_to_probe_context(self):
        from joulewise import night_agent_install as installer
        from types import SimpleNamespace
        repo = Path(__file__).resolve().parents[1]
        calendar = {"Month": 9, "Day": 25, "Hour": 22, "Minute": 0}
        prepared = installer.Prepared(
            SimpleNamespace(custody_root=str(self.root), plan_id="test", receipt_class="DIAGNOSTIC_NO_PACK"),
            self.root / "night_plan.json", repo, "synthetic-python",
            (repo / "configs/launchd/com.joulewise.night.plist.template").read_text(),
            "/bin/true", "/usr/bin:/bin", {"night_calendar": calendar, "deadman_calendar": calendar}, lambda _: [])
        with mock.patch.dict(os.environ, {"MAGISTRATE_WATCHDOG_CUSTODY_ROOT": str(self.root)}):
            first = list(prepared.render(installer.LABELS))[0][1]
        self.assertEqual(str(self.root), plistlib.loads(first)["EnvironmentVariables"]["JOULEWISE_TERMINAL_WAKE_ROOT"])
        with mock.patch.dict(os.environ, {"MAGISTRATE_WATCHDOG_CUSTODY_ROOT": str(self.root / "different")}):
            self.assertNotEqual(first, list(prepared.render(installer.LABELS))[0][1])

    def test_event_does_not_release_an_open_chain(self):
        from tests.test_magistrate_watchdog import WatchdogTestCase
        from joulewise.terminal_wake import publish
        fixture = WatchdogTestCase()
        fixture.setUp()
        try:
            plan = fixture.make_plan(t0=fixture.base.timestamp() - 1)
            night = Path(plan.custody_root) / "night"
            night.mkdir()
            (night / "chain.started").write_text("{}")
            fixture.harness.storage.mkdir(fixture.harness.storage.root)
            publish(fixture.harness.storage.root, plan.plan_id, plan.receipt_class, now=fixture.base.timestamp())
            fixture.harness.deps.git_probe = mock.Mock(side_effect=AssertionError("network in active window"))
            with mock.patch.object(wd.os, "fork", side_effect=AssertionError("unsafe spawn")):
                decision = wd.tick_on_terminal_event(fixture.harness.storage, fixture.harness.deps)
            self.assertEqual("FENCED", decision.state)
            self.assertEqual([], wd.load_state(fixture.harness.storage)[wd.TERMINAL_RELEASE_STATE_KEY])
        finally:
            fixture.tearDown()
            fixture.doCleanups()


class TerminalWakeCensusBoundsTests(twd.WatchdogTestCase):
    write_hazard_plan = twd.TerminalWindowReleaseTests.write_hazard_plan
    write_terminal = twd.TerminalWindowReleaseTests.write_terminal

    def test_terminal_window_records_one_census_even_when_driver_persists(self):
        from joulewise.terminal_wake import publish
        plan = self.write_hazard_plan(t0=self.base.timestamp() - 9.5 * 3600)
        self.write_terminal(plan, ended=self.base.timestamp() - 5)
        self.harness.driver = wd.CensusObservation(False, 0, "live driver", "")
        self.harness.storage.mkdir(self.harness.storage.root)
        publish(self.harness.storage.root, plan.plan_id, plan.receipt_class, now=self.base.timestamp())
        with mock.patch.object(wd.os, "fork", side_effect=AssertionError("must remain held")):
            decision = wd.tick_on_terminal_event(self.harness.storage, self.harness.deps)
        self.assertEqual("HOLD_CENSUS", decision.state)
        state = wd.load_state(self.harness.storage)
        self.assertIn("hold_census", [item["kind"] for item in state["notice_pending"]])
        events = [json.loads(line) for line in
                  (self.harness.storage.root / "events.jsonl").read_text().splitlines()]
        self.assertEqual(1, sum(row["kind"] == "census" for row in events))
        self.assertEqual(1, self.harness.census_calls)


if __name__ == "__main__":
    unittest.main()
