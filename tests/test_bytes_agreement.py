"""BYTES agreement test (R8 item 4, Addendum 8): the analysis against the twin on the same campaigns.

Both implementations run as separate command-line processes (``scripts/bytes_analyze.py`` and
``scripts/bytes_twin.py``) on the same production-shaped synthetic campaigns from the lane's own
generator (``tests/fixtures/bytes/campaign.py``: ten full-size modules, 50 runs per model per pass,
corpus/start/midpoint/end references, a native 10 Hz meter stream, real random hidden offsets), at
every stage: blinded, stage 1 (``--stage fit`` / ``--stage 1``, after the fit-set keys and the
NEG-8 reference key are released) and stage 2 (``--stage heldout`` / ``--stage 2``, after every key
is released).  Key release is the copy of the private key files into the release directory, as the
desk does; no stage is reached by a direct function call.

The bar is Addendum 8 items 1 and 5, per field (``bar_*`` below carries each derivation):
energies within 1% of the cell's (h + B); power within 1% of its half-width; coefficients within 1%
of their HC3 half-width; durations to 1 ms; VIF to 2 significant figures; words, k, df, n, labels,
refusals and exit codes exactly.  A difference under the bar is one count per campaign and is not
classified (item 1); a difference above the bar fails the test and is printed with its campaign,
stage, field and both values.

A fence test proves the twin shares no code with the analysis: it imports nothing from ``joulewise``
(so none of the modules the analysis imports for arithmetic), and it reproduces block 5's t table
(Addendum 7 D8) rather than importing it.

Run from the repository root (about three minutes):
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m pytest tests/test_bytes_agreement.py -q
"""
from __future__ import annotations

import ast
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import aggregate
from joulewise import bytes_analysis as ba
from joulewise.b6 import blinding, export_runs
from joulewise.external import km003c_parse as kp
from scripts import bytes_twin as bt

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/bytes"
_campaign_spec = importlib.util.spec_from_file_location("bytes_campaign", FIXTURES / "campaign.py")
_campaign = importlib.util.module_from_spec(_campaign_spec)
_campaign_spec.loader.exec_module(_campaign)
archive_campaign = _campaign.archive_campaign

# Addendum 7 item 12 counterexamples, as B1's stage-chain test uses them: pass 2 twice as long as
# pass 1, and signed clock-fit excess latency whose negative extreme is the larger one.
PASS_SCALES = (1, 2)
CLOCK_LATENCY_MS = (-8, 3)
# name: (world, seed, planted defects).  Seeds are each world's first in campaign_design.json.
# bytes/resident/time are the three truths; defects plants p08's five defects
# plus FIX-573's unresolved-anchor validity failure;
# minimum removes six of one model's pass-1 repeats so that one pass refuses (Addendum 7 D9).
DEFECTS = [
    (1, "Qwen3-14B-4bit", 15, "lost_member"),        # quad unit 1: bundle and stored reduction gone
    (1, "Qwen3-4B-4bit", 3, "token_mismatch"),        # repeat: observed 511 tokens
    (1, "Qwen3-30B-A3B-4bit", 0, "battery_assist"),   # repeat: meter halved over decode, flag battery.assist
    (2, "Qwen3-8B-4bit", 2, "thermal"),               # repeat: thermal.os_level_nonzero
    (1, "Qwen3-8B-4bit", 20, "cooldown"),             # quad unit 2: member.cooldown_cap_hit (NUMBER class)
    (1, "Qwen3-8B-4bit", 4, "anchor_not_bounded"),   # repeat: invalid energy never restored
]
DEFECTS_MINIMUM = [(1, "Qwen3-32B-4bit", i, "strict_validation") for i in range(6)]
CAMPAIGNS = {
    "bytes": ("bytes", 1100, []),
    "resident": ("resident", 3100, []),
    "time": ("time", 2100, []),
    "defects": ("bytes", 1100, DEFECTS),
    "minimum": ("bytes", 1100, DEFECTS_MINIMUM),
}
BMAP = {"rails": "rails", "DC input": "dc_input", "rest": "rest"}
VMAP = {("gross primary", "primary"): "gross", ("idle-subtracted secondary", "primary"): "idle_subtracted",
        ("gross primary", "flagged-inclusive"): "flagged_inclusive"}
ANCHOR, INTERP, DRIFT, METER = ("E_clock_anchor_shift_bound_j", "E_interpolation_joint_edge_bound_j",
                                "E_whole_window_drift_allowance_j", "E_meter_edge_bound_j")
FAMILY_KEY = {"gross": "gross", "idle_subtracted": "idle"}
WORK = {}


# ---------------------------------------------------------------------------------------------
# Bars (Addendum 8 items 1 and 5).  Each returns an absolute tolerance in the field's own unit.

def bar_energy(half_width_j):
    """1% of the cell's (h + B): Addendum 8.1.  At the smallest printed cell (0.013 J, 1.7B rails)
    this is 1.3e-4 J, above 1e6 x float noise on a 1e4 J energy (2.2e-6 J)."""
    return 0.01 * half_width_j


def bar_power(half_width_w):
    """1% of the power's own half-width, (h + B)/T: Addendum 8.5."""
    return 0.01 * half_width_w


def bar_coefficient(half_width):
    """1% of the coefficient's HC3 half-width (or of the labelled OLS half-width for the OLS line
    printed beside it): Addendum 8.5."""
    return 0.01 * half_width


FLOAT_EPS = 2.2e-16     # double precision relative float noise (the brief, section 5)


def bar_float_noise_coefficient(vif, scale):
    """The lower edge of the bar window (the brief, section 5: a bar sits above 1e6 x float noise),
    for a coefficient of a two-regressor fit whose VIF is printed (the rest model, Addendum 3 item 9).
    An input perturbation of relative size d (float noise on the fitted powers, 1e6 x eps at the
    window's edge) moves a least-squares coefficient by about kappa(X'X) x d x its natural scale, the
    response's size over its regressor's size (1 for the intercept).  For the centred two-regressor
    Gram matrix kappa = (1 + |r|)/(1 - |r|) and 1 - r^2 = 1/VIF, so kappa is about 4 x VIF.  The floor
    is therefore 1e6 x eps x 4 VIF x scale.  It matters only where the design is near-singular
    (Addendum 8.6: with VIF 3.4e6, input noise of 3e-10 moves the rest model's c by 6%, so c is not
    identified and no word is drawn from it); elsewhere 1% of the HC3 half-width is far above it.  A
    VIF the analysis prints as infinite (|r| = 1) makes every coefficient of that fit pure float
    noise, so the floor is unbounded there."""
    if vif is None or not math.isfinite(vif):
        return math.inf
    return 1e6 * FLOAT_EPS * 4 * vif * scale


