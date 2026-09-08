#!/usr/bin/env python3
"""Run one gated unattended G2-a night, or its reporting courier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
import math
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


# A LaunchAgent starts this file by absolute path with a minimal environment.
# Make the checkout importable before importing any project module.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) in sys.path:
    sys.path.remove(str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from joulewise import night_gate
from joulewise.measurement_liveness import observe_identity  # noqa: E402

from joulewise.night_gate import (  # noqa: E402
    NIGHT_DRIVER_REASON_CODES,
    NIGHT_GATE_REASON_CODES,
    NightPlan,
    PlanError,
    ProbeResult,
    Probes,
    agent_census,
    evaluate_night,
)


RESULT_SCHEMA = "joulewise.unattended_night_result.v1"
REFUSAL_SCHEMA = "joulewise.night_refusal.v1"
PROBE_TIMEOUT_S = 30
CENSUS_INTERVAL_S = 30
# R-7: min(600, max(3 * (5303 ms / 1000), 300)) from cold_start.json.
COURIER_DEADLINE_S = 300
COURIER_BACKOFF_S = (60, 180, 600)
COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)
DEADMAN_HOUR = 7
DEADMAN_MINUTE = 0
COURIER_ALLOWED_TOOLS = (
    "Read,Glob,Grep,Bash,Edit,Write,mcp__claude_ai_Gmail__send_message"
)

EXIT_GO = 0
EXIT_REFUSED = 3
EXIT_ABORTED = 4
EXIT_CHAIN_FAILED = 5
EXIT_COURIER_FAILED = 6

_WRITE_ONCE_RECORDS = (
    "receipt.json",
    "go_receipt.json",
    "go-census.json",
    "result.json",
    "refusal.json",
    "chain.started",
    "chain.exited",
    "courier.json",
)


def _build_code_map(codes: set[str] | frozenset[str]) -> dict[str, str]:
    invalid = sorted(code for code in codes if not code.startswith("night_"))
    if invalid:
        raise RuntimeError(f"night reason-code registry has invalid members: {invalid!r}")
    return {code[6:]: code for code in codes}


_CODES = _build_code_map({code for code in NIGHT_GATE_REASON_CODES | NIGHT_DRIVER_REASON_CODES if code.startswith("night_")})


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_SHA256_HEX_RE = re.compile(r"[0-9a-f]{64}")


def _sidecar_digest(sidecar_text: str, chain_basename: str) -> str | None:
    """Return a strict ``shasum``-form digest, or None when malformed."""

    tokens = sidecar_text.split()
    if not tokens or len(tokens) > 2:
        return None
    if _SHA256_HEX_RE.fullmatch(tokens[0]) is None:
        return None
    if len(tokens) == 2 and tokens[1] != chain_basename:
        return None
    return tokens[0]


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(descriptor, payload[offset:])
        if written <= 0:
            raise OSError("could not write record")
        offset += written
    os.fsync(descriptor)


def _write_bytes_exclusive(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        _write_all(descriptor, payload)
    finally:
        os.close(descriptor)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    _write_bytes_exclusive(path, _json_bytes(value))


def _fsync_path(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _append_log(custody_root: Path, message: str) -> None:
    stamp = datetime.now().astimezone().isoformat()
    with (custody_root / "night.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def _refusal_mapping(reason: str, detail: str, evidence: Any = None) -> dict[str, Any]:
    return {"reason": reason, "detail": detail, "evidence": evidence}


def _json_value(value: Any) -> Any:
    if isinstance(value, ProbeResult):
        return {
            "argv": list(value.argv),
            "exit_code": value.exit_code,
            "stdout": value.stdout,
            "stderr": value.stderr,
            "monotonic_ns": value.monotonic_ns,
        }
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _refusal_from_object(refusal: Any) -> dict[str, Any] | None:
    if refusal is None:
        return None
    if isinstance(refusal, Mapping):
        return _json_value(refusal)
    return {
        "reason": getattr(refusal, "reason", None),
        "detail": getattr(refusal, "detail", None),
        "evidence": _json_value(getattr(refusal, "evidence", None)),
    }


def validate_refusal(value: Mapping[str, object]) -> list[str]:
    """Validate one driver-owned refusal document using exact key sets."""

    defects: list[str] = []
    expected = {"schema", "receipt_class", "plan_id", "verdict", "refusal"}
    if not isinstance(value, Mapping):
        return ["refusal: must be an object"]
    if set(value) != expected:
        defects.append("refusal: keys must match the driver refusal schema exactly")
    if value.get("schema") != REFUSAL_SCHEMA:
        defects.append(f"schema: must be {REFUSAL_SCHEMA}")
    if value.get("receipt_class") not in {
        "DIAGNOSTIC_NO_PACK",
        "REHEARSAL_STUB",
        "TRANSACTION_PACK",
    }:
        defects.append("receipt_class: invalid")
    if not isinstance(value.get("plan_id"), str) or not value.get("plan_id"):
        defects.append("plan_id: must be a non-empty string")
    if value.get("verdict") != "REFUSED":
        defects.append("verdict: must be REFUSED")
    refusal = value.get("refusal")
    if not isinstance(refusal, Mapping):
        defects.append("refusal.refusal: must be an object")
        return defects
    if set(refusal) != {"reason", "detail", "evidence"}:
        defects.append("refusal.refusal: keys must match exactly")
    reason = refusal.get("reason")
    if reason not in NIGHT_DRIVER_REASON_CODES | NIGHT_GATE_REASON_CODES:
        defects.append("refusal.reason: is not registered")
    if not isinstance(refusal.get("detail"), str) or not refusal.get("detail"):
        defects.append("refusal.detail: must be a non-empty string")
    return defects


def _write_driver_refusal(
    path: Path, plan: NightPlan, reason: str, detail: str, evidence: Any = None
) -> dict[str, Any]:
    refusal = _refusal_mapping(reason, detail, evidence)
    document = {
        "schema": REFUSAL_SCHEMA,
        "receipt_class": plan.receipt_class,
        "plan_id": plan.plan_id,
        "verdict": "REFUSED",
        "refusal": refusal,
    }
    defects = validate_refusal(document)
    if defects:
        raise ValueError(f"invalid driver refusal: {defects!r}")
    _write_json(path, document)
    return refusal


def _write_gate_refusal(path: Path, receipt: Any) -> None:
    _write_bytes_exclusive(path, receipt.to_json_bytes())


def _probe_runner(argv: tuple[str, ...] | list[str]) -> ProbeResult:
    """Run a gate probe without allowing an unbounded child process."""

    started = time.monotonic_ns()
    command = tuple(str(part) for part in argv)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_S,
            check=False,
        )
        return ProbeResult(
            argv=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            monotonic_ns=time.monotonic_ns(),
        )
    except subprocess.TimeoutExpired as error:
        return ProbeResult(
            argv=command,
            exit_code=124,
            stdout=error.stdout or "",
            stderr=(error.stderr or "") + f"ProbeError: timeout after {PROBE_TIMEOUT_S} s",
            monotonic_ns=time.monotonic_ns(),
        )
    except OSError as error:
        return ProbeResult(
            argv=command,
            exit_code=127,
            stdout="",
            stderr=f"ProbeError: {error}",
            monotonic_ns=max(started, time.monotonic_ns()),
        )


def make_probes() -> Probes:
    """Build the production probe bundle used by the pure night gate."""

    def checkout_head() -> str:
        result = _probe_runner(("git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"))
        if result.exit_code != 0:
            raise RuntimeError(f"checkout head probe failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def measurement_head(root: str) -> str:
        result = _probe_runner(("git", "-C", root, "rev-parse", "HEAD"))
        if result.exit_code != 0:
            raise RuntimeError(
                f"measurement head probe failed for {root}: {result.stderr.strip()}"
            )
        return result.stdout.strip()

    return Probes(
        run=_probe_runner,
        now_epoch_s=time.time,
        monotonic_ns=time.monotonic_ns,
        read_text=lambda path: Path(path).read_text(encoding="utf-8"),
        checkout_head=checkout_head,
        measurement_head=measurement_head,
    )


def _census_record(probe: ProbeResult, refusal: Any) -> dict[str, Any]:
    return {
        "argv": list(probe.argv),
        "exit_code": probe.exit_code,
        "stdout": probe.stdout,
        "stderr": probe.stderr,
        "monotonic_ns": probe.monotonic_ns,
        "refusal": _refusal_from_object(refusal),
    }


def _append_census(path: Path, probe: ProbeResult, refusal: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_census_record(probe, refusal), sort_keys=True) + "\n")


def _record_chain_exit(
    night_dir: Path,
    exit_code: int | None,
    *,
    reaped_by: str | None = None,
    launch_failed: bool = False,
) -> None:
    record: dict[str, Any] = {
        "exit_code": exit_code,
        "epoch_s": time.time(),
        "monotonic_ns": time.monotonic_ns(),
    }
    if reaped_by is not None:
        record["reaped_by"] = reaped_by
    if launch_failed:
        record["launch_failed"] = True
    _write_json(night_dir / "chain.exited", record)


def _terminate_process_group(
    process: subprocess.Popen[Any],
    night_dir: Path | None = None,
    *,
    pgid: int | None = None,
) -> bool:
    """Return True only when wait() proves that the child session exited."""

    process_group = process.pid if pgid is None else pgid
    try:
        os.killpg(process_group, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        exit_code = process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process_group, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            exit_code = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            return False
    if night_dir is not None:
        _record_chain_exit(night_dir, exit_code)
    return True


def _claim_chain_start(night_dir: Path) -> int | None:
    try:
        return os.open(
            night_dir / "chain.started",
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError:
        return None


def _complete_chain_start(descriptor: int, process: subprocess.Popen[Any],
                          night_dir: Path) -> int:
    # start_new_session=True makes the child the process-group leader.
    pgid = process.pid
    record = {"pid": process.pid, "pgid": pgid, "epoch_s": time.time()}
    try:
        # Publish the dead-man's complete identity before any subprocess probe.
        _write_all(descriptor, _json_bytes(record))
    finally:
        os.close(descriptor)
    identity = observe_identity(process.pid)
    record["start_time"] = identity.start_time if identity.state == "LIVE" else None
    temporary = night_dir / "chain.started.tmp"
    _write_json(temporary, record)
    os.replace(temporary, night_dir / "chain.started")
    return pgid


def _complete_chain_launch_failure(descriptor: int, error: OSError) -> str:
    launch_error = f"{type(error).__name__}: {error}"
    try:
        _write_all(
            descriptor,
            _json_bytes(
                {
                    "pid": None,
                    "pgid": None,
                    "epoch_s": time.time(),
                    "launch_error": launch_error,
                }
            ),
        )
    finally:
        os.close(descriptor)
    return launch_error


def _run_chain_once(
    chain_path: Path,
    plan: NightPlan,
    probes: Probes,
    night_dir: Path,
    claim_descriptor: int,
    *,
    command: list[str] | None = None,
    abort_on_census: bool = True,
) -> tuple[int | None, dict[str, Any] | None, int, list[dict[str, Any]], bool]:
    """Run exactly one child session and continuously census it."""

    census_path = night_dir / "censuses.jsonl"
    stdout_path = night_dir / "chain.stdout.log"
    stderr_path = night_dir / "chain.stderr.log"
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        environment = os.environ.copy()
        environment["NIGHT_PLAN_ID"] = plan.plan_id
        environment["MEASUREMENT_ROOT"] = plan.measurement_root
        environment["MEASUREMENT_HEAD"] = plan.measurement_head
        # The exact v2 schema has no interpreter field; use the clone's venv.
        environment["PY"] = f"{plan.measurement_root}/.venv/bin/python"
        try:
            process = subprocess.Popen(
                command if command is not None else ["/bin/zsh", str(chain_path)],
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                env=environment,
                start_new_session=True,
            )
        except OSError as error:
            launch_error = _complete_chain_launch_failure(claim_descriptor, error)
            _record_chain_exit(night_dir, None, launch_failed=True)
            return (
                None,
                _refusal_mapping(
                    _CODES["chain_launch_failed"],
                    "night chain process could not be launched",
                    {"launch_error": launch_error},
                ),
                0,
                [],
                True,
            )
        pgid = _complete_chain_start(claim_descriptor, process, night_dir)
        census_count = 0
        census_hits: list[dict[str, Any]] = []
        next_census = time.monotonic()
        while process.poll() is None:
            now = time.monotonic()
            if now >= next_census:
                probe, refusal = agent_census(probes)
                record = _census_record(probe, refusal)
                _append_census(census_path, probe, refusal)
                census_count += 1
                if refusal is not None:
                    census_hits.append(record)
                    if abort_on_census:
                        proven = _terminate_process_group(
                            process, night_dir, pgid=pgid
                        )
                        if not proven:
                            _write_json(
                                night_dir / "chain.unkilled",
                                {"pgid": pgid, "epoch_s": time.time()},
                            )
                            return (
                                process.poll(),
                                _refusal_mapping(
                                    _CODES["chain_alive"],
                                    "process-group termination could not be proven",
                                    record,
                                ),
                                census_count,
                                census_hits,
                                False,
                            )
                        return (
                            process.poll(),
                            _refusal_mapping(
                                _CODES["aborted_agent_present"],
                                "agent census refused while the chain was running",
                                record,
                            ),
                            census_count,
                            census_hits,
                            True,
                        )
                next_census = now + CENSUS_INTERVAL_S
            time.sleep(min(1.0, max(0.01, next_census - time.monotonic())))
        exit_code = process.wait()
        _record_chain_exit(night_dir, exit_code)
        return exit_code, None, census_count, census_hits, True


def _artifact_list(custody_root: Path, night_dir: Path) -> list[dict[str, str]]:
    paths = [
        custody_root / "night.log",
        night_dir / "receipt.json",
        night_dir / "go_receipt.json",
        night_dir / "go-census.json",
        night_dir / "refusal.json",
        night_dir / "result.json",
        night_dir / "chain.started",
        night_dir / "chain.exited",
        night_dir / "chain.unkilled",
        night_dir / "censuses.jsonl",
        night_dir / "chain.stdout.log",
        night_dir / "chain.stderr.log",
        night_dir / "courier.json",
        night_dir / "courier.attempts.jsonl",
        night_dir / "courier.heartbeat",
        night_dir / "courier.sent",
    ]
    return [
        {"path": str(path.relative_to(custody_root)), "sha256": _sha256_path(path)}
        for path in paths
        if path.is_file()
    ]


def _night_date(plan: NightPlan) -> str:
    # Use local time, like _next_deadman_epoch: one civil-time base for launchd.
    return datetime.fromtimestamp(plan.t0_epoch_s).strftime("%Y%m%d")


def _durable_record(custody_root: Path, night_dir: Path, plan: NightPlan) -> None:
    """Best-effort results-branch publish; failure is logged but never fatal."""

    try:
        origin = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.strip()
        clone = custody_root / "results-clone"
        if not clone.exists():
            subprocess.run(
                ["git", "clone", "--depth", "1", origin, str(clone)],
                capture_output=True,
                text=True,
                timeout=120,
                check=True,
            )
        branch = f"night-results/{_night_date(plan)}"
        subprocess.run(
            ["git", "-C", str(clone), "checkout", "-B", branch],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        destination = clone / "docs" / "process_traces" / "night-results" / _night_date(plan)
        destination.mkdir(parents=True, exist_ok=True)
        for artifact in _artifact_list(custody_root, night_dir):
            source = custody_root / artifact["path"]
            shutil.copy2(source, destination / source.name)
        subprocess.run(
            ["git", "-C", str(clone), "add", str(destination.relative_to(clone))],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(clone), "commit", "-m", f"record night {_night_date(plan)}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(clone), "push", "origin", f"HEAD:{branch}"],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        _append_log(custody_root, f"durable record pushed branch={branch}")
    except (OSError, subprocess.SubprocessError) as error:
        _append_log(custody_root, f"durable record failed: {error}")


def _resolve_courier_bin(
    requested: Path | None,
) -> tuple[Path | None, str | None, dict[str, str] | None]:
    substitution: dict[str, str] | None = None
    if requested is not None:
        candidate = requested
        if not candidate.is_absolute():
            return None, "--courier-bin must be an absolute path", None
        if not candidate.exists():
            found = shutil.which("claude")
            if found is None:
                return (
                    None,
                    f"courier binary is missing and claude was not found on PATH: {candidate}",
                    None,
                )
            candidate = Path(found)
            substitution = {"requested": str(requested), "used": str(candidate)}
    else:
        found = shutil.which("claude")
        if found is None:
            return None, "claude was not found on PATH", None
        candidate = Path(found)
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        return None, f"courier binary is missing or not executable: {candidate}", None
    return candidate, None, substitution


def _record_courier_substitution(
    custody_root: Path, substitution: Mapping[str, str] | None
) -> None:
    if substitution is not None:
        _append_log(
            custody_root,
            "courier binary substituted "
            f"requested={substitution['requested']} used={substitution['used']}",
        )


def _watchdog_liveness_for_courier(plan: NightPlan) -> tuple[Path, str, str]:
    """Read watchdog liveness without importing the watchdog implementation."""

    state_path = Path(plan.custody_root).parent / "magistrate" / "state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        modified_epoch_s = state_path.stat().st_mtime
    except (OSError, ValueError):
        return state_path, "unavailable", "unavailable"
    decision = state.get("state") if isinstance(state, Mapping) else None
    if not isinstance(decision, str) or re.fullmatch(r"[A-Z_]+", decision) is None:
        decision = "unavailable"
    age_s = max(0.0, time.time() - modified_epoch_s)
    return state_path, f"{age_s:.3f}", decision


def _courier_argv(
    custody_root: Path, plan: NightPlan, courier_bin: Path
) -> tuple[str, ...]:
    prompt = (REPO_ROOT / "docs" / "process" / "NIGHT_COURIER_PROMPT.md").read_text(
        encoding="utf-8"
    )
    prompt = (
        prompt.replace("{custody_root}", str(custody_root))
        .replace("{plan_id}", plan.plan_id)
        .replace("@@REPO_ROOT@@", str(REPO_ROOT))
    )
    watchdog_path, watchdog_age_s, watchdog_decision = _watchdog_liveness_for_courier(
        plan
    )
    prompt += (
        "\nWatchdog state path: "
        f"{watchdog_path}\n"
        f"Watchdog state age seconds: {watchdog_age_s}\n"
        f"Watchdog last decision: {watchdog_decision}\n"
        "You must include these watchdog fields in the email body. An age greater "
        "than 900 seconds, or an unavailable age, means the watchdog is dead.\n"
    )
    return (
        str(courier_bin),
        "-p",
        prompt,
        "--output-format",
        "text",
        "--allowedTools",
        COURIER_ALLOWED_TOOLS,
    )


def _wait_for_courier(
    heartbeat: Path,
    sent: Path,
    *,
    stop_epoch_s: float | None = None,
) -> tuple[bool, bool]:
    deadline = time.monotonic() + COURIER_DEADLINE_S
    heartbeat_seen = heartbeat.is_file()
    while True:
        monotonic_now = time.monotonic()
        epoch_now = time.time() if stop_epoch_s is not None else None
        if monotonic_now >= deadline or (
            stop_epoch_s is not None
            and epoch_now is not None
            and epoch_now >= stop_epoch_s
        ):
            break
        heartbeat_seen = heartbeat_seen or heartbeat.is_file()
        if sent.is_file():
            _fsync_path(sent)
            return heartbeat_seen, True
        deadline_remaining = deadline - time.monotonic()
        stop_remaining = (
            float("inf")
            if stop_epoch_s is None
            else stop_epoch_s - time.time()
        )
        sleep_s = max(0.0, min(1.0, deadline_remaining, stop_remaining))
        if sleep_s <= 0:
            break
        time.sleep(sleep_s)
    heartbeat_seen = heartbeat_seen or heartbeat.is_file()
    if sent.is_file():
        _fsync_path(sent)
        return heartbeat_seen, True
    return heartbeat_seen, False


def _pid_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _courier_lock_is_live(night_dir: Path) -> bool:
    lock = night_dir / "courier.lock"
    if not lock.is_file():
        return False
    try:
        record = json.loads(lock.read_text(encoding="utf-8"))
        pid = record["pid"]
        epoch_s = record["epoch_s"]
        if not isinstance(pid, int) or isinstance(pid, bool):
            return False
        if not isinstance(epoch_s, (int, float)) or isinstance(epoch_s, bool):
            return False
    except (OSError, ValueError, KeyError, TypeError):
        return False
    return time.time() - float(epoch_s) <= COURIER_LOCK_FRESH_S and _pid_is_live(pid)


def _refresh_courier_lock(descriptor: int) -> None:
    os.lseek(descriptor, 0, os.SEEK_SET)
    os.ftruncate(descriptor, 0)
    _write_all(descriptor, _json_bytes({"pid": os.getpid(), "epoch_s": time.time()}))


def _acquire_courier_lock(night_dir: Path) -> int | None:
    lock = night_dir / "courier.lock"
    for _attempt in range(2):
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if _courier_lock_is_live(night_dir):
                return None
            lock.unlink(missing_ok=True)
            continue
        _refresh_courier_lock(descriptor)
        return descriptor
    return None


def run_courier(
    custody_root: Path,
    plan: NightPlan,
    courier_bin: Path,
    *,
    deadman_epoch_s: float | None = None,
    courier_bin_substitution: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run one launch plus three retries while holding the courier lock."""

    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    heartbeat = night_dir / "courier.heartbeat"
    sent = night_dir / "courier.sent"
    attempts_path = night_dir / "courier.attempts.jsonl"
    lock_descriptor = _acquire_courier_lock(night_dir)
    if lock_descriptor is None:
        return {
            "attempted": 0,
            "sent": False,
            "heartbeat_seen": heartbeat.is_file(),
            "last_error": "courier lock belongs to a live process",
        }
    attempted = 0
    heartbeat_seen = False
    last_error: str | None = None
    try:
        for attempt in range(1 + len(COURIER_BACKOFF_S)):
            if deadman_epoch_s is not None and time.time() >= deadman_epoch_s:
                last_error = "dead-man epoch reached; run-path courier handed off"
                break
            last_error = None
            _refresh_courier_lock(lock_descriptor)
            heartbeat.unlink(missing_ok=True)
            started_epoch_s = time.time()
            attempted += 1
            try:
                process = subprocess.Popen(
                    _courier_argv(custody_root, plan, courier_bin),
                    cwd=REPO_ROOT,
                    start_new_session=True,
                )
            except OSError as error:
                process = None
                last_error = str(error)
                saw_heartbeat = False
                was_sent = False
            else:
                saw_heartbeat, was_sent = _wait_for_courier(
                    heartbeat,
                    sent,
                    stop_epoch_s=deadman_epoch_s,
                )
                heartbeat_seen = heartbeat_seen or saw_heartbeat
                if not was_sent:
                    _terminate_process_group(process)
                    last_error = "courier did not create courier.sent"
            attempt_record = {
                "attempt": attempt + 1,
                "started_epoch_s": started_epoch_s,
                "heartbeat": saw_heartbeat,
                "sent": was_sent,
                "error": last_error,
            }
            if courier_bin_substitution is not None:
                attempt_record["courier_bin_substitution"] = dict(
                    courier_bin_substitution
                )
            with attempts_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(attempt_record, sort_keys=True) + "\n")
            _append_log(
                custody_root,
                f"courier attempt={attempt + 1} heartbeat={saw_heartbeat} sent={was_sent}",
            )
            if was_sent:
                return {
                    "attempted": attempted,
                    "sent": True,
                    "heartbeat_seen": heartbeat_seen,
                    "last_error": None,
                }
            if attempt < len(COURIER_BACKOFF_S):
                delay = COURIER_BACKOFF_S[attempt]
                if deadman_epoch_s is not None and time.time() + delay >= deadman_epoch_s:
                    last_error = "retry would cross dead-man epoch; run-path courier handed off"
                    break
                _refresh_courier_lock(lock_descriptor)
                time.sleep(delay)
        return {
            "attempted": attempted,
            "sent": False,
            "heartbeat_seen": heartbeat_seen,
            "last_error": last_error,
        }
    finally:
        os.close(lock_descriptor)
        (night_dir / "courier.lock").unlink(missing_ok=True)


