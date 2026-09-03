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
FINAL_WORD = re.compile(r"([A-Za-z]+)$")
COMPOUND_JOIN = r"(?:\s+|[-\u2010\u2011])"


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


def _number_forms(word: str) -> tuple[str, ...]:
    """Return conservative singular/plural spellings for a final word."""

    folded = word.casefold()
    forms = {word}
    if folded.endswith("ies") and len(word) > 3:
        forms.add(word[:-3] + "y")
    elif folded.endswith(("ches", "shes", "xes", "zes")) and len(word) > 2:
        forms.add(word[:-2])
    elif folded.endswith("s") and not folded.endswith(("ss", "ics")):
        forms.add(word[:-1])
    elif folded.endswith("y") and len(word) > 1 and folded[-2] not in "aeiou":
        forms.add(word[:-1] + "ies")
    elif folded.endswith(("ch", "sh", "x", "z")):
        forms.add(word + "es")
    else:
        forms.add(word + "s")
    return tuple(sorted(forms, key=lambda value: (-len(value), value)))


def _alternative_pattern(alternative: str) -> re.Pattern[str]:
    """Match number, possessive, and hyphenated forms of one ledger term."""

    # Several ledger entries are exact, capitalized appendix labels rather
    # than terms of art. Inflecting "The model" into ordinary prose such as
    # "the models" would turn the label inventory into a false positive.
    if alternative.startswith("The "):
        escaped = re.escape(alternative)
        return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)

    final = FINAL_WORD.search(alternative)
    if final is None:
        core = re.escape(alternative)
        if alternative and (alternative[0].isalnum() or alternative[0] == "_"):
            core = rf"(?<!\w){core}"
        if alternative and (alternative[-1].isalnum() or alternative[-1] == "_"):
            core = rf"{core}(?!\w)"
        return re.compile(core, re.IGNORECASE)

    prefix = alternative[: final.start()]
    escaped_prefix = re.escape(prefix)
    for separator in (r"\ ", r"\-", "‐", "‑"):
        escaped_prefix = escaped_prefix.replace(separator, COMPOUND_JOIN)
    form_patterns = []
    for value in _number_forms(final.group(1)):
        escaped = re.escape(value)
        possessive = (
            rf"(?:['\u2019]s|['\u2019])?"
            if value.casefold().endswith("s")
            else rf"(?:['\u2019]s)?"
        )
        form_patterns.append(escaped + possessive)
    core = rf"{escaped_prefix}(?:{'|'.join(form_patterns)})"
    if alternative[0].isalnum() or alternative[0] == "_":
        core = rf"(?<!\w){core}"
    core = rf"{core}(?!\w)"
    return re.compile(core, re.IGNORECASE)


def _occurs(alternative: str, line: str) -> bool:
    """Locate a ledger term, including its ordinary inflected forms."""

    return _alternative_pattern(alternative).search(line) is not None


def _occurs_exact(alternative: str, line: str) -> bool:
    """Retain the former literal matcher for regression discrimination."""

    escaped = re.escape(alternative)
    if alternative and (alternative[0].isalnum() or alternative[0] == "_"):
        escaped = rf"(?<!\w){escaped}"
    if alternative and (alternative[-1].isalnum() or alternative[-1] == "_"):
        escaped = rf"{escaped}(?!\w)"
    return re.search(escaped, line, re.IGNORECASE) is not None


def _first_occurrence(
    alternatives: tuple[str, ...], body_lines: list[str], *, exact: bool = False
) -> int | None:
    matcher = _occurs_exact if exact else _occurs
    for index, line in enumerate(body_lines):
        if line.startswith("#"):
            continue
        if any(matcher(part, line) for part in alternatives):
            return index
    return None


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
                first_index = _first_occurrence(alternatives, self.body_lines)
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


class PaperFirstUseFormRegressionTests(unittest.TestCase):
    FIXTURE = REPO / "tests" / "fixtures" / "paper_first_use_pre_cure.md"

    def test_number_possessive_and_compound_forms_are_uses(self) -> None:
        examples = {
            "member": ("member", "members", "member's", "members'", "member-local"),
            "entry check": ("entry checks", "entry-check", "entry-checks'"),
            "calibration policy": (
                "calibration policies",
                "calibration policies'",
                "calibration-policy",
            ),
            "first-record endpoint": ("first record endpoints", "first-record endpoint's"),
        }
        for term, forms in examples.items():
            for form in forms:
                with self.subTest(term=term, form=form):
                    self.assertTrue(_occurs(term, f"The {form} appears here."))

    def test_frozen_pre_cure_fixture_exposes_all_24_defects(self) -> None:
        text = self.FIXTURE.read_text(encoding="utf-8")
        rows, raw_body_lines = _parse_ledger(text)
        body_lines = _strip_comments_preserving_lines(
            "\n".join(raw_body_lines)
        ).splitlines()
        self.assertEqual(len(rows), 24)

        enhanced_mismatches: list[str] = []
        for row in rows:
            alternatives = _alternatives(row.term)
            old_index = _first_occurrence(alternatives, body_lines, exact=True)
            new_index = _first_occurrence(alternatives, body_lines)
            self.assertIsNotNone(old_index, row.term)
            self.assertIsNotNone(new_index, row.term)
            assert old_index is not None and new_index is not None
            self.assertEqual(_section_for_line(body_lines, old_index), row.home)
            actual_home = _section_for_line(body_lines, new_index)
            if actual_home != row.home:
                enhanced_mismatches.append(row.term)

        self.assertEqual(
            enhanced_mismatches,
            [row.term for row in rows],
            "the inflection-aware locator must expose every frozen pre-cure row",
        )


if __name__ == "__main__":
    unittest.main()
