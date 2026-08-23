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
R1_ROW_REGISTRY_SCHEMA = "joulewise.arm_readiness_row_registry.v2"
ROW_REGISTRY_ID = "d117-row-registry-v1"
FREEZE_RECEIPT_SCHEMA = "joulewise.arm_readiness_freeze_receipt.v1"
# D-139's chain-monotonic successor receipt.  ``FREEZE_RECEIPT_SCHEMA`` remains
# the v1 constant so every committed v1 receipt keeps verifying byte-identically;
# v2 replaces ``supersedes`` with an authenticated ``predecessor`` binding.
FREEZE_RECEIPT_V1_SCHEMA = FREEZE_RECEIPT_SCHEMA
FREEZE_RECEIPT_V2_SCHEMA = "joulewise.arm_readiness_freeze_receipt.v2"
FREEZE_PREDECESSOR_EVIDENCE_SET_DOMAIN = (
    b"joulewise.arm_readiness_freeze_predecessor_evidence_set.v1\n"
)
ARM_RECEIPT_SCHEMA = "joulewise.arm_readiness_receipt.v1"
DRY_RUN_RECEIPT_SCHEMA = "joulewise.arm_readiness_dry_run_receipt.v1"
EVIDENCE_RECEIPT_SCHEMA = "joulewise.arm_readiness_evidence_receipt.v1"
CONTENT_EVIDENCE_RECEIPT_SCHEMA = (
    "joulewise.arm_readiness_content_evidence_receipt.v1"
)
EXECUTION_EVIDENCE_RECEIPT_SCHEMA = (
    "joulewise.arm_readiness_execution_evidence_receipt.v1"
)
R1_LIFECYCLE_REGISTRY_SCHEMA = (
    "joulewise.arm_readiness_freeze_evidence_lifecycle_registry.v1"
)
FAMILY_PUBLICATION_MARKER_SCHEMA = "joulewise.d117_family_publication_marker.v1"
FAMILY_PUBLICATION_VERIFICATION_SCHEMA = (
    "joulewise.d117_family_publication_verification.v1"
)
STEP6_CONFIRMATION_TABLE_SCHEMA = "joulewise.d117_step6_confirmation_table.v1"
FAMILY_PUBLICATION_MARKER_NAME = "d117_family_publication_v4.json"
STEP6_CONFIRMATION_TABLE_NAME = "d117_step6_confirmation_table_v4.json"
S0_CANDIDATE_MANIFEST_NAME = "s0-candidate-manifest.json"
LEGACY_CONSUMPTION_RECEIPT_SCHEMA = (
    "joulewise.arm_readiness_launch_consumption.v1"
)
CONSUMPTION_RECEIPT_SCHEMA = "joulewise.arm_readiness_launch_consumption.v2"
LAUNCH_MANIFEST_SCHEMA = "joulewise.arm_readiness_t0_launch_manifest.v1"
LAUNCH_LINEAGE_SCHEMA = "joulewise.launch_lineage.v1"
LAUNCH_LINEAGE_LOCATOR_SCHEMA = "joulewise.launch_lineage_locator.v1"
LAUNCH_LINEAGE_LOCATOR_BASENAME = ".joulewise-launch-lineage.json"
LAUNCH_START_RECEIPT_SCHEMA = "joulewise.launch_start_receipt.v1"
LAUNCH_SETTLE_RECEIPT_SCHEMA = "joulewise.launch_settle_receipt.v1"
LAUNCH_COMPLETION_RECEIPT_SCHEMA = "joulewise.launch_completion_receipt.v1"
CONTRACT_ID = "D-134"
ROW_REGISTRY_RELATIVE_PATH = Path("configs/arm_readiness/d117_row_registry_v2.json")
_T0_EVIDENCE_SOURCE_SCHEMA = "joulewise.arm_readiness_t0_evidence_source.v1"
_T0_INPUT_DIRECTORY = "arm_readiness.t0.inputs"
# Launch-recipe receipts and sources are canonical JSON records measured in
# kilobytes.  Freeze generous ceilings here so reconciliation never slurps an
# attacker-sized artifact before its digest can fail closed.
_LAUNCH_BINDING_RECEIPT_MAX_BYTES = 1024 * 1024
_LAUNCH_BINDING_SIDECAR_MAX_BYTES = 4 * 1024
_LAUNCH_BINDING_SOURCE_MAX_BYTES = 1024 * 1024
_LAUNCH_BINDING_MANIFEST_MAX_BYTES = 1024 * 1024
_LAUNCH_BINDING_ENVIRONMENT_MAX_BYTES = 1024 * 1024
_LAUNCH_BINDING_CHAIN_MAX_BYTES = 1024 * 1024
_T0_LAUNCH_SOURCE_KEYS = frozenset(
    {
        "schema_version",
        "row_id",
        "kind",
        "head_commit",
        "head_tree_oid",
        "pack_sha256",
        "boot_session_id",
        "primary_artifacts",
        "input_artifacts",
        "probes",
        "facts",
        "derivation",
    }
)
_MISSING_LAUNCH_CONTEXT: Any = object()

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
# D-139 freeze-chain refusals.  They are raised before any successor write and
# are never minted into a receipt: an unauthenticated ancestry record is not a
# legitimate chain member, so it must not become a REFUSE receipt either.
SUCCESSOR_CHAIN_REASON_CODES = frozenset({"readiness_successor_chain_invalid"})
# R1's registry-resolved vocabulary is code-enumerated as four typed families.
# Registry loading checks both membership and type, so deleting a spelling from
# code cannot leave a dormant registry-only refusal that fails later at mint.
R1_POLICY_REASON_CODES = frozenset(
    {"readiness_r1_class_mismatch", "readiness_r1_unknown_policy"}
)
R1_LIFECYCLE_REASON_CODES = frozenset(
    {
        "readiness_r1_dependency_changed_set",
        "readiness_r1_dependency_manifest",
        "readiness_r1_temporal_budget",
        "readiness_r1_v1_grandfathering",
    }
)
R1_CUSTODY_REASON_CODES = frozenset({"readiness_r1_family_publication"})
R1_GIT_REASON_CODES = frozenset({"readiness_r1_successor_chain"})
LAUNCH_LINEAGE_REASON_CODES = frozenset(
    {
        "launch_consumption_missing",
        "launch_consumption_invalid",
        "launch_binding_mismatch",
        "launch_lineage_conflict",
        "launch_lineage_axi_unsupported",
        "launch_lifecycle_incomplete",
        "launch_handoff_invalid",
    }
)
READINESS_REASON_CODES = frozenset().union(
    STRUCTURE_REASON_CODES,
    CUSTODY_REASON_CODES,
    GIT_REASON_CODES,
    LIFECYCLE_REASON_CODES,
    POLICY_REASON_CODES,
    IDENTITY_PIN_PROJECTION_REASON_CODES,
    ENVIRONMENT_REASON_CODES,
    SUCCESSOR_CHAIN_REASON_CODES,
    R1_POLICY_REASON_CODES,
    R1_LIFECYCLE_REASON_CODES,
    R1_CUSTODY_REASON_CODES,
    R1_GIT_REASON_CODES,
)
REASON_TYPE_BY_CODE = {
    **{code: "STRUCTURE" for code in STRUCTURE_REASON_CODES},
    **{code: "CUSTODY" for code in CUSTODY_REASON_CODES},
    **{code: "GIT" for code in GIT_REASON_CODES},
    **{code: "LIFECYCLE" for code in LIFECYCLE_REASON_CODES},
    **{code: "POLICY" for code in POLICY_REASON_CODES},
    **{code: "IDENTITY" for code in IDENTITY_PIN_PROJECTION_REASON_CODES},
    **{code: "ENVIRONMENT" for code in ENVIRONMENT_REASON_CODES},
    **{code: "SUCCESSOR_CHAIN" for code in SUCCESSOR_CHAIN_REASON_CODES},
    **{code: "POLICY" for code in R1_POLICY_REASON_CODES},
    **{code: "LIFECYCLE" for code in R1_LIFECYCLE_REASON_CODES},
    **{code: "CUSTODY" for code in R1_CUSTODY_REASON_CODES},
    **{code: "GIT" for code in R1_GIT_REASON_CODES},
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
# A pack ID's trailing ``_v<N>`` is its family generation.  Generation 1 packs
# open a chain; every later generation must present an authenticated predecessor.
_PACK_GENERATION_RE = re.compile(r"_v([0-9]+)$")
# The IMMUTABLE HISTORICAL v1 mapping (R1 design; see ``_plan_profile``).  This
# map is never edited to follow a supersession: the v1 campaign packs keep their
# role forever, because their committed receipts, evidence, and freeze chains
# were minted against it and must stay authenticatable.  Successor (``_v<N>``)
# identities are NOT listed here — they install BY ROLE through the R1 registry
# (``freeze_evidence_lifecycle.successor_policy.successor_pack_ids``), and the
# code validates only the three D-139-approved uniform successor name shapes
# below.  Post-supersession refusal of a v1 pack is the job of the layered
# governed gates (R2 plan resolution, V1_GRANDFATHERING, the freeze chain), not
# of deleting history from this table.
_PROFILE_BY_PACK = {
    "d117_floor_qwen25_1p5b_v1": "ALPHA",
    "d117_floor_qwen25_7b_v1": "BETA",
    "d117_contrast_qwen25_1p5b_vs_7b_v1": "GAMMA",
}
_SUCCESSOR_PROFILE_PATTERNS = {
    "ALPHA": re.compile(r"^d117_floor_qwen25_1p5b_v(?:[2-9]|[1-9][0-9]+)$"),
    "BETA": re.compile(r"^d117_floor_qwen25_7b_v(?:[2-9]|[1-9][0-9]+)$"),
    "GAMMA": re.compile(
        r"^d117_contrast_qwen25_1p5b_vs_7b_v(?:[2-9]|[1-9][0-9]+)$"
    ),
}

REGISTRY_KEYS = {"schema_version", "registry_id", "plan_profiles", "rows"}
R1_ROW_REGISTRY_KEYS = REGISTRY_KEYS | {"freeze_evidence_lifecycle"}
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
FREEZE_RECEIPT_V1_KEYS = FREEZE_RECEIPT_KEYS
FREEZE_PREDECESSOR_RECEIPT_KEYS = {"receipt_id", "path", "sha256"}
FREEZE_PREDECESSOR_KEYS = {
    "pack_id",
    "pack_path",
    "pack_digest_algorithm",
    "pack_sha256",
    "plan_id",
    "plan_sha256",
    "freeze_receipt",
    "identity_receipt",
    "evidence_set_sha256",
}
FREEZE_RECEIPT_V2_KEYS = (FREEZE_RECEIPT_KEYS - {"supersedes"}) | {"predecessor"}
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
CONTENT_EVIDENCE_RECEIPT_KEYS = {
    "schema_version",
    "evidence_id",
    "kind",
    "status",
    "issued_at_utc",
    "freshness_class",
    "freshness_policy_id",
    "pack_sha256",
    "derivation_commit",
    "dependency_manifest_sha256",
    "facts",
    "checks",
    "reason_codes",
    "assurance",
}
EXECUTION_EVIDENCE_RECEIPT_KEYS = CONTENT_EVIDENCE_RECEIPT_KEYS | {
    "boot_session_id",
    "valid_until_monotonic_ns",
    "environment_fingerprint",
}
GENERIC_EVIDENCE_RECEIPT_SCHEMAS = frozenset(
    {
        EVIDENCE_RECEIPT_SCHEMA,
        CONTENT_EVIDENCE_RECEIPT_SCHEMA,
        EXECUTION_EVIDENCE_RECEIPT_SCHEMA,
    }
)

# R1 clause 6 deliberately leaves the values below to Ed.  The registry is
# the single input for every reserved lifecycle value; this code owns only
# its exact shape and the complete refusal-role census.  The placeholder is
# useful for tooling construction but is never an issuable registry.
R1_FRESHNESS_CLASSES = frozenset(
    {
        "RE_DERIVABLE",
        "EXECUTION_BOUND",
        "TIME_BOUND",
        "SESSION_STATE_BOUND",
        "TEMPORAL_CAPABILITY",
    }
)
R1_REFUSAL_ROLES = frozenset(
    {
        "CLASS_MISMATCH",
        "DEPENDENCY_CHANGED_SET",
        "DEPENDENCY_MANIFEST",
        "FAMILY_PUBLICATION",
        "SUCCESSOR_CHAIN",
        "TEMPORAL_BUDGET",
        "UNKNOWN_POLICY",
        "V1_GRANDFATHERING",
    }
)
FAMILY_PUBLICATION_CHECK_IDS = frozenset(
    {
        "marker_absent",
        "marker_unreadable",
        "marker_noncanonical",
        "marker_schema_mismatch",
        "marker_self_digest_mismatch",
        "lane_inconsistent",
        "lane_inadmissible",
        "registry_mismatch",
        "registry_dormant",
        "roster_mismatch",
        "roster_incomplete",
        "pack_not_member",
        "family_incoherent",
        "head_mismatch",
        "head_unpublished",
        "head_unresolvable",
        "worktree_dirty",
        "pack_digest_mismatch",
        "plan_binding_mismatch",
        "evidence_set_mismatch",
        "freeze_binding_mismatch",
        "freeze_not_pass",
        "predecessor_mismatch",
        "terminal_review_mismatch",
        "confirmation_missing",
        "confirmation_mismatch",
        "tool_mismatch",
        "output_in_tree",
        "output_collision",
    }
)
"""The closed, code-enumerated diagnostic vocabulary (marker ruling item 4).

Closed means: ``FamilyPublicationError`` refuses to construct an id outside
this set, so a diagnostic can never be invented at a call site.  It also means
a member with no raise site is dead weight that the exactness regression would
lock in forever, so every member must have one.

Finish round (2026-08-22, gap G-5) retired three members that had none and
could not honestly acquire one: ``history_shallow`` and ``git_unavailable``
(nothing in this path consults history depth, and an unavailable Git surfaces
through ``head_unresolvable``), and ``internal_error`` (an unhandled fault is
not a family-publication diagnosis and must propagate, not be relabelled).
Three others acquired real raise sites in the same round: ``registry_dormant``
(a registry with no reviewed generation threshold), ``lane_inconsistent`` (a
verification receipt whose lane fields contradict its own phase), and
``marker_self_digest_mismatch`` (marker bytes disagreeing with their sidecar,
previously reported as the vaguer ``marker_unreadable``).  ``head_unpublished``
acquired one by splitting the rollback case out of ``head_mismatch``.
"""
_R1_REGISTRY_KEYS = {
    "schema_version",
    "registry_id",
    "irrelevant_path_allowlist",
    "evidence_policies",
    "row_policies",
    "arm_policy",
    "successor_policy",
    "refusal_vocabulary",
}
_R1_EVIDENCE_POLICY_KEYS = {
    "kind",
    "freshness_class",
    "freshness_policy_id",
    "horizon_ns",
    "environment_comparison",
}
_R1_ROW_POLICY_KEYS = {"row_id", "freshness_policy_id"}
_R1_ARM_POLICY_KEYS = {"capability_horizon_ns", "arm_to_consume_budget_ns"}
_R1_SUCCESSOR_POLICY_KEYS = {
    "successor_pack_ids",
    "cross_chain_numbering",
    "freeze_receipt_v2_predecessor_bindings",
    "family_publication_marker_schema",
}
_R1_SUCCESSOR_POLICY_OPTIONAL_KEYS = {
    # Marker-ruling split S-2: the generation at which family publication first
    # engages is a REVIEWED REGISTRY VALUE, never code prose.  It is optional in
    # the schema only so that lifecycle registries authored before the `_v4`
    # transaction still validate; a registry that omits it cannot reach any
    # family-publication code path, because every reader refuses when it is
    # absent (see ``_family_first_generation``).
    "family_publication_first_generation",
}
_R1_REFUSAL_ENTRY_KEYS = {"role", "code", "type"}
_R1_ED_RESERVED_PREFIX = "ED_RESERVED:"
R1_LIFECYCLE_REGISTRY_PLACEHOLDER = {
    "schema_version": R1_LIFECYCLE_REGISTRY_SCHEMA,
    "registry_id": "ED_RESERVED:r1-lifecycle-registry-id",
    "irrelevant_path_allowlist": [],
    "evidence_policies": [],
    "row_policies": [],
    "arm_policy": {
        "capability_horizon_ns": "ED_RESERVED:arm-capability-horizon-ns",
        "arm_to_consume_budget_ns": "ED_RESERVED:arm-to-consume-budget-ns",
    },
    "successor_policy": {
        "successor_pack_ids": "ED_RESERVED:successor-pack-ids",
        "cross_chain_numbering": "ED_RESERVED:cross-chain-numbering",
        "freeze_receipt_v2_predecessor_bindings": (
            "ED_RESERVED:freeze-receipt-v2-predecessor-bindings"
        ),
        "family_publication_marker_schema": (
            "ED_RESERVED:family-publication-marker-schema"
        ),
    },
    "refusal_vocabulary": [
        {
            "role": role,
            "code": f"ED_RESERVED:refusal-code:{role.lower()}",
            "type": "ED_RESERVED:refusal-type",
        }
        for role in sorted(R1_REFUSAL_ROLES)
    ],
}
LEGACY_CONSUMPTION_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "consumed_at_utc",
    "arm_receipt",
    "pack_sha256",
    "head_commit",
    "volatile_checks",
    "assurance",
}
LAUNCH_ARTIFACT_REFERENCE_KEYS = {"path", "sha256"}
CONSUMPTION_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "consumption_id",
    "consumed_at_utc",
    "consumed_at_monotonic_ns",
    "boot_session_id",
    "pack_id",
    "pack_sha256",
    "plan_id",
    "window_id",
    "arm_receipt",
    "head_commit",
    "arm_context_sha256",
    "launch_manifest",
    "window_environment",
    "window_chain",
    "exec_argv",
    "handoff_token_sha256",
    "volatile_checks",
    "assurance",
}
LAUNCH_MANIFEST_KEYS = {
    "schema_version",
    "boot_session_id",
    "window_plan_root",
    "prewindow_command",
    "launch_command",
}
LAUNCH_LINEAGE_KEYS = {
    "schema_version",
    "collection_boot_session_id",
    "pack_id",
    "plan_id",
    "window_id",
    "bracket_session_id",
    "consumption",
    "start",
    "settle",
    "completion",
}
LAUNCH_LINEAGE_LOCATOR_KEYS = {
    "schema_version",
    "root_role",
    "root_path",
    "launch_lineage",
}
LAUNCH_LINEAGE_ROOT_ROLES = frozenset(
    {"claim_runs_root", "bound_runs_root"}
)
LAUNCH_LIFECYCLE_RECEIPT_KEYS = {
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "issued_at_utc",
    "issued_at_monotonic_ns",
    "boot_session_id",
    "pack_id",
    "pack_sha256",
    "plan_id",
    "window_id",
    "bracket_session_id",
    "window_chain",
    "consumption",
    "predecessor",
    "handoff_token_sha256",
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

# R1 S2: this is the sole freshness-class authority.  Registries name policy
# IDs and class-specific parameters, but can neither introduce an evidence
# kind nor choose its class.  ARM_CAPABILITY is not an evidence-policy row;
# it is included so the same production lifecycle dispatcher owns the fifth
# class as well.
R1_EVIDENCE_FRESHNESS_CLASSES = {
    "ACCEPTANCE_OWNER": "EXECUTION_BOUND",
    "ACCEPTANCE_SUCCESSOR": "EXECUTION_BOUND",
    "BACKUP_PREFLIGHT": "TIME_BOUND",
    "CLOCK_ATTESTATION": "TIME_BOUND",
    "CLOCK_PROBE": "TIME_BOUND",
    "DOCTRINE_PIN": "RE_DERIVABLE",
    "DRY_RUN_REHEARSAL": "EXECUTION_BOUND",
    "ESTIMATOR_IDENTITY": "EXECUTION_BOUND",
    "GIT_CHECKOUT": "EXECUTION_BOUND",
    "IDENTITY_PIN_PROJECTION": "EXECUTION_BOUND",
    "LAUNCH_RECIPE": "SESSION_STATE_BOUND",
    "LEDGER_RESERVATION": "SESSION_STATE_BOUND",
    "MACHINE_PREFLIGHT": "TIME_BOUND",
    "MAINTENANCE_CENSUS": "TIME_BOUND",
    "MINT_TRUST": "EXECUTION_BOUND",
    "MULTICELL_MINT": "EXECUTION_BOUND",
    "OFFLINE_INPUT_INVENTORY": "EXECUTION_BOUND",
    "PACK_AUTHENTICATION": "EXECUTION_BOUND",
    "PACK_FAMILY": "RE_DERIVABLE",
    "POWERMETRICS_PROBE": "TIME_BOUND",
    "POWER_PREFLIGHT": "TIME_BOUND",
    "PRIVILEGE_INSTALLATION": "EXECUTION_BOUND",
    "PROCESS_CENSUS": "TIME_BOUND",
    "REASON_CODE_COVERAGE": "EXECUTION_BOUND",
    "RECEIPT_ORACLE": "EXECUTION_BOUND",
    "RECOVERY_LEDGER_TEST": "EXECUTION_BOUND",
    "ROOT_PREFLIGHT": "SESSION_STATE_BOUND",
    "TERMINAL_REVIEW": "EXECUTION_BOUND",
    "THREE_WINDOW_REGRESSION": "EXECUTION_BOUND",
    "ARM_CAPABILITY": "TEMPORAL_CAPABILITY",
}
if set(R1_EVIDENCE_FRESHNESS_CLASSES) - {"ARM_CAPABILITY"} != set(
    _EVIDENCE_SOURCE_KINDS
):
    raise AssertionError("every evidence kind needs exactly one code freshness class")

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


class EvidenceLifecycleError(ValueError):
    """An R1 refusal whose spelling and type come only from its registry."""

    def __init__(
        self,
        registry: Mapping[str, Any],
        role: str,
        message: str,
        *,
        row_id: str | None = None,
        evidence_id: str | None = None,
    ) -> None:
        entry = _r1_refusal_entry(registry, role)
        super().__init__(message)
        self.role = role
        self.reason_code = str(entry["code"])
        self.reason_type = str(entry["type"])
        self.row_id = row_id
        self.evidence_id = evidence_id

    def refusal(self) -> dict[str, Any]:
        return {
            "type": self.reason_type,
            "code": self.reason_code,
            "row_id": self.row_id,
            "evidence_id": self.evidence_id,
        }


class LaunchLineageError(ValueError):
    """A refusal from D-078's launch-consumption lineage vocabulary."""

    def __init__(self, reason_code: str, message: str) -> None:
        if reason_code not in LAUNCH_LINEAGE_REASON_CODES:
            raise ValueError(f"unregistered launch-lineage reason code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code


HISTSEM_REASON_CODES = frozenset(
    {
        "histsem_binding_mismatch",
        "histsem_commit_off_lineage",
        "histsem_commit_unpublished",
        "histsem_commit_unresolvable",
        "histsem_git_unavailable",
        "histsem_historical_digest_mismatch",
        "histsem_historical_tree_anomalous",
        "histsem_historical_tree_not_pre_authoring",
        "histsem_history_unavailable",
        "histsem_history_shallow",
        "histsem_pack_absent_at_commit",
        "histsem_pinset_absent",
        "histsem_pinset_invalid",
        "histsem_pinset_mismatch",
        "histsem_post_authoring_delta_unexpected",
        "histsem_receipt_head_malformed",
    }
)


class HistoricalSemanticsError(ValueError):
    """A refusal from the disjoint RECEIPT-HISTSEM-01 vocabulary."""

    def __init__(self, reason_code: str, message: str) -> None:
        if reason_code not in HISTSEM_REASON_CODES:
            raise ValueError(f"unregistered historical-semantics code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code


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


def _freeze_receipt_ordinal(value: object, where: str) -> int:
    """Parse a governed ``freeze-<4+ digits>`` receipt ID into its ordinal."""

    receipt_id = _require_string(value, where)
    match = _RECEIPT_NAME_RE["freeze"].fullmatch(f"{receipt_id}.json")
    if match is None:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} is not a governed freeze receipt ID"
        )
    number = int(match.group(1))
    if number < 1:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} ordinal must be positive"
        )
    return number


def _pack_generation(pack_id: str) -> int:
    """Return the family generation encoded by a pack ID's ``_v<N>`` suffix.

    This generalizes to arbitrary ``_v<N>``, not only the v2 family the D-139
    consult licensed.  The lead ACCEPTED that generalization (delta-8 F4) as
    consistent with the generational-induction design: nothing is unlocked by
    parsing a higher generation, because a future ``_v3`` pack still has to be
    admitted by the live ``_PROFILE_BY_PACK`` map and the row registry before
    any freeze, dry-run, arm, or evidence path will look at it at all.
    """

    match = _PACK_GENERATION_RE.search(pack_id)
    return int(match.group(1)) if match is not None else 1


def _validate_freeze_predecessor(
    value: object, where: str = "freeze receipt.predecessor"
) -> int:
    """Exact-key structural validation of D-139's predecessor binding.

    This is byte-level shape only.  Filesystem authentication of the referenced
    predecessor pack lives in ``_authenticate_freeze_predecessor``.
    """

    item = _require_exact_keys(value, FREEZE_PREDECESSOR_KEYS, where)
    _require_path_component(item["pack_id"], f"{where}.pack_id")
    pack_path = _require_relative_path(item["pack_path"], f"{where}.pack_path")
    if PurePosixPath(pack_path).name != item["pack_id"]:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.pack_path must end in pack_id"
        )
    if item["pack_digest_algorithm"] != PACK_DIGEST_ALGORITHM:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.pack_digest_algorithm is invalid"
        )
    for name in ("pack_sha256", "plan_sha256", "evidence_set_sha256"):
        _require_lower_sha256(item[name], f"{where}.{name}")
    _require_string(item["plan_id"], f"{where}.plan_id")
    freeze = _require_exact_keys(
        item["freeze_receipt"],
        FREEZE_PREDECESSOR_RECEIPT_KEYS,
        f"{where}.freeze_receipt",
    )
    ordinal = _freeze_receipt_ordinal(
        freeze["receipt_id"], f"{where}.freeze_receipt.receipt_id"
    )
    freeze_path = _require_relative_path(
        freeze["path"], f"{where}.freeze_receipt.path"
    )
    _require_lower_sha256(freeze["sha256"], f"{where}.freeze_receipt.sha256")
    if PurePosixPath(freeze_path).name != f"{freeze['receipt_id']}.json":
        raise ArmReadinessError(
            "readiness_schema_invalid",
            f"{where}.freeze_receipt path and receipt_id disagree",
        )
    identity = _require_exact_keys(
        item["identity_receipt"],
        FREEZE_PREDECESSOR_RECEIPT_KEYS,
        f"{where}.identity_receipt",
    )
    _require_string(identity["receipt_id"], f"{where}.identity_receipt.receipt_id")
    _require_relative_path(identity["path"], f"{where}.identity_receipt.path")
    _require_lower_sha256(identity["sha256"], f"{where}.identity_receipt.sha256")
    return ordinal


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


def _r1_contains_reserved(value: object) -> bool:
    if isinstance(value, str):
        return value.startswith(_R1_ED_RESERVED_PREFIX)
    if isinstance(value, Mapping):
        return any(_r1_contains_reserved(item) for item in value.values())
    if isinstance(value, list):
        return any(_r1_contains_reserved(item) for item in value)
    return False


