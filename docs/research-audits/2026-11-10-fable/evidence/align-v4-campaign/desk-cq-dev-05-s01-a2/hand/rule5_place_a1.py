"""Rule 5 placement, FIRST attempt (dev-05-s01-a2 L004.a1): each leg's runs over 0.5 core (RL-72 E2 threshold) of 3 s or more, with clock times.
Reads ONLY legs/<L>/runtime/load_journal.json (cpu_busy_cores, cpu_busy_t_s) and leg_record.json (attempt
started_epoch_s). Prints run length, max cores and PST clock span. Gates nothing; rule 5 itself is hand_table.py's.
Usage: python3 -I -B rule5_place.py OUT L001 ..."""
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
TZ = ZoneInfo("America/Los_Angeles")
root = Path(sys.argv[1])
for leg in sys.argv[2:]:
    lr = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    a = lr["attempts"][0]  # first attempt (L004.a1, rejected)
    lj = json.loads((root / a["output_dir"] / "load_journal.json").read_text())
    c, t = lj["cpu_busy_cores"], lj["cpu_busy_t_s"]
    runs, i = [], 0
    while i < len(c):
        if c[i] > 0.5:
            j = i
            while j + 1 < len(c) and c[j + 1] > 0.5:
                j += 1
            if j - i + 1 >= 3:
                f = lambda s: datetime.fromtimestamp(a["started_epoch_s"] + s, TZ).strftime("%H:%M:%S")
                runs.append({"len_samples": j - i + 1, "t_s": [round(t[i], 1), round(t[j], 1)], "pst": [f(t[i]), f(t[j])],
                             "max_cores": round(max(c[i:j + 1]), 3)})
            i = j + 1
        else:
            i += 1
    print(leg, json.dumps({"attempt": a["attempt"], "runs_ge_3s": runs}))
