"""R1: reviewer-built sweep. analysis clamp == e1b3a0510 oracle bit for bit; == origin/main where defined."""
import json, math, sys, itertools
from pathlib import Path
ROOT = Path(sys.argv[1]); sys.path.insert(0, str(ROOT))
import joulewise.reduce as R
from joulewise.bundle_read import TracePoint, Window
from joulewise.whole_window import _clamped_corner_composed_anchor_shift_envelope as A
sys.path.insert(0, str(ROOT))
from tests.test_whole_window_inverted_corner_clamp import oracle_module
O = oracle_module()._corner_composed_anchor_shift_envelope
M = R._corner_composed_anchor_shift_envelope

def ival(rows):
    return [TracePoint(t=(a+b)/2, power_w=p, support_start_s=a, support_end_s=b) for a,b,p in rows]
def pts(rows):
    return [TracePoint(t=(a+b)/2, power_w=p) for a,b,p in rows]
def rows_flat(o, n, w, p): return [(o+i*w, o+(i+1)*w, p) for i in range(n)]
def rows_rand(o, n, w, seed):
    v=seed; out=[]
    for i in range(n):
        v=(v*6364136223846793005+1442695040888963407)%(2**64); out.append((o+i*w,o+(i+1)*w, (v>>11)%7000/100.0))
    return out
