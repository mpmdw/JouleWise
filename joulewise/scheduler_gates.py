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

from joulewise import arm_readiness
from joulewise.arm_readiness import _fsync_directory


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


def _validate_boot_pin(value: object) -> Mapping[str, Any]:
    pin = _require_exact_keys(value, BOOT_PIN_KEYS, "campaign boot pin")
    if pin["schema_version"] != CAMPAIGN_BOOT_PIN_SCHEMA:
        raise SchedulerGateError("scheduler_boot_pin_conflict", "campaign boot pin schema is invalid")
    _require_nonempty_string(pin["family_id"], "campaign boot pin family_id")
    _require_nonempty_string(pin["boot_session_id"], "campaign boot pin boot_session_id")
    _require_nonempty_string(pin["created_at_utc"], "campaign boot pin created_at_utc")
    return pin


def _read_boot_pin(path: Path) -> tuple[Mapping[str, Any], str]:
    digest: str | None = None
    try:
        raw = path.read_bytes()
        digest = arm_readiness.sha256_bytes(raw)
        sidecar = path.with_name(CAMPAIGN_BOOT_PIN_SIDECAR_NAME).read_bytes()
        if sidecar != arm_readiness.gnu_sidecar(digest, path.name):
            raise SchedulerGateError(
                "scheduler_boot_pin_conflict",
                "campaign boot pin SHA-256 sidecar mismatch",
                pin_sha256=digest,
            )
        value = json.loads(raw.decode("utf-8"))
        return _validate_boot_pin(value), digest
    except SchedulerGateError as exc:
        if exc.code == "scheduler_boot_pin_conflict" and exc.pin_sha256 is not None:
            raise
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict", str(exc), pin_sha256=digest
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict",
            f"cannot authenticate existing campaign boot pin: {exc}",
            pin_sha256=digest,
        ) from exc


def _create_boot_pin(
    path: Path, *, family_id: str, boot_session_id: str
) -> tuple[Mapping[str, Any], str]:
    pin = {
        "schema_version": CAMPAIGN_BOOT_PIN_SCHEMA,
        "family_id": family_id,
        "boot_session_id": boot_session_id,
        "created_at_utc": _utc_now(),
    }
    raw = render_json(pin)
    digest = arm_readiness.sha256_bytes(raw)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict",
            "campaign boot pin create lost the single-writer race",
        ) from exc
    except OSError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict", f"cannot create campaign boot pin: {exc}"
        ) from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict", f"cannot persist campaign boot pin: {exc}"
        ) from exc
    try:
        _fsync_directory(path.parent)
        sidecar_path = path.with_name(CAMPAIGN_BOOT_PIN_SIDECAR_NAME)
        descriptor = os.open(
            sidecar_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(arm_readiness.gnu_sidecar(digest, path.name))
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
    except Exception as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict",
            f"cannot persist campaign boot pin authentication sidecar: {exc}",
            pin_sha256=digest,
        ) from exc
    return pin, digest


def _load_or_create_boot_pin(
    campaign_root: Path, *, family_id: str, live_boot_session_id: str
) -> tuple[Mapping[str, Any], str, tuple[str, ...]]:
    pin_path = campaign_root / CAMPAIGN_BOOT_PIN_NAME
    if os.path.lexists(pin_path):
        pin, digest = _read_boot_pin(pin_path)
        return pin, digest, ()
    try:
        custody_entries = sorted(path.name for path in campaign_root.iterdir())
    except OSError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_underivable",
            f"cannot inspect campaign custody root before first pin: {exc}",
        ) from exc
    # A missing pin refuses when the root carries SCHEDULER CUSTODY
    # HISTORY (an orphan sidecar, or any emitted gate receipt): history
    # without a pin means the pin was lost, and re-pinning would
    # silently re-anchor the campaign span to a new boot (lens B-1a).
    # Entries foreign to this module (staging files, dotfiles, empty
    # dirs) do not brick first-pin creation (lens ND-1); they are
    # returned so the caller records them in the G5 observations.
    scheduler_history = sorted(
        name
        for name in custody_entries
        if name == CAMPAIGN_BOOT_PIN_SIDECAR_NAME
        or name.startswith(SCHEDULER_GATE_RECEIPT_FILE_PREFIX)
    )
    if scheduler_history:
        raise SchedulerGateError(
            "scheduler_boot_pin_underivable",
            "campaign boot pin is missing from a custody root that carries "
            f"scheduler history (entries={scheduler_history})",
        )
    foreign_entries = tuple(
        name for name in custody_entries if name not in scheduler_history
    )
    pin, digest = _create_boot_pin(
        pin_path,
        family_id=family_id,
        boot_session_id=live_boot_session_id,
    )
    return pin, digest, foreign_entries