def _write_result(
    custody_root: Path,
    night_dir: Path,
    plan: NightPlan,
    verdict: str,
    chain_exit_code: int | None,
    aborted_reason: str | None,
    started_epoch_s: float,
    started_monotonic_ns: int,
    chain_sha256: str | None,
    census_count: int,
    census_hits: list[dict[str, Any]] | None = None,
) -> None:
    _write_json(
        night_dir / "result.json",
        {
            "schema": RESULT_SCHEMA,
            "plan_id": plan.plan_id,
            "receipt_class": plan.receipt_class,
            "verdict": verdict,
            "chain_exit_code": chain_exit_code,
            "aborted_reason": aborted_reason,
            "started_epoch_s": started_epoch_s,
            "ended_epoch_s": time.time(),
            "started_monotonic_ns": started_monotonic_ns,
            "ended_monotonic_ns": time.monotonic_ns(),
            "chain_sha256": chain_sha256,
            "census_count": census_count,
            "census_hits": [] if census_hits is None else census_hits,
            "artifacts": _artifact_list(custody_root, night_dir),
        },
    )


def _load_plan(path: Path) -> NightPlan:
    return NightPlan.from_mapping(json.loads(path.read_text(encoding="utf-8")))


def _fallback_plan(plan_path: Path) -> NightPlan:
    now = time.time()
    raw: Mapping[str, Any] = {}
    try:
        candidate = json.loads(plan_path.read_text(encoding="utf-8"))
        if isinstance(candidate, Mapping):
            raw = candidate
    except (OSError, ValueError):
        pass
    custody = raw.get("custody_root")
    if not isinstance(custody, str) or not custody:
        custody = str(plan_path.parent / "night-custody")
    plan_id = raw.get("plan_id")
    if not isinstance(plan_id, str) or not plan_id:
        plan_id = f"malformed-{plan_path.stem or 'plan'}"
    receipt_class = raw.get("receipt_class")
    if receipt_class not in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB", "TRANSACTION_PACK"}:
        receipt_class = "DIAGNOSTIC_NO_PACK"
    return NightPlan(
        plan_id=plan_id,
        receipt_class=receipt_class,
        t0_epoch_s=now,
        window_max_s=1,
        authored_epoch_s=now,
        repo_head="0" * 40,
        measurement_root="/",
        measurement_head="0" * 40,
        chain_path="",
        chain_sha256_path="",
        custody_root=custody,
        registration_path=None,
    )


