import json, sys, statistics as st, math
M = "/Users/edr/night-archive/seats-39206674/m2"
d = json.load(open(M + "/m2_raw.json")); rows = d["rows"]
for i, r in enumerate(rows):
    r["order"] = i + 1; s = r["member"].replace("bytes-llama-70b-", "")
    r["short"] = s
    r["quad"] = "abs" if s.startswith("abs") else s.split("-")[1]
L = []; P = L.append
def f(x, n=1): return "NA" if x is None else f"{x:.{n}f}"
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); rk = [0]*len(v); i = 0
    while i < len(o):
        j = i
        while j+1 < len(o) and v[o[j+1]] == v[o[i]]: j += 1
        for k in range(i, j+1): rk[o[k]] = (i+j)/2+1
        i = j+1
    return rk
def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxy = sum((a-mx)*(b-my) for a, b in zip(x, y)); sxx = sum((a-mx)**2 for a in x); syy = sum((b-my)**2 for b in y)
    return sxy/math.sqrt(sxx*syy)
def slope(x, y):
    mx, my = st.mean(x), st.mean(y); return sum((a-mx)*(b-my) for a, b in zip(x, y))/sum((a-mx)**2 for a in x)
def trend(sub, label, key="gpu_aw_mean"):
    x = [r["order"] for r in sub]; y = [r[key] for r in sub]
    sl = slope(x, y); rho = pearson(rank(x), rank(y))
    # permutation p for Spearman (exact-ish Monte Carlo, fixed seed)
    import random; rnd = random.Random(1); ry = rank(y); rx = rank(x); cnt = 0; N = 20000
    for _ in range(N):
        rnd.shuffle(ry)
        if abs(pearson(rx, ry)) >= abs(rho) - 1e-12: cnt += 1
    P(f"| {label} | {len(sub)} | {sl:+.3f} | {sl*(len(sub)-1):+.1f} | {rho:+.2f} | {cnt/N:.3f} |")
