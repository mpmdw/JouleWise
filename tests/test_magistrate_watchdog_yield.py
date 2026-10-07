"""P3-WD: the watchdog's in-window yield alerts and its release on P2-DRV's final records.

PLAN2 section 2.2 C: the HAZARD_PACK driver runs no subprocess in the window to
report a ZERO or LOW stage; it writes ``night/yield_alert-<ordinal>.json`` and
the watchdog's own tick queues each alert once into ``notice_pending`` (P2-DRV
review F5). The end-to-end tests run the real driver (``tests/test_b5_driver``
harness) and hand its custody directory to the real watchdog ``decide``.

The release checks (P2-WD X1) run on the driver's own terminal records: a
chain stop (verdict CHAIN_STOPPED, yield EMPTY) and an empty collected window
(verdict GO, yield EMPTY, exit 5).
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise.b5 import driver as b5_driver
from scripts import magistrate_watchdog as wd
from tests import test_magistrate_watchdog as base
from tests.test_b5_driver import Harness as DriverHarness


RELEASED_TERMINAL = "released_terminal_windows"


def yield_notices(state: dict) -> list[dict]:
    return [item for item in state.get("notice_pending", []) if item.get("kind") == "yield_alert"]


def zero_stage_alert(night: Path, plan_id: str, *, stage_id: str = "alpha-science-absolute",
                     ordinal: int = 7, planned: int = 3, min_valid: int = 3) -> Path:
    """Have the driver's own YieldTripwire write one ZERO alert into ``night``."""

    runs = night.parent / "runs-yield"
    runs.mkdir(exist_ok=True)
    window = mock.Mock()
    window.plan.plan_id = plan_id
    rows = [{"stage_id": stage_id, "ordinal": ordinal, "role": "science", "runs_root": str(runs),
             "run_ids": [f"m{index}" for index in range(planned)], "planned": planned,
             "min_valid": min_valid, "count_in_window": True}]
    tripwire = b5_driver.YieldTripwire(window, night, rows, wall=time.time)
    with (night / "chain-stages.jsonl").open("a") as handle:
        handle.write(json.dumps({"stage_id": stage_id, "kind": "campaign_collection", "rc": 1,
                                 "started_epoch_s": time.time(), "ended_epoch_s": time.time()}) + "\n")
    tripwire.poll()
    alerts = sorted(night.glob("yield_alert-*.json"))
    assert len(alerts) == 1, alerts
    return alerts[0]


class YieldAlertConstantsTests(unittest.TestCase):
    def test_the_watchdog_reads_the_driver_file_name_and_schema(self) -> None:
        name = b5_driver.YIELD_ALERT.format(ordinal=12)
        import fnmatch
        self.assertTrue(fnmatch.fnmatchcase(name, wd.YIELD_ALERT_GLOB))
        self.assertEqual(b5_driver.YIELD_ALERT_SCHEMA, wd.YIELD_ALERT_SCHEMA)


