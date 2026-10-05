from __future__ import annotations

import datetime as dt
import json
import plistlib
import signal
import subprocess
import threading
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests import test_magistrate_watchdog as watchdog_tests
from tests.test_magistrate_watchdog import WatchdogTestCase


class TickSpanTests(WatchdogTestCase):
    def set_wall(self, epoch: float) -> None:
        self.harness.clock.mono += epoch - self.harness.clock.wall.timestamp()
        self.harness.clock.wall = dt.datetime.fromtimestamp(epoch, tz=self.local_tz)

    def network_free_tick(self, *, dry_run: bool = False) -> wd.Decision:
        # Assert call counts too: decide deliberately catches probe exceptions.
        with mock.patch.object(self.harness.deps, "git_probe",
                               side_effect=AssertionError("in-span network probe")) as probe, \
             mock.patch.object(wd, "remote_stop_probe",
                               side_effect=AssertionError("in-span HTTPS probe")) as remote:
            decision = wd.tick(self.harness.storage, self.harness.deps, dry_run=dry_run)
            probe.assert_not_called()
            remote.assert_not_called()
        return decision

    def installed_plan(self, plan: wd.NightPlan, label: str = "com.joulewise.night") -> Path:
        directory = wd.Path.home() / "Library" / "LaunchAgents"
        directory.mkdir(parents=True, exist_ok=True)
        plist = directory / f"{label}.plist"
        plist.write_bytes(plistlib.dumps({"ProgramArguments": [
            "python", "run_night.py", "--plan",
            str(Path(plan.custody_root) / "night_plan.json")]}))
        return plist

    def test_active_span_skips_probe_at_start_window_and_inclusive_end(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        for epoch in (plan.t0_epoch_s - wd.PLAN_LEAD_S, plan.t0_epoch_s,
                      wd.plan_completion_epoch(plan)):
            for dry_run in (False, True):
                with self.subTest(epoch=epoch, dry_run=dry_run):
                    self.set_wall(epoch)
                    self.assertEqual("FENCED", self.network_free_tick(dry_run=dry_run).state)
                    state = wd.load_state(self.harness.storage)
                    self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])
                    self.assertEqual([], state["notice_pending"])
        self.assertEqual(6, self.harness.census_calls)
        self.assertTrue((self.harness.storage.root / "events.jsonl").exists())

    def test_skipped_probe_replaces_stale_stop_or_network_uncertainty(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        for cached in ("STOPPED", "NETWORK_UNCERTAIN"):
            with self.subTest(cached=cached):
                state = wd.initial_state()
                state["remote_stop"] = {"state": cached, "detail": "old result",
                                        "observed_monotonic": 10}
                self.harness.storage.atomic_json(self.harness.storage.root / "state.json", state)
                self.assertEqual("FENCED", self.network_free_tick().state)
                state = wd.load_state(self.harness.storage)
                self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])
                self.assertEqual([], state["notice_pending"])
                self.assertFalse((self.harness.storage.root / "standdown.request").exists())

    def test_active_span_recovers_owned_session_and_enforces_standdown(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp() + wd.TERM_LEAD_S)
        lock = self.write_live_lock()
        self.harness.processes.rows = [wd.ProcessInfo(100, 1, "token-a", "session")]
        with mock.patch.object(wd.os, "fork", return_value=4321) as fork:
            decision = self.network_free_tick()
        self.assertEqual("STANDDOWN_TERM", decision.state)
        self.assertTrue(decision.adopt)
        self.assertFalse(decision.launch)
        fork.assert_called_once_with()
        self.assertEqual(lock, wd.read_lock(self.harness.storage))
        self.assertEqual(1, self.harness.census_calls)
        state = wd.load_state(self.harness.storage)
        supervisor = wd.adopt_session(self.harness.storage, self.harness.deps, state)
        self.assertIsNotNone(supervisor)
        with mock.patch.object(self.harness.deps, "git_probe",
                               side_effect=AssertionError("resident network probe")) as probe:
            self.assertTrue(supervisor.step())
            probe.assert_not_called()
        self.assertIn((100, signal.SIGTERM), self.harness.processes.signals)
        self.assertTrue((self.harness.storage.root / "standdown.request").exists())

    def test_in_span_tick_releases_zero_capture_refusal_for_immediate_retry(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp() - 60,
                              authored_epoch_s=self.base.timestamp() - 3600)
        watchdog_tests.FenceTests.write_terminal_refusal(self, plan)
        self.installed_plan(plan)
        self.assertTrue(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage))
        with mock.patch.object(wd.os, "fork", return_value=4321) as fork:
            decision = self.network_free_tick()
        self.assertEqual("LAUNCHING", decision.state)
        self.assertTrue(decision.launch)
        fork.assert_called_once_with()
        self.assertEqual(1, self.harness.census_calls)
        self.assertEqual(1, self.harness.driver_calls)
        state = wd.load_state(self.harness.storage)
        self.assertEqual(1, len(state["released_zero_capture_refusals"]))
        self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])
        self.assertEqual([], state["notice_pending"])
        self.assertFalse(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage, state))
        self.assertIsNone(wd.installed_agent_fence(self.base, self.harness.storage, state=state))
        self.assertLess(self.base.timestamp(), wd.plan_completion_epoch(plan))

    def test_skipped_result_in_resident_cache_does_not_hold_or_notice(self) -> None:
        plan = self.make_plan()  # Outside its span; exercise the cache consumer.
        supervisor = self.supervisor(plan)
        supervisor._remote_stop = wd.StopObservation("NOT_PROBED", "span tick skipped")
        supervisor._remote_probe_started_monotonic = self.harness.clock.mono
        with mock.patch.object(self.harness.deps, "git_probe",
                               side_effect=AssertionError("unexpected refresh")) as probe:
            self.assertTrue(supervisor.step())
            probe.assert_not_called()
        self.assertEqual("ACTIVE", supervisor.state["state"])
        self.assertEqual([], supervisor.state["notice_pending"])
        self.assertFalse((self.harness.storage.root / "standdown.request").exists())

    def test_local_stop_during_discovered_span_preserves_plan_precedence(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        self.harness.storage.root.mkdir(parents=True)
        (self.harness.storage.root / "STOP").write_text("stop\n", encoding="utf-8")
        self.assertEqual("FENCED", self.network_free_tick().state)
        self.assertEqual(1, self.harness.census_calls)

    def test_installed_only_span_skips_probe_but_local_stop_still_wins(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp())
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            with self.subTest(label=label):
                plist = self.installed_plan(plan, label)
                with mock.patch.object(self.harness.storage, "glob_plans", return_value=[]):
                    decision = self.network_free_tick()
                    self.assertEqual("FENCED", decision.state)
                    self.assertEqual(f"installed_plan:{plan.plan_id}", decision.reason)
                    (self.harness.storage.root / "STOP").write_text("stop\n", encoding="utf-8")
                    decision = self.network_free_tick()
                    self.assertEqual("STOPPED", decision.state)
                    self.assertEqual("local STOP file present", decision.reason)
                (self.harness.storage.root / "STOP").unlink()
                plist.unlink()
        self.assertEqual(0, self.harness.census_calls)  # Baseline installed-only path.
        self.assertEqual([], wd.load_state(self.harness.storage)["notice_pending"])

    def test_installed_only_resident_skips_refresh_at_normal_cadence(self) -> None:
        # Reviewer CONTRACT probe: discovery can miss the independently
        # installed plan while an existing resident continues polling.
        plan = self.make_plan(t0=self.base.timestamp())
        self.installed_plan(plan)
        supervisor = self.supervisor(plan)
        cached = wd.StopObservation("CLEAR", "pre-span clear")
        supervisor._remote_stop = cached
        supervisor._remote_probe_started_monotonic = self.harness.clock.mono
        supervisor._remote_stop_observed_monotonic = self.harness.clock.mono
        calls = []

        def transport(argv, **kwargs):
            self.assertIn("ls-remote", argv)
            calls.append(list(argv))
            return subprocess.CompletedProcess(
                argv, 0 if argv[-1] == wd.POSITIVE_CONTROL_REF else 2, "control", "")

        self.harness.deps.git_probe = wd.remote_stop_probe
        with mock.patch.object(self.harness.storage, "glob_plans", return_value=[]), \
             mock.patch.object(wd.subprocess, "run", side_effect=transport):
            state = wd.initial_state()
            self.assertEqual("FENCED", wd.decide(
                self.harness.storage, self.harness.deps, state).state)
            self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])
            self.assertEqual([], calls)
            self.set_wall(self.base.timestamp() + wd.REMOTE_STOP_PROBE_CADENCE_S)
            self.assertIsNotNone(wd.installed_agent_fence(
                self.harness.clock.wall, self.harness.storage, state=state))
            try:
                self.assertTrue(supervisor.step())
            finally:
                thread = supervisor._remote_probe_thread
                if thread is not None:
                    thread.join(5)
                    self.assertFalse(thread.is_alive())
            self.assertEqual([], calls)
            self.assertIsNone(thread, "suppression must prevent starting a refresh")
            self.assertIs(cached, supervisor._remote_stop)
            self.assertEqual("NOT_PROBED", supervisor.state["remote_stop"]["state"])

    def test_inflight_refresh_abandons_second_call_at_span_start(self) -> None:
        # Reviewer CONTRACT probe: hold the positive-control transport while
        # the resident crosses the inclusive boundary and requests stand-down.
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        self.set_wall(plan.t0_epoch_s - wd.PLAN_LEAD_S - 0.001)
        cached = supervisor._remote_stop
        cached_monotonic = supervisor._remote_stop_observed_monotonic
        entered = threading.Event()
        release = threading.Event()
        calls = []

        def transport(argv, **kwargs):
            calls.append((argv[-1], self.harness.clock.wall.timestamp()))
            if argv[-1] == wd.POSITIVE_CONTROL_REF:
                entered.set()
                self.assertTrue(release.wait(5))
                return subprocess.CompletedProcess(argv, 0, "control", "")
            return subprocess.CompletedProcess(argv, 2, "", "")

        self.harness.deps.git_probe = wd.remote_stop_probe
        with mock.patch.object(wd.subprocess, "run", side_effect=transport):
            try:
                self.assertTrue(supervisor.step())
                self.assertTrue(entered.wait(5))
                self.set_wall(plan.t0_epoch_s - wd.PLAN_LEAD_S)
                self.assertTrue(wd.plan_span_active(
                    plan, self.harness.clock.wall.timestamp(), self.harness.storage))
                self.assertTrue(supervisor.step())
                self.assertEqual("STANDDOWN_REQUESTED", supervisor.state["state"])
            finally:
                release.set()
                thread = supervisor._remote_probe_thread
                if thread is not None:
                    thread.join(5)
                    self.assertFalse(thread.is_alive())
            self.assertEqual([wd.POSITIVE_CONTROL_REF], [ref for ref, _ in calls])
            self.assertLess(calls[0][1], plan.t0_epoch_s - wd.PLAN_LEAD_S)
            self.assertIs(cached, supervisor._remote_stop)
            self.assertEqual(cached_monotonic, supervisor._remote_stop_observed_monotonic)
            self.assertEqual("NOT_PROBED", supervisor.state["remote_stop"]["state"])

    def test_active_span_still_records_nonempty_census_and_notice(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        self.harness.census = wd.CensusObservation(False, 0, "100 claude -p", "")
        self.assertEqual("HOLD_CENSUS", self.network_free_tick().state)
        state = wd.load_state(self.harness.storage)
        self.assertEqual(["hold_census"], [row["kind"] for row in state["notice_pending"]])
        self.assertEqual("NOT_PROBED", state["remote_stop"]["state"])

    def test_active_span_still_checks_clock_and_records_diagnostics(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        state = wd.initial_state()
        state["last_clock"] = {"epoch_s": self.base.timestamp() - 10,
                               "monotonic": self.harness.clock.mono - 100}
        self.harness.storage.atomic_json(self.harness.storage.root / "state.json", state)
        path = self.temp / "retired" / "night_plan.json"
        path.parent.mkdir()
        path.write_bytes(watchdog_tests.RETIRED_V1.read_bytes())
        self.assertEqual("CLOCK_UNCERTAIN", self.network_free_tick().state)
        events = [json.loads(line) for line in
                  (self.harness.storage.root / "events.jsonl").read_text().splitlines()]
        self.assertTrue(any(row["kind"] == "plan_retired_v1" for row in events))
        state = wd.load_state(self.harness.storage)
        self.assertEqual(["clock_uncertain"], [row["kind"] for row in state["notice_pending"]])

    def test_open_chain_skips_probe_past_deadman_until_exit(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "chain.started").write_text("{}", encoding="utf-8")
        self.set_wall(wd.deadman_epoch(plan) + wd.COURIER_LOCK_FRESH_S + 1)
        self.assertEqual("FENCED", self.network_free_tick().state)
        (night / "chain.exited").write_text("{}", encoding="utf-8")
        probe = mock.Mock(return_value=wd.StopObservation("CLEAR", "clear"))
        self.harness.deps.git_probe = probe
        self.assertEqual("LAUNCHING", wd.tick(
            self.harness.storage, self.harness.deps, dry_run=True).state)
        probe.assert_called_once_with()

    def test_unreadable_installed_fence_keeps_normal_unsafe_hold_path(self) -> None:
        with mock.patch.object(wd, "installed_agent_fence", side_effect=ValueError("torn plist")):
            decision = self.network_free_tick()
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("torn plist", decision.reason)
        self.assertEqual("HOLD_UNSAFE", wd.load_state(self.harness.storage)["state"])
        self.assertTrue((self.harness.storage.root / "events.jsonl").exists())

    def test_tick_before_span_still_probes(self) -> None:
        plan = self.make_plan()
        self.set_wall(plan.t0_epoch_s - wd.PLAN_LEAD_S - 0.001)
        probe = mock.Mock(return_value=wd.StopObservation("CLEAR", "clear"))
        self.harness.deps.git_probe = probe
        self.assertEqual("LAUNCHING", wd.tick(
            self.harness.storage, self.harness.deps, dry_run=True).state)
        probe.assert_called_once_with()

    def test_first_post_completion_tick_probes_and_observes_remote_stop(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        self.set_wall(wd.plan_completion_epoch(plan))
        self.assertEqual("FENCED", self.network_free_tick().state)
        self.set_wall(wd.plan_completion_epoch(plan) + 0.001)
        probe = mock.Mock(return_value=wd.StopObservation("STOPPED", "remote stop"))
        self.harness.deps.git_probe = probe
        decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("STOPPED", decision.state)
        self.assertEqual("remote stop", decision.reason)
        probe.assert_called_once_with()

    def test_first_post_deadman_tick_probes(self) -> None:
        plan = self.make_plan()
        end = wd.deadman_epoch(plan) + wd.COURIER_LOCK_FRESH_S
        self.set_wall(end)
        self.assertEqual("FENCED", self.network_free_tick().state)
        self.set_wall(end + 0.001)
        probe = mock.Mock(return_value=wd.StopObservation("CLEAR", "clear"))
        self.harness.deps.git_probe = probe
        self.assertEqual("LAUNCHING", wd.tick(
            self.harness.storage, self.harness.deps, dry_run=True).state)
        probe.assert_called_once_with()

    def test_first_post_installed_only_span_tick_probes(self) -> None:
        plan = self.make_plan()
        self.installed_plan(plan)
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        with mock.patch.object(self.harness.storage, "glob_plans", return_value=[]):
            self.set_wall(wd.plan_completion_epoch(plan))
            self.assertEqual("FENCED", self.network_free_tick().state)
            self.set_wall(wd.plan_completion_epoch(plan) + 0.001)
            probe = mock.Mock(return_value=wd.StopObservation("STOPPED", "remote stop"))
            self.harness.deps.git_probe = probe
            self.assertEqual("STOPPED", wd.tick(self.harness.storage, self.harness.deps).state)
            probe.assert_called_once_with()

    def test_no_plan_tick_still_probes_and_fails_closed(self) -> None:
        probe = mock.Mock(side_effect=RuntimeError("offline"))
        self.harness.deps.git_probe = probe
        decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("NETWORK_UNCERTAIN", decision.state)
        probe.assert_called_once_with()
