"""Closed, version-independent environment-admission evidence validation."""

from __future__ import annotations

from collections.abc import Mapping
import json
import math
from pathlib import Path
from typing import Any


ADMISSION_SCHEMA = "joulewise.environment_admission.v1"
EVALUATION_SCHEMA = "joulewise.environment_evaluation.v1"
MAX_ADMISSION_GAP_S = 600.0


def environment_observation_failure(observation: Any) -> str | None:
    """Apply the controller's display/screensaver failure predicate."""

    if not isinstance(observation, Mapping):
        return "environment guard observation is missing"
    display_state = observation.get("display_power_state")
    screensaver = observation.get("screensaver_engaged")
    if display_state == "any_awake":
        return "display became or remained awake during idle admission"
    if screensaver is True:
        return "screensaver became or remained engaged during idle admission"
    if display_state != "all_asleep":
        return "display power state is unknown during idle admission"
    if screensaver is not False:
        return "screensaver engagement state is unknown during idle admission"
    return None


def post_run_environment_refusals(metadata: Any) -> tuple[str, ...]:
    """Validate the post-run observation used by whole-window claims."""

    environment = metadata.get("environment") if isinstance(metadata, Mapping) else None
    observation = (
        environment.get("post_run_observation")
        if isinstance(environment, Mapping)
        else None
    )
    if (
        not isinstance(observation, Mapping)
        or observation.get("capture_skipped") is not False
        or not isinstance(observation.get("errors"), Mapping)
        or environment_observation_failure(observation) is not None
    ):
        return ("environment_admission_failed",)
    return ()


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _attempt_capture_interval(
    bundle_path: Path, attempt: int
) -> tuple[float, float] | None:
    """Read the producer's endpoint-stamped idle telemetry interval."""

    name = (
        "rich_telemetry_idle.jsonl"
        if attempt == 1
        else f"rich_telemetry_idle_attempt_{attempt}.jsonl"
    )
    try:
        lines = (Path(bundle_path) / name).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    starts: list[float] = []
    ends: list[float] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(row, Mapping):
            return None
        timestamp_s = _finite_number(row.get("timestamp_s"))
        elapsed_ns = row.get("elapsed_ns")
        if (
            timestamp_s is None
            or isinstance(elapsed_ns, bool)
            or not isinstance(elapsed_ns, int)
            or elapsed_ns <= 0
        ):
            # Current strict evidence must bind the capture to its stage.
            # Untimestamped legacy diagnostics remain replayable because
            # frozen consumers never dispatch to this validator.
            return None
        elapsed_s = elapsed_ns / 1_000_000_000.0
        # Powermetrics rich telemetry stamps each averaging interval at its
        # endpoint; this matches ``samples_from_records`` and the adapter's
        # committed ``[endpoint-elapsed, endpoint)`` association rule.
        starts.append(timestamp_s - elapsed_s)
        ends.append(timestamp_s)
    if not starts:
        return None
    return min(starts), max(ends)


def current_environment_refusals(
    metadata: Any,
    *,
    bundle_path: Path,
    measured_window_start_s: Any,
    measured_window_end_s: Any,
) -> tuple[str, ...]:
    """Current-mint causal and cross-field environment evidence validator.

    Callers must dispatch here only for strict 0.5.2/0.6.2 claim paths.  The
    frozen replay arms intentionally retain their committed validator surface.
    """

    admission = metadata.get("environment_admission") if isinstance(metadata, Mapping) else None
    reasons = set(
        environment_admission_refusals(admission, require_attempt_timing=True)
    )
    start_s = _finite_number(measured_window_start_s)
    end_s = _finite_number(measured_window_end_s)
    if start_s is None or end_s is None or start_s >= end_s:
        reasons.add("environment_admission_missing")
        return tuple(sorted(reasons))

    attempts = admission.get("attempts") if isinstance(admission, Mapping) else None
    if not isinstance(attempts, list) or not attempts:
        reasons.add("environment_admission_missing")
    else:
        final_end_s = _finite_number(
            attempts[-1].get("end_s") if isinstance(attempts[-1], Mapping) else None
        )
        if (
            final_end_s is None
            or final_end_s > start_s
            or start_s - final_end_s > MAX_ADMISSION_GAP_S
        ):
            reasons.add("environment_admission_missing")

        for expected_attempt, row in enumerate(attempts, start=1):
            if not isinstance(row, Mapping):
                reasons.add("environment_admission_missing")
                continue
            attempt_start_s = _finite_number(row.get("start_s"))
            attempt_end_s = _finite_number(row.get("end_s"))
            baseline = row.get("baseline")
            baseline_duration_s = (
                _finite_number(baseline.get("duration_s"))
                if isinstance(baseline, Mapping)
                else None
            )
            if (
                attempt_start_s is None
                or attempt_end_s is None
                or baseline_duration_s is None
                or baseline_duration_s <= 0.0
                or baseline_duration_s > attempt_end_s - attempt_start_s + 1e-9
            ):
                reasons.add("environment_admission_missing")
                continue
            capture = _attempt_capture_interval(bundle_path, expected_attempt)
            if capture is None or (
                capture[0] < attempt_start_s - 1e-9
                or capture[1] > attempt_end_s + 1e-9
            ):
                reasons.add("environment_admission_missing")

    environment = metadata.get("environment") if isinstance(metadata, Mapping) else None
    observation = (
        environment.get("post_run_observation")
        if isinstance(environment, Mapping)
        else None
    )
    captured_at_s = (
        _finite_number(observation.get("captured_at_s"))
        if isinstance(observation, Mapping)
        else None
    )
    if captured_at_s is None or captured_at_s < end_s:
        reasons.add("environment_admission_missing")
    reasons.update(post_run_environment_refusals(metadata))
    return tuple(sorted(reasons))


