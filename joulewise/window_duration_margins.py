"""Authenticated comparative-cell window-duration margin receipts.

The operator supplies only roots and a pack identity.  Comparative-cell
membership comes from the pack-pinned extraction spec (ALPHA/BETA) or the
pack-pinned ``analysis_manifest_v3.json`` (GAMMA).  Every numeric conclusion
is re-derived from authenticated collection bytes; ``summary_metrics.json``
is used only to cross-check the independent event/trace derivation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from joulewise.authentication_io import (
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    read_authentication_input,
    read_authentication_text,
)
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.cli import _strict_raw_to_trace_problems
from joulewise.reduce import (
    MIN_PHASE_SAMPLES,
    SHORT_WINDOW_CADENCE_RATIO_MIN,
    _in_window_sample_count,
    _window_gap_stats,
)
from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    AuthenticatedConsumptionSession,
    ordinary_present_bundle_paths,
    whole_window_refusal_reasons,
)


RECEIPT_SCHEMA_VERSION = "joulewise.window_duration_margins_receipt.v1"
RECEIPT_NAMESPACE = "window_duration_margins/v1"

RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "status",
        "pack_identity",
        "pack_tree_sha256",
        "registry_source_sha256",
        "evaluation_basis_sha256",
        "cell_inventory_sha256",
        "cells",
        "authoritative_inputs",
    }
)
CELL_KEYS = frozenset(
    {
        "cell_id",
        "metric",
        "membership_sha256",
        "member_count",
        "b_operative_s",
        "min_phase_window_duration_s",
        "min_phase_window_duration_bundle_id",
        "min_duration_minus_2b_operative_s",
        "min_duration_to_2b_operative_ratio",
        "min_overlapping_power_interval_count",
        "min_sample_count_margin",
        "min_reducer_cadence_ratio",
        "reducer_cadence_ratio_threshold",
        "members",
    }
)
MEMBER_KEYS = frozenset(
    {
        "bundle_id",
        "expected_config_sha256",
        "phase_window_start_s",
        "phase_window_end_s",
        "phase_window_duration_s",
        "overlapping_power_interval_count",
        "sample_count_margin",
        "reducer_cadence_ratio",
        "reducer_cadence_ratio_threshold",
    }
)
INPUT_KEYS = frozenset({"source", "sha256"})

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_PACK_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,191}")
_ABBA_POSITIONS = ("A1", "B1", "B2", "A2")


class WindowDurationMarginsRefusal(ValueError):
    """A closed, machine-readable refusal with no receipt publication."""

    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


@dataclass(frozen=True)
class RecordedWindowDurationMargins:
    path: Path
    sha256: str
    receipt: Mapping[str, Any]


@dataclass(frozen=True)
class _RegisteredCell:
    cell_id: str
    metric: str
    members: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class _MemberObservation:
    bundle_id: str
    expected_config_sha256: str
    phase: str
    start_s: float
    end_s: float
    duration_s: float
    overlapping_power_interval_count: int
    cadence_ratio: float
    cadence_ratio_threshold: float


def _refuse(reason: str, detail: str) -> None:
    raise WindowDurationMarginsRefusal(reason, detail)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256(_canonical_bytes(value))


def _receipt_bytes(receipt: Mapping[str, Any]) -> bytes:
    validate_window_duration_margins_receipt(receipt)
    return (
        json.dumps(
            receipt,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def render_window_duration_margins_receipt(
    receipt: Mapping[str, Any],
) -> bytes:
    """Return the deterministic UTF-8 representation of a valid receipt."""

    return _receipt_bytes(receipt)


def _json_object(
    path: Path,
    *,
    label: str,
) -> tuple[Mapping[str, Any], bytes]:
    raw = read_authentication_input(path, grammar="json", label=label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _refuse("authoritative_input_invalid", f"{label}: {exc}")
    if not isinstance(value, Mapping):
        _refuse("authoritative_input_invalid", f"{label} is not a JSON object")
    return value, raw


def _safe_relative_path(root: Path, text: Any, *, label: str) -> Path:
    if not isinstance(text, str) or not text:
        _refuse("pack_pin_invalid", f"{label} is not a nonempty relative path")
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts:
        _refuse("pack_pin_invalid", f"{label} escapes its governing root")
    candidate = (root / Path(*pure.parts)).resolve(strict=False)
    if candidate == root or root not in candidate.parents:
        _refuse("pack_pin_invalid", f"{label} escapes its governing root")
    return candidate


def _require_sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        _refuse("pack_pin_invalid", f"{label} is not 64 lowercase hex")
    return value


def _member_pin_map(value: Any, *, label: str) -> dict[str, str]:
    if not isinstance(value, list):
        _refuse("registered_membership_invalid", f"{label} is not an array")
    result: dict[str, str] = {}
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            _refuse(
                "registered_membership_invalid",
                f"{label}[{index}] is not an object",
            )
        bundle_id = row.get("bundle_id")
        config_sha = row.get("config_sha256")
        if (
            not isinstance(bundle_id, str)
            or not bundle_id
            or not isinstance(config_sha, str)
            or _SHA256_RE.fullmatch(config_sha) is None
            or bundle_id in result
        ):
            _refuse(
                "registered_membership_invalid",
                f"{label}[{index}] has a duplicate or malformed member pin",
            )
        result[bundle_id] = config_sha
    return result


def _floor_cells(spec: Mapping[str, Any]) -> list[_RegisteredCell]:
    if spec.get("schema_version") != "joulewise.detection_floor_extraction_spec.v1":
        _refuse("registered_cell_inventory_invalid", "unknown extraction-spec schema")
    raw_cells = spec.get("cells")
    if not isinstance(raw_cells, list):
        _refuse("registered_cell_inventory_invalid", "extraction-spec cells are absent")
    cells: list[_RegisteredCell] = []
    for index, raw_cell in enumerate(raw_cells):
        if not isinstance(raw_cell, Mapping) or raw_cell.get("kind") != "comparative":
            continue
        cell_id = raw_cell.get("cell_id")
        metric = raw_cell.get("metric")
        if not isinstance(cell_id, str) or not cell_id or not isinstance(metric, str):
            _refuse(
                "registered_cell_inventory_invalid",
                f"comparative extraction cell {index} lacks cell_id/metric",
            )
        pins = _member_pin_map(
            raw_cell.get("member_config_sha256"),
            label=f"{cell_id}.member_config_sha256",
        )
        blocks = raw_cell.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            _refuse("registered_membership_invalid", f"{cell_id} has no ABBA blocks")
        bundle_ids: list[str] = []
        for block_index, block in enumerate(blocks):
            members = block.get("members") if isinstance(block, Mapping) else None
            if not isinstance(members, Mapping) or set(members) != set(_ABBA_POSITIONS):
                _refuse(
                    "registered_membership_invalid",
                    f"{cell_id} block {block_index} is not an exact ABBA membership",
                )
            for position in _ABBA_POSITIONS:
                bundle_id = members.get(position)
                if not isinstance(bundle_id, str) or not bundle_id:
                    _refuse(
                        "registered_membership_invalid",
                        f"{cell_id} block {block_index} has a malformed {position}",
                    )
                bundle_ids.append(bundle_id)
        if len(set(bundle_ids)) != len(bundle_ids):
            _refuse("member_non_unique", f"{cell_id} repeats a registered member")
        if set(bundle_ids) != set(pins):
            _refuse(
                "registered_membership_invalid",
                f"{cell_id} member pins do not exactly cover its ABBA membership",
            )
        cells.append(
            _RegisteredCell(
                cell_id=cell_id,
                metric=metric,
                members=tuple((bundle_id, pins[bundle_id]) for bundle_id in bundle_ids),
            )
        )
    return cells


def _gamma_cells(manifest: Mapping[str, Any]) -> list[_RegisteredCell]:
    if manifest.get("schema_version") != "joulewise.analysis_manifest.v3.prospective":
        _refuse("registered_cell_inventory_invalid", "unknown GAMMA analysis schema")
    contrasts = manifest.get("contrasts")
    if not isinstance(contrasts, list):
        _refuse("registered_cell_inventory_invalid", "GAMMA contrasts are absent")
    cells: list[_RegisteredCell] = []
    for index, contrast in enumerate(contrasts):
        if not isinstance(contrast, Mapping):
            _refuse(
                "registered_cell_inventory_invalid",
                f"GAMMA contrast {index} is not an object",
            )
        cell_id = contrast.get("contrast_id")
        metric = contrast.get("metric")
        members = contrast.get("members")
        if (
            not isinstance(cell_id, str)
            or not cell_id
            or not isinstance(metric, str)
            or not isinstance(members, list)
            or not members
        ):
            _refuse(
                "registered_cell_inventory_invalid",
                f"GAMMA contrast {index} lacks identity, metric, or members",
            )
        registered: list[tuple[str, str]] = []
        for member_index, member in enumerate(members):
            bundle_id = member.get("run_id") if isinstance(member, Mapping) else None
            config_sha = (
                member.get("config_sha256") if isinstance(member, Mapping) else None
            )
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or not isinstance(config_sha, str)
                or _SHA256_RE.fullmatch(config_sha) is None
            ):
                _refuse(
                    "registered_membership_invalid",
                    f"{cell_id} member {member_index} has no valid run/config pin",
                )
            registered.append((bundle_id, config_sha))
        if len({bundle_id for bundle_id, _sha in registered}) != len(registered):
            _refuse("member_non_unique", f"{cell_id} repeats a registered member")
        cells.append(_RegisteredCell(cell_id, metric, tuple(registered)))
    return cells


def _pack_inventory(
    repository_root: Path,
    pack_root: Path,
    pack_identity: str,
) -> tuple[str, str, list[_RegisteredCell]]:
    if _PACK_ID_RE.fullmatch(pack_identity) is None:
        _refuse("pack_identity_invalid", "pack identity is not namespace-safe")
    tree_path = pack_root / "plan_tree.json"
    sidecar_path = pack_root / "plan_tree.sha256"
    tree, tree_raw = _json_object(tree_path, label="pack plan_tree.json")
    if tree.get("schema_version") != "joulewise.d117_plan_tree.v1":
        _refuse("pack_pin_invalid", "unknown plan-tree schema")
    try:
        sidecar = read_authentication_text(
            sidecar_path,
            grammar="raw",
            label="pack plan_tree.sha256",
            encoding="utf-8",
        )
    except UnicodeDecodeError as exc:
        _refuse("pack_pin_invalid", f"plan-tree sidecar is not UTF-8: {exc}")
    match = re.fullmatch(r"([0-9a-f]{64})  plan_tree\.json\n?", sidecar)
    tree_sha = _sha256(tree_raw)
    if match is None or match.group(1) != tree_sha:
        _refuse("pack_pin_invalid", "plan_tree.sha256 does not pin plan_tree.json")
    plan = tree.get("plan")
    window_identity = tree.get("window_identity")
    if (
        not isinstance(plan, Mapping)
        or not isinstance(window_identity, Mapping)
        or plan.get("plan_id") != pack_identity
        or not isinstance(plan.get("actual_sha256"), str)
        or _SHA256_RE.fullmatch(plan["actual_sha256"]) is None
        or window_identity.get("window_id") != pack_identity
    ):
        _refuse("pack_identity_invalid", "operator pack identity is not pack-derived")
    downstream = tree.get("downstream_contract")
    if not isinstance(downstream, Mapping):
        _refuse("pack_pin_invalid", "plan tree has no downstream contract")
    extraction = downstream.get("extraction_spec")
    analysis_path = downstream.get("analysis_manifest_path")
    if isinstance(extraction, Mapping) and analysis_path is None:
        registry_path = _safe_relative_path(
            repository_root,
            extraction.get("path"),
            label="downstream extraction-spec path",
        )
        expected_sha = _require_sha256(
            extraction.get("sha256"), label="downstream extraction-spec sha256"
        )
        registry, registry_raw = _json_object(
            registry_path, label="pack-pinned extraction spec"
        )
        cells = _floor_cells(registry)
    elif analysis_path is not None and extraction is None:
        registry_path = _safe_relative_path(
            pack_root,
            analysis_path,
            label="downstream analysis-manifest path",
        )
        expected_sha = _require_sha256(
            downstream.get("analysis_manifest_sha256"),
            label="downstream analysis-manifest sha256",
        )
        registry, registry_raw = _json_object(
            registry_path, label="pack-pinned GAMMA analysis manifest"
        )
        cells = _gamma_cells(registry)
        manifest_plan = registry.get("plan")
        if (
            not isinstance(manifest_plan, Mapping)
            or manifest_plan.get("plan_id") != pack_identity
            or manifest_plan.get("sha256") != plan.get("actual_sha256")
        ):
            _refuse(
                "pack_pin_invalid",
                "GAMMA analysis manifest does not bind the pack plan",
            )
    else:
        _refuse(
            "registered_cell_inventory_invalid",
            "pack must select exactly one comparative-cell registry source",
        )
    registry_sha = _sha256(registry_raw)
    if registry_sha != expected_sha:
        _refuse("pack_pin_invalid", "registered-cell source sha256 mismatches plan tree")
    if not cells:
        _refuse("registered_cell_inventory_invalid", "pack registers no comparative cells")
    cell_ids = [cell.cell_id for cell in cells]
    if len(set(cell_ids)) != len(cell_ids):
        _refuse("registered_cell_inventory_invalid", "comparative cell_id is duplicated")
    return tree_sha, registry_sha, sorted(cells, key=lambda cell: cell.cell_id)


def _resolve_member_paths(
    runs_root: Path,
    cells: Sequence[_RegisteredCell],
) -> dict[str, Path]:
    referenced = sorted(
        {bundle_id for cell in cells for bundle_id, _sha in cell.members}
    )
    result: dict[str, Path] = {}
    for bundle_id in referenced:
        present = ordinary_present_bundle_paths(runs_root, bundle_id)
        if not present:
            _refuse("member_missing", f"registered member {bundle_id!r} is absent")
        if len(present) != 1:
            _refuse(
                "member_non_unique",
                f"registered member {bundle_id!r} has {len(present)} present bundles",
            )
        result[bundle_id] = present[0]
    return result


def _phase_for_metric(metric: str, *, cell_id: str) -> str:
    prefix = "phase_energy_j."
    if not metric.startswith(prefix) or not metric[len(prefix) :]:
        _refuse(
            "registered_cell_inventory_invalid",
            f"{cell_id} metric is not a phase_energy_j metric",
        )
    return metric[len(prefix) :]


def _finite_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _observe_member(
    bundle_id: str,
    expected_config_sha256: str,
    phase: str,
    path: Path,
) -> _MemberObservation:
    try:
        config_raw = read_authentication_input(
            path / "config.json",
            grammar="json",
            label=f"{bundle_id} config",
        )
    except OSError as exc:
        _refuse("member_config_mismatch", f"{bundle_id}: config is unreadable: {exc}")
    if _sha256(config_raw) != expected_config_sha256:
        _refuse(
            "member_config_mismatch",
            f"{bundle_id}: config bytes do not match the pack pin",
        )
    reader = BundleReader(path)
    try:
        config = reader.config()
        backend = config.hardware_target.telemetry_backend.value
    except (BundleReadError, ValueError) as exc:
        _refuse("raw_to_trace_replay_failed", f"{bundle_id}: {exc}")
    if config.run_id != bundle_id:
        _refuse(
            "member_config_mismatch",
            f"{bundle_id}: authenticated config run_id does not match membership",
        )
    if backend != "powermetrics" or not (
        path / "raw" / "powermetrics.plist"
    ).is_file():
        _refuse(
            "raw_to_trace_replay_failed",
            f"{bundle_id}: authoritative raw/powermetrics.plist is unavailable",
        )
    try:
        replay_problems = _strict_raw_to_trace_problems(reader)
    except (BundleReadError, OSError, TypeError, ValueError) as exc:
        _refuse("raw_to_trace_replay_failed", f"{bundle_id}: {exc}")
    if replay_problems:
        _refuse(
            "raw_to_trace_replay_failed",
            f"{bundle_id}: {replay_problems[0]}",
        )
    try:
        windows = reader.phase_windows().get(phase)
    except (BundleReadError, OSError, TypeError, ValueError) as exc:
        _refuse("phase_window_non_unique", f"{bundle_id}/{phase}: {exc}")
    if not isinstance(windows, list) or len(windows) != 1:
        count = 0 if not isinstance(windows, list) else len(windows)
        _refuse(
            "phase_window_non_unique",
            f"{bundle_id}/{phase}: expected one phase window, found {count}",
        )
    window = windows[0]
    if (
        not _finite_number(window.start_s)
        or not _finite_number(window.end_s)
        or not _finite_number(window.duration_s)
        or window.duration_s <= 0.0
    ):
        _refuse(
            "phase_window_non_unique",
            f"{bundle_id}/{phase}: phase window is nonfinite or nonpositive",
        )
    try:
        curve = reader.summed_curve()
    except (BundleReadError, OSError, TypeError, ValueError) as exc:
        _refuse("raw_to_trace_replay_failed", f"{bundle_id}: {exc}")
    if not curve or any(
        point.support_start_s is None
        or point.support_end_s is None
        or not _finite_number(point.support_start_s)
        or not _finite_number(point.support_end_s)
        for point in curve
    ):
        _refuse(
            "raw_to_trace_replay_failed",
            f"{bundle_id}: replayed power trace lacks interval support",
        )
    count = _in_window_sample_count(curve, window)
    gap_stats = _window_gap_stats(curve, window)
    cadence = gap_stats.get("cadence_ratio")
    if type(count) is not int or count < 0 or not _finite_number(cadence):
        _refuse(
            "unrecordable_minimum",
            f"{bundle_id}/{phase}: cadence/count minimum is not derivable",
        )
    values = (
        float(window.start_s),
        float(window.end_s),
        float(window.duration_s),
        float(cadence),
        float(SHORT_WINDOW_CADENCE_RATIO_MIN),
    )
    if not all(math.isfinite(value) for value in values):
        _refuse("nonfinite_arithmetic", f"{bundle_id}/{phase}: nonfinite derivation")
    return _MemberObservation(
        bundle_id=bundle_id,
        expected_config_sha256=expected_config_sha256,
        phase=phase,
        start_s=values[0],
        end_s=values[1],
        duration_s=values[2],
        overlapping_power_interval_count=count,
        cadence_ratio=values[3],
        cadence_ratio_threshold=values[4],
    )


def _discover_evaluation_basis(
    runs_root: Path,
    referenced_bundle_ids: set[str],
) -> str:
    try:
        lines = read_authentication_text(
            runs_root / "campaign_log.jsonl",
            grammar="jsonl",
            label="window-duration-margin campaign log",
            encoding="utf-8",
        ).splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        _refuse("authenticated_b_operative_unavailable", f"campaign log: {exc}")
    candidates: set[str] = set()
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            _refuse("authenticated_b_operative_unavailable", f"campaign log: {exc}")
        if not isinstance(row, Mapping) or row.get("record_type") != (
            "idle_admission_whole_window_verdict"
        ):
            continue
        basis = row.get("evaluation_basis")
        if not isinstance(basis, Mapping):
            continue
        semantics = basis.get("consumption_semantics_id", row.get("consumption_semantics_id"))
        occurrences = basis.get("member_occurrences")
        occurrence_ids = (
            {
                occurrence.get("bundle_id")
                for occurrence in occurrences
                if isinstance(occurrence, Mapping)
                and isinstance(occurrence.get("bundle_id"), str)
            }
            if isinstance(occurrences, list)
            else set()
        )
        sha = basis.get("sha256")
        if (
            semantics == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            and referenced_bundle_ids.issubset(occurrence_ids)
            and isinstance(sha, str)
            and _SHA256_RE.fullmatch(sha) is not None
        ):
            candidates.add(sha)
    if len(candidates) != 1:
        _refuse(
            "authenticated_b_operative_unavailable",
            "exactly one max-bracket evaluation basis must cover every registered member",
        )
    return next(iter(candidates))


def _authenticate_b_operative(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    evaluation_basis_sha256: str,
) -> AuthenticatedConsumptionSession:
    try:
        session = AuthenticatedConsumptionSession(
            runs_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )
        reasons = whole_window_refusal_reasons(
            runs_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_session=session,
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )
    except (OSError, TypeError, ValueError) as exc:
        _refuse("authenticated_b_operative_unavailable", str(exc))
    if reasons or not session.ready:
        combined = tuple(reasons) or tuple(session.refusal_reasons)
        _refuse(
            "authenticated_b_operative_unavailable",
            ", ".join(combined) if combined else "authenticated session is not ready",
        )
    bound = session.operative_fiducial_bound_s
    if not _finite_number(bound) or float(bound) < 0.0:
        _refuse(
            "authenticated_b_operative_unavailable",
            "AuthenticatedConsumptionSession did not derive a finite nonnegative bound",
        )
    return session


def _numbers_equal(left: Any, right: float) -> bool:
    return _finite_number(left) and math.isclose(
        float(left), right, rel_tol=0.0, abs_tol=1e-12
    )


def _cross_check_summary(
    session: AuthenticatedConsumptionSession,
    observation: _MemberObservation,
) -> None:
    summary = session.summary_for(observation.bundle_id)
    precheck = (
        summary.get("window_evidence_precheck")
        if isinstance(summary, Mapping)
        else None
    )
    phases = precheck.get("phase") if isinstance(precheck, Mapping) else None
    phase = phases.get(observation.phase) if isinstance(phases, Mapping) else None
    windows = phase.get("windows") if isinstance(phase, Mapping) else None
    if (
        not isinstance(phase, Mapping)
        or phase.get("window_count") != 1
        or not isinstance(windows, list)
        or len(windows) != 1
        or not isinstance(windows[0], Mapping)
    ):
        _refuse(
            "summary_precheck_mismatch",
            f"{observation.bundle_id}/{observation.phase}: one cross-check window is required",
        )
    check = windows[0]
    comparisons = (
        ("window_duration_s", observation.duration_s),
        (
            "in_window_sample_count",
            float(observation.overlapping_power_interval_count),
        ),
        ("cadence_ratio", observation.cadence_ratio),
        ("cadence_ratio_min", observation.cadence_ratio_threshold),
    )
    for field, derived in comparisons:
        if not _numbers_equal(check.get(field), derived):
            _refuse(
                "summary_precheck_mismatch",
                f"{observation.bundle_id}/{observation.phase}: {field} disagrees with authenticated replay",
            )


def _member_row(observation: _MemberObservation) -> dict[str, Any]:
    return {
        "bundle_id": observation.bundle_id,
        "expected_config_sha256": observation.expected_config_sha256,
        "phase_window_start_s": observation.start_s,
        "phase_window_end_s": observation.end_s,
        "phase_window_duration_s": observation.duration_s,
        "overlapping_power_interval_count": (
            observation.overlapping_power_interval_count
        ),
        "sample_count_margin": (
            observation.overlapping_power_interval_count - MIN_PHASE_SAMPLES
        ),
        "reducer_cadence_ratio": observation.cadence_ratio,
        "reducer_cadence_ratio_threshold": observation.cadence_ratio_threshold,
    }


def _cell_row(
    cell: _RegisteredCell,
    observations: Sequence[_MemberObservation],
    b_operative_s: float,
) -> dict[str, Any]:
    members = sorted(
        (_member_row(observation) for observation in observations),
        key=lambda row: row["bundle_id"],
    )
    double_bound = 2.0 * b_operative_s
    if not math.isfinite(double_bound) or double_bound <= 0.0:
        _refuse(
            "nonfinite_arithmetic" if not math.isfinite(double_bound) else "unrecordable_minimum",
            f"{cell.cell_id}: 2*B_operative cannot support a finite ratio",
        )
    durations = [float(row["phase_window_duration_s"]) for row in members]
    margins = [duration - double_bound for duration in durations]
    ratios = [duration / double_bound for duration in durations]
    if not all(math.isfinite(value) for value in (*margins, *ratios)):
        _refuse("nonfinite_arithmetic", f"{cell.cell_id}: nonfinite margin arithmetic")
    minimum_duration, attaining_id = min(
        (float(row["phase_window_duration_s"]), str(row["bundle_id"]))
        for row in members
    )
    member_ids = [str(row["bundle_id"]) for row in members]
    row = {
        "cell_id": cell.cell_id,
        "metric": cell.metric,
        "membership_sha256": _canonical_sha256(member_ids),
        "member_count": len(members),
        "b_operative_s": b_operative_s,
        "min_phase_window_duration_s": minimum_duration,
        "min_phase_window_duration_bundle_id": attaining_id,
        "min_duration_minus_2b_operative_s": min(margins),
        "min_duration_to_2b_operative_ratio": min(ratios),
        "min_overlapping_power_interval_count": min(
            int(member["overlapping_power_interval_count"]) for member in members
        ),
        "min_sample_count_margin": min(
            int(member["sample_count_margin"]) for member in members
        ),
        "min_reducer_cadence_ratio": min(
            float(member["reducer_cadence_ratio"]) for member in members
        ),
        "reducer_cadence_ratio_threshold": float(
            SHORT_WINDOW_CADENCE_RATIO_MIN
        ),
        "members": members,
    }
    if any(
        not math.isfinite(float(row[field]))
        for field in (
            "b_operative_s",
            "min_phase_window_duration_s",
            "min_duration_minus_2b_operative_s",
            "min_duration_to_2b_operative_ratio",
            "min_reducer_cadence_ratio",
            "reducer_cadence_ratio_threshold",
        )
    ):
        _refuse("nonfinite_arithmetic", f"{cell.cell_id}: nonfinite cell minimum")
    return row


def _source_name(
    identity: str,
    *,
    repository_root: Path,
    pack_root: Path,
    runs_root: Path,
) -> str:
    if identity.startswith("git:"):
        return identity
    path = Path(identity)
    for label, root in (
        ("pack", pack_root),
        ("runs", runs_root),
        ("repository", repository_root),
    ):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        return f"{label}:{relative.as_posix()}"
    return f"external:{identity}"


def _authoritative_inputs(
    authentication: V2AuthenticationReadSession,
    *,
    repository_root: Path,
    pack_root: Path,
    runs_root: Path,
) -> list[dict[str, str]]:
    rows = [
        {
            "source": _source_name(
                identity,
                repository_root=repository_root,
                pack_root=pack_root,
                runs_root=runs_root,
            ),
            "sha256": record.sha256,
        }
        for identity, record in authentication.records.items()
    ]
    rows.sort(key=lambda row: row["source"])
    if len({row["source"] for row in rows}) != len(rows):
        _refuse("authoritative_input_invalid", "authoritative source labels collide")
    return rows


def derive_window_duration_margins(
    *,
    repository_root: Path,
    pack_root: Path,
    runs_root: Path,
    pack_identity: str,
) -> dict[str, Any]:
    """Derive a PASS receipt or raise a closed refusal without writing."""

    repository_root = Path(repository_root).resolve()
    pack_root = Path(pack_root).resolve()
    runs_root = Path(runs_root).resolve()
    for label, root in (
        ("repository root", repository_root),
        ("pack root", pack_root),
        ("runs root", runs_root),
    ):
        if not root.is_dir():
            _refuse("authoritative_input_invalid", f"{label} is not a directory")
    try:
        with V2AuthenticationReadSession() as authentication:
            tree_sha, registry_sha, cells = _pack_inventory(
                repository_root, pack_root, pack_identity
            )
            member_paths = _resolve_member_paths(runs_root, cells)
            observations: dict[tuple[str, str], _MemberObservation] = {}
            expected_by_id: dict[str, str] = {}
            for cell in cells:
                phase = _phase_for_metric(cell.metric, cell_id=cell.cell_id)
                for bundle_id, expected_config_sha in cell.members:
                    previous = expected_by_id.setdefault(bundle_id, expected_config_sha)
                    if previous != expected_config_sha:
                        _refuse(
                            "registered_membership_invalid",
                            f"{bundle_id}: pack registries disagree on config sha256",
                        )
                    key = (bundle_id, phase)
                    if key not in observations:
                        observations[key] = _observe_member(
                            bundle_id,
                            expected_config_sha,
                            phase,
                            member_paths[bundle_id],
                        )
            referenced = set(member_paths)
            basis_sha = _discover_evaluation_basis(runs_root, referenced)
            consumption = _authenticate_b_operative(
                runs_root, referenced, basis_sha
            )
            b_operative = float(consumption.operative_fiducial_bound_s)
            for observation in observations.values():
                _cross_check_summary(consumption, observation)
            cell_rows = [
                _cell_row(
                    cell,
                    [
                        observations[(bundle_id, _phase_for_metric(cell.metric, cell_id=cell.cell_id))]
                        for bundle_id, _sha in cell.members
                    ],
                    b_operative,
                )
                for cell in cells
            ]
            inventory = [
                {
                    "cell_id": row["cell_id"],
                    "metric": row["metric"],
                    "membership_sha256": row["membership_sha256"],
                    "member_count": row["member_count"],
                }
                for row in cell_rows
            ]
            receipt = {
                "schema_version": RECEIPT_SCHEMA_VERSION,
                "status": "PASS",
                "pack_identity": pack_identity,
                "pack_tree_sha256": tree_sha,
                "registry_source_sha256": registry_sha,
                "evaluation_basis_sha256": basis_sha,
                "cell_inventory_sha256": _canonical_sha256(inventory),
                "cells": cell_rows,
                "authoritative_inputs": _authoritative_inputs(
                    authentication,
                    repository_root=repository_root,
                    pack_root=pack_root,
                    runs_root=runs_root,
                ),
            }
            validate_window_duration_margins_receipt(receipt)
            return receipt
    except WindowDurationMarginsRefusal:
        raise
    except V2AuthenticationInputError as exc:
        _refuse("authoritative_input_invalid", f"{exc.reason}: {exc.detail}")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _refuse("authoritative_input_invalid", str(exc))


def _require_exact_keys(value: Any, keys: frozenset[str], *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(keys):
        observed = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        raise ValueError(f"{label} keys are {observed}, expected {sorted(keys)}")
    return value


def _schema_number(value: Any, *, label: str) -> float:
    if not _finite_number(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def validate_window_duration_margins_receipt(receipt: Mapping[str, Any]) -> None:
    """Validate the closed receipt schema and every recomputable minimum."""

    root = _require_exact_keys(receipt, RECEIPT_KEYS, label="receipt")
    if root.get("schema_version") != RECEIPT_SCHEMA_VERSION or root.get("status") != "PASS":
        raise ValueError("receipt schema/status is invalid")
    if not isinstance(root.get("pack_identity"), str) or _PACK_ID_RE.fullmatch(
        root["pack_identity"]
    ) is None:
        raise ValueError("receipt pack_identity is invalid")
    for field in (
        "pack_tree_sha256",
        "registry_source_sha256",
        "evaluation_basis_sha256",
        "cell_inventory_sha256",
    ):
        if not isinstance(root.get(field), str) or _SHA256_RE.fullmatch(root[field]) is None:
            raise ValueError(f"receipt {field} is invalid")
    raw_cells = root.get("cells")
    if not isinstance(raw_cells, list) or not raw_cells:
        raise ValueError("receipt cells must be a nonempty array")
    cell_ids: list[str] = []
    inventory: list[dict[str, Any]] = []
    for cell_index, raw_cell in enumerate(raw_cells):
        cell = _require_exact_keys(raw_cell, CELL_KEYS, label=f"cells[{cell_index}]")
        cell_id = cell.get("cell_id")
        metric = cell.get("metric")
        members = cell.get("members")
        if (
            not isinstance(cell_id, str)
            or not cell_id
            or not isinstance(metric, str)
            or not metric.startswith("phase_energy_j.")
            or not isinstance(members, list)
            or not members
        ):
            raise ValueError(f"cells[{cell_index}] identity/members are invalid")
        cell_ids.append(cell_id)
        parsed_members: list[Mapping[str, Any]] = []
        for member_index, raw_member in enumerate(members):
            member = _require_exact_keys(
                raw_member,
                MEMBER_KEYS,
                label=f"cells[{cell_index}].members[{member_index}]",
            )
            bundle_id = member.get("bundle_id")
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or not isinstance(member.get("expected_config_sha256"), str)
                or _SHA256_RE.fullmatch(member["expected_config_sha256"]) is None
            ):
                raise ValueError("receipt member identity/config pin is invalid")
            start = _schema_number(member.get("phase_window_start_s"), label="phase start")
            end = _schema_number(member.get("phase_window_end_s"), label="phase end")
            duration = _schema_number(member.get("phase_window_duration_s"), label="duration")
            if duration <= 0.0 or not math.isclose(end - start, duration, rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("receipt member phase duration is inconsistent")
            count = member.get("overlapping_power_interval_count")
            margin = member.get("sample_count_margin")
            if type(count) is not int or count < 0 or type(margin) is not int or margin != count - MIN_PHASE_SAMPLES:
                raise ValueError("receipt member sample-count margin is inconsistent")
            _schema_number(member.get("reducer_cadence_ratio"), label="cadence ratio")
            threshold = _schema_number(
                member.get("reducer_cadence_ratio_threshold"), label="cadence threshold"
            )
            if threshold != SHORT_WINDOW_CADENCE_RATIO_MIN:
                raise ValueError("receipt cadence threshold is not reducer-derived")
            parsed_members.append(member)
        bundle_ids = [str(member["bundle_id"]) for member in parsed_members]
        if bundle_ids != sorted(bundle_ids) or len(set(bundle_ids)) != len(bundle_ids):
            raise ValueError("receipt members are not unique and sorted")
        if cell.get("member_count") != len(parsed_members):
            raise ValueError("receipt member_count is inconsistent")
        if cell.get("membership_sha256") != _canonical_sha256(bundle_ids):
            raise ValueError("receipt membership_sha256 is inconsistent")
        b_operative = _schema_number(cell.get("b_operative_s"), label="B_operative")
        double_bound = 2.0 * b_operative
        if not math.isfinite(double_bound) or double_bound <= 0.0:
            raise ValueError("receipt 2*B_operative cannot support the ratio")
        duration_pairs = [
            (float(member["phase_window_duration_s"]), str(member["bundle_id"]))
            for member in parsed_members
        ]
        duration, attaining = min(duration_pairs)
        expected_numeric = {
            "min_phase_window_duration_s": duration,
            "min_duration_minus_2b_operative_s": min(
                item[0] - double_bound for item in duration_pairs
            ),
            "min_duration_to_2b_operative_ratio": min(
                item[0] / double_bound for item in duration_pairs
            ),
            "min_reducer_cadence_ratio": min(
                float(member["reducer_cadence_ratio"])
                for member in parsed_members
            ),
            "reducer_cadence_ratio_threshold": SHORT_WINDOW_CADENCE_RATIO_MIN,
        }
        for field, expected in expected_numeric.items():
            if _schema_number(cell.get(field), label=field) != expected:
                raise ValueError(f"receipt {field} is inconsistent")
        if cell.get("min_phase_window_duration_bundle_id") != attaining:
            raise ValueError("receipt minimum-duration attaining bundle is inconsistent")
        expected_count = min(
            int(member["overlapping_power_interval_count"])
            for member in parsed_members
        )
        if cell.get("min_overlapping_power_interval_count") != expected_count:
            raise ValueError("receipt minimum overlapping interval count is inconsistent")
        if cell.get("min_sample_count_margin") != expected_count - MIN_PHASE_SAMPLES:
            raise ValueError("receipt minimum sample-count margin is inconsistent")
        inventory.append(
            {
                "cell_id": cell_id,
                "metric": metric,
                "membership_sha256": cell["membership_sha256"],
                "member_count": cell["member_count"],
            }
        )
    if cell_ids != sorted(cell_ids) or len(set(cell_ids)) != len(cell_ids):
        raise ValueError("receipt cells are not unique and sorted")
    if root.get("cell_inventory_sha256") != _canonical_sha256(inventory):
        raise ValueError("receipt cell_inventory_sha256 is inconsistent")
    inputs = root.get("authoritative_inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("receipt authoritative_inputs must be nonempty")
    sources: list[str] = []
    for index, raw_input in enumerate(inputs):
        item = _require_exact_keys(raw_input, INPUT_KEYS, label=f"authoritative_inputs[{index}]")
        source = item.get("source")
        digest = item.get("sha256")
        if (
            not isinstance(source, str)
            or not source
            or not isinstance(digest, str)
            or _SHA256_RE.fullmatch(digest) is None
        ):
            raise ValueError("receipt authoritative input is invalid")
        sources.append(source)
    if sources != sorted(sources) or len(set(sources)) != len(sources):
        raise ValueError("receipt authoritative inputs are not unique and sorted")


def deterministic_window_duration_margins_path(
    receipt_root: Path,
    *,
    pack_identity: str,
    evaluation_basis_sha256: str,
) -> Path:
    """Return the governed append-only path; no operator path is accepted."""

    if _PACK_ID_RE.fullmatch(pack_identity) is None:
        _refuse("pack_identity_invalid", "pack identity is not namespace-safe")
    if _SHA256_RE.fullmatch(evaluation_basis_sha256) is None:
        _refuse("authoritative_input_invalid", "evaluation basis sha256 is invalid")
    return (
        Path(receipt_root)
        / RECEIPT_NAMESPACE
        / pack_identity
        / f"{evaluation_basis_sha256}.json"
    )


def _exclusive_idempotent_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        try:
            existing = path.read_bytes()
        except OSError as exc:
            _refuse("receipt_namespace_conflict", f"existing receipt is unreadable: {exc}")
        if existing != payload:
            _refuse(
                "receipt_namespace_conflict",
                "deterministic receipt path contains different bytes",
            )
        return
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def record_window_duration_margins(
    *,
    repository_root: Path,
    pack_root: Path,
    runs_root: Path,
    receipt_root: Path,
    pack_identity: str,
) -> RecordedWindowDurationMargins:
    """Derive then append one receipt at its deterministic namespace path."""

    receipt = derive_window_duration_margins(
        repository_root=repository_root,
        pack_root=pack_root,
        runs_root=runs_root,
        pack_identity=pack_identity,
    )
    payload = _receipt_bytes(receipt)
    path = deterministic_window_duration_margins_path(
        receipt_root,
        pack_identity=pack_identity,
        evaluation_basis_sha256=receipt["evaluation_basis_sha256"],
    )
    _exclusive_idempotent_write(path, payload)
    return RecordedWindowDurationMargins(
        path=path,
        sha256=_sha256(payload),
        receipt=receipt,
    )


__all__ = [
    "CELL_KEYS",
    "INPUT_KEYS",
    "MEMBER_KEYS",
    "RECEIPT_KEYS",
    "RECEIPT_NAMESPACE",
    "RECEIPT_SCHEMA_VERSION",
    "RecordedWindowDurationMargins",
    "WindowDurationMarginsRefusal",
    "derive_window_duration_margins",
    "deterministic_window_duration_margins_path",
    "record_window_duration_margins",
    "render_window_duration_margins_receipt",
    "validate_window_duration_margins_receipt",
]
