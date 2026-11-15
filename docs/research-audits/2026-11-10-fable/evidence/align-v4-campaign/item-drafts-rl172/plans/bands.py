"""Per-item launch bands under RL-171: which --batch-window argument each t0 uses, from the pinned bytes.

Rule (RL-171 §3, applied the same way on every campaign pin): use 02:00-02:35 wherever the pin's own `plan` admits it;
otherwise use 13:14-13:15 (the data-only route); never inside (10:50:00, 13:15:00) (v1.1: fence_problems refuses it;
v1: the soak path waits out 11:45-13:15 unbudgeted). Every band end is then CHECKED with the pinned `plan` CLI:
start and end admitted with the band's argument, and (where the band is bounded by the bytes) one second past the end
refused with it. Output: plans/bands/<item>.json, <item>.sh (the pick_arg function for the item) and verify-<item>.txt.
"""
import json, os, subprocess, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
D = "/Volumes/JW-EXT/scratch/items-rl171"
PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
ENV = dict(os.environ, TMPDIR=f"{D}/tmp", JW_B5_SYNTHETIC_ONLY="1")
def ep(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp())
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %d %b %H:%M:%S")
def L(a, b): return ",".join(f"L{i:03d}" for i in range(a, b + 1))
DEF, ALT = "02:00-02:35", "13:14-13:15"
ITEMS = {
 "hp01-s01": ("dd206025a", "cl-hp-01@bbd34dc87.json", L(1, 3), "2026-11-15T00:00:00", "2026-11-15T19:52:30"),
 "dev02-s02": ("b4b6aeb19", "cl-dev-02@589748f15.json", L(1, 6), "2026-11-15T00:00:00", "2026-11-15T23:59:59"),
 "dev02-s03": ("b4b6aeb19", "cl-dev-02@589748f15.json", L(7, 12), "2026-11-16T00:00:00", "2026-11-16T23:59:59"),
 "dev02-s01": ("b4b6aeb19", "cl-dev-02@589748f15.json", L(1, 12), "2026-11-16T00:00:00", "2026-11-16T23:59:59"),
 "dev03-s01": ("2d347f721", "cl-dev-03.v1.1.json", L(1, 3), "2026-11-16T00:00:00", "2026-11-16T23:59:59"),
 "dev03-s02": ("2d347f721", "cl-dev-03.v1.1.json", L(4, 12), "2026-11-16T00:00:00", "2026-11-16T23:59:59"),
 "dev04-s01": ("2d347f721", "cl-dev-04.v1.1.json", L(1, 6), "2026-11-17T00:00:00", "2026-11-17T23:59:59"),
 "dev04-s02": ("2d347f721", "cl-dev-04.v1.1.json", L(7, 12), "2026-11-17T00:00:00", "2026-11-17T23:59:59"),
 "dev05-s01": ("2d347f721", "cl-dev-05.v1.1.json", L(1, 6), "2026-11-18T00:00:00", "2026-11-18T23:59:59"),
 "dev05-s02": ("2d347f721", "cl-dev-05.v1.1.json", L(7, 12), "2026-11-18T00:00:00", "2026-11-18T23:59:59"),
}
def at(day, hms): return int(dt.datetime.combine(day, dt.time(*hms), TZ).timestamp())
def bands(pin, n, a, b):
    v11 = pin == "2d347f721"; W = 1950 + 1200 + (n + 2) * 2700; tail = 1460 if v11 else 0
    out = []
    d0 = dt.datetime.fromtimestamp(a, TZ).date() - dt.timedelta(days=1)
    d1 = dt.datetime.fromtimestamp(b, TZ).date() + dt.timedelta(days=1)
    d = d0
    while d <= d1:
        nxt = d + dt.timedelta(days=1)
        d_last = at(nxt, (1, 50) if v11 else (2, 0)) - W - tail          # default's last t0 on the evening of d
        a_last_next = at(nxt, (13, 4) if v11 else (13, 14)) - W - tail   # alternate's last t0 (morning of d+1)
        out.append((at(d, (2, 35)), at(d, (10, 50)), DEF, "bytes" if v11 else "soak-wait (v1 admits; the soak would wait out 11:45-13:15 unbudgeted)"))
        out.append((at(d, (13, 15)), d_last, DEF, "bytes"))
        out.append((d_last + 1, min(at(nxt, (2, 34, 59)), a_last_next), ALT, "bytes" if a_last_next < at(nxt, (2, 34, 59)) else "default-takes-over"))
        d = nxt
    res = []
    for s, e, arg, why in out:
        s2, e2 = max(s, a), min(e, b)
        if s2 <= e2: res.append([s2, e2, arg, why if e2 == e else "window"])
    return sorted(res), W
def plan(pin, kit, legs, t, arg):
    r = subprocess.run([PY, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", f"{D}/kits/{kit}", "--legs", legs,
                        "--t0", str(t), "--batch-window", arg], cwd=f"{D}/wt/{pin}", capture_output=True, text=True, env=ENV)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:110] if r.returncode else "ok"
os.makedirs(f"{D}/plans/bands", exist_ok=True)
for name, (pin, kit, legs, a, b) in ITEMS.items():
    n = len(legs.split(",")); bs, W = bands(pin, n, ep(a), ep(b))
    log = [f"{name}: pin {pin} kit {kit} legs {legs} W {W} window {a} .. {b}"]
    for s, e, arg, why in bs:
        for t, want in ((s, 0), (e, 0)) + (((e + 1, 1),) if why == "bytes" else ()):
            rc, msg = plan(pin, kit, legs, t, arg)
            ok = (rc == 0) == (want == 0)
            log.append(f"  {'OK ' if ok else 'BAD'} plan --t0 {t} ({lt(t)}) --batch-window {arg}: rc {rc} {msg}")
            assert ok, log[-1]
    sh = ["pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)",
          "  n=$1"]
    for i, (s, e, arg, why) in enumerate(bs):
        sh.append(f"  {'if  ' if i == 0 else 'elif'} [ \"$n\" -ge {s} ] && [ \"$n\" -le {e} ]; then echo {arg}   # {lt(s)} .. {lt(e)}")
    sh += ["  else echo NONE; fi", "}"]
    json.dump({"item": name, "pin": pin, "kit": kit, "legs": legs, "worst_case_s": W, "window": [a, b],
               "bands": [{"start": s, "end": e, "start_local": lt(s), "end_local": lt(e), "arg": arg, "bounded_by": why}
                         for s, e, arg, why in bs]}, open(f"{D}/plans/bands/{name}.json", "w"), indent=1)
    open(f"{D}/plans/bands/{name}.sh", "w").write("\n".join(sh) + "\n")
    open(f"{D}/plans/bands/verify-{name}.txt", "w").write("\n".join(log) + "\n")
    print("\n".join(log[:1]))
    for s, e, arg, why in bs: print(f"   {lt(s)} .. {lt(e)}  {arg}  ({why})  [{s}..{e}]")
