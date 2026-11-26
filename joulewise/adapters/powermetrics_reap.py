"""Reap and prove absent the root ``powermetrics`` a failed bounded capture leaves (RL-91).

``PowermetricsTelemetryAdapter._run_bounded_capture`` and ``_probe_capability``
run the privilege prefix plus ``/usr/bin/powermetrics`` through ``subprocess.run(timeout=...)``.
On a timeout (or any exception inside ``subprocess.run``) the standard library
SIGKILLs the privilege wrapper, which cannot relay SIGKILL, so the root ``powermetrics`` it
started is orphaned and keeps sampling into the members that follow, unrecorded.
A non-root ``killpg`` gets EPERM on it, and with no tty the wrapper's ``use_pty`` does
not move it out of the caller's process group.

The estimator file ``joulewise/adapters/powermetrics.py`` is pinned by the issued
calibration acceptance (``ESTIMATOR_CODE_PATHS``; RL-58), so the fix lives in this
subclass and leaves those bytes untouched. The normal path is the parent's,
unchanged: this class adds work only after the parent has raised (bounded
capture) or reported a probe timeout.

After such a failure the subclass:

1. identifies the capture's own sampler precisely: a process whose command line
   holds the adapter's executable and ``-o <this capture's unique temp path>``.
   Another sampler (the night's sidecar, another member's capture) has another
   output path and is never signalled;
2. signals each one through the privileged signaller (default ``KILL_PREFIX``):
   SIGINT first so powermetrics flushes, then SIGTERM, then SIGKILL, re-reading the
   process table before every signal so only a pid still matching is signalled;
3. proves absence with a successful process census that lists this process's own
   pid (so an empty or garbled table is never read as "absent") and no matching
   sampler;
4. records the reap under ``device_metadata["capture_reaps"]`` either way. When
   absence is proven the original exception (or probe result) stands. When it is
   not, it raises :class:`PowermetricsOrphanRefusal` and every later capture,
   probe or sampling start of any adapter in this process refuses with the same
   reason, so no member measures beside an unproven root sampler.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.interfaces import AdapterFailure, AdapterResult, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason

REAP_SCHEMA = "joulewise.powermetrics_capture_reap.v1"
KILL_PREFIX = ("sudo", "-n", "/bin/kill")
CENSUS_ARGV = ("/bin/ps", "-axww", "-o", "pid=,command=")
CENSUS_TIMEOUT_S = 5.0
SIGNAL_TIMEOUT_S = 5.0
REAP_GRACE_S = 2.0
REAP_POLL_S = 0.1
REAP_SIGNALS = (("INT", signal.SIGINT), ("TERM", signal.SIGTERM), ("KILL", signal.SIGKILL))

# Process-wide: an orphan this process could not prove gone poisons every later
# capture in it, whichever adapter instance a later member resolves.
UNPROVEN_REAPS: list[dict[str, Any]] = []


class PowermetricsOrphanRefusal(AdapterFailure):
    """A failed capture's root powermetrics could not be proven gone."""


def _default_run(argv: Sequence[str], timeout_s: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(argv), capture_output=True, text=True, timeout=timeout_s, check=False)


def _refusal_message(record: dict[str, Any]) -> str:
    return ("powermetrics capture sampler not proven absent after a failed capture (RL-91): "
            f"{record.get('reason')}; capture {record.get('capture_path')}; pids {record.get('remaining')}")


