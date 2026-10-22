"""Lane-vs-twin agreement for the nvml duty-cycle estimator (review round 2).

Runs ``joulewise.align.power.duty`` (lane A2 "nvml", Sol 6.1, head 432f14c7a)
and ``tests.align.twins.nvml_twin`` (independent twin) on the same seeded,
production-shaped synthetic worlds and compares their outputs.

Bars (set by the orchestrator, not chosen here):
* an output with a printed uncertainty (``joules``, printed beside
  ``half_width_j``) agrees within 1% of the smallest finite printed half-width
  of the two implementations for that world;
* an output with no printed uncertainty agrees within 1e-6 relative, or 1e-6
  absolute in its own unit when its value is below 1 (``coverage_fraction``);
* integers (offset plans) must be identical: bit identity is the property.

Where the two implementations read an open point of the brief differently,
the comparison is made on the quantity both readings define:
* Gaps. The twin (R6) integrates the covered set only; the lane multiplies
  the pooled integral by D / |C|. Both pool the same clipped windows, so the
  identity checked is lane_joules * coverage == twin_joules.
* Half-width totals. The twin adds a coverage bound, q*|C| and a cross-run
  Student-t term; the lane adds q/2 per unit coefficient, a per-phase Welch
  term and a centre-widening term, and reports systematic error only in the
  ``worst_case_bias_j=`` flag. The totals are not compared. Two worlds isolate
  terms both readings share: the resolution term on constant power
  (twin = 2 * lane) and the spread term on a d = 1 sensor (both reduce to
  t(0.975, n-1) * D * stdev(reading) / sqrt(n)).
* Offset plans agree only where both tile without repeats (n * d == 1).
  Beyond that the lane repeats ceil(1/d) phases and the twin spreads n
  offsets evenly; both are checked to tile the period.

Two lane defects found by review 2 are recorded as expected failures, so the
file flags itself when the lane is fixed: the lane's printed half-width does
not contain the truth when coverage is partial (it carries no coverage term),
nor on a deterministic replay whose end straddles a sensor window.
"""

from __future__ import annotations

import bisect
import ctypes
import json
import math
import random
import threading
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
# Diagnostic only (the lane's worst_case_bias_j flag): above every synthetic
# level below, 380 W prefill + 4 sigma of a 2 W shift + 4 sigma of 0.3 W noise.
POWER_BOUND_W = 450.0

COVERAGE_ABS = 1e-6  # orchestrator bar: value below 1, no printed uncertainty
REL = 1e-6  # orchestrator bar: no printed uncertainty


class Waveform:
    """Piecewise-constant board power on aligned time u (ns); idle outside [0, D]."""

    def __init__(self, edges: list[int], watts: list[float], idle_w: float) -> None:
        self.edges, self.watts, self.idle = edges, watts, idle_w
        self.duration = edges[-1]

    def integral_w_ns(self, a: int, b: int, shift_w: float, duration: int) -> float:
        """Integral of one run's power over [a, b] (W*ns): p0 + shift inside [0, duration]."""
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

    def truth_j(self) -> float:
        return self.integral_w_ns(0, self.duration, 0.0, self.duration) / 1e9


