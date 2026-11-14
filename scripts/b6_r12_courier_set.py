#!/usr/bin/env python3
"""Fresh one-runtime R12 cohort; original Loop owns every state and attempt.

The parent records the actual generator-child exit. An existing root is
never restarted. Only generator input suppliers are substituted; every
collection, harvest, acceptance and compression component remains pinned.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import uuid

import b6_r12_reduced_set as inputs
from b6_r12_courier_profile import prepare_profile, export_prompt, bootstrap_text
from b6_r12_segments import snapshot, validate_resume
from b6_r12_verify import REPO, child, safe_root, sha

INITIALIZE_INPUTS = inputs.initialize


def source_bootstrap(schedule):
    text = bootstrap_text()
    if schedule == "reduced":
        prefix = '''import b6_r12_orchestrate as scheduler
original_source_policy = scheduler.session_policy
def reduced_source_policy(pack, round_number, base):
    value = original_source_policy(pack, round_number, base)
    value.update(volume="reduced", primary_stream_duration_s=65,
                 token_first_s=.5, token_next_s=.001)
    return value
scheduler.session_policy = reduced_source_policy
'''
        text = prefix + text
    return text


def initialize(main, prior, declaration):
    prepare, export = inputs.prepare, inputs.export_chain_inputs

    def prepared(root):
        return prepare_profile(prepare(root))

    def exported(root):
        export(root)
        export_prompt(root)

    with patch.object(inputs, "prepare", prepared), \
         patch.object(inputs, "export_chain_inputs", exported), \
         patch.object(inputs, "reduced_bootstrap", lambda: source_bootstrap(declaration["schedule"])):
        INITIALIZE_INPUTS(main, prior)
    policy_path = main / "source-policy.json"
    policy = json.loads(policy_path.read_bytes())
    if declaration["mode"] == "denied":
        policy.update(denied_off=True, denied_normal=True)
    else:
        policy.update(primary_stream_duration_s=65)
    policy_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")
    path = main / "manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest["initialization_supplier"] = manifest.pop("reduced_set")
    manifest["initialization_supplier"]["scope"] = "setup only; active source profile declared in courier_set"
    manifest["volume"] = "reduced" if declaration["schedule"] == "reduced" else "mixed; original per-session schedule"
    manifest["courier_set"] = {**declaration, "base_source_policy": policy,
        "bootstrap_sha256": sha(main / "bootstrap.py"),
        "source_supplier": "generator b6_r12_orchestrate.session_policy; pinned code unchanged",
        "full_volume_claim": declaration["schedule"] == "registered",
        "schedule": declaration["schedule"],
        "primary_dwell": "5 s denied-action only" if declaration["mode"] == "denied" else (
            "65 s all ordinary sessions" if declaration["schedule"] == "reduced" else "original full A3/B1/G1, reduced 65 s elsewhere"),
        "chain_thresholds_rosters_calibration_waits": "unchanged",
        "smoke": "original reduced 65 s source input"}
    manifest["generator_files_sha256"].update({name: sha(REPO / "scripts" / name)
        for name in (Path(__file__).name, "b6_r12_reduced_set.py", "b6_r12_segments.py")})
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def complete(boundary, mode):
    return boundary["state"] == "DONE" if mode == "nine" else (
        boundary["state"] == "ROTATE" and boundary["attempt_count"] == 1)


def generate(outer, prior, declaration):
    main = child(outer, declaration["main"])
    control = {**declaration, "steps": []}
    control_path = outer / "segments.json"

    def record():
        temporary = control_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(control, indent=2, sort_keys=True) + "\n")
        temporary.replace(control_path)

    record()  # Preparation failure is also visibly incomplete.
    initialize(main, prior, declaration)
    pack, limit = ("all", "9") if declaration["mode"] == "nine" else ("alpha", "1")
    while True:
        if control["steps"]:
            validate_resume(main, control)
        index = len(control["steps"]) + 1
        argv = inputs.command(main, "loop-probe", pack, limit, "one")
        step = {"index": index, "argv": argv, "started_native_ns": time.time_ns()}
        control["steps"].append(step)
        record()
        out, err = outer / f"step-{index:03}.stdout", outer / f"step-{index:03}.stderr"
        with out.open("xb") as stdout, err.open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=main, stdout=stdout, stderr=stderr)
            step["pid"] = process.pid
            record()
            code = process.wait()
        step.update(exit_code=code, ended_native_ns=time.time_ns(),
                    stdout_sha256=sha(out), stderr_sha256=sha(err))
        if code == 0:
            step["boundary"] = snapshot(main)
        record()
        print(json.dumps(step, sort_keys=True), flush=True)
        if code or complete(step["boundary"], declaration["mode"]):
            return code


def run(outer, prior, mode, schedule):
    outer, prior = safe_root(outer), safe_root(prior)
    if outer.exists():
        raise ValueError("new absent cohort root required; never resume an inflight journal")
    if mode == "denied" and schedule != "reduced":
        raise ValueError("extra denied-action session is reduced")
    declaration = {"schema": "r12.courier-set.v1", "pin": inputs.PIN,
        "synthetic_only": True, "mode": mode, "schedule": schedule,
        "runner_sha256": sha(Path(__file__)), "runtime_sha256": sha(REPO / "scripts/b6_r12_runtime.py"),
        "main": str(outer / ("nine-" + "long-path-" * 18)),
        "prior_seed": str(prior), "parent_token": uuid.uuid4().hex,
        "prediction": "original closed nine, six predeclared shapes and serial/pool byte equality" if mode == "nine" else
                      "one original ordinary denied-action attempt, off rc 126 and option (c) 0/agrees",
        "prediction_sources": {name: sha(REPO / name) for name in (
            "tests/test_b6_r12_session_fixture.py", "docs/run_reports/2026-11-11-p1-b6-r12-r3.md")}}
    outer.mkdir()
    declaration_path = outer / "declaration.json"
    declaration_path.write_text(json.dumps(declaration, indent=2, sort_keys=True) + "\n")
    journal = outer / "parent.json"
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--out", str(outer),
            "--prior-chain-root", str(prior), "--mode", mode, "--schedule", schedule,
            "--child-token", declaration["parent_token"]]
    value = {"status": "inflight", "argv": argv, "supervisor_pid": os.getpid(),
             "started_native_ns": time.time_ns(), "declaration_sha256": sha(declaration_path)}
    journal.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    process = subprocess.Popen(argv, cwd=REPO)
    value["pid"] = process.pid
    journal.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    code = process.wait()
    if code == 0:
        main = child(outer, declaration["main"])
        control = json.loads((outer / "segments.json").read_bytes())
        validate_resume(main, control)
        if not complete(control["steps"][-1]["boundary"], mode):
            raise ValueError("original loop has not reached its declared completed boundary")
        (main / "generator-parent-exit.txt").write_text("0\n")
    value.update(status="done" if code == 0 else "failed", exit_code=code,
                 ended_native_ns=time.time_ns())
    journal.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps(value, sort_keys=True), flush=True)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prior-chain-root", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("nine", "denied"))
    parser.add_argument("--schedule", required=True, choices=("registered", "reduced"))
    parser.add_argument("--child-token", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child_token:
        outer = safe_root(args.out)
        declaration = json.loads((outer / "declaration.json").read_bytes())
        parent = json.loads((outer / "parent.json").read_bytes())
        if (parent["status"] != "inflight" or parent["supervisor_pid"] != os.getppid()
                or args.child_token != declaration["parent_token"]
                or (args.mode, args.schedule, str(safe_root(args.prior_chain_root))) !=
                   (declaration["mode"], declaration["schedule"], declaration["prior_seed"])
                or declaration["runner_sha256"] != sha(Path(__file__))):
            raise ValueError("owned fresh generator child required; no restart")
        return generate(outer, safe_root(args.prior_chain_root), declaration)
    return run(args.out, args.prior_chain_root, args.mode, args.schedule)


if __name__ == "__main__":
    raise SystemExit(main())