def coefficient_scales(points):
    """Natural scales of (c, epsilon_rest, lambda) for the rest model P_rest = c + e BW + l P_rails:
    the RMS response over 1, over the RMS of BW and over the RMS of P_rails."""
    def rms(values):
        return math.sqrt(math.fsum(v * v for v in values) / len(values))
    y = rms([p[0] for p in points])
    return [y, y / rms([p[1] for p in points]), y / rms([p[2] for p in points])]


# Durations compare to 1 ms: Addendum 8.5 (the printed precision F13 asks B6 to fix; 1 ms is the
# precision Addendum 8.5 names, and it is 1e6 x float noise on a 60 s decode: 1.3e-8 s, by far).
DURATION_BAR_S = 1e-3


def bar_duration_derived(value, duration_s):
    """A quantity proportional to 1/T or to T (tau = T/512, BW = b x 512/T, R/tau): the 1 ms
    duration bar propagated, |value| x 1 ms / T."""
    return abs(value) * DURATION_BAR_S / duration_s


def bar_two_significant_figures(a, t):
    """Half a unit in the second significant figure of the larger magnitude: Addendum 8.5, VIF."""
    scale = max(abs(a), abs(t))
    if scale == 0:
        return 0.0
    return 0.5 * 10 ** (math.floor(math.log10(scale)) - 1)


def bar_no_half_width(a, t):
    """A number with no half-width and no fixed printed decimals (the brief, section 5): 1e-6
    relative, or 1e-6 absolute in the column's unit, whichever is larger.  1e-6 relative is 4,500 x
    float noise (2.2e-16) and below 1% of any printed uncertainty."""
    return max(1e-6 * max(abs(a), abs(t)), 1e-6)


# ---------------------------------------------------------------------------------------------
# The recorder: every compared field is one record.

class Recorder:
    def __init__(self):
        self.rows = []

    def exact(self, stage, group, key, a, t, note=None):
        row = {"stage": stage, "group": group, "key": key, "a": a, "t": t, "bar": "exact",
               "status": "equal" if a == t else "above_bar"}
        if note:
            row["note"] = note
        self.rows.append(row)
        return row

    def number(self, stage, group, key, a, t, bar, note=None):
        """bar: an absolute tolerance in the field's unit, or None for 'no half-width' (1e-6)."""
        if a is None or t is None or isinstance(a, (bool, str, list, dict)) or isinstance(t, (bool, str, list, dict)):
            return self.exact(stage, group, key, a, t, note)
        if bar is None:
            bar = bar_no_half_width(a, t)
        diff = abs(a - t)
        status = "equal" if diff == 0 else "under_bar" if diff <= bar else "above_bar"
        row = {"stage": stage, "group": group, "key": key, "a": a, "t": t, "bar": bar, "abs": diff, "status": status}
        if note:
            row["note"] = note
        self.rows.append(row)
        return row

    def label_with_slack(self, stage, group, key, a, t, under_bar):
        """A label (sign, 'adds nothing') drawn from a number: exact, unless the number it rests on
        is itself within its bar of the decision boundary (then the difference is under the bar)."""
        if a == t:
            return self.exact(stage, group, key, a, t)
        row = self.exact(stage, group, key, a, t)
        if under_bar:
            row["status"] = "under_bar"
            row["note"] = "the deciding number is within its bar of the boundary"
        return row

    def counts(self):
        out = {"compared": len(self.rows), "equal": 0, "under_bar": 0, "above_bar": 0}
        for row in self.rows:
            out[row["status"]] += 1
        return out

    def above(self):
        return [r for r in self.rows if r["status"] == "above_bar"]


# ---------------------------------------------------------------------------------------------
# Output mapping (names only; neither side's arithmetic is touched).

def canon(name):
    return bt.canon(name)


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def a_kinds(row):
    """The analysis carries three kind slots; on DC input its first slot holds u, on rest it holds
    rails anchor + u (u printed separately as meter_phase_edge_mean_j).  Split into the twin's four."""
    k = row.get("kind_averages_j") or {}
    meter = row.get("meter_phase_edge_mean_j", 0.0) or 0.0
    if row["boundary"] == "rails":
        return {"anchor": k.get(ANCHOR), "interp": k.get(INTERP), "drift": k.get(DRIFT), "meter_edge": 0.0}
    if row["boundary"] == "DC input":
        return {"anchor": 0.0, "interp": k.get(INTERP), "drift": k.get(DRIFT), "meter_edge": k.get(ANCHOR)}
    return {"anchor": k.get(ANCHOR) - meter, "interp": k.get(INTERP), "drift": k.get(DRIFT), "meter_edge": meter}


def t_kinds(est):
    k = est.get("kind_averages_j") or {}
    return {"anchor": k.get(ANCHOR, 0.0), "interp": k.get(INTERP, 0.0), "drift": k.get(DRIFT, 0.0),
            "meter_edge": k.get(METER, 0.0)}


def t_kept(est):
    m = est.get("members") or {}
    return sorted(m.get("repeats", []) + [r for q in (m.get("quads") or {}).values() for r in q])


def compare_cell_numbers(R, stage, g, row, est):
    """One per-pass cell line (or the without-assisted diagnostic): m, h, B, kinds, interval, T, n."""
    hb = row["h_j"] + row["B_j"]
    for key in ("mean_j", "h_j", "B_j", "lower_j", "upper_j"):
        R.number(stage, g, key, row.get(key), est.get(key), bar_energy(hb))
    # variance = (h / t)^2: the h bar propagated, d(var) = 2 var dh / h with dh = 1% of (h + B).
    var_bar = 0.02 * row["variance"] * hb / row["h_j"] if row.get("h_j") else None
    R.number(stage, g, "variance", row.get("variance"), est.get("variance"), var_bar)
    for key in ("df", "n_r", "n_b"):
        R.exact(stage, g, key, row.get(key), est.get(key))
    R.number(stage, g, "duration_s", row.get("duration_s"), est.get("duration_s"), DURATION_BAR_S)
    ak, tk = a_kinds(row), t_kinds(est)
    for kind in ("anchor", "interp", "drift", "meter_edge"):
        R.number(stage, g, "B_kind:" + kind, ak[kind], tk[kind], bar_energy(hb))


