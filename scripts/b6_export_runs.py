#!/usr/bin/env python3
"""Export a block-six archive's per-run table and session summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.export_runs import export
from joulewise.desk_restore import StorageStop


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", "--archive-root", dest="archive", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--registration-dir", type=Path, required=True)
    parser.add_argument("--pack-records-root", type=Path, required=True)
    parser.add_argument("--export-dir", type=Path, required=True)
    parser.add_argument("--non-claim", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = export(args.archive, json.loads(args.plan.read_text()), args.registration_dir,
                        args.pack_records_root, args.export_dir, non_claim=args.non_claim)
        print(json.dumps(result.structure(), sort_keys=True))
        return 0
    except StorageStop as exc:
        print(f"refused: {exc}", file=sys.stderr)  # the stop names its own cause code
        return 5
    except Exception as exc:
        print(f"block-six export program fault: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
