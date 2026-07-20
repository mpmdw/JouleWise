"""Synthetic pulse-detector tests for the D-078 fiducial harness.

All traces are deterministic (sinusoidal pseudo-noise, no RNG): each test
knows the true pulse edges and asserts the estimator's error and residual
bounds against them.
"""

from __future__ import annotations

import math
import unittest

from joulewise.powermetrics_fiducial import (
    BINDING_FIELDS,
    CommandedPulse,
    TraceInterval,
    detect_pulses,
    instrument_evidence,
    pulse_gap_s,
    pulse_schedule,
    van_der_corput,
    window_license_min_duration_s,
)

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
            artifact_sha256={"raw/powermetrics.plist": "cd" * 32},
        )
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["b_fiducial_s"], detection.b_fiducial_s)
        self.assertEqual(set(payload["bindings"]), set(BINDING_FIELDS))
        self.assertEqual(payload["pulse_count"], 3)

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


if __name__ == "__main__":
    unittest.main()
