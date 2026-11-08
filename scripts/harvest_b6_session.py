#!/usr/bin/env python3
"""Harvest, screen, judge and export one block-six session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.desk_restore import StorageStop
from joulewise.b5.harvest import Seams, harvest, resolve_inputs
from joulewise.b6 import registration
from joulewise.b6.export_runs import export
from joulewise.b6.session import accept_archive
from joulewise.harvest_profile import StageProfile

# 0: harvested and judged; 2: CLI usage; 3: harvest program fault;
# 4: acceptance program fault; 5: export program fault;
# 6: numbers archived, acceptance registration unavailable (pending, not a fault).
PENDING_REGISTRATION = 6


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "archive-root", "registration-dir", "pack-records-root", "export-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--non-claim", action="store_true")
    parser.add_argument("--smoke", action="store_true", help="non-claim smoke acceptance")
    parser.add_argument("--allow-missing-terminal", action="store_true",
                        help="caller has established the collection job is gone")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--io-workers", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--parse-cache-mib", type=int, choices=(0, 32, 64, 128), default=128,
                        help="raw input cap for scoped parser reuse; 0 disables it")
    parser.add_argument("--profile", type=Path, help="new external JSONL engineering timings")
    args = parser.parse_args(argv)
    with StageProfile(args.profile) as profile:
        code = _run(args, profile)
        profile.observe({'stage': 'cli.result', 'exit_code': code})
        return code


def _run(args, profile):
    phase = 3
    try:
        # Missing quiet-machine values never prevent archiving the measurements.
        try:
            reg = registration.load(args.registration_dir)
        except (OSError, ValueError):
            reg = None
        inputs = resolve_inputs(args.plan, overrides={
            "catalog_path": ROOT / (reg or registration.DEFAULTS)["catalog"],
            "identity_pins_path": args.registration_dir / "identity_pins.json"})
        with profile.stage('harvest.total'):
            harvested = harvest(inputs, args.archive_root,
                                seams=Seams(workers=args.workers, io_workers=args.io_workers,
                                            parse_cache_bytes=args.parse_cache_mib << 20,
                                            stage_observer=profile.observe),
                                prepare_desk=True, allow_missing_terminal=args.allow_missing_terminal,
                                registration_paths=[args.registration_dir / "acceptance.json",
                                                    args.registration_dir / "identity_pins.json"])
        if harvested.get("verdict") == "HARVEST_FAULT":
            return 3
        phase = 4
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        with profile.stage('acceptance'):
            result, evidence = accept_archive(args.archive_root, plan, args.registration_dir,
                                             plan_path=args.plan, smoke=args.smoke, replace_existing=True)
        phase = 5
        with profile.stage('export'):
            exported = export(args.archive_root, plan, args.registration_dir, args.pack_records_root,
                              args.export_dir, non_claim=args.non_claim or args.smoke, evidence=evidence,
                              acceptance_record=result.record)
        print(json.dumps({"session_id": result.record["session_id"], "verdict": result.verdict,
                          "counting": result.counting, "structural": result.structural,
                          "flag_counts": result.record["flag_counts"], "export": exported.structure()}, sort_keys=True))
        return PENDING_REGISTRATION if result.verdict == "UNAVAILABLE" else 0
    except StorageStop as exc:
        print(f"refused: {exc}", file=sys.stderr)  # the stop names its own cause code
        return phase
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        print("block-six session program fault: " + detail, file=sys.stderr)
        return phase


if __name__ == "__main__":
    sys.exit(main())
