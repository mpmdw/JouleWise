#!/usr/bin/env python3
"""Mint a floor artifact with a digest-authenticated per-plan pinset.

This is the generalized sibling of ``mint_floor_artifact.py``.  It reuses
that mint's authentication, construction, binding, validation, and exclusive
write path through the review-pinned mint-core interface.  Every value that
the original tool hard-coded is required in one exact-schema JSON pinset,
whose exact file bytes must match a separately supplied SHA-256.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import inspect
import itertools
import json
import math
import re
import stat
import subprocess
import sys
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.whole_window import (  # noqa: E402
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
)
from joulewise.authentication_io import (  # noqa: E402
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    active_v2_authentication_session,
    read_authentication_input,
)
from joulewise.calibration_bracketing import (  # noqa: E402
    acceptance_allowance_rule,
    acceptance_bracket_screen_s,
    issued_calibration_allowance_projection,
    validate_calibration_bracket_binding,
)
from joulewise.floor_extraction import (  # noqa: E402
    validate_admitted_report_vocabulary,
    validate_d117_mint_consumption_report,
)
from joulewise import detection_floor  # noqa: E402
from joulewise import dominance_closeout  # noqa: E402
from joulewise import floor_mint_estimator as mint_estimator  # noqa: E402
from joulewise.identity_pins import derive_model_runtime_config  # noqa: E402


PINSET_SCHEMA_VERSION = "joulewise.floor_mint_pinset.v1"
PINSET_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pinset.v2"
PIN_REQUIREMENTS_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pin_requirements.v2"
V2_MINT_TOOL_VERSION = "joulewise.floor_mint.generalized.v2"


def allowance_rule_for(acceptance_id: str) -> str | None:
    """Resolve the mint allowance rule for the named acceptance generation."""

    return acceptance_allowance_rule(acceptance_id)


def bracket_screen_s_for(acceptance_id: str) -> str | None:
    """Resolve the mint bracket screen for the named acceptance generation."""

    return acceptance_bracket_screen_s(acceptance_id)


V2_CELL_COMPOSITION_RULE = "componentwise_max_never_sum.v1"
V2_CONSUMER_FLOOR_RULE = "cross_stack_armwise_max.v1"
V2_BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
V2_ASSURANCE_PROFILE = {
    "profile_id": "single_authority_hash_bound_replay.v1",
    "independent_attestation": False,
    "establishes": [
        "exact-byte consistency with disclosed commitments",
        "ledger and verdict consistency under the recorded code",
        "deterministic rederivability of mint inputs",
    ],
    "does_not_establish": [
        "honesty of the trusted operator",
        "independent witness of physical collection",
        "resistance to coordinated prepublication rewrite",
    ],
}
RETIRED_OPERATIVE_FLOOR_LITERAL = "7.377086"
_ORIGINAL_MINT_PATH = Path(__file__).with_name("mint_floor_artifact.py")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_SIX_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.[0-9]{6}$")
_SIX_DECIMAL_QUANTUM = Decimal("0.000001")
_EVIDENCE_ROOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SEMANTICS_IDS = {
    MINTED_CONSUMPTION_SEMANTICS_ID,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
}
_CORE_SEQUENCE = itertools.count()
_CORE_CONFIG_GLOBALS = frozenset(
    {
        "MINT_TOOL_VERSION",
        "CELL_ID",
        "TRANSPORT_GROUP_ID",
        "CONDITION_FAMILY_ID",
        "CONDITION_FAMILY_SHA256",
        "PLAN_SHA256",
        "A10_EVALUATION_BASIS_SHA256",
        "WINDOW_C_EVALUATION_BASIS_SHA256",
        "A10_EVALUATION_BASIS_MEMBERS",
        "WINDOW_C_EVALUATION_BASIS_MEMBERS",
        "A10_SPEC_MEMBERS",
        "WINDOW_C_SPEC_MEMBERS",
        "EXPECTED_ABSOLUTE_N",
        "EXPECTED_COMPARATIVE_N_BLOCKS",
        "A10_DRIFT_ALLOWANCE_J",
        "WINDOW_C_DRIFT_ALLOWANCE_J",
        "EXPECTED_OPERATIVE_FLOOR_TEXT",
        "A10_ORDER_MANIFEST_ID",
        "WINDOW_C_ORDER_MANIFEST_ID",
        "A10_CELL_ID",
        "WINDOW_C_CELL_ID",
        "METRIC",
        "WINDOW_CLASS",
        "TARGET_PRECHECK_PATH",
        "CALIBRATION_SCOPE",
        "PLAN_DECLARED_SCOPE",
        "SOURCE_CLASS",
    }
)
_CORE_SIGNATURES = {
    "ComponentPaths": (
        "(evidence_root_id: 'str', evidence_root: 'Path', report_path: 'Path', "
        "spec_path: 'Path', order_manifest_path: 'Path', "
        "calibration_cell_id: 'str', expected_kind: 'str') -> None"
    ),
    "pre_registration_gate": (
        "(*, plan: 'Mapping[str, Any]', plan_sha256: 'str', "
        "absolute: 'AuthenticatedComponent', "
        "comparative: 'AuthenticatedComponent') -> 'None'"
    ),
    "mint_authenticated_artifact": (
        "(*, artifact_id: 'str', plan: 'Mapping[str, Any]', "
        "plan_sha256: 'str', calibration_plan_relative_path: 'str', "
        "absolute: 'AuthenticatedComponent', "
        "comparative: 'AuthenticatedComponent', project_commit: 'str', "
        "project_tree_state: 'str') -> 'dict[str, Any]'"
    ),
    "validate_floor_artifact": (
        "(value: 'Mapping', *, pinset_path: 'Path | None' = None, "
        "expected_pinset_sha256: 'str | None' = None) -> 'list'"
    ),
    "mint_floor_artifact": (
        "(*, artifact_id: 'str', floor_path: 'Path', statement_path: 'Path', "
        "calibration_plan_path: 'Path', "
        "calibration_plan_relative_path: 'str', "
        "absolute_paths: 'ComponentPaths', comparative_paths: 'ComponentPaths', "
        "project_commit: 'str', project_tree_state: 'str', "
        "strict_validator: 'StrictValidator', "
        "consumption_semantics_id: 'str | None' = None, "
        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None) "
        "-> 'Mapping[str, Any]'"
    ),
    "_verify_report_widths": (
        "(cell: 'Mapping[str, Any]', widths: 'Sequence[float]') -> 'None'"
    ),
    "_authenticate_component": (
        "(paths: 'ComponentPaths', *, expected_cell_id: 'str', "
        "expected_basis_sha256: 'str', strict_validator: 'StrictValidator', "
        "consumption_authenticator: 'ConsumptionAuthenticator' = "
        "<callable:_authenticated_consumption_summaries>, allowance_deriver: "
        "'AllowanceDeriver' = <callable:whole_window_drift_allowances>, "
        "expected_consumption_semantics_id: 'str | None' = None, "
        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None, "
        "calibration_bracket_binding: 'Mapping[str, Any] | None' = None) -> "
        "'AuthenticatedComponent'"
    ),
    "bind_floor_artifact_evidence": (
        "(artifact: 'Mapping[str, Any]', floor_path: 'Path', evidence_roots: "
        "'Mapping[str, Path]', *, strict_validator: 'StrictValidator', "
        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None, "
        "calibration_bracket_binding: 'Mapping[str, Any] | None' = None) -> "
        "'Mapping[str, tuple[str, ...]]'"
    ),
}
# D-109 R1.4 added the immutable ledger-snapshot parameter. Any future
# change requires explicit signature-pin review plus parity evidence.
StrictValidator = Callable[[Path, bool], Sequence[str]]


class MintError(ValueError):
    """A pinset or delegated mint gate failed; no artifact may be written."""


D165_REPLAY_OUTPUT_REQUIRED = "d165_replay_output_required_for_common_mode"
D165_REPLAY_OUTPUT_UNUSED = "d165_replay_output_unused_without_common_mode"
D165_REPLAY_RECOMPUTATION_DIVERGENCE = "d165_replay_recomputation_divergence"


@dataclass(frozen=True)
class PlanPins:
    plan_id: str
    sha256: str
    declared_calibration_scope: str
    artifact_calibration_scope: str


@dataclass(frozen=True)
class ArtifactPins:
    cell_id: str
    transport_group_id: str
    source_class: str


@dataclass(frozen=True)
class CellPins:
    condition_family_id: str
    condition_family_sha256: str
    metric: str
    window_class: str
    target_precheck_path: tuple[str, ...]
    operative_floor_six_decimal: str


@dataclass(frozen=True)
class ComponentPins:
    evidence_root_id: str
    calibration_cell_id: str
    evaluation_basis_sha256: str
    evaluation_basis_members: int
    extraction_spec_members: int
    expected_n: int
    drift_allowance_j: float
    order_manifest_id: str
    consumption_semantics_id: str | None = None


@dataclass(frozen=True)
class MintPinset:
    mint_tool_version: str
    plan: PlanPins
    artifact: ArtifactPins
    cell: CellPins
    absolute: ComponentPins
    comparative: ComponentPins


@dataclass(frozen=True)
class V2Pinset:
    """A closed final-stage v2 pinset.

    ``value`` retains the authenticated JSON shape so producer and aggregate
    hashes can be checked over the exact governed projections.  Desk-stage
    requirements use a disjoint schema version and are never represented by
    this type.
    """

    value: Mapping[str, Any]


@dataclass(frozen=True)
class ComponentInputs:
    evidence_root: Path
    report_path: Path
    spec_path: Path
    order_manifest_path: Path


@dataclass(frozen=True)
class V2CellComponents:
    absolute: Any
    comparative: Any
    allowed_consumer_condition_families: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class V2ProducerInputs:
    plan: Mapping[str, Any]
    cells: Mapping[str, V2CellComponents]
    evidence_root: Path
    plan_sha256: str
    plan_declared_sha256: str
    plan_sidecar_sha256: str
    calibration_acceptance: Mapping[str, Any]
    calibration_acceptance_sha256: str
    bracket_binding: Mapping[str, Any]
    bracket_binding_sha256: str
    authenticated_pre_observation: Any | None = None
    authenticated_post_observation: Any | None = None
    calibration_allowance_projection: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class V2VerdictBracket:
    """Bracket identity projected from authenticated whole-window verdicts."""

    session_id: str
    window_id: str
    plan_id: str
    plan_sha256: str
    evidence_root_id: str
    runs_root: str
    endpoint_attempt_ids: tuple[str, str]
    endpoint_receipt_sha256s: tuple[str, str]
    endpoint_content_sha256s: tuple[str, str]


@dataclass(frozen=True)
class V2CellRecomputation:
    """One gated comparative result shared with artifact construction."""

    estimator_path: str
    comparative_blocks: tuple[Mapping[str, Any], ...]
    comparative_estimate: Any
    comparative_widths_j: tuple[float, ...]
    comparative_record: Mapping[str, Any]
    block_inputs: tuple[Any, ...] | None = None
    calibration_bracket: Mapping[str, Any] | None = None
    shared_edge_bound_s: float | None = None


def _object(
    value: object,
    label: str,
    expected_keys: set[str],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MintError(f"{label} must be an object")
    keys = set(value)
    missing = sorted(expected_keys - keys)
    extra = sorted(keys - expected_keys)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"extra={extra}")
        raise MintError(f"{label} schema mismatch: {'; '.join(details)}")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise MintError(f"{label} must be a nonempty trimmed string")
    return value


def _evidence_root_id(value: object, label: str) -> str:
    text = _string(value, label)
    if _EVIDENCE_ROOT_ID_RE.fullmatch(text) is None:
        raise MintError(
            f"{label} must be a portable identifier containing only letters, "
            "digits, dot, underscore, or hyphen"
        )
    return text


def _sha256(value: object, label: str) -> str:
    text = _string(value, label)
    if _SHA256_RE.fullmatch(text) is None:
        raise MintError(f"{label} must be 64 lowercase hexadecimal characters")
    return text


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise MintError(f"{label} must be a positive integer")
    return value


def _nonnegative_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise MintError(f"{label} must be a finite nonnegative number")
    converted = float(value)
    if not math.isfinite(converted) or converted < 0.0:
        raise MintError(f"{label} must be a finite nonnegative number")
    return converted


def _component_pins(value: object, label: str) -> ComponentPins:
    row = _object(
        value,
        label,
        {
            "evidence_root_id",
            "calibration_cell_id",
            "evaluation_basis_sha256",
            "evaluation_basis_members",
            "extraction_spec_members",
            "expected_n",
            "drift_allowance_j",
            "order_manifest_id",
        },
    )
    return ComponentPins(
        evidence_root_id=_evidence_root_id(
            row["evidence_root_id"], f"{label}.evidence_root_id"
        ),
        calibration_cell_id=_string(
            row["calibration_cell_id"], f"{label}.calibration_cell_id"
        ),
        evaluation_basis_sha256=_sha256(
            row["evaluation_basis_sha256"],
            f"{label}.evaluation_basis_sha256",
        ),
        evaluation_basis_members=_positive_int(
            row["evaluation_basis_members"],
            f"{label}.evaluation_basis_members",
        ),
        extraction_spec_members=_positive_int(
            row["extraction_spec_members"],
            f"{label}.extraction_spec_members",
        ),
        expected_n=_positive_int(row["expected_n"], f"{label}.expected_n"),
        drift_allowance_j=_nonnegative_number(
            row["drift_allowance_j"], f"{label}.drift_allowance_j"
        ),
        order_manifest_id=_string(
            row["order_manifest_id"], f"{label}.order_manifest_id"
        ),
    )


def _decimal_text(value: object, label: str) -> Decimal:
    text = _string(value, label)
    if _DECIMAL_RE.fullmatch(text) is None:
        raise MintError(f"{label} must be a plain unsigned decimal string")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise MintError(f"{label} must be an exact decimal string") from exc
    if not parsed.is_finite() or parsed < 0:
        raise MintError(f"{label} must be a finite nonnegative decimal string")
    return parsed


def _six_decimal(value: object, label: str) -> str:
    if not isinstance(value, str) or _SIX_DECIMAL_RE.fullmatch(value) is None:
        raise MintError(f"{label} must be a nonnegative six-decimal literal")
    if value == RETIRED_OPERATIVE_FLOOR_LITERAL:
        raise MintError(
            f"{label} reuses retired literal {RETIRED_OPERATIVE_FLOOR_LITERAL}"
        )
    return value


def _verify_six_decimal_rendering(
    full_precision: object,
    six_decimal: object,
    *,
    label: str,
) -> None:
    """Verify Decimal ``.6f`` semantics without rendering a mint literal."""

    full = _decimal_text(full_precision, f"{label}.full_precision")
    literal = _six_decimal(six_decimal, f"{label}.six_decimal")
    with localcontext() as context:
        context.prec = max(80, len(full.as_tuple().digits) + 7)
        rounded = full.quantize(
            _SIX_DECIMAL_QUANTUM,
            rounding=ROUND_HALF_EVEN,
        )
    if Decimal(literal) != rounded:
        raise MintError(
            f"{label}.six_decimal must equal the .6f rendering of "
            f"{label}.full_precision"
        )


def _member_pins(value: object, label: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list) or not value:
        raise MintError(f"{label} must be a nonempty array")
    result: list[tuple[str, str]] = []
    for index, item in enumerate(value):
        row_label = f"{label}[{index}]"
        row = _object(item, row_label, {"bundle_id", "config_sha256"})
        result.append(
            (
                _string(row["bundle_id"], f"{row_label}.bundle_id"),
                _sha256(row["config_sha256"], f"{row_label}.config_sha256"),
            )
        )
    bundle_ids = [bundle_id for bundle_id, _digest in result]
    if len(bundle_ids) != len(set(bundle_ids)):
        raise MintError(f"{label} bundle_id values must be unique")
    return tuple(result)


def _consumer_family_pins(value: object, label: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list) or not value:
        raise MintError(f"{label} must be a nonempty array")
    result = []
    for index, item in enumerate(value):
        row_label = f"{label}[{index}]"
        row = _object(
            item,
            row_label,
            {"condition_family_id", "condition_family_sha256"},
        )
        result.append(
            (
                _string(
                    row["condition_family_id"],
                    f"{row_label}.condition_family_id",
                ),
                _sha256(
                    row["condition_family_sha256"],
                    f"{row_label}.condition_family_sha256",
                ),
            )
        )
    if len(result) != len(set(result)):
        raise MintError(f"{label} entries must be unique")
    return tuple(result)


def _parse_v2_component(value: object, label: str) -> ComponentPins:
    row = _object(
        value,
        label,
        {
            "evidence_root_id",
            "calibration_cell_id",
            "evaluation_basis_sha256",
            "evaluation_basis_members",
            "extraction_spec_sha256",
            "extraction_spec_members",
            "expected_n",
            "drift_allowance_j",
            "order_manifest_id",
            "order_manifest_sha256",
            "consumption_semantics_id",
            "members",
        },
    )
    members = _member_pins(row["members"], f"{label}.members")
    extraction_count = _positive_int(
        row["extraction_spec_members"], f"{label}.extraction_spec_members"
    )
    # Parse the additional hashes even though the v1-compatible core consumes
    # only the ComponentPins projection.  The v2 gate authenticates them
    # against the supplied component evidence before construction.
    _sha256(row["extraction_spec_sha256"], f"{label}.extraction_spec_sha256")
    _sha256(row["order_manifest_sha256"], f"{label}.order_manifest_sha256")
    return ComponentPins(
        evidence_root_id=_evidence_root_id(
            row["evidence_root_id"], f"{label}.evidence_root_id"
        ),
        calibration_cell_id=_string(
            row["calibration_cell_id"], f"{label}.calibration_cell_id"
        ),
        evaluation_basis_sha256=_sha256(
            row["evaluation_basis_sha256"],
            f"{label}.evaluation_basis_sha256",
        ),
        evaluation_basis_members=_positive_int(
            row["evaluation_basis_members"],
            f"{label}.evaluation_basis_members",
        ),
        extraction_spec_members=extraction_count,
        expected_n=_positive_int(row["expected_n"], f"{label}.expected_n"),
        drift_allowance_j=_nonnegative_number(
            row["drift_allowance_j"], f"{label}.drift_allowance_j"
        ),
        order_manifest_id=_string(
            row["order_manifest_id"], f"{label}.order_manifest_id"
        ),
        consumption_semantics_id=_semantics_id(
            row["consumption_semantics_id"],
            f"{label}.consumption_semantics_id",
        ),
    )


def _semantics_id(value: object, label: str) -> str:
    text = _string(value, label)
    if text not in _SEMANTICS_IDS:
        raise MintError(f"{label} must be a registered consumption semantics id")
    return text


def _parse_v2_postcollection(
    value: object,
    label: str,
    *,
    acceptance_id: str,
) -> None:
    row = _object(
        value,
        label,
        {
            "absolute_evaluation_basis_sha256",
            "absolute_evaluation_basis_members",
            "comparative_evaluation_basis_sha256",
            "comparative_evaluation_basis_members",
            "pre_receipt_sha256",
            "pre_content_sha256",
            "post_receipt_sha256",
            "post_content_sha256",
            "bracket_binding_sha256",
            "terminal_ledger_head_sha256",
            "observed_drift_s",
            "allowance_rule",
            "bracket_screen_s",
            "applied_allowance_s",
            "allowance_embedding_count",
            "extraction_report_sha256",
            "absolute_floor_full_precision",
            "comparative_floor_full_precision",
            "operative_floor_full_precision",
            "absolute_floor_six_decimal",
            "comparative_floor_six_decimal",
            "operative_floor_six_decimal",
        },
    )
    for name in (
        "absolute_evaluation_basis_sha256",
        "comparative_evaluation_basis_sha256",
        "pre_receipt_sha256",
        "pre_content_sha256",
        "post_receipt_sha256",
        "post_content_sha256",
        "bracket_binding_sha256",
        "terminal_ledger_head_sha256",
        "extraction_report_sha256",
    ):
        _sha256(row[name], f"{label}.{name}")
    _positive_int(
        row["absolute_evaluation_basis_members"],
        f"{label}.absolute_evaluation_basis_members",
    )
    _positive_int(
        row["comparative_evaluation_basis_members"],
        f"{label}.comparative_evaluation_basis_members",
    )
    allowance_rule = allowance_rule_for(acceptance_id)
    bracket_screen_s = bracket_screen_s_for(acceptance_id)
    if allowance_rule is None or bracket_screen_s is None:
        raise MintError(f"{label}: unregistered acceptance generation {acceptance_id!r}")
    if row["allowance_rule"] != allowance_rule:
        raise MintError(
            f"{label}.allowance_rule must equal {allowance_rule!r}"
        )
    if row["bracket_screen_s"] != bracket_screen_s:
        raise MintError(
            f"{label}.bracket_screen_s must equal {bracket_screen_s!r}"
        )
    if (
        isinstance(row["allowance_embedding_count"], bool)
        or not isinstance(row["allowance_embedding_count"], int)
        or row["allowance_embedding_count"] != 1
    ):
        raise MintError(
            f"{label}.allowance_embedding_count must equal 1 (once per cell)"
        )
    observed = _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
    applied = _decimal_text(
        row["applied_allowance_s"], f"{label}.applied_allowance_s"
    )
    if applied != max(observed, Decimal(bracket_screen_s)):
        raise MintError(
            f"{label}.applied_allowance_s does not apply the never-zero rule once"
        )
    absolute_full = _decimal_text(
        row["absolute_floor_full_precision"],
        f"{label}.absolute_floor_full_precision",
    )
    comparative_full = _decimal_text(
        row["comparative_floor_full_precision"],
        f"{label}.comparative_floor_full_precision",
    )
    operative_full = _decimal_text(
        row["operative_floor_full_precision"],
        f"{label}.operative_floor_full_precision",
    )
    for name in (
        "absolute_floor_six_decimal",
        "comparative_floor_six_decimal",
        "operative_floor_six_decimal",
    ):
        _six_decimal(row[name], f"{label}.{name}")
    for component_name in ("absolute", "comparative", "operative"):
        _verify_six_decimal_rendering(
            row[f"{component_name}_floor_full_precision"],
            row[f"{component_name}_floor_six_decimal"],
            label=f"{label}.{component_name}_floor",
        )
    if operative_full != max(absolute_full, comparative_full):
        raise MintError(
            f"{label}.operative_floor_full_precision must equal the armwise maximum, never a sum"
        )


def _parse_v2_pinset(value: object) -> V2Pinset:
    root = _object(
        value,
        "pinset",
        {"schema_version", "mint_tool_version", "producer_plans", "aggregate"},
    )
    if root["schema_version"] != PINSET_SCHEMA_VERSION_V2:
        raise MintError(
            f"pinset.schema_version must equal {PINSET_SCHEMA_VERSION_V2!r}"
        )
    if root["mint_tool_version"] != V2_MINT_TOOL_VERSION:
        raise MintError(
            f"pinset.mint_tool_version must equal {V2_MINT_TOOL_VERSION!r}"
        )
    producers = root["producer_plans"]
    if not isinstance(producers, list) or len(producers) != 2:
        raise MintError("pinset.producer_plans must contain exactly two plans")

    plan_ids: list[str] = []
    cell_ids: list[str] = []
    group_ids: list[str] = []
    cell_values: list[Mapping[str, Any]] = []
    for producer_index, producer_value in enumerate(producers):
        label = f"pinset.producer_plans[{producer_index}]"
        producer = _object(
            producer_value,
            label,
            {
                "plan",
                "evidence_root_id",
                "component_artifact",
                "model_runtime_config",
                "extraction_spec",
                "calibration_acceptance",
                "cells",
            },
        )
        plan = _object(
            producer["plan"],
            f"{label}.plan",
            {
                "plan_id",
                "sha256",
                "declared_sha256",
                "sidecar_sha256",
                "relative_path",
                "declared_calibration_scope",
                "artifact_calibration_scope",
            },
        )
        plan_id = _string(plan["plan_id"], f"{label}.plan.plan_id")
        plan_ids.append(plan_id)
        for name in ("sha256", "declared_sha256", "sidecar_sha256"):
            _sha256(plan[name], f"{label}.plan.{name}")
        if plan["declared_sha256"] != plan["sha256"]:
            raise MintError(
                f"{label}.plan.declared_sha256 must equal the actual plan sha256"
            )
        _string(plan["relative_path"], f"{label}.plan.relative_path")
        _string(
            plan["declared_calibration_scope"],
            f"{label}.plan.declared_calibration_scope",
        )
        if plan["artifact_calibration_scope"] != "production_window":
            raise MintError(
                f"{label}.plan.artifact_calibration_scope must equal 'production_window'"
            )
        evidence_root_id = _evidence_root_id(
            producer["evidence_root_id"], f"{label}.evidence_root_id"
        )
        component_artifact = _object(
            producer["component_artifact"],
            f"{label}.component_artifact",
            {"artifact_id", "sha256"},
        )
        _string(
            component_artifact["artifact_id"],
            f"{label}.component_artifact.artifact_id",
        )
        _sha256(
            component_artifact["sha256"],
            f"{label}.component_artifact.sha256",
        )
        runtime = _object(
            producer["model_runtime_config"],
            f"{label}.model_runtime_config",
            {
                "model_artifact_sha256",
                "runtime_identity_sha256",
                "config_set_sha256",
            },
        )
        for name in runtime:
            _sha256(runtime[name], f"{label}.model_runtime_config.{name}")
        extraction = _object(
            producer["extraction_spec"],
            f"{label}.extraction_spec",
            {"sha256", "member_count"},
        )
        _sha256(extraction["sha256"], f"{label}.extraction_spec.sha256")
        _positive_int(
            extraction["member_count"],
            f"{label}.extraction_spec.member_count",
        )
        acceptance = _object(
            producer["calibration_acceptance"],
            f"{label}.calibration_acceptance",
            {
                "acceptance_id",
                "artifact_sha256",
                "derivation_sha256",
                "derivation_rule_id",
            },
        )
        acceptance_id = _string(
            acceptance["acceptance_id"],
            f"{label}.calibration_acceptance.acceptance_id",
        )
        _sha256(
            acceptance["artifact_sha256"],
            f"{label}.calibration_acceptance.artifact_sha256",
        )
        _sha256(
            acceptance["derivation_sha256"],
            f"{label}.calibration_acceptance.derivation_sha256",
        )
        _string(
            acceptance["derivation_rule_id"],
            f"{label}.calibration_acceptance.derivation_rule_id",
        )

        cells = producer["cells"]
        if not isinstance(cells, list) or len(cells) != 2:
            raise MintError(f"{label}.cells must contain decode and prefill")
        roles = []
        component_member_universe: set[str] = set()
        producer_custody_pins: list[tuple[object, ...]] = []
        for cell_index, cell_value in enumerate(cells):
            cell_label = f"{label}.cells[{cell_index}]"
            cell = _object(
                cell_value,
                cell_label,
                {
                    "role",
                    "cell_id",
                    "transport_group_id",
                    "condition_family_id",
                    "condition_family_sha256",
                    "metric",
                    "window_class",
                    "target_precheck_path",
                    "allowed_consumer_condition_families",
                    "absolute",
                    "comparative",
                    "postcollection",
                },
            )
            role = _string(cell["role"], f"{cell_label}.role")
            roles.append(role)
            expected_metric = {
                "decode": "phase_energy_j.decode",
                "prefill": "phase_energy_j.prefill",
            }.get(role)
            if expected_metric is None:
                raise MintError(f"{cell_label}.role must be decode or prefill")
            if cell["metric"] != expected_metric:
                raise MintError(
                    f"{cell_label}.metric must equal {expected_metric!r}"
                )
            if cell["window_class"] != "phase":
                raise MintError(f"{cell_label}.window_class must equal 'phase'")
            if cell["target_precheck_path"] != ["phase", role]:
                raise MintError(
                    f"{cell_label}.target_precheck_path must equal ['phase', {role!r}]"
                )
            cell_id = _string(cell["cell_id"], f"{cell_label}.cell_id")
            group_id = _string(
                cell["transport_group_id"],
                f"{cell_label}.transport_group_id",
            )
            cell_ids.append(cell_id)
            group_ids.append(group_id)
            cell_values.append(cell)
            _string(
                cell["condition_family_id"],
                f"{cell_label}.condition_family_id",
            )
            _sha256(
                cell["condition_family_sha256"],
                f"{cell_label}.condition_family_sha256",
            )
            _consumer_family_pins(
                cell["allowed_consumer_condition_families"],
                f"{cell_label}.allowed_consumer_condition_families",
            )
            absolute = _parse_v2_component(cell["absolute"], f"{cell_label}.absolute")
            comparative = _parse_v2_component(
                cell["comparative"], f"{cell_label}.comparative"
            )
            if absolute.evidence_root_id != evidence_root_id or (
                comparative.evidence_root_id != evidence_root_id
            ):
                raise MintError(
                    f"{cell_label}: component evidence_root_id must equal the producer root"
                )
            for component_name in ("absolute", "comparative"):
                component = cell[component_name]
                if (
                    component["extraction_spec_sha256"] != extraction["sha256"]
                    or component["extraction_spec_members"]
                    != extraction["member_count"]
                ):
                    raise MintError(
                        f"{cell_label}.{component_name}: extraction-spec inventory "
                        "must equal the producer pins"
                    )
            _parse_v2_postcollection(
                cell["postcollection"],
                f"{cell_label}.postcollection",
                acceptance_id=acceptance_id,
            )
            post = cell["postcollection"]
            producer_custody_pins.append(
                tuple(
                    post[name]
                    for name in (
                        "pre_receipt_sha256",
                        "pre_content_sha256",
                        "post_receipt_sha256",
                        "post_content_sha256",
                        "bracket_binding_sha256",
                        "terminal_ledger_head_sha256",
                        "observed_drift_s",
                        "applied_allowance_s",
                        "extraction_report_sha256",
                    )
                )
            )
            if (
                post["absolute_evaluation_basis_sha256"]
                != absolute.evaluation_basis_sha256
                or post["absolute_evaluation_basis_members"]
                != absolute.evaluation_basis_members
                or post["comparative_evaluation_basis_sha256"]
                != comparative.evaluation_basis_sha256
                or post["comparative_evaluation_basis_members"]
                != comparative.evaluation_basis_members
            ):
                raise MintError(
                    f"{cell_label}.postcollection evaluation basis disagrees with component pins"
                )
            component_member_universe.update(
                bundle_id for bundle_id, _digest in _member_pins(
                    cell["absolute"]["members"], f"{cell_label}.absolute.members"
                )
            )
            component_member_universe.update(
                bundle_id for bundle_id, _digest in _member_pins(
                    cell["comparative"]["members"],
                    f"{cell_label}.comparative.members",
                )
            )
        if set(roles) != {"decode", "prefill"} or len(roles) != len(set(roles)):
            raise MintError(f"{label}.cells must contain one decode and one prefill role")
        if len(set(producer_custody_pins)) != 1:
            raise MintError(
                f"{label}.cells must share one authenticated producer custody record"
            )
        if len(component_member_universe) > extraction["member_count"]:
            raise MintError(
                f"{label}.extraction_spec.member_count must cover the unique pinned member count"
            )

    if len(plan_ids) != len(set(plan_ids)):
        raise MintError("pinset producer plan ids must be unique")
    if len(cell_ids) != 4 or len(cell_ids) != len(set(cell_ids)):
        raise MintError("pinset must define exactly four unique cell ids")
    if len(group_ids) != 4 or len(group_ids) != len(set(group_ids)):
        raise MintError("pinset must define exactly four unique transport groups")

    aggregate = _object(
        root["aggregate"],
        "pinset.aggregate",
        {
            "artifact_id",
            "plan_set_id",
            "producer_set_sha256",
            "calibration_scope",
            "source_class",
            "cell_composition_rule",
            "consumer_floor_rule",
            "component_artifacts",
            "cell_ids",
            "transport_allowlists",
        },
    )
    _string(aggregate["artifact_id"], "pinset.aggregate.artifact_id")
    _string(aggregate["plan_set_id"], "pinset.aggregate.plan_set_id")
    _sha256(
        aggregate["producer_set_sha256"],
        "pinset.aggregate.producer_set_sha256",
    )
    if aggregate["calibration_scope"] != "production_window":
        raise MintError("pinset.aggregate.calibration_scope must equal 'production_window'")
    if aggregate["source_class"] != "prospective":
        raise MintError("pinset.aggregate.source_class must equal 'prospective'")
    if aggregate["cell_composition_rule"] != V2_CELL_COMPOSITION_RULE:
        raise MintError(
            f"pinset.aggregate.cell_composition_rule must equal {V2_CELL_COMPOSITION_RULE!r}"
        )
    if aggregate["consumer_floor_rule"] != V2_CONSUMER_FLOOR_RULE:
        raise MintError(
            f"pinset.aggregate.consumer_floor_rule must equal {V2_CONSUMER_FLOOR_RULE!r}"
        )
    if aggregate["cell_ids"] != cell_ids:
        raise MintError("pinset.aggregate.cell_ids must positionally equal producer cell ids")
    component_artifacts = aggregate["component_artifacts"]
    if not isinstance(component_artifacts, list) or len(component_artifacts) != 2:
        raise MintError("pinset.aggregate.component_artifacts must contain two entries")
    for index, entry_value in enumerate(component_artifacts):
        entry_label = f"pinset.aggregate.component_artifacts[{index}]"
        entry = _object(
            entry_value,
            entry_label,
            {"plan_id", "artifact_id", "sha256", "producer_pin_sha256"},
        )
        _string(entry["plan_id"], f"{entry_label}.plan_id")
        _string(entry["artifact_id"], f"{entry_label}.artifact_id")
        _sha256(entry["sha256"], f"{entry_label}.sha256")
        _sha256(
            entry["producer_pin_sha256"],
            f"{entry_label}.producer_pin_sha256",
        )
        producer = producers[index]
        if entry["plan_id"] != producer["plan"]["plan_id"] or (
            entry["artifact_id"] != producer["component_artifact"]["artifact_id"]
            or entry["sha256"] != producer["component_artifact"]["sha256"]
        ):
            raise MintError(
                f"{entry_label} does not match the corresponding producer component pins"
            )
    allowlists = aggregate["transport_allowlists"]
    if not isinstance(allowlists, list) or len(allowlists) != 4:
        raise MintError("pinset.aggregate.transport_allowlists must contain four entries")
    for index, entry_value in enumerate(allowlists):
        entry_label = f"pinset.aggregate.transport_allowlists[{index}]"
        entry = _object(
            entry_value,
            entry_label,
            {
                "transport_group_id",
                "cell_ids",
                "allowed_consumer_condition_families",
            },
        )
        if entry["transport_group_id"] != group_ids[index]:
            raise MintError(f"{entry_label}.transport_group_id is out of order")
        if entry["cell_ids"] != [cell_ids[index]]:
            raise MintError(
                f"{entry_label}.cell_ids must contain exactly its independently stack-scoped cell"
            )
        _consumer_family_pins(
            entry["allowed_consumer_condition_families"],
            f"{entry_label}.allowed_consumer_condition_families",
        )
        if _consumer_family_pins(
            entry["allowed_consumer_condition_families"],
            f"{entry_label}.allowed_consumer_condition_families",
        ) != _consumer_family_pins(
            cell_values[index]["allowed_consumer_condition_families"],
            f"pinset cell {cell_ids[index]}.allowed_consumer_condition_families",
        ):
            raise MintError(
                f"{entry_label}.allowed_consumer_condition_families "
                "contradicts the component cell allowlist"
            )
    return V2Pinset(value=copy.deepcopy(dict(root)))


def _parse_pinset(value: object) -> MintPinset:
    root = _object(
        value,
        "pinset",
        {
            "schema_version",
            "mint_tool_version",
            "plan",
            "artifact",
            "cell",
            "absolute",
            "comparative",
        },
    )
    if root["schema_version"] != PINSET_SCHEMA_VERSION:
        raise MintError(
            "pinset.schema_version must equal " f"{PINSET_SCHEMA_VERSION!r}"
        )
    plan = _object(
        root["plan"],
        "pinset.plan",
        {
            "plan_id",
            "sha256",
            "declared_calibration_scope",
            "artifact_calibration_scope",
        },
    )
    artifact = _object(
        root["artifact"],
        "pinset.artifact",
        {"cell_id", "transport_group_id", "source_class"},
    )
    cell = _object(
        root["cell"],
        "pinset.cell",
        {
            "condition_family_id",
            "condition_family_sha256",
            "metric",
            "window_class",
            "target_precheck_path",
            "operative_floor_six_decimal",
        },
    )
    precheck_path = cell["target_precheck_path"]
    if not isinstance(precheck_path, list) or not precheck_path:
        raise MintError("pinset.cell.target_precheck_path must be a nonempty array")
    precheck = tuple(
        _string(part, f"pinset.cell.target_precheck_path[{index}]")
        for index, part in enumerate(precheck_path)
    )
    operative_value = cell["operative_floor_six_decimal"]
    if (
        not isinstance(operative_value, str)
        or _SIX_DECIMAL_RE.fullmatch(operative_value) is None
    ):
        raise MintError(
            "pinset.cell.operative_floor_six_decimal must be a nonnegative "
            "six-decimal literal"
        )
    operative = operative_value
    pinset = MintPinset(
        mint_tool_version=_string(
            root["mint_tool_version"], "pinset.mint_tool_version"
        ),
        plan=PlanPins(
            plan_id=_string(plan["plan_id"], "pinset.plan.plan_id"),
            sha256=_sha256(plan["sha256"], "pinset.plan.sha256"),
            declared_calibration_scope=_string(
                plan["declared_calibration_scope"],
                "pinset.plan.declared_calibration_scope",
            ),
            artifact_calibration_scope=_string(
                plan["artifact_calibration_scope"],
                "pinset.plan.artifact_calibration_scope",
            ),
        ),
        artifact=ArtifactPins(
            cell_id=_string(artifact["cell_id"], "pinset.artifact.cell_id"),
            transport_group_id=_string(
                artifact["transport_group_id"],
                "pinset.artifact.transport_group_id",
            ),
            source_class=_string(
                artifact["source_class"], "pinset.artifact.source_class"
            ),
        ),
        cell=CellPins(
            condition_family_id=_string(
                cell["condition_family_id"],
                "pinset.cell.condition_family_id",
            ),
            condition_family_sha256=_sha256(
                cell["condition_family_sha256"],
                "pinset.cell.condition_family_sha256",
            ),
            metric=_string(cell["metric"], "pinset.cell.metric"),
            window_class=_string(
                cell["window_class"], "pinset.cell.window_class"
            ),
            target_precheck_path=precheck,
            operative_floor_six_decimal=operative,
        ),
        absolute=_component_pins(root["absolute"], "pinset.absolute"),
        comparative=_component_pins(
            root["comparative"], "pinset.comparative"
        ),
    )
    fixed_decode_contract = {
        "pinset.plan.artifact_calibration_scope": (
            pinset.plan.artifact_calibration_scope,
            "production_window",
        ),
        "pinset.artifact.source_class": (
            pinset.artifact.source_class,
            "prospective",
        ),
        "pinset.cell.metric": (
            pinset.cell.metric,
            "phase_energy_j.decode",
        ),
        "pinset.cell.window_class": (pinset.cell.window_class, "phase"),
    }
    for label, (observed, expected) in fixed_decode_contract.items():
        if observed != expected:
            raise MintError(f"{label} must equal {expected!r}")
    if pinset.cell.target_precheck_path != ("phase", "decode"):
        raise MintError(
            "pinset.cell.target_precheck_path must equal ['phase', 'decode']"
        )
    return pinset


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MintError(f"pinset contains duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> None:
    raise MintError(f"pinset contains non-finite JSON number {value!r}")


def _parse_finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        _reject_nonfinite_json(value)
    return parsed


def _parse_finite_json_int(value: str) -> int:
    parsed = int(value)
    try:
        finite_projection = math.isfinite(float(parsed))
    except OverflowError:
        finite_projection = False
    if not finite_projection:
        _reject_nonfinite_json(value)
    return parsed


def _strict_json_value(raw: bytes, label: str) -> Any:
    """Parse one v2 input without JSON's duplicate/non-finite extensions."""

    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
            parse_float=_parse_finite_json_float,
            parse_int=_parse_finite_json_int,
        )
    except MintError as exc:
        raise MintError(f"{label}: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MintError(f"{label} is not valid UTF-8 JSON: {exc}") from exc


def _strict_json_file(path: Path, label: str) -> tuple[Any, bytes]:
    try:
        raw = read_authentication_input(path, grammar="json", label=label)
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(
            f"{label} cannot be read: {exc.strerror or type(exc).__name__}"
        ) from exc
    return _strict_json_value(raw, label), raw


def _pre_admit_legacy_report(path: Path, label: str) -> None:
    """Guard exact report bytes before the pinned core's permissive loader."""

    value, _raw = _strict_json_file(path, label)
    if not isinstance(value, Mapping):
        raise MintError(f"{label} must contain a JSON object")
    errors = validate_admitted_report_vocabulary(value)
    if errors:
        raise MintError(f"{label} refused admitted vocabulary: {errors[0]}")


def _allow_governed_extraction_spec(path: Path) -> None:
    """Authorize the one profile where registration vocabulary is declared."""

    session = active_v2_authentication_session()
    if session is None:
        raise MintError("governed extraction spec requires an authentication session")
    session.allow_governed_extraction_spec(path)


def _strict_json_lines_file(path: Path, label: str) -> bytes:
    try:
        raw = read_authentication_input(path, grammar="jsonl", label=label)
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(
            f"{label} cannot be read: {exc.strerror or type(exc).__name__}"
        ) from exc
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise MintError(f"{label} is not valid UTF-8 JSONL: {exc}") from exc
    for index, line in enumerate(lines, start=1):
        if line.strip():
            _strict_json_value(line.encode("utf-8"), f"{label} line {index}")
    return raw


def _actual_v2_git_state() -> tuple[str, bool | None]:
    """Return the actual clean HEAD and whether origin/main contains it."""

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ("git", "-C", str(REPO_ROOT), *args),
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            raise MintError(f"cannot inspect mint repository state: {exc}") from exc

    head_result = run("rev-parse", "--verify", "HEAD")
    head = head_result.stdout.strip()
    if head_result.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise MintError("cannot derive the actual Git HEAD for v2 issuance")
    status_result = run("status", "--porcelain", "--untracked-files=all")
    if status_result.returncode != 0:
        raise MintError("cannot derive the actual Git tree state for v2 issuance")
    if status_result.stdout:
        dirty = ", ".join(
            line.strip() for line in status_result.stdout.splitlines()[:8]
        )
        raise MintError(
            "v2 issuance requires a clean Git working tree "
            f"(dirty: {dirty})"
        )
    # origin/main containment is recorded evidence, never a gate: an
    # unresolvable upstream (offline, single-branch clone) records unknown.
    upstream_result = run("rev-parse", "--verify", "origin/main^{commit}")
    if upstream_result.returncode != 0:
        return head, None
    contained_result = run("merge-base", "--is-ancestor", head, "origin/main")
    if contained_result.returncode not in (0, 1):
        return head, None
    return head, contained_result.returncode == 0


def _head_pin_commit_containment_in_origin_main(
    head_pin_path: Path,
) -> bool | None:
    """Record containment of the commit that last changed one head-pin."""

    try:
        relative = Path(head_pin_path).resolve().relative_to(REPO_ROOT.resolve())
    except (OSError, RuntimeError, ValueError):
        return None

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ("git", "-C", str(REPO_ROOT), *args),
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            return subprocess.CompletedProcess(args, 1, "", "")

    if run("rev-parse", "--verify", "origin/main^{commit}").returncode != 0:
        return None
    commit_result = run(
        "log",
        "-1",
        "--format=%H",
        "--",
        relative.as_posix(),
    )
    commit = commit_result.stdout.strip()
    if (
        commit_result.returncode != 0
        or re.fullmatch(r"[0-9a-f]{40}", commit) is None
    ):
        return None
    contained_result = run("merge-base", "--is-ancestor", commit, "origin/main")
    if contained_result.returncode not in (0, 1):
        return None
    return contained_result.returncode == 0


def load_pinset(path: Path, expected_sha256: str) -> MintPinset | V2Pinset:
    """Authenticate exact bytes, then enforce the disjoint final pinset schema."""

    expected = _sha256(expected_sha256, "pinset sha256 argument")
    path = Path(path)
    try:
        file_stat = path.lstat()
    except OSError as exc:
        raise MintError(f"pinset cannot be inspected: {exc.strerror or type(exc).__name__}") from exc
    if stat.S_ISLNK(file_stat.st_mode):
        raise MintError("pinset must not be a symlink")
    if not stat.S_ISREG(file_stat.st_mode):
        raise MintError("pinset must be a regular file")
    try:
        raw = read_authentication_input(path, grammar="json", label="pinset")
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(f"pinset cannot be read: {exc.strerror or type(exc).__name__}") from exc
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise MintError(
            f"pinset sha256 mismatch: expected {expected}, observed {actual}"
        )
    value = _strict_json_value(raw, "pinset")
    schema_version = value.get("schema_version") if isinstance(value, Mapping) else None
    if schema_version == PIN_REQUIREMENTS_SCHEMA_VERSION_V2:
        raise MintError("desk-stage pin requirements are non-mintable")
    if schema_version == PINSET_SCHEMA_VERSION_V2:
        return _parse_v2_pinset(value)
    return _parse_pinset(value)


def _load_v1_pinset(path: Path, expected_sha256: str) -> MintPinset:
    pinset = load_pinset(path, expected_sha256)
    if not isinstance(pinset, MintPinset):
        raise MintError("v2 pinset requires the multi-cell mint entry point")
    return pinset


def _render_core_signature(value: Any) -> str:
    signature = inspect.signature(value)
    rendered = str(signature)
    for parameter in signature.parameters.values():
        default = parameter.default
        if default is not inspect.Parameter.empty and callable(default):
            rendered = rendered.replace(
                repr(default),
                f"<callable:{getattr(default, '__name__', type(default).__name__)}>",
            )
    return rendered


def _assert_core_interface(module: ModuleType) -> None:
    missing = sorted(
        (_CORE_CONFIG_GLOBALS | set(_CORE_SIGNATURES) | {"MintError"})
        - set(vars(module))
    )
    if missing:
        raise MintError(
            "review-pinned mint-core interface drift: missing or renamed "
            f"symbols {missing}"
        )
    if not isinstance(module.MintError, type) or not issubclass(
        module.MintError, ValueError
    ):
        raise MintError(
            "review-pinned mint-core interface drift: MintError is not a "
            "ValueError type"
        )
    for symbol, expected in _CORE_SIGNATURES.items():
        try:
            observed = _render_core_signature(getattr(module, symbol))
        except (TypeError, ValueError) as exc:
            raise MintError(
                "review-pinned mint-core interface drift: cannot inspect "
                f"{symbol} signature"
            ) from exc
        if observed != expected:
            raise MintError(
                "review-pinned mint-core interface drift: "
                f"{symbol} signature expected {expected}, observed {observed}"
            )
    # Rendered-signature equality is spoofable: a default object whose
    # repr() is "None" renders identically while defeating the core's
    # `is None` load-on-absent behavior. Identity-check the sentinel
    # defaults structurally.
    mint_params = inspect.signature(module.mint_floor_artifact).parameters
    for name in ("consumption_semantics_id", "calibration_ledger_snapshot"):
        if mint_params[name].default is not None:
            raise MintError(
                "review-pinned mint-core interface drift: mint_floor_artifact "
                f"parameter {name} default is not the None sentinel"
            )


def _fresh_original_core() -> ModuleType:
    name = f"_joulewise_generalized_floor_mint_core_{next(_CORE_SEQUENCE)}"
    spec = importlib.util.spec_from_file_location(name, _ORIGINAL_MINT_PATH)
    if spec is None or spec.loader is None:
        raise MintError("cannot load the review-pinned mint-core interface")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        _assert_core_interface(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    sys.modules.pop(name, None)
    return module


def _configured_artifact_validator(
    core: ModuleType,
    pinset_path: Path,
    expected_pinset_sha256: str,
) -> Callable[[Mapping[str, Any]], list[Any]]:
    original_validator = core.validate_floor_artifact

    def validate(artifact: Mapping[str, Any]) -> list[Any]:
        return original_validator(
            artifact,
            pinset_path=pinset_path,
            expected_pinset_sha256=expected_pinset_sha256,
        )

    return validate


def _configured_core(
    pinset: MintPinset,
    *,
    pinset_path: Path,
    expected_pinset_sha256: str,
) -> ModuleType:
    """Load an isolated mint-1 core and replace only its hard-pin globals."""

    core = _fresh_original_core()
    original_gate = core.pre_registration_gate
    assignments = {
        "MINT_TOOL_VERSION": pinset.mint_tool_version,
        "CELL_ID": pinset.artifact.cell_id,
        "TRANSPORT_GROUP_ID": pinset.artifact.transport_group_id,
        "CONDITION_FAMILY_ID": pinset.cell.condition_family_id,
        "CONDITION_FAMILY_SHA256": pinset.cell.condition_family_sha256,
        "PLAN_SHA256": pinset.plan.sha256,
        "A10_EVALUATION_BASIS_SHA256": (
            pinset.absolute.evaluation_basis_sha256
        ),
        "WINDOW_C_EVALUATION_BASIS_SHA256": (
            pinset.comparative.evaluation_basis_sha256
        ),
        "A10_EVALUATION_BASIS_MEMBERS": (
            pinset.absolute.evaluation_basis_members
        ),
        "WINDOW_C_EVALUATION_BASIS_MEMBERS": (
            pinset.comparative.evaluation_basis_members
        ),
        "A10_SPEC_MEMBERS": pinset.absolute.extraction_spec_members,
        "WINDOW_C_SPEC_MEMBERS": pinset.comparative.extraction_spec_members,
        "EXPECTED_ABSOLUTE_N": pinset.absolute.expected_n,
        "EXPECTED_COMPARATIVE_N_BLOCKS": pinset.comparative.expected_n,
        "A10_DRIFT_ALLOWANCE_J": pinset.absolute.drift_allowance_j,
        "WINDOW_C_DRIFT_ALLOWANCE_J": pinset.comparative.drift_allowance_j,
        "EXPECTED_OPERATIVE_FLOOR_TEXT": (
            pinset.cell.operative_floor_six_decimal
        ),
        "A10_ORDER_MANIFEST_ID": pinset.absolute.order_manifest_id,
        "WINDOW_C_ORDER_MANIFEST_ID": pinset.comparative.order_manifest_id,
        "A10_CELL_ID": pinset.absolute.calibration_cell_id,
        "WINDOW_C_CELL_ID": pinset.comparative.calibration_cell_id,
        "METRIC": pinset.cell.metric,
        "WINDOW_CLASS": pinset.cell.window_class,
        "TARGET_PRECHECK_PATH": pinset.cell.target_precheck_path,
        "CALIBRATION_SCOPE": pinset.plan.artifact_calibration_scope,
        "PLAN_DECLARED_SCOPE": pinset.plan.declared_calibration_scope,
        "SOURCE_CLASS": pinset.artifact.source_class,
    }
    for name, value in assignments.items():
        setattr(core, name, value)

    core.validate_floor_artifact = _configured_artifact_validator(
        core,
        pinset_path,
        expected_pinset_sha256,
    )

    def generalized_gate(
        *,
        plan: Mapping[str, Any],
        plan_sha256: str,
        absolute: Any,
        comparative: Any,
    ) -> None:
        if plan_sha256 != pinset.plan.sha256:
            raise core.MintError(
                "pre-registration gate: calibration plan sha256 mismatch"
            )
        if (
            plan.get("plan_id") != pinset.plan.plan_id
            or plan.get("calibration_scope")
            != pinset.plan.declared_calibration_scope
        ):
            raise core.MintError(
                "pre-registration gate: calibration plan identity mismatch"
            )
        if absolute.evidence_root_id != pinset.absolute.evidence_root_id:
            raise core.MintError(
                "pre-registration gate: absolute evidence-root id mismatch"
            )
        if comparative.evidence_root_id != pinset.comparative.evidence_root_id:
            raise core.MintError(
                "pre-registration gate: comparative evidence-root id mismatch"
            )
        if (
            absolute.order_manifest.get("plan_id") != pinset.plan.plan_id
            or comparative.order_manifest.get("plan_id")
            != pinset.plan.plan_id
        ):
            raise core.MintError(
                "pre-registration gate: order manifest plan id mismatch"
            )

        # The original gate has three historical identity literals embedded
        # in its function body.  Normalize only those already-hard-checked
        # values for the call; every other check executes unchanged against
        # the configured pin globals.  Construction later receives the real
        # plan and components, so no normalized value reaches the artifact.
        legacy_plan_id = "p2-015-window-a-m3max-qwen25-1p5b-v1"
        normalized_plan = dict(plan)
        normalized_plan["plan_id"] = legacy_plan_id

        def normalized_component(component: Any, root_id: str) -> Any:
            order_manifest = dict(component.order_manifest)
            order_manifest["plan_id"] = legacy_plan_id
            return replace(
                component,
                evidence_root_id=root_id,
                order_manifest=order_manifest,
            )

        original_gate(
            plan=normalized_plan,
            plan_sha256=plan_sha256,
            absolute=normalized_component(absolute, "a10"),
            comparative=normalized_component(comparative, "window_c"),
        )

    core.pre_registration_gate = generalized_gate
    return core


def pre_registration_gate(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    plan: Mapping[str, Any],
    plan_sha256: str,
    absolute: Any,
    comparative: Any,
) -> None:
    """Run the configured pre-registration gate without building an artifact."""

    pinset = _load_v1_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        core.pre_registration_gate(
            plan=plan,
            plan_sha256=plan_sha256,
            absolute=absolute,
            comparative=comparative,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def mint_authenticated_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    artifact_id: str,
    plan: Mapping[str, Any],
    plan_sha256: str,
    calibration_plan_relative_path: str,
    absolute: Any,
    comparative: Any,
    project_commit: str,
    project_tree_state: str,
) -> Mapping[str, Any]:
    """Gate and build from already-authenticated component fixtures/evidence."""

    pinset = _load_v1_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        return core.mint_authenticated_artifact(
            artifact_id=artifact_id,
            plan=plan,
            plan_sha256=plan_sha256,
            calibration_plan_relative_path=calibration_plan_relative_path,
            absolute=absolute,
            comparative=comparative,
            project_commit=project_commit,
            project_tree_state=project_tree_state,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def validate_floor_artifact(
    *,
    artifact: Mapping[str, Any],
    pinset_path: Path,
    pinset_sha256: str,
    _skip_v2_hash_binding: bool = False,
) -> list[Any]:
    """Validate an artifact against its authenticated v1 or final-v2 pinset."""

    pinset = load_pinset(pinset_path, pinset_sha256)
    if isinstance(pinset, MintPinset):
        core = _configured_core(
            pinset,
            pinset_path=pinset_path,
            expected_pinset_sha256=pinset_sha256,
        )
        return core.validate_floor_artifact(artifact)
    core = _fresh_original_core()
    errors = list(
        core.validate_floor_artifact(
            artifact,
            pinset_path=pinset_path,
            expected_pinset_sha256=pinset_sha256,
        )
    )
    if not _skip_v2_hash_binding:
        errors.extend(_validate_v2_artifact_binding(artifact, pinset))
    return errors


def mint_floor_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    artifact_id: str,
    floor_path: Path,
    statement_path: Path,
    calibration_plan_path: Path,
    calibration_plan_relative_path: str,
    absolute_inputs: ComponentInputs,
    comparative_inputs: ComponentInputs,
    project_commit: str,
    project_tree_state: str,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None = None,
) -> Mapping[str, Any]:
    """Authenticate, gate, construct, bind, validate, and write one artifact."""

    if active_v2_authentication_session() is None:
        try:
            with V2AuthenticationReadSession():
                return mint_floor_artifact(
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha256,
                    artifact_id=artifact_id,
                    floor_path=floor_path,
                    statement_path=statement_path,
                    calibration_plan_path=calibration_plan_path,
                    calibration_plan_relative_path=calibration_plan_relative_path,
                    absolute_inputs=absolute_inputs,
                    comparative_inputs=comparative_inputs,
                    project_commit=project_commit,
                    project_tree_state=project_tree_state,
                    strict_validator=strict_validator,
                    consumption_semantics_id=consumption_semantics_id,
                )
        except V2AuthenticationInputError as exc:
            raise MintError(str(exc)) from exc

    pinset = _load_v1_pinset(pinset_path, pinset_sha256)
    _pre_admit_legacy_report(
        absolute_inputs.report_path, "absolute extraction report"
    )
    _pre_admit_legacy_report(
        comparative_inputs.report_path, "comparative extraction report"
    )
    _allow_governed_extraction_spec(absolute_inputs.spec_path)
    _allow_governed_extraction_spec(comparative_inputs.spec_path)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        return core.mint_floor_artifact(
            artifact_id=artifact_id,
            floor_path=floor_path,
            statement_path=statement_path,
            calibration_plan_path=calibration_plan_path,
            calibration_plan_relative_path=calibration_plan_relative_path,
            absolute_paths=core.ComponentPaths(
                evidence_root_id=pinset.absolute.evidence_root_id,
                evidence_root=absolute_inputs.evidence_root,
                report_path=absolute_inputs.report_path,
                spec_path=absolute_inputs.spec_path,
                order_manifest_path=absolute_inputs.order_manifest_path,
                calibration_cell_id=pinset.absolute.calibration_cell_id,
                expected_kind="absolute",
            ),
            comparative_paths=core.ComponentPaths(
                evidence_root_id=pinset.comparative.evidence_root_id,
                evidence_root=comparative_inputs.evidence_root,
                report_path=comparative_inputs.report_path,
                spec_path=comparative_inputs.spec_path,
                order_manifest_path=comparative_inputs.order_manifest_path,
                calibration_cell_id=pinset.comparative.calibration_cell_id,
                expected_kind="comparative",
            ),
            project_commit=project_commit,
            project_tree_state=project_tree_state,
            strict_validator=strict_validator,
            consumption_semantics_id=consumption_semantics_id,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def _canonical_json_sha256(value: object) -> str:
    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MintError("v2 pin projection is not canonical JSON") from exc
    return hashlib.sha256(payload).hexdigest()


def _artifact_payload(artifact: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def _artifact_sha256(artifact: Mapping[str, Any]) -> str:
    return hashlib.sha256(_artifact_payload(artifact)).hexdigest()


def _artifact_sha256_containment_variants(
    artifact: Mapping[str, Any],
) -> frozenset[str]:
    """Hash one artifact under every non-gating containment observation.

    Both Git-containment fields are required provenance, but lookup failure is
    explicitly allowed and neither fact gates issuance. Component byte pins
    therefore bind the fields' presence and every other byte while accepting
    any honest boolean/null observation made at mint time.
    """

    provenance = artifact.get("provenance")
    implementation = (
        provenance.get("implementation")
        if isinstance(provenance, Mapping)
        else None
    )
    keys = (
        "mint_commit_contained_in_origin_main",
        "head_pin_commit_contained_in_origin_main",
    )
    if not isinstance(implementation, Mapping) or any(
        key not in implementation for key in keys
    ):
        return frozenset({_artifact_sha256(artifact)})
    variants: set[str] = set()
    for values in itertools.product((False, True, None), repeat=len(keys)):
        candidate = copy.deepcopy(dict(artifact))
        candidate_implementation = candidate["provenance"]["implementation"]
        for key, value in zip(keys, values):
            candidate_implementation[key] = value
        variants.add(_artifact_sha256(candidate))
    return frozenset(variants)


def _v2_producer_hashes(pinset: V2Pinset) -> tuple[tuple[str, ...], str]:
    producers = pinset.value["producer_plans"]
    producer_hashes = tuple(_canonical_json_sha256(row) for row in producers)
    producer_set_hash = _canonical_json_sha256(producers)
    return producer_hashes, producer_set_hash


def _validate_v2_pin_hashes(pinset: V2Pinset) -> None:
    producer_hashes, producer_set_hash = _v2_producer_hashes(pinset)
    aggregate = pinset.value["aggregate"]
    for index, (observed, entry) in enumerate(
        zip(producer_hashes, aggregate["component_artifacts"])
    ):
        if observed != entry["producer_pin_sha256"]:
            raise MintError(
                "aggregate/component hash mismatch: producer pin "
                f"{index} expected {entry['producer_pin_sha256']}, observed {observed}"
            )
    if producer_set_hash != aggregate["producer_set_sha256"]:
        raise MintError(
            "aggregate hash mismatch: producer_set_sha256 expected "
            f"{aggregate['producer_set_sha256']}, observed {producer_set_hash}"
        )


def _v2_component_pins(component: Mapping[str, Any], label: str) -> ComponentPins:
    return _parse_v2_component(component, label)


def _v2_mint_pinset(
    producer: Mapping[str, Any],
    cell: Mapping[str, Any],
) -> MintPinset:
    plan = producer["plan"]
    post = cell["postcollection"]
    return MintPinset(
        mint_tool_version=V2_MINT_TOOL_VERSION,
        plan=PlanPins(
            plan_id=plan["plan_id"],
            sha256=plan["sha256"],
            declared_calibration_scope=plan["declared_calibration_scope"],
            artifact_calibration_scope=plan["artifact_calibration_scope"],
        ),
        artifact=ArtifactPins(
            cell_id=cell["cell_id"],
            transport_group_id=cell["transport_group_id"],
            source_class="prospective",
        ),
        cell=CellPins(
            condition_family_id=cell["condition_family_id"],
            condition_family_sha256=cell["condition_family_sha256"],
            metric=cell["metric"],
            window_class=cell["window_class"],
            target_precheck_path=tuple(cell["target_precheck_path"]),
            operative_floor_six_decimal=post["operative_floor_six_decimal"],
        ),
        absolute=_v2_component_pins(cell["absolute"], "v2.cell.absolute"),
        comparative=_v2_component_pins(
            cell["comparative"], "v2.cell.comparative"
        ),
    )


def _v2_gate_component(
    actual: Any,
    pins: Mapping[str, Any],
    *,
    label: str,
    metric: str,
    window_class: str,
) -> None:
    if actual.evidence_root_id != pins["evidence_root_id"]:
        raise MintError(f"{label}: evidence root id mismatch")
    if actual.calibration_cell_id != pins["calibration_cell_id"]:
        raise MintError(f"{label}: calibration cell id mismatch")
    if actual.spec_sha256 != pins["extraction_spec_sha256"]:
        raise MintError(f"{label}: extraction spec sha256 mismatch")
    if actual.order_manifest_sha256 != pins["order_manifest_sha256"]:
        raise MintError(f"{label}: order manifest sha256 mismatch")
    if actual.spec_cell.get("metric") != metric or (
        actual.spec_cell.get("window_class") != window_class
    ):
        raise MintError(f"{label}: wrong metric/phase precheck component")
    if actual.whole_window_evaluation_basis_sha256 != pins[
        "evaluation_basis_sha256"
    ]:
        raise MintError(f"{label}: evaluation basis sha256 mismatch")
    if actual.evaluation_basis_member_count != pins["evaluation_basis_members"]:
        raise MintError(f"{label}: evaluation basis member count mismatch")
    if len(set(_v2_spec_member_ids(actual.spec))) != pins[
        "extraction_spec_members"
    ]:
        raise MintError(f"{label}: extraction spec member count mismatch")
    expected_member_count = (
        pins["expected_n"]
        if actual.kind == "absolute"
        else 4 * pins["expected_n"]
    )
    if len(actual.members) != expected_member_count or actual.cell.get(
        "floor", {}
    ).get("n") != pins["expected_n"]:
        raise MintError(f"{label}: expected n mismatch")
    if actual.whole_window_drift_allowance.get("allowance_j") != pins[
        "drift_allowance_j"
    ]:
        raise MintError(f"{label}: energy drift allowance mismatch")
    if actual.order_manifest.get("manifest_id") != pins["order_manifest_id"]:
        raise MintError(f"{label}: order manifest id mismatch")
    if actual.consumption_semantics_id != pins["consumption_semantics_id"]:
        raise MintError(f"{label}: consumption semantics mismatch")
    observed_members = tuple(
        (member.bundle_id, member.config_sha256) for member in actual.members
    )
    expected_members = _member_pins(pins["members"], f"{label}.members")
    if observed_members != expected_members:
        raise MintError(f"{label}: exact member/config pins mismatch")


def _v2_spec_member_ids(spec: Mapping[str, Any]) -> tuple[str, ...]:
    """Return physical member ids across a potentially multi-metric spec."""

    ids: list[str] = []
    cells = spec.get("cells")
    if not isinstance(cells, list):
        return ()
    for cell in cells:
        if not isinstance(cell, Mapping):
            continue
        members = cell.get("members")
        if isinstance(members, list):
            ids.extend(
                row["bundle_id"]
                for row in members
                if isinstance(row, Mapping)
                and isinstance(row.get("bundle_id"), str)
            )
        blocks = cell.get("blocks")
        if isinstance(blocks, list):
            for block in blocks:
                block_members = (
                    block.get("members") if isinstance(block, Mapping) else None
                )
                if isinstance(block_members, Mapping):
                    ids.extend(
                        member
                        for member in block_members.values()
                        if isinstance(member, str)
                    )
    return tuple(ids)


def _mapping_attribute(value: object, name: str) -> object:
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def _require_postcollection_evidence_equal(
    field: str,
    pinned: object,
    evidenced: object,
    *,
    source: str,
) -> None:
    if pinned != evidenced:
        raise MintError(
            f"postcollection_evidence_mismatch: {field} mismatch against {source}"
        )


def _v2_component_verdict_bracket(
    component: Any,
    *,
    label: str,
) -> V2VerdictBracket:
    bracket = getattr(component, "whole_window_calibration_bracket", None)
    if not isinstance(bracket, Mapping):
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            f"missing authenticated bracket basis for {label}"
        )
    endpoints = tuple(bracket.get(role) for role in ("pre", "post"))
    if any(not isinstance(endpoint, Mapping) for endpoint in endpoints):
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            f"has malformed endpoints for {label}"
        )
    pre, post = endpoints
    assert isinstance(pre, Mapping) and isinstance(post, Mapping)
    common_fields = (
        ("bracket_session_id", "session_id"),
        ("bracket_window_id", "window_id"),
        ("bracket_plan_id", "plan_id"),
        ("bracket_plan_sha256", "plan_sha256"),
        ("bracket_evidence_root_id", "evidence_root_id"),
        ("bracket_runs_root", "runs_root"),
    )
    common: dict[str, str] = {}
    for source_field, projected_field in common_fields:
        pre_value = pre.get(source_field)
        post_value = post.get(source_field)
        if (
            not isinstance(pre_value, str)
            or not pre_value
            or pre_value != post_value
        ):
            raise MintError(
                "postcollection_evidence_mismatch: verdict/bracket cross-check "
                f"disagrees on {source_field} for {label}"
            )
        common[projected_field] = pre_value
    if pre.get("bracket_slot") != "pre" or post.get("bracket_slot") != "post":
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            f"has invalid endpoint slots for {label}"
        )

    def pair(field: str) -> tuple[str, str]:
        values = (pre.get(field), post.get(field))
        if any(not isinstance(value, str) or not value for value in values):
            raise MintError(
                "postcollection_evidence_mismatch: verdict/bracket cross-check "
                f"has invalid {field} for {label}"
            )
        return values  # type: ignore[return-value]

    return V2VerdictBracket(
        **common,
        endpoint_attempt_ids=pair("attempt_id"),
        endpoint_receipt_sha256s=pair("ledger_receipt_digest"),
        endpoint_content_sha256s=pair("content_id"),
    )


def _v2_verdict_bracket(
    *,
    producer: Mapping[str, Any],
    inputs: V2ProducerInputs,
) -> V2VerdictBracket:
    brackets = [
        _v2_component_verdict_bracket(
            component,
            label=f"{role}.{kind}",
        )
        for role, cell in sorted(inputs.cells.items())
        for kind, component in (
            ("absolute", cell.absolute),
            ("comparative", cell.comparative),
        )
    ]
    if not brackets or any(bracket != brackets[0] for bracket in brackets[1:]):
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            "does not identify one whole-window bracket"
        )
    expected = brackets[0]
    plan = producer["plan"]
    if (
        expected.plan_id,
        expected.plan_sha256,
        expected.evidence_root_id,
    ) != (
        plan["plan_id"],
        plan["sha256"],
        producer["evidence_root_id"],
    ) or Path(expected.runs_root).resolve() != inputs.evidence_root.resolve():
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            "disagrees with authenticated plan/evidence-root owners"
        )
    return expected


