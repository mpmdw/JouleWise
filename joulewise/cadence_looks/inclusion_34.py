"""Inclusion rules 3 and 4 at the interim look, stage 1 (RL-150 R9; RL-166 Q7). Reads stamps; opens no energy.

Both rules are judged on the leg's own interval: from its G0's start to its last stamped token
(RL-166 Q7).

Rule 3, sidecar and powermetrics coverage (RL-149 section 2.4 rule 3; U1, pilot_protocol_v4.md:451):
* sidecar coverage of at least 99 % and no gap over 2 s;
* powermetrics gaps of at most max(1 s, 5 periods).

Both use the registered U1 evaluator's definitions, not new ones:
* coverage is ``joulewise.align.apple.thermal.Coverage`` (with ``valid_value`` and ``keys``), read through
  its ``all_keys`` report the way ``thermal_desk.acceptance`` reads it;
* the powermetrics gap is the cursor loop of ``thermal_desk.member_record`` (``pm_gap``) over the
  supports [end - elapsed, end] of each sample, as ``thermal_desk.native_pm_samples`` builds them.

``thermal.py`` and ``thermal_desk.py`` are v4 strict paths (``v4_registration``). Importing them would pull
v4 strict code into the look, so the definitions are COPIED here, byte for byte, with this cite.
``tests/cadence/test_inclusion_34.py`` holds the equality tests: the copied source equals the registered
source, and the two give equal results on fixtures.
Copied from: ``joulewise/align/apple/thermal.py`` (sha256 b9b46f9e...d39d7) and
``joulewise/align/apple/thermal_desk.py`` (sha256 e3c049f2...13a2bc), as they stand at 91338c4bc.

Rule 4, the KM003C stream (RL-149 section 2.4 rule 4 as RL-166 Q7 reads "clean"):
* every stream file that overlaps the leg's interval has its header (status "streaming") and its
  trailer, and the trailer's stop reason is a normal one: a signal, "duration" or "stop file";
* inside the leg's interval, the samples the polls carried (each sample line's count ``n``, summed) are at
  least 99 % of the header's nominal sample rate (``sps``) times the interval;
* no gap over 2 s between consecutive polls that carried samples (``n > 0``), the interval's edges included.
  An empty poll covers nothing, so a stream of empty polls cannot cover a leg (Sol cold seat N5).

The trailer's counts are printed in the inclusion table (``span_trailers``) and decide nothing. RL-166
refused the "trailer counts zero" clause.

**What is read.**
* From each KM003C poll line (top-level ``"k": "b"``), only its ``rt`` stamp (CLOCK_REALTIME ns at receipt) and
  its sample count ``n``, through the look's one time-field reader (``time_fields.py``, RL-173 E.1): its lexer
  converts no SMC value and no sample byte; they are never kept, logged or copied.
* Error lines (``{"k": "e", ...}``) are skipped unread.
* Of the header and the trailer, only their operational keys (``time_fields.HEADER_KEYS``, ``TRAILER_KEYS``).
* A ``.zst`` sibling of a stream (a desk-compressed custody copy) refuses the span (Mythos round-5 N8).
* From ``rich_telemetry.jsonl``, only ``timestamp_s`` and ``elapsed_ns``, taken by pattern. The line is never
  JSON-decoded, so no power or energy value is parsed (Sol cold seat 1).
* A type-T leg (``leg_record.json`` ``spec.leg_type == "T"``, the ruled selector only) is never opened
  (RL-166 Q14; RL-167 R-21).
* The sidecar journal (``outputs/align_thermal.jsonl``) and ``events.jsonl`` are journal files.

**Clock.** The leg's interval, the rich-telemetry stamps and the meter's ``rt`` stamps are all on the wall
clock (epoch), which is step 3's convention for these bundles. The sidecar rows are judged on their
``started``/``finished`` ``wall_ns`` stamps. The registered ``thermal.coverage`` uses ``monotonic_ns``.
Coverage counts cells on a grid anchored at the first sample, so a constant offset between the clocks does
not change the result. Network time is off for the whole campaign (RL-149 section 2.2).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import sys
import math
from pathlib import Path
import re
from typing import Any

NS = 1_000_000_000

SIDECAR_MIN_FRACTION = 0.99          # U1: >= 99 % sidecar coverage
SIDECAR_MAX_INTERVAL_NS = 2 * NS     # U1: no gap > 2 s
PM_GAP_FLOOR_S = 1.0                 # U1: PM gaps <= max(1 s, 5 periods)
PM_GAP_PERIODS = 5
METER_MIN_COVERAGE = 0.99            # RL-166 Q7
METER_MAX_GAP_NS = 2 * NS            # RL-166 Q7
NORMAL_STOP_REASONS = ("duration", "stop file")     # and any "signal N" (km003c_monitor.py on_signal)
ABNORMAL_STOP_REASONS = ("absent", "exception", "consecutive USB errors")

# ------------------------------------------------------------------------------------------------------------
# Copied from joulewise/align/apple/thermal.py (v4 strict path; see the module docstring). Byte-identical:
# tests/cadence/test_inclusion_34.py compares the source.

def keys(policy: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((policy["s_fast"], policy["s_slow"], *policy["fan_keys"],
                               *policy.get("record_keys", ()))))


def valid_value(key: str, value: Any) -> bool:
    return (type(value) in (int, float) and math.isfinite(value)
            and (-40 <= value <= 150 if key.startswith("T") else value >= 0))


class Coverage:
    """Successful nominal ticks on the sampling grid, not the caller's span.

    The default 100 ms tolerance admits scheduler/read jitter. At the explicit
    500 ms (half-period) tolerance, every boundary snaps to its nearest grid
    point and each stamp belongs to exactly one cell (ties round forward).
    At narrower tolerances partial edge cells are excluded unless their
    boundaries snap within that tolerance. Duplicates
    count once; calls lasting over one period never fill ticks. Separately,
    actual sample midpoints, including both span edges, bound the longest
    interval. No temperature value is interpolated or carried across a gap.
    """
    tolerance_ns = NS // 10

    def __init__(self, start_ns: int, selected: Sequence[str], *, tolerance_ns: int = tolerance_ns):
        if type(tolerance_ns) is not int or not 0 < tolerance_ns <= NS // 2:
            raise ValueError("coverage tolerance_ns must be an integer from 1 to 500000000 ns (half the 1 s period)")
        self.tolerance_ns = tolerance_ns
        self.start_ns = start_ns
        self.grid_ns = None
        self.times: dict[str, set[int]] = {k: set() for k in selected}
        self.common: set[int] = set()

    def observe(self, started_ns: int, finished_ns: int, values: Mapping[str, Any]) -> None:
        if finished_ns < started_ns or finished_ns - started_ns > NS:
            return
        self.grid_ns = min(self.grid_ns, started_ns) if self.grid_ns is not None else started_ns
        stamp = (started_ns + finished_ns) // 2
        good = []
        for key in self.times:
            valid = key not in values.get("errors", {}) and valid_value(key, values.get("sensors", {}).get(key))
            good.append(valid)
            if valid:
                self.times[key].add(stamp)
        if good and all(good):
            self.common.add(stamp)

    def report(self, end_ns: int) -> dict[str, Any]:
        if end_ns < self.start_ns:
            raise ValueError("temperature span ends before it starts")
        grid = self.start_ns if self.grid_ns is None else self.grid_ns
        def nearest(t):
            return (t - grid + NS//2) // NS
        def boundary(t):
            snapped = grid + nearest(t) * NS
            return snapped if abs(t - snapped) <= self.tolerance_ns else t
        first = -((grid - boundary(self.start_ns)) // NS)
        last = (boundary(end_ns) - grid) // NS
        expected = max(0, last - first) if end_ns > self.start_ns else 0

        def stats(times):
            ticks = {nearest(t) for t in times
                     if first <= nearest(t) < last
                     and abs(t - (grid + nearest(t)*NS)) <= self.tolerance_ns}
            points = sorted({self.start_ns, end_ns, *(t for t in times if self.start_ns <= t <= end_ns)})
            intervals = list(zip(points, points[1:]))
            gaps = [[a, b] for a, b in intervals if b-a > NS+self.tolerance_ns]
            # Erratum 2 D6: one empty 1 s cell is admitted by the 99% bar;
            # two consecutive empty cells lose U1(c)'s 2 s reader window.
            # Include leading/trailing cells, but never another phase's grid.
            occupied = [first-1, *sorted(ticks), last]
            empty_run = max(0, max((b-a-1 for a, b in zip(occupied, occupied[1:])), default=0))
            return {"expected_samples": expected, "valid_samples": len(ticks),
                    "sample_fraction": len(ticks)/expected if expected else None,
                    "max_consecutive_empty_cells": empty_run,
                    "gaps_ns": gaps, "max_interval_ns": max((b-a for a, b in intervals), default=0)}
        return {"clock": "monotonic_ns", "period_ns": NS, "tolerance_ns": self.tolerance_ns,
                "sampling_grid_ns": grid,
                "edge_policy": ("half-period cells; all edges snapped to nearest grid; ties round forward"
                                if self.tolerance_ns == NS // 2 else
                                "partial cells excluded; near-grid edges snapped"),
                "span_ns": [self.start_ns, end_ns], "all_keys": stats(self.common),
                "per_key": {key: stats(times) for key, times in self.times.items()}}


# ------------------------------------------------------------------------------------------------------------
# Copied from joulewise/align/apple/thermal_desk.py member_record (the U1 pm_gap loop), lines 230-238 at
# 91338c4bc, wrapped in a function. tests/cadence/test_inclusion_34.py executes the registered lines and
# compares.

def pm_max_gap_ns(spans, pm_samples):
    pm_gap = 0
    for a, b in spans:
        cursor = a
        for sample in sorted(pm_samples, key=lambda s: s['start_ns']):
            left, right = max(a, sample['start_ns']), min(b, sample['end_ns'])
            if left < right:
                pm_gap = max(pm_gap, left-cursor)
                cursor = max(cursor, right)
        pm_gap = max(pm_gap, b-cursor)
    return pm_gap


# ------------------------------------------------------------------------------------------------------------
# Verdicts (pure functions over stamps).

def rule3(interval_ns, sidecar_rows, selected_keys, pm_samples, pm_period_s):
    """Rule 3 on one leg. ``interval_ns`` = (start, end) on the wall clock; ``sidecar_rows`` =
    [(started_ns, finished_ns, {"sensors": ..., "errors": ...})]; ``pm_samples`` = [{start_ns, end_ns}].
    Returns {"pass", "sample_fraction", "max_interval_s", "pm_max_gap_s", "pm_gap_limit_s", "reasons"}."""
    reasons = []
    out = {"pass": False, "sample_fraction": None, "max_interval_s": None, "pm_max_gap_s": None,
           "pm_gap_limit_s": None, "reasons": reasons}
    if interval_ns is None or interval_ns[1] <= interval_ns[0]:
        reasons.append("no leg interval (G0 start or last stamped token missing)")
        return out
    a, b = interval_ns
    counter = Coverage(a, selected_keys)
    for started, finished, values in sorted(sidecar_rows, key=lambda r: r[0]):
        counter.observe(started, finished, values)
    stats = counter.report(b)["all_keys"]
    out["sample_fraction"] = stats["sample_fraction"]
    out["max_interval_s"] = stats["max_interval_ns"] / NS
    if stats["sample_fraction"] is None or stats["sample_fraction"] < SIDECAR_MIN_FRACTION:
        reasons.append("sidecar coverage under 99 %")
    if stats["max_interval_ns"] > SIDECAR_MAX_INTERVAL_NS:
        reasons.append("sidecar gap over 2 s")
    if pm_period_s is None or not (isinstance(pm_period_s, (int, float)) and pm_period_s > 0):
        reasons.append("powermetrics period unknown")
    else:
        limit_s = max(PM_GAP_FLOOR_S, PM_GAP_PERIODS * pm_period_s)
        gap_ns = pm_max_gap_ns([(a, b)], pm_samples)
        out["pm_max_gap_s"], out["pm_gap_limit_s"] = gap_ns / NS, limit_s
        if gap_ns > limit_s * NS:
            reasons.append("powermetrics gap over max(1 s, 5 periods)")
    out["pass"] = not reasons
    return out


def normal_stop(reason):
    return isinstance(reason, str) and (reason in NORMAL_STOP_REASONS or reason.startswith("signal "))


def rule4(interval_ns, streams):
    """Rule 4 on one leg. ``streams`` = [{"name", "header", "trailer", "polls"}] from ``read_meter_stream``
    (polls = sorted (rt ns, n samples)). Coverage is the samples the polls in the interval carried against the
    header's sps over the interval; the gap is between polls that carried samples. Returns {"pass",
    "coverage_fraction", "max_gap_s", "streams", "reasons"}."""
    reasons = []
    out = {"pass": False, "coverage_fraction": None, "max_gap_s": None, "streams": [], "reasons": reasons}
    if interval_ns is None or interval_ns[1] <= interval_ns[0]:
        reasons.append("no leg interval (G0 start or last stamped token missing)")
        return out
    a, b = interval_ns
    overlapping, polls, sps = [], [], set()
    for s in streams:
        header, trailer = s.get("header"), s.get("trailer")
        start = (header or {}).get("start_real_ns")
        end = s["polls"][-1][0] if s["polls"] else start
        if start is not None and (end is None or end < a or start > b):
            continue
        overlapping.append(s)
        out["streams"].append(s["name"])
        if header is None or header.get("status") != "streaming":
            reasons.append(f"{s['name']}: no streaming header")
        else:
            sps.add(header.get("sps"))
        if trailer is None:
            reasons.append(f"{s['name']}: no trailer")
        elif not normal_stop(trailer.get("stop_reason")):
            reasons.append(f"{s['name']}: stop reason {trailer.get('stop_reason')!r} is not a normal stop")
        polls.extend((t, n) for t, n in s["polls"] if a <= t <= b)
    if not overlapping:
        reasons.append("no meter stream covers the leg's interval")
    if len(sps) != 1 or not all(isinstance(r, (int, float)) and not isinstance(r, bool) and r > 0 for r in sps):
        reasons.append("the header's nominal sample rate (sps) is missing or differs between streams")
    else:
        # Sol cold seat N5: samples, not polls. An empty poll (n = 0) carries no sample, so a stream of empty polls
        # cannot cover the leg. n is a count the monitor writes beside the stamp; no sample value is decoded.
        expected = (b - a) / NS * sps.pop()
        out["coverage_fraction"] = sum(n for _, n in polls) / expected if expected > 0 else None
        if out["coverage_fraction"] is None or out["coverage_fraction"] < METER_MIN_COVERAGE:
            reasons.append("meter samples under 99 % of the nominal rate")
    points = sorted({a, b, *(t for t, n in polls if n > 0)})
    gap = max((y - x for x, y in zip(points, points[1:])), default=b - a)
    out["max_gap_s"] = gap / NS
    if gap > METER_MAX_GAP_NS:
        reasons.append("meter gap over 2 s")
    out["pass"] = not reasons
    return out


# ------------------------------------------------------------------------------------------------------------
# Loaders: stamps only.

def _jsonl_lines(path):
    with open(path, "rb") as handle:
        for raw in handle:
            raw = raw.strip()
            if raw:
                yield raw


def read_meter_stream(path):
    """{"name", "header", "trailer", "polls"} for one KM003C stream, through the look's one time-field reader
    (``time_fields.read_stream``, RL-173 E.1): a poll line gives its ``rt`` stamp and its sample count ``n``; the
    record kind is the line's top-level ``k`` (Sol round-5 NEW-2); no SMC value or sample value is converted. The header
    is the first line when it is one, the trailer the last trailer line; only their operational keys are read
    (RL-150 R8)."""
    from joulewise.cadence_looks import time_fields as TF     # lazily: run as a program, the repository joins
    view = TF.read_stream(path, counters=False)               # sys.path in main(), after the fresh pycache prefix
    polls = sorted((p["rt"], p["n"]) for p in view["polls"]
                   if all(type(p.get(k)) is int and p[k] >= 0 for k in ("tx", "rx", "rt", "n")))
    return {"name": view["name"], "header": view["first_line_header"], "trailer": view["trailer"], "polls": polls}


TRAILER_COUNT_KEYS = ("polls", "empties", "bad", "usb_errors")


def span_trailers(span_id, streams):
    """The span's trailer counts, printed in the inclusion table; they decide nothing (RL-166 Q7)."""
    rows = []
    for s in streams:
        t = s.get("trailer") or {}
        rows.append({"span_id": span_id, "stream": s["name"], **{k: t.get(k) for k in TRAILER_COUNT_KEYS},
                     "stop_reason": t.get("stop_reason")})
    return rows