P("# M2: structure-only GPU/CPU frequency and residency during decode, BYTES session r1-bytes-s5-p1\n")
P("No power, energy, current, voltage or battery field was read or is reported. Only frequency (MHz), residency (used_ratio), idle_ratio, timing.\n")
P("## 1. Method (exact)\n")
P("""- Session: /Users/edr/night-b6/sessions/r1-bytes-s5-p1/archive/sources/claim-runs/bytes-llama-70b-*, all 50 science members (10 abs repeats, 40 null quad members). Scripts: m2.py (extraction), report.py (this file), keys.py/explore.py (key-name-only structure probes). Python: the custody venv with `-I`, repo not imported (the stored files are already production-decoder output).
- Fields read. events.jsonl: `phase`, `event_type`, `timestamp_s`, `metadata.monotonic_ns` only. metadata.json: only `uncertainty_evidence.clock_anchor.clock_stamps.sampling_started.{epoch_s, monotonic_before_s}` (clock stamps). rich_telemetry.jsonl.zst (decompressed in memory by `zstd -dc`, never written): `index`, `timestamp_s`, `elapsed_ns`, `gpu.{freq_hz, idle_ratio, active_freq_mhz_weighted, dvfm_states[].{freq, used_ratio}}`, `clusters[].{name, freq_hz, idle_ratio, dvfm_states[].{freq, used_ratio}}`. The power-like keys of each rich record (processor_combined_power_w, rail_sum_power_w, combined_power_delta_w, gpu.gpu_energy) were dropped at load by the `slim()` function and never inspected. raw/powermetrics.plist.zst was NOT opened (rich_telemetry had every needed field, so the fallback was not needed). power_trace.csv, summary_metrics.json, outputs/ were not opened.
- Decode interval: the same arithmetic as `bytes_analysis._event_span` (line 461): for the single decode `phase_start` and `phase_end` event, if `metadata.monotonic_ns` is an int use it, else monotonic_ns = round((monotonic_before_s + event.timestamp_s - epoch_s) * 1e9) with `sampling_started` from the recorded clock anchor. (Decode events carry no own monotonic_ns, so the anchor mapping was used for every member.) Decode lengths come out 55.6 to 56.2 s.
- Support mapping: a rich record's endpoint is its `timestamp_s` (epoch; the production decoder places record 0's END at the anchor endpoint, so timestamp_s is the interval end), converted to the monotonic clock with the same anchor: end_ns = (monotonic_before_s + timestamp_s - epoch_s) * 1e9. Its averaging support is [end_ns - elapsed_ns, end_ns). A record is in the decode interval when start >= decode_start and end <= decode_end (support wholly inside; boundary-straddling records are excluded, not apportioned). File-write time is not used. Result: 493 to 498 records per member (about 112 ms each).
- GPU active frequency per record: `gpu.active_freq_mhz_weighted` (the production decoder's used_ratio-weighted mean of the DVFM state frequencies, MHz; None only if the GPU residency is all zero). The reported `gpu.freq_hz` (also MHz for the GPU) was computed alongside; the two agree to within 0.01 MHz, so the table shows the weighted one. Per member: mean and minimum over its in-decode records.
- Top DVFM state: for each cluster (GPU, E-Cluster, P0-Cluster, P1-Cluster) the highest state frequency in the table (GPU 1380 MHz; E 2568; P0 4056; P1 4056, in the decoder's units for dvfm `freq`). Per record, top-state used_ratio is the residency in that state (summed if the state is listed more than once). The per-member figure is the mean of that used_ratio over the member's in-decode records, i.e. the fraction of decode time in the top state. As a second view the table also gives the fraction of records whose top-state residency is at least 0.5.
- Idle ratios: mean over in-decode records of `gpu.idle_ratio` and each cluster's `idle_ratio`.
- Missing: any whitelisted per-record field that is None/absent is counted per member (column "miss"); missing values are excluded from that member's mean, never filled.
- Collection order: ascending `min(timestamp_s)` over each member's events.jsonl. Lost set: the ten members the brief names (OS-level thermal exclusion). Quad: null-bNN block (a1,a2,b1,b2 are all four members of that block); for the abs repeats, the quad column is "abs" and the mates of r07 are r06 and r08 as ordered.
- Descriptive statistics only; samples are 10 Hz records inside one 56 s decode, the member is the unit of comparison.
""")
P("## 2. Per-member table (collection order)\n")
P("GPU columns are MHz. top = mean residency in the GPU top state (1380 MHz); top>=.5 = fraction of records with that residency at least 0.5. Cluster idle columns are mean idle_ratio (E, P0, P1). dec = decode span s. n = records inside decode.\n")
P("| # | member | quad | status | n | dec s | GPU mean | GPU min | GPU top | top>=.5 | GPU idle | E idle | P0 idle | P1 idle | miss |")
P("|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|")
for r in rows:
    P(f"| {r['order']} | {r['short']} | {r['quad']} | {'LOST' if r['lost'] else 'kept'} | {r['n']} | {r['decode_s']:.1f} | {f(r['gpu_aw_mean'])} | {f(r['gpu_aw_min'])} | {f(r['gpu_top_mean'],3)} | {f(r['gpu_top_ge_half'],3)} | {f(r['gpu_idle_mean'],4)} | {f(r['E-Cluster_idle_mean'],4)} | {f(r['P0-Cluster_idle_mean'],4)} | {f(r['P1-Cluster_idle_mean'],4)} | {r['missing_total']} |")
tot = sum(r["missing_total"] for r in rows)
P(f"\nMissing fields: {tot} across all 50 members and all whitelisted per-record fields (every member 0). CPU-cluster top-state residency (E 2568, P0 4056, P1 4056 MHz-state) is shown below; CPU clusters are idle-ratio 0 on average and sit in their middle states, so CPU top-state fractions are uninformative here.\n")
P("| member | E top | P0 top | P1 top | E freq MHz | P0 freq MHz | P1 freq MHz | GPU mean first third | last third |")
P("|--|--|--|--|--|--|--|--|--|")
for r in rows:
    P(f"| {r['short']} | {f(r['E-Cluster_top_mean'],3)} | {f(r['P0-Cluster_top_mean'],3)} | {f(r['P1-Cluster_top_mean'],3)} | {f(r['E-Cluster_freq_mean_mhz'],0)} | {f(r['P0-Cluster_freq_mean_mhz'],0)} | {f(r['P1-Cluster_freq_mean_mhz'],0)} | {f(r['gpu_aw_first_third'])} | {f(r['gpu_aw_last_third'])} |")
# comparisons
P("\n## 3. Lost vs clean quad-mates\n")
P("Mates = the other kept members of the same null block (r07: r06 and r08). Diff = lost minus mean of mates. Also given: the rank of the lost member among itself plus its mates (1 = lowest GPU mean) and the mates' range.\n")
P("| lost member | mates (kept) | lost GPU mean | mates GPU mean (range) | diff MHz | lost top | mates top | diff top | lost GPU min | mates min | in-decode last-minus-first third (lost) | same for mates |")
P("|--|--|--|--|--|--|--|--|--|--|--|--|")
by = {r["short"]: r for r in rows}
def mates_of(r):
    if r["quad"] == "abs":
        n = r["order"]; return [x for x in rows if x["quad"] == "abs" and x["order"] in (n-1, n+1)]
    return [x for x in rows if x["quad"] == r["quad"] and x is not r and not x["lost"]]
