"""The timing ledger: one JSON line per start marker and one per finished run or phase.

Every record carries the stage, its budget, the host and the wall clock. An
`end` record also carries wall seconds, CPU seconds and the exit status, so an
`end` line alone is the full row for its run or phase. A `start` line lets the
watcher see a job that is still open. The ledger lives on JW-EXT by default;
`JW_TIMING_LEDGER` or an explicit path overrides it.

Writes never raise. If the ledger cannot be written (the SSD is not mounted),
the line goes to a fallback file on the internal disk, and if that also fails it
is dropped. The wrapped command's stdio, exit status and signals are untouched.

Library hook for long jobs that want their phases recorded:

    from joulewise.pipeline_time import ledger
    with ledger.phase("inputs", stage="block-analysis", budget_s=3600):
        ...

A phase inside a wrapped run links to it through `JW_TIMING_RUN_ID`. No marker
is added inside a measured window (RL-127 term 7); do not call this there.
"""
from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import resource
import shlex
import signal
import socket
import subprocess
import sys
import time
import uuid

from joulewise.pipeline_time import budgets

SCHEMA = "joulewise.timing_ledger.v1"
DEFAULT_LEDGER = Path("/Volumes/JW-EXT/ledger/timing.jsonl")
FALLBACK_LEDGER = Path.home() / "Library/Logs/JouleWise/timing-ledger-fallback.jsonl"
ENV_LEDGER = "JW_TIMING_LEDGER"
ENV_RUN_ID = "JW_TIMING_RUN_ID"
CMD_CHARS = 400
FORWARDED_SIGNALS = (signal.SIGTERM, signal.SIGHUP)
IGNORED_WHILE_WAITING = (signal.SIGINT, signal.SIGQUIT)


def ledger_path(path: str | os.PathLike | None = None) -> Path:
    if path:
        return Path(path)
    env = os.environ.get(ENV_LEDGER)
    return Path(env) if env else DEFAULT_LEDGER


def host_name() -> str:
    try:
        return socket.gethostname().split(".")[0] or "unknown"
    except OSError:
        return "unknown"


def new_run_id() -> str:
    return uuid.uuid4().hex[:16]


def _append(path: Path, line: str) -> bool:
    import fcntl  # POSIX only; imported here so a failed import cannot break callers
    if not path.parent.is_dir():
        # Create the ledger directory only when its volume is mounted.
        anchor = path.parent.parent
        if not anchor.is_dir():
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.write(line)
            handle.flush()
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return True


def write_record(record: dict, path: str | os.PathLike | None = None,
                 fallback: str | os.PathLike | None = FALLBACK_LEDGER) -> str | None:
    """Append one record; return the path written, or None. Never raises."""
    try:
        line = json.dumps(dict(record, schema=SCHEMA), sort_keys=True, separators=(",", ":")) + "\n"
    except (TypeError, ValueError):
        return None
    for target in (ledger_path(path), Path(fallback) if fallback else None):
        if target is None:
            continue
        try:
            if _append(target, line):
                return str(target)
        except OSError:
            continue
    return None


def _base(kind, stage, budget_s, run_id, name=None, parent=None, start=None):
    record = {
        "kind": kind,
        "run_id": run_id,
        "stage": stage,
        "budget_s": budgets.budget_for(stage, budget_s),
        "host": host_name(),
        "start_epoch_s": round(time.time() if start is None else start, 3),
    }
    if name is not None:
        record["phase"] = name
    if parent:
        record["parent_run_id"] = parent
    return record


def _rss_bytes(ru_maxrss: int) -> int:
    # Darwin reports bytes; Linux reports kilobytes.
    return int(ru_maxrss) if sys.platform == "darwin" else int(ru_maxrss) * 1024


def exit_fields(status: int) -> dict:
    """Fields for a raw wait status: exit code, or the terminating signal."""
    if os.WIFSIGNALED(status):
        sig = os.WTERMSIG(status)
        return {"exit": f"signal:{sig}", "exit_code": 128 + sig, "signal": sig}
    code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
    return {"exit": code, "exit_code": code}


