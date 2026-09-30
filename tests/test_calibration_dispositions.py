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
from scripts import issue_calibration_acceptance_generation as issuer
from tests.test_calibration_bracketing import (
    _live_prefix_generation, _registered_generation, _reseal,
)
from tests.verify_w1w2_disposition_sources import candidate_members


class DispositionTests(unittest.TestCase):
    def setUp(self):
        # Exercise the loader with a synthetic live-prefix generation. The
        # withdrawn candidate is never registered, pinned, or loaded.
        self.acceptance_id, self.generation, self.issued = _live_prefix_generation()
        prior = self.issued["prior_observation_set"]
        prior["disposing_decision_ids"] = [dispositions.DISPOSITION_DECISION_ID]
        ids = dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"]
        epoch_id = next(key for key, epoch in prior["epoch_catalog"].items()
                        if epoch == self.issued["identity_epoch"])
        for index, content_id in enumerate(sorted(ids)):
            prior["observations"].append({
                "content_id": content_id, "epoch_id": epoch_id,
                "disposition": "valid", "attempt_id": f"disposed-{index}",
                "session_id": "diagnostic-session",
            })
        self.issued["backfill_candidate"]["candidate_inventory"]["valid"] += len(ids)
        self.generation["prior_observation_count"] = len(prior["observations"])
        self.issued = _reseal(self.issued)

    def bound(self):
        return copy.deepcopy(self.issued)

    def valid(self, value):
        with _registered_generation(self.acceptance_id, self.generation):
            return bracket._valid_acceptance_bound(_reseal(value))

    def valid_with_count(self, value, count):
        row = copy.deepcopy(self.generation)
        row["prior_observation_count"] = count
        with patch.object(self, "generation", row):
            return self.valid(value)

    def test_d1_registry_and_table_agree(self):
        raw = dispositions.DISPOSITION_REGISTRY_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), dispositions.DISPOSITION_REGISTRY_SHA256)
        parsed = dispositions.parse_disposition_registry(raw, expected_sha256=dispositions.DISPOSITION_REGISTRY_SHA256)
        expected = {content_id: decision_id for decision_id, row in dispositions.DISPOSITION_DECISIONS.items() for content_id in row["content_ids"]}
        self.assertEqual(parsed, expected)

    def test_w1w2_production_registry_preserves_original_bytes_and_exact_roster(self):
        rows = json.loads(dispositions.DISPOSITION_REGISTRY_PATH.read_bytes())
        original = rows[:11]
        original_raw = (json.dumps(original, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual(hashlib.sha256(original_raw).hexdigest(),
                         "ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c")
        self.assertEqual(set(dispositions.DISPOSITION_DECISIONS), {
            dispositions.DISPOSITION_DECISION_ID, dispositions.W1W2_SET_ASIDE_DECISION_ID,
        })
        members = candidate_members()
        self.assertEqual(len(rows), 23)
        self.assertEqual({row["content_id"] for row in rows[11:]}, set(members))
        self.assertEqual({row["disposing_decision_id"] for row in rows[11:]},
                         {dispositions.W1W2_SET_ASIDE_DECISION_ID})
        self.assertEqual(dispositions.DISPOSITION_DECISIONS[
            dispositions.DISPOSITION_DECISION_ID]["content_ids"],
            frozenset(row["content_id"] for row in original))
        self.assertEqual(dispositions.W1W2_SET_ASIDE_MECHANISM,
                         "valid Revision 5 capture of window W1 or W2; member of the "
                         "unregistered 25G83 candidate r1, whose member list was fixed "
                         "under the 165,000-cell cap while 8 of the 24 captures stopped "
                         "on that cap; set aside from the successor under "
                         "CAP-COUNCIL-25G83-01 addendum A1 S5 and erratum E1; "
                         "a valid capture, not a diagnostic; not a member of any registered calibration")

    def test_w1w2_missing_registry_row_refuses_and_table_counterfactual(self):
        rows = json.loads(dispositions.DISPOSITION_REGISTRY_PATH.read_bytes())
        victim = rows.pop()["content_id"]
        raw = json.dumps(rows).encode()
        digest = hashlib.sha256(raw).hexdigest()
        with patch.object(dispositions, "DISPOSITION_REGISTRY_SHA256", digest):
            with self.assertRaisesRegex(dispositions.DispositionRegistryError, "table mismatch"):
                dispositions.parse_disposition_registry(raw, expected_sha256=digest)
            altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
            altered[dispositions.W1W2_SET_ASIDE_DECISION_ID]["content_ids"] -= {victim}
            with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
                self.assertEqual(len(dispositions.parse_disposition_registry(
                    raw, expected_sha256=digest)), 22)

    def test_w1w2_both_decisions_required_and_declaration_counterfactuals(self):
        value = self.bound()
        prior = value["prior_observation_set"]
        epoch_id = next(key for key, epoch in prior["epoch_catalog"].items()
                        if epoch == value["identity_epoch"])
        for content_id, member in candidate_members().items():
            prior["observations"].append({
                "content_id": content_id, "epoch_id": epoch_id,
                "disposition": "valid", "attempt_id": member["member_id"],
                "session_id": member["source_directory"].split("/")[0],
            })
        value["backfill_candidate"]["candidate_inventory"]["valid"] += 12
        count = len(prior["observations"])
        both = sorted(dispositions.DISPOSITION_DECISIONS)
        prior["disposing_decision_ids"] = both
        self.assertTrue(self.valid_with_count(value, count))
        original_members = copy.deepcopy(value["derivation_corpus"])
        for sole_decision in both:
            with self.subTest(sole_decision=sole_decision):
                prior["disposing_decision_ids"] = [sole_decision]
                self.assertFalse(self.valid_with_count(value, count))
                # Only restoring the omitted declaration repairs the same artifact.
                prior["disposing_decision_ids"] = both
                self.assertTrue(self.valid_with_count(value, count))
                self.assertEqual(value["derivation_corpus"], original_members)

    def test_l1_synthetic_disposed_diagnostics_validate(self):
        self.assertTrue(self.valid(self.bound()))

    def test_issuer_rejects_duplicate_json_keys(self):
        row = json.loads(dispositions.DISPOSITION_REGISTRY_PATH.read_bytes())[0]
        raw = ('[' + json.dumps(row)[:-1] + ', "content_id": "' + row["content_id"] + '"}]').encode()
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_bytes(raw)
            with patch.object(issuer, "DISPOSITION_REGISTRY_SHA256", hashlib.sha256(raw).hexdigest()):
                with self.assertRaisesRegex(issuer.PrepareRefusal, "duplicate JSON key"):
                    issuer._registered_dispositions(path)

    def test_l2_unlisted_foreign_valid_refuses(self):
        value = self.bound()
        row = dict(value["prior_observation_set"]["observations"][0])
        row.update(content_id="a" * 64, epoch_id=next(key for key, epoch in value["prior_observation_set"]["epoch_catalog"].items() if epoch == value["identity_epoch"]), disposition="valid",
                   attempt_id="foreign-extra", session_id="d079-epoch-25g83-derivation-n1-20260919")
        value["prior_observation_set"]["observations"].append(row)
        value["backfill_candidate"]["candidate_inventory"]["valid"] += 1
        self.assertFalse(self.valid_with_count(value, self.generation["prior_observation_count"] + 1))
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] |= {"a" * 64}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertTrue(self.valid_with_count(value, self.generation["prior_observation_count"] + 1))

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
        self.assertFalse(self.valid_with_count(value, self.generation["prior_observation_count"] - 1))
        altered = copy.deepcopy(dispositions.DISPOSITION_DECISIONS)
        altered[dispositions.DISPOSITION_DECISION_ID]["content_ids"] -= {victim}
        with patch.object(dispositions, "DISPOSITION_DECISIONS", altered):
            self.assertTrue(self.valid_with_count(value, self.generation["prior_observation_count"] - 1))

    def test_l6_disposed_inside_registration_refuses(self):
        value = self.bound()
        victim = next(iter(dispositions.DISPOSITION_DECISIONS[dispositions.DISPOSITION_DECISION_ID]["content_ids"]))
        row = next(row for row in value["prior_observation_set"]["observations"] if row["content_id"] == victim)
        row["session_id"] = self.generation["registration_session_ids"][0]
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
                        if row.get("session_id") is None)
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
                    row["path"]), acceptance_id)


if __name__ == "__main__":
    unittest.main()