def compare_cells(R, stage, a_rows, t):
    for row in a_rows:
        variant = VMAP.get((row["basis"], row["selection"]))
        if variant is None:
            continue    # idle-subtracted x flagged-inclusive: the twin prints no such line (recorded)
        model, b = canon(row["model"]), BMAP[row["boundary"]]
        g = f"cell/{model}/pass{row['pass_id']}/{b}/{variant}"
        cell = (((t.get("cells") or {}).get(model) or {}).get(f"pass{row['pass_id']}") or {}).get("boundaries", {}).get(b)
        if cell is None:
            R.exact(stage, g, "status", row["status"], "absent")
            continue
        est = cell.get(variant) if cell.get("status", "ok") == "ok" else cell
        est = est if est is not None else {"status": cell.get("status", "absent")}
        a_ok, t_ok = row["status"] == "computed", est.get("status") == "ok"
        R.exact(stage, g, "status", "computed" if a_ok else "unavailable", "computed" if t_ok else "unavailable",
                None if a_ok and t_ok else f"analysis: {row.get('reason')}; twin: {est.get('status')}")
        if not (a_ok and t_ok):
            continue
        compare_cell_numbers(R, stage, g, row, est)
        R.exact(stage, g, "kept_runs", sorted(row.get("kept_runs", [])), t_kept(est))
        if variant == "gross":
            da = cell.get("drift_allowance") or {}
            R.number(stage, g, "drift_scale", row.get("drift_scale"), da.get("scale"), None)
            hb = row["h_j"] + row["B_j"]
            if b == "rails":
                R.number(stage, g, "attribution_floor_j", row.get("rails_attribution_floor_j"),
                         (cell.get("attribution_floor") or {}).get("value_j"), bar_energy(hb))
            else:
                R.number(stage, g, "meter_attribution_floor_j", row.get("meter_attribution_floor_j"),
                         (cell.get("meter_attribution_floor") or {}).get("value_j"), bar_energy(hb))
            # Addendum 7 D10: block 5's without-assisted line wherever a cell holds an assist member.
            wa, wt = row.get("without_assisted"), cell.get("without_assisted")
            if wa is not None or wt is not None:
                gw = g + "/without_assisted"
                a_ok = wa is not None and wa.get("status") == "computed"
                t_ok = wt is not None and wt.get("status") == "ok"
                R.exact(stage, gw, "status", "computed" if a_ok else "unavailable", "computed" if t_ok else "unavailable")
                if a_ok and t_ok:
                    compare_cell_numbers(R, stage, gw, {**wa, "boundary": row["boundary"]}, wt)


def compare_neg8(R, stage, a_rows, t):
    seen = set()
    for row in a_rows:
        sid = row["session_id"]
        if sid in seen or "neg8_inputs" not in row:
            continue
        seen.add(sid)
        tn = ((t.get("sessions") or {}).get(sid) or {}).get("neg8") or {}
        for b, ref in (row["neg8_inputs"].get("boundaries") or {}).items():
            g = f"neg8/{sid}/{BMAP[b]}"
            for family, fa in (ref.get("families") or {}).items():
                tf = tn.get(f"{BMAP[b]}/{FAMILY_KEY[family]}") or {}
                gf = g + "/" + family
                R.exact(stage, gf, "status", "ok", tf.get("status", "absent"))
                if tf.get("status") != "ok":
                    continue
                # Session-level allowance terms have no cell half-width: the no-half-width bar.
                R.number(stage, gf, "allowance_j", fa.get("allowance_j"), tf.get("allowance_j"), None)
                for key in ("bound_j", "envelope_j", "prediction_j"):
                    R.number(stage, gf, key, fa["bound_terms"].get(key), (tf.get("bound_terms") or {}).get(key), None)
            tg = tn.get(f"{BMAP[b]}/gross") or {}
            R.number(stage, g, "E_ref_j", ref["energy_j"], tg.get("E_ref_j"), None)
            R.number(stage, g, "T_ref_s", ref["duration_s"], tg.get("T_ref_s"), DURATION_BAR_S)
            R.exact(stage, g, "reference_run_ids", sorted(ref["reference_run_ids"]), sorted(tg.get("reference_run_ids", [])))
            R.exact(stage, g, "corpus_run_ids", sorted(ref["corpus_run_ids"]), sorted(tg.get("corpus_run_ids", [])))


def compare_points(R, stage, a_points, t):
    for p in a_points:
        variant = VMAP.get((p["basis"], p["selection"]))
        if variant not in ("gross", "idle_subtracted"):
            continue
        model, b = canon(p["model"]), BMAP[p["boundary"]]
        g = f"point/{model}/mean/{b}/{variant}"
        q = (((t.get("cells") or {}).get(model) or {}).get("passes_mean") or {}).get("boundaries", {}) \
            .get(b, {}).get("quantities", {}).get(variant) or {"status": "absent"}
        a_ok, t_ok = p.get("status") == "computed", q.get("status") == "ok"
        R.exact(stage, g, "status", "computed" if a_ok else "unavailable", "computed" if t_ok else "unavailable")
        if not (a_ok and t_ok):
            continue
        # Addendum 7 D9: the pass label and the number of computed passes.
        R.exact(stage, g, "pass_label", {"two_pass": "pass_mean", "one_pass": "one_pass"}.get(p.get("pass_status")),
                q.get("label"))
        R.exact(stage, g, "n_passes", p.get("n_passes"), q.get("passes_computed"))
        hb = p["h_j"] + p["B_j"]
        T = p["duration_s"]
        R.number(stage, g, "mean_j", p["mean_j"], q["E_dec_j"], bar_energy(hb))
        R.number(stage, g, "duration_s", p["duration_s"], q["T_dec_s"], DURATION_BAR_S)
        for ak, tk in (("e", "e_j_per_step"), ("lower", "e_lower_j_per_step"), ("upper", "e_upper_j_per_step"),
                       ("printed_j_per_output_token", "e_printed_j_per_token")):
            R.number(stage, g, ak, p.get(ak), q.get(tk), bar_energy(hb) / bt.DECODE_STEPS)
        R.number(stage, g, "time", p["time"], q["tau_s_per_step"], DURATION_BAR_S / bt.DECODE_STEPS)
        R.number(stage, g, "power", p["power"], q["P_mean_w"], bar_power(p["power_half_w"]))
        R.number(stage, g, "power_half_w", p["power_half_w"], q["P_half_width_w"], bar_power(p["power_half_w"]))
        R.number(stage, g, "BW", p["BW"], q["BW_GB_per_s"], bar_duration_derived(p["BW"], T))
        R.exact(stage, g, "bytes", p["bytes"], q["b_GB_per_step"])
        R.exact(stage, g, "resident", p["resident"], q["R_GB"])
        R.number(stage, g, "R_over_tau", p["resident"] / p["time"], q["R_over_tau_GB_per_s"],
                 bar_duration_derived(p["resident"] / p["time"], T))
        R.number(stage, g, "half_width_j(h+B)", hb, (q["E_dec_upper_j"] - q["E_dec_lower_j"]) / 2, bar_energy(hb))
        for i, (va, vt) in enumerate(zip(p.get("pass_values_j", []), q.get("pass_values_E_dec_j", []))):
            R.number(stage, g, f"pass_values_j[{i}]", va, vt, bar_energy(hb))
        R.number(stage, g, "pass_difference_j", p.get("pass_difference_j"), q.get("pass_difference_E_dec_j"), bar_energy(hb))


