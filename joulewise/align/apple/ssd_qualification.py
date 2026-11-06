"""Hardware qualification of an always-attached external log volume.

DRAFT amendment tooling (``docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md`` §6).
It decides nothing on its own: the council and Ed adopt or reject the
amendment from the verdict this module prints.

Four parts, all standard library:

* ``plan``: the segment schedule. Physical blocks alternate presence
  (default attached, detached, attached: an A-B-A like the High Power test).
  Inside every block, idle segments and then fixed-load decode segments come
  in ABBA-ordered pairs of a quiet segment and a write segment. In attached
  blocks the write segment replays the window write pattern onto the external
  volume; in detached blocks it replays it onto the internal disk (the status
  quo control).
* ``PatternWriter`` and ``teardown_burst``: the write pattern. The in-episode
  streams are the ones a measured segment carries today (``WINDOW_PATTERN``),
  plus, as a worst case, the 10 Hz powermetrics-sized stream that stays on
  the internal ``TMPDIR`` in production. The teardown burst stands for the
  post-member raw copy and backup rsync.
* ``extract``: mean GPU, CPU and ANE rail power over the steady core of each
  segment from one continuous powermetrics plist capture (records parsed by
  the existing ``joulewise.adapters.powermetrics`` parser, unchanged).
* ``evaluate``: the presence offset and the write effects with 90 % t
  intervals, the criteria Q1-Q3 against the design's s_r, the operational
  criterion Q5, and the strongest option (B or C) they allow; A and A-lite
  wait for a write-variability criterion.

Units: power in W, energy in J, time in s.
"""
from __future__ import annotations

import math
import os
import statistics
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.analysis_engine.distributions import student_t_quantile

SCHEMA = "joulewise.align_ssd_qualification.v1"
PASS, FAIL, INCONCLUSIVE = "PASS", "FAIL", "INCONCLUSIVE"

# Pilot-v3 sizing evidence (configs/campaigns/align_pilot_v3/registration/
# sizing_evidence.json, 24 members): mean bundle 507 MB, of which the three
# raw powermetrics plists are 89 %; the idle plist is 157 MB for 300 s of
# 10 Hz samples, so one sample is about 52 kB. The SMC thermal sidecar writes
# one line a second with an fsync every 5 s (joulewise/align/apple/thermal.py).
# The hazard monitor journals B0AC once a second (joulewise/hazards/battery.py).
WINDOW_PATTERN: dict[str, dict[str, Any]] = {
    "thermal_sidecar": {"period_s": 1.0, "bytes": 420, "fsync_every_s": 5.0},
    "monitor_journal": {"period_s": 1.0, "bytes": 300, "fsync_every_s": 1.0},
}
WORST_CASE_EXTRA: dict[str, dict[str, Any]] = {
    "powermetrics_like": {"period_s": 0.1, "bytes": 52_000, "fsync_every_s": None},
}
# One D member at the 1,800 s cap: 186.75 MB + 512.4 kB/s x 1,800 s = 1.11 GB
# (disk_member_law); the burst writes that once (raw bundle) and once more
# (backup) under Option A, once under A-lite.
TEARDOWN_BYTES = 1_110_000_000
CHUNK_BYTES = 8 * 1024 * 1024

# Design numbers the criteria are scaled to (see the study §3).
DEFAULT_S_R_MIN_J = 19.0  # smallest per-pair s_r in the series: Qwen3-30B spam, pilots 8-9
DEFAULT_T_EPISODE_S = 234.5  # 30B planning episode upper bound (sizing_b5.json episode_upper_s)
PRESENCE_FRACTION = 0.0025  # U4 point bar: 0.25 % of the decode energy
WRITE_IDLE_FRACTION = 0.05  # bias bar: 0.05 s_r per episode
WRITE_DECODE_FRACTION = 0.30  # mean write-effect bar (Q3 tests the mean, not added variance; A/A-lite only)


# ---------------------------------------------------------------- plan


