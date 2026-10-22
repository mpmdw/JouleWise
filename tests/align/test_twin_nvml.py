"""Lane-vs-twin agreement for the nvml duty-cycle estimator (review round 1).

Runs ``joulewise.align.power.duty`` (lane A2 "nvml", written by Sol 6.1) and
``tests.align.twins.nvml_twin`` (independent twin) on the same seeded,
production-shaped synthetic worlds and compares their outputs.

Bars (set by the orchestrator, not chosen here):
* an output that has a printed uncertainty (``joules``, printed with
  ``half_width_j``) agrees within 1% of the smaller of the two printed
  half-widths for that world;
* an output with no printed uncertainty agrees within 1e-6 relative, or 1e-6
  absolute in its own unit when its value is below 1 (``coverage_fraction``);
* integers (offset plans) must be identical, since bit identity is the real
  property there.

Where the two implementations read an open point of the brief differently,
the comparison is made on the quantity both readings define:
* Gaps (twin R6 integrates the covered set only; the lane divides by the
  covered fraction). Identity checked: lane_joules * coverage == twin_joules.
* Half-width (twin R8 vs the lane's docstring). The forms differ, so the
  totals are not compared. Two worlds isolate terms both readings share:
  the resolution term (twin q*|C|, lane q/2 per unit coefficient, so
  twin = 2 * lane) and the run-to-run spread term on a single-phase sensor
  (both reduce to t(0.975, n-1) * D * stdev(reading)/sqrt(n)).
* Offset plans agree only where both tile with no repeats (n * d == 1).

A known lane defect found by this review (runs whose measured durations
differ by any nanosecond are dropped) is recorded as an expected failure, so
the test flags itself when the lane is fixed.
"""

from __future__ import annotations

import bisect
import json
import math
import random
import unittest

from joulewise.align.records import PowerTrace
from tests.align.twins import nvml_twin as twin

try:  # the lane module lives on lane/2026-10-21-align-nvml; skip on a tree without it
    from joulewise.align.power import duty as lane
except ImportError:  # pragma: no cover - depends on which branch is checked out
    lane = None

MS = 1_000_000
PERIOD = 100 * MS  # A100/H100 class: a 25 ms slice of every 100 ms (records.PowerTrace)
WINDOW = 25 * MS
QUANTUM = 0.001  # NVML reports integer milliwatts
EPOCH = 10**15  # a sensor-period boundary in the trace clock
POWER_BOUND_W = 450.0  # above every synthetic level below (max 380 W + shift + noise)

COVERAGE_ABS = 1e-6  # orchestrator bar: value below 1, no printed uncertainty
REL = 1e-6  # orchestrator bar: no printed uncertainty


class Waveform:
    """Piecewise-constant board power on aligned time u (ns); idle outside [0, D]."""

    def __init__(self, edges: list[int], watts: list[float], idle_w: float) -> None:
        self.edges, self.watts, self.idle = edges, watts, idle_w
        self.duration = edges[-1]

    def integral_w_ns(self, a: int, b: int, shift_w: float, duration: int) -> float:
        parts = []
        if a < 0:
            parts.append(self.idle * (min(b, 0) - a))
        if b > duration:
            parts.append(self.idle * (b - max(a, duration)))
        lo, hi = max(a, 0), min(b, duration)
        if hi > lo:
            parts.append(shift_w * (hi - lo))
            if hi > self.duration:  # a longer run continues its last level
                parts.append(self.watts[-1] * (hi - max(lo, self.duration)))
                hi = min(hi, self.duration)
            if hi > lo:
                i = bisect.bisect_right(self.edges, lo) - 1
                while lo < hi:
                    right = min(self.edges[i + 1], hi)
                    parts.append(self.watts[i] * (right - lo))
                    lo, i = right, i + 1
        return math.fsum(parts)