def compare_h1(R, stage, a_h1, a_moe, t, a_frozen):
    for row in a_h1:
        if (row["basis"], row["selection"]) != ("gross primary", "primary"):
            continue
        pk = "passes_mean" if row["pass_id"] == "mean" else f"pass{row['pass_id']}"
        b, model = BMAP[row["boundary"]], canon(row["model"])
        g = f"h1/{b}/{pk}/{model}"
        th = (t.get("h1") or {}).get(b, {}).get(pk) or {}
        tm = (th.get("models") or {}).get(model)
        if tm is None:
            R.exact(stage, g, "word", row["word"] if row["role"] == "heldout" else None, "absent:" + str(th.get("status")))
            continue
        if row["role"] == "heldout":
            R.exact(stage, g, "word", row["word"], tm["word"])
        for c in row["checks"]:
            tc = tm["checks"][c["hypothesis"]]
            h = c["hypothesis"]
            # The held-out model's own measured half-width per step, (h + B)/512, is the cell's.
            w = (c["measured_upper"] - c["measured_lower"]) / 2
            R.number(stage, g, h + ":predicted", c["predicted"], tc["prediction"]["central"], bar_energy(w))
            R.number(stage, g, h + ":prediction_lower", c["prediction_lower"], tc["prediction"]["lower"], bar_energy(w))
            R.number(stage, g, h + ":prediction_upper", c["prediction_upper"], tc["prediction"]["upper"], bar_energy(w))
            R.number(stage, g, h + ":measured_lower", c["measured_lower"], tc["measured"][0], bar_energy(w))
            R.number(stage, g, h + ":measured_upper", c["measured_upper"], tc["measured"][1], bar_energy(w))
            R.exact(stage, g, h + ":consistent", c["consistent"], tc["consistent"])
            # ln(e / predicted): the prediction's bar divided by the prediction, dimensionless.
            ln_bar = bar_energy(w) / c["predicted"] if c.get("predicted") else None
            R.number(stage, g, h + ":ln_ratio", c["log_ratio"], tc["ln_measured_over_predicted"], ln_bar)
    for row in a_moe:
        if (row["basis"], row["selection"]) != ("gross primary", "primary"):
            continue
        b = BMAP[row["boundary"]]
        tm = ((t.get("h1") or {}).get(b, {}).get("passes_mean") or {}).get("active_or_resident") or {}
        R.exact(stage, f"moe/{b}/passes_mean", "answer", row["answer"], tm.get("answer"))
    # Frozen lines (pass mean, gross primary): central line and the set of eight corner lines.
    # A line coefficient has no half-width (its consequences are compared above at the cells' bars).
    for group in (a_frozen or {}).get("rival_lines", []):
        if (group["basis"], group["selection"]) != ("gross primary", "primary") or group["lines"] is None:
            continue
        b = BMAP[group["boundary"]]
        tl = ((t.get("h1") or {}).get(b, {}).get("passes_mean") or {}).get("lines")
        if not tl:
            R.exact(stage, f"lines/{b}", "present", True, False)
            continue
        for hyp, item in group["lines"].items():
            g = f"lines/{b}/{hyp}"
            R.number(stage, g, "intercept", item["line"][0], tl[hyp]["central"]["a"], None)
            R.number(stage, g, "slope", item["line"][1], tl[hyp]["central"]["s"], None)
            ac = sorted(item["corners"], key=lambda c: c[1])
            tc = sorted(([c["a"], c["s"]] for c in tl[hyp]["corners"]), key=lambda c: c[1])
            for i, (x, y) in enumerate(zip(ac, tc)):
                R.number(stage, g, f"corner[{i}].intercept", x[0], y[0], None)
                R.number(stage, g, f"corner[{i}].slope", x[1], y[1], None)


def _interval(R, stage, g, name, a_fit, idx, t_iv, *, floor=0.0):
    """One coefficient: estimate and HC3 interval at 1% of the HC3 half-width; the labelled OLS
    interval beside it at 1% of its own half-width.  floor: the float-noise floor of the bar (the
    rest model only, from its printed VIF); 0 for a fit that prints no VIF."""
    half = (a_fit["intervals"][idx][1] - a_fit["intervals"][idx][0]) / 2
    bar = max(bar_coefficient(half), floor)
    R.number(stage, g, name + ":estimate", a_fit["coefficients"][idx], t_iv["value"], bar)
    R.number(stage, g, name + ":lower[HC3]", a_fit["intervals"][idx][0], t_iv["lower"], bar)
    R.number(stage, g, name + ":upper[HC3]", a_fit["intervals"][idx][1], t_iv["upper"], bar)
    half_ols = (a_fit["ols_intervals"][idx][1] - a_fit["ols_intervals"][idx][0]) / 2
    t_ols = t_iv.get("ols") or {}
    bar_ols = max(bar_coefficient(half_ols), floor)
    R.number(stage, g, name + ":lower[OLS label]", a_fit["ols_intervals"][idx][0], t_ols.get("lower"), bar_ols)
    R.number(stage, g, name + ":upper[OLS label]", a_fit["ols_intervals"][idx][1], t_ols.get("upper"), bar_ols)


