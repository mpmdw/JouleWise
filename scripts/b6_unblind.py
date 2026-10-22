#!/usr/bin/env python3
"""Remove stored offsets from a frozen run export after pack release."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6 import blinding
from joulewise.b6.export_runs import atomic_write


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", dest="export_path", type=Path, required=True)
    keys = parser.add_mutually_exclusive_group(required=True)
    keys.add_argument("--key-dir", type=Path)
    keys.add_argument("--pack-records-root", type=Path)
    parser.add_argument("--blinding-group")
    parser.add_argument("--stage1-commit", help="permits loading the grouped withheld rows")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.stage1_commit and not re.fullmatch(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?", args.stage1_commit):
            raise ValueError("stage-1 commit must be a Git commit hash")
        key_dir = args.key_dir
        if key_dir is None:
            if not args.blinding_group:
                raise ValueError("--pack-records-root requires --blinding-group")
            key_dir = blinding.key_directory(args.pack_records_root, args.blinding_group,
                                             {"blinding_group": args.blinding_group})
        with args.export_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames
            source_rows = list(reader)
        flags = []
        if args.stage1_commit:
            sidecar = args.export_path.with_name(args.export_path.name.removesuffix(".runs.csv") + ".session.json")
            info = json.loads(sidecar.read_text()).get("blinding", {}).get("withheld") if sidecar.is_file() else None
            if info is not None:
                try:
                    with (args.export_path.parent / info["path"]).open(newline="", encoding="utf-8") as stream:
                        source_rows.extend(csv.DictReader(stream))
                except FileNotFoundError:
                    flags.append("bytes.withheld_missing")
        # Registered plan order, never a wall or monotonic clock.
        source_rows.sort(key=lambda row: int(row.get("order_index") or 0))
        rows = [row if row.get("non_claim", "").lower() == "true" else
                blinding.unblind(row, blinding.stored_factor(key_dir, row["config_key"])) for row in source_rows]

        def write_csv(stream):
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        atomic_write(args.out, write_csv)
        result = {"export": str(args.out), "rows": len(rows), "unblinded": True}
        if flags:
            result["flags"] = flags
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        detail = str(exc) if isinstance(exc, ValueError) and str(exc).startswith("blinding key ") else type(exc).__name__
        print("block-six unblind program fault: " + detail, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
