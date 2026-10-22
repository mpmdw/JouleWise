"""Lane-vs-twin agreement for the nvml duty-cycle estimator (review round 3).

Runs ``joulewise.align.power.duty`` (lane A2 "nvml", head dacdf9c6d) and
``tests.align.twins.nvml_twin`` (independent twin, a54570f49) on the same seeded,
production-shaped synthetic worlds and compares the outputs both define.

Worlds (reviewer 3's own generator, below): a multi-turn agent episode on an
A100/H100-class board. Each turn is request overhead with the GPU near idle, a
prefill burst at 300-400 W (50-6000 tokens at 5-12 k tokens/s), decode on a
190-250 W plateau with a per-token ripple of 5-30 W (30-60 tokens/s), and a tool
wait in which power decays from the decode level towards a 65-90 W floor. Idle
is 50-65 W. The sensor reports, every 100 ms, the mean over the 25 ms ending at
its timestamp, plus 0.3 W read noise, rounded to the NVML milliwatt; t_ns is
the window end and the notes are shaped like NvmlSampler's power_instant
notes. Replays use plan_offsets(100 ms, 0.25, 8) with repeat_group labels.

Bars (set by the orchestrator, not chosen here):
* an output printed beside a half-width (``joules``) agrees within 1% of the
  smallest finite printed half-width of the two implementations for that world;
* an output with no printed uncertainty agrees within 1e-6 relative, or 1e-6
  absolute in its own unit when its value is below 1 (``coverage_fraction``,
  the Student t quantile, the resolution and spread terms);
* integers (offset plans) are identical: bit identity is the property.

Where the implementations read an open point of the brief differently, the
comparison is made on the quantity both readings define:
* Gaps. The twin (R6) integrates the covered set only; the lane multiplies the
  pooled integral by M/C. Both pool the same clipped windows, so with equal
  durations lane_joules * coverage == twin_joules.
* Unequal durations. The twin (R5, R7) targets the longest replay; the lane
  weights each aligned span by the fraction A(u) of runs still active and
  targets the mean run. The lane's composition is rebuilt here from the twin's
  own primitives (sample_windows, pooled_integral) split at every run end, and
  the lane must match it.
* Half-width totals differ by design (the twin adds P_max * gap, q * |C| and a
  cross-run t term; the lane adds observed-range bounds, q/2 and a per-phase
  Welch term), so only shared terms are compared: the resolution term on full
  coverage (twin = 2 * lane, q against q/2) and the spread term on a d = 1
  sensor where both reduce to t(0.975, n-1) * D * stdev(run mean power) / sqrt(n).

One lane defect found by review 3 is recorded as an expected failure, so the
file flags itself when the lane is fixed: the boundary bound is computed from
25 ms window averages and does not contain a deterministic replay whose first
8 ms is a burst (hand-computed in test_boundary_bound_contains_a_sub_window_start_burst).
"""

from __future__ import annotations

import bisect
import json
import math
import random
import statistics
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
GRID = 10**15  # a sensor-period boundary in the trace clock

REL = 1e-6  # orchestrator bar: no printed uncertainty
ABS_BELOW_ONE = 1e-6  # orchestrator bar: value below 1, no printed uncertainty
SEEDS = 30  # worlds per agreement test; each must pass, so this is a sweep size, not a bar


class Wave:
    """Piecewise-constant board power on aligned time (ns); idle before 0, a decaying tail after D."""

    def __init__(self, edges: list[int], watts: list[float], idle_w: float, tail_w: float, tau_ns: float) -> None:
        self.edges, self.watts, self.idle, self.tail_w, self.tau = edges, watts, idle_w, tail_w, tau_ns
        self.duration = edges[-1]
        self.prefix = [0.0]
        for a, b, w in zip(edges, edges[1:], watts):
            self.prefix.append(self.prefix[-1] + w * (b - a))

    def _inside(self, a: int, b: int) -> float:
        i = bisect.bisect_right(self.edges, a) - 1
        j = bisect.bisect_right(self.edges, b) - 1
        if i == j or j >= len(self.watts):
            parts, x = [], a
            while x < b:
                right = min(self.edges[i + 1], b)
                parts.append(self.watts[i] * (right - x))
                x, i = right, i + 1
            return math.fsum(parts)
        return math.fsum((self.watts[i] * (self.edges[i + 1] - a), self.prefix[j] - self.prefix[i + 1],
                          self.watts[j] * (b - self.edges[j])))

    def integral(self, a: int, b: int) -> float:
        """W*ns over aligned [a, b]."""
        parts = []
        if a < 0:
            parts.append(self.idle * (min(b, 0) - a))
        lo, hi = max(a, 0), min(b, self.duration)
        if hi > lo:
            parts.append(self._inside(lo, hi))
        if b > self.duration:  # after the end: exponential decay of the last level to idle
            x0, x1 = max(a, self.duration) - self.duration, b - self.duration
            excess = self.tail_w - self.idle
            parts.append(self.idle * (x1 - x0) + excess * self.tau * (math.exp(-x0 / self.tau) - math.exp(-x1 / self.tau)))
        return math.fsum(parts)

    def truth_j(self) -> float:
        return self._inside(0, self.duration) / 1e9


