#!/usr/bin/env python3
"""Independent, non-issuing block-5 arithmetic from archived raw records.

Only the Python standard library is used. Selection, anchors, timing bounds and
calibration fits are input judgments; energy and all reported statistics are
computed here. See the build SPEC for the dependency and comparison contract.

Agreement policy (FIX-571 lead ruling): copies of the same stored number,
integer-ns clocks, and plist/CSV records from the same samples compare exactly.
Plist/CSV timestamps resolve one ulp of the epoch double (about 238 ns at
2^30 s: 2^(30-52) s), the CSV's own float-seconds resolution.
Otherwise use a bar above 1e6 times double noise (2.2e-10 relative) and below
1% of the smallest printed uncertainty, when available; without a printed
uncertainty use 1e-6 relative (1e-6 column units near zero for J/W). Rho uses
1e-6 absolute, 1% of its four-decimal resolution. Positive b_op seconds use
only the relative bar. These are agreement checks, never acceptance gates.
"""
import argparse
import bisect
import csv
import datetime
import functools
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import plistlib
import re
import statistics
import struct
import sys
from xml.parsers.expat import ExpatError

SCHEMA = "joulewise.independent_recompute_b5.v1"
POSITIONS = ("a1", "b1", "b2", "a2")
MODELS = {"ALPHA": "Qwen3-1.7B-4bit", "BETA": "Qwen3-8B-4bit"}
SIDE_MODELS = {"a": MODELS["ALPHA"], "b": MODELS["BETA"]}
LOAD_CODES = {"thermal.os_level_nonzero", "thermal.powermetrics_pressure_elevated",
              "contention.request_overlap"}
FLAG_CODES = frozenset("""archive_file_missing trace_csv_plist_mismatch trace_plist_missing trace_plist_unreadable
anchor_label_inconsistent phase_events_ambiguous kept_member_unusable
kept_member_phase_under_3_records kept_member_token_mismatch kept_unit_identity_mismatch
unit_shape_invalid kept_units_disagree claim_usable_false cell_below_minimum b_op_mismatch
b_op_from_record bracket_drift_over_budget member_pre_bound_mismatch stored_energy_mismatch
stored_envelope_mismatch interpolation_bound_nonzero neg8_allowance_mismatch
neg8_allowance_unrecorded neg8_survivor_count_mismatch unknown_auxiliary_member
gamma_midpoint_lost_on_analysed_attempt dominance_ratio_zero_denominator nonfinite_value
pack_missing calibration_capture_name_fallback excluded_reference_in_screen
kept_member_outside_verdict_membership neg8_source_not_rescreen harvest_checkout_not_clean
reference_slot_disagrees roster_pack_not_archived roster_plan_tree_not_sealed
loo_kept_n_equals_minimum sensitivity_inputs_unavailable meter_stream_malformed
meter_no_fit meter_span_uncovered meter_offset_from_journal meter_offset_unavailable
meter_battery_unavailable meter_request_mismatch meter_baseline_unavailable
member_pre_bound_missing meter_battery_activity meter_absent
exclusions_rederivation_mismatch exclusions_rederivation_unavailable""".split())
TRACE_STOP_FLAG_CODES = frozenset({"trace_plist_missing", "trace_plist_unreadable"})
STOP_FLAG_CODES = TRACE_STOP_FLAG_CODES | frozenset({"excluded_reference_in_screen", "kept_member_outside_verdict_membership",
                            "neg8_source_not_rescreen", "harvest_checkout_not_clean",
                            "reference_slot_disagrees", "roster_pack_not_archived",
                            "roster_plan_tree_not_sealed", "kept_units_disagree",
                            "exclusions_rederivation_mismatch"})
# Only these codes reach stdout/stderr; every other code, and every value, stays in the restricted output file.
STRUCTURE_FLAG_CODES = STOP_FLAG_CODES | {"loo_kept_n_equals_minimum", "calibration_capture_name_fallback",
                                          "exclusions_rederivation_unavailable"}
CATALOG_PATH = Path(__file__).resolve().parents[1] / "configs/campaigns/v5_claim_25g83/flag_catalog.json"
# Orchestrator ruling Q11 (2026-10-07): on GAMMA only, this DISCLOSE code also removes the window.
GAMMA_PACK_ID = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
GAMMA_WINDOW_REASONS = {"neg8.midpoint_lost": "neg8.midpoint_lost_primary"}
MACHINE_BOUNDARY = ("whole-machine DC input plus the battery term, measured at the USB-C input; "
                    "the adapter's AC-to-DC loss is not included.")
PHASE_MACHINE_LABEL = "descriptive: gross meter energy per phase; battery assist flagged at request level"
PHASE_MACHINE_BOUNDARY = ("whole-machine gross DC input, measured at the USB-C input; "
                          "battery energy and the adapter's AC-to-DC loss are not included.")
RECONSTRUCTION_LABEL = "diagnostic: single-step reconstruction (F5); replaces nothing"
SCALED_ALLOWANCE_LABEL = ("sensitivity: drift allowance scaled by max(1, E/E_ref, T/T_ref); "
                          "the registered result is unchanged")
BETA_INCLUSIVE_LABEL = ("including three BETA sessions removed by rules later rewritten; above 16 units "
                        "the pooled floor is an upper bound on the registered arithmetic, never smaller")
RESTORE_TOOL_DETAIL = {
    "restore_tool": "scripts/restore_run_to_scratch.py",
}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def agrees(actual, expected, *, ratio=False):
    """Agreement for unrounded quantities without a cell's printed half-width."""
    if not all(finite(v) for v in (actual, expected)):
        return False
    # Agreement policy above: 1e-6 relative, 1e-6 column units near zero; both exceed
    # 1e6 x double noise (2.2e-16 = 2.2e-10 relative). Rho's 1e-6 absolute
    # is 1% of its four-decimal printed resolution, 1e-4.
    bar = 1e-6 if ratio else max(1e-6, 1e-6 * abs(expected))
    return abs(actual - expected) <= bar


def get(obj, *keys, default=None):
    for key in keys:
        if not isinstance(obj, dict) or key not in obj:
            return default
        obj = obj[key]
    return obj


def objects(value):
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def strings(value):
    return [x for x in value if isinstance(x, str)] if isinstance(value, list) else []


def mapping(value):
    return value if isinstance(value, dict) else {}


def positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def beta_fraction(a, b, x):
    """Lentz continued fraction for the regularized incomplete beta."""
    # Lentz denominator underflow guard, far below any printed digit; not an agreement bar.
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1 / d
    h = d
    for m in range(1, 10001):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        c = 1 + aa / c
        if abs(d) < tiny:
            d = tiny
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        c = 1 + aa / c
        if abs(d) < tiny:
            d = tiny
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        # Continued-fraction convergence near 9 double epsilons; far below printed precision.
        if abs(delta - 1) <= 2e-15:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def regularized_beta(x, a, b):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * beta_fraction(a, b, x) / a
    return 1 - front * beta_fraction(b, a, 1 - x) / b


def student_p(t, df):
    """Two-sided tail computed directly, avoiding 1-CDF cancellation."""
    if df < 1:
        raise ValueError("positive degrees of freedom required")
    if math.isinf(t):
        return 0.0
    return min(1.0, max(0.0, regularized_beta(df / (df + t * t), df / 2, 0.5)))


def student_cdf(t, df):
    tail = student_p(t, df) / 2
    return 1 - tail if t >= 0 else tail


