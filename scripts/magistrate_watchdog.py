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
    PLAN_MAX_AGE_S,
    PlanError,
    agent_census,
)
from scripts.run_night import (  # noqa: E402
    COURIER_DEADLINE_S,
    COURIER_LOCK_FRESH_S,
    _next_deadman_epoch,
    make_probes,
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
RETIRED_V1_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "night_plan_v1_retired.json"
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


def _load_retired_v1_keys() -> frozenset[str]:
    """Derive the retired-plan shape from the immutable golden fixture."""

    try:
        value = json.loads(RETIRED_V1_FIXTURE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"retired-v1 fixture is unavailable: {exc}") from exc
    if (
        not isinstance(value, Mapping)
        or value.get("schema") != "joulewise.night_plan.v1"
        or not all(isinstance(key, str) for key in value)
    ):
        raise RuntimeError("retired-v1 fixture is not the golden v1 object")
    return frozenset(value)


RETIRED_V1_KEYS = _load_retired_v1_keys()
# The frozen v1 producer emitted one exact required-key shape.  Keeping the
# required set tied to the same imported fixture prevents a second hand-coded
# legacy schema from drifting away from the positive identification rule.
RETIRED_V1_REQUIRED_KEYS = RETIRED_V1_KEYS


def is_retired_v1_plan(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    keys = set(value)
    return (
        value.get("schema") == "joulewise.night_plan.v1"
        and keys <= RETIRED_V1_KEYS
        and RETIRED_V1_REQUIRED_KEYS <= keys
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
    result, refusal = agent_census(make_probes())
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
        "activation_spawn_epoch_s": None,
        "resident_session": None,
        "attempt": 0,
        "backoff_index": 0,
        "usage_backoff_index": 0,
        "generic_backoff_index": 0,
        "next_eligible_monotonic": 0.0,
        "notice_pending": [],
        "last_clock": None,
        "clock_sane_samples": 0,
        "clock_drain": False,
        "resident_hold_drain": None,
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


@dataclasses.dataclass(frozen=True)
class PlanDiagnostic:
    kind: str
    reason: str | None
    path: Path
    detail: str


@dataclasses.dataclass(frozen=True)
class PlanSnapshot:
    plans: tuple[NightPlan, ...]
    errors: tuple[str, ...]
    diagnostics: tuple[PlanDiagnostic, ...]


def _activation_spawn_epoch_s(state: Mapping[str, Any]) -> float | None:
    value = state.get("activation_spawn_epoch_s")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _plan_event_key(
    activation_id: str,
    activation_spawn_epoch_s: float | None,
    plan_dir: str,
    kind: str,
    detail: str,
) -> tuple[str, float | None, str, str, str]:
    digest = hashlib.sha256(detail.encode("utf-8")).hexdigest()
    return activation_id, activation_spawn_epoch_s, plan_dir, kind, digest


def recorded_plan_event_keys(
    storage: Storage,
    activation_id: str,
    activation_spawn_epoch_s: float | None = None,
) -> set[tuple[str, float | None, str, str, str]]:
    keys: set[tuple[str, float | None, str, str, str]] = set()
    path = storage.root / "events.jsonl"
    if not storage.exists(path):
        return keys
    try:
        lines = storage.read_text(path).splitlines()
    except OSError:
        return keys
    for line in lines:
        try:
            event = json.loads(line)
        except (TypeError, ValueError):
            continue
        if (
            not isinstance(event, Mapping)
            or event.get("activation_id") != activation_id
            or event.get("activation_spawn_epoch_s") != activation_spawn_epoch_s
        ):
            continue
        plan_dir = event.get("plan_dir")
        kind = event.get("kind")
        digest = event.get("detail_sha256")
        if all(isinstance(item, str) for item in (plan_dir, kind, digest)):
            keys.add(
                (
                    activation_id,
                    activation_spawn_epoch_s,
                    plan_dir,
                    kind,
                    digest,
                )
            )
    return keys


def record_plan_diagnostics(
    storage: Storage,
    diagnostics: Iterable[PlanDiagnostic],
    *,
    activation_id: str,
    activation_spawn_epoch_s: float | None = None,
) -> None:
    seen = recorded_plan_event_keys(
        storage, activation_id, activation_spawn_epoch_s
    )
    for diagnostic in diagnostics:
        plan_dir = str(diagnostic.path.parent.resolve(strict=False))
        detail = diagnostic.detail[:4000]
        key = _plan_event_key(
            activation_id,
            activation_spawn_epoch_s,
            plan_dir,
            diagnostic.kind,
            detail,
        )
        if key in seen:
            continue
        storage.append_jsonl(
            storage.root / "events.jsonl",
            {
                "schema": EVENT_SCHEMA,
                "kind": diagnostic.kind,
                "reason": diagnostic.reason,
                "activation_id": activation_id,
                "activation_spawn_epoch_s": activation_spawn_epoch_s,
                "plan_dir": plan_dir,
                "plan_path": str(diagnostic.path.resolve(strict=False)),
                "detail": detail,
                "detail_sha256": key[-1],
                "epoch_s": time.time(),
            },
        )
        seen.add(key)


def load_plans(storage: Storage, *, now_epoch_s: float | None = None) -> PlanSnapshot:
    """Read and classify plans without mutating watchdog custody."""

    plans: list[NightPlan] = []
    errors: list[str] = []
    diagnostics: list[PlanDiagnostic] = []
    observed_now = time.time() if now_epoch_s is None else now_epoch_s
    for path in storage.glob_plans():
        try:
            text = storage.read_text(path)
        except OSError as exc:
            detail = f"{type(exc).__name__}: {exc}"
            diagnostics.append(
                PlanDiagnostic("plan_unreadable", "night_plan_unreadable", path, detail)
            )
            errors.append(f"night_plan_unreadable {path}: {detail}")
            continue
        try:
            raw: object = json.loads(text)
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            diagnostics.append(
                PlanDiagnostic("plan_unreadable", "night_plan_unreadable", path, detail)
            )
            errors.append(f"night_plan_unreadable {path}: {detail}")
            continue
        if is_retired_v1_plan(raw):
            diagnostics.append(
                PlanDiagnostic(
                    "plan_retired_v1",
                    None,
                    path,
                    "positively identified retired schema joulewise.night_plan.v1",
                )
            )
            continue
        try:
            plan = NightPlan.from_mapping(raw)  # type: ignore[arg-type]
            if plan.authored_epoch_s > observed_now:
                raise PlanError(
                    "night_plan_malformed", "plan authored_epoch_s is in the future"
                )
        except PlanError as exc:
            detail = f"{type(exc).__name__}: {exc.detail}"
            diagnostics.append(
                PlanDiagnostic("plan_malformed", "night_plan_malformed", path, detail)
            )
            errors.append(f"night_plan_malformed {path}: {exc.detail}")
            continue
        plans.append(plan)
    return PlanSnapshot(tuple(plans), tuple(errors), tuple(diagnostics))


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


def plan_is_armed(plan: NightPlan, now_epoch_s: float, storage: Storage) -> bool:
    """An authored plan remains armed until its durable completion or final bound."""

    if plan.authored_epoch_s > now_epoch_s:
        return False
    night = Path(plan.custody_root) / "night"
    if storage.exists(night / "chain.started") and not storage.exists(night / "chain.exited"):
        return True
    if storage.exists(night / "courier.sent"):
        return False
    return now_epoch_s <= _next_deadman_epoch(plan.t0_epoch_s) + COURIER_LOCK_FRESH_S


def armed_plans(
    plans: Iterable[NightPlan], now_epoch_s: float, storage: Storage
) -> list[NightPlan]:
    return sorted(
        (plan for plan in plans if plan_is_armed(plan, now_epoch_s, storage)),
        key=lambda plan: (plan.plan_id, plan.measurement_root, plan.measurement_head),
    )


def _canonical_measurement_root(plan: NightPlan) -> str:
    return str(Path(plan.measurement_root).expanduser().resolve(strict=False))


def plan_conflicts(plans: Sequence[NightPlan]) -> list[str]:
    """Return deterministic armed-plan conflicts that make relaunch unsafe."""

    conflicts: set[str] = set()
    heads_by_root: dict[str, set[str]] = {}
    for plan in plans:
        heads_by_root.setdefault(_canonical_measurement_root(plan), set()).add(
            plan.measurement_head
        )
    for root, heads in heads_by_root.items():
        if len(heads) > 1:
            conflicts.add(
                f"one measurement_root has multiple heads: root={root!r} heads={sorted(heads)!r}"
            )

    for index, left in enumerate(plans):
        left_start = left.t0_epoch_s - PLAN_LEAD_S
        left_end = _next_deadman_epoch(left.t0_epoch_s) + COURIER_LOCK_FRESH_S
        for right in plans[index + 1 :]:
            if _canonical_measurement_root(left) == _canonical_measurement_root(right):
                continue
            right_start = right.t0_epoch_s - PLAN_LEAD_S
            right_end = _next_deadman_epoch(right.t0_epoch_s) + COURIER_LOCK_FRESH_S
            if max(left_start, right_start) <= min(left_end, right_end):
                conflicts.add(
                    "overlapping spans use different measurement roots: "
                    f"{left.plan_id}={_canonical_measurement_root(left)!r}, "
                    f"{right.plan_id}={_canonical_measurement_root(right)!r}"
                )
    return sorted(conflicts)


def fenced_checkout_rows(plans: Sequence[NightPlan]) -> list[list[str | None]]:
    """Return the deterministic prompt payload for all frozen checkouts."""

    rows: list[list[str | None]] = [
        ["__canonical_repo__", str(CANONICAL_REPO), None]
    ]
    rows.extend(
        [plan.plan_id, _canonical_measurement_root(plan), plan.measurement_head]
        for plan in plans
    )
    return rows


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


def _claude_command_suffix(command: str) -> str | None:
    match = re.search(r"(?:^|[/\s])claude(?:\s|$)", command, re.IGNORECASE)
    return command[match.end() :].lstrip().casefold() if match is not None else None


def _is_interactive_claude(command: str) -> bool:
    suffix = _claude_command_suffix(command)
    if suffix is None:
        return False
    tokens = suffix.split()
    role = tokens[0] if tokens else ""
    if role in {"daemon", "bg-pty-host", "--bg-pty-host", "bg-spare", "--bg-spare"}:
        return False
    return not any(token == "-p" or token.startswith("--print") for token in tokens)


def _is_bg_pty_host(command: str) -> bool:
    suffix = _claude_command_suffix(command)
    role = suffix.split(None, 1)[0] if suffix else ""
    return role in {"bg-pty-host", "--bg-pty-host"}


def _snapshot_descendants(rows: Sequence[ProcessInfo], roots: Iterable[int]) -> set[int]:
    selected = set(roots)
    changed = True
    while changed:
        changed = False
        for process in rows:
            if process.ppid in selected and process.pid not in selected:
                selected.add(process.pid)
                changed = True
    return selected


def handoff_inventory(
    processes: Sequence[ProcessInfo],
    caller_pid: int,
    *,
    adoptions: Sequence[tuple[int, str]] = (),
) -> dict[str, Any]:
    """Classify owned and unowned handoff rows without signalling anything."""

    rows = [
        process
        for process in processes
        if "<defunct>" not in process.command.casefold()
    ]
    by_pid = {process.pid: process for process in rows}
    ancestry: list[ProcessInfo] = []
    seen: set[int] = set()
    cursor = caller_pid
    while cursor > 1 and cursor not in seen:
        seen.add(cursor)
        process = by_pid.get(cursor)
        if process is None:
            break
        ancestry.append(process)
        cursor = process.ppid
    candidates = [process for process in ancestry if _is_interactive_claude(process.command)]
    if not candidates:
        raise RuntimeError(
            "handoff-inventory must be run by the Terminal-hosted interactive magistrate"
        )
    interactive = candidates[-1]
    inventory_call_chain = {
        process.pid for process in ancestry if process.pid != interactive.pid
    }
    tree_pids = _snapshot_descendants(rows, (interactive.pid,))
    tree_pids.difference_update(inventory_call_chain)
    orphan_roots = {
        process.pid
        for process in rows
        if process.ppid == 1
        and (
            _is_bg_pty_host(process.command)
            or "/.claude/shell-snapshots/" in process.command.casefold()
        )
    }
    candidate_pids = _snapshot_descendants(rows, orphan_roots)
    candidate_pids.difference_update(tree_pids | inventory_call_chain)

    adopted_roots: set[int] = set()
    for pid, start_time in adoptions:
        process = by_pid.get(pid)
        if process is None:
            raise RuntimeError(f"adopted pid is absent: {pid}")
        if pid not in candidate_pids:
            raise RuntimeError(f"adopted pid is not an unclassified candidate: {pid}")
        if process.start_time != start_time:
            raise RuntimeError(
                f"adopted pid/start mismatch: pid={pid} expected={start_time!r} "
                f"observed={process.start_time!r}"
            )
        adopted_roots.add(pid)

    adopted_pids = _snapshot_descendants(rows, adopted_roots)
    adopted_pids.intersection_update(candidate_pids)
    owned_pids = tree_pids | adopted_pids
    remaining_candidates = candidate_pids - adopted_pids

    def record(process: ProcessInfo, provenance: str) -> dict[str, Any]:
        return {**dataclasses.asdict(process), "provenance": provenance}

    owned_rows = [process for process in rows if process.pid in owned_pids]
    owned_rows.sort(key=lambda process: process.pid)
    candidate_rows = [process for process in rows if process.pid in remaining_candidates]
    candidate_rows.sort(key=lambda process: process.pid)
    return {
        "schema": "joulewise.magistrate_handoff_inventory.v2",
        "interactive_pid": interactive.pid,
        "owned": [
            record(
                process,
                "explicit_adoption"
                if process.pid in adopted_roots
                else "adopted_descendant"
                if process.pid in adopted_pids
                else "interactive_ancestry",
            )
            for process in owned_rows
        ],
        "unclassified_candidates": [
            record(process, "command_shape_only") for process in candidate_rows
        ],
        "explicit_adoptions": [
            {"pid": pid, "start_time": start_time}
            for pid, start_time in sorted(adoptions)
        ],
    }


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


def decide(
    storage: Storage,
    deps: Dependencies,
    state: dict[str, Any],
    *,
    plan_snapshot: PlanSnapshot | None = None,
) -> Decision:
    wall = deps.wall_now().astimezone()
    monotonic = deps.monotonic()
    if clock_uncertain(state, wall, monotonic):
        return Decision("CLOCK_UNCERTAIN", "wall and monotonic deltas disagree")

    snapshot = plan_snapshot or load_plans(storage, now_epoch_s=wall.timestamp())
    plans = list(snapshot.plans)
    armed = armed_plans(plans, wall.timestamp(), storage)
    state["fenced_checkouts"] = fenced_checkout_rows(armed)
    if snapshot.errors:
        return Decision("HOLD_UNSAFE", "; ".join(snapshot.errors))
    conflicts = plan_conflicts(armed)
    if conflicts:
        return Decision("HOLD_UNSAFE", "plan_conflict: " + "; ".join(conflicts))

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
        "@@FENCED_CHECKOUTS@@": json.dumps(
            state.get("fenced_checkouts", fenced_checkout_rows(())),
            sort_keys=True,
            separators=(",", ":"),
        ),
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
        self.state["resident_session"] = None
        self.state["clock_drain"] = False
        self.state["resident_hold_drain"] = None
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
            self.state["resident_session"] = None
            self.state["clock_drain"] = False
            self.state["resident_hold_drain"] = None
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
        record_resident_start: bool = False,
    ) -> bool:
        self._write_request(None, now, reason=reason)
        resident_hold = self.state.get("resident_hold_drain")
        drain_state = dict(resident_hold) if isinstance(resident_hold, Mapping) else None
        if record_resident_start:
            self.storage.append_jsonl(
                self.storage.root / "events.jsonl",
                {
                    "schema": EVENT_SCHEMA,
                    "kind": "resident_drain_started",
                    "activation_id": self.state.get("activation_id"),
                    "activation_spawn_epoch_s": _activation_spawn_epoch_s(self.state),
                    "epoch_s": now.timestamp(),
                    "reason": reason,
                },
            )
            if drain_state is not None:
                drain_state["started"] = True
        requested = json.loads(self.storage.read_text(self.storage.root / "standdown.request"))
        try:
            requested_monotonic = float(requested["requested_monotonic"])
            elapsed = max(0.0, monotonic - requested_monotonic)
        except (KeyError, TypeError, ValueError):
            elapsed = max(0.0, now.timestamp() - float(requested["requested_epoch_s"]))
        if elapsed >= STOP_COOPERATIVE_S + STOP_TERM_GRACE_S:
            if drain_state is not None:
                drain_state["stage"] = "KILL"
                self.state["resident_hold_drain"] = drain_state
            owner = owned_process(self.lock_record, self.deps.processes.snapshot())
            if owner is None:
                return self._forced_hold(now)
            pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGKILL)
            self._record_signal(now, signal.SIGKILL, pids)
            return self._forced_hold(now)
        if (
            elapsed >= STOP_COOPERATIVE_S
            and self.state.get("standdown_phase") != "TERM"
            and (drain_state is None or drain_state.get("stage") != "TERM")
        ):
            owner = owned_process(self.lock_record, self.deps.processes.snapshot())
            if owner is None:
                return self._forced_hold(now)
            pids = signal_owned_tree(self.deps.processes, owner.pid, signal.SIGTERM)
            self._record_signal(now, signal.SIGTERM, pids)
            self.state["standdown_phase"] = "TERM"
            if drain_state is not None:
                drain_state["stage"] = "TERM"
        elif drain_state is not None and drain_state.get("stage") not in {"TERM", "KILL"}:
            drain_state["stage"] = "REQUEST"
        if drain_state is not None:
            self.state["resident_hold_drain"] = drain_state
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

        snapshot = load_plans(self.storage, now_epoch_s=now.timestamp())
        record_plan_diagnostics(
            self.storage,
            snapshot.diagnostics,
            activation_id=str(self.state.get("activation_id") or "pre-activation"),
            activation_spawn_epoch_s=_activation_spawn_epoch_s(self.state),
        )
        plans = list(snapshot.plans)
        armed = armed_plans(plans, now.timestamp(), self.storage)
        self.state["fenced_checkouts"] = fenced_checkout_rows(armed)
        conflicts = plan_conflicts(armed)
        resident_hold = self.state.get("resident_hold_drain")
        if isinstance(resident_hold, Mapping):
            return self._enforce_drain(
                now,
                monotonic,
                reason=str(resident_hold.get("reason", "durable unsafe-plan hold")),
                state_name="HOLD_UNSAFE",
                notice=(
                    str(resident_hold["notice"])
                    if resident_hold.get("notice") is not None
                    else None
                ),
                record_resident_start=not bool(resident_hold.get("started")),
            )
        if snapshot.errors or conflicts:
            reason = (
                "; ".join(snapshot.errors)
                if snapshot.errors
                else "plan_conflict: " + "; ".join(conflicts)
            )
            notice = "plan_conflict" if conflicts else None
            self.state["resident_hold_drain"] = {
                "reason": reason,
                "notice": notice,
                "stage": None,
                "started": False,
            }
            return self._enforce_drain(
                now,
                monotonic,
                reason=reason,
                state_name="HOLD_UNSAFE",
                notice=notice,
                record_resident_start=True,
            )

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
    activation_id = str(uuid.uuid4())
    activation_spawn_epoch_s = now.timestamp()
    state["activation_id"] = activation_id
    state["activation_spawn_epoch_s"] = activation_spawn_epoch_s
    state["resident_hold_drain"] = None
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
        "activation_spawn_epoch_s": activation_spawn_epoch_s,
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
        "activation_spawn_epoch_s": activation_spawn_epoch_s,
        "pid": child.pid,
        "start_time": process.start_time,
        "supervisor_pid": os.getpid(),
        "launch_epoch_s": now.timestamp(),
        "binary_symlink": str(binary),
        "binary_version": binary_version,
        "status": "ACTIVE",
    }
    storage.atomic_json(storage.root / "magistrate.lock", lock_record)
    state["resident_session"] = lock_record
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
    launch_epoch_s = lock_record.get(
        "activation_spawn_epoch_s", lock_record.get("launch_epoch_s")
    )
    if isinstance(launch_epoch_s, (int, float)) and not isinstance(launch_epoch_s, bool):
        state["activation_spawn_epoch_s"] = float(launch_epoch_s)
    state["resident_session"] = dict(lock_record)
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