def validate_r1_lifecycle_registry(
    value: object,
    *,
    require_resolved: bool = True,
    require_registered_codes: bool = False,
) -> Mapping[str, Any]:
    """Validate the single R1 lifecycle-policy input.

    Clause-6 values may exist as explicit ``ED_RESERVED:`` placeholders for
    dry construction only.  Every issuance/consumption caller uses the
    default ``require_resolved=True`` and therefore fails closed.

    ``require_registered_codes`` is the marker ruling's REGISTRY-LOAD closure
    check: every refusal code the registry declares must already exist in
    ``READINESS_REASON_CODES`` with the same ``REASON_TYPE_BY_CODE`` type.  It
    is enabled on exactly one path -- ``validate_registry``, i.e. the tracked
    registry that ``load_registry`` reads and that ``_receipt_refusal``
    actually consults, where an unregistered code would explode into
    ``readiness_internal_error``.  Callers that hand this validator a synthetic
    lifecycle registry of their own construction are not on that path and are
    not closed against the production vocabulary.
    """

    registry = _require_exact_keys(value, _R1_REGISTRY_KEYS, "R1 lifecycle registry")
    if registry["schema_version"] != R1_LIFECYCLE_REGISTRY_SCHEMA:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 lifecycle registry schema_version is invalid",
        )
    registry_id = _require_string(
        registry["registry_id"], "R1 lifecycle registry.registry_id"
    )
    if not registry_id:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "R1 lifecycle registry_id is empty"
        )

    allowlist = registry["irrelevant_path_allowlist"]
    if (
        not isinstance(allowlist, list)
        or allowlist != sorted(set(allowlist))
        or any(
            not isinstance(path, str)
            or not path
            or "\\" in path
            or Path(path).is_absolute()
            or any(part in {"", ".", ".."} for part in PurePosixPath(path).parts)
            for path in allowlist
        )
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 irrelevant-path allowlist must be sorted unique exact repository paths",
        )

    raw_policies = registry["evidence_policies"]
    if not isinstance(raw_policies, list):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "R1 evidence policies must be an array"
        )
    policy_kinds: list[str] = []
    policy_ids: list[str] = []
    class_mismatches: list[str] = []
    contradictory_policies: list[str] = []
    for index, raw_policy in enumerate(raw_policies):
        policy = _require_exact_keys(
            raw_policy, _R1_EVIDENCE_POLICY_KEYS, f"R1 evidence_policies[{index}]"
        )
        kind = _require_string(policy["kind"], f"R1 evidence_policies[{index}].kind")
        policy_id = _require_string(
            policy["freshness_policy_id"],
            f"R1 evidence_policies[{index}].freshness_policy_id",
        )
        policy_kinds.append(kind)
        policy_ids.append(policy_id)
        claimed_class = policy["freshness_class"]
        if claimed_class not in R1_FRESHNESS_CLASSES:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 evidence_policies[{index}].freshness_class is invalid",
            )
        code_class = R1_EVIDENCE_FRESHNESS_CLASSES.get(kind)
        if code_class is None or claimed_class != code_class:
            class_mismatches.append(
                f"{kind!r}: registry={claimed_class!r}, code={code_class!r}"
            )
        horizon = policy["horizon_ns"]
        if not (
            horizon is None
            or (isinstance(horizon, int) and not isinstance(horizon, bool) and horizon > 0)
            or (
                isinstance(horizon, str)
                and horizon.startswith(_R1_ED_RESERVED_PREFIX)
            )
        ):
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 evidence_policies[{index}].horizon_ns is invalid",
            )
        environment_comparison = _require_string(
            policy["environment_comparison"],
            f"R1 evidence_policies[{index}].environment_comparison",
        )
        positive_or_reserved_horizon = (
            isinstance(horizon, int)
            and not isinstance(horizon, bool)
            and horizon > 0
        ) or (
            isinstance(horizon, str)
            and horizon.startswith(_R1_ED_RESERVED_PREFIX)
        )
        if code_class == "RE_DERIVABLE" and (
            horizon is not None or environment_comparison != "NOT_APPLICABLE"
        ):
            contradictory_policies.append(
                f"{kind!r} RE_DERIVABLE must have horizon_ns=null and "
                "environment_comparison=NOT_APPLICABLE"
            )
        elif code_class in {"TIME_BOUND", "SESSION_STATE_BOUND"} and (
            not positive_or_reserved_horizon
            or environment_comparison != "NOT_APPLICABLE"
        ):
            contradictory_policies.append(
                f"{kind!r} {code_class} must have a positive horizon and "
                "environment_comparison=NOT_APPLICABLE"
            )
        elif code_class == "EXECUTION_BOUND" and (
            not positive_or_reserved_horizon
            or environment_comparison == "NOT_APPLICABLE"
        ):
            contradictory_policies.append(
                f"{kind!r} EXECUTION_BOUND must have a positive horizon and "
                "an applicable environment comparison"
            )
    if policy_kinds != sorted(set(policy_kinds)):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 evidence kinds must be sorted and unique",
        )
    definitions_by_policy_id: dict[str, tuple[object, object, object]] = {}
    for policy in raw_policies:
        definition = (
            policy["freshness_class"],
            policy["horizon_ns"],
            policy["environment_comparison"],
        )
        prior = definitions_by_policy_id.setdefault(
            policy["freshness_policy_id"], definition
        )
        if prior != definition:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                "one freshness policy ID has conflicting definitions",
            )

    raw_rows = registry["row_policies"]
    if not isinstance(raw_rows, list):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "R1 row policies must be an array"
        )
    row_ids: list[str] = []
    for index, raw_row in enumerate(raw_rows):
        row = _require_exact_keys(
            raw_row, _R1_ROW_POLICY_KEYS, f"R1 row_policies[{index}]"
        )
        row_ids.append(
            _require_string(row["row_id"], f"R1 row_policies[{index}].row_id")
        )
        referenced = _require_string(
            row["freshness_policy_id"],
            f"R1 row_policies[{index}].freshness_policy_id",
        )
        if referenced not in set(policy_ids) and not referenced.startswith(
            _R1_ED_RESERVED_PREFIX
        ):
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 row_policies[{index}] references an unknown policy",
            )
    if row_ids != sorted(set(row_ids)):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "R1 row policy IDs must be sorted and unique"
        )

    arm_policy = _require_exact_keys(
        registry["arm_policy"], _R1_ARM_POLICY_KEYS, "R1 arm_policy"
    )
    for name in sorted(_R1_ARM_POLICY_KEYS):
        item = arm_policy[name]
        if not (
            (isinstance(item, int) and not isinstance(item, bool) and item > 0)
            or (isinstance(item, str) and item.startswith(_R1_ED_RESERVED_PREFIX))
        ):
            raise ArmReadinessError(
                "readiness_row_registry_mismatch", f"R1 arm_policy.{name} is invalid"
            )

    raw_successor_policy = registry["successor_policy"]
    if not isinstance(raw_successor_policy, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "R1 successor_policy must be an object"
        )
    observed_successor_keys = set(raw_successor_policy)
    if observed_successor_keys - (
        _R1_SUCCESSOR_POLICY_KEYS | _R1_SUCCESSOR_POLICY_OPTIONAL_KEYS
    ):
        raise ArmReadinessError(
            "readiness_unknown_key",
            "R1 successor_policy contains keys outside the closed enumeration",
        )
    if _R1_SUCCESSOR_POLICY_KEYS - observed_successor_keys:
        raise ArmReadinessError(
            "readiness_schema_invalid",
            "R1 successor_policy is missing required keys",
        )
    successor_policy = raw_successor_policy
    generation = successor_policy.get("family_publication_first_generation")
    if generation is not None and not (
        (isinstance(generation, str) and generation.startswith(_R1_ED_RESERVED_PREFIX))
        or (
            isinstance(generation, int)
            and not isinstance(generation, bool)
            and generation >= 1
        )
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 successor_policy.family_publication_first_generation is invalid",
        )
    pack_ids = successor_policy["successor_pack_ids"]
    if not (
        (isinstance(pack_ids, str) and pack_ids.startswith(_R1_ED_RESERVED_PREFIX))
        or (
            isinstance(pack_ids, Mapping)
            and set(pack_ids) == set(_SUCCESSOR_PROFILE_PATTERNS)
            and all(
                isinstance(pack_id, str)
                and pack_id
                and "/" not in pack_id
                and "\\" not in pack_id
                for pack_id in pack_ids.values()
            )
            and len(set(pack_ids.values())) == 3
        )
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 successor pack IDs are invalid",
        )
    predecessor_bindings = successor_policy[
        "freeze_receipt_v2_predecessor_bindings"
    ]
    if not (
        isinstance(predecessor_bindings, str)
        and predecessor_bindings.startswith(_R1_ED_RESERVED_PREFIX)
    ) and not (
        isinstance(predecessor_bindings, list)
        and bool(predecessor_bindings)
        and predecessor_bindings == sorted(set(predecessor_bindings))
        and all(isinstance(item, str) and item for item in predecessor_bindings)
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 freeze-v2 predecessor bindings are invalid",
        )
    for name in ("cross_chain_numbering", "family_publication_marker_schema"):
        _require_string(successor_policy[name], f"R1 successor_policy.{name}")

    raw_refusals = registry["refusal_vocabulary"]
    if not isinstance(raw_refusals, list):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "R1 refusal vocabulary must be an array"
        )
    roles: list[str] = []
    codes: list[str] = []
    for index, raw_entry in enumerate(raw_refusals):
        entry = _require_exact_keys(
            raw_entry, _R1_REFUSAL_ENTRY_KEYS, f"R1 refusal_vocabulary[{index}]"
        )
        role = _require_string(
            entry["role"], f"R1 refusal_vocabulary[{index}].role"
        )
        code = _require_string(
            entry["code"], f"R1 refusal_vocabulary[{index}].code"
        )
        reason_type = _require_string(
            entry["type"], f"R1 refusal_vocabulary[{index}].type"
        )
        roles.append(role)
        codes.append(code)
        if not code.startswith(_R1_ED_RESERVED_PREFIX) and re.fullmatch(
            r"[a-z][a-z0-9_]*", code
        ) is None:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 refusal_vocabulary[{index}].code is invalid",
            )
        if not reason_type.startswith(_R1_ED_RESERVED_PREFIX) and reason_type not in {
            "STRUCTURE",
            "CUSTODY",
            "GIT",
            "LIFECYCLE",
            "POLICY",
            "IDENTITY",
            "ENVIRONMENT",
        }:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 refusal_vocabulary[{index}].type is invalid",
            )
        if (
            require_registered_codes
            and not code.startswith(_R1_ED_RESERVED_PREFIX)
            and (
                code not in READINESS_REASON_CODES
                or REASON_TYPE_BY_CODE.get(code) != reason_type
            )
        ):
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"R1 refusal_vocabulary[{index}] is not closed by code/type authority",
            )
    if roles != sorted(R1_REFUSAL_ROLES) or len(codes) != len(set(codes)):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 refusal vocabulary must register every role exactly once",
        )
    if class_mismatches:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            f"CLASS_MISMATCH: registry cannot override code classes: {class_mismatches!r}",
        )
    if contradictory_policies:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            f"UNKNOWN_POLICY: contradictory lifecycle fields: {contradictory_policies!r}",
        )
    if require_resolved and (
        _r1_contains_reserved(registry)
        or not raw_policies
        or not raw_rows
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 lifecycle registry contains unresolved Ed-reserved values",
        )
    return registry


def _r1_policy_for_kind(
    registry: Mapping[str, Any], kind: str
) -> Mapping[str, Any]:
    validated = validate_r1_lifecycle_registry(registry)
    matches = [
        policy for policy in validated["evidence_policies"] if policy["kind"] == kind
    ]
    if len(matches) != 1:
        raise EvidenceLifecycleError(
            validated, "UNKNOWN_POLICY", f"no unique R1 policy for evidence kind {kind!r}"
        )
    return matches[0]


def _r1_refusal_entry(
    registry: Mapping[str, Any], role: str
) -> Mapping[str, Any]:
    if role not in R1_REFUSAL_ROLES:
        raise ValueError(f"unknown R1 refusal role {role!r}")
    validated = validate_r1_lifecycle_registry(registry)
    matches = [
        entry for entry in validated["refusal_vocabulary"] if entry["role"] == role
    ]
    if len(matches) != 1:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", f"R1 refusal role {role!r} is not unique"
        )
    return matches[0]


def validate_registry(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "registry must be an object"
        )
    schema = value.get("schema_version")
    registry = _require_exact_keys(
        value,
        R1_ROW_REGISTRY_KEYS if schema == R1_ROW_REGISTRY_SCHEMA else REGISTRY_KEYS,
        "registry",
    )
    if schema not in {ROW_REGISTRY_SCHEMA, R1_ROW_REGISTRY_SCHEMA}:
        raise ArmReadinessError(
            "readiness_schema_invalid", "registry schema_version is invalid"
        )
    if schema == ROW_REGISTRY_SCHEMA and registry["registry_id"] != ROW_REGISTRY_ID:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", "registry_id is invalid"
        )
    if schema == R1_ROW_REGISTRY_SCHEMA:
        _require_string(registry["registry_id"], "registry.registry_id")
        validate_r1_lifecycle_registry(
            registry["freeze_evidence_lifecycle"], require_registered_codes=True
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
    if schema == R1_ROW_REGISTRY_SCHEMA:
        lifecycle = registry["freeze_evidence_lifecycle"]
        lifecycle_row_ids = [item["row_id"] for item in lifecycle["row_policies"]]
        if lifecycle_row_ids != row_ids:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                "R1 lifecycle registry must assign a policy to every row",
            )
        policy_id_by_kind = {
            item["kind"]: item["freshness_policy_id"]
            for item in lifecycle["evidence_policies"]
        }
        policy_id_by_row = {
            item["row_id"]: item["freshness_policy_id"]
            for item in lifecycle["row_policies"]
        }
        for row in rows:
            expected_policy_ids = {
                policy_id_by_kind.get(kind)
                for kind in row["required_evidence_kinds"]
            }
            if (
                None in expected_policy_ids
                or len(expected_policy_ids) != 1
                or policy_id_by_row[row["row_id"]] not in expected_policy_ids
            ):
                raise ArmReadinessError(
                    "readiness_row_registry_mismatch",
                    f"R1 row {row['row_id']} does not match its evidence policy",
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


def _validate_legacy_evidence_receipt(value: object) -> Mapping[str, Any]:
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


def _validate_r1_evidence_receipt_common(
    value: object, *, execution_bound: bool
) -> Mapping[str, Any]:
    keys = (
        EXECUTION_EVIDENCE_RECEIPT_KEYS
        if execution_bound
        else CONTENT_EVIDENCE_RECEIPT_KEYS
    )
    where = "execution evidence receipt" if execution_bound else "content evidence receipt"
    receipt = _require_exact_keys(value, keys, where)
    expected_schema = (
        EXECUTION_EVIDENCE_RECEIPT_SCHEMA
        if execution_bound
        else CONTENT_EVIDENCE_RECEIPT_SCHEMA
    )
    expected_class = "EXECUTION_BOUND" if execution_bound else "RE_DERIVABLE"
    if receipt["schema_version"] != expected_schema:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} schema is invalid"
        )
    if receipt["freshness_class"] != expected_class:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} freshness class is invalid"
        )
    for name in (
        "evidence_id",
        "kind",
        "issued_at_utc",
        "freshness_policy_id",
    ):
        _require_string(receipt[name], f"{where}.{name}")
    _require_lower_git_oid(receipt["derivation_commit"], f"{where}.derivation_commit")
    _require_lower_sha256(receipt["pack_sha256"], f"{where}.pack_sha256")
    _require_lower_sha256(
        receipt["dependency_manifest_sha256"],
        f"{where}.dependency_manifest_sha256",
    )
    if execution_bound:
        _require_boot_session_id(receipt["boot_session_id"], f"{where}.boot_session_id")
        _require_int(
            receipt["valid_until_monotonic_ns"],
            f"{where}.valid_until_monotonic_ns",
            minimum=1,
        )
        fingerprint = receipt["environment_fingerprint"]
        if not isinstance(fingerprint, Mapping):
            raise ArmReadinessError(
                "readiness_schema_invalid", f"{where}.environment_fingerprint is invalid"
            )
        try:
            render_json(fingerprint)
        except (TypeError, ValueError) as exc:
            raise ArmReadinessError(
                "readiness_schema_invalid",
                f"{where}.environment_fingerprint is not strict JSON",
            ) from exc
    if receipt["status"] not in RECEIPT_STATUSES:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} status is invalid"
        )
    facts = receipt["facts"]
    checks = receipt["checks"]
    reasons = receipt["reason_codes"]
    if not isinstance(facts, list) or not isinstance(checks, list) or not isinstance(reasons, list):
        raise ArmReadinessError(
            "readiness_schema_invalid",
            f"{where} facts, checks, and reason_codes must be arrays",
        )
    for index, raw_fact in enumerate(facts):
        fact = _require_exact_keys(raw_fact, FACT_KEYS, f"{where}.facts[{index}]")
        _require_string(fact["fact_id"], f"{where}.facts[{index}].fact_id")
        _require_string(fact["value_type"], f"{where}.facts[{index}].value_type")
        if fact["source_kind"] not in SOURCE_KINDS:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"{where}.facts[{index}].source_kind is invalid"
            )
        _require_relative_path(
            fact["source_path"], f"{where}.facts[{index}].source_path"
        )
        _require_lower_sha256(
            fact["source_sha256"], f"{where}.facts[{index}].source_sha256"
        )
        try:
            render_json(fact["value"])
        except (TypeError, ValueError) as exc:
            raise ArmReadinessError(
                "readiness_schema_invalid",
                f"{where}.facts[{index}].value is not strict JSON",
            ) from exc
    for index, raw_check in enumerate(checks):
        check = _require_exact_keys(raw_check, EVIDENCE_CHECK_KEYS, f"{where}.checks[{index}]")
        _require_string(check["check_id"], f"{where}.checks[{index}].check_id")
        if check["status"] not in RECEIPT_STATUSES:
            raise ArmReadinessError(
                "readiness_schema_invalid", f"{where}.checks[{index}].status is invalid"
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
            f"{where}.reason_codes must be sorted domain-code strings",
        )
    if (receipt["status"] == "PASS") == bool(reasons):
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where} status and reason_codes disagree"
        )
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_evidence_receipt(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "evidence receipt must be an object"
        )
    schema = value.get("schema_version")
    if schema == EVIDENCE_RECEIPT_SCHEMA:
        return _validate_legacy_evidence_receipt(value)
    if schema == CONTENT_EVIDENCE_RECEIPT_SCHEMA:
        return _validate_r1_evidence_receipt_common(value, execution_bound=False)
    if schema == EXECUTION_EVIDENCE_RECEIPT_SCHEMA:
        return _validate_r1_evidence_receipt_common(value, execution_bound=True)
    raise ArmReadinessError(
        "readiness_schema_invalid", "evidence receipt schema is invalid"
    )


def validate_freeze_receipt(value: object) -> Mapping[str, Any]:
    """Validate a v1 or v2 freeze receipt under its own exact-key vocabulary."""

    declared = value.get("schema_version") if isinstance(value, Mapping) else None
    successor = declared == FREEZE_RECEIPT_V2_SCHEMA
    receipt = _require_exact_keys(
        value,
        FREEZE_RECEIPT_V2_KEYS if successor else FREEZE_RECEIPT_V1_KEYS,
        "freeze receipt",
    )
    if receipt["schema_version"] not in {
        FREEZE_RECEIPT_V1_SCHEMA,
        FREEZE_RECEIPT_V2_SCHEMA,
    }:
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
    if successor:
        predecessor_ordinal = _validate_freeze_predecessor(receipt["predecessor"])
        ordinal = _freeze_receipt_ordinal(
            receipt["receipt_id"], "freeze receipt.receipt_id"
        )
        if ordinal != predecessor_ordinal + 1:
            raise ArmReadinessError(
                "readiness_schema_invalid",
                "freeze receipt ordinal is not the predecessor ordinal plus one",
            )
    else:
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


def _validate_launch_artifact_reference(
    value: object, where: str
) -> Mapping[str, Any]:
    reference = _require_exact_keys(
        value, LAUNCH_ARTIFACT_REFERENCE_KEYS, where
    )
    _require_string(reference["path"], f"{where}.path")
    if not Path(str(reference["path"])).is_absolute():
        raise ArmReadinessError(
            "readiness_schema_invalid", f"{where}.path must be absolute"
        )
    _require_lower_sha256(reference["sha256"], f"{where}.sha256")
    return reference


def _validate_string_argv(value: object, where: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ArmReadinessError(
            "readiness_schema_invalid",
            f"{where} must be a nonempty array of nonempty strings",
        )
    return value


def validate_launch_manifest(value: object) -> Mapping[str, Any]:
    manifest = _require_exact_keys(value, LAUNCH_MANIFEST_KEYS, "launch manifest")
    if manifest["schema_version"] != LAUNCH_MANIFEST_SCHEMA:
        raise ArmReadinessError(
            "readiness_schema_invalid", "launch manifest schema is invalid"
        )
    _require_boot_session_id(manifest["boot_session_id"], "launch manifest.boot_session_id")
    _require_string(manifest["window_plan_root"], "launch manifest.window_plan_root")
    if not Path(str(manifest["window_plan_root"])).is_absolute():
        raise ArmReadinessError(
            "readiness_schema_invalid", "launch manifest.window_plan_root must be absolute"
        )
    _validate_string_argv(manifest["prewindow_command"], "launch manifest.prewindow_command")
    _validate_string_argv(manifest["launch_command"], "launch manifest.launch_command")
    return manifest


def validate_consumption_receipt(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "consumption receipt must be an object"
        )
    schema = value.get("schema_version")
    keys = (
        LEGACY_CONSUMPTION_RECEIPT_KEYS
        if schema == LEGACY_CONSUMPTION_RECEIPT_SCHEMA
        else CONSUMPTION_RECEIPT_KEYS
    )
    receipt = _require_exact_keys(value, keys, "consumption receipt")
    if schema not in {
        LEGACY_CONSUMPTION_RECEIPT_SCHEMA,
        CONSUMPTION_RECEIPT_SCHEMA,
    } or receipt["receipt_kind"] != "launch_consumption":
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
    if schema == CONSUMPTION_RECEIPT_SCHEMA:
        _require_string(receipt["consumption_id"], "consumption receipt.consumption_id")
        _require_int(
            receipt["consumed_at_monotonic_ns"],
            "consumption receipt.consumed_at_monotonic_ns",
        )
        if receipt["consumed_at_monotonic_ns"] < 0:
            raise ArmReadinessError(
                "readiness_schema_invalid",
                "consumption receipt.consumed_at_monotonic_ns must be nonnegative",
            )
        _require_boot_session_id(
            receipt["boot_session_id"], "consumption receipt.boot_session_id"
        )
        for name in ("pack_id", "plan_id", "window_id"):
            _require_string(receipt[name], f"consumption receipt.{name}")
        _require_lower_sha256(
            receipt["arm_context_sha256"],
            "consumption receipt.arm_context_sha256",
        )
        for name in ("launch_manifest", "window_environment", "window_chain"):
            _validate_launch_artifact_reference(
                receipt[name], f"consumption receipt.{name}"
            )
        _validate_string_argv(receipt["exec_argv"], "consumption receipt.exec_argv")
        _require_lower_sha256(
            receipt["handoff_token_sha256"],
            "consumption receipt.handoff_token_sha256",
        )
    if not isinstance(receipt["volatile_checks"], list) or receipt["volatile_checks"] != sorted(set(receipt["volatile_checks"])):
        raise ArmReadinessError(
            "readiness_schema_invalid", "volatile_checks must be sorted and unique"
        )
    _validate_assurance(receipt["assurance"])
    return receipt


def validate_launch_lifecycle_receipt(value: object) -> Mapping[str, Any]:
    receipt = _require_exact_keys(
        value, LAUNCH_LIFECYCLE_RECEIPT_KEYS, "launch lifecycle receipt"
    )
    expected = {
        "launch_start": LAUNCH_START_RECEIPT_SCHEMA,
        "launch_settle": LAUNCH_SETTLE_RECEIPT_SCHEMA,
        "launch_completion": LAUNCH_COMPLETION_RECEIPT_SCHEMA,
    }
    kind = receipt["receipt_kind"]
    if kind not in expected or receipt["schema_version"] != expected[kind]:
        raise ArmReadinessError(
            "readiness_receipt_kind_invalid", "launch lifecycle receipt kind is invalid"
        )
    for name in (
        "receipt_id",
        "pack_id",
        "plan_id",
        "window_id",
        "bracket_session_id",
    ):
        _require_string(receipt[name], f"launch lifecycle receipt.{name}")
    _require_string(receipt["issued_at_utc"], "launch lifecycle receipt.issued_at_utc")
    _require_int(
        receipt["issued_at_monotonic_ns"],
        "launch lifecycle receipt.issued_at_monotonic_ns",
    )
    _require_boot_session_id(
        receipt["boot_session_id"], "launch lifecycle receipt.boot_session_id"
    )
    _require_lower_sha256(
        receipt["pack_sha256"], "launch lifecycle receipt.pack_sha256"
    )
    _validate_launch_artifact_reference(
        receipt["window_chain"], "launch lifecycle receipt.window_chain"
    )
    _validate_launch_artifact_reference(
        receipt["consumption"], "launch lifecycle receipt.consumption"
    )
    _validate_launch_artifact_reference(
        receipt["predecessor"], "launch lifecycle receipt.predecessor"
    )
    if kind == "launch_start":
        _require_lower_sha256(
            receipt["handoff_token_sha256"],
            "launch lifecycle receipt.handoff_token_sha256",
        )
    elif receipt["handoff_token_sha256"] is not None:
        raise ArmReadinessError(
            "readiness_schema_invalid",
            "only the start receipt may name the handoff-token digest",
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


RECEIPT_HISTSEM_PINSET_RELATIVE_PATH = (
    Path("configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"),
    Path("configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"),
)
RECEIPT_HISTSEM_PINSET_SCHEMA = "joulewise.receipt_histsem_pinset.v1"
R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS = frozenset(
    {RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix()}
)
"""Allowlist entries D-151 condition 2 forgives only under a digest condition.

Membership in ``irrelevant_path_allowlist`` names a path as *eligible* for
subtraction from the R1 changed set.  For every path in this set that eligibility
is not sufficient: the bytes committed at the reviewed HEAD must additionally
hash to the digest Ed recorded in the step-6 confirmation table's matching
section (the C -> S edge).  Without that confirmation the path stays in the
relevant set and the gate refuses ``DEPENDENCY_CHANGED_SET``.
"""
_HISTSEM_CUSTODY_DIRECTORIES = frozenset(
    {
        "arm_readiness.evidence",
        "arm_readiness.freeze.receipts",
        "arm_readiness.sources",
        "identity_pin_projection.receipts",
    }
)
_HISTSEM_ALLOWED_MODIFICATIONS = frozenset(
    {
        "generate_configs.py",
        "plan_tree.json",
        "plan_tree.sha256",
        "producer_contract.json",
    }
)


def _histsem_git(
    repository: Path, *args: str
) -> tuple[int, bytes, bytes]:
    """Run one bounded, read-only Git query without fetch or repair."""

    try:
        completed = subprocess.run(
            ("git", "-C", str(repository), *args),
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise HistoricalSemanticsError(
            "histsem_git_unavailable", f"cannot execute historical Git proof: {exc}"
        ) from exc
    return completed.returncode, completed.stdout, completed.stderr


def _histsem_repository_and_pack(pack_root: Path) -> tuple[Path, str]:
    try:
        repository, _pack_prefix, pack_relative = _repository_and_pack_relative(
            pack_root
        )
    except ArmReadinessError as exc:
        reason_code = (
            "histsem_history_unavailable"
            if exc.reason_code == "readiness_pack_not_committed"
            else "histsem_git_unavailable"
        )
        raise HistoricalSemanticsError(
            reason_code, f"cannot locate historical pack repository: {exc}"
        ) from exc
    except OSError as exc:
        raise HistoricalSemanticsError(
            "histsem_git_unavailable", f"cannot locate historical pack repository: {exc}"
        ) from exc
    return repository, pack_relative


def _histsem_has_git_metadata(pack_root: Path) -> bool:
    """Return whether a pack is below a path that advertises Git metadata."""

    try:
        root = pack_root.resolve(strict=True)
    except OSError:
        return False
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


def _historical_pack_tree(
    repository: Path | str,
    pack_path: Path | str,
    head_commit: str,
) -> tuple[str, tuple[str, ...]]:
    """Return the D-134 digest and paths for a tree made only of Git objects."""

    repo = Path(repository).resolve(strict=True)
    pack_relative = PurePosixPath(str(pack_path).replace(os.sep, "/")).as_posix()
    if (
        pack_relative in {"", "."}
        or pack_relative.startswith("/")
        or ".." in PurePosixPath(pack_relative).parts
    ):
        raise HistoricalSemanticsError(
            "histsem_historical_tree_anomalous", "historical pack path is not relative"
        )
    if head_commit != "HEAD" and re.fullmatch(r"[0-9a-f]{40}", head_commit) is None:
        raise HistoricalSemanticsError(
            "histsem_receipt_head_malformed",
            "historical head_commit must be lowercase full-length SHA-1",
        )
    code, shallow_raw, _stderr = _histsem_git(
        repo, "rev-parse", "--is-shallow-repository"
    )
    if code != 0:
        raise HistoricalSemanticsError(
            "histsem_git_unavailable", "cannot determine whether Git history is shallow"
        )
    if shallow_raw.rstrip(b"\n") == b"true":
        raise HistoricalSemanticsError(
            "histsem_history_shallow", "historical semantics require a full-history checkout"
        )
    code, _stdout, _stderr = _histsem_git(
        repo, "cat-file", "-e", f"{head_commit}^{{commit}}"
    )
    if code != 0:
        raise HistoricalSemanticsError(
            "histsem_commit_unresolvable", f"historical commit {head_commit} is unavailable"
        )
    code, tree_raw, _stderr = _histsem_git(
        repo, "ls-tree", "-rz", "--full-tree", head_commit, "--", pack_relative
    )
    if code != 0:
        raise HistoricalSemanticsError(
            "histsem_history_unavailable", "historical pack tree cannot be read"
        )
    prefix = pack_relative.encode("utf-8") + b"/"
    entries: dict[bytes, tuple[str, str]] = {}
    for record in tree_raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, repository_path = record.split(b"\t", 1)
            mode_raw, type_raw, oid_raw = metadata.split(b" ", 2)
            mode = mode_raw.decode("ascii", errors="strict")
            object_type = type_raw.decode("ascii", errors="strict")
            oid = oid_raw.decode("ascii", errors="strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise HistoricalSemanticsError(
                "histsem_historical_tree_anomalous", "malformed historical tree entry"
            ) from exc
        if not repository_path.startswith(prefix):
            raise HistoricalSemanticsError(
                "histsem_historical_tree_anomalous", "Git returned an out-of-pack path"
            )
        relative_raw = repository_path[len(prefix) :]
        try:
            relative_raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise HistoricalSemanticsError(
                "histsem_historical_tree_anomalous", "historical tree has a non-UTF-8 path"
            ) from exc
        if (
            not relative_raw
            or mode not in {"100644", "100755"}
            or object_type != "blob"
            or relative_raw in entries
        ):
            raise HistoricalSemanticsError(
                "histsem_historical_tree_anomalous",
                f"inadmissible historical tree entry {relative_raw!r}",
            )
        entries[relative_raw] = (mode, oid)
    if not entries:
        raise HistoricalSemanticsError(
            "histsem_pack_absent_at_commit",
            f"pack {pack_relative!r} is absent at {head_commit}",
        )
    framed = bytearray(PACK_DIGEST_DOMAIN)
    decoded_paths: list[str] = []
    for relative_raw in sorted(entries):
        mode, oid = entries[relative_raw]
        code, blob, _stderr = _histsem_git(repo, "cat-file", "blob", oid)
        if code != 0:
            raise HistoricalSemanticsError(
                "histsem_history_unavailable", f"historical blob {oid} cannot be read"
            )
        framed.extend(relative_raw)
        framed.extend(b"\0")
        framed.extend(mode.encode("ascii"))
        framed.extend(b"\0")
        framed.extend(str(len(blob)).encode("ascii"))
        framed.extend(b"\0")
        framed.extend(sha256_bytes(blob).encode("ascii"))
        framed.extend(b"\n")
        decoded_paths.append(relative_raw.decode("utf-8"))
    return sha256_bytes(bytes(framed)), tuple(decoded_paths)


def historical_pack_tree_sha256(
    repository: Path | str,
    pack_path: Path | str,
    head_commit: str,
) -> str:
    """Hash ``pack_path`` at ``head_commit`` using only local Git objects."""

    digest, _paths = _historical_pack_tree(repository, pack_path, head_commit)
    return digest


def _histsem_exact_keys(value: object, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise HistoricalSemanticsError(
            "histsem_pinset_invalid", f"{where} must contain exactly {sorted(keys)!r}"
        )
    return value


def _validate_histsem_pinset(value: object) -> tuple[Mapping[str, Any], ...]:
    payload = _histsem_exact_keys(value, {"schema_version", "packs"}, "pinset")
    if payload["schema_version"] != RECEIPT_HISTSEM_PINSET_SCHEMA:
        raise HistoricalSemanticsError(
            "histsem_pinset_invalid", "unsupported receipt-histsem pinset schema"
        )
    packs = payload["packs"]
    if not isinstance(packs, list) or not packs:
        raise HistoricalSemanticsError("histsem_pinset_invalid", "pinset packs must be nonempty")
    rows: list[Mapping[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    row_keys = {
        "current_pack_sha256",
        "freeze_receipt",
        "head_commit",
        "historical_pack_sha256",
        "pack_id",
        "pack_path",
        "plan_sha256",
        "plan_tree_sha256",
        "post_authoring_delta",
        "published_anchor",
        "receipt_count",
        "receipts",
    }
    receipt_keys = {
        "evidence_id",
        "namespace",
        "path",
        "receipt_kind",
        "schema_version",
        "sha256",
        "status",
    }
    for index, candidate in enumerate(packs):
        row = _histsem_exact_keys(candidate, row_keys, f"pinset.packs[{index}]")
        identity = (str(row["pack_id"]), str(row["pack_path"]))
        if identity in identities or identity[0] != PurePosixPath(identity[1]).name:
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", "pinset pack identities must be unique and path-bound"
            )
        identities.add(identity)
        if re.fullmatch(r"[0-9a-f]{40}", str(row["head_commit"])) is None:
            raise HistoricalSemanticsError("histsem_pinset_invalid", "pinset head is malformed")
        for field in (
            "current_pack_sha256",
            "historical_pack_sha256",
            "plan_sha256",
            "plan_tree_sha256",
        ):
            if re.fullmatch(r"[0-9a-f]{64}", str(row[field])) is None:
                raise HistoricalSemanticsError(
                    "histsem_pinset_invalid", f"pinset {field} is malformed"
                )
        freeze = _histsem_exact_keys(
            row["freeze_receipt"], {"path", "sha256"}, "pinset freeze_receipt"
        )
        if re.fullmatch(r"[0-9a-f]{64}", str(freeze["sha256"])) is None:
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", "pinset freeze digest is malformed"
            )
        delta = _histsem_exact_keys(
            row["post_authoring_delta"], {"added", "deleted", "modified"}, "pinset delta"
        )
        if any(
            not isinstance(delta[name], list)
            or delta[name] != sorted(set(delta[name]))
            or not all(isinstance(item, str) and item for item in delta[name])
            for name in ("added", "deleted", "modified")
        ):
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", "pinset delta paths must be unique sorted strings"
            )
        receipts = row["receipts"]
        if (
            not isinstance(receipts, list)
            or row["receipt_count"] != len(receipts)
            or not receipts
        ):
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", "pinset receipt inventory/count is invalid"
            )
        receipt_ids: set[str] = set()
        for receipt_index, receipt_candidate in enumerate(receipts):
            receipt = _histsem_exact_keys(
                receipt_candidate,
                receipt_keys,
                f"pinset.packs[{index}].receipts[{receipt_index}]",
            )
            evidence_id = str(receipt["evidence_id"])
            if evidence_id in receipt_ids or re.fullmatch(
                r"[0-9a-f]{64}", str(receipt["sha256"])
            ) is None:
                raise HistoricalSemanticsError(
                    "histsem_pinset_invalid", "pinset receipt identity/digest is invalid"
                )
            receipt_ids.add(evidence_id)
        rows.append(row)
    return tuple(rows)


def _load_histsem_pinset(
    repository: Path, pinset_path: Path | str | None = None
) -> tuple[Mapping[str, Any], ...]:
    paths = (
        tuple(repository / item for item in RECEIPT_HISTSEM_PINSET_RELATIVE_PATH)
        if pinset_path is None
        else (Path(pinset_path),)
    )
    rows: list[Mapping[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    present = 0
    for path in paths:
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            # Rule-11 absence semantics are per enumerated member: a future
            # successor that has not yet been minted contributes no rows.
            continue
        except OSError as exc:
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", f"receipt-histsem pinset is unreadable: {exc}"
            ) from exc
        present += 1
        try:
            member_rows = _validate_histsem_pinset(
                parse_json_bytes(raw, require_canonical=True)
            )
        except ArmReadinessError as exc:
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid",
                f"receipt-histsem pinset is not canonical: {exc}",
            ) from exc
        for row in member_rows:
            identity = (str(row["pack_id"]), str(row["pack_path"]))
            if identity in identities:
                raise HistoricalSemanticsError(
                    "histsem_pinset_invalid",
                    f"duplicate pack identity across pinset chain: {identity!r}",
                )
            identities.add(identity)
            rows.append(row)
    if present == 0:
        label = ", ".join(str(path) for path in paths)
        raise HistoricalSemanticsError(
            "histsem_pinset_absent", f"receipt-histsem pinset is absent: {label}"
        )
    return tuple(rows)


def _histsem_read_bound_file(
    repository: Path,
    pack_root: Path,
    pack_relative: str,
    relative: str,
    expected_sha256: str | None = None,
) -> bytes:
    relative_path = PurePosixPath(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"bound artifact path escapes the pack: {relative!r}"
        )
    path = pack_root / relative_path
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"cannot read bound artifact {relative!r}: {exc}"
        ) from exc
    digest = sha256_bytes(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"bound artifact digest differs for {relative!r}"
        )
    code, committed, _stderr = _histsem_git(
        repository, "show", f"HEAD:{pack_relative}/{relative}"
    )
    if code != 0 or committed != raw:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"bound artifact is not the HEAD blob: {relative!r}"
        )
    return raw


