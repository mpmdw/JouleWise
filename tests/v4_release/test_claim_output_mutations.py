"""Item 9 coverage on invented reports and two distinct JSON wire shapes."""

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import unittest

from scripts import compare_v4_output_census as cmp
from v4_release.row13_fixture import fixture

PLAN = "row13-distinct-wire-v1"
SOURCE = "frozen synthetic design card"
IDENTITY_FIELDS = ("pair", "position")
DENOMINATOR = 2**60


def synthetic_census(prefix):
    """Compile from the frozen card, including required containers and mirrors."""
    rules = {}

    def leaf(family, row, name, kind, unit="unitless", **checks):
        key = cmp.Key(family, row, name)
        rules[key] = cmp.Rule(kind, unit, SOURCE, **checks)
        return key

    claim = leaf("claim", (), "interpretation", str, alias_reason="same interpretation rendered twice")
    complete = leaf("completion", (), "series_complete", bool, expected=not prefix)
    left_pairs = {pair: {} for pair in fixture.PAIRS}
    right_rows = {}
    for pair, pos in fixture.TURN_POSITIONS:
        identity = (pair, pos)
        ids = {name: leaf("u6_rows", identity, name, str, expected=value)
               for name, value in zip(IDENTITY_FIELDS, identity, strict=True)}
        mean = leaf("u6_values", identity, "mean", float, "fixture units", numeric_class="N3")
        count = leaf("u6_values", identity, "n", int, "count")
        judged = leaf("u6_values", identity, "judged", bool)
        left_pairs[pair][pos] = cmp.Object("u6_rows", {**ids, "n": count, "mean": mean, "judged": judged})
        right_rows[identity] = cmp.Object("u6_rows", {**ids, "count": count, "residual": mean, "judged": judged})

    left_s, right_s = {}, {}
    family = "prefix" if prefix else "s_scores"
    for member in fixture.MEMBERS:
        if prefix:
            status = leaf(family, (member,), "status", str, expected=fixture.WITHHELD)
            reason = leaf(family, (member,), "reason", str, expected="fixture-pending")
            left_s[member] = cmp.Object(family, {"status": status, "reason": reason})
            right_s[member] = cmp.Object(family, {"state": status, "why": reason})
        else:
            score = leaf(family, (member,), "score", float, numeric_class="N5")
            left_s[member] = cmp.Object(family, {"score": score})
            right_s[member] = score

    unavailable = leaf("qualification", (), "unavailable", type(None), expected=None)
    commitment = leaf("commitment", (), "opaque", str, presence_only=True, pattern="[0-9a-f]{64}")
    empty = cmp.Sequence("empty_rows", (), empty_reason="the invented stratum has no contributors")
    low = leaf("interval", (), "lower", float, numeric_class="N7")
    high = leaf("interval", (), "upper", float, numeric_class="N7")
    numerator = leaf("exact_tail", (), "numerator", int)
    denominator = leaf("exact_tail", (), "denominator", int)
    rounded = leaf("exact_tail", (), "display", float, numeric_class="N5")
    left = cmp.Object("report", {
        "claim": cmp.Object("claim", {"interpretation": claim, "rendered": claim}),
        "series_complete": complete,
        "U6": cmp.Object("u6_rows", {p: cmp.Object("u6_rows", cells) for p, cells in left_pairs.items()}),
        "S": cmp.Object(family, left_s),
        "extra/~checks": cmp.Object("coverage", {"empty": empty, "unavailable": unavailable}),
        "opaque": commitment,
        "interval": cmp.Sequence("interval", (low, high)),
        "tail": cmp.Object("exact_tail", {"num": numerator, "den": denominator, "display": rounded}),
    })
    right = cmp.Object("report", {
        "decision": cmp.Object("claim", {"text": claim}),
        "complete": complete,
        "residuals": cmp.Rows("u6_rows", IDENTITY_FIELDS, right_rows),
        "scores": cmp.Object(family, right_s),
        "coverage": cmp.Object("coverage", {"contributors": empty, "missing": unavailable}),
        "commitment": commitment,
        "interval": cmp.Object("interval", {"start": low, "end": high}),
        "tail": cmp.Sequence("exact_tail", (numerator, denominator, rounded)),
    })
    if prefix:
        marker = leaf("prefix_compact", (), "status", str, expected=fixture.WITHHELD)
        left = replace(left, fields={**left.fields, "q": marker})
        right = replace(right, fields={**right.fields, "q": cmp.Object("prefix_compact", {"status": marker})})
    return cmp.Census(left, right, rules)


