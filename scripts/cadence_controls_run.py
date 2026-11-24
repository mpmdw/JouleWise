#!/usr/bin/env python3
"""Fixed ctl-01 entry point. Run with isolated Python and a registered checkout."""

import hashlib
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


CONTROL = "docs/process/cadence/looks/"
LEDGER = CONTROL + "LOOKS.json"
MANIFEST = CONTROL + "lm-ctl-01.json"
SOURCE_INDEX = CONTROL + "lm-ctl-01.sources.json"
LAUNCHER = "scripts/cadence_controls_run.py"
ORIGIN = "https://github.com/mpmdw/JouleWise.git"
OPERATIONS = ("validate-final", "stage1", "preflight", "stage2", "status")
LOOK = "lm-ctl-01"


class Spent(Exception):
    """A local, committed spend or a stage-1-bound read-start marker."""


def _demand(predicate):
    if not predicate:
        raise ValueError("ctl launcher authentication")


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _unique(items):
    doc = {}
    for key, value in items:
        _demand(key not in doc)
        doc[key] = value
    return doc


def _git(root, *arguments):
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(root), *arguments],
                                   stderr=subprocess.PIPE, env=environment)


def _public_tip():
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    raw = subprocess.check_output(["git", "ls-remote", "--exit-code", ORIGIN, "refs/heads/main"],
                                  cwd="/", env=environment, stderr=subprocess.PIPE, timeout=15)
    revision, ref = raw.decode("ascii").split()
    _demand(ref == "refs/heads/main")
    return revision


def _read(root, name):
    parts = name.split("/")
    _demand(len(parts) >= 2 and all(part not in ("", ".", "..") and "\\" not in part for part in parts))
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        with os.fdopen(os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=fd), "rb") as handle:
            _demand(stat.S_ISREG(os.fstat(handle.fileno()).st_mode))
            return handle.read()
    finally:
        os.close(fd)


def _require_name(parent, name):
    matches = [entry for entry in os.listdir(parent) if entry.casefold() == name.casefold()]
    _demand(matches == [name])


