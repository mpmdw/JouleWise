#!/usr/bin/env python3
"""Validate/copy the D-174 methods/diagnostic draft (2026-09-05).

The legacy filename is retained for callers. Three-way selection is retired:
only METHODS_DIAGNOSTIC is accepted. This guard never supplies empirical values.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ABSTRACT_WORD_LIMIT = 250
BRANCHES = ("METHODS_DIAGNOSTIC",)
ABSTRACT_HEADLINE = (
    "In a current-method re-analysis of one historical GPU (graphics-processor) pulse capture, all 59 "
    "fitted onsets occur after their commands and 49 of 59 fitted offsets occur "
    "before them; transfer of its timing allowance to inference remains untested."
)
CONCLUSION_HEADLINE = (
    "The current-method re-analysis places all 59 fitted onsets after their "
    "commands and 49 of 59 fitted offsets before them in the historical GPU "
    "pulse capture. Transfer of its timing allowance to inference remains "
    "untested."
)
TRANSFER_LIMITATION_SENTENCE = (
    "Transfer of the pulse-derived timing allowance to inference was not tested."
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _reader_facing_text(text: str) -> str:
    return HTML_COMMENT.sub(" ", text)


def _abstract_word_count(text: str) -> int:
    visible = _reader_facing_text(text)
    start, end = "## Abstract\n", "\n## 1. Introduction"
    if visible.count(start) != 1 or visible.count(end) != 1:
        raise ValueError("expected one Abstract followed by Section 1")
    return len(visible.split(start, 1)[1].split(end, 1)[0].split())


def _check_abstract_word_budget(text: str) -> int:
    words = _abstract_word_count(text)
    if words > ABSTRACT_WORD_LIMIT:
        raise ValueError(f"rendered Abstract has {words} words; limit is {ABSTRACT_WORD_LIMIT}")
    return words


def validate_methods_draft(text: str) -> int:
    if "OUTCOME-BRANCH" in text:
        raise ValueError("empirical outcome branches are retired under D-174")
    visible = _reader_facing_text(text)
    if "## First-use audit ledger" in visible:
        raise ValueError("editorial ledger belongs in the separate audit appendix")
    if visible.count("(protocol/prospective-comparison-protocol.md)") != 1:
        raise ValueError("article must cite the prospective protocol exactly once")
    for moved in ("## 3. Instrument characterization", "Two directional comparisons—",
                  "### Measured admission rules", "Under D-173,", "revision\n`3b1b1768"):
        if moved in visible:
            raise ValueError("prospective comparison material returned to the article")
    if "[FILL:" in visible:
        raise ValueError("reader-facing result fill remains")
    if re.search(r"\[FILL:(?:DS-|PG-|OB-|OR-|R_|V5-)", text):
        raise ValueError("retired empirical fill remains, including in comments")
    for start, end, headline in (("## Abstract\n", "## 1. Introduction", ABSTRACT_HEADLINE),
                                 ("## 8. Conclusion\n", "## 9. References", CONCLUSION_HEADLINE)):
        if visible.count(start) != 1 or visible.count(end) != 1:
            raise ValueError(f"expected one {start.strip()} section")
        section = visible.split(start, 1)[1].split(end, 1)[0]
        if " ".join(section.split()).count(headline) != 1:
            raise ValueError("Abstract and Conclusion must each retain their historical headline")
    normalized = " ".join(visible.split())
    if any(normalized.count(headline) != 1 for headline in (ABSTRACT_HEADLINE, CONCLUSION_HEADLINE)):
        raise ValueError("each historical headline must have exactly one placement")
    discussion = visible.split("## 5. Discussion and limitations\n", 1)[-1].split(
        "## 6. Related work", 1)[0]
    if discussion.count(TRANSFER_LIMITATION_SENTENCE) != 1:
        raise ValueError("Discussion must retain the fixed transfer limitation")
    if visible.count("(figures/fig4_edge_excursions.svg)") != 1:
        raise ValueError("historical Figure 2 must occur exactly once")
    return _check_abstract_word_budget(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outcome", choices=BRANCHES)
    parser.add_argument("--check-rendered", type=Path,
                        help="validate the single draft and its 250-word Abstract budget")
    args = parser.parse_args()
    if args.check_rendered is not None:
        if any(value is not None for value in (args.source, args.output, args.outcome)):
            parser.error("--check-rendered cannot be combined with copy arguments")
        words = validate_methods_draft(args.check_rendered.read_text(encoding="utf-8"))
        print(f"METHODS_DIAGNOSTIC validated; abstract_words={words}, limit={ABSTRACT_WORD_LIMIT}")
        return 0
    if args.source is None or args.output is None or args.outcome is None:
        parser.error("copy requires --source, --output, and --outcome METHODS_DIAGNOSTIC")
    if args.source.resolve() == args.output.resolve():
        parser.error("--output must differ from --source")
    text = args.source.read_text(encoding="utf-8")
    words = validate_methods_draft(text)
    try:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        parser.error(f"--output already exists: {args.output}")
    print(f"METHODS_DIAGNOSTIC copied unchanged; abstract_words={words}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
