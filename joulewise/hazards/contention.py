"""Contention hazard: a process outside the measurement tree uses CPU.

Measured directly as CPU-seconds per second of every process, from the
difference of cumulative CPU time between two ``ps`` snapshots (never the
decaying ``%CPU``).  A process is identified by (pid, lstart) so a reused pid
is a new process.  The **measurement tree** is every descendant of the tree
roots (the driver's pid): the driver, the chain's process group, sudo and
powermetrics, caffeinate, the monitor and the probes themselves.

Arm, the dwell (plan §2.3): 30 s intervals; an interval is clean when no
process outside the tree exceeds 0.05 CPU-s/s (5 % of one core).  READY after
600 s of consecutive clean intervals; if none appears within 2700 s, REFUSE
(the window is NULL).  ``kernel_task`` is included at the dwell, where the Mac
should be idle.  An interval whose snapshot failed is UNMEASURED and breaks
the clean run.

In the window (flag only) the monitor journals an interval every 10 s;
:func:`span_findings` gives ``contention.request_overlap`` when an outside
process exceeds 0.05 CPU-s/s in an interval overlapping a member's request,
and ``contention.unmeasured`` when no interval covers part of the request.
``kernel_task`` is excluded in the window (its time during a request is the
workload's own driver and I/O work); its share is journaled and disclosed.

Reused (verified at a0a4f5a7): ``quiet_admission.parse_ps`` (the lstart/TIME
grammar) and the interval accounting of ``quiet_admission.interval_metrics``
(ported here so every outside consumer is kept, not only the top ten);
``prewindow.CPU_LIMIT_PERCENT`` = 5.0 and the 600 s / 30 s / 2700 s dwell of
``prewindow.t0_wait``.  The direct-CPU precedent is ``night_gate.py:1836``,
built after the 09-22 fseventsd contamination.

``PS_ARGV`` asks for ``ucomm`` (the 16-character accounting name) instead of
``comm``: on this Mac ``ps -Ao pid,ppid,lstart,time,comm`` costs 20 ms of CPU
per call against 9.6 ms with ``ucomm`` (measured 10-05), and the monitor's
whole budget is 0.5 % of one core.  The column layout is the one
``parse_ps`` reads.

Work a ps difference cannot name.  A process that starts and exits between
two snapshots is invisible to it, and one that exits inside an interval has
no closing counter (it is listed as ``unaccounted``).  Two measurements cover
that work:

- **Exited above the limit.**  A process above the limit in one interval
  that exits inside the next makes that next interval dirty too, at its
  previous rate (``exited_over_limit``).  It ran for some part of the
  interval, and no counter says it slowed down.
- **The host term.**  Every snapshot also reads the host's cumulative CPU
  ticks in process (``host_processor_info``, 100 ticks per CPU-second; about
  14 us, no child).  Each interval journals ``host_busy_cpu_s_per_s`` (user +
  system + nice over every logical CPU), ``outside_aggregate_cpu_s_per_s`` =
  host busy minus the measurement tree (and minus a listed, excluded
  ``kernel_task``), and ``unattributed_cpu_s_per_s`` = host busy minus every
  process ps measured.  The aggregate term counts the short-lived and many
  small processes that the old load-average proxies saw.  The dwell judges it
  only when the window plan registers ``aggregate_cpu_limit_s_per_s``.  No
  value is registered yet: the idle aggregate of this Mac has not been
  measured under a launchd job, and a threshold sized without that number
  could make every dwell refuse.  ALPHA-1's journal measures it.  In the
  window the aggregate is journaled, never judged: it includes the kernel's
  own work for the request, which an unprivileged ``ps -A`` cannot separate,
  because it does not list ``kernel_task`` (pid 0; checked 10-05).  Before
  each member, the core's idle admission judges the aggregate (CPU busy ratio
  and processor power, unchanged).

The kernel_task include/exclude rule applies when ps lists it.
"""

from __future__ import annotations

import ctypes
import dataclasses
import gzip
import math
import os
import sys
from datetime import datetime
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from joulewise import prewindow, quiet_admission
from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, RawRef, Stamp, Verdict, finding,
    require_thresholds, row,
)

MODULE = "contention"
PS_ARGV = ("/bin/ps", "-Ao", "pid,ppid,lstart,time,ucomm")
PROBE_TIMEOUT_S = 10.0
KERNEL_TASK = "kernel_task"
REPORT_FLOOR_CPU_S_PER_S = 0.005  # outside consumers below this are counted, not listed

DEFAULT_THRESHOLDS: dict[str, Any] = {
    "cpu_limit_s_per_s": prewindow.CPU_LIMIT_PERCENT / 100.0,   # 0.05
    "interval_s": prewindow.INTERVAL_S,                         # 30
    "clean_s": prewindow.MIN_CLEAN_DWELL_S,                     # 600
    "cap_s": prewindow.DEFAULT_TIMEOUT_S,                       # 2700
    "window_interval_s": 10,
    # None: the host aggregate is journaled at the dwell, not judged (module
    # docstring).  A registered number makes an interval dirty above it.
    "aggregate_cpu_limit_s_per_s": None,
}
ARM_THRESHOLD_KEYS = ("cpu_limit_s_per_s", "interval_s", "clean_s", "cap_s")
AGGREGATE_KEY = "aggregate_cpu_limit_s_per_s"

