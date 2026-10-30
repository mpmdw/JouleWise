"""Knee-scan cases through the program's knee_scan at a7a20c197.

Usage: python3.13 -B scan_cases.py /tmp/jw
Builds production-shaped scan receipts (three ~2 s calls per size, 16 KiB..32 GiB,
integer-ns stamps) from timing models and prints the program's verdicts.
"""
import math, random, sys
sys.path[:0] = [sys.argv[1]]
from scripts import bytes_stream_test as p

SIZES = [2**k for k in range(14, 36)]


def receipts(td_of, quantized=True, noise=None, rng=None, stop=None):
    out = []
    for s in SIZES:
        if stop and s > stop:
            break
        td = td_of(s)
        n = math.floor(2/td)
        for j in range(3):
            dur = n*td*(1+(rng.gauss(0, noise) if noise else 0))
            ns = round(dur*1e9) if quantized else dur*1e9
            out.append({"bytes_per_read": s, "repeats": n, "start_ns": 10**12, "end_ns": 10**12+ns})
    return out


def dram_only(s):
    return 50e-6+s/331.6e9


def worked5(s):
    # marginal: 1000 GB/s up to 32 MiB; 32->64 MiB pair at 198.8 GB/s; 331.6 from 64 MiB up
    k = 64*2**20
    if s <= k//2:
        return 50e-6+s/1e12
    t32 = 50e-6+(k//2)/1e12
    t64 = t32+(k//2)/198.8e9
    return t64+(s-k)/331.6e9


def show(name, r):
    above = [p_["size"] for p_ in r["pairs"] if p_["above"]]
    und = sum(1 for p_ in r["pairs"] if p_["m_bytes_s"] is None)
    print(f"{name}: {r['status']} K={r['K']} reason={r.get('reason')} above={len(above)} undefined_pairs={und}"
          + (f" m_th={r['threshold']/1e9:.4f}GB/s dm_th={r['threshold_uncertainty']/1e9:.3g}" if r['threshold'] else ""))
    return r


if __name__ == "__main__":
    for q in (False, True):
        show(f"Sol1 DRAM-only quantized={q}", p.knee_scan(receipts(dram_only, q)))
        r = show(f"§5 worked quantized={q}", p.knee_scan(receipts(worked5, q)))
        pr = next(x for x in r["pairs"] if x["size"] == 32*2**20)
        print(f"   16->32 MiB margin {pr['margin']/1e9:.3f} GB/s bar {pr['bar']/1e9:.3g} GB/s;"
              f" 32->64 m={[x for x in r['pairs'] if x['size']==64*2**20][0]['m_bytes_s']/1e9:.2f}")
    # DRAM-only with stop at 1 GiB (s_max small)
    show("§5 worked, s_max=1 GiB", p.knee_scan(receipts(worked5, True, stop=2**30)))
    # Opus-2 noise sweep through the program
    rng = random.Random(20261028)
    for sig in (0.0005, 0.001, 0.002, 0.005):
        res = {}
        for _ in range(400):
            r = p.knee_scan(receipts(worked5, True, sig, rng))
            key = r["K"] if r["K"] else r.get("reason")
            res[key] = res.get(key, 0)+1
        print(f"noise {sig*100:.2f}%:", {(k//2**20 if isinstance(k, int) else k): v/400 for k, v in res.items()})
