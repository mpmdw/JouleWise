"""Program's knee_scan on a DRAM-only world with per-call noise. Usage: python3.13 -B dram_noise.py /tmp/jw"""
import random, sys
sys.path[:0] = [sys.argv[1], '.']
from scripts import bytes_stream_test as p
from scan_cases import receipts, dram_only
rng = random.Random(11)
for sig in (0.0005, 0.002, 0.01):
    rd = {}
    for _ in range(200):
        r = p.knee_scan(receipts(dram_only, True, sig, rng)); k = ("K=%dKiB" % (r["K"]//1024)) if r["K"] else r.get("reason")
        rd[k] = rd.get(k, 0)+1
    found = sum(v for k, v in rd.items() if k.startswith("K="))/200
    print(f"noise {sig*100:.2f}%: false knee {found:.3f}; {dict(sorted(rd.items(), key=lambda kv: -kv[1])[:4])}")
