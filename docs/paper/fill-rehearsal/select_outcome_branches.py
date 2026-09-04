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
    "REFUSAL": "**Refusal — stopped before comparison or at close-out:**",
}
BRANCHES = tuple(BRANCH_LABELS)
TRANSFER_MARKER = "[FILL:TR-01]"
FAILED_COMPONENTS_MARKER = "[FILL:OB-01]"
DECODE_VERDICT_MARKER = "[FILL:DS-32]"
PREFILL_VERDICT_MARKER = "[FILL:PG-08]"
REFUSAL_REASON_MARKER = "[FILL:OR-01]"


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
    expected_verdict_slots = 0 if outcome == "REFUSAL" else 1
    for marker in (DECODE_VERDICT_MARKER, PREFILL_VERDICT_MARKER):
        if rendered_text.count(marker) != expected_verdict_slots:
            raise ValueError(
                f"{group} {outcome} must contain {expected_verdict_slots} "
                f"{marker} slot(s)"
            )
    expected_refusal_slots = 1 if outcome == "REFUSAL" else 0
    if rendered_text.count(REFUSAL_REASON_MARKER) != expected_refusal_slots:
        raise ValueError(
            f"{group} {outcome} must contain {expected_refusal_slots} "
            f"{REFUSAL_REASON_MARKER} slot(s)"
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
    # Table 3 retains one governed slot for each verdict in every working copy;
    # A/B add one paragraph placement per branch group, while Refusal adds none.
    expected_verdict_slots = 1 + (0 if args.outcome == "REFUSAL" else len(GROUPS))
    for marker in (DECODE_VERDICT_MARKER, PREFILL_VERDICT_MARKER):
        if text.count(marker) != expected_verdict_slots:
            raise ValueError(f"selected draft has the wrong {marker} slot count")
    # The one Section-4 refusal form remains as the governed reference until
    # final filling; a selected Refusal adds one carrier in each branch group.
    expected_refusal_slots = 1 + (len(GROUPS) if args.outcome == "REFUSAL" else 0)
    if text.count(REFUSAL_REASON_MARKER) != expected_refusal_slots:
        raise ValueError("selected draft has the wrong refusal-reason slot count")
    try:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        parser.error(f"--output already exists: {args.output}")
    print(
        f"selected {args.outcome}: transfer_slots={len(GROUPS)}, "
        f"failed_component_slots={expected_failure_slots}, "
        f"verdict_slots={expected_verdict_slots}, "
        f"refusal_reason_slots={expected_refusal_slots}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
