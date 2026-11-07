import json, sys, collections
M = sys.argv[1]; R = sys.argv[2]; tol = int(sys.argv[3])
sys.path.insert(0, M)
from joulewise.align.apple import smc_enumeration as se, thermal
thermal.Coverage.tolerance_ns = tol
r = json.load(open(f"{R}/smc/r0.json"))
samples = [json.loads(l) for l in open(f"{R}/smc/samples.jsonl")]
print("values keys", list(samples[0]["values"].keys()))
cap = {"inventory": r["inventory"], "phases": r["phases"], "started": r["started"],
       "finished": r["finished"], "samples": samples}
out = se.rank(cap)
rk = out["ranking"]
print("tol_ms", tol/1e6, collections.Counter(x["reason"] for x in rk).most_common(8))
print("die", out.get("die_candidates"), "heatsink", out.get("heatsink_candidates"))
for x in rk:
    if x["class"] != "record-only":
        print(x["key"], x["class"], "t63", x["t63_s"], "tau", x["tau_s"], "dT", x.get("observed_rise"), x["phase_coverage"])
try: print("select", se.select_keys(rk))
except Exception as e: print("select err", e)