def synthetic_reports(prefix):
    left = fixture.canonical_world(prefix)
    left["claim"]["rendered"] = "fixture-text"
    left["extra/~checks"] = {"empty": [], "unavailable": None}
    left["opaque"] = "0" * 64
    left["interval"] = [-1.0, 1.0]
    left["tail"] = {"num": 1, "den": DENOMINATOR, "display": 1 / DENOMINATOR}
    residuals = []
    for pair, positions in left["U6"].items():
        for pos, row in positions.items():
            row.update(pair=pair, position=pos)
            row["mean"] = 0.125 if (pair, pos) == ("bank", "0") else 0.0
            residuals.append(dict(pair=pair, position=pos, count=row["n"],
                                  residual=row["mean"], judged=row["judged"]))
    right = {
        "decision": {"text": "fixture-text"},
        "complete": not prefix,
        "residuals": residuals[::-1],
        "scores": {member: {"state": value["status"], "why": value["reason"]} if prefix else value["score"]
                   for member, value in left["S"].items()},
        "coverage": {"contributors": [], "missing": None},
        "commitment": "1" * 64,
        "interval": {"start": -1.0, "end": 1.0},
        "tail": [1, DENOMINATOR, 1 / DENOMINATOR],
    }
    if prefix:
        left["q"] = fixture.WITHHELD
        right["q"] = {"status": fixture.WITHHELD}
    return left, right


def compare(census, docs):
    return cmp.compare(census, *(doc if isinstance(doc, str) else json.dumps(doc) for doc in docs))


def alternate(value, rule):
    if rule.kind is bool:
        return not value
    if rule.kind is str:
        return value + "-alternate"
    if rule.kind is int:
        return value + 1
    return value + 1.0