def compare_h2_fit(R, stage, g, row, th, own_half, b, rest_inputs=None):
    """One H2 fit group (primary, or the two-pass sensitivity line).  rest_inputs: {model: (P_rest,
    BW, P_rails)} of the analysis's points, for the rest model's coefficient scales."""
    R.exact(stage, g, "n", row["n"], th.get("n"))
    if row["two_term"]["status"] != "computed" or th.get("status") != "ok":
        R.exact(stage, g, "status", row["two_term"]["status"], th.get("status"))
        return
    R.exact(stage, g, "simple:df", row["two_term"]["df"], th["simple"]["df"])
    _interval(R, stage, g, "simple:P0", row["two_term"], 0, {"value": th["simple"]["P0_w"], "lower": None, "upper": None}
              if False else _p0(th["simple"], "P0_w", row["two_term"], 0))
    _interval(R, stage, g, "simple:epsilon", row["two_term"], 1, th["simple"]["epsilon_j_per_GB"])
    ext_a, ext_t = row["resident_extended"], th.get("resident_extended")
    R.exact(stage, g, "extended:status", ext_a["status"], "computed" if ext_t else "refused")
    if ext_a["status"] == "computed" and ext_t:
        R.exact(stage, g, "extended:df", ext_a["df"], ext_t["df"])
        _interval(R, stage, g, "extended:P0", ext_a, 0, _p0(ext_t, "P0_w", ext_a, 0))
        _interval(R, stage, g, "extended:epsilon", ext_a, 1, ext_t["epsilon_j_per_GB"])
        _interval(R, stage, g, "extended:rho", ext_a, 2, ext_t["rho_j_per_GB"])
        lo, hi = ext_a["intervals"][2]
        slack = bar_coefficient((hi - lo) / 2)
        near = min(abs(lo), abs(hi), abs(ext_a["coefficients"][2])) <= slack
        R.label_with_slack(stage, g, "resident_adds_nothing", row["resident_adds_nothing"], ext_t["resident_adds_nothing"], near)
    tier_a, tier_t = row["tier"], th.get("tier")
    R.exact(stage, g, "tier:status", tier_a["status"], "computed" if tier_t else "refused")
    if tier_a["status"] == "computed" and tier_t:
        R.exact(stage, g, "tier:df", tier_a["df"], tier_t["df"])
        _interval(R, stage, g, "tier:P0", tier_a, 0, _p0(tier_t, "P0_w", tier_a, 0))
        _interval(R, stage, g, "tier:epsilon", tier_a, 1, tier_t["epsilon_j_per_GB"])
        _interval(R, stage, g, "tier:rho", tier_a, 2, tier_t["rho_j_per_GB"])
        for dev in row["tier_deviations"]:
            m = canon(dev["model"])
            td = tier_t["deviations"].get(m)
            gd = f"{g}/deviation/{m}"
            R.exact(stage, gd, "status", dev["status"], "computed" if td else "absent")
            if dev["status"] != "computed" or td is None:
                continue
            half = dev["prediction_half_w"] + dev["measured_half_w"]
            R.number(stage, gd, "deviation_w", dev["deviation_w"], td["deviation_w"], bar_power(half))
            R.number(stage, gd, "predicted_w", dev["predicted_w"], td["predicted_w"], bar_power(half))
            R.number(stage, gd, "measured_half_w", dev["measured_half_w"], td["measured_half_width_w"],
                     bar_power(dev["measured_half_w"]))
            R.number(stage, gd, "prediction_half_w", dev["prediction_half_w"],
                     td["half_width_w"] - td["measured_half_width_w"], bar_power(dev["prediction_half_w"]))
            R.number(stage, gd, "lower_w", dev["lower_w"], td["lower_w"], bar_power(half))
            R.number(stage, gd, "upper_w", dev["upper_w"], td["upper_w"], bar_power(half))
            near = abs(dev["deviation_w"]) <= bar_power(half) or abs(td["deviation_w"]) <= bar_power(half)
            R.label_with_slack(stage, gd, "sign", "+" if dev["deviation_w"] > 0 else "-" if dev["deviation_w"] < 0 else "0",
                               td["sign"], near)
    if b == "rest":
        rm, tr = row["rest"], th.get("rest_model")
        R.exact(stage, g, "rest:status", rm["status"], "computed" if tr else "refused")
        if rm["status"] == "computed" and tr:
            vif_a, vif_t = rm.get("vif"), tr.get("vif_BW_and_P_rails")
            fitted = [rest_inputs[canon(p["model"])] for p in rm["point_labels"]]
            floors = [bar_float_noise_coefficient(vif_a, scale) for scale in coefficient_scales(fitted)]
            _interval(R, stage, g, "rest:c", rm, 0, _p0(tr, "c_w", rm, 0), floor=floors[0])
            _interval(R, stage, g, "rest:epsilon_rest", rm, 1, tr["epsilon_rest_j_per_GB"], floor=floors[1])
            _interval(R, stage, g, "rest:lambda", rm, 2, tr["lambda"], floor=floors[2])
            vif_bar = bar_two_significant_figures(vif_a, vif_t) if vif_a is not None and vif_t is not None else None
            R.number(stage, g, "rest:vif", vif_a, vif_t, vif_bar)
    for item in row["loo_description"]:
        m = canon(item["model"])
        tl = (th.get("leave_one_out") or {}).get(m) or {}
        R.exact(stage, g + "/loo", m + ":status", item["status"], "computed" if tl else "refused")
        if item["status"] == "computed" and tl:
            R.number(stage, g + "/loo", m, item["predicted_w"], tl.get("predicted_w"), bar_power(own_half.get(m, 0.0)))


def _p0(t_fit, key, a_fit, idx):
    """The twin prints P0 and c as bare values (Addendum 3 item 6: printed, not counted); compare
    the estimate at 1% of the analysis's HC3 half-width and nothing else."""
    return {"value": t_fit[key], "lower": a_fit["intervals"][idx][0], "upper": a_fit["intervals"][idx][1],
            "ols": {"lower": a_fit["ols_intervals"][idx][0], "upper": a_fit["ols_intervals"][idx][1]}}


def compare_h2(R, stage, a_h2, t, a_points):
    for row in a_h2:
        if (row["basis"], row["selection"]) != ("gross primary", "primary"):
            continue
        b = BMAP[row["boundary"]]
        th = (t.get("h2") or {}).get(b, {}).get("passes_mean") or {}
        own = {canon(p["model"]): p for p in a_points
               if (p["boundary"], p["basis"], p["selection"]) == (row["boundary"], "gross primary", "primary")
               and p.get("status") == "computed"}
        own_half = {m: p["power_half_w"] for m, p in own.items()}
        rails = {canon(p["model"]): p["power"] for p in a_points
                 if (p["boundary"], p["basis"], p["selection"]) == ("rails", "gross primary", "primary")
                 and p.get("status") == "computed"}
        rest_inputs = {m: (p["power"], p["BW"], rails[m]) for m, p in own.items() if m in rails} if b == "rest" else None
        if row.get("analysis") == "two_pass_sensitivity":
            g = f"h2/{b}/passes_mean/two_pass_sensitivity"
            ts = th.get("two_pass_sensitivity")
            R.exact(stage, g, "present", True, ts is not None)
            if ts is not None:
                compare_h2_fit(R, stage, g, row, ts, own_half, b, rest_inputs)
            continue
        g = f"h2/{b}/passes_mean"
        k_t = (((t.get("multiplicity") or {}).get("H2") or {}).get(b) or {}).get("passes_mean", {}).get("k_primary_intervals")
        R.exact(stage, g, "k", row["k"], k_t)
        R.exact(stage, g, "k_printed_primary_rows", len(row["primary_intervals"]), k_t)
        compare_h2_fit(R, stage, g, row, th, own_half, b, rest_inputs)


