"""Independent duty estimator, derived without reading the production reducer.

This reference enumerates every interval against every window and keeps its
geometry rational.  It shares only PowerTrace and the public estimate_energy
entry point with production; no production helper or numerical constant is used.
The synthetic worlds are fixture evidence, not NVML hardware validation.
"""

from __future__ import annotations

import json
import math
import random
import unittest
from collections import defaultdict
from dataclasses import replace
from fractions import Fraction
from typing import NamedTuple, Sequence

from joulewise.align.power.duty import estimate_energy
from joulewise.align.records import PowerTrace


class TwinEstimate(NamedTuple):
    joules: float
    half_width_j: float
    coverage_fraction: float
    flags: tuple[str, ...]


class _Reading(NamedTuple):
    run: int
    left: int
    right: int
    watts: float
    quantum: float
    timing: float


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Evaluate the incomplete-beta continued fraction independently."""
    small = 1e-300  # Numerical underflow guard, not a measurement threshold.
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1.0)
    if abs(d) < small:
        d = small
    d = 1.0 / d
    answer = d
    for m in range(1, 501):
        twice = 2 * m
        aa = m * (b - m) * x / ((a + twice - 1) * (a + twice))
        d = 1 + aa * d
        c = 1 + aa / c
        d = 1.0 / (d if abs(d) >= small else small)
        c = c if abs(c) >= small else small
        answer *= d * c
        aa = -(a + m) * (a + b + m) * x / ((a + twice) * (a + twice + 1))
        d = 1 + aa * d
        c = 1 + aa / c
        d = 1.0 / (d if abs(d) >= small else small)
        c = c if abs(c) >= small else small
        change = d * c
        answer *= change
        if abs(change - 1) < 8 * math.ulp(1.0):
            return answer
    raise AssertionError("independent incomplete-beta iteration did not converge")


def _regularized_beta(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    factor = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    if x < (a + 1) / (a + b + 2):
        return factor * _beta_fraction(a, b, x) / a
    return 1 - factor * _beta_fraction(b, a, 1 - x) / b


def _student_975(df: float) -> float:
    # Two-sided 95% confidence leaves a one-sided tail probability of 0.025.
    def tail(t: float) -> float:
        return 0.5 * _regularized_beta(df / 2, 0.5, df / (df + t * t))

    lower, upper = 0.0, 1.0
    while tail(upper) > 0.025:
        upper *= 2
    # Bisection to float precision; this is solely a numerical accuracy bound.
    for _ in range(64):
        middle = (lower + upper) / 2
        if tail(middle) > 0.025:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2


def _nonnegative(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def twin_estimate_energy(
    runs: Sequence[tuple[PowerTrace, int, int]],
) -> TwinEstimate:
    """Direct rational-grid reference for the agreed window estimator."""
    readings: list[_Reading] = []
    signatures: dict[int, tuple[tuple[int, int], ...]] = {}
    power_bounds: list[float | None] = []
    flags = ["constant_workload_assumed"]
    duration: int | None = None

    for run_id, (trace, start, end) in enumerate(runs):
        width = trace.averaging_window_ns
        if (
            not isinstance(start, int) or isinstance(start, bool)
            or not isinstance(end, int) or isinstance(end, bool)
            or end <= start
            or trace.unit != "W"
            or not isinstance(width, int) or isinstance(width, bool) or width <= 0
            or not _nonnegative(trace.duty_fraction) or trace.duty_fraction == 0
            or trace.duty_fraction > 1
            or not _nonnegative(trace.resolution) or trace.resolution == 0
            or any(not _nonnegative(value) for value in trace.values)
        ):
            flags.append("invalid_run")
            continue
        try:
            notes = json.loads(trace.notes) if trace.notes else {}
        except (ValueError, TypeError):
            notes = {}
        if not isinstance(notes, dict):
            notes = {}
        reported_flags = notes.get("flags", [])
        if (
            isinstance(reported_flags, (list, tuple, str))
            and "output_average_not_single_window" in reported_flags
        ):
            flags.append("not_single_window")
            continue
        if duration is not None and end - start != duration:
            flags.append("different_duration")
            continue
        duration = end - start
        uncertainty = notes.get("timing_half_width_ns")
        if uncertainty is None:
            flags.append("timing_uncertainty_unreported")
            uncertainty = [0.0] * len(trace.values)
        elif (
            not isinstance(uncertainty, list)
            or len(uncertainty) != len(trace.values)
            or any(not _nonnegative(value) for value in uncertainty)
        ):
            uncertainty = [math.inf] * len(trace.values)
            flags.append("timing_uncertainty_unknown")
        this_run = [
            _Reading(
                run_id, timestamp - start - width, timestamp - start,
                float(value), float(trace.resolution), float(uncertainty[index]),
            )
            for index, (timestamp, value) in enumerate(zip(trace.t_ns, trace.values))
            if timestamp - start > 0 and timestamp - start - width < duration
        ]
        if not this_run:
            flags.append("run_without_coverage")
            continue
        readings.extend(this_run)
        signatures[run_id] = tuple((item.left, item.right) for item in this_run)
        bound = notes.get("power_bound_w")
        power_bounds.append(float(bound) if _nonnegative(bound) else None)

    if not readings or duration is None:
        return TwinEstimate(0.0, math.inf, 0.0, tuple(flags + ["no_coverage"]))

    edges = sorted(
        {0, duration}
        | {max(0, item.left) for item in readings}
        | {min(duration, item.right) for item in readings}
    )
    # This intentionally does O(atoms * windows) independent membership checks,
    # unlike an event sweep.  Coefficients initially carry integer nanoseconds.
    atoms = []
    for left, right in zip(edges, edges[1:]):
        active = [
            index for index, item in enumerate(readings)
            if item.left <= left and right <= item.right
        ]
        if active:
            atoms.append((right - left, active))
    covered_ns = sum(length for length, _ in atoms)
    coverage = Fraction(covered_ns, duration)
    coefficients = [Fraction(0) for _ in readings]
    for length, active in atoms:
        coefficient = Fraction(length, 1_000_000_000 * len(active)) / coverage
        for index in active:
            coefficients[index] += coefficient

    energy = math.fsum(
        float(coefficient) * item.watts
        for coefficient, item in zip(coefficients, readings)
    )
    quantum = math.fsum(
        float(abs(coefficient)) * item.quantum / 2
        for coefficient, item in zip(coefficients, readings)
    )

    # Repeatability is across runs with identical window geometry, not across
    # timestamps or staggered phases.  Each z contains the complete run weight.
    groups: dict[tuple[tuple[int, int], ...], list[float]] = defaultdict(list)
    for run_id, signature in signatures.items():
        z = math.fsum(
            float(coefficient) * item.watts
            for coefficient, item in zip(coefficients, readings)
            if item.run == run_id
        )
        groups[signature].append(z)
    contributions = []
    for zs in groups.values():
        n = len(zs)
        if n == 1:
            flags.append("unreplicated_phase")
            spread = math.inf
            break
        mean = math.fsum(zs) / n
        contribution = n * math.fsum((z - mean) ** 2 for z in zs) / (n - 1)
        contributions.append((contribution, n - 1))
    else:
        variance = math.fsum(part for part, _ in contributions)
        if variance == 0:
            spread = 0.0
        else:
            df = variance * variance / math.fsum(
                part * part / degrees for part, degrees in contributions
            )
            spread = _student_975(df) * math.sqrt(variance)

    # The second grid uses the FULL windows, including their outside tails.
    # Rational arithmetic makes a perfectly tiled kernel mismatch exactly zero.
    kernel_edges = sorted(
        {0, duration}
        | {item.left for item in readings}
        | {item.right for item in readings}
    )
    positive = Fraction(0)
    negative = Fraction(0)
    for left, right in zip(kernel_edges, kernel_edges[1:]):
        kernel = sum(
            (
                coefficient / Fraction(item.right - item.left, 1_000_000_000)
                for coefficient, item in zip(coefficients, readings)
                if item.left <= left and right <= item.right
            ),
            Fraction(0),
        )
        target = int(0 <= left and right <= duration)
        mismatch = (kernel - target) * Fraction(right - left, 1_000_000_000)
        positive += max(mismatch, 0)
        negative += max(-mismatch, 0)
    # Integral(K) and integral(target) are both the workload duration.
    assert positive == negative
    area = max(positive, negative)
    timing_area = math.fsum(
        float(abs(coefficient)) * min(item.timing / (item.right - item.left), 1.0)
        for coefficient, item in zip(coefficients, readings)
    )
    if area == 0 and timing_area == 0:
        bias = 0.0
    elif any(bound is None for bound in power_bounds):
        flags.append("power_bound_missing")
        bias = math.inf
    else:
        bound = max(power_bounds)
        bias = bound * (float(area) + timing_area)
    return TwinEstimate(energy, spread + quantum + bias, float(coverage), tuple(flags))


def _run(
    endpoints: Sequence[int],
    watts: Sequence[float],
    *,
    width: int,
    duration: int,
    period: int | None = None,
    start: int = 10_000_000_000,
    resolution: float = 0.2,
    power_bound: float | None = 250.0,
    timing: Sequence[float] | None = None,
) -> tuple[PowerTrace, int, int]:
    period = width if period is None else period
    notes = {}
    if power_bound is not None:
        notes["power_bound_w"] = power_bound
    if timing is not None:
        notes["timing_half_width_ns"] = list(timing)
    trace = PowerTrace(
        source="mock", channel="gpu0", clock_domain="fixture",
        t_ns=tuple(start + endpoint for endpoint in endpoints),
        values=tuple(watts), unit="W", nominal_interval_ns=period,
        averaging_window_ns=width, duty_fraction=min(width / period, 1.0),
        resolution=resolution, notes=json.dumps(notes),
    )
    return trace, start, start + duration


class DutyIndependentTwinTests(unittest.TestCase):
    def assert_matches_twin(self, runs):
        actual = estimate_energy(runs)
        expected = twin_estimate_energy(runs)
        scale = max(1.0, abs(actual.joules), abs(expected.joules))
        finite_widths = [
            width for width in (actual.half_width_j, expected.half_width_j)
            if math.isfinite(width) and width > 0
        ]
        if finite_widths:
            scale = max(scale, *finite_widths)
            # PIPELINE.md: the agreement bar lies between 10^6 floating-point
            # ulps and 1% of the smallest uncertainty.  Their geometric mean
            # leaves room on both sides; fixtures must support that interval.
            noise_floor = 1_000_000 * math.ulp(scale)
            uncertainty_ceiling = 0.01 * min(finite_widths)
            self.assertLess(noise_floor, uncertainty_ceiling)
            tolerance = math.sqrt(noise_floor * uncertainty_ceiling)
        else:
            # No finite uncertainty exists: PIPELINE.md specifies 1e-6 relative.
            tolerance = 1e-6 * scale
        self.assertAlmostEqual(actual.joules, expected.joules, delta=tolerance)
        self.assertAlmostEqual(
            actual.coverage_fraction, expected.coverage_fraction,
            delta=1e-6 * max(abs(expected.coverage_fraction), 1e-12),
        )
        if math.isinf(expected.half_width_j):
            self.assertEqual(actual.half_width_j, math.inf)
        else:
            self.assertAlmostEqual(
                actual.half_width_j, expected.half_width_j, delta=tolerance,
            )
        return expected

    def test_reference_student_quantiles(self):
        # Standard two-sided 95% Student quantiles, rounded to 6 decimals;
        # 1e-6 relative dominates that rounding and is the no-uncertainty bar.
        for df, expected in [(1, 12.706205), (2, 4.302653), (10, 2.228139)]:
            with self.subTest(df=df):
                self.assertAlmostEqual(
                    _student_975(df), expected, delta=1e-6 * expected,
                )

    def test_whole_windows_tiled_across_quarter_duty_phases(self):
        ms = 1_000_000
        runs = []
        for phase in range(4):
            ends = [25 * ms + phase * 25 * ms, 125 * ms + phase * 25 * ms]
            for replica, shift in enumerate((-2.0, 0.0, 2.0)):
                runs.append(_run(
                    ends, [75 + shift, 125 + shift], width=25 * ms,
                    duration=200 * ms, period=100 * ms,
                    start=10**15 + (phase * 3 + replica) * 10**9,
                    power_bound=None, timing=[0, 0],
                ))
        estimate = self.assert_matches_twin(runs)
        self.assertEqual(estimate.coverage_fraction, 1.0)
        self.assertTrue(math.isfinite(estimate.half_width_j))
        self.assertAlmostEqual(estimate.joules, 20.0, delta=20e-6)

    def test_sparse_coverage_with_and_without_explicit_power_bound(self):
        ms = 1_000_000
        for bound in (250.0, None):
            runs = [
                _run(
                    [20 * ms, 80 * ms], [80 + noise, 100 + noise],
                    width=20 * ms, duration=100 * ms, period=60 * ms,
                    power_bound=bound, timing=[0, 0],
                )
                for noise in (-1.0, 0.0, 1.0)
            ]
            with self.subTest(bound=bound):
                estimate = self.assert_matches_twin(runs)
                self.assertEqual(estimate.coverage_fraction, 0.4)
                self.assertEqual(math.isfinite(estimate.half_width_j), bound is not None)

    def test_partial_window_keeps_its_outside_support(self):
        ms = 1_000_000
        runs = [
            _run(
                [30 * ms], [100.0], width=40 * ms, duration=20 * ms,
                resolution=0.2, power_bound=250.0, timing=[0],
            )
            for _ in range(3)
        ]
        estimate = self.assert_matches_twin(runs)
        # K=1/2 on [-10,30] ms; each sign of K-target has area 10 ms.
        # Bias=250 W*10 ms=2.5 J; quantization=0.2 W/2*20 ms=.002 J.
        self.assertAlmostEqual(estimate.half_width_j, 2.502, delta=2.502e-6)

    def test_interleaved_overlapping_phases_and_welch_spread(self):
        ms = 1_000_000
        runs = []
        for ends, noises in [
            ([20 * ms, 60 * ms], [-3, 0, 3]),
            ([40 * ms, 80 * ms], [-1, 1]),
        ]:
            for noise in noises:
                runs.append(_run(
                    ends, [60 + noise, 150 + 2 * noise], width=40 * ms,
                    duration=60 * ms, timing=[0, 0],
                ))
        self.assert_matches_twin(runs)

    def test_timing_whole_window_shift_bound(self):
        ms = 1_000_000
        for timing in ([0, 0], [ms, 2 * ms], [30 * ms, 40 * ms]):
            runs = [
                _run(
                    [20 * ms, 40 * ms], [100.0, 100.0], width=20 * ms,
                    duration=40 * ms, timing=timing,
                )
                for _ in range(3)
            ]
            with self.subTest(timing=timing):
                self.assert_matches_twin(runs)

    def test_absent_timing_is_flagged_but_nominal_zero(self):
        run = _run(
            [20_000_000, 40_000_000], [90.0, 110.0],
            width=20_000_000, duration=40_000_000, power_bound=None,
        )
        expected = self.assert_matches_twin([run, run])
        self.assertIn("timing_uncertainty_unreported", expected.flags)

    def test_unreplicated_geometry_cannot_estimate_spread(self):
        runs = [
            _run(
                [25_000_000 + phase * 25_000_000], [100.0],
                width=25_000_000, duration=100_000_000, period=100_000_000,
                timing=[0],
            )
            for phase in range(4)
        ]
        self.assertEqual(self.assert_matches_twin(runs).half_width_j, math.inf)

    def test_seeded_mixed_window_worlds(self):
        rng = random.Random(470912)
        for world in range(16):
            duration = rng.randint(8, 20) * 1_000_000
            runs = []
            for phase in range(rng.randint(1, 3)):
                width = rng.randint(2, 5) * 1_000_000
                period = rng.randint(width, 2 * width)
                first = rng.randint(1, width)
                ends = list(range(first, duration + width, period))
                base = [rng.uniform(40, 160) for _ in ends]
                for replica in range(rng.randint(2, 5)):
                    offset = rng.uniform(-3, 3)
                    values = [value + offset + rng.uniform(-1, 1) for value in base]
                    runs.append(_run(
                        ends, values, width=width, duration=duration, period=period,
                        start=10**15 + (phase * 5 + replica) * 10**9,
                        resolution=rng.uniform(0.1, 0.4),
                        timing=[rng.randint(0, 50_000) for _ in ends],
                    ))
            with self.subTest(world=world):
                self.assert_matches_twin(runs)

    def test_invalid_runs_are_skipped_without_changing_valid_result(self):
        run = _run(
            [20_000_000, 40_000_000], [90.0, 110.0],
            width=20_000_000, duration=40_000_000, timing=[0, 0],
        )
        trace, start, end = run
        invalid = [
            (replace(trace, averaging_window_ns=None), start, end),
            (replace(trace, duty_fraction=None), start, end),
            (replace(trace, resolution=None), start, end),
            (replace(trace, values=(math.nan, 110.0)), start, end),
            (replace(trace, values=(-1.0, 110.0)), start, end),
            (replace(trace, source="nvml_energy", unit="J_cumulative"), start, end),
            (replace(trace, notes=json.dumps({
                "flags": ["output_average_not_single_window"],
            })), start, end),
            (trace, start, end + 1),
        ]
        self.assert_matches_twin([run, run, *invalid])

    def test_empty_input(self):
        self.assert_matches_twin([])


if __name__ == "__main__":
    unittest.main()
