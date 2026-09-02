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


def _split_table_row(line: str) -> list[str]:
    """Split a GFM table row exactly as the Tables extension does: on every
    pipe, before inline parsing; the only exception is a backslash-escaped
    pipe, literal "including inside other inline spans". No inline syntax is
    modelled, on purpose.
    """
    cells: list[str] = []
    cell: list[str] = []
    backslashes = 0
    for char in line:
        if char == "|":
            if backslashes % 2 == 1:
                cell.pop()  # The pre-pass consumes the escaping backslash.
                cell.append("|")
            else:
                cells.append("".join(cell).strip())
                cell = []
            backslashes = 0
            continue
        cell.append(char)
        backslashes = backslashes + 1 if char == "\\" else 0
    cells.append("".join(cell).strip())
    if cells and not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return cells


class _LedgerRows(dict[int, list[str]]):
    """Ledger evidence rows plus section-level refusal context."""

    def __init__(self) -> None:
        super().__init__()
        self.defects: list[str] = []
        self.heading_seen = False


def _ledger_rows(body: str) -> tuple[_LedgerRows, set[int]]:
    """Return evidence rows and malformed keys from the first ledger table."""
    rows = _LedgerRows()
    malformed: set[int] = set()
    table_started = False
    table_ended = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == LEDGER_HEADING:
            # Fences are NOT modelled; a ledger quoted inside a fence BEFORE the real
            # section will be read as the section (fail-closed: twelve NOT-RUN lines).
            if not rows.heading_seen:
                rows.heading_seen = True
            continue
        if not rows.heading_seen:
            continue
        if stripped.startswith("## "):
            break
        is_pipe_line = "|" in stripped
        if not table_started:
            if not is_pipe_line:
                continue
            table_started = True
        elif table_ended:
            if is_pipe_line:
                cells = _split_table_row(stripped)
                if cells and cells[0].isdigit() and int(cells[0]) in KEYS:
                    rows.defects.append(
                        f"gate-ledger: item {int(cells[0])}: ledger row outside the ledger table"
                    )
            continue
        elif not is_pipe_line:
            table_ended = True
            continue
        cells = _split_table_row(stripped)
        if not cells:
            rows.defects.append("gate-ledger: unrecognised ledger row: ''")
            continue
        first = cells[0]
        if first == "#" or re.fullmatch(r":?-{3,}:?", first):
            continue
        if not first.isdigit() or int(first) not in KEYS:
            rows.defects.append(f"gate-ledger: unrecognised ledger row: {first!r}")
            continue
        key = int(first)
        if len(cells) != 3:
            malformed.add(key)
            rows.defects.append(
                f"gate-ledger: item {key}: row has {len(cells)} cells, expected 3 "
                "(an unescaped | splits a cell even inside backticks; write \\|)"
            )
            continue
        rows.setdefault(key, []).append(cells[2])
    return rows, malformed


def _valid_path(path: str, repo_root: Path) -> bool:
    # Copied verbatim from scripts/gen_state.py _check_pointer path checks.
    if not isinstance(path, str) or not path:
        return False
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
    rows, malformed = _ledger_rows(body)
    if not rows and not malformed and not rows.heading_seen:
        return [f"gate-ledger: no {LEDGER_HEADING!r} section in the PR body"]
    defects = list(rows.defects)
    for key in KEYS:
        if key in malformed:
            continue
        evidence_cells = rows.get(key, [])
        if not evidence_cells:
            defects.append(f"gate-ledger: item {key}: missing")
            continue
        if len(evidence_cells) != 1:
            defects.append(f"gate-ledger: item {key}: duplicate key")
            continue

        evidence = evidence_cells[0].strip()
        if "`" in evidence:
            defects.append(f"gate-ledger: item {key}: evidence cell must be plain text (no backticks)")
            continue
        if not evidence:
            defects.append(f"gate-ledger: item {key}: evidence is empty")
            continue
        if evidence == "NOT-RUN":
            defects.append(f"gate-ledger: item {key}: NOT-RUN")
            continue
        match = re.fullmatch(r"RUN\s+(.+?)\s*", evidence)
        if not match:
            if re.match(r"(?i:run)\s+", evidence):
                defects.append(f"gate-ledger: item {key}: evidence must start with RUN (uppercase)")
            else:
                defects.append(f"gate-ledger: item {key}: evidence must be RUN <path-or-sha>")
            continue

        target = match.group(1)
        if key == 12 and SHA_RE.fullmatch(target):
            if not _is_commit(target, repo_root):
                defects.append(f"gate-ledger: item {key}: commit sha does not resolve: {target}")
            elif not head_sha.lower().startswith(target.lower()):
                defects.append(f"gate-ledger: item 12: sha is not the PR head")
        elif key == 12:
            defects.append("gate-ledger: item 12: final-head evidence must be a commit sha")
        elif not (_is_commit(target, repo_root) or _valid_path(target, repo_root)):
            defects.append(f"gate-ledger: item {key}: neither a commit nor a path: {target}")
    return defects


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body-file", "--body", dest="body_file", type=Path,
                        help="PR body file; omit to read stdin")
    parser.add_argument("--head-sha", default="", help="PR head commit SHA")
    parser.add_argument("--repo-root", "--root", dest="repo_root", type=Path,
                        required=True, help="repository root")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if not args.repo_root.is_dir():
            raise OSError(f"repository root does not exist: {args.repo_root}")
        body = args.body_file.read_text(encoding="utf-8") if args.body_file else sys.stdin.read()
        defects = check(body, args.head_sha, args.repo_root)
    except (OSError, UnicodeError) as exc:
        print(f"gate-ledger: input error: {exc}")
        return 1
    if defects:
        print("\n".join(defects))
        return 1
    print("gate-ledger: 12/12 RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
