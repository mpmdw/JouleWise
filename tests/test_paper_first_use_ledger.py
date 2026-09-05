from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT = REPO / "docs" / "paper" / "draft-v2-skeleton.md"
DRAFT = Path(
    os.environ.get(
        "PAPER_FIRST_USE_DRAFT",
        DEFAULT_DRAFT,
    )
)
LEXICON = REPO / "docs" / "paper" / "round7" / "built-terms-lexicon.md"
REAL_PRE_CURE_FIXTURE = REPO / "tests" / "fixtures" / "paper_first_use_pre_cure.md"
REAL_PRE_CURE_SHA256 = "04e78ec457bb4005ad4e135bad8894f29b4f6c0b45325b7c38874d5c1745ce89"
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
COMPOUND_JOIN = r"(?:\s+|[-\u2010\u2011\u2012\u2013])"

# These are deliberately row-specific. A general stemmer makes ordinary words
# collide; the ledger instead names only the derivations that mean the same
# technical thing in this paper.
EXTRA_ALTERNATIVES: dict[str, tuple[str, ...]] = {
    "admitted": ("admission", "admit", "admits"),
    "frozen": ("freeze", "freezes", "freezing"),
    "idle-subtracted energy": ("idle-subtracted request energy",),
    "not resolvable": ("resolvable",),
}

# Each row here was changed by the first-use cure. The required defining words
# must occur no later than the paragraph or table row containing the term's
# first use. This binds the definition itself, not merely its section heading.
GLOSS_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "powermetrics": ("macOS powermetrics is the power sampler used here",),
    "Apple M3 Max / 128 GB unified memory": (
        "measures one Apple M3 Max",
        "128 GB of unified memory",
    ),
    "detection floor": (
        "registered operational resolution guard for assigned-energy differences",
        "the detection floor in the advisor's terminology",
        "the artifacts call the final gate value after those safeguards the cell floor",
    ),
    r"\(U_{\mathrm{point}}\) / \(U_{\mathrm{corner}}\)": (
        "component bound calculated at the recorded edges",
        "largest result retained",
        "this replay uses a different numerator",
    ),
    "A/B/B/A block": ("same-model null A/B/B/A blocks, with A = B",),
    "energy-allowance sign": (
        "says which direction a nonnegative block-level allowance moves assigned energy",
    ),
    r"\(R_{cm}\)": (
        "shared-energy-sign/local-corner sensitivity diagnostic",
        "does not globally replay one physical common-time shift",
        "has no proven conservatism for common-time motion",
    ),
    "reasoning disabled": ("optional chain-of-thought output is switched off",),
    "declared machine state / instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance file": (
        "hardware and operating conditions recorded before collection",
        "list of its calibration artifacts and their SHA-256 fingerprints",
        "file that names the reserved collection slots",
        "pins in the calibration ledger's session record",
        "expected digest from the in-code ISSUED_ACCEPTANCE_REGISTRY",
    ),
    "mint": ("the analysis run that issues the paper's fixed results",),
    "frozen": ("fixed and fingerprinted before collection",),
    "signal, fit, range, trace-coverage, and completeness checks / shared search-work limits": (
        "signal rises far enough above resting power",
        "fitted pulse explains the trace better than a no-pulse model",
        "trace coverage extends through the fixed margin on both sides",
        "cap both the number of search rectangles evaluated and the elapsed search time",
    ),
    "first-record endpoint": ("wall-clock time assigned to the end of the first native power record",),
    "calibration-acceptance rule": ("pre-collection rule that decides whether those two captures may bracket one window",),
    "entry check": ("pass/fail checks on recorded machine state that a stage must satisfy before its first run is measured",),
    "admitted": ("allowed to begin its measured runs",),
    "reference runs": ("repeated at the window's opening, midpoint when present, and close to track drift",),
    "gross energy / idle-subtracted energy": (
        "processor energy recorded during a run",
        "mean idle power multiplied by run duration",
    ),
    "null-test blocks": ("blocks in which both conditions are the same",),
    "package power": ("summed CPU, GPU, and neural-engine power",),
    "workload-response slope": ("fitted change in energy per output token",),
    "workload level": ("one output-token count fixed before collection",),
    "workload magnitude": ("one target size fixed in the identical-condition ladder",),
    "per-token conversion": ("fitted joules per output token",),
    "sampling flags / cadence ratio": (
        "sampling cadence cannot be recorded or does not stay above a fixed multiple of the phase rate",
        "SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0",
        "REQUEST_WINDOW_CADENCE_RATIO_MIN = 4.0",
    ),
    "retired calculation": (
        "equal-rate clock anchor",
        "point-only value was multiplied by a fixed factor to allow for limited repetition",
        "current calculation instead uses the corner-to-point ratios",
    ),
    r"small-sample multiplier / \(g(n)\)": ("factor that widens a result to allow for limited repetition",),
    "close-out artifact": ("checks every required ratio",),
    "deterministic-bound kinds / interpolation edge": (
        "for native interval-average records, the reducer integrates constant reported power over the overlap duration",
        "its interpolation-bound term is zero",
        "timing uncertainty enters through separately recomputed boundary envelopes",
    ),
    "Figure 3": (
        "separates evidence refusal from the two claim gates",
        "four possible outcomes are refusal, not resolvable, direction unresolved, and a directional claim",
    ),
    "custody": ("each named input's fingerprint still matches its recorded bytes",),
    "measured contrast": ("point estimate and composed uncertainty interval",),
}

