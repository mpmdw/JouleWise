"""Contract tests for the single paper-supply custody seam."""

from __future__ import annotations

import ast
import copy
import dataclasses
import io
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
from joulewise import paper_rendering as rendering
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
            self._write(row["path"], raw, base=row["base"])
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

        for row in self.entry["source_census"]:
            raw = _json_bytes({"family": family, "marker": "synthetic-no-measurement-value"})
            self._write(row["path"], raw, base=row["base"])
            assert _sha(raw) == row["expected_sha256"]
            receipt_inputs.append({"path": row["path"], "role": "authenticated_source", "sha256": _sha(raw)})
            inventory_rows.append({"authority": row["authority"], "path": row["path"],
                                   "role": "authenticated_source", "sha256": _sha(raw)})

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

    def _write(self, relative: str, raw: bytes, *, base: str = "runs_root") -> None:
        path = (self.anchor_root if base == "repository" else self.runs_root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def path_for(self, record: custody.VerifiedDigest) -> Path:
        rows = [self.entry["inventory"], self.entry["receipt"], *self.entry["inputs"], *self.entry["source_census"]]
        row = next(row for row in rows if row["path"] == record.relative_path)
        return (self.anchor_root if row["base"] == "repository" else self.runs_root) / record.relative_path

    def full_reseal(self, record: custody.VerifiedDigest) -> None:
        target_role = record.role
        target_path = self.path_for(record)
        if record.role is custody.InputRole.CUSTODY_INVENTORY:
            first = self.entry["inputs"][0]
            target_role = custody.InputRole(first["role"])
            target_path = (self.anchor_root if first["base"] == "repository" else self.runs_root) / first["path"]
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
        opened = custody.open_paper_input(fixture.ref)
        self.assertFalse(opened.evidence.issuance_authorized)
        self.assertEqual(opened.evidence.mode, "test_fixture_non_issuing")
        return opened.evidence.inputs

    def test_supply_map_and_fixture_catalog_cover_exactly_five_families(self) -> None:
        supply_map = json.loads(SUPPLY_MAP.read_text(encoding="utf-8"))
        catalog = json.loads(FIXTURE_CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(supply_map["schema_version"], "joulewise.paper_supply_map.v2")
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
                    custody.InputRole.AUTHENTICATED_SOURCE,
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
            / "tests/fixtures/paper_custody"
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
            "paper_custody_issuance_gate_unregistered",
            "paper_custody_not_issuable",
            "paper_custody_binding_mismatch",
            "paper_custody_issuance_prerequisite_missing",
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



def _refusal_ast_codes(source: str) -> set[str]:
    codes = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Name) and node.func.id == "PaperCustodyRefusal"
            or isinstance(node.func, ast.Attribute) and node.func.attr == "PaperCustodyRefusal"
        ):
            if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                raise AssertionError("refusal constructor requires a literal first argument")
            codes.add(node.args[0].value)
    return codes


def _assert_refusal_census(source: str, expected: set[str]) -> None:
    if _refusal_ast_codes(source) != expected:
        raise AssertionError("refusal constructor/registry/contract census mismatch")


def _issued_control(fixture: _FamilyFixture, *, grants=None, subjects=None, payload=None):
    """Deliberate private reconstruction for wrapper controls, never live evidence."""
    opened = custody.open_paper_input(fixture.ref)
    spec = custody._FAMILY_SPECS[type(fixture.ref)]
    token = opened._custody_token
    subjects = (fixture.role,) if subjects is None else subjects
    grants = (custody._RenderGrant(custody._GRANT_KINDS[fixture.family][0], subjects[0]),) if grants is None else grants
    values = {item.name: getattr(opened.evidence, item.name) for item in dataclasses.fields(opened.evidence)
              if item.name != "_custody_token"}
    values.update(mode="production", issuance_authorized=True, subjects=subjects, grants=grants)
    evidence = custody._construct_custody_evidence(token, **values)
    return custody._construct_verified(token, spec.issuing_type, evidence,
                                       opened._payload if payload is None else custody._freeze_json(payload))


