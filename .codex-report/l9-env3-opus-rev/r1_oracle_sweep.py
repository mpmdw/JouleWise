"""R1: analysis clamp vs e1b3a0510's patched reducer, bit for bit (reviewer-built sweep)."""
import itertools, json, math, random, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _oracle_load import load_e1b
import joulewise.reduce as R
from joulewise.bundle_read import TracePoint, Window
import joulewise.whole_window as W

e1b, sha = load_e1b()
CLAMP = W._clamped_corner_composed_anchor_shift_envelope
ORACLE = e1b._corner_composed_anchor_shift_envelope
print("e1b reduce.py sha256", sha)


def canon(v):
    if v is None:
        return None
    return [(k, struct.pack(">d", x).hex() if isinstance(x, float) else repr(x)) for k, x in v.items()]


def interval_curve(t0, n, dt, rng, power=None):
    pts = []
    for i in range(n):
        p = power(i) if power else rng.uniform(0.5, 20.0)
        s = t0 + i * dt
        pts.append(TracePoint(t=s + dt / 2, power_w=p, support_start_s=s, support_end_s=s + dt))
    return pts


def point_curve(t0, n, dt, rng, power=None):
    return [TracePoint(t=t0 + i * dt, power_w=(power(i) if power else rng.uniform(0.5, 20.0)))
            for i in range(n)]


cases = []
rng = random.Random(20261030)
for epoch in (0.0, 1.7617e9, 1793232000.123456):
    for kind, mk in (("interval", interval_curve), ("point", point_curve)):
        for dt in (0.01, 0.1, 0.0731):
            for fid, span, bb in ((0.03, 0.0, 0.0005), (0.0656, 0.0012, 0.00004), (0.07899607349394995, 0.0, 0.0)):
                edge = fid + span
                curve = mk(epoch, 400, dt, rng)
                c0 = epoch + 5.0
                lens = [2 * edge * f for f in (0.0, 0.25, 0.5, 0.999, 1 - 1e-9, 1 - 1e-12)]
                two = 2 * edge
                lens += [two, math.nextafter(two, 0), math.nextafter(two, 9), two * (1 + 1e-12), two * (1 + 1e-9),
                         two * 1.001, two * 3, 7.0]
                for L in lens:
                    for off in (0.0, dt / 3, 0.5 * dt):
                        s = c0 + off
                        w = Window(start_s=s, end_s=s + L)
                        cases.append((f"{kind}/single/e{epoch}/dt{dt}/edge{edge}/L{L!r}/o{off}", [(curve, [w])], bb, fid, span))
                        # multi-window: one short + long ones
                        ws = [w, Window(start_s=s + 1.0, end_s=s + 3.0), Window(start_s=s + 4.0, end_s=s + 4.0 + 2 * L)]
                        cases.append((f"{kind}/multi/e{epoch}/dt{dt}/edge{edge}/L{L!r}/o{off}", [(curve, ws)], bb, fid, span))
                        # multi-contribution (two sources)
                        curve2 = mk(epoch, 400, dt, rng)
                        cases.append((f"{kind}/twosrc/e{epoch}/dt{dt}/edge{edge}/L{L!r}/o{off}",
                                      [(curve, [w]), (curve2, [Window(start_s=s + 2.0, end_s=s + 2.0 + L)])], bb, fid, span))
                        # epoch-scale rounding: window built as absolute from start+duration in epoch seconds
                        a = epoch + 5.0 + off + 1e-7
                        cases.append((f"{kind}/epochround/e{epoch}/dt{dt}/edge{edge}/L{L!r}/o{off}",
                                      [(curve, [Window(start_s=a, end_s=a + L)])], bb, fid, span))
