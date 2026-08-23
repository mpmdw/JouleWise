#!/usr/bin/env python3
"""Verify the closed versioned receipt-histsem chain from local Git objects."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.arm_readiness import (  # noqa: E402
    HistoricalSemanticsError,
    render_json,
    verify_all_receipt_histsem,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--pinset", type=Path, default=None)
    parser.add_argument("--pack-root", type=Path, action="append", default=None)
    parser.add_argument("--require-published", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repository = args.repository_root.resolve(strict=True)
        pinset = args.pinset
        if pinset is not None and not pinset.is_absolute():
            pinset = repository / pinset
        pack_roots = None
        if args.pack_root is not None:
            pack_roots = [
                path if path.is_absolute() else repository / path
                for path in args.pack_root
            ]
        result = verify_all_receipt_histsem(
            repository,
            pinset_path=pinset,
            pack_roots=pack_roots,
            require_published=args.require_published,
        )
    except HistoricalSemanticsError as exc:
        result = {
            "schema_version": "joulewise.receipt_histsem_verification.v1",
            "status": "REFUSE",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        sys.stdout.buffer.write(render_json(result))
        return 2
    except OSError as exc:
        result = {
            "schema_version": "joulewise.receipt_histsem_verification.v1",
            "status": "REFUSE",
            "reason_codes": ["histsem_git_unavailable"],
            "detail": str(exc),
        }
        sys.stdout.buffer.write(render_json(result))
        return 2
    raw = render_json(result)
    if args.output is not None:
        args.output.write_bytes(raw)
    sys.stdout.buffer.write(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
