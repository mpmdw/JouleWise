#!/usr/bin/env python3
"""Prepare or execute the deterministic calibration-ledger genesis import.

Dry-run is the default. It authenticates the reviewed disposition table and
per-member custody manifest, then prints the complete canonical receipt chain
plus the exact candidate head pin without writing either file. ``--execute``
atomically writes only the ledger; the lead must review and commit the printed
head pin separately.
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

from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    CalibrationLedgerError,
    HistoricalImportDurabilityUncertain,
    bootstrap_historical_import,
    canonical_json_bytes,
    custody_manifest_bytes,
    generate_historical_custody_manifest,
)


OUTPUT_SCHEMA = "joulewise.calibration_historical_import_dry_run.v1"
DURABILITY_UNCERTAIN_EXIT = 3


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


def _emit(plan: Any, *, executed: bool, outcome: str) -> None:
    for receipt in plan.receipts:
        sys.stdout.buffer.write(
            canonical_json_bytes({"record": "receipt", "receipt": receipt}) + b"\n"
        )
    summary = {
        "schema_version": OUTPUT_SCHEMA,
        "record": "bootstrap-summary",
        "executed": executed,
        "outcome": outcome,
        "receipt_count": len(plan.receipts),
        "final_sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "disposition_table_sha256": plan.disposition_table_sha256,
        "custody_manifest_sha256": plan.custody_manifest_sha256,
        "head_pin": plan.head_pin,
        "head_pin_content": _pin_content(plan.head_pin),
    }
    sys.stdout.buffer.write(canonical_json_bytes(summary) + b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="optional strict cross-check roots; required in manifest-emission mode",
    )
    parser.add_argument(
        "--disposition-table",
        required=True,
        type=Path,
        help="explicit ruled historical-import table",
    )
    parser.add_argument(
        "--expected-table-sha256",
        required=True,
        help="required SHA-256 of the disposition table's exact raw bytes",
    )
    parser.add_argument(
        "--custody-manifest",
        type=Path,
        help="reviewed content_id-to-absolute-locator custody manifest",
    )
    parser.add_argument(
        "--expected-custody-manifest-sha256",
        help="required SHA-256 of the custody manifest's exact raw bytes",
    )
    parser.add_argument(
        "--emit-custody-manifest",
        action="store_true",
        help="print a lexicographically selected manifest and write nothing",
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
        table_raw = args.disposition_table.read_bytes()
        if args.emit_custody_manifest:
            if args.execute:
                raise ValueError("--emit-custody-manifest cannot execute")
            if not args.roots:
                raise ValueError("--emit-custody-manifest requires custody roots")
            manifest = generate_historical_custody_manifest(
                roots=args.roots,
                checkout_root=args.checkout_root,
                disposition_table_raw=table_raw,
                expected_disposition_table_sha256=args.expected_table_sha256,
            )
            raw = custody_manifest_bytes(manifest)
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()
            print(
                f"custody-manifest-sha256={hashlib.sha256(raw).hexdigest()}",
                file=sys.stderr,
            )
            return 0
        if args.custody_manifest is None:
            raise ValueError("--custody-manifest is required")
        if args.expected_custody_manifest_sha256 is None:
            raise ValueError("--expected-custody-manifest-sha256 is required")
        plan = bootstrap_historical_import(
            args.ledger,
            head_pin_path=args.head_pin,
            roots=args.roots,
            checkout_root=args.checkout_root,
            disposition_table_raw=table_raw,
            expected_disposition_table_sha256=args.expected_table_sha256,
            custody_manifest_raw=args.custody_manifest.read_bytes(),
            expected_custody_manifest_sha256=(
                args.expected_custody_manifest_sha256
            ),
            execute=args.execute,
            repo_root=REPO_ROOT,
        )
    except HistoricalImportDurabilityUncertain as exc:
        _emit(exc.plan, executed=True, outcome=exc.outcome)
        print(
            "committed: parent-directory durability remains uncertain after "
            "one retry; rerun the identical --execute invocation to confirm "
            "durability before updating the head pin",
            file=sys.stderr,
        )
        return DURABILITY_UNCERTAIN_EXIT
    except (CalibrationLedgerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    _emit(
        plan,
        executed=args.execute,
        outcome="committed" if args.execute else "planned",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
