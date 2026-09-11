#!/usr/bin/env python3
"""Reserve one governed ordered-slot calibration ledger session.

Two kinds exist.  A ``bracket`` session declares exactly the two slots ``pre``
and ``post`` and keeps this tool's original flags and receipt bytes unchanged.
A ``derivation`` session declares ``--slot-count N`` slots named ``d01..dNN``
and takes its per-slot attempt ids and custody locators as repeated
``--slot-attempt-id`` / ``--slot-custody-locator`` flags, in declared order.

The capability advances the physical ledger while deliberately leaving the
committed head pin unchanged until the last declared slot is finalized (or the
session aborts). Execution is explicit so argument validation cannot
accidentally arm a quiet window.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_exits import RefusalCode, emit_refusal  # noqa: E402
from joulewise.calibration_ledger import (  # noqa: E402
    BRACKET_SESSION_SCHEMA,
    BRACKET_SESSION_SLOTS,
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    SESSION_KIND_BRACKET,
    SESSION_KIND_DERIVATION,
    SESSION_KINDS,
    derivation_session_slots,
    CalibrationLedgerError,
    CalibrationWriterLease,
    append_bracket_session_receipt,
    calibration_readiness,
    calibration_session_status,
    canonical_json_bytes,
    validate_bracket_session_reservation_inputs,
)


OUTPUT_SCHEMA = "joulewise.calibration_window_bracket_reservation.v1"


def _json_object(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_JSON_INVALID,
            context={"path": str(path)},
        ) from exc
    if not isinstance(value, Mapping):
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_JSON_INVALID,
            context={"path": str(path)},
        )
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument(
        "--plan",
        type=Path,
        help="exact frozen plan bytes; required by the production runbook",
    )
    parser.add_argument("--evidence-root-id", required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument(
        "--session-kind",
        choices=SESSION_KINDS,
        default=SESSION_KIND_BRACKET,
        help="bracket (pre/post, the default) or derivation (d01..dNN)",
    )
    parser.add_argument(
        "--slot-count",
        type=int,
        help="derivation only: how many ordered slots d01..dNN to declare",
    )
    parser.add_argument("--pre-attempt-id", help="bracket only")
    parser.add_argument("--post-attempt-id", help="bracket only")
    parser.add_argument("--pre-custody-locator", help="bracket only")
    parser.add_argument("--post-custody-locator", help="bracket only")
    parser.add_argument(
        "--slot-attempt-id",
        action="append",
        default=[],
        help="derivation only: repeat once per declared slot, in order",
    )
    parser.add_argument(
        "--slot-custody-locator",
        action="append",
        default=[],
        help="derivation only: repeat once per declared slot, in order",
    )
    parser.add_argument("--identity-epoch-json", type=Path, required=True)
    parser.add_argument("--t1-bindings-json", type=Path, required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="append the capability; without this flag only validate inputs",
    )
    parser.add_argument(
        "--allow-uncommitted-pin-for-test",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--test-writer-crash-authorization",
        type=Path,
        help=argparse.SUPPRESS,
    )
    return parser


def _declared_slot_sources(
    args: argparse.Namespace,
) -> tuple[tuple[str, ...], list[tuple[str, str]]]:
    """Map this invocation's flags onto the ordered declared slot list.

    The bracket kind reads the four original per-slot flags, so its command
    line is unchanged; the derivation kind reads the repeated list flags, one
    entry per declared slot, in declared order.
    """

    bracket_flags = (
        args.pre_attempt_id,
        args.post_attempt_id,
        args.pre_custody_locator,
        args.post_custody_locator,
    )
    list_flags = (args.slot_attempt_id, args.slot_custody_locator)
    if args.session_kind == SESSION_KIND_BRACKET:
        if args.slot_count is not None or any(list_flags):
            raise CalibrationLedgerError(
                RefusalCode.RESERVATION_INPUT_INVALID,
                context={"reason": "bracket_session_takes_pre_post_flags"},
            )
        if any(value is None for value in bracket_flags):
            raise CalibrationLedgerError(
                RefusalCode.RESERVATION_INPUT_INVALID,
                context={"reason": "bracket_session_slot_flags_missing"},
            )
        return BRACKET_SESSION_SLOTS, [
            (args.pre_attempt_id, args.pre_custody_locator),
            (args.post_attempt_id, args.post_custody_locator),
        ]
    if any(value is not None for value in bracket_flags):
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"reason": "derivation_session_takes_slot_list_flags"},
        )
    if args.slot_count is None:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"reason": "derivation_session_requires_slot_count"},
        )
    declared = derivation_session_slots(args.slot_count)
    if (
        len(args.slot_attempt_id) != len(declared)
        or len(args.slot_custody_locator) != len(declared)
    ):
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={
                "reason": "declared_slot_flag_count_mismatch",
                "slot_count": args.slot_count,
                "attempt_ids": len(args.slot_attempt_id),
                "custody_locators": len(args.slot_custody_locator),
            },
        )
    return declared, list(zip(args.slot_attempt_id, args.slot_custody_locator))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
        _configure_writer_crash_authorization,
    )

    _configure_writer_crash_authorization(
        args.test_writer_crash_authorization,
        entry_point=Path(__file__),
    )
    try:
        epoch = _json_object(args.identity_epoch_json)
        t1 = _json_object(args.t1_bindings_json)
        if args.plan is not None:
            try:
                plan_raw = args.plan.read_bytes()
                plan_value = json.loads(plan_raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CalibrationLedgerError(RefusalCode.PLAN_UNREADABLE) from exc
            if (
                not isinstance(plan_value, Mapping)
                or plan_value.get("plan_id") != args.plan_id
                or hashlib.sha256(plan_raw).hexdigest() != args.plan_sha256
            ):
                raise CalibrationLedgerError(RefusalCode.PLAN_HASH_MISMATCH)
        declared, slot_sources = _declared_slot_sources(args)
        slots = {
            role: {
                "attempt_id": attempt_id,
                "custody_locator": custody_locator,
                "identity_epoch": epoch,
                "t1_bindings": t1,
            }
            for role, (attempt_id, custody_locator) in zip(declared, slot_sources)
        }
        session_identity, normalized_slots = (
            validate_bracket_session_reservation_inputs(
                session_id=args.session_id,
                window_id=args.window_id,
                plan_id=args.plan_id,
                plan_sha256=args.plan_sha256,
                evidence_root_id=args.evidence_root_id,
                runs_root=args.runs_root,
                slots=slots,
                session_kind=args.session_kind,
                declared_slots=declared,
            )
        )
        if not args.execute:
            output = {
                "schema_version": OUTPUT_SCHEMA,
                "status": "validated_not_reserved",
                "session_schema": BRACKET_SESSION_SCHEMA,
                **dict(session_identity),
                "session_kind": args.session_kind,
                "declared_slots": list(declared),
                "slot_attempt_ids": {
                    role: slot["attempt_id"]
                    for role, slot in normalized_slots.items()
                },
            }
        else:
            from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
                WriterStage,
                _writer_stage,
            )

            _writer_stage(WriterStage.BEFORE_PRE_RESERVE_READINESS)
            with CalibrationWriterLease(args.ledger):
                readiness = calibration_readiness(
                    args.ledger,
                    args.head_pin,
                    phase="pre-reserve",
                    enforcing_under_lease=True,
                    require_committed_pin=not args.allow_uncommitted_pin_for_test,
                    repo_root=REPO_ROOT,
                )
                if readiness.status != "ready":
                    try:
                        calibration_session_status(
                            args.ledger,
                            args.head_pin,
                            session_id=args.session_id,
                            plan_path=args.plan,
                            require_committed_pin=not args.allow_uncommitted_pin_for_test,
                            repo_root=REPO_ROOT,
                        )
                    except CalibrationLedgerError as exc:
                        if exc.code == RefusalCode.SESSION_NOT_FOUND:
                            raise CalibrationLedgerError(
                                readiness.refusal_code
                                or RefusalCode.PRE_RESERVE_NOT_READY
                            ) from exc
                        raise
                else:
                    _writer_stage(WriterStage.AFTER_PRE_RESERVE_READINESS)
                    print(
                        json.dumps(
                            {
                                "event": "calibration_pre_reserve_authorized",
                                "session_id": args.session_id,
                            },
                            sort_keys=True,
                        ),
                        file=sys.stderr,
                        flush=True,
                    )
                receipt = append_bracket_session_receipt(
                    args.ledger,
                    session_id=args.session_id,
                    window_id=args.window_id,
                    plan_id=args.plan_id,
                    plan_sha256=args.plan_sha256,
                    evidence_root_id=args.evidence_root_id,
                    runs_root=args.runs_root,
                    slots=slots,
                    session_kind=args.session_kind,
                    declared_slots=declared,
                    head_pin_path=args.head_pin,
                    require_committed_pin=not args.allow_uncommitted_pin_for_test,
                    repo_root=REPO_ROOT,
                    _stage_boundary=lambda boundary: _writer_stage(
                        {
                            "intent-write": WriterStage.RESERVATION_INTENT_WRITE,
                            "intent-fsynced": WriterStage.RESERVATION_INTENT_FSYNCED,
                            "target-write": WriterStage.RESERVATION_TARGET_WRITE,
                            "target-fsynced": WriterStage.RESERVATION_TARGET_FSYNCED,
                        }[boundary]
                    ),
                )
                _writer_stage(WriterStage.RESERVATION_RETURNED)
            output = {
                "schema_version": OUTPUT_SCHEMA,
                "status": "reserved",
                "terminal_result": "operation_completed",
                "receipt": json.loads(canonical_json_bytes(receipt)),
                "terminal_head_pin": None,
                "terminal_head_pin_status": "deferred_until_post_finalization"
                if args.session_kind == SESSION_KIND_BRACKET
                else "deferred_until_terminal_slot_finalization",
            }
    except CalibrationLedgerError as exc:
        return emit_refusal(
            exc.code or RefusalCode.RESERVATION_INPUT_INVALID,
            context=dict(exc.context) | {"detail": str(exc)},
            stream=sys.stderr,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return emit_refusal(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"detail": str(exc)},
            stream=sys.stderr,
        )
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