def environment_admission_refusals(
    admission: Any, *, require_attempt_timing: bool = False
) -> tuple[str, ...]:
    """Validate all claim-bearing admission evidence, failing closed."""

    if not isinstance(admission, Mapping):
        return ("environment_admission_missing",)
    reasons: set[str] = set()
    if admission.get("schema_version") != ADMISSION_SCHEMA:
        reasons.add("environment_admission_missing")
    if admission.get("critical_environment_passed") is not True:
        reasons.add("environment_admission_failed")
    if admission.get("reference_provenance_present") is not True:
        reasons.add("environment_admission_failed")
    evaluation = admission.get("per_run_environment_evaluation")
    if (
        not isinstance(evaluation, Mapping)
        or evaluation.get("schema_version") != EVALUATION_SCHEMA
        or not isinstance(evaluation.get("snapshot_sha256"), str)
        or len(evaluation.get("snapshot_sha256", "")) != 64
    ):
        reasons.add("environment_admission_missing")
    elif evaluation.get("eligible") is not True:
        reasons.add("environment_admission_failed")
    attempts = admission.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        return ("environment_admission_missing",)
    previous_end_s: float | None = None
    for index, row in enumerate(attempts, start=1):
        if (
            not isinstance(row, Mapping)
            or isinstance(row.get("attempt"), bool)
            or row.get("attempt") != index
        ):
            return ("environment_admission_missing",)
        if require_attempt_timing:
            start_s = row.get("start_s")
            end_s = row.get("end_s")
            if (
                isinstance(start_s, bool)
                or isinstance(end_s, bool)
                or not isinstance(start_s, int | float)
                or not isinstance(end_s, int | float)
                or not math.isfinite(float(start_s))
                or not math.isfinite(float(end_s))
                or float(start_s) >= float(end_s)
                or (
                    previous_end_s is not None
                    and previous_end_s > float(start_s)
                )
            ):
                return ("environment_admission_missing",)
            previous_end_s = float(end_s)
    guards = admission.get("guard_observations")
    expected_phases = [
        phase
        for index in range(1, len(attempts) + 1)
        for phase in (f"before_attempt_{index}", f"after_attempt_{index}")
    ]
    if not isinstance(guards, list) or len(guards) != len(expected_phases):
        reasons.add("environment_admission_missing")
    else:
        for guard, expected_phase in zip(guards, expected_phases, strict=True):
            if (
                not isinstance(guard, Mapping)
                or guard.get("phase") != expected_phase
                or guard.get("capture_skipped") is not False
                or not isinstance(guard.get("errors"), Mapping)
            ):
                reasons.add("environment_admission_missing")
            elif environment_observation_failure(guard) is not None:
                reasons.add("environment_admission_failed")
    final = attempts[-1]
    decision = admission.get("decision")
    claim_reason = admission.get("claim_reason")
    admitted = final.get("admitted")
    cpu = final.get("cpu_admission")
    if (
        not isinstance(admitted, bool)
        or not isinstance(cpu, Mapping)
        or not isinstance(cpu.get("admitted"), bool)
        or decision not in {"admitted", "flagged", "abort"}
    ):
        reasons.add("environment_admission_missing")
        return tuple(sorted(reasons))
    clean = decision == "admitted" and claim_reason is None and admitted
    refused = (
        decision in {"flagged", "abort"}
        and claim_reason == "environment_admission_failed"
        and not admitted
    )
    if not clean and not refused:
        reasons.add("environment_admission_failed")
    if final.get("cpu_admission_enforced") is not True:
        reasons.add("cpu_admission_unenforced")
    if cpu.get("admitted") is not True or refused:
        reasons.add("environment_admission_failed")
    return tuple(sorted(reasons))
