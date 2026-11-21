"""Synthetic v2.2.1 description acceptance supplement. See DELTA.md for the RL-191 case map."""
from contextlib import contextmanager
import csv
from fractions import Fraction
from itertools import combinations, product
import json
import math
from pathlib import Path
import re
import tempfile
import unittest

import test_desc_looks_acceptance as frozen

S = 10**9
EPOCH = 1_800_000_000 * S
COLS = tuple(frozen.COLS)
RAW = (*COLS, "dc_in", "sidecar")
PRINTS = tuple(frozen.CHANNEL)
LOOKS = ("instrument", "stability")
NS = {"m2ns": -2, "m1ns": -1, "exact": 0, "p1ns": 1, "p2ns": 2}
WINDOWS = {
    "hold": (0, 600), "sd10": (0, 10), "sd40": (0, 40), "sd128": (0, 128),
    "recovery": (-10, 0), "mixed": (600, 606), "prefill": (602, 606),
    "level": (604, 606), "decode": (606, 610), "turn": (602, 611), "tail": (610, 611),
}


def offsets(period):
    return dict(NS, mtick=-period, ptick=period, m1s=-S, p1s=S)


def seconds(ns):
    """Exact decimal token for CSV/JSON. Input clocks are always integer ns."""
    whole, frac = divmod(abs(ns), S)
    return f"{'-' if ns < 0 else ''}{whole}.{frac:09d}"


def stamp(ns):
    return "ns@" + seconds(ns)


def encoded(meta):
    # json.dumps does not support raw decimal number tokens. Only markers
    # created by stamp() may be unquoted. No binary float is on this wire.
    return re.sub(rb'"ns@(-?\d+\.\d{9})"', rb'\1', json.dumps(meta).encode())


