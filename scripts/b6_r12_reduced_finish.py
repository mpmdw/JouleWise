#!/usr/bin/env python3
"""Verify reduced R12 coverage; explicitly leave the full-volume gate open."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from b6_r12_finish import agree
from b6_r12_verify import REPO, finalize_manifest, run_option_c, safe_root, sha, write_observations


def finish(root, denied):
    for path in (root, denied):
        if ((path / "generator-parent-exit.txt").read_text().strip() != "0"
                or (path / "source-stop.json").exists()):
            raise ValueError("completed non-retired generator required")
    if json.loads((root / "loop/state.json").read_bytes())["state"] != "DONE":
        raise ValueError("original reduced-set loop is not DONE")
    manifest = json.loads((root / "manifest.json").read_bytes())
    if manifest.get("reduced_set", {}).get("full_volume_claim") is not False:
        raise ValueError("explicit reduced-volume declaration required")
    if sha(root / "bootstrap.py") != manifest["reduced_set"]["bootstrap_sha256"]:
        raise ValueError("declared external source supplier changed")
    for path in (root, denied):
        finalize_manifest(path)
    run_option_c(root, 1)
    serial = agree(root, "option-c")
    if serial["sessions"] != 9 or not serial["closed"]:
        raise ValueError("closed nine required")
    run_option_c(root, 2, stem="option-c-pool")
    agree(root, "option-c-pool")
    proofs = {}
    for name in ("numbers", "public"):
        first, second = root / f"option-c-{name}.json", root / f"option-c-pool-{name}.json"
        if first.read_bytes() != second.read_bytes():
            raise ValueError("serial/pool bytes differ: " + name)
        proofs[name] = {"sha256": sha(first), "bytes": first.stat().st_size}
    for sid, stem in (("r1-alpha", "option-c-skips"),):
        run_option_c(root, 1, stem=stem, session_id=sid)
        agree(root, stem)
    for sid in ("r2-alpha", "r2-beta", "r1-beta", "r1-gamma"):
        metadata = json.loads((root / "sessions" / sid / "session.json").read_bytes())
        if metadata["paths"]["archive"] not in serial["archives"]:
            stem = "option-c-" + sid
            run_option_c(root, 1, stem=stem, session_id=sid)
            agree(root, stem)
    run_option_c(denied, 1, stem="option-c-denied", session_id="r1-alpha")
    agree(denied, "option-c-denied")
    write_observations(root, denied)
    names = ("waited_attempt_n", "wait_cap_and_budget_skips", "unbounded_anchor", "mixed_campaign_rows",
             "desk_compressed_logs_and_plists", "cross_session_gamma", "denied_action_ordinary_session")
    env = {**os.environ, "R12_REAL_CHAIN_SET": str(root), "R12_REDUCED_CHAIN_SET": str(root)}
    assertions = subprocess.run([sys.executable, "-B", "-m", "unittest", *[
        "tests.test_b6_r12_session_fixture.DeclaredShapeTests.test_" + name for name in names]],
        cwd=REPO, env=env, check=False)
    receipt = {"synthetic_only": True, "full_volume_claim": False, "sessions": serial["sessions"],
        "production_exit": serial["exit_code"], "comparator_agrees": serial["option_c"]["comparator"]["pass"],
        "serial_pool_byte_identical": True, "byte_proofs": proofs, "shape_assertion_exit": assertions.returncode,
        "serial_receipt_sha256": sha(root / "option-c-receipt.json"),
        "timing": serial["process_measurement"], "time_wrapper_exit": serial["time_wrapper_exit"],
        "finisher_sha256": sha(Path(__file__)),
        "remaining_gates": ["three full-volume sessions", "canonical nine-session benchmark including full-volume sessions",
                            "Opus cold review"]}
    (root / "reduced-finish-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if assertions.returncode:
        return assertions.returncode
    return subprocess.run([sys.executable, "-B", "-m", "unittest",
        "tests.test_b6_r12_session_fixture.ReducedSetTests"], cwd=REPO, env=env, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--denied-root", required=True)
    args = parser.parse_args()
    return finish(safe_root(args.root), safe_root(args.denied_root))


if __name__ == "__main__":
    raise SystemExit(main())
