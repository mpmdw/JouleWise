"""M2 structure-only measurement. Reads ONLY: events.jsonl (phase/event_type/timestamp_s/metadata.monotonic_ns),
metadata.json -> uncertainty_evidence.clock_anchor.clock_stamps.sampling_started (clock fields only),
rich_telemetry.jsonl.zst -> index, timestamp_s, elapsed_ns, gpu.{freq_hz,idle_ratio,active_freq_mhz_weighted,dvfm_states[freq,used_ratio]},
clusters[].{name,freq_hz,idle_ratio,dvfm_states[freq,used_ratio]}.
Power-like keys (processor_combined_power_w, rail_sum_power_w, combined_power_delta_w, gpu_energy) are dropped at load, never inspected.
Usage: python -I m2.py <claim-runs dir> <out json>"""
import sys, json, subprocess, os, math, statistics as st
RUNS, OUT = sys.argv[1], sys.argv[2]
LOST = {"bytes-llama-70b-abs-r07","bytes-llama-70b-null-b02-a1","bytes-llama-70b-null-b03-b1","bytes-llama-70b-null-b04-b2",
        "bytes-llama-70b-null-b05-a1","bytes-llama-70b-null-b05-a2","bytes-llama-70b-null-b06-a2","bytes-llama-70b-null-b07-a2",
        "bytes-llama-70b-null-b09-a1","bytes-llama-70b-null-b10-b1"}
def slim(r):
    g = r.get("gpu")
    out = {"i": r.get("index"), "ts": r.get("timestamp_s"), "el": r.get("elapsed_ns")}
    if isinstance(g, dict):
        out["g"] = {"f": g.get("freq_hz"), "idle": g.get("idle_ratio"), "aw": g.get("active_freq_mhz_weighted"),
                    "st": [(s.get("freq"), s.get("used_ratio")) for s in (g.get("dvfm_states") or [])]}
    else:
        out["g"] = None
    out["c"] = {}
    for c in r.get("clusters") or []:
        out["c"][c.get("name")] = {"f": c.get("freq_hz"), "idle": c.get("idle_ratio"),
                                   "st": [(s.get("freq"), s.get("used_ratio")) for s in (c.get("dvfm_states") or [])]}
    return out
def event_span(events, phase, anchor):
    # identical to joulewise.bytes_analysis._event_span
    def mapped(e):
        own = e.get("metadata", {}).get("monotonic_ns")
        return own if type(own) is int else round((anchor["monotonic_before_s"] + e["timestamp_s"] - anchor["epoch_s"]) * 1e9)
    s = [e for e in events if e.get("phase") == phase and e["event_type"] in ("phase_start", "stage_started")]
    en = [e for e in events if e.get("phase") == phase and e["event_type"] in ("phase_end", "stage_completed")]
    assert len(s) == 1 and len(en) == 1, phase
    return mapped(s[0]), mapped(en[0])
def mean(x): return sum(x)/len(x) if x else None
members = sorted(d for d in os.listdir(RUNS) if d.startswith("bytes-llama-70b-"))
res = {}
for m in members:
    D = os.path.join(RUNS, m)
    events = [json.loads(l) for l in open(D + "/events.jsonl") if l.strip()]
    first_ts = min(e["timestamp_s"] for e in events)
    anchor = json.load(open(D + "/metadata.json"))["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]["sampling_started"]
    a = {k: anchor[k] for k in ("epoch_s", "monotonic_before_s")}
    d0, d1 = event_span(events, "decode", a)
    raw = subprocess.run(["zstd", "-dc", D + "/rich_telemetry.jsonl.zst"], capture_output=True, check=True).stdout.decode().splitlines()
    recs = [slim(json.loads(l)) for l in raw if l.strip()]
    inside = []
    for r in recs:
        if r["ts"] is None or r["el"] is None: continue
        end_ns = (a["monotonic_before_s"] + r["ts"] - a["epoch_s"]) * 1e9
        start_ns = end_ns - r["el"]
        if start_ns >= d0 and end_ns <= d1:   # support [endpoint-elapsed, endpoint) inside decode span
            inside.append(r)
    res[m] = {"first_ts": first_ts, "decode_s": (d1-d0)/1e9, "n_total": len(recs), "recs": inside,
              "lost": m.replace("bytes-llama-70b-","") in {x.replace("bytes-llama-70b-","") for x in LOST}}
# top DVFM state per cluster = highest freq in the table seen anywhere in the 50 members' decode records
top = {}
for m, v in res.items():
    for r in v["recs"]:
        if r["g"]:
            for f, u in r["g"]["st"]:
                if f is not None: top["GPU"] = max(top.get("GPU", f), f)
        for n, c in r["c"].items():
            for f, u in c["st"]:
                if f is not None: top[n] = max(top.get(n, f), f)
def topfrac(r, name):
    src = r["g"] if name == "GPU" else r["c"].get(name)
    if src is None: return None
    us = [u for f, u in src["st"] if f == top[name] and u is not None]
    return sum(us) if us else None
rows = []
cnames = sorted(k for k in top if k != "GPU")
for m, v in sorted(res.items(), key=lambda kv: kv[1]["first_ts"]):
    R = v["recs"]; row = {"member": m, "first_ts": v["first_ts"], "lost": v["lost"], "n": len(R), "decode_s": v["decode_s"], "n_file": v["n_total"]}
    miss = {}
    def col(vals, key):
        got = [x for x in vals if x is not None and not (isinstance(x, float) and math.isnan(x))]
        miss[key] = len(vals) - len(got); return got
    aw = col([r["g"]["aw"] if r["g"] else None for r in R], "gpu_active_freq_weighted")
    fq = col([r["g"]["f"] if r["g"] else None for r in R], "gpu_freq")
    gi = col([r["g"]["idle"] if r["g"] else None for r in R], "gpu_idle_ratio")
    gt = col([topfrac(r, "GPU") for r in R], "gpu_top_state")
    row.update(gpu_aw_mean=mean(aw), gpu_aw_min=min(aw) if aw else None, gpu_f_mean=mean(fq), gpu_f_min=min(fq) if fq else None,
               gpu_idle_mean=mean(gi), gpu_top_mean=mean(gt),
               gpu_top_ge_half=(sum(1 for x in gt if x >= 0.5)/len(gt)) if gt else None)
    k = len(R)//3
    f3 = lambda part: mean([r["g"]["aw"] for r in part if r["g"] and r["g"]["aw"] is not None])
    row.update(gpu_aw_first_third=f3(R[:k]), gpu_aw_last_third=f3(R[-k:]))
    for n in cnames:
        ci = col([r["c"][n]["idle"] if n in r["c"] else None for r in R], n + "_idle")
        ct = col([topfrac(r, n) for r in R], n + "_top_state")
        cf = col([r["c"][n]["f"] if n in r["c"] else None for r in R], n + "_freq")
        row[n + "_idle_mean"] = mean(ci); row[n + "_top_mean"] = mean(ct); row[n + "_freq_mean_mhz"] = mean(cf)/1e6 if cf else None
    row["missing"] = miss; row["missing_total"] = sum(miss.values())
    rows.append(row)
json.dump({"top_states_mhz": top, "rows": rows}, open(OUT, "w"), indent=1)
print("top", top); print(len(rows), "members; n records min/max", min(r["n"] for r in rows), max(r["n"] for r in rows))