def agent_waveform(rng: random.Random, turns: int) -> Waveform:
    """Prefill burst, rippled decode plateau and a tool-wait dip per turn.

    Production-shaped for a small local model on a whole A100-class board:
    prefill of 400-2400 tokens at ~8k tokens/s and 300-380 W, decode of
    30-200 tokens at ~45 tokens/s on a 200-240 W plateau with a 5-25 W, 7 Hz
    ripple (5 ms steps), tool waits of 0.1-1.5 s at 60-90 W, idle 50-60 W.
    The last turn ends in decode, so the workload end is a power step that a
    sensor window straddles. Every edge falls at an arbitrary nanosecond.
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
                window: int = WINDOW, period: int = PERIOD, label: str | None = None,
                first_sample_after_start_ns: int | None = None) -> tuple[PowerTrace, int, int]:
    """One repetition: the sensor grid is fixed; the workload starts at offset (+ jitter).

    Each reading is the exact mean of the run's power over its window plus
    Gaussian noise, rounded to the NVML milliwatt. t_ns is the window end (the
    PowerTrace contract). ``first_sample_after_start_ns`` drops every sample
    before that aligned time (a sampler that started late).
    """
    start = EPOCH + offset + start_jitter_ns
    duration = wave.duration + duration_jitter_ns
    end = start + duration
    first = (start - period - EPOCH) // period
    last = (end + period - EPOCH) // period + 1
    times, values = [], []
    for k in range(first, last + 1):
        t = EPOCH + k * period
        if first_sample_after_start_ns is not None and t - start < first_sample_after_start_ns:
            continue
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


def joules_bar(a: "lane.DutyEstimate", b: twin.DutyEstimate) -> float:
    """Orchestrator bar: 1% of the smallest finite printed half-width, else 1e-6 relative."""
    widths = [w for w in (a.half_width_j, b.half_width_j) if math.isfinite(w) and w > 0]
    if widths:
        return 0.01 * min(widths)
    return REL * max(abs(a.joules), abs(b.joules))


def tiles(offsets: list[int], period: int, window: int) -> bool:
    """True when windows [o, o + window) mod period cover the whole period (integers)."""
    starts = sorted({o % period for o in offsets})
    gaps = [b - a for a, b in zip(starts, starts[1:])] + [starts[0] + period - starts[-1]]
    return max(gaps) <= window


@unittest.skipUnless(lane is not None,
                     "joulewise.align.power.duty (lane nvml) is not on this tree; run on a merge of both")
class TwinAgreementTests(unittest.TestCase):
    def assert_agree(self, runs: list[tuple[PowerTrace, int, int]], context: object) -> tuple:
        a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
        context = (context, a, b)
        self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), COVERAGE_ABS, context)
        bar = joules_bar(a, b)
        # Gap reading: lane fills uncovered time with the covered mean (D/|C|),
        # the twin does not; lane * coverage is the pooled integral both define.
        self.assertLessEqual(abs(a.joules * a.coverage_fraction - b.joules), bar, context)
        self.assertIn(f"runs_retained={len(runs)}", a.flags, context)
        return a, b, abs(a.joules * a.coverage_fraction - b.joules) / bar

    def test_offset_plans_agree_where_both_tile_without_repeats(self) -> None:
        for period in (100 * MS, 1_000_000_000, 33_333_333, 99_999_999):
            for duty in (1.0, 0.5, 0.25, 0.125, 0.0625):
                repeats = round(1 / duty)
                self.assertEqual(lane.plan_offsets(period, duty, repeats),
                                 twin.plan_offsets(period, duty, repeats),
                                 (period, duty))  # integers: identity is the property

    def test_both_offset_plans_tile_when_repeats_exceed_phases(self) -> None:
        for period in (100 * MS, 99_999_999):
            for duty in (0.5, 0.25, 0.2):
                window = math.ceil(duty * period)
                for repeats in range(math.ceil(1 / duty), 33):
                    for plan in (lane.plan_offsets(period, duty, repeats),
                                 twin.plan_offsets(period, duty, repeats)):
                        self.assertEqual(len(plan), repeats)
                        self.assertTrue(tiles(plan, period, window), (period, duty, repeats, plan))

    def test_student_t_quantiles_agree(self) -> None:
        for dof in range(1, 61):
            a = lane._student_quantile(0.975, dof)
            b = twin.student_t_quantile(0.95, dof)
            self.assertLessEqual(abs(a - b), REL * abs(b), dof)

    def test_tiled_worlds_agree(self) -> None:
        worst = 0.0
        for seed in range(24):
            rng = random.Random(seed)
            wave = agent_waveform(rng, turns=rng.randint(1, 4))
            for repeats in (4, 8, 12, 16):
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3,
                                    label=f"phase-{offset}")
                        for offset in lane.plan_offsets(PERIOD, 0.25, repeats)]
                a, b, ratio = self.assert_agree(runs, (seed, repeats))
                self.assertEqual(b.coverage_fraction, 1.0)  # the plan tiles (integer geometry)
                worst = max(worst, ratio)
        print("TWIN nvml r2 tiled worlds: worst |dJ| / bar =", worst)

    def test_jittered_replays_keep_every_run_and_agree(self) -> None:
        # F1 regression: dispatch jitter 0-2 ms and measured durations that
        # differ by up to +-300 us (the round-1 sampler-chain figure).
        worst = 0.0
        for seed in range(16):
            rng = random.Random(300 + seed)
            wave = agent_waveform(rng, turns=rng.randint(1, 4))
            for repeats in (8, 16):
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3,
                                    start_jitter_ns=rng.randint(0, 2 * MS),
                                    duration_jitter_ns=rng.randint(-300_000, 300_000),
                                    label=f"phase-{offset}")
                        for offset in lane.plan_offsets(PERIOD, 0.25, repeats)]
                a, b, ratio = self.assert_agree(runs, (seed, repeats))
                self.assertIn("durations_differ", a.flags)
                self.assertIn("durations_differ", b.flags)
                self.assertTrue(math.isfinite(a.half_width_j), a)
                worst = max(worst, ratio)
        print("TWIN nvml r2 jittered replays: worst |dJ| / bar =", worst)

    def test_partial_coverage_gap_reading_identity(self) -> None:
        worst = 0.0
        for seed in range(16):
            rng = random.Random(1000 + seed)
            wave = agent_waveform(rng, turns=rng.randint(1, 4))
            cases = [(lane.plan_offsets(PERIOD, 0.25, n), None) for n in (1, 2, 3)]
            cases.append((lane.plan_offsets(PERIOD, 0.25, 8), 1300 * MS))  # sampler 1.3 s late
            cases.append(([0] * 8, None))  # offsets not applied: every run in one phase
            for offsets, late in cases:
                runs = [sampled_run(wave, offset, rng, shift_w=rng.gauss(0, 2.0), noise_w=0.3,
                                    label=f"phase-{offset}", first_sample_after_start_ns=late)
                        for offset in offsets]
                a, b, ratio = self.assert_agree(runs, (seed, offsets, late))
                self.assertLess(b.coverage_fraction, 1.0)
                worst = max(worst, ratio)
        print("TWIN nvml r2 partial coverage: worst |dJ| / bar =", worst)

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
                self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))

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

    def test_real_sampler_traces_agree(self) -> None:
        # The lane's NvmlSampler over an A100-shaped ctypes fake: field 186
        # updates every 100 ms with the mean of the last 25 ms and a driver
        # timestamp; t_ns is the mapped window end (F2). Both implementations
        # read only the PowerTrace contract fields here.
        try:
            from joulewise.align.power.nvml import NvmlSampler
            from tests.align.test_power_nvml import FakeNvmlLibrary
        except ImportError:  # pragma: no cover
            self.skipTest("lane sampler not on this tree")
        wall0 = 1_800_000_000_000_000_000
        poll = 10 * MS

        class Sensor(FakeNvmlLibrary):
            def __init__(self, wave: Waveform, start: int, t0: int, t_stop: int) -> None:
                super().__init__()
                self.wave, self.start, self.now, self.t_stop = wave, start, t0, t_stop
                self.clock_lock, self.done, self.cache = threading.Lock(), threading.Event(), {}

            def mono(self) -> int:
                with self.clock_lock:
                    self.now += 137  # each clock read advances the fake clock
                    return self.now

            def wall(self) -> int:
                with self.clock_lock:
                    return wall0 + self.now

            def reading(self) -> tuple[int, int]:
                t = EPOCH + ((self.now - EPOCH) // PERIOD) * PERIOD
                if t not in self.cache:
                    mean = self.wave.integral_w_ns(t - WINDOW - self.start, t - self.start,
                                                   0.0, self.wave.duration) / WINDOW
                    self.cache[t] = round(mean * 1000)
                return t, self.cache[t]

            def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                with self.clock_lock:
                    self.now += poll
                    if self.now >= self.t_stop:
                        self.done.set()
                self._put(output, ctypes.c_uint, self.reading()[1])
                return 0

            def nvmlDeviceGetFieldValues(self, handle: object, count: object, values: object) -> int:
                values = getattr(values, "_obj", values)
                t, mw = self.reading()
                for index in range(int(getattr(count, "value", count))):
                    value = values[index]
                    value.nvmlReturn, value.valueType, value.value.uiVal = 0, 1, mw
                    value.timestamp, value.latencyUsec = (wall0 + t) // 1000, 0
                return 0

        wave = agent_waveform(random.Random(7), turns=2)
        runs = []
        for offset in lane.plan_offsets(PERIOD, 0.25, 8):
            start = EPOCH + 50 * PERIOD + offset
            library = Sensor(wave, start, start - 3 * PERIOD, start + wave.duration + 3 * PERIOD)
            sampler = NvmlSampler(library=library, interval_ns=50_000, clock_domain="host:monotonic",
                                  clock_ns=library.mono, wall_clock_ns=library.wall,
                                  power_bound_w=POWER_BOUND_W, repeat_group=f"phase-{offset}")
            sampler.start()
            self.assertTrue(library.done.wait(timeout=60))  # operational deadlock guard
            trace = next(t for t in sampler.stop() if t.channel.endswith(":power_instant"))
            self.assertTrue(trace.values)
            runs.append((trace, start, start + wave.duration))
        a, b, ratio = self.assert_agree(runs, "sampler chain")
        print("TWIN nvml r2 sampler chain: |dJ| / bar =", ratio, "lane", a.joules, a.half_width_j,
              "twin", b.joules, b.half_width_j, "truth", wave.truth_j())

    @unittest.expectedFailure
    def test_lane_half_width_contains_truth_when_the_sampler_starts_late(self) -> None:
        # Review 2 finding: with 15% of the workload unobserved (sampler 1.3 s
        # late, eight tiled runs, no shift or noise) the lane extrapolates by
        # D/|C| and prints a half-width with no coverage term. The twin's
        # interval contains the truth here; the lane's does not.
        rng = random.Random(42)
        wave = agent_waveform(rng, turns=3)
        runs = [sampled_run(wave, offset, rng, shift_w=0.0, noise_w=0.0, label=f"phase-{offset}",
                            first_sample_after_start_ns=1300 * MS)
                for offset in lane.plan_offsets(PERIOD, 0.25, 8)]
        a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
        truth = wave.truth_j()
        self.assertLessEqual(abs(b.joules - truth), b.half_width_j)  # twin contains it
        self.assertLessEqual(abs(a.joules - truth), a.half_width_j, (a, truth))

    @unittest.expectedFailure
    def test_lane_half_width_contains_truth_on_deterministic_replays(self) -> None:
        # Review 2 finding: deterministic replays (the protocol's premise),
        # eight exactly tiled runs, no run shift, 0.3 W reading noise. The
        # window that straddles the workload end carries idle power; the lane
        # reports that systematic error only in its worst_case_bias_j flag.
        # One-sided bar on the miss fraction: nominal 0.05 plus 4 binomial SE
        # at S seeds (the orchestrator's Monte Carlo rule), 0.188 at S = 40.
        seeds = 40
        bar = 0.05 + 4 * math.sqrt(0.05 * 0.95 / seeds)
        lane_misses = twin_misses = 0
        for seed in range(40, 40 + seeds):
            rng = random.Random(seed)
            wave = agent_waveform(rng, turns=3)
            runs = [sampled_run(wave, offset, rng, shift_w=0.0, noise_w=0.3, label=f"phase-{offset}")
                    for offset in lane.plan_offsets(PERIOD, 0.25, 8)]
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            truth = wave.truth_j()
            lane_misses += abs(a.joules - truth) > a.half_width_j
            twin_misses += abs(b.joules - truth) > b.half_width_j
        print("TWIN nvml r2 deterministic replays: lane misses", lane_misses, "twin misses",
              twin_misses, "of", seeds)
        self.assertLessEqual(twin_misses / seeds, bar)
        self.assertLessEqual(lane_misses / seeds, bar)


if __name__ == "__main__":
    unittest.main()
