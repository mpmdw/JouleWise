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

Addendum 9 (NR1, the meter label-offset alternative) and B4 (the withheld store, B6 ruling Q1) add:
C_j and the offset interval's endpoints at 1% of that alternative's own half-width, t SE_j + C_j
(``bar_offset_interval``; the labelled OLS alternative at 1% of its own); the per-point bound at the
energy bar (J) and the power bar (W); the sensitivities at the no-half-width bar; the zero/sign
decisions under both intervals as labels with the usual slack; units, flag presence, scope and
disclosure presence (and the 22 and 25 ms the disclosure states), `missing` statuses, pass labels
and withheld row counts exactly.  Two campaigns join the five: the edge-locked meter of Addendum
9.1 (every run flips a whole sample) and a withholding campaign on R6's six sub-packs with one
withheld file missing, both of one model's missing and one optional pass never collected, run
through the post-commit blinded stage as well.

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
from tests.git_fixture import init_git_fixture

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
# bytes/resident/time are the three truths; defects plants the review's five defects (p08);
# minimum removes six of one model's pass-1 repeats so that one pass refuses (Addendum 7 D9).
DEFECTS = [
    (1, "Qwen3-14B-4bit", 15, "lost_member"),        # quad unit 1: bundle and stored reduction gone
    (1, "Qwen3-4B-4bit", 3, "token_mismatch"),        # repeat: observed 511 tokens
    (1, "Qwen3-30B-A3B-4bit", 0, "battery_assist"),   # repeat: meter halved over decode, flag battery.assist
    (2, "Qwen3-8B-4bit", 2, "thermal"),               # repeat: thermal.os_level_nonzero
    (1, "Qwen3-8B-4bit", 20, "cooldown"),             # quad unit 2: member.cooldown_cap_hit (NUMBER class)
]
DEFECTS_MINIMUM = [(1, "Qwen3-32B-4bit", i, "strict_validation") for i in range(6)]
# Addendum 9 item 1: the generator's NR1 knobs (samples 50 ms into the interval, science-run edges
# at a uniform phase, a 10 ms minimum receive latency) are its defaults, so every campaign below is
# the ruled fixture in which a constant label offset flips a whole sample with probability
# delta / dt = 10 ms / 100 ms per run.  "resident" (seed 3100) is the world of the NR1 regression
# tests.test_bytes_analysis.ProductionArchiveTests.test_nr1_offset_term_covers_constant_label_offset.
NR1_KNOBS = {"sample_phase_ms": 50, "edge_phase": True, "min_receive_latency_ms": 10.0}
# Addendum 9.1's pre-ruling edge-locked meter, as closely as the generator's knobs allow: science-run
# edges on the sample grid (edge_phase False) and the sample 95 ms into its 100 ms interval, so the
# sample before each decode edge sits 5 ms before it and the 10 ms label offset carries it across
# (a baseline sample enters at the start, a decode sample leaves at the end): whole-sample flips on
# every run with certainty, Addendum 9.1's "with certainty, which no free-running meter clock can do".
# 95 ms is the largest phase that keeps 5 ms of margin on each side of the offset against the
# fitted label offset's own error (about 0.01 ms, B2-NR1-RULING "fitted label offset 9.991 ms").
EDGE_LOCKED_KNOBS = {"sample_phase_ms": 95, "edge_phase": False, "min_receive_latency_ms": 10.0}
# B4 withholding campaign (R6's six sub-packs, one session per sub-pack and pass; B6 ruling Q1):
# the withheld store of s2 pass 2 (30B-A3B's held-out rows; 8B is a fit model) is missing, both
# stores of s6 (Qwen3.5-122B, an MoE model) are missing, and s4 pass 2 (32B, 8B-8bit) was never
# collected (R6's optional pass).
WITHHELD_KNOBS = {"subpack_sessions": True, "uncollected_sessions": ("bytes-s4-p2",)}
MISSING_STORES = ("bytes-s2-p2", "bytes-s6-p1", "bytes-s6-p2")
# name: (world, seed, planted defects, generator knobs, withheld stores removed after export).
CAMPAIGNS = {
    "bytes": ("bytes", 1100, [], NR1_KNOBS, ()),
    "resident": ("resident", 3100, [], NR1_KNOBS, ()),
    "time": ("time", 2100, [], NR1_KNOBS, ()),
    "defects": ("bytes", 1100, DEFECTS, NR1_KNOBS, ()),
    "minimum": ("bytes", 1100, DEFECTS_MINIMUM, NR1_KNOBS, ()),
    "edge_locked": ("resident", 3100, [], EDGE_LOCKED_KNOBS, ()),
    "withheld": ("bytes", 1100, [], {**NR1_KNOBS, **WITHHELD_KNOBS}, MISSING_STORES),
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


def bar_offset_interval(offset_lower, offset_upper):
    """Addendum 9's labelled alternative beta_j +/- (t SE_j + C_j): C_j and the interval's endpoints
    compare at 1% of that printed alternative's own half-width, t SE_j + C_j (Addendum 8.1, "1% of
    the cell's half-width", applied to the alternative; the HC3 interval gives the registered one, the
    labelled OLS interval its own).  The half-width is formed from the analysis's endpoints, as every
    other bar is."""
    return bar_coefficient((offset_upper - offset_lower) / 2)


# The sensitivity dbeta_j/ddelta per ms (Addendum 9 item 4) and the per-point sensitivity in W have no
# half-width: bar_no_half_width in the column's unit.  The per-point bound in J has the cell's (h + B)
# (bar_energy); in W, the point's power half-width (bar_power).
WITHHELD_MISSING = "bytes.withheld_missing"


def states_delta_bound(text):
    """The numbers the disclosure states (Addendum 9 item 4: 22 to 25 ms at 50 SPS, block-6 M13):
    compared exactly; the wording is representation and is not compared."""
    import re
    numbers = {int(n) for n in re.findall(r"\b(\d+)\s*(?:to\s*\d+\s*)?ms\b", text or "")}
    numbers |= {int(n) for n in re.findall(r"\b\d+\s*to\s*(\d+)\s*ms\b", text or "")}
    return (22 in numbers, 25 in numbers, "M13" in (text or ""))


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
    if row["boundary"] != "rails":
        # Addendum 9: the pass's coherent-offset bound (J, at the cell's energy bar) and signed
        # sensitivity (W, no half-width); rails has neither (checked in compare_cells).
        offset = est.get("meter_offset") or {}
        R.number(stage, g, "meter_offset_bound_j", row.get("meter_offset_bound_j"), offset.get("bound_j"), bar_energy(hb))
        R.number(stage, g, "meter_offset_sensitivity_w", row.get("meter_offset_sensitivity_w"), offset.get("sensitivity_w"), None)


def compare_missing(R, stage, g, row, est):
    """B6 ruling Q1: a `missing` pass or point: the flag, the sidecar's withheld row counts, exactly."""
    R.exact(stage, g, "flag:" + WITHHELD_MISSING, WITHHELD_MISSING in (row.get("flags") or []),
            WITHHELD_MISSING in (est.get("flags") or []))
    for key in ("withheld_row_count", "withheld_config_row_count"):
        if key in row or key in est:
            R.exact(stage, g, key, row.get(key), est.get(key))


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
        if row["status"] == "missing" or est.get("status") == "missing":
            # B6 ruling Q1: the pass prints `missing` with the flag and the sidecar's counts.
            R.exact(stage, g, "status", row["status"], est.get("status"))
            compare_missing(R, stage, g, row, est)
            continue
        if b == "rails":
            R.exact(stage, g, "no meter offset terms on rails (Addendum 9: rails has no C term)",
                    row.get("meter_offset_bound_j") is None, est.get("meter_offset") is None)
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
        if p.get("status") == "missing" or q.get("status") == "missing":
            # B6 ruling Q1: every pass's withheld file missing: the model prints `missing`, no point.
            R.exact(stage, g, "status", p.get("status"), q.get("status"))
            R.exact(stage, g, "pass_label", p.get("pass_status"), q.get("label"))
            R.exact(stage, g, "n_passes", p.get("n_passes"), q.get("passes_computed"))
            compare_missing(R, stage, g, p, q)
            continue
        R.exact(stage, g, "status", "computed" if a_ok else "unavailable", "computed" if t_ok else "unavailable")
        if not (a_ok and t_ok):
            continue
        # Addendum 7 D9: the pass label and the number of computed passes; B6 ruling Q1: the flag of a
        # missing withheld file is carried on the one_pass point.
        R.exact(stage, g, "pass_label", {"two_pass": "pass_mean", "one_pass": "one_pass"}.get(p.get("pass_status")),
                q.get("label"))
        R.exact(stage, g, "n_passes", p.get("n_passes"), q.get("passes_computed"))
        R.exact(stage, g, "flag:" + WITHHELD_MISSING, WITHHELD_MISSING in (p.get("flags") or []),
                WITHHELD_MISSING in (q.get("flags") or []))
        hb = p["h_j"] + p["B_j"]
        T = p["duration_s"]
        if b != "rails":
            # Addendum 9 (cold disposition M1): the point's bound in J (pass-averaged, the energy bar),
            # in W (over the point's mean decode time, the power bar), and the sensitivity in W.
            R.number(stage, g, "meter_offset_bound_j", p.get("meter_offset_bound_j"), q.get("meter_offset_bound_j"), bar_energy(hb))
            R.number(stage, g, "meter_offset_bound_w", p.get("meter_offset_bound_w"), q.get("meter_offset_bound_w"),
                     bar_power(p["power_half_w"]))
            R.number(stage, g, "meter_offset_sensitivity_w", p.get("meter_offset_sensitivity_w"),
                     q.get("meter_offset_sensitivity_w"), None)
        else:
            R.exact(stage, g, "no meter offset terms on rails (Addendum 9)", p.get("meter_offset_bound_w") is None,
                    q.get("meter_offset_bound_w") is None)
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
            R.exact(stage, g, "word", row.get("word") if row["role"] == "heldout" else None, "absent:" + str(th.get("status")))
            continue
        if row.get("status") == "missing" or tm.get("status") == "missing":
            # B6 ruling Q1: a `missing` model has no H1 word; the flag is carried.
            R.exact(stage, g, "status", row.get("status"), tm.get("status"))
            R.exact(stage, g, "word", row.get("word"), tm.get("word"))
            compare_missing(R, stage, g, row, tm)
            continue
        if row["role"] == "heldout":
            R.exact(stage, g, "word", row["word"], tm["word"])
            # Addendum 7 D9 (a) and B6 ruling Q1: the one_pass label and the carried flag.
            R.exact(stage, g, "pass_label", {"two_pass": "pass_mean", "one_pass": "one_pass"}.get(row.get("pass_status")),
                    tm.get("label"))
            R.exact(stage, g, "flag:" + WITHHELD_MISSING, WITHHELD_MISSING in (row.get("flags") or []),
                    WITHHELD_MISSING in (tm.get("flags") or []))
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
        if row.get("status") == "missing" or tm.get("missing_models"):
            # B6 ruling Q1: an MoE model without a point leaves the answer `missing`, naming the models.
            R.exact(stage, f"moe/{b}/passes_mean", "missing_models",
                    sorted(canon(m["model"]) for m in row.get("missing_models") or []), sorted(tm.get("missing_models") or []))
            compare_missing(R, stage, f"moe/{b}/passes_mean", row, tm)
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


def _interval(R, stage, g, name, a_fit, idx, t_iv, *, floor=0.0, offset=False):
    """One coefficient: estimate and HC3 interval at 1% of the HC3 half-width; the labelled OLS
    interval beside it at 1% of its own half-width.  floor: the float-noise floor of the bar (the
    rest model only, from its printed VIF); 0 for a fit that prints no VIF.  offset: Addendum 9's
    labelled alternative beside the coefficient (DC input and rest)."""
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
    if offset:
        _offset_alternative(R, stage, g, name, a_fit, idx, t_iv, floor=floor)
    elif "coefficient_C" in a_fit or "offset" in t_iv:
        R.exact(stage, g, name + ":no offset alternative on rails (Addendum 9)", "coefficient_C" in a_fit, "offset" in t_iv)


def _decision_near(lower, upper, bar):
    """A zero/sign decision rests on the endpoint nearest zero: slack when it is within the bar of 0."""
    return lower is not None and upper is not None and min(abs(lower), abs(upper)) <= bar


def _offset_alternative(R, stage, g, name, a_fit, idx, t_iv, *, floor=0.0):
    """Addendum 9 items 3 and 4 beside one coefficient at DC input or rest.  C_j and the offset
    interval's endpoints at 1% of the alternative's own half-width (bar_offset_interval); the labelled
    OLS alternative at 1% of its own; dbeta/ddelta at the no-half-width bar; units exact; the
    zero/sign decisions under both intervals as labels with the usual slack."""
    o = t_iv.get("offset") or {}
    a_flag, t_flag = a_fit.get("systematics_flag"), o.get("systematics_flag")
    R.exact(stage, g, name + ":systematics_flag", a_flag is not None, t_flag is not None,
            None if (a_flag is None) == (t_flag is None) else f"analysis: {a_flag}; twin: {t_flag}")
    a_sflag, t_sflag = a_fit.get("sensitivity_flag"), o.get("sensitivity_flag")
    R.exact(stage, g, name + ":sensitivity_flag", a_sflag is not None, t_sflag is not None,
            None if (a_sflag is None) == (t_sflag is None) else f"analysis: {a_sflag}; twin: {t_sflag}")
    R.exact(stage, g, name + ":sensitivity_units", (a_fit.get("sensitivity_units") or [None] * (idx + 1))[idx],
            o.get("sensitivity_units"))
    # The registered decision rests on the HC3 endpoint nearest zero, at the HC3 bar.
    half = (a_fit["intervals"][idx][1] - a_fit["intervals"][idx][0]) / 2
    bar = max(bar_coefficient(half), floor)
    R.label_with_slack(stage, g, name + ":coefficient_decision", a_fit["coefficient_decisions"][idx], o.get("coefficient_decision"),
                       _decision_near(a_fit["intervals"][idx][0], a_fit["intervals"][idx][1], bar))
    if a_flag is None and t_flag is None:
        lo, hi = a_fit["offset_intervals"][idx]
        bar_off = max(bar_offset_interval(lo, hi), floor)
        R.number(stage, g, name + ":coefficient_C", a_fit["coefficient_C"][idx], o.get("coefficient_C"), bar_off)
        R.number(stage, g, name + ":offset_lower", lo, o.get("offset_lower"), bar_off)
        R.number(stage, g, name + ":offset_upper", hi, o.get("offset_upper"), bar_off)
        lo_ols, hi_ols = a_fit["offset_ols_intervals"][idx]
        bar_ols = max(bar_offset_interval(lo_ols, hi_ols), floor)
        R.number(stage, g, name + ":offset_ols_lower", lo_ols, o.get("offset_ols_lower"), bar_ols)
        R.number(stage, g, name + ":offset_ols_upper", hi_ols, o.get("offset_ols_upper"), bar_ols)
        R.label_with_slack(stage, g, name + ":offset_decision", a_fit["offset_decisions"][idx], o.get("offset_decision"),
                           _decision_near(lo, hi, bar_off))
    if a_sflag is None and t_sflag is None:
        R.number(stage, g, name + ":d_beta_d_delta_per_ms", a_fit["d_beta_d_delta_per_ms"][idx], o.get("d_beta_d_delta_per_ms"), None)


def compare_offset_rows(R, stage, g, row, th):
    """The H2 row's scope labels and disclosure (Addendum 9 items 2 and 4): presence exactly, and
    the numbers the disclosure states (22 and 25 ms, M13) exactly; wording is not compared.  The
    primary-row decisions (`coefficient_decision`, `offset_decision`) per primary coefficient."""
    offset = BMAP.get(row["boundary"]) != "rails"
    fits = [f for f in (row.get("two_term"), row.get("resident_extended"), row.get("tier"), row.get("rest"))
            if isinstance(f, dict) and f.get("status") == "computed"]
    R.exact(stage, g, "interval_scope present", any("interval_scope" in f for f in fits) or not fits,
            bool(th.get("interval_scope")) or not fits)
    R.exact(stage, g, "offset_scope present", any("offset_scope" in f for f in fits) if fits else offset,
            bool(th.get("offset_scope")))
    R.exact(stage, g, "offset_disclosure present", "offset_disclosure" in row, "offset_disclosure" in th)
    if "offset_disclosure" in row and "offset_disclosure" in th:
        R.exact(stage, g, "offset_disclosure states 22 ms, 25 ms, M13", states_delta_bound(row["offset_disclosure"]),
                states_delta_bound(th["offset_disclosure"]))
    if offset and th.get("status") == "ok":
        R.exact(stage, g, "resident_adds_nothing_offset present", "resident_adds_nothing_offset" in row,
                "resident_adds_nothing_offset" in (th.get("resident_extended") or {}))
    # The primary rows carry the decision pair per coefficient (deviations have none).
    twin_terms = {}
    if th.get("status") == "ok":
        twin_terms = {"epsilon": th["simple"]["epsilon_j_per_GB"]}
        if th.get("resident_extended"):
            twin_terms.update({"extended_epsilon": th["resident_extended"]["epsilon_j_per_GB"], "rho": th["resident_extended"]["rho_j_per_GB"]})
        if th.get("tier"):
            twin_terms.update({"tier_epsilon": th["tier"]["epsilon_j_per_GB"], "tier_rho": th["tier"]["rho_j_per_GB"]})
        if th.get("rest_model"):
            twin_terms.update({"rest_epsilon": th["rest_model"]["epsilon_rest_j_per_GB"], "lambda": th["rest_model"]["lambda"]})
    for item in row.get("primary_intervals") or []:
        term = item["term"]
        if term not in twin_terms or "coefficient_decision" not in item:
            continue
        t_iv = twin_terms[term]
        o = t_iv.get("offset") or {}
        half = (item["upper"] - item["lower"]) / 2
        R.label_with_slack(stage, g + "/primary", term + ":coefficient_decision", item["coefficient_decision"],
                           o.get("coefficient_decision") if offset else t_iv.get("decision"),
                           _decision_near(item["lower"], item["upper"], bar_coefficient(half)))
        if offset and item.get("offset_intervals") and o.get("coefficient_C") is not None:
            lo, hi = item["offset_intervals"]
            R.label_with_slack(stage, g + "/primary", term + ":offset_decision", item["offset_decision"], o.get("offset_decision"),
                               _decision_near(lo, hi, bar_offset_interval(lo, hi)))
            R.number(stage, g + "/primary", term + ":coefficient_C", item["coefficient_C"], o.get("coefficient_C"), bar_offset_interval(lo, hi))


def compare_h2_fit(R, stage, g, row, th, own_half, b, rest_inputs=None):
    """One H2 fit group (primary, or the two-pass sensitivity line).  rest_inputs: {model: (P_rest,
    BW, P_rails)} of the analysis's points, for the rest model's coefficient scales."""
    R.exact(stage, g, "n", row["n"], th.get("n"))
    compare_offset_rows(R, stage, g, row, th)
    if row["two_term"]["status"] != "computed" or th.get("status") != "ok":
        R.exact(stage, g, "status", row["two_term"]["status"], th.get("status"))
        return
    offset = b != "rails"      # Addendum 9: the alternative at DC input and rest; rails has no C term
    R.exact(stage, g, "simple:df", row["two_term"]["df"], th["simple"]["df"])
    _interval(R, stage, g, "simple:P0", row["two_term"], 0, _p0(th["simple"], "P0", row["two_term"], 0), offset=offset)
    _interval(R, stage, g, "simple:epsilon", row["two_term"], 1, th["simple"]["epsilon_j_per_GB"], offset=offset)
    ext_a, ext_t = row["resident_extended"], th.get("resident_extended")
    R.exact(stage, g, "extended:status", ext_a["status"], "computed" if ext_t else "refused")
    if ext_a["status"] == "computed" and ext_t:
        R.exact(stage, g, "extended:df", ext_a["df"], ext_t["df"])
        _interval(R, stage, g, "extended:P0", ext_a, 0, _p0(ext_t, "P0", ext_a, 0), offset=offset)
        _interval(R, stage, g, "extended:epsilon", ext_a, 1, ext_t["epsilon_j_per_GB"], offset=offset)
        _interval(R, stage, g, "extended:rho", ext_a, 2, ext_t["rho_j_per_GB"], offset=offset)
        lo, hi = ext_a["intervals"][2]
        slack = bar_coefficient((hi - lo) / 2)
        near = min(abs(lo), abs(hi), abs(ext_a["coefficients"][2])) <= slack
        R.label_with_slack(stage, g, "resident_adds_nothing", row["resident_adds_nothing"], ext_t["resident_adds_nothing"], near)
        if offset and ext_a.get("systematics_flag") is None and "resident_adds_nothing_offset" in row:
            # Addendum 9 item 3: "resident adds nothing" under the offset interval, with slack when
            # the offset endpoint nearest zero is within its bar of zero.
            lo, hi = ext_a["offset_intervals"][2]
            near = min(abs(lo), abs(hi), abs(ext_a["coefficients"][2])) <= bar_offset_interval(lo, hi)
            R.label_with_slack(stage, g, "resident_adds_nothing_offset", row["resident_adds_nothing_offset"],
                               ext_t.get("resident_adds_nothing_offset"), near)
    tier_a, tier_t = row["tier"], th.get("tier")
    R.exact(stage, g, "tier:status", tier_a["status"], "computed" if tier_t else "refused")
    if tier_a["status"] == "computed" and tier_t:
        R.exact(stage, g, "tier:df", tier_a["df"], tier_t["df"])
        _interval(R, stage, g, "tier:P0", tier_a, 0, _p0(tier_t, "P0", tier_a, 0), offset=offset)
        _interval(R, stage, g, "tier:epsilon", tier_a, 1, tier_t["epsilon_j_per_GB"], offset=offset)
        _interval(R, stage, g, "tier:rho", tier_a, 2, tier_t["rho_j_per_GB"], offset=offset)
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
            _interval(R, stage, g, "rest:c", rm, 0, _p0(tr, "c", rm, 0), floor=floors[0], offset=True)
            _interval(R, stage, g, "rest:epsilon_rest", rm, 1, tr["epsilon_rest_j_per_GB"], floor=floors[1], offset=True)
            _interval(R, stage, g, "rest:lambda", rm, 2, tr["lambda"], floor=floors[2], offset=True)
            vif_bar = bar_two_significant_figures(vif_a, vif_t) if vif_a is not None and vif_t is not None else None
            R.number(stage, g, "rest:vif", vif_a, vif_t, vif_bar)
    for item in row["loo_description"]:
        m = canon(item["model"])
        tl = (th.get("leave_one_out") or {}).get(m) or {}
        R.exact(stage, g + "/loo", m + ":status", item["status"], "computed" if tl else "refused")
        if item["status"] == "computed" and tl:
            R.number(stage, g + "/loo", m, item["predicted_w"], tl.get("predicted_w"), bar_power(own_half.get(m, 0.0)))


def _p0(t_fit, key, a_fit, idx):
    """P0 and c are printed and not counted (Addendum 3 item 6); the twin now prints their intervals
    too (Addendum 9: every coefficient, intercepts included, carries the alternative), so they compare
    like every other coefficient."""
    return t_fit[key]


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
              "a-fit-nokeys", "t-1-nokeys", "a-blinded-post", "t-blinded-post") if (o / (tag + ".exit")).exists()}
    R.exact("refusal", "exit", "blinded", exits.get("a-blinded"), exits.get("t-blinded"))
    if "a-blinded-post" in exits or "t-blinded-post" in exits:
        # Lead ruling 2026-10-20 items 3 and 4: the post-commit blinded run on the withheld rows never
        # refuses for a missing file.
        R.exact("refusal", "exit", "blinded after the stage-1 commit (withheld rows; never refuses)",
                exits.get("a-blinded-post"), exits.get("t-blinded-post"))
        tb = load(o / "t-blinded-post.json")
        if tb is not None and (o / "a-blinded-post").is_dir():
            rows = load(o / "a-blinded-post/blinded_pass_estimates.json")
            compare_cells(R, "blinded-post", rows, tb)
            ap = load(o / "a-blinded-post/model_estimates.json")
            compare_points(R, "blinded-post", ap, tb)
            compare_h1(R, "blinded-post", load(o / "a-blinded-post/h1.json"), load(o / "a-blinded-post/moe.json"), tb, None)
            compare_h2(R, "blinded-post", load(o / "a-blinded-post/h2.json"), tb, ap)
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
    world, seed, defects, knobs, missing_stores = CAMPAIGNS[name]
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
                                    pass_duration_scales=PASS_SCALES, clock_latency_ms=CLOCK_LATENCY_MS, **knobs)
    finally:
        export_runs.export = original
    # B6 ruling Q1: a withheld file goes missing after the export wrote it (a file-custody fault);
    # the sidecar's count-only locator stays.
    removed = []
    for session_id in missing_stores:
        sidecar = next(root.glob(f"export/*/{session_id}.session.json"))
        info = ba.read_json(sidecar)["blinding"]["withheld"]
        store = sidecar.parent / info["path"]
        store.unlink()
        removed.append({"session_id": session_id, "store": str(store), "row_count": info["row_count"]})
    _write(root / "manifest.json", manifest)
    _write(root / "build.json", {"name": name, "world": world, "seed": seed, "defects": log, "knobs": knobs,
                                 "missing_stores": removed,
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
    if any(ba.read_json(p).get("blinding", {}).get("withheld") for p in (root / "export").rglob("*.session.json")):
        # Lead ruling 2026-10-20 item 3: after the stage-1 commit and before any held-out key is
        # released, both implementations run on the blinded held-out rows (rails only).  The commit
        # is the desk's git commit of the stage-1 output; its hash admits the withheld store.
        init_git_fixture(o / "a-fit", "-q")
        subprocess.run(["git", "add", "."], cwd=o / "a-fit", check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=BYTES Synthetic", "-c", "user.email=synthetic@example.invalid",
                        "commit", "-qm", "Freeze synthetic stage-1 predictions"], cwd=o / "a-fit", check=True, capture_output=True)
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=o / "a-fit", check=True, capture_output=True,
                                text=True).stdout.strip()
        (o / "stage1-commit").write_text(commit + "\n")
        run("a-blinded-post", analysis + ["--stage", "blinded", "--stage1-commit", commit, "--out", str(o / "a-blinded-post")])
        run("t-blinded-post", twin + ["--stage", "blinded", "--stage1-commit", commit, "--out", str(o / "t-blinded-post.json")])
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


