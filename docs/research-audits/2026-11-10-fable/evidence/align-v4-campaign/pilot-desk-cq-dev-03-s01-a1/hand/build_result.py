"""Assemble RESULT.json for pilot-desk-cq-dev-03-s01-a1 from hand/ outputs (and receipt stamps/step results).

The dev-02-s03 desk's build_result.py (desk-cq-dev-02-s03-a1, 4a53c34a4), itself the dev-02-s02 desk's, adapted to
kit cl-dev-03.v1.1: per-leg budgets, the v1.1 span-reference fields (g0_role, g0_shape, span_reference, consumer checks),
the R9 line and the class A smoke line as PROPOSED verdicts (the lead signs them), and RL-158 Q5 prefill deviations.
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
factor = kit["stop_rules"]["leg_time_factor"]
ncomp = sum(len(l["compare"]) for l in legs)
ndiff = sum(1 for l in legs for c in l["compare"].values() if not c["agree"])
n = len(legs); n_incl = sum(l["included"] for l in legs); n_adm = sum(a["admitted"] for a in ds["legs"])
desk_stops = json.loads((T / "auto" / "stops.json").read_text())
L = {l["leg_id"]: l for l in legs}
hand_legs = [{"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
              "g0_role": l["g0_role_hand"], "g0_shape": l["g0_shape_hand"], "span_reference": l["span_reference_hand"],
              "prefill_tokens_realized": l["prefill_tokens"], "prefill_tokens_nominal": l["prefill_tokens_nominal_kit"], "prefill_deviation_pct": l["prefill_deviation_pct"],
              "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
              "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"],
              "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": l["load_counted"]["max_cores"],
              "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"],
              **({"consumer_checks": l["consumer_checks"], "g0_reference_source": l["g0_reference_source_record"],
                  "g0_reference_record_sha256": l["g0_reference_record_sha256_record"]} if "consumer_checks" in l else {"capture_checks": l["capture_checks"]})}
             for l in legs]
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
over_limit = [(a, w) for (a, w, r) in walls if r > factor]
over_budget = [(a, w, w - L[a]["budget_s"]) for a, w, r in walls if r > 1]
st, en = rec["started"]["epoch_s"], rec["ended"]["epoch_s"]
restore = span["restore"]
restore_proven_hand = (span["close_steps"]["restore"] == 0 and restore["ok"] is True and restore["observed"] == 0
                       and span["span_result"].get("restore_proven", True) is not False)
cons = L["L002"]; cc = cons["consumer_checks"]
smoke_met = (cons["g0_role_hand"] == "consume" and cons["g0_outcome_journal"] == "released" and all(v is True for k, v in cc.items() if k != "own_window_reference_status")
             and cons["leg_status"] == "complete" and cons["decode_tokens"] >= cons["decode_cap"] and cons["span_reference_hand"] == {"leg_id": "L001", "attempt": 1, "excluded": False, "redone": False}
             and cons["band_reached"] and cons["included"])
final = ndiff == 0 and not ht["diffs"] and n_incl == n == n_adm and not desk_stops and not span["stops_by_hand"]
r9_ok = (n == 3 and span["rc"] == 0 and span["span_result"]["chain_outcome"] == "COMPLETE" and span["legs_finished"] == 3 and n_adm == 3 and final and not desk_stops)
MAINT = open(H / "maint_judgement.txt").read().strip()
out = {
 "plan_id": "cq-dev-03-s01-a1", "span": "dev-03-s01", "legs": roster,
 "built": open(H / "built.txt").read().strip(),
 "work_order": "RUN_STATE 355 (issued 2026-11-15 15:42:10 PST); launch RUN_STATE 362 (f845859d, 2026-11-16 ~03:39 PST); magistrate Check RUN_STATE 363 (d59960c1, 05:16 PST); origin/main cd1c9bdeb",
 "data": f"{D} (read-only copy; sha256 -c of all 123 manifest entries OK; .air and .mbp manifests byte-equal, sha256 0489daf073bc8b6906e4e06d664517bd9158c9925f3529fb365f9cfa2cc441eb)",
 "code": "2d347f721552fe03bdd19f113e7bad7a7c24908e (/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721, detached, clean before and after, read-only); the desk checkout item 355 'After' names",
 "kit": {"source": "git show 9cbb365a6:docs/process/cadence/kits/cl-dev-03.v1.1.json, copied outside the checkout", "sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b",
         "sha_asserted": True, "receipt_kit": rec["kit"]},
 "desk_command": "TMPDIR=<scratch>/tmp python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-dev-03-s01-a1 --input <OUT>/desk-bundle --out auto --kit kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter, per D6)",
 "D6_span_result_json_exists": (D / "desk-bundle" / "span" / "result.json").is_file(),
 "desk_stops_json": desk_stops,
 "comparison": {
  "per_leg_values_compared": ncomp, "per_leg_values_differing": ndiff,
  "fields_per_leg": sorted(legs[0]["compare"]), "inclusion_included": True,
  "span_level_compared": ["leg count", "named stops (hand [] vs desk [])", "result (desk_summary vs receipt span_result)", "meter", "feeds_proven_stopped", "span_reference (leg_id, attempt, consumers, consistent)"],
  "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
  "scope_notes": ["the desk table has no admitted column in JOURNAL-TABLE's first table; admitted read from desk_summary.json (D1); the v1.1 cell table lists it",
                  "hand 'reached' derives from G0 released + quiet_s 0 + release-to-turn < 5 s (" + " / ".join(f'{l["release_to_turn_s"]:.3f}' for l in legs) + " s); same result",
                  "hand g0_shape and nominal prefill come from the kit (the leg spec of an own-shaped leg carries no g0_shape); hand g0_role from the kit shape (span = consume, own = capture), checked against the leg record's own g0_role; the hand span_reference is derived from the L002 G0 gate row's reference source_member, matched to L001's window reference run id, and L001's attempts/inclusion/redo by hand",
                  "the desk's prefill_tokens is the kit nominal; the realized counts (leg_record) are reported separately (RL-158 Q5), all within 5 %",
                  "OS level: hand os_level_max / pm_nominal equal the desk's on all three (1 / 2 / 2, false); not a rule: kit inclusion 'no_drop_by_outcome'",
                  f'rules 3 and 4 left to the look (meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped)',
                  "the desk omits restore lines and censuses; the hand table carries them clean"]},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL" if final else "NOT FINAL",
                "meaning": "automatic desk = independent hand table on every value, inclusion included (kit v1.1 fields too)",
                "basis": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} of 6 span-level values differ; {n_incl} of {n} included by hand, {n_adm} of {n} admitted by desk; stops.json {desk_stops} and hand stops {span['stops_by_hand']}"},
 "R9_proposed": {
   "verdict": "R9: PASSED (proposed)" if r9_ok else "R9: NOT PASSED (proposed)",
   "signed_by": "not signed: the lead signs (item 355 'After')",
   "table": {
     "1_closes_with_complete_records": f"{span['legs_finished']} of {span['legs_planned']} legs closed; receipt rc {span['rc']}, outcome {span['span_result']['outcome']}, chain {span['span_result']['chain_outcome']}, 25/25 steps rc 0; every leg_record leg_status complete, decode 4,096/4,096",
     "2_admitted": f"{n_adm} of {n} (desk, from each leg_summary.json); {n_incl} of {n} included by hand",
     "3_excluded_legs": "none (no leg fell under any inclusion rule 1-6; no redo; none refilled from the reserve)",
     "4_hand_table_equals_desk": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} of 6 span-level values differ, inclusion included; stops.json [] and hand stops []",
     "named_stops_open": "none (desk stops.json [], hand [])"}},
 "smoke_proposed": {
   "verdict": "smoke: MET (proposed)" if smoke_met else "smoke: NOT MET (proposed)",
   "signed_by": "not signed: the lead signs (RL-161 section 2, RL-158 section 2)",
   "statement": "L002's G0 released against L001's capture and L002 ran its turn",
   "evidence": {
     "L002_g0_role": cons["g0_role_hand"], "L002_g0_shape": cons["g0_shape_hand"],
     "L002_g0_outcome": cons["g0_outcome_journal"], "L002_g0_wait_s": round(cons["g0_s_journal"], 3), "g0_timeout_s": cons["g0_timeout_s"],
     "L002_prefill_tokens_realized": cons["prefill_tokens"], "L002_decode": f'{cons["decode_tokens"]}/{cons["decode_cap"]}', "L002_leg_status": cons["leg_status"],
     "g0_reference_source": cons["g0_reference_source_record"], "g0_reference_record_sha256": cons["g0_reference_record_sha256_record"],
     "span_reference": cons["span_reference_hand"], "reference_is_first_leg": cc["reference_is_first_leg"],
     "record_sha256_equals_L001_window_reference_record_sha256": cc["record_sha_equals_capture_record_sha"],
     "G0_row_reference_equals_L001_capture (fast_c and span_ns)": bool(cc["row_reference_fast_c_equals_capture_fast_c"] and cc["row_reference_span_equals_capture_span"]),
     "L001_window_reference": {"status": L["L001"]["own_window_reference"]["status"], "record_sha256": L["L001"]["own_window_reference"]["record_sha256"], "TV0h_TV1h_c": L["L001"]["own_window_reference"]["fast_c"]},
     "L001_attempts_excluded_redone": [L["L001"]["attempts"], not L["L001"]["included"], L["L001"]["contaminated_redos"] > 0],
     "release_to_turn_s": round(cons["release_to_turn_s"], 3), "turn_after_release_by_stamps": True,
     "L002_G0_release_reading": r1["L002"]["g0"]["release"], "L002_row_reference": r1["L002"]["g0"]["row_reference"],
     "l002_included_rules_1_to_6": cons["rules"], "L002_admitted_by_desk": ds["legs"][1]["admitted"]},
   "marks": "none: the span's reference is not from a redo and not from an excluded leg"},
 "rules_by_hand": {"1_ran_to_cap": f"{sum(l['rules']['1_ran_to_cap'] for l in legs)}/{n} (decode 4,096/4,096 each, leg_status complete, stage rc 0)",
                   "2_g0_released": f"{sum(l['rules']['2_g0_released'] for l in legs)}/{n} (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + "; journal G0 = record g0_wait_s; against the reference its kit shape names: L001 own capture, L002 L001's capture, L003 own capture)",
                   "5_not_contaminated": f"{sum(l['rules']['5_not_contaminated'] for l in legs)}/{n} (one attempt each, no redo; longest run over 0.5 core " + "/".join(str(l["load_counted"]["longest_run_over_0p5_s"]) for l in legs) + " s of 60; journals cover their attempts; hand agrees with recorded os_load)",
                   "6_power_mode_0": f"{sum(l['rules']['6_power_mode_0'] for l in legs)}/{n} (leg_record ac_powermode 0 at episode start; read_power before soak {span['read_power']}; restore observed {restore['observed']})",
                   "3_4": f'at the look; meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped'},
 "restore": restore, "restore_proven_hand": restore_proven_hand, "close_steps_rc": span["close_steps"], "read_power_step_before_soak": span["read_power"],
 "LEG_OVERTIME": "no" if not over_limit else "yes",
 "LEG_OVERTIME_detail": f"walls {', '.join(str(w) for _, w, _ in walls)} s against 1.5 x budgets " + ", ".join(f"{a} {L[a]['budget_s']:,}" for a in roster) + f" = " + ", ".join(f"{factor*L[a]['budget_s']:,.0f}" for a in roster) + f" s; max ratio {max(r for *_, r in walls)}; " +
                        (f"{len(over_budget)} leg(s) a few seconds over its budget_s ({', '.join(f'{a} +{d:.1f} s' for a, _, d in over_budget)}), far under the {factor} x limit; " if over_budget else "none over budget_s; ") + f"{len(over_limit)} legs over the limit, stop needs 2",
 "RL150_R1_part3_print": r1,
 "RL150_R1_note": "TV0h = TV1h in every reading (soak, references, G0 releases), so nothing routes under RL-149 section 5 item 6. Kit v1.1: L001 (first leg) captures the span's reference (status captured, source_member = itself); L002 is the span-shaped consumer and writes no window reference of its own (file absent by design); L003 is own-shaped and captures its own",
 "RL158_Q1": {"print": "RL150_R1_part3_print above IS this span's Q1 print: the soak reference, L001's capture, and L002's release reading and G0 wait",
              "soak_reference_line": r1["soak_reference_line"], "L001_capture": r1["L001"]["own_reference"],
              "L002_release_reading": r1["L002"]["g0"]["release"], "L002_g0_wait_s": round(r1["L002"]["g0"]["duration_s"], 3),
              "g0_wait_s": {a: round(r1[a]["g0"]["duration_s"], 1) for a in roster},
              "marks": "none: L001 (the reference leg) ran one attempt, was not redone and not excluded; no 'reference from a redo' or 'reference from an excluded leg' mark",
              "completion_record": "docs/research-audits/2026-11-10-fable/evidence/cadence-standing/q1/cq-dev-03-s01-a1.json (joulewise.cadence_q1_record.v1; RL-173 E)"},
 "RL158_Q5_prefill_deviation": {a: {"nominal": L[a]["prefill_tokens_nominal_kit"], "realized": L[a]["prefill_tokens"], "pct": L[a]["prefill_deviation_pct"]} for a in roster},
 "RL158_Q5_note": "no leg's realized prefill count is more than 5 % from its nominal (L001 +1.2 %, L002 0.0 %, L003 +0.15 %)",
 "RL158_Q6_consumers": "1 consumer in this span (L002); on the 3 + 9 layout the block has 5 of the 10 warm legs as consumers (L002, L008, L009, L010, L012), item 355 line 4",
 "RL156a": {"starvation": "none",
   "thermal_sampler": {k: {"cells": v["cells"], "reads": v["reads"], "read_errors": v["read_errors"], "cells_with_no_reading_at_all": v["cells_with_no_reading_at_all"],
                           "max_interval_s": v["max_interval_s"], "empty_cells_on_100ms_tolerance": v["empty_cells_tol"], "cov_reported": v["cov_reported"]} for k, v in smp.items()},
   "thermal_note": ("every 1-s cell holds a reading; " + f"{sum(v['read_errors'] for v in smp.values())} read errors; max intervals " + "/".join(str(v["max_interval_s"]) for v in smp.values()) +
                    " s. Off-grid cells (140-160 ms from the grid, tolerance 100 ms): L002 1 post-turn, L003 1 post-turn, L001 none; none in G0 or the turn. Jitter, not starvation."),
   "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
   "inventory": "not exercised: the cadence-leg kind does not run the R1 ProcessInventory journal; no inventory journal in OUT (find -iname '*inventory*' empty)"},
 "os_level_census": osl,
 "rule5_placement": r5p,
 "maintenance_overlap": MAINT,
 "span_level": {k: span[k] for k in ("rc", "mock", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": st, "receipt_ended_epoch_s": en, "runner_span_s": round(en - st, 1),
                        "item_355_plan_expected_s": 7024, "item_355_plan_worst_s": 16650, "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / n, 1)},
 "block_line_dev03": f"dev-03: {n} of 12 legs collected (L001-L003, this counted pilot), {n_adm} admitted by the desk, {n_incl} included by hand, 0 excluded, 0 redos, 0 named stops; L004-L012 are the remainder (not run; they wait for the lead's two verdicts)",
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "R9": out["R9_proposed"]["verdict"], "smoke": out["smoke_proposed"]["verdict"], "LEG_OVERTIME": out["LEG_OVERTIME_detail"],
                  "time": out["time_calendar_only"], "restore_proven_hand": restore_proven_hand, "q5": out["RL158_Q5_prefill_deviation"]}, indent=1))