def run_wrapped(argv, stage, budget_s=None, path=None, run_id=None, popen=subprocess.Popen,
                wait4=os.wait4, clock=time.time, monotonic=time.monotonic, note=None):
    """Run argv with inherited stdio, record start and end, return the raw wait status.

    The child inherits stdin, stdout, stderr and every open descriptor. SIGINT and
    SIGQUIT go to the child from the terminal's process group, so the wrapper
    ignores them while waiting; SIGTERM and SIGHUP sent to the wrapper are
    forwarded to the child. The only change to the child's environment is
    `JW_TIMING_RUN_ID` (and `JW_TIMING_LEDGER`), so phases it records link here.
    """
    run_id = run_id or new_run_id()
    parent = os.environ.get(ENV_RUN_ID) or None
    start_wall = clock()
    start = _base("run", stage, budget_s, run_id, parent=parent, start=start_wall)
    start.update({"event": "start", "pid": os.getpid(), "cwd": os.getcwd(),
                  "argv0": os.path.basename(str(argv[0])) if argv else "",
                  "cmd": shlex.join(str(a) for a in argv)[:CMD_CHARS]})
    if note:
        start["note"] = str(note)[:200]
    env = dict(os.environ)
    env[ENV_RUN_ID] = run_id
    env[ENV_LEDGER] = str(ledger_path(path))
    t0 = monotonic()
    try:
        child = popen(list(argv), env=env, close_fds=False)
    except FileNotFoundError:
        start["child_pid"] = None
        write_record(start, path)
        sys.stderr.write(f"timing_ledger: {argv[0]}: command not found\n")
        status = 127 << 8
        _write_end(start, status, start_wall, clock(), 0.0, None, path)
        return status
    except PermissionError:
        start["child_pid"] = None
        write_record(start, path)
        sys.stderr.write(f"timing_ledger: {argv[0]}: permission denied\n")
        status = 126 << 8
        _write_end(start, status, start_wall, clock(), 0.0, None, path)
        return status
    start["child_pid"] = child.pid
    write_record(start, path)

    previous = {}

    def forward(signum, _frame):
        with contextlib.suppress(ProcessLookupError, OSError):
            child.send_signal(signum)

    for signum in FORWARDED_SIGNALS:
        with contextlib.suppress(ValueError, OSError):
            previous[signum] = signal.signal(signum, forward)
    for signum in IGNORED_WHILE_WAITING:
        with contextlib.suppress(ValueError, OSError):
            previous[signum] = signal.signal(signum, signal.SIG_IGN)
    try:
        while True:
            try:
                _pid, status, usage = wait4(child.pid, 0)
                break
            except InterruptedError:
                continue
            except ChildProcessError:  # already reaped elsewhere; fall back to Popen's code
                rc = child.poll()
                rc = 1 if rc is None else rc
                status = (rc << 8) if rc >= 0 else ((-rc) & 0x7F)
                usage = None
                break
    finally:
        for signum, handler in previous.items():
            with contextlib.suppress(ValueError, OSError, TypeError):
                signal.signal(signum, handler)
    # Popen must not try to reap again.
    child.returncode = os.waitstatus_to_exitcode(status)
    wall = monotonic() - t0
    _write_end(start, status, start_wall, start_wall + wall, wall, usage, path)
    return status


def _write_end(start, status, start_wall, end_wall, wall, usage, path):
    end = {k: v for k, v in start.items() if k not in ("event",)}
    end.update({"event": "end", "end_epoch_s": round(end_wall, 3),
                "wall_s": round(max(0.0, end_wall - start_wall) if wall is None else wall, 3)})
    end.update(exit_fields(status))
    if usage is not None:
        end["cpu_user_s"] = round(usage.ru_utime, 3)
        end["cpu_sys_s"] = round(usage.ru_stime, 3)
        end["cpu_s"] = round(usage.ru_utime + usage.ru_stime, 3)
        end["max_rss_bytes"] = _rss_bytes(usage.ru_maxrss)
    budget = end.get("budget_s")
    if budget:
        end["over_budget_ratio"] = round(end["wall_s"] / budget, 3)
    write_record(end, path)


