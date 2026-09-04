"""Contract tests for the single paper-supply custody seam."""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import re
import subprocess
import tempfile
import unittest
from collections.abc import Mapping, Sequence
from pathlib import Path
from unittest import mock

from joulewise import paper_custody as custody
from joulewise import identity_pins
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.identity_pins import IdentityPinProjectionError


ROOT = Path(__file__).resolve().parents[1]
SUPPLY_MAP = ROOT / "configs/paper_supply/supply_map.json"
FIXTURE_CATALOG = ROOT / "tests/fixtures/paper_custody/family_catalog.json"
FIXTURE_SCHEMA = "joulewise.paper_custody_fixture.v1"


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
            custody.InputRole.EXTRACTION_SPEC,
            custody.InputRole.EXTRACTION_REPORT,
            custody.InputRole.WHOLE_WINDOW_BASIS,
            custody.InputRole.G2A_SELECTION,
            custody.InputRole.PROMPT_PIN,
        ),
    ),
    "d165_closeout": (
        custody.D165CloseoutRef,
        (
            custody.InputRole.D165_CLOSEOUT,
            custody.InputRole.FINALIZED_MANIFEST,
            custody.InputRole.FLOOR_ARTIFACT,
            custody.InputRole.REPLAY_SIDECAR,
        ),
    ),
    "whole_window_verdict": (
        custody.WholeWindowVerdictRef,
        (
            custody.InputRole.CAMPAIGN_LOG,
            custody.InputRole.STANDALONE_VERDICT,
            custody.InputRole.PROSPECTIVE_MANIFEST,
            custody.InputRole.PLAN,
        ),
    ),
    "claim_evidence": (
        custody.ClaimEvidenceRef,
        (
            custody.InputRole.CLAIM_VERDICTS,
            custody.InputRole.CLAIM_SIDE_BOUND,
            custody.InputRole.FINALIZED_MANIFEST,
            custody.InputRole.FLOOR_ARTIFACT,
        ),
    ),
    "transfer_projection": (
        custody.TransferProjectionRef,
        (
            custody.InputRole.TRANSFER_RESULT,
            custody.InputRole.REVIEWED_CAPTURE,
            custody.InputRole.PLAN,
            custody.InputRole.PRE_DATA_RECEIPT,
            custody.InputRole.PULSE_BOUND_SOURCE,
            custody.InputRole.BUNDLE_INVENTORY,
        ),
    ),
}


