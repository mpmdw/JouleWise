"""Assemble RESULT.json for desk-cq-hp-01-s02-a1 from hand/ outputs (and receipt stamps/step results)."""
import json, sys, ast
from pathlib import Path
T, D = Path(sys.argv[1]), Path(sys.argv[2])
H = T / "hand"
ht = json.loads((H / "hand_table.json").read_text())
ds = json.loads((T / "auto" / "desk_summary.json").read_text())
rec = json.loads((D / "runner_receipt.json").read_text())
steps = {s["name"]: s for s in rec["steps"]}
kit = json.loads((T / "kit.json").read_text())
span = ht["span"]
def lines(name):
    out = {}
    for l in (H / name).read_text().splitlines():
        k, _, v = l.partition(" ")
        out[k] = v
    return out
r1 = {}
for l in (H / "r1print.out").read_text().splitlines():
    if l.startswith("soak_reference"):
        r1["soak_reference_line"] = l
    else:
        k, _, v = l.partition(" "); r1[k] = json.loads(v)
smp = {k: json.loads(v) for k, v in lines("sampler.out").items()}
osl = {k: json.loads(v) for k, v in lines("oslevel.out").items()}
rl157 = json.loads((H / "rl157_s1.out").read_text().split(" ", 2)[2])
legs = ht["legs"]
budget = legs[0]["budget_s"]; factor = kit["stop_rules"]["leg_time_factor"]
# rule 6, second half: the NEXT observation after each leg reads 2 with this span's marker
roster = rec["roster"]
nxt = {}
for i, L in enumerate(roster):
    if i + 1 < len(roster):
        s = [x for x in rec["steps"] if x["name"] == f"{roster[i+1]}.a1-powermode"][0]; name = s["name"]
    else:
        s = steps["power_last_look"]; name = "power_last_look"
    r = s["result"]
    nxt[L] = {"step": name, "rc": s["rc"], "ac_powermode": r.get("ac_powermode"),
              "marker_is_this_spans": r.get("marker_is_this_spans"), "pmset_error": r.get("pmset_error"),
              "holds": s["rc"] == 0 and r.get("ac_powermode") == 2 and r.get("marker_is_this_spans") is True and r.get("pmset_error") is None}
