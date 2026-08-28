#!/usr/bin/env python3
"""Dependency-free structural lint for the frozen JouleWise paper draft."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit


PAPER_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DRAFT = PAPER_DIR / "draft-v1.md"
DEFINITION_RE = re.compile(r"^[ ]{0,3}\[([^\]^][^\]]*)\]:\s*(\S+)", re.MULTILINE)
FOOTNOTE_DEFINITION_RE = re.compile(r"^[ ]{0,3}\[\^([^\]]+)\]:", re.MULTILINE)
INLINE_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(\s*(<[^>]+>|[^\s)]+)", re.MULTILINE
)
REFERENCE_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\[([^\]]*)\]")
REFERENCE_LINK_RE = re.compile(r"(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]")
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^([^\]]+)\]")
PENDING_RE = re.compile(r"\[[^\]\n]*PENDING[^\]\n]*\]", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
TABLE_DELIMITER_RE = re.compile(r"^:?-{3,}:?$")


@dataclass(frozen=True)
class Paragraph:
    line: int
    text: str


@dataclass(frozen=True)
class TableDefect:
    line: int
    expected: int
    observed: int


@dataclass(frozen=True)
class MathInventory:
    inline: int
    display: int
    unterminated: tuple[str, ...]


def _normalise_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def _paragraphs(lines: list[str]) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    pending: list[str] = []
    start = 0
    for number, line in enumerate(lines, start=1):
        if line.strip():
            if not pending:
                start = number
            pending.append(line)
        elif pending:
            paragraphs.append(Paragraph(start, "\n".join(pending)))
            pending = []
    if pending:
        paragraphs.append(Paragraph(start, "\n".join(pending)))
    return paragraphs


def _unescaped_runs(text: str, character: str) -> list[int]:
    runs: list[int] = []
    index = 0
    while index < len(text):
        if text[index] != character:
            index += 1
            continue
        preceding = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            preceding += 1
            cursor -= 1
        end = index + 1
        while end < len(text) and text[end] == character:
            end += 1
        if preceding % 2 == 0:
            runs.append(end - index)
        index = end
    return runs


def _is_whitespace(character: str | None) -> bool:
    return character is None or character.isspace()


def _is_punctuation(character: str | None) -> bool:
    return character is not None and unicodedata.category(character)[0] in {"P", "S"}


def _delimiter_count(text: str, marker: str) -> int:
    """Count CommonMark-flanking emphasis runs, excluding intraword underscores."""

    count = 0
    index = 0
    while index < len(text):
        if text[index] != marker:
            index += 1
            continue
        preceding_backslashes = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            preceding_backslashes += 1
            cursor -= 1
        end = index + 1
        while end < len(text) and text[end] == marker:
            end += 1
        if preceding_backslashes % 2:
            index = end
            continue

        before = text[index - 1] if index else None
        after = text[end] if end < len(text) else None
        left_flanking = not _is_whitespace(after) and (
            not _is_punctuation(after)
            or _is_whitespace(before)
            or _is_punctuation(before)
        )
        right_flanking = not _is_whitespace(before) and (
            not _is_punctuation(before)
            or _is_whitespace(after)
            or _is_punctuation(after)
        )
        if marker == "_":
            can_open = left_flanking and (not right_flanking or _is_punctuation(before))
            can_close = right_flanking and (not left_flanking or _is_punctuation(after))
        else:
            can_open = left_flanking
            can_close = right_flanking
        if can_open or can_close:
            count += end - index
        index = end
    return count


def _mask_code_and_tex(text: str) -> str:
    if re.match(r"^\s*(```+|~~~+)", text) or all(
        not line or line.startswith("       ") for line in text.splitlines()
    ):
        return " " * len(text)
    text = re.sub(
        r"<!--.*?-->", lambda match: " " * len(match.group()), text, flags=re.DOTALL
    )
    chars = list(text)
    backticks = list(re.finditer(r"(?<!\\)(`+)", text))
    openers: dict[int, re.Match[str]] = {}
    for match in backticks:
        length = len(match.group(1))
        opener = openers.pop(length, None)
        if opener is None:
            openers[length] = match
        else:
            for index in range(opener.start(), match.end()):
                chars[index] = " "
    masked = "".join(chars)
    masked = re.sub(
        r"\\\((?:\\.|.)*?\\\)",
        lambda match: " " * len(match.group()),
        masked,
        flags=re.DOTALL,
    )
    masked = re.sub(
        r"\\\[(?:\\.|.)*?\\\]",
        lambda match: " " * len(match.group()),
        masked,
        flags=re.DOTALL,
    )
    masked = re.sub(
        r"\$\$.*?\$\$",
        lambda match: " " * len(match.group()),
        masked,
        flags=re.DOTALL,
    )
    return masked


def _math_inventory(source: str) -> MathInventory:
    """Count TeX spans and identify open delimiters without a closer."""

    inline = 0
    display = 0
    unterminated: list[str] = []
    delimiters = (
        (r"\(", r"\)", "inline"),
        (r"\[", r"\]", "display"),
        ("$$", "$$", "display"),
    )
    index = 0
    while index < len(source):
        candidates = [
            (source.find(opener, index), opener, closer, kind)
            for opener, closer, kind in delimiters
        ]
        candidates = [candidate for candidate in candidates if candidate[0] >= 0]
        if not candidates:
            break
        start, opener, closer, kind = min(candidates, key=lambda item: item[0])
        end = source.find(closer, start + len(opener))
        if kind == "inline":
            line_end = source.find("\n", start + len(opener))
            if line_end >= 0 and (end < 0 or end > line_end):
                end = -1
        if end < 0:
            line = source.count("\n", 0, start) + 1
            unterminated.append(
                f"line {line}: unterminated {kind} math delimiter {opener!r}"
            )
            index = start + len(opener)
            continue
        if kind == "inline":
            inline += 1
        else:
            display += 1
        index = end + len(closer)
    return MathInventory(inline, display, tuple(unterminated))


def _mask_balanced_star_emphasis(text: str) -> str:
    masked = re.sub(
        r"\*\*[^*\n]+?\*\*", lambda match: " " * len(match.group()), text
    )
    return re.sub(
        r"(?<!\*)\*[^*\n]+?\*(?!\*)",
        lambda match: " " * len(match.group()),
        masked,
    )


def _marker_findings(paragraphs: list[Paragraph]) -> list[str]:
    findings: list[str] = []
    for paragraph in paragraphs:
        if re.match(r"^\s*(```+|~~~+)", paragraph.text):
            continue
        without_comments = re.sub(
            r"<!--.*?-->",
            lambda match: " " * len(match.group()),
            paragraph.text,
            flags=re.DOTALL,
        )
        backtick_runs = _unescaped_runs(without_comments, "`")
        by_length = Counter(backtick_runs)
        for length, count in sorted(by_length.items()):
            if count % 2:
                findings.append(
                    f"line {paragraph.line}: backtick run length {length} occurs {count} times"
                )
        masked = _mask_code_and_tex(paragraph.text)
        for marker in ("*", "_"):
            marker_text = _mask_balanced_star_emphasis(masked) if marker == "_" else masked
            count = _delimiter_count(marker_text, marker)
            if count % 2:
                findings.append(
                    f"line {paragraph.line}: {marker!r} occurs {count} unescaped times"
                )
    return findings


def _math_findings(paragraphs: list[Paragraph]) -> list[str]:
    findings: list[str] = []
    for paragraph in paragraphs:
        masked = _mask_code_and_tex(paragraph.text)
        double_count = 0
        single_count = 0
        index = 0
        while index < len(masked):
            if masked[index] != "$":
                index += 1
                continue
            preceding = 0
            cursor = index - 1
            while cursor >= 0 and masked[cursor] == "\\":
                preceding += 1
                cursor -= 1
            if preceding % 2:
                index += 1
                continue
            if index + 1 < len(masked) and masked[index + 1] == "$":
                double_count += 1
                index += 2
            else:
                single_count += 1
                index += 1
        if double_count % 2:
            findings.append(
                f"line {paragraph.line}: '$$' occurs {double_count} times"
            )
        if single_count % 2:
            findings.append(f"line {paragraph.line}: '$' occurs {single_count} times")
    return findings


def _heading_jumps(lines: list[str]) -> list[str]:
    findings: list[str] = []
    previous_level: int | None = None
    previous_line: int | None = None
    fence: str | None = None
    for line_number, line in enumerate(lines, start=1):
        fence_match = re.match(r"^\s*(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            fence = None if fence == marker else marker
            continue
        if fence is not None:
            continue
        match = HEADING_RE.match(line)
        if match is None:
            continue
        level = len(match.group(1))
        if previous_level is not None and level > previous_level + 1:
            findings.append(
                f"line {line_number}: h{previous_level} at line {previous_line} jumps to h{level}"
            )
        previous_level = level
        previous_line = line_number
    return findings


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        stripped = stripped[:-1]

    cells: list[str] = []
    current: list[str] = []
    code_run = 0
    index = 0
    while index < len(stripped):
        char = stripped[index]
        if char == "`":
            end = index + 1
            while end < len(stripped) and stripped[end] == "`":
                end += 1
            run = end - index
            code_run = 0 if code_run == run else run
            current.extend(stripped[index:end])
            index = end
            continue
        if char == "\\" and index + 1 < len(stripped):
            current.extend(stripped[index : index + 2])
            index += 2
            continue
        if char == "|" and code_run == 0:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def _table_defects(lines: list[str]) -> tuple[int, list[TableDefect]]:
    table_count = 0
    defects: list[TableDefect] = []
    index = 0
    while index + 1 < len(lines):
        header = _split_table_row(lines[index])
        delimiter = _split_table_row(lines[index + 1])
        is_delimiter = bool(delimiter) and all(
            TABLE_DELIMITER_RE.fullmatch(cell) for cell in delimiter
        )
        if "|" not in lines[index] or not is_delimiter:
            index += 1
            continue

        table_count += 1
        expected = len(header)
        row_index = index + 1
        while row_index < len(lines) and "|" in lines[row_index] and lines[row_index].strip():
            observed = len(_split_table_row(lines[row_index]))
            if observed != expected:
                defects.append(TableDefect(row_index + 1, expected, observed))
            row_index += 1
        index = row_index
    return table_count, defects


def _definition_map(source: str) -> dict[str, str]:
    return {
        _normalise_label(match.group(1)): match.group(2)
        for match in DEFINITION_RE.finditer(source)
    }


def _undefined_references(source: str, definitions: dict[str, str]) -> list[str]:
    findings: list[str] = []
    for match in REFERENCE_LINK_RE.finditer(source):
        label = match.group(2) or match.group(1)
        if _normalise_label(label) not in definitions:
            line = source.count("\n", 0, match.start()) + 1
            findings.append(f"line {line}: [{match.group(1)}][{match.group(2)}]")
    return findings


def _is_remote(destination: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination)) or destination.startswith("//")


def _resolved_image_path(destination: str, draft_path: Path) -> Path | None:
    raw = destination[1:-1] if destination.startswith("<") and destination.endswith(">") else destination
    if _is_remote(raw) or raw.startswith("#"):
        return None
    parsed = urlsplit(raw)
    return draft_path.parent / unquote(parsed.path)


def _missing_images(
    source: str, draft_path: Path, definitions: dict[str, str]
) -> tuple[int, list[str]]:
    checked = 0
    findings: list[str] = []
    for match in INLINE_IMAGE_RE.finditer(source):
        destination = match.group(2)
        path = _resolved_image_path(destination, draft_path)
        if path is None:
            continue
        checked += 1
        if not path.is_file():
            line = source.count("\n", 0, match.start()) + 1
            findings.append(f"line {line}: {destination} -> {path}")
    for match in REFERENCE_IMAGE_RE.finditer(source):
        label = _normalise_label(match.group(2) or match.group(1))
        destination = definitions.get(label)
        if destination is None:
            line = source.count("\n", 0, match.start()) + 1
            findings.append(f"line {line}: undefined image reference [{label}]")
            continue
        path = _resolved_image_path(destination, draft_path)
        if path is None:
            continue
        checked += 1
        if not path.is_file():
            line = source.count("\n", 0, match.start()) + 1
            findings.append(f"line {line}: {destination} -> {path}")
    return checked, findings


def _undefined_footnotes(source: str) -> list[str]:
    definitions = {
        _normalise_label(match.group(1))
        for match in FOOTNOTE_DEFINITION_RE.finditer(source)
    }
    refs: dict[str, list[int]] = defaultdict(list)
    for match in FOOTNOTE_REFERENCE_RE.finditer(source):
        label = _normalise_label(match.group(1))
        refs[label].append(source.count("\n", 0, match.start()) + 1)
    return [
        f"{label} at line(s) {','.join(str(line) for line in lines)}"
        for label, lines in sorted(refs.items())
        if label not in definitions
    ]


def _pending_inventory(source: str) -> list[str]:
    occurrences: dict[str, list[int]] = defaultdict(list)
    for match in PENDING_RE.finditer(source):
        occurrences[match.group(0)].append(source.count("\n", 0, match.start()) + 1)
    return [
        f"{marker}: {len(lines)} occurrence(s), line(s) {','.join(map(str, lines))}"
        for marker, lines in sorted(occurrences.items())
    ]


def _unicode_quote_dash_inventory(source: str) -> list[str]:
    counts = Counter(
        char
        for char in source
        if ord(char) > 127
        and (unicodedata.category(char) in {"Pi", "Pf", "Pd"} or char == "−")
    )
    return [
        f"U+{ord(char):04X} {unicodedata.name(char, 'UNKNOWN')} ({char}): {count}"
        for char, count in sorted(counts.items(), key=lambda item: ord(item[0]))
    ]


def _report_group(label: str, findings: list[str]) -> list[str]:
    rows = [f"{label}: {len(findings)}"]
    rows.extend(f"  {finding}" for finding in findings)
    return rows


def check_markdown(draft_path: Path) -> tuple[str, bool]:
    """Return the complete report and whether a hard defect was found."""

    draft_path = draft_path.resolve()
    source = draft_path.read_text(encoding="utf-8")
    lines = source.splitlines()
    paragraphs = _paragraphs(lines)
    definitions = _definition_map(source)

    marker_findings = _marker_findings(paragraphs)
    math_inventory = _math_inventory(source)
    math_findings = _math_findings(paragraphs)
    reference_findings = _undefined_references(source, definitions)
    checked_images, missing_images = _missing_images(source, draft_path, definitions)
    heading_findings = _heading_jumps(lines)
    table_count, table_defects = _table_defects(lines)
    pending_inventory = _pending_inventory(source)
    footnote_findings = _undefined_footnotes(source)
    unicode_inventory = _unicode_quote_dash_inventory(source)

    hard_defect = bool(missing_images or table_defects or math_inventory.unterminated)
    report = [f"Markdown check: {draft_path}"]
    report.extend(_report_group("Unbalanced emphasis/code markers", marker_findings))
    report.append(
        f"Math spans: {math_inventory.inline} inline, {math_inventory.display} display; "
        f"unterminated: {len(math_inventory.unterminated)}"
    )
    report.extend(
        _report_group("Unterminated math spans", list(math_inventory.unterminated))
    )
    report.extend(_report_group("Unmatched $ math delimiters", math_findings))
    report.extend(_report_group("Undefined reference-style links", reference_findings))
    report.append(f"Images checked: {checked_images}")
    report.extend(_report_group("Missing images", missing_images))
    report.extend(_report_group("Heading-level jumps", heading_findings))
    table_rows = [
        f"line {defect.line}: expected {defect.expected} columns, found {defect.observed}"
        for defect in table_defects
    ]
    report.append(f"Tables checked: {table_count}")
    report.extend(_report_group("Broken table rows", table_rows))
    marker_count = len(PENDING_RE.findall(source))
    report.append(f"Pending-family markers (expected): {marker_count}")
    report.extend(f"  {row}" for row in pending_inventory)
    report.extend(_report_group("Undefined footnote references", footnote_findings))
    unicode_total = sum(
        1
        for char in source
        if ord(char) > 127
        and (unicodedata.category(char) in {"Pi", "Pf", "Pd"} or char == "−")
    )
    report.append(f"Non-ASCII quote/dash inventory: {unicode_total}")
    report.extend(f"  {row}" for row in unicode_inventory)
    hard_defect_count = (
        len(missing_images) + len(table_defects) + len(math_inventory.unterminated)
    )
    report.append(f"Hard defects: {hard_defect_count}")
    report.append(f"Exit: {1 if hard_defect else 0}")
    return "\n".join(report) + "\n", hard_defect


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check structural Markdown defects.")
    parser.add_argument(
        "draft",
        nargs="?",
        type=Path,
        default=DEFAULT_DRAFT,
        help=f"Markdown input (default: {DEFAULT_DRAFT})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report, hard_defect = check_markdown(args.draft)
    except (OSError, UnicodeError) as exc:
        print(f"markdown check error: {exc}", file=sys.stderr)
        return 1
    print(report, end="")
    return 1 if hard_defect else 0


if __name__ == "__main__":
    raise SystemExit(main())
