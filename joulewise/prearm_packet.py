"""Immutable, content-bound memoization of OFF-HOST static arm checks.

The caller supplies a reviewed recipe and an independently pinned packet
digest. Neither a packet nor its check names confer arm/GO authority. Physical
observations, notices, native qualification and single-use receipts cannot be
cached here. Paths embedded in a plan are data; they are never followed.
"""

import base64
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import uuid

from joulewise.night_gate import PLAN_MAX_AGE_S

SCHEMA = "joulewise.prearm_packet.v1"
RECIPE_SCHEMA = "joulewise.prearm_recipe.v1"
CHECKS = {"kit_regeneration", "plan_identity", "receipt_validation", "static_config"}


class PacketError(ValueError):
    pass


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise PacketError("expected finite epoch/duration")
    return value


def _relative(value):
    if (not isinstance(value, str) or not value or "\\" in value
            or value != PurePosixPath(value).as_posix()
            or PurePosixPath(value).is_absolute()
            or any(part in {"..", ".git", "restricted", "night-custody", "night-archive"}
                   for part in PurePosixPath(value).parts)):
        raise PacketError("unsafe static input path")
    return value


def _path(root, relative):
    relative = _relative(relative)
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise PacketError("symlink in static inputs: " + relative)
    return path


def _read(path, limit=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise PacketError("static input is not a regular file")
        raw = stream.read() if limit is None else stream.read(limit + 1)
    if limit is not None and len(raw) > limit:
        raise PacketError("packet exceeds size limit")
    return raw


def _root(value):
    root = Path(value).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise PacketError("static root must be an unsymlinked directory")
    return root


def _recipe(recipe):
    fields = {"schema", "identity", "plan", "files", "trees", "checks", "receipts", "not_after_epoch_s"}
    if not isinstance(recipe, dict) or set(recipe) != fields or recipe["schema"] != RECIPE_SCHEMA:
        raise PacketError("invalid recipe schema/fields")
    identity = recipe["identity"]
    if (not isinstance(identity, dict) or set(identity) != {"plan_id", "repo_head", "measurement_head"}
            or not isinstance(identity["plan_id"], str) or not identity["plan_id"]
            or any(not isinstance(identity[k], str) or not re.fullmatch("[0-9a-f]{40}", identity[k])
                   for k in ("repo_head", "measurement_head"))):
        raise PacketError("invalid identity pins")
    _relative(recipe["plan"])
    _number(recipe["not_after_epoch_s"])
    for key in ("files", "trees"):
        paths = recipe[key]
        if not isinstance(paths, list) or len(paths) != len(set(paths)):
            raise PacketError("invalid file/tree inventory")
        for path in paths:
            _relative(path)
    if not isinstance(recipe["receipts"], list):
        raise PacketError("invalid receipt freshness clauses")
    for receipt in recipe["receipts"]:
        if not isinstance(receipt, dict) or set(receipt) not in ({"path", "expires_field"}, {"path", "immutable"}):
            raise PacketError("receipt needs expiry or explicit immutable classification")
        _relative(receipt["path"])
        if "immutable" in receipt:
            if receipt["immutable"] is not True:
                raise PacketError("invalid immutable classification")
        elif not isinstance(receipt["expires_field"], str) or not receipt["expires_field"]:
            raise PacketError("invalid receipt expiry field")
    checks = recipe["checks"]
    if (not isinstance(checks, list) or len(checks) != len(CHECKS)
            or any(not isinstance(check, dict) or set(check) != {"name", "argv", "timeout_s"} for check in checks)
            or {check["name"] for check in checks} != CHECKS):
        raise PacketError("all four reviewed static checks are required")
    for check in checks:
        argv = check["argv"]
        if (not isinstance(argv, list) or not argv or argv[0] != "{python}"
                or any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in argv)
                or _number(check["timeout_s"]) <= 0):
            raise PacketError("static checks require an explicit offline Python argv and positive timeout")
        # No shell, -c, -m, PATH-selected program or unbound entry script.
        scripts = [arg for arg in argv[1:] if arg.startswith("{root}/") and arg.endswith(".py")]
        if not scripts or argv[1:1 + argv[1:].index(scripts[0])] not in ([], ["-B"]):
            raise PacketError("static check must execute a bound Python script")
        for arg in scripts:
            _relative(arg[len("{root}/"):])


def _snapshot(root, recipe):
    paths = set(recipe["files"])
    directories = set()
    for directory in recipe["trees"]:
        pending = [_path(root, directory)]
        while pending:
            current = pending.pop()
            if not current.is_dir():
                raise PacketError("static tree is not a directory")
            directories.add(current.relative_to(root).as_posix())
            for child in sorted(current.iterdir()):
                relative = child.relative_to(root).as_posix()
                # Reject forbidden names BEFORE touching the child.
                safe = _path(root, relative)
                if safe.is_dir():
                    pending.append(safe)
                else:
                    paths.add(relative)
    required = {recipe["plan"], *(r["path"] for r in recipe["receipts"])}
    required.update(arg[len("{root}/"):] for c in recipe["checks"] for arg in c["argv"]
                    if arg.startswith("{root}/") and arg.endswith(".py"))
    if not required <= paths:
        raise PacketError("plan, receipts and check programs must be inventoried")
    snapshot = {path: {"sha256": _sha(_read(_path(root, path))), "kind": "file",
                       "executable": bool(_path(root, path).stat().st_mode & 0o111)}
                for path in sorted(paths)}
    snapshot.update({path: {"kind": "directory"} for path in sorted(directories)})
    return snapshot