def _live_boot_session_id() -> str:
    try:
        return arm_readiness._current_boot_session_id()
    except arm_readiness.ArmReadinessError as exc:
        raise SchedulerGateError("scheduler_boot_pin_underivable", str(exc)) from exc


def _evaluate_g5(
    *,
    campaign_root: Path,
    family_id: str,
    receipt_boot_session_ids: Mapping[str, str],
) -> tuple[dict[str, Any], str]:
    observations: dict[str, Any] = {
        "pin_path": str((campaign_root / CAMPAIGN_BOOT_PIN_NAME).resolve()),
        "family_id": family_id,
        "live_boot_session_id": "unavailable",
        "pinned_boot_session_id": "unavailable",
        "pin_sha256": None,
        "receipt_boot_session_ids": dict(receipt_boot_session_ids),
    }
    try:
        if not campaign_root.is_dir():
            raise SchedulerGateError(
                "scheduler_boot_pin_conflict", "campaign custody root must already exist"
            )
        _require_nonempty_string(family_id, "family_id")
        if not receipt_boot_session_ids:
            raise SchedulerGateError(
                "scheduler_boot_pin_underivable", "no receipt boot_session_id values were supplied"
            )
        for receipt_id, boot_session_id in receipt_boot_session_ids.items():
            _require_nonempty_string(receipt_id, "receipt id")
            _require_nonempty_string(boot_session_id, f"{receipt_id}.boot_session_id")

        live = _live_boot_session_id()
        observations["live_boot_session_id"] = live
        pin, pin_sha256, foreign_entries = _load_or_create_boot_pin(
            campaign_root, family_id=family_id, live_boot_session_id=live
        )
        observations["pin_sha256"] = pin_sha256
        if foreign_entries:
            observations["pin_creation_ignored_entries"] = list(foreign_entries)
        pinned = str(pin["boot_session_id"])
        observations["pinned_boot_session_id"] = pinned
        observations["pin_created_at_utc"] = pin["created_at_utc"]
        if pin["family_id"] != family_id:
            raise SchedulerGateError(
                "scheduler_boot_pin_conflict", "campaign boot pin belongs to a different family"
            )
        mismatched_receipts = sorted(
            receipt_id
            for receipt_id, boot_session_id in receipt_boot_session_ids.items()
            if boot_session_id != pinned
        )
        observations["mismatched_receipts"] = mismatched_receipts
        if live != pinned or mismatched_receipts:
            raise SchedulerGateError(
                "scheduler_boot_pin_mismatch",
                "live, span-pinned, and receipt boot_session_id values are not identical",
            )
        return _gate_result("G5", "PASS", observations=observations), live
    except SchedulerGateError as exc:
        if exc.pin_sha256 is not None:
            observations["pin_sha256"] = exc.pin_sha256
        code = exc.code
        if code not in G5_REASON_CODES:
            code = "scheduler_boot_pin_underivable"
        return (
            _gate_result(
                "G5",
                "REFUSE",
                observations=observations,
                refusals=[_gate_refusal(code, gate_id="G5", detail=str(exc))],
            ),
            str(observations["live_boot_session_id"]),
        )


def _g4_failed_conjunct(reviewed: Mapping[str, Any]) -> str:
    if reviewed.get("clean") is not True:
        return "dirty"
    head = reviewed.get("head_commit")
    local_main = reviewed.get("local_main_commit")
    origin_main = reviewed.get("origin_main_commit")
    if "unavailable" in {head, local_main, origin_main}:
        return "unavailable"
    if head != local_main:
        return "head_ne_local_main"
    if head != origin_main:
        return "head_ne_origin_main"
    # A malformed or stale proof that claims non-exact despite equal raw values
    # is still underivable and therefore follows the availability refusal limb.
    return "unavailable"


def _evaluate_g4(pack_root: Path) -> tuple[dict[str, Any], Mapping[str, Any]]:
    try:
        reviewed = arm_readiness.reviewed_main(pack_root)
    except Exception:
        reviewed = {
            "head_commit": "unavailable",
            "head_tree_oid": "unavailable",
            "local_main_commit": "unavailable",
            "origin_main_commit": "unavailable",
            "clean": True,
            "exact_match": False,
        }
    observations = dict(reviewed)
    observations["freeze_interlock"] = "V-3(c)_local_main_and_origin_main"
    if reviewed.get("exact_match") is True:
        observations["failed_conjunct"] = None
        return _gate_result("G4", "PASS", observations=observations), reviewed

    failed_conjunct = _g4_failed_conjunct(reviewed)
    observations["failed_conjunct"] = failed_conjunct
    code = (
        "readiness_git_tree_dirty"
        if failed_conjunct == "dirty"
        else "readiness_reviewed_main_mismatch"
    )
    detail = f"reviewed_main exact_match is not true ({failed_conjunct})"
    return (
        _gate_result(
            "G4",
            "REFUSE",
            observations=observations,
            refusals=[_gate_refusal(code, gate_id="G4", detail=detail)],
        ),
        reviewed,
    )