def compare_commit(R, a_frozen, t1, t2):
    """Stage-1 commit content where comparable: fit points (x, e, w), tier inputs; twin hash stability."""
    stage = "fit-commit"
    content = (t1 or {}).get("stage1_commit", {}).get("content", {})
    for p in (a_frozen or {}).get("fit_points", []):
        if (p["basis"], p["selection"]) != ("gross primary", "primary") or p.get("status") != "computed":
            continue
        b, m = BMAP[p["boundary"]], canon(p["model"])
        tp = ((content.get("fit_cells") or {}).get(b) or {}).get("passes_mean", {}).get(m)
        g = f"commit/fit_point/{b}/{m}"
        if tp is None:
            R.exact(stage, g, "present", True, False)
            continue
        w = (p["upper"] - p["lower"]) / 2
        R.number(stage, g, "e", p["e"], tp["e"], bar_energy(w))
        R.number(stage, g, "w", w, tp["w"], bar_energy(w))
        R.exact(stage, g, "x_bytes", p["bytes"], tp["x"]["bytes"])
        R.exact(stage, g, "x_resident", p["resident"], tp["x"]["resident"])
        R.number(stage, g, "x_time", p["time"], tp["x"]["time"], DURATION_BAR_S / bt.DECODE_STEPS)
    for p in (a_frozen or {}).get("tier_fit_inputs", []):
        if (p["basis"], p["selection"]) != ("gross primary", "primary"):
            continue
        b, m = BMAP[p["boundary"]], canon(p["model"])
        tp = ((content.get("h2_tier1_inputs") or {}).get(b) or {}).get("passes_mean", {}).get(m)
        g = f"commit/tier_input/{b}/{m}"
        if tp is None:
            R.exact(stage, g, "present", True, False)
            continue
        T = p["time"] * bt.DECODE_STEPS
        R.number(stage, g, "BW", p["BW"], tp["BW"], bar_duration_derived(p["BW"], T))
        R.number(stage, g, "power", p["power"], tp["P"], bar_power(tp["P_half_width"]))
        R.number(stage, g, "R_over_tau", p["resident"] / p["time"], tp["R_over_tau"],
                 bar_duration_derived(p["resident"] / p["time"], T))
    if t1 and t2:
        R.exact(stage, "commit/twin_hash", "stage1 == stage2 (twin's own property)",
                t1["stage1_commit"]["sha256"], t2["stage1_commit"]["sha256"])


def compare_campaign(root):
    """Every compared field of one campaign's outputs, as records."""
    o = root / "out"
    R = Recorder()
    exits = {tag: int((o / (tag + ".exit")).read_text().strip()) for tag in
             ("a-blinded", "a-fit", "a-held", "t-blinded", "t-1", "t-2", "a-held-fitkeys", "t-2-fitkeys",
              "a-fit-nokeys", "t-1-nokeys") if (o / (tag + ".exit")).exists()}
    R.exact("refusal", "exit", "blinded", exits.get("a-blinded"), exits.get("t-blinded"))
    R.exact("refusal", "exit", "fit/stage1 before any release (must refuse)", exits.get("a-fit-nokeys"), exits.get("t-1-nokeys"))
    R.exact("refusal", "exit", "fit/stage1", exits.get("a-fit"), exits.get("t-1"))
    R.exact("refusal", "exit", "heldout/stage2 with fit-only keys (must refuse)", exits.get("a-held-fitkeys"), exits.get("t-2-fitkeys"))
    R.exact("refusal", "exit", "heldout/stage2", exits.get("a-held"), exits.get("t-2"))
    tb = load(o / "t-blinded.json")
    if tb is not None and (o / "a-blinded").is_dir():
        rows = load(o / "a-blinded/blinded_pass_estimates.json")
        compare_cells(R, "blinded", rows, tb)
        compare_neg8(R, "blinded", rows, tb)
        ap = load(o / "a-blinded/model_estimates.json")
        compare_points(R, "blinded", ap, tb)
        compare_h1(R, "blinded", load(o / "a-blinded/h1.json"), load(o / "a-blinded/moe.json"), tb, None)
        compare_h2(R, "blinded", load(o / "a-blinded/h2.json"), tb, ap)
        R.exact("blinded", "boundaries", "DC input and rest absent at the blinded stage (Addendum 3 item 4)",
                sorted({r["boundary"] for r in rows}),
                sorted({b for m in tb["cells"].values() for k, v in m.items() if k[4:].isdigit()
                        for b, c in v["boundaries"].items() if c.get("status") != "no_archive_join"}))
    t1, t2 = load(o / "t-1.json"), load(o / "t-2.json")
    frozen = load(o / "a-fit/predictions.json")
    if t1 is not None and frozen is not None:
        fit_rows = load(o / "a-fit/fit_pass_estimates.json")
        compare_cells(R, "fit", fit_rows, t1)
        compare_neg8(R, "fit", fit_rows, t1)
        compare_commit(R, frozen, t1, t2)
    if t2 is not None and (o / "a-held").is_dir():
        held_rows = load(o / "a-held/heldout_pass_estimates.json") + (load(o / "a-fit/fit_pass_estimates.json") or [])
        compare_cells(R, "heldout", held_rows, t2)
        compare_neg8(R, "heldout", load(o / "a-held/heldout_pass_estimates.json"), t2)
        ap = load(o / "a-held/model_estimates.json")
        compare_points(R, "heldout", ap, t2)
        compare_h1(R, "heldout", load(o / "a-held/h1.json"), load(o / "a-held/moe.json"), t2, frozen)
        compare_h2(R, "heldout", load(o / "a-held/h2.json"), t2, ap)
    return R


# ---------------------------------------------------------------------------------------------
# Campaign building (the lane's generator, with the review's defects planted before export).

def _write(path, value):
    Path(path).write_text(json.dumps(value) + "\n")


def _run_ids(archive, manifest_models, model):
    roster = ba.read_json(archive / "derived/roster.json")
    cell = next(m for m in manifest_models if m["model"] == model)["cell_ids"][0]
    return [m["run_id"] for m in roster["members"] if any(u["cell_id"] == cell for u in m.get("units", []))]


