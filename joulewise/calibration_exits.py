"""Typed, cross-layer governed exits for unattended calibration.

This module is the sole machine authority for expected operational refusals.
Callers raise :class:`RefusalCode` at the refusal site and recovery/runbook
surfaces project the immutable inventory below.  Human prose is deliberately
diagnostic only; retry and exit policy never depends on exception text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TextIO


class RefusalCode(str, Enum):
    # Reducer/snapshot state codes retained byte-for-byte for compatibility.
    LEDGER_MISSING = "calibration_ledger_missing"
    LEDGER_MALFORMED = "calibration_ledger_malformed"
    LEDGER_CHAIN_CONFLICT = "calibration_ledger_chain_conflict"
    LEDGER_ATTEMPT_CONFLICT = "calibration_ledger_attempt_conflict"
    LEDGER_BRACKET_SESSION_CONFLICT = "calibration_ledger_bracket_session_conflict"
    LEDGER_BRACKET_SLOT_CLAIMED = "calibration_ledger_bracket_slot_claimed"
    LEDGER_BRACKET_SESSION_OPEN = "calibration_ledger_bracket_session_open"
    LEDGER_CONTENT_CONFLICT = "calibration_ledger_content_conflict"
    LEDGER_PENDING = "calibration_ledger_pending"
    LEDGER_HEAD_UNCOMMITTED = "calibration_ledger_head_uncommitted"
    LEDGER_HEAD_MISMATCH = "calibration_ledger_head_mismatch"
    LEDGER_ROLLBACK = "calibration_ledger_rollback"
    LEDGER_RECOVERY_REQUIRED = "calibration_ledger_recovery_required"
    LEDGER_OPERATION_CONFLICT = "calibration_ledger_operation_conflict"
    LEDGER_UNGOVERNED_BUSINESS = "calibration_ledger_ungoverned_business"
    LEDGER_BASELINE_MISSING = "calibration_ledger_baseline_missing"
    LEDGER_CUSTODY_INVALID = "calibration_ledger_custody_invalid"
    LEDGER_SNAPSHOT_REQUIRED = "calibration_ledger_snapshot_required"
    LEDGER_OFF_LEDGER_ARTIFACT = "calibration_ledger_off_ledger_artifact"
    OBSERVATION_UNCLASSIFIABLE = "calibration_observation_unclassifiable"

    # Physical protocol and lease refusals.
    LIVE_WRITER_CONTENTION = "calibration_live_writer_contention"
    UNSAFE_LOCK_INODE = "calibration_unsafe_lock_inode"
    PHYSICAL_LEDGER_UNREADABLE = "calibration_physical_ledger_unreadable"
    LEGACY_JOURNAL_UNREADABLE = "calibration_legacy_journal_unreadable"
    LEGACY_JOURNAL_ARCHIVE_CONFLICT = "calibration_legacy_journal_archive_conflict"
    LEGACY_JOURNAL_ARCHIVE_FAILED = "calibration_legacy_journal_archive_failed"
    TAIL_REQUIRES_ABANDON = "calibration_tail_requires_abandon"
    INTENT_TARGET_MALFORMED = "calibration_intent_target_malformed"
    RECOVERY_NONCONVERGENT = "calibration_recovery_nonconvergent"
    RECOVERY_CREDENTIALS_INVALID = "calibration_recovery_credentials_invalid"
    ABANDON_CREDENTIALS_INVALID = "calibration_abandon_credentials_invalid"
    ABANDON_PIN_MISMATCH = "calibration_abandon_pin_mismatch"
    ABANDON_ACTIVE_INTENT = "calibration_abandon_active_intent"
    ABANDON_NOT_CLEAN = "calibration_abandon_not_clean"
    HEAD_PIN_UNREADABLE = "calibration_head_pin_unreadable"
    HEAD_PIN_MALFORMED = "calibration_head_pin_malformed"
    HEAD_PIN_NOT_COMMITTED = "calibration_head_pin_not_committed"

    # Bracket/session operation refusals.
    RESERVATION_INPUT_INVALID = "calibration_reservation_input_invalid"
    RESERVATION_HEAD_MISMATCH = "calibration_reservation_head_mismatch"
    RESERVATION_IDENTITY_CONFLICT = "calibration_reservation_identity_conflict"
    RESERVED_SLOT_MISMATCH = "calibration_reserved_slot_mismatch"
    SESSION_NOT_FOUND = "calibration_session_not_found"
    SESSION_NOT_OPEN = "calibration_session_not_open"
    SLOT_ORDER_CONFLICT = "calibration_slot_order_conflict"
    CLAIM_ID_INVALID = "calibration_claim_id_invalid"
    FINALIZATION_BINDING_CONFLICT = "calibration_finalization_binding_conflict"
    SESSION_NOT_TERMINAL = "calibration_session_not_terminal"
    SESSION_TERMINAL_NOT_HEAD = "calibration_session_terminal_not_head"
    CUSTODY_PARTIAL = "calibration_custody_partial"
    CUSTODY_UNREADABLE = "calibration_custody_unreadable"
    CUSTODY_COMPLETE_USE_RESUME = "calibration_custody_complete_use_resume"
    PLAN_UNREADABLE = "calibration_plan_unreadable"
    PLAN_HASH_MISMATCH = "calibration_plan_hash_mismatch"

    # Phase-aware readiness and pin advancement.
    PRE_RESERVE_NOT_READY = "calibration_pre_reserve_not_ready"
    PRE_SLOT_NOT_READY = "calibration_pre_slot_not_ready"
    TERMINAL_NOT_READY = "calibration_terminal_not_ready"
    PIN_ADVANCEMENT_NOT_NEEDED = "calibration_pin_advancement_not_needed"
    PIN_ADVANCEMENT_UNSAFE = "calibration_pin_advancement_unsafe"
    PIN_CANDIDATE_MISMATCH = "calibration_pin_candidate_mismatch"

    # Public writer/reservation CLI protocol refusals.
    RESERVATION_JSON_INVALID = "calibration_reservation_json_invalid"
    WRITER_BRACKET_ARGUMENTS = "calibration_writer_bracket_arguments"
    WRITER_BRACKET_REDERIVE_CONFLICT = "calibration_writer_bracket_rederive_conflict"
    FROZEN_PROTOCOL_INVALID = "calibration_frozen_protocol_invalid"
    REDERIVE_OUTPUT_REQUIRED = "calibration_rederive_output_required"
    REDERIVE_FAILED = "calibration_rederive_failed"
    OUTPUT_REQUIRES_REDERIVE = "calibration_output_requires_rederive"
    QUIET_MAC_AUTH_REQUIRED = "calibration_quiet_mac_auth_required"
    POWER_POLICY_REQUIRED = "calibration_power_policy_required"
    DISPLAY_ARM_FAILED = "calibration_display_arm_failed"
    SAMPLER_NEVER_READY = "calibration_sampler_never_ready"
    ROLLOVER_GATE_TIMEOUT = "pulse_calibration_rollover_gate_timeout"


class TerminalResult(str, Enum):
    OPERATION_COMPLETED = "operation_completed"
    READY_TO_ARM = "ready_to_arm"
    SESSION_ABORTED = "session_aborted"
    NIGHT_STOPPED_PRESERVED = "night_stopped_preserved"


class WitnessClass(str, Enum):
    OPERATIONAL = "operational"
    CORRUPTION_BACKSTOP = "corruption_backstop"
    INTERNAL_INVARIANT = "internal_invariant"


@dataclass(frozen=True)
class RefusalRecord:
    code: RefusalCode
    component: str
    phase: str
    retry_class: str
    exit_kind: str
    exit_id: str
    command: str
    runbook_anchor: str
    arm_blocked: bool
    prior_crash_reachable: bool
    witness_class: WitnessClass
    witness_id: str
    witness_note: str
    terminal_result: TerminalResult
    night_loss: bool
    description: str
    process_exit: int = 2


def _record(
    code: RefusalCode,
    description: str,
    *,
    component: str = "ledger",
    phase: str = "operation",
    retry_class: str = "after-governed-exit",
    exit_kind: str = "stop-preserved",
    exit_id: str = "hard-stop-preserved",
    command: str = "recover_calibration_ledger.py explain {code}",
    runbook_anchor: str = "d-117-10-calibration-ledger-refusals-and-governed-exits",
    terminal_result: TerminalResult = TerminalResult.NIGHT_STOPPED_PRESERVED,
    prior_crash_reachable: bool = False,
    witness_class: WitnessClass = WitnessClass.OPERATIONAL,
    witness_note: str = "reachable through governed public operations or crash recovery",
    night_loss: bool = True,
    process_exit: int = 2,
) -> RefusalRecord:
    return RefusalRecord(
        code=code,
        component=component,
        phase=phase,
        retry_class=retry_class,
        exit_kind=exit_kind,
        exit_id=exit_id,
        command=command.format(code=code.value),
        runbook_anchor=runbook_anchor,
        arm_blocked=True,
        prior_crash_reachable=prior_crash_reachable,
        witness_class=witness_class,
        witness_id=(
            f"unit.{code.value}"
            if witness_class is WitnessClass.INTERNAL_INVARIANT
            else f"witness.{code.value}"
        ),
        witness_note=witness_note,
        terminal_result=terminal_result,
        night_loss=night_loss,
        description=description,
        process_exit=process_exit,
    )


_DESCRIPTIONS: Mapping[RefusalCode, str] = MappingProxyType(
    {
        RefusalCode.LEDGER_MISSING: "the pinned non-genesis ledger is absent",
        RefusalCode.LEDGER_MALFORMED: "ledger, malformed receipt, or head-pin schema is malformed",
        RefusalCode.LEDGER_CHAIN_CONFLICT: "sequence or predecessor linkage is not one linear chain",
        RefusalCode.LEDGER_ATTEMPT_CONFLICT: "an attempt has duplicate or conflicting state transitions",
        RefusalCode.LEDGER_BRACKET_SESSION_CONFLICT: "a bracket session has duplicate, reordered, or conflicting state transitions",
        RefusalCode.LEDGER_BRACKET_SLOT_CLAIMED: "a bracket session slot has conflicting durable claims",
        RefusalCode.LEDGER_BRACKET_SESSION_OPEN: "an open bracket session has not finalized both slots or recorded a governed abort",
        RefusalCode.LEDGER_CONTENT_CONFLICT: "one content identity has conflicting authenticated classifications",
        RefusalCode.LEDGER_PENDING: "at least one reservation is unresolved",
        RefusalCode.LEDGER_HEAD_UNCOMMITTED: "the head pin differs from the Git HEAD bytes",
        RefusalCode.LEDGER_HEAD_MISMATCH: "the physical head differs from the committed pin",
        RefusalCode.LEDGER_ROLLBACK: "the physical ledger is a proper prefix of the pinned head",
        RefusalCode.LEDGER_RECOVERY_REQUIRED: "the ledger has an unresolved append intent or non-admitted tail residue",
        RefusalCode.LEDGER_OPERATION_CONFLICT: "durable operation semantic content differs from its completed target commitment",
        RefusalCode.LEDGER_UNGOVERNED_BUSINESS: "a business receipt after protocol activation has no completed append intent",
        RefusalCode.LEDGER_BASELINE_MISSING: "the acceptance cutoff is not in the current chain",
        RefusalCode.LEDGER_CUSTODY_INVALID: "receipt-bound evidence bytes are absent or hash-invalid",
        RefusalCode.LEDGER_SNAPSHOT_REQUIRED: "claim evaluation did not receive one immutable snapshot",
        RefusalCode.LEDGER_OFF_LEDGER_ARTIFACT: "a calibration artifact is not registered in the snapshot",
        RefusalCode.OBSERVATION_UNCLASSIFIABLE: "a governed observation has no ruled disposition",
        RefusalCode.LIVE_WRITER_CONTENTION: "another process holds the calibration writer lease",
        RefusalCode.UNSAFE_LOCK_INODE: "ledger lock cannot be opened safely as one dedicated regular non-aliased inode",
        RefusalCode.PHYSICAL_LEDGER_UNREADABLE: "physical ledger is unreadable",
        RefusalCode.LEGACY_JOURNAL_UNREADABLE: "legacy append journal is unreadable",
        RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT: "legacy append journal archive conflicts",
        RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED: "legacy append journal could not be archived",
        RefusalCode.TAIL_REQUIRES_ABANDON: "ledger tail requires operator-attested abandon-tail",
        RefusalCode.INTENT_TARGET_MALFORMED: "durable append intent commits a malformed target",
        RefusalCode.RECOVERY_NONCONVERGENT: "ledger recovery did not converge",
        RefusalCode.RECOVERY_CREDENTIALS_INVALID: "recovery identity and attestation reason must be nonempty",
        RefusalCode.ABANDON_CREDENTIALS_INVALID: "operator identity, reason code, and attestation reason are required",
        RefusalCode.ABANDON_PIN_MISMATCH: "operator abandonment requires the committed head digest at its pinned sequence",
        RefusalCode.ABANDON_ACTIVE_INTENT: "a durable append intent is irrevocable; run deterministic repair",
        RefusalCode.ABANDON_NOT_CLEAN: "operator abandonment did not produce a clean ledger",
        RefusalCode.HEAD_PIN_UNREADABLE: "head pin is unreadable",
        RefusalCode.HEAD_PIN_MALFORMED: "head pin is malformed",
        RefusalCode.HEAD_PIN_NOT_COMMITTED: "head pin is not committed at Git HEAD",
        RefusalCode.RESERVATION_INPUT_INVALID: "bracket session reservation is malformed",
        RefusalCode.RESERVATION_HEAD_MISMATCH: "physical ledger head differs from the committed pin",
        RefusalCode.RESERVATION_IDENTITY_CONFLICT: "bracket session identity conflicts with ledger",
        RefusalCode.RESERVED_SLOT_MISMATCH: "capture does not match the exact reserved bracket session slot",
        RefusalCode.SESSION_NOT_FOUND: "bracket session is not present in the ledger",
        RefusalCode.SESSION_NOT_OPEN: "bracket session is not open",
        RefusalCode.SLOT_ORDER_CONFLICT: "bracket session slot is not the governed next slot",
        RefusalCode.CLAIM_ID_INVALID: "bracket slot claim identity is not the deterministic policy identity",
        RefusalCode.FINALIZATION_BINDING_CONFLICT: "slot finalization conflicts with the reserved session binding",
        RefusalCode.SESSION_NOT_TERMINAL: "bracket session is not terminal; use terminal_head_pin_for_session only after closure",
        RefusalCode.SESSION_TERMINAL_NOT_HEAD: "session closure is not the terminal ledger head",
        RefusalCode.CUSTODY_PARTIAL: "partial capture custody requires abort-session",
        RefusalCode.CUSTODY_UNREADABLE: "capture custody is unreadable or unauthenticated",
        RefusalCode.CUSTODY_COMPLETE_USE_RESUME: "complete capture custody requires resume-finalize",
        RefusalCode.PLAN_UNREADABLE: "frozen reservation plan is unreadable",
        RefusalCode.PLAN_HASH_MISMATCH: "frozen reservation plan does not match the reserved digest",
        RefusalCode.PRE_RESERVE_NOT_READY: "pre-reserve readiness predicate is not satisfied",
        RefusalCode.PRE_SLOT_NOT_READY: "pre-slot readiness predicate is not satisfied",
        RefusalCode.TERMINAL_NOT_READY: "terminal readiness predicate is not satisfied",
        RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED: "physical head does not require pin advancement",
        RefusalCode.PIN_ADVANCEMENT_UNSAFE: "physical head cannot be advanced by the guarded procedure",
        RefusalCode.PIN_CANDIDATE_MISMATCH: "supplied head-pin candidate does not equal the authenticated physical head",
        RefusalCode.RESERVATION_JSON_INVALID: "reservation JSON input is unreadable or not an object",
        RefusalCode.WRITER_BRACKET_ARGUMENTS: "session id, slot, and attempt id must be supplied together",
        RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT: "bracket session parameters apply only to live capture",
        RefusalCode.FROZEN_PROTOCOL_INVALID: "frozen powermetrics protocol is missing, incomplete, or inconsistent",
        RefusalCode.REDERIVE_OUTPUT_REQUIRED: "rederive-from requires an output path",
        RefusalCode.REDERIVE_FAILED: "artifact re-derivation refused its source",
        RefusalCode.OUTPUT_REQUIRES_REDERIVE: "output requires rederive-from",
        RefusalCode.QUIET_MAC_AUTH_REQUIRED: "live calibration requires lead-owned quiet-machine authorization",
        RefusalCode.POWER_POLICY_REQUIRED: "power policy is a required binding",
        RefusalCode.DISPLAY_ARM_FAILED: "display sleep arm failed after the bracket claim",
        RefusalCode.SAMPLER_NEVER_READY: "powermetrics sampler never became ready",
        RefusalCode.ROLLOVER_GATE_TIMEOUT: "powermetrics rollover gate timed out",
    }
)


_REPAIR = {
    RefusalCode.LEDGER_RECOVERY_REQUIRED,
}
_ABANDON = {
    RefusalCode.TAIL_REQUIRES_ABANDON,
    RefusalCode.INTENT_TARGET_MALFORMED,
}
_ABORT = {
    RefusalCode.LEDGER_BRACKET_SESSION_OPEN,
    RefusalCode.CUSTODY_PARTIAL,
    RefusalCode.RESERVATION_IDENTITY_CONFLICT,
    RefusalCode.RESERVED_SLOT_MISMATCH,
    RefusalCode.SLOT_ORDER_CONFLICT,
    RefusalCode.DISPLAY_ARM_FAILED,
    RefusalCode.SAMPLER_NEVER_READY,
    RefusalCode.ROLLOVER_GATE_TIMEOUT,
}
_RESUME = {RefusalCode.CUSTODY_COMPLETE_USE_RESUME}
_ADVANCE = {
    RefusalCode.LEDGER_HEAD_MISMATCH,
    RefusalCode.LEDGER_HEAD_UNCOMMITTED,
    RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED,
}
_PREFLIGHT = {
    RefusalCode.RESERVATION_INPUT_INVALID,
    RefusalCode.RESERVATION_JSON_INVALID,
    RefusalCode.WRITER_BRACKET_ARGUMENTS,
    RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT,
    RefusalCode.FROZEN_PROTOCOL_INVALID,
    RefusalCode.REDERIVE_OUTPUT_REQUIRED,
    RefusalCode.REDERIVE_FAILED,
    RefusalCode.OUTPUT_REQUIRES_REDERIVE,
    RefusalCode.QUIET_MAC_AUTH_REQUIRED,
    RefusalCode.POWER_POLICY_REQUIRED,
    RefusalCode.PLAN_UNREADABLE,
    RefusalCode.PLAN_HASH_MISMATCH,
    RefusalCode.PRE_RESERVE_NOT_READY,
    RefusalCode.PRE_SLOT_NOT_READY,
    RefusalCode.TERMINAL_NOT_READY,
}
_RECOVERY_COMPONENT = {
    RefusalCode.PHYSICAL_LEDGER_UNREADABLE,
    RefusalCode.LEGACY_JOURNAL_UNREADABLE,
    RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT,
    RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED,
    RefusalCode.TAIL_REQUIRES_ABANDON,
    RefusalCode.INTENT_TARGET_MALFORMED,
    RefusalCode.RECOVERY_NONCONVERGENT,
    RefusalCode.RECOVERY_CREDENTIALS_INVALID,
    RefusalCode.ABANDON_CREDENTIALS_INVALID,
    RefusalCode.ABANDON_PIN_MISMATCH,
    RefusalCode.ABANDON_ACTIVE_INTENT,
    RefusalCode.ABANDON_NOT_CLEAN,
    RefusalCode.HEAD_PIN_UNREADABLE,
    RefusalCode.HEAD_PIN_MALFORMED,
    RefusalCode.HEAD_PIN_NOT_COMMITTED,
    RefusalCode.SESSION_NOT_FOUND,
    RefusalCode.SESSION_NOT_OPEN,
    RefusalCode.SESSION_NOT_TERMINAL,
    RefusalCode.SESSION_TERMINAL_NOT_HEAD,
    RefusalCode.CUSTODY_PARTIAL,
    RefusalCode.CUSTODY_UNREADABLE,
    RefusalCode.CUSTODY_COMPLETE_USE_RESUME,
    RefusalCode.PLAN_UNREADABLE,
    RefusalCode.PLAN_HASH_MISMATCH,
    RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED,
    RefusalCode.PIN_ADVANCEMENT_UNSAFE,
    RefusalCode.PIN_CANDIDATE_MISMATCH,
}
_RESERVATION_COMPONENT = {
    RefusalCode.RESERVATION_INPUT_INVALID,
    RefusalCode.RESERVATION_HEAD_MISMATCH,
    RefusalCode.RESERVATION_IDENTITY_CONFLICT,
    RefusalCode.RESERVATION_JSON_INVALID,
    RefusalCode.PRE_RESERVE_NOT_READY,
}
_WRITER_COMPONENT = {
    RefusalCode.RESERVED_SLOT_MISMATCH,
    RefusalCode.SLOT_ORDER_CONFLICT,
    RefusalCode.CLAIM_ID_INVALID,
    RefusalCode.FINALIZATION_BINDING_CONFLICT,
    RefusalCode.PRE_SLOT_NOT_READY,
    RefusalCode.WRITER_BRACKET_ARGUMENTS,
    RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT,
    RefusalCode.FROZEN_PROTOCOL_INVALID,
    RefusalCode.REDERIVE_OUTPUT_REQUIRED,
    RefusalCode.REDERIVE_FAILED,
    RefusalCode.OUTPUT_REQUIRES_REDERIVE,
    RefusalCode.QUIET_MAC_AUTH_REQUIRED,
    RefusalCode.POWER_POLICY_REQUIRED,
    RefusalCode.DISPLAY_ARM_FAILED,
    RefusalCode.SAMPLER_NEVER_READY,
    RefusalCode.ROLLOVER_GATE_TIMEOUT,
}


_CORRUPTION_BACKSTOPS = {
    RefusalCode.LEDGER_MISSING,
    RefusalCode.LEDGER_MALFORMED,
    RefusalCode.LEDGER_CHAIN_CONFLICT,
    RefusalCode.LEDGER_ATTEMPT_CONFLICT,
    RefusalCode.LEDGER_BRACKET_SESSION_CONFLICT,
    RefusalCode.LEDGER_CONTENT_CONFLICT,
    RefusalCode.LEDGER_ROLLBACK,
    RefusalCode.LEDGER_OPERATION_CONFLICT,
    RefusalCode.LEDGER_UNGOVERNED_BUSINESS,
    RefusalCode.LEDGER_CUSTODY_INVALID,
    RefusalCode.UNSAFE_LOCK_INODE,
    RefusalCode.PHYSICAL_LEDGER_UNREADABLE,
    RefusalCode.LEGACY_JOURNAL_UNREADABLE,
    RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT,
    RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED,
    RefusalCode.INTENT_TARGET_MALFORMED,
    RefusalCode.RECOVERY_NONCONVERGENT,
    RefusalCode.ABANDON_NOT_CLEAN,
    RefusalCode.HEAD_PIN_UNREADABLE,
    RefusalCode.HEAD_PIN_MALFORMED,
    RefusalCode.CUSTODY_UNREADABLE,
    RefusalCode.FINALIZATION_BINDING_CONFLICT,
}

_INTERNAL_INVARIANTS: Mapping[RefusalCode, str] = MappingProxyType(
    {
        RefusalCode.LEDGER_SNAPSHOT_REQUIRED: (
            "in-memory claim-evaluation argument guard; public runners load the "
            "immutable snapshot before evaluation, so no durable state omits it"
        ),
        RefusalCode.LEDGER_OFF_LEDGER_ARTIFACT: (
            "low-level evaluator candidate/snapshot equality guard; public bundle "
            "evaluation discovers its candidate set only from the authenticated "
            "snapshot, mapping missing custody earlier instead"
        ),
        RefusalCode.LEDGER_BRACKET_SLOT_CLAIMED: (
            "inner duplicate-claim programming guard; an exact durable claim returns "
            "idempotently and every nonmatching claim is rejected before this branch"
        ),
    }
)


def _route(code: RefusalCode) -> RefusalRecord:
    kwargs: dict[str, Any] = {}
    if code in _CORRUPTION_BACKSTOPS:
        kwargs.update(
            witness_class=WitnessClass.CORRUPTION_BACKSTOP,
            witness_note="reachable only from corrupted or hostile durable state",
        )
    elif code in _INTERNAL_INVARIANTS:
        kwargs.update(
            witness_class=WitnessClass.INTERNAL_INVARIANT,
            witness_note=_INTERNAL_INVARIANTS[code],
            exit_kind="internal-invariant",
            exit_id="internal-invariant",
            command="",
            runbook_anchor="",
        )
    if code is RefusalCode.CLAIM_ID_INVALID:
        kwargs.update(
            witness_class=WitnessClass.OPERATIONAL,
            witness_note=(
                "reachable from an authenticated durable slot claim whose nonempty "
                "claim id does not match the deterministic policy identity"
            ),
        )
    if code in _RECOVERY_COMPONENT:
        kwargs.update(component="recovery-cli", phase="recovery")
    elif code in _RESERVATION_COMPONENT:
        kwargs.update(component="reservation-cli", phase="pre-reserve")
    elif code in _WRITER_COMPONENT:
        kwargs.update(component="writer", phase="pre-slot-or-capture")
    if code in _REPAIR:
        kwargs.update(
            exit_kind="repair",
            exit_id="repair",
            command="recover_calibration_ledger.py repair",
            prior_crash_reachable=True,
            night_loss=False,
            terminal_result=TerminalResult.OPERATION_COMPLETED,
        )
    elif code in _ABANDON:
        kwargs.update(
            exit_kind="abandon-tail",
            exit_id="abandon-tail-then-repair",
            command="recover_calibration_ledger.py abandon-tail --operator-identity ID --attestation-reason REASON",
            prior_crash_reachable=True,
            night_loss=False,
            terminal_result=TerminalResult.OPERATION_COMPLETED,
        )
    elif code in _ABORT:
        kwargs.update(
            exit_kind="abort-session",
            exit_id="abort-session",
            command="recover_calibration_ledger.py abort-session --session-id SESSION --plan PLAN --reason REASON",
            prior_crash_reachable=code in {RefusalCode.CUSTODY_PARTIAL},
            night_loss=True,
            terminal_result=TerminalResult.SESSION_ABORTED,
        )
    elif code in _RESUME:
        kwargs.update(
            exit_kind="resume-finalize",
            exit_id="resume-finalize",
            command="recover_calibration_ledger.py resume-finalize --session-id SESSION --slot SLOT --plan PLAN",
            prior_crash_reachable=True,
            night_loss=False,
            terminal_result=TerminalResult.OPERATION_COMPLETED,
        )
    elif code == RefusalCode.LIVE_WRITER_CONTENTION:
        kwargs.update(
            component="lease",
            phase="writer-lease",
            retry_class="after-live-holder-exits",
            exit_kind="wait-live-writer",
            exit_id="live-writer-contention",
            command="recover_calibration_ledger.py session-status --session-id SESSION --plan PLAN",
            night_loss=False,
            terminal_result=TerminalResult.OPERATION_COMPLETED,
        )
    elif code in _ADVANCE:
        kwargs.update(
            exit_kind="advance-head-pin",
            exit_id="guarded-head-pin-advancement",
            command="recover_calibration_ledger.py advance-head-pin --session-id SESSION --expected-sequence N --expected-digest SHA --operator-identity ID --attestation-reason REASON --execute",
            prior_crash_reachable=True,
            night_loss=True,
        )
    elif code in _PREFLIGHT:
        kwargs.update(
            phase="preflight",
            retry_class="after-correction",
            exit_kind="fix-preflight",
            exit_id="correct-preflight",
            command="recover_calibration_ledger.py readiness --phase pre-reserve --session-id SESSION --plan PLAN",
            night_loss=False,
            terminal_result=TerminalResult.READY_TO_ARM,
        )
    if code is RefusalCode.CUSTODY_UNREADABLE:
        kwargs.update(
            prior_crash_reachable=True,
            exit_kind="custody-hard-stop-preserved",
            witness_note=(
                "reachable from hostile custody or a crash during a governed "
                "artifact write; bytes remain quarantined and non-finalizable"
            ),
        )
    return _record(code, _DESCRIPTIONS[code], **kwargs)


REFUSAL_INVENTORY: tuple[RefusalRecord, ...] = tuple(_route(code) for code in RefusalCode)
REFUSAL_BY_CODE: Mapping[RefusalCode, RefusalRecord] = MappingProxyType(
    {record.code: record for record in REFUSAL_INVENTORY}
)


def refusal_record(code: RefusalCode | str) -> RefusalRecord:
    return REFUSAL_BY_CODE[RefusalCode(code)]


def refusal_payload(
    code: RefusalCode | str,
    *,
    context: Mapping[str, Any] | None = None,
    terminal_result: TerminalResult | str | None = None,
) -> dict[str, Any]:
    record = refusal_record(code)
    payload: dict[str, Any] = {
        "status": "refused",
        "code": record.code.value,
        "exit_id": record.exit_id,
        "arm_blocked": record.arm_blocked,
        "next_command": record.command,
    }
    observed_terminal = terminal_result
    if (
        observed_terminal is None
        and record.terminal_result is TerminalResult.NIGHT_STOPPED_PRESERVED
    ):
        # A hard-stop refusal is itself the mapped terminal action. Other
        # registry terminal results describe work still to be executed and
        # must not be projected as if it had already happened.
        observed_terminal = record.terminal_result
    if observed_terminal is not None:
        payload["terminal_result"] = (
            observed_terminal.value
            if isinstance(observed_terminal, TerminalResult)
            else str(observed_terminal)
        )
    if context:
        payload["context"] = dict(context)
    return payload


def explain_payload(code: RefusalCode | str) -> dict[str, Any]:
    """Return the stable four-field operator explanation required by D-117."""

    payload = refusal_payload(code)
    payload.pop("status")
    payload.pop("terminal_result", None)
    return payload


def emit_refusal(
    code: RefusalCode | str,
    *,
    context: Mapping[str, Any] | None = None,
    terminal_result: TerminalResult | str | None = None,
    stream: TextIO,
) -> int:
    record = refusal_record(code)
    print(
        json.dumps(
            refusal_payload(
                record.code,
                context=context,
                terminal_result=terminal_result,
            ),
            sort_keys=True,
        ),
        file=stream,
    )
    return record.process_exit


__all__ = [
    "REFUSAL_BY_CODE",
    "REFUSAL_INVENTORY",
    "RefusalCode",
    "RefusalRecord",
    "TerminalResult",
    "WitnessClass",
    "emit_refusal",
    "explain_payload",
    "refusal_payload",
    "refusal_record",
]
