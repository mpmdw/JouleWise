"""L9-ENV6-FINAL-FABLE Q4: independent re-derivation of the clamped corner envelope.

Evaluates the energy over (delta, eps_on, eps_off) directly with its own
integrator (an inverted interval contributes 0 J), takes the exact extremum
over the admissible box (corners in eps, breakpoints in delta; interval-support
traces make the energy piecewise linear in delta), and compares it with
``whole_window._clamped_corner_composed_anchor_shift_envelope`` and with
reduce's ``_corner_composed_anchor_shift_envelope``.  Hand-built synthetic
traces only.
"""
from __future__ import annotations

import json
import math
import random
import sys

from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import _corner_composed_anchor_shift_envelope as reduce_env
from joulewise.whole_window import (
    _clamped_corner_composed_anchor_shift_envelope as clamp_env,
)


def energy(rows, windows, delta, eps_on, eps_off):
    """rows: (support_start, support_end, power); windows: (start, end)."""
    total = 0.0
    for start, end in windows:
        ws, we = start + eps_on, end + eps_off
        if we < ws:  # inverted interval -> empty set -> 0 J
            continue
        for a, b, p in rows:
            lo, hi = max(ws, a + delta), min(we, b + delta)
            if hi > lo:
                total += p * (hi - lo)
    return total


def exact_extrema(rows, windows, bundle_bound, edge):
    edges = sorted({a for a, _b, _p in rows} | {b for _a, b, _p in rows})
    lo, hi = math.inf, -math.inf
    for eps_on in (-edge, edge):
        for eps_off in (-edge, edge):
            deltas = {-bundle_bound, 0.0, bundle_bound}
            for start, end in windows:
                for wedge in (start + eps_on, end + eps_off):
                    for tedge in edges:
                        d = wedge - tedge
                        if -bundle_bound <= d <= bundle_bound:
                            deltas.add(d)
            for d in sorted(deltas):
                e = energy(rows, windows, d, eps_on, eps_off)
                lo, hi = min(lo, e), max(hi, e)
    return lo, hi


def containment(rows, windows, bundle_bound, edge, lower, upper, n=20000, seed=7):
    rng = random.Random(seed)
    worst = 0.0
    for _ in range(n):
        d = rng.uniform(-bundle_bound, bundle_bound)
        eon = rng.uniform(-edge, edge)
        eoff = rng.uniform(-edge, edge)
        e = energy(rows, windows, d, eon, eoff)
        worst = max(worst, lower - e, e - upper)
    return worst <= 1e-9, worst


def trace(rows):
    return [TracePoint(t=b, power_w=p, support_start_s=a, support_end_s=b) for a, b, p in rows]


def stepped(origin, count, width, seed):
    rng = random.Random(seed)
    return [(origin + i * width, origin + (i + 1) * width, 4.0 + 6.0 * rng.random()) for i in range(count)]


