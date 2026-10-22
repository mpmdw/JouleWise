"""Lane-vs-twin agreement for the nvml duty-cycle estimator (review round 3).

Runs ``joulewise.align.power.duty`` (lane A2 "nvml", Sol 6.1, head dacdf9c6d)
and ``tests.align.twins.nvml_twin`` (independent twin) on the same seeded,
production-shaped synthetic worlds and compares their outputs. Round 3 uses
worlds written for this review, not the round-2 worlds the lane's fix seat
was given: the sensor's 100 ms update grid has a phase unrelated to the
host-clock period boundary that plan_offsets is scheduled from, decode has
per-token ripple below the window scale, prefills start with a 1-4 ms launch
transient, and run durations vary through tool-wait latency.

Bars (set by the orchestrator, not chosen here):
* an output printed beside a half-width (``joules``) agrees within 1% of the
  smallest finite printed half-width of the implementations compared;
* an output with no printed uncertainty agrees within 1e-6 relative, or 1e-6
  absolute in its own unit when its value is below 1 (``coverage_fraction``);
* integers (offset plans) must be identical: bit identity is the property.

Readings the two implementations take differently, and what is compared:
* Gaps. The twin integrates the covered set only; the lane multiplies the
  pooled integral by M / C. With equal durations both pool the same clipped
  windows, so lane_joules * lane_coverage == twin_joules is the identity.
* Unequal durations. Since round 2 (R2-M2) the lane targets the mean run:
  each aligned span is weighted by the fraction of runs still active. The
  twin still integrates to max D at full weight; that is now a twin defect,
  so the lane is compared to ``mean_run_reference`` below, a third
  implementation written here from the lane's docstring formula.
* Half-width totals have different forms and are not compared. Two worlds
  isolate the terms both define: the resolution term on constant power
  (twin q*|C| = 2 * lane's q/2 per coefficient) and the spread term on a
  d = 1 sensor (both t(0.975, n-1) * D * sd(reading) / sqrt(n)).

The review-3 finding (the boundary term is estimated from 25 ms averages, so
a workload that begins with a feature shorter than one window escapes it) is
recorded as expected failures, so the file flags itself when it is fixed.
"""

from __future__ import annotations

import bisect
import ctypes
import json
import math
import random
import statistics
import threading
import unittest
import warnings

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
EPOCH = 10**15  # a host-clock period boundary in the trace clock

COVERAGE_ABS = 1e-6  # orchestrator bar: value below 1, no printed uncertainty
REL = 1e-6  # orchestrator bar: no printed uncertainty
# Lead's Monte Carlo bar for a bounds-dominated interval at S seeds: the miss
# fraction may not exceed nominal 0.05 by more than 4 binomial standard errors.
NOMINAL_MISS = 0.05


def one_sided_ceiling(seeds: int) -> float:
    return NOMINAL_MISS + 4 * math.sqrt(NOMINAL_MISS * (1 - NOMINAL_MISS) / seeds)


class Wave:
    """Piecewise-constant board power of one run on aligned time u (ns); idle outside [0, D]."""

    def __init__(self, edges: list[int], watts: list[float], idle_w: float) -> None:
        self.edges, self.watts, self.idle = edges, watts, idle_w
        self.duration = edges[-1]
        self.prefix = [0.0]
        for a, b, w in zip(edges, edges[1:], watts):
            self.prefix.append(self.prefix[-1] + w * (b - a))

    def _inside(self, a: int, b: int) -> float:
        if b <= a:
            return 0.0
        i = bisect.bisect_right(self.edges, a) - 1
        j = bisect.bisect_right(self.edges, b) - 1
        if i == j:
            return self.watts[i] * (b - a)
        total = self.watts[i] * (self.edges[i + 1] - a) + (self.prefix[j] - self.prefix[i + 1])
        if j < len(self.watts):
            total += self.watts[j] * (b - self.edges[j])
        return total

    def integral_w_ns(self, a: int, b: int, shift_w: float = 0.0) -> float:
        total = 0.0
        if a < 0:
            total += self.idle * (min(b, 0) - a)
        if b > self.duration:
            total += self.idle * (b - max(a, self.duration))
        lo, hi = max(a, 0), min(b, self.duration)
        if hi > lo:
            total += self._inside(lo, hi) + shift_w * (hi - lo)
        return total

    def truth_j(self) -> float:
        return self._inside(0, self.duration) / 1e9


