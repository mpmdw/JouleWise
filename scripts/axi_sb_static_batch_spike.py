#!/usr/bin/env python3
"""Pinned mlx-lm static-batch feasibility probe.

The controller process uses only the standard library.  It runs the MLX work in
an isolated child, captures every child stream, and emits JSONL only.  This
keeps missing packages, missing Metal, model-load failures, and timeouts as
machine-readable feasibility outcomes rather than tracebacks.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "joulewise.axi_sb_static_batch_spike.v1"
EXPECTED_MLX_LM = "0.31.3"
EXPECTED_MLX = "0.31.2"
DEFAULT_MODEL = "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"
DEFAULT_PROMPTS = (
    "State one reason to measure gross request energy.",
    "State one reason to retain runtime token identifiers.",
    "State one reason to record request-local stop causes.",
    "State one reason to timestamp every generated token.",
)
REQUIRED_HOOKS = {
    "request_submitted",
    "request_admitted",
    "phase_start:prefill",
    "phase_end:prefill",
    "phase_start:decode",
    "phase_end:decode",
    "generation_response",
    "request_terminal",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def json_line(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Emitter:
    def __init__(self, stream: Any = None) -> None:
        self.stream = stream if stream is not None else sys.stdout
        self.sequence = 0

    def emit(self, event: str, **payload: Any) -> dict[str, Any]:
        row = {
            "schema": SCHEMA,
            "sequence": self.sequence,
            "event": event,
            "recorded_at_utc": utc_now(),
            **payload,
        }
        self.sequence += 1
        print(json_line(row), file=self.stream, flush=True)
        return row


def _distribution_record(name: str) -> dict[str, Any]:
    try:
        distribution = importlib.metadata.distribution(name)
        top_level = "mlx_lm" if name == "mlx-lm" else "mlx"
        return {
            "name": name,
            "version": distribution.version,
            "package_root": str(Path(distribution.locate_file(top_level)).resolve()),
        }
    except importlib.metadata.PackageNotFoundError:
        return {"name": name, "version": None, "package_root": None}


def _safe_error(exc: BaseException) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)[:1000]}


def _diagnostic_tail(value: str, limit: int = 2000) -> str | None:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    value = value.strip()
    return value[-limit:] if value else None


def _request_ids(batch_size: int) -> list[str]:
    return [f"axi-sb-{index:03d}" for index in range(batch_size)]


def _prompts(batch_size: int) -> list[str]:
    prompts = []
    for index in range(batch_size):
        seed = DEFAULT_PROMPTS[index % len(DEFAULT_PROMPTS)]
        prompts.append(f"Request {index}: {seed}")
    return prompts


def _encode(tokenizer: Any, prompt: str) -> list[int]:
    try:
        value = tokenizer.encode(prompt, add_special_tokens=True)
    except TypeError:
        value = tokenizer.encode(prompt)
    if hasattr(value, "tolist"):
        value = value.tolist()
    result = [int(token) for token in value]
    if not result:
        raise ValueError("tokenizer returned an empty prompt")
    return result


def _eos_sequences(tokenizer: Any) -> list[list[int]]:
    eos = getattr(tokenizer, "eos_token_ids", None)
    if eos is None:
        token = getattr(tokenizer, "eos_token_id", None)
        eos = [] if token is None else [token]
    return [[int(token)] for token in sorted(set(eos))]


def output_ids_sha256(token_ids: Sequence[int]) -> str:
    preimage = b"joulewise.request_output_token_ids.v1\n" + json.dumps(
        list(token_ids), separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()


@dataclass
class RequestObservation:
    request_id: str
    uid: int
    prompt_tokens: int
    output_token_ids: list[int]
    token_timestamps_s: list[float]
    batch_group_id: str = "axi-sb-static-000"
    stop_reason: str | None = None
    prefill_started: bool = False
    prefill_ended: bool = False
    decode_started: bool = False
    decode_ended: bool = False
    terminal_timestamp_s: float | None = None

    def summary(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "runtime_uid": self.uid,
            "batch_group_id": self.batch_group_id,
            "prompt_token_count": self.prompt_tokens,
            "output_token_count": len(self.output_token_ids),
            "output_token_ids": list(self.output_token_ids),
            "output_token_ids_sha256": output_ids_sha256(self.output_token_ids),
            "stop_reason": self.stop_reason,
            "token_timestamps_s": list(self.token_timestamps_s),
            "terminal_timestamp_s": self.terminal_timestamp_s,
            "phase_hooks": {
                "prefill_started": self.prefill_started,
                "prefill_ended": self.prefill_ended,
                "decode_started": self.decode_started,
                "decode_ended": self.decode_ended,
            },
        }


class ModelCallObserver:
    """Transparent model proxy recording the actual leading dimensions."""

    def __init__(self, model: Any) -> None:
        self.model = model
        self.calls: list[dict[str, Any]] = []

    def __getattr__(self, name: str) -> Any:
        return getattr(self.model, name)

    def __call__(self, inputs: Any, *args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        shape = [int(dimension) for dimension in inputs.shape]
        result = self.model(inputs, *args, **kwargs)
        self.calls.append(
            {
                "call_index": len(self.calls),
                "input_shape": shape,
                "batch_dimension": shape[0] if shape else None,
                "started_at_s": started,
                "returned_at_s": time.perf_counter(),
            }
        )
        return result


class ResponseMappingError(RuntimeError):
    """The runtime response cannot be mapped to a submitted request UID."""


def _response_request(
    observations: Mapping[Any, RequestObservation], response: Any
) -> tuple[Any, RequestObservation]:
    try:
        uid = response.uid
        return uid, observations[uid]
    except (AttributeError, KeyError, TypeError) as exc:
        raise ResponseMappingError("response UID is missing or unknown") from exc


def classify_observation(observation: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the binding AXI-SB classification without importing MLX."""

    if not observation.get("runtime_available", False):
        return {
            "verdict": "runtime_unavailable",
            "reason": observation.get("runtime_unavailable_reason", "runtime_unavailable"),
        }

    requested = observation.get("requested_batch_size")
    calls = observation.get("model_calls", [])
    native_batch = (
        isinstance(requested, int)
        and not isinstance(requested, bool)
        and requested > 1
        and observation.get("insert_call_count") == 1
        and observation.get("realized_batch_size") == requested
        and len(observation.get("runtime_uids", [])) == requested
        and len(set(observation.get("runtime_uids", []))) == requested
        and any(call.get("batch_dimension") == requested for call in calls)
    )
    if not native_batch:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "native_batch_execution",
        }

    hooks = set(observation.get("observed_hooks", []))
    requests = observation.get("requests", [])
    request_ids = [request.get("request_id") for request in requests]
    observable = (
        len(requests) == requested
        and len(set(request_ids)) == requested
        and REQUIRED_HOOKS <= hooks
    )
    for request in requests:
        ids = request.get("output_token_ids")
        timestamps = request.get("token_timestamps_s")
        terminal = request.get("terminal_timestamp_s")
        phase_hooks = request.get("phase_hooks")
        numeric_timestamps = (
            isinstance(timestamps, list)
            and all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in timestamps
            )
        )
        ordered_timestamps = numeric_timestamps and all(
            left <= right for left, right in zip(timestamps, timestamps[1:])
        )
        observable = observable and (
            isinstance(request.get("request_id"), str)
            and bool(request.get("request_id"))
            and isinstance(ids, list)
            and all(isinstance(token, int) and not isinstance(token, bool) for token in ids)
            and request.get("output_token_count") == len(ids)
            and numeric_timestamps
            and ordered_timestamps
            and len(timestamps) == len(ids)
            and isinstance(request.get("stop_reason"), str)
            and bool(request.get("stop_reason"))
            and isinstance(terminal, (int, float))
            and not isinstance(terminal, bool)
            and (not timestamps or terminal >= timestamps[-1])
            and isinstance(phase_hooks, Mapping)
            and set(phase_hooks) == {
                "prefill_started",
                "prefill_ended",
                "decode_started",
                "decode_ended",
            }
            and all(value is True for value in phase_hooks.values())
        )
    if not observable:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "event_observability",
        }

    return {"verdict": "supported", "reason": None}