def _identity_and_expiry(root, recipe):
    plan = json.loads(_read(_path(root, recipe["plan"])))
    if not isinstance(plan, dict) or any(plan.get(k) != v for k, v in recipe["identity"].items()):
        raise PacketError("plan identity mismatch")
    head = subprocess.run(["git", "--no-optional-locks", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, check=True, timeout=30).stdout.decode().strip()
    if head != recipe["identity"]["measurement_head"]:
        raise PacketError("measurement HEAD mismatch")
    authored = _number(plan.get("authored_epoch_s"))
    expiry = min(recipe["not_after_epoch_s"], authored + PLAN_MAX_AGE_S)
    for receipt in recipe["receipts"]:
        if "expires_field" in receipt:
            value = json.loads(_read(_path(root, receipt["path"])))
            if not isinstance(value, dict):
                raise PacketError("receipt must be an object")
            expiry = min(expiry, _number(value.get(receipt["expires_field"])))
    return authored, expiry


def run_checks(root, recipe):
    """Run the original validators in recipe order and retain exact output bytes."""
    _recipe(recipe)
    root = _root(root)
    results = []
    for check in recipe["checks"]:
        argv = [arg.replace("{python}", sys.executable).replace("{root}", str(root)) for arg in check["argv"]]
        completed = subprocess.run(argv, cwd=root, capture_output=True, check=False,
                                   timeout=check["timeout_s"], env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if completed.returncode != 0:
            raise PacketError(f"static check {check['name']} refused (exit {completed.returncode})")
        results.append({"name": check["name"], "exit_code": completed.returncode,
                        "stdout_b64": base64.b64encode(completed.stdout).decode(),
                        "stderr_b64": base64.b64encode(completed.stderr).decode()})
    return results


def build(root, recipe, output, *, now=None):
    """Run off-host checks once; atomically publish new read-only bytes, never replace."""
    _recipe(recipe)
    root = _root(root)
    issued = _number(time.time() if now is None else now)
    before = _snapshot(root, recipe)
    authored, expires = _identity_and_expiry(root, recipe)
    if not authored <= issued < expires:
        raise PacketError("pre-arm inputs stale or future-dated")
    results = run_checks(root, recipe)
    if _snapshot(root, recipe) != before or _identity_and_expiry(root, recipe) != (authored, expires):
        raise PacketError("static inputs changed during validation")
    if now is None and not issued <= time.time() < expires:
        raise PacketError("packet expired during validation")
    document = {"schema": SCHEMA, "recipe_sha256": _sha(canonical(recipe)),
                "issued_epoch_s": issued, "expires_epoch_s": expires,
                "inputs": before, "results": results}
    raw = canonical(document)
    output = Path(output)
    temporary = output.parent / (".prearm-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        os.link(temporary, output)  # O_EXCL publication, including concurrent builders.
        fd = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)
    return _sha(raw)


def verify(root, recipe, packet, expected_sha256, *, now=None):
    """Rehash the full inventory and freshness bindings; never execute validators.

    expected_sha256 MUST come from reviewed handoff/notice custody, never an
    adjacent untrusted sidecar. The recipe MUST be the independently reviewed
    dependency closure, including validator source, configs and receipt bytes.
    """
    _recipe(recipe)
    root = _root(root)
    observed = _number(time.time() if now is None else now)
    raw = _read(Path(packet), 16 * 1024 * 1024)
    if not isinstance(expected_sha256, str) or _sha(raw) != expected_sha256:
        raise PacketError("packet digest mismatch")
    document = json.loads(raw)
    if (not isinstance(document, dict) or set(document) != {
            "schema", "recipe_sha256", "issued_epoch_s", "expires_epoch_s", "inputs", "results"}
            or document["schema"] != SCHEMA or canonical(document) != raw
            or document["recipe_sha256"] != _sha(canonical(recipe))):
        raise PacketError("packet schema/recipe mismatch")
    issued, expires = _number(document["issued_epoch_s"]), _number(document["expires_epoch_s"])
    if not issued <= observed < expires:
        raise PacketError("packet stale or future-dated")
    if document["inputs"] != _snapshot(root, recipe):
        raise PacketError("static input digest/inventory mismatch")
    authored, current_expiry = _identity_and_expiry(root, recipe)
    if not authored <= issued or expires != current_expiry:
        raise PacketError("packet freshness bindings changed")
    if now is None and not observed <= time.time() < expires:
        raise PacketError("packet expired during verification")
    return document["results"]
