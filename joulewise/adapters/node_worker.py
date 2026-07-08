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
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

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
VLLM_BINARY = "vllm"
VLLM_COMMAND_BASE = [VLLM_BINARY, "serve"]
VLLM_HOST = "127.0.0.1"
VLLM_HEALTH_PATH = "/health"
VLLM_COMPLETIONS_PATH = "/v1/completions"
VLLM_PIDFILE = "vllm.pid"
VLLM_STDERR = "vllm.stderr"
VLLM_STDOUT = "vllm.stdout"
VLLM_READINESS_TIMEOUT_S = 300.0
VLLM_READINESS_POLL_S = 0.1
VLLM_REQUEST_TIMEOUT_S = 60.0
VLLM_RUN_TIMEOUT_S = 600.0
VLLM_STOP_TIMEOUT_S = 10.0
VLLM_KILL_TIMEOUT_S = 3.0
VLLM_EVENTS_JSONL = "events.jsonl"
VLLM_RESPONSE_TXT = "response.txt"
VLLM_TOKENS_JSONL = "tokens.jsonl"
VLLM_WARMUP_PROMPT = "JouleWise warmup."
VLLM_WARMUP_MAX_TOKENS = 1
VLLM_OOM_PATTERNS = (
    "cuda out of memory",
    "outofmemoryerror",
    "out of memory",
    "cublas_status_alloc_failed",
    "cuda error: memory allocation",
    "vllm worker got oom",
)

TASK_BLOCK_KEYS = ("runtime", "workload", "telemetry")
RUNTIME_OPERATIONS = ("prepare", "warmup", "run_workload", "cleanup")
TELEMETRY_OPERATIONS = ("measure_idle", "start_sampling", "stop_sampling")

Handler = Callable[
    [Dict[str, Any], str, Callable[[str], None]],
    Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]],
]
_DETACHED_NVIDIA_SMI_PROCESSES: Dict[int, subprocess.Popen[Any]] = {}
_DETACHED_VLLM_PROCESSES: Dict[int, subprocess.Popen[Any]] = {}


class WorkerValidationError(ValueError):
    """Raised when the task JSON violates protocol v1."""


class VllmHttpError(RuntimeError):
    """HTTP error carrying vLLM response body text for classification."""

    pass


def handle_vllm_prepare(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    runtime = task.get("runtime") if isinstance(task.get("runtime"), dict) else {}
    state_dir = task["paths"]["state_dir"]
    pid_path = os.path.join(state_dir, VLLM_PIDFILE)
    stdout_path = os.path.join(state_dir, VLLM_STDOUT)
    stderr_path = os.path.join(state_dir, VLLM_STDERR)
    port = _vllm_port(runtime)
    command = _vllm_serve_command(runtime, port)
    metadata: Dict[str, Any] = {
        "command": command,
        "pidfile": pid_path,
        "port": port,
        "host": VLLM_HOST,
        "health_endpoint": _vllm_url(port, VLLM_HEALTH_PATH),
        "oom_patterns": list(VLLM_OOM_PATTERNS),
        "readiness_timeout_s": _task_timeout_s(task, VLLM_READINESS_TIMEOUT_S),
    }

    try:
        _remove_if_exists(pid_path)
        _remove_if_exists(stdout_path)
        _remove_if_exists(stderr_path)
        stdout_handle = open(stdout_path, "ab")
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
            ps_lstart = _process_lstart(process.pid)
        finally:
            stdout_handle.close()
            stderr_handle.close()
    except FileNotFoundError as exc:
        return (
            STATUS_UNSUPPORTED,
            FAILURE_RUNTIME_UNAVAILABLE,
            "vLLM launcher unavailable: %s" % exc,
            {},
            metadata,
        )
    except OSError as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not start vLLM server: %s" % exc,
            {},
            metadata,
        )

    pid_payload = {
        "pid": process.pid,
        "command": command,
        "host": VLLM_HOST,
        "port": port,
        "health_path": VLLM_HEALTH_PATH,
        "completions_path": VLLM_COMPLETIONS_PATH,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "node_started_at_s": node_started_at_s,
        "node_monotonic_started_s": node_monotonic_started_s,
        "ps_lstart": ps_lstart,
        "served_model_name": _vllm_served_model_name(runtime),
    }
    try:
        _write_json(pid_path, pid_payload)
    except OSError as exc:
        _terminate_process_object_with_timeouts(process, VLLM_STOP_TIMEOUT_S)
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not write vLLM pidfile: %s" % exc,
            {},
            metadata,
        )

    ready = _wait_for_vllm_health(
        process,
        port,
        stderr_path,
        timeout_s=_task_timeout_s(task, VLLM_READINESS_TIMEOUT_S),
    )
    metadata["readiness"] = ready
    metadata["pid"] = process.pid
    metadata["stderr_tail"] = _read_tail(stderr_path)
    artifacts = _copy_vllm_pidfile_artifact(pid_path, artifacts_dir)
    if not ready.get("ok"):
        _terminate_process_object_with_timeouts(process, VLLM_STOP_TIMEOUT_S)
        readiness_text = "%s\n%s\n%s" % (
            metadata.get("stderr_tail", ""),
            ready.get("stderr_tail", ""),
            ready.get("message", ""),
        )
        if _text_has_vllm_oom(readiness_text):
            return (
                STATUS_UNSUPPORTED,
                FAILURE_DID_NOT_FIT,
                ready.get("message", "vLLM server failed with out-of-memory evidence"),
                artifacts,
                metadata,
            )
        if _text_has_import_unavailable(readiness_text):
            return (
                STATUS_UNSUPPORTED,
                FAILURE_RUNTIME_UNAVAILABLE,
                ready.get("message", "vLLM server failed with import/module evidence"),
                artifacts,
                metadata,
            )
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            ready.get("message", "vLLM server did not become ready"),
            artifacts,
            metadata,
        )

    _DETACHED_VLLM_PROCESSES[process.pid] = process
    log("vLLM server ready pid=%s port=%s" % (process.pid, port))
    return (
        STATUS_SUCCEEDED,
        None,
        "vLLM server started",
        artifacts,
        metadata,
    )


