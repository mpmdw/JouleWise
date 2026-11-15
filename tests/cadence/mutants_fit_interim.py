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
    ("tau_no_floor", FIT, 'return max(0.0, float(x @ beta))', 'return float(x @ beta)', [T_FIT]),
    ("step_from_segment_start", FIT, 'max(0.0, v - max(u, tau))', 'max(0.0, v - u)', [T_FIT]),
    ("ramp_without_midpoint", FIT, 'vals.update(k_tf08=d * m * z[0]', 'vals.update(k_tf08=d * z[0]', [T_FIT]),
    ("hot_flag_late", FIT, 'and s["first_token_s"] - turn["turn_start_s"] >= off)', 'and s["first_token_s"] - turn["turn_start_s"] > off + 1.0)', [T_FIT]),
    ("lodo_leaks_heldout_day", FIT, 'train = [k for k in keys_all if by_key[k]["day"] != D]', 'train = list(keys_all)', [T_FIT]),
    ("censored_as_uncensored", FIT, '            y.append(st["censored_at_s"])\n            c.append(True)', '            y.append(st["censored_at_s"])\n            c.append(False)', [T_FIT]),
    ("estimable_at_5", FIT, 'ONSET_MIN_UNCENSORED = 12', 'ONSET_MIN_UNCENSORED = 5', [T_FIT]),
    ("hot_day_needs_1_leg", FIT, 'MIN_HOT_LEGS_PER_DAY = 3', 'MIN_HOT_LEGS_PER_DAY = 1', [T_FIT]),
    ("threshold_3pct", FIT, 'QUALIFIED_THRESHOLD = 0.02', 'QUALIFIED_THRESHOLD = 0.03', [T_FIT]),
    ("unknown_pm_is_off", FIT, 'OK_PM = ("Nominal", "Unknown", None)', 'OK_PM = ("Nominal", None)', [T_FIT]),
    ("level_off_requires_fresh", FIT, 'if ts < r["t_s"] <= tl and type(r["os_level"]) is int and r["os_level"] > 0:', 'if ts < r["t_s"] <= tl and type(r["os_level"]) is int and r["os_level"] > 0 and r["pm_fresh"]:', [T_FIT]),
    ("cluster_by_day", FIT, '            g += [k] * len(L["segments"])', '            g += [L["day"]] * len(L["segments"])', [T_FIT]),
    ("no_cr1_factor", FIT, 'corr = (G / (G - 1)) * ((n - 1) / (n - k)) if G > 1 and n > k else 1.0', 'corr = 1.0', [T_FIT]),
    ("bias_sign_flipped", FIT, 'diffs = [(d, rl / sd_l - rs / sd_s) for (_, d, rl, rs) in pairs]', 'diffs = [(d, rs / sd_s - rl / sd_l) for (_, d, rl, rs) in pairs]', [T_FIT]),
    ("fold_keeps_delta", FIT, 'fold_cols = [c for c in cols if c != DELTA_COL]', 'fold_cols = cols', [T_FIT]),
    ("no_hash_gate", FIT, 'if hashlib.sha256(dump(stage1_out)).hexdigest() != stage1_sha256:', 'if False:', [T_FIT]),
    ("no_output_check", FIT, '    output_check(out)\n    return out', '    return out', [T_FIT]),
    ("energy_input_hash_unchecked", FIT, 'if energy["input_sha256"] != stage1_out["input_sha256"]:', 'if False:', [T_FIT]),
    ("forbidden_fields_allowed", FIT, 'FORBIDDEN_FIELDS = ("condition", "slot", "instruction", "start_band")', 'FORBIDDEN_FIELDS = ("start_band",)', [T_FIT]),
    ("stage1_opens_power_trace", RUN, '            turn = build_turn(ldir / "runtime" / result["bundle"], result, fan_keys)',
     '            turn = build_turn(ldir / "runtime" / result["bundle"], result, fan_keys)\n            open(ldir / "runtime" / result["bundle"] / "power_trace.csv").close()', [T_RUN]),
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
        (tmp / "tests").mkdir()
        for f in (ROOT / "tests").iterdir():          # tests/__init__.py installs the host-command guard
            if f.is_file() and f.suffix == ".py":
                shutil.copy(f, tmp / "tests" / f.name)
        shutil.copytree(ROOT / "tests/cadence", tmp / "tests/cadence", ignore=shutil.ignore_patterns("__pycache__"))
        survived = []
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
            path.write_text(orig.replace(old, new))
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
        return 1 if survived else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
