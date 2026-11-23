"""Synthetic checks of the RL-187 wire rules and registered exceptions."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
import math
import unittest

from scripts import compare_v4_output_census as cmp

SOURCE = "RL-187 section 2"
BARS = {
    "N1": ("rounded_rational", 0),
    "N2": ("relative", 1e-9),
    "N2d": ("relative", 1e-3),
    "N3": ("absolute", 1e-6),
    "N4": ("relative", 1e-6),
    "N5": ("absolute", 1e-6),
    "N5p": ("absolute", 1e-4),
    "N6": ("rounded_nanoseconds", 0),
    "N7": ("absolute", 1e-9),
}


def compare(census, left, right):
    return cmp.compare(census, json.dumps(left), json.dumps(right))


def numeric_census(*classes):
    fields = {name: cmp.Key(name, ("fixture",), "value") for name in classes}
    rules = {key: cmp.Rule(float, "fixture unit", SOURCE, numeric_class=name) for name, key in fields.items()}
    schema = cmp.Object("report", fields)
    return cmp.Census(schema, schema, rules)


class NumericRules(unittest.TestCase):
    def test_registered_bars_and_mutations(self):
        self.assertEqual({name: (row["operator"], row["tolerance"])
                          for name, row in cmp._bars()["numeric_families"].items()}, BARS)
        census = numeric_census(*BARS)
        left = dict.fromkeys(BARS, 64.0)
        right = left.copy()
        left.update(N1=3 / 7, N6=27 / 10**9)
        right.update(N1=[3, 7], N6=27)
        control = compare(census, left, right)
        self.assertEqual(control.exit_code, cmp.AGREE)
        targets = tuple(cmp.mutation_targets(census, control))
        self.assertEqual(len(targets), 19)

        for binding in targets:
            name = binding.key.family
            with self.subTest(side=binding.side, pointer=cmp.pointer(binding.path), family=name):
                a, b = deepcopy((left, right))
                if binding.side == "L":
                    a[name] = math.nextafter(a[name], math.inf) if name in ("N1", "N6") else a[name] + 1.0
                elif name == "N1":
                    index = binding.component
                    b[name][index] += 1  # Both altered representations remain in lowest terms.
                elif name == "N6":
                    b[name] += 1
                else:
                    b[name] += 1.0
                result = compare(census, a, b)
                self.assertEqual([(f.exit_code, f.family, f.code) for f in result.findings],
                                 [(cmp.HOLD, name, "value")])
                self.assertEqual(compare(census, left, right), control)

        for name, (operator, tolerance) in BARS.items():
            if tolerance:
                with self.subTest(within=name):
                    bound = 64 * tolerance if operator == "relative" else tolerance
                    self.assertEqual(compare(census, left, {**right, name: 64.0 + 0.5 * bound}).exit_code,
                                     cmp.AGREE)

    def test_unbound_numeric_refuses_by_logical_name(self):
        for class_name in (None, "invented_class"):
            key = cmp.Key("uncatalogued", ("fixture",), "float_value")
            rule = cmp.Rule(float, "fixture unit", SOURCE, numeric_class=class_name)
            schema = cmp.Object("report", {"float_value": key})
            result = compare(cmp.Census(schema, schema, {key: rule}), {"float_value": 1.0}, {"float_value": 1.0})
            self.assertEqual(result.findings, tuple(cmp.Finding(cmp.REFUSED, key.family, side, ("float_value",),
                                                               "unbound_numeric", key) for side in cmp.SIDES))
            self.assertEqual(result.public_summary(), {"verdict": "REFUSED", "exit_code": cmp.REFUSED})

    def test_lossless_wire_refuses_malformed_representations(self):
        census = numeric_census("N1", "N6")
        left = {"N1": 0.0, "N6": 0.0}
        right = {"N1": [0, 1], "N6": 0}
        for family, bad in (("N1", v) for v in (0.0, [True, 1], [0, 2], [0, 0], [0, -1], [0, 1, 2])):
            with self.subTest(family=family, bad=bad):
                result = compare(census, left, {**right, family: bad})
                self.assertEqual([(f.exit_code, f.family, f.code) for f in result.findings],
                                 [(cmp.REFUSED, family, "numeric_wire")])
        for bad in (0.0, True, None):
            result = compare(census, left, {**right, "N6": bad})
            self.assertEqual([(f.exit_code, f.family, f.code) for f in result.findings],
                             [(cmp.REFUSED, "N6", "numeric_wire")])
        self.assertEqual(compare(census, {**left, "N1": -0.0}, right).exit_code, cmp.HOLD)

    def test_rational_rounds_once_and_preserves_an_exact_recompute_alias(self):
        n = 2**60
        census = numeric_census("N1")
        key = census.right.fields["N1"]
        rules = {key: replace(census.rules[key], alias_reason="same exact operand in two prints")}
        right_schema = cmp.Object("report", {"N1": key, "mirror": key})
        census = cmp.Census(census.left, right_schema, rules)
        left = {"N1": 1 / n}
        right = {"N1": [1, n], "mirror": [1, n]}
        self.assertEqual(1 / n, 1 / (n + 1))
        self.assertEqual(compare(census, left, right).exit_code, cmp.AGREE)
        result = compare(census, left, {**right, "mirror": [1, n + 1]})
        self.assertEqual([(f.exit_code, f.side, f.family) for f in result.findings], [(cmp.HOLD, "R", "N1")])

    def test_closure_remainders_are_checked_on_each_side(self):
        names = ("whole", "phase_sum", "absolute", "relative", "closes")
        fields = {name: cmp.Key("phase_closure", ("fixture",), name) for name in names}
        schema = cmp.Object("phase_closure", fields)
        closure = cmp.Closure(*(fields[name] for name in names[:4]))
        base_rules = {fields[name]: cmp.Rule(float, "J", SOURCE, numeric_class="N2") for name in names[:2]}
        for whole in (0.0, 100.0):
            abs_rule = cmp.Rule(float, "J", SOURCE)
            rel_rule = cmp.Rule(type(None) if whole == 0 else float, "unitless", SOURCE)
            rules = {**base_rules, closure.absolute_error: abs_rule, closure.relative_error: rel_rule,
                     fields["closes"]: cmp.Rule(bool, "unitless", SOURCE)}
            census = cmp.Census(schema, schema, rules, (closure,))
            value = dict(whole=whole, phase_sum=whole, absolute=0.0,
                         relative=None if whole == 0 else 0.0, closes=True)
            self.assertEqual(compare(census, value, value).exit_code, cmp.AGREE)
            both_wrong = {**value, "absolute": 1.0}
            result = compare(census, both_wrong, both_wrong)
            self.assertEqual([(f.exit_code, f.side, f.code) for f in result.findings],
                             [(cmp.REFUSED, side, "closure") for side in cmp.SIDES])
            if whole:
                right = {**value, "phase_sum": whole + 2e-9}
                right["absolute"] = abs(right["phase_sum"] - right["whole"])
                right["relative"] = right["absolute"] / whole
                self.assertEqual(compare(census, value, right).exit_code, cmp.AGREE)
                self.assertEqual(compare(census, value, {**right, "relative": 0.0}).exit_code, cmp.REFUSED)
            self.assertEqual(compare(census, value, {**value, "closes": False}).exit_code, cmp.HOLD)


def auc_fixture(null=False):
    family = cmp.METADATA_AUC.family
    rule = cmp.Rule(type(None) if null else float, "unitless", SOURCE)
    fields = {"auc": cmp.METADATA_AUC}
    rules = {cmp.METADATA_AUC: rule}
    left = {"auc": None if null else 0.5}
    right = {"metadata_print": {"status": "exempt", "reason": "shared_library_print"}}
    reason = None
    if null:
        key = cmp.Key(family, (), "null_reason")
        reason = cmp.AucNullReason(key, ("fixture_no_folds", "fixture_insufficient"))
        fields["reason"] = key
        rules[key] = cmp.Rule(str, "label", SOURCE, expected="fixture_no_folds", sides=("L",))
        left["reason"] = "fixture_no_folds"
    count_key = cmp.Key("metadata_auc_population", ("fixture_holdout", "fixture_condition"), "count")
    identity_key = cmp.Key("metadata_auc_population", ("fixture_holdout",), "pair")
    rules[count_key] = cmp.Rule(int, "count", SOURCE, expected=2, expected_hold=True, sides=("L",))
    rules[identity_key] = cmp.Rule(str, "identity", SOURCE, expected="fixture_holdout", sides=("L",))
    row = cmp.Object("metadata_auc_population", {"pair": identity_key, "count": count_key})
    folds = cmp.Rows("metadata_auc_population", ("pair",), {("fixture_holdout",): row})
    fields["folds"] = folds
    left["folds"] = [{"pair": "fixture_holdout", "count": 2}]
    return cmp.Census(cmp.Object("report", fields),
                      cmp.Object("report", {"metadata_print": cmp.METADATA_AUC}),
                      rules, auc_population=folds, auc_null_reason=reason), left, right


class AucAndSentences(unittest.TestCase):
    def test_auc_registered_mutation_vector(self):
        census, left, right = auc_fixture()
        control = compare(census, left, right)
        self.assertEqual(control.exit_code, cmp.AGREE)
        self.assertEqual({cmp.pointer(b.path) for b in cmp.mutation_targets(census, control)
                          if b.key == cmp.METADATA_AUC},
                         {"/auc", "/metadata_print/status", "/metadata_print/reason"})
        for side, name in (("L", "auc"), ("R", "metadata_print")):
            a, b = deepcopy((left, right))
            (a if side == "L" else b).pop(name)
            self.assertEqual(compare(census, a, b).findings,
                             (cmp.Finding(cmp.REFUSED, "metadata_auc", side, (name,), "missing", cmp.METADATA_AUC),))
        result = compare(census, {"folds": left["folds"]}, {})
        self.assertEqual([f.side for f in result.findings], ["L", "R"])
        self.assertEqual(result.exit_code, cmp.REFUSED)
        for malformed in (0.5, {}, {"status": "other", "reason": "shared_library_print"},
                          {"status": "exempt", "reason": "other"}, {**right["metadata_print"], "value": 0.5}):
            self.assertEqual([(f.exit_code, f.code) for f in compare(
                census, left, {**right, "metadata_print": malformed}).findings], [(cmp.REFUSED, "auc_marker")])
        for auc in (-0.01, 1.01, True, None):
            self.assertEqual([(f.exit_code, f.code) for f in compare(
                census, {**left, "auc": auc}, right).findings], [(cmp.REFUSED, "auc_shape")])
        self.assertEqual(compare(census, {**left, "auc": 0.75}, right), control)
        self.assertEqual(compare(census, {**left, "auc": 0}, right), control)
        mutated = deepcopy(left)
        mutated["folds"][0]["count"] += 1
        result = compare(census, mutated, right)
        self.assertEqual([(f.exit_code, f.family, f.side, f.code) for f in result.findings],
                         [(cmp.HOLD, "metadata_auc_population", "L", "population")])
        with self.assertRaisesRegex(ValueError, "independent engine fold population"):
            replace(census, auc_population=None)
        duplicates = cmp.Object("report", {**census.left.fields, "second_auc": cmp.METADATA_AUC})
        with self.assertRaisesRegex(ValueError, "exactly one"):
            replace(census, left=duplicates, rules={
                **census.rules, cmp.METADATA_AUC: replace(census.rules[cmp.METADATA_AUC], alias_reason="duplicate"),
            })

    def test_auc_null_has_bound_reason(self):
        census, left, right = auc_fixture(null=True)
        self.assertEqual(compare(census, left, right).exit_code, cmp.AGREE)
        for mutated in ({**left, "reason": "unregistered"}, {key: value for key, value in left.items() if key != "reason"}):
            self.assertEqual(compare(census, mutated, right).exit_code, cmp.REFUSED)
        with self.assertRaisesRegex(ValueError, "null AUC requires"):
            replace(census, auc_null_reason=None)

    def test_sentence_figures_and_each_exact_string_substitution(self):
        self.assertEqual(cmp.format_sentence_figure("one_decimal", 1.25), "1.2")
        self.assertEqual(cmp.format_sentence_figure("one_decimal", -0.02), "0.0")
        self.assertEqual(cmp.format_sentence_figure("one_decimal", 2.675), "2.7")
        self.assertEqual(cmp.format_sentence_figure("p", Fraction(1, 100_000)), "< 0.0001")
        self.assertEqual(cmp.format_sentence_figure("p", Fraction(1, 10_000)), "0.0001")
        self.assertEqual(cmp.format_sentence_figure("p", Fraction(5, 20_000)), "0.0002")
        self.assertEqual(cmp.format_sentence_figure("p", Fraction(7, 20_000)), "0.0004")
        key = cmp.Key("claim_sentence", ("fixture",), "text")
        schema = cmp.Object("report", {"sentence": key})
        census = cmp.Census(schema, schema, {key: cmp.Rule(str, "text", SOURCE)})
        figures = (("count", 4, 5), ("one_decimal", 1.25, 1.75), ("p", Fraction(5, 20_000), Fraction(7, 20_000)))
        parts = [cmp.format_sentence_figure(kind, value) for kind, value, _ in figures]
        template = "Fixture {} rows, {} fewer, p {}."
        clean = {"sentence": template.format(*parts)}
        self.assertEqual(compare(census, clean, clean).exit_code, cmp.AGREE)
        for index, (kind, _, different) in enumerate(figures):
            altered = list(parts)
            altered[index] = cmp.format_sentence_figure(kind, different)
            result = compare(census, clean, {"sentence": template.format(*altered)})
            self.assertEqual([(f.exit_code, f.family, f.code) for f in result.findings],
                             [(cmp.HOLD, "claim_sentence", "value")])