def _histsem_authenticate_legacy_item(
    repository: Path,
    pack_root: Path,
    pack_relative: str,
    item: Mapping[str, Any],
    receipt_raw: bytes,
) -> Mapping[str, Any]:
    """Authenticate frozen receipt metadata and every mandatory fact source."""

    try:
        receipt = validate_evidence_receipt(
            parse_json_bytes(receipt_raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"legacy receipt is invalid: {exc}"
        ) from exc
    if item != {
        "evidence_id": receipt["evidence_id"],
        "receipt_kind": receipt["kind"],
        "namespace": "PACK",
        "path": item["path"],
        "sha256": sha256_bytes(receipt_raw),
        "schema_version": receipt["schema_version"],
        "status": receipt["status"],
    }:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "freeze item metadata differs from receipt bytes"
        )
    for fact in receipt["facts"]:
        source_path = str(fact["source_path"])
        source_raw = _histsem_read_bound_file(
            repository, pack_root, pack_relative, source_path
        )
        if sha256_bytes(source_raw) != fact["source_sha256"]:
            raise HistoricalSemanticsError(
                "histsem_binding_mismatch",
                f"mandatory fact source digest differs for {source_path!r}",
            )
    return receipt


def _histsem_delta(
    repository: Path, pack_relative: str, head_commit: str
) -> dict[str, list[str]]:
    code, raw, _stderr = _histsem_git(
        repository,
        "diff",
        "--name-status",
        "--no-renames",
        head_commit,
        "HEAD",
        "--",
        pack_relative,
    )
    if code != 0:
        raise HistoricalSemanticsError(
            "histsem_history_unavailable", "cannot derive the post-authoring delta"
        )
    result = {"added": [], "deleted": [], "modified": []}
    status_field = {"A": "added", "D": "deleted", "M": "modified"}
    prefix = pack_relative + "/"
    try:
        lines = raw.decode("utf-8", errors="strict").splitlines()
    except UnicodeDecodeError as exc:
        raise HistoricalSemanticsError(
            "histsem_post_authoring_delta_unexpected", "Git delta contains a non-UTF-8 path"
        ) from exc
    for line in lines:
        try:
            status, repository_path = line.split("\t", 1)
        except ValueError as exc:
            raise HistoricalSemanticsError(
                "histsem_post_authoring_delta_unexpected", "malformed Git delta record"
            ) from exc
        if status not in status_field or not repository_path.startswith(prefix):
            raise HistoricalSemanticsError(
                "histsem_post_authoring_delta_unexpected", "inadmissible Git delta record"
            )
        result[status_field[status]].append(repository_path[len(prefix) :])
    for paths in result.values():
        paths.sort()
    added_ok = all(
        PurePosixPath(path).parts
        and PurePosixPath(path).parts[0] in _HISTSEM_CUSTODY_DIRECTORIES
        for path in result["added"]
    )
    if (
        not added_ok
        or result["deleted"]
        or not set(result["modified"]) <= _HISTSEM_ALLOWED_MODIFICATIONS
    ):
        raise HistoricalSemanticsError(
            "histsem_post_authoring_delta_unexpected",
            "post-authoring delta exceeds the code-level custody envelope",
        )
    return result


def verify_receipt_histsem_pack(
    pack_root: Path | str,
    *,
    pinset_path: Path | str | None = None,
    require_published: bool = False,
    _pinset_rows: tuple[Mapping[str, Any], ...] | None = None,
) -> dict[str, Any]:
    """Verify one governed pack at historical and current coordinates."""

    root = Path(pack_root).resolve(strict=True)
    repository, pack_relative = _histsem_repository_and_pack(root)
    rows = (
        _load_histsem_pinset(repository, pinset_path)
        if _pinset_rows is None
        else _pinset_rows
    )
    matches = [
        row
        for row in rows
        if row["pack_id"] == root.name and row["pack_path"] == pack_relative
    ]
    if not matches:
        raise HistoricalSemanticsError(
            "histsem_pinset_absent", f"pinset has no row for governed pack {pack_relative}"
        )
    if len(matches) != 1:
        raise HistoricalSemanticsError(
            "histsem_pinset_invalid", f"pinset has duplicate rows for {pack_relative}"
        )
    row = matches[0]
    try:
        current_digest = committed_pack_tree_sha256(root)
    except (ArmReadinessError, OSError) as exc:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"current committed pack cannot authenticate: {exc}"
        ) from exc
    if current_digest != row["current_pack_sha256"]:
        raise HistoricalSemanticsError(
            "histsem_pinset_mismatch", "current committed pack differs from the governed pin"
        )
    head_commit = str(row["head_commit"])
    code, _stdout, _stderr = _histsem_git(
        repository, "merge-base", "--is-ancestor", head_commit, "HEAD"
    )
    if code != 0:
        raise HistoricalSemanticsError(
            "histsem_commit_off_lineage", "historical receipt commit is not an ancestor of HEAD"
        )
    code, _stdout, _stderr = _histsem_git(
        repository, "merge-base", "--is-ancestor", head_commit, "origin/main"
    )
    advisories: list[str] = []
    if code != 0:
        if require_published:
            raise HistoricalSemanticsError(
                "histsem_commit_unpublished",
                "historical receipt commit is not an ancestor of origin/main",
            )
        advisories.append("histsem_commit_unpublished")
    historical_digest, historical_paths = _historical_pack_tree(
        repository, pack_relative, head_commit
    )
    if historical_digest != row["historical_pack_sha256"]:
        raise HistoricalSemanticsError(
            "histsem_historical_digest_mismatch",
            "historical pack digest differs from the governed pin",
        )
    if any(
        PurePosixPath(path).parts[0] in _HISTSEM_CUSTODY_DIRECTORIES
        for path in historical_paths
    ):
        raise HistoricalSemanticsError(
            "histsem_historical_tree_not_pre_authoring",
            "historical receipt coordinate already contains custody artifacts",
        )
    delta = _histsem_delta(repository, pack_relative, head_commit)
    if delta != row["post_authoring_delta"]:
        raise HistoricalSemanticsError(
            "histsem_post_authoring_delta_unexpected",
            "post-authoring delta differs from the governed per-pack envelope",
        )

    freeze_reference = row["freeze_receipt"]
    freeze_path = str(freeze_reference["path"])
    freeze_raw = _histsem_read_bound_file(
        repository,
        root,
        pack_relative,
        freeze_path,
        str(freeze_reference["sha256"]),
    )
    freeze_sidecar = _histsem_read_bound_file(
        repository,
        root,
        pack_relative,
        f"{freeze_path}.sha256",
    )
    if freeze_sidecar != gnu_sidecar(str(freeze_reference["sha256"]), Path(freeze_path).name):
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "freeze receipt sidecar differs from its bytes"
        )
    try:
        freeze = validate_freeze_receipt(
            parse_json_bytes(freeze_raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"freeze receipt is invalid: {exc}"
        ) from exc

    plan_tree_raw = _histsem_read_bound_file(
        repository,
        root,
        pack_relative,
        "plan_tree.json",
        str(row["plan_tree_sha256"]),
    )
    plan_sidecar = _histsem_read_bound_file(
        repository, root, pack_relative, "plan_tree.sha256"
    )
    if plan_sidecar != gnu_sidecar(sha256_bytes(plan_tree_raw), "plan_tree.json"):
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "plan-tree sidecar differs from current plan bytes"
        )
    try:
        plan_tree = parse_json_bytes(plan_tree_raw)
    except ArmReadinessError as exc:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", f"plan tree is invalid: {exc}"
        ) from exc
    readiness = (
        plan_tree.get("arm_attachments", {}).get("arm_readiness")
        if isinstance(plan_tree, Mapping)
        else None
    )
    if not isinstance(readiness, Mapping) or readiness.get("freeze_receipt") != freeze_reference:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "current plan tree does not bind the pinned freeze receipt"
        )
    plan_path = str(freeze["pack_identity"]["plan_path"])
    plan_raw = _histsem_read_bound_file(repository, root, pack_relative, plan_path)
    if (
        sha256_bytes(plan_raw) != row["plan_sha256"]
        or freeze["pack_identity"]["plan_sha256"] != row["plan_sha256"]
        or freeze["pack_identity"]["pack_id"] != row["pack_id"]
    ):
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "freeze plan/pack identity differs from current pinned bytes"
        )

    pinned_receipts = list(row["receipts"])
    freeze_pack_items = [
        dict(item)
        for item in freeze["evidence"]
        if item["namespace"] == "PACK"
        and item["schema_version"] in GENERIC_EVIDENCE_RECEIPT_SCHEMAS
    ]
    if freeze_pack_items != pinned_receipts:
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "freeze PACK evidence inventory differs from the pinset"
        )
    disk_receipt_paths = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "arm_readiness.evidence").glob("*.json")
    )
    if disk_receipt_paths != sorted(str(item["path"]) for item in pinned_receipts):
        raise HistoricalSemanticsError(
            "histsem_binding_mismatch", "committed legacy receipt set differs from the pinset"
        )
    for item in pinned_receipts:
        receipt_path = str(item["path"])
        receipt_raw = _histsem_read_bound_file(
            repository,
            root,
            pack_relative,
            receipt_path,
            str(item["sha256"]),
        )
        receipt_sidecar = _histsem_read_bound_file(
            repository, root, pack_relative, f"{receipt_path}.sha256"
        )
        if receipt_sidecar != gnu_sidecar(str(item["sha256"]), Path(receipt_path).name):
            raise HistoricalSemanticsError(
                "histsem_binding_mismatch", f"receipt sidecar differs for {receipt_path!r}"
            )
        receipt = _histsem_authenticate_legacy_item(
            repository, root, pack_relative, item, receipt_raw
        )
        receipt_head = receipt.get("head_commit", receipt.get("derivation_commit"))
        if (
            receipt["schema_version"] not in GENERIC_EVIDENCE_RECEIPT_SCHEMAS
            or re.fullmatch(r"[0-9a-f]{40}", str(receipt_head)) is None
            or re.fullmatch(r"[0-9a-f]{64}", str(receipt.get("pack_sha256"))) is None
        ):
            raise HistoricalSemanticsError(
                "histsem_receipt_head_malformed", f"receipt coordinate is malformed: {receipt_path}"
            )
        if receipt_head != head_commit or receipt["pack_sha256"] != historical_digest:
            raise HistoricalSemanticsError(
                "histsem_historical_digest_mismatch",
                f"receipt historical coordinate differs from recomputed tree: {receipt_path}",
            )
        if sha256_bytes(receipt_raw) != item["sha256"]:
            raise HistoricalSemanticsError(
                "histsem_pinset_mismatch", f"receipt differs from its pin: {receipt_path}"
            )

    predecessor = freeze.get("predecessor")
    if predecessor is not None:
        predecessor_relative = str(predecessor["pack_path"])
        predecessor_root = (repository / PurePosixPath(predecessor_relative)).resolve()
        try:
            predecessor_root.relative_to(repository)
            predecessor_digest = committed_pack_tree_sha256(predecessor_root)
            predecessor_freeze_raw = (
                predecessor_root / str(predecessor["freeze_receipt"]["path"])
            ).read_bytes()
        except (ArmReadinessError, OSError, ValueError) as exc:
            raise HistoricalSemanticsError(
                "histsem_binding_mismatch", f"predecessor binding is unreadable: {exc}"
            ) from exc
        if (
            predecessor_root.name != predecessor["pack_id"]
            or predecessor_digest != predecessor["pack_sha256"]
            or sha256_bytes(predecessor_freeze_raw)
            != predecessor["freeze_receipt"]["sha256"]
        ):
            raise HistoricalSemanticsError(
                "histsem_binding_mismatch", "freeze predecessor binding differs from current bytes"
            )
    return {
        "pack_id": row["pack_id"],
        "pack_path": pack_relative,
        "receipts_verified": len(pinned_receipts),
        "historical_pack_sha256": historical_digest,
        "current_pack_sha256": current_digest,
        "advisories": advisories,
        "status": "PASS",
    }


def verify_all_receipt_histsem(
    repository_root: Path | str,
    *,
    pinset_path: Path | str | None = None,
    pack_roots: Sequence[Path | str] | None = None,
    require_published: bool = False,
) -> dict[str, Any]:
    """Verify the governed pinset, or an explicitly selected subset of it."""

    repository = Path(repository_root).resolve(strict=True)
    rows = _load_histsem_pinset(repository, pinset_path)
    roots = (
        [repository / str(row["pack_path"]) for row in rows]
        if pack_roots is None
        else [Path(path) for path in pack_roots]
    )
    results = [
        verify_receipt_histsem_pack(
            root,
            pinset_path=pinset_path,
            require_published=require_published,
            _pinset_rows=rows,
        )
        for root in roots
    ]
    return {
        "schema_version": "joulewise.receipt_histsem_verification.v1",
        "status": "PASS",
        "pack_count": len(results),
        "receipt_count": sum(int(item["receipts_verified"]) for item in results),
        "packs": results,
    }


def _gate_receipt_histsem(pack_root: Path, *, require_published: bool = False) -> None:
    """Gate packs whose immutable repository identity is in the HEAD pinset."""

    try:
        pack_root = Path(pack_root).resolve(strict=True)
    except OSError:
        # A nonexistent or unresolvable root is ordinary-readiness input;
        # its refusal vocabulary owns the missing-path case, as before.
        return
    try:
        repository, pack_relative = _histsem_repository_and_pack(pack_root)
    except HistoricalSemanticsError:
        # A root outside a Git worktree has no governed repository-relative
        # identity.  The ordinary readiness path owns that non-histsem input;
        # an advertised but unreadable Git worktree must refuse instead.
        if not _histsem_has_git_metadata(pack_root):
            return
        raise
    governed_rows_list: list[Mapping[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for relative_path in RECEIPT_HISTSEM_PINSET_RELATIVE_PATH:
        code, pinset_entry, _stderr = _histsem_git(
            repository, "ls-tree", "HEAD", "--", relative_path.as_posix()
        )
        if code != 0:
            raise HistoricalSemanticsError(
                "histsem_history_unavailable",
                "committed receipt-histsem pinset lookup failed",
            )
        if not pinset_entry.strip():
            continue
        code, pinset_raw, _stderr = _histsem_git(
            repository, "show", f"HEAD:{relative_path.as_posix()}"
        )
        if code != 0:
            raise HistoricalSemanticsError(
                "histsem_history_unavailable",
                "committed receipt-histsem pinset read failed",
            )
        try:
            member_rows = _validate_histsem_pinset(
                parse_json_bytes(pinset_raw, require_canonical=True)
            )
        except ArmReadinessError as exc:
            raise HistoricalSemanticsError(
                "histsem_pinset_invalid", "committed receipt-histsem pinset is invalid"
            ) from exc
        for row in member_rows:
            identity = (str(row["pack_id"]), str(row["pack_path"]))
            if identity in identities:
                raise HistoricalSemanticsError(
                    "histsem_pinset_invalid",
                    f"duplicate pack identity across pinset chain: {identity!r}",
                )
            identities.add(identity)
            governed_rows_list.append(row)
    governed_rows = tuple(governed_rows_list)
    if not governed_rows:
        return
    if not any(
        row["pack_id"] == pack_root.name and row["pack_path"] == pack_relative
        for row in governed_rows
    ):
        return
    verify_receipt_histsem_pack(
        pack_root,
        require_published=require_published,
        _pinset_rows=governed_rows,
    )


def _plan_profile(
    pack_root: Path, registry: Mapping[str, Any] | None = None
) -> str:
    """Resolve a pack role without a successor-ID code allowlist.

    Historical v1 identities retain their immutable mapping.  An R1 registry
    installs successor identities by role; the code validates only the three
    D-139-approved uniform successor name shapes.
    """

    historical = _PROFILE_BY_PACK.get(pack_root.name)
    if historical is not None:
        return historical
    if registry is not None and registry.get("schema_version") == R1_ROW_REGISTRY_SCHEMA:
        lifecycle = validate_r1_lifecycle_registry(
            registry["freeze_evidence_lifecycle"]
        )
        installed = lifecycle["successor_policy"]["successor_pack_ids"]
        if isinstance(installed, Mapping):
            matches = [
                profile
                for profile, pack_id in installed.items()
                if pack_id == pack_root.name
            ]
            if len(matches) == 1:
                profile = matches[0]
                pattern = _SUCCESSOR_PROFILE_PATTERNS.get(profile)
                if pattern is not None and pattern.fullmatch(pack_root.name):
                    return profile
                raise ArmReadinessError(
                    "readiness_row_registry_mismatch",
                    f"registry-installed {profile} successor ID has an unapproved shape",
                )
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                f"successor ID {pack_root.name!r} is not installed by the R1 registry",
            )
    # The shape-only route supports construction tools before a registry is
    # loaded; production admission above still requires the registry mapping.
    shaped = [
        profile
        for profile, pattern in _SUCCESSOR_PROFILE_PATTERNS.items()
        if pattern.fullmatch(pack_root.name)
    ]
    if len(shaped) == 1:
        return shaped[0]
    raise ArmReadinessError(
        "readiness_row_registry_mismatch", f"no D-134 profile for {pack_root.name}"
    )


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
    profile = _plan_profile(pack_root, registry)
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


def _existing_plan_freeze_pin(pack_root: Path) -> dict[str, str] | None:
    """Return the freeze receipt the pack's plan tree already pins, if any."""

    path = pack_root / "plan_tree.json"
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    try:
        tree = parse_json_bytes(raw)
    except ArmReadinessError:
        return None
    attachments = tree.get("arm_attachments") if isinstance(tree, Mapping) else None
    declaration = (
        attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    )
    pin = (
        declaration.get("freeze_receipt")
        if isinstance(declaration, Mapping)
        else None
    )
    if not isinstance(pin, Mapping) or set(pin) != {"path", "sha256"}:
        return None
    return {"path": str(pin["path"]), "sha256": str(pin["sha256"])}


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
        # A highest filename confers no authority.  The pack must present one
        # committed candidate, and it must be the one the plan already pins.
        if len(committed_receipts) != 1:
            raise ArmReadinessError(
                "readiness_freeze_receipt_mismatch",
                "pack presents multiple committed freeze receipts; no unique selection",
            )
        selected = committed_receipts[0]
        freeze_reference = {
            "path": f"arm_readiness.freeze.receipts/{selected['path'].name}",
            "sha256": selected["sha256"],
        }
        pinned = _existing_plan_freeze_pin(Path(pack_root))
        if pinned is not None and pinned != freeze_reference:
            raise ArmReadinessError(
                "readiness_freeze_receipt_mismatch",
                "committed freeze receipt is not the receipt the plan pins",
            )
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


def authenticate_r1_lifecycle_registry(
    raw: bytes, expected_sha256: str
) -> Mapping[str, Any]:
    """Authenticate canonical registry bytes before any R1 policy lookup."""

    _require_lower_sha256(expected_sha256, "R1 lifecycle registry sha256")
    if sha256_bytes(raw) != expected_sha256:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 lifecycle registry digest differs from its governed pin",
        )
    value = parse_json_bytes(raw, require_canonical=True)
    return validate_r1_lifecycle_registry(value)


def _git_blob_at_commit(
    repository: Path,
    commit: str,
    relative_path: str,
    registry: Mapping[str, Any],
) -> bytes:
    try:
        return _run_git(repository, "show", f"{commit}:{relative_path}")
    except ArmReadinessError as exc:
        raise EvidenceLifecycleError(
            registry,
            "DEPENDENCY_MANIFEST",
            f"cannot authenticate dependency {relative_path!r} at {commit}: {exc}",
        ) from exc


def _json_member_value_span(text: str, target: tuple[str, ...]) -> tuple[int, int]:
    """Locate one object-member value while preserving every source character."""

    decoder = json.JSONDecoder()
    matches: list[tuple[int, int]] = []

    def whitespace(index: int) -> int:
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
        return index

    def value(index: int, path: tuple[str, ...]) -> int:
        index = whitespace(index)
        if index >= len(text):
            raise ValueError("truncated JSON value")
        if text[index] == "{":
            cursor = whitespace(index + 1)
            if cursor < len(text) and text[cursor] == "}":
                return cursor + 1
            while True:
                key, key_end = decoder.raw_decode(text, cursor)
                if not isinstance(key, str):
                    raise ValueError("JSON object key is not a string")
                cursor = whitespace(key_end)
                if cursor >= len(text) or text[cursor] != ":":
                    raise ValueError("JSON object member lacks a colon")
                member_start = whitespace(cursor + 1)
                member_path = (*path, key)
                member_end = value(member_start, member_path)
                if member_path == target:
                    matches.append((member_start, member_end))
                cursor = whitespace(member_end)
                if cursor < len(text) and text[cursor] == ",":
                    cursor = whitespace(cursor + 1)
                    continue
                if cursor < len(text) and text[cursor] == "}":
                    return cursor + 1
                raise ValueError("JSON object member is not terminated")
        if text[index] == "[":
            cursor = whitespace(index + 1)
            if cursor < len(text) and text[cursor] == "]":
                return cursor + 1
            while True:
                cursor = whitespace(value(cursor, path))
                if cursor < len(text) and text[cursor] == ",":
                    cursor = whitespace(cursor + 1)
                    continue
                if cursor < len(text) and text[cursor] == "]":
                    return cursor + 1
                raise ValueError("JSON array item is not terminated")
        _item, end = decoder.raw_decode(text, index)
        return end

    try:
        end = whitespace(value(0, ()))
    except (json.JSONDecodeError, ValueError) as exc:
        raise ArmReadinessError(
            "readiness_schema_invalid", f"cannot locate plan-tree freeze slot: {exc}"
        ) from exc
    if end != len(text) or len(matches) != 1:
        raise ArmReadinessError(
            "readiness_schema_invalid",
            "plan tree must contain exactly one arm-readiness freeze-receipt slot",
        )
    return matches[0]


def normalize_plan_tree_for_freeze_evidence(raw: bytes) -> bytes:
    """Subtract only the two future freeze-receipt slot values.

    The slot key itself and every other plan-tree byte remain semantically
    represented.  No general-purpose canonicalization exception exists.
    """

    value = parse_json_bytes(raw)
    if not isinstance(value, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan-tree normalization input is not an object"
        )
    attachments = value.get("arm_attachments")
    readiness = attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    if not isinstance(readiness, dict) or "freeze_receipt" not in readiness:
        raise ArmReadinessError(
            "readiness_schema_invalid",
            "plan tree lacks the arm-readiness freeze-receipt slot",
        )
    slot = readiness["freeze_receipt"]
    if slot is not None:
        exact = _require_exact_keys(
            slot,
            {"path", "sha256"},
            "arm_attachments.arm_readiness.freeze_receipt",
        )
        _require_relative_path(
            exact["path"], "arm_attachments.arm_readiness.freeze_receipt.path"
        )
        _require_lower_sha256(
            exact["sha256"], "arm_attachments.arm_readiness.freeze_receipt.sha256"
        )
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan-tree normalization input is not UTF-8"
        ) from exc
    start, end = _json_member_value_span(
        text, ("arm_attachments", "arm_readiness", "freeze_receipt")
    )
    # Enumerated subtraction: replace only the slot value token.  Prefix,
    # suffix, whitespace, ordering, and every non-slot byte remain identical.
    return f"{text[:start]}null{text[end:]}".encode("utf-8")


def validate_terminal_review_head_tree(
    source: Mapping[str, Any], reviewed_head_tree_oid: str
) -> None:
    """Enforce R1 clause 3 independently of every head-relaxation policy."""

    _require_lower_git_oid(reviewed_head_tree_oid, "reviewed HEAD tree OID")
    if source.get("head_tree_oid") != reviewed_head_tree_oid:
        raise ArmReadinessError(
            "readiness_terminal_review_missing",
            "terminal review does not bind the reviewed HEAD tree",
        )


def _r1_changed_paths(
    repository: Path,
    derivation_commit: str,
    current_head: str,
    registry: Mapping[str, Any],
) -> tuple[str, ...]:
    try:
        _run_git(
            repository,
            "merge-base",
            "--is-ancestor",
            derivation_commit,
            current_head,
        )
    except ArmReadinessError as exc:
        raise EvidenceLifecycleError(
            registry,
            "SUCCESSOR_CHAIN",
            "evidence derivation commit is not an ancestor of the reviewed HEAD",
        ) from exc
    try:
        raw = _run_git(
            repository,
            "diff",
            "--name-only",
            "-z",
            f"{derivation_commit}..{current_head}",
            "--",
        )
        decoded = raw.decode("utf-8", errors="strict")
    except (ArmReadinessError, UnicodeDecodeError) as exc:
        raise EvidenceLifecycleError(
            registry,
            "DEPENDENCY_CHANGED_SET",
            f"cannot enumerate the complete changed set: {exc}",
        ) from exc
    paths = tuple(item for item in decoded.split("\0") if item)
    if paths != tuple(sorted(set(paths))) or any(
        Path(path).is_absolute()
        or "\\" in path
        or any(part in {"", ".", ".."} for part in PurePosixPath(path).parts)
        for path in paths
    ):
        raise EvidenceLifecycleError(
            registry,
            "DEPENDENCY_CHANGED_SET",
            "Git returned a noncanonical changed-path set",
        )
    return paths


def _r1_manifest_dependencies(source: Mapping[str, Any]) -> list[dict[str, str]]:
    dependencies: list[dict[str, str]] = []
    primary = source.get("primary_artifacts")
    checks = source.get("checks")
    if not isinstance(primary, list) or not isinstance(checks, list):
        return dependencies
    for item in primary:
        if isinstance(item, Mapping):
            dependencies.append({"path": item.get("path"), "sha256": item.get("sha256")})
    for check in checks:
        evidence = check.get("evidence") if isinstance(check, Mapping) else None
        executed = evidence.get("executed_files") if isinstance(evidence, Mapping) else None
        if not isinstance(executed, list):
            continue
        for item in executed:
            if isinstance(item, Mapping):
                dependencies.append(
                    {"path": item.get("path"), "sha256": item.get("sha256")}
                )
    by_path: dict[object, object] = {}
    for item in dependencies:
        path = item.get("path")
        digest = item.get("sha256")
        if path in by_path and by_path[path] != digest:
            return dependencies
        by_path[path] = digest
    return [
        {"path": path, "sha256": digest}
        for path, digest in sorted(by_path.items(), key=lambda item: str(item[0]))
    ]


def _require_confirmed_conditional_path(
    root: Path,
    current_head: str,
    relative_path: str,
    registry: Mapping[str, Any],
    confirmation_path: Path | str | None,
    *,
    evidence_id: str | None,
) -> None:
    """Enforce D-151 condition 2's C -> S edge for one conditional allowlist path.

    Returns normally only when Ed's step-6 confirmation table is present, valid,
    names this exact path in its ``successor_pinset`` section, and records the
    SHA-256 of the bytes committed at ``current_head``.  Every other outcome --
    no table, an unreadable/noncanonical/invalid table, a table naming a
    different path, an absent blob, or a digest mismatch -- raises
    ``DEPENDENCY_CHANGED_SET``, which is the pre-existing refusal role the
    changed-set gate already owns (D-151 condition 1e: no new refusal codes).
    """

    def refuse(detail: str, cause: BaseException | None = None) -> EvidenceLifecycleError:
        error = EvidenceLifecycleError(
            registry,
            "DEPENDENCY_CHANGED_SET",
            f"digest-conditional allowlist path {relative_path!r}: {detail}",
            evidence_id=evidence_id,
        )
        if cause is not None:
            error.__cause__ = cause
        return error

    if confirmation_path is None:
        raise refuse(
            "changed at the reviewed HEAD with no step-6 confirmation table supplied"
        )
    try:
        table_value, _table_raw = _read_external_canonical(
            Path(confirmation_path),
            absent_check="confirmation_missing",
            invalid_check="confirmation_mismatch",
        )
        table = validate_step6_confirmation_table(table_value)
    except FamilyPublicationError as exc:
        raise refuse(
            f"step-6 confirmation table is inadmissible ({exc.check_id}): {exc}", exc
        ) from exc
    section = table["successor_pinset"]
    if section["path"] != relative_path:
        raise refuse("the confirmed step-6 table authenticates a different path")
    try:
        committed = _git_blob_at_commit(root, current_head, relative_path, registry)
    except EvidenceLifecycleError as exc:
        raise refuse(
            f"no committed bytes at the reviewed HEAD to authenticate: {exc}", exc
        ) from exc
    if sha256_bytes(committed) != section["sha256"]:
        raise refuse(
            "bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest"
        )