HostReader = Callable[[], Sequence[Sequence[int]]]
CPU_STATES = ("user", "system", "idle", "nice")  # host_processor_info order
PROCESSOR_CPU_LOAD_INFO = 2
TICK_WRAP = 1 << 32  # natural_t per-CPU counters


def aggregate_limit(thresholds: Mapping[str, Any]) -> float | None:
    """The registered aggregate limit, or None when the plan registers none."""

    value = thresholds.get(AGGREGATE_KEY)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not value > 0:
        raise ValueError(f"{MODULE} threshold {AGGREGATE_KEY} must be a positive number or null")
    return float(value)


# --------------------------------------------------------------------------
# Host CPU ticks (in process)


_HOST: dict[str, Any] = {}


def _host_functions() -> dict[str, Any]:
    if not _HOST:
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        libc.mach_host_self.restype = ctypes.c_uint
        libc.host_processor_info.argtypes = [
            ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)), ctypes.POINTER(ctypes.c_uint)]
        libc.host_processor_info.restype = ctypes.c_int
        libc.vm_deallocate.argtypes = [ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t]
        libc.vm_deallocate.restype = ctypes.c_int
        _HOST.update(libc=libc, host=libc.mach_host_self(),
                     task=ctypes.c_uint.in_dll(libc, "mach_task_self_").value)
    return _HOST


def read_host_cpu() -> list[list[int]]:
    """Cumulative ticks per logical CPU, ``[[user, system, idle, nice], ...]``.

    ``host_processor_info(PROCESSOR_CPU_LOAD_INFO)``: read-only, unprivileged,
    in process.  One tick is 1/100 s (``sysconf(_SC_CLK_TCK)``; checked live
    10-05: 99.5 ticks per CPU per second over 5 s on 16 CPUs).  Raises OSError
    off macOS or on a Mach error.
    """

    if sys.platform != "darwin":
        raise OSError("host_processor_info requires macOS")
    functions = _host_functions()
    count = ctypes.c_uint()
    info = ctypes.POINTER(ctypes.c_int)()
    words = ctypes.c_uint()
    status = functions["libc"].host_processor_info(
        functions["host"], PROCESSOR_CPU_LOAD_INFO, ctypes.byref(count), ctypes.byref(info),
        ctypes.byref(words))
    if status != 0:
        raise OSError(f"host_processor_info failed with kern_return {status}")
    try:
        values = [info[index] & 0xFFFFFFFF for index in range(words.value)]
    finally:
        functions["libc"].vm_deallocate(functions["task"], ctypes.cast(info, ctypes.c_void_p).value,
                                        words.value * ctypes.sizeof(ctypes.c_int))
    if count.value <= 0 or len(values) != count.value * len(CPU_STATES):
        raise OSError(f"host_processor_info returned {len(values)} words for {count.value} CPUs")
    return [values[cpu * 4:(cpu + 1) * 4] for cpu in range(count.value)]


def host_ticks_delta(before: Sequence[Sequence[int]], after: Sequence[Sequence[int]],
                     ) -> dict[str, int]:
    """Busy (user + system + nice) and idle ticks between two reads, per-CPU wrap-safe."""

    if len(before) != len(after):
        raise ValueError("the logical CPU count changed between host reads")
    busy = idle = 0
    for first, final in zip(before, after):
        delta = [(b - a) % TICK_WRAP for a, b in zip(first, final)]
        busy += delta[0] + delta[1] + delta[3]
        idle += delta[2]
    return {"busy_ticks": busy, "idle_ticks": idle, "cpus": len(after)}


# --------------------------------------------------------------------------
# Snapshots


@dataclasses.dataclass(frozen=True)
class Snapshot:
    started: Stamp
    finished: Stamp
    rows: Mapping[tuple[int, str], Mapping[str, Any]]
    raw: RawRef | None
    error: str | None = None
    host: Sequence[Sequence[int]] | None = None  # read_host_cpu() just after ``started``
    host_error: str | None = None

    @property
    def midpoint_ns(self) -> int:
        return (self.started.monotonic_ns + self.finished.monotonic_ns) // 2

    def stamp_json(self) -> dict[str, Any]:
        return {"started": self.started.to_json(), "finished": self.finished.to_json()}


_START_EPOCH_CACHE: dict[str, float] = {}
# Each row line of the previous snapshot -> its parsed fields.  Most rows of
# a 10 s snapshot repeat byte for byte (an idle process's TIME does not move),
# so a row is parsed once and looked up after that.
_ROW_CACHE: dict[str, tuple[int, int, str, float, str, float]] = {}


def _parse_row(line: str) -> tuple[int, int, str, float, str, float]:
    parts = line.split(None, 8)
    if len(parts) != 9:
        raise ValueError(f"malformed ps row: {line!r}")
    pid, ppid = int(parts[0]), int(parts[1])
    start = " ".join(parts[2:7])
    epoch = _START_EPOCH_CACHE.get(start)
    if epoch is None:
        epoch = datetime.strptime(start, "%a %b %d %H:%M:%S %Y").timestamp()
        if len(_START_EPOCH_CACHE) > 50_000:
            _START_EPOCH_CACHE.clear()
        _START_EPOCH_CACHE[start] = epoch
    if pid < 0 or ppid < 0:
        raise ValueError("duplicate or invalid process identity")
    return (pid, ppid, start, epoch, parts[8].strip(), quiet_admission._cpu_seconds(parts[7]))


