"""Candidate fix check: choose m_C as the defined pair with the largest lower endpoint m - dm.
Patches max() inside a copy of knee_scan only. Usage: python3.13 -B knee_fix_check.py /tmp/jw"""
import inspect, random, sys
sys.path[:0] = [sys.argv[1], '.']
from scripts import bytes_stream_test as p
from scan_cases import receipts, worked5, dram_only
src = inspect.getsource(p.knee_scan).replace(
    'peak = max(defined, key=lambda p: p["m_bytes_s"])',
    'peak = max(defined, key=lambda p: p["m_bytes_s"]-p["dm_bytes_s"])')
ns = dict(vars(p)); exec(src, ns); fixed = ns["knee_scan"]
for q in (False, True):
    print("DRAM-only q=%s:" % q, fixed(receipts(dram_only, q))["status"], "| §5:", fixed(receipts(worked5, q))["K"])
rng = random.Random(20261028)
for sig in (0.0005, 0.001, 0.002, 0.005, 0.01):
    res = {}
    for _ in range(400):
        r = fixed(receipts(worked5, True, sig, rng)); k = r["K"]//2**20 if r["K"] else r.get("reason")
        res[k] = res.get(k, 0)+1
    rd = {}
    for _ in range(200):
        r = fixed(receipts(dram_only, True, sig, rng)); k = r["K"]//2**20 if r["K"] else r.get("reason")
        rd[k] = rd.get(k, 0)+1
    print(f"noise {sig*100:.2f}%: §5 {dict((k, v/400) for k, v in res.items())}  DRAM-only {dict((k, v/200) for k, v in rd.items())}")
