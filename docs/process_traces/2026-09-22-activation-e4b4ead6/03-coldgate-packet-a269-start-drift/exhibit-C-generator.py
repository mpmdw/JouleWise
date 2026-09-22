"""Exhibit C generator — executed at the bench over the READ-ONLY harvest archive and the checkout; prints everything it computes."""
import json, hashlib, subprocess, time, os, sys, statistics
A = "/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night"
rev = sys.argv[1]
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def _env_entry(summ, i):
    env = summ["envelopes"]
    if isinstance(env, dict): return env[str(i)]
    for e in env:
        if e.get("envelope") == i or e.get("index") == i: return e
    return env[i-1]
print("# Exhibit C — executed evidence (generator output, verbatim)\n")
print(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S %Z')} at main `{rev}` over `{A}` (read-only).\n")
print("## C1 — registration digest and fields\n```")
p = "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json"
print("sha256", sha(p), p)
d = json.load(open(p))
for k in ("envelope_s","envelopes","settle_s","window_max_s","interior_offset_s","interior_s","start_drift_max_s","minimum_retained","minimum_adjacent_pairs","cadence_exclusion","exclusions","chain_source_sha256","ruling"):
    print(k, "=", json.dumps(d.get(k)))
print("slot_pitch_s present:", "slot_pitch_s" in d)
print("window arithmetic: settle + 12*600 =", d["settle_s"]+12*d["envelope_s"], "; settle + 11*620 + 600 =", d["settle_s"]+11*620+600, "; window_max_s =", d["window_max_s"])
print("```\n")
print("## C2 — per-envelope serial tail from the archive stamps (monotonic seconds)\n```")
env = [json.loads(l) for l in open(f"{A}/evidence_envelopes.jsonl")]
print("evidence_envelopes.jsonl sha256", sha(f"{A}/evidence_envelopes.jsonl"))
print(f"{'env':>3} {'chain_drift':>11} {'sess_drift':>10} {'stop-sched':>10} {'postparse-stop':>14} {'end-postparse':>13} {'nextpre-end':>11} {'groups':>6}  anchor_status  excluded(summary)")
summ = json.load(open(f"{A}/evidence/summary.json"))
print("summary.json sha256", sha(f"{A}/evidence/summary.json"))
prev_end=None
rows=[]
for i,e in enumerate(env, start=1):
    sp = f"{A}/evidence/envelope-{i:02d}/session.json"
    s = json.load(open(sp))
    st = s["power"]["anchor"]["clock_stamps"]
    m = lambda k: st[k]["monotonic_before_s"]
    sched = e.get("scheduled_mono_s")
    groups = len(e.get("cleanup",{}).get("groups",[])) if isinstance(e.get("cleanup"),dict) else None
    ex = _env_entry(summ, i)["excluded"]
    nextpre = ""
    if prev_end is not None: rows[-1]["nextpre"] = m("pre_spawn")-prev_end
    rows.append(dict(i=i, chain=e.get("start_drift_s"), sess=s.get("start_drift_s"), stop=m("sampling_stopped")-sched, pp=m("post_parse")-m("sampling_stopped"), end=s["end_stamp"]["monotonic_before_s"]-m("post_parse") if "end_stamp" in s else None, groups=groups, status=s["power"]["anchor"]["status"], ex=ex, sha=sha(sp)))
    prev_end = s["end_stamp"]["monotonic_before_s"] if "end_stamp" in s else None
for r in rows:
    print(f"{r['i']:>3} {r['chain']:>11.3f} {r['sess']:>10.3f} {r['stop']:>10.3f} {r['pp']:>14.3f} {r['end'] if r['end'] is None else round(r['end'],3):>13} {r.get('nextpre','') if r.get('nextpre') is None or r.get('nextpre')=='' else round(r['nextpre'],3):>11} {r['groups']:>6}  {r['status']:<13} {r['ex']}")
print("session.json sha256 per envelope:"); [print(f"  {r['i']:02d} {r['sha']}") for r in rows]
print("```\n")
print("## C3 — summary.json exclusion facts\n```")
for i in range(1,13):
    ent = _env_entry(summ, i)
    print(i, "excluded=", ent["excluded"], "start_drift_s=", round(ent.get("start_drift_s",0),3))
sd = [i for i in range(1,13) if "start_drift" in _env_entry(summ,i)["excluded"]]
only = [i for i in sd if _env_entry(summ,i)["excluded"]==["start_drift"]]
print("start_drift-excluded:", sd, "; excluded for start_drift ALONE:", only)
print("retained", summ["retained"], "retained_pairs", summ["retained_pairs"], "status", summ["status"])
print("```\n")
print("## C4 — attestation query cost (executed twice; `/usr/bin/log show --info --debug --style syslog --predicate 'process == \"timed\"' --start '2026-09-22 03:00:00' --end '2026-09-22 03:10:01'`)\n```")
for k in range(2):
    t=time.monotonic(); out=subprocess.run(["/usr/bin/log","show","--info","--debug","--style","syslog","--predicate",'process == "timed"',"--start","2026-09-22 03:00:00","--end","2026-09-22 03:10:01"],capture_output=True,text=True); dt=time.monotonic()-t
    print(f"run {k+1}: rc={out.returncode} lines={len(out.stdout.splitlines())} wall={dt:.3f}s")
print("```\n")
print("## C5 — group-census cost (executed: `/usr/bin/pgrep -lf -g <pgid> .` for one dead pgid, 20 runs; and one batched `pgrep -g <list>` over 113 dead pgids)\n```")
ts=[]
for k in range(20):
    t=time.monotonic(); subprocess.run(["/usr/bin/pgrep","-lf","-g","999999","."],capture_output=True); ts.append(time.monotonic()-t)
print(f"single pgrep: median {statistics.median(ts)*1000:.1f} ms, max {max(ts)*1000:.1f} ms; x113 at median = {statistics.median(ts)*113:.2f} s")
pg=",".join(str(999000+i) for i in range(113))
t=time.monotonic(); subprocess.run(["/usr/bin/pgrep","-lf","-g",pg,"."],capture_output=True); print(f"batched pgrep over 113 pgids: {(time.monotonic()-t)*1000:.1f} ms")
print("groups journaled per envelope (evidence_envelopes.jsonl cleanup.groups):", [ (len(e['cleanup']['groups']) if isinstance(e.get('cleanup'),dict) and 'groups' in e['cleanup'] else None) for e in env])
print("```\n")
print("## C6 — plist parse + derive cost at the bench (envelope 02 raw plist via the tracked collector's parse_frames; executed once)\n```")
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(),"scripts"))
try:
    import importlib; spq = importlib.import_module("sample_quiet_predicate_evidence")
    raw = f"{A}/evidence/envelope-02/raw/powermetrics-idle-2.plist"
    print("plist", raw, "bytes", os.path.getsize(raw), "sha256", sha(raw))
    t=time.monotonic(); frames = spq.parse_frames(open(raw,'rb').read()); print(f"parse_frames: {time.monotonic()-t:.2f}s, frames={len(frames)}")
except Exception as ex:
    print("NOT EXECUTED:", type(ex).__name__, ex)
print("```\n")
