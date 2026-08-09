"""Owned public-process execution for calibration witness tests.

Every process started here owns a fresh session/process group.  The direct
child's result is captured first, then all descendants in the group are
reaped.  The module registry is deliberately observable so unittest module
cleanup can turn any missed teardown into a suite failure.
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


@dataclass
class _OwnedGroup:
    pgid: int
    child_pid: int
    label: str
    process: subprocess.Popen[str] | None = None


_REGISTRY_LOCK = threading.Lock()
_OWNED_PROCESS_GROUPS: dict[int, _OwnedGroup] = {}
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


def assert_no_owned_process_group_survivors() -> None:
    """Fail on any registered live group, but reap all of them first."""

    survivors = owned_process_group_survivors()
    for pgid in survivors:
        _teardown_group(pgid)
    if survivors:
        raise AssertionError(f"owned process-group survivors: {list(survivors)}")


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
    """Start, wait for, and fully reap public subprocess process groups."""

    def __init__(self, temporary_root: Path) -> None:
        self.temporary_root = Path(temporary_root).resolve()
        self.capability_root = self.temporary_root / "owned-process-capabilities"
        self.capability_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.capability_root.chmod(0o700)
        self.communicate_timeout_s = 120.0

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
    ) -> OwnedProcessResult:
        exact_argv = [os.fspath(value) for value in argv]
        execution_env = dict(env)
        execution_env.pop(_CRASH_TOKEN_KEY, None)
        execution_env.pop(_CRASH_CAPABILITY_ROOT_KEY, None)
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
            stdout, stderr = process.communicate(
                timeout=self.communicate_timeout_s if timeout is None else timeout
            )
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
            if process.returncode is not None:
                _teardown_group(pgid)
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
    "OwnedProcessResult",
    "OwnedPublicProcessRunner",
    "PublicExecutionEvidence",
    "assert_no_owned_process_group_survivors",
    "next_execution_order",
    "owned_process_group_survivors",
    "spawn_spinning_descendant_for_guard_test",
]