def exit_like(status: int) -> None:
    """Leave the wrapper the way the child left: same exit code, or the same signal."""
    if os.WIFSIGNALED(status):
        sig = os.WTERMSIG(status)
        with contextlib.suppress(ValueError, OSError):
            signal.signal(sig, signal.SIG_DFL)
            sys.stdout.flush()
            sys.stderr.flush()
            os.kill(os.getpid(), sig)
        os._exit(128 + sig)
    sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)


def _cpu_now() -> tuple[float, float]:
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + kids.ru_utime, own.ru_stime + kids.ru_stime


@contextlib.contextmanager
def phase(name, stage, budget_s=None, path=None, clock=time.time, monotonic=time.monotonic):
    """Record one phase of the calling process: a start marker, then an end row.

    The end row's exit is 0 on normal exit and 1 when the block raised (the
    exception propagates unchanged). CPU is this process plus its reaped
    children over the phase.
    """
    run_id = new_run_id()
    parent = os.environ.get(ENV_RUN_ID) or None
    start_wall = clock()
    start = _base("phase", stage, budget_s, run_id, name=name, parent=parent, start=start_wall)
    start.update({"event": "start", "pid": os.getpid(), "child_pid": os.getpid()})
    write_record(start, path)
    user0, sys0 = _cpu_now()
    t0 = monotonic()
    ok = False
    try:
        yield run_id
        ok = True
    finally:
        wall = monotonic() - t0
        user1, sys1 = _cpu_now()
        end = {k: v for k, v in start.items() if k != "event"}
        end.update({"event": "end", "end_epoch_s": round(start_wall + wall, 3), "wall_s": round(wall, 3),
                    "cpu_user_s": round(user1 - user0, 3), "cpu_sys_s": round(sys1 - sys0, 3),
                    "cpu_s": round((user1 - user0) + (sys1 - sys0), 3),
                    "exit": 0 if ok else 1, "exit_code": 0 if ok else 1})
        if end.get("budget_s"):
            end["over_budget_ratio"] = round(wall / end["budget_s"], 3)
        write_record(end, path)


def record_phase(name, stage, start_epoch_s, end_epoch_s, budget_s=None, exit_code=0, path=None, **extra):
    """Record an already-finished phase from its stamps (for jobs that log their own times)."""
    record = _base("phase", stage, budget_s, new_run_id(), name=name,
                   parent=os.environ.get(ENV_RUN_ID) or None, start=start_epoch_s)
    wall = max(0.0, float(end_epoch_s) - float(start_epoch_s))
    record.update({"event": "end", "end_epoch_s": round(float(end_epoch_s), 3), "wall_s": round(wall, 3),
                   "exit": int(exit_code), "exit_code": int(exit_code)})
    if record.get("budget_s"):
        record["over_budget_ratio"] = round(wall / record["budget_s"], 3)
    record.update({k: v for k, v in extra.items() if k not in record})
    return write_record(record, path)


def read_ledger(path: str | os.PathLike | None = None) -> list[dict]:
    """Every parseable record, in file order. Malformed lines are skipped."""
    target = ledger_path(path)
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("schema") == SCHEMA and row.get("run_id"):
            rows.append(row)
    return rows


def pair_entries(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """(open starts without an end, finished end rows), by run id."""
    starts, ends = {}, {}
    for row in rows:
        if row.get("event") == "start":
            starts[row["run_id"]] = row
        elif row.get("event") == "end":
            ends[row["run_id"]] = row
    open_rows = [row for run_id, row in starts.items() if run_id not in ends]
    return open_rows, list(ends.values())