def agent_waveform(rng: random.Random, turns: int) -> Waveform:
    """Prefill burst, rippled decode plateau and a tool-wait dip per turn.

    Levels and spans are production-shaped for a small local model on a whole
    A100-class board: prefill of 400-2400 tokens at ~8k tokens/s and 300-380 W,
    decode of 30-200 tokens at ~45 tokens/s on a 200-240 W plateau with a
    5-25 W, 7 Hz ripple (5 ms steps), tool waits of 0.1-1.5 s at 60-90 W.
    Every edge falls at an arbitrary nanosecond, so windows straddle phase
    edges and the workload boundaries.
    """
    edges, watts = [0], []

    def segment(length: int, level: float) -> None:
        edges.append(edges[-1] + length)
        watts.append(level)

    for turn in range(turns):
        segment(int(rng.randint(400, 2400) / 8000 * 1e9) + rng.randint(1, 999),
                rng.uniform(300, 380))
        decode_ns = int(rng.randint(30, 200) / 45 * 1e9)
        base, amplitude = rng.uniform(200, 240), rng.uniform(5, 25)
        for step in range(decode_ns // (5 * MS)):
            segment(5 * MS, base + amplitude * math.sin(2 * math.pi * 7 * step * 5 / 1000))
        segment(decode_ns % (5 * MS) + rng.randint(1, 999), base)
        if turn < turns - 1:
            segment(rng.randint(100 * MS, 1500 * MS) + rng.randint(1, 999), rng.uniform(60, 90))
    return Waveform(edges, watts, rng.uniform(50, 60))


def sampled_run(wave: Waveform, offset: int, rng: random.Random, *, shift_w: float,
                noise_w: float, start_jitter_ns: int = 0, duration_jitter_ns: int = 0,
                window: int = WINDOW, period: int = PERIOD,
                label: str | None = None) -> tuple[PowerTrace, int, int]:
    """One repetition: the sensor grid is fixed; the workload starts at offset (+ jitter).

    Each reading is the exact mean of the run's power over its window plus
    Gaussian noise, rounded to the NVML milliwatt. t_ns is the window end, the
    PowerTrace contract both implementations read without lane-local notes.
    """
    start = EPOCH + offset + start_jitter_ns
    duration = wave.duration + duration_jitter_ns
    end = start + duration
    first = (start - period - EPOCH) // period
    last = (end + period - EPOCH) // period + 1
    times, values = [], []
    for k in range(first, last + 1):
        t = EPOCH + k * period
        mean = wave.integral_w_ns(t - window - start, t - start, shift_w, duration) / window
        if noise_w:
            mean += rng.gauss(0.0, noise_w)
        times.append(t)
        values.append(round(mean / QUANTUM) * QUANTUM)
    notes = {"timing_half_width_ns": [0] * len(values), "power_bound_w": POWER_BOUND_W}
    if label is not None:
        notes["repeat_group"] = label
    trace = PowerTrace("nvml_power", "gpu0:power_instant", "synthetic:monotonic",
                       tuple(times), tuple(values), "W", period, window, window / period,
                       QUANTUM, json.dumps(notes))
    return trace, start, end


def joules_bar(lane_result: "lane.DutyEstimate", twin_result: twin.DutyEstimate) -> float:
    # Orchestrator bar: 1% of the smallest printed half-width for this world.
    return 0.01 * min(lane_result.half_width_j, twin_result.half_width_j)


@unittest.skipUnless(lane is not None,
                     "joulewise.align.power.duty (lane nvml) is not on this tree; run on a merge of both")
class TwinAgreementTests(unittest.TestCase):
    def test_offset_plans_agree_where_both_tile_without_repeats(self) -> None:
        for period in (100 * MS, 1_000_000_000, 33_333_333, 99_999_999):
            for duty in (1.0, 0.5, 0.25, 0.125, 0.0625):
                repeats = round(1 / duty)
                self.assertEqual(lane.plan_offsets(period, duty, repeats),
                                 twin.plan_offsets(period, duty, repeats),
                                 (period, duty))  # integers: identity is the property

    def test_student_t_quantiles_agree(self) -> None:
        for dof in range(1, 61):
            a = lane._student_quantile(0.975, dof)
            b = twin.student_t_quantile(0.95, dof)
            self.assertLessEqual(abs(a - b), REL * abs(b), dof)

    def test_tiled_worlds_agree_on_joules_and_coverage(self) -> None:
        worst = 0.0
        for seed in range(32):
            rng = random.Random(seed)
            wave = agent_waveform(rng, turns=rng.randint(2, 4))
            for repeats in (4, 8, 12, 16):
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3)
                        for offset in lane.plan_offsets(PERIOD, 0.25, repeats)]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                context = (seed, repeats, a, b)
                self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction),
                                     COVERAGE_ABS, context)
                self.assertEqual(b.coverage_fraction, 1.0, context)  # the plan tiles
                self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b), context)
                worst = max(worst, abs(a.joules - b.joules) / joules_bar(a, b))
        print("TWIN nvml tiled worlds: worst |dJ| / bar =", worst)

    def test_partial_coverage_gap_reading_identity(self) -> None:
        # Lane fills gaps with the covered mean; twin integrates covered time
        # only. Both pool the same windows, so lane * coverage == twin.
        worst = 0.0
        for seed in range(24):
            rng = random.Random(1000 + seed)
            wave = agent_waveform(rng, turns=rng.randint(2, 4))
            cases = [(lane.plan_offsets(PERIOD, 0.25, n), 0) for n in (1, 2, 3)]
            cases.append((lane.plan_offsets(PERIOD, 0.25, 8), 2 * MS))  # dispatch jitter
            for offsets, jitter in cases:
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3,
                                    start_jitter_ns=rng.randint(0, jitter),
                                    label=f"phase-{offset}")
                        for offset in offsets]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                context = (seed, len(offsets), jitter, a, b)
                self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction),
                                     COVERAGE_ABS, context)
                difference = abs(a.joules * a.coverage_fraction - b.joules)
                self.assertLessEqual(difference, joules_bar(a, b), context)
                worst = max(worst, difference / joules_bar(a, b))
        print("TWIN nvml partial coverage: worst |dJ| / bar =", worst)

    def test_resolution_terms_agree_on_constant_power(self) -> None:
        # Constant power, D a multiple of the 25 ms window, two replicas per
        # phase, no noise: the pooling kernel is exactly one on [0, D], no
        # window straddles a boundary and every replica reads the same value.
        # Twin: q * |C|. Lane: sum(c_i) * q / 2 = q * D / 2.
        for level in (61.234, 213.457, 377.001):
            for windows in (40, 241, 1203):
                duration = windows * WINDOW
                wave = Waveform([0, duration], [level], level)
                runs = [sampled_run(wave, offset, random.Random(0), shift_w=0.0, noise_w=0.0)
                        for offset in lane.plan_offsets(PERIOD, 0.25, 8)]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                self.assertLessEqual(abs(2 * a.half_width_j - b.half_width_j),
                                     REL * b.half_width_j, (level, windows, a, b))
                expected = QUANTUM * duration / 1e9
                self.assertLessEqual(abs(b.half_width_j - expected), REL * expected)

    def test_spread_terms_agree_on_a_single_phase_sensor(self) -> None:
        # A sensor averaging its whole period (d = 1): every run's windows
        # tile [0, D] at offset 0, so all runs share one geometry. Lane:
        # one group, Welch dof n-1, sqrt(n var(z_r)) with z_r = (D/n) v_r.
        # Twin: E_r = D v_r. Both give t(0.975, n-1) * D * sd(v) / sqrt(n).
        for seed in range(12):
            rng = random.Random(500 + seed)
            for n in (2, 3, 5, 8, 16):
                duration = rng.randint(10, 300) * PERIOD
                wave = Waveform([0, duration], [rng.uniform(60, 380)], 55.0)
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.0,
                                    window=PERIOD)
                        for offset in lane.plan_offsets(PERIOD, 1.0, n)]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                resolution_twin = QUANTUM * duration / 1e9
                spread_lane = a.half_width_j - resolution_twin / 2
                spread_twin = b.half_width_j - resolution_twin
                self.assertGreater(spread_twin, 0.0)
                self.assertLessEqual(abs(spread_lane - spread_twin), REL * spread_twin,
                                     (seed, n, a, b))
                self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))

    @unittest.expectedFailure
    def test_jittered_durations_keep_every_run(self) -> None:
        # Review finding: the lane drops every run whose measured duration
        # differs from the first by any nanosecond ("duration_mismatch"), so a
        # real replay set (durations jitter by microseconds) keeps one run.
        rng = random.Random(77)
        wave = agent_waveform(rng, turns=3)
        runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3,
                            duration_jitter_ns=rng.randint(-300_000, 300_000))
                for offset in lane.plan_offsets(PERIOD, 0.25, 8)]
        a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
        self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), COVERAGE_ABS)


if __name__ == "__main__":
    unittest.main()