class _FamilyFixture:
    def __init__(self, family: str) -> None:
        ref_type, roles = _FAMILIES[family]
        self.family = family
        self.roles = roles
        self.role = f"fixture.{family}"
        self._temporary = tempfile.TemporaryDirectory()
        temporary = Path(self._temporary.name)
        self.runs_root = temporary / "runs"
        self.anchor_root = temporary / "anchor"
        self.runs_root.mkdir()
        self.anchor_root.mkdir()

        supply_map_raw = SUPPLY_MAP.read_bytes()
        supply_map = json.loads(supply_map_raw)
        self.entry = supply_map["roles"][self.role]
        input_by_role = {row["role"]: row for row in self.entry["inputs"]}

        receipt_inputs: list[dict[str, str]] = []
        inventory_rows: list[dict[str, str]] = []
        for role in roles:
            row = input_by_role[role.value]
            raw = _json_bytes(
                {
                    "family": family,
                    "marker": "synthetic-no-measurement-value",
                    "role": role.value,
                    "schema_version": FIXTURE_SCHEMA,
                }
            )
            self._write(row["path"], raw)
            if _sha(raw) != row["expected_sha256"]:
                raise AssertionError(f"stale supply-map fixture digest: {role.value}")
            receipt_inputs.append(
                {
                    "path": row["path"],
                    "role": role.value,
                    "sha256": row["expected_sha256"],
                }
            )
            inventory_rows.append(
                {
                    "authority": row["authority"],
                    "path": row["path"],
                    "role": role.value,
                    "sha256": row["expected_sha256"],
                }
            )

        validator = self.entry["validator"]
        receipt_raw = _json_bytes(
            {
                "family": family,
                "inputs": sorted(receipt_inputs, key=lambda row: row["role"]),
                "replay_codes": [],
                "schema_version": "joulewise.paper_custody_receipt.v1",
                "status": "PASS",
                "validator": validator,
                "validator_source_sha256": custody._validator_source_sha256(family),
            }
        )
        receipt = self.entry["receipt"]
        self._write(receipt["path"], receipt_raw)
        if _sha(receipt_raw) != receipt["expected_sha256"]:
            raise AssertionError(f"stale supply-map receipt digest: {family}")
        inventory_rows.append(
            {
                "authority": "generated",
                "path": receipt["path"],
                "role": custody.InputRole.VALIDATOR_RECEIPT.value,
                "sha256": receipt["expected_sha256"],
            }
        )
        inventory_raw = _json_bytes(
            {
                "family": family,
                "files": sorted(inventory_rows, key=lambda row: row["role"]),
                "inventory_id": f"fixture-{family}",
                "mode": "test_fixture_non_issuing",
                "schema_version": "joulewise.paper_custody_inventory.v1",
            }
        )
        inventory = self.entry["inventory"]
        self._write(inventory["path"], inventory_raw)
        if _sha(inventory_raw) != inventory["expected_sha256"]:
            raise AssertionError(f"stale supply-map inventory digest: {family}")

        anchor_map = self.anchor_root / custody._SUPPLY_MAP_PATH
        anchor_map.parent.mkdir(parents=True)
        anchor_map.write_bytes(supply_map_raw)
        subprocess.run(["git", "init", "-q"], cwd=self.anchor_root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "paper-custody@example.invalid"],
            cwd=self.anchor_root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Paper Custody Fixture"],
            cwd=self.anchor_root,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.anchor_root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture supply map"],
            cwd=self.anchor_root,
            check=True,
        )
        self.head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.anchor_root,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()
        self._anchor_patch = mock.patch.object(
            custody,
            "_mint_git_anchor",
            side_effect=lambda **_kwargs: (self.anchor_root, self.head),
        )
        self._anchor_patch.start()
        self.ref = ref_type(role=self.role, runs_root=self.runs_root)

    def _write(self, relative: str, raw: bytes) -> None:
        path = self.runs_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def path_for(self, record: custody.VerifiedDigest) -> Path:
        return self.runs_root / record.relative_path

    def full_reseal(self, record: custody.VerifiedDigest) -> None:
        target_role = record.role
        target_path = self.path_for(record)
        if record.role is custody.InputRole.CUSTODY_INVENTORY:
            first = self.entry["inputs"][0]
            target_role = custody.InputRole(first["role"])
            target_path = self.runs_root / first["path"]
        path = target_path
        value = json.loads(path.read_text(encoding="utf-8"))
        value["caller_resealed"] = True
        path.write_bytes(_json_bytes(value))

        actual = _sha(path.read_bytes())
        receipt_path = self.runs_root / self.entry["receipt"]["path"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if target_role is not custody.InputRole.VALIDATOR_RECEIPT:
            next(
                row for row in receipt["inputs"] if row["role"] == target_role.value
            )["sha256"] = actual
        else:
            receipt["caller_resealed"] = True
        receipt_path.write_bytes(_json_bytes(receipt))
        inventory_path = self.runs_root / self.entry["inventory"]["path"]
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        if target_role is not custody.InputRole.VALIDATOR_RECEIPT:
            next(
                row for row in inventory["files"] if row["role"] == target_role.value
            )["sha256"] = actual
        next(
            row
            for row in inventory["files"]
            if row["role"] == custody.InputRole.VALIDATOR_RECEIPT.value
        )["sha256"] = _sha(receipt_path.read_bytes())
        inventory_path.write_bytes(_json_bytes(inventory))

        anchor_map = self.anchor_root / custody._SUPPLY_MAP_PATH
        supply_map = json.loads(anchor_map.read_text(encoding="utf-8"))
        supply_map["roles"][self.role]["inventory"]["expected_sha256"] = _sha(
            inventory_path.read_bytes()
        )
        anchor_map.write_bytes(_json_bytes(supply_map))
        subprocess.run(["git", "add", "."], cwd=self.anchor_root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "reseal fixture inventory envelope"],
            cwd=self.anchor_root,
            check=True,
        )
        self.head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.anchor_root,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()

    def close(self) -> None:
        self._anchor_patch.stop()
        self._temporary.cleanup()