def _native_batch_was_observed(
    configured_batch_size: Any,
    runtime_uids: Sequence[Any],
    model_calls: Sequence[Mapping[str, Any]],
) -> bool:
    try:
        distinct_uids = len(set(runtime_uids)) == configured_batch_size
    except TypeError:
        distinct_uids = False
    return (
        isinstance(configured_batch_size, int)
        and not isinstance(configured_batch_size, bool)
        and configured_batch_size > 1
        and len(runtime_uids) == configured_batch_size
        and distinct_uids
        and any(call.get("batch_dimension") == configured_batch_size for call in model_calls)
    )


def _request_lifecycle_is_complete(
    batch_size: int,
    runtime_uids: Sequence[Any],
    rows: Sequence[Mapping[str, Any]],
    terminals: Sequence[Mapping[str, Any]],
) -> bool:
    if len(terminals) != batch_size:
        return False

    terminal_request_ids = [row.get("request_id") for row in terminals]
    terminal_runtime_uids = [row.get("runtime_uid") for row in terminals]
    terminal_pairs = list(zip(terminal_request_ids, terminal_runtime_uids))
    try:
        submitted_pairs = {
            (row.get("request_id"), row.get("runtime_uid"))
            for row in rows
            if row.get("event") == "request_submitted"
        }
        admitted_pairs = {
            (row.get("request_id"), row.get("runtime_uid"))
            for row in rows
            if row.get("event") == "request_admitted"
        }
        generation_pairs = {
            (row.get("request_id"), row.get("runtime_uid"))
            for row in rows
            if row.get("event") == "generation_response"
        }
        terminal_pair_set = set(terminal_pairs)
        return (
            all(isinstance(request_id, str) and request_id for request_id in terminal_request_ids)
            and len(set(terminal_request_ids)) == batch_size
            and len(set(terminal_runtime_uids)) == batch_size
            and set(terminal_runtime_uids) == set(runtime_uids)
            and terminal_pair_set <= submitted_pairs
            and terminal_pair_set <= admitted_pairs
            and terminal_pair_set <= generation_pairs
        )
    except TypeError:
        return False