def _next_deadman_epoch(t0_epoch_s: float) -> float:
    t0 = datetime.fromtimestamp(t0_epoch_s)
    deadman = t0.replace(
        hour=DEADMAN_HOUR,
        minute=DEADMAN_MINUTE,
        second=0,
        microsecond=0,
    )
    if deadman <= t0:
        deadman += timedelta(days=1)
    return deadman.timestamp()


def _completion_epoch_s(plan: NightPlan) -> float:
    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S


def _existing_record(night_dir: Path) -> Path | None:
    return next(
        (night_dir / name for name in _WRITE_ONCE_RECORDS if (night_dir / name).exists()),
        None,
    )


def _write_rerun_refusal(night_dir: Path, plan: NightPlan, existing: Path) -> None:
    epoch_s = int(time.time())
    path = night_dir / f"rerun-{epoch_s}.refusal.json"
    try:
        _write_driver_refusal(
            path,
            plan,
            _CODES["record_exists"],
            "a write-once night record already exists",
            {"existing": existing.name, "epoch_s": epoch_s},
        )
    except FileExistsError:
        pass


def _write_courier_outcome(night_dir: Path, outcome: Mapping[str, Any]) -> None:
    document = {
        "attempted": int(outcome["attempted"]),
        "sent": bool(outcome["sent"]),
        "heartbeat_seen": bool(outcome["heartbeat_seen"]),
        "last_error": outcome["last_error"],
    }
    _write_json(night_dir / "courier.json", document)


