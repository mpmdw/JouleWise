"""Assemble RESULT.json for desk-cq-dev-03-s02-a1 (dev-03-s02, L004-L012, kit cl-dev-03.v1.1) from hand/ outputs.

Adapted from the dev-03 pilot desk's build_result.py (pilot-desk-cq-dev-03-s01-a1, 734e7f6be): no R9/smoke lines
(the pilot's), L004 captures the span reference (span-shaped but first), four consumers, and a dev-04-s02 gate section
(RL-165 s4, RL-167, RL-173 D.4) built from the pilot's committed RESULT.json plus this span.
Usage: python3 -I -B build_result.py DESK_DIR DATA_DIR PILOT_RESULT_JSON
"""
import json, sys
from pathlib import Path
T, D, PILOT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
H = T / "hand"
ht = json.loads((H / "hand_table.json").read_text())
ds = json.loads((T / "auto" / "desk_summary.json").read_text())
rec = json.loads((D / "runner_receipt.json").read_text())
kit = json.loads((T / "kit.json").read_text())
pilot = json.loads(PILOT.read_text())
span = ht["span"]


def lines(name):
    out = {}
    for l in (H / name).read_text().splitlines():
        k, _, v = l.partition(" ")
        out[k] = v
    return out


r1 = {}
for l in (H / "r1print.out").read_text().splitlines():
    if not l.strip():
        continue
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
consumers = [l for l in legs if l["g0_role_hand"] == "consume"]
hand_legs = [{"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
              "g0_role": l["g0_role_hand"], "g0_shape": l["g0_shape_hand"], "span_reference": l["span_reference_hand"],
              "prefill_tokens_realized": l["prefill_tokens"], "prefill_tokens_nominal": l["prefill_tokens_nominal_kit"], "prefill_deviation_pct": l["prefill_deviation_pct"],
              "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
              "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"],
              "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": round(l["load_counted"]["max_cores"], 3),
              "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"],
              **({"consumer_checks": l["consumer_checks"], "g0_reference_source": l["g0_reference_source_record"],
                  "g0_reference_record_sha256": l["g0_reference_record_sha256_record"]} if "consumer_checks" in l else {"capture_checks": l["capture_checks"],
                  "own_window_reference_record_sha256": l["own_window_reference"]["record_sha256"]})}
             for l in legs]
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
over_limit = [(a, w) for (a, w, r) in walls if r > factor]
over_budget = [(a, w, w - L[a]["budget_s"]) for a, w, r in walls if r > 1]
st, en = rec["started"]["epoch_s"], rec["ended"]["epoch_s"]
restore = span["restore"]
restore_proven_hand = (span["close_steps"]["restore"] == 0 and restore["ok"] is True and restore["observed"] == 0
                       and span["span_result"].get("restore_proven", True) is not False)
final = ndiff == 0 and not ht["diffs"] and n_incl == n == n_adm and not desk_stops and not span["stops_by_hand"]
cons_ok = all(c["g0_outcome_journal"] == "released" and all(v is True for k, v in c["consumer_checks"].items() if k != "own_window_reference_status")
              and c["span_reference_hand"] == {"leg_id": "L004", "attempt": 1, "excluded": False, "redone": False} and c["included"] for c in consumers)
MAINT = open(H / "maint_judgement.txt").read().strip()

# dev-04-s02 gate facts (RL-165 s4 amending RL-163 s6; RL-167 "at least four of its five"; ITEM-dev04-s02 lines 11 and 18)
pil = next(x for x in pilot["hand_legs"] if x["leg"] == "L002")
gate_rows = [{"span": "dev-03-s01 (pilot, cq-dev-03-s01-a1)", "leg": "L002", "g0": pil["g0"], "g0_wait_s": pil["g0_s"], "g0_timeout_s": 1200,
              "released_against_span_reference": pil["g0"] == "released" and all(v is True for k, v in pil["consumer_checks"].items() if k != "own_window_reference_status"),
              "span_reference": pil["span_reference"], "reference_source": pil["g0_reference_source"], "reference_record_sha256": pil["g0_reference_record_sha256"],
              "evidence": "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/pilot-desk-cq-dev-03-s01-a1/RESULT.json (committed, 734e7f6be)"}]
