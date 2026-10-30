#!/usr/bin/env python3.13
"""RC-CMP10-OPUS-REV probes at 1affc4208 (synthetic fixtures only).

Sections:
  eq       FS3 within-bar rule on words true by exact equality: each word printed WRONG (or as a non-word) in
           every copy while the values it reads are exactly equal on both sides. Then the same cases with the
           candidate fix 'exact equality on both sides counts as decided' patched in (atom_exact below), plus the
           full-size ulp cases, to show the fix keeps the RC-CMP-10 over-refusal closure.
  p42      FS2: the p42 code replaced by another closed-set code in every copy.
Run from repo root:
  TMPDIR=<outside checkout> PYTHONPATH=. JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp10-opus-rev/probe_cmp10.py [eq|p42]
"""
import os
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_rc_cmp10 as t10  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import SENSITIVITY  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE  # noqa: E402

cmp = t10.cmp
DECODE = t10.DECODE


class C(t10.Case):
    def runTest(self):
        pass


def new(widened=False):
    c = C()
    c.base(widened)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(t10.CODED)
    except cmp.Refusal as exc:
        return 2, f"Refusal({exc})", {}
    return code, err.strip(), out


def report(label, c, keys=()):
    code, err, out = run(c)
    fails = [(r["family"], r["key"]) for r in out.get("comparisons", []) if r["verdict"] != "AGREE"]
    rows = {r["key"]: r for r in out.get("comparisons", [])}
    shown = [(k, rows[k].get("l9"), rows[k].get("recompute"), rows[k]["verdict"], rows[k].get("reason"))
             for k in keys if k in rows]
    print(f"{label}: exit={code} err={err!r} fails={len(fails)} {fails[:3]} rows={shown}")
    return code


def set_word(c, section, match, word, value):
    """The word set in every printed copy: L9's record, the disclosure's copy and its block line."""
    line = {"reported_cells": "sensitivity_reported", "floor_cells": "sensitivity_floor",
            "contrasts": "sensitivity_contrast"}[section]
    for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
        for row in record[section]:
            if match(row):
                row[word] = value
    for row in c.files[DISCLOSURE]["block_lines"]:
        if row["line"] == line and match(row["record"]):
            row["record"][word] = value


def set_widened(c, pack, value):
    for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
        record["windows"][pack]["widened"] = value
    for row in c.files[DISCLOSURE]["block_lines"]:
        if row["line"] == "sensitivity_window" and row["pack"] == pack:
            row["widened"] = value


FLOOR = "d117-qwen3-1p7b-decode-floor-v5"


def cases():
    """(label, widened, mutate, keys shown). Every mutation is a word the producer could not print for these values."""
    floor = lambda r: r.get("cell_id") == FLOOR
    reported = lambda r: r.get("status") == "computed"
    contrast = lambda r: r.get("contrast_id") == DECODE
    return [
        ("E0 control unwidened", False, lambda c: None, ()),
        ("E1 floor equals_primary False (values identical; producer raises otherwise)", False,
         lambda c: set_word(c, "floor_cells", floor, "equals_primary", False), (f"sensitivity/{FLOOR}/equals_primary",)),
        ("E2 every reported cell equals_primary False", False,
         lambda c: set_word(c, "reported_cells", reported, "equals_primary", False), ()),
        ("E3 floor not_below_primary False (diff exactly 0, 0 >= 0)", False,
         lambda c: set_word(c, "floor_cells", floor, "not_below_primary", False), (f"sensitivity/{FLOOR}/not_below_primary",)),
        ("E4 contrast not_below_primary False", False,
         lambda c: set_word(c, "contrasts", contrast, "not_below_primary", False), (f"sensitivity/{DECODE}/not_below_primary",)),
        ("E5 contrast outcome_equals_primary False (outcomes identical)", False,
         lambda c: set_word(c, "contrasts", contrast, "outcome_equals_primary", False), (f"sensitivity/{DECODE}/outcome_equals_primary",)),
        ("E6 window alpha widened True (b_sens == b_op exactly; producer uses >)", False,
         lambda c: set_widened(c, "alpha", True), ("sensitivity/windows/alpha/widened",)),
        ("E7 floor equals_primary 'banana' (not a boolean)", False,
         lambda c: set_word(c, "floor_cells", floor, "equals_primary", "banana"), (f"sensitivity/{FLOOR}/equals_primary",)),
        ("E8 widened=True window: unchanged beta reported cell equals_primary False", True,
         lambda c: set_word(c, "reported_cells", lambda r: reported(r) and r.get("cell_id") != t10.REPORTED,
                            "equals_primary", False), ()),
        ("E9 widened: floor equals_primary True (decided, control: must fail)", True,
         lambda c: set_word(c, "floor_cells", floor, "equals_primary", True), (f"sensitivity/{FLOOR}/equals_primary",)),
    ]


def atom_exact(orig):
    """Candidate fix: a test whose number equals its threshold exactly on both sides (identical printed JSON value
    on L9's side, numeric equality on the recompute's) counts as decided."""
    def atom(self, name, family, key, l9, ours, threshold, test, l9_threshold=cmp.MISSING):
        a = orig(self, name, family, key, l9, ours, threshold, test, l9_threshold)
        l9t = threshold if l9_threshold is cmp.MISSING else l9_threshold
        if a["within"] and cmp.same(l9, l9t) and ours == threshold:
            a = dict(a, within=False)
        return a
    return atom


