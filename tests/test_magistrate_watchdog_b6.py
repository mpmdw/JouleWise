"""Installed block-six plans must use the same watchdog lifecycle as scanned plans."""
from __future__ import annotations

import datetime as dt
import json
import plistlib
import signal
from pathlib import Path
from unittest import mock

from scripts import magistrate_watchdog as wd
from tests.fixtures.b5_plan import fake_window
from tests import test_magistrate_watchdog as watchdog_tests
from tests.test_magistrate_watchdog import WatchdogTestCase


class InstalledBlockSixTests(WatchdogTestCase):
    def set_wall(self, epoch: float) -> None:
        self.harness.clock.mono += epoch - self.harness.clock.wall.timestamp()
        self.harness.clock.wall = dt.datetime.fromtimestamp(epoch, tz=self.local_tz)

    def block_six_plan(self, name: str = "b6-machine-test", *,
                       plan_id: str | None = None) -> wd.NightPlan:
        # The lane's SessionPaths.plan is sessions/<id>/custody/night_plan.json.
        # Its writer uses the block-five HAZARD_PACK shape with these extensions.
        root = self.temp / "night-b6" / "sessions" / name
        custody = root / "custody"
        (custody / "night").mkdir(parents=True)
        value = fake_window.hazard_plan_mapping(
            root, plan_id=plan_id or name, t0_epoch_s=self.base.timestamp() + 600,
            authored_epoch_s=self.base.timestamp() - 60, custody_root=custody,
            measurement_root=root / "measurement")
        value["hazard_window"]["bindings"].update({
            "capture_screen": {"alignment_reference_s": "0.036462861644980",
                               "bracket_screen_s": "0.014531", "operative_bound_stop_s": "0.092"},
            "spare_retries": False,
        })
        (custody / "night_plan.json").write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual([], list(self.harness.storage.glob_plans()))
        return wd.NightPlan.from_mapping(value)

    def install(self, plan: wd.NightPlan, label: str = "com.joulewise.night", *,
                path: Path | None = None) -> Path:
        directory = wd.Path.home() / "Library" / "LaunchAgents"
        directory.mkdir(parents=True, exist_ok=True)
        plist = directory / f"{label}.plist"
        plist.write_bytes(plistlib.dumps({"ProgramArguments": [
            "python", "run_night.py", "run", "--plan",
            str(path or Path(plan.custody_root) / "night_plan.json")]}))
        return plist

    def checkout_rows(self, plan: wd.NightPlan) -> list[list[str | None]]:
        return [["__canonical_repo__", str(wd.CANONICAL_REPO), None],
                [plan.plan_id, str(Path(plan.measurement_root).resolve()), plan.measurement_head]]

    def test_decide_owned_installed_plan_phases_and_completion(self) -> None:
        plan = self.block_six_plan()
        self.install(plan)
        supervisor = self.supervisor(plan)
        state = supervisor.state
        for epoch, expected in (
            (plan.t0_epoch_s - 600, "ACTIVE"),
            (plan.t0_epoch_s - 170, "STANDDOWN_REQUEST"),
            (plan.t0_epoch_s - wd.TERM_LEAD_S, "STANDDOWN_TERM"),
            (plan.t0_epoch_s - 70, "STANDDOWN_TERM"),
            (plan.t0_epoch_s + 60, "STANDDOWN_KILL"),
        ):
            with self.subTest(epoch=epoch):
                self.set_wall(epoch)
                decision = wd.decide(self.harness.storage, self.harness.deps, state)
                self.assertEqual(expected, decision.state)
                self.assertTrue(decision.adopt)
                self.assertFalse(decision.launch)
                self.assertEqual(self.checkout_rows(plan), state["fenced_checkouts"])
        (Path(plan.custody_root) / "night" / "courier.sent").write_text("sent\n")
        self.set_wall(wd.plan_completion_epoch(plan) + 1)
        self.assertEqual("ACTIVE", wd.decide(self.harness.storage, self.harness.deps, state).state)
        self.assertEqual(wd.fenced_checkout_rows([]), state["fenced_checkouts"])
        self.assertIsNone(wd.installed_agent_fence(self.harness.clock.wall, self.harness.storage, state=state))

    def test_resident_requests_terms_and_kills_installed_plan_at_existing_leads(self) -> None:
        plan = self.block_six_plan()
        self.install(plan)
        supervisor = self.supervisor(plan)
        self.harness.processes.rows.append(wd.ProcessInfo(101, 100, "child-token", "codex child"))
        request = self.harness.storage.root / "standdown.request"
        with mock.patch.object(supervisor, "_cached_remote_stop", return_value=wd.StopObservation("CLEAR", "clear")):
            self.assertTrue(supervisor.step())  # t0-600: owned session may run.
            self.assertFalse(request.exists())
            for lead in (wd.REQUEST_LEAD_S, 170):
                self.set_wall(plan.t0_epoch_s - lead)
                self.assertTrue(supervisor.step())
                self.assertTrue(request.exists())
                self.assertEqual("STANDDOWN_REQUESTED", supervisor.state["state"])
                self.assertEqual([], self.harness.processes.signals)
            value = json.loads(request.read_text())
            self.assertEqual(plan.plan_id, value["plan_id"])
            self.assertEqual(plan.t0_epoch_s - wd.REQUEST_LEAD_S, value["requested_epoch_s"])
            self.assertEqual(plan.t0_epoch_s - wd.TERM_LEAD_S, value["term_epoch_s"])
            self.assertEqual(plan.t0_epoch_s - wd.KILL_LEAD_S, value["kill_epoch_s"])
            self.set_wall(plan.t0_epoch_s - wd.TERM_LEAD_S)
            self.assertTrue(supervisor.step())
            self.assertEqual("STANDDOWN_TERM", supervisor.state["state"])
            self.assertEqual({(100, signal.SIGTERM), (101, signal.SIGTERM)}, set(self.harness.processes.signals))
            self.assertEqual(self.checkout_rows(plan), supervisor.state["fenced_checkouts"])
            self.set_wall(plan.t0_epoch_s - 70)
            self.assertTrue(supervisor.step())
            self.assertEqual("STANDDOWN_TERM", supervisor.state["state"])
            self.assertFalse(any(sig == signal.SIGKILL for _, sig in self.harness.processes.signals))
            self.set_wall(plan.t0_epoch_s - wd.KILL_LEAD_S)
            self.assertFalse(supervisor.step())
        self.assertTrue({(100, signal.SIGKILL), (101, signal.SIGKILL)} <= set(self.harness.processes.signals))
        self.assertEqual([], self.harness.processes.rows)
        self.assertFalse(request.exists())
        self.assertIsNone(wd.read_lock(self.harness.storage))
        for epoch in (plan.t0_epoch_s + 60, wd.plan_completion_epoch(plan)):
            self.set_wall(epoch)
            decision = wd.decide(self.harness.storage, self.harness.deps, supervisor.state)
            self.assertEqual("FENCED", decision.state)
            self.assertFalse(decision.launch)
        (Path(plan.custody_root) / "night" / "courier.sent").write_text("sent\n")
        self.set_wall(wd.plan_completion_epoch(plan) + 1)
        self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, supervisor.state).launch)
        self.assertEqual(wd.fenced_checkout_rows([]), supervisor.state["fenced_checkouts"])

    def test_resident_first_sees_installed_plan_in_window_and_after_completion(self) -> None:
        plan = self.block_six_plan()
        self.install(plan)
        self.set_wall(plan.t0_epoch_s + 60)
        supervisor = self.supervisor(plan)
        with mock.patch.object(supervisor, "_cached_remote_stop", return_value=wd.StopObservation("CLEAR", "clear")):
            self.assertFalse(supervisor.step())
        self.assertIn((100, signal.SIGKILL), self.harness.processes.signals)
        (Path(plan.custody_root) / "night" / "courier.sent").write_text("sent\n")
        self.set_wall(wd.plan_completion_epoch(plan) + 1)
        supervisor = self.supervisor(plan)
        with mock.patch.object(supervisor, "_cached_remote_stop", return_value=wd.StopObservation("CLEAR", "clear")):
            self.assertTrue(supervisor.step())
        self.assertEqual("ACTIVE", supervisor.state["state"])
        self.assertEqual(wd.fenced_checkout_rows([]), supervisor.state["fenced_checkouts"])
        self.assertFalse((self.harness.storage.root / "standdown.request").exists())

    def test_plan_deduplicates_across_scan_night_and_deadman_resolved_paths(self) -> None:
        plan = self.block_six_plan()
        self.install(plan)
        scanned = self.temp / "scanned-alias" / "night_plan.json"
        scanned.parent.mkdir()
        scanned.symlink_to(Path(plan.custody_root) / "night_plan.json")
        self.install(plan, "com.joulewise.night.deadman", path=scanned)
        self.assertEqual("installed_plan:" + plan.plan_id,
                         wd.installed_agent_fence(dt.datetime.fromtimestamp(plan.t0_epoch_s), self.harness.storage))
        snapshot = wd.load_plans(self.harness.storage, now_epoch_s=self.base.timestamp())
        self.assertEqual((), snapshot.errors)
        self.assertEqual([plan], list(snapshot.plans))
        state = wd.initial_state()
        self.assertTrue(wd.decide(self.harness.storage, self.harness.deps, state).launch)
        self.assertEqual(self.checkout_rows(plan), state["fenced_checkouts"])

    def test_installed_conflicts_include_same_id_at_distinct_paths_and_scanned_plans(self) -> None:
        first = self.block_six_plan("first", plan_id="same-id")
        second = self.block_six_plan("second", plan_id="same-id")
        self.install(first)
        deadman = self.install(second, "com.joulewise.night.deadman")
        for scanned in (False, True):
            with self.subTest(scanned=scanned):
                if scanned:
                    deadman.unlink()
                    alias = self.temp / "scanned" / "night_plan.json"
                    alias.parent.mkdir()
                    alias.symlink_to(Path(second.custody_root) / "night_plan.json")
                state = wd.initial_state()
                decision = wd.decide(self.harness.storage, self.harness.deps, state)
                self.assertEqual("HOLD_UNSAFE", decision.state)
                self.assertIn("plan_conflict:", decision.reason)
                self.assertEqual(3, len(state["fenced_checkouts"]))
                supervisor = self.supervisor(first)
                self.assertTrue(supervisor.step())
                self.assertEqual("HOLD_UNSAFE", supervisor.state["state"])
                self.assertIn("plan_conflict:", supervisor.state["resident_hold_drain"]["reason"])
                self.assertTrue((self.harness.storage.root / "standdown.request").exists())

    def test_installed_terminal_release_is_census_backed_and_latched(self) -> None:
        plan = self.block_six_plan()
        self.install(plan)
        self.install(plan, "com.joulewise.night.deadman")
        self.set_wall(plan.t0_epoch_s + 60)
        watchdog_tests.TerminalWindowReleaseTests.write_terminal(self, plan, ended=plan.t0_epoch_s + 30)
        state = wd.initial_state()
        self.harness.census = wd.CensusObservation(False, 0, "100 claude -p", "")
        self.assertEqual("HOLD_CENSUS", wd.decide(self.harness.storage, self.harness.deps, state).state)
        self.assertEqual([], state[wd.TERMINAL_RELEASE_STATE_KEY])
        self.harness.census = wd.CensusObservation(True, 1, "", "")
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertTrue(decision.launch)
        self.assertEqual(1, len(state[wd.TERMINAL_RELEASE_STATE_KEY]))
        self.assertEqual(wd.fenced_checkout_rows([]), state["fenced_checkouts"])
        self.assertIsNone(wd.installed_agent_fence(self.harness.clock.wall, self.harness.storage, state=state))
        self.harness.storage.atomic_json(self.harness.storage.root / "state.json", state)
        supervisor = self.supervisor(plan)
        supervisor.state.update(state)
        with mock.patch.object(supervisor, "_cached_remote_stop", return_value=wd.StopObservation("CLEAR", "clear")):
            self.assertTrue(supervisor.step())
        self.assertEqual("ACTIVE", supervisor.state["state"])
        self.assertFalse((self.harness.storage.root / "standdown.request").exists())
        events = [json.loads(line) for line in (self.harness.storage.root / "events.jsonl").read_text().splitlines()]
        self.assertEqual(1, sum(event["kind"] == "terminal_release" for event in events))

    def test_unreadable_installed_plist_drains_resident_before_any_span(self) -> None:
        plan = self.block_six_plan()
        self.install(plan).write_bytes(b"unreadable plist")
        self.assertEqual("HOLD_UNSAFE", wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)
        supervisor = self.supervisor(plan)
        self.assertTrue(supervisor.step())
        self.assertEqual("HOLD_UNSAFE", supervisor.state["state"])
        self.assertIn("unreadable installed agent", supervisor.state["resident_hold_drain"]["reason"])
        self.assertTrue((self.harness.storage.root / "standdown.request").exists())

    def test_installed_plist_content_faults_hold_and_drain(self) -> None:
        # Contents whose parse raises outside the plist/JSON error classes (review r2 MINOR-1).
        deep = b"<array>" * 5000 + b"</array>" * 5000
        bodies = {
            "bad_date": b'<?xml version="1.0"?><plist version="1.0"><dict><key>d</key>'
                        b'<date>not-a-date</date></dict></plist>',
            "deep": b'<?xml version="1.0"?><plist version="1.0">' + deep + b"</plist>",
        }
        plan = self.block_six_plan()
        for name, body in bodies.items():
            with self.subTest(body=name):
                self.install(plan).write_bytes(body)
                self.assertEqual("HOLD_UNSAFE",
                                 wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state)
                supervisor = self.supervisor(plan)
                self.assertTrue(supervisor.step())
                self.assertEqual("HOLD_UNSAFE", supervisor.state["state"])
                self.assertIn("unreadable installed agent", supervisor.state["resident_hold_drain"]["reason"])
                self.assertTrue((self.harness.storage.root / "standdown.request").exists())
                (self.harness.storage.root / "standdown.request").unlink()

    def test_readable_installed_sibling_keeps_deadlines_when_other_plist_is_torn(self) -> None:
        plan = self.block_six_plan()
        for torn_label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            with self.subTest(torn_label=torn_label):
                self.set_wall(plan.t0_epoch_s - wd.TERM_LEAD_S)
                self.install(plan)
                self.install(plan, "com.joulewise.night.deadman")
                self.install(plan, torn_label).write_bytes(b"torn plist")
                supervisor = self.supervisor(plan)
                self.assertTrue(supervisor.step())
                self.assertEqual("HOLD_UNSAFE", supervisor.state["state"])
                self.assertEqual(self.checkout_rows(plan), supervisor.state["fenced_checkouts"])
                request = json.loads((self.harness.storage.root / "standdown.request").read_text())
                self.assertEqual(plan.plan_id, request["plan_id"])
                self.assertIn((100, signal.SIGTERM), self.harness.processes.signals)
                self.set_wall(plan.t0_epoch_s - wd.KILL_LEAD_S)
                self.assertFalse(supervisor.step())
                self.assertIn((100, signal.SIGKILL), self.harness.processes.signals)
