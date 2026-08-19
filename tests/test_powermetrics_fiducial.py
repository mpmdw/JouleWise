"""Synthetic pulse-detector tests for the D-078 fiducial harness.

All traces are deterministic (sinusoidal pseudo-noise, no RNG): each test
knows the true pulse edges and asserts the estimator's error and residual
bounds against them.
"""

from __future__ import annotations

import copy
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from decimal import Decimal, ROUND_HALF_EVEN
import io
import importlib
import math
import json
import hashlib
import subprocess
import tempfile
import threading
import unittest
import sys
from dataclasses import replace
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Mapping
from unittest.mock import patch

from joulewise import calibration_ledger as ledger_module
from joulewise import powermetrics_fiducial as fiducial_module
from joulewise.powermetrics_fiducial import (
    BINDING_FIELDS,
    CLOCK_ANCHOR_UNRESOLVED,
    DETECTION_NONCONVERGENT,
    DETECTION_PROJECTION_CELL_BUDGET,
    LEGACY_PROTOCOL_ID,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V2_SHA256,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    RESIDUAL_REGION_METHOD,
    CommandedPulse,
    TraceInterval,
    authenticate_protocol_schedule,
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

try:
    stage1_test_module = importlib.import_module("tests.test_arm_readiness")
    from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID
except ModuleNotFoundError as exc:  # Stage-1 lands via the lead-owned main sync.
    if exc.name not in {
        "tests.test_arm_readiness",
        "tests.test_arm_readiness_schemas",
    }:
        raise
    stage1_test_module = None
    TEST_BOOT_SESSION_ID = None

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

    def test_phase_locked_uniform_gap_schedule_refuses_authentication(self) -> None:
        pulses = commanded(
            [(5.0 + 2.5 * index, 6.0 + 2.5 * index) for index in range(5)]
        )
        trace = [TraceInterval(start_s=0.0, end_s=pulses[-1].off_s + 5.0, power_w=2.0)]
        with self.assertRaisesRegex(ValueError, "gaps disagree"):
            authenticate_protocol_schedule(pulses, trace)

    def test_vdc_schedule_passes_authentication(self) -> None:
        scheduled = pulse_schedule(5, start_s=5.0)
        pulses = commanded(scheduled)
        trace = [TraceInterval(start_s=0.0, end_s=pulses[-1].off_s + 5.0, power_w=2.0)]
        authenticate_protocol_schedule(pulses, trace)

    def test_rederivation_authenticates_executed_schedule(self) -> None:
        from tests.test_reduce import self_consistent_calibration

        first_endpoint_s = 1_784_490_850.05
        first_pulse_s = first_endpoint_s + 14.95
        uniform_edges = [
            (first_pulse_s + 2.5 * index, first_pulse_s + 2.5 * index + 1.0)
            for index in range(40)
        ]
        uniform_evidence, uniform_raw, uniform_events = self_consistent_calibration(
            first_endpoint_s=first_endpoint_s,
            commanded_edges=uniform_edges,
        )
        self.assertEqual(uniform_evidence["status"], "valid")
        with self.assertRaisesRegex(ValueError, "gaps disagree"):
            fiducial_module.rederive_detection_from_artifacts(
                uniform_raw,
                uniform_events,
                uniform_evidence["clock_anchor"],
                protocol_id=PROTOCOL_V2_ID,
            )

        vdc_evidence, vdc_raw, vdc_events = self_consistent_calibration()
        accepted = fiducial_module.rederive_detection_from_artifacts(
            vdc_raw,
            vdc_events,
            vdc_evidence["clock_anchor"],
            protocol_id=PROTOCOL_V2_ID,
        )
        self.assertTrue(accepted.all_pulses_detected, accepted.reasons)
        self.assertIsNotNone(accepted.b_fiducial_s)

    def test_negative_resolution_stamp_previously_understated_bound_now_refuses(
        self,
    ) -> None:
        from tests.test_reduce import self_consistent_calibration

        evidence, raw, events = self_consistent_calibration(
            protocol_id=PROTOCOL_V2_ID
        )
        valid = fiducial_module.rederive_detection_from_artifacts(
            raw,
            events,
            evidence["clock_anchor"],
            protocol_id=PROTOCOL_V2_ID,
        )
        rows = [json.loads(line) for line in events.splitlines()]
        for row in rows:
            stamp = row["metadata"]["clock_stamp"]
            stamp["wall_resolution_s"] = -2e-6
            stamp["monotonic_resolution_s"] = -2e-6
        mutated_events = "".join(
            json.dumps(row, sort_keys=True) + "\n" for row in rows
        ).encode("utf-8")

        # Pin the former defect shape on the explicitly frozen v1 replay arm:
        # its historical arithmetic produces a three-microsecond smaller
        # bound, while current strict v2/v3 acceptance below refuses it.
        understated = fiducial_module.rederive_detection_from_artifacts(
            raw,
            mutated_events,
            evidence["clock_anchor"],
            protocol_id=LEGACY_PROTOCOL_ID,
        )
        self.assertGreater(valid.b_fiducial_s, understated.b_fiducial_s)
        self.assertAlmostEqual(
            valid.b_fiducial_s - understated.b_fiducial_s,
            3e-6,
            places=12,
        )
        with self.assertRaisesRegex(ValueError, "ClockStamp"):
            fiducial_module.rederive_detection_from_artifacts(
                raw,
                mutated_events,
                evidence["clock_anchor"],
                protocol_id=PROTOCOL_V2_ID,
            )
        with self.assertRaisesRegex(ValueError, "half-width"):
            fiducial_module.clock_stamp_half_width_s(
                SimpleNamespace(
                    monotonic_before_s=1.0,
                    monotonic_after_s=1.0 + 2e-6,
                    wall_resolution_s=-2e-6,
                    monotonic_resolution_s=-2e-6,
                )
            )


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

    # D-138 parameter ruling, 2026-08-18.  The retired 100,000-cell budget was
    # calibrated from the 17,505-cell synthetic acceptance trace and is
    # exhausted by every real corpus-grade capture: the complete retained
    # unique protocol-v3 corpus (n=34 full 59-pulse convergences) spans
    # 112,205..137,189 evaluated cells.  These two constants are the ruled
    # basis; a silent revert of the production default must fail here.
    RULED_DETECTION_CELL_BUDGET = 165_000
    RETIRED_DETECTION_CELL_BUDGET = 100_000
    OBSERVED_CORPUS_MAX_CELLS = 137_189

    def test_detection_cell_budget_is_the_ruled_corpus_calibrated_value(
        self,
    ) -> None:
        self.assertEqual(
            DETECTION_PROJECTION_CELL_BUDGET,
            self.RULED_DETECTION_CELL_BUDGET,
            "the D-138 detection budget ruling pins 165,000 cells; changing it "
            "rotates the estimator pin and requires a D-079 reissue plus the "
            "atomic _v2 successor-family re-freeze",
        )
        # The retired budget sits below the observed corpus maximum, so it
        # could never have admitted a corpus-grade trace.
        self.assertLess(
            self.RETIRED_DETECTION_CELL_BUDGET,
            self.OBSERVED_CORPUS_MAX_CELLS,
        )
        # The ruled budget clears the observed maximum by more than the entire
        # observed min-to-max spread (24,984 cells).
        self.assertGreater(
            DETECTION_PROJECTION_CELL_BUDGET - self.OBSERVED_CORPUS_MAX_CELLS,
            24_984,
        )

    def test_production_default_budget_spends_past_the_retired_ceiling(
        self,
    ) -> None:
        # Behavioural kill evidence for the ruling: with no injected budget the
        # production default must keep evaluating past the retired 100,000-cell
        # ceiling and stop exactly at the ruled bound, still fail-closed.
        trace, pulses = self.make_case(shift_s=0.0, count=1)
        with patch.object(
            fiducial_module,
            "_pulse_loss_cell_lower_bound",
            return_value=0.0,
        ):
            detection = detect_pulses(trace, pulses)
        self.assertGreater(
            detection.projection_evaluated_cell_count,
            self.RETIRED_DETECTION_CELL_BUDGET,
        )
        self.assertEqual(
            detection.projection_evaluated_cell_count,
            DETECTION_PROJECTION_CELL_BUDGET,
        )
        self.assertEqual(
            detection.projection_evaluated_cell_budget,
            DETECTION_PROJECTION_CELL_BUDGET,
        )
        self.assertEqual(
            detection.projection_budget_trigger,
            "evaluated_cell_budget",
        )
        # Fail-closed behaviour is retained at the raised budget.
        self.assertFalse(detection.all_pulses_detected)
        self.assertIsNone(detection.b_fiducial_s)
        self.assertEqual(detection.fits, ())
        self.assertEqual(detection.reasons, (DETECTION_NONCONVERGENT,))

    def test_flat_loss_projection_exhausts_deterministic_cell_budget(self) -> None:
        # A zero lower bound prevents every branch-and-bound prune. Without a
        # work limit this one-pulse analog expands toward the full 2^28 leaf
        # tree; the small injected limit exercises the production counter.
        trace, pulses = self.make_case(shift_s=0.0, count=1)
        outcomes = []
        for _repeat in range(2):
            with patch.object(
                fiducial_module,
                "_pulse_loss_cell_lower_bound",
                return_value=0.0,
            ):
                outcomes.append(
                    detect_pulses(
                        trace,
                        pulses,
                        projection_cell_budget=31,
                    )
                )

        for detection in outcomes:
            self.assertFalse(detection.all_pulses_detected)
            self.assertIsNone(detection.b_fiducial_s)
            self.assertEqual(detection.fits, ())
            self.assertEqual(detection.reasons, (DETECTION_NONCONVERGENT,))
            self.assertEqual(detection.projection_evaluated_cell_count, 31)
            self.assertEqual(detection.projection_evaluated_cell_budget, 31)
            self.assertEqual(
                detection.projection_budget_trigger,
                "evaluated_cell_budget",
            )
        self.assertEqual(
            (
                outcomes[0].projection_evaluated_cell_count,
                outcomes[0].projection_disposition,
            ),
            (
                outcomes[1].projection_evaluated_cell_count,
                outcomes[1].projection_disposition,
            ),
        )
        payload = instrument_evidence(
            outcomes[0],
            bindings={},
            validation_id="flat-loss-budget",
            artifact_sha256={},
            protocol_pulse_count=1,
            protocol_id=LEGACY_PROTOCOL_ID,
        )
        self.assertEqual(payload["status"], "invalid")
        self.assertIn(DETECTION_NONCONVERGENT, payload["reasons"])
        self.assertEqual(
            payload["detection_projection"],
            {
                "disposition": DETECTION_NONCONVERGENT,
                "cell_budget": 31,
                "wall_budget_s": 120.0,
                "diagnostics": {
                    "reproducible": True,
                    "evaluated_cell_count": 31,
                    "trigger": "evaluated_cell_budget",
                },
            },
        )

    def test_wall_deadline_is_nonreproducible_host_pathology_diagnostic(
        self,
    ) -> None:
        trace, pulses = self.make_case(shift_s=0.0, count=1)
        with patch.object(
            fiducial_module,
            "_pulse_loss_cell_lower_bound",
            return_value=0.0,
        ):
            deterministic = detect_pulses(
                trace,
                pulses,
                projection_cell_budget=31,
            )
        with (
            patch.object(
                fiducial_module,
                "_pulse_loss_cell_lower_bound",
                return_value=0.0,
            ),
            patch.object(fiducial_module.time, "monotonic", return_value=1e99),
        ):
            wall = detect_pulses(
                trace,
                pulses,
                projection_cell_budget=31,
            )

        def evidence_payload(detection):
            return instrument_evidence(
                detection,
                bindings={},
                validation_id="wall-pathology-diagnostic",
                artifact_sha256={},
                protocol_pulse_count=1,
                protocol_id=LEGACY_PROTOCOL_ID,
            )

        deterministic_evidence = evidence_payload(deterministic)
        wall_evidence = evidence_payload(wall)
        deterministic_projection = deterministic_evidence[
            "detection_projection"
        ]
        wall_projection = wall_evidence["detection_projection"]
        reproducible_fields = ("disposition", "cell_budget", "wall_budget_s")
        self.assertEqual(
            {key: deterministic_projection[key] for key in reproducible_fields},
            {key: wall_projection[key] for key in reproducible_fields},
        )
        self.assertEqual(
            deterministic_projection["diagnostics"],
            {
                "reproducible": True,
                "evaluated_cell_count": 31,
                "trigger": "evaluated_cell_budget",
            },
        )
        self.assertEqual(
            wall_projection["diagnostics"],
            {
                "reproducible": False,
                "evaluated_cell_count": 0,
                "trigger": "wall_deadline",
            },
        )
        self.assertEqual(wall.fits, ())
        self.assertIsNone(wall.b_fiducial_s)
        self.assertEqual(wall.reasons, (DETECTION_NONCONVERGENT,))
        self.assertEqual(wall_evidence["status"], "invalid")
        self.assertIsNone(wall_evidence["b_fiducial_s"])
        self.assertEqual(wall_evidence["pulses"], [])

    def test_unresolved_anchor_bypasses_every_projection_cell(self) -> None:
        trace, pulses = self.make_case(shift_s=0.0, count=3)
        with patch.object(
            fiducial_module,
            "_accepted_region_projection",
            side_effect=AssertionError("projection must be skipped"),
        ) as projection:
            detection = detect_pulses(
                trace,
                pulses,
                projection_bypass_reason=CLOCK_ANCHOR_UNRESOLVED,
            )
        projection.assert_not_called()
        self.assertEqual(
            detection.projection_disposition,
            CLOCK_ANCHOR_UNRESOLVED,
        )
        self.assertEqual(detection.projection_evaluated_cell_count, 0)
        self.assertEqual(
            detection.projection_evaluated_cell_budget,
            DETECTION_PROJECTION_CELL_BUDGET,
        )
        self.assertEqual(detection.reasons, (CLOCK_ANCHOR_UNRESOLVED,))
        self.assertEqual(detection.fits, ())

    def test_unresolved_anchor_bypass_refuses_nonzero_anchor_bound(self) -> None:
        trace, pulses = self.make_case(shift_s=0.0, count=3)
        with self.assertRaisesRegex(ValueError, "trace_anchor_bound_s == 0"):
            detect_pulses(
                trace,
                pulses,
                trace_anchor_bound_s=0.001,
                projection_bypass_reason=CLOCK_ANCHOR_UNRESOLVED,
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

    def test_healthy_evidence_bytes_match_pre_budget_baseline(self) -> None:
        bindings = self.bindings(
            os_build="25F84",
            mlx_version="0.29.3",
            pulse_protocol_id=PROTOCOL_ID,
            estimator_revision=RESIDUAL_REGION_METHOD,
            protocol_sha256=PROTOCOL_V3_SHA256,
        )
        payload = instrument_evidence(
            self.make_detection(),
            bindings=bindings,
            validation_id="full-writer-artifact-compare",
            artifact_sha256={
                "raw/powermetrics.plist": "cd" * 32,
                "events.jsonl": "ef" * 32,
                "power_trace.csv": "01" * 32,
            },
            protocol_pulse_count=3,
            protocol_id=PROTOCOL_ID,
            capture_wall_time_s=1_784_491_000.25,
        )
        payload["clock_anchor"] = {
            "method": fiducial_module.CLOCK_METHOD_V2,
            "effective_clock_anchor_bound_s": 0.0025,
            "diagnostic": "fixed-review-fixture",
        }
        payload["clock_anchor_resolved"] = True
        raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        self.assertNotIn("detection_projection", payload)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(len(raw), 3923)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "254b86581074063da7622fd792d520d53726e2b3e4744a4a0647a4fd68cc02c7",
        )

    def test_launch_lineage_stamping_preserves_projection_disposition(self) -> None:
        projected = replace(
            self.make_detection(),
            all_pulses_detected=False,
            b_fiducial_s=None,
            fits=(),
            reasons=(DETECTION_NONCONVERGENT,),
            projection_evaluated_cell_count=31,
            projection_evaluated_cell_budget=31,
            projection_disposition=DETECTION_NONCONVERGENT,
            projection_budget_trigger="evaluated_cell_budget",
        )
        kwargs = {
            "bindings": {},
            "validation_id": "launch-bound-projection",
            "artifact_sha256": {},
            "protocol_pulse_count": 0,
            "protocol_id": LEGACY_PROTOCOL_ID,
        }
        legacy = instrument_evidence(projected, **kwargs)
        lineage = {
            "schema_version": "joulewise.launch_lineage.v1",
            "pack_id": "pack-stage-2",
            "completion": None,
        }
        stamped = instrument_evidence(
            projected,
            launch_lineage=lineage,
            **kwargs,
        )

        self.assertEqual(
            stamped["detection_projection"], legacy["detection_projection"]
        )
        self.assertEqual(stamped["launch_lineage"], lineage)
        without_lineage = dict(stamped)
        without_lineage.pop("launch_lineage")
        self.assertEqual(without_lineage, legacy)
        lineage["pack_id"] = "mutated-after-serialization"
        self.assertEqual(stamped["launch_lineage"]["pack_id"], "pack-stage-2")

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

    def test_projection_disposition_with_fitted_evidence_refuses_serialization(
        self,
    ) -> None:
        inconsistent = replace(
            self.make_detection(),
            reasons=(DETECTION_NONCONVERGENT,),
            projection_evaluated_cell_count=31,
            projection_evaluated_cell_budget=31,
            projection_disposition=DETECTION_NONCONVERGENT,
            projection_budget_trigger="evaluated_cell_budget",
        )
        with self.assertRaisesRegex(
            ValueError,
            "detection_nonconvergent: projection disposition conflicts with "
            "fitted evidence",
        ):
            instrument_evidence(
                inconsistent,
                bindings=self.bindings(),
                validation_id="inconsistent-projection",
                artifact_sha256={
                    "raw/powermetrics.plist": "cd" * 32,
                    "events.jsonl": "ef" * 32,
                },
                protocol_pulse_count=3,
                protocol_id=LEGACY_PROTOCOL_ID,
            )

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


class CalibrationLaunchBoundaryTests(unittest.TestCase):
    def test_non_marker_config_keeps_launch_binding_dormant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "acceptance.json"
            config.write_text('{"schema_version":"legacy"}\n', encoding="utf-8")
            self.assertIsNone(
                validation_script.authenticate_calibration_writer_launch_lineage(
                    root / "wrong-output-name",
                    session_id=None,
                    slot=None,
                    attempt_id=None,
                    source_config_path=config,
                )
            )

    def test_marker_checks_output_basename_before_locator_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "acceptance.json"
            config.write_text(
                '{"run_metadata":{"tags":["launch_lineage_required"]}}\n',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError) as caught:
                validation_script.authenticate_calibration_writer_launch_lineage(
                    root / "wrong-output-name",
                    session_id="session-1",
                    slot="pre",
                    attempt_id="attempt-pre",
                    source_config_path=config,
                )
            self.assertEqual(
                caught.exception.reason_code, "launch_binding_mismatch"
            )

    def test_external_acceptance_requires_authenticated_plan_path_and_digest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "pack"
            pack.mkdir()
            config = root / "acceptance.json"
            config.write_text('{"run_metadata":{"tags":[]}}\n', encoding="utf-8")
            digest = hashlib.sha256(config.read_bytes()).hexdigest()
            plan = {
                "acceptance_policy": {
                    "issued_acceptance": {
                        "path": "acceptance.json",
                        "artifact_sha256": digest,
                    }
                }
            }
            (pack / "plan_tree.json").write_text(json.dumps(plan), encoding="utf-8")
            authentication = {"pack_root": str(pack), "config_inventory": {}}
            with patch.object(validation_script, "REPO_ROOT", root):
                validation_script._authenticate_calibration_source_config(
                    authentication,
                    config_path=config,
                    config_raw=config.read_bytes(),
                )
                plan["acceptance_policy"]["issued_acceptance"][
                    "artifact_sha256"
                ] = "0" * 64
                (pack / "plan_tree.json").write_text(
                    json.dumps(plan), encoding="utf-8"
                )
                with self.assertRaises(ValueError) as caught:
                    validation_script._authenticate_calibration_source_config(
                        authentication,
                        config_path=config,
                        config_raw=config.read_bytes(),
                    )
            self.assertEqual(
                caught.exception.reason_code, "launch_binding_mismatch"
            )

    def test_marker_missing_locator_refuses_before_ledger_construction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "acceptance.json"
            config.write_text(
                json.dumps(
                    {"run_metadata": {"tags": ["launch_lineage_required"]}}
                ),
                encoding="utf-8",
            )
            output_root = root / "runs" / "instrument_validation"
            output_root.parent.mkdir()

            class ForbiddenLedgerLifecycle:
                def __init__(self, **_kwargs):
                    raise AssertionError("ledger construction must not occur")

            stderr = io.StringIO()
            with (
                patch.object(validation_script, "verify_frozen_protocol", return_value=True),
                patch.object(
                    validation_script,
                    "DEFAULT_ACCEPTANCE_BOUND_PATH",
                    config,
                ),
                patch.object(
                    validation_script,
                    "_CaptureLedgerLifecycle",
                    ForbiddenLedgerLifecycle,
                ),
                redirect_stderr(stderr),
            ):
                result = validation_script.main(
                    [
                        "--allow-live",
                        "--output-root",
                        str(output_root),
                        "--session-id",
                        "session-1",
                        "--slot",
                        "pre",
                        "--attempt-id",
                        "attempt-pre",
                        "--power-policy",
                        "ac_high_power",
                    ]
                )

            self.assertEqual(result, 2)
            self.assertIn("launch_consumption_missing", stderr.getvalue())
            self.assertFalse(output_root.exists())


@unittest.skipUnless(
    stage1_test_module is not None
    and hasattr(validation_script.arm_readiness_module, "authenticate_launch_lineage"),
    "stage-1 launch-lineage machinery awaits lead-owned main sync",
)
class CalibrationLaunchAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        assert stage1_test_module is not None
        self.stage1 = stage1_test_module.LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        self.stage1.setUp()
        self.addCleanup(self.stage1.doCleanups)
        self.readiness = validation_script.arm_readiness_module
        self.config = self.stage1.pack / "calibration-acceptance.json"
        self.config.write_bytes(
            self.readiness.render_json(
                {
                    "schema_version": "synthetic.calibration_acceptance.v1",
                    "run_metadata": {
                        "tags": ["launch_lineage_required"]
                    },
                }
            )
        )
        self.output_root = (
            Path(self.stage1.arm["arm_context"]["claim_runs_root"])
            / "instrument_validation"
        )

    @contextmanager
    def _authentication_environment(
        self,
        *,
        boot_session_id: str | None = None,
        inventory: Mapping[str, str] | None = None,
    ):
        if boot_session_id is None:
            boot_session_id = str(TEST_BOOT_SESSION_ID)
        if inventory is None:
            inventory = {
                self.config.relative_to(self.stage1.pack).as_posix():
                hashlib.sha256(self.config.read_bytes()).hexdigest()
            }
        with (
            patch.object(
                self.readiness,
                "_current_boot_session_id",
                return_value=boot_session_id,
            ),
            patch.object(
                self.readiness,
                "_git_text",
                return_value=self.stage1.arm["reviewed_main"]["head_commit"],
            ),
            patch.object(
                self.readiness,
                "_authenticated_pack_config_inventory",
                return_value=dict(inventory),
            ),
        ):
            yield

    def _authenticate(
        self,
        *,
        output_root: Path | None = None,
        session_id: str = "session-1",
        slot: str = "pre",
        attempt_id: str = "attempt-pre",
        boot_session_id: str | None = None,
        inventory: Mapping[str, str] | None = None,
    ) -> dict[str, object] | None:
        with self._authentication_environment(
            boot_session_id=boot_session_id,
            inventory=inventory,
        ):
            return validation_script.authenticate_calibration_writer_launch_lineage(
                self.output_root if output_root is None else output_root,
                session_id=session_id,
                slot=slot,
                attempt_id=attempt_id,
                source_config_path=self.config,
            )

    def _assert_refusal(self, code: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as caught:
            self._authenticate(**kwargs)
        self.assertEqual(caught.exception.reason_code, code)

    def test_real_settle_locator_authenticates_all_writer_bindings(self) -> None:
        _consumption_path, settled = self.stage1._settle()
        authenticated = self._authenticate()
        assert authenticated is not None
        self.assertEqual(
            authenticated["launch_lineage"], settled["launch_lineage"]
        )
        self.assertEqual(
            authenticated["selected_config_sha256"],
            hashlib.sha256(self.config.read_bytes()).hexdigest(),
        )

    def test_missing_locator_refuses_registered_missing_code(self) -> None:
        self._assert_refusal("launch_consumption_missing")

    def test_corrupt_locator_refuses_registered_invalid_code(self) -> None:
        self.stage1._settle()
        locator = (
            self.output_root.parent
            / self.readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        locator.write_bytes(locator.read_bytes() + b" ")
        self._assert_refusal("launch_consumption_invalid")

    def test_wrong_root_refuses_binding_mismatch(self) -> None:
        self.stage1._settle()
        source = (
            self.output_root.parent
            / self.readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        alien_root = Path(self.stage1.temporary.name) / "alien-root"
        alien_root.mkdir()
        alien = alien_root / source.name
        alien.write_bytes(source.read_bytes())
        alien.with_name(f"{alien.name}.sha256").write_bytes(
            source.with_name(f"{source.name}.sha256").read_bytes()
        )
        self._assert_refusal(
            "launch_binding_mismatch",
            output_root=alien_root / "instrument_validation",
        )

    def test_wrong_boot_refuses_binding_mismatch(self) -> None:
        self.stage1._settle()
        self._assert_refusal(
            "launch_binding_mismatch",
            boot_session_id="00000000-0000-4000-8000-000000000099",
        )

    def test_wrong_bracket_session_refuses_binding_mismatch(self) -> None:
        self.stage1._settle()
        self._assert_refusal(
            "launch_binding_mismatch", session_id="session-other"
        )

    def test_wrong_attempt_for_slot_refuses_binding_mismatch(self) -> None:
        self.stage1._settle()
        self._assert_refusal(
            "launch_binding_mismatch",
            slot="post",
            attempt_id="attempt-pre",
        )

    def test_unauthenticated_config_refuses_binding_mismatch(self) -> None:
        self.stage1._settle()
        self._assert_refusal("launch_binding_mismatch", inventory={})

    def test_mixed_root_lineages_refuse_conflict(self) -> None:
        self.stage1._settle()
        assert stage1_test_module is not None
        second = stage1_test_module.LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        second.setUp()
        try:
            second._settle()
            second_locator_path = (
                Path(second.arm["arm_context"]["bound_runs_root"])
                / self.readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            )
            second_locator = self.readiness.parse_json_bytes(
                second_locator_path.read_bytes(), require_canonical=True
            )
        finally:
            second.doCleanups()
        bound_locator_path = (
            Path(self.stage1.arm["arm_context"]["bound_runs_root"])
            / self.readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        mixed = self.readiness.parse_json_bytes(
            bound_locator_path.read_bytes(), require_canonical=True
        )
        mixed["launch_lineage"] = copy.deepcopy(
            second_locator["launch_lineage"]
        )
        mixed_raw = self.readiness.render_json(mixed)
        bound_locator_path.write_bytes(mixed_raw)
        bound_locator_path.with_name(
            f"{bound_locator_path.name}.sha256"
        ).write_bytes(
            self.readiness.gnu_sidecar(
                hashlib.sha256(mixed_raw).hexdigest(),
                bound_locator_path.name,
            )
        )
        self._assert_refusal("launch_lineage_conflict")


class FrozenProtocolTests(unittest.TestCase):
    def test_preflight_screen_is_derived_bit_exactly_from_real_artifact(self) -> None:
        # The ACTIVE generation since the anchor-v3 science reissue.  The
        # estimator-bearing branch was fail-closed while the issued pin was
        # stale; the atomic Phase-2 acceptance/pin re-freeze is exactly what
        # cures it, so this unit proves the cured state end to end.
        path = Path(
            "configs/calibration/calibration_acceptance_d079_v2_n17_r3.json"
        )
        raw = path.read_bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "73f022633e7bc22e9e129617f3f2ad8797293adaff3b53923dc41f75da2ae917",
        )
        artifact = json.loads(raw)
        self.assertEqual(
            artifact["acceptance_id"], "d079_calibration_acceptance_v2_n17_r3"
        )
        self.assertEqual(artifact["derivation_corpus"]["n"], 17)
        derivation = artifact["decimal_derivation"]
        rounding = derivation["rounding"]["preflight_level_screen"]
        expected = Decimal(
            derivation["source_statistics"]["maximum_s"]
        ).quantize(Decimal(rounding["quantum_s"]), rounding=ROUND_HALF_EVEN)
        # The artifact's own estimator pins are the live ones: no isolation
        # patch, so this also proves the staleness guard is genuinely cured.
        self.assertEqual(
            validation_script._current_estimator_code_sha256(),
            dict(artifact["prospective_rederivation"]["estimator_code_sha256"]),
        )
        observed = validation_script._derive_preflight_systematic_screen_s(
            artifact["identity_epoch"], acceptance_path=path
        )
        self.assertIsInstance(observed, Decimal)
        self.assertEqual(observed.as_tuple(), expected.as_tuple())
        self.assertEqual(
            validation_script.PREFLIGHT_SYSTEMATIC_SCREEN_S,
            observed,
            "the branch-wide convenience value derives from the issued "
            "artifact once its estimator pin is fresh",
        )
        # Every retained predecessor generation keeps its own exact bytes and
        # stays stale-pinned: a superseded generation must never be able to
        # serve as live authority just because a caller names its path.
        for relative, expected_sha256 in (
            (
                "configs/calibration/calibration_acceptance_d079_v2.json",
                "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
            ),
            (
                "configs/calibration/calibration_acceptance_d079_v2_r2.json",
                "3c92dd664cdf138860f2bb29e8dcf8397d5d1608b24d65e3de62a78d279e0d6e",
            ),
        ):
            predecessor = Path(relative)
            self.assertEqual(
                hashlib.sha256(predecessor.read_bytes()).hexdigest(),
                expected_sha256,
                relative,
            )
            with self.assertRaisesRegex(
                validation_script._AcceptancePreflightError,
                "acceptance_artifact_stale",
            ):
                validation_script._derive_preflight_systematic_screen_s(
                    artifact["identity_epoch"], acceptance_path=predecessor
                )

    def test_writer_has_no_copied_preflight_scalar_and_comparison_is_derived(self) -> None:
        source = Path(validation_script.__file__).read_text(encoding="utf-8")
        self.assertNotIn(
            'PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.032898493715362")',
            source,
        )
        self.assertNotIn(
            'PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")',
            source,
        )
        comparison = "Decimal(bound_lexeme) > preflight_systematic_screen_s"
        self.assertEqual(source.count(comparison), 1)
        self.assertNotIn(
            "Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S",
            source,
        )

    def test_acceptance_artifact_refusals_are_distinct_and_emit_no_output(self) -> None:
        real_path = Path(
            "configs/calibration/calibration_acceptance_d079_v2.json"
        )
        real_raw = real_path.read_bytes()
        real_artifact = json.loads(real_raw)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.json"
            tampered = root / "tampered.json"
            tampered.write_bytes(real_raw + b" ")
            exact = root / "exact.json"
            exact.write_bytes(real_raw)
            cases = (
                ("missing", missing, real_artifact["identity_epoch"], "acceptance_artifact_missing"),
                ("tampered", tampered, real_artifact["identity_epoch"], "acceptance_artifact_unauthenticated"),
                (
                    "wrong_epoch",
                    exact,
                    {**real_artifact["identity_epoch"], "os_build": "25F85"},
                    "acceptance_artifact_epoch_mismatch",
                ),
            )
            observed_reasons = []
            for name, acceptance_path, epoch, expected_reason in cases:
                with self.subTest(case=name):
                    identity_path = root / f"{name}-identity.json"
                    identity_path.write_text(json.dumps(epoch), encoding="utf-8")
                    output_root = root / f"{name}-output"
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with (
                        patch.object(
                            validation_script,
                            "DEFAULT_ACCEPTANCE_BOUND_PATH",
                            acceptance_path,
                        ),
                        patch.object(
                            validation_script,
                            "_current_estimator_code_sha256",
                            return_value=dict(
                                real_artifact["prospective_rederivation"][
                                    "estimator_code_sha256"
                                ]
                            ),
                        ),
                        redirect_stdout(stdout),
                        redirect_stderr(stderr),
                    ):
                        return_code = validation_script.main(
                            [
                                "--allow-live",
                                "--power-policy",
                                "ac_high_power",
                                "--identity-epoch-json-for-test",
                                str(identity_path),
                                "--output-root",
                                str(output_root),
                            ]
                        )
                    self.assertEqual(return_code, 2)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertFalse(output_root.exists())
                    refusal = json.loads(stderr.getvalue())
                    self.assertEqual(
                        refusal["context"]["reason"], expected_reason
                    )
                    observed_reasons.append(refusal["context"]["reason"])
            self.assertEqual(len(set(observed_reasons)), len(cases))

    def test_estimator_byte_drift_refuses_acceptance_as_stale(self) -> None:
        artifact = json.loads(
            Path(
                "configs/calibration/calibration_acceptance_d079_v2.json"
            ).read_bytes()
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity_path = root / "identity.json"
            identity_path.write_text(
                json.dumps(artifact["identity_epoch"]), encoding="utf-8"
            )
            output_root = root / "output"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                patch.object(
                    validation_script,
                    "_current_estimator_code_sha256",
                    return_value={"unexpected": "0" * 64},
                ),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                return_code = validation_script.main(
                    [
                        "--allow-live",
                        "--power-policy",
                        "ac_high_power",
                        "--identity-epoch-json-for-test",
                        str(identity_path),
                        "--output-root",
                        str(output_root),
                    ]
                )
            self.assertEqual(return_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertFalse(output_root.exists())
            refusal = json.loads(stderr.getvalue())
            self.assertEqual(
                refusal["context"]["reason"], "acceptance_artifact_stale"
            )

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


class WriterLedgerIntegrationTests(unittest.TestCase):
    def _open_session(self, root: Path):
        ledger = root / "ledger.jsonl"
        pin = root / "head.json"
        pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": ledger_module.GENESIS_DIGEST,
                    "ledger_schema": ledger_module.LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": RESIDUAL_REGION_METHOD,
            "pulse_protocol_id": PROTOCOL_ID,
        }
        t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
        t1.update(epoch)
        custody = {
            slot: root / "instrument_validation" / f"session-writer-{slot}"
            for slot in ledger_module.BRACKET_SESSION_SLOTS
        }
        receipt = ledger_module.append_bracket_session_receipt(
            ledger,
            session_id="session-writer",
            window_id="window-writer",
            plan_id="plan-writer",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-writer",
            runs_root=root,
            slots={
                slot: {
                    "attempt_id": f"session-writer-{slot}",
                    "custody_locator": str(custody[slot]),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for slot in ledger_module.BRACKET_SESSION_SLOTS
            },
            head_pin_path=pin,
            require_committed_pin=False,
        )
        return ledger, pin, epoch, t1, custody, receipt

    def _lifecycle(
        self,
        ledger: Path,
        pin: Path,
        epoch: dict,
        t1: dict,
        custody: dict[str, Path],
        slot: str,
    ) -> validation_script._CaptureLedgerLifecycle:
        return validation_script._CaptureLedgerLifecycle(
            ledger_path=ledger,
            head_pin_path=pin,
            attempt_id=f"session-writer-{slot}",
            custody_locator=str(custody[slot]),
            identity_epoch=epoch,
            t1_bindings=t1,
            session_id="session-writer",
            slot=slot,
            require_committed_pin=False,
        )

    def test_session_writer_authenticates_reservation_before_capture_without_ordinary_append(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, pin, epoch, t1, custody, capability = self._open_session(
                Path(tmp)
            )
            lifecycle = self._lifecycle(
                ledger, pin, epoch, t1, custody, "pre"
            )
            with patch.object(validation_script, "append_pending_receipt") as ordinary:
                lifecycle.begin()
            ordinary.assert_not_called()
            receipts = [json.loads(line) for line in ledger.read_text().splitlines()]
            business_by_event = {
                receipt["event"]: receipt
                for receipt in receipts
                if receipt.get("schema_version")
                == ledger_module.BRACKET_SESSION_SCHEMA
            }
            expected_events = {
                ledger_module.BRACKET_SESSION_OPEN_EVENT,
                ledger_module.BRACKET_SESSION_SLOT_CLAIM_EVENT,
            }
            self.assertEqual(set(business_by_event), expected_events)
            self.assertEqual(
                business_by_event[ledger_module.BRACKET_SESSION_OPEN_EVENT],
                capability,
            )
            self.assertFalse(custody["pre"].exists())
            with self.assertRaisesRegex(
                ledger_module.CalibrationLedgerError,
                "calibration_live_writer_contention",
            ):
                ledger_module.CalibrationWriterLease(ledger).acquire()

            mismatched = validation_script._CaptureLedgerLifecycle(
                ledger_path=ledger,
                head_pin_path=pin,
                attempt_id="not-the-reserved-attempt",
                custody_locator=str(custody["pre"]),
                identity_epoch=epoch,
                t1_bindings=t1,
                session_id="session-writer",
                slot="pre",
                require_committed_pin=False,
            )
            with self.assertRaisesRegex(
                ledger_module.CalibrationLedgerError, "exact reserved"
            ):
                mismatched.begin()
            self.assertEqual(len(ledger.read_text().splitlines()), 4)
            lifecycle.abandon("test_exact_reservation_cleanup")
            with ledger_module.CalibrationWriterLease(ledger):
                self.assertTrue(True)

    def test_concurrent_double_arm_accepts_exactly_one_and_loser_cannot_abort_winner(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, pin, epoch, t1, custody, _capability = self._open_session(
                Path(tmp)
            )
            lifecycles = [
                self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
                for _index in range(2)
            ]
            outcomes: list[tuple[str, object]] = []
            both_attempted = threading.Event()
            release_winner = threading.Event()
            winner_abort: list[object] = []

            def arm(lifecycle):
                try:
                    lifecycle.begin()
                except Exception as exc:  # noqa: BLE001 - asserted below
                    outcomes.append(("refused", exc))
                else:
                    outcomes.append(("accepted", lifecycle))
                    if len(outcomes) == 2:
                        both_attempted.set()
                    release_winner.wait(timeout=10)
                    winner_abort.append(
                        lifecycle.abandon("winning_writer_governed_abort")
                    )
                    return
                if len(outcomes) == 2:
                    both_attempted.set()

            threads = [
                threading.Thread(target=arm, args=(lifecycle,))
                for lifecycle in lifecycles
            ]
            for thread in threads:
                thread.start()
            self.assertTrue(both_attempted.wait(timeout=10))

            accepted = [value for status, value in outcomes if status == "accepted"]
            refused = [value for status, value in outcomes if status == "refused"]
            self.assertEqual(len(accepted), 1)
            self.assertEqual(len(refused), 1)
            self.assertEqual(
                refused[0].code,
                __import__(
                    "joulewise.calibration_exits", fromlist=["RefusalCode"]
                ).RefusalCode.LIVE_WRITER_CONTENTION,
            )
            loser = next(lifecycle for lifecycle in lifecycles if not lifecycle.begun)
            self.assertIsNone(loser.abandon("losing_writer_exit"))
            receipts = [json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertFalse(
                any(
                    receipt.get("event") == ledger_module.BRACKET_SESSION_ABORT_EVENT
                    for receipt in receipts
                )
            )
            release_winner.set()
            for thread in threads:
                thread.join(timeout=10)
            self.assertEqual(
                winner_abort[0]["event"], ledger_module.BRACKET_SESSION_ABORT_EVENT
            )

    def test_session_writer_process_death_leaves_claim_then_governed_abort_recovers(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, pin, epoch, t1, custody, _capability = self._open_session(
                Path(tmp)
            )
            pre = self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
            with (
                patch.object(validation_script, "append_pending_receipt") as reserve,
                patch.object(validation_script, "finalize_attempt_receipt") as ordinary,
            ):
                pre.begin()
                (custody["pre"] / "raw").mkdir(parents=True)
                (custody["pre"] / "raw" / "powermetrics.plist").write_bytes(
                    b"raw"
                )
                (custody["pre"] / "events.jsonl").write_text("{}\n")
                (custody["pre"] / "power_trace.csv").write_text("header\n")
                (custody["pre"] / "instrument_evidence.json").write_text("{}\n")
                (custody["pre"] / "manifest.json").write_text("{}\n")
                pre.capture_wall_time_s = "99.0"
                pre.exact_bound_lexeme_s = "0.025"
                _pre_receipt, pre_head = pre.finalize("valid")
                self.assertIsNone(pre_head)

            code = f"""
import os
from pathlib import Path
from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle
lifecycle = _CaptureLedgerLifecycle(
    ledger_path=Path({str(ledger)!r}),
    head_pin_path=Path({str(pin)!r}),
    attempt_id='session-writer-post',
    custody_locator={str(custody['post'])!r},
    identity_epoch={epoch!r},
    t1_bindings={t1!r},
    session_id='session-writer',
    slot='post',
    require_committed_pin=False,
)
lifecycle.begin()
os._exit(23)
"""
            died = subprocess.run(
                [sys.executable, "-c", code],
                cwd=Path(__file__).resolve().parents[1],
                check=False,
            )
            self.assertEqual(died.returncode, 23)
            crashed = ledger_module.load_calibration_ledger_snapshot(
                ledger,
                pin,
                require_committed_pin=False,
                verify_custody=True,
            )
            self.assertIn(
                "calibration_ledger_bracket_session_open",
                crashed.refusal_reasons,
            )
            abort = ledger_module.abort_bracket_session(
                ledger,
                session_id="session-writer",
                reason="post_writer_process_died_after_claim",
            )
            reserve.assert_not_called()
            ordinary.assert_not_called()
            self.assertIsNotNone(abort)
            self.assertEqual(abort["event"], ledger_module.BRACKET_SESSION_ABORT_EVENT)
            self.assertEqual(abort["session_id"], "session-writer")
            self.assertEqual(tuple(abort["finalized_slots"]), ("pre",))
            self.assertEqual(tuple(abort["unused_slots"]), ("post",))
            self.assertEqual(
                abort["reason"], "post_writer_process_died_after_claim"
            )
            self.assertEqual(
                ledger_module.terminal_head_pin_for_session(
                    ledger, session_id="session-writer"
                )["sequence"],
                10,
            )

    def test_main_preserves_symlinked_custody_spelling_used_by_reservation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            physical_root = root / "physical-runs"
            physical_root.mkdir()
            symlinked_root = root / "symlinked-runs"
            symlinked_root.symlink_to(physical_root, target_is_directory=True)
            output_root = symlinked_root / "instrument_validation"
            attempt_id = "session-writer-pre"
            epoch = {
                "os_build": "25F84",
                "hardware_model": "Mac15,9",
                "power_policy": "ac_high_power",
                "sampling_interval_ms": 100,
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "pulse_protocol_id": PROTOCOL_ID,
            }
            t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
            t1.update(epoch)
            _session, normalized_slots = (
                ledger_module.validate_bracket_session_reservation_inputs(
                    session_id="session-writer",
                    window_id="window-writer",
                    plan_id="plan-writer",
                    plan_sha256="a" * 64,
                    evidence_root_id="evidence-writer",
                    runs_root=symlinked_root,
                    slots={
                        slot: {
                            "attempt_id": f"session-writer-{slot}",
                            "custody_locator": str(
                                output_root / f"session-writer-{slot}"
                            ),
                            "identity_epoch": epoch,
                            "t1_bindings": t1,
                        }
                        for slot in ledger_module.BRACKET_SESSION_SLOTS
                    },
                )
            )
            expected_custody = normalized_slots["pre"]["custody_locator"]
            observed: dict[str, str] = {}

            class StopAfterCustodyCapture:
                def __init__(self, **kwargs):
                    observed["custody_locator"] = kwargs["custody_locator"]

                def begin(self):
                    raise ledger_module.CalibrationLedgerError(
                        "stop after custody-path regression observation"
                    )

            mlx_package = ModuleType("mlx")
            mlx_core = ModuleType("mlx.core")
            mlx_core.__version__ = "synthetic"
            mlx_package.core = mlx_core
            with (
                patch.dict(
                    sys.modules,
                    {"mlx": mlx_package, "mlx.core": mlx_core},
                ),
                patch.object(
                    validation_script,
                    "verify_frozen_protocol",
                    return_value=True,
                ),
                patch.object(
                    validation_script,
                    "_sysctl_identity",
                    side_effect=lambda name: (
                        "25F84" if name == "kern.osversion" else "Mac15,9"
                    ),
                ),
                patch.object(
                    validation_script,
                    "sha256_path",
                    return_value="a" * 64,
                ),
                patch.object(
                    validation_script,
                    "SystemClock",
                    return_value=SimpleNamespace(now=lambda: 0.0),
                ),
                patch.object(
                    validation_script,
                    "_CaptureLedgerLifecycle",
                    StopAfterCustodyCapture,
                ),
                patch.object(
                    validation_script,
                    "_current_estimator_code_sha256",
                    return_value=dict(
                        json.loads(
                            validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH.read_text(
                                encoding="utf-8"
                            )
                        )["prospective_rederivation"][
                            "estimator_code_sha256"
                        ]
                    ),
                ),
            ):
                return_code = validation_script.main(
                    [
                        "--allow-live",
                        "--output-root",
                        str(output_root),
                        "--session-id",
                        "session-writer",
                        "--slot",
                        "pre",
                        "--attempt-id",
                        attempt_id,
                        "--power-policy",
                        "ac_high_power",
                    ]
                )

            self.assertEqual(return_code, 2)
            self.assertEqual(observed["custody_locator"], expected_custody)

    def test_writer_repairs_under_lease_and_uses_one_stable_claim(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, pin, epoch, t1, custody, _capability = self._open_session(
                Path(tmp)
            )
            lifecycle = self._lifecycle(
                ledger, pin, epoch, t1, custody, "pre"
            )
            events: list[str] = []
            claim_ids: list[str] = []
            real_repair = validation_script.repair_calibration_ledger
            real_validate = validation_script._validate_reserved_bracket_slot
            real_claim = validation_script.claim_bracket_session_slot

            def observe_repair(*args, **kwargs):
                events.append("repair")
                return real_repair(*args, **kwargs)

            def observe_validate(*args, **kwargs):
                events.append("validate")
                return real_validate(*args, **kwargs)

            def observe_claim(*args, **kwargs):
                claim_ids.append(kwargs["claim_id"])
                return real_claim(*args, **kwargs)

            with (
                patch.object(
                    validation_script,
                    "repair_calibration_ledger",
                    side_effect=observe_repair,
                ),
                patch.object(
                    validation_script,
                    "_validate_reserved_bracket_slot",
                    side_effect=observe_validate,
                ),
                patch.object(
                    validation_script,
                    "claim_bracket_session_slot",
                    side_effect=observe_claim,
                ),
            ):
                lifecycle.begin()
            self.assertEqual(events, ["validate", "repair", "validate"])
            self.assertEqual(claim_ids, [lifecycle.claim_id])
            self.assertEqual(
                lifecycle.claim_id,
                ledger_module.stable_bracket_claim_id(
                    session_id="session-writer",
                    slot="pre",
                    attempt_id="session-writer-pre",
                ),
            )
            lifecycle.abandon("test_stable_claim_cleanup")


class AnchorMethodDispatchTests(unittest.TestCase):
    @staticmethod
    def empty_detection(**overrides):
        value = fiducial_module.FiducialDetection(
            baseline_w=None,
            robust_sigma_w=None,
            fits=(),
            spurious_plateau_count=0,
            all_pulses_detected=False,
            b_fiducial_s=None,
            residual_median_s=None,
            residual_p95_s=None,
        )
        return replace(value, **overrides)

    def test_fresh_cross_method_derivation_skips_stored_number_comparison(self) -> None:
        from tests.test_reduce import self_consistent_calibration
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        evidence, raw, events = self_consistent_calibration()
        recorded = copy.deepcopy(evidence["clock_anchor"])
        before = copy.deepcopy(recorded)
        prospective = {
            "status": "bounded",
            "method": CLOCK_METHOD_V3,
            "first_sample_end_point_epoch_s": (
                recorded["first_sample_end_point_epoch_s"] + 0.0001
            ),
            "effective_clock_anchor_bound_s": 0.003,
        }
        detector_result = self.empty_detection()
        with (
            patch.object(
                fiducial_module,
                "resolve_anchor_deriver",
                return_value=lambda **_kwargs: prospective,
            ) as resolver,
            patch.object(
                fiducial_module, "detect_pulses", return_value=detector_result
            ),
        ):
            result = fiducial_module.rederive_detection_from_artifacts(
                raw,
                events,
                recorded,
                protocol_id=PROTOCOL_V2_ID,
                anchor_method=CLOCK_METHOD_V3,
                derivation_role="validation_only",
            )
        resolver.assert_called_once_with(CLOCK_METHOD_V3)
        self.assertEqual(recorded, before)
        self.assertEqual(result.anchor_method, CLOCK_METHOD_V3)
        self.assertEqual(result.derivation_role, "validation_only")

    def test_authentication_mode_dispatches_stored_method_and_keeps_equality_gate(self) -> None:
        from tests.test_reduce import self_consistent_calibration
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V2

        evidence, raw, events = self_consistent_calibration()
        recorded = evidence["clock_anchor"]
        mismatched = dict(recorded)
        mismatched["first_sample_end_point_epoch_s"] += 0.01
        with patch.object(
            fiducial_module,
            "resolve_anchor_deriver",
            return_value=lambda **_kwargs: mismatched,
        ) as resolver:
            with self.assertRaisesRegex(ValueError, "disagrees with raw bytes"):
                fiducial_module.rederive_detection_from_artifacts(
                    raw, events, recorded, protocol_id=LEGACY_PROTOCOL_ID
                )
        resolver.assert_called_once_with(CLOCK_METHOD_V2)

    def test_unregistered_stored_method_and_invalid_roles_fail_closed(self) -> None:
        from tests.test_reduce import self_consistent_calibration

        evidence, raw, events = self_consistent_calibration()
        recorded = copy.deepcopy(evidence["clock_anchor"])
        recorded["method"] = "unregistered"
        with self.assertRaisesRegex(
            ValueError, "calibration clock anchor method is unregistered"
        ):
            fiducial_module.rederive_detection_from_artifacts(
                raw, events, recorded, protocol_id=LEGACY_PROTOCOL_ID
            )
        with self.assertRaisesRegex(ValueError, "derivation_role"):
            fiducial_module.rederive_detection_from_artifacts(
                raw,
                events,
                evidence["clock_anchor"],
                protocol_id=LEGACY_PROTOCOL_ID,
                derivation_role="claim_bearing",
            )
        with self.assertRaisesRegex(ValueError, "derivation_role"):
            self.empty_detection(derivation_role="claim_bearing")

    def test_evidence_author_stamps_method_that_produced_detection(self) -> None:
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        payload = instrument_evidence(
            self.empty_detection(
                anchor_method=CLOCK_METHOD_V3,
                derivation_role="prospective",
            ),
            bindings={},
            validation_id="prospective-v3",
            artifact_sha256={},
            protocol_pulse_count=0,
            protocol_id=LEGACY_PROTOCOL_ID,
        )
        self.assertEqual(payload["anchor_method_version"], CLOCK_METHOD_V3)


if __name__ == "__main__":
    unittest.main()
