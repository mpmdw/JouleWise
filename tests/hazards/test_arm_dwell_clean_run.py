"""Gate prune 2, A1: the hazard arm's dwell needs a 180 s clean run, the legacy
prewindow dwell keeps 600 s, and the 0.05 CPU-s/s limit and 2700 s cap stay."""
from __future__ import annotations

import unittest

from joulewise import prewindow
from joulewise.hazards import arm, base, contention
from tests.hazards.fakes import FakeClocks, FakeProcessTable, Runner

DRIVER = 4000


def machine():
    clocks = FakeClocks()
    table = FakeProcessTable(clocks, driver_pid=DRIVER)
    runner = Runner({contention.PS_ARGV: table.ps})
    return clocks, table, base.Context(run=runner, clocks=clocks)


class HazardArmCleanRunTests(unittest.TestCase):
    def test_the_hazard_arm_default_is_180_s_and_prewindow_keeps_600_s(self):
        self.assertEqual(contention.DEFAULT_THRESHOLDS["clean_s"], 180)
        self.assertEqual(arm.default_thresholds()["contention"]["clean_s"], 180)
        self.assertEqual(prewindow.MIN_CLEAN_DWELL_S, 600)
        # The limits that protect the arm are unchanged.
        self.assertEqual(contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"], 0.05)
        self.assertEqual(contention.DEFAULT_THRESHOLDS["cap_s"], 2700)
        self.assertEqual(contention.DEFAULT_THRESHOLDS["interval_s"], 30)

    def test_a_quiet_mac_is_ready_after_180_s_with_the_default_thresholds(self):
        _clocks, _table, ctx = machine()
        thresholds = arm.default_thresholds()["contention"]
        measurement = contention.run_dwell(ctx, thresholds, tree_roots=[DRIVER])
        verdict = contention.judge(measurement, thresholds)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertGreaterEqual(measurement.values["clean_run_s"], 180)
        self.assertLess(measurement.values["elapsed_s"], 240)

    def test_a_dirty_interval_still_restarts_the_180_s_run(self):
        _clocks, table, ctx = machine()
        table.processes[360].schedule = [(60.0, 90.0, 0.368)]
        thresholds = arm.default_thresholds()["contention"]
        measurement = contention.run_dwell(ctx, thresholds, tree_roots=[DRIVER])
        self.assertEqual(contention.judge(measurement, thresholds).status, base.PASS)
        intervals = measurement.values["intervals"]
        dirty_end = [item for item in intervals if item["clean"] is False][-1]["interval"]["monotonic_ns"][1]
        self.assertGreaterEqual(measurement.values["ready_at_monotonic_ns"] - dirty_end, 180 * 10**9)

    def test_a_persistent_contender_still_refuses_at_the_cap(self):
        _clocks, table, ctx = machine()
        table.processes[340].cpu_per_s = 0.06
        thresholds = arm.default_thresholds()["contention"]
        measurement = contention.run_dwell(ctx, thresholds, tree_roots=[DRIVER])
        self.assertEqual(contention.judge(measurement, thresholds).status, base.REFUSE)
        self.assertGreaterEqual(measurement.values["elapsed_s"], 2700)


if __name__ == "__main__":
    unittest.main()
