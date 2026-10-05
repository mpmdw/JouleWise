from __future__ import annotations

import contextlib
import datetime as dt
import plistlib
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests.test_magistrate_watchdog import WatchdogTestCase


class TickSpanTests(WatchdogTestCase):
    def set_wall(self, epoch: float) -> None:
        self.harness.clock.wall = dt.datetime.fromtimestamp(epoch, tz=self.local_tz)

    def quiet_tick(self, *, dry_run: bool = False) -> wd.Decision:
        """Fail on every subprocess seam and every avoidable custody write."""
        targets = (
            (self.harness.deps, "git_probe"),
            (self.harness.deps, "census"),
            (self.harness.deps, "driver_probe"),
            (self.harness.deps, "spawn"),
            (self.harness.deps, "version_probe"),
            (self.harness.processes, "snapshot"),
            (self.harness.processes, "send_signal"),
            (self.harness.storage, "atomic_bytes"),
            (self.harness.storage, "append_jsonl"),
            (self.harness.storage, "unlink"),
            (wd.subprocess, "run"),
            (wd.subprocess, "Popen"),
            (wd.os, "fork"),
            (wd, "decide"),
        )
        with contextlib.ExitStack() as stack:
            guards = [stack.enter_context(mock.patch.object(
                owner, name, side_effect=AssertionError(f"active tick called {name}")
            )) for owner, name in targets]
            decision = wd.tick(self.harness.storage, self.harness.deps, dry_run=dry_run)
            for guard in guards:
                guard.assert_not_called()
        self.assertFalse(decision.launch)
        self.assertFalse(decision.adopt)
        return decision

    def test_active_span_is_quiet_at_start_window_and_inclusive_end(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        for epoch in (plan.t0_epoch_s - wd.PLAN_LEAD_S, plan.t0_epoch_s,
                      wd.plan_completion_epoch(plan)):
            for dry_run in (False, True):
                with self.subTest(epoch=epoch, dry_run=dry_run):
                    self.set_wall(epoch)
                    self.assertEqual("FENCED", self.quiet_tick(dry_run=dry_run).state)

    def test_active_span_does_not_reset_backoff_or_refresh_stop_cache(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp())
        state = wd.initial_state()
        state.update({"next_eligible_epoch_s": plan.t0_epoch_s + 3600,
                      "next_eligible_monotonic": 3600,
                      "remote_stop": {"state": "STOPPED", "detail": "cached stop",
                                      "observed_monotonic": 10}})
        path = self.harness.storage.root / "state.json"
        self.harness.storage.atomic_json(path, state)
        before = path.read_bytes()
        self.assertEqual("FENCED", self.quiet_tick().state)
        self.assertEqual(before, path.read_bytes())

    def test_active_span_with_owned_session_defers_adoption(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        lock = self.write_live_lock()
        self.assertEqual("FENCED", self.quiet_tick().state)
        self.assertEqual(lock, wd.read_lock(self.harness.storage))

    def test_active_span_with_malformed_sibling_holds_without_recovery(self) -> None:
        self.make_plan(t0=self.base.timestamp())
        path = self.temp / "torn" / "night_plan.json"
        path.parent.mkdir()
        path.write_text("{torn", encoding="utf-8")
        decision = self.quiet_tick()
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("night_plan_unreadable", decision.reason)

    def test_installed_only_span_is_quiet(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp())
        directory = wd.Path.home() / "Library" / "LaunchAgents"
        directory.mkdir(parents=True)
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            with self.subTest(label=label):
                plist = directory / f"{label}.plist"
                plist.write_bytes(plistlib.dumps({"ProgramArguments": [
                    "python", "run_night.py", "--plan",
                    str(Path(plan.custody_root) / "night_plan.json")]}))
                with mock.patch.object(self.harness.storage, "glob_plans", return_value=[]):
                    decision = self.quiet_tick()
                self.assertEqual("FENCED", decision.state)
                self.assertEqual(f"installed_plan:{plan.plan_id}", decision.reason)
                plist.unlink()

    def test_open_chain_keeps_tick_quiet_past_deadman(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "chain.started").write_text("{}", encoding="utf-8")
        self.set_wall(wd.deadman_epoch(plan) + wd.COURIER_LOCK_FRESH_S + 1)
        self.assertEqual("FENCED", self.quiet_tick().state)
        (night / "chain.exited").write_text("{}", encoding="utf-8")
        probe = mock.Mock(return_value=wd.StopObservation("CLEAR", "clear"))
        self.harness.deps.git_probe = probe
        self.assertEqual("LAUNCHING", wd.tick(
            self.harness.storage, self.harness.deps, dry_run=True).state)
        probe.assert_called_once_with()

    def test_unreadable_installed_fence_keeps_normal_unsafe_hold_path(self) -> None:
        probe = mock.Mock(side_effect=AssertionError("unsafe tick probed network"))
        self.harness.deps.git_probe = probe
        with mock.patch.object(wd, "installed_agent_fence", side_effect=ValueError("torn plist")):
            decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("torn plist", decision.reason)
        self.assertEqual("HOLD_UNSAFE", wd.load_state(self.harness.storage)["state"])
        self.assertTrue((self.harness.storage.root / "events.jsonl").exists())
        probe.assert_not_called()

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
        self.assertEqual("FENCED", self.quiet_tick().state)
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
        self.assertEqual("FENCED", self.quiet_tick().state)
        self.set_wall(end + 0.001)
        probe = mock.Mock(return_value=wd.StopObservation("CLEAR", "clear"))
        self.harness.deps.git_probe = probe
        self.assertEqual("LAUNCHING", wd.tick(
            self.harness.storage, self.harness.deps, dry_run=True).state)
        probe.assert_called_once_with()

    def test_no_plan_tick_still_probes_and_fails_closed(self) -> None:
        probe = mock.Mock(side_effect=RuntimeError("offline"))
        self.harness.deps.git_probe = probe
        decision = wd.tick(self.harness.storage, self.harness.deps)
        self.assertEqual("NETWORK_UNCERTAIN", decision.state)
        probe.assert_called_once_with()