def audit_cases(test, prefix):
    census = synthetic_census(prefix)
    clean = synthetic_reports(prefix)
    mode = "prefix" if prefix else "full"
    control = compare(census, clean)
    test.assertEqual(control.public_summary(), {"verdict": "AGREE", "exit_code": cmp.AGREE})
    yield {"mode": mode, "mutation_id": "control", "expected_exit": cmp.AGREE,
           "actual_exit": control.exit_code, "blinded": control.public_summary(),
           "coverage": dict(Counter(binding.side for binding in control.bindings))}

    def check(case, mutated, exit_code, expected, side, path, binding=None):
        outcome = compare(census, mutated)
        test.assertEqual(outcome.exit_code, exit_code, (mode, case))
        actual = {(finding.family, finding.side, finding.code) for finding in outcome.findings}
        test.assertEqual(actual, set(expected), (mode, case))
        test.assertEqual(compare(census, clean), control, (mode, case, "restored"))
        key = None
        operation = "shape"
        if binding is not None:
            key = {"family": binding.key.family, "row": binding.key.row, "leaf": binding.key.leaf}
            test.assertTrue(any(finding.path == binding.path or finding.key == binding.key
                                or (finding.code == "extra_row" and finding.path == binding.path[:-1])
                                for finding in outcome.findings), (mode, case, key))
            rule = binding.rule
            if rule.presence_only:
                operation = "presence"
            elif rule.expected is not cmp.UNSET:
                operation = "state"
            else:
                operation = rule.bar["operator"] if rule.bar else "exact"
        return {
            "mode": mode, "mutation_id": case, "wire_side": side, "pointer": path,
            "logical_key": key, "rule_source": binding.rule.source if binding else SOURCE,
            "operator": operation, "unit": binding.rule.unit if binding else None,
            "numeric_class": binding.rule.numeric_class if binding else None,
            "tolerance": binding.rule.bar["tolerance"] if binding and binding.rule.bar else None,
            "expected_exit": exit_code,
            "actual_exit": outcome.exit_code, "expected_failures": sorted(expected),
            "actual_failures": sorted(actual),
        }

    targets = tuple(cmp.mutation_targets(census, control))
    test.assertEqual(Counter(target.side for target in targets), {"L": 30 if prefix else 27,
                                                                 "R": 29 if prefix else 26})
    for target in targets:
        side, path, key, rule = target.side, target.path, target.key, target.rule
        mutated = deepcopy(clean)
        parent = fixture.resolve(mutated[cmp.SIDES.index(side)], path[:-1])
        member = path[-1]
        expected = [(key.family, "LR", "value")]
        exit_code = cmp.HOLD
        if rule.presence_only or rule.kind is type(None):
            del parent[member]
            expected, exit_code = [(key.family, side, "missing")], cmp.REFUSED
        else:
            parent[member] = alternate(parent[member], rule)
            if key.family == "u6_rows" and side == "R":
                expected = [(key.family, side, "missing_row"), (key.family, side, "extra_row")]
                exit_code = cmp.REFUSED
            elif rule.expected is not cmp.UNSET:
                expected, exit_code = [(key.family, side, "state")], cmp.REFUSED
            elif key.family == "claim" and side == "L":
                expected.append((key.family, side, "value"))
        pointer = cmp.pointer(path)
        yield check(f"leaf/{side}{pointer}", mutated, exit_code, expected, side, pointer, target)

    def structural(case, side, path, action, *expected):
        mutated = deepcopy(clean)
        action(*mutated)
        return check(case, mutated, cmp.REFUSED, expected, side, path)

    def missing_both(left, right):
        del left["U6"]["spam"]["1"]
        del right["residuals"][1]

    def extra_both(left, right):
        left["U6"]["spam"]["9"] = dict(left["U6"]["spam"]["0"], position="9")
        right["residuals"].append(dict(right["residuals"][1], position="9"))

    def wrong_prefix(left, right):
        left["S"]["A"]["status"] = right["scores"]["A"]["state"] = "early"

    def swap_identities(_, right):
        a, b = right["residuals"][:2]
        for field in IDENTITY_FIELDS:
            a[field], b[field] = b[field], a[field]

    yield structural("common_omission", "LR", ["/U6/spam/1", "/residuals/1"], missing_both,
                     ("u6_rows", "L", "missing"), ("u6_rows", "R", "missing_row"))
    yield structural("common_addition", "LR", ["/U6/spam/9", "/residuals/3"], extra_both,
                     ("u6_rows", "L", "extra"), ("u6_rows", "R", "extra_row"))
    yield structural("duplicate_identity", "R", "/residuals/3",
                     lambda _, r: r["residuals"].append(deepcopy(r["residuals"][0])),
                     ("u6_rows", "R", "duplicate_identity"))
    yield structural("same_count_substitute", "L", "/U6/spam/1",
                     lambda l, _: l["U6"]["spam"].update({"9": l["U6"]["spam"].pop("1")}),
                     ("u6_rows", "L", "extra"), ("u6_rows", "L", "missing"))
    mutated = deepcopy(clean)
    swap_identities(*mutated)
    yield check("swap_identities", mutated, cmp.HOLD, [("u6_values", "LR", "value")],
                "R", ["/residuals/0", "/residuals/1"])
    yield structural("remove_empty", "L", "/extra~1~0checks/empty",
                     lambda l, _: l["extra/~checks"].pop("empty"), ("empty_rows", "L", "missing"))
    yield structural("replace_null_with_zero", "R", "/coverage/missing",
                     lambda _, r: r["coverage"].update(missing=0), ("qualification", "R", "type"))
    yield structural("remove_bound_endpoint", "L", "/interval/1",
                     lambda l, _: l["interval"].pop(), ("interval", "L", "missing"))
    yield structural("extra_recompute_leaf", "R", "/decision/fresh",
                     lambda _, r: r["decision"].update(fresh="unexpected"), ("claim", "R", "extra"))
    yield structural("claim_omission_both", "LR", ["/claim/interpretation", "/decision/text"],
                     lambda l, r: (l["claim"].pop("interpretation"), r["decision"].pop("text")),
                     ("claim", "L", "missing"), ("claim", "R", "missing"))
    if prefix:
        yield structural("changed_shared_marker", "LR", ["/S/A/status", "/scores/A/state"], wrong_prefix,
                         ("prefix", "L", "state"), ("prefix", "R", "state"))
        yield structural("unopened_prefix_payload", "R", "/scores/A/score",
                         lambda _, r: r["scores"]["A"].update(score=0.25), ("prefix", "R", "extra"))
        yield structural("compact_marker_sibling", "R", "/q/result",
                         lambda _, r: r["q"].update(result=0.25), ("prefix_compact", "R", "extra"))
    else:
        mutated = deepcopy(clean)
        mutated[1]["scores"]["A"] += 0.5e-6
        yield check("within_score_bar", mutated, cmp.AGREE, (), "R", "/scores/A")
    mutated = deepcopy(clean)
    mutated[1]["residuals"].reverse()
    yield check("reordered_set", mutated, cmp.AGREE, (), "R", "/residuals")
    mutated = deepcopy(clean)
    mutated[1]["commitment"] = "2" * 64
    yield check("other_valid_commitment", mutated, cmp.AGREE, (), "R", "/commitment")
    test.assertEqual(1 / DENOMINATOR, 1 / (DENOMINATOR + 1))


