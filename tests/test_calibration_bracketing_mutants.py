"""Synthetic regression cases for bracket selection and allowance projection."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import calibration_bracketing as bracketing
from joulewise import powermetrics_fiducial as fiducial
from joulewise.schemas import CalibrationBracketingPolicy
from tests.test_calibration_bracketing import evaluate_calibration_bracket


class BracketSelectionTests(unittest.TestCase):
    def setUp(self):
        self.bindings = {field: f"value-{field}" for field in fiducial.V2_BINDING_FIELDS}
        self.bindings.update(
            hardware_model="Mac15,9", os_build="25F84", sampling_interval_ms=100,
            pulse_protocol_id=fiducial.PROTOCOL_ID, power_policy="ac_high_power",
            anchor_method_version=bracketing.ACTIVE_CAPTURE_ANCHOR_METHOD,
            estimator_revision=fiducial.RESIDUAL_REGION_METHOD,
            protocol_sha256=fiducial.protocol_sha256(fiducial.PROTOCOL_ID),
        )

    def candidate(self, name, capture, bound):
        return bracketing.CalibrationCandidate(
            relative_path=f"instrument_validation/{name}",
            manifest_sha256="ab" * 32, evidence_sha256="cd" * 32,
            protocol_id=fiducial.PROTOCOL_ID, capture_wall_time_s=capture,
            b_fiducial_s=bound, bindings=self.bindings,
        )

    def evaluate(self, candidates, start=100.0, end=110.0):
        return evaluate_calibration_bracket(
            candidates, window_start_s=start, window_end_s=end,
            bindings=self.bindings,
            policy=CalibrationBracketingPolicy(
                require_bracket=True, calibration_bracket_max_drift_s=0.010,
            ),
        )

    def test_larger_pre_endpoint_sets_operative_bound(self):
        """The larger endpoint is widened once. Kills M01913 (max -> post)."""
        result, reasons = self.evaluate([
            self.candidate("pre", 99.0, "0.027"),
            self.candidate("post", 111.0, "0.020"),
        ])
        self.assertEqual(reasons, ())
        # 0.027 + the fixture's registered 0.010818 s screen = 0.037818 s.
        # Bar: 1e-6 relative (COMMON fallback; no printed half-width).
        # Mutant loses 0.007 s, over 185,000 bars.
        self.assertAlmostEqual(result["b_fiducial_s"], 0.037818, delta=0.037818e-6)

    def test_earliest_post_wins_in_either_input_order(self):
        """Unordered posts select the earliest fresh one. Kills M02164."""
        pre = self.candidate("pre", 99.0, "0.027")
        early = self.candidate("early", 111.0, "0.020")
        late = self.candidate("late", 112.0, "0.026")
        for posts in ([late, early], [early, late]):
            with self.subTest(order=[post.relative_path for post in posts]):
                result, reasons = self.evaluate([pre, *posts])
                self.assertEqual(reasons, ())
                # Endpoint identity is an exact wire property.
                self.assertEqual(result["post"]["relative_path"], early.relative_path)

    def test_fresh_window_far_from_epoch_zero(self):
        """Freshness is elapsed time, independent of epoch origin. Kills M02503."""
        start = fiducial.MAX_AGE_S + 100.0
        result, reasons = self.evaluate([
            self.candidate("pre", start - 1.0, "0.025"),
            self.candidate("post", start + 11.0, "0.026"),
        ], start=start, end=start + 10.0)
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")

    def test_zero_duration_window_refuses(self):
        """A bracket needs a positive-duration window. Kills M02143 (>= -> >)."""
        _result, reasons = self.evaluate([
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 101.0, "0.026"),
        ], start=100.0, end=100.0)
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))


class AllowanceProjectionTests(unittest.TestCase):
    def project(self, post):
        # Synthetic authenticated authority isolates Decimal arithmetic from
        # generation pinning; neither value is a measurement or a live pin.
        authority = {
            "artifact_role": "issued",
            "decimal_derivation": {"ratified_operatives": {
                "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
                "embedding_count": 1, "bracket_screen_s": "0.125",
                "maximum_budgetable_drift_s": "0.25",
            }},
        }
        with patch.object(bracketing, "_authenticated_explicit_acceptance_bound",
                          return_value=authority):
            return bracketing.issued_calibration_allowance_projection(
                authority, pre_exact_bound_lexeme_s="0", post_exact_bound_lexeme_s=post,
            )

    def test_observed_drift_above_screen_is_applied(self):
        """Observed drift dominates the allowance above the screen. Kills M02283."""
        # Exact Decimal strings: drift 3/16 exceeds screen 1/8 by 1/16.
        projection = self.project("0.1875")
        self.assertEqual(projection["applied_allowance_s"], "0.1875")

    def test_exact_decimal_budget_is_inclusive(self):
        """Drift equal to the exact budget is admitted. Kills M01894 (> -> >=)."""
        projection = self.project("0.25")
        self.assertIsNotNone(projection)
        self.assertEqual(projection["observed_drift_s"], "0.25")


class CandidateCaptureTests(unittest.TestCase):
    def test_capture_at_epoch_zero_is_admitted(self):
        """A capture timestamp of zero is valid. Kills M02309 (lower bound 0 -> 1)."""
        bindings = {field: "synthetic" for field in fiducial.V2_BINDING_FIELDS}
        bindings.update(pulse_protocol_id=fiducial.PROTOCOL_ID,
                        protocol_sha256=fiducial.protocol_sha256(fiducial.PROTOCOL_ID))
        events, power = b"synthetic events", b"synthetic power"
        evidence = {
            "schema_version": "joulewise.instrument_evidence.v1",
            "protocol_id": fiducial.PROTOCOL_ID,
            "pulse_count": fiducial.protocol_pulse_count(fiducial.PROTOCOL_ID),
            "bindings": bindings, fiducial.CAPTURE_TIME_FIELD: 0.0,
            "b_fiducial_s": 0.02,
            "anchor_method_version": bracketing.ACTIVE_CAPTURE_ANCHOR_METHOD,
            "residual_region_method": fiducial.RESIDUAL_REGION_METHOD,
            "residual_region_coverage_assumption": "synthetic",
            "residual_region_coverage_resolution_s": fiducial.REGION_COVERAGE_RESOLUTION_S,
            "max_age_s": fiducial.MAX_AGE_S,
            "artifact_sha256": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(power).hexdigest(),
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "candidate"
            (candidate / "raw").mkdir(parents=True)
            assets = {"events.jsonl": events, "raw/powermetrics.plist": power,
                      "instrument_evidence.json": json.dumps(evidence).encode()}
            for name, raw in assets.items():
                (candidate / name).write_bytes(raw)
            (candidate / "manifest.json").write_text(json.dumps({
                "schema_version": "joulewise.instrument_validation_manifest.v1",
                "protocol_id": fiducial.PROTOCOL_ID,
                "pulse_count": fiducial.protocol_pulse_count(fiducial.PROTOCOL_ID),
                "artifacts": {name: hashlib.sha256(raw).hexdigest()
                              for name, raw in assets.items()},
            }))
            with (
                patch.object(bracketing, "_binding_evidence_authentic", return_value=True),
                patch.object(bracketing, "capture_wall_time_from_events", return_value=0.0),
                patch.object(bracketing, "verify_stored_evidence_physics", return_value=0.02),
            ):
                loaded = bracketing.load_calibration_candidate(candidate, runs_root=root)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.capture_wall_time_s, 0.0)  # Exact binary zero.
