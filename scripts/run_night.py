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
from datetime import date, datetime, time as wall_time, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


# Keep aligned with pyproject.toml requires-python. The installer reads this literal.
MIN_PYTHON = (3, 11)
if sys.version_info[:2] < MIN_PYTHON:
    raise RuntimeError(
        f"Python {sys.version_info[0]}.{sys.version_info[1]} is below the minimum "
        f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    )


# A LaunchAgent starts this file by absolute path with a minimal environment.
# Make the checkout importable before importing any project module.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) in sys.path:
    sys.path.remove(str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT))

# Eager imports cover every formerly lazy run/dead-man/rehearse dependency,
# so importing this driver during preflight catches failures before installation.
from joulewise import arm_readiness as readiness
from joulewise import arm_readiness_evidence_t0 as t0_author
from joulewise import night_gate, t0_rehearsal
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
DEADMAN_GRACE_S = 3600
# LEAD-MARGIN-01: 391a194b introduced a flat hour before the resident fence.
# D-180/D-181 permit any quiet window; that pad is not a measurement gate.
# Two minutes separate the exclusive installation cutoff from REQUEST (twelve
# nominal 10 s resident polls to discover the published plan and hand back).
# With the eight-minute plan lead, the exclusive arm-to-t0 floor is ten minutes.
# This is an installation/handback allowance, not load-average settling time:
# that belongs after agent teardown. The installer still rechecks its cutoff.
INSTALL_CLOSE_MARGIN_S = 2 * 60
INSTALL_SPANS: tuple[tuple[str, str], ...] = (("00:00", "24:00"),)
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


def _write_refusal_bytes(path: Path, payload: bytes) -> Path:
    """Allocate immutable refusal records; exclusive creation arbitrates races."""
    index = 0
    while True:
        candidate = path if index == 0 else path.with_name(f"{path.stem}-{index:02d}{path.suffix}")
        try:
            _write_bytes_exclusive(candidate, payload)
            return candidate
        except FileExistsError:
            index += 1


def _refusal_paths(night_dir: Path) -> list[Path]:
    return sorted({*night_dir.glob("refusal.json"), *night_dir.glob("refusal-[0-9]*.json"),
                   *night_dir.glob("calibration-refusal.json"),
                   *night_dir.glob("calibration-refusal.json.*.json")})


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
    _write_refusal_bytes(path, _json_bytes(document))
    return refusal


def _write_gate_refusal(path: Path, receipt: Any) -> None:
    _write_refusal_bytes(path, receipt.to_json_bytes())


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


