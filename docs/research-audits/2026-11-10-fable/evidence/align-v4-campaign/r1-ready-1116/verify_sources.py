#!/usr/bin/env python3
"""Check repository source bytes only. Never reads a run, slot or custody file."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def check(root):
    root = Path(root).resolve(strict=True)
    kit = json.loads((HERE / "KIT.json").read_text())
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != kit["measurement_commit"]:
        raise ValueError("HEAD differs from the session pin; lead must adjudicate carry before re-pinning")
    for name, expected in kit["source_sha256"].items():
        path = root / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("source differs: " + name)
    config = json.loads((root / "configs/align/v4/r1_runtime.json").read_text())
    assert config["d_n_chunk"] == 4096
    assert [config["sensors"][r] for r in ("s_fast", "s_slow")] == ["TV0h", "TV1h"]
    assert config["sensors"]["record_keys"] == ["Tf08"]
    assert len(config["r0_classified_keys"]) == 60
    assert {c: list(config["r0_classes"].values()).count(c) for c in ("die", "heatsink")} == {"die": 16, "heatsink": 44}
    registration = root / "configs/campaigns/align_v4/registration"
    if (registration / "ruling_1f_receipt.json").exists() or (registration / "ruling_1f_receipt.json").is_symlink():
        raise ValueError("retired ruling_1f_receipt exists (refused unread)")
    inputs = json.loads((registration / "inputs.json").read_text())
    if "g0_cap_receipt" in (inputs.get("R1", {}).get("thermal_policy") or {}):
        raise ValueError("retired g0_cap_receipt in inputs")
    return {"status": "SOURCE_BYTES_OK_ONLY", "head": head,
            "hashes": len(kit["source_sha256"]), "native_ready": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.root), sort_keys=True))
