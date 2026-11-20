"""A self-contained copy of the look's pinned files, for tests of the entry points' pin checks.

``mini_repo(test)`` copies every file lm-interim-01 pins (look code, dependencies, schemas, the step 3 file), the
manifest, LOOKS.json and the cited evidence into a temporary directory. A pinned file this branch does not carry
(the analyst seat's fit_interim.py and cadence_look_run.py live on PR #795) is written as a stub. It then re-pins
the copy with the real ``pin --write``, so the copy's manifest, LOOKS.json and files agree. Entry points are run
from the copy as files under ``-I``, so ``verify_pins`` checks the copy's own bytes. Synthetic only.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from joulewise.cadence_looks import manifest as lm

REPO = Path(__file__).resolve().parents[2]
LOOKS_DIR = "docs/process/cadence/looks"
MANIFEST = f"{LOOKS_DIR}/lm-interim-01.json"
STUB = "# stub: the pinned file lives on another branch (PR #795)\n"


def mini_repo(test):
    root = Path(tempfile.mkdtemp(prefix="lm-mini-"))
    test.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
    doc = json.loads((REPO / MANIFEST).read_text(encoding="utf-8"))
    paths = {path for _, path, _ in lm.code_refs(doc)} | set(lm.EVIDENCE) | {MANIFEST, lm.LOOK_LEDGER_PATH}
    for rel in sorted(paths):
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if (REPO / rel).is_file():
            shutil.copyfile(REPO / rel, dst)
        else:
            dst.write_text(STUB, encoding="utf-8")
    run([sys.executable, "-B", str(root / "scripts/cadence_look_manifest.py"), "pin", str(root / MANIFEST),
         "--repo", str(root), "--write"], root, check=True)
    return root


def run(argv, cwd, check=False):
    r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=300)
    if check and r.returncode != 0:
        raise AssertionError(f"{argv[2:4]} exit {r.returncode}: {r.stdout[-800:]} {r.stderr[-800:]}")
    return r


def py(root, rel, *args):
    """Run a copied entry point as a file under -I, from outside the copy."""
    return run([sys.executable, "-I", "-B", str(root / rel), *map(str, args)], tempfile.gettempdir())


def commit(root, *, stage1_sha256=None, roster_sha256=None):
    """Mark the copy's manifest committed (status and LOOKS.json row), as the lead's commit would."""
    m = root / MANIFEST
    doc = json.loads(m.read_text(encoding="utf-8"))
    doc["status"] = "committed"
    m.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    looks = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
    row = next(r for r in looks["looks"] if r["look_id"] == doc["look_id"])
    row.update(sha256=lm.sha256_file(m), status="committed")
    if stage1_sha256:
        row.update(status="stage1_committed", stage1_sha256=stage1_sha256, roster_sha256=roster_sha256 or "0" * 64)
    (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
