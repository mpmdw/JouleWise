#!/usr/bin/env python3
"""Mint the first cross-window JouleWise detection-floor artifact.

The command consumes two already-produced, authenticated extraction reports.
It does not run extraction itself.  All report, specification, order, plan,
campaign-log, and admitted-bundle bytes are authenticated before any
``detection_floor`` builder is called.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_engine.inputs import scientific_config_identity  # noqa: E402
from joulewise.authentication_io import (  # noqa: E402
    V2AuthenticationInputError,
    read_authentication_input,
    sha256_authentication_input,
)
from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    STACK_IDENTITY_DOMAIN,
    absolute_false_effect_floor,
    abba_delta,
    attribution_single_count_discipline,
    build_absolute_record,
    build_comparative_record,
    build_floor_artifact,
    build_floor_cell,
    build_transport_group,
    canonical_domain_sha256,
    complete_bundle_sha256,
    comparative_false_effect_floor,
    validate_floor_artifact,
)
from joulewise.floor_extraction import (  # noqa: E402
    EXTRACTION_SCHEMA_VERSION,
    EXTRACTION_SPEC_SCHEMA_VERSION,
    validate_extraction_spec,
)
from joulewise.whole_window import (  # noqa: E402
    AuthenticatedConsumptionSession,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    neg8_claim_family_for_metric,
    whole_window_drift_allowances,
    whole_window_refusal_reasons,
)
from joulewise.calibration_bracketing import (  # noqa: E402
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (  # noqa: E402
    CalibrationLedgerSnapshot,
    load_calibration_ledger_snapshot,
)


MINT_TOOL_VERSION = "joulewise.floor_mint.v1"
CELL_ID = "df-ph-decode-floor"
TRANSPORT_GROUP_ID = "tg-df-ph-decode-production-v1"
CONDITION_FAMILY_ID = "df-ph-decode"
CONDITION_FAMILY_SHA256 = (
    "e38e2a2f3e76b8cdd6b3ef4f5d3d7090ef4846dbf83279001ff4df8a9a762bfe"
)
PLAN_SHA256 = (
    "e529a0624b7618edaade511dd610ae0837f31de299dde642a055974c382681ab"
)
A10_EVALUATION_BASIS_SHA256 = (
    "79c6e8b9211f18a5ad8937f155230a9090706bf1dfc8c3ed767deb53074e053e"
)
WINDOW_C_EVALUATION_BASIS_SHA256 = (
    "0cf07a5cdc3847e67ba9be9dc50ffda43b7d00ef10d03485faf36c2693418fa6"
)
A10_EVALUATION_BASIS_MEMBERS = 37
WINDOW_C_EVALUATION_BASIS_MEMBERS = 47
A10_SPEC_MEMBERS = 30
WINDOW_C_SPEC_MEMBERS = 40
EXPECTED_ABSOLUTE_N = 10
EXPECTED_COMPARATIVE_N_BLOCKS = 10
A10_DRIFT_ALLOWANCE_J = 0.652271753365838
WINDOW_C_DRIFT_ALLOWANCE_J = 0.5812720449734456
EXPECTED_OPERATIVE_FLOOR_TEXT = "7.377086"
A10_ORDER_MANIFEST_ID = "p2-015-02_phase_absolute-order-v1"
WINDOW_C_ORDER_MANIFEST_ID = "p2-015-05_phase_decode_abba-order-v1"
A10_CELL_ID = "df-ph-decode-absolute"
WINDOW_C_CELL_ID = "df-cmp-abba-ph-decode"
METRIC = "phase_energy_j.decode"
WINDOW_CLASS = "phase"
TARGET_PRECHECK_PATH = ("phase", "decode")
CALIBRATION_SCOPE = "production_window"
PLAN_DECLARED_SCOPE = "window_a"
SOURCE_CLASS = "prospective"

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_SEMANTICS_IDS = {
    MINTED_CONSUMPTION_SEMANTICS_ID,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
}
_ABBA_POSITIONS = ("A1", "B1", "B2", "A2")
StrictValidator = Callable[[Path, bool], Sequence[str]]
ConsumptionAuthenticator = Callable[
    ...,
    tuple[Mapping[str, Mapping[str, Any]], str],
]
AllowanceDeriver = Callable[..., Any]

_BINDING_SUMMARY_CACHE: dict[
    tuple[str, str, tuple[tuple[str, str], ...]],
    Mapping[str, Mapping[str, Any]],
] = {}


class MintError(ValueError):
    """A hard mint gate failed; no artifact may be written."""


@dataclass(frozen=True)
class ComponentPaths:
    """Files and source root for one extraction component."""

    evidence_root_id: str
    evidence_root: Path
    report_path: Path
    spec_path: Path
    order_manifest_path: Path
    calibration_cell_id: str
    expected_kind: str


@dataclass(frozen=True)
class AuthenticatedMember:
    bundle_id: str
    bundle_sha256: str
    config_sha256: str
    metric_value_j: float
    raw_config: Mapping[str, Any]
    metadata: Mapping[str, Any]
    summary: Mapping[str, Any]
    admissible_half_width_j: float | None = None


@dataclass(frozen=True)
class AuthenticatedComponent:
    """All information admitted before the pre-registration gate."""

    evidence_root_id: str
    calibration_cell_id: str
    kind: str
    report: Mapping[str, Any]
    report_sha256: str
    spec: Mapping[str, Any]
    spec_sha256: str
    order_manifest: Mapping[str, Any]
    order_manifest_sha256: str
    campaign_log_sha256: str
    cell: Mapping[str, Any]
    spec_cell: Mapping[str, Any]
    members: tuple[AuthenticatedMember, ...]
    widths_j: tuple[float, ...]
    whole_window_evaluation_basis_sha256: str
    evaluation_basis_member_count: int
    consumption_semantics_id: str
    whole_window_drift_allowance: Mapping[str, Any]
    source_regime: Mapping[str, Any]
    scientific_config_identity_sha256: str
    backend: str
    # The authenticated whole-window verdict owns the bracket that covered
    # this component.  Generalized v2 consumers use this exact basis record
    # to prevent a supplied bracket binding from choosing its own window.
    # Historical v1 records did not retain the projection in memory, so the
    # optional default preserves their construction and artifact bytes.
    whole_window_calibration_bracket: Mapping[str, Any] | None = None


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_json_object(path: Path, label: str) -> tuple[Mapping[str, Any], bytes]:
    try:
        raw = read_authentication_input(path, grammar="json", label=label)
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(f"{label} cannot be read: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MintError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise MintError(f"{label} must contain a JSON object")
    return value, raw


def _load_json_lines(path: Path, label: str) -> tuple[list[Mapping[str, Any]], bytes]:
    try:
        raw = read_authentication_input(path, grammar="jsonl", label=label)
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(f"{label} cannot be read: {exc}") from exc
    rows: list[Mapping[str, Any]] = []
    try:
        for line in raw.decode("utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, Mapping):
                raise MintError(f"{label} rows must be JSON objects")
            rows.append(row)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MintError(f"{label} is not valid UTF-8 JSONL: {exc}") from exc
    return rows, raw


def _finite(value: object, label: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise MintError(f"{label} must be a finite number")
    converted = float(value)
    if not math.isfinite(converted) or (nonnegative and converted < 0.0):
        raise MintError(f"{label} must be a finite nonnegative number")
    return converted


def _safe_relative_posix(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MintError(f"{label} must be a nonempty safe-relative POSIX path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or "\\" in value
        or value != path.as_posix()
        or any(part in {"", ".", ".."} for part in path.parts)
        or _WINDOWS_ABSOLUTE_RE.match(value)
    ):
        raise MintError(f"{label} must be a safe-relative POSIX path")
    return value


def _assert_path_independent(value: object, label: str = "artifact") -> None:
    """Reject absolute paths and validate every persisted relative_path."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            if key == "relative_path":
                _safe_relative_posix(child, child_label)
            _assert_path_independent(child, child_label)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_path_independent(child, f"{label}[{index}]")
        return
    if isinstance(value, str) and (
        value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value)
    ):
        raise MintError(f"{label}: absolute paths may not be persisted")


def _metric_value(summary: Mapping[str, Any]) -> float:
    phases = summary.get("phase_energy_j")
    value = phases.get("decode") if isinstance(phases, Mapping) else None
    return _finite(value, "summary phase_energy_j.decode")


def _sha256_file(path: Path, label: str) -> str:
    try:
        return sha256_authentication_input(path, label=label)
    except V2AuthenticationInputError as exc:
        raise MintError(str(exc)) from exc
    except OSError as exc:
        raise MintError(f"{label} cannot be read: {exc}") from exc


def _path_independent_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MintError(f"{label} must be a nonempty string")
    if value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value):
        name = PurePosixPath(value.replace("\\", "/")).name
        if not name:
            raise MintError(f"{label} cannot be reduced to a path-independent id")
        return name
    return value


