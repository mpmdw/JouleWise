#!/usr/bin/env python3
"""Additional full-roster, reduced-stream single-pack R12 shape fixture."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import b6_r12_reduced_set as inputs
from b6_r12_session_fixture import command
from b6_r12_segments import snapshot, validate_resume
from b6_r12_verify import REPO, child, safe_root, sha


def run(root, prior=None, pack=None, scenario=None):
    root = safe_root(root)
    fresh = prior is not None
    if fresh:
        if root.exists() or pack is None or scenario is None:
            raise ValueError("new root, pack and scenario required")
        root.mkdir()
    with (root / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        path = root / "segments.json"
        if fresh:
            control = {"schema": "r12.single-pack.v1", "synthetic_only": True, "pin": inputs.PIN,
                "runner_sha256": sha(Path(__file__)), "implementation_sha256": sha(Path(inputs.__file__)),
                "main": str(root / ("single-" + "long-path-" * 18)), "pack": pack,
                "scenario": scenario, "steps": [], "full_volume_claim": False, "closed_nine_claim": False,
                "prediction": "option (c) 0/agrees; anchor/mixed/compressed shape assertions for anchor BETA; no roster or threshold changes"}
        else:
            control = json.loads(path.read_bytes())
            if (control["runner_sha256"] != sha(Path(__file__))
                    or control["implementation_sha256"] != sha(Path(inputs.__file__))):
                raise ValueError("single-pack generator changed")
            if (pack is not None and pack != control["pack"]) or (scenario is not None and scenario != control["scenario"]):
                raise ValueError("predeclared pack/scenario changed")
            validate_resume(child(root, control["main"]), control)
            if control["steps"][-1]["boundary"]["attempt_count"] >= 1:
                print("one original ordinary attempt complete; single-pack fixture stops", flush=True)
                return 0
        main = child(root, control["main"])
        index = len(control["steps"]) + 1
        step = {"index": index, "started_native_ns": time.time_ns()}
        control["steps"].append(step)

        def record():
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(control, indent=2, sort_keys=True) + "\n")
            temporary.replace(path)

        record()
        if fresh:
            inputs.initialize(main, safe_root(prior))
            source = main / "source-policy.json"
            policy = json.loads(source.read_bytes())
            changes = ({"native_timestamp_offsets_s": {"27": 5.0}} if scenario == "anchor" else
                       {"gpu_busy_primary_ordinals": [1]} if scenario == "waited" else {})
            policy.update(changes)
            source.write_text(json.dumps(policy, indent=2) + "\n")
            manifest_path = main / "manifest.json"
            manifest = json.loads(manifest_path.read_bytes())
            manifest["single_pack"] = {"pack": pack, "scenario": scenario, "source_policy": policy,
                "runner_sha256": sha(Path(__file__)), "implementation_sha256": control["implementation_sha256"],
                "registered_member_counts": "unchanged", "registered_thresholds": "unchanged",
                "full_volume_claim": False, "closed_nine_claim": False,
                "unused_catalog": "fixture-plan.json lists the shared generator's all-pack schedules; this one-pack path uses the literal base source policy above"}
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        argv = command(main, "loop-probe", control["pack"], "1", "one")
        step["argv"] = argv
        stdout, stderr = root / f"step-{index:03}.stdout", root / f"step-{index:03}.stderr"
        with stdout.open("xb") as output, stderr.open("xb") as error:
            process = subprocess.Popen(argv, cwd=main, stdout=output, stderr=error)
            step["pid"] = process.pid
            record()
            code = process.wait()
        step.update(exit_code=code, ended_native_ns=time.time_ns(), stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
        if code == 0:
            step["boundary"] = snapshot(main)
            if step["boundary"]["attempt_count"] >= 1:
                (main / "generator-parent-exit.txt").write_text("0\n")
        record()
        print(json.dumps(step, sort_keys=True), flush=True)
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prior-chain-root", type=Path)
    parser.add_argument("--pack", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--scenario", choices=("plain", "anchor", "waited"))
    args = parser.parse_args()
    return run(args.out, args.prior_chain_root, args.pack, args.scenario)


if __name__ == "__main__":
    raise SystemExit(main())
