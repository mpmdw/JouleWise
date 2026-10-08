#!/usr/bin/env python3
"""Recompute every digest the block-5 seal record pins, and compare.

Run from anywhere inside a checkout of the repository that holds the seal record:

    python3 docs/process_traces/2026-10-07-block5-seal/bench/check_seal_record.py

What it reads out of SEAL_RECORD.md, and how it recomputes each value:

- section 4.1, the three seal documents at the seal commit, and section 4.2, the other pinned files at
  H_claim: `git show <commit>:<path>` hashed with SHA-256. The two commits are read from the headings of the
  two sections. Each file of section 4.2 is also required to have the same bytes at the seal commit.
- section 5, the copies of the gate's records in the seal record's directory, and the table of helpers in
  the section "Plans written after the seal": the file beside the record, hashed with SHA-256.
- section 2's statements about the seal commit: one parent, which is H_claim; a three-file difference; the
  sealed inventory's `status`, `head` and number of entries.

- each harvest addendum: the three harvest program files at the pinned commit, `git show <commit>:<path>` hashed
  with SHA-256, and the list of paths that differ between H_claim and that commit. A clone that does not hold
  the pinned commit prints that it cannot make this check, and does not fail.

It does not recompute the six plan digests of the section "Plans written after the seal": those are digests
of scratch files outside the repository, and the section says so.

Standard library only. It writes nothing. Exit status 0 when every value agrees, 1 otherwise.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1] / "SEAL_RECORD.md"
HEX64 = r"[0-9a-f]{64}"
HEX40 = r"[0-9a-f]{40}"


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def section(text: str, heading_start: str) -> tuple[str, str]:
    """Return (the heading line, the body up to the next heading of the same or a higher level)."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading_start))
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"#{1,%d} " % level, lines[i]):
            end = i
            break
    return lines[start], "\n".join(lines[start + 1:end])


