"""D-134 arm-readiness receipts and fail-closed launch consumption.

This module authenticates committed pack bytes and evidence receipts.  It does
not perform live machine probes and it never treats a diagnostic result as
authority to start a measurement.  ``GO`` is only a machine-readable necessary
condition; physical launch remains outside this module.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from joulewise.identity_pins import (
    IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
    IDENTITY_PIN_PROJECTION_REASON_CODES,
    IdentityPinProjectionError,
    _gnu_sidecar,
    _render_json,
    _require_exact_keys as _identity_require_exact_keys,
    _require_lower_sha256 as _identity_require_lower_sha256,
    validate_identity_pin_projection,
    validate_projection_receipt,
    verify_frozen_projection,
)


PACK_DIGEST_ALGORITHM = "joulewise.committed_pack_tree_sha256.v1"
PACK_DIGEST_DOMAIN = b"joulewise.committed_pack_tree_sha256.v1\n"
ROW_REGISTRY_SCHEMA = "joulewise.arm_readiness_row_registry.v1"
ROW_REGISTRY_ID = "d117-row-registry-v1"
FREEZE_RECEIPT_SCHEMA = "joulewise.arm_readiness_freeze_receipt.v1"
ARM_RECEIPT_SCHEMA = "joulewise.arm_readiness_receipt.v1"
DRY_RUN_RECEIPT_SCHEMA = "joulewise.arm_readiness_dry_run_receipt.v1"
EVIDENCE_RECEIPT_SCHEMA = "joulewise.arm_readiness_evidence_receipt.v1"
CONSUMPTION_RECEIPT_SCHEMA = "joulewise.arm_readiness_launch_consumption.v1"
CONTRACT_ID = "D-134"
ROW_REGISTRY_RELATIVE_PATH = Path("configs/arm_readiness/d117_row_registry_v1.json")

ASSURANCE = {
    "model": "single_authority_hash_bound_replay.v1",
    "independent_attestation": False,
}

STRUCTURE_REASON_CODES = frozenset(
    {
        "readiness_schema_invalid",
        "readiness_receipt_kind_invalid",
        "readiness_unknown_key",
        "readiness_row_registry_mismatch",
        "readiness_row_set_incomplete",
        "readiness_row_applicability_invalid",
        "readiness_evidence_reference_invalid",
        "readiness_usage_invalid",
    }
)
CUSTODY_REASON_CODES = frozenset(
    {
        "readiness_pack_unreadable",
        "readiness_pack_namespace_anomalous",
        "readiness_pack_digest_mismatch",
        "readiness_pack_not_committed",
        "readiness_freeze_receipt_unreadable",
        "readiness_freeze_receipt_mismatch",
        "readiness_evidence_unreadable",
        "readiness_evidence_digest_mismatch",
        "readiness_receipt_namespace_anomalous",
    }
)
GIT_REASON_CODES = frozenset(
    {
        "readiness_git_tree_dirty",
        "readiness_reviewed_main_mismatch",
        "readiness_terminal_review_missing",
    }
)
LIFECYCLE_REASON_CODES = frozenset(
    {
        "readiness_receipt_superseded",
        "readiness_record_expired",
        "readiness_record_consumed",
        "readiness_output_collision",
        "readiness_lock_unavailable",
        "readiness_dry_run_missing",
        "readiness_dry_run_refused",
        "readiness_dry_run_stale",
        "readiness_dry_run_used_as_arm_record",
    }
)
POLICY_REASON_CODES = frozenset(
    {
        "readiness_dependency_refused",
        "readiness_waiver_source_invalid",
        "readiness_waiver_set_nonempty",
        "readiness_root_binding_invalid",
        "readiness_root_not_fresh",
        "readiness_backup_preflight_refused",
        "readiness_machine_preflight_refused",
        "readiness_clock_preflight_refused",
        "readiness_ledger_preflight_refused",
        "readiness_launch_capability_unavailable",
    }
)
ENVIRONMENT_REASON_CODES = frozenset(
    {"readiness_io_error", "readiness_internal_error"}
)
READINESS_REASON_CODES = frozenset().union(
    STRUCTURE_REASON_CODES,
    CUSTODY_REASON_CODES,
    GIT_REASON_CODES,
    LIFECYCLE_REASON_CODES,
    POLICY_REASON_CODES,
    IDENTITY_PIN_PROJECTION_REASON_CODES,
    ENVIRONMENT_REASON_CODES,
)
REASON_TYPE_BY_CODE = {
    **{code: "STRUCTURE" for code in STRUCTURE_REASON_CODES},
    **{code: "CUSTODY" for code in CUSTODY_REASON_CODES},
    **{code: "GIT" for code in GIT_REASON_CODES},
    **{code: "LIFECYCLE" for code in LIFECYCLE_REASON_CODES},
    **{code: "POLICY" for code in POLICY_REASON_CODES},
    **{code: "IDENTITY" for code in IDENTITY_PIN_PROJECTION_REASON_CODES},
    **{code: "ENVIRONMENT" for code in ENVIRONMENT_REASON_CODES},
}

WINDOW_KINDS = frozenset({"ALPHA", "BETA", "GAMMA"})
EVALUATION_PHASES = frozenset({"FREEZE_AND_ARM", "ARM_ONLY"})
APPLICABILITY_RULES = frozenset(
    {"ALWAYS", "CLOCK_HELPER_ONLY", "SUCCESSOR_ACCEPTANCE_ONLY"}
)
APPLICABILITIES = frozenset({"REQUIRED", "NOT_APPLICABLE"})
ROW_VERDICTS = frozenset({"PASS", "REFUSE", "NOT_APPLICABLE"})
RECEIPT_STATUSES = frozenset({"PASS", "REFUSE"})
ARM_DISPOSITIONS = frozenset({"GO", "NO_GO", "NOT_APPLICABLE"})
EVIDENCE_NAMESPACES = frozenset({"PACK", "WINDOW_CUSTODY"})
SOURCE_KINDS = frozenset({"PROBE", "PACK", "GIT", "OPERATOR_ATTESTATION"})
SYNTHETIC_DOMAINS = (
    "LIVE_PRIVILEGE",
    "LIVE_CLOCK",
    "LIVE_MACHINE",
    "LIVE_POWER",
    "PRODUCTION_ROOTS",
    "PRODUCTION_BACKUPS",
    "PRODUCTION_LEDGER",
    "LAUNCH_CONSUMPTION",
)

_LOWER_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_LOWER_GIT_OID_RE = re.compile(r"^[0-9a-f]{40}$")
_RECEIPT_NAME_RE = {
    "freeze": re.compile(r"^freeze-([0-9]{4,})\.json$"),
    "arm": re.compile(r"^arm-([0-9]{4,})\.json$"),
    "dry-run": re.compile(r"^dry-run-([0-9]{4,})\.json$"),
}
_PROFILE_BY_PACK = {
    "d117_floor_qwen25_1p5b_v1": "ALPHA",
    "d117_floor_qwen25_7b_v1": "BETA",
    "d117_contrast_qwen25_1p5b_vs_7b_v1": "GAMMA",
}

REGISTRY_KEYS = {"schema_version", "registry_id", "plan_profiles", "rows"}
PROFILE_KEYS = {"profile_id", "window_kind", "required_row_ids"}
ROW_DEFINITION_KEYS = {
    "row_id",
    "evaluation_phase",
    "applicability_rule",
    "predicate_id",
    "required_evidence_kinds",
}
PACK_IDENTITY_KEYS = {
    "pack_id",
    "plan_id",
    "window_id",
    "pack_root",
    "plan_path",
    "plan_sha256",
}
PACK_KEYS = {
    "pack_id",
    "plan_id",
    "window_id",
    "pack_root",
    "pack_digest_algorithm",
    "pack_sha256",
    "plan_tree_path",
    "plan_tree_sha256",
    "plan_tree_sidecar_path",
    "plan_tree_sidecar_sha256",
}
REVIEWED_MAIN_KEYS = {
    "head_commit",
    "head_tree_oid",
    "local_main_commit",
    "origin_main_commit",
    "clean",
    "exact_match",
}
ARM_CONTEXT_KEYS = {
    "bracket_session_id",
    "pre_attempt_id",
    "post_attempt_id",
    "clock_route",
    "claim_runs_root",
    "bound_runs_root",
    "custody_root",
    "quarantine_root",
    "claim_backup_destination",
    "bound_backup_destination",
    "waiver_path",
}
ROW_REGISTRY_REFERENCE_KEYS = {"registry_id", "path", "sha256", "plan_profile"}
FREEZE_REFERENCE_KEYS = {"receipt_id", "path", "sha256"}
EVIDENCE_ITEM_KEYS = {
    "evidence_id",
    "receipt_kind",
    "namespace",
    "path",
    "sha256",
    "schema_version",
    "status",
}
ROW_KEYS = {
    "row_id",
    "evaluation_phase",
    "applicability",
    "verdict",
    "predicate_id",
    "evidence_ids",
}
REFUSAL_KEYS = {"type", "code", "row_id", "evidence_id"}
SUPERSEDES_KEYS = {
    "receipt_id",
    "receipt_path",
    "receipt_sha256",
    "pack_id",
    "pack_sha256",
}
ASSURANCE_KEYS = {"model", "independent_attestation"}
SYNTHETIC_CONTEXT_KEYS = {"rehearsal_id", "root", "ledger_path", "backend"}
DRY_RUN_CHECK_KEYS = {
    "check_id",
    "status",
    "command_sha256",
    "stdout_sha256",
    "stderr_sha256",
    "exit_code",
}
FACT_KEYS = {
    "fact_id",
    "value_type",
    "value",
    "source_kind",
    "source_path",
    "source_sha256",
}
EVIDENCE_CHECK_KEYS = {"check_id", "status"}
FREEZE_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "status",
    "arm_disposition",
    "issued_at_utc",
    "pack_identity",
    "row_registry",
    "evidence",
    "rows",
    "refusals",
    "supersedes",
    "assurance",
}
ARM_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "mode",
    "status",
    "arm_disposition",
    "issued_at_utc",
    "boot_session_id",
    "valid_until_monotonic_ns",
    "pack",
    "reviewed_main",
    "arm_context",
    "freeze_receipt",
    "row_registry",
    "evidence",
    "rows",
    "refusals",
    "supersedes",
    "assurance",
}
DRY_RUN_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "mode",
    "status",
    "arm_disposition",
    "issued_at_utc",
    "pack",
    "synthetic_context",
    "evidence",
    "checks",
    "omitted_live_domains",
    "refusals",
    "assurance",
}
EVIDENCE_RECEIPT_KEYS = {
    "schema_version",
    "evidence_id",
    "kind",
    "status",
    "issued_at_utc",
    "boot_session_id",
    "valid_until_monotonic_ns",
    "pack_sha256",
    "head_commit",
    "facts",
    "checks",
    "reason_codes",
    "assurance",
}
CONSUMPTION_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "consumed_at_utc",
    "arm_receipt",
    "pack_sha256",
    "head_commit",
    "volatile_checks",
    "assurance",
}

# D-134's row table is design authority for these requirements.  The registry
# deliberately remains the exact-key row/kind vocabulary; content and source
# admissibility are derived here from those existing evidence kinds.
_EVIDENCE_SOURCE_KINDS = {
    "ACCEPTANCE_OWNER": frozenset({"PROBE"}),
    "ACCEPTANCE_SUCCESSOR": frozenset({"PACK", "PROBE"}),
    "BACKUP_PREFLIGHT": frozenset({"PROBE"}),
    "CLOCK_ATTESTATION": frozenset({"OPERATOR_ATTESTATION", "PROBE"}),
    "CLOCK_PROBE": frozenset({"PROBE"}),
    "DOCTRINE_PIN": frozenset({"PACK"}),
    "DRY_RUN_REHEARSAL": frozenset(),
    "ESTIMATOR_IDENTITY": frozenset({"PACK"}),
    "GIT_CHECKOUT": frozenset({"GIT"}),
    "IDENTITY_PIN_PROJECTION": frozenset(),
    "LAUNCH_RECIPE": frozenset({"PACK", "PROBE"}),
    "LEDGER_RESERVATION": frozenset({"PROBE"}),
    "MACHINE_PREFLIGHT": frozenset({"PROBE"}),
    "MAINTENANCE_CENSUS": frozenset({"OPERATOR_ATTESTATION", "PROBE"}),
    "MINT_TRUST": frozenset({"PROBE"}),
    "MULTICELL_MINT": frozenset({"PROBE"}),
    "OFFLINE_INPUT_INVENTORY": frozenset({"PROBE"}),
    "PACK_AUTHENTICATION": frozenset({"GIT", "PACK", "PROBE"}),
    "PACK_FAMILY": frozenset({"PACK"}),
    "POWERMETRICS_PROBE": frozenset({"PROBE"}),
    "POWER_PREFLIGHT": frozenset({"PROBE"}),
    "PRIVILEGE_INSTALLATION": frozenset({"PROBE"}),
    "PROCESS_CENSUS": frozenset({"PROBE"}),
    "REASON_CODE_COVERAGE": frozenset({"PROBE"}),
    "RECEIPT_ORACLE": frozenset({"PROBE"}),
    "RECOVERY_LEDGER_TEST": frozenset({"PROBE"}),
    "ROOT_PREFLIGHT": frozenset({"PROBE"}),
    "TERMINAL_REVIEW": frozenset({"GIT", "PROBE"}),
    "THREE_WINDOW_REGRESSION": frozenset({"PROBE"}),
}

_LOWER_SHA256_CONTENT = object()
_PREDICATE_CONTENT_REQUIREMENTS: dict[str, Mapping[str, Any]] = {
    "clock.correct_and_prior_state.v1": {
        "independent_clock_attestation": True,
        "prior_systemsetup_state_captured": True,
    },
    "clock.network_time_off.v1": {
        "fresh_probe": True,
        "network_time": "off",
    },
    "clock.restore_recipe.v1": {
        "close_out_recipe_hashes_match_pack": True,
        "restore_after_both_backups": True,
        "restore_after_verdict": True,
    },
    "desk.acceptance_owner.v1": {
        "active_acceptance_artifact_authenticated": True,
        "copied_scalar_accepted": False,
        "domain_owner_verified": True,
        "unknown_key_accepted": False,
        "writer_test_status": "PASS",
    },
    "desk.acceptance_successor.v1": {
        "selected_before_member_one": True,
        "successor_receipt_authenticated": True,
        "successor_receipt_status": "PASS",
    },
    "desk.arming_procedure.v1": {
        "frozen_launch_recipe_hash_matches_pack": True,
        "runbook_section_hashes_match_pack": True,
        "runbook_sections": ["5", "5A", "5B", "5C", "6", "10"],
    },
    "desk.current_pack.v1": {
        "attempt_policy_status": "PASS",
        "committed_pack_digest_status": "PASS",
        "extraction_specification_status": "PASS",
        "manifest_validator_status": "PASS",
        "pack_generator_check_status": "PASS",
        "plan_validator_status": "PASS",
    },
    "desk.estimator_identity.v1": {
        "admitted_by_mint_registry": True,
        "cli_estimator_id_accepted": False,
        "estimator_id_derived_from_frozen_plan": True,
    },
    "desk.identity_pin_projection.v1": {
        "projection_status": "PASS",
    },
    "desk.mint_trust.v1": {
        "profile_test_status": "PASS",
        "same_head": True,
        "same_pack_digest": True,
    },
    "desk.multicell_mint.v1": {
        "focused_integration_status": "PASS",
        "mint_schemas_match_committed_sources": True,
        "pinsets_match_committed_sources": True,
    },
    "desk.pack_family.v1": {
        "floor_transport_identities_consistent": True,
        "pack_receipts": ["ALPHA", "BETA", "GAMMA"],
        "same_reviewed_head": True,
    },
    "desk.reason_code_plumbing.v1": {
        "all_produced_refusals_are_closed": True,
        "rehearsal_receipt_status": "PASS",
        "registry_coverage_test_status": "PASS",
    },
    "desk.receipt_oracle.v1": {
        "derived_from_committed_ledger_implementation": True,
        "exact_pack_oracle_match": True,
    },
    "desk.recovery_ledger_path.v1": {
        "bound_head": True,
        "recovery_ledger_focused_suite_status": "PASS",
    },
    "desk.reviewed_checkout.v1": {
        "exact_tree_equality": True,
        "head_equals_local_main": True,
        "head_equals_origin_main": True,
        "status_empty_including_untracked": True,
    },
    "desk.terminal_review.v1": {
        "same_head_tree": True,
        "same_pack_digest": True,
        "terminal_review_status": "PASS",
    },
    "desk.three_window_regression.v1": {
        "profiles": ["ALPHA", "BETA", "GAMMA"],
        "same_head": True,
        "three_window_live_ledger_regression_status": "PASS",
    },
    "desk.under_lease_rehearsal.v1": {
        "real_reservation_cli_execute": "PASS",
        "real_writer_entry_post": "PASS",
        "real_writer_entry_pre": "PASS",
        "same_head_pack_binding": "PASS",
    },
    "privilege.activation_fence.v1": {
        "inactive_state_preceded_activation": True,
        "separate_ed_visible_activation": True,
    },
    "privilege.fresh_authorization.v1": {
        "fresh_authorization_sequence": True,
        "sudo_k_reviewed": True,
    },
    "privilege.installed_bytes.v1": {
        "installed_digests_match_pack_staged_digests": True,
    },
    "privilege.isolated_interpreter.v1": {
        "frozen_isolated_interpreter_contract": True,
    },
    "t0.background_quiet.v1": {
        "observation_status": "PASS",
    },
    "t0.campaign_lock_absent.v1": {
        "fresh_root_receipt": True,
        "live_lock_absent": True,
        "stale_lock_absent": True,
        "unreadable_lock_absent": True,
    },
    "t0.display_thermal_idle.v1": {
        "display_predicate": True,
        "idle_predicate": True,
        "prewindow_check_wait_status": "PASS",
        "quiet_mac_prep_status": "PASS",
        "screensaver_predicate": True,
        "thermal_predicate": True,
    },
    "t0.fresh_roots_waivers.v1": {
        "roots_absolute": True,
        "roots_derived_from_frozen_leaves_and_arm_context": True,
        "roots_distinct": True,
        "roots_empty": True,
        "waiver_bytes_decoded": [],
    },
    "t0.ledger_reservation.v1": {
        "diagnostic_status": "PASS",
        "events": ["calibration_pre_reserve_authorized"],
        "execute_mode": True,
        "plan_sha256": _LOWER_SHA256_CONTENT,
        "status": "reserved",
    },
    "t0.machine_readiness.v1": {
        "current": True,
        "frozen_prewindow_check_wait_command": True,
        "same_plan": True,
        "same_roots": True,
        "status": "READY",
    },
    "t0.no_stray_keepawake.v1": {
        "absent_process_classes": ["agent", "browser", "keep_awake", "monitor"],
        "fresh_process_census": True,
    },
    "t0.offline_inputs.v1": {
        "file_inventory_matches_frozen_inputs": True,
        "no_network_fetch": True,
        "u11_live_derivation_matches_frozen_inputs": True,
    },
    "t0.passwordless_powermetrics.v1": {
        "exact_reviewed_sudo_n_powermetrics_command": True,
        "exit_code": 0,
    },
    "t0.power_path.v1": {
        "ac_state_matches_frozen_policy": True,
        "negotiation_matches_frozen_policy": True,
        "power_policy_matches": True,
        "supply_matches_frozen_policy": True,
    },
    "t0.single_launch_capability.v1": {
        "atomic_single_use_capability_available": True,
        "attempt_ids_unused": True,
        "exact_launch_command_frozen": True,
        "session_id_unused": True,
    },
    "t0.storage_backup_capacity.v1": {
        "destinations_distinct": True,
        "destinations_exist": True,
        "destinations_have_required_capacity": True,
        "destinations_writable": True,
    },
}

_PREDICATE_EVIDENCE_KIND = {
    "clock.correct_and_prior_state.v1": "CLOCK_ATTESTATION",
    "clock.network_time_off.v1": "CLOCK_PROBE",
    "clock.restore_recipe.v1": "DOCTRINE_PIN",
    "desk.acceptance_owner.v1": "ACCEPTANCE_OWNER",
    "desk.acceptance_successor.v1": "ACCEPTANCE_SUCCESSOR",
    "desk.arming_procedure.v1": "DOCTRINE_PIN",
    "desk.current_pack.v1": "PACK_AUTHENTICATION",
    "desk.estimator_identity.v1": "ESTIMATOR_IDENTITY",
    "desk.identity_pin_projection.v1": "IDENTITY_PIN_PROJECTION",
    "desk.mint_trust.v1": "MINT_TRUST",
    "desk.multicell_mint.v1": "MULTICELL_MINT",
    "desk.pack_family.v1": "PACK_FAMILY",
    "desk.reason_code_plumbing.v1": "REASON_CODE_COVERAGE",
    "desk.receipt_oracle.v1": "RECEIPT_ORACLE",
    "desk.recovery_ledger_path.v1": "RECOVERY_LEDGER_TEST",
    "desk.reviewed_checkout.v1": "GIT_CHECKOUT",
    "desk.terminal_review.v1": "TERMINAL_REVIEW",
    "desk.three_window_regression.v1": "THREE_WINDOW_REGRESSION",
    "desk.under_lease_rehearsal.v1": "DRY_RUN_REHEARSAL",
    "privilege.activation_fence.v1": "PRIVILEGE_INSTALLATION",
    "privilege.fresh_authorization.v1": "PRIVILEGE_INSTALLATION",
    "privilege.installed_bytes.v1": "PRIVILEGE_INSTALLATION",
    "privilege.isolated_interpreter.v1": "PRIVILEGE_INSTALLATION",
    "t0.background_quiet.v1": "MAINTENANCE_CENSUS",
    "t0.campaign_lock_absent.v1": "ROOT_PREFLIGHT",
    "t0.display_thermal_idle.v1": "MACHINE_PREFLIGHT",
    "t0.fresh_roots_waivers.v1": "ROOT_PREFLIGHT",
    "t0.ledger_reservation.v1": "LEDGER_RESERVATION",
    "t0.machine_readiness.v1": "MACHINE_PREFLIGHT",
    "t0.no_stray_keepawake.v1": "PROCESS_CENSUS",
    "t0.offline_inputs.v1": "OFFLINE_INPUT_INVENTORY",
    "t0.passwordless_powermetrics.v1": "POWERMETRICS_PROBE",
    "t0.power_path.v1": "POWER_PREFLIGHT",
    "t0.single_launch_capability.v1": "LAUNCH_RECIPE",
    "t0.storage_backup_capacity.v1": "BACKUP_PREFLIGHT",
}


class ArmReadinessError(ValueError):
    """A refusal with one code from the D-134 closed vocabulary."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        row_id: str | None = None,
        evidence_id: str | None = None,
    ) -> None:
        if reason_code not in READINESS_REASON_CODES:
            raise ValueError(f"unregistered readiness reason code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code
        self.row_id = row_id
        self.evidence_id = evidence_id

    def refusal(self) -> dict[str, Any]:
        return {
            "type": REASON_TYPE_BY_CODE[self.reason_code],
            "code": self.reason_code,
            "row_id": self.row_id,
            "evidence_id": self.evidence_id,
        }


def render_json(value: Any) -> bytes:
    """Return the D-134 canonical bytes, shared with D-131."""

    return _render_json(value)


def _render_plan_tree(value: Any) -> bytes:
    """Preserve the byte format owned by the three D-117 pack generators."""

    return (
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def gnu_sidecar(digest: str, filename: str) -> bytes:
    _require_lower_sha256(digest, "sidecar digest")
    return _gnu_sidecar(digest, filename)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_exact_keys(
    value: object, keys: set[str], where: str
) -> Mapping[str, Any]:
    try:
        return _identity_require_exact_keys(value, keys, where)
    except IdentityPinProjectionError as exc:
        observed = set(value) if isinstance(value, Mapping) else set()
        code = "readiness_unknown_key" if observed - keys else "readiness_schema_invalid"
        raise ArmReadinessError(code, str(exc)) from exc


def _require_lower_sha256(value: object, where: str) -> str:
    try:
        return _identity_require_lower_sha256(value, where)
    except IdentityPinProjectionError as exc:
        raise ArmReadinessError("readiness_schema_invalid", str(exc)) from exc


def _require_lower_git_oid(value: object, where: str) -> str:
    if not isinstance(value, str) or _LOWER_GIT_OID_RE.fullmatch(value) is None:
        raise ArmReadinessError(
            "readiness_schema_invalid",
            f"{where} must be exactly 40 lowercase hexadecimal characters",
        )
    return value


def _require_boot_session_id(value: object, where: str) -> str:
    if not isinstance(value, str):
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must be a canonical UUID"
        )
    try:
        canonical = str(uuid.UUID(value))
    except (ValueError, AttributeError) as exc:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must be a canonical UUID"
        ) from exc
    if value != canonical:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must be a canonical UUID"
        )
    return value


