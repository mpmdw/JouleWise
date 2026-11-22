#!/usr/bin/env python3
"""Fixed ctl-01 entry point. Run with isolated Python and a registered checkout."""

import hashlib
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import subprocess
import sys


CONTROL = "docs/process/cadence/looks/"
MANIFEST = CONTROL + "lm-ctl-01.json"
SOURCE_INDEX = CONTROL + "lm-ctl-01.sources.json"
LAUNCHER = "scripts/cadence_controls_run.py"
OPERATIONS = ("validate-final", "stage1", "preflight", "stage2", "status")


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
            return handle.read()
    finally:
        os.close(fd)


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


def _registration(root):
    tip = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main^{commit}").decode().strip()
    ledger = json.loads(_git(root, "show", f"{tip}:{CONTROL}LOOKS.json"), object_pairs_hook=_unique)
    row, = (row for row in ledger["looks"] if row["look_id"] == "lm-ctl-01")
    _demand(row["manifest_path"] == MANIFEST and row["status"] == "registered")
    committed = _git(root, "show", f"{tip}:{MANIFEST}")
    _demand(_digest(committed) == row["sha256"])
    manifest = json.loads(committed, object_pairs_hook=_unique)
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
    except (OSError, ValueError, TypeError, KeyError, ImportError, subprocess.SubprocessError):
        os.write(2, b"REFUSE PREFLIGHT FREEZE\n")
        return 2
    return run(argv, root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