def _halve_meter_over_decode(archive, run_id):
    """p08 E: the meter (DC input) reads half during the member's decode span; SMC shows discharge."""
    bundle = archive / "sources/claim-runs" / run_id
    md = ba.read_json(bundle / "metadata.json")
    events = [json.loads(s) for s in (bundle / "events.jsonl").read_text().splitlines() if s.strip()]
    t0, t1 = ba._event_span(events, "decode", md)
    path = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
    lines = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    changed = 0
    for b in lines[1:-1]:
        raw = bytes.fromhex(b["p"])
        out = []
        for i in range(b["n"]):
            f = list(kp.SAMPLE.unpack(raw[i * kp.SAMPLE.size:(i + 1) * kp.SAMPLE.size]))
            tick = b["rx"] // 100_000_000 - (b["n"] - 1 - i)
            if t0 <= tick * 100_000_000 < t1:
                f[3] = f[3] // 2
                changed += 1
                b["smc"] = {"B0AC": -3000, "B0AV": 12000}
            out.append(kp.SAMPLE.pack(*f))
        b["p"] = b"".join(out).hex()
    path.write_text("".join(json.dumps(x) + "\n" for x in lines))
    return changed


def plant(archive, acceptance, models, pass_id, defects, log):
    """Plant defects in the archive and the acceptance record before the session is exported, so the
    export CSV (which the twin reads) and the archive (which the analysis reads) carry the same
    exclusions and flags."""
    for p, model, ordinal, kind in defects:
        if p != pass_id:
            continue
        rid = _run_ids(archive, models, model)[ordinal]
        bundle = archive / "sources/claim-runs" / rid
        if kind == "lost_member":
            shutil.rmtree(bundle)
            (archive / "withheld/reductions" / (rid + ".summary_metrics.rereduced.json")).unlink()
            codes = ["member.bytes_missing"]
        elif kind == "token_mismatch":
            md = ba.read_json(bundle / "metadata.json")
            md["workload_observed"]["output_token_count"] = 511
            _write(bundle / "metadata.json", md)
            codes = ["member.token_count_mismatch"]
        elif kind == "thermal":
            codes = ["thermal.os_level_nonzero"]
        elif kind == "strict_validation":
            codes = ["member.strict_validation_failed"]
        elif kind == "anchor_not_bounded":
            codes = ["member.anchor_not_bounded"]
        elif kind == "cooldown":
            codes = ["member.cooldown_cap_hit"]
        elif kind == "battery_assist":
            n = _halve_meter_over_decode(archive, rid)
            acceptance["emitted_flags"].append({"scope": {"run_id": rid}, "code": "battery.assist"})
            log.append({"pass": pass_id, "model": model, "run_id": rid, "kind": kind, "meter_samples_halved": n})
            continue
        else:
            raise ValueError(kind)
        for code in codes:
            acceptance["excluding"].append({"scope": "member", "run_id": rid, "code": code})
            acceptance["emitted_flags"].append({"scope": {"run_id": rid}, "code": code})
        log.append({"pass": pass_id, "model": model, "run_id": rid, "kind": kind, "exclusion_codes": codes})
    _write(archive / "derived/b6-acceptance.json", acceptance)


def build(root, name):
    world, seed, defects = CAMPAIGNS[name]
    root.mkdir(parents=True)
    log = []
    original = export_runs.export
    design_models = ba.read_json(FIXTURES / "campaign_design.json")["models"]

    def export_with_defects(archive, plan, registration, private, export_dir, **kw):
        if defects:
            pass_id = 1 if Path(archive).name.endswith("p1") else 2
            plant(Path(archive), kw["acceptance_record"], design_models, pass_id, defects, log)
        return original(archive, plan, registration, private, export_dir, **kw)

    export_runs.export = export_with_defects
    try:
        manifest = archive_campaign(root, world=world, seed=seed, non_claim=False, release="none",
                                    pass_duration_scales=PASS_SCALES, clock_latency_ms=CLOCK_LATENCY_MS)
    finally:
        export_runs.export = original
    _write(root / "manifest.json", manifest)
    _write(root / "build.json", {"name": name, "world": world, "seed": seed, "defects": log,
                                 "pass_duration_scales": PASS_SCALES, "clock_latency_ms": CLOCK_LATENCY_MS})
    return manifest


def run_both(root, manifest):
    """Every stage of both sides, in the desk's order, with key release by file copy in between."""
    o = root / "out"
    o.mkdir()
    private = root / "private-keys/bytes/blinding"
    released = root / "released-keys/bytes/blinding"
    assert list(released.iterdir()) == []
    analysis = [sys.executable, str(ROOT / "scripts/bytes_analyze.py"),
                "--export", str(root / "export"), "--manifest", str(root / "manifest.json")]
    twin = [sys.executable, str(ROOT / "scripts/bytes_twin.py"),
            "--export-dir", str(root / "export"), "--manifest", str(root / "manifest.json")]
    for session in manifest["sessions"]:
        twin += ["--archive", session["archive"]]

    def run(tag, command):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        (o / (tag + ".exit")).write_text(str(result.returncode) + "\n")
        (o / (tag + ".stdout")).write_text(result.stdout)
        (o / (tag + ".stderr")).write_text(result.stderr)
        return result.returncode

    run("a-blinded", analysis + ["--stage", "blinded", "--out", str(o / "a-blinded")])
    run("t-blinded", twin + ["--stage", "blinded", "--out", str(o / "t-blinded.json")])
    # Stage 1 before any release must refuse on both sides.
    run("a-fit-nokeys", analysis + ["--stage", "fit", "--key-dir", str(released), "--out", str(o / "a-fit-nokeys")])
    run("t-1-nokeys", twin + ["--stage", "1", "--key-dir", str(released), "--out", str(o / "t-1-nokeys.json")])
    # Stage-1 release: the fit set's keys and the NEG-8 reference key (Addendum 3 item 1).
    fit_keys = {"neg8_reference", *(m["model"] + "|bytes-synthetic|512" for m in manifest["models"] if m["role"] == "fit")}
    for name in sorted({"pack.json", *(blinding._config_filename(k) for k in fit_keys)}):
        shutil.copyfile(private / name, released / name)
    run("a-fit", analysis + ["--stage", "fit", "--key-dir", str(released), "--out", str(o / "a-fit")])
    run("t-1", twin + ["--stage", "1", "--key-dir", str(released), "--out", str(o / "t-1.json")])
    predictions = o / "a-fit/predictions.json"
    # Stage 2 with only the fit keys released must refuse on both sides (Addendum 3 item 4, D7).
    run("a-held-fitkeys", analysis + ["--stage", "heldout", "--key-dir", str(released), "--predictions", str(predictions),
                                      "--out", str(o / "a-held-fitkeys")])
    run("t-2-fitkeys", twin + ["--stage", "2", "--key-dir", str(released), "--out", str(o / "t-2-fitkeys.json")])
    # Stage-2 release: every key.
    for path in sorted(private.glob("*.json")):
        shutil.copyfile(path, released / path.name)
    run("a-held", analysis + ["--stage", "heldout", "--key-dir", str(released), "--predictions", str(predictions),
                              "--out", str(o / "a-held")])
    run("t-2", twin + ["--stage", "2", "--key-dir", str(released), "--out", str(o / "t-2.json")])