def _current_boot_session_id() -> str:
    """Derive Darwin's boot epoch; callers must fail closed if unavailable."""

    try:
        completed = subprocess.run(
            ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ArmReadinessError(
            "readiness_io_error", f"cannot derive kern.bootsessionuuid: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ArmReadinessError(
            "readiness_io_error",
            f"cannot derive kern.bootsessionuuid: {detail or 'sysctl failed'}",
        )
    try:
        value = completed.stdout.decode("ascii", errors="strict").strip().lower()
    except UnicodeDecodeError as exc:
        raise ArmReadinessError(
            "readiness_io_error", "kern.bootsessionuuid is not ASCII"
        ) from exc
    try:
        return _require_boot_session_id(value, "kern.bootsessionuuid")
    except ArmReadinessError as exc:
        raise ArmReadinessError("readiness_io_error", str(exc)) from exc


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"duplicate JSON key {key!r}"
            )
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ArmReadinessError(
        "readiness_schema_invalid", f"non-finite JSON number {value!r} is forbidden"
    )


def _strict_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ArmReadinessError(
            "readiness_schema_invalid",
            f"non-finite JSON number {value!r} is forbidden",
        )
    return parsed


def parse_json_bytes(raw: bytes, *, require_canonical: bool = False) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ArmReadinessError(
            "readiness_schema_invalid", "JSON bytes are not valid UTF-8"
        ) from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
            parse_float=_strict_float,
        )
    except ArmReadinessError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"invalid strict JSON: {exc}"
        ) from exc
    if require_canonical:
        try:
            canonical = render_json(value)
        except (TypeError, ValueError) as exc:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"JSON cannot be canonicalized: {exc}"
            ) from exc
        if raw != canonical:
            raise ArmReadinessError(
                "readiness_schema_invalid", "JSON bytes are not canonical D-134 bytes"
            )
    return value


def load_json_file(path: Path | str, *, canonical: bool = False) -> Any:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_io_error", f"cannot read {path}: {exc}"
        ) from exc
    return parse_json_bytes(raw, require_canonical=canonical)


def _require_string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must be a nonempty string"
        )
    return value


def _require_int(value: object, where: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must be an integer >= {minimum}"
        )
    return value


def _require_relative_path(value: object, where: str) -> str:
    path = _require_string(value, where)
    if "\\" in path:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid", f"{where} uses a backslash"
        )
    pure = PurePosixPath(path)
    if pure.is_absolute() or path != pure.as_posix() or ".." in pure.parts or "." in pure.parts:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid", f"{where} escapes its namespace"
        )
    return path


def _require_path_component(value: object, where: str) -> str:
    result = _require_string(value, where)
    if (
        PurePosixPath(result).name != result
        or result in {".", ".."}
        or "\\" in result
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid", f"{where} must be one path-safe component"
        )
    return result


def _resolve_namespace_path(
    namespace_root: Path,
    relative_path: object,
    where: str,
) -> Path:
    """Resolve an existing namespace-relative path without permitting escape."""

    relative = _require_relative_path(relative_path, where)
    try:
        resolved_root = namespace_root.resolve(strict=True)
        resolved = (namespace_root / relative).resolve(strict=True)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"{where} is missing or unreadable",
        ) from exc
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            f"{where} does not resolve inside its namespace",
        ) from exc
    return resolved


def _validate_assurance(value: object, where: str = "assurance") -> None:
    assurance = _require_exact_keys(value, ASSURANCE_KEYS, where)
    if dict(assurance) != ASSURANCE:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} must carry the D-120 qualifier"
        )


def _validate_supersedes(value: object, where: str = "supersedes") -> None:
    if value is None:
        return
    item = _require_exact_keys(value, SUPERSEDES_KEYS, where)
    for name in ("receipt_id", "receipt_path", "pack_id"):
        _require_string(item[name], f"{where}.{name}")
    _require_relative_path(item["receipt_path"], f"{where}.receipt_path")
    for name in ("receipt_sha256", "pack_sha256"):
        _require_lower_sha256(item[name], f"{where}.{name}")


def _validate_row_registry_reference(value: object, where: str) -> None:
    item = _require_exact_keys(value, ROW_REGISTRY_REFERENCE_KEYS, where)
    _require_string(item["registry_id"], f"{where}.registry_id")
    _require_relative_path(item["path"], f"{where}.path")
    _require_lower_sha256(item["sha256"], f"{where}.sha256")
    if item["plan_profile"] not in WINDOW_KINDS:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.plan_profile is invalid"
        )


def _validate_pack_identity(value: object, where: str) -> None:
    item = _require_exact_keys(value, PACK_IDENTITY_KEYS, where)
    for name in ("pack_id", "plan_id", "window_id", "pack_root"):
        _require_string(item[name], f"{where}.{name}")
    _require_relative_path(item["plan_path"], f"{where}.plan_path")
    _require_lower_sha256(item["plan_sha256"], f"{where}.plan_sha256")


def _validate_pack(value: object, where: str) -> None:
    item = _require_exact_keys(value, PACK_KEYS, where)
    for name in ("pack_id", "plan_id", "window_id", "pack_root"):
        _require_string(item[name], f"{where}.{name}")
    if item["pack_digest_algorithm"] != PACK_DIGEST_ALGORITHM:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.pack_digest_algorithm is invalid"
        )
    for name in ("pack_sha256", "plan_tree_sha256", "plan_tree_sidecar_sha256"):
        _require_lower_sha256(item[name], f"{where}.{name}")
    for name in ("plan_tree_path", "plan_tree_sidecar_path"):
        _require_relative_path(item[name], f"{where}.{name}")


def _validate_evidence_item(value: object, where: str) -> None:
    item = _require_exact_keys(value, EVIDENCE_ITEM_KEYS, where)
    for name in ("evidence_id", "receipt_kind", "schema_version"):
        _require_string(item[name], f"{where}.{name}")
    if item["namespace"] not in EVIDENCE_NAMESPACES:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.namespace is invalid"
        )
    _require_relative_path(item["path"], f"{where}.path")
    _require_lower_sha256(item["sha256"], f"{where}.sha256")
    if item["status"] not in RECEIPT_STATUSES:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.status is invalid"
        )


def _validate_row(value: object, where: str) -> None:
    item = _require_exact_keys(value, ROW_KEYS, where)
    _require_string(item["row_id"], f"{where}.row_id")
    if item["evaluation_phase"] not in EVALUATION_PHASES:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.evaluation_phase is invalid"
        )
    if item["applicability"] not in APPLICABILITIES:
        raise ArmReadinessError(
            "readiness_row_applicability_invalid", f"{where}.applicability is invalid"
        )
    if item["verdict"] not in ROW_VERDICTS:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.verdict is invalid"
        )
    if (item["applicability"] == "NOT_APPLICABLE") != (
        item["verdict"] == "NOT_APPLICABLE"
    ):
        raise ArmReadinessError(
            "readiness_row_applicability_invalid",
            f"{where} applicability and verdict disagree",
        )
    _require_string(item["predicate_id"], f"{where}.predicate_id")
    if not isinstance(item["evidence_ids"], list) or any(
        not isinstance(evidence_id, str) or not evidence_id
        for evidence_id in item["evidence_ids"]
    ):
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.evidence_ids is invalid"
        )
    if item["evidence_ids"] != sorted(set(item["evidence_ids"])):
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.evidence_ids must be sorted and unique"
        )


def _validate_refusal(value: object, where: str) -> None:
    item = _require_exact_keys(value, REFUSAL_KEYS, where)
    if item["code"] not in READINESS_REASON_CODES:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.code is not closed"
        )
    if item["type"] != REASON_TYPE_BY_CODE[item["code"]]:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.type does not match code"
        )
    for name in ("row_id", "evidence_id"):
        if item[name] is not None and (not isinstance(item[name], str) or not item[name]):
            raise ArmReadinessError(
                "readiness_schema_invalid", f"{where}.{name} is invalid"
            )


def _validate_rows_and_refusals(receipt: Mapping[str, Any]) -> None:
    rows = receipt["rows"]
    refusals = receipt["refusals"]
    evidence = receipt["evidence"]
    if not isinstance(rows, list) or not isinstance(refusals, list) or not isinstance(evidence, list):
        raise ArmReadinessError(
            "readiness_schema_invalid", "rows, refusals, and evidence must be arrays"
        )
    for index, item in enumerate(evidence):
        _validate_evidence_item(item, f"evidence[{index}]")
    for index, row in enumerate(rows):
        _validate_row(row, f"rows[{index}]")
    for index, refusal in enumerate(refusals):
        _validate_refusal(refusal, f"refusals[{index}]")
    row_ids = [row["row_id"] for row in rows]
    evidence_ids = [item["evidence_id"] for item in evidence]
    if row_ids != sorted(set(row_ids)) or evidence_ids != sorted(set(evidence_ids)):
        raise ArmReadinessError(
            "readiness_schema_invalid", "row and evidence IDs must be sorted and unique"
        )
    if any(
        evidence_id not in set(evidence_ids)
        for row in rows
        for evidence_id in row["evidence_ids"]
    ):
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid", "row references absent evidence"
        )
    row_id_set = set(row_ids)
    if any(
        refusal["row_id"] is not None and refusal["row_id"] not in row_id_set
        for refusal in refusals
    ):
        raise ArmReadinessError(
            "readiness_row_set_incomplete", "refusal references an absent row"
        )
    refused_row_ids = {
        refusal["row_id"]
        for refusal in refusals
        if refusal["row_id"] is not None
    }
    if any(
        row["verdict"] == "REFUSE" and row["row_id"] not in refused_row_ids
        for row in rows
    ):
        raise ArmReadinessError(
            "readiness_schema_invalid", "every refused row must carry a row refusal"
        )


