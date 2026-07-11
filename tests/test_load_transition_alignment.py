from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.load_transition_alignment import (
    ARTIFACT_SCHEMA_VERSION,
    AlignmentRefusal,
    build_alignment_artifact,
    render_artifact,
    validate_alignment_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs" / "calibration" / "p2_046_load_transition" / "manifest.json"
FIXTURES = ROOT / "tests" / "fixtures" / "p2046"
VALID = FIXTURES / "valid_observations.json"
MALFORMED = FIXTURES / "malformed_observations.json"
MISSING = FIXTURES / "missing_transition_observations.json"
SCRIPT = ROOT / "scripts" / "characterize_load_transition.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_script(observations: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(MANIFEST),
            "--observations",
            str(observations),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


class LoadTransitionAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_json(MANIFEST)
        self.observations = load_json(VALID)

    def test_frozen_counterbalanced_plan_is_provisional(self) -> None:
        self.assertEqual(self.manifest["freeze_status"], "frozen_pre_execution")
        self.assertEqual(self.manifest["evidence_status"], "PROVISIONAL_PRE_EXECUTION")
        self.assertFalse(self.manifest["scope"]["physical_claims_allowed"])
        directions = [row["direction"] for row in self.manifest["execution_plan"]]
        self.assertEqual(
            directions,
            [
                "idle_to_load",
                "load_to_idle",
                "load_to_idle",
                "idle_to_load",
                "idle_to_load",
                "load_to_idle",
                "load_to_idle",
                "idle_to_load",
            ],
        )

    def test_closed_form_offset_residual_and_bound(self) -> None:
        artifact = build_alignment_artifact(self.manifest, self.observations)
        self.assertEqual(artifact["schema_version"], ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(artifact["evidence_status"], "PROVISIONAL_FIXTURE_ONLY")
        self.assertEqual(validate_alignment_artifact(artifact), [])

        rows = {row["transition_id"]: row for row in artifact["transitions"]}
        # t01 support relative to marker is [0, 2]: offset=(0+2)/2=1,
        # idle->load center=median(1,3,1,3)=2, residual=1-2=-1,
        # and its endpoint-support bound=max(|0|,|2|)=2 seconds.
        self.assertEqual(rows["p2046-t01"]["offset_s"], 1.0)
        self.assertEqual(rows["p2046-t01"]["direction_center_offset_s"], 2.0)
        self.assertEqual(rows["p2046-t01"]["residual_s"], -1.0)
        self.assertEqual(rows["p2046-t01"]["per_transition_conservative_bound_s"], 2.0)
        # t02 support is [-1, 1]: offset=0, load->idle center=1,
        # residual=-1, and its endpoint-support bound is 1 second.
        self.assertEqual(rows["p2046-t02"]["offset_s"], 0.0)
        self.assertEqual(rows["p2046-t02"]["direction_center_offset_s"], 1.0)
        self.assertEqual(rows["p2046-t02"]["residual_s"], -1.0)
        self.assertEqual(rows["p2046-t02"]["per_transition_conservative_bound_s"], 1.0)

        summaries = {row["direction"]: row for row in artifact["direction_summaries"]}
        self.assertEqual(summaries["idle_to_load"]["center_offset_s"], 2.0)
        self.assertEqual(summaries["idle_to_load"]["max_abs_residual_s"], 1.0)
        self.assertEqual(summaries["idle_to_load"]["conservative_bound_s"], 4.0)
        self.assertEqual(summaries["load_to_idle"]["center_offset_s"], 1.0)
        self.assertEqual(summaries["load_to_idle"]["max_abs_residual_s"], 1.0)
        self.assertEqual(summaries["load_to_idle"]["conservative_bound_s"], 3.0)
        # Overall fixture bound=max(direction bounds)=max(4,3)=4 seconds.
        self.assertEqual(artifact["conservative_bound"]["value_s"], 4.0)
        self.assertEqual(
            artifact["conservative_bound"]["p2_038_disposition"],
            "UNASSESSED_PENDING_P2_046B_QUIET_MAC",
        )

    def test_two_identical_fixture_runs_emit_byte_identical_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "one.json"
            two = Path(tmp) / "two.json"
            first = run_script(VALID, one)
            second = run_script(VALID, two)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(one.read_bytes(), two.read_bytes())
            self.assertEqual(
                hashlib.sha256(one.read_bytes()).hexdigest(),
                hashlib.sha256(two.read_bytes()).hexdigest(),
            )
            artifact = load_json(one)
            self.assertEqual(artifact["manifest"]["sha256"], hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
            self.assertEqual(artifact["observations"]["sha256"], hashlib.sha256(VALID.read_bytes()).hexdigest())

    def test_malformed_observations_refuse_before_artifact(self) -> None:
        with self.assertRaises(AlignmentRefusal) as caught:
            build_alignment_artifact(self.manifest, load_json(MALFORMED))
        self.assertEqual(caught.exception.reason_code, "observations_schema_invalid")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "artifact.json"
            result = run_script(MALFORMED, output)
            self.assertEqual(result.returncode, 2)
            self.assertIn("REFUSED[observations_schema_invalid]", result.stderr)
            self.assertFalse(output.exists())

    def test_missing_transition_set_refuses_before_artifact(self) -> None:
        with self.assertRaises(AlignmentRefusal) as caught:
            build_alignment_artifact(self.manifest, load_json(MISSING))
        self.assertEqual(caught.exception.reason_code, "transition_set_mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "artifact.json"
            result = run_script(MISSING, output)
            self.assertEqual(result.returncode, 2)
            self.assertIn("REFUSED[transition_set_mismatch]", result.stderr)
            self.assertFalse(output.exists())

    def test_missing_persistent_transition_response_refuses(self) -> None:
        observations = copy.deepcopy(self.observations)
        final = observations["transitions"][-1]
        for sample in final["samples"]:
            sample["mean_power_w"] = final["low_plateau_samples_w"][0]
        with self.assertRaises(AlignmentRefusal) as caught:
            build_alignment_artifact(self.manifest, observations)
        self.assertEqual(caught.exception.reason_code, "transition_not_observed")

    def test_overlapping_sample_intervals_refuse_as_malformed(self) -> None:
        observations = copy.deepcopy(self.observations)
        observations["transitions"][0]["samples"][1]["interval_start_s"] = 9.0
        with self.assertRaises(AlignmentRefusal) as caught:
            build_alignment_artifact(self.manifest, observations)
        self.assertEqual(caught.exception.reason_code, "transition_malformed")

    def test_artifact_validator_rederives_arithmetic_and_identity(self) -> None:
        artifact = build_alignment_artifact(self.manifest, self.observations)
        artifact["transitions"][0]["residual_s"] = 99.0
        errors = validate_alignment_artifact(artifact)
        self.assertTrue(any("residual_s" in error for error in errors), errors)
        self.assertIn("artifact_id does not match canonical artifact content", errors)
        with self.assertRaises(AlignmentRefusal) as caught:
            render_artifact(artifact)
        self.assertEqual(caught.exception.reason_code, "artifact_schema_invalid")

    def test_artifact_validator_returns_errors_for_wholly_malformed_transition(self) -> None:
        artifact = build_alignment_artifact(self.manifest, self.observations)
        artifact["transitions"] = [{"transition_id": "broken"}]
        errors = validate_alignment_artifact(artifact)
        self.assertIn("transitions[0] keys differ from v1 schema", errors)
        self.assertIn("conservative_bound cannot be re-derived without valid transitions", errors)

    def test_part_b_input_stays_provisional_and_requires_review(self) -> None:
        observations = copy.deepcopy(self.observations)
        observations["evidence_status"] = "PROVISIONAL_REAL_MAC_UNADJUDICATED"
        observations["source"] = {
            "capture_class": "real_mac_capture",
            "raw_samples_sha256": "0" * 64,
            "markers_sha256": "1" * 64,
        }
        artifact = build_alignment_artifact(self.manifest, observations)
        self.assertEqual(artifact["evidence_status"], "PROVISIONAL_REAL_MAC_UNADJUDICATED")
        self.assertEqual(artifact["claim_disposition"], "PROVISIONAL_PHYSICAL_BOUND_REVIEW_REQUIRED")
        self.assertEqual(validate_alignment_artifact(artifact), [])


if __name__ == "__main__":
    unittest.main()
