"""Closed-form and hand-computable checks of the nvml twin (tests/align/twins/nvml_twin.py).

Every expected value below is computed by hand (in a comment) or by exact
rational arithmetic (fractions.Fraction) independent of the twin's code. Every
bar on a float carries its derivation.

Float-noise bars count the correctly rounded operations between the exact value
and the float compared. Each such operation is off by at most half an ulp,
which is EPS/2 relative. When all the terms summed have one sign, these
relative errors add: k roundings give at most k * EPS/2 relative
(``noise_bar``).
"""

from __future__ import annotations

import dataclasses
import math
import statistics
import sys
import unittest
from fractions import Fraction

from joulewise.align.records import PowerTrace
from tests.align.twins.nvml_twin import (
    DutyEstimate, estimate_energy, plan_offsets, student_t_quantile,
)

EPS = sys.float_info.epsilon
MS = 1_000_000  # ns per ms
NS_PER_S = 1_000_000_000

# The simulated sensor: a 25 ms averaging window in every 100 ms period (the
# A100/H100 behaviour the brief names), reporting at the end of each window.
PERIOD = 100 * MS
WINDOW = 25 * MS
DUTY = 0.25
DURATION = 1000 * MS  # workload length: 10 periods, 40 windows
RESOLUTION_W = 0.001  # NVML power is reported in integer milliwatts


def noise_bar(magnitude: float, roundings: int) -> float:
    """At most ``roundings`` half-ulp roundings on same-signed terms: roundings * EPS/2 relative."""
    return roundings * 0.5 * EPS * abs(magnitude)


# Relative bar for comparing two computations of a quantity that has no
# printed uncertainty: 1e-6 relative (docs/align/PIPELINE.md, "where no
# uncertainty exists, 1e-6 relative").
AGREEMENT_REL = 1e-6


# ------------------------------------------------------------------ exact waveform

def _waveform_segments() -> list[tuple[int, int, Fraction, Fraction]]:
    """Piecewise-linear power (W) against aligned time (ns): (t0, t1, p(t0), p(t1)).

    idle 60 W before the workload; prefill burst (ramp 60 -> 350 W over 50 ms,
    hold to 200 ms); decode plateau 220 W with a triangular ripple of +-15 W
    and period 40 ms (200-600 ms); a tool-wait dip to 90 W (600-750 ms); decode
    220 W (750-1000 ms); idle 60 W after.
    """
    seg = [(-20 * PERIOD, 0, 60, 60), (0, 50 * MS, 60, 350), (50 * MS, 200 * MS, 350, 350),
           (200 * MS, 210 * MS, 220, 235)]
    knots = [(210 + 20 * j, 235 if j % 2 == 0 else 205) for j in range(20)]  # 210..590 ms
    for (ta, pa), (tb, pb) in zip(knots, knots[1:]):
        seg.append((ta * MS, tb * MS, pa, pb))
    seg += [(590 * MS, 600 * MS, 205, 220), (600 * MS, 750 * MS, 90, 90),
            (750 * MS, 1000 * MS, 220, 220), (1000 * MS, 40 * PERIOD, 60, 60)]
    return [(a, b, Fraction(pa), Fraction(pb)) for a, b, pa, pb in seg]


SEGMENTS = _waveform_segments()


def exact_integral(lo: int, hi: int) -> Fraction:
    """Exact integral of the waveform over [lo, hi] in W*ns (trapezoids on linear pieces)."""
    total = Fraction(0)
    for a, b, pa, pb in SEGMENTS:
        x0, x1 = max(a, lo), min(b, hi)
        if x1 > x0:
            p0 = pa + (pb - pa) * Fraction(x0 - a, b - a)
            p1 = pa + (pb - pa) * Fraction(x1 - a, b - a)
            total += (p0 + p1) / 2 * (x1 - x0)
    return total


