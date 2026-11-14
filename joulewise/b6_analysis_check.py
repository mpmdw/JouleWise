"""Option (c)'s second side: twins plus a small counting/pairing/§10–11 checker.

No production driver, recompute, reducer or estimator is imported. Decoded
authenticated member inputs are supplied by the caller. The meter-only phase
line is deliberately excluded: R8 calls it single-implementation.
"""
import math
import statistics as stats

from joulewise.twins import engine_twin as engine
from joulewise.twins import harvest_twin as harvest


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def summary(values):
    xs = [x for x in values if finite(x)]
    return {"n": len(xs), "mean": stats.mean(xs) if xs else None,
            "sd": stats.stdev(xs) if len(xs) > 1 else None}


def check_block(sessions, results, lines, block5):
    failures, counts = [], {}
    table = {"schema": "joulewise.b6_comparison_table.v1", "sessions": {}, "block": {"quantities": {}}}

    def check(family, scope, actual, expected, bar=0.000005):
        counts[family] = counts.get(family, 0) + 1
        if finite(actual) and finite(expected):
            same = abs(actual - expected) <= bar
        else:
            same = actual == expected
        if not same:
            failures.append(family + ":" + scope)

    # Tie by the actual loop t0, never by the spelling of a session id.
    ordered = sorted(sessions.values(), key=lambda s: (s.attempt.get("t0", float("inf"))
                                                       if s.attempt else float("inf"), s.session_id))
    for s in ordered:
        r = results[s.session_id]
        q, runs = {}, {}
        table["sessions"][s.session_id] = {"quantities": q, "run_phase_energy_j": runs}
        a = s.acceptance
        counted = a.get("counting") is True and a.get("verdict") == "ACCEPT" and a.get("physics_stop") is not True
        if s.attempt:
            status = s.reharvested.get(s.session_id, s.attempt["outcomes"])[s.pack.lower()]["status"]
            counted = counted and status == "counting"
        check("counting", s.session_id, r["counting"], counted, 0)
        bracket = harvest.calibration_bracket(s.b["b_pre_s"], s.b["b_post_s"], 0.010818)
        q["calibration/b_op_s"] = bracket.operative_fiducial_s
        check("calibration", s.session_id, s.b["b_op_s"], bracket.operative_fiducial_s, 0.5e-6)
        for rid, m in s.members.items():
            if rid not in s.compared_run_ids or not m.usable:
                continue
            rows = [harvest.PowerInterval(*row) for row in m.records]
            runs[rid] = {}
            for phase, (start, end) in m.edges.items():
                energy = harvest.overlap_energy(rows, start, end)
                runs[rid][phase] = energy
                check("harvest_energy", rid + "/" + phase, m.energies.get(phase), energy, 0.001)
                if phase != "request" and end - start > 2 * (s.b["b_op_s"] + m.s + m.m):
                    env = harvest.anchor_envelope(rows, start, end, s.b["b_op_s"], m.s, m.m)
                    check("harvest_bound", rid + "/" + phase, m.op[phase]["max_abs_delta_j"], env.max_abs_delta_j)
        reference = lambda rid: harvest.ReferenceEnergy(
            s.members[rid].energies["request"],
            s.members[rid].energies["request"] - s.members[rid]._rail_idle_power *
            (s.members[rid].edges["request"][1] - s.members[rid].edges["request"][0]))
        if s.neg8["verdict"] != "undefined":
            ids = s.neg8["survivor_ids"]
            twin = harvest.session_drift([reference(x) for x in s.neg8["corpus_ids"]],
                [reference(x) for x in ids if "-start" in x], [reference(x) for x in ids if "-end" in x],
                next((reference(x) for x in ids if "-midpoint" in x), None), block=6)
            q.update({"neg8/allowance_j": twin.gross.allowance_j, "neg8/bound_j": twin.gross.bound_j,
                      "neg8/verdict": "passed" if twin.passed else "failed"})
            for key, expected in q.items():
                check("harvest_drift", s.session_id + "/" + key, r["quantities"].get(key), expected)
        if s.pack == "GAMMA":
            if s.neg8["verdict"] == "undefined":
                # RL-114: no drift allowance, so no engine inputs and no twin call. Guard the word instead.
                for cid, original in r["contrasts"].items():
                    interval = original.get("decision_interval_j")
                    guarded = (original.get("outcome") in ("not_resolvable", "not_estimable")
                               and original.get("D_j") is None
                               and isinstance(interval, (list, tuple)) and list(interval) == [None, None])
                    check("engine_screen_undefined", cid, guarded, True, 0)
            else:
                family, floors = {}, {}
                names = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j",
                         "E_whole_window_drift_allowance_j")
                for cid, selection in r["_selections"].items():
                    phase = "decode" if "decode" in cid else "prefill"
                    blocks = []
                    for uid, members in selection["quad"]:
                        sides = {"a": [], "b": []}
                        for m in members:
                            bounds = dict(zip(names, (m.op[phase]["max_abs_delta_j"], 0.0, s.neg8["allowance_j"] / 2)))
                            sides[m.run_id.rsplit("-", 1)[-1][0]].append(engine.Run(m.energies[phase], bounds=bounds))
                        blocks.append(engine.Block(uid, tuple(sides["a"]), tuple(sides["b"])))
                    family[cid], floors[cid] = blocks, r["contrasts"][cid]["floor_gate_j"]
                twins = engine.family(family, floors)
                # RL-133 §1a: the registered minimum is five quads. A short contrast (two to four) enters the
                # session's Holm family as p = 1.0 on both sides: its p is passed as None and the frozen family
                # size is kept. One path, short contrast or not.
                short = {cid for cid, blocks in family.items() if len(blocks) < 5}
                ruled = engine.adjust({cid: None if cid in short or row["estimate"] is None else row["estimate"].p
                                       for cid, row in twins.items()}, len(twins))
                for cid, row in twins.items():
                    v, original = row["estimate"], r["contrasts"][cid]
                    if v is None:
                        check("engine_refusal", cid, original["outcome"], "not_estimable", 0)
                        continue
                    for key, expected in (("n", v.n), ("dbar_j", v.point), ("s_d_j", v.sd), ("se_j", v.se_total),
                                          ("D_j", sum(v.bounds.values())), ("p", v.p), ("holm_p", ruled[cid])):
                        if cid in short and key in ("p", "holm_p"):
                            continue  # below the minimum these are guarded, not compared (first_program_only)
                        check("engine", cid + "/" + key, original[key], expected)
                        exposed = {"n": "n", "dbar_j": "dbar_j", "D_j": "D_j", "p": "p", "holm_p": "holm_p"}
                        if key in exposed:
                            q["contrast/" + ("decode" if "decode" in cid else "prefill-p2048") + "/" + exposed[key]] = expected
                    for i in (0, 1):
                        check("engine", cid + "/decision", original["decision_interval_j"][i], v.decision[i])
                    if cid in short:
                        # Below the minimum the first program prints p = holm_p = 1.0 and not_estimable.
                        guarded = (original.get("p") == 1.0 and original.get("holm_p") == 1.0
                                   and original.get("outcome") == "not_estimable")
                        check("engine_below_minimum", cid, guarded, True, 0)
                    else:
                        check("engine_word", cid, original["outcome"], engine.outcome(v, floors[cid], ruled[cid]), 0)
            for pack in ("ALPHA", "BETA"):
                candidates = [x for x in ordered if x.pack == pack and results[x.session_id]["counting"]]
                same = [x for x in candidates if x.round == s.round]
                later = sorted([x for x in candidates if x.round > s.round], key=lambda x: (x.round, ordered.index(x)))
                earlier = sorted([x for x in candidates if x.round < s.round], key=lambda x: (-x.round, ordered.index(x)))
                selected = (same or later or earlier or [None])[0]
                rule = ("1_same_round" if same else "2_next_counting" if later else
                        "3_last_earlier_counting" if earlier else "3_floor_from_block_5")
                check("pairing", s.session_id + "/" + pack, r["pairing"][pack]["session_id"],
                      selected.session_id if selected else None, 0)
                check("pairing", s.session_id + "/" + pack, r["pairing"][pack]["rule"], rule, 0)

    for pack, block in lines["between_session"].items():
        counted = [r for r in results.values() if r["pack"] == pack and r["counting"]]
        included = counted + [r for r in results.values() if r["pack"] == pack and not r["counting"] and r["inclusive"]["eligible"]]
        for key, row in block["values"].items():
            base = [block5[key]] if row["block5_included"] else []
            for group, members, actual in (("summary", counted, row),
                                          ("inclusive", included, lines["flagged_inclusive"][pack]["values"][key])):
                expected = summary(base + [r["quantities"].get(key) for r in members])
                for stat, value in expected.items():
                    name = group + "/" + pack + "/" + key + "/" + stat
                    table["block"]["quantities"][name] = value
                    check("section10", name, actual[stat], value)
            b5 = block5.get(key)
            mean = summary([r["quantities"].get(key) for r in counted])["mean"]
            delta = mean - b5 if finite(mean) and finite(b5) else None
            name = "side_by_side/" + pack + "/" + key + "/delta"
            table["block"]["quantities"][name] = delta
            check("section10", name, lines["side_by_side"][pack][key]["delta"], delta)
        check("section11_short", pack, lines["short"][pack]["short"], len(counted) < 3, 0)
    for phase, row in lines["replication"].items():
        key = "contrast/" + phase
        expected = None
        defect = any(r.get("binding_defect") for r in results.values() if r["pack"] == "GAMMA" and r["counting"])
        if block5.get(key + "/outcome") not in (None, "not_estimable") and row["sessions"] and not defect:
            expected = "replicated" if all(
                x["outcome"] == block5[key + "/outcome"] and x["direction"] == block5.get(key + "/direction")
                for x in row["sessions"]) else "not replicated"
        check("section11_replication", phase, row["word"], expected, 0)
        table["block"]["quantities"]["replication/" + phase + "/word"] = expected
    return {"pass": not failures, "families": counts, "failures": failures,
            "comparison_table": table,
            "single_implementation": ["per-phase whole-machine (R8)"]}
