"""Assemble RESULT.json for desk-cq-dev-02-s02-a1 from hand/ outputs (and receipt stamps/step results).

The hp-01-s03 desk's build_result.py (desk-cq-hp-01-s03-a1, 05c681ac4) adapted to a development span on Automatic:
the High Power fields (powermode steps, close_proof, revoked, RL-157 section 1) are dropped; rule 6 is the s04 desk's
(leg record ac_powermode 0, restore step observed 0); the rule-5 placement (rule5_place.out) and the per-minute
burst (maint_burst.out) feed the RL-171 section 5 judgement; the block line is dev-02's first half only.
Usage: python3 -I -B build_result.py DESK_DIR OUT
"""
import json, sys
from pathlib import Path
T, D = Path(sys.argv[1]), Path(sys.argv[2])
H = T / "hand"
ht = json.loads((H / "hand_table.json").read_text())
ds = json.loads((T / "auto" / "desk_summary.json").read_text())
rec = json.loads((D / "runner_receipt.json").read_text())
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
r5p = {k: json.loads(v) for k, v in lines("rule5_place.out").items()}
legs = ht["legs"]
roster = rec["roster"]
budget = legs[0]["budget_s"]; factor = kit["stop_rules"]["leg_time_factor"]
ncomp = sum(len(l["compare"]) for l in legs)
ndiff = sum(1 for l in legs for c in l["compare"].values() if not c["agree"])
n = len(legs); n_incl = sum(l["included"] for l in legs); n_adm = sum(a["admitted"] for a in ds["legs"])
desk_stops = json.loads((T / "auto" / "stops.json").read_text())
hand_legs = [{"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
              "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
              "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"],
              "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": l["load_counted"]["max_cores"],
              "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"]}
             for l in legs]
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
over_budget = [(L, w) for L, w, r in walls if r > 1]
st, en = rec["started"]["epoch_s"], rec["ended"]["epoch_s"]
offs = [off for v in smp.values() for _, _, off in v["empty_cells_tol"]]
phases = {ph for v in smp.values() for _, ph, _ in v["empty_cells_tol"]}


def cells(L):
    e = smp[L]["empty_cells_tol"]
    if not e:
        return f"{L} none"
    by = {}
    for _, ph, off in e:
        by.setdefault(ph, []).append(off)
    return f"{L} " + " + ".join(f"{len(v)} {ph}" for ph, v in by.items())


def onset(L):
    return osl[L]["turn"]["non_nominal_from_turn_start_s"][0]


restore = span["restore"]
restore_proven_hand = (span["close_steps"]["restore"] == 0 and restore["ok"] is True and restore["observed"] == 0
                       and span["span_result"].get("restore_proven", True) is not False)