def validate_registry(value: object) -> Mapping[str, Any]:
    registry = _require_exact_keys(value, REGISTRY_KEYS, "registry")
    if registry["schema_version"] != ROW_REGISTRY_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "registry schema_version is invalid"
        )
    if registry["registry_id"] != ROW_REGISTRY_ID:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "registry_id is invalid"
        )
    profiles = registry["plan_profiles"]
    rows = registry["rows"]
    if not isinstance(profiles, list) or not isinstance(rows, list):
        raise ArmReadinessError(
            "readiness_schema_invalid", "registry profiles and rows must be arrays"
        )
    row_ids: list[str] = []
    for index, raw_row in enumerate(rows):
        row = _require_exact_keys(raw_row, ROW_DEFINITION_KEYS, f"rows[{index}]")
        row_id = _require_string(row["row_id"], f"rows[{index}].row_id")
        row_ids.append(row_id)
        if row["evaluation_phase"] not in EVALUATION_PHASES:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"rows[{index}].evaluation_phase is invalid"
            )
        if row["applicability_rule"] not in APPLICABILITY_RULES:
            raise ArmReadinessError(
                "readiness_row_applicability_invalid",
                f"rows[{index}].applicability_rule is invalid",
            )
        _require_string(row["predicate_id"], f"rows[{index}].predicate_id")
        kinds = row["required_evidence_kinds"]
        if (
            not isinstance(kinds, list)
            or not kinds
            or any(not isinstance(kind, str) or not kind for kind in kinds)
            or kinds != sorted(set(kinds))
        ):
            raise ArmReadinessError(
                "readiness_schema_invalid",
                f"rows[{index}].required_evidence_kinds is invalid",
            )
    if row_ids != sorted(set(row_ids)) or len(row_ids) != 35:
        raise ArmReadinessError(
            "readiness_row_set_incomplete", "registry must contain 35 unique sorted rows"
        )
    profile_ids: list[str] = []
    for index, raw_profile in enumerate(profiles):
        profile = _require_exact_keys(raw_profile, PROFILE_KEYS, f"plan_profiles[{index}]")
        profile_id = _require_string(
            profile["profile_id"], f"plan_profiles[{index}].profile_id"
        )
        profile_ids.append(profile_id)
        if profile["window_kind"] not in WINDOW_KINDS or profile_id != profile["window_kind"]:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"plan_profiles[{index}] identity is invalid"
            )
        required = profile["required_row_ids"]
        if not isinstance(required, list) or required != row_ids:
            raise ArmReadinessError(
                "readiness_row_set_incomplete",
                f"plan_profiles[{index}] must name the complete ordered row set",
            )
    if profile_ids != ["ALPHA", "BETA", "GAMMA"]:
        raise ArmReadinessError(
            "readiness_row_set_incomplete", "registry must contain ALPHA, BETA, GAMMA"
        )
    return registry


def validate_evidence_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, EVIDENCE_RECEIPT_KEYS, "evidence receipt")
    if receipt["schema_version"] != EVIDENCE_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "evidence receipt schema is invalid"
        )
    for name in ("evidence_id", "kind", "issued_at_utc"):
        _require_string(receipt[name], f"evidence receipt.{name}")
    _require_boot_session_id(
        receipt["boot_session_id"], "evidence receipt.boot_session_id"
    )
    _require_lower_git_oid(receipt["head_commit"], "evidence receipt.head_commit")
    if receipt["status"] not in RECEIPT_STATUSES:
        raise ArmReadinessError(
            "readiness_schema_invalid", "evidence status is invalid"
        )
    _require_int(
        receipt["valid_until_monotonic_ns"],
        "evidence receipt.valid_until_monotonic_ns",
        minimum=1,
    )
    _require_lower_sha256(receipt["pack_sha256"], "evidence receipt.pack_sha256")
    facts = receipt["facts"]
    checks = receipt["checks"]
    reasons = receipt["reason_codes"]
    if not isinstance(facts, list) or not isinstance(checks, list) or not isinstance(reasons, list):
        raise ArmReadinessError(
            "readiness_schema_invalid", "evidence facts, checks, and reason_codes must be arrays"
        )
    for index, raw_fact in enumerate(facts):
        fact = _require_exact_keys(raw_fact, FACT_KEYS, f"facts[{index}]")
        _require_string(fact["fact_id"], f"facts[{index}].fact_id")
        _require_string(fact["value_type"], f"facts[{index}].value_type")
        if fact["source_kind"] not in SOURCE_KINDS:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"facts[{index}].source_kind is invalid"
            )
        _require_relative_path(fact["source_path"], f"facts[{index}].source_path")
        _require_lower_sha256(fact["source_sha256"], f"facts[{index}].source_sha256")
        try:
            render_json(fact["value"])
        except (TypeError, ValueError) as exc:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"facts[{index}].value is not strict JSON"
            ) from exc
    for index, raw_check in enumerate(checks):
        check = _require_exact_keys(raw_check, EVIDENCE_CHECK_KEYS, f"checks[{index}]")
        _require_string(check["check_id"], f"checks[{index}].check_id")
        if check["status"] not in RECEIPT_STATUSES:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"checks[{index}].status is invalid"
            )
    if (
        any(
            not isinstance(reason, str)
            or re.fullmatch(r"[a-z][a-z0-9_]*", reason) is None
            for reason in reasons
        )
        or reasons != sorted(set(reasons))
    ):
        raise ArmReadinessError(
            "readiness_schema_invalid",
            "evidence reason_codes must be sorted domain-code strings",
        )
    if (receipt["status"] == "PASS") == bool(reasons):
        raise ArmReadinessError(
            "readiness_schema_invalid", "evidence status and reason_codes disagree"
        )
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_freeze_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, FREEZE_RECEIPT_KEYS, "freeze receipt")
    if receipt["schema_version"] != FREEZE_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "freeze receipt schema is invalid"
        )
    if receipt["receipt_kind"] != "freeze":
        raise ArmReadinessError(
            "readiness_receipt_kind_invalid", "freeze receipt_kind is invalid"
        )
    if receipt["status"] not in RECEIPT_STATUSES or receipt["arm_disposition"] != "NOT_APPLICABLE":
        raise ArmReadinessError(
            "readiness_schema_invalid", "freeze status/disposition is invalid"
        )
    for name in ("receipt_id", "issued_at_utc"):
        _require_string(receipt[name], f"freeze receipt.{name}")
    _validate_pack_identity(receipt["pack_identity"], "freeze receipt.pack_identity")
    _validate_row_registry_reference(receipt["row_registry"], "freeze receipt.row_registry")
    _validate_rows_and_refusals(receipt)
    if any(row["evaluation_phase"] != "FREEZE_AND_ARM" for row in receipt["rows"]):
        raise ArmReadinessError(
            "readiness_row_set_incomplete", "freeze receipt contains an ARM_ONLY row"
        )
    if (receipt["status"] == "PASS") == bool(receipt["refusals"]):
        raise ArmReadinessError(
            "readiness_schema_invalid", "freeze status and refusals disagree"
        )
    _validate_supersedes(receipt["supersedes"])
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_arm_context(value: object) -> Mapping[str, Any]:
    context = _require_exact_keys(value, ARM_CONTEXT_KEYS, "arm_context")
    for name in ("bracket_session_id", "pre_attempt_id", "post_attempt_id"):
        _require_path_component(context[name], f"arm_context.{name}")
    if context["clock_route"] not in {"MANUAL", "HELPER"}:
        raise ArmReadinessError(
            "readiness_usage_invalid", "arm_context.clock_route must be MANUAL or HELPER"
        )
    for name in ARM_CONTEXT_KEYS - {
        "bracket_session_id",
        "pre_attempt_id",
        "post_attempt_id",
        "clock_route",
    }:
        path = _require_string(context[name], f"arm_context.{name}")
        if not Path(path).is_absolute():
            raise ArmReadinessError(
                "readiness_root_binding_invalid", f"arm_context.{name} must be absolute"
            )
    return context


def validate_arm_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, ARM_RECEIPT_KEYS, "arm receipt")
    if receipt["schema_version"] != ARM_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "arm receipt schema is invalid"
        )
    if receipt["receipt_kind"] != "arm" or receipt["mode"] != "arm":
        raise ArmReadinessError(
            "readiness_receipt_kind_invalid", "arm receipt kind/mode is invalid"
        )
    if receipt["status"] not in RECEIPT_STATUSES or receipt["arm_disposition"] not in {"GO", "NO_GO"}:
        raise ArmReadinessError(
            "readiness_schema_invalid", "arm receipt status/disposition is invalid"
        )
    if (receipt["status"], receipt["arm_disposition"]) not in {
        ("PASS", "GO"),
        ("REFUSE", "NO_GO"),
    }:
        raise ArmReadinessError(
            "readiness_schema_invalid", "arm status and disposition disagree"
        )
    for name in ("receipt_id", "issued_at_utc"):
        _require_string(receipt[name], f"arm receipt.{name}")
    _require_boot_session_id(receipt["boot_session_id"], "arm receipt.boot_session_id")
    _require_int(
        receipt["valid_until_monotonic_ns"],
        "arm receipt.valid_until_monotonic_ns",
        minimum=1,
    )
    _validate_pack(receipt["pack"], "arm receipt.pack")
    reviewed = _require_exact_keys(receipt["reviewed_main"], REVIEWED_MAIN_KEYS, "reviewed_main")
    for name in ("head_commit", "head_tree_oid", "local_main_commit", "origin_main_commit"):
        _require_lower_git_oid(reviewed[name], f"reviewed_main.{name}")
    if not isinstance(reviewed["clean"], bool) or not isinstance(reviewed["exact_match"], bool):
        raise ArmReadinessError(
            "readiness_schema_invalid", "reviewed_main booleans are invalid"
        )
    validate_arm_context(receipt["arm_context"])
    freeze = _require_exact_keys(receipt["freeze_receipt"], FREEZE_REFERENCE_KEYS, "freeze_receipt")
    _require_string(freeze["receipt_id"], "freeze_receipt.receipt_id")
    _require_relative_path(freeze["path"], "freeze_receipt.path")
    _require_lower_sha256(freeze["sha256"], "freeze_receipt.sha256")
    _validate_row_registry_reference(receipt["row_registry"], "arm receipt.row_registry")
    _validate_rows_and_refusals(receipt)
    if (receipt["status"] == "PASS") == bool(receipt["refusals"]):
        raise ArmReadinessError(
            "readiness_schema_invalid", "arm status and refusals disagree"
        )
    _validate_supersedes(receipt["supersedes"])
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_dry_run_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, DRY_RUN_RECEIPT_KEYS, "dry-run receipt")
    if receipt["schema_version"] != DRY_RUN_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run receipt schema is invalid"
        )
    if receipt["receipt_kind"] != "dry_run" or receipt["mode"] != "dry_run":
        raise ArmReadinessError(
            "readiness_receipt_kind_invalid", "dry-run kind/mode is invalid"
        )
    if receipt["status"] not in RECEIPT_STATUSES or receipt["arm_disposition"] != "NOT_APPLICABLE":
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run status/disposition is invalid"
        )
    for name in ("receipt_id", "issued_at_utc"):
        _require_string(receipt[name], f"dry-run receipt.{name}")
    _validate_pack(receipt["pack"], "dry-run receipt.pack")
    synthetic = _require_exact_keys(
        receipt["synthetic_context"], SYNTHETIC_CONTEXT_KEYS, "synthetic_context"
    )
    for name in SYNTHETIC_CONTEXT_KEYS:
        _require_string(synthetic[name], f"synthetic_context.{name}")
    if not Path(synthetic["root"]).is_absolute() or not Path(synthetic["ledger_path"]).is_absolute():
        raise ArmReadinessError(
            "readiness_schema_invalid", "synthetic paths must be absolute"
        )
    if not isinstance(receipt["evidence"], list) or not isinstance(receipt["checks"], list):
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run evidence/checks must be arrays"
        )
    for index, item in enumerate(receipt["evidence"]):
        _validate_evidence_item(item, f"evidence[{index}]")
    for index, raw_check in enumerate(receipt["checks"]):
        check = _require_exact_keys(raw_check, DRY_RUN_CHECK_KEYS, f"checks[{index}]")
        _require_string(check["check_id"], f"checks[{index}].check_id")
        if check["status"] not in RECEIPT_STATUSES:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"checks[{index}].status is invalid"
            )
        for name in ("command_sha256", "stdout_sha256", "stderr_sha256"):
            _require_lower_sha256(check[name], f"checks[{index}].{name}")
        _require_int(check["exit_code"], f"checks[{index}].exit_code")
    if receipt["omitted_live_domains"] != list(SYNTHETIC_DOMAINS):
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run omitted_live_domains is not the closed list"
        )
    if not isinstance(receipt["refusals"], list):
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run refusals must be an array"
        )
    for index, refusal in enumerate(receipt["refusals"]):
        _validate_refusal(refusal, f"refusals[{index}]")
    if (receipt["status"] == "PASS") == bool(receipt["refusals"]):
        raise ArmReadinessError(
            "readiness_schema_invalid", "dry-run status and refusals disagree"
        )
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_consumption_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(value, CONSUMPTION_RECEIPT_KEYS, "consumption receipt")
    if receipt["schema_version"] != CONSUMPTION_RECEIPT_SCHEMA or receipt["receipt_kind"] != "launch_consumption":
        raise ArmReadinessError(
            "readiness_receipt_kind_invalid", "consumption receipt kind is invalid"
        )
    _require_string(receipt["consumed_at_utc"], "consumption receipt.consumed_at_utc")
    arm = _require_exact_keys(receipt["arm_receipt"], FREEZE_REFERENCE_KEYS, "arm_receipt")
    _require_string(arm["receipt_id"], "arm_receipt.receipt_id")
    _require_relative_path(arm["path"], "arm_receipt.path")
    _require_lower_sha256(arm["sha256"], "arm_receipt.sha256")
    _require_lower_sha256(receipt["pack_sha256"], "consumption receipt.pack_sha256")
    _require_lower_git_oid(receipt["head_commit"], "consumption receipt.head_commit")
    if not isinstance(receipt["volatile_checks"], list) or receipt["volatile_checks"] != sorted(set(receipt["volatile_checks"])):
        raise ArmReadinessError(
            "readiness_schema_invalid", "volatile_checks must be sorted and unique"
        )
    _validate_assurance(receipt["assurance"])
    return receipt


def load_registry(repository_root: Path | str) -> tuple[Mapping[str, Any], bytes]:
    path = Path(repository_root) / ROW_REGISTRY_RELATIVE_PATH
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", f"cannot read row registry: {exc}"
        ) from exc
    value = parse_json_bytes(raw, require_canonical=True)
    return validate_registry(value), raw


