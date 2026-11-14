"""Air desk: the per-span journal table, built automatically, with no energy read.

``build_desk`` runs under ``AIR-QUIET.lock`` (``air_quiet_lock``) over a local
copy of a span's operational records and writes three files to ``out_dir``:

* ``JOURNAL-TABLE.md``   the table the lead and research lead read;
* ``desk_summary.json``  the operational span summary that ``stops`` judges;
* ``stops.json``         the named stops that fired (empty list = no page).

Adapters (the kit's ``desk.adapter``):

* ``leg-summary-v1``: ``legs/<leg_id>/leg_summary.json`` written by the campaign
  runner, plus ``span/meter.json`` and ``span/result.json`` (projected). A leg
  summary is our own format, so any energy, power, slot or transcript key in it
  is a refusal (RL-143 2(d) guard), not a skip.
* ``r1-journal-v1``: the journals the 11-13 desk copied by hand
  (``events.jsonl`` / ``align_runtime_events.jsonl`` gate and hold ``phase_end``
  metadata; ``align_turns.jsonl`` turn numbers, prefill counts, decode lengths and
  finish reasons). Ported from the r1fu-1113 desk's ``build_table.py``. Fields
  are projected on read; token ids are only counted, never kept.

Only allowlisted basenames are ever opened (``ALLOWED_FILES``). The finished
text and summary are scanned for denied key names before anything is written.
Energy is read only by frozen fit code at the kit's pre-fixed looks; nothing here
opens it.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
from pathlib import Path
import re
import time

from joulewise.cadence.stops import evaluate_named_stops

QUIET_LOCK = Path("/Volumes/JW-EXT/scratch/AIR-QUIET.lock")
ALLOWED_FILES = {
    "leg-summary-v1": {"leg_summary.json", "meter.json", "result.json"},
    "r1-journal-v1": {"events.jsonl", "align_runtime_events.jsonl", "align_turns.jsonl", "meter.json",
                      "result.json"},
}
DENIED_KEY_RE = re.compile(r"(?i)(energy|joule|power_w|_j$|^j_|watt|slot|transcript|output_text|prompt_text|"
                           r"token_ids|completion|meter_samples|samples_w)")
LEG_SUMMARY_KEYS = {"leg_id", "seed", "start_band", "band_reached", "g0_s", "g0_outcome", "wall_s", "budget_s",
                    "attempts", "contaminated_redos", "redo_reasons", "os_level_max", "pm_nominal",
                    "started_epoch_s", "ended_epoch_s", "admitted"}
METER_KEYS = {"present", "proven_stopped", "bad_polls", "usb_errors", "elapsed_s", "polls"}
RESULT_KEYS = {"chain_exit_code", "chain_outcome", "fault", "outcome", "verdict"}


class DeskRefusal(RuntimeError):
    pass


class LockBusy(RuntimeError):
    pass


def _pid_alive(pid):
    try:
        os.kill(pid, 0)  # signal 0: existence check only, never delivers a signal
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@contextlib.contextmanager
def air_quiet_lock(label, path=QUIET_LOCK):
    """Hold AIR-QUIET.lock (``label=… pid=… start=…``). Serialized by an advisory guard; a lock
    held by a live process raises LockBusy; a lock whose pid is gone is NOT stolen (LockBusy
    with 'stale': the lead clears it with identity evidence)."""
    path = Path(path)
    guard = path.with_name("." + path.name + ".guard")
    with open(guard, "a+") as g:
        fcntl.flock(g, fcntl.LOCK_EX)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            text = None
        if text is not None:
            m = re.search(r"pid=(\d+)", text)
            alive = bool(m) and _pid_alive(int(m.group(1)))
            raise LockBusy(("held: " if alive else "stale (pid gone; not stolen): ") + text.strip()[:200])
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as handle:
            handle.write(f"label={label} pid={os.getpid()} start={time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
        fcntl.flock(g, fcntl.LOCK_UN)
    try:
        yield path
    finally:
        with contextlib.suppress(FileNotFoundError):
            if f"pid={os.getpid()} " in path.read_text(encoding="utf-8"):
                path.unlink()


def _open_allowed(path, adapter):
    if path.name not in ALLOWED_FILES[adapter]:
        raise DeskRefusal(f"{path.name} is not a desk input for {adapter}")
    return path.open(encoding="utf-8")


def _jsonl(path, adapter):
    rows = []
    with _open_allowed(path, adapter) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def _json(path, adapter):
    with _open_allowed(path, adapter) as handle:
        return json.load(handle)


def _project(doc, keys, where, refuse_denied):
    if not isinstance(doc, dict):
        raise DeskRefusal(f"{where}: not an object")
    if refuse_denied:
        bad = sorted(k for k in doc if DENIED_KEY_RE.search(str(k)))
        if bad:
            raise DeskRefusal(f"{where}: carries denied keys {bad} (energy, power, slot or transcript)")
        unknown = sorted(set(doc) - keys)
        if unknown:
            raise DeskRefusal(f"{where}: unknown keys {unknown}")
    return {k: doc[k] for k in keys if k in doc}


def _span_extras(root, adapter):
    meter, result = {}, None
    if (root / "span" / "meter.json").is_file():
        meter = _project(_json(root / "span" / "meter.json", adapter), METER_KEYS, "span/meter.json", True)
    if (root / "span" / "result.json").is_file():
        result = _project(_json(root / "span" / "result.json", adapter), RESULT_KEYS, "span/result.json", False)
    return meter, result


def leg_summary_rows(root):
    legs = []
    base = root / "legs"
    for leg_dir in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
        f = leg_dir / "leg_summary.json"
        if f.is_file():
            legs.append(_project(_json(f, "leg-summary-v1"), LEG_SUMMARY_KEYS, f"legs/{leg_dir.name}", True))
    return legs


def leg_table(legs, rules):
    out = ["| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for leg in legs:
        wall, budget = leg.get("wall_s"), leg.get("budget_s")
        ratio = f"{wall / budget:.2f}" if isinstance(wall, (int, float)) and isinstance(budget, (int, float)) and budget else "-"
        flag = " **over**" if ratio != "-" and float(ratio) > rules["leg_time_factor"] else ""
        out.append(f"| {leg.get('leg_id')} | {leg.get('start_band')} | {leg.get('band_reached')} | "
                   f"{_f(leg.get('g0_s'))} | {leg.get('g0_outcome', '-')} | {_f(wall)} | {_f(budget)} | {ratio}{flag} | "
                   f"{leg.get('attempts', '-')} | {leg.get('contaminated_redos', 0)} | "
                   f"{','.join(map(str, leg.get('redo_reasons') or [])) or '-'} | {leg.get('os_level_max', '-')} | "
                   f"{leg.get('pm_nominal', '-')} | {leg.get('admitted', '-')} |")
    return out


def _f(v):
    return f"{v:.1f}" if isinstance(v, (int, float)) and not isinstance(v, bool) else "-"


def r1_run_rows(run_dir):
    """Per-run gate/hold totals from one R1 member's journals (port of build_table.py)."""
    adapter = "r1-journal-v1"
    events_path = run_dir / "align_runtime_events.jsonl"
    if not events_path.is_file():
        events_path = run_dir / "events.jsonl"
    events = _jsonl(events_path, adapter) if events_path.is_file() else []
    gates = []
    for e in events:
        if e.get("event_type") == "phase_end" and e.get("phase") in ("align_thermal_gate", "align_thermal_hold"):
            m = e.get("metadata") or {}
            gates.append({k: m.get(k) for k in ("kind", "turn", "duration_s", "outcome")})
    turns = []
    if (run_dir / "align_turns.jsonl").is_file():
        for t in _jsonl(run_dir / "align_turns.jsonl", adapter):
            g = t.get("generation") or {}
            turns.append({"turn": t.get("turn"), "prefill_tokens": g.get("prefill_tokens"),
                          "decode_tokens": len(g.get("output_token_ids") or []), "finish_reason": g.get("finish_reason")})
    g0 = sum(g["duration_s"] or 0 for g in gates if g["kind"] == "G0")
    g1 = sum(g["duration_s"] or 0 for g in gates if g["kind"] == "G1")
    holds = [g for g in gates if g["kind"] == "H"]
    timeouts = [f"{g['kind']}@{g['turn']}" for g in gates if g["outcome"] == "timeout"]
    deadman = [f"{g['kind']}@{g['turn']}" for g in gates if g["outcome"] == "deadman"]
    return {"run": run_dir.name, "turns": len(turns), "g0_s": g0, "g1_s": g1, "holds": len(holds),
            "hold_s": sum(h["duration_s"] or 0 for h in holds), "timeouts": timeouts, "deadman": deadman,
            "decode_tokens": [t["decode_tokens"] for t in turns],
            "finish": [t["finish_reason"] for t in turns]}