def make_script(rng: random.Random, turns: int, *, short_first: bool = False,
                short_decode: bool = False) -> dict:
    """A deterministic agent episode (what each replay repeats), small model on an A100-class board.

    Per turn: prefill of 300-3000 tokens at ~10k tokens/s (30-300 ms, 300-390 W)
    or, for half of the follow-up turns, a short 60-400 token tool result;
    a 1-4 ms launch transient 30-80 W above the prefill level; decode of
    20-300 tokens (3-40 if short_decode) at 15-35 ms per token on a 190-250 W
    plateau, each token 75% compute at +a and 25% sampling/sync at -3a
    (a = 5-30 W); a 80-1500 ms tool wait at 65-90 W between turns; idle
    50-60 W. short_first: the system prompt is in the prefix cache and only a
    60-200 token user message is prefilled (6-20 ms).
    """
    script = {"idle": rng.uniform(50, 60), "tool": rng.uniform(65, 90), "turns": []}
    for k in range(turns):
        tokens = rng.randint(60, 400) if (k > 0 and rng.random() < 0.5) else rng.randint(300, 3000)
        if short_first and k == 0:
            tokens = rng.randint(60, 200)
        prefill_w = rng.uniform(300, 390)
        script["turns"].append({
            "prefill_ns": int(tokens / 10000 * 1e9) + rng.randint(1, 999), "prefill_w": prefill_w,
            "spike": (rng.randint(1 * MS, 4 * MS), prefill_w + rng.uniform(30, 80)),
            "decode": rng.randint(3, 40) if short_decode else rng.randint(20, 300),
            "token_ns": rng.randint(15 * MS, 35 * MS) + rng.randint(1, 999),
            "base": rng.uniform(190, 250), "amp": rng.uniform(5, 30),
            "tool_ns": rng.randint(80 * MS, 1500 * MS) + rng.randint(1, 999) if k < turns - 1 else 0})
    return script


def realize(script: dict, rng: random.Random | None, tool_jitter_ns: int = 0) -> Wave:
    """One replay; tool-wait latency varies by up to +-tool_jitter_ns (duration variation)."""
    edges, watts = [0], []

    def seg(length: int, level: float) -> None:
        if length > 0:
            edges.append(edges[-1] + length)
            watts.append(level)

    for turn in script["turns"]:
        spike_ns, spike_w = turn["spike"]
        seg(spike_ns, spike_w)
        seg(max(turn["prefill_ns"] - spike_ns, 1), turn["prefill_w"])
        high = int(turn["token_ns"] * 0.75)
        for _ in range(turn["decode"]):
            seg(high, turn["base"] + turn["amp"])
            seg(turn["token_ns"] - high, turn["base"] - 3 * turn["amp"])
        if turn["tool_ns"]:
            jitter = rng.randint(-tool_jitter_ns, tool_jitter_ns) if (rng and tool_jitter_ns) else 0
            seg(turn["tool_ns"] + jitter, script["tool"])
    return Wave(edges, watts, script["idle"])


def sampled_run(wave: Wave, start: int, phi: int, rng: random.Random, *, shift_w: float = 0.0,
                noise_w: float = 0.3, label: str | None = None, window: int = WINDOW,
                period: int = PERIOD, roll_ns: int = 300 * MS, first_after_ns: int | None = None,
                timing_ns: int = 3000) -> tuple[PowerTrace, int, int]:
    """Sensor windows of ``window`` ns ending at EPOCH + phi + k*period, around one run.

    Each reading is the exact window mean of the run's power plus Gaussian
    noise, rounded to the NVML milliwatt. t_ns is the reported window end,
    within +-timing_ns of the true end; the notes carry it as the mapped
    driver endpoint with that half-width (the sampler's notes shape).
    """
    end = start + wave.duration
    k0 = (start - roll_ns - EPOCH - phi) // period
    k1 = (end + roll_ns - EPOCH - phi) // period + 1
    times, values = [], []
    for k in range(k0, k1 + 1):
        t = EPOCH + phi + k * period
        if t < start - roll_ns or t > end + roll_ns:
            continue
        if first_after_ns is not None and t - start < first_after_ns:
            continue
        mean = wave.integral_w_ns(t - window - start, t - start, shift_w) / window
        if noise_w:
            mean += rng.gauss(0.0, noise_w)
        reported = t + (rng.randint(-timing_ns, timing_ns) if timing_ns else 0)
        if times and reported <= times[-1]:
            reported = times[-1] + 1
        times.append(reported)
        values.append(max(round(mean / QUANTUM) * QUANTUM, 0.0))
    notes = {"flags": ["driver_field_timestamp_is_wall_clock"], "window_end_ns": times,
             "window_timing_half_width_ns": [timing_ns] * len(times)}
    if label is not None:
        notes["repeat_group"] = label
    trace = PowerTrace("nvml_power", "gpu0:power_instant", "host:monotonic", tuple(times),
                       tuple(values), "W", 10 * MS, window, window / period, QUANTUM,
                       json.dumps(notes))
    return trace, start, end


