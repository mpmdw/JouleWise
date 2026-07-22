"""Synthetic pulse-detector tests for the D-078 fiducial harness.

All traces are deterministic (sinusoidal pseudo-noise, no RNG): each test
knows the true pulse edges and asserts the estimator's error and residual
bounds against them.
"""

from __future__ import annotations

import math
import json
import hashlib
import tempfile
import unittest
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import powermetrics_fiducial as fiducial_module
from joulewise.powermetrics_fiducial import (
    BINDING_FIELDS,
    LEGACY_PROTOCOL_ID,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V2_SHA256,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    RESIDUAL_REGION_METHOD,
    CommandedPulse,
    TraceInterval,
    detect_pulses,
    instrument_evidence,
    protocol_definition,
    pulse_gap_s,
    pulse_schedule,
    van_der_corput,
    window_license_min_duration_s,
)
from scripts.validate_powermetrics_fiducial import (
    trim_trace_after_warmups,
    verify_frozen_protocol,
)
from scripts import validate_powermetrics_fiducial as validation_script

CADENCE_S = 0.1
BASELINE_W = 2.0
AMPLITUDE_W = 20.0


def overlap_fraction(start_s: float, end_s: float, on_s: float, off_s: float) -> float:
    width = end_s - start_s
    if width <= 0:
        return 0.0
    return max(0.0, min(end_s, off_s) - max(start_s, on_s)) / width


def synthetic_trace(
    true_pulses: list[tuple[float, float]],
    *,
    start_s: float = 0.0,
    end_s: float,
    cadence_s: float = CADENCE_S,
    jitter: bool = False,
    noise_w: float = 0.03,
    amplitude_w: float = AMPLITUDE_W,
) -> list[TraceInterval]:
    intervals: list[TraceInterval] = []
    cursor = start_s
    index = 0
    while cursor < end_s:
        width = cadence_s
        if jitter:
            width = cadence_s * (1.0 + 0.3 * math.sin(1.7 * index))
        nxt = min(cursor + width, end_s)
        frac = sum(
            overlap_fraction(cursor, nxt, on_s, off_s)
            for on_s, off_s in true_pulses
        )
        power = BASELINE_W + amplitude_w * frac + noise_w * math.sin(2.3 * index)
        intervals.append(TraceInterval(start_s=cursor, end_s=nxt, power_w=power))
        cursor = nxt
        index += 1
    return intervals


def commanded(true_pulses, shift_s: float = 0.0, uncertainty_s: float = 0.0):
    """Commanded pulses whose true realization is shifted by ``shift_s``."""

    return [
        CommandedPulse(
            on_s=on_s - shift_s,
            off_s=off_s - shift_s,
            on_uncertainty_s=uncertainty_s,
            off_uncertainty_s=uncertainty_s,
        )
        for on_s, off_s in true_pulses
    ]


class ScheduleTests(unittest.TestCase):
    def test_van_der_corput_prefix(self) -> None:
        self.assertEqual(
            [van_der_corput(index) for index in range(1, 8)],
            [0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875],
        )

    def test_gaps_avoid_ten_hertz_phase_lock(self) -> None:
        gaps = [pulse_gap_s(index) for index in range(1, 41)]
        residues = {round((gap % CADENCE_S) / CADENCE_S, 6) for gap in gaps}
        # A constant-gap schedule would collapse to one residue; the van der
        # Corput offsets spread the pulse edges across the sampling phase.
        self.assertGreaterEqual(len(residues), 8)

    def test_schedule_shape(self) -> None:
        schedule = pulse_schedule(5, start_s=10.0)
        self.assertEqual(len(schedule), 5)
        for (on_s, off_s), (next_on_s, _next_off) in zip(schedule, schedule[1:]):
            self.assertAlmostEqual(off_s - on_s, 1.0, places=12)
            self.assertGreaterEqual(next_on_s - off_s, 1.5)
        self.assertEqual(schedule[0][0], 10.0)