diffs = []; tdiffs = []
for r in rows:
    if not r["lost"]: continue
    ms = mates_of(r); mm = st.mean(m["gpu_aw_mean"] for m in ms); mt = st.mean(m["gpu_top_mean"] for m in ms)
    mmin = st.mean(m["gpu_aw_min"] for m in ms)
    lt = r["gpu_aw_last_third"]-r["gpu_aw_first_third"]; mlt = st.mean(m["gpu_aw_last_third"]-m["gpu_aw_first_third"] for m in ms)
    diffs.append(r["gpu_aw_mean"]-mm); tdiffs.append(r["gpu_top_mean"]-mt)
    P(f"| {r['short']} | {len(ms)}: {', '.join(m['short'] for m in ms)} | {f(r['gpu_aw_mean'])} | {f(mm)} ({f(min(m['gpu_aw_mean'] for m in ms))} to {f(max(m['gpu_aw_mean'] for m in ms))}) | {r['gpu_aw_mean']-mm:+.1f} | {f(r['gpu_top_mean'],3)} | {f(mt,3)} | {r['gpu_top_mean']-mt:+.3f} | {f(r['gpu_aw_min'])} | {f(mmin)} | {lt:+.1f} | {mlt:+.1f} |")
P(f"\nLost minus mates, GPU mean: median {st.median(diffs):+.1f} MHz, mean {st.mean(diffs):+.1f}, range {min(diffs):+.1f} to {max(diffs):+.1f}; negative in {sum(1 for x in diffs if x<0)} of {len(diffs)}. Top-state fraction diff: median {st.median(tdiffs):+.3f}, range {min(tdiffs):+.3f} to {max(tdiffs):+.3f}; negative in {sum(1 for x in tdiffs if x<0)} of {len(tdiffs)}.\n")
P("Reference spread (the same statistic for kept members, each against its other kept quad-mates, so the lost diffs have a yardstick; abs repeats r02..r10 kept use their neighbours):\n")
kd = []; ktd = []
for r in rows:
    if r["lost"]: continue
    ms = [m for m in mates_of(r) if not m["lost"]]
    if r["quad"] == "abs": ms = [m for m in mates_of(r) if not m["lost"]]
    if not ms: continue
    kd.append(r["gpu_aw_mean"]-st.mean(m["gpu_aw_mean"] for m in ms)); ktd.append(r["gpu_top_mean"]-st.mean(m["gpu_top_mean"] for m in ms))