def _run_git(root: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ("git", "-C", str(root), *args),
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ArmReadinessError(
            "readiness_pack_not_committed", f"cannot execute Git proof: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ArmReadinessError(
            "readiness_pack_not_committed", f"Git proof failed: {detail}"
        )
    return completed.stdout


def _repository_and_pack_relative(pack_root: Path) -> tuple[Path, bytes, str]:
    root = pack_root.resolve(strict=True)
    repo_raw = _run_git(root, "rev-parse", "--show-toplevel").rstrip(b"\n")
    try:
        repo = Path(repo_raw.decode("utf-8", errors="strict")).resolve(strict=True)
        relative = root.relative_to(repo).as_posix()
    except (UnicodeDecodeError, OSError, ValueError) as exc:
        raise ArmReadinessError(
            "readiness_pack_not_committed", "pack root is not below a UTF-8 Git worktree"
        ) from exc
    return repo, relative.encode("utf-8"), relative


def committed_pack_tree_sha256(pack_root: Path | str) -> str:
    """Hash every committed pack blob using D-134's exact framing."""

    root = Path(pack_root)
    try:
        repository, pack_prefix, pack_relative = _repository_and_pack_relative(root)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"pack root is unreadable: {exc}"
        ) from exc
    tree_raw = _run_git(repository, "ls-tree", "-rz", "--full-tree", "HEAD", "--", pack_relative)
    committed: dict[bytes, tuple[str, str]] = {}
    prefix = pack_prefix + b"/"
    for record in tree_raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, repository_path = record.split(b"\t", 1)
            mode_raw, object_type_raw, oid_raw = metadata.split(b" ", 2)
        except ValueError as exc:
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous", "malformed Git tree entry"
            ) from exc
        if not repository_path.startswith(prefix):
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous", "Git returned an out-of-pack path"
            )
        relative_raw = repository_path[len(prefix) :]
        try:
            relative_raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous", "pack contains a non-UTF-8 path"
            ) from exc
        mode = mode_raw.decode("ascii", errors="strict")
        object_type = object_type_raw.decode("ascii", errors="strict")
        oid = oid_raw.decode("ascii", errors="strict")
        if mode not in {"100644", "100755"} or object_type != "blob":
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous",
                f"inadmissible Git mode/type for {relative_raw!r}",
            )
        if relative_raw in committed:
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous", "duplicate committed pack path"
            )
        committed[relative_raw] = (mode, oid)
    if not committed:
        raise ArmReadinessError(
            "readiness_pack_not_committed", "pack contains no committed files"
        )

    disk: dict[bytes, Path] = {}
    disk_directories: set[bytes] = set()
    try:
        for path in root.rglob("*"):
            relative = path.relative_to(root).as_posix().encode("utf-8", errors="strict")
            status = path.lstat()
            if stat.S_ISLNK(status.st_mode):
                raise ArmReadinessError(
                    "readiness_pack_namespace_anomalous", f"pack symlink is forbidden: {path}"
                )
            if stat.S_ISREG(status.st_mode):
                disk[relative] = path
            elif stat.S_ISDIR(status.st_mode):
                disk_directories.add(relative)
            else:
                raise ArmReadinessError(
                    "readiness_pack_namespace_anomalous", f"special pack entry is forbidden: {path}"
                )
    except ArmReadinessError:
        raise
    except (OSError, UnicodeEncodeError) as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"cannot inventory pack bytes: {exc}"
        ) from exc
    committed_paths = set(committed)
    disk_paths = set(disk)
    committed_directories = {
        b"/".join(relative.split(b"/")[:index])
        for relative in committed_paths
        for index in range(1, len(relative.split(b"/")))
    }
    if disk_directories - committed_directories:
        extra_directory = min(disk_directories - committed_directories)
        raise ArmReadinessError(
            "readiness_pack_not_committed",
            f"untracked pack directory: {extra_directory!r}",
        )
    if disk_paths - committed_paths:
        extra = min(disk_paths - committed_paths)
        raise ArmReadinessError(
            "readiness_pack_not_committed", f"untracked pack entry: {extra!r}"
        )
    if committed_paths - disk_paths:
        missing = min(committed_paths - disk_paths)
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"committed pack entry is missing: {missing!r}"
        )
    framed = bytearray(PACK_DIGEST_DOMAIN)
    for relative_raw in sorted(committed, key=lambda value: value):
        mode, oid = committed[relative_raw]
        path = disk[relative_raw]
        try:
            raw = path.read_bytes()
            blob = _run_git(repository, "cat-file", "blob", oid)
            disk_mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        except OSError as exc:
            raise ArmReadinessError(
                "readiness_pack_unreadable", f"cannot authenticate pack file {path}: {exc}"
            ) from exc
        if raw != blob or disk_mode != mode:
            raise ArmReadinessError(
                "readiness_pack_digest_mismatch",
                f"disk and committed bytes/mode differ for {relative_raw!r}",
            )
        framed.extend(relative_raw)
        framed.extend(b"\0")
        framed.extend(mode.encode("ascii"))
        framed.extend(b"\0")
        framed.extend(str(len(raw)).encode("ascii"))
        framed.extend(b"\0")
        framed.extend(sha256_bytes(raw).encode("ascii"))
        framed.extend(b"\n")
    return sha256_bytes(bytes(framed))


def _plan_profile(pack_root: Path) -> str:
    try:
        return _PROFILE_BY_PACK[pack_root.name]
    except KeyError as exc:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", f"no D-134 profile for {pack_root.name}"
        ) from exc


def _plan_tree(pack_root: Path) -> tuple[dict[str, Any], bytes]:
    path = pack_root / "plan_tree.json"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"cannot read plan tree: {exc}"
        ) from exc
    value = parse_json_bytes(raw)
    if not isinstance(value, dict):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan_tree.json must contain an object"
        )
    sidecar_path = pack_root / "plan_tree.sha256"
    try:
        sidecar = sidecar_path.read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"cannot read plan-tree sidecar: {exc}"
        ) from exc
    expected = gnu_sidecar(sha256_bytes(raw), "plan_tree.json")
    if sidecar != expected:
        raise ArmReadinessError(
            "readiness_pack_digest_mismatch", "plan-tree sidecar does not authenticate exact bytes"
        )
    return value, raw


def _repo_for_pack(pack_root: Path) -> Path:
    repository, _prefix, _relative = _repository_and_pack_relative(pack_root)
    return repository


def _registry_reference(pack_root: Path) -> tuple[Mapping[str, Any], bytes, dict[str, str]]:
    repository = _repo_for_pack(pack_root)
    registry, raw = load_registry(repository)
    committed_raw = _git_blob_at_head(
        repository, ROW_REGISTRY_RELATIVE_PATH.as_posix()
    )
    if committed_raw != raw:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "row registry bytes are not the committed HEAD bytes",
        )
    profile = _plan_profile(pack_root)
    reference = {
        "registry_id": registry["registry_id"],
        "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
        "sha256": sha256_bytes(raw),
        "plan_profile": profile,
    }
    return registry, raw, reference


def _valid_plan_attachment(value: object, expected: Mapping[str, Any]) -> None:
    keys = {
        "contract_id",
        "required_before_arm",
        "row_registry",
        "freeze_receipt",
        "arm_receipt_namespace",
        "pack_digest_algorithm",
    }
    item = _require_exact_keys(value, keys, "arm_attachments.arm_readiness")
    if (
        item["contract_id"] != CONTRACT_ID
        or item["required_before_arm"] is not True
        or item["row_registry"] != expected
        or item["arm_receipt_namespace"] != "arm_readiness.receipts/arm-<4+ digits>.json"
        or item["pack_digest_algorithm"] != PACK_DIGEST_ALGORITHM
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "plan arm-readiness declaration differs from D-134"
        )
    if item["freeze_receipt"] is not None:
        freeze = _require_exact_keys(item["freeze_receipt"], {"path", "sha256"}, "plan freeze_receipt")
        _require_relative_path(freeze["path"], "plan freeze_receipt.path")
        _require_lower_sha256(freeze["sha256"], "plan freeze_receipt.sha256")


def plan_arm_readiness_attachment(
    pack_root: Path | str,
    plan_profile: str,
    repository_root: Path | str,
) -> dict[str, Any]:
    """Build the generator-owned declaration and derive any freeze reference."""

    if plan_profile not in WINDOW_KINDS:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "unknown plan profile"
        )
    registry, raw = load_registry(repository_root)
    receipts = scan_receipt_namespace(
        Path(pack_root) / "arm_readiness.freeze.receipts", "freeze", allow_absent=True
    )
    freeze_reference: dict[str, str] | None = None
    committed_receipts: list[dict[str, Any]] = []
    if receipts:
        pack = Path(pack_root).resolve(strict=True)
        repository, _prefix, pack_relative = _repository_and_pack_relative(pack)
        for item in receipts:
            relative_json = (
                f"{pack_relative}/arm_readiness.freeze.receipts/{item['path'].name}"
            )
            relative_sidecar = f"{relative_json}.sha256"
            json_at_head = _git_blob_at_head(repository, relative_json)
            sidecar_at_head = _git_blob_at_head(repository, relative_sidecar)
            if json_at_head is None and sidecar_at_head is None:
                continue
            if (
                json_at_head != item["raw"]
                or sidecar_at_head
                != gnu_sidecar(item["sha256"], item["path"].name)
            ):
                raise ArmReadinessError(
                    "readiness_freeze_receipt_mismatch",
                    "committed freeze receipt differs from working-tree bytes",
                )
            committed_receipts.append(item)
    if committed_receipts:
        latest = committed_receipts[-1]
        freeze_reference = {
            "path": f"arm_readiness.freeze.receipts/{latest['path'].name}",
            "sha256": latest["sha256"],
        }
    return {
        "contract_id": CONTRACT_ID,
        "required_before_arm": True,
        "row_registry": {
            "registry_id": registry["registry_id"],
            "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "sha256": sha256_bytes(raw),
            "plan_profile": plan_profile,
        },
        "freeze_receipt": freeze_reference,
        "arm_receipt_namespace": "arm_readiness.receipts/arm-<4+ digits>.json",
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
    }


def _git_blob_at_head(repository: Path, relative_path: str) -> bytes | None:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repository), "show", f"HEAD:{relative_path}"),
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ArmReadinessError(
            "readiness_pack_not_committed",
            f"cannot authenticate committed receipt: {exc}",
        ) from exc
    if completed.returncode != 0:
        return None
    return completed.stdout


def scan_receipt_namespace(
    namespace: Path | str, kind: str, *, allow_absent: bool = False
) -> list[dict[str, Any]]:
    """Authenticate a governed append-only namespace without skipping entries."""

    if kind not in _RECEIPT_NAME_RE:
        raise ArmReadinessError(
            "readiness_internal_error", f"unknown namespace kind {kind!r}"
        )
    root = Path(namespace)
    if not root.exists():
        if allow_absent:
            return []
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous", f"missing {kind} receipt namespace"
        )
    if root.is_symlink() or not root.is_dir():
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous",
            f"{kind} receipt namespace is not a real directory",
        )
    try:
        entries = sorted(root.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous", f"cannot scan receipt namespace: {exc}"
        ) from exc
    json_by_stem: dict[str, Path] = {}
    sidecar_by_stem: dict[str, Path] = {}
    numbers: set[int] = set()
    for path in entries:
        if not path.is_file() or path.is_symlink():
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", f"non-file namespace entry {path.name}"
            )
        if path.name.endswith(".sha256"):
            stem = path.name[: -len(".sha256")]
            if stem in sidecar_by_stem:
                raise ArmReadinessError(
                    "readiness_receipt_namespace_anomalous", "duplicate receipt sidecar"
                )
            sidecar_by_stem[stem] = path
            continue
        match = _RECEIPT_NAME_RE[kind].fullmatch(path.name)
        if match is None:
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", f"malformed receipt name {path.name}"
            )
        number = int(match.group(1))
        if number < 1 or number in numbers:
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", "duplicate/nonpositive receipt number"
            )
        numbers.add(number)
        json_by_stem[path.name] = path
    if set(json_by_stem) != set(sidecar_by_stem):
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous", "receipt/sidecar namespace is unpaired"
        )
    result: list[dict[str, Any]] = []
    receipt_ids: set[str] = set()
    for filename, path in json_by_stem.items():
        try:
            raw = path.read_bytes()
            digest = sha256_bytes(raw)
            sidecar = sidecar_by_stem[filename].read_bytes()
        except OSError as exc:
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", f"cannot read namespace entry: {exc}"
            ) from exc
        if sidecar != gnu_sidecar(digest, filename):
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", f"sidecar mismatch for {filename}"
            )
        value = parse_json_bytes(raw, require_canonical=True)
        validated = (
            validate_freeze_receipt(value)
            if kind == "freeze"
            else validate_arm_receipt(value)
            if kind == "arm"
            else validate_dry_run_receipt(value)
        )
        receipt_id = str(validated["receipt_id"])
        expected_receipt_id = filename.removesuffix(".json")
        if receipt_id != expected_receipt_id:
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous",
                f"receipt_id does not match governed filename {filename}",
            )
        if receipt_id in receipt_ids:
            raise ArmReadinessError(
                "readiness_receipt_namespace_anomalous", "duplicate semantic receipt_id"
            )
        receipt_ids.add(receipt_id)
        number = int(_RECEIPT_NAME_RE[kind].fullmatch(filename).group(1))  # type: ignore[union-attr]
        result.append(
            {
                "number": number,
                "path": path,
                "sha256": digest,
                "raw": raw,
                "receipt": validated,
            }
        )
    result.sort(key=lambda item: item["number"])
    if kind == "arm":
        for prior, successor in zip(result, result[1:]):
            expected_supersedes = {
                "receipt_id": prior["receipt"]["receipt_id"],
                "receipt_path": f"arm_readiness.receipts/{prior['path'].name}",
                "receipt_sha256": prior["sha256"],
                "pack_id": prior["receipt"]["pack"]["pack_id"],
                "pack_sha256": prior["receipt"]["pack"]["pack_sha256"],
            }
            if successor["receipt"]["supersedes"] != expected_supersedes:
                raise ArmReadinessError(
                    "readiness_receipt_namespace_anomalous",
                    "arm receipt does not semantically supersede its predecessor",
                )
    return result


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _exclusive_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise ArmReadinessError(
            "readiness_output_collision", f"refusing to overwrite {path}"
        ) from exc
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_io_error", f"cannot create {path}: {exc}"
        ) from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        raise


def _atomic_replace(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def _receipt_refusal(
    code: str, *, row_id: str | None = None, evidence_id: str | None = None
) -> dict[str, Any]:
    if code not in READINESS_REASON_CODES:
        raise ArmReadinessError(
            "readiness_internal_error", f"attempted to emit unregistered refusal {code}"
        )
    return {
        "type": REASON_TYPE_BY_CODE[code],
        "code": code,
        "row_id": row_id,
        "evidence_id": evidence_id,
    }


def _git_text(repository: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repository), *args),
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def reviewed_main(pack_root: Path | str) -> dict[str, Any]:
    root = Path(pack_root)
    repository = _repo_for_pack(root)
    head = _git_text(repository, "rev-parse", "HEAD") or "unavailable"
    tree = _git_text(repository, "rev-parse", "HEAD^{tree}") or "unavailable"
    local_main = _git_text(repository, "rev-parse", "refs/heads/main") or "unavailable"
    origin_main = _git_text(repository, "rev-parse", "refs/remotes/origin/main") or "unavailable"
    status_raw = _git_text(
        repository,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    clean = status_raw == ""
    exact = clean and head == local_main == origin_main and head != "unavailable"
    return {
        "head_commit": head,
        "head_tree_oid": tree,
        "local_main_commit": local_main,
        "origin_main_commit": origin_main,
        "clean": clean,
        "exact_match": exact,
    }


def _pack_record(pack_root: Path) -> dict[str, Any]:
    tree, tree_raw = _plan_tree(pack_root)
    plan = tree.get("plan")
    window = tree.get("window_identity")
    if not isinstance(plan, Mapping) or not isinstance(window, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan tree omits plan/window identity"
        )
    plan_id = _require_string(plan.get("plan_id"), "plan.plan_id")
    window_id = _require_string(window.get("window_id"), "window_identity.window_id")
    sidecar_raw = (pack_root / "plan_tree.sha256").read_bytes()
    return {
        "pack_id": pack_root.name,
        "plan_id": plan_id,
        "window_id": window_id,
        "pack_root": str(pack_root.resolve()),
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
        "pack_sha256": committed_pack_tree_sha256(pack_root),
        "plan_tree_path": "plan_tree.json",
        "plan_tree_sha256": sha256_bytes(tree_raw),
        "plan_tree_sidecar_path": "plan_tree.sha256",
        "plan_tree_sidecar_sha256": sha256_bytes(sidecar_raw),
    }


def _pack_identity(pack_root: Path, tree: Mapping[str, Any]) -> dict[str, Any]:
    plan = tree.get("plan")
    window = tree.get("window_identity")
    if not isinstance(plan, Mapping) or not isinstance(window, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan tree omits plan/window identity"
        )
    plan_path_value = plan.get("path")
    if not isinstance(plan_path_value, str):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan path is invalid"
        )
    plan_path = PurePosixPath(plan_path_value).name
    raw = (pack_root / plan_path).read_bytes()
    return {
        "pack_id": pack_root.name,
        "plan_id": _require_string(plan.get("plan_id"), "plan.plan_id"),
        "window_id": _require_string(window.get("window_id"), "window_identity.window_id"),
        "pack_root": str(pack_root.resolve()),
        "plan_path": plan_path,
        "plan_sha256": sha256_bytes(raw),
    }


def _profile_rows(
    registry: Mapping[str, Any], profile: str, *, phase: str
) -> list[Mapping[str, Any]]:
    required = next(
        item["required_row_ids"]
        for item in registry["plan_profiles"]
        if item["profile_id"] == profile
    )
    by_id = {row["row_id"]: row for row in registry["rows"]}
    rows = [by_id[row_id] for row_id in required]
    if phase == "freeze":
        rows = [row for row in rows if row["evaluation_phase"] == "FREEZE_AND_ARM"]
    return rows


def _validate_profile_rows(
    receipt: Mapping[str, Any],
    definitions: Sequence[Mapping[str, Any]],
    *,
    clock_route: str,
    successor_acceptance: bool,
) -> None:
    rows = receipt["rows"]
    expected_ids = [definition["row_id"] for definition in definitions]
    if [row["row_id"] for row in rows] != expected_ids:
        raise ArmReadinessError(
            "readiness_row_set_incomplete",
            "receipt row set differs from the authoritative profile",
        )
    for row, definition in zip(rows, definitions, strict=True):
        expected_applicability = applicability_for_row(
            definition,
            clock_route=clock_route,
            successor_acceptance=successor_acceptance,
        )
        if (
            row["evaluation_phase"] != definition["evaluation_phase"]
            or row["predicate_id"] != definition["predicate_id"]
            or row["applicability"] != expected_applicability
        ):
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"row {definition['row_id']} differs from the authoritative registry",
                row_id=str(definition["row_id"]),
            )