def _keep(allowed):
    def hook(pairs):
        return {k: v for k, v in pairs if k in allowed}
    return hook


_TS_RE = re.compile(rb'"timestamp_s":\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*[,}]')
_EL_RE = re.compile(rb'"elapsed_ns":\s*(\d+)\s*[,}]')


def read_pm_supports(bundle):
    """[{start_ns, end_ns}] from rich_telemetry.jsonl: timestamp_s is the sample's end (D-078), elapsed_ns
    its length, as thermal_desk.native_pm_samples builds the supports. The two stamps are taken from each line
    by pattern; the line is never JSON-decoded, so no power or energy value is parsed (Sol cold seat 1). A line
    that does not carry each key exactly once gives no support (a gap rule 3 then sees)."""
    out = []
    for raw in _jsonl_lines(Path(bundle) / "rich_telemetry.jsonl"):
        if raw.count(b'"timestamp_s"') != 1 or raw.count(b'"elapsed_ns"') != 1:
            continue
        ts, el = _TS_RE.search(raw), _EL_RE.search(raw)
        if ts is None or el is None:
            continue
        end = round(float(ts.group(1)) * NS)
        out.append({"start_ns": end - int(el.group(1)), "end_ns": end})
    return out


def read_sidecar_rows(bundle):
    """[(started wall_ns, finished wall_ns, {"sensors", "errors"})] for the journal's temperature readings."""
    rows = []
    for raw in _jsonl_lines(Path(bundle) / "outputs" / "align_thermal.jsonl"):
        r = json.loads(raw)                       # a journal file: temperatures, levels, states, stamps
        if r.get("module") != "temperature" or r.get("kind") != "reading":
            continue
        s, f = (r.get("started") or {}).get("wall_ns"), (r.get("finished") or {}).get("wall_ns")
        if type(s) is int and type(f) is int:
            v = r.get("values") or {}
            rows.append((s, f, {"sensors": v.get("sensors") or {}, "errors": v.get("errors") or {}}))
    return rows