def _v2_crosscheck_binding_against_verdict(
    binding: Mapping[str, Any],
    expected: V2VerdictBracket,
) -> None:
    for field in (
        "session_id",
        "window_id",
        "plan_id",
        "plan_sha256",
        "evidence_root_id",
        "runs_root",
    ):
        if binding.get(field) != getattr(expected, field):
            raise MintError(
                "postcollection_evidence_mismatch: verdict/bracket cross-check "
                f"refused binding {field}"
            )
    endpoints = binding.get("endpoints")
    if not isinstance(endpoints, Mapping):
        raise MintError(
            "postcollection_evidence_mismatch: verdict/bracket cross-check "
            "refused malformed binding endpoints"
        )
    for index, role in enumerate(("pre", "post")):
        endpoint = endpoints.get(role)
        if not isinstance(endpoint, Mapping):
            raise MintError(
                "postcollection_evidence_mismatch: verdict/bracket cross-check "
                f"refused malformed {role} endpoint"
            )
        expected_endpoint = {
            "attempt_id": expected.endpoint_attempt_ids[index],
            "receipt_digest": expected.endpoint_receipt_sha256s[index],
            "content_digest": expected.endpoint_content_sha256s[index],
        }
        if dict(endpoint) != expected_endpoint:
            raise MintError(
                "postcollection_evidence_mismatch: verdict/bracket cross-check "
                f"refused binding {role} endpoint"
            )


