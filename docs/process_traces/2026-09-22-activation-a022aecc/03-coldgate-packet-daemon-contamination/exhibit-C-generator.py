"""Exhibit C generator — executed at the bench over the READ-ONLY night archives and the checkout.

Every number below is computed by this script; nothing is transcribed by hand.
Run from the worktree root:  python3 exhibit-C-generator.py 91f80870 > exhibit-C-executed-evidence.md
"""
import hashlib, json, math, os, statistics, subprocess, sys, time

rev = sys.argv[1]
SELF = os.path.abspath(__file__)
TONIGHT = "/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night"
PRIOR_ARCHIVE = "/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night"
PRIOR_CUSTODY = ("/Users/edr/night-custody/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-"
                 "d45378c6010b538ca1bb74ae0f2222dceb4df1e4/night")
PRIOR = PRIOR_ARCHIVE if os.path.isdir(PRIOR_ARCHIVE) else PRIOR_CUSTODY

_read = {}


def sha(path):
    d = hashlib.sha256(open(path, "rb").read()).hexdigest()
    _read[path] = d
    return d


def jload(path):
    sha(path)
    return json.load(open(path))


def jlines(path):
    sha(path)
    return [json.loads(l) for l in open(path) if l.strip()]


def base(cmd):
    return os.path.basename((cmd or "").split()[0]) if cmd else "<none>"


