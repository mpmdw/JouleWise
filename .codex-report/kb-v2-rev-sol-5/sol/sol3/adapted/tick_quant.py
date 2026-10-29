"""DRAM-only and §5 scans with stamps on a 24 MHz tick (125/3 ns, Apple-silicon mach timebase),
start stamps at varied phases. Usage: python3.13 -B tick_quant.py /tmp/jw"""
import math, random, sys
sys.path[:0] = [sys.argv[1], '.']
from scripts import bytes_stream_test as p
from scan_cases import SIZES, dram_only, worked5
TICK = 125/3
def rec(td_of, rng):
    out = []
    for s in SIZES:
        td = td_of(s); n = math.floor(2/td)
        for j in range(3):
            t0 = rng.uniform(1e12, 2e12)
            q = lambda x: round(math.floor(x/TICK)*TICK)
            out.append({"bytes_per_read": s, "repeats": n, "start_ns": q(t0), "end_ns": q(t0+n*td*1e9)})

    for c in out: c.update(clock='CLOCK_MONOTONIC_RAW', clock_resolution_s=4.2e-8, clock_tick_num_ns=125, clock_tick_den=3, clock_tick_source='synthetic lead 2026-10-28 tick', clock_ns_conversion='unknown', clock_ns_conversion_source='synthetic replay')
    return out
rng = random.Random(3)
for name, f in (("DRAM-only", dram_only), ("§5", worked5)):
    res = {}
    for _ in range(200):
        r = p.knee_scan(rec(f, rng)); k = ("K=%dKiB" % (r["K"]//1024)) if r["K"] else r.get("reason")
        res[k] = res.get(k, 0)+1
    print(name, "24 MHz tick, 200 trials:", res)