def rows_bump(o, n, w, p):  # zeros, positive plateau in the middle, zeros
    return [(o+i*w, o+(i+1)*w, p if n//3 <= i < 2*n//3 else 0.0) for i in range(n)]

def same(a, b):
    if a is None or b is None: return a is b
    if a.keys() != b.keys(): return False
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, float) or isinstance(y, float):
            if not (x == y and math.copysign(1, x) == math.copysign(1, y)): return False
        elif x != y: return False
    return json.dumps(a) == json.dumps(b)

stats = {"inverted_defined":0, "noninverted_defined":0, "none":0, "point_at_lower":0, "point_at_upper":0, "point_at_both":0, "mismatch":0, "origin_mismatch":0, "cases":0}
bad = []
def check(label, contributions, bb, fb, sp):
    stats["cases"] += 1
    a = A(contributions, bb, fb, sp); o = O(contributions, bb, fb, sp); m = M(contributions, bb, fb, sp)
    if not same(a, o):
        stats["mismatch"] += 1; bad.append((label, a, o)); return
    if m is not None and not same(a, m):
        stats["origin_mismatch"] += 1; bad.append((label+" vs origin", a, m)); return
    if a is None: stats["none"] += 1; return
    if m is None: stats["inverted_defined"] += 1
    else: stats["noninverted_defined"] += 1
    if a["point_j"] == a["lower_j"] == a["upper_j"]: stats["point_at_both"] += 1
    elif a["point_j"] == a["lower_j"]: stats["point_at_lower"] += 1
    elif a["point_j"] == a["upper_j"]: stats["point_at_upper"] += 1

bound_sets = [(0.0,0.0,0.0),(0.01,0.02,0.0),(0.0566,0.02142716616057592,8.106231689453125e-06),(0.03,0.0665,1e-05),(0.001,0.1,0.05),(0.2,0.05,0.0)]
factors = [0.0, 1e-7, 0.25, 0.5, 0.9, 1-1e-6, 1-1e-9, 1.0, 1+1e-9, 1+1e-6, 1.1, 2.0, 10.0]
for epoch in (0.0, 1_700_000_000.123456, 1_784_491_122.85):
    for mk in (ival, pts):
        curves = [("flat", mk(rows_flat(epoch-1.0, 80, 0.05, 12.5))), ("rand", mk(rows_rand(epoch-1.0, 80, 0.05, 9))), ("bump", mk(rows_bump(epoch-1.0, 90, 0.05, 20.0))), ("zero", mk(rows_flat(epoch-1.0, 80, 0.05, 0.0)))]
        for cname, curve in curves:
            for bb, fb, sp in bound_sets:
                g = fb + sp
                for f in factors:
                    D = 2*g*f if g else 0.3*f
                    for start_off in (0.4, 0.4+1/3.0, 1.0):
                        s = epoch + start_off
                        short = Window(s, s+D); long = Window(s+1.2, s+1.9)
                        # long windows at offsets incommensurate with the 0.05 s sample width, so the clamped
                        # zero-length window's breakpoints cannot coincide with the long window's own
                        long2 = Window(s+0.9137, s+1.4421); long3 = Window(s-0.3719, s-0.0123)
                        for wins in ([short],[short,long],[long,short],[long],[short,long2],[long3,short],[long3,short,long2]):
                            check(f"{cname}/{mk.__name__}/e{epoch}/b{bb},{fb},{sp}/f{f}/o{start_off}/{len(wins)}w", [(curve, wins)], bb, fb, sp)
                        # two contributions, second from another curve with its own short window
                        other = mk(rows_rand(epoch-1.0, 80, 0.05, 77))
                        check(f"{cname}/2c/e{epoch}/b{bb},{fb},{sp}/f{f}", [(curve,[short]),(other,[Window(s+0.3, s+0.3+D)])], bb, fb, sp)
                        check(f"{cname}/2c-mixed/e{epoch}/b{bb},{fb},{sp}/f{f}", [(curve,[long]),(other,[Window(s+0.3, s+0.3+D)])], bb, fb, sp)
# windows in the all-zero region of the bump curve -> point == lower == upper == 0 (inverting and not)
for mk in (ival, pts):
    curve = mk(rows_bump(-1.0, 90, 0.05, 20.0))
    for D in (0.01, 0.05, 0.3):
        check(f"bump-zero-region/{mk.__name__}/D{D}", [(curve,[Window(-0.5, -0.5+D)])], 0.01, 0.03, 0.0)
    # window covering the plateau with slack > total bound: shifts never change energy -> point == lower == upper
    check(f"bump-cover/{mk.__name__}", [(curve,[Window(0.3, 2.3)])], 0.01, 0.03, 0.0)
# guards
c = ival(rows_flat(-1.0, 80, 0.05, 10.0))
for args in [
    ([(c,[Window(0.5,0.6)])], None, 0.1, 0.0), ([(c,[Window(0.5,0.6)])], 0.0, None, 0.0),
    ([(c,[Window(0.5,0.6)])], math.nan, 0.1, 0.0), ([(c,[Window(0.5,0.6)])], 0.0, math.inf, 0.0),
    ([(c,[Window(0.5,0.6)])], -1e-12, 0.1, 0.0), ([(c,[Window(0.5,0.6)])], 0.0, -1e-12, 0.0),
    ([(c,[Window(0.5,0.6)])], 0.0, 0.1, -1e-12), ([(c,[Window(0.5,0.6)])], 0.0, 0.1, math.inf),
    ([], 0.0, 0.1, 0.0), ([(c,[])], 0.0, 0.1, 0.0), ([([],[Window(0.5,0.6)])], 0.0, 0.1, 0.0),
    ([(c,[Window(0.5,0.6)]),(c,[])], 0.0, 0.1, 0.0),
    ([(ival(rows_flat(-1.0,80,0.05,10.0)[:40]+[(1.0,1.05,-1e-9)]+rows_flat(-1.0,80,0.05,10.0)[41:]),[Window(0.5,0.6)])], 0.0, 0.1, 0.0),
    ([(c,[Window(0.5,0.6)])], 5.0, 0.1, 0.0),          # bundle bound exceeds coverage -> None
    ([(c,[Window(2.95,2.96)])], 0.0, 0.1, 0.0),        # window at trace edge; coverage fails
    ([(c,[Window(10.0,10.05)])], 0.0, 0.1, 0.0),       # no overlap at all
    ([(c,[Window(0.6,0.5)])], 0.0, 0.1, 0.0),          # invalid (reversed) unshifted window
    ([(c,[Window(0.5,0.5)])], 0.0, 0.1, 0.0),          # zero-length unshifted window (inverts at corner)
    ([(c,[Window(0.5,0.6)])], 0.0, 0.0, 0.0),          # no edge bound at all
    ([(pts(rows_flat(-1.0,80,0.05,10.0)),[Window(0.5,0.6)])], 0.0, 0.1, 0.0),
]:
    check("guard", *args)
# epoch-scale rounding: durations that are exactly 2g nominally but round when placed at epoch
for epoch in (1_784_491_122.85, 1.7e9+0.1234567):
    curve = ival(rows_rand(epoch-1.0, 80, 0.05, 5))
    for bb, fb, sp in bound_sets[1:]:
        g = fb+sp
        for k in range(-8, 9):
            s = epoch + 0.37
            D = 2*g + k*math.ulp(2*g)*4
            check(f"ulp-edge/e{epoch}/g{g}/k{k}", [(curve,[Window(s, s+D)])], bb, fb, sp)
            e = s + 2*g
            check(f"ulp-edge-endpoint/e{epoch}/g{g}/k{k}", [(curve,[Window(s, e + k*math.ulp(e))])], bb, fb, sp)
print(json.dumps(stats, indent=1))
for b in bad[:20]: print("MISMATCH", b)
print("RESULT:", "PASS" if not bad else "FAIL")