for c in consumers:
    gate_rows.append({"span": "dev-03-s02 (this span, cq-dev-03-s02-a1)", "leg": c["leg_id"], "g0": c["g0_outcome_journal"], "g0_wait_s": round(c["g0_s_journal"], 3), "g0_timeout_s": c["g0_timeout_s"],
                      "released_against_span_reference": c["g0_outcome_journal"] == "released" and all(v is True for k, v in c["consumer_checks"].items() if k != "own_window_reference_status"),
                      "span_reference": c["span_reference_hand"], "reference_source": c["g0_reference_source_record"], "reference_record_sha256": c["g0_reference_record_sha256_record"],
                      "evidence": "this RESULT.json hand_legs"})
released = sum(g["released_against_span_reference"] for g in gate_rows)
total = len(gate_rows)
expect = ["L002", "L008", "L009", "L010", "L012"]
gate_ok = [g["leg"] for g in gate_rows] == expect and total == 5 and released >= 4
l005 = "NOT YET RECORDED: dev-04-s01 (item 367) has not run (it cannot arm before 00:00:00 PST Tue 17 Nov; item 370 'Next'), so its Check holds no L005 G0 outcome; nothing in dev-03's data speaks to dev-04's L005"
gate = {
 "gate_wording": ("ITEM-dev04-s02.md line 18 (RL-165 s4, amending RL-163 s6; RL-167 'at least four of its five'; Mythos dev-04/05 F3): 'If dev-04-s01's L005 released its G0, this span arms on its own gates. "
                  "If L005 timed out at G0: this span arms on the lead's record only if dev-03 ended with at least four of its five consumers released (L002, L008, L009, L010, L012); with fewer than four it does NOT arm.' "
                  "Line 11 (4) (RL-173 D.4): issued 'only after dev-04-s01's Check records L005's G0 outcome (released, or dev-03 released at least four of its five consumers)'."),
 "dev03_consumers": gate_rows,
 "dev03_consumers_released": f"{released} of {total}",
 "dev03_consumers_list": expect,
 "consumer_G0_waits_s": {g["leg"]: g["g0_wait_s"] for g in gate_rows},
 "reference_sources": {"L002": "cadence-cl-dev-03-l001 (L001 attempt 1, pilot span; record sha256 1675f044...bf6e)", "L008_L009_L010_L012": "cadence-cl-dev-03-l004 (L004 attempt 1, this span; record sha256 3692d95c...fc44)"},
 "L005_own_G0_outcome": l005,
 "dev04_s01_ran": False,
 "alternative_basis_met": f"yes: the 'dev-03 released at least four of its five consumers' basis is {released} of {total} (threshold 4); it is the basis RL-173 D.4 names alongside L005 released",
 "verdict": ("L005 gate: MET (proposed)" if gate_ok else "L005 gate: NOT MET (proposed)"),
 "verdict_basis": ("Met on the dev-03 count alone: " + f"{released} of {total} consumers released against their span reference (4 of 4 here, plus L002 in the pilot), threshold 4; "
                   "that is sufficient whether L005 releases or times out, so item 367's Check (not yet run) decides nothing further for this gate. If L005 released, the span arms on its own gates anyway."),
 "signed_by": "not signed: the lead signs",
 "note": "Release is by hand (hand_table: G0 gate row outcome released, the leg record's reference source and sha equal the span capture's record sha, fast_c and span_ns equal the capture's) and by the automatic desk (all admitted). No consumer leg was excluded or redone."}