def validate_r1_evidence_lifecycle(
    repository: Path | str,
    receipt: Mapping[str, Any],
    source: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    current_head: str,
    expected_freshness_class: str,
    plan_tree_path: str,
    step6_confirmation_table: Path | str | None = None,
) -> tuple[str, ...]:
    """Apply R1's changed-set primary gate and manifest conjunct."""

    root = Path(repository).resolve(strict=True)
    governed = validate_r1_lifecycle_registry(registry)
    validated_receipt = validate_evidence_receipt(receipt)
    if validated_receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA:
        raise EvidenceLifecycleError(
            governed,
            "V1_GRANDFATHERING",
            "legacy generic evidence may not enter the R1 lifecycle",
            evidence_id=str(validated_receipt["evidence_id"]),
        )
    kind = str(validated_receipt["kind"])
    policy = _r1_policy_for_kind(governed, kind)
    if (
        expected_freshness_class not in R1_FRESHNESS_CLASSES
        or validated_receipt["freshness_class"] != expected_freshness_class
        or policy["freshness_class"] != expected_freshness_class
        or validated_receipt["freshness_policy_id"]
        != policy["freshness_policy_id"]
    ):
        raise EvidenceLifecycleError(
            governed,
            "CLASS_MISMATCH",
            f"registry, receipt, and code freshness classes disagree for {kind}",
            evidence_id=str(validated_receipt["evidence_id"]),
        )
    derivation_commit = str(validated_receipt["derivation_commit"])
    _require_lower_git_oid(current_head, "R1 current reviewed HEAD")
    changed_paths = _r1_changed_paths(
        root, derivation_commit, current_head, governed
    )
    allowlist = set(governed["irrelevant_path_allowlist"])
    conditional = allowlist & R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS
    outstanding = set(changed_paths) - (allowlist - conditional)
    for conditional_path in sorted(outstanding & conditional):
        _require_confirmed_conditional_path(
            root,
            current_head,
            conditional_path,
            governed,
            step6_confirmation_table,
            evidence_id=str(validated_receipt["evidence_id"]),
        )
        outstanding.discard(conditional_path)
    relevant = sorted(outstanding)
    if relevant:
        raise EvidenceLifecycleError(
            governed,
            "DEPENDENCY_CHANGED_SET",
            f"reviewed HEAD changed relevant path(s): {relevant!r}",
            evidence_id=str(validated_receipt["evidence_id"]),
        )

    source_raw = render_json(source)
    if (
        sha256_bytes(source_raw) != validated_receipt["dependency_manifest_sha256"]
        or any(
            fact["source_sha256"] != validated_receipt["dependency_manifest_sha256"]
            for fact in validated_receipt["facts"]
        )
        or source.get("kind") != kind
        or source.get("derivation_commit", source.get("head_commit"))
        != derivation_commit
        or source.get("pack_sha256") != validated_receipt["pack_sha256"]
    ):
        raise EvidenceLifecycleError(
            governed,
            "DEPENDENCY_MANIFEST",
            "evidence source and receipt dependency-manifest bindings disagree",
            evidence_id=str(validated_receipt["evidence_id"]),
        )

    dependencies = _r1_manifest_dependencies(source)
    if not dependencies:
        raise EvidenceLifecycleError(
            governed,
            "DEPENDENCY_MANIFEST",
            "evidence dependency manifest is empty",
            evidence_id=str(validated_receipt["evidence_id"]),
        )
    pairs = [(item.get("path"), item.get("sha256")) for item in dependencies]
    if any(
        not isinstance(path, str)
        or not isinstance(digest, str)
        or _LOWER_SHA256_RE.fullmatch(digest) is None
        for path, digest in pairs
    ) or len([path for path, _digest in pairs]) != len(
        {path for path, _digest in pairs}
    ):
        raise EvidenceLifecycleError(
            governed,
            "DEPENDENCY_MANIFEST",
            "evidence dependency manifest contains malformed or duplicate entries",
            evidence_id=str(validated_receipt["evidence_id"]),
        )
    for relative, recorded_digest in pairs:
        assert isinstance(relative, str) and isinstance(recorded_digest, str)
        derived_raw = _git_blob_at_commit(
            root, derivation_commit, relative, governed
        )
        if sha256_bytes(derived_raw) != recorded_digest:
            raise EvidenceLifecycleError(
                governed,
                "DEPENDENCY_MANIFEST",
                f"recorded dependency differs at derivation commit: {relative}",
                evidence_id=str(validated_receipt["evidence_id"]),
            )
        current_raw = _git_blob_at_commit(root, current_head, relative, governed)
        try:
            equal = (
                normalize_plan_tree_for_freeze_evidence(derived_raw)
                == normalize_plan_tree_for_freeze_evidence(current_raw)
                if relative == plan_tree_path
                else sha256_bytes(current_raw) == recorded_digest
            )
        except ArmReadinessError as exc:
            raise EvidenceLifecycleError(
                governed,
                "DEPENDENCY_MANIFEST",
                f"plan-tree subtraction refused: {exc}",
                evidence_id=str(validated_receipt["evidence_id"]),
            ) from exc
        if not equal:
            raise EvidenceLifecycleError(
                governed,
                "DEPENDENCY_MANIFEST",
                f"current dependency differs from its derivation binding: {relative}",
                evidence_id=str(validated_receipt["evidence_id"]),
            )
    return changed_paths


def validate_r1_temporal_budget(
    evidence_receipts: Iterable[Mapping[str, Any]],
    registry: Mapping[str, Any],
    *,
    now_monotonic_ns: int,
) -> int | None:
    """Evaluate the TIME_BOUND T-0 set against the governed consume budget."""

    governed = validate_r1_lifecycle_registry(registry)
    budget = governed["arm_policy"]["arm_to_consume_budget_ns"]
    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "R1 arm-to-consume budget remains unresolved",
        )
    deadlines: list[int] = []
    for receipt in evidence_receipts:
        kind = receipt.get("kind")
        if R1_EVIDENCE_FRESHNESS_CLASSES.get(kind) != "TIME_BOUND":
            continue
        deadline = receipt.get("valid_until_monotonic_ns")
        if not isinstance(deadline, int) or isinstance(deadline, bool) or deadline <= 0:
            raise EvidenceLifecycleError(
                governed,
                "TEMPORAL_BUDGET",
                f"TIME_BOUND evidence {kind!r} lacks a valid deadline",
                evidence_id=(
                    str(receipt["evidence_id"])
                    if isinstance(receipt.get("evidence_id"), str)
                    else None
                ),
            )
        deadlines.append(deadline)
    if not deadlines:
        return None
    earliest = min(deadlines)
    if earliest - now_monotonic_ns < budget:
        raise EvidenceLifecycleError(
            governed,
            "TEMPORAL_BUDGET",
            "T-0 evidence lifetime cannot cover the governed arm-to-consume budget",
        )
    return earliest


def validate_r1_class_lifecycle(
    receipt: Mapping[str, Any],
    evidence_kind: str,
    *,
    current_boot_session_id: str,
    now_monotonic_ns: int,
    semantic_state_valid: bool | None = None,
    capability_consumed: bool | None = None,
) -> None:
    """Apply only the class-level invariants already fixed by R1.

    Row-specific probes and comparison semantics remain registry-reserved;
    callers must supply their already-derived semantic-state result.
    """

    freshness_class = R1_EVIDENCE_FRESHNESS_CLASSES.get(evidence_kind)
    if freshness_class is None:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            f"no code freshness class for evidence kind {evidence_kind!r}",
        )
    _require_boot_session_id(current_boot_session_id, "current boot session")
    if freshness_class == "RE_DERIVABLE":
        if "boot_session_id" in receipt or "valid_until_monotonic_ns" in receipt:
            raise ArmReadinessError(
                "readiness_schema_invalid",
                "RE_DERIVABLE evidence may not store boot or deadline validity",
            )
        return
    if freshness_class in {
        "EXECUTION_BOUND",
        "TIME_BOUND",
        "SESSION_STATE_BOUND",
        "TEMPORAL_CAPABILITY",
    }:
        if (
            receipt.get("boot_session_id") != current_boot_session_id
            or not isinstance(receipt.get("valid_until_monotonic_ns"), int)
            or receipt["valid_until_monotonic_ns"] < now_monotonic_ns
        ):
            raise ArmReadinessError(
                "readiness_record_expired",
                f"{freshness_class} evidence is outside its boot/horizon binding",
            )
    if freshness_class == "SESSION_STATE_BOUND" and semantic_state_valid is not True:
        raise ArmReadinessError(
            "readiness_dependency_refused",
            "SESSION_STATE_BOUND predicate did not semantically revalidate",
        )
    if freshness_class == "TEMPORAL_CAPABILITY":
        if semantic_state_valid is not True:
            raise ArmReadinessError(
                "readiness_dependency_refused",
                "TEMPORAL_CAPABILITY state did not semantically revalidate",
            )
        if capability_consumed is not False:
            raise ArmReadinessError(
                "readiness_record_consumed",
                "TEMPORAL_CAPABILITY is already consumed or its state is unknown",
            )


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
    if kind == "freeze":
        for item in result:
            if item["receipt"]["schema_version"] != FREEZE_RECEIPT_V2_SCHEMA:
                continue
            predecessor_ordinal = _freeze_receipt_ordinal(
                item["receipt"]["predecessor"]["freeze_receipt"]["receipt_id"],
                "predecessor freeze receipt_id",
            )
            if item["number"] < 2 or item["number"] != predecessor_ordinal + 1:
                raise ArmReadinessError(
                    "readiness_receipt_namespace_anomalous",
                    "successor freeze receipt ordinal is not the predecessor ordinal plus one",
                )
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


def _fsync_directory(path: Path) -> None:
    """Persist a just-created no-clobber namespace entry."""

    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_io_error", f"cannot open directory for fsync {path}: {exc}"
        ) from exc
    try:
        os.fsync(descriptor)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_io_error", f"cannot fsync directory {path}: {exc}"
        ) from exc
    finally:
        os.close(descriptor)


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


def _refusal_sort_key(item: Mapping[str, Any]) -> tuple[str, str, str]:
    """The ONE canonical refusal ordering every minted receipt is written in."""

    return (item["code"], item["row_id"] or "", item["evidence_id"] or "")


