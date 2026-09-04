#!/usr/bin/env python3
"""Launch and supervise the JouleWise magistrate without touching a repo tree.

The launchd process is a short tick.  When a launch is safe it forks a resident
supervisor, which retains the service lock and enforces the ruled stand-down
deadlines at ten-second resolution.  All mutable state is kept below the
configured magistrate custody root.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) in sys.path:
    sys.path.remove(str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from joulewise.night_gate import (  # noqa: E402
    NightPlan,
    ProbeResult,
    Probes,
    agent_census,
)
from scripts.run_night import (  # noqa: E402
    COURIER_DEADLINE_S,
    COURIER_LOCK_FRESH_S,
    _next_deadman_epoch,
)


SCHEMA = "joulewise.magistrate_watchdog_state.v1"
LOCK_SCHEMA = "joulewise.magistrate_lock.v1"
EVENT_SCHEMA = "joulewise.magistrate_event.v1"
DEFAULT_CUSTODY_ROOT = Path.home() / "night-custody" / "magistrate"
CANONICAL_REPO = Path("/Users/edr/code/JouleWise")
SESSION_BIN_ENV = "MAGISTRATE_SESSION_BIN"
CUSTODY_ROOT_ENV = "MAGISTRATE_WATCHDOG_CUSTODY_ROOT"
DEFAULT_SESSION_BIN = Path("/Users/edr/.local/bin/claude")
PROMPT_TEMPLATE = REPO_ROOT / "docs" / "process" / "MAGISTRATE_RELAUNCH_PROMPT.md"
STOP_REPOSITORY = "https://github.com/mpmdw/JouleWise.git"
STOP_REF_GLOB = "refs/heads/ops/stop*"
POSITIVE_CONTROL_REF = "refs/heads/main"

# File 15 rows 3-4: these are local-time/fence and resident deadlines.
PLAN_LEAD_S = 25 * 60
REQUEST_LEAD_S = 25 * 60
TERM_LEAD_S = 16 * 60
KILL_LEAD_S = 15 * 60
SUPERVISOR_POLL_S = 10
REMOTE_STOP_PROBE_CADENCE_S = 5 * 60
STOP_COOPERATIVE_S = 9 * 60
STOP_TERM_GRACE_S = 60
CLOCK_SKEW_LIMIT_S = 60
GENERIC_BACKOFF_S = (120, 300, 900, 1800, 3600)
USAGE_BACKOFF_S = (900, 1800, 3600, 7200, 7200)

# Keep this launch shape in one place.  The magistrate can change one tuple
# after the owed permission-prompt bench without touching supervisor logic.
SESSION_ARGV_AFTER_PROMPT = (
    "--output-format",
    "stream-json",
    "--verbose",
    "--permission-mode",
    "auto",
    "--permission-prompts",
    "none",
    "--model",
    "fable",
    "--effort",
    "high",
    "--allowedTools",
    "Read,Glob,Grep,Bash,Edit,Write,Agent,Task,Skill,ScheduleWakeup,SendMessage,ListAgents,TaskCreate,TaskUpdate,TaskList,"
    "mcp__claude_ai_Gmail__send_message,mcp__codex__codex,mcp__codex__codex-reply",
)

USAGE_EXHAUSTED_PATTERNS = (
    re.compile(r"\busage\s+limit(?:ed|\s+reached)?\b", re.IGNORECASE),
    re.compile(r"\bspend\s+limit\b", re.IGNORECASE),
    re.compile(r"\brate\s+limit(?:ed|\s+reached)?\b", re.IGNORECASE),
    re.compile(r"\brate_limit\b", re.IGNORECASE),
    re.compile(r"\bquota\s+(?:exceeded|exhausted)\b", re.IGNORECASE),
    re.compile(r"\b(?:limit|usage)\s+resets?(?:\s+(?:at|in))?\b", re.IGNORECASE),
    re.compile(r"\bhttp\s+429\b", re.IGNORECASE),
    re.compile(r"\bhit\s+(?:your|the)\s+(?:usage\s+)?limit\b", re.IGNORECASE),
)


@dataclasses.dataclass(frozen=True)
class ProcessInfo:
    pid: int
    ppid: int
    start_time: str
    command: str


class ProcessTable(Protocol):
    def snapshot(self) -> Sequence[ProcessInfo]: ...

    def send_signal(self, pid: int, signum: int) -> None: ...


class Child(Protocol):
    pid: int

    def poll(self) -> int | None: ...


@dataclasses.dataclass(frozen=True)
class CensusObservation:
    empty: bool
    exit_code: int
    stdout: str
    stderr: str


@dataclasses.dataclass(frozen=True)
class StopObservation:
    state: str  # CLEAR, STOPPED, or NETWORK_UNCERTAIN
    detail: str


@dataclasses.dataclass(frozen=True)
class Decision:
    state: str
    reason: str
    launch: bool = False
    adopt: bool = False


@dataclasses.dataclass
class Dependencies:
    wall_now: Callable[[], dt.datetime]
    monotonic: Callable[[], float]
    census: Callable[[], CensusObservation]
    git_probe: Callable[[], StopObservation]
    processes: ProcessTable
    spawn: Callable[[Sequence[str], Path, Path, Path], Child]
    version_probe: Callable[[Path], str]
    sleep: Callable[[float], None]


class RealProcessTable:
    """A process table with a stable lstart token for PID-reuse protection."""

    def snapshot(self) -> Sequence[ProcessInfo]:
        result = subprocess.run(
            ("/bin/ps", "-axo", "pid=,ppid=,lstart=,command="),
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ps failed: {result.stderr.strip()}")
        rows: list[ProcessInfo] = []
        for line in result.stdout.splitlines():
            parts = line.strip().split(None, 7)
            if len(parts) != 8:
                continue
            try:
                pid = int(parts[0])
                ppid = int(parts[1])
            except ValueError:
                continue
            rows.append(
                ProcessInfo(
                    pid=pid,
                    ppid=ppid,
                    start_time=" ".join(parts[2:7]),
                    command=parts[7],
                )
            )
        return rows

    def send_signal(self, pid: int, signum: int) -> None:
        try:
            os.kill(pid, signum)
        except ProcessLookupError:
            pass


class Storage:
    """Filesystem seam and the single guarded writer for watchdog custody."""

    def __init__(self, root: Path, *, dry_run: bool = False) -> None:
        self.root = root.expanduser().resolve(strict=False)
        self.dry_run = dry_run
        self.would_write: list[str] = []

    def _write_path(self, path: Path) -> Path:
        resolved = path.expanduser().resolve(strict=False)
        if resolved != self.root and self.root not in resolved.parents:
            raise RuntimeError(f"refusing write outside custody root: {resolved}")
        return resolved

    def exists(self, path: Path) -> bool:
        return path.exists() or path.is_symlink()

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def glob_plans(self) -> Sequence[Path]:
        return sorted(self.root.parent.glob("*/night_plan.json"))

    def mkdir(self, path: Path) -> None:
        path = self._write_path(path)
        if self.dry_run:
            self.would_write.append(f"mkdir {path}")
            return
        path.mkdir(parents=True, exist_ok=True)

    def atomic_json(self, path: Path, value: Mapping[str, Any]) -> None:
        data = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
        self.atomic_bytes(path, data)

    def atomic_bytes(self, path: Path, data: bytes) -> None:
        path = self._write_path(path)
        if self.dry_run:
            self.would_write.append(f"atomic_write {path} ({len(data)} bytes)")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            view = memoryview(data)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, path)
        self._fsync_dir(path.parent)

    def exclusive_json(self, path: Path, value: Mapping[str, Any]) -> None:
        path = self._write_path(path)
        data = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
        if self.dry_run:
            self.would_write.append(f"exclusive_write {path} ({len(data)} bytes)")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            view = memoryview(data)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self._fsync_dir(path.parent)

    def append_jsonl(self, path: Path, value: Mapping[str, Any]) -> None:
        path = self._write_path(path)
        data = (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")
        if self.dry_run:
            self.would_write.append(f"append {path} ({len(data)} bytes)")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            view = memoryview(data)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def unlink(self, path: Path) -> None:
        path = self._write_path(path)
        if self.dry_run:
            self.would_write.append(f"unlink {path}")
            return
        path.unlink(missing_ok=True)
        self._fsync_dir(path.parent)

    @staticmethod
    def _fsync_dir(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _probe_runner(argv: tuple[str, ...]) -> ProbeResult:
    started = time.monotonic_ns()
    try:
        result = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,  # magistrate bench 2026-09-03: 2 s produced spurious NETWORK_UNCERTAIN holds on slow links
        )
        return ProbeResult(
            argv=argv,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            monotonic_ns=max(started, time.monotonic_ns()),
        )
    except Exception as exc:
        return ProbeResult(
            argv=argv,
            exit_code=-1,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
            monotonic_ns=max(started, time.monotonic_ns()),
        )


def production_census() -> CensusObservation:
    probes = Probes(
        run=_probe_runner,
        now_epoch_s=time.time,
        monotonic_ns=time.monotonic_ns,
        read_text=lambda path: Path(path).read_text(encoding="utf-8"),
        checkout_head=lambda: "unused-by-agent-census",
    )
    result, refusal = agent_census(probes)
    return CensusObservation(
        empty=refusal is None,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def remote_stop_probe() -> StopObservation:
    base = (
        "/usr/bin/git",
        "-c",
        "credential.helper=",
        "-c",
        "credential.helper=!false",
        "ls-remote",
        "--exit-code",
        STOP_REPOSITORY,
    )

    def run(ref: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["GIT_TERMINAL_PROMPT"] = "0"
        environment["GIT_CONFIG_NOSYSTEM"] = "1"
        return subprocess.run(
            (*base, ref),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,  # magistrate bench 2026-09-03: 2 s produced spurious NETWORK_UNCERTAIN holds on slow links
            env=environment,
        )

    try:
        control = run(POSITIVE_CONTROL_REF)
    except Exception as exc:
        return StopObservation("NETWORK_UNCERTAIN", f"positive control exception: {exc}")
    if control.returncode != 0:
        return StopObservation(
            "NETWORK_UNCERTAIN",
            f"positive control rc={control.returncode}: {control.stderr.strip()}",
        )
    try:
        stop = run(STOP_REF_GLOB)
    except Exception as exc:
        return StopObservation("NETWORK_UNCERTAIN", f"stop-ref exception: {exc}")
    if stop.returncode == 0:
        return StopObservation("STOPPED", stop.stdout.strip() or STOP_REF_GLOB)
    if stop.returncode == 2:
        return StopObservation("CLEAR", "stop branch absent; positive control present")
    return StopObservation(
        "NETWORK_UNCERTAIN",
        f"stop-ref rc={stop.returncode}: {stop.stderr.strip()}",
    )


def real_spawn(argv: Sequence[str], cwd: Path, stdout_path: Path, stderr_path: Path) -> Child:
    stdout_handle = stdout_path.open("ab", buffering=0)
    stderr_handle = stderr_path.open("ab", buffering=0)
    try:
        return subprocess.Popen(
            list(argv),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            start_new_session=True,
            close_fds=True,
        )
    finally:
        stdout_handle.close()
        stderr_handle.close()


def version_probe(binary: Path) -> str:
    result = subprocess.run(
        (str(binary), "--version"),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"session binary --version failed rc={result.returncode}")
    return result.stdout.strip()


def real_dependencies() -> Dependencies:
    return Dependencies(
        wall_now=lambda: dt.datetime.now().astimezone(),
        monotonic=time.monotonic,
        census=production_census,
        git_probe=remote_stop_probe,
        processes=RealProcessTable(),
        spawn=real_spawn,
        version_probe=version_probe,
        sleep=time.sleep,
    )


def initial_state() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "state": "BOOT",
        "transition_seq": 0,
        "activation_id": None,
        "attempt": 0,
        "backoff_index": 0,
        "usage_backoff_index": 0,
        "generic_backoff_index": 0,
        "next_eligible_monotonic": 0.0,
        "notice_pending": [],
        "last_clock": None,
        "clock_sane_samples": 0,
        "clock_drain": False,
        "standdown_phase": None,
    }


def load_state(storage: Storage) -> dict[str, Any]:
    path = storage.root / "state.json"
    if not storage.exists(path):
        return initial_state()
    try:
        value = json.loads(storage.read_text(path))
    except (OSError, ValueError):
        value = initial_state()
        value["state_error"] = "state.json unreadable; launch held until rewritten"
        value["state"] = "HOLD_UNSAFE"
        return value
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        value = initial_state()
        value["state_error"] = "state.json schema invalid; launch held until rewritten"
        value["state"] = "HOLD_UNSAFE"
    return value


def load_plans(storage: Storage) -> tuple[list[NightPlan], list[str]]:
    plans: list[NightPlan] = []
    errors: list[str] = []
    for path in storage.glob_plans():
        try:
            raw = json.loads(storage.read_text(path))
            plans.append(NightPlan.from_mapping(raw))
        except Exception as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return plans, errors


def local_fixed_fence(now: dt.datetime) -> str | None:
    local = now.astimezone()
    second = (
        local.hour * 3600
        + local.minute * 60
        + local.second
        + local.microsecond / 1_000_000
    )
    if 2 * 3600 + 45 * 60 <= second < 3 * 3600 + 30 * 60:
        return "belt_02:45_03:30"
    if 7 * 3600 <= second < 7 * 3600 + 60:
        return "deadman_minute_07:00"
    return None


def plan_completion_epoch(plan: NightPlan) -> float:
    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S


def plan_span_active(plan: NightPlan, now_epoch_s: float, storage: Storage) -> bool:
    """File 15 row 3, including completion, courier, dead-man, and chain rules."""

    if now_epoch_s < plan.t0_epoch_s - PLAN_LEAD_S:
        return False
    night = Path(plan.custody_root) / "night"
    chain_open = storage.exists(night / "chain.started") and not storage.exists(
        night / "chain.exited"
    )
    if chain_open:
        return True
    if now_epoch_s <= plan_completion_epoch(plan):
        return True
    if storage.exists(night / "courier.sent"):
        return False
    return now_epoch_s <= _next_deadman_epoch(plan.t0_epoch_s) + COURIER_LOCK_FRESH_S


def relevant_standdown_plan(
    plans: Iterable[NightPlan], now_epoch_s: float, storage: Storage
) -> NightPlan | None:
    candidates = [
        plan
        for plan in plans
        if now_epoch_s >= plan.t0_epoch_s - REQUEST_LEAD_S
        and plan_span_active(plan, now_epoch_s, storage)
    ]
    return min(candidates, key=lambda plan: plan.t0_epoch_s, default=None)


def standdown_phase(plan: NightPlan, now_epoch_s: float) -> str | None:
    if now_epoch_s >= plan.t0_epoch_s - KILL_LEAD_S:
        return "KILL"
    if now_epoch_s >= plan.t0_epoch_s - TERM_LEAD_S:
        return "TERM"
    if now_epoch_s >= plan.t0_epoch_s - REQUEST_LEAD_S:
        return "REQUEST"
    return None


def read_lock(storage: Storage) -> dict[str, Any] | None:
    path = storage.root / "magistrate.lock"
    if not storage.exists(path):
        return None
    try:
        value = json.loads(storage.read_text(path))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def process_by_pid(processes: Sequence[ProcessInfo], pid: int) -> ProcessInfo | None:
    return next(
        (
            item
            for item in processes
            if item.pid == pid and "<defunct>" not in item.command.casefold()
        ),
        None,
    )


def owned_process(lock: Mapping[str, Any] | None, processes: Sequence[ProcessInfo]) -> ProcessInfo | None:
    if not lock or lock.get("schema") != LOCK_SCHEMA:
        return None
    pid = lock.get("pid")
    start_time = lock.get("start_time")
    if isinstance(pid, bool) or not isinstance(pid, int) or not isinstance(start_time, str):
        return None
    process = process_by_pid(processes, pid)
    if process is None or process.start_time != start_time:
        return None
    return process


def clock_uncertain(state: dict[str, Any], wall: dt.datetime, monotonic: float) -> bool:
    previous = state.get("last_clock")
    uncertain = False
    if isinstance(previous, Mapping):
        try:
            wall_delta = wall.timestamp() - float(previous["epoch_s"])
            mono_delta = monotonic - float(previous["monotonic"])
            uncertain = (
                wall_delta < 0
                or mono_delta < 0
                or abs(wall_delta - mono_delta) > CLOCK_SKEW_LIMIT_S
            )
        except (KeyError, TypeError, ValueError):
            uncertain = True
    state["last_clock"] = {"epoch_s": wall.timestamp(), "monotonic": monotonic}
    if uncertain:
        state["clock_sane_samples"] = 0
        return True
    state["clock_sane_samples"] = int(state.get("clock_sane_samples", 0)) + 1
    if state.get("state") == "CLOCK_UNCERTAIN" and state["clock_sane_samples"] < 2:
        return True
    return False


def transition(
    storage: Storage,
    state: dict[str, Any],
    new_state: str,
    reason: str,
    now: dt.datetime,
    *,
    notice: str | None = None,
) -> None:
    old_state = str(state.get("state", "BOOT"))
    if old_state == new_state:
        return
    sequence = int(state.get("transition_seq", 0)) + 1
    state["state"] = new_state
    state["transition_seq"] = sequence
    state["reason"] = reason
    state["transition_epoch_s"] = now.timestamp()
    event = {
        "schema": EVENT_SCHEMA,
        "kind": "transition",
        "sequence": sequence,
        "from": old_state,
        "to": new_state,
        "reason": reason,
        "epoch_s": now.timestamp(),
    }
    storage.append_jsonl(storage.root / "events.jsonl", event)
    if notice is not None:
        pending = state.setdefault("notice_pending", [])
        notice_id = f"transition-{sequence}-{notice}"
        if not any(item.get("id") == notice_id for item in pending if isinstance(item, dict)):
            pending.append(
                {
                    "id": notice_id,
                    "kind": notice,
                    "epoch_s": now.timestamp(),
                    "reason": reason,
                }
            )


def append_census_event(
    storage: Storage, state: Mapping[str, Any], now: dt.datetime, census: CensusObservation
) -> None:
    storage.append_jsonl(
        storage.root / "events.jsonl",
        {
            "schema": EVENT_SCHEMA,
            "kind": "census",
            "sequence": state.get("transition_seq", 0),
            "epoch_s": now.timestamp(),
            "exit_code": census.exit_code,
            "empty": census.empty,
            "stdout": census.stdout[:4000],
            "stderr": census.stderr[:1000],
        },
    )


def consume_notice_ack(storage: Storage, state: dict[str, Any], now: dt.datetime) -> bool:
    path = storage.root / "notice.ack"
    if not storage.exists(path):
        return False
    try:
        value = json.loads(storage.read_text(path))
        activation_id = value["activation_id"]
    except (OSError, ValueError, KeyError, TypeError):
        return False
    if activation_id != state.get("activation_id"):
        return False
    acknowledged = list(state.get("notice_pending", []))
    state["notice_pending"] = []
    storage.atomic_json(storage.root / "state.json", state)
    storage.append_jsonl(
        storage.root / "events.jsonl",
        {
            "schema": EVENT_SCHEMA,
            "kind": "notice_acknowledged",
            "activation_id": activation_id,
            "epoch_s": now.timestamp(),
            "notice_ids": [
                item.get("id") for item in acknowledged if isinstance(item, Mapping)
            ],
        },
    )
    storage.unlink(path)
    return True


def jitter_for_activation(activation_id: str) -> int:
    return int(hashlib.sha256(activation_id.encode("utf-8")).hexdigest()[:8], 16) % 121


def classify_exit(exit_code: int, output: str) -> str:
    if exit_code == 0:
        return "clean"
    if any(pattern.search(output) for pattern in USAGE_EXHAUSTED_PATTERNS):
        return "usage_exhausted"
    return "generic_error"


def apply_backoff(
    storage: Storage,
    state: dict[str, Any],
    now: dt.datetime,
    monotonic: float,
    exit_class: str,
    detail: str,
) -> None:
    usage = exit_class == "usage_exhausted"
    index_key = "usage_backoff_index" if usage else "generic_backoff_index"
    index = int(state.get(index_key, state.get("backoff_index", 0)))
    ladder = USAGE_BACKOFF_S if usage else GENERIC_BACKOFF_S
    delay = ladder[min(index, len(ladder) - 1)]
    activation_id = str(state.get("activation_id") or "unassigned")
    if usage:
        delay += jitter_for_activation(activation_id)
    state[index_key] = min(index + 1, len(ladder) - 1)
    state["backoff_index"] = min(index + 1, len(ladder) - 1)
    state["next_eligible_monotonic"] = monotonic + delay
    state["last_exit_class"] = exit_class
    transition(
        storage,
        state,
        "BACKOFF_USAGE" if usage else "BACKOFF",
        detail,
        now,
        notice="usage_backoff" if usage else "launch_failure",
    )


def decide(storage: Storage, deps: Dependencies, state: dict[str, Any]) -> Decision:
    wall = deps.wall_now().astimezone()
    monotonic = deps.monotonic()
    if clock_uncertain(state, wall, monotonic):
        return Decision("CLOCK_UNCERTAIN", "wall and monotonic deltas disagree")

    plans, plan_errors = load_plans(storage)
    if plan_errors:
        return Decision("HOLD_UNSAFE", "; ".join(plan_errors))

    lock = read_lock(storage)
    owner: ProcessInfo | None = None
    if lock is not None:
        try:
            process_snapshot = deps.processes.snapshot()
        except Exception as exc:
            return Decision("HOLD_UNSAFE", f"process table unavailable: {exc}")
        owner = owned_process(lock, process_snapshot)
        if owner is None:
            storage.unlink(storage.root / "magistrate.lock")
            lock = None

    fixed = local_fixed_fence(wall)
    active_plans = [plan for plan in plans if plan_span_active(plan, wall.timestamp(), storage)]
    try:
        stop = deps.git_probe()
    except Exception as exc:
        stop = StopObservation("NETWORK_UNCERTAIN", f"git probe exception: {exc}")
    state["remote_stop"] = {
        "state": stop.state,
        "detail": stop.detail,
        "observed_monotonic": monotonic,
    }
    if storage.exists(storage.root / "STOP"):
        stop = StopObservation("STOPPED", "local STOP file present")
    if active_plans:
        census = deps.census()
        append_census_event(storage, state, wall, census)
        if owner is not None:
            phase = standdown_phase(min(active_plans, key=lambda item: item.t0_epoch_s), wall.timestamp())
            return Decision(
                f"STANDDOWN_{phase}",
                f"owned session; plan span; phase={phase}",
                adopt=True,
            )
        if not census.empty:
            return Decision("HOLD_CENSUS", "production census non-empty inside plan span")
        return Decision("FENCED", "plan span active and census empty")
    if stop.state == "STOPPED":
        return Decision("STOPPED", stop.detail, adopt=owner is not None)
    if stop.state != "CLEAR":
        return Decision("NETWORK_UNCERTAIN", stop.detail, adopt=owner is not None)
    if fixed is not None:
        return Decision("FENCED", fixed)
    if owner is not None:
        return Decision("ACTIVE", f"owned pid {owner.pid} is live", adopt=True)
    if monotonic < float(state.get("next_eligible_monotonic", 0.0)):
        waiting_state = (
            "BACKOFF_USAGE"
            if state.get("last_exit_class") == "usage_exhausted"
            else "BACKOFF"
        )
        return Decision(waiting_state, "backoff has not expired")
    if lock is not None:
        return Decision("HOLD_UNSAFE", "magistrate.lock could not be cleared")
    return Decision("LAUNCHING", "all launch predicates clear", launch=True)


def resolve_session_binary(path: Path) -> Path:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise RuntimeError(f"session binary symlink unavailable: {path}: {exc}") from exc
    if not stat.S_ISLNK(metadata.st_mode):
        raise RuntimeError(f"session binary must be a symlink: {path}")
    try:
        target = path.resolve(strict=True)
        target_metadata = target.stat()
    except OSError as exc:
        raise RuntimeError(f"session binary symlink is dangling: {path}: {exc}") from exc
    if not stat.S_ISREG(target_metadata.st_mode) or not os.access(target, os.X_OK):
        raise RuntimeError(f"session binary target is not an executable regular file: {path}")
    return path


def render_prompt(storage: Storage, state: Mapping[str, Any], now: dt.datetime) -> str:
    text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "@@ACTIVATION_ID@@": str(state.get("activation_id")),
        "@@CUSTODY_ROOT@@": str(storage.root),
        "@@LAUNCH_ISO@@": now.isoformat(),
        "@@NOTICE_PENDING@@": json.dumps(state.get("notice_pending", []), sort_keys=True),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def session_argv(binary: Path, prompt: str, activation_id: str) -> tuple[str, ...]:
    return (
        str(binary),
        "-p",
        prompt,
        *SESSION_ARGV_AFTER_PROMPT,
        "--name",
        f"joulewise-magistrate-{activation_id[:12]}",
    )


def stable_descendants(processes: ProcessTable, root_pid: int) -> list[int]:
    """Walk ppid edges repeatedly; process groups are deliberately irrelevant."""

    seen = {root_pid}
    unchanged = 0
    for _ in range(8):
        snapshot = [
            process
            for process in processes.snapshot()
            if "<defunct>" not in process.command.casefold()
        ]
        before = set(seen)
        changed = True
        while changed:
            changed = False
            for process in snapshot:
                if process.ppid in seen and process.pid not in seen:
                    seen.add(process.pid)
                    changed = True
        if seen == before:
            unchanged += 1
            if unchanged >= 2:
                break
        else:
            unchanged = 0
    return sorted(seen, reverse=True)


def signal_owned_tree(processes: ProcessTable, root_pid: int, signum: int) -> list[int]:
    pids = stable_descendants(processes, root_pid)
    # Descendants are signalled before the root so they cannot be orphaned first.
    for pid in [item for item in pids if item != root_pid] + [root_pid]:
        processes.send_signal(pid, signum)
    return pids


class AdoptedChild:
    """Read-only Popen substitute for a child whose prior supervisor exited."""

    def __init__(self, processes: ProcessTable, lock_record: Mapping[str, Any]) -> None:
        self.pid = int(lock_record["pid"])
        self._processes = processes
        self._lock_record = lock_record

    def poll(self) -> int | None:
        return (
            None
            if owned_process(self._lock_record, self._processes.snapshot()) is not None
            else 0
        )


class ResidentSupervisor:
    def __init__(
        self,
        storage: Storage,
        deps: Dependencies,
        state: dict[str, Any],
        child: Child,
        lock_record: dict[str, Any],
        stdout_path: Path,
        stderr_path: Path,
    ) -> None:
        self.storage = storage
        self.deps = deps
        self.state = state
        self.child = child
        self.lock_record = lock_record
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        cached_stop = state.get("remote_stop")
        if isinstance(cached_stop, Mapping):
            cached_state = str(cached_stop.get("state", "NETWORK_UNCERTAIN"))
            cached_detail = str(cached_stop.get("detail", "remote stop has not been probed"))
            try:
                cached_monotonic = float(cached_stop.get("observed_monotonic", float("-inf")))
            except (TypeError, ValueError):
                cached_monotonic = float("-inf")
        else:
            cached_state = "NETWORK_UNCERTAIN"
            cached_detail = "remote stop has not been probed"
            cached_monotonic = float("-inf")
        self._remote_stop = StopObservation(cached_state, cached_detail)
        self._remote_stop_observed_monotonic = cached_monotonic
        self._remote_probe_started_monotonic = cached_monotonic
        self._remote_probe_thread: threading.Thread | None = None
        self._remote_probe_lock = threading.Lock()

    def _run_remote_probe(self) -> None:
        try:
            observation = self.deps.git_probe()
        except Exception as exc:
            observation = StopObservation("NETWORK_UNCERTAIN", f"git probe exception: {exc}")
        observed_monotonic = self.deps.monotonic()
        with self._remote_probe_lock:
            self._remote_stop = observation
            self._remote_stop_observed_monotonic = observed_monotonic

    def _cached_remote_stop(self, monotonic: float) -> StopObservation:
        """Return immediately; refresh the remote switch only on a daemon thread."""

        with self._remote_probe_lock:
            thread = self._remote_probe_thread
            if thread is not None and not thread.is_alive():
                self._remote_probe_thread = None
                thread = None
            due = monotonic - self._remote_probe_started_monotonic >= REMOTE_STOP_PROBE_CADENCE_S
            if thread is None and due:
                self._remote_probe_started_monotonic = monotonic
                thread = threading.Thread(
                    target=self._run_remote_probe,
                    name="magistrate-remote-stop-probe",
                    daemon=True,
                )
                self._remote_probe_thread = thread
                thread.start()
            observation = self._remote_stop
            observed_monotonic = self._remote_stop_observed_monotonic
        self.state["remote_stop"] = {
            "state": observation.state,
            "detail": observation.detail,
            "observed_monotonic": observed_monotonic,
        }
        return observation

    def _output_tail(self) -> str:
        pieces: list[str] = []
        for path in (self.stdout_path, self.stderr_path):
            try:
                pieces.append(self.storage.read_text(path)[-4096:])
            except OSError:
                pass
        return "\n".join(pieces)

    def _finish_child(self, exit_code: int, now: dt.datetime) -> bool:
        requested = self.storage.exists(self.storage.root / "standdown.request")
        self.storage.unlink(self.storage.root / "magistrate.lock")
        self.state["clock_drain"] = False
        if requested:
            self.storage.unlink(self.storage.root / "standdown.request")
            self.state["standdown_phase"] = "COMPLETE"
            self.state["backoff_index"] = 0
            transition(
                self.storage,
                self.state,
                "FENCED",
                f"cooperative stand-down exit={exit_code}",
                now,
            )
        else:
            exit_class = classify_exit(exit_code, self._output_tail())
            if exit_class == "clean":
                self.state["backoff_index"] = 0
                self.state["usage_backoff_index"] = 0
                self.state["generic_backoff_index"] = 0
                self.state["next_eligible_monotonic"] = self.deps.monotonic() + 300
                transition(self.storage, self.state, "IDLE", "clean activation exit", now)
            else:
                apply_backoff(
                    self.storage,
                    self.state,
                    now,
                    self.deps.monotonic(),
                    exit_class,
                    f"session exit={exit_code} class={exit_class}",
                )
        self.storage.atomic_json(self.storage.root / "state.json", self.state)
        return False

    def _write_request(self, plan: NightPlan | None, now: dt.datetime, *, reason: str) -> None:
        path = self.storage.root / "standdown.request"
        if self.storage.exists(path):
            return
        value: dict[str, Any] = {
            "reason": reason,
            "requested_epoch_s": now.timestamp(),
            "requested_monotonic": self.deps.monotonic(),
            "exit_within_s": STOP_COOPERATIVE_S,
        }
        if plan is not None:
            value.update(
                {
                    "plan_id": plan.plan_id,
                    "t0_epoch_s": plan.t0_epoch_s,
                    "term_epoch_s": plan.t0_epoch_s - TERM_LEAD_S,
                    "kill_epoch_s": plan.t0_epoch_s - KILL_LEAD_S,
                }
            )
        self.storage.atomic_json(path, value)

    def _record_signal(self, now: dt.datetime, signum: int, pids: Sequence[int]) -> None:
        self.storage.append_jsonl(
            self.storage.root / "events.jsonl",
            {
                "schema": EVENT_SCHEMA,
                "kind": "signal",
                "activation_id": self.state.get("activation_id"),
                "epoch_s": now.timestamp(),
                "signal": signal.Signals(signum).name,
                "pids": list(pids),
            },
        )

    def _forced_hold(self, now: dt.datetime) -> bool:
        owner_gone = False
        for _ in range(SUPERVISOR_POLL_S):
            if self.child.poll() is not None:
                owner_gone = True
                break
            if owned_process(self.lock_record, self.deps.processes.snapshot()) is None:
                owner_gone = True
                break
            self.deps.sleep(1)
        census = self.deps.census()
        append_census_event(self.storage, self.state, now, census)
        if owner_gone:
            self.storage.unlink(self.storage.root / "magistrate.lock")
            self.state["clock_drain"] = False
        self.storage.unlink(self.storage.root / "standdown.request")
        self.state["standdown_phase"] = "COMPLETE"
        held = not census.empty or not owner_gone
        transition(
            self.storage,
            self.state,
            "HOLD_CENSUS" if held else "FENCED",
            (
                "owned process survived forced stand-down"
                if not owner_gone
                else "post-kill census non-empty"
                if not census.empty
                else "forced stand-down complete"
            ),
            now,
            notice="forced_standdown",
        )
        self.storage.atomic_json(self.storage.root / "state.json", self.state)
        return False

    def _enforce_plan(self, plan: NightPlan, now: dt.datetime) -> bool:
        phase = standdown_phase(plan, now.timestamp())
        self._write_request(plan, now, reason=f"plan {plan.plan_id} stand-down")
        if phase == "REQUEST":
            transition(
                self.storage,
                self.state,
                "STANDDOWN_REQUESTED",
                f"plan={plan.plan_id}; t0={plan.t0_epoch_s}",
                now,
            )
        elif phase == "TERM":
            if self.state.get("standdown_phase") != "TERM":
                owner = owned_process(self.lock_record, self.deps.processes.snapshot())
                if owner is None:
                    return self._forced_hold(now)
                pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGTERM)
                self._record_signal(now, signal.SIGTERM, pids)
                self.state["standdown_phase"] = "TERM"
            transition(
                self.storage,
                self.state,
                "STANDDOWN_TERM",
                f"plan={plan.plan_id}; t0={plan.t0_epoch_s}",
                now,
            )
        elif phase == "KILL":
            owner = owned_process(self.lock_record, self.deps.processes.snapshot())
            if owner is None:
                return self._forced_hold(now)
            pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGKILL)
            self._record_signal(now, signal.SIGKILL, pids)
            return self._forced_hold(now)
        self.storage.atomic_json(self.storage.root / "state.json", self.state)
        return True

    def _enforce_drain(
        self,
        now: dt.datetime,
        monotonic: float,
        *,
        reason: str,
        state_name: str,
        notice: str | None = None,
    ) -> bool:
        self._write_request(None, now, reason=reason)
        requested = json.loads(self.storage.read_text(self.storage.root / "standdown.request"))
        try:
            requested_monotonic = float(requested["requested_monotonic"])
            elapsed = max(0.0, monotonic - requested_monotonic)
        except (KeyError, TypeError, ValueError):
            elapsed = max(0.0, now.timestamp() - float(requested["requested_epoch_s"]))
        if elapsed >= STOP_COOPERATIVE_S + STOP_TERM_GRACE_S:
            owner = owned_process(self.lock_record, self.deps.processes.snapshot())
            if owner is None:
                return self._forced_hold(now)
            pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGKILL)
            self._record_signal(now, signal.SIGKILL, pids)
            return self._forced_hold(now)
        if elapsed >= STOP_COOPERATIVE_S and self.state.get("standdown_phase") != "TERM":
            owner = owned_process(self.lock_record, self.deps.processes.snapshot())
            if owner is None:
                return self._forced_hold(now)
            pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGTERM)
            self._record_signal(now, signal.SIGTERM, pids)
            self.state["standdown_phase"] = "TERM"
        transition(self.storage, self.state, state_name, reason, now, notice=notice)
        self.storage.atomic_json(self.storage.root / "state.json", self.state)
        return True

    def step(self) -> bool:
        now = self.deps.wall_now().astimezone()
        monotonic = self.deps.monotonic()
        # The email acknowledgement is durable evidence and must win even if
        # the child exits between resident polls.
        consume_notice_ack(self.storage, self.state, now)
        exit_code = self.child.poll()
        if exit_code is not None:
            return self._finish_child(exit_code, now)

        uncertain = clock_uncertain(self.state, now, monotonic)
        if uncertain:
            self.state["clock_drain"] = True
        if self.state.get("clock_drain"):
            return self._enforce_drain(
                now,
                monotonic,
                reason="wall and monotonic deltas disagree; conservative resident drain",
                state_name="CLOCK_UNCERTAIN",
                notice="clock_uncertain",
            )

        plans, errors = load_plans(self.storage)
        if errors:
            self._write_request(None, now, reason="malformed plan")
            transition(self.storage, self.state, "HOLD_UNSAFE", "; ".join(errors), now)
            self.storage.atomic_json(self.storage.root / "state.json", self.state)
            return True

        plan = relevant_standdown_plan(plans, now.timestamp(), self.storage)
        # Physical stand-down deadlines are resolved before consulting even a
        # cached remote result.  An in-flight network probe runs independently
        # and can never delay this path.
        if plan is not None:
            return self._enforce_plan(plan, now)

        if self.storage.exists(self.storage.root / "STOP"):
            stop = StopObservation("STOPPED", "local STOP file present")
        else:
            stop = self._cached_remote_stop(monotonic)
        if stop.state == "STOPPED":
            return self._enforce_drain(
                now,
                monotonic,
                reason=stop.detail,
                state_name="STOP_REQUESTED",
            )
        if stop.state != "CLEAR":
            transition(
                self.storage,
                self.state,
                "NETWORK_UNCERTAIN",
                stop.detail,
                now,
                notice="network_uncertain",
            )
            self.storage.atomic_json(self.storage.root / "state.json", self.state)
            return True

        transition(self.storage, self.state, "ACTIVE", "owned session running", now)
        self.storage.atomic_json(self.storage.root / "state.json", self.state)
        return True

    def run(self) -> None:
        while True:
            started = self.deps.monotonic()
            if not self.step():
                return
            elapsed = max(0.0, self.deps.monotonic() - started)
            self.deps.sleep(max(0.0, SUPERVISOR_POLL_S - elapsed))


def start_session(
    storage: Storage,
    deps: Dependencies,
    state: dict[str, Any],
    *,
    binary_path: Path | None = None,
) -> ResidentSupervisor:
    now = deps.wall_now().astimezone()
    activation_id = str(state.get("activation_id") or uuid.uuid4())
    state["activation_id"] = activation_id
    state["attempt"] = int(state.get("attempt", 0)) + 1
    requested_binary = binary_path or Path(
        os.environ.get(SESSION_BIN_ENV, str(DEFAULT_SESSION_BIN))
    )
    binary = resolve_session_binary(requested_binary)
    binary_version = deps.version_probe(binary)
    prompt = render_prompt(storage, state, now)
    attempt_dir = storage.root / "attempts" / activation_id
    storage.mkdir(attempt_dir)
    prompt_path = attempt_dir / "prompt.md"
    stdout_path = attempt_dir / f"attempt-{state['attempt']}.stream.jsonl"
    stderr_path = attempt_dir / f"attempt-{state['attempt']}.stderr.log"
    storage.atomic_bytes(prompt_path, prompt.encode("utf-8"))
    argv = session_argv(binary, prompt, activation_id)
    supervisor_process = process_by_pid(deps.processes.snapshot(), os.getpid())
    starting_lock = {
        "schema": LOCK_SCHEMA,
        "activation_id": activation_id,
        "pid": os.getpid(),
        "start_time": (
            supervisor_process.start_time if supervisor_process is not None else "unobserved"
        ),
        "supervisor_pid": os.getpid(),
        "launch_epoch_s": now.timestamp(),
        "binary_symlink": str(binary),
        "binary_version": binary_version,
        "status": "STARTING",
    }
    storage.exclusive_json(storage.root / "magistrate.lock", starting_lock)
    try:
        child = deps.spawn(argv, CANONICAL_REPO, stdout_path, stderr_path)
    except Exception:
        storage.unlink(storage.root / "magistrate.lock")
        raise

    process: ProcessInfo | None = None
    for _ in range(20):
        process = process_by_pid(deps.processes.snapshot(), child.pid)
        if process is not None:
            break
        deps.sleep(0.1)
    if process is None:
        raise RuntimeError(f"spawned pid {child.pid} absent from process table")
    lock_record = {
        "schema": LOCK_SCHEMA,
        "activation_id": activation_id,
        "pid": child.pid,
        "start_time": process.start_time,
        "supervisor_pid": os.getpid(),
        "launch_epoch_s": now.timestamp(),
        "binary_symlink": str(binary),
        "binary_version": binary_version,
        "status": "ACTIVE",
    }
    storage.atomic_json(storage.root / "magistrate.lock", lock_record)
    state["standdown_phase"] = None
    state["clock_drain"] = False
    transition(storage, state, "ACTIVE", f"spawned activation {activation_id}", now)
    storage.atomic_json(storage.root / "state.json", state)
    return ResidentSupervisor(
        storage,
        deps,
        state,
        child,
        lock_record,
        stdout_path,
        stderr_path,
    )


def start_session_guarded(
    storage: Storage,
    deps: Dependencies,
    state: dict[str, Any],
    *,
    binary_path: Path | None = None,
) -> ResidentSupervisor | None:
    try:
        return start_session(storage, deps, state, binary_path=binary_path)
    except Exception as exc:
        now = deps.wall_now().astimezone()
        apply_backoff(
            storage,
            state,
            now,
            deps.monotonic(),
            "generic_error",
            f"supervisor start failed: {type(exc).__name__}: {exc}",
        )
        storage.atomic_json(storage.root / "state.json", state)
        return None


def adopt_session(
    storage: Storage, deps: Dependencies, state: dict[str, Any]
) -> ResidentSupervisor:
    lock_record = read_lock(storage)
    process_snapshot = deps.processes.snapshot()
    owner = owned_process(lock_record, process_snapshot)
    if lock_record is None or owner is None:
        raise RuntimeError("owned session disappeared before supervisor adoption")
    activation_id = str(lock_record["activation_id"])
    state["activation_id"] = activation_id
    attempt = int(state.get("attempt", 1) or 1)
    attempt_dir = storage.root / "attempts" / activation_id
    storage.append_jsonl(
        storage.root / "events.jsonl",
        {
            "schema": EVENT_SCHEMA,
            "kind": "supervisor_adopted",
            "activation_id": activation_id,
            "pid": owner.pid,
            "epoch_s": deps.wall_now().astimezone().timestamp(),
        },
    )
    return ResidentSupervisor(
        storage,
        deps,
        state,
        AdoptedChild(deps.processes, lock_record),
        dict(lock_record),
        attempt_dir / f"attempt-{attempt}.stream.jsonl",
        attempt_dir / f"attempt-{attempt}.stderr.log",
    )


@contextlib.contextmanager
def service_lock(storage: Storage) -> Iterable[int | None]:
    storage.mkdir(storage.root)
    path = storage._write_path(storage.root / "watchdog.lock")
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield None
            return
        yield descriptor
    finally:
        os.close(descriptor)


def tick(storage: Storage, deps: Dependencies, *, dry_run: bool = False) -> Decision:
    state = load_state(storage)
    decision = decide(storage, deps, state)
    now = deps.wall_now().astimezone()
    notice = None
    if decision.state in {"CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN", "HOLD_CENSUS"}:
        notice = decision.state.lower()
    transition(storage, state, decision.state, decision.reason, now, notice=notice)
    storage.atomic_json(storage.root / "state.json", state)
    if dry_run:
        return decision
    if not decision.launch and not decision.adopt:
        return decision

    pid = os.fork()
    if pid:
        return decision
    try:
        os.setsid()
        supervisor = (
            start_session_guarded(storage, deps, state)
            if decision.launch
            else adopt_session(storage, deps, state)
        )
        if supervisor is not None:
            supervisor.run()
    except BaseException as exc:
        failed_now = deps.wall_now().astimezone()
        apply_backoff(
            storage,
            state,
            failed_now,
            deps.monotonic(),
            "generic_error",
            f"supervisor start failed: {type(exc).__name__}: {exc}",
        )
        storage.atomic_json(storage.root / "state.json", state)
    finally:
        os._exit(0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print decisions and suppress writes/spawn")
    parser.add_argument(
        "--custody-root",
        type=Path,
        default=Path(os.environ.get(CUSTODY_ROOT_ENV, str(DEFAULT_CUSTODY_ROOT))),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    storage = Storage(args.custody_root, dry_run=args.dry_run)
    deps = real_dependencies()
    if args.dry_run:
        storage.mkdir(storage.root)
        storage.would_write.append(f"open_and_flock {storage.root / 'watchdog.lock'}")
        decision = tick(storage, deps, dry_run=True)
        print(f"decision={decision.state} reason={decision.reason}")
        for action in storage.would_write:
            print(f"WOULD_WRITE {action}")
        if decision.launch:
            print(f"WOULD_WRITE mkdir {storage.root / 'attempts' / '<activation-id>'}")
            print("WOULD_WRITE prompt, stream, stderr, and exclusive magistrate.lock under that attempt")
            print("WOULD_SPAWN resident supervisor; child spawn suppressed")
        elif decision.adopt:
            print("WOULD_ADOPT owned session; supervisor adoption suppressed")
        else:
            print("WOULD_SPAWN none")
        return 0
    with service_lock(storage) as descriptor:
        if descriptor is None:
            return 0
        tick(storage, deps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
