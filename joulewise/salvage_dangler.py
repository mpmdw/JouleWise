"""Mechanical D-100 authorization for one terminally absent campaign member.

This module deliberately does not read the campaign log.  Every fact that can
license the exceptional disposition is re-derived from immutable closure and
bundle bytes.  Callers may append a new verdict under the dedicated
consumption semantic; they may never rewrite the failed source attempts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import stat
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SALVAGE_CLOSURE_SCHEMA = "joulewise.salvage_closure.v1"
SALVAGE_EXCLUSION_SCHEMA = "joulewise.salvage_dangler_exclusion.v1"
MEMBERSHIP_BINDING_SCHEMA = "joulewise.whole_window_membership_binding.v1"
LAUNCHER_REFUSAL_SCHEMA = "joulewise.salvage_launcher_refusal.v1"
SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID = "salvage_dangler_exclusion_v1"
TEARDOWN_BOUND_S = 0.250
_SHA256_LENGTH = 64
_REQUIRED_BUNDLE_FILES = (
    "config.json",
    "metadata.json",
    "summary_metrics.json",
    "events.jsonl",
    "power_trace.csv",
)
_MEASURAND_FIELDS = frozenset(
    {
        "decode_latency_s",
        "energy_bound_terms_j",
        "energy_output_token_j",
        "energy_request_j",
        "energy_token_j",
        "energy_uncertainty_status",
        "energy_variance_terms_j2",
        "gross_energy_j",
        "idle_mean_uncertainty",
        "idle_subtracted_energy_j",
        "inter_token_throughput_tokens_s",
        "phase_energy_j",
        "suite_metrics",
        "throughput_tokens_s",
        "ttft_s",
        "uncertainty",
        "window_evidence_precheck",
    }
)
_ALLOWED_FAILED_SUMMARY_NONNULL = frozenset(
    {
        "status",
        "failure_message",
        "failure_reason",
        "idle_baseline",
        "measurement_quality",
        "summary_provenance",
    }
)


class SalvageAuthorizationError(ValueError):
    """The supplied evidence does not satisfy the closed D-100 license."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_text(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SalvageAuthorizationError(f"unreadable JSON evidence: {path}") from exc
    if not isinstance(value, dict):
        raise SalvageAuthorizationError(f"JSON evidence is not an object: {path}")
    return value


def _descriptor(path: Path, *, relative_to: Path | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    name = (
        path.relative_to(relative_to).as_posix()
        if relative_to is not None
        else str(path.resolve())
    )
    return {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}


def _enumerate_artifacts(bundle_path: Path) -> list[dict[str, Any]]:
    """Enumerate every regular file and reject aliasing or ambiguous custody."""

    supplied = Path(bundle_path)
    if supplied.is_symlink():
        raise SalvageAuthorizationError(f"attempt path is a symlink: {supplied}")
    root = supplied.resolve(strict=True)
    if not root.is_dir():
        raise SalvageAuthorizationError(f"attempt path is not a directory: {root}")
    seen_inodes: set[tuple[int, int]] = set()
    descriptors: list[dict[str, Any]] = []

    def walk_error(error: OSError) -> None:
        raise SalvageAuthorizationError(
            f"unreadable artifact directory: {error.filename}"
        ) from error

    for parent, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=walk_error
    ):
        parent_path = Path(parent)
        for name in sorted(directory_names):
            child = parent_path / name
            try:
                mode = child.lstat().st_mode
            except OSError as exc:
                raise SalvageAuthorizationError(
                    f"unreadable artifact directory: {child}"
                ) from exc
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise SalvageAuthorizationError(f"non-directory artifact node: {child}")
        for name in sorted(file_names):
            child = parent_path / name
            try:
                info = child.lstat()
            except OSError as exc:
                raise SalvageAuthorizationError(f"unreadable artifact: {child}") from exc
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise SalvageAuthorizationError(f"non-regular artifact: {child}")
            identity = (info.st_dev, info.st_ino)
            if identity in seen_inodes:
                raise SalvageAuthorizationError(f"duplicate artifact inode: {child}")
            seen_inodes.add(identity)
            try:
                descriptors.append(_descriptor(child, relative_to=root))
            except OSError as exc:
                raise SalvageAuthorizationError(f"unreadable artifact: {child}") from exc
    paths = [row["path"] for row in descriptors]
    if len(paths) != len(set(paths)):
        raise SalvageAuthorizationError("duplicate artifact paths")
    return sorted(descriptors, key=lambda row: row["path"])


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise SalvageAuthorizationError(f"unreadable JSONL evidence: {path}") from exc
    if not lines:
        raise SalvageAuthorizationError(f"empty JSONL evidence: {path}")
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise SalvageAuthorizationError(
                f"blank JSONL evidence row: {path}:{line_number}"
            )
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SalvageAuthorizationError(
                f"truncated JSONL evidence: {path}:{line_number}"
            ) from exc
        if not isinstance(value, dict):
            raise SalvageAuthorizationError(
                f"non-object JSONL evidence: {path}:{line_number}"
            )
        rows.append(value)
    return rows