def _canonical_refusals(
    refusals: Iterable[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Return ``refusals`` in the canonical order receipts record them in.

    Refusal ORDER carries no conclusion: two refusal lists that differ only in
    order record the same verdict.  Every mint site writes this order, so any
    replay that compares a recorded list against a freshly derived one must
    canonicalize BOTH sides -- otherwise a receipt authenticates against its own
    evidence and still fails an ordering comparison.
    """

    return sorted(refusals, key=_refusal_sort_key)


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
    plan_path, plan_relative, plan_id, raw = resolve_frozen_plan(pack_root, tree)
    plan = tree.get("plan")
    window = tree.get("window_identity")
    if not isinstance(plan, Mapping) or not isinstance(window, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan tree omits plan/window identity"
        )
    return {
        "pack_id": pack_root.name,
        "plan_id": plan_id,
        "window_id": _require_string(window.get("window_id"), "window_identity.window_id"),
        "pack_root": str(pack_root.resolve()),
        "plan_path": plan_relative,
        "plan_sha256": sha256_bytes(raw),
    }


def resolve_frozen_plan(
    pack_root: Path | str,
    tree: Mapping[str, Any] | None = None,
) -> tuple[Path, str, str, bytes]:
    """Resolve and authenticate R2's committed pack-relative plan reference.

    The stored path is never repaired with a basename or repository-root
    fallback.  The absolute path returned here is the sole execution-boundary
    literal for ``FROZEN_PLAN`` and every governed ``--plan`` argument.
    """

    try:
        root = Path(pack_root).resolve(strict=True)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"pack root is unreadable: {exc}"
        ) from exc
    if tree is None:
        tree, _tree_raw = _plan_tree(root)
    plan = tree.get("plan")
    if not isinstance(plan, Mapping):
        raise ArmReadinessError(
            "readiness_schema_invalid", "plan tree omits plan identity"
        )
    relative = _require_relative_path(plan.get("path"), "plan.path")
    plan_id = _require_string(plan.get("plan_id"), "plan.plan_id")
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    try:
        current = root
        for component in PurePosixPath(relative).parts:
            current = current / component
            status = current.lstat()
            if stat.S_ISLNK(status.st_mode):
                raise ArmReadinessError(
                    "readiness_pack_namespace_anomalous",
                    f"frozen plan reference traverses a symlink: {relative}",
                )
        if not stat.S_ISREG(candidate.lstat().st_mode):
            raise ArmReadinessError(
                "readiness_pack_namespace_anomalous",
                f"frozen plan is not a regular file: {relative}",
            )
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
        raw = candidate.read_bytes()
    except ArmReadinessError:
        raise
    except (OSError, ValueError) as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable",
            f"frozen plan is missing, unreadable, or outside the pack: {relative}",
        ) from exc

    repository, _pack_prefix, pack_relative = _repository_and_pack_relative(root)
    repository_relative = (PurePosixPath(pack_relative) / relative).as_posix()
    committed = _git_blob_at_head(repository, repository_relative)
    if committed is None:
        raise ArmReadinessError(
            "readiness_pack_not_committed",
            f"frozen plan is not committed at HEAD: {relative}",
        )
    if committed != raw:
        raise ArmReadinessError(
            "readiness_pack_digest_mismatch",
            f"frozen plan differs from committed bytes: {relative}",
        )
    try:
        plan_value = parse_json_bytes(raw)
    except ArmReadinessError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"frozen plan is invalid JSON: {relative}"
        ) from exc
    if not isinstance(plan_value, Mapping) or plan_value.get("plan_id") != plan_id:
        raise ArmReadinessError(
            "readiness_pack_digest_mismatch",
            "frozen plan plan_id differs from plan_tree.json",
        )
    digest = sha256_bytes(raw)
    for field_name in ("actual_sha256", "declared_sha256"):
        declared = plan.get(field_name)
        if declared is not None and declared != digest:
            raise ArmReadinessError(
                "readiness_pack_digest_mismatch",
                f"plan.{field_name} differs from the committed frozen plan",
            )
    return resolved, relative, plan_id, raw


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
    # Every issued D-079 generation routes as the issued artifact.  The D-138
    # reissue re-derived the same corpus at the integrated estimator head; the
    # anchor-v3 generation re-derived the same LEDGER under a corrected
    # estimator method.  Neither is a D-102 corpus-GROWTH successor, which is
    # what `SUCCESSOR_ACCEPTANCE_ONLY` rows exist for.  Earlier ids stay listed
    # so predecessor packs are unaffected.
    return issued in {
        "d079",
        "d079_calibration_acceptance_v2_n19",
        "d079_calibration_acceptance_v2_n19_r2",
        "d079_calibration_acceptance_v2_n17_r3",
        "d079_calibration_acceptance_v2_n17_r4",
        "d079_calibration_acceptance_v2_n17_r5",
        "d079_calibration_acceptance_v2_n17_r6",
    }


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
    enforce_expiry: bool = True,
    launch_binding_cache: dict[Path, bytes] | None = None,
    lifecycle_registry: Mapping[str, Any] | None = None,
    step6_confirmation_table: Path | str | None = None,
) -> Mapping[str, Any]:
    _validate_evidence_item(item, "evidence item")
    if item["schema_version"] not in GENERIC_EVIDENCE_RECEIPT_SCHEMAS:
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
        if launch_binding_cache is None:
            raw = path.read_bytes()
            sidecar = path.with_name(f"{path.name}.sha256").read_bytes()
        else:
            raw = _read_launch_binding_artifact(
                path,
                max_bytes=_LAUNCH_BINDING_RECEIPT_MAX_BYTES,
                label="launch-recipe evidence receipt",
                cache=launch_binding_cache,
            )
            sidecar = _read_launch_binding_artifact(
                path.with_name(f"{path.name}.sha256"),
                max_bytes=_LAUNCH_BINDING_SIDECAR_MAX_BYTES,
                label="launch-recipe evidence sidecar",
                cache=launch_binding_cache,
            )
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
    if (
        lifecycle_registry is not None
        and item["namespace"] == "PACK"
        and receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
    ):
        raise EvidenceLifecycleError(
            lifecycle_registry,
            "V1_GRANDFATHERING",
            "legacy generic freeze evidence may not enter the R1 lifecycle",
            evidence_id=str(receipt["evidence_id"]),
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
    receipt_head = receipt.get("head_commit", receipt.get("derivation_commit"))
    if (
        receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
        and
        expected_pack_sha256 is not None
        and receipt["pack_sha256"] != expected_pack_sha256
    ) or (
        receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
        and expected_head_commit is not None
        and receipt_head != expected_head_commit
    ):
        raise ArmReadinessError(
            "readiness_evidence_digest_mismatch",
            "evidence item is stale for pack or HEAD",
        )
    if (
        expected_boot_session_id is not None
        and "boot_session_id" in receipt
        and receipt["boot_session_id"] != expected_boot_session_id
    ):
        raise ArmReadinessError(
            "readiness_record_expired", "evidence item belongs to a prior boot session"
        )
    if enforce_expiry and "valid_until_monotonic_ns" in receipt:
        authentication_now = (
            time.monotonic_ns()
            if now_monotonic_ns is None
            else now_monotonic_ns
        )
        if receipt["valid_until_monotonic_ns"] < authentication_now:
            raise ArmReadinessError(
                "readiness_record_expired", "evidence item expired"
            )
    source_payloads: dict[str, tuple[bytes, Mapping[str, Any]]] = {}
    for fact in receipt["facts"]:
        source_path = _resolve_namespace_path(
            namespace_root,
            fact["source_path"],
            "evidence fact source_path",
        )
        try:
            if launch_binding_cache is None:
                source_raw = source_path.read_bytes()
            else:
                source_raw = _read_launch_binding_artifact(
                    source_path,
                    max_bytes=_LAUNCH_BINDING_SOURCE_MAX_BYTES,
                    label="launch-recipe T-0 source",
                    cache=launch_binding_cache,
                )
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
        try:
            source_value = parse_json_bytes(source_raw, require_canonical=True)
        except ArmReadinessError as exc:
            raise ArmReadinessError(
                "readiness_evidence_digest_mismatch",
                f"evidence fact source is invalid: {exc}",
            ) from exc
        if not isinstance(source_value, Mapping):
            raise ArmReadinessError(
                "readiness_evidence_digest_mismatch",
                "evidence fact source is not an object",
            )
        source_payloads[fact["source_path"]] = (source_raw, source_value)
    if receipt["schema_version"] != EVIDENCE_RECEIPT_SCHEMA:
        if lifecycle_registry is None:
            raise ArmReadinessError(
                "readiness_row_registry_mismatch",
                "R1 evidence requires its governed lifecycle registry",
            )
        if len(source_payloads) != 1:
            raise EvidenceLifecycleError(
                lifecycle_registry,
                "DEPENDENCY_MANIFEST",
                "R1 evidence must bind exactly one dependency manifest",
                evidence_id=str(receipt["evidence_id"]),
            )
        _source_raw, source = next(iter(source_payloads.values()))
        from joulewise import arm_readiness_evidence as _evidence_author

        expected_class = _evidence_author._DERIVER_FRESHNESS_CLASSES.get(
            str(receipt["kind"])
        )
        if expected_class is None:
            raise EvidenceLifecycleError(
                lifecycle_registry,
                "UNKNOWN_POLICY",
                f"no code freshness class for {receipt['kind']!r}",
                evidence_id=str(receipt["evidence_id"]),
            )
        repository, _pack_prefix, pack_relative = _repository_and_pack_relative(
            pack_root
        )
        current_head = expected_head_commit or _git_text(repository, "rev-parse", "HEAD")
        if current_head is None:
            raise EvidenceLifecycleError(
                lifecycle_registry,
                "DEPENDENCY_CHANGED_SET",
                "current reviewed HEAD is unavailable",
                evidence_id=str(receipt["evidence_id"]),
            )
        validate_r1_evidence_lifecycle(
            repository,
            receipt,
            source,
            lifecycle_registry,
            current_head=current_head,
            expected_freshness_class=expected_class,
            plan_tree_path=f"{pack_relative}/plan_tree.json",
            step6_confirmation_table=step6_confirmation_table,
        )
        if expected_class == "RE_DERIVABLE":
            try:
                _evidence_author._r1_rederive_at_arm(pack_root, receipt, source)
            except (ValueError, _evidence_author.EvidenceAuthoringError) as exc:
                raise EvidenceLifecycleError(
                    lifecycle_registry,
                    "DEPENDENCY_MANIFEST",
                    f"ARM re-derivation refused: {exc}",
                    evidence_id=str(receipt["evidence_id"]),
                ) from exc
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
    launch_binding_cache: dict[Path, bytes] | None = None,
    lifecycle_registry: Mapping[str, Any] | None = None,
    step6_confirmation_table: Path | str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Mapping[str, Any]], list[dict[str, Any]]]:
    governed_lifecycle = (
        validate_r1_lifecycle_registry(lifecycle_registry)
        if lifecycle_registry is not None
        else None
    )
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
                if launch_binding_cache is None:
                    raw = path.read_bytes()
                    sidecar_raw = sidecars[filename].read_bytes()
                else:
                    raw = _read_launch_binding_artifact(
                        path,
                        max_bytes=_LAUNCH_BINDING_RECEIPT_MAX_BYTES,
                        label="launch-verification evidence receipt",
                        cache=launch_binding_cache,
                    )
                    sidecar_raw = _read_launch_binding_artifact(
                        sidecars[filename],
                        max_bytes=_LAUNCH_BINDING_SIDECAR_MAX_BYTES,
                        label="launch-verification evidence sidecar",
                        cache=launch_binding_cache,
                    )
                digest = sha256_bytes(raw)
                if sidecar_raw != gnu_sidecar(digest, filename):
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
                    receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
                    and (
                        (pack_sha256 is not None and receipt["pack_sha256"] != pack_sha256)
                        or (head_commit is not None and receipt["head_commit"] != head_commit)
                    )
                ):
                    raise ArmReadinessError(
                        "readiness_evidence_digest_mismatch", "evidence is stale for pack/HEAD"
                    )
                if (
                    governed_lifecycle is None
                    and
                    boot_session_id is not None
                    and "boot_session_id" in receipt
                    and receipt["boot_session_id"] != boot_session_id
                ):
                    raise ArmReadinessError(
                        "readiness_record_expired",
                        "evidence receipt belongs to a prior boot session",
                    )
                if (
                    governed_lifecycle is None
                    and
                    now_monotonic_ns is not None
                    and "valid_until_monotonic_ns" in receipt
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
                        if (
                            launch_binding_cache is not None
                            and receipt["kind"] == "LAUNCH_RECIPE"
                        ):
                            source_raw = _read_launch_binding_artifact(
                                source_path,
                                max_bytes=_LAUNCH_BINDING_SOURCE_MAX_BYTES,
                                label="launch-recipe T-0 source",
                                cache=launch_binding_cache,
                            )
                        else:
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
                    if receipt["kind"] == "TERMINAL_REVIEW":
                        terminal_source = parse_json_bytes(
                            source_raw, require_canonical=True
                        )
                        if (
                            not isinstance(terminal_source, Mapping)
                            or terminal_source.get("schema_version")
                            != _T0_EVIDENCE_SOURCE_SCHEMA
                        ):
                            # Historical synthetic fixtures predate the T-0
                            # source schema. They are never production inputs;
                            # the schema-bearing route below is unconditional.
                            continue
                        repository = _repo_for_pack(pack_root)
                        reviewed_head = head_commit or _git_text(
                            repository, "rev-parse", "HEAD"
                        )
                        reviewed_tree = (
                            _git_text(
                                repository,
                                "rev-parse",
                                f"{reviewed_head}^{{tree}}",
                            )
                            if reviewed_head is not None
                            else None
                        )
                        if reviewed_tree is None:
                            raise ArmReadinessError(
                                "readiness_terminal_review_missing",
                                "reviewed HEAD tree is unavailable",
                            )
                        validate_terminal_review_head_tree(
                            terminal_source, reviewed_tree
                        )
                if governed_lifecycle is not None:
                    kind = str(receipt["kind"])
                    policy = _r1_policy_for_kind(governed_lifecycle, kind)
                    code_class = R1_EVIDENCE_FRESHNESS_CLASSES.get(kind)
                    if code_class is None or policy["freshness_class"] != code_class:
                        raise EvidenceLifecycleError(
                            governed_lifecycle,
                            "CLASS_MISMATCH",
                            f"registry cannot override the code class for {kind}",
                            evidence_id=str(receipt["evidence_id"]),
                        )
                    if boot_session_id is None or now_monotonic_ns is None:
                        raise EvidenceLifecycleError(
                            governed_lifecycle,
                            "UNKNOWN_POLICY",
                            "R1 production evidence validation lacks boot/time context",
                            evidence_id=str(receipt["evidence_id"]),
                        )
                    validate_r1_class_lifecycle(
                        receipt,
                        kind,
                        current_boot_session_id=boot_session_id,
                        now_monotonic_ns=now_monotonic_ns,
                        semantic_state_valid=(receipt["status"] == "PASS"),
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
                if namespace == "PACK" and lifecycle_registry is not None:
                    receipt = _authenticate_generic_evidence_item(
                        item,
                        pack_root,
                        custody_pack_root,
                        expected_head_commit=head_commit,
                        expected_boot_session_id=boot_session_id,
                        now_monotonic_ns=now_monotonic_ns,
                        lifecycle_registry=lifecycle_registry,
                        step6_confirmation_table=step6_confirmation_table,
                    )
                items.append(item)
                receipts[receipt["evidence_id"]] = receipt
            except EvidenceLifecycleError as exc:
                refusals.append(exc.refusal())
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


def _predicate_passes(
    receipt: Mapping[str, Any],
    predicate_id: str,
    *,
    expected_plan_sha256: str | None = None,
) -> bool:
    """Apply the D-134 row's content and source derivation predicate.

    ``expected_plan_sha256`` is the plan SHA-256 derived from *this* pack's
    committed plan bytes.  Rows whose contract predicate requires an
    evidence receipt to BIND the pack plan SHA fail closed when it is not
    supplied: a well-formed digest is not a bound digest.
    """

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
        if predicate_id == "t0.ledger_reservation.v1":
            # The contract requires the reservation receipt to BIND the pack
            # plan SHA, not merely to carry a well-formed digest.  A receipt
            # reserved against a different plan must refuse, and an unknown
            # expected value fails closed.
            if (
                expected_plan_sha256 is None
                or value.get("plan_sha256") != expected_plan_sha256
            ):
                continue
        if (
            predicate_id == "t0.single_launch_capability.v1"
            and fact["source_kind"] == "PACK"
        ):
            # Frozen pack bytes may attest only that the launch command is
            # frozen.  "Session/attempt IDs are unused" and "an atomic
            # single-use capability is available" are live T-0 conditions
            # that committed bytes cannot establish, so PACK-sourced
            # evidence can never satisfy this row on its own.
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
    expected_plan_sha256: str | None = None,
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
            if _predicate_passes(
                receipts[evidence_id],
                definition["predicate_id"],
                expected_plan_sha256=expected_plan_sha256,
            )
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


def _successor_chain_refusal(detail: str) -> ArmReadinessError:
    return ArmReadinessError("readiness_successor_chain_invalid", detail)


def _read_predecessor_file(pack_root: Path, relative: str, where: str) -> bytes:
    """Read one predecessor-pack file without following a symlink out of it."""

    try:
        resolved_root = pack_root.resolve(strict=True)
        current = pack_root
        for component in PurePosixPath(relative).parts:
            current = current / component
            if stat.S_ISLNK(current.lstat().st_mode):
                raise OSError(f"{where} traverses a symlink")
        if not stat.S_ISREG(current.lstat().st_mode):
            raise OSError(f"{where} is not a regular file")
        current.resolve(strict=True).relative_to(resolved_root)
        return current.read_bytes()
    except (OSError, ValueError) as exc:
        raise _successor_chain_refusal(
            f"{where} is missing, unreadable, or outside the predecessor pack: {relative}"
        ) from exc


def _predecessor_evidence_set_sha256(evidence: Sequence[Mapping[str, Any]]) -> str:
    """Domain-separated canonical hash of a freeze receipt's evidence array."""

    return sha256_bytes(
        FREEZE_PREDECESSOR_EVIDENCE_SET_DOMAIN + render_json(list(evidence))
    )


def _predecessor_pinned_receipt(
    predecessor_root: Path,
) -> tuple[Mapping[str, Any], dict[str, str], Mapping[str, Any]]:
    """Return the predecessor's plan-pinned freeze receipt, pin, and identity item.

    Every value here comes from the predecessor pack's OWN committed bytes.  The
    current R2 plan resolver and the live pack/profile map are deliberately not
    consulted: a superseded pack is a historical record whose plan spelling and
    pack ID are no longer live vocabulary, and re-deriving them would make the
    committed v1 packs permanently unauthenticatable.
    """

    try:
        tree, _tree_raw = _plan_tree(predecessor_root)
    except ArmReadinessError as exc:
        raise _successor_chain_refusal(
            f"predecessor plan tree is unreadable: {exc}"
        ) from exc
    attachments = tree.get("arm_attachments")
    declaration = (
        attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    )
    pin = (
        declaration.get("freeze_receipt")
        if isinstance(declaration, Mapping)
        else None
    )
    if not isinstance(pin, Mapping) or set(pin) != {"path", "sha256"}:
        raise _successor_chain_refusal(
            "predecessor plan tree does not pin exactly one freeze receipt"
        )
    try:
        receipts = scan_receipt_namespace(
            predecessor_root / "arm_readiness.freeze.receipts", "freeze"
        )
    except ArmReadinessError as exc:
        raise _successor_chain_refusal(
            f"predecessor freeze namespace is anomalous: {exc}"
        ) from exc
    matches = [
        item
        for item in receipts
        if f"arm_readiness.freeze.receipts/{item['path'].name}" == pin["path"]
        and item["sha256"] == pin["sha256"]
    ]
    if len(matches) != 1:
        raise _successor_chain_refusal(
            "the plan-pinned predecessor freeze receipt does not exist exactly once"
        )
    receipt = matches[0]["receipt"]
    identity_items = [
        item
        for item in receipt["evidence"]
        if item["schema_version"] == IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA
    ]
    if len(identity_items) != 1:
        raise _successor_chain_refusal(
            "predecessor freeze receipt does not bind exactly one identity receipt"
        )
    return (
        receipt,
        {"path": str(pin["path"]), "sha256": str(pin["sha256"])},
        identity_items[0],
    )


def _predecessor_identity_receipt(
    predecessor_root: Path, item: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Authenticate the predecessor's identity projection receipt bytes."""

    relative = _require_relative_path(item["path"], "predecessor identity receipt path")
    raw = _read_predecessor_file(
        predecessor_root, relative, "predecessor identity projection receipt"
    )
    digest = sha256_bytes(raw)
    if digest != item["sha256"]:
        raise _successor_chain_refusal(
            "predecessor identity projection receipt digest differs from its binding"
        )
    sidecar_relative = PurePosixPath(relative).with_suffix(".sha256").as_posix()
    sidecar = _read_predecessor_file(
        predecessor_root,
        sidecar_relative,
        "predecessor identity projection sidecar",
    )
    if sidecar != gnu_sidecar(digest, PurePosixPath(relative).name):
        raise _successor_chain_refusal(
            "predecessor identity projection sidecar does not authenticate its bytes"
        )
    try:
        return validate_projection_receipt(
            parse_json_bytes(raw, require_canonical=True)
        )
    except (IdentityPinProjectionError, ArmReadinessError) as exc:
        raise _successor_chain_refusal(
            f"predecessor identity projection receipt is invalid: {exc}"
        ) from exc


def _resolve_predecessor_root(pack_root: Path, candidate: Path) -> tuple[Path, Path, str]:
    """Resolve a predecessor pack root inside the successor's repository."""

    try:
        successor_root = Path(pack_root).resolve(strict=True)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"pack root is unreadable: {exc}"
        ) from exc
    repository = _repo_for_pack(successor_root)
    try:
        resolved = Path(candidate).resolve(strict=True)
        relative = resolved.relative_to(repository).as_posix()
        if not resolved.is_dir() or Path(candidate).is_symlink():
            raise OSError("predecessor pack root is not a real directory")
    except (OSError, ValueError) as exc:
        raise _successor_chain_refusal(
            "predecessor pack is absent, unreadable, or outside the successor repository"
        ) from exc
    if resolved == successor_root:
        raise _successor_chain_refusal("a pack cannot be its own freeze predecessor")
    return successor_root, resolved, relative


def _authenticate_freeze_predecessor(
    pack_root: Path,
    predecessor: Mapping[str, Any],
    *,
    successor_receipt_id: str,
    successor_profile: str,
) -> Mapping[str, Any]:
    """Authenticate D-139's freeze chain before any successor write or use.

    Absent, unreadable, uncommitted, malformed, digest-divergent, profile
    mismatched, REFUSE-status, and ordinal-violating ancestries all refuse with
    the governed ``readiness_successor_chain_invalid`` code.  An invalid
    ancestry never mints a REFUSE receipt.
    """

    try:
        _validate_freeze_predecessor(predecessor)
    except ArmReadinessError as exc:
        raise _successor_chain_refusal(
            f"predecessor binding is malformed: {exc}"
        ) from exc
    try:
        successor_root = Path(pack_root).resolve(strict=True)
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_pack_unreadable", f"pack root is unreadable: {exc}"
        ) from exc
    repository = _repo_for_pack(successor_root)
    candidate = repository.joinpath(
        *PurePosixPath(str(predecessor["pack_path"])).parts
    )
    successor_root, predecessor_root, relative = _resolve_predecessor_root(
        successor_root, candidate
    )
    if relative != predecessor["pack_path"]:
        raise _successor_chain_refusal(
            "predecessor pack path does not resolve to its recorded repository location"
        )
    if predecessor_root.name != predecessor["pack_id"]:
        raise _successor_chain_refusal("predecessor pack_path does not name pack_id")
    if successor_root.name == predecessor["pack_id"]:
        raise _successor_chain_refusal("a pack cannot be its own freeze predecessor")
    if predecessor["pack_digest_algorithm"] != PACK_DIGEST_ALGORITHM:
        raise _successor_chain_refusal(
            "predecessor pack digest algorithm is not the D-134 algorithm"
        )
    try:
        observed_pack_sha256 = committed_pack_tree_sha256(predecessor_root)
    except ArmReadinessError as exc:
        raise _successor_chain_refusal(
            f"predecessor pack bytes are not authentically committed: {exc}"
        ) from exc
    if observed_pack_sha256 != predecessor["pack_sha256"]:
        raise _successor_chain_refusal(
            "predecessor committed pack digest differs from the recorded binding"
        )
    receipt, pin, identity_item = _predecessor_pinned_receipt(predecessor_root)
    recorded_freeze = predecessor["freeze_receipt"]
    if (
        pin["path"] != recorded_freeze["path"]
        or pin["sha256"] != recorded_freeze["sha256"]
        or receipt["receipt_id"] != recorded_freeze["receipt_id"]
    ):
        raise _successor_chain_refusal(
            "predecessor freeze receipt binding differs from the recorded values"
        )
    if receipt["status"] != "PASS":
        raise _successor_chain_refusal(
            "predecessor freeze receipt did not record PASS"
        )
    identity = receipt["pack_identity"]
    if (
        identity["pack_id"] != predecessor["pack_id"]
        or identity["plan_id"] != predecessor["plan_id"]
        or identity["plan_sha256"] != predecessor["plan_sha256"]
    ):
        raise _successor_chain_refusal(
            "predecessor pack identity differs from the recorded bindings"
        )
    plan_raw = _read_predecessor_file(
        predecessor_root,
        _require_relative_path(identity["plan_path"], "predecessor plan_path"),
        "predecessor frozen plan",
    )
    if sha256_bytes(plan_raw) != predecessor["plan_sha256"]:
        raise _successor_chain_refusal(
            "predecessor frozen-plan bytes differ from the recorded plan digest"
        )
    recorded_identity = predecessor["identity_receipt"]
    if (
        identity_item["path"] != recorded_identity["path"]
        or identity_item["sha256"] != recorded_identity["sha256"]
    ):
        raise _successor_chain_refusal(
            "recorded identity receipt differs from the predecessor freeze binding"
        )
    identity_receipt = _predecessor_identity_receipt(predecessor_root, identity_item)
    if identity_receipt["receipt_id"] != recorded_identity["receipt_id"]:
        raise _successor_chain_refusal(
            "predecessor identity projection receipt ID differs from the recorded binding"
        )
    if identity_receipt["status"] != "PASS":
        raise _successor_chain_refusal(
            "predecessor identity projection receipt did not record PASS"
        )
    if (
        _predecessor_evidence_set_sha256(receipt["evidence"])
        != predecessor["evidence_set_sha256"]
    ):
        raise _successor_chain_refusal(
            "predecessor evidence-set digest differs from the recorded binding"
        )
    if receipt["row_registry"]["plan_profile"] != successor_profile:
        raise _successor_chain_refusal(
            "predecessor freeze receipt binds a different plan profile"
        )
    predecessor_ordinal = _freeze_receipt_ordinal(
        receipt["receipt_id"], "predecessor freeze receipt_id"
    )
    successor_ordinal = _freeze_receipt_ordinal(
        successor_receipt_id, "successor freeze receipt_id"
    )
    if successor_ordinal != predecessor_ordinal + 1:
        raise _successor_chain_refusal(
            "successor ordinal is not the predecessor ordinal plus one"
        )
    return receipt


def _derive_freeze_predecessor(
    pack_root: Path, predecessor_pack_root: Path
) -> dict[str, Any]:
    """Derive the serialized predecessor object from committed paths only."""

    _successor_root, predecessor_root, relative = _resolve_predecessor_root(
        Path(pack_root), Path(predecessor_pack_root)
    )
    receipt, pin, identity_item = _predecessor_pinned_receipt(predecessor_root)
    identity_receipt = _predecessor_identity_receipt(predecessor_root, identity_item)
    try:
        pack_sha256 = committed_pack_tree_sha256(predecessor_root)
    except ArmReadinessError as exc:
        raise _successor_chain_refusal(
            f"predecessor pack bytes are not authentically committed: {exc}"
        ) from exc
    identity = receipt["pack_identity"]
    return {
        "pack_id": predecessor_root.name,
        "pack_path": relative,
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
        "pack_sha256": pack_sha256,
        "plan_id": str(identity["plan_id"]),
        "plan_sha256": str(identity["plan_sha256"]),
        "freeze_receipt": {
            "receipt_id": str(receipt["receipt_id"]),
            "path": pin["path"],
            "sha256": pin["sha256"],
        },
        "identity_receipt": {
            "receipt_id": str(identity_receipt["receipt_id"]),
            "path": str(identity_item["path"]),
            "sha256": str(identity_item["sha256"]),
        },
        "evidence_set_sha256": _predecessor_evidence_set_sha256(receipt["evidence"]),
    }


def _load_freeze_reference(
    pack_root: Path,
    tree: Mapping[str, Any],
    registry_reference: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    require_pass: bool = True,
    step6_confirmation_table: Path | str | None = None,
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
    if receipt["schema_version"] == FREEZE_RECEIPT_V2_SCHEMA:
        _authenticate_freeze_predecessor(
            pack_root,
            receipt["predecessor"],
            successor_receipt_id=str(receipt["receipt_id"]),
            successor_profile=str(registry_reference["plan_profile"]),
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
    lifecycle_registry = (
        registry["freeze_evidence_lifecycle"]
        if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
        else None
    )
    generic_items = [
        item
        for item in receipt["evidence"]
        if item["schema_version"] in GENERIC_EVIDENCE_RECEIPT_SCHEMAS
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
                expected_head_commit=(
                    reviewed_main(pack_root)["head_commit"]
                    if lifecycle_registry is not None
                    else None
                ),
                lifecycle_registry=lifecycle_registry,
                step6_confirmation_table=step6_confirmation_table,
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
    # Loading a freeze receipt is BYTE AUTHENTICATION plus RECORDED-CONCLUSION
    # RETURN, never a re-adjudication of the conclusion itself.  Everything the
    # receipt binds has already been authenticated above -- the plan-pinned
    # receipt and its sidecar, ``pack_identity`` against committed pack bytes,
    # every referenced evidence digest including the identity-projection
    # receipt, and (for v2) the predecessor chain -- so this comparison exists
    # only to prove the recorded rows and refusals still DERIVE from those
    # authenticated bytes.  Refusal ORDER is not part of that derivation: mint
    # writes the canonical order while ``_evaluate_rows`` returns row-definition
    # order, so both sides are canonicalized before comparison.  Without this a
    # validly minted REFUSE -- e.g. one caused by a REFUSE identity projection,
    # whose refusal sorts by code away from its row-definition slot -- would
    # authenticate perfectly and still raise instead of replaying as the REFUSE
    # it is.  The recorded conclusion replays, PASS or REFUSE alike; only the
    # ``require_pass`` gate below decides whether a caller may USE a REFUSE.
    if receipt["rows"] != expected_rows or _canonical_refusals(
        receipt["refusals"]
    ) != _canonical_refusals(expected_refusals):
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
    registry: Mapping[str, Any] | None = None,
    *,
    step6_confirmation_table: Path | str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Mapping[str, Any]]]:
    items = copy.deepcopy(list(freeze_receipt["evidence"]))
    receipts: dict[str, Mapping[str, Any]] = {}
    boot_session_id = _current_boot_session_id()
    plan_identity_item, plan_identity_receipt, _reasons = (
        _load_frozen_identity_evidence(pack_root, tree)
    )
    lifecycle_registry = (
        registry["freeze_evidence_lifecycle"]
        if isinstance(registry, Mapping)
        and registry.get("schema_version") == R1_ROW_REGISTRY_SCHEMA
        else None
    )
    expected_head = (
        reviewed_main(pack_root)["head_commit"]
        if lifecycle_registry is not None
        else None
    )
    for item in items:
        if item["schema_version"] in GENERIC_EVIDENCE_RECEIPT_SCHEMAS:
            receipts[item["evidence_id"]] = _authenticate_generic_evidence_item(
                item,
                pack_root,
                pack_root,
                expected_boot_session_id=boot_session_id,
                expected_head_commit=expected_head,
                lifecycle_registry=lifecycle_registry,
                step6_confirmation_table=step6_confirmation_table,
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


def generate_freeze_receipt(
    pack_root: Path | str,
    *,
    predecessor_pack_root: Path | str | None = None,
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
) -> dict[str, Any]:
    """Write or idempotently authenticate the pack's non-authorizing receipt.

    A successor pack (family generation two or later) must present the path of
    its predecessor pack.  Every ID, digest, ordinal, and conclusion in the
    resulting ``predecessor`` binding is derived here from committed bytes; the
    caller supplies paths only.
    """

    root = Path(pack_root).resolve(strict=True)
    try:
        if predecessor_pack_root is not None:
            _gate_receipt_histsem(Path(predecessor_pack_root))
    except HistoricalSemanticsError as exc:
        return {
            "status": "REFUSE",
            "arm_disposition": "NOT_APPLICABLE",
            "receipt_path": None,
            "receipt_sha256": None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
            "mutated": False,
        }
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    attachments = tree.get("arm_attachments")
    readiness = attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    _valid_plan_attachment(readiness, registry_reference)
    generation = _pack_generation(root.name)
    # Split S-2: engage on the REGISTRY's generation threshold, and only when
    # the registry actually carries one.  A registry without the reviewed value
    # never engages family publication (the `_v1`..`_v3` generations).
    family_first_generation: int | None
    try:
        family_first_generation = _family_first_generation(registry)
    except ArmReadinessError:
        family_first_generation = None
    # Resolve the predecessor ONCE, and refuse with the governed code rather
    # than letting a bare OSError escape.  The strict resolve used to sit
    # inside the gate condition below, where an absent directory raised
    # FileNotFoundError straight out of generate_freeze_receipt.  That was
    # unreachable while no registry carried a generation threshold (the `and`
    # short-circuited on `family_first_generation is None`); the ruled registry
    # supplies one, so the expression is now evaluated on every call.
    predecessor_root: Path | None = None
    if predecessor_pack_root is not None:
        try:
            predecessor_root = Path(predecessor_pack_root).resolve(strict=True)
        except OSError as exc:
            raise _successor_chain_refusal(
                f"predecessor pack root is unreadable: {exc}"
            ) from exc
    if (
        predecessor_root is not None
        and family_first_generation is not None
        and _pack_generation(predecessor_root.name) >= family_first_generation
    ):
        try:
            _gate_family_publication(
                predecessor_root,
                marker_path=family_publication_marker,
                confirmation_path=step6_confirmation_table,
            )
        except FamilyPublicationError as exc:
            predecessor_registry, _raw = load_registry(
                _repo_for_pack(Path(predecessor_pack_root))
            )
            entry = _family_refusal_entry(predecessor_registry)
            return {
                "status": "REFUSE",
                "arm_disposition": "NOT_APPLICABLE",
                "receipt_path": None,
                "receipt_sha256": None,
                "reason_codes": [entry["code"]],
                "detail": f"{exc.check_id}: {exc}",
                "mutated": False,
            }
    if generation > 1 and predecessor_pack_root is None:
        raise _successor_chain_refusal(
            "a successor pack requires an authenticated predecessor pack root"
        )
    if generation == 1 and predecessor_pack_root is not None:
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "a first-generation pack cannot carry a freeze predecessor",
        )
    namespace = root / "arm_readiness.freeze.receipts"
    existing = scan_receipt_namespace(namespace, "freeze", allow_absent=True)
    if existing and readiness["freeze_receipt"] is not None:
        pinned = [
            item
            for item in existing
            if {
                "path": f"arm_readiness.freeze.receipts/{item['path'].name}",
                "sha256": item["sha256"],
            }
            == readiness["freeze_receipt"]
        ]
        if len(pinned) != 1:
            raise ArmReadinessError(
                "readiness_freeze_receipt_mismatch", "existing freeze receipt is not plan-pinned"
            )
        latest = pinned[0]
        # Idempotent replay is an active use of the receipt, not a namespace
        # lookup.  Re-authenticate the CURRENT successor in full before any
        # ``mutated: false`` conclusion: the plan-pinned receipt and sidecar,
        # ``pack_identity`` against the committed pack bytes, and every
        # referenced evidence digest including the identity-projection receipt.
        # For a v2 receipt this loader also authenticates the recorded
        # predecessor chain, so ancestry is never the only thing checked.
        # ``require_pass`` stays False because a recorded REFUSE must replay as
        # the REFUSE it is rather than raise.
        _load_freeze_reference(
            root,
            tree,
            registry_reference,
            registry,
            require_pass=False,
            step6_confirmation_table=step6_confirmation_table,
        )
        if (
            latest["receipt"]["schema_version"] == FREEZE_RECEIPT_V2_SCHEMA
            and predecessor_pack_root is not None
            and _derive_freeze_predecessor(root, Path(predecessor_pack_root))
            != dict(latest["receipt"]["predecessor"])
        ):
            raise _successor_chain_refusal(
                "replayed predecessor derivation differs from the recorded binding"
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
    # Chain authentication precedes every write and every derived conclusion.
    predecessor: dict[str, Any] | None = None
    number = 1
    if generation > 1:
        predecessor = _derive_freeze_predecessor(root, Path(predecessor_pack_root))
        number = (
            _freeze_receipt_ordinal(
                predecessor["freeze_receipt"]["receipt_id"],
                "predecessor freeze receipt_id",
            )
            + 1
        )
        _authenticate_freeze_predecessor(
            root,
            predecessor,
            successor_receipt_id=f"freeze-{number:04d}",
            successor_profile=str(registry_reference["plan_profile"]),
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
        lifecycle_registry=(
            registry["freeze_evidence_lifecycle"]
            if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
            else None
        ),
        step6_confirmation_table=step6_confirmation_table,
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
        key=_refusal_sort_key,
    )
    status = "REFUSE" if refusals else "PASS"
    receipt_name = f"freeze-{number:04d}.json"
    receipt = {
        "schema_version": (
            FREEZE_RECEIPT_V2_SCHEMA if predecessor is not None else FREEZE_RECEIPT_SCHEMA
        ),
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
        "assurance": copy.deepcopy(ASSURANCE),
    }
    if predecessor is not None:
        receipt["predecessor"] = copy.deepcopy(predecessor)
    else:
        receipt["supersedes"] = None
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
    plan_path, _plan_relative, _plan_id, plan_raw = resolve_frozen_plan(
        pack_root, tree
    )
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
            key=_refusal_sort_key,
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
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    try:
        _gate_receipt_histsem(root)
    except HistoricalSemanticsError as exc:
        return {
            "status": "REFUSE",
            "arm_disposition": "NO_GO",
            "receipt_path": None,
            "receipt_sha256": None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
    context = validate_arm_context(arm_context)
    publication_root = Path(window_custody_root).resolve() / "family_publication"
    marker_path = (
        Path(family_publication_marker)
        if family_publication_marker is not None
        else publication_root / FAMILY_PUBLICATION_MARKER_NAME
    )
    confirmation_path = (
        Path(step6_confirmation_table)
        if step6_confirmation_table is not None
        else publication_root / STEP6_CONFIRMATION_TABLE_NAME
    )
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
        step6_confirmation_table=confirmation_path,
    )
    custody_root = Path(window_custody_root).resolve()
    custody_pack_root = custody_root / root.name
    arm_namespace = custody_pack_root / "arm_readiness.receipts"
    existing = scan_receipt_namespace(arm_namespace, "arm", allow_absent=True)
    prior_receipts = [item["receipt"] for item in existing]
    number = max((item["number"] for item in existing), default=0) + 1
    evaluated_at_monotonic_ns = time.monotonic_ns()
    boot_session_id = _current_boot_session_id()
    lifecycle_registry = (
        registry["freeze_evidence_lifecycle"]
        if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
        else None
    )
    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=pack["pack_sha256"],
        head_commit=reviewed["head_commit"],
        boot_session_id=boot_session_id,
        now_monotonic_ns=evaluated_at_monotonic_ns,
        include_pack=False,
        lifecycle_registry=lifecycle_registry,
        step6_confirmation_table=confirmation_path,
    )
    try:
        _gate_family_publication(
            root,
            marker_path=marker_path,
            confirmation_path=confirmation_path,
        )
    except FamilyPublicationError:
        entry = _family_refusal_entry(registry)
        evidence_refusals.append(
            {
                "type": entry["type"],
                "code": entry["code"],
                "row_id": None,
                "evidence_id": None,
            }
        )
    try:
        freeze_items, freeze_evidence_receipts = _freeze_evidence_for_arm(
            root,
            tree,
            freeze_receipt,
            registry,
            step6_confirmation_table=confirmation_path,
        )
    except EvidenceLifecycleError as exc:
        evidence_refusals.append(exc.refusal())
        freeze_items, freeze_evidence_receipts = [], {}
    duplicate_ids = set(evidence_receipts).intersection(freeze_evidence_receipts)
    if duplicate_ids:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            f"arm and freeze evidence IDs collide: {sorted(duplicate_ids)!r}",
        )
    evidence_items.extend(freeze_items)
    evidence_items.sort(key=lambda item: item["evidence_id"])
    evidence_receipts.update(freeze_evidence_receipts)
    if lifecycle_registry is not None:
        try:
            validate_r1_temporal_budget(
                evidence_receipts.values(),
                lifecycle_registry,
                now_monotonic_ns=evaluated_at_monotonic_ns,
            )
        except EvidenceLifecycleError as exc:
            evidence_refusals.append(exc.refusal())
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
        expected_plan_sha256=_pack_identity(root, tree)["plan_sha256"],
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
        key=_refusal_sort_key,
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
    arm_horizon_ns = (
        int(lifecycle_registry["arm_policy"]["capability_horizon_ns"])
        if lifecycle_registry is not None
        else validity_ns
    )
    valid_until = min(
        [evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations]
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
    *,
    launch_binding_cache: dict[Path, bytes] | None = None,
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
    publication_root = custody_pack_root.parent / "family_publication"
    confirmation_path = publication_root / STEP6_CONFIRMATION_TABLE_NAME
    freeze_receipt, freeze_reference = _load_freeze_reference(
        root,
        tree,
        registry_reference,
        registry,
        require_pass=False,
        step6_confirmation_table=confirmation_path,
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
        launch_binding_cache=launch_binding_cache,
        lifecycle_registry=(
            registry["freeze_evidence_lifecycle"]
            if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
            else None
        ),
        step6_confirmation_table=confirmation_path,
    )
    try:
        _gate_family_publication(
            root,
            marker_path=publication_root / FAMILY_PUBLICATION_MARKER_NAME,
            confirmation_path=confirmation_path,
        )
    except FamilyPublicationError:
        entry = _family_refusal_entry(registry)
        evidence_refusals.append(
            {
                "type": entry["type"],
                "code": entry["code"],
                "row_id": None,
                "evidence_id": None,
            }
        )
    try:
        freeze_items, freeze_evidence_receipts = _freeze_evidence_for_arm(
            root,
            tree,
            freeze_receipt,
            registry,
            step6_confirmation_table=confirmation_path,
        )
    except EvidenceLifecycleError as exc:
        evidence_refusals.append(exc.refusal())
        freeze_items, freeze_evidence_receipts = [], {}
    if set(evidence_receipts).intersection(freeze_evidence_receipts):
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            "arm and freeze evidence IDs collide",
        )
    evidence_items.extend(freeze_items)
    evidence_items.sort(key=lambda item: item["evidence_id"])
    evidence_receipts.update(freeze_evidence_receipts)
    lifecycle_registry = (
        registry["freeze_evidence_lifecycle"]
        if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
        else None
    )
    if lifecycle_registry is not None:
        try:
            validate_r1_temporal_budget(
                evidence_receipts.values(),
                lifecycle_registry,
                now_monotonic_ns=time.monotonic_ns(),
            )
        except EvidenceLifecycleError as exc:
            evidence_refusals.append(exc.refusal())
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
        expected_plan_sha256=_pack_identity(root, tree)["plan_sha256"],
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
        key=_refusal_sort_key,
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


def _verify_arm_receipt(
    pack_root: Path | str,
    arm_receipt: Path | str,
    *,
    require_unconsumed: bool,
    launch_binding_cache: dict[Path, bytes] | None = None,
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
    validate_r1_class_lifecycle(
        receipt,
        "ARM_CAPABILITY",
        current_boot_session_id=_current_boot_session_id(),
        now_monotonic_ns=time.monotonic_ns(),
        semantic_state_valid=True,
        capability_consumed=(
            consumption_path.exists() or consumption_path.is_symlink()
        ),
    )
    if require_unconsumed and (
        consumption_path.exists() or consumption_path.is_symlink()
    ):
        raise ArmReadinessError(
            "readiness_record_consumed", "launch capability was already consumed"
        )
    expected_rows, expected_refusals = _derive_arm_semantics_for_verification(
        root,
        custody_pack_root,
        receipt,
        launch_binding_cache=launch_binding_cache,
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


def verify_arm_receipt(
    pack_root: Path | str, arm_receipt: Path | str
) -> dict[str, Any]:
    return _verify_arm_receipt(
        pack_root, arm_receipt, require_unconsumed=True
    )


def _read_launch_lineage_primary(
    path: Path,
    *,
    missing_code: str,
) -> tuple[Mapping[str, Any], bytes, str]:
    try:
        if path.is_symlink():
            raise LaunchLineageError(
                "launch_consumption_invalid",
                f"launch-lineage primary must not be a symlink: {path}",
            )
        sidecar_path = path.with_name(f"{path.name}.sha256")
        if sidecar_path.is_symlink():
            raise LaunchLineageError(
                "launch_consumption_invalid",
                f"launch-lineage sidecar must not be a symlink: {sidecar_path}",
            )
        raw = path.read_bytes()
        sidecar = sidecar_path.read_bytes()
    except LaunchLineageError:
        raise
    except OSError as exc:
        raise LaunchLineageError(
            missing_code, f"launch-lineage receipt is absent: {path}: {exc}"
        ) from exc
    digest = sha256_bytes(raw)
    if sidecar != gnu_sidecar(digest, path.name):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"launch-lineage receipt sidecar mismatch: {path}",
        )
    try:
        value = parse_json_bytes(raw, require_canonical=True)
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"launch-lineage receipt is noncanonical: {path}: {exc}",
        ) from exc
    if not isinstance(value, Mapping):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"launch-lineage receipt is not an object: {path}",
        )
    return value, raw, digest


def _launch_artifact_reference(
    path: Path,
    *,
    max_bytes: int,
    label: str,
    cache: dict[Path, bytes],
) -> dict[str, str]:
    if path.is_symlink():
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"launch artifact must not be a symlink: {path}",
        )
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"launch artifact must be one regular non-symlink file: {path}",
        )
    try:
        raw = _read_launch_binding_artifact(
            resolved, max_bytes=max_bytes, label=label, cache=cache
        )
    except LaunchLineageError:
        raise
    except MemoryError as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"{label} is unavailable within its frozen byte limit: {resolved}: {exc}",
        ) from exc
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"cannot read launch artifact {resolved}: {exc}",
        ) from exc
    return {"path": str(resolved), "sha256": sha256_bytes(raw)}


def _load_launch_manifest_for_consumption(
    launch_manifest: Path,
    *,
    launch_binding_cache: dict[Path, bytes],
) -> tuple[Mapping[str, Any], dict[str, str], dict[str, str], dict[str, str]]:
    manifest_reference = _launch_artifact_reference(
        launch_manifest,
        max_bytes=_LAUNCH_BINDING_MANIFEST_MAX_BYTES,
        label="launch manifest",
        cache=launch_binding_cache,
    )
    try:
        raw = launch_binding_cache[Path(manifest_reference["path"])]
        manifest = validate_launch_manifest(
            parse_json_bytes(raw, require_canonical=True)
        )
    except OSError as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable", f"cannot read launch manifest: {exc}"
        ) from exc
    try:
        window_root = Path(str(manifest["window_plan_root"])).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"launch manifest window root is unavailable: {exc}",
        ) from exc
    env_reference = _launch_artifact_reference(
        window_root / "window.env",
        max_bytes=_LAUNCH_BINDING_ENVIRONMENT_MAX_BYTES,
        label="window environment",
        cache=launch_binding_cache,
    )
    chain_reference = _launch_artifact_reference(
        window_root / "window-chain.zsh",
        max_bytes=_LAUNCH_BINDING_CHAIN_MAX_BYTES,
        label="window chain",
        cache=launch_binding_cache,
    )
    return manifest, manifest_reference, env_reference, chain_reference


def _read_v2_consumption(
    consumption_receipt: Path | str,
) -> tuple[Mapping[str, Any], bytes, str, Path]:
    path = Path(consumption_receipt).resolve(strict=False)
    value, raw, digest = _read_launch_lineage_primary(
        path, missing_code="launch_consumption_missing"
    )
    try:
        receipt = validate_consumption_receipt(value)
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"invalid consumption receipt: {exc}"
        ) from exc
    if receipt["schema_version"] != CONSUMPTION_RECEIPT_SCHEMA:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "legacy consumption receipts do not authorize a physical launch",
        )
    if (
        path.parent.name != "arm_readiness.consumptions"
        or path.name != f"{receipt['arm_receipt']['receipt_id']}.consumed.json"
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid", "consumption receipt is outside its namespace"
        )
    return receipt, raw, digest, path


def _read_exact_launch_reference(
    reference: Mapping[str, Any],
    *,
    max_bytes: int,
    label: str,
    expected_path: Path | None = None,
    launch_binding_cache: dict[Path, bytes] | None = None,
) -> tuple[Path, bytes]:
    path = Path(str(reference["path"]))
    try:
        if path.is_symlink():
            raise OSError("symlink refused")
        resolved = path.resolve(strict=True)
        raw = _read_launch_binding_artifact(
            resolved,
            max_bytes=max_bytes,
            label=label,
            cache=(
                launch_binding_cache
                if launch_binding_cache is not None
                else {}
            ),
        )
    except OSError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"bound launch artifact is unreadable: {path}: {exc}",
        ) from exc
    if not resolved.is_file():
        raise LaunchLineageError(
            "launch_consumption_invalid", f"bound launch artifact is not regular: {path}"
        )
    if expected_path is not None and resolved != expected_path.resolve(strict=True):
        raise LaunchLineageError(
            "launch_binding_mismatch", f"bound launch artifact path changed: {path}"
        )
    if sha256_bytes(raw) != reference["sha256"]:
        raise LaunchLineageError(
            "launch_binding_mismatch", f"bound launch artifact bytes changed: {path}"
        )
    return resolved, raw


def _launch_argv_matches(
    argv: Sequence[str], *, chain_path: Path, window_root: Path
) -> bool:
    """Compare the exact frozen argv without leaking path-resolution errors."""

    if len(argv) != 5:
        return False
    try:
        resolved_chain = Path(argv[3]).resolve(strict=True)
        resolved_root = Path(argv[4]).resolve(strict=True)
    except (OSError, RuntimeError):
        return False
    return (
        Path(argv[0]).name == "caffeinate"
        and argv[1] == "-is"
        and argv[2] == "/bin/zsh"
        and resolved_chain == chain_path
        and resolved_root == window_root
    )


def _read_launch_binding_artifact(
    path: Path,
    *,
    max_bytes: int,
    label: str,
    cache: dict[Path, bytes],
) -> bytes:
    """Read one reconciliation artifact once, with a fixed memory ceiling."""

    cached = cache.get(path)
    if cached is not None:
        return cached
    try:
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    f"{label} is not a regular file: {path}",
                )
            if opened.st_size > max_bytes:
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    f"{label} exceeds the frozen {max_bytes}-byte limit: {path}",
                )
            raw = handle.read(max_bytes + 1)
    except LaunchLineageError:
        raise
    except (MemoryError, OSError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"{label} is unavailable within its frozen byte limit: {path}: {exc}",
        ) from exc
    if len(raw) > max_bytes:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"{label} exceeds the frozen {max_bytes}-byte limit: {path}",
        )
    cache[path] = raw
    return raw


