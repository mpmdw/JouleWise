"""Mechanical pre-arm scheduler gates for governed measurement windows.

Stages 1-2 implement the receipt contract plus G4 (reviewed-main identity) and
G5 (campaign-span boot identity).  The remaining gates are explicit
``NOT_IMPLEMENTED`` entries, so this staged evaluator cannot authorize a
window before their ruled implementations land.

Scheduler refusal codes deliberately remain separate from
``arm_readiness.READINESS_REASON_CODES``.  Admitting scheduler-only codes to an
arm receipt would make those codes legal at issuance and could then make the
arm derivation/replay equality fail closed.  G4's two identical predicates are
the only mirrored codes; their scheduler refusals name that provenance.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any



SCHEDULER_GATE_RECEIPT_SCHEMA = "joulewise.window_scheduler_gate_receipt.v2"
CAMPAIGN_BOOT_PIN_SCHEMA = "joulewise.campaign_boot_pin.v1"
CAMPAIGN_BOOT_PIN_NAME = "campaign_boot_pin.v1"
CAMPAIGN_BOOT_PIN_SIDECAR_NAME = f"{CAMPAIGN_BOOT_PIN_NAME}.sha256"
# On-disk prefix every emitted gate-receipt file MUST carry (the stage-6
# writer uses this constant); the missing-pin history predicate keys on it.
SCHEDULER_GATE_RECEIPT_FILE_PREFIX = "window_scheduler_gate_receipt"

GATE_IDS = ("G1", "G2", "G3", "G4", "G5", "G6", "G7")
# Receipt order is evaluation order.  G5 must precede monotonic-clock gates.
GATE_EVALUATION_ORDER = ("G5", "G1", "G2", "G3", "G4", "G6", "G7")
MONOTONIC_GATE_IDS = frozenset({"G1", "G2"})
WINDOW_CLASSES = frozenset({"SHAKEDOWN", "CLAIM"})
GATE_VERDICTS = frozenset(
    {"PASS", "REFUSE", "RECORD_ONLY", "NOT_EVALUATED", "NOT_IMPLEMENTED"}
)

G1_REASON_CODES = frozenset(
    {
        "scheduler_fuse_insufficient",
        "scheduler_fuse_underivable",
        "scheduler_span_undeclared",
        "scheduler_budget_unresolved",
    }
)
G2_REASON_CODES = frozenset(
    {
        "scheduler_halt_bound_violated",
        "scheduler_campaign_halted",
        "scheduler_bounds_unmeasured",
        "scheduler_timing_underivable",
        "scheduler_timing_cross_boot",
    }
)
G3_REASON_CODES = frozenset(
    {
        "scheduler_b22_cure_absent",
        "scheduler_b22_binding_absent",
        "scheduler_b22_cure_ineffective",
        "scheduler_shakedown_record_claim_use",
    }
)
G4_REASON_CODES = frozenset(
    {"readiness_git_tree_dirty", "readiness_reviewed_main_mismatch"}
)
G5_REASON_CODES = frozenset(
    {
        "scheduler_boot_pin_mismatch",
        "scheduler_boot_pin_underivable",
        "scheduler_boot_pin_conflict",
    }
)
G6_REASON_CODES = frozenset(
    {
        "scheduler_c1_verdict_uncustodied",
        "scheduler_c1_verdict_unparseable",
        "scheduler_c1_form_failed",
        "scheduler_c2_arm_not_pass",
        "scheduler_c2_horizon_exhausted",
        "scheduler_c3_census_missing",
        "scheduler_c3_census_dirty",
        "scheduler_c3_writers_present",
        "scheduler_c3_evaluator_context_invalid",
        "scheduler_c4_clock_underivable",
        "scheduler_c4_network_time_on",
        "scheduler_c4_privilege_absent",
        "scheduler_c5_undiagnosed_retry",
        "scheduler_c5_refusal_log_unreadable",
    }
)
G7_REASON_CODES = frozenset(
    {
        "scheduler_family_unpublished",
        "scheduler_family_marker_absent",
        "scheduler_family_marker_invalid",
        "scheduler_family_confirmation_absent",
        "scheduler_family_confirmation_invalid",
        "scheduler_family_boot_pin_mismatch",
    }
)
SCHEDULER_ENVIRONMENT_REASON_CODES = frozenset({"scheduler_environment_error"})

SCHEDULER_GATE_REASON_CODES = frozenset().union(
    G1_REASON_CODES,
    G2_REASON_CODES,
    G3_REASON_CODES,
    G4_REASON_CODES,
    G5_REASON_CODES,
    G6_REASON_CODES,
    G7_REASON_CODES,
    SCHEDULER_ENVIRONMENT_REASON_CODES,
)

_REASON_CODES_BY_GATE = {
    "G1": G1_REASON_CODES,
    "G2": G2_REASON_CODES,
    "G3": G3_REASON_CODES,
    "G4": G4_REASON_CODES,
    "G5": G5_REASON_CODES,
    "G6": G6_REASON_CODES,
    "G7": G7_REASON_CODES,
}

_REASON_TYPE_BY_CODE = {
    **{code: "TEMPORAL" for code in G1_REASON_CODES},
    **{code: "HALT" for code in G2_REASON_CODES},
    **{code: "ADMISSION" for code in G3_REASON_CODES},
    **{code: "GIT" for code in G4_REASON_CODES},
    **{code: "IDENTITY" for code in G5_REASON_CODES},
    **{code: "CONDITION" for code in G6_REASON_CODES},
    **{code: "CUSTODY" for code in G7_REASON_CODES},
    **{code: "ENVIRONMENT" for code in SCHEDULER_ENVIRONMENT_REASON_CODES},
}
_MIRRORED_FROM_BY_CODE = {code: "arm_readiness" for code in G4_REASON_CODES}

RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "receipt_kind",
        "receipt_id",
        "issued_at_utc",
        "now_monotonic_ns",
        "boot_session_id",
        "campaign_boot_pin_sha256",
        "window_class",
        "pack",
        "reviewed_main",
        "gates",
        "verdict",
        "claim_admissible",
        "assurance",
        "family_publication",
    }
)
GATE_RESULT_KEYS = frozenset(
    {"gate_id", "verdict", "observations", "refusals"}
)
REFUSAL_KEYS = frozenset({"type", "code", "gate_id", "detail"})
MIRRORED_REFUSAL_KEYS = REFUSAL_KEYS | {"mirrored_from"}
BOOT_PIN_KEYS = frozenset(
    {"schema_version", "family_id", "boot_session_id", "created_at_utc"}
)
FAMILY_PUBLICATION_KEYS = frozenset(
    {
        "family_id",
        "marker_path",
        "marker_sha256",
        "confirmation_sha256",
        "verification_receipt",
        "publication_head",
        "verdict",
        "refusals",
    }
)
FAMILY_VERIFICATION_REFERENCE_KEYS = frozenset({"path", "sha256"})
FAMILY_LIFECYCLE_REFUSAL_KEYS = frozenset({"role", "code", "type"})


class SchedulerGateError(ValueError):
    """The scheduler contract or a scheduler-controlled operation refused."""

    def __init__(
        self, code: str, detail: str, *, pin_sha256: str | None = None
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.pin_sha256 = pin_sha256


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def render_json(value: Mapping[str, Any]) -> bytes:
    """Return canonical human-readable receipt bytes."""

    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _require_exact_keys(value: object, keys: frozenset[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SchedulerGateError("scheduler_environment_error", f"{where} must be an object")
    observed = set(value)
    if observed != keys:
        missing = sorted(keys - observed)
        unknown = sorted(observed - keys)
        raise SchedulerGateError(
            "scheduler_environment_error",
            f"{where} keys are not exact (missing={missing}, unknown={unknown})",
        )
    return value


def _require_nonempty_string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchedulerGateError(
            "scheduler_environment_error", f"{where} must be a non-empty string"
        )
    return value


def _require_lower_sha256(value: object, where: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise SchedulerGateError(
            "scheduler_environment_error", f"{where} must be a lowercase SHA-256"
        )
    return value


def _gate_refusal(code: str, *, gate_id: str, detail: str) -> dict[str, Any]:
    """Mint one refusal under the scheduler's closed vocabulary."""

    if code not in SCHEDULER_GATE_REASON_CODES:
        raise SchedulerGateError(
            "scheduler_environment_error",
            f"attempted to emit unregistered scheduler refusal {code}",
        )
    if gate_id not in GATE_IDS:
        raise SchedulerGateError(
            "scheduler_environment_error", f"unknown scheduler gate {gate_id}"
        )
    if code not in _REASON_CODES_BY_GATE[gate_id]:
        raise SchedulerGateError(
            "scheduler_environment_error",
            f"scheduler refusal {code} does not belong to {gate_id}",
        )
    refusal = {
        "type": _REASON_TYPE_BY_CODE[code],
        "code": code,
        "gate_id": gate_id,
        "detail": detail,
    }
    mirrored_from = _MIRRORED_FROM_BY_CODE.get(code)
    if mirrored_from is not None:
        refusal["mirrored_from"] = mirrored_from
    return refusal