def parse(stdout: bytes) -> dict[tuple[int, str], dict[str, Any]]:
    """``quiet_admission.parse_ps`` with the lstart conversion and repeated rows cached.

    The same grammar and the same rows (the command stripped of ucomm's
    padding); ``strptime`` on every row cost 3.6 ms per snapshot, most of the
    monitor's own CPU, and a process's start text never changes.  A row line
    identical to one of the previous snapshot's is not parsed again (10-06:
    0.9 ms of CPU per 680-row snapshot without it).
    tests/hazards/test_contention.py checks equality with ``parse_ps``.
    """

    global _ROW_CACHE
    text = stdout.decode("utf-8", errors="replace")
    lines = text.strip().splitlines()
    if not lines or not lines[0].split()[:2] == ["PID", "PPID"]:
        raise ValueError("ps header missing")
    cache = _ROW_CACHE
    seen: dict[str, tuple[int, int, str, float, str, float]] = {}
    result: dict[tuple[int, str], dict[str, Any]] = {}
    for line in lines[1:]:
        fields = cache.get(line)
        if fields is None:
            fields = _parse_row(line)
        seen[line] = fields
        pid, ppid, start, epoch, command, cpu = fields
        identity = (pid, start)
        if identity in result:
            raise ValueError("duplicate or invalid process identity")
        result[identity] = dict(pid=pid, ppid=ppid, start_identity=start, start_epoch_s=epoch,
                                command=command, cumulative_cpu_seconds=cpu)
    if not result:
        raise ValueError("ps contains no processes")
    _ROW_CACHE = seen
    return result


def take_snapshot(ctx: Context, *, raw_name: str = "ps.txt", compress: bool = False,
                  host_reader: HostReader | None = read_host_cpu) -> Snapshot:
    """One ``ps`` snapshot; the raw bytes are kept (gzip with mtime 0 when ``compress``).

    The host's CPU ticks are read just before ps (``host_reader``; None skips
    them).  A failed host read is recorded on the snapshot, never a ps error.
    """

    started = ctx.stamp()
    host = host_error = None
    if host_reader is not None:
        try:
            host = [list(cpu) for cpu in host_reader()]
        except Exception as exc:  # recorded; judged only under a registered aggregate limit
            host_error = f"{type(exc).__name__}: {exc}"
    completed = ctx.run(PS_ARGV, PROBE_TIMEOUT_S)
    finished = ctx.stamp()
    data = completed.stdout
    raw = (ctx.keep_raw(raw_name + ".gz", gzip.compress(data, compresslevel=1, mtime=0)) if compress
           else ctx.keep_raw(raw_name, data))
    error = None
    rows: dict[tuple[int, str], dict[str, Any]] = {}
    if completed.error:
        error = f"ps could not run: {completed.error}"
    elif completed.timed_out:
        error = f"ps timed out after {PROBE_TIMEOUT_S} s"
    elif completed.returncode != 0:
        error = f"ps exit code {completed.returncode}"
    else:
        try:
            rows = parse(data)
        except ValueError as exc:
            error = f"ps output unparsable: {exc}"
    return Snapshot(started, finished, rows, raw, error, host, host_error)


def tree_identities(rows: Iterable[Mapping[str, Any]], roots: Iterable[int]) -> set[int]:
    """Pids of the roots and every descendant by ppid closure."""

    members = set(int(pid) for pid in roots)
    children: dict[int, list[int]] = {}
    for row in rows:
        children.setdefault(row["ppid"], []).append(row["pid"])
    pending = list(members)
    while pending:
        for child in children.get(pending.pop(), ()):
            if child not in members:
                members.add(child)
                pending.append(child)
    return members


