#!/usr/bin/env python3
"""Select the same A, B, or Refusal branch in the three seat-G regions."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


GROUPS = ("ABSTRACT", "DISCUSSION", "CONCLUSION")
BRANCH_LABELS = {
    "A": "**A — every required ratio passes:**",
    "B": "**B — an authenticated, evaluable ratio is below 2:**",
    "REFUSAL": (
        "**Refusal — a required ratio is missing, unauthenticated, or has a "
        "zero denominator:**"
    ),
}
BRANCHES = tuple(BRANCH_LABELS)
TRANSFER_MARKER = "[FILL:TR-01]"
FAILED_COMPONENTS_MARKER = "[FILL:OB-01]"


def _select_group(text: str, group: str, outcome: str) -> str:
    start = f"<!-- OUTCOME-BRANCHES:{group}:START -->"
    end = f"<!-- OUTCOME-BRANCHES:{group}:END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"expected one complete {group} branch group")
    before, remainder = text.split(start, 1)
    body, after = remainder.split(end, 1)

    pattern = re.compile(
        r"<!-- OUTCOME-BRANCH:(A|B|REFUSAL):START -->\n"
        r"(.*?)"
        r"<!-- OUTCOME-BRANCH:\1:END -->",
        re.DOTALL,
    )
    matches = list(pattern.finditer(body))
    if tuple(match.group(1) for match in matches) != BRANCHES:
        raise ValueError(f"{group} must contain A, B, and REFUSAL in that order")
    residue = pattern.sub("", body)
    if residue.strip():
        raise ValueError(f"unexpected text outside {group} branch blocks")

    selected = next(match.group(2) for match in matches if match.group(1) == outcome)
    lines = selected.strip().splitlines()
    expected_label = BRANCH_LABELS[outcome]
    if not lines or lines[0] != expected_label:
        raise ValueError(f"{group} {outcome} label is not {expected_label!r}")
    lines = lines[1:]
    while lines and not lines[0].strip():
        lines.pop(0)

    rendered: list[str] = []
    for line in lines:
        if line == ">":
            rendered.append("")
        elif line.startswith("> "):
            rendered.append(line[2:])
        else:
            raise ValueError(f"{group} {outcome} contains a non-quoted content line")
    rendered_text = "\n".join(rendered).strip()
    if rendered_text.count(TRANSFER_MARKER) != 1:
        raise ValueError(
            f"{group} {outcome} must contain exactly one {TRANSFER_MARKER} slot"
        )
    expected_failure_slots = 1 if outcome == "B" else 0
    if rendered_text.count(FAILED_COMPONENTS_MARKER) != expected_failure_slots:
        raise ValueError(
            f"{group} {outcome} must contain {expected_failure_slots} "
            f"{FAILED_COMPONENTS_MARKER} slot(s)"
        )
    return before + rendered_text + "\n\n" + after.lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--outcome", required=True, choices=BRANCHES)
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        parser.error("--output must differ from --source; select into a working copy")
    text = args.source.read_text(encoding="utf-8")
    for group in GROUPS:
        text = _select_group(text, group, args.outcome)
    if "<!-- OUTCOME-BRANCHES:" in text or "<!-- OUTCOME-BRANCH:" in text:
        raise ValueError("an outcome branch marker remains after selection")
    if text.count(TRANSFER_MARKER) != len(GROUPS):
        raise ValueError("selected draft lost a branch-independent transfer-result slot")
    expected_failure_slots = len(GROUPS) if args.outcome == "B" else 0
    if text.count(FAILED_COMPONENTS_MARKER) != expected_failure_slots:
        raise ValueError("selected draft has the wrong failed-component slot count")
    try:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        parser.error(f"--output already exists: {args.output}")
    print(
        f"selected {args.outcome}: transfer_slots={len(GROUPS)}, "
        f"failed_component_slots={expected_failure_slots}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
