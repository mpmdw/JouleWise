"""BYTES agreement test (R8 item 4, Addendum 8): the analysis against the twin on the same campaigns.

Both implementations run as separate command-line processes (``scripts/bytes_analyze.py`` and
``scripts/bytes_twin.py``) on the same production-shaped synthetic campaigns from the lane's own
generator (``tests/fixtures/bytes/campaign.py``: ten full-size modules, 50 runs per model per pass,
corpus/start/midpoint/end references, a native 50 SPS meter stream, real random hidden offsets), at
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
C_j at the coefficient row's printed precision, and all coefficient interval endpoints at 1% of
the HC3 half-width; the per-point bound at the
energy bar (J) and the power bar (W); the sensitivities at the no-half-width bar; the zero/sign
decisions under both intervals as exact labels (registration §12); units, flag presence, scope and
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
import bisect
import copy
import importlib.util
import json
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tests.desk_restore_support import compress_member, ample_space_command
from joulewise.desk_restore import RestoreRefused
from joulewise import desk_restore
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
ANCHOR_DEFECTS = [(1, "Qwen3-1.7B-4bit", 0, "member.anchor_not_bounded")]
# Addendum 9 item 1: the generator's NR1 knobs (samples 10 ms into the interval, science-run edges
# at a uniform phase, a 10 ms minimum receive latency) are its defaults, so every campaign below is
# the ruled fixture in which a constant label offset flips a whole sample with probability
# delta / dt = 10 ms / 20 ms per run.  "resident" (seed 3100) is the world of the NR1 regression
# tests.test_bytes_analysis.ProductionArchiveTests.test_nr1_offset_term_covers_constant_label_offset.
NR1_KNOBS = {"sample_phase_ms": 10, "edge_phase": True, "min_receive_latency_ms": 10.0}
# Addendum 9.1's pre-ruling edge-locked meter, as closely as the generator's knobs allow: science-run
# edges on the sample grid (edge_phase False) and the sample 19 ms into its 20 ms interval, so the
# sample before each decode edge sits 1 ms before it and the 10 ms label offset carries it across
# (a baseline sample enters at the start, a decode sample leaves at the end): whole-sample flips on
# every run with certainty, Addendum 9.1's "with certainty, which no free-running meter clock can do".
# 19 ms keeps 1 ms of margin on each side of the offset against the
# fitted label offset's own error (about 0.01 ms, B2-NR1-RULING "fitted label offset 9.991 ms").
EDGE_LOCKED_KNOBS = {"sample_phase_ms": 19, "edge_phase": False, "min_receive_latency_ms": 10.0}
# B4 withholding campaign (R6's six sub-packs, one session per sub-pack and pass; B6 ruling Q1):
# the withheld store of s2 pass 2 (30B-A3B's held-out rows; 8B is a fit model) is missing, both
# stores of s6 (Qwen3.5-122B, an MoE model) are missing, and s4 pass 2 (32B, 8B-8bit) was never
# collected (R6's optional pass).
WITHHELD_KNOBS = {"subpack_sessions": True, "uncollected_sessions": ("bytes-s4-p2",)}
MISSING_STORES = ("bytes-s2-p2", "bytes-s6-p1", "bytes-s6-p2")
# name: (world, seed, planted defects, generator knobs, withheld stores removed after export).
CAMPAIGNS = {
    "bytes": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True, "battery_publication": "delayed", "battery_reference_assist": True}, ()),
    "resident": ("resident", 3100, [], NR1_KNOBS, ()),
    "time": ("time", 2100, [], NR1_KNOBS, ()),
    "defects": ("bytes", 1100, DEFECTS, NR1_KNOBS, ()),
    "minimum": ("bytes", 1100, DEFECTS_MINIMUM, NR1_KNOBS, ()),
    "edge_locked": ("resident", 3100, [], EDGE_LOCKED_KNOBS, ()),
    "withheld": ("bytes", 1100, [], {**NR1_KNOBS, **WITHHELD_KNOBS}, MISSING_STORES),
    "invalid_anchor": ("bytes", 1100, ANCHOR_DEFECTS, NR1_KNOBS, ()),
    "marker_incomplete": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                           "truncate_marker_window": True}, ()),
    "late_start": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                   "battery_publication": "delayed", "battery_reference_assist": True,
                   "late_start_stream": True}, ()),
    "polls_only": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                   "battery_publication": "delayed", "battery_reference_assist": True,
                   "marker_stream_mode": "polls_only"}, ()),
    "header_closed": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                      "battery_publication": "delayed", "battery_reference_assist": True,
                      "marker_stream_mode": "header_closed"}, ()),
    "empty_payload_n": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                        "battery_publication": "delayed", "battery_reference_assist": True,
                        "marker_stream_mode": "empty_payload_n"}, ()),
    "replayed_batch": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                       "battery_publication": "delayed", "battery_reference_assist": True,
                       "marker_stream_mode": "replayed_batch"}, ()),
    "replayed_tail": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                      "battery_publication": "delayed", "battery_reference_assist": True,
                      "marker_stream_mode": "replayed_tail"}, ()),
    "first_batch_tail_replayed": ("bytes", 1100, [], {**NR1_KNOBS, "battery_assist": True,
                                  "battery_publication": "delayed", "battery_reference_assist": True,
                                  "marker_stream_mode": "first_batch_tail_replayed"}, ()),
    "compressed": ("bytes", 1100, [], NR1_KNOBS, ()),
}
BMAP = {"rails": "rails", "DC input": "dc_input", "rest": "rest"}
VMAP = {("gross primary", "primary"): "gross", ("idle-subtracted secondary", "primary"): "idle_subtracted",
        ("gross primary", "flagged-inclusive"): "flagged_inclusive",
        ("idle-subtracted secondary", "flagged-inclusive"): "idle_flagged_inclusive"}
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
    """1% of the coefficient's HC3 half-width: registration section 12."""
    return 0.01 * half_width


def bar_h2_printed(half_width):
    """Section 14: estimates and errors use the decimal place of a two-significant-figure half-width."""
    rounded = float(f"{abs(half_width):.2g}")
    return 0.5 * 10 ** (math.floor(math.log10(rounded)) - 1) if rounded else 0.0


def bar_rest_intercept_floor(vif, inputs):
    """Doctrine's lower edge: 1e6 × binary64 noise × 4 VIF × RMS(P_rest).

    The centred two-regressor Gram condition number is approximately 4 VIF.
    The response RMS is the intercept's natural W scale. Registration §12 /
    Addendum 8.6 declares c unidentified and draws no word from it; where this
    floor exceeds 1% of a printed interval, that interval's 1% ceiling governs
    and the comparison record discloses the floor/ceiling crossing ratio.
    """
    response_rms = math.sqrt(math.fsum(p[0] ** 2 for p in inputs) / len(inputs))
    return 1e6 * sys.float_info.epsilon * 4 * vif * response_rms


def coefficient_bar_note(ceiling, floor):
    """Record an empty doctrine window beside the unchanged 1% ceiling."""
    if floor > ceiling:
        return f"float-noise lower edge / 1% ceiling = {floor / ceiling:.12g}; window empty, ceiling governs"
    return None


# Durations compare to 1 ms: Addendum 8.5 (the printed precision F13 asks B6 to fix; 1 ms is the
# precision Addendum 8.5 names, and it is 1e6 x float noise on a 60 s decode: 1.3e-8 s, by far).
DURATION_BAR_S = 1e-3


def bar_duration_derived(value, duration_s):
    """BW and R/tau print three decimals (section 14), without duration propagation."""
    return 0.0005


def bar_no_half_width(a, t, key=""):
    """Section 14 half-digit bars; None identifies an unprinted diagnostic."""
    if key in ("drift_scale", "time", "x_time", "intercept", "slope") or key.endswith((".intercept", ".slope")):
        return 0.0000005
    if key in ("BW", "R_over_tau", "bytes", "resident"):
        return 0.0005
    if key in ("critical",):
        return 0.00005
    if key.endswith("_j") or key.startswith("endpoint mean:"):
        return 0.0005
    if key.endswith("_s"):
        return DURATION_BAR_S
    if key.endswith("_w") or key.startswith(("edge_powers_w[", "adjacent_before_edge_powers_w[")):
        return 0.00005
    return None


# F3: unprinted sensitivities are diagnostics. Bounds in J use the cell's (h + B),
# and their printed power equivalents use the point's power half-width.
WITHHELD_MISSING = "bytes.withheld_missing"
UNPRINTED_DIAGNOSTICS = frozenset({"variance", "covariance", "ols_covariance", "mse",
    "d_beta_d_delta_per_ms", "meter_offset_sensitivity_w", "offset_sensitivity_w",
    "edge_powers_w", "adjacent_before_edge_powers_w", "idle_power_w", "meter_idle_power_w", "battery_idle_power_w"})


def printed_fields(value):
    if isinstance(value, dict):
        return {key: printed_fields(item) for key, item in value.items() if key not in UNPRINTED_DIAGNOSTICS}
    if isinstance(value, list):
        return [printed_fields(item) for item in value]
    return value


def states_delta_bound(text):
    """The numbers the disclosure states (Addendum 9 item 4: 22 to 25 ms at 50 SPS, block-6 M13):
    compared exactly; the wording is representation and is not compared."""
    import re
    numbers = {int(n) for n in re.findall(r"\b(\d+)\s*(?:to\s*\d+\s*)?ms\b", text or "")}
    numbers |= {int(n) for n in re.findall(r"\b\d+\s*to\s*(\d+)\s*ms\b", text or "")}
    return (22 in numbers, 25 in numbers, "M13" in (text or ""))


def reason_run_ids(text):
    """Reason wording is descriptive; the set of affected kept runs is exact."""
    return sorted(set(re.findall(r"\(run ([^)]+)\)", text or "")))


# ---------------------------------------------------------------------------------------------
# The recorder: every compared field is one record.

class Recorder:
    def __init__(self):
        self.rows = []
        self.diagnostics = []

    def diagnostic(self, stage, group, key, a, t):
        """F3: report unprinted differences without a tolerance or acceptance effect."""
        row = {"stage": stage, "group": group, "key": key, "a": a, "t": t,
               "different": a != t}
        self.diagnostics.append(row)
        return row

    def exact(self, stage, group, key, a, t, note=None):
        a, t = printed_fields(a), printed_fields(t)
        row = {"stage": stage, "group": group, "key": key, "a": a, "t": t, "bar": "exact",
               "status": "equal" if a == t else "above_bar"}
        if note:
            row["note"] = note
        self.rows.append(row)
        return row

    def number(self, stage, group, key, a, t, bar, note=None):
        """bar: an absolute tolerance, or None to look up the field's printed precision."""
        if a is None or t is None or isinstance(a, (bool, str, list, dict)) or isinstance(t, (bool, str, list, dict)):
            return self.exact(stage, group, key, a, t, note)
        if bar is None:
            bar = bar_no_half_width(a, t, key)
            if bar is None:
                return self.diagnostic(stage, group, key, a, t)
        diff = abs(a - t)
        status = "equal" if diff == 0 else "under_bar" if diff <= bar else "above_bar"
        row = {"stage": stage, "group": group, "key": key, "a": a, "t": t, "bar": bar, "abs": diff, "status": status}
        if note:
            row["note"] = note
        self.rows.append(row)
        return row


    def counts(self):
        out = {"compared": len(self.rows), "equal": 0, "under_bar": 0, "above_bar": 0}
        for row in self.rows:
            out[row["status"]] += 1
        out.update(diagnostic_compared=len(self.diagnostics),
                   diagnostic_different=sum(r["different"] for r in self.diagnostics))
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
    R.exact(stage, g, "drift_family", row.get("drift_family"), est.get("drift_family"))
    for key in ("mean_j", "h_j", "B_j", "lower_j", "upper_j"):
        R.number(stage, g, key, row.get(key), est.get(key), bar_energy(hb))
    for key in ("attribution_floor_j", "rails_attribution_floor_j", "meter_attribution_floor_j", "meter_phase_edge_mean_j"):
        R.number(stage, g, key, row.get(key), est.get(key), bar_energy(hb))
    R.diagnostic(stage, g, "variance", row.get("variance"), est.get("variance"))
    for key in ("df", "n_r", "n_b"):
        R.exact(stage, g, key, row.get(key), est.get(key))
    R.number(stage, g, "duration_s", row.get("duration_s"), est.get("duration_s"), DURATION_BAR_S)
    ak, tk = a_kinds(row), t_kinds(est)
    for kind in ("anchor", "interp", "drift", "meter_edge"):
        R.number(stage, g, "B_kind:" + kind, ak[kind], tk[kind], bar_energy(hb))
    if row["boundary"] != "rails":
        compare_battery_columns(R, stage, g, row, est, hb)
        # Addendum 9: the pass's coherent-offset bound (J, at the cell's energy bar) and signed
        # sensitivity (W, no half-width); rails has neither (checked in compare_cells).
        offset = est.get("meter_offset") or {}
        R.number(stage, g, "meter_offset_bound_j", row.get("meter_offset_bound_j"), offset.get("bound_j"), bar_energy(hb))
        R.diagnostic(stage, g, "meter_offset_sensitivity_w", row.get("meter_offset_sensitivity_w"), offset.get("sensitivity_w"))


def compare_battery_columns(R, stage, g, row, est, half):
    """BAT-2: diagnostic energies use the same cell half-width; counts and boundary words are exact."""
    for key in ("battery_term_mean_j", "battery_term_max_j", "battery_phase_edge_max_j"):
        R.number(stage, g, key, row.get(key), est.get(key), bar_energy(half))
    for key in ("battery_nonzero_run_count", "boundary_description"):
        R.exact(stage, g, key, row.get(key), est.get(key))
    # Run terms use their enclosing cell's energy bar. Missing polls remove DC/rest only.
    tm = {r["run_id"]: r for r in est.get("meter_run_terms", [])}
    R.exact(stage, g, "meter run census", sorted(r["run_id"] for r in row.get("meter_run_terms", [])),
            sorted(r["run_id"] for r in est.get("meter_run_terms", [])))
    for run in row.get("meter_run_terms", []):
        other = tm.get(run["run_id"], {})
        rg = g + "/meter/" + run["run_id"]
        for key in ("meter_gross_j", "meter_secondary_j", "battery_gross_j", "battery_secondary_j",
                    "battery_v_start_j", "battery_v_end_j", "battery_phase_edge_j", "offset_bound_j",
                    "gross_j", "secondary_j", "phase_edge_j", "meter_phase_edge_j"):
            R.number(stage, rg, key, run.get(key), other.get(key), bar_energy(half))
        for key in ("battery_tau_s", "battery_poll_interval_max_s", "sample_interval_s", "r_max_s"):
            # Durations use the registered 1 ms bar, without propagation.
            R.number(stage, rg, key, run.get(key), other.get(key), None)
        for key in ("battery_idle_power_w", "meter_idle_power_w", "idle_power_w", "offset_sensitivity_w"):
            R.diagnostic(stage, rg, key, run.get(key), other.get(key))
        for key in ("edge_powers_w", "adjacent_before_edge_powers_w"):
            for i, value in enumerate(run.get(key, [])):
                R.diagnostic(stage, rg, key + f"[{i}]", value, (other.get(key) or [None, None])[i])
        for key in ("battery_n", "battery_n_idle", "n", "n_idle", "decode_battery_assist"):
            R.exact(stage, rg, key, run.get(key), other.get(key))
        R.exact(stage, rg, "battery_end_window_complete", run.get("battery_end_window_complete"),
                other.get("battery_end_window_complete"))