# Five physical blocks: Q1 fits block means with intercept, drift and presence,
# so it needs at least four blocks for one residual df; five give two. The
# CLI (scripts/align_ssd_qualification.py) takes its defaults from here.
DEFAULT_BLOCKS = ("attached", "detached", "attached", "detached", "attached")
DEFAULT_IDLE_PAIRS = 6


def _abba(n_pairs: int) -> list[tuple[str, str]]:
    order = []
    for i in range(n_pairs):
        order.append(("quiet", "write") if i % 4 in (0, 3) else ("write", "quiet"))
    return order


def plan(*, blocks: Sequence[str] = DEFAULT_BLOCKS, idle_pairs: int = DEFAULT_IDLE_PAIRS,
         decode_pairs: int = 6, segment_s: float = 120.0, gap_s: float = 60.0,
         settle_s: float = 600.0) -> dict[str, Any]:
    """The schedule. Every block repeats the same idle-then-decode shape."""

    if any(kind not in ("attached", "detached") for kind in blocks) or not blocks:
        raise ValueError("blocks must be a non-empty sequence of 'attached'/'detached'")
    if "attached" not in blocks or "detached" not in blocks:
        raise ValueError("a qualification needs at least one attached and one detached block")
    if idle_pairs < 2 or decode_pairs < 2:
        raise ValueError("at least two pairs per load level")
    if not (segment_s > 0 and gap_s >= 0 and settle_s >= 0):
        raise ValueError("durations must be positive")
    segments = []
    ordinal = 0
    for index, presence in enumerate(blocks):
        block = f"{index + 1}-{presence}"
        target = "external" if presence == "attached" else "internal"
        segments.append({"ordinal": ordinal, "block": block, "presence": presence, "load": "settle",
                         "condition": "settle", "pair": None, "planned_s": settle_s, "gap_after_s": 0.0,
                         "write_target": None, "burst_after": False, "analyzed": False})
        ordinal += 1
        for load, pairs in (("idle", idle_pairs), ("decode", decode_pairs)):
            for pair, order in enumerate(_abba(pairs)):
                for condition in order:
                    segments.append({
                        "ordinal": ordinal, "block": block, "presence": presence, "load": load,
                        "condition": condition, "pair": f"{block}/{load}/{pair}", "planned_s": segment_s,
                        "gap_after_s": gap_s, "write_target": target if condition == "write" else None,
                        "burst_after": condition == "write", "analyzed": True})
                    ordinal += 1
    total = sum(s["planned_s"] + s["gap_after_s"] for s in segments)
    return {"schema": SCHEMA + ".plan", "blocks": list(blocks), "segments": segments,
            "planned_total_s": total, "note": "decode segments last as long as the fixed work; "
            "planned_s is the idle length and the decode planning guess"}


# ---------------------------------------------------------------- write pattern


