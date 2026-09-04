"""Contract tests for the single paper-supply custody seam."""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import subprocess
import tempfile
import unittest
from collections.abc import Mapping, Sequence
from pathlib import Path
from unittest import mock

from joulewise import paper_custody as custody


_FIXTURE_SCHEMA = "joulewise.paper_custody_fixture.v1"
_FIXTURE_CATALOG = (
    Path(__file__).parent / "fixtures/paper_custody/family_catalog.json"
)


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


_FAMILIES = {
    "reported_energy_parents": (
        custody.ReportedEnergyParentsRef,
        (
            ("extraction_spec", custody.InputRole.EXTRACTION_SPEC, "git_blob"),
            ("extraction_report", custody.InputRole.EXTRACTION_REPORT, "generated"),
            ("whole_window_basis", custody.InputRole.WHOLE_WINDOW_BASIS, "generated"),
            ("g2a_selection", custody.InputRole.G2A_SELECTION, "git_blob"),
            ("prompt_pin", custody.InputRole.PROMPT_PIN, "git_blob"),
        ),
    ),
    "d165_closeout": (
        custody.D165CloseoutRef,
        (
            ("closeout", custody.InputRole.D165_CLOSEOUT, "generated"),
            ("finalized_manifest", custody.InputRole.FINALIZED_MANIFEST, "generated"),
            ("floor_artifact", custody.InputRole.FLOOR_ARTIFACT, "generated"),
            ("replay_sidecar", custody.InputRole.REPLAY_SIDECAR, "generated"),
        ),
    ),
    "whole_window_verdict": (
        custody.WholeWindowVerdictRef,
        (
            ("campaign_log", custody.InputRole.CAMPAIGN_LOG, "generated"),
            ("standalone_verdict", custody.InputRole.STANDALONE_VERDICT, "generated"),
            ("prospective_manifest", custody.InputRole.PROSPECTIVE_MANIFEST, "generated"),
            ("plan", custody.InputRole.PLAN, "git_blob"),
        ),
    ),
    "claim_evidence": (
        custody.ClaimEvidenceRef,
        (
            ("claim_verdicts", custody.InputRole.CLAIM_VERDICTS, "generated"),
            ("claim_side_bound", custody.InputRole.CLAIM_SIDE_BOUND, "generated"),
            ("finalized_manifest", custody.InputRole.FINALIZED_MANIFEST, "generated"),
            ("floor_artifact", custody.InputRole.FLOOR_ARTIFACT, "generated"),
        ),
    ),
    "transfer_projection": (
        custody.TransferProjectionRef,
        (
            ("result_projection", custody.InputRole.TRANSFER_RESULT, "generated"),
            ("reviewed_capture", custody.InputRole.REVIEWED_CAPTURE, "generated"),
            ("plan", custody.InputRole.PLAN, "git_blob"),
            ("pre_data_receipt", custody.InputRole.PRE_DATA_RECEIPT, "generated"),
            ("pulse_bound_source", custody.InputRole.PULSE_BOUND_SOURCE, "git_blob"),
            ("bundle_inventory", custody.InputRole.BUNDLE_INVENTORY, "generated"),
        ),
    ),
}