ncomp = sum(len(l["compare"]) for l in legs)
hand_legs = []
for l in legs:
    hand_legs.append({"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
        "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
        "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"], "pre_attempt_powermode_step": l["powermode_step"],
        "next_observation_powermode": nxt[l["leg_id"]], "revoked": l["revoked"],
        "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": l["load_counted"]["max_cores"],
        "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"]})
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
st, en = rec["started"]["epoch_s"], rec["ended"]["epoch_s"]
out = {
 "plan_id": "cq-hp-01-s02-a1", "span": "hp-01-s02", "legs": roster,
 "built": "2026-11-15 07:20-07:25 PST on the Air (desk builder for the lead)",
 "work_order": "RUN_STATE 338 (issued 04:58:30 PST); magistrate Check RUN_STATE 340 (ad4b32be, 07:16 PST, origin/main)",
 "data": f"{D} (read-only copy; sha256 -c of all 158 manifest entries OK; .air and .mbp manifests byte-equal, sha256 02d997efd17bc9bc80c2480dafa5a194c8c7ac484dcabd916c757e4f68a048ba)",
 "code": "dd206025abb30fd5c07515cd4b34b3e653174810 (/Volumes/JW-EXT/jw-wt/hp01-ready-dd2, detached, clean before and after, read-only)",
 "kit": {"source": "git show bbd34dc876001786c3603d9c4583391639284253:docs/process/cadence/kits/cl-hp-01.json",
         "sha256": "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965", "sha_asserted": True, "power_mode": kit["power_mode"]},
 "desk_command": "python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-hp-01-s02-a1 --input <OUT>/desk-bundle --out auto --kit kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter, per D6). auto/ = the 07:20 run; auto-rerun/ = this builder's 07:21 re-run: desk_summary.json and stops.json identical, JOURNAL-TABLE.md differs only in its build-time line",
 "D6_span_result_json_exists": (D / "desk-bundle" / "span" / "result.json").is_file(),
 "desk_stops_json": json.loads((T / "auto" / "stops.json").read_text()),
 "desk_block_mode_line": "Block AC powermode 2 (JOURNAL-TABLE.md)",
 "comparison": {
  "per_leg_values_compared": ncomp, "per_leg_values_differing": sum(1 for l in legs for c in l["compare"].values() if not c["agree"]),
  "fields_per_leg": sorted(legs[0]["compare"]), "inclusion_included": True,
  "span_level_compared": ["leg count", "named stops (hand [] vs desk [])", "result (desk_summary vs receipt span_result vs span/result.json)", "meter", "feeds_proven_stopped"],
  "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
  "scope_notes": ["the desk table has no admitted column (dev-01 F8): admitted read from desk_summary.json, i.e. each leg_summary.json (D1)",
                  "hand 'reached' derives from G0 released + quiet_s 0 + release-to-turn < 5 s (" + " / ".join(f'{l["release_to_turn_s"]:.3f}' for l in legs) + " s); same result",
                  "L004 os_level_max 2 / pm_nominal false agrees by hand (turn readings: os_level 0 x373, 1 x29, 2 x36; pm_state Nominal 373, Moderate 29, Heavy 36; non-Nominal from 312.9 s to 376.9 s after turn start); L005-L007 0/Nominal throughout. Not a rule: kit inclusion 'no_drop_by_outcome' (no leg is dropped for its OS level or state)",
                  "rules 3 and 4 left to the look (meter present, 35,459 polls, 0 bad, 0 usb, proven stopped)",
                  "the desk omits restore lines and censuses; the hand table carries them clean"]},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL", "meaning": "automatic desk = independent hand table on every value, inclusion included",
                "basis": f"0 of {ncomp} per-leg and 0 of 5 span-level values differ; 4 of 4 included by hand, 4 of 4 admitted by desk; stops.json [] and hand stops []",
                "R9": "not applicable (remainder span, not the smoke)"},
 "rules_by_hand": {"1_ran_to_cap": "4/4 (decode 4,096/4,096 each, leg_status complete, member succeeded, stage rc 0)",
                   "2_g0_released": "4/4 (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + "; journal G0 = record g0_wait_s)",
                   "5_not_contaminated": "4/4 (one attempt each, no redo; longest run over 0.5 core " + "/".join(str(l["load_counted"]["longest_run_over_0p5_s"]) for l in legs) + " s of 60; journals cover their attempts; hand agrees with recorded os_load)",
                   "6_high_power": "4/4 (leg_record ac_powermode 2 at episode start; own pre-attempt L00n.a1-powermode step rc 0 reads 2 with this span's marker; next observation (next leg's powermode step, or power_last_look after L007) reads 2 with this span's marker; high_power.revoked null)",
                   "3_4": "at the look; meter present, 35,459 polls, 0 bad, 0 usb, proven stopped"},
 "restore_proven": {"span_result_json": ht["span"]["span_result_file"]["restore_proven"], "receipt_span_result": span["span_result"]["restore_proven"], "hand": span["restore_proven_hand"]},
 "close_proof": span["high_power"]["close_proof"], "restore": span["high_power"]["restore"],
 "power_proof_step": span["power_proof"], "power_last_look_step": span["power_last_look"], "read_power_step_before_soak": span["read_power"],
 "high_power_step": span["high_power_step"], "host_lock_release": span["host_lock_release"], "close_steps_rc": span["close_steps"],
 "high_power": {"revoked": span["high_power"]["revoked"], "before_restore": span["high_power"]["before_restore"], "block_power_mode": span["high_power"]["block_power_mode"]},
 "D1": "admitted from each leg_summary true x4; high_power.revoked null; before_restore {ac_powermode 2, marker present, marker_is_this_spans true, pmset_error null}. D1 second line: no revoked entry, so nothing holds the next span on D1.",
 "D5": "not engaged: no SIGKILL (receipt rc 0, power_last_look rc 0 read mode 2 with this span's marker after L007, revoked null); every admitted:true is backed by a later observation.",
 "LEG_OVERTIME": "no",
 "LEG_OVERTIME_detail": f"walls {', '.join(str(w) for _, w, _ in walls)} s against {factor} x {budget:,} = {factor*budget:,} s; max ratio {max(r for *_, r in walls)} (none over budget_s); 0 legs over, stop needs 2",
 "RL157_s1": rl157,
 "RL157_s5": [{"leg": l, "g0_s": round(next(x for x in legs if x["leg_id"] == l)["g0_s_journal"], 1), "wall_s": w, "budget_s": budget, "wall_over_budget": r} for l, w, r in walls],
 "RL150_R1_part3_print": r1,
 "RL150_R1_note": "TV0h = TV1h in every reading (soak, own references, G0 releases), so nothing routes under RL-149 §5 item 6",
 "RL156a": {"starvation": "none",
   "thermal_sampler": {k: {"cells": v["cells"], "reads": v["reads"], "read_errors": v["read_errors"], "cells_with_no_reading_at_all": v["cells_with_no_reading_at_all"],
                           "max_interval_s": v["max_interval_s"], "empty_cells_on_100ms_tolerance": v["empty_cells_tol"], "cov_reported": v["cov_reported"]} for k, v in smp.items()},
   "thermal_note": "every 1-s cell holds a reading; 0 read errors; max intervals " + "/".join(str(v["max_interval_s"]) for v in smp.values()) + " s. Off-grid cells (103-177 ms from the grid, tolerance 100 ms): L004 1 pre-G0 + 3 post-turn, L005 2 post-turn, L006 1 post-turn, L007 2 post-turn; none in G0 or the turn. Jitter, not starvation.",
   "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
   "inventory": "no gap and not exercised: the cadence-leg kind never calls start_inventory at dd206025a (only r1_runtime k_step_30b and k_step_d do; read for the smoke desk); no inventory journal in OUT (find -iname '*inventory*' empty)"},
 "os_level_census": osl,
 "maintenance_overlap": "MAINTENANCE-OVERLAP.md (print only): dasd steady in every phase (3,215-3,627 per leg); no XProtect, no mdworker, no mds in any leg (mds 6 in the 05:00 bucket, pre-soak/soak); softwareupdated 8 in L005's pre-G0; backupd 6-48 per leg; mobileassetd 165 in L006's TURN (06:40:03-06:47:22) + 8 in L006 post-turn (the magistrate's '173 in the 06:40 bucket (L006 end, L007 start)' is L006's turn, not L007), 3-4 elsewhere; rule 5 clean on all four (longest run over 0.5 core 2/1/2/4 s; L006 max 1.373 cores)",
 "span_level": {k: span[k] for k in ("rc", "mock", "kit", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": st, "receipt_ended_epoch_s": en, "runner_span_s": round(en - st, 1),
                        "smoke_desk_estimate_s02_s": 7092, "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / 4, 1)},
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "LEG_OVERTIME": out["LEG_OVERTIME_detail"], "rl157": rl157, "time": out["time_calendar_only"], "nxt": nxt}, indent=1))
