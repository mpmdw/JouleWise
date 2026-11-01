"""Search for inputs distinguishing L9-ENV-4 mutants M01 (shifted start), M02 (shifted end),
M03 (<=) from the clamp's midpoint rule.  Usage: equiv_search.py ROOT TRIALS SEED"""
import json, random, sys, types
from pathlib import Path
ROOT = Path(sys.argv[1]); sys.path.insert(0, str(ROOT))
from joulewise.bundle_read import TracePoint, Window
import joulewise.whole_window as W
SRC = (ROOT / "joulewise/whole_window.py").read_text()
MID = ("                    Window(\n                        start_s=(window.start_s + window.end_s) / 2.0,\n"
       "                        end_s=(window.start_s + window.end_s) / 2.0,\n                    )")
MUT = {
 "M01_start": [(MID, "                    Window(\n                        start_s=window.start_s,\n                        end_s=window.start_s,\n                    )")],
 "M02_end": [(MID, "                    Window(\n                        start_s=window.end_s,\n                        end_s=window.end_s,\n                    )")],
 "M03_le": [("                    if window.end_s < window.start_s\n                    else window",
             "                    if window.end_s <= window.start_s\n                    else window")],
}
mods = {}
for name, pairs in MUT.items():
    src = SRC
    for o, n in pairs:
        assert src.count(o) == 1, name
        src = src.replace(o, n)
    m = types.ModuleType(name); m.__file__ = str(ROOT / "joulewise/whole_window.py")
    sys.modules[name] = m; exec(compile(src, name, "exec"), m.__dict__); mods[name] = m
trials, seed = int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
found = {k: 0 for k in mods}; examples = []
for trial in range(trials):
    interval = rng.random() < 0.6
    dt = rng.choice([0.01, 0.0731, 0.05, 0.1, 0.25, 0.0123])
    epoch = rng.choice([0.0, 1761700000.0, 1793232000.123456])
    n = 160
    curve = [TracePoint(t=epoch + i*dt + (dt/2 if interval else 0), power_w=rng.choice([0.0, rng.uniform(0, 12), rng.uniform(0, 1e-3)]),
                        support_start_s=(epoch + i*dt) if interval else None, support_end_s=(epoch + (i+1)*dt) if interval else None)
             for i in range(n)]
    edge = rng.uniform(0.005, 0.2)
    T = n*dt
    contribs = []
    for _c in range(rng.randint(1, 2)):
        ws = []
        for _ in range(rng.randint(1, 4)):
            s = rng.uniform(0.5, T - 1.0)
            L = rng.choice([0.0, rng.uniform(0, 2*edge), rng.uniform(0, 3.0), 2*edge])
            ws.append(Window(start_s=epoch + s, end_s=epoch + s + L))
        contribs.append((curve, ws))
    bb = rng.choice([0.0, 0.0005, 0.01, rng.uniform(0, 0.05)])
    span = rng.choice([0.0, 0.0012, rng.uniform(0, 0.01)])
    a = json.dumps(W._clamped_corner_composed_anchor_shift_envelope(contribs, bb, edge, span))
    for name, m in mods.items():
        b = json.dumps(m._clamped_corner_composed_anchor_shift_envelope(contribs, bb, edge, span))
        if a != b:
            found[name] += 1
            if len(examples) < 6:
                examples.append({"mutant": name, "trial": trial, "seed": seed, "a": a[:300], "b": b[:300]})
print(json.dumps({"seed": seed, "trials": trials, "distinguishing": found}))
for e in examples: print(json.dumps(e))
