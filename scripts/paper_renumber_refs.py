#!/usr/bin/env python3
"""Remove uncited references and renumber Markdown citations in one guarded pass.

The default mode is read-only.  Use ``--apply`` to rewrite a draft in place.
The frozen round-6 draft additionally requires ``--i-am-round-7``.

Exit codes:
    0  analysis or rewrite completed
    2  arguments, input structure, or I/O were invalid
    3  ``--apply`` found an already-renumbered document (or no work to do)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REFERENCE_HEADING = "## 11. References"
REFERENCE_LINE = re.compile(r"^(\d+)(\.\s+)(.*?)(\r?\n)?$")
NEXT_LEVEL_TWO_HEADING = re.compile(r"^## (?!#)", re.MULTILINE)
CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


class RenumberError(RuntimeError):
    """The draft does not satisfy the structure required for safe rewriting."""


@dataclass(frozen=True)
class ReferenceEntry:
    number: int
    separator: str
    text: str
    newline: str


@dataclass(frozen=True)
class Analysis:
    heading_start: int
    entries_start: int
    section_end: int
    references: tuple[ReferenceEntry, ...]
    cited: frozenset[int]
    orphans: tuple[int, ...]
    renumbering: dict[int, int]


def _reference_bounds(text: str) -> tuple[int, int, int]:
    heading_pattern = re.compile(rf"^{re.escape(REFERENCE_HEADING)}\s*$", re.MULTILINE)
    headings = list(heading_pattern.finditer(text))
    if len(headings) != 1:
        raise RenumberError(
            f"expected exactly one {REFERENCE_HEADING!r} heading, found {len(headings)}"
        )
    heading = headings[0]
    entries_start = heading.end()
    if text.startswith("\r\n", entries_start):
        entries_start += 2
    elif text.startswith("\n", entries_start):
        entries_start += 1
    following = NEXT_LEVEL_TWO_HEADING.search(text, entries_start)
    section_end = following.start() if following else len(text)
    return heading.start(), entries_start, section_end


def _parse_references(section: str) -> tuple[ReferenceEntry, ...]:
    entries: list[ReferenceEntry] = []
    for line in section.splitlines(keepends=True):
        if not line.strip():
            continue
        match = REFERENCE_LINE.fullmatch(line)
        if match is None:
            raise RenumberError(
                "reference section contains a nonblank line that is not a numbered entry: "
                f"{line.rstrip()!r}"
            )
        entries.append(
            ReferenceEntry(
                number=int(match.group(1)),
                separator=match.group(2),
                text=match.group(3),
                newline=match.group(4) or "",
            )
        )
    if not entries:
        raise RenumberError("reference section contains no entries")
    numbers = [entry.number for entry in entries]
    expected = list(range(1, len(entries) + 1))
    if numbers != expected:
        raise RenumberError(
            "reference numbers must be contiguous 1..N in list order; "
            f"found {numbers!r}"
        )
    return tuple(entries)


def _closing_fence(line: str, marker: str, width: int) -> bool:
    pattern = rf" {{0,3}}{re.escape(marker)}{{{width},}}\s*"
    return re.fullmatch(pattern, line.rstrip("\r\n")) is not None


def _rewrite_visible_line(
    line: str,
    maximum: int,
    replacement: dict[int, int] | None,
    in_display_math: bool,
    code_ticks: int | None,
) -> tuple[str, set[int], bool, int | None]:
    output: list[str] = []
    cited: set[int] = set()
    index = 0
    length = len(line)
    while index < length:
        if in_display_math:
            close = line.find(r"\]", index)
            if close < 0:
                output.append(line[index:])
                break
            output.append(line[index : close + 2])
            index = close + 2
            in_display_math = False
            continue

        if code_ticks is not None:
            delimiter = "`" * code_ticks
            close = line.find(delimiter, index)
            if close < 0:
                output.append(line[index:])
                break
            output.append(line[index : close + code_ticks])
            index = close + code_ticks
            code_ticks = None
            continue

        if line.startswith(r"\[", index):
            output.append(r"\[")
            index += 2
            in_display_math = True
            continue

        if line[index] == "`":
            end = index + 1
            while end < length and line[end] == "`":
                end += 1
            code_ticks = end - index
            output.append(line[index:end])
            index = end
            continue

        match = CITATION.match(line, index)
        if match is not None:
            previous_is_bracket = index > 0 and line[index - 1] == "["
            next_index = match.end()
            next_character = line[next_index : next_index + 1]
            numbers = [int(value) for value in re.findall(r"\d+", match.group(1))]
            is_known_citation = (
                not previous_is_bracket
                and next_character not in {"(", "]"}
                and all(1 <= number <= maximum for number in numbers)
            )
            if is_known_citation:
                cited.update(numbers)
                rendered = match.group(0)
                if replacement is not None:
                    rendered = re.sub(
                        r"\d+",
                        lambda number: str(replacement[int(number.group(0))]),
                        rendered,
                    )
                output.append(rendered)
                index = match.end()
                continue

        output.append(line[index])
        index += 1
    return "".join(output), cited, in_display_math, code_ticks


def transform_citations(
    text: str, maximum: int, replacement: dict[int, int] | None = None
) -> tuple[str, frozenset[int]]:
    """Find or rewrite numeric citations while preserving protected Markdown."""

    output: list[str] = []
    cited: set[int] = set()
    fence: tuple[str, int] | None = None
    in_display_math = False
    code_ticks: int | None = None

    for line in text.splitlines(keepends=True):
        if fence is not None:
            output.append(line)
            if _closing_fence(line, *fence):
                fence = None
            continue

        opened = FENCE_OPEN.match(line)
        if opened is not None and not in_display_math and code_ticks is None:
            marker_run = opened.group(1)
            fence = (marker_run[0], len(marker_run))
            output.append(line)
            continue

        rendered, line_cited, in_display_math, code_ticks = _rewrite_visible_line(
            line, maximum, replacement, in_display_math, code_ticks
        )
        output.append(rendered)
        cited.update(line_cited)

    return "".join(output), frozenset(cited)


def analyze_document(text: str) -> Analysis:
    heading_start, entries_start, section_end = _reference_bounds(text)
    references = _parse_references(text[entries_start:section_end])
    maximum = len(references)
    _, cited_before = transform_citations(text[:heading_start], maximum)
    _, cited_after = transform_citations(text[section_end:], maximum)
    cited = cited_before | cited_after
    present = {entry.number for entry in references}
    orphans = tuple(sorted(present - cited))
    kept = [entry.number for entry in references if entry.number not in orphans]
    renumbering = {old: new for new, old in enumerate(kept, start=1)}
    return Analysis(
        heading_start=heading_start,
        entries_start=entries_start,
        section_end=section_end,
        references=references,
        cited=cited,
        orphans=orphans,
        renumbering=renumbering,
    )


def rewrite_document(text: str, analysis: Analysis) -> str:
    maximum = len(analysis.references)
    prefix, cited_before = transform_citations(
        text[: analysis.heading_start], maximum, analysis.renumbering
    )
    suffix, cited_after = transform_citations(
        text[analysis.section_end :], maximum, analysis.renumbering
    )
    if cited_before | cited_after != analysis.cited:
        raise RenumberError("citation set changed while preparing the rewrite")

    reference_lines: list[str] = []
    entries = iter(analysis.references)
    current = next(entries, None)
    for line in text[analysis.entries_start : analysis.section_end].splitlines(keepends=True):
        if not line.strip():
            reference_lines.append(line)
            continue
        if current is None:
            raise RenumberError("reference list changed during rewrite")
        if current.number in analysis.renumbering:
            reference_lines.append(
                f"{analysis.renumbering[current.number]}{current.separator}"
                f"{current.text}{current.newline}"
            )
        current = next(entries, None)
    if current is not None:
        raise RenumberError("reference list changed during rewrite")

    heading = text[analysis.heading_start : analysis.entries_start]
    return prefix + heading + "".join(reference_lines) + suffix


def _write_atomic(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.renumber-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _print_analysis(path: Path, analysis: Analysis, mode: str) -> None:
    print(f"MODE: {mode}")
    print(f"DRAFT: {path}")
    print(f"REFERENCES: {len(analysis.references)}")
    print("CITED: " + ", ".join(str(number) for number in sorted(analysis.cited)))
    orphan_text = ", ".join(str(number) for number in analysis.orphans) or "(none)"
    print(f"ORPHANS: {orphan_text}")
    print("MAP:")
    for old, new in analysis.renumbering.items():
        print(f"  {old} -> {new}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("draft", type=Path, help="Markdown draft to inspect or rewrite")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="print the orphan set and old-to-new map without writing (default)",
    )
    mode.add_argument("--apply", action="store_true", help="rewrite the draft in place")
    parser.add_argument(
        "--i-am-round-7",
        action="store_true",
        help="required with --apply for the frozen docs/paper/draft-v1.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    draft = args.draft
    repository_root = Path(__file__).resolve().parent.parent
    frozen_draft = (repository_root / "docs" / "paper" / "draft-v1.md").resolve()

    if args.apply and draft.resolve() == frozen_draft and not args.i_am_round_7:
        print(
            "REFUSED: --apply on docs/paper/draft-v1.md requires --i-am-round-7",
            file=sys.stderr,
        )
        return 2

    try:
        text = draft.read_text(encoding="utf-8")
        analysis = analyze_document(text)
    except (OSError, UnicodeError, RenumberError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.apply and not analysis.orphans:
        print(
            "ALREADY RENUMBERED: reference list is contiguous, has no orphans, "
            "and its citation numbering has no further work",
            file=sys.stderr,
        )
        return 3

    mode = "apply" if args.apply else "dry-run"
    _print_analysis(draft, analysis, mode)
    if not args.apply:
        print("RESULT: no changes written")
        return 0

    try:
        rewritten = rewrite_document(text, analysis)
        _write_atomic(draft, rewritten)
    except (OSError, RenumberError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"RESULT: rewrote {draft} with {len(analysis.renumbering)} references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
