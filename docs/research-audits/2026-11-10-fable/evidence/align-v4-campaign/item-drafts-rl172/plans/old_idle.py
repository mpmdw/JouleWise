"""Idle per day of the OLD (RL-165) chain, from items-rl165/plans/chain.json (expected case), same method as chain.py."""
import json, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
DAY = {"Sat": "2026-11-14", "Sun": "2026-11-15", "Mon": "2026-11-16", "Tue": "2026-11-17", "Wed": "2026-11-18"}
def ep(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp())
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %H:%M:%S")
rows = json.load(open("/Volumes/JW-EXT/scratch/items-rl165/plans/chain.json"))
busy = []
for r in rows:
    d, t = r["t0"].split(); t0 = ep(f"{DAY[d]}T{t}"); busy.append((t0, t0 + r["expected_s"], r["name"]))
S = ep("2026-11-15T00:00")
def idle(a, b):
    t = 0; cur = a
    for s, en, _ in sorted(busy):
        s, en = max(s, a), min(en, b)
        if en <= cur: continue
        if s > cur: t += s - cur
        cur = max(cur, en)
    return round((t + max(0, b - cur)) / 3600, 2)
out = {n: idle(S + i * 86400, S + (i + 1) * 86400) for i, n in enumerate(["Sun", "Mon", "Tue", "Wed"])}
print("old idle h/day", out)
cur = S
for s, en, n in sorted(busy):
    if en <= S: continue
    if s - cur >= 600: print("gap", lt(cur), lt(s), round((s - cur) / 3600, 2), n)
    cur = max(cur, en)
print("gap", lt(cur), "Thu 00:00:00", round((S + 4 * 86400 - cur) / 3600, 2))
json.dump(out, open("plans/old-idle.json", "w"))
