"""Recorded /proc cumulative CPU-s/s census and R0-L3-style contention policy.

The measured quantity is the largest SINGLE process outside the capture and
server trees. Aggregate CPU is disclosed, never used to trigger a redo. Linux
has no kernel_task exemption. This is not the Mac's agent/custody admission
census; operators must keep the rig free of other agents and measurement jobs.
"""
from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import math
import os
from pathlib import Path
import threading
import time


class QuietIndeterminate(RuntimeError):
    pass


@dataclass(frozen=True)
class ProcessCpu:
    pid: int
    ppid: int
    start_ticks: int
    cpu_ticks: int
    command: str


@dataclass(frozen=True)
class CpuSnapshot:
    stamp_ns: int
    processes: tuple[ProcessCpu, ...]
    disappeared: tuple[int, ...] = ()


def proc_snapshot(root="/proc", *, clock_ns=time.monotonic_ns):
    """PID identity includes start ticks, so PID reuse cannot become CPU work."""
    start = clock_ns()
    rows, gone = [], []
    try:
        for directory in Path(root).iterdir():
            if not directory.name.isdigit():
                continue
            try:
                text = (directory / "stat").read_text()
            except FileNotFoundError:
                gone.append(int(directory.name))
                continue
            left, right = text.index("("), text.rindex(")")
            fields = text[right + 1:].split()
            row = ProcessCpu(int(text[:left].strip()), int(fields[1]), int(fields[19]),
                             int(fields[11]) + int(fields[12]), text[left + 1:right])
            if row.pid != int(directory.name) or min(row.ppid, row.start_ticks, row.cpu_ticks) < 0:
                raise ValueError("invalid process identity/counters")
            rows.append(row)
    except (OSError, ValueError, IndexError) as exc:
        raise QuietIndeterminate("/proc CPU snapshot unreadable: " + str(exc)) from exc
    if not rows:
        raise QuietIndeterminate("/proc CPU snapshot empty")
    end = clock_ns()
    if end < start:
        raise QuietIndeterminate("snapshot clock regressed")
    return CpuSnapshot((start + end) // 2, tuple(rows), tuple(gone))


def cpu_interval(opening, closing, *, ticks_per_s, tree_roots=()):
    elapsed = (closing.stamp_ns - opening.stamp_ns) / 1e9
    if elapsed <= 0 or ticks_per_s <= 0:
        raise QuietIndeterminate("invalid CPU interval/tick rate")
    before = {(p.pid, p.start_ticks): p for p in opening.processes}
    after = {(p.pid, p.start_ticks): p for p in closing.processes}
    excluded = set(tree_roots)
    changed = True
    while changed:
        descendants = {p.pid for p in (*opening.processes, *closing.processes) if p.ppid in excluded}
        changed = not descendants <= excluded
        excluded.update(descendants)
    rows = []
    for identity in before.keys() & after.keys():
        a, b = before[identity], after[identity]
        if b.cpu_ticks < a.cpu_ticks:
            raise QuietIndeterminate(f"CPU counter regressed for pid {b.pid}")
        rows.append({**asdict(b), "cpu_s_per_s": (b.cpu_ticks - a.cpu_ticks) / ticks_per_s / elapsed,
                     "in_capture_tree": b.pid in excluded})
    outside = [r for r in rows if not r["in_capture_tree"]]
    largest = max(outside, key=lambda r: r["cpu_s_per_s"], default=None)
    return {"start_ns": opening.stamp_ns, "end_ns": closing.stamp_ns,
            "elapsed_s": elapsed, "processes": sorted(rows, key=lambda r: r["pid"]),
            "largest_outside": largest,
            "outside_cpu_s_per_s": sum(r["cpu_s_per_s"] for r in outside),
            "unaccounted_started": [asdict(after[k]) for k in sorted(after.keys() - before.keys())],
            "unaccounted_exited": [asdict(before[k]) for k in sorted(before.keys() - after.keys())],
            "disappeared_during_snapshot": list(opening.disappeared + closing.disappeared)}


class ContentionPolicy:
    """Touching/overlapping >=0.5-core windows spanning >=60 s are sustained.

    Ordinary >0.05-core contention is a flag. Attempt zero may be redone once;
    a sustained episode on attempt one is retained with contended=True.
    """

    def __init__(self):
        self.heavy_start = self.heavy_end = None
        self.sustained = False
        self.receipts = []

    def observe(self, row):
        largest = (row.get("largest_outside") or {}).get("cpu_s_per_s", 0)
        heavy = largest >= 0.5
        flagged = largest > 0.05
        if heavy:
            if self.heavy_end is None or row["start_ns"] > self.heavy_end:
                self.heavy_start = row["start_ns"]
            self.heavy_end = row["end_ns"]
            self.sustained |= self.heavy_end - self.heavy_start >= 60_000_000_000
        else:
            self.heavy_start = self.heavy_end = None
        self.receipts.append({**row, "heavy": heavy, "flagged": flagged,
                              "sustained_detected": self.sustained})

    def decision(self, attempt):
        if attempt not in (0, 1):
            raise ValueError("only original and one redo are permitted")
        return "redo" if self.sustained and attempt == 0 else "contended" if self.sustained else "keep"


class LinuxQuietGuard:
    """One worker records rolling >=30 s windows at a 5 s cadence.

    stop returns every raw snapshot and interval, including unaccounted process
    churn. Missing observations are tooling faults, never declarations of quiet.
    Tests inject snapshot/tick sources; no live /proc access is needed.
    """

    def __init__(self, *, snapshot=proc_snapshot, ticks_per_s=None, tree_roots=(),
                 interval_s=5.0, window_s=30.0):
        if (not math.isfinite(interval_s) or not math.isfinite(window_s)
                or interval_s <= 0 or window_s < interval_s):
            raise ValueError("quiet window must be at least one positive polling interval")
        self.snapshot = snapshot
        self.ticks = ticks_per_s if ticks_per_s is not None else os.sysconf("SC_CLK_TCK")
        self.tree_roots = tuple(tree_roots)
        self.interval_s, self.window_ns = interval_s, round(window_s * 1e9)
        self.event = threading.Event()
        self.thread = None
        self.policy = ContentionPolicy()
        self.snapshots = []
        self.windows = deque()
        self.errors = []
        self.result = None
        self.root_identities = {}

    def check(self):
        try:
            current = self.snapshot()
            by_pid = {p.pid: p for p in current.processes}
            for pid in self.tree_roots:
                if pid not in by_pid:
                    raise QuietIndeterminate(f"required capture/server root pid {pid} absent")
                identity = by_pid[pid].start_ticks
                if pid in self.root_identities and identity != self.root_identities[pid]:
                    raise QuietIndeterminate(f"required root pid {pid} reused")
                self.root_identities[pid] = identity
            if self.snapshots and current.stamp_ns <= self.snapshots[-1].stamp_ns:
                raise QuietIndeterminate("quiet snapshot clock not increasing")
            self.snapshots.append(current)
            self.windows.append(current)
            while len(self.windows) > 1 and current.stamp_ns - self.windows[1].stamp_ns >= self.window_ns:
                self.windows.popleft()
            if current.stamp_ns - self.windows[0].stamp_ns >= self.window_ns:
                self.policy.observe(cpu_interval(self.windows[0], current,
                    ticks_per_s=self.ticks, tree_roots=self.tree_roots))
        except Exception as exc:
            self.errors.append(type(exc).__name__ + ":" + str(exc))

    def _loop(self):
        while not self.event.wait(self.interval_s):
            self.check()

    def start(self):
        self.check()
        if self.errors:
            raise QuietIndeterminate(self.errors[-1])
        self.thread = threading.Thread(target=self._loop, daemon=True, name="align-linux-quiet")
        self.thread.start()

    def stop(self, attempt=0):
        if self.result is not None:
            return self.result
        self.event.set()
        if self.thread is not None:
            self.thread.join(10)
        if self.thread is not None and self.thread.is_alive():
            self.errors.append("quiet worker stop timeout")
        else:
            self.check()
        if not self.policy.receipts:
            self.errors.append("no complete 30 s CPU interval")
        self.result = {"decision": "indeterminate" if self.errors else self.policy.decision(attempt),
                       "errors": self.errors, "ticks_per_s": self.ticks,
                       "tree_roots": list(self.tree_roots),
                       "snapshots": [asdict(s) for s in self.snapshots],
                       "intervals": self.policy.receipts}
        return self.result