def derive_evidence_verdict(
    rows: Sequence[Mapping[str, Any]], requested_batch_size: int
) -> dict[str, Any]:
    """Reconstruct a semantic verdict from worker evidence events."""

    batch_rows = [row for row in rows if row.get("event") == "batch_observation"]
    if len(batch_rows) != 1:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "native_batch_execution",
        }

    observation = dict(batch_rows[0])
    configured = observation.get("configured_batch_size")
    calls = observation.get("model_calls")
    runtime_uids = observation.get("runtime_uids")
    if (
        observation.get("requested_batch_size") != requested_batch_size
        or configured != requested_batch_size
    ):
        return {
            "verdict": "runtime_unavailable",
            "reason": "evidence_verdict_mismatch",
        }
    native_evidence = (
        isinstance(requested_batch_size, int)
        and not isinstance(requested_batch_size, bool)
        and requested_batch_size > 1
        and observation.get("realized_batch_size") == requested_batch_size
        and observation.get("insert_call_count") == 1
        and isinstance(calls, list)
        and bool(calls)
        and all(
            isinstance(call, Mapping)
            and call.get("batch_dimension") == requested_batch_size
            for call in calls
        )
        and isinstance(runtime_uids, list)
        and _native_batch_was_observed(requested_batch_size, runtime_uids, calls)
    )
    if not native_evidence:
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "native_batch_execution",
        }

    terminals = [dict(row) for row in rows if row.get("event") == "request_terminal"]
    if not _request_lifecycle_is_complete(
        requested_batch_size, runtime_uids, rows, terminals
    ):
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "event_observability",
        }
    observation["requests"] = terminals
    try:
        return classify_observation(observation)
    except (AttributeError, TypeError):
        return {
            "verdict": "unsupported_for_joulewise",
            "reason": "event_observability",
        }


