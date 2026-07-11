"""Validated manifest, bundle, floor, and evidence inputs for P2-037.

The module deliberately isolates every concurrently moving interface:

* strict validation is injected from :func:`joulewise.cli.validate_bundle`;
* reducer evidence is read through :func:`window_evidence_precheck`;
* P2-039 exact floor rows are bound to declared bundle/config identities; and
* campaign cooldown evidence is independently hash-verified per member.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

from joulewise.analysis_manifest import validate_analysis_manifest
from joulewise.bundle_read import BundleReader
from joulewise.detection_floor import (
    TRANSPORT_RULE_ID,
    transport_refusal_reasons,
    validate_floor_artifact,
)
from joulewise.schemas import BenchmarkConfig, SchemaError

from .claims import REDUCER_REASON_CODES, ordered_reason_codes


StrictValidator = Callable[[Path, bool], list[str]]
CAMPAIGN_PROVENANCE_SCHEMA = "joulewise.campaign_provenance.v1"
GOVERNED_IDLE_VARIANCE_METHOD = "newey_west_bartlett_10s_iid_floor_v1"
GOVERNED_IDLE_VARIANCE_REDUCER = "0.4.1"


def _governed_idle_variance_reducer(value: object) -> bool:
    """Accept the 0.4.1 wire and additive 0.4.x successors only."""

    if not isinstance(value, str):
        return False
    match = re.fullmatch(r"0\.4\.(\d+)", value)
    return match is not None and int(match.group(1)) >= 1


class AnalysisInputError(ValueError):
    """Invalid process input: CLI exits 2 and writes no artifact."""


@dataclass(frozen=True)
class FloorRequest:
    backend: str
    metric: str
    window_class: str
    condition_family_id: str
    condition_family_sha256: str
    stack_identity_sha256: str
    consumer_stress: Mapping[str, Any]


@dataclass(frozen=True)
class FloorResolution:
    status: str
    artifact_id: str
    artifact_sha256: str
    source_cell_ids: tuple[str, ...]
    transport_group_id: str | None
    transport_rule_id: str | None
    floor_abs_j: float | None
    floor_cmp_j: float | None
    floor_gate_j: float | None
    reason_codes: tuple[str, ...]


@dataclass
class BundleEvidence:
    entry: Mapping[str, Any]
    bundle_id: str
    relative_path: str
    path: Path
    summary: Mapping[str, Any] | None
    metadata: Mapping[str, Any] | None
    raw_config: Mapping[str, Any] | None
    strict_problems: tuple[str, ...]
    base_reason_codes: tuple[str, ...]
    config_sha256: str | None
    summary_sha256: str | None
    replacement_classification: str
    inclusion_status: str
    claim_evidence_flags: tuple[str, ...] = ()
    waiver: Mapping[str, Any] | None = None
    expected_config_sha256: str | None = None
    window_prechecks: dict[str, dict[str, Any]] = field(default_factory=dict)
    campaign_cooldown: Mapping[str, Any] | None = None

    @property
    def included(self) -> bool:
        return self.inclusion_status == "included"

    def audit_row(self) -> dict[str, Any]:
        token = token_provenance(self)
        identity = realized_scientific_identity(self.raw_config, self.metadata)
        quality = self.summary.get("measurement_quality") if isinstance(self.summary, Mapping) else None
        return {
            "bundle_id": self.bundle_id,
            "relative_path": self.relative_path,
            "entry_id": self.entry.get("entry_id"),
            "block_id": self.entry.get("block_id"),
            "cell_id": self.entry.get("cell_id"),
            "condition_id": self.entry.get("condition_id"),
            "config_sha256": self.config_sha256,
            "expected_config_sha256": self.expected_config_sha256,
            "manifest_config_sha256": self.entry.get("config_sha256"),
            "summary_sha256": self.summary_sha256,
            "strict_status": "valid" if not self.strict_problems else "invalid",
            "strict_problems": list(self.strict_problems),
            "summary_status": self.summary.get("status") if isinstance(self.summary, Mapping) else None,
            "base_reason_codes": list(self.base_reason_codes),
            "window_prechecks": {
                key: dict(value) for key, value in sorted(self.window_prechecks.items())
            },
            "cooldown_cap_hit": quality.get("cooldown_cap_hit") if isinstance(quality, Mapping) else None,
            "campaign_cooldown": (
                dict(self.campaign_cooldown)
                if isinstance(self.campaign_cooldown, Mapping)
                else None
            ),
            "idle_window_suspect": quality.get("idle_window_suspect") if isinstance(quality, Mapping) else None,
            "token_provenance": token,
            "scientific_identity": identity,
            "replacement_classification": self.replacement_classification,
            "inclusion_status": self.inclusion_status,
        }


@dataclass(frozen=True)
class LoadedAnalysisInputs:
    manifest: Mapping[str, Any]
    manifest_sha256: str
    floor_artifact: Mapping[str, Any]
    floor_sha256: str
    registered: Mapping[str, BundleEvidence]
    effective: Mapping[str, BundleEvidence]
    extra_audits: tuple[BundleEvidence, ...]
    valid_replacements: tuple[Mapping[str, Any], ...]
    unregistered_matching: tuple[Mapping[str, Any], ...]
    top_up_entry_ids: frozenset[str]


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _expected_bundle_config_sha256(value: Mapping[str, Any]) -> str | None:
    """Hash the exact D-001 bytes the bundle writer derives from a config.

    The frozen analysis manifest hashes the hand-authored/generated source
    config bytes.  ``RunBundleWriter`` deliberately writes the validated,
    sorted-key representation instead, so comparing a bundle directly to the
    manifest's source-file hash would reject every legitimate run.  This
    derivation binds the bundle bytes to that manifest-validated source while
    still rejecting byte-level reserialization or coordinated metadata edits.
    """

    try:
        normalized = BenchmarkConfig.from_mapping(value).to_dict()
        rendered = (
            json.dumps(normalized, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    except (SchemaError, TypeError, ValueError):
        return None
    return hashlib.sha256(rendered).hexdigest()


def _load_json_object(path: Path, label: str) -> tuple[Mapping[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AnalysisInputError(f"cannot read {label} {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalysisInputError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise AnalysisInputError(f"{label} top level must be an object")
    return value, raw


def load_manifest(path: Path) -> tuple[Mapping[str, Any], str]:
    value, raw = _load_json_object(path, "analysis manifest")
    errors = validate_analysis_manifest(value, manifest_dir=path.parent)
    if errors:
        raise AnalysisInputError("invalid analysis manifest: " + "; ".join(errors))
    return value, hashlib.sha256(raw).hexdigest()


def load_floor_artifact(path: Path) -> tuple[Mapping[str, Any], str]:
    value, raw = _load_json_object(path, "floor artifact")
    errors = validate_floor_artifact(value)
    if errors:
        raise AnalysisInputError("invalid floor artifact: " + "; ".join(errors))
    return value, hashlib.sha256(raw).hexdigest()


def _verified_cooldown_raw_artifact(
    cooldown: Mapping[str, Any], manifest_dir: Path
) -> Mapping[str, Any] | None:
    """Return a path-independent descriptor only after rechecking raw bytes."""

    descriptor = cooldown.get("raw_artifact")
    if not isinstance(descriptor, Mapping):
        return None
    path_text = descriptor.get("path")
    expected_sha = descriptor.get("sha256")
    expected_records = descriptor.get("records")
    if (
        not isinstance(path_text, str)
        or not path_text
        or Path(path_text).is_absolute()
        or Path(path_text).name == path_text
        or ".." in Path(path_text).parts
        or not isinstance(expected_sha, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha) is None
        or isinstance(expected_records, bool)
        or not isinstance(expected_records, int)
        or expected_records <= 0
    ):
        return None
    try:
        root = manifest_dir.resolve()
        raw_path = (manifest_dir / path_text).resolve()
        raw_path.relative_to(root)
        payload = raw_path.read_bytes()
    except (OSError, RuntimeError, ValueError):
        return None
    if hashlib.sha256(payload).hexdigest() != expected_sha:
        return None
    try:
        rows = [json.loads(line) for line in payload.decode("utf-8").splitlines()]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if len(rows) != expected_records or not all(isinstance(row, Mapping) for row in rows):
        return None
    return {
        "path": path_text,
        "sha256": expected_sha,
        "records": expected_records,
    }


def _campaign_cooldown_evidence(
    runs_root: Path, manifest_id: str
) -> dict[str, Mapping[str, Any]]:
    """Recover only independently verified per-member campaign provenance."""

    manifest_dir = runs_root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return {}
    candidates: dict[str, list[Mapping[str, Any]]] = {}
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            not isinstance(raw, Mapping)
            or raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA
            or raw.get("analysis_manifest_id") != manifest_id
            or not isinstance(raw.get("members"), list)
        ):
            continue
        session_id = raw.get("session_id")
        first_run_id = raw.get("first_physical_run_id")
        accepted_first_exemption = False
        for member in raw["members"]:
            if not isinstance(member, Mapping) or member.get("execution") != "invoked":
                continue
            member_run_id = member.get("run_id")
            bundle_ids = member.get("bundle_ids")
            cooldown = member.get("preceding_campaign_cooldown")
            if (
                not isinstance(member_run_id, str)
                or not member_run_id
                or not isinstance(bundle_ids, list)
                or not bundle_ids
                or any(not isinstance(bundle_id, str) or not bundle_id for bundle_id in bundle_ids)
                or not isinstance(cooldown, Mapping)
            ):
                continue
            ids_match_member = all(
                bundle_id == member_run_id
                or (
                    bundle_id.startswith(f"{member_run_id}__r")
                    and bundle_id[len(f"{member_run_id}__r") :].isdigit()
                )
                for bundle_id in bundle_ids
            )
            result = cooldown.get("result")
            verified = False
            raw_artifact: Mapping[str, Any] | None = None
            if result == "first_run_exempt":
                verified = bool(
                    not accepted_first_exemption
                    and isinstance(session_id, str)
                    and session_id
                    and cooldown.get("session_id") == session_id
                    and first_run_id == member_run_id
                    and cooldown.get("following_run_id") == first_run_id
                    and ids_match_member
                )
                accepted_first_exemption = accepted_first_exemption or verified
            elif result in {"recovered", "cap_hit"}:
                raw_artifact = _verified_cooldown_raw_artifact(cooldown, manifest_dir)
                verified = bool(
                    raw_artifact is not None
                    and isinstance(session_id, str)
                    and session_id
                    and cooldown.get("session_id") == session_id
                    and cooldown.get("following_run_id") == member_run_id
                    and ids_match_member
                )
            normalized = {
                "result": result if isinstance(result, str) else "unknown",
                "verified": verified,
                "session_id": session_id if isinstance(session_id, str) else None,
                "manifest": f"campaign_manifests/{path.name}",
                "raw_artifact": dict(raw_artifact) if raw_artifact is not None else None,
            }
            for bundle_id in bundle_ids:
                candidates.setdefault(bundle_id, []).append(normalized)

    resolved: dict[str, Mapping[str, Any]] = {}
    for bundle_id, rows in candidates.items():
        canonical = {
            json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
        }
        if len(canonical) == 1:
            resolved[bundle_id] = rows[0]
        else:
            resolved[bundle_id] = {
                "result": "unknown",
                "verified": False,
                "session_id": None,
                "manifest": None,
                "raw_artifact": None,
            }
    return resolved


def _campaign_claim_records(
    runs_root: Path, manifest_id: str
) -> dict[str, tuple[str, ...]]:
    """Read runner-recorded cleanup flags for fail-closed comparison.

    Waivers remain campaign-level audit context and are intentionally ignored
    here. The analysis engine re-derives cleanup flags from immutable bundle
    evidence; malformed provenance is a process-input error, and disagreement
    with the recorded cleanup subset fails closed downstream.
    """

    manifest_dir = runs_root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return {}
    result: dict[str, tuple[str, ...]] = {}
    cleanup_scopes = {"runtime_cleanup_ok", "remote_cleanup_failed"}
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            not isinstance(raw, Mapping)
            or raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA
            or raw.get("analysis_manifest_id") != manifest_id
            or not isinstance(raw.get("members"), list)
        ):
            continue
        for member in raw["members"]:
            if not isinstance(member, Mapping):
                continue
            run_id = member.get("run_id")
            bundle_ids = member.get("bundle_ids")
            claim_evidence = member.get("claim_evidence")
            if (
                not isinstance(run_id, str)
                or not run_id
                or not isinstance(bundle_ids, list)
                or not isinstance(claim_evidence, list)
            ):
                continue
            valid_bundle_ids = {
                bundle_id
                for bundle_id in bundle_ids
                if isinstance(bundle_id, str)
                and (
                    bundle_id == run_id
                    or (
                        bundle_id.startswith(f"{run_id}__r")
                        and bundle_id[len(f"{run_id}__r") :].isdigit()
                    )
                )
            }
            for row in claim_evidence:
                if not isinstance(row, Mapping):
                    continue
                bundle_id = row.get("bundle_id")
                flags = row.get("claim_evidence_flags")
                try:
                    if not isinstance(bundle_id, str) or not bundle_id:
                        raise TypeError("bundle_id must be a non-empty string")
                    if not isinstance(flags, list) or any(
                        not isinstance(flag, str) or not flag for flag in flags
                    ):
                        raise TypeError(
                            "claim_evidence_flags must contain only non-empty strings"
                        )
                    recorded_cleanup = cleanup_scopes.intersection(flags)
                except TypeError as exc:
                    raise AnalysisInputError(
                        f"malformed campaign claim evidence in {path.name}: {exc}"
                    ) from exc
                if bundle_id not in valid_bundle_ids:
                    continue
                result[bundle_id] = tuple(sorted(recorded_cleanup))
    return result


def _safe_relative(path: Path, root: Path) -> str:
    if path.is_symlink():
        raise AnalysisInputError(f"bundle path must not be a symlink: {path}")
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise AnalysisInputError(f"bundle path escapes runs root: {path}") from exc
    parsed = PurePosixPath(relative)
    if parsed.is_absolute() or ".." in parsed.parts or not relative:
        raise AnalysisInputError(f"invalid bundle relative path: {relative!r}")
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError) as exc:
        raise AnalysisInputError(
            f"bundle path_resolution_refused: {path}"
        ) from exc
    except ValueError as exc:
        raise AnalysisInputError(f"bundle path escapes runs root: {path}") from exc
    return relative


def _typed_config(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    try:
        return BenchmarkConfig.from_mapping(value).to_dict()
    except (SchemaError, TypeError, ValueError):
        return None


def realized_scientific_identity(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    """Return the realized cross-block identity required by B2.

    Collection-varying values (run ID, prompt hash, emitted tokens, stop
    reason, environment load) are deliberately excluded.  Model artifact,
    tokenizer, runtime/telemetry boundary, model, and quantization identities
    must remain exact within a frozen model cohort.
    """

    if not isinstance(raw_config, Mapping) or not isinstance(metadata, Mapping):
        return None
    workload = metadata.get("workload_provenance")
    adapters = metadata.get("adapters")
    runtime = adapters.get("runtime") if isinstance(adapters, Mapping) else None
    telemetry = adapters.get("telemetry") if isinstance(adapters, Mapping) else None
    runtime_prepare = runtime.get("prepare_metadata") if isinstance(runtime, Mapping) else None
    workload_model = workload.get("model") if isinstance(workload, Mapping) else None
    artifact = workload_model.get("artifact_identity") if isinstance(workload_model, Mapping) else None
    tokenizer = workload.get("tokenizer") if isinstance(workload, Mapping) else None
    device = metadata.get("device")
    model = metadata.get("model")
    quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            workload,
            runtime,
            telemetry,
            runtime_prepare,
            workload_model,
            artifact,
            tokenizer,
            device,
            model,
            quantization,
        )
    ):
        return None
    assert isinstance(artifact, Mapping)
    artifact_sha = artifact.get("sha256")
    if (
        artifact.get("status") != "ok"
        or not isinstance(artifact_sha, str)
        or re.fullmatch(r"[0-9a-f]{64}", artifact_sha) is None
    ):
        return None
    required_tokenizer = ("backend", "identifier", "revision", "class", "vocab_size")
    if any(key not in tokenizer for key in required_tokenizer) or any(
        tokenizer.get(key) is None for key in ("backend", "identifier", "class")
    ):
        return None
    return {
        "model_artifact": {
            "kind": artifact.get("kind"),
            "algorithm": artifact.get("algorithm"),
            "sha256": artifact_sha,
        },
        "tokenizer": {key: tokenizer.get(key) for key in required_tokenizer},
        "runtime": {
            "name": runtime.get("name"),
            "adapter": runtime_prepare.get("adapter"),
            "version": runtime_prepare.get("version"),
        },
        "telemetry": {"name": telemetry.get("name")},
        "device_boundary": {
            "device": device.get("device"),
            "telemetry": device.get("telemetry"),
            "rail_manifest": device.get("rail_manifest"),
            "boundary": device.get("boundary"),
        },
        "model": dict(model),
        "quantization": dict(quantization),
    }


def _realized_identity_matches_config(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> bool:
    identity = realized_scientific_identity(raw_config, metadata)
    typed = _typed_config(raw_config) if isinstance(raw_config, Mapping) else None
    if identity is None or typed is None or not isinstance(metadata, Mapping):
        return False
    hardware = typed.get("hardware_target")
    workload_config = typed.get("workload_profile")
    workload = metadata.get("workload_provenance")
    output_policy = workload.get("output_policy") if isinstance(workload, Mapping) else None
    connection = metadata.get("connection")
    expected_model = typed.get("model")
    expected_quantization = typed.get("quantization")
    observed_model = metadata.get("model")
    observed_quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            hardware,
            workload_config,
            output_policy,
            connection,
            expected_model,
            expected_quantization,
            observed_model,
            observed_quantization,
        )
    ):
        return False
    return bool(
        identity["runtime"]["name"] == hardware.get("runtime_backend")
        and identity["telemetry"]["name"] == hardware.get("telemetry_backend")
        and identity["device_boundary"]["device"] == hardware.get("id")
        and identity["device_boundary"]["telemetry"] == hardware.get("telemetry_backend")
        and connection.get("transport") == hardware.get("transport")
        and dict(observed_model) == dict(expected_model)
        and dict(observed_quantization) == dict(expected_quantization)
        and output_policy.get("requested_tokens") == workload_config.get("output_tokens")
    )


def _exclude_evidence(evidence: BundleEvidence, reason: str) -> None:
    evidence.base_reason_codes = tuple(
        ordered_reason_codes((*evidence.base_reason_codes, reason))
    )
    evidence.inclusion_status = "excluded"


def cleanup_claim_evidence_flags(summary: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Return exact suspect-cleanup field names from reducer quality evidence."""

    quality = (
        summary.get("measurement_quality")
        if isinstance(summary, Mapping)
        else None
    )
    if not isinstance(quality, Mapping):
        return ()
    flags: list[str] = []
    if quality.get("runtime_cleanup_ok") is False:
        flags.append("runtime_cleanup_ok")
    remote = quality.get("remote_cleanup_failed")
    if isinstance(remote, list) and remote:
        flags.append("remote_cleanup_failed")
    return tuple(flags)


