#!/usr/bin/env python3
"""Run a fresh synthetic R12 cohort and verify it after its writers exit.

This is external scheduling only. The existing generator supplies declared
inputs to the unmodified pinned chain. No session tree is repaired, resumed,
copied from an interrupted cohort, or post-processed by this runner.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from b6_r12_verify import REPO, safe_root, sha
from b6_r12_chain_fixture import PIN


def run_batch(root):
    root = safe_root(root)
    if root.exists():
        raise ValueError("a new cohort root is required; interrupted outputs are never resumed")
    root.mkdir()
    paths = {"seed": root / "seed", "main": root / ("nine-" + "long-path-" * 18),
             "denied": root / "denied"}
    env = {**os.environ, "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    for name in ("R12_TRACE_STACKS", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME"):
        env.pop(name, None)
    manifest = {"schema": "r12.cohort.v1", "synthetic_only": True, "pin": PIN,
        "generator_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO,
                                                    env=env, text=True).strip(),
        "runner_sha256": sha(Path(__file__)),
        "paths": {key: str(path) for key, path in paths.items()},
        "pre_run_prediction_sources": {name: sha(REPO / name) for name in (
            "tests/test_b6_r12_session_fixture.py", "docs/run_reports/2026-11-11-p1-b6-r12-r3.md")},
        "prior_interrupted_inputs": "none; fresh pinned prerequisite writers run first",
        "phase": "prerequisite", "children": {}}
    manifest_path = root / "batch.json"

    def record():
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    def start(name, argv):
        out, err = root / (name + ".stdout"), root / (name + ".stderr")
        with out.open("wb") as stdout, err.open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr)
        manifest["children"][name] = {"argv": argv, "pid": process.pid,
            "started_native_ns": time.time_ns(), "stdout": str(out), "stderr": str(err)}
        record()
        return process

    def ended(name, process, destination):
        code = process.wait()
        manifest["children"][name].update(exit_code=code, ended_native_ns=time.time_ns(),
            stdout_sha256=sha(root / (name + ".stdout")), stderr_sha256=sha(root / (name + ".stderr")))
        # These receipts are outside every chain-produced tree. A missing
        # root cannot receive a successful receipt after a startup failure.
        if destination.is_dir():
            (destination / "generator-parent-exit.txt").write_text(str(code) + "\n")
        record()
        return code

    def generator(name, *options):
        return [sys.executable, "-B", str(REPO / "scripts/b6_r12_session_fixture.py"),
                "--out", str(paths[name]), "--synthetic-models", "--volume", "prerequisite", *options]

    record()  # Predictions and all fresh destinations are written before the first chain runs.
    seed = start("seed", generator("seed", "--seed-probe"))
    if ended("seed", seed, paths["seed"]) != 0:
        manifest["phase"] = "prerequisite_failed"
        record()
        return 2
    manifest["phase"] = "collection"
    children = {"main": start("main", generator("main", "--nine-session-set",
                                               "--prior-chain-root", str(paths["seed"]))),
                "denied": start("denied", generator("denied", "--loop-probe", "alpha",
                    "--deny-normal-session", "--prior-chain-root", str(paths["seed"])))}
    pending = dict(children)
    while pending:
        for name, process in list(pending.items()):
            if process.poll() is not None:
                ended(name, process, paths[name])
                del pending[name]
        if pending:
            time.sleep(2)
    if any(manifest["children"][name]["exit_code"] != 0 for name in children):
        manifest["phase"] = "collection_failed"
        record()
        return 2
    manifest["phase"] = "verification"
    record()
    # Import verification in a fresh interpreter after collection; implementation
    # increments during a long collection must never be attributed to old code.
    verifier = start("finish", [sys.executable, "-B", str(REPO / "scripts/b6_r12_finish.py"),
        "--root", str(paths["main"]), "--denied-root", str(paths["denied"])])
    code = verifier.wait()
    manifest["children"]["finish"].update(exit_code=code, ended_native_ns=time.time_ns(),
        stdout_sha256=sha(root / "finish.stdout"), stderr_sha256=sha(root / "finish.stderr"))
    (paths["main"] / "finish-parent-exit.txt").write_text(str(code) + "\n")
    manifest["phase"] = "complete" if code == 0 else "verification_failed"
    record()
    print(json.dumps({"root": str(root), "phase": manifest["phase"], "exit_code": code}, sort_keys=True))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="new resolved directory under resolved TMPDIR")
    return run_batch(parser.parse_args().out)


if __name__ == "__main__":
    raise SystemExit(main())