def eq():
    for patched in (False, True):
        print(f"--- {'with candidate fix (exact equality decided)' if patched else 'at 1affc4208'}")
        ctx = mock.patch.object(cmp.Comparison, "atom", atom_exact(cmp.Comparison.atom)) if patched else mock.patch.object(cmp, "MISSING", cmp.MISSING)
        with ctx:
            for label, widened, mutate, keys in cases():
                c = new(widened)
                mutate(c)
                report(label, c, keys)
            # The ulp cases RC-CMP-10 closed must stay closed under the fix.
            for label, l9e, owne, trig in (("U1 full-size b10 flip inside bar, L9 ['estimate_sign']", 3.55e-15, -1.78e-15, ["estimate_sign"]),
                                           ("U2 full-size b10 flip inside bar, L9 []", 3.55e-15, -1.78e-15, []),
                                           ("U3 L9 exactly 0.0, recompute 1e-16, L9 []", 0.0, 1e-16, []),
                                           ("U4 L9 exactly 0.0, recompute -1e-16, L9 ['estimate_sign']", 0.0, -1e-16, ["estimate_sign"])):
                c = new(True)
                t10.set_loo(c, t10.WithinBarTests.BLOCK, l9e, owne, trig)
                report(label, c, (f"{DECODE}/loo/b10/influence_triggers",))


def p42():
    """FS2: the p42 code is any closed-set member printed identically everywhere (NEEDS_RULING 1)."""
    c = new(True)
    code0 = report("P0 control", c)
    import json
    sample = json.dumps(c.files)
    produced = next(code for code in cmp.REPORTED_REFUSAL_CODES if code in sample)
    print("producer code in fixture:", produced)
    for other in sorted(cmp.REPORTED_REFUSAL_CODES):
        if other == produced:
            continue
        c = new(True)

        def swap(obj):
            if isinstance(obj, dict):
                return {k: swap(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [swap(v) for v in obj]
            return other if obj == produced else obj
        for name in list(c.files):
            c.files[name] = swap(c.files[name])
        report(f"P42 code -> {other}", c)
    return code0


if __name__ == "__main__" and sys.argv[1] in ("eq", "p42"):
    {"eq": eq, "p42": p42}[sys.argv[1]]()


def hist():
    """FS4 class sweep on the history lines (producer-printed from a 6-attempt index): every line dropped, every
    leaf of every line deleted, and every scalar leaf relabelled (strings, bools, ints, None). Prints the exit-0
    mutations only, plus totals."""
    import copy as _copy
    records = {"plan-beta": {"g10_codes": {"g10.redraw": 1}},
               "plan-alpha": {"bracket": {"observed_triggers": ["t1"], "other_session_systematic_sequences": [3]}}}
    words = ("attempt_count", "attempt_history", "g10", "superseded_history", "reharvest_account")
    c = new(True)
    with t10.history_case(c, t10.HISTORY, records):
        lines = [l for l in c.files[DISCLOSURE]["block_lines"] if l["line"] in words]
        base = report("H0 control", c)
    mutations = []
    for i, line in enumerate(lines):
        mutations.append((f"drop {line['line']}#{i}", i, None, None))
        for key, value in line.items():
            if key == "line":
                continue
            mutations.append((f"del {line['line']}#{i}.{key}", i, key, "DEL"))
            t = type(value)
            alts = ([value + "_x", ""] if t is str else [not value] if t is bool else [value + 1, value - 1]
                    if t is int else ["x", 0, False] if value is None else [[], value + value if value else ["x"]]
                    if t is list else [])
            if isinstance(value, list):
                for j, member in enumerate(value):
                    if isinstance(member, str):
                        alts.append(value[:j] + [member + "_x"] + value[j + 1:])
                    if member is None:
                        alts.append(value[:j] + ["x"] + value[j + 1:])
            for alt in alts:
                mutations.append((f"set {line['line']}#{i}.{key}={alt!r} (was {value!r})", i, key, alt))
    exits = {}
    for label, i, key, alt in mutations:
        c = new(True)

        def edit(ls, i=i, key=key, alt=alt):
            mine = [l for l in ls if l["line"] in words]
            target = mine[i]
            if key is None:
                ls.remove(target)
            elif alt == "DEL":
                del target[key]
            else:
                target[key] = _copy.deepcopy(alt)
        with t10.history_case(c, t10.HISTORY, records, edit=edit):
            code, err, _ = run(c)
        exits[code] = exits.get(code, 0) + 1
        if code == 0:
            print("EXIT0", label)
    print(f"control={base} mutations={len(mutations)} exits={exits}")


def garbage():
    """Undetermined rows read no word set: a non-word inside the bar."""
    for label, trig in (("G1 b10 inside bar, L9 triggers ['banana']", ["banana"]),
                        ("G2 b10 inside bar, L9 triggers ['estimate_sign','estimate_sign']", ["estimate_sign", "estimate_sign"]),
                        ("G3 b10 inside bar, L9 triggers ['outcome']", ["outcome"])):
        c = new(True)
        t10.set_loo(c, t10.WithinBarTests.BLOCK, 3.55e-15, -1.78e-15, trig)
        report(label, c, (f"{DECODE}/loo/b10/influence_triggers",))


if __name__ == "__main__" and sys.argv[1] in ("hist", "garbage"):
    {"hist": hist, "garbage": garbage}[sys.argv[1]]()


def direction():
    """The direction word on a not-supported contrast is 'none' via `or`: any falsy value prints as none."""
    from tests.independent_recompute.test_rc_cmp8 import contrast_rows
    for label, value in (("D0 control (None)", None), ("D1 False", False), ("D2 ''", ""), ("D3 0", 0), ("D4 []", [])):
        c = new(True)
        for row in contrast_rows(c):
            if row.get("contrast_id") == t10.PREFILL and "claim_evaluation" in row:
                row["claim_evaluation"]["direction"] = value
        report(label, c, (f"{t10.PREFILL}/direction",))


if __name__ == "__main__" and sys.argv[1] == "direction":
    direction()