def _apply_cleanup_claim_policy(
    evidence: BundleEvidence, recorded_flags: Sequence[str] | None
) -> None:
    flags = cleanup_claim_evidence_flags(evidence.summary)
    evidence.claim_evidence_flags = flags
    if flags or (
        recorded_flags is not None and set(recorded_flags) != set(flags)
    ):
        # Cleanup contamination is an unquantified required error term.  Reuse
        # the frozen engine vocabulary rather than inventing a cleanup reason.
        _exclude_evidence(evidence, "required_error_term_unknown")


def _replacement_tags(raw_config: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    metadata = raw_config.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return [], []
    targets = [tag.split("=", 1)[1] for tag in tags if tag.startswith("analysis-replacement-of=")]
    reasons = [tag.split("=", 1)[1] for tag in tags if tag.startswith("analysis-replacement-reason=")]
    return targets, reasons


def scientific_config_identity(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Closed-set scientific identity, excluding run/rep collection labels."""

    typed = _typed_config(value)
    if typed is None:
        return None
    result = copy.deepcopy(dict(typed))
    result.pop("run_id", None)
    metadata = result.get("run_metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("tags"), list):
        metadata["tags"] = [
            tag
            for tag in metadata["tags"]
            if not tag.startswith("analysis-replacement-of=")
            and not tag.startswith("analysis-replacement-reason=")
            and re.fullmatch(r"rep[0-9]+", tag) is None
        ]
        result["run_metadata"] = {"tags": metadata["tags"]}
    return result


def replacement_config_identity(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """B11 identity: remove only run ID and the two replacement tags.

    Unlike the broader closed-set scan identity, this retains the registered
    ``repN`` slot tag and every other normalized config field.  A candidate
    cannot claim to fill one slot while silently changing its repetition tag.
    """

    typed = _typed_config(value)
    if typed is None:
        return None
    result = copy.deepcopy(dict(typed))
    result.pop("run_id", None)
    metadata = result.get("run_metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("tags"), list):
        metadata["tags"] = [
            tag
            for tag in metadata["tags"]
            if not tag.startswith("analysis-replacement-of=")
            and not tag.startswith("analysis-replacement-reason=")
        ]
    return result


def _read_bundle(
    entry: Mapping[str, Any],
    path: Path,
    runs_root: Path,
    source_config: Mapping[str, Any],
    strict_validator: StrictValidator,
    *,
    replacement_classification: str = "registered",
    allow_replacement_tags: bool = False,
) -> BundleEvidence:
    relative = _safe_relative(path, runs_root)
    if not path.is_dir():
        return BundleEvidence(
            entry=entry,
            bundle_id=path.name,
            relative_path=relative,
            path=path,
            summary=None,
            metadata=None,
            raw_config=None,
            strict_problems=("bundle directory is missing",),
            base_reason_codes=("bundle_missing",),
            config_sha256=None,
            expected_config_sha256=None,
            summary_sha256=None,
            replacement_classification=replacement_classification,
            inclusion_status="excluded",
        )

    try:
        strict_problems = tuple(strict_validator(path, True))
    except Exception as exc:  # shared validator failures are input failures, never passes
        strict_problems = (f"strict validation raised {type(exc).__name__}: {exc}",)
    reader = BundleReader(path)
    raw_config = reader.raw_config()
    summary = reader.raw_summary()
    metadata = reader.raw_metadata()
    config_sha256 = _sha256_file(path / "config.json")
    expected_config_sha256 = (
        None if allow_replacement_tags else _expected_bundle_config_sha256(source_config)
    )
    reasons: list[str] = []
    if strict_problems:
        reasons.append("bundle_strict_invalid")
    expected = replacement_config_identity(source_config) if allow_replacement_tags else _typed_config(source_config)
    observed = replacement_config_identity(raw_config) if allow_replacement_tags and isinstance(raw_config, Mapping) else (
        _typed_config(raw_config) if isinstance(raw_config, Mapping) else None
    )
    if expected is None or observed is None or expected != observed:
        reasons.append("config_hash_mismatch")
    if not _realized_identity_matches_config(raw_config, metadata):
        reasons.append("config_hash_mismatch")
    if (
        not allow_replacement_tags
        and (
            expected_config_sha256 is None
            or config_sha256 != expected_config_sha256
        )
    ):
        reasons.append("config_hash_mismatch")
    if not isinstance(summary, Mapping) or summary.get("status") != "succeeded":
        reasons.append("bundle_status_not_succeeded")
    inclusion = "included" if not reasons else "excluded"
    return BundleEvidence(
        entry=entry,
        bundle_id=path.name,
        relative_path=relative,
        path=path,
        summary=summary,
        metadata=metadata,
        raw_config=raw_config,
        strict_problems=strict_problems,
        base_reason_codes=tuple(ordered_reason_codes(reasons)),
        config_sha256=config_sha256,
        expected_config_sha256=expected_config_sha256,
        summary_sha256=_sha256_file(path / "summary_metrics.json"),
        replacement_classification=replacement_classification,
        inclusion_status=inclusion,
    )


def _enforce_registered_realized_identity(
    manifest: Mapping[str, Any],
    registered: Mapping[str, BundleEvidence],
) -> dict[str, Mapping[str, Any]]:
    """Fail the whole realized model cohort closed on identity disagreement."""

    by_model: dict[str, list[BundleEvidence]] = {}
    model_by_entry = {
        entry["entry_id"]: entry["model_tag"] for entry in manifest["entries"]
    }
    for entry_id, evidence in registered.items():
        if evidence.raw_config is not None and evidence.metadata is not None:
            by_model.setdefault(model_by_entry[entry_id], []).append(evidence)
    result: dict[str, Mapping[str, Any]] = {}
    for model_tag, evidence_rows in by_model.items():
        identities = [
            realized_scientific_identity(row.raw_config, row.metadata)
            for row in evidence_rows
        ]
        if any(identity is None for identity in identities):
            for row, identity in zip(evidence_rows, identities):
                if identity is None:
                    _exclude_evidence(row, "config_hash_mismatch")
            identities = [identity for identity in identities if identity is not None]
        canonical = {
            json.dumps(identity, sort_keys=True, separators=(",", ":"))
            for identity in identities
            if identity is not None
        }
        if len(canonical) > 1:
            for row in evidence_rows:
                _exclude_evidence(row, "config_hash_mismatch")
            continue
        if identities:
            assert identities[0] is not None
            result[model_tag] = identities[0]
    return result


def _scan_replacements_and_topups(
    manifest: Mapping[str, Any],
    manifest_dir: Path,
    runs_root: Path,
    strict_validator: StrictValidator,
    registered: Mapping[str, BundleEvidence],
    cohort_identities: Mapping[str, Mapping[str, Any]],
    cleanup_records: Mapping[str, Sequence[str]],
) -> tuple[
    dict[str, BundleEvidence],
    list[BundleEvidence],
    list[Mapping[str, Any]],
    list[Mapping[str, Any]],
    set[str],
]:
    entries = {entry["entry_id"]: entry for entry in manifest["entries"]}
    identities: dict[str, Mapping[str, Any]] = {}
    source_configs: dict[str, Mapping[str, Any]] = {}
    for entry_id, entry in entries.items():
        source, _ = _load_json_object(manifest_dir / entry["config"], "manifest config")
        source_configs[entry_id] = source
        identity = scientific_config_identity(source)
        if identity is None:
            raise AnalysisInputError(f"manifest config for {entry_id} cannot be normalized")
        identities[entry_id] = identity

    try:
        registered_paths = {e.path.resolve() for e in registered.values()}
    except (OSError, RuntimeError) as exc:
        raise AnalysisInputError("bundle path_resolution_refused during closed-set scan") from exc
    candidates: dict[str, list[BundleEvidence]] = {}
    extras: list[BundleEvidence] = []
    unmatched_rows: list[Mapping[str, Any]] = []
    top_up_entry_ids: set[str] = set()
    if not runs_root.is_dir():
        return dict(registered), extras, [], unmatched_rows, top_up_entry_ids

    for path in sorted((item for item in runs_root.iterdir() if item.is_dir()), key=lambda p: p.name):
        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError) as exc:
            raise AnalysisInputError(
                f"bundle path_resolution_refused during closed-set scan: {path}"
            ) from exc
        if resolved_path in registered_paths or not (path / "config.json").is_file():
            continue
        try:
            raw = json.loads((path / "config.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(raw, Mapping):
            continue
        identity = scientific_config_identity(raw)
        if identity is None:
            continue
        matching_entry_ids = sorted(entry_id for entry_id, expected in identities.items() if expected == identity)
        if not matching_entry_ids:
            continue
        targets, reasons = _replacement_tags(raw)
        target_entry_id = targets[0] if len(targets) == 1 else matching_entry_ids[0]
        entry = entries.get(target_entry_id) or entries[matching_entry_ids[0]]
        evidence = _read_bundle(
            entry,
            path,
            runs_root,
            source_configs[entry["entry_id"]],
            strict_validator,
            replacement_classification="replacement_candidate",
            allow_replacement_tags=True,
        )
        _apply_cleanup_claim_policy(evidence, cleanup_records.get(evidence.bundle_id))
        cohort_identity = cohort_identities.get(entry["model_tag"])
        if (
            cohort_identity is not None
            and realized_scientific_identity(evidence.raw_config, evidence.metadata)
            != cohort_identity
        ):
            _exclude_evidence(evidence, "config_hash_mismatch")
        extras.append(evidence)
        valid_tag_shape = (
            len(targets) == 1
            and len(reasons) == 1
            and targets[0] in entries
            and reasons[0]
            in manifest["design"]["sampling_plan"]["allowed_replacement_reasons"]
            and replacement_config_identity(source_configs[targets[0]])
            == replacement_config_identity(raw)
        )
        original = registered.get(targets[0]) if targets else None
        original_invalid = original is not None and not original.included
        if valid_tag_shape and original_invalid and evidence.included:
            candidates.setdefault(targets[0], []).append(evidence)
            continue
        for matched in matching_entry_ids:
            top_up_entry_ids.add(matched)
        unmatched_rows.append(
            {
                "bundle_id": path.name,
                "relative_path": evidence.relative_path,
                "matching_entry_ids": matching_entry_ids,
                "classification": "unregistered_matching_top_up",
            }
        )

    effective = dict(registered)
    valid_replacements: list[Mapping[str, Any]] = []
    for entry_id, values in sorted(candidates.items()):
        if len(values) != 1:
            top_up_entry_ids.add(entry_id)
            for evidence in values:
                unmatched_rows.append(
                    {
                        "bundle_id": evidence.bundle_id,
                        "relative_path": evidence.relative_path,
                        "matching_entry_ids": [entry_id],
                        "classification": "multiple_successful_replacements_top_up",
                    }
                )
            continue
        replacement = values[0]
        replacement.replacement_classification = "valid_replacement"
        effective[entry_id] = replacement
        valid_replacements.append(
            {
                "entry_id": entry_id,
                "original_bundle_id": registered[entry_id].bundle_id,
                "replacement_bundle_id": replacement.bundle_id,
                "relative_path": replacement.relative_path,
            }
        )
    return effective, extras, valid_replacements, unmatched_rows, top_up_entry_ids


def load_analysis_inputs(
    analysis_manifest_path: Path,
    runs_root: Path,
    floor_artifact_path: Path,
    *,
    strict_validator: StrictValidator,
) -> LoadedAnalysisInputs:
    manifest, manifest_sha = load_manifest(Path(analysis_manifest_path))
    floor_artifact, floor_sha = load_floor_artifact(Path(floor_artifact_path))
    runs_root = Path(runs_root)
    cleanup_records = _campaign_claim_records(
        runs_root, str(manifest["manifest_id"])
    )
    registered: dict[str, BundleEvidence] = {}
    for entry in manifest["entries"]:
        run_id = entry["run_id"]
        if (
            not isinstance(run_id, str)
            or "\\" in run_id
            or PurePosixPath(run_id).name != run_id
        ):
            raise AnalysisInputError(f"manifest run_id is not a safe basename: {run_id!r}")
        source_config, _ = _load_json_object(
            Path(analysis_manifest_path).parent / entry["config"], "manifest config"
        )
        registered[entry["entry_id"]] = _read_bundle(
            entry,
            runs_root / run_id,
            runs_root,
            source_config,
            strict_validator,
        )
        _apply_cleanup_claim_policy(
            registered[entry["entry_id"]], cleanup_records.get(run_id)
        )
    cohort_identities = _enforce_registered_realized_identity(manifest, registered)
    effective, extras, replacements, unregistered, top_up_ids = _scan_replacements_and_topups(
        manifest,
        Path(analysis_manifest_path).parent,
        runs_root,
        strict_validator,
        registered,
        cohort_identities,
        cleanup_records,
    )
    cooldown_by_bundle = _campaign_cooldown_evidence(
        runs_root, str(manifest["manifest_id"])
    )
    for evidence in (*registered.values(), *extras):
        evidence.campaign_cooldown = cooldown_by_bundle.get(evidence.bundle_id)
    return LoadedAnalysisInputs(
        manifest=manifest,
        manifest_sha256=manifest_sha,
        floor_artifact=floor_artifact,
        floor_sha256=floor_sha,
        registered=registered,
        effective=effective,
        extra_audits=tuple(extras),
        valid_replacements=tuple(replacements),
        unregistered_matching=tuple(unregistered),
        top_up_entry_ids=frozenset(top_up_ids),
    )


def metric_value(summary: Mapping[str, Any], metric: Mapping[str, Any]) -> float | None:
    name = metric.get("name")
    value: Any
    if isinstance(name, str) and name.startswith("phase_energy_j."):
        phase = name.split(".", 1)[1]
        phase_values = summary.get("phase_energy_j")
        value = phase_values.get(phase) if isinstance(phase_values, Mapping) else None
    else:
        value = summary.get(name) if isinstance(name, str) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _precheck_path(metric: Mapping[str, Any]) -> tuple[str, str | None]:
    name = metric.get("name")
    if name == "gross_energy_j":
        return "gross_request", None
    if name == "energy_request_j":
        return "idle_subtracted_request", None
    if isinstance(name, str) and name.startswith("phase_energy_j."):
        return "phase", name.split(".", 1)[1]
    return "", None


def window_evidence_precheck(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> dict[str, Any]:
    """Return one canonical metric precheck; legacy current-era input fails."""

    metric_tag = str(metric.get("metric_tag", "unknown"))
    if metric_tag in evidence.window_prechecks:
        return evidence.window_prechecks[metric_tag]
    summary = evidence.summary
    root: Any = summary.get("window_evidence_precheck") if isinstance(summary, Mapping) else None
    source_field = "window_evidence_precheck"
    legacy_root = summary.get("claim_eligibility") if isinstance(summary, Mapping) else None
    legacy = not isinstance(root, Mapping) and isinstance(legacy_root, Mapping)
    if legacy:
        root = legacy_root
        source_field = "claim_eligibility"
    key, child = _precheck_path(metric)
    candidate = root.get(key) if isinstance(root, Mapping) and key else None
    if child is not None:
        candidate = candidate.get(child) if isinstance(candidate, Mapping) else None
    reasons: list[str] = []
    eligible = False
    if not isinstance(candidate, Mapping):
        reasons.append("window_evidence_precheck_missing")
    else:
        raw_reasons = candidate.get("reasons")
        if not isinstance(raw_reasons, list) or any(not isinstance(item, str) for item in raw_reasons):
            reasons.append("window_evidence_precheck_missing")
        elif any(reason not in REDUCER_REASON_CODES for reason in raw_reasons):
            reasons.append("window_evidence_precheck_missing")
        else:
            reasons.extend(raw_reasons)
            eligible = candidate.get("eligible") is True and not raw_reasons
            if not isinstance(candidate.get("eligible"), bool):
                reasons.append("window_evidence_precheck_missing")
            elif candidate.get("eligible") is False and not raw_reasons:
                # A failed boolean without a governed reason is internally
                # incomplete evidence, never an implicit pass.
                reasons.append("window_evidence_precheck_missing")
        if legacy:
            reasons.append("window_evidence_precheck_missing")

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    summary_cooldown = quality.get("cooldown_cap_hit") if isinstance(quality, Mapping) else None
    campaign_cooldown = evidence.campaign_cooldown
    campaign_result = (
        campaign_cooldown.get("result")
        if isinstance(campaign_cooldown, Mapping)
        else None
    )
    campaign_verified = bool(
        isinstance(campaign_cooldown, Mapping)
        and campaign_cooldown.get("verified") is True
    )
    if summary_cooldown is True or campaign_result == "cap_hit":
        reasons.append("cooldown_cap_hit")
    if not (
        campaign_verified
        and campaign_result in {"recovered", "first_run_exempt", "cap_hit"}
    ):
        # ``cooldown_cap_hit=false`` is only a local summary fact.  It is not
        # proof of the campaign-level gate that preceded this physical run.
        reasons.append("campaign_cooldown_evidence_missing")
    if metric.get("name") == "energy_request_j":
        suspect = quality.get("idle_window_suspect") if isinstance(quality, Mapping) else None
        if suspect is True:
            reasons.append("idle_window_suspect")
        elif suspect is not False:
            reasons.append("idle_window_suspect_unknown")
    result = {
        "status": "eligible" if eligible and not reasons else "ineligible",
        "eligible": eligible and not reasons,
        "reasons": ordered_reason_codes(reasons),
        "source_field": source_field if isinstance(root, Mapping) else None,
        "legacy_precheck_not_claim_evaluator": legacy,
        "evidence": dict(candidate) if isinstance(candidate, Mapping) else None,
    }
    evidence.window_prechecks[metric_tag] = result
    return result


def token_provenance_from_artifacts(
    summary: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Extract the exact reducer/engine token gate inputs from bundle artifacts."""

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    observed = metadata.get("workload_observed") if isinstance(metadata, Mapping) else None
    provenance = metadata.get("workload_provenance") if isinstance(metadata, Mapping) else None
    tokenizer = provenance.get("tokenizer") if isinstance(provenance, Mapping) else None
    policy = provenance.get("output_policy") if isinstance(provenance, Mapping) else None
    sampler = provenance.get("sampler") if isinstance(provenance, Mapping) else None
    policy_identity = (
        {
            "name": policy.get("name"),
            "requested_tokens": policy.get("requested_tokens"),
            "sampler": dict(sampler) if isinstance(sampler, Mapping) else None,
        }
        if isinstance(policy, Mapping)
        else None
    )
    return {
        "output_tokens": observed.get("output_token_count") if isinstance(observed, Mapping) else None,
        "token_count_source": quality.get("token_counts_source") if isinstance(quality, Mapping) else None,
        "stop_reason": policy.get("stop_condition") if isinstance(policy, Mapping) else None,
        # Emitted count and realized stop are observations, not frozen policy
        # identity.  Compare the requested budget, policy label, and sampler;
        # validate the realized stop separately above.
        "output_policy": policy_identity,
        "tokenizer_identity": dict(tokenizer) if isinstance(tokenizer, Mapping) else None,
    }


def token_provenance(evidence: BundleEvidence) -> dict[str, Any]:
    return token_provenance_from_artifacts(evidence.summary, evidence.metadata)


def governed_stochastic_variance(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], tuple[str, ...]]:
    """Read the frozen P2-044 scalar without recomputing raw-trace policy."""

    name = metric.get("name")
    if name != "energy_request_j":
        return (), ()
    summary = evidence.summary
    provenance = summary.get("summary_provenance") if isinstance(summary, Mapping) else None
    uncertainty = summary.get("idle_mean_uncertainty") if isinstance(summary, Mapping) else None
    variances = summary.get("energy_variance_terms_j2") if isinstance(summary, Mapping) else None
    variance = variances.get("E_idle_mean_j2") if isinstance(variances, Mapping) else None
    variance_present = (
        isinstance(variance, (int, float))
        and not isinstance(variance, bool)
        and math.isfinite(float(variance))
        and float(variance) >= 0.0
    )
    governed_evidence_present = bool(
        isinstance(provenance, Mapping)
        and _governed_idle_variance_reducer(provenance.get("reducer_version"))
        and isinstance(uncertainty, Mapping)
        and uncertainty.get("status") == "estimated"
        and uncertainty.get("method") == GOVERNED_IDLE_VARIANCE_METHOD
        and variance_present
    )
    if not governed_evidence_present:
        return (), ("required_error_term_unknown",)
    if uncertainty.get("correlation_scope") != "independent_run":
        return (), ("required_covariance_unknown",)
    return (
        (
            {
                "name": "E_idle_mean_j2",
                "variance": float(variance),
                "correlation_scope": "independent_run",
            },
        ),
        (),
    )


def deterministic_bounds(
    evidence: BundleEvidence,
    metric: Mapping[str, Any],
) -> tuple[dict[str, float], tuple[str, ...]]:
    summary = evidence.summary
    if not isinstance(summary, Mapping):
        return {}, ("required_error_term_unknown",)
    name = metric.get("name")
    result: dict[str, float] = {}
    reasons: list[str] = []
    if name in {"gross_energy_j", "energy_request_j"}:
        terms = summary.get("energy_bound_terms_j")
        interpolation = terms.get("E_interpolation_joint_edge_bound_j") if isinstance(terms, Mapping) else None
        if isinstance(interpolation, (int, float)) and not isinstance(interpolation, bool) and math.isfinite(interpolation) and interpolation >= 0:
            result["E_interpolation_joint_edge_bound_j"] = float(interpolation)
        else:
            reasons.append("interpolation_bound_unrecorded")
        if name == "energy_request_j":
            drift = terms.get("E_drift_bound_j") if isinstance(terms, Mapping) else None
            if isinstance(drift, (int, float)) and not isinstance(drift, bool) and math.isfinite(drift) and drift >= 0:
                result["E_drift_bound_j"] = float(drift)
            else:
                reasons.append("drift_term_unknown")
    elif isinstance(name, str) and name.startswith("phase_energy_j."):
        precheck = window_evidence_precheck(evidence, metric)
        raw = precheck.get("evidence")
        windows = raw.get("windows") if isinstance(raw, Mapping) else None
        if isinstance(windows, list) and windows:
            values = [window.get("interpolation_joint_edge_bound_j") for window in windows if isinstance(window, Mapping)]
            if len(values) == len(windows) and all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                and value >= 0
                for value in values
            ):
                result["E_interpolation_joint_edge_bound_j"] = float(sum(values))
            else:
                reasons.append("interpolation_bound_unrecorded")
        else:
            reasons.append("interpolation_bound_unrecorded")
    return result, tuple(ordered_reason_codes(reasons))


