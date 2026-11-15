"""Hand table for the cl-dev-01 pilot, built from raw records WITHOUT joulewise.cadence.desk.

Opens only: runner_receipt.json, span_plan.json, chain-stages.jsonl, censuses.jsonl,
volume_censuses.jsonl, legs/*/leg_record.json, legs/*/runtime/load_journal.json (outside-load
journal; keys checked: no energy/power key), each leg's outputs/align_thermal.jsonl. Then compares
with the automatic desk's desk_summary.json and stops.json.
Usage: python3 -I -B hand_table.py OUT AUTO_DIR OUT_JSON
"""
import json
import sys
from pathlib import Path

root, auto, out_json = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
NS = 10**9
rec = json.loads((root / "runner_receipt.json").read_text())
plan = json.loads((root / "span_plan.json").read_text())
stages = [json.loads(l) for l in (root / "chain-stages.jsonl").read_text().splitlines() if l.strip()]
censuses = [json.loads(l) for l in (root / "censuses.jsonl").read_text().splitlines() if l.strip()]
vols = [json.loads(l) for l in (root / "volume_censuses.jsonl").read_text().splitlines() if l.strip()]
steps = {s["name"]: s for s in rec["steps"]}
stage_end = {s["stage_id"]: s for s in stages if s["event"] == "end"}
budgets = {l["leg_id"]: l for l in plan["legs"]}
rules = json.loads(Path(sys.argv[4]).read_text())["stop_rules"] if len(sys.argv) > 4 else {"leg_time_factor": 1.5,
                                                                                         "contaminated_redos_max": 3}
