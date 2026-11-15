"""Hand table for hp-01-s02 (cq-hp-01-s02-a1, L004-L007, High Power), built from raw records WITHOUT joulewise.cadence.desk.

The hp-01 smoke desk's hand_table.py (desk-cq-hp-01-s01-a1, e7859778) used verbatim; it iterates the receipt roster.
Earlier header (hp-01-s01):

Hand table for the hp-01 High Power smoke hp-01-s01 (L001-L003), built from raw records WITHOUT joulewise.cadence.desk.

This is the s04 desk's hand_table.py (desk-cq-dev-01-s04-a1, c9fc0339d) with three High Power changes:
  * rule 6 means the kit's block mode (kit power_mode = 2, High Power; item 334 "Counted", design doc 13.2.1):
    the leg record's ac_powermode at episode start must equal it, its pre-attempt `L00n.aK-powermode` step must
    read that mode with this span's marker, and the leg must not be in the receipt's high_power.revoked;
  * RESTORE_UNPROVEN by hand: span/result.json restore_proven true AND receipt span_result restore_proven true AND
    high_power.close_proof {proven true, ac_powermode 0, host_marker_present false, pmset_error null} AND
    high_power.restore.ok AND the power_proof step proven (the receipt's restore step carries no `observed`);
  * D1/D5: admitted is compared with each leg_summary.json (via desk_summary), revoked legs are listed.
Earlier header (s04):

The pilot's hand_table.py (pilot-desk-cq-dev-01-s01-a1, used verbatim for s03), adapted for a span with a
load redo:
  * every attempt is read (legs/<L>/<attempt output_dir>/load_journal.json, from leg_record.attempts),
    and rule 5 (> 0.5 core sustained 60 s, RL-72 E2; os_load_verdict) is recomputed per attempt;
  * a leg passes rule 5 when its counted (last) attempt is clean by hand and every earlier attempt was
    recorded contaminated AND fires by hand (a correct redo), within the span's redo quota;
  * the leg's wall time and stage come from its last attempt (`<L>.a<n>`), as the desk's leg_summary does;
  * the thermal journal is the counted attempt's (result.bundle under the counted output_dir).
The rest is the pilot's logic unchanged.

Opens only: runner_receipt.json, span_plan.json, chain-stages.jsonl, censuses.jsonl, volume_censuses.jsonl,
legs/*/leg_record.json, legs/*/{runtime,runtime.rejected<N>}/load_journal.json (outside-load journal; keys
checked: no energy/power key), each counted attempt's outputs/align_thermal.jsonl, the kit (stop_rules only).
Then compares with the automatic desk's desk_summary.json and stops.json.
Usage: python3 -I -B hand_table.py OUT AUTO_DIR OUT_JSON KIT
"""
import json
import sys
from pathlib import Path

root, auto, out_json = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
NS = 10**9
LIMIT_CORES, SUSTAINED_S, MAX_GAP_S, MIN_RATE, SLACK_S = 0.5, 60, 5.0, 0.9, 5  # RL-72 E2 / os_load_verdict
rec = json.loads((root / "runner_receipt.json").read_text())
plan = json.loads((root / "span_plan.json").read_text())
stages = [json.loads(l) for l in (root / "chain-stages.jsonl").read_text().splitlines() if l.strip()]
censuses = [json.loads(l) for l in (root / "censuses.jsonl").read_text().splitlines() if l.strip()]
vols = [json.loads(l) for l in (root / "volume_censuses.jsonl").read_text().splitlines() if l.strip()]
steps = {s["name"]: s for s in rec["steps"]}
stage_end = {s["stage_id"]: s for s in stages if s["event"] == "end"}
budgets = {l["leg_id"]: l for l in plan["legs"]}
kit = json.loads(Path(sys.argv[4]).read_text())
rules = kit["stop_rules"]
redo_quota = kit["span_template"]["redo_quota"]
BLOCK_MODE = kit["power_mode"]   # 2 = High Power for cl-hp-01
HP = rec["high_power"]
REVOKED = {e["leg_id"] for e in (HP.get("revoked") or [])}
span_result_file = json.loads((root / "desk-bundle" / "span" / "result.json").read_text())


def load_check(path, wall_s):
    load = json.loads(path.read_text())
    run = longest = 0
    for v in load["cpu_busy_cores"]:
        run = run + 1 if v > LIMIT_CORES else 0
        longest = max(longest, run)
    t = load["cpu_busy_t_s"]
    gaps = [b - a for a, b in zip(t, t[1:])]
    need = MIN_RATE * wall_s - SLACK_S
    return {"samples": len(load["cpu_busy_cores"]), "required_samples": round(need, 1),
            "coverage_ok": len(load["cpu_busy_cores"]) >= need and len(t) == len(load["cpu_busy_cores"])
            and all(g >= 0 for g in gaps) and max(gaps) <= MAX_GAP_S,
            "max_gap_s": max(gaps), "max_cores": max(load["cpu_busy_cores"]),
            "longest_run_over_0p5_s": longest, "fires": longest >= SUSTAINED_S,
            "census_present": bool(load.get("census"))}


