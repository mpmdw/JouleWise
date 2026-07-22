"""Claim-time pre/post powermetrics fiducial calibration bracketing.

The bracket carries a nonparametric 95/95 calibration-distribution bound into
claims only under the registered T1-T3 transfer assumptions; it does not turn
either finite sample maximum into an unconditional instrument property.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.powermetrics_fiducial import (
    CAPTURE_TIME_FIELD,
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
    capture_wall_time_from_events,
    protocol_pulse_count,
    protocol_sha256,
    verify_stored_evidence_physics,
)
from joulewise.schemas import CalibrationBracketingPolicy

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"


@dataclass(frozen=True)
class CalibrationCandidate:
    relative_path: str
    manifest_sha256: str
    evidence_sha256: str
    protocol_id: str
    capture_wall_time_s: float
    b_fiducial_s: float
    bindings: Mapping[str, Any]

    def descriptor(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "manifest_sha256": self.manifest_sha256,
            "evidence_sha256": self.evidence_sha256,
            "protocol_id": self.protocol_id,
            "capture_wall_time_s": self.capture_wall_time_s,
            "b_fiducial_s": self.b_fiducial_s,
        }


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _binding_evidence_authentic(
    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
) -> bool:
    binding_evidence = evidence.get("binding_evidence")
    binary = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    power_policy = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    # Canonical form MUST match the generation (powermetrics_fiducial) and
    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
    # unmatchable as bracket candidates).
    canonical = json.dumps(
        dict(bindings),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return bool(
        isinstance(binding_evidence, Mapping)
        and binding_evidence.get("schema_version")
        == "joulewise.instrument_binding_evidence.v1"
        and binding_evidence.get("binding_vector_sha256")
        == hashlib.sha256(canonical).hexdigest()
        and isinstance(binary, Mapping)
        and binary.get("sha256") == bindings.get("powermetrics_sha256")
        and isinstance(binary.get("path"), str)
        and bool(binary.get("path"))
        and isinstance(power_policy, Mapping)
        and power_policy.get("id") == bindings.get("power_policy")
    )


def load_calibration_candidate(
    directory: Path, *, runs_root: Path
) -> CalibrationCandidate | None:
    """Authenticate one standalone validation directory from primary bytes."""

    root = Path(runs_root).resolve()
    try:
        directory = Path(directory).resolve(strict=True)
        relative = directory.relative_to(root).as_posix()
        manifest_raw = (directory / "manifest.json").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
    if (
        not relative
        or not isinstance(artifacts, Mapping)
        or manifest.get("schema_version")
        != "joulewise.instrument_validation_manifest.v1"
    ):
        return None
    members: dict[str, bytes] = {}
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            return None
        try:
            member = (directory / name).resolve(strict=True)
            member.relative_to(directory)
            raw = member.read_bytes()
        except (OSError, ValueError):
            return None
        if not _valid_sha256(expected) or hashlib.sha256(raw).hexdigest() != expected:
            return None
        members[name] = raw
    try:
        evidence_raw = members["instrument_evidence.json"]
        events_raw = members["events.jsonl"]
        powermetrics_raw = members["raw/powermetrics.plist"]
        evidence = json.loads(evidence_raw)
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(evidence, Mapping):
        return None
    protocol_id = evidence.get("protocol_id")
    bindings = evidence.get("bindings")
    capture = evidence.get(CAPTURE_TIME_FIELD)
    if (
        protocol_id not in {PROTOCOL_V2_ID, PROTOCOL_ID}
        or evidence.get("schema_version") != "joulewise.instrument_evidence.v1"
        or manifest.get("protocol_id") != protocol_id
        or manifest.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or not isinstance(bindings, Mapping)
        or any(bindings.get(field) in (None, "") for field in V2_BINDING_FIELDS)
        or not _binding_evidence_authentic(evidence, bindings)
        or bindings.get("pulse_protocol_id") != protocol_id
        or bindings.get("protocol_sha256") != protocol_sha256(str(protocol_id))
        or evidence.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or evidence.get("anchor_method_version")
        != "powermetrics_native_second_censored_intersection_v1"
        or evidence.get("residual_region_method") != RESIDUAL_REGION_METHOD
        or not isinstance(
            evidence.get("residual_region_coverage_assumption"), str
        )
        or not evidence.get("residual_region_coverage_assumption")
        or evidence.get("residual_region_coverage_resolution_s")
        != REGION_COVERAGE_RESOLUTION_S
        or evidence.get("max_age_s") != MAX_AGE_S
        or isinstance(capture, bool)
        or not isinstance(capture, int | float)
        or not math.isfinite(float(capture))
        or float(capture) < 0.0
    ):
        return None
    artifact_hashes = evidence.get("artifact_sha256")
    if (
        not isinstance(artifact_hashes, Mapping)
        or artifact_hashes.get("events.jsonl")
        != hashlib.sha256(events_raw).hexdigest()
        or artifact_hashes.get("raw/powermetrics.plist")
        != hashlib.sha256(powermetrics_raw).hexdigest()
    ):
        return None
    try:
        authenticated_capture = capture_wall_time_from_events(events_raw)
        effective_bound = verify_stored_evidence_physics(
            evidence, powermetrics_raw, events_raw
        )
    except (KeyError, TypeError, ValueError):
        return None
    if abs(float(capture) - authenticated_capture) > 1.0:
        return None
    return CalibrationCandidate(
        relative_path=relative,
        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
        protocol_id=str(protocol_id),
        capture_wall_time_s=float(capture),
        b_fiducial_s=float(effective_bound),
        bindings=dict(bindings),
    )


def discover_calibration_candidates(runs_root: Path) -> tuple[CalibrationCandidate, ...]:
    validation_root = Path(runs_root) / "instrument_validation"
    try:
        directories = sorted(path.parent for path in validation_root.glob("*/manifest.json"))
    except OSError:
        return ()
    return tuple(
        candidate
        for directory in directories
        if (candidate := load_calibration_candidate(directory, runs_root=Path(runs_root)))
        is not None
    )


def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],
    policy: CalibrationBracketingPolicy,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Select a causal bracket and consume the larger authenticated bound."""

    result: dict[str, Any] = {
        "schema_version": BRACKET_SCHEMA,
        "policy": {
            "require_bracket": policy.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracket_max_drift_s
            ),
        },
        "window_start_s": window_start_s,
        "window_end_s": window_end_s,
        "pre": None,
        "post": None,
        "b_fiducial_s": None,
        "drift_s": None,
        "status": "not_required" if not policy.require_bracket else "failed",
    }
    if not policy.require_bracket:
        return result, ()
    if (
        not math.isfinite(window_start_s)
        or not math.isfinite(window_end_s)
        or window_start_s >= window_end_s
    ):
        return result, ("instrument_calibration_bracket_missing",)
    matching = [
        candidate
        for candidate in candidates
        if all(candidate.bindings.get(field) == bindings.get(field) for field in V2_BINDING_FIELDS)
    ]
    causal_pre = [
        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
    ]
    causal_post = [
        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
    ]
    fresh_pre = [
        candidate
        for candidate in causal_pre
        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    ]
    fresh_post = [
        candidate
        for candidate in causal_post
        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    ]
    if not fresh_pre or not fresh_post:
        reason = (
            "instrument_calibration_stale"
            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
            else "instrument_calibration_bracket_missing"
        )
        return result, (reason,)
    pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
    post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
    drift_s = abs(pre.b_fiducial_s - post.b_fiducial_s)
    result.update(
        {
            "pre": pre.descriptor(),
            "post": post.descriptor(),
            "b_fiducial_s": max(pre.b_fiducial_s, post.b_fiducial_s),
            "drift_s": drift_s,
        }
    )
    if drift_s > policy.calibration_bracket_max_drift_s:
        return result, ("instrument_calibration_mismatch",)
    result["status"] = "passed"
    return result, ()


