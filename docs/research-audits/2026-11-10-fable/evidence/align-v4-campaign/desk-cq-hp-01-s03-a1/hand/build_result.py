"""Assemble RESULT.json for desk-cq-hp-01-s03-a1 from hand/ outputs (and receipt stamps/step results).

The hp-01-s02 desk's build_result.py (desk-cq-hp-01-s02-a1, 37afda2a4) with s03 strings, notes computed from this
span's hand outputs instead of typed, and a block summary (hp-01 = s01 + s02 + s03, 12 legs) read from the s01 and s02
desks' committed hand_table.json / desk_summary.json / stops.json on audit/2026-11-10-fable (argv[3]).
Usage: python3 -I -B build_result.py DESK_DIR OUT EVIDENCE_ROOT
"""
import json, sys
from pathlib import Path
T, D, EV = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
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
ndiff = sum(1 for l in legs for c in l["compare"].values() if not c["agree"])
n = len(legs); n_incl = sum(l["included"] for l in legs); n_adm = sum(a["admitted"] for a in ds["legs"])
desk_stops = json.loads((T / "auto" / "stops.json").read_text())
hand_legs = []
for l in legs:
    hand_legs.append({"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
        "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
        "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"], "pre_attempt_powermode_step": l["powermode_step"],
        "next_observation_powermode": nxt[l["leg_id"]], "revoked": l["revoked"],
        "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": l["load_counted"]["max_cores"],
        "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"]})
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
over_budget = [(L, w) for L, w, r in walls if r > 1]
st, en = rec["started"]["epoch_s"], rec["ended"]["epoch_s"]


def osnote(L):
    t = osl[L]["turn"]
    return (f'{L} turn readings: os_level ' + ", ".join(f'{k} x{v}' for k, v in sorted(t["os_level"].items())) +
            "; pm_state " + ", ".join(f'{k} {v}' for k, v in sorted(t["pm_state"].items())) +
            (f'; non-Nominal from {t["non_nominal_from_turn_start_s"][0]} s to {t["non_nominal_from_turn_start_s"][1]} s after turn start'
             if t["non_nominal_from_turn_start_s"] else ""))
hot = [L for L in roster if osl[L]["turn"]["non_nominal_from_turn_start_s"]]
cool = [L for L in roster if L not in hot]


def cells(L):
    e = smp[L]["empty_cells_tol"]
    if not e:
        return f"{L} none"
    by = {}
    for _, ph, off in e:
        by.setdefault(ph, []).append(off)
    return f"{L} " + " + ".join(f"{len(v)} {ph}" for ph, v in by.items())
offs = [off for v in smp.values() for _, _, off in v["empty_cells_tol"]]
phases = {ph for v in smp.values() for _, ph, _ in v["empty_cells_tol"]}

# block summary: hp-01 = s01 (L001-L003) + s02 (L004-L007) + this span (L008-L012)
block = {"block": "hp-01 (kit cl-hp-01, High Power, type-H legs; description only, never in the fit)", "spans": []}
for sid, plan, d in (("hp-01-s01", "cq-hp-01-s01-a1", EV / "desk-cq-hp-01-s01-a1"),
                     ("hp-01-s02", "cq-hp-01-s02-a1", EV / "desk-cq-hp-01-s02-a1"), ("hp-01-s03", "cq-hp-01-s03-a1", None)):
    if d is None:
        h, a, sj = ht, ds, desk_stops
        verdict = "FINAL (this desk)"
    else:
        h = json.loads((d / "hand" / "hand_table.json").read_text()); a = json.loads((d / "auto" / "desk_summary.json").read_text())
        sj = json.loads((d / "auto" / "stops.json").read_text()); rr = json.loads((d / "RESULT.json").read_text())
        verdict = (rr.get("desk_final") or {}).get("verdict") or ("FINAL, RL-150 R9 " + rr["RL150_R9"]["verdict"])
    block["spans"].append({"span": sid, "plan_id": plan, "legs": [l["leg_id"] for l in h["legs"]],
        "admitted_desk": sum(x["admitted"] for x in a["legs"]), "included_hand": sum(l["included"] for l in h["legs"]),
        "attempts": sum(l["attempts"] for l in h["legs"]), "redos": sum(len(l["redo"]) for l in h["legs"]),
        "stops_desk": [s["code"] for s in sj], "stops_hand": h["span"]["stops_by_hand"], "restore_proven_hand": h["span"]["restore_proven_hand"],
        "high_power_revoked": h["span"]["high_power"]["revoked"], "desk_verdict": verdict,
        "legs_os_level_max_2": [l["leg_id"] for l in h["legs"] if l["os_level_max_turn"] == 2],
        "walls_s": [round(l["wall_s_stage"], 1) for l in h["legs"]]})