def interval(before: Snapshot, after: Snapshot, *, tree_roots: Iterable[int],
             include_kernel_task: bool, limit: float,
             previous_over: Mapping[tuple[int, str], float] | None = None,
             aggregate_limit: float | None = None) -> dict[str, Any]:
    """CPU-s/s of every process between two snapshots, split by tree membership.

    Ported from ``quiet_admission.interval_metrics``: a process present in both
    snapshots contributes its counter difference; a process that started inside
    the interval contributes its whole counter; one that exited has no
    measurable delta and is listed as unaccounted.

    ``previous_over`` maps (pid, start) to the rate of each outside process
    that was above ``limit`` in the previous interval (:func:`over_limit`); one
    of them that exited inside this interval makes it dirty at that rate.
    ``aggregate_limit`` (None: not judged) makes the interval dirty when the
    host's busy CPU outside the tree exceeds it; with a limit, an unread host
    term leaves the interval unmeasured.
    """

    window = {"monotonic_ns": [before.midpoint_ns, after.midpoint_ns],
              "monotonic_raw_ns": [_mid(before, "monotonic_raw_ns"), _mid(after, "monotonic_raw_ns")],
              "wall_ns": [_mid(before, "wall_ns"), _mid(after, "wall_ns")]}
    result: dict[str, Any] = {"interval": window, "error": None}
    if before.error or after.error:
        result.update(error=before.error or after.error, clean=None)
        return result
    elapsed_s = (after.midpoint_ns - before.midpoint_ns) / 1e9
    if not math.isfinite(elapsed_s) or elapsed_s <= 0:
        result.update(error="snapshots are not in time order", clean=None)
        return result
    union = {**before.rows, **after.rows}
    tree = tree_identities(union.values(), tree_roots)
    wall_start_s = before.started.wall_ns / 1e9
    outside: list[dict[str, Any]] = []
    unaccounted: list[dict[str, Any]] = []
    exited_over: list[dict[str, Any]] = []
    tree_cpu = 0.0
    kernel_task_cpu = None
    for identity in sorted(set(before.rows) | set(after.rows)):
        first, final = before.rows.get(identity), after.rows.get(identity)
        row = final or first
        if final is None or (first is None and row["start_epoch_s"] < wall_start_s - 1):
            unaccounted.append({"pid": row["pid"], "command": row["command"],
                                "start": row["start_identity"],
                                "reason": "exited" if final is None else "missed by the first snapshot"})
            if final is None and previous_over and identity in previous_over:
                exited_over.append({
                    "pid": row["pid"], "command": row["command"], "start": row["start_identity"],
                    "cpu_s_per_s": previous_over[identity],
                    "basis": "exited inside this interval; its rate over the previous interval"})
            continue
        delta = final["cumulative_cpu_seconds"] - (first["cumulative_cpu_seconds"] if first else 0.0)
        if not math.isfinite(delta) or delta < 0:
            # Seen live (10-05): a process exiting between snapshots is listed
            # with TIME 0:00.00 while it is a zombie.  Its delta is unmeasurable.
            unaccounted.append({"pid": row["pid"], "command": row["command"],
                                "start": row["start_identity"], "reason": "counter regressed"})
            continue
        rate = delta / elapsed_s
        if row["command"] == KERNEL_TASK and row["pid"] == 0:
            kernel_task_cpu = rate
            if not include_kernel_task:
                continue
        if row["pid"] in tree:
            tree_cpu += rate
            continue
        outside.append({"pid": row["pid"], "command": row["command"],
                        "start": row["start_identity"], "cpu_s_per_s": rate})
    outside.sort(key=lambda item: (-item["cpu_s_per_s"], item["pid"]))
    worst = outside[0] if outside else None
    outside_total = sum(item["cpu_s_per_s"] for item in outside)
    excluded_kernel = (kernel_task_cpu or 0.0) if not include_kernel_task else 0.0
    host = _host_rates(before, after)
    host_busy = host["host_busy_cpu_s_per_s"]
    outside_aggregate = None if host_busy is None else host_busy - tree_cpu - excluded_kernel
    unattributed = (None if host_busy is None
                    else host_busy - tree_cpu - outside_total - excluded_kernel)
    aggregate_over = (aggregate_limit is not None and outside_aggregate is not None
                      and outside_aggregate > aggregate_limit)
    over = [item for item in outside if item["cpu_s_per_s"] > limit]
    result.update(
        elapsed_s=elapsed_s,
        clean=not over and not exited_over and not aggregate_over,
        max_outside=worst,
        outside_over_limit=over + exited_over,
        exited_over_limit=exited_over,
        outside_listed=[item for item in outside if item["cpu_s_per_s"] >= REPORT_FLOOR_CPU_S_PER_S],
        outside_total_cpu_s_per_s=outside_total,
        outside_process_count=len(outside),
        tree_cpu_s_per_s=tree_cpu,
        tree_process_count=len(tree & {r["pid"] for r in union.values()}),
        kernel_task_cpu_s_per_s=kernel_task_cpu,
        kernel_task_included=include_kernel_task,
        **host,
        outside_aggregate_cpu_s_per_s=outside_aggregate,
        unattributed_cpu_s_per_s=unattributed,
        aggregate_limit_s_per_s=aggregate_limit,
        aggregate_over_limit=aggregate_over,
        unaccounted=unaccounted,
        raw=[ref.to_json() for ref in (before.raw, after.raw) if ref is not None],
    )
    if aggregate_limit is not None and host_busy is None:
        result.update(error=f"host CPU unread, so the registered aggregate limit cannot be "
                            f"judged: {host['host_error']}", clean=None)
    return result


def over_limit(result: Mapping[str, Any]) -> dict[tuple[int, str], float]:
    """(pid, start) -> rate of each outside process measured above the limit in
    ``result``: the ``previous_over`` of the next interval."""

    return {(item["pid"], item["start"]): item["cpu_s_per_s"]
            for item in result.get("outside_over_limit") or ()
            if "basis" not in item and item.get("start") is not None}


