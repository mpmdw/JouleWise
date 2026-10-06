"""The continuous in-window sampler (plan §2.1) and its member join (§3.4).

The driver starts the monitor after the arm decision and before the chain,
through :class:`Supervisor`, which runs ``scripts/hazard_monitor.py`` in its
own process group under ``taskpolicy -b`` (background priority, efficiency
cores).  The driver's one-second supervision loop calls
:meth:`Supervisor.poll`, which restarts a dead monitor and records the gap;
:meth:`Supervisor.stop` runs after the chain's process group is proven gone.

The monitor writes one JSON-lines journal per module under
``<custody>/hazards/monitor/`` plus ``monitor.jsonl`` (its own pids and CPU
time) and ``supervisor.jsonl`` (starts, deaths, restarts and gaps, written by
the driver side).  Each line is written to the kernel at once (``os.write``),
so a reader and a monitor crash see it immediately; the monitor's journals
fsync at most every ``FSYNC_INTERVAL_S`` and at close (PLAN2 t3-8: one fsync a
second on the clock journal was most of its disk wake-ups), so only a power
loss can drop the last few seconds.  Cadence (plan §2.3):

=========== ======== ==================================================
journal     every    reading
=========== ======== ==================================================
clock       1 s      anchor (REALTIME - MONOTONIC_RAW); f every 5 s
battery     5 s      poll of the grammar's six fields in process
                     (``battery.RegistryReader``); ``ioreg`` whenever one
                     of them changes (each 60 s gauge publication, read
                     within 5 s), at least every 90 s, and whenever the
                     poll fails; raw bytes kept whenever UpdateTime or a
                     polled field changes.  Without the reader (or after a
                     failed poll): ``ioreg`` ~2 s after each publication,
                     retried every 5 s while one is late, at most 30 s apart
battery     1 s      SMC battery current B0AC (and B0AV, PDTR, PSTR, PPBR)
                     read in process (``smc.Reader``), one ``reading`` line
                     each with ``values.source = "smc"``; each ``ioreg``
                     line also carries the SMC read taken with it
thermal     5 s      OS thermal pressure level (notify_get_state in process;
                     notifyutil when that fails)
contention  10 s     ps interval, CPU-s/s outside the tree, host CPU ticks
                     (in process); raw ps (gzip)
disk        60 s     statvfs; ``disk.low`` marker below 10 GiB
monitor     30 s     own pid, pgid, CPU time of itself and its children,
                     battery poll and ``ioreg`` counts
=========== ======== ==================================================

Every line carries ``started`` and ``finished`` stamps, each with the three
clocks (wall, ``time.monotonic_ns``, MONOTONIC_RAW), so a harvest joins it
exactly to a member's sampler stream.  :func:`member_findings` is that join.

Cost.  The monitor's CPU lands inside every member's package energy, so it is
kept small (tests/hazards/test_monitor.py measures it on a desk run).  On
10-06, under ``taskpolicy -b``, one ``ps -Ao`` child cost 22-36 ms of CPU on a
quiet desk and 55-67 ms with other work running (load average 2-3.5), one
``ioreg`` child 43-53 ms and 70-85 ms; everything read in process (clock,
frequency word, host ticks, thermal level, battery poll, statvfs) costs well
under 1 ms.  ``ps`` every 10 s is therefore most of the cost, and it cannot be
replaced in process: it is setuid root, and an unprivileged ``proc_pidinfo``
cannot read another user's CPU time (EPERM), which is where the contaminants
live; its kernel time does not shrink with fewer columns (``ps -Ao pid`` costs
the same).  Every task runs on the 1 s grid of the clock journal.  In
production the in-process samplers run on a second thread (:meth:`Monitor.run`),
and both threads sleep in steps of at most 0.25 s so a stop signal is seen
promptly; a wake-up with nothing due costs microseconds.
"""

from __future__ import annotations

import dataclasses
import json
import os
import resource
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.hazards import battery, clock, contention, disk, smc, thermal
from joulewise.hazards.base import (
    Context, Stamp, canonical_json, sha256_hex, write_create_once,
)

CONFIG_SCHEMA = "joulewise.hazard_monitor_config.v1"
JOURNAL_SCHEMA = "joulewise.hazard_journal.v1"
SUPERVISOR_SCHEMA = "joulewise.hazard_monitor_supervisor.v1"
JOURNALS = ("clock", "battery", "thermal", "contention", "disk", "monitor")
DISK_LOW_MARKER = "disk.low"
REPO_ROOT = Path(__file__).resolve().parents[2]
MONITOR_SCRIPT = REPO_ROOT / "scripts" / "hazard_monitor.py"
TASKPOLICY_PREFIX = ("/usr/sbin/taskpolicy", "-b")
# PLAN2 t3-8: the monitor's journals batch their fsyncs; 0 is one fsync per line.
FSYNC_INTERVAL_S = 5.0