def handle_vllm_warmup(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    del artifacts_dir
    runtime = task.get("runtime") if isinstance(task.get("runtime"), dict) else {}
    server = _read_vllm_server(task["paths"]["state_dir"])
    metadata: Dict[str, Any] = {
        "pidfile": server.get("pidfile"),
        "port": server.get("port"),
        "request_path": VLLM_COMPLETIONS_PATH,
        "warmup_max_tokens": VLLM_WARMUP_MAX_TOKENS,
    }
    request_payload = {
        "model": server.get("served_model_name") or _vllm_served_model_name(runtime),
        "prompt": VLLM_WARMUP_PROMPT,
        "max_tokens": VLLM_WARMUP_MAX_TOKENS,
        "temperature": 0.0,
        "top_p": 1.0,
        "stream": False,
    }
    try:
        _vllm_json_post(int(server["port"]), VLLM_COMPLETIONS_PATH, request_payload)
    except Exception as exc:  # noqa: BLE001 - worker maps backend failures structurally.
        stderr_tail = _read_tail(str(server.get("stderr_path", "")))
        metadata["stderr_tail"] = stderr_tail
        metadata["exception"] = "%s: %s" % (exc.__class__.__name__, exc)
        if _text_has_vllm_oom(stderr_tail) or _text_has_vllm_oom(str(exc)):
            return (
                STATUS_UNSUPPORTED,
                FAILURE_DID_NOT_FIT,
                "vLLM warmup failed with out-of-memory evidence",
                {},
                metadata,
            )
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "vLLM warmup request failed: %s" % exc,
            {},
            metadata,
        )
    log("vLLM warmup completed")
    return (
        STATUS_SUCCEEDED,
        None,
        "vLLM warmup completed",
        {},
        metadata,
    )