class _FamilyFixture:
    def __init__(self, family: str) -> None:
        ref_type, fields = _FAMILIES[family]
        self.family = family
        self.ref_type = ref_type
        self.fields = fields
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        (self.root / "inputs").mkdir()
        self.bindings: dict[str, custody.BoundFile] = {}
        inventory_rows: list[dict[str, str]] = []
        receipt_inputs: list[dict[str, str]] = []
        for field, role, authority in fields:
            suffix = ".jsonl" if role is custody.InputRole.CAMPAIGN_LOG else ".json"
            relative = f"inputs/{field}{suffix}"
            raw = _json_bytes(
                {
                    "family": family,
                    "marker": "synthetic-no-measurement-value",
                    "role": role.value,
                    "schema_version": _FIXTURE_SCHEMA,
                }
            )
            (self.root / relative).write_bytes(raw)
            digest = _sha(raw)
            self.bindings[field] = custody.BoundFile(
                path=Path(relative), expected_sha256=digest, role=role
            )
            inventory_rows.append(
                {
                    "authority": authority,
                    "path": relative,
                    "role": role.value,
                    "sha256": digest,
                }
            )
            receipt_inputs.append(
                {"path": relative, "role": role.value, "sha256": digest}
            )

        validator = f"joulewise.paper_custody.{family}.v1"
        validator_source_sha256 = custody._validator_source_sha256(family)
        receipt_value = {
            "family": family,
            "inputs": sorted(receipt_inputs, key=lambda row: row["role"]),
            "replay_codes": [],
            "schema_version": "joulewise.paper_custody_receipt.v1",
            "status": "PASS",
            "validator": validator,
            "validator_source_sha256": validator_source_sha256,
        }
        receipt_relative = "inputs/validator_receipt.json"
        receipt_raw = _json_bytes(receipt_value)
        (self.root / receipt_relative).write_bytes(receipt_raw)
        receipt_file = custody.BoundFile(
            path=Path(receipt_relative),
            expected_sha256=_sha(receipt_raw),
            role=custody.InputRole.VALIDATOR_RECEIPT,
        )
        self.receipt = custody.ReceiptRef(
            file=receipt_file,
            schema="joulewise.paper_custody_receipt.v1",
            validator=validator,
            validator_source_sha256=validator_source_sha256,
        )
        inventory_rows.append(
            {
                "authority": "generated",
                "path": receipt_relative,
                "role": custody.InputRole.VALIDATOR_RECEIPT.value,
                "sha256": _sha(receipt_raw),
            }
        )
        inventory_value = {
            "family": family,
            "files": sorted(inventory_rows, key=lambda row: row["role"]),
            "inventory_id": f"fixture-{family}",
            "mode": "test_fixture_non_issuing",
            "schema_version": "joulewise.paper_custody_inventory.v1",
        }
        inventory_relative = "inventory.json"
        inventory_raw = _json_bytes(inventory_value)
        (self.root / inventory_relative).write_bytes(inventory_raw)
        self.inventory = custody.BoundFile(
            path=Path(inventory_relative),
            expected_sha256=_sha(inventory_raw),
            role=custody.InputRole.CUSTODY_INVENTORY,
        )
        self.ref = ref_type(
            root=self.root,
            inventory=self.inventory,
            receipt=self.receipt,
            **self.bindings,
        )
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "paper-custody@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Paper Custody Fixture"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture anchor"], cwd=self.root, check=True
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def replace_binding_digest(self, record: custody.VerifiedDigest) -> None:
        actual = _sha((self.root / record.relative_path).read_bytes())
        if record.role is custody.InputRole.CUSTODY_INVENTORY:
            self.inventory = dataclasses.replace(
                self.inventory, expected_sha256=actual
            )
            self.ref = dataclasses.replace(self.ref, inventory=self.inventory)
            return
        if record.role is custody.InputRole.VALIDATOR_RECEIPT:
            receipt_file = dataclasses.replace(
                self.receipt.file, expected_sha256=actual
            )
            self.receipt = dataclasses.replace(self.receipt, file=receipt_file)
            self.ref = dataclasses.replace(self.ref, receipt=self.receipt)
            return
        for field, role, _authority in self.fields:
            if role is record.role:
                binding = dataclasses.replace(
                    getattr(self.ref, field), expected_sha256=actual
                )
                self.ref = dataclasses.replace(self.ref, **{field: binding})
                receipt_path = self.root / self.receipt.file.path
                receipt_value = json.loads(receipt_path.read_text(encoding="utf-8"))
                for row in receipt_value["inputs"]:
                    if row["role"] == role.value:
                        row["sha256"] = actual
                        break
                else:
                    raise AssertionError(f"receipt omitted census role {role}")
                receipt_raw = _json_bytes(receipt_value)
                receipt_path.write_bytes(receipt_raw)
                receipt_file = dataclasses.replace(
                    self.receipt.file, expected_sha256=_sha(receipt_raw)
                )
                self.receipt = dataclasses.replace(
                    self.receipt, file=receipt_file
                )
                self.ref = dataclasses.replace(self.ref, receipt=self.receipt)
                return
        raise AssertionError(f"unmapped census role {record.role}")


