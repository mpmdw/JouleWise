#!/usr/bin/env python3
"""Prepare/install an R1 LaunchAgent using the shared HAZARD_PACK route."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.align import r1_arm


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--measurement-root", type=Path, required=True)
    prepare.add_argument("--custody-root", type=Path, required=True)
    prepare.add_argument("--t0", type=int, required=True, help="whole-minute Unix epoch")
    prepare.add_argument("--planned-bytes", type=int, default=0,
                         help="optional sourced allocation estimate; absent is explicitly unsized")
    sizing = commands.add_parser("size")
    sizing.add_argument("--t0", type=int, required=True, help="whole-minute Unix epoch")
    for name in ("install", "render", "uninstall", "_bookend", "_display-dwell"):
        command = commands.add_parser(name)
        command.add_argument("--custody-root", type=Path, required=True)
        if name == "render":
            command.add_argument("--output", type=Path, required=True)
        if name == "_bookend":
            command.add_argument("--slot", choices=("pre", "post"), required=True)
    args = parser.parse_args(argv)
    if args.command == "size":
        print(json.dumps(r1_arm.size_window(args.t0), indent=2))
        return 0
    if args.command == "prepare":
        print(json.dumps(r1_arm.prepare(args.measurement_root, args.custody_root, args.t0,
                                        planned_bytes=args.planned_bytes), indent=2))
        return 0
    if args.command == "_bookend":
        return r1_arm.bookend(args.custody_root, args.slot)
    if args.command == "_display-dwell":
        return r1_arm.display_dwell(args.custody_root)
    return subprocess.run(r1_arm.installer_argv(args.custody_root, uninstall=args.command == "uninstall",
                         render_only=args.output if args.command == "render" else None), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
