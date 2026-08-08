#!/usr/bin/env python3
"""Inspect and repair the ledger-resident calibration append protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_exits import (  # noqa: E402
    RefusalCode,
    emit_refusal,
    explain_payload,
)
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    CalibrationLedgerInspection,
    abort_calibration_session,
    advance_calibration_head_pin,
    abandon_calibration_ledger_tail,
    calibration_readiness,
    calibration_session_status,
    canonical_json_bytes,
    inspect_calibration_ledger,
    load_calibration_ledger_snapshot,
    repair_calibration_ledger,
    resume_finalize_bracket_session,
    terminal_head_pin_for_session,
)


_AUDIT_REFUSAL_PRECEDENCE = (
    RefusalCode.LEDGER_MISSING,
    RefusalCode.LEDGER_MALFORMED,
    RefusalCode.LEDGER_CHAIN_CONFLICT,
    RefusalCode.LEDGER_UNGOVERNED_BUSINESS,
    RefusalCode.LEDGER_OPERATION_CONFLICT,
    RefusalCode.LEDGER_CUSTODY_INVALID,
    RefusalCode.LEDGER_BRACKET_SESSION_CONFLICT,
    RefusalCode.LEDGER_ATTEMPT_CONFLICT,
    RefusalCode.LEDGER_CONTENT_CONFLICT,
    RefusalCode.LEDGER_PENDING,
    RefusalCode.LEDGER_BRACKET_SESSION_OPEN,
    RefusalCode.LEDGER_RECOVERY_REQUIRED,
    RefusalCode.LEDGER_HEAD_UNCOMMITTED,
    RefusalCode.LEDGER_HEAD_MISMATCH,
    RefusalCode.LEDGER_ROLLBACK,
    RefusalCode.LEDGER_BASELINE_MISSING,
)

_AUTOMATIC_ABORT_REFUSALS = {
    "display_arm_failed": RefusalCode.DISPLAY_ARM_FAILED,
    "powermetrics_never_ready": RefusalCode.SAMPLER_NEVER_READY,
    "pulse_calibration_rollover_gate_timeout": RefusalCode.ROLLOVER_GATE_TIMEOUT,
}


def _audit_refusal(
    reasons: tuple[str, ...], *, active_operation_id: str | None = None
) -> RefusalCode:
    available = {RefusalCode(reason) for reason in reasons}
    # A valid intent plus a torn target is the repairable crash family even
    # though the target fragment is also not a complete JSON record.
    if (
        active_operation_id is not None
        and RefusalCode.LEDGER_RECOVERY_REQUIRED in available
        and RefusalCode.LEDGER_MALFORMED in available
    ):
        return RefusalCode.LEDGER_RECOVERY_REQUIRED
    return next(
        (code for code in _AUDIT_REFUSAL_PRECEDENCE if code in available),
        sorted(available, key=lambda code: code.value)[0],
    )


def _payload(
    inspection: CalibrationLedgerInspection, *, head_pin_path: Path
) -> dict[str, Any]:
    try:
        pin = json.loads(Path(head_pin_path).read_text(encoding="utf-8"))
        pin_pair = (pin.get("sequence"), pin.get("head_digest"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        pin_pair = (None, None)
    physical_pair = (inspection.head_sequence, inspection.head_digest)
    return {
        "state": inspection.state,
        "ledger_id": inspection.ledger_id,
        "head_sequence": inspection.head_sequence,
        "head_digest": inspection.head_digest,
        "valid_end_offset": inspection.valid_end_offset,
        "residue_start_offset": inspection.residue_start_offset,
        "residue_length": inspection.residue_length,
        "residue_sha256": inspection.residue_sha256,
        "active_operation_id": inspection.active_operation_id,
        "active_operation_key": (
            dict(inspection.active_operation_key)
            if inspection.active_operation_key is not None
            else None
        ),
        "target_core_sha256": inspection.target_core_sha256,
        "legacy_journal_path": inspection.legacy_journal_path,
        "legacy_journal_sha256": inspection.legacy_journal_sha256,
        "needs_pin_commit": pin_pair != physical_pair,
        "head_pin_candidate": {
            "sequence": inspection.head_sequence,
            "head_digest": inspection.head_digest,
            "ledger_schema": LEDGER_SCHEMA,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger", type=Path, default=DEFAULT_LEDGER_PATH
    )
    parser.add_argument(
        "--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="report maximal-chain recovery state")
    audit = commands.add_parser(
        "audit", help="authenticate one immutable snapshot and emit its primary refusal"
    )
    audit.add_argument("--baseline-sequence", type=int)
    audit.add_argument("--baseline-digest")
    observation_audit = commands.add_parser(
        "audit-observations",
        help="refuse any post-baseline observation without a ruled classification",
    )
    observation_audit.add_argument("--baseline-sequence", type=int, required=True)
    observation_audit.add_argument("--baseline-digest", required=True)
    repair = commands.add_parser(
        "repair", help="complete the target committed by the locked ledger"
    )
    repair.add_argument(
        "--engine-identity", default="recover_calibration_ledger.py"
    )
    repair.add_argument(
        "--attestation-reason",
        default="operator invoked deterministic ledger-only repair",
    )
    abandon = commands.add_parser(
        "abandon-tail",
        help="authenticate residue after the maximal valid chain",
    )
    abandon.add_argument("--operator-identity", required=True)
    abandon.add_argument("--attestation-reason", required=True)
    abandon.add_argument(
        "--reason-code", default="operator-attested-tail-abandonment"
    )
    explain = commands.add_parser(
        "explain", help="emit the registered governed exit for one refusal code"
    )
    explain.add_argument("code", choices=tuple(code.value for code in RefusalCode))
    readiness = commands.add_parser(
        "readiness", help="early-warning phase-aware readiness; never authorizes ARM"
    )
    readiness.add_argument(
        "--phase", required=True, choices=("pre-reserve", "pre-slot", "terminal")
    )
    readiness.add_argument("--session-id")
    readiness.add_argument("--slot", choices=("pre", "post"))
    readiness.add_argument("--attempt-id")
    readiness.add_argument("--plan", type=Path)
    status = commands.add_parser(
        "session-status", help="derive durable bracket progress in a fresh process"
    )
    status.add_argument("--session-id", required=True)
    status.add_argument("--plan", type=Path, required=True)
    session_refusal = commands.add_parser(
        "session-refusal",
        help="emit the typed automatic refusal recorded by an aborted session",
    )
    session_refusal.add_argument("--session-id", required=True)
    session_refusal.add_argument("--plan", type=Path, required=True)
    validate_slot = commands.add_parser(
        "validate-slot",
        help="authenticate one proposed writer invocation against its reserved slot",
    )
    validate_slot.add_argument("--session-id", required=True)
    validate_slot.add_argument("--slot", choices=("pre", "post"), required=True)
    validate_slot.add_argument("--attempt-id", required=True)
    validate_slot.add_argument("--custody-locator", required=True)
    validate_slot.add_argument("--identity-epoch-json", type=Path, required=True)
    validate_slot.add_argument("--t1-bindings-json", type=Path, required=True)
    terminal_pin = commands.add_parser(
        "terminal-pin", help="derive the authenticated terminal pin for one session"
    )
    terminal_pin.add_argument("--session-id", required=True)
    resume = commands.add_parser(
        "resume-finalize", help="finalize complete authenticated capture custody"
    )
    resume.add_argument("--session-id", required=True)
    resume.add_argument("--slot", choices=("pre", "post"), required=True)
    resume.add_argument("--plan", type=Path, required=True)
    abort = commands.add_parser(
        "abort-session", help="abort an open session while preserving custody"
    )
    abort.add_argument("--session-id", required=True)
    abort.add_argument("--plan", type=Path, required=True)
    abort.add_argument("--reason", required=True)
    advance = commands.add_parser(
        "advance-head-pin", help="guarded desk-only terminal head-pin advancement"
    )
    advance.add_argument("--session-id")
    advance.add_argument("--expected-sequence", type=int, required=True)
    advance.add_argument("--expected-digest", required=True)
    advance.add_argument("--operator-identity", required=True)
    advance.add_argument("--attestation-reason", required=True)
    advance.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "explain":
            print(json.dumps(explain_payload(args.code), sort_keys=True))
            return 0
        if args.command == "inspect":
            inspection = inspect_calibration_ledger(args.ledger)
        elif args.command == "audit":
            snapshot = load_calibration_ledger_snapshot(
                args.ledger,
                args.head_pin,
                baseline_sequence=args.baseline_sequence,
                baseline_digest=args.baseline_digest,
                require_committed_pin=True,
                verify_custody=True,
                repo_root=REPO_ROOT,
            )
            if snapshot.refusal_reasons:
                inspection = inspect_calibration_ledger(args.ledger)
                return emit_refusal(
                    _audit_refusal(
                        snapshot.refusal_reasons,
                        active_operation_id=inspection.active_operation_id,
                    ),
                    context={"refusal_reasons": list(snapshot.refusal_reasons)},
                    stream=sys.stdout,
                )
            print(
                json.dumps(
                    {
                        "status": "ready",
                        "terminal_result": "ready_to_arm",
                        "head_sequence": snapshot.head_sequence,
                        "head_digest": snapshot.head_digest,
                    },
                    sort_keys=True,
                )
            )
            return 0
        elif args.command == "audit-observations":
            snapshot = load_calibration_ledger_snapshot(
                args.ledger,
                args.head_pin,
                baseline_sequence=args.baseline_sequence,
                baseline_digest=args.baseline_digest,
                require_committed_pin=True,
                verify_custody=True,
                repo_root=REPO_ROOT,
            )
            if snapshot.refusal_reasons:
                inspection = inspect_calibration_ledger(args.ledger)
                return emit_refusal(
                    _audit_refusal(
                        snapshot.refusal_reasons,
                        active_operation_id=inspection.active_operation_id,
                    ),
                    context={"refusal_reasons": list(snapshot.refusal_reasons)},
                    stream=sys.stdout,
                )
            unclassifiable = [
                observation.attempt_id
                for observation in snapshot.post_cutoff_live_observations(
                    args.baseline_sequence
                )
                if observation.classification_disposition
                not in {"valid", "systematic-invalid", "ordinary-invalid"}
            ]
            if unclassifiable:
                return emit_refusal(
                    RefusalCode.OBSERVATION_UNCLASSIFIABLE,
                    context={"attempt_ids": unclassifiable},
                    stream=sys.stdout,
                )
            print(
                json.dumps(
                    {"status": "ready", "terminal_result": "ready_to_arm"},
                    sort_keys=True,
                )
            )
            return 0
        elif args.command == "repair":
            inspection = repair_calibration_ledger(
                args.ledger,
                engine_identity=args.engine_identity,
                attestation_reason=args.attestation_reason,
            )
        elif args.command == "abandon-tail":
            inspection = abandon_calibration_ledger_tail(
                args.ledger,
                operator_identity=args.operator_identity,
                attestation_reason=args.attestation_reason,
                reason_code=args.reason_code,
                head_pin_path=args.head_pin,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
        elif args.command == "session-status":
            output = calibration_session_status(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                plan_path=args.plan,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
            print(canonical_json_bytes(output).decode("utf-8"))
            return 0
        elif args.command == "session-refusal":
            output = calibration_session_status(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                plan_path=args.plan,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
            code = _AUTOMATIC_ABORT_REFUSALS.get(str(output.get("abort_reason")))
            if output.get("session_state") != "aborted" or code is None:
                raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
            return emit_refusal(
                code,
                context={"durable_session_status": output},
                stream=sys.stdout,
            )
        elif args.command == "validate-slot":
            from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
                _validate_reserved_bracket_slot,
            )

            try:
                epoch = json.loads(args.identity_epoch_json.read_bytes())
                t1 = json.loads(args.t1_bindings_json.read_bytes())
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CalibrationLedgerError(RefusalCode.RESERVED_SLOT_MISMATCH) from exc
            _validate_reserved_bracket_slot(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                slot=args.slot,
                attempt_id=args.attempt_id,
                custody_locator=args.custody_locator,
                identity_epoch=epoch,
                t1_bindings=t1,
                require_committed_pin=True,
            )
            print(
                json.dumps(
                    {"status": "ready", "terminal_result": "ready_to_arm"},
                    sort_keys=True,
                )
            )
            return 0
        elif args.command == "terminal-pin":
            output = terminal_head_pin_for_session(
                args.ledger, session_id=args.session_id
            )
            print(canonical_json_bytes(output).decode("utf-8"))
            return 0
        elif args.command == "readiness":
            frozen_plan: dict[str, Any] | None = None
            if args.phase == "pre-reserve":
                if args.plan is None or args.session_id is None:
                    raise CalibrationLedgerError(RefusalCode.PLAN_UNREADABLE)
                try:
                    plan_raw = args.plan.read_bytes()
                    plan_value = json.loads(plan_raw)
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise CalibrationLedgerError(RefusalCode.PLAN_UNREADABLE) from exc
                if not isinstance(plan_value, dict) or not isinstance(
                    plan_value.get("plan_id"), str
                ):
                    raise CalibrationLedgerError(RefusalCode.PLAN_UNREADABLE)
                frozen_plan = {
                    "path": str(args.plan),
                    "plan_id": plan_value["plan_id"],
                    "sha256": hashlib.sha256(plan_raw).hexdigest(),
                    "proposed_session_id": args.session_id,
                }
            elif args.plan is not None and args.session_id is not None:
                calibration_session_status(
                    args.ledger,
                    args.head_pin,
                    session_id=args.session_id,
                    plan_path=args.plan,
                    require_committed_pin=True,
                    repo_root=REPO_ROOT,
                )
            result = calibration_readiness(
                args.ledger,
                args.head_pin,
                phase=args.phase,
                session_id=args.session_id,
                slot=args.slot,
                attempt_id=args.attempt_id,
                enforcing_under_lease=False,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            ).as_dict()
            result["early_warning_only"] = True
            result["frozen_plan"] = frozen_plan
            if result["status"] != "ready":
                return emit_refusal(
                    result["refusal_code"] or RefusalCode.PRE_SLOT_NOT_READY,
                    context={"readiness": result},
                    stream=sys.stdout,
                )
            print(json.dumps(result, sort_keys=True))
            return 0
        elif args.command == "resume-finalize":
            from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
                PREFLIGHT_SYSTEMATIC_SCREEN_S,
            )

            output = resume_finalize_bracket_session(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                slot=args.slot,
                plan_path=args.plan,
                systematic_screen_s=PREFLIGHT_SYSTEMATIC_SCREEN_S,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
            print(canonical_json_bytes(output).decode("utf-8"))
            return 0
        elif args.command == "abort-session":
            output = abort_calibration_session(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                reason=args.reason,
                plan_path=args.plan,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
            print(canonical_json_bytes(output).decode("utf-8"))
            return 0
        else:
            output = advance_calibration_head_pin(
                args.ledger,
                args.head_pin,
                session_id=args.session_id,
                expected_sequence=args.expected_sequence,
                expected_digest=args.expected_digest,
                operator_identity=args.operator_identity,
                attestation_reason=args.attestation_reason,
                execute=args.execute,
                require_committed_pin=True,
                repo_root=REPO_ROOT,
            )
            print(canonical_json_bytes(output).decode("utf-8"))
            return 0
    except CalibrationLedgerError as exc:
        return emit_refusal(
            exc.code or RefusalCode.LEDGER_MALFORMED,
            context=dict(exc.context) | {"detail": str(exc)},
            stream=sys.stdout,
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "terminal_result": "operation_completed",
                "inspection": _payload(inspection, head_pin_path=args.head_pin),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