def _declared_exact_floor_resolution(
    artifact: Mapping[str, Any],
    artifact_sha256: str,
    contrast: Mapping[str, Any],
    condition_family_id: str,
    evidence: Sequence[BundleEvidence],
) -> FloorResolution | None:
    """Bind an exact floor cell to declared consumer bundle/config identities."""

    if not evidence:
        return None
    backends = {
        hardware.get("telemetry_backend")
        for row in evidence
        if isinstance(row.raw_config, Mapping)
        and isinstance((hardware := row.raw_config.get("hardware_target")), Mapping)
    }
    if len(backends) != 1 or not all(isinstance(value, str) and value for value in backends):
        return None
    backend = next(iter(backends))
    selector = contrast.get("floor_selector")
    if not isinstance(selector, Mapping):
        return None
    consumer_pairs = {
        (row.bundle_id, row.config_sha256)
        for row in evidence
        if isinstance(row.bundle_id, str) and isinstance(row.config_sha256, str)
    }
    if len(consumer_pairs) != len(evidence):
        return None
    matches: list[Mapping[str, Any]] = []
    for cell in artifact.get("cells", []):
        if not isinstance(cell, Mapping):
            continue
        key = cell.get("key")
        absolute = cell.get("absolute")
        observations = (
            absolute.get("bundle_observations")
            if isinstance(absolute, Mapping)
            else None
        )
        if (
            not isinstance(key, Mapping)
            or key.get("backend") != backend
            or key.get("metric") != selector.get("metric")
            or key.get("window_class") != selector.get("window_class")
            or key.get("condition_family_id") != condition_family_id
            or not isinstance(observations, list)
        ):
            continue
        source_pairs = {
            (row.get("bundle_id"), row.get("config_sha256"))
            for row in observations
            if isinstance(row, Mapping)
        }
        # LOO consumes a strict subset of the already-bound full cell.  A
        # foreign bundle/config pair can never acquire the source identity.
        if consumer_pairs and consumer_pairs.issubset(source_pairs):
            matches.append(cell)
    if not matches:
        return None
    if len(matches) != 1:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=("transport_group_incomplete",),
        )
    cell = matches[0]
    eligibility = cell.get("eligibility")
    reasons: list[str] = []
    if artifact.get("calibration_scope") == "smoke" or not isinstance(
        eligibility, Mapping
    ) or eligibility.get("status") != "claim_ready":
        reasons.append("cell_not_claim_ready")
    if selector.get("metric") == "energy_request_j":
        guard = artifact.get("idle_drift_guard")
        if not isinstance(guard, Mapping) or guard.get("calibration_status") != "calibrated":
            reasons.append("consumer_term_unknown")
    floor_values = (cell.get("floor_abs_j"), cell.get("floor_cmp_j"), cell.get("floor_gate_j"))
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
        for value in floor_values
    ):
        reasons.append("cell_not_claim_ready")
    if reasons:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(str(cell.get("cell_id", "")),),
            transport_group_id=cell.get("transport_group_id"),
            transport_rule_id=TRANSPORT_RULE_ID,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=tuple(dict.fromkeys(reasons)),
        )
    return FloorResolution(
        status="exact",
        artifact_id=str(artifact.get("artifact_id", "")),
        artifact_sha256=artifact_sha256,
        source_cell_ids=(str(cell["cell_id"]),),
        transport_group_id=cell.get("transport_group_id"),
        transport_rule_id=TRANSPORT_RULE_ID,
        floor_abs_j=float(floor_values[0]),
        floor_cmp_j=float(floor_values[1]),
        floor_gate_j=float(floor_values[2]),
        reason_codes=(),
    )


