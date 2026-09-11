"""Defect-shaped regressions for the epoch-equivalence desk check.

Seat S9. Every fixture is a SYNTHETIC ledger built with the real reservation
API (`tests.fixtures.epoch_bootstrap.build`), so the tool under test reads real
receipts, real custody hashes and real primary bytes; nothing about the machine
is mocked, and no real ledger, config or capture is touched.

The two comparators are READ from the validator's registered generation row,
never typed: a test that restated them would keep passing after the registry
moved, which is the one failure a guard on those numbers exists to prevent.
"""

from __future__ import annotations

from contextlib import redirect_stdout
from decimal import Decimal
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.calibration_bracketing import (
    _D102_GENERATION_DERIVATIONS,
    ACTIVE_ACCEPTANCE_ID,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    acceptance_generation_operatives,
)
from joulewise.calibration_ledger import SESSION_KIND_BRACKET
from scripts import epoch_equivalence_check as checker
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger


SESSION = "derivation-night-1"
# The envelope in force, read from the registry the tool itself consults.
OPERATIVES = acceptance_generation_operatives(ACTIVE_ACCEPTANCE_ID)
LEVEL_SCREEN = Decimal(OPERATIVES["preflight_level_screen_s"])
BRACKET_SCREEN = Decimal(OPERATIVES["bracket_screen_s"])
# One unit in the last place OF THE LEVEL SCREEN'S OWN LEXEME -- derived from
# the stored string's exponent, so the boundary test moves with the registry
# instead of asserting against a hand-copied number of decimal places.
LEVEL_ULP = Decimal(1).scaleb(Decimal(OPERATIVES["preflight_level_screen_s"]).as_tuple().exponent)


def _lexeme(value: Decimal) -> str:
    """A plain decimal lexeme: the fixture writes it into JSON verbatim."""

    text = format(value, "f")
    return text


def _tight_grid(count: int, top: Decimal, step: Decimal) -> list[str]:
    """`count` ascending lexemes ending at `top`, spaced by `step`."""

    return [_lexeme(top - step * (count - 1 - index)) for index in range(count)]