def _host_rates(before: Snapshot, after: Snapshot) -> dict[str, Any]:
    out: dict[str, Any] = {"host_busy_cpu_s_per_s": None, "host_idle_cpu_s_per_s": None,
                           "host_ticks": None, "host_error": None}
    if before.host is None or after.host is None:
        out["host_error"] = before.host_error or after.host_error or "host CPU not read"
        return out
    elapsed_s = (after.started.monotonic_ns - before.started.monotonic_ns) / 1e9
    try:
        ticks = host_ticks_delta(before.host, after.host)
    except ValueError as exc:
        out["host_error"] = str(exc)
        return out
    if not elapsed_s > 0:
        out["host_error"] = "host reads are not in time order"
        return out
    rate = float(os.sysconf("SC_CLK_TCK"))
    out.update(host_ticks={**ticks, "ticks_per_s": rate, "elapsed_s": elapsed_s},
               host_busy_cpu_s_per_s=ticks["busy_ticks"] / rate / elapsed_s,
               host_idle_cpu_s_per_s=ticks["idle_ticks"] / rate / elapsed_s)
    return out


def _mid(snapshot: Snapshot, field: str) -> int:
    return (getattr(snapshot.started, field) + getattr(snapshot.finished, field)) // 2


# --------------------------------------------------------------------------
# The dwell


class Dwell:
    """Consecutive clean 30 s intervals until ``clean_s`` (READY) or ``cap_s`` (REFUSE)."""

    def __init__(self, thresholds: Mapping[str, Any], *, started_ns: int) -> None:
        self.limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
        self.started_ns = started_ns
        self.intervals: list[dict[str, Any]] = []
        self.clean_since_ns: int | None = None
        self.ready_at_ns: int | None = None

    def add(self, result: Mapping[str, Any]) -> None:
        summary = _summary(result)
        self.intervals.append(summary)
        a, b = result["interval"]["monotonic_ns"]
        if result.get("clean"):
            if self.clean_since_ns is None:
                self.clean_since_ns = a
            if self.ready_at_ns is None and b - self.clean_since_ns >= self.limits["clean_s"] * 1e9:
                self.ready_at_ns = b
        else:
            self.clean_since_ns = None

    @property
    def ready(self) -> bool:
        return self.ready_at_ns is not None

    def clean_run_s(self, now_ns: int | None = None) -> float:
        if self.clean_since_ns is None or not self.intervals:
            return 0.0
        end = self.intervals[-1]["interval"]["monotonic_ns"][1]
        return (end - self.clean_since_ns) / 1e9

    def expired(self, now_ns: int) -> bool:
        return not self.ready and now_ns - self.started_ns >= self.limits["cap_s"] * 1e9

    def measurement(self, *, started: Stamp, finished: Stamp) -> Measurement:
        values = {"intervals": self.intervals, "ready": self.ready,
                  "ready_at_monotonic_ns": self.ready_at_ns,
                  "clean_run_s": self.clean_run_s(), "elapsed_s":
                  (finished.monotonic_ns - self.started_ns) / 1e9,
                  "started_monotonic_ns": self.started_ns}
        error = None
        if self.intervals and all(item["error"] for item in self.intervals):
            error = "every dwell interval failed to measure"
        elif not self.intervals:
            error = "no dwell interval was measured"
        return Measurement(MODULE, "dwell", values, (), started, finished, error)


def _summary(result: Mapping[str, Any]) -> dict[str, Any]:
    keys = ("interval", "error", "clean", "elapsed_s", "max_outside", "outside_over_limit",
            "exited_over_limit", "outside_total_cpu_s_per_s", "outside_process_count",
            "tree_cpu_s_per_s", "kernel_task_cpu_s_per_s", "host_busy_cpu_s_per_s",
            "outside_aggregate_cpu_s_per_s", "unattributed_cpu_s_per_s",
            "aggregate_limit_s_per_s", "aggregate_over_limit", "host_error", "unaccounted",
            "raw")
    return {key: result.get(key) for key in keys}


def run_dwell(ctx: Context, thresholds: Mapping[str, Any], *, tree_roots: Iterable[int],
              on_tick=None, tick_s: float = 1.0,
              host_reader: HostReader | None = read_host_cpu) -> Measurement:
    """The arm dwell: a ps snapshot every ``interval_s``; ``on_tick`` runs every
    ``tick_s`` in between (the arm samples the clock there at 1 Hz).

    Returns the dwell Measurement as soon as it is READY or past ``cap_s``.
    """

    limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
    aggregate = aggregate_limit(limits)
    roots = tuple(tree_roots)
    started = ctx.stamp()
    dwell = Dwell(limits, started_ns=started.monotonic_ns)
    index = 0
    previous = take_snapshot(ctx, raw_name=f"dwell-{index:04d}-ps.txt", compress=True,
                             host_reader=host_reader)
    previous_over: dict[tuple[int, str], float] = {}
    next_snapshot_ns = previous.midpoint_ns + int(limits["interval_s"] * 1e9)
    while True:
        now = ctx.clocks.monotonic_ns()
        if now >= next_snapshot_ns:
            index += 1
            current = take_snapshot(ctx, raw_name=f"dwell-{index:04d}-ps.txt", compress=True,
                                    host_reader=host_reader)
            result = interval(previous, current, tree_roots=roots, include_kernel_task=True,
                              limit=limits["cpu_limit_s_per_s"], previous_over=previous_over,
                              aggregate_limit=aggregate)
            previous_over = over_limit(result)
            dwell.add(result)
            previous = current
            next_snapshot_ns = current.midpoint_ns + int(limits["interval_s"] * 1e9)
            if dwell.ready:
                break
        if dwell.expired(ctx.clocks.monotonic_ns()):
            break
        if on_tick is not None:
            on_tick()
        remaining = (next_snapshot_ns - ctx.clocks.monotonic_ns()) / 1e9
        ctx.clocks.sleep(max(0.0, min(tick_s, remaining)))
    return dwell.measurement(started=started, finished=ctx.stamp())


