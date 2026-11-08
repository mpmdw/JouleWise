"""Witness for Opus review finding W-M1 (eng-prearm terminal wake), MEDIUM.

Run against origin/perf/2026-11-08-eng-prearm (348c4a70b) by copying this file
to tests/ and running, one module per process:

    TMPDIR=<real dir> python3.13 -B -m unittest tests.test_terminal_wake_witness

Synthetic plans and a fake process table only; os.fork is patched to the
parent branch, so nothing launches. The marker is published by run_night
before the driver exits (scripts/run_night.py _finish_reporting), so the first
event tick sees the driver alive and transitions FENCED -> HOLD_CENSUS, which
queues a 'hold_census' notice for the magistrate to relay to Ed. A 300 s timer
tick almost always lands after the driver is gone and queues nothing. Fails on
348c4a70b at the notice assertion.
"""

from pathlib import Path
from unittest import mock
import unittest

from scripts import magistrate_watchdog as wd
from tests import test_magistrate_watchdog as twd


class TerminalWakeDoesNotRaiseSpuriousHoldNotice(twd.WatchdogTestCase):
    write_hazard_plan = twd.TerminalWindowReleaseTests.write_hazard_plan
    write_terminal = twd.TerminalWindowReleaseTests.write_terminal

    def _run(self, *, driver_alive_first_tick: bool):
        from joulewise.terminal_wake import publish
        plan = self.write_hazard_plan(t0=self.base.timestamp() - 9.5 * 3600)
        self.write_terminal(plan, ended=self.base.timestamp() - 5)
        self.harness.storage.mkdir(self.harness.storage.root)
        alive = wd.CensusObservation(False, 0, f"4242 python3 scripts/run_night.py run --plan {plan.custody_root}/night_plan.json", "")
        gone = wd.CensusObservation(True, 1, "", "")
        self.harness.driver = alive if driver_alive_first_tick else gone

        def sleep(_seconds):
            self.harness.driver = gone  # the driver exits about one second later

        self.harness.deps.sleep = sleep
        publish(self.harness.storage.root, plan.plan_id, plan.receipt_class,
                now=self.base.timestamp() - 1)
        with mock.patch.object(wd.os, "fork", return_value=4243):
            decision = wd.tick_on_terminal_event(self.harness.storage, self.harness.deps)
        return decision, wd.load_state(self.harness.storage)

    def test_event_tick_racing_the_driver_exit_queues_no_hold_census_notice(self):
        decision, state = self._run(driver_alive_first_tick=True)
        self.assertEqual("LAUNCHING", decision.state)  # the wake itself works
        kinds = [item.get("kind") for item in state.get("notice_pending", [])]
        self.assertNotIn("hold_census", kinds,
                         "terminal wake turned the driver's own exit tail into a census-hold notice")

    def test_control_timer_tick_after_driver_exit_queues_nothing(self):
        decision, state = self._run(driver_alive_first_tick=False)
        self.assertEqual("LAUNCHING", decision.state)
        kinds = [item.get("kind") for item in state.get("notice_pending", [])]
        self.assertNotIn("hold_census", kinds)


if __name__ == "__main__":
    unittest.main()
