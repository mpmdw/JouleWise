from __future__ import annotations

import copy
import hashlib
import inspect
import json
import math
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
# T-0 liveness bound (cold gate T26 item 3): the sample clock probe finishes
# R1 at 2_000_000_000 ns, so the sample EVIDENCE horizon of R1 + 6 h + 1 s sits
# inside the ruled 600 s window (`_MIN_IDLE_NS`); the previous 10**30 horizon
# was rejected by the liveness predicate. The sample ARM keeps 10**30 because
# `sample_arm` carries no clock PROBE fact (empty evidence/rows), so the
# liveness conjunct in `_clock_probe_predicate_passes` never runs against it.
SAMPLE_VALID_UNTIL_NS = 2_000_000_000 + 21_600_000_000_000 + 1_000_000_000


def probe_clock_value() -> dict[str, Any]:
    r0_raw = 1_000_000_000
    anchor_raw = r0_raw + 600_000_000_000
    realtime_offset = 2_000_000_000_000_000_000
    r1_started = anchor_raw - 1_000
    return {
        "independent_clock_attestation": True,
        "reference_quorum_satisfied": True,
        "absolute_offset_within_ceiling": True,
        "unstepped_across_t0_sequence": True,
        "sample_policy_id": readiness._clock_reference.SAMPLE_POLICY_ID,
        "reference_server_count": 3,
        "reference_bound_seconds": 0.03,
        "comparison_delta_seconds": 0.01,
        "r0_anchor_realtime_ns": realtime_offset + r0_raw,
        "r0_anchor_monotonic_raw_ns": r0_raw,
        "r0_anchor_read_skew_ns": 1_000,
        "anchor_realtime_ns": realtime_offset + anchor_raw,
        "anchor_monotonic_raw_ns": anchor_raw,
        "anchor_read_skew_ns": 1_000,
        "anchor_delta_ns": 0,
        "t0_span_ns": 600_000_000_000,
        "r1_batch_started_monotonic_raw_ns": r1_started,
        "r1_batch_finished_monotonic_raw_ns": anchor_raw,
        "r1_batch_duration_ns": anchor_raw - r1_started,
        "r1_batch_finished_monotonic_ns": 2_000_000_000,
    }


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
    elif predicate_id == "clock.correct_and_prior_state.v1":
        content.update(probe_clock_value())
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
        "valid_until_monotonic_ns": SAMPLE_VALID_UNTIL_NS,
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
    reviewed_git_commit: str = "a" * 40,
) -> dict[str, Any]:
    return identity_pins._receipt(
        kind=kind,
        receipt_id=f"synthetic/{kind}",
        status=status,
        pack={
            "pack_id": pack_id,
            "window_id": "window-test",
            "plan_id": "plan-test",
            "reviewed_git_commit": reviewed_git_commit,
            "projection_input_sha256": ZERO_SHA,
        },
        units=[sample_identity_unit(unit_id) for unit_id in identity_unit_ids],
        derivation={
            "contract_id": identity_pins.IDENTITY_PIN_DERIVATION_CONTRACT,
            "callables": ["synthetic_derivation"],
            "source_file_sha256": {"synthetic.py": ZERO_SHA},
            "git_commit": reviewed_git_commit,
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



def sample_unprojected_projection(
    identity_unit_ids: tuple[str, ...] = ("synthetic/decode",),
) -> dict[str, Any]:
    """The projection block a pack carries BEFORE `freeze_projection` runs.

    `identity_pins` (:522) requires every `model_runtime_config` value to be
    None until a pack is frozen: the runtime triple is what the projection
    derives, so a pack that already carried it would be claiming a derivation
    it never ran.
    """

    projection = sample_frozen_projection(
        "identity_pin_projection.receipts/projection-0001.json",
        ZERO_SHA,
        identity_unit_ids,
    )
    projection["state"] = "unprojected"
    projection["projection_receipt"] = None
    for unit in projection["identity_units"]:
        unit["model_runtime_config"] = {
            name: None for name in unit["model_runtime_config"]
        }
    return projection


def apply_freeze_projection(
    pack_root: Path,
    receipt: Mapping[str, Any],
    receipt_relative: str,
    receipt_sha256: str,
) -> None:
    """Rewrite an unprojected committed pack exactly as `freeze_projection` does.

    This deliberately mirrors `identity_pins.freeze_projection` (:1826) rather
    than calling the evidence author's replay: a fixture built BY the code under
    test could only ever agree with it.  The real `freeze_projection` cannot be
    used here because it derives identity units through the mlx runtime adapters
    and mints its git anchor under a clean-tree gate.  Fidelity to the real
    write set is proven separately, against the live `_v5` packs.
    """

    tree, projection, producer = identity_pins._load_pack_projection(pack_root)
    frozen = copy.deepcopy(projection)
    frozen["state"] = "frozen"
    frozen["projection_receipt"] = {
        "path": receipt_relative,
        "sha256": receipt_sha256,
    }
    runtime_by_id = {
        unit["identity_unit_id"]: unit["model_runtime_config"]
        for unit in receipt["identity_units"]
    }
    for unit in frozen["identity_units"]:
        unit["model_runtime_config"] = copy.deepcopy(
            runtime_by_id[unit["identity_unit_id"]]
        )
    tree["arm_attachments"]["identity_pin_projection"] = copy.deepcopy(frozen)
    if producer is not None:
        producer["identity_pin_projection"] = copy.deepcopy(frozen)
        producer_bytes = identity_pins._render_json(producer)
        (pack_root / "producer_contract.json").write_bytes(producer_bytes)
        downstream = tree.get("downstream_contract")
        reference = (
            downstream.get("producer_contract")
            if isinstance(downstream, Mapping)
            else None
        )
        if isinstance(reference, dict):
            reference["sha256"] = identity_pins._sha256_bytes(producer_bytes)
    tree_bytes = identity_pins._render_json(tree)
    (pack_root / "plan_tree.json").write_bytes(tree_bytes)
    (pack_root / "plan_tree.sha256").write_bytes(
        identity_pins._gnu_sidecar(
            identity_pins._sha256_bytes(tree_bytes), "plan_tree.json"
        )
    )


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
        successor = "configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json"
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
        self.assertEqual(
            vocabulary["MEASUREMENT_CHECKOUT"],
            {
                "role": "MEASUREMENT_CHECKOUT",
                "code": "readiness_r1_measurement_checkout",
                "type": "CUSTODY",
            },
        )
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

    def test_registry_load_closure_requires_measurement_checkout_role_and_code(
        self,
    ) -> None:
        registry, _raw = load_registry(ROOT)
        cases: list[tuple[str, dict[str, Any], str]] = []

        unregistered = copy.deepcopy(registry)
        entry = next(
            item
            for item in unregistered["freeze_evidence_lifecycle"][
                "refusal_vocabulary"
            ]
            if item["role"] == "MEASUREMENT_CHECKOUT"
        )
        entry["code"] = "readiness_r1_not_registered"
        cases.append(
            (
                "code absent from READINESS_REASON_CODES",
                unregistered,
                "closed by code/type",
            )
        )

        missing_role = copy.deepcopy(registry)
        vocabulary = missing_role["freeze_evidence_lifecycle"][
            "refusal_vocabulary"
        ]
        vocabulary[:] = [
            item for item in vocabulary if item["role"] != "MEASUREMENT_CHECKOUT"
        ]
        cases.append(
            (
                "vocabulary role absent",
                missing_role,
                "register every role exactly once",
            )
        )

        for label, mutated, detail in cases:
            with self.subTest(direction=label):
                with tempfile.TemporaryDirectory() as temporary:
                    repository = Path(temporary)
                    target = repository / readiness.ROW_REGISTRY_RELATIVE_PATH
                    target.parent.mkdir(parents=True)
                    target.write_bytes(render_json(mutated))
                    with self.assertRaisesRegex(ArmReadinessError, detail):
                        load_registry(repository)

    def test_r4_evidence_lifecycle_escape_sites_are_caught(self) -> None:
        registry, _raw = load_registry(ROOT)
        lifecycle = registry["freeze_evidence_lifecycle"]
        escaped = readiness.EvidenceLifecycleError(
            lifecycle, "DEPENDENCY_CHANGED_SET", "corrupt confirmation custody"
        )
        # A schema-shaped pack record: `_validate_pack` enforces exactly
        # `PACK_KEYS` on every receipt read, so both sides of the D-154
        # field-wise comparison always carry `pack_root` in production.  The
        # earlier two-key stub no longer modelled that record and made the
        # comparison report a content difference before the escape site could
        # be reached.
        pack = {
            "pack_id": "synthetic",
            "plan_id": "synthetic-plan",
            "window_id": "synthetic-window",
            "pack_root": "/synthetic/repository/configs/campaigns/synthetic",
            "pack_digest_algorithm": readiness.PACK_DIGEST_ALGORITHM,
            "pack_sha256": "a" * 64,
            "plan_tree_path": "plan_tree.json",
            "plan_tree_sha256": "d" * 64,
            "plan_tree_sidecar_path": "plan_tree.sha256",
            "plan_tree_sidecar_sha256": "e" * 64,
        }
        self.assertEqual(set(pack), readiness.PACK_KEYS)
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
        selected_source = source_kind or predicate_source_kind(evidence_kind)
        value = predicate_content(row["predicate_id"])
        if (
            row["predicate_id"] == "clock.correct_and_prior_state.v1"
            and selected_source == "OPERATOR_ATTESTATION"
        ):
            value = {
                "independent_clock_attestation": True,
                "prior_systemsetup_state_captured": True,
            }
        receipt["facts"] = [
            {
                "fact_id": row["predicate_id"],
                "value_type": "OBJECT",
                "value": value,
                "source_kind": selected_source,
                "source_path": "source.json",
                "source_sha256": ZERO_SHA,
            }
        ]
        validate_evidence_receipt(receipt)
        return receipt

    def _clock_predicate_receipt(
        self,
        *,
        source_kind: str = "PROBE",
        value: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        registry, _raw = load_registry(ROOT)
        row = next(
            item
            for item in registry["rows"]
            if item["predicate_id"] == "clock.correct_and_prior_state.v1"
        )
        receipt = self._generic_predicate_receipt(row, source_kind=source_kind)
        if value is not None:
            receipt["facts"][0]["value"] = copy.deepcopy(dict(value))
        if source_kind == "PROBE":
            finished = receipt["facts"][0]["value"][
                "r1_batch_finished_monotonic_ns"
            ]
            receipt["valid_until_monotonic_ns"] = (
                finished + 21_600_000_000_000
            )
        return receipt

    def _probe_passes(
        self,
        receipt: Mapping[str, Any],
        *,
        live_clock_anchor: Mapping[str, Any] | object | None = (
            readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE
        ),
    ) -> bool:
        return readiness._predicate_passes(
            receipt,
            "clock.correct_and_prior_state.v1",
            live_clock_anchor=live_clock_anchor,
        )

    @staticmethod
    def _set_span(value: dict[str, Any], span: int) -> None:
        raw = value["r0_anchor_monotonic_raw_ns"] + span
        offset = (
            value["r0_anchor_realtime_ns"]
            - value["r0_anchor_monotonic_raw_ns"]
        )
        value["anchor_monotonic_raw_ns"] = raw
        value["anchor_realtime_ns"] = offset + raw
        value["t0_span_ns"] = span
        value["anchor_delta_ns"] = 0

    def test_clock_probe_omitted_live_anchor_defaults_to_static_replay(self) -> None:
        receipt = self._clock_predicate_receipt()
        self.assertTrue(
            readiness._predicate_passes(
                receipt,
                "clock.correct_and_prior_state.v1",
            )
        )

    def test_evaluate_rows_omitted_live_anchor_defaults_to_static_replay(self) -> None:
        receipt = self._clock_predicate_receipt()
        registry, _raw = load_registry(ROOT)
        definition = next(
            item
            for item in registry["rows"]
            if item["predicate_id"] == "clock.correct_and_prior_state.v1"
        )
        rows, refusals = readiness._evaluate_rows(
            [definition],
            {receipt["evidence_id"]: receipt},
            clock_route="MANUAL",
            successor_acceptance=False,
        )
        self.assertEqual(rows[0]["verdict"], "PASS")
        self.assertEqual(refusals, [])

    def test_evaluate_rows_threads_an_explicit_live_anchor_value(self) -> None:
        receipt = self._clock_predicate_receipt()
        registry, _raw = load_registry(ROOT)
        definition = next(
            item
            for item in registry["rows"]
            if item["predicate_id"] == "clock.correct_and_prior_state.v1"
        )
        observed: list[object] = []

        def predicate(_receipt, _predicate_id, **kwargs):
            observed.append(kwargs.get("live_clock_anchor", mock.sentinel.omitted))
            return True

        with mock.patch.object(
            readiness,
            "_predicate_passes",
            side_effect=predicate,
        ):
            readiness._evaluate_rows(
                [definition],
                {receipt["evidence_id"]: receipt},
                clock_route="MANUAL",
                successor_acceptance=False,
                live_clock_anchor=None,
            )
        self.assertEqual(observed, [None])

    def test_clock_source_branches_preserve_attended_and_close_probe_hole(self) -> None:
        attended = self._clock_predicate_receipt(source_kind="OPERATOR_ATTESTATION")
        self.assertTrue(
            readiness._predicate_passes(
                attended, "clock.correct_and_prior_state.v1"
            )
        )
        del attended["facts"][0]["value"]["prior_systemsetup_state_captured"]
        self.assertFalse(
            readiness._predicate_passes(
                attended, "clock.correct_and_prior_state.v1"
            )
        )
        minimal_probe = self._clock_predicate_receipt()
        minimal_probe["facts"][0]["value"] = {
            "independent_clock_attestation": True
        }
        self.assertFalse(self._probe_passes(minimal_probe))

    def test_clock_probe_gate_booleans_and_reference_bound_are_recomputed(self) -> None:
        receipt = self._clock_predicate_receipt()
        self.assertTrue(self._probe_passes(receipt))
        for gate in (
            "independent_clock_attestation",
            "reference_quorum_satisfied",
            "absolute_offset_within_ceiling",
            "unstepped_across_t0_sequence",
        ):
            mutated = copy.deepcopy(receipt)
            mutated["facts"][0]["value"][gate] = False
            with self.subTest(gate=gate):
                self.assertFalse(self._probe_passes(mutated))
        wrong_policy = copy.deepcopy(receipt)
        wrong_policy["facts"][0]["value"]["sample_policy_id"] = "substitute.v1"
        self.assertFalse(self._probe_passes(wrong_policy))
        extra = copy.deepcopy(receipt)
        extra["facts"][0]["value"]["unruled"] = 1
        self.assertFalse(self._probe_passes(extra))
        for bound, expected in (
            (0.5, True),
            (math.nextafter(0.5, 0.0), True),
            (math.nextafter(0.5, math.inf), False),
        ):
            mutated = copy.deepcopy(receipt)
            mutated["facts"][0]["value"]["reference_bound_seconds"] = bound
            with self.subTest(bound=bound):
                self.assertEqual(self._probe_passes(mutated), expected)

    def test_clock_probe_span_boundaries_and_exact_difference_gate(self) -> None:
        receipt = self._clock_predicate_receipt()
        for span, expected in (
            (599_999_999_999, False),
            (600_000_000_000, True),
            (600_000_000_001, True),
            (3_599_999_999_999, True),
            (3_600_000_000_000, True),
            (3_600_000_000_001, False),
        ):
            mutated = copy.deepcopy(receipt)
            self._set_span(mutated["facts"][0]["value"], span)
            with self.subTest(span=span):
                self.assertEqual(self._probe_passes(mutated), expected)
        mismatch = copy.deepcopy(receipt)
        mismatch["facts"][0]["value"]["t0_span_ns"] += 1
        self.assertFalse(self._probe_passes(mismatch))

    def test_clock_probe_anchor_delta_and_skew_boundaries_gate(self) -> None:
        receipt = self._clock_predicate_receipt()
        for delta, expected in (
            (4_999_999, True),
            (5_000_000, True),
            (5_000_001, False),
        ):
            mutated = copy.deepcopy(receipt)
            value = mutated["facts"][0]["value"]
            value["anchor_realtime_ns"] += delta
            value["anchor_delta_ns"] = delta
            with self.subTest(delta=delta):
                self.assertEqual(self._probe_passes(mutated), expected)
        mismatch = copy.deepcopy(receipt)
        mismatch["facts"][0]["value"]["anchor_delta_ns"] = 1
        self.assertFalse(self._probe_passes(mismatch))
        for name in ("r0_anchor_read_skew_ns", "anchor_read_skew_ns"):
            for skew, expected in ((-1, False), (0, True), (999_999, True), (1_000_000, True), (1_000_001, False)):
                mutated = copy.deepcopy(receipt)
                mutated["facts"][0]["value"][name] = skew
                with self.subTest(name=name, skew=skew):
                    self.assertEqual(self._probe_passes(mutated), expected)

    def test_clock_probe_r1_duration_quorum_and_horizon_boundaries_gate(self) -> None:
        receipt = self._clock_predicate_receipt()
        for duration, expected in (
            (-1, False),
            (0, True),
            (1, True),
            (29_999_999_999, True),
            (30_000_000_000, True),
            (30_000_000_001, False),
        ):
            mutated = copy.deepcopy(receipt)
            value = mutated["facts"][0]["value"]
            value["r1_batch_started_monotonic_raw_ns"] = (
                value["r1_batch_finished_monotonic_raw_ns"] - duration
            )
            value["r1_batch_duration_ns"] = duration
            with self.subTest(duration=duration):
                self.assertEqual(self._probe_passes(mutated), expected)
        for count, expected in ((1, False), (2, True), (3, True)):
            mutated = copy.deepcopy(receipt)
            mutated["facts"][0]["value"]["reference_server_count"] = count
            with self.subTest(count=count):
                self.assertEqual(self._probe_passes(mutated), expected)
        finished = receipt["facts"][0]["value"]["r1_batch_finished_monotonic_ns"]
        for delta, expected in (
            (21_599_999_999_999, False),
            (21_600_000_000_000, True),
            (21_600_000_000_001, True),
        ):
            mutated = copy.deepcopy(receipt)
            mutated["valid_until_monotonic_ns"] = finished + delta
            with self.subTest(horizon_delta=delta):
                self.assertEqual(self._probe_passes(mutated), expected)

    def test_clock_probe_rejects_every_non_integer_and_ordered_endpoint_reversal(self) -> None:
        expected_integer_fields = (
            "reference_server_count",
            "r0_anchor_realtime_ns",
            "r0_anchor_monotonic_raw_ns",
            "r0_anchor_read_skew_ns",
            "anchor_realtime_ns",
            "anchor_monotonic_raw_ns",
            "anchor_read_skew_ns",
            "anchor_delta_ns",
            "t0_span_ns",
            "r1_batch_started_monotonic_raw_ns",
            "r1_batch_finished_monotonic_raw_ns",
            "r1_batch_duration_ns",
            "r1_batch_finished_monotonic_ns",
        )
        self.assertEqual(
            readiness._CLOCK_PROBE_INTEGER_FIELDS,
            expected_integer_fields,
        )
        receipt = self._clock_predicate_receipt()
        for name in (*expected_integer_fields, "valid_until_monotonic_ns"):
            for bad in (True, 1.0, "1"):
                mutated = copy.deepcopy(receipt)
                if name == "valid_until_monotonic_ns":
                    mutated[name] = bad
                else:
                    mutated["facts"][0]["value"][name] = bad
                with self.subTest(field=name, value=bad):
                    self.assertFalse(self._probe_passes(mutated))

        def reverse_t0_span(mutated: dict[str, Any]) -> None:
            value = mutated["facts"][0]["value"]
            value["anchor_monotonic_raw_ns"] = (
                value["r0_anchor_monotonic_raw_ns"] - 1
            )
            value["anchor_realtime_ns"] = value["r0_anchor_realtime_ns"] - 1
            value["t0_span_ns"] = -1
            value["anchor_delta_ns"] = 0

        def reverse_r1_batch(mutated: dict[str, Any]) -> None:
            value = mutated["facts"][0]["value"]
            value["r1_batch_started_monotonic_raw_ns"] = (
                value["r1_batch_finished_monotonic_raw_ns"] + 1
            )
            value["r1_batch_duration_ns"] = -1

        def reverse_validity_horizon(mutated: dict[str, Any]) -> None:
            value = mutated["facts"][0]["value"]
            mutated["valid_until_monotonic_ns"] = (
                value["r1_batch_finished_monotonic_ns"] - 1
            )

        for relation, mutate in (
            ("r0_before_author", reverse_t0_span),
            ("r1_start_before_finish", reverse_r1_batch),
            ("r1_finish_before_valid_until", reverse_validity_horizon),
        ):
            mutated = copy.deepcopy(receipt)
            mutate(mutated)
            with self.subTest(relation=relation):
                self.assertFalse(self._probe_passes(mutated))

    def test_probe_fact_none_fails_closed_while_static_replay_uses_receipt_bytes(self) -> None:
        receipt = self._clock_predicate_receipt()
        self.assertFalse(self._probe_passes(receipt, live_clock_anchor=None))
        self.assertTrue(
            self._probe_passes(
                receipt,
                live_clock_anchor=(
                    readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE
                ),
            )
        )

    def test_clock_probe_live_anchor_states_and_falsifier_boundaries_gate(self) -> None:
        receipt = self._clock_predicate_receipt()
        value = receipt["facts"][0]["value"]
        base = {
            "boot_session_id": receipt["boot_session_id"],
            "realtime_ns": value["anchor_realtime_ns"],
            "monotonic_raw_ns": value["anchor_monotonic_raw_ns"],
            "read_skew_ns": 1_000,
        }
        for delta, expected in (
            (4_999_999, True),
            (5_000_000, True),
            (5_000_001, False),
        ):
            live = dict(base)
            live["realtime_ns"] += delta
            with self.subTest(delta=delta):
                self.assertEqual(
                    self._probe_passes(receipt, live_clock_anchor=live), expected
                )
        high_skew = dict(base, read_skew_ns=1_000_001)
        self.assertFalse(self._probe_passes(receipt, live_clock_anchor=high_skew))
        wrong_boot = dict(base, boot_session_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
        self.assertFalse(self._probe_passes(receipt, live_clock_anchor=wrong_boot))

    def test_original_arm_path_samples_once_and_passes_value_explicitly(self) -> None:
        source = inspect.getsource(readiness.generate_arm_receipt)
        self.assertEqual(source.count("_sample_live_clock_anchor()"), 1)
        self.assertIn("live_clock_anchor=live_clock_anchor", source)

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
                        receipt,
                        predicate_id,
                        expected_plan_sha256=ZERO_SHA,
                        live_clock_anchor=readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
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
                        missing_content,
                        predicate_id,
                        expected_plan_sha256=ZERO_SHA,
                        live_clock_anchor=readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
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
                        mutated,
                        predicate_id,
                        expected_plan_sha256=ZERO_SHA,
                        live_clock_anchor=readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
                    )
                )

            if kind not in {"IDENTITY_PIN_PROJECTION", "DRY_RUN_REHEARSAL"}:
                operator = self._generic_predicate_receipt(
                    row, source_kind="OPERATOR_ATTESTATION"
                )
                with self.subTest(row=row["row_id"], case="operator-source"):
                    self.assertEqual(
                        readiness._predicate_passes(
                            operator,
                            predicate_id,
                            expected_plan_sha256=ZERO_SHA,
                            live_clock_anchor=readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
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
        self.assertEqual(len(READINESS_REASON_CODES), 56)
        self.assertNotIn("GO", READINESS_REASON_CODES)
        self.assertNotIn("UNKNOWN", READINESS_REASON_CODES)
        upstream_refusal = sample_evidence()
        upstream_refusal["status"] = "REFUSE"
        upstream_refusal["reason_codes"] = ["clock_probe_failed"]
        validate_evidence_receipt(upstream_refusal)
        self.assertNotIn("clock_probe_failed", READINESS_REASON_CODES)


if __name__ == "__main__":
    unittest.main()
