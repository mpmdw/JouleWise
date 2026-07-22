"""Defect-shaped regressions for claim-bearing calibration bracketing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.calibration_bracketing import (
    CalibrationCandidate,
    evaluate_calibration_bracket,
    load_calibration_candidate,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
)
from joulewise.schemas import CalibrationBracketingPolicy


class CalibrationBracketingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )

    def candidate(self, name: str, capture_s: float, bound_s: float) -> CalibrationCandidate:
        return CalibrationCandidate(
            relative_path=f"instrument_validation/{name}",
            manifest_sha256="ab" * 32,
            evidence_sha256="cd" * 32,
            protocol_id=PROTOCOL_ID,
            capture_wall_time_s=capture_s,
            b_fiducial_s=bound_s,
            bindings=self.bindings,
        )

    def test_claim_window_passes_with_authenticated_pre_post_bracket_and_uses_max(self) -> None:
        # Exact H2 defect shape: a single sample maximum used to stand in for
        # temporal instrument stability. Two causal endpoints now bracket it.
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.027)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["b_fiducial_s"], 0.027)

    def test_missing_post_bracket_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

    def test_bracket_drift_over_registered_tolerance_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.031)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertAlmostEqual(result["drift_s"], 0.011)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))

    def test_hash_rekeyed_candidate_cannot_bypass_binding_authentication(self) -> None:
        # H2 validity defect shape: rewriting a binding and then rehashing the
        # evidence/manifest must not create an authenticated bracket endpoint.
        bindings = dict(self.bindings)
        bindings.update(
            {
                "anchor_method_version": (
                    "powermetrics_native_second_censored_intersection_v1"
                ),
                "pulse_protocol_id": PROTOCOL_ID,
                "protocol_sha256": PROTOCOL_V3_SHA256,
                "estimator_revision": RESIDUAL_REGION_METHOD,
            }
        )
        canonical = json.dumps(
            bindings,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        events = b'{"timestamp_s":99.0}\n'
        raw = b"authenticated-by-patched-physics"
        evidence = {
            "schema_version": "joulewise.instrument_evidence.v1",
            "protocol_id": PROTOCOL_ID,
            "pulse_count": PULSE_COUNT,
            "anchor_method_version": bindings["anchor_method_version"],
            "residual_region_method": RESIDUAL_REGION_METHOD,
            "residual_region_coverage_assumption": "complete accepted region",
            "residual_region_coverage_resolution_s": (
                REGION_COVERAGE_RESOLUTION_S
            ),
            "capture_wall_time_s": 99.0,
            "max_age_s": MAX_AGE_S,
            "bindings": bindings,
            "binding_evidence": {
                "schema_version": "joulewise.instrument_binding_evidence.v1",
                "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
                "powermetrics_binary": {
                    "path": "/usr/bin/powermetrics",
                    "sha256": bindings["powermetrics_sha256"],
                },
                "power_policy": {"id": bindings["power_policy"]},
            },
            "artifact_sha256": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "instrument_validation" / "candidate"
            (directory / "raw").mkdir(parents=True)
            (directory / "events.jsonl").write_bytes(events)
            (directory / "raw/powermetrics.plist").write_bytes(raw)

            def write_evidence_and_manifest() -> None:
                evidence_raw = json.dumps(evidence, sort_keys=True).encode()
                (directory / "instrument_evidence.json").write_bytes(evidence_raw)
                artifacts = {
                    "events.jsonl": hashlib.sha256(events).hexdigest(),
                    "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                    "instrument_evidence.json": hashlib.sha256(
                        evidence_raw
                    ).hexdigest(),
                }
                (directory / "manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": (
                                "joulewise.instrument_validation_manifest.v1"
                            ),
                            "protocol_id": PROTOCOL_ID,
                            "pulse_count": PULSE_COUNT,
                            "artifacts": artifacts,
                        }
                    )
                )

            write_evidence_and_manifest()
            with patch(
                "joulewise.calibration_bracketing.verify_stored_evidence_physics",
                return_value=0.02,
            ):
                self.assertIsNotNone(
                    load_calibration_candidate(directory, runs_root=root)
                )
                evidence["bindings"]["hardware_model"] = "tampered-model"
                write_evidence_and_manifest()
                self.assertIsNone(
                    load_calibration_candidate(directory, runs_root=root)
                )


if __name__ == "__main__":
    unittest.main()