G0_EVENT_FILES = ("events.jsonl", "outputs/align_runtime_events.jsonl", "align_runtime_events.jsonl")


def _scan_events(path):
    hook = _keep({"event_type", "phase", "timestamp_s", "metadata", "kind"})
    g0, last = None, None
    for raw in _jsonl_lines(path):
        e = json.loads(raw, object_pairs_hook=hook)
        et, ts = e.get("event_type"), e.get("timestamp_s")
        if not isinstance(ts, (int, float)):
            continue
        if et == "token":
            last = ts if last is None else max(last, ts)
        elif (et == "phase_start" and e.get("phase") == "align_thermal_gate"
              and (e.get("metadata") or {}).get("kind") == "G0" and g0 is None):
            g0 = ts
    return g0, last


def read_leg_interval(bundle):
    """(G0 start, last stamped token) in wall-clock ns, or None. The last token is the latest token event's
    stamp in events.jsonl. The G0 start is the phase_start of the leg's align_thermal_gate with metadata kind
    G0 (thermal_gates.py), from events.jsonl, else from the runtime's align_runtime_events.jsonl (the same
    fallback the desk and RL-149 section 1.2 item 6 use). Only these fields are kept."""
    bundle = Path(bundle)
    g0, last = _scan_events(bundle / "events.jsonl")
    for name in G0_EVENT_FILES[1:]:
        if g0 is not None:
            break
        if (bundle / name).is_file():
            g0, _ = _scan_events(bundle / name)
    if g0 is None or last is None:
        return None
    return round(g0 * NS), round(last * NS)


