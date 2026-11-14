#!/usr/bin/env python3
"""Run verified R12 phase commands, with explicit window limits or unbounded mode.

Only scheduling and outside-tree receipts live here. No chain state, attempt,
verdict, archive or scientific output is edited by this supervisor.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from b6_r12_segments import validate_resume
from b6_r12_verify import REPO, child, safe_root, sha


def utc(value):
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("explicit UTC offset required")
    return parsed.timestamp()


def ready(root):
    control = json.loads((root / "segments.json").read_bytes())
    main = child(root, control["main"])
    validate_resume(main, control)
    return main, control["steps"][-1]["boundary"]["state"]


def supervise(args):
    root = safe_root(args.cohort_root)
    if not args.journal or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in args.journal):
        raise ValueError("plain new journal name required")
    with (root / "supervisor.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main, state = ready(root)
        out = child(root, root / args.journal)
        out.mkdir(exist_ok=False)
        record_path = out / "receipt.json"
        value = {"schema": "r12.supervisor.v1", "synthetic_only": True,
            "runner_sha256": sha(Path(__file__)), "kind": args.kind, "commands": [],
            "started_native_ns": time.time_ns(), "driver_start_before": args.driver_start_before,
            "desk_start_before": args.desk_start_before, "unbounded": args.unbounded,
            "max_phases": args.max_phases, "original_state_at_start": state,
            "full_volume_claim": False, "closed_nine_claim": False}

        def record():
            temporary = record_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
            temporary.replace(record_path)

        env = {**os.environ, "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
        for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "R12_TRACE_STACKS"):
            env.pop(key, None)
        script = "b6_r12_segments.py" if args.kind == "registered" else "b6_r12_reduced_set.py"
        record()
        code = 0
        while state != "DONE":
            if args.max_phases is not None and len(value["commands"]) >= args.max_phases:
                value["reason"] = "phase_limit"
                break
            desk_next = state in {"SMOKE_RUN", "SESSION_RUN"}
            cutoff = args.desk_start_before if desk_next else args.driver_start_before
            if not args.unbounded and time.time() >= cutoff:
                value["reason"] = "phase_start_cutoff"
                break
            index = len(value["commands"]) + 1
            argv = [sys.executable, "-B", str(REPO / "scripts" / script), "--out", str(root)]
            item = {"argv": argv, "started_native_ns": time.time_ns(), "before": state}
            value["commands"].append(item)
            record()
            stdout, stderr = out / f"phase-{index:03}.stdout", out / f"phase-{index:03}.stderr"
            with stdout.open("xb") as output, stderr.open("xb") as error:
                process = subprocess.Popen(argv, cwd=REPO, env=env, stdout=output, stderr=error)
                item["pid"] = process.pid
                record()
                code = process.wait()
            item.update(exit_code=code, ended_native_ns=time.time_ns(),
                        stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
            record()
            if code:
                value["reason"] = "phase_failed"
                break
            main, state = ready(root)
            item["after"] = state
            record()
            print(json.dumps({"phase": index, "exit_code": code, "original_state": state}), flush=True)
        value.update(ended_native_ns=time.time_ns(), original_state_at_end=state,
                     last_phase_exit=code, reason=value.get("reason", "original_loop_done"))
        record()
        print(json.dumps({"journal": str(out), "state": state, "exit_code": code,
                          "reason": value["reason"]}), flush=True)
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", required=True, type=Path)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--kind", required=True, choices=("registered", "reduced"))
    parser.add_argument("--unbounded", action="store_true", help="explicitly run without a window cutoff")
    parser.add_argument("--driver-start-before", type=utc)
    parser.add_argument("--desk-start-before", type=utc)
    parser.add_argument("--max-phases", type=int)
    args = parser.parse_args()
    if args.max_phases is not None and args.max_phases < 1:
        parser.error("max-phases must be positive")
    if args.unbounded == (args.driver_start_before is not None or args.desk_start_before is not None):
        parser.error("choose unbounded or both explicit window cutoffs")
    if not args.unbounded and (args.driver_start_before is None or args.desk_start_before is None):
        parser.error("both window cutoffs required")
    return supervise(args)


if __name__ == "__main__":
    raise SystemExit(main())
