"""Fail-closed privacy audit and public-bundle transformation.

Private run bundles are immutable evidence.  This module never edits them.  It
audits the complete relative-path surface, rejects unclassified structured
fields, and writes a deliberately non-byte-identical public projection into a
new directory.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POLICY_SCHEMA = "joulewise.publication_privacy.v1"
TRANSFORMATION_SCHEMA = "joulewise.publication_transformation.v1"
REDACTED_TEXT = "[REDACTED:PUBLICATION_PRIVACY]"
REDACTED_PATH = "[REDACTED:ABSOLUTE_PATH]"
REDACTED_IDENTITY = "[REDACTED:USER_OR_HOST_IDENTITY]"
TREE_IDENTITY_ALGORITHM = "sha256"
TREE_IDENTITY_VERSION = "joulewise.bundle-tree.nul-v1"
SOURCE_PROVENANCE_SCHEMA = "joulewise.source_provenance.v1"
SOURCE_DIFF_IDENTITY_ALGORITHM = "sha256"
SOURCE_DIFF_IDENTITY_VERSION = "joulewise.git-diff.nul-v1"
SOURCE_STATE_VALUES = frozenset({"clean", "dirty", "unknown"})
REDACTED_CONTENT = "[REDACTED:PROMPT_OR_RESPONSE_CONTENT]"
REDACTED_CLEANUP_PATH = "[REDACTED:REMOTE_CLEANUP_PATH]"

CLASS_RETAIN = "retain_reviewed_measurement"
CLASS_TRANSFORM = "transform_reviewed_structure"
CLASS_OMIT_CONTENT = "omit_prompt_response_or_token_content"
CLASS_OMIT_LOG = "omit_controller_or_worker_log"
CLASS_OMIT_CUSTODY_LOG = "omit_machine_local_custody_operational_log"
CLASS_OMIT_RAW = "omit_backend_native_or_rich_telemetry"

OP_RETAIN = "retain_bytes"
OP_TRANSFORM_JSON = "transform_json"
OP_TRANSFORM_JSONL = "transform_jsonl"
OP_OMIT = "omit"

_CONFIG_KEYS: dict[str, frozenset[str]] = {
    "": frozenset(
        {
            "schema_version",
            "run_id",
            "model",
            "quantization",
            "hardware_target",
            "workload_profile",
            "interconnect",
            "sampling",
            "run_metadata",
        }
    ),
    "model": frozenset(
        {"name", "family", "source", "revision", "weight_format", "context_window"}
    ),
    "quantization": frozenset({"name", "bits", "group_size"}),
    "hardware_target": frozenset(
        {"id", "transport", "runtime_backend", "telemetry_backend", "host", "device_kind", "notes"}
    ),
    "workload_profile": frozenset(
        {
            "name",
            "prompt_tokens",
            "output_tokens",
            "prompt_text",
            "dataset_ref",
            "suite_manifest_ref",
            "suite_manifest_sha256",
            "generator_sidecar_ref",
            "repetitions",
            "warmup_runs",
        }
    ),
    "interconnect": frozenset({"name", "link_speed_mbps", "notes"}),
    "sampling": frozenset({"power_hz", "idle_seconds", "warmup_seconds"}),
    "run_metadata": frozenset({"project", "operator", "ambient_temp_c", "notes", "tags"}),
}

_METADATA_KEYS = frozenset(
    {
        "platform",
        "machine",
        "python_version",
        "joulewise_version",
        "schema_version",
        "config_sha256",
        "run_id",
        "git_commit",
        "source_provenance",
        "clock",
        "config_warnings",
        "model",
        "quantization",
        "device",
        "connection",
        "environment",
        "adapters",
        "idle_baseline",
        "thermal_pre",
        "thermal_post",
        "uncertainty_evidence",
        "clock_anchor_bound_s",
        "marker_to_first_sample_phase_bound_s",
        "marker_to_last_sample_phase_bound_s",
        "idle_drift_bound_w",
        "trace_window_margins",
        "workload_observed",
        "workload_provenance",
        "suite",
        "extra",
        # Private diagnostics can contain adapter-defined metadata paths, so
        # the public transform accepts the field but redacts its whole subtree.
        "serialization_quarantine",
    }
)

# These metadata fields are scalar provenance or governed numeric evidence.
# Every other reviewed top-level field is replaced as a complete subtree.  The
# subtree classification is intentional: it covers future values without ever
# copying an unreviewed nested field into the public artifact.
_METADATA_RETAIN_KEYS = frozenset(
    {
        "config_sha256",
        "git_commit",
        "source_provenance",
        "clock_anchor_bound_s",
        "marker_to_first_sample_phase_bound_s",
        "marker_to_last_sample_phase_bound_s",
        "idle_drift_bound_w",
        "trace_window_margins",
    }
)

_SUMMARY_REDACTED_SUBTREES = frozenset(
    {
        "idle_baseline",
        "uncertainty",
        "phase_energy_j",
        "suite_metrics",
        "energy_variance_terms_j2",
        "energy_bound_terms_j",
        "claim_eligibility",
        "window_evidence_precheck",
        "summary_provenance",
    }
)
_QUALITY_TELEMETRY_SOURCES = frozenset(
    {"mock", "powermetrics", "nvidia_smi", "jetson_rails", "wall_meter"}
)
_QUALITY_TOKEN_SOURCES = frozenset(
    {"runtime_observed", "config_fallback", "server_usage", "stream_chunk_fallback"}
)

_SUMMARY_KEYS = frozenset(
    {
        "status",
        "energy_request_j",
        "energy_token_j",
        "energy_output_token_j",
        "gross_energy_j",
        "idle_subtracted_energy_j",
        "ttft_s",
        "decode_latency_s",
        "throughput_tokens_s",
        "inter_token_throughput_tokens_s",
        "idle_baseline",
        "uncertainty",
        "measurement_quality",
        "phase_energy_j",
        "suite_metrics",
        "energy_uncertainty_status",
        "idle_mean_uncertainty",
        "energy_variance_terms_j2",
        "energy_bound_terms_j",
        "claim_eligibility",
        "window_evidence_precheck",
        "summary_provenance",
        "failure_reason",
        "failure_message",
    }
)

_IDLE_MEAN_UNCERTAINTY_KEYS = frozenset(
    {
        "status",
        "method",
        "source_artifact",
        "source_sha256",
        "raw_sample_count",
        "median_sample_interval_s",
        "cadence_p95_p05_ratio",
        "bandwidth_s",
        "lag_count",
        "sample_variance_w2",
        "iid_variance_of_mean_w2",
        "hac_variance_of_mean_w2",
        "governed_variance_of_mean_w2",
        "effective_sample_size",
        "correlation_scope",
        "reason_codes",
    }
)
_IDLE_MEAN_UNCERTAINTY_NUMERIC_KEYS = frozenset(
    {
        "median_sample_interval_s",
        "cadence_p95_p05_ratio",
        "sample_variance_w2",
        "iid_variance_of_mean_w2",
        "hac_variance_of_mean_w2",
        "governed_variance_of_mean_w2",
        "effective_sample_size",
    }
)
_IDLE_MEAN_UNCERTAINTY_REASON_CODES = frozenset(
    {
        "raw_idle_trace_unavailable",
        "raw_idle_trace_invalid",
        "nonfinite_idle_power",
        "insufficient_idle_samples",
        "idle_trace_span_below_three_bandwidths",
        "idle_cadence_irregular",
        "idle_metadata_mismatch",
        "backend_policy_not_frozen",
    }
)

_MEASUREMENT_QUALITY_KEYS = frozenset(
    {
        "requested_sampling_hz",
        "observed_sampling_hz",
        "dropped_samples",
        "idle_power_w_stddev",
        "thermal_drift_c",
        "telemetry_source",
        "cooldown_cap_hit",
        "token_count_source",
        "idle_window_suspect",
        "token_counts_source",
        "phase_identifiability",
        "remote_cleanup_failed",
        "runtime_cleanup_ok",
    }
)

_EVENT_KEYS = frozenset({"timestamp_s", "event_type", "phase", "message", "metadata"})
_REQUIRED_CORE_PATHS = frozenset(
    {"config.json", "metadata.json", "events.jsonl", "summary_metrics.json"}
)
_RAW_PATHS = frozenset(
    {
        "raw/mock_samples.json",
        "raw/powermetrics.plist",
        "raw/powermetrics_idle.plist",
        "raw/powermetrics_idle_post.plist",
        "raw/nvidia_smi.csv",
        "raw/nvidia_smi_idle.csv",
        "raw/vllm_events.jsonl",
        "raw/vllm_response.txt",
        "raw/vllm_tokens.jsonl",
    }
)
_RICH_PATHS = frozenset(
    {"rich_telemetry.jsonl", "rich_telemetry_idle.jsonl", "rich_telemetry_idle_post.jsonl"}
)
_OUTPUT_PATHS = frozenset(
    {"outputs/response.txt", "outputs/tokens.jsonl", "outputs/suite_items.jsonl"}
)
_LOG_PATHS = frozenset({"logs/controller.log", "logs/runtime.log", "logs/telemetry.log"})
_WORKER_LOG_RE = re.compile(
    r"logs/(?:(?:task-(?:runtime|telemetry)-[a-z0-9_-]+-[0-9]{3})|"
    r"(?:(?:nvidia-smi|vllm)-[a-z0-9_-]+))_worker\.log\Z"
)
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_POWER_SOURCES = frozenset({"mock", "powermetrics", "nvidia_smi"})
_POWER_RAILS = frozenset({"", "mock", "cpu_power", "gpu_power", "ane_power", "gpu_board"})
_IDLE_MEAN_UNCERTAINTY_METHODS = frozenset(
    {
        "newey_west_bartlett_10s_iid_floor_v1",
        "duration_weighted_newey_west_bartlett_10s_iid_floor_v2",
    }
)
_POWER_TRACE_POINT_COLUMNS = (
    "timestamp_s",
    "power_w",
    "source",
    "rail",
)
_POWER_TRACE_INTERVAL_COLUMNS = (
    *_POWER_TRACE_POINT_COLUMNS,
    "interval_start_s",
    "interval_end_s",
)


class PrivacyAuditError(RuntimeError):
    """Raised when a private bundle contains an unreviewed publication surface."""


@dataclass(frozen=True)
class AuditedFile:
    path: str
    classification: str
    operation: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class PrivacyAudit:
    schema: str
    source_bundle_sha256: str
    files: tuple[AuditedFile, ...]
    classification_counts: dict[str, int]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_identity_descriptor() -> dict[str, str]:
    """Return the canonical bundle-tree identity algorithm/version descriptor."""

    return {
        "algorithm": TREE_IDENTITY_ALGORITHM,
        "version": TREE_IDENTITY_VERSION,
    }


def tree_sha256(entries: list[dict[str, Any]] | tuple[AuditedFile, ...]) -> str:
    """Fold sorted path/hash/size entries with NUL field delimiters.

    This is the canonical ``joulewise.bundle-tree.nul-v1`` identity primitive
    shared by publication packs and versioned report artifacts.
    """

    digest = hashlib.sha256()
    for item in sorted(entries, key=lambda value: value.path if isinstance(value, AuditedFile) else value["path"]):
        if isinstance(item, AuditedFile):
            path, file_hash, size = item.path, item.sha256, item.size_bytes
        else:
            path, file_hash, size = item["path"], item["sha256"], item["size_bytes"]
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _path_policy(rel: str) -> tuple[str, str] | None:
    if rel in {"config.json", "metadata.json", "summary_metrics.json"}:
        return CLASS_TRANSFORM, OP_TRANSFORM_JSON
    if rel == "events.jsonl":
        return CLASS_TRANSFORM, OP_TRANSFORM_JSONL
    if rel == "power_trace.csv":
        return CLASS_RETAIN, OP_RETAIN
    if rel == "suite_manifest.json" or rel in _OUTPUT_PATHS:
        return CLASS_OMIT_CONTENT, OP_OMIT
    # Custody acknowledgements are operational recovery records.  Their
    # artifact paths are meaningful only on the machine holding the private
    # bundle, so name the class in the audited inventory and never publish it.
    if rel.startswith("logs/custody/"):
        return CLASS_OMIT_CUSTODY_LOG, OP_OMIT
    if rel in _LOG_PATHS or _WORKER_LOG_RE.fullmatch(rel):
        return CLASS_OMIT_LOG, OP_OMIT
    if rel in _RAW_PATHS or rel in _RICH_PATHS:
        return CLASS_OMIT_RAW, OP_OMIT
    return None


def classification_for_path(rel: str) -> tuple[str, str] | None:
    """Return the reviewed classification/operation for a bundle-relative path."""

    return _path_policy(rel)


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PrivacyAuditError(f"{label} is not readable JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PrivacyAuditError(f"{label} must be a JSON object: {path}")
    return value


def _unknown_keys(actual: set[str], allowed: frozenset[str], label: str) -> None:
    unknown = sorted(actual - allowed)
    if unknown:
        raise PrivacyAuditError(
            f"unclassified field(s) in {label}: {', '.join(unknown)}"
        )


def _audit_config(path: Path) -> None:
    value = _load_json_object(path, "config.json")
    _unknown_keys(set(value), _CONFIG_KEYS[""], "config.json")
    for section, allowed in _CONFIG_KEYS.items():
        if not section or section not in value:
            continue
        child = value[section]
        if not isinstance(child, dict):
            raise PrivacyAuditError(f"config.json.{section} must be an object")
        _unknown_keys(set(child), allowed, f"config.json.{section}")


def _audit_metadata(path: Path) -> None:
    value = _load_json_object(path, "metadata.json")
    _unknown_keys(set(value), _METADATA_KEYS, "metadata.json")
    for key in (
        "clock_anchor_bound_s",
        "marker_to_first_sample_phase_bound_s",
        "marker_to_last_sample_phase_bound_s",
        "idle_drift_bound_w",
    ):
        if key in value and value[key] is not None and not isinstance(value[key], (int, float)):
            raise PrivacyAuditError(f"metadata.json.{key} is not numeric or null")
    margins = value.get("trace_window_margins")
    if margins is not None:
        expected_margin_keys = {
            "requested_post_window_dwell_s",
            "achieved_pre_window_margin_s",
            "achieved_post_window_margin_s",
        }
        if not isinstance(margins, dict) or set(margins) != expected_margin_keys:
            raise PrivacyAuditError(
                "metadata.json.trace_window_margins must have the exact governed keys"
            )
        for key, margin in margins.items():
            if (
                isinstance(margin, bool)
                or not isinstance(margin, (int, float))
                or not math.isfinite(float(margin))
            ):
                raise PrivacyAuditError(
                    f"metadata.json.trace_window_margins.{key} is not finite numeric evidence"
                )
        if float(margins["requested_post_window_dwell_s"]) < 0.0:
            raise PrivacyAuditError(
                "metadata.json.trace_window_margins.requested_post_window_dwell_s "
                "must be nonnegative"
            )
    config_hash = value.get("config_sha256")
    if config_hash is not None and (
        not isinstance(config_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", config_hash)
    ):
        raise PrivacyAuditError("metadata.json.config_sha256 is not a lowercase SHA-256")
    git_commit = value.get("git_commit")
    if git_commit is not None and git_commit != "unknown" and (
        not isinstance(git_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", git_commit)
    ):
        raise PrivacyAuditError("metadata.json.git_commit is not a lowercase Git object id")
    if "source_provenance" in value:
        problems = source_provenance_problems(value["source_provenance"])
        if problems:
            raise PrivacyAuditError(f"metadata.json.source_provenance: {problems[0]}")
        if git_commit != value["source_provenance"]["start"]["git_commit"]:
            raise PrivacyAuditError(
                "metadata.json.git_commit does not match source_provenance.start.git_commit"
            )


def _source_snapshot_problems(value: Any, label: str) -> list[str]:
    problems: list[str] = []
    required = {"git_commit", "tracked", "staged", "untracked", "diff_sha256"}
    if not isinstance(value, dict):
        return [f"{label} must be an object"]
    actual = set(value)
    if actual != required:
        problems.append(
            f"{label} keys must be exactly {', '.join(sorted(required))}"
        )
        return problems
    commit = value["git_commit"]
    if commit != "unknown" and (
        not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit)
    ):
        problems.append(f"{label}.git_commit must be unknown or a lowercase Git object id")
    for component in ("tracked", "staged", "untracked"):
        if (
            not isinstance(value[component], str)
            or value[component] not in SOURCE_STATE_VALUES
        ):
            problems.append(
                f"{label}.{component} must be clean, dirty, or unknown"
            )
    diff_sha256 = value["diff_sha256"]
    if diff_sha256 != "unknown" and (
        not isinstance(diff_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", diff_sha256)
    ):
        problems.append(
            f"{label}.diff_sha256 must be unknown or a lowercase SHA-256"
        )
    components_known = all(
        value[component] != "unknown" for component in ("tracked", "staged", "untracked")
    )
    if components_known != (diff_sha256 != "unknown"):
        problems.append(
            f"{label}.diff_sha256 must be known exactly when all diff components are known"
        )
    return problems


def _snapshot_fully_known(value: dict[str, Any]) -> bool:
    return all(value[key] != "unknown" for key in value)


def _expected_source_reason_codes(
    start: dict[str, Any],
    end: dict[str, Any],
    changed_during_run: bool | None,
) -> list[str]:
    reasons: list[str] = []
    for phase, state in (("start", start), ("end", end)):
        if state["git_commit"] == "unknown":
            reasons.append(f"{phase}_git_commit_unknown")
        for component in ("tracked", "staged", "untracked"):
            if state[component] == "unknown":
                reasons.append(f"{phase}_{component}_unknown")
            elif state[component] == "dirty":
                reasons.append(f"{phase}_{component}_dirty")
        if state["diff_sha256"] == "unknown":
            reasons.append(f"{phase}_diff_identity_unknown")
    if changed_during_run is True:
        reasons.append("source_changed_during_run")
    return reasons


def source_provenance_problems(
    value: Any, *, require_eligible: bool = False
) -> list[str]:
    """Validate the governed source-provenance record and its eligibility rule."""

    required = {
        "schema",
        "diff_identity",
        "start",
        "end",
        "changed_during_run",
        "claim_eligible",
        "reason_codes",
    }
    if not isinstance(value, dict):
        return ["must be an object"]
    if set(value) != required:
        return [f"keys must be exactly {', '.join(sorted(required))}"]
    problems: list[str] = []
    if value["schema"] != SOURCE_PROVENANCE_SCHEMA:
        problems.append(f"schema must be {SOURCE_PROVENANCE_SCHEMA}")
    if value["diff_identity"] != {
        "algorithm": SOURCE_DIFF_IDENTITY_ALGORITHM,
        "version": SOURCE_DIFF_IDENTITY_VERSION,
    }:
        problems.append("diff_identity descriptor is not governed")
    problems.extend(_source_snapshot_problems(value["start"], "start"))
    problems.extend(_source_snapshot_problems(value["end"], "end"))
    if problems:
        return problems

    start = value["start"]
    end = value["end"]
    expected_changed: bool | None = None
    if _snapshot_fully_known(start) and _snapshot_fully_known(end):
        expected_changed = start != end
    if value["changed_during_run"] is not expected_changed:
        problems.append(
            f"changed_during_run must be {expected_changed!r} for the recorded snapshots"
        )
    expected_reasons = _expected_source_reason_codes(start, end, expected_changed)
    if value["reason_codes"] != expected_reasons:
        problems.append("reason_codes do not match the recorded snapshots")
    expected_eligible = not expected_reasons
    if not isinstance(value["claim_eligible"], bool) or value["claim_eligible"] is not expected_eligible:
        problems.append(
            f"claim_eligible must be {expected_eligible!r} for the recorded snapshots"
        )
    if require_eligible and not expected_eligible:
        problems.append(
            "claim-ineligible source provenance: " + ", ".join(expected_reasons)
        )
    return problems


def _audit_summary(path: Path) -> None:
    value = _load_json_object(path, "summary_metrics.json")
    _unknown_keys(set(value), _SUMMARY_KEYS, "summary_metrics.json")
    inter_token_throughput = value.get("inter_token_throughput_tokens_s")
    if inter_token_throughput is not None and (
        isinstance(inter_token_throughput, bool)
        or not isinstance(inter_token_throughput, (int, float))
        or not math.isfinite(inter_token_throughput)
    ):
        raise PrivacyAuditError(
            "summary_metrics.json.inter_token_throughput_tokens_s is not finite numeric or null"
        )
    idle_mean = value.get("idle_mean_uncertainty")
    if idle_mean is not None:
        _audit_idle_mean_uncertainty(idle_mean)
    quality = value.get("measurement_quality")
    if quality is not None:
        if not isinstance(quality, dict):
            raise PrivacyAuditError("summary_metrics.json.measurement_quality must be an object or null")
        _unknown_keys(
            set(quality),
            _MEASUREMENT_QUALITY_KEYS,
            "summary_metrics.json.measurement_quality",
        )
        telemetry_source = quality.get("telemetry_source")
        if telemetry_source is not None and telemetry_source not in _QUALITY_TELEMETRY_SOURCES:
            raise PrivacyAuditError(
                "summary_metrics.json.measurement_quality.telemetry_source is unclassified"
            )
        for key in ("token_count_source", "token_counts_source"):
            source = quality.get(key)
            if source is not None and source not in _QUALITY_TOKEN_SOURCES:
                raise PrivacyAuditError(
                    f"summary_metrics.json.measurement_quality.{key} is unclassified"
                )


def _audit_idle_mean_uncertainty(value: Any) -> None:
    label = "summary_metrics.json.idle_mean_uncertainty"
    if not isinstance(value, dict):
        raise PrivacyAuditError(f"{label} must be an object or null")
    actual = set(value)
    _unknown_keys(actual, _IDLE_MEAN_UNCERTAINTY_KEYS, label)
    missing = sorted(_IDLE_MEAN_UNCERTAINTY_KEYS - actual)
    if missing:
        raise PrivacyAuditError(f"{label} is missing governed field(s): {', '.join(missing)}")
    if not isinstance(value["status"], str) or value["status"] not in {
        "estimated",
        "not_estimable",
    }:
        raise PrivacyAuditError(f"{label}.status is unclassified")
    if value["method"] not in _IDLE_MEAN_UNCERTAINTY_METHODS:
        raise PrivacyAuditError(f"{label}.method is unclassified")
    if value["source_artifact"] != "raw/powermetrics_idle.plist":
        raise PrivacyAuditError(f"{label}.source_artifact is unclassified")
    source_sha256 = value["source_sha256"]
    if source_sha256 is not None and (
        not isinstance(source_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", source_sha256)
    ):
        raise PrivacyAuditError(f"{label}.source_sha256 is not a lowercase SHA-256 or null")
    for key in ("raw_sample_count", "lag_count"):
        inner = value[key]
        if inner is not None and (
            isinstance(inner, bool) or not isinstance(inner, int) or inner < 0
        ):
            raise PrivacyAuditError(f"{label}.{key} is not a nonnegative integer or null")
    for key in _IDLE_MEAN_UNCERTAINTY_NUMERIC_KEYS:
        inner = value[key]
        if inner is not None and (
            isinstance(inner, bool)
            or not isinstance(inner, (int, float))
            or not math.isfinite(inner)
        ):
            raise PrivacyAuditError(f"{label}.{key} is not finite numeric or null")
    if value["bandwidth_s"] != 10.0 or isinstance(value["bandwidth_s"], bool):
        raise PrivacyAuditError(f"{label}.bandwidth_s is not the governed value 10.0")
    if value["correlation_scope"] != "independent_run":
        raise PrivacyAuditError(f"{label}.correlation_scope is unclassified")
    reason_codes = value["reason_codes"]
    if not isinstance(reason_codes, list) or any(
        not isinstance(reason, str) or reason not in _IDLE_MEAN_UNCERTAINTY_REASON_CODES
        for reason in reason_codes
    ):
        raise PrivacyAuditError(f"{label}.reason_codes contains an unclassified value")


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise PrivacyAuditError(f"{label} is not readable UTF-8: {path}: {exc}") from exc
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PrivacyAuditError(f"{label} line {index} is not JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise PrivacyAuditError(f"{label} line {index} must be a JSON object")
        records.append(value)
    return records


def _audit_events(path: Path) -> None:
    for index, record in enumerate(_read_jsonl(path, "events.jsonl"), start=1):
        actual = set(record)
        if actual != _EVENT_KEYS:
            missing = sorted(_EVENT_KEYS - actual)
            unknown = sorted(actual - _EVENT_KEYS)
            details = []
            if missing:
                details.append(f"missing {', '.join(missing)}")
            if unknown:
                details.append(f"unclassified {', '.join(unknown)}")
            raise PrivacyAuditError(f"events.jsonl line {index}: {'; '.join(details)}")
        if not isinstance(record.get("metadata"), dict):
            raise PrivacyAuditError(f"events.jsonl line {index}.metadata must be an object")


def _audit_power_trace(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PrivacyAuditError(f"power_trace.csv is not readable UTF-8: {path}: {exc}") from exc
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration as exc:
        raise PrivacyAuditError("power_trace.csv is empty") from exc
    expected_headers = {
        _POWER_TRACE_POINT_COLUMNS,
        _POWER_TRACE_INTERVAL_COLUMNS,
    }
    header_tuple = tuple(header)
    if header_tuple not in expected_headers:
        raise PrivacyAuditError(
            "unclassified power_trace.csv columns: expected exactly "
            f"{list(_POWER_TRACE_POINT_COLUMNS)!r} or "
            f"{list(_POWER_TRACE_INTERVAL_COLUMNS)!r}, got {header!r}"
        )
    interval_trace = header_tuple == _POWER_TRACE_INTERVAL_COLUMNS
    for index, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise PrivacyAuditError(f"power_trace.csv line {index} has {len(row)} columns")
        try:
            timestamp_s = float(row[0])
            power_w = float(row[1])
        except ValueError as exc:
            raise PrivacyAuditError(
                f"power_trace.csv line {index} has a non-numeric timestamp or power value"
            ) from exc
        if not math.isfinite(timestamp_s) or not math.isfinite(power_w):
            raise PrivacyAuditError(
                f"power_trace.csv line {index} has a non-finite timestamp or power value"
            )
        if row[2] not in _POWER_SOURCES:
            raise PrivacyAuditError(
                f"unclassified power_trace.csv source at line {index}: {row[2]!r}"
            )
        if row[3] not in _POWER_RAILS:
            raise PrivacyAuditError(
                f"unclassified power_trace.csv rail at line {index}: {row[3]!r}"
            )
        if interval_trace:
            try:
                interval_start_s = float(row[4])
                interval_end_s = float(row[5])
            except ValueError as exc:
                raise PrivacyAuditError(
                    f"power_trace.csv line {index} has a non-numeric interval support edge"
                ) from exc
            if not math.isfinite(interval_start_s) or not math.isfinite(interval_end_s):
                raise PrivacyAuditError(
                    f"power_trace.csv line {index} has a non-finite interval support edge"
                )
            if interval_start_s >= interval_end_s:
                raise PrivacyAuditError(
                    f"power_trace.csv line {index} interval support must have start < end"
                )
            if interval_end_s != timestamp_s:
                raise PrivacyAuditError(
                    f"power_trace.csv line {index} interval_end_s must equal timestamp_s"
                )


def audit_private_bundle(bundle: Path) -> PrivacyAudit:
    """Audit every source artifact and return its immutable hash inventory."""

    bundle = Path(bundle)
    if not bundle.is_dir() or bundle.is_symlink():
        raise PrivacyAuditError(f"bundle must be a non-symlink directory: {bundle}")
    audited: list[AuditedFile] = []
    seen: set[str] = set()
    for path in sorted(bundle.rglob("*")):
        rel = path.relative_to(bundle).as_posix()
        if path.is_symlink():
            raise PrivacyAuditError(f"symlink is not publication-auditable: {rel}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise PrivacyAuditError(f"non-file artifact is not publication-auditable: {rel}")
        policy = _path_policy(rel)
        if policy is None:
            raise PrivacyAuditError(f"unclassified bundle path: {rel}")
        classification, operation = policy
        if rel == "config.json":
            _audit_config(path)
        elif rel == "metadata.json":
            _audit_metadata(path)
        elif rel == "summary_metrics.json":
            _audit_summary(path)
        elif rel == "events.jsonl":
            _audit_events(path)
        elif rel == "power_trace.csv":
            _audit_power_trace(path)
        audited.append(
            AuditedFile(
                path=rel,
                classification=classification,
                operation=operation,
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
            )
        )
        seen.add(rel)
    missing = sorted(_REQUIRED_CORE_PATHS - seen)
    if missing:
        raise PrivacyAuditError(f"missing required audited path(s): {', '.join(missing)}")
    counts: dict[str, int] = {}
    for item in audited:
        counts[item.classification] = counts.get(item.classification, 0) + 1
    frozen = tuple(audited)
    return PrivacyAudit(
        schema=POLICY_SCHEMA,
        source_bundle_sha256=tree_sha256(frozen),
        files=frozen,
        classification_counts=dict(sorted(counts.items())),
    )


def public_bundle_id(source_bundle_sha256: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", source_bundle_sha256):
        raise PrivacyAuditError("source bundle SHA-256 must be 64 lowercase hex characters")
    return f"public-{source_bundle_sha256[:16]}"


def _redacted(value: Any, marker: str = REDACTED_TEXT) -> Any:
    return None if value is None else marker


def _looks_absolute_path(value: str) -> bool:
    return value.startswith(("/", "~/", "\\\\")) or bool(_WINDOWS_ABSOLUTE_RE.match(value))


def _scrub_path_strings(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _scrub_path_strings(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_scrub_path_strings(inner) for inner in value]
    if isinstance(value, str) and _looks_absolute_path(value):
        return REDACTED_PATH
    return value


def _transform_config(value: dict[str, Any], public_id: str) -> dict[str, Any]:
    result = json.loads(json.dumps(value))
    if "run_id" in result:
        result["run_id"] = public_id
    model = result.get("model")
    if isinstance(model, dict) and "source" in model:
        model["source"] = _redacted(model["source"], REDACTED_PATH)
    target = result.get("hardware_target")
    if isinstance(target, dict):
        for key in ("id", "host"):
            if key in target:
                target[key] = _redacted(target[key], REDACTED_IDENTITY)
        if "notes" in target:
            target["notes"] = _redacted(target["notes"])
    workload = result.get("workload_profile")
    if isinstance(workload, dict):
        if "prompt_text" in workload:
            workload["prompt_text"] = _redacted(workload["prompt_text"], REDACTED_CONTENT)
        for key in ("dataset_ref", "suite_manifest_ref", "generator_sidecar_ref"):
            if key in workload:
                workload[key] = _redacted(workload[key], REDACTED_PATH)
    interconnect = result.get("interconnect")
    if isinstance(interconnect, dict) and "notes" in interconnect:
        interconnect["notes"] = _redacted(interconnect["notes"])
    run_metadata = result.get("run_metadata")
    if isinstance(run_metadata, dict):
        for key in ("project", "operator", "notes", "tags"):
            if key in run_metadata:
                run_metadata[key] = _redacted(run_metadata[key], REDACTED_IDENTITY)
    return _scrub_path_strings(result)


def _redacted_subtree(label: str) -> dict[str, Any]:
    return {"redacted": True, "classification": label}


def _transform_metadata(value: dict[str, Any], public_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, inner in value.items():
        if key == "run_id":
            result[key] = public_id
        elif key in _METADATA_RETAIN_KEYS:
            result[key] = _scrub_path_strings(inner)
        elif key in {"platform", "machine"}:
            result[key] = _redacted(inner, REDACTED_IDENTITY)
        else:
            result[key] = _redacted_subtree(f"metadata.{key}")
    return result


def _transform_summary(value: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(value))
    if result.get("failure_message") is not None:
        result["failure_message"] = REDACTED_TEXT
    quality = result.get("measurement_quality")
    if isinstance(quality, dict):
        remote = quality.get("remote_cleanup_failed")
        if isinstance(remote, list):
            quality["remote_cleanup_failed"] = [REDACTED_CLEANUP_PATH for _ in remote]
        if "phase_identifiability" in quality:
            quality["phase_identifiability"] = None
    for key in _SUMMARY_REDACTED_SUBTREES:
        if key in result:
            result[key] = None
    return _scrub_path_strings(result)


def _transform_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for record in records:
        transformed = dict(record)
        transformed["message"] = REDACTED_TEXT
        transformed["metadata"] = _redacted_subtree("events.metadata")
        result.append(transformed)
    return result


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(record, sort_keys=True) + "\n").encode("utf-8")
        for record in records
    )


def _write_transformed_file(source: Path, destination: Path, rel: str, operation: str, public_id: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if operation == OP_RETAIN:
        shutil.copyfile(source, destination)
        return
    if operation == OP_TRANSFORM_JSON:
        value = _load_json_object(source, rel)
        if rel == "config.json":
            transformed = _transform_config(value, public_id)
        elif rel == "metadata.json":
            transformed = _transform_metadata(value, public_id)
        elif rel == "summary_metrics.json":
            transformed = _transform_summary(value)
        else:  # pragma: no cover - policy and dispatcher are kept adjacent
            raise PrivacyAuditError(f"no JSON transformation is defined for {rel}")
        destination.write_bytes(_json_bytes(transformed))
        return
    if operation == OP_TRANSFORM_JSONL and rel == "events.jsonl":
        destination.write_bytes(_jsonl_bytes(_transform_events(_read_jsonl(source, rel))))
        return
    raise PrivacyAuditError(f"no transformation is defined for {rel}: {operation}")


def _output_entries(bundle: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(bundle.rglob("*")):
        if path.is_symlink():
            raise PrivacyAuditError(f"public output contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise PrivacyAuditError(f"public output contains a non-file artifact: {path}")
        rel = path.relative_to(bundle).as_posix()
        entries.append({"path": rel, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    return entries


def transform_public_bundle(source: Path, destination: Path) -> dict[str, Any]:
    """Write a new public projection and return its transformation manifest.

    The source tree hash is checked again after writing.  Any concurrent or
    accidental source mutation removes the incomplete destination and fails.
    """

    source = Path(source)
    destination = Path(destination)
    audit = audit_private_bundle(source)
    public_id = public_bundle_id(audit.source_bundle_sha256)
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise PrivacyAuditError(f"public bundle destination already exists: {destination}") from exc
    transformations: list[dict[str, Any]] = []
    try:
        for item in audit.files:
            output_hash: str | None = None
            output_size: int | None = None
            byte_identical = False
            if item.operation != OP_OMIT:
                output_path = destination / item.path
                _write_transformed_file(source / item.path, output_path, item.path, item.operation, public_id)
                output_hash = sha256_file(output_path)
                output_size = output_path.stat().st_size
                byte_identical = output_hash == item.sha256 and output_size == item.size_bytes
            transformations.append(
                {
                    "path": item.path,
                    "classification": item.classification,
                    "operation": item.operation,
                    "source_sha256": item.sha256,
                    "source_size_bytes": item.size_bytes,
                    "output_sha256": output_hash,
                    "output_size_bytes": output_size,
                    "byte_identical": byte_identical,
                }
            )
        post_audit = audit_private_bundle(source)
        if post_audit.source_bundle_sha256 != audit.source_bundle_sha256:
            raise PrivacyAuditError(
                "private source bundle changed during transformation; refusing output"
            )
        output_entries = _output_entries(destination)
        output_tree_hash = tree_sha256(output_entries)
        if output_tree_hash == audit.source_bundle_sha256:
            raise PrivacyAuditError("public projection unexpectedly remained byte-identical")
        public_problems = verify_public_bundle(destination, public_id)
        if public_problems:
            raise PrivacyAuditError("public projection failed privacy verification: " + "; ".join(public_problems))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return {
        "schema": TRANSFORMATION_SCHEMA,
        "privacy_policy_schema": POLICY_SCHEMA,
        "bundle_tree_identity": tree_identity_descriptor(),
        "public_bundle_id": public_id,
        "source_bundle_sha256": audit.source_bundle_sha256,
        "output_bundle_sha256": output_tree_hash,
        "byte_identical_to_private_source": False,
        "classification_counts": audit.classification_counts,
        "files": transformations,
    }


def verify_public_bundle(bundle: Path, expected_public_id: str | None = None) -> list[str]:
    """Verify that a transformed bundle contains only governed public values."""

    bundle = Path(bundle)
    problems: list[str] = []
    try:
        audit_private_bundle(bundle)
    except PrivacyAuditError as exc:
        return [str(exc)]
    try:
        config = _load_json_object(bundle / "config.json", "config.json")
        metadata = _load_json_object(bundle / "metadata.json", "metadata.json")
        summary = _load_json_object(bundle / "summary_metrics.json", "summary_metrics.json")
        events = _read_jsonl(bundle / "events.jsonl", "events.jsonl")
    except PrivacyAuditError as exc:
        return [str(exc)]
    public_id = config.get("run_id")
    if not isinstance(public_id, str) or not public_id.startswith("public-"):
        problems.append("config.run_id is not a public pseudonym")
    if expected_public_id is not None and public_id != expected_public_id:
        problems.append(f"config.run_id {public_id!r} does not match {expected_public_id!r}")
    if metadata.get("run_id") != public_id:
        problems.append("metadata.run_id does not match the public config run_id")
    provenance_problems = source_provenance_problems(
        metadata.get("source_provenance"),
        require_eligible=True,
    )
    problems.extend(
        f"metadata.source_provenance {problem}" for problem in provenance_problems
    )
    for section, keys in {
        "model": ("source",),
        "hardware_target": ("id", "host", "notes"),
        "workload_profile": ("prompt_text", "dataset_ref", "suite_manifest_ref", "generator_sidecar_ref"),
        "interconnect": ("notes",),
        "run_metadata": ("project", "operator", "notes", "tags"),
    }.items():
        value = config.get(section)
        if not isinstance(value, dict):
            continue
        for key in keys:
            if key in value and value[key] is not None and value[key] not in {
                REDACTED_TEXT,
                REDACTED_PATH,
                REDACTED_IDENTITY,
                REDACTED_CONTENT,
            }:
                problems.append(f"config.{section}.{key} is not redacted")
    for key in _METADATA_KEYS - _METADATA_RETAIN_KEYS - {"run_id", "platform", "machine"}:
        if key in metadata and metadata[key] != _redacted_subtree(f"metadata.{key}"):
            problems.append(f"metadata.{key} is not a redacted subtree")
    for key in ("platform", "machine"):
        if key in metadata and metadata[key] not in {None, REDACTED_IDENTITY}:
            problems.append(f"metadata.{key} is not identity-redacted")
    for index, event in enumerate(events, start=1):
        if event.get("message") != REDACTED_TEXT:
            problems.append(f"events.jsonl line {index} message is not redacted")
        if event.get("metadata") != _redacted_subtree("events.metadata"):
            problems.append(f"events.jsonl line {index} metadata is not redacted")
    quality = summary.get("measurement_quality")
    if isinstance(quality, dict):
        remote = quality.get("remote_cleanup_failed")
        if isinstance(remote, list) and any(item != REDACTED_CLEANUP_PATH for item in remote):
            problems.append("measurement_quality.remote_cleanup_failed contains an unredacted path")
        if "runtime_cleanup_ok" in quality and quality["runtime_cleanup_ok"] not in {True, False, None}:
            problems.append("measurement_quality.runtime_cleanup_ok is not a retained boolean/null")
    if summary.get("failure_message") not in {None, REDACTED_TEXT}:
        problems.append("summary failure_message is not redacted")
    for key in _SUMMARY_REDACTED_SUBTREES:
        if summary.get(key) is not None:
            problems.append(f"summary {key} derived/open subtree is not omitted")
    if isinstance(quality, dict) and quality.get("phase_identifiability") is not None:
        problems.append("measurement_quality.phase_identifiability is not omitted")
    for path in bundle.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line in text.splitlines():
            for token in re.findall(r"(?:^|[\s\"'])((?:/|~/|[A-Za-z]:[\\/])[^\s\"']+)", line):
                if token not in {REDACTED_PATH, REDACTED_CLEANUP_PATH}:
                    problems.append(f"{path.relative_to(bundle).as_posix()} contains an absolute path")
                    break
    return problems