def _identity_projection_pseudo_receipt(
    *, status: str, reason_codes: Sequence[str]
) -> dict[str, Any]:
    return {
        "kind": "IDENTITY_PIN_PROJECTION",
        "status": status,
        "facts": (
            [
                {
                    "fact_id": "desk.identity_pin_projection.v1",
                    "value_type": "OBJECT",
                    "value": {"projection_status": "PASS"},
                }
            ]
            if status == "PASS"
            else []
        ),
        "checks": [],
        "reason_codes": list(reason_codes),
    }


def _read_identity_projection_receipt(
    path: Path,
    expected_sha256: str,
    *,
    namespace_root: Path | None = None,
) -> tuple[Mapping[str, Any], bytes]:
    if namespace_root is not None:
        try:
            resolved_root = namespace_root.resolve(strict=True)
            for candidate in (path, path.with_suffix(".sha256")):
                mode = candidate.lstat().st_mode
                if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                    raise OSError(f"non-regular identity evidence path: {candidate}")
                candidate.resolve(strict=True).relative_to(resolved_root)
        except (OSError, ValueError) as exc:
            raise ArmReadinessError(
                "readiness_identity_artifact_unreadable",
                "identity projection receipt escaped or violated its namespace",
            ) from exc
    try:
        raw = path.read_bytes()
        sidecar = path.with_suffix(".sha256").read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_identity_artifact_unreadable",
            f"cannot read identity projection receipt: {exc}",
        ) from exc
    digest = sha256_bytes(raw)
    if digest != expected_sha256 or sidecar != gnu_sidecar(digest, path.name):
        raise ArmReadinessError(
            "readiness_identity_pinset_frozen_mismatch",
            "identity projection receipt digest differs from its binding",
        )
    try:
        receipt = validate_projection_receipt(
            parse_json_bytes(raw, require_canonical=True)
        )
    except IdentityPinProjectionError as exc:
        raise ArmReadinessError(exc.reason_code, str(exc)) from exc
    return receipt, raw


def _load_frozen_identity_evidence(
    pack_root: Path, tree: Mapping[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    try:
        attachments = tree.get("arm_attachments")
        raw_projection = (
            attachments.get("identity_pin_projection")
            if isinstance(attachments, Mapping)
            else None
        )
        try:
            projection = validate_identity_pin_projection(raw_projection)
        except IdentityPinProjectionError as exc:
            raise ArmReadinessError(exc.reason_code, str(exc)) from exc
        if projection["state"] != "frozen" or projection["projection_receipt"] is None:
            raise ArmReadinessError(
                "readiness_identity_pinset_frozen_mismatch",
                "identity projection is not frozen",
            )
        reference = projection["projection_receipt"]
        relative = _require_relative_path(
            reference["path"], "identity projection receipt path"
        )
        expected_sha = _require_lower_sha256(
            reference["sha256"], "identity projection receipt sha256"
        )
        path = pack_root / relative
        receipt, _raw = _read_identity_projection_receipt(
            path,
            expected_sha,
            namespace_root=pack_root,
        )
        plan = tree.get("plan")
        window = tree.get("window_identity")
        if (
            not isinstance(plan, Mapping)
            or not isinstance(window, Mapping)
            or receipt["pack"]["pack_id"] != pack_root.name
            or receipt["pack"]["plan_id"] != plan.get("plan_id")
            or receipt["pack"]["window_id"] != window.get("window_id")
            or [unit["identity_unit_id"] for unit in receipt["identity_units"]]
            != [unit["identity_unit_id"] for unit in projection["identity_units"]]
            or [unit["model_runtime_config"] for unit in receipt["identity_units"]]
            != [unit["model_runtime_config"] for unit in projection["identity_units"]]
        ):
            raise ArmReadinessError(
                "readiness_identity_pinset_frozen_mismatch",
                "identity projection receipt differs from the frozen plan",
            )
        if receipt["status"] != "PASS":
            return None, None, list(receipt["reason_codes"])
        evidence_id = "u11-freeze-projection"
        item = {
            "evidence_id": evidence_id,
            "receipt_kind": str(receipt["receipt_kind"]),
            "namespace": "PACK",
            "path": relative,
            "sha256": expected_sha,
            "schema_version": IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
            "status": "PASS",
        }
        return (
            item,
            _identity_projection_pseudo_receipt(status="PASS", reason_codes=[]),
            [],
        )
    except ArmReadinessError as exc:
        return None, None, [exc.reason_code]


def _run_identity_arm_reverification(
    pack_root: Path,
    custody_root: Path,
    bracket_session_id: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    try:
        result = verify_frozen_projection(
            pack_root, custody_root, bracket_session_id
        )
        path = Path(str(result["receipt_path"])).resolve(strict=True)
        custody_pack_root = (custody_root / pack_root.name).resolve()
        try:
            relative = path.relative_to(custody_pack_root).as_posix()
        except ValueError as exc:
            raise ArmReadinessError(
                "readiness_identity_artifact_unreadable",
                "identity arm receipt escaped window custody",
            ) from exc
        expected_sha = _require_lower_sha256(
            result["receipt_sha256"], "identity arm receipt sha256"
        )
        receipt, _raw = _read_identity_projection_receipt(
            path,
            expected_sha,
            namespace_root=custody_pack_root,
        )
        status = str(receipt["status"])
        reasons = list(receipt["reason_codes"])
        evidence_id = "u11-arm-reverification"
        item = {
            "evidence_id": evidence_id,
            "receipt_kind": str(receipt["receipt_kind"]),
            "namespace": "WINDOW_CUSTODY",
            "path": relative,
            "sha256": expected_sha,
            "schema_version": IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
            "status": status,
        }
        return (
            item,
            _identity_projection_pseudo_receipt(
                status=status, reason_codes=reasons
            ),
            reasons,
        )
    except IdentityPinProjectionError as exc:
        return None, None, [exc.reason_code]
    except ArmReadinessError as exc:
        return None, None, [exc.reason_code]


def _authenticate_identity_arm_evidence(
    item: Mapping[str, Any],
    custody_pack_root: Path,
    pack_root: Path,
    reviewed: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if (
        item["evidence_id"] != "u11-arm-reverification"
        or item["namespace"] != "WINDOW_CUSTODY"
        or item["schema_version"] != IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA
    ):
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "arm identity evidence binding is not the D-131 binding",
        )
    path = custody_pack_root / _require_relative_path(
        item["path"], "arm identity evidence path"
    )
    expected_sha = _require_lower_sha256(
        item["sha256"], "arm identity evidence sha256"
    )
    receipt, _raw = _read_identity_projection_receipt(
        path,
        expected_sha,
        namespace_root=custody_pack_root,
    )
    if (
        item["receipt_kind"] != receipt["receipt_kind"]
        or item["status"] != receipt["status"]
    ):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "arm identity evidence metadata differs from authenticated bytes",
        )
    tree, _tree_raw = _plan_tree(pack_root)
    attachments = tree.get("arm_attachments")
    raw_projection = (
        attachments.get("identity_pin_projection")
        if isinstance(attachments, Mapping)
        else None
    )
    try:
        projection = validate_identity_pin_projection(raw_projection)
    except IdentityPinProjectionError as exc:
        raise ArmReadinessError(exc.reason_code, str(exc)) from exc
    plan = tree.get("plan")
    window = tree.get("window_identity")
    if (
        not isinstance(plan, Mapping)
        or not isinstance(window, Mapping)
        or receipt["pack"]["pack_id"] != pack_root.name
        or receipt["pack"]["plan_id"] != plan.get("plan_id")
        or receipt["pack"]["window_id"] != window.get("window_id")
        or receipt["pack"]["reviewed_git_commit"] != reviewed["head_commit"]
        or [unit["identity_unit_id"] for unit in receipt["identity_units"]]
        != [unit["identity_unit_id"] for unit in projection["identity_units"]]
    ):
        raise ArmReadinessError(
            "readiness_identity_environment_dirty",
            "arm identity evidence differs from the bound pack or HEAD",
        )
    reasons = list(receipt["reason_codes"])
    return (
        _identity_projection_pseudo_receipt(
            status=str(receipt["status"]), reason_codes=reasons
        ),
        reasons,
    )


def applicability_for_row(
    row: Mapping[str, Any], *, clock_route: str, successor_acceptance: bool
) -> str:
    rule = row["applicability_rule"]
    if rule == "ALWAYS":
        return "REQUIRED"
    if rule == "CLOCK_HELPER_ONLY":
        return "REQUIRED" if clock_route == "HELPER" else "NOT_APPLICABLE"
    if rule == "SUCCESSOR_ACCEPTANCE_ONLY":
        return "REQUIRED" if successor_acceptance else "NOT_APPLICABLE"
    raise ArmReadinessError(
        "readiness_row_applicability_invalid", f"unknown applicability rule {rule!r}"
    )


def _issued_d079(tree: Mapping[str, Any]) -> bool:
    policy = tree.get("acceptance_policy")
    if not isinstance(policy, Mapping):
        return False
    if policy.get("selection") != "issued_d116_artifact_only":
        return False
    issued = policy.get("issued")
    nested = policy.get("issued_acceptance")
    if issued is None and isinstance(nested, Mapping):
        issued = nested.get("acceptance_id")
    if issued is None:
        issued = policy.get("issued_artifact_id")
    return issued in {"d079", "d079_calibration_acceptance_v2_n19"}


def _evidence_directories(pack_root: Path, custody_pack_root: Path) -> tuple[tuple[str, Path], ...]:
    if pack_root.resolve() == custody_pack_root.resolve():
        return (("PACK", pack_root / "arm_readiness.evidence"),)
    return (
        ("PACK", pack_root / "arm_readiness.evidence"),
        ("WINDOW_CUSTODY", custody_pack_root / "arm_readiness.evidence"),
    )


def _authenticate_generic_evidence_item(
    item: Mapping[str, Any],
    pack_root: Path,
    custody_pack_root: Path,
    *,
    expected_pack_sha256: str | None = None,
    expected_head_commit: str | None = None,
    expected_boot_session_id: str | None = None,
    now_monotonic_ns: int | None = None,
) -> Mapping[str, Any]:
    _validate_evidence_item(item, "evidence item")
    if item["schema_version"] != EVIDENCE_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "generic evidence item names a non-generic schema",
        )
    namespace_root = (
        pack_root if item["namespace"] == "PACK" else custody_pack_root
    )
    path = _resolve_namespace_path(
        namespace_root,
        item["path"],
        "evidence item.path",
    )
    try:
        raw = path.read_bytes()
        sidecar = path.with_name(f"{path.name}.sha256").read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable", f"cannot read evidence item: {exc}"
        ) from exc
    digest = sha256_bytes(raw)
    if digest != item["sha256"] or sidecar != gnu_sidecar(digest, path.name):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "evidence item digest differs from authenticated bytes",
        )
    receipt = validate_evidence_receipt(
        parse_json_bytes(raw, require_canonical=True)
    )
    if receipt["kind"] in {"IDENTITY_PIN_PROJECTION", "DRY_RUN_REHEARSAL"}:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "specialized evidence must use its governing receipt schema",
        )
    if item != {
        "evidence_id": receipt["evidence_id"],
        "receipt_kind": receipt["kind"],
        "namespace": item["namespace"],
        "path": item["path"],
        "sha256": digest,
        "schema_version": receipt["schema_version"],
        "status": receipt["status"],
    }:
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "evidence item metadata differs from authenticated bytes",
        )
    if (
        expected_pack_sha256 is not None
        and receipt["pack_sha256"] != expected_pack_sha256
    ) or (
        expected_head_commit is not None
        and receipt["head_commit"] != expected_head_commit
    ):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "evidence item is stale for pack or HEAD",
        )
    if (
        expected_boot_session_id is not None
        and receipt["boot_session_id"] != expected_boot_session_id
    ):
        raise ArmReadinessError(
            "readiness_record_expired", "evidence item belongs to a prior boot session"
        )
    if (
        now_monotonic_ns is not None
        and receipt["valid_until_monotonic_ns"] < now_monotonic_ns
    ):
        raise ArmReadinessError(
            "readiness_record_expired", "evidence item expired"
        )
    for fact in receipt["facts"]:
        source_path = _resolve_namespace_path(
            namespace_root,
            fact["source_path"],
            "evidence fact source_path",
        )
        try:
            source_raw = source_path.read_bytes()
        except OSError as exc:
            raise ArmReadinessError(
                "readiness_evidence_unreadable",
                f"cannot read evidence fact source: {exc}",
            ) from exc
        if sha256_bytes(source_raw) != fact["source_sha256"]:
            raise ArmReadinessError(
                "readiness_evidence_digest_mismatch",
                "evidence fact source digest mismatch",
            )
    return receipt


