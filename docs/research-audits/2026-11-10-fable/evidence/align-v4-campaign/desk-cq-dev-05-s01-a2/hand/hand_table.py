"""Hand table for dev-05 cq-dev-05-s01-a2 (L001-L006, kit cl-dev-05.v1.1), copied from desk-cq-dev-04-s01-a1
(itself desk-cq-dev-03-s02-a1's, comparison code unchanged). Comparison code and rule thresholds unchanged.
Receipt roster determines legs; kit shape and first-leg rule determine roles (L001 captures this span reference).
Every attempt is checked, including runtime.rejected<N> (s01: L004.a1, the cpu_load redo).
Opens only the key-scanned paths logged in OPENED.txt; no joulewise.cadence.desk import.
Usage: python3.13 -I -B hand_table.py DATA AUTO_DIR OUT_JSON KIT
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
    wp = counted_dir / res["bundle"] / "outputs" / "align_window_reference.json"  # a consumer leg writes none (v1.1)
    wref = json.loads(wp.read_text()) if wp.is_file() else {"status": "absent (consumer)", "source": {"run_id": None}, "record_sha256": None, "fast_c": None, "span_ns": None}
    in_turn = [r for r in thermal if r["kind"] == "reading"
               and res["turn_start_ns"] <= r["started"]["monotonic_ns"] <= res["turn_end_ns"]]
    levels = [r["values"]["status"].get("os_level") for r in in_turn if type(r["values"]["status"].get("os_level")) is int]
    states = [r["values"]["status"].get("pm_state") for r in in_turn if isinstance(r["values"]["status"].get("pm_state"), str)]
    cov = [r for r in thermal if r["kind"] == "session_end"][0]["values"]["coverage"]["all_keys"]
    wall_stage = counted["stage_wall_s"]
    mode = res["ac_powermode"]["value"] if isinstance(res["ac_powermode"], dict) else res["ac_powermode"]
    r1 = res["decode_tokens"] is not None and res["decode_tokens"] >= res["decode_cap"] and res["leg_status"] == "complete"
    r2 = g0 is not None and g0["outcome"] == "released"
    # rule 5 with a redo: counted attempt clean by hand and by record; every earlier attempt contaminated by
    # record AND firing by hand (the redo was owed); every journal covers its attempt
    r5 = (not counted["hand_load"]["fires"] and not counted["recorded"]["contaminated"]
          and all(a["hand_load"]["fires"] and a["recorded"]["contaminated"] and a["recorded"]["redone"] for a in earlier)
          and all(a["hand_load"]["coverage_ok"] for a in atts))
    r6 = mode == 0
    release_to_turn_s = (res["turn_start_ns"] - g0["end_ns"]) / NS if g0 else None
    rows.append({
        "leg_id": leg_id, "seed": lr["spec"]["seed"], "start_band": lr["spec"]["start_band"],
        "attempts": len(lr["attempts"]), "receipt_attempts": len(next(l for l in rec["legs"] if l["leg_id"] == leg_id)["attempts"]),
        "attempt_detail": atts,
        # v1.1 (kit cl-dev-05.v1.1): hand-derived from leg_record result/spec, the G0 gate row and the window reference
        "prefill_tokens": res["prefill_tokens"], "prefill_tokens_nominal_spec": lr["spec"]["prefill_tokens"],
        "g0_shape_spec": lr["spec"].get("g0_shape"), "g0_role_record": res.get("g0_role"), "g0_shape_record": res.get("g0_shape"),
        "g0_reference_source_record": res.get("g0_reference_source"),
        "g0_reference_record_sha256_record": res.get("g0_reference_record_sha256"),
        "g0_row_reference_source": (g0 or {}).get("reference", {}).get("source_member"),
        "g0_row_reference_fast_c": (g0 or {}).get("reference", {}).get("fast_c"),
        "g0_row_reference_span_ns": (g0 or {}).get("reference", {}).get("span_ns"),
        "own_window_reference": {"status": wref["status"], "source_run_id": wref["source"]["run_id"], "record_sha256": wref["record_sha256"],
                                 "fast_c": wref["fast_c"], "span_ns": wref["span_ns"]},
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
        "load_counted": counted["hand_load"],
        "thermal_coverage": cov,
        "rules": {"1_ran_to_cap": r1, "2_g0_released": r2, "3_sidecar": "at look (R9 note)",
                  "4_km003c": "at look (R9 note); meter present/0 bad/0 usb", "5_not_contaminated": r5,
                  "6_power_mode_0": r6},
    })
    rows[-1]["included"] = r1 and r2 and r5 and r6
    rows[-1]["excluded_by"] = [k for k, v in rows[-1]["rules"].items() if v is False]

# v1.1 span reference by hand: the span's first leg's accepted (last) attempt, in roster order
first = rows[0]
for r in rows:
    kl = next(x for x in kit["legs"] if x["leg_id"] == r["leg_id"])
    r["g0_shape_kit"] = kl["g0_shape"]; r["prefill_tokens_nominal_kit"] = kl["prefill_tokens"]
    consumer = kl["g0_shape"] == "span" and r is not first  # v1.1: a span-shaped leg that is first in its span captures (L001 here)
    r["g0_role_hand"] = "consume" if consumer else "capture"
    r["g0_shape_hand"] = kl["g0_shape"]
    if consumer:
        src = r["g0_row_reference_source"]  # run id of the capture the G0 gate row judged against
        src_leg = next((x for x in rows if x["own_window_reference"]["source_run_id"] == src), None)
        r["span_reference_hand"] = None if src_leg is None else {
            "leg_id": src_leg["leg_id"], "attempt": src_leg["attempts"], "excluded": not src_leg["included"],
            "redone": src_leg["contaminated_redos"] > 0}
        r["consumer_checks"] = {
            "reference_is_first_leg": src_leg is first,
            "record_sha_equals_capture_record_sha": r["g0_reference_record_sha256_record"] == (src_leg or first)["own_window_reference"]["record_sha256"],
            "record_source_equals_row_source": r["g0_reference_source_record"] == src,
            "row_reference_fast_c_equals_capture_fast_c": r["g0_row_reference_fast_c"] == (src_leg or first)["own_window_reference"]["fast_c"],
            "row_reference_span_equals_capture_span": r["g0_row_reference_span_ns"] == (src_leg or first)["own_window_reference"]["span_ns"],
            "own_window_reference_status": r["own_window_reference"]["status"]}
    else:
        r["span_reference_hand"] = None
        r["capture_checks"] = {"own_window_reference_status": r["own_window_reference"]["status"],
                               "row_reference_source_is_self": r["g0_row_reference_source"] == r["own_window_reference"]["source_run_id"]}
    r["prefill_deviation_pct"] = round(100 * (r["prefill_tokens"] - r["prefill_tokens_nominal_kit"]) / r["prefill_tokens_nominal_kit"], 3)  # realized vs nominal (RL-158 Q5)
    r["rules"]["2_g0_released"] = r["rules"]["2_g0_released"] and (not consumer or all(
        v is True for k, v in r["consumer_checks"].items() if k != "own_window_reference_status"))
    r["included"] = r["rules"]["1_ran_to_cap"] and r["rules"]["2_g0_released"] and r["rules"]["5_not_contaminated"] and r["rules"]["6_power_mode_0"]
    r["excluded_by"] = [k for k, v in r["rules"].items() if v is False]

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
    "step_names": [s["name"] for s in rec["steps"]],
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
             "included/admitted": (h["included"], a["admitted"]),
             "g0_role": (h["g0_role_hand"], a["g0_role"]), "g0_shape": (h["g0_shape_hand"], a["g0_shape"]),
             "g0_role(record vs desk)": (h["g0_role_record"], a["g0_role"]),
             "prefill_tokens(nominal: kit/spec vs desk)": ((h["prefill_tokens_nominal_kit"] if h["prefill_tokens_nominal_kit"] == h["prefill_tokens_nominal_spec"] else None), a["prefill_tokens"]), "span_reference": (h["span_reference_hand"], a["span_reference"]),
             "seed": (h["seed"], a["seed"])}
    for k, (x, y) in pairs.items():
        if x != y:
            diffs.append(f"{h['leg_id']} {k}: hand={x!r} desk={y!r}")
    h["compare"] = {k: {"hand": x, "desk": y, "agree": x == y} for k, (x, y) in pairs.items()}
hand_ref = {"attempt": rows[0]["attempts"], "consistent": all(r["consumer_checks"]["reference_is_first_leg"] for r in rows if "consumer_checks" in r),
            "consumers": sum(r["g0_role_hand"] == "consume" for r in rows), "leg_id": rows[0]["leg_id"]}
if {k: ds["span_reference"].get(k) for k in hand_ref} != hand_ref:
    diffs.append(f"span_reference: hand={hand_ref} desk={ds['span_reference']}")
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
print(json.dumps({"diffs": diffs, "stops_by_hand": stops,
                  "included": [(r["leg_id"], r["included"], r["excluded_by"]) for r in rows]}))