allw = [w for s in block["spans"] for w in s["walls_s"]]
block.update({"legs_total": sum(len(s["legs"]) for s in block["spans"]), "spans_total": len(block["spans"]),
              "admitted_total_desk": sum(s["admitted_desk"] for s in block["spans"]),
              "included_total_hand": sum(s["included_hand"] for s in block["spans"]),
              "excluded": [], "redos_total": sum(s["redos"] for s in block["spans"]),
              "named_stops": sum(len(s["stops_desk"]) + len(s["stops_hand"]) for s in block["spans"]),
              "restore_proven_all": all(s["restore_proven_hand"] for s in block["spans"]),
              "revoked_any": any(s["high_power_revoked"] for s in block["spans"]),
              "wall_s_range": [min(allw), max(allw)], "budget_s": budget, "leg_overtime_limit_s": factor * budget,
              "reserve": "none (RL-157 §4): an excluded type-H leg would not be replaced; none was excluded",
              "os_level_note": "the first leg of s02 (L004) and of s03 (L008) reached os_level 2 / pm_state Heavy late in its turn; s01's legs stayed 0. Not a rule (kit inclusion no_drop_by_outcome)."})
block["line"] = (f'hp-01: {block["legs_total"]} legs over {block["spans_total"]} spans (' + " + ".join(str(len(s["legs"])) for s in block["spans"]) +
                 f'), admitted {block["admitted_total_desk"]} of {block["legs_total"]} by the desks (' + " + ".join(str(s["admitted_desk"]) for s in block["spans"]) +
                 f'), included {block["included_total_hand"]} of {block["legs_total"]} by hand; {len(block["excluded"])} excluded, {block["redos_total"]} redos, '
                 f'{block["named_stops"]} named stops, restore proven on all {block["spans_total"]} closes, high_power.revoked null on all {block["spans_total"]}; '
                 f'walls {min(allw)}-{max(allw)} s against {factor} x {budget:,} = {factor*budget:,} s')