# zero-power region: point_j at lower bound / both bounds
for kind, mk in (("interval", interval_curve), ("point", point_curve)):
    zcurve = mk(0.0, 400, 0.05, rng, power=lambda i: 0.0)
    for L in (0.01, 0.2, 2.0):
        cases.append((f"{kind}/zero/L{L}", [(zcurve, [Window(start_s=5.0, end_s=5.0 + L)])], 0.001, 0.07, 0.0))
    step = mk(0.0, 400, 0.05, rng, power=lambda i: 0.0 if i < 100 else 10.0)
    for s in (4.9, 5.0, 5.05):
        for L in (0.05, 0.1, 1.0):
            cases.append((f"{kind}/step/s{s}/L{L}", [(step, [Window(start_s=s, end_s=s + L)])], 0.0, 0.03, 0.0))
    # zero bounds: lower == point == upper
    cases.append((f"{kind}/zerobounds", [(mk(0.0, 400, 0.05, rng), [Window(start_s=5.0, end_s=6.0)])], 0.0, 0.0, 0.0))
    cases.append((f"{kind}/zerobounds-zero-len", [(mk(0.0, 400, 0.05, rng), [Window(start_s=5.0, end_s=5.0)])], 0.0, 0.0, 0.0))
# guards
good = interval_curve(0.0, 400, 0.05, rng)
gw = [Window(start_s=5.0, end_s=5.1)]
neg = list(good); neg[50] = TracePoint(t=neg[50].t, power_w=-1e-9, support_start_s=neg[50].support_start_s, support_end_s=neg[50].support_end_s)
for name, args in {
    "none-bundle": ([(good, gw)], None, 0.07, 0.0),
    "none-fid": ([(good, gw)], 0.001, None, 0.0),
    "nan-bundle": ([(good, gw)], float("nan"), 0.07, 0.0),
    "inf-fid": ([(good, gw)], 0.001, float("inf"), 0.0),
    "neg-bundle": ([(good, gw)], -1e-12, 0.07, 0.0),
    "neg-fid": ([(good, gw)], 0.001, -1e-12, 0.0),
    "neg-span": ([(good, gw)], 0.001, 0.07, -1e-12),
    "nan-span": ([(good, gw)], 0.001, 0.07, float("nan")),
    "empty-contrib": ([], 0.001, 0.07, 0.0),
    "empty-curve": ([([], gw)], 0.001, 0.07, 0.0),
    "empty-windows": ([(good, [])], 0.001, 0.07, 0.0),
    "neg-power": ([(neg, gw)], 0.001, 0.07, 0.0),
    "no-overlap-after": ([(good, [Window(start_s=19.99, end_s=20.03)])], 0.001, 0.07, 0.0),
    "no-overlap-before": ([(good, [Window(start_s=-0.02, end_s=0.05)])], 0.001, 0.07, 0.0),
    "no-overlap-far": ([(good, [Window(start_s=100.0, end_s=100.1)])], 0.001, 0.07, 0.0),
    "already-inverted-input": ([(good, [Window(start_s=5.1, end_s=5.0)])], 0.001, 0.07, 0.0),
    "already-inverted-input-long": ([(good, [Window(start_s=6.0, end_s=5.0)])], 0.001, 0.07, 0.0),
    "huge-bound": ([(good, gw)], 1e308, 0.07, 0.0),
}.items():
    cases.append(("guard/" + name, *args))

mismatch, inverted_defined, origin_none_defined, n = [], 0, 0, 0
for name, contribs, bb, fid, span in cases:
    n += 1
    out = []
    for fn in (CLAMP, ORACLE):
        try:
            out.append(("ok", canon(fn(contribs, bb, fid, span))))
        except Exception as exc:  # noqa: BLE001
            out.append(("raise", type(exc).__name__))
    if out[0] != out[1]:
        mismatch.append((name, out))
    orig = R._corner_composed_anchor_shift_envelope(contribs, bb, fid, span)
    if orig is None and out[0][0] == "ok" and out[0][1] is not None:
        origin_none_defined += 1
        if "guard/" in name:
            print("GUARD DEFINED:", name)
print("cases", n, "mismatches", len(mismatch), "origin-None-but-clamp-defined", origin_none_defined)
for m in mismatch[:20]:
    print("MISMATCH", m)
guards = {name: CLAMP(c, b, f, s) for name, c, b, f, s in cases if name.startswith("guard/")}
print("guard results:", json.dumps({k: (None if v is None else "defined") for k, v in guards.items()}, sort_keys=True))
sys.exit(1 if mismatch else 0)