def _discover_evidence(
    pack_root: Path,
    custody_pack_root: Path,
    *,
    pack_sha256: str | None,
    head_commit: str | None,
    boot_session_id: str | None,
    now_monotonic_ns: int | None,
    include_pack: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Mapping[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    receipts: dict[str, Mapping[str, Any]] = {}
    refusals: list[dict[str, Any]] = []
    directories = _evidence_directories(pack_root, custody_pack_root)
    if not include_pack:
        directories = tuple(item for item in directories if item[0] != "PACK")
    for namespace, directory in directories:
        if not directory.exists():
            continue
        if directory.is_symlink():
            refusals.append(
                _receipt_refusal("readiness_evidence_reference_invalid")
            )
            continue
        try:
            entries = sorted(directory.iterdir(), key=lambda path: path.name)
        except OSError:
            refusals.append(_receipt_refusal("readiness_evidence_unreadable"))
            continue
        if any(
            not (
                path.name.endswith(".json")
                or path.name.endswith(".json.sha256")
            )
            for path in entries
        ):
            refusals.append(_receipt_refusal("readiness_evidence_unreadable"))
            continue
        json_paths = {path.name: path for path in entries if path.name.endswith(".json")}
        sidecars = {
            path.name[: -len(".sha256")]: path
            for path in entries
            if path.name.endswith(".json.sha256")
        }
        if any(not path.is_file() or path.is_symlink() for path in entries) or set(json_paths) != set(sidecars):
            refusals.append(_receipt_refusal("readiness_evidence_unreadable"))
            continue
        for filename, path in json_paths.items():
            relative = f"arm_readiness.evidence/{filename}"
            receipt: Mapping[str, Any] | None = None
            try:
                raw = path.read_bytes()
                digest = sha256_bytes(raw)
                if sidecars[filename].read_bytes() != gnu_sidecar(digest, filename):
                    raise ArmReadinessError(
                        "readiness_evidence_digest_mismatch", "evidence sidecar mismatch"
                    )
                receipt = validate_evidence_receipt(
                    parse_json_bytes(raw, require_canonical=True)
                )
                if receipt["kind"] in {
                    "IDENTITY_PIN_PROJECTION",
                    "DRY_RUN_REHEARSAL",
                }:
                    raise ArmReadinessError(
                        "readiness_evidence_reference_invalid",
                        "specialized evidence must use its governing receipt schema",
                    )
                if (
                    (pack_sha256 is not None and receipt["pack_sha256"] != pack_sha256)
                    or (head_commit is not None and receipt["head_commit"] != head_commit)
                ):
                    raise ArmReadinessError(
                        "readiness_evidence_digest_mismatch", "evidence is stale for pack/HEAD"
                    )
                if (
                    boot_session_id is not None
                    and receipt["boot_session_id"] != boot_session_id
                ):
                    raise ArmReadinessError(
                        "readiness_record_expired",
                        "evidence receipt belongs to a prior boot session",
                    )
                if (
                    now_monotonic_ns is not None
                    and receipt["valid_until_monotonic_ns"] < now_monotonic_ns
                ):
                    raise ArmReadinessError(
                        "readiness_record_expired", "evidence receipt expired"
                    )
                if receipt["evidence_id"] in receipts:
                    raise ArmReadinessError(
                        "readiness_evidence_reference_invalid", "duplicate evidence ID"
                    )
                source_root = pack_root if namespace == "PACK" else custody_pack_root
                for fact in receipt["facts"]:
                    source_path = _resolve_namespace_path(
                        source_root,
                        fact["source_path"],
                        "evidence fact source_path",
                    )
                    try:
                        source_raw = source_path.read_bytes()
                    except OSError as exc:
                        raise ArmReadinessError(
                            "readiness_evidence_unreadable",
                            f"cannot read evidence fact source: {exc}",
                        ) from exc
                    if sha256_bytes(source_raw) != fact["source_sha256"]:
                        raise ArmReadinessError(
                            "readiness_evidence_digest_mismatch",
                            "evidence fact source digest mismatch",
                        )
                item = {
                    "evidence_id": receipt["evidence_id"],
                    "receipt_kind": receipt["kind"],
                    "namespace": namespace,
                    "path": relative,
                    "sha256": digest,
                    "schema_version": receipt["schema_version"],
                    "status": receipt["status"],
                }
                items.append(item)
                receipts[receipt["evidence_id"]] = receipt
            except ArmReadinessError as exc:
                refusals.append(
                    _receipt_refusal(
                        exc.reason_code,
                        evidence_id=(
                            receipt.get("evidence_id")
                            if isinstance(receipt, Mapping)
                            else None
                        ),
                    )
                )
            except OSError:
                refusals.append(_receipt_refusal("readiness_evidence_unreadable"))
    items.sort(key=lambda item: item["evidence_id"])
    return items, receipts, refusals


def _content_matches(value: object, required: object) -> bool:
    if required is _LOWER_SHA256_CONTENT:
        return isinstance(value, str) and _LOWER_SHA256_RE.fullmatch(value) is not None
    if isinstance(required, Mapping):
        return isinstance(value, Mapping) and all(
            key in value and _content_matches(value[key], expected)
            for key, expected in required.items()
        )
    return value == required


def _predicate_passes(receipt: Mapping[str, Any], predicate_id: str) -> bool:
    """Apply the D-134 row's content and source derivation predicate."""

    if receipt.get("status") != "PASS":
        return False
    expected_kind = _PREDICATE_EVIDENCE_KIND.get(predicate_id)
    required = _PREDICATE_CONTENT_REQUIREMENTS.get(predicate_id)
    if expected_kind is None or required is None or receipt.get("kind") != expected_kind:
        return False
    facts = receipt.get("facts")
    if not isinstance(facts, list):
        return False
    if expected_kind in {"IDENTITY_PIN_PROJECTION", "DRY_RUN_REHEARSAL"}:
        return any(
            isinstance(fact, Mapping)
            and fact.get("fact_id") == predicate_id
            and fact.get("value_type") == "OBJECT"
            and _content_matches(fact.get("value"), required)
            for fact in facts
        )
    admitted_sources = _EVIDENCE_SOURCE_KINDS[expected_kind]
    for fact in facts:
        if (
            not isinstance(fact, Mapping)
            or fact.get("fact_id") != predicate_id
            or fact.get("value_type") != "OBJECT"
            or fact.get("source_kind") not in admitted_sources
            or not _content_matches(fact.get("value"), required)
        ):
            continue
        value = fact["value"]
        if predicate_id == "t0.background_quiet.v1":
            source_kind = fact["source_kind"]
            if source_kind == "OPERATOR_ATTESTATION" and value.get(
                "closed_operator_observation"
            ) is not True:
                continue
            if source_kind == "PROBE" and value.get(
                "fresh_maintenance_census"
            ) is not True:
                continue
        return True
    return False


def _missing_row_code(row_id: str) -> str:
    if row_id == "desk.under_lease_rehearsal":
        return "readiness_dry_run_missing"
    if row_id == "desk.terminal_review":
        return "readiness_terminal_review_missing"
    if row_id == "desk.identity_pin_projection":
        return "readiness_identity_artifact_unreadable"
    if row_id.startswith("clock."):
        return "readiness_clock_preflight_refused"
    if row_id == "t0.storage_backup_capacity":
        return "readiness_backup_preflight_refused"
    if row_id in {"t0.machine_readiness", "t0.campaign_lock_absent"}:
        return "readiness_machine_preflight_refused"
    if row_id == "t0.ledger_reservation":
        return "readiness_ledger_preflight_refused"
    if row_id == "t0.single_launch_capability":
        return "readiness_launch_capability_unavailable"
    return "readiness_dependency_refused"


def _evaluate_rows(
    definitions: Sequence[Mapping[str, Any]],
    receipts: Mapping[str, Mapping[str, Any]],
    *,
    clock_route: str,
    successor_acceptance: bool,
    internal_passes: Iterable[str] = (),
    forced_reason_codes: Mapping[str, Sequence[str]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    internal = set(internal_passes)
    forced = forced_reason_codes or {}
    rows: list[dict[str, Any]] = []
    refusals: list[dict[str, Any]] = []
    for definition in definitions:
        row_id = definition["row_id"]
        applicability = applicability_for_row(
            definition,
            clock_route=clock_route,
            successor_acceptance=successor_acceptance,
        )
        if applicability == "NOT_APPLICABLE":
            rows.append(
                {
                    "row_id": row_id,
                    "evaluation_phase": definition["evaluation_phase"],
                    "applicability": applicability,
                    "verdict": "NOT_APPLICABLE",
                    "predicate_id": definition["predicate_id"],
                    "evidence_ids": [],
                }
            )
            continue
        matching = sorted(
            evidence_id
            for evidence_id, receipt in receipts.items()
            if receipt["kind"] in definition["required_evidence_kinds"]
        )
        passing = [
            evidence_id
            for evidence_id in matching
            if _predicate_passes(receipts[evidence_id], definition["predicate_id"])
        ]
        forced_codes = sorted(set(forced.get(row_id, ())))
        verdict = (
            "REFUSE"
            if forced_codes
            else "PASS"
            if passing or row_id in internal
            else "REFUSE"
        )
        if verdict == "REFUSE":
            propagated = sorted(
                {
                    code
                    for evidence_id in matching
                    for code in receipts[evidence_id]["reason_codes"]
                    if code in IDENTITY_PIN_PROJECTION_REASON_CODES
                }
            )
            codes = forced_codes or propagated or [
                _missing_row_code(row_id)
            ]
            for code in codes:
                refusals.append(
                    _receipt_refusal(
                        code,
                        row_id=row_id,
                        evidence_id=matching[0] if matching else None,
                    )
                )
        rows.append(
            {
                "row_id": row_id,
                "evaluation_phase": definition["evaluation_phase"],
                "applicability": applicability,
                "verdict": verdict,
                "predicate_id": definition["predicate_id"],
                "evidence_ids": passing,
            }
        )
    rows.sort(key=lambda row: row["row_id"])
    return rows, refusals


def _load_freeze_reference(
    pack_root: Path,
    tree: Mapping[str, Any],
    registry_reference: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    require_pass: bool = True,
) -> tuple[Mapping[str, Any], dict[str, Any]]:
    attachments = tree.get("arm_attachments")
    readiness = attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    _valid_plan_attachment(readiness, registry_reference)
    plan_reference = readiness["freeze_receipt"]
    if plan_reference is None:
        raise ArmReadinessError(
            "readiness_freeze_receipt_unreadable", "plan does not pin a freeze receipt"
        )
    receipts = scan_receipt_namespace(
        pack_root / "arm_readiness.freeze.receipts", "freeze"
    )
    matches = [
        item
        for item in receipts
        if f"arm_readiness.freeze.receipts/{item['path'].name}" == plan_reference["path"]
        and item["sha256"] == plan_reference["sha256"]
    ]
    if len(matches) != 1:
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch", "plan freeze reference is not exact"
        )
    receipt = matches[0]["receipt"]
    if receipt["row_registry"] != registry_reference:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "freeze receipt registry binding differs from the plan",
        )
    if receipt["pack_identity"] != _pack_identity(pack_root, tree):
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch",
            "freeze receipt pack identity differs from committed pack bytes",
        )
    definitions = _profile_rows(
        registry, str(registry_reference["plan_profile"]), phase="freeze"
    )
    _validate_profile_rows(
        receipt,
        definitions,
        clock_route="MANUAL",
        successor_acceptance=not _issued_d079(tree),
    )
    semantic_receipts: dict[str, Mapping[str, Any]] = {}
    identity_reasons: list[str] = []
    boot_session_id = _current_boot_session_id()
    generic_items = [
        item
        for item in receipt["evidence"]
        if item["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
    ]
    evidence_directory = pack_root / "arm_readiness.evidence"
    if evidence_directory.exists():
        expected_names = {
            name
            for item in generic_items
            for name in (str(item["path"]), f"{item['path']}.sha256")
        }
        try:
            observed_names = {
                f"arm_readiness.evidence/{path.name}"
                for path in evidence_directory.iterdir()
            }
        except OSError as exc:
            raise ArmReadinessError(
                "readiness_evidence_unreadable",
                f"cannot scan freeze evidence namespace: {exc}",
            ) from exc
        if expected_names != observed_names:
            raise ArmReadinessError(
                "readiness_evidence_reference_invalid",
                "freeze evidence namespace differs from receipt bindings",
            )
    elif generic_items:
        raise ArmReadinessError(
            "readiness_evidence_unreadable", "freeze evidence namespace is absent"
        )
    for item in generic_items:
        if item["namespace"] != "PACK":
            raise ArmReadinessError(
                "readiness_evidence_reference_invalid",
                "freeze evidence must be pack-relative",
            )
        semantic_receipts[item["evidence_id"]] = (
            _authenticate_generic_evidence_item(
                item,
                pack_root,
                pack_root,
                expected_boot_session_id=boot_session_id,
            )
        )
    identity_items = [
        item
        for item in receipt["evidence"]
        if item["schema_version"] == IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA
    ]
    if len(identity_items) == 1:
        item = identity_items[0]
        if item["evidence_id"] != "u11-freeze-projection" or item["namespace"] != "PACK":
            raise ArmReadinessError(
                "readiness_evidence_reference_invalid",
                "freeze identity evidence binding is invalid",
            )
        path = pack_root / _require_relative_path(
            item["path"], "freeze identity evidence path"
        )
        identity_receipt, _raw = _read_identity_projection_receipt(
            path, str(item["sha256"])
        )
        if (
            item["receipt_kind"] != identity_receipt["receipt_kind"]
            or item["status"] != identity_receipt["status"]
        ):
            raise ArmReadinessError(
                "readiness_evidence_digest_mismatch",
                "freeze identity evidence metadata differs from its bytes",
            )
        identity_reasons = list(identity_receipt["reason_codes"])
        semantic_receipts[item["evidence_id"]] = (
            _identity_projection_pseudo_receipt(
                status=str(identity_receipt["status"]),
                reason_codes=identity_reasons,
            )
        )
    elif identity_items:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "freeze receipt contains multiple identity bindings",
        )
    else:
        identity_reasons = ["readiness_identity_artifact_unreadable"]
    plan_identity_item, plan_identity_receipt, plan_identity_reasons = (
        _load_frozen_identity_evidence(pack_root, tree)
    )
    bound_identity_item = identity_items[0] if identity_items else None
    if bound_identity_item != plan_identity_item:
        raise ArmReadinessError(
            "readiness_identity_pinset_frozen_mismatch",
            "freeze receipt identity binding differs from the frozen plan",
        )
    identity_reasons = list(plan_identity_reasons)
    if plan_identity_item is not None and plan_identity_receipt is not None:
        semantic_receipts[plan_identity_item["evidence_id"]] = plan_identity_receipt
    expected_rows, expected_refusals = _evaluate_rows(
        definitions,
        semantic_receipts,
        clock_route="MANUAL",
        successor_acceptance=not _issued_d079(tree),
        forced_reason_codes={
            "desk.identity_pin_projection": identity_reasons
        },
    )
    if receipt["rows"] != expected_rows or receipt["refusals"] != expected_refusals:
        raise ArmReadinessError(
            "readiness_dependency_refused",
            "freeze receipt conclusions do not replay from authenticated evidence",
        )
    if require_pass and receipt["status"] != "PASS":
        raise ArmReadinessError(
            "readiness_dependency_refused", "freeze receipt refused"
        )
    return receipt, {
        "receipt_id": receipt["receipt_id"],
        "path": plan_reference["path"],
        "sha256": plan_reference["sha256"],
    }


def _freeze_evidence_for_arm(
    pack_root: Path,
    tree: Mapping[str, Any],
    freeze_receipt: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Mapping[str, Any]]]:
    items = copy.deepcopy(list(freeze_receipt["evidence"]))
    receipts: dict[str, Mapping[str, Any]] = {}
    boot_session_id = _current_boot_session_id()
    plan_identity_item, plan_identity_receipt, _reasons = (
        _load_frozen_identity_evidence(pack_root, tree)
    )
    for item in items:
        if item["schema_version"] == EVIDENCE_RECEIPT_SCHEMA:
            receipts[item["evidence_id"]] = _authenticate_generic_evidence_item(
                item,
                pack_root,
                pack_root,
                expected_boot_session_id=boot_session_id,
            )
        elif item["schema_version"] == IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA:
            if item != plan_identity_item or plan_identity_receipt is None:
                raise ArmReadinessError(
                    "readiness_identity_pinset_frozen_mismatch",
                    "arm replay found a different frozen identity binding",
                )
            receipts[item["evidence_id"]] = plan_identity_receipt
        else:
            raise ArmReadinessError(
                "readiness_evidence_reference_invalid",
                "freeze receipt names an unsupported evidence schema",
            )
    return items, receipts


def generate_freeze_receipt(pack_root: Path | str) -> dict[str, Any]:
    """Write or idempotently authenticate the pack's non-authorizing receipt."""

    root = Path(pack_root).resolve(strict=True)
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    attachments = tree.get("arm_attachments")
    readiness = attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    _valid_plan_attachment(readiness, registry_reference)
    namespace = root / "arm_readiness.freeze.receipts"
    existing = scan_receipt_namespace(namespace, "freeze", allow_absent=True)
    if existing and readiness["freeze_receipt"] is not None:
        latest = existing[-1]
        expected = {
            "path": f"arm_readiness.freeze.receipts/{latest['path'].name}",
            "sha256": latest["sha256"],
        }
        if readiness["freeze_receipt"] != expected:
            raise ArmReadinessError(
                "readiness_freeze_receipt_mismatch", "existing freeze receipt is not plan-pinned"
            )
        return {
            "status": latest["receipt"]["status"],
            "arm_disposition": "NOT_APPLICABLE",
            "receipt_path": str(latest["path"]),
            "receipt_sha256": latest["sha256"],
            "reason_codes": sorted(
                {item["code"] for item in latest["receipt"]["refusals"]}
            ),
            "mutated": False,
        }
    if existing:
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch", "unreferenced freeze receipt exists"
        )
    # The pre-freeze pack must be an exact committed tree.  The writes below
    # intentionally make it dirty until the lead commits the final frozen pack.
    pre_freeze_pack_sha = committed_pack_tree_sha256(root)
    del pre_freeze_pack_sha
    pack = _pack_record(root)
    head = reviewed_main(root)["head_commit"]
    custody_pack_root = root
    evaluated_at_monotonic_ns = time.monotonic_ns()
    boot_session_id = _current_boot_session_id()
    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=None,
        head_commit=None,
        boot_session_id=boot_session_id,
        now_monotonic_ns=evaluated_at_monotonic_ns,
    )
    identity_item, identity_receipt, identity_reasons = _load_frozen_identity_evidence(
        root, tree
    )
    if identity_item is not None and identity_receipt is not None:
        evidence_items.append(identity_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[identity_item["evidence_id"]] = identity_receipt
    definitions = _profile_rows(registry, registry_reference["plan_profile"], phase="freeze")
    rows, refusals = _evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route="MANUAL",
        successor_acceptance=not _issued_d079(tree),
        forced_reason_codes={
            "desk.identity_pin_projection": identity_reasons
        },
    )
    refusals = sorted(
        evidence_refusals + refusals,
        key=lambda item: (item["code"], item["row_id"] or "", item["evidence_id"] or ""),
    )
    status = "REFUSE" if refusals else "PASS"
    number = 1
    receipt_name = f"freeze-{number:04d}.json"
    receipt = {
        "schema_version": FREEZE_RECEIPT_SCHEMA,
        "receipt_kind": "freeze",
        "receipt_id": receipt_name.removesuffix(".json"),
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": _utc_now(),
        "pack_identity": _pack_identity(root, tree),
        "row_registry": copy.deepcopy(registry_reference),
        "evidence": evidence_items,
        "rows": rows,
        "refusals": refusals,
        "supersedes": None,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_freeze_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(namespace / receipt_name, raw)
    _exclusive_write(
        namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
        "path": f"arm_readiness.freeze.receipts/{receipt_name}",
        "sha256": digest,
    }
    tree_raw = _render_plan_tree(tree)
    _atomic_replace(root / "plan_tree.json", tree_raw)
    _atomic_replace(
        root / "plan_tree.sha256",
        gnu_sidecar(sha256_bytes(tree_raw), "plan_tree.json"),
    )
    return {
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "receipt_path": str(namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in refusals}),
        "mutated": True,
    }


def _dry_run_check(
    check_id: str, command: Sequence[str], exit_code: int, stdout: str, stderr: str
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "PASS" if exit_code == 0 else "REFUSE",
        "command_sha256": sha256_bytes("\0".join(command).encode("utf-8")),
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "exit_code": exit_code,
    }