out = {
 "plan_id": "cq-hp-01-s03-a1", "span": "hp-01-s03", "legs": roster,
 "built": "2026-11-15 09:56-10:05 PST on the Air (desk builder for the lead)",
 "work_order": "RUN_STATE 341 (issued 07:20:13 PST); launch RUN_STATE 342 (ef6153c3, 07:26 PST); magistrate Check RUN_STATE 343 (2e53c580, 09:50 PST, origin/main b7e453018)",
 "data": f"{D} (read-only copy; sha256 -c of all 192 manifest entries OK; .air and .mbp manifests byte-equal, sha256 042585323ba9eac4d8ff70f6d5a6507a8cce7e00c8d6bee5798cf57933cd2de9)",
 "code": "dd206025abb30fd5c07515cd4b34b3e653174810 (/Volumes/JW-EXT/jw-wt/hp01-ready-dd2, detached, clean before and after, read-only)",
 "kit": {"source": "git show bbd34dc876001786c3603d9c4583391639284253:docs/process/cadence/kits/cl-hp-01.json (copy of /Volumes/JW-EXT/scratch/desk-hp01-s02/kit.json)",
         "sha256": "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965", "sha_asserted": True, "power_mode": kit["power_mode"]},
 "desk_command": "python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-hp-01-s03-a1 --input <OUT>/desk-bundle --out auto --kit kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter, per D6). auto/ = the lead's 09:55:30 run; auto-rerun/ = this builder's 09:57:17 re-run: desk_summary.json and stops.json identical, JOURNAL-TABLE.md differs only in its build-time line",
 "D6_span_result_json_exists": (D / "desk-bundle" / "span" / "result.json").is_file(),
 "desk_stops_json": desk_stops,
 "desk_block_mode_line": "Block AC powermode 2 (JOURNAL-TABLE.md)",
 "comparison": {
  "per_leg_values_compared": ncomp, "per_leg_values_differing": ndiff,
  "fields_per_leg": sorted(legs[0]["compare"]), "inclusion_included": True,
  "span_level_compared": ["leg count", "named stops (hand [] vs desk [])", "result (desk_summary vs receipt span_result vs span/result.json)", "meter", "feeds_proven_stopped"],
  "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
  "scope_notes": ["the desk table has no admitted column (dev-01 F8): admitted read from desk_summary.json, i.e. each leg_summary.json (D1)",
                  "hand 'reached' derives from G0 released + quiet_s 0 + release-to-turn < 5 s (" + " / ".join(f'{l["release_to_turn_s"]:.3f}' for l in legs) + " s); same result",
                  "; ".join(osnote(L) for L in hot) + f"; {', '.join(cool)} 0/Nominal throughout the turn; hand os_level_max / pm_nominal agree with the desk on all five. Not a rule: kit inclusion 'no_drop_by_outcome' (no leg is dropped for its OS level or state)",
                  f'rules 3 and 4 left to the look (meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped)',
                  "the desk omits restore lines and censuses; the hand table carries them clean"]},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL" if (ndiff == 0 and not ht["diffs"] and n_incl == n == n_adm and not desk_stops and not span["stops_by_hand"]) else "NOT FINAL",
                "meaning": "automatic desk = independent hand table on every value, inclusion included",
                "basis": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} of 5 span-level values differ; {n_incl} of {n} included by hand, {n_adm} of {n} admitted by desk; stops.json {desk_stops} and hand stops {span['stops_by_hand']}",
                "R9": "not applicable (remainder span, not the smoke)"},
 "rules_by_hand": {"1_ran_to_cap": f"{sum(l['rules']['1_ran_to_cap'] for l in legs)}/{n} (decode 4,096/4,096 each, leg_status complete, member succeeded, stage rc 0)",
                   "2_g0_released": f"{sum(l['rules']['2_g0_released'] for l in legs)}/{n} (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + "; journal G0 = record g0_wait_s)",
                   "5_not_contaminated": f"{sum(l['rules']['5_not_contaminated'] for l in legs)}/{n} (one attempt each, no redo; longest run over 0.5 core " + "/".join(str(l["load_counted"]["longest_run_over_0p5_s"]) for l in legs) + " s of 60; journals cover their attempts; hand agrees with recorded os_load)",
                   "6_high_power": f"{sum(l['rules']['6_block_power_mode_2_high_power'] for l in legs)}/{n} (leg_record ac_powermode 2 at episode start; own pre-attempt L0nn.a1-powermode step rc 0 reads 2 with this span's marker; next observation (next leg's powermode step, or power_last_look after L012) reads 2 with this span's marker: {sum(v['holds'] for v in nxt.values())}/{n}; high_power.revoked null)",
                   "3_4": f'at the look; meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped'},
 "restore_proven": {"span_result_json": ht["span"]["span_result_file"]["restore_proven"], "receipt_span_result": span["span_result"]["restore_proven"], "hand": span["restore_proven_hand"]},
 "close_proof": span["high_power"]["close_proof"], "restore": span["high_power"]["restore"],
 "power_proof_step": span["power_proof"], "power_last_look_step": span["power_last_look"], "read_power_step_before_soak": span["read_power"],
 "high_power_step": span["high_power_step"], "host_lock_release": span["host_lock_release"], "close_steps_rc": span["close_steps"],
 "high_power": {"revoked": span["high_power"]["revoked"], "before_restore": span["high_power"]["before_restore"],
                "block_power_mode": span["high_power"]["block_power_mode"], "host_marker": span["high_power"]["host_marker"]},
 "D1": f"admitted from each leg_summary true x{n_adm}; high_power.revoked null; before_restore {{ac_powermode 2, marker present, marker_is_this_spans true, pmset_error null}}. D1 second line: no revoked entry, so nothing holds the next span on D1.",
 "D5": "not engaged: no SIGKILL (receipt rc 0, power_last_look rc 0 read mode 2 with this span's marker after L012, revoked null); every admitted:true is backed by a later observation.",
 "LEG_OVERTIME": "no",
 "LEG_OVERTIME_detail": f"walls {', '.join(str(w) for _, w, _ in walls)} s against {factor} x {budget:,} = {factor*budget:,} s; max ratio {max(r for *_, r in walls)}; " +
                        (f"{len(over_budget)} legs a few seconds over budget_s {budget:,} ({', '.join(f'{L} +{w - budget:.1f} s' for L, w in over_budget)}), far under the {factor} x limit; " if over_budget else "none over budget_s; ") +
                        "0 legs over, stop needs 2",
 "RL157_s1": rl157,
 "RL157_s5": [{"leg": l, "g0_s": round(next(x for x in legs if x["leg_id"] == l)["g0_s_journal"], 1), "wall_s": w, "budget_s": budget, "wall_over_budget": r} for l, w, r in walls],
 "RL150_R1_part3_print": r1,
 "RL150_R1_note": "TV0h = TV1h in every reading (soak, own references, G0 releases), so nothing routes under RL-149 §5 item 6",
 "RL156a": {"starvation": "none",
   "thermal_sampler": {k: {"cells": v["cells"], "reads": v["reads"], "read_errors": v["read_errors"], "cells_with_no_reading_at_all": v["cells_with_no_reading_at_all"],
                           "max_interval_s": v["max_interval_s"], "empty_cells_on_100ms_tolerance": v["empty_cells_tol"], "cov_reported": v["cov_reported"]} for k, v in smp.items()},
   "thermal_note": ("every 1-s cell holds a reading; " + f"{sum(v['read_errors'] for v in smp.values())} read errors; max intervals " + "/".join(str(v["max_interval_s"]) for v in smp.values()) +
                    f" s. Off-grid cells ({min(offs):.0f}-{max(offs):.0f} ms from the grid, tolerance 100 ms): " + ", ".join(cells(L) for L in roster) +
                    f"; phases with any: {sorted(phases)}; none in G0 or the turn. Jitter, not starvation."),
   "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
   "inventory": "no gap and not exercised: the cadence-leg kind never calls start_inventory at dd206025a (only r1_runtime k_step_30b and k_step_d do; read for the smoke desk at the same pin, not re-read); no inventory journal in OUT (find -iname '*inventory*' empty)"},
 "os_level_census": osl,
 "maintenance_overlap": ("MAINTENANCE-OVERLAP.md (print only, gates nothing): dasd in every phase (3,254-4,958 per leg; L008 4,937 and L011 4,958 the high two); no XProtect, no mdworker in any leg; "
                         "mds 3 in L011's TURN (09:20:51) and 6 in the 07:20 bucket (soak start, before L008); softwareupdated 8 in L008's G0 (08:11:53) and 8 in L011's pre-G0 (09:12:01); backupd 6-24 per leg; "
                         "mobileassetd: 1,398 in L011's TURN (09:16:17-09:23:36; 3 at 09:18, 33 at 09:20, 1,362 at 09:21), 385 in L008 (208 pre-G0, 176 in G0 at 08:10-08:12, 1 turn), 182 in L009 (179 pre-G0, 3 turn), 4 in L010 (turn), 1 in L012 (09:26:28, pre-G0). "
                         "The magistrate's '1,396 lines in the 09:20 bucket (L011 end, L012 start)' is L011's turn, not L012 (L012 starts 09:25:00 and holds 1); the bucket's 1,396 = 33 + 1,362 + the one at 09:26. "
                         "Rule 5 clean on all five (longest run over 0.5 core 2/2/2/13/5 s of 60); L011's 13 s run (max 2.964 cores, the span's highest) falls at about 09:21:23-09:21:35 PST (attempt start + 1,033-1,045 s on the load journal's t_s), inside the 09:21 mobileassetd burst and L011's turn. Print only; no rule fires; kit no_drop_by_outcome."),
 "span_level": {k: span[k] for k in ("rc", "mock", "kit", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": st, "receipt_ended_epoch_s": en, "runner_span_s": round(en - st, 1),
                        "item_341_plan_expected_s": 9405, "item_341_plan_worst_s": 22050, "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / n, 1)},
 "block_summary_hp01": block,
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "LEG_OVERTIME": out["LEG_OVERTIME_detail"], "rl157": rl157, "time": out["time_calendar_only"], "nxt": nxt,
                  "block": block["line"], "thermal_note": out["RL156a"]["thermal_note"], "os": out["comparison"]["scope_notes"][2]}, indent=1))