class RoundFiveTests(unittest.TestCase):
    def fixture(self, family="d165_closeout"):
        value = _FamilyFixture(family)
        self.addCleanup(value.close)
        return value

    def assert_code(self, code, function, *args, **kwargs):
        with self.assertRaises(custody.PaperCustodyRefusal) as raised:
            function(*args, **kwargs)
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(raised.exception.rendered_output, ())

    def context(self, family="d165_closeout"):
        fixture = self.fixture(family)
        spec = custody._FAMILY_SPECS[type(fixture.ref)]
        sources = tuple(custody._map_binding({key: value for key, value in row.items() if key != "role"},
                                             role=custody.InputRole(row["role"]), include_authority=True)
                        for row in fixture.entry["inputs"])
        census = tuple(custody._map_binding(row, role=custody.InputRole.AUTHENTICATED_SOURCE,
                                            include_authority=True) for row in fixture.entry["source_census"])
        raws = {binding.role: b"{}" for binding in sources}
        ctx = custody._GateContext(family, fixture.role, "production", "d165-closeout.v1",
                                   (fixture.role,), fixture.anchor_root, fixture.runs_root, fixture.head,
                                   sources, census, raws, V2AuthenticationReadSession())
        return ctx

    def acceptance(self, ctx):
        return _json_bytes({
            "schema_version": "joulewise.paper_floor_acceptance.v1", "status": "PASS",
            "floor_sha256": _sha(ctx.raws[custody.InputRole.FLOOR_ARTIFACT]),
            "sources": sorted([{"path": f"{binding.base}/{binding.path.as_posix()}", "sha256": binding.expected_sha256}
                               for binding in ctx.source_census], key=lambda row: row["path"]),
            "binder_source_sha256": custody._floor_binder_source_sha256(), "anchor_head": ctx.head,
        })

    def test_fixture_results_never_enter_any_renderer(self):
        for family in _FAMILIES:
            fixture = self.fixture(family)
            value = custody.open_paper_input(fixture.ref)
            for name, (expected, grant) in rendering._RENDERERS.items():
                with self.subTest(family=family, renderer=name):
                    self.assert_code("paper_custody_not_issuable", getattr(rendering, name), value)
                    body = mock.Mock(return_value="paper output")
                    guarded = rendering._issued_renderer(expected, grant)(body)
                    self.assert_code("paper_custody_not_issuable", guarded, value)
                    body.assert_not_called()

    def test_issuing_fixture_type_matrix(self):
        all_types = {kind for spec in custody._FAMILY_SPECS.values() for kind in (spec.issuing_type, spec.fixture_type)}
        self.assertEqual(len(all_types), 10)
        for family in _FAMILIES:
            fixture = self.fixture(family)
            spec = custody._FAMILY_SPECS[type(fixture.ref)]
            opened = custody.open_paper_input(fixture.ref)
            self.assertIs(type(opened), spec.fixture_type)
            self.assertEqual(spec.fixture_type.__name__, spec.issuing_type.__name__.replace("Verified", "Fixture", 1))
            self.assertFalse(issubclass(spec.fixture_type, spec.issuing_type))
            for kind in (spec.issuing_type, spec.fixture_type):
                self.assertTrue(kind.__dataclass_params__.frozen)
                self.assertFalse(issubclass(kind, (Mapping, Sequence, bytes)))
                self.assert_code("paper_custody_request_invalid", kind)
                forged = object.__new__(kind)
                self.assert_code("paper_custody_request_invalid", getattr, forged, "evidence")
            self.assertFalse(hasattr(opened, "__dict__"))
            with self.assertRaises(dataclasses.FrozenInstanceError):
                opened.evidence = None
            self.assert_code("paper_custody_not_issuable", custody._construct_verified,
                             opened._custody_token, spec.issuing_type, opened.evidence, opened._payload)
            issued = _issued_control(fixture)
            self.assertIs(type(issued), spec.issuing_type)
            body = mock.Mock(return_value="synthetic issuing control")
            renderer = rendering._issued_renderer(spec.issuing_type, custody._GRANT_KINDS[family][0])(body)
            self.assertEqual(renderer(issued), "synthetic issuing control")
            body.assert_called_once_with(issued)
            for other in all_types - {spec.issuing_type}:
                if other is not spec.fixture_type:
                    self.assert_code("paper_custody_not_issuable", custody._construct_verified,
                                     opened._custody_token, other, issued.evidence, opened._payload)

    def test_closed_gate_registry(self):
        self.assertEqual(set(custody._ISSUANCE_GATES), {("d165_closeout", "d165-closeout.v1")})
        ctx = self.context()
        for gate_id in (None, "unknown.v1", "reported-energy.v1"):
            self.assert_code("paper_custody_issuance_gate_unregistered", custody._run_issuance_gate,
                             dataclasses.replace(ctx, issuance_gate_id=gate_id))
        fixture = self.fixture()
        source_digest = custody._validator_source_sha256("d165_closeout")
        with mock.patch.object(custody, "_validator_source_sha256", return_value=source_digest), mock.patch.object(custody, "_run_issuance_gate", side_effect=AssertionError("fixture gate dispatch")) as dispatch:
            self.assertIs(type(custody.open_paper_input(fixture.ref)), custody.FixtureD165Closeout)
            dispatch.assert_not_called()
        for replay in ((), custody._FamilyReplay(True, True, (), ()), custody._FamilyReplay(False, True, (), ())):
            with mock.patch.dict(custody._ISSUANCE_GATES, {("d165_closeout", "d165-closeout.v1"): lambda _: replay}):
                self.assert_code("paper_custody_not_issuable", custody._run_issuance_gate, ctx)
        self.assert_code("paper_custody_not_issuable", custody._run_issuance_gate,
                         dataclasses.replace(ctx, mode="test_fixture_non_issuing"))
        # A corroborating PASS receipt cannot turn a fixture replay into production.
        with mock.patch.object(custody, "_validator_source_sha256", return_value=source_digest), mock.patch.object(custody, "_replay_family", return_value=custody._FamilyReplay(True, True, (), ())):
            self.assert_code("paper_custody_not_issuable", custody.open_paper_input, fixture.ref)
        supply_map = json.loads((fixture.anchor_root / custody._SUPPLY_MAP_PATH).read_bytes())
        supply_map["roles"][fixture.role]["issuance_gate_id"] = "d165-closeout.v1"
        with mock.patch.object(custody, "_git_blob", return_value=_json_bytes(supply_map)):
            self.assert_code("paper_custody_supply_map_invalid", custody.open_paper_input, fixture.ref)

    def test_d165_gate_branches_and_floor_acceptance(self):
        from joulewise import dominance_closeout as owner
        ctx = self.context()
        # Synthetic gate-policy controls isolate owner authentication. The existing
        # D165 module separately tests all four real owner calls/arithmetic.
        for branch in ("A", "B", None):
            ratios = [{"passes": branch == "A", "status": "ok"}]
            value = dict(owner._expected_global_fields(ratios, ratios, ()),
                         independent_ratios=ratios, comparative_common_mode_ratios=ratios)
            if branch is None:
                value.update(branch=None, refusal_reason="synthetic_structural_refusal",
                             dominance_sentence_licensed=False, subtitle_licensed=False)
            ctx.raws[custody.InputRole.D165_CLOSEOUT] = _json_bytes(value)
            ctx.raws[custody.InputRole.FLOOR_ACCEPTANCE] = self.acceptance(ctx)
            with mock.patch.object(owner, "validate_d165_paper_sources", return_value=()) as replay:
                result = custody._d165_issuance_gate(ctx)
                replay.assert_called_once()
            self.assertTrue(result.authentic)
            self.assertEqual(result.admitted, branch is not None)
            self.assertEqual({grant.kind for grant in result.grants},
                             {"outcome", "dominance_sentence", "subtitle"} if branch == "A"
                             else {"outcome"} if branch == "B" else set())
        with mock.patch.object(owner, "validate_d165_paper_sources", return_value=("owner_refused",)) as replay:
            self.assertFalse(custody._d165_issuance_gate(ctx).authentic)
            replay.assert_called_once()
        baseline = self.acceptance(ctx)
        for field, replacement in (("floor_sha256", "0" * 64), ("sources", []), ("status", "FAIL"),
                                   ("binder_source_sha256", "0" * 64), ("anchor_head", "0" * 40)):
            bad = json.loads(baseline); bad[field] = replacement
            ctx.raws[custody.InputRole.FLOOR_ACCEPTANCE] = _json_bytes(bad)
            with mock.patch.object(owner, "validate_d165_paper_sources", return_value=()):
                self.assert_code("paper_custody_issuance_prerequisite_missing", custody._d165_issuance_gate, ctx)
        ctx.raws.pop(custody.InputRole.FLOOR_ACCEPTANCE)
        with mock.patch.object(owner, "validate_d165_paper_sources", return_value=()):
            self.assert_code("paper_custody_issuance_prerequisite_missing", custody._d165_issuance_gate, ctx)
        ctx.raws[custody.InputRole.FLOOR_ACCEPTANCE] = baseline
        with mock.patch.object(owner, "validate_d165_paper_sources", return_value=()):
            self.assert_code("paper_custody_binding_mismatch", custody._d165_issuance_gate,
                             dataclasses.replace(ctx, subjects=("wrong-subject",)))

    def test_claim_gate_per_contrast(self):
        import base64
        from contextlib import ExitStack
        from joulewise.analysis_engine import claim_side_bound
        ctx = self.context("claim_evidence")
        supported = {"contrast_id": "supported", "claim_role": "primary",
                     "sampling": {"confirmatory_status": "confirmatory"},
                     "estimator": {"estimate": 10, "metrology_aware_CI95": {"lower": 9, "upper": 11}},
                     "deterministic_bounds": {"total": 1, "decision_interval": {"lower": 8, "upper": 12}},
                     "floor": {"active_floor_j": 2}, "multiplicity": {"rejected": True},
                     "claim_evaluation": {"reason_codes": [], "claim_ready_for_l2_l3": True,
                                          "claim_level_ceiling": "L2", "outcome": "direction_supported"}}
        unsupported = copy.deepcopy(supported); unsupported["contrast_id"] = "unsupported"
        unsupported["multiplicity"]["rejected"] = False  # Deliberately lying ready flag.
        demoted = copy.deepcopy(supported); demoted["contrast_id"] = "demoted"
        demoted["sampling"]["confirmatory_status"] = "exploratory"
        artifact = {"evidence_class": "current", "contrasts": [supported, unsupported, demoted],
                    "inputs": {"floor_artifact": {"embedded_bytes_base64": ""}}}
        floor = {"artifact_id": "synthetic-floor", "cells": [{"cell_id": "cell"}]}
        ctx.raws[custody.InputRole.FLOOR_ARTIFACT] = _json_bytes(floor)
        artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"] = base64.b64encode(ctx.raws[custody.InputRole.FLOOR_ARTIFACT]).decode()
        ctx.raws[custody.InputRole.CLAIM_VERDICTS] = _json_bytes(artifact)
        manifest = {"contrasts": [{"contrast_id": row["contrast_id"], "source_cell_ids": ["cell"]} for row in artifact["contrasts"]]}
        ctx.raws[custody.InputRole.FINALIZED_MANIFEST] = _json_bytes(manifest)
        sidecar = {"schema_version": "joulewise.claim_side_bound.v1",
                   "claim_verdicts_sha256": _sha(ctx.raws[custody.InputRole.CLAIM_VERDICTS]),
                   "contrasts": [{"contrast_id": row["contrast_id"], "source_cell_ids": ["cell"],
                                  "floor_artifact_id": "synthetic-floor", "claim_side_bound_j": 1,
                                  "metrology_aware_CI95": row["estimator"]["metrology_aware_CI95"],
                                  "decision_interval": row["deterministic_bounds"]["decision_interval"]}
                                 for row in artifact["contrasts"]]}
        ctx.raws[custody.InputRole.CLAIM_SIDE_BOUND] = _json_bytes(sidecar)
        ctx.raws[custody.InputRole.FLOOR_ACCEPTANCE] = self.acceptance(ctx)
        with ExitStack() as stack:
            owner = stack.enter_context(mock.patch("joulewise.analysis_engine.artifact.validate_claim_verdicts", return_value=[]))
            disk = stack.enter_context(mock.patch("joulewise.analysis_manifest_v3.validate_finalized_analysis_manifest_v3", return_value=[]))
            side = stack.enter_context(mock.patch.object(claim_side_bound, "validate_claim_side_bound", wraps=claim_side_bound.validate_claim_side_bound))
            for subjects, admitted, kinds in [(("supported",), True, {("outcome", "supported"), ("l2", "supported")}),
                                             (("unsupported",), True, {("outcome", "unsupported")}),
                                             (("demoted",), False, set()),
                                             (("supported", "unsupported"), True, {("outcome", "supported"), ("l2", "supported"), ("outcome", "unsupported")}),
                                             (("supported", "demoted"), False, {("outcome", "supported"), ("l2", "supported")})]:
                result = custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=subjects))
                self.assertTrue(result.authentic)
                self.assertEqual(result.admitted, admitted)
                self.assertEqual({(grant.kind, grant.subject_id) for grant in result.grants}, kinds)
            self.assertEqual(owner.call_count, 5); self.assertEqual(disk.call_count, 5); self.assertEqual(side.call_count, 5)
            for field, replacement in (("source_cell_ids", ["wrong"]), ("floor_artifact_id", "wrong"),
                                       ("claim_side_bound_j", 4), ("contrast_id", "wrong")):
                bad = copy.deepcopy(sidecar); bad["contrasts"][0][field] = replacement
                ctx.raws[custody.InputRole.CLAIM_SIDE_BOUND] = _json_bytes(bad)
                self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
            bad = copy.deepcopy(sidecar); bad["claim_verdicts_sha256"] = "0" * 64
            ctx.raws[custody.InputRole.CLAIM_SIDE_BOUND] = _json_bytes(bad)
            self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
            ctx.raws[custody.InputRole.CLAIM_SIDE_BOUND] = _json_bytes(sidecar)
            ctx.raws[custody.InputRole.FLOOR_ARTIFACT] += b" "
            self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
        self.assertNotIn(("claim_evidence", "claim-evidence.v1"), custody._ISSUANCE_GATES)

    def test_gate_sources_change_receipt_digest(self):
        original = inspect.getsource
        count = 0
        for family in _FAMILIES:
            fixture = self.fixture(family)
            with V2AuthenticationReadSession() as session:
                spec = custody._FAMILY_SPECS[type(fixture.ref)]
                supply = custody._load_supply_entry(session, fixture.anchor_root, fixture.head, fixture.role, spec)
            raw = (fixture.runs_root / fixture.entry["receipt"]["path"]).read_bytes()
            census = custody._validator_source_census(family)
            members = dict(census)
            self.assertIn("module:joulewise.paper_custody", members)
            for required in ("_run_issuance_gate", "_validate_grants", "_d165_issuance_gate", "_claim_issuance_gate", "_validate_floor_acceptance", "_make_custody_capability_mint"):
                self.assertIn(f"paper_custody.{required}", members)
            if family == "claim_evidence":
                for required in ("analysis_engine.claims.evaluate_claim", "analysis_engine.claim_side_bound.validate_claim_side_bound",
                                 "analysis_engine.artifact._validate_cross_field_claim_semantics"):
                    self.assertIn(required, members)
            for member_id, member in census:
                with self.subTest(family=family, owner=member_id), mock.patch.object(
                    custody.inspect, "getsource", side_effect=lambda candidate, target=member: original(candidate) + ("\n# kill mutation\n" if candidate is target else "")):
                    self.assert_code("paper_custody_receipt_binding_mismatch", custody._validate_receipt, raw, supply.receipt,
                                     family=family, sources=(*supply.sources, *supply.source_census))
                    count += 1
            with mock.patch.dict(custody._GRANT_KINDS, {family: ("changed-policy",)}):
                self.assert_code("paper_custody_receipt_binding_mismatch", custody._validate_receipt, raw, supply.receipt,
                                 family=family, sources=(*supply.sources, *supply.source_census))
        print(f"KILLED {count} owner-source mutations and 5 grant-policy mutations: stale receipts refused")

    def test_production_git_blob_coverage(self):
        supply = json.loads(SUPPLY_MAP.read_bytes())
        role = "production.reported_energy_parents.qwen3-1p7b.v5"
        path = "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json"
        if role not in supply["roles"]:
            self.assertEqual(supply["pending_roles"][role], {
                "status": "pending_desk_day", "family": "reported_energy_parents", "input_role": "extraction_spec",
                "base": "repository", "authority": "git_blob", "path": path})
            self.assertTrue(all(entry["mode"] == "test_fixture_non_issuing" for entry in supply["roles"].values()))
            print("PENDING production Git-blob role: fixture coverage is not production coverage")
        else:
            entry = supply["roles"][role]
            self.assertEqual(entry["mode"], "production")
            row = next(row for row in entry["inputs"] if row["role"] == "extraction_spec")
            self.assertEqual((row["base"], row["authority"], row["path"]), ("repository", "git_blob", path))
            self.assertEqual(_sha(custody._git_blob(ROOT, "HEAD", path)), row["expected_sha256"])
            self.assertTrue(entry["source_census"])

    def test_git_blob_dispatch_checks_blob_before_parse_and_worktree(self):
        fixture = self.fixture("reported_energy_parents")
        row = fixture.entry["inputs"][0]
        self.assertEqual((row["base"], row["authority"]), ("repository", "git_blob"))
        original = custody._git_blob
        with mock.patch.object(custody, "_git_blob", side_effect=lambda repo, head, path, role=None:
                               b"!invalid" if path == row["path"] else original(repo, head, path, role)) as read:
            self.assert_code("paper_custody_digest_mismatch", custody.open_paper_input, fixture.ref)
            self.assertTrue(any(call.args[2] == row["path"] for call in read.call_args_list))
        # Repo-only source proves root selection; the runs root has no substitute.
        self.assertFalse((fixture.runs_root / row["path"]).exists())
        self.assertIs(type(custody.open_paper_input(fixture.ref)), custody.FixtureReportedEnergyParents)

    def test_contract_threat_model_matches_capability_wire(self):
        contract = (ROOT / "docs/contracts/paper_supply_custody.md").read_text()
        spec = (ROOT / "docs/process_traces/2026-09-04-paper-custody/11-round-5-design-spec-astra.md").read_text()
        for prefix in ("> A verified result is ", "> Whole-window issuance, "):
            exact = next(line[2:] for line in spec.splitlines() if line.startswith(prefix))
            self.assertIn(exact, contract)
        for required in ("ordinary attribute access", "tokenless `object.__new__`", "_construct_custody_evidence",
                         "The token is recoverable from the closure cells of the private guard functions."):
            self.assertIn(required, contract)
        self.assertNotIn("held only inside", contract)
        opened = custody.open_paper_input(self.fixture().ref)
        self.assertIs(opened._custody_token, opened.evidence._custody_token)
        self.assertIn(opened._custody_token, [cell.cell_contents for cell in custody._require_custody_capability.__closure__])

    def test_refusal_constructor_ast_census(self):
        contract = (ROOT / "docs/contracts/paper_supply_custody.md").read_text()
        codes = set(re.findall(r"`(paper_custody_[a-z0-9_]+)`", contract))
        self.assertEqual(codes, custody.PAPER_CUSTODY_REFUSAL_CODES)
        _assert_refusal_census(inspect.getsource(custody), codes)

    def test_refusal_ast_census_kills_dead_literal(self):
        source = inspect.getsource(custody)
        codes = set(custody.PAPER_CUSTODY_REFUSAL_CODES)
        # AST rewrite every constructor for one code, leaving declarations and dead strings.
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "PaperCustodyRefusal" and node.args:
                if isinstance(node.args[0], ast.Constant) and node.args[0].value == "paper_custody_role_unregistered":
                    node.args[0] = ast.Constant("paper_custody_request_invalid")
        variants = [ast.unparse(tree) + '\n"paper_custody_role_unregistered"\n',
                    source + '\nPaperCustodyRefusal("paper_custody_undeclared")\n',
                    source + '\nPaperCustodyRefusal(code)\n']
        for mutation in variants:
            with self.assertRaises(AssertionError):
                _assert_refusal_census(mutation, codes)
        with self.assertRaises(AssertionError):
            _assert_refusal_census(source, codes | {"paper_custody_declared_only"})
        print("KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code")

    def test_unmapped_transitive_reads_and_root_aliases_refuse(self):
        fixture = self.fixture()
        original = custody._replay_family
        source_digest = custody._validator_source_sha256(fixture.family)
        def extra_read(ctx):
            ctx.session.ingest(f"git:{ctx.head}:unmapped.json", b"{}", grammar="json", label="synthetic unmapped owner")
            return original(ctx)
        with mock.patch.object(custody, "_replay_family", side_effect=extra_read), mock.patch.object(custody, "_validator_source_sha256", return_value=source_digest):
            self.assert_code("paper_custody_binding_mismatch", custody.open_paper_input, fixture.ref)
        spec = custody._FAMILY_SPECS[type(fixture.ref)]
        with V2AuthenticationReadSession() as session:
            supply = custody._load_supply_entry(session, fixture.anchor_root, fixture.head, fixture.role, spec)
        alias = dataclasses.replace(supply.sources[0], base="repository", role=custody.InputRole.AUTHENTICATED_SOURCE)
        # The roots coincide; differently labelled bases must not hide one path.
        aliased = dataclasses.replace(supply, source_census=(alias,))
        with mock.patch.object(custody, "_load_supply_entry", return_value=aliased):
            self.assert_code("paper_custody_evidence_ambiguous", custody.open_paper_input,
                             dataclasses.replace(fixture.ref, runs_root=fixture.anchor_root))

    def test_refusal_condition_controls(self):
        fixture = self.fixture()
        with V2AuthenticationReadSession() as session:
            spec = custody._FAMILY_SPECS[type(fixture.ref)]
            supply = custody._load_supply_entry(session, fixture.anchor_root, fixture.head, fixture.role, spec)
            binding = supply.sources[0]
            path = fixture.runs_root / binding.path
            original = path.read_bytes()
            path.write_bytes(b'{"x":1,"x":2}')
            malformed = dataclasses.replace(binding, expected_sha256=_sha(path.read_bytes()))
            self.assert_code("paper_custody_parse_invalid", custody._read_once, session, fixture.anchor_root,
                             fixture.runs_root, malformed, head=fixture.head, bindings=(malformed,))
            path.unlink()
            self.assert_code("paper_custody_input_unreadable", custody._read_once, session, fixture.anchor_root,
                             fixture.runs_root, binding, head=fixture.head, bindings=(binding,))
            path.symlink_to(fixture.runs_root / "missing")
            self.assert_code("paper_custody_path_refused", custody._read_once, session, fixture.anchor_root,
                             fixture.runs_root, binding, head=fixture.head, bindings=(binding,))
            path.unlink(); path.write_bytes(original)
        raw = (fixture.runs_root / fixture.entry["inventory"]["path"]).read_bytes()
        self.assert_code("paper_custody_receipt_invalid", custody._validate_inventory, raw, family=fixture.family,
                         expected=(*supply.sources, *supply.source_census, supply.receipt.file), expected_mode="production")
        self.assert_code("paper_custody_evidence_ambiguous", custody._validate_inventory, raw, family=fixture.family,
                         expected=(), expected_mode="test_fixture_non_issuing")
        with mock.patch.object(custody, "_validate_fixture_documents", return_value=("owner_failure",)):
            self.assert_code("paper_custody_validator_refused", custody.open_paper_input, fixture.ref)
        self.assert_code("paper_custody_binding_mismatch", custody._validate_grants, "d165_closeout", ("one",),
                         (custody._RenderGrant("outcome", "two"),))


if __name__ == "__main__":
    unittest.main()