rows = []
for leg_id in rec["roster"]:
    lr = json.loads((root / "legs" / leg_id / "leg_record.json").read_text())
    res = lr["result"]
    load = json.loads((root / "legs" / leg_id / "runtime" / "load_journal.json").read_text())
    thermal = [json.loads(l) for l in (root / "legs" / leg_id / "runtime" / res["bundle"] / "outputs" /
                                        "align_thermal.jsonl").read_text().splitlines() if l.strip()]
    gates = [r["values"]["gate"] for r in thermal if r["kind"] == "align_thermal_gate" and "gate" in r["values"]]
    g0 = [g for g in gates if g["kind"] == "G0"]
    g0 = g0[0] if len(g0) == 1 else None
    # rule 5, recomputed: > 0.5 core of outside load sustained 60 s (RL-72 E2, os_load_verdict)
    run = longest = 0
    for v in load["cpu_busy_cores"]:
        run = run + 1 if v > 0.5 else 0
        longest = max(longest, run)
    t = load["cpu_busy_t_s"]
    load_gap = max(b - a for a, b in zip(t, t[1:]))
    load_fired = longest >= 60
    contaminated = [a for a in lr["attempts"] if a["contaminated"]]
    # OS level / PM state over the turn, from the thermal journal
    in_turn = [r for r in thermal if r["kind"] == "reading"
               and res["turn_start_ns"] <= r["started"]["monotonic_ns"] <= res["turn_end_ns"]]
    levels = [r["values"]["status"].get("os_level") for r in in_turn if type(r["values"]["status"].get("os_level")) is int]
    states = [r["values"]["status"].get("pm_state") for r in in_turn if isinstance(r["values"]["status"].get("pm_state"), str)]
    cov = [r for r in thermal if r["kind"] == "session_end"][0]["values"]["coverage"]["all_keys"]
    st = stage_end[f"{leg_id}.a1"]
    wall_stage = st["ended_epoch_s"] - st["started_epoch_s"]
    mode = res["ac_powermode"]["value"] if isinstance(res["ac_powermode"], dict) else res["ac_powermode"]
    r1 = res["decode_tokens"] is not None and res["decode_tokens"] >= res["decode_cap"] and res["leg_status"] == "complete"
    r2 = g0 is not None and g0["outcome"] == "released"
    r5 = not contaminated and not load_fired
    r6 = mode == 0
    release_to_turn_s = (res["turn_start_ns"] - g0["end_ns"]) / NS if g0 else None
    rows.append({
        "leg_id": leg_id, "seed": lr["spec"]["seed"], "start_band": lr["spec"]["start_band"],
        "attempts": len(lr["attempts"]), "receipt_attempts": len(next(l for l in rec["legs"] if l["leg_id"] == leg_id)["attempts"]),
        "redo": [a.get("redo_reason") for a in lr["attempts"] if a.get("redone")],
        "contaminated_redos": len(contaminated),
        "g0_outcome_journal": g0 and g0["outcome"], "g0_s_journal": g0 and g0["duration_s"],
        "g0_s_record": res["g0_wait_s"], "g0_timeout_s": res["g0_timeout_s"],
        "band_reached": bool(r2 and res["quiet_s"] == 0 and release_to_turn_s is not None and 0 <= release_to_turn_s < 5),
        "release_to_turn_s": release_to_turn_s,
        "decode_tokens": res["decode_tokens"], "decode_cap": res["decode_cap"], "leg_status": res["leg_status"],
        "member_status": res["member_status"], "incomplete_reasons": res["incomplete_reasons"],
        "decode_closed": r1,
        "wall_s_stage": wall_stage, "wall_s_attempt": lr["attempts"][-1]["wall_s"], "budget_s": budgets[leg_id]["budget_s"],
        "over_time": wall_stage > rules["leg_time_factor"] * budgets[leg_id]["budget_s"],
        "ac_powermode": mode, "os_level_max_turn": max(levels) if levels else None,
        "pm_nominal_turn": (all(s == "Nominal" for s in states) if states else None),
        "load_samples": len(load["cpu_busy_cores"]), "load_max_gap_s": load_gap,
        "load_max_cores": max(load["cpu_busy_cores"]), "load_longest_run_over_0p5_s": longest,
        "thermal_coverage": cov,
        "rules": {"1_ran_to_cap": r1, "2_g0_released": r2, "3_sidecar": "at look (R9 note)",
                  "4_km003c": "at look (R9 note); meter present/0 bad/0 usb", "5_not_contaminated": r5,
                  "6_power_mode_0": r6},
    })
    rows[-1]["included"] = r1 and r2 and r5 and r6
    rows[-1]["excluded_by"] = [k for k, v in rows[-1]["rules"].items() if v is False]

# span level
res_doc = rec["span_result"]
meter = rec["meter"]
feeds = {k: v["stop"]["proven_stopped"] for k, v in rec["feeds"].items()}
stops = []
if not (res_doc["chain_exit_code"] == 0 and res_doc["chain_outcome"] == "COMPLETE" and res_doc["outcome"] == "MEASURED_OK"):
    stops.append("REFUSAL")
if res_doc["fault"] or not meter["present"] or not meter["proven_stopped"] or meter["bad_polls"] or meter["usb_errors"] \
        or not all(feeds.values()):
    stops.append("INSTRUMENT_FAULT")
if sum(r["contaminated_redos"] for r in rows) >= rules["contaminated_redos_max"]:
    stops.append("CONTAMINATED_REDOS")
if sum(r["over_time"] for r in rows) >= 2:
    stops.append("LEG_OVERTIME")
if not (steps["restore"]["rc"] == 0 and steps["restore"]["result"]["ok"] and steps["restore"]["result"]["observed"] == 0):
    stops.append("RESTORE_UNPROVEN")