def handle_vllm_run_workload(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    workload = task.get("workload") if isinstance(task.get("workload"), dict) else {}
    server = _read_vllm_server(task["paths"]["state_dir"])
    response_path = os.path.join(artifacts_dir, VLLM_RESPONSE_TXT)
    tokens_path = os.path.join(artifacts_dir, VLLM_TOKENS_JSONL)
    events_path = os.path.join(artifacts_dir, VLLM_EVENTS_JSONL)
    max_tokens = _positive_int_or_default(workload.get("output_tokens"), 1)
    sampling_params = dict(workload.get("sampling_params") or {})
    sampling_params["max_tokens"] = _positive_int_or_default(
        sampling_params.get("max_tokens"),
        max_tokens,
    )
    request_payload = {
        "model": server.get("served_model_name"),
        "prompt": _workload_prompt(workload),
        "stream": True,
    }
    request_payload.update(sampling_params)
    metadata: Dict[str, Any] = {
        "pidfile": server.get("pidfile"),
        "port": server.get("port"),
        "request_path": VLLM_COMPLETIONS_PATH,
        "sampling_params": sampling_params,
        "requested_output_tokens": max_tokens,
        "phase_boundary_method": "first_stream_chunk",
    }
    events: List[Dict[str, Any]] = []
    token_count = 0
    text_parts: List[str] = []

    try:
        _append_runtime_event(
            events,
            "phase_start",
            "prefill",
            "vLLM prefill started",
            {
                "phase_boundary_method": "first_stream_chunk",
                "requested_output_tokens": max_tokens,
                "sampling_params": sampling_params,
            },
        )
        with open(tokens_path, "w", encoding="utf-8") as tokens_handle:
            for piece in _vllm_stream_completion(
                int(server["port"]),
                VLLM_COMPLETIONS_PATH,
                request_payload,
                timeout_s=VLLM_RUN_TIMEOUT_S,
            ):
                timestamp_s = time.time()
                if token_count == 0:
                    _append_runtime_event(
                        events,
                        "phase_end",
                        "prefill",
                        "vLLM prefill completed",
                        {"phase_boundary_method": "first_stream_chunk"},
                        timestamp_s=timestamp_s,
                    )
                    _append_runtime_event(
                        events,
                        "phase_start",
                        "decode",
                        "vLLM decode started",
                        {
                            "phase_boundary_method": "first_stream_chunk",
                            "requested_output_tokens": max_tokens,
                        },
                        timestamp_s=timestamp_s,
                    )
                text_parts.append(piece)
                token_record = {
                    "index": token_count,
                    "timestamp_s": timestamp_s,
                    "text": piece,
                }
                tokens_handle.write(json.dumps(token_record, sort_keys=True) + "\n")
                token_count += 1
        if token_count == 0:
            timestamp_s = time.time()
            _append_runtime_event(
                events,
                "phase_end",
                "prefill",
                "vLLM prefill completed without emitted tokens",
                {"phase_boundary_method": "first_stream_chunk"},
                timestamp_s=timestamp_s,
            )
            _append_runtime_event(
                events,
                "phase_start",
                "decode",
                "vLLM decode started without emitted tokens",
                {
                    "phase_boundary_method": "first_stream_chunk",
                    "requested_output_tokens": max_tokens,
                },
                timestamp_s=timestamp_s,
            )
        _append_runtime_event(
            events,
            "phase_end",
            "decode",
            "vLLM decode completed",
            {
                "phase_boundary_method": "first_stream_chunk",
                "emitted_tokens": token_count,
                "requested_output_tokens": max_tokens,
            },
        )
        with open(response_path, "w", encoding="utf-8") as response_handle:
            response_handle.write("".join(text_parts))
        _write_jsonl(events_path, events)
    except Exception as exc:  # noqa: BLE001 - worker maps backend failures structurally.
        stderr_tail = _read_tail(str(server.get("stderr_path", "")))
        metadata["stderr_tail"] = stderr_tail
        metadata["exception"] = "%s: %s" % (exc.__class__.__name__, exc)
        if _text_has_vllm_oom(stderr_tail) or _text_has_vllm_oom(str(exc)):
            return (
                STATUS_UNSUPPORTED,
                FAILURE_DID_NOT_FIT,
                "vLLM workload failed with out-of-memory evidence",
                _existing_runtime_artifacts(artifacts_dir),
                metadata,
            )
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "vLLM workload request failed: %s" % exc,
            _existing_runtime_artifacts(artifacts_dir),
            metadata,
        )

    metadata["emitted_tokens"] = token_count
    log("vLLM workload completed tokens=%s" % token_count)
    return (
        STATUS_SUCCEEDED,
        None,
        "vLLM workload completed",
        {
            "events_jsonl": VLLM_EVENTS_JSONL,
            "response_txt": VLLM_RESPONSE_TXT,
            "tokens_jsonl": VLLM_TOKENS_JSONL,
        },
        metadata,
    )