def _run_under_lease_rehearsal(
    pack_root: Path,
    synthetic_root: Path,
    rehearsal_id: str,
) -> list[dict[str, Any]]:
    """Exercise the real reservation CLI and real writer lifecycle twice."""

    from joulewise.calibration_ledger import GENESIS_DIGEST, LEDGER_SCHEMA, T1_FIELDS
    from scripts import reserve_calibration_window_bracket as reserve_cli
    from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle

    try:
        synthetic_root.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ArmReadinessError(
            "readiness_root_not_fresh",
            "synthetic rehearsal root already exists",
        ) from exc
    ledger = synthetic_root / "calibration_observation_ledger.jsonl"
    head_pin = synthetic_root / "calibration_ledger_head.json"
    head_pin.write_bytes(
        render_json(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
    )
    tree, _raw = _plan_tree(pack_root)
    plan_path = pack_root / PurePosixPath(str(tree["plan"]["path"])).name
    plan_raw = plan_path.read_bytes()
    session_id = f"dry-{rehearsal_id}"
    pre_attempt = f"{session_id}-pre"
    post_attempt = f"{session_id}-post"
    runs_root = synthetic_root / "runs"
    epoch = {
        "os_build": "synthetic",
        "hardware_model": "synthetic",
        "power_policy": "ac_high_power",
        "sampling_interval_ms": 100,
        "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
        "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
    }
    t1 = {field: f"synthetic-{field}" for field in T1_FIELDS}
    t1.update(epoch)
    epoch_path = synthetic_root / "identity_epoch.json"
    t1_path = synthetic_root / "t1_bindings.json"
    epoch_path.write_bytes(render_json(epoch))
    t1_path.write_bytes(render_json(t1))
    argv = [
        "--ledger",
        str(ledger),
        "--head-pin",
        str(head_pin),
        "--session-id",
        session_id,
        "--window-id",
        str(tree["window_identity"]["window_id"]),
        "--plan-id",
        str(tree["plan"]["plan_id"]),
        "--plan-sha256",
        sha256_bytes(plan_raw),
        "--plan",
        str(plan_path),
        "--evidence-root-id",
        str(tree["window_identity"]["evidence_root_id"]),
        "--runs-root",
        str(runs_root),
        "--pre-attempt-id",
        pre_attempt,
        "--post-attempt-id",
        post_attempt,
        "--pre-custody-locator",
        str(runs_root / "instrument_validation" / pre_attempt),
        "--post-custody-locator",
        str(runs_root / "instrument_validation" / post_attempt),
        "--identity-epoch-json",
        str(epoch_path),
        "--t1-bindings-json",
        str(t1_path),
        "--execute",
        "--allow-uncommitted-pin-for-test",
    ]
    stdout_stream = io.StringIO()
    stderr_stream = io.StringIO()
    with redirect_stdout(stdout_stream), redirect_stderr(stderr_stream):
        reserve_rc = reserve_cli.main(argv)
    stdout = stdout_stream.getvalue()
    stderr = stderr_stream.getvalue()
    checks = [
        _dry_run_check(
            "real_reservation_cli_execute",
            ["reserve_calibration_window_bracket.py", *argv],
            reserve_rc,
            stdout,
            stderr,
        )
    ]
    if reserve_rc != 0 or "calibration_pre_reserve_authorized" not in stderr:
        return checks
    for slot, attempt_id in (("pre", pre_attempt), ("post", post_attempt)):
        custody = runs_root / "instrument_validation" / attempt_id
        writer_stdout = io.StringIO()
        writer_stderr = io.StringIO()
        rc = 0
        try:
            lifecycle = _CaptureLedgerLifecycle(
                ledger_path=ledger,
                head_pin_path=head_pin,
                attempt_id=attempt_id,
                custody_locator=str(custody),
                identity_epoch=epoch,
                t1_bindings=t1,
                session_id=session_id,
                slot=slot,
                require_committed_pin=False,
            )
            with redirect_stdout(writer_stdout), redirect_stderr(writer_stderr):
                lifecycle.begin()
                # The real writer creates custody only after the reserved slot
                # has been claimed.  A pre-existing directory is deliberately
                # treated as partial custody by the ledger implementation.
                custody.mkdir(parents=True, exist_ok=False)
                (custody / "instrument_evidence.json").write_bytes(
                    render_json(
                        {
                            "mode": "synthetic_dry_run",
                            "slot": slot,
                            "status": "valid",
                        }
                    )
                )
                (custody / "manifest.json").write_bytes(
                    render_json(
                        {
                            "mode": "synthetic_dry_run",
                            "slot": slot,
                        }
                    )
                )
                lifecycle.capture_wall_time_s = "1.0"
                lifecycle.exact_bound_lexeme_s = "0.001"
                lifecycle.finalize("valid")
        except Exception as exc:  # fail closed into an authenticated check
            rc = 1
            print(f"{type(exc).__name__}: {exc}", file=writer_stderr)
        checks.append(
            _dry_run_check(
                f"real_writer_entry_{slot}",
                ["validate_powermetrics_fiducial.py", "--session-id", session_id, "--slot", slot],
                rc,
                writer_stdout.getvalue(),
                writer_stderr.getvalue(),
            )
        )
        if "calibration_writer_arm_authorized" not in writer_stderr.getvalue():
            checks[-1]["status"] = "REFUSE"
            checks[-1]["exit_code"] = max(1, checks[-1]["exit_code"])
    return checks


def generate_dry_run_receipt(
    pack_root: Path | str,
    window_custody_root: Path | str,
    rehearsal_id: str,
    synthetic_root: Path | str,
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    custody_root = Path(window_custody_root).resolve()
    synthetic = Path(synthetic_root).resolve()
    _require_path_component(rehearsal_id, "rehearsal_id")
    if not synthetic.is_absolute():
        raise ArmReadinessError(
            "readiness_usage_invalid", "synthetic root must be absolute"
        )
    custody_pack_root = custody_root / root.name
    existing = scan_receipt_namespace(
        custody_pack_root / "arm_readiness.dry_run.receipts",
        "dry-run",
        allow_absent=True,
    )
    if any(
        item["receipt"]["synthetic_context"]["rehearsal_id"] == rehearsal_id
        for item in existing
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid", "rehearsal_id was already used"
        )
    pack = _pack_record(root)
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    try:
        freeze_receipt, _freeze_reference = _load_freeze_reference(
            root,
            tree,
            registry_reference,
            registry,
            require_pass=False,
        )
        freeze_refusals = copy.deepcopy(freeze_receipt["refusals"])
        if freeze_receipt["status"] != "PASS" and not freeze_refusals:
            freeze_refusals = [_receipt_refusal("readiness_dependency_refused")]
    except ArmReadinessError as exc:
        freeze_refusals = [exc.refusal()]
    checks = _run_under_lease_rehearsal(root, synthetic, rehearsal_id)
    reviewed = reviewed_main(root)
    head_binding = reviewed["head_commit"]
    checks.append(
        _dry_run_check(
            "same_head_pack_binding",
            ["reviewed-head", head_binding, "pack", pack["pack_sha256"]],
            0 if reviewed["clean"] and reviewed["exact_match"] else 1,
            head_binding,
            "",
        )
    )
    refusals = list(freeze_refusals)
    if any(check["status"] != "PASS" for check in checks):
        refusals.append(_receipt_refusal("readiness_ledger_preflight_refused"))
    if not reviewed["clean"]:
        refusals.append(_receipt_refusal("readiness_git_tree_dirty"))
    elif not reviewed["exact_match"]:
        refusals.append(_receipt_refusal("readiness_reviewed_main_mismatch"))
    status = "REFUSE" if refusals else "PASS"
    namespace = custody_pack_root / "arm_readiness.dry_run.receipts"
    number = max((item["number"] for item in existing), default=0) + 1
    receipt_name = f"dry-run-{number:04d}.json"
    receipt = {
        "schema_version": DRY_RUN_RECEIPT_SCHEMA,
        "receipt_kind": "dry_run",
        "receipt_id": receipt_name.removesuffix(".json"),
        "mode": "dry_run",
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": _utc_now(),
        "pack": pack,
        "synthetic_context": {
            "rehearsal_id": rehearsal_id,
            "root": str(synthetic),
            "ledger_path": str(synthetic / "calibration_observation_ledger.jsonl"),
            "backend": "synthetic_real_lease_replay.v1",
        },
        "evidence": [],
        "checks": checks,
        "omitted_live_domains": list(SYNTHETIC_DOMAINS),
        "refusals": sorted(
            refusals,
            key=lambda item: (item["code"], item["row_id"] or "", item["evidence_id"] or ""),
        ),
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_dry_run_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(namespace / receipt_name, raw)
    _exclusive_write(
        namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    return {
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "receipt_path": str(namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in receipt["refusals"]}),
    }


def _latest_dry_run_binding(
    custody_pack_root: Path,
    pack: Mapping[str, Any],
    reviewed: Mapping[str, Any],
) -> tuple[Mapping[str, Any] | None, dict[str, Any] | None, str | None]:
    receipts = scan_receipt_namespace(
        custody_pack_root / "arm_readiness.dry_run.receipts",
        "dry-run",
        allow_absent=True,
    )
    if not receipts:
        return None, None, "readiness_dry_run_missing"
    latest = receipts[-1]
    receipt = latest["receipt"]
    evidence_item = {
        "evidence_id": f"dry-run-rehearsal/{receipt['receipt_id']}",
        "receipt_kind": "DRY_RUN_REHEARSAL",
        "namespace": "WINDOW_CUSTODY",
        "path": f"arm_readiness.dry_run.receipts/{latest['path'].name}",
        "sha256": latest["sha256"],
        "schema_version": DRY_RUN_RECEIPT_SCHEMA,
        "status": receipt["status"],
    }
    if receipt["status"] != "PASS":
        return receipt, evidence_item, "readiness_dry_run_refused"
    expected_binding = sha256_bytes(
        "\0".join(
            [
                "reviewed-head",
                str(reviewed["head_commit"]),
                "pack",
                str(pack["pack_sha256"]),
            ]
        ).encode("utf-8")
    )
    binding_checks = [
        check
        for check in receipt["checks"]
        if check["check_id"] == "same_head_pack_binding"
    ]
    if (
        receipt["pack"] != pack
        or reviewed["head_commit"] == "unavailable"
        or not reviewed["clean"]
        or not reviewed["exact_match"]
        or len(binding_checks) != 1
        or binding_checks[0]["command_sha256"] != expected_binding
    ):
        return receipt, evidence_item, "readiness_dry_run_stale"
    return receipt, evidence_item, None


def _latest_dry_run(
    custody_pack_root: Path, pack: Mapping[str, Any], reviewed: Mapping[str, Any]
) -> tuple[Mapping[str, Any] | None, str | None]:
    receipt, _evidence_item, refusal = _latest_dry_run_binding(
        custody_pack_root, pack, reviewed
    )
    return receipt, refusal


def _dry_run_semantic_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    status = str(receipt["status"])
    check_statuses = {
        str(check["check_id"]): str(check["status"])
        for check in receipt["checks"]
    }
    return {
        "kind": "DRY_RUN_REHEARSAL",
        "status": status,
        "facts": (
            [
                {
                    "fact_id": "desk.under_lease_rehearsal.v1",
                    "value_type": "OBJECT",
                    "value": {
                        check_id: check_statuses.get(check_id)
                        for check_id in _PREDICATE_CONTENT_REQUIREMENTS[
                            "desk.under_lease_rehearsal.v1"
                        ]
                    },
                }
            ]
            if status == "PASS"
            else []
        ),
        "checks": [],
        "reason_codes": [],
    }


def _root_policy_refusals(
    context: Mapping[str, Any], prior_arms: Sequence[Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], set[str]]:
    refusals: list[dict[str, Any]] = []
    passes: set[str] = set()
    root_names = ("claim_runs_root", "bound_runs_root", "custody_root", "quarantine_root")
    roots = [Path(str(context[name])) for name in root_names]
    try:
        resolved_roots = [path.resolve(strict=True) for path in roots]
    except OSError:
        resolved_roots = []
    if resolved_roots and len(set(resolved_roots)) != len(resolved_roots):
        refusals.append(
            _receipt_refusal("readiness_root_binding_invalid", row_id="t0.fresh_roots_waivers")
        )
    elif len(resolved_roots) != len(roots) or any(not path.is_dir() for path in roots):
        refusals.append(
            _receipt_refusal("readiness_root_not_fresh", row_id="t0.fresh_roots_waivers")
        )
    else:
        try:
            if any(any(path.iterdir()) for path in roots):
                raise OSError("root not empty")
        except OSError:
            refusals.append(
                _receipt_refusal("readiness_root_not_fresh", row_id="t0.fresh_roots_waivers")
            )
    waiver = Path(str(context["waiver_path"]))
    try:
        waiver_value = parse_json_bytes(waiver.read_bytes(), require_canonical=True)
        if not isinstance(waiver_value, list):
            raise ArmReadinessError("readiness_waiver_source_invalid", "waiver is not an array")
        if waiver_value:
            refusals.append(
                _receipt_refusal("readiness_waiver_set_nonempty", row_id="t0.fresh_roots_waivers")
            )
            passes.discard("t0.fresh_roots_waivers")
    except (OSError, ArmReadinessError):
        refusals.append(
            _receipt_refusal("readiness_waiver_source_invalid", row_id="t0.fresh_roots_waivers")
        )
        passes.discard("t0.fresh_roots_waivers")
    backups = [
        Path(str(context["claim_backup_destination"])),
        Path(str(context["bound_backup_destination"])),
    ]
    try:
        resolved_backups = [path.resolve(strict=True) for path in backups]
    except OSError:
        resolved_backups = []
    if (
        len(resolved_backups) != 2
        or len(set(resolved_backups)) != 2
        or any(not path.is_dir() or not os.access(path, os.W_OK) for path in backups)
    ):
        refusals.append(
            _receipt_refusal("readiness_backup_preflight_refused", row_id="t0.storage_backup_capacity")
        )
    lock_paths = [path / "campaign.lock" for path in roots[:2]]
    if any(path.exists() or path.is_symlink() for path in lock_paths):
        refusals.append(
            _receipt_refusal("readiness_machine_preflight_refused", row_id="t0.campaign_lock_absent")
        )
    used_fields = root_names + (
        "bracket_session_id",
        "pre_attempt_id",
        "post_attempt_id",
    )
    def _same_bound_value(prior: Mapping[str, Any], name: str) -> bool:
        if name not in root_names:
            return prior["arm_context"][name] == context[name]
        try:
            return Path(str(prior["arm_context"][name])).resolve() == Path(
                str(context[name])
            ).resolve()
        except OSError:
            return True

    if any(
        any(_same_bound_value(prior, name) for name in used_fields)
        for prior in prior_arms
    ):
        refusals.append(
            _receipt_refusal("readiness_root_not_fresh", row_id="t0.fresh_roots_waivers")
        )
        refusals.append(
            _receipt_refusal(
                "readiness_launch_capability_unavailable",
                row_id="t0.single_launch_capability",
            )
        )
    return refusals, passes


def _plan_root_binding_refusals(
    tree: Mapping[str, Any], context: Mapping[str, Any]
) -> list[dict[str, Any]]:
    roots = tree.get("roots")
    claim_leaf: object = None
    bound_leaf: object = None
    if isinstance(roots, Mapping):
        claim_leaf = roots.get("claim_root_leaf")
        bound_leaf = roots.get("bound_root_leaf")
    namespace = tree.get("root_namespace")
    if isinstance(namespace, Mapping):
        claim_leaf = namespace.get("claim_leaf", claim_leaf)
        bound_leaf = namespace.get("bound_leaf", bound_leaf)
    if (
        not isinstance(claim_leaf, str)
        or not claim_leaf
        or not isinstance(bound_leaf, str)
        or not bound_leaf
        or Path(str(context["claim_runs_root"])).name != claim_leaf
        or Path(str(context["bound_runs_root"])).name != bound_leaf
    ):
        return [
            _receipt_refusal(
                "readiness_root_binding_invalid",
                row_id="t0.fresh_roots_waivers",
            )
        ]
    return []


def generate_arm_receipt(
    pack_root: Path | str,
    arm_context: Mapping[str, Any],
    window_custody_root: Path | str,
    *,
    validity_ns: int = 300_000_000_000,
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    context = validate_arm_context(arm_context)
    pack = _pack_record(root)
    reviewed = reviewed_main(root)
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    freeze_receipt, freeze_reference = _load_freeze_reference(
        root,
        tree,
        registry_reference,
        registry,
        require_pass=False,
    )
    custody_root = Path(window_custody_root).resolve()
    custody_pack_root = custody_root / root.name
    arm_namespace = custody_pack_root / "arm_readiness.receipts"
    existing = scan_receipt_namespace(arm_namespace, "arm", allow_absent=True)
    prior_receipts = [item["receipt"] for item in existing]
    number = max((item["number"] for item in existing), default=0) + 1
    evaluated_at_monotonic_ns = time.monotonic_ns()
    boot_session_id = _current_boot_session_id()
    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=pack["pack_sha256"],
        head_commit=reviewed["head_commit"],
        boot_session_id=boot_session_id,
        now_monotonic_ns=evaluated_at_monotonic_ns,
        include_pack=False,
    )
    freeze_items, freeze_evidence_receipts = _freeze_evidence_for_arm(
        root, tree, freeze_receipt
    )
    duplicate_ids = set(evidence_receipts).intersection(freeze_evidence_receipts)
    if duplicate_ids:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            f"arm and freeze evidence IDs collide: {sorted(duplicate_ids)!r}",
        )
    evidence_items.extend(freeze_items)
    evidence_items.sort(key=lambda item: item["evidence_id"])
    evidence_receipts.update(freeze_evidence_receipts)
    identity_item, identity_receipt, identity_reasons = (
        _run_identity_arm_reverification(
            root, custody_root, str(context["bracket_session_id"])
        )
    )
    if identity_item is not None and identity_receipt is not None:
        evidence_items.append(identity_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[identity_item["evidence_id"]] = identity_receipt
    dry_run, dry_run_item, dry_run_code = _latest_dry_run_binding(
        custody_pack_root, pack, reviewed
    )
    if dry_run is not None and dry_run_item is not None:
        evidence_items.append(dry_run_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[dry_run_item["evidence_id"]] = (
            _dry_run_semantic_receipt(dry_run)
        )
    root_refusals, internal_passes = _root_policy_refusals(context, prior_receipts)
    root_refusals.extend(_plan_root_binding_refusals(tree, context))
    if reviewed["exact_match"]:
        internal_passes.add("desk.reviewed_checkout")
    forced: dict[str, list[str]] = {
        "desk.identity_pin_projection": list(identity_reasons)
    }
    for refusal in root_refusals:
        if refusal["row_id"] is not None:
            forced.setdefault(str(refusal["row_id"]), []).append(refusal["code"])
    definitions = _profile_rows(registry, registry_reference["plan_profile"], phase="arm")
    rows, row_refusals = _evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route=context["clock_route"],
        successor_acceptance=not _issued_d079(tree),
        internal_passes=internal_passes,
        forced_reason_codes=forced,
    )
    refusals = list(evidence_refusals) + list(root_refusals) + row_refusals
    if freeze_receipt["status"] != "PASS":
        refusals.append(_receipt_refusal("readiness_dependency_refused"))
    if not reviewed["clean"]:
        refusals.append(_receipt_refusal("readiness_git_tree_dirty", row_id="desk.reviewed_checkout"))
    elif not reviewed["exact_match"]:
        refusals.append(
            _receipt_refusal("readiness_reviewed_main_mismatch", row_id="desk.reviewed_checkout")
        )
    if dry_run_code is not None:
        refusals.append(_receipt_refusal(dry_run_code, row_id="desk.under_lease_rehearsal"))
    # De-duplicate exact refusal records without weakening any row refusal.
    unique = {
        (item["type"], item["code"], item["row_id"], item["evidence_id"]): item
        for item in refusals
    }
    refusals = sorted(
        unique.values(),
        key=lambda item: (item["code"], item["row_id"] or "", item["evidence_id"] or ""),
    )
    status = "REFUSE" if refusals else "PASS"
    receipt_name = f"arm-{number:04d}.json"
    supersedes = None
    if existing:
        prior = existing[-1]
        supersedes = {
            "receipt_id": prior["receipt"]["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{prior['path'].name}",
            "receipt_sha256": prior["sha256"],
            "pack_id": prior["receipt"]["pack"]["pack_id"],
            "pack_sha256": prior["receipt"]["pack"]["pack_sha256"],
        }
    evidence_expirations = [
        int(item["valid_until_monotonic_ns"])
        for item in evidence_receipts.values()
        if "valid_until_monotonic_ns" in item
    ]
    valid_until = min(
        [evaluated_at_monotonic_ns + validity_ns, *evidence_expirations]
    )
    receipt = {
        "schema_version": ARM_RECEIPT_SCHEMA,
        "receipt_kind": "arm",
        "receipt_id": receipt_name.removesuffix(".json"),
        "mode": "arm",
        "status": status,
        "arm_disposition": "NO_GO" if refusals else "GO",
        "issued_at_utc": _utc_now(),
        "boot_session_id": boot_session_id,
        "valid_until_monotonic_ns": valid_until,
        "pack": pack,
        "reviewed_main": reviewed,
        "arm_context": copy.deepcopy(dict(context)),
        "freeze_receipt": freeze_reference,
        "row_registry": copy.deepcopy(registry_reference),
        "evidence": evidence_items,
        "rows": rows,
        "refusals": refusals,
        "supersedes": supersedes,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_arm_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(arm_namespace / receipt_name, raw)
    _exclusive_write(
        arm_namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    return {
        "status": status,
        "arm_disposition": receipt["arm_disposition"],
        "receipt_path": str(arm_namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in refusals}),
    }


def _derive_arm_semantics_for_verification(
    root: Path,
    custody_pack_root: Path,
    receipt: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pack = _pack_record(root)
    if receipt["pack"] != pack:
        raise ArmReadinessError(
            "readiness_pack_digest_mismatch",
            "arm receipt pack binding differs from committed pack bytes",
        )
    reviewed = reviewed_main(root)
    if receipt["reviewed_main"] != reviewed:
        raise ArmReadinessError(
            "readiness_reviewed_main_mismatch",
            "arm receipt reviewed-main proof is stale",
        )
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    if receipt["row_registry"] != registry_reference:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "arm receipt registry binding differs from committed bytes",
        )
    freeze_receipt, freeze_reference = _load_freeze_reference(
        root,
        tree,
        registry_reference,
        registry,
        require_pass=False,
    )
    if receipt["freeze_receipt"] != freeze_reference:
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch",
            "arm receipt freeze binding differs from the plan",
        )

    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=pack["pack_sha256"],
        head_commit=reviewed["head_commit"],
        boot_session_id=str(receipt["boot_session_id"]),
        now_monotonic_ns=time.monotonic_ns(),
        include_pack=False,
    )
    freeze_items, freeze_evidence_receipts = _freeze_evidence_for_arm(
        root, tree, freeze_receipt
    )
    if set(evidence_receipts).intersection(freeze_evidence_receipts):
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "arm and freeze evidence IDs collide",
        )
    evidence_items.extend(freeze_items)
    evidence_items.sort(key=lambda item: item["evidence_id"])
    evidence_receipts.update(freeze_evidence_receipts)
    identity_items = [
        item
        for item in receipt["evidence"]
        if item["evidence_id"] == "u11-arm-reverification"
    ]
    identity_reasons: list[str]
    if len(identity_items) == 1:
        identity_item = identity_items[0]
        identity_receipt, identity_reasons = _authenticate_identity_arm_evidence(
            identity_item, custody_pack_root, root, reviewed
        )
        evidence_items.append(copy.deepcopy(dict(identity_item)))
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[identity_item["evidence_id"]] = identity_receipt
    elif identity_items:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "arm receipt contains multiple D-131 evidence bindings",
        )
    else:
        identity_reasons = ["readiness_identity_artifact_unreadable"]
    dry_run, dry_run_item, dry_run_code = _latest_dry_run_binding(
        custody_pack_root, pack, reviewed
    )
    if dry_run is not None and dry_run_item is not None:
        evidence_items.append(dry_run_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[dry_run_item["evidence_id"]] = (
            _dry_run_semantic_receipt(dry_run)
        )
    if receipt["evidence"] != evidence_items:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "arm receipt evidence bindings are not the authenticated namespace",
        )
    root_refusals, internal_passes = _root_policy_refusals(
        receipt["arm_context"], []
    )
    root_refusals.extend(
        _plan_root_binding_refusals(tree, receipt["arm_context"])
    )
    if reviewed["exact_match"]:
        internal_passes.add("desk.reviewed_checkout")
    forced: dict[str, list[str]] = {
        "desk.identity_pin_projection": identity_reasons
    }
    for refusal in root_refusals:
        if refusal["row_id"] is not None:
            forced.setdefault(str(refusal["row_id"]), []).append(refusal["code"])
    definitions = _profile_rows(
        registry, registry_reference["plan_profile"], phase="arm"
    )
    rows, row_refusals = _evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route=str(receipt["arm_context"]["clock_route"]),
        successor_acceptance=not _issued_d079(tree),
        internal_passes=internal_passes,
        forced_reason_codes=forced,
    )
    refusals = list(evidence_refusals) + list(root_refusals) + row_refusals
    if freeze_receipt["status"] != "PASS":
        refusals.append(_receipt_refusal("readiness_dependency_refused"))
    if not reviewed["clean"]:
        refusals.append(
            _receipt_refusal(
                "readiness_git_tree_dirty", row_id="desk.reviewed_checkout"
            )
        )
    elif not reviewed["exact_match"]:
        refusals.append(
            _receipt_refusal(
                "readiness_reviewed_main_mismatch",
                row_id="desk.reviewed_checkout",
            )
        )
    if dry_run_code is not None:
        refusals.append(
            _receipt_refusal(
                dry_run_code, row_id="desk.under_lease_rehearsal"
            )
        )
    unique = {
        (item["type"], item["code"], item["row_id"], item["evidence_id"]): item
        for item in refusals
    }
    refusals = sorted(
        unique.values(),
        key=lambda item: (
            item["code"],
            item["row_id"] or "",
            item["evidence_id"] or "",
        ),
    )
    _validate_profile_rows(
        receipt,
        definitions,
        clock_route=str(receipt["arm_context"]["clock_route"]),
        successor_acceptance=not _issued_d079(tree),
    )
    return rows, refusals