def session(script: dict, rng: random.Random, offsets: list[int], *, phi: int | None = None,
            shift_sd: float = 0.0, start_jitter_ns: int = 1 * MS, tool_jitter_ns: int = 0,
            labels: bool = True, **kw) -> list[tuple[PowerTrace, int, int]]:
    """Replays at the planned offsets from host-clock period boundaries; one sensor phase phi."""
    phi = rng.randrange(PERIOD) if phi is None else phi
    runs = []
    for index, offset in enumerate(offsets):
        wave = realize(script, rng, tool_jitter_ns)
        start = (EPOCH + (index + 10) * 37 * PERIOD + offset
                 + (rng.randint(0, start_jitter_ns) if start_jitter_ns else 0))
        runs.append(sampled_run(wave, start, phi, rng,
                                shift_w=rng.gauss(0.0, shift_sd) if shift_sd else 0.0,
                                label=f"phase-{offset}" if labels else None, **kw))
    return runs


def plan(repeats: int) -> list[int]:
    with warnings.catch_warnings():  # under-tiled plans warn; partial coverage is the point
        warnings.simplefilter("ignore", RuntimeWarning)
        return lane.plan_offsets(PERIOD, 0.25, repeats)


def mean_run_reference(runs: list[tuple[PowerTrace, int, int]]) -> tuple[float, float]:
    """The lane docstring's mean-run estimand, implemented here independently.

    A(u) = fraction of runs with D_r > u; p(u) = mean reading of the windows
    (each clipped to its own run's [0, D_r]) that cover u. Returns
    (integral over covered u of A(u) * p(u) in J, integral over covered u of
    A(u) / mean(D_r)). The lane's joules * coverage must equal the first and
    its coverage the second.
    """
    durations = [end - start for _, start, end in runs]
    pieces = []
    for trace, start, end in runs:
        for t, value in zip(trace.t_ns, trace.values):
            a, b = max(t - trace.averaging_window_ns - start, 0), min(t - start, end - start)
            if b > a:
                pieces.append((a, b, value))
    cuts = sorted({0, *durations, *(a for a, _, _ in pieces), *(b for _, b, _ in pieces)})
    entering: dict[int, list[int]] = {}
    for index, (a, _, _) in enumerate(pieces):
        entering.setdefault(a, []).append(index)
    active_pieces: set[int] = set()
    energy, covered = [], []
    for left, right in zip(cuts, cuts[1:]):
        active_pieces |= set(entering.get(left, ()))
        active_pieces = {i for i in active_pieces if pieces[i][1] > left}
        readings = [pieces[i][2] for i in active_pieces]
        if not readings:
            continue
        active = sum(d > left for d in durations) / len(durations)
        energy.append(active * math.fsum(readings) / len(readings) * (right - left))
        covered.append(active * (right - left))
    return math.fsum(energy) / 1e9, math.fsum(covered) / statistics.fmean(durations)


def joules_bar(*estimates) -> float:
    """1% of the smallest finite printed half-width, else 1e-6 relative."""
    widths = [e.half_width_j for e in estimates if math.isfinite(e.half_width_j) and e.half_width_j > 0]
    if widths:
        return 0.01 * min(widths)
    return REL * max(abs(e.joules) for e in estimates)


def tiles(offsets: list[int], period: int, window: int) -> bool:
    """True when windows [o, o + window) mod period cover the whole period (integers)."""
    starts = sorted({o % period for o in offsets})
    gaps = [b - a for a, b in zip(starts, starts[1:])] + [starts[0] + period - starts[-1]]
    return max(gaps) <= window


@unittest.skipUnless(lane is not None,
                     "joulewise.align.power.duty (lane nvml) is not on this tree; run on a merge of both")
