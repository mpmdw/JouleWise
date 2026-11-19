"""Assemble RESULT.json for a dev-05 desk (cq-dev-05-s01-a2 or cq-dev-05-s02-a1, kit cl-dev-05.v1.1) from hand/ outputs.

Adapted from desk-cq-dev-03-s02-a1's build_result.py (no dev-04-s02 gate section) with desk-cq-dev-04-s01-a1's redo
evidence (rejected attempt placement via rule5_place_a1.out). Adds: the Check agreement (RUN_STATE 436 / 437 values,
typed in below from the committed items), the seeded hand-sample draw record (row7-reconcile-1119/draw.json), and the
reference-window clock placement (ref_window_place.out). No new tolerance; the comparison is hand_table.py's.
Usage: python3 -I -B build_result.py DESK_DIR DATA_DIR PLAN_ID SPAN_ID ATTEMPT DRAW_JSON
"""
import json, sys
from pathlib import Path
T, D, PLAN, SPAN, ATT, DRAW = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), Path(sys.argv[6])
H = T / "hand"
ht = json.loads((H / "hand_table.json").read_text())
ds = json.loads((T / "auto" / "desk_summary.json").read_text())
desk_stops = json.loads((T / "auto" / "stops.json").read_text())
rec = json.loads((D / "runner_receipt.json").read_text())
kit = json.loads((T / "kit.json").read_text())
span = ht["span"]
legs = ht["legs"]
L = {l["leg_id"]: l for l in legs}
roster = rec["roster"]
first = roster[0]


def lines(name):
    out = {}
    p = H / name
    if not p.is_file():
        return out
    for l in p.read_text().splitlines():
        if l.strip():
            k, _, v = l.partition(" ")
            out[k] = json.loads(v)
    return out


r1 = {}
for l in (H / "r1print.out").read_text().splitlines():
    if l.startswith("soak_reference"):
        r1["soak_reference_line"] = l
    elif l.strip():
        k, _, v = l.partition(" "); r1[k] = json.loads(v)
smp, osl, r5p, r5a1, refw = (lines(n) for n in ("sampler.out", "oslevel.out", "rule5_place.out", "rule5_place_a1.out", "ref_window_place.out"))
factor = kit["stop_rules"]["leg_time_factor"]
ncomp = sum(len(l["compare"]) for l in legs)
ndiff = sum(1 for l in legs for c in l["compare"].values() if not c["agree"])
n = len(legs); n_incl = sum(l["included"] for l in legs); n_adm = sum(a["admitted"] for a in ds["legs"])
consumers = [l for l in legs if l["g0_role_hand"] == "consume"]
redone = [l for l in legs if l["contaminated_redos"] > 0]
hand_legs = [{"leg": l["leg_id"], "attempts": l["attempts"], "g0": l["g0_outcome_journal"], "g0_s": round(l["g0_s_journal"], 3),
              "g0_role": l["g0_role_hand"], "g0_shape": l["g0_shape_hand"], "span_reference": l["span_reference_hand"],
              "prefill_tokens_realized": l["prefill_tokens"], "prefill_tokens_nominal": l["prefill_tokens_nominal_kit"], "prefill_deviation_pct": l["prefill_deviation_pct"],
              "decode": f'{l["decode_tokens"]}/{l["decode_cap"]}', "leg_status": l["leg_status"], "wall_s": round(l["wall_s_stage"], 1),
              "budget_s": l["budget_s"], "leg_record_ac_powermode": l["ac_powermode"],
              "rule5_longest_run_over_0p5_core_s": l["load_counted"]["longest_run_over_0p5_s"], "rule5_max_busy_cores": round(l["load_counted"]["max_cores"], 3),
              "redo": l["redo"], "os_level_max_turn": l["os_level_max_turn"], "pm_nominal_turn": l["pm_nominal_turn"], "included": l["included"], "rules": l["rules"],
              **({"consumer_checks": l["consumer_checks"], "g0_reference_source": l["g0_reference_source_record"],
                  "g0_reference_record_sha256": l["g0_reference_record_sha256_record"]} if "consumer_checks" in l else {"capture_checks": l["capture_checks"],
                  "own_window_reference_record_sha256": l["own_window_reference"]["record_sha256"]})}
             for l in legs]