def simulated_run(offset_ns: int, *, reports: int = 17) -> tuple[PowerTrace, int, int]:
    """One run of the workload sampled by the 25-of-100 ms sensor.

    The sensor reports at t_j = j * PERIOD (j = 1 .. reports) in the trace
    clock; reading j is the exact mean of the run's power over
    [t_j - WINDOW, t_j], rounded once to float. The workload starts at phase
    ``offset_ns`` of the period: start = 5 * PERIOD + offset_ns.
    """
    start = 5 * PERIOD + offset_ns
    t_ns = tuple(j * PERIOD for j in range(1, reports + 1))
    values = tuple(float(exact_integral(t - WINDOW - start, t - start) / WINDOW) for t in t_ns)
    trace = PowerTrace("nvml_power", "gpu0", "gpu0.mono", t_ns, values, "W", PERIOD,
                       averaging_window_ns=WINDOW, duty_fraction=DUTY, resolution=RESOLUTION_W)
    return trace, start, start + DURATION


def constant_trace(watts: float, t_ns: tuple[int, ...], window_ns: int | None, nominal_ns: int,
                   *, channel: str = "gpu0", resolution: float | None = RESOLUTION_W) -> PowerTrace:
    return PowerTrace("nvml_power", channel, "gpu0.mono", t_ns, tuple(watts for _ in t_ns), "W",
                      nominal_ns, averaging_window_ns=window_ns, resolution=resolution)


def readings_inside(trace: PowerTrace, start: int, end: int) -> list[float]:
    """Readings whose whole window lies inside [start, end] (in the tiled world every window is inside or outside)."""
    return [v for t, v in zip(trace.t_ns, trace.values) if t - WINDOW >= start and t <= end]


# ------------------------------------------------------------------ plan_offsets

class PlanOffsetsTest(unittest.TestCase):
    def test_quarter_duty_four_repeats_by_hand(self):
        # floor(k * 100 ms / 4) = 0, 25, 50, 75 ms. Integers: exact equality is the property.
        self.assertEqual(plan_offsets(PERIOD, DUTY, 4), [0, 25 * MS, 50 * MS, 75 * MS])

    def test_eight_repeats_spread_evenly(self):
        self.assertEqual(plan_offsets(PERIOD, DUTY, 8), [k * 12_500_000 for k in range(8)])

    def test_floor_when_period_does_not_divide(self):
        # floor(0), floor(100/3) = 33, floor(200/3) = 66.
        self.assertEqual(plan_offsets(100, 0.5, 3), [0, 33, 66])

    def test_full_duty_single_run(self):
        self.assertEqual(plan_offsets(PERIOD, 1.0, 1), [0])

    def test_offsets_are_ints(self):
        self.assertTrue(all(type(x) is int for x in plan_offsets(99_999_999, 0.3, 7)))

    def test_windows_tile_the_period(self):
        # Every cyclic gap between consecutive offsets is at most the window
        # length d*T plus 1 ns: floor() moves each offset down by less than
        # 1 ns, so a gap is at most 1 ns longer than T/n <= d*T.
        for period, duty, repeats in [(PERIOD, 0.25, 4), (PERIOD, 0.25, 5), (PERIOD, 0.3, 4),
                                      (99_999_999, 0.1, 10), (7, 0.5, 2), (PERIOD, 1.0, 3)]:
            offsets = plan_offsets(period, duty, repeats)
            gaps = [b - a for a, b in zip(offsets, offsets[1:])] + [period - offsets[-1] + offsets[0]]
            self.assertLessEqual(max(gaps), duty * period + 1, (period, duty, repeats))

    def test_too_few_repeats_cannot_tile(self):
        with self.assertRaises(ValueError):
            plan_offsets(PERIOD, 0.25, 3)  # 3 * 0.25 = 0.75 of the period
        with self.assertRaises(ValueError):
            plan_offsets(PERIOD, 0.3, 3)  # 0.9 of the period
        plan_offsets(PERIOD, 0.3, 4)  # 1.2: tiles

    def test_epsilon_allowance_admits_exact_reciprocal(self):
        # 49 * fl(1/49) evaluates to 0.9999999999999999 in IEEE doubles, one
        # rounding below 1; mathematically it is 1, so the windows tile.
        self.assertLess(49 * (1 / 49), 1.0)
        self.assertEqual(len(plan_offsets(49 * MS, 1 / 49, 49)), 49)

    def test_invalid_arguments(self):
        for args in [(0, 0.25, 4), (-5, 0.25, 4), (True, 0.25, 4), (PERIOD, 0.0, 4),
                     (PERIOD, 1.5, 4), (PERIOD, -0.1, 4), (PERIOD, 0.25, 0), (PERIOD, 0.25, 2.0)]:
            with self.assertRaises(ValueError, msg=repr(args)):
                plan_offsets(*args)