def pm_period_s(bundle):
    """1 / sampling.power_hz of the bundle's config.json, as thermal_desk.read_bundle_record takes it."""
    path = Path(bundle) / "config.json"
    if not path.is_file():
        return None
    cfg = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_keep({"sampling", "power_hz"}))
    hz = (cfg.get("sampling") or {}).get("power_hz")
    return 1 / hz if isinstance(hz, (int, float)) and hz > 0 else None


def judge_leg(bundle, meter_streams, selected_keys, *, period_s=None):
    """Rules 3 and 4 for one leg's accepted attempt. ``meter_streams`` are ``read_meter_stream`` results for
    the span. ``selected_keys`` = ``keys(policy sensors)`` of the leg's runtime config. Opens events.jsonl,
    outputs/align_thermal.jsonl, rich_telemetry.jsonl (two stamps by pattern) and config.json; no energy value is decoded."""
    interval = read_leg_interval(bundle)
    period = period_s if period_s is not None else pm_period_s(bundle)
    return {"rule3": rule3(interval, read_sidecar_rows(bundle), selected_keys, read_pm_supports(bundle), period),
            "rule4": rule4(interval, meter_streams)}


# ------------------------------------------------------------------------------------------------------------
# Custody mode: the verdict file the stage-1 CLI reads (docs/process/cadence_look_fit_interface.md section 7).
#
#     python3 -I -B joulewise/cadence_looks/inclusion_34.py --roster ROSTER.json --custody ROOT
#         [--span-dir SPAN_ID=PATH ...] --manifest MANIFEST.json [--allow-draft]
#         --out VERDICTS.json [--detail-out DETAIL.json]
#
# VERDICTS.json is {"<span_id>/<leg_id>": {"sidecar_coverage": bool, "km003c_clean": bool}}, one entry per leg
# of each roster span's runner_receipt.json roster. A leg with no leg_record.json, or no accepted bundle, gets
# both false. DETAIL.json carries each leg's rule_detail and each span's trailer counts; it is a print.
# Opens per span: runner_receipt.json, hazards/meter/stream-*.jsonl (stamps, header, trailer); per leg:
# leg_record.json; per accepted bundle: events.jsonl, outputs/align_thermal.jsonl, rich_telemetry.jsonl (two
# keys) and config.json. Never power_trace.csv or raw/powermetrics.plist.