# battery_s: the poll (and the ioreg retry without the reader); battery_max_s:
# the longest gap between ioreg reads without the reader; battery_full_max_s:
# the longest gap between ioreg reads with it, longer than one publication
# period plus one poll so it never fires while the gauge publishes.
DEFAULT_CADENCE: dict[str, float] = {"clock_s": 1.0, "frequency_s": 5.0, "battery_s": 5.0,
                                     "battery_smc_s": 1.0,
                                     "battery_max_s": 30.0, "battery_publication_s": 60.0,
                                     "battery_full_max_s": 90.0,
                                     "thermal_s": 5.0, "contention_s": 10.0, "disk_s": 60.0,
                                     "self_s": 30.0}
# In production the in-process samplers run on their own thread (Monitor.run):
# the clock, the 1 s SMC battery current (about 75 us in process) and the
# thermal level.  The subprocess probes (ioreg, ps) and the rest run on the
# main thread.  Together the two tuples name every task in ``Monitor.due``.
FAST_TASKS = ("clock", "battery_smc", "thermal")
SLOW_TASKS = ("battery", "contention", "disk", "self")


def build_config(*, custody_dir: Path | str, tree_roots: Sequence[int],
                 disk_targets: Sequence[Mapping[str, Any]], low_bytes: int = disk.DEFAULT_THRESHOLDS["low_bytes"],
                 cpu_limit_s_per_s: float = contention.DEFAULT_THRESHOLDS["cpu_limit_s_per_s"],
                 cadence: Mapping[str, float] | None = None,
                 tree_root_files: Sequence[str] = ()) -> dict[str, Any]:
    """The monitor's whole input; the driver writes it once as ``monitor/config.json``.

    ``tree_root_files`` (PLAN2 row 10) name JSON files whose ``pgid`` becomes a
    further tree root once the file appears: the driver passes the chain's
    ``night/chain.started``, so the chain's process tree stays inside the
    measurement tree even if the driver dies and the chain is reparented.
    """

    merged = dict(DEFAULT_CADENCE)
    merged.update(cadence or {})
    config = {"schema": CONFIG_SCHEMA, "custody_dir": str(custody_dir),
              "tree_roots": [int(pid) for pid in tree_roots],
              "disk_targets": [dict(item) for item in disk_targets], "low_bytes": int(low_bytes),
              "cpu_limit_s_per_s": float(cpu_limit_s_per_s), "cadence": merged}
    if tree_root_files:
        config["tree_root_files"] = [str(path) for path in tree_root_files]
    return config


def validate_config(config: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(config, Mapping) or config.get("schema") != CONFIG_SCHEMA:
        raise ValueError("monitor config schema is not " + CONFIG_SCHEMA)
    required = {"custody_dir", "tree_roots", "disk_targets", "low_bytes", "cpu_limit_s_per_s",
                "cadence"}
    missing = required - set(config)
    if missing:
        raise ValueError(f"monitor config lacks {sorted(missing)}")
    if not config["tree_roots"] or any(type(pid) is not int or pid <= 0
                                       for pid in config["tree_roots"]):
        raise ValueError("monitor config tree_roots must be positive pids")
    for key in DEFAULT_CADENCE:
        value = config["cadence"].get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"monitor cadence {key} must be positive")
    files = config.get("tree_root_files", [])
    if not isinstance(files, list) or not all(isinstance(item, str) and Path(item).is_absolute()
                                              for item in files):
        raise ValueError("monitor config tree_root_files must be a list of absolute paths")
    return dict(config)


def monitor_dir(custody_dir: Path | str) -> Path:
    return Path(custody_dir) / "hazards" / "monitor"


# --------------------------------------------------------------------------
# Journals


class Journal:
    """Append-only JSON lines; ``os.write`` per line, an fsync at most every
    ``fsync_interval_s`` (0: every line) and at close."""

    def __init__(self, path: Path, *, fsync_interval_s: float = 0.0) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        self.fsync_interval_s = float(fsync_interval_s)
        self._synced_at = time.monotonic()
        self._dirty = False

    def write(self, record: Mapping[str, Any]) -> None:
        line = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False,
                          default=str) + "\n"
        os.write(self._fd, line.encode())
        self._dirty = True
        now = time.monotonic()
        if self.fsync_interval_s <= 0 or now - self._synced_at >= self.fsync_interval_s:
            os.fsync(self._fd)
            self._synced_at, self._dirty = now, False

    def close(self) -> None:
        if self._fd >= 0:
            try:
                if self._dirty:
                    os.fsync(self._fd)
            finally:
                os.close(self._fd)
                self._fd = -1
                self._dirty = False


