# RL-157 §1 print, item 334 "Check" verbatim (gates nothing)
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = [json.loads(line) for line in (root / "chain-stages.jsonl").read_text().splitlines()]
ends, starts = {}, {}
for d in rows:
    (ends if d.get("event") == "end" else starts).setdefault(d["stage_id"], d)
hp_end = (ends.get("high_power") or {}).get("ended_epoch_s")
soak_end = (ends.get("soak") or {}).get("ended_epoch_s")
rec = json.loads((root / "legs" / "L001" / "leg_record.json").read_text())
n = len(rec.get("attempts") or [])
leg_start = (starts.get(f"L001.a{n}") or {}).get("started_epoch_s")
g0_entry = None
bname = (rec.get("result") or {}).get("bundle")
if bname:
    p = root / "legs" / "L001" / "runtime" / bname / "outputs" / "align_thermal.jsonl"
    if p.is_file():
        for line in p.read_text().splitlines():
            d = json.loads(line)
            g = (d.get("values") or {}).get("gate") or {}
            if d.get("module") == "temperature" and d.get("kind") == "align_thermal_gate" and g.get("kind") == "G0":
                g0_entry = g.get("entry_epoch_s"); break
def diff(a, b):
    return None if a is None or b is None else round(a - b, 1)
print("RL-157 §1", json.dumps({"soak_end_epoch_s": soak_end, "high_power_end_epoch_s": hp_end,
      "L001_attempts": n, "L001_attempt_start_epoch_s": leg_start, "L001_g0_entry_epoch_s": g0_entry,
      "soak_end_to_mode_set_s": diff(hp_end, soak_end),
      "mode_set_to_L001_attempt_start_s": diff(leg_start, hp_end),
      "mode_set_to_L001_G0_start_s": diff(g0_entry, hp_end)}, sort_keys=True))