@functools.lru_cache(maxsize=None)
def student_quantile(df, probability=0.975):
    if df < 1 or not 0 < probability < 1:
        raise ValueError("invalid quantile arguments")
    if probability < 0.5:
        return -student_quantile(df, 1 - probability)
    if probability == 0.5:
        return 0.0
    lo, hi = 0.0, 1.0
    target = 2 * (1 - probability)
    while student_p(hi, df) > target:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        # Root-bracket stop at double resolution, far below any printed t digit.
        if mid == lo or mid == hi or hi - lo <= 1e-15:
            break
        if student_p(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def overlap(records, x, y):
    """Registered left-to-right overlap sum; no interpolation or idle removal."""
    total, count = 0.0, 0
    for start, end, power in records:
        length = max(0.0, min(y, end) - max(x, start))
        total += power * length
        if length > 0:
            count += 1
    return total, count


def shift_envelope(records, onset, offset, b, span, clock):
    g = b + span
    point = overlap(records, onset, offset)[0]
    boundaries = sorted({x for start, end, _ in records for x in (start, end)})
    lower, upper = point, point
    for e_on, e_off in itertools.product((-g, g), repeat=2):
        shifts = {-clock, clock}
        for edge in (onset + e_on, offset + e_off):
            # Search all breakpoints inside the allowed common-shift interval.
            left = bisect.bisect_left(boundaries, edge - clock)
            right = bisect.bisect_right(boundaries, edge + clock)
            shifts.update(x - edge for x in boundaries[left:right]
                          if -clock <= x - edge <= clock)
        for shift in sorted(shifts):
            energy = overlap(records, onset + e_on + shift, offset + e_off + shift)[0]
            lower, upper = min(lower, energy), max(upper, energy)
    return {"point_j": point, "lower_j": lower, "upper_j": upper,
            "max_abs_delta_j": max(point - lower, upper - point)}


def ordinal(run_id):
    match = re.search(r"-r(\d+)$", run_id)
    if match:
        return int(match[1])
    match = re.search(r"-b(\d+)-(a1|b1|b2|a2)$", run_id)
    if match:
        return 10 + 4 * (int(match[1]) - 1) + POSITIONS.index(match[2]) + 1
    return 1000000


def unit_order(unit_id):
    match = re.search(r"-(?:r|b)(\d+)$", unit_id)
    return (int(match[1]) if match else 1000000, unit_id)


def role(run_id):
    if re.fullmatch(r"neg8-refcorpus-r\d+", run_id):
        return "corpus"
    for endpoint in ("start", "end"):
        if re.fullmatch(r"neg8-window-" + endpoint + r"-(?:r\d+|spare-\d+)", run_id):
            return endpoint
    if run_id in ("neg8-window-midpoint", "neg8-window-midpoint-spare-1"):
        return "midpoint"
    if run_id.startswith("gamma-interior-reference-"):
        return "diagnostic"
    return "unknown"


class Reader:
    """Read accounting and deterministic, path-free problem records."""
    def __init__(self, pack, flags):
        self.pack, self.flags = pack, flags
        self.files = set()

    def flag(self, code, scope, detail):
        assert code in FLAG_CODES, code
        row = {"code": code, "pack": self.pack, "scope": str(scope), "detail": detail}
        if row not in self.flags:
            self.flags.append(row)

    def raw(self, path, scope, required=True):
        try:
            data = path.read_bytes()
            self.files.add(str(path))
            return data
        except OSError:
            if required:
                self.flag("archive_file_missing", scope, "missing or unreadable")
            return None

    def json(self, path, scope, required=True):
        data = self.raw(path, scope, required)
        if data is None:
            return {}
        try:
            result = json.loads(data)
            if not isinstance(result, dict):
                raise ValueError("not an object")
            return result
        except (ValueError, UnicodeError):
            self.flag("archive_file_missing", scope, "malformed JSON object")
            return {}

    def lines(self, path, scope):
        data = self.raw(path, scope)
        if data is None:
            return []
        rows = []
        try:
            for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("not an object")
                    rows.append(row)
                except ValueError:
                    self.flag("archive_file_missing", scope, {"malformed_line": number})
        except UnicodeError:
            self.flag("archive_file_missing", scope, "invalid UTF-8")
        return rows


def csv_records(data):
    records = []
    rails = []
    for row in csv.DictReader(data.decode("utf-8").splitlines()):
        start, end, power = (float(row[k]) for k in
                             ("interval_start_s", "interval_end_s", "power_w"))
        if not all(finite(x) for x in (start, end, power)) or end <= start or power < 0:
            raise ValueError("invalid CSV record")
        if records and (start, end) == records[-1][:2]:
            old = records[-1]
            records[-1] = (start, end, old[2] + power)
            rails[-1].append(row["rail"])
        else:
            records.append((start, end, power))
            rails.append([row["rail"]])
    if not records or any(set(r) != {"cpu_power", "gpu_power", "ane_power"} or len(r) != 3 for r in rails):
        raise ValueError("CSV requires three distinct rails per record")
    return records


def plist_records(data, anchor, reader=None, scope=""):
    records, cumulative = [], 0.0
    for frame in data.split(b"\x00"):
        if not frame.strip():
            continue
        doc = plistlib.loads(frame.strip())
        if not isinstance(doc, dict) or not positive_int(doc.get("elapsed_ns")):
            raise ValueError("positive integer elapsed_ns required")
        length = doc["elapsed_ns"] / 1_000_000_000.0
        if records:
            cumulative += length
        end = anchor + cumulative
        start = end - length
        processor = doc["processor"]
        power = (processor["cpu_power"] / 1000.0 + processor["gpu_power"] / 1000.0
                 + processor["ane_power"] / 1000.0)
        if not all(finite(x) for x in (start, end, power, length)) or end <= start or power < 0:
            raise ValueError("invalid plist record")
        records.append((start, end, power))
        label = doc["timestamp"].replace(tzinfo=datetime.timezone.utc).timestamp()
        # D-078 label sanity: 250 us affine residual + 50 ppm elapsed drift
        # + 1 us numeric padding (four epoch double ulps <954 ns). Whole-second
        # plist labels span [end-1, end]; this is not an agreement bar.
        pad = 0.00025 + 50e-6 * (end - anchor) + 1e-6
        if reader and not -pad <= end - label <= 1 + pad:
            reader.flag("anchor_label_inconsistent", scope,
                        {"record": len(records) - 1, "end_minus_label_s": end - label})
    if not records:
        raise ValueError("empty plist stream")
    return records


class Member:
    def __init__(self, path, run_id, reader, bop, member_role="science"):
        self.run_id, self.role = run_id, member_role
        self.path = path
        self.reader = reader
        self.metadata = reader.json(path / "metadata.json", run_id + "/metadata.json")
        self.summary = reader.json(path / "summary_metrics.json", run_id + "/summary_metrics.json")
        self.events = reader.lines(path / "events.jsonl", run_id + "/events.jsonl")
        self.model = get(self.metadata, "model", "name")
        anchor = mapping(get(self.metadata, "uncertainty_evidence", "clock_anchor"))
        self.bpre = get(self.metadata, "instrument_calibration", "b_fiducial_s")
        self.m = get(anchor, "effective_clock_anchor_bound_s")
        self.s = get(anchor, "wall_minus_monotonic_span_s")
        self.usable = (self.summary.get("status") == "succeeded" and anchor.get("status") == "bounded")
        self.records, self.edges, self.energies, self.counts = [], {}, {}, {}
        self.pre, self.op, self.residual = {}, {}, {}
        self.comparison = {"status": "not_compared", "reason": "independent_trace_unavailable"}
        self.config_tags = None
        if member_role == "science" and "sw-" in run_id:
            config = reader.json(path / "config.json", run_id + "/config.json")
            self.config_tags = get(config, "run_metadata", "tags", default=[])
        elif reader.pack == "GAMMA" and member_role == "science":
            config = reader.json(path / "config.json", run_id + "/config.json")
            self.config_tags = get(config, "run_metadata", "tags", default=[])
        endpoint = anchor.get("first_sample_end_point_epoch_s")
        raw = reader.raw(path / "raw/powermetrics.plist", run_id + "/raw/powermetrics.plist", False)
        trace = reader.raw(path / "power_trace.csv", run_id + "/power_trace.csv")
        csv_data = None
        if trace is not None:
            try:
                csv_data = csv_records(trace)
            except (ValueError, KeyError, TypeError, UnicodeError, csv.Error):
                reader.flag("archive_file_missing", run_id + "/power_trace.csv", "malformed trace")
        placed = None
        if raw is None:
            compressed = path / "raw/powermetrics.plist.zst"
            is_compressed = compressed.is_file()
            self.comparison = {"status": "not_compared", "reason": "trace_plist_missing",
                               "input": "raw/powermetrics.plist",
                               "input_status": "compressed" if is_compressed else "missing_or_unreadable"}
            if is_compressed:
                self.comparison.update(compressed_input="raw/powermetrics.plist.zst",
                                       **RESTORE_TOOL_DETAIL)
            reader.flag("trace_plist_missing", run_id, self.comparison.copy())
        elif finite(endpoint):
            try:
                placed = plist_records(raw, endpoint, reader, run_id)
            except (ValueError, KeyError, TypeError, OverflowError, AttributeError, ExpatError):
                self.comparison = {"status": "not_compared", "reason": "trace_plist_unreadable",
                                   "input": "raw/powermetrics.plist", "input_status": "malformed"}
                reader.flag("trace_plist_unreadable", run_id, self.comparison.copy())
        else:
            reader.flag("kept_member_unusable", run_id, "record placement anchor missing or nonfinite")
            self.comparison["reason"] = "anchor_unbounded"
        if placed and csv_data:
            # Same capture code, samples, placement arithmetic and rail sum:
            # copy identity is the property, with no epoch-scaled tolerance.
            # Timestamp resolution is one epoch-double ulp, the CSV's own
            # float-seconds resolution (2^(30-52) s, about 238 ns at 2^30 s).
            if placed != csv_data:
                reader.flag("trace_csv_plist_mismatch", run_id, "plist is primary")
        if not placed:
            self.usable = False
        elif self.usable:
            origin = placed[0][0]
            self.origin = origin
            self.records = [(a - origin, b - origin, p) for a, b, p in placed]
            for phase, start_type, end_type in (("prefill", "phase_start", "phase_end"),
                                               ("decode", "phase_start", "phase_end"),
                                               ("request", "sampling_started", "sampling_stopped")):
                event_phase = "measured_run" if phase == "request" else phase
                starts = [e.get("timestamp_s") for e in self.events
                          if e.get("phase") == event_phase and e.get("event_type") == start_type]
                ends = [e.get("timestamp_s") for e in self.events
                        if e.get("phase") == event_phase and e.get("event_type") == end_type]
                if len(starts) != 1 or len(ends) != 1 or not all(finite(x) for x in starts + ends) or ends[0] <= starts[0]:
                    reader.flag("phase_events_ambiguous", run_id + "/" + phase, "need one ordered start/end pair")
                    continue
                onset, offset = starts[0] - origin, ends[0] - origin
                self.edges[phase] = (onset, offset)
                self.energies[phase], self.counts[phase] = overlap(self.records, onset, offset)
                if not finite(self.energies[phase]):
                    reader.flag("nonfinite_value", run_id + "/" + phase, "overlap energy nonfinite")
                    del self.energies[phase]
                    continue
                if all(finite(x) and x >= 0 for x in (self.m, self.s)):
                    for b, target in ((self.bpre, self.pre), (bop, self.op), (0.0, self.residual)):
                        if finite(b) and b >= 0 and finite(b + self.s):
                            target[phase] = shift_envelope(self.records, onset, offset, b, self.s, self.m)
                stored = (self.summary.get("gross_energy_j") if phase == "request" else
                          get(self.summary, "phase_energy_j", phase))
                # Unrounded stored joules: the agreement policy's 1e-6 relative / absolute near zero.
                if finite(stored) and not agrees(self.energies[phase], stored):
                    reader.flag("stored_energy_mismatch", run_id + "/" + phase,
                                {"own_j": self.energies[phase], "stored_j": stored})
                envelope_key = "/gross_energy_j" if phase == "request" else "/phase_energy_j/" + phase
                stored_a = get(self.summary, "energy_anchor_shift_envelopes", envelope_key, "max_abs_delta_j")
                # Same unrounded-joule agreement bar for the stored allowance.
                if phase in self.pre and finite(stored_a) and not agrees(self.pre[phase]["max_abs_delta_j"], stored_a):
                    reader.flag("stored_envelope_mismatch", run_id + "/" + phase,
                                {"own_j": self.pre[phase]["max_abs_delta_j"], "stored_j": stored_a})
        if placed:
            if not self.usable:
                reason = "anchor_unbounded" if anchor.get("status") != "bounded" else "status_not_succeeded"
                self.comparison = {"status": "not_compared", "reason": reason}
            elif self.energies:
                self.comparison = {"status": "compared", "reason": None}
            else:
                self.comparison = {"status": "not_compared", "reason": "phase_events_ambiguous"}
        self.tokens = self.token_surfaces()

    def token_surfaces(self):
        output = get(self.metadata, "workload_observed", "output_token_count")
        total = get(self.metadata, "workload_observed", "token_count")
        surfaces = [get(self.metadata, "workload_provenance", "prompt", "realized_token_count")]
        for phase, event_type in (("tokenize", "phase_end"), ("prefill", "phase_start")):
            surfaces.extend(get(e, "metadata", "prompt_tokens") for e in self.events
                            if e.get("phase") == phase and e.get("event_type") == event_type)
            if not any(e.get("phase") == phase and e.get("event_type") == event_type for e in self.events):
                surfaces.append(None)
        surfaces.append(total - output if positive_int(total) and positive_int(output) else None)
        prompt = surfaces[0] if all(positive_int(x) and x == surfaces[0] for x in surfaces) else None
        return {"decode": output if positive_int(output) and output == 512 else None,
                "prefill": prompt if prompt == 2048 else None, "prompt_surfaces": surfaces}

    def detail(self):
        stored_a = {}
        for phase in ("prefill", "decode", "request"):
            key = "/gross_energy_j" if phase == "request" else "/phase_energy_j/" + phase
            stored_a[phase] = get(self.summary, "energy_anchor_shift_envelopes", key, "max_abs_delta_j")
        return {"model": self.model, "role": self.role, "comparison": self.comparison,
                "E_j": self.energies, "n_overlap": self.counts,
                "a_bop_j": {k: v["max_abs_delta_j"] for k, v in self.op.items()},
                "a_bpre_j": {k: v["max_abs_delta_j"] for k, v in self.pre.items()},
                "stored_E_j": {**mapping(get(self.summary, "phase_energy_j")),
                               "request": self.summary.get("gross_energy_j")},
                "stored_max_abs_delta_j": stored_a,
                "r_j": {k: v["max_abs_delta_j"] for k, v in self.residual.items()},
                "m_s": self.m, "s_s": self.s, "tokens": self.tokens}


def catalog_effect(catalog, code):
    entry = mapping(get(catalog, "codes", code))
    return entry.get("effect", "UNCLASSIFIED"), entry.get("family")


def interval_pair(value):
    if (isinstance(value, (list, tuple)) and len(value) == 2 and value[0] <= value[1]
            and all(isinstance(v, int) and not isinstance(v, bool) for v in value)):
        return int(value[0]), int(value[1])
    return None


def rederive_exclusions(flags, roster, spans, catalog, catalog_sha256):
    """AN-18 (partial): plan section 3.3's exclusion rule, re-derived from the flag
    rows, the harvest's roster and spans, and the registered catalog's effects.
    Reads only code, scope, interval and flag_id of a flag; never a value."""
    unknown = lambda a, b: a is None or b is None or str(a) == str(b)
    plan_id, attempt = roster.get("plan_id"), roster.get("attempt")
    window_only = GAMMA_WINDOW_REASONS if roster.get("pack_id") == GAMMA_PACK_ID else {}
    position = {m["run_id"]: i for i, m in enumerate(roster["members"])}
    if len(position) != len(roster["members"]):
        raise ValueError("duplicate roster run id")
    by_stage = {}
    for m in roster["members"]:
        if m.get("stage_id") is not None:
            by_stage.setdefault(m["stage_id"], []).append(m["run_id"])
    run_of_bundle = {}
    for b in roster.get("bundles") or ():
        if b["run_id"] in position:
            run_of_bundle.setdefault(str(b["bundle_id"]), b["run_id"])
    excluded, reasons, unclassified, seen, foreign, unmatched, unplaced = {}, set(), set(), set(), set(), set(), set()
    counts = {"by_code": {}, "by_family": {}, "by_effect": {}}
    bump = lambda table, key: counts[table].__setitem__(key, counts[table].get(key, 0) + 1)
    for flag in flags:
        if flag["flag_id"] in seen:
            continue
        seen.add(flag["flag_id"])
        code, scope = flag["code"], flag["scope"]
        if not (unknown(plan_id, scope["plan_id"]) and unknown(attempt, scope["attempt"])):
            foreign.add(flag["flag_id"])
            continue
        effect, family = catalog_effect(catalog, code)
        bump("by_code", code), bump("by_family", family or "UNCLASSIFIED"), bump("by_effect", effect)
        if effect == "DISCLOSE":
            if code in window_only:
                reasons.add(window_only[code])
            continue
        if effect == "EXCLUDE_WINDOW":
            reasons.add(code)
            continue
        if effect != "EXCLUDE_MEMBER":
            unclassified.add(code)
            continue
        level = scope["level"]
        if level == "member" or (level == "quad" and scope["run_id"] is not None):
            rid = scope["run_id"]
            if rid not in position:
                rid = run_of_bundle.get(str(scope.get("bundle_id"))) or run_of_bundle.get(str(rid)) or rid
            if rid in position:
                excluded.setdefault(rid, set()).add(code)
            else:
                unmatched.add(flag["flag_id"])
            continue
        targets = list(position)
        if level == "stage" and by_stage.get(scope["stage_id"]):
            targets = by_stage[scope["stage_id"]]
        elif level in ("stage", "quad"):
            unmatched.add(flag["flag_id"])
        interval = interval_pair(flag["interval"]["monotonic_ns"])
        for rid in targets:
            span = interval_pair(get(spans, rid, "monotonic_ns"))
            if interval is not None and span is None:
                unplaced.add(rid)
            if interval is None or span is None or (span[0] <= interval[1] and interval[0] <= span[1]):
                excluded.setdefault(rid, set()).add(code)
    ignored, ambiguous = [], []
    if roster.get("bundles") is not None:
        admitted, started = {}, roster.get("chain_started_monotonic_ns")
        for b in roster["bundles"]:
            created = b.get("created_monotonic_ns")
            why = ("roster.not_in_plan" if b["run_id"] not in position else
                   "roster.foreign_attempt" if not unknown(attempt, b.get("attempt")) else
                   "roster.creation_unplaced" if started is not None and created is None else
                   "roster.before_chain_started" if started is not None and created < started else None)
            if why:
                ignored.append({"bundle_id": str(b["bundle_id"]), "run_id": b["run_id"], "code": why})
            else:
                admitted.setdefault(b["run_id"], []).append(str(b["bundle_id"]))
        for rid in position:
            if len(admitted.get(rid, ())) != 1:
                excluded.setdefault(rid, set()).add("member.bytes_ambiguous" if admitted.get(rid) else "member.bytes_missing")
                if admitted.get(rid):
                    ambiguous.append(rid)
    units = {}
    for m in roster["members"]:
        for u in m.get("units") or ():
            units.setdefault((u["cell_id"], u["stratum"], str(u["unit_id"])), []).append(m["run_id"])
    specs = {c["cell_id"]: c for c in roster.get("cells") or ()}
    floor_n = get(catalog, "rules", "cell_unit_minimum", default=8)
    cells, unresolvable = [], False
    for cid in sorted(set(specs) | {k[0] for k in units}):
        spec = specs.get(cid, {})
        strata = sorted({k[1] for k in units if k[0] == cid} | set(spec.get("strata", ["quad"])))
        minimum = {s: max(int(spec["minimum"][s]), floor_n) if s in spec.get("minimum", {}) else floor_n for s in strata}
        planned, kept, dropped = {}, {}, []
        for s in strata:
            keys = sorted(k for k in units if k[0] == cid and k[1] == s)
            planned[s], kept[s] = len(keys), []
            for k in keys:
                codes = sorted(set().union(*(excluded.get(rid, set()) for rid in units[k])))
                if codes:
                    dropped.append({"stratum": s, "unit_id": k[2], "codes": codes, "run_ids": sorted(units[k]),
                                    "positions": sorted(position[rid] for rid in units[k])})
                else:
                    kept[s].append(k[2])
        resolvable = bool(strata) and all(len(kept[s]) >= minimum[s] for s in strata)
        target = bool(spec.get("target", True))
        unresolvable |= target and not resolvable
        cells.append({"cell_id": cid, "target": target, "planned": planned, "minimum": minimum,
                      "n_repeats": len(kept.get("repeat", [])), "n_quads": len(kept.get("quad", [])),
                      "n_kept": {s: len(kept[s]) for s in strata}, "kept_units": kept,
                      "dropped_units": sorted(dropped, key=lambda d: (d["stratum"], d["unit_id"])),
                      "resolvable": resolvable})
    if unresolvable:
        reasons.add("cell.below_minimum")
    members = sorted(({"run_id": rid, "position": position[rid], "codes": sorted(codes),
                       "families": sorted({catalog_effect(catalog, c)[1] or "UNCLASSIFIED" for c in codes})}
                      for rid, codes in excluded.items() if codes), key=lambda m: (m["position"], m["run_id"]))
    return {"schema_version": "joulewise.exclusions.v1", "catalog_sha256": catalog_sha256,
            "plan_id": plan_id, "attempt": attempt, "members_excluded": members,
            "bundles_ignored": sorted(ignored, key=lambda b: (b["bundle_id"], b["code"])),
            "duplicate_bundles": sorted(ambiguous), "cells": cells, "claim_usable": not reasons,
            "reasons": sorted(reasons), "unclassified": sorted(unclassified), "release_blocked": bool(unclassified),
            "flag_counts": {**{k: dict(sorted(v.items())) for k, v in counts.items()},
                            "foreign_scope": len(foreign), "unmatched_member": len(unmatched)},
            "span_unknown": sorted(unplaced)}


def neg8_bound(corpus, n_start, n_end):
    n = len(corpus)
    if n < 2 or not 0 < n_start <= n or not 0 < n_end <= n:
        return None
    ordered = sorted(corpus)
    upper = lambda j: statistics.fmean(ordered[-j:])
    lower = lambda j: statistics.fmean(ordered[:j])
    envelope = max(upper(n_start) - lower(n_end), upper(n_end) - lower(n_start))
    s = statistics.stdev(corpus)
    t = round(student_quantile(n - 1), 3)
    prediction = t * s * math.sqrt(1 / n_start + 1 / n_end)
    return {"t": t, "s_j": s, "bound_envelope_j": envelope,
            "bound_prediction_j": prediction, "bound_j": max(envelope, prediction)}


def drift_allowance(start, midpoint, end, bound):
    points = [start, end] + ([] if midpoint is None else [midpoint])
    spread = max(points) - min(points)
    return spread, max(spread, bound)


class Window:
    def __init__(self, pack, archive, flags, exclusions=None, claim_root=None, bound_root=None, diagnostic=False):
        self.pack, self.archive, self.diagnostic = pack, Path(archive), diagnostic
        self.reader = Reader(pack, flags)
        self.claim_root = Path(claim_root) if claim_root else self.archive / "sources/claim-runs"
        self.bound_root = Path(bound_root) if bound_root else self.archive / "sources/bound-runs"
        r = self.reader
        self.harvest = r.json(self.archive / "harvest.json", "harvest.json")
        self.roster = r.json(self.archive / "derived/roster.json", "derived/roster.json")
        for field in ("cells", "members"):
            if not isinstance(self.roster.get(field), list):
                r.flag("archive_file_missing", "derived/roster.json", {"invalid_list": field})
        self.exclusion_path = Path(exclusions) if exclusions else self.archive / "derived/exclusions.json"
        self.exclusions = r.json(self.exclusion_path, "derived/exclusions.json")
        for field in ("cells", "members_excluded"):
            if not isinstance(self.exclusions.get(field), list):
                r.flag("archive_file_missing", "derived/exclusions.json", {"invalid_list": field})
        if not isinstance(self.exclusions.get("claim_usable"), bool):
            r.flag("archive_file_missing", "derived/exclusions.json", "claim_usable must be boolean")
        exclusion_bytes = r.raw(self.exclusion_path, "derived/exclusions.json", False)
        self.exclusion_hash = hashlib.sha256(exclusion_bytes).hexdigest() if exclusion_bytes is not None else None
        self.exclusion_cells = {c["cell_id"]: c for c in objects(self.exclusions.get("cells"))
                                if isinstance(c.get("cell_id"), str)}
        self.excluded = {m["run_id"] for m in objects(self.exclusions.get("members_excluded"))
                         if isinstance(m.get("run_id"), str)}
        self.flag_rows = r.lines(self.archive / "derived/flags.jsonl", "derived/flags.jsonl")
        self.assist = {get(f, "scope", "run_id") for f in self.flag_rows if f.get("code") == "battery.assist"
                       and isinstance(get(f, "scope", "run_id"), str)}
        if self.exclusions.get("claim_usable") is not True:
            r.flag("claim_usable_false", "window", "exclusions claim_usable is false or absent")
        self.members = {}
        # Only kept units, surviving references and the selected corpus count
        # toward or can stop the primary comparison. Detail/disclosure loads do not add ids.
        self.compared_run_ids = set()
        self.verdict = r.json(self.claim_root / "whole-window-verdict.json", "whole-window-verdict.json")
        self.verdict_members = set(strings(self.verdict.get("bundle_ids")))
        self.reference_slots, self.plan_binding = self.read_reference_slots()
        checkout = mapping(self.harvest.get("harvest_checkout"))
        if (checkout.get("status_clean") is not True or checkout.get("status_lines") != 0
                or checkout.get("errors") != []):
            r.flag("harvest_checkout_not_clean", "window", "harvest checkout not recorded clean and error-free")
        self.units = {}
        for m in objects(self.roster.get("members")):
            if m.get("kind") != "science" or not isinstance(m.get("run_id"), str):
                continue
            for u in objects(m.get("units")):
                if not all(isinstance(u.get(k), str) for k in ("cell_id", "stratum", "unit_id")):
                    r.flag("unit_shape_invalid", "roster", "malformed unit identity")
                    continue
                key = (u["cell_id"], u["stratum"], u["unit_id"])
                self.units.setdefault(key, []).append(m["run_id"])
        self.b = self.calibration()
        self.neg8 = self.compute_neg8()
        self.exclusion_check = self.check_exclusions()

    def check_exclusions(self):
        """AN-18 (partial): derived/exclusions.json must equal the registered rule applied to
        derived/flags.jsonl and the harvest's withheld roster and spans."""
        r = self.reader
        inputs = r.json(self.archive / "withheld/exclusion-inputs.json", "withheld/exclusion-inputs.json", False)
        catalog_bytes = r.raw(CATALOG_PATH, "flag_catalog", False)
        if not inputs or catalog_bytes is None:
            reason = "exclusion_inputs_missing" if not inputs else "catalog_missing"
            r.flag("exclusions_rederivation_unavailable", "derived/exclusions.json", reason)
            return {"status": "not_computed", "reason": reason}
        try:
            catalog = json.loads(catalog_bytes)
            derived = rederive_exclusions(self.flag_rows, inputs["roster"], mapping(inputs.get("spans")), catalog,
                                          hashlib.sha256(catalog_bytes).hexdigest())
        except (KeyError, TypeError, ValueError, AttributeError):
            r.flag("exclusions_rederivation_unavailable", "derived/exclusions.json", "inputs_malformed")
            return {"status": "not_computed", "reason": "inputs_malformed"}
        differing = sorted(k for k in derived if self.exclusions.get(k) != derived[k])
        if differing:
            r.flag("exclusions_rederivation_mismatch", "derived/exclusions.json", {"keys": differing})
        stored = {m.get("run_id") for m in objects(self.exclusions.get("members_excluded"))}
        ours = {m["run_id"] for m in derived["members_excluded"]}
        return {"status": "disagrees" if differing else "agrees", "differing_keys": differing,
                "members_only_stored": sorted(map(str, stored - ours)), "members_only_rederived": sorted(ours - stored),
                "catalog_sha256": derived["catalog_sha256"], "rederived": derived}

    def read_reference_slots(self):
        """ROS(ii): independently parse the archived tree; never rebuild via repo code."""
        r = self.reader
        pack_id = self.roster.get("pack_id", self.harvest.get("pack_id"))
        if not isinstance(pack_id, str) or Path(pack_id).name != pack_id:
            r.flag("roster_pack_not_archived", "plan_tree", "invalid pack id")
            return {}, {}
        relative = "configs/campaigns/" + pack_id + "/plan_tree.json"
        path = self.archive / "sources/repo" / relative
        data = r.raw(path, "plan_tree", False)
        if data is None:
            r.flag("roster_pack_not_archived", "plan_tree", "archived tree missing")
            return {}, {}
        tree = r.json(path, "plan_tree")
        sizing_path = self.archive / "sources/repo/configs/campaigns/v5_claim_25g83/sizing_b5.json"
        source = "archive"
        if not sizing_path.is_file():
            # ROS(ii)(b) explicitly reads the analysis checkout's sealed pack table.
            sizing_path = Path(__file__).resolve().parents[1] / "configs/campaigns/v5_claim_25g83/sizing_b5.json"
            source = "analysis_checkout"
        sizing = r.json(sizing_path, "sizing_b5.json")
        expected = get(sizing, "packs", self.pack, "plan_tree", "sha256")
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            r.flag("roster_plan_tree_not_sealed", "plan_tree", {"own_sha256": digest, "sealed_sha256": expected})
        slots = {}
        external_value = tree.get("external_inputs")
        external = objects(external_value if isinstance(external_value, list) else get(external_value, "manifests"))
        for stage in objects(tree.get("stage_graph")):
            retry = mapping(stage.get("spare_retry"))
            slot = retry.get("slot")
            if slot not in ("start", "midpoint", "end"):
                continue
            input_path, input_id = get(stage, "input", "path"), get(stage, "input_ref", "input_id")
            primary = [m for ext in external if (
                (input_path is not None and get(ext, "manifest", "path") == input_path)
                or (input_id is not None and ext.get("input_id") == input_id))
                       for m in objects(ext.get("members"))]
            for member in primary + objects(retry.get("members")):
                rid = member.get("run_id")
                if not isinstance(rid, str) or Path(rid).name != rid or rid in (".", ".."):
                    r.flag("unit_shape_invalid", "plan_tree", "invalid reference run id")
                    continue
                if rid in slots:
                    r.flag("unit_shape_invalid", rid, "reference listed twice in tree")
                slots[rid] = slot
                named = role(rid)
                if named != slot:
                    r.flag("reference_slot_disagrees", rid, {"run_id_role": named, "plan_slot": slot})
        return slots, {"sha256": digest, "sealed_sha256": expected, "sizing_source": source}

    def calibration(self):
        r = self.reader
        record = r.json(self.archive / "withheld/bracket-evaluation.json", "withheld/bracket-evaluation.json")
        recorded = get(record, "assessment", "b_fiducial_s")
        binding = r.json(self.archive / "derived/bracket-binding.json", "derived/bracket-binding.json", False)
        inventory = [(p, r.json(p, "calibration/" + p.parent.name)) for p in
                     sorted((self.claim_root / "instrument_validation").glob("*/instrument_evidence.json"))]
        captures = {}
        for slot in ("pre", "post"):
            attempt = get(binding, "endpoints", slot, "attempt_id")
            matches = [(p, c) for p, c in inventory if isinstance(attempt, str)
                       and c.get("attempt_id", c.get("validation_id")) == attempt]
            if not matches:
                matches = [(p, c) for p, c in inventory if p.parent.name.endswith("-cal-" + slot)]
                if matches:
                    r.flag("calibration_capture_name_fallback", "cal-" + slot, "binding absent or names no existing capture")
            if len(matches) == 1:
                capture = matches[0][1]
                value = capture.get("b_fiducial_s")
                if finite(value) and value >= 0:
                    captures[slot] = value
                else:
                    r.flag("nonfinite_value", "cal-" + slot, "invalid fiducial bound")
            else:
                r.flag("archive_file_missing", "cal-" + slot, "need exactly one capture")
        pre, post = captures.get("pre"), captures.get("post")
        bop = recorded if finite(recorded) and recorded >= 0 else None
        if pre is None or post is None:
            r.flag("b_op_from_record", "window", "capture missing; recorded operative bound used if available")
        else:
            drift = abs(post - pre)
            # Frozen bracket arithmetic: 14.531 ms allowance and the registered
            # 15.50217418713139 ms drift budget, not numerical agreement bars.
            # From calibration_acceptance_d079_v2_n24_25g83_r2.json:
            # quantized_range_s and prediction_99_within_window_two_draw_s.
            bop = max(pre, post) + max(drift, 0.014531)
            # Positive unrounded b_op has no printed cell half-width: use the
            # ruling's 1e-6 relative bar (>2.2e-10 relative double noise), with
            # no absolute seconds floor that would hide sub-microsecond edits.
            if finite(recorded) and abs(bop - recorded) > 1e-6 * abs(bop):
                r.flag("b_op_mismatch", "window", {"own_s": bop, "recorded_s": recorded})
            if drift > 0.01550217418713139:
                r.flag("bracket_drift_over_budget", "window", {"drift_s": drift})
        return {"b_pre_s": pre, "b_post_s": post, "b_op_s": bop, "b_op_recorded_s": recorded}

    def member(self, run_id, member_role="science", *, compared=False):
        if compared:
            self.compared_run_ids.add(run_id)
        if run_id not in self.members:
            root = self.bound_root if member_role == "corpus" else self.claim_root
            self.members[run_id] = Member(root / run_id, run_id, self.reader, self.b["b_op_s"], member_role)
            m = self.members[run_id]
            pre = self.b["b_pre_s"]
            if member_role == "science" and not finite(m.bpre):
                self.reader.flag("member_pre_bound_missing", run_id, {"window_s": pre, "member_s": m.bpre})
            # Both fields are stored copies of the pre-capture bound.
            elif member_role == "science" and finite(pre) and m.bpre != pre:
                self.reader.flag("member_pre_bound_mismatch", run_id, {"window_s": pre, "member_s": m.bpre})
        return self.members[run_id]

    def compute_neg8(self):
        r, a = self.reader, self.archive
        source = r.json(a / "derived/neg8-allowance.json", "derived/neg8-allowance.json")
        screen = r.json(a / "derived/neg8-screen.json", "derived/neg8-screen.json")
        clean = r.json(a / "derived/neg8-clean-corpus.json", "derived/neg8-clean-corpus.json", False)
        registered_source = source.get("source") == "survivor_rescreen"
        if not registered_source and not self.diagnostic:
            r.flag("neg8_source_not_rescreen", "window", {"source": source.get("source")})
        clean_members = objects(clean.get("members"))
        if clean_members:
            ids = [m.get("bundle_id") for m in clean_members]
        else:
            if source.get("clean_bound") or not self.diagnostic:
                r.flag("archive_file_missing", "derived/neg8-clean-corpus.json", "named clean corpus missing")
                ids = []
            else:
                bound = r.json(self.bound_root / "neg8-drift-bound.json", "neg8-drift-bound.json")
                ids = get(bound, "reference_corpus", "member_ids", default=[])
        ids = ids if isinstance(ids, list) else []
        corpus = []
        actual_ids = []
        for run_id in ids:
            if not isinstance(run_id, str) or role(run_id) != "corpus":
                r.flag("kept_unit_identity_mismatch", "corpus", "invalid corpus run id")
                continue
            m = self.member(run_id, "corpus", compared=True)
            if m.usable and "request" in m.energies and m.model == "Qwen2.5-1.5B-Instruct-4bit":
                corpus.append(m.energies["request"])
                actual_ids.append(run_id)
            else:
                r.flag("kept_member_unusable", run_id, "selected corpus member unusable or wrong model")
        survivors = mapping(get(screen, "rescreen", "survivors"))
        losses = {m["bundle_id"] for m in objects(get(survivors, "reference_losses"))
                   if isinstance(m.get("bundle_id"), str)}
        losses.update(mapping(screen.get("harvest_reference_losses")))
        basis = {m["bundle_id"] for m in objects(get(self.verdict, "evaluation_basis", "member_occurrences"))
                 if isinstance(m.get("bundle_id"), str)}
        survivor_ids = sorted(set(self.reference_slots) & basis - losses)
        intersection = sorted(set(survivor_ids) & self.excluded)
        if intersection:
            r.flag("excluded_reference_in_screen", "window", {"run_ids": intersection})
        refs = {"start": [], "midpoint": [], "end": []}
        for run_id in survivor_ids:
            which = self.reference_slots[run_id]
            m = self.member(run_id, which, compared=True)
            if m.usable and "request" in m.energies and m.model == "Qwen2.5-1.5B-Instruct-4bit":
                refs[which].append(m.energies["request"])
            else:
                r.flag("kept_member_unusable", run_id, "survivor has no usable reference request")
        counts = {k: sum(self.reference_slots[i] == k for i in survivor_ids) for k in refs}
        shape_valid = counts["midpoint"] <= 1 and counts["start"] <= 3 and counts["end"] <= 3
        if not shape_valid:
            r.flag("unit_shape_invalid", "neg8/references", "at most 3 start, 1 midpoint and 3 end references")
        maximum_n = 18 if self.diagnostic else 12
        if not 10 <= len(corpus) <= maximum_n:
            r.flag("unit_shape_invalid", "neg8/corpus", {"corpus_n": len(corpus), "expected": "10.." + str(maximum_n)})
            if not self.diagnostic:
                corpus = []
        recorded_counts = get(survivors, "reference_counts", default={"start": 3, "midpoint": 1, "end": 3})
        if recorded_counts != counts:
            r.flag("neg8_survivor_count_mismatch", "window", {"own": counts, "recorded": recorded_counts})
        if self.pack == "GAMMA" and get(survivors, "midpoint_lost"):
            r.flag("gamma_midpoint_lost_on_analysed_attempt", "window", "screen records lost midpoint")
        result = {"source": source.get("source"), "screen_decision": get(screen, "rescreen", "decision"),
                  "corpus_n": len(corpus), "corpus_ids": actual_ids, "survivor_ids": survivor_ids,
                  "n_start": counts["start"], "n_mid": counts["midpoint"], "n_end": counts["end"],
                  "start_mean_j": statistics.fmean(refs["start"]) if refs["start"] else None,
                  "midpoint_j": statistics.fmean(refs["midpoint"]) if refs["midpoint"] else None,
                  "end_mean_j": statistics.fmean(refs["end"]) if refs["end"] else None,
                  "t": None, "s_j": None, "bound_envelope_j": None, "bound_prediction_j": None,
                  "bound_j": None, "spread_j": None, "allowance_j": None, "allowance_recorded_j": None}
        own_bound = neg8_bound(corpus, counts["start"], counts["end"]) if (
            shape_valid and all(len(refs[k]) == counts[k] for k in refs)
            and (registered_source or self.diagnostic)) else None
        if own_bound:
            result.update(own_bound)
            result["spread_j"], result["allowance_j"] = drift_allowance(
                result["start_mean_j"], result["midpoint_j"], result["end_mean_j"], own_bound["bound_j"])
        if source.get("source") == "survivor_rescreen":
            bracket = r.json(a / "withheld/neg8-rescreen-bracket.json", "withheld/neg8-rescreen-bracket.json")
            bracket = bracket.get("bracket", {})
        elif source.get("source") == "stored_verdict" and self.diagnostic:
            bracket = get(self.verdict, "idle_admission_core", "neg8_bracket", default={})
        else:
            bracket = {}
        recorded = get(bracket, "drift_allowances", "gross_energy", "allowance_j")
        result["allowance_recorded_j"] = recorded
        if not finite(recorded):
            r.flag("neg8_allowance_unrecorded", "window", "no recorded gross allowance")
        # Agreement policy, unrounded joules; no printed cell half-width on the allowance.
        elif finite(result["allowance_j"]) and not agrees(result["allowance_j"], recorded):
            r.flag("neg8_allowance_mismatch", "window", {"own_j": result["allowance_j"], "recorded_j": recorded})
        return result

    def select(self, cell_id, stratum, chosen=None, compare=True):
        """Select only roster science units; validate the whole unit before pooling."""
        r = self.reader
        cell = self.exclusion_cells.get(cell_id, {})
        universe = {u: ids for (c, s, u), ids in self.units.items() if c == cell_id and s == stratum}
        declared = get(cell, "kept_units", stratum, default=[])
        if not isinstance(declared, list) or len(strings(declared)) != len(declared):
            r.flag("unit_shape_invalid", cell_id + "/" + stratum, "kept unit ids must be strings")
        declared = strings(declared)
        checked = {u for u, ids in universe.items() if not any(i in self.excluded for i in ids)}
        if compare and not self.diagnostic and set(declared) != checked:
            r.flag("kept_units_disagree", cell_id + "/" + stratum,
                   {"declared": sorted(declared), "from_members_excluded": sorted(checked)})
        if chosen is None:
            chosen = list(universe) if self.diagnostic else declared
            # Plan section 2.2 outranks SPEC 4.3's contradictory-list fallback:
            # a named removed member removes its whole unit from every primary cell.
            if not self.diagnostic:
                chosen = [u for u in chosen if not any(i in self.excluded for i in universe.get(u, []))]
        phase = "decode" if "decode" in cell_id else "prefill"
        selected = []
        for unit_id in sorted(set(chosen), key=unit_order):
            ids = universe.get(unit_id, [])
            if any(Path(i).name != i or i in (".", "..") for i in ids):
                r.flag("unit_shape_invalid", unit_id, "run ids must be bundle basenames")
                continue
            positions = [i.rsplit("-", 1)[-1] for i in ids]
            if len(ids) != (4 if stratum == "quad" else 1) or (stratum == "quad" and set(positions) != set(POSITIONS)):
                r.flag("unit_shape_invalid", unit_id, "need one repeat or four distinct ABBA positions")
                continue
            unit_number = unit_order(unit_id)[0]
            member_numbers = [unit_order(i.rsplit("-", 1)[0] if stratum == "quad" else i)[0] for i in ids]
            if unit_number == 1000000 or any(number != unit_number for number in member_numbers):
                r.flag("unit_shape_invalid", unit_id, "unit and member ordinals disagree")
                continue
            ids = sorted(ids, key=lambda i: (ordinal(i), i))
            if self.diagnostic and not all((self.claim_root / i).is_dir() for i in ids):
                continue
            members = [self.member(i, compared=compare) for i in ids]
            for rid in ids:
                if compare and not self.diagnostic and rid not in self.verdict_members:
                    r.flag("kept_member_outside_verdict_membership", unit_id, {"run_id": rid})
            if self.diagnostic and not all(m.usable for m in members):
                continue
            valid = True
            for m in members:
                position = m.run_id.rsplit("-", 1)[-1]
                expected = SIDE_MODELS.get(position[:1]) if self.pack == "GAMMA" else MODELS.get(self.pack)
                tags_valid = True
                if self.pack == "GAMMA":
                    arm = "decode" if phase == "decode" else "prefill-p2048"
                    model_tag = "qwen3-1p7b" if position.startswith("a") else "qwen3-8b"
                    required_tag = "df-condition=sw-" + arm + "-" + position[:1] + "-" + model_tag
                    tags_valid = isinstance(m.config_tags, list) and required_tag in m.config_tags
                if m.model != expected or not tags_valid or ordinal(m.run_id) == 1000000:
                    r.flag("kept_unit_identity_mismatch", unit_id, {"run_id": m.run_id, "model": m.model})
                    valid = False
                if not m.usable or phase not in m.energies:
                    r.flag("kept_member_unusable", m.run_id + "/" + phase, "status, anchor, trace or phase invalid")
                    valid = False
                # Registered long-phase minimum: three overlapping records;
                # the short-prompt p42 diagnostic is explicitly exempt.
                elif "p42" not in cell_id and m.counts[phase] < 3:
                    r.flag("kept_member_phase_under_3_records", m.run_id + "/" + phase, {"count": m.counts[phase]})
                if "p42" not in cell_id and m.tokens[phase] is None:
                    r.flag("kept_member_token_mismatch", m.run_id + "/" + phase, m.tokens)
                interpolation = get(m.summary, "energy_bound_terms_j", "E_interpolation_joint_edge_bound_j")
                if interpolation is not None and interpolation != 0.0:
                    r.flag("interpolation_bound_nonzero", m.run_id, {"stored_j": interpolation})
            if valid:
                selected.append((unit_id, members))
        return selected


def reported_estimate(repeats, quad_means, kinds=(0.0, 0.0, 0.0), ordered_energies=None):
    nr, nb = len(repeats), len(quad_means)
    result = {"n_r": nr, "n_b": nb, "n_bundles": nr + 4 * nb}
    if min(nr, nb) < 2:
        return {**result, "mean_j": None, "lower_j": None, "upper_j": None, "interval": None}
    mean = (statistics.fmean(ordered_energies) if nr == nb == 10 and ordered_energies is not None
            else 0.2 * statistics.fmean(repeats) + 0.8 * statistics.fmean(quad_means))
    sr, sb = statistics.stdev(repeats), statistics.stdev(quad_means)
    variance = 0.04 * sr ** 2 / nr + 0.64 * sb ** 2 / nb
    df = min(nr, nb) - 1
    t = student_quantile(df)
    h = t * math.sqrt(variance)
    B = math.fsum(kinds) if all(finite(x) for x in kinds) else None
    return {**result, "mean_j": mean, "lower_j": mean - h - B if B is not None else None,
            "upper_j": mean + h + B if B is not None else None,
            "interval": {"df": df, "t": t, "s_r": sr, "s_b": sb, "variance": variance,
                         "h_j": h, "kind_averages_j": list(kinds), "B_j": B}}


def flatten(units):
    return [m for _, members in units for m in members]


def phase_bound(member, phase, bound=None):
    if bound is None:
        return get(member.op, phase, "max_abs_delta_j")
    if not finite(bound) or not all(finite(x) for x in (member.s, member.m)) or phase not in member.edges:
        return None
    return shift_envelope(member.records, *member.edges[phase], bound, member.s, member.m)["max_abs_delta_j"]


def make_reported(window, cell_id, repeats, quads, minimum=5, bound=None):
    phase = "decode" if "decode" in cell_id else "prefill"
    rm, qm = flatten(repeats), flatten(quads)
    all_members = sorted(rm + qm, key=lambda m: (ordinal(m.run_id), m.run_id))
    result = {"status": "computed", "model": MODELS[window.pack], "phase": phase,
              "n_r": len(repeats), "n_b": len(quads), "n_bundles": len(all_members),
              "kept_units": {"repeat": [u for u, _ in repeats], "quad": [u for u, _ in quads]},
              "removed_units": window.exclusion_cells.get(cell_id, {}).get("dropped_units", []),
              "mean_j": None, "lower_j": None, "upper_j": None, "interval": None,
              "attribution_floor": {"value_j": None, "attained_by": None, "minimum_j": None},
              "per_token": {"j_per_token": None, "denominator": 512 if phase == "decode" else 2048,
                            "status": "not_computed"}}
    if minimum is not None and min(len(repeats), len(quads)) < minimum:
        result["status"] = "below_minimum"
        window.reader.flag("cell_below_minimum", cell_id, {"n_r": len(repeats), "n_b": len(quads)})
        return result
    if min(len(repeats), len(quads)) < 2:
        result["status"] = "not_computed"
        result["reason"] = "insufficient_units"
        if len(quads) >= 2:
            values = [statistics.fmean(m.energies[phase] for m in ms) for _, ms in quads]
            result["diagnostic_quad_mean_j"] = statistics.fmean(values)
            result["diagnostic_quad_stdev_j"] = statistics.stdev(values)
        return result
    bounds = {m.run_id: phase_bound(m, phase, bound) for m in all_members}
    if all(finite(v) for v in bounds.values()):
        anchor_average = (0.2 * statistics.fmean(bounds[m.run_id] for m in rm)
                          + 0.8 * statistics.fmean(bounds[m.run_id] for m in qm))
        maximum = max(bounds.values())
        result["attribution_floor"] = {"value_j": maximum, "minimum_j": min(bounds.values()),
                                       "attained_by": next(m.run_id for m in all_members if bounds[m.run_id] == maximum)}
    else:
        anchor_average = None
        window.reader.flag("kept_member_unusable", cell_id, "phase bound unavailable")
    allowance = window.neg8["allowance_j"]
    kinds = (anchor_average, 0.0, allowance / 2 if finite(allowance) else None)
    result.update(reported_estimate([m.energies[phase] for m in rm],
                                   [statistics.fmean(m.energies[phase] for m in ms) for _, ms in quads],
                                   kinds, [m.energies[phase] for m in all_members]))
    if all(m.tokens[phase] is not None for m in all_members):
        result["per_token"]["j_per_token"] = (
            0.2 * sum(m.energies[phase] for m in rm) / sum(m.tokens[phase] for m in rm)
            + 0.8 * sum(m.energies[phase] for m in qm) / sum(m.tokens[phase] for m in qm))
        result["per_token"]["status"] = "computed"
    else:
        result["per_token"]["status"] = "token_mismatch"
    if minimum is None and min(len(repeats), len(quads)) < 5:
        result["status"] = "below_registered_minimum"
    return result


def quad_difference(members, phase, floor=False):
    energies = {m.run_id.rsplit("-", 1)[-1]: m.energies[phase] for m in members}
    if floor:
        return (energies["b1"] + energies["b2"] - energies["a1"] - energies["a2"]) / 2
    return (energies["b1"] + energies["b2"]) / 2 - (energies["a1"] + energies["a2"]) / 2


def common_width(members, phase, bop):
    if not finite(bop) or any(phase not in m.residual for m in members):
        return None
    def q(on, off):
        values = {m.run_id.rsplit("-", 1)[-1]: overlap(
            m.records, m.edges[phase][0] + on, m.edges[phase][1] + off)[0] for m in members}
        return (values["b1"] + values["b2"] - values["a1"] - values["a2"]) / 2
    z = q(0.0, 0.0)
    extrema = []
    for index in (0, 1):
        points = {-bop, 0.0, bop}
        for m in members:
            edge = m.edges[phase][index]
            for start, end, _ in m.records:
                points.update(x - edge for x in (start, end) if -bop <= x - edge <= bop)
        values = [q(delta, 0.0) if index == 0 else q(0.0, delta) for delta in sorted(points)]
        extrema.append((min(values), max(values)))
    shared = max(abs((extrema[0][0] - z) + (extrema[1][0] - z)),
                 abs((extrema[0][1] - z) + (extrema[1][1] - z))) + abs(z - quad_difference(members, phase, True))
    local = 0.5 * sum(m.residual[phase]["max_abs_delta_j"] for m in members)
    return {"shared_j": shared, "local_j": local, "width_j": shared + local,
            "z_j": z, "onset_extrema_j": list(extrema[0]), "offset_extrema_j": list(extrema[1])}


def point_floor(values, form):
    n = len(values)
    mean = statistics.fmean(values)
    dev = [v - mean for v in values] if form == "absolute" else values
    s = statistics.stdev(dev)
    prediction = round(student_quantile(n - 1), 3) * s * math.sqrt(1 + 1 / n)
    if form == "comparative":
        prediction += abs(mean)
    maximum = max(abs(v) for v in dev)
    return {"point_unguarded_floor_j": max(maximum, prediction), "prediction_j": prediction,
            "max_abs_deviation_j": maximum, "s_j": s}


def corner_max(values, widths, form):
    if len(values) > 16:
        return None
    return max(point_floor([v + sign * w for v, sign, w in zip(values, signs, widths)], form)[
        "point_unguarded_floor_j"] for signs in itertools.product((-1, 1), repeat=len(values)))


def floor_estimate(values, widths, form, shared=None, local=None):
    n = len(values)
    result = {"n": n, "status": "below_minimum", "point_unguarded_floor_j": None,
              "prediction_j": None, "max_abs_deviation_j": None,
              "corner_widened_unguarded_floor_j": None, "operative_unguarded_floor_j": None,
              "guard": None, "guarded_floor_j": None, "widths_j": widths,
              "shared_j": shared or [], "local_j": local or [], "R": None,
              "R_cm": "not_applicable" if form == "absolute" else None}
    if n < 5:
        return result
    result.update(point_floor(values, form))
    if len(widths) != n or not all(finite(w) and w >= 0 for w in widths) or n > 16:
        result.update(status="not_computed", reason="width_unavailable_or_corner_cap")
        return result
    corner = corner_max(values, widths, form)
    if form == "absolute":
        mean = statistics.fmean(values)
        linear = max(abs(v - mean) + w * (1 - 1 / n) +
                     sum(widths[j] for j in range(n) if j != i) / n
                     for i, (v, w) in enumerate(zip(values, widths)))
    else:
        linear = max(abs(v) + w for v, w in zip(values, widths))
    corner = max(corner, linear)
    point = result["point_unguarded_floor_j"]
    operative = max(point, corner)
    guard = 1.0 if n >= 10 else math.sqrt(9 / (n - 1))
    result.update(status="computed", corner_widened_unguarded_floor_j=corner,
                  operative_unguarded_floor_j=operative, guard=guard, guarded_floor_j=guard * operative,
                  linear_deviation_bound_j=linear, R=corner / point if point else None)
    if form == "comparative" and shared is not None and local is not None:
        numerator = max(corner_max([v + sign * w for v, w in zip(values, shared)], local, form)
                        for sign in (-1, 1))
        result["common_mode_numerator_j"] = numerator
        result["R_cm"] = numerator / point if point else None
    return result


def corner_upper_bound(values, widths, form):
    """Director's pooled-only bound on every corner, without enumerating the box."""
    n = len(values)
    point = point_floor(values, form)
    mean = statistics.fmean(values)
    if form == "absolute":
        linear = max(abs(v - mean) + w * (1 - 1 / n) +
                     sum(widths[j] for j in range(n) if j != i) / n
                     for i, (v, w) in enumerate(zip(values, widths)))
    else:
        linear = max(abs(v) + w for v, w in zip(values, widths))
    s_bound = point["s_j"] + math.sqrt(math.fsum(w ** 2 for w in widths) / (n - 1))
    prediction = round(student_quantile(n - 1), 3) * s_bound * math.sqrt(1 + 1 / n)
    if form == "comparative":
        prediction += abs(mean) + statistics.fmean(widths)
    return {"corner_widened_unguarded_floor_j": max(linear, prediction),
            "linear_deviation_bound_j": linear, "s_upper_bound_j": s_bound,
            "prediction_upper_bound_j": prediction}


def pooled_floor_estimate(values, widths, form):
    """Keep the registered estimator/cap intact; only pooled samples may use the bound."""
    result = floor_estimate(values, widths, form)
    n = len(values)
    result["corner_method"] = ("exact_enumeration" if n <= 16 else "triangle_inequality_upper_bound")
    if n <= 16 or len(widths) != n or not all(finite(w) and w >= 0 for w in widths):
        return result
    bounds = corner_upper_bound(values, widths, form)
    corner = bounds["corner_widened_unguarded_floor_j"]
    point = result["point_unguarded_floor_j"]
    operative = max(point, corner)
    guard = 1.0 if n >= 10 else math.sqrt(9 / (n - 1))
    result.pop("reason", None)
    result.update(bounds, status="computed", operative_unguarded_floor_j=operative,
                  guard=guard, guarded_floor_j=guard * operative, R=corner / point if point else None)
    return result


def contrast_stats(d, D=0.0):
    n = len(d)
    result = {"n": n, "d_k": d, "dbar_j": None, "s_d_j": None, "se_j": None,
              "t_star": None, "metrology_interval_j": [None, None], "D_j": D,
              "decision_interval_j": [None, None], "t_stat": None, "p": 1.0}
    if n < 2:
        return result
    mean, s = statistics.fmean(d), statistics.stdev(d)
    se = s / math.sqrt(n)
    t = round(student_quantile(n - 1), 3)
    interval = [mean - t * se, mean + t * se]
    # A constant nonzero effect has limiting t=+/-infinity, p=0. Output t=null.
    statistic = mean / se if se else None
    p = student_p(statistic, n - 1) if se else (0.0 if mean else 1.0)
    result.update(dbar_j=mean, s_d_j=s, se_j=se, t_star=t, metrology_interval_j=interval,
                  decision_interval_j=[interval[0] - D, interval[1] + D] if finite(D) else [None, None],
                  t_stat=statistic, p=p)
    return result


def holm(p_values):
    p = [x if finite(x) else 1.0 for x in p_values]
    order = sorted(range(2), key=lambda i: (p[i], i))
    result = [None, None]
    result[order[0]] = min(1.0, 2 * p[order[0]])
    result[order[1]] = min(1.0, max(2 * p[order[0]], p[order[1]]))
    return result


def contains_zero(interval):
    return all(finite(x) for x in interval) and interval[0] <= 0 <= interval[1]


def decision_beyond_floor(contrast, floor):
    decision, mean = contrast["decision_interval_j"], contrast["dbar_j"]
    return ((decision[0] > floor if mean > 0 else decision[1] < -floor)
            if finite(floor) and finite(mean) and all(finite(v) for v in decision) else None)


def evaluate_outcome(row, floor, reject, minimum=5, missing=False):
    mean = row["dbar_j"]
    if row["n"] < minimum or not finite(mean) or missing:
        return "not_estimable"
    metrology, decision = row["metrology_interval_j"], row["decision_interval_j"]
    if (not finite(floor) or not finite(row["D_j"]) or floor == 0 or mean == 0 or abs(mean) <= floor
            or (contains_zero(decision) and not contains_zero(metrology))):
        return "not_resolvable"
    if contains_zero(metrology) or not reject:
        return "unresolved"
    return "direction_supported"


def block_number(unit_id):
    match = re.search(r"-b(\d+)$", unit_id)
    return int(match[1]) if match else unit_id


def reduced_contrast(row, ids, kinds, omitted):
    keep = [i for i, uid in enumerate(ids) if block_number(uid) != omitted]
    if kinds is not None:
        terms = [statistics.fmean(kinds[i][j] for i in keep)
                 if keep and all(finite(kinds[i][j]) for i in keep) else None for j in range(3)]
        D = math.fsum(terms) if all(finite(t) for t in terms) else None
    else:
        terms, D = row.get("D_terms_j"), row["D_j"]
    return {**contrast_stats([row["d_k"][i] for i in keep], D), "D_terms_j": terms}


def finish_contrast(row, other_p, floor, ids=None, kind_rows=None, minimum=5, missing=False, partner=None):
    row = dict(row)
    if row["n"] < minimum or missing or not finite(row["dbar_j"]):
        row["p"] = 1.0
    row.update(floor_gate_j=floor, holm_p=holm([row["p"], other_p])[0])
    # PLAN 7.2 fixes familywise alpha=0.05; not a numerical agreement bar.
    row["holm_reject"] = row["holm_p"] <= 0.05
    row["direction"] = "positive" if finite(row["dbar_j"]) and row["dbar_j"] > 0 else (
        "negative" if finite(row["dbar_j"]) and row["dbar_j"] < 0 else None)
    row["outcome"] = evaluate_outcome(row, floor, row["holm_reject"], minimum, missing)
    row["kept_quads"] = ids or [str(i + 1) for i in range(row["n"])]
    loo, verdict_influential, magnitude_influential = [], False, False
    if row["n"] >= 3:
        for i, unit_id in enumerate(row["kept_quads"]):
            omitted = block_number(unit_id)
            reduced = reduced_contrast(row, row["kept_quads"], kind_rows, omitted)
            partner_p, partner_n = other_p, None
            if partner is not None:
                partner_row, partner_ids, partner_kinds, partner_missing = partner
                paired = reduced_contrast(partner_row, partner_ids, partner_kinds, omitted)
                partner_n = paired["n"]
                partner_p = 1.0 if partner_missing else paired["p"]
                # An unchanged partner retains its full-data minimum rule.
                if paired["n"] == partner_row["n"] and paired["n"] < minimum:
                    partner_p = 1.0
            adjusted = holm([1.0 if missing else reduced["p"], partner_p])[0]
            # Same PLAN 7.2 familywise alpha for the leave-one-out replay.
            reject = adjusted <= 0.05
            outcome = evaluate_outcome(reduced, floor, reject, 2, missing)
            sign = "positive" if reduced["dbar_j"] > 0 else ("negative" if reduced["dbar_j"] < 0 else None)
            above = finite(floor) and abs(reduced["dbar_j"]) > floor
            full_above = finite(floor) and abs(row["dbar_j"]) > floor
            verdict_influential |= (sign != row["direction"] or above != full_above
                                    or reject != row["holm_reject"] or outcome != row["outcome"])
            # PLAN 7.3 fixes magnitude influence at one quarter of the floor.
            magnitude_influential |= finite(floor) and abs(reduced["dbar_j"] - row["dbar_j"]) > 0.25 * floor
            loo.append({**reduced, "dropped": unit_id, "block_number": omitted, "partner_n": partner_n,
                        "partner_p": partner_p, "holm_p": adjusted,
                        "holm_reject": reject, "above_floor": above, "outcome": outcome, "direction": sign})
    row.update(loo=loo, loo_verdict_influential=verdict_influential,
               loo_magnitude_influential=magnitude_influential)
    row["ceiling"] = ("L2" if row["outcome"] == "direction_supported" and row["direction"] == "positive"
                      and not verdict_influential else "L1")
    return row


def descriptive_estimate(side_a, side_b, contrast, phase):
    n = len(side_a)
    result = {"ratio": None, "ratio_interval": [None, None], "per_token_difference_j": None,
              "per_token_metrology_interval_j": [None, None], "per_token_decision_interval_j": [None, None],
              "per_token_unit": "output_token" if phase == "decode" else "prompt_token"}
    if n >= 2 and all(a > 0 and b > 0 for a, b in zip(side_a, side_b)):
        logs = [math.log(b / a) if finite(b / a) and b / a > 0 else math.log(b) - math.log(a)
                for a, b in zip(side_a, side_b)]
        mean = statistics.fmean(logs)
        h = student_quantile(n - 1) * statistics.stdev(logs) / math.sqrt(n)
        try:
            result.update(ratio=math.exp(mean), ratio_interval=[math.exp(mean - h), math.exp(mean + h)])
        except OverflowError:
            result.update(ratio=float("inf"), ratio_interval=[None, float("inf")])
    denominator = 512 if phase == "decode" else 2048
    if finite(contrast["dbar_j"]):
        result["per_token_difference_j"] = contrast["dbar_j"] / denominator
        for source, target in (("metrology_interval_j", "per_token_metrology_interval_j"),
                               ("decision_interval_j", "per_token_decision_interval_j")):
            result[target] = [v / denominator if finite(v) else None for v in contrast[source]]
    return result


def cross_window(side_means, reported):
    if len(side_means) < 2 or not finite(reported.get("mean_j")) or not reported.get("interval"):
        return {"status": "not_computed", "reason": "insufficient_units"}
    G = statistics.fmean(side_means)
    h = student_quantile(len(side_means) - 1) * statistics.stdev(side_means) / math.sqrt(len(side_means))
    F, hf = reported["mean_j"], reported["interval"]["h_j"]
    delta = G - F
    return {"G_j": G, "h_G_j": h, "F_j": F, "h_F_j": hf, "delta_j": delta,
            "agree": abs(delta) <= math.sqrt(h ** 2 + hf ** 2), "n": len(side_means)}


def contrast_inputs(window, quads, phase, bound=None):
    d, kinds, a, b = [], [], [], []
    for _, members in quads:
        d.append(quad_difference(members, phase))
        energies = {m.run_id.rsplit("-", 1)[-1]: m.energies[phase] for m in members}
        a.append((energies["a1"] + energies["a2"]) / 2)
        b.append((energies["b1"] + energies["b2"]) / 2)
        anchors = [phase_bound(m, phase, bound) for m in members]
        allowance = window.neg8["allowance_j"]
        kinds.append([0.5 * sum(anchors) if all(finite(v) for v in anchors) else None, 0.0,
                      allowance if finite(allowance) else None])
    terms = [statistics.fmean(k[j] for k in kinds) if kinds and all(finite(k[j]) for k in kinds) else None
             for j in range(3)]
    D = math.fsum(terms) if all(finite(v) for v in terms) else None
    return {**contrast_stats(d, D), "D_terms_j": terms}, kinds, a, b


def missing_pack():
    return {"status": "not_computed", "reason": "pack_missing"}


def make_floors(window, phase, chosen, reported, bound=None):
    forms = {}
    for form, stratum in (("absolute", "repeat"), ("comparative", "quad")):
        units = chosen[stratum]
        if form == "absolute":
            values = [ms[0].energies[phase] for _, ms in units]
            widths = [phase_bound(ms[0], phase, bound) for _, ms in units]
            shared = local = None
        else:
            values = [quad_difference(ms, phase, True) for _, ms in units]
            splits = [common_width(ms, phase, window.b["b_op_s"] if bound is None else bound) for _, ms in units]
            widths = [s["width_j"] if s else None for s in splits]
            shared = [s["shared_j"] if s else None for s in splits]
            local = [s["local_j"] if s else None for s in splits]
        result = floor_estimate(values, widths, form, shared, local)
        if not window.diagnostic and reported["status"] == "below_minimum":
            result = floor_estimate([], [], form)
            result["n"] = len(units)
        result.update(kept_units=[u for u, _ in units], removed_units=reported["removed_units"],
                      allowance_j=window.neg8["allowance_j"], allowance_source=window.neg8["source"])
        guarded, allowance = result["guarded_floor_j"], result["allowance_j"]
        result["drift_widened_guarded_floor_j"] = (guarded + allowance
            if finite(guarded) and finite(allowance) else None)
        if result["status"] == "computed" and not finite(allowance):
            result.update(status="not_computed", reason="whole_window_drift_allowance_unrecorded")
        if form == "absolute":
            result["widths_bpre_j"] = [get(ms[0].pre, phase, "max_abs_delta_j") for _, ms in units]
        forms[form] = result
    absolute = forms["absolute"]["drift_widened_guarded_floor_j"]
    comparative = forms["comparative"]["drift_widened_guarded_floor_j"]
    return forms, {"floor_abs_j": absolute, "floor_cmp_j": comparative,
                   "floor_gate_j": max(absolute, comparative) if all(finite(v) for v in (absolute, comparative)) else None}


def contrast_floor(cells, phase):
    sides = {pack: cells.get(model + "/" + phase, {}) for pack, model in MODELS.items()}
    values = [c.get("floor_gate_j") for c in sides.values()]
    value = max(values) if all(finite(v) for v in values) else None
    attained = [pack for pack, cell in sides.items() if value is not None and cell.get("floor_gate_j") == value]
    return {"floor_gate_j": value, "attained_by": attained, "sides": sides}


def number(value):
    try:
        result = float(value)
        return result if finite(result) and result >= 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def fit_line(points):
    """Centered ordinary least squares, preserving ns-scale host precision."""
    x0, y0 = points[0]
    xs, ys = [x - x0 for x, _ in points], [y - y0 for _, y in points]
    xm, ym = statistics.fmean(xs), statistics.fmean(ys)
    denominator = math.fsum((x - xm) ** 2 for x in xs)
    if not denominator:
        return None
    slope = math.fsum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / denominator
    return y0 + ym - slope * (x0 + xm), slope


# Registered meter clock fit (block-5 registration: "the parser fits the
# meter's sample clock to the host's clock from the poll times"; RUN_STATE
# item 84). Same definition as the parser's, written here independently.
FIT_RESPONSE_CAP = 63        # a full 63-sample response may have left samples queued
FIT_MAX_RTT_MS = 3.0         # eligible polls answered within 3 ms
FIT_MIN_POINTS = 20          # fewer eligible polls: fit every poll instead
FIT_BIN_DEVICE_MS = 10_000   # envelope bins about 10 s of device time wide
FIT_MIN_BINS = 4


def meter_clock_fit(points):
    """Lower-envelope clock fit over (newest device ms, rx ns, RTT ms, n) per poll."""
    if len(points) < 2:
        return None
    eligible = [p for p in points if p[3] < FIT_RESPONSE_CAP and p[2] < FIT_MAX_RTT_MS]
    filtered = len(eligible) >= FIT_MIN_POINTS
    used = eligible if filtered else points
    if len(used) < 2:
        return None
    pairs = [(p[0], p[1]) for p in used]
    initial = fit_line(pairs)
    if initial is None:
        return None
    a0, b0 = initial
    origin = pairs[0][0]
    span = pairs[-1][0] - origin
    bins = max(FIT_MIN_BINS, int(span / FIT_BIN_DEVICE_MS))
    width = (span + 1) / bins
    minima = {}
    for x, y in pairs:
        residual = y - (a0 + b0 * x)
        key = min(int((x - origin) / width), bins - 1)
        if key not in minima or residual < minima[key][0]:
            minima[key] = (residual, (x, y))
    envelope = fit_line([minima[k][1] for k in sorted(minima)]) if len(minima) >= 2 else None
    a, b = envelope if envelope is not None else initial
    if b <= 0 or not all(finite(v) for v in (a, b)):
        return None
    return {"intercept_ns": a, "slope_ns_per_ms": b, "fit_points": len(points),
            "points_used": len(used), "filtered": filtered, "bins": bins,
            "minimum_bins": len(minima), "envelope_fallback": envelope is None,
            "bin_origin": "device time of the first fit point", "bin_width_device_ms": width,
            "max_above_envelope_ns": max(y - (a + b * x) for x, y in pairs)}


class MeterStream:
    """Independent raw-byte decoder and clock fit, RECONCILE-r2 section 3."""
    def __init__(self, path, reader):
        self.name, self.reader = path.name, reader
        self.times, self.powers, self.battery_times, self.battery_powers = [], [], [], []
        self.battery_current_times, self.battery_currents = [], []
        self.header, self.trailer, self.fit, self.r_max_s = {}, {}, None, None
        rows = reader.lines(path, "meter/" + self.name)
        headers = [x for x in rows if x.get("k") == "h"]
        trailers = [x for x in rows if x.get("k") == "t"]
        if len(headers) != 1 or headers[0].get("rate_idx") not in (0, 1, 2, 3):
            reader.flag("meter_stream_malformed", self.name, "need one header with a known rate")
            return
        self.header = headers[0]
        self.trailer = trailers[-1] if trailers else {}
        device, powers, points = [], [], []
        previous_seq, previous_rx, current, running_max, duplicates = None, None, 0, None, 0
        decoder = struct.Struct("<HHiiHHHH")
        polls = []
        for row in rows:
            if row.get("k") != "b":
                continue
            tx, rx, n = row.get("tx"), row.get("rx"), row.get("n")
            try:
                if not all(finite(v) for v in (tx, rx, n)) or not isinstance(n, int) or n < 0:
                    raise ValueError("invalid batch timestamps/count")
                payload = bytes.fromhex(row.get("p", ""))
                if len(payload) != n * decoder.size:
                    raise ValueError("payload length differs from count")
            except (ValueError, TypeError):
                reader.flag("meter_stream_malformed", self.name, "invalid batch")
                continue
            polls.append((rx, tx, n, payload, row))
        # Registered parser definition: polls are taken in host receive order
        # (stable for equal rx), so decoding and the fit see one sequence.
        polls.sort(key=lambda poll: poll[0])
        for rx, tx, n, payload, row in polls:
            newest = None
            for k, (seq, _, voltage, current_ua, *_aux) in enumerate(decoder.iter_unpack(payload)):
                if previous_seq is not None:
                    # Sequence is a 16-bit millisecond counter. Signed modular
                    # steps use half its 65536 ms range; longer host gaps pick
                    # the nearest whole wrap from elapsed host milliseconds.
                    step = ((seq - previous_seq + 32768) % 65536) - 32768
                    if k == 0 and previous_rx is not None:
                        host_ms = (rx - previous_rx) / 1e6
                        if host_ms > 32768:
                            step += round((host_ms - step) / 65536) * 65536
                    current += step
                previous_seq = seq
                if running_max is not None and current <= running_max:
                    duplicates += 1
                    continue
                running_max, newest = current, current
                device.append(current)
                powers.append((voltage / 1e6) * (current_ua / 1e6))
            if payload:
                previous_rx = rx
            # One fit point per poll that kept a sample: its newest sample
            # against the poll's host receive time, with RTT ms and count.
            if newest is not None:
                points.append((newest, rx, (rx - tx) / 1e6, n))
            ac, av = get(row, "smc", "B0AC"), get(row, "smc", "B0AV")
            if finite(ac):
                self.battery_current_times.append(rx)
                self.battery_currents.append(ac)
            if finite(ac) and finite(av):
                self.battery_times.append(rx)
                self.battery_powers.append(-ac * av / 1e6)
        fit = meter_clock_fit(points)
        if fit is None:
            reader.flag("meter_no_fit", self.name, {"fit_points": len(points)})
            return
        a, b = fit["intercept_ns"], fit["slope_ns_per_ms"]
        self.fit = {**fit, "duplicates_dropped": duplicates}
        self.r_max_s = max(0.0, fit["max_above_envelope_ns"] / 1e9)
        # Meter clock contract: publish integer host ns before sample selection.
        self.times = [round(a + b * x) for x in device]
        self.powers = powers
        ordered = sorted(zip(self.battery_times, self.battery_powers))
        self.battery_times = [t for t, _ in ordered]
        self.battery_powers = [p for _, p in ordered]
        currents = sorted(zip(self.battery_current_times, self.battery_currents))
        self.battery_current_times = [t for t, _ in currents]
        self.battery_currents = [c for _, c in currents]

    def offset(self, mono_midpoint, journal, scope):
        start = (self.header.get("start_raw_ns"), self.header.get("start_mono_ns"))
        end = (self.trailer.get("end_raw_ns"), self.trailer.get("end_mono_ns"))
        if all(finite(v) for v in start + end):
            offset = start[0] - start[1]
            # Meter contract's 1 ms RAW-minus-MONO stability check detects
            # sleep; it grants no slack to move an agreement window.
            if abs((end[0] - end[1]) - offset) <= 1e6:
                return offset, "stream"
        candidates = []
        for row in journal:
            stamp = mapping(row.get("finished", row.get("started")))
            mono, raw = stamp.get("monotonic_ns"), stamp.get("monotonic_raw_ns")
            if all(finite(v) for v in (mono, raw)):
                candidates.append((abs(mono - mono_midpoint), mono, raw - mono))
        if candidates:
            offset = min(candidates)[2]
            self.reader.flag("meter_offset_from_journal", scope, {"stream": self.name})
            return offset, "journal"
        self.reader.flag("meter_offset_unavailable", scope, {"stream": self.name})
        return None, None


def sampled_term(times, powers, phase, baseline):
    lo, hi = (bisect.bisect_left(times, edge) for edge in phase)
    u0, u1 = (bisect.bisect_left(times, edge) for edge in baseline)
    if lo == hi or u0 == u1:
        return None
    T = (phase[1] - phase[0]) / 1e9
    mean, idle = statistics.fmean(powers[lo:hi]), statistics.fmean(powers[u0:u1])
    energy = mean * T
    return {"energy_J": energy, "baseline_W": idle, "delta_J": energy - idle * T,
            "n": hi - lo, "n_baseline": u1 - u0}


def idle_span(member):
    completions = [e.get("timestamp_s") for e in member.events if e.get("phase") == "idle_baseline"
                   and e.get("event_type") == "stage_completed" and finite(e.get("timestamp_s"))]
    if not completions:
        return None
    end = completions[-1]
    starts = [e.get("timestamp_s") for e in member.events if e.get("phase") == "idle_baseline"
              and e.get("event_type") == "stage_started" and finite(e.get("timestamp_s")) and e["timestamp_s"] < end]
    return (max(starts), end) if starts else None


def controller_request_spans(member):
    """Re-derive the meter's controller spans from raw stamps and idle events."""
    stamps = mapping(get(member.metadata, "uncertainty_evidence", "clock_anchor", "clock_stamps"))
    start, stop = mapping(stamps.get("sampling_started")), mapping(stamps.get("sampling_stopped"))
    before, after, epoch = start.get("monotonic_before_s"), stop.get("monotonic_after_s"), start.get("epoch_s")
    if not all(finite(v) and v >= 0 for v in (before, after, epoch)) or after <= before:
        return None
    # Meter boundary: start's before stamp to stop's after stamp, floored to
    # integer ns as recorded. Quantization is a method, not an agreement bar.
    request = [math.floor(before * 1e9), math.floor(after * 1e9)]
    idle_start = idle_end = None
    for event in member.events:
        if event.get("phase") != "idle_baseline":
            continue
        wall = event.get("timestamp_s")
        mapped = math.floor((before + (wall - epoch)) * 1e9) if finite(wall) else None
        if event.get("event_type") == "stage_started" and idle_start is None:
            own_ns = get(event, "metadata", "monotonic_ns")
            idle_start = own_ns if type(own_ns) is int else mapped
        elif event.get("event_type") == "stage_completed":
            idle_end = mapped
    baseline = [idle_start, idle_end] if all(finite(v) for v in (idle_start, idle_end)) and idle_start < idle_end else None
    return request, baseline


def rail_idle_power(member):
    """REG 5.8: elapsed_ns-weighted rich idle telemetry, never the trace's idle overlap."""
    if not hasattr(member, "_rail_idle_power"):
        rows = member.reader.lines(member.path / "rich_telemetry_idle.jsonl", member.run_id + "/rich_telemetry_idle.jsonl")
        valid = [row for row in rows if positive_int(row.get("elapsed_ns"))
                 and finite(row.get("rail_sum_power_w")) and row["rail_sum_power_w"] >= 0]
        member._rail_idle_power = (math.fsum(row["rail_sum_power_w"] * row["elapsed_ns"] for row in valid)
                                  / sum(row["elapsed_ns"] for row in valid)) if valid and len(valid) == len(rows) else None
        if member._rail_idle_power is None:
            member.reader.flag("meter_baseline_unavailable", member.run_id + "/request",
                               "rich idle telemetry lacks valid elapsed_ns and rail_sum_power_w")
    return member._rail_idle_power


def sampled_gross(times, powers, span):
    lo, hi = (bisect.bisect_left(times, edge) for edge in span)
    if lo == hi:
        return None
    mean = statistics.fmean(powers[lo:hi])
    return {"energy_J": mean * ((span[1] - span[0]) / 1e9), "mean_W": mean, "n": hi - lo}


def request_battery_activity(member, stream, wall, offset, flag):
    if "request" not in member.edges:
        return {"available": False, "active": False, "n": 0}
    controller = controller_request_spans(member)
    mono = controller[0] if controller else [(member.origin + edge - wall) * 1e9 for edge in member.edges["request"]]
    span = [edge + offset for edge in mono]
    lo, hi = (bisect.bisect_left(stream.battery_current_times, edge) for edge in span)
    active = any(c != 0 for c in stream.battery_currents[lo:hi])
    if active and flag:
        member.reader.flag("meter_battery_activity", member.run_id,
                           {"source": "request B0AC read not zero", "stream": stream.name})
    return {"available": lo != hi, "active": active, "n": hi - lo}


def machine_member(member, phase, streams, journal, bop, shifts=(0.0, 0.0), flag=True):
    """Request: REG 5.8 delta. Phases: 03:26 amendment, gross meter only."""
    scope = member.run_id + "/" + phase
    baseline = idle_span(member)
    anchor = mapping(member.metadata.get("clock_anchor") or get(member.metadata, "uncertainty_evidence", "clock_anchor"))
    lower, upper = anchor.get("wall_minus_monotonic_lower_s"), anchor.get("wall_minus_monotonic_upper_s")
    request = phase == "request"
    unavailable = {"delta_J": None, "boundary": MACHINE_BOUNDARY} if request else {
        "energy_J": None, "label": PHASE_MACHINE_LABEL, "basis": "gross meter term only; adapter loss excluded",
        "boundary": PHASE_MACHINE_BOUNDARY}
    comparison = getattr(member, "comparison", {})
    if comparison.get("status") == "not_compared":
        return {**unavailable, "status": "not_compared", "reason": comparison["reason"]}
    controller = controller_request_spans(member) if request else None
    if (request and (controller[1] if controller else baseline) is None) or phase not in member.edges or (
            controller is None and not all(finite(v) for v in (lower, upper))):
        if flag:
            member.reader.flag("meter_baseline_unavailable", scope, "idle edges or wall/monotonic anchor unavailable")
        return unavailable
    wall = (lower + upper) / 2 if all(finite(v) for v in (lower, upper)) else 0.0
    phase_wall = [member.origin + edge for edge in member.edges[phase]]
    phase_mono = [(edge - wall) * 1e9 for edge in phase_wall]
    baseline_mono = [(edge - wall) * 1e9 for edge in baseline] if request and baseline else []
    if controller:
        phase_mono, baseline_mono = controller
    for stream in streams:
        if not stream.times:
            continue
        offset, source = stream.offset(statistics.fmean(phase_mono), journal, scope)
        if offset is None:
            continue
        delta = bop + stream.r_max_s if finite(bop) else None
        if shifts != (0.0, 0.0) and delta is None:
            continue
        # Preserve integer controller ns for the unshifted reported window;
        # only sensitivity corners need fractional shifts in seconds.
        phase_raw = ([t + offset for t in phase_mono] if shifts == (0.0, 0.0) else
                     [t + offset + shift * (delta or 0.0) * 1e9 for t, shift in zip(phase_mono, shifts)])
        base_raw = [t + offset for t in baseline_mono]
        coverage = phase_raw + base_raw
        if phase_raw[1] <= phase_raw[0] or min(coverage) < stream.times[0] or max(coverage) > stream.times[-1]:
            continue
        meter = (sampled_term(stream.times, stream.powers, phase_raw, base_raw) if request else
                 sampled_gross(stream.times, stream.powers, phase_raw))
        if meter is None:
            continue
        activity = request_battery_activity(member, stream, wall, offset, flag)
        length = (phase_raw[1] - phase_raw[0]) / 1e9
        rail_phase = tuple(edge + shift * (delta or 0.0) for edge, shift in zip(member.edges[phase], shifts))
        gross_rail = overlap(member.records, *rail_phase)[0]
        if not request:
            energy = meter["energy_J"]
            return {"energy_J": energy, "meter": meter, "gross_rail_energy_J": gross_rail,
                    "gross_share": gross_rail / energy if energy > 0 else None, "share_label": "gross share",
                    "battery_activity": activity, "duration_s": length, "window_ns": phase_raw,
                    "offset_source": source, "stream": stream.name, "edge_delta_s": delta,
                    "label": PHASE_MACHINE_LABEL, "basis": "gross meter term only; adapter loss excluded",
                    "boundary": PHASE_MACHINE_BOUNDARY}
        battery = sampled_term(stream.battery_times, stream.battery_powers, phase_raw, base_raw)
        if battery is None and flag:
            member.reader.flag("meter_battery_unavailable", scope, {"stream": stream.name})
        machine = meter["delta_J"] + (battery["delta_J"] if battery else 0.0)
        idle = rail_idle_power(member)
        # REG 5.8's rail delta is the reducer's event-window gross energy less
        # idle over that same event duration. Controller before/after brackets
        # define the meter span, not the duration of the rail subtraction.
        rail = gross_rail - idle * (rail_phase[1] - rail_phase[0]) if finite(idle) else None
        return {"delta_J": machine, "rail_delta_J": rail,
                "rho": rail / machine if machine > 0 and finite(rail) else None,
                "meter": meter, "battery": battery, "battery_term_available": battery is not None,
                "rail_idle_baseline_W": idle, "battery_activity": activity,
                "duration_s": length, "window_ns": phase_raw, "baseline_ns": base_raw,
                "window_basis": "controller_stamps" if controller else "wall_anchor",
                "offset_source": source, "stream": stream.name, "edge_delta_s": delta,
                "metadata_idle_baseline_power_w_mean": get(member.metadata, "idle_baseline", "power_w_mean"),
                "boundary": MACHINE_BOUNDARY}
    if flag:
        member.reader.flag("meter_span_uncovered", scope, "no fitted stream covers phase and baseline")
    return unavailable


def machine_mean(repeats, quads, values, side=None):
    kept_r = [(uid, ms) for uid, ms in repeats if all(finite(get(values, m.run_id, "delta_J")) for m in ms)]
    kept_b = [(uid, ms) for uid, ms in quads if all(finite(get(values, m.run_id, "delta_J")) for m in ms)]
    scalar = lambda m: values[m.run_id]["delta_J"]
    if side is None:
        ordered = sorted(flatten(kept_r + kept_b), key=lambda m: (ordinal(m.run_id), m.run_id))
        row = reported_estimate([scalar(ms[0]) for _, ms in kept_r],
                                [statistics.fmean(scalar(m) for m in ms) for _, ms in kept_b],
                                ordered_energies=[scalar(m) for m in ordered])
        if row["mean_j"] is None and kept_r and kept_b:
            row["mean_j"] = (0.2 * statistics.fmean(scalar(ms[0]) for _, ms in kept_r)
                             + 0.8 * statistics.fmean(statistics.fmean(scalar(m) for m in ms) for _, ms in kept_b))
        row["h_j"] = None
        if row["interval"]:
            # Descriptive within-window interval: h only, no deterministic B.
            row["h_j"] = row["interval"]["h_j"]
            row["interval"].pop("B_j")
            row["interval"].pop("kind_averages_j")
        row["missing_units_by_stratum"] = {"repeat": len(repeats) - len(kept_r), "quad": len(quads) - len(kept_b)}
        members = flatten(kept_r + kept_b)
        minimum = min(len(kept_r), len(kept_b))
    else:
        means = [statistics.fmean(scalar(m) for m in ms if m.run_id.rsplit("-", 1)[-1].startswith(side))
                 for _, ms in kept_b]
        n = len(means)
        mean = statistics.fmean(means) if means else None
        h = student_quantile(n - 1) * statistics.stdev(means) / math.sqrt(n) if n >= 2 else None
        row = {"n": n, "mean_j": mean, "h_j": h,
               "lower_j": mean - h if h is not None else None, "upper_j": mean + h if h is not None else None,
               "missing_quads": len(quads) - n}
        members = [m for m in flatten(kept_b) if m.run_id.rsplit("-", 1)[-1].startswith(side)]
        minimum = n
    rhos = [values[m.run_id]["rho"] for m in members if finite(values[m.run_id].get("rho"))]
    row.update(status="computed" if minimum >= 5 else "below_registered_minimum",
               note="" if minimum >= 5 else "below the registered minimum",
               battery_unavailable_members=sum(not values[m.run_id].get("battery_term_available") for m in members),
               rho_median=statistics.median(rhos) if rhos else None, rho_n=len(rhos), boundary=MACHINE_BOUNDARY)
    return row


def diagnostic_estimate(repeats, quad_means):
    """Estimator 1's fixed stratum weights; h only, including counts below the minimum."""
    row = reported_estimate(repeats, quad_means)
    if row["mean_j"] is None and repeats and quad_means:
        row["mean_j"] = .2 * statistics.fmean(repeats) + .8 * statistics.fmean(quad_means)
    row["h_j"] = get(row, "interval", "h_j")
    if row["interval"]:
        row["interval"].pop("B_j")
        row["interval"].pop("kind_averages_j")
    row["status"] = "computed" if min(len(repeats), len(quad_means)) >= 5 else "below_registered_minimum"
    row["note"] = "" if row["status"] == "computed" else "below the registered minimum"
    return row


def step_edge(records, stamp, left_power, right_power):
    """F5 real.py 23-33, including clamp rescaling to preserve the record's energy."""
    for i, (a, b, power) in enumerate(records):
        if a < stamp < b:
            T, f = b - a, (stamp - a) / (b - a)
            gp = .5 if left_power == right_power else min(1., max(0., (power - right_power) / (left_power - right_power)))
            left = T * (min(f, gp) * left_power + max(0., f - gp) * right_power)
            right = T * (max(0., gp - f) * left_power + (1 - max(f, gp)) * right_power)
            scale = (power * T) / (left + right) if left + right > 0 else 1.
            left *= scale
            right *= scale
            return {"record": i, "f": f, "step_fraction": gp, "duration_s": T, "power_w": power,
                    "left_bias_j": f * T * power - left, "right_bias_j": (1 - f) * T * power - right,
                    "left_model_j": left, "right_model_j": right, "rescale": scale}
    # A stamp exactly on a record boundary has no allocation ambiguity.
    for i, (a, b, power) in enumerate(records):
        if stamp == a or stamp == b:
            return {"record": i, "f": 0. if stamp == a else 1., "step_fraction": None,
                    "duration_s": b - a, "power_w": power, "left_bias_j": 0., "right_bias_j": 0.,
                    "rescale": 1.}
    return None


def single_step_member(member):
    if hasattr(member, "_single_step"):
        return member._single_step
    result = {"label": RECONSTRUCTION_LABEL, "status": "not_computed", "reason": None,
              "bias_j": {}, "energy_j": {}, "edges": {}, "plateau_w": {}}
    member._single_step = result
    if not all(p in member.edges for p in ("prefill", "decode")):
        result["reason"] = "phase stamps unavailable"
        return result
    # F5 sums every equal support first, independent of whether the rails are adjacent.
    supports = {}
    for a, b, power in member.records:
        supports[(a, b)] = supports.get((a, b), 0.) + power
    records = [(a, b, p) for (a, b), p in supports.items()]
    # F5's long-prompt middle stamp is prefill end (real.py 38); the
    # brief explicitly uses the decode-start stamp for short-prompt decode.
    t0, t1, t2 = member.edges["prefill"][0], member.edges["prefill"][1], member.edges["decode"][1]
    def holding(stamp):
        return next((i for i, (a, b, _) in enumerate(records) if a <= stamp < b), None)
    i0, i1, i2 = (holding(t) for t in (t0, t1, t2))
    # F5 diagnostic support: five complete idle records before onset and
    # three after completion; edge records themselves are not idle support.
    if None in (i0, i1, i2) or i0 < 5 or i2 + 3 >= len(records):
        result["reason"] = "edge records or five idle-before / three idle-after records unavailable"
        return result
    idle_b = statistics.median(p for _, _, p in records[i0-5:i0])
    idle_a = statistics.median(p for _, _, p in records[i2+1:i2+4])
    pre_in = [p for _, _, p in records[i0+1:i1]]
    dec_in = [p for _, _, p in records[i1+1:i2]]
    # F5 uses a prefill plateau only with >=3 interior records, then drops
    # the first; decode drops both ends and needs >=3 to retain one record.
    Ppre = statistics.median(pre_in[1:]) if len(pre_in) > 2 else None
    if len(dec_in) <= 2:
        result["reason"] = "decode plateau has no interior records after dropping first and last"
        return result
    Pdec = statistics.median(dec_in[1:-1])
    result["plateau_w"] = {"idle_before": idle_b, "idle_after": idle_a, "prefill": Ppre, "decode": Pdec}
    short = Ppre is None
    if short:
        t1 = member.edges["decode"][0]
        i1 = holding(t1)
    # Short prompts have no measured prefill plateau: both onset records use idle -> decode.
    eS = step_edge(records, t0, idle_b, Pdec if short else Ppre)
    eM = step_edge(records, t1, idle_b if short else Ppre, Pdec)
    eE = step_edge(records, t2, Pdec, idle_a)
    if any(edge is None for edge in (eS, eM, eE)):
        result["reason"] = "phase edge outside trace"
        return result
    result.update(status="computed", reason=None, kind="decode42" if short else "prefill2048",
                  onset_records="same" if i0 == i1 else "different",
                  middle_stamp_basis="decode start" if short else "prefill end (F5 real.py 38)",
                  edges={"prefill_start": eS, "decode_start": eM, "decode_end": eE})
    result["bias_j"] = {"decode": eM["right_bias_j"] + eE["left_bias_j"],
                        "request": eS["right_bias_j"] + eE["left_bias_j"]}
    if not short:
        result["bias_j"]["prefill"] = eS["right_bias_j"] + eM["left_bias_j"]
    else:
        result["prefill"] = {"status": "not_computed", "reason": "prefill-p42 has no resolved prefill plateau"}
    result["energy_j"] = {phase: member.energies[phase] - bias for phase, bias in result["bias_j"].items()
                          if phase in member.energies}
    return result


def add_reconstruction(output, selections, windows):
    line = {"label": RECONSTRUCTION_LABEL, "cells": {}, "p42": {}}
    output["disclosures"]["single_step_reconstruction"] = line
    for (pack, cid), chosen in selections.items():
        if pack == "GAMMA":
            continue
        if "p42" in cid:
            line["p42"][cid] = {"label": RECONSTRUCTION_LABEL, "status": "not_computed",
                                "reason": "prefill-p42 has no resolved prefill plateau"}
            continue
        phase = "decode" if "decode" in cid else "prefill"
        members = flatten(chosen["repeat"] + chosen["quad"])
        values = {m.run_id: single_step_member(m) for m in members}
        missing = sorted(m.run_id for m in members if not finite(get(values, m.run_id, "energy_j", phase)))
        row = {"label": RECONSTRUCTION_LABEL, "phase": phase, "model": MODELS[pack],
               "kept_units": {s: [uid for uid, _ in units] for s, units in chosen.items()}, "unavailable_members": missing,
               "n_r": len(chosen["repeat"]), "n_b": len(chosen["quad"]),
               "mean_j": None, "h_j": None, "shift_j": None, "stratified_sd_ratio": None,
               "registered_estimator1_mean_j": output["reported_cells"][cid]["mean_j"]}
        line["cells"][cid] = row
        if missing:
            row.update(status="not_computed", reason="reconstruction unavailable for a kept member; units unchanged")
            continue
        original = diagnostic_estimate([ms[0].energies[phase] for _, ms in chosen["repeat"]],
            [statistics.fmean(m.energies[phase] for m in ms) for _, ms in chosen["quad"]])
        recon = diagnostic_estimate([values[ms[0].run_id]["energy_j"][phase] for _, ms in chosen["repeat"]],
            [statistics.fmean(values[m.run_id]["energy_j"][phase] for m in ms) for _, ms in chosen["quad"]])
        row.update(recon, estimator1_mean_j=original["mean_j"], estimator1_h_j=original["h_j"])
        if finite(recon["mean_j"]) and finite(original["mean_j"]):
            row["shift_j"] = recon["mean_j"] - original["mean_j"]
        # The standard deviation of estimator 1's stratified m is sqrt(V), PLAN 4 step 3.
        def stratified_sd(estimate):
            interval = estimate["interval"]
            return math.sqrt(interval["variance"]) if interval else None
        sd_recon, sd_original = stratified_sd(recon), stratified_sd(original)
        row["stratified_sd_j"] = sd_recon
        row["estimator1_stratified_sd_j"] = sd_original
        row["stratified_sd_ratio"] = sd_recon / sd_original if sd_original and sd_recon is not None else None
        row["sd_definition"] = "sqrt(V) of estimator 1's stratified mean; reconstructed / assigned"


def phase_machine_mean(repeats, quads, values):
    kept = {s: [(uid, ms) for uid, ms in units if all(finite(get(values, m.run_id, "energy_J")) for m in ms)]
            for s, units in (("repeat", repeats), ("quad", quads))}
    scalar = lambda m: values[m.run_id]["energy_J"]
    row = diagnostic_estimate([scalar(ms[0]) for _, ms in kept["repeat"]],
                              [statistics.fmean(scalar(m) for m in ms) for _, ms in kept["quad"]])
    members = flatten(kept["repeat"] + kept["quad"])
    shares = [values[m.run_id]["gross_share"] for m in members if finite(values[m.run_id].get("gross_share"))]
    flagged = sorted(m.run_id for m in flatten(repeats + quads) if get(values, m.run_id, "battery_activity", "active"))
    row.update(label=PHASE_MACHINE_LABEL, basis="gross meter term only; adapter loss excluded",
               missing_units_by_stratum={"repeat": len(repeats) - len(kept["repeat"]), "quad": len(quads) - len(kept["quad"])},
               battery_assist_count=len(flagged), battery_assist_members=flagged,
               gross_share={"label": "gross share", "median": statistics.median(shares) if shares else None, "n": len(shares)},
               boundary=PHASE_MACHINE_BOUNDARY)
    return row


def percentile(values, q):
    if not values:
        return None
    v = sorted(values)
    position = (len(v) - 1) * q / 100
    lower, upper = math.floor(position), math.ceil(position)
    return v[lower] + (v[upper] - v[lower]) * (position - lower)


def plausible_machine(row):
    rho, machine, rail = row.get("rho"), row.get("delta_J"), row.get("rail_delta_J")
    return all(finite(v) for v in (rho, machine, rail)) and 0 < rho <= 1 and machine - rail >= 0


def request_cross_check(lines):
    """PLAN 8.2, all collected members grouped by their actual model, never pooled into a claim cell."""
    result = {"label": "registered descriptive request cross-check (PLAN 8.2); never a claim number",
              "boundary": MACHINE_BOUNDARY, "windows": {}, "central_bands": {},
              "order_basis": "chronological first collected science/reference request; ties by window identifier and pack"}
    ordered = sorted(lines.items(), key=lambda item: (item[1].get("first_request_epoch_s") is None,
                     item[1].get("first_request_epoch_s") or 0, item[1]["identifier"], item[0]))
    for pack, line in ordered:
        meter_flags = objects(line.get("meter_flags"))
        window_flags = [f for f in meter_flags if f.get("code") != "meter.battery_activity"]
        battery_ids = {get(f, "scope", "run_id") for f in meter_flags if f.get("code") == "meter.battery_activity"}
        battery_ids.update(rid for rid, m in line.get("members", {}).items()
                           if get(m, "phases", "request", "battery_activity", "active"))
        clean = line.get("reason") != "meter_absent" and not window_flags and not battery_ids
        groups = {}
        for rid, member in line.get("members", {}).items():
            row = get(member, "phases", "request", default={})
            if not all(finite(row.get(k)) for k in ("delta_J", "rail_delta_J")):
                continue
            groups.setdefault(member.get("model") or "unknown", []).append((rid, row))
        record = {"identifier": line["identifier"], "clean": clean, "models": {}, "boundary": MACHINE_BOUNDARY}
        result["windows"][pack] = record
        for model, members in sorted(groups.items()):
            rhos = [m["rho"] for _, m in members if finite(m.get("rho"))]
            plausible = [m["rho"] for _, m in members if plausible_machine(m)]
            median = statistics.median(plausible) if plausible else None
            spread = (max(plausible) - min(plausible)) / median if median is not None else None
            outside = [{"run_id": rid, "delta_J": row["delta_J"], "rail_delta_J": row["rail_delta_J"], "rho": row.get("rho"),
                        "member_battery_activity": rid in battery_ids,
                        "meter_flags": window_flags + [f for f in meter_flags
                            if f.get("code") == "meter.battery_activity" and get(f, "scope", "run_id") == rid],
                        "raw_battery_activity": row.get("battery_activity"), "removed_by_this_check": False}
                       for rid, row in members if not plausible_machine(row)]
            # PLAN 8.2 fixes descriptive "consistent" at spread <=0.2; this
            # registered label excludes nothing and is not an agreement bar.
            summary = {"n_members": len(members), "rho_n": len(rhos), "rho_median": statistics.median(rhos) if rhos else None,
                       "rail_delta_median_J": statistics.median(row["rail_delta_J"] for _, row in members),
                       "machine_delta_median_J": statistics.median(row["delta_J"] for _, row in members),
                       "rho_min": min(rhos) if rhos else None, "rho_max": max(rhos) if rhos else None,
                       "rho_iqr": [percentile(rhos, 25), percentile(rhos, 75)],
                       "outside_hard_band": outside, "plausible_n": len(plausible),
                       "within_model_spread": spread,
                       # PLAN 8.2's 20% descriptive spread threshold.
                       "consistency": "consistent" if spread is not None and spread <= .2 else (
                           "not consistent" if spread is not None else "not computed"), "boundary": MACHINE_BOUNDARY}
            if clean and plausible and model not in result["central_bands"]:
                result["central_bands"][model] = {"window_identifier": line["identifier"], "pack": pack,
                                                 "rho_min": min(plausible), "rho_max": max(plausible)}
            band = result["central_bands"].get(model)
            if band:
                inside = sum(band["rho_min"] <= rho <= band["rho_max"] for rho in rhos)
                summary["central_band"] = {**band, "inside_n": inside, "n": len(members),
                    "note": "sets the first clean window's band" if band["pack"] == pack else
                            f"{inside} of {len(members)} member windows inside the first clean window's band"}
            else:
                summary["central_band"] = {"note": "no clean analysed window with plausible values for this model; no central band is set"}
            record["models"][model] = summary
    result["note"] = ("no window is clean; no central band is set" if not any(w["clean"] for w in result["windows"].values())
                      else "central bands use each model's first clean analysed window with plausible values")
    return result


def add_machine(output, selections, windows, meter_dir=None):
    disclosure = {"label": "descriptive; never a claim number", "boundary": MACHINE_BOUNDARY, "windows": {}}
    output["disclosures"]["whole_machine"] = disclosure
    for pack, w in windows.items():
        directory = Path(meter_dir) if meter_dir else w.archive / "sources/night-custody/hazards/meter"
        paths = sorted(directory.glob("stream-*.jsonl"))
        if not paths:
            compressed = [p.name for p in sorted(directory.glob("stream-*.jsonl.zst"))]
            detail = {"reason": "meter_stream_compressed" if compressed else "meter_absent",
                      "compressed_inputs": compressed}
            if compressed:
                detail.update(RESTORE_TOOL_DETAIL)
            w.reader.flag("meter_absent", "whole_machine", detail)
            disclosure["windows"][pack] = {"status": "not_computed", "reason": "meter_absent", "boundary": MACHINE_BOUNDARY,
                                           "input_detail": detail,
                                           "identifier": w.harvest.get("plan_id", w.archive.name)}
            continue
        streams = [MeterStream(p, w.reader) for p in paths]
        clock_path = w.archive / "sources/night-custody/hazards/monitor/clock.jsonl"
        journal = w.reader.lines(clock_path, "meter/clock_journal") if clock_path.exists() else []
        line = {"members": {}, "cells": {}, "streams": {s.name: {"fit": s.fit, "r_max_s": s.r_max_s} for s in streams},
                "meter_flags": [f for f in w.flag_rows if str(f.get("code", "")).startswith("meter.")],
                "boundary": MACHINE_BOUNDARY, "identifier": w.harvest.get("plan_id", w.archive.name),
                "first_request_epoch_s": None}
        disclosure["windows"][pack] = line
        # Request cross-check covers every collected member, including removed and corpus members.
        recorded = w.reader.json(w.archive / "withheld/meter.json", "withheld/meter.json", False)
        collected = {m["run_id"]: m for m in objects(w.roster.get("members")) if isinstance(m.get("run_id"), str)}
        for rid in mapping(recorded.get("members")):
            collected.setdefault(rid, {})
        for rid, roster in sorted(collected.items()):
            if Path(rid).name != rid or rid in (".", ".."):
                continue
            which = "corpus" if role(rid) == "corpus" else ("science" if roster.get("kind") == "science" else role(rid))
            root = w.bound_root if which == "corpus" else w.claim_root
            if not (root / rid / "metadata.json").is_file():
                continue
            member = w.member(rid, which)
            if which != "corpus" and "request" in member.edges:
                start = member.origin + member.edges["request"][0]
                old = line["first_request_epoch_s"]
                line["first_request_epoch_s"] = min(start, old) if old is not None else start
            values = {phase: machine_member(member, phase, streams, journal, w.b["b_op_s"])
                      for phase in (("request",) if pack == "GAMMA" else ("request", "decode", "prefill"))}
            request_activity = get(values, "request", "battery_activity", default={})
            archived_activity = any(f.get("code") == "meter.battery_activity" and get(f, "scope", "run_id") == rid
                                    for f in w.flag_rows)
            for phase in ("decode", "prefill"):
                if phase in values:
                    values[phase]["battery_activity"] = {**request_activity,
                        "active": bool(request_activity.get("active") or archived_activity)}
            line["members"][rid] = {"model": member.model, "phases": values}
            stored = get(recorded, "members", rid, "machine")
            if isinstance(stored, dict):
                own = values["request"]
                if own.get("status") == "not_compared":
                    own["recorded_comparison"] = {"status": "not_compared", "matches": None, "reason": own["reason"]}
                    continue
                mismatch = []
                for keys in (("delta_J",), ("meter", "energy_J"), ("meter", "baseline_W")):
                    actual, expected = get(own, *keys), get(stored, *keys)
                    # Agreement policy: unrounded J/W, 1e-6 relative / absolute near zero.
                    if not agrees(actual, expected):
                        mismatch.append("/".join(keys))
                for field in ("rail_delta_J", "rho"):
                    actual, expected = own.get(field), get(recorded, "members", rid, field)
                    # Rho: 1e-6 absolute, 1% of four-decimal resolution; rail: J.
                    if not (actual is None and expected is None) and not agrees(actual, expected, ratio=field == "rho"):
                        mismatch.append(field)
                # Counts exact: +/-2 samples at 50 Hz spans 40 ms and cannot
                # guarantee the agreement policy's energy bar. Fit uncertainty is carried by
                # edge sensitivity, never by accepting a changed sample set.
                for keys in (("meter", "n"), ("battery", "n")):
                    actual, expected = get(own, *keys), get(stored, *keys)
                    if actual != expected:
                        mismatch.append("/".join(keys))
                for index, name in enumerate(("window_start_ns", "window_end_ns")):
                    own_window, stored_window = own.get("window_ns"), stored.get("window_ns")
                    actual = own_window[index] if isinstance(own_window, (list, tuple)) and len(own_window) > index else None
                    expected = stored_window[index] if isinstance(stored_window, (list, tuple)) and len(stored_window) > index else None
                    # Controller stamps are identical quantized integer-ns
                    # inputs. Legacy wall placement instead compares the edge
                    # difference in seconds at the agreement policy's 1e-6 absolute near zero.
                    # Neither grants energy/count slack from the fit bound or
                    # the 20 ms meter period: those strict checks still apply.
                    same = (actual == expected if own.get("window_basis") == "controller_stamps" else
                            all(finite(v) for v in (actual, expected)) and agrees((actual - expected) / 1e9, 0.0))
                    if not same:
                        mismatch.append(name)
                values["request"]["recorded_comparison"] = {"status": "compared", "matches": not mismatch,
                                                             "mismatched_fields": mismatch}
                if mismatch:
                    cause = "anchor unknown: independently placed rail energy differs" if not member.usable else "raw recomputation differs from withheld record"
                    w.reader.flag("meter_request_mismatch", rid, {"fields": mismatch, "cause": cause,
                        "rail_difference_J": own.get("rail_delta_J") - get(recorded, "members", rid, "rail_delta_J")
                        if all(finite(v) for v in (own.get("rail_delta_J"), get(recorded, "members", rid, "rail_delta_J"))) else None})
        for (selected_pack, cid), chosen in selections.items():
            if selected_pack != pack or pack == "GAMMA":
                continue
            phase = "decode" if "decode" in cid else "prefill"
            repeats, quads = chosen.get("repeat", []), chosen["quad"]
            values = {rid: get(row, "phases", phase, default={}) for rid, row in line["members"].items()}
            sides = (None,)
            for side in sides:
                key = cid + ("/" + SIDE_MODELS[side] if side else "")
                cell = phase_machine_mean(repeats, quads, values)
                cell["phase"] = "prefill-p42" if "p42" in cid else ("decode" if phase == "decode" else "prefill-p2048")
                if "p42" in cid:
                    cell["label"] = "diagnostic: gross prefill-p42 meter energy; about four meter samples"
                shifts = []
                for on, off in itertools.product((-1, 1), repeat=2):
                    shifted = {m.run_id: machine_member(m, phase,
                               [s for s in streams if s.name == values[m.run_id].get("stream")],
                               journal, w.b["b_op_s"], (on, off), False)
                               for m in flatten(repeats + quads) if finite(get(values, m.run_id, "energy_J"))}
                    changed = phase_machine_mean(repeats, quads, shifted)
                    mean, primary = changed.get("mean_j"), cell.get("mean_j")
                    # A sensitivity cannot silently switch its units when a shifted edge loses coverage.
                    count_keys = ("n",) if side else ("n_r", "n_b")
                    valid = all(changed.get(k) == cell.get(k) for k in count_keys)
                    shifts.append({"on_sign": on, "off_sign": off,
                                   "change_j": mean - primary if valid and all(finite(v) for v in (mean, primary)) else None})
                cell["edge_shift_sensitivity"] = {"label": "edge-shift sensitivity (b_op + clock-fit residual)",
                    "corners": shifts, "max_abs_change_j": max(abs(v["change_j"]) for v in shifts)
                    if all(finite(v["change_j"]) for v in shifts) else None}
                line["cells"][key] = cell
    disclosure["request_cross_check"] = request_cross_check(disclosure["windows"])


def sensitivity_bound(windows):
    pins = {pack: w.reader.json(w.archive / "derived/terminal-pin.json", "derived/terminal-pin.json")
            for pack, w in windows.items()}
    terminal = [(p.get("sequence"), pack) for pack, p in pins.items() if positive_int(p.get("sequence"))]
    result = {"label": "sensitivity", "B_max_s": None, "attaining_sequence": None, "T": None, "windows": {}}
    if not terminal:
        return result
    T, pack = max(terminal)
    window = windows[pack]
    r = window.reader
    acceptance_relative = "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"
    acceptances = sorted((window.archive / "sources/repo/configs/calibration").glob("calibration_acceptance*.json"))
    # The registered acceptance id, rather than a glob's first draft, owns the epoch.
    acceptance = next((a for p in acceptances if (a := r.json(p, "calibration_acceptance"))
                       .get("acceptance_id") == "d079_calibration_acceptance_v2_n24_25g83_r2"), {})
    source = "archive"
    if not acceptance:
        # E3 item 14 fixes the block's issued acceptance; S10 does not archive it.
        acceptance = r.json(Path(__file__).resolve().parents[1] / acceptance_relative, "calibration_acceptance")
        source = "analysis_checkout"
    members = objects(get(acceptance, "derivation_corpus", "members"))
    epoch = acceptance.get("identity_epoch")
    ledger = r.lines(window.archive / "sources/ledger/calibration_observation_ledger.jsonl", "calibration_ledger")
    candidates = []
    for member in members:
        value, member_id = number(member.get("b_fiducial_s")), member.get("member_id")
        if value is None:
            continue
        sequences = [row["sequence"] for row in ledger if positive_int(row.get("sequence"))
                     and row["sequence"] <= 376 and row.get("attempt_id") == member_id
                     and row.get("identity_epoch") == epoch and row.get("disposition") == "valid"
                     and number(row.get("exact_bound_lexeme_s")) == value]
        candidates.append((value, min(sequences) if sequences else None, member_id))
    for row in ledger:
        seq = row.get("sequence")
        if (positive_int(seq) and 376 < seq <= T and row.get("identity_epoch") == epoch
                and row.get("disposition", row.get("class")) in ("valid", "systematic-invalid")):
            value = number(row.get("exact_bound_lexeme_s", row.get("b_fiducial_s")))
            if value is not None:
                candidates.append((value, seq, row.get("attempt_id")))
    if len(members) != 24 or not epoch or not candidates or not ledger:
        r.flag("sensitivity_inputs_unavailable", "sensitivity", "need acceptance's 24 members, epoch and archived ledger")
        return {**result, "T": T}
    # Ties disclose the earliest attaining ledger sequence, or the acceptance member.
    maximum = max(v for v, _, _ in candidates)
    winners = sorted((c for c in candidates if c[0] == maximum), key=lambda c: (c[1] is None, c[1] or 0, c[2] or ""))
    _, sequence, member_id = winners[0]
    result.update(B_max_s=maximum, attaining_sequence=sequence, attaining_member=member_id, T=T,
                  acceptance_source=source)
    for pack, window in windows.items():
        operative = window.b["b_op_s"]
        bound = max(operative, maximum) if finite(operative) else None
        result["windows"][pack] = {"b_sens_s": bound, "equals_primary_bound": bound == operative,
                                  "note": "sensitivity values equal primary" if bound == operative else "bound widened"}
    return result


def add_sensitivity(output, selections, windows, diagnostic):
    line = sensitivity_bound(windows)
    line.update(reported_cells={}, floors={}, floor_cells={}, contrasts={})
    output["disclosures"]["sensitivity_bound"] = line
    if not finite(line["B_max_s"]):
        line.update(status="not_computed", reason="sensitivity_inputs_unavailable")
        return
    rows, operands = {}, {}
    for (pack, cid), chosen in selections.items():
        if "p42" in cid:
            continue
        w = windows[pack]
        bound = line["windows"][pack]["b_sens_s"]
        phase = "decode" if "decode" in cid else "prefill"
        if not finite(bound):
            continue
        if pack != "GAMMA":
            reported = make_reported(w, cid, chosen["repeat"], chosen["quad"], None if diagnostic else 5, bound)
            line["reported_cells"][cid] = reported
            forms, cell = make_floors(w, phase, chosen, reported, bound)
            prefix = MODELS[pack] + "/" + phase
            line["floor_cells"][prefix] = cell
            for form, floor in forms.items():
                line["floors"][prefix + "/" + form] = floor
        else:
            row, kinds, _, _ = contrast_inputs(w, chosen["quad"], phase, bound)
            missing = len(chosen["quad"]) < len(strings(get(w.exclusion_cells.get(cid, {}), "kept_units", "quad")))
            if not diagnostic and (row["n"] < 5 or missing):
                row["p"] = 1.0
            rows[cid], operands[cid] = row, (phase, kinds, missing and not diagnostic)
    if set(windows) != {"ALPHA", "BETA", "GAMMA"}:
        line["contrasts"] = missing_pack()
        return
    for cid, row in rows.items():
        phase, kinds, missing = operands[cid]
        floor = contrast_floor(line["floor_cells"], phase)
        other = next((r["p"] for c, r in rows.items() if c != cid), 1.0)
        ids = [u for u, _ in selections[("GAMMA", cid)]["quad"]]
        contrast = finish_contrast(row, other, floor["floor_gate_j"], ids, kinds,
                                   2 if diagnostic else 5, missing)
        # The sensitivity registers an outcome word, not a second LOO ceiling.
        for key in ("loo", "loo_verdict_influential", "loo_magnitude_influential", "ceiling"):
            contrast.pop(key, None)
        contrast["floor"] = floor
        contrast["outcome_equals_primary"] = contrast["outcome"] == output["contrasts"][cid]["outcome"]
        line["contrasts"][cid] = contrast


def reference_scale_basis(window):
    members = [window.members[rid] for rid in window.neg8["survivor_ids"]
               if rid in window.members and window.members[rid].usable
               and window.members[rid].model == "Qwen2.5-1.5B-Instruct-4bit"
               and finite(window.members[rid].energies.get("request"))]
    return {"label": SCALED_ALLOWANCE_LABEL, "reference_ids": [m.run_id for m in members], "n": len(members),
            "E_ref_j": statistics.fmean(m.energies["request"] for m in members) if members else None,
            "T_ref_s": statistics.fmean(m.edges["request"][1] - m.edges["request"][0] for m in members) if members else None,
            "allowance_j": window.neg8["allowance_j"]}


def allowance_factor(energy, duration, basis):
    Eref, Tref = basis["E_ref_j"], basis["T_ref_s"]
    if not all(finite(v) for v in (energy, duration, Eref, Tref)) or min(Eref, Tref) <= 0:
        return None
    return max(1., energy / Eref, duration / Tref)


def scaled_reported(primary, factor, allowance):
    result = {**primary, "label": SCALED_ALLOWANCE_LABEL, "factor": factor,
              "registered_allowance_j": allowance, "scaled_allowance_j": allowance * factor
              if all(finite(v) for v in (allowance, factor)) else None}
    if primary["interval"] and finite(result["scaled_allowance_j"]):
        kinds = list(primary["interval"]["kind_averages_j"])
        kinds[2] = result["scaled_allowance_j"] / 2
        if not all(finite(value) for value in kinds):
            return {**result, "status": "not_computed", "reason": "registered bound term unavailable"}
        B = math.fsum(kinds)
        result["interval"] = {**primary["interval"], "kind_averages_j": kinds, "B_j": B}
        result["lower_j"] = primary["mean_j"] - primary["interval"]["h_j"] - B
        result["upper_j"] = primary["mean_j"] + primary["interval"]["h_j"] + B
    else:
        result.update(status="not_computed", reason="cell mean or reference scale basis unavailable")
    return result


def scaled_floor(primary, factor):
    allowance = primary["allowance_j"]
    scaled = allowance * factor if all(finite(v) for v in (allowance, factor)) else None
    guarded = primary["guarded_floor_j"]
    minted = guarded + scaled if all(finite(v) for v in (guarded, scaled)) else None
    return {**primary, "label": SCALED_ALLOWANCE_LABEL, "factor": factor, "registered_allowance_j": allowance,
            "registered_minted_floor_j": primary["drift_widened_guarded_floor_j"],
            "allowance_j": scaled, "scaled_allowance_j": scaled, "drift_widened_guarded_floor_j": minted}


def scaled_gamma_inputs(window, quads, phase, basis):
    registered, kinds, a, b = contrast_inputs(window, quads, phase)
    sides = {}
    for side, energies in (("a", a), ("b", b)):
        members = [m for m in flatten(quads) if m.run_id.rsplit("-", 1)[-1].startswith(side)]
        energy = statistics.fmean(energies) if energies else None
        duration = statistics.fmean(m.edges[phase][1] - m.edges[phase][0] for m in members) if members else None
        factor = allowance_factor(energy, duration, basis)
        allowance = window.neg8["allowance_j"]
        sides[side] = {"model": SIDE_MODELS[side], "E_j": energy, "T_s": duration, "factor": factor,
                       "registered_allowance_j": allowance, "scaled_allowance_j": allowance * factor
                       if all(finite(v) for v in (allowance, factor)) else None}
    factors = [side["factor"] for side in sides.values()]
    factor = max(factors) if all(finite(v) for v in factors) else None
    scaled_kinds = [[*k[:2], k[2] * factor if all(finite(v) for v in (k[2], factor)) else None] for k in kinds]
    terms = [statistics.fmean(k[j] for k in scaled_kinds)
             if scaled_kinds and all(finite(k[j]) for k in scaled_kinds) else None for j in range(3)]
    D = math.fsum(terms) if all(finite(v) for v in terms) else None
    return {**contrast_stats(registered["d_k"], D), "label": SCALED_ALLOWANCE_LABEL, "factor": factor,
            "E_a_j": sides["a"]["E_j"], "E_b_j": sides["b"]["E_j"],
            "T_a_s": sides["a"]["T_s"], "T_b_s": sides["b"]["T_s"], "sides": sides,
            "registered_allowance_j": window.neg8["allowance_j"], "scaled_allowance_j": terms[2],
            "registered_D_j": registered["D_j"], "registered_D_terms_j": registered["D_terms_j"],
            "D_terms_j": terms}, scaled_kinds


def add_scaled_allowance(output, selections, windows, diagnostic=False):
    line = {"label": SCALED_ALLOWANCE_LABEL, "windows": {p: reference_scale_basis(w) for p, w in windows.items()},
            "reported_cells": {}, "floors": {}, "floor_cells": {}, "contrasts": {}, "decision_vs_floor": {}}
    output["disclosures"]["scaled_allowance"] = line
    gamma_rows = {}
    for (pack, cid), chosen in selections.items():
        if "p42" in cid:
            continue
        phase = "decode" if "decode" in cid else "prefill"
        w = windows[pack]
        basis = line["windows"][pack]
        if pack == "GAMMA":
            gamma_rows[cid] = scaled_gamma_inputs(w, chosen["quad"], phase, basis)
            continue
        primary = output["reported_cells"][cid]
        members = flatten(chosen["repeat"] + chosen["quad"])
        duration = statistics.fmean(m.edges[phase][1] - m.edges[phase][0] for m in members) if members else None
        factor = allowance_factor(primary["mean_j"], duration, basis)
        line["reported_cells"][cid] = {**scaled_reported(primary, factor, w.neg8["allowance_j"]),
                                       "E_j": primary["mean_j"], "T_s": duration}
        prefix = MODELS[pack] + "/" + phase
        for form in ("absolute", "comparative"):
            key = prefix + "/" + form
            line["floors"][key] = scaled_floor(output["floors"][key], factor)
        absolute = line["floors"][prefix + "/absolute"]["drift_widened_guarded_floor_j"]
        comparative = line["floors"][prefix + "/comparative"]["drift_widened_guarded_floor_j"]
        line["floor_cells"][prefix] = {"label": SCALED_ALLOWANCE_LABEL, "factor": factor, "floor_abs_j": absolute,
            "floor_cmp_j": comparative, "floor_gate_j": max(absolute, comparative)
            if all(finite(v) for v in (absolute, comparative)) else None,
            "registered": output["floor_cells"][prefix]}
    for cid, (row, kinds) in gamma_rows.items():
        phase = "decode" if "decode" in cid else "prefill"
        floor = contrast_floor(line["floor_cells"], phase)
        primary = get(output, "contrasts", cid)
        if primary is None:
            line["contrasts"][cid] = {**row, "floor": floor, "status": "not_computed", "reason": "pack_missing"}
            continue
        row["p"] = primary["p"]
        other_p = next((c["p"] for key, c in output["contrasts"].items() if key != cid), 1.0)
        chosen = selections[("GAMMA", cid)]["quad"]
        declared_n = len(strings(get(windows["GAMMA"].exclusion_cells.get(cid, {}), "kept_units", "quad")))
        missing = not diagnostic and len(chosen) < declared_n
        contrast = finish_contrast(row, other_p, floor["floor_gate_j"], [u for u, _ in chosen], kinds,
                                   2 if diagnostic else 5, missing)
        # As for the timing-bound sensitivity, this line issues no second LOO ceiling.
        for key in ("loo", "loo_verdict_influential", "loo_magnitude_influential", "ceiling"):
            contrast.pop(key, None)
        contrast.update(floor=floor, registered_outcome=primary["outcome"],
                        registered_decision_interval_j=primary["decision_interval_j"],
                        outcome_equals_primary=contrast["outcome"] == primary["outcome"])
        line["contrasts"][cid] = contrast
        line["decision_vs_floor"][cid] = decision_beyond_floor(contrast, floor["floor_gate_j"])


def alternative_allowance(window):
    excluded = sorted(set(window.neg8["survivor_ids"]) & window.excluded)
    result = {"label": "sensitivity: drift allowance without references named by excluded_reference_in_screen",
              "registered_allowance_j": window.neg8["allowance_j"], "excluded_reference_ids": excluded,
              "tripwire": "excluded_reference_in_screen" if excluded else None,
              "note": "excluded references removed from the screen" if excluded else "no excluded reference in the screen"}
    ids = [rid for rid in window.neg8["survivor_ids"] if rid not in excluded]
    refs = {slot: [window.members[rid].energies.get("request") for rid in ids
                   if window.reference_slots[rid] == slot and rid in window.members and window.members[rid].usable
                   and window.members[rid].model == "Qwen2.5-1.5B-Instruct-4bit"] for slot in ("start", "midpoint", "end")}
    counts = {slot: sum(window.reference_slots[rid] == slot for rid in ids) for slot in refs}
    result.update(survivor_ids=ids, corpus_n=window.neg8["corpus_n"],
                  n_start=counts["start"], n_mid=counts["midpoint"], n_end=counts["end"],
                  allowance_j=None, bound_j=None, spread_j=None, difference_j=None)
    corpus = ([window.members[rid].energies["request"] for rid in window.neg8["corpus_ids"]]
              if len(window.neg8["corpus_ids"]) == window.neg8["corpus_n"] else [])
    bound = neg8_bound(corpus, counts["start"], counts["end"])
    if bound and all(len(refs[k]) == counts[k] and all(finite(v) for v in refs[k]) for k in refs):
        result.update(bound)
        means = {k: statistics.fmean(v) if v else None for k, v in refs.items()}
        result.update(start_mean_j=means["start"], midpoint_j=means["midpoint"], end_mean_j=means["end"])
        result["spread_j"], result["allowance_j"] = drift_allowance(means["start"], means["midpoint"], means["end"], bound["bound_j"])
    if not excluded:
        result["allowance_j"] = window.neg8["allowance_j"]
    if all(finite(v) for v in (result["allowance_j"], result["registered_allowance_j"])):
        result["difference_j"] = result["allowance_j"] - result["registered_allowance_j"]
    return result


def add_alternative_allowance(output, windows):
    line = {"label": "sensitivity: drift allowance with and without excluded screen references", "windows": {}}
    output["disclosures"]["excluded_reference_allowance"] = line
    for pack, w in windows.items():
        record = alternative_allowance(w)
        record["floors"] = {}
        for key, primary in output["floors"].items():
            if not key.startswith(MODELS.get(pack, "__gamma__") + "/"):
                continue
            guarded = primary["guarded_floor_j"]
            record["floors"][key] = {"registered_minted_floor_j": primary["drift_widened_guarded_floor_j"],
                "alternative_minted_floor_j": guarded + record["allowance_j"]
                if all(finite(v) for v in (guarded, record["allowance_j"])) else None}
        line["windows"][pack] = record


def floor_sample(window, chosen, phase, form):
    units = chosen["repeat" if form == "absolute" else "quad"]
    if form == "absolute":
        return [ms[0].energies[phase] for _, ms in units], [phase_bound(ms[0], phase) for _, ms in units]
    splits = [common_width(ms, phase, window.b["b_op_s"]) for _, ms in units]
    return [quad_difference(ms, phase, True) for _, ms in units], [s["width_j"] if s else None for s in splits]


def flag_counts(rows):
    counts = {}
    for row in rows:
        code = row.get("code") if isinstance(row.get("code"), str) else "unknown"
        counts[code] = counts.get(code, 0) + 1
    return dict(sorted(counts.items()))


def beta_floor_quantities(window, selections):
    result = {"floors": {}, "floor_cells": {}}
    for cid, chosen in selections.items():
        phase = "decode" if "decode" in cid else "prefill"
        reported = make_reported(window, cid, chosen["repeat"], chosen["quad"])
        forms, cell = make_floors(window, phase, chosen, reported)
        prefix = MODELS["BETA"] + "/" + phase
        result["floor_cells"][prefix] = cell
        for form, floor in forms.items():
            result["floors"][prefix + "/" + form] = {**floor, "minted_floor_j": floor["drift_widened_guarded_floor_j"], **cell}
    return result


def flag_stops_comparison(flag, windows):
    if flag["code"] not in STOP_FLAG_CODES:
        return False
    if flag["code"] in TRACE_STOP_FLAG_CODES:
        # A trace failure on an excluded/detail-only run is recorded without
        # stopping a comparison whose selected inputs do not include that run.
        return any(flag["pack"] == w.pack and flag["scope"] in w.compared_run_ids
                   for w in windows.values())
    return True


def member_comparison_report(windows):
    comparisons = {key: {rid: m.comparison for rid, m in sorted(window.members.items())}
                   for key, window in windows.items()}

    def summarize(rows):
        reasons = {}
        for row in rows:
            if row["status"] == "not_compared":
                reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
        return {"compared_runs": sum(row["status"] == "compared" for row in rows),
                "not_compared_runs": sum(reasons.values()), "not_compared_by_reason": reasons}

    selected, detail_only = [], []
    for key, window in windows.items():
        for rid, row in comparisons[key].items():
            (selected if rid in window.compared_run_ids else detail_only).append(row)
    return {"members": comparisons, "summary": summarize(selected),
            "detail_only_runs": {"count": len(detail_only), **summarize(detail_only)}}


def add_beta_inclusive(output, registered, extras):
    """Extras have isolated readers/flags and cannot mutate any registered output or selection."""
    line = {"label": BETA_INCLUSIVE_LABEL, "sessions": [], "pooled": {"floors": {}, "floor_cells": {}},
            "cli_form": "repeat --extra-beta ARCHIVE [CLAIM_ROOT [BOUND_ROOT]]; '-' uses the archive default"}
    output["disclosures"]["beta_including_removed_sessions"] = line
    sessions = []
    if registered is not None:
        sessions.append(registered)
    sessions.extend(extras)
    chosen_sessions = []
    for index, w in enumerate(sessions):
        selections = {c["cell_id"]: {s: w.select(c["cell_id"], s) for s in ("repeat", "quad")}
                      for c in objects(w.roster.get("cells")) if isinstance(c.get("cell_id"), str)
                      and "p42" not in c["cell_id"] and c["cell_id"].endswith("-qwen3-8b")}
        identifier = w.harvest.get("plan_id", w.archive.name)
        chosen_sessions.append((w, identifier, selections))
        quantities = beta_floor_quantities(w, selections)
        if w is not registered:
            line["sessions"].append({"identifier": identifier, "archive": str(w.archive),
                "attempt": w.exclusions.get("attempt", w.harvest.get("attempt")),
                "claim_usable": w.exclusions.get("claim_usable"), "allowance_j": w.neg8["allowance_j"],
                "b_op_s": w.b["b_op_s"], "harvest_flags": w.flag_rows, "harvest_flag_counts": flag_counts(w.flag_rows),
                "script_flags": w.reader.flags, "script_flag_counts": flag_counts(w.reader.flags), **quantities})
    allowances = [w.neg8["allowance_j"] for w, _, _ in chosen_sessions]
    allowance = max(allowances) if allowances and all(finite(a) for a in allowances) else None
    line["pooled"]["allowance_j"] = allowance
    line["pooled"]["session_allowances"] = [{"identifier": identifier, "allowance_j": w.neg8["allowance_j"]}
                                           for w, identifier, _ in chosen_sessions]
    cids = sorted({cid for _, _, chosen in chosen_sessions for cid in chosen})
    for cid in cids:
        phase = "decode" if "decode" in cid else "prefill"
        prefix = MODELS["BETA"] + "/" + phase
        forms = {}
        for form in ("absolute", "comparative"):
            values, widths, units = [], [], []
            for w, identifier, selected in chosen_sessions:
                if cid not in selected:
                    continue
                v, a = floor_sample(w, selected[cid], phase, form)
                values.extend(v)
                widths.extend(a)
                units.extend({"identifier": identifier, "unit_id": uid, "b_op_s": w.b["b_op_s"]}
                             for uid, _ in selected[cid]["repeat" if form == "absolute" else "quad"])
            floor = pooled_floor_estimate(values, widths, form)
            guarded = floor["guarded_floor_j"]
            minted = guarded + allowance if all(finite(v) for v in (guarded, allowance)) else None
            floor.update(label=BETA_INCLUSIVE_LABEL, allowance_j=allowance, minted_floor_j=minted,
                         drift_widened_guarded_floor_j=minted, units=units)
            forms[form] = floor
        absolute, comparative = (forms[f]["minted_floor_j"] for f in ("absolute", "comparative"))
        cell = {"floor_abs_j": absolute, "floor_cmp_j": comparative,
                "floor_gate_j": max(absolute, comparative) if all(finite(v) for v in (absolute, comparative)) else None}
        line["pooled"]["floor_cells"][prefix] = {"label": BETA_INCLUSIVE_LABEL, **cell}
        for form, floor in forms.items():
            line["pooled"]["floors"][prefix + "/" + form] = {**floor, **cell}


def recompute(windows, flags, member_detail=False, diagnostic=False, meter_dir=None):
    output = {"schema": SCHEMA, "mode": "DIAGNOSTIC_NOT_REGISTERED" if diagnostic else "REGISTERED",
              "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "interpreter": {"implementation": platform.python_implementation(), "version": platform.python_version()},
              "exclusions_rederivation": {pack: window.exclusion_check for pack, window in windows.items()},
              "inputs": {}, "windows": {}, "reported_cells": {}, "p42": {}, "floors": {},
              "floor_gate": {}, "floor_cells": {}, "floor_gate_unguarded": {}, "dominance": {}, "contrasts": {},
              "descriptive": {}, "disclosures": {"load_sensitivity": {}, "battery_assist": {},
                                                 "cross_window": {}, "decision_vs_floor": {}}}
    selections = {}
    for pack, window in windows.items():
        output["windows"][pack] = {**window.b, "neg8": window.neg8, "plan_tree_binding": window.plan_binding}
        for cell in objects(window.roster.get("cells")):
            cid = cell.get("cell_id")
            if not isinstance(cid, str):
                window.reader.flag("unit_shape_invalid", "roster/cells", "cell id must be a string")
                continue
            tag = "qwen3-1p7b" if pack == "ALPHA" else "qwen3-8b"
            if pack != "GAMMA" and not cid.endswith("-" + tag):
                window.reader.flag("kept_unit_identity_mismatch", cid, "cell model disagrees with pack")
                continue
            strata = ("quad",) if pack == "GAMMA" else ("repeat", "quad")
            chosen = {s: window.select(cid, s) for s in strata}
            selections[(pack, cid)] = chosen
            if pack == "GAMMA":
                continue
            if "p42" in cid:
                output["p42"][cid] = {"status": "expected_unresolvable", "members_with_3plus_records":
                    sum(m.counts.get("prefill", 0) >= 3 for s in strata for m in flatten(chosen[s]))}
                continue
            phase = "decode" if "decode" in cid else "prefill"
            model = MODELS[pack]
            reported = make_reported(window, cid, chosen["repeat"], chosen["quad"], None if diagnostic else 5)
            output["reported_cells"][cid] = reported
            forms, floor_cell = make_floors(window, phase, chosen, reported)
            for form, result in forms.items():
                output["floors"][model + "/" + phase + "/" + form] = result
            output["floor_cells"][model + "/" + phase] = floor_cell
            output["floor_gate"][model + "/" + phase] = floor_cell["floor_gate_j"]
            fs = list(forms.values())
            output["floor_gate_unguarded"][model + "/" + phase] = (max(f["operative_unguarded_floor_j"] for f in fs)
                if all(finite(f["operative_unguarded_floor_j"]) for f in fs) else None)
    complete = set(windows) == {"ALPHA", "BETA", "GAMMA"}
    if not complete:
        flags.append({"code": "pack_missing", "pack": "", "scope": "aggregate",
                      "detail": {"missing": sorted({"ALPHA", "BETA", "GAMMA"} - set(windows))}})
    ratios, common, failed = {}, {}, []
    if complete or diagnostic:
        for key, floor in output["floors"].items():
            denominator = floor["point_unguarded_floor_j"]
            if denominator == 0:
                flags.append({"code": "dominance_ratio_zero_denominator", "pack": "", "scope": key,
                              "detail": "point floor is zero"})
            ratio = floor["R"]
            # PLAN 6 fixes branch dominance at R>=2 (a doubled point floor).
            ratios[key] = {"numerator_j": floor["corner_widened_unguarded_floor_j"], "denominator_j": denominator,
                           "R": ratio, "pass": finite(ratio) and ratio >= 2, "n": floor["n"],
                           "R_cm": "not_applicable" if key.endswith("absolute") else floor["R_cm"]}
            if not ratios[key]["pass"]:
                failed.append(key)
            if key.endswith("comparative"):
                cmkey = key.rsplit("/", 1)[0]
                ratio = floor["R_cm"]
                # PLAN 6 applies the same registered factor two to common mode.
                common[cmkey] = {"numerator_j": floor.get("common_mode_numerator_j"), "denominator_j": denominator,
                                 "R_cm": ratio, "pass": finite(ratio) and ratio >= 2, "n": floor["n"]}
                if not common[cmkey]["pass"]:
                    failed.append(cmkey + "/common_mode")
        output["dominance"] = {"ratios": ratios, "common_mode": common, "failed": sorted(failed),
                               "branch": "B" if failed else "A"}
        if not complete:
            output["dominance"].update(missing_pack(), branch=None)
    else:
        output["dominance"] = missing_pack()
    if not complete:
        output["contrasts"] = missing_pack()
        output["descriptive"] = missing_pack()
        # Aggregate gates are not issued from a partial block (plan section 2.3).
        if not diagnostic:
            output["floor_gate"] = missing_pack()
            output["floor_gate_unguarded"] = missing_pack()
    else:
        gamma = windows["GAMMA"]
        rows, operands = {}, {}
        for (pack, cid), chosen in selections.items():
            if pack != "GAMMA":
                continue
            phase = "decode" if "decode" in cid else "prefill"
            row, kinds, a, b = contrast_inputs(gamma, chosen["quad"], phase)
            declared_n = len(strings(get(gamma.exclusion_cells.get(cid, {}), "kept_units", "quad")))
            if not diagnostic and (row["n"] < 5 or row["n"] < declared_n):
                row["p"] = 1.0
            rows[cid], operands[cid] = row, (kinds, a, b, phase)
            if len(chosen["quad"]) < 5 and not diagnostic:
                gamma.reader.flag("cell_below_minimum", cid, {"n": len(chosen["quad"])})
        for cid, row in rows.items():
            other = next((r["p"] for c, r in rows.items() if c != cid), 1.0)
            kinds, a, b, phase = operands[cid]
            floor_record = contrast_floor(output["floor_cells"], phase)
            floor = floor_record["floor_gate_j"]
            chosen = selections[("GAMMA", cid)]["quad"]
            declared_n = len(strings(get(gamma.exclusion_cells.get(cid, {}), "kept_units", "quad")))
            missing = not diagnostic and len(chosen) < declared_n
            other_cid = next((c for c in rows if c != cid), None)
            partner = None
            if other_cid is not None:
                other_chosen = selections[("GAMMA", other_cid)]["quad"]
                other_declared = len(strings(get(gamma.exclusion_cells.get(other_cid, {}), "kept_units", "quad")))
                partner = (rows[other_cid], [u for u, _ in other_chosen], operands[other_cid][0],
                           not diagnostic and len(other_chosen) < other_declared)
            contrast = finish_contrast(row, other, floor, [u for u, _ in chosen], kinds,
                                       2 if diagnostic else 5, missing, partner)
            contrast["floor"] = floor_record
            if row["n"] == 5:
                gamma.reader.flag("loo_kept_n_equals_minimum", cid, {"kept_n": 5, "loo_n": 4})
            output["contrasts"][cid] = contrast
            output["descriptive"][cid] = descriptive_estimate(a, b, contrast, phase)
            decision = contrast["decision_interval_j"]
            output["disclosures"]["decision_vs_floor"][cid] = decision_beyond_floor(contrast, floor)
            for model, side in ((MODELS["ALPHA"], a), (MODELS["BETA"], b)):
                reported = next((r for r in output["reported_cells"].values()
                                 if r["model"] == model and r["phase"] == phase), {})
                output["disclosures"]["cross_window"][model + "/" + phase] = cross_window(side, reported)
    # Disclosure unit sets reuse the exact primary estimators, without altering primary selection.
    for (pack, cid), selected in selections.items():
        if "p42" in cid:
            continue
        window = windows[pack]
        dropped = objects(window.exclusion_cells.get(cid, {}).get("dropped_units"))
        for d in dropped:
            if not isinstance(d.get("codes"), list) or len(strings(d.get("codes"))) != len(d["codes"]):
                window.reader.flag("archive_file_missing", cid + "/dropped_units", "codes must be strings")
        load = [d for d in dropped if isinstance(d.get("codes"), list) and d["codes"]
                and len(strings(d["codes"])) == len(d["codes"])
                and set(d["codes"]) <= LOAD_CODES]
        triggered = [d for d in dropped if set(strings(d.get("codes"))) & LOAD_CODES]
        if triggered:
            restored = {}
            for stratum, units in selected.items():
                ids = [u for u, _ in units] + [d["unit_id"] for d in load
                      if d.get("stratum") == stratum and isinstance(d.get("unit_id"), str)]
                restored[stratum] = window.select(cid, stratum, ids, False)
            if pack == "GAMMA":
                phase = "decode" if "decode" in cid else "prefill"
                stats, _, _, _ = contrast_inputs(window, restored["quad"], phase)
                disclosure = {k: stats[k] for k in ("n", "dbar_j", "s_d_j", "se_j", "t_star", "metrology_interval_j")}
            else:
                disclosure = make_reported(window, cid, restored["repeat"], restored["quad"], None)
            restored_counts = {s: len(restored[s]) - len(selected[s]) for s in selected}
            disclosure["restored_by_stratum"] = restored_counts
            disclosure["restored_count"] = sum(restored_counts.values())
            codes = sorted({c for d in triggered for c in strings(d.get("codes")) if c in LOAD_CODES})
            disclosure["codes"] = codes
            disclosure["code_families"] = sorted({"thermal pressure" if c.startswith("thermal.") else "contention"
                                                  for c in codes})
            disclosure["note"] = "no unit restored" if not sum(restored_counts.values()) else "load-correlated exclusions not applied"
            output["disclosures"]["load_sensitivity"][cid] = disclosure
        counts = {s: sum(m.run_id in window.assist for m in flatten(units)) for s, units in selected.items()}
        unassisted = {s: [(u, ms) for u, ms in units if not any(m.run_id in window.assist for m in ms)]
                      for s, units in selected.items()}
        if pack == "GAMMA":
            phase = "decode" if "decode" in cid else "prefill"
            d = [quad_difference(ms, phase) for _, ms in unassisted["quad"]]
            stats = contrast_stats(d)
            disclosure = {k: stats[k] for k in ("n", "dbar_j", "s_d_j", "se_j", "t_star", "metrology_interval_j")}
            disclosure["status"] = "computed" if len(d) >= 5 else "below_registered_minimum"
            disclosure["assist_quads"] = len(selected["quad"]) - len(unassisted["quad"])
        else:
            disclosure = make_reported(window, cid, unassisted["repeat"], unassisted["quad"], None)
        disclosure["assist_members_by_stratum"] = counts
        output["disclosures"]["battery_assist"][cid] = disclosure
    add_sensitivity(output, selections, windows, diagnostic)
    add_machine(output, selections, windows, meter_dir)
    add_reconstruction(output, selections, windows)
    add_scaled_allowance(output, selections, windows, diagnostic)
    add_alternative_allowance(output, windows)
    for pack, window in windows.items():
        if member_detail:
            # Include every collected roster bundle, but never diagnostic interior references.
            for m in objects(window.roster.get("members")):
                rid = m.get("run_id")
                if isinstance(rid, str) and Path(rid).name == rid and rid not in (".", "..") and (window.claim_root / rid).is_dir():
                    which = "science" if m.get("kind") == "science" else role(rid)
                    if which in ("science", "start", "midpoint", "end"):
                        window.member(rid, which)
            for path in sorted(window.bound_root.glob("neg8-refcorpus-r*/metadata.json")):
                window.member(path.parent.name, "corpus")
            output.setdefault("members", {})[pack] = {rid: m.detail() for rid, m in sorted(window.members.items())}
            for rid, m in sorted(window.members.items()):
                if m.role == "science":
                    output["members"][pack][rid]["single_step_reconstruction"] = single_step_member(m)
        output["inputs"][pack] = {"archive": str(window.archive), "exclusions_sha256": window.exclusion_hash,
                                  "claim_usable": window.exclusions.get("claim_usable"),
                                  "attempt": window.exclusions.get("attempt"),
                                  "pack_id": window.roster.get("pack_id", window.harvest.get("pack_id")),
                                  "files_read": len(window.reader.files)}
    output["comparison"] = member_comparison_report(windows)
    output["flags"] = flags
    return output


def sanitize(value, flags, scope="output"):
    if isinstance(value, float) and not math.isfinite(value):
        flags.append({"code": "nonfinite_value", "pack": "", "scope": scope, "detail": "serialized as null"})
        return None
    if isinstance(value, dict):
        return {k: sanitize(v, flags, scope + "/" + k) for k, v in value.items() if k != "flags"}
    if isinstance(value, (list, tuple)):
        return [sanitize(v, flags, scope + "/" + str(i)) for i, v in enumerate(value)]
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for pack in ("alpha", "beta", "gamma"):
        parser.add_argument("--" + pack)
        parser.add_argument("--" + pack + "-exclusions")
        parser.add_argument("--claim-runs-" + pack)
        parser.add_argument("--bound-runs-" + pack)
    parser.add_argument("--member-detail", action="store_true")
    parser.add_argument("--diagnostic-ignore-exclusions", action="store_true")
    parser.add_argument("--meter-dir", help="override the archive's raw meter-stream directory")
    parser.add_argument("--extra-beta", action="append", nargs="+", default=[],
                        metavar="PATH", help="extra BETA ARCHIVE [CLAIM_ROOT [BOUND_ROOT]]; '-' means archive default")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    flags, windows = [], {}
    for pack in ("alpha", "beta", "gamma"):
        archive = getattr(args, pack)
        if not archive:
            if any(getattr(args, attr + pack) for attr in ("claim_runs_", "bound_runs_")) or getattr(args, pack + "_exclusions"):
                parser.error("pack overrides require --" + pack)
            continue
        path = Path(archive)
        try:
            if not path.is_dir():
                raise OSError("not a directory")
            next(path.iterdir(), None)
        except OSError:
            parser.error("unreadable archive root: " + archive)
        windows[pack.upper()] = Window(pack.upper(), archive, flags, getattr(args, pack + "_exclusions"),
                                        getattr(args, "claim_runs_" + pack), getattr(args, "bound_runs_" + pack),
                                        args.diagnostic_ignore_exclusions)
    output = recompute(windows, flags, args.member_detail, args.diagnostic_ignore_exclusions, args.meter_dir)
    if args.extra_beta:
        extras = []
        for entry in args.extra_beta:
            if len(entry) > 3:
                parser.error("--extra-beta takes ARCHIVE and at most two runs roots")
            archive, claim, bound = [*entry, *([None] * (3 - len(entry)))]
            extras.append(Window("BETA", archive, [], claim_root=claim if claim != "-" else None,
                                 bound_root=bound if bound != "-" else None))
        add_beta_inclusive(output, windows.get("BETA"), extras)
        extra_windows = {str(i): w for i, w in enumerate(extras)}
        report = member_comparison_report(extra_windows)
        report["comparison_stopped"] = any(flag_stops_comparison(f, {str(i): w})
                                           for i, w in enumerate(extras) for f in w.reader.flags)
        output["comparison"]["extra_beta"] = report
    clean = sanitize(output, flags)
    clean["flags"] = sorted((sanitize(f, [], "flag") for f in flags),
                            key=lambda f: (f["code"], f["pack"], f["scope"], json.dumps(f["detail"], sort_keys=True)))
    for flag in clean["flags"]:
        flag["stops_comparison"] = flag_stops_comparison(flag, windows)
        flag["blinding"] = "STRUCTURE" if flag["code"] in STRUCTURE_FLAG_CODES else "not_classified"
    clean["comparison_stopped"] = any(f["stops_comparison"] for f in clean["flags"])
    data = (json.dumps(clean, sort_keys=True, indent=1, allow_nan=False) + "\n").encode("utf-8")
    try:
        Path(args.out).write_bytes(data)
    except OSError as exc:
        parser.error("output cannot be written: " + exc.strerror)
    # Public streams carry STRUCTURE codes only (registration section 8); other codes stay in --out.
    counts = {}
    for flag in clean["flags"]:
        if flag["blinding"] == "STRUCTURE":
            counts[flag["code"]] = counts.get(flag["code"], 0) + 1
    rederived = {pack: check["status"] for pack, check in sorted(clean["exclusions_rederivation"].items())}
    print("sha256=" + hashlib.sha256(data).hexdigest() + " python=" + platform.python_version()
          + " flags=" + json.dumps(counts, sort_keys=True, separators=(",", ":"))
          + " exclusions_rederivation=" + json.dumps(rederived, sort_keys=True, separators=(",", ":"))
          + " comparison=" + json.dumps(clean["comparison"]["summary"], sort_keys=True, separators=(",", ":"))
          + " comparison_stopped=" + json.dumps(clean["comparison_stopped"])
          + (" extra_beta_comparison=" + json.dumps({key: clean["comparison"]["extra_beta"][key]
                                                     for key in ("summary", "comparison_stopped")},
                                                    sort_keys=True, separators=(",", ":")) if args.extra_beta else ""))
    return 0


def guarded_main(argv=None) -> int:
    # An uncaught exception's text can carry a value; stderr names only its type.
    try:
        return main(argv)
    except Exception as exc:
        print("error: internal " + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(guarded_main())