VERDICT_KEYS = ("sidecar_coverage", "km003c_clean")
REPO = Path(__file__).resolve().parents[2]
RUNTIME_CONFIG = "configs/align/v4/r1_runtime.json"    # rule 3's sensor policy; pinned in fit.dependencies


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def span_dirs(custody, overrides=()):
    """span_id -> directory: <custody>/<span_id> unless SPAN_ID=PATH overrides it (as the stage-1 CLI)."""
    extra = dict(o.split("=", 1) for o in overrides)
    return lambda span_id: Path(extra[span_id]) if span_id in extra else Path(custody) / span_id


def judge_span(sdir, span_id, selected_keys):
    """({leg_key: {sidecar_coverage, km003c_clean}}, {leg_key: detail}, trailers) for one span directory."""
    sdir = Path(sdir)
    from joulewise.cadence_looks import time_fields as TF
    streams = [read_meter_stream(p) for p in TF.span_streams(sdir)]       # a .zst sibling refuses (Mythos r5 N8)
    verdicts, detail = {}, {}
    for leg_id in _json(sdir / "runner_receipt.json")["roster"]:
        key = f"{span_id}/{leg_id}"
        record = sdir / "legs" / leg_id / "leg_record.json"
        bundle = None
        rec = _json(record) if record.is_file() else {}
        if (rec.get("spec") or {}).get("leg_type") == "T":
            # RL-166 Q14: a type-T leg is not read at this look at all. The ruled selector only (RL-167 R-21):
            # spec.leg_type, no legacy field.
            verdicts[key] = {k: False for k in VERDICT_KEYS}
            why = ["type T: never read (RL-166 Q14)"]
            detail[key] = {"rule3": {"reasons": why}, "rule4": {"reasons": why}}
            continue
        if rec:
            name = (rec.get("result") or {}).get("bundle")
            if isinstance(name, str) and name and (sdir / "legs" / leg_id / "runtime" / name).is_dir():
                bundle = sdir / "legs" / leg_id / "runtime" / name
        if bundle is None:
            verdicts[key] = {k: False for k in VERDICT_KEYS}
            detail[key] = {"rule3": {"reasons": ["no accepted bundle"]}, "rule4": {"reasons": ["no accepted bundle"]}}
            continue
        try:
            v = judge_leg(bundle, streams, selected_keys)
        except (OSError, ValueError, KeyError, TypeError) as exc:   # a missing or malformed journal file
            verdicts[key] = {k: False for k in VERDICT_KEYS}
            why = [f"unreadable bundle: {type(exc).__name__}"]  # the type only: a message could carry a value
            detail[key] = {"rule3": {"reasons": why}, "rule4": {"reasons": why}}
            continue
        verdicts[key] = {"sidecar_coverage": v["rule3"]["pass"], "km003c_clean": v["rule4"]["pass"]}
        detail[key] = {r: {k: x for k, x in v[r].items() if k != "pass"} for r in ("rule3", "rule4")}
    return verdicts, detail, span_trailers(span_id, streams)


