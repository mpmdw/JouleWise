"""RL-171 chain forecast, Sun 15 Nov 00:00 -> Thu 19 Nov 00:00, and MBP idle per day (old chain vs new). Air only.

Expected-case: each span takes its pin's own `plan` expected_s (probe/boundaries.json and the old plans/ cover
every roster; the numbers are the plan's, re-asserted below by calling the pinned `plan` CLI at every forecast
t0 with the argument the item would pick). Launch legality is the BYTES only (probe/scan-*.txt, boundaries.json):
  v1 pins (b4b6aeb19, dd206025a): default 02:00-02:35 admits t0 in [02:35, 02:00 - W]; 13:14-13:15 admits
      [13:15, 13:14 - W]; no t0 in (10:50, 13:15) (the soak path waits out 11:45-13:15 unbudgeted).
  v1.1 pin (2d347f721): default admits [02:35, 01:50 - W - 1460]; 13:14-13:15 admits [13:15, 13:04 - W - 1460];
      fence_problems refuses (10:50, 13:15) under either argument.
  c3f4bacd8 (F0): soak_child refuses a soak start in (22:50:40, 02:35:00); launch 02:35:00-22:40:00 (RL-156 §5,
      restored by RL-171 §3).
Kept rules: hp-01 worst-case end by 00:30 (RL-165 §7); calendar days (dev-01-s04 Sun, dev-02-s02 Sun, dev-02-s03
Mon); ruled order (RL-165 §1, §2); F0 rules 3, 5, 7 (RL-165 §3); close interval RL-171 §6.1 (QUIET after a
campaign close, 1,200 s before a counted span after F0/F2); hand-read gaps (the lead) of HAND s.
"""
import json, os, subprocess, sys, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
D = "/Volumes/JW-EXT/scratch/items-rl171"
PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
ENV = dict(os.environ, TMPDIR=f"{D}/tmp", JW_B5_SYNTHETIC_ONLY="1")
QUIET = int(os.environ.get("QUIET", 300))      # RL-171 §6.1 floor after a campaign close (lead confirms; else 1200)
HAND = int(os.environ.get("HAND", 1200))       # the lead's hand-read before hp-01-s02 and dev-03's rest
F2 = os.environ.get("F2", "0") == "1"          # fill with F2 pieces if READY (draft kit f2-inst-01.v1.1, 2d347f721)
TAG = os.environ.get("TAG", "new")
DAYBAL = os.environ.get("DAYBAL", "1") == "1"   # RL-172 (a): dev-03 Mon, dev-04 Tue, dev-05 Wed
def ep(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp())
def lt(e): return dt.datetime.fromtimestamp(e, TZ).strftime("%a %H:%M:%S")
def sod(e):
    d = dt.datetime.fromtimestamp(e, TZ); return d.hour * 3600 + d.minute * 60 + d.second
def at(e, hms, plus=0):
    d = dt.datetime.fromtimestamp(e, TZ).date() + dt.timedelta(days=plus)
    return int(dt.datetime.combine(d, dt.time(*hms), TZ).timestamp())
H = lambda h, m, s=0: h * 3600 + m * 60 + s
KITS = {"dev01": ("b4b6aeb19", "cl-dev-01@589748f15.json"), "dev02": ("b4b6aeb19", "cl-dev-02@589748f15.json"),
        "hp01": ("dd206025a", "cl-hp-01@bbd34dc87.json"), "dev03": ("2d347f721", "cl-dev-03.v1.1.json"),
        "dev04": ("2d347f721", "cl-dev-04.v1.1.json"), "dev05": ("2d347f721", "cl-dev-05.v1.1.json"),
        "f2": ("2d347f721", "/Volumes/JW-EXT/scratch/sol-f2-delta/head/docs/process/cadence/kits/f2-inst-01.v1.1.json")}