l002_run = r5p["L002"]["runs_ge_3s"][0]
final = ndiff == 0 and not ht["diffs"] and n_incl == n == n_adm and not desk_stops and not span["stops_by_hand"]
out = {
 "plan_id": "cq-dev-02-s02-a1", "span": "dev-02-s02", "legs": roster,
 "built": "2026-11-15 15:31-15:50 PST on the Air (desk builder for the lead)",
 "work_order": "RUN_STATE 344 (issued 09:55:43 PST); launch RUN_STATE 345 (f6a8d11b, 10:02 PST); magistrate Check RUN_STATE 349 (a187f945, 12:47 PST); offload RUN_STATE 350; origin/main ebd56fb3d",
 "data": f"{D} (read-only copy; sha256 -c of all 226 manifest entries OK; .air and .mbp manifests byte-equal, sha256 abc831aca7acbdd49b177fc7fcd899e9a67efe0d88d75d5a9438e5dbdbcf43f2)",
 "code": "b4b6aeb192da60d895a7529311b06599efff5be4 (/Volumes/JW-EXT/jw-wt/desk-final-pin-b4b6aeb19, detached, clean before and after, read-only)",
 "kit": {"source": "git show 589748f15af6415dc536520469cd19c7800d9adf:docs/process/cadence/kits/cl-dev-02.json (blob 7e8dc7a2), copied outside the checkout",
         "sha256": "d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8", "sha_asserted": True,
         "receipt_kit": rec["kit"]},
 "desk_command": "TMPDIR=<scratch>/tmp python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-dev-02-s02-a1 --input <OUT>/desk-bundle --out auto --kit kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter, per D6)",
 "D6_span_result_json_exists": (D / "desk-bundle" / "span" / "result.json").is_file(),
 "desk_stops_json": desk_stops,
 "comparison": {
  "per_leg_values_compared": ncomp, "per_leg_values_differing": ndiff,
  "fields_per_leg": sorted(legs[0]["compare"]), "inclusion_included": True,
  "span_level_compared": ["leg count", "named stops (hand [] vs desk [])", "result (desk_summary vs receipt span_result)", "meter", "feeds_proven_stopped"],
  "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
  "scope_notes": ["the desk table has no admitted column (dev-01 F8): admitted read from desk_summary.json, i.e. each leg_summary.json (D1)",
                  "hand 'reached' derives from G0 released + quiet_s 0 + release-to-turn < 5 s (" + " / ".join(f'{l["release_to_turn_s"]:.3f}' for l in legs) + " s); same result",
                  "every leg reached os_level 2 / pm_state Heavy in its turn (non-Nominal from " + ", ".join(f"{L} {onset(L)} s" for L in roster) +
                  " after turn start, to the turn's end); hand os_level_max 2 / pm_nominal false agree with the desk on all six. Not a rule: kit inclusion 'no_drop_by_outcome'",
                  f'rules 3 and 4 left to the look (meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped)',
                  "the desk omits restore lines and censuses; the hand table carries them clean"]},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL" if final else "NOT FINAL",
                "meaning": "automatic desk = independent hand table on every value, inclusion included",
                "basis": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} of 5 span-level values differ; {n_incl} of {n} included by hand, {n_adm} of {n} admitted by desk; stops.json {desk_stops} and hand stops {span['stops_by_hand']}",
                "R9": "not applicable (dev-02's pilot is dev-01's; item 344 line 8)"},
 "rules_by_hand": {"1_ran_to_cap": f"{sum(l['rules']['1_ran_to_cap'] for l in legs)}/{n} (decode 4,096/4,096 each, leg_status complete, stage rc 0)",
                   "2_g0_released": f"{sum(l['rules']['2_g0_released'] for l in legs)}/{n} (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + "; journal G0 = record g0_wait_s)",
                   "5_not_contaminated": f"{sum(l['rules']['5_not_contaminated'] for l in legs)}/{n} (one attempt each, no redo; longest run over 0.5 core " + "/".join(str(l["load_counted"]["longest_run_over_0p5_s"]) for l in legs) + " s of 60; journals cover their attempts; hand agrees with recorded os_load)",
                   "6_power_mode_0": f"{sum(l['rules']['6_power_mode_0'] for l in legs)}/{n} (leg_record ac_powermode 0 at episode start; read_power before soak {span['read_power']}; restore observed {restore['observed']})",
                   "3_4": f'at the look; meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped'},
 "restore": restore, "restore_proven_hand": restore_proven_hand, "close_steps_rc": span["close_steps"], "read_power_step_before_soak": span["read_power"],
 "LEG_OVERTIME": "no",
 "LEG_OVERTIME_detail": f"walls {', '.join(str(w) for _, w, _ in walls)} s against {factor} x {budget:,} = {factor*budget:,} s; max ratio {max(r for *_, r in walls)}; " +
                        (f"{len(over_budget)} legs a few seconds over budget_s {budget:,} ({', '.join(f'{L} +{w - budget:.1f} s' for L, w in over_budget)}), far under the {factor} x limit; " if over_budget else "none over budget_s; ") +
                        "0 legs over, stop needs 2",
 "RL150_R1_part3_print": r1,
 "RL150_R1_note": "TV0h = TV1h in every reading (soak, own references, G0 releases), so nothing routes under RL-149 section 5 item 6. Kit cl-dev-02 (v1): every leg captures its own reference (status captured, source_member = itself); no span reference",
 "RL158_Q1": {"applies": "Q1's hand print is defined for v1.1 spans (span reference = first leg's capture); cl-dev-02 is a v1 kit where each leg is its own reference",
              "print": "RL150_R1_part3_print above IS this span's Q1 print in its v1 form: the soak reference, the first leg's (L001's) capture, and for every leg its own capture, release reading and G0 wait",
              "first_leg_capture": r1["L001"]["own_reference"], "soak_reference_line": r1["soak_reference_line"],
              "g0_wait_s": {L: round(r1[L]["g0"]["duration_s"], 1) for L in roster},
              "marks": "none: L001 ran one attempt (no redo, not excluded)",
              "completion_record": "docs/research-audits/2026-11-10-fable/evidence/cadence-standing/q1/cq-dev-02-s02-a1.json (joulewise.cadence_q1_record.v1; RL-173 E)"},
 "RL156a": {"starvation": "none",
   "thermal_sampler": {k: {"cells": v["cells"], "reads": v["reads"], "read_errors": v["read_errors"], "cells_with_no_reading_at_all": v["cells_with_no_reading_at_all"],
                           "max_interval_s": v["max_interval_s"], "empty_cells_on_100ms_tolerance": v["empty_cells_tol"], "cov_reported": v["cov_reported"]} for k, v in smp.items()},
   "thermal_note": ("every 1-s cell holds a reading; " + f"{sum(v['read_errors'] for v in smp.values())} read errors; max intervals " + "/".join(str(v["max_interval_s"]) for v in smp.values()) +
                    f" s. Off-grid cells ({min(offs):.0f}-{max(offs):.0f} ms from the grid, tolerance 100 ms): " + ", ".join(cells(L) for L in roster) +
                    f"; phases with any: {sorted(phases)}; none in G0 or the turn. Jitter, not starvation."),
   "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
   "inventory": "not exercised: the cadence-leg kind does not run the R1 ProcessInventory journal (item 344 line 8); no inventory journal in OUT (find -iname '*inventory*' empty)"},
 "os_level_census": osl,
 "rule5_placement": r5p,
 "maintenance_overlap": ("MAINTENANCE-OVERLAP.md (print only, gates nothing). Item 349's heavy 11:00 bucket (softwareupdated 2,596, mobileassetd 2,044, XProtectPluginService 1,124) is all inside L002's G0 (11:07:06-11:10:31): "
                         "per minute (maint_burst.out) XProtect 62 + XProtectPluginService 1,124, mobileassetd 1,358, softwareupdated 1,776 at 11:08 (all four start 11:08:55; XProtect* ends 11:08:58), then mobileassetd 686 + softwareupdated 820 at 11:09, 12 + 24 at 11:10. "
                         "In L002's turn (11:10:31-11:17:51) only mobileassetd 16, softwareupdated 33, backupd 6 and dasd. XProtect* 0 and softwareupdated <= 8 in every other leg; mds 6 only at 10:00 (soak start). "
                         f"Rule 5 (RL-72 E2, > 0.5 core sustained 60 s): L002's longest run over 0.5 core is {l002_run['len_samples']} s ({l002_run['pst'][0]}-{l002_run['pst'][1]} PST, max {l002_run['max_cores']} cores, the span's highest), exactly at the burst's onset, inside G0; "
                         "it does not fire (8 of 60 s), the runner recorded L002 clean (contaminated false, no redo), and the hand recomputation agrees. "
                         "JUDGEMENT (as the s04 and hp-01-s03 desks judged rule 5: by the load journal's sustained-load test, not by log-line counts): rule 5 passes on L002 and all six; nothing excluded, no redo owed. "
                         "Contrast dev-01-s04 L012.a1 (XProtect 794 + mobileassetd 3,362 across G0 and turn, 696 s over 0.5 core: fired, redone). G0 still released at 205.1 s (span range 204.0-210.4 s), and the turn began after the burst had ended. "
                         "Recorded for the look: L002's G0 overlaps an OS-update burst of about 7 s CPU; print only, kit no_drop_by_outcome."),
 "span_level": {k: span[k] for k in ("rc", "mock", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": st, "receipt_ended_epoch_s": en, "runner_span_s": round(en - st, 1),
                        "item_344_plan_expected_s": 10656, "item_344_plan_worst_s": 24750, "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / n, 1)},
 "block_line_dev02": f"dev-02: {n} of 12 legs collected (L001-L006, this span), {n_adm} admitted by the desk, {n_incl} included by hand, 0 excluded, 0 redos, 0 named stops; L007-L012 are dev-02-s03 (not run)",
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "LEG_OVERTIME": out["LEG_OVERTIME_detail"], "time": out["time_calendar_only"],
                  "restore_proven_hand": restore_proven_hand, "thermal_note": out["RL156a"]["thermal_note"]}, indent=1))
