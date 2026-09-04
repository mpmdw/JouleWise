#!/usr/bin/env python3
"""Select one seat-G outcome and enforce its rendered Abstract budget."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


GROUPS = ("ABSTRACT", "DISCUSSION", "CONCLUSION")
ABSTRACT_WORD_LIMIT = 250
BRANCH_LABELS = {
    "A": "**A — every required ratio passes:**",
    "B": "**B — an authenticated, evaluable ratio is below 2:**",
    # The governed label names both OR-01 stop stages; the selected prose
    # supplies the stage-specific conditions and issued-reason slot.
    "REFUSAL": "**Refusal — stopped before comparison or at close-out:**",
}
BRANCHES = tuple(BRANCH_LABELS)
TRANSFER_MARKER = "[FILL:TR-01]"
FAILED_COMPONENTS_MARKER = "[FILL:OB-01]"
DECODE_VERDICT_MARKER = "[FILL:DS-32]"
PREFILL_VERDICT_MARKER = "[FILL:PG-08]"
REFUSAL_REASON_MARKER = "[FILL:OR-01]"
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _reader_facing_text(text: str) -> str:
    """Remove HTML comments before reader-facing counts."""

    return HTML_COMMENT.sub(" ", text)


def _abstract_word_count(text: str) -> int:
    """Count whitespace-delimited words in the rendered Abstract body."""

    visible = _reader_facing_text(text)
    start = "## Abstract\n"
    end = "\n## 1. Introduction"
    if visible.count(start) != 1 or visible.count(end) != 1:
        raise ValueError("expected one Abstract followed by Section 1")
    abstract = visible.split(start, 1)[1].split(end, 1)[0]
    return len(abstract.split())


def _check_abstract_word_budget(text: str) -> int:
    words = _abstract_word_count(text)
    if words > ABSTRACT_WORD_LIMIT:
        raise ValueError(
            f"rendered Abstract has {words} words; limit is {ABSTRACT_WORD_LIMIT}"
        )
    return words


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
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outcome", choices=BRANCHES)
    parser.add_argument(
        "--check-rendered",
        type=Path,
        help="check the 250-word limit on an already selected, fully filled draft",
    )
    args = parser.parse_args()

    if args.check_rendered is not None:
        if any(value is not None for value in (args.source, args.output, args.outcome)):
            parser.error("--check-rendered cannot be combined with selection arguments")
        words = _check_abstract_word_budget(
            args.check_rendered.read_text(encoding="utf-8")
        )
        print(f"rendered abstract_words={words}, limit={ABSTRACT_WORD_LIMIT}")
        return 0

    if args.source is None or args.output is None or args.outcome is None:
        parser.error("selection requires --source, --output, and --outcome")

    if args.source.resolve() == args.output.resolve():
        parser.error("--output must differ from --source; select into a working copy")
    text = args.source.read_text(encoding="utf-8")
    for group in GROUPS:
        text = _select_group(text, group, args.outcome)
    if "<!-- OUTCOME-BRANCHES:" in text or "<!-- OUTCOME-BRANCH:" in text:
        raise ValueError("an outcome branch marker remains after selection")
    reader_text = _reader_facing_text(text)
    if reader_text.count(TRANSFER_MARKER) != len(GROUPS):
        raise ValueError("selected draft lost a branch-independent transfer-result slot")
    expected_failure_slots = len(GROUPS) if args.outcome == "B" else 0
    if reader_text.count(FAILED_COMPONENTS_MARKER) != expected_failure_slots:
        raise ValueError("selected draft has the wrong failed-component slot count")
    # Table 3 retains one governed slot for each verdict in every working copy;
    # A/B add one paragraph placement per branch group, while Refusal adds none.
    expected_verdict_slots = 1 + (0 if args.outcome == "REFUSAL" else len(GROUPS))
    for marker in (DECODE_VERDICT_MARKER, PREFILL_VERDICT_MARKER):
        if reader_text.count(marker) != expected_verdict_slots:
            raise ValueError(f"selected draft has the wrong {marker} slot count")
    # The one Section-4 refusal form remains as the governed reference until
    # final filling; a selected Refusal adds one carrier in each branch group.
    expected_refusal_slots = 1 + (len(GROUPS) if args.outcome == "REFUSAL" else 0)
    if reader_text.count(REFUSAL_REASON_MARKER) != expected_refusal_slots:
        raise ValueError("selected draft has the wrong refusal-reason slot count")
    abstract_words = _check_abstract_word_budget(text)
    try:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        parser.error(f"--output already exists: {args.output}")
    print(
        f"selected {args.outcome}: transfer_slots={len(GROUPS)}, "
        f"failed_component_slots={expected_failure_slots}, "
        f"verdict_slots={expected_verdict_slots}, "
        f"refusal_reason_slots={expected_refusal_slots}, "
        f"abstract_words={abstract_words}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
