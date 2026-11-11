#!/usr/bin/env python3
"""Check committed owner permission before a tool displays outcomes."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.unseal_record import UnsealRefused, require_unseal

RECORDS_DIR = ROOT / "docs" / "unseals"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--block", required=True)
    check.add_argument("--verdict", type=Path, required=True)
    check.add_argument("--path")
    args = parser.parse_args(argv)
    try:
        digest = hashlib.sha256()
        # Explicit caller-supplied verdict only: hash bytes without parsing or
        # printing them. Record verdict_path and patterns remain inert text.
        with open(args.verdict, "rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except (OSError, ValueError):
        print("verdict_unreadable", file=sys.stderr)
        return 1
    try:
        require_unseal(RECORDS_DIR, block=args.block, verdict_sha256=digest.hexdigest(), path=args.path)
    except UnsealRefused as exc:
        print(exc.code, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