def _finish_reporting(
    custody_root: Path,
    night_dir: Path,
    plan: NightPlan,
    base_exit_code: int,
    courier_bin: Path | None,
    *,
    courier_error: str | None = None,
    deadman_epoch_s: float | None = None,
    allow_courier: bool = True,
    courier_bin_substitution: Mapping[str, str] | None = None,
) -> int:
    _durable_record(custody_root, night_dir, plan)
    if allow_courier and courier_bin is not None:
        outcome = run_courier(
            custody_root,
            plan,
            courier_bin,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_bin_substitution,
        )
    else:
        outcome = {
            "attempted": 0,
            "sent": False,
            "heartbeat_seen": (night_dir / "courier.heartbeat").is_file(),
            "last_error": courier_error or "courier suppressed by safety refusal",
        }
    _write_courier_outcome(night_dir, outcome)
    _durable_record(custody_root, night_dir, plan)
    return base_exit_code if outcome["sent"] else EXIT_COURIER_FAILED


def _write_standard_refusal_result(
    custody_root: Path,
    night_dir: Path,
    plan: NightPlan,
    reason: str,
    detail: str,
    started_epoch_s: float,
    started_monotonic_ns: int,
    *,
    evidence: Any = None,
) -> None:
    if plan.receipt_class == "TRANSACTION_PACK" and not (night_dir / "receipt.json").exists():
        failed = night_gate.Receipt(night_gate.SCHEMA, plan.receipt_class, plan.plan_id, "REFUSED",
            tuple(night_gate.ConditionRow(key, "FAIL", None, (), {"detail": detail}) for key in night_gate._CONDITION_IDS),
            night_gate.Refusal("launch_go_receipt_invalid", detail, ()), int(started_monotonic_ns))
        _write_bytes_exclusive(night_dir / "receipt.json", failed.to_json_bytes())
    refusal = _write_driver_refusal(
        night_dir / "refusal.json", plan, reason, detail, evidence
    )
    _write_result(
        custody_root,
        night_dir,
        plan,
        "REFUSED",
        None,
        refusal["reason"],
        started_epoch_s,
        started_monotonic_ns,
        None,
        0,
    )


def _malformed_plan_exit(plan_path: Path, error: Exception, courier_bin: Path | None) -> int:
    plan = _fallback_plan(plan_path)
    custody_root = Path(plan.custody_root)
    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_record(night_dir)
    if existing is not None:
        _write_rerun_refusal(night_dir, plan, existing)
        return EXIT_REFUSED
    (night_dir / "censuses.jsonl").touch(exist_ok=True)
    started_epoch_s = time.time()
    started_monotonic_ns = time.monotonic_ns()
    _append_log(custody_root, "night plan malformed")
    _write_standard_refusal_result(
        custody_root,
        night_dir,
        plan,
        _CODES["plan_malformed"],
        str(error),
        started_epoch_s,
        started_monotonic_ns,
    )
    resolved, resolution_error, substitution = _resolve_courier_bin(courier_bin)
    _record_courier_substitution(custody_root, substitution)
    return _finish_reporting(
        custody_root,
        night_dir,
        plan,
        EXIT_REFUSED,
        resolved,
        courier_error=resolution_error,
        courier_bin_substitution=substitution,
    )


class PackNightRefusal(ValueError):
    def __init__(self, detail: str, *, missing: bool = False):
        self.reason = "launch_go_receipt_missing" if missing else "launch_go_receipt_invalid"
        super().__init__(detail)


def _pack_bytes(path: Path, field: str, expected: str | None = None) -> bytes:
    from joulewise import arm_readiness as readiness
    try:
        if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
            raise PackNightRefusal(field + ": non-absolute or symlinked")
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise PackNightRefusal(field, missing=True) from exc
    except OSError as exc:
        raise PackNightRefusal(field + ": " + str(exc)) from exc
    if expected is not None and readiness.sha256_bytes(raw) != expected:
        raise PackNightRefusal(field + ": sha256 mismatch")
    return raw


def _pack_object(path: Path, field: str, expected: str | None = None):
    from joulewise import arm_readiness as readiness
    raw = _pack_bytes(path, field, expected)
    try:
        value = readiness.parse_json_bytes(raw)
        if not isinstance(value, Mapping):
            raise ValueError("not an object")
    except (ValueError, TypeError) as exc:
        raise PackNightRefusal(field + ": invalid JSON") from exc
    return value


def _pack_digest(plan: NightPlan, arm=None) -> Path:
    from joulewise import arm_readiness as readiness
    binding = plan.pack_night
    root = Path(binding["pack_root"])
    if (not root.is_absolute() or root.name != binding["pack_id"]
            or any(p.is_symlink() for p in (root, *root.parents))):
        raise PackNightRefusal("pack_root")
    try:
        root = root.resolve(strict=True)
        digest = readiness.committed_pack_tree_sha256(root)
    except FileNotFoundError as exc:
        raise PackNightRefusal("pack_root", missing=True) from exc
    except (OSError, ValueError, RuntimeError) as exc:
        raise PackNightRefusal("pack_root: " + str(exc)) from exc
    if digest != binding["pack_sha256"]:
        raise PackNightRefusal("pack_root.pack_sha256")
    if arm is not None and (arm["pack"]["pack_sha256"] != digest
                            or arm["pack"]["pack_root"] != str(root)
                            or arm["pack"]["pack_id"] != binding["pack_id"]):
        raise PackNightRefusal("arm_receipt.pack.pack_root/pack_sha256")
    return root


