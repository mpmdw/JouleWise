#!/usr/bin/env python3
"""Harvest one block-5 window: archive the bytes, emit the numbers and the flags.

Nothing here refuses on data.  Exit status:

* 0  COLLECTED or NULL (read ``claim_usable`` in harvest.json / window_flags.json)
* 2  HARVEST_FAULT (the program failed on present bytes; outputs are written,
     claim_usable is false; fix by R3 and re-run on the archived bytes)
* 3  inputs could not be resolved or the archive root is unusable
* 4  not ready: the chain's process group is alive or the terminal record is absent

stdout carries structure only: the verdict, counts and output digests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.b5 import harvest as h  # noqa: E402

OVERRIDES = (
    "custody_root", "measurement_root", "pack_root", "pack_id", "claim_runs_root", "bound_runs_root",
    "chain_path", "chain_sha256_path", "ledger_path", "head_pin_path", "acceptance_path",
    "bracket_session_id", "pre_attempt_id", "post_attempt_id", "h_claim", "sealed_inventory_path",
    "executed_inventory_path", "catalog_path", "identity_pins_path", "monitor_dir", "arm_record_path",
    "flags_dir", "plan_id", "attempt",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, type=Path, help="the HAZARD_PACK window plan")
    parser.add_argument("--archive-root", required=True, type=Path, help="new directory; created once")
    for name in OVERRIDES:
        parser.add_argument("--" + name.replace("_", "-"), dest=name,
                            help="override the value the plan gives (or omits)")
    parser.add_argument("--thresholds", type=Path, help="JSON object of threshold overrides")
    parser.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 2) // 2)),
                        help="member-assessment worker processes")
    parser.add_argument("--prepare-desk", action="store_true",
                        help="produce the whole-window verdict with the production writer when absent")
    parser.add_argument("--skip-g3", action="store_true", help="do not run the G3 provenance checker")
    parser.add_argument("--allow-missing-terminal", action="store_true",
                        help="open even without night/result.json once the chain group is proven gone")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    overrides = {name: getattr(args, name) for name in OVERRIDES}
    if overrides.get("attempt") is not None:
        try:
            overrides["attempt"] = int(overrides["attempt"])
        except ValueError:
            pass
    if args.thresholds is not None:
        overrides["thresholds"] = json.loads(args.thresholds.read_bytes())
    try:
        inputs = h.resolve_inputs(args.plan, overrides)
        record = h.harvest(inputs, args.archive_root, seams=h.Seams(workers=args.workers),
                           prepare_desk=args.prepare_desk, run_g3=not args.skip_g3,
                           allow_missing_terminal=args.allow_missing_terminal)
    except h.NotReady as exc:
        print(f"verdict=NOT_READY reason={exc}")
        return 4
    except (h.HarvestFault, OSError, ValueError) as exc:
        print(f"verdict=HARVEST_FAULT reason={type(exc).__name__}:{str(exc)[:200]}")
        return 3
    print(f"verdict={record['verdict']} claim_usable={str(record['claim_usable']).lower()} "
          f"flags={record['flags']} members={record['members_assessed']}")
    harvest_json = Path(record["archive_root"]) / "harvest.json"
    print(f"harvest={harvest_json} sha256={h.sha256_file(harvest_json)}")
    for name, digest in record["outputs"].items():
        print(f"path={Path(record['archive_root']) / name} sha256={digest}")
    return 2 if record["verdict"] == h.HARVEST_FAULT else 0


if __name__ == "__main__":
    raise SystemExit(main())
