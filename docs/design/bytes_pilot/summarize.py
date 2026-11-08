import glob
import json
import statistics as st

G = 1e9
rows = []
for p in sorted(glob.glob("/Users/edr/night-archive/pilots/bytes/r_*.json")):
    r = json.load(open(p))
    a = r.get("accounting", {})
    runs = r.get("runs", [])
    if not r.get("ok"):
        rows.append((r["repo"], "FAILED", (r.get("errors") or [""])[-1].strip().splitlines()[-1][:120]))
        continue
    dec = [x["decode_tps"] for x in runs]
    pre = [x["prefill_tps"] for x in runs]
    kv_end = runs[-1]["kv_cache_bytes_end"]
    br = a["bytes_read_per_token_measured"]
    # mean KV read across decode: context grows 2048 -> 2560; full-attention KV scales linearly,
    # so mean ~ end * 2304/2560 (an approximation for hybrid/sliding caches, which hold fixed-size state)
    rows.append(dict(
        repo=r["repo"],
        moe=bool(a.get("num_experts")),
        total_B=a["total_params"] / 1e9,
        active_B=a["active_params"] / 1e9,
        disk_GB=r["on_disk_bytes"] / G,
        resident_w_GB=a["resident_weight_bytes"] / G,
        read_formula_GB=a["bytes_read_per_token_formula_4bit"] / G,
        read_meas_GB=br / G,
        kv_end_GB=kv_end / G,
        load_s=r["load_s"],
        peak_rss_GB=r["peak_rss_bytes"] / G,
        mlx_peak_GB=max(x["mlx_peak_bytes"] for x in runs) / G,
        prefill_tps=st.median(pre),
        prefill_rng=(min(pre), max(pre)),
        decode_tps=st.median(dec),
        decode_rng=(min(dec), max(dec)),
        decode_512_s=511 / st.median(dec),
        run_s=st.median([x["total_s"] for x in runs]),
        eff_bw_weights=br * st.median(dec) / G,
        quant=a.get("quant_mix_logical_params"),
        E=a.get("num_experts"), k=a.get("experts_per_tok"),
        distinct=[x["distinct_tokens_out"] for x in runs],
    ))
print(json.dumps(rows, indent=1, default=str))