class PaperCustodyCensusTests(unittest.TestCase):
    def _fixture(self, family: str) -> _FamilyFixture:
        fixture = _FamilyFixture(family)
        self.addCleanup(fixture.close)
        return fixture

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

    def test_supply_map_and_fixture_catalog_cover_exactly_five_families(self) -> None:
        supply_map = json.loads(SUPPLY_MAP.read_text(encoding="utf-8"))
        catalog = json.loads(FIXTURE_CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(supply_map["schema_version"], "joulewise.paper_supply_map.v1")
        self.assertEqual(
            set(supply_map["roles"]),
            {f"fixture.{family}" for family in _FAMILIES},
        )
        self.assertEqual(catalog["families"], sorted(_FAMILIES))
        self.assertEqual(catalog["marker"], "synthetic-no-measurement-value")

    def test_every_family_actual_read_census_refuses_all_three_attack_arms(
        self,
    ) -> None:
        for family in _FAMILIES:
            with self.subTest(family=family):
                fixture = self._fixture(family)
                records = self._baseline_records(fixture)
                expected_roles = {
                    custody.InputRole.CUSTODY_INVENTORY,
                    custody.InputRole.VALIDATOR_RECEIPT,
                    *fixture.roles,
                }
                self.assertEqual({record.role for record in records}, expected_roles)
                self.assertTrue(all(record.read_count == 2 for record in records))

                for original_record in records:
                    raw_fixture = self._fixture(family)
                    raw_record = next(
                        record
                        for record in self._baseline_records(raw_fixture)
                        if record.role is original_record.role
                    )
                    path = raw_fixture.path_for(raw_record)
                    raw = path.read_bytes()
                    path.write_bytes(b"!" + raw[1:])
                    with self.assertRaises(custody.PaperCustodyRefusal) as flipped:
                        custody.open_paper_input(raw_fixture.ref)
                    self.assertEqual(
                        flipped.exception.code, "paper_custody_digest_mismatch"
                    )
                    self.assertEqual(flipped.exception.rendered_output, ())

                    sealed_fixture = self._fixture(family)
                    sealed_record = next(
                        record
                        for record in self._baseline_records(sealed_fixture)
                        if record.role is original_record.role
                    )
                    sealed_fixture.full_reseal(sealed_record)
                    with self.assertRaises(custody.PaperCustodyRefusal) as resealed:
                        custody.open_paper_input(sealed_fixture.ref)
                    self.assertEqual(
                        resealed.exception.code, "paper_custody_anchor_mismatch"
                    )
                    self.assertEqual(resealed.exception.rendered_output, ())

                    reopened_fixture = self._fixture(family)
                    reopened_record = next(
                        record
                        for record in self._baseline_records(reopened_fixture)
                        if record.role is original_record.role
                    )
                    reopen_path = reopened_fixture.path_for(reopened_record)
                    reopen_raw = reopen_path.read_bytes()
                    original_hook = custody._after_validator_replay

                    def replace_after_replay(
                        state: object,
                        *,
                        _path: Path = reopen_path,
                        _raw: bytes = reopen_raw,
                    ) -> None:
                        original_hook(state)
                        _path.write_bytes(_raw + b" ")

                    with mock.patch.object(
                        custody,
                        "_after_validator_replay",
                        side_effect=replace_after_replay,
                    ):
                        with self.assertRaises(
                            custody.PaperCustodyRefusal
                        ) as reopened:
                            custody.open_paper_input(reopened_fixture.ref)
                    self.assertEqual(
                        reopened.exception.code, "paper_custody_input_changed"
                    )
                    self.assertEqual(reopened.exception.rendered_output, ())


class PaperCustodyApiTests(unittest.TestCase):
    def _fixture(self, family: str) -> _FamilyFixture:
        fixture = _FamilyFixture(family)
        self.addCleanup(fixture.close)
        return fixture

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

    def test_verified_outputs_refuse_empty_public_construction(self) -> None:
        for output_type in (
            custody.VerifiedReportedEnergyParents,
            custody.VerifiedD165Closeout,
            custody.VerifiedWholeWindowVerdict,
            custody.VerifiedClaimEvidence,
            custody.VerifiedTransferProjection,
        ):
            with self.subTest(output_type=output_type.__name__):
                with self.assertRaises(custody.PaperCustodyRefusal) as raised:
                    output_type()
                self.assertEqual(
                    raised.exception.code, "paper_custody_request_invalid"
                )

    def test_evidence_and_verified_outputs_require_the_private_seam_token(
        self,
    ) -> None:
        with self.assertRaises(custody.PaperCustodyRefusal) as direct:
            custody.CustodyEvidence(
                family="d165_closeout",
                inputs=(),
                receipt_sha256="0" * 64,
                validator_source_sha256="1" * 64,
                mode="production",
                issuance_authorized=True,
            )
        self.assertEqual(direct.exception.code, "paper_custody_request_invalid")
        with self.assertRaises(custody.PaperCustodyRefusal):
            custody._construct_custody_evidence(
                object(),
                family="d165_closeout",
                inputs=(),
                receipt_sha256="0" * 64,
                validator_source_sha256="1" * 64,
                anchor_head="2" * 40,
                supply_map_sha256="3" * 64,
                mode="production",
                issuance_authorized=True,
            )

        forged_evidence = object.__new__(custody.CustodyEvidence)
        object.__setattr__(forged_evidence, "issuance_authorized", True)
        with self.assertRaises(custody.PaperCustodyRefusal):
            _ = forged_evidence.issuance_authorized

        for output_type in (
            custody.VerifiedReportedEnergyParents,
            custody.VerifiedD165Closeout,
            custody.VerifiedWholeWindowVerdict,
            custody.VerifiedClaimEvidence,
            custody.VerifiedTransferProjection,
        ):
            with self.subTest(output_type=output_type.__name__):
                forged = object.__new__(output_type)
                object.__setattr__(forged, "evidence", forged_evidence)
                object.__setattr__(forged, "_payload", object())
                with self.assertRaises(custody.PaperCustodyRefusal):
                    _ = forged.evidence

    def test_verified_evidence_carries_anchor_commit_and_supply_map_digest(self) -> None:
        fixture = self._fixture("reported_energy_parents")
        opened = custody.open_paper_input(fixture.ref)
        self.assertEqual(opened.evidence.anchor_head, fixture.head)
        self.assertEqual(
            opened.evidence.supply_map_sha256,
            _sha((fixture.anchor_root / custody._SUPPLY_MAP_PATH).read_bytes()),
        )

    def test_no_post_pin_inventory_digest_comparison_remains_unreachable(self) -> None:
        source = inspect.getsource(custody._open_paper_input_impl)
        self.assertNotIn('row["sha256"] != _sha256(raw)', source)

    def test_anchor_refuses_head_not_contained_in_origin_main(self) -> None:
        mint_module = identity_pins._load_mint_module()
        with mock.patch.object(
            mint_module,
            "_actual_v2_git_state",
            return_value=("a" * 40, False),
        ):
            with self.assertRaises(IdentityPinProjectionError) as raised:
                identity_pins._mint_git_anchor(require_origin_main=True)
        self.assertEqual(
            raised.exception.reason_code,
            "readiness_identity_artifact_unreadable",
        )

    def test_real_anchor_refuses_untracked_nongoverned_file_without_mocking(self) -> None:
        probe = (
            ROOT
            / "docs/process_traces/2026-09-04-paper-custody"
            / ".untracked-nongoverned-anchor-probe"
        )
        self.assertFalse(probe.exists())
        probe.write_text("anchor probe\n", encoding="utf-8")
        try:
            with self.assertRaises(IdentityPinProjectionError) as raised:
                identity_pins._mint_git_anchor(require_origin_main=True)
        finally:
            probe.unlink()
        self.assertEqual(
            raised.exception.reason_code,
            "readiness_identity_environment_dirty",
        )

    def test_validator_source_digest_census_includes_every_governed_member(
        self,
    ) -> None:
        original_getsource = inspect.getsource
        for family in _FAMILIES:
            with self.subTest(family=family):
                census = custody._validator_source_census(family)
                self.assertIn("paper_custody._replay_family", dict(census))
                self.assertIn(
                    "paper_custody._validate_production_documents", dict(census)
                )
                baseline = custody._validator_source_sha256(family)
                for member_id, member in census:
                    with self.subTest(family=family, member=member_id), mock.patch.object(
                        custody.inspect,
                        "getsource",
                        side_effect=lambda candidate, _member=member: (
                            original_getsource(candidate)
                            + ("\n# mutation\n" if candidate is _member else "")
                        ),
                    ):
                        self.assertNotEqual(
                            custody._validator_source_sha256(family), baseline
                        )

    def test_role_lookup_uses_fixed_clean_anchor_and_rejects_unknown_role(self) -> None:
        fixture = self._fixture("reported_energy_parents")
        unknown = custody.ReportedEnergyParentsRef(
            role="fixture.not_registered", runs_root=fixture.runs_root
        )
        with self.assertRaises(custody.PaperCustodyRefusal) as unregistered:
            custody.open_paper_input(unknown)
        self.assertEqual(
            unregistered.exception.code, "paper_custody_role_unregistered"
        )

        with mock.patch.object(
            custody,
            "_mint_git_anchor",
            side_effect=IdentityPinProjectionError(
                "readiness_identity_environment_dirty", "dirty fixture"
            ),
        ):
            with self.assertRaises(custody.PaperCustodyRefusal) as dirty:
                custody.open_paper_input(fixture.ref)
        self.assertEqual(dirty.exception.code, "paper_custody_anchor_unavailable")

    def test_malformed_map_digest_and_nested_session_are_closed_refusals(self) -> None:
        fixture = self._fixture("reported_energy_parents")
        supply_map = json.loads(SUPPLY_MAP.read_text(encoding="utf-8"))
        supply_map["roles"][fixture.role]["inputs"][0]["expected_sha256"] = None
        with mock.patch.object(custody, "_git_blob", return_value=_json_bytes(supply_map)):
            with self.assertRaises(custody.PaperCustodyRefusal) as malformed:
                custody.open_paper_input(fixture.ref)
        self.assertEqual(
            malformed.exception.code, "paper_custody_supply_map_invalid"
        )

        with V2AuthenticationReadSession():
            with self.assertRaises(custody.PaperCustodyRefusal) as nested:
                custody.open_paper_input(fixture.ref)
        self.assertIn(nested.exception.code, custody.PAPER_CUSTODY_REFUSAL_CODES)

    def test_public_boundary_rejects_supplier_authored_value_shapes(self) -> None:
        for value in ({}, b"{}", object()):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(custody.PaperCustodyRefusal) as raised:
                    custody.open_paper_input(value)
                self.assertEqual(
                    raised.exception.code, "paper_custody_request_invalid"
                )
        forged = object.__new__(custody.VerifiedReportedEnergyParents)
        with self.assertRaises(custody.PaperCustodyRefusal):
            custody.open_paper_input(forged)

    def test_public_read_operation_is_only_open_paper_input(self) -> None:
        public_functions = {
            name
            for name, value in vars(custody).items()
            if inspect.isfunction(value)
            and value.__module__ == custody.__name__
            and not name.startswith("_")
        }
        self.assertEqual(public_functions, {"open_paper_input"})
        self.assertNotIn("BoundFile", custody.__all__)
        self.assertNotIn("ReceiptRef", custody.__all__)

    def test_refusal_namespace_is_closed_and_nonrendering(self) -> None:
        expected = {
            "paper_custody_request_invalid",
            "paper_custody_anchor_unavailable",
            "paper_custody_anchor_mismatch",
            "paper_custody_supply_map_invalid",
            "paper_custody_role_unregistered",
            "paper_custody_path_refused",
            "paper_custody_input_unreadable",
            "paper_custody_digest_mismatch",
            "paper_custody_parse_invalid",
            "paper_custody_receipt_unissued",
            "paper_custody_blocked_pending_receipt",
            "paper_custody_receipt_invalid",
            "paper_custody_receipt_binding_mismatch",
            "paper_custody_validator_refused",
            "paper_custody_evidence_ambiguous",
            "paper_custody_input_changed",
        }
        self.assertEqual(custody.PAPER_CUSTODY_REFUSAL_CODES, expected)
        contract = (
            ROOT / "docs/contracts/paper_supply_custody.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            set(re.findall(r"`(paper_custody_[a-z0-9_]+)`", contract)),
            expected,
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

        source = inspect.getsource(custody)
        for code in expected:
            with self.subTest(reachable=code):
                self.assertGreater(source.count(f'"{code}"'), 1)


if __name__ == "__main__":
    unittest.main()
