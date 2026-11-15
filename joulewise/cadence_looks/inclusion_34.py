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
* inside the leg's interval, the count of sample lines is at least 99 % of the header's nominal poll
  rate (1 / poll_s) times the interval;
* no gap over 2 s between consecutive sample stamps, the interval's edges included.

The trailer's counts are printed in the inclusion table (``span_trailers``) and decide nothing. RL-166
refused the "trailer counts zero" clause.

**What is read.**
* From each KM003C sample line (``{"k":"b",...}``), only its ``rt`` stamp (CLOCK_REALTIME ns at receipt),
  taken with a fixed-prefix regular expression. The line is never JSON-decoded, and its sample bytes,
  SMC values and counts are never kept, logged or copied.
* Error lines (``{"k": "e", ...}``) are skipped unread.
* Only the header and the trailer are decoded, as the runner already does (RL-150 R8).
* From ``rich_telemetry.jsonl``, only ``timestamp_s`` and ``elapsed_ns``. A JSON hook drops every other key
  as it is decoded, so no power or energy value reaches any structure this module keeps.
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

_SAMPLE_LINE_RE = re.compile(rb'^\{"k":"b","tx":\d+,"rx":\d+,"rt":(\d+),')
_ERROR_LINE_PREFIX = b'{"k": "e"'


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
    """Rule 4 on one leg. ``streams`` = [{"name", "header", "trailer", "stamps"}] from ``read_meter_stream``
    (stamps = sorted rt ns). Returns {"pass", "coverage_fraction", "max_gap_s", "streams", "reasons"}."""
    reasons = []
    out = {"pass": False, "coverage_fraction": None, "max_gap_s": None, "streams": [], "reasons": reasons}
    if interval_ns is None or interval_ns[1] <= interval_ns[0]:
        reasons.append("no leg interval (G0 start or last stamped token missing)")
        return out
    a, b = interval_ns
    overlapping, stamps, poll_s = [], [], set()
    for s in streams:
        header, trailer = s.get("header"), s.get("trailer")
        start = (header or {}).get("start_real_ns")
        end = s["stamps"][-1] if s["stamps"] else start
        if start is not None and (end is None or end < a or start > b):
            continue
        overlapping.append(s)
        out["streams"].append(s["name"])
        if header is None or header.get("status") != "streaming":
            reasons.append(f"{s['name']}: no streaming header")
        else:
            poll_s.add(header.get("poll_s"))
        if trailer is None:
            reasons.append(f"{s['name']}: no trailer")
        elif not normal_stop(trailer.get("stop_reason")):
            reasons.append(f"{s['name']}: stop reason {trailer.get('stop_reason')!r} is not a normal stop")
        stamps.extend(t for t in s["stamps"] if a <= t <= b)
    if not overlapping:
        reasons.append("no meter stream covers the leg's interval")
    poll_s.discard(None)
    if len(poll_s) != 1 or not all(isinstance(p, (int, float)) and p > 0 for p in poll_s):
        reasons.append("the header's nominal poll period is missing or differs between streams")
    else:
        expected = (b - a) / NS / poll_s.pop()
        out["coverage_fraction"] = len(stamps) / expected if expected > 0 else None
        if out["coverage_fraction"] is None or out["coverage_fraction"] < METER_MIN_COVERAGE:
            reasons.append("meter coverage under 99 % of the nominal rate")
    points = sorted({a, b, *stamps})
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
    """{"name", "header", "trailer", "stamps"} for one KM003C stream. Sample lines give their rt stamp only
    and are never decoded; error lines are skipped; header and trailer are decoded (RL-150 R8)."""
    path = Path(path)
    header = trailer = None
    stamps, first, last_other = [], True, None
    for raw in _jsonl_lines(path):
        m = _SAMPLE_LINE_RE.match(raw)
        if m:
            stamps.append(int(m.group(1)))
        elif raw.startswith(_ERROR_LINE_PREFIX) or raw.startswith(b'{"k":"b"'):
            pass                                  # an error line, or a sample line in an unknown form: unread
        else:
            doc = json.loads(raw)
            if first and doc.get("k") == "h":
                header = doc
            elif doc.get("k") == "t":
                last_other = doc
        first = False
    if last_other is not None:
        trailer = last_other
    stamps.sort()
    return {"name": path.name, "header": header, "trailer": trailer, "stamps": stamps}


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