def whole_sample_flips(name):
    """Addendum 9 item 1: the science runs whose mapped DC-input decode energy differs from the
    generator's truth (DC = 2 x rails) by more than the integer-microwatt payload rounding can
    explain (at most 0.5 uW x T): a whole 100 ms sample taken or lost at a decode edge.  Read with
    the twin's own meter reader and export reader after every key is released."""
    root = WORK["root"] / name
    manifest = load(root / "manifest.json")
    released = root / "released-keys/bytes/blinding"
    flips = runs = 0
    largest = 0.0
    for session in manifest["sessions"]:
        archive = bt.load_archive(session["archive"])
        rows = bt.read_export(next(root.glob(f"export/*/{session['session_id']}.runs.csv")))
        rows = bt.unblind(rows, released, {r["config_key"] for r in rows if r["role"] == "science"})
        for row in rows:
            if row["role"] != "science":
                continue
            dc = bt.dc_join(archive, row["run_id"])
            error = abs(dc["decode_energy_j"] - 2 * row["phase_decode_j"])
            runs += 1
            largest = max(largest, error)
            flips += error > 0.5e-6 * row["dur_decode_s"]
    return {"runs": runs, "flips": flips, "largest_error_j": largest,
            "label_offset_s": manifest["synthetic_parameters"]["min_receive_latency_ms"] / 1000,
            "sample_interval_s": kp.STEP_MS[1] / 1000}


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
        self.check_offset_terms_exercised(name, R)
        return R

    def check_offset_terms_exercised(self, name, R):
        """Addendum 8.4: the Addendum 9 fields must move above their bars in every campaign, so a
        twin that omitted them (or printed zero) would fail: every C_j, every point's bound and
        every pass's bound and sensitivity, and every dbeta/ddelta, is larger than its own bar."""
        rows = [r for r in R.rows if r["stage"] == "heldout"]
        for key in ("coefficient_C", "offset_lower", "offset_upper", "meter_offset_bound_j", "meter_offset_bound_w",
                    "meter_offset_sensitivity_w"):
            hits = [r for r in rows if r["key"].split(":")[-1] == key and "abs" in r]
            self.assertTrue(hits, f"{name}: no {key} compared")
            self.assertTrue(all(abs(r["a"]) > r["bar"] for r in hits), f"{name}: a {key} within its own bar of zero")
        # dbeta/ddelta has the no-half-width bar with its 1e-6 absolute floor in the column's unit; rho's
        # sensitivity (J/GB per ms) is of order 1e-7 in these worlds, so the field is exercised by the
        # intercept and epsilon terms (W per ms and J/GB per ms, of order 1e-3 and 1e-5): most rows above.
        hits = [r for r in rows if r["key"].endswith(":d_beta_d_delta_per_ms") and "abs" in r]
        self.assertTrue(hits, f"{name}: no d_beta_d_delta_per_ms compared")
        self.assertGreater(sum(abs(r["a"]) > r["bar"] for r in hits), len(hits) / 2, name)
        # Rails has no C term (Addendum 9 item 3): both sides print none, and the comparer says so.
        rails = [r for r in rows if "rails" in r["key"] and r["key"].startswith("no ") or "no offset alternative on rails" in r["key"]]
        self.assertTrue(rails and all(r["status"] == "equal" and r["a"] is True for r in rails))
        self.assertTrue(all(r["status"] == "equal" for r in rows if r["key"].endswith("sensitivity_units")))
        self.assertTrue([r for r in rows if r["key"] == "offset_disclosure states 22 ms, 25 ms, M13"
                         and r["a"] == r["t"] == (True, True, True)])
        self.assertFalse([r for r in rows if r["key"].endswith(("systematics_flag", "sensitivity_flag")) and r["a"] is True])

    def check_flips(self, name, certain):
        """Addendum 9 item 1: the label offset flips a whole sample with probability delta / dt per
        run (within three binomial standard errors, the ruling's bar), or, on the edge-locked meter,
        on every run with certainty.  Printed for the record."""
        flips = whole_sample_flips(name)
        print(f"\nflips {name}: {flips['flips']} of {flips['runs']} runs, largest error {flips['largest_error_j']:.3f} J")
        if certain:
            self.assertEqual(flips["flips"], flips["runs"])
        else:
            p = flips["label_offset_s"] / flips["sample_interval_s"]
            n = flips["runs"]
            self.assertLessEqual(abs(flips["flips"] / n - p), 3 * math.sqrt(p * (1 - p) / n))
        return flips

    def test_bytes_world(self):
        # 7 held-out models x 3 boundaries x (2 passes + their mean) = 63 primary-and-description words.
        self.check("bytes", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                 "h2/rest/passes_mean": (11, 11)})

    def test_resident_world(self):
        # The NR1 regression's world (Addendum 9 item 1): about delta / dt = 10% of the runs take or
        # lose a whole sample; at this seed every registered decision survives the alternative
        # (every C_j is below the HC3 half-width of a coefficient whose interval excludes zero).
        R = self.check("resident", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                        "h2/rest/passes_mean": (11, 11)})
        self.check_flips("resident", certain=False)
        self.assertTrue([r for r in R.rows if r["key"].endswith(":offset_decision") and r["stage"] == "heldout"])

    def test_edge_locked_meter_flips_every_run_and_moves_decisions(self):
        # Addendum 9.1's pre-ruling edge-locked meter: the offset carries a sample across both decode
        # edges of every run, and the coherent bias moves the resident-extended and rest-model P0 /
        # epsilon decisions at DC input and rest from a sign to "contains zero" under the alternative.
        R = self.check("edge_locked", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                           "h2/rest/passes_mean": (11, 11)})
        self.check_flips("edge_locked", certain=True)
        moved = [r for r in R.rows if r["key"].endswith(":offset_decision") and r["stage"] == "heldout"
                 and r["a"] != next(x["a"] for x in R.rows if x["stage"] == r["stage"] and x["group"] == r["group"]
                                    and x["key"] == r["key"].replace(":offset_decision", ":coefficient_decision"))]
        self.assertTrue(moved, "no offset decision differs from its registered decision")
        self.assertTrue(all(r["status"] == "equal" for r in moved))
        print("\nedge_locked decisions moved: " + ", ".join(sorted(f"{r['group'].split('/')[1]} {r['key']}" for r in moved)))

    def test_withheld_campaign_missing_files_and_uncollected_pass(self):
        # B6 ruling Q1 through the CLI chain on R6's six sub-packs: s2 pass 2's withheld file missing
        # (30B-A3B: one_pass with the flag), both s6 files missing (Qwen3.5-122B: missing, no point, no
        # H1 word, the MoE answer missing), s4 pass 2 never collected (32B, 8B-8bit: one_pass without
        # the flag); nothing refuses, the post-commit blinded run included.  H2 is fitted on nine
        # models (k = 8, 8, 10 from what is printed as primary) and the two-pass sensitivity line on
        # the six models with two computed passes, whose tier fit refuses (n - p = 1).
        # Words: per boundary 3 x 3 (two-pass held-out models) + 3 x 2 (one-pass: mean and the
        # surviving pass) + 1 (the missing model's mean row, no word) = 16.
        R = self.check("withheld", 48, {"h2/rails/passes_mean": (8, 8), "h2/dc_input/passes_mean": (8, 8),
                                        "h2/rest/passes_mean": (10, 10)})
        exits = {r["key"]: (r["a"], r["t"]) for r in R.rows if r["group"] == "exit"}
        self.assertEqual(exits["blinded after the stage-1 commit (withheld rows; never refuses)"], (0, 0))
        rows = [r for r in R.rows if r["stage"] in ("heldout", "blinded-post")]
        labels = {r["group"]: r["a"] for r in rows if r["key"] == "pass_label" and r["group"].startswith("point/")
                  and r["group"].endswith("/rails/gross") and r["stage"] == "heldout"}
        self.assertEqual(labels["point/qwen3-30b-a3b-4bit/mean/rails/gross"], "one_pass")
        self.assertEqual(labels["point/qwen3-32b-4bit/mean/rails/gross"], "one_pass")
        self.assertEqual(labels["point/qwen3-8b-8bit/mean/rails/gross"], "one_pass")
        self.assertEqual(labels["point/qwen3.5-122b-a10b-4bit/mean/rails/gross"], "no_pass")
        self.assertEqual(labels["point/qwen3-14b-4bit/mean/rails/gross"], "pass_mean")
        flags = {r["group"]: r["a"] for r in rows if r["key"] == "flag:" + WITHHELD_MISSING and r["stage"] == "heldout"
                 and r["group"].startswith("point/") and r["group"].endswith("/rails/gross")}
        self.assertTrue(flags["point/qwen3-30b-a3b-4bit/mean/rails/gross"])
        self.assertTrue(flags["point/qwen3.5-122b-a10b-4bit/mean/rails/gross"])
        self.assertFalse(flags["point/qwen3-32b-4bit/mean/rails/gross"])
        self.assertFalse(flags["point/qwen3-8b-8bit/mean/rails/gross"])
        statuses = {r["group"]: r["a"] for r in rows if r["key"] == "status" and r["stage"] == "heldout"}
        self.assertEqual(statuses["cell/qwen3-30b-a3b-4bit/pass2/rails/gross"], "missing")
        self.assertEqual(statuses["cell/qwen3.5-122b-a10b-4bit/pass1/dc_input/gross"], "missing")
        self.assertEqual(statuses["point/qwen3.5-122b-a10b-4bit/mean/rest/gross"], "missing")
        self.assertEqual(statuses["h1/rails/passes_mean/qwen3.5-122b-a10b-4bit"], "missing")
        counts = {(r["group"], r["key"]): (r["a"], r["t"]) for r in rows if r["key"].startswith("withheld_")}
        self.assertEqual(counts[("cell/qwen3-30b-a3b-4bit/pass2/rails/gross", "withheld_row_count")], (50, 50))
        self.assertEqual(counts[("cell/qwen3-30b-a3b-4bit/pass2/rails/gross", "withheld_config_row_count")], (50, 50))
        self.assertEqual({r["a"] for r in rows if r["key"] == "answer"}, {"missing"})
        self.assertEqual({(tuple(r["a"]), tuple(r["t"])) for r in rows if r["key"] == "missing_models"},
                         {(("qwen3.5-122b-a10b-4bit",), ("qwen3.5-122b-a10b-4bit",))})
        sensitivity = {(r["stage"], r["group"]): (r["a"], r["t"]) for r in rows if "two_pass_sensitivity" in r["group"] and r["key"] == "n"}
        self.assertEqual(set(sensitivity.values()), {(6, 6)})
        self.assertEqual({(r["a"], r["t"]) for r in rows if "two_pass_sensitivity" in r["group"] and r["key"] == "tier:status"},
                         {("refused", "refused")})
        # Every rule above holds on both sides: no comparison of these fields is above the bar (check),
        # and the twin's values are the ones asserted on the analysis's side.
        self.assertTrue(all(r["status"] == "equal" for r in rows if r["key"] in ("status", "pass_label", "answer", "n")
                            or r["key"].startswith(("flag:", "withheld_"))))

    def test_time_world(self):
        self.check("time", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                "h2/rest/passes_mean": (11, 11)})

    def test_defects_campaign(self):
        R = self.check("defects", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                       "h2/rest/passes_mean": (11, 11)})
        # The five planted defects reach both sides: D5's cooldown restore and D10's without-assisted line.
        kept = {r["group"]: r for r in R.rows if r["key"] == "n_b" and r["stage"] == "heldout"}
        self.assertEqual(kept["cell/qwen3-8b-4bit/pass1/rails/gross"]["a"], 9)
        self.assertEqual(kept["cell/qwen3-8b-4bit/pass1/rails/flagged_inclusive"]["a"], 10)
        self.assertEqual(kept["cell/qwen3-14b-4bit/pass1/rails/flagged_inclusive"]["a"], 9)
        without = [r for r in R.rows if "/without_assisted" in r["group"] and r["key"] == "status"]
        self.assertTrue(without and all(r["a"] == r["t"] == "computed" for r in without))

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
