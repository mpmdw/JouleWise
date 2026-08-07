#!/usr/bin/env python3
"""Reserve one governed two-slot calibration bracket session.

The capability advances the physical ledger while deliberately leaving the
committed head pin unchanged until the post slot is finalized. Execution is
explicit so argument validation cannot accidentally arm a quiet window.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import (  # noqa: E402
    BRACKET_SESSION_SCHEMA,
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    CalibrationLedgerError,
    append_bracket_session_receipt,
    canonical_json_bytes,
    validate_bracket_session_reservation_inputs,
)


OUTPUT_SCHEMA = "joulewise.calibration_window_bracket_reservation.v1"


def _json_object(path: Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--evidence-root-id", required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--pre-attempt-id", required=True)
    parser.add_argument("--post-attempt-id", required=True)
    parser.add_argument("--pre-custody-locator", required=True)
    parser.add_argument("--post-custody-locator", required=True)
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        epoch = _json_object(args.identity_epoch_json)
        t1 = _json_object(args.t1_bindings_json)
        slots = {
            "pre": {
                "attempt_id": args.pre_attempt_id,
                "custody_locator": args.pre_custody_locator,
                "identity_epoch": epoch,
                "t1_bindings": t1,
            },
            "post": {
                "attempt_id": args.post_attempt_id,
                "custody_locator": args.post_custody_locator,
                "identity_epoch": epoch,
                "t1_bindings": t1,
            },
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
            )
        )
        if not args.execute:
            output = {
                "schema_version": OUTPUT_SCHEMA,
                "status": "validated_not_reserved",
                "session_schema": BRACKET_SESSION_SCHEMA,
                **dict(session_identity),
                "slot_attempt_ids": {
                    role: slot["attempt_id"]
                    for role, slot in normalized_slots.items()
                },
            }
        else:
            receipt = append_bracket_session_receipt(
                args.ledger,
                session_id=args.session_id,
                window_id=args.window_id,
                plan_id=args.plan_id,
                plan_sha256=args.plan_sha256,
                evidence_root_id=args.evidence_root_id,
                runs_root=args.runs_root,
                slots=slots,
                head_pin_path=args.head_pin,
                require_committed_pin=not args.allow_uncommitted_pin_for_test,
                repo_root=REPO_ROOT,
            )
            output = {
                "schema_version": OUTPUT_SCHEMA,
                "status": "reserved",
                "receipt": json.loads(canonical_json_bytes(receipt)),
                "terminal_head_pin": None,
                "terminal_head_pin_status": "deferred_until_post_finalization",
            }
    except (CalibrationLedgerError, OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