def _attested_launch_artifact_references(
    pack_root: Path,
    custody_pack_root: Path,
    arm_receipt: Mapping[str, Any],
    *,
    launch_binding_cache: dict[Path, bytes],
) -> dict[str, dict[str, str]]:
    """Resolve the digest-bound T-0 LAUNCH_RECIPE input identities."""

    try:
        candidates: list[Mapping[str, Any]] = []
        for item in arm_receipt["evidence"]:
            if (
                item.get("namespace") != "WINDOW_CUSTODY"
                or item.get("receipt_kind") != "LAUNCH_RECIPE"
            ):
                continue
            evidence = _authenticate_generic_evidence_item(
                item,
                pack_root,
                custody_pack_root,
                expected_pack_sha256=arm_receipt["pack"]["pack_sha256"],
                expected_head_commit=arm_receipt["reviewed_main"]["head_commit"],
                expected_boot_session_id=arm_receipt["boot_session_id"],
                launch_binding_cache=launch_binding_cache,
            )
            if _predicate_passes(
                evidence, "t0.single_launch_capability.v1"
            ):
                candidates.append(evidence)
        if len(candidates) != 1:
            raise ValueError("arm must bind exactly one launch-recipe receipt")
        facts = candidates[0]["facts"]
        if (
            not facts
            or facts[0]["fact_id"] != "t0.single_launch_capability.v1"
            or facts[0]["source_kind"] != "PROBE"
        ):
            raise ValueError("launch-recipe receipt must bind its T-0 source")
        fact = facts[0]
        source_path = _resolve_namespace_path(
            custody_pack_root,
            fact["source_path"],
            "launch-recipe T-0 source_path",
        )
        source_raw = launch_binding_cache[source_path]
        if sha256_bytes(source_raw) != fact["source_sha256"]:
            raise ValueError("launch-recipe T-0 source digest changed")
        source = parse_json_bytes(source_raw, require_canonical=True)
        if (
            not isinstance(source, Mapping)
            or set(source) != _T0_LAUNCH_SOURCE_KEYS
            or source["schema_version"] != _T0_EVIDENCE_SOURCE_SCHEMA
            or source["row_id"] != "t0.single_launch_capability"
            or source["kind"] != "LAUNCH_RECIPE"
            or source["head_commit"]
            != arm_receipt["reviewed_main"]["head_commit"]
            or source["head_tree_oid"]
            != arm_receipt["reviewed_main"]["head_tree_oid"]
            or source["pack_sha256"] != arm_receipt["pack"]["pack_sha256"]
            or source["boot_session_id"] != arm_receipt["boot_session_id"]
            or not isinstance(source["input_artifacts"], list)
        ):
            raise ValueError("launch-recipe T-0 source identity is invalid")
        artifacts: list[dict[str, str]] = []
        for raw_artifact in source["input_artifacts"]:
            if (
                not isinstance(raw_artifact, Mapping)
                or set(raw_artifact) != LAUNCH_ARTIFACT_REFERENCE_KEYS
                or not isinstance(raw_artifact["path"], str)
                or not Path(raw_artifact["path"]).is_absolute()
            ):
                raise ValueError("launch-recipe input artifact is invalid")
            artifacts.append(
                {
                    "path": raw_artifact["path"],
                    "sha256": _require_lower_sha256(
                        raw_artifact["sha256"],
                        "launch-recipe input artifact.sha256",
                    ),
                }
            )
        canonical_manifest = (
            custody_pack_root / _T0_INPUT_DIRECTORY / "launch-manifest.json"
        ).resolve(strict=False)
        selections = {
            "launch_manifest": [
                item
                for item in artifacts
                if Path(item["path"]).resolve(strict=False) == canonical_manifest
            ],
            "window_environment": [
                item for item in artifacts if Path(item["path"]).name == "window.env"
            ],
            "window_chain": [
                item
                for item in artifacts
                if Path(item["path"]).name == "window-chain.zsh"
            ],
        }
        if any(len(items) != 1 for items in selections.values()):
            raise ValueError("launch-recipe artifact identities are ambiguous")
        return {name: dict(items[0]) for name, items in selections.items()}
    except LaunchLineageError:
        raise
    except (
        ArmReadinessError,
        KeyError,
        MemoryError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"arm-attested launch recipe is unavailable or invalid: {exc}",
        ) from exc


def _reconcile_launch_binding(
    *,
    pack_root: Path,
    custody_pack_root: Path,
    window_custody_root: Path,
    arm_receipt: Mapping[str, Any],
    manifest: Mapping[str, Any],
    manifest_reference: Mapping[str, Any],
    launch_manifest_sha256: str,
    window_plan_root: Path,
    window_environment_reference: Mapping[str, Any],
    window_environment_sha256: str,
    window_chain_reference: Mapping[str, Any],
    window_chain_sha256: str,
    exec_argv: Sequence[str],
    launch_binding_cache: dict[Path, bytes],
) -> None:
    """Bind supplied launch inputs to the arm-attested T-0 identities."""

    attested = _attested_launch_artifact_references(
        pack_root,
        custody_pack_root,
        arm_receipt,
        launch_binding_cache=launch_binding_cache,
    )
    try:
        canonical_manifest = (
            custody_pack_root / _T0_INPUT_DIRECTORY / "launch-manifest.json"
        ).resolve(strict=True)
        manifest_path = Path(str(manifest_reference["path"])).resolve(strict=True)
        attested_manifest_path = Path(
            attested["launch_manifest"]["path"]
        ).resolve(strict=True)
        custody_root = window_custody_root.resolve(strict=True)
        supplied_window_root = window_plan_root.resolve(strict=True)
        manifest_window_root = Path(
            str(manifest["window_plan_root"])
        ).resolve(strict=True)
        manifest_window_root.relative_to(custody_root)
        environment_path = Path(
            str(window_environment_reference["path"])
        ).resolve(strict=True)
        attested_environment_path = Path(
            attested["window_environment"]["path"]
        ).resolve(strict=True)
        chain_path = Path(str(window_chain_reference["path"])).resolve(
            strict=True
        )
        attested_chain_path = Path(attested["window_chain"]["path"]).resolve(
            strict=True
        )
        manifest_argv = list(manifest["launch_command"])
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"launch binding paths are unavailable or outside custody: {exc}",
        ) from exc
    if (
        manifest_path != canonical_manifest
        or manifest_path != attested_manifest_path
        or launch_manifest_sha256 != manifest_reference["sha256"]
        or launch_manifest_sha256 != attested["launch_manifest"]["sha256"]
        or environment_path != manifest_window_root / "window.env"
        or environment_path != attested_environment_path
        or window_environment_sha256 != window_environment_reference["sha256"]
        or window_environment_sha256
        != attested["window_environment"]["sha256"]
        or chain_path != manifest_window_root / "window-chain.zsh"
        or chain_path != attested_chain_path
        or window_chain_sha256 != window_chain_reference["sha256"]
        or window_chain_sha256 != attested["window_chain"]["sha256"]
        or manifest["boot_session_id"] != arm_receipt["boot_session_id"]
        or supplied_window_root != manifest_window_root
        or list(exec_argv) != manifest_argv
        or not _launch_argv_matches(
            list(exec_argv),
            chain_path=chain_path,
            window_root=manifest_window_root,
        )
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "launch inputs differ from the arm-attested T-0 recipe",
        )


def _replay_consumed_arm(
    expected_pack_root: Path | None,
    consumption: Mapping[str, Any],
    consumption_path: Path,
    *,
    require_current_boot: bool,
    require_unexpired: bool,
    replay_arm_semantics: bool,
    launch_binding_cache: dict[Path, bytes] | None = None,
) -> tuple[Mapping[str, Any], Path, Path, Mapping[str, Any]]:
    arm_reference = consumption["arm_receipt"]
    arm_path = consumption_path.parent.parent / str(arm_reference["path"])
    try:
        arm, _arm_raw, arm_digest = _read_arm_with_sidecar(arm_path)
    except (ArmReadinessError, OSError) as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"consumption predecessor is invalid: {exc}"
        ) from exc
    if (
        arm_digest != arm_reference["sha256"]
        or arm["receipt_id"] != arm_reference["receipt_id"]
        or arm["receipt_kind"] != "arm"
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid", "consumption predecessor reference disagrees"
        )
    try:
        recorded_pack_root = Path(str(arm["pack"]["pack_root"])).resolve(
            strict=True
        )
        if (
            expected_pack_root is not None
            and recorded_pack_root
            != Path(expected_pack_root).resolve(strict=True)
        ):
            raise LaunchLineageError(
                "launch_binding_mismatch",
                "consumed arm pack root differs from the caller-expected root",
            )
        authenticated_pack = _pack_record(recorded_pack_root)
    except LaunchLineageError:
        raise
    except (ArmReadinessError, OSError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"consumed arm pack root cannot be authenticated: {exc}",
        ) from exc
    if dict(authenticated_pack) != dict(arm["pack"]):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "consumed arm pack record differs from authenticated pack bytes",
        )
    if consumption_path.parent.parent.name != recorded_pack_root.name:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "consumption/arm namespace does not belong to the authenticated pack",
        )
    if require_current_boot:
        try:
            current_boot = _current_boot_session_id()
        except ArmReadinessError as exc:
            raise LaunchLineageError("launch_binding_mismatch", str(exc)) from exc
        if arm["boot_session_id"] != current_boot:
            raise LaunchLineageError(
                "launch_binding_mismatch", "consumed arm belongs to another boot"
            )
        if require_unexpired and time.monotonic_ns() > arm["valid_until_monotonic_ns"]:
            raise LaunchLineageError(
                "launch_binding_mismatch", "consumed arm expired before launch entry"
            )
    try:
        scanned = scan_receipt_namespace(arm_path.parent, "arm")
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"arm namespace is invalid: {exc}"
        ) from exc
    target = next(
        (item for item in scanned if item["path"].resolve() == arm_path.resolve()),
        None,
    )
    superseded = any(
        item["number"] > target["number"]
        and item["receipt"]["supersedes"]
        == {
            "receipt_id": arm["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{arm_path.name}",
            "receipt_sha256": arm_digest,
            "pack_id": arm["pack"]["pack_id"],
            "pack_sha256": arm["pack"]["pack_sha256"],
        }
        for item in scanned
    ) if target is not None else False
    if target is None or (replay_arm_semantics and superseded):
        raise LaunchLineageError(
            "launch_binding_mismatch", "consumed arm is absent or superseded"
        )
    if replay_arm_semantics:
        try:
            rows, refusals = _derive_arm_semantics_for_verification(
                recorded_pack_root,
                consumption_path.parent.parent,
                arm,
                launch_binding_cache=launch_binding_cache,
            )
        except ArmReadinessError as exc:
            raise LaunchLineageError("launch_binding_mismatch", str(exc)) from exc
        if (
            arm["rows"] != rows
            or arm["refusals"] != refusals
            or refusals
            or arm["status"] != "PASS"
            or arm["arm_disposition"] != "GO"
        ):
            raise LaunchLineageError(
                "launch_binding_mismatch", "consumed arm no longer replays to PASS/GO"
            )
    return arm, arm_path, recorded_pack_root, authenticated_pack


def verify_consumed_launch(
    pack_root: Path | str,
    consumption_receipt: Path | str,
    *,
    launch_manifest: Path | str | None = None,
    expected_exec_argv: Sequence[str] | None = None,
    require_current_boot: bool = True,
) -> dict[str, Any]:
    """Replay a v2 consumption without treating its arm as unconsumed."""

    launch_binding_cache: dict[Path, bytes] = {}
    try:
        root = Path(pack_root).resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch", f"pack root is unavailable: {exc}"
        ) from exc
    consumption, _raw, digest, path = _read_v2_consumption(consumption_receipt)
    arm, _arm_path, _recorded_pack_root, pack = _replay_consumed_arm(
        root,
        consumption,
        path,
        require_current_boot=require_current_boot,
        require_unexpired=require_current_boot,
        replay_arm_semantics=require_current_boot,
        launch_binding_cache=launch_binding_cache,
    )
    expected_identity = {
        "pack_id": pack["pack_id"],
        "pack_sha256": pack["pack_sha256"],
        "plan_id": pack["plan_id"],
        "window_id": pack["window_id"],
        "boot_session_id": arm["boot_session_id"],
        "head_commit": arm["reviewed_main"]["head_commit"],
        "arm_context_sha256": sha256_bytes(render_json(arm["arm_context"])),
    }
    if any(consumption[name] != value for name, value in expected_identity.items()):
        raise LaunchLineageError(
            "launch_binding_mismatch", "consumption identity differs from its arm/pack"
        )
    if consumption["consumed_at_monotonic_ns"] > arm["valid_until_monotonic_ns"]:
        raise LaunchLineageError(
            "launch_binding_mismatch", "consumption was recorded after arm expiry"
        )
    manifest_path, manifest_raw = _read_exact_launch_reference(
        consumption["launch_manifest"],
        max_bytes=_LAUNCH_BINDING_MANIFEST_MAX_BYTES,
        label="launch manifest",
        expected_path=Path(launch_manifest) if launch_manifest is not None else None,
        launch_binding_cache=launch_binding_cache,
    )
    try:
        manifest = validate_launch_manifest(
            parse_json_bytes(manifest_raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"launch manifest is invalid: {exc}"
        ) from exc
    try:
        window_root = Path(str(manifest["window_plan_root"])).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"launch manifest window root is unavailable: {exc}",
        ) from exc
    _read_exact_launch_reference(
        consumption["window_environment"],
        max_bytes=_LAUNCH_BINDING_ENVIRONMENT_MAX_BYTES,
        label="window environment",
        expected_path=window_root / "window.env",
        launch_binding_cache=launch_binding_cache,
    )
    _read_exact_launch_reference(
        consumption["window_chain"],
        max_bytes=_LAUNCH_BINDING_CHAIN_MAX_BYTES,
        label="window chain",
        expected_path=window_root / "window-chain.zsh",
        launch_binding_cache=launch_binding_cache,
    )
    manifest_argv = list(manifest["launch_command"])
    _reconcile_launch_binding(
        pack_root=root,
        custody_pack_root=path.parent.parent,
        window_custody_root=path.parent.parent.parent,
        arm_receipt=arm,
        manifest=manifest,
        manifest_reference=consumption["launch_manifest"],
        launch_manifest_sha256=consumption["launch_manifest"]["sha256"],
        window_plan_root=window_root,
        window_environment_reference=consumption["window_environment"],
        window_environment_sha256=consumption["window_environment"]["sha256"],
        window_chain_reference=consumption["window_chain"],
        window_chain_sha256=consumption["window_chain"]["sha256"],
        exec_argv=consumption["exec_argv"],
        launch_binding_cache=launch_binding_cache,
    )
    if expected_exec_argv is not None and list(expected_exec_argv) != manifest_argv:
        raise LaunchLineageError(
            "launch_binding_mismatch", "exact frozen foreground argv disagrees"
        )
    return {
        "status": "PASS",
        "consumption_path": str(path),
        "consumption_sha256": digest,
        "consumption_id": consumption["consumption_id"],
        "boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "pack_sha256": consumption["pack_sha256"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
        "window_chain": copy.deepcopy(dict(consumption["window_chain"])),
        "exec_argv": manifest_argv,
        "handoff_token_sha256": consumption["handoff_token_sha256"],
    }


def _consume_launch_capability(
    *,
    pack_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    arm_receipt: Path | str = _MISSING_LAUNCH_CONTEXT,
    authenticated_arm_receipt: Mapping[str, Any] = _MISSING_LAUNCH_CONTEXT,
    arm_receipt_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_custody_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    launch_manifest: Path | str = _MISSING_LAUNCH_CONTEXT,
    authenticated_launch_manifest: Mapping[str, Any] = _MISSING_LAUNCH_CONTEXT,
    launch_manifest_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_plan_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    window_environment_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_chain_sha256: str = _MISSING_LAUNCH_CONTEXT,
    exec_argv: Sequence[str] = _MISSING_LAUNCH_CONTEXT,
    handoff_token_sha256: str = _MISSING_LAUNCH_CONTEXT,
) -> dict[str, Any]:
    """Reauthenticate complete launch inputs, then atomically claim one GO."""

    if any(
        value is _MISSING_LAUNCH_CONTEXT
        for value in (
            pack_root,
            arm_receipt,
            authenticated_arm_receipt,
            arm_receipt_sha256,
            window_custody_root,
            launch_manifest,
            authenticated_launch_manifest,
            launch_manifest_sha256,
            window_plan_root,
            window_environment_sha256,
            window_chain_sha256,
            exec_argv,
            handoff_token_sha256,
        )
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "complete authenticated launch context is required",
        )
    if not isinstance(authenticated_arm_receipt, Mapping):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated arm receipt context is required",
        )
    if not isinstance(authenticated_launch_manifest, Mapping):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated launch-manifest context is required",
        )
    for value, where in (
        (pack_root, "pack_root"),
        (arm_receipt, "arm_receipt"),
        (window_custody_root, "window_custody_root"),
        (launch_manifest, "launch_manifest"),
        (window_plan_root, "window_plan_root"),
    ):
        if not isinstance(value, (str, os.PathLike)):
            raise ArmReadinessError(
                "readiness_usage_invalid", f"{where} is required"
            )
    if isinstance(exec_argv, (str, bytes)) or not isinstance(exec_argv, Sequence):
        raise ArmReadinessError(
            "readiness_usage_invalid", "exact exec argv is required"
        )
    for value, where in (
        (arm_receipt_sha256, "arm_receipt_sha256"),
        (launch_manifest_sha256, "launch_manifest_sha256"),
        (window_environment_sha256, "window_environment_sha256"),
        (window_chain_sha256, "window_chain_sha256"),
        (handoff_token_sha256, "handoff_token_sha256"),
    ):
        _require_lower_sha256(value, where)

    launch_binding_cache: dict[Path, bytes] = {}
    verified = _verify_arm_receipt(
        pack_root,
        arm_receipt,
        require_unconsumed=False,
        launch_binding_cache=launch_binding_cache,
    )
    root = Path(pack_root).resolve(strict=True)
    receipt_path = Path(arm_receipt).resolve(strict=True)
    receipt, _raw, digest = _read_arm_with_sidecar(receipt_path)
    if (
        dict(authenticated_arm_receipt) != dict(receipt)
        or arm_receipt_sha256 != digest
        or dict(verified)
        != {
            "status": "PASS",
            "arm_disposition": "GO",
            "receipt_path": str(receipt_path),
            "receipt_sha256": arm_receipt_sha256,
            "pack_sha256": receipt["pack"]["pack_sha256"],
        }
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated arm receipt context changed before consumption",
        )
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
    consumption_name = f"{receipt['receipt_id']}.consumed.json"
    relative_arm_path = f"arm_readiness.receipts/{receipt_path.name}"
    volatile_checks = sorted(
        [
            "arm_receipt_unsuperseded",
            "campaign_lock_absent",
            "pack_digest_unchanged",
            "roots_and_backups_rechecked",
            "same_head",
        ]
    )
    manifest, manifest_ref, env_ref, chain_ref = (
        _load_launch_manifest_for_consumption(
            Path(launch_manifest),
            launch_binding_cache=launch_binding_cache,
        )
    )
    try:
        authenticated_manifest = validate_launch_manifest(
            authenticated_launch_manifest
        )
    except (OSError, RuntimeError) as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"assembled launch root is unavailable: {exc}",
        ) from exc
    if dict(authenticated_manifest) != dict(manifest):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "assembled launch context changed before consumption",
        )
    _reconcile_launch_binding(
        pack_root=root,
        custody_pack_root=custody_pack_root,
        window_custody_root=Path(window_custody_root),
        arm_receipt=receipt,
        manifest=manifest,
        manifest_reference=manifest_ref,
        launch_manifest_sha256=launch_manifest_sha256,
        window_plan_root=Path(window_plan_root),
        window_environment_reference=env_ref,
        window_environment_sha256=window_environment_sha256,
        window_chain_reference=chain_ref,
        window_chain_sha256=window_chain_sha256,
        exec_argv=exec_argv,
        launch_binding_cache=launch_binding_cache,
    )
    pack = receipt["pack"]
    consumption = {
        "schema_version": CONSUMPTION_RECEIPT_SCHEMA,
        "receipt_kind": "launch_consumption",
        "consumption_id": f"{receipt['receipt_id']}-launch",
        "consumed_at_utc": _utc_now(),
        "consumed_at_monotonic_ns": time.monotonic_ns(),
        "boot_session_id": receipt["boot_session_id"],
        "pack_id": pack["pack_id"],
        "pack_sha256": verified["pack_sha256"],
        "plan_id": pack["plan_id"],
        "window_id": pack["window_id"],
        "arm_receipt": {
            "receipt_id": receipt["receipt_id"],
            "path": relative_arm_path,
            "sha256": digest,
        },
        "head_commit": reviewed["head_commit"],
        "arm_context_sha256": sha256_bytes(render_json(context)),
        "launch_manifest": manifest_ref,
        "window_environment": env_ref,
        "window_chain": chain_ref,
        "exec_argv": list(exec_argv),
        "handoff_token_sha256": handoff_token_sha256,
        "volatile_checks": volatile_checks,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_consumption_receipt(consumption)
    raw = render_json(consumption)
    consumption_dir = custody_pack_root / "arm_readiness.consumptions"
    consumption_dir.mkdir(parents=True, exist_ok=True)
    _fsync_directory(custody_pack_root)
    consumption_path = consumption_dir / consumption_name
    # Python caller identity is not authenticated here.  This atomic
    # no-clobber primary is the only real enforcement and the single-use
    # linearization point; every later complete caller must lose this write.
    try:
        _exclusive_write(consumption_path, raw)
    except ArmReadinessError as exc:
        if exc.reason_code == "readiness_output_collision":
            raise ArmReadinessError(
                "readiness_record_consumed", "launch capability was already consumed"
            ) from exc
        raise
    _fsync_directory(consumption_dir)
    digest_out = sha256_bytes(raw)
    _exclusive_write(
        consumption_dir / f"{consumption_name}.sha256",
        gnu_sidecar(digest_out, consumption_name),
    )
    _fsync_directory(consumption_dir)
    return {
        "status": "CONSUMED",
        "arm_disposition": "NOT_APPLICABLE",
        "consumption_path": str(consumption_path),
        "consumption_sha256": digest_out,
    }


def _lifecycle_receipt_path(consumption_path: Path, event: str) -> Path:
    consumption, _raw, _digest, resolved = _read_v2_consumption(consumption_path)
    return (
        resolved.parent.parent
        / "arm_readiness.launch_lifecycle"
        / f"{consumption['consumption_id']}.{event}.json"
    )


def _reference_for_existing_receipt(path: Path, digest: str) -> dict[str, str]:
    return {"path": str(path.resolve(strict=True)), "sha256": digest}


def _read_lifecycle_receipt(
    path: Path, *, expected_kind: str
) -> tuple[Mapping[str, Any], str, Path]:
    value, _raw, digest = _read_launch_lineage_primary(
        path, missing_code="launch_lifecycle_incomplete"
    )
    try:
        receipt = validate_launch_lifecycle_receipt(value)
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"invalid lifecycle receipt: {exc}"
        ) from exc
    if receipt["receipt_kind"] != expected_kind:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"expected {expected_kind}, found {receipt['receipt_kind']}",
        )
    return receipt, digest, path.resolve(strict=True)


def _launch_lineage_for_event(
    consumption: Mapping[str, Any],
    consumption_path: Path,
    consumption_digest: str,
    arm: Mapping[str, Any],
    event: str,
    event_path: Path,
    event_digest: str,
) -> dict[str, Any]:
    start_path = _lifecycle_receipt_path(consumption_path, "start")
    start_reference = (
        _reference_for_existing_receipt(event_path, event_digest)
        if event == "start"
        else _reference_for_existing_receipt(
            start_path,
            _read_lifecycle_receipt(
                start_path, expected_kind="launch_start"
            )[1],
        )
    )
    settle_reference: dict[str, str] | None = None
    if event == "settle":
        settle_reference = _reference_for_existing_receipt(
            event_path, event_digest
        )
    elif event == "completion":
        settle_path = _lifecycle_receipt_path(consumption_path, "settle")
        settle_reference = _reference_for_existing_receipt(
            settle_path,
            _read_lifecycle_receipt(
                settle_path, expected_kind="launch_settle"
            )[1],
        )
    return {
        "schema_version": LAUNCH_LINEAGE_SCHEMA,
        "collection_boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
        "consumption": _reference_for_existing_receipt(
            consumption_path, consumption_digest
        ),
        "start": start_reference,
        "settle": settle_reference,
        "completion": (
            _reference_for_existing_receipt(event_path, event_digest)
            if event == "completion"
            else None
        ),
    }


def _publish_launch_lineage_locator(
    root: Path,
    *,
    root_role: str,
    launch_lineage: Mapping[str, Any],
) -> Path:
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"authenticated {root_role} is unavailable: {exc}",
        ) from exc
    if not resolved_root.is_dir():
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"authenticated {root_role} is not a directory",
        )
    locator = {
        "schema_version": LAUNCH_LINEAGE_LOCATOR_SCHEMA,
        "root_role": root_role,
        "root_path": str(resolved_root),
        "launch_lineage": copy.deepcopy(dict(launch_lineage)),
    }
    raw = render_json(locator)
    path = resolved_root / LAUNCH_LINEAGE_LOCATOR_BASENAME
    try:
        _exclusive_write(path, raw)
        _fsync_directory(resolved_root)
        digest = sha256_bytes(raw)
        _exclusive_write(
            path.with_name(f"{path.name}.sha256"),
            gnu_sidecar(digest, path.name),
        )
        _fsync_directory(resolved_root)
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            f"launch-lineage locator publication failed and burned the attempt: {exc}",
        ) from exc
    return path


def record_launch_lifecycle_event(
    pack_root: Path | str,
    consumption_receipt: Path | str,
    event: str,
    *,
    handoff_token: bytes | None = None,
) -> dict[str, Any]:
    """Append one start/settle/completion receipt with no-clobber custody."""

    if event not in {"start", "settle", "completion"}:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"unknown launch lifecycle event {event!r}"
        )
    consumption, _raw, consumption_digest, consumption_path = (
        _read_v2_consumption(consumption_receipt)
    )
    arm, _arm_path, _recorded_pack_root, _pack = _replay_consumed_arm(
        Path(pack_root),
        consumption,
        consumption_path,
        require_current_boot=False,
        require_unexpired=False,
        replay_arm_semantics=False,
    )
    try:
        current_boot = _current_boot_session_id()
    except ArmReadinessError as exc:
        raise LaunchLineageError("launch_binding_mismatch", str(exc)) from exc
    if current_boot != consumption["boot_session_id"]:
        raise LaunchLineageError(
            "launch_binding_mismatch", "launch lifecycle crossed a boot boundary"
        )
    if event == "start":
        if handoff_token is None or sha256_bytes(handoff_token) != consumption[
            "handoff_token_sha256"
        ]:
            raise LaunchLineageError(
                "launch_handoff_invalid", "inherited one-use handoff token is absent or invalid"
            )
        predecessor = _reference_for_existing_receipt(
            consumption_path, consumption_digest
        )
        predecessor_monotonic_ns = consumption["consumed_at_monotonic_ns"]
        handoff_digest: str | None = consumption["handoff_token_sha256"]
        schema = LAUNCH_START_RECEIPT_SCHEMA
        kind = "launch_start"
    else:
        predecessor_event = "start" if event == "settle" else "settle"
        predecessor_kind = f"launch_{predecessor_event}"
        predecessor_path = _lifecycle_receipt_path(
            consumption_path, predecessor_event
        )
        predecessor_receipt, predecessor_digest, predecessor_path = (
            _read_lifecycle_receipt(
                predecessor_path, expected_kind=predecessor_kind
            )
        )
        predecessor = _reference_for_existing_receipt(
            predecessor_path, predecessor_digest
        )
        predecessor_monotonic_ns = predecessor_receipt[
            "issued_at_monotonic_ns"
        ]
        handoff_digest = None
        schema = (
            LAUNCH_SETTLE_RECEIPT_SCHEMA
            if event == "settle"
            else LAUNCH_COMPLETION_RECEIPT_SCHEMA
        )
        kind = f"launch_{event}"
    issued_monotonic_ns = time.monotonic_ns()
    if issued_monotonic_ns < predecessor_monotonic_ns:
        raise LaunchLineageError(
            "launch_binding_mismatch", "launch lifecycle monotonic order reversed"
        )
    receipt = {
        "schema_version": schema,
        "receipt_kind": kind,
        "receipt_id": f"{consumption['consumption_id']}-{event}",
        "issued_at_utc": _utc_now(),
        "issued_at_monotonic_ns": issued_monotonic_ns,
        "boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "pack_sha256": consumption["pack_sha256"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
        "window_chain": copy.deepcopy(dict(consumption["window_chain"])),
        "consumption": _reference_for_existing_receipt(
            consumption_path, consumption_digest
        ),
        "predecessor": predecessor,
        "handoff_token_sha256": handoff_digest,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_launch_lifecycle_receipt(receipt)
    path = _lifecycle_receipt_path(consumption_path, event)
    path.parent.mkdir(parents=True, exist_ok=True)
    _fsync_directory(path.parent.parent)
    raw = render_json(receipt)
    try:
        _exclusive_write(path, raw)
    except ArmReadinessError as exc:
        if event == "start" and exc.reason_code == "readiness_output_collision":
            raise LaunchLineageError(
                "launch_handoff_invalid", "launch handoff was already consumed"
            ) from exc
        raise LaunchLineageError(
            "launch_consumption_invalid", f"cannot record launch lifecycle: {exc}"
        ) from exc
    _fsync_directory(path.parent)
    digest = sha256_bytes(raw)
    try:
        _exclusive_write(
            path.with_name(f"{path.name}.sha256"),
            gnu_sidecar(digest, path.name),
        )
        _fsync_directory(path.parent)
    except ArmReadinessError as exc:
        # The primary is the durable append point. A missing sidecar remains
        # an incomplete, burned lifecycle and is never repaired in place.
        raise LaunchLineageError(
            "launch_consumption_invalid", f"lifecycle sidecar publication failed: {exc}"
        ) from exc
    launch_lineage = _launch_lineage_for_event(
        consumption,
        consumption_path,
        consumption_digest,
        arm,
        event,
        path,
        digest,
    )
    if event == "settle":
        claim_root = Path(str(arm["arm_context"]["claim_runs_root"]))
        bound_root = Path(str(arm["arm_context"]["bound_runs_root"]))
        try:
            if claim_root.resolve(strict=True) == bound_root.resolve(strict=True):
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    "claim and bound runs roots must be distinct locator namespaces",
                )
        except OSError as exc:
            raise LaunchLineageError(
                "launch_binding_mismatch",
                f"authenticated runs root is unavailable: {exc}",
            ) from exc
        # Fixed order is deliberate. Any failure after either no-clobber
        # primary leaves the settle receipt durable and makes retry impossible.
        _publish_launch_lineage_locator(
            claim_root,
            root_role="claim_runs_root",
            launch_lineage=launch_lineage,
        )
        _publish_launch_lineage_locator(
            bound_root,
            root_role="bound_runs_root",
            launch_lineage=launch_lineage,
        )
    return {
        "status": "RECORDED",
        "event": event,
        "receipt_path": str(path),
        "receipt_sha256": digest,
        "launch_lineage": launch_lineage,
    }


def _validate_lineage_reference(
    value: object, name: str, *, missing_code: str
) -> Mapping[str, Any]:
    if value is None:
        raise LaunchLineageError(missing_code, f"launch lineage omits {name}")
    try:
        return _validate_launch_artifact_reference(value, f"launch lineage.{name}")
    except ArmReadinessError as exc:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"launch lineage {name} is invalid: {exc}"
        ) from exc