def main() -> int:
    text = RECORD.read_text(encoding="utf-8")
    root = Path(git(RECORD.parent, "rev-parse", "--show-toplevel").decode().strip())
    problems: list[str] = []
    checked = 0

    def compare(label: str, expected: str, got: str) -> None:
        nonlocal checked
        checked += 1
        if expected == got:
            print("equal    ", label)
        else:
            problems.append(f"{label}: the record says {expected}, recomputed {got}")
            print("DIFFERENT", label)

    head_41, body_41 = section(text, "### 4.1 ")
    head_42, body_42 = section(text, "### 4.2 ")
    seal = re.search(HEX40, head_41).group(0)
    h_claim = re.search(HEX40, head_42).group(0)

    rows_41 = re.findall(r"^\| `([^`]+)` \| `(%s)` \|$" % HEX64, body_41, re.M)
    rows_42 = re.findall(r"^\| [^|]+ \| `([^`]+)` \| `(%s)` \|$" % HEX64, body_42, re.M)
    if len(rows_41) != 3:
        problems.append(f"section 4.1 has {len(rows_41)} rows, expected 3")
    if len(rows_42) != 19:
        problems.append(f"section 4.2 has {len(rows_42)} rows, expected 19")
    for path, digest in rows_41:
        compare(f"{path} at the seal commit", digest, hashlib.sha256(git(root, "show", f"{seal}:{path}")).hexdigest())
    for path, digest in rows_42:
        at_h = git(root, "show", f"{h_claim}:{path}")
        compare(f"{path} at H_claim", digest, hashlib.sha256(at_h).hexdigest())
        if git(root, "show", f"{seal}:{path}") != at_h:
            problems.append(f"{path}: the bytes at the seal commit differ from the bytes at H_claim")

    # Section 2: the shape of the seal commit and of the inventory.
    parents = git(root, "rev-list", "--parents", "-n", "1", seal).decode().split()
    compare("the seal commit's parents", h_claim, " ".join(parents[1:]))
    changed = sorted(git(root, "diff", "--name-only", "--no-renames", h_claim, seal).decode().split())
    compare("the paths the seal commit changes", " ".join(sorted(path for path, _ in rows_41)), " ".join(changed))
    inventory_path = next(path for path, _ in rows_41 if path.endswith("sealed_inventory.json"))
    inventory = json.loads(git(root, "show", f"{seal}:{inventory_path}"))
    stated = re.search(r"has `status` `(\w+)`, `head` `(%s)`, and\s+(\d+) entries" % HEX40, text)
    if stated is None:
        problems.append("section 2 does not state the inventory's status, head and number of entries")
    else:
        compare("the inventory's status, head and number of entries",
                " ".join(stated.groups()), f"{inventory['status']} {inventory['head']} {len(inventory['files'])}")
    compare("the inventory's head is H_claim", h_claim, str(inventory["head"]))

    # Section 5 and the helpers: files beside the record.
    _, body_5 = section(text, "## 5. ")
    for rel, digest in re.findall(r"^\| [^|]+ \| `([^`]+)` \| `(%s)` \|$" % HEX64, body_5, re.M):
        compare(f"the copy {rel}", digest, hashlib.sha256((RECORD.parent / rel).read_bytes()).hexdigest())
    _, body_plans = section(text, "## Plans written after the seal")
    helper_rows = re.findall(r"^\| `([A-Za-z0-9_.]+)`[^|]* \| `(%s)` \|$" % HEX64, body_plans, re.M)
    if len(helper_rows) != 5:
        problems.append(f"the helpers table has {len(helper_rows)} rows, expected 5")
    for name, digest in helper_rows:
        compare(f"the helper bench/{name}", digest, hashlib.sha256((RECORD.parent / "bench" / name).read_bytes()).hexdigest())

    # The harvest addenda: each pins one commit and the SHA-256 of the three harvest program files at it.
    for heading in re.findall(r"^## (Addendum \d+: the harvest program[^\n]*)$", text, re.M):
        _, body = section(text, "## " + heading)
        pins = re.findall(r"^B5-HARVEST-PIN: (.*)$", body, re.M)
        if len(pins) != 1:
            problems.append(f"{heading[:11]}: expected one line that starts with 'B5-HARVEST-PIN: ', found {len(pins)}")
            continue
        pin = pins[0]
        if not re.fullmatch(HEX40, pin):
            print(f"{heading[:11]}: the pin is not filled yet ({pin})")
            continue
        try:
            git(root, "cat-file", "-e", pin + "^{commit}")
        except subprocess.CalledProcessError:
            print(f"{heading[:11]}: commit {pin} is not in this clone, so its files cannot be recomputed here")
            continue
        for path, digest in re.findall(r"((?:joulewise|scripts)/[A-Za-z0-9_/.]+\.py) (%s)[;.]" % HEX64, body):
            compare(f"{path} at the pinned harvest commit {pin[:9]}", digest,
                    hashlib.sha256(git(root, "show", f"{pin}:{path}")).hexdigest())
        changed = git(root, "diff", "--name-only", "--no-renames", h_claim, pin).decode().split()
        allowed = {"joulewise/b5/harvest.py", "joulewise/whole_window.py", "scripts/harvest_b5_window.py"}
        outside = [path for path in changed if path not in allowed and not path.startswith("tests/")]
        compare(f"paths changed between H_claim and {pin[:9]} outside the three harvest files and tests/", "", " ".join(outside))
        try:
            git(root, "merge-base", "--is-ancestor", h_claim, pin)
            print("equal    ", f"H_claim is an ancestor of {pin[:9]}")
        except subprocess.CalledProcessError:
            problems.append(f"H_claim is not an ancestor of the pinned harvest commit {pin}")
    pending = sorted(set(re.findall(r"PENDING\[[A-Z0-9-]+\]", text)))
    if pending:
        print("markers still to fill:", ", ".join(pending))

    if problems:
        print(f"seal record: {len(problems)} problem(s)")
        for problem in problems:
            print("  -", problem)
        return 1
    print(f"seal record: every digest recomputed and equal ({checked} comparisons)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