def read_pm_supports(bundle):
    """[{start_ns, end_ns}] from rich_telemetry.jsonl: timestamp_s is the sample's end (D-078), elapsed_ns
    its length, as thermal_desk.native_pm_samples builds the supports. Every other key is dropped while the
    line is decoded."""
    hook = _keep({"timestamp_s", "elapsed_ns"})
    out = []
    for raw in _jsonl_lines(Path(bundle) / "rich_telemetry.jsonl"):
        d = json.loads(raw, object_pairs_hook=hook)
        if "timestamp_s" in d and "elapsed_ns" in d:
            end = round(float(d["timestamp_s"]) * NS)
            out.append({"start_ns": end - int(d["elapsed_ns"]), "end_ns": end})
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


def read_leg_interval(bundle):
    """(G0 start, last stamped token) in wall-clock ns from events.jsonl, or None. The G0 start is the
    phase_start of the leg's align_thermal_gate with metadata kind G0 (thermal_gates.py); the last token is
    the latest token event's stamp. Only these fields are kept."""
    hook = _keep({"event_type", "phase", "timestamp_s", "metadata", "kind"})
    g0, last = None, None
    for raw in _jsonl_lines(Path(bundle) / "events.jsonl"):
        e = json.loads(raw, object_pairs_hook=hook)
        et, ts = e.get("event_type"), e.get("timestamp_s")
        if not isinstance(ts, (int, float)):
            continue
        if et == "token":
            last = ts if last is None else max(last, ts)
        elif (et == "phase_start" and e.get("phase") == "align_thermal_gate"
              and (e.get("metadata") or {}).get("kind") == "G0" and g0 is None):
            g0 = ts
    if g0 is None or last is None:
        return None
    return round(g0 * NS), round(last * NS)


def pm_period_s(bundle):
    """1 / sampling.power_hz of the bundle's config.json, as thermal_desk.read_bundle_record takes it."""
    cfg = json.loads((Path(bundle) / "config.json").read_text(encoding="utf-8"),
                     object_pairs_hook=_keep({"sampling", "power_hz"}))
    hz = (cfg.get("sampling") or {}).get("power_hz")
    return 1 / hz if isinstance(hz, (int, float)) and hz > 0 else None


def judge_leg(bundle, meter_streams, selected_keys, *, period_s=None):
    """Rules 3 and 4 for one leg's accepted attempt. ``meter_streams`` are ``read_meter_stream`` results for
    the span. ``selected_keys`` = ``keys(policy sensors)`` of the leg's runtime config. Opens events.jsonl,
    outputs/align_thermal.jsonl, rich_telemetry.jsonl (stamps) and config.json; no energy file."""
    interval = read_leg_interval(bundle)
    period = period_s if period_s is not None else pm_period_s(bundle)
    return {"rule3": rule3(interval, read_sidecar_rows(bundle), selected_keys, read_pm_supports(bundle), period),
            "rule4": rule4(interval, meter_streams)}


# ------------------------------------------------------------------------------------------------------------
# Custody mode: the verdict file the stage-1 CLI reads (docs/process/cadence_look_fit_interface.md section 7).
#
#     python3 -I -m joulewise.cadence_looks.inclusion_34 --roster ROSTER.json --custody ROOT
#         [--span-dir SPAN_ID=PATH ...] [--runtime-config configs/align/v4/r1_runtime.json]
#         --out VERDICTS.json [--detail-out DETAIL.json]
#
# VERDICTS.json is {"<span_id>/<leg_id>": {"sidecar_coverage": bool, "km003c_clean": bool}}, one entry per leg
# of each roster span's runner_receipt.json roster. A leg with no leg_record.json, or no accepted bundle, gets
# both false. DETAIL.json carries each leg's rule_detail and each span's trailer counts; it is a print.
# Opens per span: runner_receipt.json, hazards/meter/stream-*.jsonl (stamps, header, trailer); per leg:
# leg_record.json; per accepted bundle: events.jsonl, outputs/align_thermal.jsonl, rich_telemetry.jsonl (two
# keys) and config.json. Never power_trace.csv or raw/powermetrics.plist.