# --------------------------------------------------------------------------
# Judge


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("contention.judge received another module's measurement")
    if measurement.kind != "dwell":
        raise ValueError("the arm judges contention on a dwell, not a single snapshot")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    values = measurement.values
    intervals = values["intervals"]
    observed = {"intervals": len(intervals), "clean_run_s": values["clean_run_s"],
                "elapsed_s": values["elapsed_s"],
                "unclean_intervals": sum(1 for item in intervals if item["clean"] is False),
                "unmeasured_intervals": sum(1 for item in intervals if item["error"])}
    if values["ready"]:
        return Verdict(MODULE, PASS, (), limits, observed)
    last_dirty = next((item for item in reversed(intervals) if not item["clean"]), None)
    detail = ""
    if last_dirty is not None:
        if last_dirty["error"]:
            detail = f"; last failed interval: {last_dirty['error']}"
        elif last_dirty.get("outside_over_limit"):
            worst = max(last_dirty["outside_over_limit"], key=lambda item: item["cpu_s_per_s"])
            detail = (f"; last dirty interval: {worst['command']} (pid {worst['pid']}) at "
                      f"{worst['cpu_s_per_s']:.3f} CPU-s/s"
                      + (" (exited inside it; previous-interval rate)" if "basis" in worst else ""))
        elif last_dirty.get("aggregate_over_limit"):
            detail = (f"; last dirty interval: host CPU outside the tree "
                      f"{last_dirty['outside_aggregate_cpu_s_per_s']:.3f} CPU-s/s > "
                      f"{last_dirty['aggregate_limit_s_per_s']} CPU-s/s")
    return Verdict(MODULE, REFUSE,
                   (f"no {limits['clean_s']} s run of clean {limits['interval_s']} s intervals "
                    f"within {limits['cap_s']} s{detail}",), limits, observed)


# --------------------------------------------------------------------------
# In-window member join (plan §3.4)


def span_findings(intervals: Sequence[Mapping[str, Any]], request: Mapping[str, Any],
                  thresholds: Mapping[str, Any] = DEFAULT_THRESHOLDS) -> list[dict[str, Any]]:
    """``contention.request_overlap`` and ``contention.unmeasured`` for one request.

    ``request`` is ``{"monotonic_ns": [request_start, request_end]}``; journal
    intervals carry ``interval.monotonic_ns`` [a, b] and exclude kernel_task.
    """

    limit = thresholds["cpu_limit_s_per_s"]
    start, stop = request["monotonic_ns"]
    found = []
    covered: list[tuple[int, int]] = []
    for item in intervals:
        a, b = item["interval"]["monotonic_ns"]
        if b < start or a > stop:
            continue
        if item.get("error"):
            continue
        covered.append((a, b))
        over = [entry for entry in item.get("outside_over_limit") or ()
                if entry["cpu_s_per_s"] > limit]
        if over:
            found.append(finding("contention.request_overlap", span=request, observed=over,
                                 expected=limit, interval=item["interval"],
                                 detail="outside process(es) above "
                                        f"{limit} CPU-s/s during the request: "
                                        + ", ".join(f"{e['command']}({e['pid']}) "
                                                    f"{e['cpu_s_per_s']:.3f}" for e in over),
                                 evidence=item.get("raw") or ()))
    hole = _uncovered(covered, start, stop)
    if hole is not None:
        found.append(finding("contention.unmeasured", span=request, observed=hole, expected=None,
                             detail="no ps interval covers part of the request"))
    return found


