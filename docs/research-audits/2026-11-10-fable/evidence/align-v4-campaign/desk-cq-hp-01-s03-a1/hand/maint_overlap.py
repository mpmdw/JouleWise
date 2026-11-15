"""RL-171 §5 maintenance line, per leg: which OS maintenance jobs overlapped each leg attempt and phase.

Reads ONLY the leading fields of each maintenance-log.txt entry (date, time, process name; the message text
is never kept or printed), the leg records (attempt epochs, turn stamps) and each attempt's thermal journal
(G0 gate stamps and the monotonic->wall mapping only). Prints nothing from the log but process name, time
bucket and count. Gates nothing (RL-171 §5 item 2: print-only for development blocks).
Usage: python3 -I -B maint_overlap.py OUT OUT_JSON OUT_MD
"""
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

root, out_json, out_md = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
TZ = ZoneInfo("America/Los_Angeles")
NS = 10**9
ENTRY = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d+)\s+\S+\s+([^\[\s]+)\[")
NAMED = [("dasd", lambda p: p == "dasd"), ("XProtect*", lambda p: p.startswith("XProtect")),
         ("mds", lambda p: p == "mds" or p == "mds_stores"), ("mdworker*", lambda p: p.startswith("mdworker")),
         ("backupd", lambda p: p.startswith("backupd")), ("softwareupdated", lambda p: p == "softwareupdated"),
         ("mobileassetd", lambda p: p == "mobileassetd")]


def job(p):
    return next((n for n, f in NAMED if f(p)), "other:" + p)


entries, skipped = [], 0
with (root / "maintenance-log.txt").open(errors="replace") as fh:
    for i, line in enumerate(fh):
        m = ENTRY.match(line)
        if not m:
            skipped += 1
            continue
        t = datetime.strptime(f"{m.group(1)} {m.group(2)[:15]}", "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=TZ).timestamp()
        entries.append((t, job(m.group(3))))
entries.sort()
times = [e[0] for e in entries]


def local(e):
    return datetime.fromtimestamp(e, TZ).strftime("%H:%M:%S")


def gate_and_offset(thermal_path):
    rows = [json.loads(l) for l in thermal_path.read_text().splitlines() if l.strip()]
    reads = [r for r in rows if r["kind"] == "reading"]
    off = statistics.median(r["started"]["wall_ns"] - r["started"]["monotonic_ns"] for r in reads)
    g0 = [r["values"]["gate"] for r in rows if r["kind"] == "align_thermal_gate"
          and r["values"].get("gate", {}).get("kind") == "G0"][0]
    return g0, off


def count(lo, hi):
    c = Counter(j for t, j in entries if lo <= t < hi)
    return {k: c[k] for k in sorted(c)}


legs = []
for leg_dir in sorted((root / "legs").iterdir()):
    lr = json.loads((leg_dir / "leg_record.json").read_text())
    res = lr["result"]
    for a in lr["attempts"]:
        adir = root / a["output_dir"]
        th = next(adir.glob("runs/*/outputs/align_thermal.jsonl"))
        g0, off = gate_and_offset(th)
        w = lambda ns: (ns + off) / NS
        phases = [("pre-G0", a["started_epoch_s"], w(g0["start_ns"])), ("G0", w(g0["start_ns"]), w(g0["end_ns"]))]
        counted = a["output_dir"].endswith("/runtime")
        if counted:
            phases += [("G0->turn", w(g0["end_ns"]), w(res["turn_start_ns"])),
                       ("turn", w(res["turn_start_ns"]), w(res["turn_end_ns"])),
                       ("post-turn", w(res["turn_end_ns"]), a["ended_epoch_s"])]
        else:
            phases += [("after-G0 (turn+post; rejected attempt, turn stamps not read)", w(g0["end_ns"]), a["ended_epoch_s"])]
        legs.append({"leg": lr["spec"]["leg_id"], "attempt": a["attempt"], "counted": counted,
                     "contaminated": a["contaminated"], "redo_reason": a.get("redo_reason"),
                     "start": local(a["started_epoch_s"]), "end": local(a["ended_epoch_s"]),
                     "whole": count(a["started_epoch_s"], a["ended_epoch_s"]),
                     "phases": [{"phase": n, "from": local(lo), "to": local(hi), "jobs": count(lo, hi)} for n, lo, hi in phases]})

# 10-minute buckets, named jobs only, to set beside item 333's maintenance line
buckets = defaultdict(Counter)
for t, j in entries:
    if not j.startswith("other:"):
        d = datetime.fromtimestamp(t, TZ)
        buckets[d.strftime("%H:") + f"{d.minute // 10 * 10:02d}"][j] += 1
others = Counter(j for _, j in entries if j.startswith("other:"))
doc = {"entries": len(entries), "non_entry_lines": skipped, "first": local(times[0]), "last": local(times[-1]),
       "named_totals": dict(Counter(j for _, j in entries if not j.startswith("other:"))),
       "other_processes": dict(others.most_common()), "legs": legs,
       "buckets_10min": {k: dict(v) for k, v in sorted(buckets.items())}}
out_json.write_text(json.dumps(doc, indent=1) + "\n")

names = [n for n, _ in NAMED]
fmt = lambda c: ", ".join(f"{k} {v:,}" for k, v in c.items() if not k.startswith("other:")) or "none"
md = ["# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)", "",
      f"Source: `maintenance-log.txt` ({doc['entries']:,} entries, {doc['first']}-{doc['last']} PST). "
      "Only process name, time and count were read. Counts are log entries, not CPU time.", "",
      "| leg.attempt | counted | wall (PST) | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
for l in legs:
    md.append(f"| {l['leg']}.a{l['attempt']} | {'yes' if l['counted'] else 'no (redone: ' + str(l['redo_reason']) + ')'} | "
              f"{l['start']}-{l['end']} | " + " | ".join(f"{l['whole'].get(n, 0):,}" for n in names) + " |")
md += ["", "## By phase (named jobs with any entry)", ""]
for l in legs:
    md.append(f"- **{l['leg']}.a{l['attempt']}**")
    for p in l["phases"]:
        md.append(f"  - {p['phase']} {p['from']}-{p['to']}: {fmt(p['jobs'])}")
md += ["", "## 10-minute buckets (named jobs)", "", "| bucket | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
for k, v in doc["buckets_10min"].items():
    md.append(f"| {k} | " + " | ".join(f"{v.get(n, 0):,}" for n in names) + " |")
md += ["", f"Other process names in the query output: {', '.join(f'{k[6:]} {v:,}' for k, v in others.most_common()) or 'none'}. "
       f"Lines without a leading timestamp (continuation lines of multi-line messages, and the header): {skipped:,}; not read further."]
out_md.write_text("\n".join(md) + "\n")
print(json.dumps({"entries": doc["entries"], "non_entry_lines": skipped, "named_totals": doc["named_totals"],
                  "other_top": others.most_common(8)}))