# RL-171 and RL-172a: the span's soak may be retried once, on a slope or a load refusal. Receipt fields only (the
# lead's ruling on the open list): the receipt's soak_attempts ({"attempt", "refused", ...}) and its steps list,
# whose soak stages are named "soak" and "soak.a<n>". A receipt from the v1/v1.1 pins has no soak_attempts field,
# which means one attempt. The receipt's "refused" text is the same for both kinds, so the kind is read from a
# receipt field that names it (SOAK_KIND_FIELDS; none exists at the RL-171 pin 6010985a3), else it is "kind not
# recorded". No log and no soak file is opened. A soak retried and then accepted is not a stop: whether the span's
# soak was accepted is its last soak step's rc, and no look code reads the stage journal.
SOAK_KINDS = ("slope", "load", "kind not recorded")
SOAK_KIND_FIELDS = ("refusal_kind",)


def soak_fields(receipt):
    """The receipt fields the soak-retry print reads, as level R carries them (fit_interim stage 1 computes the print
    from level R, so the twin can): whether ``soak_attempts`` is present, its value, and the receipt's soak steps
    ({"name", "rc"} of each step named "soak" or "soak.a<n>"). The ruled soak_refusals array is normalized into
    the matching attempt's soak_refusals_kind field; old receipts keep the same projection."""
    steps = [{"name": st.get("name"), "rc": st.get("rc")} for st in receipt.get("steps") or []
             if isinstance(st, dict) and re.fullmatch(r"soak(\.a\d+)?", str(st.get("name")))]
    attempts = receipt.get("soak_attempts")
    refusals = receipt.get("soak_refusals")
    if refusals is not None:
        if (not isinstance(refusals, list) or any(
                not isinstance(r, dict) or set(r) != {"attempt", "kind"}
                or not isinstance(r["attempt"], int) or isinstance(r["attempt"], bool)
                or r["attempt"] < 1 or r["kind"] not in ("slope", "load") for r in refusals)
                or len({r["attempt"] for r in refusals}) != len(refusals)):
            raise ValueError("runner_receipt.json soak_refusals: unique {attempt, kind}, kind slope or load")
        if refusals and (not isinstance(attempts, list) or any(not isinstance(a, dict) for a in attempts)):
            raise ValueError("runner_receipt.json soak_refusals: soak_attempts must be recorded objects")
        attempts = [dict(a) for a in attempts] if isinstance(attempts, list) else attempts
        for r in refusals:
            a = next((a for a in attempts or [] if isinstance(a, dict) and a.get("attempt") == r["attempt"]), None)
            if a is None or a.get("refused") is None:
                raise ValueError("runner_receipt.json soak_refusals: each entry names a refused soak attempt")
            a["soak_refusals_kind"] = r["kind"]
    return {"field_present": "soak_attempts" in receipt, "soak_attempts": attempts, "soak_steps": steps}