def _derive_stack_identity(
    raw_config: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Derive the governed stack identity from current bundle evidence."""

    hardware = raw_config.get("hardware_target")
    workload = metadata.get("workload_provenance")
    adapters = metadata.get("adapters")
    runtime = adapters.get("runtime") if isinstance(adapters, Mapping) else None
    telemetry = (
        adapters.get("telemetry") if isinstance(adapters, Mapping) else None
    )
    prepare = (
        runtime.get("prepare_metadata") if isinstance(runtime, Mapping) else None
    )
    model = workload.get("model") if isinstance(workload, Mapping) else None
    artifact = (
        model.get("artifact_identity") if isinstance(model, Mapping) else None
    )
    tokenizer = (
        workload.get("tokenizer") if isinstance(workload, Mapping) else None
    )
    sampler = workload.get("sampler") if isinstance(workload, Mapping) else None
    output_policy = (
        workload.get("output_policy") if isinstance(workload, Mapping) else None
    )
    device = metadata.get("device")
    quantization = metadata.get("quantization")
    required_mappings = (
        hardware,
        workload,
        runtime,
        telemetry,
        prepare,
        artifact,
        tokenizer,
        sampler,
        output_policy,
        device,
        quantization,
    )
    if not all(isinstance(value, Mapping) for value in required_mappings):
        raise MintError("source stack identity fields are unavailable")
    artifact_sha256 = artifact.get("sha256") or artifact.get("folded_sha256")
    telemetry_name = telemetry.get("name")
    if (
        not isinstance(artifact_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", artifact_sha256) is None
        or not isinstance(telemetry_name, str)
        or not telemetry_name
    ):
        raise MintError("source stack artifact/telemetry identity is unavailable")
    tokenizer_identity = dict(tokenizer)
    tokenizer_identity["identifier"] = _path_independent_identifier(
        tokenizer.get("identifier"), "tokenizer identifier"
    )
    runtime_version = (
        prepare.get("version")
        or prepare.get("mlx_version")
        or prepare.get("mlx_lm_version")
    )
    if not isinstance(runtime_version, str) or not runtime_version:
        raise MintError("source runtime version is unavailable")
    return {
        "hardware_unit": {
            "config_id": hardware.get("id"),
            "device": device.get("device"),
            "machine": metadata.get("machine"),
        },
        "os_version": str(metadata.get("platform") or "unknown"),
        "runtime_version": {
            "name": runtime.get("name"),
            "adapter": prepare.get("adapter"),
            "version": runtime_version,
        },
        "kernel_library": str(
            prepare.get("kernel_library") or "unavailable"
        ),
        "model_artifact_sha256": artifact_sha256,
        "quantization": dict(quantization),
        "tokenizer_identity": tokenizer_identity,
        "sampler_output_policy": {
            "sampler": dict(sampler),
            "output_policy": {
                key: output_policy.get(key)
                for key in ("name", "requested_tokens", "stop_condition")
            },
        },
        "batching_concurrency_policy": str(
            prepare.get("batching_concurrency_policy")
            or "single-request sequential"
        ),
        "measurement_boundary_label": {
            "boundary": device.get("boundary", "unavailable"),
            "rails": device.get("rail_manifest"),
        },
        "telemetry_backend": telemetry_name,
    }


def _source_admissible_half_width(
    summary: Mapping[str, Any], bundle_id: str
) -> float:
    envelopes = summary.get("energy_anchor_shift_envelopes")
    envelope = (
        envelopes.get("/phase_energy_j/decode")
        if isinstance(envelopes, Mapping)
        else None
    )
    if not isinstance(envelope, Mapping):
        raise MintError(
            f"{bundle_id}: decode anchor-shift envelope is unavailable"
        )
    point = _finite(envelope.get("point_j"), f"{bundle_id} anchor point")
    lower = _finite(envelope.get("lower_j"), f"{bundle_id} anchor lower")
    upper = _finite(envelope.get("upper_j"), f"{bundle_id} anchor upper")
    max_delta = _finite(
        envelope.get("max_abs_delta_j"),
        f"{bundle_id} anchor max delta",
        nonnegative=True,
    )
    if lower > point or upper < point:
        raise MintError(f"{bundle_id}: anchor-shift envelope does not contain point")
    bound_terms = summary.get("energy_bound_terms_j")
    interpolation = (
        bound_terms.get("E_interpolation_joint_edge_bound_j")
        if isinstance(bound_terms, Mapping)
        else None
    )
    interpolation_j = _finite(
        interpolation,
        f"{bundle_id} joint interpolation bound",
        nonnegative=True,
    )
    return max(point - lower, upper - point, max_delta) + interpolation_j


def _strict_bundle(
    root: Path,
    bundle_id: object,
    stored_row: Mapping[str, Any],
    strict_validator: StrictValidator,
    *,
    operative_summary: Mapping[str, Any] | None = None,
) -> AuthenticatedMember:
    if (
        not isinstance(bundle_id, str)
        or not bundle_id
        or "\\" in bundle_id
        or PurePosixPath(bundle_id).name != bundle_id
        or bundle_id in {".", ".."}
    ):
        raise MintError("bundle_id must be a safe basename")
    resolved_root = root.resolve()
    bundle_path = (root / bundle_id).resolve()
    try:
        bundle_path.relative_to(resolved_root)
    except ValueError as exc:
        raise MintError(f"{bundle_id}: bundle path escapes its evidence root") from exc
    try:
        problems = tuple(strict_validator(bundle_path, True))
    except Exception as exc:
        raise MintError(
            f"{bundle_id}: strict validation raised {type(exc).__name__}: {exc}"
        ) from exc
    if problems:
        raise MintError(f"{bundle_id}: strict validation failed: {problems[0]}")
    config, _ = _load_json_object(bundle_path / "config.json", f"{bundle_id} config")
    metadata, _ = _load_json_object(
        bundle_path / "metadata.json", f"{bundle_id} metadata"
    )
    stored_summary, _ = _load_json_object(
        bundle_path / "summary_metrics.json", f"{bundle_id} summary"
    )
    summary = (
        operative_summary
        if isinstance(operative_summary, Mapping)
        else stored_summary
    )
    if summary.get("status") != "succeeded":
        raise MintError(f"{bundle_id}: source summary status is not succeeded")
    try:
        bundle_sha256 = complete_bundle_sha256(bundle_path)
    except ValueError as exc:
        raise MintError(f"{bundle_id}: cannot hash complete bundle: {exc}") from exc
    config_sha256 = _sha256_file(bundle_path / "config.json", f"{bundle_id} config")
    if bundle_sha256 != stored_row.get("bundle_sha256"):
        raise MintError(f"{bundle_id}: report bundle_sha256 does not match source bytes")
    if config_sha256 != stored_row.get("config_sha256"):
        raise MintError(f"{bundle_id}: report config_sha256 does not match source bytes")
    metric = _metric_value(summary)
    stored_metric = _finite(
        stored_row.get("metric_value_j"), f"{bundle_id} report metric"
    )
    if not math.isclose(metric, stored_metric, rel_tol=1e-12, abs_tol=1e-12):
        raise MintError(f"{bundle_id}: report metric does not match source bytes")
    admissible_half_width = _source_admissible_half_width(summary, bundle_id)
    if "anchor_shift_bound_j" in stored_row:
        stored_width = _finite(
            stored_row.get("anchor_shift_bound_j"),
            f"{bundle_id} report anchor width",
            nonnegative=True,
        )
        if not math.isclose(
            admissible_half_width,
            stored_width,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise MintError(
                f"{bundle_id}: report anchor width does not match source bytes"
            )
    return AuthenticatedMember(
        bundle_id=bundle_id,
        bundle_sha256=bundle_sha256,
        config_sha256=config_sha256,
        metric_value_j=metric,
        raw_config=config,
        metadata=metadata,
        summary=summary,
        admissible_half_width_j=admissible_half_width,
    )


def _authenticated_consumption_summaries(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    evaluation_basis_sha256: str,
    *,
    target_bundle_ids: set[str],
    consumption_semantics_id: str | None = None,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
) -> tuple[Mapping[str, Mapping[str, Any]], str]:
    """Replay the authenticated whole-window consumption semantics once."""

    session = AuthenticatedConsumptionSession(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_semantics_id=(
            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        ),
        calibration_ledger_snapshot=calibration_ledger_snapshot,
    )
    reasons = whole_window_refusal_reasons(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_session=session,
        consumption_semantics_id=consumption_semantics_id,
    )
    if reasons:
        raise MintError(
            "authenticated whole-window consumption refused: " + reasons[0]
        )
    if session.ready:
        for bundle_id in sorted(target_bundle_ids):
            target_reasons = session.path_refusal_reasons.get(
                bundle_id, {}
            ).get(TARGET_PRECHECK_PATH, ())
            if target_reasons:
                raise MintError(
                    f"{bundle_id}: authenticated target metric refused: "
                    f"{target_reasons[0]}"
                )
        summaries = {
            bundle_id: summary
            for bundle_id in referenced_bundle_ids
            if isinstance(
                (summary := session.summary_for(bundle_id)),
                Mapping,
            )
        }
        if set(summaries) != referenced_bundle_ids:
            raise MintError(
                "authenticated whole-window consumption omitted source members"
            )
        return summaries, getattr(
            session,
            "consumption_semantics_id",
            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )

    summaries: dict[str, Mapping[str, Any]] = {}
    for bundle_id in referenced_bundle_ids:
        summary, _ = _load_json_object(
            runs_root / bundle_id / "summary_metrics.json",
            f"{bundle_id} summary",
        )
        summaries[bundle_id] = summary
    return summaries, MINTED_CONSUMPTION_SEMANTICS_ID


def _spec_member_ids(spec: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for cell in spec.get("cells", []):
        if not isinstance(cell, Mapping):
            continue
        members = cell.get("members")
        if isinstance(members, list):
            ids.extend(
                row["bundle_id"]
                for row in members
                if isinstance(row, Mapping) and isinstance(row.get("bundle_id"), str)
            )
        blocks = cell.get("blocks")
        if isinstance(blocks, list):
            for block in blocks:
                block_members = (
                    block.get("members") if isinstance(block, Mapping) else None
                )
                if isinstance(block_members, Mapping):
                    ids.extend(
                        block_members[position]
                        for position in _ABBA_POSITIONS
                        if isinstance(block_members.get(position), str)
                    )
    return ids


def _target_spec_cell(
    spec: Mapping[str, Any], cell_id: str, kind: str
) -> Mapping[str, Any]:
    matches = [
        cell
        for cell in spec.get("cells", [])
        if isinstance(cell, Mapping) and cell.get("cell_id") == cell_id
    ]
    if len(matches) != 1:
        raise MintError(f"extraction spec must contain exactly one {cell_id!r} cell")
    cell = matches[0]
    if (
        cell.get("kind") != kind
        or cell.get("metric") != METRIC
        or cell.get("window_class") != WINDOW_CLASS
    ):
        raise MintError(f"{cell_id}: extraction spec cell key/kind mismatch")
    return cell


def _target_report_cell(
    report: Mapping[str, Any], cell_id: str, kind: str
) -> Mapping[str, Any]:
    matches = [
        cell
        for cell in report.get("cells", [])
        if isinstance(cell, Mapping) and cell.get("cell_id") == cell_id
    ]
    if len(matches) != 1:
        raise MintError(f"extraction report must contain exactly one {cell_id!r} cell")
    cell = matches[0]
    if (
        cell.get("kind") != kind
        or cell.get("metric") != METRIC
        or cell.get("window_class") != WINDOW_CLASS
        or cell.get("extractable") is not True
        or cell.get("refusal_reasons") not in ([], ())
    ):
        raise MintError(f"{cell_id}: extraction report is not an extractable target")
    floor = cell.get("floor")
    if not isinstance(floor, Mapping):
        raise MintError(f"{cell_id}: extraction report has no floor row")
    return cell


def _report_members(
    cell: Mapping[str, Any], spec_cell: Mapping[str, Any], kind: str
) -> tuple[list[Mapping[str, Any]], tuple[float, ...]]:
    raw_members = cell.get("members")
    if not isinstance(raw_members, list) or not all(
        isinstance(row, Mapping) for row in raw_members
    ):
        raise MintError("extraction report members must be an array of objects")
    members = [
        row
        for row in raw_members
        if row.get("excluded") is False and not row.get("reasons")
    ]
    if len(members) != len(raw_members):
        raise MintError("target extraction cell contains excluded or refused members")
    by_id = {row.get("bundle_id"): row for row in members}
    if len(by_id) != len(members) or None in by_id:
        raise MintError("target extraction report has duplicate/invalid bundle ids")
    if kind == "absolute":
        spec_members = spec_cell.get("members")
        if not isinstance(spec_members, list):
            raise MintError("absolute extraction spec members must be an array")
        ids = [
            row.get("bundle_id") if isinstance(row, Mapping) else None
            for row in spec_members
        ]
        if ids != [row.get("bundle_id") for row in members]:
            raise MintError("absolute report membership/order differs from extraction spec")
        widths = tuple(
            _finite(
                row.get("anchor_shift_bound_j"),
                f"{row.get('bundle_id')} anchor width",
                nonnegative=True,
            )
            for row in members
        )
        return members, widths

    blocks = spec_cell.get("blocks")
    if not isinstance(blocks, list):
        raise MintError("comparative extraction spec blocks must be an array")
    ordered: list[Mapping[str, Any]] = []
    widths: list[float] = []
    for block in blocks:
        if not isinstance(block, Mapping):
            raise MintError("comparative extraction spec block must be an object")
        block_id = block.get("block_id")
        spec_members = block.get("members")
        if not isinstance(spec_members, Mapping):
            raise MintError("comparative block members must be an object")
        block_rows: list[Mapping[str, Any]] = []
        for position in _ABBA_POSITIONS:
            bundle_id = spec_members.get(position)
            row = by_id.get(bundle_id)
            if (
                not isinstance(row, Mapping)
                or row.get("block_id") != block_id
                or row.get("position") != position
            ):
                raise MintError(
                    "comparative report membership/order differs from extraction spec"
                )
            block_rows.append(row)
        ordered.extend(block_rows)
        widths.append(
            math.fsum(
                _finite(
                    row.get("anchor_shift_bound_j"),
                    f"{row.get('bundle_id')} anchor width",
                    nonnegative=True,
                )
                for row in block_rows
            )
            / 2.0
        )
    if ordered != members:
        raise MintError("comparative report member sequence is not flattened A1/B1/B2/A2")
    return ordered, tuple(widths)


def _verify_report_widths(
    cell: Mapping[str, Any], widths: Sequence[float]
) -> None:
    floor = cell.get("floor")
    report_widths = (
        floor.get("admissible_half_widths_j")
        if isinstance(floor, Mapping)
        else None
    )
    if (
        not isinstance(report_widths, list)
        or len(report_widths) != len(widths)
        or any(
            not math.isclose(
                _finite(value, "reported admissible width", nonnegative=True),
                expected,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            for value, expected in zip(report_widths, widths)
        )
    ):
        raise MintError(
            "extraction-report widths differ element-for-element from member evidence"
        )


def _authenticated_evaluation_basis(
    rows: Sequence[Mapping[str, Any]], expected_sha256: str
) -> Mapping[str, Any]:
    matching_bases: list[Mapping[str, Any]] = []
    for row in rows:
        basis = row.get("evaluation_basis")
        if not isinstance(basis, Mapping) or basis.get("sha256") != expected_sha256:
            continue
        occurrences = basis.get("member_occurrences")
        if not isinstance(occurrences, list) or any(
            not isinstance(item, Mapping)
            or not isinstance(item.get("bundle_id"), str)
            for item in occurrences
        ):
            raise MintError("evaluation basis member_occurrences are malformed")
        member_ids = [item["bundle_id"] for item in occurrences]
        if len(member_ids) != len(set(member_ids)):
            raise MintError("evaluation basis contains duplicate member occurrences")
        matching_bases.append(basis)
    if len(matching_bases) != 1:
        raise MintError(
            f"campaign log must contain exactly one evaluation basis {expected_sha256}"
        )
    return matching_bases[0]


def _evaluation_basis_members(
    rows: Sequence[Mapping[str, Any]], expected_sha256: str
) -> frozenset[str]:
    basis = _authenticated_evaluation_basis(rows, expected_sha256)
    return frozenset(
        item["bundle_id"] for item in basis["member_occurrences"]
    )


def _order_manifest_ids(order_manifest: Mapping[str, Any]) -> list[str]:
    rows = order_manifest.get("executed_order")
    if not isinstance(rows, list):
        raise MintError("order manifest executed_order must be an array")
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise MintError("order manifest rows must be objects")
        bundle_id = row.get("run_id")
        if not isinstance(bundle_id, str) or not bundle_id:
            raise MintError("order manifest row run_id must be nonempty")
        ids.append(bundle_id)
    if len(ids) != len(set(ids)):
        raise MintError("order manifest executed_order contains duplicate run ids")
    return ids


def _validate_order(
    order_manifest: Mapping[str, Any],
    *,
    target_ids: Sequence[str],
    spec_ids: Sequence[str],
) -> None:
    ordered = _order_manifest_ids(order_manifest)
    if set(ordered) != set(spec_ids) or len(ordered) != len(spec_ids):
        raise MintError("order manifest membership differs from extraction spec")
    selected = [bundle_id for bundle_id in ordered if bundle_id in set(target_ids)]
    if selected != list(target_ids):
        raise MintError("order manifest disagrees with target component member order")


def _source_regime(
    members: Sequence[AuthenticatedMember],
) -> tuple[Mapping[str, Any], str, str]:
    if not members:
        raise MintError("component needs authenticated source members")
    stack_identities: list[Mapping[str, Any]] = []
    scientific_hashes: set[str] = set()
    backends: set[str] = set()
    for member in members:
        stack = _derive_stack_identity(member.raw_config, member.metadata)
        stack_identities.append(stack)
        scientific = scientific_config_identity(member.raw_config)
        if not isinstance(scientific, Mapping):
            raise MintError(
                f"{member.bundle_id}: scientific config identity is unavailable"
            )
        scientific_hashes.add(
            _sha256(
                json.dumps(
                    scientific,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8")
            )
        )
        hardware = member.raw_config.get("hardware_target")
        backend = (
            hardware.get("telemetry_backend")
            if isinstance(hardware, Mapping)
            else None
        )
        if not isinstance(backend, str) or not backend:
            raise MintError(f"{member.bundle_id}: telemetry backend is unavailable")
        backends.add(backend)
    stack_hashes = {
        canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack)
        for stack in stack_identities
    }
    if len(stack_hashes) != 1:
        raise MintError("component members do not share one stack identity")
    if len(scientific_hashes) != 1:
        raise MintError("component members do not share one scientific config identity")
    if len(backends) != 1:
        raise MintError("component members do not share one telemetry backend")
    stress = _stress_observed(members)
    stack = dict(stack_identities[0])
    return (
        {
            "stack_identity": stack,
            "stack_identity_sha256": next(iter(stack_hashes)),
            "stress_observed": stress,
        },
        next(iter(scientific_hashes)),
        next(iter(backends)),
    )


def _stress_observed(
    members: Sequence[AuthenticatedMember],
) -> Mapping[str, Any]:
    powers: list[float] = []
    durations: list[float] = []
    p95_gaps: list[float] = []
    bracketing_gaps: list[float] = []
    cadence_ratios: list[float] = []
    clock_bounds: list[float] = []
    interpolation_bounds: list[float] = []

    for member in members:
        prechecks = member.summary.get("window_evidence_precheck")
        phases = prechecks.get("phase") if isinstance(prechecks, Mapping) else None
        decode = phases.get("decode") if isinstance(phases, Mapping) else None
        windows = decode.get("windows") if isinstance(decode, Mapping) else None
        if not isinstance(windows, list) or not windows:
            raise MintError(
                f"{member.bundle_id}: phase decode stress evidence is unavailable"
            )
        member_duration = 0.0
        for window in windows:
            if not isinstance(window, Mapping):
                raise MintError(f"{member.bundle_id}: malformed decode stress window")
            duration = _finite(
                window.get("window_duration_s"),
                f"{member.bundle_id} window duration",
                nonnegative=True,
            )
            p95 = _finite(
                window.get("observed_window_p95_sample_gap_s"),
                f"{member.bundle_id} p95 gap",
                nonnegative=True,
            )
            bracket = _finite(
                window.get("observed_bracketing_max_sample_gap_s"),
                f"{member.bundle_id} bracketing gap",
                nonnegative=True,
            )
            cadence = _finite(
                window.get("cadence_ratio"),
                f"{member.bundle_id} cadence ratio",
                nonnegative=True,
            )
            clock = _finite(
                window.get("clock_anchor_bound_s"),
                f"{member.bundle_id} clock anchor bound",
                nonnegative=True,
            )
            interpolation = _finite(
                window.get("interpolation_joint_edge_bound_j"),
                f"{member.bundle_id} interpolation bound",
                nonnegative=True,
            )
            if duration <= 0.0:
                raise MintError(f"{member.bundle_id}: window duration must be positive")
            member_duration += duration
            durations.append(duration)
            p95_gaps.append(p95)
            bracketing_gaps.append(bracket)
            cadence_ratios.append(cadence)
            clock_bounds.append(clock)
            interpolation_bounds.append(interpolation)
        powers.append(member.metric_value_j / member_duration)

    return {
        "mean_power_w_min": min(powers),
        "mean_power_w_max": max(powers),
        "window_duration_s_min": min(durations),
        "window_duration_s_max": max(durations),
        "p95_sample_gap_s_max": max(p95_gaps),
        "bracketing_sample_gap_s_max": max(bracketing_gaps),
        "cadence_ratio_min": min(cadence_ratios),
        "bound_terms": {
            "clock_anchor_bound_s": {
                "applicability": "required",
                "maximum": max(clock_bounds),
            },
            "interpolation_bound_j": {
                "applicability": "required",
                "maximum": max(interpolation_bounds),
            },
            "idle_drift_bound_j": {
                "applicability": "not_applicable",
                "maximum": None,
            },
        },
    }


def _tag_value(raw_config: Mapping[str, Any], prefix: str) -> str | None:
    run_metadata = raw_config.get("run_metadata")
    tags = (
        run_metadata.get("tags")
        if isinstance(run_metadata, Mapping)
        else None
    )
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return None
    values = [tag[len(prefix) :] for tag in tags if tag.startswith(prefix)]
    return values[0] if len(values) == 1 and values[0] else None


def _verify_source_order_tags(
    member: AuthenticatedMember,
    report_row: Mapping[str, Any],
    *,
    comparative: bool,
) -> None:
    if _tag_value(
        member.raw_config, "calibration-plan-sha256="
    ) != PLAN_SHA256:
        raise MintError(f"{member.bundle_id}: source calibration-plan tag mismatch")
    if not comparative:
        return
    if _tag_value(
        member.raw_config, "calibration-abba-block-id="
    ) != report_row.get("block_id"):
        raise MintError(f"{member.bundle_id}: source ABBA block tag mismatch")
    position = report_row.get("position")
    expected_label = (
        position[0]
        if isinstance(position, str) and position in _ABBA_POSITIONS
        else None
    )
    if _tag_value(
        member.raw_config, "calibration-abba-label="
    ) != expected_label:
        raise MintError(f"{member.bundle_id}: source ABBA label tag mismatch")
    expected_index = (
        str(_ABBA_POSITIONS.index(position) + 1)
        if position in _ABBA_POSITIONS
        else None
    )
    if _tag_value(
        member.raw_config, "calibration-abba-sequence-index="
    ) != expected_index:
        raise MintError(f"{member.bundle_id}: source ABBA sequence tag mismatch")


def _authenticate_component(
    paths: ComponentPaths,
    *,
    expected_cell_id: str,
    expected_basis_sha256: str,
    strict_validator: StrictValidator,
    consumption_authenticator: ConsumptionAuthenticator = (
        _authenticated_consumption_summaries
    ),
    allowance_deriver: AllowanceDeriver = whole_window_drift_allowances,
    expected_consumption_semantics_id: str | None = None,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
) -> AuthenticatedComponent:
    if calibration_ledger_snapshot is None:
        acceptance = load_calibration_acceptance_bound()
        cutoff = (
            acceptance.get("ledger_cutoff")
            if isinstance(acceptance, Mapping)
            else None
        )
        calibration_ledger_snapshot = load_calibration_ledger_snapshot(
            baseline_sequence=(
                cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
            ),
            baseline_digest=(
                cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
            ),
        )
    report, report_raw = _load_json_object(paths.report_path, "extraction report")
    spec, spec_raw = _load_json_object(paths.spec_path, "extraction spec")
    if (
        report.get("schema_version") != EXTRACTION_SCHEMA_VERSION
        or report.get("spec_schema_version") != EXTRACTION_SPEC_SCHEMA_VERSION
    ):
        raise MintError("extraction report schema literals are not governed")
    if (
        report.get("spec_membership_refusals") not in ([], ())
        or report.get("idle_admission_refusals") not in ([], ())
    ):
        raise MintError("extraction report carries global refusal records")
    report_root = report.get("runs_root")
    if (
        not isinstance(report_root, str)
        or Path(report_root).resolve() != paths.evidence_root.resolve()
    ):
        raise MintError("extraction report runs_root differs from evidence root")
    errors = validate_extraction_spec(spec)
    if errors:
        raise MintError(f"invalid extraction spec: {errors[0]}")
    order, order_raw = _load_json_object(
        paths.order_manifest_path, "order manifest"
    )
    spec_cell = _target_spec_cell(spec, expected_cell_id, paths.expected_kind)
    cell = _target_report_cell(report, expected_cell_id, paths.expected_kind)
    report_members, widths = _report_members(cell, spec_cell, paths.expected_kind)
    _verify_report_widths(cell, widths)
    spec_ids = _spec_member_ids(spec)
    referenced_bundle_ids = set(spec_ids)
    target_ids = {
        row.get("bundle_id")
        for row in report_members
        if isinstance(row.get("bundle_id"), str)
    }
    semantics = report.get("consumption_semantics_id")
    if semantics not in _SEMANTICS_IDS:
        raise MintError("extraction report consumption_semantics_id is unknown")
    if (
        expected_consumption_semantics_id is not None
        and semantics != expected_consumption_semantics_id
    ):
        raise MintError(
            "extraction report consumption_semantics_id differs from explicit dispatch"
        )
    operative_summaries, actual_semantics = consumption_authenticator(
        paths.evidence_root,
        referenced_bundle_ids,
        expected_basis_sha256,
        target_bundle_ids=target_ids,
        consumption_semantics_id=expected_consumption_semantics_id,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
    )
    if semantics != actual_semantics:
        raise MintError(
            "extraction report consumption_semantics_id differs from "
            "authenticated source consumption"
        )
    if not target_ids.issubset(operative_summaries):
        raise MintError("authenticated consumption omitted target report members")
    members = tuple(
        _strict_bundle(
            paths.evidence_root,
            row.get("bundle_id"),
            row,
            strict_validator,
            operative_summary=(
                operative_summaries.get(row.get("bundle_id"))
                if isinstance(row.get("bundle_id"), str)
                else None
            ),
        )
        for row in report_members
    )
    for member, report_row in zip(members, report_members, strict=True):
        _verify_source_order_tags(
            member,
            report_row,
            comparative=paths.expected_kind == "comparative",
        )
    _validate_order(
        order,
        target_ids=[member.bundle_id for member in members],
        spec_ids=spec_ids,
    )
    campaign_rows, campaign_raw = _load_json_lines(
        paths.evidence_root / "campaign_log.jsonl", "campaign log"
    )
    campaign_log_sha256 = _sha256(campaign_raw)
    evaluation_basis = _authenticated_evaluation_basis(
        campaign_rows, expected_basis_sha256
    )
    basis_members = frozenset(
        item["bundle_id"] for item in evaluation_basis["member_occurrences"]
    )
    if not set(spec_ids).issubset(basis_members):
        raise MintError(
            "extraction-spec members are not a subset of the evaluation basis"
        )
    allowance = cell.get("whole_window_drift_allowance")
    if not isinstance(allowance, Mapping):
        raise MintError("target report cell has no whole-window drift allowance")
    basis_sha256 = allowance.get("whole_window_evaluation_basis_sha256")
    if basis_sha256 != expected_basis_sha256:
        raise MintError("component whole-window evaluation basis is not pinned")
    floor_basis = cell["floor"].get("whole_window_drift_allowance_provenance")
    if not isinstance(floor_basis, Mapping) or dict(floor_basis) != dict(allowance):
        raise MintError("floor allowance provenance differs from component allowance")

    campaign_log_path = paths.evidence_root / "campaign_log.jsonl"
    try:
        allowance_session = AuthenticatedConsumptionSession(
            paths.evidence_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=expected_basis_sha256,
            consumption_semantics_id=(
                expected_consumption_semantics_id
                or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            ),
            calibration_ledger_snapshot=calibration_ledger_snapshot,
        )
        allowance_result = allowance_deriver(
            paths.evidence_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=expected_basis_sha256,
            consumption_session=allowance_session,
            consumption_semantics_id=expected_consumption_semantics_id,
        )
    except Exception as exc:
        if (
            _sha256_file(campaign_log_path, "campaign log")
            != campaign_log_sha256
        ):
            raise MintError(
                "campaign log changed during whole-window allowance "
                "re-derivation"
            ) from exc
        raise MintError(
            "whole-window drift allowance is not derivable from "
            f"authenticated campaign evidence: {type(exc).__name__}: {exc}"
        ) from exc
    # The derivation re-reads campaign_log.jsonl. Re-pin the bytes afterward
    # so the authenticated input and the derivation input share one custody
    # identity even if the file was concurrently replaced.
    if _sha256_file(campaign_log_path, "campaign log") != campaign_log_sha256:
        raise MintError(
            "campaign log changed during whole-window allowance re-derivation"
        )
    if getattr(allowance_result, "status", None) != "allowances":
        raise MintError(
            "whole-window drift allowance is not derivable from "
            "authenticated campaign evidence "
            f"(status={getattr(allowance_result, 'status', None)!r})"
        )
    derived_allowances = getattr(allowance_result, "allowances", None)
    claim_family = neg8_claim_family_for_metric(METRIC)
    derived_allowance = (
        derived_allowances.get(claim_family)
        if isinstance(derived_allowances, Mapping)
        else None
    )
    if not isinstance(derived_allowance, Mapping):
        raise MintError(
            "authenticated whole-window drift allowance is missing "
            f"claim family {claim_family!r}"
        )
    # Both records are JSON-number mappings parsed by Python. Exact nested
    # equality enforces the contract's "differs in any way" rule, including
    # sub-microjoule substitutions and non-numeric provenance changes.
    if dict(derived_allowance) != dict(allowance):
        raise MintError(
            "report whole-window drift allowance differs from "
            "authenticated source re-derivation"
        )

    regime, scientific_hash, backend = _source_regime(members)
    return AuthenticatedComponent(
        evidence_root_id=paths.evidence_root_id,
        calibration_cell_id=paths.calibration_cell_id,
        kind=paths.expected_kind,
        report=report,
        report_sha256=_sha256(report_raw),
        spec=spec,
        spec_sha256=_sha256(spec_raw),
        order_manifest=order,
        order_manifest_sha256=_sha256(order_raw),
        campaign_log_sha256=campaign_log_sha256,
        cell=cell,
        spec_cell=spec_cell,
        members=members,
        widths_j=widths,
        whole_window_evaluation_basis_sha256=basis_sha256,
        evaluation_basis_member_count=len(basis_members),
        consumption_semantics_id=semantics,
        whole_window_drift_allowance=dict(allowance),
        source_regime=regime,
        scientific_config_identity_sha256=scientific_hash,
        backend=backend,
        whole_window_calibration_bracket=(
            dict(evaluation_basis["calibration_bracket_set"])
            if isinstance(
                evaluation_basis.get("calibration_bracket_set"), Mapping
            )
            else None
        ),
    )


def _definition_binding(component: AuthenticatedComponent) -> Mapping[str, Any]:
    bindings = component.spec_cell.get("condition_family_definitions")
    if not isinstance(bindings, Mapping):
        raise MintError("target spec cell lacks condition-family definitions")
    key = "all" if component.kind == "absolute" else "A"
    binding = bindings.get(key)
    if not isinstance(binding, Mapping):
        raise MintError(f"target spec cell lacks condition-family binding {key!r}")
    return binding


def _diagnostics_are_nonpublishing(
    value: object, *, diagnostic_context: bool = False
) -> bool:
    if isinstance(value, Mapping):
        is_diagnostic = diagnostic_context or (
            value.get("label") == "repeatability_diagnostic"
        )
        if is_diagnostic and value.get("published_claim_floor") is not False:
            return False
        for key, child in value.items():
            if key == "published_claim_floor" and child is not False:
                return False
            if not _diagnostics_are_nonpublishing(
                child,
                diagnostic_context=key in {
                    "point_floor_diagnostic",
                    "point_floor_diagnostics",
                },
            ):
                return False
    elif isinstance(value, list):
        return all(_diagnostics_are_nonpublishing(child) for child in value)
    return True


def pre_registration_gate(
    *,
    plan: Mapping[str, Any],
    plan_sha256: str,
    absolute: AuthenticatedComponent,
    comparative: AuthenticatedComponent,
) -> None:
    """Enforce the ratified mint-1 literals before any builder call."""

    if plan_sha256 != PLAN_SHA256:
        raise MintError("pre-registration gate: calibration plan sha256 mismatch")
    if (
        plan.get("plan_id") != "p2-015-window-a-m3max-qwen25-1p5b-v1"
        or plan.get("calibration_scope") != PLAN_DECLARED_SCOPE
    ):
        raise MintError("pre-registration gate: calibration plan identity mismatch")
    if absolute.evidence_root_id != "a10" or comparative.evidence_root_id != "window_c":
        raise MintError(
            "pre-registration gate: components require distinct a10/window_c roots"
        )
    if (
        absolute.whole_window_evaluation_basis_sha256
        != A10_EVALUATION_BASIS_SHA256
        or comparative.whole_window_evaluation_basis_sha256
        != WINDOW_C_EVALUATION_BASIS_SHA256
    ):
        raise MintError("pre-registration gate: component evaluation bases mismatch")
    if (
        absolute.evaluation_basis_member_count != A10_EVALUATION_BASIS_MEMBERS
        or comparative.evaluation_basis_member_count
        != WINDOW_C_EVALUATION_BASIS_MEMBERS
    ):
        raise MintError("pre-registration gate: evaluation-basis member count mismatch")
    if (
        len(_spec_member_ids(absolute.spec)) != A10_SPEC_MEMBERS
        or len(_spec_member_ids(comparative.spec)) != WINDOW_C_SPEC_MEMBERS
    ):
        raise MintError("pre-registration gate: extraction-spec membership mismatch")
    if (
        absolute.cell["floor"].get("n") != EXPECTED_ABSOLUTE_N
        or len(absolute.members) != EXPECTED_ABSOLUTE_N
        or comparative.cell["floor"].get("n") != EXPECTED_COMPARATIVE_N_BLOCKS
        or len(comparative.members) != 4 * EXPECTED_COMPARATIVE_N_BLOCKS
    ):
        raise MintError("pre-registration gate: absolute/comparative n mismatch")
    if absolute.order_manifest.get("manifest_id") != A10_ORDER_MANIFEST_ID:
        raise MintError("pre-registration gate: a10 order manifest mismatch")
    if (
        comparative.order_manifest.get("manifest_id")
        != WINDOW_C_ORDER_MANIFEST_ID
    ):
        raise MintError("pre-registration gate: window-C order manifest mismatch")
    if (
        absolute.order_manifest.get("calibration_plan_sha256") != PLAN_SHA256
        or comparative.order_manifest.get("calibration_plan_sha256")
        != PLAN_SHA256
        or absolute.order_manifest.get("plan_id") != plan.get("plan_id")
        or comparative.order_manifest.get("plan_id") != plan.get("plan_id")
    ):
        raise MintError("pre-registration gate: order manifest plan pin mismatch")
    if absolute.consumption_semantics_id not in _SEMANTICS_IDS or (
        comparative.consumption_semantics_id not in _SEMANTICS_IDS
    ):
        raise MintError("pre-registration gate: unknown consumption semantics")

    absolute_binding = _definition_binding(absolute)
    comparative_bindings = comparative.spec_cell.get(
        "condition_family_definitions"
    )
    if (
        not isinstance(comparative_bindings, Mapping)
        or comparative_bindings.get("A") != comparative_bindings.get("B")
        or absolute_binding != comparative_bindings.get("A")
        or absolute_binding.get("condition_family_id") != CONDITION_FAMILY_ID
        or absolute_binding.get("condition_family_sha256")
        != CONDITION_FAMILY_SHA256
        or absolute_binding.get("condition_family_definition", {}).get(
            "abba_alias_relation"
        )
        != "A_equals_B"
    ):
        raise MintError("pre-registration gate: window-C is not the pinned A==B null")
    allowance = _finite(
        absolute.whole_window_drift_allowance.get("allowance_j"),
        "a10 whole-window allowance",
        nonnegative=True,
    )
    if not math.isclose(
        allowance, A10_DRIFT_ALLOWANCE_J, rel_tol=0.0, abs_tol=1e-12
    ):
        raise MintError("pre-registration gate: a10 drift allowance mismatch")
    comparative_allowance = _finite(
        comparative.whole_window_drift_allowance.get("allowance_j"),
        "window-C comparative whole-window allowance",
        nonnegative=True,
    )
    if not math.isclose(
        comparative_allowance,
        WINDOW_C_DRIFT_ALLOWANCE_J,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise MintError(
            "pre-registration gate: window-C drift allowance mismatch"
        )
    operative = max(
        _finite(
            absolute.cell["floor"].get("drift_widened_guarded_floor_j"),
            "absolute operative floor",
            nonnegative=True,
        ),
        _finite(
            comparative.cell["floor"].get("drift_widened_guarded_floor_j"),
            "comparative operative floor",
            nonnegative=True,
        ),
    )
    if format(operative, ".6f") != EXPECTED_OPERATIVE_FLOOR_TEXT:
        raise MintError("pre-registration gate: formatted operative floor mismatch")
    if not _diagnostics_are_nonpublishing(absolute.report) or not (
        _diagnostics_are_nonpublishing(comparative.report)
    ):
        raise MintError(
            "pre-registration gate: diagnostic floor is marked as published"
        )
    if absolute.scientific_config_identity_sha256 != (
        comparative.scientific_config_identity_sha256
    ):
        raise MintError("pre-registration gate: scientific config identity mismatch")
    if absolute.source_regime["stack_identity_sha256"] != (
        comparative.source_regime["stack_identity_sha256"]
    ):
        raise MintError("pre-registration gate: stack identity mismatch")
    if absolute.backend != comparative.backend:
        raise MintError("pre-registration gate: telemetry backend mismatch")


def _absolute_observations(
    component: AuthenticatedComponent,
) -> list[Mapping[str, Any]]:
    return [
        {
            "bundle_id": member.bundle_id,
            "bundle_sha256": member.bundle_sha256,
            "config_sha256": member.config_sha256,
            "metric_value_j": member.metric_value_j,
        }
        for member in component.members
    ]


def _comparative_blocks(
    component: AuthenticatedComponent,
) -> tuple[list[Mapping[str, Any]], list[float]]:
    blocks = component.spec_cell["blocks"]
    member_by_id = {member.bundle_id: member for member in component.members}
    result: list[Mapping[str, Any]] = []
    deltas: list[float] = []
    for spec_block in blocks:
        block_id = spec_block["block_id"]
        ids = spec_block["members"]
        values = {
            position: member_by_id[ids[position]].metric_value_j
            for position in _ABBA_POSITIONS
        }
        delta = abba_delta(
            values["A1"], values["B1"], values["B2"], values["A2"]
        )
        deltas.append(delta)
        result.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": [
                    {
                        "position": position,
                        "bundle_id": member_by_id[ids[position]].bundle_id,
                        "bundle_sha256": member_by_id[
                            ids[position]
                        ].bundle_sha256,
                        "config_sha256": member_by_id[
                            ids[position]
                        ].config_sha256,
                        "metric_value_j": values[position],
                    }
                    for position in _ABBA_POSITIONS
                ],
                "delta_j": delta,
            }
        )
    return result, deltas


def _component_provenance(
    component: AuthenticatedComponent,
) -> Mapping[str, Any]:
    return {
        "calibration_cell_id": component.calibration_cell_id,
        "evidence_root_id": component.evidence_root_id,
        "order_manifest": {
            "manifest_id": component.order_manifest["manifest_id"],
            "sha256": component.order_manifest_sha256,
        },
        "campaign_log": {"sha256": component.campaign_log_sha256},
        "extraction_report": {"sha256": component.report_sha256},
        "extraction_spec": {"sha256": component.spec_sha256},
        "bundle_ids": [member.bundle_id for member in component.members],
        "bundle_sha256s": [
            member.bundle_sha256 for member in component.members
        ],
        "source_regime": component.source_regime,
    }


def mint_authenticated_artifact(
    *,
    artifact_id: str,
    plan: Mapping[str, Any],
    plan_sha256: str,
    calibration_plan_relative_path: str,
    absolute: AuthenticatedComponent,
    comparative: AuthenticatedComponent,
    project_commit: str,
    project_tree_state: str,
) -> dict[str, Any]:
    """Run the gate, then construct and validate the one governed artifact."""

    pre_registration_gate(
        plan=plan,
        plan_sha256=plan_sha256,
        absolute=absolute,
        comparative=comparative,
    )
    relative_plan = _safe_relative_posix(
        calibration_plan_relative_path,
        "calibration_plan.relative_path",
    )
    if re.fullmatch(r"[0-9a-f]{40}", project_commit) is None:
        raise MintError("project_commit must be 40 lowercase hex chars")
    if project_tree_state not in {"clean", "dirty"}:
        raise MintError("project_tree_state must be 'clean' or 'dirty'")

    abs_estimate = absolute_false_effect_floor(
        [member.metric_value_j for member in absolute.members],
        admissible_half_widths_j=absolute.widths_j,
    )
    absolute_record = build_absolute_record(
        abs_estimate,
        _absolute_observations(absolute),
        consumption_semantics_id=absolute.consumption_semantics_id,
        whole_window_drift_allowance=absolute.whole_window_drift_allowance,
    )
    comparative_blocks, deltas = _comparative_blocks(comparative)
    cmp_estimate = comparative_false_effect_floor(
        deltas,
        admissible_half_widths_j=comparative.widths_j,
    )
    comparative_record = build_comparative_record(
        cmp_estimate,
        comparative_blocks,
        consumption_semantics_id=comparative.consumption_semantics_id,
        whole_window_drift_allowance=comparative.whole_window_drift_allowance,
    )

    binding = _definition_binding(absolute)
    definition = binding["condition_family_definition"]
    if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition) != (
        CONDITION_FAMILY_SHA256
    ):
        raise MintError("condition-family definition hash changed after gate")
    cell = build_floor_cell(
        cell_id=CELL_ID,
        key={
            "backend": absolute.backend,
            "metric": METRIC,
            "window_class": WINDOW_CLASS,
            "condition_family_id": CONDITION_FAMILY_ID,
            "condition_family_definition": definition,
            "condition_family_sha256": CONDITION_FAMILY_SHA256,
        },
        eligibility={
            "use_role": "primary_claim_gate",
            "minimum_claim_n": 10,
            "status": "claim_ready",
            "claim_usable": True,
            "reason_codes": [],
        },
        absolute=absolute_record,
        comparative=comparative_record,
        transport_group_id=TRANSPORT_GROUP_ID,
        provenance={
            "absolute": _component_provenance(absolute),
            "comparative": _component_provenance(comparative),
        },
    )
    group = build_transport_group(
        transport_group_id=TRANSPORT_GROUP_ID,
        backend=absolute.backend,
        metric=METRIC,
        window_class=WINDOW_CLASS,
        stack_identity=cell["source_regime"]["stack_identity"],
        source_cells=[cell],
        allowed_consumer_condition_families=[
            {
                "condition_family_id": CONDITION_FAMILY_ID,
                "condition_family_definition": definition,
                "condition_family_sha256": CONDITION_FAMILY_SHA256,
            }
        ],
    )
    artifact = build_floor_artifact(
        artifact_id=artifact_id,
        calibration_scope=CALIBRATION_SCOPE,
        source_class=SOURCE_CLASS,
        provenance={
            "calibration_plan": {
                "plan_id": plan["plan_id"],
                "declared_calibration_scope": PLAN_DECLARED_SCOPE,
                "relative_path": relative_plan,
                "sha256": plan_sha256,
            },
            "mint_tool_version": MINT_TOOL_VERSION,
            "implementation": {
                "project_commit": project_commit,
                "project_tree_state": project_tree_state,
                "python_package": "joulewise",
            },
        },
        cells=[cell],
        transport_groups=[group],
    )
    artifact_cell = artifact["cells"][0]
    if format(artifact_cell["floor_gate_j"], ".6f") != (
        EXPECTED_OPERATIVE_FLOOR_TEXT
    ):
        raise MintError("post-construction floor_gate_j headline mismatch")
    if artifact_cell["floor_gate_j"] != group["composed_floor_gate_j"]:
        raise MintError("post-construction transport headline mismatch")
    errors = validate_floor_artifact(artifact)
    if errors:
        raise MintError(f"constructed artifact is invalid: {errors[0]}")
    _assert_path_independent(artifact)
    return artifact


def _resolve_plan_path(floor_path: Path, relative_path: object) -> Path:
    relative = _safe_relative_posix(
        relative_path, "artifact.provenance.calibration_plan.relative_path"
    )
    root = floor_path.parent.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise MintError("calibration plan escapes the artifact root") from exc
    return candidate


def _record_rows(component_name: str, cell: Mapping[str, Any]) -> list[Mapping]:
    record = cell.get(component_name)
    if not isinstance(record, Mapping):
        return []
    if component_name == "absolute":
        rows = record.get("bundle_observations")
        return list(rows) if isinstance(rows, list) else []
    result: list[Mapping] = []
    blocks = record.get("blocks")
    if isinstance(blocks, list):
        for block in blocks:
            members = block.get("members") if isinstance(block, Mapping) else None
            if isinstance(members, list):
                result.extend(row for row in members if isinstance(row, Mapping))
    return result


def _binding_cache_key(
    root: Path,
    basis_sha256: str,
    rows: Sequence[Mapping[str, Any]],
) -> tuple[str, str, tuple[tuple[str, str], ...]]:
    members: list[tuple[str, str]] = []
    for row in rows:
        bundle_id = row.get("bundle_id")
        bundle_sha256 = row.get("bundle_sha256")
        if not isinstance(bundle_id, str) or not isinstance(bundle_sha256, str):
            raise MintError("component rows lack bundle identity hashes")
        members.append((bundle_id, bundle_sha256))
    return (str(root.resolve()), basis_sha256, tuple(members))


def bind_floor_artifact_evidence(
    artifact: Mapping[str, Any],
    floor_path: Path,
    evidence_roots: Mapping[str, Path],
    *,
    strict_validator: StrictValidator,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
) -> Mapping[str, tuple[str, ...]]:
    """Rebind a constructed artifact to plan, campaign, and bundle bytes.

    The plan is resolved from its persisted safe-relative path.  Each
    component's campaign log and bundle basenames are resolved only beneath
    the root selected by that component's ``evidence_root_id``.
    """

    if calibration_ledger_snapshot is None:
        acceptance = load_calibration_acceptance_bound()
        cutoff = (
            acceptance.get("ledger_cutoff")
            if isinstance(acceptance, Mapping)
            else None
        )
        calibration_ledger_snapshot = load_calibration_ledger_snapshot(
            baseline_sequence=(
                cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
            ),
            baseline_digest=(
                cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
            ),
        )
    validator_errors = validate_floor_artifact(artifact)
    if validator_errors:
        raise MintError(f"cannot bind invalid floor artifact: {validator_errors[0]}")
    _assert_path_independent(artifact)
    provenance = artifact.get("provenance")
    plan_pin = (
        provenance.get("calibration_plan")
        if isinstance(provenance, Mapping)
        else None
    )
    if not isinstance(plan_pin, Mapping):
        raise MintError("artifact calibration-plan provenance is missing")
    plan_path = _resolve_plan_path(Path(floor_path), plan_pin.get("relative_path"))
    plan, plan_raw = _load_json_object(plan_path, "calibration plan")
    if _sha256(plan_raw) != plan_pin.get("sha256"):
        raise MintError("calibration plan bytes do not match artifact sha256")
    if (
        plan.get("plan_id") != plan_pin.get("plan_id")
        or plan.get("calibration_scope")
        != plan_pin.get("declared_calibration_scope")
    ):
        raise MintError("calibration plan bytes do not match declared provenance")
    # Deliberately do not compare artifact["calibration_scope"] with the
    # historical plan declaration: Q2 requires production_window vs window_a.

    result: dict[str, tuple[str, ...]] = {}
    for cell in artifact.get("cells", []):
        if not isinstance(cell, Mapping):
            continue
        cell_provenance = cell.get("provenance")
        if not isinstance(cell_provenance, Mapping):
            continue
        for component_name in ("absolute", "comparative"):
            component = cell_provenance.get(component_name)
            if not isinstance(component, Mapping):
                continue
            root_id = component.get("evidence_root_id")
            root_value = evidence_roots.get(root_id) if isinstance(root_id, str) else None
            if root_value is None:
                raise MintError(f"missing evidence-root mapping for {root_id!r}")
            root = Path(root_value)
            if not root.is_dir():
                raise MintError(f"evidence root {root_id!r} is not a directory")
            campaign_sha256 = _sha256_file(
                root / "campaign_log.jsonl", f"{root_id} campaign log"
            )
            if campaign_sha256 != component.get("campaign_log", {}).get("sha256"):
                raise MintError(f"{root_id}: campaign log sha256 mismatch")
            record_rows = _record_rows(component_name, cell)
            record = cell.get(component_name)
            basis_sha256 = (
                record.get("whole_window_evaluation_basis_sha256")
                if isinstance(record, Mapping)
                else None
            )
            semantics = (
                record.get("consumption_semantics_id")
                if isinstance(record, Mapping)
                else None
            )
            if (
                not isinstance(basis_sha256, str)
                or semantics not in _SEMANTICS_IDS
            ):
                raise MintError(f"{root_id}: component consumption wire is invalid")
            cache_key = _binding_cache_key(root, basis_sha256, record_rows)
            operative_summaries = _BINDING_SUMMARY_CACHE.get(cache_key)
            if operative_summaries is None:
                operative_summaries, actual_semantics = (
                    _authenticated_consumption_summaries(
                        root,
                        {
                            str(row["bundle_id"])
                            for row in record_rows
                        },
                        basis_sha256,
                        target_bundle_ids={
                            str(row["bundle_id"])
                            for row in record_rows
                        },
                        consumption_semantics_id=semantics,
                        calibration_ledger_snapshot=calibration_ledger_snapshot,
                    )
                )
                if actual_semantics != semantics:
                    raise MintError(
                        f"{root_id}: artifact consumption semantics differ "
                        "from authenticated source consumption"
                    )
            record_ids = {str(row.get("bundle_id")) for row in record_rows}
            if not record_ids.issubset(operative_summaries):
                raise MintError(
                    f"{root_id}: authenticated consumption omitted artifact members"
                )
            rebound: list[str] = []
            rebound_member_widths: list[float] = []
            stack_hashes: set[str] = set()
            for row in record_rows:
                member = _strict_bundle(
                    root,
                    row.get("bundle_id"),
                    row,
                    strict_validator,
                    operative_summary=operative_summaries.get(
                        str(row.get("bundle_id"))
                    ),
                )
                stack = _derive_stack_identity(
                    member.raw_config, member.metadata
                )
                stack_hashes.add(
                    canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack)
                )
                rebound.append(member.bundle_sha256)
                if member.admissible_half_width_j is None:
                    raise MintError(
                        f"{member.bundle_id}: source admissible width unavailable"
                    )
                rebound_member_widths.append(member.admissible_half_width_j)
            expected_hashes = component.get("bundle_sha256s")
            if rebound != expected_hashes:
                raise MintError(
                    f"{root_id}: rebound bundle hashes differ from component provenance"
                )
            expected_stack = component.get("source_regime", {}).get(
                "stack_identity_sha256"
            )
            if stack_hashes != {expected_stack}:
                raise MintError(f"{root_id}: source stack differs from artifact")
            stored_widths = (
                record.get("admissible_half_widths_j")
                if isinstance(record, Mapping)
                else None
            )
            if component_name == "absolute":
                rebound_widths = rebound_member_widths
            else:
                if len(rebound_member_widths) % 4:
                    raise MintError(
                        f"{root_id}: comparative member count is not divisible by four"
                    )
                rebound_widths = [
                    math.fsum(rebound_member_widths[index : index + 4]) / 2.0
                    for index in range(0, len(rebound_member_widths), 4)
                ]
            if not isinstance(stored_widths, list) or (
                len(stored_widths) != len(rebound_widths)
            ) or any(
                not math.isclose(
                    _finite(value, "artifact admissible width", nonnegative=True),
                    expected,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                )
                for value, expected in zip(stored_widths, rebound_widths)
            ):
                raise MintError(
                    f"{root_id}: artifact widths differ from authenticated source bytes"
                )
            result[component_name] = tuple(rebound)
    if set(result) != {"absolute", "comparative"}:
        raise MintError("claim-ready bind requires both component evidence roots")
    return result


def render_single_count_statement(artifact: Mapping[str, Any]) -> str:
    """Render the convenience prose only from the canonical artifact object."""

    expected = attribution_single_count_discipline()
    carried: list[Mapping[str, Any]] = []
    for cell in artifact.get("cells", []):
        if isinstance(cell, Mapping) and isinstance(
            cell.get("single_count_discipline"), Mapping
        ):
            carried.append(cell["single_count_discipline"])
    for group in artifact.get("transport_groups", []):
        if isinstance(group, Mapping) and isinstance(
            group.get("single_count_discipline"), Mapping
        ):
            carried.append(group["single_count_discipline"])
    if not carried:
        raise MintError("artifact does not carry a single-count discipline object")
    if any(dict(value) != expected for value in carried):
        raise MintError("artifact single-count discipline is not canonical")
    return (
        f"{expected['statement']}. "
        f"Formula: {expected['effective_clearable_effect_formula']}; "
        f"floor role: {expected['floor_role']}; "
        f"claim-side role: {expected['claim_side_bound_role']}; "
        f"claim-side source: {expected['claim_side_bound_source']}.\n"
    )


def _exclusive_write(path: Path, payload: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except FileExistsError as exc:
        raise MintError(f"refusing to overwrite existing output: {path}") from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def write_outputs_exclusive(
    artifact: Mapping[str, Any],
    floor_path: Path,
    statement_path: Path,
) -> None:
    """Write the artifact and convenience statement with O_EXCL semantics."""

    floor_path = Path(floor_path)
    statement_path = Path(statement_path)
    if floor_path == statement_path:
        raise MintError("artifact and statement outputs must differ")
    if floor_path.exists() or statement_path.exists():
        existing = floor_path if floor_path.exists() else statement_path
        raise MintError(f"refusing to overwrite existing output: {existing}")
    artifact_payload = (
        json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    statement_payload = render_single_count_statement(artifact).encode("utf-8")
    _exclusive_write(floor_path, artifact_payload)
    try:
        _exclusive_write(statement_path, statement_payload)
    except Exception:
        try:
            floor_path.unlink()
        except OSError:
            pass
        raise


def mint_floor_artifact(
    *,
    artifact_id: str,
    floor_path: Path,
    statement_path: Path,
    calibration_plan_path: Path,
    calibration_plan_relative_path: str,
    absolute_paths: ComponentPaths,
    comparative_paths: ComponentPaths,
    project_commit: str,
    project_tree_state: str,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None = None,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
) -> Mapping[str, Any]:
    """Authenticate, gate, construct, rebind, validate, and write mint #1."""

    plan, plan_raw = _load_json_object(calibration_plan_path, "calibration plan")
    plan_sha256 = _sha256(plan_raw)
    if calibration_ledger_snapshot is None:
        acceptance = load_calibration_acceptance_bound()
        cutoff = (
            acceptance.get("ledger_cutoff")
            if isinstance(acceptance, Mapping)
            else None
        )
        calibration_ledger_snapshot = load_calibration_ledger_snapshot(
            baseline_sequence=(
                cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
            ),
            baseline_digest=(
                cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
            ),
        )
    absolute = _authenticate_component(
        absolute_paths,
        expected_cell_id=A10_CELL_ID,
        expected_basis_sha256=A10_EVALUATION_BASIS_SHA256,
        strict_validator=strict_validator,
        expected_consumption_semantics_id=consumption_semantics_id,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
    )
    comparative = _authenticate_component(
        comparative_paths,
        expected_cell_id=WINDOW_C_CELL_ID,
        expected_basis_sha256=WINDOW_C_EVALUATION_BASIS_SHA256,
        strict_validator=strict_validator,
        expected_consumption_semantics_id=consumption_semantics_id,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
    )
    artifact = mint_authenticated_artifact(
        artifact_id=artifact_id,
        plan=plan,
        plan_sha256=plan_sha256,
        calibration_plan_relative_path=calibration_plan_relative_path,
        absolute=absolute,
        comparative=comparative,
        project_commit=project_commit,
        project_tree_state=project_tree_state,
    )
    cache_keys: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
    artifact_cell = artifact["cells"][0]
    for component_name, component, root in (
        ("absolute", absolute, absolute_paths.evidence_root),
        ("comparative", comparative, comparative_paths.evidence_root),
    ):
        rows = _record_rows(component_name, artifact_cell)
        cache_key = _binding_cache_key(
            root,
            component.whole_window_evaluation_basis_sha256,
            rows,
        )
        _BINDING_SUMMARY_CACHE[cache_key] = {
            member.bundle_id: member.summary for member in component.members
        }
        cache_keys.append(cache_key)
    try:
        bind_floor_artifact_evidence(
            artifact,
            floor_path,
            {
                absolute.evidence_root_id: absolute_paths.evidence_root,
                comparative.evidence_root_id: comparative_paths.evidence_root,
            },
            strict_validator=strict_validator,
            calibration_ledger_snapshot=calibration_ledger_snapshot,
        )
    finally:
        for cache_key in cache_keys:
            _BINDING_SUMMARY_CACHE.pop(cache_key, None)
    if validate_floor_artifact(artifact) != []:
        raise MintError("post-bind artifact validation failed")
    write_outputs_exclusive(artifact, floor_path, statement_path)
    return artifact


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--single-count-out", required=True, type=Path)
    parser.add_argument("--calibration-plan", required=True, type=Path)
    parser.add_argument("--calibration-plan-relative-path", required=True)
    parser.add_argument("--a10-root", required=True, type=Path)
    parser.add_argument("--a10-report", required=True, type=Path)
    parser.add_argument(
        "--a10-spec",
        type=Path,
        default=REPO_ROOT / "configs/floor_mint/a10_extraction_spec.json",
    )
    parser.add_argument("--a10-order-manifest", required=True, type=Path)
    parser.add_argument("--window-c-root", required=True, type=Path)
    parser.add_argument("--window-c-report", required=True, type=Path)
    parser.add_argument(
        "--window-c-spec",
        type=Path,
        default=REPO_ROOT / "configs/floor_mint/window_c_extraction_spec.json",
    )
    parser.add_argument("--window-c-order-manifest", required=True, type=Path)
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
        mint_floor_artifact(
            artifact_id=args.artifact_id,
            floor_path=args.out,
            statement_path=args.single_count_out,
            calibration_plan_path=args.calibration_plan,
            calibration_plan_relative_path=args.calibration_plan_relative_path,
            absolute_paths=ComponentPaths(
                evidence_root_id="a10",
                evidence_root=args.a10_root,
                report_path=args.a10_report,
                spec_path=args.a10_spec,
                order_manifest_path=args.a10_order_manifest,
                calibration_cell_id=A10_CELL_ID,
                expected_kind="absolute",
            ),
            comparative_paths=ComponentPaths(
                evidence_root_id="window_c",
                evidence_root=args.window_c_root,
                report_path=args.window_c_report,
                spec_path=args.window_c_spec,
                order_manifest_path=args.window_c_order_manifest,
                calibration_cell_id=WINDOW_C_CELL_ID,
                expected_kind="comparative",
            ),
            project_commit=args.project_commit,
            project_tree_state=args.project_tree_state,
            strict_validator=lambda path, strict: validate_bundle(
                path, strict=strict
            ),
            consumption_semantics_id=args.consumption_semantics_id,
        )
    except MintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