class DetectorTests(unittest.TestCase):
    def make_case(self, *, shift_s: float, jitter: bool = False, count: int = 6):
        true_pulses = [
            (on_s + 10.0 + shift_s, off_s + 10.0 + shift_s)
            for on_s, off_s in pulse_schedule(count)
        ]
        trace = synthetic_trace(
            true_pulses, end_s=true_pulses[-1][1] + 10.0, jitter=jitter
        )
        pulses = [
            CommandedPulse(on_s=on_s - shift_s, off_s=off_s - shift_s)
            for on_s, off_s in true_pulses
        ]
        return trace, pulses

    def test_bias_recovery_beats_first_threshold_crossing(self) -> None:
        shift_s = 0.037
        trace, pulses = self.make_case(shift_s=shift_s)
        detection = detect_pulses(trace, pulses)
        self.assertTrue(detection.all_pulses_detected, detection.reasons)
        self.assertIsNotNone(detection.b_fiducial_s)
        for fit in detection.fits:
            # The model fit recovers the true shift well below one cadence.
            self.assertLess(abs(fit.delta_on_s - shift_s), 0.02)
            self.assertLess(abs(fit.delta_off_s - shift_s), 0.02)
            # Residual intervals contain the truth (they are shifts relative
            # to the commanded edge).
            self.assertLessEqual(fit.onset_residual_lower_s, shift_s + 1e-9)
            self.assertGreaterEqual(fit.onset_residual_upper_s, shift_s - 1e-9)
        # A naive first-above-threshold endpoint estimator quantizes the
        # onset to the next interval END: up to one full cadence of bias.
        pulse = pulses[0]
        threshold_w = BASELINE_W + 0.5 * AMPLITUDE_W
        naive_onset = next(
            interval.end_s
            for interval in trace
            if interval.end_s > pulse.on_s - 0.5 and interval.power_w > threshold_w
        )
        naive_error = abs((naive_onset - pulse.on_s) - shift_s)
        fitted_error = abs(detection.fits[0].delta_on_s - shift_s)
        self.assertGreater(naive_error, fitted_error)
        # B_fiducial dominates the worst true residual across every edge.
        worst_true_error = max(
            max(
                abs(fit.delta_on_s - shift_s) + abs(shift_s),
                abs(fit.delta_off_s - shift_s) + abs(shift_s),
            )
            for fit in detection.fits
        )
        self.assertGreaterEqual(detection.b_fiducial_s, abs(shift_s) - 0.02)
        self.assertLessEqual(detection.residual_median_s, detection.b_fiducial_s)
        self.assertLessEqual(detection.residual_p95_s, detection.b_fiducial_s)
        del worst_true_error

    def test_cadence_jitter_still_recovers_shift(self) -> None:
        shift_s = -0.042
        trace, pulses = self.make_case(shift_s=shift_s, jitter=True)
        detection = detect_pulses(trace, pulses)
        self.assertTrue(detection.all_pulses_detected, detection.reasons)
        for fit in detection.fits:
            self.assertLess(abs(fit.delta_on_s - shift_s), 0.03)
            self.assertLess(abs(fit.delta_off_s - shift_s), 0.03)

    def test_validated_tenth_and_three_tenth_second_delays_are_recovered(self) -> None:
        # F8 contract boundary: the production fiducial must still recover
        # the synthetic 0.10 s and 0.30 s delay fixtures after replacing the
        # one-dimensional loss slices with a joint acceptance projection.
        for shift_s in (0.10, 0.30):
            with self.subTest(shift_s=shift_s):
                trace, pulses = self.make_case(shift_s=shift_s, count=3)
                detection = detect_pulses(trace, pulses)
                self.assertTrue(detection.all_pulses_detected, detection.reasons)
                self.assertGreaterEqual(detection.b_fiducial_s, shift_s - 0.02)
                for fit in detection.fits:
                    self.assertLess(abs(fit.delta_on_s - shift_s), 0.03)
                    self.assertLess(abs(fit.delta_off_s - shift_s), 0.03)

    def test_half_second_delay_fails_closed_outside_validated_region(self) -> None:
        trace, pulses = self.make_case(shift_s=0.50, count=3)
        detection = detect_pulses(trace, pulses)
        self.assertFalse(detection.all_pulses_detected)
        self.assertIsNone(detection.b_fiducial_s)
        self.assertIn("pulse_detection_incomplete", detection.reasons)
        self.assertTrue(
            any(
                "fitted_shift_exceeds_validation_limit" in fit.reasons
                for fit in detection.fits
            )
        )

    def test_event_stamp_uncertainty_widens_residuals(self) -> None:
        trace, _ = self.make_case(shift_s=0.0)
        true_pulses = [
            (pulse.on_s, pulse.off_s)
            for pulse in commanded(
                [(on_s + 10.0, off_s + 10.0) for on_s, off_s in pulse_schedule(6)]
            )
        ]
        tight = detect_pulses(trace, commanded(true_pulses, uncertainty_s=0.0))
        wide = detect_pulses(trace, commanded(true_pulses, uncertainty_s=0.05))
        self.assertIsNotNone(tight.b_fiducial_s)
        self.assertIsNotNone(wide.b_fiducial_s)
        self.assertGreaterEqual(
            wide.b_fiducial_s, tight.b_fiducial_s + 0.049
        )

    def test_live_shaped_bound_includes_capture_trace_anchor(self) -> None:
        # F4 live-calibration shape: the fit/event component is ~24.0 ms and
        # the capture's own effective trace anchor is 2.926 ms. Pre-fix the
        # latter was omitted and the physical bound stopped near 24.0 ms.
        trace, pulses = self.make_case(shift_s=0.02, count=3)
        pulses = [
            replace(
                pulse,
                on_uncertainty_s=0.0035,
                off_uncertainty_s=0.0035,
            )
            for pulse in pulses
        ]
        detection = detect_pulses(
            trace, pulses, trace_anchor_bound_s=0.002926
        )
        self.assertAlmostEqual(detection.b_fiducial_s, 0.0269, delta=0.0002)
        self.assertGreaterEqual(detection.b_fiducial_s, 0.026039)

    def test_trace_anchor_widening_is_monotone_for_clean_inputs(self) -> None:
        # Property-style regression over different accepted pulse phases: the
        # fixed estimator can only add the causal anchor component.
        for shift_s in (-0.04, 0.0, 0.03):
            with self.subTest(shift_s=shift_s):
                trace, pulses = self.make_case(shift_s=shift_s, count=3)
                old = detect_pulses(trace, pulses)
                new = detect_pulses(
                    trace, pulses, trace_anchor_bound_s=0.002926
                )
                self.assertGreaterEqual(new.b_fiducial_s, old.b_fiducial_s)
                self.assertAlmostEqual(
                    new.b_fiducial_s,
                    old.b_fiducial_s + 0.002926,
                    places=12,
                )

    def test_full_region_projection_dominates_legacy_directional_scan(self) -> None:
        # F4 monotonicity across the estimator revision itself: every point
        # admitted by the former axes/two-diagonals scan must lie inside the
        # analytic full-region projection on the same input.
        trace, pulses = self.make_case(shift_s=0.037, count=3)
        detection = detect_pulses(trace, pulses)
        strict_excursion_found = False
        for pulse, fit in zip(pulses, detection.fits, strict=True):
            local = [
                interval
                for interval in trace
                if min(
                    interval.end_s,
                    pulse.off_s + fiducial_module.LOCAL_MARGIN_S,
                )
                > max(
                    interval.start_s,
                    pulse.on_s - fiducial_module.LOCAL_MARGIN_S,
                )
            ]
            loss = lambda onset, offset: fiducial_module._pulse_loss(
                local,
                detection.baseline_w,
                fit.amplitude_w,
                detection.robust_sigma_w,
                pulse.on_s + onset,
                pulse.off_s + offset,
            )
            best_loss = loss(fit.delta_on_s, fit.delta_off_s)
            limit = best_loss + max(1.0, 0.05 * best_loss)
            old_onsets = [fit.delta_on_s]
            old_offsets = [fit.delta_off_s]

            def admit(onset, offset):
                if (
                    abs(onset) <= fiducial_module.FIT_HALF_RANGE_S
                    and abs(offset) <= fiducial_module.FIT_HALF_RANGE_S
                    and loss(onset, offset) <= limit
                ):
                    old_onsets.append(onset)
                    old_offsets.append(offset)

            for value in fiducial_module._grid(
                fit.delta_on_s,
                fiducial_module.FIT_HALF_RANGE_S,
                fiducial_module.FIT_FINE_STEP_S,
            ):
                admit(value, fit.delta_off_s)
            for value in fiducial_module._grid(
                fit.delta_off_s,
                fiducial_module.FIT_HALF_RANGE_S,
                fiducial_module.FIT_FINE_STEP_S,
            ):
                admit(fit.delta_on_s, value)
            for shift in fiducial_module._grid(
                0.0,
                fiducial_module.FIT_HALF_RANGE_S,
                fiducial_module.FIT_FINE_STEP_S,
            ):
                admit(fit.delta_on_s + shift, fit.delta_off_s + shift)
                admit(fit.delta_on_s + shift, fit.delta_off_s - shift)

            self.assertLessEqual(
                fit.onset_residual_lower_s, min(old_onsets) + 1e-12
            )
            self.assertGreaterEqual(
                fit.onset_residual_upper_s, max(old_onsets) - 1e-12
            )
            self.assertLessEqual(
                fit.offset_residual_lower_s, min(old_offsets) + 1e-12
            )
            self.assertGreaterEqual(
                fit.offset_residual_upper_s, max(old_offsets) - 1e-12
            )
            strict_excursion_found |= any(
                (
                    fit.onset_residual_lower_s < min(old_onsets) - 5e-5,
                    fit.onset_residual_upper_s > max(old_onsets) + 5e-5,
                    fit.offset_residual_lower_s < min(old_offsets) - 5e-5,
                    fit.offset_residual_upper_s > max(old_offsets) + 5e-5,
                )
            )
        self.assertTrue(
            strict_excursion_found,
            "fixture must expose an accepted off-axis excursion missed by axes/diagonals",
        )

    def test_missing_edge_fails_closed(self) -> None:
        trace, pulses = self.make_case(shift_s=0.0)
        # Truncate the capture before the final pulse's off edge margin.
        cutoff_s = pulses[-1].off_s - 0.3
        truncated = [
            interval for interval in trace if interval.end_s <= cutoff_s
        ]
        detection = detect_pulses(truncated, pulses)
        self.assertFalse(detection.all_pulses_detected)
        self.assertIsNone(detection.b_fiducial_s)
        self.assertIn("pulse_detection_incomplete", detection.reasons)

    def test_false_positive_plateau_fails_closed(self) -> None:
        trace, pulses = self.make_case(shift_s=0.0)
        # Inject an uncommanded plateau in the leading baseline.
        spiked = [
            (
                TraceInterval(
                    start_s=interval.start_s,
                    end_s=interval.end_s,
                    power_w=interval.power_w + AMPLITUDE_W,
                )
                if 2.0 <= interval.start_s and interval.end_s <= 4.0
                else interval
            )
            for interval in trace
        ]
        detection = detect_pulses(spiked, pulses)
        self.assertGreater(detection.spurious_plateau_count, 0)
        self.assertIsNone(detection.b_fiducial_s)
        self.assertIn("spurious_plateau_detected", detection.reasons)

    def test_harness_warmups_are_trimmed_but_real_spurious_plateau_remains(self) -> None:
        # W7 exact harness shape: three captured warmups precede a second
        # baseline and the measured train.  Before the harness fix, those
        # warmups lived in detector ``outside`` and made every clean run
        # spuriously invalid.
        warmup_edges = [(5.0, 6.0), (7.5, 8.5), (10.0, 11.0)]
        measured_edges = [
            (on_s + 16.0, off_s + 16.0) for on_s, off_s in pulse_schedule(3)
        ]
        trace = synthetic_trace(
            [*warmup_edges, *measured_edges], end_s=measured_edges[-1][1] + 5.0
        )
        trimmed = trim_trace_after_warmups(
            trace, commanded(warmup_edges)
        )
        clean = detect_pulses(trimmed, commanded(measured_edges))
        self.assertIsNotNone(clean.b_fiducial_s, clean.reasons)
        self.assertEqual(clean.spurious_plateau_count, 0)

        spurious = [
            replace(interval, power_w=interval.power_w + AMPLITUDE_W)
            if 13.0 <= interval.start_s and interval.end_s <= 14.0
            else interval
            for interval in trimmed
        ]
        contaminated = detect_pulses(spurious, commanded(measured_edges))
        self.assertGreater(contaminated.spurious_plateau_count, 0)
        self.assertIsNone(contaminated.b_fiducial_s)

    def test_low_plateau_and_low_snr_fail_closed(self) -> None:
        true_pulses = [
            (on_s + 10.0, off_s + 10.0) for on_s, off_s in pulse_schedule(3)
        ]
        pulses = commanded(true_pulses)
        weak_trace = synthetic_trace(
            true_pulses, end_s=true_pulses[-1][1] + 10.0, amplitude_w=5.0
        )
        weak = detect_pulses(weak_trace, pulses)
        self.assertFalse(weak.all_pulses_detected)
        self.assertIn(
            "plateau_below_minimum", weak.fits[0].reasons
        )
        noisy_trace = synthetic_trace(
            true_pulses,
            end_s=true_pulses[-1][1] + 10.0,
            amplitude_w=12.0,
            noise_w=2.0,
        )
        noisy = detect_pulses(noisy_trace, pulses)
        self.assertFalse(noisy.all_pulses_detected)
        self.assertTrue(
            any(
                "robust_snr_below_minimum" in fit.reasons
                or "plateau_below_minimum" in fit.reasons
                or "model_fit_not_significant" in fit.reasons
                for fit in noisy.fits
            ),
            [fit.reasons for fit in noisy.fits],
        )
        self.assertIsNone(noisy.b_fiducial_s)

    def test_phase_locked_grid_pulses_still_fit_via_model(self) -> None:
        # Pulses whose edges land exactly on the 10 Hz grid: the overlap-model
        # fit must not inherit the one-cadence quantization a threshold
        # estimator would.
        true_pulses = [(12.0, 13.0), (15.0, 16.0), (18.5, 19.5)]
        trace = synthetic_trace(true_pulses, end_s=30.0)
        detection = detect_pulses(trace, commanded(true_pulses))
        self.assertTrue(detection.all_pulses_detected, detection.reasons)
        for fit in detection.fits:
            self.assertLess(abs(fit.delta_on_s), 0.02)
            self.assertLess(abs(fit.delta_off_s), 0.02)