def _v2_allowance_projection(
    inputs: V2ProducerInputs,
    pre: Any,
    post: Any,
) -> Mapping[str, Any]:
    projection = issued_calibration_allowance_projection(
        inputs.calibration_acceptance,
        pre_exact_bound_lexeme_s=str(
            _mapping_attribute(pre, "exact_bound_lexeme_s")
        ),
        post_exact_bound_lexeme_s=str(
            _mapping_attribute(post, "exact_bound_lexeme_s")
        ),
    )
    if projection is None:
        raise MintError(
            "postcollection_evidence_mismatch: issued acceptance allowance is not derivable"
        )
    pin_projection = dict(projection)
    for field in (
        "observed_drift_s",
        "bracket_screen_s",
        "applied_allowance_s",
    ):
        pin_projection[field] = format(
            Decimal(str(pin_projection[field])), "f"
        )
    pin_projection["allowance_rule"] = (
        f"max(observed_drift_s,{pin_projection['bracket_screen_s']})"
    )
    return pin_projection


def _v2_authenticate_bracket_binding(
    *,
    producer: Mapping[str, Any],
    inputs: V2ProducerInputs,
    ledger_snapshot: Any,
) -> tuple[Any, Any, Mapping[str, Any]]:
    label = f"producer {producer['plan']['plan_id']!r}"
    binding = inputs.bracket_binding
    if not isinstance(binding, Mapping):
        raise MintError(
            f"postcollection_evidence_mismatch: {label} bracket binding is malformed"
        )
    expected = _v2_verdict_bracket(producer=producer, inputs=inputs)
    _v2_crosscheck_binding_against_verdict(binding, expected)
    resolved = validate_calibration_bracket_binding(
        binding,
        ledger_snapshot,
        window_id=expected.window_id,
        plan_id=producer["plan"]["plan_id"],
        plan_sha256=producer["plan"]["sha256"],
        evidence_root_id=producer["evidence_root_id"],
        runs_root=inputs.evidence_root,
    )
    if resolved is None:
        raise MintError(
            f"postcollection_evidence_mismatch: {label} bracket binding failed authenticated validation"
        )
    pre, post = resolved
    return pre, post, _v2_allowance_projection(inputs, pre, post)