def r1_table(rows):
    out = ["| run | turns | G0 s | G1 s | holds (n) | holds s | timeouts | deadman | decode tokens per turn | finish |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['run']} | {r['turns']} | {r['g0_s']:.1f} | {r['g1_s']:.1f} | {r['holds']} | {r['hold_s']:.1f} | "
                   f"{','.join(r['timeouts']) or 'none'} | {','.join(r['deadman']) or 'none'} | "
                   f"{','.join(map(str, r['decode_tokens'])) or '-'} | {','.join(map(str, r['finish'])) or '-'} |")
    return out


def _guard_text(text):
    hit = re.search(r"(?i)\b(\w*energy\w*|joules?|\w*power_w\w*|watts?|slots?|slot_\w+|\w*transcripts?)\b", text)
    if hit:
        raise DeskRefusal(f"output would carry a denied word {hit.group(0)!r}; nothing written")


def build_desk(*, plan_id, input_dir, out_dir, adapter, stop_rules, history=(), now=None):
    """Build the table, the span summary and the stops. Returns (summary, stops). Raises DeskRefusal."""
    if adapter not in ALLOWED_FILES:
        raise DeskRefusal(f"unknown adapter {adapter}")
    root = Path(input_dir)
    meter, result = _span_extras(root, adapter)
    lines = [f"# Desk table: {plan_id}", "",
             f"Built automatically on the Air at {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(now))} "
             f"by joulewise.cadence.desk ({adapter}). Operational fields only.", ""]
    legs = []
    if adapter == "leg-summary-v1":
        legs = leg_summary_rows(root)
        lines += ["## Legs", ""] + leg_table(legs, stop_rules)
    else:
        runs = sorted(p for p in root.iterdir() if p.is_dir() and p.name != "span")
        lines += ["## Gated runs", ""] + r1_table([r1_run_rows(p) for p in runs])
    summary = {"plan_id": plan_id, "adapter": adapter, "result": result, "meter": meter,
               "feeds_proven_stopped": bool(meter.get("proven_stopped")), "legs": legs}
    stops = evaluate_named_stops(stop_rules, summary, history)
    lines += ["", "## Named stops", ""]
    lines += [f"- **{s['code']}**: {s['detail']}" for s in stops] or ["- none (no page)"]
    lines += ["", "## Restore and capture", "",
              f"- result: {json.dumps(result, sort_keys=True) if result is not None else 'not supplied'}",
              f"- KM003C: {json.dumps(meter, sort_keys=True) if meter else 'not supplied'}"]
    text = "\n".join(lines) + "\n"
    body = json.dumps(summary, sort_keys=True, indent=1)
    _guard_text(text)
    bad = [k for k in _keys(summary) if DENIED_KEY_RE.search(k)]
    if bad:
        raise DeskRefusal(f"summary carries denied keys {bad}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "JOURNAL-TABLE.md").write_text(text, encoding="utf-8")
    (out / "desk_summary.json").write_text(body + "\n", encoding="utf-8")
    (out / "stops.json").write_text(json.dumps(stops, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return summary, stops


def _keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield str(k)
            yield from _keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _keys(v)
