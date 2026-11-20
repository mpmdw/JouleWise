"""OS thermal level / pm_state census for each leg (thermal journal status fields only; prints counts and turn-relative times)."""
import json, sys, glob
from collections import Counter
NS = 10**9
root = sys.argv[1]
for leg in sys.argv[2:]:
    res = json.load(open(f"{root}/legs/{leg}/leg_record.json"))["result"]
    p = glob.glob(f"{root}/legs/{leg}/runtime/runs/*/outputs/align_thermal.jsonl")[0]
    reads = [r for r in (json.loads(l) for l in open(p) if l.strip()) if r["kind"] == "reading"]
    ts, te = res["turn_start_ns"], res["turn_end_ns"]
    out = {}
    for name, sel in (("turn", lambda t: ts <= t <= te), ("whole_leg", lambda t: True)):
        rs = [r for r in reads if sel(r["started"]["monotonic_ns"])]
        lv = Counter(r["values"]["status"].get("os_level") for r in rs)
        st = Counter(r["values"]["status"].get("pm_state") for r in rs)
        nonnom = [(r["started"]["monotonic_ns"] - ts) / NS for r in rs if r["values"]["status"].get("pm_state") not in ("Nominal", None)]
        out[name] = {"readings": len(rs), "os_level": {str(k): v for k, v in lv.items()}, "pm_state": {str(k): v for k, v in st.items()},
                     "non_nominal_from_turn_start_s": [round(min(nonnom), 1), round(max(nonnom), 1)] if nonnom else None}
    print(leg, json.dumps(out, sort_keys=True))