def _v2_gate_producer_inventory(
    producer: Mapping[str, Any],
    inputs: V2ProducerInputs,
) -> None:
    plan = producer["plan"]
    plan_id = plan["plan_id"]
    if inputs.plan_sha256 != plan["sha256"]:
        raise MintError(f"producer {plan_id!r}: calibration plan sha256 mismatch")
    if inputs.plan_declared_sha256 != plan["declared_sha256"]:
        raise MintError(f"producer {plan_id!r}: declared plan sha256 mismatch")
    if inputs.plan_sidecar_sha256 != plan["sidecar_sha256"]:
        raise MintError(f"producer {plan_id!r}: plan sidecar sha256 mismatch")
    if inputs.plan.get("plan_id") != plan_id or inputs.plan.get(
        "calibration_scope"
    ) != plan["declared_calibration_scope"]:
        raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
    acceptance = inputs.calibration_acceptance
    acceptance_pins = producer["calibration_acceptance"]
    if (
        not isinstance(acceptance, Mapping)
        or acceptance.get("acceptance_id") != acceptance_pins["acceptance_id"]
        or inputs.calibration_acceptance_sha256
        != acceptance_pins["artifact_sha256"]
        or acceptance.get("derivation_sha256")
        != acceptance_pins["derivation_sha256"]
        or acceptance.get("schema_version")
        != acceptance_pins["derivation_rule_id"]
    ):
        raise MintError(
            f"producer {plan_id!r}: calibration acceptance evidence mismatch"
        )
    components = [
        component
        for cell in inputs.cells.values()
        for component in (cell.absolute, cell.comparative)
    ]
    if not components:
        raise MintError(f"producer {plan_id!r}: no authenticated components")
    extraction_sha256s = {component.spec_sha256 for component in components}
    if extraction_sha256s != {producer["extraction_spec"]["sha256"]}:
        raise MintError(f"producer {plan_id!r}: extraction spec inventory mismatch")
    unique_members = {
        member.bundle_id for component in components for member in component.members
    }
    governed_spec_members = {
        member
        for component in components
        for member in _v2_spec_member_ids(component.spec)
    }
    if (
        len(governed_spec_members)
        != producer["extraction_spec"]["member_count"]
        or not unique_members.issubset(governed_spec_members)
    ):
        raise MintError(f"producer {plan_id!r}: extraction member inventory mismatch")
    observed_runtime_configs: list[Mapping[str, str]] = []
    for component in components:
        try:
            observed_runtime_configs.append(
                derive_model_runtime_config(
                    component.source_regime.get("stack_identity", {}),
                    component.scientific_config_identity_sha256,
                )
            )
        except ValueError as exc:
            raise MintError(
                f"producer {plan_id!r}: shared model/runtime/config derivation failed: {exc}"
            ) from exc
    model_hashes = {
        observed["model_artifact_sha256"] for observed in observed_runtime_configs
    }
    runtime_hashes = {
        observed["runtime_identity_sha256"] for observed in observed_runtime_configs
    }
    config_hashes = {
        observed["config_set_sha256"] for observed in observed_runtime_configs
    }
    runtime_pins = producer["model_runtime_config"]
    if model_hashes != {runtime_pins["model_artifact_sha256"]}:
        raise MintError(f"producer {plan_id!r}: model artifact inventory mismatch")
    if runtime_hashes != {runtime_pins["runtime_identity_sha256"]}:
        raise MintError(f"producer {plan_id!r}: runtime identity inventory mismatch")
    if config_hashes != {runtime_pins["config_set_sha256"]}:
        raise MintError(f"producer {plan_id!r}: config-set inventory mismatch")