def _uncovered(covered: Sequence[tuple[int, int]], start: int, stop: int) -> list[int] | None:
    cursor = start
    for a, b in sorted(covered):
        if a > cursor:
            return [cursor, a]
        cursor = max(cursor, b)
        if cursor >= stop:
            return None
    return [cursor, stop] if cursor < stop else None


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 1437: The ps CPU probe failed (nonzero exit or stderr).
    row("joulewise/arm_readiness_evidence_t0.py", "_maintenance_probe",
        "evidence_author_t0_maintenance_census_underivable", 1),
    # base line 1441: The ps CPU output is malformed.
    row("joulewise/arm_readiness_evidence_t0.py", "_maintenance_probe",
        "evidence_author_t0_maintenance_census_underivable", 2),
    # base line 1443: Maintenance census: a contaminant-pattern process is above 5.0% CPU in either of...
    row("joulewise/arm_readiness_evidence_t0.py", "_maintenance_probe",
        "evidence_author_t0_maintenance_census_underivable", 3),
    # base line 887: the sampler output has the per-process rows with a boolean observer flag
    row("joulewise/night_gate.py", "non_observer_consumers",
        "night_probe_error (non_observer_consumers: observation not an object / no metrics / no top_consumers / malformed consumer; lines 887,890,893,904)", 1),
    # base line 1826: the per-process CPU sampler raised
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (non-observer interval observation failed)", 1),
    # base line 1832: the sampler reports its interval length
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (non-observer observation carries no interval_s)", 1),
    # base line 1836: 30 s per-process CPU interval sample; refuses if any process outside the gate's o...
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_not_quiet (non-observer process busy >= T0_NON_OBSERVER_SHARE_MAX 0.5 cores)", 1),
    # base line 12: ps returned rows.
    row("joulewise/prewindow.py", "busy_contaminants",
        "ValueError empty process census (becomes BLOCK at L64)", 1),
    # base line 19: Each ps row has pid, pcpu and args.
    row("joulewise/prewindow.py", "busy_contaminants",
        "ValueError invalid process census row (becomes BLOCK)", 1),
    # base line 22: pcpu is finite and >= 0.
    row("joulewise/prewindow.py", "busy_contaminants",
        "ValueError invalid process CPU (becomes BLOCK)", 1),
    # base line 59: A process whose args match the CONTAMINANTS regex is above 5.0% CPU.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK background daemon active", 1),
    # base line 64: ps census ran and parsed.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK maintenance CPU probe failed", 1),
    # base line 146: Within timeout_s (<=2700 s), a run of clean 30 s samples spanning >=600 s on time...
    row("joulewise/prewindow.py", "t0_wait",
        "return 1 TIMED OUT without 600 s continuous clean time", 1),
    # base line 861: prewindow.py --t0-wait exit 1: no 600 s continuous clean dwell within 45 min (con...
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "evidence_author_t0_capture_command_failed (prewindow-check nonzero)", 1),
    # base line 90: ps aux %CPU of processes matching the XProtect|mds_stores|...|mediaanalysisd rege...
    row("scripts/prewindow_check.sh", "check_once",
        "BLOCK background daemon active (named daemon >5% CPU)", 1),
    # base line 181: Aggregate of the check_once domains.
    row("scripts/prewindow_check.sh", "check_once",
        "exit 1 NOT READY (single-shot)", 1),
    # base line 222: Within the timeout, 600 s of consecutive clean 30 s samples.
    row("scripts/prewindow_check.sh", "check_once",
        "exit 1 TIMED OUT without 600 s continuous clean time", 1),
    # base line 2767: The quiet-binding observer's own job queue (32 jobs) has room to start another ce...
    row("scripts/run_night.py", "_BindTask.__init__",
        "ProbeError 'binding launch queue saturated' / 3002 'binding job limit reached' -> night_probe_error", 1),
    # base line 2826: Each observer worker returns one well-formed framed JSON result of at most 256 KiB.
    row("scripts/run_night.py", "_BindTask.result",
        "ProbeError(envelope error) via _BindTask.result: 'premature EOF', 'binding payload length exceeds cap', 'malformed binding frame', 'pipe read failed' (2789-2812), 2824 'binding result is not published' -> night_probe_error", 1),
    # base line 3070: The run of consecutive quiet CPU samples (quiet_admission.is_quiet, busy cores) c...
    row("scripts/run_night.py", "bind_until_quiet",
        "night_refused_bind_expired 'bind deadline expired'", 1),
    # base line 3160: The sampler observation is well formed and carries a boot identity.
    row("scripts/run_night.py", "bind_until_quiet",
        "ProbeError 'boot_identity_unavailable: ...' / quiet_admission.validate_observation errors (3157) -> night_probe_error", 1),
    # base line 3204: A catch-all: any exception in the bind loop refuses.
    row("scripts/run_night.py", "bind_until_quiet",
        "night_probe_error 'binding observation failed: <exception>'", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 1085: The maintenance census observation_status is PASS (background maintenance quiet).
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.background_quiet.v1", 1),
    # base line 1116: The prewindow-check-wait status is READY, current, same plan and same roots.
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.machine_readiness.v1", 1),
    # base line 7046: The maintenance-census receipt says observation_status PASS plus closed_operator_...
    row("joulewise/arm_readiness.py", "_predicate_passes",
        "readiness_dependency_refused (row t0.background_quiet)", 1),
    # base line 7168: The MACHINE_PREFLIGHT receipt says status READY, current, same plan, same roots,...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_machine_preflight_refused (row t0.machine_readiness)", 1),
    # base line 1398: The prewindow dwell capture exited nonzero (no clean 600 s before its 45-minute t...
    row("joulewise/arm_readiness_evidence_t0.py", "_prewindow_capture",
        "evidence_author_t0_{maintenance_census|machine_preflight}_underivable", 1),
    # base line 1402: The dwell capture lasted under 600 s of monotonic time.
    row("joulewise/arm_readiness_evidence_t0.py", "_prewindow_capture",
        "evidence_author_t0_<kind>_underivable", 1),
    # base line 1404: Dwell validator: the transcript's final clean-dwell suffix does not end in READY...
    row("joulewise/arm_readiness_evidence_t0.py", "_prewindow_capture",
        "evidence_author_t0_<kind>_underivable", 2),
    # base line 1499: The quiet_mac_prep.sh capture exited nonzero.
    row("joulewise/arm_readiness_evidence_t0.py", "_quiet_capture",
        "evidence_author_t0_machine_preflight_underivable", 1),
    # base line 1509: The quiet-Mac transcript has a FAIL: line or lacks the OK: strings for passwordle...
    row("joulewise/arm_readiness_evidence_t0.py", "_quiet_capture",
        "evidence_author_t0_machine_preflight_underivable", 2),
    # base line 8: Transcript has no timeout line.
    row("joulewise/dwell.py", "final_clean_dwell",
        "final_clean_dwell False: 'TIMED OUT' in transcript", 1),
    # base line 12: Transcript has a clean-run start marker.
    row("joulewise/dwell.py", "final_clean_dwell",
        "final_clean_dwell False: no 'continuous clean dwell 0/600s (check 1)' marker", 1),
    # base line 15: Final clean run has no dirty sample.
    row("joulewise/dwell.py", "final_clean_dwell",
        "final_clean_dwell False: BLOCK or 'not ready' after last start", 1),
    # base line 18: Sample lines exist with goal 600.
    row("joulewise/dwell.py", "final_clean_dwell",
        "final_clean_dwell False: no samples or goal != 600", 1),
    # base line 21: Shape and monotonicity of the final clean run in text.
    row("joulewise/dwell.py", "final_clean_dwell",
        "final_clean_dwell False: checks not 1..n, elapsed not sorted, last <600, or last line not 'READY after N min.'", 1),
    # base line 1640: defaults read exit 0 and an integer output
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (screensaver probe failed / output malformed; 1640,1642; v4 arm path)", 1),
    # base line 1643: `defaults -currentHost read com.apple.screensaver idleTime` must read exactly '0'...
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_hid_idle", 1),
    # base line 1727: sysctl vm.loadavg exit 0 and output matches '{ a b c }'
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (load average output malformed)", 1),
    # base line 1733: 1-minute host-wide load average from sysctl vm.loadavg must be <= 2.0 at t0 (lega...
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_not_quiet (load_average predicate, LOAD_MAX 2.0)", 1),
    # base line 1799: /usr/bin/log show: counts launchd 'Successfully spawned corecaptured' lines in th...
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_not_quiet (corecaptured: > SPAWNS_MAX=2 launchd spawns in last 10 min)", 1),
    # base line 509: ioreg HID output has HIDIdleTime
    row("joulewise/t0_rehearsal.py", "parse_hid_idle_time",
        "ValueError HIDIdleTime output is absent", 1),
    # base line 512: exactly one HIDIdleTime line
    row("joulewise/t0_rehearsal.py", "parse_hid_idle_time",
        "ValueError HIDIdleTime output is ambiguous", 1),
    # base line 513: HIDIdleTime line is decimal
    row("joulewise/t0_rehearsal.py", "parse_hid_idle_time",
        "ValueError HIDIdleTime output is unparsable", 1),
    # base line 869: hid_idle record present
    row("joulewise/t0_rehearsal.py", "evaluate_g3",
        "G3 FAIL HIDIdleTime output is absent", 1),
    # base line 885: no local keyboard/mouse input during the T-0 span
    row("joulewise/t0_rehearsal.py", "evaluate_g3",
        "G3 FAIL HIDIdleTime below measured T-0 span", 1),
    # base line 659: quiet_mac_prep.sh stdout has no 'FAIL:' anywhere and contains three OK lines: pas...
    row("scripts/capture_t0_step.py", "_validate_result",
        "evidence_author_t0_capture_result_invalid (E-7a FAIL or missing quiet-Mac predicate)", 1),
    # base line 665: dwell.final_clean_dwell replays the prewindow transcript text.
    row("scripts/capture_t0_step.py", "_validate_result",
        "evidence_author_t0_capture_result_invalid (E-7b not READY)", 1),
    # base line 869: Wall duration of the prewindow command is >=600 s.
    row("scripts/capture_t0_step.py", "_capture_step_with_dependencies",
        "evidence_author_t0_capture_result_invalid (E-7b returned before 600 s)", 1),
    # base line 101: uptime 1-min load <= 2.0.
    row("scripts/prewindow_check.sh", "check_once",
        "BLOCK 1-minute load average exceeds 2.0", 1),
    # base line 3585: Re-reads clean_dwell.json: exit 0, not timed out, no error.
    row("scripts/run_night.py", "_write_start_conditions",
        "ValueError at 3618: 'clean dwell not admitted'", 1),
    # base line 3687: prewindow_check.sh --wait reports 600 s continuous clean. Each 30 s check covers:...
    row("scripts/run_night.py", "_admit_derivation_clean_dwell",
        "ValueError 'clean dwell timed out at derivation start deadline' / 'clean dwell could not run' / 'clean dwell refused (exit N)'", 1),
    # base line 3709: Re-reads the T-0 prewindow-check.json capture: step id, exit 0, elapsed at least...
    row("scripts/run_night.py", "_admit_qualification_clean_dwell",
        "PackNightRefusal 'qualification clean dwell cap or start budget' (exit_code/step_id/elapsed >= 600 s part)", 1),
)
