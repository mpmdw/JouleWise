#!/usr/bin/env python3.13
"""RC-CMP11-OPUS-REV probes at f6a54deed (synthetic fixtures only).

  direction  F4 with the PREFILL rows actually mutated (contrast_rows(c, PREFILL)); D7 the key absent.
  zero       F1 corner: the producer's equals_primary is a canonical digest (sensitivity.py _same: signed zero and
             JSON int/float differ); the comparator's NE test on (sensitivity - primary) reads -0.0 vs 0.0 and 1 vs 1.0
             as equal. Unit call of relation_words on identical values on both sides, L9 printing the producer's word.
Run from repo root:
  TMPDIR=<outside checkout> PYTHONPATH=. JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp11-opus-rev/probe_cmp11.py [direction|zero]
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_rc_cmp10 as t10  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import contrast_rows  # noqa: E402

cmp = t10.cmp


class C(t10.Case):
    def runTest(self):
        pass


def run(c):
    try:
        code, err, out = c.exit_code(t10.CODED)
    except cmp.Refusal as exc:
        return 2, f"Refusal({exc})", {}
    return code, err.strip(), out


def direction():
    for label, value in (("D0 None (control)", None), ("D1 False", False), ("D2 ''", ""), ("D3 0", 0), ("D4 []", []),
                         ("D5 'banana'", "banana"), ("D6 'positive' (not supported)", "positive"),
                         ("D7 key absent", KeyError)):
        c = C()
        c.base(True)
        n = 0
        for row in contrast_rows(c, t10.PREFILL):
            if value is KeyError:
                row["claim_evaluation"].pop("direction", None)
            else:
                row["claim_evaluation"]["direction"] = value
            n += 1
        code, err, out = run(c)
        r = next((r for r in out.get("comparisons", []) if r["key"] == f"{t10.PREFILL}/direction"), {})
        print(f"{label}: rows mutated={n} exit={code} err={err!r} row=({r.get('l9')!r}, {r.get('recompute')!r}, "
              f"{r.get('verdict')}, {r.get('reason')})")


def zero():
    bars = json.loads((ROOT / "configs/analysis/b5/recompute_bars.json").read_text())
    families = {k: "floor_j" for k in cmp.FLOOR_KEYS + ("allowance_j",)}
    for label, p, s in (("Z0 0.0 -> 0.0 (control)", 0.0, 0.0), ("Z1 0.0 -> -0.0", 0.0, -0.0),
                        ("Z2 1 (int) -> 1.0", 1, 1.0)):
        producer_word = json.dumps(p) == json.dumps(s)  # sensitivity.py _same (canonical digest)
        before = {k: 0.5 for k in cmp.FLOOR_KEYS + ("allowance_j",)}
        after = dict(before)
        before["floor_abs_j"], after["floor_abs_j"] = p, s
        row = {"primary": dict(before), "sensitivity": dict(after), "equals_primary": producer_word,
               "not_below_primary": True}
        c = cmp.Comparison(bars)
        cmp.relation_words(c, "sensitivity/probe", row, before, after, cmp.FLOOR_KEYS + ("allowance_j",),
                           cmp.FLOOR_KEYS, families)
        r = next(r for r in c.rows if r["key"].endswith("/equals_primary"))
        print(f"{label}: producer equals_primary={producer_word} comparator row=({r['l9']!r}, {r['recompute']!r}, "
              f"{r['verdict']}, {r.get('reason')})")


if __name__ == "__main__":
    {"direction": direction, "zero": zero}[sys.argv[1]]()
