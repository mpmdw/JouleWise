#!/usr/bin/env python3
"""Row 13 output-only experiment. Synthetic trees in memory, two pinned public source files."""
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "public-source"
PINS = {
    "compare_v4_recompute.py": "38438e051fcbdb6d481ff2bd502da53d38d6599ac624b1c56dffe7272c398495",
    "recompute_bars.json": "17a268152f709fd075035598805b70cbe030361d74147c893351161e7b6fbcd4",
}
PAIRS = ("spam", "bank")
# External design card for this invented world. The first member had two turn positions.
TURN_POSITIONS = (("spam", "0"), ("spam", "1"), ("bank", "0"))
MEMBERS = ("A", "B")
WITHHELD = "withheld_until_series_complete"


def historical_source():
    for name, digest in PINS.items():
        if sha256((SOURCES / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"wrong historical source: {name}")
    module = importlib.util.spec_from_file_location("old_comparison", SOURCES / "compare_v4_recompute.py")
    old = importlib.util.module_from_spec(module)
    module.loader.exec_module(old)
    bars, _ = old.load_bars(SOURCES / "recompute_bars.json")
    return old, bars


def historical_world():
    fill = {"claim": {"interpretation": "fixture-text", "detection_rate_licensed": True}, "U6": {}}
    rec = {"acceptance": {"U6": {}}}
    for pair in PAIRS:
        positions = ("0", "1") if pair == "spam" else ("0",)
        fill["U6"][pair] = {
            "status": "pass", "effect_j": 1.0, "margin_j": 1.0, "s_r_j": 1.0,
            "trajectory_clustered_se_j": 1.0, "ci90_j": [0.0, 2.0], "pooled_rss": 1,
            "pooled_df": 1, "imprecise": False,
            "turn_position_residual_means": {
                "means_j": dict.fromkeys(positions, 0.0), "trajectory_counts": dict.fromkeys(positions, 2),
                "evaluable": dict.fromkeys(positions, True),
            },
        }
        rec["acceptance"]["U6"][pair] = {
            "verdict": "pass", "difference": 1.0, "margin": 1.0, "s_r": 1.0, "se": 1.0,
            "interval": [0.0, 2.0], "imprecise": False,
            "per_position_print_only": {p: {"mean": 0.0, "n": 2, "judged": True} for p in positions},
        }
    return fill, rec


def historical_cases():
    old, bars = historical_source()
    member = dict(window="C1", attempt_id="fixture", ordinal=6, engine_run_id="a",
                  recompute_window_id="c", recompute_run_id="b", pair="spam", condition="benign",
                  model="D", role="benign", captured=True, seed_index=1)
    crosswalk = {"schema": "joulewise.v4_release.crosswalk.v1", "members": [member]}
    for case in ("control", "missing_left", "missing_both", "extra_both", "value", "claim_text"):
        fill, rec = historical_world()
        positions = fill["U6"]["spam"]["turn_position_residual_means"]
        right = rec["acceptance"]["U6"]["spam"]["per_position_print_only"]
        if case.startswith("missing"):
            for field in positions.values():
                del field["1"]
            if case == "missing_both":
                del right["1"]
        elif case == "extra_both":
            for field in positions.values():
                field["9"] = field["0"]
            right["9"] = deepcopy(right["0"])
        elif case == "value":
            right["1"]["mean"] += 1
        elif case == "claim_text":
            fill["claim"]["interpretation"] = "fixture-altered"
        engine = old.Engine(fill, {})
        cmp = old.Comparison(engine, rec, crosswalk, bars)
        cmp.u6()
        cmp.claim()
        failures = sorted((row["family"], row["key"]) for row in cmp.rows if not row["ok"])
        expected = []
        if case == "missing_left":
            expected = sorted(("row_completeness", ("U6", "spam", k)) for k in positions)
        if case == "value":
            expected = [("u6_values", ("U6", "spam", "position", "1", "mean"))]
        assert failures == expected, (case, failures, expected)
        assert engine.exempt_of["/fill/claim/interpretation"] == "claim_contract_open"
        assert not (set(engine.leaf) - engine.used - set(engine.exempt_of))
        detail = ",".join(f + "/" + "/".join(k) for f, k in failures) or "none"
        print(f"historical {case} rows={len(cmp.rows)} failed={detail} interpretation=exempt")


@dataclass(frozen=True)
class Leaf:
    family: str
    kind: type
    constant: object = None
    absolute: float = 0.0


def expected(prefix):
    # Semantic rows and branch-specific leaves derived only from the external card.
    schema = {"U6": {p: {} for p in PAIRS}, "claim": {"interpretation": Leaf("claim", str)},
              "S": {}, "series_complete": Leaf("completion", bool, not prefix)}
    for pair, position in TURN_POSITIONS:
        schema["U6"][pair][position] = {
            "n": Leaf("u6", int), "mean": Leaf("u6_values", float, absolute=1e-6),
            "judged": Leaf("u6", bool),
        }
    for member in MEMBERS:
        if prefix:
            schema["S"][member] = {"status": Leaf("prefix", str, WITHHELD),
                                   "reason": Leaf("prefix", str, "fixture-pending")}
        else:
            schema["S"][member] = {"score": Leaf("s_scores", float, absolute=1e-6)}
    return schema


def canonical_world(prefix):
    # Minimal output adapters' target shape. Claim text here is a synthetic public static label.
    def position():
        return {"n": 2, "mean": 0.0, "judged": True}
    phase = {"status": WITHHELD, "reason": "fixture-pending"} if prefix else {"score": 0.25}
    return {"U6": {"spam": {"0": position(), "1": position()}, "bank": {"0": position()}},
            "claim": {"interpretation": "fixture-text"}, "S": {"A": phase.copy(), "B": phase.copy()},
            "series_complete": not prefix}


def leaves(tree, parts=()):
    if isinstance(tree, Leaf):
        yield parts, tree
    else:
        for key, value in sorted(tree.items()):
            yield from leaves(value, parts + (key,))


def resolve(tree, path):
    for part in path:
        tree = tree[part]
    return tree


def failures(schema, left, right):
    errors = []
    def visit(rule, node, path, side):
        location = "/" + "/".join(path)
        if isinstance(rule, Leaf):
            if type(node) is not rule.kind or (rule.kind is float and not math.isfinite(node)):
                errors.append(("REFUSE", side, location, "type"))
            elif rule.constant is not None and node != rule.constant:
                errors.append(("REFUSE", side, location, "state"))
            return
        if type(node) is not dict:
            errors.append(("REFUSE", side, location, "type"))
            return
        for key in sorted(node.keys() ^ rule.keys()):
            errors.append(("REFUSE", side, location.rstrip("/") + "/" + key,
                           "extra" if key in node else "missing"))
        for key in sorted(node.keys() & rule.keys()):
            visit(rule[key], node[key], path + (key,), side)
    for side, tree in (("L", left), ("R", right)):
        visit(schema, tree, (), side)
    if errors:
        return errors
    for path, rule in leaves(schema):
        a, b = resolve(left, path), resolve(right, path)
        same = abs(a - b) <= rule.absolute if rule.kind is float else a == b
        if not same:
            errors.append(("HOLD", "LR", "/" + "/".join(path), rule.family))
    return errors


def exercise():
    for prefix in (False, True):
        mode = "prefix" if prefix else "full"
        schema = expected(prefix)
        def check(case, left, right, wanted):
            result = failures(schema, left, right)
            assert result == wanted, (mode, case, result, wanted)
            report = " | ".join(" ".join(x) for x in result) or "AGREE"
            print(mode, case, report)
        left = canonical_world(prefix)
        right = deepcopy(left)
        check("control", left, right, [])
        a = deepcopy(left)
        del a["U6"]["spam"]["1"]
        check("missing_left", a, right, [("REFUSE", "L", "/U6/spam/1", "missing")])
        b = deepcopy(right)
        b["claim"]["unexpected"] = {}
        check("extra_empty_right", left, b, [("REFUSE", "R", "/claim/unexpected", "extra")])
        for cutoff in ("missing", "extra"):
            a, b = deepcopy(left), deepcopy(right)
            key = "1" if cutoff == "missing" else "9"
            for doc in (a, b):
                rows = doc["U6"]["spam"]
                if cutoff == "missing":
                    del rows[key]
                else:
                    rows[key] = deepcopy(rows["0"])
            check(cutoff + "_both", a, b, [("REFUSE", s, "/U6/spam/" + key, cutoff) for s in "LR"])
        a, b = deepcopy(left), deepcopy(right)
        for doc in (a, b):
            del doc["S"]["B"]
        check("missing_S_member_both", a, b, [("REFUSE", s, "/S/B", "missing") for s in "LR"])
        for path, rule in leaves(schema):
            b = deepcopy(right)
            parent = resolve(b, path[:-1])
            old = parent[path[-1]]
            parent[path[-1]] = {bool: lambda: not old, str: lambda: old + "-altered",
                                int: lambda: old + 1, float: lambda: old + 1.0}[rule.kind]()
            loc = "/" + "/".join(path)
            want = ("REFUSE", "R", loc, "state") if rule.constant is not None else ("HOLD", "LR", loc, rule.family)
            check("mutate" + loc, left, b, [want])
        a, b = deepcopy(left), deepcopy(right)
        for doc in (a, b):
            del doc["claim"]["interpretation"]
        check("missing_claim_both", a, b, [("REFUSE", s, "/claim/interpretation", "missing") for s in "LR"])
        if prefix:
            for doc in (a, b):
                doc["claim"] = deepcopy(left["claim"])
                doc["S"]["A"]["status"] = "fixture-early"
            check("changed_status_both", a, b, [("REFUSE", s, "/S/A/status", "state") for s in "LR"])
            b = deepcopy(right)
            b["S"]["A"]["score"] = 0.25
            check("extra_prefix_payload", left, b, [("REFUSE", "R", "/S/A/score", "extra")])
        else:
            b = deepcopy(right)
            b["S"]["A"]["score"] += 0.5e-6
            check("within_score_bar", left, b, [])


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("run without -O; assertions are the regression oracles")
    historical_cases()
    exercise()
    print("PASS all exact diagnostic assertions")
