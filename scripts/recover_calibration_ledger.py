#!/usr/bin/env python3
"""Inspect and repair the ledger-resident calibration append protocol."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    CalibrationLedgerInspection,
    abandon_calibration_ledger_tail,
    inspect_calibration_ledger,
    repair_calibration_ledger,
)


def _payload(inspection: CalibrationLedgerInspection) -> dict[str, Any]:
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
    parser.add_argument(
        "--allow-uncommitted-head-pin",
        action="store_true",
        help="test/development only; production operator use must omit this flag",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="report maximal-chain recovery state")
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            inspection = inspect_calibration_ledger(args.ledger)
        elif args.command == "repair":
            inspection = repair_calibration_ledger(
                args.ledger,
                engine_identity=args.engine_identity,
                attestation_reason=args.attestation_reason,
            )
        else:
            inspection = abandon_calibration_ledger_tail(
                args.ledger,
                operator_identity=args.operator_identity,
                attestation_reason=args.attestation_reason,
                reason_code=args.reason_code,
                head_pin_path=args.head_pin,
                require_committed_pin=not args.allow_uncommitted_head_pin,
                repo_root=REPO_ROOT,
            )
    except CalibrationLedgerError as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}))
        return 2
    print(json.dumps({"status": "ok", "inspection": _payload(inspection)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