def _read_arm_with_sidecar(path: Path) -> tuple[Mapping[str, Any], bytes, str]:
    try:
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        sidecar = path.with_name(f"{path.name}.sha256").read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable", f"cannot read arm receipt: {exc}"
        ) from exc
    if sidecar != gnu_sidecar(digest, path.name):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch", "arm receipt sidecar mismatch"
        )
    value = parse_json_bytes(raw, require_canonical=True)
    if isinstance(value, Mapping) and value.get("schema_version") == DRY_RUN_RECEIPT_SCHEMA:
        raise ArmReadinessError(
            "readiness_dry_run_used_as_arm_record", "dry-run cannot be used as an arm receipt"
        )
    receipt = validate_arm_receipt(value)
    return receipt, raw, digest


def verify_arm_receipt(
    pack_root: Path | str, arm_receipt: Path | str
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    path = Path(arm_receipt).resolve(strict=True)
    receipt, _raw, digest = _read_arm_with_sidecar(path)
    if receipt["receipt_kind"] != "arm":
        raise ArmReadinessError(
            "readiness_dry_run_used_as_arm_record", "only an arm receipt may verify"
        )
    if receipt["boot_session_id"] != _current_boot_session_id():
        raise ArmReadinessError(
            "readiness_record_expired", "arm receipt belongs to a prior boot session"
        )
    if time.monotonic_ns() > receipt["valid_until_monotonic_ns"]:
        raise ArmReadinessError(
            "readiness_record_expired", "arm receipt expired"
        )
    namespace = path.parent
    if namespace.name != "arm_readiness.receipts":
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous",
            "arm receipt is outside arm_readiness.receipts",
        )
    scanned = scan_receipt_namespace(namespace, "arm")
    matches = [item for item in scanned if item["path"].resolve() == path]
    if len(matches) != 1:
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous", "arm receipt is outside its governed namespace"
        )
    target = matches[0]
    if any(
        item["number"] > target["number"]
        and item["receipt"]["supersedes"] is not None
        and item["receipt"]["supersedes"]
        == {
            "receipt_id": receipt["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{path.name}",
            "receipt_sha256": digest,
            "pack_id": receipt["pack"]["pack_id"],
            "pack_sha256": receipt["pack"]["pack_sha256"],
        }
        for item in scanned
    ):
        raise ArmReadinessError(
            "readiness_receipt_superseded", "arm receipt has a valid semantic successor"
        )
    custody_pack_root = namespace.parent
    if custody_pack_root.name != root.name:
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous",
            "arm receipt namespace does not belong to this pack",
        )
    consumption_path = (
        custody_pack_root
        / "arm_readiness.consumptions"
        / f"{receipt['receipt_id']}.consumed.json"
    )
    if consumption_path.exists() or consumption_path.is_symlink():
        raise ArmReadinessError(
            "readiness_record_consumed", "launch capability was already consumed"
        )
    expected_rows, expected_refusals = _derive_arm_semantics_for_verification(
        root, custody_pack_root, receipt
    )
    if receipt["rows"] != expected_rows or receipt["refusals"] != expected_refusals:
        raise ArmReadinessError(
            "readiness_dependency_refused",
            "arm receipt conclusions do not replay from authenticated evidence",
        )
    if (
        expected_refusals
        or receipt["status"] != "PASS"
        or receipt["arm_disposition"] != "GO"
    ):
        raise ArmReadinessError(
            "readiness_dependency_refused", "arm receipt does not carry PASS/GO"
        )
    return {
        "status": "PASS",
        "arm_disposition": "GO",
        "receipt_path": str(path),
        "receipt_sha256": digest,
        "pack_sha256": receipt["pack"]["pack_sha256"],
    }


def consume_launch_capability(
    pack_root: Path | str,
    arm_receipt: Path | str,
    window_custody_root: Path | str,
) -> dict[str, Any]:
    """Atomically consume one unsuperseded GO receipt; never execute a command."""

    verified = verify_arm_receipt(pack_root, arm_receipt)
    root = Path(pack_root).resolve(strict=True)
    receipt_path = Path(arm_receipt).resolve(strict=True)
    receipt, _raw, digest = _read_arm_with_sidecar(receipt_path)
    reviewed = reviewed_main(root)
    context = receipt["arm_context"]
    root_refusals, _passes = _root_policy_refusals(context, [])
    if root_refusals:
        raise ArmReadinessError(
            root_refusals[0]["code"], "volatile root/backup/lock predicate changed"
        )
    custody_pack_root = Path(window_custody_root).resolve() / root.name
    if custody_pack_root != receipt_path.parent.parent:
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous",
            "consumption custody root differs from the arm receipt namespace",
        )
    consumption_dir = custody_pack_root / "arm_readiness.consumptions"
    consumption_name = f"{receipt['receipt_id']}.consumed.json"
    relative_arm_path = f"arm_readiness.receipts/{receipt_path.name}"
    consumption = {
        "schema_version": CONSUMPTION_RECEIPT_SCHEMA,
        "receipt_kind": "launch_consumption",
        "consumed_at_utc": _utc_now(),
        "arm_receipt": {
            "receipt_id": receipt["receipt_id"],
            "path": relative_arm_path,
            "sha256": digest,
        },
        "pack_sha256": verified["pack_sha256"],
        "head_commit": reviewed["head_commit"],
        "volatile_checks": sorted(
            [
                "arm_receipt_unsuperseded",
                "campaign_lock_absent",
                "pack_digest_unchanged",
                "roots_and_backups_rechecked",
                "same_head",
            ]
        ),
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_consumption_receipt(consumption)
    raw = render_json(consumption)
    consumption_path = consumption_dir / consumption_name
    try:
        _exclusive_write(consumption_path, raw)
    except ArmReadinessError as exc:
        if exc.reason_code == "readiness_output_collision":
            raise ArmReadinessError(
                "readiness_record_consumed", "launch capability was already consumed"
            ) from exc
        raise
    digest_out = sha256_bytes(raw)
    _exclusive_write(
        consumption_dir / f"{consumption_name}.sha256",
        gnu_sidecar(digest_out, consumption_name),
    )
    return {
        "status": "CONSUMED",
        "arm_disposition": "NOT_APPLICABLE",
        "consumption_path": str(consumption_path),
        "consumption_sha256": digest_out,
    }


def verify_receipt(
    pack_root: Path | str, receipt_path: Path | str
) -> dict[str, Any]:
    path = Path(receipt_path)
    try:
        raw = path.read_bytes()
        sidecar = path.with_name(f"{path.name}.sha256").read_bytes()
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable", f"cannot read receipt: {exc}"
        ) from exc
    digest = sha256_bytes(raw)
    if sidecar != gnu_sidecar(digest, path.name):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "receipt sidecar does not authenticate exact bytes",
        )
    value = parse_json_bytes(raw, require_canonical=True)
    if not isinstance(value, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "receipt must be an object"
        )
    schema = value.get("schema_version")
    if schema == ARM_RECEIPT_SCHEMA:
        return verify_arm_receipt(pack_root, path)
    if schema == DRY_RUN_RECEIPT_SCHEMA:
        validate_dry_run_receipt(value)
        raise ArmReadinessError(
            "readiness_dry_run_used_as_arm_record", "dry-run cannot verify as arm authority"
        )
    if schema == FREEZE_RECEIPT_SCHEMA:
        receipt = validate_freeze_receipt(value)
        return {
            "status": receipt["status"],
            "arm_disposition": "NOT_APPLICABLE",
            "receipt_path": str(path),
            "receipt_sha256": digest,
        }
    raise ArmReadinessError(
        "readiness_receipt_kind_invalid", "unknown readiness receipt schema"
    )


__all__ = [
    "ARM_CONTEXT_KEYS",
    "ARM_RECEIPT_SCHEMA",
    "ASSURANCE",
    "ArmReadinessError",
    "CONSUMPTION_RECEIPT_SCHEMA",
    "DRY_RUN_RECEIPT_SCHEMA",
    "EVIDENCE_RECEIPT_SCHEMA",
    "FREEZE_RECEIPT_SCHEMA",
    "PACK_DIGEST_ALGORITHM",
    "READINESS_REASON_CODES",
    "ROW_REGISTRY_ID",
    "ROW_REGISTRY_SCHEMA",
    "SYNTHETIC_DOMAINS",
    "applicability_for_row",
    "committed_pack_tree_sha256",
    "consume_launch_capability",
    "generate_arm_receipt",
    "generate_dry_run_receipt",
    "generate_freeze_receipt",
    "gnu_sidecar",
    "load_registry",
    "parse_json_bytes",
    "plan_arm_readiness_attachment",
    "render_json",
    "reviewed_main",
    "scan_receipt_namespace",
    "sha256_bytes",
    "validate_arm_context",
    "validate_arm_receipt",
    "validate_consumption_receipt",
    "validate_dry_run_receipt",
    "validate_evidence_receipt",
    "validate_freeze_receipt",
    "validate_registry",
    "verify_arm_receipt",
    "verify_receipt",
]