def W(n, quota=2): return 1950 + 1200 + (n + quota) * 2700
def arg_for(pin, w, t):
    """The argument the item picks at t (default first, RL-171 §3), or None when the bytes refuse both."""
    s = sod(t); v11 = pin == "2d347f721"
    if H(10, 50) < s < H(13, 15): return None
    dl = (H(1, 50) - w - 1460) if v11 else (H(2, 0) - w)       # may be negative: wraps to previous evening
    al = (H(13, 4) - w - 1460) if v11 else (H(13, 14) - w)
    dl %= 86400
    if H(2, 35) <= s <= H(10, 50) or (H(13, 15) <= s <= dl): return "02:00-02:35"
    # (dl, 02:35): the alternate, if it reaches
    if s > dl or s < H(2, 35):
        if s >= H(13, 15) or s <= al: return "13:14-13:15"
    return None
def plan(kit, legs, t, arg):
    pin, k = KITS[kit]; kp = k if k.startswith("/") else f"{D}/kits/{k}"
    r = subprocess.run([PY, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", kp, "--legs", legs, "--t0", str(t),
                        "--batch-window", arg], cwd=f"{D}/wt/{pin}", capture_output=True, text=True, env=ENV)
    os.makedirs(f"{D}/plans/{TAG}", exist_ok=True)
    open(f"{D}/plans/{TAG}/plan-{kit}-{legs.split(',')[0]}-{legs.split(',')[-1]}-{dt.datetime.fromtimestamp(t, TZ).strftime('%a%H%M%S')}.json", "w").write(r.stdout + r.stderr)
    assert r.returncode == 0, (kit, legs, lt(t), arg, r.stderr[-300:])
    return json.loads(r.stdout)
def L(a, b): return ",".join(f"L{i:03d}" for i in range(a, b + 1))
rows, busy = [], []
f0_t0 = [ep("2026-11-14T16:43:46")]   # item 319; item 325's t0 (Sat evening) is older than 4 h before any F0 below
def first_legal(kit, n, t, hp=False, quota=2):
    pin = KITS[kit][0]; w = W(n, quota)
    while True:
        a = arg_for(pin, w, t)
        if a and (not hp or t + w <= at(t - H(0, 30), (0, 30), 1)):   # hp-01: worst-case end by the next 00:30
            return t, a
        t += 10 if a is None and H(10, 50) < sod(t) < H(13, 15) else 1
        if H(10, 50) < sod(t) < H(13, 15): t = at(t, (13, 15))
def span(name, kit, legs, ready, gate, hp=False, not_before=None, quota=2):
    n = len(legs.split(",")); t = max(ready, not_before or 0)
    t0, a = first_legal(kit, n, t, hp, quota)
    p = plan(kit, legs, t0, a)
    assert p["worst_case_s"] == W(n, quota)
    end = t0 + p["expected_s"]; worst = t0 + p["worst_case_s"]
    rows.append(dict(name=name, kind="span", kit=kit, legs=legs, t0=t0, arg=a, exp=p["expected_s"], worst_s=p["worst_case_s"],
                     end=end, worst_end=worst, wait=t0 - ready, gate=gate))
    busy.append((t0, end, name)); return end
def f0(name, ready, gate):
    t = max(ready, f0_t0[-1] + 14400)
    if sod(t) > H(22, 40) or sod(t) < H(2, 35):
        t = at(t, (2, 35), 1 if sod(t) > H(22, 40) else 0)
    day = dt.datetime.fromtimestamp(t, TZ).date()
    if sum(1 for x in f0_t0 if dt.datetime.fromtimestamp(x, TZ).date() == day) >= 3: return None
    f0_t0.append(t); end = t + 7134
    rows.append(dict(name=name, kind="F0", kit="partc", legs="Part C", t0=t, arg="(c3f4)", exp=7134, worst_s=12180,
                     end=end, worst_end=t + 12180, wait=t - ready, gate=gate))
    busy.append((t, end, name)); return end
def f2(name, ready, piece):
    legs = L(3 * piece - 2, 3 * piece)
    return span(name, "f2", legs, ready, "F2 READY (RL-169a); ladder P, F0, F2", quota=0)