def soak_attempts_of(span_id, fields):
    """(attempts, field present, accepted) from a span's soak fields. Each attempt is checked against the receipt's
    soak steps: numbered from 1, one step per attempt in order, every refused attempt's step nonzero."""
    if not fields["field_present"]:
        return [{"attempt": 1, "refused": None}], False, True
    attempts, steps = fields["soak_attempts"], fields["soak_steps"]
    names = ["soak" if i == 0 else f"soak.a{i + 1}" for i in range(len(attempts) if isinstance(attempts, list) else 0)]
    if (not isinstance(attempts, list) or [st["name"] for st in steps] != names or any(
            not isinstance(a, dict) or a.get("attempt") != i + 1
            or not (a.get("refused") is None or isinstance(a.get("refused"), str))
            or (a.get("refused") is None and i != len(attempts) - 1)
            or (a.get("refused") is not None and steps[i].get("rc") in (0, None)) for i, a in enumerate(attempts))):
        raise ValueError(f"{span_id}: runner_receipt.json soak_attempts does not match its soak steps "
                         "(numbered attempts, each refused but the last, one soak step each)")
    accepted = bool(attempts) and attempts[-1].get("refused") is None and steps[-1].get("rc") == 0
    return attempts, True, accepted


def soak_attempts(sdir):
    """soak_attempts_of on the span directory's receipt."""
    return soak_attempts_of(Path(sdir).name, soak_fields(_json(Path(sdir) / "runner_receipt.json")))


def soak_refusal_kind(attempt):
    """("slope" | "load" | "kind not recorded", the receipt field it was read from or None)."""
    if attempt.get("soak_refusals_kind") in ("slope", "load"):
        return attempt["soak_refusals_kind"], "receipt soak_refusals[].kind"
    for field in SOAK_KIND_FIELDS:
        if attempt.get(field) in ("slope", "load"):
            return attempt[field], f"receipt soak_attempts[].{field}"
    return "kind not recorded", None


def soak_retries_from(fields_by_span):
    """The look's soak-retry print (RL-172a) from each span's soak fields: per span, its attempts and the kinds of
    the retried ones; in sum, the spans with a retry, the retried soaks by kind, the spans accepted after a retry and
    those the soak stopped."""
    spans, by_kind = {}, {k: 0 for k in SOAK_KINDS}
    for span_id, fields in sorted(fields_by_span.items()):
        attempts, recorded, accepted = soak_attempts_of(span_id, fields)
        retried = []
        for a in attempts[:-1]:                     # every attempt with a successor was retried
            kind, source = soak_refusal_kind(a)
            by_kind[kind] += 1
            retried.append({"attempt": a["attempt"], "kind": kind, "read_from": source})
        spans[span_id] = {"attempts": len(attempts), "field_present": recorded, "accepted": accepted,
                          "retried": retried}
    return {"spans": spans, "spans_with_retry": sum(1 for v in spans.values() if v["retried"]),
            "retried_by_kind": by_kind,
            "accepted_after_retry": sum(1 for v in spans.values() if v["retried"] and v["accepted"]),
            "stopped_by_soak": sum(1 for v in spans.values() if v["attempts"] and not v["accepted"])}


def soak_retries(span_dirs_by_id):
    """soak_retries_from on each span directory's receipt."""
    return soak_retries_from({sid: soak_fields(_json(Path(sdir) / "runner_receipt.json"))
                              for sid, sdir in span_dirs_by_id.items()})


def judge_custody(roster, sdir_of, selected_keys):
    """The verdict file and its detail for every roster span (``manifest.resolve_roster``'s list)."""
    verdicts, detail, trailers = {}, {}, []
    for entry in roster:
        v, d, t = judge_span(sdir_of(entry["span_id"]), entry["span_id"], selected_keys)
        verdicts.update(v)
        detail.update(d)
        trailers += t
    soaks = soak_retries({e["span_id"]: Path(sdir_of(e["span_id"])) for e in roster})
    return verdicts, {"legs": detail, "span_trailers": trailers, "soak_retries": soaks}