# ------------------------------------------------------------------ estimate_energy, hand worlds

class EstimateEnergyHandTest(unittest.TestCase):
    def test_record_shape(self):
        self.assertEqual([f.name for f in dataclasses.fields(DutyEstimate)],
                         ["joules", "half_width_j", "coverage_fraction", "flags"])

    def test_clipped_windows_by_hand(self):
        # Samples at 10, 110, 210 ms (100, 200, 300 W), window 25 ms, workload
        # [0, 200 ms]. Windows cut to the workload: [0,10] at 100 W,
        # [85,110] at 200 W, [185,200] at 300 W. Covered 10 + 25 + 15 = 50 ms.
        # joules = (100*10 + 200*25 + 300*15) W*ms = 10500 W*ms = 10.5 J.
        # coverage = 50/200 = 0.25.
        # hw = 150 ms * 300 W (uncovered * P_max) + 0.001 W * 50 ms = 45 + 0.00005 J.
        trace = PowerTrace("nvml_power", "gpu0", "gpu0.mono", (10 * MS, 110 * MS, 210 * MS),
                           (100.0, 200.0, 300.0), "W", PERIOD, averaging_window_ns=WINDOW,
                           duty_fraction=DUTY, resolution=RESOLUTION_W)
        est = estimate_energy([(trace, 0, 200 * MS)])
        # joules: three products, one fsum, one division (5 roundings, all positive terms).
        self.assertLessEqual(abs(est.joules - 10.5), noise_bar(10.5, 5))
        self.assertLessEqual(abs(est.coverage_fraction - 0.25), noise_bar(0.25, 1))  # one division
        # hw: product and division per term (2+2), the sum of the terms (1),
        # and the expected value's own two operations: 7 roundings.
        self.assertLessEqual(abs(est.half_width_j - (45.0 + 0.00005)), noise_bar(45.00005, 7))
        self.assertEqual(est.flags, ("incomplete_coverage", "spread_unavailable"))

    def test_overlapping_windows_within_one_run(self):
        # Polling every 10 ms with a 25 ms window: samples at 25 and 35 ms
        # (100, 200 W) cover [0,25] and [10,35]. Pooled: [0,10) 100 W,
        # [10,25) mean 150 W, [25,35) 200 W:
        # 100*10 + 150*15 + 200*10 = 5250 W*ms = 5.25 J; coverage 35/100.
        trace = PowerTrace("nvml_power", "gpu0", "gpu0.mono", (25 * MS, 35 * MS), (100.0, 200.0), "W",
                           10 * MS, averaging_window_ns=WINDOW, resolution=RESOLUTION_W)
        est = estimate_energy([(trace, 0, 100 * MS)])
        # fsum of two readings and halving (1), three products (1 each), fsum (1), division (1).
        self.assertLessEqual(abs(est.joules - 5.25), noise_bar(5.25, 4))
        self.assertLessEqual(abs(est.coverage_fraction - 0.35), noise_bar(0.35, 2))  # the division and the literal
        # hw = 65 ms * 200 W + 0.001 W * 35 ms = 13 + 0.000035 J (7 roundings as above).
        self.assertLessEqual(abs(est.half_width_j - 13.000035), noise_bar(13.000035, 7))

    def test_missing_averaging_window_uses_nominal_interval(self):
        # Ten samples of 50 W every 100 ms, no window recorded: each stands for
        # the 100 ms before it, so [0, 1 s] is covered and joules = 50 J.
        t_ns = tuple(j * PERIOD for j in range(1, 11))
        est = estimate_energy([(constant_trace(50.0, t_ns, None, PERIOD), 0, DURATION)])
        self.assertLessEqual(abs(est.joules - 50.0), noise_bar(50.0, 3))  # products exact; fsum, division
        self.assertEqual(est.coverage_fraction, 1.0)  # covered == reference as integers: 1e9/1e9
        self.assertIn("averaging_window_unknown", est.flags)

    def test_two_runs_spread_closed_form(self):
        # Full-duty sensor (window = period = 100 ms). Two runs, same phase,
        # constant 100 W and 110 W over 1 s. Pooled power is 105 W everywhere:
        # joules = 105 J, coverage 1. Single-run estimates 100 and 110 J:
        # stdev = sqrt(50); m = 2, t(0.975, 1) = tan(0.475*pi) (Cauchy).
        # hw = 0.001 W * 1 s + tan(0.475*pi) * sqrt(50)/sqrt(2)
        #    = 0.001 + 5 * tan(0.475*pi) = 0.001 + 63.531... J.
        t_ns = tuple(j * PERIOD for j in range(1, 16))
        runs = [(constant_trace(100.0, t_ns, PERIOD, PERIOD), 2 * PERIOD, 12 * PERIOD),
                (constant_trace(110.0, t_ns, PERIOD, PERIOD), 2 * PERIOD, 12 * PERIOD)]
        est = estimate_energy(runs)
        self.assertLessEqual(abs(est.joules - 105.0), noise_bar(105.0, 3))
        self.assertEqual(est.coverage_fraction, 1.0)
        expected_hw = 0.001 + 5.0 * math.tan(0.475 * math.pi)
        # The twin finds t by bisection, the test by the closed form: two
        # computations, no printed uncertainty, so 1e-6 relative.
        self.assertLessEqual(abs(est.half_width_j - expected_hw), AGREEMENT_REL * expected_hw)
        self.assertEqual(est.flags, ())

    def test_runs_of_different_length(self):
        # Constant 100 W, full-duty sensor; runs of 1.0 s and 1.1 s. The aligned
        # union is [0, 1.1 s], fully covered at 100 W: joules = 110 J.
        t_ns = tuple(j * PERIOD for j in range(1, 16))
        runs = [(constant_trace(100.0, t_ns, PERIOD, PERIOD), 2 * PERIOD, 12 * PERIOD),
                (constant_trace(100.0, t_ns, PERIOD, PERIOD), 2 * PERIOD, 13 * PERIOD)]
        est = estimate_energy(runs)
        self.assertLessEqual(abs(est.joules - 110.0), noise_bar(110.0, 3))
        self.assertEqual(est.coverage_fraction, 1.0)
        self.assertIn("durations_differ", est.flags)

    def test_mixed_channels_flagged(self):
        t_ns = tuple(j * PERIOD for j in range(1, 16))
        runs = [(constant_trace(100.0, t_ns, PERIOD, PERIOD), 2 * PERIOD, 12 * PERIOD),
                (constant_trace(100.0, t_ns, PERIOD, PERIOD, channel="gpu1"), 2 * PERIOD, 12 * PERIOD)]
        self.assertIn("mixed_channels", estimate_energy(runs).flags)

    def test_unknown_resolution_adds_nothing_and_is_flagged(self):
        t_ns = tuple(j * PERIOD for j in range(1, 11))
        est = estimate_energy([(constant_trace(50.0, t_ns, PERIOD, PERIOD, resolution=None), 0, DURATION)])
        self.assertEqual(est.half_width_j, 0.0)  # full coverage, one run, no quantum: every term is exactly 0
        self.assertIn("resolution_unknown", est.flags)

    def test_no_coverage(self):
        # One sample whose 5 ms window ends at 10 ms; the workload is [100, 200] ms.
        trace = constant_trace(80.0, (10 * MS,), 5 * MS, 5 * MS)
        est = estimate_energy([(trace, 100 * MS, 200 * MS)])
        self.assertEqual(est.joules, 0.0)
        self.assertEqual(est.coverage_fraction, 0.0)
        self.assertEqual(est.half_width_j, math.inf)
        self.assertEqual(est.flags, ("incomplete_coverage", "no_coverage", "run_without_coverage",
                                     "spread_unavailable"))

    def test_refusals(self):
        with self.assertRaises(ValueError):
            estimate_energy([])
        energy = PowerTrace("nvml_energy", "gpu0", "gpu0.mono", (1, 2), (0.0, 1.0), "J_cumulative", 1)
        with self.assertRaises(ValueError):
            estimate_energy([(energy, 0, 2)])
        with self.assertRaises(ValueError):
            estimate_energy([(constant_trace(1.0, (10,), 5, 5), 7, 7)])


