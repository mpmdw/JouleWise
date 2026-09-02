#!/usr/bin/env python3
"""Validate the D-118/D-121 gate ledger in a pull-request body."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys


KEYS = tuple(range(1, 13))
SHA_RE = re.compile(r"[0-9a-fA-F]{7,40}")
LEDGER_HEADING = "## Gate ledger (D-118 / D-121)"


def _ledger_rows(body: str) -> dict[int, list[str]]:
    """Return evidence cells for numbered rows in the named ledger section."""
    rows: dict[int, list[str]] = {}
    in_ledger = False
    for line in body.splitlines():
        if line.strip() == LEDGER_HEADING:
            in_ledger = True
            continue
        if in_ledger and line.startswith("## "):
            break
        if not in_ledger or "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not cells[0].isdigit():
            continue
        key = int(cells[0])
        if key in KEYS:
            rows.setdefault(key, []).append(cells[2])
    return rows


def _valid_path(path: str, repo_root: Path) -> bool:
    # Copied verbatim from scripts/gen_state.py _check_pointer path checks.
    if path.startswith("/") or path.startswith("~") or ".." in path.split("/") or "://" in path:
        return False
    target = os.path.join(repo_root, *path.split("/"))
    return os.path.isfile(target)


def _is_commit(sha: str, repo_root: Path) -> bool:
    if not SHA_RE.fullmatch(sha):
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check(body: str, head_sha: str, repo_root: Path) -> list[str]:
    """Return one refusal message per ledger defect."""
    defects: list[str] = []
    rows = _ledger_rows(body)
    for key in KEYS:
        evidence_cells = rows.get(key, [])
        if not evidence_cells:
            defects.append(f"gate-ledger: item {key}: missing")
            continue
        if len(evidence_cells) != 1:
            defects.append(f"gate-ledger: item {key}: duplicate key")
            continue

        evidence = evidence_cells[0].strip()
        if not evidence:
            defects.append(f"gate-ledger: item {key}: evidence is empty")
            continue
        if evidence == "NOT-RUN":
            defects.append(f"gate-ledger: item {key}: NOT-RUN")
            continue
        match = re.fullmatch(r"RUN\s+(.+?)\s*", evidence)
        if not match:
            defects.append(f"gate-ledger: item {key}: evidence must be RUN <path-or-sha>")
            continue

        target = match.group(1)
        if SHA_RE.fullmatch(target):
            if not _is_commit(target, repo_root):
                defects.append(f"gate-ledger: item {key}: commit sha does not resolve: {target}")
            elif key == 12 and not head_sha.lower().startswith(target.lower()):
                defects.append(f"gate-ledger: item 12: sha is not the PR head")
        elif key == 12:
            defects.append("gate-ledger: item 12: final-head evidence must be a commit sha")
        elif not _valid_path(target, repo_root):
            defects.append(f"gate-ledger: item {key}: path does not resolve: {target}")
    return defects


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body-file", type=Path, help="PR body file; omit to read stdin")
    parser.add_argument("--head-sha", required=True, help="PR head commit SHA")
    parser.add_argument("--repo-root", type=Path, required=True, help="repository root")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    body = args.body_file.read_text(encoding="utf-8") if args.body_file else sys.stdin.read()
    defects = check(body, args.head_sha, args.repo_root)
    if defects:
        print("\n".join(defects))
        return 1
    print("gate-ledger: 12/12 RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
