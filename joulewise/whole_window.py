"""Hash-bound, coverage-complete whole-window idle-admission verdict join.

The verdict is a claim barrier, not an append-log preference.  A consumer must
prove that one internally consistent row covers every bundle it is about to
use.  Conflicting append-only rows are therefore an ambiguity/refusal; file
order never grants a later row authority to erase an earlier failure.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from joulewise.idle_admission import (
    ADAPTER_CONTINUITY_SCHEMA,
    NEG8_BRACKET_SCHEMA,
)
from joulewise.bundle import sanitize_id_component

WHOLE_WINDOW_SCHEMA = "joulewise.idle_admission_whole_window_verdict.v1"
IDLE_ADMISSION_CORE_SCHEMA = "joulewise.idle_admission_core_verdict.v1"
WHOLE_WINDOW_PROVENANCE_SCHEMA = (
    "joulewise.idle_admission_whole_window_provenance.v1"
)


def validate_attempt_ledger(*args: Any, **kwargs: Any) -> Any:
    """Lazily delegate to the single authoritative registry validator."""

    # ``analysis_engine.inputs`` consumes whole-window results, so importing
    # the package-level registry while this module initializes creates a cycle.
    from joulewise.analysis_engine.registry import validate_attempt_ledger as shared

    return shared(*args, **kwargs)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def source_manifest_descriptors(
    runs_root: Path, manifest_paths: Sequence[str | Path]
) -> list[dict[str, str]]:
    """Bind every source campaign manifest by safe runs-root-relative path."""

    root = Path(runs_root).resolve()
    result: list[dict[str, str]] = []
    for value in manifest_paths:
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        resolved = path.resolve()
        if resolved == root or root not in resolved.parents:
            raise ValueError(f"whole-window source manifest escapes runs root: {value}")
        raw = resolved.read_bytes()
        result.append(
            {
                "path": resolved.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return sorted(result, key=lambda row: row["path"])


def build_row_provenance(
    *,
    policy_sha256: str,
    bundle_ids: Sequence[str],
    source_manifests: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    members = sorted(bundle_ids)
    return {
        "schema_version": WHOLE_WINDOW_PROVENANCE_SCHEMA,
        "policy_sha256": policy_sha256,
        "membership_sha256": canonical_sha256(members),
        "source_campaign_manifests": [dict(row) for row in source_manifests],
    }


def _safe_source_path(root: Path, text: Any) -> Path | None:
    if not isinstance(text, str) or not text:
        return None
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    try:
        path = (root / Path(*pure.parts)).resolve()
        resolved_root = root.resolve()
    except (OSError, RuntimeError):
        return None
    if path == resolved_root or resolved_root not in path.parents:
        return None
    return path


def _evidence_map(path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    if not path.is_dir():
        return result
    for candidate in sorted(path.glob("*.json")):
        raw = candidate.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest in result:
            raise ValueError("duplicate attempt evidence digest")
        result[digest] = raw
    return result


def validated_attempt_selection(
    selection: Mapping[str, Any], runs_root: Path
) -> set[str] | None:
    """Re-run the authoritative attempt-ledger validator at consumption."""

    ledger = _safe_source_path(runs_root, selection.get("attempt_ledger_path"))
    manifest_path = _safe_source_path(
        runs_root, selection.get("analysis_manifest_path")
    )
    if ledger is None or manifest_path is None:
        return None
    try:
        ledger_raw = ledger.read_bytes()
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        rows = [
            json.loads(line)
            for line in ledger_raw.decode("utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if (
        hashlib.sha256(ledger_raw).hexdigest()
        != selection.get("attempt_ledger_sha256")
        or hashlib.sha256(manifest_raw).hexdigest()
        != selection.get("analysis_manifest_sha256")
        or not isinstance(manifest, Mapping)
        or not rows
        or any(not isinstance(row, Mapping) for row in rows)
    ):
        return None
    evidence_root = ledger.parent
    try:
        receipts = _evidence_map(evidence_root / "dispatch_receipts")
        strict_evidence = _evidence_map(evidence_root / "strict_validation")
        finalized: dict[tuple[str, int, str], Path] = {}
        for row in rows:
            run_id = row.get("run_id")
            entry_id = row.get("entry_id")
            ordinal = row.get("attempt_ordinal")
            if not isinstance(run_id, str):
                continue
            if (
                not isinstance(entry_id, str)
                or isinstance(ordinal, bool)
                or not isinstance(ordinal, int)
            ):
                return None
            path = (
                runs_root
                / "axi_attempt_bundles"
                / str(manifest.get("manifest_id"))
                / sanitize_id_component(entry_id)
                / f"a{ordinal}"
                / sanitize_id_component(run_id)
            )
            finalized[(entry_id, ordinal, run_id)] = path
        selected = validate_attempt_ledger(
            rows,
            manifest,
            receipts=receipts,
            strict_evidence=strict_evidence,
            finalized_bundles=finalized,
        )
    except (OSError, TypeError, ValueError):
        return None
    expected_descriptors = {
        (
            entry_id,
            row.get("attempt_ordinal"),
            row.get("run_id"),
            (
                f"{sanitize_id_component(entry_id)}__a{row.get('attempt_ordinal')}__"
                f"{sanitize_id_component(str(row.get('run_id')))}"
            ),
            (
                Path("axi_attempt_bundles")
                / str(manifest.get("manifest_id"))
                / sanitize_id_component(entry_id)
                / f"a{row.get('attempt_ordinal')}"
                / sanitize_id_component(str(row.get("run_id")))
            ).as_posix(),
        )
        for entry_id, row in selected.items()
        if row is not None
    }
    descriptors = selection.get("selected_bundles")
    if not isinstance(descriptors, list):
        return None
    actual: set[tuple[Any, Any, Any, Any, Any]] = set()
    selected_ids: set[str] = set()
    selected_paths: set[str] = set()
    for descriptor in descriptors:
        if not isinstance(descriptor, Mapping):
            return None
        identity = (
            descriptor.get("entry_id"),
            descriptor.get("attempt_ordinal"),
            descriptor.get("run_id"),
            descriptor.get("bundle_id"),
            descriptor.get("path"),
        )
        bundle_id = descriptor.get("bundle_id")
        path_text = descriptor.get("path")
        if (
            identity in actual
            or not isinstance(bundle_id, str)
            or bundle_id in selected_ids
            or not isinstance(path_text, str)
            or path_text in selected_paths
        ):
            return None
        actual.add(identity)
        selected_ids.add(bundle_id)
        selected_paths.add(path_text)
    if actual != expected_descriptors:
        return None
    quarantined = selection.get("quarantined_attempts")
    if not isinstance(quarantined, list):
        return None
    expected_quarantined = {
        (row.get("entry_id"), row.get("attempt_ordinal"), row.get("run_id"))
        for row in rows
        if row.get("eligible_for_analysis") is False
    }
    actual_quarantined: set[tuple[Any, Any, Any]] = set()
    for row in quarantined:
        if (
            not isinstance(row, Mapping)
            or row.get("properly_quarantined") is not True
            or row.get("recovery_continuity_verified") is not True
        ):
            return None
        identity = (
            row.get("entry_id"),
            row.get("attempt_ordinal"),
            row.get("run_id"),
        )
        if identity in actual_quarantined:
            return None
        actual_quarantined.add(identity)
    if actual_quarantined != expected_quarantined or {
        identity[:3] for identity in actual
    } & actual_quarantined:
        return None
    return selected_ids


def _manifest_members(
    value: Mapping[str, Any], runs_root: Path
) -> set[str] | None:
    selection = value.get("attempt_ledger_selection")
    if isinstance(selection, Mapping):
        validated_selected = validated_attempt_selection(selection, runs_root)
        if validated_selected is None:
            return None
        selected = selection.get("selected_bundle_ids")
        if not isinstance(selected, list) or any(
            not isinstance(item, str) or not item for item in selected
        ):
            return None
        if canonical_sha256(sorted(selected)) != selection.get(
            "selected_membership_sha256"
        ):
            return None
        if selection.get("schema_version") != "joulewise.attempt_ledger_selection.v1":
            return None
        ledger = _safe_source_path(runs_root, selection.get("attempt_ledger_path"))
        ledger_sha = selection.get("attempt_ledger_sha256")
        try:
            ledger_raw = ledger.read_bytes() if ledger is not None else None
        except OSError:
            return None
        if (
            ledger_raw is None
            or not isinstance(ledger_sha, str)
            or hashlib.sha256(ledger_raw).hexdigest() != ledger_sha
        ):
            return None
        descriptors = selection.get("selected_bundles")
        if not isinstance(descriptors, list) or len(descriptors) != len(selected):
            return None
        descriptor_ids: set[str] = set()
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                return None
            bundle_id = descriptor.get("bundle_id")
            bundle_path = _safe_source_path(runs_root, descriptor.get("path"))
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or bundle_id in descriptor_ids
                or bundle_path is None
                or not bundle_path.is_dir()
            ):
                return None
            descriptor_ids.add(bundle_id)
        quarantined = selection.get("quarantined_attempts")
        if isinstance(quarantined, list) and any(
            not isinstance(row, Mapping)
            or row.get("properly_quarantined") is not True
            or row.get("recovery_continuity_verified") is not True
            for row in quarantined
        ):
            return None
        if descriptor_ids != set(selected) or descriptor_ids != validated_selected:
            return None
        return set(selected)
    members = value.get("members")
    if not isinstance(members, list):
        return None
    result: set[str] = set()
    for row in members:
        if not isinstance(row, Mapping) or row.get("execution") != "invoked":
            continue
        bundle_ids = row.get("bundle_ids")
        if not isinstance(bundle_ids, list):
            return None
        if any(not isinstance(item, str) or not item for item in bundle_ids):
            return None
        result.update(bundle_ids)
    return result


def _validate_row(
    row: Mapping[str, Any], runs_root: Path, referenced: set[str]
) -> tuple[bool, tuple[str, ...]]:
    reasons: set[str] = set()
    if row.get("schema_version") != WHOLE_WINDOW_SCHEMA:
        reasons.add("whole_window_verdict_provenance_invalid")
    bundle_ids = row.get("bundle_ids")
    if (
        not isinstance(bundle_ids, list)
        or any(not isinstance(item, str) or not item for item in bundle_ids)
        or len(set(bundle_ids)) != len(bundle_ids)
        or not referenced.issubset(set(bundle_ids))
    ):
        reasons.add("whole_window_verdict_coverage_incomplete")
        return False, tuple(sorted(reasons))

    policy = row.get("campaign_policy")
    policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
    provenance = row.get("row_provenance")
    if (
        not isinstance(policy_sha, str)
        or len(policy_sha) != 64
        or not isinstance(provenance, Mapping)
        or provenance.get("schema_version") != WHOLE_WINDOW_PROVENANCE_SCHEMA
        or provenance.get("policy_sha256") != policy_sha
        or provenance.get("membership_sha256")
        != canonical_sha256(sorted(bundle_ids))
    ):
        reasons.add("whole_window_verdict_provenance_invalid")

    core = row.get("idle_admission_core")
    if not isinstance(core, Mapping) or core.get("schema_version") != IDLE_ADMISSION_CORE_SCHEMA:
        reasons.add("whole_window_verdict_provenance_invalid")
    elif core.get("policy_sha256") != policy_sha:
        reasons.add("whole_window_verdict_provenance_invalid")

    descriptors = (
        provenance.get("source_campaign_manifests")
        if isinstance(provenance, Mapping)
        else None
    )
    covered_by_sources: set[str] = set()
    if not isinstance(descriptors, list) or not descriptors:
        reasons.add("whole_window_verdict_provenance_invalid")
    else:
        seen_paths: set[str] = set()
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            text = descriptor.get("path")
            expected_sha = descriptor.get("sha256")
            path = _safe_source_path(runs_root, text)
            if (
                path is None
                or not isinstance(text, str)
                or text in seen_paths
                or not isinstance(expected_sha, str)
                or len(expected_sha) != 64
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            seen_paths.add(text)
            try:
                raw = path.read_bytes()
                manifest = json.loads(raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            if hashlib.sha256(raw).hexdigest() != expected_sha or not isinstance(
                manifest, Mapping
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            manifest_policy = manifest.get("campaign_policy")
            if (
                manifest.get("schema_version")
                != "joulewise.campaign_provenance.v1"
                or not isinstance(manifest_policy, Mapping)
                or manifest_policy.get("sha256") != policy_sha
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            members = _manifest_members(manifest, runs_root)
            if members is None:
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            covered_by_sources.update(members)
    if not set(bundle_ids).issubset(covered_by_sources):
        reasons.add("whole_window_verdict_provenance_invalid")

    if isinstance(core, Mapping):
        bracket = core.get("neg8_bracket")
        continuity = core.get("adapter_wattage_continuity")
        members = core.get("members")
        if not isinstance(bracket, Mapping) or bracket.get("schema_version") != NEG8_BRACKET_SCHEMA:
            reasons.add("whole_window_neg8_verdict_missing")
        elif row.get("status") != "passed" or bracket.get("decision") != "passed":
            reasons.add("whole_window_neg8_verdict_failed")
        if not isinstance(continuity, Mapping) or continuity.get("schema_version") != ADAPTER_CONTINUITY_SCHEMA:
            reasons.add("adapter_continuity_evidence_missing")
        elif continuity.get("decision") != "stable":
            reasons.add("adapter_continuity_failed")
        if not isinstance(members, list) or not members:
            reasons.add("cpu_admission_core_missing")
        else:
            member_ids = {
                member.get("bundle_id")
                for member in members
                if isinstance(member, Mapping)
                and isinstance(member.get("bundle_id"), str)
            }
            if not referenced.issubset(member_ids):
                reasons.add("whole_window_verdict_coverage_incomplete")
            if any(
                not isinstance(member, Mapping)
                or not isinstance(member.get("cpu_admission"), Mapping)
                or member["cpu_admission"].get("decision") != "admitted"
                for member in members
            ):
                reasons.add("cpu_admission_core_failed")
    return not reasons, tuple(sorted(reasons))


def whole_window_refusal_reasons(
    runs_root: Path, referenced_bundle_ids: set[str]
) -> tuple[str, ...]:
    """Return stable refusal reasons for a coverage-complete verdict join."""

    missing = (
        "whole_window_neg8_verdict_missing",
        "adapter_continuity_evidence_missing",
        "cpu_admission_core_missing",
    )
    try:
        lines = (Path(runs_root) / "campaign_log.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    except (OSError, UnicodeDecodeError):
        return missing
    overlapping: list[Mapping[str, Any]] = []
    valid: list[Mapping[str, Any]] = []
    invalid_reasons: set[str] = set()
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, Mapping) or row.get("record_type") != (
            "idle_admission_whole_window_verdict"
        ):
            continue
        bundle_ids = row.get("bundle_ids")
        ids = {
            item for item in bundle_ids or [] if isinstance(item, str)
        } if isinstance(bundle_ids, list) else set()
        if not ids.intersection(referenced_bundle_ids):
            continue
        overlapping.append(row)
        ok, reasons = _validate_row(row, Path(runs_root), referenced_bundle_ids)
        if ok:
            valid.append(row)
        else:
            invalid_reasons.update(reasons)
    if not overlapping:
        return missing
    if not valid:
        return tuple(sorted(invalid_reasons or set(missing)))
    # Any overlapping malformed/incomplete row or any semantically different
    # valid row makes append-only history ambiguous.  No "latest wins" escape.
    if len(valid) != len(overlapping):
        return ("whole_window_verdict_conflict",)
    semantic = {
        canonical_sha256(
            {
                "status": row.get("status"),
                "bundle_ids": sorted(row.get("bundle_ids", [])),
                "campaign_policy": row.get("campaign_policy"),
                "idle_admission_core": row.get("idle_admission_core"),
                "row_provenance": row.get("row_provenance"),
            }
        )
        for row in valid
    }
    if len(semantic) != 1:
        return ("whole_window_verdict_conflict",)
    return ()


__all__ = [
    "WHOLE_WINDOW_PROVENANCE_SCHEMA",
    "WHOLE_WINDOW_SCHEMA",
    "build_row_provenance",
    "canonical_sha256",
    "source_manifest_descriptors",
    "whole_window_refusal_reasons",
]