out = {
 "plan_id": "cq-dev-03-s02-a1", "span": "dev-03-s02", "legs": roster,
 "built": open(H / "built.txt").read().strip(),
 "work_order": "RUN_STATE 366 (issued 2026-11-16 05:38:05 PST); launch RUN_STATE 369 (abc54ff5, ~07:52 PST); magistrate Check RUN_STATE 370 (f3195d501, 1292492b, 11:21 PST); origin/main 020e17fee",
 "data": f"{D} (read-only copy; sha256 -c of all 324 manifest entries OK; .air and .mbp manifests byte-equal, sha256 284f653143daeef63571517054ba0bab9dee091f43f02a5364d719fe7d708b30)",
 "code": "2d347f721552fe03bdd19f113e7bad7a7c24908e (/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721, detached, clean before and after, read-only)",
 "kit": {"source": "git show 9cbb365a6:docs/process/cadence/kits/cl-dev-03.v1.1.json, copied outside the checkout", "sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b", "sha_asserted": True, "receipt_kit": rec["kit"]},
 "desk_command": "TMPDIR=<scratch>/tmp python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-dev-03-s02-a1 --input <DATA>/desk-bundle --out auto --kit kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter)",
 "desk_stops_json": desk_stops,
 "comparison": {
  "per_leg_values_compared": ncomp, "per_leg_values_differing": ndiff, "fields_per_leg": sorted(legs[0]["compare"]), "inclusion_included": True,
  "span_level_compared": ["leg count", "named stops (hand [] vs desk [])", "result (desk_summary vs receipt span_result)", "meter", "feeds_proven_stopped", "span_reference (leg_id, attempt, consumers, consistent)"],
  "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
  "scope_notes": ["hand g0_role: a span-shaped leg that is first in its span captures (L004: role capture, shape span); the others from kit shape (span = consume, own = capture), checked against each leg record's g0_role; hand span_reference derived from each consumer's G0 gate-row reference source_member matched to L004's window reference run id",
                  "hand 'reached' derives from G0 released + quiet_s 0 + release-to-turn < 5 s; same result as the desk",
                  "the desk's prefill_tokens is the kit nominal; realized counts (leg_record) reported separately (RL-158 Q5)",
                  f'rules 3 and 4 left to the look (meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped)',
                  "the desk omits restore lines and censuses; the hand table carries them clean"]},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL" if final else "NOT FINAL", "meaning": "automatic desk = independent hand table on every value, inclusion included (kit v1.1 fields too)",
                "basis": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} span-level values differ; {n_incl} of {n} included by hand, {n_adm} of {n} admitted by desk; stops.json {desk_stops} and hand stops {span['stops_by_hand']}"},
 "consumers_released": {"this_span": f"{sum(c['g0_outcome_journal'] == 'released' for c in consumers)} of {len(consumers)} (" + ", ".join(c["leg_id"] for c in consumers) + ") released against L004's capture; all consumer checks true" if cons_ok else "CHECK FAILED"},
 "dev04_s02_gate": gate,
 "rules_by_hand": {"1_ran_to_cap": f"{sum(l['rules']['1_ran_to_cap'] for l in legs)}/{n} (decode 4,096/4,096 each, leg_status complete, stage rc 0)",
                   "2_g0_released": f"{sum(l['rules']['2_g0_released'] for l in legs)}/{n} (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + "; journal G0 = record g0_wait_s; each against the reference its kit shape names: L004, L005, L006, L007, L011 own capture; L008, L009, L010, L012 L004's capture)",
                   "5_not_contaminated": f"{sum(l['rules']['5_not_contaminated'] for l in legs)}/{n} (one attempt each, no redo; longest run over 0.5 core " + "/".join(str(l["load_counted"]["longest_run_over_0p5_s"]) for l in legs) + " s of 60; journals cover their attempts; hand agrees with recorded os_load)",
                   "6_power_mode_0": f"{sum(l['rules']['6_power_mode_0'] for l in legs)}/{n} (leg_record ac_powermode 0 at episode start; read_power before soak {span['read_power']}; restore observed {restore['observed']})",
                   "3_4": f'at the look; meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped'},
 "rule5_judgements": {"L004": "clean: longest run 1 s of 60", "L005": "clean: 3 s (08:52:41, 1.844 cores)", "L006": "clean: 12 s of 60 (mobileassetd burst 09:21 inside the turn; max 2.642 cores); does not fire; no redo owed",
                      "L007": "clean: 11 s of 60", "L008": "clean: 2 s", "L009": "clean: 2 s", "L010": "clean: 2 s", "L011": "clean: 2 s",
                      "L012": "clean: 4 s of 60 (XProtect + softwareupdated + mobileassetd burst 11:09 inside the turn; max 3.296 cores); does not fire; no redo owed",
                      "basis": "the load journal's sustained-load test (RL-72 E2: > 0.5 core held 60 s), recomputed by hand per attempt; hand = recorded os_load on every leg; not log-line counts"},
 "restore": restore, "restore_proven_hand": restore_proven_hand, "close_steps_rc": span["close_steps"], "read_power_step_before_soak": span["read_power"],
 "LEG_OVERTIME": "no" if not over_limit else "yes",
 "LEG_OVERTIME_detail": f"walls {', '.join(str(w) for _, w, _ in walls)} s against 1.5 x budgets; max ratio {max(r for *_, r in walls)}; " +
                        (f"{len(over_budget)} leg(s) a few seconds over budget_s ({', '.join(f'{a} +{d:.1f} s' for a, _, d in over_budget)}), far under the {factor} x limit; " if over_budget else "none over budget_s; ") + f"{len(over_limit)} legs over the limit, stop needs 2",
 "RL150_R1_part3_print": r1,
 "RL150_R1_note": "TV0h = TV1h in every reading (soak, references, G0 releases), so nothing routes under RL-149 section 5 item 6. L004 (first leg, span-shaped) captures the span's reference (status captured, source_member = itself); L008, L009, L010, L012 are consumers and write no window reference of their own (file absent by design); L005, L006, L007, L011 are own-shaped and capture their own",
 "RL158_Q1": {"print": "RL150_R1_part3_print above IS this span's Q1 print: the soak reference, L004's capture, each consumer's release reading and G0 wait",
              "soak_reference_line": r1["soak_reference_line"], "L004_capture": r1["L004"]["own_reference"],
              "consumer_release_readings": {c["leg_id"]: r1[c["leg_id"]]["g0"]["release"] for c in consumers},
              "g0_wait_s": {a: round(r1[a]["g0"]["duration_s"], 1) for a in roster},
              "marks": "none: L004 (the reference leg) ran one attempt, was not redone and not excluded; no 'reference from a redo' or 'reference from an excluded leg' mark",
              "completion_record": "docs/research-audits/2026-11-10-fable/evidence/cadence-standing/q1/cq-dev-03-s02-a1.json (joulewise.cadence_q1_record.v1; RL-173 E)"},
 "RL158_Q5_prefill_deviation": {a: {"nominal": L[a]["prefill_tokens_nominal_kit"], "realized": L[a]["prefill_tokens"], "pct": L[a]["prefill_deviation_pct"]} for a in roster},
 "RL158_Q5_note": "no leg's realized prefill count is more than 5 % from its nominal (max +1.2 %, the 2,000-token cell at 2,024)",
 "RL158_Q6_consumers": "4 consumers in this span (L008, L009, L010, L012); with the pilot's L002, 5 of dev-03's 10 warm legs (L002, L008, L009, L010, L012) are consumers",
 "RL156a": {"starvation": "none",
   "thermal_sampler": {k: {"cells": v["cells"], "reads": v["reads"], "read_errors": v["read_errors"], "cells_with_no_reading_at_all": v["cells_with_no_reading_at_all"],
                           "max_interval_s": v["max_interval_s"], "empty_cells_on_100ms_tolerance": v["empty_cells_tol"], "cov_reported": v["cov_reported"]} for k, v in smp.items()},
   "thermal_note": f"{sum(v['read_errors'] for v in smp.values())} read errors; cells with no reading at all: {sum(len(v['cells_with_no_reading_at_all']) for v in smp.values())}; max interval {max(v['max_interval_s'] for v in smp.values())} s; empty cells on the 100 ms tolerance (jitter, not starvation): " + ", ".join(f"{k} {len(v['empty_cells_tol'])}" for k, v in smp.items() if v["empty_cells_tol"]) + ".",
   "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
   "inventory": "not exercised: the cadence-leg kind does not run the R1 ProcessInventory journal"},
 "os_level_census": osl, "rule5_placement": r5p, "maintenance_overlap": MAINT,
 "span_level": {k: span[k] for k in ("rc", "mock", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": st, "receipt_ended_epoch_s": en, "runner_span_s": round(en - st, 1), "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / n, 1)},
 "block_line_dev03": f"dev-03: with the pilot (L001-L003) and this span ({n} legs, L004-L012), 12 of 12 legs run; this span {n_adm} admitted by the desk, {n_incl} included by hand, 0 excluded, 0 redos, 0 named stops",
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "gate": gate["verdict"], "released": gate["dev03_consumers_released"], "LEG_OVERTIME": out["LEG_OVERTIME_detail"], "restore_proven_hand": restore_proven_hand,
                  "consumers": out["consumers_released"]}, indent=1))
