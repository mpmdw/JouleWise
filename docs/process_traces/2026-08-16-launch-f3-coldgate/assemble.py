#!/usr/bin/env python3
"""Mechanical non-author assembly for the F3 third-failure cold gate.

Copies the named primary artifacts VERBATIM and emits a SHA-256 manifest.
No editorial content is generated; the file list below is the complete input.
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path

SP = Path("/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad")
WT = Path("/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/wo-launch")
OUT = Path(sys.argv[1])
ARTIFACTS = {
    "01-lensB-contract-report.md": SP / "sol-lensB-contract.md",
    "02-lensB-execution-report.md": SP / "sol-lensB-execution.md",
    "03-fix1-prompt.md": SP / "wo-launch-fix1-prompt.md",
    "04-delta1-report.md": SP / "sol-deltaB.md",
    "05-escalation-consult-prompt.md": SP / "consultB-f3-prompt.md",
    "06-escalation-consult-report.md": SP / "sol-consultB-f3.md",
    "07-fix2-prompt.md": SP / "wo-launch-fix2-prompt.md",
    "08-fix2-report.md": SP / "sol-launch-fix2.md",
    "09-fix2b-report.md": SP / "sol-launch-fix2b.md",
    "10-delta2-report.md": SP / "sol-deltaB2.md",
}
manifest = {}
for name, src in ARTIFACTS.items():
    shutil.copy(src, OUT / name)
    manifest[name] = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
diff = subprocess.run(["git", "-C", str(WT), "diff", "origin/main...HEAD"], capture_output=True, text=True, check=True).stdout
(OUT / "11-branch-full-diff.patch").write_text(diff)
manifest["11-branch-full-diff.patch"] = hashlib.sha256(diff.encode()).hexdigest()
head = subprocess.run(["git", "-C", str(WT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
manifest["_branch_head"] = head
(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("assembled", len(ARTIFACTS) + 1, "artifacts at head", head)
