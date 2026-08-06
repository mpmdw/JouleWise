#!/usr/bin/env python3
"""Prepare or execute the deterministic calibration-ledger genesis import.

Dry-run is the default. It authenticates every supplied custody copy and
prints the complete canonical receipt chain plus the exact candidate head pin
without writing either file. ``--execute`` atomically writes only the ledger;
the lead must review and commit the printed head pin separately.
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
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    CalibrationLedgerError,
    bootstrap_historical_import,
    canonical_json_bytes,
)


OUTPUT_SCHEMA = "joulewise.calibration_historical_import_dry_run.v1"


def _json_object(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _pin_content(pin: Mapping[str, Any]) -> str:
    ordered = {
        "sequence": pin["sequence"],
        "head_digest": pin["head_digest"],
        "ledger_schema": pin["ledger_schema"],
    }
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"


def _emit(plan: Any, *, executed: bool) -> None:
    for receipt in plan.receipts:
        sys.stdout.buffer.write(
            canonical_json_bytes({"record": "receipt", "receipt": receipt}) + b"\n"
        )
    summary = {
        "schema_version": OUTPUT_SCHEMA,
        "record": "bootstrap-summary",
        "executed": executed,
        "receipt_count": len(plan.receipts),
        "final_sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "head_pin": plan.head_pin,
        "head_pin_content": _pin_content(plan.head_pin),
    }
    sys.stdout.buffer.write(canonical_json_bytes(summary) + b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="+",
        type=Path,
        help="run root, instrument_validation directory, or custody directory",
    )
    parser.add_argument(
        "--disposition-table",
        required=True,
        type=Path,
        help="explicit ruled historical-import table",
    )
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=REPO_ROOT,
        help="root against which deterministic custody locators are stored",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="atomically write the ledger (the head pin is still never written)",
    )
    args = parser.parse_args()
    try:
        plan = bootstrap_historical_import(
            args.ledger,
            head_pin_path=args.head_pin,
            roots=args.roots,
            checkout_root=args.checkout_root,
            disposition_table=_json_object(args.disposition_table),
            execute=args.execute,
            repo_root=REPO_ROOT,
        )
    except (CalibrationLedgerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    _emit(plan, executed=args.execute)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
