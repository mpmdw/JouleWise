"""Self-contained remote node worker (D-002, D-009, D-012).

This file is shipped to remote nodes as a single script; the JouleWise package
is not installed there. It therefore mirrors wire-level strings such as
FailureReason values instead of importing :mod:`joulewise` (stream ledger
2026-07-07-2k-nvidia B-2..B-6, B-8). U1 pins task validation, status artifact
writing, clock echo, and an empty dispatch table; concrete telemetry/runtime
handlers are added by later units.
"""

from __future__ import annotations

import argparse
import json
import os
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

TASK_BLOCK_KEYS = ("runtime", "workload", "telemetry")
RUNTIME_OPERATIONS = ("prepare", "warmup", "run_workload", "cleanup")
TELEMETRY_OPERATIONS = ("measure_idle", "start_sampling", "stop_sampling")

Handler = Callable[
    [Dict[str, Any], str, Callable[[str], None]],
    Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]],
]


class WorkerValidationError(ValueError):
    """Raised when the task JSON violates protocol v1."""


# Later units register concrete operation handlers here. U1 intentionally
# leaves the table empty so every structurally valid task is unsupported.
OPERATION_HANDLERS: Dict[Tuple[str, str], Handler] = {}


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
