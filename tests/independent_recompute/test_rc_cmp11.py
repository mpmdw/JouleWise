"""RC-CMP-11: the fix round inside the RC-CMP-10 design (review/2026-10-30-rc-cmp10-opus-rev and
review/2026-10-30-rc-cmp10-fable-rev, both ACCEPT_WITH_FIXES).

F1: bit-identical numbers and thresholds on both sides decide a test (a wrong relation word on unchanged values
refuses). F2: the registered p42 cell's code is the producer's own. F3: the two by-construction True literals are
pinned. F4: the direction word is "none" only for a printed None. F5: an undetermined trigger is a member of the
engine's trigger vocabulary, printed once.

Counterfactuals are in place: the check this round adds is switched off (mock) and the same case passes, as it did at
1affc4208. Fixture words come from the producers (producer_fixtures).
"""
import ast
from pathlib import Path
import re
from unittest import mock

from . import producer_fixtures, test_rc_cmp10
from .test_comparator import DECODE, PREFILL, SHA, cmp
from .test_input_gate import CODED
from .test_rc_cmp7 import find
from .test_rc_cmp8 import REPORTED, SENSITIVITY, contrast_rows
from .test_rc_cmp9 import function, producer
from .test_rc_cmp10 import Case, set_loo
from .test_review_fixes import DISCLOSURE

FLOOR = "d117-qwen3-1p7b-decode-floor-v5"
BLOCK = test_rc_cmp10.WithinBarTests.BLOCK
ATOM = cmp.Comparison.atom


def atom_before(self, name, family, key, l9, ours, threshold, test, l9_threshold=cmp.MISSING):
    """The comparator at 1affc4208: a test inside its bar on either side is undetermined, even bit-identical."""
    found = ATOM(self, name, family, key, l9, ours, threshold, test, l9_threshold)
    l9_threshold = threshold if l9_threshold is cmp.MISSING else l9_threshold
    if all(cmp.finite(v) for v in (l9, ours, threshold, l9_threshold)):
        bar = self.bar(family, key, l9)
        found["within"] = abs(l9 - l9_threshold) <= bar or abs(ours - threshold) <= bar
    return found


def source(case, path):
    """A producer source on origin/main, read as text (skipped where origin/main is absent)."""
    text = producer(path)
    if text is None:
        case.skipTest("origin/main is not available in this clone")
    return text


def set_word(case, section, match, word, value):
    """The word set in every printed copy: L9's record, the disclosure's copy and its block line."""
    line = {"reported_cells": "sensitivity_reported", "floor_cells": "sensitivity_floor",
            "contrasts": "sensitivity_contrast"}[section]
    for record in (case.files[SENSITIVITY], case.files[DISCLOSURE]["sensitivity"]):
        for row in record[section]:
            if match(row):
                row[word] = value
    for row in case.files[DISCLOSURE]["block_lines"]:
        if row["line"] == line and match(row["record"]):
            row["record"][word] = value


def set_widened(case, pack, value):
    for record in (case.files[SENSITIVITY], case.files[DISCLOSURE]["sensitivity"]):
        record["windows"][pack]["widened"] = value
    for row in case.files[DISCLOSURE]["block_lines"]:
        if row["line"] == "sensitivity_window" and row["pack"] == pack:
            row["widened"] = value


def floor(row):
    return row.get("cell_id") == FLOOR


def computed(row):
    return row.get("status") == "computed"


def decode(row):
    return row.get("contrast_id") == DECODE


# Opus E1-E4, E6-E8: each word printed wrong in every copy while the values it reads are equal on both sides.
WRONG_WORDS = (
    ("E1 floor equals_primary False", False, lambda c: set_word(c, "floor_cells", floor, "equals_primary", False)),
    ("E2 reported equals_primary False", False,
     lambda c: set_word(c, "reported_cells", computed, "equals_primary", False)),
    ("E3 floor not_below_primary False (0 >= 0)", False,
     lambda c: set_word(c, "floor_cells", floor, "not_below_primary", False)),
    ("E4 contrast not_below_primary False", False,
     lambda c: set_word(c, "contrasts", decode, "not_below_primary", False)),
    ("E6 widened True at b_sens == b_op (strict)", False, lambda c: set_widened(c, "alpha", True)),
    ("E7 floor equals_primary not a boolean", False,
     lambda c: set_word(c, "floor_cells", floor, "equals_primary", "banana")),
    ("E8 widened window, unchanged reported equals_primary False", True,
     lambda c: set_word(c, "reported_cells", lambda r: computed(r) and r.get("cell_id") != REPORTED,
                        "equals_primary", False)),
)