def quant(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def chi_square_lower_decile(df):
    """Invert the regularized lower gamma P(df/2, x/2) at p=0.10; stdlib only (algorithm of
    joulewise.quiet_predicate_campaign.chi_square_lower_decile at this revision)."""
    shape = df / 2
    low, high = 0.0, float(df)
    for _ in range(200):
        mid = (low + high) / 2
        x = mid / 2
        term = total = 1 / shape
        for k in range(1, 2000):
            term *= x / (shape + k)
            total += term
            if term <= total * 1e-15:
                break
        probability = total * math.exp(-x + shape * math.log(x) - math.lgamma(shape))
        if probability < 0.10:
            low = mid
        else:
            high = mid
    return (low + high) / 2


print("# Exhibit C — executed evidence (generator output, verbatim)\n")
print(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S %Z')} at main `{rev}` by `{os.path.basename(SELF)}`.\n")
print("Archive roots, both read-only:\n")
print(f"- TONIGHT = `{TONIGHT}`")
print(f"- PRIOR   = `{PRIOR}`" + ("  (archive copy present; preferred)" if PRIOR == PRIOR_ARCHIVE
                                  else "  (archive copy absent; custody copy used)"))
print()
print("```")
print("sha256(this generator) =", hashlib.sha256(open(SELF, "rb").read()).hexdigest())
print("```\n")

# ---------------------------------------------------------------- C1
print("## C1 — registration digest check and the fields that govern this night\n")
REG = "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json"
raw = subprocess.run(["git", "show", f"{rev}:{REG}"], capture_output=True, check=True).stdout
reg_sha = hashlib.sha256(raw).hexdigest()
reg = json.loads(raw)
pinned = None
for line in subprocess.run(["git", "show", f"{rev}:joulewise/night_gate.py"],
                           capture_output=True, text=True, check=True).stdout.splitlines():
    if line.startswith("QPE01_PILOT_REGISTRATION_SHA256"):
        pinned = line.split("=", 1)[1].strip().strip('"')
print("```")
print(f"command: git show {rev}:{REG} | shasum -a 256")
print(f"sha256(registration at {rev})              = {reg_sha}")
print(f"night_gate.QPE01_PILOT_REGISTRATION_SHA256 = {pinned}")
print(f"MATCH = {reg_sha == pinned}")
print()
for k in ("busy_cores_role", "exclusions", "load_generator", "stop_branches", "sizing",
          "block_two", "cadence_exclusion", "envelope_s", "envelopes", "interior_s",
          "minimum_retained", "minimum_adjacent_pairs", "pairing_rule"):
    print(f"{k} = {json.dumps(reg.get(k), indent=2) if isinstance(reg.get(k), (dict, list)) else json.dumps(reg.get(k))}")
print("```\n")

# ---------------------------------------------------------------- C2
print("## C2 — TONIGHT per-envelope table and headline summary fields\n")
print(f"Sources: `{TONIGHT}/evidence/summary.json`, `{TONIGHT}/evidence/envelope-NN/session.json`, "
      f"`{TONIGHT}/evidence_envelopes.jsonl`.\n")
summ = jload(f"{TONIGHT}/evidence/summary.json")
chain = {e["index"]: e for e in jlines(f"{TONIGHT}/evidence_envelopes.jsonl")}
envs = {e["index"]: e for e in summ["envelopes"]}
sessions = {}
print("```")
hdr = (f"{'idx':>3} {'joules':>10} {'excluded':<22} {'net_time_attest':<14} "
       f"{'chain_drift_s':>13} {'sess_drift_s':>12} {'anchor':<9} {'interior':<9} "
       f"{'native':>7} {'bc_med':>7} {'bc_max':>7} {'obs_cpu_s':>9}")
print(hdr)
for i in range(1, 13):
    sp = f"{TONIGHT}/evidence/envelope-{i:02d}/session.json"
    s = jload(sp)
    sessions[i] = s
    e = envs[i]
    ch = chain.get(i, {})
    j = e.get("joules")
    jtxt = "None" if j is None else format(j, "10.3f")
    bc = e.get("busy_cores") or {}
    print(f"{i:>3} {jtxt:>10} "
          f"{(','.join(e['excluded']) or '-'):<22} {str(e.get('network_time_attestation')):<14} "
          f"{ch.get('start_drift_s', float('nan')):13.4f} {s.get('start_drift_s', float('nan')):12.4f} "
          f"{str(s['power']['anchor'].get('status')):<9} {str(s['interior'].get('status')):<9} "
          f"{s['interior'].get('native_samples', -1):>7} "
          f"{(bc.get('median') if bc.get('median') is not None else float('nan')):7.4f} "
          f"{(bc.get('max') if bc.get('max') is not None else float('nan')):7.4f} "
          f"{e.get('observer_cpu_s', float('nan')):9.3f}")
print()
print("session.json sha256 per envelope:")
for i in range(1, 13):
    print(f"  {i:02d} {_read[f'{TONIGHT}/evidence/envelope-{i:02d}/session.json']}")
print()
print("summary headline fields:")
for k in ("status", "evidence_status", "retained", "retained_pairs", "pair_sd_j", "pair_df",
          "s_upper", "s_upper_factor", "s_upper_reason", "block_two_pairs", "block_two_pairs_reason",
          "block_two_stop", "cutoff_authority", "busy_cores", "clean_machine_busy_cores",
          "observer_floor_cores", "observer_support_s", "single_envelope_sd_j",
          "unfiltered_single_envelope_sd_j", "first_to_last_retained_drift_j", "max_abs_delta_j",
          "adjacent_pair_sd_j", "top_up", "busy_cores_role", "busy_cores_source"):
    v = summ.get(k)
    print(f"  {k} = {json.dumps(v)}")
print()
print("sizing_pairs (the six disjoint registered pairs; all deltas):")
for p in summ["sizing_pairs"]:
    print(f"  pair ({p['left']},{p['right']})  delta_j = {p['delta_j']:+.6f}  retained={p['retained']}")
print("sizing_pairs delta_j list =", [round(p["delta_j"], 6) for p in summ["sizing_pairs"]])
print()
print("adjacent_pairs (overlapping; diagnostic only per the summary):")
for p in summ["adjacent_pairs"]:
    print(f"  pair ({p['left']},{p['right']})  delta_j = {p['delta_j']:+.6f}  retained={p['retained']}")
print("```\n")

# ---------------------------------------------------------------- C3
print("## C3 — TONIGHT load journal `evidence_busy_cores.jsonl`\n")
rows = jlines(f"{TONIGHT}/evidence_busy_cores.jsonl")
print("```")
print(f"file: {TONIGHT}/evidence_busy_cores.jsonl")
print(f"sha256 = {_read[f'{TONIGHT}/evidence_busy_cores.jsonl']}")
print(f"row count = {len(rows)}")
def has_metrics(r):
    return isinstance(r.get("observation"), dict) and isinstance(r["observation"].get("metrics"), dict)


bad = [r for r in rows if not has_metrics(r)]
good = [r for r in rows if has_metrics(r)]
print(f"rows without observation.metrics = {len(bad)}")
for r in bad:
    print(f"  monotonic_start={r.get('monotonic_start')} error={json.dumps(r.get('error'))}")
print()
agg = {}
for r in good:
    for c in r["observation"]["metrics"].get("top_consumers", []):
        a = agg.setdefault(base(c.get("command")), {"n": 0, "sum": 0.0, "max": 0.0, "observer": set()})
        a["n"] += 1
        a["sum"] += c["busy_cores"]
        a["max"] = max(a["max"], c["busy_cores"])
        a["observer"].add(bool(c.get("observer")))
print(f"top_consumers aggregation over {len(good)} rows with metrics, by command basename, "
      "sorted by total busy-core-seconds share (sum of per-sample busy_cores); top 10:")
print(f"{'command':<28} {'rows':>5} {'total':>10} {'mean':>9} {'max':>9}  observer_flag")
for name, a in sorted(agg.items(), key=lambda kv: -kv[1]["sum"])[:10]:
    print(f"{name:<28} {a['n']:>5} {a['sum']:>10.4f} {a['sum']/a['n']:>9.4f} {a['max']:>9.4f}  "
          f"{sorted(a['observer'])}")
print()
print(f"(full basename list, {len(agg)} distinct: " + ", ".join(sorted(agg)) + ")")
print()
print("per-envelope join: a journal row belongs to envelope i when its monotonic_start lies in")
print("[scheduled_mono_s, scheduled_mono_s + 600) of summary envelopes[i].")
print(f"{'idx':>3} {'rows':>5} {'fseventsd>=0.9':>15} {'mediaanalysisd rows':>20} {'median total busy_cores':>24}")
per_env = {}
for i in range(1, 13):
    lo = envs[i]["scheduled_mono_s"]
    hi = lo + 600
    sel = [r for r in good if lo <= r["monotonic_start"] < hi]
    per_env[i] = sel
    fse = sum(1 for r in sel for c in r["observation"]["metrics"].get("top_consumers", [])
              if base(c.get("command")) == "fseventsd" and c["busy_cores"] >= 0.9)
    med = sum(1 for r in sel if any(base(c.get("command")) == "mediaanalysisd"
                                    for c in r["observation"]["metrics"].get("top_consumers", [])))
    tot = [r["observation"]["metrics"]["busy_cores"] for r in sel]
    print(f"{i:>3} {len(sel):>5} {fse:>15} {med:>20} "
          f"{(statistics.median(tot) if tot else float('nan')):>24.4f}")
unassigned = len(good) - sum(len(v) for v in per_env.values())
print(f"rows not inside any scheduled envelope window = {unassigned}")
print()
t0 = rows[0]["monotonic_start"]
print("first 25 rows (offset_s from the first journal row's monotonic_start):")
print(f"{'offset_s':>9} {'busy_cores':>11}  top 3 consumers (basename=busy_cores)")
for r in rows[:25]:
    if not has_metrics(r):
        print(f"{r['monotonic_start']-t0:9.1f} {'ERROR':>11}  {json.dumps(r.get('error'))}")
        continue
    m = r["observation"]["metrics"]
    top3 = "  ".join(f"{base(c.get('command'))}={c['busy_cores']:.4f}"
                     for c in m.get("top_consumers", [])[:3])
    print(f"{r['monotonic_start']-t0:9.1f} {m['busy_cores']:11.4f}  {top3}")
print("```\n")

# ---------------------------------------------------------------- C4
print("## C4 — PRIOR night (qpe01-pilot-n1-20260922-0217), same aggregation\n")
psum = jload(f"{PRIOR}/evidence/summary.json")
prows = jlines(f"{PRIOR}/evidence_busy_cores.jsonl")
pgood = [r for r in prows if isinstance(r.get("observation"), dict)
         and isinstance(r["observation"].get("metrics"), dict)]
print("```")
print(f"file: {PRIOR}/evidence_busy_cores.jsonl")
print(f"sha256 = {_read[f'{PRIOR}/evidence_busy_cores.jsonl']}")
print(f"summary.json sha256 = {_read[f'{PRIOR}/evidence/summary.json']}")
print(f"row count = {len(prows)}; rows with metrics = {len(pgood)}")
pagg = {}
for r in pgood:
    for c in r["observation"]["metrics"].get("top_consumers", []):
        a = pagg.setdefault(base(c.get("command")), {"n": 0, "sum": 0.0, "max": 0.0})
        a["n"] += 1
        a["sum"] += c["busy_cores"]
        a["max"] = max(a["max"], c["busy_cores"])
print(f"{'command':<28} {'rows':>5} {'total':>10} {'mean':>9} {'max':>9}")
for name, a in sorted(pagg.items(), key=lambda kv: -kv[1]["sum"])[:6]:
    print(f"{name:<28} {a['n']:>5} {a['sum']:>10.4f} {a['sum']/a['n']:>9.4f} {a['max']:>9.4f}")
print()
print("PRIOR summary busy_cores quantiles =", json.dumps(psum.get("busy_cores")))
print("PRIOR status =", json.dumps(psum.get("status")), "; evidence_status =",
      json.dumps(psum.get("evidence_status")), "; retained =", psum.get("retained"),
      "; retained_pairs =", psum.get("retained_pairs"))
pret = [(e["index"], e["joules"]) for e in psum["envelopes"] if not e["excluded"]]
print("PRIOR retained envelopes (excluded == []):")
for i, j in pret:
    print(f"  envelope {i:02d}  joules = {j:.6f}")
print("PRIOR all envelopes (index, joules, excluded, busy_cores median):")
for e in psum["envelopes"]:
    jv = e.get("joules")
    jt = "None" if jv is None else format(jv, "10.3f")
    ex = ",".join(e["excluded"]) or "-"
    bcm = (e.get("busy_cores") or {}).get("median")
    print(f"  {e['index']:02d} {jt:>10} {ex:<62} {bcm}")
print("```\n")

# ---------------------------------------------------------------- C5
print("## C5 — TONIGHT t0 receipt and result\n")
rec = jload(f"{TONIGHT}/receipt.json")
res = jload(f"{TONIGHT}/result.json")
print("```")
print(f"receipt.json sha256 = {_read[f'{TONIGHT}/receipt.json']}")
print(f"result.json  sha256 = {_read[f'{TONIGHT}/result.json']}")
c3 = rec["conditions"][2]
print(f"conditions[2].condition_id = {c3['condition_id']}  status = {c3['status']}")
m = c3["measured"]
for k in ("load_1m", "load_average_raw", "agent_census_exit_code", "agent_census_stdout",
          "cpu_speed_limit", "ac_power_raw", "hid_idle_raw", "thermal_raw", "detail"):
    print(f"  {k} = {json.dumps(m.get(k))}")
print()
hits = []


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("top_consumers_at_decision", "quiet_admission"):
                hits.append(path + "/" + k)
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + f"[{i}]")


walk(rec)
print("walk of the whole receipt for keys named top_consumers_at_decision or quiet_admission:")
print("  hits =", hits if hits else "NONE — neither key appears anywhere in the receipt")
print("  receipt top-level keys =", sorted(rec.keys()))
print("  receipt_class =", json.dumps(rec.get("receipt_class")),
      "; verdict =", json.dumps(rec.get("verdict")),
      "; refusal =", json.dumps(rec.get("refusal")))
print("  condition statuses =", {c["condition_id"]: c["status"] for c in rec["conditions"]})
print()
print("result.json: census_count =", res.get("census_count"), "; census_hits =",
      json.dumps(res.get("census_hits")), "; verdict =", json.dumps(res.get("verdict")),
      "; chain_exit_code =", json.dumps(res.get("chain_exit_code")),
      "; aborted_reason =", json.dumps(res.get("aborted_reason")))
print("```\n")

# ---------------------------------------------------------------- C6
print("## C6 — machine-state probes executed now (unified log, `ps`, `mount`)\n")
print("```")
argv = ["/usr/bin/log", "show", "--last", "30h", "--predicate",
        'process == "fseventsd" AND eventMessage CONTAINS "scan_old"', "--style", "compact"]
print("command:", " ".join(f"'{a}'" if " " in a else a for a in argv))
t = time.monotonic()
out = subprocess.run(argv, capture_output=True, text=True)
dt = time.monotonic() - t
lines = out.stdout.splitlines()
print(f"rc = {out.returncode}; wall = {dt:.1f} s; total stdout lines = {len(lines)}")
if out.stderr.strip():
    print("stderr:", out.stderr.strip()[:500])
body = [l for l in lines if l[:4].isdigit()]
print(f"timestamped lines = {len(body)}")
if body:
    print("first:", body[0][:200])
    print("last: ", body[-1][:200])
    print()
    print("hourly histogram (cut -c1-13 | sort | uniq -c):")
    hist = {}
    for l in body:
        hist[l[:13]] = hist.get(l[:13], 0) + 1
    for k in sorted(hist):
        print(f"  {hist[k]:>7} {k}")
else:
    print("no timestamped matching lines")
print()
print(f"command: ps -axo pid,pcpu,time,etime,rss,command | grep '[f]seventsd'   (wall clock "
      f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')})")
ps = subprocess.run("ps -axo pid,pcpu,time,etime,rss,command | grep '[f]seventsd'",
                    shell=True, capture_output=True, text=True)
print(ps.stdout.rstrip() or "(no match)")
print()
print("command: mount | grep -v devfs")
mt = subprocess.run("mount | grep -v devfs", shell=True, capture_output=True, text=True)
print(mt.stdout.rstrip())
print("```\n")

# ---------------------------------------------------------------- C7
print("## C7 — counterfactual sizing (DIAGNOSTIC ONLY — not a re-verdict, not registered)\n")
print("The registration fixes the six disjoint pairs and the sizing rule; dropping a pair after "
      "seeing the data is NOT admissible sizing. The (ii) row exists only to show how much of "
      "the sizing outcome rides on pair (1,2).\n")
print("```")
print("formula (registration `sizing`, ruling 46b):")
print("  s_pair   = sample SD of the pair deltas (n-1 denominator)")
print("  s_upper  = s_pair * sqrt((n-1) / chi2_0.10(n-1))     [one-sided upper 90% chi-square bound]")
print(f"  pairs    = max({reg['sizing']['minimum_pairs']}, ceil({reg['sizing']['multiplier']} "
      f"* s_upper**2 / {reg['sizing']['delta_j']}**2)); stop above "
      f"{reg['sizing']['maximum_pairs']} pairs")
print("  chi2_0.10 computed by the stdlib lower-gamma inversion of "
      "joulewise.quiet_predicate_campaign.chi_square_lower_decile (scipy not importable here:",
      end=" ")
try:
    import scipy  # noqa: F401
    print("scipy IS importable)")
except Exception as ex:
    print(f"{type(ex).__name__})")
print()
for df in (3, 4, 5):
    q = chi_square_lower_decile(df)
    print(f"  chi2_0.10(df={df}) = {q:.9f}   factor sqrt(df/chi2) = {math.sqrt(df/q):.9f}")
print(f"  cross-check: summary.s_upper_factor = {summ['s_upper_factor']:.9f} "
      f"(df = {summ['pair_df']}) -> agreement "
      f"{abs(summ['s_upper_factor'] - math.sqrt(summ['pair_df']/chi_square_lower_decile(summ['pair_df']))) < 1e-9}")
print()
deltas = [p["delta_j"] for p in summ["sizing_pairs"]]
print("registered pair deltas (J):", [round(d, 6) for d in deltas])


def size(ds):
    n = len(ds)
    s = statistics.stdev(ds)
    df = n - 1
    q = chi_square_lower_decile(df)
    f = math.sqrt(df / q)
    su = s * f
    pairs = max(reg["sizing"]["minimum_pairs"],
                math.ceil(reg["sizing"]["multiplier"] * su ** 2 / reg["sizing"]["delta_j"] ** 2))
    print(f"    n = {n}; df = {df}; mean delta = {statistics.mean(ds):+.6f} J")
    print(f"    s_pair  = {s:.6f} J")
    print(f"    chi2_0.10({df}) = {q:.9f}; factor = {f:.9f}")
    print(f"    s_upper = {su:.6f} J")
    print(f"    pairs   = max({reg['sizing']['minimum_pairs']}, ceil({reg['sizing']['multiplier']}"
          f" * {su:.6f}**2 / {reg['sizing']['delta_j']}**2)) = {pairs}")
    print(f"    stop (pairs > {reg['sizing']['maximum_pairs']})? "
          f"{pairs > reg['sizing']['maximum_pairs']}")
    return s, su, pairs


print()
print("(i) all six pairs as registered [AUTHORITATIVE — this is what the summary reports]:")
i_s, i_su, i_p = size(deltas)
print(f"    summary agreement: pair_sd_j = {summ['pair_sd_j']:.6f} -> "
      f"{abs(summ['pair_sd_j'] - i_s) < 1e-6}; s_upper = {summ['s_upper']:.6f} -> "
      f"{abs(summ['s_upper'] - i_su) < 1e-6}; block_two_pairs = {summ['block_two_pairs']} -> "
      f"{summ['block_two_pairs'] == i_p}")
print()
print("(ii) pairs 2-6 only, dropping pair (1,2) [COUNTERFACTUAL, NOT ADMISSIBLE SIZING]:")
ii_s, ii_su, ii_p = size(deltas[1:])
print()
print("(iii) PRIOR night: retained_pairs =", psum["retained_pairs"],
      "-> 0 pairs; no pair SD, no s_upper and no block-two sizing were computable from it.")
print("      PRIOR summary pair_sd_j =", json.dumps(psum.get("pair_sd_j")),
      "; s_upper =", json.dumps(psum.get("s_upper")),
      "; block_two_pairs =", json.dumps(psum.get("block_two_pairs")))
print("```\n")

# ---------------------------------------------------------------- C8
print("## C8 — energy comparison, TONIGHT vs PRIOR\n")
print("```")
tj = [(e["index"], e["joules"]) for e in summ["envelopes"] if e.get("joules") is not None]
print("TONIGHT joules per envelope (over the registered 480 s interior):")
for i, j in tj:
    print(f"  {i:02d} {j:12.4f}")
pj = [j for _, j in pret]
print("PRIOR retained joules:", [round(x, 4) for x in pj],
      f"(envelopes {[i for i, _ in pret]}, read from {PRIOR}/evidence/summary.json)")
tmed = statistics.median([j for _, j in tj])
pmed = statistics.median(pj)
print(f"TONIGHT median joules = {tmed:.4f} over {len(tj)} envelopes")
print(f"PRIOR   median joules = {pmed:.4f} over {len(pj)} retained envelopes")
print(f"ratio of medians TONIGHT/PRIOR = {tmed/pmed:.4f}")
print(f"delta J (median) = {tmed - pmed:+.4f} J")
print(f"implied extra mean power over the 480 s interior = ({tmed:.4f} - {pmed:.4f}) / 480 "
      f"= {(tmed - pmed)/480:+.4f} W")
tmin = min(j for _, j in tj)
print(f"TONIGHT minimum envelope = {tmin:.4f} J -> extra mean power vs PRIOR median "
      f"= {(tmin - pmed)/480:+.4f} W")
print(f"TONIGHT envelope 01 (the outlier pair's left member) = {dict(tj)[1]:.4f} J -> "
      f"extra mean power vs PRIOR median = {(dict(tj)[1] - pmed)/480:+.4f} W")
print("```\n")

# ---------------------------------------------------------------- anchors
print("## C9 — file digests read by this generator (self-anchoring)\n")
print("```")
for p in sorted(_read):
    print(f"{_read[p]}  {p}")
print()
print("sha256(this generator) =", hashlib.sha256(open(SELF, "rb").read()).hexdigest())
print("```")
