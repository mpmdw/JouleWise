"""Installed R1-shaped plans use discovery's parser and release predicates."""
from __future__ import annotations

import datetime as dt
import json
import plistlib
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from scripts import run_night
from tests.fixtures.b5_plan import fake_window
from tests import test_magistrate_watchdog as watchdog_tests


class InstalledV5Tests(watchdog_tests.WatchdogTestCase):
    def write_plan(self, **changes):
        custody = self.temp / "sessions" / "synthetic-r1" / "custody"
        (custody / "night").mkdir(parents=True, exist_ok=True)
        value = fake_window.hazard_plan_mapping(
            custody, plan_id="synthetic-r1", t0_epoch_s=self.base.timestamp() - 60,
            window_max_s=29 * 60 * 60,
            authored_epoch_s=self.base.timestamp() - 3600, custody_root=custody,
            measurement_root=self.temp / "measurement", pack_root=self.temp / "pack")
        value.update(ac_powermode=0, **changes)
        path = custody / "night_plan.json"
        path.write_text(json.dumps(value))
        directory = wd.Path.home() / "Library" / "LaunchAgents"
        directory.mkdir(parents=True, exist_ok=True)
        for label, command in (("com.joulewise.night", "run"),
                               ("com.joulewise.night.deadman", "dead-man")):
            (directory / (label + ".plist")).write_bytes(plistlib.dumps({
                "ProgramArguments": ["python", "run_night.py", command, "--plan", str(path)]}))
        return path, value

    def test_both_installed_plists_and_discovery_parse_the_same_v5_plan(self):
        path, value = self.write_plan()
        self.assertEqual([], list(self.harness.storage.glob_plans()))
        installed = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
        self.assertEqual((), installed.errors)
        self.assertEqual(1, len(installed.plans))
        plan = installed.plans[0]
        self.assertEqual(0, plan.ac_powermode)
        self.assertEqual(value["hazard_window"], plan.hazard_window)
        self.assertEqual(plan, run_night._load_plan(path))
        with mock.patch.object(self.harness.storage, "glob_plans", return_value=[path]):
            scanned = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
        self.assertEqual(installed, scanned)
        self.assertEqual("installed_plan:synthetic-r1",
                         wd.installed_agent_fence(self.base, self.harness.storage))
        self.assertEqual("FENCED", wd.decide(
            self.harness.storage, self.harness.deps, wd.initial_state()).state)

    def test_terminal_release_keeps_all_existing_evidence_and_process_gates(self):
        self.write_plan()
        snapshot = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
        self.assertEqual((), snapshot.errors)
        plan = snapshot.plans[0]
        state = wd.initial_state()
        night = watchdog_tests.TerminalWindowReleaseTests.write_terminal(
            self, plan, ended=self.base.timestamp() - 1)
        for name in ("courier.sent", "chain.exited", "result.json"):
            path = night / name
            saved = path.read_bytes()
            path.unlink()
            self.assertFalse(wd.decide(self.harness.storage, self.harness.deps, state).launch)
            self.assertEqual([], state[wd.TERMINAL_RELEASE_STATE_KEY])
            path.write_bytes(saved)
        for seam in ("census", "driver", "processes"):
            with self.subTest(seam=seam):
                self.harness.census = wd.CensusObservation(seam != "census", 0, "", "")
                self.harness.driver = wd.CensusObservation(seam != "driver", 0, "", "")
                self.harness.processes.rows = ([wd.ProcessInfo(
                    4242, 1, "start", f"zsh {plan.custody_root}/chain.zsh")]
                    if seam == "processes" else [])
                self.assertFalse(wd.decide(self.harness.storage, self.harness.deps, state).launch)
                self.assertEqual([], state[wd.TERMINAL_RELEASE_STATE_KEY])
        self.harness.census = self.harness.driver = wd.CensusObservation(True, 1, "", "")
        self.harness.processes.rows = []
        self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, state).launch)
        self.assertEqual(1, len(state[wd.TERMINAL_RELEASE_STATE_KEY]))
        self.assertIsNone(wd.installed_agent_fence(self.base, self.harness.storage, state=state))
        self.assertFalse(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage, state))
        (night / "chain.exited").unlink()
        self.assertTrue(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage, state))

    def test_unknown_keys_schemas_and_future_authorship_still_hold(self):
        for changes in ({"really_unknown": 1}, {"schema": "joulewise.night_plan.v999"},
                        {"authored_epoch_s": self.base.timestamp() + 1}):
            with self.subTest(changes=changes):
                self.write_plan(**changes)
                snapshot = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
                self.assertEqual((), snapshot.plans)
                self.assertEqual(2, len(snapshot.errors))
                self.assertTrue(all("installed_agent_fence" in error for error in snapshot.errors))
                self.assertEqual("HOLD_UNSAFE", wd.decide(
                    self.harness.storage, self.harness.deps, wd.initial_state()).state)

    def test_installed_v5_uses_discovery_completion_and_deadman_tail(self):
        self.write_plan()
        snapshot = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
        self.assertEqual((), snapshot.errors)
        plan = snapshot.plans[0]
        for epoch, active in ((plan.t0_epoch_s - wd.PLAN_LEAD_S - 1, False),
                              (plan.t0_epoch_s - wd.PLAN_LEAD_S, True),
                              (wd.deadman_epoch(plan) + wd.COURIER_LOCK_FRESH_S, True),
                              (wd.deadman_epoch(plan) + wd.COURIER_LOCK_FRESH_S + 1, False)):
            now = dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc)
            with self.subTest(epoch=epoch):
                self.assertEqual(active, wd.installed_agent_fence(now, self.harness.storage) is not None)
        night = Path(plan.custody_root) / "night"
        (night / "courier.sent").touch()
        for epoch, active in ((wd.plan_completion_epoch(plan), True),
                              (wd.plan_completion_epoch(plan) + 1, False)):
            self.assertEqual(active, wd.installed_agent_fence(
                dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc), self.harness.storage) is not None)
