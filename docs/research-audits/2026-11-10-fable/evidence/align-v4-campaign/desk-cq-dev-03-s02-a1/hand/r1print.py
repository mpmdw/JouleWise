import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
KEYS = ("TV0h", "TV1h", "Tf08")
def rows(path):
    out = []
    for line in path.read_text().splitlines():
        d = json.loads(line)
        if d.get("module") == "temperature" and d.get("kind") in ("reading", "align_thermal_gate"):
            out.append(d)
    return out
def reading(d):
    return d["started"]["monotonic_ns"], (d["values"].get("sensors") or {})
soak = json.loads((root / "soak" / "soak_reference.json").read_text())
sj = [reading(d) for d in rows(root / "soak" / "idle_soak" / "sensors" / "align_thermal.jsonl") if d["kind"] == "reading"]
end = sj[-1][0]
tail = [s for t, s in sj if t > end - 1200 * 10**9]
tf08 = [s["Tf08"] for s in tail if isinstance(s.get("Tf08"), (int, float))]
print("soak_reference", {k: soak["sensors_c"].get(k) for k in ("TV0h", "TV1h")},
      "Tf08_last1200s_mean", statistics.fmean(tf08) if tf08 else None)
l004_ref = json.loads((root / "legs" / "L004" / "runtime" / "runs" / "cadence-cl-dev-03-l004" / "outputs" / "align_window_reference.json").read_text())
for leg in ("L004", "L005", "L006", "L007", "L008", "L009", "L010", "L011", "L012"):  # dev-03-s02 roster (v1.1: a consumer leg has no own window reference)
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    bname = (rec.get("result") or {}).get("bundle")
    if not bname:
        print(leg, json.dumps({"no_bundle": True, "leg_status": rec.get("leg_status")})); continue
    out = root / "legs" / leg / "runtime" / bname / "outputs"
    j = rows(out / "align_thermal.jsonl")
    reads = [reading(d) for d in j if d["kind"] == "reading"]
    rp = out / "align_window_reference.json"
    ref = json.loads(rp.read_text()) if rp.is_file() else None
    ref_tf08 = []
    if ref:
        lo, hi = ref["span_ns"]
        ref_tf08 = [s["Tf08"] for t, s in reads if lo <= t <= hi and isinstance(s.get("Tf08"), (int, float))]
    g0 = next((d["values"]["gate"] for d in j if d["kind"] == "align_thermal_gate"
               and d["values"].get("gate", {}).get("kind") == "G0"), None)
    at = next((s for t, s in reads if g0 and t == g0.get("exit_sample_ns")), {})
    print(leg, json.dumps({
        "own_reference": None if ref is None else {"status": ref["status"], "TV0h": ref["fast_c"], "TV1h": ref["slow_c"],
                          "Tf08_median": statistics.median(ref_tf08) if ref_tf08 else None},
        "own_reference_file": "present" if ref else "absent (consumer leg, v1.1)",
        "g0_reference_equals_L004_capture": None if g0 is None else bool(
            g0.get("reference", {}).get("span_ns") == l004_ref["span_ns"] and g0.get("reference", {}).get("fast_c") == l004_ref["fast_c"]),
        "g0": None if g0 is None else {"outcome": g0["outcome"], "duration_s": g0["duration_s"],
                                       "row_reference": g0.get("reference"), "row_release": g0.get("release"),
                                       "release": {k: at.get(k) for k in KEYS}}}, sort_keys=True))