S = ep("2026-11-15T00:00"); MON = ep("2026-11-16T00:00"); TUE = ep("2026-11-17T00:00"); WED = ep("2026-11-18T00:00"); THU = ep("2026-11-19T00:00")
e = span("dev-01-s04 (item 331)", "dev01", L(8, 12), ep("2026-11-15T00:20"), "issued; t0 00:20 forecast by the lead")
e = span("hp-01-s01 smoke", "hp01", L(1, 3), e + QUIET, "s04 closed + Check; RL-155 §5.2; line 2; line 9 s03 desk", hp=True)
e = span("hp-01-s02", "hp01", L(4, 7), e + HAND, "smoke hand-read + R9; s04 desk final; CI base+0", hp=True)
e = span("hp-01-s03", "hp01", L(8, 12), e + QUIET, "s02 closed clean; smoke desk final", hp=True)
e = span("dev-02-s02", "dev02", L(1, 6), e + QUIET, "append committed; RL-155 §3.3; line 9 hp-01-s02 desk; Sunday")
state = {"piece": 1, "last": "span"}
HELD = []      # (from, until, why): a READY counted span held by RL-172 (a)'s date rule ("idle for day balance")
EVENTS = []    # host events (the RL-172 (h) restart)
def nxt(e):
    """The successor's earliest start: 300 s after a campaign close, 1,200 s after F0, F2 or any other close (RL-171 §6.1, RL-172 §0, (d))."""
    return e + (QUIET if state["last"] == "span" else 1200)
def ladder_until(e, until, why, f0_hold_until=None):
    """Fill [e, until) with the ladder (F2 if READY, F0 on its rules) while the next counted span is held to `until`."""
    if why: HELD.append((nxt(e), until, why))
    while True:
        start = nxt(e)
        t_f0 = max(start, f0_t0[-1] + 14400, f0_hold_until or 0)
        if F2 and state["piece"] <= 4 and (t_f0 - start >= 3600 or sod(t_f0) > H(22, 40) or sod(t_f0) < H(2, 35)) \
                and start + 7442 + 1200 <= until:
            e = f2(f"F2 piece {state['piece']}", start, state["piece"]); state["piece"] += 1; state["last"] = "F2"; continue
        if sod(t_f0) > H(22, 40): t_f0 = at(t_f0, (2, 35), 1)       # F0 launch window 02:35-22:40 (c3f4 soak_child)
        elif sod(t_f0) < H(2, 35): t_f0 = at(t_f0, (2, 35))
        while sum(1 for x in f0_t0 if dt.datetime.fromtimestamp(x, TZ).date() == dt.datetime.fromtimestamp(t_f0, TZ).date()) >= 3:
            t_f0 = at(t_f0, (2, 35), 1)                                # three F0 a day: next day 02:35
        if t_f0 >= until: break
        r = f0("F0 (standing, trigger c)", t_f0, "no staged item can hold within 2 h 30")
        if r is None: break
        e = r; state["last"] = "F0"
    return e
