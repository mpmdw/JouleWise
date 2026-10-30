"""RC-CMP10-FABLE-REV FS3 probes at 1affc4208 (synthetic only). Question 2: for relation words true by exact
equality, can a WRONG L9 word exit 0 when the values are equal? And would the 'bit-identical on both sides counts
as decided' closure (BI) or the self-consistency closure (SC: each side's word must equal its own test on its own
printed numbers when undetermined) catch it without refusing the sound windows and the full-size b10 flip?"""
import copy
import itertools
import json
import sys

sys.path.insert(0, "/home/user/JouleWise")
from unittest import mock  # noqa: E402

from tests.independent_recompute import test_comparator, test_rc_cmp10  # noqa: E402
from tests.independent_recompute.test_comparator import BLOCKS, DECODE, cmp  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED  # noqa: E402
from tests.independent_recompute.test_rc_cmp7 import find, with_neg8, with_references  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import BLOCK_LINES, RELATION_WORDS, SENSITIVITY, contrast_rows, with_sensitivity  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE  # noqa: E402


class P(test_rc_cmp10.Case):
    def runTest(self):
        pass


def case(widened=True, full=True):
    c = P()
    if full:
        c.base(widened)
    else:
        c.setUp(); with_sensitivity(c, widened)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def flip(c, section, index, word, copies=("record", "disclosure", "block")):
    targets = []
    if "record" in copies:
        targets.append(c.files[SENSITIVITY][section][index])
    if "disclosure" in copies:
        targets.append(c.files[DISCLOSURE]["sensitivity"][section][index])
    if "block" in copies:
        lines = [r for r in c.files[DISCLOSURE]["block_lines"] if r["line"] == BLOCK_LINES[section]]
        targets.append(lines[index]["record"])
    for t in targets:
        t[word] = not t[word]
    return targets[0]


def flip_widened(c, pack):
    for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
        record["windows"][pack]["widened"] = not record["windows"][pack]["widened"]
    line = next(r for r in c.files[DISCLOSURE]["block_lines"] if r["line"] == "sensitivity_window" and r["pack"] == pack)
    line["widened"] = not line["widened"]


# ---- the two candidate closures, as monkeypatches of Comparison.atom / Comparison.word ----
ORIG_ATOM, ORIG_WORD = cmp.Comparison.atom, cmp.Comparison.word


def atom_bi(self, name, family, key, l9, ours, threshold, test, l9_threshold=cmp.MISSING):
    """BI: a test whose number equals its threshold exactly on both sides is decided (no rounding moves an exact
    equality), with truth test(x, x) on each side."""
    a = ORIG_ATOM(self, name, family, key, l9, ours, threshold, test, l9_threshold)
    lt = threshold if l9_threshold is cmp.MISSING else l9_threshold
    if a["within"] and cmp.finite(l9) and cmp.finite(ours) and l9 == lt and ours == threshold:
        a["within"] = False
    return a


def atom_sc(self, name, family, key, l9, ours, threshold, test, l9_threshold=cmp.MISSING):
    a = ORIG_ATOM(self, name, family, key, l9, ours, threshold, test, l9_threshold)
    lt = threshold if l9_threshold is cmp.MISSING else l9_threshold
    a["l9_truth"] = bool(test(l9, lt)) if cmp.finite(l9) and cmp.finite(lt) else None
    return a


def word_sc(self, family, key, l9, ours, atoms=(), decide=None, raw=cmp.MISSING):
    """SC: as word(), but an undetermined row also requires each side's word to equal decide() over that side's
    own truth values (its printed numbers against its own thresholds)."""
    row = ORIG_WORD(self, family, key, l9, ours, atoms, decide, raw)
    if row.get("reason") == "within_bar_undetermined" and decide is not None and row["verdict"] == "AGREE":
        if all(a["l9_truth"] is not None and a["truth"] is not None for a in atoms):
            l9_expect = decide({a["name"]: a["l9_truth"] for a in atoms})
            own_expect = decide({a["name"]: a["truth"] for a in atoms})
            if not (cmp.same(l9, l9_expect) and cmp.same(ours, own_expect)):
                row["verdict"], row["reason"] = "DISAGREE", "within_bar_self_inconsistent"
    return row


CLOSURES = {"head": {}, "BI": {"atom": atom_bi}, "SC": {"atom": atom_sc, "word": word_sc}}


def under(closure, fn):
    patches = [mock.patch.object(cmp.Comparison, name, value) for name, value in CLOSURES[closure].items()]
    for p in patches:
        p.start()
    try:
        return fn()
    finally:
        for p in patches:
            p.stop()


