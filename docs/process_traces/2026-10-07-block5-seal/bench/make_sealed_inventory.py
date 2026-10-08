"""The filled sealed inventory for the block-5 seal commit, from a clean checkout of H_claim.

A file cannot name the commit that contains it. The inventory names H_claim as
its ``head``, so it is generated from a checkout of H_claim and committed in
the next commit, the seal commit (SEAL_LANDING.md, step 4).

It uses the repository's own generator, ``scripts/rehearse_b5_real.py``
``sealed_inventory()``: ``git ls-files`` under ``joulewise/``, ``scripts/`` and
the three pack directories, the SHA-256 of each file's bytes in the working
tree, plus the flag catalog. The working tree must be clean, so those bytes
are the committed bytes. ``tests/test_b5_seal_landing.py`` then recomputes
every digest from git objects at ``head``, an independent second reading.

Usage:
    /opt/homebrew/bin/python3.13 -B make_sealed_inventory.py <clean checkout at H_claim> <out.json>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

checkout, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
sys.dont_write_bytecode = True
sys.path.insert(0, str(checkout))
from scripts.rehearse_b5_real import sealed_inventory  # noqa: E402


def git(*argv: str) -> str:
    return subprocess.run(["git", "-C", str(checkout), *argv], capture_output=True, text=True, check=True).stdout


status = git("status", "--porcelain=v1", "--untracked-files=all")
if status.strip():
    raise SystemExit(f"the checkout is not clean; refusing to hash a working tree that is not a commit:\n{status}")
head = git("rev-parse", "HEAD").strip()
inventory = sealed_inventory(checkout)
files = inventory["files"]
PIN = "configs/calibration/calibration_ledger_head.json"
CATALOG = "configs/campaigns/v5_claim_25g83/flag_catalog.json"
if PIN in files or CATALOG not in files:
    raise SystemExit("the generator's file list is not the registered one (pin listed, or catalog missing)")
document = {"schema_version": inventory["schema_version"], "status": "SEALED", "head": head,
            "files": dict(sorted(files.items()))}
raw = (json.dumps(document, indent=2, sort_keys=True) + "\n").encode()
out.write_bytes(raw)
print(f"head={head} files={len(files)} sha256={hashlib.sha256(raw).hexdigest()} out={out}")
