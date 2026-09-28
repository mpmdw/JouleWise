"""D-138 loader disposition fences and their counterfactuals."""

import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_bracketing as bracket
import joulewise.calibration_dispositions as dispositions
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256, derivation_sha256


class DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.issued = json.loads(bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH.read_text())

    def bound(self):
        return copy.deepcopy(self.issued)

    def valid(self, value):
        value["derivation_sha256"] = derivation_sha256(value)
        return bracket._valid_acceptance_bound(value)

    def valid_with_count(self, value, count):
        row = copy.deepcopy(bracket._D102_GENERATION_DERIVATIONS[bracket.EPOCH_25G83_R1_ACCEPTANCE_ID])
        row["prior_observation_count"] = count
        value["registered_generation_row"]["prior_observation_count"] = count
        value["derivation_input_sha256"] = derivation_input_sha256(value)
        with patch.dict(bracket._D102_GENERATION_DERIVATIONS,
                        {bracket.EPOCH_25G83_R1_ACCEPTANCE_ID: row}):
            return self.valid(value)

    def test_d1_registry_and_table_agree(self):
        raw = dispositions.DISPOSITION_REGISTRY_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), dispositions.DISPOSITION_REGISTRY_SHA256)
        parsed = dispositions.parse_disposition_registry(raw, expected_sha256=dispositions.DISPOSITION_REGISTRY_SHA256)
        expected = {content_id: decision_id for decision_id, row in dispositions.DISPOSITION_DECISIONS.items() for content_id in row["content_ids"]}
        self.assertEqual(parsed, expected)

    def test_l1_issued_loads(self):
        self.assertIsNotNone(bracket.load_calibration_acceptance_bound(bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH))

    def test_l2_unlisted_foreign_valid_refuses(self):
        value = self.bound()
        row = dict(value["prior_observation_set"]["observations"][0])
        row.update(content_id="a" * 64, epoch_id="d079_epoch_25g83", disposition="valid",
                   attempt_id="foreign-extra", session_id="d079-epoch-25g83-derivation-n1-20260919")
        value["prior_observation_set"]["observations"].append(row)
        value["backfill_candidate"]["candidate_inventory"]["valid"] += 1
        self.assertFalse(self.valid_with_count(value, 87))
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] |= {"a" * 64}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertTrue(self.valid_with_count(value, 87))

    def test_l3_l4_declaration_refuses(self):
        for declaration in (["D-126-forged"], [], [dispositions.DISPOSITION_DECISION_ID] * 2, None):
            value = self.bound()
            if declaration is None:
                del value["prior_observation_set"]["disposing_decision_ids"]
            else:
                value["prior_observation_set"]["disposing_decision_ids"] = declaration
            self.assertFalse(self.valid(value), declaration)
            with patch.object(bracket, "decisions_disposing", return_value=declaration or []), patch.object(
                bracket, "disposed_content_ids_for",
                return_value=dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"],
            ):
                self.assertTrue(self.valid(value), declaration)

    def test_l5_missing_disposed_row_refuses(self):
        value = self.bound()
        prior = value["prior_observation_set"]
        victim = next(iter(dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"]))
        prior["observations"] = [row for row in prior["observations"] if row["content_id"] != victim]
        value["backfill_candidate"]["candidate_inventory"]["valid"] -= 1
        self.assertFalse(self.valid_with_count(value, 85))
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] -= {victim}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertTrue(self.valid_with_count(value, 85))

    def test_l6_disposed_inside_registration_refuses(self):
        value = self.bound()
        victim = next(iter(dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"]))
        row = next(row for row in value["prior_observation_set"]["observations"] if row["content_id"] == victim)
        row["session_id"] = self.issued["registered_generation_row"]["registration_session_ids"][0]
        self.assertFalse(self.valid(value))
        row["session_id"] = "d079-epoch-25g83-derivation-n1-20260919"
        self.assertTrue(self.valid(value))

    def test_l7_member_in_disposition_table_refuses(self):
        value = self.bound()
        member = value["derivation_corpus"]["members"][0]
        from joulewise.calibration_ledger import content_id_from_artifact_hashes
        content_id = content_id_from_artifact_hashes({"manifest.json": member["manifest_sha256"], "instrument_evidence.json": member["instrument_evidence_sha256"]})
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] = altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] | {content_id}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertFalse(self.valid(value))
            original = dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"] - {content_id}
            with patch.object(bracket, "disposed_content_ids_for", return_value=original):
                self.assertTrue(self.valid(value))

    def test_l8_table_missing_row_refuses(self):
        value = self.bound()
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        ids = altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"]
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] = ids - {next(iter(ids))}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertFalse(self.valid(value))
            with patch.object(bracket, "disposed_content_ids_for", return_value=ids):
                self.assertTrue(self.valid(value))

    def test_l9_old_files_load_without_registry_io(self):
        original = Path.read_bytes
        def guarded(path):
            if path == dispositions.DISPOSITION_REGISTRY_PATH:
                raise AssertionError("old issuance read disposition file")
            return original(path)
        with patch.object(Path, "read_bytes", guarded):
            for acceptance_id, row in bracket.ISSUED_ACCEPTANCE_REGISTRY.items():
                if acceptance_id != bracket.EPOCH_25G83_R1_ACCEPTANCE_ID:
                    self.assertIsNotNone(bracket.load_calibration_acceptance_bound(row["path"]), acceptance_id)


if __name__ == "__main__":
    unittest.main()
