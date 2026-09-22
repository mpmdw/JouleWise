#!/usr/bin/env python3
"""Desk harness for QUIET-PREDICATE-EVIDENCE-01; never admission authority.

Live collect/load belong to a lead-controlled, agent-free bench. Offline
summaries are descriptive and install no cutoff. Example:
  python3 -B scripts/sample_quiet_predicate_evidence.py collect --state idle \
      --repeat 1 --duration-s 480 --sample-interval-s 30 --out evidence/idle-1
  python3 -B scripts/sample_quiet_predicate_evidence.py load --cores .2 \
      --duration-s 600 --period-ms 100 --qos background --profile scalar \
      --seed 1 --log load.json
  python3 -B scripts/sample_quiet_predicate_evidence.py summarize --in evidence \
      --reference-state idle

Imports the actual smoke round (run_night.py:2603-2712), including hard checks,
census, framed worker transport, journal ACK and reaping. Only the sample argv
is redirected to this file's instrumented public sample_interval wrapper. Its
pipe is supplied by the driver's _BindTask, not stdout. The full observation is
unchanged. Local module proxies capture raw tools and bracket wall reads; no
production source is copied or edited (quiet_admission.py:231-278).

Alignment imports the production rate-aware anchor. It requires >=60 s of
native support, early first-parse observation, energy counters and is_delta;
unresolved evidence stays null with the production reason. No arrival-time or
linear fallback is silently substituted. Like the adapter, endpoints advance
by elapsed_ns after record zero (powermetrics.py:1775-1785, 2009-2025).
The bound is conditional on the anchor's affine clock model AND on network
time being OFF for the whole capture.  The collector does not toggle it: the
evidence chain establishes OFF before settle and names its receipt in
EVIDENCE_NETWORK_TIME_RECORD, which this collector reads and records as
structured provenance.  With no readable receipt the envelope is refused
before powermetrics is spawned (exit 3); provenance is never null.  Every
artifact remains PROVISIONAL desk evidence.

Schema joulewise.quiet_predicate_evidence.v1 adds per-round censuses (source,
job_id and unchanged result), census_errors, and census_clean. Clean is true
only when all available concurrent/sampler censuses report absence; a hit is
false and missing/failed evidence is null with a reason. Summary groups and
reference comparisons keep true, false and unknown census conditions separate.
Rows also retain every hard-probe worker response (including failed AC and
thermal probes) and copy the validated session OS build. These are recorded
evidence, not admission decisions; missing evidence remains explicitly unknown.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import ctypes
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import quiet_admission
from joulewise.adapters import powermetrics as pm
from joulewise.arm_readiness import EXPECTED_NETWORK_TIME_OFF_STDOUT
from joulewise.clock import ClockStamp
from joulewise.uncertainty_evidence import (
    CLOCK_METHOD_V3_1, NativeAnchorRecord, derive_powermetrics_anchor_v3,
)

SCHEMA = "joulewise.quiet_predicate_evidence.v1"
# Cold gate 2026-09-22, ruling 10 Q1 rule 3: the evidence chain establishes
# network time OFF before settle and names its receipt in this variable.  A
# collector that cannot read and match that receipt refuses the envelope
# before powermetrics is spawned; it never records an unknown clock regime as
# if it were a measurement.
NETWORK_TIME_RECORD_ENV = "EVIDENCE_NETWORK_TIME_RECORD"
NETWORK_TIME_REFUSAL = "network_time_provenance"
NETWORK_TIME_REFUSAL_EXIT = 3
NETWORK_TIME_PROVENANCE_METHOD = "systemsetup_setusingnetworktime_off_exact_stdout"
NETWORK_TIME_PROVENANCE_REASON = "established by the evidence chain before settle"
ALIGNMENT_MODEL = "affine wall clock; production rate-aware bound; PROVISIONAL"
RAILS = ("cpu_w", "gpu_w", "ane_w", "rail_sum_w", "combined_w", "dram_w")
ROUND_KEYS = (
    "schema", "session", "state", "repeat", "round", "status", "error",
    "epoch_s", "boot_id", "os_build", "os_build_valid", "load_setting", "round_wall_start_s",
    "round_wall_end_s", "round_mono_start_s", "round_mono_end_s",
    "observation", "observer_cpu_s", "power", "clusters", "cpus",
    "alignment", "raw", "censuses", "census_clean", "census_errors",
    "hard_probes", "hard_probe_errors",
)


def reasons(value, reason="not available in source evidence"):
    """Every null object field has a sibling <field>_reason, recursively."""
    if isinstance(value, dict):
        result = {key: reasons(item, reason) for key, item in value.items()}
        for key, item in list(result.items()):
            if item is None:
                result.setdefault(key + "_reason", reason)
        return result
    if isinstance(value, list):
        return [reasons(item, reason) for item in value]
    return value


def write_json(path, value):
    path.write_text(json.dumps(reasons(value), sort_keys=True, indent=2,
                               allow_nan=False) + "\n")


def number(value):
    return (float(value) if type(value) in (float, int)
            and math.isfinite(value) else None)


def os_build_identity(value):
    """Validate a recorded build label without guessing it from another field."""
    if (not isinstance(value, str) or not value or value != value.strip()
            or any(character.isspace() or not character.isprintable() for character in value)):
        return None, "OS build missing or malformed in session metadata"
    return value, None


class Clock:
    monotonic = staticmethod(time.monotonic)
    cpu = staticmethod(time.thread_time)
    sleep = staticmethod(time.sleep)

    def stamp(self):
        lo = self.monotonic()
        wall = time.time()
        hi = self.monotonic()
        return ClockStamp(wall, lo, hi, time.get_clock_info("time").resolution,
                          time.get_clock_info("monotonic").resolution)

    def sleep_until(self, deadline):
        while (left := deadline - self.monotonic()) > 0:
            self.sleep(left)


def cpu_total():
    return sum(u.ru_utime + u.ru_stime for u in (
        resource.getrusage(resource.RUSAGE_SELF),
        resource.getrusage(resource.RUSAGE_CHILDREN)))


def command_text(argv):
    try:
        return subprocess.run(argv, check=True, capture_output=True, text=True,
                              timeout=5, env={**os.environ, "LC_ALL": "C"}).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(exc)


def identity(pid):
    result = command_text(["/bin/ps", "-p", str(pid), "-o", "lstart="])
    # ps pads single-digit days; parse_ps uses the same five tokens joined by
    # one space. Preserve identity across the two renderings, never across PID reuse.
    return reasons({"pid": pid, "start_identity": " ".join(result.split()) if isinstance(result, str) and result else None},
                   "ps lstart unavailable" if isinstance(result, str) else result[1])


def power_argv(path, interval_ms=100):
    """Use the production builder without adapter initialization or probes."""
    adapter = object.__new__(pm.PowermetricsTelemetryAdapter)
    adapter._privilege_prefix = ("sudo", "-n")
    adapter._executable = pm.POWER_METRICS
    return adapter._command(None, Path(path), count=None, interval_ms=interval_ms)


def residency(item, cpu=False):
    idle, down = number(item.get("idle_ratio")), number(item.get("down_ratio"))
    valid = idle is not None and down is not None and 0 <= idle + down <= 1.0000001
    freq = number(item.get("freq_hz"))
    # CPU/cluster dvfm freq is Hz; GPU dvfm freq is MHz and is not used here.
    if freq is None:
        states = [(number(s.get("freq")), number(s.get("used_ratio")))
                  for s in item.get("dvfm_states", []) if isinstance(s, dict)]
        states = [(f, w) for f, w in states if f is not None and w is not None and w > 0]
        if states:
            freq = math.fsum(f * w for f, w in states) / math.fsum(w for _, w in states)
    result = {"cpu" if cpu else "name": item.get("cpu" if cpu else "name"),
              "active_ratio": 1 - idle - down if valid else None, "freq_hz": freq}
    if not cpu:
        result.update(idle_ratio=idle, down_ratio=down,
                      online_ratio=number(item.get("online_ratio")))
    return reasons(result)


def parse_frames(data):
    """NUL-separated native plists; preserve the adapter's truncated-tail diagnostic."""
    documents, dropped = pm._powermetrics_documents(data)
    frames = []
    for doc in documents:
        elapsed = doc.get("elapsed_ns")
        native = doc.get("timestamp")
        if type(elapsed) is not int or elapsed <= 0 or not isinstance(native, datetime):
            raise ValueError("frame requires positive elapsed_ns and native datetime timestamp")
        if native.tzinfo is None:
            native = native.replace(tzinfo=timezone.utc)
        native_ns = pm._timestamp_epoch_ns_utc(native)
        processor = doc.get("processor", {})
        power = {}
        for rail in RAILS:
            if rail == "rail_sum_w":
                continue
            mw = number(processor.get(rail[:-2] + "_power"))
            power[rail] = mw / 1000 if mw is not None and mw >= 0 else None
        core_rails = [power[r] for r in RAILS[:3]]
        power["rail_sum_w"] = sum(core_rails) if all(v is not None for v in core_rails) else None
        energies = [number(processor.get(r + "_energy")) for r in ("cpu", "gpu", "ane")]
        energy = sum(energies) / 1000 if all(v is not None for v in energies) else None
        clusters = processor.get("clusters", [])
        frames.append({"native_timestamp_s": native.timestamp(), "native_timestamp_ns": native_ns,
                       "elapsed_ns": elapsed, "elapsed_s": elapsed / 1e9,
                       "is_delta": doc.get("is_delta"), "energy_j": energy,
                       "power": reasons(power, "rail absent or invalid in native frame"),
                       "clusters": [residency(c) for c in clusters],
                       "cpus": [residency(c, cpu=True) for group in clusters
                                for c in group.get("cpus", [])]})
    return frames, asdict(dropped) if dropped else None


