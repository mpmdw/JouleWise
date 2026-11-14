#!/usr/bin/env python3
"""Schedule complete pinned-chain phases; never resume an interrupted phase.

Control receipts live beside the chain root. The pinned Loop reads its own
state/attempt log on each invocation; this module never writes either.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from b6_r12_chain_fixture import PIN
from b6_r12_verify import REPO, child, safe_root, sha


def snapshot(root):
    state_path = root / "loop/state.json"
    state = json.loads(state_path.read_bytes())
    attempts = root / "loop/attempts.jsonl"
    result = {"state": state["state"], "state_sha256": sha(state_path),
              "attempts_sha256": sha(attempts) if attempts.exists() else None,
              "attempt_count": len(attempts.read_text().splitlines()) if attempts.exists() else 0}
    session = state.get("session") or {}
    result["session_id"] = session.get("id")
    if state["state"] in {"SMOKE_RUN", "SESSION_RUN"}:
        prefix = "smoke_" if state["state"] == "SMOKE_RUN" else ""
        prepared = session.get(prefix + "prepared") or {}
        terminal = child(root, prepared.get("terminal_path", ""))
        if not session.get(prefix + "handle") or not terminal.is_file():
            raise ValueError("driver boundary lacks original handle/terminal")
        result.update(terminal_path=str(terminal), terminal_sha256=sha(terminal))
    elif state["state"] == "ARM_WAIT":
        if not session.get("smoke_done"):
            raise ValueError("smoke desk boundary lacks original smoke_done")
    elif state["state"] == "ROTATE":
        if not result["attempt_count"]:
            raise ValueError("desk boundary lacks original attempt")
    elif state["state"] != "DONE":
        raise ValueError("not a completed scheduler boundary: " + state["state"])
    return result


def validate_resume(root, control):
    """A plausible original state alone cannot authenticate a stopped parent."""
    steps = control["steps"]
    if not steps or steps[-1].get("exit_code") != 0 or "boundary" not in steps[-1]:
        raise ValueError("interrupted/failed phase: start a fresh cohort, never resume")
    if snapshot(root) != steps[-1]["boundary"]:
        raise ValueError("original boundary bytes changed after successful parent exit")
    if (root / "source-stop.json").exists():
        raise ValueError("retired source cohort")
    manifest = json.loads((root / "manifest.json").read_bytes())
    if manifest.get("pin") != PIN or manifest.get("synthetic_only") is not True:
        raise ValueError("synthetic pinned manifest required")
    for name, expected in manifest["generator_files_sha256"].items():
        if sha(REPO / "scripts" / name) != expected:
            raise ValueError("collection harness changed: " + name)


def run(root, prior=None, denied=None):
    root = safe_root(root)
    fresh = prior is not None
    if fresh:
        if root.exists():
            raise ValueError("new cohort root required")
        prior, denied = safe_root(prior), safe_root(denied)
        for completed in (prior, denied):
            if (completed / "generator-parent-exit.txt").read_text().strip() != "0":
                raise ValueError("prior input did not complete successfully")
            common = json.loads((completed / "manifest.json").read_bytes())
            if common.get("pin") != PIN or common.get("synthetic_only") is not True:
                raise ValueError("prior input is not a pinned synthetic fixture")
        root.mkdir()
    with (root / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control_path = root / "segments.json"
        if fresh:
            control = {"schema": "r12.segments.v1", "pin": PIN, "synthetic_only": True,
                "runner_sha256": sha(Path(__file__)), "steps": [],
                "main": str(root / ("nine-" + "long-path-" * 18)),
                "prior_seed": str(prior), "denied": str(denied),
                "prediction": "same predeclared six R12 shapes; full A3/B1/G1; nine counting sessions; no interrupted-phase reuse",
                "prediction_sources": {name: sha(REPO / name) for name in (
                    "tests/test_b6_r12_session_fixture.py", "docs/run_reports/2026-11-11-p1-b6-r12-r3.md")}}
        else:
            control = json.loads(control_path.read_bytes())
            if control["runner_sha256"] != sha(Path(__file__)):
                raise ValueError("scheduler implementation changed")
            validate_resume(child(root, control["main"]), control)
            if control["steps"][-1]["boundary"]["state"] == "DONE":
                print("original loop is DONE; run b6_r12_finish.py", flush=True)
                return 0
        main = child(root, control["main"])
        index = len(control["steps"]) + 1
        argv = [sys.executable, "-B", str(REPO / "scripts/b6_r12_session_fixture.py"),
                "--out", str(main), "--nine-session-set", "--one-boundary"]
        if fresh:
            argv += ["--synthetic-models", "--volume", "prerequisite", "--prior-chain-root", str(prior)]
        else:
            argv += ["--continue-segment"]
        step = {"index": index, "argv": argv, "started_native_ns": time.time_ns()}
        control["steps"].append(step)

        def record():
            temporary = control_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(control, indent=2, sort_keys=True) + "\n")
            temporary.replace(control_path)

        record()  # Missing finish receipt always forbids continuation.
        env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
        for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "R12_TRACE_STACKS"):
            env.pop(key, None)
        out, err = root / f"step-{index:03}.stdout", root / f"step-{index:03}.stderr"
        with out.open("xb") as stdout, err.open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr)
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
    parser.add_argument("--denied-root", type=Path)
    args = parser.parse_args()
    if bool(args.prior_chain_root) != bool(args.denied_root):
        parser.error("fresh start requires both completed prior roots")
    return run(args.out, args.prior_chain_root, args.denied_root)


if __name__ == "__main__":
    raise SystemExit(main())