def compare_missing(R, stage, g, row, est):
    """B6 ruling Q1: a `missing` pass or point: the flag, the sidecar's withheld row counts, exactly."""
    R.exact(stage, g, "flag:" + WITHHELD_MISSING, WITHHELD_MISSING in (row.get("flags") or []),
            WITHHELD_MISSING in (est.get("flags") or []))
    for key in ("withheld_row_count", "withheld_config_row_count"):
        if key in row or key in est:
            R.exact(stage, g, key, row.get(key), est.get(key))


def row_key(row, *, point=False):
    return (canon(row["model"]), "mean" if point else str(row["pass_id"]),
            row["boundary"], row["basis"], row["selection"])


def compare_census(R, stage, rows, t, *, point=False, table=None):
    """Compare identities both ways, including unavailable rows and duplicate rows."""
    if table is not None:
        primary = [r for r in rows if (r["basis"], r["selection"]) == ("gross primary", "primary")]
        expected = []
        # Before withheld rows are admitted, the blinded primary has fit points
        # only and emits no hypothesis tables (bytes_analyze's evaluation gate).
        tables = t.get("h2" if table == "h2" else "h1", {}) if any(
            model not in bt.FIT_SET for model in t.get("cells", {})) else {}
        for boundary, passes in tables.items():
            if stage.startswith("blinded") and boundary != "rails":
                continue
            if table == "moe":
                if "passes_mean" in passes:
                    expected.append((boundary,))
            elif table == "h1":
                for pk, block in passes.items():
                    models = block.get("models", {})
                    for model, cells in t.get("cells", {}).items():
                        if model in bt.FIT_SET:
                            continue
                        quantity = cells.get(pk, {}).get("boundaries", {}).get(boundary, {}).get("quantities", {}).get("gross", {})
                        if block.get("status") == "refused_fit_set_incomplete":
                            present = pk == "passes_mean" and quantity.get("status") != "ok"
                        else:
                            member = models.get(model)
                            present = member is not None and (pk == "passes_mean" or
                                ("refused" not in member and member.get("status") != "missing"))
                        if present:
                            expected.append((model, boundary, "mean" if pk == "passes_mean" else pk[4:]))
            elif "passes_mean" in passes:
                expected.append((boundary, "primary"))
                quantities = [cells.get("passes_mean", {}).get("boundaries", {}).get(boundary, {}).get("quantities", {}).get("gross", {})
                              for cells in t.get("cells", {}).values()]
                if "two_pass_sensitivity" in passes["passes_mean"] or any(
                    q.get("status") != "ok" or q.get("passes_computed", 1) < 2 for q in quantities):
                    expected.append((boundary, "two_pass_sensitivity"))
        if table == "h1":
            actual = [(canon(r["model"]), BMAP.get(r["boundary"], r["boundary"]), str(r["pass_id"]))
                      for r in primary if r["role"] == "heldout"]
        elif table == "h2":
            actual = [(BMAP.get(r["boundary"], r["boundary"]), r["analysis"]) for r in primary]
        else:
            actual = [(BMAP.get(r["boundary"], r["boundary"]),) for r in primary]
        R.exact(stage, table + " census", "row keys", sorted(actual), sorted(expected))
        return
    expected = []
    reverse_b = {v: k for k, v in BMAP.items()}
    for model, passes in (t.get("cells") or {}).items():
        for pk, block in passes.items():
            if (pk == "passes_mean") != point:
                continue
            for boundary, cell in block.get("boundaries", {}).items():
                if stage.startswith("blinded") and boundary != "rails":
                    # Registration Addendum 3.4: no DC/rest table exists at
                    # this stage, including missing-withheld placeholders.
                    continue
                # At blinded stages the twin explicitly prints no_archive_join;
                # primary has rails only, also for the model's pass mean.
                if cell.get("status") == "no_archive_join" or (point and all(
                    p.get("boundaries", {}).get(boundary, {}).get("status") == "no_archive_join"
                    for key, p in passes.items() if key != "passes_mean")):
                    continue
                for basis, selection in VMAP:
                    expected.append((model, "mean" if point else pk[4:], reverse_b[boundary], basis, selection))
    R.exact(stage, "point census" if point else "cell census", "row keys",
            sorted(row_key(r, point=point) for r in rows), sorted(expected))


def compare_cells(R, stage, a_rows, t):
    compare_census(R, stage, a_rows, t)
    for row in a_rows:
        variant = VMAP.get((row["basis"], row["selection"]))
        if variant is None or row["boundary"] not in BMAP:
            R.exact(stage, "cell census", "known labels", row_key(row), "registered labels required")
            continue
        model, b = canon(row["model"]), BMAP[row["boundary"]]
        g = f"cell/{model}/pass{row['pass_id']}/{b}/{variant}"
        cell = (((t.get("cells") or {}).get(model) or {}).get(f"pass{row['pass_id']}") or {}).get("boundaries", {}).get(b)
        if cell is None:
            R.exact(stage, g, "status", row["status"], "absent")
            continue
        est = cell.get(variant) if cell.get("status", "ok") == "ok" else cell
        est = est if est is not None else {"status": cell.get("status", "absent")}
        R.exact(stage, g, "flags", row.get("flags", []), est.get("flags", []))
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
        for key in ("decode_assisted_member_counts", "harvest_assisted_member_counts"):
            R.exact(stage, g, key, row.get(key), est.get(key))
        R.exact(stage, g, "decode_assisted_member_counts_reason:run_ids",
                reason_run_ids(row.get("decode_assisted_member_counts_reason")),
                reason_run_ids(est.get("decode_assisted_member_counts_reason")))
        R.exact(stage, g, "kept_runs", sorted(row.get("kept_runs", [])), t_kept(est))
        if "assisted_unit_counts" in row:
            assists = set(cell.get("assist_members", []))
            members = est.get("members", {})
            R.exact(stage, g, "assisted_unit_counts", row["assisted_unit_counts"], {
                "repeat": sum(r in assists for r in members.get("repeats", [])),
                "quad": sum(bool(set(q) & assists) for q in members.get("quads", {}).values())})
        if variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive"):
            da = cell.get("drift_allowance") or {}
            R.number(stage, g, "drift_scale", row.get("drift_scale"), est.get("drift_scale", da.get("scale")), 0.0000005)
            hb = row["h_j"] + row["B_j"]
            if b == "rails":
                R.number(stage, g, "attribution_floor_j", row.get("rails_attribution_floor_j"),
                         (cell.get("attribution_floor") or {}).get("value_j"), bar_energy(hb))
            else:
                R.number(stage, g, "meter_attribution_floor_j", row.get("meter_attribution_floor_j"),
                         (cell.get("meter_attribution_floor") or {}).get("value_j"), bar_energy(hb))
            # Addendum 7 D10: block 5's without-assisted line wherever a cell holds an assist member.
            wa, wt = row.get("without_assisted"), est.get("without_assisted")
            if wa is not None or wt is not None:
                gw = g + "/without_assisted"
                a_ok = wa is not None and wa.get("status") == "computed"
                t_ok = wt is not None and wt.get("status") == "ok"
                R.exact(stage, gw, "status", "computed" if a_ok else "unavailable", "computed" if t_ok else "unavailable")
                if wa is not None and wt is not None:
                    R.exact(stage, gw, "description_only", wa.get("description_only"), True)
                    R.exact(stage, gw, "below_minimum", wa.get("below_minimum"), wt.get("below_minimum"))
                    if wa.get("status") == "not_evaluated" or wt.get("status") == "not_evaluated":
                        R.exact(stage, gw, "evaluation status", wa.get("status"), wt.get("status"))
                        R.exact(stage, gw, "reason:run_ids", reason_run_ids(wa.get("reason")),
                                reason_run_ids(wt.get("reason")))
                        for key in ("mean_j", "h_j", "B_j", "lower_j", "upper_j", "n_r", "n_b"):
                            R.exact(stage, gw, key + ":not evaluated is null", wa.get(key), None)
                if a_ok and t_ok:
                    compare_cell_numbers(R, stage, gw, {**wa, "boundary": row["boundary"]}, wt)
                    R.number(stage, gw, "drift_scale", wa.get("drift_scale"), wt.get("drift_scale"), 0.0000005)
                    R.exact(stage, gw, "drift_family", wa.get("drift_family"), wt.get("drift_family"))
                    R.exact(stage, gw, "flags", wa.get("flags", []), wt.get("flags", []))
                    R.exact(stage, gw, "kept_runs", sorted(wa.get("kept_runs", [])), t_kept(wt))


def reference_reason_code(reason):
    """Compare registered words; the bound analysis retains meter diagnostic prose.

    Only meter-unavailable diagnostics lack a printed code: clock/mapping,
    span coverage, absent samples/battery readings, and absent meter requests.
    Their registered disclosure is bytes.meter_decode_unavailable, except a
    dropped device sample, whose disclosure is bytes.meter_gap. Do not fold
    status/exclusion words or unknown text into a generic unavailable value.
    """
    if reason == "dropped device sample in meter span":
        return "bytes.meter_gap"
    if reason in ("meter does not cover decode and own idle spans", "meter span has no samples",
                  "battery reading missing", "meter request unavailable",
                  "meter clock fit or raw/monotonic mapping unavailable") or (
            isinstance(reason, str) and reason.startswith(
                "meter clock fit or raw/monotonic mapping unavailable: ")):
        return "bytes.meter_decode_unavailable"
    return reason


def compare_neg8(R, stage, a_rows, t):
    def drops(record):
        value = record.get("dropped_references")
        return sorted(({**r, "reason": reference_reason_code(r["reason"])} for r in value),
                      key=lambda r: r["run_id"]) if isinstance(value, list) else value

    seen = set()
    for row in a_rows:
        sid = row["session_id"]
        if sid in seen or "neg8_inputs" not in row:
            continue
        seen.add(sid)
        tn = ((t.get("sessions") or {}).get(sid) or {}).get("neg8") or {}
        rails = tn.get("rails/gross") or {}
        R.exact(stage, f"neg8/{sid}/rails", "dropped reference census and reasons",
                drops(row["neg8_inputs"]), drops(rails))
        R.exact(stage, f"neg8/{sid}/rails", "dropped reference count",
                row["neg8_inputs"].get("dropped_reference_count", 0), rails.get("dropped_reference_count", 0))
        # Registration section 6 requires both readers to print each dropped
        # reference's identity and reason, including unavailable DC/rest joins.
        for b in (("rails",) if stage.startswith("blinded") else BMAP):
            boundary = row["neg8_inputs"].get("boundary_reference_drops", {}).get(b, {})
            for family in ("gross", "idle"):
                target = tn.get(f"{BMAP[b]}/{family}") or {}
                g = f"neg8/{sid}/{BMAP[b]}/{family}"
                R.exact(stage, g, "boundary dropped reference census and reasons", drops(boundary), drops(target))
                R.exact(stage, g, "boundary dropped reference count",
                        boundary.get("dropped_reference_count"), target.get("dropped_reference_count"))
        references = row["neg8_inputs"].get("references", [])
        reference_ids = {ref["run_id"] for ref in references}
        target_drops = (tn.get("dc_input/gross") or {}).get("dropped_references", [])
        R.exact(stage, f"neg8/{sid}", "reference meter unavailable reasons",
                {ref["run_id"]: reference_reason_code(ref["meter_unavailable_reason"]) for ref in references
                 if "meter_unavailable_reason" in ref},
                {ref["run_id"]: reference_reason_code(ref["reason"]) for ref in target_drops
                 if ref["run_id"] in reference_ids})
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
                for key in ("n_start", "n_end"):
                    R.exact(stage, gf, key, fa["bound_terms"].get(key), (tf.get("bound_terms") or {}).get(key))
                for role, value in fa.get("means_j", {}).items():
                    R.number(stage, gf, "endpoint mean:" + role, value, tf.get("endpoint_means_j", {}).get(role), None)
                source = [r for r in row["neg8_inputs"].get("references", []) if b in r]
                target = {r["run_id"]: r for r in tf.get("reference_values", [])}
                R.exact(stage, gf, "source reference census", sorted(r["run_id"] for r in source), sorted(target))
                for ref_row in source:
                    other = target.get(ref_row["run_id"], {})
                    gr = gf + "/" + ref_row["run_id"]
                    R.exact(stage, gr, "role", ref_row["role"], other.get("role"))
                    R.number(stage, gr, "duration_s", ref_row["duration_s"], other.get("duration_s"), DURATION_BAR_S)
                    R.number(stage, gr, "energy_j", ref_row[b].get(family), other.get("energy_j"), None)
            tg = tn.get(f"{BMAP[b]}/gross") or {}
            R.number(stage, g, "E_ref_j", ref["energy_j"], tg.get("E_ref_j"), None)
            R.number(stage, g, "T_ref_s", ref["duration_s"], tg.get("T_ref_s"), DURATION_BAR_S)
            R.exact(stage, g, "reference_run_ids", sorted(ref["reference_run_ids"]), sorted(tg.get("reference_run_ids", [])))
            R.exact(stage, g, "corpus_run_ids", sorted(ref["corpus_run_ids"]), sorted(tg.get("corpus_run_ids", [])))


