#!/usr/bin/env python3
"""Record the authenticated comparative-cell window-duration margin receipt.

The interface intentionally accepts roots and a pack identity only.  Cell
IDs, members, margins, statuses, and output paths are always derived.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.window_duration_margins import (  # noqa: E402
    WindowDurationMarginsRefusal,
    record_window_duration_margins,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--receipt-root", required=True, type=Path)
    parser.add_argument("--pack-identity", required=True)
    args = parser.parse_args(argv)
    try:
        recorded = record_window_duration_margins(
            repository_root=args.repository_root,
            pack_root=args.pack_root,
            runs_root=args.runs_root,
            receipt_root=args.receipt_root,
            pack_identity=args.pack_identity,
        )
    except WindowDurationMarginsRefusal as exc:
        print(
            json.dumps(
                {"status": "REFUSE", "reason": exc.reason, "detail": exc.detail},
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "status": "PASS",
                "receipt_path": str(recorded.path),
                "receipt_sha256": recorded.sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