def resolve_floor(
    artifact: Mapping[str, Any],
    artifact_sha256: str,
    request: FloorRequest,
) -> FloorResolution:
    """Resolve a fully typed P2-039 request without guessing its provenance."""

    preflight_reasons: list[str] = []
    if artifact.get("calibration_scope") == "smoke":
        preflight_reasons.append("cell_not_claim_ready")
    if request.metric == "energy_request_j":
        idle_guard = artifact.get("idle_drift_guard")
        if not isinstance(idle_guard, Mapping) or idle_guard.get("calibration_status") != "calibrated":
            preflight_reasons.append("consumer_term_unknown")
    if preflight_reasons:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=tuple(dict.fromkeys(preflight_reasons)),
        )

    cells = {
        cell.get("cell_id"): cell
        for cell in artifact.get("cells", [])
        if isinstance(cell, Mapping) and isinstance(cell.get("cell_id"), str)
    }
    matching: list[Mapping[str, Any]] = []
    for group in artifact.get("transport_groups", []):
        if not isinstance(group, Mapping):
            continue
        if any(
            group.get(key) != expected
            for key, expected in (
                ("backend", request.backend),
                ("metric", request.metric),
                ("window_class", request.window_class),
                ("stack_identity_sha256", request.stack_identity_sha256),
            )
        ):
            continue
        allowed = group.get("allowed_consumer_condition_families")
        if not isinstance(allowed, list) or not any(
            isinstance(item, Mapping)
            and item.get("condition_family_id") == request.condition_family_id
            and item.get("condition_family_sha256") == request.condition_family_sha256
            for item in allowed
        ):
            continue
        matching.append(group)
    if len(matching) != 1:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=(),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=("cell_missing" if not matching else "transport_group_incomplete",),
        )
    group = matching[0]
    consumer = {
        "backend": request.backend,
        "metric": request.metric,
        "window_class": request.window_class,
        "condition_family_id": request.condition_family_id,
        "condition_family_sha256": request.condition_family_sha256,
        "stack_identity_sha256": request.stack_identity_sha256,
        **dict(request.consumer_stress),
    }
    refusals = transport_refusal_reasons(
        consumer,
        group,
        cells,
        artifact_sha256=artifact_sha256,
        expected_artifact_sha256=artifact_sha256,
        artifact_schema_valid=True,
    )
    if refusals:
        return FloorResolution(
            status="refused",
            artifact_id=str(artifact.get("artifact_id", "")),
            artifact_sha256=artifact_sha256,
            source_cell_ids=tuple(group.get("source_cell_ids") or ()),
            transport_group_id=group.get("transport_group_id"),
            transport_rule_id=group.get("rule_id"),
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=tuple(refusals),
        )
    return FloorResolution(
        status="transported",
        artifact_id=str(artifact.get("artifact_id", "")),
        artifact_sha256=artifact_sha256,
        source_cell_ids=tuple(group["source_cell_ids"]),
        transport_group_id=group["transport_group_id"],
        transport_rule_id=group.get("rule_id", TRANSPORT_RULE_ID),
        floor_abs_j=float(group["composed_floor_abs_j"]),
        floor_cmp_j=float(group["composed_floor_cmp_j"]),
        floor_gate_j=float(group["composed_floor_gate_j"]),
        reason_codes=(),
    )


def unavailable_floor_resolution(
    artifact: Mapping[str, Any], artifact_sha256: str
) -> FloorResolution:
    """Fail closed when no exact declared-input row or private seam resolves."""

    return FloorResolution(
        status="refused",
        artifact_id=str(artifact.get("artifact_id", "")),
        artifact_sha256=artifact_sha256,
        source_cell_ids=(),
        transport_group_id=None,
        transport_rule_id=None,
        floor_abs_j=None,
        floor_cmp_j=None,
        floor_gate_j=None,
        reason_codes=("consumer_term_unknown",),
    )


__all__ = [
    "AnalysisInputError",
    "BundleEvidence",
    "cleanup_claim_evidence_flags",
    "FloorRequest",
    "FloorResolution",
    "LoadedAnalysisInputs",
    "deterministic_bounds",
    "governed_stochastic_variance",
    "load_analysis_inputs",
    "load_floor_artifact",
    "load_manifest",
    "metric_value",
    "realized_scientific_identity",
    "resolve_floor",
    "replacement_config_identity",
    "scientific_config_identity",
    "token_provenance",
    "token_provenance_from_artifacts",
    "unavailable_floor_resolution",
    "window_evidence_precheck",
]