def l9_self_consistent(section, row, word):
    """What L9's own printed primary/sensitivity values say the word should be (the producer's derivation:
    sensitivity.py _same (canonical digest) for equals_primary, >= for not_below_primary)."""
    before, after = row["primary"], row["sensitivity"]
    if word == "equals_primary":
        return json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)
    if word == "not_below_primary":
        keys = {"reported_cells": ("attribution_floor_j",), "floor_cells": ("floor_abs_j", "floor_cmp_j", "floor_gate_j"),
                "contrasts": ("floor_abs_j", "floor_cmp_j", "floor_gate_j", "D_j")}[section]
        return all(after[k] >= before[k] for k in keys)
    if word == "outcome_equals_primary":
        return after["outcome"] == before["outcome"]
    return None


print("=" * 8, "A. undetermined rows on the sound window (base = with_neg8 + with_references + with_sensitivity)")
for widened in (True, False):
    c = case(widened)
    code, err, out = run(c)
    und = [r for r in out["comparisons"] if r.get("reason") == "within_bar_undetermined"]
    print(f"A widened={widened}: exit={code} err={err!r} undetermined rows={len(und)}")
    for r in und:
        print(f"    {r['key']}: l9={r['l9']!r} recompute={r['recompute']!r} within_bar={r['within_bar']}")

print("=" * 8, "B. each relation word negated in every copy (test_rc_cmp8 RELATION_WORDS) + widened, under head / BI / SC")
results = {}
for widened in (True, False):
    for section, index, word in RELATION_WORDS + (("windows", "alpha", "widened"), ("windows", "beta", "widened")):
        for closure in CLOSURES:
            def go():
                c = case(widened)
                if section == "windows":
                    flip_widened(c, index)
                    row = c.files[SENSITIVITY]["windows"][index]
                    printed, should = row["widened"], row["b_sens_s"] > row["b_op_s"]
                else:
                    row = flip(c, section, index, word)
                    printed, should = row[word], l9_self_consistent(section, row, word)
                code, err, out = run(c)
                return code, err, printed, should
            results[(widened, section, index, word, closure)] = under(closure, go)
        head, bi, sc = (results[(widened, section, index, word, k)] for k in ("head", "BI", "SC"))
        print(f"B widened={widened} {section}[{index}].{word}: L9 prints {head[2]!r}, its own numbers say {head[3]!r}; "
              f"exit head={head[0]} BI={bi[0]} SC={sc[0]}" + (f" ({head[1]})" if head[1] else ""))
wrong0 = [k for k, v in results.items() if k[4] == "head" and v[0] == 0 and v[2] != v[3]]
print(f"B summary: WRONG words (contradicting L9's own printed numbers) that exit 0 at head: {len(wrong0)}; "
      f"of these still exit 0 under BI: {sum(results[k[:4] + ('BI',)][0] == 0 for k in wrong0)}, "
      f"under SC: {sum(results[k[:4] + ('SC',)][0] == 0 for k in wrong0)}")

print("=" * 8, "C. the closures must not refuse sound windows or the full-size b10 flip inside the bar")
for closure in CLOSURES:
    for widened in (True, False):
        code, err, out = under(closure, lambda: run(case(widened)))
        print(f"C {closure} sound widened={widened}: exit={code} err={err!r}")
    def b10():
        c = case()
        test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, -1.78e-15, ["estimate_sign"])
        return run(c)
    code, err, out = under(closure, b10)
    r = next((r for r in out.get("comparisons", []) if r["key"] == f"{DECODE}/loo/b10/influence_triggers/0"), None)
    print(f"C {closure} full-size b10 sign flip inside the bar (L9 ['estimate_sign'] vs []): exit={code} "
          f"row={(r or {}).get('verdict')}/{(r or {}).get('reason')}")
    def b10_wrong():
        # L9's number +3.55e-15 and the recompute's +3.55e-15 (identical), L9 prints [] where its sign says a flip.
        c = case()
        test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, 3.55e-15, [])
        return run(c)
    code, err, out = under(closure, b10_wrong)
    print(f"C {closure} b10 identical +3.55e-15 both sides, L9 prints no trigger, recompute raises one: exit={code}")

print("=" * 8, "D. a relation word negated in the record copy only (copy consistency still catches it)")
c = case(False)
flip(c, "floor_cells", 0, "equals_primary", ("record",))
print("D record-only flip unwidened floor equals_primary: exit=%d" % run(c)[0])