def _prepare_pack_night(plan: NightPlan, plan_path: Path, plan_raw: bytes):
    """Re-read armed authority; no ARM authoring and no GO occurs here."""
    from joulewise import arm_readiness as readiness
    _pack_bytes(plan_path, "plan_sha256", readiness.sha256_bytes(plan_raw))
    root = _pack_digest(plan)
    binding = plan.pack_night
    records = {}
    for field in ("authorization_record", "confirmation_record"):
        locator = binding[field]
        path = Path(locator["path"])
        try:
            path.resolve(strict=True).relative_to(Path(plan.custody_root).resolve(strict=True))
        except FileNotFoundError as exc:
            raise PackNightRefusal(field, missing=True) from exc
        except (OSError, ValueError, RuntimeError) as exc:
            raise PackNightRefusal(field + ".path") from exc
        records[field] = _pack_object(path, field, locator["sha256"])
    authorization = records["authorization_record"]
    keys = {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256", "permitted_blocks", "authority"}
    if set(authorization) != keys:
        raise PackNightRefusal("authorization_record.keys")
    for field in ("pack_sha256", "permitted_chain_sha256"):
        if not isinstance(authorization[field], str) or re.fullmatch("[0-9a-f]{64}", authorization[field]) is None:
            raise PackNightRefusal("authorization_record." + field)
    if authorization["attempt_id"] != f"{plan.plan_id}/{binding['attempt_ordinal']}":
        raise PackNightRefusal("authorization_record.attempt_id")
    if authorization["pack_sha256"] != binding["pack_sha256"]:
        raise PackNightRefusal("authorization_record.pack_sha256")
    purpose = authorization["purpose"]
    if not isinstance(purpose, str) or purpose not in {"G2B_SHAKEDOWN", "CAMPAIGN_TRANSACTION", "T0_REHEARSAL"}:
        raise PackNightRefusal("authorization_record.purpose")
    if (type(authorization["claim_eligible"]) is not bool
            or type(authorization["permitted_blocks"]) is not int or authorization["permitted_blocks"] < 1
            or not isinstance(authorization["authority"], str) or not authorization["authority"].strip()):
        raise PackNightRefusal("authorization_record.claim_eligible/permitted_blocks/authority")
    if purpose != "CAMPAIGN_TRANSACTION" and authorization["claim_eligible"]:
        raise PackNightRefusal("authorization_record.claim_eligible")
    if purpose == "G2B_SHAKEDOWN" and (authorization["permitted_blocks"] != 1 or "D-171" not in authorization["authority"]):
        raise PackNightRefusal("authorization_record.permitted_blocks")
    if purpose == "CAMPAIGN_TRANSACTION" and authorization["authority"] != "V5-TRANSACTION-GO-01":
        raise PackNightRefusal("authorization_record.authority")
    confirmation = records["confirmation_record"]
    if set(confirmation) != {"table_path", "table_sha256", "transcript_sha256", "confirmed_at"}:
        raise PackNightRefusal("confirmation_record.keys")
    for field in ("table_sha256", "transcript_sha256"):
        if not isinstance(confirmation[field], str) or re.fullmatch("[0-9a-f]{64}", confirmation[field]) is None:
            raise PackNightRefusal("confirmation_record." + field)
    event = confirmation["confirmed_at"]
    if (not isinstance(event, Mapping) or set(event) != {"epoch_s", "iso8601_utc"}
            or type(event["epoch_s"]) is not float or not math.isfinite(event["epoch_s"])):
        raise PackNightRefusal("confirmation_record.confirmed_at")
    try:
        stamp = datetime.strptime(event["iso8601_utc"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if abs(stamp.timestamp() - event["epoch_s"]) > 0.000001:
            raise ValueError("timestamps differ")
    except (TypeError, ValueError) as exc:
        raise PackNightRefusal("confirmation_record.confirmed_at") from exc
    if not isinstance(confirmation["table_path"], str):
        raise PackNightRefusal("confirmation_record.table_path")
    _pack_bytes(Path(confirmation["table_path"]), "confirmation_record.table_sha256", confirmation["table_sha256"])
    chain = _pack_bytes(Path(plan.chain_path), "window_chain_sha256", authorization["permitted_chain_sha256"])
    sidecar = _pack_bytes(Path(plan.chain_sha256_path), "chain_sha256_path").decode("utf-8")
    if _sidecar_digest(sidecar, Path(plan.chain_path).name) != readiness.sha256_bytes(chain):
        raise PackNightRefusal("window_chain_sha256: sidecar mismatch")
    return {"root": root, **records}


def _pack_no_retry(plan: NightPlan, boot: str, written: Path | None = None):
    from joulewise import arm_readiness as readiness
    pack_custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    for directory in (pack_custody, pack_custody / "arm_readiness.receipts", pack_custody / "arm_readiness.consumptions"):
        if directory.is_symlink():
            raise PackNightRefusal("arm_receipt: symlinked namespace")
    for path in pack_custody.rglob("*.consumed.json"):
        value = _pack_object(path, "consumption")
        if not isinstance(value.get("boot_session_id"), str):
            raise PackNightRefusal("consumption.boot_session_id")
        if value.get("boot_session_id") == boot:
            raise PackNightRefusal("arm_receipt: consumption this boot")
    namespace = pack_custody / "arm_readiness.receipts"
    if not namespace.exists():
        return
    for entry in readiness.scan_receipt_namespace(namespace, "arm"):
        if entry["receipt"]["boot_session_id"] != boot:
            continue
        if written is None or entry["number"] > int(written.stem.removeprefix("arm-")):
            raise PackNightRefusal("arm_receipt: higher-numbered unconsumed receipt or re-arm this boot")


def _author_pack_arm(plan: NightPlan, prepared):
    from joulewise import arm_readiness as readiness
    from joulewise import arm_readiness_evidence_t0 as t0_author
    root = prepared["root"]
    custody = Path(plan.custody_root)
    pack_custody = custody / plan.pack_night["pack_id"]
    boot = readiness._current_boot_session_id()
    _pack_no_retry(plan, boot)
    namespace = pack_custody / "arm_readiness.receipts"
    before = {p.resolve() for p in namespace.glob("arm-*.json")}
    authored = t0_author.author_arm_readiness_evidence_t0(root, custody)
    if authored.get("status") != "PASS":
        raise PackNightRefusal("t0_evidence: author refused")
    context = _pack_object(pack_custody / "arm_readiness.t0.inputs/arm-context.json", "arm_context")
    confirmation = prepared["confirmation_record"]
    result = readiness.generate_arm_receipt(
        root, context, custody,
        step6_confirmation_table=confirmation["table_path"],
        expected_confirmation_digest=confirmation["table_sha256"],
    )
    if result.get("arm_disposition") != "GO" or result.get("status") != "PASS":
        raise PackNightRefusal("arm_receipt: NO_GO")
    path = Path(result["receipt_path"])
    if (path.parent != namespace or not re.fullmatch(r"arm-[0-9]{4,}\.json", path.name)
            or path.resolve() in before):
        raise PackNightRefusal("arm_receipt: must be the driver's self-written receipt")
    verification = readiness._verify_arm_receipt(
        root, path, require_unconsumed=True,
        step6_confirmation_table=confirmation["table_path"],
        expected_confirmation_digest=confirmation["table_sha256"],
    )
    arm = _pack_object(path, "arm_receipt", result["receipt_sha256"])
    if verification.get("receipt_sha256") != result["receipt_sha256"]:
        raise PackNightRefusal("arm_receipt.sha256")
    _pack_no_retry(plan, boot, path)
    return {"path": path, "arm": arm, "sha256": result["receipt_sha256"], "authored": authored}


def _pack_evidence(plan: NightPlan, arm_state):
    from joulewise import arm_readiness as readiness
    from joulewise import arm_readiness_evidence_t0 as t0_author
    custody = Path(plan.custody_root)
    pack_custody = custody / plan.pack_night["pack_id"]
    paths = arm_state["authored"].get("receipt_paths")
    expected_paths = {str(pack_custody / t0_author._EVIDENCE_DIRECTORY / t0_author._receipt_name(row)) for row in t0_author._EXPECTED_ROWS}
    if not isinstance(paths, list) or len(paths) != 15 or any(not isinstance(path, str) for path in paths) or set(paths) != expected_paths:
        raise PackNightRefusal("t0_evidence.receipt_paths")
    arm_paths = {str(pack_custody / item["path"]): item["sha256"]
                 for item in arm_state["arm"]["evidence"] if item.get("namespace") == "WINDOW_CUSTODY"}
    records = []
    inputs = {}
    for text in paths:
        if text not in arm_paths:
            raise PackNightRefusal("t0_evidence: author receipt absent from ARM")
        path = Path(text)
        value = _pack_object(path, "t0_evidence", arm_paths[text])
        for fact in value.get("facts", []):
            if fact.get("source_kind") != "PROBE":
                continue
            source = _pack_object(pack_custody / fact["source_path"], "t0_evidence.source", fact["source_sha256"])
            for item in source.get("input_artifacts", []):
                if item["path"] in inputs and inputs[item["path"]] != item["sha256"]:
                    raise PackNightRefusal("t0_evidence.source: conflicting input digest")
                inputs[item["path"]] = item["sha256"]
        records.append(path)
    # This is the author's exact capture inventory, not a caller glob or subset.
    records.extend(pack_custody / "arm_readiness.t0.inputs" / name for name in t0_author._CAPTURE_FILES.values())
    result = []
    for path in records:
        expected = arm_paths.get(str(path), inputs.get(str(path)))
        if expected is None:
            raise PackNightRefusal("t0_evidence.capture: absent from author attestation")
        raw = _pack_bytes(path, "t0_evidence", expected)
        try:
            relative = path.resolve(strict=True).relative_to(custody.resolve(strict=True)).as_posix()
        except ValueError as exc:
            raise PackNightRefusal("t0_evidence.path") from exc
        result.append({"path": relative, "sha256": readiness.sha256_bytes(raw)})
    return sorted(result, key=lambda item: item["path"])


def _pack_launch_references(plan: NightPlan, arm):
    from joulewise import arm_readiness as readiness
    root = Path(plan.pack_night["pack_root"])
    pack_custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    fixed = pack_custody / "arm_readiness.t0.inputs/launch-manifest.json"
    _pack_bytes(fixed, "launch_manifest")
    # More than one manifest-shaped input is ambiguous even if one has the
    # preferred spelling. Never choose a fallback candidate.
    for path in (pack_custody / "arm_readiness.t0.inputs").rglob("*.json"):
        if path != fixed and _pack_object(path, "launch_manifest candidates").get("schema_version") == readiness.LAUNCH_MANIFEST_SCHEMA:
            raise PackNightRefusal("launch_manifest: duplicate candidate")
    refs = readiness._attested_launch_artifact_references(root, pack_custody, arm, launch_binding_cache={})
    if refs["launch_manifest"]["path"] != str(fixed):
        raise PackNightRefusal("launch_manifest.path")
    for name, item in refs.items():
        _pack_bytes(Path(item["path"]), name + "_sha256", item["sha256"])
    if refs["window_chain"]["path"] != plan.chain_path:
        raise PackNightRefusal("window_chain.path")
    return refs


def _pack_rehearsal_roots(plan, arm, purpose):
    from joulewise import arm_readiness as readiness, t0_rehearsal
    from scripts.rehearse_t0_unattended import _production_inventory
    window_id = arm["pack"]["window_id"]
    prefixed = isinstance(window_id, str) and window_id.startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX)
    if prefixed != (purpose == "T0_REHEARSAL"):
        raise PackNightRefusal("rehearsal_purpose_on_production_id" if purpose == "T0_REHEARSAL" else "purpose")
    if not prefixed:
        return
    production = readiness.production_custody_roots(home=Path.home(), inventory=_production_inventory())
    roots = {"measurement_root": plan.measurement_root, "custody_root": plan.custody_root}
    roots.update({"arm_context." + key: value for key, value in arm["arm_context"].items()
                  if key not in {"bracket_session_id", "pre_attempt_id", "post_attempt_id", "clock_route"}})
    for field, text in roots.items():
        path = Path(text)
        if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
            raise PackNightRefusal(field)
        try:
            path = path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise PackNightRefusal(field + ": resolution_error") from exc
        for root in production:
            if root.resolution_error is not None:
                raise PackNightRefusal("rehearsal_roots_not_disjoint: resolution_error " + root.role)
            predicate = next((spec.predicate for spec in readiness.PRODUCTION_CUSTODY_ROOTS
                              if spec.role == root.role.split(":", 1)[0]), None)
            if predicate not in {"DISJOINT", "SIBLING_CHILD"}:
                raise PackNightRefusal("rehearsal_roots_not_disjoint: unknown production predicate")
            if predicate == "SIBLING_CHILD" and field in {"custody_root", "arm_context.custody_root"}:
                if path.parent != root.path or path.name != window_id:
                    raise PackNightRefusal("rehearsal_roots_not_disjoint: " + field)
            elif t0_rehearsal._contains(root.path, path) or t0_rehearsal._contains(path, root.path):
                raise PackNightRefusal("rehearsal_roots_not_disjoint: " + field)


def _produce_pack_go(plan, plan_path, plan_raw, prepared, arm_state, receipt, probes):
    """Final producer reauthentication; publish once only after every check."""
    from joulewise import arm_readiness as readiness
    if receipt.verdict != "GO" or any(row.status != "PASS" for row in receipt.conditions):
        raise PackNightRefusal("conditions: refused night")
    current = _prepare_pack_night(plan, plan_path, plan_raw)
    if current != prepared:
        raise PackNightRefusal("preparation changed")
    arm = arm_state["arm"]
    _pack_digest(plan, arm)
    confirmation = prepared["confirmation_record"]
    readiness._verify_arm_receipt(prepared["root"], arm_state["path"], require_unconsumed=True,
        step6_confirmation_table=confirmation["table_path"], expected_confirmation_digest=confirmation["table_sha256"])
    _pack_bytes(arm_state["path"], "arm_receipt", arm_state["sha256"])
    _pack_no_retry(plan, readiness._current_boot_session_id(), arm_state["path"])
    refs = _pack_launch_references(plan, arm)
    evidence = _pack_evidence(plan, arm_state)
    probe, refusal = agent_census(probes)
    _append_census(Path(plan.custody_root) / "night/censuses.jsonl", probe, refusal)
    if refusal is not None or probe.exit_code != 1 or probe.stdout != "":
        raise PackNightRefusal("census: " + (refusal.detail if refusal else "stdout must be empty"))
    issued = time.monotonic_ns()
    issued_epoch = float(probes.now_epoch_s())
    if not plan.t0_epoch_s <= issued_epoch <= plan.t0_epoch_s + plan.window_max_s:
        raise PackNightRefusal("conditions.C5.window_expired")
    if arm["boot_session_id"] != readiness._current_boot_session_id() or not probe.monotonic_ns <= issued < arm["valid_until_monotonic_ns"]:
        raise PackNightRefusal("boot_session_id/valid_until_monotonic_ns")
    authorization = prepared["authorization_record"]
    if arm["pack"]["plan_id"] != plan.plan_id:
        raise PackNightRefusal("arm_receipt.pack.plan_id")
    if arm["reviewed_main"]["head_commit"] != plan.repo_head or probes.checkout_head() != plan.repo_head:
        raise PackNightRefusal("repo_head")
    if next(row for row in receipt.conditions if row.condition_id == "C4").measured.get("boot_session_uuid") != arm["boot_session_id"]:
        raise PackNightRefusal("conditions.C4.boot_session_id")
    _pack_rehearsal_roots(plan, arm, authorization["purpose"])
    custody = Path(plan.custody_root).resolve(strict=True)
    def reference(path, digest):
        return {"path": Path(path).resolve(strict=True).relative_to(custody).as_posix(), "sha256": digest}
    arm_ref = reference(arm_state["path"], arm_state["sha256"])
    auth_ref = reference(plan.pack_night["authorization_record"]["path"], plan.pack_night["authorization_record"]["sha256"])
    confirmation_ref = reference(plan.pack_night["confirmation_record"]["path"], plan.pack_night["confirmation_record"]["sha256"])
    # The running census journal remains append-only. GO instead binds this
    # immutable snapshot so a later journal append cannot invalidate C3 replay.
    census_path = custody / "night/go-census.json"
    census_raw = readiness.render_json(_census_record(probe, None))
    _write_bytes_exclusive(census_path, census_raw)
    census_ref = reference(census_path, readiness.sha256_bytes(census_raw))
    condition_evidence = {"C1": [auth_ref, confirmation_ref], "C2": [arm_ref, *evidence],
                          "C3": [census_ref], "C4": evidence, "C5": [arm_ref, auth_ref]}
    conditions = []
    for row in receipt.conditions:
        conditions.append({"condition_id": row.condition_id, "status": row.status, "basis": row.basis,
                           "evidence": condition_evidence[row.condition_id], "measured": dict(row.measured)})
    go = {
        "schema_version": "joulewise.pack_night_go_receipt.v1", "receipt_id": str(uuid.uuid4()),
        "receipt_class": "TRANSACTION_PACK", "purpose": authorization["purpose"],
        "plan_id": plan.plan_id, "plan_sha256": readiness.sha256_bytes(plan_raw),
        "pack_id": plan.pack_night["pack_id"], "pack_sha256": plan.pack_night["pack_sha256"],
        "arm_receipt": {"receipt_id": arm["receipt_id"], "sha256": arm_state["sha256"],
                        "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"]},
        "boot_session_id": arm["boot_session_id"], "t0_evidence": evidence,
        "t0_evidence_set_sha256": readiness.sha256_bytes(readiness.render_json(evidence)),
        "launch_manifest_sha256": refs["launch_manifest"]["sha256"],
        "window_environment_sha256": refs["window_environment"]["sha256"],
        "window_chain_sha256": refs["window_chain"]["sha256"],
        "repo_head": plan.repo_head, "measurement_root": plan.measurement_root, "measurement_head": plan.measurement_head,
        "confirmation_record": dict(plan.pack_night["confirmation_record"]),
        "authorization": {**plan.pack_night["authorization_record"], **{k: authorization[k] for k in ("purpose", "attempt_id", "claim_eligible")}},
        "census": {"argv": list(probe.argv), "exit_code": probe.exit_code,
                   "stdout_sha256": readiness.sha256_bytes(probe.stdout.encode()), "monotonic_ns": probe.monotonic_ns},
        "issued_epoch_s": issued_epoch, "issued_monotonic_ns": issued,
        "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"], "conditions": conditions, "verdict": "GO",
    }
    path = Path(plan.custody_root) / "night/go_receipt.json"
    _write_bytes_exclusive(path, readiness.render_json(go))
    _fsync_path(path.parent)
    return _pack_launcher_argv(plan, plan_path, arm_state["path"], Path(refs["launch_manifest"]["path"]), path, confirmation)