def episode(rng: random.Random, turns: int) -> tuple[list[tuple[int, int, int, int]], dict[str, float]]:
    """A replay script (overhead ns, prefill tokens, decode tokens, tool wait ns) and machine constants."""
    script = []
    for k in range(turns):
        wait = rng.randint(50 * MS, 1500 * MS) if k < turns - 1 else 0
        script.append((rng.randint(2 * MS, 10 * MS), rng.randint(1500, 6000) if k == 0 else rng.randint(50, 3000),
                       rng.randint(5, 150), wait))
    machine = dict(prefill_rate=rng.uniform(5000, 12000), decode_rate=rng.uniform(30, 60),
                   prefill_w=rng.uniform(300, 400), decode_w=rng.uniform(190, 250), ripple_w=rng.uniform(5, 30),
                   tool_floor_w=rng.uniform(65, 90), tau_ns=rng.uniform(50, 250) * MS, idle_w=rng.uniform(50, 65))
    return script, machine


def realize(script, machine, rng: random.Random, *, shift_w: float, tool_jitter_ns: int) -> Wave:
    """One replay's power: the script's phases plus this run's shift and tool-latency jitter."""
    edges, watts = [0], []
    m = machine

    def seg(length: float, level: float) -> None:
        edges.append(edges[-1] + max(1, int(length)))
        watts.append(level)

    for k, (overhead, prefill, decode, wait) in enumerate(script):
        seg(overhead, m["idle_w"] + 8 + shift_w)
        seg(prefill / m["prefill_rate"] * 1e9 + 1 + (k * 7919) % 997, m["prefill_w"] + shift_w)
        token = 1e9 / m["decode_rate"]
        for _ in range(decode):
            seg(0.6 * token, m["decode_w"] + m["ripple_w"] / 2 + shift_w)
            seg(0.4 * token, m["decode_w"] - m["ripple_w"] / 2 + shift_w)
        if wait:
            wait += int(rng.gauss(0, tool_jitter_ns)) if tool_jitter_ns else 0
            level, t = m["decode_w"] + shift_w, 0
            while t < wait:
                step = min(10 * MS, wait - t)
                seg(step, m["tool_floor_w"] + (level - m["tool_floor_w"]) * math.exp(-(t + step / 2) / m["tau_ns"]))
                t += step
    return Wave(edges, watts, m["idle_w"], m["decode_w"] + shift_w, m["tau_ns"])