class EvidenceTests(unittest.TestCase):
    def make_detection(self):
        true_pulses = [
            (on_s + 10.0, off_s + 10.0) for on_s, off_s in pulse_schedule(3)
        ]
        trace = synthetic_trace(true_pulses, end_s=true_pulses[-1][1] + 10.0)
        return detect_pulses(trace, commanded(true_pulses))

    def bindings(self, **overrides):
        base = {
            "hardware_model": "Mac15,9",
            "os_build": "25.5.0",
            "powermetrics_sha256": "ab" * 32,
            "sampling_interval_ms": 100,
            "anchor_method_version": "powermetrics_native_second_censored_intersection_v1",
            "mlx_version": "0.30.0",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v1",
            "power_policy": "ac_high_power",
        }
        base.update(overrides)
        return base

    def test_valid_evidence_carries_bindings_and_bound(self) -> None:
        detection = self.make_detection()
        payload = instrument_evidence(
            detection,
            bindings=self.bindings(),
            validation_id="v-test",
            artifact_sha256={
                "raw/powermetrics.plist": "cd" * 32,
                "events.jsonl": "ef" * 32,
            },
            protocol_pulse_count=3,
            protocol_id=LEGACY_PROTOCOL_ID,
        )
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["b_fiducial_s"], detection.b_fiducial_s)
        self.assertEqual(set(payload["bindings"]), set(self.bindings()))
        self.assertEqual(payload["pulse_count"], 3)

    def test_v2_evidence_requires_and_records_capture_wall_time(self) -> None:
        detection = self.make_detection()
        bindings = self.bindings(
            pulse_protocol_id=PROTOCOL_V2_ID,
            estimator_revision=RESIDUAL_REGION_METHOD,
            protocol_sha256=PROTOCOL_V2_SHA256,
        )
        kwargs = {
            "bindings": bindings,
            "validation_id": "v2-capture-time",
            "artifact_sha256": {
                "raw/powermetrics.plist": "cd" * 32,
                "events.jsonl": "ef" * 32,
            },
            "protocol_pulse_count": 3,
        }
        missing = instrument_evidence(
            detection, protocol_id=PROTOCOL_V2_ID, **kwargs
        )
        recorded = instrument_evidence(
            detection,
            capture_wall_time_s=1_784_491_000.25,
            protocol_id=PROTOCOL_V2_ID,
            **kwargs,
        )

        self.assertEqual(missing["status"], "invalid")
        self.assertEqual(recorded["status"], "valid")
        self.assertEqual(recorded["capture_wall_time_s"], 1_784_491_000.25)
        self.assertEqual(recorded["max_age_s"], 86400)

    def test_any_detection_reason_forces_invalid_status(self) -> None:
        # F5 exact defect: structural fields and B were clean, but a registered
        # refusal reason still serialized status=valid.
        detection = replace(
            self.make_detection(), reasons=("pulse_detection_incomplete",)
        )
        payload = instrument_evidence(
            detection,
            bindings=self.bindings(),
            validation_id="v-reasoned",
            artifact_sha256={
                "raw/powermetrics.plist": "cd" * 32,
                "events.jsonl": "ef" * 32,
            },
            protocol_pulse_count=3,
        )
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("pulse_detection_incomplete", payload["reasons"])

    def test_fitted_bound_below_protocol_pulse_count_is_invalid(self) -> None:
        # Regression: a 3-pulse run yields a fitted bound and all-detected, but
        # the default protocol binds all 59 pulses. It must NOT be valid.
        detection = self.make_detection()
        self.assertTrue(detection.all_pulses_detected)
        self.assertIsNotNone(detection.b_fiducial_s)
        payload = instrument_evidence(
            detection,
            bindings=self.bindings(),
            validation_id="v-test",
            artifact_sha256={},
        )
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(
            any(
                reason.startswith("pulse_count_below_protocol:")
                for reason in payload["reasons"]
            ),
            payload["reasons"],
        )

    def test_undetected_pulse_forces_invalid_even_when_bound_present(self) -> None:
        # A detection with a fitted bound but all_pulses_detected False (e.g.
        # count matches but a pulse failed) must fail closed.
        detection = self.make_detection()
        forced = replace(
            detection,
            all_pulses_detected=False,
            b_fiducial_s=0.01,
            reasons=("pulse_detection_incomplete",),
        )
        payload = instrument_evidence(
            forced,
            bindings=self.bindings(),
            validation_id="v-test",
            artifact_sha256={},
            protocol_pulse_count=len(forced.fits),
        )
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("not_all_pulses_detected", payload["reasons"])

    def test_missing_binding_field_fails_closed(self) -> None:
        detection = self.make_detection()
        payload = instrument_evidence(
            detection,
            bindings=self.bindings(power_policy=None),
            validation_id="v-test",
            artifact_sha256={},
        )
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(
            any(
                reason.startswith("binding_fields_missing:")
                for reason in payload["reasons"]
            )
        )

    def test_window_license_scales_with_effective_bound(self) -> None:
        # At ~115 ms cadence, request metrics need >= ~460 ms regardless of
        # anchor quality; a large B_effective dominates beyond that.
        self.assertAlmostEqual(
            window_license_min_duration_s(0.115, 0.46), 0.46 + 0.0, places=12
        )
        self.assertAlmostEqual(
            window_license_min_duration_s(0.2, 0.46), 0.8, places=12
        )
        with self.assertRaises(ValueError):
            window_license_min_duration_s(-1.0, 0.46)

    def test_trace_anchor_component_flips_four_b_window_license(self) -> None:
        # F2 defect shape using the sealed-capture magnitudes: residual-only
        # B licensed a 100 ms window, while the physically complete composite
        # B (including capture trace-anchor uncertainty) must refuse it.
        residual_only_s = 0.024002791515387596
        trace_anchor_s = 0.002926038
        composite_s = residual_only_s + trace_anchor_s
        window_s = 0.100
        self.assertLessEqual(
            window_license_min_duration_s(residual_only_s, 0.0), window_s
        )
        self.assertGreater(
            window_license_min_duration_s(composite_s, 0.0), window_s
        )

    def test_trace_anchor_term_flips_four_b_window_license(self) -> None:
        # F2 live-shaped defect: residual-only B licensed a 100 ms window,
        # while the physically complete residual+capture-anchor B must refuse.
        residual_only_s = 0.024002791515387596
        trace_anchor_s = 0.002926038
        composite_s = residual_only_s + trace_anchor_s
        window_s = 0.100
        old_min_s = window_license_min_duration_s(residual_only_s, 0.0)
        new_min_s = window_license_min_duration_s(composite_s, 0.0)
        self.assertAlmostEqual(old_min_s, 0.09601116606155038, places=14)
        self.assertAlmostEqual(new_min_s, 0.10771531806155038, places=14)
        self.assertLessEqual(old_min_s, window_s)
        self.assertGreater(new_min_s, window_s)