class PaperCustodyCensusTests(unittest.TestCase):
    def test_fixture_catalog_is_complete_and_contains_no_measurement_values(self) -> None:
        catalog = json.loads(_FIXTURE_CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(catalog["families"], sorted(_FAMILIES))
        self.assertEqual(catalog["marker"], "synthetic-no-measurement-value")
        self.assertEqual(
            set(catalog), {"families", "marker", "schema_version"}
        )

    def _baseline_records(
        self, fixture: _FamilyFixture
    ) -> tuple[custody.VerifiedDigest, ...]:
        if fixture.family == "whole_window_verdict":
            with self.assertRaises(custody.PaperCustodyRefusal) as raised:
                custody.open_paper_input(fixture.ref)
            self.assertEqual(
                raised.exception.code,
                "paper_custody_blocked_pending_receipt",
            )
            self.assertEqual(raised.exception.rendered_output, ())
            return raised.exception.records
        opened = custody.open_paper_input(fixture.ref)
        self.assertFalse(opened.evidence.issuance_authorized)
        self.assertEqual(opened.evidence.mode, "test_fixture_non_issuing")
        return opened.evidence.inputs

    def test_every_family_actual_read_census_refuses_all_three_attack_arms(
        self,
    ) -> None:
        """Raw, caller-resealed, and replay/reopen attacks return no output."""

        for family in _FAMILIES:
            with self.subTest(family=family):
                fixture = _FamilyFixture(family)
                self.addCleanup(fixture.close)
                records = self._baseline_records(fixture)
                expected_roles = {
                    custody.InputRole.CUSTODY_INVENTORY,
                    custody.InputRole.VALIDATOR_RECEIPT,
                    *(role for _field, role, _authority in fixture.fields),
                }
                self.assertEqual({record.role for record in records}, expected_roles)
                self.assertTrue(all(record.read_count == 2 for record in records))

                for record in records:
                    path = fixture.root / record.relative_path
                    original = path.read_bytes()
                    try:
                        path.write_bytes(b"!" + original[1:])
                        with self.assertRaises(custody.PaperCustodyRefusal) as raw:
                            custody.open_paper_input(fixture.ref)
                        self.assertEqual(raw.exception.code, "paper_custody_digest_mismatch")
                        self.assertEqual(raw.exception.rendered_output, ())
                    finally:
                        path.write_bytes(original)

                    try:
                        value = json.loads(original.decode("utf-8"))
                        if isinstance(value, dict):
                            value["caller_resealed"] = True
                            path.write_bytes(_json_bytes(value))
                        else:
                            self.fail("paper-custody fixture must be one JSON object")
                        fixture.replace_binding_digest(record)
                        with self.assertRaises(custody.PaperCustodyRefusal) as resealed:
                            custody.open_paper_input(fixture.ref)
                        self.assertEqual(
                            resealed.exception.code,
                            "paper_custody_anchor_mismatch",
                        )
                        self.assertEqual(resealed.exception.rendered_output, ())
                    finally:
                        path.write_bytes(original)
                        fixture = _FamilyFixture(family)
                        self.addCleanup(fixture.close)

                    record = next(
                        item
                        for item in self._baseline_records(fixture)
                        if item.role is record.role
                    )
                    path = fixture.root / record.relative_path
                    original = path.read_bytes()
                    original_hook = custody._after_validator_replay

                    def replace_after_replay(state, *, _path=path, _raw=original):
                        original_hook(state)
                        _path.write_bytes(_raw + b" ")

                    try:
                        with mock.patch.object(
                            custody,
                            "_after_validator_replay",
                            side_effect=replace_after_replay,
                        ):
                            with self.assertRaises(custody.PaperCustodyRefusal) as reopened:
                                custody.open_paper_input(fixture.ref)
                        self.assertEqual(
                            reopened.exception.code,
                            "paper_custody_input_changed",
                        )
                        self.assertEqual(reopened.exception.rendered_output, ())
                    finally:
                        path.write_bytes(original)


class PaperCustodyApiTests(unittest.TestCase):
    def test_five_outputs_are_distinct_frozen_noncontainer_types(self) -> None:
        output_types = (
            custody.VerifiedReportedEnergyParents,
            custody.VerifiedD165Closeout,
            custody.VerifiedWholeWindowVerdict,
            custody.VerifiedClaimEvidence,
            custody.VerifiedTransferProjection,
        )
        self.assertEqual(len(set(output_types)), 5)
        for output_type in output_types:
            self.assertTrue(dataclasses.is_dataclass(output_type))
            self.assertTrue(output_type.__dataclass_params__.frozen)
            self.assertFalse(issubclass(output_type, (Mapping, Sequence, bytes)))

    def test_public_read_operation_is_only_open_paper_input(self) -> None:
        public_functions = {
            name
            for name, value in vars(custody).items()
            if inspect.isfunction(value)
            and value.__module__ == custody.__name__
            and not name.startswith("_")
        }
        self.assertEqual(public_functions, {"open_paper_input"})

    def test_refusal_namespace_is_closed_and_nonrendering(self) -> None:
        self.assertIn(
            "paper_custody_blocked_pending_receipt",
            custody.PAPER_CUSTODY_REFUSAL_CODES,
        )
        self.assertTrue(
            all(
                code.startswith("paper_custody_")
                for code in custody.PAPER_CUSTODY_REFUSAL_CODES
            )
        )
        refusal = custody.PaperCustodyRefusal(
            "paper_custody_validator_refused",
            input_role=custody.InputRole.EXTRACTION_SPEC,
            validator_codes=("private_validator_detail",),
        )
        self.assertNotIn("private_validator_detail", str(refusal))
        self.assertEqual(refusal.rendered_output, ())


if __name__ == "__main__":
    unittest.main()
