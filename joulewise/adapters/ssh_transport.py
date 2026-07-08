"""SSH transport adapter for remote JouleWise nodes.

Slice 2K pins stdlib-only SSH/SCP subprocess transport (D-009), raw artifact
preservation (D-002), injected-clock metadata (D-003), and structured failure
taxonomy (D-012). The stream ledger entries B-4/B-5/B-7/B-8 bind the behavior
here: SSH destinations are opaque OpenSSH targets, transport failures report
``transport_unavailable``, and clock-alignment metadata is carried lazily after
the node-worker client records a marker.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Protocol

from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason

SSH_CONNECT_TIMEOUT_S = 10
SSH_COMMAND_TIMEOUT_S = 60
SCP_TIMEOUT_S = 60
STDERR_TAIL_CHARS = 1000

SSH_BINARY = "ssh"
SCP_BINARY = "scp"
SSH_OPTIONS = (
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=%d" % SSH_CONNECT_TIMEOUT_S,
)


@dataclass(frozen=True)
class RunnerCompleted:
    """Small subprocess result shape accepted by the injectable runner seam."""

    returncode: int
    stdout: bytes = b""
    stderr: bytes = b""


class Runner(Protocol):
    def __call__(self, argv: list[str], *, timeout: float) -> RunnerCompleted:
        """Run a command and return a subprocess-like result."""


def _default_runner(argv: list[str], *, timeout: float) -> RunnerCompleted:
    completed = subprocess.run(argv, capture_output=True, timeout=timeout)
    return RunnerCompleted(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _decode_tail(payload: bytes | str | None) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        text = payload
    else:
        text = payload.decode("utf-8", errors="replace")
    return text.strip()[-STDERR_TAIL_CHARS:]


def _decode_stdout(payload: bytes | str | None) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    return payload.decode("utf-8", errors="replace")


def _looks_like_ssh_transport_failure(returncode: int, stderr_tail: str) -> bool:
    if returncode == 255:
        return True
    lowered = stderr_tail.lower()
    needles = (
        "permission denied",
        "could not resolve hostname",
        "connection timed out",
        "connection refused",
        "no route to host",
        "host key verification failed",
        "connection closed",
        "connection reset",
        "operation timed out",
    )
    return any(needle in lowered for needle in needles)


class SshTransport:
    """``TransportAdapter`` implementation backed by OpenSSH subprocesses."""

    name = "ssh"

    def __init__(
        self,
        clock: Clock,
        destination: str,
        *,
        runner: Runner | None = None,
        command_timeout_s: float = SSH_COMMAND_TIMEOUT_S,
        file_timeout_s: float = SCP_TIMEOUT_S,
    ) -> None:
        self.clock = clock
        self.destination = destination
        self.runner = runner or _default_runner
        self.command_timeout_s = float(command_timeout_s)
        self.file_timeout_s = float(file_timeout_s)
        self._clock_alignment: dict | None = None

    def connection_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict:
        metadata = {"transport": self.name, "host": self.destination}
        if self._clock_alignment is not None:
            metadata["clock_alignment"] = self._clock_alignment
        return metadata

    def record_clock_alignment(self, alignment: dict) -> None:
        self._clock_alignment = dict(alignment)

    def run_command(
        self,
        config: BenchmarkConfig,
        command: list[str],
        context: RunContext | None = None,
    ) -> AdapterResult:
        return self.run(command, timeout_s=self.command_timeout_s)

    def collect_artifact(
        self,
        config: BenchmarkConfig,
        source: str,
        destination: str,
        context: RunContext | None = None,
    ) -> AdapterResult:
        return self.collect(source, destination, timeout_s=self.file_timeout_s)

    def put_file(
        self,
        source: str,
        destination: str,
        *,
        timeout_s: float | None = None,
    ) -> AdapterResult:
        argv = self._scp_argv(source, self._remote_spec(destination), recursive=False)
        return self._run_file_transfer(argv, "put", timeout_s or self.file_timeout_s)

    def collect(
        self,
        source: str,
        destination: str,
        *,
        timeout_s: float | None = None,
    ) -> AdapterResult:
        argv = self._scp_argv(self._remote_spec(source), destination, recursive=True)
        return self._run_file_transfer(argv, "collect", timeout_s or self.file_timeout_s)

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        argv = self._ssh_argv(command)
        timeout = timeout_s or self.command_timeout_s
        try:
            completed = self.runner(argv, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="ssh command timed out after %.3fs: %s" % (timeout, exc),
                metadata={"ssh_error_class": "timeout"},
            )
        except OSError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="ssh command could not run: %s" % exc,
                metadata={"ssh_error_class": exc.__class__.__name__},
            )

        stdout = _decode_stdout(completed.stdout)
        stderr_tail = _decode_tail(completed.stderr)
        metadata = {
            "returncode": completed.returncode,
            "stdout": stdout,
            "stderr_tail": stderr_tail,
        }
        if completed.returncode == 0:
            return AdapterResult(ok=True, metadata=metadata)
        if _looks_like_ssh_transport_failure(completed.returncode, stderr_tail):
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=stderr_tail
                or "ssh command failed with returncode %d" % completed.returncode,
                metadata={**metadata, "ssh_error_class": "ssh_transport"},
            )
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message=stderr_tail
            or "remote command exited with returncode %d and empty stderr"
            % completed.returncode,
            metadata=metadata,
        )

    def _run_file_transfer(
        self, argv: list[str], operation: str, timeout_s: float
    ) -> AdapterResult:
        try:
            completed = self.runner(argv, timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="scp %s timed out after %.3fs: %s" % (operation, timeout_s, exc),
                metadata={"ssh_error_class": "timeout"},
            )
        except OSError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="scp %s could not run: %s" % (operation, exc),
                metadata={"ssh_error_class": exc.__class__.__name__},
            )

        stderr_tail = _decode_tail(completed.stderr)
        metadata = {
            "returncode": completed.returncode,
            "stdout": _decode_stdout(completed.stdout),
            "stderr_tail": stderr_tail,
        }
        if completed.returncode == 0:
            return AdapterResult(ok=True, metadata=metadata)
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
            message=stderr_tail
            or "scp %s failed with returncode %d" % (operation, completed.returncode),
            metadata={**metadata, "ssh_error_class": "scp"},
        )

    def _ssh_argv(self, command: list[str]) -> list[str]:
        return [SSH_BINARY, *SSH_OPTIONS, self.destination, "--", *command]

    def _scp_argv(self, source: str, destination: str, *, recursive: bool) -> list[str]:
        argv = [SCP_BINARY, *SSH_OPTIONS]
        if recursive:
            argv.append("-r")
        argv.extend(["--", source, destination])
        return argv

    def _remote_spec(self, remote_path: str) -> str:
        return "%s:%s" % (self.destination, remote_path)