def sense(wave: Wave, start: int, rng: random.Random, *, label: str | None, noise_w: float = 0.3,
          window: int = WINDOW, period: int = PERIOD, late_ns: int | None = None) -> PowerTrace:
    """The sensor beside one replay, with 1.5 s pre- and post-roll, as NvmlSampler's power_instant emits it."""
    end = start + wave.duration
    times, values = [], []
    for k in range((start - 1500 * MS - GRID) // period, (end + 1500 * MS - GRID) // period + 2):
        t = GRID + k * period
        if late_ns is not None and t - start < late_ns:
            continue
        mean = wave.integral(t - window - start, t - start) / window + (rng.gauss(0, noise_w) if noise_w else 0.0)
        times.append(t)
        values.append(round(mean / QUANTUM) * QUANTUM)
    n = len(times)
    notes = {"format": "joulewise.align.nvml.v1", "measurement": "power_instant",
             "flags": ["driver_field_timestamp_is_wall_clock", "resolution_is_quantum_not_accuracy"],
             "window_end_ns": times, "window_timing_half_width_ns": [0] * n, "timing_half_width_ns": [25000] * n,
             "power_bound_w": None, "repeat_group": label}
    return PowerTrace("nvml_power", "gpu0:power_instant", "host:monotonic", tuple(times), tuple(values), "W",
                      period, window, window / period, QUANTUM, json.dumps(notes))


def replays(seed: int, *, repeats: int = 8, turns: int | None = None, shift_w: float = 1.0, start_jitter_ns: int = 0,
            tool_jitter_ns: int = 0, late_ns: int | None = None, window: int = WINDOW,
            same_label: bool = False) -> tuple[list[tuple[PowerTrace, int, int]], list[float]]:
    rng = random.Random(seed)
    script, machine = episode(rng, turns if turns is not None else rng.randint(1, 4))
    duty = window / PERIOD
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        offsets = lane.plan_offsets(PERIOD, duty, repeats)
    runs, truths = [], []
    for i, offset in enumerate(offsets):
        wave = realize(script, machine, rng, shift_w=rng.gauss(0, shift_w) if shift_w else 0.0,
                       tool_jitter_ns=tool_jitter_ns)
        start = GRID + (60 + 200 * i) * PERIOD + offset + (rng.randint(0, start_jitter_ns) if start_jitter_ns else 0)
        label = "phase-0" if same_label else f"phase-{offset}"
        runs.append((sense(wave, start, rng, label=label, window=window, late_ns=late_ns), start, start + wave.duration))
        truths.append(wave.truth_j())
    return runs, truths


def joules_bar(a, b) -> float:
    """Orchestrator bar: 1% of the smallest finite printed half-width, else 1e-6 relative."""
    widths = [w for w in (a.half_width_j, b.half_width_j) if math.isfinite(w) and w > 0]
    return 0.01 * min(widths) if widths else REL * max(abs(a.joules), abs(b.joules))


def coverage_bar(value: float) -> float:
    """Orchestrator bar for an output without a printed uncertainty."""
    return ABS_BELOW_ONE if abs(value) < 1 else REL * abs(value)


def flag_value(flags: tuple[str, ...], name: str) -> float:
    return float(next(f.split("=", 1)[1] for f in flags if f.startswith(name + "=")))


def active_weighted_reference(runs) -> tuple[float, float, float]:
    """The lane's documented target rebuilt from twin primitives: (I [J], C [s], M [s]).

    Each run's windows are clipped to its own workload by twin.sample_windows. The aligned
    axis is split at every run end; on span k the fraction A_k of runs still active weights
    the twin's pooled integral and covered length of the windows clipped to that span.
    """
    per_run, durations = [], []
    for trace, start, end in runs:
        per_run.append(twin.sample_windows(trace.t_ns, trace.values, trace.averaging_window_ns, start, end))
        durations.append(end - start)
    pooled = [w for ws in per_run for w in ws]
    cuts = [0] + sorted(set(durations))
    integral, covered = [], []
    for lo, hi in zip(cuts, cuts[1:]):
        active = sum(d >= hi for d in durations) / len(durations)
        clipped = [(max(a, lo), min(b, hi), y) for a, b, y in pooled if min(b, hi) > max(a, lo)]
        piece, length = twin.pooled_integral(clipped)
        integral.append(active * piece)
        covered.append(active * length)
    return math.fsum(integral) / 1e9, math.fsum(covered) / 1e9, statistics.fmean(durations) / 1e9


@unittest.skipUnless(lane is not None,
                     "joulewise.align.power.duty (lane nvml) is not on this tree; run on a merge of both")
class TwinAgreementTests(unittest.TestCase):
    def test_offset_plans_identical_where_both_tile_without_repeats(self) -> None:
        for period in (100 * MS, 1_000_000_000, 33_333_333, 99_999_999):
            for parts in (1, 2, 4, 5, 8, 10, 16):
                duty = 1 / parts
                self.assertEqual(lane.plan_offsets(period, duty, parts), twin.plan_offsets(period, duty, parts),
                                 (period, parts))  # integers: identity is the property

    def test_student_t_quantiles_agree(self) -> None:
        for dof in list(range(1, 61)) + [80, 100, 150, 200]:
            a = lane._student_quantile(0.975, dof)
            b = twin.student_t_quantile(0.95, dof)
            self.assertLessEqual(abs(a - b), REL * abs(b), dof)  # no printed uncertainty: 1e-6 relative

    def test_joules_agree_on_exactly_tiled_replays(self) -> None:
        """Full coverage, equal durations: both integrate the same pooled windows over [0, D]."""
        for seed in range(SEEDS):
            runs, truths = replays(1000 + seed, shift_w=1.0)
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            context = (seed, a, b)
            self.assertEqual(b.coverage_fraction, 1.0, context)  # world design: phases tile exactly
            self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), coverage_bar(b.coverage_fraction), context)
            self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b), context)

    def test_pooled_integral_agrees_with_dispatch_jitter_and_a_late_sampler(self) -> None:
        """Partial coverage, equal durations: lane_joules * coverage is the twin's covered integral."""
        partial = 0
        for seed in range(SEEDS):
            late = 1300 * MS if seed % 3 == 0 else None
            runs, truths = replays(2000 + seed, start_jitter_ns=MS, late_ns=late)
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            context = (seed, a, b)
            partial += b.coverage_fraction < 1.0
            self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), coverage_bar(b.coverage_fraction), context)
            self.assertLessEqual(abs(a.joules * a.coverage_fraction - b.joules), joules_bar(a, b), context)
        # World design: jitter or lateness leaves gaps in most worlds (overlapping jitter can still tile).
        self.assertGreater(partial, SEEDS // 2)

    def test_unequal_durations_match_the_active_fraction_composition_of_twin_primitives(self) -> None:
        for seed in range(SEEDS):
            runs, truths = replays(3000 + seed, turns=3, tool_jitter_ns=20 * MS, start_jitter_ns=MS)
            self.assertGreater(len({end - start for _, start, end in runs}), 1)  # world design: durations differ
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            integral, covered, mean_duration = active_weighted_reference(runs)
            context = (seed, a, b, integral, covered, mean_duration)
            self.assertLessEqual(abs(a.coverage_fraction - covered / mean_duration), coverage_bar(covered / mean_duration), context)
            self.assertLessEqual(abs(a.joules - integral * mean_duration / covered), joules_bar(a, b), context)

    def test_resolution_terms_differ_by_the_documented_factor_two(self) -> None:
        """Full coverage: twin q*|C| (rounding mode unknown) against lane sum(c_i) * q/2 = M * q/2."""
        for seed in range(10):
            runs, _ = replays(4000 + seed)
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            twin_term = QUANTUM * (runs[0][2] - runs[0][1]) / 1e9 * b.coverage_fraction
            lane_term = flag_value(a.flags, "resolution_bound_j")
            self.assertLessEqual(abs(twin_term - 2 * lane_term), REL * twin_term, (seed, a.flags))  # 1e-6 relative

    def test_spread_terms_agree_on_a_full_duty_sensor(self) -> None:
        """d = 1: every run covers its whole workload; one phase group; both give t * D * sd(pbar) / sqrt(n)."""
        for seed in range(10):
            runs, _ = replays(5000 + seed, window=PERIOD, shift_w=2.0, same_label=True)
            a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
            self.assertEqual(b.coverage_fraction, 1.0)
            twin_spread = b.half_width_j - QUANTUM * (runs[0][2] - runs[0][1]) / 1e9
            lane_spread = flag_value(a.flags, "repeatability_half_width_j")
            self.assertGreater(lane_spread, 0.0)
            self.assertLessEqual(abs(lane_spread - twin_spread), REL * twin_spread, (seed, a.flags, b))  # 1e-6 relative
            self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b), (seed, a, b))

    @unittest.expectedFailure
    def test_boundary_bound_contains_a_sub_window_start_burst(self) -> None:
        """Review 3 finding: the boundary bound's local range comes from 25 ms averages.

        By hand (no noise, no shift; readings exact in mW): idle 55 W; workload 8 ms at 360 W,
        then 210 W to D = 1987.5 ms; window ends at 12.5 ms + k*25 ms in aligned time over the
        four phases, so only the phase-0 window [-12.5, 12.5] ms straddles an edge.
          truth = (8*360 + 1979.5*210) W*ms = 418.575 J
          straddling reading = (12.5*55 + 8*360 + 4.5*210)/25 = 180.5 W
          error = 12.5*180.5 - (8*360 + 4.5*210) = -1568.75 W*ms = -1.569 J (both implementations)
          lane boundary bound = 12.5*(1 - 12.5/25)*(210 - 55) = 0.969 J; other terms ~0.001 J
        """
        grid = GRID + 12 * MS + MS // 2
        duration = 1987 * MS + MS // 2
        segments = [(0, 8 * MS, 360.0), (8 * MS, duration, 210.0)]

        def mean(a: int, b: int) -> float:
            parts = [55.0 * (min(b, 0) - a)] if a < 0 else []
            parts += [w * (min(b, hi) - max(a, lo)) for lo, hi, w in segments if min(b, hi) > max(a, lo)]
            if b > duration:
                parts.append(55.0 * (b - max(a, duration)))
            return math.fsum(parts) / (b - a)

        runs = []
        for offset in lane.plan_offsets(PERIOD, 0.25, 8):
            start = GRID + 40 * PERIOD + offset
            times = [grid + k * PERIOD for k in range((start - 2 * PERIOD - grid) // PERIOD,
                                                       (start + duration + 2 * PERIOD - grid) // PERIOD + 2)]
            values = [round(mean(t - WINDOW - start, t - start) / QUANTUM) * QUANTUM for t in times]
            notes = {"window_end_ns": times, "window_timing_half_width_ns": [0] * len(times),
                     "repeat_group": f"phase-{offset}"}
            runs.append((PowerTrace("nvml_power", "gpu0:power_instant", "host:monotonic", tuple(times),
                                    tuple(values), "W", PERIOD, WINDOW, 0.25, QUANTUM, json.dumps(notes)),
                         start, start + duration))
        a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
        truth = 418.575
        self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))  # both: 417.00625 J
        self.assertLessEqual(abs(a.joules - truth), a.half_width_j, (a.joules, a.half_width_j, a.flags))


if __name__ == "__main__":
    unittest.main()
