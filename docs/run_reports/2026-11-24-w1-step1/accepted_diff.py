#!/usr/bin/env python3
"""Reconstruct BASE..REV for the RL-193 W1 accepted-diff proof.

Start at presign, apply each component's own merge-base delta, then the
explicit step-1 and PR #973 deltas. Print path names and tree-entry metadata.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


REGULAR_MODES = {b"100644", b"100755"}


class ProofError(Exception):
    pass


class MergeConflict(Exception):
    pass


@dataclass(frozen=True)
class Entry:
    mode: bytes
    kind: bytes
    oid: bytes

    def metadata(self):
        return {"mode": self.mode.decode(), "kind": self.kind.decode(), "oid": self.oid.decode()}


@dataclass(frozen=True)
class Delta:
    owner: str
    before: bytes
    after: bytes
    entries: dict[bytes, tuple[Entry | None, Entry | None]]


class Git:
    def __init__(self, repo):
        self.repo = repo
        self.env = {**os.environ, "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1"}
        if any(name in self.env for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")):
            raise ProofError("GIT_ENV_OVERRIDE")
        self.trees = {}
        self.blobs = {}

    def run(self, *args, data=None, check=True):
        result = subprocess.run(["git", *args], cwd=self.repo, env=self.env, input=data, capture_output=True)
        if check and result.returncode:
            raise ProofError(f"GIT_COMMAND_FAILED: {args[0]}")
        return result

    def commit(self, name):
        return self.run("rev-parse", "--verify", "--end-of-options", f"{name}^{{commit}}").stdout.strip()

    def tree(self, rev):
        if rev not in self.trees:
            entries = {}
            for record in self.run("ls-tree", "-rz", "--full-tree", rev).stdout.split(b"\0"):
                if record:
                    meta, path = record.split(b"\t", 1)
                    entries[path] = Entry(*meta.split())
            self.trees[rev] = entries
        return self.trees[rev]

    def changed(self, before, after):
        return self.run("diff", "--name-only", "-z", "--no-renames", "--ignore-submodules=none",
                        before, after, "--").stdout.split(b"\0")[:-1]

    def delta(self, owner, before, after):
        old, new = self.tree(before), self.tree(after)
        return Delta(owner, before, after, {path: (old.get(path), new.get(path))
                                            for path in self.changed(before, after)})

    def blob(self, oid):
        if oid not in self.blobs:
            self.blobs[oid] = self.run("cat-file", "blob", oid).stdout
        return self.blobs[oid]


def component_deltas(git, heads_path, base, rev):
    heads = json.loads(heads_path.read_bytes())
    if not isinstance(heads, dict) or not heads:
        raise ProofError("INVALID_COMPONENT_HEADS")
    deltas = []
    for pr, head in heads.items():
        if (not re.fullmatch(r"[0-9]+", pr) or pr in {"809", "959"} or not isinstance(head, str)
                or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head)):
            raise ProofError("INVALID_COMPONENT_HEADS")
        oid = git.commit(head)
        if oid != head.encode() or git.run("merge-base", "--is-ancestor", oid, rev, check=False).returncode:
            raise ProofError(f"COMPONENT_NOT_IN_REV: PR #{pr}")
        merge_base = git.run("merge-base", oid, base).stdout.strip()
        deltas.append(git.delta(f"PR #{pr}", merge_base, oid))
    superseding = next((delta for delta in deltas if delta.owner == "PR #839"), None)
    if superseding:
        for delta in deltas:
            if delta.owner == "PR #826":
                for path in superseding.entries:
                    delta.entries.pop(path, None)
    return deltas


def range_deltas(git, owner, ranges, rev):
    for value in ranges:
        start, sep, end = value.partition("..")
        if not sep or not start or not end or end.startswith(".") or ".." in end:
            raise ProofError(f"INVALID_RANGE: {owner}")
        before, after = git.commit(start), git.commit(end)
        if (git.run("merge-base", "--is-ancestor", before, after, check=False).returncode
                or git.run("merge-base", "--is-ancestor", after, rev, check=False).returncode):
            raise ProofError(f"RANGE_NOT_IN_REV: {owner}")
        yield git.delta(owner, before, after)


def merge_value(current, ancestor, incoming):
    if current == ancestor or current == incoming:
        return incoming
    if incoming == ancestor:
        return current
    raise MergeConflict


def merge_entry(git, current, ancestor, incoming):
    if current == ancestor or current == incoming:
        return incoming
    if incoming == ancestor:
        return current
    if None in (current, ancestor, incoming):
        raise MergeConflict

    mode = merge_value(current.mode, ancestor.mode, incoming.mode)
    kind = merge_value(current.kind, ancestor.kind, incoming.kind)
    if len({current.kind, ancestor.kind, incoming.kind}) != 1:
        raise MergeConflict
    try:
        oid = merge_value(current.oid, ancestor.oid, incoming.oid)
    except MergeConflict:
        if any(entry.mode not in REGULAR_MODES for entry in (current, ancestor, incoming)):
            raise
        with tempfile.TemporaryDirectory(prefix="w1-accepted-diff-") as temp:
            files = [Path(temp) / name for name in ("presign", "ancestor", "incoming")]
            for file, entry in zip(files, (current, ancestor, incoming), strict=True):
                file.write_bytes(git.blob(entry.oid))
            merged = git.run("merge-file", "--stdout", *files, check=False)
        if merged.returncode:
            raise MergeConflict
        oid = git.run("hash-object", "--stdin", data=merged.stdout).stdout.strip()
        git.blobs[oid] = merged.stdout
    return Entry(mode, kind, oid)


def same_entry(git, expected, actual):
    if expected is None or actual is None:
        return expected is actual
    if (expected.mode, expected.kind) != (actual.mode, actual.kind):
        return False
    if expected.kind == b"blob":
        return git.blob(expected.oid) == git.blob(actual.oid)
    return expected.oid == actual.oid


def load_kit():
    # Use the generator shipped with the proof, without importing from --kit-root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from scripts import align_v4_kit
    return align_v4_kit


def generated_files(root, rev):
    checkout = Git(root)
    if (checkout.commit("HEAD") != rev
            or checkout.run("status", "--porcelain=v1", "-z", "--untracked-files=all",
                            "--ignored=matching").stdout):
        raise ProofError("KIT_ROOT_MUST_BE_CLEAN_AT_REV")
    kit = load_kit()
    # These inputs pass through build_files verbatim. Their provenance still
    # comes from the accepted deltas or an explicit residual.
    passthrough = {Path(path) for path in (kit.INPUTS, kit.R1_SLOTS, kit.R1_PLANNING_RELEASE, kit.W1_PLAN)}
    return {os.fsencode(path): raw for path, raw in kit.build_files(root).items() if Path(path) not in passthrough}


def classify(git, base, rev, presign, deltas, generated, accepted):
    base_tree, actual_tree, presign_tree = (git.tree(ref) for ref in (base, rev, presign))
    for path in git.changed(base, rev):
        expected = presign_tree.get(path)
        actual = actual_tree.get(path)
        owned = [delta for delta in deltas if path in delta.entries]
        owners = (["presign"] if expected != base_tree.get(path) else []) + [delta.owner for delta in owned]
        conflict = None
        for delta in owned:
            try:
                expected = merge_entry(git, expected, *delta.entries[path])
            except MergeConflict:
                conflict = delta.owner
                break

        result = "residual"
        if conflict is None:
            mode = expected.mode if expected is not None else b"100644"
            if (path in generated and actual is not None and actual.mode in REGULAR_MODES
                    and actual.mode == mode and git.blob(actual.oid) == generated[path]):
                result = "step1-generated"
            elif same_entry(git, expected, actual):
                result = "reconstructed-equal"
        yield {"path": os.fsdecode(path), "result": result, "owners": owners, "conflict": conflict,
               "expected": expected.metadata() if conflict is None and expected else None,
               "actual": actual.metadata() if actual else None,
               "accepted_residual": result == "residual" and path in accepted}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rev", help="candidate commit under review")
    parser.add_argument("base", help="comparison base and merge-base reference for component deltas")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--presign", help="presign commit, including the Part C port (defaults to BASE)")
    parser.add_argument("--component-heads", type=Path, required=True,
                        help="JSON map from PR numbers to full commit IDs, in application order")
    parser.add_argument("--step1", action="append", default=[], metavar="OLD..NEW")
    parser.add_argument("--pr973", action="append", default=[], metavar="OLD..NEW")
    parser.add_argument("--kit-root", type=Path, help="clean candidate checkout at REV for in-memory kit derivation")
    parser.add_argument("--accept-residual", action="append", default=[], metavar="PATH")
    args = parser.parse_args(argv)
    try:
        git = Git(args.repo)
        rev, base, presign = (git.commit(name) for name in (args.rev, args.base, args.presign or args.base))
        deltas = component_deltas(git, args.component_heads, base, rev)
        deltas.extend(range_deltas(git, "step 1", args.step1, rev))
        deltas.extend(range_deltas(git, "PR #973", args.pr973, rev))
        generated = generated_files(args.kit_root.resolve(), rev) if args.kit_root else {}
        rows = list(classify(git, base, rev, presign, deltas, generated,
                             {os.fsencode(path) for path in args.accept_residual}))
    except ProofError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        # Kit validation errors can carry registration values.
        print(f"PROOF_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(json.dumps({"rev": rev.decode(), "base": base.decode(), "presign": presign.decode(),
                      "deltas": [{"owner": delta.owner, "before": delta.before.decode(),
                                  "after": delta.after.decode()} for delta in deltas],
                      "paths": rows}, indent=2))
    return int(any(row["result"] == "residual" and not row["accepted_residual"] for row in rows))


if __name__ == "__main__":
    sys.exit(main())