def compare_points(R, stage, a_points, t):
    compare_census(R, stage, a_points, t, point=True)
    for p in a_points:
        variant = VMAP.get((p["basis"], p["selection"]))
        if variant is None or p["boundary"] not in BMAP:
            R.exact(stage, "point census", "known labels", row_key(p, point=True), "registered labels required")
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
        for key in ("attribution_floor_j", "meter_attribution_floor_j", "meter_phase_edge_mean_j"):
            R.number(stage, g, key, p.get(key), q.get(key), bar_energy(hb))
        if b != "rails":
            compare_battery_columns(R, stage, g, p, q, hb)
            # Addendum 9 (cold disposition M1): the point's bound in J (pass-averaged, the energy bar),
            # in W (over the point's mean decode time, the power bar), and the sensitivity in W.
            R.number(stage, g, "meter_offset_bound_j", p.get("meter_offset_bound_j"), q.get("meter_offset_bound_j"), bar_energy(hb))
            R.number(stage, g, "meter_offset_bound_w", p.get("meter_offset_bound_w"), q.get("meter_offset_bound_w"),
                     bar_power(p["power_half_w"]))
            R.diagnostic(stage, g, "meter_offset_sensitivity_w", p.get("meter_offset_sensitivity_w"),
                         q.get("meter_offset_sensitivity_w"))
        else:
            R.exact(stage, g, "no meter offset terms on rails (Addendum 9)", p.get("meter_offset_bound_w") is None,
                    q.get("meter_offset_bound_w") is None)
        R.number(stage, g, "mean_j", p["mean_j"], q["E_dec_j"], bar_energy(hb))
        R.exact(stage, g, "output_label", p.get("output_label"), q.get("printed_label"))
        R.number(stage, g, "duration_s", p["duration_s"], q["T_dec_s"], DURATION_BAR_S)
        for ak, tk in (("e", "e_j_per_step"), ("lower", "e_lower_j_per_step"), ("upper", "e_upper_j_per_step"),
                       ("printed_j_per_output_token", "e_printed_j_per_token")):
            R.number(stage, g, ak, p.get(ak), q.get(tk), bar_energy(hb) / bt.DECODE_STEPS)
        R.number(stage, g, "time", p["time"], q["tau_s_per_step"], 0.0000005)
        R.number(stage, g, "power", p["power"], q["P_mean_w"], bar_power(p["power_half_w"]))
        R.number(stage, g, "power_half_w", p["power_half_w"], q["P_half_width_w"], bar_power(p["power_half_w"]))
        R.number(stage, g, "BW", p["BW"], q["BW_GB_per_s"], bar_duration_derived(p["BW"], T))
        R.number(stage, g, "bytes", p["bytes"], q["b_GB_per_step"], 0.0005)
        R.number(stage, g, "resident", p["resident"], q["R_GB"], 0.0005)
        R.number(stage, g, "R_over_tau", p["resident"] / p["time"], q["R_over_tau_GB_per_s"],
                 bar_duration_derived(p["resident"] / p["time"], T))
        R.number(stage, g, "half_width_j(h+B)", hb, (q["E_dec_upper_j"] - q["E_dec_lower_j"]) / 2, bar_energy(hb))
        for i, (va, vt) in enumerate(zip(p.get("pass_values_j", []), q.get("pass_values_E_dec_j", []))):
            R.number(stage, g, f"pass_values_j[{i}]", va, vt, bar_energy(hb))
        R.number(stage, g, "pass_difference_j", p.get("pass_difference_j"), q.get("pass_difference_E_dec_j"), bar_energy(hb))
        if "without_assisted" in p:
            wa, wt = p["without_assisted"], q.get("without_assisted", {})
            if wa.get("status") == "not_evaluated" or wt.get("status") == "not_evaluated":
                R.exact(stage, g + "/without_assisted", "evaluation status", wa.get("status"), wt.get("status"))
                R.exact(stage, g + "/without_assisted", "reason", wa.get("reason"), wt.get("reason"))
            R.exact(stage, g + "/without_assisted", "below_minimum", wa.get("below_minimum", False), wt.get("below_minimum", False))
            R.exact(stage, g + "/without_assisted", "evaluated", wa.get("mean_j") is not None, wt.get("status") == "ok")
            if wa.get("mean_j") is not None and wt.get("status") == "ok":
                # This descriptive line has its own (h+B) half-width, exactly as the primary.
                half = wa["h_j"] + wa["B_j"]
                for ak, tk in (("mean_j", "E_dec_j"), ("h_j", "h_j"), ("B_j", "B_j"),
                               ("lower_j", "E_dec_lower_j"), ("upper_j", "E_dec_upper_j")):
                    R.number(stage, g + "/without_assisted", ak, wa.get(ak), wt.get(tk), bar_energy(half))
                R.number(stage, g + "/without_assisted", "printed_j_per_output_token",
                         wa.get("printed_j_per_output_token"), wt.get("e_printed_j_per_token"), bar_energy(half) / 512)


def compare_h1(R, stage, a_h1, a_moe, t, a_frozen):
    compare_census(R, stage, a_h1, t, table="h1")
    compare_census(R, stage, a_moe, t, table="moe")
    for row in a_h1:
        if (row["basis"], row["selection"]) != ("gross primary", "primary"):
            continue
        pk = "passes_mean" if row["pass_id"] == "mean" else f"pass{row['pass_id']}"
        b, model = BMAP[row["boundary"]], canon(row["model"])
        g = f"h1/{b}/{pk}/{model}"
        th = (t.get("h1") or {}).get(b, {}).get(pk) or {}
        tm = (th.get("models") or {}).get(model)
        if tm is None:
            if th.get("status") == "refused_fit_set_incomplete" and row.get("status") == "missing":
                # Same unavailable boundary: primary emits null words per model;
                # twin emits the parent fit-set refusal, with no model words.
                R.exact(stage, g, "word", row.get("word"), None)
                R.exact(stage, g, "fit unavailable", row["status"], "missing")
                continue
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
            if c["hypothesis"] not in tm["checks"]:
                R.exact(stage, g, "known hypothesis", c["hypothesis"], sorted(tm["checks"]))
                continue
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
            # Section 14 prints the log ratio to four decimals; no propagated energy bar.
            R.number(stage, g, h + ":ln_ratio", c["log_ratio"], tc["ln_measured_over_predicted"], 0.00005)
            R.exact(stage, g, h + ":log_status", c.get("log_status"),
                    "computed" if tc["ln_measured_over_predicted"] is not None else "undefined_nonpositive")
    for row in a_moe:
        if (row["basis"], row["selection"]) != ("gross primary", "primary"):
            continue
        b = BMAP[row["boundary"]]
        group = (t.get("h1") or {}).get(b, {}).get("passes_mean") or {}
        tm = group.get("active_or_resident") or {}
        if group.get("status") == "refused_fit_set_incomplete":
            # No MoE answer can be drawn from an unavailable fit set. Recover
            # the missing-point census from the twin's explicit model statuses.
            missing = sorted(m for m, block in t.get("cells", {}).items() if
                block.get("passes_mean", {}).get("boundaries", {}).get(b, {}).get("quantities", {}).get("gross", {}).get("status") != "ok")
            tm = {"answer": "missing", "missing_models": missing}
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
            R.number(stage, g, "intercept", item["line"][0], tl[hyp]["central"]["a"], 0.0000005)
            R.number(stage, g, "slope", item["line"][1], tl[hyp]["central"]["s"], 0.0000005)
            ac = sorted(item["corners"], key=lambda c: c[1])
            tc = sorted(([c["a"], c["s"]] for c in tl[hyp]["corners"]), key=lambda c: c[1])
            for i, (x, y) in enumerate(zip(ac, tc)):
                R.number(stage, g, f"corner[{i}].intercept", x[0], y[0], 0.0000005)
                R.number(stage, g, f"corner[{i}].slope", x[1], y[1], 0.0000005)


def _interval(R, stage, g, name, a_fit, idx, t_iv, *, offset=False, floor=0.0):
    """Coefficient estimates and interval endpoints use 1% of the HC3 half-width.
    Standard errors use section 14's printed decimal place. No VIF multiplier.
    """
    half = (a_fit["intervals"][idx][1] - a_fit["intervals"][idx][0]) / 2
    bar = bar_coefficient(half)
    note = coefficient_bar_note(bar, floor)
    R.number(stage, g, name + ":estimate", a_fit["coefficients"][idx], t_iv["value"], bar, note)
    R.number(stage, g, name + ":lower[HC3]", a_fit["intervals"][idx][0], t_iv["lower"], bar, note)
    R.number(stage, g, name + ":upper[HC3]", a_fit["intervals"][idx][1], t_iv["upper"], bar, note)
    t_ols = t_iv.get("ols") or {}
    bar_ols = bar
    note_ols = coefficient_bar_note(bar_ols, floor)
    R.number(stage, g, name + ":lower[OLS label]", a_fit["ols_intervals"][idx][0], t_ols.get("lower"), bar_ols, note_ols)
    R.number(stage, g, name + ":upper[OLS label]", a_fit["ols_intervals"][idx][1], t_ols.get("upper"), bar_ols, note_ols)
    # Errors are printed at the row's registered decimal place, not at a propagated bar.
    printed_bar = bar_h2_printed(half)
    R.number(stage, g, name + ":SE[HC3]", a_fit["standard_errors"][idx], t_iv["half_width"] / a_fit["critical"], printed_bar, note)
    R.number(stage, g, name + ":SE[OLS]", a_fit["ols_standard_errors"][idx], t_ols["half_width"] / a_fit["critical"], printed_bar, note_ols)
    if offset:
        _offset_alternative(R, stage, g, name, a_fit, idx, t_iv, floor=floor)
    elif "coefficient_C" in a_fit or "offset" in t_iv:
        R.exact(stage, g, name + ":no offset alternative on rails (Addendum 9)", "coefficient_C" in a_fit, "offset" in t_iv)


def _offset_alternative(R, stage, g, name, a_fit, idx, t_iv, *, floor=0.0):
    """The offset alternative uses the coefficient's HC3 bar for interval endpoints.
    C_j uses the row's printed decimal place. Unprinted derivatives are diagnostics.
    Units and zero/sign decisions compare exactly.
    """
    o = t_iv.get("offset") or {}
    a_flag, t_flag = a_fit.get("systematics_flag"), o.get("systematics_flag")
    R.exact(stage, g, name + ":systematics_flag", a_flag is not None, t_flag is not None,
            None if (a_flag is None) == (t_flag is None) else f"analysis: {a_flag}; twin: {t_flag}")
    a_sflag, t_sflag = a_fit.get("sensitivity_flag"), o.get("sensitivity_flag")
    R.exact(stage, g, name + ":sensitivity_flag", a_sflag is not None, t_sflag is not None,
            None if (a_sflag is None) == (t_sflag is None) else f"analysis: {a_sflag}; twin: {t_sflag}")
    R.exact(stage, g, name + ":sensitivity_units", (a_fit.get("sensitivity_units") or [None] * (idx + 1))[idx],
            o.get("sensitivity_units"))
    R.exact(stage, g, name + ":coefficient_decision", a_fit["coefficient_decisions"][idx], o.get("coefficient_decision"))
    if a_flag is None and t_flag is None:
        half = (a_fit["intervals"][idx][1] - a_fit["intervals"][idx][0]) / 2
        lo, hi = a_fit["offset_intervals"][idx]
        bar_off = bar_coefficient(half)
        note = coefficient_bar_note(bar_off, floor)
        R.number(stage, g, name + ":coefficient_C", a_fit["coefficient_C"][idx], o.get("coefficient_C"), bar_h2_printed(half), note)
        R.number(stage, g, name + ":offset_lower", lo, o.get("offset_lower"), bar_off, note)
        R.number(stage, g, name + ":offset_upper", hi, o.get("offset_upper"), bar_off, note)
        lo_ols, hi_ols = a_fit["offset_ols_intervals"][idx]
        bar_ols = bar_off
        note_ols = coefficient_bar_note(bar_ols, floor)
        R.number(stage, g, name + ":offset_ols_lower", lo_ols, o.get("offset_ols_lower"), bar_ols, note_ols)
        R.number(stage, g, name + ":offset_ols_upper", hi_ols, o.get("offset_ols_upper"), bar_ols, note_ols)
        R.exact(stage, g, name + ":offset_decision", a_fit["offset_decisions"][idx], o.get("offset_decision"))
    if a_sflag is None and t_sflag is None:
        R.diagnostic(stage, g, name + ":d_beta_d_delta_per_ms", a_fit["d_beta_d_delta_per_ms"][idx], o.get("d_beta_d_delta_per_ms"))


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
        R.exact(stage, g + "/primary", term + ":coefficient_decision", item["coefficient_decision"], o.get("coefficient_decision") if offset else t_iv.get("decision"))
        if offset and item.get("offset_intervals") and o.get("coefficient_C") is not None:
            lo, hi = item["offset_intervals"]
            R.exact(stage, g + "/primary", term + ":offset_decision", item["offset_decision"], o.get("offset_decision"))
            R.number(stage, g + "/primary", term + ":coefficient_C", item["coefficient_C"], o.get("coefficient_C"), bar_h2_printed(half))


