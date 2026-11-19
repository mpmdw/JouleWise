"""Clock placement of each capture leg's own window reference (span_ns) and its G0 gate (thermal journal only:
monotonic->wall median offset, as maint_overlap.py; window reference span_ns/status only). Prints PST times. Gates nothing.
Usage: python3 -I -B ref_window_place.py OUT L001 ..."""
import json, statistics, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
TZ = ZoneInfo("America/Los_Angeles"); NS = 10**9
root = Path(sys.argv[1])
for leg in sys.argv[2:]:
    lr = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    out = root / lr["attempts"][-1]["output_dir"] / lr["result"]["bundle"] / "outputs"
    rows = [json.loads(l) for l in (out / "align_thermal.jsonl").read_text().splitlines() if l.strip()]
    off = statistics.median(r["started"]["wall_ns"] - r["started"]["monotonic_ns"] for r in rows if r["kind"] == "reading")
    w = lambda ns: datetime.fromtimestamp((ns + off) / NS, TZ).strftime("%H:%M:%S")
    g0 = [r["values"]["gate"] for r in rows if r["kind"] == "align_thermal_gate" and r["values"].get("gate", {}).get("kind") == "G0"][0]
    rp = out / "align_window_reference.json"
    ref = json.loads(rp.read_text()) if rp.is_file() else None
    print(leg, json.dumps({"attempt": lr["attempts"][-1]["attempt"], "ref_status": ref and ref["status"],
                           "ref_window_pst": ref and [w(ref["span_ns"][0]), w(ref["span_ns"][1])],
                           "g0_pst": [w(g0["start_ns"]), w(g0["end_ns"])] if g0.get("start_ns") else [None, w(g0["end_ns"])]}))