# ------------------------------------------------------------------ estimate_energy, waveform worlds

class EstimateEnergyWaveformTest(unittest.TestCase):
    """The brief's synthetic waveform under the 25-of-100 ms sensor, checked against exact integrals."""

    def setUp(self):
        self.truth_w_ns = exact_integral(0, DURATION)
        self.truth_j = float(self.truth_w_ns / NS_PER_S)

    def test_four_tiled_runs_recover_the_exact_integral(self):
        # Offsets 0, 25, 50, 75 ms: the 25 ms windows of the four runs abut
        # in aligned time, and every window lies wholly inside or outside
        # [0, 1 s]. Each reading times its window length is that window's
        # exact energy, so the pooled integral is the exact integral.
        runs = [simulated_run(o) for o in plan_offsets(PERIOD, DUTY, 4)]
        est = estimate_energy(runs)
        # Roundings: each reading (1) and its product with the window length
        # (1) on positive terms; the fsum (1), the division by 1e9 (1), and
        # the float conversion of the exact truth (1). 5 in all.
        self.assertLessEqual(abs(est.joules - self.truth_j), noise_bar(self.truth_j, 5))
        self.assertEqual(est.coverage_fraction, 1.0)  # covered == reference, both the integer 1e9
        self.assertEqual(est.flags, ())

        # Half-width by hand: resolution term 0.001 W * 1 s, plus the spread
        # of the four single-run estimates E_k = D * mean(run k's 10 readings).
        single = [DURATION * (math.fsum(readings_inside(*run)) / 10) / NS_PER_S for run in runs]
        self.assertEqual([len(readings_inside(*run)) for run in runs], [10, 10, 10, 10])
        m = len(single)
        t975 = student_t_quantile(0.95, m - 1)
        expected = RESOLUTION_W * DURATION / NS_PER_S + t975 * statistics.stdev(single) / math.sqrt(m)
        # Bar. The twin's E_k and the test's differ only in rounding: 5 (twin:
        # products, fsum, mean, times D, /1e9) + 4 (test: fsum, /10, times D,
        # /1e9) = 9 half-ulp roundings of E_k. A sample stdev moves by at most
        # max|delta| * sqrt(m/(m-1)) when each input moves by at most |delta|,
        # so the spread term moves by at most t * max|delta| / sqrt(m-1). The
        # remaining arithmetic (the stdev's own rounding, times t, / sqrt(m),
        # the resolution term, the sum) is 8 roundings of the half-width on
        # each side.
        bar = (t975 * noise_bar(max(single), 9) / math.sqrt(m - 1)
               + noise_bar(expected, 16))
        self.assertLessEqual(abs(est.half_width_j - expected), bar)
        # The printed interval contains the truth.
        self.assertLessEqual(abs(est.joules - self.truth_j), est.half_width_j)

    def test_single_run_sees_a_quarter(self):
        # Offset 0: run 0's windows are [75, 100] + 100 i ms, i = 0..9, ten
        # windows of 25 ms. joules = exact energy in those windows;
        # coverage = 250/1000 = 0.25. hw = 750 ms * P_max + 0.001 W * 250 ms.
        run = simulated_run(0)
        est = estimate_energy([run])
        covered_exact = sum(exact_integral((75 + 100 * i) * MS, (100 + 100 * i) * MS) for i in range(10))
        expected_j = float(covered_exact / NS_PER_S)
        self.assertLessEqual(abs(est.joules - expected_j), noise_bar(expected_j, 5))  # as in the tiled test
        self.assertEqual(est.coverage_fraction, 0.25)  # 250e6 / 1e9, correctly rounded, exact in binary
        p_max = max(readings_inside(*run))
        expected_hw = 750 * MS * p_max / NS_PER_S + RESOLUTION_W * 250 * MS / NS_PER_S
        # 2 + 2 roundings for the two terms and 1 for their sum, on each side: 10.
        self.assertLessEqual(abs(est.half_width_j - expected_hw), noise_bar(expected_hw, 10))
        self.assertEqual(est.flags, ("incomplete_coverage", "spread_unavailable"))
        # The uncovered three quarters stay inside the printed interval.
        self.assertLessEqual(abs(est.joules - self.truth_j), est.half_width_j)

    def test_eight_runs_double_cover_constant_power(self):
        # Eight runs, offsets every 12.5 ms: each aligned point lies under two
        # 25 ms windows; windows straddling 0 and 1 s are cut. Constant 150 W
        # everywhere, so every pooled mean is 150 W and every single-run
        # estimate is 150 J: joules = 150 J, spread 0, hw = 0.001 W * 1 s.
        t_ns = tuple(j * PERIOD for j in range(1, 18))
        runs = []
        for offset in plan_offsets(PERIOD, DUTY, 8):
            trace = constant_trace(150.0, t_ns, WINDOW, PERIOD)
            start = 5 * PERIOD + offset
            runs.append((trace, start, start + DURATION))
        est = estimate_energy(runs)
        # Means of two equal readings and products with integer lengths are
        # exact here; fsum (1) and division (1) remain.
        self.assertLessEqual(abs(est.joules - 150.0), noise_bar(150.0, 2))
        self.assertEqual(est.coverage_fraction, 1.0)
        self.assertLessEqual(abs(est.half_width_j - 0.001), noise_bar(0.001, 4))  # product, division; stdev 0
        self.assertEqual(est.flags, ())

    def test_run_without_coverage_drops_from_spread(self):
        # A run whose trace stops before its workload gives no windows: it is
        # flagged, and with one covered run left the spread is unavailable.
        covered = simulated_run(0)
        empty_trace = constant_trace(80.0, (MS,), WINDOW, PERIOD)
        est = estimate_energy([covered, (empty_trace, 5 * PERIOD, 5 * PERIOD + DURATION)])
        self.assertIn("run_without_coverage", est.flags)
        self.assertIn("spread_unavailable", est.flags)


# ------------------------------------------------------------------ Student t quantile

class StudentTQuantileTest(unittest.TestCase):
    def test_closed_forms(self):
        # dof 1 (Cauchy): t = tan(pi * (0.975 - 0.5)).
        # dof 2: P(|T| <= t) = t / sqrt(2 + t^2), so t = a * sqrt(2 / (1 - a^2)), a = 0.95.
        # Two computations, no printed uncertainty: 1e-6 relative.
        for dof, closed in [(1, math.tan(0.475 * math.pi)), (2, 0.95 * math.sqrt(2 / (1 - 0.95 ** 2)))]:
            self.assertLessEqual(abs(student_t_quantile(0.95, dof) - closed), AGREEMENT_REL * closed)

    def test_printed_table(self):
        # NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.6.7.2
        # (upper critical values of Student's t, column 0.025), printed to
        # three decimals: the bar is half a unit in the last printed digit.
        table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 10: 2.228, 30: 2.042, 100: 1.984}
        for dof, printed in table.items():
            self.assertLessEqual(abs(student_t_quantile(0.95, dof) - printed), 0.0005, dof)


if __name__ == "__main__":
    unittest.main()