def _chain_environment(plan: NightPlan, night_dir: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update({
        "NIGHT_PLAN_ID": plan.plan_id,
        "JOULEWISE_NIGHT_PLAN_ID": plan.plan_id,
        "NIGHT_DIR": str(night_dir),
        "MEASUREMENT_ROOT": plan.measurement_root,
        "MEASUREMENT_HEAD": plan.measurement_head,
        # The exact v2 schema has no interpreter or custody-budget field.
        "PY": f"{plan.measurement_root}/.venv/bin/python",
        "CUSTODY_BUDGET_S": str(getattr(plan, "custody_budget_s", 120)),
    })
    # An inherited probe switch must never turn an admitted night into a probe,
    # and an inherited custody budget must never displace the chain's own
    # export (the chain sets JOULEWISE_NIGHT_CUSTODY_BUDGET_S from
    # CUSTODY_BUDGET_S above; a desk shell value would silently outrank it).
    environment.pop("JOULEWISE_NIGHT_CUSTODY_BUDGET_S", None)
    environment.pop("NIGHT_VERIFY_ONLY", None)
    environment.pop("NIGHT_RESERVATION_ARGV_ONLY", None)
    return environment


def reservation_input_paths(plan: NightPlan, plan_path: Path) -> list[Path]:
    """Discover files from the actual chain argv, never a parallel flag list.

    The pinned wrapper and chain expand their arguments with the same driver
    environment as run/probe. The chain's inspection branch prints NUL-separated
    reservation argv before running any reservation, settle or capture.
    """
    environment = _chain_environment(plan, Path(plan.custody_root) / "night")
    environment.update(NIGHT_VERIFY_ONLY="1", NIGHT_RESERVATION_ARGV_ONLY="1")
    completed = subprocess.run(["/bin/zsh", plan.chain_path], env=environment,
        stdin=subprocess.DEVNULL, capture_output=True, timeout=10, check=True)
    if not completed.stdout.endswith(b"\0"):
        raise ValueError("input_digests: chain did not describe reservation arguments")
    paths = {plan_path.resolve()}
    for argument in completed.stdout.decode("utf-8").split("\0")[:-1]:
        if argument.startswith("--"):
            if "=" not in argument:
                continue
            argument = argument.split("=", 1)[1]
        path = Path(argument)
        if not path.is_absolute():
            path = Path(plan.measurement_root) / path
        if path.exists() and not path.is_dir():
            paths.add(path.absolute())
    return sorted(paths)


def _calibration_refusal(night_dir: Path, plan: NightPlan, chain_exit_code: int | None = None) -> dict[str, Any] | None:
    path = night_dir / "calibration-refusal.json"
    if not os.path.lexists(path):
        return None
    payload: Any = None
    raw: str | None = None
    try:
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        if (not isinstance(payload, dict)
                or payload.get("schema") != "joulewise.calibration_refusal.v1"
                or payload.get("plan_id") != plan.plan_id
                or not isinstance(payload.get("code"), str) or not payload["code"]
                or type(payload.get("exit_code")) is not int or payload["exit_code"] != 2
                or (chain_exit_code is not None and payload["exit_code"] != chain_exit_code)):
            raise ValueError("schema, plan_id, code, or exit_code mismatch")
    except (OSError, ValueError, UnicodeError) as exc:
        return _refusal_mapping(_CODES["calibration_refused"], "document_invalid",
                                {"path": str(path), "payload": payload, "raw": raw, "error": str(exc)})
    return _refusal_mapping(_CODES["calibration_refused"], payload["code"], payload)


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
        environment = _chain_environment(plan, night_dir)
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
        *_refusal_paths(night_dir),
        # Informational only: a rerun refusal records a second driver fire that
        # did nothing. It is carried as evidence so the durable publish keeps
        # it, and deliberately left out of _refusal_paths so it never enters
        # result.json's refusal_documents or the courier's refusal discovery.
        *sorted(night_dir.glob("rerun.refusal*.json")),
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
        branch = f"night-results/{plan.plan_id}"
        subprocess.run(
            ["git", "-C", str(clone), "checkout", "-B", branch],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        destination = clone / "docs" / "process_traces" / "night-results" / plan.plan_id
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
            ["git", "-C", str(clone), "commit", "-m", f"record night {plan.plan_id}"],
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
    calibration_refusal: dict[str, Any] | None = None,
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
            "calibration_refusal": calibration_refusal,
            "evidence": {"calibration_refusal": calibration_refusal},
            "calibration_code": (calibration_refusal["detail"]
                                 if calibration_refusal and calibration_refusal["detail"] != "document_invalid"
                                 else None),
            "refusal_documents": [str(path.relative_to(custody_root))
                                  for path in _refusal_paths(night_dir)],
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


def deadman_epoch(plan: NightPlan) -> float:
    """The plan's completion plus recovery grace, rounded up to a minute."""
    try:
        return float(math.ceil(
            (plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S + DEADMAN_GRACE_S)
            / 60
        ) * 60)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"t0_epoch_s/window_max_s cannot derive deadman_epoch_s: {exc}") from exc


def install_close_epoch(plan: NightPlan) -> float:
    # The watchdog owns this existing stand-down lead and imports this driver.
    # Resolve it only when needed, after module initialization on either path.
    from scripts.magistrate_watchdog import PLAN_LEAD_S

    return plan.t0_epoch_s - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S


def _span_minute(value: str, *, close: bool = False) -> int:
    if close and value == "24:00":
        return 24 * 60
    if not isinstance(value, str) or re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is None:
        raise ValueError(f"invalid local install span time: {value!r}")
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def _validate_install_spans(spans: tuple[tuple[str, str], ...]) -> None:
    if not isinstance(spans, tuple):
        raise ValueError("INSTALL_SPANS must be a tuple of (open, close) tuples")
    previous_close = 0
    for span in spans:
        if not isinstance(span, tuple) or len(span) != 2:
            raise ValueError("each install span must be an (open, close) tuple")
        opening = _span_minute(span[0])
        closing = _span_minute(span[1], close=True)
        if opening < previous_close or closing <= opening:
            raise ValueError("install spans must be ordered, disjoint, and close > open")
        previous_close = closing


_validate_install_spans(INSTALL_SPANS)


def _local_span_boundary(day: date, minute: int, *, close: bool) -> float:
    local = datetime.combine(day, wall_time()) + timedelta(minutes=minute)
    # Resolve EACH wall-clock boundary in the host timezone, not in the fixed
    # UTC offset returned by astimezone() for the start of the day. Repeated
    # minutes open on their first occurrence and close on their last; missing
    # spring-forward minutes normalize forward using fold=0.
    candidates = [local.replace(fold=fold).timestamp() for fold in (0, 1)]
    valid = [epoch for epoch in candidates if datetime.fromtimestamp(epoch) == local]
    epoch = (max(valid) if close else min(valid)) if valid else candidates[0]
    return datetime.fromtimestamp(epoch).astimezone().timestamp()


def install_spans_for_day(day: date) -> list[tuple[float, float]]:
    spans = [
        (_local_span_boundary(day, _span_minute(opening), close=False),
         _local_span_boundary(day, _span_minute(closing, close=True), close=True))
        for opening, closing in INSTALL_SPANS
    ]
    for index, (opening, closing) in enumerate(spans):
        if closing <= opening or (index and opening < spans[index - 1][1]):
            raise PlanError("install_spans_unresolvable_on_day",
                f"{day}: offending span {INSTALL_SPANS[index]!r} resolves to {spans[index]!r}; "
                f"previous span={None if index == 0 else (INSTALL_SPANS[index - 1], spans[index - 1])!r}")
    return spans


def install_span_containing(now_epoch_s: float) -> tuple[float, float] | None:
    day = datetime.fromtimestamp(now_epoch_s).astimezone().date()
    return next((span for span in install_spans_for_day(day)
                 if span[0] <= now_epoch_s < span[1]), None)


def calendar_fields(epoch_s: float) -> dict[str, int]:
    local = datetime.fromtimestamp(epoch_s).astimezone()
    return {"Month": local.month, "Day": local.day,
            "Hour": local.hour, "Minute": local.minute}


def schedule(plan: NightPlan) -> dict[str, Any]:
    if plan.t0_epoch_s % 60 != 0:
        raise PlanError("plan_t0_not_minute_aligned",
                        f"t0_epoch_s={plan.t0_epoch_s} must fall on a whole minute")
    # Keep the host-local datetime naive: astimezone() attaches a fixed offset
    # and would hide the alternative epoch for a repeated wall-clock minute.
    local_t0 = datetime.fromtimestamp(plan.t0_epoch_s)
    candidates = {local_t0.replace(fold=fold).timestamp() for fold in (0, 1)}
    valid = {epoch for epoch in candidates if datetime.fromtimestamp(epoch) == local_t0}
    if len(valid) > 1:
        raise PlanError("plan_t0_ambiguous_local_time",
                        f"t0_epoch_s={plan.t0_epoch_s}: {local_t0.isoformat()} occurs twice in local time")
    deadman = deadman_epoch(plan)
    return {
        "t0_epoch_s": plan.t0_epoch_s,
        "install_close_epoch_s": install_close_epoch(plan),
        "deadman_epoch_s": deadman,
        "night_calendar": calendar_fields(plan.t0_epoch_s),
        "deadman_calendar": {key: value for key, value in calendar_fields(deadman).items()
                             if key in {"Hour", "Minute"}},
        "install_spans_today": install_spans_for_day(datetime.fromtimestamp(time.time()).astimezone().date()),
    }


def _completion_epoch_s(plan: NightPlan) -> float:
    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S


def _existing_record(night_dir: Path) -> Path | None:
    return next(
        (night_dir / name for name in _WRITE_ONCE_RECORDS if (night_dir / name).exists()),
        None,
    )


def _write_rerun_refusal(night_dir: Path, plan: NightPlan, existing: Path) -> None:
    """Record a spurious second fire without contradicting the first night.

    A rerun refusal says only "this invocation did nothing"; it is never the
    night's verdict. Two rules keep it from being read as one. It never takes
    the authoritative `refusal.json` name, so the result record's
    `refusal_documents` and the courier's `refusal*.json` discovery cannot pick
    it up; and once `result.json` exists the night has already published a
    verdict, so no document is written at all. The remaining case - a second
    fire while the first night is still running, with only `chain.started` or
    `receipt.json` present - writes `rerun.refusal.json` through the same
    exclusive-create allocator, which numbers concurrent writers
    `rerun.refusal-01.json` and so on.
    """
    if (night_dir / "result.json").exists():
        return
    _write_driver_refusal(
        night_dir / "rerun.refusal.json", plan, _CODES["record_exists"],
        "a write-once night record already exists", {"existing": existing.name},
    )


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
        # §10.3: the frozen gate validator accepts gate codes only. Preserve
        # the driver cause in detail and in the authoritative refusal.json.
        receipt_reason = reason if reason in NIGHT_GATE_REASON_CODES else _CODES["probe_error"]
        failed = night_gate.Receipt(night_gate.SCHEMA, plan.receipt_class, plan.plan_id, "REFUSED",
            tuple(night_gate.ConditionRow(key, "FAIL", None, (), {"detail": detail}) for key in night_gate._CONDITION_IDS),
            night_gate.Refusal(receipt_reason, f"{reason}: {detail}", ()), int(started_monotonic_ns))
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


# Shared custody authentication belongs to the gate; preparation and final GO
# publication re-use the same checks.
PackNightRefusal = night_gate.PackNightRefusal
_pack_bytes = night_gate._pack_bytes
_pack_object = night_gate._pack_object
_pack_digest = night_gate._pack_digest
_pack_no_retry = night_gate._pack_no_retry
_pack_evidence = night_gate._pack_evidence


def _prepare_pack_night(plan: NightPlan, plan_path: Path, plan_raw: bytes):
    """Re-read pinned plan and authority before authoring ARM or publishing GO."""
    _pack_bytes(plan_path, "plan_sha256", hashlib.sha256(plan_raw).hexdigest())
    return night_gate._authenticate_pack_records(plan)


def _author_pack_arm(plan: NightPlan, prepared):
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


def _pack_launch_references(plan: NightPlan, arm):
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


_pack_rehearsal_roots = night_gate._pack_rehearsal_roots


def _produce_pack_go(plan, plan_path, plan_raw, prepared, arm_state, receipt, probes):
    """Final producer reauthentication; publish once only after every check."""
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


def produce_g7_control(control_plan_path, rehearsal_receipt_path, rehearsal_go_path):
    """Present two retained rehearsal artifacts to a fresh production control.

    This post-night command uses the production launcher's real eight-flag
    entry. It never starts a rehearsal or changes the completed night.
    """

    plan_path = Path(control_plan_path)
    plan_raw = plan_path.read_bytes()
    plan = NightPlan.from_mapping(readiness.parse_json_bytes(plan_raw))
    control = Path(plan.custody_root)
    receipt_path = Path(rehearsal_receipt_path)
    go_path = Path(rehearsal_go_path)
    for path in (plan_path, control, receipt_path, go_path):
        if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
            raise PackNightRefusal("G7 paths must be absolute and non-symlink")
    receipt_raw, go_raw = receipt_path.read_bytes(), go_path.read_bytes()
    receipt = readiness.parse_json_bytes(receipt_raw)
    if (set(receipt) != t0_rehearsal._REHEARSAL_RECEIPT_KEYS
            or receipt["schema_version"] != t0_rehearsal.REHEARSAL_RECEIPT_SCHEMA
            or receipt["receipt_class"] != t0_rehearsal.REHEARSAL_RECEIPT_CLASS
            or receipt["claim_eligible"] is not False):
        raise PackNightRefusal("G7 rehearsal receipt")
    window = receipt["window_id"]
    source = Path(receipt["custody_root"])
    if (not window.startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX)
            or source != Path.home() / "night-custody" / window
            or control != source.with_name(window + "-g7-control")
            or not receipt_path.is_relative_to(source)
            or go_path != source / "night/go_receipt.json"
            or not plan_path.is_relative_to(control)):
        raise PackNightRefusal("G7 control/source custody")
    go = readiness.validate_pack_night_go_receipt(readiness.parse_json_bytes(go_raw))
    if go["purpose"] != "T0_REHEARSAL" or go["authorization"]["claim_eligible"] is not False:
        raise PackNightRefusal("G7 rehearsal GO purpose")
    if plan.receipt_class != "TRANSACTION_PACK" or plan.plan_id.startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX):
        raise PackNightRefusal("G7 production plan")
    production_pack = readiness._pack_record(Path(plan.pack_night["pack_root"]))
    if (production_pack["window_id"].startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX)
            or production_pack["plan_id"] != plan.plan_id
            or production_pack["pack_sha256"] != plan.pack_night["pack_sha256"]):
        raise PackNightRefusal("G7 production window_id")
    authorization = _pack_object(Path(plan.pack_night["authorization_record"]["path"]),
        "authorization_record", plan.pack_night["authorization_record"]["sha256"])
    if authorization["purpose"] != "CAMPAIGN_TRANSACTION":
        raise PackNightRefusal("G7 production authorization")
    confirmation = _pack_object(Path(plan.pack_night["confirmation_record"]["path"]),
        "confirmation_record", plan.pack_night["confirmation_record"]["sha256"])
    allowed = {plan_path, Path(plan.pack_night["authorization_record"]["path"]),
               Path(plan.pack_night["confirmation_record"]["path"]), Path(confirmation["table_path"])}
    if any(path.is_file() and path not in allowed for path in control.rglob("*")):
        raise PackNightRefusal("G7 control must be fresh")
    night = control / "night"
    def verify_destination():
        try:
            if control.resolve(strict=True) != control or control.is_symlink():
                raise ValueError("control path changed")
            if night.is_symlink() or (night.exists() and night.resolve(strict=True) != night):
                raise ValueError("night path changed")
        except (OSError, RuntimeError, ValueError) as exc:
            raise PackNightRefusal("G7 destination must be absolute and non-symlink") from exc
    # Check both destinations before mkdir or any artifact write. Directory-FD
    # writes below remain confined even if a path is replaced after this check.
    verify_destination()
    control_stat = control.stat()
    control_fd = os.open(control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(control_fd)
        if (opened.st_dev, opened.st_ino) != (control_stat.st_dev, control_stat.st_ino):
            raise PackNightRefusal("G7 control destination changed")
        try:
            os.mkdir("night", mode=0o700, dir_fd=control_fd)
        except FileExistsError:
            pass
        verify_destination()
        night_stat = night.stat()
        night_fd = os.open("night", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=control_fd)
        opened = os.fstat(night_fd)
        if (opened.st_dev, opened.st_ino) != (night_stat.st_dev, night_stat.st_ino):
            os.close(night_fd)
            raise PackNightRefusal("G7 night destination changed")
    finally:
        os.close(control_fd)
    def write_control(filename, raw):
        verify_destination()
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=night_fd)
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
    def absence():
        return {"consumption_absent": not any(control.rglob("*.consumed.json"))
                and not any(p.is_file() for d in control.rglob("arm_readiness.consumptions") for p in d.rglob("*")),
                "chain_started_absent": not any(control.rglob("chain.started")),
                "checked_monotonic_ns": time.monotonic_ns()}
    try:
        presented = []
        for kind, raw, filename in (("rehearsal_receipt", receipt_raw, "presented_rehearsal_receipt.json"),
                                    ("rehearsal_go", go_raw, "presented_go_receipt.json")):
            _pack_bytes(plan_path, "G7 control plan", readiness.sha256_bytes(plan_raw))
            before = absence()
            target = night / filename
            # The first presented file is the exclusive claim. A racing or resumed
            # producer cannot present anything before successfully creating it.
            write_control(filename, raw)
            argv = _pack_launcher_argv(plan, plan_path, night / "absent-arm.json",
                                      night / "absent-manifest.json", target, confirmation)
            at = time.monotonic_ns()
            result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, check=False)
            _pack_bytes(plan_path, "G7 control plan", readiness.sha256_bytes(plan_raw))
            try:
                refusal = readiness.parse_json_bytes(result.stdout)
            except readiness.ArmReadinessError:
                refusal = {}
            reasons = refusal.get("reason_codes", [])
            presented.append({"kind": kind, "path": str(target), "sha256": readiness.sha256_bytes(raw),
                "refusal": {"reason": reasons[0] if result.returncode == 2 and len(reasons) == 1 else "unexpected_launch_result",
                            "detail": refusal.get("detail", "missing refusal")},
                "first_refusal": before["consumption_absent"] and before["chain_started_absent"],
                "presented_monotonic_ns": at})
        artifact = {"schema_version": t0_rehearsal.G7_CONTROL_SCHEMA, "control_custody_root": str(control),
            "rehearsal_window_id": window, "control_plan_sha256": readiness.sha256_bytes(plan_raw),
            "presented": presented, "absence": absence(), "verdict": "PASS"}
        try:
            t0_rehearsal.validate_g7_control(artifact)
        except ValueError:
            artifact["verdict"] = "FAIL"
        artifact_path = night / "g7_refusal.json"
        raw = readiness.render_json(artifact)
        write_control(artifact_path.name, raw)
        os.fsync(night_fd)
        return {"path": str(artifact_path), "sha256": readiness.sha256_bytes(raw)}

    finally:
        os.close(night_fd)


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

    deadman_epoch_s = deadman_epoch(plan)
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
            receipt = evaluate_night(plan, probes, pack_arm_receipt=arm_state["path"])
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
    gate_message = f"night gate verdict={receipt.verdict}"
    if receipt.verdict == "REFUSED":
        refusal = _refusal_from_object(receipt.refusal) or {}
        detail = " ".join(str(refusal.get("detail", "")).splitlines())[:200]
        gate_message += f" reason={refusal.get('reason')} detail={detail}"
    _append_log(custody_root, gate_message)

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

    calibration_refusal = _calibration_refusal(
        night_dir, plan, chain_exit_code if abort is None else None)
    if calibration_refusal is not None and abort is None:
        _write_driver_refusal(night_dir / "refusal.json", plan,
                              calibration_refusal["reason"], calibration_refusal["detail"],
                              calibration_refusal["evidence"])

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
    elif calibration_refusal is not None:
        verdict = "REFUSED"
        base_exit_code = EXIT_REFUSED
        aborted_reason = calibration_refusal["reason"]
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
        calibration_refusal,
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
    if census_refusal is not None:
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