class InWindowYieldAlertTests(base.WatchdogTestCase):
    """The alert is queued while the chain is still open and the span fenced."""

    write_hazard_plan = base.TerminalWindowReleaseTests.write_hazard_plan
    decide = base.TerminalWindowReleaseTests.decide
    events = base.TerminalWindowReleaseTests.events

    def open_window(self) -> tuple[wd.NightPlan, Path]:
        plan = self.write_hazard_plan(t0=self.base.timestamp() - 3600)
        night = Path(plan.custody_root) / "night"
        (night / "chain.started").write_text('{"pgid": 4242}', encoding="utf-8")
        return plan, night

    def test_a_driver_alert_in_an_open_window_is_queued_once(self) -> None:
        plan, night = self.open_window()
        alert = zero_stage_alert(night, plan.plan_id)
        decision, state = self.decide()
        self.assertEqual("FENCED", decision.state)
        self.assertTrue(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage))
        notices = yield_notices(state)
        self.assertEqual(1, len(notices))
        notice = notices[0]
        self.assertEqual(plan.plan_id, notice["plan_id"])
        self.assertEqual(str(alert), notice["path"])
        self.assertEqual(("yield.stage_zero", "ZERO", 3, 0, 0, 3),
                         tuple(notice["alert"][key] for key in
                               ("code", "status", "planned", "present", "succeeded", "min_valid")))
        self.assertIn("alpha-science-absolute", notice["reason"])
        self.assertIn("0 of 3 planned members", notice["reason"])
        self.assertEqual(1, len(self.events("yield_alert_queued")))
        # Later ticks, and a magistrate acknowledgement, never queue it again.
        _decision, state = self.decide()
        self.assertEqual(1, len(yield_notices(state)))
        state["notice_pending"] = []
        self.harness.storage.atomic_json(self.harness.storage.root / "state.json", state)
        _decision, state = self.decide()
        self.assertEqual([], yield_notices(state))
        self.assertEqual(1, len(self.events("yield_alert_queued")))

    def test_a_second_alert_is_queued_on_its_own(self) -> None:
        plan, night = self.open_window()
        zero_stage_alert(night, plan.plan_id, stage_id="s1", ordinal=1)
        _decision, state = self.decide()
        (night / "yield_alert-2.json").write_text(json.dumps({
            "schema": wd.YIELD_ALERT_SCHEMA, "plan_id": plan.plan_id, "code": "yield.stage_low",
            "stage_id": "s2", "ordinal": 2, "role": "science", "planned": 20, "present": 20,
            "succeeded": 15, "min_valid": 16, "status": "LOW", "rc": 0}), encoding="utf-8")
        _decision, state = self.decide()
        self.assertEqual(["s1", "s2"], [item["alert"]["stage_id"] for item in yield_notices(state)])

    def test_a_partly_written_alert_waits_and_is_queued_once_whole(self) -> None:
        plan, night = self.open_window()
        path = night / "yield_alert-3.json"
        path.write_text('{"schema": "joulewise.b5_yield', encoding="utf-8")
        _decision, state = self.decide()
        self.assertEqual([], yield_notices(state))
        path.write_text(json.dumps({
            "schema": wd.YIELD_ALERT_SCHEMA, "plan_id": plan.plan_id, "code": "yield.stage_zero",
            "stage_id": "s3", "ordinal": 3, "role": "corpus", "planned": 12, "present": 0,
            "succeeded": 0, "min_valid": 10, "status": "ZERO", "rc": 1}), encoding="utf-8")
        _decision, state = self.decide()
        self.assertEqual(["s3"], [item["alert"]["stage_id"] for item in yield_notices(state)])

    def test_an_unreadable_alert_after_the_result_is_queued_as_unrecognized(self) -> None:
        plan, night = self.open_window()
        (night / "yield_alert-4.json").write_text("{", encoding="utf-8")
        (night / "result.json").write_text("{}", encoding="utf-8")
        _decision, state = self.decide()
        notices = yield_notices(state)
        self.assertEqual(1, len(notices))
        self.assertIsNone(notices[0]["alert"])
        self.assertIn("unrecognized yield alert", notices[0]["reason"])

    def test_reading_alerts_runs_no_subprocess_and_never_changes_the_decision(self) -> None:
        plan, night = self.open_window()
        zero_stage_alert(night, plan.plan_id)
        state = wd.load_state(self.harness.storage)
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess")), \
                mock.patch.object(subprocess, "run", side_effect=AssertionError("subprocess")):
            queued = wd.queue_yield_alerts([plan], self.harness.storage, state, self.base)
        self.assertEqual(1, len(queued))
        census_before = self.harness.census_calls
        with mock.patch.object(wd, "queue_yield_alerts", side_effect=RuntimeError("boom")):
            decision, _state = self.decide()
        self.assertEqual("FENCED", decision.state)
        self.assertEqual(census_before + 1, self.harness.census_calls)

    def test_legacy_plans_are_never_read_and_their_state_gains_no_key(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp() - 60)
        night = Path(plan.custody_root) / "night"
        night.mkdir(parents=True, exist_ok=True)
        (night / "yield_alert-1.json").write_text(json.dumps({
            "schema": wd.YIELD_ALERT_SCHEMA, "plan_id": plan.plan_id}), encoding="utf-8")
        _decision, state = self.decide()
        self.assertEqual([], yield_notices(state))
        self.assertNotIn(wd.YIELD_ALERT_STATE_KEY, state)

    def test_alerts_outside_the_plan_span_and_tail_are_not_read(self) -> None:
        plan = self.write_hazard_plan(t0=self.base.timestamp() - 40 * 86400)
        night = Path(plan.custody_root) / "night"
        zero_stage_alert(night, plan.plan_id)
        _decision, state = self.decide()
        self.assertEqual([], yield_notices(state))