def compare_h2_fit(R, stage, g, row, th, own_half, b, rest_inputs=None):
    """One H2 fit group (primary, or the two-pass sensitivity line).  rest_inputs: {model: (P_rest,
    BW, P_rails)} of the analysis's points, for the rest model's coefficient scales."""
    R.exact(stage, g, "n", row["n"], th.get("n"))
    compare_offset_rows(R, stage, g, row, th)
    for ak, tk in (("two_term", "simple"), ("resident_extended", "resident_extended"), ("tier", "tier"), ("rest", "rest_model")):
        af, tf = row.get(ak) or {}, (th.get(tk) or {}).get("details") or {}
        if af.get("status") != "computed" or not tf:
            continue
        for key in ("n", "p", "df", "se_method", "family_size"):
            R.exact(stage, g + "/" + ak, key, af.get(key), tf.get(key))
        R.number(stage, g + "/" + ak, "critical", af.get("critical"), tf.get("critical"), None)
        R.diagnostic(stage, g + "/" + ak, "mse", af.get("mse"), tf.get("mse"))
        R.exact(stage, g + "/" + ak, "point_models", sorted(canon(p["model"]) for p in af["point_labels"]), sorted(tf["models"]))
        for key in ("covariance", "ols_covariance"):
            for i, values in enumerate(af[key]):
                for j, value in enumerate(values):
                    R.diagnostic(stage, g + "/" + ak, f"{key}[{i},{j}]", value, tf[key][i][j])
    if row["two_term"]["status"] != "computed" or th.get("status") != "ok":
        status = th.get("status")
        R.exact(stage, g, "status", row["two_term"]["status"], "refused" if str(status).startswith("refused_") else status)
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
        R.exact(stage, g, "resident_adds_nothing", row["resident_adds_nothing"], ext_t["resident_adds_nothing"])
        if offset and ext_a.get("systematics_flag") is None and "resident_adds_nothing_offset" in row:
            # Registration §12 requires exact words under the offset alternative too.
            R.exact(stage, g, "resident_adds_nothing_offset", row["resident_adds_nothing_offset"], ext_t.get("resident_adds_nothing_offset"))
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
            R.exact(stage, gd, "sign", "+" if dev["deviation_w"] > 0 else "-" if dev["deviation_w"] < 0 else "0", td["sign"])
    if b == "rest":
        rm, tr = row["rest"], th.get("rest_model")
        R.exact(stage, g, "rest:status", rm["status"], "computed" if tr else "refused")
        if rm["status"] == "computed" and tr:
            vif_a, vif_t = rm.get("vif"), tr.get("vif_BW_and_P_rails")
            fitted = [rest_inputs[canon(p["model"])] for p in rm["point_labels"]
                      if canon(p["model"]) in (rest_inputs or {})]
            R.exact(stage, g, "rest:c scale inputs present", len(fitted), len(rm["point_labels"]))
            floor = bar_rest_intercept_floor(vif_a, fitted) if fitted and vif_a is not None else 0.0
            _interval(R, stage, g, "rest:c", rm, 0, _p0(tr, "c", rm, 0), offset=True, floor=floor)
            _interval(R, stage, g, "rest:epsilon_rest", rm, 1, tr["epsilon_rest_j_per_GB"], offset=True)
            _interval(R, stage, g, "rest:lambda", rm, 2, tr["lambda"], offset=True)
            R.exact(stage, g, "rest:vif", None if vif_a is None else f"{vif_a:.2g}",
                    None if vif_t is None else f"{vif_t:.2g}")
            R.exact(stage, g, "rest:vif_status", rm.get("vif_status"), "computed" if vif_t is not None else "infinite")
            # Registration §14 prints r to 9 decimals: half a last digit, 5e-10,
            # above 1e6 * 2.2e-16 = 2.2e-10 roundoff on this dimensionless quantity.
            R.number(stage, g, "rest:correlation_r", rm.get("correlation"), tr.get("correlation_r"), 5e-10)
    for item in row["loo_description"]:
        m = canon(item["model"])
        tl = (th.get("leave_one_out") or {}).get(m) or {}
        R.exact(stage, g + "/loo", m + ":status", item["status"], "computed" if tl else "refused")
        if item["status"] == "computed" and tl:
            half = own_half.get(m)
            R.exact(stage, g + "/loo", m + ":own half-width present", half is not None, True)
            if half is not None:
                R.number(stage, g + "/loo", m, item["predicted_w"], tl.get("predicted_w"), bar_power(half))


def _p0(t_fit, key, a_fit, idx):
    """P0 and c are printed and not counted (Addendum 3 item 6); the twin now prints their intervals
    too (Addendum 9: every coefficient, intercepts included, carries the alternative), so they compare
    like every other coefficient."""
    return t_fit[key]


def compare_h2(R, stage, a_h2, t, a_points):
    compare_census(R, stage, a_h2, t, table="h2")
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
            if ts is None:
                eligible = [m for m, block in t.get("cells", {}).items() if
                    (block.get("passes_mean", {}).get("boundaries", {}).get(b, {}).get("quantities", {}).get("gross") or {}).get("passes_computed", 0) >= 2]
                if not eligible and row.get("n") == 0:
                    # Primary prints an empty, refused sensitivity; twin has no
                    # line when there are no two-pass points (Addendum 7 D9).
                    R.exact(stage, g, "n", row["n"], len(eligible))
                    R.exact(stage, g, "status", row["two_term"]["status"], "refused")
                    continue
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
        if p["boundary"] not in BMAP:
            R.exact(stage, "commit/fit_point", "known boundary", p["boundary"], sorted(BMAP))
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
        R.number(stage, g, "x_bytes", p["bytes"], tp["x"]["bytes"], 0.0005)
        R.number(stage, g, "x_resident", p["resident"], tp["x"]["resident"], 0.0005)
        R.number(stage, g, "x_time", p["time"], tp["x"]["time"], 0.0000005)
    for p in (a_frozen or {}).get("tier_fit_inputs", []):
        if (p["basis"], p["selection"]) != ("gross primary", "primary"):
            continue
        if p["boundary"] not in BMAP:
            R.exact(stage, "commit/tier_input", "known boundary", p["boundary"], sorted(BMAP))
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


def compare_primary_copies(R, stage, rows, points, *, frozen=None, h2_rows=(), h1_rows=(), moe_rows=(), unavailable=()):
    """Bit identity is required only for copies within the primary's artifacts.

    Independent arithmetic still uses the registered bars. These assertions make
    the exemptions for pass copies, aliases, and repeated fit disclosures real.
    """
    source = {row_key(r): r for r in rows}
    point_source = {row_key(p, point=True): p for p in points}
    references = {}
    for row in rows:
        g = "primary copies/" + repr(row_key(row))
        owner = point_source.get(row_key(row, point=True), {})
        for key in ("n_passes", "pass_status"):
            if key in row:
                R.exact(stage, g, "pass label copy:" + key, row[key], owner.get(key))
        if "assisted_member_counts" in row:
            R.exact(stage, g, "assisted member alias", row["assisted_member_counts"], row.get("decode_assisted_member_counts"))
        ref = row.get("neg8_inputs")
        if ref is not None:
            sid = row["session_id"]
            references.setdefault(sid, ref)
            R.exact(stage, g, "NEG-8 session copy", ref, references[sid])
    for point in points:
        g = "primary copies/" + repr(row_key(point, point=True))
        for item in point.get("passes", []):
            for key in ("model", "boundary", "basis", "selection", "bytes", "resident", "role", "moe", "tier"):
                R.exact(stage, g, "point input copy:" + key, point.get(key), item.get(key))
        for item in point.get("passes", []):
            original = source.get(row_key({**point, "pass_id": item["pass_id"]}))
            expected = None if original is None else {**original, "pass_status": point["pass_status"], "n_passes": point["n_passes"]}
            R.exact(stage, g, "pass copy:" + str(item["pass_id"]), item, expected)
        wa = point.get("without_assisted", {})
        if wa:
            R.exact(stage, g, "without-assisted description_only", wa.get("description_only"), True)
            for key in ("model", "n_passes", "pass_status", "output_label"):
                R.exact(stage, g, "without-assisted label copy:" + key, wa.get(key), point.get(key))
            if stage.startswith("blinded"):
                R.exact(stage, g, "without-assisted evaluation status", wa.get("status"), "not_evaluated")
                for key in ("mean_j", "h_j", "B_j", "lower_j", "upper_j", "printed_j_per_output_token"):
                    R.exact(stage, g, "without-assisted blinded null:" + key, wa.get(key), None)
        for item in wa.get("passes", []):
            original = source.get(row_key({**point, "pass_id": item["pass_id"]}))
            expected = None if original is None else {"pass_id": item["pass_id"], **original.get("without_assisted",
                {k: v for k, v in original.items() if k not in ("pass_status", "n_passes")})}
            R.exact(stage, g, "without-assisted pass copy:" + str(item["pass_id"]), item, expected)
        if point.get("status") == "computed":
            # These are independently formed endpoints, so use the energy bar,
            # rather than exact float equality after multiplication/division.
            half = point["h_j"] + point["B_j"]
            for key, endpoint in (("lower_j", "lower"), ("upper_j", "upper")):
                R.number(stage, g, key, point.get(key), point[endpoint] * bt.DECODE_STEPS, bar_energy(half))
    if frozen is not None:
        for point in frozen.get("fit_points", []):
            expected = point_source.get(row_key(point, point=True))
            R.exact(stage, "primary copies/frozen", repr(row_key(point, point=True)), point, expected)
        for sid, ref in frozen.get("neg8_inputs", {}).items():
            R.exact(stage, "primary copies/frozen", "NEG-8:" + sid, ref, references.get(sid))
        for item in frozen.get("tier_fit_inputs", []):
            original = point_source.get(row_key(item, point=True), {})
            R.exact(stage, "primary copies/frozen", "tier:" + repr(row_key(item, point=True)), item,
                    {k: original[k] for k in item if k in original})
    for group in unavailable:
        missing = {p["model"]: p for p in points if p.get("status") != "computed" and
                   (p["boundary"], p["basis"], p["selection"]) == (group["boundary"], group["basis"], group["selection"])}
        R.exact(stage, "primary copies/unavailable", "models", sorted(group["models"]), sorted(missing))
        for item in group.get("refusals", []):
            original = missing.get(item["model"], {})
            keys = ("model", "n_passes", "pass_status", "flags", "reason", "passes")
            R.exact(stage, "primary copies/unavailable", item["model"],
                    {k: item[k] for k in keys if k in item}, {k: original[k] for k in keys if k in original})
    for row in h1_rows:
        original = point_source.get(row_key(row, point=True), {})
        for key in ("model", "n_passes", "pass_status", "role"):
            R.exact(stage, "primary copies/h1", key + ":" + repr(row_key(row, point=True)), row.get(key), original.get(key))
        if "flags" in row:
            flags = set(original.get("flags", []))
            if row.get("status") == "missing":
                flags.update(f for p in original.get("passes", []) for f in p.get("flags", []))
            R.exact(stage, "primary copies/h1", "flags:" + repr(row_key(row, point=True)), row["flags"], sorted(flags))
        measured = original if row["pass_id"] == "mean" else source.get(row_key(row), {})
        if measured.get("status") == "computed":
            energy = measured.get("e", measured["mean_j"] / bt.DECODE_STEPS)
            half = (measured["h_j"] + measured["B_j"]) / bt.DECODE_STEPS
            for check in row.get("checks", []):
                R.number(stage, "primary copies/h1", "measured:" + check["hypothesis"], check.get("measured"), energy, bar_energy(half))
    for row in moe_rows:
        for item in row.get("misses", []) + row.get("missing_models", []):
            original = point_source.get(row_key({**row, "model": item["model"]}, point=True), {})
            for key in ("model", "n_passes", "pass_status", "flags"):
                if key in item or key in original:
                    R.exact(stage, "primary copies/moe", key + ":" + item["model"], item.get(key), original.get(key))
        for item in row.get("misses", []):
            h1 = next((h for h in h1_rows if h["model"] == item["model"] and h["pass_id"] == "mean" and
                       (h["boundary"], h["basis"], h["selection"]) == (row["boundary"], row["basis"], row["selection"])), {})
            checks = {c["hypothesis"]: c for c in h1.get("checks", [])}
            for key, hypothesis in (("resident_above", "resident"), ("bytes_below", "bytes")):
                check = checks.get(hypothesis)
                expected = None if check is None else not check["consistent"] and (
                    check["prediction_lower"] > check["measured_upper"] if key == "resident_above" else
                    check["prediction_upper"] < check["measured_lower"])
                R.exact(stage, "primary copies/moe", key + ":" + item["model"], item.get(key), expected)
        if row.get("status") == "missing":
            missing = [p for p in points if p.get("status") != "computed" and
                       (p["boundary"], p["basis"], p["selection"]) == (row["boundary"], row["basis"], row["selection"])]
            flags = sorted({f for p in missing for item in p.get("passes", []) for f in item.get("flags", [])})
            R.exact(stage, "primary copies/moe", "missing flags", row.get("flags", []), flags)
        if "missing_models" in row:
            R.exact(stage, "primary copies/moe", "status of missing answer", row.get("status"), "missing")
    for row in h2_rows:
        subset = {p["model"]: p for p in points if
                  (p["boundary"], p["basis"], p["selection"]) == (row["boundary"], row["basis"], row["selection"])}
        g = "primary copies/h2/" + repr((row["boundary"], row.get("analysis"), row["basis"], row["selection"]))
        def check_label(item):
            original = subset.get(item["model"], {})
            keys = ("model", "n_passes", "pass_status", "flags")
            R.exact(stage, g, "point label:" + item["model"],
                    {k: item[k] for k in keys if k in item}, {k: original[k] for k in keys if k in original})
        for item in row.get("point_labels", []):
            check_label(item)
        for fit_name in ("two_term", "resident_extended", "tier", "rest"):
            for item in (row.get(fit_name) or {}).get("point_labels", []):
                check_label(item)
        for item in row.get("loo_description", []):
            check_label(item)
            R.exact(stage, g, "observed power copy:" + item["model"], item.get("observed_w"), subset.get(item["model"], {}).get("power"))
        for item in row.get("tier_deviations", []):
            check_label(item)
        terms = {"epsilon": ("two_term", 1), "extended_epsilon": ("resident_extended", 1),
                 "rho": ("resident_extended", 2), "tier_epsilon": ("tier", 1),
                 "tier_rho": ("tier", 2), "rest_epsilon": ("rest", 1), "lambda": ("rest", 2)}
        for item in row.get("primary_intervals", row.get("sensitivity_intervals", [])):
            term = item["term"]
            if term.startswith("tier_deviation:"):
                R.exact(stage, g, "deviation term identity", term, "tier_deviation:" + item["model"])
                original = next((v for v in row["tier_deviations"] if v["model"] == item["model"]), {})
                for key, field in (("estimate", "deviation_w"), ("lower", "lower_w"), ("upper", "upper_w")):
                    R.exact(stage, g, term + ":" + key, item.get(key), original.get(field))
                check_label(item)
                continue
            if term not in terms:
                R.exact(stage, g, "registered interval term", term, sorted(terms))
                continue
            fit_name, index = terms[term]
            fit = row[fit_name]
            copies = {"estimate": fit["coefficients"][index], "lower": fit["intervals"][index][0],
                      "upper": fit["intervals"][index][1], "HC3_se": fit["standard_errors"][index],
                      "OLS_se": fit["ols_standard_errors"][index]}
            for target, field in (("coefficient_C", "coefficient_C"), ("offset_intervals", "offset_intervals"),
                                  ("offset_ols_intervals", "offset_ols_intervals"), ("coefficient_decision", "coefficient_decisions"),
                                  ("offset_decision", "offset_decisions"), ("d_beta_d_delta_per_ms", "d_beta_d_delta_per_ms"),
                                  ("sensitivity_units", "sensitivity_units")):
                if field in fit:
                    copies[target] = fit[field][index]
            R.exact(stage, g, term + ":interval copy", {k: v for k, v in item.items() if k != "term"}, copies)


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
            compare_neg8(R, "blinded-post", rows, tb)
            ap = load(o / "a-blinded-post/model_estimates.json")
            compare_points(R, "blinded-post", ap, tb)
            compare_primary_copies(R, "blinded-post", rows, ap,
                                   h2_rows=load(o / "a-blinded-post/h2.json"), h1_rows=load(o / "a-blinded-post/h1.json"), moe_rows=load(o / "a-blinded-post/moe.json"), unavailable=load(o / "a-blinded-post/unavailable.json"))
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
        compare_primary_copies(R, "blinded", rows, ap, h2_rows=load(o / "a-blinded/h2.json"), h1_rows=load(o / "a-blinded/h1.json"), moe_rows=load(o / "a-blinded/moe.json"), unavailable=load(o / "a-blinded/unavailable.json"))
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
        compare_primary_copies(R, "heldout", held_rows, ap, frozen=frozen, h2_rows=load(o / "a-held/h2.json"), h1_rows=load(o / "a-held/h1.json"), moe_rows=load(o / "a-held/moe.json"), unavailable=load(o / "a-held/unavailable.json"))
        compare_h1(R, "heldout", load(o / "a-held/h1.json"), load(o / "a-held/moe.json"), t2, frozen)
        compare_h2(R, "heldout", load(o / "a-held/h2.json"), t2, ap)
        record = load(o / "a-held/analysis_record.json")
        R.exact("heldout", "primary copies/analysis record", "H1_checks", record.get("H1_checks"), frozen.get("H1_checks"))
        primary_h2 = [r for r in load(o / "a-held/h2.json") if not r["description_only"]]
        R.exact("heldout", "primary copies/analysis record", "H2_intervals", record.get("H2_intervals"),
                [{k: r[k] for k in ("selection", "basis", "boundary", "n", "k")} for r in primary_h2])
        R.exact("heldout", "primary copies/analysis record", "output_label", record.get("output_label"), bt.PER_TOKEN_LABEL)
        R.exact("heldout", "primary copies/analysis record", "note", record.get("note"), frozen.get("note"))
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
    parsed = kp.parse(path)
    positions = iter(parsed.host_ns)
    changed = 0
    for b in lines[1:-1]:
        raw = bytes.fromhex(b["p"])
        out = []
        for i in range(b["n"]):
            f = list(kp.SAMPLE.unpack(raw[i * kp.SAMPLE.size:(i + 1) * kp.SAMPLE.size]))
            host = next(positions) - kp.raw_offset_ns(parsed)
            if t0 <= host < t1:
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
        elif kind in ("member.anchor_not_bounded", "member.target_phase_precheck_failed"):
            codes = [kind]
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
    world, seed, defects, knobs, missing_stores = CAMPAIGNS[name]
    knobs = dict(knobs)
    truncate_marker = knobs.pop("truncate_marker_window", False)
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
    if truncate_marker:
        for session in manifest["sessions"]:
            archive = Path(session["archive"])
            roster = load(archive / "derived/roster.json")["members"]
            ends = []
            for member in roster:
                if member["role"] == "science":
                    bundle = archive / "sources/claim-runs" / member["run_id"]
                    events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
                    ends.append(ba._event_span(events, "decode", load(bundle / "metadata.json"))[1])
            # Pass 1 ends inside the delayed end window, after science decode.
            # Pass 2 ends before the last decode's delayed marker window starts,
            # leaving no marker polls and making not_evaluated non-vacuous.
            last_member = next(member for member in reversed(roster) if member["role"] == "science")
            bundle = archive / "sources/claim-runs" / last_member["run_id"]
            events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
            last_start = ba._event_span(events, "decode", load(bundle / "metadata.json"))[0]
            cutoff = (max(ends) if session["pass_id"] == 1 else last_start) + 1_000_000_000
            stream = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
            batches = [json.loads(line) for line in stream.read_text().splitlines()]
            stream.write_text("".join(json.dumps(b) + "\n" for b in batches
                                       if b.get("k") != "b" or b["rx"] <= cutoff))
    # B6 ruling Q1: a withheld file goes missing after the export wrote it (a file-custody fault);
    # the sidecar's count-only locator stays.
    removed = []
    for session_id in missing_stores:
        sidecar = next(root.glob(f"export/*/{session_id}.session.json"))
        info = ba.read_json(sidecar)["blinding"]["withheld"]
        store = sidecar.parent / info["path"]
        store.unlink()
        removed.append({"session_id": session_id, "store": str(store), "row_count": info["row_count"]})
    if name == "compressed":
        # Desk layout from the cold probe: both primary-byte files of every
        # Qwen3-8B claim run, after export, with the plain originals removed.
        for session in manifest["sessions"]:
            for events in Path(session["archive"]).glob("sources/claim-runs/qwen3-8b-4bit-*/events.jsonl"):
                for path in (events, events.with_name("metadata.json")):
                    compress_member(path, Path(session["archive"]))
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
        result = subprocess.run(ample_space_command(command), cwd=ROOT, capture_output=True, text=True, check=False)
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
    explain (at most 0.5 uW x T): a whole 20 ms sample taken or lost at a decode edge.  Read with
    the twin's own meter reader and export reader after every key is released."""
    root = WORK["root"] / name
    manifest = load(root / "manifest.json")
    released = root / "released-keys/bytes/blinding"
    flips = runs = 0
    largest = 0.0
    sample_intervals = set()
    for session in manifest["sessions"]:
        archive = bt.load_archive(session["archive"])
        sample_intervals.update(stream["step_ms"] / 1000 for stream in archive["streams"] if stream["aligned"])
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
    assert len(sample_intervals) == 1
    return {"runs": runs, "flips": flips, "largest_error_j": largest,
            "label_offset_s": manifest["synthetic_parameters"]["min_receive_latency_ms"] / 1000,
            "sample_interval_s": sample_intervals.pop()}
