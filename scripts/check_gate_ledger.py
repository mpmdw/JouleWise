#!/usr/bin/env python3
"""Validate the gate ledger and Impact statement in a pull-request body.

The ledger is D-118 as thinned on 2026-09-29 (owner-authorized; D-186;
summary in docs/process_prune_2026-09-29.md): five table rows plus the
six-line Impact statement. Each key protects something real:

1. independent review by a non-author, with a lens that executes the code;
2. the whole suite on the merged tree;
3. CI green on the final head (evidence: that head's sha);
4. a cold final pass on merge code that touches measurement, calibration
   or claims;
5. findings dispositioned (fixed, deferred to a named lane, or rejected
   with a reason);
6. the Impact statement, lines (i)-(vi), each starting with Yes or No.

Light tier (docs, records or tests only, every Impact line No) needs rows
2 and 3 plus the Impact statement; row 2 may read N/A (docs only) when no
test or code file changed. The checker targets mistakes (a forgotten row,
a light tier that changes a number), not deliberate forgery (D-161).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys


KEYS = (1, 2, 3, 4, 5)
LEDGER_HEADING = "## Gate ledger"
LIGHT_NA_TEXT = "N/A (light tier)"
DOCS_NA_TEXT = "N/A (docs only)"
NO_CLAIM_NA_TEXT = "N/A (no measurement, calibration or claim code)"
IMPACT_LABELS = ("i", "ii", "iii", "iv", "v", "vi")
FINAL_HEAD_KEY = 3
CLAIM_PASS_KEY = 4
SHA_RE = re.compile(r"[0-9a-fA-F]{7,40}")
IMPACT_RE = re.compile(r"\((i|ii|iii|iv|v|vi)\) [^:]*:(.*)")
ANSWER_RE = re.compile(r"(?i)(yes|no|none)\b")

# The one N/A text each row accepts, by tier. A row absent from a tier's
# map needs RUN evidence in that tier.
ALLOWED_NA = {
    "full": {CLAIM_PASS_KEY: NO_CLAIM_NA_TEXT},
    "light": {1: LIGHT_NA_TEXT, 2: DOCS_NA_TEXT, 4: LIGHT_NA_TEXT, 5: LIGHT_NA_TEXT},
}
# A light-tier PR runs no audit rounds, so these rows must read N/A there.
LIGHT_MUST_BE_NA = frozenset((1, 4, 5))


def _split_table_row(line: str) -> list[str]:
    """Split a GFM table row on every unescaped pipe, as GitHub does.

    GitHub splits cells before it parses inline syntax, so a pipe inside
    backticks still splits the cell unless it is written as \\|.
    """
    cells: list[str] = []
    cell: list[str] = []
    backslashes = 0
    for char in line:
        if char == "|":
            if backslashes % 2 == 1:
                cell.pop()  # The escaping backslash is consumed.
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


def _ledger_rows(body: str) -> tuple[dict[int, list[str]], set[int], list[str], bool]:
    """Return (evidence cells by row, malformed rows, defects, heading seen)."""
    rows: dict[int, list[str]] = {}
    malformed: set[int] = set()
    defects: list[str] = []
    heading_seen = False
    table_started = False
    table_ended = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == LEDGER_HEADING:
            # Code fences are not modelled: a ledger quoted in a fence before
            # the real one is read as the ledger, and its NOT-RUN rows fail.
            heading_seen = True
            continue
        if not heading_seen:
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
                    defects.append(
                        f"gate-ledger: row {int(cells[0])}: this row sits outside the ledger table"
                    )
            continue
        elif not is_pipe_line:
            table_ended = True
            continue
        cells = _split_table_row(stripped)
        if not cells:
            defects.append("gate-ledger: the ledger table has an empty row")
            continue
        first = cells[0]
        if first == "#" or re.fullmatch(r":?-{3,}:?", first):
            continue
        if not first.isdigit() or int(first) not in KEYS:
            defects.append(f"gate-ledger: the ledger table has a row with an unknown key: {first!r}")
            continue
        key = int(first)
        if len(cells) != 3:
            malformed.add(key)
            defects.append(
                f"gate-ledger: row {key}: has {len(cells)} cells, expected 3 "
                "(an unescaped | splits a cell even inside backticks; write \\|)"
            )
            continue
        rows.setdefault(key, []).append(cells[2])
    return rows, malformed, defects, heading_seen


def _impact(body: str) -> tuple[list[str], list[str]]:
    """Return (labels answered Yes, defects) for the six Impact lines."""
    answers: dict[str, list[str]] = {}
    for line in body.splitlines():
        match = IMPACT_RE.fullmatch(line.rstrip())
        if match:
            answers.setdefault(match.group(1), []).append(match.group(2).strip())
    yes_labels: list[str] = []
    defects: list[str] = []
    for label in IMPACT_LABELS:
        found = answers.get(label, [])
        if not found:
            defects.append(f"gate-ledger: Impact statement line ({label}) is missing")
        elif len(found) > 1:
            defects.append(f"gate-ledger: Impact statement line ({label}) appears more than once")
        elif not found[0] or found[0] == "TODO":
            defects.append(f"gate-ledger: Impact statement line ({label}) is not answered")
        else:
            word = ANSWER_RE.match(found[0])
            if not word:
                defects.append(
                    f"gate-ledger: Impact statement line ({label}) must start with Yes or No"
                )
            elif word.group(1).lower() == "yes":
                yes_labels.append(label)
    return yes_labels, defects


def _valid_path(path: str, repo_root: Path) -> bool:
    # Same rules as scripts/gen_state.py _check_pointer.
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


def _declared_tier(body: str) -> tuple[str, str | None]:
    """Return (tier, defect). Only an unindented `Tier:` line declares; none means full."""
    tier_lines = [line.strip() for line in body.splitlines() if line.startswith("Tier:")]
    if len(tier_lines) > 1:
        return "full", "gate-ledger: the body declares Tier more than once"
    if tier_lines and tier_lines[0] not in ("Tier: full", "Tier: light"):
        return "full", "gate-ledger: Tier must be full or light"
    return (tier_lines[0].removeprefix("Tier: ") if tier_lines else "full"), None


def _check_row(key: int, evidence: str, tier: str, head_sha: str, repo_root: Path) -> str | None:
    """Return one plain defect message for a row, or None."""
    if "`" in evidence:
        return f"gate-ledger: row {key}: write the evidence as plain text, without backticks"
    if not evidence:
        return f"gate-ledger: row {key}: evidence is empty"
    allowed_na = ALLOWED_NA[tier].get(key)
    if tier == "light" and key in LIGHT_MUST_BE_NA:
        if evidence != LIGHT_NA_TEXT:
            return f"gate-ledger: row {key}: a light-tier PR writes {LIGHT_NA_TEXT} here"
        return None
    if evidence.startswith("N/A"):
        if evidence == allowed_na:
            return None
        if allowed_na:
            return f"gate-ledger: row {key}: the only N/A this row accepts in {tier} tier is {allowed_na}"
        return f"gate-ledger: row {key}: {tier} tier needs RUN evidence here, not N/A"
    if evidence == "NOT-RUN":
        return f"gate-ledger: row {key}: still NOT-RUN"
    match = re.fullmatch(r"RUN\s+(.+?)\s*", evidence)
    if not match:
        if re.match(r"(?i:run)\s+", evidence):
            return f"gate-ledger: row {key}: write RUN in capitals"
        return f"gate-ledger: row {key}: evidence must be RUN <path-or-sha>"
    target = match.group(1)
    if ":" in target or "#" in target:
        # Refused as syntax before the existence check, so a committed file
        # literally named `evidence.txt:12` cannot pass (Sol 233 SF1).
        return f"gate-ledger: row {key}: a :N line suffix or #anchor is not a path: {target}"
    if key == FINAL_HEAD_KEY:
        if not SHA_RE.fullmatch(target):
            return f"gate-ledger: row {key}: name the final head as a commit sha"
        if not _is_commit(target, repo_root):
            return f"gate-ledger: row {key}: commit sha does not resolve: {target}"
        if not head_sha.lower().startswith(target.lower()):
            return f"gate-ledger: row {key}: sha is not the PR head (a push moved the head; update this row)"
        return None
    if not (_is_commit(target, repo_root) or _valid_path(target, repo_root)):
        return f"gate-ledger: row {key}: neither a commit nor a file in the repo: {target}"
    return None


def check(body: str, head_sha: str, repo_root: Path) -> list[str]:
    """Return one plain message per defect; an empty list means the ledger passes."""
    tier, tier_defect = _declared_tier(body)
    if tier_defect:
        return [tier_defect]
    rows, malformed, defects, heading_seen = _ledger_rows(body)
    if not heading_seen:
        return [f"gate-ledger: no {LEDGER_HEADING!r} section in the PR body"]
    yes_labels, impact_defects = _impact(body)
    defects.extend(impact_defects)
    if tier == "light" and yes_labels:
        defects.append(
            f"gate-ledger: Tier is light but Impact line ({yes_labels[0]}) says Yes; "
            "a PR that can change a number is full tier"
        )
    for key in KEYS:
        if key in malformed:
            continue  # Already reported.
        cells = rows.get(key, [])
        if not cells:
            defects.append(f"gate-ledger: row {key}: missing")
            continue
        if len(cells) != 1:
            defects.append(f"gate-ledger: row {key}: appears more than once")
            continue
        evidence = cells[0].strip()
        defect = _check_row(key, evidence, tier, head_sha, repo_root)
        if defect:
            defects.append(defect)
        elif tier == "full" and key == CLAIM_PASS_KEY and evidence == NO_CLAIM_NA_TEXT and yes_labels:
            defects.append(
                f"gate-ledger: row {key}: Impact line ({yes_labels[0]}) says Yes, "
                "so this PR needs the cold final pass"
            )
    return defects


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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
    tier, _ = _declared_tier(body)
    print(f"gate-ledger: {tier} tier passes (5 rows, Impact statement answered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
