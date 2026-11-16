"""STANDING-F0 run 1 (b2e01464d) vs the previous Part C (item 325/328, c3f4bacd8), line by line (item 346 rule 10): evaluation
lines, then the desk tables' thermal prints. The second Part C's compare_runs.py (partc2-c3f4-desk, c9fc0339d) with the run
labels changed and one block added: the categorical desk rows (counts, clauses, picks, flags) compared and any difference listed.
Earlier header: Second Part C vs the first, line by line (RL-155a §1.2): evaluation lines, then the desk tables' thermal prints.
Reads only the two recorded_eval.json (item Check prints) and the two desk JSONs. Usage:
  python3 -I -B compare_runs.py RUN2_EVAL RUN1_EVAL RUN2_DESK RUN1_DESK
"""
import json
import sys

e2, e1, d2, d1 = (json.load(open(p)) for p in sys.argv[1:5])
out = {"verdict": [e2["evaluation"]["verdict"], e1["evaluation"]["verdict"]],
       "lines": {k: [e2["evaluation"]["lines"][k]["pass"], e1["evaluation"]["lines"][k]["pass"]]
                 for k in sorted(set(e2["evaluation"]["lines"]) | set(e1["evaluation"]["lines"]))},
       "log": [e2["evaluation"]["log"], e1["evaluation"]["log"]],
       "admitted_turns": [e2["evaluation"]["lines"]["d_bank_mechanics"]["checks"]["admitted_turns"].get("status"),
                          e1["evaluation"]["lines"]["d_bank_mechanics"]["checks"]["admitted_turns"].get("status")],
       "gate_time_s/limit_s": [[round(e["evaluation"]["lines"]["d_bank_mechanics"]["checks"]["gate_time"][k], 2)
                               for k in ("gates_plus_holds_s", "limit_s")] for e in (e2, e1)],
       "N_chunk": [e2["N_chunk"], e1["N_chunk"]], "T_dead_s": [round(e2["T_dead_s"], 2), round(e1["T_dead_s"], 2)]}
out["lines_differ"] = sorted(k for k, (a, b) in out["lines"].items() if a != b) + \
    (["verdict"] if out["verdict"][0] != out["verdict"][1] else [])


def desk(d):
    g = d["gates"]
    sd = d["step_D"]
    t = sd["turn"]
    bank = d["row6"]["D_bank"]
    return {"gates_released": f"{sum(x['outcome'] == 'released' for x in g)}/{len(g)}",
            "gates_release_sample_L0_Nominal_fresh": f"{sum(bool(x['exit_ok_2s']) for x in g)}/{len(g)}",
            "replay_agrees": f"{sum(x['replay_agrees'] for x in g)}/{len(g)}",
            "step_D_G0_s/clause": [round(sd["g0"]["duration_s"], 2), sd["g0"]["clause_last"]],
            "step_D_turn_s": t["turn_s"], "step_D_level1_s": t["first_level1_s"], "step_D_level2_s": t["first_level2_s"],
            "step_D_max_TV0h": round(t["max_TV0h"], 2),
            "step_D_p7_level0_x5_s": sd["p7"]["level0_x5_s"], "step_D_p7_band_1C_x5_s": sd["p7"]["band_1C_x5_s"],
            "classifier_free_pick": [sd["p4_meta"]["s_fast"], sd["p4_meta"]["s_slow"]],
            "night_confirmation": [sd["p4_meta"]["night_confirmation"]["s_fast"], sd["p4_meta"]["night_confirmation"]["s_slow"],
                                   sd["p4_meta"]["night_confirmation"]["ok"]],
            "D_bank_G0+G1_s": [round(x["duration_s"], 2) for x in g if x["member"] == "D_bank"],
            "D_bank_turn1_first_off_s": bank["turns"][1]["first_off"]["s_from_start"] if bank["turns"][1]["first_off"] else None,
            "D_bank_exclusion_1Hz": bank["exclusion_reasons_1Hz"],
            "D_bank_stale_after_turn1": bank["turns"][1]["stale_after_end"],
            "X_G_turns_all_L0_Nominal": all(x["os_nominal_1Hz"] and x["pm_nominal_1Hz"] for x in d["row6"]["X_G"]["turns"]),
            "G1_after_hot_turn": {m: d["row6"][m]["g1_after_hot_turn"] for m in d["row6"]},
            "TV_unequal_rows (member, seq, in gate, look-back)": [(r["member"], r["seq"], r["inside_gate_window"], r["in_lookback_of"])
                                                                  for r in d["tv_trigger_rows"]],
            "soak_TV0h=TV1h": [round(d["soak"]["sensors_c"]["TV0h"], 3), d["soak"]["sensors_c"]["TV0h"] == d["soak"]["sensors_c"]["TV1h"]]}


out["desk"] = {"f0run1_b2e01464d": desk(d2), "partc2_c3f4bacd8": desk(d1)}
CATEGORICAL = ("gates_released", "gates_release_sample_L0_Nominal_fresh", "replay_agrees", "classifier_free_pick",
               "night_confirmation", "D_bank_exclusion_1Hz", "D_bank_stale_after_turn1", "X_G_turns_all_L0_Nominal",
               "G1_after_hot_turn", "TV_unequal_rows (member, seq, in gate, look-back)")
a, b = out["desk"]["f0run1_b2e01464d"], out["desk"]["partc2_c3f4bacd8"]
out["desk_categorical_differ"] = {k: [a[k], b[k]] for k in CATEGORICAL if json.dumps(a[k], default=str) != json.dumps(b[k], default=str)}
out["step_D_G0_clause_differ"] = a["step_D_G0_s/clause"][1] != b["step_D_G0_s/clause"][1]
print(json.dumps(out, indent=1, default=str))
