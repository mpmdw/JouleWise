#!/usr/bin/env python3
"""One offline refresh command. Review the output diff; never executes a prune."""
import argparse
from pathlib import Path
import re

from prune_inventory import git, inventory, rows, write_tsv
from prune_branch_names import scan
from prune_verify import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive-commit", required=True)
    parser.add_argument("--archive-date", required=True)
    parser.add_argument("--inputs", type=Path, default=Path("docs/ops"))
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.archive_date):
        parser.error("archive date must be YYYY-MM-DD")
    base = git(args.repo, "rev-parse", "refs/remotes/origin/main^{commit}").decode().strip()
    if args.archive_commit != base:
        parser.error("ARCHIVE_COMMIT must equal origin/main (fetch first in the later connected session)")
    inventory(args.repo, args.output, rows(args.inputs / "BRANCH-TRIAGE.tsv"))
    tags = rows(args.inputs / "TAGS-TO-CREATE.tsv")
    archive = [r for r in tags if r["tag"].startswith("archive/process-traces-before-release-prune-")]
    if len(archive) != 1:
        parser.error("exactly one archive input row required")
    archive[0].update(tag="archive/process-traces-before-release-prune-" + args.archive_date,
                      commit=base)
    write_tsv(args.output / "TAGS-TO-CREATE.tsv", ["tag", "commit"], tags)
    matches = scan(args.repo, args.output, args.output / "BRANCH-NAME-CONSUMERS.tsv")
    verify(args.repo, args.output, args.output / "TAGS-TO-CREATE.tsv", base)
    print("Branch-name hits require dispositions:", matches)


if __name__ == "__main__":
    main()