class PatternWriter:
    """Fixed-cadence appends; every stream keeps its own schedule (no drift)."""

    def __init__(self, directory: str | os.PathLike[str], *, pattern: Mapping[str, Mapping[str, Any]],
                 clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
        self.directory = Path(directory)
        self.pattern = {name: dict(spec) for name, spec in pattern.items()}
        for name, spec in self.pattern.items():
            if not (spec["period_s"] > 0 and int(spec["bytes"]) > 0):
                raise ValueError(f"stream {name} needs a positive period and size")
        self.clock = clock
        self.sleep = sleep

    def run(self, seconds: float, *, stop: Callable[[], bool] = lambda: False) -> dict[str, Any]:
        self.directory.mkdir(parents=True, exist_ok=True)
        start = self.clock()
        handles = {name: (self.directory / f"{name}.bin").open("ab") for name in self.pattern}
        ticks = {name: 0 for name in self.pattern}
        due = {name: start for name in self.pattern}
        last_sync = {name: -math.inf for name in self.pattern}
        stats = {name: {"writes": 0, "bytes": 0, "fsyncs": 0} for name in self.pattern}
        max_late = 0.0
        try:
            while not stop():
                name = min(due, key=due.get)
                when = due[name]
                if when - start >= seconds:
                    break
                now = self.clock()
                if when > now:
                    self.sleep(when - now)
                    now = self.clock()
                max_late = max(max_late, now - when)
                spec = self.pattern[name]
                handle = handles[name]
                handle.write(b"j" * int(spec["bytes"]))
                handle.flush()
                stats[name]["writes"] += 1
                stats[name]["bytes"] += int(spec["bytes"])
                every = spec.get("fsync_every_s")
                if every is not None and now - last_sync[name] >= every - 1e-9:
                    os.fsync(handle.fileno())
                    last_sync[name] = now
                    stats[name]["fsyncs"] += 1
                ticks[name] += 1
                due[name] = start + ticks[name] * float(spec["period_s"])
        finally:
            for handle in handles.values():
                handle.close()
        return {"streams": stats, "elapsed_s": self.clock() - start, "max_lateness_s": max_late}


def teardown_burst(directory: str | os.PathLike[str], *, nbytes: int = TEARDOWN_BYTES, copies: int = 1,
                   tag: str = "burst", chunk: int = CHUNK_BYTES) -> dict[str, Any]:
    """Write ``copies`` files of ``nbytes`` each and fsync them (raw copy, backup)."""

    if nbytes <= 0 or copies <= 0 or chunk <= 0:
        raise ValueError("burst sizes must be positive")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    block = b"b" * min(chunk, nbytes)
    paths = []
    for copy in range(copies):
        path = directory / f"{tag}-{copy}.bin"
        with path.open("xb") as handle:
            left = nbytes
            while left > 0:
                piece = block if left >= len(block) else block[:left]
                handle.write(piece)
                left -= len(piece)
            handle.flush()
            os.fsync(handle.fileno())
        paths.append(str(path))
    return {"bytes": nbytes * copies, "paths": paths}


# ---------------------------------------------------------------- extraction


def segment_power(records: Sequence[Any], start_s: float, end_s: float, *, guard_s: float = 5.0) -> dict[str, Any]:
    """Mean rail power over [start + guard, end - guard], overlap-weighted.

    ``records`` are ``PowermetricsRecord``s from one continuous capture; the
    interval of a record is [timestamp_s, timestamp_s + elapsed_ns / 1e9]. A
    constant anchor offset of that capture shifts every segment alike.
    """

    lo, hi = start_s + guard_s, end_s - guard_s
    if not hi > lo:
        return {"covered_s": 0.0, "power_w": None, "flags": ["segment.too_short"]}
    energy = {"gpu": 0.0, "cpu": 0.0, "ane": 0.0}
    covered = 0.0
    for record in records:
        r0 = float(record.timestamp_s)
        width = record.elapsed_ns / 1e9
        if width <= 0:
            continue
        overlap = min(hi, r0 + width) - max(lo, r0)
        if overlap <= 0:
            continue
        share = overlap / width
        energy["gpu"] += record.rail_energy_mj["gpu_energy"] / 1000.0 * share
        energy["cpu"] += record.rail_energy_mj["cpu_energy"] / 1000.0 * share
        energy["ane"] += record.rail_energy_mj["ane_energy"] / 1000.0 * share
        covered += overlap
    flags = [] if covered >= 0.95 * (hi - lo) else ["segment.coverage_below_95pct"]
    power = {k: (v / covered if covered > 0 else None) for k, v in energy.items()}
    return {"covered_s": covered, "power_w": power, "flags": flags}


def extract(plist_bytes: bytes, journal: Sequence[Mapping[str, Any]], *, guard_s: float = 5.0,
            parse: Callable[[bytes], Sequence[Any]] | None = None) -> list[dict[str, Any]]:
    """One row per analyzed segment from the run journal and the capture."""

    if parse is None:
        from joulewise.adapters.powermetrics import parse_powermetrics_records as parse
    records = list(parse(plist_bytes))
    rows = []
    for entry in journal:
        if entry.get("kind") != "segment" or not entry.get("analyzed"):
            continue
        start, end = float(entry["work_start_epoch_s"]), float(entry["work_end_epoch_s"])
        measured = segment_power(records, start, end, guard_s=guard_s)
        rows.append({**{k: entry.get(k) for k in ("ordinal", "block", "presence", "load", "condition",
                                                   "pair", "smc_means", "flags")},
                     "start_epoch_s": start, "end_epoch_s": end, "covered_s": measured["covered_s"],
                     "power_w": measured["power_w"],
                     "extract_flags": measured["flags"]})
    return rows


# ---------------------------------------------------------------- evaluation


def _interval(values: Sequence[float], level: float = 0.90) -> dict[str, Any] | None:
    n = len(values)
    if n < 2:
        return None
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    t = student_t_quantile(0.5 + level / 2, n - 1)
    half = t * sd / math.sqrt(n)
    return {"n": n, "mean": mean, "sd": sd, "df": n - 1, "lo": mean - half, "hi": mean + half}


def _judge(interval: Mapping[str, Any] | None, margin: float) -> str:
    """PASS inside the margin; FAIL if the point is outside; else INCONCLUSIVE."""

    if interval is None or not math.isfinite(margin):
        return INCONCLUSIVE
    if abs(interval["mean"]) > margin:
        return FAIL
    if -margin <= interval["lo"] and interval["hi"] <= margin:
        return PASS
    return INCONCLUSIVE


def _gpu(row: Mapping[str, Any]) -> float | None:
    power = row.get("power_w") or {}
    value = power.get("gpu")
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def paired_write_effect(rows: Sequence[Mapping[str, Any]], *, presence: str, load: str) -> dict[str, Any] | None:
    """Mean of (write - quiet) GPU power over complete pairs, with a 90 % t interval."""

    pairs: dict[str, dict[str, float]] = {}
    for row in rows:
        if row.get("presence") != presence or row.get("load") != load or row.get("extract_flags"):
            continue
        value = _gpu(row)
        if value is None:
            continue
        pairs.setdefault(row["pair"], {})[row["condition"]] = value
    diffs = [p["write"] - p["quiet"] for p in pairs.values() if "write" in p and "quiet" in p]
    return _interval(diffs)


def _ols(x_rows: Sequence[Sequence[float]], y: Sequence[float]) -> tuple[list[float], list[list[float]], float, int]:
    """Least squares by the normal equations: coefficients, (X'X)^-1, s^2 and df."""

    p = len(x_rows[0])
    xtx = [[sum(r[i] * r[j] for r in x_rows) for j in range(p)] for i in range(p)]
    xty = [sum(r[i] * v for r, v in zip(x_rows, y)) for i in range(p)]
    aug = [xtx[i] + [1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
    for col in range(p):
        pivot = max(range(col, p), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("design is singular")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [v / div for v in aug[col]]
        for r in range(p):
            if r != col:
                f = aug[r][col]
                aug[r] = [a - f * b for a, b in zip(aug[r], aug[col])]
    inv = [row[p:] for row in aug]
    beta = [sum(inv[i][j] * xty[j] for j in range(p)) for i in range(p)]
    resid = [v - sum(b * xv for b, xv in zip(beta, r)) for r, v in zip(x_rows, y)]
    df = len(y) - p
    s2 = sum(e * e for e in resid) / df if df > 0 else math.nan
    return beta, inv, s2, df


def presence_offset(rows: Sequence[Mapping[str, Any]], *, load: str) -> dict[str, Any] | None:
    """Attached minus detached quiet GPU power, adjusted for linear drift.

    Model over *block means* of the quiet segments: P = a + b * t + c *
    attached, with t the mean segment start in hours.  Blocks, rather than
    segments, are the independent units for the physical presence treatment.
    Consequently the residual degrees of freedom are ``blocks - 3``.  The
    old segment-level fit was pseudoreplication: changing the cable once did
    not turn every segment in that block into an independent presence trial.
    """

    kept = []
    for row in rows:
        if row.get("load") != load or row.get("condition") != "quiet" or row.get("extract_flags"):
            continue
        value = _gpu(row)
        if value is not None:
            kept.append((row, value))
    # One time basis for every row: epoch stamps when all rows have them,
    # otherwise the planned ordinal clock for all (never a mix of the two).
    epoch = all(isinstance(row.get("start_epoch_s"), (int, float)) for row, _v in kept)
    picked = [(float(row["start_epoch_s"]) / 3600 if epoch else float(row["ordinal"]) * 180 / 3600,
               1.0 if row["presence"] == "attached" else 0.0, value, row["block"]) for row, value in kept]
    grouped: dict[str, list[tuple[float, float, float]]] = {}
    for t, attached, value, block in picked:
        grouped.setdefault(block, []).append((t, attached, value))
    if len(grouped) < 4:
        return None
    # The fit weights block means equally, which is valid while their
    # segment-noise shares are similar. Fail closed (INCONCLUSIVE) when a block
    # kept fewer than half the quiet segments of the fullest block.
    counts = {block: len(members) for block, members in grouped.items()}
    if 2 * min(counts.values()) < max(counts.values()):
        return None
    block_rows = [(block, statistics.fmean(t for t, _a, _v in members), members[0][1],
                   statistics.fmean(v for _t, _a, v in members))
                  for block, members in grouped.items()]
    if {a for _block, _t, a, _v in block_rows} != {0.0, 1.0}:
        return None
    t0 = min(t for _block, t, _a, _v in block_rows)
    x_rows = [[1.0, t - t0, a] for _block, t, a, _v in block_rows]
    y = [v for _block, _t, _a, v in block_rows]
    try:
        beta, inv, s2, _df = _ols(x_rows, y)
    except ValueError:
        return None
    se = math.sqrt(s2 * inv[2][2]) if math.isfinite(s2) else math.nan
    df = len(block_rows) - 3
    if df <= 0 or not math.isfinite(se):
        return None
    t = student_t_quantile(0.95, df)
    nonlinearity = {block: value - sum(b * xv for b, xv in zip(beta, xr))
                    for (block, _time, _attached, value), xr in zip(block_rows, x_rows)}
    return {"mean": beta[2], "se": se, "df": df, "lo": beta[2] - t * se, "hi": beta[2] + t * se,
            "drift_w_per_h": beta[1], "reference_power_w": statistics.fmean(y),
            "quiet_segments_per_block": counts, "time_basis": "epoch" if epoch else "ordinal",
            "block_mean_minus_fit_w_print_only": nonlinearity}


def criteria_margins(*, s_r_min_j: float = DEFAULT_S_R_MIN_J,
                     t_episode_s: float = DEFAULT_T_EPISODE_S) -> dict[str, float]:
    """Power margins (W) for Q2/Q3 from the per-episode energy bars."""

    if not (s_r_min_j > 0 and t_episode_s > 0):
        raise ValueError("s_r and episode duration must be positive")
    return {"q2_write_idle_w": WRITE_IDLE_FRACTION * s_r_min_j / t_episode_s,
            "q3_write_decode_w": WRITE_DECODE_FRACTION * s_r_min_j / t_episode_s}


def operational(ops: Mapping[str, Any]) -> dict[str, Any]:
    """Q5 from the session journal summary; a missing item is a failure."""

    checks = {
        "arm_check_pass_at_start": ops.get("arm_check_start") == "PASS",
        "arm_check_pass_at_end": ops.get("arm_check_end") == "PASS",
        "no_volume_loss": ops.get("volume_lost") == 0,
        "no_metadata_daemon_contention": ops.get("metadata_daemon_contention_intervals") == 0,
        "battery_float_held": ops.get("battery_float_violations") == 0,
        "thermal_offset_within_half_band": (isinstance(ops.get("s_slow_presence_offset_c"), (int, float))
                                            and abs(ops["s_slow_presence_offset_c"]) <= 0.5),
    }
    return {"verdict": PASS if all(checks.values()) else FAIL, "checks": checks}


def evaluate(rows: Sequence[Mapping[str, Any]], *, ops: Mapping[str, Any],
             s_r_min_j: float = DEFAULT_S_R_MIN_J, t_episode_s: float = DEFAULT_T_EPISODE_S) -> dict[str, Any]:
    margins = criteria_margins(s_r_min_j=s_r_min_j, t_episode_s=t_episode_s)
    presence = presence_offset(rows, load="decode")
    presence_idle = presence_offset(rows, load="idle")
    write_idle = paired_write_effect(rows, presence="attached", load="idle")
    write_decode = paired_write_effect(rows, presence="attached", load="decode")
    control_idle = paired_write_effect(rows, presence="detached", load="idle")
    control_decode = paired_write_effect(rows, presence="detached", load="decode")
    q1_margin = PRESENCE_FRACTION * presence["reference_power_w"] if presence else math.nan
    q = {
        "Q1_presence_decode": _judge(presence, q1_margin),
        "Q2_write_idle": _judge(write_idle, margins["q2_write_idle_w"]),
        "Q3_write_decode": _judge(write_decode, margins["q3_write_decode_w"]),
    }
    q5 = operational(ops)
    q["Q5_operational"] = q5["verdict"]
    # A and A-lite are capped off: Q3 bounds only the mean write effect, and
    # no variability criterion exists yet (study section 6). Q2/Q3 still print.
    allowed = "B" if q["Q1_presence_decode"] == PASS and q5["verdict"] == PASS else "C"
    return {"schema": SCHEMA + ".verdict", "criteria": q, "strongest_option_allowed": allowed,
            "write_criteria_pass_print_only": q["Q2_write_idle"] == PASS and q["Q3_write_decode"] == PASS,
            "margins_w": {"q1_presence_decode_w": q1_margin if math.isfinite(q1_margin) else None, **margins},
            "inputs": {"s_r_min_j": s_r_min_j, "t_episode_s": t_episode_s},
            "estimates_w": {"presence_decode": presence, "presence_idle_print_only": presence_idle,
                            "write_idle": write_idle, "write_decode": write_decode,
                            "internal_write_control_idle_print_only": control_idle,
                            "internal_write_control_decode_print_only": control_decode},
            "operational": q5,
            "note": "B needs Q1 and Q5 PASS; otherwise C. A and A-lite are not available from this "
                    "verdict until a write-variability criterion exists (Q3 tests the mean only). "
                    "The council and Ed decide; this verdict only states what the data allow."}



# ---------------------------------------------------------------- metadata daemons and ops


# Daemons a mounted volume can wake (Spotlight, fsevents, Time Machine, disk
# arbitration, APFS space reclaim); contention.py's limit is 0.05 CPU-s/s.
METADATA_DAEMONS = frozenset({
    "mds", "mds_stores", "mdworker", "mdworker_shared", "mdbulkimport", "mdsync", "corespotlightd",
    "spotlightknowledged", "fseventsd", "backupd", "backupd-helper", "diskarbitrationd", "deleted",
    "apfsd", "fsck_apfs", "revisiond"})
DAEMON_LIMIT_CPU_S_PER_S = 0.05
PS_ARGV = ("/bin/ps", "-Ao", "pid=,time=,ucomm=")


def parse_ps_time(text: str) -> float:
    """``ps`` TIME: [[dd-]hh:]mm:ss[.ff] as seconds."""

    days = 0
    if "-" in text:
        head, text = text.split("-", 1)
        days = int(head)
    parts = text.split(":")
    if not 2 <= len(parts) <= 3:
        raise ValueError(f"bad ps time {text!r}")
    seconds = float(parts[-1]) + 60 * int(parts[-2])
    if len(parts) == 3:
        seconds += 3600 * int(parts[0])
    return seconds + 86400 * days


def parse_ps(text: str) -> dict[tuple[int, str], float]:
    rows = {}
    for line in text.splitlines():
        fields = line.split(None, 2)
        if len(fields) != 3:
            continue
        try:
            rows[(int(fields[0]), fields[2].strip())] = parse_ps_time(fields[1])
        except ValueError:
            continue
    return rows


def daemon_cpu_rates(before: Mapping[tuple[int, str], float], after: Mapping[tuple[int, str], float],
                     seconds: float) -> dict[str, Any]:
    """CPU-s/s of each metadata daemon over the segment; new processes count from zero."""

    if not seconds > 0:
        return {"rates": {}, "max": None, "contended": None}
    rates: dict[str, float] = {}
    for key, value in after.items():
        if key[1] not in METADATA_DAEMONS:
            continue
        delta = value - before.get(key, 0.0)
        if delta > 0:
            rates[key[1]] = rates.get(key[1], 0.0) + delta / seconds
    peak = max(rates.values(), default=0.0)
    return {"rates": rates, "max": peak, "contended": peak > DAEMON_LIMIT_CPU_S_PER_S}


def summarize_ops(journal: Sequence[Mapping[str, Any]], *, s_slow_key: str | None = None) -> dict[str, Any]:
    """The Q5 inputs from a run journal; anything unobserved stays None (fails)."""

    arm = [r for r in journal if r.get("kind") == "arm_check"]
    segments = [r for r in journal if r.get("kind") == "segment" and r.get("analyzed")]
    attached = [r for r in segments if r.get("presence") == "attached"]
    daemons = [r.get("metadata_daemons") for r in attached]
    contention = (None if not daemons or any(d is None or d.get("contended") is None for d in daemons)
                  else sum(1 for d in daemons if d["contended"]))
    b0ac = [((r.get("smc_means") or {}).get("B0AC")) for r in segments if r.get("load") == "idle"]
    battery = (None if not b0ac or any(v is None for v in b0ac)
               else sum(1 for v in b0ac if abs(v) > 200.0))
    offset = None
    if s_slow_key:
        def mean_for(kind):
            values = [(r.get("smc_means") or {}).get(s_slow_key) for r in segments
                      if r.get("presence") == kind and r.get("load") == "idle" and r.get("condition") == "quiet"]
            if not values or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
                return None  # a missing reading is missing evidence: Q5 fails
            return statistics.fmean(values)
        a, d = mean_for("attached"), mean_for("detached")
        offset = a - d if a is not None and d is not None else None
    return {"arm_check_start": arm[0].get("verdict") if arm else None,
            "arm_check_end": arm[-1].get("verdict") if len(arm) > 1 else None,
            "volume_lost": sum(1 for r in attached if "volume.absent_in_attached_block" in (r.get("flags") or [])),
            "metadata_daemon_contention_intervals": contention,
            "metadata_daemon_contention_detached_print_only": sum(
                1 for r in segments if r.get("presence") == "detached"
                and (r.get("metadata_daemons") or {}).get("contended")),
            "battery_float_violations": battery,
            "s_slow_presence_offset_c": offset}


# ---------------------------------------------------------------- session runner


class _Sampler:
    """1 Hz SMC reads (PSTR, PDTR, B0AC and any extra keys) kept in memory."""

    def __init__(self, read: Callable[[], Mapping[str, Any]], *, clock: Callable[[], float] = time.time,
                 period_s: float = 1.0):
        import threading

        self._read, self._clock, self._period = read, clock, period_s
        self.rows: list[dict[str, Any]] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self) -> None:
        while not self._stop.is_set():
            started = self._clock()
            try:
                values = dict(self._read().get("values", {}))
            except Exception as exc:  # a failed read is data, never a crash
                values = {"error": f"{type(exc).__name__}: {exc}"}
            self.rows.append({"epoch_s": started, **values})
            self._stop.wait(self._period)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=5)

    def means(self, start: float, end: float) -> dict[str, float]:
        picked = [r for r in self.rows if start <= r["epoch_s"] <= end]
        keys = sorted({k for r in picked for k in r if k != "epoch_s"})
        out = {}
        for key in keys:
            values = [r[key] for r in picked
                      if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
            if values:
                out[key] = statistics.fmean(values)
        return out


def run_session(schedule: Mapping[str, Any], *, journal_path: str | os.PathLike[str],
                external_dir: str | os.PathLike[str], internal_dir: str | os.PathLike[str],
                decode: Callable[[], Mapping[str, float]], wait_presence: Callable[[str], None],
                pattern: Mapping[str, Mapping[str, Any]] | None = None,
                smc_read: Callable[[], Mapping[str, Any]] | None = None,
                burst_bytes: int = TEARDOWN_BYTES, burst_copies: int = 2,
                ps_text: Callable[[], str] | None = None,
                is_attached: Callable[[], bool] | None = None,
                clock: Callable[[], float] = time.time, sleep: Callable[[float], None] = time.sleep,
                monotonic: Callable[[], float] = time.monotonic) -> list[dict[str, Any]]:
    """Run every segment, journaling each to ``journal_path`` (internal disk).

    ``decode()`` performs the fixed work and returns ``work_start_epoch_s`` and
    ``work_end_epoch_s`` stamped around the decode only (after load/warmup).
    ``wait_presence(kind)`` returns once the drive is physically attached or
    detached as the block requires (the operator does the plugging).
    """

    import json
    import threading

    journal_path = Path(journal_path)
    ext, jdir = Path(external_dir).resolve(), journal_path.parent.resolve()
    if ext.is_relative_to(jdir) or jdir.is_relative_to(ext):
        raise ValueError("the journal must not share a tree with the external write target")
    pattern = dict(pattern or {**WINDOW_PATTERN, **WORST_CASE_EXTRA})
    sampler = _Sampler(smc_read, clock=clock) if smc_read is not None else None
    rows: list[dict[str, Any]] = []
    journal_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(row: dict[str, Any]) -> None:
        rows.append(row)
        with journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    if sampler is not None:
        sampler.start()
    current_block = None
    try:
        emit({"kind": "session_start", "epoch_s": clock(), "schema": SCHEMA + ".journal",
              "pattern": pattern, "burst_bytes": burst_bytes, "burst_copies": burst_copies})
        for segment in schedule["segments"]:
            if segment["block"] != current_block:
                wait_presence(segment["presence"])
                current_block = segment["block"]
                emit({"kind": "block_start", "block": current_block, "epoch_s": clock()})
            target = segment.get("write_target")
            directory = None
            if target is not None:
                base = Path(external_dir if target == "external" else internal_dir)
                directory = base / f"seg-{segment['ordinal']:04d}"
            stop = threading.Event()
            writer_stats: dict[str, Any] = {}
            worker = None
            if directory is not None:
                writer = PatternWriter(directory, pattern=pattern, clock=monotonic, sleep=sleep)
                worker = threading.Thread(
                    target=lambda: writer_stats.update(writer.run(math.inf, stop=stop.is_set)), daemon=True)
                worker.start()
            flags = []
            before = parse_ps(ps_text()) if ps_text is not None else None
            if segment["load"] == "decode":
                stamps = decode()
                work_start, work_end = float(stamps["work_start_epoch_s"]), float(stamps["work_end_epoch_s"])
            else:
                work_start = clock()
                sleep(float(segment["planned_s"]))
                work_end = clock()
            if worker is not None:
                stop.set()
                worker.join(timeout=30)
                if worker.is_alive():
                    flags.append("writer.did_not_stop")
            daemons = None
            if before is not None:
                daemons = daemon_cpu_rates(before, parse_ps(ps_text()), work_end - work_start)
            if is_attached is not None and segment["presence"] == "attached" and not is_attached():
                flags.append("volume.absent_in_attached_block")
            burst = None
            if segment.get("burst_after") and directory is not None:
                burst = teardown_burst(directory, nbytes=burst_bytes, copies=burst_copies)
            emit({"kind": "segment", **{k: segment.get(k) for k in ("ordinal", "block", "presence", "load",
                                                                      "condition", "pair", "analyzed")},
                  "write_target": target, "work_start_epoch_s": work_start, "work_end_epoch_s": work_end,
                  "writer": writer_stats or None, "burst": burst, "flags": flags,
                  "metadata_daemons": daemons,
                  "smc_means": sampler.means(work_start, work_end) if sampler is not None else None})
            sleep(float(segment.get("gap_after_s", 0.0)))
        emit({"kind": "session_end", "epoch_s": clock()})
    finally:
        if sampler is not None:
            sampler.stop()
            emit({"kind": "smc_rows", "rows": sampler.rows})
    return rows
