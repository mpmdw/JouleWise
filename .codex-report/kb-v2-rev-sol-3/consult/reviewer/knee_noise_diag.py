"""Why the program's knee scan refuses under small per-call noise (a7a20c197).
Usage: python3.13 -B knee_noise_diag.py /tmp/jw"""
import random, sys
sys.path[:0] = [sys.argv[1], '.']
from scripts import bytes_stream_test as p
from scan_cases import receipts, worked5
rng = random.Random(7)
fails, ok, peaks = 0, 0, {}
for _ in range(400):
    r = p.knee_scan(receipts(worked5, True, 0.0005, rng))
    if r["K"] is None:
        fails += 1
        d = [x for x in r["pairs"] if x["m_bytes_s"] is not None]
        pk = max(d, key=lambda x: x["m_bytes_s"])
        peaks[pk["size"]//1024] = peaks.get(pk["size"]//1024, 0)+1
        if fails == 1:
            print("example: m_C pair size", pk["size"], "B; m_C =", f"{pk['m_bytes_s']/1e9:.1f}", "GB/s; dm_C =",
                  f"{pk['dm_bytes_s']/1e9:.1f}", "GB/s; D =", f"{pk['difference_s']*1e9:.1f}", "ns; dD =", f"{pk['uncertainty_s']*1e9:.1f}", "ns")
            top = r["pairs"][-1]
            print("         top pair m_D =", f"{top['m_bytes_s']/1e9:.2f} ± {top['dm_bytes_s']/1e9:.3f} GB/s (resolved)")
    else:
        ok += 1
print(f"0.05% noise, 400 trials: knee not found {fails/400:.3f}; m_C pair size (KiB) in failures: {dict(sorted(peaks.items()))}")
