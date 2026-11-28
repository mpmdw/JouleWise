"""RUN_STATE 280: the R1 inventory sampler holds a 1.000 s period (RL-74/RL-76 bar).

The real ``_inventory_process`` loop runs in this interpreter on a fake
monotonic clock: waits and sweeps advance the clock instead of real time.
"""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit

WAKE_LATENCY_S = 0.006      # smoke 280: 1.124 s measured vs 0.99 + 0.128 s predicted


class Clock:
    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now


CLOCK = Clock()
SWEEPS = {"default": 0.13, "stall": {}}


class FakeReader:
    """One key; each read costs the configured sweep time on the fake clock."""

    def __init__(self):
        self.reads = 0

    def enumerate_sensors(self):
        return {"complete": True, "keys": [{"key": "TV0h", "unit": "degC"}], "errors": {}}

    def read(self, keys):
        self.reads += 1
        CLOCK.now += SWEEPS["stall"].get(self.reads, SWEEPS["default"])
        return {"values": {key: 40.0 for key in keys}, "errors": {}}

    def close(self):
        pass


class Stop:
    def __init__(self, ticks):
        self.ticks, self.waits = ticks, 0

    def is_set(self):
        return self.waits >= self.ticks

    def wait(self, seconds):
        self.waits += 1
        CLOCK.now += seconds + WAKE_LATENCY_S
        return self.is_set()


class Ready:
    def send(self, value):
        self.value = value

    def close(self):
        pass


def run(ticks, sweep, stall=None):
    SWEEPS["default"], SWEEPS["stall"] = sweep, stall or {}
    CLOCK.now = 1000.0
    with tempfile.TemporaryDirectory() as tmp, patch("time.monotonic", CLOCK.monotonic):
        path = Path(tmp) / "inventory_journal.jsonl"
        rt._inventory_process(str(path), Stop(ticks), Ready(), __name__ + ":FakeReader")
        import json
        return [json.loads(line) for line in path.read_text().splitlines()]


class InventoryPeriodTests(unittest.TestCase):
    def coverage(self, rows):
        start = rows[0]["started"]["monotonic_ns"]
        end = rows[-1]["started"]["monotonic_ns"] + rt.NS
        return kit.phase_coverage(rows, ["TV0h"], {"span": (start, end)}, required_keys=["TV0h"])

    def starts(self, rows):
        return [r["started"]["monotonic_ns"] / rt.NS for r in rows]

    def test_slow_sweeps_keep_a_one_second_period_and_fill_99_percent_of_cells(self):
        for sweep in (0.13, 0.21):
            with self.subTest(sweep=sweep):
                rows = run(620, sweep)
                starts = self.starts(rows)
                gaps = [b - a for a, b in zip(starts, starts[1:])]
                self.assertGreaterEqual(len(rows), 600)
                self.assertAlmostEqual(sorted(gaps)[len(gaps) // 2], 1.0, delta=0.002)   # median period
                self.assertAlmostEqual((starts[-1] - starts[0]) / (len(starts) - 1), 1.0, delta=0.002)
                report = self.coverage(rows)
                self.assertGreaterEqual(report["sampler"]["span"]["sample_fraction"], .99, report["sampler"])
                self.assertGreaterEqual(report["phases"]["span"]["TV0h"]["sample_fraction"], .99)
                self.assertTrue(report["pass"], report["sampler"])

    def test_a_stall_skips_whole_ticks_without_a_burst(self):
        rows = run(620, 0.13, stall={300: 2.5})
        starts = self.starts(rows)
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        report = self.coverage(rows)
        self.assertGreaterEqual(report["sampler"]["span"]["sample_fraction"], .99, report["sampler"])
        self.assertGreater(min(gaps), 0.9)         # no catch-up burst after the stall
        stall = gaps.index(max(gaps))
        self.assertAlmostEqual(gaps[stall], 3.0, delta=0.01)   # the stall row, then the next grid tick
        after = gaps[stall + 1:]
        self.assertTrue(all(abs(g - 1.0) < 0.002 for g in after), after[:5])   # back on the 1 s grid
        # Missed cells stay missed: no row synthesizes them.
        self.assertEqual(len(rows), len(set(round(s) for s in starts)))


if __name__ == "__main__":
    unittest.main()