def setUpModule():
    WORK["dir"] = tempfile.TemporaryDirectory(prefix="bytes-agreement-")
    WORK["root"] = Path(WORK["dir"].name)


def tearDownModule():
    WORK["dir"].cleanup()


def campaign(name):
    if name not in WORK:
        root = WORK["root"] / name
        manifest = build(root, name)
        run_both(root, manifest)
        WORK[name] = compare_campaign(root)
    return WORK[name]


def describe(row):
    return (f"{row['stage']} {row['group']} {row['key']}: analysis={row['a']!r} twin={row['t']!r}"
            + (f" |a-t|={row['abs']:.3e} bar={row['bar']:.3e}" if "abs" in row else ""))


class AgreementTests(unittest.TestCase):
    """Every campaign, every stage: zero differences above the bar; the under-bar count is printed."""

    def check(self, name, expected_words, expected_h2):
        R = campaign(name)
        above = R.above()
        counts = R.counts()
        self.assertEqual(above, [], f"{name}: {len(above)} above the bar:\n" + "\n".join(describe(r) for r in above[:40]))
        # One count per campaign for the differences under the bar (Addendum 8.1), not classified.
        print(f"\nagreement {name}: compared {counts['compared']}, equal {counts['equal']}, "
              f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}")
        words = [r for r in R.rows if r["key"] == "word" and r["stage"] == "heldout"]
        self.assertEqual(len(words), expected_words)
        self.assertTrue(all(r["status"] == "equal" for r in words))
        exits = {r["key"]: (r["a"], r["t"]) for r in R.rows if r["group"] == "exit"}
        self.assertEqual(exits["blinded"], (0, 0))
        self.assertEqual(exits["fit/stage1"], (0, 0))
        self.assertEqual(exits["heldout/stage2"], (0, 0))
        self.assertEqual(exits["fit/stage1 before any release (must refuse)"], (1, 1))
        self.assertEqual(exits["heldout/stage2 with fit-only keys (must refuse)"], (1, 1))
        ks = {r["group"]: (r["a"], r["t"]) for r in R.rows if r["key"] == "k" and r["stage"] == "heldout"}
        self.assertEqual(ks, expected_h2)
        return R

    def test_bytes_world(self):
        # 7 held-out models x 3 boundaries x (2 passes + their mean) = 63 primary-and-description words.
        self.check("bytes", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                 "h2/rest/passes_mean": (11, 11)})

    def test_resident_world(self):
        self.check("resident", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                    "h2/rest/passes_mean": (11, 11)})

    def test_time_world(self):
        self.check("time", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                "h2/rest/passes_mean": (11, 11)})

    def test_defects_campaign(self):
        R = self.check("defects", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                       "h2/rest/passes_mean": (11, 11)})
        # D5 restores cooldown, but FIX-573's invalid-anchor repeat stays out
        # on both primary and flagged-inclusive lines of both implementations.
        kept = {r["group"]: r for r in R.rows if r["key"] == "n_b" and r["stage"] == "heldout"}
        self.assertEqual(kept["cell/qwen3-8b-4bit/pass1/rails/gross"]["a"], 9)
        self.assertEqual(kept["cell/qwen3-8b-4bit/pass1/rails/flagged_inclusive"]["a"], 10)
        self.assertEqual(kept["cell/qwen3-14b-4bit/pass1/rails/flagged_inclusive"]["a"], 9)
        repeats = {r['group']: r for r in R.rows if r['key'] == 'n_r' and r['stage'] == 'heldout'}
        for variant in ('gross', 'flagged_inclusive'):
            row = repeats['cell/qwen3-8b-4bit/pass1/rails/' + variant]
            self.assertEqual((row['a'], row['t']), (9, 9))
        without = [r for r in R.rows if "/without_assisted" in r["group"] and r["key"] == "status"]
        self.assertTrue(without)
        self.assertTrue(all(r["a"] == r["t"] == ("unavailable" if r["stage"] == "blinded" else "computed")
                            for r in without))

    def test_minimum_campaign_one_pass_refused(self):
        # Addendum 7 D9: 32B's pass 1 refuses; its point is pass 2, labelled one_pass; H2 is fitted on
        # ten models and the two-pass sensitivity line is printed beside it on both sides.
        # 63 words less 32B's three pass-1 description words (that pass refused): 60.
        R = self.check("minimum", 60, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                       "h2/rest/passes_mean": (11, 11)})
        labels = {r["group"]: r for r in R.rows if r["key"] == "pass_label" and r["stage"] == "heldout"}
        self.assertEqual(labels["point/qwen3-32b-4bit/mean/rails/gross"]["a"], "one_pass")
        self.assertEqual(labels["point/qwen3-8b-4bit/mean/rails/gross"]["a"], "pass_mean")
        statuses = {r["group"]: r for r in R.rows if r["key"] == "status" and r["stage"] == "heldout"}
        self.assertEqual(statuses["cell/qwen3-32b-4bit/pass1/rails/gross"]["a"], "unavailable")
        sensitivity = [r for r in R.rows if "two_pass_sensitivity" in r["group"] and r["key"] == "n"]
        self.assertEqual({(r["a"], r["t"]) for r in sensitivity}, {(9, 9)})


class FenceTests(unittest.TestCase):
    """The twin shares no code with the analysis (R8 item 4)."""

    def test_twin_imports_only_the_standard_library(self):
        tree = ast.parse((ROOT / "scripts/bytes_twin.py").read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported - sys.stdlib_module_names, set())
        self.assertNotIn("joulewise", imported)
        self.assertNotIn("scripts", imported)

    def test_twin_runs_with_joulewise_unimportable(self):
        code = ("import sys, runpy; sys.modules['joulewise'] = None\n"
                "m = runpy.run_path(sys.argv[1], run_name='bytes_twin_fenced')\n"
                "assert not any(n == 'joulewise' or n.startswith('joulewise.') for n, v in sys.modules.items() if v)\n"
                "print(m['student_t_critical_95'](9))\n")
        result = subprocess.run([sys.executable, "-I", "-c", code, str(ROOT / "scripts/bytes_twin.py")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "2.262")

    def test_d8_block5_t_table_reproduced_not_imported(self):
        # Every df the library answers, including its floor rule for unlisted df and above 120.
        for df in range(1, 200):
            self.assertEqual(bt.student_t_critical_95(df), aggregate.student_t_critical_95(df), df)
        self.assertEqual(bt.T_TABLE_95, aggregate._T_CRITICAL_95)
        with self.assertRaises(ValueError):
            bt.student_t_critical_95(0)


if __name__ == "__main__":
    unittest.main()