def _gate_result(
    gate_id: str,
    verdict: str,
    *,
    observations: Mapping[str, Any] | None = None,
    refusals: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "verdict": verdict,
        "observations": dict(observations or {}),
        "refusals": [dict(item) for item in (refusals or [])],
    }


def _not_implemented(gate_id: str) -> dict[str, Any]:
    return _gate_result(
        gate_id,
        "NOT_IMPLEMENTED",
        observations={"stage": "not_implemented"},
    )


def _not_evaluated(gate_id: str) -> dict[str, Any]:
    return _gate_result(
        gate_id,
        "NOT_EVALUATED",
        observations={"reason": "G5_boot_pin_not_pass"},
    )


def validate_scheduler_gate_receipt(receipt: object) -> Mapping[str, Any]:
    """Validate the exact v2 receipt shape and staged verdict invariants."""

    value = _require_exact_keys(receipt, RECEIPT_KEYS, "scheduler gate receipt")
    if value["schema_version"] != SCHEDULER_GATE_RECEIPT_SCHEMA:
        raise SchedulerGateError("scheduler_environment_error", "scheduler receipt schema is invalid")
    if value["receipt_kind"] != "window_scheduler_gate":
        raise SchedulerGateError("scheduler_environment_error", "scheduler receipt kind is invalid")
    try:
        if str(uuid.UUID(value["receipt_id"])) != value["receipt_id"]:
            raise ValueError
    except (TypeError, ValueError, AttributeError) as exc:
        raise SchedulerGateError(
            "scheduler_environment_error", "receipt_id must be a canonical UUID"
        ) from exc
    _require_nonempty_string(value["issued_at_utc"], "issued_at_utc")
    if not isinstance(value["now_monotonic_ns"], int) or isinstance(
        value["now_monotonic_ns"], bool
    ) or value["now_monotonic_ns"] < 0:
        raise SchedulerGateError(
            "scheduler_environment_error", "now_monotonic_ns must be a non-negative integer"
        )
    _require_nonempty_string(value["boot_session_id"], "boot_session_id")
    if value["window_class"] not in WINDOW_CLASSES:
        raise SchedulerGateError("scheduler_environment_error", "window_class is invalid")
    if not isinstance(value["pack"], Mapping):
        raise SchedulerGateError("scheduler_environment_error", "pack must be an object")
    if not isinstance(value["reviewed_main"], Mapping):
        raise SchedulerGateError("scheduler_environment_error", "reviewed_main must be an object")
    if value["verdict"] not in {"GO", "NO-GO"}:
        raise SchedulerGateError("scheduler_environment_error", "receipt verdict is invalid")
    if not isinstance(value["claim_admissible"], bool):
        raise SchedulerGateError("scheduler_environment_error", "claim_admissible must be boolean")
    if not isinstance(value["assurance"], Mapping):
        raise SchedulerGateError("scheduler_environment_error", "assurance must be an object")

    gates = value["gates"]
    if not isinstance(gates, list) or len(gates) != len(GATE_EVALUATION_ORDER):
        raise SchedulerGateError("scheduler_environment_error", "all seven gates must be present")
    observed_order: list[str] = []
    for index, raw_gate in enumerate(gates):
        gate = _require_exact_keys(raw_gate, GATE_RESULT_KEYS, f"gates[{index}]")
        gate_id = gate["gate_id"]
        if gate_id not in GATE_IDS:
            raise SchedulerGateError(
                "scheduler_environment_error", f"unknown scheduler gate {gate_id}"
            )
        observed_order.append(gate_id)
        if gate["verdict"] not in GATE_VERDICTS:
            raise SchedulerGateError(
                "scheduler_environment_error", f"{gate_id} verdict is invalid"
            )
        if not isinstance(gate["observations"], Mapping):
            raise SchedulerGateError(
                "scheduler_environment_error", f"{gate_id} observations must be an object"
            )
        refusals = gate["refusals"]
        if not isinstance(refusals, list):
            raise SchedulerGateError(
                "scheduler_environment_error", f"{gate_id} refusals must be a list"
            )
        for refusal_index, raw_refusal in enumerate(refusals):
            if not isinstance(raw_refusal, Mapping):
                raise SchedulerGateError(
                    "scheduler_environment_error",
                    f"{gate_id}.refusals[{refusal_index}] must be an object",
                )
            code = raw_refusal.get("code")
            expected_keys = (
                MIRRORED_REFUSAL_KEYS if code in _MIRRORED_FROM_BY_CODE else REFUSAL_KEYS
            )
            refusal = _require_exact_keys(
                raw_refusal, expected_keys, f"{gate_id}.refusals[{refusal_index}]"
            )
            if code not in SCHEDULER_GATE_REASON_CODES:
                raise SchedulerGateError(
                    "scheduler_environment_error", f"unregistered scheduler refusal {code}"
                )
            if code not in _REASON_CODES_BY_GATE[gate_id]:
                raise SchedulerGateError(
                    "scheduler_environment_error",
                    f"scheduler refusal {code} does not belong to {gate_id}",
                )
            if refusal["gate_id"] != gate_id:
                raise SchedulerGateError(
                    "scheduler_environment_error", "refusal gate_id does not match its gate"
                )
            if refusal["type"] != _REASON_TYPE_BY_CODE[code]:
                raise SchedulerGateError(
                    "scheduler_environment_error", "refusal type does not match its code"
                )
            if code in _MIRRORED_FROM_BY_CODE and refusal["mirrored_from"] != "arm_readiness":
                raise SchedulerGateError(
                    "scheduler_environment_error", "mirrored refusal omits its exact origin"
                )
            _require_nonempty_string(refusal["detail"], "refusal detail")
        if gate["verdict"] == "REFUSE" and not refusals:
            raise SchedulerGateError(
                "scheduler_environment_error", f"{gate_id} REFUSE requires a refusal"
            )
        if gate["verdict"] != "REFUSE" and refusals:
            raise SchedulerGateError(
                "scheduler_environment_error", f"{gate_id} non-REFUSE cannot carry refusals"
            )
    if tuple(observed_order) != GATE_EVALUATION_ORDER:
        raise SchedulerGateError(
            "scheduler_environment_error", "gate order must record G5 first"
        )

    gates_by_id = {gate["gate_id"]: gate for gate in gates}
    g5_verdict = gates_by_id["G5"]["verdict"]
    if g5_verdict not in {"PASS", "REFUSE"}:
        raise SchedulerGateError(
            "scheduler_environment_error", "G5 must be PASS or REFUSE in stages 1-2"
        )
    if gates_by_id["G4"]["verdict"] not in {"PASS", "REFUSE"}:
        raise SchedulerGateError(
            "scheduler_environment_error", "G4 must be PASS or REFUSE in stages 1-2"
        )
    expected_monotonic_verdict = (
        "NOT_IMPLEMENTED" if g5_verdict == "PASS" else "NOT_EVALUATED"
    )
    for gate_id in ("G1", "G2"):
        if gates_by_id[gate_id]["verdict"] != expected_monotonic_verdict:
            raise SchedulerGateError(
                "scheduler_environment_error",
                f"{gate_id} must be {expected_monotonic_verdict} in stages 1-2",
            )
    for gate_id in ("G3", "G6"):
        if gates_by_id[gate_id]["verdict"] != "NOT_IMPLEMENTED":
            raise SchedulerGateError(
                "scheduler_environment_error",
                f"{gate_id} must be NOT_IMPLEMENTED in stages 1-2",
            )
    if gates_by_id["G7"]["verdict"] not in {"PASS", "REFUSE"}:
        raise SchedulerGateError(
            "scheduler_environment_error", "G7 must be PASS or REFUSE"
        )

    family = _require_exact_keys(
        value["family_publication"],
        FAMILY_PUBLICATION_KEYS,
        "family_publication",
    )
    if family["verdict"] != gates_by_id["G7"]["verdict"]:
        raise SchedulerGateError(
            "scheduler_environment_error",
            "family_publication verdict differs from G7",
        )
    _require_nonempty_string(family["family_id"], "family_publication.family_id")
    verification = _require_exact_keys(
        family["verification_receipt"],
        FAMILY_VERIFICATION_REFERENCE_KEYS,
        "family_publication.verification_receipt",
    )
    lifecycle_refusals = family["refusals"]
    if not isinstance(lifecycle_refusals, list):
        raise SchedulerGateError(
            "scheduler_environment_error", "family_publication.refusals must be a list"
        )
    for index, raw_refusal in enumerate(lifecycle_refusals):
        refusal = _require_exact_keys(
            raw_refusal,
            FAMILY_LIFECYCLE_REFUSAL_KEYS,
            f"family_publication.refusals[{index}]",
        )
        if refusal != {
            "role": "FAMILY_PUBLICATION",
            "code": "readiness_r1_family_publication",
            "type": "CUSTODY",
        }:
            raise SchedulerGateError(
                "scheduler_environment_error",
                "family publication lifecycle refusal differs from R1",
            )
    if family["verdict"] == "PASS":
        for name in (
            "marker_path",
            "marker_sha256",
            "confirmation_sha256",
            "publication_head",
        ):
            if family[name] is None:
                raise SchedulerGateError(
                    "scheduler_environment_error", f"passing family publication omits {name}"
                )
        _require_nonempty_string(family["marker_path"], "family_publication.marker_path")
        _require_lower_sha256(family["marker_sha256"], "family_publication.marker_sha256")
        _require_lower_sha256(
            family["confirmation_sha256"], "family_publication.confirmation_sha256"
        )
        _require_nonempty_string(
            family["publication_head"], "family_publication.publication_head"
        )
        _require_nonempty_string(verification["path"], "family verification path")
        _require_lower_sha256(verification["sha256"], "family verification digest")
        if lifecycle_refusals:
            raise SchedulerGateError(
                "scheduler_environment_error", "passing family publication carries refusals"
            )
    else:
        if any(
            family[name] is not None
            for name in (
                "marker_path",
                "marker_sha256",
                "confirmation_sha256",
                "publication_head",
            )
        ) or any(verification[name] is not None for name in ("path", "sha256")):
            raise SchedulerGateError(
                "scheduler_environment_error",
                "refused family publication must null unverifiable bindings",
            )
        if lifecycle_refusals != [
            {
                "role": "FAMILY_PUBLICATION",
                "code": "readiness_r1_family_publication",
                "type": "CUSTODY",
            }
        ]:
            raise SchedulerGateError(
                "scheduler_environment_error", "refused family publication needs one R1 refusal"
            )

    g5_observations = gates_by_id["G5"]["observations"]
    if "pin_sha256" not in g5_observations:
        raise SchedulerGateError(
            "scheduler_environment_error", "G5 observations must bind pin_sha256"
        )
    bound_pin_sha256 = value["campaign_boot_pin_sha256"]
    if bound_pin_sha256 != g5_observations["pin_sha256"]:
        raise SchedulerGateError(
            "scheduler_environment_error",
            "receipt campaign boot pin digest disagrees with G5 observations",
        )
    if bound_pin_sha256 is None:
        if g5_verdict != "REFUSE":
            raise SchedulerGateError(
                "scheduler_environment_error",
                "a passing G5 receipt must bind the campaign boot pin digest",
            )
    else:
        _require_lower_sha256(
            bound_pin_sha256, "campaign_boot_pin_sha256"
        )

    go_eligible = all(
        gate["verdict"] in {"PASS", "RECORD_ONLY"} for gate in gates
    ) and family["verdict"] == "PASS"
    if (value["verdict"] == "GO") is not go_eligible:
        raise SchedulerGateError(
            "scheduler_environment_error", "composed verdict disagrees with gate verdicts"
        )
    if value["claim_admissible"] and value["verdict"] != "GO":
        raise SchedulerGateError(
            "scheduler_environment_error", "a NO-GO receipt cannot be claim-admissible"
        )
    return value


