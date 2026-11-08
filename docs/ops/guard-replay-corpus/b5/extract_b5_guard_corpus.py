#!/usr/bin/env python3
"""Export Block 5's real contention traces as a guard-replay corpus (process and timing fields only).

Run by a reader authorized for the Block 5 harvest archives (the lead or the magistrate). The
lessons seat that wrote this script was NOT authorized to open them (they live under
~/night-archive/harvest-v5-b5-*), so the corpus it describes has not been generated yet. See README.md.

Usage (stdlib only; python3.13 -I -B):

    python3 -I -B extract_b5_guard_corpus.py \
        --window alpha=~/night-archive/harvest-v5-b5-alpha-a1-20261009T2312Z \
        --window beta=~/night-archive/harvest-v5-b5-beta-a6-20261011T2011Z \
        --window gamma=~/night-archive/harvest-v5-b5-gamma-a1-20261012T0420Z \
        --corpus-out corpus-b5.json --culprits-out culprits-b5.json > culprits-b5.md

What it reads in each harvest root (and nothing else):

* ``sources/night-custody/hazards/monitor/contention.jsonl``: the hazard monitor's 10 s
  ``kind == "interval"`` rows. Only the CPU and process keys of guard_replay_corpus.project_cpu are
  kept (pid, command, start, cpu_s_per_s and the per-interval CPU summaries), plus the interval's
  monotonic and wall stamps.
* ``withheld/spans.json`` (fallback ``withheld/exclusion-inputs.json``): each member's request span
  (``sampling_started`` to ``sampling_stopped``) in time.monotonic_ns.
* ``derived/roster.json``: run id, stage id, ordinal, role, block, position and arm.
* ``derived/flags.jsonl``: for each member, the codes and the ``contention.request_overlap``
  offenders (pid, command, cpu_s_per_s, interval).

No power, energy, token, score or outcome field is read into memory: every JSON row is filtered by
an allowlist before it is kept, and numbers outside the allowlist are discarded unread.

Outputs:

* ``--corpus-out``: ``joulewise.guard_replay.corpus.v1``. One run per member (``contention_interval``
  frames from ``pad_s`` before to ``pad_s`` after its request, with ``request`` set so the
  ``contention_request`` adapter replays the real span), and one run per window (the whole monitor
  journal). Member labels come from the B5 harvest's own predicate. That makes them circular for that
  predicate and usable only for evaluating a DIFFERENT candidate guard (ruling 8, an energy-scaled bar,
  or a 30 s interval). ``label_basis`` says so, and window runs are ``unknown``.
* ``--culprits-out``: per flagged member, every offender with its CPU-s/s, start (UTC and
  America/Los_Angeles), and episode duration (the consecutive over-limit intervals of that pid), plus a
  window census of over-limit intervals by command and local hour.
* stdout: the same culprit tables as Markdown, ready to paste into LESSONS-FOR-V4-V5.md §1.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import math
import pathlib
import sys

try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo("America/Los_Angeles")
except Exception:  # pragma: no cover - zoneinfo is stdlib on 3.9+
    LOCAL = dt.timezone(dt.timedelta(hours=-7), "PDT")

SCHEMA = "joulewise.guard_replay.corpus.v1"
LIMIT = 0.05  # registration_block5 §6.4: 5 % of one core, judged per 10 s interval
EXEMPT = {"kernel_task"}  # joulewise/b5/harvest.py CONTENTION_EXEMPT
# The same allowlists as joulewise/guard_replay_corpus.py (ops/2026-11-08-guard-replay).
CPU_KEYS = {"elapsed_s", "clean", "error", "host_error", "interval", "max_outside", "outside_over_limit",
            "outside_listed", "outside_total_cpu_s_per_s", "kernel_task_cpu_s_per_s", "host_busy_cpu_s_per_s",
            "outside_aggregate_cpu_s_per_s", "cpu_limit_s_per_s", "aggregate_cpu_limit_s_per_s",
            "aggregate_over_limit"}
PROCESS_KEYS = {"pid", "command", "start", "cpu_s_per_s", "basis"}
INTERVAL_KEYS = {"monotonic_ns", "wall_ns"}
FLAG_CODES = {"contention.request_overlap", "contention.unmeasured", "member.admission_aborted",
              "member.span_unknown", "member.anchor_not_bounded"}
ROSTER_KEYS = {"run_id", "kind", "ordinal", "stage_id", "role", "block_id", "position", "arm"}


def project_rows(value):
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if k in PROCESS_KEYS}
    if isinstance(value, list):
        return [{k: v for k, v in row.items() if k in PROCESS_KEYS} for row in value if isinstance(row, dict)]
    return None


def project_cpu(values: dict) -> dict:
    out = {k: v for k, v in values.items() if k in CPU_KEYS}
    for field in ("max_outside", "outside_over_limit", "outside_listed"):
        if field in out:
            out[field] = project_rows(out[field])
    if isinstance(out.get("interval"), dict):
        out["interval"] = {k: v for k, v in out["interval"].items() if k in INTERVAL_KEYS}
    return out


def read_jsonl(path: pathlib.Path):
    with path.open("rb") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def intervals_of(root: pathlib.Path) -> list[dict]:
    path = root / "sources/night-custody/hazards/monitor/contention.jsonl"
    rows = []
    for row in read_jsonl(path):
        if row.get("kind") != "interval" or not isinstance(row.get("values"), dict):
            continue
        cpu = project_cpu(row["values"])
        mono = (cpu.get("interval") or {}).get("monotonic_ns")
        if not (isinstance(mono, list) and len(mono) == 2):
            continue
        rows.append(cpu)
    rows.sort(key=lambda r: r["interval"]["monotonic_ns"][0])
    return rows


def roster_of(root: pathlib.Path) -> dict[str, dict]:
    data = json.loads((root / "derived/roster.json").read_text())
    members = data.get("members", [])
    if isinstance(members, dict):
        members = [{"run_id": k, **v} for k, v in members.items()]
    return {m["run_id"]: {k: m.get(k) for k in ROSTER_KEYS} for m in members if isinstance(m, dict)}


def spans_of(root: pathlib.Path) -> dict[str, list[int] | None]:
    for name in ("withheld/spans.json", "withheld/exclusion-inputs.json"):
        path = root / name
        if path.exists():
            spans = json.loads(path.read_text()).get("spans") or {}
            return {rid: (s or {}).get("request") for rid, s in spans.items() if isinstance(s, dict)}
    raise SystemExit(f"{root}: no withheld/spans.json or exclusion-inputs.json")


def flags_of(root: pathlib.Path) -> dict[str, list[dict]]:
    out = collections.defaultdict(list)
    for row in read_jsonl(root / "derived/flags.jsonl"):
        code = row.get("code")
        if code not in FLAG_CODES:
            continue
        run_id = (row.get("scope") or {}).get("run_id")
        observed = row.get("observed") if isinstance(row.get("observed"), dict) else {}
        offenders = []
        for item in observed.get("offenders") or []:
            if isinstance(item, dict):
                offenders.append({k: item.get(k) for k in ("pid", "command", "cpu_s_per_s", "interval_monotonic_ns")})
        out[run_id].append({"code": code, "offenders": offenders,
                            "offender_count": observed.get("offender_count") if code.startswith("contention") else None})
    return out


def wall_of(intervals: list[dict], mono_ns: int) -> dt.datetime | None:
    """Map a monotonic stamp to wall time through the nearest journal interval (both stamps recorded)."""
    best = None
    for cpu in intervals:
        iv = cpu["interval"]
        if "wall_ns" not in iv:
            continue
        d = abs(iv["monotonic_ns"][0] - mono_ns)
        if best is None or d < best[0]:
            best = (d, iv["wall_ns"][0] + (mono_ns - iv["monotonic_ns"][0]))
    return dt.datetime.fromtimestamp(best[1] / 1e9, dt.timezone.utc) if best else None


def over_limit(cpu: dict) -> list[dict]:
    rows = {}
    for field in ("outside_over_limit", "outside_listed"):
        for row in cpu.get(field) or []:
            rate = row.get("cpu_s_per_s")
            if row.get("command") in EXEMPT or not isinstance(rate, (int, float)) or rate <= LIMIT:
                continue
            key = (row.get("pid"), row.get("command"))
            if key not in rows or rows[key]["cpu_s_per_s"] < rate:
                rows[key] = {"pid": row.get("pid"), "command": row.get("command"), "cpu_s_per_s": rate}
    return list(rows.values())


def episode(intervals: list[dict], index: int, pid) -> tuple[int, float, float]:
    """Consecutive over-limit intervals of one pid around interval ``index``: (count, seconds, peak)."""
    def hit(i):
        return next((r for r in over_limit(intervals[i]) if r["pid"] == pid), None)
    lo = hi = index
    while lo > 0 and hit(lo - 1):
        lo -= 1
    while hi + 1 < len(intervals) and hit(hi + 1):
        hi += 1
    start, end = intervals[lo]["interval"]["monotonic_ns"][0], intervals[hi]["interval"]["monotonic_ns"][1]
    peak = max(hit(i)["cpu_s_per_s"] for i in range(lo, hi + 1))
    return hi - lo + 1, (end - start) / 1e9, peak


def coverage(frames: list[dict], cadence_s: float = 10.0) -> bool:
    ts = [f["t"] for f in frames]
    return len(ts) >= 2 and all(0 <= b - a <= cadence_s * 1.1 for a, b in zip(ts, ts[1:]))


def build(windows: dict[str, pathlib.Path], pad_s: float):
    runs, culprits, census = [], [], collections.Counter()
    by_hour = collections.Counter()
    for label, root in windows.items():
        intervals = intervals_of(root)
        roster, spans, flags = roster_of(root), spans_of(root), flags_of(root)
        frames = [{"t": cpu["interval"]["monotonic_ns"][1] / 1e9, "contention_interval": cpu} for cpu in intervals]
        runs.append({"id": f"b5-{label}-window-monitor", "label": "unknown", "stratum": "b5_window_monitor",
                     "label_basis": "No independent idle/contended label; whole-window host trace for slicing",
                     "complete": coverage(frames), "duration_s": frames[-1]["t"] - frames[0]["t"] if frames else 0,
                     "source": {"window": label, "journal": "hazards/monitor/contention.jsonl"}, "frames": frames})
        for i, cpu in enumerate(intervals):
            for row in over_limit(cpu):
                census[(label, row["command"])] += 1
                wall = wall_of([cpu], cpu["interval"]["monotonic_ns"][0])
                if wall:
                    by_hour[(row["command"], wall.astimezone(LOCAL).hour)] += 1
        for run_id, request in spans.items():
            if not request or run_id not in roster:
                continue
            a, b = request
            lo, hi = a - pad_s * 1e9, b + pad_s * 1e9
            member_frames = [f for f in frames
                             if f["contention_interval"]["interval"]["monotonic_ns"][1] >= lo
                             and f["contention_interval"]["interval"]["monotonic_ns"][0] <= hi]
            codes = sorted({f["code"] for f in flags.get(run_id, [])})
            contended = "contention.request_overlap" in codes
            runs.append({
                "id": f"b5-{label}-{run_id}", "label": "contended" if contended else "benign",
                "label_basis": ("B5 harvest predicate contention.request_overlap (outside process > 0.05 CPU-s/s in a "
                                "10 s interval overlapping the request). Circular for that predicate; usable only to "
                                "evaluate a different candidate guard."),
                "stratum": f"b5_member_request_{label}", "complete": coverage(member_frames),
                "duration_s": (member_frames[-1]["t"] - member_frames[0]["t"]) if member_frames else 0,
                "request": {"monotonic_ns": [a, b]}, "request_s": (b - a) / 1e9,
                "member": roster[run_id], "harvest_codes": codes,
                "source": {"window": label}, "frames": member_frames})
            for flag in flags.get(run_id, []):
                if flag["code"] != "contention.request_overlap":
                    continue
                for off in flag["offenders"]:
                    iv = off.get("interval_monotonic_ns") or [a, b]
                    idx = next((k for k, cpu in enumerate(intervals)
                                if cpu["interval"]["monotonic_ns"][0] == iv[0]), None)
                    n, secs, peak = episode(intervals, idx, off.get("pid")) if idx is not None else (None, None, None)
                    wall = wall_of(intervals, iv[0])
                    culprits.append({
                        "window": label, "run_id": run_id, "stage_id": roster[run_id].get("stage_id"),
                        "ordinal": roster[run_id].get("ordinal"), "arm": roster[run_id].get("arm"),
                        "request_s": round((b - a) / 1e9, 3), "command": off.get("command"), "pid": off.get("pid"),
                        "cpu_s_per_s": off.get("cpu_s_per_s"),
                        "interval_start_utc": wall.isoformat() if wall else None,
                        "interval_start_local": wall.astimezone(LOCAL).isoformat() if wall else None,
                        "episode_intervals": n, "episode_s": secs, "episode_peak_cpu_s_per_s": peak})
    corpus = {"schema": SCHEMA, "provenance": "Block 5 harvest archives; process and timing fields only",
              "runs": runs}
    return corpus, {"schema": "joulewise.b5_contention_culprits.v1", "limit_cpu_s_per_s": LIMIT,
                    "culprits": culprits,
                    "census_over_limit_intervals": [{"window": w, "command": c, "intervals": n}
                                                    for (w, c), n in census.most_common()],
                    "by_local_hour": [{"command": c, "hour": h, "intervals": n}
                                      for (c, h), n in sorted(by_hour.items())]}


def markdown(culprits: dict) -> str:
    out = ["| Window | Member | Arm | Request s | Process | CPU-s/s | Start (local) | Episode s |",
           "|---|---|---|---|---|---|---|---|"]
    for c in culprits["culprits"]:
        out.append(f"| {c['window']} | {c['run_id']} | {c['arm']} | {c['request_s']} | {c['command']} | "
                   f"{c['cpu_s_per_s']:.3f} | {c['interval_start_local']} | {c['episode_s']} |")
    out += ["", "| Window | Process | Over-limit 10 s intervals (whole window) |", "|---|---|---|"]
    out += [f"| {r['window']} | {r['command']} | {r['intervals']} |" for r in culprits["census_over_limit_intervals"]]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--window", action="append", required=True, help="label=harvest_root (repeat per window)")
    ap.add_argument("--pad-s", type=float, default=60.0, help="trace kept around each request (default 60 s)")
    ap.add_argument("--corpus-out", required=True)
    ap.add_argument("--culprits-out", required=True)
    args = ap.parse_args(argv)
    windows = {}
    for item in args.window:
        label, _, root = item.partition("=")
        windows[label] = pathlib.Path(root).expanduser()
    corpus, culprits = build(windows, args.pad_s)
    for run in corpus["runs"]:  # fail loudly on non-finite times, as guard_replay.validate would
        if not all(math.isfinite(f["t"]) for f in run["frames"]):
            raise SystemExit(f"non-finite frame time in {run['id']}")
    pathlib.Path(args.corpus_out).write_text(json.dumps(corpus, sort_keys=True) + "\n")
    pathlib.Path(args.culprits_out).write_text(json.dumps(culprits, indent=1, sort_keys=True) + "\n")
    sys.stdout.write(markdown(culprits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
