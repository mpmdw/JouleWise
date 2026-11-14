#!/usr/bin/env python3
"""Verify an already completed BETA anchor fixture, never generate a session.

Analysis receipts live beside the original session trees. This makes no
full-volume, closed-nine or overall R12 completion claim.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

from b6_r12_finish import agree
from b6_r12_segments import validate_resume
from b6_r12_verify import REPO, child, finalize_manifest, run_option_c, safe_root, session_facts, sha

LOADED_SHA = sha(Path(__file__))


def verify(outer, stem):
    outer = safe_root(outer)
    if sha(Path(__file__)) != LOADED_SHA:
        raise ValueError("reload changed single-pack verifier")
    if not stem or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in stem):
        raise ValueError("plain new verification name required")
    with (outer / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control = json.loads((outer / "segments.json").read_bytes())
        main = child(outer, control["main"])
        validate_resume(main, control)
        boundary = control["steps"][-1]["boundary"]
        if boundary["attempt_count"] != 1 or boundary["state"] != "ROTATE":
            raise ValueError("one completed ordinary desk and original attempt required")
        if control.get("pack") != "beta" or control.get("scenario") != "anchor":
            raise ValueError("the three declared tests require the BETA anchor fixture")
        if (main / "generator-parent-exit.txt").read_text().strip() != "0":
            raise ValueError("completed chain parent required")
        view = outer / stem
        view.mkdir(exist_ok=False)
        snapshots = {}
        for key, name in (("loop_state", "state.json"), ("loop_attempts", "attempts.jsonl")):
            source, target = main / "loop" / name, view / name
            target.write_bytes(source.read_bytes())
            if sha(source) != sha(target):
                raise ValueError("literal loop snapshot changed")
            snapshots[key] = {"snapshot": str(target), "sha256": sha(target)}
        declaration = {"synthetic_only": True, "verifier_sha256": LOADED_SHA,
            "literal_loop_inputs": snapshots, "source_root": str(main),
            "boundary": boundary,
            "full_volume_claim": False, "closed_nine_claim": False}
        (view / "declaration.json").write_text(json.dumps(declaration, indent=2, sort_keys=True) + "\n")
        finalize_manifest(main)
        run_option_c(main, 1, stem=stem, session_id="r1-beta")
        receipt = agree(main, stem)
        inputs = json.loads((main / (stem + "-inputs.json")).read_bytes())
        if any(inputs["external"][key] != data["sha256"] for key, data in snapshots.items()):
            raise ValueError("program loop pins differ from literal snapshots")
        facts = session_facts(main, "r1-beta")
        facts.update(production_exit=receipt["exit_code"],
                     comparator_agrees=receipt["option_c"]["comparator"]["pass"])
        (view / "single-observations.json").write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
        tests = ["tests.test_b6_r12_session_fixture.SinglePackShapeTests"]
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=REPO,
            env={**os.environ, "R12_SINGLE_PACK_SET": str(view)}, check=False)
        (view / "receipt.json").write_text(json.dumps({**declaration,
            "test_exit": result.returncode, "tests": tests,
            "observations_sha256": sha(view / "single-observations.json"),
            "program_receipt_sha256": sha(main / (stem + "-receipt.json")),
            "timing": receipt["process_measurement"], "time_wrapper_exit": receipt["time_wrapper_exit"]},
            indent=2, sort_keys=True) + "\n")
        return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", required=True, type=Path)
    parser.add_argument("--stem", required=True)
    args = parser.parse_args()
    return verify(args.cohort_root, args.stem)


if __name__ == "__main__":
    raise SystemExit(main())