class TwinAgreementTests(unittest.TestCase):
    def assert_equal_duration_agreement(self, runs, context) -> float:
        a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
        context = (context, a, b)
        self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), COVERAGE_ABS, context)
        bar = joules_bar(a, b)
        # Gap reading: the lane fills uncovered time by M / C, the twin does
        # not; lane * coverage is the pooled integral both define.
        self.assertLessEqual(abs(a.joules * a.coverage_fraction - b.joules), bar, context)
        self.assertIn(f"runs_retained={len(runs)}", a.flags, context)
        return abs(a.joules * a.coverage_fraction - b.joules) / bar

    def test_offset_plans_agree_where_both_tile_without_repeats(self) -> None:
        for period in (100 * MS, 1_000_000_000, 33_333_333, 99_999_999):
            for duty in (1.0, 0.5, 0.25, 0.2, 0.125, 0.1, 0.0625):
                repeats = round(1 / duty)
                self.assertEqual(lane.plan_offsets(period, duty, repeats),
                                 twin.plan_offsets(period, duty, repeats), (period, duty))

    def test_both_offset_plans_tile_when_repeats_exceed_phases(self) -> None:
        for period in (100 * MS, 99_999_999):
            for duty in (0.5, 0.3, 0.25, 0.2):
                window = math.ceil(duty * period)
                for repeats in range(math.ceil(1 / duty), 33):
                    for offsets in (lane.plan_offsets(period, duty, repeats),
                                    twin.plan_offsets(period, duty, repeats)):
                        self.assertEqual(len(offsets), repeats)
                        self.assertTrue(tiles(offsets, period, window), (period, duty, repeats))

    def test_under_tiled_plans_warn_in_the_lane_and_raise_in_the_twin(self) -> None:
        for repeats in (1, 2, 3):
            with self.assertWarns(RuntimeWarning):
                self.assertEqual(len(lane.plan_offsets(PERIOD, 0.25, repeats)), repeats)
            with self.assertRaises(ValueError):
                twin.plan_offsets(PERIOD, 0.25, repeats)

    def test_student_t_quantiles_agree(self) -> None:
        for dof in range(1, 61):
            a = lane._student_quantile(0.975, dof)
            b = twin.student_t_quantile(0.95, dof)
            self.assertLessEqual(abs(a - b), REL * abs(b), dof)

    def test_equal_duration_worlds_agree(self) -> None:
        # Random sensor phase, launch transients, sub-window decode ripple,
        # dispatch jitter 0-1 ms, run shifts 0-2 W, 0.3 W noise; 4 to 16
        # replays; plus under-tiled plans, a sampler that starts 1.3 s late
        # and unapplied offsets (all runs in one phase): partial coverage.
        worst = 0.0
        for seed in range(30):
            rng = random.Random(3000 + seed)
            script = make_script(rng, rng.randint(1, 4), short_first=rng.random() < 0.3)
            for repeats, late, offsets in ((4, None, None), (8, None, None), (16, None, None),
                                           (2, None, None), (8, 1300 * MS, None), (8, None, [0] * 8)):
                runs = session(script, rng, offsets or plan(repeats),
                               shift_sd=rng.choice((0.0, 0.5, 2.0)), first_after_ns=late,
                               labels=rng.random() < 0.8)
                worst = max(worst, self.assert_equal_duration_agreement(runs, (seed, repeats, late)))
        print("TWIN nvml r3 equal-duration worlds: worst |dJ| / bar =", worst)

    def test_unequal_duration_worlds_match_the_mean_run_reference(self) -> None:
        # Tool-wait latency varies +-5 to +-50 ms per wait, so turns after a
        # tool wait move and durations differ. The twin targets max D here
        # (a twin defect since R2-M2); the lane must match the reference.
        worst = 0.0
        twin_gap = []
        for seed in range(24):
            rng = random.Random(4000 + seed)
            script = make_script(rng, rng.randint(2, 4))
            for repeats in (8, 16):
                runs = session(script, rng, plan(repeats), shift_sd=0.5,
                               tool_jitter_ns=rng.choice((5, 20, 50)) * MS)
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                expected_j, expected_cov = mean_run_reference(runs)
                context = (seed, repeats, a, expected_j, expected_cov)
                self.assertIn("durations_differ", a.flags)
                self.assertLessEqual(abs(a.coverage_fraction - expected_cov), COVERAGE_ABS, context)
                bar = joules_bar(a, b)
                self.assertLessEqual(abs(a.joules * a.coverage_fraction - expected_j), bar, context)
                worst = max(worst, abs(a.joules * a.coverage_fraction - expected_j) / bar)
                twin_gap.append(b.joules - expected_j)
        print("TWIN nvml r3 unequal durations: lane worst |dJ| / bar =", worst,
              "; twin minus mean-run reference (twin max-D defect), median J:",
              statistics.median(twin_gap))

    def test_resolution_terms_agree_on_constant_power(self) -> None:
        # Constant power equal to idle (no boundary contrast, observed range
        # 0), D a multiple of 25 ms, sensor phase 0, no noise, no timing
        # error: the kernel is exactly one on [0, D]. Twin: q * |C|. Lane:
        # sum(c_i) * q / 2 = q * D / 2, and every other lane term is zero.
        for level in (61.234, 213.457, 377.001):
            for windows in (40, 241, 1203):
                duration = windows * WINDOW
                wave = Wave([0, duration], [level], level)
                runs = [sampled_run(wave, EPOCH + 50 * PERIOD + o, 0, random.Random(0), noise_w=0.0,
                                    timing_ns=0, label=f"phase-{o}") for o in plan(8)]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                self.assertLessEqual(abs(2 * a.half_width_j - b.half_width_j),
                                     REL * b.half_width_j, (level, windows, a, b))
                expected = QUANTUM * duration / 1e9
                self.assertLessEqual(abs(b.half_width_j - expected), REL * expected)
                self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))

    def test_spread_terms_agree_on_a_single_phase_sensor(self) -> None:
        # A sensor averaging its whole period (d = 1), constant power equal to
        # idle, D a whole number of periods: all runs share one geometry.
        # Lane: one group, dof n-1; twin: E_r = D v_r. Both give
        # t(0.975, n-1) * D * sd(v) / sqrt(n), on top of their resolution terms.
        for seed in range(12):
            rng = random.Random(500 + seed)
            for n in (2, 3, 5, 8, 16):
                duration = rng.randint(10, 300) * PERIOD
                level = rng.uniform(60, 380)
                wave = Wave([0, duration], [level], level)
                runs = [sampled_run(wave, EPOCH + 50 * PERIOD + o, 0, rng, shift_w=rng.gauss(0, 2.0),
                                    noise_w=0.0, window=PERIOD, timing_ns=0)
                        for o in lane.plan_offsets(PERIOD, 1.0, n)]
                a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
                resolution_twin = QUANTUM * duration / 1e9
                spread_lane = a.half_width_j - resolution_twin / 2
                spread_twin = b.half_width_j - resolution_twin
                self.assertGreater(spread_twin, 0.0)
                self.assertLessEqual(abs(spread_lane - spread_twin), REL * spread_twin, (seed, n, a, b))
                self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))

    def test_real_sampler_traces_agree_and_contain_the_truth(self) -> None:
        # The lane's NvmlSampler over an A100-shaped ctypes fake: field 186
        # updates every 100 ms (phase 37 ms from the host period boundary)
        # with the mean of the last 25 ms and a driver timestamp; t_ns is the
        # mapped window end. Both implementations read only PowerTrace fields.
        try:
            from joulewise.align.power.nvml import NvmlSampler
            from tests.align.test_power_nvml import FakeNvmlLibrary
        except ImportError:  # pragma: no cover
            self.skipTest("lane sampler not on this tree")
        wall0 = 1_800_000_000_000_000_000
        phi = 37 * MS

        class Sensor(FakeNvmlLibrary):
            def __init__(self, wave: Wave, start: int, t0: int, t_stop: int) -> None:
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
                t = EPOCH + phi + ((self.now - EPOCH - phi) // PERIOD) * PERIOD
                if t not in self.cache:
                    mean = self.wave.integral_w_ns(t - WINDOW - self.start, t - self.start) / WINDOW
                    self.cache[t] = round(mean * 1000)
                return t, self.cache[t]

            def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                with self.clock_lock:
                    self.now += 10 * MS
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

        wave = realize(make_script(random.Random(11), 2, short_decode=True), None)
        runs = []
        for offset in plan(8):
            start = EPOCH + 50 * PERIOD + offset
            library = Sensor(wave, start, start - 3 * PERIOD, start + wave.duration + 3 * PERIOD)
            sampler = NvmlSampler(library=library, interval_ns=50_000, clock_domain="host:monotonic",
                                  clock_ns=library.mono, wall_clock_ns=library.wall,
                                  repeat_group=f"phase-{offset}")
            sampler.start()
            self.assertTrue(library.done.wait(timeout=60))  # operational deadlock guard
            trace = next(t for t in sampler.stop() if t.channel.endswith(":power_instant"))
            self.assertTrue(trace.values)
            runs.append((trace, start, start + wave.duration))
        ratio = self.assert_equal_duration_agreement(runs, "sampler chain")
        a = lane.estimate_energy(runs)
        print("TWIN nvml r3 sampler chain: |dJ| / bar =", ratio, "lane", a.joules, a.half_width_j,
              "truth", wave.truth_j())
        self.assertLessEqual(abs(a.joules - wave.truth_j()), a.half_width_j)

    def test_round2_regressions_stay_fixed(self) -> None:
        # R2-B1: sampler 1.3 s late (15% unobserved), eight tiled runs, no
        # shift or noise. R2-M1: deterministic replays with a decode-to-idle
        # end, 0.3 W noise, one-sided ceiling at S = 40 seeds.
        rng = random.Random(42)
        script = make_script(rng, 3)
        runs = session(script, rng, plan(8), first_after_ns=1300 * MS, noise_w=0.0)
        a = lane.estimate_energy(runs)
        truth = realize(script, None).truth_j()
        self.assertLessEqual(abs(a.joules - truth), a.half_width_j, (a, truth))
        seeds, misses = 40, 0
        for seed in range(seeds):
            rng = random.Random(5000 + seed)
            script = make_script(rng, 3)
            a = lane.estimate_energy(session(script, rng, plan(8)))
            misses += abs(a.joules - realize(script, None).truth_j()) > a.half_width_j
        self.assertLessEqual(misses / seeds, one_sided_ceiling(seeds), misses)

    @unittest.expectedFailure
    def test_lane_half_width_contains_truth_when_a_short_prefill_starts_the_workload(self) -> None:
        # Review-3 finding, exact world (no noise, no jitter, no shift): idle
        # 55 W; 10 ms prefill at 350 W, then 200 W decode to D = 1.2345 s;
        # sensor windows end 12.5 ms after each host period boundary; 16
        # replays. Every start-straddling window has inside length 12.5 ms:
        # y = (12.5*55 + 10*350 + 2.5*200)/25 = 187.5 W, so the start edge is
        # off by 12.5*187.5 - 4000 = -1656.25 W*ms. The lane's start term is
        # 12.5 * (1 - 0.5) * R_b with R_b = 200 - 55 = 145 W from the nearest
        # 25 ms averages: 906.25 W*ms. The 25 ms averages never see 350 W.
        # Lane: 246.361 +- 1.290 J; truth 248.400 J.
        duration = 1_234_500_000
        wave = Wave([0, 10 * MS, duration], [350.0, 200.0], 55.0)
        runs = [sampled_run(wave, EPOCH + 50 * PERIOD + o, 12_500_000, random.Random(0),
                            noise_w=0.0, timing_ns=0, label=f"phase-{o}") for o in plan(16)]
        a = lane.estimate_energy(runs)
        self.assertLessEqual(abs(a.joules - wave.truth_j()), a.half_width_j, (a, wave.truth_j()))

    @unittest.expectedFailure
    def test_lane_half_width_calibrates_on_one_turn_short_prefill_replays(self) -> None:
        # Review-3 finding, production-shaped: one model call whose system
        # prompt is prefix-cached (6-20 ms prefill), 20-300 decode tokens,
        # 0.3 W noise, 0-1 ms dispatch jitter, random sensor phase, the
        # runbook's 16 replays. The reviewer's 400-seed run gives 206 misses;
        # the one-sided ceiling at S = 40 is 0.188 (7 misses).
        seeds, misses = 40, 0
        for seed in range(seeds):
            rng = random.Random(6000 + seed)
            script = make_script(rng, 1, short_first=True)
            a = lane.estimate_energy(session(script, rng, plan(16)))
            misses += abs(a.joules - realize(script, None).truth_j()) > a.half_width_j
        print("TWIN nvml r3 one-turn short-prefill replays: lane misses", misses, "of", seeds)
        self.assertLessEqual(misses / seeds, one_sided_ceiling(seeds), misses)


if __name__ == "__main__":
    unittest.main()
