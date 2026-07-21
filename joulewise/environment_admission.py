"""Closed, version-independent environment-admission evidence validation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def environment_admission_refusals(admission: Any) -> tuple[str, ...]:
    """Validate ledger order and bind its final attempt to the decision."""

    if not isinstance(admission, Mapping):
        return ("environment_admission_missing",)
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
        return ("environment_admission_missing",)
    clean = decision == "admitted" and claim_reason is None and admitted
    refused = (
        decision in {"flagged", "abort"}
        and claim_reason == "environment_admission_failed"
        and not admitted
    )
    if not clean and not refused:
        return ("environment_admission_failed",)
    reasons: list[str] = []
    if final.get("cpu_admission_enforced") is not True:
        reasons.append("cpu_admission_unenforced")
    if cpu.get("admitted") is not True or refused:
        reasons.append("environment_admission_failed")
    return tuple(sorted(set(reasons)))