agent_hits = [c for c in censuses if c["exit_code"] != 1 or c["stdout"].strip() or c["refusal"]]
cts = [c["monotonic_ns"] for c in censuses]
span = {
    "rc": rec["rc"], "mock": rec["mock"], "span_result": res_doc, "meter": meter, "feeds_proven_stopped": feeds,
    "steps_nonzero": [s["name"] for s in rec["steps"] if s["rc"] != 0], "n_steps": len(rec["steps"]),
    "soak_rc": steps["soak"]["rc"], "soak_s": steps["soak"]["ended"]["epoch_s"] - steps["soak"]["started"]["epoch_s"],
    "restore": steps["restore"]["result"], "read_power": steps["read_power"]["result"],
    "close_steps": {n: steps[n]["rc"] for n in ("restore", "stop-volumes", "stop-meter", "stop-agents", "close-volumes")},
    "stages_end_rc_nonzero": [s["stage_id"] for s in stages if s["event"] == "end" and s["rc"] != 0],
    "stages_unclosed": sorted({s["stage_id"] for s in stages if s["event"] == "start"} - set(stage_end)),
    "agent_census": {"polls": len(censuses), "argv": censuses[0]["argv"], "hits": len(agent_hits),
                     "max_gap_s": max(b - a for a, b in zip(cts, cts[1:])) / NS,
                     "first_after_start_s": (cts[0] - rec["started"]["monotonic_ns"]) / NS,
                     "last_before_end_s": (rec["ended"]["monotonic_ns"] - cts[-1]) / NS},
    "volume_census": [(v["verdict"], v["reasons"], v["external"]) for v in vols],
    "deadlines_files": sorted(str(p.relative_to(root)) for p in root.rglob("deadlines/**/*") if p.is_file()),
    "load_redos_used": rec["load_redos_used"], "legs_finished": rec["legs_finished"], "legs_planned": rec["legs_planned"],
    "batch_windows": rec["batch_windows"], "stops_by_hand": stops,
}
# compare with the automatic desk
ds = json.loads((auto / "desk_summary.json").read_text())
astops = json.loads((auto / "stops.json").read_text())
diffs = []
for h, a in zip(rows, ds["legs"]):
    pairs = {"leg_id": (h["leg_id"], a["leg_id"]), "start_band": (h["start_band"], a["start_band"]),
             "band_reached": (h["band_reached"], a["band_reached"]), "g0_outcome": (h["g0_outcome_journal"], a["g0_outcome"]),
             "g0_s": (round(h["g0_s_journal"], 6), round(a["g0_s"], 6)), "attempts": (h["attempts"], a["attempts"]),
             "contaminated_redos": (h["contaminated_redos"], a["contaminated_redos"]),
             "redo_reasons": (h["redo"], a["redo_reasons"]), "budget_s": (h["budget_s"], a["budget_s"]),
             "wall_s(stage vs summary)": (round(h["wall_s_stage"], 1), round(a["wall_s"], 1)),
             "os_level_max": (h["os_level_max_turn"], a["os_level_max"]), "pm_nominal": (h["pm_nominal_turn"], a["pm_nominal"]),
             "included/admitted": (h["included"], a["admitted"])}
    for k, (x, y) in pairs.items():
        if x != y:
            diffs.append(f"{h['leg_id']} {k}: hand={x!r} desk={y!r}")
    h["compare"] = {k: {"hand": x, "desk": y, "agree": x == y} for k, (x, y) in pairs.items()}
if len(rows) != len(ds["legs"]):
    diffs.append(f"leg count: hand={len(rows)} desk={len(ds['legs'])}")
if sorted(stops) != sorted(s["code"] for s in astops):
    diffs.append(f"stops: hand={stops} desk={[s['code'] for s in astops]}")
if ds["result"] != res_doc:
    diffs.append(f"result: hand={res_doc} desk={ds['result']}")
if {k: ds["meter"].get(k) for k in meter} != meter:
    diffs.append(f"meter: hand={meter} desk={ds['meter']}")
if ds["feeds_proven_stopped"] != all(feeds.values()):
    diffs.append("feeds_proven_stopped differs")
out = {"legs": rows, "span": span, "diffs": diffs, "desk_stops": astops}
out_json.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps({"diffs": diffs, "stops_by_hand": stops, "included": [(r["leg_id"], r["included"], r["excluded_by"]) for r in rows]}))
