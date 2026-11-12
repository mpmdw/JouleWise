#!/usr/bin/env python3
"""Finish one full BETA fixture and its reader, preserving actual parent exits.

A killed supervisor leaves an explicit inflight journal. It must not be
restarted on that root. It never writes an original session/loop record.
"""
from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

from b6_r12_segments import validate_resume
from b6_r12_verify import REPO, child, safe_root, sha


def smoke_proof(root, control):
    first = control["steps"][0]["boundary"]
    terminal = child(root, first["terminal_path"])
    courier = terminal.parent / "courier.json"
    value = json.loads(courier.read_bytes())
    if value.get("sent") is not True or value.get("heartbeat_seen") is not True:
        raise ValueError("original smoke courier did not complete; no ordinary collection")
    records = terminal.parent.parent.parent / "courier-program"
    paths = sorted(records.glob("*.json"))
    if not paths:
        raise ValueError("original smoke file courier records required")
    proof = {"courier_json_sha256": sha(courier), "courier": value, "records": {}}
    for path in paths:
        record = json.loads(path.read_bytes())
        if record.get("transport") != "file" or record.get("mail_sent") is not False:
            raise ValueError("expected original mail-free file transport")
        stdin = child(root, str(path.parent / record["stdin"]))
        proof["records"][str(path)] = {"sha256": sha(path), "stdin_sha256": sha(stdin)}
    return proof


def run(outer, stem):
    outer = safe_root(outer)
    journal = outer / "full-reader-supervision.json"
    if journal.exists():
        raise ValueError("new supervision journal required; never restart an interrupted supervisor")
    with (outer / "full-reader-supervision.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control = json.loads((outer / "segments.json").read_bytes())
        root = child(outer, control["main"])
        validate_resume(root, control)
        if len(control["steps"]) != 1 or control["steps"][-1]["boundary"]["state"] != "SMOKE_RUN":
            raise ValueError("start after exactly one completed smoke driver")
        state = {"synthetic_only": True, "supervisor_sha256": sha(Path(__file__)),
                 "smoke_writer_proof": smoke_proof(root, control), "steps": [], "status": "ready"}

        def record():
            temporary = journal.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
            temporary.replace(journal)

        def invoke(argv, label):
            item = {"argv": argv, "label": label, "started_native_ns": time.time_ns()}
            state["steps"].append(item)
            state["status"] = "inflight"
            record()
            print("starting " + label, flush=True)
            result = subprocess.run(argv, cwd=REPO, check=False)
            item.update(exit_code=result.returncode, ended_native_ns=time.time_ns())
            state["status"] = "boundary" if result.returncode == 0 else "failed"
            record()
            return result.returncode

        record()
        for label in ("smoke desk", "ordinary full driver", "ordinary full desk"):
            code = invoke([sys.executable, "-B", str(REPO / "scripts/b6_r12_profile_session.py"),
                           "--out", str(outer)], label)
            if code:
                return code
            control = json.loads((outer / "segments.json").read_bytes())
            validate_resume(root, control)
        boundary = control["steps"][-1]["boundary"]
        if boundary["state"] != "ROTATE" or boundary["attempt_count"] != 1:
            raise ValueError("full ordinary desk/attempt did not complete")
        code = invoke([sys.executable, "-B", str(REPO / "scripts/b6_r12_full_verify.py"),
                       "--cohort-root", str(outer), "--stem", stem], "production-size reader and named tests")
        state["status"] = "done" if code == 0 else "failed"
        record()
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", required=True, type=Path)
    parser.add_argument("--stem", required=True)
    args = parser.parse_args()
    return run(args.cohort_root, args.stem)


if __name__ == "__main__":
    raise SystemExit(main())
