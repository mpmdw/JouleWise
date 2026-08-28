#!/usr/bin/env python3
"""Print Codex's own rate-limit signal (the same data the TUI's /usage shows).

Reads the newest `rate_limits` event across recent session rollouts under
~/.codex/sessions and prints window, used %, and reset time. Read-only.
"""
from __future__ import annotations
import glob, json, os, sys, time

root = os.path.expanduser("~/.codex/sessions")
files = sorted(glob.glob(os.path.join(root, "*", "*", "*", "*.jsonl")), key=os.path.getmtime, reverse=True)[:40]
best = None
for f in files:
    try:
        with open(f, "rb") as fh:
            for raw in fh:
                if b'"rate_limits"' not in raw:
                    continue
                try:
                    o = json.loads(raw)
                except Exception:
                    continue
                s = json.dumps(o)
                i = s.find('"rate_limits"')
                # locate the object
                try:
                    rl = None
                    def walk(x):
                        global rl
                        if isinstance(x, dict):
                            if "rate_limits" in x and isinstance(x["rate_limits"], dict):
                                rl = x["rate_limits"]; return
                            for v in x.values(): walk(v)
                        elif isinstance(x, list):
                            for v in x: walk(v)
                    walk(o)
                    ts = o.get("timestamp") or os.path.getmtime(f)
                    if rl and (best is None or str(ts) > str(best[0])):
                        best = (ts, rl, f)
                except Exception:
                    pass
    except OSError:
        continue
if not best:
    print("codex usage: no rate_limits event found"); sys.exit(1)
ts, rl, f = best
p = rl.get("primary") or {}
s2 = rl.get("secondary") or {}
def fmt(w):
    if not w: return "n/a"
    mins = w.get("window_minutes"); used = w.get("used_percent"); rs = w.get("resets_at")
    when = time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(rs)) if rs else "?"
    return f"{used}% of {mins/1440:.0f}d window, resets {when}" if mins else f"{used}%"
print(f"codex usage (plan={rl.get('plan_type')}, as of {ts}): primary {fmt(p)}; secondary {fmt(s2)}; reached={rl.get('rate_limit_reached_type')}")