def authenticate_launch_lineage(
    value: object,
    *,
    require_completion: bool,
    expected_pack_root: Path | str | None = None,
    require_current_boot: bool = False,
    require_completion_absent: bool = False,
) -> dict[str, Any]:
    """Authenticate one immutable consumption→start→settle→completion chain."""

    launch_binding_cache: dict[Path, bytes] = {}
    if require_completion and require_completion_absent:
        raise ValueError(
            "completion cannot be simultaneously required and required absent"
        )

    if not isinstance(value, Mapping):
        raise LaunchLineageError(
            "launch_consumption_missing", "launch lineage metadata is absent"
        )
    if set(value) != LAUNCH_LINEAGE_KEYS or value.get("schema_version") != LAUNCH_LINEAGE_SCHEMA:
        raise LaunchLineageError(
            "launch_consumption_invalid", "launch lineage schema/keys are invalid"
        )
    for name in ("pack_id", "plan_id", "window_id", "bracket_session_id"):
        if not isinstance(value[name], str) or not value[name]:
            raise LaunchLineageError(
                "launch_consumption_invalid", f"launch lineage {name} is invalid"
            )
    try:
        _require_boot_session_id(
            value["collection_boot_session_id"],
            "launch lineage.collection_boot_session_id",
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError("launch_consumption_invalid", str(exc)) from exc
    consumption_ref = _validate_lineage_reference(
        value["consumption"], "consumption", missing_code="launch_consumption_missing"
    )
    consumption, _raw, consumption_digest, consumption_path = _read_v2_consumption(
        str(consumption_ref["path"])
    )
    if consumption_digest != consumption_ref["sha256"]:
        raise LaunchLineageError(
            "launch_consumption_invalid", "consumption digest reference disagrees"
        )
    arm, _arm_path, pack_root, pack = _replay_consumed_arm(
        Path(expected_pack_root) if expected_pack_root is not None else None,
        consumption,
        consumption_path,
        require_current_boot=require_current_boot,
        require_unexpired=False,
        replay_arm_semantics=False,
    )
    expected_identity = {
        "collection_boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
    }
    if any(value[name] != expected for name, expected in expected_identity.items()):
        raise LaunchLineageError(
            "launch_binding_mismatch", "bundle lineage differs from consumption identity"
        )
    if any(
        consumption[name] != expected
        for name, expected in (
            ("pack_id", pack["pack_id"]),
            ("pack_sha256", pack["pack_sha256"]),
            ("plan_id", pack["plan_id"]),
            ("window_id", pack["window_id"]),
            ("boot_session_id", arm["boot_session_id"]),
            ("head_commit", arm["reviewed_main"]["head_commit"]),
            (
                "arm_context_sha256",
                sha256_bytes(render_json(arm["arm_context"])),
            ),
        )
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "consumption identity differs from its authenticated arm/pack",
        )
    if consumption["consumed_at_monotonic_ns"] > arm["valid_until_monotonic_ns"]:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "consumption occurred after the arm validity horizon",
        )
    if require_current_boot:
        current_head = _git_text(pack_root, "rev-parse", "HEAD")
        if current_head != consumption["head_commit"]:
            raise LaunchLineageError(
                "launch_binding_mismatch",
                "current checkout HEAD differs from the reviewed launch HEAD",
            )
    manifest_path, manifest_raw = _read_exact_launch_reference(
        consumption["launch_manifest"],
        max_bytes=_LAUNCH_BINDING_MANIFEST_MAX_BYTES,
        label="launch manifest",
        launch_binding_cache=launch_binding_cache,
    )
    try:
        manifest = validate_launch_manifest(
            parse_json_bytes(manifest_raw, require_canonical=True)
        )
    except ArmReadinessError as exc:
        raise LaunchLineageError("launch_consumption_invalid", str(exc)) from exc
    try:
        window_root = Path(str(manifest["window_plan_root"])).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"launch manifest window root is unavailable: {exc}",
        ) from exc
    _read_exact_launch_reference(
        consumption["window_environment"],
        max_bytes=_LAUNCH_BINDING_ENVIRONMENT_MAX_BYTES,
        label="window environment",
        expected_path=window_root / "window.env",
        launch_binding_cache=launch_binding_cache,
    )
    chain_path, _chain_raw = _read_exact_launch_reference(
        consumption["window_chain"],
        max_bytes=_LAUNCH_BINDING_CHAIN_MAX_BYTES,
        label="window chain",
        expected_path=window_root / "window-chain.zsh",
        launch_binding_cache=launch_binding_cache,
    )
    manifest_argv = list(manifest["launch_command"])
    if (
        manifest_path != Path(str(consumption["launch_manifest"]["path"])).resolve(strict=True)
        or manifest["boot_session_id"] != consumption["boot_session_id"]
        or manifest_argv != consumption["exec_argv"]
        or not _launch_argv_matches(
            manifest_argv, chain_path=chain_path, window_root=window_root
        )
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch", "launch manifest no longer binds the consumed argv"
        )

    start_ref = _validate_lineage_reference(
        value["start"], "start", missing_code="launch_lifecycle_incomplete"
    )
    start, start_digest, start_path = _read_lifecycle_receipt(
        Path(str(start_ref["path"])), expected_kind="launch_start"
    )
    if start_digest != start_ref["sha256"]:
        raise LaunchLineageError(
            "launch_consumption_invalid", "start digest reference disagrees"
        )
    settle_ref = _validate_lineage_reference(
        value["settle"], "settle", missing_code="launch_lifecycle_incomplete"
    )
    settle, settle_digest, settle_path = _read_lifecycle_receipt(
        Path(str(settle_ref["path"])), expected_kind="launch_settle"
    )
    if settle_digest != settle_ref["sha256"]:
        raise LaunchLineageError(
            "launch_consumption_invalid", "settle digest reference disagrees"
        )

    lifecycle = ((start, start_path, start_digest), (settle, settle_path, settle_digest))
    for receipt, _path, _digest in lifecycle:
        if receipt["consumption"] != consumption_ref:
            raise LaunchLineageError(
                "launch_consumption_invalid",
                "lifecycle consumption predecessor differs",
            )
        if any(
            receipt[name] != expected
            for name, expected in (
                ("boot_session_id", consumption["boot_session_id"]),
                ("pack_id", consumption["pack_id"]),
                ("pack_sha256", consumption["pack_sha256"]),
                ("plan_id", consumption["plan_id"]),
                ("window_id", consumption["window_id"]),
                ("bracket_session_id", arm["arm_context"]["bracket_session_id"]),
                ("window_chain", consumption["window_chain"]),
            )
        ):
            raise LaunchLineageError(
                "launch_binding_mismatch", "lifecycle identity differs from consumption"
            )
    if (
        start["predecessor"] != consumption_ref
        or start["handoff_token_sha256"]
        != consumption["handoff_token_sha256"]
        or start["issued_at_monotonic_ns"]
        < consumption["consumed_at_monotonic_ns"]
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "start receipt predecessor/handoff/order binding differs",
        )
    if settle["predecessor"] != start_ref or settle[
        "issued_at_monotonic_ns"
    ] < start["issued_at_monotonic_ns"]:
        raise LaunchLineageError(
            "launch_consumption_invalid", "settle receipt predecessor/order differs"
        )

    completion: Mapping[str, Any] | None = None
    completion_ref = value["completion"]
    completion_path = _lifecycle_receipt_path(consumption_path, "completion")
    completion_sidecar = completion_path.with_name(
        f"{completion_path.name}.sha256"
    )
    if require_completion_absent and (
        completion_ref is not None
        or completion_path.exists()
        or completion_path.is_symlink()
        or completion_sidecar.exists()
        or completion_sidecar.is_symlink()
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "launch completion already exists before new collection",
        )
    if require_completion and completion_ref is None:
        completion, completion_digest, completion_path = _read_lifecycle_receipt(
            completion_path, expected_kind="launch_completion"
        )
        completion_ref = _reference_for_existing_receipt(
            completion_path, completion_digest
        )
    elif completion_ref is not None:
        validated_completion_ref = _validate_lineage_reference(
            completion_ref,
            "completion",
            missing_code="launch_lifecycle_incomplete",
        )
        completion, completion_digest, _completion_path = _read_lifecycle_receipt(
            Path(str(validated_completion_ref["path"])),
            expected_kind="launch_completion",
        )
        if completion_digest != validated_completion_ref["sha256"]:
            raise LaunchLineageError(
                "launch_consumption_invalid", "completion digest reference disagrees"
            )
        completion_ref = validated_completion_ref
    if require_completion and completion is None:
        raise LaunchLineageError(
            "launch_lifecycle_incomplete", "launch completion receipt is absent"
        )
    if completion is not None and (
        completion["predecessor"] != settle_ref
        or completion["consumption"] != consumption_ref
        or completion["issued_at_monotonic_ns"] < settle["issued_at_monotonic_ns"]
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "completion receipt predecessor/order differs",
        )
    if completion is not None and any(
            completion[name] != expected
            for name, expected in (
                ("boot_session_id", consumption["boot_session_id"]),
                ("pack_id", consumption["pack_id"]),
                ("pack_sha256", consumption["pack_sha256"]),
                ("plan_id", consumption["plan_id"]),
                ("window_id", consumption["window_id"]),
                ("bracket_session_id", arm["arm_context"]["bracket_session_id"]),
                ("window_chain", consumption["window_chain"]),
            )
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "completion receipt identity differs",
        )
    return {
        "schema_version": LAUNCH_LINEAGE_SCHEMA,
        "consumption_id": consumption["consumption_id"],
        "consumption_path": str(consumption_path),
        "consumption_sha256": consumption_digest,
        "boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "pack_sha256": consumption["pack_sha256"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
        "pack_root": str(pack_root),
        "arm_context": copy.deepcopy(dict(arm["arm_context"])),
        "launch_lineage": copy.deepcopy(dict(value)),
        "start_sha256": start_digest,
        "settle_sha256": settle_digest,
        "completion_sha256": (
            completion_ref["sha256"]
            if isinstance(completion_ref, Mapping)
            else None
        ),
    }


def _read_launch_lineage_locator(
    path: Path,
    *,
    expected_root: Path,
    expected_role: str | None = None,
) -> tuple[Mapping[str, Any], str]:
    if path.name != LAUNCH_LINEAGE_LOCATOR_BASENAME:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "launch-lineage locator does not use the fixed basename",
        )
    value, _raw, digest = _read_launch_lineage_primary(
        path, missing_code="launch_consumption_missing"
    )
    if (
        set(value) != LAUNCH_LINEAGE_LOCATOR_KEYS
        or value.get("schema_version") != LAUNCH_LINEAGE_LOCATOR_SCHEMA
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "launch-lineage locator schema/keys are invalid",
        )
    role = value.get("root_role")
    if role not in LAUNCH_LINEAGE_ROOT_ROLES:
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "launch-lineage locator root_role is invalid",
        )
    root_path = value.get("root_path")
    if not isinstance(root_path, str) or not Path(root_path).is_absolute():
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "launch-lineage locator root_path is invalid",
        )
    try:
        resolved_expected = expected_root.resolve(strict=True)
        resolved_recorded = Path(root_path).resolve(strict=True)
        resolved_locator_parent = path.parent.resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"launch-lineage locator root is unavailable: {exc}",
        ) from exc
    if (
        root_path != str(resolved_expected)
        or resolved_recorded != resolved_expected
        or resolved_locator_parent != resolved_expected
        or (expected_role is not None and role != expected_role)
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "launch-lineage locator root role/path differs from the selected root",
        )
    if not isinstance(value.get("launch_lineage"), Mapping):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "launch-lineage locator payload is not an object",
        )
    return value, digest


def _authenticated_pack_config_inventory(
    pack_root: Path,
) -> dict[str, str]:
    try:
        tree, _raw = _plan_tree(pack_root)
        attachments = tree["arm_attachments"]
        projection = attachments["identity_pin_projection"]
        units = projection["identity_units"]
    except (ArmReadinessError, KeyError, TypeError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"authenticated pack omits its config inventory: {exc}",
        ) from exc
    if not isinstance(units, list) or not units:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "authenticated pack config inventory is empty or invalid",
        )
    inventory: dict[str, str] = {}
    for unit in units:
        rows = unit.get("config_inventory") if isinstance(unit, Mapping) else None
        if not isinstance(rows, list) or not rows:
            raise LaunchLineageError(
                "launch_binding_mismatch",
                "authenticated pack config inventory unit is invalid",
            )
        for row in rows:
            if not isinstance(row, Mapping) or set(row) != {"path", "sha256"}:
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    "authenticated pack config inventory row is invalid",
                )
            relative = row.get("path")
            digest = row.get("sha256")
            try:
                _require_relative_path(relative, "config inventory.path")
                _require_lower_sha256(digest, "config inventory.sha256")
            except ArmReadinessError as exc:
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    f"authenticated pack config inventory row is invalid: {exc}",
                ) from exc
            assert isinstance(relative, str) and isinstance(digest, str)
            prior = inventory.get(relative)
            if prior is not None and prior != digest:
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    "authenticated pack config inventory has conflicting duplicates",
                )
            inventory[relative] = digest
    return inventory


def authenticate_campaign_launch_lineage(
    runs_root: Path | str,
    *,
    config_paths: Sequence[Path | str] = (),
) -> dict[str, Any]:
    """Derive and authenticate the campaign writer's fixed root-local locator."""

    try:
        selected_root = Path(runs_root).resolve(strict=True)
    except OSError as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch", f"campaign runs root is unavailable: {exc}"
        ) from exc
    if not selected_root.is_dir():
        raise LaunchLineageError(
            "launch_binding_mismatch", "campaign runs root is not a directory"
        )
    locator_path = selected_root / LAUNCH_LINEAGE_LOCATOR_BASENAME
    locator, locator_digest = _read_launch_lineage_locator(
        locator_path, expected_root=selected_root
    )
    authenticated = authenticate_launch_lineage(
        locator["launch_lineage"],
        require_completion=False,
        require_current_boot=True,
        require_completion_absent=True,
    )
    context = authenticated["arm_context"]
    resolved_roots: dict[str, Path] = {}
    try:
        for role in sorted(LAUNCH_LINEAGE_ROOT_ROLES):
            resolved_roots[role] = Path(str(context[role])).resolve(strict=True)
    except (KeyError, OSError) as exc:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            f"authenticated arm runs root is unavailable: {exc}",
        ) from exc
    matching_roles = [
        role for role, root in resolved_roots.items() if root == selected_root
    ]
    if len(matching_roles) != 1:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "campaign runs root is not exactly one authenticated arm-context root",
        )
    selected_role = matching_roles[0]
    if locator["root_role"] != selected_role:
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "campaign locator role differs from its authenticated arm-context root",
        )
    lineage = locator["launch_lineage"]
    for role, root in resolved_roots.items():
        sibling, _sibling_digest = _read_launch_lineage_locator(
            root / LAUNCH_LINEAGE_LOCATOR_BASENAME,
            expected_root=root,
            expected_role=role,
        )
        if sibling["launch_lineage"] != lineage:
            raise LaunchLineageError(
                "launch_lineage_conflict",
                "claim and bound roots carry different authenticated launch lineages",
            )
    pack_root = Path(str(authenticated["pack_root"]))
    inventory = _authenticated_pack_config_inventory(pack_root)
    for config_path in config_paths:
        candidate = Path(config_path)
        try:
            if candidate.is_symlink():
                raise OSError("symlink refused")
            resolved = candidate.resolve(strict=True)
            relative = resolved.relative_to(pack_root).as_posix()
            raw = resolved.read_bytes()
        except (OSError, ValueError) as exc:
            raise LaunchLineageError(
                "launch_binding_mismatch",
                f"campaign config is outside the authenticated pack: {candidate}: {exc}",
            ) from exc
        if inventory.get(relative) != sha256_bytes(raw):
            raise LaunchLineageError(
                "launch_binding_mismatch",
                f"campaign config is not an authenticated pack member: {relative}",
            )
    return {
        "launch_lineage": copy.deepcopy(dict(lineage)),
        "pack_root": str(pack_root),
        "root_role": selected_role,
        "root_path": str(selected_root),
        "locator_sha256": locator_digest,
        "config_inventory": copy.deepcopy(inventory),
        "authentication": {
            key: copy.deepcopy(value)
            for key, value in authenticated.items()
            if key not in {"arm_context", "launch_lineage"}
        },
    }


def launch_lineage_required(config: object) -> bool:
    """Return the frozen successor-pack marker from run-metadata tags."""

    if not isinstance(config, Mapping):
        return False
    metadata = config.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    return isinstance(tags, list) and "launch_lineage_required" in tags


def authenticate_bundle_launch_lineage(
    bundle_path: Path | str,
    *,
    config: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    require_completion: bool,
) -> dict[str, Any] | None:
    """Gate marker-bearing bundle metadata with direct receipt authentication."""

    path = Path(bundle_path)
    if config is None:
        try:
            parsed = parse_json_bytes(
                (path / "config.json").read_bytes(), require_canonical=False
            )
            config = parsed if isinstance(parsed, Mapping) else None
        except (OSError, ArmReadinessError):
            config = None
    if not launch_lineage_required(config):
        return None
    if metadata is None:
        try:
            parsed = parse_json_bytes(
                (path / "metadata.json").read_bytes(), require_canonical=False
            )
            metadata = parsed if isinstance(parsed, Mapping) else None
        except (OSError, ArmReadinessError):
            metadata = None
    extra = metadata.get("extra") if isinstance(metadata, Mapping) else None
    lineage = extra.get("launch_lineage") if isinstance(extra, Mapping) else None
    if not isinstance(lineage, Mapping):
        raise LaunchLineageError(
            "launch_consumption_missing",
            "bundle launch-lineage stamp is absent",
        )
    locator_digest = (
        extra.get("launch_lineage_locator_sha256")
        if isinstance(extra, Mapping)
        else None
    )
    if not isinstance(locator_digest, str) or not _LOWER_SHA256_RE.fullmatch(
        locator_digest
    ):
        raise LaunchLineageError(
            "launch_consumption_invalid",
            "bundle launch-lineage locator digest is absent or invalid",
        )
    locator_path = path.parent / LAUNCH_LINEAGE_LOCATOR_BASENAME
    locator, authenticated_locator_digest = _read_launch_lineage_locator(
        locator_path,
        expected_root=path.parent,
    )
    if (
        authenticated_locator_digest != locator_digest
        or locator.get("launch_lineage") != lineage
    ):
        raise LaunchLineageError(
            "launch_binding_mismatch",
            "bundle launch lineage differs from its authenticated root locator",
        )
    return authenticate_launch_lineage(
        lineage, require_completion=require_completion
    )


class FamilyPublicationError(ValueError):
    """A closed diagnostic at the custody-external publication boundary."""

    def __init__(self, check_id: str, detail: str) -> None:
        if check_id not in FAMILY_PUBLICATION_CHECK_IDS:
            raise ValueError(f"unregistered family-publication check_id {check_id!r}")
        super().__init__(detail)
        self.check_id = check_id


_FAMILY_MARKER_KEYS = frozenset(
    {
        "schema_version",
        "marker_kind",
        "family_id",
        "family_generation",
        "publication_state",
        "publication_git",
        "common_evidence_git",
        "lifecycle_registry",
        "members",
        "terminal_review",
        "publication_authority",
        "authoring_context",
        "assurance",
    }
)
_FAMILY_MEMBER_KEYS = frozenset(
    {
        "profile",
        "pack_id",
        "pack_path",
        "pack_digest_algorithm",
        "pack_sha256",
        "plan_tree",
        "frozen_plan",
        "freeze_receipt",
    }
)
_STEP6_TABLE_KEYS = frozenset(
    {
        "schema_version",
        "table_kind",
        "transaction_id",
        "family_id",
        "git",
        "registry",
        "family_publication",
        "successor_pinset",
        "confirmation",
    }
)


def _family_exact(value: object, keys: frozenset[str], where: str) -> Mapping[str, Any]:
    try:
        return _require_exact_keys(value, keys, where)
    except ArmReadinessError as exc:
        raise FamilyPublicationError("marker_schema_mismatch", str(exc)) from exc


def _family_first_generation(registry: Mapping[str, Any]) -> int:
    """Read split S-2's generation threshold out of the tracked registry.

    ``registry`` is the whole row registry (the object ``load_registry``
    returns).  The threshold is the pack generation at which family publication
    first engages -- 4 for the ``_v4`` family.  It lives in
    ``freeze_evidence_lifecycle.successor_policy.family_publication_first_generation``
    precisely so that advancing to ``_v5`` is a REVIEWED REGISTRY EDIT rather
    than a code change, which is what the marker ruling adopted in place of the
    literal predecessor-in-current-roster predicate.  A registry that does not
    carry the value cannot engage the mechanism at all: this refuses.
    """

    lifecycle = registry.get("freeze_evidence_lifecycle")
    value = (
        lifecycle.get("successor_policy", {}).get(
            "family_publication_first_generation"
        )
        if isinstance(lifecycle, Mapping)
        else None
    )
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "registry does not carry a resolved family-publication generation threshold",
        )
    return value


def _family_refusal_entry(registry: Mapping[str, Any]) -> dict[str, str]:
    entry = _r1_refusal_entry(registry["freeze_evidence_lifecycle"], "FAMILY_PUBLICATION")
    return {
        "role": "FAMILY_PUBLICATION",
        "code": str(entry["code"]),
        "type": str(entry["type"]),
    }


def _family_git_oid(value: object, where: str) -> str:
    if not isinstance(value, str) or _LOWER_GIT_OID_RE.fullmatch(value) is None:
        raise FamilyPublicationError("marker_schema_mismatch", f"{where} is not a Git OID")
    return value


def _family_sha(value: object, where: str) -> str:
    if not isinstance(value, str) or _LOWER_SHA256_RE.fullmatch(value) is None:
        raise FamilyPublicationError("marker_schema_mismatch", f"{where} is not a SHA-256")
    return value


def validate_family_publication_marker(
    value: object, *, first_generation: int
) -> Mapping[str, Any]:
    """Validate the immutable-from-build marker's exact schema.

    ``first_generation`` is the reviewed registry threshold (split S-2); the
    caller reads it from the tracked registry with ``_family_first_generation``
    so that no code literal names a family generation.
    """

    marker = _family_exact(value, _FAMILY_MARKER_KEYS, "family marker")
    if (
        marker["schema_version"] != FAMILY_PUBLICATION_MARKER_SCHEMA
        or marker["marker_kind"] != "FAMILY_PUBLICATION"
        or marker["family_id"] != "d117-v4"
        or marker["family_generation"] != first_generation
        or isinstance(marker["family_generation"], bool)
        or marker["publication_state"] != "PUBLISHED"
    ):
        raise FamilyPublicationError("marker_schema_mismatch", "family marker constants differ")
    publication_git = _family_exact(
        marker["publication_git"],
        frozenset(
            {
                "head_commit",
                "head_tree_oid",
                "local_main_commit",
                "origin_main_commit",
                "clean",
                "exact_match",
            }
        ),
        "family marker.publication_git",
    )
    head = _family_git_oid(publication_git["head_commit"], "publication head")
    _family_git_oid(publication_git["head_tree_oid"], "publication tree")
    if (
        publication_git["local_main_commit"] != head
        or publication_git["origin_main_commit"] != head
        or publication_git["clean"] is not True
        or publication_git["exact_match"] is not True
    ):
        raise FamilyPublicationError("head_mismatch", "publication Git values are not four-way exact")
    common_git = _family_exact(
        marker["common_evidence_git"],
        frozenset({"head_commit", "head_tree_oid"}),
        "family marker.common_evidence_git",
    )
    _family_git_oid(common_git["head_commit"], "common evidence head")
    _family_git_oid(common_git["head_tree_oid"], "common evidence tree")
    lifecycle = _family_exact(
        marker["lifecycle_registry"],
        frozenset(
            {
                "path",
                "schema_version",
                "registry_id",
                "sha256",
                "lifecycle_registry_id",
                "family_publication_marker_schema",
                "family_publication_refusal",
            }
        ),
        "family marker.lifecycle_registry",
    )
    if (
        lifecycle["path"] != ROW_REGISTRY_RELATIVE_PATH.as_posix()
        or lifecycle["schema_version"] != R1_ROW_REGISTRY_SCHEMA
        or lifecycle["registry_id"] != "d117-row-registry-v2"
        or lifecycle["lifecycle_registry_id"] != "d117-r1-lifecycle-v1"
        or lifecycle["family_publication_marker_schema"]
        != FAMILY_PUBLICATION_MARKER_SCHEMA
    ):
        raise FamilyPublicationError("registry_mismatch", "marker registry constants differ")
    _family_sha(lifecycle["sha256"], "marker registry digest")
    refusal = _family_exact(
        lifecycle["family_publication_refusal"],
        frozenset({"role", "code", "type"}),
        "family marker family-publication refusal",
    )
    if refusal != {
        "role": "FAMILY_PUBLICATION",
        "code": "readiness_r1_family_publication",
        "type": "CUSTODY",
    }:
        raise FamilyPublicationError("registry_mismatch", "marker refusal entry differs")

    members = marker["members"]
    if not isinstance(members, list) or len(members) != 3:
        raise FamilyPublicationError("roster_incomplete", "marker must carry three members")
    expected = (
        ("ALPHA", "d117_floor_qwen25_1p5b_v4"),
        ("BETA", "d117_floor_qwen25_7b_v4"),
        ("GAMMA", "d117_contrast_qwen25_1p5b_vs_7b_v4"),
    )
    for index, (raw_member, (profile, pack_id)) in enumerate(zip(members, expected, strict=True)):
        member = _family_exact(raw_member, _FAMILY_MEMBER_KEYS, f"family marker.members[{index}]")
        if (
            member["profile"] != profile
            or member["pack_id"] != pack_id
            or member["pack_path"] != f"configs/campaigns/{pack_id}"
            or member["pack_digest_algorithm"] != PACK_DIGEST_ALGORITHM
        ):
            raise FamilyPublicationError("roster_mismatch", f"member {index} identity differs")
        _family_sha(member["pack_sha256"], f"member {index} pack digest")
        plan_tree = _family_exact(
            member["plan_tree"],
            frozenset({"path", "sha256", "sidecar_path", "sidecar_sha256"}),
            f"member {index} plan tree",
        )
        if plan_tree["path"] != "plan_tree.json" or plan_tree["sidecar_path"] != "plan_tree.sha256":
            raise FamilyPublicationError("plan_binding_mismatch", "plan-tree paths differ")
        _family_sha(plan_tree["sha256"], "plan-tree digest")
        _family_sha(plan_tree["sidecar_sha256"], "plan-tree sidecar digest")
        frozen_plan = _family_exact(
            member["frozen_plan"],
            frozenset({"plan_id", "window_id", "path", "sha256"}),
            f"member {index} frozen plan",
        )
        for name in ("plan_id", "window_id", "path"):
            _require_string(frozen_plan[name], f"member {index} frozen_plan.{name}")
        _family_sha(frozen_plan["sha256"], "frozen-plan digest")
        freeze = _family_exact(
            member["freeze_receipt"],
            frozenset(
                {
                    "schema_version",
                    "receipt_id",
                    "ordinal",
                    "path",
                    "sha256",
                    "sidecar_path",
                    "sidecar_sha256",
                    "status",
                }
            ),
            f"member {index} freeze receipt",
        )
        if (
            freeze["schema_version"] != FREEZE_RECEIPT_V2_SCHEMA
            or freeze["receipt_id"] != "freeze-0004"
            or freeze["ordinal"] != 4
            or isinstance(freeze["ordinal"], bool)
            or freeze["path"] != "arm_readiness.freeze.receipts/freeze-0004.json"
            or freeze["sidecar_path"]
            != "arm_readiness.freeze.receipts/freeze-0004.json.sha256"
            or freeze["status"] != "PASS"
        ):
            raise FamilyPublicationError("freeze_binding_mismatch", "freeze-0004 constants differ")
        _family_sha(freeze["sha256"], "freeze digest")
        _family_sha(freeze["sidecar_sha256"], "freeze sidecar digest")
    terminal = _family_exact(
        marker["terminal_review"],
        frozenset({"evidence_kind", "head_tree_oid"}),
        "family marker.terminal_review",
    )
    if terminal["evidence_kind"] != "TERMINAL_REVIEW":
        raise FamilyPublicationError("terminal_review_mismatch", "terminal-review kind differs")
    terminal_tree = _family_git_oid(terminal["head_tree_oid"], "terminal-review tree")
    if terminal_tree != publication_git["head_tree_oid"]:
        raise FamilyPublicationError("terminal_review_mismatch", "terminal review binds another tree")
    authority = _family_exact(
        marker["publication_authority"],
        frozenset({"confirmation_schema", "required_decision"}),
        "family marker.publication_authority",
    )
    if authority != {
        "confirmation_schema": STEP6_CONFIRMATION_TABLE_SCHEMA,
        "required_decision": "YES",
    }:
        raise FamilyPublicationError("marker_schema_mismatch", "confirmation contract differs")
    context = _family_exact(
        marker["authoring_context"],
        frozenset(
            {
                "transaction_id",
                "source_commit_time_utc",
                "construction_phase",
                "custody_class",
                "builder",
                "consumer",
            }
        ),
        "family marker.authoring_context",
    )
    if (
        context["transaction_id"] != f"d117-v4@{head}"
        or context["construction_phase"] != "POST_FREEZE_FAMILY_BOUNDARY"
        or context["custody_class"] != "TRANSACTION_EXTERNAL"
    ):
        raise FamilyPublicationError("marker_schema_mismatch", "authoring constants differ")
    _require_string(context["source_commit_time_utc"], "marker source commit time")
    for role, expected_path in (
        ("builder", "scripts/build_family_marker.py"),
        ("consumer", "scripts/verify_family_marker.py"),
    ):
        tool = _family_exact(
            context[role], frozenset({"path", "sha256"}), f"marker {role}"
        )
        if tool["path"] != expected_path:
            raise FamilyPublicationError("tool_mismatch", f"marker {role} path differs")
        _family_sha(tool["sha256"], f"marker {role} digest")
    if marker["assurance"] != ASSURANCE:
        raise FamilyPublicationError("marker_schema_mismatch", "marker assurance differs")
    return marker


def validate_step6_confirmation_table(value: object) -> Mapping[str, Any]:
    """Validate the one-home, two-consumer step-6 confirmation artifact."""

    table = _family_exact(value, _STEP6_TABLE_KEYS, "step-6 confirmation table")
    if (
        table["schema_version"] != STEP6_CONFIRMATION_TABLE_SCHEMA
        or table["table_kind"] != "D117_STEP6_CONFIRMATION"
        or table["family_id"] != "d117-v4"
    ):
        raise FamilyPublicationError("confirmation_mismatch", "confirmation constants differ")
    _require_string(table["transaction_id"], "confirmation transaction_id")
    git = _family_exact(
        table["git"], frozenset({"head_commit", "head_tree_oid"}), "confirmation git"
    )
    _family_git_oid(git["head_commit"], "confirmation head")
    _family_git_oid(git["head_tree_oid"], "confirmation tree")
    registry = _family_exact(
        table["registry"],
        frozenset({"path", "schema_version", "registry_id", "sha256"}),
        "confirmation registry",
    )
    if (
        registry["path"] != ROW_REGISTRY_RELATIVE_PATH.as_posix()
        or registry["schema_version"] != R1_ROW_REGISTRY_SCHEMA
        or registry["registry_id"] != "d117-row-registry-v2"
    ):
        raise FamilyPublicationError("confirmation_mismatch", "confirmation registry differs")
    _family_sha(registry["sha256"], "confirmation registry digest")
    family = _family_exact(
        table["family_publication"],
        frozenset({"marker", "members"}),
        "confirmation family-publication section",
    )
    marker_ref = _family_exact(
        family["marker"],
        frozenset({"path", "schema_version", "sha256"}),
        "confirmation marker reference",
    )
    if (
        marker_ref["path"] != FAMILY_PUBLICATION_MARKER_NAME
        or marker_ref["schema_version"] != FAMILY_PUBLICATION_MARKER_SCHEMA
    ):
        raise FamilyPublicationError("confirmation_mismatch", "confirmation marker constants differ")
    _family_sha(marker_ref["sha256"], "confirmation marker digest")
    members = family["members"]
    if not isinstance(members, list) or len(members) != 3:
        raise FamilyPublicationError("confirmation_mismatch", "confirmation member table is incomplete")
    for index, member in enumerate(members):
        row = _family_exact(
            member,
            frozenset({"profile", "pack_id", "pack_sha256", "freeze_receipt_sha256"}),
            f"confirmation member {index}",
        )
        _family_sha(row["pack_sha256"], "confirmation member pack digest")
        _family_sha(row["freeze_receipt_sha256"], "confirmation member freeze digest")
    successor = _family_exact(
        table["successor_pinset"],
        frozenset({"path", "schema_version", "sha256", "pack_count", "receipt_count", "fact_count"}),
        "confirmation successor-pinset section",
    )
    if (
        successor["path"] != RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix()
        or successor["schema_version"] != RECEIPT_HISTSEM_PINSET_SCHEMA
    ):
        raise FamilyPublicationError("confirmation_mismatch", "successor-pinset constants differ")
    _family_sha(successor["sha256"], "confirmation successor pinset digest")
    for name in ("pack_count", "receipt_count", "fact_count"):
        if not isinstance(successor[name], int) or isinstance(successor[name], bool) or successor[name] < 0:
            raise FamilyPublicationError("confirmation_mismatch", f"confirmation {name} is invalid")
    # The contract fixes both counts for the _v4 family (contract doc
    # "successor_pinset section"); only fact_count is recomputed and free.
    if successor["pack_count"] != 3 or successor["receipt_count"] != 33:
        raise FamilyPublicationError(
            "confirmation_mismatch",
            "confirmation successor counts differ from the _v4 contract (3 packs, 33 receipts)",
        )
    confirmation = _family_exact(
        table["confirmation"],
        frozenset({"authority", "decision", "statement"}),
        "confirmation decision",
    )
    if (
        confirmation["authority"] != "ED"
        or confirmation["decision"] != "YES"
        or not isinstance(confirmation["statement"], str)
        or not confirmation["statement"]
    ):
        raise FamilyPublicationError("confirmation_mismatch", "Ed confirmation is not exact YES")
    return table