def network_time_provenance(environ=None):
    """Read the chain's network-time receipt, or say exactly why there is none.

    Returns ``(provenance, reason)``.  ``provenance`` is ``None`` -- which the
    caller turns into a refusal before any child is launched -- when the
    environment variable naming the receipt is absent, the receipt cannot be
    read as JSON, or its recorded ``off`` result is not an exit-0 run whose
    stdout is EXACTLY ``joulewise.arm_readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT``.
    The comparator is imported, never retyped (ruling 10 Q1 rule 1), and the
    comparison is byte equality: the observed ``setUsingNetworkTime: off``
    (lower case) of a different code path is NOT a match.
    """

    environ = os.environ if environ is None else environ
    path = environ.get(NETWORK_TIME_RECORD_ENV)
    if not path:
        return None, f"{NETWORK_TIME_RECORD_ENV} is not set by the evidence chain"
    try:
        raw = Path(path).read_bytes()
        control = json.loads(raw)
        off = control["off"]
        stdout, exit_code = off["stdout"], off["exit_code"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return None, f"network time control record unreadable: {type(exc).__name__}: {exc}"
    if exit_code != 0 or stdout != EXPECTED_NETWORK_TIME_OFF_STDOUT:
        return None, ("network time OFF not proven by the control record: "
                      f"exit {exit_code!r}, stdout {stdout!r}")
    return {"state": "off", "method": NETWORK_TIME_PROVENANCE_METHOD,
            "established_epoch_s": off.get("epoch_s"),
            "established_monotonic_s": off.get("monotonic_s"),
            "record": Path(path).name,
            "record_sha256": hashlib.sha256(raw).hexdigest()}, NETWORK_TIME_PROVENANCE_REASON


def align_frames(frames, stamps, deriver=derive_powermetrics_anchor_v3):
    """Tile the native frames on the wall timeline in exact integer nanoseconds.

    Cold gate 2026-09-22, ruling 10 Q3 as worded by 14 R5: the anchor's only
    endpoint field is the binary64 ``first_sample_end_point_epoch_s``, so it is
    rounded ONCE here to integer nanoseconds and every later endpoint is an
    integer sum of the recorder's own integer ``elapsed_ns``.  Tiling in float
    epoch seconds mis-placed consecutive frames by up to one ulp each -- one
    UNIT IN THE LAST PLACE, the spacing between adjacent float64 values, which
    at epoch scale (1.8e9 s) is 238 ns -- and that is what the retired
    1 microsecond comparators were measuring.  The float ``start_s``/``end_s`` fields are kept for readers, but
    they are now DERIVED from the integers, never the other way round.

    The evidence consumer prices the anchor bound in joules, so it selects the
    v3.1 anchor identity (``method=CLOCK_METHOD_V3_1``; ruling 14 R2).
    """

    records = [NativeAnchorRecord(
        elapsed_s=f["elapsed_s"], native_timestamp_s=f["native_timestamp_s"],
        power_w=f["power"]["rail_sum_w"] if f["power"]["rail_sum_w"] is not None else math.nan,
        energy_j=f["energy_j"], is_delta=f["is_delta"],
        elapsed_ns=f["elapsed_ns"], native_timestamp_ns=f["native_timestamp_ns"])
        for f in frames]
    anchor = deriver(stamps=stamps, records=records, method=CLOCK_METHOD_V3_1)
    if anchor["status"] != "bounded":
        return [], anchor
    endpoint_ns = round(anchor["first_sample_end_point_epoch_s"] * 1e9)
    aligned, elapsed_ns = [], 0
    for i, frame in enumerate(frames):
        if i:
            elapsed_ns += frame["elapsed_ns"]
        end_ns = endpoint_ns + elapsed_ns
        start_ns = end_ns - frame["elapsed_ns"]
        aligned.append({**frame, "start_ns": start_ns, "end_ns": end_ns,
                        "start_s": start_ns / 1e9, "end_s": end_ns / 1e9})
    return aligned, anchor


def overlap(a, b, c, d):
    """Intersection length of [a,b] and [c,d]; exact on integer nanoseconds.

    The zero floor is the integer 0, so an all-integer call returns an exact
    integer count of nanoseconds and a float call is unchanged.
    """
    return max(0, min(b, d) - max(a, c))


def integrate_seconds(frames, start_s, end_s, uncertainty_s=0.0):
    """Float-seconds adapter: map the window ONCE, then integrate in integers.

    The round-level reduction in :func:`collect` is the only caller whose
    window exists solely as binary64 seconds (``round_wall_start_s`` /
    ``round_wall_end_s`` off the wall-clock stamps), so the seconds-to-integer
    mapping lives here instead of inside :func:`integrate`.  The endpoints are
    rounded to nearest; the uncertainty is rounded OUTWARD (ceiling) so the
    expanded round is never narrowed by the conversion -- an uncertainty of
    one picosecond still buys a full nanosecond of expansion.
    """

    if end_s <= start_s or uncertainty_s < 0:
        raise ValueError("invalid round support or alignment uncertainty")
    return integrate(frames, round(start_s * 1e9), round(end_s * 1e9),
                     math.ceil(uncertainty_s * 1e9))


def integrate(frames, start_ns, end_ns, uncertainty_ns=0):
    """Overlap seconds times watts; means divide by each rail's own coverage.

    For each averaging interval, moving either boundary by at most epsilon
    changes overlap by <=2*epsilon. Sum P_i*min(dt_i,2*epsilon) over frames
    touching the expanded round. This conservative interval-power bound does
    not shrink with sample count. Unobserved gaps have no finite energy bound.

    All interval arithmetic is exact integer nanoseconds (ruling 10 Q3 as
    worded by 14 R5), and the WINDOW ARRIVES AS INTEGERS: ``start_ns``,
    ``end_ns`` and ``uncertainty_ns`` are integer nanoseconds, the frame
    endpoints arrive as integers from ``align_frames``, ``coverage_ns`` and
    the per-rail coverage are integer sums, and the two former ``> 1e-6``
    comparators are exact equality.  They remain live fail-closed gap
    detectors, not dead code: under exact tiling any nonzero mismatch is a
    missing or duplicated frame interval, never rounding.  Seconds appear only
    at the ``P * w`` multiply and in the reported fields.

    The signature is integer because the float round trip is NOT the identity:
    mapping an epoch-scale integer to seconds and back is exact only when the
    value sits on the 256 ns float64 lattice at that magnitude.  It happens to
    be exact for the pilot's 480 s, 570 s and 600 s windows, and wrong by up
    to 128 ns for durations such as 12.345 s -- which, against an exact
    completeness gate, turns a fully covered interior into a partial one.

    Every caller in the repository: ``reduce_interior`` (which computes the
    interior window's integers itself and passes them straight through) and
    ``integrate_seconds``, the float adapter used by the round-level reduction
    in ``collect``.  There is no other call site.
    """
    if any(type(value) is not int for value in (start_ns, end_ns, uncertainty_ns)):
        raise TypeError("integrate takes integer nanoseconds")
    if end_ns <= start_ns or uncertainty_ns < 0:
        raise ValueError("invalid round support or alignment uncertainty")
    for left, right in zip(frames, frames[1:]):
        if right["start_ns"] < left["end_ns"]:
            raise ValueError("overlapping or unordered native supports")
    weighted = [(f, overlap(start_ns, end_ns, f["start_ns"], f["end_ns"])) for f in frames]
    coverage_ns = sum(w for _, w in weighted)
    energy, rail_coverage, rail_coverage_ns, bounds, power = {}, {}, {}, {}, {}
    for rail in RAILS:
        selected = [(f["power"][rail], w) for f, w in weighted
                    if w > 0 and f["power"][rail] is not None]
        den_ns = sum(w for _, w in selected)
        rail_coverage_ns[rail] = den_ns
        expanded_coverage_ns = sum(overlap(start_ns - uncertainty_ns, end_ns + uncertainty_ns,
            f["start_ns"], f["end_ns"]) for f in frames if f["power"][rail] is not None)
        joules = math.fsum(p * (w / 1e9) for p, w in selected)
        rail_coverage[rail] = den_ns / 1e9
        energy[rail] = joules if den_ns else None
        power[rail] = joules / (den_ns / 1e9) if den_ns else None
        bounds[rail] = (math.fsum(
            f["power"][rail] * (min(f["end_ns"] - f["start_ns"], 2 * uncertainty_ns) / 1e9)
            for f in frames if f["power"][rail] is not None
            and overlap(start_ns - uncertainty_ns, end_ns + uncertainty_ns, f["start_ns"], f["end_ns"]) > 0)
            if expanded_coverage_ns >= end_ns - start_ns + 2 * uncertainty_ns else None)
    power.update(coverage_s=coverage_ns / 1e9, rail_coverage_s=rail_coverage, energy_j=energy)
    def average_entities(kind, id_key, keys):
        ids = sorted({entry[id_key] for f, w in weighted if w > 0
                      for entry in f[kind] if entry[id_key] is not None}, key=str)
        result = []
        for entity in ids:
            row = {id_key: entity, "coverage_s": {}}
            for key in keys:
                values = [(entry[key], w) for f, w in weighted if w > 0 for entry in f[kind]
                          if entry[id_key] == entity and entry[key] is not None]
                den = sum(w for _, w in values)  # integer nanoseconds
                row[key] = math.fsum(v * w for v, w in values) / den if den else None
                row["coverage_s"][key] = den / 1e9
            result.append(reasons(row))
        return result
    return {
        "power": reasons(power, "no covered native samples for this rail"),
        "clusters": average_entities("clusters", "name", ("active_ratio", "idle_ratio", "down_ratio", "online_ratio", "freq_hz")) or None,
        "cpus": average_entities("cpus", "cpu", ("active_ratio", "freq_hz")) or None,
        "coverage_ns": coverage_ns, "rail_coverage_ns": rail_coverage_ns,
        "span_mismatch": coverage_ns != end_ns - start_ns,
        "error_bound_j": bounds["rail_sum_w"], "rail_error_bound_j": reasons(bounds, "incomplete rail coverage; unobserved energy is unbounded"),
    }


def reduce_interior(frames, anchor, start, duration):
    """Integrate native interval supports; never rescale a whole-round mean.

    The interior window is mapped to integer nanoseconds ONCE here, and the
    per-rail coverage check is exact integer equality against that window
    (ruling 10 Q3): a rail is complete only when its covered nanoseconds equal
    the window's, so a one-nanosecond hole is a partial interior, not a
    rounding artefact.

    Those integers go STRAIGHT to ``integrate``.  Handing them over as float
    seconds and re-rounding them there moved the window's width by up to
    128 ns for any duration off the 256 ns float64 lattice at epoch scale --
    exact for the pilot's 480 s, and enough to report a fully covered 12.345 s
    interior as partial.
    """
    result = {"start_epoch_s": start, "end_epoch_s": start + duration,
              "duration_s": duration, "complete_support": False, "status": "partial",
              "native_samples": 0, "power": None, "reason": "clock anchor unresolved"}
    if anchor.get("status") != "bounded":
        return reasons(result)
    start_ns = round(start * 1e9)
    duration_ns = round(duration * 1e9)
    end_ns = start_ns + duration_ns
    values = integrate(frames, start_ns, end_ns,
                       math.ceil(anchor["effective_clock_anchor_bound_s"] * 1e9))
    complete = (not values["span_mismatch"] and all(
        values["rail_coverage_ns"][rail] == duration_ns
        for rail in ("rail_sum_w", "combined_w")))
    result.update(values, complete_support=complete, status="complete" if complete else "partial",
                  native_samples=sum(overlap(start_ns, end_ns, f["start_ns"], f["end_ns"]) > 0 for f in frames),
                  reason="complete native support" if complete else "incomplete interior support")
    return reasons(result)


def join_load_log(row, report, before, after):
    """Join full raw ps counters by PID+lstart and the sampler's monotonic support.

    Requested share and top-ten attribution cannot substitute for this join.
    Period CPU is integrated only over its native support; gaps stay unknown.
    """
    start, end = (row.get("alignment", {}).get(k) for k in ("ps_start", "ps_end"))
    result = {"status": "unresolved", "workers": [], "reason": "load identity/support unavailable"}
    if (report.get("boot_id") != row.get("boot_id") or not row.get("boot_id") or
            report.get("error") or number(start) is None or number(end) is None or end <= start):
        return result
    cleanup = report.get("cleanup") or []
    if (not cleanup or any(c.get("alive") is not False or c.get("exitcode") != 0 for c in cleanup) or
            {c.get("pid") for c in cleanup} != {w.get("identity", {}).get("pid") for w in report.get("workers", [])}):
        result["reason"] = "load cleanup incomplete or escalated"
        return result
    span = end - start
    seen = set()
    for worker in report.get("workers", []):
        ident = worker.get("identity", {})
        start_identity = ident.get("start_identity")
        key = (ident.get("pid"), " ".join(start_identity.split()) if isinstance(start_identity, str) else None)
        item = {"identity": ident, "status": "unresolved", "reason": "identity missing from both ps endpoints"}
        if key in seen:
            raise ValueError("duplicate load worker identity")
        seen.add(key)
        first, last = before.get(key), after.get(key)
        periods = worker.get("periods", [])
        if first and last and key[1]:
            support, cpu, calibration, overrun = 0.0, 0.0, 0.0, 0.0
            first_cpu = last_cpu = 0.0
            previous = None
            for period in periods:
                lo, hi, used = (number(period.get(k)) for k in ("start_mono_s", "end_mono_s", "cpu_used_s"))
                if lo is None or hi is None or used is None or hi <= lo or used < 0 or (previous is not None and lo < previous - 1e-6):
                    raise ValueError("invalid or overlapping load period support")
                previous = hi
                covered = overlap(start, end, lo, hi)
                if period.get("calibrating"):
                    calibration += covered
                    continue
                support += covered
                cpu += used * covered / (hi - lo)
                first_cpu += used * overlap(start, start + span / 3, lo, hi) / (hi - lo)
                last_cpu += used * overlap(end - span / 3, end, lo, hi) / (hi - lo)
                if number(period.get("overrun_cpu_s")) is not None:
                    overrun += period["overrun_cpu_s"] * covered / (hi - lo)
            delta = last["cumulative_cpu_seconds"] - first["cumulative_cpu_seconds"]
            item.update(support_s=support, sampled_cpu_s=delta, delivered_cpu_s=cpu,
                        calibration_overlap_s=calibration, overrun_cpu_s=overrun,
                        first_last_delta_cores=(last_cpu - first_cpu) / (span / 3),
                        worker_stationarity=worker.get("stationarity"),
                        delivered_busy_cores=cpu / span, sampled_busy_cores=delta / span,
                        support_model="interval-average CPU delivery over native load periods")
            if abs(support - span) <= 1e-6 and delta >= 0:
                item.update(status="joined", reason="worker identity and monotonic support matched")
            else:
                item["reason"] = "incomplete load support or regressed process counter"
        result["workers"].append(item)
    if result["workers"] and all(w["status"] == "joined" for w in result["workers"]):
        result.update(status="joined", reason="all load workers matched",
                      delivered_busy_cores=sum(w["delivered_busy_cores"] for w in result["workers"]),
                      sampled_busy_cores=sum(w["sampled_busy_cores"] for w in result["workers"]))
    return result


@contextmanager
def replaced(module, **attributes):
    old = {key: getattr(module, key) for key in attributes}
    try:
        for key, value in attributes.items():
            setattr(module, key, value)
        yield
    finally:
        for key, value in old.items():
            setattr(module, key, value)


def sample_worker(args):
    """Production public sampler + raw/stamp hooks, on the driver's framed FD."""
    raw_dir = Path(args.raw_dir)
    clock, records, wall_reads, marks = Clock(), [], [], {}
    pending = None
    ps_count = 0

    def wall():
        stamp = clock.stamp()
        wall_reads.append(asdict(stamp))
        return stamp.epoch_s

    def mono():
        nonlocal pending
        value = clock.monotonic()
        if pending:
            marks[pending] = value
            pending = None
        return value

    def run(argv, **kwargs):
        nonlocal ps_count, pending
        before = clock.stamp()
        value = subprocess.run(argv, **kwargs)
        after = clock.stamp()
        label = f"tool-{len(records):02d}"
        if tuple(argv) == quiet_admission.PS_ARGV:
            label = "ps_before" if ps_count == 0 else "ps_after"
            pending = "ps_start" if ps_count == 0 else "ps_end"
            ps_count += 1
        elif argv[0] == "/usr/bin/top":
            label = "top"
            marks.update(top_start=before.monotonic_before_s, top_end=after.monotonic_after_s)
        path = raw_dir / (label + ".txt")
        path.write_text(value.stdout or "")
        records.append({"argv": list(argv), "start": asdict(before), "end": asdict(after),
                        "returncode": value.returncode, "stderr": value.stderr,
                        "path": str(path.name), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        write_json(raw_dir / "sampler.json", {"tools": records, "wall_reads": wall_reads, "marks": marks})
        return value

    def call():
        write_json(raw_dir / "sampler-identity.json", identity(os.getpid()))
        with replaced(quiet_admission, time=SimpleNamespace(time=wall, monotonic=mono),
                      subprocess=SimpleNamespace(run=run, SubprocessError=subprocess.SubprocessError)):
            try:
                return quiet_admission.sample_interval(args.sample_interval_s, observer_pid=args.observer_pid)
            finally:
                write_json(raw_dir / "sampler.json", {"tools": records, "wall_reads": wall_reads, "marks": marks})
    quiet_admission.publish_observation(args.result_fd, args.job_id, call)
    return 0


class CollectionExpired(Exception):
    pass


def production_round(interval_s, deadline, raw_dir, clock):
    from scripts import run_night
    tasks, argv_records = [], []
    old_task, old_argv = run_night._BindTask, run_night._bind_argv
    temporary_directory = tempfile.TemporaryDirectory

    def round_directory(*args, **kwargs):
        # The production smoke imports tempfile locally. Confine its journals
        # without changing production code or process-wide TMPDIR selection.
        return temporary_directory(*args, **{**kwargs, "dir": raw_dir})
    start_cpu = cpu_total()
    observation = error = None
    censuses, census_errors = [], []
    hard_probes, hard_probe_errors = [], []
    status = "complete"

    def task(*args, **kwargs):
        result = old_task(*args, **kwargs)
        tasks.append(result)
        return result

    def argv(kind, job_id, descriptor, request):
        result = list(old_argv(kind, job_id, descriptor, request))
        if kind == "sample":
            result = [sys.executable, "-B", str(Path(__file__).resolve()), "_sample",
                      "--sample-interval-s", str(interval_s), "--observer-pid", str(os.getpid()),
                      "--job-id", job_id, "--result-fd", str(descriptor), "--raw-dir", str(raw_dir)]
        result = [sys.executable, "-B", str(Path(__file__).resolve()), "_exec",
                  str(raw_dir / (job_id + "-identity.json")), *result]
        argv_records.append({"job_id": job_id, "argv": result})
        return result

    def sleep(seconds):
        if clock.monotonic() >= deadline:
            raise CollectionExpired("collection duration reached during round")
        clock.sleep(min(seconds, max(0, deadline - clock.monotonic())))
        if clock.monotonic() >= deadline:
            raise CollectionExpired("collection duration reached during round")

    try:
        with replaced(tempfile, TemporaryDirectory=round_directory), \
                replaced(run_night, _BindTask=task, _bind_argv=argv,
                      time=SimpleNamespace(monotonic=clock.monotonic, sleep=sleep)):
            observation, _cost = run_night.smoke_observation_round(interval_s)
    except CollectionExpired as exc:
        status, error = "partial", str(exc)
    except Exception as exc:
        status, error = "error", f"{type(exc).__name__}: {exc}"
    finally:
        support_end = clock.stamp()
        if observation is None:
            for job in tasks:
                if job.job_id.startswith("sample-") and job.ready():
                    try:
                        observation = job.result()
                    except Exception:
                        pass  # The round error and raw transport remain available.
        for job in tasks:
            if job.job_id.startswith("census-"):
                if job.ready():
                    try:
                        censuses.append({"source": "concurrent", "job_id": job.job_id,
                                         "result": job.result()})
                    except Exception as exc:
                        census_errors.append({"job_id": job.job_id, "error": str(exc)})
                else:
                    census_errors.append({"job_id": job.job_id, "error": "census did not complete during round"})
            elif job.job_id.startswith("smoke-hard-"):
                # The smoke loop intentionally ignores these values because
                # it measures observer overhead, not admission. Its cached
                # worker responses are still the per-round AC/thermal evidence.
                # Retain raw exit codes/stdout/stderr even when a probe failed.
                if job.ready():
                    try:
                        hard_probes.append({"job_id": job.job_id, "result": job.result()})
                    except Exception as exc:
                        hard_probe_errors.append({"job_id": job.job_id, "error": str(exc)})
                else:
                    hard_probe_errors.append({"job_id": job.job_id,
                                              "error": "hard probes did not complete during round"})
        # _BindTask owns process-group cancellation and nonblocking reap. Keep
        # this outside the duration-limited support and include its CPU cost.
        def cleaned(job):
            return job.reaped or (job.launch_done and getattr(job.process, "pid", None) is None)
        for job in tasks:
            if not job.reaped:
                job.cancel()
        cleanup_deadline = clock.monotonic() + 5
        while any(not cleaned(job) for job in tasks) and clock.monotonic() < cleanup_deadline:
            for job in tasks:
                if not job.reaped:
                    job.poll_cleanup()
            clock.sleep(.01)
        cost = cpu_total() - start_cpu
    jobs = [{"job_id": job.job_id, "pid": getattr(job.process, "pid", None),
             "reaped": job.reaped, "launch_done": job.launch_done} for job in tasks]
    residue = any(not cleaned(job) for job in tasks)
    if residue:
        error = (error or "") + "; worker cleanup incomplete"
        status = "error" if status != "partial" else status
    if observation and "boot_identity_unavailable" in observation and status == "complete":
        status, error = "error", observation["boot_identity_unavailable"]
    write_json(raw_dir / "workers.json", {"argv": argv_records, "jobs": jobs})
    return {"status": status, "error": error, "observation": observation,
            "observer_cpu_s": cost if not residue else None,
            "observer_cpu_s_reason": "worker cleanup incomplete" if residue else "SELF + reaped CHILDREN; no subtraction",
            "end_stamp": asdict(support_end), "workers": jobs, "argv": argv_records,
            "censuses": censuses, "census_errors": census_errors,
            "hard_probes": hard_probes, "hard_probe_errors": hard_probe_errors,
            "cleanup_incomplete": residue}


class PowerRecorder:
    def __init__(self, path, interval_ms, clock, deadline):
        self.path, self.clock, self.deadline = path, clock, deadline
        self.argv = power_argv(path, interval_ms)
        self.process = None
        self.stamps = {}
        self.timer = None
        self.kill_timer = None
        self.stop_lock = threading.Lock()
        self.metadata = {"argv": self.argv, "identity": None, "processes": None, "cleanup": None,
                         "term_sent": False, "kill_sent": False}

    def start(self):
        self.stamps["pre_spawn"] = self.clock.stamp()
        stderr = self.path.with_suffix(".stderr")
        with stderr.open("wb") as stream:
            self.process = subprocess.Popen(self.argv, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.DEVNULL, stderr=stream,
                                            start_new_session=True)
        from joulewise.quiet_predicate_campaign import journal_process
        journal_process("power", self.process.pid)
        self.timer = threading.Timer(max(0, self.deadline - self.clock.monotonic()), self.request_stop)
        self.timer.daemon = True
        self.timer.start()
        # Observe first complete frame promptly; this stamp is a causal bound,
        # never a sample timestamp. Delay ps identity lookup until after it.
        ready_until = min(self.deadline, self.clock.monotonic() + 15)
        while self.clock.monotonic() < ready_until:
            data = self.path.read_bytes() if self.path.exists() else b""
            if b"</plist>" in data:
                parse_frames(data)  # The stamp follows a real complete-frame parse.
                self.stamps["first_parse"] = self.clock.stamp()
                self.stamps["sampling_started"] = self.clock.stamp()
                self.metadata["identity"] = identity(self.process.pid)
                tree = command_text(quiet_admission.PS_ARGV)
                if isinstance(tree, str):
                    self.path.with_suffix(".processes.txt").write_text(tree + "\n")
                    entries = list(quiet_admission.parse_ps(tree).values())
                    owned = {self.process.pid}
                    while (extended := owned | {p["pid"] for p in entries if p["ppid"] in owned}) != owned:
                        owned = extended
                    self.metadata["processes"] = [p for p in entries if p["pid"] in owned]
                return
            if self.process.poll() is not None:
                raise RuntimeError(f"powermetrics exited during startup: {self.process.returncode}")
            self.clock.sleep(.02)
        raise RuntimeError("powermetrics first complete frame unavailable by startup deadline")

    def request_stop(self):
        with self.stop_lock:
            if "sampling_stopped" not in self.stamps:
                self.stamps["sampling_stopped"] = self.clock.stamp()
                if self.process:
                    # Do not poll/wait here: reaping the recorder while the
                    # final observer bracket is open would charge the entire
                    # recorder's CPU to that one round's RUSAGE_CHILDREN.
                    # Signal the supervised sudo process, which forwards TERM
                    # using its launch privilege; do not signal the root group.
                    try:
                        os.kill(self.process.pid, signal.SIGTERM)
                        self.metadata["term_sent"] = True
                    except ProcessLookupError:
                        pass
                    except PermissionError as exc:
                        self.metadata.setdefault("signal_errors", []).append(str(exc))
                    self.kill_timer = threading.Timer(5, self.force_stop)
                    self.kill_timer.daemon = True
                    self.kill_timer.start()

    def force_stop(self):
        with self.stop_lock:
            if self.process:
                try:
                    # Unreaped child PID cannot be reused. Signalling an
                    # already-exited zombie is harmless and is not reaping.
                    os.kill(self.process.pid, signal.SIGKILL)
                    self.metadata["kill_sent"] = True
                except ProcessLookupError:
                    pass
                except PermissionError as exc:
                    self.metadata.setdefault("signal_errors", []).append(str(exc))

    def finish(self):
        self.request_stop()
        if self.timer:
            self.timer.cancel()
        if self.process:
            remaining = max(0.0, 5 - (self.clock.monotonic() - self.stamps["sampling_stopped"].monotonic_before_s))
            try:
                code = self.process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                self.force_stop()
                try:
                    code = self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    code = None
            self.metadata["cleanup"] = reasons({"returncode": code, "term": self.metadata["term_sent"],
                "kill": code in (-signal.SIGKILL, 128 + signal.SIGKILL),
                "reap_after_observer_bracket": True}, "process not reaped after KILL")
        if self.kill_timer:
            self.kill_timer.cancel()
        data = self.path.read_bytes() if self.path.exists() else b""
        frames, dropped = parse_frames(data) if data else ([], None)
        self.stamps["post_parse"] = self.clock.stamp()
        aligned, anchor = align_frames(frames, self.stamps)
        self.metadata.update(stamps={k: asdict(v) for k, v in self.stamps.items()},
                             anchor=anchor, dropped_final_frame=dropped)
        return aligned, anchor


def census_condition(censuses, errors=()):
    results = [c.get("result", {}) for c in censuses or []]
    if any(c.get("exit_code") == 0 and c.get("stdout", "").strip() for c in results):
        return False, "agent detected by round census"
    if not results:
        return None, "no census completed during round"
    if errors or any(c.get("exit_code") != 1 or c.get("stdout") != "" or c.get("refusal")
                     for c in results):
        return None, "round census incomplete, failed or malformed"
    return True, "all completed round censuses report absence"


def new_row(session, args, index, start, end, result):
    row = dict.fromkeys(ROUND_KEYS)
    row.update(schema=SCHEMA, session=session, state=args.state, repeat=args.repeat,
               round=index, status=result["status"], error=result["error"],
               epoch_s=start.epoch_s, load_setting=args.load_cores,
               round_wall_start_s=start.epoch_s, round_wall_end_s=end.epoch_s,
               round_mono_start_s=start.monotonic_before_s, round_mono_end_s=end.monotonic_after_s,
               observation=result["observation"], observer_cpu_s=result["observer_cpu_s"],
               power={**dict.fromkeys(RAILS), "coverage_s": 0.0}, clusters=None, cpus=None,
               alignment=dict.fromkeys(("anchor_lo", "anchor_hi", "ps_start", "ps_end", "top_start", "top_end", "error_bound_j")),
               raw={"paths": [], "sha256": {}})
    censuses = list(result.get("censuses") or [])
    sample_census = (result["observation"] or {}).get("census")
    if sample_census is not None:
        censuses.append({"source": "sampler", "result": sample_census})
    errors = result.get("census_errors") or []
    clean, reason = census_condition(censuses, errors)
    row.update(censuses=censuses or None, census_errors=errors,
               census_clean=clean, census_clean_reason=reason)
    row["hard_probes"] = result.get("hard_probes") or None
    row["hard_probe_errors"] = result.get("hard_probe_errors") or []
    if row["hard_probes"] is None:
        row["hard_probes_reason"] = "no hard-probe worker completed during round"
    if not censuses:
        row["censuses_reason"] = "no census completed during round"
    row["error_reason"] = "no round error" if row["error"] is None else "round failed or incomplete"
    if result.get("observer_cpu_s_reason"):
        row["observer_cpu_s_reason"] = result["observer_cpu_s_reason"]
    if args.load_cores is None:
        row["load_setting_reason"] = "injected increment not supplied; use --load-cores (never inferred from state name)"
    row["alignment"].update(round_start_stamp=asdict(start), round_end_stamp=asdict(end),
                            support="whole observer round, clipped to collection deadline",
                            top_support="command bracket; native second-sample support is not separately exposed")
    return row


def collect(args, *, clock=None, round_runner=production_round, recorder_factory=PowerRecorder,
            metadata_reader=None):
    clock = clock or Clock()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError("collection output directory must be empty; evidence is never overwritten")
    raw = out / "raw"
    raw.mkdir()
    session_id = str(uuid.uuid4())
    if metadata_reader is None:
        def metadata_reader():
            boot = command_text(quiet_admission.BOOT_ARGV)
            build = command_text(["/usr/bin/sw_vers", "-buildVersion"])
            version = command_text(["/usr/bin/sw_vers"])
            executable = Path(pm.POWER_METRICS)
            try:
                power_identity = {"path": str(executable), "sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
            except OSError as exc:
                power_identity = {"path": str(executable), "sha256": None, "sha256_reason": str(exc)}
            return reasons({"sw_vers": version if isinstance(version, str) else None,
                            "powermetrics_identity": power_identity,
                            "boot_id": boot if isinstance(boot, str) else None,
                            "os_build": build if isinstance(build, str) else None,
                            "collector": identity(os.getpid()), "argv": sys.argv,
                            "metadata_errors": [v[1] for v in (boot, build) if isinstance(v, tuple)]})
    metadata = metadata_reader()
    provenance, provenance_reason = network_time_provenance()
    session = {"schema": SCHEMA, "session": session_id, **metadata,
               "state": args.state, "repeat": args.repeat, "load_setting": args.load_cores,
               "duration_s": args.duration_s, "sample_interval_s": args.sample_interval_s,
               "power_interval_ms": args.power_interval_ms, "power_enabled": args.power,
               "powermetrics_needs_root": True, "sudo_policy_probed": False,
               "evidence_status": "PROVISIONAL", "network_time_provenance": provenance,
               "alignment_model": ALIGNMENT_MODEL,
               "network_time_provenance_reason": provenance_reason,
               "observer_definition": "SELF + reaped CHILDREN over production smoke incl. raw/stamp hooks; recorder CPU excluded",
               "round_workers": [], "power": None, "error": None, "error_rounds": 0}
    envelope_cpu_start = cpu_total()
    start = clock.stamp()
    scheduled = getattr(args, "envelope_start_mono_s", None)
    deadline = (start.monotonic_before_s if scheduled is None else scheduled) + args.duration_s
    session["scheduled_mono_s"] = scheduled
    session["start_drift_s"] = start.monotonic_before_s - scheduled if scheduled is not None else None
    session["start_stamp"] = asdict(start)
    session["deadline_mono_s"] = deadline
    if provenance is None:
        # Ruling 10 Q1 rule 3: refuse the envelope here, BEFORE powermetrics is
        # spawned, rather than capture under an unknown clock regime and record
        # the provenance as null.  main() maps this to exit 3.
        session["error"] = "network time provenance not established: " + provenance_reason
        session["error_class"] = NETWORK_TIME_REFUSAL
        session["error_rounds"] = 0
        write_json(out / "session.json", session)
        (out / "rounds.jsonl").write_text("")
        return session, []
    write_json(out / "session.json", session)
    recorder = None
    rows, frames, anchor = [], [], {"status": "unresolved", "detail": "power disabled"}
    try:
        if args.power:
            path = raw / f"powermetrics-{args.state}-{args.repeat}.plist"
            recorder = recorder_factory(path, args.power_interval_ms, clock, deadline)
            recorder.start()
        while clock.monotonic() < deadline:
            index = len(rows) + 1
            round_dir = raw / f"round-{index:04d}"
            round_dir.mkdir()
            before = clock.stamp()
            try:
                result = round_runner(args.sample_interval_s, deadline, round_dir, clock)
            except (Exception, KeyboardInterrupt) as exc:
                session["error"] = f"{type(exc).__name__}: {exc}"
                result = {"status": "partial" if isinstance(exc, KeyboardInterrupt) else "error",
                          "error": session["error"], "observation": None, "observer_cpu_s": None,
                          "end_stamp": asdict(clock.stamp())}
            after = ClockStamp(**result["end_stamp"])
            row = new_row(session_id, args, index, before, after, result)
            if result.get("cleanup_incomplete"):
                session["error"] = "round worker cleanup incomplete; collection stopped"
            if after.monotonic_after_s > deadline:
                # Support ends at the duration limit, not after child cleanup.
                offset = after.monotonic_after_s - deadline
                row["round_wall_end_s"] = after.epoch_s - offset
                row["round_mono_end_s"] = deadline
                row["alignment"]["end_clipping_s"] = offset
                row["status"] = "partial"
                row["error"] = row["error"] or "round exceeded collection duration"
            row["boot_id"] = metadata.get("boot_id")
            row["os_build"], build_error = os_build_identity(session.get("os_build"))
            row["os_build_valid"] = build_error is None
            if build_error is not None:
                row["os_build_reason"] = build_error
            session["round_workers"].append({"round": index, "workers": result.get("workers", []),
                                             "argv": result.get("argv", []),
                                             "identities": [json.loads(p.read_text()) for p in sorted(round_dir.glob("*-identity.json"))]})
            sampler = round_dir / "sampler.json"
            if sampler.exists():
                evidence = json.loads(sampler.read_text())
                row["alignment"].update(evidence["marks"])
                row["alignment"]["sampler_wall_stamps"] = evidence["wall_reads"]
                ps_start, ps_end = (evidence["marks"].get(k) for k in ("ps_start", "ps_end"))
                if ps_start is not None and ps_end is not None:
                    row["alignment"]["ps_span_s"] = ps_end - ps_start
                    row["alignment"]["round_minus_ps_s"] = row["round_mono_end_s"] - row["round_mono_start_s"] - (ps_end - ps_start)
                    top_start, top_end = (evidence["marks"].get(k) for k in ("top_start", "top_end"))
                    top_span = top_end - top_start if top_start is not None and top_end is not None else None
                    row["alignment"].update(top_command_span_s=top_span,
                        ps_top_span_mismatch=(abs(ps_end - ps_start - top_span) > 1e-6) if top_span is not None else None,
                        round_ps_span_mismatch=abs(row["alignment"]["round_minus_ps_s"]) > 1e-6)
            rows.append(row)
            # Durable one-row-per-attempt journal before the offline reduction.
            with (out / "rounds.jsonl").open("a") as stream:
                stream.write(json.dumps(reasons(row, "power reduction pending or source unavailable"), allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            if row["status"] == "partial" or session["error"]:
                break
            if clock.monotonic() <= before.monotonic_before_s:
                raise RuntimeError("round made no monotonic progress")
    except (Exception, KeyboardInterrupt) as exc:
        session["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if recorder is not None:
            try:
                frames, anchor = recorder.finish()
            except Exception as exc:
                session["error"] = (session["error"] or "") + f"; power finalization: {exc}"
                anchor = {"status": "unresolved", "detail": str(exc)}
            session["power"] = recorder.metadata
            cleanup = recorder.metadata.get("cleanup") or {}
            if cleanup.get("kill") or (cleanup and cleanup.get("returncode") is None):
                session["error"] = (session["error"] or "") + "; power cleanup escalated; root descendant termination needs bench verification"
            elif cleanup and cleanup["returncode"] not in (0, -signal.SIGTERM, 128 + signal.SIGTERM):
                session["error"] = (session["error"] or "") + f"; powermetrics exit {cleanup['returncode']}"
        session["end_stamp"] = asdict(clock.stamp())
        session["whole_envelope_observer_cpu_s"] = cpu_total() - envelope_cpu_start
        session["whole_envelope_observer_definition"] = "SELF + all reaped CHILDREN, including power recorder; never subtracted"
    session["error_rounds"] = sum(row["status"] == "error" for row in rows)
    if session["error_rounds"] and not any(row["status"] == "complete" for row in rows):
        session["error"] = session["error"] or "no round completed successfully"
    if getattr(args, "interior_s", None) is not None:
        interior_anchor = dict(anchor)
        if anchor.get("status") == "bounded":
            interior_anchor["effective_clock_anchor_bound_s"] += start.monotonic_after_s - start.monotonic_before_s
        # Use the wall/monotonic mapping in the actual start bracket to map
        # the frozen scheduled start, preserving the bracket uncertainty.
        interior_epoch = start.epoch_s - (session["start_drift_s"] or 0) + args.interior_offset_s
        session["interior"] = reduce_interior(frames, interior_anchor, interior_epoch, args.interior_s)
    for row in rows:
        align = row["alignment"]
        why = str(anchor.get("detail", anchor.get("reason", "clock anchor unresolved")))
        if anchor["status"] == "bounded" and row["round_wall_end_s"] > row["round_wall_start_s"]:
            epsilon = anchor["effective_clock_anchor_bound_s"]
            # Add this round's own wall-read brackets to the production bound.
            epsilon += max(s["monotonic_after_s"] - s["monotonic_before_s"]
                           for s in (align["round_start_stamp"], align["round_end_stamp"]))
            values = integrate_seconds(frames, row["round_wall_start_s"],
                                       row["round_wall_end_s"], epsilon)
            row.update({k: values[k] for k in ("power", "clusters", "cpus")})
            align.update(anchor_lo=anchor["admissible_lower_epoch_s"], anchor_hi=anchor["admissible_upper_epoch_s"],
                         error_bound_j=values["error_bound_j"], rail_error_bound_j=values["rail_error_bound_j"],
                         frame_span_mismatch=values["span_mismatch"], error_bound_s=epsilon,
                         error_bound_j_reason="incomplete rail coverage; unobserved energy is unbounded")
        else:
            align.update(frame_span_mismatch=True, error_bound_j_reason=why)
            row["power"] = reasons(row["power"], why)
        align.update(method=anchor.get("method"), anchor_status=anchor["status"],
                     model=ALIGNMENT_MODEL,
                     bound_method="sum of per-frame overlap perturbation bounds on the interval-average power signal; gaps unbounded")
        if align["error_bound_j"] is not None:
            align.pop("error_bound_j_reason", None)
        paths = sorted(p for p in raw.rglob("*") if p.is_file() and (
            p.parent == raw or p.parent.name == f"round-{row['round']:04d}"))
        row["raw"] = {"paths": [str(p.relative_to(out)) for p in paths],
                      "sha256": {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    # Final reduction replaces only this session's provisional derived journal.
    with (out / "rounds.jsonl").open("w") as stream:
        for row in rows:
            stream.write(json.dumps(reasons(row), sort_keys=True, allow_nan=False) + "\n")
    write_json(out / "session.json", session)
    return session, rows


def burn_profile(profile, seed):
    """Separate OS processes avoid the GIL; memory is allocated before timing."""
    state = seed & 0xFFFFFFFF
    memory = bytearray(16 * 1024 * 1024) if profile == "memory" else None
    if memory is not None:
        # Commit pages before the measured duty loop, without per-period allocation.
        for i in range(0, len(memory), 4096):
            memory[i] = (i + seed) & 255
    def burn(count):
        nonlocal state
        for _ in range(count):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            if memory is not None:
                index = state & (len(memory) - 1)
                memory[index] = (memory[index] + 1) & 255
        return state
    return burn


def duty_periods(share, duration_s, period_s, burn, clock, *, start=None):
    """Thread-CPU budgets, absolute wall deadlines, no catch-up burst.

    During the first five seconds calibrate the loop duty for measured period
    overhead and the batch size toward 100 us CPU. Then freeze both. An
    overshoot is charged against the next period; unsatisfied CPU is never
    carried forward under contention. Each batch and clock check is measured:
    reported overshoot bound = largest observed batch + accounting tail.
    This is a measured CPU bound, not a real-time scheduling guarantee.
    """
    start = clock.monotonic() if start is None else start
    end = start + duration_s
    duty, batch, debt = share, 1, 0.0
    rows = []
    index = 0
    previous_cpu_end = clock.cpu()
    while (now := clock.monotonic()) < end:
        boundary = min(end, start + (index + 1) * period_s)
        if boundary <= now:
            index = int((now - start) / period_s)
            boundary = min(end, start + (index + 1) * period_s)
        nominal_start = start + index * period_s
        elapsed = boundary - nominal_start
        calibrating = nominal_start - start < 5.0 - 1e-9
        cpu_start = previous_cpu_end
        carry_in = max(0.0, clock.cpu() - cpu_start)
        budget = share * elapsed
        work_budget = max(0.0, min(budget, duty * elapsed) - debt)
        quantum_max = 0.0
        current = clock.cpu()
        while current - cpu_start < work_budget and clock.monotonic() < boundary:
            previous = current
            burn(batch)
            current = clock.cpu()
            quantum = current - previous
            quantum_max = max(quantum_max, quantum)
            if calibrating and quantum > 0:
                batch = max(1, min(4096, int(batch * min(2, max(.5, .0001 / quantum)))))
        burn_used = current - cpu_start
        clock.sleep_until(boundary)
        cpu_end = clock.cpu()
        previous_cpu_end = cpu_end
        used = cpu_end - cpu_start
        debt = max(0.0, burn_used - work_budget)
        tail = max(0.0, used - burn_used)
        overrun = max(0.0, used - budget)
        rows.append({"period": index, "start_mono_s": nominal_start, "end_mono_s": boundary,
                     "elapsed_s": elapsed, "cpu_used_s": used, "budget_cpu_s": budget,
                     "work_budget_cpu_s": work_budget, "overrun_cpu_s": overrun,
                     "shortfall_cpu_s": max(0.0, budget - used),
                     "wake_late_s": max(0.0, clock.monotonic() - boundary),
                     "max_quantum_cpu_s": quantum_max, "overshoot_bound_cpu_s": quantum_max + tail + carry_in,
                     "accounting_cpu_s": carry_in,
                     "duty": duty, "batch": batch, "calibrating": calibrating})
        if calibrating:
            duty = max(0.0, min(share, duty + .25 * (budget - used) / elapsed))
        index += 1
    return rows


def stationarity(periods, target):
    """Duration-weighted, post-calibration first/last thirds; no admission test."""
    selected = [p for p in periods if not p["calibrating"]]
    if not selected:
        return reasons({"mean_busy_cores": None, "first_third_busy_cores": None,
                        "last_third_busy_cores": None, "first_last_delta_cores": None,
                        "mean_minus_setting_cores": None}, "no post-calibration periods")
    start = min(p["start_mono_s"] for p in selected)
    end = max(p["end_mono_s"] for p in selected)
    def busy(lo, hi):
        return math.fsum(p["cpu_used_s"] / p["elapsed_s"] * overlap(
            lo, hi, p["start_mono_s"], p["end_mono_s"]) for p in selected) / (hi - lo)
    mean, first, last = busy(start, end), busy(start, start + (end - start) / 3), busy(end - (end - start) / 3, end)
    return {"mean_busy_cores": mean, "first_third_busy_cores": first,
            "last_third_busy_cores": last, "first_last_delta_cores": last - first,
            "mean_minus_setting_cores": mean - target, "coverage_s": end - start}


def set_qos(qos):
    if sys.platform != "darwin":
        raise RuntimeError("native QoS load workers require macOS")
    lib = ctypes.CDLL(None)
    function = lib.pthread_set_qos_class_self_np
    function.argtypes = [ctypes.c_uint, ctypes.c_int]
    function.restype = ctypes.c_int
    code = 0x09 if qos == "background" else 0x19
    result = function(code, 0)
    if result:
        raise OSError(result, "pthread_set_qos_class_self_np")


def load_worker(connection, config):
    try:
        set_qos(config["qos"])
        burn = burn_profile(config["profile"], config["seed"])
        worker_identity = identity(os.getpid())
        connection.send({"ready": True, "identity": worker_identity})
        start = connection.recv()
        clock = Clock()
        clock.sleep_until(start)
        periods = duty_periods(config["share"], config["duration_s"], config["period_s"],
                               burn, clock, start=start)
        connection.send({"identity": worker_identity, "periods": periods,
                         "stationarity": stationarity(periods, config["share"])})
    except BaseException as exc:
        connection.send({"error": f"{type(exc).__name__}: {exc}"})
    finally:
        connection.close()


def load(args, *, join_grace_s: float = 5.0):
    log = Path(args.log)
    if log.exists():
        raise ValueError("load log exists; refusing to overwrite evidence")
    context = multiprocessing.get_context("spawn")
    count = max(1, math.ceil(args.cores))
    if count > (os.cpu_count() or 1):
        raise ValueError("requested CPU budget exceeds this host's logical CPU count")
    children, connections, results = [], [], []
    report = {"schema": SCHEMA, "command": "load", "cores": args.cores,
              "duration_s": args.duration_s, "period_ms": args.period_ms,
              "qos": args.qos, "profile": args.profile, "seed": args.seed,
              "implementation": "OS processes with native thread CPU clocks; independent GILs",
              "calibration_s": 5, "workers": [], "error": None}
    boot = command_text(quiet_admission.BOOT_ARGV)
    report["boot_id"] = boot if isinstance(boot, str) else None
    try:
        for index in range(count):
            parent, child = context.Pipe()
            config = {"share": args.cores / count, "duration_s": args.duration_s,
                      "period_s": args.period_ms / 1000, "qos": args.qos,
                      "profile": args.profile, "seed": args.seed + index}
            process = context.Process(target=load_worker, args=(child, config))
            try:
                process.start()
            except BaseException:
                parent.close()
                child.close()
                raise
            child.close()
            children.append(process)
            connections.append(parent)
        for connection in connections:
            if not connection.poll(15):
                raise RuntimeError("load worker startup timed out")
            ready = connection.recv()
            if not ready.get("ready"):
                raise RuntimeError(ready.get("error", "load worker failed startup"))
            report["workers"].append(ready)
        start = time.monotonic() + .2
        report["start_stamp"] = asdict(Clock().stamp())
        for connection in connections:
            connection.send(start)
        # All results share an absolute deadline; slow/dead workers cannot
        # multiply a duration-sized wait by the number of processes.
        deadline = start + args.duration_s + 10
        for connection in connections:
            if not connection.poll(max(0, deadline - time.monotonic())):
                raise RuntimeError("load worker result timed out")
            result = connection.recv()
            if "error" in result:
                raise RuntimeError(result["error"])
            results.append(result)
        report["workers"] = results
        report["stationarity"] = stationarity([p for r in results for p in r["periods"]], args.cores)
    except (Exception, KeyboardInterrupt) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for process in children:
            process.join(timeout=join_grace_s)
            if process.is_alive():
                process.terminate()
                process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
        for connection in connections:
            connection.close()
        report["cleanup"] = [{"pid": p.pid, "exitcode": p.exitcode, "alive": p.is_alive()} for p in children]
        escalated = [row for row in report["cleanup"] if row["alive"] or row["exitcode"] != 0]
        if escalated and report["error"] is None:
            report["error"] = "worker cleanup escalated: " + "; ".join(
                f"pid {row['pid']} exitcode {row['exitcode']}" for row in escalated)
        write_json(log, report)
    return report


def quantiles(values):
    ordered = sorted(v for v in values if number(v) is not None)
    def at(q):
        if not ordered:
            return None
        position = q * (len(ordered) - 1)
        lo = int(position)
        hi = min(lo + 1, len(ordered) - 1)
        return ordered[lo] + (position - lo) * (ordered[hi] - ordered[lo])
    return reasons({key: at(q) for key, q in zip(("min", "p10", "p50", "p90", "max"), (0, .1, .5, .9, 1))},
                   "no complete round metrics")


def aggregate(rows):
    complete = [r for r in rows if r["status"] == "complete"]
    result = {"rounds": len(rows), "complete_rounds": len(complete),
              "partial_rounds": sum(r["status"] == "partial" for r in rows),
              "error_rounds": sum(r["status"] == "error" for r in rows),
              "os_build_unavailable_rounds": sum(os_build_identity(r.get("os_build"))[0] is None for r in rows),
              "quantiles": {}, "power": {}, "coverage_s": {}, "alignment_bound_w": {}}
    for key in ("busy_cores", "host_busy_cores", "observer_cpu_s"):
        result["quantiles"][key] = quantiles(
            [r.get("observer_cpu_s") if key == "observer_cpu_s" else
             (r.get("observation") or {}).get("metrics", {}).get(key) for r in complete])
    for rail in RAILS:
        values = [(r["power"][rail], r["power"].get("rail_coverage_s", {}).get(rail, r["power"]["coverage_s"]),
                   r["alignment"].get("rail_error_bound_j", {}).get(rail)) for r in complete
                  if number(r["power"].get(rail)) is not None]
        den = math.fsum(c for _, c, _ in values)
        result["power"][rail] = math.fsum(p * c for p, c, _ in values) / den if den else None
        result["coverage_s"][rail] = den
        result["alignment_bound_w"][rail] = (math.fsum(b for _, _, b in values) / den
            if den and all(number(b) is not None for _, _, b in values) else None)
    compared = [((r.get("observation") or {}).get("metrics", {}).get("busy_cores"), r["load_setting"])
                for r in complete if r.get("observation") and number(r.get("load_setting")) is not None]
    if any(number(busy) is None for busy, _ in compared):
        raise ValueError("load comparison requires finite busy_cores")
    result["load_compared_rounds"] = len(compared)
    result["load_disagreement_rounds"] = sum(abs(busy - setting) > max(.02, .1 * setting)
                                              for busy, setting in compared)
    result["load_comparison"] = "total busy_cores versus injected increment, without baseline subtraction"
    return reasons(result, "no covered evidence or finite alignment bound")


def summarize(directory, reference_state=None, load_logs=()):
    directory = Path(directory)
    paths = sorted(directory.rglob("rounds.jsonl"))
    rows = []
    reports = [(Path(path), json.loads(Path(path).read_text())) for path in load_logs]
    for path in paths:
        session_path = path.parent / "session.json"
        session = json.loads(session_path.read_text()) if session_path.exists() else None
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            # Older rows may lack the build; preserve that unknown rather than
            # retroactively filling it from the session. A supplied identity
            # must agree with its own session, never with a neighbouring file.
            build, build_error = os_build_identity(row.get("os_build"))
            if "os_build" in row and session is not None:
                expected, _ = os_build_identity(session.get("os_build"))
                if row.get("session") != session.get("session") or build != expected:
                    raise ValueError(f"row/session OS build identity mismatch: {path}")
            if "os_build" in row:
                row["os_build"] = build
                row["os_build_valid"] = build_error is None
                if build_error is not None:
                    row["os_build_reason"] = build_error
            joins = []
            if reports:
                raw = path.parent / "raw" / f"round-{row['round']:04d}"
                try:
                    before = quiet_admission.parse_ps((raw / "ps_before.txt").read_text())
                    after = quiet_admission.parse_ps((raw / "ps_after.txt").read_text())
                except (OSError, ValueError):
                    before, after = {}, {}
                joins = [{"load_log": str(source), "load_log_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                          **join_load_log(row, report, before, after)} for source, report in reports]
            row["load_joins"] = joins
            rows.append(row)
    if any(r.get("schema") != SCHEMA for r in rows):
        raise ValueError("unsupported evidence schema")
    # Older v1 rows lack whole-round coverage: never infer clean from only
    # their sampler census. They remain in the explicitly unknown group.
    def condition(row):
        return row.get("census_clean") if type(row.get("census_clean")) is bool else None
    has_os_build = any("os_build" in row for row in rows)
    def comparison_key(row):
        return (condition(row), row.get("boot_id"), row.get("os_build"))
    def comparison_fields(key):
        clean, boot_id, os_build = key
        return {"census_clean": clean, "boot_id": boot_id,
                **({"os_build": os_build} if has_os_build else {})}
    reference_rows = [r for r in rows if r["state"] == reference_state]
    if rows and reference_state is not None and not reference_rows:
        raise ValueError("reference state is absent")
    reference_conditions = {comparison_key(r) for r in reference_rows}
    reference = ({**comparison_fields(next(iter(reference_conditions))), **aggregate(reference_rows)}
                 if len(reference_conditions) == 1 else None)
    references = {key: aggregate([r for r in reference_rows if comparison_key(r) == key])
                  for key in reference_conditions}
    groups = []
    keys = {(r["state"], str(r["repeat"]), comparison_key(r)) for r in rows}
    for state, repeat, key in sorted(keys, key=lambda k: (k[0], k[1], str(k[2]))):
        subset = [r for r in rows if (r["state"], str(r["repeat"]), comparison_key(r)) == (state, repeat, key)]
        group_reference = references.get(key)
        clean = key[0]
        entry = {"state": state, "repeat": repeat, "sessions": sorted({r["session"] for r in subset}),
                 **comparison_fields(key), "census_clean_reason": "whole-round census condition unavailable" if clean is None else "derived from round censuses",
                 **aggregate(subset), "delta_j_480": {}, "delta_alignment_bound_j_480": {}}
        for rail in RAILS:
            value = entry["power"][rail]
            ref = group_reference["power"][rail] if group_reference else None
            bound = entry["alignment_bound_w"][rail]
            ref_bound = group_reference["alignment_bound_w"][rail] if group_reference else None
            entry["delta_j_480"][rail] = 480 * (value - ref) if value is not None and ref is not None else None
            entry["delta_alignment_bound_j_480"][rail] = (480 * (bound + ref_bound)
                if bound is not None and ref_bound is not None else None)
        groups.append(reasons(entry, "reference or finite alignment evidence unavailable"))
    provenance = []
    for path in sorted(directory.rglob("session.json")):
        session = json.loads(path.read_text())
        provenance.append({"source": str(path.relative_to(directory)),
                           **{key: session[key] for key in (
                               "evidence_status", "alignment_model", "network_time_provenance",
                               "network_time_provenance_reason") if key in session}})
    def common_provenance(key, default):
        values = [p.get(key, default) for p in provenance]
        return (values[0] if all(v == values[0] for v in values) else None) if values else default
    summary = reasons({"schema": SCHEMA, "reference_state": reference_state, "reference": reference,
                       "reference_reason": "reference absent or spans census conditions, boots or OS builds; see references_by_census",
                       "references_by_census": [{**comparison_fields(key), **references[key]}
                                                for key in sorted(references, key=str)],
                       "status": "complete" if rows else "no_rounds",
                       "reason": "descriptive summary" if rows else "no rounds.jsonl rows found",
                       "evidence_status": "PROVISIONAL",
                       "alignment_model": common_provenance("alignment_model", ALIGNMENT_MODEL),
                       "alignment_model_reason": "models differ across sessions; see session_provenance",
                       "network_time_provenance": common_provenance("network_time_provenance", None),
                       "network_time_provenance_reason": common_provenance("network_time_provenance_reason",
                           "unavailable or differs across sessions; see session_provenance"),
                       "session_provenance": provenance,
                       "load_joins": [{"session": r["session"], "round": r["round"], "joins": r["load_joins"]}
                                      for r in rows if r["load_joins"]],
                       "groups": groups, "sources": [str(p.relative_to(directory)) for p in paths],
                       "aggregation": "complete rounds only; duration-weighted rail coverage; reference pooled across repeats within the same census_clean condition, boot_id and OS build only; bounds add without independence assumptions"})
    for field in ("reference", "alignment_model"):
        if summary[field] is not None:
            summary.pop(field + "_reason", None)
    write_json(directory / "summary.json", summary)
    def fmt(value):
        return "null" if value is None else f"{value:.6g}"
    def cell(value):
        # Missing identity values render as the JSON spelling, never Python's None.
        return "null" if value is None else str(value).replace("|", "\\|").replace("\n", " ")
    identity_header = "| State | Repeat / census_clean | boot_id |" + (" os_build |" if has_os_build else "")
    identity_separator = "|---|---|---|" + ("---|" if has_os_build else "")
    def identity_cells(entry):
        return (f"| {cell(entry['state'])} | {cell(entry['repeat'])} / {entry['census_clean']} | {cell(entry['boot_id'])} |" +
                (f" {cell(entry['os_build'])} |" if has_os_build else ""))
    lines = ["# Quiet predicate evidence (descriptive)", "",
             "Complete rounds only. Reference: " + cell(reference_state or "not supplied") + ".",
             "Alignment bounds are systematic sums; no statistical uncertainty is inferred.", "",
             identity_header + " Metric | min | p10 | p50 | p90 | max |", identity_separator + "---|---:|---:|---:|---:|---:|"]
    for entry in groups:
        for metric, q in entry["quantiles"].items():
            lines.append(identity_cells(entry) + f" {metric} | " +
                         " | ".join(fmt(q[k]) for k in ("min", "p10", "p50", "p90", "max")) + " |")
    lines += ["", identity_header + " Rail | Mean W | Coverage s | ΔJ / 480 s | Alignment bound J |", identity_separator + "---|---:|---:|---:|---:|"]
    for entry in groups:
        for rail in RAILS:
            lines.append(identity_cells(entry) + f" {rail} | " + " | ".join(fmt(v) for v in (
                entry["power"][rail], entry["coverage_s"][rail], entry["delta_j_480"][rail], entry["delta_alignment_bound_j_480"][rail])) + " |")
    lines += ["", identity_header + " Complete | Partial | Error | Load disagreements / compared |", identity_separator + "---:|---:|---:|---:|"]
    for e in groups:
        lines.append(identity_cells(e) + f" {e['complete_rounds']} | {e['partial_rounds']} | {e['error_rounds']} | {e['load_disagreement_rounds']} / {e['load_compared_rounds']} |")
    lines += ["", "Load comparison uses total busy cores versus injected increment; no observer or idle subtraction.",
              "Partial rounds and unavailable bounds remain in the JSON evidence. PROVISIONAL; no cutoff or verdict.", ""]
    (directory / "summary.md").write_text("\n".join(lines))
    return summary


def positive(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return result


def nonnegative(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("must be finite and nonnegative")
    return result


def label(value):
    if not value or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for c in value) or value in (".", ".."):
        raise argparse.ArgumentTypeError("use a simple state/repeat label, without path separators")
    return value


def parser():
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command", required=True)
    collection = commands.add_parser("collect", help="lead-only live evidence; no admission decision")
    collection.add_argument("--state", required=True, type=label)
    collection.add_argument("--repeat", required=True, type=label)
    collection.add_argument("--duration-s", required=True, type=positive)
    collection.add_argument("--sample-interval-s", type=positive, default=30)
    collection.add_argument("--power-interval-ms", type=int, default=100)
    collection.add_argument("--out", required=True)
    collection.add_argument("--load-cores", type=nonnegative, help="known injected increment; omitted means unknown")
    collection.add_argument("--interior-offset-s", type=nonnegative, default=60)
    collection.add_argument("--interior-s", type=positive)
    collection.add_argument("--envelope-start-mono-s", type=nonnegative, help=argparse.SUPPRESS)
    collection.add_argument("--power", action=argparse.BooleanOptionalAction, default=True)
    workload = commands.add_parser("load", help="native OS processes, preallocated profiles, thread CPU clocks")
    workload.add_argument("--cores", required=True, type=nonnegative)
    workload.add_argument("--duration-s", required=True, type=positive)
    workload.add_argument("--period-ms", type=positive, default=100)
    workload.add_argument("--qos", choices=("background", "user-initiated"), required=True)
    workload.add_argument("--profile", choices=("scalar", "memory"), required=True)
    workload.add_argument("--seed", type=int, required=True)
    workload.add_argument("--log", required=True)
    summary = commands.add_parser("summarize", help="offline descriptive JSON and Markdown")
    summary.add_argument("--in", dest="input", required=True)
    summary.add_argument("--reference-state")
    summary.add_argument("--load-log", action="append", default=[])
    worker = commands.add_parser("_sample", help=argparse.SUPPRESS)
    worker.add_argument("--sample-interval-s", type=float, required=True)
    worker.add_argument("--observer-pid", type=int, required=True)
    worker.add_argument("--job-id", required=True)
    worker.add_argument("--result-fd", type=int, required=True)
    worker.add_argument("--raw-dir", required=True)
    return root


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "_exec":
        from joulewise.quiet_predicate_campaign import journal_process
        journal_process("sampler_or_probe", os.getpgrp())
        write_json(Path(argv[1]), {**identity(os.getpid()), "argv": argv[2:],
                                  "stamp": asdict(Clock().stamp())})
        os.execv(argv[2], argv[2:])
    args = parser().parse_args(argv)
    try:
        if args.command == "_sample":
            return sample_worker(args)
        if args.command == "collect":
            quiet_admission.top_argv(args.sample_interval_s)
            if args.power_interval_ms <= 0:
                raise ValueError("power interval must be positive")
            if args.interior_s is not None and args.interior_offset_s + args.interior_s > args.duration_s:
                raise ValueError("interior must fit inside collection duration")
            def terminate(_number, _frame):
                raise KeyboardInterrupt("collector termination requested")
            previous = signal.signal(signal.SIGTERM, terminate)
            try:
                session, _ = collect(args)
            finally:
                signal.signal(signal.SIGTERM, previous)
            if session.get("error_class") == NETWORK_TIME_REFUSAL:
                print(f"error: {session['error']}", file=sys.stderr)
                return NETWORK_TIME_REFUSAL_EXIT
            return int(session["error"] is not None)
        if args.command == "load":
            return int(load(args)["error"] is not None)
        summarize(args.input, args.reference_state, args.load_log)
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