def _worker_emit(stream: Any, event: str, **payload: Any) -> None:
    print(json_line({"event": event, **payload}), file=stream, flush=True)


def _worker_outcome(
    stream: Any,
    verdict: str,
    reason: str | None,
    *,
    stage: str,
    error: BaseException | None = None,
) -> int:
    payload: dict[str, Any] = {"verdict": verdict, "reason": reason, "stage": stage}
    if error is not None:
        payload["error"] = _safe_error(error)
    _worker_emit(stream, "probe_outcome", **payload)
    return 0


def runtime_worker(args: argparse.Namespace) -> int:
    """Run inside the captured child process."""

    evidence_stream = sys.stdout
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            import mlx.core as mx
            import mlx_lm
            from mlx_lm.generate import BatchGenerator
    except BaseException as exc:  # MLX can raise RuntimeError during import.
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "runtime_import_failed",
            stage="runtime_import",
            error=exc,
        )

    try:
        metal_available = bool(mx.metal.is_available())
    except BaseException as exc:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "metal_probe_failed",
            stage="metal_probe",
            error=exc,
        )
    _worker_emit(evidence_stream, "metal_probe", metal_available=metal_available)
    if not metal_available:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "metal_unavailable",
            stage="metal_probe",
        )

    try:
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
            captured_stderr
        ):
            model, tokenizer = mlx_lm.load(args.model)
    except BaseException as exc:
        return _worker_outcome(
            evidence_stream,
            "runtime_unavailable",
            "model_load_failed",
            stage="model_load",
            error=exc,
        )

    observer = ModelCallObserver(model)
    request_ids = _request_ids(args.batch_size)
    prompts = _prompts(args.batch_size)
    uids: Sequence[Any] = []
    observations: dict[Any, RequestObservation] = {}
    observed_hooks: set[str] = set()
    insert_call_count = 0
    try:
        prompt_ids = [_encode(tokenizer, prompt) for prompt in prompts]
        generator = BatchGenerator(
            observer,
            max_tokens=args.max_tokens,
            stop_tokens=_eos_sequences(tokenizer),
            completion_batch_size=args.batch_size,
            prefill_batch_size=args.batch_size,
        )
        submitted_at = time.perf_counter()
        uids = generator.insert(prompt_ids, [args.max_tokens] * args.batch_size)
        insert_call_count = 1
        admitted_at = time.perf_counter()
        observations = {
            uid: RequestObservation(request_ids[index], uid, len(prompt_ids[index]), [], [])
            for index, uid in enumerate(uids)
        }
        observed_hooks = {"request_submitted", "request_admitted"}
        for uid in uids:
            row = observations[uid]
            _worker_emit(
                evidence_stream,
                "request_submitted",
                request_id=row.request_id,
                runtime_uid=uid,
                batch_group_id=row.batch_group_id,
                timestamp_s=submitted_at,
            )
            _worker_emit(
                evidence_stream,
                "request_admitted",
                request_id=row.request_id,
                runtime_uid=uid,
                batch_group_id=row.batch_group_id,
                timestamp_s=admitted_at,
            )
            row.prefill_started = True
            observed_hooks.add("phase_start:prefill")
            _worker_emit(
                evidence_stream,
                "request_phase",
                request_id=row.request_id,
                runtime_uid=uid,
                batch_group_id=row.batch_group_id,
                phase="prefill",
                boundary="start",
                timestamp_s=admitted_at,
            )

        scheduler_step_id = 0
        while True:
            with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(
                captured_stderr
            ):
                prompt_responses, generation_responses = generator.next()
            returned_at = time.perf_counter()
            if not prompt_responses and not generation_responses:
                break

            for response in prompt_responses:
                response_uid, row = _response_request(observations, response)
                observed_hooks.add("prompt_response")
                _worker_emit(
                    evidence_stream,
                    "prompt_response",
                    request_id=row.request_id,
                    runtime_uid=response_uid,
                    batch_group_id=row.batch_group_id,
                    scheduler_step_id=scheduler_step_id,
                    processed_tokens=int(response.progress[0]),
                    total_tokens=int(response.progress[1]),
                    end_of_prompt=bool(response.end_of_prompt),
                    timestamp_s=returned_at,
                )
                if response.end_of_prompt and not row.prefill_ended:
                    row.prefill_ended = True
                    row.decode_started = True
                    observed_hooks.update({"phase_end:prefill", "phase_start:decode"})
                    _worker_emit(
                        evidence_stream,
                        "request_phase",
                        request_id=row.request_id,
                        runtime_uid=response_uid,
                        batch_group_id=row.batch_group_id,
                        scheduler_step_id=scheduler_step_id,
                        phase="prefill",
                        boundary="end",
                        timestamp_s=returned_at,
                    )
                    _worker_emit(
                        evidence_stream,
                        "request_phase",
                        request_id=row.request_id,
                        runtime_uid=response_uid,
                        batch_group_id=row.batch_group_id,
                        scheduler_step_id=scheduler_step_id,
                        phase="decode",
                        boundary="start",
                        timestamp_s=returned_at,
                    )

            for response in generation_responses:
                response_uid, row = _response_request(observations, response)
                committed = response.finish_reason != "stop"
                token_ordinal = len(row.output_token_ids) if committed else None
                if committed:
                    row.output_token_ids.append(int(response.token))
                    row.token_timestamps_s.append(returned_at)
                observed_hooks.add("generation_response")
                _worker_emit(
                    evidence_stream,
                    "generation_response",
                    request_id=row.request_id,
                    runtime_uid=response_uid,
                    batch_group_id=row.batch_group_id,
                    scheduler_step_id=scheduler_step_id,
                    token_id=int(response.token),
                    output_token_ordinal=token_ordinal,
                    committed=committed,
                    finish_reason=response.finish_reason,
                    timestamp_s=returned_at,
                )
                if response.finish_reason is not None:
                    row.stop_reason = str(response.finish_reason)
                    row.terminal_timestamp_s = returned_at
                    row.decode_ended = True
                    observed_hooks.update({"phase_end:decode", "request_terminal"})
                    _worker_emit(
                        evidence_stream,
                        "request_phase",
                        request_id=row.request_id,
                        runtime_uid=response_uid,
                        batch_group_id=row.batch_group_id,
                        scheduler_step_id=scheduler_step_id,
                        phase="decode",
                        boundary="end",
                        timestamp_s=returned_at,
                    )
                    _worker_emit(
                        evidence_stream,
                        "request_terminal",
                        scheduler_step_id=scheduler_step_id,
                        **row.summary(),
                    )
            scheduler_step_id += 1
        generator.close()
    except BaseException as exc:
        native_batch_observed = (
            isinstance(exc, ResponseMappingError)
            and insert_call_count == 1
            and _native_batch_was_observed(args.batch_size, uids, observer.calls)
        )
        if native_batch_observed:
            _worker_emit(
                evidence_stream,
                "batch_observation",
                runtime_available=True,
                requested_batch_size=args.batch_size,
                configured_batch_size=args.batch_size,
                realized_batch_size=len(uids),
                insert_call_count=insert_call_count,
                runtime_uids=list(uids),
                model_calls=observer.calls,
                observed_hooks=sorted(observed_hooks),
                requests=[row.summary() for row in observations.values()],
                incomplete=True,
            )
        return _worker_outcome(
            evidence_stream,
            "unsupported_for_joulewise",
            (
                "event_observability"
                if native_batch_observed
                else "native_batch_execution"
            ),
            stage="batch_generation",
            error=exc,
        )

    request_summaries = [observations[uid].summary() for uid in uids]
    try:
        peak_memory_bytes = int(mx.get_peak_memory())
    except BaseException:
        peak_memory_bytes = None
    _worker_emit(
        evidence_stream,
        "memory_fit_observation",
        tested_batch_size=args.batch_size,
        fit=True,
        peak_memory_bytes=peak_memory_bytes,
        range_established=False,
    )
    observation = {
        "runtime_available": True,
        "requested_batch_size": args.batch_size,
        "configured_batch_size": args.batch_size,
        "realized_batch_size": len(uids),
        "insert_call_count": insert_call_count,
        "runtime_uids": list(uids),
        "model_calls": observer.calls,
        "observed_hooks": sorted(observed_hooks),
        "requests": request_summaries,
    }
    _worker_emit(evidence_stream, "batch_observation", **observation)
    diagnostics = {
        "captured_stdout_tail": _diagnostic_tail(captured_stdout.getvalue()),
        "captured_stderr_tail": _diagnostic_tail(captured_stderr.getvalue()),
    }
    if any(diagnostics.values()):
        _worker_emit(evidence_stream, "runtime_diagnostics", **diagnostics)
    classification = classify_observation(observation)
    return _worker_outcome(
        evidence_stream,
        classification["verdict"],
        classification["reason"],
        stage="complete",
    )


