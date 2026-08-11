"""Owned writer execution for calibration witness tests.

Every process started here owns a fresh session/process group, and every
writer thread is paired with a stop event.  The direct child's result is
captured first, then all descendants in the group are reaped; threads are
stopped and joined.  The module registries are deliberately observable so
unittest module cleanup can turn any missed teardown into a suite failure.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import stat
import subprocess
import sys
import threading
import time
from types import MappingProxyType
from typing import Any


CRASH_AUTHORIZATION_SCHEMA = "joulewise.test_writer_crash_authorization.v1"
_CRASH_STAGE_KEY = "JOULEWISE_TEST_WRITER_CRASH_STAGE"
_CRASH_TOKEN_KEY = "JOULEWISE_TEST_WRITER_CRASH_TOKEN"
_CRASH_CAPABILITY_ROOT_KEY = "JOULEWISE_TEST_WRITER_CRASH_CAPABILITY_ROOT"
_CRASH_AUTHORIZATION_ARGUMENT = "--test-writer-crash-authorization"
_OWNED_DESCENDANT_REGISTRY_KEY = "JOULEWISE_TEST_OWNED_DESCENDANT_REGISTRY"
_OWNED_FAKE_SAMPLER_SCHEMA = "joulewise.test_owned_fake_sampler.v1"
_PUBLIC_WRITER_NAMES = frozenset(
    {
        "reserve_calibration_window_bracket.py",
        "validate_powermetrics_fiducial.py",
    }
)


@dataclass(frozen=True)
class PublicExecutionEvidence:
    """Immutable evidence created only by :class:`OwnedPublicProcessRunner`."""

    refusal_code: str
    registered_surface: str
    resolved_entry_point: str
    argv: tuple[str, ...]
    cwd: str
    pid: int
    pgid: int
    start_order: int
    end_order: int
    returncode: int
    stdout_sha256: str
    stderr_sha256: str
    structured_events: tuple[Mapping[str, Any], ...]
    durable_postcondition: Mapping[str, Any]


@dataclass(frozen=True)
class OwnedProcessResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    pid: int
    pgid: int
    start_order: int
    end_order: int
    public_evidence: PublicExecutionEvidence | None = None


@dataclass(frozen=True)
class AuthenticatedProgress:
    """One monotonic progress token derived from owned writer artifacts."""

    ordinal: int
    stage: str
    authenticator: str = "owned-writer-filesystem-v1"


@dataclass
class _OwnedGroup:
    pgid: int
    child_pid: int
    label: str
    process: subprocess.Popen[str] | None = None


@dataclass
class _OwnedThread:
    thread: threading.Thread
    stop_event: threading.Event
    label: str
    error: BaseException | None = None


@dataclass(frozen=True)
class _OwnedFakeSampler:
    pid: int
    pgid: int
    sampler_path: str
    record_path: str


_REGISTRY_LOCK = threading.Lock()
_OWNED_PROCESS_GROUPS: dict[int, _OwnedGroup] = {}
_OWNED_THREADS: dict[int, _OwnedThread] = {}
_OWNED_FAKE_SAMPLERS: dict[int, _OwnedFakeSampler] = {}
_ORDER_LOCK = threading.Lock()
_ORDER = 0


def next_execution_order() -> int:
    """Return one process-wide monotonic evidence ordering token."""

    global _ORDER
    with _ORDER_LOCK:
        _ORDER += 1
        return _ORDER


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _forget_if_gone(pgid: int) -> bool:
    if _group_exists(pgid):
        return False
    with _REGISTRY_LOCK:
        _OWNED_PROCESS_GROUPS.pop(pgid, None)
    return True


def _poll_group_gone(pgid: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if _forget_if_gone(pgid):
            return True
        time.sleep(0.01)
    return _forget_if_gone(pgid)


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _owned_fake_sampler_exists(sampler: _OwnedFakeSampler) -> bool:
    try:
        return os.getpgid(sampler.pid) == sampler.pgid
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _poll_pid_gone(pid: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if not _pid_exists(pid):
            return True
        time.sleep(0.01)
    return not _pid_exists(pid)


def _terminate_owned_fake_sampler(
    sampler: _OwnedFakeSampler,
    *,
    grace_s: float = 0.5,
) -> None:
    """Boundedly terminate one fixture-registered sampler by exact PID."""

    if not _owned_fake_sampler_exists(sampler):
        return
    try:
        os.kill(sampler.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    if _poll_pid_gone(sampler.pid, grace_s):
        return
    try:
        os.kill(sampler.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    if not _poll_pid_gone(sampler.pid, max(2.0, grace_s)):
        raise RuntimeError(
            "owned fake sampler survived SIGKILL: "
            f"pid={sampler.pid} pgid={sampler.pgid} "
            f"path={sampler.sampler_path} record={sampler.record_path}"
        )


def owned_fake_sampler_survivors() -> tuple[_OwnedFakeSampler, ...]:
    """Return live fixture-registered samplers known to this test module."""

    with _REGISTRY_LOCK:
        candidates = tuple(_OWNED_FAKE_SAMPLERS.values())
    survivors = tuple(
        sampler for sampler in candidates if _owned_fake_sampler_exists(sampler)
    )
    dead = {sampler.pid for sampler in candidates} - {
        sampler.pid for sampler in survivors
    }
    if dead:
        with _REGISTRY_LOCK:
            for pid in dead:
                _OWNED_FAKE_SAMPLERS.pop(pid, None)
    return survivors


def assert_no_owned_fake_sampler_survivors() -> None:
    """Suite guard: fail loudly if any witness-owned fake sampler is alive."""

    survivors = owned_fake_sampler_survivors()
    if survivors:
        details = [
            {
                "pid": sampler.pid,
                "pgid": sampler.pgid,
                "sampler_path": sampler.sampler_path,
                "record_path": sampler.record_path,
            }
            for sampler in survivors
        ]
        raise AssertionError(f"owned fake-sampler survivors: {details!r}")


def _teardown_group(pgid: int, *, grace_s: float = 0.5) -> None:
    """Boundedly terminate a complete owned group and require ESRCH."""

    with _REGISTRY_LOCK:
        owned = _OWNED_PROCESS_GROUPS.get(pgid)

    def reap_direct_child() -> None:
        if owned is not None and owned.process is not None:
            try:
                owned.process.wait(timeout=grace_s)
            except subprocess.TimeoutExpired:
                pass

    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError) as exc:
        reap_direct_child()
        if _poll_group_gone(pgid, grace_s):
            return
        raise exc
    reap_direct_child()
    if _poll_group_gone(pgid, grace_s):
        return
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError) as exc:
        reap_direct_child()
        if _poll_group_gone(pgid, grace_s):
            return
        raise exc
    reap_direct_child()
    if not _poll_group_gone(pgid, max(2.0, grace_s)):
        raise RuntimeError(f"owned process group {pgid} survived SIGKILL")


def owned_process_group_survivors() -> tuple[int, ...]:
    """Return live registered groups, dropping registrations already at ESRCH."""

    with _REGISTRY_LOCK:
        candidates = tuple(_OWNED_PROCESS_GROUPS)
    return tuple(pgid for pgid in candidates if not _forget_if_gone(pgid))


def owned_thread_survivors() -> tuple[str, ...]:
    """Return live registered threads, dropping joined registrations."""

    with _REGISTRY_LOCK:
        candidates = tuple(_OWNED_THREADS.items())
    survivors: list[str] = []
    for token, owned in candidates:
        if owned.thread.is_alive():
            survivors.append(owned.label)
            continue
        owned.thread.join()
        with _REGISTRY_LOCK:
            _OWNED_THREADS.pop(token, None)
    return tuple(survivors)


def assert_no_owned_process_group_survivors() -> None:
    """Fail on any registered live group, but reap all of them first."""

    survivors = owned_process_group_survivors()
    for pgid in survivors:
        _teardown_group(pgid)
    if survivors:
        raise AssertionError(f"owned process-group survivors: {list(survivors)}")


def assert_no_owned_writer_survivors() -> None:
    """Stop and reap every registered writer, then fail if any was leaked."""

    with _REGISTRY_LOCK:
        threads = tuple(_OWNED_THREADS.values())
    for owned in threads:
        owned.stop_event.set()
    for owned in threads:
        owned.thread.join(timeout=5.0)
    thread_survivors = owned_thread_survivors()
    process_survivors = owned_process_group_survivors()
    for pgid in process_survivors:
        _teardown_group(pgid)
    if thread_survivors or process_survivors:
        raise AssertionError(
            "owned writer survivors: "
            f"threads={list(thread_survivors)}, "
            f"process_groups={list(process_survivors)}"
        )


def spawn_spinning_descendant_for_guard_test() -> subprocess.Popen[str]:
    """Create one intentionally uncontained owned group for the guard test."""

    code = (
        "import subprocess,sys,time; "
        "subprocess.Popen([sys.executable,'-c','while True: pass']); "
        "print('SPINNING', flush=True); time.sleep(60)"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", code],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    pgid = os.getpgid(process.pid)
    with _REGISTRY_LOCK:
        _OWNED_PROCESS_GROUPS[pgid] = _OwnedGroup(
            pgid=pgid,
            child_pid=process.pid,
            label="synthetic-spinning-descendant",
            process=process,
        )
    return process


def _structured_events(stdout: str, stderr: str) -> tuple[Mapping[str, Any], ...]:
    events: list[Mapping[str, Any]] = []
    for line in (stdout + "\n" + stderr).splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping):
            events.append(MappingProxyType(dict(value)))
    return tuple(events)


def _entry_point(argv: Sequence[str]) -> Path:
    if len(argv) < 2:
        raise ValueError("public process argv has no entry point")
    return Path(argv[1]).resolve(strict=True)


class OwnedPublicProcessRunner:
    """Start, wait for, and fully reap owned process groups and threads."""

    def __init__(self, temporary_root: Path) -> None:
        self.temporary_root = Path(temporary_root).resolve()
        self.capability_root = self.temporary_root / "owned-process-capabilities"
        self.capability_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.capability_root.chmod(0o700)
        self.descendant_registry = self.temporary_root / "owned-descendants"
        self.descendant_registry.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.descendant_registry.chmod(0o700)
        self.communicate_timeout_s = 600.0
        self._owned_pgids: set[int] = set()
        self._owned_threads: set[int] = set()
        self.observed_fake_sampler_pids: set[int] = set()
        # The post-fix valid-writer p99 is expected to remain well below 30 s.
        # A bounded same-runner yield probe lets a badly oversubscribed worker
        # enlarge the idle allowance without making elapsed host time create
        # more fixture work.  The consult clamps this range to 120..480 s.
        probe_started = time.monotonic()
        for _ in range(64):
            time.sleep(0)
        probe_s = time.monotonic() - probe_started
        self.writer_stage_idle_timeout_s = min(
            480.0,
            max(120.0, 4.0 * 30.0, probe_s * 2400.0),
        )

    def start_owned_thread(
        self,
        target: Callable[[threading.Event], None],
        *,
        label: str,
    ) -> threading.Thread:
        """Start a writer thread registered before it can mutate its root."""

        stop_event = threading.Event()
        owned: _OwnedThread

        def run_target() -> None:
            try:
                target(stop_event)
            except BaseException as exc:
                owned.error = exc

        thread = threading.Thread(
            target=run_target,
            name=f"joulewise-owned-{label}",
            daemon=True,
        )
        token = id(thread)
        owned = _OwnedThread(thread=thread, stop_event=stop_event, label=label)
        with _REGISTRY_LOCK:
            _OWNED_THREADS[token] = owned
        self._owned_threads.add(token)
        try:
            thread.start()
        except BaseException:
            with _REGISTRY_LOCK:
                _OWNED_THREADS.pop(token, None)
            self._owned_threads.discard(token)
            raise
        return thread

    def stop_owned_thread(
        self,
        thread: threading.Thread,
        *,
        timeout_s: float = 5.0,
    ) -> None:
        """Request stop, join, and surface failure for one owned thread."""

        token = id(thread)
        if token not in self._owned_threads:
            if thread.is_alive():
                raise AssertionError(
                    f"thread {thread.name!r} is not owned by this runner"
                )
            return
        with _REGISTRY_LOCK:
            owned = _OWNED_THREADS.get(token)
        if owned is None:
            raise AssertionError(f"owned thread {thread.name!r} lost its registration")
        owned.stop_event.set()
        thread.join(timeout=timeout_s)
        if thread.is_alive():
            raise AssertionError(f"owned writer thread {owned.label!r} did not stop")
        with _REGISTRY_LOCK:
            _OWNED_THREADS.pop(token, None)
        self._owned_threads.discard(token)
        if owned.error is not None:
            raise owned.error

    def start_owned(
        self,
        argv: Sequence[str | os.PathLike[str]],
        *,
        cwd: Path,
        env: Mapping[str, str],
        label: str,
    ) -> subprocess.Popen[str]:
        """Start an auxiliary process in the same ownership registry."""

        execution_env = dict(env)
        execution_env[_OWNED_DESCENDANT_REGISTRY_KEY] = str(
            self.descendant_registry
        )
        process = subprocess.Popen(
            [os.fspath(value) for value in argv],
            cwd=Path(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=execution_env,
            start_new_session=True,
        )
        pgid = os.getpgid(process.pid)
        if pgid != process.pid:
            process.kill()
            process.communicate()
            raise AssertionError(f"owned auxiliary pgid {pgid} != pid {process.pid}")
        with _REGISTRY_LOCK:
            _OWNED_PROCESS_GROUPS[pgid] = _OwnedGroup(
                pgid=pgid,
                child_pid=process.pid,
                label=label,
                process=process,
            )
        self._owned_pgids.add(pgid)
        return process

    def _registered_fake_samplers(self) -> tuple[_OwnedFakeSampler, ...]:
        samplers: list[_OwnedFakeSampler] = []
        for record in sorted(self.descendant_registry.glob("fake-sampler-*.json")):
            try:
                payload = json.loads(record.read_text(encoding="utf-8"))
                if payload.get("schema") != _OWNED_FAKE_SAMPLER_SCHEMA:
                    raise ValueError("unexpected schema")
                sampler = _OwnedFakeSampler(
                    pid=int(payload["pid"]),
                    pgid=int(payload["pgid"]),
                    sampler_path=str(Path(payload["sampler_path"]).resolve()),
                    record_path=str(record),
                )
                if sampler.pid <= 1 or sampler.pgid <= 1:
                    raise ValueError("unsafe pid or pgid")
                if Path(sampler.sampler_path).name != "fake_sampler.py":
                    raise ValueError("unexpected sampler fixture")
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                raise AssertionError(
                    f"invalid owned fake-sampler record {record}: {exc}"
                ) from exc
            samplers.append(sampler)
            self.observed_fake_sampler_pids.add(sampler.pid)
            with _REGISTRY_LOCK:
                _OWNED_FAKE_SAMPLERS[sampler.pid] = sampler
        return tuple(samplers)

    def reap_owned_fake_samplers(self) -> None:
        """Terminate every sampler explicitly registered to this runner."""

        samplers = self._registered_fake_samplers()
        for sampler in samplers:
            _terminate_owned_fake_sampler(sampler)
        survivors = tuple(
            sampler for sampler in samplers if _owned_fake_sampler_exists(sampler)
        )
        if survivors:
            raise AssertionError(
                "runner-owned fake samplers survived teardown: "
                f"{[(item.pid, item.pgid, item.sampler_path) for item in survivors]!r}"
            )
        for sampler in samplers:
            Path(sampler.record_path).unlink(missing_ok=True)
            with _REGISTRY_LOCK:
                _OWNED_FAKE_SAMPLERS.pop(sampler.pid, None)

    def terminate_owned(
        self,
        process: subprocess.Popen[str],
        *,
        timeout_s: float = 10.0,
    ) -> tuple[str, str]:
        """Kill, wait, prove ESRCH, and close pipes for one auxiliary group."""

        pgid = process.pid
        if pgid not in self._owned_pgids:
            if process.poll() is None:
                raise AssertionError(f"process {process.pid} is not owned by this runner")
            return "", ""
        _teardown_group(pgid, grace_s=min(0.5, timeout_s))
        try:
            stdout, stderr = process.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover - SIGKILL must reap
            raise AssertionError(f"owned process group {pgid} did not reap") from exc
        if not _forget_if_gone(pgid):
            raise AssertionError(f"owned process group {pgid} did not reach ESRCH")
        self._owned_pgids.discard(pgid)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()
        return stdout, stderr

    def close(self) -> None:
        """Stop and reap every writer owned by this runner."""

        errors: list[BaseException] = []
        with _REGISTRY_LOCK:
            owned_threads = tuple(
                _OWNED_THREADS[token]
                for token in self._owned_threads
                if token in _OWNED_THREADS
            )
        for owned in owned_threads:
            owned.stop_event.set()
        for pgid in tuple(self._owned_pgids):
            with _REGISTRY_LOCK:
                owned = _OWNED_PROCESS_GROUPS.get(pgid)
            try:
                _teardown_group(pgid)
                if owned is not None and owned.process is not None:
                    try:
                        owned.process.communicate(timeout=2.0)
                    except (subprocess.TimeoutExpired, OSError):
                        pass
                    if owned.process.stdout is not None:
                        owned.process.stdout.close()
                    if owned.process.stderr is not None:
                        owned.process.stderr.close()
                if not _forget_if_gone(pgid):
                    raise AssertionError(
                        f"owned process group {pgid} survived runner close"
                    )
            except BaseException as exc:  # close all groups before surfacing one
                errors.append(exc)
            finally:
                self._owned_pgids.discard(pgid)
        for token in tuple(self._owned_threads):
            with _REGISTRY_LOCK:
                owned = _OWNED_THREADS.get(token)
            if owned is None:
                errors.append(AssertionError(f"owned thread token {token} was lost"))
                self._owned_threads.discard(token)
                continue
            try:
                self.stop_owned_thread(owned.thread)
            except BaseException as exc:  # join all threads before surfacing one
                errors.append(exc)
        try:
            self.reap_owned_fake_samplers()
        except BaseException as exc:
            errors.append(exc)
        if self._owned_pgids:
            raise AssertionError(
                f"runner registry not empty after close: {sorted(self._owned_pgids)}"
            )
        if self._owned_threads:
            raise AssertionError(
                "runner thread registry not empty after close: "
                f"{sorted(self._owned_threads)}"
            )
        if errors:
            raise errors[0]

    def _crash_capability(self, *, stage: str, entry_point: Path) -> tuple[Path, str]:
        nonce = secrets.token_hex(32)
        capability = self.capability_root / f"crash-{secrets.token_hex(12)}.json"
        payload = {
            "schema_version": CRASH_AUTHORIZATION_SCHEMA,
            "nonce": nonce,
            "stage": stage,
            "entry_point": str(entry_point),
            "entry_point_sha256": hashlib.sha256(entry_point.read_bytes()).hexdigest(),
        }
        descriptor = os.open(
            capability,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            raw = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
            os.write(descriptor, raw)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        mode = stat.S_IMODE(capability.stat().st_mode)
        if mode != 0o600:
            raise AssertionError(f"crash capability mode is {mode:o}, expected 600")
        return capability, nonce

    def run(
        self,
        argv: Sequence[str | os.PathLike[str]],
        *,
        cwd: Path,
        env: Mapping[str, str],
        timeout: float | None = None,
        crash_stage: str | None = None,
        authorize_crash: bool = False,
        refusal_code: str | None = None,
        registered_surface: str | None = None,
        durable_postcondition: Callable[[], Mapping[str, Any]] | None = None,
        readiness_path: Path | None = None,
        readiness_timeout_s: float = 5.0,
        progress_probe: Callable[[], AuthenticatedProgress | None] | None = None,
        progress_reporter: Callable[[AuthenticatedProgress], None] | None = None,
        stage_idle_timeout_s: float | None = None,
    ) -> OwnedProcessResult:
        exact_argv = [os.fspath(value) for value in argv]
        execution_env = dict(env)
        execution_env.pop(_CRASH_TOKEN_KEY, None)
        execution_env.pop(_CRASH_CAPABILITY_ROOT_KEY, None)
        execution_env[_OWNED_DESCENDANT_REGISTRY_KEY] = str(
            self.descendant_registry
        )
        entry_point = _entry_point(exact_argv)
        capability: Path | None = None
        if crash_stage is not None:
            execution_env[_CRASH_STAGE_KEY] = crash_stage
        if authorize_crash:
            if crash_stage is None:
                raise ValueError("authorized crash requires an exact stage")
            if entry_point.name not in _PUBLIC_WRITER_NAMES:
                raise ValueError("crash capability is restricted to public writer surfaces")
            capability, nonce = self._crash_capability(
                stage=crash_stage,
                entry_point=entry_point,
            )
            exact_argv.extend([_CRASH_AUTHORIZATION_ARGUMENT, str(capability)])
            execution_env[_CRASH_TOKEN_KEY] = nonce
            execution_env[_CRASH_CAPABILITY_ROOT_KEY] = str(self.capability_root)

        process = subprocess.Popen(
            exact_argv,
            cwd=Path(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=execution_env,
            start_new_session=True,
        )
        pgid = os.getpgid(process.pid)
        if pgid != process.pid:
            process.kill()
            process.communicate()
            raise AssertionError(f"owned process pgid {pgid} != pid {process.pid}")
        with _REGISTRY_LOCK:
            _OWNED_PROCESS_GROUPS[pgid] = _OwnedGroup(
                pgid=pgid,
                child_pid=process.pid,
                label=entry_point.name,
                process=process,
            )
        self._owned_pgids.add(pgid)
        start_order = next_execution_order()
        try:
            if readiness_path is not None:
                readiness = Path(readiness_path)
                deadline = time.monotonic() + readiness_timeout_s
                while not readiness.exists():
                    if process.poll() is not None:
                        raise RuntimeError(
                            f"owned process exited before readiness path: {readiness}"
                        )
                    if time.monotonic() >= deadline:
                        raise subprocess.TimeoutExpired(
                            exact_argv, readiness_timeout_s
                        )
                    time.sleep(0.01)
            hard_ceiling_s = self.communicate_timeout_s if timeout is None else timeout
            hard_deadline = time.monotonic() + hard_ceiling_s
            idle_limit_s = (
                self.writer_stage_idle_timeout_s
                if stage_idle_timeout_s is None
                else min(480.0, max(120.0, stage_idle_timeout_s))
            )
            idle_deadline = time.monotonic() + idle_limit_s
            last_progress = -1
            while True:
                if progress_probe is not None:
                    update = progress_probe()
                    if update is not None:
                        if update.authenticator != "owned-writer-filesystem-v1":
                            raise AssertionError(
                                f"unauthenticated writer progress: {update.authenticator}"
                            )
                        if update.ordinal < last_progress:
                            raise AssertionError(
                                "writer progress regressed from "
                                f"{last_progress} to {update.ordinal}"
                            )
                        if update.ordinal > last_progress:
                            last_progress = update.ordinal
                            idle_deadline = time.monotonic() + idle_limit_s
                            if progress_reporter is not None:
                                progress_reporter(update)
                now = time.monotonic()
                if progress_probe is not None and now >= idle_deadline:
                    raise subprocess.TimeoutExpired(
                        exact_argv,
                        idle_limit_s,
                        output=f"writer stage stalled after ordinal {last_progress}",
                    )
                remaining = hard_deadline - now
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(exact_argv, hard_ceiling_s)
                try:
                    stdout, stderr = process.communicate(timeout=min(0.1, remaining))
                    break
                except subprocess.TimeoutExpired:
                    continue
            returncode = process.returncode
            if returncode is None:  # pragma: no cover - communicate guarantees this
                raise AssertionError("direct child has no return code after communicate")
        except BaseException:
            _teardown_group(pgid)
            try:
                process.communicate(timeout=2.0)
            except (subprocess.TimeoutExpired, OSError):
                pass
            raise
        finally:
            try:
                if process.returncode is not None:
                    _teardown_group(pgid)
                if _forget_if_gone(pgid):
                    self._owned_pgids.discard(pgid)
            finally:
                self.reap_owned_fake_samplers()
        end_order = next_execution_order()
        if capability is not None and capability.exists():
            raise AssertionError("writer did not consume one-use crash capability")

        evidence: PublicExecutionEvidence | None = None
        if refusal_code is not None or registered_surface is not None:
            if refusal_code is None or registered_surface is None:
                raise ValueError("public evidence requires refusal code and surface")
            postcondition = (
                durable_postcondition() if durable_postcondition is not None else {}
            )
            evidence = PublicExecutionEvidence(
                refusal_code=refusal_code,
                registered_surface=registered_surface,
                resolved_entry_point=str(entry_point),
                argv=tuple(exact_argv),
                cwd=str(Path(cwd).resolve()),
                pid=process.pid,
                pgid=pgid,
                start_order=start_order,
                end_order=end_order,
                returncode=returncode,
                stdout_sha256=hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
                stderr_sha256=hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
                structured_events=_structured_events(stdout, stderr),
                durable_postcondition=MappingProxyType(dict(postcondition)),
            )
        return OwnedProcessResult(
            args=tuple(exact_argv),
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            pid=process.pid,
            pgid=pgid,
            start_order=start_order,
            end_order=end_order,
            public_evidence=evidence,
        )


__all__ = [
    "AuthenticatedProgress",
    "OwnedProcessResult",
    "OwnedPublicProcessRunner",
    "PublicExecutionEvidence",
    "assert_no_owned_process_group_survivors",
    "assert_no_owned_writer_survivors",
    "next_execution_order",
    "owned_process_group_survivors",
    "owned_thread_survivors",
    "spawn_spinning_descendant_for_guard_test",
]