def read_journal(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    """All complete lines, plus a note when the last line is truncated (a death mid-write)."""

    path = Path(path)
    if not path.exists():
        return [], None
    data = path.read_bytes()
    lines = data.split(b"\n")
    tail = lines.pop()  # empty when the file ends with a newline
    out = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            return out, f"line {number} is not JSON"
    return out, (f"truncated final line of {len(tail)} bytes" if tail.strip() else None)


def load_journals(custody_dir: Path | str) -> dict[str, list[dict[str, Any]]]:
    directory = monitor_dir(custody_dir)
    return {name: read_journal(directory / f"{name}.jsonl")[0] for name in JOURNALS}


# --------------------------------------------------------------------------
# The monitor process


class Monitor:
    """Samples every module on its cadence until stopped.  All hardware is reached
    through ``ctx`` (and ``frequency_reader``/``statvfs``), so tests drive it with fakes."""

    def __init__(self, config: Mapping[str, Any], *, ctx: Context | None = None,
                 frequency_reader: Callable[[], Mapping[str, Any]] = clock.read_frequency,
                 statvfs: Callable[[str], Any] = os.statvfs, stat: Callable[[str], Any] = os.stat,
                 notify_reader: Any = None, battery_reader: Any = None, smc_reader: Any = None,
                 host_reader: contention.HostReader | None = contention.read_host_cpu) -> None:
        self.config = validate_config(config)
        self.custody = Path(self.config["custody_dir"])
        self.directory = monitor_dir(self.custody)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.ctx = ctx or Context()
        self.frequency_reader = frequency_reader
        self.statvfs, self.stat = statvfs, stat
        self.notify_reader = notify_reader  # None: read the level through notifyutil
        # None: ioreg on the publication schedule; else polled every battery_s
        # (``battery.RegistryReader`` in production) and ioreg on a change.
        self.battery_reader = battery_reader
        self.battery_poll_at_read: dict[str, Any] | None = None  # the poll before the last good ioreg
        self.battery_read_ns: int | None = None                  # when that ioreg finished
        # None: no SMC lines (the battery current falls back to the registry,
        # disclosed at the join); else ``smc.Reader`` (production), read every
        # battery_smc_s.
        self.smc_reader = smc_reader
        self.counts = {"battery_polls": 0, "battery_poll_failures": 0, "battery_ioreg_reads": 0,
                       "smc_reads": 0}
        self.host_reader = host_reader
        self.cadence = self.config["cadence"]
        self.tree_roots = tuple(self.config["tree_roots"])
        self.stopping = False
        first = self.ctx.stamp()
        self.session = f"{os.getpid()}-{first.monotonic_ns}"
        self.journals = {name: Journal(self.directory / f"{name}.jsonl", fsync_interval_s=FSYNC_INTERVAL_S)
                         for name in JOURNALS}
        self.tree_root_files = {str(path): None for path in self.config.get("tree_root_files", [])}
        self.seq = {name: 0 for name in JOURNALS}
        self.due = {name: first.monotonic_ns for name in ("clock", "battery_smc", "battery",
                                                          "thermal", "contention", "disk", "self")}
        self.next_frequency_ns = first.monotonic_ns
        self.last_update_time: int | None = None
        self.previous_snapshot: contention.Snapshot | None = None
        self.previous_over: dict[tuple[int, str], float] = {}
        self.disk_low_written = (self.directory / DISK_LOW_MARKER).exists()
        self.started = first
        self._raw_index = 0
        self._write_lock = threading.Lock()
        # smc.Reader is not thread-safe (it opens and drops its IOKit user client
        # lazily); the fast thread's 1 s read and the ioreg line's read share it.
        self._smc_lock = threading.Lock()

    # -- lines --------------------------------------------------------------

    def _write(self, name: str, kind: str, *, started: Stamp | Mapping[str, Any] | None = None,
               finished: Stamp | Mapping[str, Any] | None = None, values: Any = None,
               error: str | None = None, raw: Sequence[Mapping[str, Any]] = ()) -> None:
        with self._write_lock:  # both sampler threads write the ``battery`` and ``monitor`` journals
            self.seq[name] += 1
            stamp = None if started is not None and finished is not None else self.ctx.stamp()
            self.journals[name].write({
                "schema": JOURNAL_SCHEMA, "module": name, "session": self.session,
                "seq": self.seq[name], "kind": kind,
                "started": _stamp_json(started) or stamp.to_json(),
                "finished": _stamp_json(finished) or stamp.to_json(),
                "values": values, "error": error, "raw": list(raw)})

    def _raw_context(self, module: str) -> Context:
        self._raw_index += 1
        return dataclasses.replace(self.ctx, raw_dir=self.directory / "raw" / module,
                                   custody_root=self.custody,
                                   label=f"{self.session}-{self._raw_index:07d}")

    # -- lifecycle ------------------------------------------------------------

    def open_session(self, argv: Sequence[str] = ()) -> None:
        for name in JOURNALS:
            self._write(name, "session_start", values={
                "pid": os.getpid(), "pgid": os.getpgrp(), "ppid": os.getppid(),
                "argv": list(argv), "config_sha256": sha256_hex(canonical_json(self.config)),
                "tree_roots": list(self.tree_roots), "cadence": dict(self.cadence)})

    def close_session(self, reason: str) -> None:
        self._self_cost()
        for name in JOURNALS:
            self._write(name, "session_end", values={"reason": reason})
        for journal in self.journals.values():
            journal.close()

    def run(self, *, max_seconds: float | None = None, fast_thread: bool = False) -> None:
        """Loop until ``stopping`` (set by a signal) or ``max_seconds`` elapse.

        ``fast_thread`` (production, :func:`run_forever`): the clock (1 s), SMC
        battery current (1 s) and thermal (5 s) samplers, which read in
        process, run on their own thread (:data:`FAST_TASKS`),
        so a slow subprocess probe (``ioreg`` for the battery, ``ps`` for
        contention, each bounded only by its own timeout) can no longer hole
        their journals. The real-model rehearsal of 2026-10-06 saw a ``ps``
        timeout (10 s) followed by a 16 s ``ioreg`` stall the single loop for
        35 s, which the harvest disclosed as ``clock.unmeasured`` and
        ``thermal.unmeasured`` on a member. Tests on a simulated timeline keep
        the single loop (the default).
        """

        deadline = None if max_seconds is None else self.started.monotonic_ns + int(max_seconds * 1e9)
        if not fast_thread:
            self._loop(None, deadline)
            return
        fast = threading.Thread(target=self._loop, args=(FAST_TASKS, deadline),
                                name="hazard-monitor-fast", daemon=True)
        fast.start()
        try:
            self._loop(SLOW_TASKS, deadline)
        finally:
            self.stopping = True
            fast.join()

    def _loop(self, names: Sequence[str] | None, deadline: int | None) -> None:
        keys = list(self.due) if names is None else list(names)
        while not self.stopping:
            now = self.ctx.clocks.monotonic_ns()
            if deadline is not None and now >= deadline:
                break
            self.tick(now, names)
            next_due = min(self.due[name] for name in keys)
            pause = (next_due - self.ctx.clocks.monotonic_ns()) / 1e9
            if deadline is not None:
                pause = min(pause, (deadline - self.ctx.clocks.monotonic_ns()) / 1e9)
            if pause > 0 and not self.stopping:
                # A signal sets ``stopping`` on the main thread; sleep in short
                # steps so the other loop notices within a quarter second.
                self.ctx.clocks.sleep(min(pause, 0.25) if names is not None else pause)

    def tick(self, now_ns: int, names: Sequence[str] | None = None) -> None:
        for name, task in (("clock", self._clock), ("battery_smc", self._battery_smc),
                           ("battery", self._battery),
                           ("thermal", self._thermal), ("contention", self._contention),
                           ("disk", self._disk), ("self", self._self_cost)):
            if self.stopping:
                return
            if names is not None and name not in names:
                continue
            if now_ns >= self.due[name]:
                period_ns = int(self.cadence[f"{name}_s"] * 1e9)  # battery re-plans itself
                # Fixed-rate schedule; after a stall longer than a period, resume from now.
                self.due[name] += period_ns
                if self.due[name] <= now_ns:
                    self.due[name] = now_ns + period_ns
                try:
                    task()
                except Exception as exc:  # a failed probe is a journaled error, never a stop
                    self._write("monitor", "event", values={"task": name},
                                error=f"{type(exc).__name__}: {exc}")

    # -- tasks ----------------------------------------------------------------

    def _clock(self) -> None:
        now = self.ctx.clocks.monotonic_ns()
        reader = None
        if now >= self.next_frequency_ns:
            reader = self.frequency_reader
            self.next_frequency_ns = now + int(self.cadence["frequency_s"] * 1e9)
        item = clock.sample(self.ctx, frequency_reader=reader)
        self._write("clock", "reading", started=item["started"], finished=item["finished"],
                    values={"anchor": item["anchor"], "frequency": item["frequency"]},
                    error=item["error"])

    def _smc_read(self) -> Mapping[str, Any]:
        with self._smc_lock:
            return self.smc_reader.read()

    def _battery_smc(self) -> None:
        """The 1 s SMC read of the battery current, journaled whatever it returned."""

        if self.smc_reader is None:
            return
        self.counts["smc_reads"] += 1
        started = self.ctx.stamp()
        sample = battery.smc_sample(self._smc_read)
        finished = self.ctx.stamp()
        _current, why = battery.smc_current(sample)
        self._write("battery", "reading", started=started, finished=finished,
                    values={"source": "smc", "smc": sample}, error=why)

    def _battery(self) -> None:
        """The 5 s battery task: an in-process poll, and ``ioreg`` when it changed.

        Without a reader, ``ioreg`` on the publication schedule
        (:meth:`_next_battery_poll`).  With one, the poll runs on the fixed 5 s
        grid and ``ioreg`` runs when a polled field differs from the poll taken
        before the last good ``ioreg`` (a publication, or a state change between
        publications), when no good ``ioreg`` finished within
        ``battery_full_max_s``, or when the poll fails.  A failed poll falls back
        to the publication schedule until the next poll succeeds, so a broken
        reader never turns into an ``ioreg`` every 5 s.  An unchanged poll
        writes no line: the reading in force is the last ``ioreg`` line, and the
        ``monitor`` journal's cost lines count the polls.
        """

        if self.battery_reader is None:
            self._battery_ioreg(None, schedule=True)
            return
        self.counts["battery_polls"] += 1
        started = self.ctx.stamp()
        try:
            poll = dict(self.battery_reader.read())
            if type(poll.get("UpdateTime")) is not int:
                raise ValueError(f"UpdateTime is {poll.get('UpdateTime')!r}, not an integer")
            error = None
        except Exception as exc:  # any reader failure: ioreg now, on its own schedule
            poll, error = None, f"{type(exc).__name__}: {exc}"
        finished = self.ctx.stamp()
        trigger: dict[str, Any] = {"poll": poll, "poll_started": started.to_json(),
                                   "poll_finished": finished.to_json()}
        if error is not None:
            self.counts["battery_poll_failures"] += 1
            self._battery_ioreg({**trigger, "reason": "poll failed", "poll_error": error},
                                schedule=True)
            return
        previous = self.battery_poll_at_read
        if previous is None:
            reason = "first read"
        elif poll != previous:
            reason = "changed: " + ", ".join(sorted(key for key in set(poll) | set(previous)
                                                    if poll.get(key) != previous.get(key)))
        elif (self.battery_read_ns is None or finished.monotonic_ns - self.battery_read_ns
              >= int(self.cadence["battery_full_max_s"] * 1e9)):
            reason = f"no ioreg read for {self.cadence['battery_full_max_s']:g} s"
        else:
            return
        if self._battery_ioreg({**trigger, "reason": reason}, schedule=False):
            self.battery_poll_at_read = poll

    def _battery_ioreg(self, trigger: Mapping[str, Any] | None, *, schedule: bool) -> bool:
        """One ``ioreg`` read through the frozen grammar, journaled; True when good.

        Raw bytes are kept when the read failed, when UpdateTime changed, or
        when a polled field changed (``trigger``).  ``schedule`` re-plans the
        next battery task on the publication schedule.
        """

        self.counts["battery_ioreg_reads"] += 1
        started = self.ctx.stamp()
        completed = self.ctx.run(battery.IOREG_BATTERY_ARGV, battery.PROBE_TIMEOUT_S)
        finished = self.ctx.stamp()
        error = None
        values: dict[str, Any] = {"returncode": completed.returncode}
        if trigger is not None:
            values["trigger"] = dict(trigger)
        if self.smc_reader is not None:  # B0AC beside the registry's InstantAmperage
            values["smc"] = battery.smc_sample(self._smc_read, self.ctx)
        raw: list[dict[str, Any]] = []
        stamp_update = None
        if not completed.ok:
            error = (completed.error or ("ioreg timed out" if completed.timed_out
                                         else f"ioreg exit code {completed.returncode}"))
        else:
            stamp_update = battery.update_time(completed.stdout)
            try:
                values.update(battery.parse_reading(completed.stdout, started.wall_ns / 1e9))
            except ValueError as exc:  # battery.ProbeError is a ValueError
                error = f"ioreg bytes refused by the BFG grammar: {exc}"
            changed = trigger is not None and str(trigger.get("reason", "")).startswith("changed")
            if error is not None or stamp_update != self.last_update_time or changed:
                ref = self._raw_context("battery").keep_raw("battery.ioreg", completed.stdout)
                raw.append(ref.to_json())
                values["publication"] = error is None
            if error is None:
                self.last_update_time = stamp_update
                self.battery_read_ns = finished.monotonic_ns
        self._write("battery", "reading", started=started, finished=finished, values=values,
                    error=error, raw=raw)
        if schedule:
            self.due["battery"] = self._next_battery_poll(finished, None if error else stamp_update)
        return error is None

    def _next_battery_poll(self, finished: Stamp, update_time_s: int | None) -> int:
        """Poll just after the gauge's next publication, never more than ``battery_max_s`` apart.

        The gauge publishes on a fixed 60 s grid (UpdateTime = 21 mod 60 on
        every archived and live read) and every ioreg field, the accumulators
        included, is frozen between publications (16 reads 5 s apart on 10-05
        changed only when UpdateTime did).  A fixed 5 s poll re-read identical
        bytes 11 times in 12 and tripled the monitor's CPU; this schedule reads
        each publication about 2 s after it appears, retries every
        ``battery_s`` while one is late, and adds one mid-cycle read so an
        off-grid publication is not missed.
        """

        now = finished.monotonic_ns
        retry = int(self.cadence["battery_s"] * 1e9)
        longest = int(self.cadence["battery_max_s"] * 1e9)
        if update_time_s is None:
            return now + retry
        expected_wall_ns = int((update_time_s + self.cadence["battery_publication_s"] + 2) * 1e9)
        expected = now + (expected_wall_ns - finished.wall_ns)
        target = expected if expected > now else now + retry
        return min(max(target, now + retry), now + longest)

    def _thermal(self) -> None:
        if self.notify_reader is not None:
            started = self.ctx.stamp()
            try:
                level, error = self.notify_reader.read(), None
            except OSError as exc:
                level, error = None, f"notify_get_state failed: {exc}"
            finished = self.ctx.stamp()
            if error is None:
                self._write("thermal", "reading", started=started, finished=finished,
                            values={"level": level, "source": "notify_get_state"}, error=None)
                return
        measurement = thermal.measure(self.ctx)
        self._write("thermal", "reading", started=measurement.started,
                    finished=measurement.finished,
                    values={"level": measurement.values.get("level"), "source": "notifyutil"},
                    error=measurement.error)

    def _resolve_tree_roots(self) -> None:
        """Add the pgid of each ``tree_root_files`` entry once it exists (PLAN2 row 10)."""

        for path, resolved in self.tree_root_files.items():
            if resolved is not None:
                continue
            try:
                pgid = json.loads(Path(path).read_bytes()).get("pgid")
            except (OSError, ValueError, AttributeError):
                continue
            if type(pgid) is not int or pgid <= 1:
                continue
            self.tree_root_files[path] = pgid
            if pgid not in self.tree_roots:
                self.tree_roots = (*self.tree_roots, pgid)
            self._write("monitor", "event", values={"task": "tree_root", "pgid": pgid, "source": path,
                                                    "tree_roots": list(self.tree_roots)})

    def _contention(self) -> None:
        if self.tree_root_files:
            self._resolve_tree_roots()
        snapshot = contention.take_snapshot(self._raw_context("contention"), compress=True,
                                            host_reader=self.host_reader)
        previous, self.previous_snapshot = self.previous_snapshot, snapshot
        if previous is None:
            self._write("contention", "snapshot", started=snapshot.started,
                        finished=snapshot.finished, values=None, error=snapshot.error,
                        raw=[snapshot.raw.to_json()] if snapshot.raw else [])
            return
        # In the window the host aggregate is journaled, never judged (contention docstring).
        result = contention.interval(previous, snapshot, tree_roots=self.tree_roots,
                                     include_kernel_task=False,
                                     limit=self.config["cpu_limit_s_per_s"],
                                     previous_over=self.previous_over)
        self.previous_over = contention.over_limit(result)
        error = result.pop("error")
        self._write("contention", "interval", started=previous.started, finished=snapshot.finished,
                    values=result, error=error, raw=result.get("raw") or ())

    def _disk(self) -> None:
        measurement = disk.measure(self.ctx, targets=self.config["disk_targets"],
                                   statvfs=self.statvfs, stat=self.stat)
        low = disk.low(measurement, self.config["low_bytes"])
        self._write("disk", "reading", started=measurement.started, finished=measurement.finished,
                    values={"targets": measurement.values["targets"], "low": low},
                    error=measurement.error)
        if low and not self.disk_low_written:
            marker = self.directory / DISK_LOW_MARKER
            try:
                write_create_once(marker, canonical_json(
                    {"code": "disk.low", "low": low, "stamp": measurement.finished.to_json(),
                     "session": self.session}) + b"\n")
            except FileExistsError:
                pass
            self.disk_low_written = True
            self._write("disk", "event", values={"code": "disk.low", "low": low,
                                                 "marker": str(marker)})

    def _self_cost(self) -> None:
        own = resource.getrusage(resource.RUSAGE_SELF)
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        self._write("monitor", "cost", values={
            "pid": os.getpid(), "pgid": os.getpgrp(),
            "cpu_self_s": own.ru_utime + own.ru_stime,
            "cpu_children_s": children.ru_utime + children.ru_stime,
            "maxrss": own.ru_maxrss, "battery_reader": self.battery_reader is not None,
            **self.counts})


def _stamp_json(value: Stamp | Mapping[str, Any] | None) -> dict[str, int] | None:
    if value is None:
        return None
    if isinstance(value, Stamp):
        return value.to_json()
    return dict(value)


def run_forever(config_path: Path, argv: Sequence[str] = ()) -> int:
    """The body of ``scripts/hazard_monitor.py``."""

    config = json.loads(Path(config_path).read_text())
    try:
        notify_reader = thermal.NotifyReader()
    except OSError:
        notify_reader = None  # notifyutil every 5 s instead
    try:
        battery_reader = battery.RegistryReader()
    except OSError:
        battery_reader = None  # ioreg on the publication schedule instead
    smc_reader = smc.Reader() if sys.platform == "darwin" else None  # never raises; opens lazily
    monitor = Monitor(config, notify_reader=notify_reader, battery_reader=battery_reader,
                      smc_reader=smc_reader)

    def stop(signum, _frame):
        monitor.stopping = True
        monitor.stop_signal = signum

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(sig, stop)
    monitor.open_session(argv)
    try:
        monitor.run(fast_thread=True)
    finally:
        monitor.close_session(f"signal {getattr(monitor, 'stop_signal', None)}")
    return 0


# --------------------------------------------------------------------------
# Driver side


class Supervisor:
    """Start, poll (restart on death, record the gap) and stop the monitor process."""

    def __init__(self, custody_dir: Path | str, config: Mapping[str, Any], *,
                 python: str = sys.executable, script: Path = MONITOR_SCRIPT,
                 prefix: Sequence[str] = TASKPOLICY_PREFIX, ctx: Context | None = None) -> None:
        self.custody = Path(custody_dir)
        self.directory = monitor_dir(self.custody)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.config = validate_config(config)
        self.config_path = self.directory / "config.json"
        self.python, self.script, self.prefix = python, Path(script), tuple(prefix)
        self.ctx = ctx or Context()
        self.journal = Journal(self.directory / "supervisor.jsonl")
        self.process: subprocess.Popen | None = None
        self.starts = 0
        self.restarts = 0

    def argv(self) -> list[str]:
        return [*self.prefix, self.python, "-B", str(self.script), "--config", str(self.config_path)]

    def start(self) -> int:
        if not self.config_path.exists():
            write_create_once(self.config_path, canonical_json(self.config) + b"\n")
        argv = self.argv()
        stamp = self.ctx.stamp()
        log = open(self.directory / "monitor.stderr.log", "ab")
        try:
            self.process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log,
                                            stderr=log, start_new_session=True,
                                            cwd=str(REPO_ROOT))
        finally:
            log.close()
        self.starts += 1
        self._record("start", stamp=stamp, pid=self.process.pid, argv=argv, start_index=self.starts)
        return self.process.pid

    def poll(self) -> bool:
        """Called once a second by the driver.  Restarts a dead monitor; True if it did."""

        if self.process is None:
            raise RuntimeError("monitor not started")
        returncode = self.process.poll()
        if returncode is None:
            return False
        detected = self.ctx.stamp()
        previous_pid = self.process.pid
        last = last_line_stamp(self.custody, pid=previous_pid)
        self._record("exit", stamp=detected, pid=previous_pid, returncode=returncode,
                     last_line_finished=last)
        self.restarts += 1
        new_pid = self.start()
        restarted = self.ctx.stamp()
        self._record("gap", stamp=restarted, previous_pid=previous_pid, pid=new_pid,
                     gap={"from": last or detected.to_json(), "to": restarted.to_json()})
        return True

    def stop(self, *, timeout_s: float = 10.0) -> dict[str, Any]:
        """SIGTERM to the monitor's group, wait, KILL fallback; the group is censused."""

        if self.process is None:
            raise RuntimeError("monitor not started")
        pgid = self.process.pid
        stamp = self.ctx.stamp()
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(pgid, sig)
            except ProcessLookupError:
                pass
            try:
                self.process.wait(timeout=timeout_s)
                break
            except subprocess.TimeoutExpired:
                continue
        gone = _group_gone(pgid)
        result = {"pid": pgid, "returncode": self.process.returncode, "group_gone": gone}
        self._record("stop", stamp=stamp, **result)
        self.journal.close()
        return result

    def _record(self, event: str, *, stamp: Stamp, **fields: Any) -> None:
        self.journal.write({"schema": SUPERVISOR_SCHEMA, "event": event, "stamp": stamp.to_json(),
                            **fields})


