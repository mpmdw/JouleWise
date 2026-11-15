# RL-157 §1 print, item 334 "Check" verbatim (gates nothing); hp-01-s02 copy: the first leg is argv[2] (L004) instead of a hard-coded L001
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
FIRST = sys.argv[2] if len(sys.argv) > 2 else "L001"
rows = [json.loads(line) for line in (root / "chain-stages.jsonl").read_text().splitlines()]
ends, starts = {}, {}
for d in rows:
    (ends if d.get("event") == "end" else starts).setdefault(d["stage_id"], d)
hp_end = (ends.get("high_power") or {}).get("ended_epoch_s")
soak_end = (ends.get("soak") or {}).get("ended_epoch_s")
rec = json.loads((root / "legs" / FIRST / "leg_record.json").read_text())
n = len(rec.get("attempts") or [])
leg_start = (starts.get(f"{FIRST}.a{n}") or {}).get("started_epoch_s")
g0_entry = None
bname = (rec.get("result") or {}).get("bundle")
if bname:
    p = root / "legs" / FIRST / "runtime" / bname / "outputs" / "align_thermal.jsonl"
    if p.is_file():
        for line in p.read_text().splitlines():
            d = json.loads(line)
            g = (d.get("values") or {}).get("gate") or {}
            if d.get("module") == "temperature" and d.get("kind") == "align_thermal_gate" and g.get("kind") == "G0":
                g0_entry = g.get("entry_epoch_s"); break
def diff(a, b):
    return None if a is None or b is None else round(a - b, 1)
print("RL-157 §1", json.dumps({"soak_end_epoch_s": soak_end, "high_power_end_epoch_s": hp_end,
      f"{FIRST}_attempts": n, f"{FIRST}_attempt_start_epoch_s": leg_start, f"{FIRST}_g0_entry_epoch_s": g0_entry,
      "soak_end_to_mode_set_s": diff(hp_end, soak_end),
      f"mode_set_to_{FIRST}_attempt_start_s": diff(leg_start, hp_end),
      f"mode_set_to_{FIRST}_G0_start_s": diff(g0_entry, hp_end)}, sort_keys=True))
