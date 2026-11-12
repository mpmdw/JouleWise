#!/usr/bin/env python3
"""Verify two completed R12 shapes at a quiescent scheduler boundary.

This writes analysis receipts beside, never into, original session trees.
It makes no full-volume, closed-nine or overall R12 completion claim.
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
from b6_r12_verify import REPO, child, run_option_c, safe_root, session_facts, sha


def verify(outer, denied, stem):
    outer, denied = safe_root(outer), safe_root(denied)
    if not stem or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in stem):
        raise ValueError("plain new checkpoint name required")
    with (outer / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control = json.loads((outer / "segments.json").read_bytes())
        main = child(outer, control["main"])
        validate_resume(main, control)
        state = control["steps"][-1]["boundary"]["state"]
        if state not in {"ROTATE", "DONE"}:
            raise ValueError("ordinary desk must have completed before checkpoint verification")
        if ((denied / "generator-parent-exit.txt").read_text().strip() != "0"
                or (denied / "source-stop.json").exists()):
            raise ValueError("completed non-retired denied fixture required")
        view = outer / stem
        if view.exists():
            raise ValueError("new checkpoint output directory required")
        view.mkdir()
        declarations = {"synthetic_only": True, "kind": "partial shape verification, not a session",
            "source_root": str(main), "denied_root": str(denied), "script_sha256": sha(Path(__file__)),
            "boundary": control["steps"][-1]["boundary"],
            "prediction": "original named skip and denied tests pass with production exit 0/comparator agreement",
            "full_volume_claim": False, "closed_nine_claim": False}
        (view / "declaration.json").write_text(json.dumps(declarations, indent=2, sort_keys=True) + "\n")
        observed = {}
        receipts = {}
        for label, root, run_stem in (("r12-skips", main, stem + "-skips"),
                                      ("r12-denied-action", denied, stem + "-denied")):
            run_option_c(root, 1, stem=run_stem, session_id="r1-alpha")
            receipt = agree(root, run_stem)
            facts = session_facts(root, "r1-alpha")
            value = {"flags": facts["flags"], "production_exit": receipt["exit_code"],
                "comparator_agrees": receipt["option_c"]["comparator"]["pass"],
                "archive": facts["archive"], "real_loop_attempt": facts["real_loop_attempt"],
                "receipt_sha256": sha(root / (run_stem + "-receipt.json"))}
            if label == "r12-denied-action":
                value["off_action_returncode"] = next((a.get("returncode") for a in facts["off_actions"]), None)
            observed[label] = value
            receipts[label] = {"measurement": receipt["process_measurement"],
                               "time_wrapper_exit": receipt["time_wrapper_exit"],
                               "receipt_sha256": value["receipt_sha256"]}
        # This is a report view of authenticated writer outputs, not a new
        # archive, altered loop log, invented verdict or session fixture.
        (view / "observations.json").write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n")
        tests = ["tests.test_b6_r12_session_fixture.DeclaredShapeTests.test_" + name for name in (
            "wait_cap_and_budget_skips", "denied_action_ordinary_session")]
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=REPO,
            env={**os.environ, "R12_REAL_CHAIN_SET": str(view)}, check=False)
        (view / "receipt.json").write_text(json.dumps({**declarations, "test_exit": result.returncode,
            "tests": tests, "program_receipts": receipts, "observations_sha256": sha(view / "observations.json")},
            indent=2, sort_keys=True) + "\n")
        return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", type=Path, required=True)
    parser.add_argument("--denied-root", type=Path, required=True)
    parser.add_argument("--stem", required=True)
    args = parser.parse_args()
    return verify(args.cohort_root, args.denied_root, args.stem)


if __name__ == "__main__":
    raise SystemExit(main())
