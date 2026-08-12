from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Mapping

import joulewise.arm_readiness as readiness
from joulewise import identity_pins
from joulewise.arm_readiness import (
    ARM_RECEIPT_SCHEMA,
    ASSURANCE,
    DRY_RUN_RECEIPT_SCHEMA,
    EVIDENCE_RECEIPT_SCHEMA,
    FREEZE_RECEIPT_SCHEMA,
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


def sample_arm(root: Path | str = "/tmp/readiness") -> dict[str, Any]:
    return {
        "schema_version": ARM_RECEIPT_SCHEMA,
        "receipt_kind": "arm",
        "receipt_id": "arm-0001",
        "mode": "arm",
        "status": "PASS",
        "arm_disposition": "GO",
        "issued_at_utc": "2026-08-11T00:00:00Z",
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
        "valid_until_monotonic_ns": 10**30,
        "pack_sha256": ZERO_SHA,
        "head_commit": "a" * 40,
        "facts": [
            {
                "fact_id": "desk.current_pack.v1",
                "value_type": "BOOLEAN",
                "value": True,
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
    maxDiff = None

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

    def test_assurance_and_closed_refusals_are_literal(self) -> None:
        self.assertEqual(
            ASSURANCE,
            {
                "model": "single_authority_hash_bound_replay.v1",
                "independent_attestation": False,
            },
        )
        self.assertEqual(len(READINESS_REASON_CODES), 46)
        self.assertNotIn("GO", READINESS_REASON_CODES)
        self.assertNotIn("UNKNOWN", READINESS_REASON_CODES)
        upstream_refusal = sample_evidence()
        upstream_refusal["status"] = "REFUSE"
        upstream_refusal["reason_codes"] = ["clock_probe_failed"]
        validate_evidence_receipt(upstream_refusal)
        self.assertNotIn("clock_probe_failed", READINESS_REASON_CODES)


if __name__ == "__main__":
    unittest.main()
