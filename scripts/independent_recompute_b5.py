#!/usr/bin/env python3
"""Independent, non-issuing block-5 arithmetic from archived raw records.

Only the Python standard library is used. Selection, anchors, timing bounds and
calibration fits are input judgments; energy and all reported statistics are
computed here. See the build SPEC for the dependency and comparison contract.
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
import plistlib
import re
import statistics
from xml.parsers.expat import ExpatError

SCHEMA = "joulewise.independent_recompute_b5.v1"
POSITIONS = ("a1", "b1", "b2", "a2")
MODELS = {"ALPHA": "Qwen3-1.7B-4bit", "BETA": "Qwen3-8B-4bit"}
SIDE_MODELS = {"a": MODELS["ALPHA"], "b": MODELS["BETA"]}
LOAD_CODES = {"thermal.os_level_nonzero", "thermal.powermetrics_pressure_elevated",
              "contention.request_overlap"}
FLAG_CODES = frozenset("""archive_file_missing trace_csv_plist_mismatch trace_plist_missing
anchor_label_inconsistent phase_events_ambiguous kept_member_unusable
kept_member_phase_under_3_records kept_member_token_mismatch kept_unit_identity_mismatch
unit_shape_invalid kept_units_disagree claim_usable_false cell_below_minimum b_op_mismatch
b_op_from_record bracket_drift_over_budget member_pre_bound_mismatch stored_energy_mismatch
stored_envelope_mismatch interpolation_bound_nonzero neg8_allowance_mismatch
neg8_allowance_unrecorded neg8_survivor_count_mismatch unknown_auxiliary_member
gamma_midpoint_lost_on_analysed_attempt dominance_ratio_zero_denominator nonfinite_value
pack_missing""".split())


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


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
            reader.flag("trace_plist_missing", run_id, "using CSV fallback when available")
            placed = csv_data
        elif finite(endpoint):
            try:
                placed = plist_records(raw, endpoint, reader, run_id)
            except (ValueError, KeyError, TypeError, OverflowError, AttributeError, ExpatError):
                reader.flag("archive_file_missing", run_id + "/raw/powermetrics.plist", "malformed trace")
        else:
            reader.flag("kept_member_unusable", run_id, "record placement anchor missing or nonfinite")
        if placed and csv_data:
            match = len(placed) == len(csv_data) and all(
                abs(a[0] - b[0]) <= 1e-9 and abs(a[1] - b[1]) <= 1e-9 and abs(a[2] - b[2]) <= 1e-12
                for a, b in zip(placed, csv_data))
            if not match:
                reader.flag("trace_csv_plist_mismatch", run_id, "plist is primary")
        if not placed:
            self.usable = False
        else:
            origin = placed[0][0]
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
                if finite(stored) and abs(stored - self.energies[phase]) > 1e-9:
                    reader.flag("stored_energy_mismatch", run_id + "/" + phase,
                                {"own_j": self.energies[phase], "stored_j": stored})
                envelope_key = "/gross_energy_j" if phase == "request" else "/phase_energy_j/" + phase
                stored_a = get(self.summary, "energy_anchor_shift_envelopes", envelope_key, "max_abs_delta_j")
                if phase in self.pre and finite(stored_a) and abs(stored_a - self.pre[phase]["max_abs_delta_j"]) > 1e-9:
                    reader.flag("stored_envelope_mismatch", run_id + "/" + phase,
                                {"own_j": self.pre[phase]["max_abs_delta_j"], "stored_j": stored_a})
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
        return {"model": self.model, "role": self.role, "E_j": self.energies, "n_overlap": self.counts,
                "a_bop_j": {k: v["max_abs_delta_j"] for k, v in self.op.items()},
                "a_bpre_j": {k: v["max_abs_delta_j"] for k, v in self.pre.items()},
                "stored_E_j": {**mapping(get(self.summary, "phase_energy_j")),
                               "request": self.summary.get("gross_energy_j")},
                "stored_max_abs_delta_j": stored_a,
                "r_j": {k: v["max_abs_delta_j"] for k, v in self.residual.items()},
                "m_s": self.m, "s_s": self.s, "tokens": self.tokens}


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

    def calibration(self):
        r = self.reader
        record = r.json(self.archive / "withheld/bracket-evaluation.json", "withheld/bracket-evaluation.json")
        recorded = get(record, "assessment", "b_fiducial_s")
        captures = {}
        for slot in ("pre", "post"):
            paths = sorted((self.claim_root / "instrument_validation").glob("*-cal-" + slot + "/instrument_evidence.json"))
            if len(paths) == 1:
                capture = r.json(paths[0], "cal-" + slot + "/instrument_evidence.json")
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
            bop = max(pre, post) + max(drift, 0.014531)
            if finite(recorded) and abs(bop - recorded) > 1e-12:
                r.flag("b_op_mismatch", "window", {"own_s": bop, "recorded_s": recorded})
            if drift > 0.01550217418713139:
                r.flag("bracket_drift_over_budget", "window", {"drift_s": drift})
        return {"b_pre_s": pre, "b_post_s": post, "b_op_s": bop, "b_op_recorded_s": recorded}

    def member(self, run_id, member_role="science"):
        if run_id not in self.members:
            root = self.bound_root if member_role == "corpus" else self.claim_root
            self.members[run_id] = Member(root / run_id, run_id, self.reader, self.b["b_op_s"], member_role)
            m = self.members[run_id]
            pre = self.b["b_pre_s"]
            if member_role == "science" and finite(pre) and m.bpre != pre:
                self.reader.flag("member_pre_bound_mismatch", run_id, {"window_s": pre, "member_s": m.bpre})
        return self.members[run_id]

    def compute_neg8(self):
        r, a = self.reader, self.archive
        source = r.json(a / "derived/neg8-allowance.json", "derived/neg8-allowance.json")
        screen = r.json(a / "derived/neg8-screen.json", "derived/neg8-screen.json")
        clean = r.json(a / "derived/neg8-clean-corpus.json", "derived/neg8-clean-corpus.json", False)
        clean_members = objects(clean.get("members"))
        if clean_members:
            ids = [m.get("bundle_id") for m in clean_members]
        else:
            if source.get("clean_bound"):
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
            m = self.member(run_id, "corpus")
            if m.usable and "request" in m.energies and m.model == "Qwen2.5-1.5B-Instruct-4bit":
                corpus.append(m.energies["request"])
                actual_ids.append(run_id)
            else:
                r.flag("kept_member_unusable", run_id, "selected corpus member unusable or wrong model")
        survivors = mapping(get(screen, "rescreen", "survivors"))
        losses = {m["bundle_id"] for m in objects(get(survivors, "reference_losses"))
                   if isinstance(m.get("bundle_id"), str)}
        refs = {"start": [], "midpoint": [], "end": []}
        for mrow in objects(self.roster.get("members")):
            if mrow.get("kind") != "auxiliary":
                continue
            run_id = mrow.get("run_id")
            if not isinstance(run_id, str):
                continue
            which = role(run_id)
            if which == "diagnostic" or which == "corpus":
                continue
            if which == "unknown":
                r.flag("unknown_auxiliary_member", run_id, "not a NEG-8 role")
                continue
            stage = str(mrow.get("stage_id", ""))
            if which not in stage:
                r.flag("unknown_auxiliary_member", run_id, "role disagrees with stage_id")
                continue
            if run_id in losses or not (self.claim_root / run_id).is_dir():
                continue
            m = self.member(run_id, which)
            if m.usable and "request" in m.energies and m.model == "Qwen2.5-1.5B-Instruct-4bit":
                refs[which].append(m.energies["request"])
            else:
                r.flag("kept_member_unusable", run_id, "survivor has no usable reference request")
        counts = {k: len(v) for k, v in refs.items()}
        shape_valid = counts["midpoint"] <= 1 and counts["start"] <= 3 and counts["end"] <= 3
        if not shape_valid:
            r.flag("unit_shape_invalid", "neg8/references", "at most 3 start, 1 midpoint and 3 end references")
        if not 10 <= len(corpus) <= 18:
            r.flag("unit_shape_invalid", "neg8/corpus", {"corpus_n": len(corpus), "expected": "10..18"})
        recorded_counts = get(survivors, "reference_counts")
        if recorded_counts is not None and recorded_counts != counts:
            r.flag("neg8_survivor_count_mismatch", "window", {"own": counts, "recorded": recorded_counts})
        if self.pack == "GAMMA" and get(survivors, "midpoint_lost"):
            r.flag("gamma_midpoint_lost_on_analysed_attempt", "window", "screen records lost midpoint")
        result = {"source": source.get("source"), "screen_decision": get(screen, "rescreen", "decision"),
                  "corpus_n": len(corpus), "corpus_ids": actual_ids,
                  "n_start": counts["start"], "n_mid": counts["midpoint"], "n_end": counts["end"],
                  "start_mean_j": statistics.fmean(refs["start"]) if refs["start"] else None,
                  "midpoint_j": statistics.fmean(refs["midpoint"]) if refs["midpoint"] else None,
                  "end_mean_j": statistics.fmean(refs["end"]) if refs["end"] else None,
                  "t": None, "s_j": None, "bound_envelope_j": None, "bound_prediction_j": None,
                  "bound_j": None, "spread_j": None, "allowance_j": None, "allowance_recorded_j": None}
        own_bound = neg8_bound(corpus, counts["start"], counts["end"]) if shape_valid else None
        if own_bound:
            result.update(own_bound)
            result["spread_j"], result["allowance_j"] = drift_allowance(
                result["start_mean_j"], result["midpoint_j"], result["end_mean_j"], own_bound["bound_j"])
        if source.get("source") == "survivor_rescreen":
            bracket = r.json(a / "withheld/neg8-rescreen-bracket.json", "withheld/neg8-rescreen-bracket.json")
            bracket = bracket.get("bracket", {})
        elif source.get("source") == "stored_verdict":
            verdict = r.json(self.claim_root / "whole-window-verdict.json", "whole-window-verdict.json")
            bracket = get(verdict, "idle_admission_core", "neg8_bracket", default={})
        else:
            bracket = {}
        recorded = get(bracket, "drift_allowances", "gross_energy", "allowance_j")
        result["allowance_recorded_j"] = recorded
        if not finite(recorded):
            r.flag("neg8_allowance_unrecorded", "window", "no recorded gross allowance")
        elif finite(result["allowance_j"]) and abs(result["allowance_j"] - recorded) > 1e-9:
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
            members = [self.member(i) for i in ids]
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


def make_reported(window, cell_id, repeats, quads, minimum=5):
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
    bound = lambda m: get(m.op, phase, "max_abs_delta_j")
    if all(finite(bound(m)) for m in all_members):
        anchor_average = 0.2 * statistics.fmean(bound(m) for m in rm) + 0.8 * statistics.fmean(bound(m) for m in qm)
        maximum = max(bound(m) for m in all_members)
        result["attribution_floor"] = {"value_j": maximum, "minimum_j": min(bound(m) for m in all_members),
                                       "attained_by": next(m.run_id for m in all_members if bound(m) == maximum)}
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


def finish_contrast(row, other_p, floor, ids=None, kind_rows=None, minimum=5, missing=False):
    row = dict(row)
    if row["n"] < minimum or missing or not finite(row["dbar_j"]):
        row["p"] = 1.0
    row.update(floor_gate_j=floor, holm_p=holm([row["p"], other_p])[0])
    row["holm_reject"] = row["holm_p"] <= 0.05
    row["direction"] = "positive" if finite(row["dbar_j"]) and row["dbar_j"] > 0 else (
        "negative" if finite(row["dbar_j"]) and row["dbar_j"] < 0 else None)
    row["outcome"] = evaluate_outcome(row, floor, row["holm_reject"], minimum, missing)
    row["kept_quads"] = ids or [str(i + 1) for i in range(row["n"])]
    loo, verdict_influential, magnitude_influential = [], False, False
    if row["n"] >= 3:
        for i, unit_id in enumerate(row["kept_quads"]):
            d = row["d_k"][:i] + row["d_k"][i + 1:]
            if kind_rows is not None:
                remaining = kind_rows[:i] + kind_rows[i + 1:]
                terms = [statistics.fmean(k[j] for k in remaining) if all(finite(k[j]) for k in remaining)
                         else None for j in range(3)]
                D = math.fsum(terms) if all(finite(x) for x in terms) else None
            else:
                terms, D = row.get("D_terms_j"), row["D_j"]
            reduced = contrast_stats(d, D)
            adjusted = holm([reduced["p"], other_p])[0]
            reject = adjusted <= 0.05
            outcome = evaluate_outcome(reduced, floor, reject, 2, missing)
            sign = "positive" if reduced["dbar_j"] > 0 else ("negative" if reduced["dbar_j"] < 0 else None)
            above = finite(floor) and abs(reduced["dbar_j"]) > floor
            full_above = finite(floor) and abs(row["dbar_j"]) > floor
            verdict_influential |= (sign != row["direction"] or above != full_above
                                    or reject != row["holm_reject"] or outcome != row["outcome"])
            magnitude_influential |= finite(floor) and abs(reduced["dbar_j"] - row["dbar_j"]) > 0.25 * floor
            loo.append({**reduced, "dropped": unit_id, "D_terms_j": terms, "holm_p": adjusted,
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


def contrast_inputs(window, quads, phase):
    d, kinds, a, b = [], [], [], []
    for _, members in quads:
        d.append(quad_difference(members, phase))
        energies = {m.run_id.rsplit("-", 1)[-1]: m.energies[phase] for m in members}
        a.append((energies["a1"] + energies["a2"]) / 2)
        b.append((energies["b1"] + energies["b2"]) / 2)
        anchors = [get(m.op, phase, "max_abs_delta_j") for m in members]
        allowance = window.neg8["allowance_j"]
        kinds.append([0.5 * sum(anchors) if all(finite(v) for v in anchors) else None, 0.0,
                      allowance if finite(allowance) else None])
    terms = [statistics.fmean(k[j] for k in kinds) if kinds and all(finite(k[j]) for k in kinds) else None
             for j in range(3)]
    D = math.fsum(terms) if all(finite(v) for v in terms) else None
    return {**contrast_stats(d, D), "D_terms_j": terms}, kinds, a, b


def missing_pack():
    return {"status": "not_computed", "reason": "pack_missing"}


def recompute(windows, flags, member_detail=False, diagnostic=False):
    output = {"schema": SCHEMA, "mode": "DIAGNOSTIC_NOT_REGISTERED" if diagnostic else "REGISTERED",
              "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "inputs": {}, "windows": {}, "reported_cells": {}, "p42": {}, "floors": {},
              "floor_gate": {}, "floor_gate_unguarded": {}, "dominance": {}, "contrasts": {},
              "descriptive": {}, "disclosures": {"load_sensitivity": {}, "battery_assist": {},
                                                 "cross_window": {}, "decision_vs_floor": {}}}
    selections = {}
    for pack, window in windows.items():
        output["windows"][pack] = {**window.b, "neg8": window.neg8}
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
            for form, stratum in (("absolute", "repeat"), ("comparative", "quad")):
                units = chosen[stratum]
                if form == "absolute":
                    values = [ms[0].energies[phase] for _, ms in units]
                    widths = [max(e["point_j"] - e["lower_j"], e["upper_j"] - e["point_j"], e["max_abs_delta_j"])
                              if (e := ms[0].op.get(phase)) else None for _, ms in units]
                    pre_widths = [get(ms[0].pre, phase, "max_abs_delta_j") for _, ms in units]
                    shared = local = None
                else:
                    values = [quad_difference(ms, phase, True) for _, ms in units]
                    splits = [common_width(ms, phase, window.b["b_op_s"]) for _, ms in units]
                    widths = [s["width_j"] if s else None for s in splits]
                    shared = [s["shared_j"] if s else None for s in splits]
                    local = [s["local_j"] if s else None for s in splits]
                result = floor_estimate(values, widths, form, shared, local)
                if not diagnostic and reported["status"] == "below_minimum":
                    # A target cell cannot publish any registered number below its stratum minimum.
                    result = floor_estimate([], [], form)
                    result["n"] = len(units)
                result["kept_units"] = [u for u, _ in units]
                result["removed_units"] = reported["removed_units"]
                if form == "absolute":
                    result["widths_bpre_j"] = pre_widths
                output["floors"][model + "/" + phase + "/" + form] = result
            fs = [output["floors"][model + "/" + phase + "/" + f] for f in ("absolute", "comparative")]
            output["floor_gate"][model + "/" + phase] = (max(f["guarded_floor_j"] for f in fs)
                if all(finite(f["guarded_floor_j"]) for f in fs) else None)
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
            ratios[key] = {"numerator_j": floor["corner_widened_unguarded_floor_j"], "denominator_j": denominator,
                           "R": ratio, "pass": finite(ratio) and ratio >= 2, "n": floor["n"],
                           "R_cm": "not_applicable" if key.endswith("absolute") else floor["R_cm"]}
            if not ratios[key]["pass"]:
                failed.append(key)
            if key.endswith("comparative"):
                cmkey = key.rsplit("/", 1)[0]
                ratio = floor["R_cm"]
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
            model_floors = [output["floor_gate"].get(model + "/" + phase) for model in MODELS.values()]
            floor = max(model_floors) if all(finite(f) for f in model_floors) else None
            chosen = selections[("GAMMA", cid)]["quad"]
            declared_n = len(strings(get(gamma.exclusion_cells.get(cid, {}), "kept_units", "quad")))
            missing = not diagnostic and len(chosen) < declared_n
            contrast = finish_contrast(row, other, floor, [u for u, _ in chosen], kinds,
                                       2 if diagnostic else 5, missing)
            output["contrasts"][cid] = contrast
            output["descriptive"][cid] = descriptive_estimate(a, b, contrast, phase)
            decision = contrast["decision_interval_j"]
            output["disclosures"]["decision_vs_floor"][cid] = (
                (decision[0] > floor if contrast["dbar_j"] > 0 else decision[1] < -floor)
                if finite(floor) and finite(contrast["dbar_j"]) and all(finite(v) for v in decision) else None)
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
        if load:
            restored = {}
            for stratum, units in selected.items():
                ids = [u for u, _ in units] + [d["unit_id"] for d in load
                      if d.get("stratum") == stratum and isinstance(d.get("unit_id"), str)]
                restored[stratum] = window.select(cid, stratum, ids, False)
            if pack == "GAMMA":
                phase = "decode" if "decode" in cid else "prefill"
                row, kinds, _, _ = contrast_inputs(window, restored["quad"], phase)
                primary = output["contrasts"].get(cid, {})
                other = next((r.get("p", 1.0) for c, r in output["contrasts"].items()
                              if c != cid and isinstance(r, dict)), 1.0)
                disclosure = finish_contrast(row, other, primary.get("floor_gate_j"),
                                            [u for u, _ in restored["quad"]], kinds)
            else:
                disclosure = make_reported(window, cid, restored["repeat"], restored["quad"], None)
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
        output["inputs"][pack] = {"archive": str(window.archive), "exclusions_sha256": window.exclusion_hash,
                                  "claim_usable": window.exclusions.get("claim_usable"),
                                  "attempt": window.exclusions.get("attempt"),
                                  "pack_id": window.roster.get("pack_id", window.harvest.get("pack_id")),
                                  "files_read": len(window.reader.files)}
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
    output = recompute(windows, flags, args.member_detail, args.diagnostic_ignore_exclusions)
    clean = sanitize(output, flags)
    clean["flags"] = sorted((sanitize(f, [], "flag") for f in flags),
                            key=lambda f: (f["code"], f["pack"], f["scope"], json.dumps(f["detail"], sort_keys=True)))
    data = (json.dumps(clean, sort_keys=True, indent=1, allow_nan=False) + "\n").encode("utf-8")
    try:
        Path(args.out).write_bytes(data)
    except OSError as exc:
        parser.error("output cannot be written: " + exc.strerror)
    counts = {}
    for flag in clean["flags"]:
        counts[flag["code"]] = counts.get(flag["code"], 0) + 1
    print("sha256=" + hashlib.sha256(data).hexdigest() + " flags=" + json.dumps(counts, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