def handle_vllm_cleanup(
    task: Dict[str, Any],
    artifacts_dir: str,
    log: Callable[[str], None],
) -> Tuple[str, Optional[str], str, Dict[str, str], Dict[str, Any]]:
    del artifacts_dir
    state_dir = task["paths"]["state_dir"]
    pid_path = os.path.join(state_dir, VLLM_PIDFILE)
    metadata: Dict[str, Any] = {"pidfile": pid_path}
    try:
        pid_payload = _read_json(pid_path)
        pid = int(pid_payload["pid"])
    except FileNotFoundError:
        metadata["termination"] = "no_pidfile"
        return (
            STATUS_SUCCEEDED,
            None,
            "vLLM server was not running",
            {},
            metadata,
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "could not read vLLM pidfile: %s" % exc,
            {},
            metadata,
        )

    metadata["pid"] = pid
    metadata["pidfile_payload"] = pid_payload
    if pid not in _DETACHED_VLLM_PROCESSES and not _pidfile_matches_live_process(pid_payload, metadata):
        metadata["termination"] = "stale_pidfile"
        _remove_if_exists(pid_path)
        return (
            STATUS_SUCCEEDED,
            None,
            "vLLM pidfile was stale; no matching process was signaled",
            {},
            metadata,
        )
    _terminate_vllm_pid(pid, metadata)
    _remove_if_exists(pid_path)
    log("vLLM cleanup requested pid=%s" % pid)
    return (
        STATUS_SUCCEEDED,
        None,
        "vLLM server stopped",
        {},
        metadata,
    )


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
    metadata.update(_node_timezone_metadata())
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
            ps_lstart = _process_lstart(process.pid)
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
        "ps_lstart": ps_lstart,
        "interval_ms": interval_ms,
        "query_fields": telemetry.get("query_fields"),
        "rail_manifest": telemetry.get("rail_manifest"),
    }
    pid_payload.update(_node_timezone_metadata())
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
    if pid not in _DETACHED_NVIDIA_SMI_PROCESSES and not _pidfile_matches_live_process(pid_payload, metadata):
        metadata["termination"] = "stale_pidfile"
        _remove_if_exists(pid_path)
        return (
            STATUS_FAILED,
            FAILURE_UNKNOWN_ERROR,
            "nvidia-smi pidfile was stale; no matching sampler was signaled",
            artifacts,
            metadata,
        )
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
    metadata.update(_node_timezone_metadata())
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


def _task_timeout_s(task: Dict[str, Any], default: float) -> float:
    try:
        value = float(task.get("timeout_s", default))
    except (TypeError, ValueError):
        value = default
    return max(0.1, value)


def _node_timezone_metadata() -> Dict[str, Any]:
    now = datetime.datetime.now().astimezone()
    offset = now.utcoffset()
    metadata: Dict[str, Any] = {"node_tzname": now.tzname()}
    if offset is not None:
        metadata["node_utc_offset_s"] = offset.total_seconds()
    return metadata


def _nvidia_smi_command(interval_ms: int) -> List[str]:
    return [
        NVIDIA_SMI_BINARY,
        "--query-gpu=%s" % NVIDIA_SMI_QUERY,
        "--format=%s" % NVIDIA_SMI_FORMAT,
        "-lms",
        str(interval_ms),
    ]


def _vllm_serve_command(runtime: Dict[str, Any], port: int) -> List[str]:
    model = runtime.get("model") if isinstance(runtime.get("model"), dict) else {}
    quantization = runtime.get("quantization") if isinstance(runtime.get("quantization"), dict) else {}
    options = runtime.get("options") if isinstance(runtime.get("options"), dict) else {}
    model_arg = str(model.get("source") or model.get("name") or "")
    command = list(VLLM_COMMAND_BASE)
    if model_arg:
        command.append(model_arg)
    command.extend(["--host", VLLM_HOST, "--port", str(port)])

    served_model_name = _vllm_served_model_name(runtime)
    if served_model_name:
        command.extend(["--served-model-name", served_model_name])
    if model.get("revision"):
        command.extend(["--revision", str(model["revision"])])
    if quantization.get("name") and str(quantization.get("name")) != "none":
        command.extend(["--quantization", str(quantization["name"])])

    option_flags = {
        "tensor_parallel_size": "--tensor-parallel-size",
        "gpu_memory_utilization": "--gpu-memory-utilization",
        "dtype": "--dtype",
        "max_model_len": "--max-model-len",
        "download_dir": "--download-dir",
    }
    for key, flag in option_flags.items():
        value = options.get(key)
        if value is not None:
            command.extend([flag, str(value)])

    extra_args = options.get("extra_args")
    if isinstance(extra_args, list):
        command.extend(str(item) for item in extra_args)
    return command


