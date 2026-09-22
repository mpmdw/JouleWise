#!/usr/bin/env python3
"""Exhibit C generator: reads ONLY the harvest archive's per-envelope session.json
files and prints the fields the packet relies on. Output is captured verbatim
into exhibit-C-executed-evidence.md. No narrative input."""
import json, math, hashlib, sys, os
A = "/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence"
STAMPS = ("pre_spawn", "sampling_started", "first_parse", "post_parse", "sampling_stopped")
print("archive:", A)
print("envelope | anchor status/detail | offset(pre_spawn) s | offset(sampling_stopped) s | offset change ms | span ms (max-min over 5 stamps) | baseline s (stopped-pre_spawn, monotonic) | equiv rate ppm (change/baseline) | anchor-only H ms | effective bound ms | interior status | span_mismatch | coverage-480 s | native samples | rail_sum_w W | error_bound_j | net_time_prov")
rows = []
for n in range(1, 13):
    e = f"{n:02d}"
    p = f"{A}/envelope-{e}/session.json"
    s = json.load(open(p))
    an = s["power"]["anchor"]; cs = an["clock_stamps"]; i = s["interior"]
    off = {k: cs[k]["epoch_s"] - (cs[k]["monotonic_before_s"] + cs[k]["monotonic_after_s"]) / 2 for k in STAMPS}
    span = max(off.values()) - min(off.values())
    base = cs["sampling_stopped"]["monotonic_after_s"] - cs["pre_spawn"]["monotonic_before_s"]
    change = off["sampling_stopped"] - off["pre_spawn"]
    pw = (i.get("power") or {})
    cov = (pw.get("rail_coverage_s") or {}).get("rail_sum_w")
    det = an.get("detail") or an.get("status")
    H = an.get("anchor_only_bound_s"); eb = an.get("effective_clock_anchor_bound_s")
    print(f"{e} | {an['status']}/{det} | {off['pre_spawn']:.6f} | {off['sampling_stopped']:.6f} | {change*1e3:+.3f} | {span*1e3:.3f} | {base:.1f} | {change/base*1e6:+.2f} | {'' if H is None else f'{H*1e3:.3f}'} | {'' if eb is None else f'{eb*1e3:.3f}'} | {i['status']} | {i.get('span_mismatch')} | {'' if cov is None else repr(cov-480.0)} | {i.get('native_samples')} | {'' if pw.get('rail_sum_w') is None else f'{pw['rail_sum_w']:.4f}'} | {i.get('error_bound_j')} | {s.get('network_time_provenance')}")
    rows.append((e, s))
print()
print("sha256 of each session.json read above:")
for e, s in rows:
    p = f"{A}/envelope-{e}/session.json"
    print(hashlib.sha256(open(p, "rb").read()).hexdigest(), " envelope-" + e + "/session.json")
print()
print("float64 ulp at epoch scale:", math.ulp(1790069880.0), "s ; at 480 s:", math.ulp(480.0))
print("per-envelope start drift s:", [round(json.load(open(f"{A}/envelope-{n:02d}/session.json")).get("collector_start_drift_s", float('nan')), 3) if "collector_start_drift_s" in json.load(open(f"{A}/envelope-{n:02d}/session.json")) else None for n in range(1, 13)])
summ = json.load(open(f"{A}/summary.json"))
print("summary.json: retained", summ.get("retained"), "status", summ.get("status"), "block_two_stop", summ.get("block_two_stop"), "unfiltered_single_envelope_sd_j", summ.get("unfiltered_single_envelope_sd_j"), "single_envelope_sd_j", summ.get("single_envelope_sd_j"))
print("per-envelope excluded reasons:", [(x["index"], x.get("excluded")) for x in summ["envelopes"]])
print("per-envelope collector_start_drift_s:", [(x["index"], round(x.get("collector_start_drift_s", -1), 2)) for x in summ["envelopes"]])
print("network_time_provenance_reason (envelope 01):", json.load(open(f"{A}/envelope-01/session.json")).get("network_time_provenance_reason"))
