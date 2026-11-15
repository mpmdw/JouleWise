"""Scan which t0s a pin's own `plan` admits, per batch-window argument (Air only; synthetic; no measurement data).

Run with cwd = a detached worktree at the pin:  python3.13 -B scan.py KIT ROSTER WINDOW START_LOCAL HOURS STEP_S
Prints the admitted and refused intervals with the refusal reason, using the pin's own functions exactly as its
`plan` CLI calls them (v1: legs.plan_span; v1.1: plus legs.fence_problems(plan, windows, default_windows())).
Also prints, for v1 pins, the t0s whose soak (start t0+P, P in {300, 1200}) would meet the runner's soak_windows
(the R1 driver's OS_BATCH_WINDOW_LOCAL), i.e. the unbudgeted midday soak wait.
"""
import json, sys, os, datetime as dt, zoneinfo
sys.path.insert(0, os.getcwd())
from joulewise.cadence import legs as L
from scripts import cadence_legs_runner as R
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
kit_path, roster, window, start_local, hours, step = sys.argv[1:7]
kit, sha = R._load(kit_path)
roster = roster.split(",")
wins = [L.parse_window(window)]
v11 = hasattr(L, "fence_problems")
soakw = R.default_windows()
t = int(dt.datetime.fromisoformat(start_local).replace(tzinfo=TZ).timestamp())
end = t + int(float(hours) * 3600)
step = int(step)
def verdict(t0):
    try:
        p = L.plan_span(kit, t0_epoch=t0, windows=wins, leg_ids=roster, max_span_s=R.max_span_s())
    except L.PlanError as e:
        return "REFUSE plan_span: " + e.problems[0][:90]
    if v11:
        f = L.fence_problems(p, wins, soakw)
        if f:
            return "REFUSE fence_problems: " + f[0][:110]
    else:
        # v1: no launch refusal; flag the runner's unbudgeted soak wait (soak path refuses soak_windows)
        w = [*wins, *soakw]
        d = [L.interval_delay(t0 + P, 1950, w) for P in (300, 1200)]
        if any(d):
            return f"ADMIT (soak would wait: {int(d[0])} s at P=300, {int(d[1])} s at P=1200)"
    return "ADMIT"
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %H:%M:%S")
prev, since = None, t
rows = []
while t <= end:
    v = verdict(t)
    key = v.split(" (")[0] if v.startswith("ADMIT (soak") else v
    key = "ADMIT-soakwait" if v.startswith("ADMIT (soak") else (v if not v.startswith("REFUSE") else v.split(":")[0] + ":" + v.split(":")[1])
    if prev is None:
        prev, since, pv = key, t, v
    elif key != prev:
        rows.append((since, t - step, prev, pv)); prev, since, pv = key, t, v
    t += step
rows.append((since, end, prev, pv))
print(json.dumps({"cwd": os.getcwd(), "kit_sha256": sha, "roster": roster, "window": window, "v11": v11,
                  "soak_windows": [L.format_window(x) for x in soakw], "step_s": step}))
for a, b, k, v in rows:
    print(f"{lt(a)} .. {lt(b)}  [{a}..{b}]  {v}")