def parse_worker_lines(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    malformed: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            malformed.append(line[-1000:])
            continue
        if not isinstance(row, dict) or not isinstance(row.get("event"), str):
            malformed.append(line[-1000:])
            continue
        rows.append(row)
    return rows, malformed


def controller(args: argparse.Namespace, emitter: Emitter | None = None) -> int:
    emitter = emitter or Emitter()
    emitter.emit(
        "probe_start",
        probe="pinned_mlx_lm_static_batch",
        model=str(Path(args.model).expanduser()),
        requested_batch_size=args.batch_size,
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
        measurement_kind="feasibility_not_energy",
    )
    distributions = [_distribution_record("mlx-lm"), _distribution_record("mlx")]
    emitter.emit(
        "runtime_environment",
        python_executable=sys.executable,
        python_version=sys.version.split()[0],
        distributions=distributions,
        expected_versions={"mlx-lm": EXPECTED_MLX_LM, "mlx": EXPECTED_MLX},
    )

    versions = {row["name"]: row["version"] for row in distributions}
    if versions != {"mlx-lm": EXPECTED_MLX_LM, "mlx": EXPECTED_MLX}:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="pin_mismatch",
            stage="runtime_environment",
        )
        return 0

    model_path = Path(args.model).expanduser()
    artifact = {
        "path": str(model_path),
        "directory_present": model_path.is_dir(),
        "config_present": (model_path / "config.json").is_file(),
    }
    emitter.emit("model_artifact", **artifact)
    if not artifact["directory_present"] or not artifact["config_present"]:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="model_artifact_missing",
            stage="model_artifact",
        )
        return 0

    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_worker",
        "--model",
        str(model_path),
        "--batch-size",
        str(args.batch_size),
        "--max-tokens",
        str(args.max_tokens),
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="probe_timeout",
            stage="worker",
            timeout_seconds=args.timeout_seconds,
            captured_stdout_tail=_diagnostic_tail(exc.stdout or ""),
            captured_stderr_tail=_diagnostic_tail(exc.stderr or ""),
        )
        return 0
    except OSError as exc:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="worker_launch_failed",
            stage="worker",
            error=_safe_error(exc),
        )
        return 0

    rows, malformed = parse_worker_lines(completed.stdout)
    last_worker_event = rows[-1]["event"] if rows else None
    if malformed or completed.stderr.strip():
        emitter.emit(
            "worker_diagnostics",
            malformed_stdout=malformed,
            captured_stderr_tail=_diagnostic_tail(completed.stderr),
            worker_exit_code=completed.returncode,
        )
    valid_worker_protocol = last_worker_event == "probe_outcome" and completed.returncode == 0
    forwarded_rows = rows[:-1] if last_worker_event == "probe_outcome" else rows
    for row in forwarded_rows:
        emitter.emit(row["event"], **{key: value for key, value in row.items() if key != "event"})
    if not valid_worker_protocol:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason=(
                "worker_protocol_failure"
                if last_worker_event != "probe_outcome"
                else "worker_nonzero_exit"
            ),
            stage="worker",
            worker_exit_code=completed.returncode,
        )
        return 0

    child_outcome = rows[-1]
    child_verdict = child_outcome.get("verdict")
    child_reason = child_outcome.get("reason")
    semantic_verdicts = {"supported", "unsupported_for_joulewise"}
    has_batch_evidence = any(row.get("event") == "batch_observation" for row in rows)
    if child_verdict not in semantic_verdicts and not has_batch_evidence:
        if child_verdict != "runtime_unavailable":
            emitter.emit(
                "probe_outcome",
                verdict="runtime_unavailable",
                reason="evidence_verdict_mismatch",
                stage="controller_evidence_validation",
                child_verdict=child_verdict,
                child_reason=child_reason,
            )
        else:
            emitter.emit(
                "probe_outcome",
                **{
                    key: value
                    for key, value in child_outcome.items()
                    if key != "event"
                },
            )
        return 0

    evidence_outcome = derive_evidence_verdict(rows, args.batch_size)
    verdict_matches = (
        child_verdict == evidence_outcome["verdict"]
        and child_reason == evidence_outcome["reason"]
    )
    if evidence_outcome["verdict"] != "supported":
        emitter.emit(
            "probe_outcome",
            verdict=evidence_outcome["verdict"],
            reason=evidence_outcome["reason"],
            stage="controller_evidence_validation",
            evidence_verdict_mismatch=not verdict_matches,
            child_verdict=child_verdict,
            child_reason=child_reason,
        )
    elif verdict_matches:
        emitter.emit(
            "probe_outcome",
            verdict="supported",
            reason=None,
            stage="controller_evidence_validation",
        )
    else:
        emitter.emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="evidence_verdict_mismatch",
            stage="controller_evidence_validation",
            child_verdict=child_verdict,
            child_reason=child_reason,
            evidence_verdict=evidence_outcome["verdict"],
            evidence_reason=evidence_outcome["reason"],
        )
    return 0


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        Emitter().emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="invalid_probe_configuration",
            stage="argument_parsing",
            error={"type": "ArgumentError", "message": message},
        )
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        description="Emit JSONL evidence for the pinned mlx-lm static-batch spike."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=8)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    return parser


def _validate_args(args: argparse.Namespace) -> str | None:
    if args.batch_size <= 1:
        return "--batch-size must be greater than 1"
    if args.max_tokens <= 0:
        return "--max-tokens must be greater than 0"
    if args.timeout_seconds <= 0:
        return "--timeout-seconds must be greater than 0"
    return None


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    problem = _validate_args(args)
    if problem is not None:
        Emitter().emit(
            "probe_outcome",
            verdict="runtime_unavailable",
            reason="invalid_probe_configuration",
            stage="argument_validation",
            error={"type": "ValueError", "message": problem},
        )
        return 2
    if args._worker:
        return runtime_worker(args)
    return controller(args)


if __name__ == "__main__":
    raise SystemExit(main())
