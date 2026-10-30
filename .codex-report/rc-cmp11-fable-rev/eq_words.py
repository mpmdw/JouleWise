"""RC-CMP11-FABLE-REV answer 2: the exact-equality semantics of Comparison.atom at f6a54deed, per relation word.
For every relation the comparator's words read (GT, LT, LE, GE, NE), a bit-identical number and threshold on both
sides must be decided (within False) with the exact relation's truth: strict words False at equality, non-strict and
equality words True. Then each producer relation (origin/main, read as text in RC-CMP-11's pins) is evaluated at
equality next to the comparator's encoding of it, and the one representation gap (the producer's _same canonical
digest versus the comparator's float ==) is demonstrated at unit level. Synthetic numbers only."""
import json
import math
import sys

sys.path.insert(0, "/home/user/JouleWise")
from tests.independent_recompute.test_comparator import cmp  # noqa: E402

c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))
print("=" * 8, "A. atom at bit-identical equality, each relation (family contrast_j, threshold 0.25)")
for name, test, expect in (("GT strict", cmp.GT, False), ("LT strict", cmp.LT, False), ("NE strict", cmp.NE, False),
                           ("LE non-strict", cmp.LE, True), ("GE non-strict", cmp.GE, True)):
    a = c.atom("t", "contrast_j", "probe/x", 0.25, 0.25, 0.25, test)
    print(f"A {name}: within={a['within']} truth={a['truth']} agree={a['agree']}  -> {'ok' if (not a['within'] and a['truth'] is expect) else 'MISMATCH'}")
print("=" * 8, "B. the same with the threshold given on each side (l9_threshold == threshold), and the controls")
a = c.atom("t", "contrast_j", "probe/x", 0.25, 0.25, 0.25, cmp.GT, 0.25)
print(f"B identical numbers and thresholds: within={a['within']} truth={a['truth']}")
a = c.atom("t", "contrast_j", "probe/x", 0.25, 0.25, 0.25, cmp.GT, 0.25 * (1 + 2 ** -52))
print(f"B identical numbers, thresholds one ulp apart (inside the bar): within={a['within']} (undetermined kept)")
a = c.atom("t", "contrast_j", "probe/x", 3.55e-15, 3.5500000000000004e-15, 0.0, cmp.GT)
print(f"B numbers one ulp apart against 0: within={a['within']} (undetermined kept)")
a = c.atom("t", "contrast_j", "probe/x", 0.0, -0.0, 0.0, cmp.GT)
print(f"B +0.0 vs -0.0 against 0: within={a['within']} truth={a['truth']} (Python == decides a signed-zero pair)")
a = c.atom("t", "contrast_j", "probe/x", float("nan"), float("nan"), 0.0, cmp.GT)
print(f"B nan both sides: within={a['within']} truth={a['truth']} agree={a['agree']} (not known: never decided)")

print("=" * 8, "C. each producer relation at equality next to the comparator's encoding (x == threshold on both sides)")
x = 0.75
rows = [
    ("equals_primary (sensitivity.py:303/320 _same; comparator NE on sensitivity - primary, word = not any)",
     json.dumps(x) == json.dumps(x), not any([cmp.NE(x - x, 0.0)])),
    ("not_below_primary (sensitivity.py:304/321/346 >=; comparator GE on sensitivity - primary)", x >= x, cmp.GE(x - x, 0.0)),
    ("widened (sensitivity.py:279 b_sens > b_op, b_sens = max(b_op, b_max) bracket.py:387; comparator NE on b_sens - b_op)",
     x > x, cmp.NE(x - x, 0.0)),
    ("below_screen_bound (disclosures.py:1099 b_op < SCREEN_BOUND_S; comparator LT)", x < x, cmp.LT(x, x)),
    ("agree (disclosures.py:440 abs(delta) <= hypot; comparator LE on abs(delta) - hypot against 0)",
     abs(x) <= math.hypot(0.45, 0.6), cmp.LE(abs(x) - math.hypot(0.45, 0.6), 0.0)),
    ("plausible rho > 0 (disclosures.py:653 0 < rho; comparator GT 0)", 0 < 0.0, cmp.GT(0.0, 0.0)),
    ("plausible rho <= 1 (disclosures.py:653; comparator LE 1)", 1.0 <= 1, cmp.LE(1.0, 1.0)),
    ("plausible machine - rail >= 0 (disclosures.py:653; comparator GE 0)", x - x >= 0, cmp.GE(x - x, 0.0)),
    ("holm_reject / rejected (multiplicity.py:157 adjusted_p <= threshold; comparator LE alpha)", 0.05 <= 0.05, cmp.LE(0.05, 0.05)),
    ("dominance branch (dominance_closeout ratio >= DOMINANCE_THRESHOLD; comparator GE)", 2.0 >= 2.0, cmp.GE(2.0, 2.0)),
    ("above_floor (claims.py:343 abs(estimate) <= floor -> not above; engine __init__ floor_status abs > floor; comparator GT)",
     not (abs(x) <= x), cmp.GT(abs(x), x)),
    ("estimate sign positive (claims.py:386 > 0.0; engine _sign > 0; comparator GT 0)", 0.0 > 0.0, cmp.GT(0.0, 0.0)),
    ("estimate sign negative (engine _sign < 0; comparator LT 0)", 0.0 < 0.0, cmp.LT(0.0, 0.0)),
    ("decision/metrology contain zero (claims.py:370-371 lower <= 0.0 <= upper; comparator LE 0 / GE 0)",
     0.0 <= 0.0 <= 0.0, cmp.LE(0.0, 0.0) and cmp.GE(0.0, 0.0)),
    ("magnitude trigger (engine sensitivity.py abs(loo - full) > 0.25 * threshold; comparator GT times(0.25, floor))",
     abs(x - x) > 0.25 * x, cmp.GT(abs(x - x), cmp.times(0.25, x))),
]
bad = 0
for label, producer, comparator in rows:
    ok = producer == comparator
    bad += not ok
    print(f"C {'ok      ' if ok else 'MISMATCH'} producer={producer!s:5} comparator={comparator!s:5}  {label}")
print(f"C summary: {len(rows)} relations, {bad} mismatched at equality")

print("=" * 8, "D. the representation gap: _same is a canonical JSON digest (idle_admission.canonical_sha256)")
from joulewise.idle_admission import canonical_sha256  # noqa: E402
for before, after in ((0.0, -0.0), (1, 1.0)):
    same = canonical_sha256(before) == canonical_sha256(after)
    rel = cmp.relation({"k": before}, {"k": after}, ("k",), lambda a, b: a == b)
    a = c.atom("k", "floor_gate_j", "probe/k", cmp.minus(after, before), cmp.minus(after, before), 0.0, cmp.NE)
    print(f"D primary={before!r} sensitivity={after!r}: producer _same={same} (equals_primary printed {same}); "
          f"comparator relation(==)={rel}, atom within={a['within']} truth={a['truth']} -> word decided {not a['truth']}"
          f"{'  <- producer False vs comparator True: DISAGREE (over-refusal) if ever printed' if same != rel else ''}")
print("D note: a sensitivity value equal to its primary value in binary64 but differing in sign of zero or in JSON "
      "number representation is the only pair the two encodings classify differently; both sides' values are "
      "computed by the same code path under an equal bound (b_sens == b_op), so no producer path is shown to print one.")