def _g7_scheduler_code(check_id: str) -> str:
    if check_id == "marker_absent":
        return "scheduler_family_marker_absent"
    if check_id == "confirmation_missing":
        return "scheduler_family_confirmation_absent"
    if check_id.startswith("confirmation_"):
        return "scheduler_family_confirmation_invalid"
    if check_id == "head_unpublished":
        return "scheduler_family_unpublished"
    if check_id == "family_incoherent":
        return "scheduler_family_boot_pin_mismatch"
    return "scheduler_family_marker_invalid"


def _evaluate_g7(
    *,
    repository: Path,
    pack_root: Path,
    campaign_root: Path,
    family_id: str,
    marker_path: Path,
    confirmation_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    observations: dict[str, Any] = {
        "phase": "pre-arm",
        "diagnostic": None,
        "lifecycle_refusal": None,
    }
    try:
        result = arm_readiness.verify_family_publication_marker(
            repository,
            marker_path,
            phase="pre-arm",
            confirmation_path=confirmation_path,
            target_pack_root=pack_root,
        )
        # The receipt must be able to gate before anything downstream records
        # it: a candidate-lane receipt is forged-origin/main-conditional and
        # must never launder into a scheduler PASS.
        arm_readiness.require_gate_admissible_verification(result)
        if result["family_id"] != family_id:
            raise arm_readiness.FamilyPublicationError(
                "family_incoherent",
                "published marker family differs from campaign boot-pin family",
            )
        verification_root = campaign_root / "family_publication"
        verification_root.mkdir(parents=True, exist_ok=True)
        verification_path = verification_root / f"pre-arm-verification-{uuid.uuid4()}.json"
        verification_raw = render_json(result)
        arm_readiness._exclusive_write(verification_path, verification_raw)
        arm_readiness._exclusive_write(
            verification_path.with_name(f"{verification_path.name}.sha256"),
            arm_readiness.gnu_sidecar(
                arm_readiness.sha256_bytes(verification_raw), verification_path.name
            ),
        )
        marker_sha = arm_readiness.sha256_bytes(marker_path.read_bytes())
        confirmation_sha = arm_readiness.sha256_bytes(confirmation_path.read_bytes())
        block = {
            "family_id": family_id,
            "marker_path": str(marker_path),
            "marker_sha256": marker_sha,
            "confirmation_sha256": confirmation_sha,
            "verification_receipt": {
                "path": str(verification_path),
                "sha256": arm_readiness.sha256_bytes(verification_raw),
            },
            "publication_head": result["consulted_git"]["head_commit"],
            "verdict": "PASS",
            "refusals": [],
        }
        return _gate_result("G7", "PASS", observations=observations), block
    except arm_readiness.FamilyPublicationError as exc:
        code = _g7_scheduler_code(exc.check_id)
        lifecycle = {
            "role": "FAMILY_PUBLICATION",
            "code": "readiness_r1_family_publication",
            "type": "CUSTODY",
        }
        observations["diagnostic"] = exc.check_id
        observations["lifecycle_refusal"] = lifecycle
        block = {
            "family_id": family_id,
            "marker_path": None,
            "marker_sha256": None,
            "confirmation_sha256": None,
            "verification_receipt": {"path": None, "sha256": None},
            "publication_head": None,
            "verdict": "REFUSE",
            "refusals": [lifecycle],
        }
        return (
            _gate_result(
                "G7",
                "REFUSE",
                observations=observations,
                refusals=[_gate_refusal(code, gate_id="G7", detail=str(exc))],
            ),
            block,
        )
    except (OSError, arm_readiness.ArmReadinessError) as exc:
        wrapped = arm_readiness.FamilyPublicationError("registry_mismatch", str(exc))
        return _evaluate_g7_refusal(family_id, observations, wrapped)


def _evaluate_g7_refusal(
    family_id: str,
    observations: dict[str, Any],
    exc: arm_readiness.FamilyPublicationError,
) -> tuple[dict[str, Any], dict[str, Any]]:
    lifecycle = {
        "role": "FAMILY_PUBLICATION",
        "code": "readiness_r1_family_publication",
        "type": "CUSTODY",
    }
    observations["diagnostic"] = exc.check_id
    observations["lifecycle_refusal"] = lifecycle
    block = {
        "family_id": family_id,
        "marker_path": None,
        "marker_sha256": None,
        "confirmation_sha256": None,
        "verification_receipt": {"path": None, "sha256": None},
        "publication_head": None,
        "verdict": "REFUSE",
        "refusals": [lifecycle],
    }
    return (
        _gate_result(
            "G7",
            "REFUSE",
            observations=observations,
            refusals=[
                _gate_refusal(
                    _g7_scheduler_code(exc.check_id),
                    gate_id="G7",
                    detail=str(exc),
                )
            ],
        ),
        block,
    )


def evaluate_scheduler_gates(
    *,
    pack_root: Path | str,
    campaign_root: Path | str,
    family_id: str,
    window_class: str,
    receipt_boot_session_ids: Mapping[str, str],
    now_monotonic_ns: int | None = None,
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
) -> dict[str, Any]:
    """Evaluate every scheduler gate and return a strict staged receipt.

    G5 always executes first.  A G5 refusal makes only the monotonic-clock
    gates G1/G2 ``NOT_EVALUATED``; G4 still executes, and all other staged
    gates remain visibly ``NOT_IMPLEMENTED``.
    """

    pack_path = Path(pack_root)
    campaign_path = Path(campaign_root)
    if window_class not in WINDOW_CLASSES:
        raise SchedulerGateError("scheduler_environment_error", "window_class is invalid")
    now_ns = time.monotonic_ns() if now_monotonic_ns is None else now_monotonic_ns
    if not isinstance(now_ns, int) or isinstance(now_ns, bool) or now_ns < 0:
        raise SchedulerGateError(
            "scheduler_environment_error", "now_monotonic_ns must be a non-negative integer"
        )

    # Required evaluation order: G5 completes before any other gate is called.
    g5, live_boot_session_id = _evaluate_g5(
        campaign_root=campaign_path,
        family_id=family_id,
        receipt_boot_session_ids=receipt_boot_session_ids,
    )
    g1 = _not_implemented("G1") if g5["verdict"] == "PASS" else _not_evaluated("G1")
    g2 = _not_implemented("G2") if g5["verdict"] == "PASS" else _not_evaluated("G2")
    g3 = _not_implemented("G3")
    g4, reviewed = _evaluate_g4(pack_path)
    g6 = _not_implemented("G6")
    try:
        repository = arm_readiness._repo_for_pack(pack_path)
    except arm_readiness.ArmReadinessError:
        repository = pack_path
    publication_root = campaign_path / "family_publication"
    marker_path = (
        Path(family_publication_marker)
        if family_publication_marker is not None
        else publication_root / arm_readiness.FAMILY_PUBLICATION_MARKER_NAME
    )
    confirmation_path = (
        Path(step6_confirmation_table)
        if step6_confirmation_table is not None
        else publication_root / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
    )
    g7, family_publication = _evaluate_g7(
        repository=repository,
        pack_root=pack_path,
        campaign_root=campaign_path,
        family_id=family_id,
        marker_path=marker_path,
        confirmation_path=confirmation_path,
    )

    # Pack authentication is not a scheduler gate and cannot be represented as
    # a successful placeholder.  All seven gate evaluations above still run;
    # then the owning arm-readiness loader fails closed if the pack is invalid.
    pack = arm_readiness._pack_record(pack_path)

    gates = [g5, g1, g2, g3, g4, g6, g7]
    receipt = {
        "schema_version": SCHEDULER_GATE_RECEIPT_SCHEMA,
        "receipt_kind": "window_scheduler_gate",
        "receipt_id": str(uuid.uuid4()),
        "issued_at_utc": _utc_now(),
        "now_monotonic_ns": now_ns,
        "boot_session_id": live_boot_session_id,
        "campaign_boot_pin_sha256": g5["observations"]["pin_sha256"],
        "window_class": window_class,
        "pack": dict(pack),
        "reviewed_main": dict(reviewed),
        "gates": gates,
        "verdict": (
            "GO"
            if all(gate["verdict"] in {"PASS", "RECORD_ONLY"} for gate in gates)
            else "NO-GO"
        ),
        # G3 owns claim admission and is not implemented in this stage.
        "claim_admissible": False,
        "assurance": dict(arm_readiness.ASSURANCE),
        "family_publication": family_publication,
    }
    validate_scheduler_gate_receipt(receipt)
    return receipt