def ceil(q):
    return -(-q.numerator // q.denominator)


def expected_samples(a, b, split, slow, fast):
    s = max(a, min(split, b))
    return Fraction(s-a, slow) + Fraction(b-s, fast)


def count(stamps, a, b):
    return sum(a <= t < b for t in stamps)


def even(a, b, n):
    return [a + (2*i+1)*(b-a)//(2*n) for i in range(n)]


def with_probe(a, b, n, probe):
    inside = a <= probe < b
    if n == 0 and inside:
        # A zero-count tape cannot contain an in-window sample.
        return []
    other = even(a, b, n - int(inside))
    if probe in other:
        other[other.index(probe)] += 100_000  # distinct by 0.1 ms, even at Unix epoch
    return sorted([*other, probe])


def joined(rails):
    return sorted(set.intersection(*(set((a,b) for a,b,_ in rails[r]) for r in COLS)))


def judged_stamps(rails, dc, side, raw):
    if raw == "sidecar":
        return side
    if raw == "dc_in":
        return [s for s,_ in dc]
    if raw == "gpu_power":
        return [a for a,_,_ in rails[raw]]
    return [a for a,_ in joined(rails)]


def targets(raw):
    return {"cpu_power": ("rail_sum",), "ane_power": ("rail_sum",),
            "gpu_power": ("gpu_rail","rail_sum"), "dc_in": ("dc_in",),
            "sidecar": PRINTS}[raw]


def write_tape(folder, rails, dc, side, turn, first, last, slow=S,
               rail_tick=S//4, dc_tick=S//20, **overrides):
    # Exercise production parsing of the attested JSON metadata and CSV clocks.
    # A future parser may keep the original exact tokens here.
    bounds = sorted({(a,b) for rows in rails.values() for a,b,_ in rows})
    meta = dict(rail_manifest=list(COLS), rail_intervals=[[stamp(a),stamp(b)] for a,b in bounds],
                sidecar_times=list(map(stamp, side)), meter_times=[stamp(t) for t,_ in dc],
                meter_clean=True, meter_present=True,
                meter_counts=dict(decoded=len(dc),bad=0,usb_errors=0),
                sample_period_s=dict(hold=stamp(slow),rail_edge=stamp(rail_tick),dc_edge=stamp(dc_tick)),
                turn_start_s=stamp(turn), first_token_s=stamp(first), last_token_s=stamp(last),
                clock=dict(raw_anchor_s=1000,trace_anchor_s=stamp(turn-602*S)),
                sampling_started_raw_s=990, completion_log_raw_s=981, warmup_stage_raw_s=986,
                sensors=[dict(fan_keys={"left":800},T=40)],host_fan_keys=["left"])
    meta.update(overrides)
    paths = {n:folder/n for n in ("support.json", frozen.RAIL_FILE, frozen.DC_FILE)}
    paths["support.json"].write_bytes(encoded(meta))
    with paths[frozen.RAIL_FILE].open("w", newline="") as out:
        rows = csv.writer(out)
        rows.writerow(frozen.RAIL_HEADER)
        for a,b,r,v in sorted((a,b,r,v) for r,series in rails.items() for a,b,v in series):
            rows.writerow([seconds(a),seconds(b),seconds(b),"powermetrics",r,v])
    with paths[frozen.DC_FILE].open("w", newline="") as out:
        rows = csv.writer(out)
        rows.writerow(["epoch_s","watts"])
        rows.writerows((seconds(t),v) for t,v in dc)
    return paths


@contextmanager
def open_signal(paths):
    reader = frozen.executor()
    with paths["support.json"].open("rb") as stream:
        metadata, span = reader._support_metadata(stream)
        yield reader.Signals(metadata,paths,lambda:None,frozen.fixture_step3(),
                             sensor_source=(stream,span))


def report(signal, quiet_ns, look):
    detail = ({"quiet_spans_ns":[(quiet_ns,quiet_ns+600*S)]},None,None,None,
              {"nominal_prefill_tokens":19458,"realised_decode_tokens":512})
    return frozen.executor().print_leg(signal,detail,look=="instrument")


def ticks(raw):
    return S if raw=="sidecar" else S//20 if raw=="dc_in" else S//4


def window_case(test, phase, raw, edge, offset, delta, origin):
    a,b = [origin + t*S for t in WINDOWS[phase]]
    split = origin+602*S
    period = S if (a if edge=="left" else b-1)<split else ticks(raw)
    probe = (a if edge=="left" else b) + offsets(period)[offset]
    expected = expected_samples(a,b,split,S,ticks(raw))
    threshold = ceil(expected*99/100)
    n = threshold+delta
    chosen = with_probe(a,b,n,probe)
    def points(key):
        total = expected_samples(a,b,split,S,ticks(key))
        if key==raw or (key in COLS and raw in COLS):
            inside = chosen
        else:
            # Nominal start count, evenly distributed in each cadence segment.
            middle = max(a,min(split,b))
            inside = [*even(a,middle,ceil(Fraction(middle-a,S))),
                      *even(middle,b,ceil(Fraction(b-middle,ticks(key))))]
        # Bracket all trials outside the interval by less than a nominal period.
        # Guards and probes never collide for these offsets.
        return sorted(set([a-S//3,*inside,b+S//3]))
    side = points("sidecar")
    dc = [(t,40) for t in points("dc_in")]
    starts = points("gpu_power")
    # Keep separate component counts observable. An extra short row carries
    # just the two siblings when the selected rail is the scarce component.
    extra = a+(b-a)*1237//4093
    if raw in COLS:
        assert extra not in starts
        starts = sorted([*starts,extra])
    rails = {r:[(s,t,8) for s,t in zip(starts,starts[1:]+[starts[-1]+S//4])
                if not (r==raw and s==extra)] for r in COLS}
    observed = count(judged_stamps(rails,dc,side,raw),a,b)
    test.assertEqual(observed,n)
    reason = "coverage" if 100*observed<99*expected else None
    paths = write_tape(test.folder,rails,dc,side,split,split+4*S,split+8*S)
    with open_signal(paths) as sig:
        # These interval endpoints are exactly representable integer seconds.
        for ch in targets(raw):
            with test.subTest(channel=ch,expected_count=n):
                value = sig.average(ch,a//S,b//S)
                frozen.assert_scalar(test,value,reason)


def scored_hold(test, look, raw, edge, offset, delta):
    # Move the actual integer quiet-span record relative to a whole-second
    # observation. All other sample clocks are at least 1 ms from the probe.
    q = EPOCH - offsets(S)[offset]
    a,b = q,q+600*S
    at = EPOCH if edge=="left" else EPOCH+600*S
    n = 594+delta
    chosen = with_probe(a,b,n,at)
    before = list(range(EPOCH-10*S,EPOCH-2*S,S))
    after = list(range(EPOCH+602*S,EPOCH+614*S,S))
    # Outside guard stamps make DC brackets and point gaps independently good.
    def clocks(key):
        inside = chosen if key==raw or (key in COLS and raw in COLS) else even(a,b,600)
        return sorted(set([*before,a-S//3,*inside,b+S//3,*after]))
    starts = clocks("gpu_power")
    rails = {r:[(s,t,8) for s,t in zip(starts,starts[1:])] for r in COLS}
    dc = [(t,40) for t in clocks("dc_in")]
    side = clocks("sidecar")
    test.assertEqual(count(judged_stamps(rails,dc,side,raw),a,b),n)
    paths = write_tape(test.folder,rails,dc,side,EPOCH+603*S,EPOCH+607*S,EPOCH+611*S)
    with open_signal(paths) as sig:
        means = report(sig,q,look)["hold"]
    for ch in targets(raw):
        with test.subTest(channel=ch):
            expected = frozen.null("coverage") if n<594 else {"dc_in":40,"rail_sum":24,"gpu_rail":8}[ch]
            value = means[ch]["mean_w"]
            if n<594:
                test.assertEqual(value,expected)
            else:
                test.assertIn(type(value),(int,float),value)
                test.assertAlmostEqual(value,expected,delta=1e-8)


def translated_turn(test, look, millis, delta):
    # Two neighboring epochs straddle the exact binary-float exponent change
    # in audit 3. Clean H and the 5 W s answer are independent of translation.
    t = millis*1_000_000
    quiet = t-602*S
    b = t+5*S
    lead = list(range(quiet-10*S,t,S))
    side = [*lead,*range(t,b+2*S,S)]
    cuts = [*lead,*range(t,b+2*S,S//4)]
    rails = {r:[(a,z,8) for a,z in zip(cuts,cuts[1:])] for r in COLS}
    stamps = [*lead,*range(t,b+2*S,S//20)]
    for i in range(1-delta):
        stamps.remove(t+(31+20*i)*(S//20))
    dc = [(s,40+int(s>=t)) for s in stamps]
    test.assertEqual(count(stamps,t,b),99+delta)
    paths = write_tape(test.folder,rails,dc,side,t,t+2*S,t+4*S)
    with open_signal(paths) as sig:
        result = report(sig,quiet,look)["turn"]["energy_j"]["dc_in"]
    if delta<0:
        test.assertEqual(result,frozen.null("coverage"))
    else:
        test.assertIn(type(result),(int,float),result)
        test.assertAlmostEqual(result,5,delta=1e-8)


class Supplement(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)


def add(name, func, *args):
    def check(self):
        func(self,*args)
    check.__name__ = "test_" + name
    assert not hasattr(Supplement,check.__name__), name
    setattr(Supplement,check.__name__,check)


def register_time():
    for phase,raw,edge,off,d,era in product(WINDOWS,RAW,("left","right"),offsets(S),(-1,0,1),("local","epoch")):
        add(f"A_window_{phase}_{raw}_{edge}_{off}_n{d+1}_{era}",window_case,
            phase,raw,edge,off,d,0 if era=="local" else EPOCH)
    for look,raw,edge,off,d in product(LOOKS,("sidecar","dc_in","gpu_power"),("left","right"),
                                       offsets(S),(-1,0,1)):
        add(f"A_record_{look}_{raw}_{edge}_{off}_n{d+1}",scored_hold,look,raw,edge,off,d)
    for look,millis,d in product(LOOKS,(1023005,1024005,1800000000005,1800000001005),(-1,0,1)):
        add(f"A_translate_{look}_{millis}_n{d+1}",translated_turn,look,millis,d)


register_time()

BASE = dict(zip(COLS,(8,12,4)))
WEIGHT = dict(zip(COLS,(1,2,3)))
T = 602*S
END = T+4*S


def elevation(shape, ns):
    u = Fraction(ns-T,S)
    if shape=="identity":
        return 0
    if shape=="flat":
        return 4
    if shape=="negative":
        return -2
    if shape=="step":
        return 2 if u<2 else 6
    if shape=="ramp":
        return 2+2*u
    raise ValueError(shape)


def energy_tape(shape, rail_mask, dc_mask):
    # Eight half-second strata. Bit zero delays the first interval. Each
    # other bit removes the last eighth-second of that stratum. No rail
    # starts are lost. Rail powers are interval means (a staircase on ramp).
    p = S//2
    prefix = list(range(-10*S,T,S))
    rails = {}
    for r in COLS:
        series = [(s,s+S,BASE[r]) for s in prefix]
        for i in range(8):
            nominal = T+i*p
            a,b = nominal,nominal+p
            if rail_mask & (1<<i):
                if i==0:
                    a += p//4
                else:
                    b -= p//4
            watts = BASE[r]+WEIGHT[r]*elevation(shape,nominal+p//2)
            series.append((a,b,watts))
        series.extend((t,t+p,BASE[r]) for t in range(END,END+2*S,p))
        rails[r] = series
    dc_times = set(range(T,END+2*S,S//4))
    for i in range(8):
        if dc_mask & (1<<i):
            s = T+i*p
            if i==3:
                # Move the predecessor of the step at u=2; this changes the
                # clipped trapezoid on a step, while a linear ramp is invariant.
                s += p//2
            if i==7:
                # Displace the right bracket beyond the cut and move the
                # last in-window point back. The clipped end has no sample.
                dc_times.remove(END)
                dc_times.add(END+p//4)
                s = END-S//4
                dc_times.remove(s)
                dc_times.add(s-p//4)
            else:
                dc_times.remove(s)
                dc_times.add(s+p//4)
    # Begin the DC signal before the turn so start gaps require clipping.
    # The H window ends at 600 and retains its constant bracketing point.
    dc = [(s,40+(elevation(shape,s) if s>600*S else 0))
          for s in sorted([*prefix,*dc_times])]
    side = list(range(-10*S,END+2*S,S))
    return rails,dc,side


def wire_watts(w):
    # All planted powers are dyadic and small enough for exact binary64.
    assert Fraction(float(w))==w
    return float(w)


def exact_energy(rails, dc, a, b):
    # Do not call the executor or the pinned loader for an expected result.
    def rectangles(rows,h):
        return sum(Fraction(max(0,min(b,z)-max(a,s)),S)*(v-h) for s,z,v in rows)
    lookup = {r:{(s,z):v for s,z,v in rows} for r,rows in rails.items()}
    total = [(s,z,sum(lookup[r][s,z] for r in COLS)) for s,z in joined(rails)]
    trapezoids = Fraction(0)
    for (s,w0),(z,w1) in zip(dc,dc[1:]):
        lo,hi = max(a,s),min(b,z)
        if lo>=hi:
            continue
        slope = Fraction(w1-w0,z-s)
        left,right = w0-40+slope*(lo-s),w0-40+slope*(hi-s)
        trapezoids += Fraction(hi-lo,2*S)*(left+right)
    return dict(gpu_rail=rectangles(rails["gpu_power"],12),
                rail_sum=rectangles(total,24),dc_in=trapezoids)


def assert_energy(test, look, shape, rails, dc, side, period=S//2):
    oracle = exact_energy(rails,dc,T,END)
    if shape=="identity":
        test.assertEqual(oracle,dict.fromkeys(PRINTS,0))
    wire_rails = {r:[(s,z,wire_watts(w)) for s,z,w in rows] for r,rows in rails.items()}
    paths = write_tape(test.folder,wire_rails,[(s,wire_watts(w)) for s,w in dc],side,
                       T,T+S,END-S,rail_tick=period,dc_tick=S//4)
    with open_signal(paths) as sig:
        printed = report(sig,0,look)
    for ch,h in zip(PRINTS,(12,24,40)):
        with test.subTest(channel=ch,exact_j=str(oracle[ch])):
            test.assertEqual(printed["hold"][ch]["mean_w"],h)
            v = printed["turn"]["energy_j"][ch]
            test.assertIn(type(v),(int,float),v)
            # Dyadic rails and identity have exact answers. Non-dyadic DC
            # clipping permits arithmetic roundoff only, never admission slack.
            test.assertAlmostEqual(v,float(oracle[ch]),delta=0 if oracle[ch]==0 else 1e-10)


def energy_case(test, look, shape, rm, dm):
    rails,dc,side = energy_tape(shape,rm,dm)
    for r in COLS:
        test.assertEqual(count([a for a,b,w in rails[r]],T,END),8)
    test.assertEqual(count([s for s,_ in dc],T,END),16)
    assert_energy(test,look,shape,rails,dc,side)


def component_case(test, look, shape, raw, placement):
    # 99/100 rows is admissible. A missing CPU/ANE row removes the whole
    # corresponding triple even though GPU still supplies that rectangle.
    rails,dc,side = energy_tape(shape,0,0)
    tick = S//25
    missing_index = {"start":0,"middle":49,"end":99}[placement]
    for r in COLS:
        body = []
        for i in range(100):
            if r==raw and i==missing_index:
                continue
            a = T+i*tick
            # Powers on the denser grid also have exact on-wire values.
            watts = BASE[r]+WEIGHT[r]*elevation(shape,T+(i//25)*S)
            body.append((a,a+tick,watts))
        rails[r] = [row for row in rails[r] if row[1]<=T] + body + [row for row in rails[r] if row[0]>=END]
    test.assertEqual(count([a for a,b in joined(rails)],T,END),99)
    assert_energy(test,look,shape,rails,dc,side,tick)


def register_energy():
    # Exhaust all combined start/middle/end masks independently on rails and
    # DC. For the identity, also exhaust every eight-stratum mask per stream.
    named = (0,1,8,128,9,129,136,137)
    for look,shape,rm,dm in product(LOOKS,("identity","flat","negative","step","ramp"),named,named):
        add(f"B_{look}_{shape}_r{rm:02x}_d{dm:02x}",energy_case,look,shape,rm,dm)
    for look,mask in product(LOOKS,range(256)):
        if mask not in named:
            add(f"B_identity_{look}_mask{mask:02x}",energy_case,look,"identity",mask,mask)
    for look,shape,raw,loc in product(LOOKS,("identity","flat","step","ramp"),COLS,("start","middle","end")):
        add(f"B_triple_{look}_{shape}_{raw}_{loc}",component_case,look,shape,raw,loc)


register_energy()

def scored_edge(test, phase, look, raw, edge, off, d, origin):
    turn,first,last = (origin+i*S for i in (602,606,610))
    a,b = (last if phase=="tail" else turn),last+S
    p = ticks(raw)
    probe = (a if edge=="left" else b)+offsets(p)[off]
    expected = Fraction(b-a,p)
    n = ceil(expected*99/100)+d
    chosen = with_probe(a,b,n,probe)

    def series(key):
        period = ticks(key)
        central = chosen if key==raw or (key in COLS and raw in COLS) else even(a,b,(b-a)//period)
        # Reserve both adjacent phases enough samples to pass independently.
        # Leave space around the two edges so that no CSV row collapses to
        # zero duration when read on an old binary64 clock.
        lead = range(origin-10*S,origin+601*S,S)
        pre = range(origin+601*S,a-period//4,period//2)
        post = range(b+period//4,b+3*S,period//2)
        return sorted({*lead,*pre,a-period//4,*central,*post})
    side = series("sidecar")
    dc = [(s,int(s>origin+600*S)) for s in series("dc_in")]
    starts = series("gpu_power")
    extra = None
    if raw in COLS and n < ceil(expected*99/100):
        extra = a + (b-a)*1237//4093
        assert extra not in starts
        starts = sorted([*starts,extra])
    rails = {r:[(s,z,int(s>=origin+600*S)) for s,z in zip(starts,starts[1:])
                if not (r==raw and s==extra)] for r in COLS}
    test.assertEqual(count(judged_stamps(rails,dc,side,raw),a,b),n)
    paths = write_tape(test.folder,rails,dc,side,turn,first,last)
    with open_signal(paths) as sig:
        printed = report(sig,origin,look)
    bad = n*100<99*expected
    if phase=="turn":
        for ch in targets(raw):
            with test.subTest(channel=ch):
                value = printed["turn"]["energy_j"][ch]
                if bad:
                    test.assertEqual(value,frozen.null("coverage"))
                else:
                    test.assertIn(type(value),(int,float),value)
                    test.assertAlmostEqual(value,27 if ch=="rail_sum" else 9,delta=1e-8)
    else:
        for ch in PRINTS[:2]:
            with test.subTest(channel=ch):
                affected = ch in targets(raw) or raw=="dc_in"
                want = frozen.null("coverage") if bad and affected else frozen.null("over 1 s",bound_s=1)
                test.assertEqual(printed["edges"]["decode_end_lag_s"][ch],want)


def segments(a,b,hole,where,n):
    """Exactly n disjoint sample intervals tile the complement of one hole."""
    if where=="start":
        ranges = [(a+hole,b,n)]
    elif where=="end":
        ranges = [(a,b-hole,n)]
    else:
        left = a+(b-a-hole)//2
        ranges = [(a,left,n//2),(left+hole,b,n-n//2)]
    out = []
    for lo,hi,k in ranges:
        marks = [lo+i*(hi-lo)//k for i in range(k+1)]
        out.extend(zip(marks,marks[1:]))
    return out


def stamp_gap(a,b,hole,where,n):
    # The two endpoints of the wide consecutive-point pair are observations.
    # A leading or trailing pair straddles the integration boundary.
    guard = min(S//8,hole//4)
    if where=="start":
        first = a+hole-guard
        return [a-guard,first,*even(first,b,n-1),b+S//8]
    if where=="end":
        last = b+guard-hole
        return [a-S//8,*even(a,last,n-1),last,b+guard]
    lo = a+(b-a-hole)//2
    return [a-S//8,*even(a,lo,n//2-1),lo,lo+hole,
            *even(lo+hole,b,n-n//2-1),b+S//8]


def gap_boundary(test, raw, period, where, label, delta, origin):
    a,b = origin+602*S,origin+622*S
    rail = raw in COLS
    maximum = max(S,5*period) if rail else 2*S
    hole = maximum+offsets(period)[label]
    nominal = Fraction(b-a,period)
    n = ceil(nominal*99/100)+delta
    if rail:
        spans = segments(a,b,hole,where,n)
        lengths = [spans[0][0]-a,b-spans[-1][1],*(y-x for (_,x),(y,_) in zip(spans,spans[1:]))]
        test.assertEqual(max(lengths),hole)
    else:
        spans = segments(a,b,0,"start",80)
    rails = {r:[(x,y,1) for x,y in spans] for r in COLS}
    healthy = [a-S//4,*even(a,b,80),b+S//4]
    bad_grid = None if rail else stamp_gap(a,b,hole,where,n)
    if bad_grid:
        test.assertEqual(max(y-x for x,y in zip(bad_grid,bad_grid[1:])),hole)
    dc = [(t,1) for t in (bad_grid if raw=="dc_in" else healthy)]
    side = bad_grid if raw=="sidecar" else healthy
    test.assertEqual(count(judged_stamps(rails,dc,side,raw),a,b),n)
    paths = write_tape(test.folder,rails,dc,side,a,a+4*S,b-S,
                       slow=period if raw=="sidecar" else S,
                       rail_tick=period if rail else S//4,dc_tick=period if raw=="dc_in" else S//4)
    reason = "coverage" if 100*n<99*nominal else "meter_gap" if hole>maximum else None
    with open_signal(paths) as sig:
        for ch in targets(raw):
            with test.subTest(channel=ch,gap_ns=hole,eligible_count=n):
                frozen.assert_scalar(test,sig.average(ch,a//S,b//S),reason)


def register_edges():
    pairs = (("turn","instrument"),("turn","stability"),("tail","instrument"))
    for (phase,look),raw,edge,off,d,era in product(pairs,RAW,("left","right"),offsets(S),(-1,0,1),("local","epoch")):
        add(f"A_print_{phase}_{look}_{raw}_{edge}_{off}_n{d+1}_{era}",scored_edge,
            phase,look,raw,edge,off,d,EPOCH if era=="epoch" else 0)
    rates = [(r,p) for r in COLS for p in (S//10,S//5,S//4)] + [("dc_in",S//4),("sidecar",S//4)]
    for (raw,p),where,off,d,era in product(rates,("start","middle","end"),offsets(S),(-1,0,1),("local","epoch")):
        add(f"A_u1_{raw}_{p}_{where}_{off}_n{d+1}_{era}",gap_boundary,
            raw,p,where,off,d,EPOCH if era=="epoch" else 0)


register_edges()

# Normalized admission causes. Absence necessarily removes all DC brackets
# and observations. Distinguish that state from a dirty, populated stream.
COUNTS = {"own_count","side_count"}
GAPS = {"own_gap","side_gap","left_bracket","right_bracket"}
# The original shared scenarios below also serve cases whose expectations did
# not change. Registration selects the ruled scenario only for a former skip.
def defer(test, key):
    test.fail("Unresolved v2.2 scenario selected by registration: " + key)


# RL-191 §1.1, §1.3 and §1.4. Both operands are independently established by
# the fixture. Select the first applicable reason without consulting the output.
REASON_RANK = (
    "rail_manifest", "meter_absent", "meter_contaminated", "coverage", "meter_gap",
    "nonpositive_level", "nonpositive_denominator", "crossed_before_span", "over 1 s",
)


def ranked_reason(*operand_reasons):
    return next(reason for reason in REASON_RANK if reason in operand_reasons)


def admission_faults(ch):
    common = ("own_count","side_count","own_gap","side_gap")
    if ch=="dc_in":
        return (*common,"left_bracket","right_bracket","absent","dirty")
    return (*common,"manifest") if ch=="rail_sum" else common


def admission_case(test, ch, pair):
    a,b = T,T+20*S
    faults = set(pair)
    n = 80 if "own_count" not in faults else 79
    side_n = 20 if "side_count" not in faults else 19
    rail = ch!="dc_in"
    spans = segments(a,b,3*S if rail and "own_gap" in faults else 0,"middle",n if rail else 80)
    rails = {r:[(s,z,1) for s,z in spans] for r in COLS}
    def point_grid(k,broken):
        return stamp_gap(a,b,3*S,"middle",k) if broken else [a-S//8,*even(a,b,k),b+S//8]
    side = point_grid(side_n,"side_gap" in faults)
    values = point_grid(n if not rail else 80,not rail and "own_gap" in faults)
    if "left_bracket" in faults:
        values = [s for s in values if s>=a]
    if "right_bracket" in faults:
        values = [s for s in values if s<b]
    dc = [(s,40) for s in values] if "absent" not in faults else []
    paths = write_tape(test.folder,rails,dc,side,a,a+3*S,b-S,dc_tick=S//4,
                       rail_manifest=list(reversed(COLS)) if "manifest" in faults else list(COLS),
                       meter_present="absent" not in faults,meter_clean="dirty" not in faults)
    test.assertEqual(count(side,a,b),side_n)
    test.assertEqual(count(judged_stamps(rails,dc,side,"dc_in" if not rail else "cpu_power"),a,b),
                     0 if "absent" in faults else n)
    with open_signal(paths) as sig:
        v = sig.average(ch,a//S,b//S)
    if "absent" in faults or ("dirty" in faults and len(faults)>1):
        test.assertIsNone(v["value"])
        test.assertNotIn("bound_s",v)
        defer(test,"health")
    reason = ("rail_manifest" if "manifest" in faults else "coverage" if faults & COUNTS else
              "meter_gap" if faults & GAPS else "meter_contaminated" if "dirty" in faults else None)
    frozen.assert_scalar(test,v,reason)


def admission_case_rl191(test, ch, pair):
    a,b = T,T+20*S
    faults = set(pair)
    n = 80 if "own_count" not in faults else 79
    side_n = 20 if "side_count" not in faults else 19
    rail = ch!="dc_in"
    spans = segments(a,b,3*S if rail and "own_gap" in faults else 0,"middle",n if rail else 80)
    rails = {r:[(s,z,1) for s,z in spans] for r in COLS}
    def point_grid(k,broken):
        return stamp_gap(a,b,3*S,"middle",k) if broken else [a-S//8,*even(a,b,k),b+S//8]
    side = point_grid(side_n,"side_gap" in faults)
    values = point_grid(n if not rail else 80,not rail and "own_gap" in faults)
    if "left_bracket" in faults:
        values = [s for s in values if s>=a]
    if "right_bracket" in faults:
        values = [s for s in values if s<b]
    dc = [(s,40) for s in values] if "absent" not in faults else []
    paths = write_tape(test.folder,rails,dc,side,a,a+3*S,b-S,dc_tick=S//4,
                       rail_manifest=list(reversed(COLS)) if "manifest" in faults else list(COLS),
                       meter_present="absent" not in faults,meter_clean="dirty" not in faults)
    test.assertEqual(count(side,a,b),side_n)
    test.assertEqual(count(judged_stamps(rails,dc,side,"dc_in" if not rail else "cpu_power"),a,b),
                     0 if "absent" in faults else n)
    with open_signal(paths) as sig:
        v = sig.average(ch,a//S,b//S)
    # RL-191 §1.2. A stream veto precedes every count, gap and bracket test.
    reason = "meter_absent" if "absent" in faults else "meter_contaminated"
    test.assertEqual(v, frozen.null(reason))


def set_hold_fault(leg,kind):
    if kind=="coverage":
        leg.omit("sidecar",range(50,400,50))
    if kind=="meter_gap":
        leg.omit("sidecar",[100,101])
    if kind=="rail_manifest":
        leg.meta["rail_manifest"] = list(reversed(COLS))


def physical_tail(test, hold, tail, end, raw):
    leg = frozen.TraceLeg(test.folder)
    set_hold_fault(leg,hold)
    leg.meta["rail_intervals"] = [row for row in leg.meta["rail_intervals"] if row[1]<=end]
    leg.rows[frozen.RAIL_FILE] = [r for r in leg.rows[frozen.RAIL_FILE] if float(r["interval_end_s"])<=end]
    if "count" in tail:
        leg.omit(raw,[610.25])
    if "gap" in tail:
        # Right point brackets the interval but is 3 s from the previous one.
        leg.meta["sidecar_times"] = [t for t in leg.meta["sidecar_times"] if t<end]+[end+3]
    obj = frozen.print_one(leg.signal(),frozen.IDS[0])
    ch = "gpu_rail" if raw=="gpu_power" else "rail_sum"
    h = obj["hold"][ch]["mean_w"]
    frozen.assert_scalar(test,h,None if hold=="ok" else hold)
    v = obj["edges"]["rail_return_censor_s"][ch]
    if hold=="rail_manifest":
        test.assertEqual(v["reason"],"rail_manifest")
        test.assertIsNone(v["value"])
        defer(test,"manifest_tail")
    if tail=="ok" and hold!="ok":
        test.assertIsNone(v["value"])
        defer(test,"clean_tail")
    reason = "coverage" if "count" in tail else "meter_gap" if "gap" in tail else "stream_end"
    test.assertEqual(v,frozen.null(reason,bound_s=end-610))


def physical_tail_rl191(test, hold, tail, end, raw):
    leg = frozen.TraceLeg(test.folder)
    set_hold_fault(leg,hold)
    leg.meta["rail_intervals"] = [row for row in leg.meta["rail_intervals"] if row[1]<=end]
    leg.rows[frozen.RAIL_FILE] = [r for r in leg.rows[frozen.RAIL_FILE] if float(r["interval_end_s"])<=end]
    if "count" in tail:
        leg.omit(raw,[610.25])
    if "gap" in tail:
        # Right point brackets the interval but is 3 s from the previous one.
        leg.meta["sidecar_times"] = [t for t in leg.meta["sidecar_times"] if t<end]+[end+3]
    obj = frozen.print_one(leg.signal(),frozen.IDS[0])
    ch = "gpu_rail" if raw=="gpu_power" else "rail_sum"
    h = obj["hold"][ch]["mean_w"]
    frozen.assert_scalar(test,h,None if hold=="ok" else hold)
    v = obj["edges"]["rail_return_censor_s"][ch]
    # RL-191 §1.5. A manifest veto or a clean tail with a refused hold
    # carries the stamp-only EOF bound, even when no threshold was readable.
    test.assertEqual(v, frozen.null(hold, bound_s=end - 610))


def recovery_pair(test, left, right):
    # Natural clean threshold and a passing successor; two different causes
    # on W0 must be counted once, in the recovery spelling of the table.
    leg,start,_ = frozen.recovery_fixture(test.folder,0,10)
    pair = {left,right}
    if "own_count" in pair:
        leg.omit("gpu_power",[start+9])
    if "side_count" in pair:
        leg.omit("sidecar",[start+7])
    if "own_gap" in pair:
        frozen.plant_rail_gap(leg,"gpu_power",start)
    if "side_gap" in pair:
        frozen.shift_points(leg,"sidecar",start)
    edges = frozen.print_one(leg.signal(),frozen.IDS[0])["edges"]
    reason = "coverage" if pair & COUNTS else "gap_over_u1"
    for ch in PRINTS[:2]:
        with test.subTest(channel=ch):
            test.assertEqual(edges["recovery_s"][ch],19)
            test.assertEqual(edges["recovery_skipped_windows"][ch],1)
            test.assertEqual(edges["recovery_skip_reasons"][ch],[reason])


def dependent(test, dc_fault, rail_fault, print_name, ch):
    # Distinct faults in the same physical phase; use the actual energy and
    # gain operands to verify that the intended collision was reached.
    leg = frozen.TraceLeg(test.folder)
    raw = "gpu_power" if ch=="gpu_rail" else "ane_power"
    if dc_fault=="coverage":
        leg.omit("dc_in",[607,608,609])
    elif dc_fault=="meter_gap":
        # Leave all 80 decode points, move them on either side of a 2.25 s
        # hole. Also retain both brackets and keep the independent turn count.
        rows = [r for r in leg.rows[frozen.DC_FILE] if not 606<=float(r["epoch_s"])<610]
        marks = stamp_gap(606*S,610*S,9*S//4,"middle",80)[1:-1]
        rows += [dict(epoch_s=seconds(s),watts=55) for s in marks]
        leg.rows[frozen.DC_FILE] = sorted(rows,key=lambda r:float(r["epoch_s"]))
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in leg.rows[frozen.DC_FILE]]
    elif dc_fault=="meter_contaminated":
        leg.meta["meter_clean"] = False
    if rail_fault=="coverage":
        leg.omit(raw,[607.25])
    elif rail_fault=="meter_gap":
        # A 1.5 s uncovered run despite a full decode count at 4 Hz.
        rowset = [r for r in leg.rows[frozen.RAIL_FILE] if not 606<=float(r["interval_start_s"])<610]
        spans = segments(606*S,610*S,3*S//2,"middle",16)
        leg.meta["rail_intervals"] = sorted([r for r in leg.meta["rail_intervals"] if not 606<=r[0]<610]
                                            + [[s/S,z/S] for s,z in spans])
        for s,z in spans:
            for r,w in zip(COLS,(12,20,6)):
                rowset.append(dict(zip(frozen.RAIL_HEADER,(s/S,z/S,z/S,"powermetrics",r,w))))
        leg.rows[frozen.RAIL_FILE] = sorted(rowset,key=lambda r:float(r["interval_start_s"]))
    elif rail_fault=="rail_manifest":
        leg.meta["rail_manifest"] = list(reversed(COLS))
    elif rail_fault=="nonpositive_denominator":
        for r in leg.rows[frozen.RAIL_FILE]:
            if r["source"]=="powermetrics" and float(r["interval_start_s"])>=602:
                r["power_w"] = 0
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    ratio = printed["turn"]["ratios"][ch] if print_name=="turn" else printed["gain"]["decode_gain"][ch]
    for operand,why in (("numerator",dc_fault),("denominator",rail_fault)):
        if why=="nonpositive_denominator":
            test.assertLessEqual(ratio[operand],0)
        else:
            frozen.assert_scalar(test,ratio[operand],None if why=="ok" else why)
    causes = {dc_fault,rail_fault}-{"ok"}
    if len(causes)>1:
        test.assertIsNone(ratio["value"])
        test.assertNotIn("bound_s",ratio)
        defer(test,"nonpositive" if "nonpositive_denominator" in causes else "operands")
    if causes:
        reason, = causes
        test.assertEqual({k:v for k,v in ratio.items() if k not in ("numerator","denominator")},frozen.null(reason))
    else:
        test.assertAlmostEqual(ratio["value"],ratio["numerator"]/ratio["denominator"])


def dependent_rl191(test, dc_fault, rail_fault, print_name, ch):
    # Distinct faults in the same physical phase; use the actual energy and
    # gain operands to verify that the intended collision was reached.
    leg = frozen.TraceLeg(test.folder)
    raw = "gpu_power" if ch=="gpu_rail" else "ane_power"
    if dc_fault=="coverage":
        leg.omit("dc_in",[607,608,609])
    elif dc_fault=="meter_gap":
        # Leave all 80 decode points, move them on either side of a 2.25 s
        # hole. Also retain both brackets and keep the independent turn count.
        rows = [r for r in leg.rows[frozen.DC_FILE] if not 606<=float(r["epoch_s"])<610]
        marks = stamp_gap(606*S,610*S,9*S//4,"middle",80)[1:-1]
        rows += [dict(epoch_s=seconds(s),watts=55) for s in marks]
        leg.rows[frozen.DC_FILE] = sorted(rows,key=lambda r:float(r["epoch_s"]))
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in leg.rows[frozen.DC_FILE]]
    elif dc_fault=="meter_contaminated":
        leg.meta["meter_clean"] = False
    if rail_fault=="coverage":
        leg.omit(raw,[607.25])
    elif rail_fault=="meter_gap":
        # A 1.5 s uncovered run despite a full decode count at 4 Hz.
        rowset = [r for r in leg.rows[frozen.RAIL_FILE] if not 606<=float(r["interval_start_s"])<610]
        spans = segments(606*S,610*S,3*S//2,"middle",16)
        leg.meta["rail_intervals"] = sorted([r for r in leg.meta["rail_intervals"] if not 606<=r[0]<610]
                                            + [[s/S,z/S] for s,z in spans])
        for s,z in spans:
            for r,w in zip(COLS,(12,20,6)):
                rowset.append(dict(zip(frozen.RAIL_HEADER,(s/S,z/S,z/S,"powermetrics",r,w))))
        leg.rows[frozen.RAIL_FILE] = sorted(rowset,key=lambda r:float(r["interval_start_s"]))
    elif rail_fault=="rail_manifest":
        leg.meta["rail_manifest"] = list(reversed(COLS))
    elif rail_fault=="nonpositive_denominator":
        for r in leg.rows[frozen.RAIL_FILE]:
            if r["source"]=="powermetrics" and float(r["interval_start_s"])>=602:
                r["power_w"] = 0
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    ratio = printed["turn"]["ratios"][ch] if print_name=="turn" else printed["gain"]["decode_gain"][ch]
    for operand,why in (("numerator",dc_fault),("denominator",rail_fault)):
        if why=="nonpositive_denominator":
            test.assertLessEqual(ratio[operand],0)
        else:
            frozen.assert_scalar(test,ratio[operand],None if why=="ok" else why)
    # RL-191 §1.3. A measured nonpositive denominator is preserved even
    # when the refused numerator supplies the ratio's reason.
    reason = ranked_reason(dc_fault, rail_fault)
    payload = {k: v for k, v in ratio.items() if k not in ("numerator", "denominator")}
    test.assertEqual(payload, frozen.null(reason))


def floor_pair(test, decode, sd):
    leg = frozen.TraceLeg(test.folder)
    if sd=="fewer_than_two":
        # Redistribute 59 samples: H passes exactly, but only tile 59 can
        # estimate a 10 s mean. No sample gap exceeds 2 s.
        leg.omit("sidecar",range(5,595,10))
        leg.meta["sidecar_times"] = sorted(leg.meta["sidecar_times"]+[590+i/64 for i in range(1,60)])
    if decode=="coverage":
        leg.omit("gpu_power",[608])
    if decode=="meter_gap":
        # The full-count common sidecar has no sample inside (606.25,608.5).
        leg.meta["sidecar_times"] = [t for t in leg.meta["sidecar_times"] if not 606.25<t<608.5]
    if decode=="nonpositive":
        for r in leg.rows[frozen.RAIL_FILE]:
            if r["rail"]=="gpu_power" and 606<=float(r["interval_start_s"])<610:
                r["power_w"]=0
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    h = printed["hold"]["gpu_rail"]
    frozen.assert_scalar(test,h["mean_w"],None)
    if sd=="fewer_than_two":
        test.assertEqual(h["kept"][0],1)
        test.assertEqual(h["sd10_w"],frozen.null("fewer_than_two"))
    watts = printed["gain"]["decode_w"]["gpu_rail"]
    frozen.assert_scalar(test,watts,decode if decode in ("coverage","meter_gap") else None)
    if decode=="nonpositive":
        test.assertLessEqual(watts,0)
    reason = decode if decode in ("coverage","meter_gap") else (
        "decode_or_sd_undefined" if decode=="nonpositive" or sd=="fewer_than_two" else None)
    frozen.assert_scalar(test,printed["gain"]["floor_tokens"]["gpu_rail"][0],reason)


def cross_pair(test, bad, crossing):
    # Both members of a lag can independently supply a terminal condition.
    leg = frozen.TraceLeg(test.folder)
    if crossing=="rail":
        for row in leg.rows[frozen.RAIL_FILE]:
            if row["rail"]=="gpu_power" and float(row["interval_start_s"])>=610:
                row["power_w"]=0
        if bad=="coverage":
            leg.omit("dc_in",[610.5])
        else:
            rows = leg.rows[frozen.DC_FILE]
            rows[-2]["epoch_s"],rows[-1]["epoch_s"]=614,614.05
            leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    else:
        for row in leg.rows[frozen.DC_FILE]:
            if float(row["epoch_s"])>=610:
                row["watts"]=0
        leg.omit("gpu_power",[610.5])
    e = frozen.print_one(leg.signal(),frozen.IDS[0])["edges"]
    # RL-191 §1.4. The opposite interval refusal outranks crossed_before_span.
    test.assertEqual(e["decode_end_lag_s"]["gpu_rail"], frozen.null(bad))


def endpoint_case(test):
    leg = frozen.TraceLeg(test.folder)
    rows = leg.rows[frozen.DC_FILE]
    for row in rows:
        if float(row["epoch_s"])>=610:
            row["watts"]=60
    rows[-2].update(epoch_s=611,watts=40)
    leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    # RL-191 §1.6. The 60-to-40 W segment reaches 49.6875 W at
    # 610.97578125 s. Subtract the two rail crossings at 610.25 and 610.5.
    lags = frozen.print_one(leg.signal(), frozen.IDS[0])["edges"]["decode_end_lag_s"]
    for ch, expected in (("gpu_rail", 0.72578125), ("rail_sum", 0.47578125)):
        with test.subTest(channel=ch):
            test.assertIn(type(lags[ch]), (int, float), lags[ch])
            test.assertAlmostEqual(lags[ch], expected, delta=0.5 / S)


def register_reasons():
    for ch in PRINTS:
        opts = admission_faults(ch)
        for q in [(),*((a,) for a in opts),*combinations(opts,2)]:
            # An absent stream has no observable pair of points forming an
            # own gap. It cannot also be a present dirty stream.
            if "absent" in q and ("own_gap" in q or "dirty" in q):
                continue
            ruled = "absent" in q or ("dirty" in q and len(q) > 1)
            scenario = admission_case_rl191 if ruled else admission_case
            add(f"C_interval_{ch}_{'_'.join(q) or 'clean'}",scenario,ch,q)
    for raw,hold,tail,end in product(COLS,("ok","coverage","meter_gap","rail_manifest"),
                                      ("ok","count","gap","count_gap"),(610.75,611)):
        if raw=="gpu_power" and hold=="rail_manifest":
            continue
        ruled = hold == "rail_manifest" or (tail == "ok" and hold != "ok")
        scenario = physical_tail_rl191 if ruled else physical_tail
        add(f"C_tail_{raw}_{hold}_{tail}_{int((end-610)*1000)}",scenario,hold,tail,end,raw)
    for a,b in combinations(("own_count","side_count","own_gap","side_gap"),2):
        add(f"C_recovery_{a}_{b}",recovery_pair,a,b)
    for dc,rail,name,ch in product(("ok","coverage","meter_gap","meter_contaminated"),
            ("ok","coverage","meter_gap","rail_manifest","nonpositive_denominator"),
            ("turn","decode"),PRINTS[:2]):
        if ch=="gpu_rail" and rail=="rail_manifest":
            continue
        ruled = dc != "ok" and rail != "ok" and dc != rail
        scenario = dependent_rl191 if ruled else dependent
        add(f"C_ratio_{name}_{ch}_{dc}_{rail}",scenario,dc,rail,name,ch)
    for decode,sd in product(("ok","coverage","meter_gap","nonpositive"),("ok","fewer_than_two")):
        add(f"C_floor_{decode}_{sd}",floor_pair,decode,sd)
    for bad,cross in (("coverage","rail"),("meter_gap","rail"),("coverage","dc")):
        add(f"C_lag_{cross}_already_across_other_{bad}",cross_pair,bad,cross)
    add("C_lag_dc_exact_right_endpoint",endpoint_case)


register_reasons()

def duration_case(test, field, look, raw, edge, off, d, origin):
    # Exact integral expected counts have discontinuities immediately ABOVE
    # the integer threshold. Translate or move one endpoint, never both.
    # On the rail return the observed capture end is independent of last+1.
    p = S//4 if raw in COLS else S//20 if raw=="dc_in" else S
    base = origin+602*S
    a,b = base,base+100*p
    shift = offsets(p)[off]
    if edge=="left":
        a += shift
    else:
        b += shift
    n = ceil(Fraction(99*(b-a),100*p))+d
    turn,first,last = (a,a+(b-a)//3,b-S) if field=="turn" else (a-4*S,a-2*S,a)
    def points(key):
        step = ticks(key)
        m = n if raw==key or (raw in COLS and key in COLS) else ceil(Fraction(b-a,step))
        return even(a,b,m)
    # A clean hold separated from every surgery by at least 2 s.
    q = turn-605*S
    def clocks(key):
        stride = ticks(key)
        lead = range(q-10*S,turn,S)
        phase = range(turn,a-stride//2,stride//2)
        return sorted({*lead,*phase,a-stride//4,*points(key),b+stride//4,b+stride})
    side = clocks("sidecar")
    dc = [(s,int(s>=q+601*S)) for s in clocks("dc_in")]
    starts = clocks("gpu_power")
    if field=="eof":
        # Preserve the recorded EOF exactly (a missing component need not
        # mean the capture ends early). All affected rails stay above H.
        starts = [s for s in starts if s<b]+[b]
    rails = {r:[(s,z,int(s>=q+600*S)) for s,z in zip(starts,starts[1:])] for r in COLS}
    test.assertEqual(count(judged_stamps(rails,dc,side,raw),a,b),n)
    paths = write_tape(test.folder,rails,dc,side,turn,first,last)
    admitted = 100*n*p >= 99*(b-a)
    with open_signal(paths) as sig:
        printed = report(sig,q,look)
    for ch in targets(raw):
        if field=="eof" and ch=="dc_in":
            continue
        with test.subTest(channel=ch,eligible=n,nominal=str(Fraction(b-a,p))):
            if field=="eof":
                v = printed["edges"]["rail_return_censor_s"][ch]
                test.assertEqual(set(v),{"reason","value","bound_s"})
                test.assertIsNone(v["value"])
                test.assertEqual(v["reason"],"stream_end" if admitted else "coverage")
                # Compare on the recorded clock; fractional-nanosecond
                # display roundoff cannot change this decision.
                test.assertEqual(round(Fraction(str(v["bound_s"]))*S),b-a)
            else:
                v = printed["turn"]["energy_j"][ch]
                if admitted:
                    test.assertIn(type(v),(int,float),v)
                    test.assertAlmostEqual(v,(3 if ch=="rail_sum" else 1)*(b-a)/S,delta=1e-8)
                else:
                    test.assertEqual(v,frozen.null("coverage"))


def max_energy(test,shape,look,where,raw):
    rails,dc,side = energy_tape(shape,0,0)
    if raw=="dc_in":
        # Exactly 2 s between consecutive points; keep 16 starts and clip
        # both end pairs. Powers are the sample values of the planted curve.
        stamps = stamp_gap(T,END,2*S,where,16)
        # Rounding the resampled power to a dyadic number is the fixture's
        # declared wattage. Oracle integrates those same recorded values.
        dc = [r for r in dc if r[0]<T-S//2 or r[0]>END+S//2]
        dc += [(t,40+Fraction(round(elevation(shape,t)*256),256)) for t in stamps]
        dc.sort()
    else:
        period = {"rail":S//10,"rail_tie":S//5,"rail_five":S//2}[raw]
        spans = segments(T,END,max(S,5*period),where,(END-T)//period)
        for r in COLS:
            body = [(s,z,BASE[r]+WEIGHT[r]*elevation(shape,T+((s-T)//(S//4))*(S//4)))
                    for s,z in spans]
            rails[r] = [x for x in rails[r] if x[1]<=T]+body+[x for x in rails[r] if x[0]>=END]
    assert_energy(test,look,shape,rails,dc,side,S//2 if raw=="dc_in" else period)


def two_intervals(test,look,raw,hold,turn):
    leg = frozen.TraceLeg(test.folder)
    set_hold_fault(leg,hold)
    if turn=="coverage":
        leg.omit(raw,[605.25,606.5,607.5])
    if turn=="meter_gap":
        leg.meta["sidecar_times"] = [s for s in leg.meta["sidecar_times"] if not 605<s<608]
    printed = frozen.print_one(leg.signal(),frozen.IDS[0] if look=="instrument" else frozen.IDS[1])
    for ch in targets(raw):
        with test.subTest(channel=ch):
            frozen.assert_scalar(test,printed["hold"][ch]["mean_w"],None if hold=="ok" else hold)
            reason = turn if turn!="ok" else hold
            frozen.assert_scalar(test,printed["turn"]["energy_j"][ch],None if reason=="ok" else reason)


def skip_and_eof(test, reason, in_complete):
    # RL-190 H: same pair of defects, on opposite sides of the last
    # complete-window boundary. A skipped window and an EOF censor can coexist.
    leg = frozen.terminal_leg(test.folder,-14)
    anchor = 576 if in_complete else 586
    if reason in ("coverage","both"):
        leg.omit("gpu_power",[anchor+9 if in_complete else anchor+8])
    if reason in ("gap_over_u1","both"):
        frozen.plant_rail_gap(leg,"gpu_power",anchor)
    end = 595.75
    rows = [r for r in leg.rows[frozen.RAIL_FILE] if float(r["interval_start_s"])<end]
    for r in rows:
        if float(r["interval_end_s"])>end:
            r.update(interval_end_s=end,timestamp_s=end)
    leg.rows[frozen.RAIL_FILE] = rows
    leg.meta["rail_intervals"] = [(a,min(b,end)) for a,b in leg.meta["rail_intervals"] if a<end]
    # A complete gap inside the quiet hold would otherwise also destroy H.
    # Use the *sidecar* U1 or rail U1 only when that threshold remains
    # available. RL-190 lists a thresholdless leg separately.
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    edges = printed["edges"]
    ch = "gpu_rail"
    if reason!="coverage":
        test.assertEqual(printed["hold"][ch]["mean_w"],frozen.null("meter_gap"))
        v = edges["recovery_s"][ch]
        test.assertIsNone(v["value"])
        test.assertNotIn(v["reason"],("under","not returned"))
        test.assertNotIn("bound_s",v)
    else:
        test.assertEqual(edges["recovery_s"][ch],frozen.null("not returned",bound_s=612))
        test.assertEqual(edges["recovery_skipped_windows"][ch],int(in_complete))
        test.assertEqual(edges.get("recovery_skip_reasons",{}).get(ch,[]),
                         ["coverage"] if in_complete else [])


def register_additions():
    for (field,look),raw,edge,off,d,era in product(
            (("turn","instrument"),("turn","stability"),("eof","instrument")),RAW,
            ("left","right"),offsets(S),(-1,0,1),("local","epoch")):
        if field=="eof" and raw=="dc_in":
            continue
        add(f"A_duration_{field}_{look}_{raw}_{edge}_{off}_n{d+1}_{era}",duration_case,
            field,look,raw,edge,off,d,EPOCH if era=="epoch" else 0)
    for shape,look,loc,raw in product(("identity","flat","step","ramp"),LOOKS,
                                      ("start","middle","end"),("rail","rail_tie","rail_five","dc_in")):
        add(f"B_u1_{look}_{shape}_{raw}_{loc}",max_energy,shape,look,loc,raw)
    for look,raw,hold,turn in product(LOOKS,(*COLS,"dc_in"),("ok","coverage","meter_gap"),
                                      ("ok","coverage","meter_gap")):
        add(f"C_holds_turns_{look}_{raw}_{hold}_{turn}",two_intervals,look,raw,hold,turn)
    for reason,complete in product(("coverage","gap_over_u1","both"),(True,False)):
        add(f"C_recovery_end_{reason}_{'complete' if complete else 'fragment'}",skip_and_eof,reason,complete)


register_additions()



def lag_collision(test, ch, dc, rail):
    leg = frozen.TraceLeg(test.folder)
    raw = "gpu_power" if ch=="gpu_rail" else "ane_power"
    if dc in ("crossed_before_span","unobserved","no_threshold"):
        for r in leg.rows[frozen.DC_FILE]:
            t = float(r["epoch_s"])
            if dc=="no_threshold" and 606<=t<=610:
                r["watts"]=0
            if dc!="no_threshold" and t>=610:
                r["watts"]=0 if dc=="crossed_before_span" else 100
    elif dc=="coverage":
        leg.omit("dc_in",[610.5])
    elif dc=="meter_gap":
        rows = leg.rows[frozen.DC_FILE]
        rows[-2]["epoch_s"],rows[-1]["epoch_s"]=614,614.05
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    elif dc=="meter_contaminated":
        leg.meta["meter_clean"]=False
    elif dc=="absent":
        leg.meta.update(meter_present=False,meter_times=[],meter_counts={"decoded":0,"bad":0,"usb_errors":0})
        # TraceLeg only writes a CSV with a header when it has a row. Meter
        # absence is authenticated metadata and the DC file must not be used.
        frozen.put(test.folder/frozen.DC_FILE,frozen.csvbytes([("epoch_s","watts")]))
    if rail in ("crossed_before_span","unobserved","no_threshold"):
        for r in leg.rows[frozen.RAIL_FILE]:
            t = float(r["interval_start_s"])
            if r["source"]!="powermetrics":
                continue
            if rail=="no_threshold" and 606<=t<610:
                r["power_w"]=0
            if rail!="no_threshold" and t>=610:
                r["power_w"]=0 if rail=="crossed_before_span" else 100
    elif rail=="coverage":
        leg.omit(raw,[610.25])
    elif rail=="rail_manifest":
        leg.meta["rail_manifest"]=list(reversed(COLS))
    if dc=="absent":
        del leg.rows[frozen.DC_FILE]
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    v = printed["edges"]["decode_end_lag_s"][ch]
    issues = {dc,rail}-{"ok"}
    if not issues:
        test.assertEqual(v,.2578125 if ch=="gpu_rail" else .0078125)
        return
    test.assertIsNone(v["value"])
    if "absent" in issues:
        defer(test,"health")
    if "no_threshold" in issues:
        defer(test,"threshold_lag")
    if issues=={"unobserved"}:
        test.assertEqual(v,frozen.null("over 1 s",bound_s=1))
        return
    issues.discard("unobserved")
    if len(issues)>1:
        defer(test,"cross_pair" if "crossed_before_span" in issues else "operands")
    test.assertEqual(v,frozen.null(issues.pop()))


def lag_collision_rl191(test, ch, dc, rail):
    leg = frozen.TraceLeg(test.folder)
    raw = "gpu_power" if ch=="gpu_rail" else "ane_power"
    if dc in ("crossed_before_span","unobserved","no_threshold"):
        for r in leg.rows[frozen.DC_FILE]:
            t = float(r["epoch_s"])
            if dc=="no_threshold" and 606<=t<=610:
                r["watts"]=0
            if dc!="no_threshold" and t>=610:
                r["watts"]=0 if dc=="crossed_before_span" else 100
    elif dc=="coverage":
        leg.omit("dc_in",[610.5])
    elif dc=="meter_gap":
        rows = leg.rows[frozen.DC_FILE]
        rows[-2]["epoch_s"],rows[-1]["epoch_s"]=614,614.05
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    elif dc=="meter_contaminated":
        leg.meta["meter_clean"]=False
    elif dc=="absent":
        leg.meta.update(meter_present=False,meter_times=[],meter_counts={"decoded":0,"bad":0,"usb_errors":0})
        # TraceLeg only writes a CSV with a header when it has a row. Meter
        # absence is authenticated metadata and the DC file must not be used.
        frozen.put(test.folder/frozen.DC_FILE,frozen.csvbytes([("epoch_s","watts")]))
    if rail in ("crossed_before_span","unobserved","no_threshold"):
        for r in leg.rows[frozen.RAIL_FILE]:
            t = float(r["interval_start_s"])
            if r["source"]!="powermetrics":
                continue
            if rail=="no_threshold" and 606<=t<610:
                r["power_w"]=0
            if rail!="no_threshold" and t>=610:
                r["power_w"]=0 if rail=="crossed_before_span" else 100
    elif rail=="coverage":
        leg.omit(raw,[610.25])
    elif rail=="rail_manifest":
        leg.meta["rail_manifest"]=list(reversed(COLS))
    if dc=="absent":
        del leg.rows[frozen.DC_FILE]
    printed = frozen.print_one(leg.signal(),frozen.IDS[0])
    v = printed["edges"]["decode_end_lag_s"][ch]
    # RL-191 §1.2, §1.3 and §1.4. Use the same rank for health, distinct
    # refusals and unavailable thresholds. All of these collisions omit bound_s.
    labels = {"absent": "meter_absent", "no_threshold": "nonpositive_level",
              "unobserved": "over 1 s"}
    reason = ranked_reason(labels.get(dc, dc), labels.get(rail, rail))
    test.assertEqual(v, frozen.null(reason))


def no_tail(test, hold, shift):
    leg = frozen.TraceLeg(test.folder)
    set_hold_fault(leg,hold)
    end = 610+shift
    leg.rows[frozen.RAIL_FILE] = [r for r in leg.rows[frozen.RAIL_FILE] if float(r["interval_end_s"])<=end]
    leg.meta["rail_intervals"] = [r for r in leg.meta["rail_intervals"] if r[1]<=end]
    obj = frozen.print_one(leg.signal(),frozen.IDS[0])
    # RL-191 §1.5. At or before the last token neither rail has a positive
    # tail. These fixtures have a valid manifest, including the refused holds.
    for ch in PRINTS[:2]:
        with test.subTest(channel=ch):
            test.assertEqual(obj["edges"]["rail_return_censor_s"][ch], frozen.null("no_tail"))


def crossing_time(test, channel, direction, edge, off, era):
    # Search admission uses half-open counts. Independently move the first
    # qualifying *value* through both edges, including bracket-only points.
    origin = EPOCH if era=="epoch" else 0
    a,b = origin+610*S,origin+611*S
    p = S//20 if channel=="dc_in" else S//4
    probe = (a if edge=="left" else b)+offsets(p)[off]
    grid = sorted({a-S-S//8,a-S//8,*even(a,b,24),probe,b+S//8,b+S+S//8})
    falls = direction=="fall"
    def value(s):
        return 0 if (s<probe)!=falls else 8
    # Constant over each rail row; the DC midpoint is its linear crossing.
    rails = {r:[(s,z,value(s)) for s,z in zip(grid,grid[1:])] for r in COLS}
    dc = [(s,value(s)) for s in grid]
    side = [a-S//8,a,b,b+S//8]
    paths = write_tape(test.folder,rails,dc,side,a-8*S,a-4*S,a)
    with open_signal(paths) as sig:
        result = sig.cross(channel,a//S,b//S,12 if channel=="rail_sum" else 4,falls=falls)
    if channel=="dc_in" and probe==b:
        defer(test,"tail_endpoint")
    if probe<=a:
        test.assertEqual(result,frozen.null("crossed_before_span"))
    elif probe>=b:
        test.assertEqual(result,frozen.null("crossing_unobserved"))
    elif channel!="dc_in":
        test.assertIn(type(result),(float,int),result)
        test.assertAlmostEqual(result, float(Fraction(probe,S)), delta=math.ulp(float(result)))
    else:
        previous = max(s for s in grid if s<probe)
        if previous<a:
            test.assertEqual(result,frozen.null("crossed_before_span"))
        else:
            test.assertIn(type(result),(float,int),result)
            # Interpolation may yield a half nanosecond.
            target = Fraction(probe+previous,2)
            test.assertAlmostEqual(result,float(target/S),delta=math.ulp(float(result)))


def crossing_time_rl191(test, channel, direction, edge, off, era):
    # Search admission uses half-open counts. Independently move the first
    # qualifying *value* through both edges, including bracket-only points.
    origin = EPOCH if era=="epoch" else 0
    a,b = origin+610*S,origin+611*S
    p = S//20 if channel=="dc_in" else S//4
    probe = (a if edge=="left" else b)+offsets(p)[off]
    grid = sorted({a-S-S//8,a-S//8,*even(a,b,24),probe,b+S//8,b+S+S//8})
    falls = direction=="fall"
    def value(s):
        return 0 if (s<probe)!=falls else 8
    # Constant over each rail row; the DC midpoint is its linear crossing.
    rails = {r:[(s,z,value(s)) for s,z in zip(grid,grid[1:])] for r in COLS}
    dc = [(s,value(s)) for s in grid]
    side = [a-S//8,a,b,b+S//8]
    paths = write_tape(test.folder,rails,dc,side,a-8*S,a-4*S,a)
    with open_signal(paths) as sig:
        result = sig.cross(channel,a//S,b//S,12 if channel=="rail_sum" else 4,falls=falls)
    # RL-191 §1.6. The closed DC span includes b. Its predecessor is at
    # a + 979166666 ns, so the qualifying segment crosses at a + 989583333 ns.
    expected = float(Fraction(a + 989_583_333, S))
    test.assertIn(type(result), (int, float), result)
    test.assertAlmostEqual(result, expected, delta=math.ulp(expected))


def register_lags():
    for ch,dc,rail in product(PRINTS[:2],
            ("ok","coverage","meter_gap","meter_contaminated","absent","crossed_before_span","unobserved","no_threshold"),
            ("ok","coverage","rail_manifest","crossed_before_span","unobserved","no_threshold")):
        if ch=="gpu_rail" and rail=="rail_manifest":
            continue
        issues = {dc, rail} - {"ok", "unobserved"}
        ruled = "absent" in issues or "no_threshold" in issues or len(issues) > 1
        scenario = lag_collision_rl191 if ruled else lag_collision
        add(f"C_lag_pair_{ch}_{dc}_{rail}",scenario,ch,dc,rail)
    for hold,shift in product(("ok","meter_gap","coverage"),(0,-.25)):
        add(f"C_tail_no_support_{hold}_{int(-shift*1000)}",no_tail,hold,shift)
    for ch,direction,edge,off,era in product(PRINTS,("rise","fall"),("left","right"),offsets(S),("local","epoch")):
        endpoint = ch == "dc_in" and (edge, off) in (("right", "exact"), ("left", "p1s"))
        scenario = crossing_time_rl191 if endpoint else crossing_time
        add(f"A_cross_{ch}_{direction}_{edge}_{off}_{era}",scenario,ch,direction,edge,off,era)


register_lags()



def projected_cross(test,raw,edge,off,origin):
    a = origin+610*S
    b = a+S
    p = ticks(raw)
    probe = (a if edge=="left" else b)+offsets(p)[off]
    def tape(key):
        stride = ticks(key)
        lead = list(range(origin-10*S,origin+602*S,S))
        lead += list(range(origin+602*S,a-S//8,stride//2))
        normal = (a,*even(a,a+3*S//8,12),a+3*S//8,a+5*S//8,*even(a+5*S//8,b,12),b)
        if key=="rail":
            normal = (*normal,a+S//2)
        mid = even(a,b,24)
        active = (key=="rail")==(raw in COLS)
        series = sorted({*lead,a-S//8,*(mid if active else normal),
                         *([probe] if active else []), b+S//8,b+S+S//8})
        when = probe if active else (a+S//2 if key=="rail" else a+5*S//8)
        return [(s,8 if origin+602*S<=s<when else 0) for s in series]
    pairs = tape("rail")
    rails = {r:[(s,z,w) for (s,w),(z,_) in zip(pairs,pairs[1:])] for r in COLS}
    dc = tape("dc_in")
    side = list(range(origin-10*S,b+3*S,S))
    paths = write_tape(test.folder,rails,dc,side,origin+602*S,origin+606*S,a)
    with open_signal(paths) as sig:
        v = report(sig,origin,"instrument")["edges"]["decode_end_lag_s"]["gpu_rail"]
    if raw=="dc_in" and probe==b:
        defer(test,"tail_endpoint")
    if probe<=a:
        test.assertEqual(v,frozen.null("crossed_before_span"))
        return
    if probe>=b:
        test.assertEqual(v,frozen.null("over 1 s",bound_s=1))
        return
    if raw=="dc_in":
        prior = max(s for s,w in dc if s<probe)
        if prior<a:
            test.assertEqual(v,frozen.null("crossed_before_span"))
            return
        expected = Fraction(prior+probe,2)-(a+S//2)
    else:
        expected = a+S//2-probe
    # Actual printed difference, not an absolute binary64 epoch. The result
    # is resolvable to the nearest ns even at the Unix-scale epoch.
    test.assertIn(type(v),(int,float),v)
    test.assertLessEqual(abs(Fraction(str(v))*S-expected),Fraction(1,2))


def projected_cross_rl191(test,raw,edge,off,origin):
    a = origin+610*S
    b = a+S
    p = ticks(raw)
    probe = (a if edge=="left" else b)+offsets(p)[off]
    def tape(key):
        stride = ticks(key)
        lead = list(range(origin-10*S,origin+602*S,S))
        lead += list(range(origin+602*S,a-S//8,stride//2))
        normal = (a,*even(a,a+3*S//8,12),a+3*S//8,a+5*S//8,*even(a+5*S//8,b,12),b)
        if key=="rail":
            normal = (*normal,a+S//2)
        mid = even(a,b,24)
        active = (key=="rail")==(raw in COLS)
        series = sorted({*lead,a-S//8,*(mid if active else normal),
                         *([probe] if active else []), b+S//8,b+S+S//8})
        when = probe if active else (a+S//2 if key=="rail" else a+5*S//8)
        return [(s,8 if origin+602*S<=s<when else 0) for s in series]
    pairs = tape("rail")
    rails = {r:[(s,z,w) for (s,w),(z,_) in zip(pairs,pairs[1:])] for r in COLS}
    dc = tape("dc_in")
    side = list(range(origin-10*S,b+3*S,S))
    paths = write_tape(test.folder,rails,dc,side,origin+602*S,origin+606*S,a)
    with open_signal(paths) as sig:
        v = report(sig,origin,"instrument")["edges"]["decode_end_lag_s"]["gpu_rail"]
    # RL-191 §1.6. Subtract the rail crossing at a + 500000000 ns from
    # the interpolated DC crossing at a + 989583333 ns on either clock.
    test.assertIn(type(v), (int, float), v)
    test.assertLessEqual(abs(Fraction(str(v)) * S - 489_583_333), Fraction(1, 2))


def clipped_energy(test,look,shape,place,width):
    rails,dc,side = energy_tape(shape,0,137)
    for r in COLS:
        lead = [(s,min(z,T-S//8),w) for s,z,w in rails[r] if z<=T]
        body = [(s,z,w) for s,z,w in rails[r] if T<=s<END]
        tail = [(max(s,END+S//8),z,w) for s,z,w in rails[r] if s>=END]
        s,z,w = body[0]
        body[0] = (s-S//8,z,w)
        s,z,w = body[-1]
        body[-1] = (s,z+S//8,w)
        i = {"near_start":0,"middle":3,"near_end":7}[place]
        s,z,w = body[i]
        split = (s+z)//2
        # Split inside the judged interval and restore its eligible count to
        # 8/8 while excising an exactly 1, 2 or 125,000,000 ns hole.
        body[i:i+1] = [(s,split,w),(split+width,z,w)]
        rails[r] = lead+body+tail
    test.assertEqual(count([s for s,z in joined(rails)],T,END),8)
    assert_energy(test,look,shape,rails,dc,side)




def mixed_gap(test,placement):
    a,b,split = 598*S,606*S,602*S
    s = split+{"slow":-3*S,"fast":S//2,"straddles":-S}[placement]
    z = s+2*S
    cuts1 = [a+i*(s-a)//10 for i in range(11)]
    cuts2 = [z+i*(b-z)//10 for i in range(11)]
    spans = list(zip(cuts1,cuts1[1:]))+list(zip(cuts2,cuts2[1:]))
    test.assertEqual(len(spans),expected_samples(a,b,split,S,S//4))
    rails = {r:[(x,y,1) for x,y in spans] for r in COLS}
    side = list(range(a-S,b+S,S))
    dc = [(t,1) for t in range(a-S,b+S,S//20)]
    paths = write_tape(test.folder,rails,dc,side,split,split+2*S,split+4*S)
    with open_signal(paths) as sig:
        value = sig.average("rail_sum",a//S,b//S)
    if placement=="straddles":
        defer(test,"mixed_gap")
    frozen.assert_scalar(test,value,None if placement=="slow" else "meter_gap")


def mixed_gap_rl191(test,placement):
    a,b,split = 598*S,606*S,602*S
    s = split+{"slow":-3*S,"fast":S//2,"straddles":-S}[placement]
    z = s+2*S
    cuts1 = [a+i*(s-a)//10 for i in range(11)]
    cuts2 = [z+i*(b-z)//10 for i in range(11)]
    spans = list(zip(cuts1,cuts1[1:]))+list(zip(cuts2,cuts2[1:]))
    test.assertEqual(len(spans),expected_samples(a,b,split,S,S//4))
    rails = {r:[(x,y,1) for x,y in spans] for r in COLS}
    side = list(range(a-S,b+S,S))
    dc = [(t,1) for t in range(a-S,b+S,S//20)]
    paths = write_tape(test.folder,rails,dc,side,split,split+2*S,split+4*S)
    with open_signal(paths) as sig:
        value = sig.average("rail_sum",a//S,b//S)
    # RL-191 §1.7. The two one-second parts pass limits of 5 s and 1.25 s.
    frozen.assert_scalar(test, value, None)


for raw,edge,off,era in product(("gpu_power","dc_in"),("left","right"),offsets(S),("local","epoch")):
    endpoint = raw == "dc_in" and (edge, off) in (("right", "exact"), ("left", "p1s"))
    scenario = projected_cross_rl191 if endpoint else projected_cross
    add(f"A_printed_lag_{raw}_{edge}_{off}_{era}",scenario,raw,edge,off,0 if era=="local" else EPOCH)
for look,shape,place,width in product(LOOKS,("identity","flat","step","ramp"),
                                     ("near_start","middle","near_end"),(1,2,S//8)):
    add(f"B_clipped_{look}_{shape}_{place}_{width}",clipped_energy,look,shape,place,width)
for place in ("slow","fast","straddles"):
    scenario = mixed_gap_rl191 if place == "straddles" else mixed_gap
    add(f"A_mixed_u1_{place}",scenario,place)



def skipped_before_end(test, fault):
    leg = frozen.terminal_leg(test.folder,-15)
    if fault in ("gap","both"):
        frozen.plant_rail_gap(leg,"gpu_power",-15)
    if fault in ("count","both"):
        leg.omit("gpu_power",[-6])
    end = 595.75
    rows = [r for r in leg.rows[frozen.RAIL_FILE] if float(r["interval_start_s"])<end]
    for r in rows:
        if float(r["interval_end_s"])>end:
            r.update(interval_end_s=end,timestamp_s=end)
    leg.rows[frozen.RAIL_FILE] = rows
    leg.meta["rail_intervals"] = [(a,min(b,end)) for a,b in leg.meta["rail_intervals"] if a<end]
    v = frozen.print_one(leg.signal(),frozen.IDS[0])
    for ch in PRINTS[:2]:
        test.assertIn(type(v["hold"][ch]["mean_w"]),(int,float))
        test.assertEqual(v["edges"]["recovery_s"][ch],frozen.null("not returned",bound_s=622))
        test.assertEqual(v["edges"]["recovery_skipped_windows"][ch],1)
        test.assertEqual(v["edges"]["recovery_skip_reasons"][ch],
                         ["gap_over_u1" if fault=="gap" else "coverage"])


def authenticated_case(test,look,mode):
    # Construct the redacted operation record and copy before the synthetic
    # World signs them. Score consumes its authenticated roster and opens the
    # verified files. The top-level one-use publication is exercised in v2.1.
    class World(frozen.World):
        def leg(self,kit,pos,v,day,ordinal,status):
            refs = super().leg(kit,pos,v,day,ordinal,status)
            # RL-192b: ordinal zero stays loaded; authenticate the tape on qualified ordinal one.
            if ordinal!=1:
                return refs
            self.witness = refs["key"]
            folder = self.copy/self.witness
            epoch = (int(frozen.read(self.repo/refs["receipt"])["t0_epoch_s"])+120)*S
            op_path = self.repo/refs["leg_record"]
            op = frozen.read(op_path)
            q = epoch+(50 if mode=="clock" else 0)
            op["quiet_spans_ns"] = [[q,q+600*S]]
            frozen.put(op_path,op)
            rs,points,side = energy_tape("identity",8 if mode=="energy" else 0,0)
            if mode=="clock":
                lost = {i*S for i in (100,200,300,400,450,500,600)}
                side = [t for t in side if t not in lost]
                test.assertEqual(count(side,50,600*S+50),593)
            levels = {r:[(epoch+s,epoch+z,wire_watts(w)) for s,z,w in rows] for r,rows in rs.items()}
            write_tape(folder,levels,[(epoch+s,wire_watts(w)) for s,w in points],
                       [epoch+s for s in side],epoch+T,epoch+T+S,epoch+END-S,
                       rail_tick=S//2,dc_tick=S//4)
            return refs
    world = World(test.folder/"book-fixture",frozen.IDS[0] if look=="instrument" else frozen.IDS[1])
    frozen.Checks().stage1(world)
    reader = frozen.executor()
    snap = reader.Snapshot(world.repo,world.look,"stage2")
    stage,legs = reader.census(snap)
    snap.check_stage1(stage)
    scored = reader.score(snap,reader.verify_gates(snap,legs),legs,lambda:None)
    for ch in PRINTS:
        with test.subTest(channel=ch):
            if mode=="clock":
                test.assertEqual(scored["hold"][world.witness][ch]["mean_w"],frozen.null("coverage"))
            else:
                test.assertEqual(scored["turn"][world.witness]["energy_j"][ch],0)


for fault in ("gap","count","both"):
    add(f"C_recovery_skip_and_eof_{fault}",skipped_before_end,fault)
for look,mode in product(LOOKS,("clock","energy")):
    add(f"{'A' if mode=='clock' else 'B'}_authenticated_{mode}_{look}",authenticated_case,look,mode)



NAMED = ("coverage","meter_gap","gap_over_u1","stream_end","missing_operand","decode_or_sd_undefined")


def named_pair(test, p, q):
    # All fifteen unordered pairs on the brief's named axis can coexist on
    # one leg. These fields have different interval/operand domains. The
    # same-output collisions are separately exercised by the C_* tables.
    leg,start,_ = frozen.recovery_fixture(test.folder,0,10)
    pair = {p,q}
    if "coverage" in pair:
        leg.omit("ane_power",[607.5])
    if "meter_gap" in pair:
        rows = leg.rows[frozen.DC_FILE]
        rows[-2]["epoch_s"],rows[-1]["epoch_s"] = 614,614.05
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    if "gap_over_u1" in pair:
        frozen.plant_rail_gap(leg,"gpu_power",start)
    for r in leg.rows[frozen.RAIL_FILE]:
        if r["source"]=="powermetrics" and r["rail"]=="gpu_power":
            s = float(r["interval_start_s"])
            if ("missing_operand" in pair and 604<=s<606) or ("decode_or_sd_undefined" in pair and 606<=s<610):
                r["power_w"]=0
    obj = frozen.print_one(leg.signal(),frozen.IDS[0])
    if "coverage" in pair:
        test.assertEqual(obj["turn"]["energy_j"]["rail_sum"],frozen.null("coverage"))
    if "meter_gap" in pair:
        test.assertEqual(obj["turn"]["energy_j"]["dc_in"],frozen.null("meter_gap"))
    if "gap_over_u1" in pair:
        test.assertEqual(obj["edges"]["recovery_skip_reasons"]["gpu_rail"],["gap_over_u1"])
        test.assertEqual(obj["edges"]["recovery_s"]["gpu_rail"],19)
    if "stream_end" in pair:
        test.assertEqual(obj["edges"]["rail_return_censor_s"]["gpu_rail"],frozen.null("stream_end",bound_s=1))
    if "decode_or_sd_undefined" in pair:
        test.assertLessEqual(obj["gain"]["decode_w"]["gpu_rail"],0)
        test.assertEqual(obj["gain"]["floor_tokens"]["gpu_rail"],[frozen.null("decode_or_sd_undefined")]*3)
    if "missing_operand" in pair:
        v = obj["edges"]["onset_lag_s"]["gpu_rail"]
        test.assertIsNone(v["value"])
        test.assertNotIn("bound_s",v)
        defer(test,"onset_operand")


def named_pair_rl191(test, p, q):
    # All fifteen unordered pairs on the brief's named axis can coexist on
    # one leg. These fields have different interval/operand domains. The
    # same-output collisions are separately exercised by the C_* tables.
    leg,start,_ = frozen.recovery_fixture(test.folder,0,10)
    pair = {p,q}
    if "coverage" in pair:
        leg.omit("ane_power",[607.5])
    if "meter_gap" in pair:
        rows = leg.rows[frozen.DC_FILE]
        rows[-2]["epoch_s"],rows[-1]["epoch_s"] = 614,614.05
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in rows]
    if "gap_over_u1" in pair:
        frozen.plant_rail_gap(leg,"gpu_power",start)
    for r in leg.rows[frozen.RAIL_FILE]:
        if r["source"]=="powermetrics" and r["rail"]=="gpu_power":
            s = float(r["interval_start_s"])
            if ("missing_operand" in pair and 604<=s<606) or ("decode_or_sd_undefined" in pair and 606<=s<610):
                r["power_w"]=0
    obj = frozen.print_one(leg.signal(),frozen.IDS[0])
    if "coverage" in pair:
        test.assertEqual(obj["turn"]["energy_j"]["rail_sum"],frozen.null("coverage"))
    if "meter_gap" in pair:
        test.assertEqual(obj["turn"]["energy_j"]["dc_in"],frozen.null("meter_gap"))
    if "gap_over_u1" in pair:
        test.assertEqual(obj["edges"]["recovery_skip_reasons"]["gpu_rail"],["gap_over_u1"])
        test.assertEqual(obj["edges"]["recovery_s"]["gpu_rail"],19)
    if "stream_end" in pair:
        test.assertEqual(obj["edges"]["rail_return_censor_s"]["gpu_rail"],frozen.null("stream_end",bound_s=1))
    if "decode_or_sd_undefined" in pair:
        test.assertLessEqual(obj["gain"]["decode_w"]["gpu_rail"],0)
        test.assertEqual(obj["gain"]["floor_tokens"]["gpu_rail"],[frozen.null("decode_or_sd_undefined")]*3)
    if "missing_operand" in pair:
        v = obj["edges"]["onset_lag_s"]["gpu_rail"]
        # RL-191 §1.4. The GPU prefill level supplies no threshold. Its
        # historical case label is preserved and the onset lag has no bound.
        test.assertEqual(v, frozen.null("nonpositive_level"))


for p,q in combinations(NAMED,2):
    scenario = named_pair_rl191 if "missing_operand" in (p, q) else named_pair
    add(f"C_named_{p}_and_{q}",scenario,p,q)

if __name__=="__main__":
    unittest.main()