class ExactEqualityTests(Case):
    """F1: bit-identical numbers decide the test; strict relations are false at equality, non-strict true."""
    def test_wrong_words_on_identical_values_refuse(self):
        for label, widened, mutate in WRONG_WORDS:
            with self.subTest(label):
                self.base(widened)
                mutate(self)
                self.assertNotEqual(self.outcome(), 0)
                # Counterfactual (1affc4208): inside the bar, undetermined, the wrong word passed.
                with mock.patch.object(cmp.Comparison, "atom", atom_before):
                    self.assertEqual(self.outcome(), 0)

    def test_sound_windows_have_no_undetermined_relation_word(self):
        for widened in (True, False):
            with self.subTest(widened=widened):
                self.base(widened)
                code, err, out = self.exit_code(CODED)
                self.assertEqual((code, err), (0, ""))
                rows = [r for r in out["comparisons"] if r["key"].startswith("sensitivity/")
                        and r.get("reason") == "within_bar_undetermined"]
                self.assertEqual(rows, [])

    def test_strict_claim_over_equal_values_fails(self):
        # below_screen_bound reads b_op < bound (strict): at b_op == bound on both sides the word is False.
        for l9_word, expected in ((True, 1), (False, 0)):
            with self.subTest(below=l9_word):
                self.base()
                b_op = cmp.SCREEN_BOUND_S
                lines, index = find(self, "below_screen_bound")
                lines[index].update(b_op_s=b_op, below=l9_word)
                self.ours["windows"]["ALPHA"]["b_op_s"] = b_op
                self.files[f"brackets/{SHA}-alpha.json"]["evaluation"]["acceptance"]["allowance"][
                    "operative_b_fiducial_binary64_s"] = b_op
                for record in (self.files[SENSITIVITY], self.files[DISCLOSURE]["sensitivity"]):
                    record["windows"]["alpha"]["b_op_s"] = b_op
                for line in self.files[DISCLOSURE]["block_lines"]:
                    if line["line"] == "sensitivity_window" and line["pack"] == "alpha":
                        line["b_op_s"] = b_op
                self.assertEqual(self.outcome() != 0, bool(expected))
                if expected:
                    with mock.patch.object(cmp.Comparison, "atom", atom_before):
                        self.assertEqual(self.outcome(), 0)
        # widened reads b_sens > b_op (strict): at b_sens == b_op the word is False (E6 above); equals_primary and
        # not_below_primary (==, >=) are True at equality, so the producer's True passes (the sound window).

    def test_identical_b10_trigger_mismatch_refuses(self):
        # Fable fs3 C: decode loo b10 at +3.55e-15 on both sides, L9 printing no estimate_sign trigger while the
        # recompute's identical numbers raise one.
        self.base()
        set_loo(self, BLOCK, 3.55e-15, 3.55e-15, [])
        self.assertNotEqual(self.outcome(), 0)
        with mock.patch.object(cmp.Comparison, "atom", atom_before):
            self.assertEqual(self.outcome(), 0)
        # The trigger printed on both sides passes.
        self.base()
        set_loo(self, BLOCK, 3.55e-15, 3.55e-15, ["estimate_sign"])
        self.assertEqual(self.outcome(), 0)

    def test_ulp_cases_stay_undetermined(self):
        # The full-size b10 flip and Opus U1-U4 (one exactly-0 side against a 1e-16 other side).
        key = f"{DECODE}/loo/b10/influence_triggers"
        for l9, own, triggers in ((3.55e-15, -1.78e-15, ["estimate_sign"]), (3.55e-15, -1.78e-15, []),
                                  (0.0, 1e-16, []), (0.0, -1e-16, ["estimate_sign"])):
            with self.subTest(l9=l9, own=own, triggers=triggers):
                self.base()
                set_loo(self, BLOCK, l9, own, triggers)
                code, err, out = self.exit_code(CODED)
                self.assertEqual((code, err), (0, ""))
                self.assertEqual(self.row(out, key)["reason"], "within_bar_undetermined")


class P42ProducerCodeTests(Case):
    """F2: the registered p42 cell's code is the one the producer derives for it."""
    copies = test_rc_cmp10.P42CodeTests.copies

    def test_the_code_is_pinned_to_the_producer(self):
        kernel = ast.parse(source(self, "joulewise/paper_reported_energy.py"))
        project = ast.unparse(function(kernel, "_project_kept_cell"))
        self.assertIn("if row['strict_valid'] is not True or row['unit'] != unit or type(row['unit']['index']) is not "
                      f"int:\n            raise PaperReportedEnergyRefusal('{cmp.P42_REFUSAL_CODE}')", project)
        issuer = source(self, "joulewise/paper_reported_energy_issuer.py")
        self.assertIn("'strict_valid': not problems and not precheck['reasons']", issuer)
        self.assertIn("p42_precheck=True", issuer)
        self.assertEqual(producer_fixtures.p42_refusal_code(), cmp.P42_REFUSAL_CODE)
        self.assertIn(cmp.P42_REFUSAL_CODE, cmp.REPORTED_REFUSAL_CODES)

    def test_every_other_member_code_refuses(self):
        # Opus p42.out: each of the other 32 closed codes printed identically in every copy.
        for other in cmp.REPORTED_REFUSAL_CODES:
            if other == cmp.P42_REFUSAL_CODE:
                continue
            with self.subTest(other):
                self.base()
                self.copies(other)
                self.assertNotEqual(self.outcome(), 0)