def _v2_gate_postcollection(
    *,
    producer: Mapping[str, Any],
    cell_pins: Mapping[str, Any],
    cell_inputs: V2CellComponents,
    producer_inputs: V2ProducerInputs,
    ledger_snapshot: Any,
) -> V2CellRecomputation:
    post = cell_pins["postcollection"]
    if (
        producer_inputs.authenticated_pre_observation is not None
        and producer_inputs.authenticated_post_observation is not None
        and producer_inputs.calibration_allowance_projection is not None
    ):
        expected_bracket = _v2_verdict_bracket(
            producer=producer,
            inputs=producer_inputs,
        )
        _v2_crosscheck_binding_against_verdict(
            producer_inputs.bracket_binding,
            expected_bracket,
        )
        pre = producer_inputs.authenticated_pre_observation
        post_observation = producer_inputs.authenticated_post_observation
        for index, observation in enumerate((pre, post_observation)):
            role = ("pre", "post")[index]
            observed_endpoint = (
                _mapping_attribute(observation, "attempt_id"),
                _mapping_attribute(observation, "receipt_digest"),
                _mapping_attribute(observation, "content_id"),
            )
            expected_endpoint = (
                expected_bracket.endpoint_attempt_ids[index],
                expected_bracket.endpoint_receipt_sha256s[index],
                expected_bracket.endpoint_content_sha256s[index],
            )
            if observed_endpoint != expected_endpoint:
                raise MintError(
                    "postcollection_evidence_mismatch: verdict/bracket "
                    f"cross-check refused authenticated {role} endpoint"
                )
        allowance_projection = _v2_allowance_projection(
            producer_inputs,
            pre,
            post_observation,
        )
        if dict(producer_inputs.calibration_allowance_projection) != dict(
            allowance_projection
        ):
            raise MintError(
                "postcollection_evidence_mismatch: cached calibration "
                "allowance differs from authenticated endpoint derivation"
            )
    else:
        pre, post_observation, allowance_projection = (
            _v2_authenticate_bracket_binding(
                producer=producer,
                inputs=producer_inputs,
                ledger_snapshot=ledger_snapshot,
            )
        )

    # Steps 8-9: the report is a closed cache. It may contain only governed
    # extractor keys, and its cached component results must match a fresh
    # calculation from authenticated member values, widths, and allowances.
    actual_components = (cell_inputs.absolute, cell_inputs.comparative)
    for component in actual_components:
        profile_errors = validate_d117_mint_consumption_report(component.report)
        if profile_errors:
            raise MintError(
                "postcollection_evidence_mismatch: closed D-117 extraction "
                f"report profile refused: {profile_errors[0]}"
            )
    report_hashes = {component.report_sha256 for component in actual_components}
    if len(report_hashes) != 1:
        raise MintError(
            "postcollection_evidence_mismatch: component extraction reports disagree"
        )

    core = _fresh_original_core()
    absolute_estimate = core.absolute_false_effect_floor(
        [member.metric_value_j for member in cell_inputs.absolute.members],
        admissible_half_widths_j=cell_inputs.absolute.widths_j,
    )
    absolute_record = core.build_absolute_record(
        absolute_estimate,
        core._absolute_observations(cell_inputs.absolute),
        consumption_semantics_id=cell_inputs.absolute.consumption_semantics_id,
        whole_window_drift_allowance=(
            cell_inputs.absolute.whole_window_drift_allowance
        ),
    )
    try:
        recomputed = mint_estimator.recompute_comparative_estimate(
            core=core,
            comparative_component=cell_inputs.comparative,
            runs_root=producer_inputs.evidence_root,
            calibration_acceptance=producer_inputs.calibration_acceptance,
            calibration_acceptance_sha256=(
                producer_inputs.calibration_acceptance_sha256
            ),
            calibration_allowance_projection=allowance_projection,
            declared_calibration_scope=producer["plan"][
                "declared_calibration_scope"
            ],
            calibration_ledger_snapshot=ledger_snapshot,
            calibration_bracket_binding=producer_inputs.bracket_binding,
        )
    except ValueError as exc:
        raise MintError(
            "postcollection_evidence_mismatch: comparative estimator "
            f"recomputation refused: {exc}"
        ) from exc
    report_widths = cell_inputs.comparative.cell.get("floor", {}).get(
        "admissible_half_widths_j"
    )
    try:
        widths_match = (
            isinstance(report_widths, list)
            and len(report_widths) == len(recomputed.exact_widths_j)
            and all(
                not isinstance(observed, bool)
                and isinstance(observed, int | float)
                and Decimal(str(observed)) == Decimal(str(expected))
                for observed, expected in zip(
                    report_widths,
                    recomputed.exact_widths_j,
                    strict=True,
                )
            )
        )
    except InvalidOperation:
        widths_match = False
    if not widths_match:
        raise MintError(
            "postcollection_evidence_mismatch: extraction-report comparative "
            "widths differ exactly from the authenticated spec-selected estimator"
        )
    comparative_record = recomputed.comparative_record
    absolute_value = absolute_record.get("drift_widened_guarded_floor_j")
    comparative_value = comparative_record.get("drift_widened_guarded_floor_j")
    if any(
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        for value in (absolute_value, comparative_value)
    ):
        raise MintError(
            "postcollection_evidence_mismatch: recomputed floors are not finite"
        )
    for component, expected in zip(
        actual_components,
        (absolute_value, comparative_value),
    ):
        cached = component.cell.get("floor", {}).get(
            "drift_widened_guarded_floor_j"
        )
        operative = component.cell.get("operative_floor_j")
        try:
            cached_matches = (
                not isinstance(cached, bool)
                and isinstance(cached, int | float)
                and Decimal(str(cached)) == Decimal(str(expected))
            )
            operative_matches = (
                not isinstance(operative, bool)
                and isinstance(operative, int | float)
                and Decimal(str(operative)) == Decimal(str(expected))
            )
        except InvalidOperation:
            cached_matches = operative_matches = False
        if not cached_matches or not operative_matches:
            raise MintError(
                "postcollection_evidence_mismatch: report cell floor differs "
                f"from authenticated {component.kind} member evidence"
            )

    absolute_decimal = Decimal(str(absolute_value))
    comparative_decimal = Decimal(str(comparative_value))
    operative_decimal = max(absolute_decimal, comparative_decimal)
    projection = {
        "absolute_evaluation_basis_sha256": (
            cell_inputs.absolute.whole_window_evaluation_basis_sha256
        ),
        "absolute_evaluation_basis_members": (
            cell_inputs.absolute.evaluation_basis_member_count
        ),
        "comparative_evaluation_basis_sha256": (
            cell_inputs.comparative.whole_window_evaluation_basis_sha256
        ),
        "comparative_evaluation_basis_members": (
            cell_inputs.comparative.evaluation_basis_member_count
        ),
        "pre_receipt_sha256": _mapping_attribute(pre, "receipt_digest"),
        "pre_content_sha256": _mapping_attribute(pre, "content_id"),
        "post_receipt_sha256": _mapping_attribute(
            post_observation, "receipt_digest"
        ),
        "post_content_sha256": _mapping_attribute(post_observation, "content_id"),
        "bracket_binding_sha256": producer_inputs.bracket_binding_sha256,
        "terminal_ledger_head_sha256": (
            _mapping_attribute(ledger_snapshot, "committed_head_digest")
            or _mapping_attribute(ledger_snapshot, "head_digest")
        ),
        **dict(allowance_projection),
        "extraction_report_sha256": next(iter(report_hashes)),
        "absolute_floor_full_precision": str(absolute_decimal),
        "comparative_floor_full_precision": str(comparative_decimal),
        "operative_floor_full_precision": str(operative_decimal),
        "absolute_floor_six_decimal": format(
            absolute_decimal.quantize(
                _SIX_DECIMAL_QUANTUM, rounding=ROUND_HALF_EVEN
            ),
            ".6f",
        ),
        "comparative_floor_six_decimal": format(
            comparative_decimal.quantize(
                _SIX_DECIMAL_QUANTUM, rounding=ROUND_HALF_EVEN
            ),
            ".6f",
        ),
        "operative_floor_six_decimal": format(
            operative_decimal.quantize(
                _SIX_DECIMAL_QUANTUM, rounding=ROUND_HALF_EVEN
            ),
            ".6f",
        ),
    }

    # Step 10: compare every independently frozen U10 literal. There is no
    # fill/default path; the closed pinset parser has already required all.
    for field in (
        "pre_receipt_sha256",
        "post_receipt_sha256",
        "pre_content_sha256",
        "post_content_sha256",
        "bracket_binding_sha256",
        "terminal_ledger_head_sha256",
        "observed_drift_s",
        "allowance_rule",
        "bracket_screen_s",
        "applied_allowance_s",
        "allowance_embedding_count",
        "absolute_evaluation_basis_sha256",
        "absolute_evaluation_basis_members",
        "comparative_evaluation_basis_sha256",
        "comparative_evaluation_basis_members",
        "extraction_report_sha256",
        "absolute_floor_full_precision",
        "comparative_floor_full_precision",
        "operative_floor_full_precision",
        "absolute_floor_six_decimal",
        "comparative_floor_six_decimal",
        "operative_floor_six_decimal",
    ):
        pinned = post[field]
        evidenced = projection[field]
        _require_postcollection_evidence_equal(
            field,
            pinned,
            evidenced,
            source="domain-owned verification projection",
        )
    return V2CellRecomputation(
        estimator_path=recomputed.estimator_path,
        comparative_blocks=tuple(recomputed.comparative_blocks),
        comparative_estimate=recomputed.estimate,
        comparative_widths_j=tuple(recomputed.exact_widths_j),
        comparative_record=copy.deepcopy(dict(recomputed.comparative_record)),
        block_inputs=(
            tuple(recomputed.block_inputs)
            if getattr(recomputed, "block_inputs", None) is not None
            else None
        ),
        calibration_bracket=(
            copy.deepcopy(dict(getattr(recomputed, "calibration_bracket")))
            if getattr(recomputed, "calibration_bracket", None) is not None
            else None
        ),
        shared_edge_bound_s=getattr(recomputed, "shared_edge_bound_s", None),
    )


def _v2_allowed_families(
    supplied: Sequence[Mapping[str, Any]],
    pins: Sequence[Mapping[str, Any]],
    *,
    label: str,
) -> list[Mapping[str, Any]]:
    expected = [
        (row["condition_family_id"], row["condition_family_sha256"])
        for row in pins
    ]
    observed = []
    normalized = []
    from joulewise.detection_floor import (
        CONDITION_FAMILY_DOMAIN,
        canonical_domain_sha256,
    )

    for index, row in enumerate(supplied):
        if not isinstance(row, Mapping):
            raise MintError(f"{label}[{index}] must be an object")
        definition = row.get("condition_family_definition")
        family_id = row.get("condition_family_id")
        family_sha256 = row.get("condition_family_sha256")
        if not isinstance(definition, Mapping) or not isinstance(family_id, str):
            raise MintError(f"{label}[{index}] is incomplete")
        if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition) != (
            family_sha256
        ):
            raise MintError(f"{label}[{index}] condition-family hash mismatch")
        observed.append((family_id, family_sha256))
        normalized.append(dict(row))
    if observed != expected:
        raise MintError(f"{label} does not match the transport allowlist pins")
    return normalized


def _v2_pre_registration_gate(
    *,
    core: ModuleType,
    producer: Mapping[str, Any],
    cell_pins: Mapping[str, Any],
    plan: Mapping[str, Any],
    absolute: Any,
    comparative: Any,
) -> Mapping[str, Any]:
    plan_pins = producer["plan"]
    if absolute.order_manifest.get("calibration_plan_sha256") != plan_pins[
        "sha256"
    ] or comparative.order_manifest.get("calibration_plan_sha256") != plan_pins[
        "sha256"
    ]:
        raise MintError("v2 pre-registration gate: order-manifest plan sha mismatch")
    if absolute.order_manifest.get("plan_id") != plan.get(
        "plan_id"
    ) or comparative.order_manifest.get("plan_id") != plan.get("plan_id"):
        raise MintError("v2 pre-registration gate: order-manifest plan id mismatch")
    absolute_binding = core._definition_binding(absolute)
    comparative_bindings = comparative.spec_cell.get(
        "condition_family_definitions"
    )
    if (
        not isinstance(comparative_bindings, Mapping)
        or comparative_bindings.get("A") != comparative_bindings.get("B")
        or absolute_binding != comparative_bindings.get("A")
        or absolute_binding.get("condition_family_id")
        != cell_pins["condition_family_id"]
        or absolute_binding.get("condition_family_sha256")
        != cell_pins["condition_family_sha256"]
        or absolute_binding.get("condition_family_definition", {}).get(
            "abba_alias_relation"
        )
        != "A_equals_B"
    ):
        raise MintError(
            "v2 pre-registration gate: components are not the pinned A==B null"
        )
    if not core._diagnostics_are_nonpublishing(
        absolute.report
    ) or not core._diagnostics_are_nonpublishing(comparative.report):
        raise MintError(
            "v2 pre-registration gate: diagnostic floor is marked as published"
        )
    if absolute.scientific_config_identity_sha256 != (
        comparative.scientific_config_identity_sha256
    ):
        raise MintError(
            "v2 pre-registration gate: scientific config identity mismatch"
        )
    if absolute.source_regime["stack_identity_sha256"] != (
        comparative.source_regime["stack_identity_sha256"]
    ):
        raise MintError("v2 pre-registration gate: stack identity mismatch")
    if absolute.backend != comparative.backend:
        raise MintError("v2 pre-registration gate: telemetry backend mismatch")
    return absolute_binding