def _exact_open(parent, name, flags):
    fd = os.open(name, flags | os.O_NOFOLLOW, dir_fd=parent)
    try:
        _require_name(parent, name)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_started(layout, uid, manifest_sha, stage1_sha):
    """Inspect only the durable marker and the identity of its reservation."""
    path = layout["path"]
    _demand(path.startswith("/") and "\\" not in path)
    parts = path.split("/")[1:]
    _demand(all(part not in ("", ".", "..") for part in parts))
    dir_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent = os.open("/", dir_flags)
    try:
        for part in parts:
            child = _exact_open(parent, part, dir_flags)
            os.close(parent)
            parent = child
        reserved = os.stat("RESTRICTED", dir_fd=parent, follow_symlinks=False)
        _require_name(parent, "RESTRICTED")
        _demand(stat.S_ISDIR(reserved.st_mode))
        fd = _exact_open(parent, "read-started", os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(fd)
            _demand(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
                    and info.st_uid == uid and info.st_nlink == 1 and info.st_dev == reserved.st_dev)
            raw = stream.read(8193)
        marker = dict(look_id=LOOK, manifest_sha256=manifest_sha, stage1_sha256=stage1_sha,
                      device=layout["device"], inode=reserved.st_ino)
        # The registered device is durable across mount renumbering. The
        # reservation inode and same-filesystem relationship must still match.
        return raw == json.dumps(marker, sort_keys=True, separators=(",", ":")).encode()
    finally:
        os.close(parent)


def _check_local_spend(events, manifest, manifest_sha, seen):
    for event in events:
        if event.get("kind") != "stage1" or event.get("manifest_sha256") != manifest_sha:
            continue
        stage1_sha = event.get("stage1_sha256")
        if type(stage1_sha) is not str or re.fullmatch("[0-9a-f]{64}", stage1_sha) is None:
            continue
        binding = (manifest_sha, stage1_sha)
        if binding in seen:
            continue
        seen.add(binding)
        try:
            started = _read_started(manifest["release_layout"]["private"], manifest["execution"]["uid"],
                                    manifest_sha, stage1_sha)
        except (AttributeError, KeyError, OSError, TypeError, ValueError):
            continue
        if started:
            raise Spent()


class VerifiedModule(importlib.abc.Loader):
    def __init__(self, source, origin):
        self.source = source
        self.origin = origin

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        exec(compile(self.source, self.origin, "exec", dont_inherit=True), module.__dict__)


class RegisteredModules(importlib.abc.MetaPathFinder):
    def __init__(self, root, inventory):
        self.root = root
        self.inventory = inventory

    def find_spec(self, fullname, path=None, target=None):
        if fullname != "joulewise" and not fullname.startswith("joulewise."):
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        _demand(spec is not None)
        if spec.origin is None:
            # Namespace packages cannot point to a second worktree or an
            # editable install. They execute no package initializer.
            _demand(all(Path(name).is_relative_to(self.root) for name in spec.submodule_search_locations))
            return spec
        origin = Path(spec.origin)
        name = origin.relative_to(self.root).as_posix()
        _demand(name.endswith(".py") and name in self.inventory)
        raw = _read(self.root, name)
        _demand(_digest(raw) == self.inventory[name])
        spec.loader = VerifiedModule(raw, spec.origin)
        spec.cached = None
        return spec


def _look_events(ledger):
    return [event for event in ledger.get("events", [])
            if type(event) is dict and event.get("look_id") == LOOK]


def _has_spend(events):
    return any(event.keys() == {"look_id", "kind", "manifest_sha256", "stage1_sha256"}
               and event["kind"] in ("first_ctl_read", "published")
               and all(type(event[key]) is str and re.fullmatch("[0-9a-f]{64}", event[key])
                       for key in ("manifest_sha256", "stage1_sha256"))
               for event in events)


def _registered_manifest(root, revision, ledger):
    row, = (row for row in ledger["looks"] if type(row) is dict and row.get("look_id") == LOOK)
    _demand(ledger["schema"] == "joulewise.cadence_look_ledger.v1"
            and row["manifest_path"] == MANIFEST and row["status"] == "registered")
    committed = _git(root, "show", f"{revision}:{MANIFEST}")
    _demand(_digest(committed) == row["sha256"])
    return json.loads(committed, object_pairs_hook=_unique), row["sha256"]


def _require_unspent_ancestry(root, tip):
    # Historical evidence can only deny execution. The authenticated tip and
    # full ledger replay still govern authorization for a fresh look.
    revisions = _git(root, "log", "--first-parent", "--format=%H", tip, "--", LEDGER).decode().splitlines()
    seen = set()
    for revision in revisions:
        try:
            old = json.loads(_git(root, "show", f"{revision}:{LEDGER}"), object_pairs_hook=_unique)
            events = _look_events(old)
            if _has_spend(events):
                raise Spent()
            if any(event.get("kind") == "stage1" for event in events):
                manifest, manifest_sha = _registered_manifest(root, revision, old)
                _check_local_spend(events, manifest, manifest_sha, seen)
        except (AttributeError, KeyError, TypeError, ValueError, subprocess.CalledProcessError):
            continue  # The fully authenticated replay still enforces ledger integrity.


def _registration(root):
    tip = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main^{commit}").decode().strip()
    _require_unspent_ancestry(root, tip)
    ledger = json.loads(_git(root, "show", f"{tip}:{LEDGER}"), object_pairs_hook=_unique)
    manifest, _ = _registered_manifest(root, tip, ledger)
    _demand(tip == _public_tip())
    launcher_pin = manifest["pins"]["print_code/launcher"]
    _demand(_digest(_read(root, LAUNCHER)) == launcher_pin
            and _digest(_git(root, "show", f"{tip}:{LAUNCHER}")) == launcher_pin)
    raw = _git(root, "show", f"{tip}:{SOURCE_INDEX}")
    _demand(_digest(raw) == manifest["execution"]["sources_sha256"])
    inventory = json.loads(raw, object_pairs_hook=_unique)["paths"]
    _demand(inventory[LAUNCHER] == launcher_pin)
    return inventory


def main(argv):
    try:
        _demand(sys.flags.isolated and sys.flags.dont_write_bytecode)
        _demand(len(argv) == 1 and argv[0] in OPERATIONS)
        root = Path(__file__).resolve(strict=True).parents[1]
        _demand(Path(os.path.abspath(__file__)) == root / LAUNCHER)
        inventory = _registration(root)
        _demand(not any(name == "joulewise" or name.startswith("joulewise.") for name in sys.modules))
        sys.path.insert(0, str(root))
        sys.meta_path.insert(0, RegisteredModules(root, inventory))
        from joulewise.cadence_looks.controls_run import main as run
    except Spent:
        os.write(2, b"REFUSE SPENT\n")
        return 3
    except Exception:
        os.write(2, b"REFUSE PREFLIGHT FREEZE\n")
        return 2
    return run(argv, root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
