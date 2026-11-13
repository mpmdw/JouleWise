#!/usr/bin/env python3
"""RL-123 native three-hour stop for an R12 closed-nine dry run.

Only this supervisor's newly created reader process group may be stopped.
Generation is never launched here. A timeout requires profiling before retry.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from b6_r12_verify import REPO, safe_root, sha

LIMIT_S = 3 * 60 * 60


def wait_owned(process):
    try:
        return process.wait(timeout=LIMIT_S), False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        return 124, True


def run(root, denied, stem, reduced):
    root, denied = safe_root(root), safe_root(denied)
    if not stem or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in stem):
        raise ValueError("plain fresh dry-run journal name required")
    for path in (root, denied):
        if (path / "generator-parent-exit.txt").read_text().strip() != "0":
            raise ValueError("actual completed generator parent required")
    if json.loads((root / "loop/state.json").read_bytes())["state"] != "DONE":
        raise ValueError("original closed loop required")
    view = root / stem
    view.mkdir(exist_ok=False)
    program = REPO / "scripts/independent_recompute_b6.py"
    script = REPO / "scripts" / ("b6_r12_reduced_finish.py" if reduced else "b6_r12_finish.py")
    argv = [sys.executable, "-B", str(script), "--root", str(root), "--denied-root", str(denied)]
    record = {"synthetic_only": True, "status": "inflight", "argv": argv,
        "program_sha256": sha(program), "supervisor_sha256": sha(__file__),
        "native_limit_s": LIMIT_S, "started_native_ns": time.time_ns(),
        "reader_host": "Air", "other_R12_work_allowed": False,
        "precondition": "orchestrator confirms no other R12 generator/reader on the Air",
        "reduced_volume": reduced}
    receipt = view / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    with (view / "stdout").open("xb") as out, (view / "stderr").open("xb") as err:
        process = subprocess.Popen(argv, cwd=REPO, stdin=subprocess.DEVNULL,
                                   stdout=out, stderr=err, start_new_session=True)
        record["pid"] = process.pid
        receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        code, stopped = wait_owned(process)
    record.update(ended_native_ns=time.time_ns(), exit_code=code,
        status="stopped_profile_required" if stopped else ("done" if code == 0 else "failed"),
        program_sha256_after=sha(program), stdout_sha256=sha(view / "stdout"), stderr_sha256=sha(view / "stderr"))
    if record["program_sha256"] != record["program_sha256_after"]:
        code = 2
        record.update(status="program_changed_reread_required", exit_code=code)
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--denied-root", required=True)
    parser.add_argument("--stem", required=True)
    parser.add_argument("--reduced", action="store_true")
    args = parser.parse_args()
    return run(args.root, args.denied_root, args.stem, args.reduced)


if __name__ == "__main__":
    raise SystemExit(main())
