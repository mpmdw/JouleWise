"""Closed, version-independent environment-admission evidence validation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


ADMISSION_SCHEMA = "joulewise.environment_admission.v1"
EVALUATION_SCHEMA = "joulewise.environment_evaluation.v1"


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


def environment_admission_refusals(admission: Any) -> tuple[str, ...]:
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
    for index, row in enumerate(attempts, start=1):
        if (
            not isinstance(row, Mapping)
            or isinstance(row.get("attempt"), bool)
            or row.get("attempt") != index
        ):
            return ("environment_admission_missing",)
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