def calibration_bracket_for_bundles(
    runs_root: Path,
    bundle_paths: Sequence[Path],
    policy: CalibrationBracketingPolicy,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Derive the collection window and binding vector from member custody."""

    if not bundle_paths:
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    windows = []
    bindings: list[Mapping[str, Any]] = []
    try:
        for path in bundle_paths:
            reader = BundleReader(path)
            window = reader.measured_window()
            metadata = reader.metadata()
            calibration = metadata.get("instrument_calibration")
            binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
            if window is None or not isinstance(binding, Mapping):
                raise ValueError("member omits calibration binding evidence")
            windows.append(window)
            bindings.append(binding)
    except (BundleReadError, OSError, TypeError, ValueError):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    expected = bindings[0]
    if any(
        any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
        for binding in bindings[1:]
    ):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=min(window.start_s for window in windows),
            window_end_s=max(window.end_s for window in windows),
            bindings=expected,
            policy=policy,
        )
        return empty, ("instrument_calibration_mismatch",)
    return evaluate_calibration_bracket(
        discover_calibration_candidates(runs_root),
        window_start_s=min(window.start_s for window in windows),
        window_end_s=max(window.end_s for window in windows),
        bindings=expected,
        policy=policy,
    )


__all__ = [
    "BRACKET_SCHEMA",
    "CalibrationCandidate",
    "calibration_bracket_for_bundles",
    "discover_calibration_candidates",
    "evaluate_calibration_bracket",
    "load_calibration_candidate",
]