def _common_minted_artifact_launch_lineage(
    artifacts: Sequence[Mapping[str, Any]],
    *,
    label: str,
) -> Mapping[str, Any] | None:
    """Require component artifacts to omit lineage together or carry one value."""

    lineages: list[Mapping[str, Any]] = []
    for artifact in artifacts:
        provenance = artifact.get("provenance")
        lineage = (
            provenance.get("launch_lineage")
            if isinstance(provenance, Mapping)
            else None
        )
        if lineage is None:
            continue
        if not isinstance(lineage, Mapping):
            raise MintError(
                f"launch_consumption_invalid: {label} launch lineage is not an object"
            )
        lineages.append(lineage)
    if lineages and len(lineages) != len(artifacts):
        raise MintError(
            f"launch_lineage_conflict: {label} mixes marker-bearing and legacy provenance"
        )
    if len({_canonical_json_sha256(lineage) for lineage in lineages}) > 1:
        raise MintError(
            f"launch_lineage_conflict: {label} does not carry one authenticated lineage"
        )
    return copy.deepcopy(dict(lineages[0])) if lineages else None


def _mint_v2_cell_artifact(
    *,
    core: ModuleType,
    producer: Mapping[str, Any],
    cell_pins: Mapping[str, Any],
    plan: Mapping[str, Any],
    project_commit: str,
    project_tree_state: str,
    origin_main_contains_head: bool | None,
    head_pin_commit_contained_in_origin_main: bool | None,
    absolute: Any,
    comparative: Any,
    recomputation: V2CellRecomputation,
    calibration_ledger_snapshot: Any,
) -> Mapping[str, Any]:
    """Construct one v2 cell without invoking either v1 literal derivation."""

    plan_pins = producer["plan"]
    binding = _v2_pre_registration_gate(
        core=core,
        producer=producer,
        cell_pins=cell_pins,
        plan=plan,
        absolute=absolute,
        comparative=comparative,
    )
    launch_lineage = core._common_authenticated_launch_lineage(
        absolute,
        comparative,
    )
    relative_plan = core._safe_relative_posix(
        plan_pins["relative_path"], "calibration_plan.relative_path"
    )
    absolute_estimate = core.absolute_false_effect_floor(
        [member.metric_value_j for member in absolute.members],
        admissible_half_widths_j=absolute.widths_j,
    )
    absolute_record = core.build_absolute_record(
        absolute_estimate,
        core._absolute_observations(absolute),
        consumption_semantics_id=absolute.consumption_semantics_id,
        whole_window_drift_allowance=absolute.whole_window_drift_allowance,
    )
    comparative_record = copy.deepcopy(dict(recomputation.comparative_record))
    if tuple(comparative_record.get("admissible_half_widths_j", ())) != (
        recomputation.comparative_widths_j
    ):
        raise MintError("frozen v2 comparative recomputation changed before construction")
    definition = binding["condition_family_definition"]
    if core.canonical_domain_sha256(
        core.CONDITION_FAMILY_DOMAIN, definition
    ) != cell_pins["condition_family_sha256"]:
        raise MintError("condition-family definition hash changed after v2 gate")
    cell = core.build_floor_cell(
        cell_id=cell_pins["cell_id"],
        key={
            "backend": absolute.backend,
            "metric": cell_pins["metric"],
            "window_class": cell_pins["window_class"],
            "condition_family_id": cell_pins["condition_family_id"],
            "condition_family_definition": definition,
            "condition_family_sha256": cell_pins["condition_family_sha256"],
        },
        eligibility={
            "use_role": "primary_claim_gate",
            "minimum_claim_n": cell_pins["absolute"]["expected_n"],
            "status": "claim_ready",
            "claim_usable": True,
            "reason_codes": [],
        },
        absolute=absolute_record,
        comparative=comparative_record,
        transport_group_id=cell_pins["transport_group_id"],
        provenance={
            "absolute": core._component_provenance(absolute),
            "comparative": core._component_provenance(comparative),
        },
    )
    group = core.build_transport_group(
        transport_group_id=cell_pins["transport_group_id"],
        backend=absolute.backend,
        metric=cell_pins["metric"],
        window_class=cell_pins["window_class"],
        stack_identity=cell["source_regime"]["stack_identity"],
        source_cells=[cell],
        allowed_consumer_condition_families=[
            {
                "condition_family_id": cell_pins["condition_family_id"],
                "condition_family_definition": definition,
                "condition_family_sha256": cell_pins[
                    "condition_family_sha256"
                ],
            }
        ],
    )
    provenance = {
        "calibration_plan": {
            "plan_id": plan["plan_id"],
            "declared_calibration_scope": plan_pins[
                "declared_calibration_scope"
            ],
            "relative_path": relative_plan,
            "sha256": plan_pins["sha256"],
        },
        "mint_tool_version": V2_MINT_TOOL_VERSION,
        "assurance": copy.deepcopy(V2_ASSURANCE_PROFILE),
        "implementation": {
            "project_commit": project_commit,
            "project_tree_state": project_tree_state,
            "mint_commit_contained_in_origin_main": (
                origin_main_contains_head
            ),
            "head_pin_commit_contained_in_origin_main": (
                head_pin_commit_contained_in_origin_main
            ),
            "python_package": "joulewise",
        },
    }
    custody_store_provenance = core._expected_custody_store_provenance(
        calibration_ledger_snapshot
    )
    if custody_store_provenance is not None:
        provenance["calibration_custody_store"] = dict(
            custody_store_provenance
        )
    if launch_lineage is not None:
        provenance["launch_lineage"] = copy.deepcopy(dict(launch_lineage))
    artifact = core.build_floor_artifact(
        artifact_id=producer["component_artifact"]["artifact_id"],
        calibration_scope=plan_pins["artifact_calibration_scope"],
        source_class="prospective",
        provenance=provenance,
        cells=[cell],
        transport_groups=[group],
    )
    if artifact["cells"][0]["floor_gate_j"] != group["composed_floor_gate_j"]:
        raise MintError("v2 post-construction transport headline mismatch")
    errors = core.validate_floor_artifact(artifact)
    if errors:
        raise MintError(f"constructed v2 cell artifact is invalid: {errors[0]}")
    core._assert_path_independent(artifact)
    return artifact


def _build_v2_artifacts(
    *,
    pinset: V2Pinset,
    pinset_path: Path,
    pinset_sha256: str,
    producer_inputs: Mapping[str, V2ProducerInputs],
    calibration_ledger_snapshot: Any,
    project_commit: str,
    project_tree_state: str,
    origin_main_contains_head: bool | None = False,
    head_pin_commit_contained_in_origin_main: bool | None = False,
    recomputation_sink: dict[str, V2CellRecomputation] | None = None,
) -> tuple[Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
    """Build the combined artifact and its two deterministic components.

    This helper deliberately does not compare the supplied producer/component
    hashes; it is the deterministic authoring primitive used to freeze those
    hashes.  The public mint entry point performs every comparison before it
    returns an artifact.
    """

    if re.fullmatch(r"[0-9a-f]{40}", project_commit) is None:
        raise MintError("project_commit must be 40 lowercase hex chars")
    if project_tree_state not in {"clean", "dirty"}:
        raise MintError("project_tree_state must be 'clean' or 'dirty'")
    component_artifacts: list[Mapping[str, Any]] = []
    all_cells: list[Mapping[str, Any]] = []
    all_groups: list[Mapping[str, Any]] = []
    producer_plan_records: list[Mapping[str, Any]] = []

    for producer_index, producer in enumerate(pinset.value["producer_plans"]):
        plan_pins = producer["plan"]
        plan_id = plan_pins["plan_id"]
        inputs = producer_inputs.get(plan_id)
        if inputs is None:
            raise MintError(f"missing authenticated producer inputs for {plan_id!r}")
        if set(inputs.cells) != {"decode", "prefill"}:
            raise MintError(
                f"producer inputs for {plan_id!r} must contain decode and prefill"
            )
        if inputs.plan.get("plan_id") != plan_id:
            raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
        producer_cells: list[Mapping[str, Any]] = []
        producer_groups: list[Mapping[str, Any]] = []
        producer_cell_artifacts: list[Mapping[str, Any]] = []
        recomputations: dict[str, V2CellRecomputation] = {}
        # Authenticate every spec, member, config, order, and producer pin
        # before the first per-cell estimator selection can execute.
        for cell_index, cell_pins in enumerate(producer["cells"]):
            role = cell_pins["role"]
            cell_inputs = inputs.cells[role]
            _v2_gate_component(
                cell_inputs.absolute,
                cell_pins["absolute"],
                label=f"producer[{producer_index}].{role}.absolute",
                metric=cell_pins["metric"],
                window_class=cell_pins["window_class"],
            )
            _v2_gate_component(
                cell_inputs.comparative,
                cell_pins["comparative"],
                label=f"producer[{producer_index}].{role}.comparative",
                metric=cell_pins["metric"],
                window_class=cell_pins["window_class"],
            )
        _v2_gate_producer_inventory(producer, inputs)

        # Finish steps 8-10 for every cell before any artifact construction.
        for cell_pins in producer["cells"]:
            role = cell_pins["role"]
            recomputations[role] = _v2_gate_postcollection(
                producer=producer,
                cell_pins=cell_pins,
                cell_inputs=inputs.cells[role],
                producer_inputs=inputs,
                ledger_snapshot=calibration_ledger_snapshot,
            )
            if recomputation_sink is not None:
                recomputation_sink[cell_pins["cell_id"]] = recomputations[role]

        # Step 11 begins only after the complete producer projection matches.
        for cell_index, cell_pins in enumerate(producer["cells"]):
            role = cell_pins["role"]
            cell_inputs = inputs.cells[role]
            configured_pins = _v2_mint_pinset(producer, cell_pins)
            core = _configured_core(
                configured_pins,
                pinset_path=pinset_path,
                expected_pinset_sha256=pinset_sha256,
            )
            try:
                cell_artifact = _mint_v2_cell_artifact(
                    core=core,
                    producer=producer,
                    cell_pins=cell_pins,
                    plan=inputs.plan,
                    absolute=cell_inputs.absolute,
                    comparative=cell_inputs.comparative,
                    recomputation=recomputations[role],
                    calibration_ledger_snapshot=(
                        calibration_ledger_snapshot
                    ),
                    project_commit=project_commit,
                    project_tree_state=project_tree_state,
                    origin_main_contains_head=origin_main_contains_head,
                    head_pin_commit_contained_in_origin_main=(
                        head_pin_commit_contained_in_origin_main
                    ),
                )
            except core.MintError as exc:
                raise MintError(str(exc)) from exc
            cell = copy.deepcopy(cell_artifact["cells"][0])
            group = copy.deepcopy(cell_artifact["transport_groups"][0])
            allowed = _v2_allowed_families(
                cell_inputs.allowed_consumer_condition_families,
                cell_pins["allowed_consumer_condition_families"],
                label=f"producer[{producer_index}].cells[{cell_index}].allowlist",
            )
            group["allowed_consumer_condition_families"] = allowed
            producer_cells.append(cell)
            producer_groups.append(group)
            producer_cell_artifacts.append(cell_artifact)

        producer_launch_lineage = _common_minted_artifact_launch_lineage(
            producer_cell_artifacts,
            label=f"producer {plan_id!r} cells",
        )
        first_cell_artifact = producer_cell_artifacts[0]
        component = {
            **copy.deepcopy(first_cell_artifact),
            "artifact_id": producer["component_artifact"]["artifact_id"],
            "cells": producer_cells,
            "transport_groups": producer_groups,
        }
        if producer_launch_lineage is not None:
            component["provenance"]["launch_lineage"] = (
                producer_launch_lineage
            )
        component_errors = validate_floor_artifact(
            artifact=component,
            pinset_path=pinset_path,
            pinset_sha256=pinset_sha256,
            _skip_v2_hash_binding=True,
        )
        if component_errors:
            raise MintError(
                f"constructed v2 component artifact is invalid: {component_errors[0]}"
            )
        component_artifacts.append(component)
        all_cells.extend(copy.deepcopy(producer_cells))
        all_groups.extend(copy.deepcopy(producer_groups))
        producer_plan_records.append(
            {
                "plan_id": plan_id,
                "declared_calibration_scope": plan_pins[
                    "declared_calibration_scope"
                ],
                "relative_path": plan_pins["relative_path"],
                "sha256": plan_pins["sha256"],
            }
        )

    aggregate = pinset.value["aggregate"]
    implementation = copy.deepcopy(
        component_artifacts[0]["provenance"]["implementation"]
    )
    aggregate_provenance = {
        "calibration_plan": {
            "plan_id": aggregate["plan_set_id"],
            "declared_calibration_scope": "production_window",
            "relative_path": Path(pinset_path).name,
            "sha256": aggregate["producer_set_sha256"],
        },
        "producer_calibration_plans": producer_plan_records,
        "mint_tool_version": V2_MINT_TOOL_VERSION,
        "assurance": copy.deepcopy(V2_ASSURANCE_PROFILE),
        "implementation": implementation,
    }
    custody_store_provenance = component_artifacts[0]["provenance"].get(
        "calibration_custody_store"
    )
    if custody_store_provenance is not None:
        aggregate_provenance["calibration_custody_store"] = copy.deepcopy(
            custody_store_provenance
        )
    aggregate_launch_lineage = _common_minted_artifact_launch_lineage(
        component_artifacts,
        label="aggregate components",
    )
    if aggregate_launch_lineage is not None:
        aggregate_provenance["launch_lineage"] = aggregate_launch_lineage
    artifact = {
        **copy.deepcopy(component_artifacts[0]),
        "artifact_id": aggregate["artifact_id"],
        "calibration_scope": aggregate["calibration_scope"],
        "source_class": aggregate["source_class"],
        "provenance": aggregate_provenance,
        "cells": all_cells,
        "transport_groups": all_groups,
    }
    errors = validate_floor_artifact(
        artifact=artifact,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
        _skip_v2_hash_binding=True,
    )
    if errors:
        raise MintError(f"constructed v2 aggregate artifact is invalid: {errors[0]}")
    return artifact, tuple(component_artifacts)


def _validate_v2_artifact_binding(
    artifact: Mapping[str, Any],
    pinset: V2Pinset,
) -> list[str]:
    errors: list[str] = []
    value = pinset.value
    aggregate = value["aggregate"]
    try:
        _validate_v2_pin_hashes(pinset)
    except MintError as exc:
        errors.append(f"artifact.pinset: {exc}")
    if artifact.get("artifact_id") != aggregate["artifact_id"]:
        errors.append("artifact: aggregate artifact_id mismatch")
    provenance = artifact.get("provenance")
    expected_producer_plans = [
        {
            "plan_id": producer["plan"]["plan_id"],
            "declared_calibration_scope": producer["plan"][
                "declared_calibration_scope"
            ],
            "relative_path": producer["plan"]["relative_path"],
            "sha256": producer["plan"]["sha256"],
        }
        for producer in value["producer_plans"]
    ]
    if not isinstance(provenance, Mapping):
        errors.append("artifact.provenance: v2 aggregate provenance is missing")
    else:
        expected_aggregate_plan = {
            "plan_id": aggregate["plan_set_id"],
            "declared_calibration_scope": "production_window",
            "relative_path": Path("pinset.json").name,
            "sha256": aggregate["producer_set_sha256"],
        }
        aggregate_plan = provenance.get("calibration_plan")
        if not isinstance(aggregate_plan, Mapping) or any(
            aggregate_plan.get(field) != expected
            for field, expected in expected_aggregate_plan.items()
            if field != "relative_path"
        ):
            errors.append("artifact.provenance: aggregate plan-set pin mismatch")
        if provenance.get("producer_calibration_plans") != expected_producer_plans:
            errors.append("artifact.provenance: producer plan pins mismatch")
        if provenance.get("mint_tool_version") != V2_MINT_TOOL_VERSION:
            errors.append("artifact.provenance: v2 mint-tool identity mismatch")
    cells = artifact.get("cells")
    groups = artifact.get("transport_groups")
    if not isinstance(cells, list) or not isinstance(groups, list):
        return [*errors, "artifact: v2 cells/transport_groups are not arrays"]
    if [cell.get("cell_id") for cell in cells if isinstance(cell, Mapping)] != (
        aggregate["cell_ids"]
    ):
        errors.append("artifact: four-cell order does not match aggregate pins")
    group_by_id = {
        group.get("transport_group_id"): group
        for group in groups
        if isinstance(group, Mapping)
    }
    cell_by_id = {
        cell.get("cell_id"): cell
        for cell in cells
        if isinstance(cell, Mapping)
    }

    for producer in value["producer_plans"]:
        for cell_pin in producer["cells"]:
            cell = cell_by_id.get(cell_pin["cell_id"])
            if not isinstance(cell, Mapping):
                continue
            key = cell.get("key", {})
            for field in (
                "metric",
                "window_class",
                "condition_family_id",
                "condition_family_sha256",
            ):
                expected = (
                    cell_pin[field]
                    if field in cell_pin
                    else cell_pin.get(field)
                )
                if key.get(field) != expected:
                    errors.append(f"cells[{cell_pin['cell_id']}]: {field} pin mismatch")
            post = cell_pin["postcollection"]
            for artifact_field, pin_field, component_name in (
                (
                    "floor_abs_j",
                    "absolute_floor_full_precision",
                    "absolute",
                ),
                (
                    "floor_cmp_j",
                    "comparative_floor_full_precision",
                    "comparative",
                ),
                (
                    "floor_gate_j",
                    "operative_floor_full_precision",
                    "operative",
                ),
            ):
                actual = cell.get(artifact_field)
                if (
                    isinstance(actual, bool)
                    or not isinstance(actual, int | float)
                    or not math.isfinite(float(actual))
                    or Decimal(str(actual)) != Decimal(post[pin_field])
                ):
                    errors.append(
                        f"cells[{cell_pin['cell_id']}]: {component_name} "
                        "full-precision pin mismatch"
                    )
            cell_provenance = cell.get("provenance", {})
            roots = {
                row.get("evidence_root_id")
                for row in cell_provenance.values()
                if isinstance(row, Mapping)
            }
            if roots != {producer["evidence_root_id"]}:
                errors.append(f"cells[{cell_pin['cell_id']}]: evidence-root pin mismatch")
            group = group_by_id.get(cell_pin["transport_group_id"])
            if not isinstance(group, Mapping) or group.get("source_cell_ids") != [
                cell_pin["cell_id"]
            ]:
                errors.append(
                    f"cells[{cell_pin['cell_id']}]: transport must remain independently stack-scoped"
                )
            elif [
                (row.get("condition_family_id"), row.get("condition_family_sha256"))
                for row in group.get("allowed_consumer_condition_families", [])
                if isinstance(row, Mapping)
            ] != [
                (row["condition_family_id"], row["condition_family_sha256"])
                for row in cell_pin["allowed_consumer_condition_families"]
            ]:
                errors.append(f"cells[{cell_pin['cell_id']}]: transport allowlist mismatch")

            aggregate_entry = next(
                (
                    row
                    for row in aggregate["transport_allowlists"]
                    if row["transport_group_id"]
                    == cell_pin["transport_group_id"]
                ),
                None,
            )
            if not isinstance(aggregate_entry, Mapping) or aggregate_entry[
                "allowed_consumer_condition_families"
            ] != cell_pin["allowed_consumer_condition_families"]:
                errors.append(
                    f"cells[{cell_pin['cell_id']}]: aggregate transport allowlist mismatch"
                )

    if isinstance(provenance, Mapping):
        for producer, component_pin in zip(
            value["producer_plans"], aggregate["component_artifacts"]
        ):
            producer_cell_ids = [cell["cell_id"] for cell in producer["cells"]]
            producer_group_ids = [
                cell["transport_group_id"] for cell in producer["cells"]
            ]
            component = copy.deepcopy(dict(artifact))
            component["artifact_id"] = component_pin["artifact_id"]
            component["provenance"] = {
                "calibration_plan": expected_producer_plans[
                    value["producer_plans"].index(producer)
                ],
                "mint_tool_version": V2_MINT_TOOL_VERSION,
                "assurance": copy.deepcopy(V2_ASSURANCE_PROFILE),
                "implementation": copy.deepcopy(
                    provenance.get("implementation")
                ),
            }
            if provenance.get("calibration_custody_store") is not None:
                component["provenance"]["calibration_custody_store"] = (
                    copy.deepcopy(provenance["calibration_custody_store"])
                )
            component["cells"] = [
                copy.deepcopy(cell_by_id[cell_id])
                for cell_id in producer_cell_ids
                if cell_id in cell_by_id
            ]
            component["transport_groups"] = [
                copy.deepcopy(group_by_id[group_id])
                for group_id in producer_group_ids
                if group_id in group_by_id
            ]
            if len(component["cells"]) != 2 or len(
                component["transport_groups"]
            ) != 2:
                continue
            observed_component_sha256s = (
                _artifact_sha256_containment_variants(component)
            )
            if component_pin["sha256"] not in observed_component_sha256s:
                errors.append(
                    "artifact: component artifact hash mismatch for "
                    f"{component_pin['plan_id']!r}"
                )
    return errors


def mint_multi_cell_authenticated_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    producer_inputs: Mapping[str, V2ProducerInputs],
    calibration_ledger_snapshot: Any,
    project_commit: str,
    project_tree_state: str,
) -> Mapping[str, Any]:
    """Mint the D-117 two-plan/four-cell artifact from authenticated inputs."""

    loaded = load_pinset(pinset_path, pinset_sha256)
    if not isinstance(loaded, V2Pinset):
        raise MintError("multi-cell mint requires a final v2 pinset")
    _validate_v2_pin_hashes(loaded)
    artifact, components = _build_v2_artifacts(
        pinset=loaded,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
        producer_inputs=producer_inputs,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
        project_commit=project_commit,
        project_tree_state=project_tree_state,
    )
    for index, (component, expected) in enumerate(
        zip(components, loaded.value["aggregate"]["component_artifacts"])
    ):
        observed = _artifact_sha256(component)
        if expected["sha256"] not in _artifact_sha256_containment_variants(
            component
        ):
            raise MintError(
                "aggregate/component hash mismatch: component artifact "
                f"{index} expected {expected['sha256']}, observed {observed}"
            )
    errors = validate_floor_artifact(
        artifact=artifact,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
    )
    if errors:
        raise MintError(f"constructed v2 artifact is invalid: {errors[0]}")
    return artifact