kds = sorted(kd)
P(f"- kept-vs-kept-mates GPU mean diff (n={len(kd)}): median {st.median(kd):+.1f} MHz, 10th to 90th percentile {kds[int(.1*len(kds))]:+.1f} to {kds[int(.9*len(kds))]:+.1f}, min {min(kd):+.1f}, max {max(kd):+.1f}; negative in {sum(1 for x in kd if x<0)}.")
P(f"- kept-vs-kept-mates top-state diff: median {st.median(ktd):+.3f}, min {min(ktd):+.3f}, max {max(ktd):+.3f}.")
# lost vs kept distribution
lost = [r["gpu_aw_mean"] for r in rows if r["lost"]]; kept = [r["gpu_aw_mean"] for r in rows if not r["lost"]]
P(f"\nWhole-session view: lost GPU mean {min(lost):.1f} to {max(lost):.1f} (median {st.median(lost):.1f}); kept {min(kept):.1f} to {max(kept):.1f} (median {st.median(kept):.1f}). Kept members at or below the highest lost value ({max(lost):.1f}): {sum(1 for x in kept if x<=max(lost))} of {len(kept)}. Lost members below 1290 MHz: {sum(1 for x in lost if x<1290)} of {len(lost)}; kept below 1290: {sum(1 for x in kept if x<1290)} of {len(kept)}.")
fast = [r for r in rows if r["gpu_aw_mean"] >= 1330]
P(f"Members with GPU mean >= 1330 MHz ('fast mode'): {len(fast)} ({', '.join(r['short'] for r in fast)}); lost among them: {sum(1 for r in fast if r['lost'])}. Their decode spans are the shortest ({min(r['decode_s'] for r in fast):.1f} to {max(r['decode_s'] for r in fast):.1f} s vs {st.median([r['decode_s'] for r in rows if r['gpu_aw_mean']<1330]):.1f} s median for the rest).")
slow_kept = [r for r in rows if not r["lost"] and r["gpu_aw_mean"] < 1330]
sk = [r["gpu_aw_mean"] for r in slow_kept]
lt3 = [r["gpu_aw_last_third"]-r["gpu_aw_first_third"] for r in rows if r["lost"]]
kt3s = [r["gpu_aw_last_third"]-r["gpu_aw_first_third"] for r in slow_kept]
kt3f = [r["gpu_aw_last_third"]-r["gpu_aw_first_third"] for r in fast]
P(f"\nWhy the lost-vs-mates differences are all negative: the mates include 'fast mode' members, which the lost never are. Against kept slow-mode members only (GPU mean < 1330, n={len(slow_kept)}): kept slow median {st.median(sk):.1f} MHz (range {min(sk):.1f} to {max(sk):.1f}) vs lost median {st.median(lost):.1f}; kept slow top-state median {st.median([r['gpu_top_mean'] for r in slow_kept]):.3f} vs lost {st.median([r['gpu_top_mean'] for r in rows if r['lost']]):.3f}. Lost members' GPU means lie below the kept-slow median ({st.median(sk):.1f}) in {sum(1 for x in lost if x < st.median(sk))} of 10 cases, but kept-slow members {sum(1 for x in sk if x <= max(lost))} of {len(sk)} are at or below the highest lost value, so the lost sit at the low edge of the slow group, not outside it.")
from math import comb
P(f"If the 10 lost were a random draw from the 50, the chance that none falls among the 8 fast-mode members is C(42,10)/C(50,10) = {comb(42,10)/comb(50,10):.3f}.")
P(f"In-decode drift (mean of last third of decode records minus mean of first third, GPU MHz): lost median {st.median(lt3):+.1f}; kept slow-mode median {st.median(kt3s):+.1f}; kept fast-mode median {st.median(kt3f):+.1f}. A fall of about 100 to 130 MHz within each 56 s decode is present in every slow-mode member, lost or kept.")
P("\n## 4. Session trend: GPU mean frequency vs collection order\n")
P("OLS slope in MHz per collection-order step, implied change across the span, Spearman rho (rank correlation), and two-sided permutation p for rho (20000 shuffles, seed 1). A permutation p is descriptive here: members are not independent draws.\n")
P("| subset | n | slope MHz/step | change across span MHz | Spearman rho | perm p |")
P("|--|--|--|--|--|--|")
trend(rows, "all members"); trend([r for r in rows if not r["lost"]], "kept only")
trend([r for r in rows if r["order"] >= 7], "all, from #7 on (after abs warm-in)")
trend([r for r in rows if r["order"] >= 7 and not r["lost"]], "kept only, from #7 on")
trend([r for r in rows if r["order"] >= 11], "all, null blocks only (#11-50)")
trend([r for r in rows if r["order"] >= 11 and not r["lost"]], "kept only, null blocks only")
trend(rows[:6], "first six (abs r01-r06)", )
P("\nSame with the per-member GPU minimum (the lowest 10 Hz record in decode):\n")
P("| subset | n | slope MHz/step | change across span MHz | Spearman rho | perm p |")
P("|--|--|--|--|--|--|")
trend(rows, "all members, GPU min", "gpu_aw_min"); trend([r for r in rows if not r["lost"]], "kept only, GPU min", "gpu_aw_min")
P("\nBlock medians of GPU mean (kept only), in collection order of blocks (abs split into r01-r05 and r06-r10):\n")
P("| block | kept n | median GPU mean | lowest | highest |")
P("|--|--|--|--|--|")
groups = [("abs r01-05", [r for r in rows if r["quad"]=="abs" and r["order"]<=5]), ("abs r06-10", [r for r in rows if r["quad"]=="abs" and r["order"]>5])] + [(f"b{n:02d}", [r for r in rows if r["quad"]==f"b{n:02d}"]) for n in range(1,11)]
for name, g in groups:
    k = [r["gpu_aw_mean"] for r in g if not r["lost"]]
    P(f"| {name} | {len(k)} | {st.median(k):.1f} | {min(k):.1f} | {max(k):.1f} |")
open(M + "/M2.body.md", "w").write("\n".join(L) + "\n")
print("\n".join(L[-60:]))
