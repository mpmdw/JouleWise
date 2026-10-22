"""Independent direct-grid duty estimator, amended for the R2 interval rule.

This reference enumerates every interval against every window and keeps its
geometry rational.  It shares only PowerTrace and the public estimate_energy
entry point with production; no production helper or numerical constant is used.
The original reference was independently authored; this lane updates only
the R2 rule's data-bounded interval terms, leaving its direct-grid integration
and Student inversion independent. The external twin is never edited.
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
    declared_groups: dict[int, str] = {}
    power_bounds: list[float | None] = []
    observed: list[float] = []
    raw_rows = []
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
        observed.extend(trace.values)
        raw_rows.append([(t-start-width, t-start, value)
                         for t, value in zip(trace.t_ns, trace.values)])
        readings.extend(this_run)
        signatures[run_id] = tuple((item.left, item.right) for item in this_run)
        label = notes.get("repeat_group")
        if isinstance(label, str) and label:
            declared_groups[run_id] = label
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
    # Planned labels select replicas without moving their actual boundaries.
    # Normalize each run's weighted power so a common Gaussian run shift has
    # the same scale within a declared group even when its total weight differs.
    groups: dict[object, list[int]] = defaultdict(list)
    for run_id, signature in signatures.items():
        key = (
            ("declared", declared_groups[run_id])
            if run_id in declared_groups else ("geometry", signature)
        )
        groups[key].append(run_id)
    run_mass = {
        run_id: sum(
            (coefficient for coefficient, item in zip(coefficients, readings)
             if item.run == run_id),
            Fraction(0),
        )
        for run_id in signatures
    }
    normalized_power = {
        run_id: math.fsum(
            float(coefficient) * item.watts
            for coefficient, item in zip(coefficients, readings)
            if item.run == run_id
        ) / float(run_mass[run_id])
        for run_id in signatures
    }
    auxiliary = coefficients.copy()
    contributions = []
    spread = 0.0
    unreplicated_mass = Fraction(0)
    for run_ids in groups.values():
        n = len(run_ids)
        group_mass = sum((run_mass[run_id] for run_id in run_ids), Fraction(0))
        for index, item in enumerate(readings):
            if item.run in run_ids:
                auxiliary[index] *= group_mass / (n * run_mass[item.run])
        if any(run_id in declared_groups for run_id in run_ids):
            if len({signatures[run_id] for run_id in run_ids}) > 1:
                flags.append("declared_phase_variable_geometry_provisional")
        if n == 1:
            flags.append("unreplicated_phase")
            # R2 property 2: finite data-envelope bound, not an identified SE.
            unreplicated_mass += group_mass
        else:
            xs = [normalized_power[run_id] for run_id in run_ids]
            mean = math.fsum(xs) / n
            sample_variance = math.fsum((x - mean) ** 2 for x in xs) / (n - 1)
            contribution = float(group_mass) ** 2 * sample_variance / n
            contributions.append((contribution, n - 1))
    if math.isfinite(spread):
        variance = math.fsum(part for part, _ in contributions)
        if variance:
            df = variance * variance / math.fsum(
                part * part / degrees for part, degrees in contributions
            )
            spread = _student_975(df) * math.sqrt(variance)

    auxiliary_energy = math.fsum(
        float(coefficient) * item.watts
        for coefficient, item in zip(auxiliary, readings)
    )
    center_shift = abs(energy - auxiliary_energy)
    quantum = math.fsum(
        float(abs(coefficient)) * item.quantum / 2
        for coefficient, item in zip(auxiliary, readings)
    )

    # F5 separates this diagnostic worst-case bias from the nominal interval.
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
                for coefficient, item in zip(auxiliary, readings)
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
        for coefficient, item in zip(auxiliary, readings)
    )
    if area == 0 and timing_area == 0:
        bias = 0.0
    elif any(bound is None for bound in power_bounds):
        flags.append("power_bound_missing")
        bias = math.inf
    else:
        bound = max(power_bounds)
        bias = bound * (float(area) + timing_area)
    reading_range = max(observed)-min(observed)
    # R2: missing time times observed contrast; whole-window contamination
    # times each auxiliary coefficient; displaced-window fraction times it.
    # These assume underlying contrasts stay in the observed reading range.
    coverage_bound = (duration-covered_ns)/1_000_000_000*reading_range
    outside_mass = sum((
        weight * Fraction((item.right-item.left) -
                          (min(item.right, duration)-max(item.left, 0)),
                          item.right-item.left)
        for weight, item in zip(auxiliary, readings)), Fraction(0))
    edge_ranges = []
    for edge in (0, duration):
        selected = []
        for row in raw_rows:
            within = [(a, b, v) for a, b, v in row if a >= 0 and b <= duration]
            beyond = [(a, b, v) for a, b, v in row
                      if (b <= 0 if edge == 0 else a >= duration)]
            if not within or not beyond:
                selected = []
                break
            within.sort()
            beyond.sort()
            selected.extend((within[0 if edge == 0 else -1][2],
                             beyond[-1 if edge == 0 else 0][2]))
        edge_ranges.append(max(selected)-min(selected) if selected else reading_range)
    boundary_bound = math.fsum(
        float(weight) * ((item.right-item.left) -
                         (min(item.right, duration)-max(item.left, 0))) /
        (item.right-item.left) * max(edge_ranges[0] if item.left < 0 else 0.0,
                                    edge_ranges[1] if item.right > duration else 0.0)
        for weight, item in zip(auxiliary, readings))
    timing_bound = timing_area*reading_range
    return TwinEstimate(
        energy, spread + quantum + center_shift + coverage_bound + boundary_bound
        + timing_bound + float(unreplicated_mass)*reading_range,
        float(coverage), tuple(flags),
    )


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
    repeat_group: str | None = None,
) -> tuple[PowerTrace, int, int]:
    period = width if period is None else period
    notes = {}
    if repeat_group is not None:
        notes["repeat_group"] = repeat_group
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
            # N2: use 1% of the smallest printed uncertainty. The fixture
            # must still leave that ceiling above one million float ulps.
            noise_floor = 1_000_000 * math.ulp(scale)
            uncertainty_ceiling = 0.01 * min(finite_widths)
            self.assertLess(noise_floor, uncertainty_ceiling)
            tolerance = uncertainty_ceiling
        else:
            # No finite uncertainty exists: PIPELINE.md specifies 1e-6 relative.
            tolerance = 1e-6 * scale
        self.assertAlmostEqual(actual.joules, expected.joules, delta=tolerance)
        self.assertAlmostEqual(
            actual.coverage_fraction, expected.coverage_fraction,
            # N4: below 1, use 1e-6 absolute; otherwise 1e-6 relative.
            delta=1e-6 * max(abs(expected.coverage_fraction), 1.0),
        )
        if math.isinf(expected.half_width_j):
            self.assertEqual(actual.half_width_j, math.inf)
        else:
            self.assertAlmostEqual(
                actual.half_width_j, expected.half_width_j,
                delta=1e-6 * abs(expected.half_width_j),  # N3: no uncertainty on a width.
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
        # N7: a joules value with finite printed half-width uses its 1% bar.
        self.assertAlmostEqual(estimate.joules, 20.0, delta=0.01 * estimate.half_width_j)

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
                # R2: observed-range coverage bound needs no physical power bound.
                self.assertTrue(math.isfinite(estimate.half_width_j))

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
        # F5: bias=250 W*10 ms=2.5 J is a separate receipt. The nominal
        # width here is quantization=0.2 W/2*20 ms=.002 J, with no run spread.
        self.assertAlmostEqual(estimate.half_width_j, .002, delta=.002e-6)

    def test_local_boundary_range_excludes_unrelated_prefill(self):
        ms = 1_000_000
        ends = list(range(0, 226 * ms, 25 * ms))
        # 100 ms prefill at 350 W, 90 ms tool wait at 75 W, idle 55 W.
        def integral(left, right):
            cuts = sorted({left, right, *(t for t in (0, 100*ms, 190*ms)
                                         if left < t < right)})
            return sum((b-a)*(55 if a < 0 or a >= 190*ms else
                              350 if a < 100*ms else 75)
                       for a, b in zip(cuts, cuts[1:]))
        values = [integral(t-25*ms, t)/(25*ms) for t in ends]
        runs = [_run(ends, values, width=25*ms, duration=190*ms,
                     resolution=.001, timing=[0]*len(ends)) for _ in range(3)]
        estimate = self.assert_matches_twin(runs)
        # The end window reads 67 W: 15 ms inside at 75 W, 10 outside at
        # 55 W. Error/bound=.015*(10/25)*20=.120 J; q/2*D=.000095 J.
        expected_width = .120+.001/2*.190
        self.assertAlmostEqual(estimate.half_width_j, expected_width,
                               delta=1e-6*expected_width)  # Width has no own uncertainty.
        self.assertLessEqual(abs(estimate.joules-(350*.100+75*.090)), estimate.half_width_j)

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

    def test_unreplicated_geometry_has_a_flagged_data_envelope(self):
        runs = [
            _run(
                [25_000_000 + phase * 25_000_000], [100.0],
                width=25_000_000, duration=100_000_000, period=100_000_000,
                timing=[0],
            )
            for phase in range(4)
        ]
        estimate = self.assert_matches_twin(runs)
        self.assertTrue(math.isfinite(estimate.half_width_j))
        self.assertIn("unreplicated_phase", estimate.flags)

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

    def test_declared_replicas_with_unequal_weights_and_analytic_jitter(self):
        ms = 1_000_000
        width, duration = 25 * ms, 200 * ms
        breaks = [0, 40 * ms, 115 * ms, 170 * ms, duration]
        levels = [20, 80, 160, 95, 45, 20]

        def window_mean(left, right):
            # Integrate the declared piecewise waveform analytically, including
            # power before/after the workload for boundary-straddling windows.
            cuts = sorted({left, right, *(b for b in breaks if left < b < right)})
            numerator = sum(
                (b - a) * levels[sum(a >= boundary for boundary in breaks)]
                for a, b in zip(cuts, cuts[1:])
            )
            return numerator / (right - left)

        jitters = [
            [-400_000, 200_000, 800_000],
            [900_000, -200_000, 100_000],
            [-600_000, 700_000, 300_000],
            [500_000, -800_000, -100_000],
        ]
        shifts = [-0.7, 0.2, 0.5]
        runs = []
        for phase, phase_jitters in enumerate(jitters):
            for replica, jitter in enumerate(phase_jitters):
                ends = [
                    (phase + 1) * width + jitter,
                    (phase + 1) * width + 100 * ms
                    + jitter * (replica + 1) // 2 + (phase - 1) * 100_000,
                ]
                runs.append(_run(
                    ends,
                    [window_mean(end - width, end) + shifts[replica] for end in ends],
                    width=width, duration=duration, period=100 * ms,
                    start=10**15 + len(runs) * 10**9,
                    resolution=0.2 + replica * 0.05 + phase * 0.01,
                    timing=[10_000 * (replica + 1), 5_000 * (phase + 1)],
                    repeat_group=f"planned-phase-{phase}",
                ))

        # Prove this fixture exercises unequal run masses, rather than merely
        # unequal endpoints whose aggregate coefficients happen to match.
        supports = [
            (run_id, timestamp - start - width, timestamp - start)
            for run_id, (trace, start, _) in enumerate(runs)
            for timestamp in trace.t_ns
            if timestamp - start > 0 and timestamp - start - width < duration
        ]
        edges = sorted(
            {0, duration}
            | {max(0, left) for _, left, _ in supports}
            | {min(duration, right) for _, _, right in supports}
        )
        masses = [Fraction(0) for _ in runs]
        for left, right in zip(edges, edges[1:]):
            active = [run_id for run_id, a, b in supports if a <= left and right <= b]
            if active:
                for run_id in active:
                    masses[run_id] += Fraction(right - left, len(active))
        self.assertGreater(len(set(masses[:3])), 1)

        expected = self.assert_matches_twin(runs)
        self.assertTrue(math.isfinite(expected.half_width_j))
        self.assertIn("declared_phase_variable_geometry_provisional", expected.flags)

        # Actual geometry stays distinct: without the caller's planned labels
        # these runs have no exact replicas and the Gaussian spread is
        # unidentifiable. R2 property 2 uses a flagged range envelope instead.
        unlabeled = []
        for trace, start, end in runs:
            notes = json.loads(trace.notes)
            del notes["repeat_group"]
            unlabeled.append((replace(trace, notes=json.dumps(notes)), start, end))
        estimate = self.assert_matches_twin(unlabeled)
        self.assertTrue(math.isfinite(estimate.half_width_j))
        self.assertIn("unreplicated_phase", estimate.flags)

    def test_invalid_runs_are_skipped_without_changing_valid_result(self):
        run = _run(
            [20_000_000, 40_000_000], [90.0, 110.0],
            width=20_000_000, duration=40_000_000, timing=[0, 0],
        )
        trace, start, end = run
        invalid = [
            (replace(trace, averaging_window_ns=None), start, end),
            (replace(trace, source="nvml_energy", unit="J_cumulative"), start, end),
            (replace(trace, notes=json.dumps({
                "flags": ["output_average_not_single_window"],
            })), start, end),
        ]
        self.assert_matches_twin([run, run, *invalid])

    def test_empty_input(self):
        self.assert_matches_twin([])


if __name__ == "__main__":
    unittest.main()
