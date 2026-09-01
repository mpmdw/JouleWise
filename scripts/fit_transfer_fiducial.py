#!/usr/bin/env python3
"""Fit a governed inserted-gap transfer-fiducial diagnostic capture."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.transfer_fiducial import (  # noqa: E402
    TransferFiducialError,
    build_capture,
    canonical_receipt_bytes,
    issue_pre_data_receipt,
    receipt_sha256_sidecar_path,
)


def _exclusive_write(path: Path, raw: bytes) -> None:
    """Publish bytes only if no filesystem entry already has this name."""

    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise TransferFiducialError("pre_data_receipt_already_exists") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _publish_pre_data_receipt(path: Path, receipt: dict[str, object]) -> bytes:
    """Create the canonical receipt and its digest sidecar exactly once."""

    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = canonical_receipt_bytes(receipt)
    _exclusive_write(path, rendered)
    sidecar_path = receipt_sha256_sidecar_path(path)
    try:
        import hashlib

        _exclusive_write(
            sidecar_path,
            (hashlib.sha256(rendered).hexdigest() + "\n").encode("ascii"),
        )
    except BaseException as exc:
        raise TransferFiducialError(
            f"pre_data_receipt_sha256_sidecar_issue_failed:{exc}"
        ) from exc
    return rendered


def _parser(*, receipt_mode: bool = False) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit ten-run inserted-gap transfer-fiducial evidence"
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=not receipt_mode)
    parser.add_argument("--pulse-calibration-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--issue-receipt", action="store_true")
    parser.add_argument("--output", type=Path, required=not receipt_mode)
    return parser


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parser(receipt_mode="--issue-receipt" in raw_argv).parse_args(raw_argv)
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
        if args.receipt.exists():
            print(
                "transfer fiducial receipt failed: "
                "pre_data_receipt_already_exists",
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
        try:
            rendered = _publish_pre_data_receipt(args.receipt, receipt)
        except (OSError, TransferFiducialError, ValueError) as exc:
            print(f"transfer fiducial receipt failed: {exc}", file=sys.stderr)
            return 2
        print(rendered.decode("utf-8"), end="")
        return 0
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