class EpochEquivalenceCheckTest(unittest.TestCase):
    """Each test names the clause of issue 316's rule it defends."""

    def run_check(self, fixture, *extra: str, session: str = SESSION):
        """Run the tool exactly as the CLI does, returning (rc, text, record)."""

        # Outside the fixture checkout: an --out inside it would be an
        # untracked file in the tree whose head pin is being authenticated.
        out = fixture["root"].parent / (fixture["root"].name + "-record.json")
        args = checker.build_parser().parse_args(
            [
                "--session-id", session,
                "--ledger", str(fixture["ledger"]),
                "--head-pin", str(fixture["pin"]),
                "--acceptance", str(DEFAULT_ACCEPTANCE_BOUND_PATH),
                "--repo-root", str(fixture["root"]),
                "--out", str(out),
                *extra,
            ]
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = checker.main_args(args)
        text = stream.getvalue()
        record = None
        if out.exists():
            raw = out.read_text(encoding="utf-8")
            # A refusal leaves whatever was there; only a written record
            # parses, so "unchanged" and "absent" both read back as None.
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                record = None
        return code, text, record

    def build(self, tmp: str, name: str, slots, **kwargs):
        return build_derivation_ledger(Path(tmp) / name, slots, **kwargs)

    # ---- the PASS arm ---------------------------------------------------

    def test_twelve_retained_values_inside_the_envelope_pass(self) -> None:
        """Both comparisons hold, so the night is EQUIVALENT to the envelope.

        The grid sits just under the level screen and spans far less than the
        bracket screen, so neither comparison is satisfied by accident.
        """

        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "pass", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(record["m"], 12)
        self.assertIn("EPOCH_EQUIVALENCE: PASS (m=12)", text)
        self.assertEqual(record["verdict"], "PASS")
        self.assertTrue(record["level_screen_comparison"]["holds"])
        self.assertTrue(record["bracket_screen_comparison"]["holds"])
        # Every declared slot is listed, not only the retained ones.
        for index in range(1, 13):
            self.assertIn(f"  d{index:02d}: valid+resolved ", text)

    # ---- the level-screen arm of FAIL -----------------------------------

    def test_one_value_above_the_level_screen_fails(self) -> None:
        """A single capture above the absolute bound FAILS the night.

        The spread is left well inside the bracket screen, so the ONLY thing
        that can fail is the level comparison: an implementation that dropped
        the level test would report PASS here.
        """

        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        values[-1] = _lexeme(LEVEL_SCREEN + LEVEL_ULP)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "levelfail", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, checker.FAIL_EXIT)
        self.assertEqual(code, 4)
        self.assertEqual(record["verdict"], "FAIL")
        self.assertFalse(record["level_screen_comparison"]["holds"])
        self.assertTrue(record["bracket_screen_comparison"]["holds"])
        self.assertIn("LEVEL screen:", text)
        self.assertIn("VIOLATED", text)
        self.assertIn("EPOCH_EQUIVALENCE: FAIL (m=12)", text)

    # ---- the bracket-screen arm of FAIL ---------------------------------

    def test_range_above_the_bracket_screen_fails_with_every_value_inside(self) -> None:
        """The night's SPREAD is the second, independent test.

        Every value is at or below the level screen, so a build that tested
        only the level screen would report PASS on a night whose scatter is
        wider than the whole envelope it is being compared against.
        """

        top = LEVEL_SCREEN - Decimal("0.00005")
        # Eleven steps spanning slightly more than the bracket screen.
        step = (BRACKET_SCREEN + Decimal("0.00011")) / 11
        values = _tight_grid(12, top, step)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "bracketfail", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, checker.FAIL_EXIT)
        self.assertEqual(record["verdict"], "FAIL")
        self.assertTrue(record["level_screen_comparison"]["holds"])
        self.assertFalse(record["bracket_screen_comparison"]["holds"])
        self.assertGreater(Decimal(record["range_s"]), BRACKET_SCREEN)
        self.assertLessEqual(Decimal(record["maximum_s"]), LEVEL_SCREEN)
        self.assertIn("BRACKET screen:", text)

    # ---- the m < 6 arm --------------------------------------------------

    def test_five_retained_values_are_inconclusive_even_though_all_pass(self) -> None:
        """Too few values to judge a spread, whatever the values say.

        INCONCLUSIVE is NOT a failure: the exit code is distinct from FAIL and
        from the refusal code, and no comparison is reported at all.
        """

        values = _tight_grid(5, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(
                tmp, "m5",
                [Slot(v) for v in values] + [Slot(values[0])] * 7,
                fill_slots=5, abort_reason="window_exhausted",
            )
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, checker.INCONCLUSIVE_EXIT)
        self.assertEqual(code, 5)
        self.assertNotEqual(code, checker.FAIL_EXIT)
        self.assertNotEqual(code, checker.REFUSAL_EXIT)
        self.assertEqual(record["m"], 5)
        self.assertEqual(record["verdict"], "INCONCLUSIVE")
        self.assertIsNone(record["level_screen_comparison"])
        self.assertIsNone(record["bracket_screen_comparison"])
        self.assertIsNone(record["range_s"])
        self.assertIn("EPOCH_EQUIVALENCE: INCONCLUSIVE (m=5)", text)

    # ---- what m counts --------------------------------------------------

    def test_m_counts_only_valid_and_resolved_rows_and_lists_the_rest(self) -> None:
        """Retention turns on TWO facts, and each one is witnessed here.

        An `ordinary-invalid` row is excluded by its disposition; a `valid` row
        whose anchor-v3 replay refused with the registered
        `affine_clock_fit_empty` mechanism is excluded by its replay outcome.
        Both are LISTED, because a night's record that silently dropped rows
        could not be audited against the chain log.
        """

        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        slots = [Slot(v) for v in values]
        slots[2] = Slot(values[2], disposition="ordinary-invalid")
        slots[7] = Slot(values[7], unresolved_detail="affine_clock_fit_empty")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "mixed", slots)
            code, text, record = self.run_check(fixture)
        self.assertEqual(record["m"], 10)
        self.assertEqual(code, 0)
        self.assertIn("  d03: ordinary-invalid", text)
        self.assertIn("  d08: valid+unresolved affine_clock_fit_empty", text)
        self.assertEqual(len(record["retained"]), 10)
        self.assertNotIn("d03", [row["slot"] for row in record["retained"]])
        self.assertNotIn("d08", [row["slot"] for row in record["retained"]])
        # The excluded rows contribute no value to either statistic.
        self.assertNotEqual(record["maximum_s"], values[7])

    # ---- terminal states: aborted counts its finalized slots ------------

    def test_an_aborted_window_exhausted_night_is_evaluated(self) -> None:
        """`window_exhausted` is the planned early close, not a broken night.

        Its finalized slots are captures and are judged; its unused slots are
        named as unused rather than being confused with a refused slot.
        """

        values = _tight_grid(7, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(
                tmp, "aborted",
                [Slot(v) for v in values] + [Slot(values[0])] * 5,
                fill_slots=7, abort_reason="window_exhausted",
            )
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(record["m"], 7)
        self.assertEqual(record["session"]["state"], "aborted")
        self.assertIn("EPOCH_EQUIVALENCE: PASS (m=7)", text)
        self.assertIn("  d08: unused (window_exhausted)", text)
        self.assertIn("  d12: unused (window_exhausted)", text)
        self.assertEqual(len(record["slot_outcomes"]), 12)

    # ---- refusals: the tool will not judge ------------------------------

    def test_an_open_session_refuses_and_writes_nothing(self) -> None:
        """The rule applies AFTER the night closes; mid-campaign it refuses."""

        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "open", [Slot(v) for v in values], fill_slots=6)
            code, text, record = self.run_check(fixture)
            self.assertFalse(
                (fixture["root"].parent / (fixture["root"].name + "-record.json")).exists()
            )
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertEqual(code, 3)
        self.assertIsNone(record)
        self.assertIn("REFUSED:", text)
        self.assertIn("not terminal", text)

    def test_a_bracket_kind_session_refuses(self) -> None:
        """A bracket session is a measurement window's pair, not a night."""

        values = _tight_grid(2, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(
                tmp, "bracketkind", [Slot(v) for v in values],
                session_kind=SESSION_KIND_BRACKET,
            )
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIsNone(record)
        self.assertIn("not 'derivation'", text)

    def test_an_absent_session_refuses(self) -> None:
        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "absent", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture, session="no-such-night")
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIsNone(record)
        self.assertIn("is not in the ledger", text)

    def test_artifact_and_registry_disagreement_refuses(self) -> None:
        """Two sources for one operative, and they must agree.

        End to end, a rewritten registry row is refused before any verdict:
        the production loader authenticates the artifact AGAINST the registry,
        so the crosswire never reaches a comparison at all. That is the outer
        guard, and it is asserted here with the registry actually rewritten.
        """

        row = dict(_D102_GENERATION_DERIVATIONS[ACTIVE_ACCEPTANCE_ID])
        for field in ("preflight_level_screen_s", "bracket_screen_s"):
            operatives = dict(row["operatives"])
            operatives[field] = _lexeme(Decimal(operatives[field]) + Decimal("0.001"))
            crosswired = {**row, "operatives": operatives}
            with self.subTest(field=field):
                with mock.patch.dict(
                    _D102_GENERATION_DERIVATIONS,
                    {ACTIVE_ACCEPTANCE_ID: crosswired},
                ):
                    stream = io.StringIO()
                    with redirect_stdout(stream):
                        code = checker.main(
                            ["--print-envelope-only",
                             "--acceptance", str(DEFAULT_ACCEPTANCE_BOUND_PATH)]
                        )
                self.assertEqual(code, checker.REFUSAL_EXIT)
                self.assertIn("REFUSED:", stream.getvalue())
                self.assertNotIn("OPERATIVE level screen", stream.getvalue())

    def test_an_operative_the_loader_does_not_police_still_refuses(self) -> None:
        """The INNER guard, with the outer one held open.

        `load_calibration_acceptance_bound` is replaced by a stub returning a
        well-formed acceptance whose ratified operatives disagree with the
        registry, which is the state an outer guard that stopped covering one
        field would produce. Nothing about the machine is mocked -- only the
        byte loader, so that this tool's own field-by-field comparison is what
        is under test. Each of the three cross-checked operatives is witnessed
        separately: a loop that dropped one would pass the other two.
        """

        authentic = checker.load_calibration_acceptance_bound(
            DEFAULT_ACCEPTANCE_BOUND_PATH
        )
        for field in checker.CROSSCHECKED_OPERATIVES:
            ratified = dict(authentic["decimal_derivation"]["ratified_operatives"])
            ratified[field] = _lexeme(Decimal(ratified[field]) + Decimal("0.001"))
            derivation = {
                **authentic["decimal_derivation"],
                "ratified_operatives": ratified,
            }
            forged = {**authentic, "decimal_derivation": derivation}
            with self.subTest(field=field):
                with mock.patch.object(
                    checker, "load_calibration_acceptance_bound",
                    return_value=forged,
                ):
                    with self.assertRaises(checker.EquivalenceRefusal) as caught:
                        checker.reference_envelope(DEFAULT_ACCEPTANCE_BOUND_PATH)
                self.assertIn("disagree", caught.exception.reason)
                self.assertIn(field, caught.exception.reason)

    def test_a_disagreeing_corpus_size_refuses(self) -> None:
        """n is stated twice too, and the two statements must be the same n."""

        authentic = checker.load_calibration_acceptance_bound(
            DEFAULT_ACCEPTANCE_BOUND_PATH
        )
        corpus = {**authentic["derivation_corpus"],
                  "n": authentic["derivation_corpus"]["n"] + 1}
        forged = {**authentic, "derivation_corpus": corpus}
        with mock.patch.object(
            checker, "load_calibration_acceptance_bound", return_value=forged
        ):
            with self.assertRaises(checker.EquivalenceRefusal) as caught:
                checker.reference_envelope(DEFAULT_ACCEPTANCE_BOUND_PATH)
        self.assertIn("corpus n", caught.exception.reason)

    def test_an_out_path_under_configs_calibration_refuses(self) -> None:
        """This tool never writes where an acceptance lives, by any route."""

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "configs" / "calibration" / "record.json"
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = checker.main(
                    ["--session-id", SESSION, "--out", str(target)]
                )
            self.assertFalse(target.exists())
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIn("never writes into an acceptance directory", stream.getvalue())

    def test_another_authenticated_generation_is_refused_as_the_reference(self) -> None:
        """Issue 316 names r6; the n19 predecessor authenticates but is not it.

        Refuter 157 F1: twelve values of 0.033 FAIL against r6's level screen
        and PASS against the n19 predecessor's. Pointing `--acceptance` at any
        other registered generation must refuse before a comparison exists.
        """

        predecessor = (
            DEFAULT_ACCEPTANCE_BOUND_PATH.parent / "calibration_acceptance_d079_v2.json"
        )
        self.assertTrue(predecessor.exists())
        values = ["0.033"] * 12
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "n19", [Slot(v) for v in values])
            code, text, record = self.run_check(
                fixture, "--acceptance", str(predecessor)
            )
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIsNone(record)
        self.assertIn("issue 316 fixes the reference envelope", text)
        self.assertIn(checker.REQUIRED_ACCEPTANCE_ID, text)
        self.assertNotIn("EPOCH_EQUIVALENCE:", text)

    def test_an_out_path_under_configs_calibration_refuses_case_folded(self) -> None:
        """Refuter 157 F2: CONFIGS/CALIBRATION is the same directory on macOS."""

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "CONFIGS" / "CALIBRATION" / "record.json"
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = checker.main(
                    ["--session-id", SESSION, "--out", str(target)]
                )
            self.assertFalse(target.exists())
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIn("never writes into an acceptance directory", stream.getvalue())

    def test_an_out_path_under_a_unicode_case_alias_refuses(self) -> None:
        """Delta 158: `configſ` (LONG S) folds to `configs`; lower() missed it."""

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config\u017f" / "calibration" / "record.json"
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = checker.main(
                    ["--session-id", SESSION, "--out", str(target)]
                )
            self.assertFalse(target.exists())
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIn("never writes into an acceptance directory", stream.getvalue())

    def test_an_out_path_that_is_the_acceptance_directory_by_identity_refuses(self) -> None:
        """Whatever the spelling, a parent that IS configs/calibration refuses."""

        target = checker.REPO_ROOT / "configs" / "calibration" / "record.json"
        with mock.patch.object(checker, "FORBIDDEN_OUT_PARTS", ("never", "matches")):
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = checker.main(
                    ["--session-id", SESSION, "--out", str(target)]
                )
        self.assertFalse(target.exists())
        self.assertEqual(code, checker.REFUSAL_EXIT)
        self.assertIn("never writes into an acceptance directory", stream.getvalue())

    def test_exactly_six_retained_values_are_judged_not_inconclusive(self) -> None:
        """m = 6 is the first m the rule judges: the boundary is inclusive."""

        values = _tight_grid(6, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(
                tmp, "m6",
                [Slot(v) for v in values] + [Slot(values[0])] * 6,
                fill_slots=6, abort_reason="window_exhausted",
            )
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(record["m"], 6)
        self.assertEqual(record["verdict"], "PASS")
        self.assertIsNotNone(record["bracket_screen_comparison"])
        self.assertIn("EPOCH_EQUIVALENCE: PASS (m=6)", text)

    def test_a_range_exactly_equal_to_the_bracket_screen_passes(self) -> None:
        """`<=` on the spread too: a night whose spread IS the screen passes."""

        top = LEVEL_SCREEN - Decimal("0.00005")
        bottom = top - BRACKET_SCREEN
        values = [_lexeme(bottom)] + _tight_grid(11, top, Decimal("0.000001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "rangeeq", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(Decimal(record["range_s"]), BRACKET_SCREEN)
        self.assertTrue(record["bracket_screen_comparison"]["holds"])
        self.assertEqual(record["verdict"], "PASS")

    def test_an_existing_out_is_not_overwritten_without_force(self) -> None:
        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "exists", [Slot(v) for v in values])
            out = fixture["root"].parent / (fixture["root"].name + "-record.json")
            out.write_text("prior\n", encoding="utf-8")
            code, text, _record = self.run_check(fixture)
            self.assertEqual(out.read_text(encoding="utf-8"), "prior\n")
            self.assertEqual(code, checker.REFUSAL_EXIT)
            self.assertIn("pass --force", text)
            forced, _text, record = self.run_check(fixture, "--force")
        self.assertEqual(forced, 0)
        self.assertEqual(record["verdict"], "PASS")

    # ---- the record: printed and stored agree ---------------------------

    def test_the_json_record_equals_the_printed_values(self) -> None:
        """A record on disk that disagreed with the record on screen would
        make the addendum's citation unverifiable, so every number printed is
        asserted to appear in the JSON, and the verdict line is rebuilt from it.
        """

        values = _tight_grid(12, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "record", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        for key in ("maximum_s", "minimum_s", "range_s"):
            self.assertIn(record[key], text)
        self.assertIn(
            f"EPOCH_EQUIVALENCE: {record['verdict']} (m={record['m']})", text
        )
        envelope = record["reference_envelope"]
        for key in (
            "raw_corpus_maximum_s", "raw_corpus_range_s", "level_screen_s",
            "bracket_screen_s", "maximum_budgetable_drift_s",
        ):
            self.assertIn(envelope[key], text)
        self.assertEqual(envelope["acceptance_id"], ACTIVE_ACCEPTANCE_ID)
        self.assertEqual(envelope["level_screen_s"], OPERATIVES["preflight_level_screen_s"])
        self.assertEqual(envelope["bracket_screen_s"], OPERATIVES["bracket_screen_s"])
        # The retained lexemes are the stored ones, not a reformatting of them.
        self.assertEqual([row["b_fiducial_s"] for row in record["retained"]], values)
        self.assertEqual(record["maximum_s"], values[-1])
        self.assertEqual(record["minimum_s"], values[0])

    # ---- the boundary the comparison operator decides -------------------

    def test_a_value_exactly_on_the_level_screen_passes_and_one_ulp_above_fails(
        self,
    ) -> None:
        """The rule says `<=`, so equality is INSIDE the envelope.

        One unit in the last place of the level screen's own lexeme separates
        the two runs, which is the smallest difference the stored decimals can
        express -- and the difference a float comparison would lose.
        """

        base = _tight_grid(11, LEVEL_SCREEN - Decimal("0.0005"), Decimal("0.00001"))
        on_boundary = base + [_lexeme(LEVEL_SCREEN)]
        above = base + [_lexeme(LEVEL_SCREEN + LEVEL_ULP)]
        self.assertNotEqual(on_boundary[-1], above[-1])
        with tempfile.TemporaryDirectory() as tmp:
            equal_fixture = self.build(tmp, "eq", [Slot(v) for v in on_boundary])
            equal_code, _text, equal_record = self.run_check(equal_fixture)
            above_fixture = self.build(tmp, "above", [Slot(v) for v in above])
            above_code, _text, above_record = self.run_check(above_fixture)
        self.assertEqual(equal_code, 0)
        self.assertEqual(equal_record["verdict"], "PASS")
        self.assertEqual(
            Decimal(equal_record["maximum_s"]), LEVEL_SCREEN
        )
        self.assertEqual(above_code, checker.FAIL_EXIT)
        self.assertEqual(above_record["verdict"], "FAIL")
        self.assertFalse(above_record["level_screen_comparison"]["holds"])

    # ---- Decimal, not float ---------------------------------------------

    def test_full_precision_lexemes_survive_the_check_unrounded(self) -> None:
        """The stored lexemes carry more digits than a float can hold.

        A real capture's `b_fiducial_s` runs to seventeen significant digits --
        more than binary64 represents exactly -- so a build that took any value
        through a float would hand back a DIFFERENT number here. The grid below
        is deliberately built at that width, and the record's maximum, minimum
        and range are asserted against the exact Decimal arithmetic on the
        stored strings.
        """

        top = LEVEL_SCREEN - Decimal("0.000500000000000123")
        step = Decimal("0.000010000000000007")
        values = _tight_grid(12, top, step)
        # The fixture really is wider than a float: proving it here means the
        # assertions below cannot pass by accident on short numbers.
        self.assertNotEqual(_lexeme(Decimal(repr(float(values[-1])))), values[-1])
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.build(tmp, "precision", [Slot(v) for v in values])
            code, text, record = self.run_check(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(record["maximum_s"], values[-1])
        self.assertEqual(record["minimum_s"], values[0])
        self.assertEqual(Decimal(record["range_s"]), step * 11)
        self.assertEqual(record["range_s"], _lexeme(step * 11))
        for value in values:
            self.assertIn(value, text)

    # ---- the tool's stated limits ---------------------------------------

    def test_help_says_what_the_tool_never_does_and_glosses_its_terms(self) -> None:
        """The gloss is load-bearing: a reader who mistakes this for the issuer
        would think a PASS had already continued the acceptance."""

        text = checker.build_parser().format_help()
        for phrase in (
            "DERIVATION NIGHT", "RETAINED", "REFERENCE ENVELOPE",
            "LEVEL SCREEN", "BRACKET SCREEN", "EPOCH EQUIVALENCE",
        ):
            self.assertIn(phrase, text)
        for phrase in (
            "NEVER issues", "never writes an addendum",
            "never writes under configs/calibration",
        ):
            self.assertIn(phrase, text)

    def test_print_envelope_only_needs_no_session_and_writes_nothing(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = checker.main(["--print-envelope-only"])
        text = stream.getvalue()
        self.assertEqual(code, 0)
        self.assertIn(OPERATIVES["preflight_level_screen_s"], text)
        self.assertIn(OPERATIVES["bracket_screen_s"], text)
        self.assertNotIn("record written", text)


if __name__ == "__main__":
    unittest.main()
