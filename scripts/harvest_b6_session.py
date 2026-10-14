#!/usr/bin/env python3
"""Harvest, screen, judge and export one block-six session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b5.harvest import harvest, resolve_inputs
from joulewise.b6 import registration
from joulewise.b6.export_runs import export
from joulewise.b6.session import accept_archive


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "archive-root", "registration-dir", "pack-records-root", "export-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--non-claim", action="store_true")
    args = parser.parse_args(argv)
    phase = 3
    try:
        reg = registration.load(args.registration_dir)
        inputs = resolve_inputs(args.plan, overrides={
            "catalog_path": ROOT / reg["catalog"],
            "identity_pins_path": args.registration_dir / "identity_pins.json"})
        harvested = harvest(inputs, args.archive_root)
        if harvested.get("verdict") == "HARVEST_FAULT":
            return 3
        phase = 4
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result, evidence = accept_archive(args.archive_root, plan, args.registration_dir)
        phase = 5
        exported = export(args.archive_root, plan, args.registration_dir, args.pack_records_root,
                          args.export_dir, non_claim=args.non_claim, evidence=evidence,
                          acceptance_record=result.record)
        print(json.dumps({"session_id": result.record["session_id"], "verdict": result.verdict,
                          "counting": result.counting, "structural": result.structural,
                          "flag_counts": result.record["flag_counts"], "export": exported.structure()}, sort_keys=True))
        return 0
    except Exception as exc:
        print("block-six session program fault: " + type(exc).__name__, file=sys.stderr)
        return phase


if __name__ == "__main__":
    sys.exit(main())