walls = [(l["leg_id"], round(l["wall_s_stage"], 1), round(l["wall_s_stage"] / l["budget_s"], 4)) for l in legs]
over_limit = [(a, w) for (a, w, r) in walls if r > factor]
over_budget = [(a, w, w - L[a]["budget_s"]) for a, w, r in walls if r > 1]
restore = span["restore"]
restore_proven_hand = span["close_steps"]["restore"] == 0 and restore["ok"] is True and restore["observed"] == 0
final = ndiff == 0 and not ht["diffs"] and n_incl == n == n_adm and not desk_stops and not span["stops_by_hand"]
cons_ok = all(c["g0_outcome_journal"] == "released" and all(v is True for k, v in c["consumer_checks"].items() if k != "own_window_reference_status")
              and c["span_reference_hand"] == {"leg_id": first, "attempt": 1, "excluded": False, "redone": False} and c["included"] for c in consumers)
MAINT = (H / "maint_judgement.txt").read_text().strip()

# The magistrate's Check (separate code), values as committed in RUN_STATE on origin/main (436 for s01-a2, 437 for s02)
CHECK = {"cq-dev-05-s01-a2": {"item": 436, "g0_s": {"L001": 237.6, "L002": 146.9, "L003": 210.1, "L004": 148.8, "L005": 212.2, "L006": 218.3},
                              "roles": {"L001": "capture", "L002": "consume", "L003": "consume", "L004": "capture", "L005": "consume", "L006": "consume"},
                              "redos": 1, "soak_TV0h": 34.000, "meter_polls": 49346, "manifest": "35c11dfe778bdd2bf750055bad9d9eca577448e35c01f3fef39a965fb4be0858"},
         "cq-dev-05-s02-a1": {"item": 437, "g0_s": {"L007": 206.0, "L008": 143.7, "L009": 227.4, "L010": 142.7, "L011": 207.2, "L012": 221.4},
                              "roles": {"L007": "capture", "L008": "consume", "L009": "capture", "L010": "capture", "L011": "capture", "L012": "consume"},
                              "redos": 0, "soak_TV0h": 34.012, "meter_polls": 44307, "manifest": "c6ab586e5146d739046f29ff2da16b830e2d5c718c0050c8790341dbcb7f43f2"}}[PLAN]
soak_tv0h = float(r1["soak_reference_line"].split("'TV0h': ")[1].split(",")[0])
chk = {"g0_s_rounded_equal": all(round(L[k]["g0_s_journal"], 1) == v for k, v in CHECK["g0_s"].items()),
       "roles_equal": all(L[k]["g0_role_hand"] == v for k, v in CHECK["roles"].items()),
       "redos_equal": sum(l["contaminated_redos"] for l in legs) == CHECK["redos"],
       "soak_reference_equal_3dp": round(soak_tv0h, 3) == CHECK["soak_TV0h"],
       "meter_polls_equal": span["meter"]["polls"] == CHECK["meter_polls"]}
check_agreement = {"item": CHECK["item"], **chk, "all": all(chk.values()),
                   "note": "the Check is the magistrate's close script (separate code); values typed from RUN_STATE on origin/main"}

draw = next(x for x in json.loads(DRAW.read_text()) if x["span_id"] == SPAN)
mandatory = []
if redone:
    mandatory.append("redo (" + ", ".join(f'{l["leg_id"]} {l["redo"]}' for l in redone) + ")")
if any(not l["included"] for l in legs):
    mandatory.append("exclusion")
soaks = [s for s in span["step_names"] if s.startswith("soak")]
if soaks != ["soak"]:
    mandatory.append(f"retried soak ({soaks})")
first_of_group = SPAN == "dev-05-s01"
sample = {"law": "sha256-hand-sample-v3", "seed": 2026111501, "rate": 4, "stratum": {"kit_sha256": draw["kit_sha256"], "shape": draw["shape"]},
          "value": draw["value"], "hash_selected": draw["hash_selected"],
          "first_of_group": first_of_group,
          "first_of_group_basis": ("dev-05-s01 is the first span of (cl-dev-05.v1.1, span) that ran; a1 (cq-dev-05-s01-a1-20261118T082155Z) was a zero-capture refusal of the same span id (0 of 6 legs), which keeps 'first' (desk_final.hand_sample: an earlier attempt of the same span is not another span of the group)"
                                   if first_of_group else "not first: dev-05-s01 (same group) ran before it"),
          "mandatory_triggers": mandatory, "schema_change": "no: same kit schema (joulewise.cadence_campaign_kit.v1.1) and leg-field set as dev-04's v1.1 summaries",
          "selected": first_of_group or draw["value"] == 0 or bool(mandatory),
          "hand_table_supplied": True}
sample["why"] = ("drawn: " + ", ".join(x for x in (["first of group"] if first_of_group else []) + (["hash value 0"] if draw["value"] == 0 else []) + mandatory)
                 if sample["selected"] else f"undrawn by the law (hash value {draw['value']}, not first of group, no redo/exclusion/retried soak/schema change); hand table supplied anyway (the lead's selection, --hand-sample, if the lead adopts it)")