rows = []
for leg_id in rec["roster"]:
    lr = json.loads((root / "legs" / leg_id / "leg_record.json").read_text())
    res = lr["result"]
    atts = []
    for a in lr["attempts"]:
        lc = load_check(root / a["output_dir"] / "load_journal.json", a["wall_s"])
        st = stage_end[f"{leg_id}.a{a['attempt']}"]
        atts.append({"attempt": a["attempt"], "output_dir": a["output_dir"], "stage_rc": st["rc"],
                     "started_epoch_s": a["started_epoch_s"], "ended_epoch_s": a["ended_epoch_s"],
                     "stage_wall_s": st["ended_epoch_s"] - st["started_epoch_s"], "record_wall_s": a["wall_s"],
                     "recorded": {"contaminated": a["contaminated"], "redone": a.get("redone"),
                                  "redo_reason": a.get("redo_reason"), "os_load": a.get("os_load")},
                     "hand_load": lc,
                     "hand_agrees_with_record": lc["fires"] == a["contaminated"]
                     and a["os_load"]["seconds"] == lc["samples"]
                     and abs(a["os_load"]["max_busy_cores"] - lc["max_cores"]) < 1e-9})
    counted, earlier = atts[-1], atts[:-1]
    counted_dir = root / counted["output_dir"]
    thermal = [json.loads(l) for l in (counted_dir / res["bundle"] / "outputs" /
                                        "align_thermal.jsonl").read_text().splitlines() if l.strip()]
    gates = [r["values"]["gate"] for r in thermal if r["kind"] == "align_thermal_gate" and "gate" in r["values"]]
    g0 = [g for g in gates if g["kind"] == "G0"]
    g0 = g0[0] if len(g0) == 1 else None
    contaminated = [a for a in lr["attempts"] if a["contaminated"]]
    in_turn = [r for r in thermal if r["kind"] == "reading"
               and res["turn_start_ns"] <= r["started"]["monotonic_ns"] <= res["turn_end_ns"]]
    levels = [r["values"]["status"].get("os_level") for r in in_turn if type(r["values"]["status"].get("os_level")) is int]
    states = [r["values"]["status"].get("pm_state") for r in in_turn if isinstance(r["values"]["status"].get("pm_state"), str)]
    cov = [r for r in thermal if r["kind"] == "session_end"][0]["values"]["coverage"]["all_keys"]
    wall_stage = counted["stage_wall_s"]
    mode = res["ac_powermode"]["value"] if isinstance(res["ac_powermode"], dict) else res["ac_powermode"]
    pm_steps = [s for s in rec["steps"] if s["name"] == f"{leg_id}.a{len(lr['attempts'])}-powermode"]
    pm_step = pm_steps[0]["result"] if len(pm_steps) == 1 else None
    pm_step_ok = bool(pm_step and pm_steps[0]["rc"] == 0 and pm_step.get("ac_powermode") == BLOCK_MODE
                      and pm_step.get("marker_is_this_spans") is True and pm_step.get("pmset_error") is None)
    revoked_leg = leg_id in REVOKED
    r1 = res["decode_tokens"] is not None and res["decode_tokens"] >= res["decode_cap"] and res["leg_status"] == "complete"
    r2 = g0 is not None and g0["outcome"] == "released"
    # rule 5 with a redo: counted attempt clean by hand and by record; every earlier attempt contaminated by
    # record AND firing by hand (the redo was owed); every journal covers its attempt
    r5 = (not counted["hand_load"]["fires"] and not counted["recorded"]["contaminated"]
          and all(a["hand_load"]["fires"] and a["recorded"]["contaminated"] and a["recorded"]["redone"] for a in earlier)
          and all(a["hand_load"]["coverage_ok"] for a in atts))
    r6 = mode == BLOCK_MODE and pm_step_ok and not revoked_leg
    release_to_turn_s = (res["turn_start_ns"] - g0["end_ns"]) / NS if g0 else None
    rows.append({
        "leg_id": leg_id, "seed": lr["spec"]["seed"], "start_band": lr["spec"]["start_band"],
        "attempts": len(lr["attempts"]), "receipt_attempts": len(next(l for l in rec["legs"] if l["leg_id"] == leg_id)["attempts"]),
        "attempt_detail": atts,
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
        "ac_powermode": mode, "powermode_step": pm_step, "revoked": revoked_leg, "os_level_max_turn": max(levels) if levels else None,
        "pm_nominal_turn": (all(s == "Nominal" for s in states) if states else None),
        "load_counted": counted["hand_load"],
        "thermal_coverage": cov,
        "rules": {"1_ran_to_cap": r1, "2_g0_released": r2, "3_sidecar": "at look (R9 note)",
                  "4_km003c": "at look (R9 note); meter present/0 bad/0 usb", "5_not_contaminated": r5,
                  "6_block_power_mode_2_high_power": r6},
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
cp = HP.get("close_proof") or {}
restore_proven_hand = (span_result_file.get("restore_proven") is True and res_doc.get("restore_proven") is True
    and cp.get("proven") is True and cp.get("ac_powermode") == 0 and cp.get("host_marker_present") is False
    and cp.get("pmset_error") is None and (HP.get("restore") or {}).get("ok") is True
    and steps["restore"]["rc"] == 0 and steps["restore"]["result"]["ok"] is True
    and steps["power_proof"]["rc"] == 0 and steps["power_proof"]["result"]["proven"] is True
    and steps["power_proof"]["result"]["ac_powermode"] == 0 and steps["power_proof"]["result"]["host_marker_present"] is False)
if not restore_proven_hand:
    stops.append("RESTORE_UNPROVEN")
agent_hits = [c for c in censuses if c["exit_code"] != 1 or c["stdout"].strip() or c["refusal"]]
cts = [c["monotonic_ns"] for c in censuses]
span = {
    "rc": rec["rc"], "mock": rec["mock"], "kit": rec["kit"], "batch_windows_receipt": rec["batch_windows"], "span_result": res_doc, "meter": meter, "feeds_proven_stopped": feeds,
    "steps_nonzero": [s["name"] for s in rec["steps"] if s["rc"] != 0], "n_steps": len(rec["steps"]),
    "step_names": [s["name"] for s in rec["steps"]],
    "soak_rc": steps["soak"]["rc"], "soak_s": steps["soak"]["ended"]["epoch_s"] - steps["soak"]["started"]["epoch_s"],
    "restore": steps["restore"]["result"], "read_power": steps["read_power"]["result"],
    "power_proof": steps["power_proof"]["result"], "power_last_look": steps["power_last_look"]["result"],
    "high_power_step": steps["high_power"]["result"], "host_lock_release": steps["host_lock_release"]["result"],
    "high_power": {k: HP.get(k) for k in ("block_power_mode", "revoked", "before_restore", "restore", "close_proof", "host_marker")},
    "span_result_file": span_result_file, "restore_proven_hand": restore_proven_hand,
    "close_steps": {n: steps[n]["rc"] for n in ("power_last_look", "restore", "power_proof", "host_lock_release", "stop-volumes", "stop-meter", "stop-agents", "close-volumes")},
    "stages_end_rc_nonzero": [s["stage_id"] for s in stages if s["event"] == "end" and s["rc"] != 0],
    "stages_unclosed": sorted({s["stage_id"] for s in stages if s["event"] == "start"} - set(stage_end)),
    "agent_census": {"polls": len(censuses), "argv": censuses[0]["argv"], "hits": len(agent_hits),
                     "max_gap_s": max(b - a for a, b in zip(cts, cts[1:])) / NS,
                     "first_after_start_s": (cts[0] - rec["started"]["monotonic_ns"]) / NS,
                     "last_before_end_s": (rec["ended"]["monotonic_ns"] - cts[-1]) / NS},
    "volume_census": [(v["verdict"], v["reasons"], v["external"]) for v in vols],
    "deadlines_files": sorted(str(p.relative_to(root)) for p in root.rglob("deadlines/**/*") if p.is_file()),
    "load_redos_used": rec["load_redos_used"], "redo_quota_kit": redo_quota,
    "redos_by_hand": sum(len(r["redo"]) for r in rows),
    "legs_finished": rec["legs_finished"], "legs_planned": rec["legs_planned"],
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
if ds["result"] != res_doc or span_result_file != res_doc:
    diffs.append(f"result: hand={res_doc} desk={ds['result']}")
if {k: ds["meter"].get(k) for k in meter} != meter:
    diffs.append(f"meter: hand={meter} desk={ds['meter']}")
if ds["feeds_proven_stopped"] != all(feeds.values()):
    diffs.append("feeds_proven_stopped differs")
out = {"legs": rows, "span": span, "diffs": diffs, "desk_stops": astops}
out_json.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps({"diffs": diffs, "stops_by_hand": stops,
                  "included": [(r["leg_id"], r["included"], r["excluded_by"]) for r in rows]}))