def _load_v2_input_manifest(path: Path) -> Mapping[str, Any]:
    try:
        raw = read_authentication_input(
            path, grammar="json", label="v2 input manifest"
        )
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(
            f"v2 input manifest cannot be read: {exc.strerror or type(exc).__name__}"
        ) from exc
    value = _strict_json_value(raw, "v2 input manifest")
    root = _object(
        value,
        "v2 input manifest",
        {
            "schema_version",
            "calibration_acceptance",
            "calibration_ledger",
            "calibration_ledger_head_pin",
            "producer_plans",
        },
    )
    if root["schema_version"] != "joulewise.floor_mint_inputs.v2":
        raise MintError(
            "v2 input manifest.schema_version must equal "
            "'joulewise.floor_mint_inputs.v2'"
        )
    if not isinstance(root["producer_plans"], list):
        raise MintError("v2 input manifest.producer_plans must be an array")
    return root


def _v2_component_input_paths(
    value: object,
    label: str,
) -> ComponentInputs:
    row = _object(
        value,
        label,
        {"evidence_root", "report", "spec", "order_manifest"},
    )
    return ComponentInputs(
        evidence_root=Path(_string(row["evidence_root"], f"{label}.evidence_root")),
        report_path=Path(_string(row["report"], f"{label}.report")),
        spec_path=Path(_string(row["spec"], f"{label}.spec")),
        order_manifest_path=Path(
            _string(row["order_manifest"], f"{label}.order_manifest")
        ),
    )


def _load_v2_ledger_snapshot(
    core: ModuleType,
    *,
    acceptance: Mapping[str, Any],
    ledger_path: Path,
    head_pin_path: Path,
    calibration_custody_store: Path | None = None,
) -> Any:
    cutoff = (
        acceptance.get("ledger_cutoff")
        if isinstance(acceptance, Mapping)
        else None
    )
    return core.load_calibration_ledger_snapshot(
        ledger_path=ledger_path,
        head_pin_path=head_pin_path,
        baseline_sequence=(
            cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
        ),
        baseline_digest=(
            cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
        ),
        calibration_custody_store=calibration_custody_store,
    )


def _authenticate_v2_component(
    core: ModuleType,
    paths: Any,
    **kwargs: Any,
) -> Any:
    """Run pinned authentication while deferring one comparative equality.

    The pinned core reconstructs comparative floor widths with the default
    estimator before the generalized v2 producer/spec pins can be gated.  The
    lead-authorized v2 seam defers only that elementwise equality.  Shape and
    finite/nonnegative validation remain here; an unconditional exact
    spec-selected equality replaces the deferred check in postcollection after
    every component and producer pin has passed.
    """

    pinned_width_verifier = core._verify_report_widths

    def defer_comparative_width_equality(
        cell: Mapping[str, Any], widths: Sequence[float]
    ) -> None:
        if cell.get("kind") != "comparative":
            pinned_width_verifier(cell, widths)
            return
        floor = cell.get("floor")
        report_widths = (
            floor.get("admissible_half_widths_j")
            if isinstance(floor, Mapping)
            else None
        )
        if not isinstance(report_widths, list) or len(report_widths) != len(
            widths
        ):
            raise core.MintError(
                "extraction-report widths differ element-for-element from member evidence"
            )
        for value in report_widths:
            core._finite(value, "reported admissible width", nonnegative=True)

    core._verify_report_widths = defer_comparative_width_equality
    try:
        authenticated = core._authenticate_component(paths, **kwargs)
    finally:
        core._verify_report_widths = pinned_width_verifier
    # Only a positively selected common-mode cell needs the equality deferred
    # to the spec-selected postcollection recomputation.  Every default,
    # absent, unknown, or malformed selector retains the pinned verifier's
    # exact default-path refusal, after the authenticated spec cell is known.
    if (
        authenticated.kind == "comparative"
        and authenticated.spec_cell.get("estimator")
        != detection_floor.COMMON_MODE_ESTIMATOR_ID
    ):
        pinned_width_verifier(authenticated.cell, authenticated.widths_j)
    return authenticated


def _authenticate_v2_inputs(
    *,
    pinset: V2Pinset,
    pinset_path: Path,
    pinset_sha256: str,
    input_manifest_path: Path,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None,
    input_manifest: Mapping[str, Any] | None = None,
    calibration_custody_store: Path | None = None,
) -> tuple[
    Mapping[str, V2ProducerInputs],
    Mapping[str, Path],
    Any,
]:
    if active_v2_authentication_session() is None:
        try:
            with V2AuthenticationReadSession():
                return _authenticate_v2_inputs(
                    pinset=pinset,
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha256,
                    input_manifest_path=input_manifest_path,
                    strict_validator=strict_validator,
                    consumption_semantics_id=consumption_semantics_id,
                    input_manifest=input_manifest,
                    calibration_custody_store=calibration_custody_store,
                )
        except V2AuthenticationInputError as exc:
            raise MintError(str(exc)) from exc

    manifest = (
        input_manifest
        if input_manifest is not None
        else _load_v2_input_manifest(input_manifest_path)
    )
    rows = manifest["producer_plans"]
    if len(rows) != len(pinset.value["producer_plans"]):
        raise MintError("v2 input manifest must contain every producer plan exactly once")
    by_plan_id: dict[str, Mapping[str, Any]] = {}
    for index, row_value in enumerate(rows):
        label = f"v2 input manifest.producer_plans[{index}]"
        row = _object(
            row_value,
            label,
            {
                "plan_id",
                "calibration_plan",
                "calibration_plan_sidecar",
                "bracket_binding",
                "cells",
            },
        )
        plan_id = _string(row["plan_id"], f"{label}.plan_id")
        if plan_id in by_plan_id:
            raise MintError("v2 input manifest producer plan ids must be unique")
        by_plan_id[plan_id] = row

    evidence_core = _fresh_original_core()
    acceptance_path = Path(
        _string(
            manifest["calibration_acceptance"],
            "v2 input manifest.calibration_acceptance",
        )
    )
    acceptance_value, acceptance_raw = _strict_json_file(
        acceptance_path, "v2 calibration acceptance"
    )
    if not isinstance(acceptance_value, Mapping):
        raise MintError("v2 calibration acceptance must be an object")
    acceptance = evidence_core.load_calibration_acceptance_bound(acceptance_path)
    if not isinstance(acceptance, Mapping):
        raise MintError("v2 calibration acceptance evidence is not authenticated")
    try:
        acceptance_after = read_authentication_input(
            acceptance_path,
            grammar="json",
            label="v2 calibration acceptance re-read",
        )
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(
            "v2 calibration acceptance cannot be re-read after authentication: "
            f"{exc.strerror or type(exc).__name__}"
        ) from exc
    if acceptance_after != acceptance_raw:
        raise MintError("v2 calibration acceptance changed during authentication")
    acceptance_sha256 = hashlib.sha256(acceptance_raw).hexdigest()
    ledger_path = Path(
        _string(
            manifest["calibration_ledger"],
            "v2 input manifest.calibration_ledger",
        )
    )
    head_pin_path = Path(
        _string(
            manifest["calibration_ledger_head_pin"],
            "v2 input manifest.calibration_ledger_head_pin",
        )
    )
    ledger_raw = _strict_json_lines_file(ledger_path, "v2 calibration ledger")
    head_value, head_raw = _strict_json_file(
        head_pin_path, "v2 calibration ledger head pin"
    )
    if not isinstance(head_value, Mapping):
        raise MintError("v2 calibration ledger head pin must be an object")
    ledger_snapshot = _load_v2_ledger_snapshot(
        evidence_core,
        acceptance=acceptance,
        ledger_path=ledger_path,
        head_pin_path=head_pin_path,
        calibration_custody_store=calibration_custody_store,
    )
    if not bool(getattr(ledger_snapshot, "valid", False)):
        raise MintError("v2 calibration ledger snapshot is not authenticated")
    try:
        ledger_after = read_authentication_input(
            ledger_path,
            grammar="jsonl",
            label="v2 calibration ledger re-read",
        )
        head_after = read_authentication_input(
            head_pin_path,
            grammar="json",
            label="v2 calibration ledger head-pin re-read",
        )
        if ledger_after != ledger_raw or head_after != head_raw:
            raise MintError("v2 calibration ledger changed during authentication")
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError("v2 calibration ledger cannot be re-read") from exc

    result: dict[str, V2ProducerInputs] = {}
    evidence_roots: dict[str, Path] = {}
    for producer_index, producer in enumerate(pinset.value["producer_plans"]):
        plan_id = producer["plan"]["plan_id"]
        manifest_row = by_plan_id.get(plan_id)
        if manifest_row is None:
            raise MintError(f"v2 input manifest is missing producer {plan_id!r}")
        plan_path = Path(
            _string(
                manifest_row["calibration_plan"],
                f"v2 input manifest producer {plan_id}.calibration_plan",
            )
        )
        plan, plan_raw = _strict_json_file(
            plan_path, f"producer {plan_id!r} calibration plan"
        )
        if not isinstance(plan, Mapping):
            raise MintError(f"producer {plan_id!r} calibration plan must be an object")
        if hashlib.sha256(plan_raw).hexdigest() != producer["plan"]["sha256"]:
            raise MintError(f"producer {plan_id!r} calibration plan sha256 mismatch")
        sidecar_path = Path(
            _string(
                manifest_row["calibration_plan_sidecar"],
                f"v2 input manifest producer {plan_id}.calibration_plan_sidecar",
            )
        )
        try:
            sidecar_raw = read_authentication_input(
                sidecar_path,
                grammar="raw",
                label=f"producer {plan_id!r} plan sidecar",
            )
            sidecar_text = sidecar_raw.decode("utf-8")
        except V2AuthenticationInputError as exc:
            raise MintError(str(exc)) from exc
        except OSError as exc:
            raise MintError(
                f"producer {plan_id!r} plan sidecar cannot be read: "
                f"{exc.strerror or type(exc).__name__}"
            ) from exc
        except UnicodeDecodeError as exc:
            raise MintError(
                f"producer {plan_id!r} plan sidecar is not UTF-8"
            ) from exc
        sidecar_parts = sidecar_text.strip().split()
        if (
            len(sidecar_parts) != 2
            or sidecar_parts[0] != producer["plan"]["declared_sha256"]
            or sidecar_parts[0] != hashlib.sha256(plan_raw).hexdigest()
            or sidecar_parts[1] != plan_path.name
            or hashlib.sha256(sidecar_raw).hexdigest()
            != producer["plan"]["sidecar_sha256"]
        ):
            raise MintError(f"producer {plan_id!r} plan sidecar pins mismatch")
        bracket_path = Path(
            _string(
                manifest_row["bracket_binding"],
                f"v2 input manifest producer {plan_id}.bracket_binding",
            )
        )
        bracket_binding, bracket_raw = _strict_json_file(
            bracket_path, f"producer {plan_id!r} bracket binding"
        )
        if not isinstance(bracket_binding, Mapping):
            raise MintError(f"producer {plan_id!r} bracket binding must be an object")
        cells = manifest_row["cells"]
        if not isinstance(cells, list) or len(cells) != 2:
            raise MintError(
                f"v2 input manifest producer {plan_id!r} must contain two cells"
            )
        cell_rows: dict[str, Mapping[str, Any]] = {}
        for cell_index, cell_value in enumerate(cells):
            cell_label = (
                f"v2 input manifest producer {plan_id}.cells[{cell_index}]"
            )
            cell_row = _object(
                cell_value,
                cell_label,
                {
                    "role",
                    "absolute",
                    "comparative",
                    "allowed_consumer_condition_families",
                },
            )
            role = _string(cell_row["role"], f"{cell_label}.role")
            if role in cell_rows:
                raise MintError(f"producer {plan_id!r} cell roles must be unique")
            cell_rows[role] = cell_row
        if set(cell_rows) != {"decode", "prefill"}:
            raise MintError(
                f"producer {plan_id!r} input cells must be decode and prefill"
            )

        component_paths: dict[tuple[str, str], ComponentInputs] = {}
        producer_evidence_root: Path | None = None
        for cell_pins in producer["cells"]:
            role = cell_pins["role"]
            cell_row = cell_rows[role]
            for component_name in ("absolute", "comparative"):
                paths = _v2_component_input_paths(
                    cell_row[component_name],
                    f"producer {plan_id}.{role}.{component_name}",
                )
                component_paths[(role, component_name)] = paths
                root_id = cell_pins[component_name]["evidence_root_id"]
                existing_root = evidence_roots.get(root_id)
                if existing_root is not None and existing_root.resolve() != (
                    paths.evidence_root.resolve()
                ):
                    raise MintError(
                        f"evidence-root id {root_id!r} maps to multiple paths"
                    )
                evidence_roots[root_id] = paths.evidence_root
                if (
                    producer_evidence_root is not None
                    and producer_evidence_root.resolve()
                    != paths.evidence_root.resolve()
                ):
                    raise MintError(
                        f"producer {plan_id!r} components map to multiple evidence roots"
                    )
                producer_evidence_root = paths.evidence_root
        if producer_evidence_root is None:
            raise MintError(f"producer {plan_id!r} has no authenticated evidence root")
        authenticated_cells: dict[str, V2CellComponents] = {}
        for cell_pins in producer["cells"]:
            role = cell_pins["role"]
            cell_row = cell_rows[role]
            configured = _v2_mint_pinset(producer, cell_pins)
            core = _configured_core(
                configured,
                pinset_path=pinset_path,
                expected_pinset_sha256=pinset_sha256,
            )
            authenticated = []
            for component_name, expected_kind in (
                ("absolute", "absolute"),
                ("comparative", "comparative"),
            ):
                paths = component_paths[(role, component_name)]
                root_id = cell_pins[component_name]["evidence_root_id"]
                _pre_admit_legacy_report(
                    paths.report_path,
                    f"producer {plan_id}.{role}.{component_name} extraction report",
                )
                _allow_governed_extraction_spec(paths.spec_path)
                try:
                    component = _authenticate_v2_component(
                        core,
                        core.ComponentPaths(
                            evidence_root_id=root_id,
                            evidence_root=paths.evidence_root,
                            report_path=paths.report_path,
                            spec_path=paths.spec_path,
                            order_manifest_path=paths.order_manifest_path,
                            calibration_cell_id=cell_pins[component_name][
                                "calibration_cell_id"
                            ],
                            expected_kind=expected_kind,
                        ),
                        expected_cell_id=cell_pins[component_name][
                            "calibration_cell_id"
                        ],
                        expected_basis_sha256=cell_pins[component_name][
                            "evaluation_basis_sha256"
                        ],
                        strict_validator=strict_validator,
                        expected_consumption_semantics_id=cell_pins[
                            component_name
                        ]["consumption_semantics_id"],
                        calibration_ledger_snapshot=ledger_snapshot,
                        calibration_bracket_binding=bracket_binding,
                    )
                except core.MintError as exc:
                    raise MintError(str(exc)) from exc
                authenticated.append(component)
            families = cell_row["allowed_consumer_condition_families"]
            if not isinstance(families, list):
                raise MintError(
                    f"producer {plan_id}.{role} allowed families must be an array"
                )
            authenticated_cells[role] = V2CellComponents(
                absolute=authenticated[0],
                comparative=authenticated[1],
                allowed_consumer_condition_families=tuple(families),
            )
        if consumption_semantics_id is not None:
            pinned_semantics = {
                cell[component_name]["consumption_semantics_id"]
                for cell in producer["cells"]
                for component_name in ("absolute", "comparative")
            }
            if pinned_semantics != {consumption_semantics_id}:
                raise MintError(
                    "explicit v2 consumption semantics dispatch contradicts "
                    "per-component pins"
                )
        authenticated_inputs = V2ProducerInputs(
            plan=dict(plan),
            cells=authenticated_cells,
            evidence_root=producer_evidence_root,
            plan_sha256=hashlib.sha256(plan_raw).hexdigest(),
            plan_declared_sha256=sidecar_parts[0],
            plan_sidecar_sha256=hashlib.sha256(sidecar_raw).hexdigest(),
            calibration_acceptance=dict(acceptance),
            calibration_acceptance_sha256=acceptance_sha256,
            bracket_binding=dict(bracket_binding),
            bracket_binding_sha256=hashlib.sha256(bracket_raw).hexdigest(),
        )
        authenticated_pre, authenticated_post, allowance_projection = (
            _v2_authenticate_bracket_binding(
                producer=producer,
                inputs=authenticated_inputs,
                ledger_snapshot=ledger_snapshot,
            )
        )
        result[plan_id] = replace(
            authenticated_inputs,
            authenticated_pre_observation=authenticated_pre,
            authenticated_post_observation=authenticated_post,
            calibration_allowance_projection=dict(allowance_projection),
        )
    return result, evidence_roots, ledger_snapshot