def _write(path, doc):
    import hashlib
    text = json.dumps(doc, indent=1, sort_keys=True, allow_nan=False) + "\n"
    Path(path).write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _fresh_bytecode_cache():
    """Mythos round-4 N4, Sol round-4 NEW-2: -B stops Python writing bytecode, not reading it. A fresh, empty
    pycache prefix (removed at exit) means no repository module can run from a stale __pycache__ entry beside its
    pinned source: each compiles from the bytes verify_pins hashes. Called before the first repository import when
    the file runs as a program; manifest.cached_bytecode() confirms it before custody opens."""
    import atexit
    import shutil
    import tempfile
    sys.dont_write_bytecode = True
    prefix = tempfile.mkdtemp(prefix="jw-look-pyc-")
    sys.pycache_prefix = prefix
    atexit.register(shutil.rmtree, prefix, True)


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Rules 3 and 4 at the look (RL-166 Q7): the verdict file. No energy.")
    p.add_argument("--roster", required=True)
    p.add_argument("--custody", required=True)
    p.add_argument("--span-dir", action="append", default=[])
    p.add_argument("--manifest", required=True, help="the look manifest; every pin is verified before custody is opened")
    p.add_argument("--allow-draft", action="store_true", help="synthetic runs only: a draft manifest")
    p.add_argument("--ledger-ref", help="the remote-tracking branch the committed LOOKS.json must be on (default: the "
                                        "upstream, else origin/main; never HEAD or a local ref: manifest.shared_ref)")
    p.add_argument("--out", required=True)
    p.add_argument("--detail-out")
    a = p.parse_args(argv)
    if str(REPO) not in sys.path:                 # -I drops the repository from sys.path
        sys.path.insert(0, str(REPO))
    from joulewise.cadence_looks import manifest as lm
    try:
        doc = lm.verify_pins(a.manifest, REPO, allow_draft=a.allow_draft,
                             running=[Path(__file__).resolve(), REPO / RUNTIME_CONFIG], ledger_ref=a.ledger_ref)
        gate = None if a.allow_draft else lm.ledger_gate(REPO, a.ledger_ref)
        stale = lm.cached_bytecode(REPO)
        if stale:
            raise lm.ManifestError([f"a repository module may have run from cached bytecode: {', '.join(stale[:4])}"])
    except lm.ManifestError as error:
        for problem in error.problems:
            print(f"REFUSE {problem}")
        return 1
    roster = _json(a.roster)
    if not isinstance(roster, list):
        print("REFUSE the roster is a JSON list (validate --span-ledger --roster-out writes it)")
        return 1
    sdir_of = span_dirs(a.custody, a.span_dir)
    if a.allow_draft:
        # Mythos N2: --allow-draft is for synthetic custody only (every span's receipt says so)
        real = [e["span_id"] for e in roster
                if _json(Path(sdir_of(e["span_id"])) / "runner_receipt.json").get("synthetic") is not True]
        if real:
            print(f"REFUSE --allow-draft on custody that is not synthetic: {', '.join(real[:5])}")
            return 1
    selected = keys(_json(REPO / RUNTIME_CONFIG)["sensors"])
    try:
        verdicts, detail = judge_custody(roster, sdir_of, selected)
    except Exception as exc:                      # type and line only: a message could carry a value
        if any(c.__name__ == "TimeFieldError" for c in type(exc).__mro__):    # time_fields' refusal names a file and a field, never a value
            print(f"REFUSE {exc}")
            return 1
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        print(f"FAILED {type(exc).__name__} at line {tb.tb_lineno}")
        return 2
    unpinned = lm.unpinned_loaded_modules(doc, REPO)                 # Mythos N6
    if unpinned:
        print("REFUSE loaded repository modules the manifest does not pin: " + ", ".join(unpinned[:6]))
        return 1
    verdicts_sha = _write(a.out, verdicts)
    print(f"wrote {a.out} sha256={verdicts_sha} legs={len(verdicts)} roster_sha256={lm.sha256_file(a.roster)}")
    detail["pins"] = {"manifest_sha256": lm.sha256_file(a.manifest), "look_id": doc["look_id"],
                      "inclusion_34_sha256": lm.sha256_file(Path(__file__).resolve()),
                      "runtime_config_sha256": lm.sha256_file(REPO / RUNTIME_CONFIG),
                      "code_sha256": lm.loaded_repo_files(REPO)}
    detail["allow_draft"] = bool(a.allow_draft)
    detail["ledger_gate"] = gate
    # Mythos round-3 N8: the lead commits these two hashes in LOOKS.json before stage 1, which checks them
    detail["roster_sha256"] = lm.sha256_file(a.roster)
    detail["verdicts_sha256"] = verdicts_sha
    if a.detail_out:
        print(f"wrote {a.detail_out} sha256={_write(a.detail_out, detail)}")
    return 0


if __name__ == "__main__":
    _fresh_bytecode_cache()
    raise SystemExit(main())
