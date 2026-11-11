#!/usr/bin/env python3
"""Gate one branch-deletion batch against a FRESH census. Never deletes anything.

Run after `git fetch --prune origin` and `prune_refresh.py` (which re-runs the
branch-name consumer scan). A branch passes only if ALL hold:
  - the fresh census lists it as MERGED-CANDIDATE at an unchanged tip;
  - refs/remotes/origin/<branch> still equals that tip;
  - the tip is an ancestor of origin/main and of the archive tag;
  - the fresh BRANCH-NAME-CONSUMERS.tsv has no row naming it;
  - no open PR uses it as head or base (--open-prs, from `gh pr list`);
  - it is not in the KEEP set (main, archive/*, records/*, the live lanes file).
Passing rows go to --approved (branch, commit); others go to stderr with reasons.
Exit 1 if any row is refused, so a partial batch cannot be mistaken for a clean one.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

from prune_inventory import git, rows, write_tsv

KEEP = re.compile(r"^(main|HEAD|archive/.*|records/.*)$")


def is_ancestor(repo, commit, ref):
    return subprocess.run(["git", "-c", "gc.auto=0", "-C", str(repo), "merge-base", "--is-ancestor",
                           commit, ref], capture_output=True).returncode == 0


def gate(repo, census, batch, open_prs, archive_tag, keep_extra=()):
    triage = {r["branch"]: r for r in rows(census / "BRANCH-TRIAGE.tsv")}
    consumed = {r["candidate"] for r in rows(census / "BRANCH-NAME-CONSUMERS.tsv")}
    pr_refs = set()
    for line in open_prs:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            pr_refs.update(parts[1:3])
    keep = set(keep_extra)
    archive = git(repo, "rev-parse", f"refs/tags/{archive_tag}^{{commit}}").decode().strip()
    approved, refused = [], []
    for branch in batch:
        reasons = []
        row = triage.get(branch)
        if row is None or row["disposition"] != "MERGED-CANDIDATE":
            reasons.append("not-merged-candidate-in-fresh-census")
        if KEEP.match(branch) or branch in keep:
            reasons.append("keep-set")
        if branch in consumed:
            reasons.append("name-consumer-hit")
        if branch in pr_refs:
            reasons.append("open-pr-head-or-base")
        if row is not None:
            tip = row["snapshot_commit"]
            current = subprocess.run(["git", "-C", str(repo), "rev-parse", "-q", "--verify",
                                      f"refs/remotes/origin/{branch}"], capture_output=True, text=True).stdout.strip()
            if current != tip:
                reasons.append("tip-moved-or-gone")
            if not is_ancestor(repo, tip, "refs/remotes/origin/main"):
                reasons.append("not-ancestor-of-main")
            if not is_ancestor(repo, tip, archive):
                reasons.append("not-ancestor-of-archive-tag")
        if reasons:
            refused.append((branch, reasons))
        else:
            approved.append(dict(branch=branch, commit=row["snapshot_commit"]))
    return approved, refused


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--census", type=Path, required=True, help="fresh prune_refresh.py output")
    parser.add_argument("--batch", type=Path, required=True, help="one branch name per line")
    parser.add_argument("--open-prs", type=Path, required=True, help="TSV: number, head, base")
    parser.add_argument("--archive-tag", required=True)
    parser.add_argument("--keep", type=Path, help="extra KEEP branch names, one per line")
    parser.add_argument("--approved", type=Path, required=True)
    args = parser.parse_args()
    batch = [b.strip() for b in args.batch.read_text().splitlines() if b.strip()]
    keep = [b.strip() for b in args.keep.read_text().splitlines() if b.strip()] if args.keep else []
    approved, refused = gate(args.repo, args.census, batch, args.open_prs.read_text().splitlines(),
                             args.archive_tag, keep)
    write_tsv(args.approved, ["branch", "commit"], approved)
    for branch, reasons in refused:
        print(f"REFUSED\t{branch}\t{','.join(reasons)}", file=sys.stderr)
    print(f"approved={len(approved)} refused={len(refused)}")
    raise SystemExit(1 if refused else 0)


if __name__ == "__main__":
    main()
