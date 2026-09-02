"""Bench replay for file 26: rebuild Sol 250's golden bundle from its literals
and re-derive every reported value independently of the producer.
Run: python3 docs/process_traces/2026-09-02-paper-d-dg071/26a-golden-check.py <outdir>"""
import hashlib, sys
from decimal import Decimal as D, ROUND_HALF_EVEN
ts = ["1784978889.10000000","1784978889.19900020","1784978889.30000029","1784978889.40000024",
      "1784978889.50200074","1784978889.60200041","1784978889.70300110","1784978889.80360015"]
st = ["1784978888.99959995","1784978889.10000020","1784978889.19899990","1784978889.30000029",
      "1784978889.40000074","1784978889.50200034","1784978889.60200111","1784978889.70300010"]
lines = ["timestamp_s,power_w,source,rail,interval_start_s,interval_end_s"]
for i, (t, s) in enumerate(zip(ts, st), 1):
    for k, r in enumerate(("cpu_power", "gpu_power", "ane_power")):
        lines.append(f"{t},{3*i-2+k}.0,fixture,{r},{s},{t}")
csv = "\n".join(lines) + "\n"
open(sys.argv[1] + "/golden.csv", "w").write(csv)
print("sha", hashlib.sha256(csv.encode()).hexdigest())
def q7(v, p):
    v = sorted(v); h = (D(len(v)) - 1) * D(p); lo = int(h); fr = h - lo
    return v[lo] if fr == 0 else v[lo] + (v[lo + 1] - v[lo]) * fr
def ms(x): return str((x * 1000).quantize(D("0.0001"), ROUND_HALF_EVEN))
w = [D(t) - D(s) for t, s in zip(ts, st)]
sp = [D(ts[i]) - D(ts[i - 1]) for i in range(1, 8)]
gaps = [D(st[i]) - D(ts[i - 1]) for i in range(1, 8)]
print("gaps", gaps, "max", max(abs(g) for g in gaps), "nonzero", sum(g != 0 for g in gaps))
for name, v in (("dg071", w), ("dg075", sp)):
    q1, md, q3 = (q7(v, p) for p in ("0.25", "0.5", "0.75")); i = q3 - q1
    print(name, len(v), q1, md, q3, i, "|", ms(q1), ms(md), ms(q3), ms(i), "diffRendered", D(ms(q3)) - D(ms(q1)))
