from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Mapping
from unittest import mock

import joulewise.arm_readiness as readiness
from joulewise import identity_pins
from joulewise.arm_readiness import (
    ARM_RECEIPT_SCHEMA,
    ASSURANCE,
    DRY_RUN_RECEIPT_SCHEMA,
    EVIDENCE_RECEIPT_SCHEMA,
    FREEZE_RECEIPT_SCHEMA,
    FREEZE_RECEIPT_V2_SCHEMA,
    PACK_DIGEST_ALGORITHM,
    READINESS_REASON_CODES,
    ROW_REGISTRY_ID,
    SYNTHETIC_DOMAINS,
    ArmReadinessError,
    gnu_sidecar,
    load_registry,
    parse_json_bytes,
    render_json,
    validate_arm_context,
    validate_arm_receipt,
    validate_dry_run_receipt,
    validate_evidence_receipt,
    validate_freeze_receipt,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
ZERO_SHA = "0" * 64
TEST_BOOT_SESSION_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def predicate_content(
    predicate_id: str, *, plan_sha256: str | None = None
) -> dict[str, Any]:
    """Build genuine predicate content.

    ``plan_sha256`` is the pack plan SHA that a reservation receipt must
    BIND.  Callers building evidence for a real pack must pass the pack's
    actual value; the ZERO_SHA default exists only for unit fixtures that
    never reach a real pack.
    """

    content = copy.deepcopy(readiness._PREDICATE_CONTENT_REQUIREMENTS[predicate_id])
    if predicate_id == "t0.ledger_reservation.v1":
        content["plan_sha256"] = plan_sha256 or ZERO_SHA
    elif predicate_id == "t0.background_quiet.v1":
        content["closed_operator_observation"] = True
        content["fresh_maintenance_census"] = True
    return content


def predicate_source_kind(evidence_kind: str) -> str:
    preferred = {
        "GIT_CHECKOUT": "GIT",
        "DOCTRINE_PIN": "PACK",
        "ESTIMATOR_IDENTITY": "PACK",
        "PACK_FAMILY": "PACK",
        "LAUNCH_RECIPE": "PROBE",
    }
    return preferred.get(evidence_kind, "PROBE")


def registry_reference(profile: str = "ALPHA") -> dict[str, Any]:
    return {
        "registry_id": ROW_REGISTRY_ID,
        "path": "configs/arm_readiness/d117_row_registry_v1.json",
        "sha256": ZERO_SHA,
        "plan_profile": profile,
    }


def pack_identity(pack_id: str = "d117_floor_qwen25_1p5b_v1") -> dict[str, Any]:
    return {
        "pack_id": pack_id,
        "plan_id": "plan-test",
        "window_id": "window-test",
        "pack_root": "/tmp/pack",
        "plan_path": "calibration_plan.json",
        "plan_sha256": ZERO_SHA,
    }


def pack_record(pack_id: str = "d117_floor_qwen25_1p5b_v1") -> dict[str, Any]:
    return {
        "pack_id": pack_id,
        "plan_id": "plan-test",
        "window_id": "window-test",
        "pack_root": "/tmp/pack",
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
        "pack_sha256": ZERO_SHA,
        "plan_tree_path": "plan_tree.json",
        "plan_tree_sha256": ZERO_SHA,
        "plan_tree_sidecar_path": "plan_tree.sha256",
        "plan_tree_sidecar_sha256": ZERO_SHA,
    }


def arm_context(root: Path | str = "/tmp/readiness") -> dict[str, Any]:
    base = Path(root)
    return {
        "bracket_session_id": "session-1",
        "pre_attempt_id": "attempt-pre",
        "post_attempt_id": "attempt-post",
        "clock_route": "MANUAL",
        "claim_runs_root": str(base / "claim"),
        "bound_runs_root": str(base / "bound"),
        "custody_root": str(base / "custody"),
        "quarantine_root": str(base / "quarantine"),
        "claim_backup_destination": str(base / "backup-claim"),
        "bound_backup_destination": str(base / "backup-bound"),
        "waiver_path": str(base / "waivers.json"),
    }


def sample_freeze(profile: str = "ALPHA") -> dict[str, Any]:
    return {
        "schema_version": FREEZE_RECEIPT_SCHEMA,
        "receipt_kind": "freeze",
        "receipt_id": "freeze-0001",
        "status": "PASS",
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": "2026-08-11T00:00:00Z",
        "pack_identity": pack_identity(),
        "row_registry": registry_reference(profile),
        "evidence": [],
        "rows": [],
        "refusals": [],
        "supersedes": None,
        "assurance": copy.deepcopy(ASSURANCE),
    }


def sample_freeze_predecessor(
    pack_id: str = "d117_floor_qwen25_1p5b_v1",
) -> dict[str, Any]:
    return {
        "pack_id": pack_id,
        "pack_path": f"configs/campaigns/{pack_id}",
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
        "pack_sha256": ZERO_SHA,
        "plan_id": "plan-test",
        "plan_sha256": ZERO_SHA,
        "freeze_receipt": {
            "receipt_id": "freeze-0001",
            "path": "arm_readiness.freeze.receipts/freeze-0001.json",
            "sha256": ZERO_SHA,
        },
        "identity_receipt": {
            "receipt_id": f"{pack_id}/projection-0001",
            "path": "identity_pin_projection.receipts/projection-0001.json",
            "sha256": ZERO_SHA,
        },
        "evidence_set_sha256": ZERO_SHA,
    }


def sample_freeze_v2(
    profile: str = "ALPHA",
    pack_id: str = "d117_floor_qwen25_1p5b_v2",
) -> dict[str, Any]:
    receipt = sample_freeze(profile)
    receipt["schema_version"] = FREEZE_RECEIPT_V2_SCHEMA
    receipt["receipt_id"] = "freeze-0002"
    receipt["pack_identity"] = pack_identity(pack_id)
    del receipt["supersedes"]
    receipt["predecessor"] = sample_freeze_predecessor()
    return receipt


def sample_arm(root: Path | str = "/tmp/readiness") -> dict[str, Any]:
    return {
        "schema_version": ARM_RECEIPT_SCHEMA,
        "receipt_kind": "arm",
        "receipt_id": "arm-0001",
        "mode": "arm",
        "status": "PASS",
        "arm_disposition": "GO",
        "issued_at_utc": "2026-08-11T00:00:00Z",
        "boot_session_id": TEST_BOOT_SESSION_ID,
        "valid_until_monotonic_ns": 10**30,
        "pack": pack_record(),
        "reviewed_main": {
            "head_commit": "a" * 40,
            "head_tree_oid": "b" * 40,
            "local_main_commit": "a" * 40,
            "origin_main_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        },
        "arm_context": arm_context(root),
        "freeze_receipt": {
            "receipt_id": "freeze-0001",
            "path": "arm_readiness.freeze.receipts/freeze-0001.json",
            "sha256": ZERO_SHA,
        },
        "row_registry": registry_reference(),
        "evidence": [],
        "rows": [],
        "refusals": [],
        "supersedes": None,
        "assurance": copy.deepcopy(ASSURANCE),
    }


def sample_dry_run(root: Path | str = "/tmp/readiness") -> dict[str, Any]:
    base = Path(root)
    return {
        "schema_version": DRY_RUN_RECEIPT_SCHEMA,
        "receipt_kind": "dry_run",
        "receipt_id": "dry-run-0001",
        "mode": "dry_run",
        "status": "PASS",
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": "2026-08-11T00:00:00Z",
        "pack": pack_record(),
        "synthetic_context": {
            "rehearsal_id": "rehearsal-1",
            "root": str(base),
            "ledger_path": str(base / "ledger.jsonl"),
            "backend": "synthetic_real_lease_replay.v1",
        },
        "evidence": [],
        "checks": [],
        "omitted_live_domains": list(SYNTHETIC_DOMAINS),
        "refusals": [],
        "assurance": copy.deepcopy(ASSURANCE),
    }


def sample_evidence() -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_RECEIPT_SCHEMA,
        "evidence_id": "evidence-1",
        "kind": "PACK_AUTHENTICATION",
        "status": "PASS",
        "issued_at_utc": "2026-08-11T00:00:00Z",
        "boot_session_id": TEST_BOOT_SESSION_ID,
        "valid_until_monotonic_ns": 10**30,
        "pack_sha256": ZERO_SHA,
        "head_commit": "a" * 40,
        "facts": [
            {
                "fact_id": "desk.current_pack.v1",
                "value_type": "OBJECT",
                "value": predicate_content("desk.current_pack.v1"),
                "source_kind": "GIT",
                "source_path": "source.json",
                "source_sha256": ZERO_SHA,
            }
        ],
        "checks": [],
        "reason_codes": [],
        "assurance": copy.deepcopy(ASSURANCE),
    }


def sample_identity_unit(identity_unit_id: str = "synthetic/decode") -> dict[str, Any]:
    declared = {name: f"synthetic-{name}" for name in identity_pins.DECLARED_IDENTITY_FIELDS}
    runtime = {name: ZERO_SHA for name in identity_pins.MODEL_RUNTIME_CONFIG_FIELDS}
    return {
        "identity_unit_id": identity_unit_id,
        "producer_plan_reference": {
            "plan_id": "plan-test",
            "path": "calibration_plan.json",
        },
        "consumer_bindings": [
            {"arm": "A", "family": "synthetic", "measurement_arm": "decode"}
        ],
        "declared_identity": declared,
        "config_inventory": [{"path": "calibration_plan.json", "sha256": ZERO_SHA}],
        "model_file_inventory": [
            {
                "path": "model/weights.bin",
                "resolved_path": "/synthetic/model/weights.bin",
                "sha256": ZERO_SHA,
                "size_bytes": 1,
                "symlink": False,
            }
        ],
        "realized_stack_identity": {
            name: ZERO_SHA if name == "model_artifact_sha256" else f"synthetic-{name}"
            for name in identity_pins.STACK_IDENTITY_FIELDS
        },
        "model_runtime_config": runtime,
    }


def sample_identity_receipt(
    *,
    kind: str = "freeze_projection",
    status: str = "PASS",
    reason_codes: list[str] | None = None,
    pack_id: str = "d117_floor_qwen25_1p5b_v1",
    identity_unit_ids: tuple[str, ...] = ("synthetic/decode",),
) -> dict[str, Any]:
    return identity_pins._receipt(
        kind=kind,
        receipt_id=f"synthetic/{kind}",
        status=status,
        pack={
            "pack_id": pack_id,
            "window_id": "window-test",
            "plan_id": "plan-test",
            "reviewed_git_commit": "a" * 40,
            "projection_input_sha256": ZERO_SHA,
        },
        units=[sample_identity_unit(unit_id) for unit_id in identity_unit_ids],
        derivation={
            "contract_id": identity_pins.IDENTITY_PIN_DERIVATION_CONTRACT,
            "callables": ["synthetic_derivation"],
            "source_file_sha256": {"synthetic.py": ZERO_SHA},
            "git_commit": "a" * 40,
        },
        checks=[],
        reason_codes=reason_codes or [],
        supersedes=[],
    )


def sample_frozen_projection(
    receipt_path: str,
    receipt_sha256: str,
    identity_unit_ids: tuple[str, ...] = ("synthetic/decode",),
) -> dict[str, Any]:
    units = [sample_identity_unit(unit_id) for unit_id in identity_unit_ids]
    return {
        "work_order": identity_pins.IDENTITY_PIN_PROJECTION_WORK_ORDER,
        "mode": "derive_never_operator_enter",
        "state": "frozen",
        "required_before_arm": True,
        "derivation_contract": identity_pins.IDENTITY_PIN_DERIVATION_CONTRACT,
        "identity_units": [
            {
                key: copy.deepcopy(unit[key])
                for key in identity_pins.IDENTITY_UNIT_FIELDS
            }
            for unit in units
        ],
        "projection_receipt": {
            "path": receipt_path,
            "sha256": receipt_sha256,
        },
        "supersedes": [],
    }


class ArmReadinessSchemaTests(unittest.TestCase):
    def test_resolved_r1_registry_coordinate_allowlist_horizons_and_vocabulary(self) -> None:
        registry, raw = load_registry(ROOT)
        self.assertEqual(readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix(), "configs/arm_readiness/d117_row_registry_v2.json")
        self.assertEqual(registry["registry_id"], "d117-row-registry-v2")
        self.assertEqual(registry["schema_version"], readiness.R1_ROW_REGISTRY_SCHEMA)
        self.assertEqual(raw, render_json(registry))
        lifecycle = registry["freeze_evidence_lifecycle"]
        allowlist = lifecycle["irrelevant_path_allowlist"]
        self.assertEqual(len(allowlist), 112)
        self.assertEqual(allowlist, sorted(set(allowlist)))
        successor = "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
        # Membership is the ruled 112th entry (D-151 condition 1) and is NOT a
        # licence to subtract: the successor class is digest-conditional
        # (condition 2).  The behavioural proof that membership alone does not
        # subtract lives in
        # tests.test_receipt_histsem.SuccessorPinsetDigestConditionTests
        # (finish round, gap G-2).
        self.assertIn(successor, allowlist)
        self.assertIn(successor, readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS)
        self.assertFalse(any("d117_step6_confirmation" in path for path in allowlist))
        self.assertFalse(any("family_publication" in path for path in allowlist))
        policies = {item["kind"]: item for item in lifecycle["evidence_policies"]}
        generic = {
            "ACCEPTANCE_OWNER", "ACCEPTANCE_SUCCESSOR", "ESTIMATOR_IDENTITY",
            "MINT_TRUST", "MULTICELL_MINT", "PACK_AUTHENTICATION",
            "REASON_CODE_COVERAGE", "RECEIPT_ORACLE", "RECOVERY_LEDGER_TEST",
            "THREE_WINDOW_REGRESSION",
        }
        for kind in generic:
            self.assertEqual(policies[kind]["horizon_ns"], 604800000000000)
            self.assertEqual(policies[kind]["freshness_policy_id"], "r1.execution_bound.freeze_generic_168h.v1")
        for kind in {"DRY_RUN_REHEARSAL", "GIT_CHECKOUT", "IDENTITY_PIN_PROJECTION", "PRIVILEGE_INSTALLATION"}:
            self.assertEqual(policies[kind]["horizon_ns"], 86400000000000)
            self.assertEqual(policies[kind]["environment_comparison"], "NO_R1_AUTHORING_LANE")
        for kind in {"OFFLINE_INPUT_INVENTORY", "TERMINAL_REVIEW"}:
            self.assertEqual(policies[kind]["horizon_ns"], 21600000000000)
        vocabulary = {item["role"]: item for item in lifecycle["refusal_vocabulary"]}
        self.assertEqual(vocabulary["FAMILY_PUBLICATION"], {
            "role": "FAMILY_PUBLICATION", "code": "readiness_r1_family_publication", "type": "CUSTODY"
        })
        self.assertLessEqual(
            {item["code"] for item in vocabulary.values()},
            readiness.READINESS_REASON_CODES,
        )

    def test_registry_load_closes_conditional_code_paths_against_allowlist(self) -> None:
        registry, _raw = load_registry(ROOT)
        with mock.patch.object(
            readiness,
            "R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS",
            readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS
            | {"configs/arm_readiness/not-in-registry.json"},
        ):
            with self.assertRaises(ArmReadinessError) as caught:
                validate_registry(registry)
        self.assertEqual(
            caught.exception.reason_code, "readiness_row_registry_mismatch"
        )
        self.assertIn("absent from the registry allowlist", str(caught.exception))

    def test_archival_v1_registry_is_sha_pinned(self) -> None:
        raw = (ROOT / "configs/arm_readiness/d117_row_registry_v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5")

    def test_registry_load_closes_resolved_refusal_code_and_type(self) -> None:
        registry, _raw = load_registry(ROOT)
        missing = copy.deepcopy(registry)
        entry = missing["freeze_evidence_lifecycle"]["refusal_vocabulary"][0]
        entry["code"] = "readiness_r1_not_registered"
        with self.assertRaisesRegex(ArmReadinessError, "closed by code/type"):
            validate_registry(missing)
        mistyped = copy.deepcopy(registry)
        entry = next(item for item in mistyped["freeze_evidence_lifecycle"]["refusal_vocabulary"] if item["role"] == "FAMILY_PUBLICATION")
        entry["type"] = "POLICY"
        with self.assertRaisesRegex(ArmReadinessError, "closed by code/type"):
            validate_registry(mistyped)

    def test_r4_evidence_lifecycle_escape_sites_are_caught(self) -> None:
        registry, _raw = load_registry(ROOT)
        lifecycle = registry["freeze_evidence_lifecycle"]
        escaped = readiness.EvidenceLifecycleError(
            lifecycle, "DEPENDENCY_CHANGED_SET", "corrupt confirmation custody"
        )
        pack = {"pack_id": "synthetic", "pack_sha256": "a" * 64}
        reviewed = {"head_commit": "b" * 40}
        reference = {
            "registry_id": registry["registry_id"],
            "path": readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "sha256": "c" * 64,
            "plan_profile": "ALPHA",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "pack"
            root.mkdir()
            with (
                mock.patch.object(readiness, "_gate_receipt_histsem", return_value=None),
                mock.patch.object(readiness, "validate_arm_context", return_value={}),
                mock.patch.object(readiness, "_pack_record", return_value=pack),
                mock.patch.object(readiness, "reviewed_main", return_value=reviewed),
                mock.patch.object(readiness, "_plan_tree", return_value=({}, b"{}\n")),
                mock.patch.object(
                    readiness,
                    "_registry_reference",
                    return_value=(registry, b"{}\n", reference),
                ),
                mock.patch.object(
                    readiness, "_load_freeze_reference", side_effect=escaped
                ),
            ):
                result = readiness.generate_arm_receipt(root, {}, Path(temporary))
                self.assertEqual(
                    result["reason_codes"], [escaped.reason_code]
                )

                receipt = {
                    "pack": pack,
                    "reviewed_main": reviewed,
                    "row_registry": reference,
                }
                with self.assertRaises(ArmReadinessError) as caught:
                    readiness._derive_arm_semantics_for_verification(
                        root, Path(temporary) / "custody" / root.name, receipt
                    )
                self.assertEqual(caught.exception.reason_code, escaped.reason_code)

    maxDiff = None

    def test_r2_shared_resolver_uses_real_pack_relative_reference(self) -> None:
        gamma = (
            ROOT
            / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1"
        )
        tree, _raw = readiness._plan_tree(gamma)
        path, relative, plan_id, plan_raw = readiness.resolve_frozen_plan(
            gamma, tree
        )
        self.assertEqual(relative, "calibration_plan.json")
        self.assertEqual(path, (gamma / relative).resolve())
        self.assertEqual(plan_id, tree["plan"]["plan_id"])
        self.assertEqual(hashlib.sha256(plan_raw).hexdigest(), tree["plan"]["actual_sha256"])

    def test_r2_shared_resolver_rejects_real_doubled_pack_paths(self) -> None:
        for pack_id in (
            "d117_floor_qwen25_1p5b_v1",
            "d117_floor_qwen25_7b_v1",
        ):
            with self.subTest(pack_id=pack_id):
                pack = ROOT / "configs/campaigns" / pack_id
                tree, _raw = readiness._plan_tree(pack)
                with self.assertRaises(ArmReadinessError) as caught:
                    readiness.resolve_frozen_plan(pack, tree)
                self.assertEqual(
                    caught.exception.reason_code, "readiness_pack_unreadable"
                )

    def schema_cases(self) -> list[tuple[str, Mapping[str, Any], Callable[[object], object]]]:
        registry, _raw = load_registry(ROOT)
        return [
            ("registry", registry, validate_registry),
            ("freeze", sample_freeze(), validate_freeze_receipt),
            ("arm", sample_arm(), validate_arm_receipt),
            ("dry-run", sample_dry_run(), validate_dry_run_receipt),
            ("evidence", sample_evidence(), validate_evidence_receipt),
        ]

    def test_every_schema_exact_keys_duplicate_utf8_number_digest_and_canonical_bytes(self) -> None:
        for name, value, validator in self.schema_cases():
            with self.subTest(schema=name, case="valid"):
                self.assertEqual(validator(copy.deepcopy(value)), value)
                raw = render_json(value)
                self.assertEqual(parse_json_bytes(raw, require_canonical=True), value)
            with self.subTest(schema=name, case="unknown-key"):
                mutated = copy.deepcopy(dict(value))
                mutated["operator_verdict"] = "PASS"
                with self.assertRaisesRegex(ArmReadinessError, "exactly"):
                    validator(mutated)
            with self.subTest(schema=name, case="missing-key"):
                mutated = copy.deepcopy(dict(value))
                mutated.pop(next(iter(mutated)))
                with self.assertRaises(ArmReadinessError):
                    validator(mutated)
            with self.subTest(schema=name, case="duplicate-key"):
                raw = render_json(value)
                duplicate = raw.replace(b"{\n", b'{\n  "schema_version": "duplicate",\n', 1)
                with self.assertRaisesRegex(ArmReadinessError, "duplicate"):
                    parse_json_bytes(duplicate)
            with self.subTest(schema=name, case="invalid-utf8"):
                with self.assertRaisesRegex(ArmReadinessError, "UTF-8"):
                    parse_json_bytes(render_json(value)[:-2] + b"\xff}\n")
            with self.subTest(schema=name, case="nonfinite-number"):
                raw = render_json(value).replace(b"{\n", b'{\n  "number_probe": NaN,\n', 1)
                with self.assertRaisesRegex(ArmReadinessError, "non-finite"):
                    parse_json_bytes(raw)
            with self.subTest(schema=name, case="noncanonical"):
                compact = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
                with self.assertRaisesRegex(ArmReadinessError, "canonical"):
                    parse_json_bytes(compact, require_canonical=True)

        digest_mutations = [
            (sample_freeze(), validate_freeze_receipt, ("pack_identity", "plan_sha256")),
            (sample_arm(), validate_arm_receipt, ("pack", "pack_sha256")),
            (sample_dry_run(), validate_dry_run_receipt, ("pack", "pack_sha256")),
            (sample_evidence(), validate_evidence_receipt, (None, "pack_sha256")),
        ]
        for value, validator, (parent, field) in digest_mutations:
            target = value if parent is None else value[parent]
            target[field] = "A" * 64
            with self.assertRaisesRegex(ArmReadinessError, "lowercase SHA-256"):
                validator(value)

    def test_canonical_render_is_identical_to_d131_and_sidecar_authenticates_exact_bytes(self) -> None:
        value = sample_arm()
        raw = render_json(value)
        self.assertEqual(raw, identity_pins._render_json(value))
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(gnu_sidecar(digest, "arm-0001.json"), identity_pins._gnu_sidecar(digest, "arm-0001.json"))
        self.assertEqual(
            gnu_sidecar(digest, "arm-0001.json"),
            f"{digest}  arm-0001.json\n".encode("ascii"),
        )

    def test_every_nested_schema_rejects_unknown_and_missing_keys(self) -> None:
        evidence_item = {
            "evidence_id": "evidence-1",
            "receipt_kind": "PACK_AUTHENTICATION",
            "namespace": "PACK",
            "path": "arm_readiness.evidence/evidence-1.json",
            "sha256": ZERO_SHA,
            "schema_version": EVIDENCE_RECEIPT_SCHEMA,
            "status": "PASS",
        }
        row = {
            "row_id": "desk.current_pack",
            "evaluation_phase": "FREEZE_AND_ARM",
            "applicability": "REQUIRED",
            "verdict": "PASS",
            "predicate_id": "desk.current_pack.v1",
            "evidence_ids": ["evidence-1"],
        }
        refusal = {
            "type": "POLICY",
            "code": "readiness_dependency_refused",
            "row_id": "desk.current_pack",
            "evidence_id": None,
        }
        supersedes = {
            "receipt_id": "arm-0001",
            "receipt_path": "arm_readiness.receipts/arm-0001.json",
            "receipt_sha256": ZERO_SHA,
            "pack_id": "pack-1",
            "pack_sha256": ZERO_SHA,
        }
        direct_cases = [
            (pack_identity(), lambda value: readiness._validate_pack_identity(value, "test")),
            (pack_record(), lambda value: readiness._validate_pack(value, "test")),
            (registry_reference(), lambda value: readiness._validate_row_registry_reference(value, "test")),
            (evidence_item, lambda value: readiness._validate_evidence_item(value, "test")),
            (row, lambda value: readiness._validate_row(value, "test")),
            (refusal, lambda value: readiness._validate_refusal(value, "test")),
            (supersedes, readiness._validate_supersedes),
            (copy.deepcopy(ASSURANCE), readiness._validate_assurance),
            (arm_context(), validate_arm_context),
        ]
        for index, (value, validator) in enumerate(direct_cases):
            for mutation in ("unknown", "missing"):
                mutated = copy.deepcopy(value)
                if mutation == "unknown":
                    mutated["operator_override"] = True
                else:
                    mutated.pop(next(iter(mutated)))
                with self.subTest(case=index, mutation=mutation):
                    with self.assertRaises(ArmReadinessError):
                        validator(mutated)

        registry, _raw = load_registry(ROOT)
        dry = sample_dry_run()
        dry["checks"] = [
            {
                "check_id": "check-1",
                "status": "PASS",
                "command_sha256": ZERO_SHA,
                "stdout_sha256": ZERO_SHA,
                "stderr_sha256": ZERO_SHA,
                "exit_code": 0,
            }
        ]
        evidence = sample_evidence()
        evidence["checks"] = [{"check_id": "check-1", "status": "PASS"}]
        arm = sample_arm()
        embedded_cases = [
            (registry, ("plan_profiles", 0), validate_registry),
            (registry, ("rows", 0), validate_registry),
            (arm, ("reviewed_main",), validate_arm_receipt),
            (arm, ("freeze_receipt",), validate_arm_receipt),
            (dry, ("synthetic_context",), validate_dry_run_receipt),
            (dry, ("checks", 0), validate_dry_run_receipt),
            (evidence, ("facts", 0), validate_evidence_receipt),
            (evidence, ("checks", 0), validate_evidence_receipt),
        ]

        def nested(value: Any, path: tuple[Any, ...]) -> dict[str, Any]:
            target = value
            for component in path:
                target = target[component]
            return target

        for index, (value, path, validator) in enumerate(embedded_cases):
            for mutation in ("unknown", "missing"):
                mutated = copy.deepcopy(value)
                target = nested(mutated, path)
                if mutation == "unknown":
                    target["operator_override"] = True
                else:
                    target.pop(next(iter(target)))
                with self.subTest(embedded=index, mutation=mutation):
                    with self.assertRaises(ArmReadinessError):
                        validator(mutated)

    def test_numeric_fields_and_exponent_overflow_fail_closed(self) -> None:
        with self.assertRaisesRegex(ArmReadinessError, "non-finite"):
            parse_json_bytes(b'{"value": 1e400}\n')
        for invalid in (True, 1.5, 0, -1):
            arm = sample_arm()
            arm["valid_until_monotonic_ns"] = invalid
            with self.subTest(schema="arm", value=invalid):
                with self.assertRaises(ArmReadinessError):
                    validate_arm_receipt(arm)
            evidence = sample_evidence()
            evidence["valid_until_monotonic_ns"] = invalid
            with self.subTest(schema="evidence", value=invalid):
                with self.assertRaises(ArmReadinessError):
                    validate_evidence_receipt(evidence)

    def test_four_git_oid_fields_require_exact_lowercase_hex(self) -> None:
        cases = [
            (
                "head_commit",
                sample_evidence,
                validate_evidence_receipt,
                lambda value: value,
            ),
            (
                "head_tree_oid",
                sample_arm,
                validate_arm_receipt,
                lambda value: value["reviewed_main"],
            ),
            (
                "local_main_commit",
                sample_arm,
                validate_arm_receipt,
                lambda value: value["reviewed_main"],
            ),
            (
                "origin_main_commit",
                sample_arm,
                validate_arm_receipt,
                lambda value: value["reviewed_main"],
            ),
        ]
        for field, factory, validator, target in cases:
            value = factory()
            target(value)[field] = "A" * 40
            with self.subTest(field=field):
                with self.assertRaisesRegex(ArmReadinessError, "40 lowercase"):
                    validator(value)

    def test_boot_session_schema_amendment_is_exact_and_canonical(self) -> None:
        for name, factory, validator in (
            ("arm", sample_arm, validate_arm_receipt),
            ("evidence", sample_evidence, validate_evidence_receipt),
        ):
            for invalid in ("not-a-uuid", TEST_BOOT_SESSION_ID.upper(), ""):
                value = factory()
                value["boot_session_id"] = invalid
                with self.subTest(schema=name, value=invalid):
                    with self.assertRaisesRegex(ArmReadinessError, "canonical UUID"):
                        validator(value)
            missing = factory()
            del missing["boot_session_id"]
            with self.subTest(schema=name, value="missing"):
                with self.assertRaises(ArmReadinessError):
                    validator(missing)

    def _generic_predicate_receipt(
        self, row: Mapping[str, Any], *, source_kind: str | None = None
    ) -> dict[str, Any]:
        receipt = sample_evidence()
        evidence_kind = row["required_evidence_kinds"][0]
        receipt["kind"] = evidence_kind
        receipt["facts"] = [
            {
                "fact_id": row["predicate_id"],
                "value_type": "OBJECT",
                "value": predicate_content(row["predicate_id"]),
                "source_kind": source_kind or predicate_source_kind(evidence_kind),
                "source_path": "source.json",
                "source_sha256": ZERO_SHA,
            }
        ]
        validate_evidence_receipt(receipt)
        return receipt

    def test_all_35_contract_predicates_require_named_content_and_admissible_sources(self) -> None:
        registry, _raw = load_registry(ROOT)
        self.assertEqual(
            set(readiness._PREDICATE_CONTENT_REQUIREMENTS),
            {row["predicate_id"] for row in registry["rows"]},
        )
        self.assertEqual(
            set(readiness._EVIDENCE_SOURCE_KINDS),
            {
                kind
                for row in registry["rows"]
                for kind in row["required_evidence_kinds"]
            },
        )
        for row in registry["rows"]:
            predicate_id = row["predicate_id"]
            kind = row["required_evidence_kinds"][0]
            if kind == "IDENTITY_PIN_PROJECTION":
                receipt = readiness._identity_projection_pseudo_receipt(
                    status="PASS", reason_codes=[]
                )
            elif kind == "DRY_RUN_REHEARSAL":
                dry_run = sample_dry_run()
                dry_run["checks"] = [
                    readiness._dry_run_check(check_id, [check_id], 0, "", "")
                    for check_id in readiness._PREDICATE_CONTENT_REQUIREMENTS[
                        predicate_id
                    ]
                ]
                receipt = readiness._dry_run_semantic_receipt(dry_run)
            else:
                receipt = self._generic_predicate_receipt(row)
            with self.subTest(row=row["row_id"], case="genuine"):
                self.assertTrue(
                    readiness._predicate_passes(
                        receipt, predicate_id, expected_plan_sha256=ZERO_SHA
                    )
                )

            missing_content = copy.deepcopy(receipt)
            missing_fact = next(
                item
                for item in missing_content["facts"]
                if item["fact_id"] == predicate_id
            )
            missing_fact["value"].pop(
                next(iter(readiness._PREDICATE_CONTENT_REQUIREMENTS[predicate_id]))
            )
            with self.subTest(row=row["row_id"], case="missing-content"):
                self.assertFalse(
                    readiness._predicate_passes(
                        missing_content, predicate_id, expected_plan_sha256=ZERO_SHA
                    )
                )

            mutated = copy.deepcopy(receipt)
            fact = next(
                item for item in mutated["facts"] if item["fact_id"] == predicate_id
            )
            fact["value_type"] = "BOOLEAN"
            fact["value"] = True
            with self.subTest(row=row["row_id"], case="bare-boolean"):
                self.assertFalse(
                    readiness._predicate_passes(
                        mutated, predicate_id, expected_plan_sha256=ZERO_SHA
                    )
                )

            if kind not in {"IDENTITY_PIN_PROJECTION", "DRY_RUN_REHEARSAL"}:
                operator = self._generic_predicate_receipt(
                    row, source_kind="OPERATOR_ATTESTATION"
                )
                with self.subTest(row=row["row_id"], case="operator-source"):
                    self.assertEqual(
                        readiness._predicate_passes(
                            operator, predicate_id, expected_plan_sha256=ZERO_SHA
                        ),
                        row["row_id"]
                        in {
                            "clock.correct_and_prior_state",
                            "t0.background_quiet",
                        },
                    )

    def test_ledger_reservation_requires_binding_not_wellformedness(self) -> None:
        """D-134 delta re-audit F1: the receipt must BIND this pack's plan SHA.

        A well-formed digest is not a bound digest: a reservation receipt
        issued against a DIFFERENT plan must refuse.
        """

        registry, _raw = load_registry(ROOT)
        row = next(
            row for row in registry["rows"] if row["row_id"] == "t0.ledger_reservation"
        )
        bound = "a" * 64
        other = "b" * 64
        evidence = sample_evidence()
        evidence["kind"] = "LEDGER_RESERVATION"
        evidence["facts"][0].update(
            {
                "fact_id": "t0.ledger_reservation.v1",
                "source_kind": "PROBE",
                "value_type": "OBJECT",
                "value": {
                    "diagnostic_status": "PASS",
                    "events": ["calibration_pre_reserve_authorized"],
                    "execute_mode": True,
                    "plan_sha256": other,
                    "status": "reserved",
                },
            }
        )
        validated = validate_evidence_receipt(evidence)

        # Cross-plan reservation refuses even though every field is well formed.
        self.assertFalse(
            readiness._predicate_passes(
                validated, "t0.ledger_reservation.v1", expected_plan_sha256=bound
            )
        )
        # An unknown expected value fails closed rather than accepting any SHA.
        self.assertFalse(
            readiness._predicate_passes(
                validated, "t0.ledger_reservation.v1", expected_plan_sha256=None
            )
        )
        rows, _refusals = readiness._evaluate_rows(
            [row],
            {validated["evidence_id"]: validated},
            clock_route="MANUAL",
            successor_acceptance=False,
            expected_plan_sha256=bound,
        )
        self.assertEqual(rows[0]["verdict"], "REFUSE")

        # The correctly bound receipt still passes.
        evidence["facts"][0]["value"]["plan_sha256"] = bound
        rebound = validate_evidence_receipt(evidence)
        self.assertTrue(
            readiness._predicate_passes(
                rebound, "t0.ledger_reservation.v1", expected_plan_sha256=bound
            )
        )

    def test_single_launch_capability_refuses_frozen_bytes_asserting_live_facts(
        self,
    ) -> None:
        """D-134 delta re-audit F2: PACK bytes cannot establish live T-0 facts.

        "IDs unused" and "capability available" are conditions of the world at
        T-0; only "the launch command is frozen" is a property of committed
        bytes.  PACK-sourced evidence therefore cannot satisfy this row.
        """

        registry, _raw = load_registry(ROOT)
        row = next(
            row
            for row in registry["rows"]
            if row["row_id"] == "t0.single_launch_capability"
        )
        value = {
            "atomic_single_use_capability_available": True,
            "attempt_ids_unused": True,
            "exact_launch_command_frozen": True,
            "session_id_unused": True,
        }
        evidence = sample_evidence()
        evidence["kind"] = "LAUNCH_RECIPE"
        evidence["facts"][0].update(
            {
                "fact_id": "t0.single_launch_capability.v1",
                "source_kind": "PACK",
                "value_type": "OBJECT",
                "value": value,
            }
        )
        pack_sourced = validate_evidence_receipt(evidence)
        self.assertFalse(
            readiness._predicate_passes(
                pack_sourced, "t0.single_launch_capability.v1"
            )
        )
        rows, _refusals = readiness._evaluate_rows(
            [row],
            {pack_sourced["evidence_id"]: pack_sourced},
            clock_route="MANUAL",
            successor_acceptance=False,
        )
        self.assertEqual(rows[0]["verdict"], "REFUSE")

        # A live probe of the same claims still passes.
        evidence["facts"][0]["source_kind"] = "PROBE"
        probe_sourced = validate_evidence_receipt(evidence)
        self.assertTrue(
            readiness._predicate_passes(
                probe_sourced, "t0.single_launch_capability.v1"
            )
        )

    def test_ledger_boolean_forgery_refuses_with_closed_code(self) -> None:
        registry, _raw = load_registry(ROOT)
        row = next(
            row
            for row in registry["rows"]
            if row["row_id"] == "t0.ledger_reservation"
        )
        evidence = sample_evidence()
        evidence["kind"] = "LEDGER_RESERVATION"
        evidence["facts"][0].update(
            {
                "fact_id": "t0.ledger_reservation.v1",
                "source_kind": "OPERATOR_ATTESTATION",
                "value_type": "BOOLEAN",
                "value": True,
            }
        )
        validated = validate_evidence_receipt(evidence)
        self.assertFalse(
            readiness._predicate_passes(validated, "t0.ledger_reservation.v1")
        )
        rows, refusals = readiness._evaluate_rows(
            [row],
            {validated["evidence_id"]: validated},
            clock_route="MANUAL",
            successor_acceptance=False,
        )
        self.assertEqual(rows[0]["verdict"], "REFUSE")
        self.assertEqual(
            [refusal["code"] for refusal in refusals],
            ["readiness_ledger_preflight_refused"],
        )
        check_forgery = copy.deepcopy(validated)
        check_forgery["facts"] = []
        check_forgery["checks"] = [
            {"check_id": "t0.ledger_reservation.v1", "status": "PASS"}
        ]
        self.assertFalse(
            readiness._predicate_passes(
                check_forgery, "t0.ledger_reservation.v1"
            )
        )

    def test_contract_manual_observations_still_accept_operator_attestation(self) -> None:
        registry, _raw = load_registry(ROOT)
        rows = {row["row_id"]: row for row in registry["rows"]}
        for row_id in (
            "clock.correct_and_prior_state",
            "t0.background_quiet",
        ):
            receipt = self._generic_predicate_receipt(
                rows[row_id], source_kind="OPERATOR_ATTESTATION"
            )
            with self.subTest(row=row_id):
                self.assertTrue(
                    readiness._predicate_passes(receipt, rows[row_id]["predicate_id"])
                )

    def test_freeze_v2_exact_keys_reject_supersession_and_bad_predecessors(
        self,
    ) -> None:
        """R-11: v2 carries `predecessor`, never `supersedes`, exact-key."""

        receipt = sample_freeze_v2()
        validate_freeze_receipt(receipt)
        self.assertEqual(
            set(receipt),
            (set(readiness.FREEZE_RECEIPT_KEYS) - {"supersedes"}) | {"predecessor"},
        )
        illegal = copy.deepcopy(receipt)
        illegal["supersedes"] = None
        with self.assertRaises(ArmReadinessError) as caught:
            validate_freeze_receipt(illegal)
        self.assertEqual(caught.exception.reason_code, "readiness_unknown_key")

        for key in sorted(readiness.FREEZE_PREDECESSOR_KEYS):
            with self.subTest(missing=key):
                missing = copy.deepcopy(receipt)
                del missing["predecessor"][key]
                with self.assertRaises(ArmReadinessError):
                    validate_freeze_receipt(missing)
        unknown = copy.deepcopy(receipt)
        unknown["predecessor"]["lineage_id"] = "family-2"
        with self.assertRaises(ArmReadinessError) as caught:
            validate_freeze_receipt(unknown)
        self.assertEqual(caught.exception.reason_code, "readiness_unknown_key")

        for name, mutation in (
            ("absolute pack_path", {"pack_path": "/tmp/pack"}),
            ("pack_path/pack_id disagreement", {"pack_path": "configs/campaigns/other"}),
            ("foreign digest algorithm", {"pack_digest_algorithm": "sha256"}),
            ("uppercase digest", {"pack_sha256": "A" * 64}),
        ):
            with self.subTest(mutation=name):
                mutated = copy.deepcopy(receipt)
                mutated["predecessor"].update(mutation)
                with self.assertRaises(ArmReadinessError):
                    validate_freeze_receipt(mutated)

        misnamed = copy.deepcopy(receipt)
        misnamed["predecessor"]["freeze_receipt"]["path"] = (
            "arm_readiness.freeze.receipts/freeze-0002.json"
        )
        with self.assertRaises(ArmReadinessError):
            validate_freeze_receipt(misnamed)

    def test_freeze_v2_receipt_id_must_be_the_predecessor_ordinal_plus_one(
        self,
    ) -> None:
        """R-6: freeze-0001 may only be followed by freeze-0002."""

        for receipt_id in ("freeze-0001", "freeze-0003", "freeze-0010"):
            with self.subTest(receipt_id=receipt_id):
                receipt = sample_freeze_v2()
                receipt["receipt_id"] = receipt_id
                with self.assertRaises(ArmReadinessError) as caught:
                    validate_freeze_receipt(receipt)
                self.assertEqual(
                    caught.exception.reason_code, "readiness_schema_invalid"
                )
        succeeding = sample_freeze_v2()
        succeeding["receipt_id"] = "freeze-0003"
        succeeding["predecessor"]["freeze_receipt"] = {
            "receipt_id": "freeze-0002",
            "path": "arm_readiness.freeze.receipts/freeze-0002.json",
            "sha256": ZERO_SHA,
        }
        validate_freeze_receipt(succeeding)

    def test_freeze_v1_remains_its_own_exact_key_vocabulary(self) -> None:
        """R-9/R-11: v1 receipts keep validating and cannot carry a predecessor."""

        receipt = sample_freeze()
        self.assertEqual(receipt["schema_version"], FREEZE_RECEIPT_SCHEMA)
        validate_freeze_receipt(receipt)
        intruder = sample_freeze()
        intruder["predecessor"] = sample_freeze_predecessor()
        with self.assertRaises(ArmReadinessError) as caught:
            validate_freeze_receipt(intruder)
        self.assertEqual(caught.exception.reason_code, "readiness_unknown_key")
        unknown_schema = sample_freeze()
        unknown_schema["schema_version"] = "joulewise.arm_readiness_freeze_receipt.v3"
        with self.assertRaisesRegex(ArmReadinessError, "schema is invalid"):
            validate_freeze_receipt(unknown_schema)

    def test_successor_chain_refusal_is_governed_and_typed(self) -> None:
        self.assertIn(
            "readiness_successor_chain_invalid", READINESS_REASON_CODES
        )
        self.assertEqual(
            readiness.REASON_TYPE_BY_CODE["readiness_successor_chain_invalid"],
            "SUCCESSOR_CHAIN",
        )
        self.assertEqual(
            readiness.SUCCESSOR_CHAIN_REASON_CODES,
            frozenset({"readiness_successor_chain_invalid"}),
        )

    def test_assurance_and_closed_refusals_are_literal(self) -> None:
        self.assertEqual(
            ASSURANCE,
            {
                "model": "single_authority_hash_bound_replay.v1",
                "independent_attestation": False,
            },
        )
        self.assertEqual(len(READINESS_REASON_CODES), 55)
        self.assertNotIn("GO", READINESS_REASON_CODES)
        self.assertNotIn("UNKNOWN", READINESS_REASON_CODES)
        upstream_refusal = sample_evidence()
        upstream_refusal["status"] = "REFUSE"
        upstream_refusal["reason_codes"] = ["clock_probe_failed"]
        validate_evidence_receipt(upstream_refusal)
        self.assertNotIn("clock_probe_failed", READINESS_REASON_CODES)


if __name__ == "__main__":
    unittest.main()