def _recomputation_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _recomputation_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_recomputation_json_value(item) for item in value]
    fields = getattr(value, "__dataclass_fields__", None)
    if isinstance(fields, Mapping):
        return {
            name: _recomputation_json_value(getattr(value, name))
            for name in fields
        }
    return value


def _recomputation_bytes(value: object) -> bytes:
    payload = {
        "estimator_path": getattr(value, "estimator_path", None),
        "comparative_blocks": getattr(value, "comparative_blocks", None),
        "estimate": getattr(
            value,
            "estimate",
            getattr(value, "comparative_estimate", None),
        ),
        "exact_widths_j": getattr(
            value,
            "exact_widths_j",
            getattr(value, "comparative_widths_j", None),
        ),
        "comparative_record": getattr(value, "comparative_record", None),
        "block_inputs": getattr(value, "block_inputs", None),
        "calibration_bracket": getattr(value, "calibration_bracket", None),
        "shared_edge_bound_s": getattr(value, "shared_edge_bound_s", None),
    }
    return json.dumps(
        _recomputation_json_value(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _validate_v2_recomputation_census(
    gate_recomputations: Mapping[str, Any],
    bind_recomputations: Mapping[str, Any],
) -> None:
    for cell_id, bind_recomputation in bind_recomputations.items():
        gate_recomputation = gate_recomputations.get(cell_id)
        if gate_recomputation is None or _recomputation_bytes(
            gate_recomputation
        ) != _recomputation_bytes(bind_recomputation):
            raise MintError(D165_REPLAY_RECOMPUTATION_DIVERGENCE)


def _write_v2_artifact_outputs(
    *,
    output_core: ModuleType,
    artifact: Mapping[str, Any],
    sidecar: Mapping[str, Any],
    floor_path: Path,
    statement_path: Path,
    d165_replay_out: Path,
) -> None:
    paths = tuple(Path(path) for path in (floor_path, statement_path, d165_replay_out))
    absolute_paths = tuple(path.absolute() for path in paths)
    if len(set(absolute_paths)) != len(absolute_paths):
        raise MintError("v2 artifact, statement, and replay outputs must differ")
    for path in paths:
        if path.exists():
            raise MintError(f"refusing to overwrite existing output: {path}")
    artifact_payload = (
        json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    statement_payload = output_core.render_single_count_statement(artifact).encode(
        "utf-8"
    )
    sidecar_payload = (
        json.dumps(sidecar, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    written: list[Path] = []
    try:
        for path, payload in (
            (floor_path, artifact_payload),
            (statement_path, statement_payload),
            (d165_replay_out, sidecar_payload),
        ):
            written.append(path)
            output_core._exclusive_write(path, payload)
    except Exception:
        for path in reversed(written):
            try:
                path.unlink()
            except OSError:
                pass
        raise


def mint_multi_cell_floor_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    input_manifest_path: Path,
    floor_path: Path,
    statement_path: Path,
    project_commit: str,
    project_tree_state: str,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None = None,
    calibration_custody_store: Path | None = None,
    d165_replay_out: Path | None = None,
) -> Mapping[str, Any]:
    """Authenticate all v2 sources, mint once, rebind, and write exclusively."""

    if active_v2_authentication_session() is not None:
        return _mint_multi_cell_floor_artifact_active(
            pinset_path=pinset_path,
            pinset_sha256=pinset_sha256,
            input_manifest_path=input_manifest_path,
            floor_path=floor_path,
            statement_path=statement_path,
            project_commit=project_commit,
            project_tree_state=project_tree_state,
            strict_validator=strict_validator,
            consumption_semantics_id=consumption_semantics_id,
            calibration_custody_store=calibration_custody_store,
            d165_replay_out=d165_replay_out,
        )
    try:
        with V2AuthenticationReadSession():
            return _mint_multi_cell_floor_artifact_active(
                pinset_path=pinset_path,
                pinset_sha256=pinset_sha256,
                input_manifest_path=input_manifest_path,
                floor_path=floor_path,
                statement_path=statement_path,
                project_commit=project_commit,
                project_tree_state=project_tree_state,
                strict_validator=strict_validator,
                consumption_semantics_id=consumption_semantics_id,
                calibration_custody_store=calibration_custody_store,
                d165_replay_out=d165_replay_out,
            )
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc


def _mint_multi_cell_floor_artifact_active(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    input_manifest_path: Path,
    floor_path: Path,
    statement_path: Path,
    project_commit: str,
    project_tree_state: str,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None = None,
    calibration_custody_store: Path | None = None,
    d165_replay_out: Path | None = None,
) -> Mapping[str, Any]:
    """Implementation body; caller guarantees one active v2 read session."""

    actual_head, origin_main_contains_head = _actual_v2_git_state()
    if project_commit != actual_head:
        raise MintError(
            "claimed project commit differs from the actual v2 mint Git HEAD"
        )
    if project_tree_state != "clean":
        raise MintError("claimed project tree state must be 'clean' for v2 issuance")
    loaded = load_pinset(pinset_path, pinset_sha256)
    if not isinstance(loaded, V2Pinset):
        raise MintError("multi-cell floor mint requires a final v2 pinset")
    _validate_v2_pin_hashes(loaded)
    input_manifest = _load_v2_input_manifest(input_manifest_path)
    head_pin_path = Path(
        _string(
            input_manifest["calibration_ledger_head_pin"],
            "v2 input manifest.calibration_ledger_head_pin",
        )
    )
    inputs, evidence_roots, ledger_snapshot = _authenticate_v2_inputs(
        pinset=loaded,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
        input_manifest_path=input_manifest_path,
        strict_validator=strict_validator,
        consumption_semantics_id=consumption_semantics_id,
        input_manifest=input_manifest,
        calibration_custody_store=calibration_custody_store,
    )
    # The path has now participated in successful ledger authentication;
    # derive its last-changing commit only after that domain owner accepts it.
    head_pin_commit_contained = (
        _head_pin_commit_containment_in_origin_main(head_pin_path)
    )
    gate_recomputations: dict[str, V2CellRecomputation] = {}
    artifact, components = _build_v2_artifacts(
        pinset=loaded,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
        producer_inputs=inputs,
        calibration_ledger_snapshot=ledger_snapshot,
        project_commit=actual_head,
        project_tree_state="clean",
        origin_main_contains_head=origin_main_contains_head,
        head_pin_commit_contained_in_origin_main=(
            head_pin_commit_contained
        ),
        recomputation_sink=gate_recomputations,
    )
    bind_recomputations: dict[str, Any] = {}
    common_mode_cells = 0
    for producer, component, expected in zip(
        loaded.value["producer_plans"],
        components,
        loaded.value["aggregate"]["component_artifacts"],
    ):
        observed = _artifact_sha256(component)
        if expected["sha256"] not in _artifact_sha256_containment_variants(
            component
        ):
            raise MintError(
                "aggregate/component hash mismatch: component artifact "
                f"{expected['plan_id']!r} expected {expected['sha256']}, observed {observed}"
            )
        cells_by_id = {
            cell["cell_id"]: cell for cell in component["cells"]
        }
        groups_by_id = {
            group["transport_group_id"]: group
            for group in component["transport_groups"]
        }
        for cell_pins in producer["cells"]:
            configured = _v2_mint_pinset(producer, cell_pins)
            core = _configured_core(
                configured,
                pinset_path=pinset_path,
                expected_pinset_sha256=pinset_sha256,
            )
            single_cell_component = copy.deepcopy(dict(component))
            single_cell_component["cells"] = [
                copy.deepcopy(cells_by_id[cell_pins["cell_id"]])
            ]
            single_cell_component["transport_groups"] = [
                copy.deepcopy(
                    groups_by_id[cell_pins["transport_group_id"]]
                )
            ]
            producer_input = inputs[producer["plan"]["plan_id"]]
            cell_input = producer_input.cells[cell_pins["role"]]
            try:
                bind_result = mint_estimator.bind_v2_floor_artifact_evidence(
                    core=core,
                    artifact=single_cell_component,
                    floor_path=floor_path,
                    evidence_roots=evidence_roots,
                    strict_validator=strict_validator,
                    comparative_component=cell_input.comparative,
                    runs_root=producer_input.evidence_root,
                    calibration_acceptance=(
                        producer_input.calibration_acceptance
                    ),
                    calibration_acceptance_sha256=(
                        producer_input.calibration_acceptance_sha256
                    ),
                    calibration_allowance_projection=(
                        producer_input.calibration_allowance_projection or {}
                    ),
                    declared_calibration_scope=producer["plan"][
                        "declared_calibration_scope"
                    ],
                    calibration_ledger_snapshot=ledger_snapshot,
                    calibration_bracket_binding=(
                        producer_input.bracket_binding
                    ),
                )
            except (core.MintError, ValueError) as exc:
                raise MintError(str(exc)) from exc
            if (
                isinstance(bind_result, tuple)
                and len(bind_result) == 2
            ):
                _legacy_result, bind_recomputation = bind_result
            else:
                _legacy_result = bind_result
                bind_recomputation = None
            cell_id = cell_pins["cell_id"]
            if bind_recomputation is None:
                continue
            bind_recomputations[cell_id] = bind_recomputation
            _validate_v2_recomputation_census(
                gate_recomputations, bind_recomputations
            )
            estimator_path = getattr(bind_recomputation, "estimator_path", None)
            if estimator_path == "common_mode":
                common_mode_cells += 1
                if d165_replay_out is None:
                    raise MintError(D165_REPLAY_OUTPUT_REQUIRED)
            elif estimator_path == "default":
                pass
            else:
                raise MintError(D165_REPLAY_RECOMPUTATION_DIVERGENCE)
    if d165_replay_out is not None and common_mode_cells == 0:
        raise MintError(D165_REPLAY_OUTPUT_UNUSED)
    errors = validate_floor_artifact(
        artifact=artifact,
        pinset_path=pinset_path,
        pinset_sha256=pinset_sha256,
    )
    if errors:
        raise MintError(f"post-bind v2 artifact validation failed: {errors[0]}")
    output_core = _fresh_original_core()
    if d165_replay_out is None:
        try:
            output_core.write_outputs_exclusive(artifact, floor_path, statement_path)
        except output_core.MintError as exc:
            raise MintError(str(exc)) from exc
        return artifact
    try:
        sidecar = dominance_closeout.build_d165_replay_sidecar(
            artifact,
            bind_recomputations,
        )
        _write_v2_artifact_outputs(
            output_core=output_core,
            artifact=artifact,
            sidecar=sidecar,
            floor_path=floor_path,
            statement_path=statement_path,
            d165_replay_out=d165_replay_out,
        )
    except output_core.MintError as exc:
        raise MintError(str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise MintError(str(exc)) from exc
    return artifact


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pinset", required=True, type=Path)
    parser.add_argument("--pinset-sha256", required=True)
    parser.add_argument("--artifact-id")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--single-count-out", required=True, type=Path)
    parser.add_argument("--d165-replay-out", type=Path)
    parser.add_argument("--v2-input-manifest", type=Path)
    parser.add_argument("--calibration-custody-store", type=Path)
    parser.add_argument("--calibration-plan", type=Path)
    parser.add_argument("--calibration-plan-relative-path")
    parser.add_argument("--absolute-root", type=Path)
    parser.add_argument("--absolute-report", type=Path)
    parser.add_argument("--absolute-spec", type=Path)
    parser.add_argument("--absolute-order-manifest", type=Path)
    parser.add_argument("--comparative-root", type=Path)
    parser.add_argument("--comparative-report", type=Path)
    parser.add_argument("--comparative-spec", type=Path)
    parser.add_argument(
        "--comparative-order-manifest", type=Path
    )
    parser.add_argument("--project-commit", required=True)
    parser.add_argument(
        "--project-tree-state", choices=("clean", "dirty"), required=True
    )
    parser.add_argument(
        "--consumption-semantics-id",
        choices=tuple(sorted(_SEMANTICS_IDS)),
        help=(
            "optional exact semantics dispatch; when supplied both component "
            "reports must use this id"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    from joulewise.cli import validate_bundle

    args = _parser().parse_args(argv)
    try:
        if args.v2_input_manifest is not None:
            with V2AuthenticationReadSession():
                loaded = load_pinset(args.pinset, args.pinset_sha256)
                if not isinstance(loaded, V2Pinset):
                    raise MintError(
                        "--v2-input-manifest requires a final v2 pinset"
                    )
                mint_multi_cell_floor_artifact(
                    pinset_path=args.pinset,
                    pinset_sha256=args.pinset_sha256,
                    input_manifest_path=args.v2_input_manifest,
                    floor_path=args.out,
                    statement_path=args.single_count_out,
                    project_commit=args.project_commit,
                    project_tree_state=args.project_tree_state,
                    strict_validator=lambda path, strict: validate_bundle(
                        path, strict=strict
                    ),
                    consumption_semantics_id=args.consumption_semantics_id,
                    calibration_custody_store=(
                        args.calibration_custody_store
                    ),
                    d165_replay_out=args.d165_replay_out,
                )
            return 0
        loaded = load_pinset(args.pinset, args.pinset_sha256)
        if isinstance(loaded, V2Pinset):
            raise MintError("final v2 pinset requires --v2-input-manifest")
        if args.calibration_custody_store is not None:
            raise MintError(
                "--calibration-custody-store requires --v2-input-manifest"
            )
        if args.d165_replay_out is not None:
            raise MintError(D165_REPLAY_OUTPUT_UNUSED)
        legacy_fields = {
            "--artifact-id": args.artifact_id,
            "--calibration-plan": args.calibration_plan,
            "--calibration-plan-relative-path": (
                args.calibration_plan_relative_path
            ),
            "--absolute-root": args.absolute_root,
            "--absolute-report": args.absolute_report,
            "--absolute-spec": args.absolute_spec,
            "--absolute-order-manifest": args.absolute_order_manifest,
            "--comparative-root": args.comparative_root,
            "--comparative-report": args.comparative_report,
            "--comparative-spec": args.comparative_spec,
            "--comparative-order-manifest": (
                args.comparative_order_manifest
            ),
        }
        missing = [name for name, value in legacy_fields.items() if value is None]
        if missing:
            raise MintError(
                "v1 pinset requires arguments: " + ", ".join(missing)
            )
        mint_floor_artifact(
            pinset_path=args.pinset,
            pinset_sha256=args.pinset_sha256,
            artifact_id=args.artifact_id,
            floor_path=args.out,
            statement_path=args.single_count_out,
            calibration_plan_path=args.calibration_plan,
            calibration_plan_relative_path=(
                args.calibration_plan_relative_path
            ),
            absolute_inputs=ComponentInputs(
                evidence_root=args.absolute_root,
                report_path=args.absolute_report,
                spec_path=args.absolute_spec,
                order_manifest_path=args.absolute_order_manifest,
            ),
            comparative_inputs=ComponentInputs(
                evidence_root=args.comparative_root,
                report_path=args.comparative_report,
                spec_path=args.comparative_spec,
                order_manifest_path=args.comparative_order_manifest,
            ),
            project_commit=args.project_commit,
            project_tree_state=args.project_tree_state,
            strict_validator=lambda path, strict: validate_bundle(
                path, strict=strict
            ),
            consumption_semantics_id=args.consumption_semantics_id,
        )
    except (MintError, V2AuthenticationInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
