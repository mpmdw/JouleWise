"""Local transport adapter (decisions D-002, D-009).

Runs commands and collects artifacts on the controller host itself - the
degenerate transport for local targets such as the Mac vertical slice. Real
remote work (commands, file collection) happens over the SSH transport in
Slice 2K; both satisfy the same ``TransportAdapter`` protocol so the
controller composes them interchangeably. Subprocess execution failures map
to structured ``AdapterResult`` failures, never exceptions, matching the
stdlib-only structured-failure policy (D-009).
"""

from __future__ import annotations

import shutil
import subprocess

from joulewise.interfaces import AdapterResult, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason

#: Hard cap on local command duration; a hung command becomes a structured
#: transport failure instead of wedging the controller.
COMMAND_TIMEOUT_S = 60

_STDERR_TAIL_CHARS = 1000


def _stderr_tail(stderr: bytes) -> str:
    text = stderr.decode("utf-8", errors="replace").strip()
    return text[-_STDERR_TAIL_CHARS:]


class LocalTransport:
    """``TransportAdapter`` implementation for the controller host."""

    name = "local"

    def connection_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict:
        return {"transport": "local", "host": "localhost"}

    def run_command(
        self,
        config: BenchmarkConfig,
        command: list[str],
        context: RunContext | None = None,
    ) -> AdapterResult:
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                timeout=COMMAND_TIMEOUT_S,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=f"local command {command!r} could not run: {exc}",
            )
        if completed.returncode == 0:
            return AdapterResult(ok=True, metadata={"returncode": 0})
        tail = _stderr_tail(completed.stderr)
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message=tail
            or f"local command {command!r} exited with returncode {completed.returncode} and empty stderr",
            metadata={"returncode": completed.returncode},
        )

    def collect_artifact(
        self,
        config: BenchmarkConfig,
        source: str,
        destination: str,
        context: RunContext | None = None,
    ) -> AdapterResult:
        try:
            copied_to = shutil.copy2(source, destination)
        except OSError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=f"could not collect artifact {source!r} -> {destination!r}: {exc}",
            )
        return AdapterResult(
            ok=True,
            metadata={"source": source, "destination": str(copied_to)},
        )