@unittest.skipUnless(shutil.which("zstd"), "compressed refusal probes require zstd on PATH")
class CompressedRefusalTests(unittest.TestCase):
    """Fable variants 01-03: storage corruption terminates both programs."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="bytes-compressed-refusal-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name) / "compressed"
        cls.manifest = build(cls.root, "compressed")
        cls.session = next(s for s in cls.manifest["sessions"] if s["pass_id"] == 1)
        cls.archive = Path(cls.session["archive"])
        cls.run_id = "qwen3-8b-4bit-0"
        cls.bundle = cls.archive / "sources/claim-runs" / cls.run_id

    def replay(self, name, payload, variant):
        path = self.bundle / (name + ".zst")
        original = path.read_bytes()
        try:
            path.write_bytes(payload(original))
            keys = self.root / "private-keys/bytes/blinding"
            records = ba.archive_records(self.archive, self.manifest, self.session,
                                         stage="fit", key_dir=keys)
            with mock.patch.object(desk_restore.shutil, 'disk_usage', return_value=type('Space', (), {'free': 1024**4})()):
                with self.assertRaisesRegex(RestoreRefused, "restore_refused: "):
                    list(records)
            output = self.root / (variant + ".json")
            argv = [sys.executable, "-B", str(ROOT / "scripts/bytes_twin.py"),
                    "--export-dir", str(self.root / "export"),
                    "--manifest", str(self.root / "manifest.json"),
                    "--key-dir", str(keys), "--stage", "1", "--out", str(output)]
            for session in self.manifest["sessions"]:
                argv += ["--archive", session["archive"]]
            result = subprocess.run(ample_space_command(argv), cwd=ROOT, capture_output=True, text=True)
            print(f"\ncompressed probe {variant}: analysis=restore_refused "
                  f"twin_exit={result.returncode} refusal={result.stdout.startswith('refused: ')}",
                  flush=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertTrue(result.stdout.startswith("refused: restore_refused: "), result.stdout)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(output.exists())
        finally:
            path.write_bytes(original)

    def test_01_truncated_events_frame_analysis_unusable_twin_refuses(self):
        self.replay("events.jsonl", lambda frame: frame[:len(frame) // 2], "01-truncated-frame")

    def test_02_flipped_metadata_bytes_analysis_unusable_twin_refuses(self):
        def flip(frame):
            damaged = bytearray(frame)
            # Reproduce Fable's 16 mid-frame byte flips (not a numeric bar).
            middle = len(frame) // 2
            for index in range(middle, middle + 16):
                damaged[index] ^= 0xff
            return bytes(damaged)
        self.replay("metadata.json", flip, "02-flipped-bytes")

    def test_03_non_json_metadata_payload_analysis_unusable_twin_refuses(self):
        frame = subprocess.run(["zstd", "-qc"], input=b"not JSON", capture_output=True,
                               check=True).stdout
        self.replay("metadata.json", lambda _: frame, "03-non-json-payload")

    def test_short_reserve_stops_both_programs(self):
        keys = self.root / 'private-keys/bytes/blinding'
        with mock.patch.object(desk_restore.shutil, 'disk_usage', return_value=type('Space', (), {'free': 0})()):
            with self.assertRaisesRegex(RestoreRefused, 'restore_refused: insufficient scratch space'):
                list(ba.archive_records(self.archive, self.manifest, self.session, stage='fit', key_dir=keys))
        commands = [
            [sys.executable, '-B', str(ROOT / 'scripts/bytes_analyze.py'), '--export', str(self.root / 'export'),
             '--manifest', str(self.root / 'manifest.json'), '--key-dir', str(keys), '--stage', 'fit',
             '--out', str(self.root / 'short-analysis')],
            [sys.executable, '-B', str(ROOT / 'scripts/bytes_twin.py'), '--export-dir', str(self.root / 'export'),
             '--manifest', str(self.root / 'manifest.json'), '--key-dir', str(keys), '--stage', '1',
             '--out', str(self.root / 'short-twin.json')]]
        for session in self.manifest['sessions']:
            commands[1] += ['--archive', session['archive']]
        for command in commands:
            result = subprocess.run(ample_space_command(command, free=0), cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('restore_refused: insufficient scratch space', result.stdout + result.stderr)
            self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((self.root / 'short-analysis/predictions.json').exists())
        self.assertFalse((self.root / 'short-twin.json').exists())


    def test_journal_less_campaign_stops_both_programs(self):
        journal = Path(str(self.archive) + '.desk') / 'compression.jsonl'
        saved = journal.read_bytes()
        journal.unlink()
        keys = self.root / 'private-keys/bytes/blinding'
        try:
            with self.assertRaisesRegex(RestoreRefused, 'restore_refused:.*compression.jsonl'):
                list(ba.archive_records(self.archive, self.manifest, self.session, stage='fit', key_dir=keys))
            programs = [
                [sys.executable, '-B', str(ROOT / 'scripts/bytes_analyze.py'), '--export', str(self.root / 'export'),
                 '--manifest', str(self.root / 'manifest.json'), '--key-dir', str(keys), '--stage', 'fit',
                 '--out', str(self.root / 'journal-less-analysis')],
                [sys.executable, '-B', str(ROOT / 'scripts/bytes_twin.py'), '--export-dir', str(self.root / 'export'),
                 '--manifest', str(self.root / 'manifest.json'), '--key-dir', str(keys), '--stage', '1',
                 '--out', str(self.root / 'journal-less-twin.json')]]
            for session in self.manifest['sessions']:
                programs[1] += ['--archive', session['archive']]
            for command in programs:
                result = subprocess.run(ample_space_command(command), cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn('restore_refused:', result.stdout + result.stderr)
                self.assertIn('compression.jsonl', result.stdout + result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse((self.root / 'journal-less-analysis/predictions.json').exists())
                self.assertFalse((self.root / 'journal-less-twin.json').exists())
        finally:
            journal.write_bytes(saved)



class AgreementTests(unittest.TestCase):
    """Every campaign, every stage: zero differences above the bar; the under-bar count is printed."""

    def check(self, name, expected_words, expected_h2):
        R = campaign(name)
        above = R.above()
        counts = R.counts()
        self.assertEqual(above, [], f"{name}: {len(above)} above the bar:\n" + "\n".join(describe(r) for r in above[:40]))
        # One count per campaign for the differences under the bar (Addendum 8.1), not classified.
        print(f"\nagreement {name}: compared {counts['compared']}, equal {counts['equal']}, "
              f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}; "
              f"diagnostics {counts['diagnostic_compared']}, different {counts['diagnostic_different']}")
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
        """Omitting each printed offset column must fail the campaign's registered bars.

        At 50 SPS an individual bound can be below its cell's 1% bar. The
        complete-column omission must still be detected, without widening
        any bar or imposing an extra acceptance condition on a valid cell.
        """
        rows = [r for r in R.rows if r["stage"] == "heldout"]
        for key in ("coefficient_C", "offset_lower", "offset_upper", "meter_offset_bound_j", "meter_offset_bound_w"):
            hits = [r for r in rows if r["key"].split(":")[-1] == key and "abs" in r]
            self.assertTrue(hits, f"{name}: no {key} compared")
            omission = Recorder()
            for row in hits:
                omission.number(row["stage"], row["group"], row["key"], row["a"], 0.0, row["bar"])
            self.assertTrue(omission.above(), f"{name}: omitting {key} does not fail the registered bar")
        # F3: sensitivities remain visible as diagnostics; their effect is
        # checked through the printed coefficient intervals and C terms.
        hits = [r for r in R.diagnostics if r["stage"] == "heldout" and r["key"].endswith(":d_beta_d_delta_per_ms")]
        self.assertTrue(hits, f"{name}: no d_beta_d_delta_per_ms compared")
        self.assertTrue(any(r["a"] != 0 for r in hits))
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
        root = WORK["root"] / "bytes"
        rows = load(root / "out/a-held/heldout_pass_estimates.json")
        terms = [t for r in rows if r["boundary"] == "DC input" and r["selection"] == "primary"
                 and r["basis"] == "gross primary" for t in r.get("meter_run_terms", [])]
        # Fixture discharges at 12.774 W for 0.8--1 s: at least 10 J, above the
        # registered approximately 1 J per-run attribution limit, both in decode and at its edges.
        self.assertTrue(any(t["battery_gross_j"] > 1 for t in terms))
        self.assertTrue(any(t["battery_v_start_j"] > 1 for t in terms))
        self.assertTrue(any(t["battery_v_end_j"] > 1 for t in terms))

    def test_neg8_reference_battery_omission_is_detected(self):
        campaign("bytes")
        root = WORK["root"] / "bytes"
        # Fault the independent program's request term only. NEG-8 consumes
        # request energy; science cells consume decode energy and stay intact.
        source = (ROOT / "scripts/bytes_twin.py").read_text()
        expression = 'request_energy + request_battery["battery_gross_j"]'
        self.assertEqual(source.count(expression), 1)
        mutant = root / "twin-no-reference-battery.py"
        mutant.write_text(source.replace(expression, "request_energy"))
        manifest = load(root / "manifest.json")
        output = root / "no-reference-battery.json"
        command = [sys.executable, str(mutant), "--export-dir", str(root / "export"),
                   "--manifest", str(root / "manifest.json"), "--stage", "2",
                   "--key-dir", str(root / "released-keys/bytes/blinding"), "--out", str(output)]
        for session in manifest["sessions"]:
            command += ["--archive", session["archive"]]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        wrong = load(output)
        original = load
        with mock.patch(__name__ + ".load", side_effect=lambda p: wrong if Path(p) == root / "out/t-2.json" else original(p)):
            above = compare_campaign(root).above()
        self.assertTrue(any(r["group"].startswith("neg8/") and r["stage"] == "heldout" for r in above),
                        "omitting reference battery energy must fail NEG-8 agreement itself")

    def test_incomplete_marker_window_campaign(self):
        R = campaign("marker_incomplete")
        self.assertEqual(R.above(), [], "\n".join(describe(r) for r in R.above()[:40]))
        counts = R.counts()
        print(f"\nagreement marker_incomplete: compared {counts['compared']}, equal {counts['equal']}, "
              f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}; "
              f"diagnostics {counts['diagnostic_compared']}, different {counts['diagnostic_different']}")
        root = WORK["root"] / "marker_incomplete"
        manifest = load(root / "manifest.json")
        records = ba.load_records(root / "export", manifest, stage="all", key_dir=root / "released-keys/bytes/blinding")
        self.assertTrue(any(r.get("meter") and not r["meter"]["battery_end_window_complete"] for r in records))
        twin = load(root / "out/t-2.json")
        reasons = [str(est.get("without_assisted", {}).get("reason", ""))
                   for model in twin["cells"].values() for pk, block in model.items() if pk != "passes_mean"
                   for cell in block["boundaries"].values() for variant in VMAP.values()
                   for est in [cell.get(variant, {})]]
        self.assertFalse(any("blinded stage" in reason for reason in reasons))
        unevaluated = [cell[variant]["without_assisted"]
                       for model in twin["cells"].values() for pk, block in model.items() if pk != "passes_mean"
                       for cell in block["boundaries"].values() for variant in VMAP.values()
                       if cell.get(variant, {}).get("without_assisted", {}).get("status") == "not_evaluated"]
        self.assertTrue(unevaluated, "campaign must exercise cells with no marker-window polls")
        for line in unevaluated:
            self.assertIn("no mapped meter stream has polls carrying B0AC in the marker window", line["reason"])

    def test_late_start_marker_window_campaign(self):
        recorder = campaign("late_start")
        self.assertEqual(recorder.above(), [], "\n".join(describe(r) for r in recorder.above()[:40]))
        counts = recorder.counts()
        print(f"\nagreement late_start: compared {counts['compared']}, equal {counts['equal']}, "
              f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}; "
              f"diagnostics {counts['diagnostic_compared']}, different {counts['diagnostic_different']}")
        root = WORK["root"] / "late_start"
        manifest = load(root / "manifest.json")
        records = ba.load_records(root / "export", manifest, stage="all", key_dir=root / "released-keys/bytes/blinding")
        partial = [r for r in records if r.get("meter") is None and r.get("decode_assist_evaluated")]
        self.assertTrue(partial, "late-start stream must miss decode coverage but reach the marker window")
        self.assertTrue(any("bytes.decode_battery_assist" in r["flags"] for r in partial))
        self.assertTrue(any(r["battery_end_window_complete"] for r in partial))

    def test_meter_batches_without_new_samples_campaigns(self):
        for name in ("empty_payload_n", "replayed_batch", "replayed_tail", "first_batch_tail_replayed"):
            with self.subTest(campaign=name):
                recorder = campaign(name)
                self.assertEqual(recorder.above(), [], "\n".join(describe(r) for r in recorder.above()[:40]))
                counts = recorder.counts()
                print(f"\nagreement {name}: compared {counts['compared']}, equal {counts['equal']}, "
                      f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}; "
              f"diagnostics {counts['diagnostic_compared']}, different {counts['diagnostic_different']}")

    def test_unaligned_marker_campaigns(self):
        for name in ("polls_only", "header_closed"):
            with self.subTest(campaign=name):
                recorder = campaign(name)
                self.assertEqual(recorder.above(), [], "\n".join(describe(r) for r in recorder.above()[:40]))
                counts = recorder.counts()
                print(f"\nagreement {name}: compared {counts['compared']}, equal {counts['equal']}, "
                      f"under the bar {counts['under_bar']}, above the bar {counts['above_bar']}; "
              f"diagnostics {counts['diagnostic_compared']}, different {counts['diagnostic_different']}")
                root = WORK["root"] / name
                records = ba.load_records(root / "export", load(root / "manifest.json"), stage="all",
                                          key_dir=root / "released-keys/bytes/blinding")
                self.assertEqual(len(records), 1000)
                self.assertTrue(all(r["meter"] is None and r.get("decode_assist_evaluated") for r in records))
                self.assertTrue(any("bytes.decode_battery_assist" in r["flags"] for r in records))

    def test_unresolved_anchors_are_unusable_in_both_selections(self):
        R = self.check("invalid_anchor", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
                                              "h2/rest/passes_mean": (11, 11)})
        root = WORK["root"] / "invalid_anchor"
        planted = load(root / "build.json")["defects"]
        manifest = ba.read_json(root / "manifest.json")
        # This generator reuses run IDs across passes; session + run is the identity.
        unusable = {(s["session_id"], d["run_id"]) for d in planted for s in manifest["sessions"]
                    if s["pass_id"] == d["pass"]}
        primary = ba.load_records(root / "export", manifest, stage="all", key_dir=root / "released-keys/bytes/blinding")
        bad = [r for r in primary if (r["session_id"], r["run_id"]) in unusable]
        self.assertEqual(len(bad), len(unusable))
        self.assertTrue(all(r["status"] == "unusable" and r["invalid_energy_record"] for r in bad))
        twin = load(root / "out/t-2.json")
        removed = [(cell["session_id"], r) for model in twin["cells"].values() for key, cell in model.items() if key != "passes_mean"
                   for boundary in cell["boundaries"].values() for r in boundary.get("removed_members", [])
                   if (cell["session_id"], r["run_id"]) in unusable]
        self.assertEqual({(session, r["run_id"]) for session, r in removed}, unusable)
        self.assertTrue(all(r["status"] == "unusable" and not r["restorable"] for _, r in removed))
        passes = {f"pass{d['pass']}" for d in planted}
        kept = [r for r in R.rows if r["stage"] == "heldout" and r["key"] == "kept_runs"
                and r["group"].split("/")[2] in passes]
        self.assertTrue(kept)
        ids = {run_id for _, run_id in unusable}
        self.assertTrue(all(not (ids & set(r[side])) for r in kept for side in ("a", "t")))

    @unittest.skipUnless(shutil.which("zstd"), "compressed-bundle campaign requires zstd on PATH")
    def test_compressed_bundle_campaign(self):
        # Same words and fits as bytes: compression changes storage only.
        # check uses the existing per-field derived agreement bars above.
        self.check("compressed", 63, {"h2/rails/passes_mean": (9, 9), "h2/dc_input/passes_mean": (9, 9),
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
        without = [r for r in R.rows if "/without_assisted" in r["group"] and r["key"] == "status"
                   and r["stage"] in ("fit", "heldout")]
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
        sensitivity = [r for r in R.rows if r["group"].endswith("two_pass_sensitivity") and r["key"] == "n"]
        self.assertEqual({(r["a"], r["t"]) for r in sensitivity}, {(9, 9)})


class ComparerRegressionTests(unittest.TestCase):
    def test_reference_reasons_compare_codes_and_preserve_unknown_words(self):
        for prose in ("meter does not cover decode and own idle spans", "meter span has no samples",
                      "battery reading missing", "meter request unavailable",
                      "meter clock fit or raw/monotonic mapping unavailable: fewer than two batches with samples"):
            self.assertEqual(reference_reason_code(prose), "bytes.meter_decode_unavailable")
        self.assertEqual(reference_reason_code("dropped device sample in meter span"), "bytes.meter_gap")
        for reason in ("bytes.reference_request_unavailable", "bytes.meter_gap", "status: failed",
                       "excluded: member.anchor_not_bounded", "bytes.__coverage_fault__",
                       "unrecognized diagnostic", "bytes.meter_gap__coverage_fault__"):
            self.assertEqual(reference_reason_code(reason), reason)

    def test_unprinted_differences_are_counted_without_gating_or_a_tolerance(self):
        recorder = Recorder()
        for key in ("variance", "mse", "d_beta_d_delta_per_ms"):
            recorder.number("probe", "diagnostic", key, 1, 1e30, None)
        recorder.exact("probe", "copies", "row", {"mean_j": 1, "covariance": [[1]]},
                       {"mean_j": 1, "covariance": [[1e30]]})
        self.assertEqual(recorder.above(), [])
        self.assertEqual(recorder.counts()["diagnostic_different"], 3)
        self.assertTrue(all("bar" not in row for row in recorder.diagnostics))
        recorder.number("probe", "printed", "mean_j", 1, 2, .001)
        self.assertEqual(len(recorder.above()), 1)

    def test_h2_error_precision_is_the_half_width_printed_place(self):
        self.assertEqual(bar_h2_printed(123.4), 5)
        self.assertEqual(bar_h2_printed(99.99), 5)
        self.assertEqual(bar_h2_printed(.001234), .00005)
        self.assertEqual(bar_h2_printed(0), 0)

    def test_registered_BW_and_drift_scale_mutations_are_above_bar(self):
        recorder = Recorder()
        recorder.number("probe", "model", "BW", 266, 266.05, bar_duration_derived(266, 2.37))
        recorder.number("probe", "cell", "drift_scale", 100, 100.00005, None)
        self.assertEqual(len(recorder.above()), 2)
        self.assertEqual([r["bar"] for r in recorder.rows], [0.0005, 0.0000005])

    def test_not_evaluated_reason_run_sets_are_compared_in_both_directions(self):
        campaign("marker_incomplete")
        root = WORK["root"] / "marker_incomplete"
        primary_path = root / "out/a-held/heldout_pass_estimates.json"
        twin_path = root / "out/t-2.json"
        primary, twin = load(primary_path), load(twin_path)
        row = next(r for r in primary if r.get("decode_assisted_member_counts_reason"))
        block = twin["cells"][canon(row["model"])][f"pass{row['pass_id']}"]["boundaries"][BMAP[row["boundary"]]]
        est = block[VMAP[(row["basis"], row["selection"])]]
        for field in ("decode_assisted_member_counts_reason", "without_assisted"):
            for side in ("primary", "twin"):
                with self.subTest(field=field, side=side):
                    target = row if side == "primary" else est
                    parent, key = (target[field], "reason") if field == "without_assisted" else (target, field)
                    original_value = parent[key]
                    parent[key] += "; no polls (run planted-run-id)"
                    original_load = load
                    try:
                        with mock.patch(__name__ + ".load", side_effect=lambda p: (
                                primary if Path(p) == primary_path else twin if Path(p) == twin_path else original_load(p))):
                            above = compare_campaign(root).above()
                        expected_key = "reason:run_ids" if field == "without_assisted" else field + ":run_ids"
                        self.assertTrue(any(r["key"] == expected_key for r in above))
                    finally:
                        parent[key] = original_value
        self.assertEqual(reason_run_ids("cause (run b); cause (run a); again (run b)"), ["a", "b"])

    def test_row_census_detects_deletions_additions_and_unknown_labels(self):
        rows = [{"model": "Qwen3-1.7B-4bit", "pass_id": 1, "boundary": "rails", "basis": basis,
                 "selection": selection, "status": "unavailable"} for basis, selection in VMAP]
        cell = {variant: {"status": "unavailable"} for variant in VMAP.values()}
        twin = {"cells": {canon(rows[0]["model"]): {
            "pass1": {"boundaries": {"rails": cell}},
            "passes_mean": {"boundaries": {"rails": {"quantities": cell}}}}}}
        for point, compare in ((False, compare_cells), (True, compare_points)):
            baseline = Recorder()
            compare(baseline, "fixture", rows, twin)
            self.assertEqual(baseline.above(), [])
            for index in range(len(rows)):
                for kind in ("delete", "extra", "basis", "selection"):
                    with self.subTest(point=point, index=index, kind=kind):
                        changed = copy.deepcopy(rows)
                        if kind == "delete":
                            changed.pop(index)
                        elif kind == "extra":
                            changed.append(dict(rows[index]))
                        else:
                            changed[index][kind] = "unregistered"
                        recorder = Recorder()
                        compare(recorder, "fixture", changed, twin)
                        self.assertTrue(recorder.above())
            recorder = Recorder()
            extra = copy.deepcopy(twin)
            extra["cells"]["unexpected-model"] = copy.deepcopy(next(iter(twin["cells"].values())))
            compare(recorder, "fixture", rows, extra)
            self.assertTrue(recorder.above())

    def test_meter_census_and_no_half_width_duration_bars(self):
        for key in ("battery_tau_s", "battery_poll_interval_max_s", "sample_interval_s", "r_max_s"):
            with self.subTest(key=key):
                row = {"meter_run_terms": [{"run_id": "member", key: .008}]}
                other = {"meter_run_terms": [{"run_id": "member", key: .0091}]}
                recorder = Recorder()
                compare_battery_columns(recorder, "fixture", "meter", row, other, 100)
                self.assertTrue(recorder.above())
        for row, other in (({"meter_run_terms": []}, {"meter_run_terms": [{"run_id": "member"}]}),
                           ({"meter_run_terms": [{"run_id": "member"}]}, {"meter_run_terms": []})):
            recorder = Recorder()
            compare_battery_columns(recorder, "fixture", "meter", row, other, 100)
            self.assertTrue(recorder.above())

    def test_missing_own_half_width_is_an_explicit_failure(self):
        campaign("bytes")
        root = WORK["root"] / "bytes" / "out"
        points = load(root / "a-held/model_estimates.json")
        missing = canon("Qwen3-1.7B-4bit")
        points = [p for p in points if canon(p["model"]) != missing]
        rows = [r for r in load(root / "a-held/h2.json") if r["boundary"] == "rails"]
        recorder = Recorder()
        compare_h2(recorder, "fixture", rows, load(root / "t-2.json"), points)
        self.assertTrue(any(r["key"].endswith(":own half-width present") for r in recorder.above()))
        self.assertFalse(any(r.get("bar") == 0 and r["group"].endswith("/loo") for r in recorder.rows))

    def test_rest_intercept_bar_uses_ceiling_and_clears_observed_noise(self):
        recorder = campaign("bytes")
        root = WORK["root"] / "bytes" / "out"
        h2 = next(r for r in load(root / "a-held/h2.json") if
                  (r["boundary"], r["basis"], r["selection"]) == ("rest", "gross primary", "primary"))
        powers = [p["power"] for p in load(root / "a-held/model_estimates.json") if
                  (p["boundary"], p["basis"], p["selection"]) == ("rest", "gross primary", "primary")]
        # Independent lower-edge calculation from the doctrine's 1e6 × noise,
        # the centred Gram condition number ~4 VIF and the RMS response scale.
        floor = 1e6 * sys.float_info.epsilon * 4 * h2["rest"]["vif"] * math.sqrt(sum(v*v for v in powers) / len(powers))
        fit = h2["rest"]
        ceilings = {}
        half = (fit["intervals"][0][1] - fit["intervals"][0][0]) / 2
        for field, keys in (("intervals", ("estimate", "lower[HC3]", "upper[HC3]")),
                            ("ols_intervals", ("lower[OLS label]", "upper[OLS label]")),
                            ("offset_intervals", ("coefficient_C", "offset_lower", "offset_upper")),
                            ("offset_ols_intervals", ("offset_ols_lower", "offset_ols_upper"))):
            ceilings.update({"rest:c:" + key: (bar_h2_printed(half) if key == "coefficient_C"
                                             else .01 * half) for key in keys})
        rows = [r for r in recorder.rows if r["stage"] == "heldout" and r["key"] in ceilings]
        self.assertEqual({r["key"] for r in rows}, set(ceilings))
        self.assertGreater(floor, min(ceilings.values()), "bytes campaign must have an empty doctrine window")
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertEqual(row["bar"], ceilings[row["key"]])
                self.assertLessEqual(row["abs"], row["bar"])
                if floor > row["bar"] and row["key"] != "rest:c:coefficient_C":
                    self.assertIn(f"{floor / row['bar']:.12g}", row.get("note", ""))

    def test_hypothesis_censuses_detect_missing_extra_and_relabelled_rows(self):
        campaign("bytes")
        root = WORK["root"] / "bytes" / "out"
        h1, moe, h2 = [load(root / ("a-held/" + name + ".json")) for name in ("h1", "moe", "h2")]
        twin = load(root / "t-2.json")
        points = load(root / "a-held/model_estimates.json")
        for table, rows in (("h1", h1), ("moe", moe), ("h2", h2)):
            baseline = Recorder()
            if table == "h2":
                compare_h2(baseline, "heldout", rows, twin, points)
            else:
                compare_h1(baseline, "heldout", h1, moe, twin, None)
            self.assertEqual(baseline.above(), [])
            indices = [i for i, r in enumerate(rows) if
                       (r["basis"], r["selection"]) == ("gross primary", "primary") and
                       (table != "h1" or r["role"] == "heldout")]
            self.assertTrue(indices)
            for index in indices:
                for kind in ("delete", "duplicate", "relabel"):
                    with self.subTest(table=table, index=index, kind=kind):
                        changed = copy.deepcopy(rows)
                        if kind == "delete":
                            changed.pop(index)
                        elif kind == "duplicate":
                            changed.append(dict(rows[index]))
                        else:
                            changed[index]["selection"] = "flagged-inclusive"
                        result = Recorder()
                        if table == "h2":
                            compare_h2(result, "heldout", changed, twin, points)
                        else:
                            compare_h1(result, "heldout", changed if table == "h1" else h1,
                                       changed if table == "moe" else moe, twin, None)
                        self.assertTrue(any(r["group"] == table + " census" for r in result.above()),
                                        "the comparer itself must detect changed row identities")


class WordRuleTests(unittest.TestCase):
    def test_near_zero_endpoint_never_excuses_unequal_decision_words(self):
        # Planted edge case: the lower endpoints differ by 2e-10, far inside
        # 1% of this 5e-5 half-width (5e-7), but lie on opposite sides of zero.
        # This is a fixture placement, not a smaller numerical agreement bar.
        fit = {"intervals": [[-1e-10, 1e-4]], "coefficient_decisions": ["contains zero"],
               "systematics_flag": "fixture has no bound", "sensitivity_flag": "fixture has no sensitivity",
               "sensitivity_units": ["J/GB per ms"]}
        twin = {"offset": {"coefficient_decision": "positive", "systematics_flag": fit["systematics_flag"],
                           "sensitivity_flag": fit["sensitivity_flag"], "sensitivity_units": "J/GB per ms"}}
        recorder = Recorder()
        half = (fit["intervals"][0][1] - fit["intervals"][0][0]) / 2
        numeric = recorder.number("fixture", "edge", "lower", -1e-10, 1e-10, bar_coefficient(half))
        _offset_alternative(recorder, "fixture", "edge", "epsilon", fit, 0, twin)
        self.assertEqual(numeric["status"], "under_bar")
        self.assertEqual([row["key"] for row in recorder.above()], ["epsilon:coefficient_decision"])


class MarkerPathAgreementTests(unittest.TestCase):
    """Small real stream files exercise every parser/join marker gate without a campaign."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="marker-paths-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "sources/night-custody/hazards/meter"
        self.directory.mkdir(parents=True)
        self.path = self.directory / "stream-001.jsonl"
        self.spans = {"decode_ns": [4_000_000_000, 8_000_000_000],
                      "idle_ns": [0, 2_000_000_000], "request_ns": [2_000_000_000, 8_000_000_000]}

    def items(self):
        items = [{"k": "h", "status": "streaming", "rate_idx": 2,
                  "start_raw_ns": 0, "start_mono_ns": 0}]
        for i in range(13):
            # Keep the cold probe's poll/last-sample clocks, but supply every
            # intervening 20 ms device counter instead of implicit dropouts.
            counters = range((i - 1) * 1000 + 20, i * 1000 + 1, 20) if i else [0]
            words = [kp.SAMPLE.pack(c, 0, 12_000_000, 1_000_000, 0, 0, 0, 0) for c in counters]
            items.append({"k": "b", "rx": i * 1_000_000_000, "tx": i * 1_000_000_000 - 1_000_000,
                          "n": len(words), "p": b"".join(words).hex(),
                          "smc": {"B0AC": -1000 if i == 9 else 0, "B0AV": 12000}})
        return items + [{"k": "t", "end_raw_ns": 12_000_000_000, "end_mono_ns": 12_000_000_000}]

    def write(self, items):
        self.path.write_text("".join(json.dumps(item) + "\n" for item in items))

    def primary_decision(self, streams):
        """Use the primary's energy join first, then its registered marker fallback."""
        for _, stream in streams:
            try:
                result = ba.meter_decode(stream, self.spans["decode_ns"], self.spans["idle_ns"])
                offset = kp.raw_offset_ns(stream)
                window = [t + offset for t in self.spans["decode_ns"]]
                marker = ba._decode_battery_marker(stream, window, ba._battery_delay_ns(stream))
                return True, marker, result["battery_end_window_complete"]
            except ba.AnalysisError:
                pass
        markers, complete = [], []
        for _, stream in streams:
            offset = kp.raw_offset_ns(stream)
            if offset is None:
                continue
            window = [t + offset for t in self.spans["decode_ns"]]
            tau_ns = ba._battery_delay_ns(stream)
            marker = ba._decode_battery_marker(stream, window, tau_ns)
            if marker is None:
                continue
            markers.append(marker)
            complete.append(stream.poll_ns[-1] >= window[1] + tau_ns)
        return False, any(markers) if markers else None, any(complete)

    def assert_agreement(self):
        selected = [self.spans["decode_ns"], self.spans["idle_ns"]]
        primary = ba._session_streams(self.root, selected)
        twin = bt.load_archive(self.root)
        with mock.patch.object(bt, "_bundle", return_value=self.root), mock.patch.object(
                bt, "member_spans", return_value=self.spans):
            actual = bt.dc_join(twin, "member")
        expected = self.primary_decision(primary)
        self.assertEqual((actual["status"] == "ok", actual.get("decode_assisted"),
                          actual.get("battery_end_window_complete")), expected)
        return primary, twin, actual

    def test_marker_without_current_is_unknown_on_energy_and_marker_only_paths(self):
        for successful in (False, True):
            with self.subTest(successful=successful):
                items = self.items()
                if not successful:
                    items[0]["status"] = "closed"
                for item in items:
                    if item.get("k") == "b" and 7_000_000_000 <= item["rx"] < 11_000_000_000:
                        item["smc"].pop("B0AC")
                self.write(items)
                _, _, actual = self.assert_agreement()
                self.assertEqual(actual["status"] == "ok", successful)
                self.assertIsNone(actual.get("decode_assisted"))
                reason = actual["decode_assist_evaluated_reason"]
                self.assertIn("selected meter stream" if successful else "no mapped meter stream", reason)
                self.assertIn("B0AC", reason)
                self.assertIn("member", reason)

    def test_batches_without_new_samples_match_native_fit_points(self):
        for case in ("empty_payload_n", "replayed_batch"):
            with self.subTest(path=case):
                items = self.items()
                items[7]["p"] = "" if case == "empty_payload_n" else items[2]["p"]
                self.write(items)
                native = kp.parse(self.path)
                primary, twin, _ = self.assert_agreement()
                stream = primary[0][1]
                self.assertEqual(stream.fit.stats, native.fit.stats)
                self.assertEqual(twin["streams"][0]["fit"]["points"], native.fit.stats["points"])
                self.assertEqual(native.fit.stats["points"], 12)
                self.assertEqual(stream.poll_ns, native.poll_ns)

    def shape_cases(self):
        """Cold rounds b/c/d probes, including replay within a native batch."""
        cases = {}
        for name in ("baseline", "empty_p_n0", "empty_p_n1", "seq_equals_running_max",
                     "replayed_batch", "tail_word_replayed", "new_word_then_replayed_tail", "first_batch_tail_replayed",
                     "mid_word_replayed_last_advances", "partial_tail", "partial_mid",
                     "partial_mid_payload_n0", "only_partial", "one_partial",
                     "header_closed", "only_partial_header_closed", "one_partial_header_closed",
                     "nonhex_payload", "nonstring_payload", "whitespace_hex",
                     "n0_nonhex", "n0_nonstring", "missing_payload", "reversed_polls",
                     "dup_poll", "dup_rx_diff_payload", "smc_with_p_key", "voltage_missing",
                     "edge_poll_start", "edge_poll_end",
                     "dropped_edge_sample", "dropped_start_sample", "dropped_idle_end_sample",
                     "wrap", "long_stall"):
            items = self.items()
            if name in ("empty_p_n0", "empty_p_n1"):
                items[7].update(n=int(name.endswith("n1")), p="")
            if name in ("seq_equals_running_max", "replayed_batch"):
                items[7]["p"] = items[6 if name == "seq_equals_running_max" else 2]["p"]
            if name in ("tail_word_replayed", "new_word_then_replayed_tail"):
                # The cold probe puts the next batch's word here, then an
                # old tail. Native has no fit point at that following batch.
                word = items[8 if name == "tail_word_replayed" else 7]["p"]
                items[7].update(n=2, p=word + items[2]["p"])
            if name == "first_batch_tail_replayed":
                word = kp.SAMPLE.pack(100, 0, 12_000_000, 1_000_000, 0, 0, 0, 0).hex()
                items[1].update(n=2, p=word + items[1]["p"])
            if name == "mid_word_replayed_last_advances":
                word = kp.SAMPLE.pack(6100, 0, 12_000_000, 1_000_000, 0, 0, 0, 0).hex()
                items[7].update(n=3, p=items[7]["p"] + items[2]["p"] + word)
            if name == "partial_tail":
                items[-2]["p"] += "ab"
            if name in ("partial_mid", "partial_mid_payload_n0"):
                items[7]["p"] += "ab" + items[7]["p"]
                if name.endswith("n0"):
                    items[7]["n"] = 0
            if name.startswith("only_partial"):
                for batch in items[1:-1]:
                    batch["p"] = "ab"
            if name.startswith("one_partial"):
                items[7]["p"] = "ab"
            if name.endswith("header_closed"):
                items[0]["status"] = "closed"
            if name in ("nonhex_payload", "nonstring_payload", "n0_nonhex", "n0_nonstring"):
                items[7]["p"] = 42 if "nonstring" in name else "not-hex"
                if name.startswith("n0_"):
                    items[7]["n"] = 0
            if name == "missing_payload":
                items[7].pop("p")
            if name == "whitespace_hex":
                for batch in items[1:-1]:
                    batch["p"] = " ".join(batch["p"][i:i + 2] for i in range(0, len(batch["p"]), 2))
            if name == "dup_poll":
                items.insert(8, copy.deepcopy(items[7]))
            if name == "dup_rx_diff_payload":
                for key in ("rx", "tx"):
                    items[8][key] = items[7][key]
            if name == "smc_with_p_key":
                batch = items[7]
                items[7] = {"k": "b", "tx": batch["tx"], "rx": batch["rx"], "n": batch["n"],
                            "smc": {"p": "ab", **batch["smc"]}, "p": batch["p"]}
            if name == "voltage_missing":
                for batch in items[1:-1:3]:
                    batch["smc"].pop("B0AV")
            if name in ("edge_poll_start", "edge_poll_end"):
                for batch in items[1:-1]:
                    batch["smc"]["B0AC"] = 0
                items[8 if name == "edge_poll_start" else 12]["smc"]["B0AC"] = -1000
            if name == "reversed_polls":
                items[1:-1] = reversed(items[1:-1])
            if name.startswith("dropped_"):
                edge = {"dropped_edge_sample": 8, "dropped_start_sample": 4,
                        "dropped_idle_end_sample": 2}[name] * 1_000_000_000
                batch = next(b for b in items if b.get("k") == "b" and b["rx"] == edge)
                raw = bytes.fromhex(batch["p"])
                words = [raw[k:k + kp.SAMPLE.size] for k in range(0, len(raw), kp.SAMPLE.size)]
                words = [word for word in words if kp.SAMPLE.unpack(word)[0] != edge // 1_000_000]
                batch.update(n=len(words), p=b"".join(words).hex())
            if name in ("wrap", "long_stall"):
                for i, batch in enumerate(items[1:-1]):
                    shift = 65000 if name == "wrap" else (70000 if i >= 7 else 0)
                    batch["p"] = kp.SAMPLE.pack((i * 1000 + shift) % kp.WRAP, 0,
                                                12_000_000, 1_000_000, 0, 0, 0, 0).hex()
                    if name == "long_stall" and i >= 7:
                        batch["rx"] += 70_000_000_000
                        batch["tx"] += 70_000_000_000
            cases[name] = items
        return cases

    def test_review_shapes_native_samples_fit_and_marker_inputs(self):
        for name, items in self.shape_cases().items():
            with self.subTest(shape=name):
                self.write(items)
                # Full selection observes every native kept sample. The join
                # below independently exercises the actual decode/idle spans.
                primary = ba._filtered_stream(self.path, [(-10**15, 10**15)])
                twin = bt.parse_meter_stream(self.path)
                try:
                    native = kp.parse(self.path)
                except (ValueError, TypeError, struct.error):
                    self.assertIsNone(primary.fit)
                    self.assertIsNone(primary.samples)
                    self.assertFalse(twin["aligned"])
                else:
                    if native.fit is not None:
                        cold_fit = {"tail_word_replayed": (12, -82191780.82191849, 968036.5296803653),
                                    "first_batch_tail_replayed": (13, 17440170.526111603, 1008623.1954267997)}
                        if name in cold_fit:
                            self.assertEqual((native.fit.stats["points"], native.fit.a_ns,
                                              native.fit.b_ns_per_ms), cold_fit[name])
                        self.assertEqual(primary.fit, native.fit)
                        self.assertEqual(primary.samples, native.samples)
                        self.assertEqual(primary.host_ns, native.host_ns)
                        self.assertEqual(primary.watts, native.watts)
                        self.assertEqual(twin["host_ns"], native.host_ns)
                        self.assertEqual(twin["watts"], native.watts)
                        for key in ("a_ns", "b_ns_per_ms"):
                            self.assertEqual(twin["fit"][key], getattr(native.fit, key))
                        for key in ("points", "points_used", "clock_rate_ppm", "excess_latency_ms_p50",
                                    "excess_latency_ms_p95", "excess_latency_ms_min", "excess_latency_ms_max"):
                            self.assertEqual(twin["fit"][key], native.fit.stats[key])
                    else:
                        self.assertIsNone(primary.fit)
                        self.assertFalse(twin["aligned"])
                # Native parse intentionally has no polls on a closed header,
                # and raises on bad sample words. Ruling F2 keeps load()'s
                # polls as the independent marker oracle in both cases.
                header, trailer, batches, errors = kp.load(self.path)
                polls = sorted(batches, key=lambda b: b["rx"])
                marker = kp.Stream(header, trailer, polls, errors, None, None, [], [],
                                   [b["rx"] for b in polls], [dict(b.get("smc") or {}) for b in polls])
                self.assertEqual(primary.poll_ns, marker.poll_ns)
                self.assertEqual(primary.smc, marker.smc)
                self.assertEqual(twin["poll_ns"], marker.poll_ns)
                self.assertEqual(twin["battery_current_ma"], [b.get("B0AC") for b in marker.smc])
                self.assertEqual(twin["battery_voltage_mv"], [b.get("B0AV") for b in marker.smc])
                tau = ba._battery_delay_ns(marker)
                self.assertEqual(ba._battery_delay_ns(primary), tau)
                self.assertEqual(twin["battery_tau_ns"], tau)
                self.assertEqual(ba._decode_battery_marker(primary, self.spans["decode_ns"], tau),
                                 ba._decode_battery_marker(marker, self.spans["decode_ns"], tau))
                self.assert_agreement()

    def test_crlf_stream_keeps_native_samples_and_markers(self):
        self.write(self.items())
        self.path.write_bytes(self.path.read_bytes().replace(b"\n", b"\r\n"))
        native = kp.parse(self.path)
        primary, twin, actual = self.assert_agreement()
        self.assertEqual(primary[0][1].fit, native.fit)
        self.assertEqual(twin["streams"][0]["host_ns"], native.host_ns)
        self.assertEqual(actual["status"], "ok")

    def test_partial_words_keep_polls_and_marker_without_energy(self):
        for name, items in self.shape_cases().items():
            if "partial" not in name or name.endswith("n0"):
                continue
            with self.subTest(shape=name):
                self.write(items)
                primary, twin, actual = self.assert_agreement()
                self.assertIsNone(primary[0][1].fit)
                self.assertFalse(twin["streams"][0]["aligned"])
                self.assertEqual(primary[0][1].poll_ns, [b["rx"] for b in items if b["k"] == "b"])
                self.assertIs(actual.get("decode_assisted"), True)
                self.assertIs(actual.get("battery_end_window_complete"), True)
                self.assertNotEqual(actual["status"], "ok")

    def test_dropped_edge_samples_refuse_dc_only_when_missing_counter_is_in_decode(self):
        for name, items in self.shape_cases().items():
            if not name.startswith("dropped_"):
                continue
            with self.subTest(shape=name):
                self.write(items)
                native = kp.parse(self.path)
                primary, _, result = self.assert_agreement()
                window = [t + kp.raw_offset_ns(native) for t in self.spans["decode_ns"]]
                if kp.span_has_drops(native, *window):
                    for stream in (native, primary[0][1]):
                        with self.assertRaises(ba.MeterGapError):
                            ba.meter_decode(stream, self.spans["decode_ns"], self.spans["idle_ns"])
                    self.assertEqual(result["status"], "meter_gap")
                    self.assertEqual(result["flags"], ["bytes.meter_gap"])
                    continue
                expected = ba.meter_decode(native, self.spans["decode_ns"], self.spans["idle_ns"])
                self.assertEqual(ba.meter_decode(primary[0][1], self.spans["decode_ns"], self.spans["idle_ns"]), expected)
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["edge_powers_w"], expected["edge_powers_w"])
                self.assertEqual(result["n"], expected["n"])

    def test_smc_with_p_key_uses_the_native_top_level_payload(self):
        items = self.items()
        batch = items[7]
        items[7] = {"k": "b", "tx": batch["tx"], "rx": batch["rx"], "n": batch["n"],
                    "smc": {"p": "ab", **batch["smc"]}, "p": batch["p"]}
        self.write(items)
        native = kp.parse(self.path)
        primary, twin, _ = self.assert_agreement()
        self.assertEqual(primary[0][1].fit.stats, native.fit.stats)
        self.assertEqual(twin["streams"][0]["host_ns"], native.host_ns)
        native_power = dict(zip(native.host_ns, native.watts))
        self.assertEqual(primary[0][1].watts, [native_power[t] for t in primary[0][1].host_ns])

    def test_parser_early_returns_preserve_mapped_polls(self):
        for case in ("streaming", "header_closed", "polls_only", "one_batch", "duplicate_sequences",
                     "missing_payload", "nonhex_payload", "no_header", "no_trailer", "no_polls", "implicit_streaming",
                     "offset_at_limit", "offset_drift"):
            with self.subTest(path=case):
                items = self.items()
                if case == "header_closed":
                    items[0].update(status="closed", rate_idx=99)  # rate is irrelevant without a fit
                if case == "implicit_streaming":
                    items[0].pop("status")
                if case in ("polls_only", "one_batch"):
                    for i, item in enumerate(items[1:-1]):
                        if case == "polls_only" or i != 0:
                            item.update(n=0, p="")
                if case == "duplicate_sequences":
                    for item in items[1:-1]:
                        item["p"] = items[1]["p"]
                if case == "missing_payload":
                    for item in items[1:-1]:
                        item.pop("p")
                if case == "nonhex_payload":
                    for item in items[1:-1]:
                        item["p"] = "not-hex"
                if case == "no_header":
                    items = items[1:]
                if case == "no_trailer":
                    items = items[:-1]
                if case == "no_polls":
                    items = [items[0], items[-1]]
                if case in ("offset_at_limit", "offset_drift"):
                    items[-1]["end_raw_ns"] += 1_000_000 + (case == "offset_drift")
                self.write(items)
                primary, twin, _ = self.assert_agreement()
                stream = twin["streams"][0]
                self.assertEqual(stream["poll_ns"], primary[0][1].poll_ns)
                self.assertEqual(stream["raw_offset_ns"], kp.raw_offset_ns(primary[0][1]))
                self.assertEqual(stream["battery_tau_ns"], 3_000_000_000 if stream["poll_ns"] else 2_000_000_000)
                if case in ("header_closed", "polls_only", "one_batch", "duplicate_sequences", "missing_payload", "nonhex_payload"):
                    self.assertFalse(stream["aligned"])
                    self.assertEqual(stream["battery_current_ma"][9], -1000)
                    self.assertEqual(stream["battery_voltage_mv"][9], 12000)

    def test_transport_failures_discard_the_stream_like_the_primary(self):
        for case in ("invalid_json", "blank_line", "missing_rx", "missing_rate"):
            with self.subTest(path=case):
                items = self.items()
                if case == "missing_rx":
                    items[1].pop("rx")
                if case == "missing_rate":
                    items[0].pop("rate_idx")
                self.write(items)
                if case in ("invalid_json", "blank_line"):
                    with self.path.open("a") as handle:
                        handle.write("{broken\n" if case == "invalid_json" else "\n")
                primary, twin, actual = self.assert_agreement()
                self.assertIsNone(actual.get("decode_assisted"))
                self.assertEqual(primary[0][1].poll_ns, [])
                self.assertEqual(twin["streams"][0]["poll_ns"], [])

    def test_missing_canonical_stream_directory_does_not_read_a_fallback(self):
        self.write(self.items())
        fallback = self.root / "hazards/meter"
        fallback.parent.mkdir(parents=True)
        self.directory.rename(fallback)
        self.assert_agreement()
        self.assertEqual(bt.load_archive(self.root)["streams"], [])

    def test_unreadable_stream_has_no_marker_on_either_side(self):
        self.write(self.items())
        original_open = Path.open
        def unreadable_stream(path, *args, **kwargs):
            if path == self.path:
                raise OSError("unreadable stream")
            return original_open(path, *args, **kwargs)
        # #573 propagates custody read errors. Fail the intended meter stream,
        # while absent acceptance/roster files retain their missing-file path.
        with mock.patch.object(Path, "open", unreadable_stream):
            self.assert_agreement()

    def test_non_object_transport_has_the_primarys_parse_failure(self):
        self.write(self.items())
        with self.path.open("a") as handle:
            handle.write("[]\n")
        with self.assertRaises(AttributeError):
            ba._session_streams(self.root, list(self.spans.values()))
        with self.assertRaises(AttributeError):
            bt.load_archive(self.root)

    def test_clock_fit_failure_and_envelope_fallback_preserve_marker(self):
        self.write(self.items())
        with mock.patch.object(kp, "clock_fit", side_effect=ValueError("fit failed")), mock.patch.object(
                bt, "_linear_fit", side_effect=ValueError("fit failed")):
            _, _, result = self.assert_agreement()
            self.assertIs(result["decode_assisted"], True)
        def fail_second(original):
            calls = 0
            def fit(*args):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise ValueError("envelope fit failed")
                return original(*args)
            return fit
        with mock.patch.object(kp, "_linear_fit", side_effect=fail_second(kp._linear_fit)), mock.patch.object(
                bt, "_linear_fit", side_effect=fail_second(bt._linear_fit)):
            _, _, result = self.assert_agreement()
            self.assertEqual(result["status"], "ok")
            self.assertIs(result["decode_assisted"], True)

    def test_energy_join_skip_paths_keep_the_marker(self):
        for case in ("late_start", "end_in_decode", "idle_outside", "decode_samples_missing", "idle_samples_missing",
                     "decode_voltage_missing", "idle_voltage_missing", "all_voltage_missing",
                     "quiet_marker", "no_marker_polls"):
            with self.subTest(path=case):
                items = self.items()
                if case == "late_start":
                    items = [b for b in items if b["k"] != "b" or b["rx"] >= 6_000_000_000]
                if case == "end_in_decode":
                    items = [b for b in items if b["k"] != "b" or b["rx"] <= 7_000_000_000]
                if case == "no_marker_polls":
                    items = [b for b in items if b["k"] != "b" or b["rx"] <= 6_000_000_000]
                if case == "idle_outside":
                    self.spans["idle_ns"] = [-2_000_000_000, -1_000_000_000]
                else:
                    self.spans["idle_ns"] = [0, 2_000_000_000]
                if case == "idle_samples_missing":
                    self.spans["idle_ns"] = [1_000_000_000, 2_000_000_000]
                for b in items[1:-1]:
                    if case == "decode_samples_missing" and 4_000_000_000 <= b["rx"] < 8_000_000_000:
                        b.update(n=0, p="")
                    if case == "idle_samples_missing" and b["rx"] == 1_000_000_000:
                        b.update(n=0, p="")
                    if (case == "all_voltage_missing" or
                        case == "decode_voltage_missing" and 4_000_000_000 <= b["rx"] < 8_000_000_000 or
                        case == "idle_voltage_missing" and b["rx"] < 2_000_000_000):
                        b["smc"].pop("B0AV")
                    if case == "quiet_marker":
                        b["smc"]["B0AC"] = 0
                self.write(items)
                self.assert_agreement()

    def test_successful_join_uses_its_stream_before_marker_only_fallbacks(self):
        self.write(self.items())
        assisted = self.path.read_text()
        quiet = self.items()
        for b in quiet[1:-1]:
            b["smc"]["B0AC"] = 0
        self.write(quiet)
        second = self.directory / "stream-002.jsonl"
        second.write_text(assisted)
        _, _, result = self.assert_agreement()
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["decode_assisted"])
        # A prior unaligned assisted stream also yields to the successful join.
        assisted_items = self.items()
        assisted_items[0]["status"] = "closed"
        self.write(assisted_items)
        second.write_text("".join(json.dumps(b) + "\n" for b in quiet))
        _, _, result = self.assert_agreement()
        self.assertEqual(result["stream"], "stream-002.jsonl")
        self.assertFalse(result["decode_assisted"])

    def test_marker_only_streams_are_combined_in_both_orders(self):
        quiet = self.items()
        quiet[0]["status"] = "closed"
        for b in quiet[1:-1]:
            b["smc"]["B0AC"] = 0
        assisted = self.items()
        for b in assisted[1:-1]:
            b.update(n=0, p="")
        for first, second in ((quiet, assisted), (assisted, quiet)):
            with self.subTest(assisted_first=first is assisted):
                self.write(first)
                (self.directory / "stream-002.jsonl").write_text("".join(json.dumps(b) + "\n" for b in second))
                _, _, result = self.assert_agreement()
                self.assertIs(result["decode_assisted"], True)


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