q1_marks = (f"none: {first} (the span reference) ran one attempt, was not redone and not excluded; no 'reference from a redo' or 'reference from an excluded leg' mark"
            + ("; L004 is own-shaped and its counted attempt a2 captured its OWN reference after the cpu_load redo (record sha256 "
               + L["L004"]["own_window_reference"]["record_sha256"] + "); no consumer reads it" if "L004" in L and L["L004"]["contaminated_redos"] else ""))
out = {
 "plan_id": PLAN, "span": SPAN, "attempt": ATT, "legs": roster,
 "built": (H / "built.txt").read_text().strip(),
 "work_order": {"cq-dev-05-s01-a2": "items 393 (issue), 427 (a1 pre-launch), 429 (a1 zero-capture refusal; a2 rerun_of a1 under Ed's 2026-09-16 retry ruling), 436 (a2 Check, magistrate 4ad54659); origin/main",
                "cq-dev-05-s02-a1": "items 394 (issue), 430 (re-issue), 436 (Start and check, launch), 437 (Check, magistrate 6de5b183); origin/main"}[PLAN],
 "data": f"{D} (read-only Air copy; shasum -a 256 -c of every .mbp.SHA256SUMS entry OK; .air and .mbp manifests list the same entries (sorted-equal), sha256 of .mbp = {CHECK['manifest']}, equal to the Check's manifest hash)",
 "code": "2d347f721552fe03bdd19f113e7bad7a7c24908e (/Volumes/JW-EXT/jw-wt/desk-pin-2d347f721-1119, detached, git status empty before and after)",
 "kit": {"source": "git show fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-05.v1.1.json, copied outside the checkout (kit.json)",
         "sha256": "2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a", "sha_asserted": True, "receipt_kit": rec["kit"]},
 "desk_command": f"TMPDIR=<desk>/tmp python3.13 -B scripts/air/cadence_desk.py build --plan-id {PLAN} --input <DATA>/desk-bundle --out <desk>/auto --kit <desk>/kit.json (rc 0, 'stops 0'; WITH --kit, never --adapter; default lock)",
 "desk_stops_json": desk_stops,
 "comparison": {"per_leg_values_compared": ncomp, "per_leg_values_differing": ndiff, "fields_per_leg": sorted(legs[0]["compare"]),
                "span_level_differing": len(ht["diffs"]), "diffs": ht["diffs"],
                "scope_notes": ["comparison code is desk-cq-dev-03-s02-a1's hand_table.py, unchanged (header and kit name only); G0 s to 6 dp, wall to 1 dp, else equality",
                                "hand g0_role from kit shape with the first-leg rule; span_reference from each consumer's G0 gate-row reference source matched to the capture's window reference run id",
                                "the desk's prefill_tokens is the kit nominal; realized counts reported separately (RL-158 Q5)",
                                f'rules 3 and 4 left to the look (meter present, {span["meter"]["polls"]:,} polls, {span["meter"]["bad_polls"]} bad, {span["meter"]["usb_errors"]} usb, proven stopped)']},
 "hand_legs": hand_legs,
 "desk_final": {"verdict": "FINAL" if final else "NOT FINAL", "status": "PROPOSED (the lead signs)",
                "meaning": "automatic desk = independent hand table on every value, inclusion included (kit v1.1 fields too)",
                "basis": f"{ndiff} of {ncomp} per-leg and {len(ht['diffs'])} span-level values differ; {n_incl} of {n} included by hand, {n_adm} of {n} admitted by desk; stops.json {desk_stops} and hand stops {span['stops_by_hand']}"},
 "consumers_released": (f"{sum(c['g0_outcome_journal'] == 'released' for c in consumers)} of {len(consumers)} (" + ", ".join(c["leg_id"] for c in consumers)
                        + f") released against {first}'s capture (attempt 1); all consumer checks true") if cons_ok else "CHECK FAILED",
 "redo": ({l["leg_id"]: {"attempts": [{"attempt": a["attempt"], "output_dir": a["output_dir"], "recorded_contaminated": a["recorded"]["contaminated"],
                                       "redo_reason": a["recorded"]["redo_reason"], "hand_longest_run_s": a["hand_load"]["longest_run_over_0p5_s"],
                                       "hand_fires": a["hand_load"]["fires"], "hand_max_cores": round(a["hand_load"]["max_cores"], 3),
                                       "coverage_ok": a["hand_load"]["coverage_ok"], "hand_agrees_with_record": a["hand_agrees_with_record"]} for a in l["attempt_detail"]],
                         "verdict": "correct redo: a1 fires by hand and was recorded contaminated/redone; the counted attempt is clean by hand and by record"}
          for l in redone} or "none"),
 "redo_quota": f'{span["load_redos_used"]} used of quota {span["redo_quota_kit"]} (contaminated_redos stop at {kit["stop_rules"]["contaminated_redos_max"]})',
 "rules_by_hand": {"1_ran_to_cap": f"{sum(l['rules']['1_ran_to_cap'] for l in legs)}/{n}",
                   "2_g0_released": f"{sum(l['rules']['2_g0_released'] for l in legs)}/{n} (" + ", ".join(f'{l["leg_id"]} {l["g0_s_journal"]:.1f} s' for l in legs) + ")",
                   "5_not_contaminated": f"{sum(l['rules']['5_not_contaminated'] for l in legs)}/{n} (longest run over 0.5 core, counted attempts: " + ", ".join(f'{l["leg_id"]} {l["load_counted"]["longest_run_over_0p5_s"]}' for l in legs) + " s of 60)",
                   "6_power_mode_0": f"{sum(l['rules']['6_power_mode_0'] for l in legs)}/{n} (read_power before soak {span['read_power']}; restore observed {restore['observed']})",
                   "3_4": "at the look"},
 "restore": restore, "restore_proven_hand": restore_proven_hand, "close_steps_rc": span["close_steps"], "read_power_step_before_soak": span["read_power"],
 "LEG_OVERTIME": "no" if len(over_limit) < 2 else "yes",
 "LEG_OVERTIME_detail": f"max wall/budget {max(r for *_, r in walls)}; " + (", ".join(f"{a} +{d:.1f} s" for a, _, d in over_budget) + " over budget_s; " if over_budget else "")
                        + f"{len(over_limit)} legs over the {factor} x limit, stop needs 2",
 "RL150_R1_part3_print": r1,
 "RL158_Q1": {"print": "hand/r1print.out: soak reference, the span capture, each consumer's release reading and G0 wait (thermal sensor readings only)",
              "soak_reference_line": r1["soak_reference_line"], f"{first}_capture": r1[first]["own_reference"],
              "consumer_release_readings": {c["leg_id"]: r1[c["leg_id"]]["g0"]["release"] for c in consumers},
              "g0_wait_s": {a: round(r1[a]["g0"]["duration_s"], 1) for a in roster},
              "marks": q1_marks,
              "reference_window_clock": refw,
              "completion_record_draft": f"q1/{PLAN}.json -> docs/research-audits/2026-11-10-fable/evidence/cadence-standing/q1/{PLAN}.json (joulewise.cadence_q1_record.v1; RL-173 E)"},
 "RL158_Q5_prefill_deviation": {a: {"nominal": L[a]["prefill_tokens_nominal_kit"], "realized": L[a]["prefill_tokens"], "pct": L[a]["prefill_deviation_pct"]} for a in roster},
 "RL156a": {"thermal_sampler": smp, "load_sampler": {l["leg_id"]: {"samples": l["load_counted"]["samples"], "max_gap_s": round(l["load_counted"]["max_gap_s"], 3), "coverage_ok": l["load_counted"]["coverage_ok"]} for l in legs},
            "thermal_note": f"{sum(v['read_errors'] for v in smp.values())} read errors; cells with no reading at all: {sum(len(v['cells_with_no_reading_at_all']) for v in smp.values())}; max interval {max(v['max_interval_s'] for v in smp.values())} s"},
 "os_level_census": osl, "rule5_placement": r5p, "rule5_placement_rejected_a1": r5a1 or None, "maintenance_overlap": MAINT,
 "check_agreement": check_agreement,
 "hand_sample": sample,
 "span_level": {k: span[k] for k in ("rc", "mock", "batch_windows", "soak_rc", "agent_census", "deadlines_files", "load_redos_used", "feeds_proven_stopped", "meter", "stages_unclosed", "stages_end_rc_nonzero", "steps_nonzero", "n_steps", "legs_finished", "legs_planned")},
 "span_level_extra": {"soak_s": round(span["soak_s"], 1), "soak_steps": soaks, "volume_census": f'{sum(v[0] == "PASS" for v in span["volume_census"])}/{len(span["volume_census"])} PASS', "redo_quota_kit": span["redo_quota_kit"]},
 "time_calendar_only": {"receipt_started_epoch_s": rec["started"]["epoch_s"], "receipt_ended_epoch_s": rec["ended"]["epoch_s"], "mean_leg_wall_s": round(sum(w for _, w, _ in walls) / n, 1)},
}
(T / "RESULT.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"final": out["desk_final"], "consumers": out["consumers_released"], "check": check_agreement["all"], "sample": sample["why"],
                  "overtime": out["LEG_OVERTIME_detail"], "restore": restore_proven_hand}, indent=1))
