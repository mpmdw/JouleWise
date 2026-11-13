"""Exact historical completed-session profiles admitted by RL-123, reader only.

This never authorizes generation or continuation. Original archive and state
bytes are unchanged. Listed generator hashes are authenticated by Git blobs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from b6_r12_chain_fixture import PIN
from b6_r12_segments import snapshot
from b6_r12_verify import REPO, child, sha

PROFILES = {
    "04eacce2afb5a5b7e5abae12d2d17ba11d39d9f8": (
        "beta-air-23", "beta", "14ec9e7dfd310e3660bd338e9156f632cbcb941ef9ab66414d654b0f88e7fc98"),
    "68be80a79f396cefd4e02d8143c0208d661d91ff": (
        "alpha-mbp-1", "alpha", "14ec9e7dfd310e3660bd338e9156f632cbcb941ef9ab66414d654b0f88e7fc98"),
    "27897044d0b7b6c34501b537a0746cd4f386e656": (
        "gamma-mbp-2", "gamma", "a08bc6ea3984a1f60ab92d92ca8662e2d0622d2c1e0b4671d019ee12110f0ad1"),
}
FILES = ("b6_r12_chain_fixture.py", "b6_r12_courier_profile.py", "b6_r12_orchestrate.py",
         "b6_r12_profile_session.py", "b6_r12_runtime.py", "b6_r12_session_fixture.py", "b6_r12_verify.py")
COPIES = {"runtime.py": "b6_r12_runtime.py", "arm_sources.py": "b6_r12_chain_fixture.py",
          "b6_r12_orchestrate.py": "b6_r12_orchestrate.py",
          "b6_r12_courier_profile.py": "b6_r12_courier_profile.py"}
LOADED_SHA = sha(Path(__file__))


def source_hashes(commit):
    return {name: hashlib.sha256(subprocess.check_output(
        ["git", "--no-replace-objects", "show", commit + ":scripts/" + name], cwd=REPO)).hexdigest()
        for name in FILES}


def validate_completed_profile(root, control):
    if sha(Path(__file__)) != LOADED_SHA:
        raise ValueError("reload changed historical-profile reader")
    steps = control["steps"]
    if not steps or steps[-1].get("exit_code") != 0 or "boundary" not in steps[-1]:
        raise ValueError("interrupted/failed phase: no completed historical profile")
    if snapshot(root) != steps[-1]["boundary"]:
        raise ValueError("original boundary bytes changed after successful parent exit")
    if (root / "source-stop.json").exists() or (root / "generator-parent-exit.txt").read_text().strip() != "0":
        raise ValueError("completed non-retired parent required")
    manifest = json.loads((root / "manifest.json").read_bytes())
    if manifest.get("pin") != PIN or manifest.get("synthetic_only") is not True:
        raise ValueError("synthetic pinned manifest required")
    commit = manifest.get("generator_commit")
    if commit not in PROFILES:
        raise ValueError("unlisted historical generator profile")
    name, pack, runtime = PROFILES[commit]
    if manifest.get("runtime_sha256") != runtime:
        raise ValueError("historical runtime hash does not match listed profile")
    expected = source_hashes(commit)
    if expected["b6_r12_runtime.py"] != runtime or manifest.get("generator_files_sha256") != expected:
        raise ValueError("historical generator hashes differ from recorded Git blobs")
    for copy, original in COPIES.items():
        if sha(child(root, str(root / copy))) != expected[original]:
            raise ValueError("historical source copy altered: " + copy)
    return {"name": name, "pack": pack, "generator_commit": commit,
            "runtime_sha256": runtime, "git_blob_sha256": expected,
            "guard_sha256": LOADED_SHA, "generation_resume_authorized": False}
