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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping


# A LaunchAgent starts this file by absolute path with a minimal environment.
# Make the checkout importable before importing any project module.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) in sys.path:
    sys.path.remove(str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT))

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


_CODES = _build_code_map(NIGHT_GATE_REASON_CODES | NIGHT_DRIVER_REASON_CODES)


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


def _complete_chain_start(descriptor: int, process: subprocess.Popen[Any]) -> int:
    # start_new_session=True makes the child the process-group leader.
    pgid = process.pid
    try:
        _write_all(
            descriptor,
            _json_bytes({"pid": process.pid, "pgid": pgid, "epoch_s": time.time()}),
        )
    finally:
        os.close(descriptor)
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
        try:
            process = subprocess.Popen(
                command if command is not None else ["/bin/zsh", str(chain_path)],
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
        pgid = _complete_chain_start(claim_descriptor, process)
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


def run_night(
    plan_path: Path,
    *,
    rehearsal: bool = False,
    courier_bin: Path | None = None,
) -> int:
    try:
        plan = _load_plan(plan_path)
    except (OSError, ValueError, TypeError, PlanError) as error:
        return _malformed_plan_exit(plan_path, error, courier_bin)

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

    probes = make_probes()
    receipt = evaluate_night(plan, probes)
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
