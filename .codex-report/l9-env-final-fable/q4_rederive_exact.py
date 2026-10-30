"""Q4, exact version: eps at the four corners (monotone in each edge), delta at
every window-edge minus trace-edge breakpoint in [-B, B] (energy is piecewise
linear in delta for interval-support traces), plus 20000 random interior
(delta, eps_on, eps_off) samples that must stay inside [lower_j, upper_j].
Inverted intervals contribute 0 J.  Independent of reduce's scanner."""
import random, sys
sys.path.insert(0, ".")
from joulewise.bundle_read import TracePoint, Window
from joulewise import reduce as R
from joulewise import whole_window as W

def interval_curve(origin, n, dt, powers):
    return [TracePoint(t=origin+(i+1)*dt, power_w=powers[i % len(powers)],
                       support_start_s=origin+i*dt, support_end_s=origin+(i+1)*dt) for i in range(n)]

def energy(contribs, delta, on, off):
    total = 0.0
    for curve, windows in contribs:
        for w in windows:
            a, b = w.start_s + on, w.end_s + off
            if b <= a:
                continue
            for p in curve:
                total += p.power_w * max(0.0, min(b, p.support_end_s + delta) - max(a, p.support_start_s + delta))
    return total

def exact_extrema(contribs, B, e):
    # shift to a common origin first, as both functions do, to avoid epoch rounding
    o = contribs[0][0][0].t
    contribs = [([TracePoint(t=p.t-o, power_w=p.power_w, support_start_s=p.support_start_s-o, support_end_s=p.support_end_s-o) for p in c],
                 [Window(start_s=w.start_s-o, end_s=w.end_s-o) for w in ws]) for c, ws in contribs]
    vals = []
    for on in (-e, e):
        for off in (-e, e):
            deltas = {-B, 0.0, B}
            for c, ws in contribs:
                edges = [p.support_start_s for p in c] + [p.support_end_s for p in c]
                for w in ws:
                    for we in (w.start_s + on, w.end_s + off):
                        for te in edges:
                            d = we - te
                            if -B <= d <= B:
                                deltas.add(d)
            vals += [energy(contribs, d, on, off) for d in deltas]
    rng = random.Random(7)
    interior = [energy(contribs, rng.uniform(-B, B), rng.uniform(-e, e), rng.uniform(-e, e)) for _ in range(20000)]
    return min(vals), max(vals), min(interior), max(interior), energy(contribs, 0, 0, 0)

origin = 1_700_000_000.0
curve = interval_curve(origin, 40, 0.1, [2.0, 3.0, 1.0, 4.0])
cases = [
    ("A single short window (0.30 s, 2e = 0.40)", [(curve, [Window(origin+1.55, origin+1.85)])], 0.05, 0.15, 0.05),
    ("B two intervals (1.0 s and 0.10 s), e = 0.12", [(curve, [Window(origin+1.0, origin+2.0), Window(origin+2.5, origin+2.6)])], 0.03, 0.10, 0.02),
    ("C non-inverting control (1.0 s, 2e = 0.40)", [(curve, [Window(origin+1.2, origin+2.2)])], 0.05, 0.15, 0.05),
    ("D zero-length input window", [(curve, [Window(origin+1.5, origin+1.5)])], 0.05, 0.15, 0.05),
    ("E window exactly 2e long (boundary)", [(curve, [Window(origin+1.5, origin+1.9)])], 0.05, 0.15, 0.05),
]
ok = True
for name, contribs, B, fid, span in cases:
    e = fid + span
    minted = R._corner_composed_anchor_shift_envelope(contribs, B, fid, span)
    clamped = W._clamped_corner_composed_anchor_shift_envelope(contribs, B, fid, span)
    lo, hi, ilo, ihi, point = exact_extrema(contribs, B, e)
    print(f"== {name}")
    print(f"   reduce : {None if minted is None else {k: minted[k] for k in ('point_j','lower_j','upper_j')}}")
    print(f"   clamp  : {None if clamped is None else {k: clamped[k] for k in ('point_j','lower_j','upper_j')}}")
    print(f"   exact  : point={point!r} min={lo!r} max={hi!r}; random interior within [min,max]: {lo-1e-12 <= ilo and ihi <= hi+1e-12}")
    if minted is not None:
        print(f"   reduce defined -> clamp returned reduce's object: {clamped is minted}")
        ok &= clamped is minted
    else:
        good = (abs(clamped['point_j']-point) <= 1e-9 and abs(clamped['lower_j']-lo) <= 1e-9 and abs(clamped['upper_j']-hi) <= 1e-9)
        print(f"   clamp == exact extrema (1e-9): {good}")
        ok &= good
print("ALL_MATCH" if ok else "MISMATCH")