class DriverRecordsToWatchdogTests(unittest.TestCase):
    """The real driver's custody directory read by the real watchdog."""

    def watchdog(self, driver: DriverHarness) -> base.Harness:
        # The watchdog finds plans as siblings of its own custody root.
        wall = dt.datetime.fromtimestamp(time.time() + 1).astimezone()
        return base.Harness(driver.root / "magistrate", wall)

    def decide(self, watchdog: base.Harness) -> tuple[wd.Decision, dict]:
        state = wd.load_state(watchdog.storage)
        decision = wd.decide(watchdog.storage, watchdog.deps, state)
        watchdog.storage.atomic_json(watchdog.storage.root / "state.json", state)
        return decision, state

    def deliver(self, driver: DriverHarness) -> None:
        # run_courier is mocked in the driver harness; the courier writes this.
        (driver.night / "courier.sent").write_text("sent\n", encoding="utf-8")

    def assert_released(self, driver: DriverHarness, watchdog: base.Harness, kind: str) -> dict:
        plan = wd.load_plans(watchdog.storage).plans[0]
        now = watchdog.clock.wall.timestamp()
        self.assertTrue(wd.plan_span_active(plan, now, watchdog.storage))
        decision, state = self.decide(watchdog)
        self.assertEqual("LAUNCHING", decision.state)
        self.assertEqual(1, len(state[RELEASED_TERMINAL]))
        self.assertFalse(wd.plan_span_active(plan, now, watchdog.storage))
        self.assertFalse(wd.plan_is_armed(plan, now, watchdog.storage))
        events = [json.loads(line) for line in
                  (watchdog.storage.root / "events.jsonl").read_text().splitlines()]
        self.assertEqual([kind], [row["release_kind"] for row in events if row["kind"] == "terminal_release"])
        return state

    def test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery(self) -> None:
        driver = DriverHarness(self, "alpha", g10=False)
        ids = [row["stage_id"] for row in b5_driver.yield_plan(driver.plan)["stages"]]
        journal = "".join(
            f"print -r -- '{{\"stage_id\":\"{stage}\",\"kind\":\"campaign_collection\",\"rc\":1,"
            f"\"started_epoch_s\":0,\"ended_epoch_s\":0}}' >> \"$NIGHT_DIR/chain-stages.jsonl\"\n"
            for stage in ids)
        driver.replace_chain("#!/bin/zsh -f\n" + journal + "/bin/sleep 2\nexit 0\n", keep_yield_plan=True)
        self.assertEqual(driver.driver.EXIT_CHAIN_FAILED, driver.run())
        result = driver.result()
        self.assertEqual(("GO", "EMPTY"), (result["verdict"], driver.hazard()["yield"]["yield_status"]))
        alerts = sorted(driver.night.glob("yield_alert-*.json"))
        self.assertEqual(10, len(alerts))
        watchdog = self.watchdog(driver)
        # Before delivery the span holds, and every alert is already queued.
        decision, state = self.decide(watchdog)
        self.assertEqual("FENCED", decision.state)
        notices = yield_notices(state)
        self.assertEqual(sorted(ids), sorted(item["alert"]["stage_id"] for item in notices))
        self.assertTrue(all(item["alert"]["status"] == "ZERO" for item in notices))
        self.assertEqual(sorted(str(path) for path in alerts), sorted(item["path"] for item in notices))
        self.deliver(driver)
        state = self.assert_released(driver, watchdog, "collected_window")
        self.assertEqual(10, len(yield_notices(state)))

    def test_a_chain_stop_is_released_on_the_driver_records(self) -> None:
        driver = DriverHarness(self, "alpha", g10=False, behavior={"reservation_rc": 1})
        self.assertEqual(driver.driver.EXIT_CHAIN_FAILED, driver.run())
        result = driver.result()
        self.assertEqual(("CHAIN_STOPPED", 10), (result["verdict"], result["chain_exit_code"]))
        self.assertEqual("EMPTY", driver.hazard()["yield"]["yield_status"])
        self.assertTrue((driver.night / "chain.started").exists())
        self.assertTrue((driver.night / "chain.exited").exists())
        watchdog = self.watchdog(driver)
        decision, state = self.decide(watchdog)
        self.assertEqual("FENCED", decision.state)       # no courier yet: the dead-man tail holds
        self.assertEqual([], state.get(RELEASED_TERMINAL, []))
        self.deliver(driver)
        self.assert_released(driver, watchdog, "chain_stopped")

    def test_a_live_process_naming_the_custody_holds_the_release(self) -> None:
        driver = DriverHarness(self, "alpha", g10=False, behavior={"reservation_rc": 1})
        driver.run()
        self.deliver(driver)
        watchdog = self.watchdog(driver)
        watchdog.processes.rows = [wd.ProcessInfo(
            4242, 1, "start", f"python3 monitor --config {driver.custody}/hazards/monitor.json")]
        decision, state = self.decide(watchdog)
        self.assertEqual("HOLD_CENSUS", decision.state)
        self.assertEqual([], state.get(RELEASED_TERMINAL, []))


if __name__ == "__main__":
    unittest.main()
