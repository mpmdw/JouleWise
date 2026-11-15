"""CLI `plan` at boundary t0s for every roster, both arguments; and one mock per pin/roster crossing 02:00 with 13:14-13:15.
Air only; synthetic. Outputs: probe/plan/<tag>-<arg>-<local>.json(.err) and mock/<tag>-alt0030/ ; summary on stdout."""
import json, subprocess, os, datetime as dt, zoneinfo, sys
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
D = "/Volumes/JW-EXT/scratch/items-rl171"
ENV = dict(os.environ, TMPDIR=f"{D}/tmp", JW_B5_SYNTHETIC_ONLY="1")
K = f"{D}/kits"
def L(a, b): return ",".join(f"L{i:03d}" for i in range(a, b + 1))
def ep(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp())
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %Y-%m-%d %H:%M:%S")
CFG = [  # tag, pin, kit, roster, v11, worst
 ("dev02-s02-6", "b4b6aeb19", "cl-dev-02@589748f15.json", L(1, 6), False),
 ("dev02-s03-6", "b4b6aeb19", "cl-dev-02@589748f15.json", L(7, 12), False),
 ("dev02-s01-12", "b4b6aeb19", "cl-dev-02@589748f15.json", L(1, 12), False),
 ("hp01-s01-3", "dd206025a", "cl-hp-01@bbd34dc87.json", L(1, 3), False),
 ("hp01-s02-4", "dd206025a", "cl-hp-01@bbd34dc87.json", L(4, 7), False),
 ("hp01-s03-5", "dd206025a", "cl-hp-01@bbd34dc87.json", L(8, 12), False),
 ("dev03-s01-3", "2d347f721", "cl-dev-03.v1.1.json", L(1, 3), True),
 ("dev03-s02-9", "2d347f721", "cl-dev-03.v1.1.json", L(4, 12), True),
 ("dev03-s02b-3", "2d347f721", "cl-dev-03.v1.1.json", L(4, 6), True),
 ("dev03-s03b-6", "2d347f721", "cl-dev-03.v1.1.json", L(7, 12), True),
 ("dev04-s01-6", "2d347f721", "cl-dev-04.v1.1.json", L(1, 6), True),
 ("dev04-s02-6", "2d347f721", "cl-dev-04.v1.1.json", L(7, 12), True),
 ("dev05-s01-6", "2d347f721", "cl-dev-05.v1.1.json", L(1, 6), True),
 ("dev05-s02-6", "2d347f721", "cl-dev-05.v1.1.json", L(7, 12), True),
]
os.makedirs(f"{D}/probe/plan", exist_ok=True); os.makedirs(f"{D}/mock", exist_ok=True)
def plan(pin, kit, roster, t0, arg, tag):
    r = subprocess.run([PY, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", f"{K}/{kit}", "--legs", roster,
                        "--t0", str(t0), "--batch-window", arg], cwd=f"{D}/wt/{pin}", capture_output=True, text=True, env=ENV)
    name = f"{D}/probe/plan/{tag}-{arg.replace(':','')}-{dt.datetime.fromtimestamp(t0, TZ).strftime('%a%H%M%S')}.txt"
    open(name, "w").write(f"$ plan --t0 {t0} ({lt(t0)}) --batch-window {arg}  [pin {pin}]\nrc {r.returncode}\n{r.stdout}{r.stderr}")
    if r.returncode:
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:120]
    p = json.loads(r.stdout); return 0, f"exp {p['expected_s']} worst {p['worst_case_s']}"
out = {}
day = "2026-11-16"   # Mon; the bands repeat daily
for tag, pin, kit, roster, v11 in CFG:
    n = len(roster.split(",")); W = 1950 + 1200 + (n + 2) * 2700
    tail = 1460 if v11 else 0
    d_last = ep(f"{day}T{'01:50' if v11 else '02:00'}:00") - W - tail
    a_last = ep(f"{day}T{'13:04' if v11 else '13:14'}:00") - W - tail
    # d_last is on the previous evening when W > ~?: normalise to the band following 13:15 or 02:35
    pts = [("02:00-02:35", d_last), ("02:00-02:35", d_last + 1), ("13:14-13:15", a_last), ("13:14-13:15", a_last + 1),
           ("02:00-02:35", ep(f"{day}T02:34:59")), ("02:00-02:35", ep(f"{day}T02:35:00")),
           ("13:14-13:15", ep(f"{day}T13:14:59")), ("13:14-13:15", ep(f"{day}T13:15:00"))]
    if v11:
        pts += [("02:00-02:35", ep(f"{day}T10:50:00")), ("02:00-02:35", ep(f"{day}T10:50:01"))]
    res = []
    for arg, t0 in pts:
        rc, msg = plan(pin, kit, roster, t0, arg, tag)
        res.append((arg, lt(t0), t0, rc, msg))
    out[tag] = {"pin": pin, "worst": W, "d_last": lt(d_last), "a_last": lt(a_last), "plans": res}
    print(tag, pin, "W", W, "default-last", lt(d_last), "alt-last", lt(a_last))
    for r in res: print("   ", r)
json.dump(out, open(f"{D}/probe/boundaries.json", "w"), indent=1)