LEXICON_REQUIRED_TERMS = (
    "| powermetrics | §1 |",
    "| mint | §2 |",
    "| declared machine state / instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance file | §2 |",
    "| entry check | §2 |",
    "| admitted | §2 |",
    "| workload level / workload magnitude / per-token conversion | §3 |",
    "| cadence ratio / sampling flags | §3 |",
    "| interpolation edge / deterministic-bound kinds | §4 |",
    "| measured contrast / custody / Figure 3 | §4 |",
)


@dataclass(frozen=True)
class LedgerRow:
    term: str
    home: str
    status: str
    disposition: str


@dataclass(frozen=True)
class SearchBlock:
    text: str
    line_map: tuple[int, ...]


@dataclass(frozen=True)
class Occurrence:
    block_index: int
    line_index: int
    character_index: int


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
    base = tuple(_display_text(part) for part in term.split(" / "))
    extras = tuple(
        extra
        for alternative in base
        for extra in EXTRA_ALTERNATIVES.get(alternative.casefold(), ())
    )
    return base + extras


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


def _search_blocks(body_lines: list[str]) -> list[SearchBlock]:
    """Join wrapped Markdown paragraphs and retain a source-line map."""

    blocks: list[SearchBlock] = []
    text_parts: list[str] = []
    line_map: list[int] = []
    in_fence = False

    def flush() -> None:
        if text_parts:
            blocks.append(SearchBlock("".join(text_parts), tuple(line_map)))
            text_parts.clear()
            line_map.clear()

    def append_text(value: str, line_index: int) -> None:
        text_parts.append(value)
        line_map.extend([line_index] * len(value))

    for line_index, line in enumerate(body_lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if not stripped or line.startswith("#"):
            flush()
            continue
        if in_fence or line.lstrip().startswith("|"):
            flush()
            blocks.append(SearchBlock(line, tuple([line_index] * len(line))))
            continue
        if text_parts:
            joiner = "" if text_parts[-1].endswith(("-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014")) else " "
            append_text(joiner, line_index)
        append_text(stripped, line_index)
    flush()
    return blocks


def _first_match(
    alternatives: tuple[str, ...], body_lines: list[str], *, exact: bool = False
) -> Occurrence | None:
    matcher = _occurs_exact if exact else _occurs
    if exact:
        blocks = [
            SearchBlock(line, tuple([index] * len(line)))
            for index, line in enumerate(body_lines)
            if not line.startswith("#")
        ]
    else:
        blocks = _search_blocks(body_lines)

    for block_index, block in enumerate(blocks):
        matches = [
            match
            for part in alternatives
            if (match := (_alternative_pattern(part) if not exact else re.compile(
                rf"(?<!\w){re.escape(part)}(?!\w)", re.IGNORECASE
            )).search(block.text))
        ]
        if not matches:
            continue
        first = min(matches, key=lambda match: match.start())
        return Occurrence(
            block_index=block_index,
            line_index=block.line_map[first.start()],
            character_index=first.start(),
        )
    return None


def _first_occurrence(
    alternatives: tuple[str, ...], body_lines: list[str], *, exact: bool = False
) -> int | None:
    match = _first_match(alternatives, body_lines, exact=exact)
    return match.line_index if match else None


def _plain_for_gloss_check(text: str) -> str:
    return text.replace("**", "").replace("`", "").casefold()


def _gloss_failures(rows: list[LedgerRow], body_lines: list[str]) -> list[str]:
    rows_by_term = {row.term: row for row in rows}
    blocks = _search_blocks(body_lines)
    failures: list[str] = []
    for row_term, required_phrases in GLOSS_REQUIREMENTS.items():
        row = rows_by_term.get(row_term)
        if row is None:
            failures.append(f"{row_term}: required ledger row is missing")
            continue
        occurrence = _first_match(_alternatives(row.term), body_lines)
        if occurrence is None:
            failures.append(f"{row_term}: term is absent")
            continue
        block = _plain_for_gloss_check(blocks[occurrence.block_index].text)
        missing = [
            phrase for phrase in required_phrases if phrase.casefold() not in block
        ]
        if missing:
            failures.append(
                f"{row_term}: first-use paragraph (line {occurrence.line_index + 1}) "
                f"is missing defining words {missing}"
            )
    return failures


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

    def test_required_gloss_is_present_by_first_use_paragraph(self) -> None:
        self.assertEqual(
            _gloss_failures(self.rows, self.body_lines),
            [],
            "required first-use glosses are absent or arrive too late",
        )

    def test_successor_lexicon_is_regeneration_protected(self) -> None:
        text = LEXICON.read_text(encoding="utf-8")
        self.assertIn("binds this hand-maintained successor table", text)
        missing = [term for term in LEXICON_REQUIRED_TERMS if term not in text]
        self.assertEqual(missing, [], "successor lexicon entries were discarded")

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
    FIXTURE = REAL_PRE_CURE_FIXTURE

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

    def test_wrapped_derivational_dash_and_modifier_forms_are_uses(self) -> None:
        wrapped = [
            "## Earlier",
            "The entry",
            "check is applied before measurement.",
            "",
            "## Later",
        ]
        self.assertEqual(_first_occurrence(("entry check",), wrapped), 1)

        hyphen_wrapped = [
            "## Earlier",
            "The close-",
            "out artifact is checked.",
            "",
            "## Later",
        ]
        self.assertEqual(_first_occurrence(("close-out artifact",), hyphen_wrapped), 1)

        row_cases = {
            "admitted": ("Admission is required.", "The bundle was admitted."),
            "frozen": ("We freeze the plan.",),
            "not resolvable": ("The effect is resolvable.",),
            "idle-subtracted energy": ("Idle-subtracted request energy is retained.",),
            "close-out artifact": ("The close–out artifact is checked.",),
        }
        for term, examples in row_cases.items():
            alternatives = _alternatives(term)
            for example in examples:
                with self.subTest(term=term, example=example):
                    self.assertIsNotNone(_first_occurrence(alternatives, [example]))

    def test_fixture_is_exact_main_pre_cure_draft(self) -> None:
        digest = hashlib.sha256(self.FIXTURE.read_bytes()).hexdigest()
        self.assertEqual(digest, REAL_PRE_CURE_SHA256)

    def test_real_pre_cure_fixture_violates_hardened_ledger(self) -> None:
        text = self.FIXTURE.read_text(encoding="utf-8")
        rows, raw_body_lines = _parse_ledger(text)
        body_lines = _strip_comments_preserving_lines(
            "\n".join(raw_body_lines)
        ).splitlines()
        failures = _gloss_failures(rows, body_lines)
        joined = "\n".join(failures)
        self.assertIn("package power", joined)
        self.assertIn("retired calculation", joined)
        self.assertIn("entry check", joined)
        self.assertGreaterEqual(len(failures), 8)

    def test_gloss_checks_bite_when_cures_are_removed(self) -> None:
        text = DEFAULT_DRAFT.read_text(encoding="utf-8")
        mutations = {
            "package power": (
                "its duration times its largest recorded **package power**—the summed CPU, GPU,\n"
                "and neural-engine power—bounds what may be missing.",
                "its duration times its largest recorded package power bounds what may be missing.",
            ),
            "retired calculation": (
                "That calculation used an equal-rate clock anchor and a yes/no rule that\n"
                "called a cell attribution-limited when its exact moved-edge limit\n"
                "exceeded its point-only value after that point-only value was multiplied by a\n"
                "fixed factor to allow for limited repetition. The\n"
                "current calculation instead uses the corner-to-point ratios in Section 4.\n",
                "",
            ),
            r"\(U_{\mathrm{point}}\) / \(U_{\mathrm{corner}}\)": (
                "lower-or-upper edge choice for that component is evaluated jointly and the\n"
                "largest result retained.",
                "lower-or-upper edge choice for that component is evaluated jointly.",
            ),
        }
        for term, (cured, reverted) in mutations.items():
            with self.subTest(term=term):
                self.assertIn(cured, text)
                mutated = text.replace(cured, reverted, 1)
                rows, raw_body_lines = _parse_ledger(mutated)
                body_lines = _strip_comments_preserving_lines(
                    "\n".join(raw_body_lines)
                ).splitlines()
                failures = "\n".join(_gloss_failures(rows, body_lines))
                self.assertIn(term, failures)


if __name__ == "__main__":
    unittest.main()