class FrozenProtocolTests(unittest.TestCase):
    def test_shared_controller_verifier_rejects_forged_zero_residual_rows(self) -> None:
        from joulewise.powermetrics_fiducial import verify_stored_evidence_physics
        from tests.test_reduce import self_consistent_calibration

        evidence, raw, events = self_consistent_calibration()
        evidence["b_fiducial_s"] = 0.0
        for pulse in evidence["pulses"]:
            for field in (
                "onset_residual_lower_s",
                "onset_residual_upper_s",
                "offset_residual_lower_s",
                "offset_residual_upper_s",
            ):
                pulse[field] = 0.0
        with self.assertRaisesRegex(ValueError, "residual does not contain"):
            verify_stored_evidence_physics(evidence, raw, events)

    def test_consistent_protocol_json_matches_executable_pins(self) -> None:
        self.assertTrue(verify_frozen_protocol())

    def test_v1_v2_protocol_bytes_remain_frozen_and_v3_hash_is_bound(self) -> None:
        v1 = Path("configs/calibration/powermetrics_fiducial/protocol_v1.json")
        v2 = Path("configs/calibration/powermetrics_fiducial/protocol_v2.json")
        v3 = Path("configs/calibration/powermetrics_fiducial/protocol_v3.json")
        self.assertEqual(
            hashlib.sha256(v1.read_bytes()).hexdigest(),
            "14a7b5d82f446ba76609dafb0773ea1c3588ab6247919518e50c275e8b99eff9",
        )
        self.assertEqual(hashlib.sha256(v2.read_bytes()).hexdigest(), PROTOCOL_V2_SHA256)
        self.assertEqual(hashlib.sha256(v3.read_bytes()).hexdigest(), PROTOCOL_V3_SHA256)
        self.assertEqual(protocol_definition()["protocol_id"], PROTOCOL_ID)

    def test_protocol_v3_uses_d054_nonparametric_95_95_sample_count(self) -> None:
        # H1 exact defect: the 40-pulse maximum provided only 87.1%
        # confidence of covering the 95th percentile, yet was described as an
        # out-of-sample deterministic bound. The prospective mint uses n=59.
        self.assertEqual(PULSE_COUNT, 59)
        self.assertGreaterEqual(1.0 - 0.95**PULSE_COUNT, 0.95)
        self.assertLess(1.0 - 0.95**40, 0.95)
        self.assertEqual(protocol_definition()["pulse_count"], 59)

    def test_rederive_only_emits_v2_widened_evidence_and_rejects_hash_mismatch(self) -> None:
        from tests.test_reduce import self_consistent_calibration

        evidence, raw, events = self_consistent_calibration()
        stored_only = max(
            abs(float(pulse[field]))
            for pulse in evidence["pulses"]
            for field in (
                "onset_residual_lower_s",
                "onset_residual_upper_s",
                "offset_residual_lower_s",
                "offset_residual_upper_s",
            )
        )
        evidence["b_fiducial_s"] = stored_only
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            (source / "raw").mkdir(parents=True)
            (source / "raw" / "powermetrics.plist").write_bytes(raw)
            (source / "events.jsonl").write_bytes(events)
            evidence_raw = (
                json.dumps(evidence, indent=2, sort_keys=True) + "\n"
            ).encode()
            (source / "instrument_evidence.json").write_bytes(evidence_raw)
            artifacts = {
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
            }
            (source / "manifest.json").write_text(
                json.dumps({"artifacts": artifacts}) + "\n"
            )
            output = Path(tmp) / "fresh" / "instrument_evidence.json"
            fresh = validation_script.rederive_artifact(source, output)
            self.assertEqual(fresh["protocol_id"], PROTOCOL_V2_ID)
            self.assertGreater(fresh["b_fiducial_s"], stored_only)
            self.assertEqual(
                fresh["bindings"]["estimator_revision"], RESIDUAL_REGION_METHOD
            )
            self.assertEqual(
                fresh["bindings"]["protocol_sha256"], PROTOCOL_V2_SHA256
            )
            source_times = [
                float(json.loads(line)["timestamp_s"])
                for line in events.splitlines()
            ]
            self.assertEqual(fresh["capture_wall_time_s"], min(source_times))
            self.assertEqual(fresh["max_age_s"], 86400)
            (source / "events.jsonl").write_bytes(events + b"{}\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                validation_script.rederive_artifact(source, output)

    def test_incomplete_or_tampered_protocol_refuses(self) -> None:
        # F7 defect shape: the harness formerly never loaded this file, so
        # removing a gate or changing an estimator rule had no effect.
        for mutation in ("missing_edge_gate", "wrong_estimator"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                payload = protocol_definition()
                if mutation == "missing_edge_gate":
                    del payload["gates"]["edge_coverage_across_full_fit_range"]
                else:
                    payload["estimator_revision"] = "axes_only_v0"
                path = Path(tmp) / "protocol.json"
                path.write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                self.assertFalse(verify_frozen_protocol(path))

    def test_calibration_entrypoint_refuses_protocol_mismatch_before_live_import(self) -> None:
        with patch.object(
            validation_script, "verify_frozen_protocol", return_value=False
        ), patch.object(
            sys,
            "argv",
            [
                "validate_powermetrics_fiducial.py",
                "--allow-live",
                "--power-policy",
                "ac_high_power",
            ],
        ):
            self.assertEqual(validation_script.main(), 2)

    def test_preworkload_rollover_timeout_terminates_and_mints_no_artifact(self) -> None:
        class FakeProcess:
            def __init__(self) -> None:
                self.terminated = False

            def terminate(self) -> None:
                self.terminated = True

            def communicate(self, timeout=None):
                return b"", b""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            capture = root / "raw.plist"
            capture.write_bytes(b"incomplete but parse-patched")
            artifact = root / "instrument_evidence.json"
            process = FakeProcess()
            records = [
                SimpleNamespace(metadata={"plist_timestamp_s": 100.0}),
                SimpleNamespace(metadata={"plist_timestamp_s": 100.0}),
            ]
            with (
                patch.object(
                    validation_script,
                    "parse_powermetrics_records",
                    return_value=records,
                ),
                patch.object(
                    validation_script.time,
                    "monotonic",
                    side_effect=[0.0, 0.1, 1.0],
                ),
                patch.object(validation_script.time, "sleep"),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    validation_script.ROLLOVER_GATE_TIMEOUT_REASON,
                ):
                    validation_script.wait_for_preworkload_rollover(
                        capture,
                        process,
                        timeout_s=0.5,
                    )
            self.assertTrue(process.terminated)
            self.assertFalse(artifact.exists())
            self.assertIn(
                validation_script.ROLLOVER_GATE_TIMEOUT_REASON,
                __import__(
                    "joulewise.analysis_engine.claims",
                    fromlist=["REDUCER_REASON_CODES"],
                ).REDUCER_REASON_CODES,
            )


if __name__ == "__main__":
    unittest.main()