def run_case(name, rows, windows, bundle_bound, fiducial, span, expect=None):
    edge = fiducial + span
    contributions = [(trace(rows), [Window(s, e) for s, e in windows])]
    r = reduce_env(contributions, bundle_bound, fiducial, span)
    c = clamp_env(contributions, bundle_bound, fiducial, span)
    point = energy(rows, windows, 0.0, 0.0, 0.0)
    lo, hi = exact_extrema(rows, windows, bundle_bound, edge)
    print(f"== {name}: edge={edge} 2*edge={2*edge} windows={windows}")
    print(f"   reduce : {'None' if r is None else json.dumps({k: r[k] for k in ('point_j','lower_j','upper_j')})}")
    print(f"   clamp  : {'None' if c is None else json.dumps({k: c[k] for k in ('point_j','lower_j','upper_j')})}")
    print(f"   exact  : point={point!r} min={lo!r} max={hi!r}")
    ok = True
    if c is None:
        ok = False
        print("   FAIL: clamp returned None")
    else:
        for key, mine in (("point_j", point), ("lower_j", lo), ("upper_j", hi)):
            if not math.isclose(float(c[key]), mine, rel_tol=1e-9, abs_tol=1e-9):
                ok = False
                print(f"   FAIL: {key} clamp={c[key]!r} exact={mine!r}")
        inside, worst = containment(rows, windows, bundle_bound, edge, float(c["lower_j"]), float(c["upper_j"]))
        print(f"   containment of 20000 random interior points: {inside} (worst excursion {worst:.3e})")
        ok = ok and inside
        if r is not None:
            same = r == c
            print(f"   reduce defined -> clamp == reduce (dict equality): {same}")
            ok = ok and same
        if expect is not None:
            for key, val in expect.items():
                if not math.isclose(float(c[key]), val, rel_tol=1e-9, abs_tol=1e-9):
                    ok = False
                    print(f"   FAIL: hand-derived {key}={val!r} vs clamp {c[key]!r}")
            print(f"   hand-derived expectation {expect}: {'matches' if ok else 'MISMATCH'}")
    print(f"   RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    results = []
    const = [(i * 0.1, (i + 1) * 0.1, 10.0) for i in range(100)]  # 10 W, [0, 10] s
    # A: single short window 0.3 s, edge 0.2 -> 2*edge 0.4 > 0.3: inverts at (+e,-e).
    #    Hand: lower = 0 J (clamped to zero length); upper = 10 W * (0.3 + 0.4) s = 7 J; point = 3 J.
    results.append(run_case("A constant power, short window", const, [(5.0, 5.3)], 0.05, 0.15, 0.05,
                            expect={"point_j": 3.0, "lower_j": 0.0, "upper_j": 7.0}))
    # B: two intervals, only the short one inverts; lower bound is NOT 0.
    var = stepped(0.0, 120, 0.1, seed=11)  # [0, 12] s varying power
    results.append(run_case("B two intervals, one inverts", var, [(2.0, 3.0), (6.0, 6.1)], 0.03, 0.06, 0.02))
    # C: non-inverting control -> reduce defines; clamp must be reduce's bytes.
    results.append(run_case("C non-inverting control", var, [(5.0, 6.0)], 0.03, 0.06, 0.02))
    # D: window exactly 2*edge long -> zero-length at the corner, not inverted; reduce defines.
    results.append(run_case("D window exactly 2*edge", var, [(5.0, 5.16)], 0.03, 0.06, 0.02))
    # E: window just under 2*edge -> inverts; clamp defines with lower 0 for a single window.
    results.append(run_case("E window just under 2*edge", var, [(5.0, 5.16 - 1e-6)], 0.03, 0.06, 0.02))
    # F: already-inverted input window: reduce None and clamp None (outside the ruling).
    contributions = [(trace(var), [Window(5.1, 5.0)])]
    f_r = reduce_env(contributions, 0.03, 0.06, 0.02)
    f_c = clamp_env(contributions, 0.03, 0.06, 0.02)
    print(f"== F already-inverted input window [5.1, 5.0]: reduce={f_r} clamp={f_c}")
    results.append(f_r is None and f_c is None)
    print(f"   RESULT: {'PASS' if results[-1] else 'FAIL'}")
    # G: negative power sample: both None.
    neg = list(var); neg[50] = (neg[50][0], neg[50][1], -1.0)
    contributions = [(trace(neg), [Window(5.0, 5.1)])]
    g_r = reduce_env(contributions, 0.03, 0.06, 0.02)
    g_c = clamp_env(contributions, 0.03, 0.06, 0.02)
    print(f"== G negative power sample, short window: reduce={g_r} clamp={g_c}")
    results.append(g_r is None and g_c is None)
    print(f"   RESULT: {'PASS' if results[-1] else 'FAIL'}")
    print(f"\nALL {'PASS' if all(results) else 'FAIL'} ({sum(results)}/{len(results)})")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