class ReapingPowermetricsTelemetryAdapter(PowermetricsTelemetryAdapter):
    """``PowermetricsTelemetryAdapter`` that reaps a failed capture's root sampler."""

    def __init__(
        self,
        *args: Any,
        kill_prefix: tuple[str, ...] = KILL_PREFIX,
        census_argv: tuple[str, ...] = CENSUS_ARGV,
        reap_run: Callable[[Sequence[str], float], Any] | None = None,
        reap_grace_s: float = REAP_GRACE_S,
        reap_sleep: Callable[[float], None] | None = None,
        reap_monotonic: Callable[[], float] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._kill_prefix = tuple(kill_prefix)
        self._census_argv = tuple(census_argv)
        self._reap_run = reap_run if reap_run is not None else _default_run
        self._reap_grace_s = float(reap_grace_s)
        self._reap_sleep = reap_sleep if reap_sleep is not None else time.sleep
        self._reap_monotonic = reap_monotonic if reap_monotonic is not None else time.monotonic
        self._bounded_output_path: Path | None = None
        self._probe_output_path: Path | None = None

    # -- capture identity ---------------------------------------------------
    def _command(self, config, output_path, *, count, interval_ms=None):  # type: ignore[override]
        command = super()._command(config, output_path, count=count, interval_ms=interval_ms)
        if count is not None:
            self._bounded_output_path = Path(output_path)
        return command

    def _probe_command(self, output_path: Path) -> list[str]:
        self._probe_output_path = Path(output_path)
        return super()._probe_command(output_path)

    # -- guarded entry points -------------------------------------------------
    def _ensure_capability(self) -> AdapterResult:
        if UNPROVEN_REAPS:
            record = UNPROVEN_REAPS[0]
            return AdapterResult(ok=False, failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                                 message=_refusal_message(record), metadata={"capture_reap": dict(record)})
        result = super()._ensure_capability()
        return result

    def _probe_capability(self) -> AdapterResult:
        self._probe_output_path = None
        result = super()._probe_capability()
        probe = (self._device_metadata.get("powermetrics") or {}).get("samplers_probe")
        if probe == {"ok": False, "reason": "timeout"} and self._probe_output_path is not None:
            record = self._reap_capture(self._probe_output_path, artifact="capability_probe",
                                        trigger="TimeoutExpired")
            if not record["absent"]:
                return AdapterResult(ok=False, failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                                     message=_refusal_message(record), metadata={"capture_reap": dict(record)})
        return result

    def _run_bounded_capture(
        self,
        config: BenchmarkConfig,
        *,
        count: int,
        artifact_name: str,
        context: RunContext | None,
    ) -> bytes:
        if UNPROVEN_REAPS:
            record = UNPROVEN_REAPS[0]
            raise PowermetricsOrphanRefusal(FailureReason.TELEMETRY_UNAVAILABLE, _refusal_message(record),
                                            {"capture_reap": dict(record)})
        self._bounded_output_path = None
        try:
            return super()._run_bounded_capture(config, count=count, artifact_name=artifact_name,
                                                context=context)
        except BaseException as exc:
            output_path = self._bounded_output_path
            if output_path is not None:
                record = self._reap_capture(output_path, artifact=artifact_name, trigger=type(exc).__name__)
                if not record["absent"]:
                    raise PowermetricsOrphanRefusal(FailureReason.TELEMETRY_UNAVAILABLE,
                                                    _refusal_message(record),
                                                    {"capture_reap": dict(record)}) from exc
            raise

    # -- reap -------------------------------------------------------------------
    def _census(self, output_path: Path) -> tuple[list[int] | None, str | None]:
        """Pids of this capture's samplers, or ``(None, reason)`` when the census cannot answer."""

        try:
            completed = self._reap_run(self._census_argv, CENSUS_TIMEOUT_S)
        except Exception as exc:  # noqa: BLE001 - an unanswerable census is "not proven"
            return None, f"process census failed: {type(exc).__name__}: {exc}"
        if getattr(completed, "returncode", None) != 0:
            return None, f"process census exited {getattr(completed, 'returncode', None)}"
        stdout = completed.stdout
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if not isinstance(stdout, str):
            return None, "process census returned no text"
        marker = f" -o {output_path}"
        own = os.getpid()
        own_seen = False
        found = []
        for row in stdout.splitlines():
            parts = row.strip().split(None, 1)
            if not parts or not parts[0].isdigit():
                continue
            pid = int(parts[0])
            command = parts[1] if len(parts) > 1 else ""
            if pid == own:
                own_seen = True
                continue
            if self._executable in command and (command.endswith(marker) or marker + " " in command):
                found.append(pid)
        if not own_seen:
            return None, "process census did not list this process (table unreadable)"
        return sorted(found), None

    def _reap_capture(self, output_path: Path, *, artifact: str, trigger: str) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": REAP_SCHEMA, "artifact": artifact, "capture_path": str(output_path),
            "trigger": trigger, "executable": self._executable, "kill_prefix": list(self._kill_prefix),
            "found": [], "signals": [], "remaining": [], "absent": False, "reason": None,
        }
        pids, problem = self._census(output_path)
        if pids is not None:
            record["found"] = list(pids)
        for name, _signum in REAP_SIGNALS:
            if pids is None or not pids:
                break
            for pid in pids:
                argv = [*self._kill_prefix, f"-{name}", str(pid)]
                try:
                    completed = self._reap_run(argv, SIGNAL_TIMEOUT_S)
                    rc = getattr(completed, "returncode", None)
                except Exception as exc:  # noqa: BLE001 - recorded; absence is judged by census
                    rc = f"{type(exc).__name__}: {exc}"
                record["signals"].append({"pid": pid, "signal": name, "rc": rc})
            deadline = self._reap_monotonic() + self._reap_grace_s
            while True:
                pids, problem = self._census(output_path)
                if pids is None or not pids or self._reap_monotonic() >= deadline:
                    break
                self._reap_sleep(REAP_POLL_S)
        if pids is None:
            record["reason"] = problem
        elif pids:
            record["remaining"] = list(pids)
            record["reason"] = "sampler still running after INT, TERM and KILL"
        else:
            record["absent"] = True
        self._device_metadata.setdefault("capture_reaps", []).append(dict(record))
        if not record["absent"]:
            UNPROVEN_REAPS.append(dict(record))
        return record
