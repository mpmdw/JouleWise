"""R2 (0.6.2): mirror vs a literal re-execution of reduce._reduce_v060's grouping on multi-source / multi-request /
overlapping-window shapes, using a duck-typed reader. Also 0.5.2 with multi-interval phases, several items/blocks/levels."""
import sys, json, math, random
from pathlib import Path
ROOT = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(ROOT))
import joulewise.reduce as R
import joulewise.whole_window as W
from joulewise.bundle_read import TracePoint, Window, ItemWindow
import inspect

def curve(seed, o, n=80, w=0.05):
    rnd = random.Random(seed)
    return [TracePoint(t=o+(i+0.5)*w, power_w=rnd.uniform(0, 50), support_start_s=o+i*w, support_end_s=o+(i+1)*w) for i in range(n)]

class Reader62:
    def __init__(self, rpw, sources, raw, o):
        self._rpw = rpw; self._src = sources; self._raw = raw
    def summed_curve(self): return self._raw
    def request_phase_windows(self): return dict(self._rpw)
    def source_curve(self, s): return self._src[s]

def reduce_v060_literal(reader, anchor_curve):
    """Lines copied from reduce._reduce_v060 (grouping + per-phase contributions), kept literal."""
    curve = reader.summed_curve()
    anchor_shift_s = 0.0
    if anchor_curve is not None:
        if curve:
            anchor_shift_s = anchor_curve[0].t - curve[0].t
        curve = anchor_curve
    def _source_curve(source_identity):
        return R._shift_curve(reader.source_curve(source_identity), anchor_shift_s)
    request_windows = reader.request_phase_windows()
    group_windows = {}
    for (source, _request_id, phase, _ordinal), phase_window in request_windows.items():
        group_windows.setdefault((source, phase), []).append(phase_window)
    group_unions = {key: R._union_windows(windows) for key, windows in group_windows.items()}
    out = []
    for phase in sorted({phase for _source, phase in group_unions}):
        contributions = [(_source_curve(source), windows) for (source, candidate), windows in sorted(group_unions.items()) if candidate == phase]
        out.append(("/phase_energy_j/" + R._json_pointer_token(phase), contributions))
    return out

def eq_contribs(a, b):
    if len(a) != len(b): return False
    for (c1, w1), (c2, w2) in zip(a, b):
        if len(c1) != len(c2) or len(w1) != len(w2): return False
        if any(p.t != q.t or p.power_w != q.power_w or p.support_start_s != q.support_start_s or p.support_end_s != q.support_end_s for p, q in zip(c1, c2)): return False
        if any(x.start_s != y.start_s or x.end_s != y.end_s for x, y in zip(w1, w2)): return False
    return True

fails = 0; cases = 0
rnd = random.Random(3)
for trial in range(300):
    o = rnd.choice([0.0, 1.7e9 + rnd.random()])
    sources = [f"src{i}" for i in range(rnd.randint(1, 3))]
    phases = rnd.sample(["prefill", "decode", "tokenize", "a/b", "x~y"], rnd.randint(1, 4))
    rpw = {}
    for s in sources:
        for r in range(rnd.randint(1, 4)):
            for i, ph in enumerate(phases):
                st = o + rnd.uniform(0.2, 3.0); d = rnd.choice([1e-4, 0.01, 0.05, 0.2, 0.6])
                rpw[(s, f"request-{r:03d}", ph, i)] = Window(st, st + d)
    srcs = {s: curve(hash((trial, s)) % 1000, o - 1.0) for s in sources}
    raw = curve(trial, o - 1.0)
    shift = rnd.choice([0.0, 0.0123, -0.0077])
    anchor = R._shift_curve(raw, shift) if rnd.random() < 0.8 else None
    reader = Reader62(rpw, srcs, raw, o)
    mine = W._group_envelope_contributions(reader, "0.6.2", anchor)
    lit = reduce_v060_literal(reader, anchor)
    cases += 1
    if [p for p, _ in mine] != [p for p, _ in lit] or any(not eq_contribs(a, b) for (_, a), (_, b) in zip(mine, lit)):
        fails += 1; print("MISMATCH 0.6.2 trial", trial)
