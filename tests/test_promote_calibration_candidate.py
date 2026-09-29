"""Promotion input, seals, disclosure, and temporary-output counterfactuals."""

import copy
import hashlib
import gzip
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_bracketing as bracket
from scripts import promote_calibration_candidate as promote
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.candidate_raw = promote.CANDIDATE.read_bytes()
        self.candidate = json.loads(self.candidate_raw)
        (root / "candidate.json").write_bytes(self.candidate_raw)
        ruling_raw = b"synthetic ruling citation for promotion tests\n"
        (root / "ruling.txt").write_bytes(ruling_raw)
        log_raw = b"synthetic preserved network-time log\n"
        (root / "log.gz").write_bytes(gzip.compress(log_raw))
        citation = {"relative_path": "ruling.txt",
                    "file_sha256": hashlib.sha256(ruling_raw).hexdigest()}
        # Main has the candidate, but no issuance text for the withdrawn file.
        # Supply synthetic text and cited evidence entirely in a temporary tree.
        issuance = {
            "reason": "synthetic promotion test",
            "required_verification": "complete: synthetic promotion test",
            "network_time_provenance": {
                "disclosure_id": "D8", "text": "synthetic disclosure 8",
                "source_rulings": [dict(citation)],
                "preserved_log": {"relative_path": "log.gz",
                                  "plain_text_sha256": hashlib.sha256(log_raw).hexdigest()},
            },
            "issuance_record": {
                "source_candidate": {
                    "relative_path": "candidate.json", "file_sha256": promote.CANDIDATE_SHA256,
                    "derivation_sha256": self.candidate["derivation_sha256"],
                },
                "disclosures": [{"id": f"D{n}", "text": f"synthetic disclosure {n}"}
                                for n in range(1, 9)],
                "holds": [{"id": key, "text": f"synthetic condition {key}"}
                          for key in ("H1", "H5", "H6", "H7")],
                "rulings": [{"id": key, **citation} for key in promote.RULING_IDS],
                "claim_eligible_meaning": promote.CLAIM_ELIGIBLE_MEANING,
                "hold_enforcement": "synthetic issuance metadata; no runtime authority",
            },
        }
        self.issuance_raw = json.dumps(issuance).encode()
        (root / "issuance.json").write_bytes(self.issuance_raw)
        root_patch = patch.object(promote, "ROOT", root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.issued_raw = promote.promote(self.candidate_raw, self.issuance_raw)
        self.issued = json.loads(self.issued_raw)

    def test_p1_write_and_check_temporary_output(self):
        runner = ("import sys; from pathlib import Path; "
                  "from scripts import promote_calibration_candidate as p; "
                  "p.ROOT = Path(sys.argv.pop(1)); p.main()")
        path = promote.ROOT / "issued.json"
        common = ["python3", "-B", "-c", runner, str(promote.ROOT),
                  "--candidate", str(promote.ROOT / "candidate.json"),
                  "--issuance-text", str(promote.ROOT / "issuance.json")]
        for action in ("--out", "--check"):
            result = subprocess.run(common + [action, str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(),
                             f"issued sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
        self.assertEqual(path.read_bytes(), self.issued_raw)
        self.assertIsNone(bracket.load_calibration_acceptance_bound(path))
        self.assertNotIn(self.issued["acceptance_id"], bracket.ISSUED_ACCEPTANCE_REGISTRY)
        self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.ANCHOR_V3_R7_ACCEPTANCE_ID)

    def test_cli_requires_explicit_issuance_text(self):
        script = Path(__file__).resolve().parents[1] / "scripts/promote_calibration_candidate.py"
        path = promote.ROOT / "must-not-be-created.json"
        result = subprocess.run(["python3", "-B", str(script), "--out", str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("--issuance-text", result.stderr)
        self.assertFalse(path.exists())

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

    def test_p8_citations_and_all_four_holds_are_complete(self):
        issuance = json.loads(self.issuance_raw)
        edits = (
            lambda t: t["issuance_record"]["source_candidate"].pop("relative_path"),
            lambda t: t["issuance_record"]["rulings"][0].pop("relative_path"),
            lambda t: t["network_time_provenance"]["source_rulings"][0].pop("file_sha256"),
            lambda t: t["network_time_provenance"]["preserved_log"].pop("relative_path"),
            lambda t: t["issuance_record"]["holds"][1].__setitem__("text", ""),
        )
        for edit in edits:
            text = copy.deepcopy(issuance)
            edit(text)
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                promote.promote(self.candidate_raw, json.dumps(text).encode())

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