VERDICT_KEYS = ("sidecar_coverage", "km003c_clean")
DEFAULT_RUNTIME_CONFIG = "configs/align/v4/r1_runtime.json"


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def span_dirs(custody, overrides=()):
    """span_id -> directory: <custody>/<span_id> unless SPAN_ID=PATH overrides it (as the stage-1 CLI)."""
    extra = dict(o.split("=", 1) for o in overrides)
    return lambda span_id: Path(extra[span_id]) if span_id in extra else Path(custody) / span_id


def judge_span(sdir, span_id, selected_keys):
    """({leg_key: {sidecar_coverage, km003c_clean}}, {leg_key: detail}, trailers) for one span directory."""
    sdir = Path(sdir)
    streams = [read_meter_stream(p) for p in sorted((sdir / "hazards" / "meter").glob("stream-*.jsonl"))]
    verdicts, detail = {}, {}
    for leg_id in _json(sdir / "runner_receipt.json")["roster"]:
        key = f"{span_id}/{leg_id}"
        record = sdir / "legs" / leg_id / "leg_record.json"
        bundle = None
        if record.is_file():
            name = (_json(record).get("result") or {}).get("bundle")
            if isinstance(name, str) and name and (sdir / "legs" / leg_id / "runtime" / name).is_dir():
                bundle = sdir / "legs" / leg_id / "runtime" / name
        if bundle is None:
            verdicts[key] = {k: False for k in VERDICT_KEYS}
            detail[key] = {"rule3": {"reasons": ["no accepted bundle"]}, "rule4": {"reasons": ["no accepted bundle"]}}
            continue
        v = judge_leg(bundle, streams, selected_keys)
        verdicts[key] = {"sidecar_coverage": v["rule3"]["pass"], "km003c_clean": v["rule4"]["pass"]}
        detail[key] = {r: {k: x for k, x in v[r].items() if k != "pass"} for r in ("rule3", "rule4")}
    return verdicts, detail, span_trailers(span_id, streams)


def judge_custody(roster, sdir_of, selected_keys):
    """The verdict file and its detail for every roster span (``manifest.resolve_roster``'s list)."""
    verdicts, detail, trailers = {}, {}, []
    for entry in roster:
        v, d, t = judge_span(sdir_of(entry["span_id"]), entry["span_id"], selected_keys)
        verdicts.update(v)
        detail.update(d)
        trailers += t
    return verdicts, {"legs": detail, "span_trailers": trailers}


def _write(path, doc):
    import hashlib
    text = json.dumps(doc, indent=1, sort_keys=True, allow_nan=False) + "\n"
    Path(path).write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Rules 3 and 4 at the look (RL-166 Q7): the verdict file. No energy.")
    p.add_argument("--roster", required=True)
    p.add_argument("--custody", required=True)
    p.add_argument("--span-dir", action="append", default=[])
    p.add_argument("--runtime-config", default=DEFAULT_RUNTIME_CONFIG)
    p.add_argument("--out", required=True)
    p.add_argument("--detail-out")
    a = p.parse_args(argv)
    roster = _json(a.roster)
    roster = roster["roster"] if isinstance(roster, dict) else roster
    selected = keys(_json(a.runtime_config)["sensors"])
    try:
        verdicts, detail = judge_custody(roster, span_dirs(a.custody, a.span_dir), selected)
    except Exception as exc:                      # type and line only: a message could carry a value
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        print(f"FAILED {type(exc).__name__} at line {tb.tb_lineno}")
        return 2
    print(f"wrote {a.out} sha256={_write(a.out, verdicts)} legs={len(verdicts)}")
    if a.detail_out:
        print(f"wrote {a.detail_out} sha256={_write(a.detail_out, detail)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