def _probe_group_absent(pgid: int, timeout_s: float = 1) -> bool:
    # pgrep also works where the sandbox denies killpg(..., 0) after exit.
    try:
        result = subprocess.run(["/usr/bin/pgrep", "-lf", "-g", str(pgid), "."],
                                capture_output=True, text=True, timeout=timeout_s, check=False)
    except (OSError, subprocess.SubprocessError):
        return False  # Unknown census still requires attempted termination.
    return result.returncode == 1 and not result.stdout.strip()


def _stop_probe_group(process: subprocess.Popen[Any]) -> bool:
    """Reap the supervised probe group within the two-second cleanup allowance."""
    deadline = time.monotonic() + 1.5
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=max(0.01, deadline - time.monotonic()))
    except (OSError, subprocess.SubprocessError):
        return False
    while time.monotonic() < deadline:
        if _probe_group_absent(process.pid, min(0.2, max(0.01, deadline - time.monotonic()))):
            return True
        time.sleep(0.02)
    return False


def _atomic_probe_json(path: Path, record: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    _write_json(temporary, record)
    os.replace(temporary, path)


def probe_night(plan_path: Path, receipt_path: Path, timeout_s: float = 600) -> int:
    """Supervise ALL probe input reads and execution under one monotonic deadline."""
    import tempfile
    if not math.isfinite(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s must be finite and positive")
    started, deadline = time.time(), time.monotonic() + timeout_s
    # absolute() performs no input-file read or symlink traversal.
    plan_path, receipt_path = plan_path.absolute(), receipt_path.absolute()
    record = dict(schema="joulewise.night_probe_receipt.v1", plan_id=None,
        plan_sha256=None, measurement_head=None, ledger_head_sha256=None,
        input_digests={}, code_digests={}, driver_python=None, chain_python=None,
        custody_budget_s=None, custody_elapsed_s=0.0, observations=0,
        outcome="refused", refusal_code="probe_worker_failed", phase="startup",
        started_epoch_s=started, finished_epoch_s=None,
        launchd_label=os.environ.get("JOULEWISE_LAUNCHD_LABEL"))
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="night-probe-supervisor-", dir=receipt_path.parent) as directory:
        output, progress = Path(directory) / "worker.json", Path(directory) / "progress.json"
        process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).absolute()),
            "_probe-worker", "--plan", str(plan_path), "--receipt", str(output),
            "--progress", str(progress), "--deadline", str(deadline)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True)
        identity = {"driver_pid": os.getpid(), "chain_pgid": process.pid,
                    "launchd_label": record["launchd_label"]}
        timed_out = False
        stderr = b""
        try:
            # The supervisor owns the identity before any chain can be launched.
            _atomic_probe_json(receipt_path.with_name(receipt_path.name + ".process.json"), identity)
            _, stderr = process.communicate(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            gone = _stop_probe_group(process)
            process.stdout.close()
            process.stderr.close()
        if progress.is_file():
            state = json.loads(progress.read_text())
            record.update(state.get("record", {}))
            record["phase"] = state["phase"]
        if output.is_file():
            record.update(json.loads(output.read_text()))
        record.update(identity, started_epoch_s=started, finished_epoch_s=time.time(), cleanup_proven=gone)
        if timed_out:
            record.update(outcome="timeout", refusal_code="calibration_ledger_custody_timeout",
                          custody_elapsed_s=time.monotonic() - (deadline - timeout_s))
        elif not gone:
            record.update(outcome="refused", refusal_code="probe_process_survived")
        elif not output.is_file():
            record.update(outcome="refused", refusal_code="probe_worker_failed", detail=stderr.decode(errors="replace"))
        _atomic_probe_json(receipt_path, record)
    return 0 if record["outcome"] == "ok" else 2


def _probe_worker(plan_path: Path, receipt_path: Path, progress_path: Path, deadline: float) -> int:
    """Disposable worker; the supervisor bounds every synchronous read below."""
    import tempfile
    from joulewise.night_agent_install import interpreter_identity, probe_bindings

    def phase(name, record=None):
        _atomic_probe_json(progress_path, {"phase": name, "record": record or {}})
    phase("plan")
    started = time.time()
    plan = _load_plan(plan_path)
    phase("bindings", {"plan_id": plan.plan_id, "measurement_head": plan.measurement_head})
    bindings = probe_bindings(plan, plan_path, sys.executable)
    record = dict(bindings, schema="joulewise.night_probe_receipt.v1",
                  custody_budget_s=float(getattr(plan, "custody_budget_s", 120)),
                  custody_elapsed_s=0.0, observations=0, outcome="refused",
                  refusal_code=None, started_epoch_s=started, finished_epoch_s=None,
                  launchd_label=os.environ.get("JOULEWISE_LAUNCHD_LABEL"))
    phase("chain", record)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    # Keep probe refusals away from write-once production night records.
    with tempfile.TemporaryDirectory(prefix="night-probe-", dir=receipt_path.parent) as directory:
        night_dir = Path(directory)
        environment = _chain_environment(plan, night_dir)
        environment["NIGHT_VERIFY_ONLY"] = "1"
        process = subprocess.Popen(["/bin/zsh", plan.chain_path], env=environment,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout = b""
        chain_started = time.monotonic()
        try:
            stdout, _stderr = process.communicate(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            record["outcome"] = "timeout"
            record["custody_elapsed_s"] = time.monotonic() - chain_started
            record["refusal_code"] = "calibration_ledger_custody_timeout"
        finally:
            process.stdout.close()
            process.stderr.close()
        if record["outcome"] != "timeout":
            refusal = _calibration_refusal(night_dir, plan, process.returncode)
            if refusal is not None:
                record["refusal_code"] = refusal["detail"]
                record["calibration_refusal"] = refusal
                if refusal["detail"] != "document_invalid":
                    record["custody_budget_s"] = refusal["evidence"].get("budget_s")
                    record["custody_elapsed_s"] = refusal["evidence"].get("elapsed_s")
            elif process.returncode == 0:
                try:
                    lines = []
                    for line in stdout.decode("utf-8").splitlines():
                        try:
                            value = json.loads(line)
                        except ValueError:
                            continue
                        if isinstance(value, dict) and value.get("verify_only") == "ok":
                            lines.append(value)
                    if len(lines) != 1:
                        raise ValueError("expected one verify-only receipt line")
                    value = lines[0]
                    chain_python = interpreter_identity(value["python"])
                    if chain_python["version"] != value["python_version"]:
                        raise ValueError("chain_python version changed")
                    for field, actual in (("chain_python", chain_python),
                                          ("ledger_head_sha256", value["ledger_head_sha256"])):
                        if actual != bindings[field]:
                            raise ValueError(field + " mismatch")
                    # The reservation echoes digests only for the programs it
                    # knows about; the installer binds a superset (it also pins
                    # the driver and the writer). Reconciliation: every echoed
                    # entry must name a bound path and equal the installer-side
                    # digest, and the receipt then carries the installer-side
                    # set, which validate_probe_receipt recomputes field by
                    # field against PROBE_CODE_PATHS at install time.
                    echoed = value["code_digests"]
                    if not isinstance(echoed, dict) or not echoed:
                        raise ValueError("code_digests missing or invalid")
                    if any(bindings["code_digests"].get(name) != digest
                           for name, digest in echoed.items()):
                        raise ValueError("code_digests mismatch")
                    for field in ("custody_budget_s", "custody_elapsed_s", "observations"):
                        actual = value[field]
                        if isinstance(actual, bool) or not isinstance(actual, (float, int)) or not math.isfinite(actual) or actual < 0:
                            raise ValueError(field + " invalid")
                        record[field] = actual
                    if record["custody_budget_s"] != bindings["custody_budget_s"]:
                        raise ValueError("custody_budget_s mismatch")
                    if not isinstance(record["observations"], int):
                        raise ValueError("observations must be an integer")
                    # Recompute under the SAME supervisor deadline.
                    phase("revalidation", record)
                    if bindings != probe_bindings(plan, plan_path, sys.executable):
                        raise ValueError("probe bindings changed during verification")
                    # Publish the installer-side (superset) binding, never the
                    # reservation's partial echo.
                    record["code_digests"] = bindings["code_digests"]
                    record["outcome"] = "ok"
                except (KeyError, ValueError, OSError, subprocess.SubprocessError) as exc:
                    record["refusal_code"] = "probe_receipt_invalid"
                    record["detail"] = str(exc)
            else:
                record["refusal_code"] = "probe_chain_failed"
        record["finished_epoch_s"] = time.time()
        _atomic_probe_json(receipt_path, record)
    return 0 if record["outcome"] == "ok" else 2


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
    access_probe = subcommands.add_parser("probe")
    access_probe.add_argument("--plan", required=True, type=Path)
    access_probe.add_argument("--receipt", required=True, type=Path)
    access_probe.add_argument("--timeout-s", type=float, default=600)
    worker = subcommands.add_parser("_probe-worker", help=argparse.SUPPRESS)
    worker.add_argument("--plan", required=True, type=Path)
    worker.add_argument("--receipt", required=True, type=Path)
    worker.add_argument("--progress", required=True, type=Path)
    worker.add_argument("--deadline", required=True, type=float)
    scheduling = subcommands.add_parser("schedule")
    scheduling.add_argument("--plan", required=True, type=Path, metavar="PLAN.json")
    preflight = subcommands.add_parser("preflight")
    preflight.add_argument("--plan", required=True, type=Path, metavar="PLAN.json")
    control = subcommands.add_parser("g7-control")
    control.add_argument("--plan", required=True, type=Path)
    control.add_argument("--rehearsal-receipt", required=True, type=Path)
    control.add_argument("--rehearsal-go", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "_probe-worker":
        return _probe_worker(args.plan, args.receipt, args.progress, args.deadline)
    if args.command == "probe":
        try:
            return probe_night(args.plan, args.receipt, args.timeout_s)
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            print(f"night probe refused: {exc}", file=sys.stderr)
            return 2
    if args.command == "schedule":
        try:
            derived = schedule(_load_plan(args.plan))
        except (OSError, ValueError, OverflowError, TypeError) as exc:
            reason = exc.reason if isinstance(exc, PlanError) else "plan_schedule_unrepresentable"
            detail = " ".join(str(exc).split())
            print(f"{reason}: {detail}", file=sys.stderr)
            return 2
        print(json.dumps(derived, sort_keys=True))
        return EXIT_GO
    if args.command == "preflight":
        _load_plan(args.plan)
        print(json.dumps({
            "preflight": "ok",
            "python": sys.executable,
            "version": ".".join(map(str, sys.version_info[:3])),
            # The driver and its direct module-scope project imports; this
            # does not claim to exercise lazy imports inside those modules.
            "modules": ["scripts.run_night"] + [module.__name__ for module in (
                readiness, t0_author, t0_rehearsal, night_gate,
                sys.modules["joulewise.measurement_liveness"],
            )],
        }))
        return 0
    if args.command == "g7-control":
        locator = produce_g7_control(args.plan, args.rehearsal_receipt, args.rehearsal_go)
        sys.stdout.buffer.write(_json_bytes(locator))
        return 0 if json.loads(Path(locator["path"]).read_bytes())["verdict"] == "PASS" else EXIT_REFUSED
    if args.command == "run":
        return run_night(args.plan, courier_bin=args.courier_bin)
    if args.command == "rehearse":
        return run_night(args.plan, rehearsal=True, courier_bin=args.courier_bin)
    return dead_man(args.plan, courier_bin=args.courier_bin)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
