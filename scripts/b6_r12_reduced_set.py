#!/usr/bin/env python3
"""Additional reduced-volume R12 set, using the same unmodified pinned chain.

The short model-source dwell is an external input, never a shortened chain
wait, admission threshold or calibration. Full-volume evidence is separate.
Each invocation ends at one completed original driver/desk boundary.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

from b6_r12_session_fixture import (prepare, command, export_chain_inputs,
    materialize_inputs, prepare_interpreters, init_source_repo, declare_sources)
from b6_r12_segments import snapshot, validate_resume
from b6_r12_verify import REPO, child, safe_root, sha
from b6_r12_chain_fixture import PIN


def reduced_bootstrap():
    """Only replace this generator's external source-policy supplier."""
    return '''import b6_r12_orchestrate as scheduler
original_source_policy = scheduler.session_policy
def reduced_source_policy(pack, round_number, base):
    value = original_source_policy(pack, round_number, base)
    value.update(volume="reduced", primary_stream_duration_s=5,
                 token_first_s=.5, token_next_s=.001)
    return value
scheduler.session_policy = reduced_source_policy
from runtime import bootstrap
raise SystemExit(bootstrap())
'''


def initialize(main, prior):
    """Prepare only generator inputs, before any chain program starts."""
    prior = safe_root(prior)
    common = json.loads((prior / "manifest.json").read_bytes())
    seed = json.loads((prior / "seed-receipt.json").read_bytes())
    if ((prior / "generator-parent-exit.txt").read_text().strip() != "0"
            or common.get("synthetic_only") is not True or common.get("pin") != PIN
            or seed.get("driver_rc") not in (0, 6)):
        raise ValueError("completed pinned synthetic prerequisite required")
    measurement = child(prior, seed["smoke"]["measurement"])
    files = [prior / "manifest.json", prior / "seed-receipt.json",
             measurement / "runs/calibration_observation_ledger.jsonl",
             measurement / "configs/calibration/calibration_ledger_head.json"]
    declaration = {"root": str(prior), "measurement": str(measurement),
        "files": {str(p): sha(p) for p in files},
        "clock_ns": struct.unpack("!Q", (prior / "clock.bin").read_bytes())[0],
        "writer": "pinned joulewise.b6.smoke.copy_ledger; immutable prior synthetic captures"}
    prepare(main)
    (main / "bootstrap.py").write_text(reduced_bootstrap())
    (main / "prior-seed-input.json").write_text(json.dumps(declaration, indent=2) + "\n")
    (main / "source-policy.json").write_text(json.dumps({"volume": "reduced", "denied_off": False,
        "denied_normal": False, "primary_stream_duration_s": 5,
        "token_first_s": .5, "token_next_s": .001}, indent=2) + "\n")
    path = main / "manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest.update(prior_chain_seed_input=declaration,
        reduced_set={"scheduler_sha256": sha(Path(__file__)), "bootstrap_sha256": sha(main / "bootstrap.py"),
            "source_supplier": "generator b6_r12_orchestrate.session_policy; no pinned binding replaced",
            "values": {"volume": "reduced", "primary_stream_duration_s": 5,
                       "token_first_s": .5, "token_next_s": .001},
            "full_volume_claim": False, "calibration_and_chain_waits": "unchanged"})
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    export_chain_inputs(main)
    subprocess.run(command(main, "make-inputs"), cwd=main, check=True)
    materialize_inputs(main)
    prepare_interpreters(main)
    init_source_repo(main)
    declare_sources(main)


def run(root, prior=None):
    root = safe_root(root)
    fresh = prior is not None
    if fresh:
        if root.exists():
            raise ValueError("new reduced cohort root required")
        root.mkdir()
    with (root / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        path = root / "segments.json"
        if fresh:
            control = {"schema": "r12.reduced-segments.v1", "pin": PIN, "synthetic_only": True,
                "runner_sha256": sha(Path(__file__)), "steps": [],
                "main": str(root / ("nine-" + "long-path-" * 18)),
                "prediction": "six declared R12 shapes agree; closed nine; serial/pool identical; NOT full volume",
                "prior_seed": str(safe_root(prior)), "prediction_sources": {n: sha(REPO / n) for n in (
                    "tests/test_b6_r12_session_fixture.py", "docs/run_reports/2026-11-11-p1-b6-r12-r3.md")}}
        else:
            control = json.loads(path.read_bytes())
            if control["runner_sha256"] != sha(Path(__file__)):
                raise ValueError("reduced scheduler changed")
            validate_resume(child(root, control["main"]), control)
            manifest = json.loads((Path(control["main"]) / "manifest.json").read_bytes())
            if sha(Path(control["main"]) / "bootstrap.py") != manifest["reduced_set"]["bootstrap_sha256"]:
                raise ValueError("external source policy changed")
            if control["steps"][-1]["boundary"]["state"] == "DONE":
                print("original loop DONE; reduced-set verification may run", flush=True)
                return 0
        main = child(root, control["main"])
        index = len(control["steps"]) + 1
        step = {"index": index, "started_native_ns": time.time_ns()}
        control["steps"].append(step)

        def record():
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(control, indent=2, sort_keys=True) + "\n")
            temporary.replace(path)

        record()  # Preparation failures/interruption also forbid continuation.
        if fresh:
            initialize(main, prior)
        argv = command(main, "loop-probe", "all", "9", "one")
        step["argv"] = argv
        out, err = root / f"step-{index:03}.stdout", root / f"step-{index:03}.stderr"
        with out.open("xb") as stdout, err.open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=main, stdout=stdout, stderr=stderr)
            step["pid"] = process.pid
            record()
            code = process.wait()
        step.update(exit_code=code, ended_native_ns=time.time_ns(),
                    stdout_sha256=sha(out), stderr_sha256=sha(err))
        if code == 0:
            step["boundary"] = snapshot(main)
            if step["boundary"]["state"] == "DONE":
                (main / "generator-parent-exit.txt").write_text("0\n")
        record()
        print(json.dumps(step, sort_keys=True), flush=True)
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prior-chain-root", type=Path)
    args = parser.parse_args()
    return run(args.out, args.prior_chain_root)


if __name__ == "__main__":
    raise SystemExit(main())