class OutputMutations(unittest.TestCase):
    def test_frozen_fixture(self):
        with redirect_stdout(io.StringIO()):
            fixture.historical_cases()
            fixture.exercise()

    def test_indexed_output_mutations(self):
        for prefix in (False, True):
            list(audit_cases(self, prefix))

    def test_strict_parse_on_both_sides(self):
        census = synthetic_census(False)
        clean = synthetic_reports(False)
        for side in cmp.SIDES:
            for raw, code in (('{"z":1,"z":2}', "duplicate_json_key"), ('{"z":1e400}', "nonfinite_json"),
                              ('{"z":NaN}', "nonfinite_json"), ("{", "invalid_json")):
                with self.subTest(side=side, code=code, raw=raw):
                    mutated = list(clean)
                    mutated[cmp.SIDES.index(side)] = raw
                    result = compare(census, mutated)
                    self.assertEqual(result.findings, (cmp.Finding(cmp.REFUSED, "report", side, (), code),))
                    self.assertEqual(result.public_summary(), {"verdict": "REFUSED", "exit_code": cmp.REFUSED})

    def test_unbound_rules_and_unjustified_empty_family(self):
        census = synthetic_census(False)
        rules = dict(census.rules)
        rules.pop(next(iter(rules)))
        with self.assertRaisesRegex(ValueError, "unbound leaf"):
            replace(census, rules=rules)
        rules = {**census.rules, cmp.Key("unused", (), "x"): cmp.Rule(str, "unitless", SOURCE)}
        with self.assertRaisesRegex(ValueError, "unused rule"):
            replace(census, rules=rules)
        with self.assertRaisesRegex(ValueError, "empty container"):
            cmp.Census(cmp.Object("empty", {}), cmp.Object("empty", {}), {})

    def test_required_opaque_shape(self):
        census = synthetic_census(True)
        docs = synthetic_reports(True)
        docs[1]["commitment"] = "unrecognized"
        result = compare(census, docs)
        self.assertEqual(result.exit_code, cmp.REFUSED)
        self.assertEqual([(f.family, f.side, f.code) for f in result.findings],
                         [("commitment", "R", "shape")])

    def test_ruled_refusal_for_an_exact_mismatch(self):
        census = synthetic_census(False)
        key = cmp.Key("exact_tail", (), "numerator")
        rules = {**census.rules, key: replace(census.rules[key], refuse_mismatch=True)}
        left, right = synthetic_reports(False)
        right["tail"][0] += 1
        result = compare(replace(census, rules=rules), (left, right))
        self.assertEqual(result.findings,
                         (cmp.Finding(cmp.REFUSED, "exact_tail", "LR", ("tail", 0), "value", key),))

    def test_shared_wrong_literal_fails_the_design(self):
        census = synthetic_census(False)
        key = cmp.Key("claim", (), "interpretation")
        census = replace(census, rules={**census.rules, key: replace(census.rules[key], expected="fixture-text")})
        left, right = synthetic_reports(False)
        for name in left["claim"]:
            left["claim"][name] = "fixture-wrong"
        right["decision"]["text"] = "fixture-wrong"
        result = compare(census, (left, right))
        self.assertEqual(result.exit_code, cmp.REFUSED)
        self.assertEqual([(f.family, f.side, f.code) for f in result.findings],
                         [("claim", "L", "state"), ("claim", "L", "state"), ("claim", "R", "state")])


def evidence_index():
    test = OutputMutations()
    pins = {label: sha256(Path(path).read_bytes()).hexdigest() for label, path in (
        ("historical_fixture_sha256", fixture.__file__), ("schema_runner_sha256", __file__),
        ("synthetic_comparator_sha256", cmp.__file__),
    )}
    for prefix in (False, True):
        run = f"{PLAN}/{'prefix' if prefix else 'full'}"
        card = {"prefix": prefix, "positions": fixture.TURN_POSITIONS, "members": fixture.MEMBERS,
                "tail_denominator": DENOMINATOR}
        print(json.dumps({
            "fixture_id": PLAN, "run": run, "evidence": "invented-json", "pins": pins,
            "input_card_sha256": sha256(json.dumps(card, sort_keys=True).encode()).hexdigest(),
            "bars_sha256": sha256(cmp.BARS_PATH.read_bytes()).hexdigest(),
        }, sort_keys=True, separators=(",", ":")))
        for result in audit_cases(test, prefix):
            print(json.dumps({"run": run, **result},
                             sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    if sys.argv[1:] == ["--evidence-index"]:
        evidence_index()
    else:
        unittest.main()
