"""Promotion input, seals, disclosure, and registry counterfactuals."""

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_bracketing as bracket
from scripts import promote_calibration_candidate as promote
from scripts.issue_calibration_acceptance_generation import generation_row_for_registry
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256


class PromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate_raw = promote.CANDIDATE.read_bytes()
        cls.issuance_raw = promote.ISSUANCE_TEXT.read_bytes()
        cls.candidate = json.loads(cls.candidate_raw)
        cls.issued_raw = bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH.read_bytes()
        cls.issued = json.loads(cls.issued_raw)

    def test_p1_check_and_pin(self):
        result = subprocess.run(["/opt/homebrew/bin/python3", "-B", str(promote.ROOT / "scripts/promote_calibration_candidate.py"), "--check", str(bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(promote.promote(self.candidate_raw, self.issuance_raw), self.issued_raw)
        self.assertEqual(hashlib.sha256(self.issued_raw).hexdigest(), bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_SHA256)

    def test_p2_protected_paths_unchanged(self):
        protected = (
            "schema_version", "acceptance_id", "decision_ids", "ledger_cutoff",
            "identity_epoch", "prospective_rederivation", "derivation_corpus",
            "prior_observation_set", "decimal_derivation", "registered_generation_row",
            "derivation_input_sha256",
        )
        for key in protected:
            self.assertEqual(self.issued[key], self.candidate[key], key)
            self.assertEqual(json.dumps(self.issued[key], ensure_ascii=True), json.dumps(self.candidate[key], ensure_ascii=True), key)
        for key in self.candidate["derivation_notes"]:
            self.assertEqual(self.issued["derivation_notes"][key], self.candidate["derivation_notes"][key])
            self.assertEqual(json.dumps(self.issued["derivation_notes"][key], ensure_ascii=True),
                             json.dumps(self.candidate["derivation_notes"][key], ensure_ascii=True))
        self.assertEqual(self.issued["backfill_candidate"]["candidate_inventory"], self.candidate["backfill_candidate"]["candidate_inventory"])
        self.assertEqual(json.dumps(self.issued["backfill_candidate"]["candidate_inventory"], ensure_ascii=True),
                         json.dumps(self.candidate["backfill_candidate"]["candidate_inventory"], ensure_ascii=True))

    def test_p3_changed_member_refuses_both_seals(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.9"
        raw = (json.dumps(candidate, indent=2) + "\n").encode()
        with self.assertRaisesRegex(ValueError, "candidate digest mismatch"):
            promote.promote(raw, self.issuance_raw)
        with patch.object(promote, "CANDIDATE_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, "candidate seal"):
                promote.promote(raw, self.issuance_raw)

    def test_p4_required_disclosures_h1_and_ruling_digests(self):
        issuance = json.loads(self.issuance_raw)
        for missing in (f"D{number}" for number in range(1, 9)):
            text = copy.deepcopy(issuance)
            text["issuance_record"]["disclosures"] = [row for row in text["issuance_record"]["disclosures"] if row["id"] != missing]
            with self.assertRaises(ValueError):
                promote.promote(self.candidate_raw, json.dumps(text).encode())
        text = copy.deepcopy(issuance)
        text["issuance_record"]["holds"] = [row for row in text["issuance_record"]["holds"] if row["id"] != "H1"]
        with self.assertRaisesRegex(ValueError, "H1"):
            promote.promote(self.candidate_raw, json.dumps(text).encode())
        for index in range(4):
            text = copy.deepcopy(issuance)
            del text["issuance_record"]["rulings"][index]["file_sha256"]
            with self.assertRaisesRegex(ValueError, "ruling digests"):
                promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_p5_generation_row_matches_code(self):
        self.assertEqual(generation_row_for_registry(self.issued["registered_generation_row"]), bracket._D102_GENERATION_DERIVATIONS[bracket.EPOCH_25G83_R1_ACCEPTANCE_ID])

    def test_p6_cited_evidence_and_disclosure_mutations_refuse(self):
        issuance = json.loads(self.issuance_raw)
        mutations = []

        def changed(edit):
            text = copy.deepcopy(issuance)
            edit(text)
            mutations.append(text)

        changed(lambda t: t["issuance_record"]["rulings"][0].__setitem__("file_sha256", "f" * 64))
        changed(lambda t: t["issuance_record"]["rulings"][0].__setitem__("relative_path", "nonexistent.md"))
        changed(lambda t: t["issuance_record"]["disclosures"][7].__setitem__("text", "x"))
        changed(lambda t: t["network_time_provenance"].__setitem__("text", "contradicts D8"))
        changed(lambda t: (t["issuance_record"].pop("claim_eligible_meaning"),
                           t["issuance_record"].pop("hold_enforcement")))
        changed(lambda t: t["issuance_record"]["source_candidate"].__setitem__("relative_path", "elsewhere"))
        for index, text in enumerate(mutations, start=1):
            with self.subTest(altered_text=f"P4{chr(ord('a') + index - 1)}"):
                with self.assertRaises(ValueError):
                    promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_p7_issued_input_seal_drift_stops(self):
        def drift_on_issued(value):
            if value.get("artifact_role") == "issued":
                return "f" * 64
            return derivation_input_sha256(value)

        with patch.object(promote, "derivation_input_sha256", side_effect=drift_on_issued):
            with self.assertRaisesRegex(ValueError, "STOP: derivation input seal"):
                promote.promote(self.candidate_raw, self.issuance_raw)


if __name__ == "__main__":
    unittest.main()
