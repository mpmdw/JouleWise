"""Invented Git authority, staged leaves and one-delta filesystem cases."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


PACKET = "series/c1-next-arm.json"
REF = "refs/heads/lite-attempt"
FAMILIES = {
    "c1-code": ("repo", "scripts/registered_tool.py"),
    "c1-policy": ("repo", "configs/campaign_policies/quiet_mac_p2_production.json"),
    "c1-head-pin": ("repo", "configs/calibration/calibration_ledger_head.json"),
    "c1-derivation": ("repo", "configs/campaigns/fixture-derivation/settled_corpus.json"),
    "c2-dispatch": ("stage", "pack/members/second/order_manifest.json"),
    "c2-identity": ("stage", "inputs/identity-epoch.json"),
    "c2-ledger": ("stage", "ledger/live.jsonl"),
    "c2-packet": ("stage", PACKET),
}
OPERATIONS = ("missing", "modified", "extra-file", "symlink-escape")
CONTROLS = ("copy", "repo-link", "stage-dir-link", "executable-bit", "dir-link-escape")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def git(root, *args):
    env = {
        "PATH": os.defpath, "HOME": str(root.parent), "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TEMPLATE_DIR": "", "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": "Fixture", "GIT_COMMITTER_NAME": "Fixture",
        "GIT_AUTHOR_EMAIL": "fixture@invalid", "GIT_COMMITTER_EMAIL": "fixture@invalid",
        "GIT_AUTHOR_DATE": "2001-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2001-01-01T00:00:00Z",
    }
    return subprocess.check_output(["git", "-C", root, *args], env=env).decode().strip()


def history(suite, dest):
    dest.mkdir()
    git(dest, "init", "--bare", "-q", "--object-format=sha1")
    bundle = str(suite / "history.bundle")
    git(dest, "bundle", "verify", bundle)
    for row in git(dest, "bundle", "unbundle", bundle).splitlines():
        oid, ref = row.split()
        if ref.startswith("refs/"):
            git(dest, "update-ref", ref, oid)
    git(dest, "symbolic-ref", "HEAD", "refs/heads/invented-c1")
    ids = json.loads((suite / "history-identity.json").read_bytes())
    if (git(dest, "rev-parse", "HEAD"), git(dest, "rev-parse", ids["pushed_ref"])) != (
            ids["series_commit"], ids["record_commit"]):
        raise ValueError("synthetic history identity differs")


def seed(base):
    authority = base / "authority"
    stage = base / "stage"
    authority.mkdir(parents=True)
    git(authority, "init", "-q", "-b", "execution", "--object-format=sha1")
    pins = {}
    for family, (scope, name) in FAMILIES.items():
        if name == PACKET:
            continue
        data = b"" if family == "c2-ledger" else encode({"fixture": family})
        if scope == "repo":
            put(authority / name, data)
        else:
            put(stage / name, data)
            pins[name] = sha(data)

    # Both transport controls preserve the original logical names and bytes.
    code = authority / FAMILIES["c1-code"][1]
    code.chmod(0o755)
    shutil.copy2(code, code.with_name("same_bytes.py"))
    identity = FAMILIES["c2-identity"][1]
    put(authority / "prepared-mirror" / Path(identity).name, (stage / identity).read_bytes())
    put(authority / ".gitignore", b".unlisted*\n")
    git(authority, "add", "-A")
    git(authority, "commit", "-qm", "Invented execution inputs")
    commit = git(authority, "rev-parse", "HEAD")
    tree = git(authority, "rev-parse", "HEAD^{tree}")
    shutil.copytree(authority, base / "repo", ignore=shutil.ignore_patterns(".git"))

    closure = {"schema": "joulewise.c1_staged_closure.v1",
               "repo": {"object_format": "sha1", "commit": commit, "tree": tree},
               "stage_files": pins}
    raw = encode({"c1_closure": closure})
    put(stage / PACKET, raw)
    git(authority, "switch", "-qc", REF.removeprefix("refs/heads/"))
    put(authority / PACKET, raw)
    git(authority, "add", PACKET)
    git(authority, "commit", "-qm", "Finalize invented attempt after prepare")
    delivery = git(authority, "rev-parse", REF)
    git(authority, "switch", "-q", "execution")
    return {"git": authority, "commit": commit, "delivery_ref": REF,
            "delivery_commit": delivery, "packet": PACKET}


def vectors():
    for family in FAMILIES:
        for op in OPERATIONS:
            yield family, op
    for op in CONTROLS:
        yield "walk", op


def view(base, work, authority, family, op):
    for root in ("repo", "stage"):
        shutil.copytree(base / root, work / root)
    outside = work / "outside"
    outside.mkdir()
    if family in FAMILIES:
        root, name = FAMILIES[family]
        path = work / root / name
        if op == "missing":
            path.unlink()
        elif op == "modified":
            put(path, path.read_bytes() + b"\n")
        elif op == "extra-file":
            put(path.parent / ".unlisted-extra", b"unused")
        elif op == "symlink-escape":
            target = outside / path.name
            shutil.copy2(path, target)
            path.unlink()
            path.symlink_to(target)
        else:
            raise ValueError(op)
    elif op in ("repo-link", "executable-bit"):
        code = work / "repo" / FAMILIES["c1-code"][1]
        if op == "repo-link":
            code.unlink()
            code.symlink_to("same_bytes.py")
        else:
            code.chmod(0o644)
    elif op in ("stage-dir-link", "dir-link-escape"):
        inputs = work / "stage" / "inputs"
        target = work / "repo" / "prepared-mirror"
        if op == "dir-link-escape":
            target = outside / "mirror"
            shutil.copytree(inputs, target)
        shutil.rmtree(inputs)
        inputs.symlink_to(target, target_is_directory=True)
    elif op != "copy":
        raise ValueError(op)
    return {**authority, "repo": work / "repo", "stage": work / "stage"}
