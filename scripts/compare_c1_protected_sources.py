#!/usr/bin/env python3
"""Apply the B1 closure byte freeze to two commits in a local public-code Git repository."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess


REQUIRED_FILES = (
    "joulewise/align/apple/rl176.py",
    "joulewise/align/apple/rl176_phases.py",
    "scripts/align_v4_series_release.py",
)


class InvalidInput(ValueError):
    """An input could not support a complete byte comparison."""


def git(repo, *args, data=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="", GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output([
        "git", "--no-pager", "--no-replace-objects", "--literal-pathspecs", "-C", repo, *args,
    ], input=data, env=env, stderr=subprocess.DEVNULL)


def read_tree(repo, label, commit, oid_pattern):
    if not oid_pattern.fullmatch(commit):
        raise InvalidInput(f"{label} requires a full commit ID")
    try:
        if git(repo, "cat-file", "-t", commit) != b"commit\n":
            raise InvalidInput(f"{label} ID is not a commit")
        entries = git(repo, "ls-tree", "-rz", "--full-tree", commit)
    except (OSError, subprocess.CalledProcessError):
        raise InvalidInput(f"{label} commit or tree is unreadable") from None

    tree = {}
    for entry in entries.split(b"\0")[:-1]:
        metadata, separator, pathname = entry.partition(b"\t")
        path = os.fsdecode(pathname)
        if not separator or not path or path in tree:
            raise InvalidInput(f"{label} tree has ambiguous entries")
        try:
            mode, kind, oid = metadata.decode("ascii").split()
        except ValueError:
            raise InvalidInput(f"{label} tree metadata is malformed") from None
        tree[path] = {"blob": oid, "mode": mode, "kind": kind}
    return tree


def required_file_errors(repo, w1_tree, c1_tree):
    errors = []
    roots = []
    for label, tree in (("W1", w1_tree), ("C1", c1_tree)):
        for path in REQUIRED_FILES:
            entry = tree.get(path)
            if entry is None:
                errors.append(f"{label} {path} is missing")
            elif entry["kind"] != "blob" or entry["mode"] not in ("100644", "100755"):
                errors.append(f"{label} {path} requires a regular Git blob")
            else:
                roots.append((label, path, entry["blob"]))
    if roots:
        oids = sorted({oid for _, _, oid in roots})
        try:
            types = git(repo, "cat-file", "--batch-check=%(objecttype)",
                        data=("\n".join(oids) + "\n").encode("ascii")).splitlines()
        except (OSError, subprocess.CalledProcessError):
            types = []
        verified = dict(zip(oids, types)) if len(types) == len(oids) else {}
        for label, path, oid in roots:
            if verified.get(oid) != b"blob":
                errors.append(f"{label} {path} blob is unreadable")
    return errors


def compare(repo, w1, c1):
    try:
        object_format = git(repo, "rev-parse", "--show-object-format").strip()
        oid_length = {b"sha1": 40, b"sha256": 64}[object_format]
    except (OSError, subprocess.CalledProcessError, KeyError):
        raise InvalidInput("local Git repository or object format is unreadable") from None

    oid_pattern = re.compile(rf"[0-9a-f]{{{oid_length}}}")
    w1, c1 = w1.lower(), c1.lower()
    old = read_tree(repo, "W1", w1, oid_pattern)
    new = read_tree(repo, "C1", c1, oid_pattern)

    # A committed module can use any tracked path as a dependency. Include
    # every leaf in the conservative closure and compare identities only.
    changes = {
        path: {"w1": old.get(path), "c1": new.get(path)}
        for path in sorted(old.keys() | new.keys())
        if old.get(path) != new.get(path)
    }
    result = {
        "revisions": {"w1": {"commit": w1}, "c1": {"commit": c1}},
        "closure_changes": changes,
        "files_for_review": list(changes),
    }
    errors = required_file_errors(repo, old, new)
    if errors:
        result["error"] = ". ".join(errors)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Compare Git blob IDs and modes for every tracked file as a conservative closure. "
        "List every added, removed or changed path. Exit 2 for any change or invalid input. "
        "Exit 0 for complete inputs with identical tracked files."
    ))
    parser.add_argument("--repo", required=True, type=Path, help="local public-code Git repository")
    parser.add_argument("--w1-commit", required=True, help="full W1 commit ID")
    parser.add_argument("--c1-commit", required=True, help="full C1 commit ID")
    args = parser.parse_args()
    try:
        result = compare(args.repo, args.w1_commit, args.c1_commit)
    except InvalidInput as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(result, indent=2))
    return 2 if result.get("error") or result["closure_changes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
