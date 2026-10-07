"""Reap the processes a test left behind (test hygiene, 2026-10-07).

The block-5 driver tests start real child processes: the fake hazard monitor
and the fake KM003C meter (their command lines name the test's temporary
custody root) and the chains' ``/bin/sleep`` children (in process groups the
driver journals). A test that fails, or that deliberately leaves a group
running for the dead-man path, used to leave them alive after the suite, and
a leaked process is a contending process in the next window's census.

``reap(marker, night=...)`` kills (SIGKILL) every process of this user that
either names ``marker`` (the test's own temporary directory) on its command
line, or belongs to a process group recorded in the test's night journals and
started after the test did, then waits for each to be gone (``waitpid`` when
it is this process's child). It never touches a process that names neither.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Iterable

PS_ARGV = ["/bin/ps", "-axww", "-o", "pid=,pgid=,uid=,etime=,command="]


def _elapsed_s(text: str) -> float | None:
    """ps etime ([[dd-]hh:]mm:ss) in seconds."""

    try:
        days, _, clock = text.rpartition("-")
        parts = [int(part) for part in clock.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        return int(days or 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]
    except ValueError:
        return None


def processes() -> list[tuple[int, int, int, float | None, str]]:
    """(pid, pgid, uid, elapsed seconds, command) for every process."""

    try:
        output = subprocess.run(PS_ARGV, capture_output=True, text=True, timeout=10, check=False,
                                env={**os.environ, "LC_ALL": "C"}).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in output.splitlines():
        fields = line.split(None, 4)
        if len(fields) < 4:
            continue
        try:
            pid, pgid, uid = int(fields[0]), int(fields[1]), int(fields[2])
        except ValueError:
            continue
        rows.append((pid, pgid, uid, _elapsed_s(fields[3]), fields[4] if len(fields) > 4 else ""))
    return rows


def journal_pgids(night: Path | None) -> set[int]:
    """Every integer ``pgid`` recorded in the JSON lines under ``night``."""

    found: set[int] = set()
    if night is None or not Path(night).is_dir():
        return found
    for path in Path(night).rglob("*.json*"):
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines() or [text]:
            try:
                value = json.loads(line)
            except ValueError:
                continue
            stack = [value]
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    for key, inner in item.items():
                        if key == "pgid" and isinstance(inner, int) and not isinstance(inner, bool) and inner > 1:
                            found.add(inner)
                        else:
                            stack.append(inner)
                elif isinstance(item, list):
                    stack.extend(item)
    return found


def targets(marker: str, *, pgids: Iterable[int] = (), lived_s: float | None = None) -> list[int]:
    """The pids to reap: naming ``marker``, or in ``pgids`` and younger than ``lived_s``."""

    me, uid, groups = os.getpid(), os.getuid(), {int(pgid) for pgid in pgids}
    own_group = os.getpgid(0)
    chosen = []
    for pid, pgid, owner, elapsed, command in processes():
        if pid == me or owner != uid or "/bin/ps" in command:
            continue
        if marker and marker in command:
            chosen.append(pid)
        elif (pgid in groups and pgid != own_group and lived_s is not None and elapsed is not None
              and elapsed <= lived_s + 1):
            chosen.append(pid)
    return chosen


def reap(marker: str, *, night: Path | None = None, started_monotonic: float | None = None,
         timeout_s: float = 5.0) -> list[int]:
    """Kill and wait for the test's leftover processes; returns the pids killed."""

    lived_s = None if started_monotonic is None else time.monotonic() - started_monotonic
    pids = targets(marker, pgids=journal_pgids(night), lived_s=lived_s)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    deadline = time.monotonic() + timeout_s
    pending = set(pids)
    while pending and time.monotonic() < deadline:
        for pid in list(pending):
            try:
                done, _status = os.waitpid(pid, os.WNOHANG)
                if done == pid:
                    pending.discard(pid)
                    continue
            except ChildProcessError:
                pass  # not our child: gone when kill(0) fails
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                pending.discard(pid)
            except PermissionError:
                pending.discard(pid)
        if pending:
            time.sleep(0.02)
    return pids


def kill_and_wait(process: subprocess.Popen, timeout_s: float = 5.0) -> None:
    """Kill a test's own child if it still runs, and reap it (no zombie left)."""

    if process.poll() is None:
        try:
            process.kill()
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        pass
