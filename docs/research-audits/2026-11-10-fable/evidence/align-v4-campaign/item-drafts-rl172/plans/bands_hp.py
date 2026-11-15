"""hp-01 remainder bands: v1 argument bands at dd206025a intersected with RL-165 §7's 00:30 rule (worst-case end by the
next 00:30; kept by RL-171 §2, small hours confirmed by RL-172 §0), window Sun 00:00:00 to Mon 23:59:59. Every band end
checked with the pinned `plan` CLI (the argument admits it; the bytes' own ends also refuse +1 s)."""
import json, os, subprocess, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles"); D = "/Volumes/JW-EXT/scratch/items-rl171"
PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"; ENV = dict(os.environ, TMPDIR=f"{D}/tmp", JW_B5_SYNTHETIC_ONLY="1")
def ep(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp())
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %d %b %H:%M:%S")
def at(d, h, m, s=0): return int(dt.datetime.combine(d, dt.time(h, m, s), TZ).timestamp())
DEF, ALT = "02:00-02:35", "13:14-13:15"
for name, legs in (("hp01-s02", "L004,L005,L006,L007"), ("hp01-s03", "L008,L009,L010,L011,L012")):
    n = len(legs.split(",")); W = 1950 + 1200 + (n + 2) * 2700
    days = [dt.date(2026, 11, 15), dt.date(2026, 11, 16)]
    raw = []
    for d in days:
        nd = d + dt.timedelta(days=1)
        raw.append((at(d, 0, 0), min(at(d, 2, 34, 59), at(d, 13, 14) - W), ALT, "bytes" if at(d, 13, 14) - W < at(d, 2, 34, 59) else "default-takes-over"))
        raw.append((at(d, 2, 35), at(d, 10, 50), DEF, "soak-wait"))
        raw.append((at(d, 13, 15), at(nd, 2, 0) - W, DEF, "bytes"))
    # the 00:30 rule: t0 + W <= the next 00:30 after t0 (t0 in (00:30(D) - W, 00:30(D)] is refused)
    bands = []
    for s, e, arg, why in raw:
        d = dt.datetime.fromtimestamp(s, TZ).date()
        cut_eve = at(d + dt.timedelta(days=1), 0, 30) - W          # evening limit for t0 on date d
        cut_morn = at(d, 0, 30) + 1                                  # a t0 after 00:30 of date d
        s2, e2 = s, min(e, cut_eve)
        if e2 < cut_eve and why == "bytes" and e2 == e: pass
        if s2 < cut_morn: s2 = cut_morn if e2 >= cut_morn else e2 + 1
        if s2 <= e2: bands.append([s2, e2, arg, "00:30 rule" if e2 == cut_eve and cut_eve < e else why])
    log = [f"{name}: legs {legs} W {W}"]
    for s, e, arg, why in bands:
        for t in (s, e):
            r = subprocess.run([PY, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", f"{D}/kits/cl-hp-01@bbd34dc87.json",
                                "--legs", legs, "--t0", str(t), "--batch-window", arg], cwd=f"{D}/wt/dd206025a", capture_output=True, text=True, env=ENV)
            log.append(f"  {'OK ' if r.returncode == 0 else 'BAD'} plan --t0 {t} ({lt(t)}) --batch-window {arg}: rc {r.returncode}"); assert r.returncode == 0, log[-1]
            assert t + W <= at(dt.datetime.fromtimestamp(t - 1800, TZ).date() + dt.timedelta(days=1), 0, 30), ("00:30", lt(t))
        if why == "bytes":
            r = subprocess.run([PY, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", f"{D}/kits/cl-hp-01@bbd34dc87.json",
                                "--legs", legs, "--t0", str(e + 1), "--batch-window", arg], cwd=f"{D}/wt/dd206025a", capture_output=True, text=True, env=ENV)
            log.append(f"  {'OK ' if r.returncode else 'BAD'} plan --t0 {e+1} ({lt(e+1)}) --batch-window {arg}: rc {r.returncode} (refused past the bytes' end)"); assert r.returncode, log[-1]
    sh = ["pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3 bands of this pin's own plan, cut by the 00:30 rule)", "  n=$1"]
    for i, (s, e, arg, why) in enumerate(bands):
        sh.append(f"  {'if  ' if i == 0 else 'elif'} [ \"$n\" -ge {s} ] && [ \"$n\" -le {e} ]; then echo {arg}   # {lt(s)} .. {lt(e)} ({why})")
    sh += ["  else echo NONE; fi", "}"]
    open(f"{D}/plans/bands/{name}.sh", "w").write("\n".join(sh) + "\n")
    open(f"{D}/plans/bands/verify-{name}.txt", "w").write("\n".join(log) + "\n")
    json.dump({"item": name, "legs": legs, "worst_case_s": W, "bands": bands}, open(f"{D}/plans/bands/{name}.json", "w"), indent=1)
    print(log[0]); [print("   ", lt(s), "..", lt(e), arg, why, f"[{s}..{e}]") for s, e, arg, why in bands]