def _group_gone(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def last_line_stamp(custody_dir: Path | str, *, pid: int) -> dict[str, int] | None:
    """The latest ``finished`` stamp any journal line of a session of ``pid`` carries."""

    best = None
    for name in JOURNALS:
        lines, _note = read_journal(monitor_dir(custody_dir) / f"{name}.jsonl")
        for line in lines:
            if str(line.get("session", "")).split("-", 1)[0] != str(pid):
                continue
            finished = line.get("finished")
            if finished and (best is None or finished["monotonic_ns"] > best["monotonic_ns"]):
                best = finished
    return best


# --------------------------------------------------------------------------
# The member join (plan §3.4)


def clock_samples(lines: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [{"started": line["started"], "finished": line["finished"],
             "anchor": (line.get("values") or {}).get("anchor"),
             "frequency": (line.get("values") or {}).get("frequency"), "error": line.get("error")}
            for line in lines if line.get("kind") == "reading"]


def contention_intervals(lines: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for line in lines:
        if line.get("kind") != "interval":
            continue
        values = dict(line.get("values") or {})
        values.setdefault("interval", {"monotonic_ns": [line["started"]["monotonic_ns"],
                                                        line["finished"]["monotonic_ns"]]})
        values["error"] = line.get("error")
        values["raw"] = line.get("raw") or []
        out.append(values)
    return out


def readings(lines: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [line for line in lines if line.get("kind") == "reading"]


def member_findings(journals: Mapping[str, Sequence[Mapping[str, Any]]], *,
                    span: Mapping[str, Any], request: Mapping[str, Any] | None = None,
                    thresholds: Mapping[str, Mapping[str, Any]] | None = None,
                    ) -> list[dict[str, Any]]:
    """Every physics-in-span finding for one member.

    ``span`` is the member's sampler stream ``{"monotonic_ns": [start, stop]}``
    and ``request`` its request window (contention is judged on the request);
    both in the controller's ``time.monotonic_ns`` domain.
    """

    limits = {"battery": battery.DEFAULT_THRESHOLDS, "thermal": thermal.DEFAULT_THRESHOLDS,
              "contention": contention.DEFAULT_THRESHOLDS, "clock": clock.DEFAULT_THRESHOLDS}
    limits.update(thresholds or {})
    found = []
    found += battery.span_findings(readings(journals.get("battery", ())), span,
                                   limits["battery"])
    found += thermal.span_findings(readings(journals.get("thermal", ())), span,
                                   limits["thermal"])
    found += clock.span_findings(clock_samples(journals.get("clock", ())), span,
                                 step_ns=int(limits["clock"]["step_ns"]))
    found += contention.span_findings(contention_intervals(journals.get("contention", ())),
                                      request or span, limits["contention"])
    return found


def window_events(journals: Mapping[str, Sequence[Mapping[str, Any]]],
                  ) -> list[dict[str, Any]]:
    """Window-level events: ``clock.step``/``clock.frequency_changed`` anywhere,
    ``disk.low``, and monitor sessions (each restart opens a new session)."""

    events = [dict(item) for item in clock.window_events(clock_samples(journals.get("clock", ())))]
    for line in journals.get("disk", ()):
        if line.get("kind") == "event" and (line.get("values") or {}).get("code") == "disk.low":
            events.append({"code": "disk.low", "interval": {
                "monotonic_ns": [line["finished"]["monotonic_ns"]] * 2},
                "observed": line["values"]["low"]})
    sessions = sorted({line["session"] for line in journals.get("monitor", ())
                       if line.get("kind") == "session_start"})
    if len(sessions) > 1:
        events.append({"code": "monitor.restarted", "observed": sessions, "interval": None})
    return events


__all__ = [
    "CONFIG_SCHEMA", "DEFAULT_CADENCE", "DISK_LOW_MARKER", "JOURNALS", "JOURNAL_SCHEMA", "Journal",
    "MONITOR_SCRIPT", "Monitor", "Supervisor", "TASKPOLICY_PREFIX", "build_config",
    "clock_samples", "contention_intervals", "last_line_stamp", "load_journals",
    "member_findings", "monitor_dir", "read_journal", "readings", "run_forever",
    "validate_config", "window_events",
]