print(f"0.6.2 structural: {cases} random shapes, mismatches={fails}")

# 0.5.2: multi-interval phases, several items/blocks/levels vs _energy_anchor_envelopes_v05's argument construction
class Reader52:
    def __init__(self, raw, ph, items, blocks, levels): self._raw=raw; self._ph=ph; self._it=items; self._bl=blocks; self._lv=levels
    def summed_curve(self): return self._raw
    def phase_windows(self): return dict(self._ph)
    def item_windows(self): return list(self._it)
    def block_windows(self): return dict(self._bl)
    def level_windows(self): return dict(self._lv)
def v05_literal(reader, curve):
    # exactly the argument construction in reduce._reduce -> _energy_anchor_envelopes_v05, then its iteration order
    phase_windows = reader.phase_windows()
    item_windows = [(f"{item.item_index}:{item.item_id}", item.window) for item in reader.item_windows()]
    block_windows = reader.block_windows()
    level_windows = {f"{block_id}/{level_id}": intervals for (block_id, level_id), intervals in reader.level_windows().items()}
    out = []
    for phase, intervals in sorted((phase_windows or {}).items()): out.append(("/phase_energy_j/" + R._json_pointer_token(phase), [(curve, intervals)]))
    for key, item_window in item_windows or []: out.append(("/suite_item_energy_j/" + R._json_pointer_token(key), [(curve, [item_window])]))
    for block_id, intervals in sorted((block_windows or {}).items()): out.append(("/suite_block_energy_j/" + R._json_pointer_token(block_id), [(curve, intervals)]))
    for level_key, intervals in sorted((level_windows or {}).items()): out.append(("/suite_level_energy_j/" + R._json_pointer_token(level_key), [(curve, intervals)]))
    return out
sig = inspect.signature(ItemWindow)
print("ItemWindow fields:", list(sig.parameters))
f52 = 0; c52 = 0
for trial in range(300):
    o = rnd.choice([0.0, 1.7e9 + rnd.random()])
    raw = curve(trial + 1000, o - 1.0)
    ph = {p: [Window(o + rnd.uniform(0.2, 3.0), o + rnd.uniform(0.2, 3.0) + 0.01) for _ in range(rnd.randint(1, 3))] for p in rnd.sample(["prefill", "decode", "tokenize", "gen/setup"], rnd.randint(0, 4))}
    items = []
    for idx in rnd.sample(range(10), rnd.randint(0, 4)):
        st = o + rnd.uniform(0.2, 3.0)
        kwargs = {k: None for k in sig.parameters}
        kwargs.update(item_id=f"item_{idx}", item_index=idx, window=Window(st, st + 0.05))
        try: items.append(ItemWindow(**kwargs))
        except TypeError as e: print("ItemWindow ctor", e); break
    items.sort(key=lambda i: i.item_index)
    blocks = {f"blk{j}": [Window(o + 0.3 * j, o + 0.3 * j + 0.2)] for j in range(rnd.randint(0, 3))}
    levels = {(f"blk{j}", f"lvl{k}"): [Window(o + 0.3 * j + 0.05 * k, o + 0.3 * j + 0.05 * k + 0.03)] for j in range(rnd.randint(0, 3)) for k in range(rnd.randint(0, 3))}
    reader = Reader52(raw, ph, items, blocks, levels)
    anchor = R._shift_curve(raw, 0.01) if rnd.random() < 0.8 else None
    mine = W._group_envelope_contributions(reader, "0.5.2", anchor)
    lit = v05_literal(reader, anchor if anchor is not None else raw)
    c52 += 1
    if [p for p, _ in mine] != [p for p, _ in lit] or any(not eq_contribs(a, b) for (_, a), (_, b) in zip(mine, lit)):
        f52 += 1; print("MISMATCH 0.5.2 trial", trial, [p for p,_ in mine][:5], [p for p,_ in lit][:5])
print(f"0.5.2 structural: {c52} random shapes, mismatches={f52}")
print("RESULT:", "PASS" if fails == 0 and f52 == 0 else "FAIL")