def _vllm_served_model_name(runtime: Dict[str, Any]) -> str:
    options = runtime.get("options") if isinstance(runtime.get("options"), dict) else {}
    model = runtime.get("model") if isinstance(runtime.get("model"), dict) else {}
    return str(options.get("served_model_name") or model.get("name") or "joulewise-vllm")


def _vllm_port(runtime: Dict[str, Any]) -> int:
    options = runtime.get("options") if isinstance(runtime.get("options"), dict) else {}
    value = options.get("port")
    try:
        port = int(value)
    except (TypeError, ValueError):
        port = _choose_free_local_port()
    return max(1, min(65535, port))


def _choose_free_local_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((VLLM_HOST, 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def _vllm_url(port: int, path: str) -> str:
    return "http://%s:%s%s" % (VLLM_HOST, port, path)


def _wait_for_vllm_health(
    process: subprocess.Popen[Any],
    port: int,
    stderr_path: str,
    *,
    timeout_s: float,
) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    last_error = ""
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stderr_tail = _read_tail(stderr_path)
            return {
                "ok": False,
                "message": "vLLM exited before readiness (returncode %s)" % process.returncode,
                "stderr_tail": stderr_tail,
            }
        try:
            request = urllib.request.Request(_vllm_url(port, VLLM_HEALTH_PATH), method="GET")
            with urllib.request.urlopen(request, timeout=1.0) as response:
                status = getattr(response, "status", response.getcode())
                if 200 <= int(status) < 300:
                    return {
                        "ok": True,
                        "ready_check": "http_get_health",
                        "status": int(status),
                    }
                last_error = "HTTP %s" % status
        except (OSError, urllib.error.URLError, ValueError) as exc:
            last_error = str(exc)
        time.sleep(VLLM_READINESS_POLL_S)
    return {
        "ok": False,
        "message": (
            "vLLM health endpoint did not become ready within %.1f s: %s"
            % (timeout_s, last_error)
        ),
    }


def _read_vllm_server(state_dir: str) -> Dict[str, Any]:
    pid_path = os.path.join(state_dir, VLLM_PIDFILE)
    payload = _read_json(pid_path)
    payload["pidfile"] = pid_path
    return payload


def _vllm_json_post(port: int, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    request = urllib.request.Request(
        _vllm_url(port, path),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=VLLM_REQUEST_TIMEOUT_S) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VllmHttpError("HTTP %s from vLLM %s: %s" % (exc.code, path, body)) from exc
    if not body:
        return {}
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise ValueError("vLLM response JSON must be an object")
    return parsed


def _vllm_stream_completion(
    port: int,
    path: str,
    payload: Dict[str, Any],
    *,
    timeout_s: float,
) -> Iterator[str]:
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    request = urllib.request.Request(
        _vllm_url(port, path),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = urllib.request.urlopen(request, timeout=timeout_s)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VllmHttpError("HTTP %s from vLLM %s: %s" % (exc.code, path, body)) from exc
    with response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            if line.startswith("data:"):
                line = line[len("data:") :].strip()
            if line == "[DONE]":
                break
            payload_obj = json.loads(line)
            if not isinstance(payload_obj, dict):
                continue
            for piece in _completion_text_pieces(payload_obj):
                if piece:
                    yield piece


def _completion_text_pieces(payload: Dict[str, Any]) -> Iterator[str]:
    choices = payload.get("choices")
    if not isinstance(choices, list):
        return
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        if "text" in choice:
            yield str(choice.get("text") or "")
        elif isinstance(choice.get("delta"), dict):
            yield str(choice["delta"].get("content") or "")


def _workload_prompt(workload: Dict[str, Any]) -> str:
    if workload.get("prompt_text") is not None:
        return str(workload["prompt_text"])
    if workload.get("dataset_ref") is not None:
        return "Dataset reference: %s" % workload["dataset_ref"]
    prompt_tokens = _positive_int_or_default(workload.get("prompt_tokens"), 1)
    return " ".join("jw%d" % index for index in range(prompt_tokens))


def _positive_int_or_default(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(1, parsed)


def _append_runtime_event(
    events: List[Dict[str, Any]],
    event_type: str,
    phase: str,
    message: str,
    metadata: Dict[str, Any],
    *,
    timestamp_s: Optional[float] = None,
) -> None:
    events.append(
        {
            "timestamp_s": time.time() if timestamp_s is None else timestamp_s,
            "event_type": event_type,
            "phase": phase,
            "message": message,
            "metadata": metadata,
        }
    )


def _write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _text_has_vllm_oom(text: str) -> bool:
    normalized = text.lower().replace("_", "")
    return any(pattern.replace("_", "") in normalized for pattern in VLLM_OOM_PATTERNS)


def _text_has_import_unavailable(text: str) -> bool:
    lowered = text.lower()
    return "modulenotfounderror" in lowered or "importerror" in lowered


def _copy_vllm_pidfile_artifact(pid_path: str, artifacts_dir: str) -> Dict[str, str]:
    try:
        shutil.copy2(pid_path, os.path.join(artifacts_dir, VLLM_PIDFILE))
    except OSError:
        return {}
    return {"vllm_pidfile": VLLM_PIDFILE}


def _existing_runtime_artifacts(artifacts_dir: str) -> Dict[str, str]:
    artifacts: Dict[str, str] = {}
    for key, name in (
        ("events_jsonl", VLLM_EVENTS_JSONL),
        ("response_txt", VLLM_RESPONSE_TXT),
        ("tokens_jsonl", VLLM_TOKENS_JSONL),
    ):
        if os.path.exists(os.path.join(artifacts_dir, name)):
            artifacts[key] = name
    return artifacts


def _terminate_process_object_with_timeouts(
    process: subprocess.Popen[Any],
    stop_timeout_s: float,
) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.communicate(timeout=stop_timeout_s)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()


def _terminate_vllm_pid(pid: int, metadata: Dict[str, Any]) -> None:
    cached_process = _DETACHED_VLLM_PROCESSES.pop(pid, None)
    if cached_process is not None:
        _terminate_process_object_with_timeouts(cached_process, VLLM_STOP_TIMEOUT_S)
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

    if _wait_for_pid_exit(pid, VLLM_STOP_TIMEOUT_S):
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
    if not _wait_for_pid_exit(pid, VLLM_KILL_TIMEOUT_S):
        metadata["termination_warning"] = "pid still visible after SIGKILL"


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
            diagnostics = _nvidia_smi_csv_readiness_diagnostics(raw_path)
            message = (
                "nvidia-smi exited before producing a parseable CSV row "
                "(returncode %s)" % process.returncode
            )
            if diagnostics.get("csv_rows_seen") and not diagnostics.get("numeric_power_rows"):
                message = (
                    "nvidia-smi exited after producing CSV rows but no numeric "
                    "power.draw sample (returncode %s)" % process.returncode
                )
            return {
                "ok": False,
                "message": message,
                **diagnostics,
            }
        time.sleep(NVIDIA_SMI_READINESS_POLL_S)
    diagnostics = _nvidia_smi_csv_readiness_diagnostics(raw_path)
    return {
        "ok": False,
        "message": (
            "nvidia-smi did not produce a parseable CSV row within %.1f s"
            % NVIDIA_SMI_READINESS_TIMEOUT_S
        ),
        **diagnostics,
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


def _nvidia_smi_csv_readiness_diagnostics(path: str) -> Dict[str, Any]:
    diagnostics: Dict[str, Any] = {
        "csv_rows_seen": 0,
        "numeric_power_rows": 0,
        "unsupported_power_rows": 0,
    }
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        return diagnostics
    for line in lines:
        parts = [part.strip() for part in line.strip().split(",")]
        if len(parts) != 3:
            continue
        try:
            datetime.datetime.strptime(parts[0], "%Y/%m/%d %H:%M:%S.%f")
        except ValueError:
            continue
        diagnostics["csv_rows_seen"] += 1
        power = parts[1].strip().strip("[]").strip().lower()
        if power in {"n/a", "not supported", "na", ""}:
            diagnostics["unsupported_power_rows"] += 1
            continue
        try:
            float(parts[1])
        except ValueError:
            continue
        diagnostics["numeric_power_rows"] += 1
    return diagnostics


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


def _pidfile_matches_live_process(
    pid_payload: Dict[str, Any],
    metadata: Dict[str, Any],
) -> bool:
    try:
        pid = int(pid_payload["pid"])
    except (KeyError, TypeError, ValueError):
        metadata["pid_verification"] = "invalid_pid"
        return False

    expected_command = pid_payload.get("command")
    if not isinstance(expected_command, list) or not expected_command:
        metadata["pid_verification"] = "missing_expected_command"
        return False

    live_command = _live_process_cmdline(pid)
    if live_command is None:
        metadata["pid_verification"] = "process_not_found"
        return False
    metadata["live_cmdline"] = live_command
    if not _command_matches(expected_command, live_command):
        metadata["pid_verification"] = "cmdline_mismatch"
        return False

    expected_ps_lstart = pid_payload.get("ps_lstart")
    if isinstance(expected_ps_lstart, str) and expected_ps_lstart.strip():
        live_ps_lstart = _process_lstart(pid)
        metadata["live_ps_lstart"] = live_ps_lstart
        metadata["expected_ps_lstart"] = expected_ps_lstart
        if live_ps_lstart != expected_ps_lstart:
            metadata["pid_verification"] = "start_time_mismatch"
            return False

    expected_started_at = _float_or_none(pid_payload.get("node_started_at_s"))
    live_started_at = _linux_process_start_epoch_s(pid)
    if live_started_at is not None:
        metadata["live_started_at_s"] = live_started_at
    if expected_started_at is not None and live_started_at is not None:
        if abs(live_started_at - expected_started_at) > 10.0:
            metadata["pid_verification"] = "start_time_mismatch"
            return False

    metadata["pid_verification"] = "matched"
    return True


def _live_process_cmdline(pid: int) -> Optional[List[str]]:
    proc_path = "/proc/%s/cmdline" % pid
    try:
        with open(proc_path, "rb") as handle:
            payload = handle.read()
    except OSError:
        payload = b""
    if payload:
        parts = [
            item.decode("utf-8", errors="replace")
            for item in payload.split(b"\0")
            if item
        ]
        if parts:
            return parts

    try:
        completed = subprocess.run(
            ["ps", "-p", str(pid), "-o", "args="],
            check=False,
            capture_output=True,
            text=True,
            timeout=2.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    args = completed.stdout.strip()
    return args.split() if args else None


def _command_matches(expected: List[Any], live: List[str]) -> bool:
    expected_strings = [str(item) for item in expected]
    if len(live) < len(expected_strings):
        return False
    for index, expected_value in enumerate(expected_strings):
        live_value = live[index]
        if index == 0:
            if os.path.basename(live_value) != os.path.basename(expected_value):
                return False
        elif live_value != expected_value:
            return False
    return True


def _linux_process_start_epoch_s(pid: int) -> Optional[float]:
    try:
        with open("/proc/%s/stat" % pid, "r", encoding="utf-8") as handle:
            stat_text = handle.read()
        with open("/proc/stat", "r", encoding="utf-8") as handle:
            proc_stat = handle.readlines()
    except OSError:
        return None
    parts = stat_text.split()
    if len(parts) < 22:
        return None
    try:
        start_ticks = float(parts[21])
        ticks_per_second = float(os.sysconf(os.sysconf_names["SC_CLK_TCK"]))
    except (KeyError, OSError, TypeError, ValueError):
        return None
    boot_time = None
    for line in proc_stat:
        if line.startswith("btime "):
            try:
                boot_time = float(line.split()[1])
            except (IndexError, ValueError):
                return None
            break
    if boot_time is None:
        return None
    return boot_time + start_ticks / ticks_per_second


def _process_lstart(pid: int) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["ps", "-p", str(pid), "-o", "lstart="],
            check=False,
            capture_output=True,
            text=True,
            timeout=2.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def _float_or_none(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    ("runtime", "prepare"): handle_vllm_prepare,
    ("runtime", "warmup"): handle_vllm_warmup,
    ("runtime", "run_workload"): handle_vllm_run_workload,
    ("runtime", "cleanup"): handle_vllm_cleanup,
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
    metadata["worker_build"] = "u4-vllm-runtime"


if __name__ == "__main__":
    sys.exit(main())
