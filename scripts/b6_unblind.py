#!/usr/bin/env python3
"""Remove stored offsets from a frozen run export after pack release."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6 import blinding
from joulewise.b6.export_runs import atomic_write


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", dest="export_path", type=Path, required=True)
    parser.add_argument("--key-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with args.export_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames
            rows = [row if row.get("non_claim", "").lower() == "true" else
                    blinding.unblind(row, blinding.factor(args.key_dir, row["config_key"])) for row in reader]

        def write_csv(stream):
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        atomic_write(args.out, write_csv)
        print(json.dumps({"export": str(args.out), "rows": len(rows), "unblinded": True}, sort_keys=True))
        return 0
    except Exception as exc:
        print("block-six unblind program fault: " + type(exc).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
