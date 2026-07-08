"""Self-contained remote node worker (D-002, D-009, D-012).

This file is shipped to remote nodes as a single script; the JouleWise package
is not installed there. It therefore mirrors wire-level strings such as
FailureReason values instead of importing :mod:`joulewise` (stream ledger
2026-07-07-2k-nvidia B-2..B-6, B-8). U1 pins task validation, status artifact
writing, clock echo, and the dispatch table seam; U3 registers the
``nvidia-smi`` telemetry handlers while runtime handlers remain additive.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

PROTOCOL_VERSION = 1

STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_UNSUPPORTED = "unsupported"

FAILURE_DID_NOT_FIT = "did_not_fit"
FAILURE_RUNTIME_UNAVAILABLE = "runtime_unavailable"
FAILURE_TELEMETRY_UNAVAILABLE = "telemetry_unavailable"
FAILURE_FORMAT_UNAVAILABLE = "format_unavailable"
FAILURE_PERMISSION_DENIED = "permission_denied"
FAILURE_TRANSPORT_UNAVAILABLE = "transport_unavailable"
FAILURE_UNSUPPORTED_WORKLOAD = "unsupported_workload"
FAILURE_UNKNOWN_ERROR = "unknown_error"

STATUS_JSON = "status.json"
WORKER_LOG = "worker.log"
STATUS_TMP_PREFIX = ".status.json.tmp."
NVIDIA_SMI_BINARY = "nvidia-smi"
NVIDIA_SMI_QUERY = "timestamp,power.draw,temperature.gpu"
NVIDIA_SMI_FORMAT = "csv,noheader,nounits"
NVIDIA_SMI_CSV = "nvidia_smi.csv"
NVIDIA_SMI_IDLE_CSV = "nvidia_smi_idle.csv"
NVIDIA_SMI_PIDFILE = "nvidia_smi.pid"
NVIDIA_SMI_STDERR = "nvidia_smi.stderr"
NVIDIA_SMI_READINESS_TIMEOUT_S = 10.0
NVIDIA_SMI_READINESS_POLL_S = 0.05
NVIDIA_SMI_STOP_TIMEOUT_S = 5.0
NVIDIA_SMI_KILL_TIMEOUT_S = 2.0

TASK_BLOCK_KEYS = ("runtime", "workload", "telemetry")
RUNTIME_OPERATIONS = ("prepare", "warmup", "run_workload", "cleanup")
TELEMETRY_OPERATIONS = ("measure_idle", "start_sampling", "stop_sampling")

Handler = Callable[
    [Dict[str, Any], str, Callable[[str], None]],
    Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]],
]
_DETACHED_NVIDIA_SMI_PROCESSES: Dict[int, subprocess.Popen[Any]] = {}


class WorkerValidationError(ValueError):
    """Raised when the task JSON violates protocol v1."""


def handle_nvidia_smi_start_sampling(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    telemetry = task.get("telemetry") if isinstance(task.get("telemetry"), dict) else {}
    state_dir = task["paths"]["state_dir"]
    interval_ms = _telemetry_interval_ms(telemetry)
    raw_path = os.path.join(state_dir, NVIDIA_SMI_CSV)
    pid_path = os.path.join(state_dir, NVIDIA_SMI_PIDFILE)
    stderr_path = os.path.join(state_dir, NVIDIA_SMI_STDERR)
    command = _nvidia_smi_command(interval_ms)
    metadata: Dict[str, Any] = {
        "command": command,
        "raw_path": raw_path,
        "pidfile": pid_path,
        "interval_ms": interval_ms,
        "query_fields": telemetry.get("query_fields"),
        "rail_manifest": telemetry.get("rail_manifest"),
    }
    try:
        _remove_if_exists(raw_path)
        _remove_if_exists(pid_path)
        _remove_if_exists(stderr_path)
        stdout_handle = open(raw_path, "ab")
        stderr_handle = open(stderr_path, "ab")
        try:
            node_started_at_s = time.time()
            node_monotonic_started_s = time.monotonic()
            process = subprocess.Popen(
                command,
                stdout=stdout_handle,
                stderr=stderr_handle,
                stdin=subprocess.DEVNULL,
            )
        finally:
            stdout_handle.close()
            stderr_handle.close()
    except FileNotFoundError as exc:
        return (
            STATUS_UNSUPPORTED,
            FAILURE_TELEMETRY_UNAVAILABLE,
            "nvidia-smi unavailable: %s" % exc,
            {},
            metadata,
        )
    except OSError as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not start nvidia-smi sampler: %s" % exc,
            {},
            metadata,
        )

    pid_payload = {
        "pid": process.pid,
        "command": command,
        "raw_path": raw_path,
        "stderr_path": stderr_path,
        "node_started_at_s": node_started_at_s,
        "node_monotonic_started_s": node_monotonic_started_s,
        "interval_ms": interval_ms,
        "query_fields": telemetry.get("query_fields"),
        "rail_manifest": telemetry.get("rail_manifest"),
    }
    try:
        _write_json(pid_path, pid_payload)
    except OSError as exc:
        _terminate_process_object(process)
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not write nvidia-smi pidfile: %s" % exc,
            {},
            metadata,
        )

    ready = _wait_for_nvidia_smi_csv(process, raw_path)
    metadata["readiness"] = ready
    metadata["pid"] = process.pid
    if not ready.get("ok"):
        _terminate_process_object(process)
        metadata["stderr_tail"] = _read_tail(stderr_path)
        return (
            STATUS_UNSUPPORTED,
            FAILURE_TELEMETRY_UNAVAILABLE,
            ready.get("message", "nvidia-smi sampler did not become ready"),
            _copy_pidfile_artifact(pid_path, artifacts_dir),
            metadata,
        )

    _DETACHED_NVIDIA_SMI_PROCESSES[process.pid] = process
    log("nvidia-smi sampler ready pid=%s" % process.pid)
    return (
        STATUS_SUCCEEDED,
        None,
        "nvidia-smi sampler started",
        _copy_pidfile_artifact(pid_path, artifacts_dir),
        metadata,
    )


def handle_nvidia_smi_stop_sampling(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    state_dir = task["paths"]["state_dir"]
    pid_path = os.path.join(state_dir, NVIDIA_SMI_PIDFILE)
    raw_path = os.path.join(state_dir, NVIDIA_SMI_CSV)
    metadata: Dict[str, Any] = {"pidfile": pid_path, "raw_path": raw_path}
    artifacts: Dict[str, str] = {}

    try:
        pid_payload = _read_json(pid_path)
        pid = int(pid_payload["pid"])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not read nvidia-smi pidfile: %s" % exc,
            artifacts,
            metadata,
        )

    metadata["pid"] = pid
    metadata["pidfile_payload"] = pid_payload
    _terminate_pid(pid, metadata)
    log("nvidia-smi sampler stop requested pid=%s" % pid)

    if not os.path.exists(raw_path):
        artifacts.update(_copy_pidfile_artifact(pid_path, artifacts_dir))
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "nvidia-smi CSV was not found after sampler stop",
            artifacts,
            metadata,
        )

    try:
        shutil.copy2(raw_path, os.path.join(artifacts_dir, NVIDIA_SMI_CSV))
        artifacts["nvidia_smi_csv"] = NVIDIA_SMI_CSV
        artifacts.update(_copy_pidfile_artifact(pid_path, artifacts_dir))
    except OSError as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not collect nvidia-smi CSV: %s" % exc,
            artifacts,
            metadata,
        )
    return (
        STATUS_SUCCEEDED,
        None,
        "nvidia-smi sampler stopped",
        artifacts,
        metadata,
    )


def handle_nvidia_smi_measure_idle(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    telemetry = task.get("telemetry") if isinstance(task.get("telemetry"), dict) else {}
    interval_ms = _telemetry_interval_ms(telemetry)
    idle_seconds = _telemetry_idle_seconds(telemetry)
    raw_path = os.path.join(artifacts_dir, NVIDIA_SMI_IDLE_CSV)
    stderr_path = os.path.join(artifacts_dir, "nvidia_smi_idle.stderr")
    command = _nvidia_smi_command(interval_ms)
    metadata: Dict[str, Any] = {
        "command": command,
        "raw_artifact": NVIDIA_SMI_IDLE_CSV,
        "interval_ms": interval_ms,
        "idle_seconds": idle_seconds,
        "query_fields": telemetry.get("query_fields"),
        "rail_manifest": telemetry.get("rail_manifest"),
    }
    try:
        _remove_if_exists(raw_path)
        with open(raw_path, "ab") as stdout_handle, open(stderr_path, "ab") as stderr_handle:
            process = subprocess.Popen(
                command,
                stdout=stdout_handle,
                stderr=stderr_handle,
                stdin=subprocess.DEVNULL,
            )
            deadline = time.monotonic() + max(0.0, idle_seconds)
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                remaining_s = deadline - time.monotonic()
                if remaining_s <= 0:
                    break
                time.sleep(min(0.05, remaining_s))
            _terminate_process_object(process)
    except FileNotFoundError as exc:
        _remove_if_exists(raw_path)
        return (
            STATUS_UNSUPPORTED,
            FAILURE_TELEMETRY_UNAVAILABLE,
            "nvidia-smi unavailable: %s" % exc,
            {},
            metadata,
        )
    except OSError as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not run nvidia-smi idle capture: %s" % exc,
            {},
            metadata,
        )

    if not _csv_file_has_parseable_row(raw_path):
        metadata["stderr_tail"] = _read_tail(stderr_path)
        return (
            STATUS_UNSUPPORTED,
            FAILURE_TELEMETRY_UNAVAILABLE,
            "nvidia-smi idle capture did not produce a parseable CSV row",
            {"nvidia_smi_idle_csv": NVIDIA_SMI_IDLE_CSV},
            metadata,
        )
    log("nvidia-smi idle capture completed")
    return (
        STATUS_SUCCEEDED,
        None,
        "nvidia-smi idle capture completed",
        {"nvidia_smi_idle_csv": NVIDIA_SMI_IDLE_CSV},
        metadata,
    )


def _telemetry_interval_ms(telemetry: Dict[str, Any]) -> int:
    value = telemetry.get("interval_ms", 100)
    try:
        interval_ms = int(value)
    except (TypeError, ValueError):
        interval_ms = 100
    return max(1, interval_ms)


def _telemetry_idle_seconds(telemetry: Dict[str, Any]) -> float:
    value = telemetry.get("idle_seconds", 1.0)
    try:
        idle_seconds = float(value)
    except (TypeError, ValueError):
        idle_seconds = 1.0
    return max(0.0, idle_seconds)


def _nvidia_smi_command(interval_ms: int) -> List[str]:
    return [
        NVIDIA_SMI_BINARY,
        "--query-gpu=%s" % NVIDIA_SMI_QUERY,
        "--format=%s" % NVIDIA_SMI_FORMAT,
        "-lms",
        str(interval_ms),
    ]


def _wait_for_nvidia_smi_csv(
    process: subprocess.Popen[Any],
    raw_path: str,
) -> Dict[str, Any]:
    deadline = time.monotonic() + NVIDIA_SMI_READINESS_TIMEOUT_S
    while time.monotonic() < deadline:
        if _csv_file_has_parseable_row(raw_path):
            return {
                "ok": True,
                "ready_check": "first_parseable_nvidia_smi_csv_row",
                "ready_bytes": os.path.getsize(raw_path),
            }
        if process.poll() is not None:
            return {
                "ok": False,
                "message": (
                    "nvidia-smi exited before producing a parseable CSV row "
                    "(returncode %s)" % process.returncode
                ),
            }
        time.sleep(NVIDIA_SMI_READINESS_POLL_S)
    return {
        "ok": False,
        "message": (
            "nvidia-smi did not produce a parseable CSV row within %.1f s"
            % NVIDIA_SMI_READINESS_TIMEOUT_S
        ),
    }


def _csv_file_has_parseable_row(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        return False
    return any(_line_is_parseable_nvidia_smi_row(line) for line in lines)


def _line_is_parseable_nvidia_smi_row(line: str) -> bool:
    parts = [part.strip() for part in line.strip().split(",")]
    if len(parts) != 3:
        return False
    try:
        datetime.datetime.strptime(parts[0], "%Y/%m/%d %H:%M:%S.%f")
        float(parts[1])
        float(parts[2])
    except (TypeError, ValueError):
        return False
    return True


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    tmp_path = path + ".tmp.%s" % os.getpid()
    try:
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        _remove_if_exists(tmp_path)


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload


def _copy_pidfile_artifact(pid_path: str, artifacts_dir: str) -> Dict[str, str]:
    try:
        shutil.copy2(pid_path, os.path.join(artifacts_dir, NVIDIA_SMI_PIDFILE))
    except OSError:
        return {}
    return {"nvidia_smi_pidfile": NVIDIA_SMI_PIDFILE}


def _terminate_process_object(process: subprocess.Popen[Any]) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.communicate(timeout=NVIDIA_SMI_STOP_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()


def _terminate_pid(pid: int, metadata: Dict[str, Any]) -> None:
    cached_process = _DETACHED_NVIDIA_SMI_PROCESSES.pop(pid, None)
    if cached_process is not None:
        _terminate_process_object(cached_process)
        metadata["termination"] = "cached_popen"
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        metadata["termination"] = "already_exited"
        return
    except OSError as exc:
        metadata["termination_error"] = str(exc)
        return

    if _wait_for_pid_exit(pid, NVIDIA_SMI_STOP_TIMEOUT_S):
        metadata["termination"] = "sigterm"
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        metadata["termination"] = "sigterm"
        return
    except OSError as exc:
        metadata["termination_error"] = str(exc)
        return
    metadata["termination"] = "sigkill"
    if not _wait_for_pid_exit(pid, NVIDIA_SMI_KILL_TIMEOUT_S):
        metadata["termination_warning"] = "pid still visible after SIGKILL"


def _wait_for_pid_exit(pid: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except OSError:
            return False
        time.sleep(0.05)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    return False


def _read_tail(path: str, limit: int = 2000) -> str:
    try:
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - limit))
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def _remove_if_exists(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    except OSError:
        pass


OPERATION_HANDLERS: Dict[Tuple[str, str], Handler] = {
    ("telemetry", "measure_idle"): handle_nvidia_smi_measure_idle,
    ("telemetry", "start_sampling"): handle_nvidia_smi_start_sampling,
    ("telemetry", "stop_sampling"): handle_nvidia_smi_stop_sampling,
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="JouleWise node worker")
    parser.add_argument("--task", help="path to task JSON")
    parser.add_argument("--artifacts", help="directory for worker artifacts")
    parser.add_argument("--clock-echo", action="store_true", help="print node clock marker JSON")
    args = parser.parse_args(argv)

    if args.clock_echo:
        return clock_echo()

    if not args.task or not args.artifacts:
        print("--task and --artifacts are required unless --clock-echo is used", file=sys.stderr)
        return 2
    return run_task(args.task, args.artifacts)


def clock_echo() -> int:
    print(
        json.dumps(
            {"node_time_s": time.time(), "monotonic_s": time.monotonic()},
            sort_keys=True,
        )
    )
    return 0


def run_task(task_path: str, artifacts_dir: str) -> int:
    try:
        os.makedirs(artifacts_dir, exist_ok=True)
    except OSError as exc:
        print("cannot create artifacts directory: %s" % exc, file=sys.stderr)
        return 2

    started_at_s = time.time()
    monotonic_started_s = time.monotonic()
    artifacts: Dict[str, str] = {}
    task: Optional[Dict[str, Any]] = None
    status = STATUS_FAILED
    failure_reason: Optional[str] = FAILURE_UNKNOWN_ERROR
    message = "worker failed before task execution"
    metadata: Dict[str, Any] = {}

    def log(line: str) -> None:
        try:
            write_log_line(artifacts_dir, line)
        except OSError as exc:
            metadata.setdefault("worker_log_errors", []).append(str(exc))
        else:
            artifacts["worker_log"] = WORKER_LOG

    try:
        log("worker started")
        task = load_task(task_path)
        apply_task_identity_to_metadata(task, metadata)
        validate_task(task)
        os.makedirs(task["paths"]["state_dir"], exist_ok=True)
        log("task validated")

        handler = OPERATION_HANDLERS.get((task["task_type"], task["operation"]))
        if handler is None:
            status = STATUS_UNSUPPORTED
            failure_reason = FAILURE_UNSUPPORTED_WORKLOAD
            message = (
                "task_type=%s operation=%s is not implemented in this worker build"
                % (task["task_type"], task["operation"])
            )
            log(message)
        else:
            status, failure_reason, message, produced_artifacts, produced_metadata = handler(
                task,
                artifacts_dir,
                log,
            )
            artifacts.update(produced_artifacts)
            metadata.update(produced_metadata)
            log("handler completed with status=%s" % status)
    except WorkerValidationError as exc:
        status = STATUS_FAILED
        failure_reason = FAILURE_UNKNOWN_ERROR
        message = str(exc)
        log("validation failed: %s" % message)
    except Exception as exc:  # noqa: BLE001 - remote worker must never crash bare.
        status = STATUS_FAILED
        failure_reason = FAILURE_UNKNOWN_ERROR
        message = "%s: %s" % (exc.__class__.__name__, exc)
        log("unexpected failure: %s" % message)

    ended_at_s = time.time()
    monotonic_ended_s = time.monotonic()
    artifacts["status_json"] = STATUS_JSON
    status_payload = build_status_payload(
        task=task,
        status=status,
        failure_reason=failure_reason,
        message=message,
        started_at_s=started_at_s,
        ended_at_s=ended_at_s,
        monotonic_started_s=monotonic_started_s,
        monotonic_ended_s=monotonic_ended_s,
        artifacts=artifacts,
        metadata=metadata,
    )
    try:
        write_status_atomic(artifacts_dir, status_payload)
    except OSError as exc:
        print("cannot write status.json: %s" % exc, file=sys.stderr)
        return 2
    return 0 if status == STATUS_SUCCEEDED else 1


def load_task(task_path: str) -> Dict[str, Any]:
    try:
        with open(task_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise WorkerValidationError("malformed task JSON: %s" % exc) from exc
    except OSError as exc:
        raise WorkerValidationError("cannot read task JSON: %s" % exc) from exc
    if not isinstance(payload, dict):
        raise WorkerValidationError("task JSON must be an object")
    return payload


def validate_task(task: Dict[str, Any]) -> None:
    if "protocol_version" not in task:
        raise WorkerValidationError("protocol_version is required and must be integer 1")
    version = task["protocol_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != PROTOCOL_VERSION:
        raise WorkerValidationError("protocol_version must be integer 1, got %r" % (version,))

    for key in ("task_id", "run_id", "task_type", "operation"):
        if key not in task:
            raise WorkerValidationError("%s is required" % key)
        if not isinstance(task[key], str) or not task[key].strip():
            raise WorkerValidationError("%s must be a non-empty string" % key)

    if "node_role" not in task:
        raise WorkerValidationError("node_role is required and may be null")
    if task["node_role"] is not None and not isinstance(task["node_role"], str):
        raise WorkerValidationError("node_role must be null or a string")

    if "paths" not in task or not isinstance(task["paths"], dict):
        raise WorkerValidationError("paths must be an object with paths.state_dir")
    state_dir = task["paths"].get("state_dir")
    if not isinstance(state_dir, str) or not state_dir.strip():
        raise WorkerValidationError("paths.state_dir must be a non-empty string")

    present_blocks = [key for key in TASK_BLOCK_KEYS if key in task]
    if len(present_blocks) != 1:
        raise WorkerValidationError(
            "task must include exactly one task-specific block: runtime, workload, or telemetry"
        )
    block_key = present_blocks[0]
    if not isinstance(task[block_key], dict):
        raise WorkerValidationError("%s must be an object" % block_key)

    task_type = task["task_type"]
    operation = task["operation"]
    if task_type == "runtime":
        expected = "workload" if operation == "run_workload" else "runtime"
        if operation in RUNTIME_OPERATIONS and block_key != expected:
            raise WorkerValidationError(
                "runtime operation %s requires %s block" % (operation, expected)
            )
    elif task_type == "telemetry":
        if operation in TELEMETRY_OPERATIONS and block_key != "telemetry":
            raise WorkerValidationError("telemetry operation %s requires telemetry block" % operation)


def build_status_payload(
    *,
    task: Optional[Dict[str, Any]],
    status: str,
    failure_reason: Optional[str],
    message: str,
    started_at_s: float,
    ended_at_s: float,
    monotonic_started_s: float,
    monotonic_ended_s: float,
    artifacts: Dict[str, str],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "task_id": task.get("task_id") if isinstance(task, dict) else None,
        "task_type": task.get("task_type") if isinstance(task, dict) else None,
        "operation": task.get("operation") if isinstance(task, dict) else None,
        "node_role": task.get("node_role") if isinstance(task, dict) else None,
        "status": status,
        "failure_reason": failure_reason,
        "message": message,
        "started_at_s": started_at_s,
        "ended_at_s": ended_at_s,
        "monotonic_started_s": monotonic_started_s,
        "monotonic_ended_s": monotonic_ended_s,
        "artifacts": dict(sorted(artifacts.items())),
        "metadata": metadata,
    }


def write_status_atomic(artifacts_dir: str, payload: Dict[str, Any]) -> None:
    tmp_name = STATUS_TMP_PREFIX + str(os.getpid())
    tmp_path = os.path.join(artifacts_dir, tmp_name)
    status_path = os.path.join(artifacts_dir, STATUS_JSON)
    try:
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, status_path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except OSError:
            pass


def write_log_line(artifacts_dir: str, line: str) -> None:
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(artifacts_dir, WORKER_LOG), "a", encoding="utf-8") as handle:
        handle.write("%s %s\n" % (timestamp, line))


def apply_task_identity_to_metadata(task: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    metadata["worker_build"] = "u1-protocol-harness"


if __name__ == "__main__":
    sys.exit(main())
