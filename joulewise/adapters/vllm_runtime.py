"""vLLM runtime adapter backed by the Slice 2K node worker.

The controller never imports vLLM. It asks the shipped node worker to manage a
``vllm serve`` child process and then parses collected worker artifacts into
JouleWise runtime objects. Worker artifact timestamps are node epoch seconds;
derived RuntimeEvent/token output timestamps are converted to the controller
clock domain with the B-5 clock offset while verbatim worker artifacts are
preserved under ``raw/`` when a RunContext is available.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import (
    NodeTaskResult,
    NodeWorkerClient,
    convert_node_timestamp,
)
from joulewise.bundle import write_raw_artifact
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    RunContext,
    RuntimeEvent,
    RuntimeResult,
)
from joulewise.schemas import BenchmarkConfig, FailureReason

RAW_EVENTS_NAME = "vllm_events.jsonl"
RAW_RESPONSE_NAME = "vllm_response.txt"
RAW_TOKENS_NAME = "vllm_tokens.jsonl"
WORKER_EVENTS_NAME = "events.jsonl"
WORKER_LOG_NAME = "worker.log"
WORKER_RESPONSE_NAME = "response.txt"
WORKER_TOKENS_NAME = "tokens.jsonl"
DEFAULT_TENSOR_PARALLEL_SIZE = 1
DEFAULT_GPU_MEMORY_UTILIZATION = 0.82
DEFAULT_OUTPUT_TOKENS = 8
DEFAULT_SAMPLING_PARAMS = {
    "temperature": 0.0,
    "top_p": 1.0,
    "seed": 0,
}


class VllmRuntimeAdapter:
    """RuntimeAdapter implementation for remote node-worker managed vLLM."""

    name = "vllm"

    def __init__(self, clock: Clock, client: NodeWorkerClient) -> None:
        self._clock = clock
        self._client = client
        self._task_counter = 0
        self._clock_alignments: list[dict[str, Any]] = []

    def clock_alignments(self) -> list[dict[str, Any]]:
        return [dict(alignment) for alignment in self._clock_alignments]

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        result = self._run_task(
            "prepare",
            config,
            context,
            timeout_s=900.0,
            block=self._runtime_block(config),
        )
        self._preserve_worker_log(result, context, "prepare")
        return self._adapter_result(result)

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        result = self._run_task(
            "warmup",
            config,
            context,
            timeout_s=120.0,
            block=self._runtime_block(config),
        )
        self._preserve_worker_log(result, context, "warmup")
        return self._adapter_result(result)

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        result = self._run_task(
            "run_workload",
            config,
            context,
            timeout_s=900.0,
            block=self._workload_block(config),
        )
        self._preserve_worker_log(result, context, "run_workload")
        if not result.ok:
            self._raise_task_failure(result, "vLLM workload failed")

        events_text = self._artifact_text(result, "events_jsonl", WORKER_EVENTS_NAME)
        response_text = self._artifact_text(result, "response_txt", WORKER_RESPONSE_NAME)
        tokens_text = self._artifact_text(result, "tokens_jsonl", WORKER_TOKENS_NAME)
        if context is not None:
            write_raw_artifact(context, RAW_EVENTS_NAME, events_text)
            write_raw_artifact(context, RAW_RESPONSE_NAME, response_text)
            write_raw_artifact(context, RAW_TOKENS_NAME, tokens_text)

        offset = self._offset(result)
        events = parse_vllm_events_jsonl(events_text, offset)
        converted_tokens_text, output_tokens = convert_vllm_tokens_jsonl(tokens_text, offset)
        prompt_tokens = self._prompt_token_target(config)
        return RuntimeResult(
            events=events,
            output_artifacts={
                WORKER_RESPONSE_NAME: response_text,
                WORKER_TOKENS_NAME: converted_tokens_text,
            },
            token_count=(prompt_tokens + output_tokens if prompt_tokens is not None else output_tokens),
            output_token_count=output_tokens,
            metadata=self._result_metadata(result),
        )

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        result = self._run_task(
            "cleanup",
            config,
            context,
            timeout_s=120.0,
            block=self._runtime_block(config),
        )
        self._preserve_worker_log(result, context, "cleanup")
        return self._adapter_result(result)

    def _run_task(
        self,
        operation: str,
        config: BenchmarkConfig,
        context: RunContext | None,
        *,
        timeout_s: float,
        block: dict[str, Any],
    ) -> NodeTaskResult:
        self._task_counter += 1
        run_id = self._task_run_id(config, context)
        task: dict[str, Any] = {
            "task_id": "task-runtime-%s-%03d" % (operation, self._task_counter),
            "run_id": run_id,
            "task_type": "runtime",
            "operation": operation,
            "node_role": context.node_role if context is not None else None,
        }
        if operation == "run_workload":
            task["workload"] = block
        else:
            task["runtime"] = block
        result = self._client.run_task(task, timeout_s=timeout_s)
        self._record_clock_alignment(result)
        return result

    def _runtime_block(self, config: BenchmarkConfig) -> dict[str, Any]:
        served_model_name = _served_model_name(config)
        return {
            "backend": self.name,
            "model": {
                "name": config.model.name,
                "source": config.model.source,
                "revision": config.model.revision,
                "weight_format": config.model.weight_format,
            },
            "quantization": {
                "name": config.quantization.name,
                "bits": config.quantization.bits,
                "group_size": config.quantization.group_size,
            },
            "options": {
                "tensor_parallel_size": DEFAULT_TENSOR_PARALLEL_SIZE,
                "gpu_memory_utilization": DEFAULT_GPU_MEMORY_UTILIZATION,
                "served_model_name": served_model_name,
            },
        }

    def _workload_block(self, config: BenchmarkConfig) -> dict[str, Any]:
        profile = config.workload_profile
        output_tokens = profile.output_tokens or DEFAULT_OUTPUT_TOKENS
        sampling_params = dict(DEFAULT_SAMPLING_PARAMS)
        sampling_params["max_tokens"] = output_tokens
        return {
            "prompt_text": profile.prompt_text,
            "prompt_tokens": profile.prompt_tokens,
            "dataset_ref": profile.dataset_ref,
            "output_tokens": output_tokens,
            "sampling_params": sampling_params,
        }

    def _adapter_result(self, result: NodeTaskResult) -> AdapterResult:
        return AdapterResult(
            ok=result.ok,
            failure_reason=result.failure_reason if not result.ok else None,
            message=result.message,
            metadata=self._result_metadata(result),
        )

    def _artifact_text(
        self,
        result: NodeTaskResult,
        artifact_key: str,
        fallback_name: str,
    ) -> str:
        if result.artifacts_path is None:
            raise AdapterFailure(
                result.failure_reason or FailureReason.UNKNOWN_ERROR,
                "node task did not return an artifacts path",
                self._result_metadata(result),
            )
        artifacts = result.raw_status.get("artifacts", {}) if result.raw_status else {}
        relative = artifacts.get(artifact_key, fallback_name)
        path = Path(result.artifacts_path) / str(relative)
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AdapterFailure(
                FailureReason.UNKNOWN_ERROR,
                "could not read collected vLLM artifact %s: %s" % (path.name, exc),
                self._result_metadata(result),
            ) from exc

    def _preserve_worker_log(
        self,
        result: NodeTaskResult,
        context: RunContext | None,
        operation: str,
    ) -> None:
        if context is None or result.artifacts_path is None:
            return
        artifacts = result.raw_status.get("artifacts", {}) if result.raw_status else {}
        relative = artifacts.get("worker_log", WORKER_LOG_NAME)
        source = Path(result.artifacts_path) / str(relative)
        task_id = (
            str(result.raw_status.get("task_id"))
            if result.raw_status and result.raw_status.get("task_id")
            else "vllm-%s" % operation
        )
        safe_task_id = task_id.replace("/", "-")
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            return
        (context.logs_dir / ("%s_worker.log" % safe_task_id)).write_text(
            text,
            encoding="utf-8",
        )

    def _raise_task_failure(self, result: NodeTaskResult, fallback: str) -> None:
        raise AdapterFailure(
            result.failure_reason or FailureReason.UNKNOWN_ERROR,
            result.message or fallback,
            self._result_metadata(result),
        )

    def _result_metadata(self, result: NodeTaskResult) -> dict[str, Any]:
        metadata = dict(result.metadata)
        if result.raw_status and isinstance(result.raw_status.get("metadata"), dict):
            metadata["worker_metadata"] = result.raw_status["metadata"]
        metadata["worker_status"] = result.status
        if result.offset_estimate_s is not None:
            metadata["offset_estimate_s"] = result.offset_estimate_s
        if result.offset_bound_s is not None:
            metadata["offset_bound_s"] = result.offset_bound_s
        return metadata

    def _record_clock_alignment(self, result: NodeTaskResult) -> None:
        alignment = result.metadata.get("clock_alignment")
        if isinstance(alignment, dict):
            self._clock_alignments.append(dict(alignment))

    def _task_run_id(self, config: BenchmarkConfig, context: RunContext | None) -> str:
        if context is not None and context.run_id:
            return context.run_id
        if config.run_id:
            return config.run_id
        raise AdapterFailure(
            FailureReason.UNKNOWN_ERROR,
            "vLLM node task requires a run_id from RunContext or config",
        )

    def _prompt_token_target(self, config: BenchmarkConfig) -> int | None:
        profile = config.workload_profile
        if profile.prompt_tokens is not None:
            return profile.prompt_tokens
        if profile.prompt_text is not None:
            return len(profile.prompt_text.split())
        return None

    @staticmethod
    def _offset(result: NodeTaskResult) -> float:
        return float(result.offset_estimate_s) if result.offset_estimate_s is not None else 0.0


def parse_vllm_events_jsonl(text: str, offset_estimate_s: float) -> list[RuntimeEvent]:
    events: list[RuntimeEvent] = []
    for index, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError("vLLM event row %d must be an object" % index)
        events.append(
            RuntimeEvent(
                timestamp_s=convert_node_timestamp(
                    float(payload["timestamp_s"]),
                    offset_estimate_s,
                ),
                event_type=str(payload.get("event_type", "")),
                phase=str(payload.get("phase", "")),
                message=str(payload.get("message", "")),
                metadata=dict(payload.get("metadata") or {}),
            )
        )
    return events


def convert_vllm_tokens_jsonl(text: str, offset_estimate_s: float) -> tuple[str, int]:
    converted: list[dict[str, Any]] = []
    for index, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError("vLLM token row %d must be an object" % index)
        if "timestamp_s" in payload:
            payload["timestamp_s"] = convert_node_timestamp(
                float(payload["timestamp_s"]),
                offset_estimate_s,
            )
        converted.append(payload)
    return ("".join(json.dumps(record, sort_keys=True) + "\n" for record in converted), len(converted))


def _served_model_name(config: BenchmarkConfig) -> str:
    return "%s-joulewise" % _slug(config.model.name)


def _slug(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "-":
            chars.append("-")
    slug = "".join(chars).strip("-")
    return slug or "vllm-model"
