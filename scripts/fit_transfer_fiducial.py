#!/usr/bin/env python3
"""Fit a governed inserted-gap transfer-fiducial diagnostic capture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.transfer_fiducial import (  # noqa: E402
    TransferFiducialError,
    build_capture,
    issue_pre_data_receipt,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit ten-run inserted-gap transfer-fiducial evidence"
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path)
    parser.add_argument("--pulse-calibration-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--issue-receipt", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.issue_receipt:
        if args.receipt is None:
            print(
                "transfer fiducial receipt failed: --issue-receipt requires --receipt",
                file=sys.stderr,
            )
            return 2
        if args.runs_root is not None or args.output is not None:
            print(
                "transfer fiducial receipt failed: --issue-receipt does not accept "
                "--runs-root or --output",
                file=sys.stderr,
            )
            return 2
        try:
            receipt = issue_pre_data_receipt(
                plan_path=args.plan,
                pulse_calibration_dir=args.pulse_calibration_dir,
            )
        except (OSError, TransferFiducialError, ValueError) as exc:
            print(f"transfer fiducial receipt failed: {exc}", file=sys.stderr)
            return 2
        rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    if args.runs_root is None or args.receipt is None or args.output is None:
        print(
            "transfer fiducial fit failed: --runs-root, --receipt, and --output are required",
            file=sys.stderr,
        )
        return 2
    try:
        capture = build_capture(
            plan_path=args.plan,
            runs_root=args.runs_root,
            pulse_calibration_dir=args.pulse_calibration_dir,
            pre_data_receipt_path=args.receipt,
        )
    except (OSError, TransferFiducialError, ValueError) as exc:
        print(f"transfer fiducial fit failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(capture, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