def _pack_launcher_argv(plan, plan_path, arm_path, manifest_path, go_path, confirmation):
    return [str(Path(plan.measurement_root) / ".venv/bin/python"),
            str(Path(plan.measurement_root) / "scripts/launch_window.py"),
            "--pack-root", plan.pack_night["pack_root"], "--arm-receipt", str(arm_path),
            "--arm-readiness-custody-root", plan.custody_root, "--launch-manifest", str(manifest_path),
            "--night-plan", str(plan_path), "--go-receipt", str(go_path),
            "--step6-confirmation-table", confirmation["table_path"],
            "--expected-confirmation-digest", confirmation["table_sha256"]]


def _pack_refused_receipt(plan, error, probes):
    reason = getattr(error, "reason", "launch_go_receipt_invalid")
    return night_gate.Receipt(night_gate.SCHEMA, plan.receipt_class, plan.plan_id, "REFUSED",
        tuple(night_gate.ConditionRow(key, "FAIL", None, (), {"detail": str(error)}) for key in night_gate._CONDITION_IDS),
        night_gate.Refusal(reason, str(error), ()), int(probes.monotonic_ns()))


def run_night(
    plan_path: Path,
    *,
    rehearsal: bool = False,
    courier_bin: Path | None = None,
) -> int:
    from joulewise import arm_readiness as readiness
    probes = make_probes()
    initial_probe, initial_refusal = agent_census(probes)
    try:
        plan_path = plan_path.resolve(strict=True)
        plan_raw = plan_path.read_bytes()
        plan = NightPlan.from_mapping(readiness.parse_json_bytes(plan_raw))
    except (OSError, ValueError, TypeError, PlanError) as error:
        return _malformed_plan_exit(plan_path, error, courier_bin)

    custody_root = Path(plan.custody_root)
    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_record(night_dir)
    if existing is not None:
        _write_rerun_refusal(night_dir, plan, existing)
        return EXIT_REFUSED

    _append_census(night_dir / "censuses.jsonl", initial_probe, initial_refusal)
    started_epoch_s = time.time()
    started_monotonic_ns = time.monotonic_ns()
    _append_log(custody_root, "night driver started")
    resolved_courier, courier_error, courier_substitution = _resolve_courier_bin(
        courier_bin
    )
    _record_courier_substitution(custody_root, courier_substitution)
    if resolved_courier is None:
        _write_standard_refusal_result(
            custody_root,
            night_dir,
            plan,
            _CODES["courier_unavailable"],
            courier_error or "courier unavailable",
            started_epoch_s,
            started_monotonic_ns,
        )
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            EXIT_REFUSED,
            None,
            courier_error=courier_error,
            courier_bin_substitution=courier_substitution,
        )

    deadman_epoch_s = _next_deadman_epoch(plan.t0_epoch_s)
    completion_epoch_s = _completion_epoch_s(plan)
    if completion_epoch_s >= deadman_epoch_s:
        _write_standard_refusal_result(
            custody_root,
            night_dir,
            plan,
            _CODES["plan_overruns_deadman"],
            (
                f"t0_epoch_s={plan.t0_epoch_s}; window_max_s={plan.window_max_s}; "
                f"courier_deadline_s={COURIER_DEADLINE_S}; "
                f"deadman_epoch_s={deadman_epoch_s}"
            ),
            started_epoch_s,
            started_monotonic_ns,
        )
        _append_log(custody_root, "night plan overran dead-man")
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            EXIT_REFUSED,
            resolved_courier,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_substitution,
        )

    prepared = arm_state = None
    is_pack = plan.receipt_class == "TRANSACTION_PACK"
    if is_pack:
        try:
            if initial_refusal is not None or initial_probe.exit_code != 1 or initial_probe.stdout != "":
                error = PackNightRefusal("census: " + (initial_refusal.detail if initial_refusal else "stdout must be empty"))
                if initial_refusal is not None:
                    error.reason = initial_refusal.reason
                raise error
            if rehearsal:
                raise PackNightRefusal("receipt_class: rehearsal flag requires REHEARSAL_STUB")
            prepared = _prepare_pack_night(plan, plan_path, plan_raw)
            arm_state = _author_pack_arm(plan, prepared)
            conditions = {
                "C1": night_gate.ConditionRow("C1", "PASS", None, (str(plan.pack_night["authorization_record"]["path"]),), dict(prepared["authorization_record"])),
                "C2": night_gate.ConditionRow("C2", "PASS", None, (str(arm_state["path"]),), {"arm_sha256": arm_state["sha256"]}),
            }
            receipt = evaluate_night(plan, probes, pack_conditions=conditions)
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
            receipt = _pack_refused_receipt(plan, error, probes)
    else:
        # Reuse the first census for the legacy evaluator's census slot; no
        # filesystem or command probe preceded the driver's initial census.
        original_run = probes.run
        cached = [initial_probe]
        def first_census(argv):
            if tuple(argv) == night_gate.AGENT_CENSUS_ARGV and cached:
                return cached.pop()
            return original_run(argv)
        receipt = evaluate_night(plan, replace(probes, run=first_census))
    if not is_pack or receipt.verdict != "GO":
        _write_bytes_exclusive(night_dir / "receipt.json", receipt.to_json_bytes())
    _append_log(custody_root, f"night gate verdict={receipt.verdict}")

    if rehearsal and plan.receipt_class != "REHEARSAL_STUB":
        _write_standard_refusal_result(
            custody_root,
            night_dir,
            plan,
            _CODES["receipt_class_invalid"],
            "rehearsal requires receipt class REHEARSAL_STUB",
            started_epoch_s,
            started_monotonic_ns,
        )
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            EXIT_REFUSED,
            resolved_courier,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_substitution,
        )

    rehearsal_effective = rehearsal or plan.receipt_class == "REHEARSAL_STUB"
    if receipt.verdict != "GO" and not rehearsal_effective:
        _write_gate_refusal(night_dir / "refusal.json", receipt)
        refusal = _refusal_from_object(receipt.refusal) or {}
        _write_result(
            custody_root,
            night_dir,
            plan,
            str(receipt.verdict),
            None,
            str(refusal.get("reason")) if refusal.get("reason") is not None else None,
            started_epoch_s,
            started_monotonic_ns,
            None,
            0,
        )
        _append_log(custody_root, "night gate refused")
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            EXIT_REFUSED,
            resolved_courier,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_substitution,
        )

    if rehearsal_effective:
        chain_path = Path("/dev/null")
        chain_sha256 = None
        command = ["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]
    else:
        chain_path = Path(plan.chain_path)
        chain_sha256 = _sha256_path(chain_path) if chain_path.is_file() else None
        sidecar_path = Path(plan.chain_sha256_path)
        sidecar_text = (
            sidecar_path.read_text(encoding="utf-8") if sidecar_path.is_file() else ""
        )
        expected = _sidecar_digest(sidecar_text, chain_path.name)
        if chain_sha256 is None or expected is None or chain_sha256 != expected:
            _write_standard_refusal_result(
                custody_root,
                night_dir,
                plan,
                _CODES["chain_digest_mismatch"],
                "chain bytes do not match the arm-time SHA-256 sidecar",
                started_epoch_s,
                started_monotonic_ns,
                evidence={
                    "actual": chain_sha256,
                    "expected": expected,
                    "sidecar": sidecar_text,
                },
            )
            _append_log(custody_root, "night chain digest refused")
            return _finish_reporting(
                custody_root,
                night_dir,
                plan,
                EXIT_REFUSED,
                resolved_courier,
                deadman_epoch_s=deadman_epoch_s,
                courier_bin_substitution=courier_substitution,
            )
        command = ["/bin/zsh", str(chain_path)]
        _append_log(custody_root, "night chain digest verified")

    if is_pack:
        try:
            command = _produce_pack_go(plan, plan_path, plan_raw, prepared, arm_state, receipt, probes)
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
            receipt = _pack_refused_receipt(plan, error, probes)
            _write_bytes_exclusive(night_dir / "receipt.json", receipt.to_json_bytes())
            _write_standard_refusal_result(custody_root, night_dir, plan, receipt.refusal.reason,
                receipt.refusal.detail, started_epoch_s, started_monotonic_ns)
            return _finish_reporting(custody_root, night_dir, plan, EXIT_REFUSED, resolved_courier,
                deadman_epoch_s=deadman_epoch_s, courier_bin_substitution=courier_substitution)
        _write_bytes_exclusive(night_dir / "receipt.json", receipt.to_json_bytes())

    claim_descriptor = _claim_chain_start(night_dir)
    if claim_descriptor is None:
        _write_standard_refusal_result(
            custody_root,
            night_dir,
            plan,
            _CODES["chain_already_started"],
            "chain.started already exists; the night chain is once-only",
            started_epoch_s,
            started_monotonic_ns,
        )
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            EXIT_REFUSED,
            resolved_courier,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_substitution,
        )

    chain_exit_code, abort, census_count, census_hits, termination_proven = (
        _run_chain_once(
            chain_path,
            plan,
            probes,
            night_dir,
            claim_descriptor,
            command=command,
            abort_on_census=not rehearsal_effective,
        )
    )

    if abort is not None:
        abort_reason = str(abort["reason"])
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            abort_reason,
            str(abort["detail"]),
            abort["evidence"],
        )
        refused = (
            abort_reason == _CODES["chain_launch_failed"] or not termination_proven
        )
        verdict = "REFUSED" if refused else "ABORTED"
        base_exit_code = EXIT_REFUSED if refused else EXIT_ABORTED
        aborted_reason = abort_reason
    elif rehearsal_effective:
        verdict = "REHEARSAL_ONLY"
        base_exit_code = EXIT_REFUSED
        aborted_reason = None
    else:
        verdict = "GO"
        base_exit_code = EXIT_GO if chain_exit_code == 0 else EXIT_CHAIN_FAILED
        aborted_reason = None
    _write_result(
        custody_root,
        night_dir,
        plan,
        verdict,
        chain_exit_code,
        aborted_reason,
        started_epoch_s,
        started_monotonic_ns,
        chain_sha256,
        census_count,
        census_hits,
    )
    _append_log(custody_root, f"night result verdict={verdict}")
    if not termination_proven:
        return _finish_reporting(
            custody_root,
            night_dir,
            plan,
            base_exit_code,
            resolved_courier,
            courier_error="chain termination was not proven",
            allow_courier=False,
            courier_bin_substitution=courier_substitution,
        )
    return _finish_reporting(
        custody_root,
        night_dir,
        plan,
        base_exit_code,
        resolved_courier,
        deadman_epoch_s=deadman_epoch_s,
        courier_bin_substitution=courier_substitution,
    )


