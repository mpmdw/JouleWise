"""Is M01 (clamp inverted window to zero length at its shifted START instead of midpoint) equivalent?
Search for a distinguishing input directly against the analysis function's mutated body."""
import json, random, sys, types
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from mutants import MUTANTS
import joulewise.whole_window as W
from joulewise.bundle_read import TracePoint, Window
src = (ROOT / "joulewise/whole_window.py").read_text()
old, new = MUTANTS["M01_clamp_to_start"][0]
m = types.ModuleType("m01"); sys.modules["m01"] = m; m.__file__ = str(ROOT / "joulewise/whole_window.py"); exec(compile(src.replace(old, new), "m01", "exec"), m.__dict__)
rng = random.Random(11)
found = []
for trial in range(4000):
    interval = trial % 2 == 0
    dt = rng.choice([0.01, 0.05, 0.1, 0.25])
    n = 120
    curve = [TracePoint(t=i*dt + (dt/2 if interval else 0), power_w=rng.uniform(0, 10),
                        support_start_s=i*dt if interval else None, support_end_s=(i+1)*dt if interval else None) for i in range(n)]
    edge = rng.uniform(0.01, 0.2)
    T = n*dt
    ws = []
    for _ in range(rng.randint(1, 3)):
        s = rng.uniform(0.0, T - 0.05)
        ws.append(Window(start_s=s, end_s=min(T, s + rng.uniform(0, 2*edge))))
    bb = rng.choice([0.0, 0.0005, 0.01])
    a = W._clamped_corner_composed_anchor_shift_envelope([(curve, ws)], bb, edge, 0.0)
    b = m._clamped_corner_composed_anchor_shift_envelope([(curve, ws)], bb, edge, 0.0)
    if json.dumps(a) != json.dumps(b):
        found.append({"interval": interval, "dt": dt, "edge": edge, "bb": bb, "windows": [(w.start_s, w.end_s) for w in ws],
                      "midpoint": a, "start": b})
        if len(found) >= 3: break
print("trials", trial + 1, "distinguishing inputs", len(found))
for f in found: print(json.dumps(f)[:900])