def _finite_timestamp(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _telemetry_last_timestamp(bundle_path: Path) -> float:
    timestamps: list[float] = []
    power_path = bundle_path / "power_trace.csv"
    try:
        with power_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise SalvageAuthorizationError("power trace is unreadable or truncated") from exc
    required_columns = {
        "timestamp_s",
        "power_w",
        "source",
        "rail",
        "interval_start_s",
        "interval_end_s",
    }
    if not rows or not required_columns.issubset(rows[0]):
        raise SalvageAuthorizationError("power trace has no telemetry rows")
    for row in rows:
        if any(row.get(column) in (None, "") for column in required_columns):
            raise SalvageAuthorizationError("power trace row is truncated")
        try:
            timestamp = float(row["timestamp_s"])
            power_w = float(row["power_w"])
            interval_start = float(row["interval_start_s"])
            interval_end = float(row["interval_end_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SalvageAuthorizationError("power trace numeric evidence is malformed") from exc
        if not all(
            math.isfinite(value)
            for value in (timestamp, power_w, interval_start, interval_end)
        ) or interval_start > interval_end:
            raise SalvageAuthorizationError("power trace numeric evidence is invalid")
        timestamps.append(max(timestamp, interval_end))
    if timestamps != sorted(timestamps):
        raise SalvageAuthorizationError("power trace timestamps are unordered")
    rich_paths = sorted(bundle_path.glob("rich_telemetry*.jsonl"))
    if not rich_paths:
        raise SalvageAuthorizationError("rich telemetry evidence is missing")
    for rich_path in rich_paths:
        rich_timestamps: list[float] = []
        for row in _jsonl_rows(rich_path):
            timestamp = _finite_timestamp(row.get("timestamp_s"))
            if timestamp is None:
                raise SalvageAuthorizationError(
                    f"rich telemetry timestamp is malformed: {rich_path}"
                )
            rich_timestamps.append(timestamp)
        if rich_timestamps != sorted(rich_timestamps):
            raise SalvageAuthorizationError(
                f"rich telemetry timestamps are unordered: {rich_path}"
            )
        timestamps.extend(rich_timestamps)
    return max(timestamps)


def inspect_preworkload_abort(bundle_path: str | Path) -> dict[str, Any]:
    """Re-derive the D-100 b-ii admission-bounded abort from bundle bytes."""

    path = Path(bundle_path).resolve(strict=True)
    metadata = _read_json_object(path / "metadata.json")
    summary = _read_json_object(path / "summary_metrics.json")
    events = _jsonl_rows(path / "events.jsonl")

    event_timestamps = [_finite_timestamp(row.get("timestamp_s")) for row in events]
    if (
        any(timestamp is None for timestamp in event_timestamps)
        or event_timestamps != sorted(event_timestamps)
        or events[0].get("event_type") != "run_started"
        or events[-1].get("event_type") != "run_finalized"
        or sum(row.get("event_type") == "run_started" for row in events) != 1
        or sum(row.get("event_type") == "run_finalized" for row in events) != 1
    ):
        raise SalvageAuthorizationError("event stream is incomplete or unordered")

    started = [
        row.get("phase")
        for row in events
        if row.get("event_type") == "stage_started"
    ]
    if started != ["validate", "prepare", "idle_baseline"]:
        raise SalvageAuthorizationError(
            "stage_started prefix is not validate,prepare,idle_baseline only"
        )
    failures = [row for row in events if row.get("event_type") == "failure"]
    if len(failures) != 1 or failures[0].get("phase") != "idle_baseline":
        raise SalvageAuthorizationError("terminal failure is not idle_baseline")
    failure_timestamp = _finite_timestamp(failures[0].get("timestamp_s"))
    if failure_timestamp is None:
        raise SalvageAuthorizationError("idle-baseline failure timestamp is malformed")

    admission = metadata.get("environment_admission")
    attempts = admission.get("attempts") if isinstance(admission, Mapping) else None
    if (
        not isinstance(admission, Mapping)
        or admission.get("decision") != "abort"
        or admission.get("claim_reason") != "environment_admission_failed"
        or not isinstance(attempts, list)
        or not attempts
        or any(
            not isinstance(attempt, Mapping) or attempt.get("admitted") is not False
            for attempt in attempts
        )
        or [attempt.get("attempt") for attempt in attempts]
        != list(range(1, len(attempts) + 1))
    ):
        raise SalvageAuthorizationError("environment admission is not the ratified abort")

    if summary.get("status") != "failed":
        raise SalvageAuthorizationError("summary status is not failed")
    if any(summary.get(field) is not None for field in _MEASURAND_FIELDS):
        raise SalvageAuthorizationError("failed attempt contains measurand bytes")
    unknown_nonnull = {
        key
        for key, value in summary.items()
        if value is not None and key not in _ALLOWED_FAILED_SUMMARY_NONNULL
    }
    if unknown_nonnull:
        raise SalvageAuthorizationError(
            "unknown non-null failed-summary fields: "
            + ", ".join(sorted(unknown_nonnull))
        )
    failure_reason = summary.get("failure_reason")
    event_reason = failures[0].get("metadata")
    event_reason = (
        event_reason.get("failure_reason")
        if isinstance(event_reason, Mapping)
        else None
    )
    if not isinstance(failure_reason, str) or not failure_reason:
        raise SalvageAuthorizationError("summary failure reason is missing")
    if event_reason != failure_reason:
        raise SalvageAuthorizationError("event and summary failure reasons disagree")

    telemetry_last = _telemetry_last_timestamp(path)
    teardown_s = telemetry_last - failure_timestamp
    if teardown_s > TEARDOWN_BOUND_S + 1e-9:
        raise SalvageAuthorizationError(
            f"telemetry exceeds the {TEARDOWN_BOUND_S:.3f} s teardown bound"
        )
    signature_payload = {
        "license_branch": "preworkload_environment_admission_abort",
        "terminal_stage": "idle_baseline",
        "failure_reason": failure_reason,
        "claim_reason": "environment_admission_failed",
        "stage_started": started,
    }
    return {
        "licensed": True,
        "license_branch": "preworkload_environment_admission_abort",
        "terminal_stage": "idle_baseline",
        "failure_reason": failure_reason,
        "failure_timestamp_s": failure_timestamp,
        "telemetry_last_timestamp_s": telemetry_last,
        "teardown_s": teardown_s,
        "failure_signature_sha256": _canonical_sha256(signature_payload),
    }


def inspect_salvage_attempt(bundle_path: str | Path) -> dict[str, Any]:
    """Inspect one physical failed occurrence and bind its complete file set."""

    supplied = Path(bundle_path)
    manifest = _enumerate_artifacts(supplied)
    path = supplied.resolve(strict=True)
    by_path = {row["path"]: row for row in manifest}
    missing = [name for name in _REQUIRED_BUNDLE_FILES if name not in by_path]
    if missing:
        raise SalvageAuthorizationError(
            "required salvage evidence missing: " + ", ".join(missing)
        )
    config = _read_json_object(path / "config.json")
    metadata = _read_json_object(path / "metadata.json")
    bundle_id = config.get("run_id")
    if not isinstance(bundle_id, str) or not bundle_id:
        raise SalvageAuthorizationError("config run_id is missing")
    if metadata.get("run_id") != bundle_id:
        raise SalvageAuthorizationError("config and metadata run_id disagree")
    abort = inspect_preworkload_abort(path)
    return {
        "bundle_id": bundle_id,
        "quarantine_path": str(path),
        "config_sha256": by_path["config.json"]["sha256"],
        "metadata_sha256": by_path["metadata.json"]["sha256"],
        "summary_sha256": by_path["summary_metrics.json"]["sha256"],
        "events_sha256": by_path["events.jsonl"]["sha256"],
        "power_trace_sha256": by_path["power_trace.csv"]["sha256"],
        "artifact_manifest": manifest,
        "operator_deviations_flagged": False,
        **abort,
    }


def inspect_launcher_refusal(
    refusal: Mapping[str, Any], custody_roots: Sequence[str | Path]
) -> dict[str, Any]:
    """Validate D-100 b-i: a hash-sealed refusal and no occurrence bytes."""

    payload = {key: value for key, value in refusal.items() if key != "record_sha256"}
    bundle_id = payload.get("bundle_id")
    if (
        payload.get("schema_version") != LAUNCHER_REFUSAL_SCHEMA
        or not isinstance(bundle_id, str)
        or not bundle_id
        or not isinstance(payload.get("timestamp"), str)
        or not payload.get("timestamp")
        or not isinstance(payload.get("reason"), str)
        or not payload.get("reason")
        or not isinstance(payload.get("refusal_code"), str)
        or not payload.get("refusal_code")
        or refusal.get("record_sha256") != _canonical_sha256(payload)
    ):
        raise SalvageAuthorizationError("launcher refusal record is malformed")
    supplied_roots = [Path(value) for value in custody_roots]
    if any(root.is_symlink() for root in supplied_roots):
        raise SalvageAuthorizationError("custody universe contains a symlink")
    roots = [root.resolve(strict=True) for root in supplied_roots]
    if not roots:
        raise SalvageAuthorizationError("launcher refusal custody universe is empty")
    def walk_error(error: OSError) -> None:
        raise SalvageAuthorizationError(
            f"custody universe cannot be exhaustively inspected: {error.filename}"
        ) from error

    for root in roots:
        if not root.is_dir():
            raise SalvageAuthorizationError(f"custody root is not a directory: {root}")
        for parent, directories, files in os.walk(
            root, followlinks=False, onerror=walk_error
        ):
            parent_path = Path(parent)
            if bundle_id in directories or bundle_id in files:
                raise SalvageAuthorizationError("launcher-refused occurrence bytes exist")
            for directory in directories:
                if (parent_path / directory).is_symlink():
                    raise SalvageAuthorizationError(
                        "custody universe contains a symlink"
                    )
            for filename in files:
                candidate = parent_path / filename
                try:
                    mode = candidate.lstat().st_mode
                except OSError as exc:
                    raise SalvageAuthorizationError(
                        "custody universe cannot be exhaustively inspected"
                    ) from exc
                if stat.S_ISLNK(mode):
                    raise SalvageAuthorizationError("custody universe contains a symlink")
                if not stat.S_ISREG(mode):
                    raise SalvageAuthorizationError(
                        "custody universe contains a non-regular node"
                    )
                if filename == "config.json":
                    try:
                        config = json.loads(candidate.read_bytes())
                    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise SalvageAuthorizationError(
                            "custody universe cannot be exhaustively inspected"
                        ) from exc
                    if isinstance(config, Mapping) and config.get("run_id") == bundle_id:
                        raise SalvageAuthorizationError(
                            "launcher-refused occurrence bytes exist"
                        )
    signature_payload = {
        "license_branch": "launcher_refusal_zero_bytes",
        "refusal_code": payload["refusal_code"],
    }
    return {
        "licensed": True,
        "bundle_id": bundle_id,
        "license_branch": "launcher_refusal_zero_bytes",
        "terminal_stage": "launcher",
        "failure_reason": payload["reason"],
        "failure_signature_sha256": _canonical_sha256(signature_payload),
        "refusal_record": dict(refusal),
        "custody_roots": [str(root) for root in roots],
        "operator_deviations_flagged": False,
    }


def _binding_descriptor(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise SalvageAuthorizationError("membership binding is a symlink")
    descriptor = _descriptor(path)
    payload = _read_json_object(path)
    policy_sha = payload.get("campaign_policy_sha256")
    manifests = payload.get("source_campaign_manifests")
    if (
        payload.get("schema_version") != MEMBERSHIP_BINDING_SCHEMA
        or not _sha256_text(policy_sha)
        or not isinstance(manifests, list)
        or not manifests
    ):
        raise SalvageAuthorizationError("membership binding schema is invalid")
    normalized: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for row in manifests:
        if not isinstance(row, Mapping):
            raise SalvageAuthorizationError("membership manifest descriptor is invalid")
        manifest_path = row.get("path")
        size = row.get("size")
        if (
            not isinstance(manifest_path, str)
            or not manifest_path
            or manifest_path in seen_paths
            or not _sha256_text(row.get("sha256"))
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
        ):
            raise SalvageAuthorizationError("membership manifest descriptor is invalid")
        seen_paths.add(manifest_path)
        normalized.append(
            {key: row.get(key) for key in ("path", "sha256", "size")}
        )
    normalized.sort(key=lambda row: row["path"])
    membership_id = _canonical_sha256(normalized)
    if manifests != normalized or payload.get("membership_id") != membership_id:
        raise SalvageAuthorizationError("membership binding identity is invalid")
    descriptor.update(
        {
            "membership_id": membership_id,
            "campaign_policy_sha256": policy_sha,
            "source_campaign_manifests": normalized,
        }
    )
    return descriptor


def load_salvage_closure(
    closure_path: str | Path,
    *,
    expected_policy_sha256: str | None = None,
    expected_membership_binding_sha256: str | None = None,
) -> dict[str, Any]:
    """Load and re-authenticate one exactly-three-occurrence D-087 closure."""

    supplied_path = Path(closure_path)
    if supplied_path.is_symlink():
        raise SalvageAuthorizationError("salvage closure is a symlink")
    path = supplied_path.resolve(strict=True)
    value = _read_json_object(path)
    if value.get("schema_version") != SALVAGE_CLOSURE_SCHEMA:
        raise SalvageAuthorizationError("salvage closure schema is invalid")
    policy_sha = value.get("campaign_policy_sha256")
    binding_sha = value.get("membership_binding_sha256")
    if not _sha256_text(policy_sha) or not _sha256_text(binding_sha):
        raise SalvageAuthorizationError("closure policy or membership binding is unbound")
    if expected_policy_sha256 is not None and policy_sha != expected_policy_sha256:
        raise SalvageAuthorizationError("closure campaign policy mismatch")
    if (
        expected_membership_binding_sha256 is not None
        and binding_sha != expected_membership_binding_sha256
    ):
        raise SalvageAuthorizationError("closure membership binding mismatch")
    occurrences = value.get("occurrences")
    if not isinstance(occurrences, list) or len(occurrences) != 3:
        raise SalvageAuthorizationError("D-087 closure requires exactly three occurrences")
    terminal_index = value.get("terminal_occurrence_index")
    if terminal_index != 2:
        raise SalvageAuthorizationError("third D-087 occurrence must be terminal")
    custody_roots = value.get("custody_roots")
    if (
        not isinstance(custody_roots, list)
        or not custody_roots
        or any(not isinstance(root, str) or not root for root in custody_roots)
    ):
        raise SalvageAuthorizationError("closure custody-root universe is malformed")
    if not isinstance(value.get("opened_at"), str) or not isinstance(
        value.get("closed_at"), str
    ):
        raise SalvageAuthorizationError("closure timestamps are missing")

    inspected: list[dict[str, Any]] = []
    for occurrence in occurrences:
        if not isinstance(occurrence, Mapping):
            raise SalvageAuthorizationError("closure occurrence is not an object")
        evidence_paths = occurrence.get("evidence_paths")
        deviations = occurrence.get("operator_deviations")
        occurrence_timestamp = occurrence.get("timestamp")
        if not isinstance(evidence_paths, list) or not evidence_paths:
            raise SalvageAuthorizationError("closure occurrence has no evidence paths")
        if not isinstance(deviations, list):
            raise SalvageAuthorizationError("operator deviations are not recorded")
        if not isinstance(occurrence_timestamp, str) or not occurrence_timestamp:
            raise SalvageAuthorizationError("closure occurrence timestamp is missing")
        branch = occurrence.get("license_branch")
        if branch == "preworkload_environment_admission_abort":
            attempt_path = occurrence.get("quarantine_path")
            if not isinstance(attempt_path, str) or not attempt_path:
                raise SalvageAuthorizationError("closure attempt path is missing")
            observation = inspect_salvage_attempt(attempt_path)
        elif branch == "launcher_refusal_zero_bytes":
            refusal_path_text = occurrence.get("launcher_refusal_path")
            if not isinstance(refusal_path_text, str) or not refusal_path_text:
                raise SalvageAuthorizationError(
                    "closure launcher refusal path is missing"
                )
            refusal_path = Path(refusal_path_text)
            if refusal_path.is_symlink():
                raise SalvageAuthorizationError(
                    "closure launcher refusal path is a symlink"
                )
            try:
                refusal_path = refusal_path.resolve(strict=True)
                if not stat.S_ISREG(refusal_path.lstat().st_mode):
                    raise SalvageAuthorizationError(
                        "closure launcher refusal is not a regular file"
                    )
            except OSError as exc:
                raise SalvageAuthorizationError(
                    "closure launcher refusal is unreadable"
                ) from exc
            record = _read_json_object(refusal_path)
            observation = inspect_launcher_refusal(record, custody_roots)
            observation["launcher_refusal_path"] = str(refusal_path)
            observation["artifact_manifest"] = [_descriptor(refusal_path)]
        else:
            raise SalvageAuthorizationError("unknown closure license branch")
        if branch in {
            "preworkload_environment_admission_abort",
            "launcher_refusal_zero_bytes",
        }:
            expected_paths = [
                {
                    key: row.get(key)
                    for key in ("path", "sha256", "size")
                }
                for row in evidence_paths
                if isinstance(row, Mapping)
            ]
            actual_paths = observation.get("artifact_manifest", [])
            if (
                len(expected_paths) != len(evidence_paths)
                or expected_paths != actual_paths
            ):
                raise SalvageAuthorizationError(
                    "closure evidence paths do not match bundle bytes"
                )
        if occurrence.get("failure_signature_sha256") != observation.get(
            "failure_signature_sha256"
        ):
            raise SalvageAuthorizationError("closure failure signature mismatch")
        observation["operator_deviations_flagged"] = bool(deviations)
        observation["operator_deviations"] = [
            dict(row) if isinstance(row, Mapping) else row for row in deviations
        ]
        observation["timestamp"] = occurrence_timestamp
        inspected.append(observation)
    signatures = {row["failure_signature_sha256"] for row in inspected}
    if len(signatures) != 1:
        raise SalvageAuthorizationError("D-087 occurrences are not the same failure")
    return {
        **value,
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": path.stat().st_size,
        "inspected_occurrences": inspected,
    }


def build_salvage_exclusion_payload(
    closure: Mapping[str, Any], membership_binding_path: str | Path
) -> dict[str, Any]:
    """Build the hash-sealed compound-semantic exclusion payload."""

    binding_path = Path(membership_binding_path)
    binding = _binding_descriptor(binding_path)
    if (
        closure.get("membership_binding_sha256") != binding["sha256"]
        or closure.get("campaign_policy_sha256")
        != binding["campaign_policy_sha256"]
    ):
        raise SalvageAuthorizationError("closure and membership binding disagree")
    inspected = closure.get("inspected_occurrences")
    if not isinstance(inspected, list) or len(inspected) != 3:
        raise SalvageAuthorizationError("closure has not been mechanically inspected")
    terminal_index = closure.get("terminal_occurrence_index")
    terminal = (
        inspected[terminal_index]
        if isinstance(terminal_index, int)
        and not isinstance(terminal_index, bool)
        and 0 <= terminal_index < len(inspected)
        else None
    )
    terminal_bundle_id = terminal.get("bundle_id") if isinstance(terminal, Mapping) else None
    if not isinstance(terminal_bundle_id, str) or not terminal_bundle_id:
        raise SalvageAuthorizationError("closure terminal occurrence has no member id")
    payload: dict[str, Any] = {
        "schema_version": SALVAGE_EXCLUSION_SCHEMA,
        "disposition": "whole_window_member_terminally_absent_salvage",
        "bundle_id": terminal_bundle_id,
        "campaign_policy_sha256": closure.get("campaign_policy_sha256"),
        "membership_id": binding.get("membership_id"),
        "closure": {
            key: closure.get(key) for key in ("path", "sha256", "size")
        },
        "membership_binding": binding,
        "attempts": [
            {
                key: row.get(key)
                for key in (
                    "bundle_id",
                    "quarantine_path",
                    "config_sha256",
                    "metadata_sha256",
                    "summary_sha256",
                    "events_sha256",
                    "power_trace_sha256",
                    "artifact_manifest",
                    "terminal_stage",
                    "failure_reason",
                    "license_branch",
                    "failure_signature_sha256",
                    "operator_deviations_flagged",
                    "operator_deviations",
                    "refusal_record",
                    "launcher_refusal_path",
                    "custody_roots",
                    "timestamp",
                )
                if key in row
            }
            for row in inspected
            if isinstance(row, Mapping)
        ],
        "operator_deviations_flagged": any(
            row.get("operator_deviations_flagged") is True
            for row in inspected
            if isinstance(row, Mapping)
        ),
    }
    return {**payload, "payload_sha256": _canonical_sha256(payload)}


def validate_salvage_exclusion_payload(
    payload: Mapping[str, Any], *, revalidate_bytes: bool = True
) -> bool:
    """Validate the closed payload shape and, by default, every named byte."""

    core = {key: value for key, value in payload.items() if key != "payload_sha256"}
    if (
        payload.get("schema_version") != SALVAGE_EXCLUSION_SCHEMA
        or payload.get("disposition")
        != "whole_window_member_terminally_absent_salvage"
        or not isinstance(payload.get("bundle_id"), str)
        or not payload.get("bundle_id")
        or not _sha256_text(payload.get("campaign_policy_sha256"))
        or payload.get("payload_sha256") != _canonical_sha256(core)
        or not isinstance(payload.get("attempts"), list)
        or len(payload["attempts"]) != 3
    ):
        return False
    closure = payload.get("closure")
    binding = payload.get("membership_binding")
    if not isinstance(closure, Mapping) or not isinstance(binding, Mapping):
        return False
    for descriptor in (closure, binding):
        if (
            not isinstance(descriptor.get("path"), str)
            or not _sha256_text(descriptor.get("sha256"))
            or isinstance(descriptor.get("size"), bool)
            or not isinstance(descriptor.get("size"), int)
            or descriptor.get("size") < 0
        ):
            return False
    if not revalidate_bytes:
        return True
    try:
        closure_path = Path(closure["path"]).resolve(strict=True)
        binding_path = Path(binding["path"]).resolve(strict=True)
        if _descriptor(closure_path) != {
            key: closure.get(key) for key in ("path", "sha256", "size")
        }:
            return False
        if _descriptor(binding_path) != {
            key: binding.get(key) for key in ("path", "sha256", "size")
        }:
            return False
        loaded = load_salvage_closure(
            closure_path,
            expected_policy_sha256=payload["campaign_policy_sha256"],
            expected_membership_binding_sha256=binding["sha256"],
        )
        return build_salvage_exclusion_payload(loaded, binding_path) == dict(payload)
    except (OSError, SalvageAuthorizationError, TypeError, ValueError):
        return False


def authorize_salvage_dangler_exclusion(
    closure_path: str | Path,
    membership_binding_path: str | Path,
    *,
    campaign_policy_sha256: str,
    terminal_absent_bundle_ids: Sequence[str],
    waivers: object = None,
) -> dict[str, Any]:
    """Authorize the single exceptional absence, or fail closed."""

    if waivers not in (None, (), [], {}):
        raise SalvageAuthorizationError("waivers are forbidden in salvage mode")
    absent = list(terminal_absent_bundle_ids)
    if len(absent) != 1 or not isinstance(absent[0], str) or not absent[0]:
        raise SalvageAuthorizationError("salvage exclusion cap is exactly one")
    binding_path = Path(membership_binding_path)
    binding_descriptor = _binding_descriptor(binding_path)
    closure = load_salvage_closure(
        closure_path,
        expected_policy_sha256=campaign_policy_sha256,
        expected_membership_binding_sha256=binding_descriptor["sha256"],
    )
    payload = build_salvage_exclusion_payload(closure, binding_path)
    if payload.get("bundle_id") != absent[0] or not validate_salvage_exclusion_payload(
        payload
    ):
        raise SalvageAuthorizationError("closure does not license the absent member")
    return payload


__all__ = [
    "LAUNCHER_REFUSAL_SCHEMA",
    "MEMBERSHIP_BINDING_SCHEMA",
    "SALVAGE_CLOSURE_SCHEMA",
    "SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID",
    "SALVAGE_EXCLUSION_SCHEMA",
    "SalvageAuthorizationError",
    "TEARDOWN_BOUND_S",
    "authorize_salvage_dangler_exclusion",
    "build_salvage_exclusion_payload",
    "inspect_launcher_refusal",
    "inspect_preworkload_abort",
    "inspect_salvage_attempt",
    "load_salvage_closure",
    "validate_salvage_exclusion_payload",
]
