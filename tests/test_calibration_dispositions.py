"""D-138 loader disposition fences and their counterfactuals."""

import copy
import builtins
import hashlib
import json
import os
import sys
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
        self.assertIsNotNone(bracket.load_calibration_acceptance_bound(
            bracket.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH, allow_claim_held=True))

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
        member_row = next(row for row in value["prior_observation_set"]["observations"] if row["content_id"] == content_id)
        registered_session = member_row["session_id"]
        member_row["session_id"] = "d079-epoch-25g83-derivation-n1-20260919"
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] = altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] | {content_id}
        reached_completeness = False

        def trace(frame, event, arg):
            nonlocal reached_completeness
            if (frame.f_code is bracket._valid_acceptance_bound.__code__
                    and event == "line" and "registration_valid_ids" in frame.f_locals):
                reached_completeness = True
            return trace

        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            previous_trace = sys.gettrace()
            try:
                sys.settrace(trace)
                self.assertFalse(self.valid(value))
            finally:
                sys.settrace(previous_trace)
            self.assertFalse(reached_completeness, "disposed member passed the member guard")
            member_row["session_id"] = registered_session
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

    def test_l10_undeclared_decision_touching_prior_set_refuses(self):
        value = self.bound()
        prior_id = next(row["content_id"] for row in value["prior_observation_set"]["observations"]
                        if row["epoch_id"] != "d079_epoch_25g83")
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered["D-138-test-second-decision"] = {
            "mechanism": "test-only second decision",
            "content_ids": frozenset({prior_id}),
        }
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertFalse(self.valid(value))

    def test_l9_all_files_load_without_registry_io(self):
        target = dispositions.DISPOSITION_REGISTRY_PATH
        original_open, original_os_open, original_read_bytes = (
            builtins.open, os.open, Path.read_bytes,
        )

        def is_target(path):
            return isinstance(path, (str, bytes, os.PathLike)) and Path(path) == target

        def guarded_open(file, *args, **kwargs):
            if is_target(file):
                raise AssertionError("issuance read disposition file via open")
            return original_open(file, *args, **kwargs)

        def guarded_os_open(file, *args, **kwargs):
            if is_target(file):
                raise AssertionError("issuance read disposition file via os.open")
            return original_os_open(file, *args, **kwargs)

        def guarded_read_bytes(path):
            if is_target(path):
                raise AssertionError("issuance read disposition file via Path.read_bytes")
            return original_read_bytes(path)

        with patch.object(builtins, "open", guarded_open), patch.object(os, "open", guarded_os_open), patch.object(Path, "read_bytes", guarded_read_bytes):
            for acceptance_id, row in bracket.ISSUED_ACCEPTANCE_REGISTRY.items():
                self.assertIsNotNone(bracket.load_calibration_acceptance_bound(
                    row["path"], allow_claim_held=True), acceptance_id)


if __name__ == "__main__":
    unittest.main()