def _candidate_manifest_tool_digest(
    manifest_path: Path, relative_path: str
) -> str:
    """Read one tool's reviewed digest out of the S-0 ``$INPUT`` manifest.

    The manifest is ``s0-candidate-manifest.json`` from S-0 runsheet section
    1.3 -- the lead-reviewed custody record that names the candidate patch, its
    changed paths, and the exact bytes of every custody tool.  The binding this
    function reads is::

        {"custody_tools": {"<repo-relative tool path>": "<64 hex sha256>"}}

    Reading it is what makes candidate mode non-tautological: the digest comes
    from a document written and reviewed BEFORE the tool is executed, so a
    modified tool cannot authenticate itself by regenerating its own sidecar.
    """

    try:
        raw = manifest_path.resolve(strict=True).read_bytes()
    except OSError as exc:
        raise FamilyPublicationError(
            "tool_mismatch",
            f"reviewed candidate manifest is unreadable at {manifest_path}: {exc}",
        ) from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FamilyPublicationError(
            "tool_mismatch", f"reviewed candidate manifest is not JSON: {exc}"
        ) from exc
    tools = value.get("custody_tools") if isinstance(value, Mapping) else None
    if not isinstance(tools, Mapping):
        raise FamilyPublicationError(
            "tool_mismatch",
            "reviewed candidate manifest has no custody_tools object",
        )
    recorded = tools.get(relative_path)
    if not isinstance(recorded, str) or _LOWER_SHA256_RE.fullmatch(recorded) is None:
        raise FamilyPublicationError(
            "tool_mismatch",
            f"reviewed candidate manifest records no SHA-256 for {relative_path}",
        )
    return recorded


def _family_tool_reference(
    repository: Path,
    head: str,
    relative_path: str,
    executing_path: Path,
    *,
    phase: str,
    candidate_manifest: Path | str | None = None,
) -> dict[str, str]:
    """Authenticate the executing custody tool under the lane's own rule.

    PRODUCTION (``phase`` is anything but ``"candidate"``): the executing bytes
    must equal the blob committed at ``head``.  This is the ruled rule and the
    only one that can gate a publication.

    CANDIDATE (``phase == "candidate"``): the tools deliberately do not exist at
    the pinned HEAD of the S-0 clone, so committed-blob equality would refuse
    the clone proof.  The executing bytes are instead compared against the
    digest recorded in the reviewed ``$INPUT`` manifest (marker ruling, split
    S-5).  The lane is chosen by this argument alone -- never by the presence of
    a file on disk, which would let a dropped sidecar silently downgrade a
    production consult.
    """

    if phase not in {"candidate", "publication", "pre-arm", "t0"}:
        raise FamilyPublicationError(
            "lane_inadmissible", f"unsupported tool-authentication phase {phase!r}"
        )
    try:
        raw = executing_path.resolve(strict=True).read_bytes()
    except OSError as exc:
        raise FamilyPublicationError("tool_mismatch", f"cannot read {relative_path}: {exc}") from exc
    digest = sha256_bytes(raw)
    if phase == "candidate":
        manifest_path = (
            Path(candidate_manifest)
            if candidate_manifest is not None
            else executing_path.resolve(strict=True).with_name(
                S0_CANDIDATE_MANIFEST_NAME
            )
        )
        if _candidate_manifest_tool_digest(manifest_path, relative_path) != digest:
            raise FamilyPublicationError(
                "tool_mismatch",
                f"{relative_path} differs from the digest the reviewed candidate "
                "manifest records for it",
            )
    else:
        code, committed, _stderr = _histsem_git(repository, "show", f"{head}:{relative_path}")
        if code != 0 or committed != raw:
            raise FamilyPublicationError(
                "tool_mismatch",
                f"{relative_path} is not the blob committed at the reviewed head",
            )
    return {"path": relative_path, "sha256": digest}


def _family_member(
    repository: Path,
    root: Path,
    registry: Mapping[str, Any],
    registry_reference: Mapping[str, Any],
    *,
    step6_confirmation_table: Path | str | None = None,
) -> tuple[dict[str, Any], set[str]]:
    # A roster member that cannot be resolved or read at all is a family
    # diagnosis too.  Without these two wrappers the failure escapes as a bare
    # ArmReadinessError, which the CLI then reports as `registry_mismatch` --
    # naming the wrong artifact entirely (found by the G-7 live fixture).
    try:
        profile = _plan_profile(root, registry)
    except ArmReadinessError as exc:
        raise FamilyPublicationError("roster_mismatch", str(exc)) from exc
    try:
        tree, tree_raw = _plan_tree(root)
    except ArmReadinessError as exc:
        raise FamilyPublicationError("plan_binding_mismatch", str(exc)) from exc
    # Loading a v2 freeze receipt also authenticates its recorded D-139
    # predecessor chain.  That failure is a family diagnosis, not a generic
    # readiness error: give it the closed id the verification receipt reports,
    # so a marker consult can never say "predecessor_mismatch: PASS" for a
    # check whose refusal would have escaped as something else (gap G-5/G-9).
    try:
        freeze, freeze_ref = _load_freeze_reference(
            root,
            tree,
            registry_reference,
            registry,
            require_pass=True,
            step6_confirmation_table=step6_confirmation_table,
        )
    except ArmReadinessError as exc:
        if exc.reason_code == "readiness_successor_chain_invalid":
            raise FamilyPublicationError("predecessor_mismatch", str(exc)) from exc
        raise
    if freeze["schema_version"] != FREEZE_RECEIPT_V2_SCHEMA:
        raise FamilyPublicationError("freeze_binding_mismatch", "family freeze must use schema v2")
    if freeze["receipt_id"] != "freeze-0004" or freeze["status"] != "PASS":
        raise FamilyPublicationError("freeze_not_pass", "family freeze must be PASS freeze-0004")
    try:
        _items, receipts = _freeze_evidence_for_arm(
            root,
            tree,
            freeze,
            registry,
            step6_confirmation_table=step6_confirmation_table,
        )
    except (ArmReadinessError, EvidenceLifecycleError) as exc:
        raise FamilyPublicationError("evidence_set_mismatch", str(exc)) from exc
    derivation_heads = {
        str(receipt["derivation_commit"])
        for receipt in receipts.values()
        if "derivation_commit" in receipt
    }
    try:
        _repo, _prefix, pack_path = _repository_and_pack_relative(root)
        plan_sidecar_raw = (root / "plan_tree.sha256").read_bytes()
        freeze_raw = (root / str(freeze_ref["path"])).read_bytes()
        freeze_sidecar_raw = (root / f"{freeze_ref['path']}.sha256").read_bytes()
        plan_path = str(freeze["pack_identity"]["plan_path"])
        plan_raw = (root / plan_path).read_bytes()
    except (OSError, ArmReadinessError) as exc:
        raise FamilyPublicationError("plan_binding_mismatch", str(exc)) from exc
    pack = _pack_record(root)
    return (
        {
            "profile": profile,
            "pack_id": root.name,
            "pack_path": pack_path,
            "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
            "pack_sha256": pack["pack_sha256"],
            "plan_tree": {
                "path": "plan_tree.json",
                "sha256": sha256_bytes(tree_raw),
                "sidecar_path": "plan_tree.sha256",
                "sidecar_sha256": sha256_bytes(plan_sidecar_raw),
            },
            "frozen_plan": {
                "plan_id": freeze["pack_identity"]["plan_id"],
                "window_id": tree["window_identity"]["window_id"],
                "path": plan_path,
                "sha256": sha256_bytes(plan_raw),
            },
            "freeze_receipt": {
                "schema_version": freeze["schema_version"],
                "receipt_id": freeze["receipt_id"],
                "ordinal": _freeze_receipt_ordinal(str(freeze["receipt_id"]), "family freeze receipt_id"),
                "path": freeze_ref["path"],
                "sha256": sha256_bytes(freeze_raw),
                "sidecar_path": f"{freeze_ref['path']}.sha256",
                "sidecar_sha256": sha256_bytes(freeze_sidecar_raw),
                "status": freeze["status"],
            },
        },
        derivation_heads,
    )


def build_family_publication_marker(
    repository_root: Path | str,
    head: str,
    pack_roots: Sequence[Path | str],
    output_path: Path | str,
    *,
    builder_tool: Path | str,
    consumer_tool: Path | str,
    phase: str = "publication",
    candidate_manifest: Path | str | None = None,
) -> dict[str, Any]:
    """Construct deterministic marker bytes in external create-only custody.

    ``phase`` selects the tool-authentication lane (split S-5) and defaults to
    the strict production rule, so candidate semantics are always an explicit
    opt-in rather than something a stray file on disk can turn on.
    """

    repository = Path(repository_root).resolve(strict=True)
    output = Path(output_path).resolve(strict=False)
    try:
        output.relative_to(repository)
    except ValueError:
        pass
    else:
        raise FamilyPublicationError("output_in_tree", "marker output must be outside the repository")
    if output.exists() or output.with_name(f"{output.name}.sha256").exists():
        raise FamilyPublicationError("output_collision", "marker output or sidecar already exists")
    if len(pack_roots) != 3:
        raise FamilyPublicationError("roster_incomplete", "exactly three pack roots are required")
    roots = [
        (Path(item) if Path(item).is_absolute() else repository / Path(item)).resolve(strict=True)
        for item in pack_roots
    ]
    reviewed = reviewed_main(roots[0])
    if reviewed["head_commit"] != head or reviewed["exact_match"] is not True:
        diagnostic = "worktree_dirty" if reviewed["clean"] is not True else "head_mismatch"
        raise FamilyPublicationError(diagnostic, "marker build requires strict four-way reviewed main")
    registry, registry_raw = load_registry(repository)
    try:
        first_generation = _family_first_generation(registry)
    except ArmReadinessError as exc:
        raise FamilyPublicationError("registry_dormant", str(exc)) from exc
    lifecycle = registry["freeze_evidence_lifecycle"]
    expected = lifecycle["successor_policy"]["successor_pack_ids"]
    if {root.name for root in roots} != set(expected.values()):
        raise FamilyPublicationError("roster_mismatch", "pack roots differ from registry successor roster")
    registry_reference = {
        "registry_id": registry["registry_id"],
        "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
        "sha256": sha256_bytes(registry_raw),
        "plan_profile": None,
    }
    members: list[dict[str, Any]] = []
    derivation_heads: set[str] = set()
    for root in roots:
        reference = dict(registry_reference)
        reference["plan_profile"] = _plan_profile(root, registry)
        member, heads = _family_member(repository, root, registry, reference)
        members.append(member)
        derivation_heads.update(heads)
    members.sort(key=lambda member: ("ALPHA", "BETA", "GAMMA").index(member["profile"]))
    if len(derivation_heads) != 1:
        raise FamilyPublicationError("evidence_set_mismatch", "family evidence has no single derivation head")
    common_head = next(iter(derivation_heads))
    code, common_tree_raw, _stderr = _histsem_git(repository, "rev-parse", f"{common_head}^{{tree}}")
    if code != 0:
        raise FamilyPublicationError("head_unresolvable", "common evidence head is unavailable")
    common_tree = common_tree_raw.decode("ascii", errors="strict").strip()
    family_refusal = _family_refusal_entry(registry)
    builder_ref = _family_tool_reference(
        repository,
        head,
        "scripts/build_family_marker.py",
        Path(builder_tool),
        phase=phase,
        candidate_manifest=candidate_manifest,
    )
    consumer_ref = _family_tool_reference(
        repository,
        head,
        "scripts/verify_family_marker.py",
        Path(consumer_tool),
        phase=phase,
        candidate_manifest=candidate_manifest,
    )
    code, commit_time_raw, _stderr = _histsem_git(repository, "show", "-s", "--format=%cI", head)
    if code != 0:
        raise FamilyPublicationError("head_unresolvable", "publication commit time is unavailable")
    commit_time = datetime.fromisoformat(commit_time_raw.decode().strip()).astimezone(UTC)
    marker = {
        "schema_version": FAMILY_PUBLICATION_MARKER_SCHEMA,
        "marker_kind": "FAMILY_PUBLICATION",
        "family_id": "d117-v4",
        "family_generation": first_generation,
        "publication_state": "PUBLISHED",
        "publication_git": dict(reviewed),
        "common_evidence_git": {
            "head_commit": common_head,
            "head_tree_oid": common_tree,
        },
        "lifecycle_registry": {
            "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "schema_version": registry["schema_version"],
            "registry_id": registry["registry_id"],
            "sha256": sha256_bytes(registry_raw),
            "lifecycle_registry_id": lifecycle["registry_id"],
            "family_publication_marker_schema": lifecycle["successor_policy"]["family_publication_marker_schema"],
            "family_publication_refusal": family_refusal,
        },
        "members": members,
        "terminal_review": {
            "evidence_kind": "TERMINAL_REVIEW",
            "head_tree_oid": reviewed["head_tree_oid"],
        },
        "publication_authority": {
            "confirmation_schema": STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        },
        "authoring_context": {
            "transaction_id": f"d117-v4@{head}",
            "source_commit_time_utc": commit_time.isoformat().replace("+00:00", "Z"),
            "construction_phase": "POST_FREEZE_FAMILY_BOUNDARY",
            "custody_class": "TRANSACTION_EXTERNAL",
            "builder": builder_ref,
            "consumer": consumer_ref,
        },
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_family_publication_marker(marker, first_generation=first_generation)
    raw = render_json(marker)
    output.parent.mkdir(parents=True, exist_ok=True)
    _exclusive_write(output, raw)
    _exclusive_write(output.with_name(f"{output.name}.sha256"), gnu_sidecar(sha256_bytes(raw), output.name))
    return {
        "schema_version": "joulewise.d117_family_publication_build.v1",
        "status": "PASS",
        "marker_path": str(output),
        "marker_sha256": sha256_bytes(raw),
        "sidecar_path": str(output.with_name(f"{output.name}.sha256")),
        "sidecar_sha256": sha256_bytes(gnu_sidecar(sha256_bytes(raw), output.name)),
        "family_id": marker["family_id"],
        "head_commit": head,
        "head_tree_oid": reviewed["head_tree_oid"],
    }


def _read_external_canonical(
    path: Path,
    *,
    absent_check: str,
    invalid_check: str,
    noncanonical_check: str | None = None,
    digest_check: str | None = None,
) -> tuple[Mapping[str, Any], bytes]:
    try:
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        sidecar = path.with_name(f"{path.name}.sha256").read_bytes()
    except FileNotFoundError as exc:
        raise FamilyPublicationError(absent_check, f"custody artifact is absent: {path}") from exc
    except OSError as exc:
        raise FamilyPublicationError(invalid_check, f"custody artifact is unreadable: {exc}") from exc
    digest = sha256_bytes(raw)
    if sidecar != gnu_sidecar(digest, path.name):
        raise FamilyPublicationError(
            digest_check or invalid_check, "custody artifact sidecar differs"
        )
    try:
        value = parse_json_bytes(raw, require_canonical=True)
    except ArmReadinessError as exc:
        raise FamilyPublicationError(
            noncanonical_check or invalid_check,
            f"custody JSON is noncanonical: {exc}",
        ) from exc
    if not isinstance(value, Mapping):
        raise FamilyPublicationError(invalid_check, "custody JSON must be an object")
    return value, raw


def verify_family_publication_marker(
    repository_root: Path | str,
    marker_path: Path | str,
    *,
    phase: str,
    confirmation_path: Path | str | None = None,
    target_pack_root: Path | str | None = None,
    consumer_tool: Path | str | None = None,
    candidate_manifest: Path | str | None = None,
) -> dict[str, Any]:
    """Replay marker semantics; candidate PASS is never gate-admissible."""

    if phase not in {"candidate", "publication", "pre-arm", "t0"}:
        raise FamilyPublicationError("lane_inadmissible", f"unsupported marker phase {phase!r}")
    repository = Path(repository_root).resolve(strict=True)
    marker_file = Path(marker_path).resolve(strict=False)
    try:
        marker_file.relative_to(repository)
    except ValueError:
        pass
    else:
        raise FamilyPublicationError(
            "marker_unreadable", "published marker custody must be outside the repository"
        )
    registry, registry_raw = load_registry(repository)
    refusal = _family_refusal_entry(registry)
    marker_value, marker_raw = _read_external_canonical(
        marker_file,
        absent_check="marker_absent",
        invalid_check="marker_unreadable",
        noncanonical_check="marker_noncanonical",
        digest_check="marker_self_digest_mismatch",
    )
    try:
        marker = validate_family_publication_marker(
            marker_value, first_generation=_family_first_generation(registry)
        )
    except ArmReadinessError as exc:
        raise FamilyPublicationError("registry_dormant", str(exc)) from exc
    live = reviewed_main(repository)
    if live["clean"] is not True:
        raise FamilyPublicationError("worktree_dirty", "live marker consult requires a clean tree")
    # Split S-1 is STRICT FOUR-WAY equality.  Separate the two ways it can
    # fail, because they mean different things to an operator: the marker names
    # a head that is not the published head (`head_unpublished` -- the rollback
    # case the Sol refuter used to decide S-1: a checkout of an old published
    # head is trivially an ancestor of origin/main, so ancestry would admit it
    # and equality does not), versus the live coordinates simply disagreeing.
    if marker["publication_git"]["head_commit"] != live["origin_main_commit"]:
        raise FamilyPublicationError(
            "head_unpublished",
            "marker publication head is not the current origin/main -- an old "
            "published head or an unpushed head cannot gate",
        )
    if live["exact_match"] is not True or marker["publication_git"] != live:
        raise FamilyPublicationError("head_mismatch", "marker and live four-way Git coordinates differ")
    if marker["lifecycle_registry"] != {
        "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
        "schema_version": registry["schema_version"],
        "registry_id": registry["registry_id"],
        "sha256": sha256_bytes(registry_raw),
        "lifecycle_registry_id": registry["freeze_evidence_lifecycle"]["registry_id"],
        "family_publication_marker_schema": registry["freeze_evidence_lifecycle"]["successor_policy"]["family_publication_marker_schema"],
        "family_publication_refusal": refusal,
    }:
        raise FamilyPublicationError("registry_mismatch", "current registry differs from marker authority")
    expected_roster = registry["freeze_evidence_lifecycle"]["successor_policy"]["successor_pack_ids"]
    if {member["profile"]: member["pack_id"] for member in marker["members"]} != dict(expected_roster):
        raise FamilyPublicationError("roster_mismatch", "current registry roster differs from marker")
    common_heads: set[str] = set()
    for expected_member in marker["members"]:
        root = repository / str(expected_member["pack_path"])
        reference = {
            "registry_id": registry["registry_id"],
            "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "sha256": sha256_bytes(registry_raw),
            "plan_profile": expected_member["profile"],
        }
        observed, heads = _family_member(
            repository,
            root,
            registry,
            reference,
            step6_confirmation_table=(
                confirmation_path if phase != "candidate" else None
            ),
        )
        if observed != expected_member:
            raise FamilyPublicationError("pack_digest_mismatch", f"member replay differs: {root.name}")
        common_heads.update(heads)
    if len(common_heads) != 1:
        raise FamilyPublicationError("evidence_set_mismatch", "replayed family has mixed derivation heads")
    common_head = next(iter(common_heads))
    code, tree_raw, _stderr = _histsem_git(repository, "rev-parse", f"{common_head}^{{tree}}")
    if code != 0 or marker["common_evidence_git"] != {
        "head_commit": common_head,
        "head_tree_oid": tree_raw.decode("ascii", errors="strict").strip(),
    }:
        raise FamilyPublicationError("evidence_set_mismatch", "common evidence Git binding differs")
    if target_pack_root is not None:
        target = Path(target_pack_root).resolve(strict=True)
        _repo, _prefix, target_relative = _repository_and_pack_relative(target)
        if not any(
            member["pack_id"] == target.name and member["pack_path"] == target_relative
            for member in marker["members"]
        ):
            raise FamilyPublicationError("pack_not_member", "target pack is outside the published roster")
    if consumer_tool is not None:
        builder_path = Path(consumer_tool).with_name("build_family_marker.py")
        expected_builder = _family_tool_reference(
            repository,
            str(live["head_commit"]),
            "scripts/build_family_marker.py",
            builder_path,
            phase=phase,
            candidate_manifest=candidate_manifest,
        )
        expected_consumer = _family_tool_reference(
            repository,
            str(live["head_commit"]),
            "scripts/verify_family_marker.py",
            Path(consumer_tool),
            phase=phase,
            candidate_manifest=candidate_manifest,
        )
        if (
            marker["authoring_context"]["builder"] != expected_builder
            or marker["authoring_context"]["consumer"] != expected_consumer
        ):
            raise FamilyPublicationError("tool_mismatch", "executing tool pair differs from marker")

    confirmation_ref: dict[str, str] | None = None
    if phase != "candidate":
        if confirmation_path is None:
            raise FamilyPublicationError("confirmation_missing", "published phase requires step-6 table")
        table_value, table_raw = _read_external_canonical(
            Path(confirmation_path),
            absent_check="confirmation_missing",
            invalid_check="confirmation_mismatch",
        )
        table = validate_step6_confirmation_table(table_value)
        expected_members = [
            {
                "profile": member["profile"],
                "pack_id": member["pack_id"],
                "pack_sha256": member["pack_sha256"],
                "freeze_receipt_sha256": member["freeze_receipt"]["sha256"],
            }
            for member in marker["members"]
        ]
        if (
            table["git"]
            != {
                "head_commit": marker["publication_git"]["head_commit"],
                "head_tree_oid": marker["publication_git"]["head_tree_oid"],
            }
            or table["registry"]["sha256"] != marker["lifecycle_registry"]["sha256"]
            or table["family_publication"]["marker"]["sha256"] != sha256_bytes(marker_raw)
            or table["family_publication"]["members"] != expected_members
        ):
            raise FamilyPublicationError("confirmation_mismatch", "table C-to-M edge differs")
        confirmation_ref = {
            "path": str(Path(confirmation_path)),
            "sha256": sha256_bytes(table_raw),
        }
    # The checks array records the checks this run ACTUALLY executed, in the
    # order the code performs them.  It was previously a hardcoded literal that
    # reported PASS for checks that never ran (notably predecessor_mismatch),
    # which made a PASS receipt overstate what had been verified (gap G-9).
    executed = [
        "marker_self_digest_mismatch",
        "marker_noncanonical",
        "marker_schema_mismatch",
        "worktree_dirty",
        "head_unpublished",
        "head_mismatch",
        "registry_mismatch",
        "roster_mismatch",
        "predecessor_mismatch",
        "freeze_binding_mismatch",
        "freeze_not_pass",
        "plan_binding_mismatch",
        "pack_digest_mismatch",
        "evidence_set_mismatch",
        "terminal_review_mismatch",
    ]
    if target_pack_root is not None:
        executed.append("pack_not_member")
    if consumer_tool is not None:
        executed.append("tool_mismatch")
    if phase != "candidate":
        executed.append("confirmation_missing")
        executed.append("confirmation_mismatch")
    checks = [{"check_id": check_id, "status": "PASS"} for check_id in executed]
    return {
        "schema_version": FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
        "receipt_kind": "family_publication_verification",
        "phase": phase,
        "lane": "candidate" if phase == "candidate" else "published",
        "gate_admissible": phase != "candidate",
        "checked_at_utc": _utc_now(),
        "status": "PASS",
        "publication_authorized": phase != "candidate",
        "family_id": marker["family_id"],
        "marker": {"path": str(Path(marker_path)), "sha256": sha256_bytes(marker_raw)},
        "confirmation": confirmation_ref,
        "consulted_git": dict(live),
        "checks": checks,
        "refusals": [],
        "detail": None,
        "assurance": copy.deepcopy(ASSURANCE),
    }


def require_gate_admissible_verification(
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Refuse a verification receipt that cannot lawfully gate an arm.

    A family-publication verification receipt records the lane it was produced
    in.  Candidate-lane receipts are produced inside the S-0 clone, whose
    ``origin/main`` ref is deliberately forged, so a candidate PASS is
    forged-ref-conditional and must never be consumed as publication proof
    (D-151 condition 4, extended to this verifier by the marker ruling).

    Two distinct failures are separated here:

    * ``lane_inconsistent`` -- the receipt's own ``lane`` / ``gate_admissible``
      / ``publication_authorized`` fields disagree with its ``phase``.  Such a
      document is forged or corrupt: no honest run can emit it.
    * ``lane_inadmissible`` -- the receipt is internally coherent but is a
      candidate-lane or non-PASS receipt, which cannot gate.

    Call this on any verification receipt before letting it authorise anything,
    including one just produced in-process: it costs nothing and it is the only
    thing standing between a laundered candidate receipt and an arm.
    """

    if not isinstance(receipt, Mapping):
        raise FamilyPublicationError(
            "lane_inconsistent", "verification receipt is not an object"
        )
    phase = receipt.get("phase")
    if (
        receipt.get("schema_version") != FAMILY_PUBLICATION_VERIFICATION_SCHEMA
        or receipt.get("receipt_kind") != "family_publication_verification"
        or phase not in {"candidate", "publication", "pre-arm", "t0"}
    ):
        raise FamilyPublicationError(
            "lane_inconsistent", "verification receipt identity is not the governed one"
        )
    published = phase != "candidate"
    if (
        receipt.get("lane") != ("published" if published else "candidate")
        or receipt.get("gate_admissible") is not published
        or receipt.get("publication_authorized") is not published
    ):
        raise FamilyPublicationError(
            "lane_inconsistent",
            "verification receipt lane fields disagree with its own phase",
        )
    if receipt.get("gate_admissible") is not True or receipt.get("status") != "PASS":
        raise FamilyPublicationError(
            "lane_inadmissible",
            "a candidate-lane or non-PASS verification receipt cannot gate an arm",
        )
    return receipt


def _gate_family_publication(
    pack_root: Path,
    *,
    marker_path: Path | str | None,
    confirmation_path: Path | str | None,
) -> None:
    """Engage from the tracked successor roster, never marker presence."""

    repository = _repo_for_pack(pack_root)
    registry, _raw = load_registry(repository)
    roster = set(
        registry["freeze_evidence_lifecycle"]["successor_policy"][
            "successor_pack_ids"
        ].values()
    )
    if pack_root.name not in roster:
        return
    if marker_path is None:
        raise FamilyPublicationError("marker_absent", "registry-installed family has no marker")
    require_gate_admissible_verification(
        verify_family_publication_marker(
            repository,
            marker_path,
            phase="pre-arm",
            confirmation_path=confirmation_path,
            target_pack_root=pack_root,
        )
    )


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
    if schema in {FREEZE_RECEIPT_V1_SCHEMA, FREEZE_RECEIPT_V2_SCHEMA}:
        receipt = validate_freeze_receipt(value)
        if schema == FREEZE_RECEIPT_V2_SCHEMA:
            _authenticate_freeze_predecessor(
                Path(pack_root),
                receipt["predecessor"],
                successor_receipt_id=str(receipt["receipt_id"]),
                successor_profile=str(receipt["row_registry"]["plan_profile"]),
            )
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
    "CONTENT_EVIDENCE_RECEIPT_SCHEMA",
    "CONSUMPTION_RECEIPT_SCHEMA",
    "DRY_RUN_RECEIPT_SCHEMA",
    "EVIDENCE_RECEIPT_SCHEMA",
    "EXECUTION_EVIDENCE_RECEIPT_SCHEMA",
    "EvidenceLifecycleError",
    "FAMILY_PUBLICATION_CHECK_IDS",
    "FAMILY_PUBLICATION_MARKER_NAME",
    "FAMILY_PUBLICATION_MARKER_SCHEMA",
    "FAMILY_PUBLICATION_VERIFICATION_SCHEMA",
    "FamilyPublicationError",
    "FREEZE_RECEIPT_SCHEMA",
    "FREEZE_RECEIPT_V1_SCHEMA",
    "FREEZE_RECEIPT_V2_SCHEMA",
    "LAUNCH_COMPLETION_RECEIPT_SCHEMA",
    "LAUNCH_LINEAGE_LOCATOR_BASENAME",
    "LAUNCH_LINEAGE_LOCATOR_SCHEMA",
    "LAUNCH_LINEAGE_REASON_CODES",
    "LAUNCH_LINEAGE_SCHEMA",
    "LAUNCH_MANIFEST_SCHEMA",
    "LAUNCH_SETTLE_RECEIPT_SCHEMA",
    "LAUNCH_START_RECEIPT_SCHEMA",
    "LaunchLineageError",
    "PACK_DIGEST_ALGORITHM",
    "READINESS_REASON_CODES",
    "R1_FRESHNESS_CLASSES",
    "R1_LIFECYCLE_REGISTRY_PLACEHOLDER",
    "R1_LIFECYCLE_REGISTRY_SCHEMA",
    "R1_REFUSAL_ROLES",
    "R1_ROW_REGISTRY_SCHEMA",
    "RECEIPT_HISTSEM_PINSET_RELATIVE_PATH",
    "RECEIPT_HISTSEM_PINSET_SCHEMA",
    "ROW_REGISTRY_ID",
    "ROW_REGISTRY_SCHEMA",
    "SYNTHETIC_DOMAINS",
    "STEP6_CONFIRMATION_TABLE_NAME",
    "STEP6_CONFIRMATION_TABLE_SCHEMA",
    "applicability_for_row",
    "authenticate_bundle_launch_lineage",
    "authenticate_campaign_launch_lineage",
    "authenticate_launch_lineage",
    "authenticate_r1_lifecycle_registry",
    "committed_pack_tree_sha256",
    "build_family_publication_marker",
    "generate_arm_receipt",
    "generate_dry_run_receipt",
    "generate_freeze_receipt",
    "gnu_sidecar",
    "load_registry",
    "launch_lineage_required",
    "parse_json_bytes",
    "plan_arm_readiness_attachment",
    "record_launch_lifecycle_event",
    "render_json",
    "resolve_frozen_plan",
    "reviewed_main",
    "scan_receipt_namespace",
    "sha256_bytes",
    "normalize_plan_tree_for_freeze_evidence",
    "validate_arm_context",
    "validate_arm_receipt",
    "validate_consumption_receipt",
    "validate_dry_run_receipt",
    "validate_evidence_receipt",
    "validate_freeze_receipt",
    "validate_family_publication_marker",
    "validate_r1_class_lifecycle",
    "validate_r1_evidence_lifecycle",
    "validate_r1_lifecycle_registry",
    "validate_r1_temporal_budget",
    "validate_registry",
    "validate_terminal_review_head_tree",
    "validate_step6_confirmation_table",
    "verify_arm_receipt",
    "verify_consumed_launch",
    "verify_receipt",
    "verify_family_publication_marker",
]