# RL-172 (h): the restart at 14:08 (+-15 min) on Sunday, once dev-02's first half has closed; no F0 after 12:00 until done.
# Modelled as 20 min of host event (the lead's remote proof, the restart, the readback); its close counts as "other".
RESTART = ep("2026-11-15T14:08")
assert e <= RESTART + 900, "dev-02-s02 not closed by 14:23: the restart moves to the next span boundary"
EVENTS.append((max(e, RESTART), max(e, RESTART) + 1200, "RL-172 (h) restart and readback"))
state["last"] = "span"
e = max(e, RESTART) + 1200; state["last"] = "other"
# Sunday rest: dev-02-s03 is the Monday half (RL-165 §2; RL-172 (a))
e = ladder_until(e, MON, "dev-02-s03 dated Monday (6 + 6 split; RL-172 (a))")
e = span("dev-02-s03", "dev02", L(7, 12), nxt(e), "s02 checked; line 9 hp-01-s03 desk; Monday", not_before=MON); state["last"] = "span"
e = span("dev-03-s01 pilot", "dev03", L(1, 3), nxt(e), "READY+staged; dev-02 closed; line 9 dev-02-s02 desk; dated Monday")
e = span("dev-03-s02 rest (nine)", "dev03", L(4, 12), e + HAND, "hand-read R9 + L002 released; append; line 9 dev-02-s03 desk; dated Monday")
e = ladder_until(e, TUE if DAYBAL else e, "dev-04 dated Tuesday (RL-172 (a): <= 12 mixed-size legs a date)")
e = span("dev-04-s01", "dev04", L(1, 6), nxt(e), "delta ADMIT; Q6; line 9 dev-03 pilot desk; dated Tuesday", not_before=TUE if DAYBAL else None); state["last"] = "span"
e = span("dev-04-s02", "dev04", L(7, 12), nxt(e), "L005 released or >=4 of dev-03's 5 consumers; line 9 dev-03 rest desk; Tuesday")
e = ladder_until(e, WED if DAYBAL else e, "dev-05 dated Wednesday (RL-172 (a))")
e = span("dev-05-s01", "dev05", L(1, 6), nxt(e), "delta ADMIT; Q6; line 9 dev-04-s01 desk; dated Wednesday", not_before=WED if DAYBAL else None); state["last"] = "span"
e = span("dev-05-s02", "dev05", L(7, 12), nxt(e), "line 9 dev-04-s02 desk; Wednesday")
# After development: the ladder until Thu 00:00 (freeze 2, look manifest, qual kits not READY)
e = ladder_until(e, THU, None)
def idle(busy, a, b):
    t = 0; cur = a
    for s, en, _ in sorted(busy):
        s, en = max(s, a), min(en, b)
        if en <= cur: continue
        if s > cur: t += s - cur
        cur = max(cur, en)
    return (t + max(0, b - cur)) / 3600
def gaps(busy, a, b, minimum=600):
    out = []; cur = a
    for s, en, n in sorted(busy):
        if en <= a or s >= b: continue
        if s - cur >= minimum: out.append((cur, s, n))
        cur = max(cur, en)
    if b - cur >= minimum: out.append((cur, b, None))
    return out
days = [("Sun", S, MON), ("Mon", MON, TUE), ("Tue", TUE, WED), ("Wed", WED, THU)]
def held_idle(a, b):
    t = 0
    for h0, h1, _ in HELD:
        x0, x1 = max(h0, a), min(h1, b)
        if x1 > x0: t += idle(busy, x0, x1) * 3600
    return round(t / 3600, 2)
res = {"tag": TAG, "daybal": DAYBAL, "events": [(lt(a), lt(b), w) for a, b, w in EVENTS], "held": [(lt(a), lt(b), w) for a, b, w in HELD],
       "idle_daybalance_h": {d: held_idle(a, b) for d, a, b in days}, "quiet": QUIET, "hand": HAND, "f2": F2, "rows": rows,
       "idle_h": {d: round(idle(busy, a, b), 2) for d, a, b in days},
       "gaps": [(lt(a), lt(b), round((b - a) / 3600, 2), n) for a, b, n in gaps(busy, S, THU)]}
json.dump(res, open(f"{D}/plans/chain-{TAG}.json", "w"), indent=1, default=str)
for r in rows:
    print(f"{r['name']:<28} {r['kit']:<6} {r['legs'][:9]+'..' if len(r['legs'])>12 else r['legs']:<12} t0 {lt(r['t0'])} ({r['t0']}) arg {r['arg']:<12} "
          f"exp {r['exp']:>6} end {lt(r['end'])} worst {lt(r['worst_end'])} waited {r['wait']}s")
print("idle h/day", res["idle_h"]); print("of which idle for day balance", res["idle_daybalance_h"]); print("held", res["held"])
for g in res["gaps"]: print("gap", g)
