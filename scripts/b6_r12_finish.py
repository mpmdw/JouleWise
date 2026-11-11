#!/usr/bin/env python3
"""Verify completed, explicitly named synthetic R12 roots without editing archives.

No judgments are cached. Each invocation runs both production recomputations,
the separately selected shape archives, and the predeclared integration tests.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from b6_r12_verify import REPO, finalize_manifest, rows, run_option_c, safe_root, sha, write_observations
LOADED_FINISHER_SHA256 = sha(Path(__file__))


def agree(root, stem):
    receipt = json.loads((root / (stem + "-receipt.json")).read_bytes())
    if receipt["exit_code"] != 0 or not receipt.get("option_c", {}).get("comparator", {}).get("pass"):
        raise RuntimeError("production recomputation did not agree: " + str(root / (stem + "-receipt.json")))
    return receipt


def finish(root, denied):
    if sha(Path(__file__)) != LOADED_FINISHER_SHA256:
        raise RuntimeError("finisher changed after import; reload before producing evidence")
    state = json.loads((root / "loop/state.json").read_bytes())
    if state["state"] != "DONE":
        raise RuntimeError("the original loop has not closed: " + state["state"])
    denied_attempts = rows((denied / "loop/attempts.jsonl").read_bytes())
    if [row["session_id"] for row in denied_attempts] != ["r1-alpha"]:
        raise RuntimeError("one original ordinary denied-action attempt required")
    for path in (root, denied):
        if (path / "source-stop.json").exists():
            raise RuntimeError("retired development source is not final R12 evidence")
        finalize_manifest(path)

    run_option_c(root, 1)
    serial = agree(root, "option-c")
    if serial["sessions"] != 9 or not serial["closed"]:
        raise RuntimeError("nine archives and original closed-loop evidence required")
    run_option_c(root, 2, stem="option-c-pool")
    pooled = agree(root, "option-c-pool")
    proofs = {}
    for name in ("numbers", "public"):
        first = root / ("option-c-" + name + ".json")
        second = root / ("option-c-pool-" + name + ".json")
        if first.read_bytes() != second.read_bytes():
            raise RuntimeError("serial/pool bytes differ: " + name)
        proofs[name] = {"sha256": sha(first), "bytes": first.stat().st_size}

    selected = {"r1-alpha": "option-c-skips"}
    for sid in ("r2-alpha", "r2-beta", "r1-beta", "r1-gamma"):
        metadata = json.loads((root / "sessions" / sid / "session.json").read_bytes())
        if metadata["paths"]["archive"] not in serial["archives"]:
            selected[sid] = "option-c-" + sid
    for sid, stem in selected.items():
        run_option_c(root, 1, stem=stem, session_id=sid)
        agree(root, stem)
    run_option_c(denied, 1, stem="option-c-denied", session_id="r1-alpha")
    denied_receipt = agree(denied, "option-c-denied")
    observed = write_observations(root, denied)
    result = subprocess.run([sys.executable, "-B", "-m", "unittest",
        "tests.test_b6_r12_session_fixture.DeclaredShapeTests"], cwd=REPO,
        env={**os.environ, "R12_REAL_CHAIN_SET": str(root)}, check=False)
    receipt = {"synthetic_only": True, "integration_test_exit": result.returncode,
        "finisher_sha256": LOADED_FINISHER_SHA256,
        "serial_pool_byte_proof": proofs, "serial_receipt_sha256": sha(root / "option-c-receipt.json"),
        "pool_receipt_sha256": sha(root / "option-c-pool-receipt.json"),
        "denied_receipt_sha256": sha(denied / "option-c-denied-receipt.json"),
        "shape_observations_sha256": sha(root / "observations.json"),
        "full_volume_observations_sha256": sha(root / "full-volume-observations.json"),
        "shapes": sorted(observed), "timing": serial["process_measurement"],
        "time_wrapper_exit": serial["time_wrapper_exit"],
        "denied_timing": denied_receipt["process_measurement"]}
    (root / "finish-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if result.returncode:
        raise RuntimeError("predeclared R12 integration expectation failed")
    print(json.dumps(receipt, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--denied-root", required=True)
    args = parser.parse_args()
    finish(safe_root(args.root), safe_root(args.denied_root))


if __name__ == "__main__":
    main()
