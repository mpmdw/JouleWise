"""Regressions for the non-issued D-079 reissue candidate tooling."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from joulewise.calibration_bracketing import (
    _canonical_sha256,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import content_id_from_artifact_hashes
from scripts import reissue_calibration_acceptance as reissue


ROOT = Path(__file__).resolve().parents[1]
ISSUED = ROOT / "configs/calibration/calibration_acceptance_d079_v2.json"


class ReissueCalibrationAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        temp_root = os.environ.get("TMPDIR")
        self.temporary = tempfile.TemporaryDirectory(dir=temp_root)
        self.root = Path(self.temporary.name)
        self.corpus_root = self.root / "corpus-copy"
        self.corpus_root.mkdir()
        self.artifact = json.loads(ISSUED.read_text(encoding="utf-8"))
        prior_by_attempt = {
            row["attempt_id"]: row
            for row in self.artifact["prior_observation_set"]["observations"]
        }
        for member in self.artifact["derivation_corpus"]["members"]:
            directory = self.corpus_root / member["source_directory"]
            directory.mkdir(parents=True)
            manifest = (json.dumps({"member_id": member["member_id"]}) + "\n").encode()
            evidence = (
                json.dumps(
                    {"b_fiducial_s": member["b_fiducial_s"]},
                    separators=(",", ":"),
                )
                + "\n"
            ).encode()
            (directory / "manifest.json").write_bytes(manifest)
            (directory / "instrument_evidence.json").write_bytes(evidence)
            member["manifest_sha256"] = hashlib.sha256(manifest).hexdigest()
            member["instrument_evidence_sha256"] = hashlib.sha256(
                evidence
            ).hexdigest()
            prior_by_attempt[member["member_id"]]["content_id"] = (
                content_id_from_artifact_hashes(
                    {
                        "manifest.json": member["manifest_sha256"],
                        "instrument_evidence.json": member[
                            "instrument_evidence_sha256"
                        ],
                    }
                )
            )
        self.artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in self.artifact.items()
                if key != "derivation_sha256"
            }
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _authenticate(self) -> reissue.CorpusAuthentication:
        return reissue.authenticate_derivation_corpus(
            self.artifact, corpus_root=self.corpus_root
        )

    def test_corpus_authentication_catches_tampered_member_copy(self) -> None:
        member = self.artifact["derivation_corpus"]["members"][7]
        evidence_path = (
            self.corpus_root
            / member["source_directory"]
            / "instrument_evidence.json"
        )
        evidence_path.write_bytes(evidence_path.read_bytes() + b" ")

        authentication = self._authenticate()

        by_id = {row["member_id"]: row for row in authentication.members}
        tampered = by_id[member["member_id"]]
        self.assertFalse(authentication.all_authenticated)
        self.assertEqual(authentication.authenticated_count, 18)
        self.assertEqual(tampered["manifest_sha256"]["result"], "PASS")
        self.assertEqual(
            tampered["instrument_evidence_sha256"]["result"], "FAIL"
        )
        self.assertFalse(tampered["authenticated"])

    def test_threshold_delta_forces_stop_verdict(self) -> None:
        candidate = reissue.derive_candidate_artifact(
            self.artifact, self._authenticate()
        )
        changed = deepcopy(candidate)
        changed["decimal_derivation"]["ratified_operatives"][
            "bracket_screen_s"
        ] = "0.010819"

        report = reissue.build_member_delta_report(self.artifact, changed)

        self.assertEqual(report["verdict"], "STOP")
        self.assertFalse(report["thresholds"]["identical"])
        self.assertIn("thresholds_changed", report["stop_reasons"])
        self.assertIn("science_facing_values_changed", report["stop_reasons"])

    def test_candidate_marker_refuses_at_acceptance_loader_boundary(self) -> None:
        # Change only the marker and its covering whole-core digest.  This
        # isolates the candidate state from estimator-pin and fixture changes.
        issued = json.loads(ISSUED.read_text(encoding="utf-8"))
        candidate = {"candidate_not_issued": True, **issued}
        candidate["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in candidate.items()
                if key != "derivation_sha256"
            }
        )
        output = self.root / "candidate.json"
        reissue.write_candidate_artifact(output, candidate)

        self.assertTrue(candidate["candidate_not_issued"])
        self.assertIsNone(load_calibration_acceptance_bound(output))

    def test_two_runs_emit_byte_identical_candidates(self) -> None:
        authentication = self._authenticate()
        first = reissue.derive_candidate_artifact(self.artifact, authentication)
        second = reissue.derive_candidate_artifact(self.artifact, authentication)
        first_path = self.root / "candidate-1.json"
        second_path = self.root / "candidate-2.json"

        first_bytes = reissue.write_candidate_artifact(first_path, first)
        second_bytes = reissue.write_candidate_artifact(second_path, second)

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
        report = reissue.build_member_delta_report(self.artifact, first)
        self.assertEqual(report["verdict"], "PROCEED")
        self.assertTrue(report["member_set"]["identical"])
        self.assertTrue(report["thresholds"]["identical"])
        self.assertTrue(report["science_facing"]["identical"])


if __name__ == "__main__":
    unittest.main()