class LiteralPinTests(Case):
    """F3: the two by-construction words the comparator expects True, pinned to sensitivity.py."""
    def test_by_construction_true_literals(self):
        text = source(self, "joulewise/b5_analysis/sensitivity.py")
        for word in ("mean_and_half_width_equal_primary", "bound_independent_values_equal_primary"):
            with self.subTest(word):
                self.assertRegex(text, rf'"{word}": True,')
                script = Path(cmp.__file__).read_text()
                self.assertRegex(script, rf'{word}",\n\s+[a-z]+\.get\("{word}"\), True\)')


class DirectionTests(Case):
    """F4: L9's direction is "none" only when it prints None; any other value is compared as printed."""
    def set_direction(self, value):
        for row in contrast_rows(self, PREFILL):
            row["claim_evaluation"]["direction"] = value

    def test_falsy_and_foreign_directions_refuse(self):
        self.base()
        self.set_direction(None)
        self.assertEqual(self.outcome(), 0)
        for value in (False, "", 0, [], "banana"):
            with self.subTest(value=value):
                self.base()
                self.set_direction(value)
                self.assertNotEqual(self.outcome(), 0)
        # Counterfactual (1affc4208): any falsy value read as "none".
        original = cmp.Comparison.word

        def falsy_none(c, family, key, l9, ours, atoms=(), decide=None, raw=cmp.MISSING, vocabulary=None):
            if key == f"{PREFILL}/direction" and not l9:
                l9 = "none"
            return original(c, family, key, l9, ours, atoms, decide, raw)
        for value in (False, "", 0, []):
            with self.subTest(counterfactual=value):
                self.base()
                self.set_direction(value)
                with mock.patch.object(cmp.Comparison, "word", falsy_none):
                    self.assertEqual(self.outcome(), 0)

    def test_direction_words_pinned(self):
        text = source(self, "joulewise/analysis_engine/claims.py")
        self.assertIn('direction = "positive" if numeric_estimate > 0.0 else "negative"', text)
        self.assertIn('"direction": direction,', text)
        self.assertEqual(cmp.DIRECTION_WORDS, ("positive", "negative", "none"))


class TriggerVocabularyTests(Case):
    """F5: an undetermined trigger row still requires a vocabulary word printed once."""
    def test_duplicate_and_foreign_triggers_refuse(self):
        for triggers in (["estimate_sign", "estimate_sign"], ["banana"], ["outcome"]):
            with self.subTest(triggers=triggers):
                self.base()
                set_loo(self, BLOCK, 3.55e-15, -1.78e-15, triggers)
                self.assertNotEqual(self.outcome(), 0)
        # The full-size flip with one printed trigger passes.
        self.base()
        set_loo(self, BLOCK, 3.55e-15, -1.78e-15, ["estimate_sign"])
        self.assertEqual(self.outcome(), 0)

    def test_duplicate_passed_before(self):
        # Counterfactual (1affc4208): an undetermined position row took any word in the open set, so the duplicate
        # passed.
        original = cmp.Comparison.word

        def open_word(c, family, key, l9, ours, atoms=(), decide=None, raw=cmp.MISSING, vocabulary=None):
            if re.search(r"/influence_triggers/\d+$", key) and atoms and ours is None and l9 in cmp.INFLUENCE_TRIGGERS:
                ours = l9
            return original(c, family, key, l9, ours, atoms, decide, raw, vocabulary)
        self.base()
        set_loo(self, BLOCK, 3.55e-15, -1.78e-15, ["estimate_sign", "estimate_sign"])
        self.assertNotEqual(self.outcome(), 0)
        with mock.patch.object(cmp.Comparison, "word", open_word):
            self.assertEqual(self.outcome(), 0)

    def test_trigger_vocabulary_is_the_engines(self):
        tree = ast.parse(source(self, "joulewise/analysis_engine/sensitivity.py"))
        names = [call.args[0] for call in ast.walk(function(tree, "influence_triggers")) if isinstance(call, ast.Call)
                 and ast.unparse(call.func) == "triggers.append"]
        constant = next(node.value.value for node in tree.body if isinstance(node, ast.Assign)
                        and ast.unparse(node.targets[0]) == "MAGNITUDE_INFLUENCE_TRIGGER")
        self.assertEqual(cmp.INFLUENCE_TRIGGERS, tuple(n.value if isinstance(n, ast.Constant) else constant
                                                       for n in names))