def adopt_recorded_session_for_drain(
    storage: Storage,
    deps: Dependencies,
    state: dict[str, Any],
    *,
    reason: str,
    notice: str | None,
) -> ResidentSupervisor | None:
    """Adopt one state-recorded child for a single durable drain step."""

    recorded = state.get("resident_session")
    if not isinstance(recorded, Mapping) or recorded.get("schema") != LOCK_SCHEMA:
        return None
    lock_record = dict(recorded)
    pid = lock_record.get("pid")
    start_time = lock_record.get("start_time")
    activation = str(lock_record.get("activation_id") or state.get("activation_id"))
    owner = owned_process(lock_record, deps.processes.snapshot())
    now = deps.wall_now().astimezone()
    if owner is None:
        storage.append_jsonl(
            storage.root / "events.jsonl",
            {
                "schema": EVENT_SCHEMA,
                "kind": "already_gone",
                "pid": pid,
                "start_time": start_time,
                "activation": activation,
                "epoch_s": now.timestamp(),
            },
        )
        state["resident_session"] = None
        state["resident_hold_drain"] = {
            "reason": reason,
            "notice": notice,
            "stage": "already_gone",
            "started": False,
        }
        current_lock = read_lock(storage)
        if current_lock == lock_record:
            storage.unlink(storage.root / "magistrate.lock")
        storage.atomic_json(storage.root / "state.json", state)
        return None

    state["activation_id"] = activation
    launch_epoch_s = lock_record.get(
        "activation_spawn_epoch_s", lock_record.get("launch_epoch_s")
    )
    if isinstance(launch_epoch_s, (int, float)) and not isinstance(launch_epoch_s, bool):
        state["activation_spawn_epoch_s"] = float(launch_epoch_s)
    resident_hold = state.get("resident_hold_drain")
    if not isinstance(resident_hold, Mapping) or resident_hold.get("stage") == "already_gone":
        state["resident_hold_drain"] = {
            "reason": reason,
            "notice": notice,
            "stage": None,
            "started": False,
        }
    storage.append_jsonl(
        storage.root / "events.jsonl",
        {
            "schema": EVENT_SCHEMA,
            "kind": "resident_adopted",
            "pid": owner.pid,
            "start_time": owner.start_time,
            "activation": activation,
            "activation_id": activation,
            "epoch_s": now.timestamp(),
        },
    )
    attempt = int(state.get("attempt", 1) or 1)
    attempt_dir = storage.root / "attempts" / activation
    return ResidentSupervisor(
        storage,
        deps,
        state,
        AdoptedChild(deps.processes, lock_record),
        lock_record,
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
    observed_wall = deps.wall_now().astimezone()
    snapshot = load_plans(storage, now_epoch_s=observed_wall.timestamp())
    record_plan_diagnostics(
        storage,
        snapshot.diagnostics,
        activation_id=str(state.get("activation_id") or "pre-activation"),
        activation_spawn_epoch_s=_activation_spawn_epoch_s(state),
    )
    decision = decide(storage, deps, state, plan_snapshot=snapshot)
    now = deps.wall_now().astimezone()
    notice = None
    if decision.state in {"CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN", "HOLD_CENSUS"}:
        notice = decision.state.lower()
    elif decision.reason.startswith("plan_conflict:"):
        notice = "plan_conflict"
    transition(storage, state, decision.state, decision.reason, now, notice=notice)
    storage.atomic_json(storage.root / "state.json", state)
    if dry_run:
        return decision
    if decision.state == "HOLD_UNSAFE":
        supervisor = adopt_recorded_session_for_drain(
            storage,
            deps,
            state,
            reason=decision.reason,
            notice=notice,
        )
        if supervisor is not None:
            supervisor.step()
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
    parser.add_argument(
        "command",
        nargs="?",
        choices=("tick", "handoff-inventory"),
        default="tick",
        help="run one watchdog tick or print the read-only install-handoff PID inventory",
    )
    parser.add_argument("--dry-run", action="store_true", help="print decisions and suppress writes/spawn")
    parser.add_argument(
        "--custody-root",
        type=Path,
        default=Path(os.environ.get(CUSTODY_ROOT_ENV, str(DEFAULT_CUSTODY_ROOT))),
    )
    parser.add_argument(
        "--adopt-pid",
        action="append",
        type=int,
        default=[],
        help="handoff-inventory only: explicitly adopt one candidate PID",
    )
    parser.add_argument(
        "--start",
        action="append",
        default=[],
        help="handoff-inventory only: exact start token paired with --adopt-pid",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "handoff-inventory":
        if len(args.adopt_pid) != len(args.start):
            print(
                "handoff-inventory failed: each --adopt-pid requires one --start",
                file=sys.stderr,
            )
            return 3
        try:
            inventory = handoff_inventory(
                RealProcessTable().snapshot(),
                os.getpid(),
                adoptions=tuple(zip(args.adopt_pid, args.start)),
            )
        except Exception as exc:
            print(f"handoff-inventory failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3
        print(json.dumps(inventory, sort_keys=True, indent=2))
        return 0
    if args.adopt_pid or args.start:
        print("--adopt-pid/--start require handoff-inventory", file=sys.stderr)
        return 3
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