def _read_started_pgid(path: Path) -> int | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        pgid = value["pgid"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if not isinstance(pgid, int) or isinstance(pgid, bool) or pgid <= 0:
        return None
    return pgid


def dead_man(plan_path: Path, *, courier_bin: Path | None = None) -> int:
    try:
        plan = _load_plan(plan_path)
    except (OSError, ValueError, TypeError, PlanError) as error:
        return _malformed_plan_exit(plan_path, error, courier_bin)
    custody_root = Path(plan.custody_root)
    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    sent = night_dir / "courier.sent"
    if sent.exists():
        _fsync_path(sent)
        _append_log(custody_root, "dead-man skipped: courier already sent")
        return EXIT_GO
    completion_epoch_s = _completion_epoch_s(plan)
    if time.time() < completion_epoch_s:
        _append_log(
            custody_root,
            "dead-man fired before the night's completion epoch "
            f"{int(completion_epoch_s)}; standing down",
        )
        return EXIT_GO

    resolved_courier, courier_error, courier_substitution = _resolve_courier_bin(
        courier_bin
    )
    _record_courier_substitution(custody_root, courier_substitution)
    if _courier_lock_is_live(night_dir):
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            _CODES["courier_running"],
            "a fresh courier lock belongs to a live process",
        )
        _append_log(custody_root, "dead-man refused while courier was running")
        _durable_record(custody_root, night_dir, plan)
        return EXIT_REFUSED

    started = night_dir / "chain.started"
    exited = night_dir / "chain.exited"
    if started.exists() and not exited.exists():
        pgid = _read_started_pgid(started)
        if pgid is None:
            _record_chain_exit(
                night_dir,
                None,
                reaped_by="dead-man",
                launch_failed=True,
            )
            _append_log(
                custody_root,
                "dead-man found no live process-group identity in chain.started",
            )
        else:
            group_alive = True
            try:
                os.killpg(pgid, 0)
            except ProcessLookupError:
                group_alive = False
            except PermissionError:
                group_alive = True
            if group_alive:
                _write_driver_refusal(
                    night_dir / "refusal.json",
                    plan,
                    _CODES["chain_alive"],
                    "chain process group is still alive or cannot be disproven",
                    {"pgid": pgid},
                )
                _append_log(custody_root, "dead-man refused while chain was alive")
                _durable_record(custody_root, night_dir, plan)
                return EXIT_REFUSED
            _record_chain_exit(night_dir, None, reaped_by="dead-man")
            _append_log(custody_root, "dead-man proved the chain process group was gone")

    probes = make_probes()
    probe, census_refusal = agent_census(probes)
    _append_census(night_dir / "censuses.jsonl", probe, census_refusal)
    if census_refusal is not None and not (night_dir / "refusal.json").exists():
        refusal = _refusal_from_object(census_refusal) or {}
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            str(refusal.get("reason")),
            str(refusal.get("detail")),
            refusal.get("evidence"),
        )
    _append_log(custody_root, "dead-man starting courier")
    _durable_record(custody_root, night_dir, plan)
    if resolved_courier is None:
        outcome = {
            "attempted": 0,
            "sent": False,
            "heartbeat_seen": False,
            "last_error": courier_error,
        }
    else:
        outcome = run_courier(
            custody_root,
            plan,
            resolved_courier,
            courier_bin_substitution=courier_substitution,
        )
    if not (night_dir / "courier.json").exists():
        _write_courier_outcome(night_dir, outcome)
    _durable_record(custody_root, night_dir, plan)
    return EXIT_GO if outcome["sent"] else EXIT_COURIER_FAILED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Exit 0: GO chain/courier succeeded; 3: refusal; 4: census abort; "
            "5: chain failure; 6: courier failure."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "dead-man", "rehearse"):
        command = subcommands.add_parser(name)
        command.add_argument("--plan", required=True, type=Path, metavar="PLAN.json")
        command.add_argument("--courier-bin", type=Path, metavar="ABSOLUTE_PATH")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return run_night(args.plan, courier_bin=args.courier_bin)
    if args.command == "rehearse":
        return run_night(args.plan, rehearsal=True, courier_bin=args.courier_bin)
    return dead_man(args.plan, courier_bin=args.courier_bin)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
