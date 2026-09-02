from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
DRAFT = Path(
    os.environ.get(
        "PAPER_FIRST_USE_DRAFT",
        REPO / "docs" / "paper" / "draft-v2-skeleton.md",
    )
)
LEDGER_HEADING = "## First-use audit ledger"
TABLE_HEADER = "| Term | First reader-facing home | Status | Definition or disposition |"
STATUSES = frozenset(
    {
        "built-before",
        "glossed-at-first-use",
        "audience-vocabulary",
        "forward-pointer-next-paragraph",
        "FAILS",
    }
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
BOLD_PHRASE = re.compile(r"\*\*(.+?)\*\*")
SECTION_HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*$")


@dataclass(frozen=True)
class LedgerRow:
    term: str
    home: str
    status: str
    disposition: str


def _strip_comments_preserving_lines(text: str) -> str:
    return HTML_COMMENT.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def _display_text(value: str) -> str:
    """Remove presentation-only Markdown while preserving literal LaTeX."""

    value = value.strip()
    while len(value) >= 2 and (
        (value.startswith("`") and value.endswith("`"))
        or (value.startswith("*") and value.endswith("*"))
    ):
        value = value[1:-1].strip()
    return value.rstrip(".:").strip()


def _alternatives(term: str) -> tuple[str, ...]:
    return tuple(_display_text(part) for part in term.split(" / "))


def _occurs(alternative: str, line: str) -> bool:
    """Match a literal alternative without accepting substrings of words."""

    escaped = re.escape(alternative)
    if alternative and (alternative[0].isalnum() or alternative[0] == "_"):
        escaped = rf"(?<!\w){escaped}"
    if alternative and (alternative[-1].isalnum() or alternative[-1] == "_"):
        escaped = rf"{escaped}(?!\w)"
    return re.search(escaped, line, re.IGNORECASE) is not None


def _parse_ledger(text: str) -> tuple[list[LedgerRow], list[str]]:
    lines = text.splitlines()
    try:
        ledger_line = lines.index(LEDGER_HEADING)
    except ValueError as error:
        raise AssertionError(f"missing ledger heading: {LEDGER_HEADING}") from error

    try:
        table_line = lines.index(TABLE_HEADER, ledger_line + 1)
    except ValueError as error:
        raise AssertionError(f"missing ledger table header: {TABLE_HEADER}") from error

    rows: list[LedgerRow] = []
    for line in lines[table_line + 2 :]:
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            raise AssertionError(f"ledger row must have four cells: {line}")
        rows.append(LedgerRow(*cells))
    return rows, lines[:ledger_line]


def _section_for_line(body_lines: list[str], line_index: int) -> str | None:
    for candidate in range(line_index, -1, -1):
        match = SECTION_HEADING.match(body_lines[candidate])
        if match:
            return match.group(2)
    return None


class PaperFirstUseLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DRAFT.read_text(encoding="utf-8")
        cls.rows, raw_body_lines = _parse_ledger(cls.text)
        cls.body_lines = _strip_comments_preserving_lines(
            "\n".join(raw_body_lines)
        ).splitlines()

    def test_ledger_shape_statuses_and_count(self) -> None:
        self.assertGreaterEqual(len(self.rows), 60)

        terms = [row.term.casefold() for row in self.rows]
        self.assertEqual(len(terms), len(set(terms)), "duplicate ledger Term cells")

        alternatives = [
            alternative.casefold()
            for row in self.rows
            for alternative in _alternatives(row.term)
        ]
        self.assertNotIn("", alternatives, "empty Term alternative")
        self.assertEqual(
            len(alternatives),
            len(set(alternatives)),
            "duplicate ledger Term alternatives",
        )

        unknown = sorted({row.status for row in self.rows} - STATUSES)
        self.assertEqual(unknown, [], f"unknown ledger statuses: {unknown}")
        failures = [row.term for row in self.rows if row.status == "FAILS"]
        self.assertEqual(failures, [], f"unresolved first-use rows: {failures}")

        count_sentences = re.findall(r"Terms inventoried: (\d+); FAILS: (\d+)\.", self.text)
        self.assertEqual(len(count_sentences), 1, "expected one mechanical count sentence")
        row_count, fail_count = map(int, count_sentences[0])
        self.assertEqual(row_count, len(self.rows))
        self.assertEqual(fail_count, len(failures))

    def test_first_occurrence_is_in_exact_home_section(self) -> None:
        known_homes = {
            match.group(2)
            for line in self.body_lines
            if (match := SECTION_HEADING.match(line))
        }
        for row in self.rows:
            with self.subTest(term=row.term):
                self.assertIn(row.home, known_homes, f"unknown home for {row.term}")
                alternatives = _alternatives(row.term)
                first_index = None
                for index, line in enumerate(self.body_lines):
                    # A heading names a section; it is not a body occurrence inside
                    # that section. Tables remain reader-facing body and are searched.
                    if line.startswith("#"):
                        continue
                    if any(_occurs(part, line) for part in alternatives):
                        first_index = index
                        break
                self.assertIsNotNone(first_index, f"orphan ledger term: {row.term}")
                assert first_index is not None
                actual_home = _section_for_line(self.body_lines, first_index)
                self.assertEqual(
                    actual_home,
                    row.home,
                    f"{row.term!r} first occurs on line {first_index + 1} "
                    f"in {actual_home!r}, not {row.home!r}: "
                    f"{self.body_lines[first_index].strip()}",
                )

    def test_bold_multiword_introductions_are_in_ledger(self) -> None:
        # One-token bold uses include outcome labels, symbols, and ordinary
        # emphasis. Requiring at least two lexical words keeps this closure rule
        # deterministic while covering phrase-shaped term introductions.
        inventoried = {
            alternative.casefold()
            for row in self.rows
            for alternative in _alternatives(row.term)
        }
        missing: list[str] = []
        for line_number, line in enumerate(self.body_lines, 1):
            if line.startswith("#") or line.lstrip().startswith("|"):
                continue
            for raw_phrase in BOLD_PHRASE.findall(line):
                phrase = _display_text(raw_phrase)
                lexical_words = [
                    token for token in phrase.split() if any(char.isalpha() for char in token)
                ]
                if len(lexical_words) >= 2 and phrase.casefold() not in inventoried:
                    missing.append(f"line {line_number}: {phrase}")
        self.assertEqual(missing, [], "bold phrase(s) absent from ledger:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
