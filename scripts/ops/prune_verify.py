#!/usr/bin/env python3
"""Verify a census offline; --release-ready requires protected-ref coverage.

This is NOT proof of fresh fetch, ruleset installation, PR checks, disk copies,
or permission to delete. Those receipts remain operator gates in PRUNE-PLAN.
"""
import argparse
import json
from pathlib import Path
import re

import subprocess

from prune_inventory import git, reachable, rows, scope as expected_scope


def is_ancestor(repo, commit, ref):
    return subprocess.run(["git", "-c", "gc.auto=0", "-C", str(repo), "merge-base", "--is-ancestor",
                           commit, ref], capture_output=True).returncode == 0


def verify(repo, census, tags, archive_commit, release_ready=False):
    base = git(repo, "rev-parse", "refs/remotes/origin/main^{commit}").decode().strip()
    # The archive tag is created once at release-day main and never moves; main
    # keeps moving afterwards. Require ancestry, not equality, after creation.
    if not is_ancestor(repo, archive_commit, base):
        raise ValueError("ARCHIVE_COMMIT must be freshly fetched origin/main or its ancestor")
    current = dict(line.split() for line in git(
        repo, "for-each-ref", "--format=%(refname) %(objectname)",
        "refs/remotes/origin").decode().splitlines())
    scope = rows(census / "CENSUS-SCOPE.tsv")
    for row in scope:
        if current.get(row["ref"]) != row["commit"]:
            raise ValueError("stale census scope: " + row["ref"])
    if scope[0]["commit"] != base:
        raise ValueError("stale census main")
    branches = rows(census / "BRANCH-TRIAGE.tsv")
    if [(r["ref"], r["commit"]) for r in scope] != expected_scope(base, branches):
        raise ValueError("incomplete main/HOLD scope")
    expected = {"refs/remotes/origin/" + r["branch"]: r["snapshot_commit"] for r in branches}
    if current != expected:
        raise ValueError("stale branch census (added, removed, or moved ref)")
    protected = [base]
    archive_rows = 0
    for row in rows(tags):
        name, commit = row["tag"], row["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("unresolved tag target: " + name)
        git(repo, "check-ref-format", "refs/tags/" + name)
        if name.startswith("archive/process-traces-before-release-prune-"):
            archive_rows += 1
            if commit != archive_commit:
                raise ValueError("stale archive TSV target")
        if git(repo, "rev-parse", commit + "^{commit}").decode().strip() != commit:
            raise ValueError("unavailable anchor: " + name)
        if release_ready:
            ref = "refs/tags/" + name
            if git(repo, "cat-file", "-t", ref).decode().strip() != "tag":
                raise ValueError("annotated tag required: " + name)
            if git(repo, "rev-parse", ref + "^{commit}").decode().strip() != commit:
                raise ValueError("tag conflict: " + name)
        protected.append(commit)
    if archive_rows != 1:
        raise ValueError("exactly one release-day archive row required")
    covered = reachable(repo, protected)
    pull_refs = git(repo, "for-each-ref", "--format=%(objectname)",
                    "refs/remotes/pull", "refs/pull").decode().splitlines()
    all_refs = covered | reachable(repo, [r["snapshot_commit"] for r in branches] + pull_refs)
    missing, held = [], []
    pins = rows(census / "PIN-COMMITS.tsv")
    metadata = json.loads((census / "CENSUS.json").read_text())
    if (metadata["main"] != base or metadata["scope_tips"] != len(scope)
            or metadata["commits"] != len(pins)
            or len({r["commit"] for r in pins}) != len(pins)):
        raise ValueError("incomplete or mismatched census outputs")
    for row in pins:
        if row["commit"] not in covered:
            (held if row["commit"] in all_refs else missing).append(row["commit"])
    if missing or (release_ready and held):
        raise ValueError(f"unretained={len(missing)}, HOLD-only={len(held)}; do not delete affected refs")
    print(f"PASS snapshot topology: {len(covered)} anchor/main ancestors; {len(held)} HOLD-only pins")
    print("Release remains gated on server/PR/receipt/copy evidence and unresolved-text dispositions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--tags", type=Path, default=Path("docs/ops/TAGS-TO-CREATE.tsv"))
    parser.add_argument("--archive-commit", required=True)
    parser.add_argument("--release-ready", action="store_true")
    args = parser.parse_args()
    verify(args.repo, args.census, args.tags, args.archive_commit, args.release_ready)


if __name__ == "__main__":
    main()
