#!/usr/bin/env python3
"""Mutation check for the interim look's fit and CLI (RL-166 item 5): each mutant must be killed by the tests.

    python3 -B tests/cadence/mutants_fit_interim.py [--only N ...]

Works on a private copy of joulewise/, scripts/ and tests/ in a temporary directory; the worktree is never
written. Arithmetic and custody mutants only: no mutant starts, signals or touches any process."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIT = "joulewise/cadence_looks/fit_interim.py"
RUN = "scripts/cadence_look_run.py"
T_FIT = "tests.cadence.test_fit_interim"
T_RUN = "tests.cadence.test_look_run"

# (id, file, old, new, test modules)
MUTANTS = [
    ("R1_decode_N_not_N_minus_1", FIT, 'legs_d[k]["decode_tokens"] - 1 for k in keys)', 'legs_d[k]["decode_tokens"] for k in keys)', [T_FIT]),
    ("R2_n_from_n_tokens", FIT, 'n = float(s["edge_hi"] - s["edge_lo"])', 'n = float(s["n_tokens"])', [T_FIT]),
    ("R3_c_from_tok", FIT, 'c = P + 0.5 * (s["edge_lo"] + 1 + s["edge_hi"])', 'c = P + 0.5 * (s["tok_first"] + s["tok_last"])', [T_FIT]),
    ("start_age_ignored", FIT, 'if ts - r["t_s"] > START_MAX_AGE_S or not r["pm_fresh"]:', 'if not r["pm_fresh"]:', [T_FIT]),
    ("start_fresh_ignored", FIT, 'if ts - r["t_s"] > START_MAX_AGE_S or not r["pm_fresh"]:', 'if ts - r["t_s"] > START_MAX_AGE_S:', [T_FIT]),
    ("tau_out_of_state_not_zero", FIT, 'if L["start"]["state"] == "start_out_of_state":\n        return 0.0', 'if False:\n        return 0.0', [T_FIT]),
    ("tau_no_floor", FIT, '    return max(0.0, linear_predictor(L, model))', '    return linear_predictor(L, model)', [T_FIT]),
    ("step_from_segment_start", FIT, '        return max(0.0, v - max(u, max(0.0, ell)))', '        return max(0.0, v - u)', [T_FIT]),
    ("ramp_without_midpoint", FIT, 'vals.update(k_tf08=d * m * z[0]', 'vals.update(k_tf08=d * z[0]', [T_FIT]),
    ("hot_flag_late", FIT, 'and s["first_token_s"] - turn["turn_start_s"] >= off)', 'and s["first_token_s"] - turn["turn_start_s"] > off + 1.0)', [T_FIT]),
    ("lodo_leaks_heldout_day", FIT, 'train = [k for k in keys_all if by_key[k]["day"] != D]', 'train = list(keys_all)', [T_FIT]),
    ("censored_as_uncensored", FIT, '            y.append(st["censored_at_s"])\n            c.append(True)', '            y.append(st["censored_at_s"])\n            c.append(False)', [T_FIT]),
    ("estimable_at_5", FIT, 'ONSET_MIN_UNCENSORED = 12', 'ONSET_MIN_UNCENSORED = 5', [T_FIT]),
    ("hot_day_needs_1_leg", FIT, 'MIN_HOT_LEGS_PER_DAY = 3', 'MIN_HOT_LEGS_PER_DAY = 1', [T_FIT]),
    ("threshold_3pct", FIT, 'QUALIFIED_THRESHOLD = 0.02', 'QUALIFIED_THRESHOLD = 0.03', [T_FIT]),
    ("unknown_pm_is_off", FIT, 'OK_PM = ("Nominal", "Unknown", None)', 'OK_PM = ("Nominal", None)', [T_FIT]),
    # RL-167
    ("row6_unknown_start_is_out_of_state", FIT, '    return "start_state_unobserved"\n\n\ndef fresh_state', '    return "start_out_of_state"\n\n\ndef fresh_state', [T_FIT]),
    ("row6_unobserved_start_in_onset_fit", FIT, '            elif st["state"] == "start_state_unobserved":       # RL-167 row 6, R-16\n                s["onset_use"] = "left_out_state_unobserved"\n', '', [T_FIT]),
    ("row4_any_fresh_counts", FIT, 'return type(r["os_level"]) is int and r["pm_fresh"] and r["pm_state"] is not None and r["pm_state"] != "Unknown"', 'return r["pm_fresh"]', [T_FIT]),
    ("row5_anchor_first_fresh_reading", FIT, 'first = before[-1]["t_s"] if before and fresh_state(before[-1]) else ts\n    anchors = [first] + ', 'anchors = ([before[-1]["t_s"]] if before and fresh_state(before[-1]) else []) + ', [T_FIT]),
    ("row5_no_floor", FIT, 'return max(0.0, a - ts)', 'return a - ts', [T_FIT]),
    ("row7_fold_needs_12_on_3", FIT, 'if int((~c).sum()) < FOLD_MIN_UNCENSORED or not _two_cells(_unc_by_cell(c, cells), FOLD_MIN_PER_CELL):', 'if not onset_estimable(c, _, cells)[0]:', [T_FIT]),
    ("row8_unconverged_used", FIT, '    if not f["converged"]:\n        return None, info\n', '', [T_FIT]),
    ("row12_pooled_counted_only", FIT, '                num_h += pn - mn                         # RL-167 row 12: pooled over every hot block, every day\n                den_h += mn\n                if len(hk) >= MIN_HOT_LEGS_PER_DAY:\n                    counted.append(D)', '                if len(hk) >= MIN_HOT_LEGS_PER_DAY:\n                    counted.append(D)\n                    num_h += pn - mn\n                    den_h += mn', [T_FIT]),
    ("row16_marked_uses_main_onset", FIT, '                cw = _channel(legs, E, ch, model_keep, active, include=keep)', '                cw = _channel(legs, E, ch, model_main, active, include=keep)', [T_FIT]),
    ("row20_none_key", FIT, '            g = "null" if v is None else str(v)', '            g = str(v)', [T_FIT]),
    ("row21_hp_any_type", FIT, 'if legs_d[k]["included"] and legs_d[k]["leg_type"] == "A") if hp else None', 'if legs_d[k]["included"]) if hp else None', [T_FIT]),
    ("row22_hp_in_level_e", FIT, '    needed = {L["leg_key"]: L for L in legs if L["in_energy_fit"]}', '    needed = {L["leg_key"]: L for L in legs if L["in_energy_fit"] or L["hp_describe"]}', [T_FIT]),
    ("row22_reader_reads_hp", RUN, '        if not L["in_energy_fit"]:                  # RL-167 §3: no hp-01 energy is opened\n            continue', '        if not (L["in_energy_fit"] or L["hp_describe"]):\n            continue', [T_RUN]),
    ("precedence_excluded_first", FIT, '        if leg["leg_type"] == "T":                      # RL-167 §2.1: type T, excluded, describe-only, missing start\n            reason = "type_T"\n        elif not included:\n            reason = "excluded"', '        if not included:\n            reason = "excluded"\n        elif leg["leg_type"] == "T":\n            reason = "type_T"', [T_FIT]),
    ("r18_no_positive_check", FIT, '        if any(v <= 0 for v in meas_leg.values()):', '        if False:', [T_FIT]),
    ("r11_n_days_zero", FIT, '"n_pairs": len(pairs), "n_days": n_days_pairs}', '"n_pairs": len(pairs), "n_days": 0}', [T_FIT]),
    ("r11_sd_floor_dropped", FIT, 'if len(pairs) < 3 or sd_l <= SD_FLOOR_J or sd_s <= SD_FLOOR_J:', 'if len(pairs) < 3:', [T_FIT]),
    ("r11_ci_with_one_day", FIT, '    if nd >= 2:\n        se = ', '    if nd >= 1:\n        se = ', [T_FIT]),
    ("r20_drift_threshold", FIT, 'METER_DRIFT_MAX_S = 0.1', 'METER_DRIFT_MAX_S = 1.0', [T_FIT]),
    ("r20_reader_parses_poll_lines", RUN, '            if _B_KIND.search(line):', '            if _B_KIND.search(line) and json.loads(line):', [T_RUN]),
    # RL-166b
    ("b1_overlap_not_expected", FIT, '    return sigma * (_G((v - ell) / sigma) - _G((u - ell) / sigma))', '    return max(0.0, v - max(u, max(0.0, ell)))', [T_FIT]),
    ("b1_clipped_ell", FIT, 'return {L["leg_key"]: (linear_predictor(L, model), model["sigma"],', 'return {L["leg_key"]: (max(0.0, linear_predictor(L, model)), model["sigma"],', [T_FIT]),
    ("b1_oos_overlap", FIT, '    if oos:\n        return v - u\n    if sigma < SIGMA_MIN_S:', '    if sigma < SIGMA_MIN_S:', [T_FIT]),
    ("b1_G_without_phi", FIT, 'return x * 0.5 * math.erfc(-x / _SQRT2) + math.exp(-0.5 * x * x - _LOG_SQRT_2PI)', 'return x * 0.5 * math.erfc(-x / _SQRT2)', [T_FIT]),
    ("b1_fold_uses_main_sigma", FIT, '                    onsets = _onsets(fit, bo)', '                    onsets = _onsets(fit, dict(bo, sigma=model["sigma"]))', [T_FIT]),
    ("b2_tolerance_inclusive", FIT, 'counts = [sum(1 for d, z in day_z if d != D and abs(z) > tol) for D in days]', 'counts = [sum(1 for d, z in day_z if d != D and abs(z) >= tol) for D in days]', [T_FIT]),
    ("b2_count_includes_day", FIT, 'counts = [sum(1 for d, z in day_z if d != D and abs(z) > tol) for D in days]', 'counts = [sum(1 for d, z in day_z if abs(z) > tol) for D in days]', [T_FIT]),
    ("b2_inactive_kept_in_energy", FIT, '    heat_cols = (list(BASE_COLS) + [HEAT_OF[n] for n in READINGS if active[n]]', '    heat_cols = (list(BASE_COLS) + [HEAT_OF[n] for n in READINGS]', [T_FIT]),
    ("b2_inactive_kept_in_onset", FIT, '    return ["intercept"] + [n for n in READINGS if active[n]] + ["t_p_s"]', '    return ["intercept"] + list(READINGS) + ["t_p_s"]', [T_FIT]),
    ("b3_no_cell_rule", FIT, '          and _two_cells(by_cell, ONSET_MIN_PER_CELL))', '          and True)', [T_FIT]),
    ("b4_no_fold_cell_rule", FIT, 'if int((~c).sum()) < FOLD_MIN_UNCENSORED or not _two_cells(_unc_by_cell(c, cells), FOLD_MIN_PER_CELL):', 'if int((~c).sum()) < FOLD_MIN_UNCENSORED:', [T_FIT]),
    ("b5_no_decrement_check", FIT, 'out["passes"] = bool(cond <= CONV_MAX_COND and dec <= CONV_DECREMENT and math.isfinite(dec))', 'out["passes"] = bool(cond <= CONV_MAX_COND)', [T_FIT]),
    ("b5_no_cond_check", FIT, 'out["passes"] = bool(cond <= CONV_MAX_COND and dec <= CONV_DECREMENT and math.isfinite(dec))', 'out["passes"] = bool(dec <= CONV_DECREMENT and math.isfinite(dec))', [T_FIT]),
    ("b5_no_pd_check", FIT, '    if not ev[0] > 0:\n        return out\n    cond', '    cond', [T_FIT]),
    ("b6_loose_rank", FIT, 'RANK_RTOL = 1e-10 ', 'RANK_RTOL = 1e-14 ', [T_FIT]),
    ("b7_days_3", FIT, 'TRIP = {"dev_included": 45, "days": 4,', 'TRIP = {"dev_included": 45, "days": 3,', [T_FIT]),
    ("p2_se_unpooled", FIT, '                         "se": None if sd_w is None else sd_w / math.sqrt(len(ks))}', '                         "se": None if sd_w is None else sd_w / len(ks)}', [T_FIT]),
    ("p3_offset_from_first_block", FIT, '            o = blocks.index(hot[0])', '            o = 0', [T_FIT]),
    ("p4_le_116", FIT, 'if L["start"]["state"] == "in_state" and off is not None and off < COUNT_ONLY_CUT_FIXED_S:', 'if off is not None and off < COUNT_ONLY_CUT_FIXED_S:', [T_FIT]),
    ("p4_flag_always_false", FIT, '"to_research_lead": onset["status"] == "not_estimable" and n_early > 0}', '"to_research_lead": False}', [T_FIT]),
    # RL-166c
    ("c4_p3_any_off_reading", FIT, '            if L["state"]["onset_use"] != "uncensored":          # RL-166c row 4: the onset sample\'s uncensored legs', '            if L["state"]["first_off_s"] is None:', [T_FIT]),
    ("c5_p3_no_refusal", FIT, '                    if not y[i] > 0:                             # RL-166c row 5, R-18', '                    if False:', [T_FIT]),
    ("r18_hot_no_refusal", FIT, '        if any(v is not None and v <= 0 for v in meas_hot.values()):', '        if False:', [T_FIT]),
    ("f1_kinds_sorted", FIT, '    return t_off - ts, "+".join(k for k in OFF_KINDS if any(x == t_off and w == k for x, w in offs))', '    return t_off - ts, "+".join(sorted(k for x, k in offs if x == t_off))', [T_FIT]),
    ("f2_oos_none_when_not_estimable", FIT, '    if L["start"]["state"] == "start_out_of_state":\n        return 0.0\n    if model is None:\n        return None', '    if model is None:\n        return None\n    if L["start"]["state"] == "start_out_of_state":\n        return 0.0', [T_FIT]),
    # cold seats on 5ea1bdee9
    ('cs_m1_g0_timeout_refuses', RUN, '                if all(inc.values()):\n                    raise F.LookInputError(f"an included leg', '                if True:\n                    raise F.LookInputError(f"an included leg', [T_RUN]),
    ('cs_m7_no_look_mark', RUN, '    if consumers and any(not all(leg["inclusion"].values()) for leg in legs if leg["leg_id"] in supplier_ids):', '    if False:', [T_RUN]),
    ('cs_mn3_own_supplier_unmarked', RUN, '    supplier_ids = suppliers | {leg["leg_id"] for leg in legs if leg["g0_role"] == "capture"}', '    supplier_ids = {leg["leg_id"] for leg in legs if leg["g0_role"] == "capture"}', [T_RUN]),
    ('cs_m13_synthetic_false', RUN, '"synthetic": bool(synth) and all(synth),', '"synthetic": False,', [T_RUN]),
    ('cs_m14_unrun_cell_invented', RUN, '                         "cell_prompt_tokens": None, "g0_role": None,\n                         "inclusion": {r: False for r in F.RULES}, "turn": None})', '                         "cell_prompt_tokens": 2000, "g0_role": None,\n                         "inclusion": {r: False for r in F.RULES}, "turn": None})', [T_RUN]),
    ('cs_m14_validator_r21', FIT, '        if leg["turn"] is None and leg["leg_type"] == "A" and all(leg["inclusion"].values()):', '        if False:', [T_RUN]),
    ('cs_sol2_legacy_type', RUN, 'leg_type = "T" if spec.get("leg_type") == "T" else "A"', 'leg_type = "T" if (spec.get("leg_type") == "T" or spec.get("type") == "T") else "A"', [T_RUN]),
    ('cs_roster_dict', RUN, '    if not isinstance(roster, list):                # one shape', '    if isinstance(roster, dict):\n        roster = roster.get("roster")\n    if not isinstance(roster, list):                # one shape', [T_RUN]),
    ('cs_m4_meter_stub_refuses', RUN, '                del st\n                continue', '                raise F.LookInputError("a meter stream without aligned samples")', [T_RUN]),
    ('cs_m4_no_power_trace_preflight', RUN, '        if not (sdir / "legs" / leg_id / "runtime" / rec["result"]["bundle"] / "power_trace.csv").is_file():', '        if False:', [T_RUN]),
    ('cs_sol8_no_cli_preflight', RUN, '    F.stage2_preflight(s1)                          # refuses before any energy file is opened\n', '', [T_RUN]),
    ('cs_sol8_no_day_check', FIT, '    if len(stage1_out["roster"]["fit_days"]) < 2:', '    if False:', [T_RUN]),
    ('cs_sol3_guard_below_one', FIT, 'if v is not None and not (isinstance(v, float) and math.isfinite(v)):', 'if v is not None and not (isinstance(v, float) and abs(v) < 1.0):', [T_FIT]),
    ("pins_not_checked", RUN, '        _VERIFIED[:] = [(M.verify_pins(a.manifest, ROOT, allow_draft=a.allow_draft, running=RUNNING,\n                                       ledger_ref=getattr(a, "ledger_ref", None)), a.manifest)]\n', '        _VERIFIED[:] = [(json.loads(Path(a.manifest).read_text()), a.manifest)]\n', [T_RUN]),
    ("stage1_commit_not_checked", RUN, '        M.require_stage1_committed(ROOT, F.LOOK_ID, a.stage1_sha256, stage1_doc=s1, ledger_ref=a.ledger_ref)\n', '        pass\n', [T_RUN]),
    ("level_off_requires_fresh", FIT, 'if ts < r["t_s"] <= tl and type(r["os_level"]) is int and r["os_level"] > 0:', 'if ts < r["t_s"] <= tl and type(r["os_level"]) is int and r["os_level"] > 0 and r["pm_fresh"]:', [T_FIT]),
    ("cluster_by_day", FIT, '            g += [k] * len(L["segments"])', '            g += [L["day"]] * len(L["segments"])', [T_FIT]),
    ("no_cr1_factor", FIT, 'corr = (G / (G - 1)) * ((n - 1) / (n - k)) if G > 1 and n > k else 1.0', 'corr = 1.0', [T_FIT]),
    ("bias_sign_flipped", FIT, 'diffs = [(d, rl / sd_l - rs / sd_s) for (_, d, rl, rs) in pairs]', 'diffs = [(d, rs / sd_s - rl / sd_l) for (_, d, rl, rs) in pairs]', [T_FIT]),
    ("fold_keeps_delta", FIT, 'fold_cols = [c for c in cols if c != DELTA_COL]', 'fold_cols = cols', [T_FIT]),
    ("no_hash_gate", FIT, 'if hashlib.sha256(dump(stage1_out)).hexdigest() != stage1_sha256:', 'if False:', [T_FIT]),
    ("no_output_check", FIT, '    output_check(out)\n    return out', '    return out', [T_FIT]),
    ("energy_input_hash_unchecked", FIT, 'if energy["input_sha256"] != stage1_out["input_sha256"]:', 'if False:', [T_FIT]),
    ("forbidden_fields_allowed", FIT, 'FORBIDDEN_FIELDS = ("condition", "slot", "instruction", "start_band")', 'FORBIDDEN_FIELDS = ("start_band",)', [T_FIT]),
    # inside build_turn's try block (16 spaces), so the mutant compiles (Sol cold seat N4)
    ("stage1_opens_power_trace", RUN, '                turn = build_turn(ldir / "runtime" / result["bundle"], result, fan_keys)',
     '                turn = build_turn(ldir / "runtime" / result["bundle"], result, fan_keys)\n                open(ldir / "runtime" / result["bundle"] / "power_trace.csv").close()', [T_RUN]),
    ("stage1_parses_rich_lines", RUN, '            m, e = _RICH_TS.search(line), _RICH_EL.search(line)',
     '            json.loads(line)\n            m, e = _RICH_TS.search(line), _RICH_EL.search(line)', [T_RUN]),
    ("fan_mean_over_present_keys", RUN, 'if fans and all(x is not None for x in fans) else None',
     'if fans and any(x is not None for x in fans) and all(x is not None for x in fans[:1]) else None', [T_RUN]),
    ("cli_stage1_hash_not_checked", RUN, '    if hashlib.sha256(raw).hexdigest() != a.stage1_sha256:', '    if False:', [T_RUN]),
    ("meter_left_rectangle", RUN, 'tot += 0.5 * (self._at(lo, i) + self._at(hi, i)) * (hi - lo)', 'tot += self._at(lo, i) * (hi - lo)', [T_RUN]),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    tmp = Path(tempfile.mkdtemp(prefix="jw-fit-mutants-"))
    try:
        for d in ("joulewise", "scripts"):
            shutil.copytree(ROOT / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / "configs/align/v4").mkdir(parents=True)      # the runtime sensor policy the rules-3/4 test reads
        shutil.copy(ROOT / "configs/align/v4/r1_runtime.json", tmp / "configs/align/v4/r1_runtime.json")
        shutil.copytree(ROOT / "docs/process/cadence/looks", tmp / "docs/process/cadence/looks")   # the schemas
        (tmp / "tests").mkdir()
        for f in (ROOT / "tests").iterdir():          # tests/__init__.py installs the host-command guard
            if f.is_file() and f.suffix == ".py":
                shutil.copy(f, tmp / "tests" / f.name)
        shutil.copytree(ROOT / "tests/cadence", tmp / "tests/cadence", ignore=shutil.ignore_patterns("__pycache__"))
        survived, invalid = [], []
        # control: the unmutated copy must pass, or every "kill" below means nothing
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", T_FIT, T_RUN], cwd=tmp, capture_output=True,
                           text=True, timeout=1800, env={**os.environ, "PYTHONPATH": str(tmp)})
        if r.returncode != 0:
            print("CONTROL FAILED: the unmutated copy does not pass\n" + r.stderr[-3000:], flush=True)
            return 2
        print("control: unmutated copy passes", flush=True)
        for mid, rel, old, new, tests in MUTANTS:
            if a.only and mid not in a.only:
                continue
            path = tmp / rel
            orig = path.read_text()
            if orig.count(old) != 1:
                print(f"{mid}: STALE (pattern found {orig.count(old)} times)", flush=True)
                survived.append(mid)
                continue
            mutated = orig.replace(old, new)
            if rel.endswith(".py"):
                # Sol cold seat N4: a mutant that does not compile is not a behaviour the tests caught. It is
                # reported as INVALID and fails the run; it is never counted as killed.
                try:
                    compile(mutated, str(path), "exec")
                except SyntaxError as exc:
                    print(f"{mid}: INVALID (does not compile: line {exc.lineno})", flush=True)
                    invalid.append(mid)
                    continue
            path.write_text(mutated)
            try:
                r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-f", *tests], cwd=tmp,
                                   capture_output=True, text=True, timeout=900,
                                   env={**os.environ, "PYTHONPATH": str(tmp)})
                killed = r.returncode != 0
            finally:
                path.write_text(orig)
            print(f"{mid}: {'killed' if killed else 'SURVIVED'}", flush=True)
            if not killed:
                survived.append(mid)
        print(f"{len(survived)} survived: {survived}")
        print(f"{len(invalid)} invalid (did not compile): {invalid}")
        return 1 if survived or invalid else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
