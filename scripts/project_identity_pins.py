#!/usr/bin/env python3
"""Freeze or read-only verify D-117 identity-pin projections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.identity_pins import (  # noqa: E402
    IdentityPinProjectionError,
    freeze_projection,
    verify_frozen_projection,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser(
        "freeze", help="derive and freeze pins from pack/config/runtime bytes"
    )
    freeze.add_argument("pack_root", type=Path)

    verify = subparsers.add_parser(
        "verify", help="re-derive frozen pins and write an external arm receipt"
    )
    verify.add_argument("pack_root", type=Path)
    verify.add_argument("--window-custody-root", type=Path, required=True)
    verify.add_argument("--bracket-session-id", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "freeze":
            result = freeze_projection(args.pack_root)
        else:
            result = verify_frozen_projection(
                args.pack_root,
                args.window_custody_root,
                args.bracket_session_id,
            )
    except IdentityPinProjectionError as exc:
        result = {
            "status": "REFUSE",
            "reason_codes": [exc.reason_code],
            "message": str(exc),
            "observed": exc.observed,
        }
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

