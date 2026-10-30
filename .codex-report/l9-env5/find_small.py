import json, random, sys, types
from pathlib import Path
ROOT = Path(sys.argv[1]); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from joulewise.bundle_read import TracePoint, Window
import joulewise.whole_window as W
from equiv_search_mods import mods
from tests.test_whole_window_inverted_corner_clamp import oracle_module
O = oracle_module()

def case(seed):
    rng = random.Random(seed)
    interval = rng.random() < 0.5
    dt = rng.choice([0.05, 0.1, 0.0731])
    n = 40
    curve = [TracePoint(t=i*dt + (dt/2 if interval else 0), power_w=round(rng.uniform(0, 12), 3),
                        support_start_s=i*dt if interval else None, support_end_s=(i+1)*dt if interval else None) for i in range(n)]
    edge = round(rng.uniform(0.02, 0.2), 4)
    ws = []
    for _ in range(rng.randint(2, 3)):
        s = round(rng.uniform(0.5, n*dt - 1.0), 4)
        L = round(rng.choice([rng.uniform(0, 2*edge), rng.uniform(0, 1.0)]), 4)
        ws.append(Window(start_s=s, end_s=s + L))
    bb = rng.choice([0.0, 0.0005, 0.01])
    return [(curve, ws)], bb, edge, 0.0
hits = {}
for seed in range(int(sys.argv[2])):
    args = case(seed)
    a = json.dumps(W._clamped_corner_composed_anchor_shift_envelope(*args))
    o = json.dumps(O._corner_composed_anchor_shift_envelope(*args))
    assert a == o, seed
    for name, m in mods.items():
        if json.dumps(m._clamped_corner_composed_anchor_shift_envelope(*args)) != a:
            hits.setdefault(name, []).append(seed)
print({k: v[:10] for k, v in hits.items()}, {k: len(v) for k, v in hits.items()})
