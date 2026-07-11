from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import NodeTaskResult
from joulewise.adapters.vllm_runtime import (
    RAW_EVENTS_NAME,
    RAW_RESPONSE_NAME,
    RAW_TOKENS_NAME,
    VllmRuntimeAdapter,
    convert_vllm_tokens_jsonl,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import AdapterFailure, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason

PROMPT_TOKEN_DOMAIN = "joulewise.prompt_token_ids.v1"


def make_config(*, workload_profile: dict[str, Any] | None = None) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "run_id": "run-vllm-test",
        "model": {
            "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "family": "llama",
            "source": "/models/tinyllama",
            "revision": "main",
            "weight_format": "safetensors",
        },
        "quantization": {"name": "none"},
        "hardware_target": {
            "id": "rtx_3050",
            "transport": "ssh",
            "host": "test-node",
            "runtime_backend": "vllm",
            "telemetry_backend": "nvidia_smi",
        },
        "workload_profile": {
            "name": "vllm_smoke",
            "prompt_text": "alpha beta gamma",
            "output_tokens": 3,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "sampling": {"power_hz": 2.0, "idle_seconds": 1.0},
    }
    if workload_profile is not None:
        data["workload_profile"] = {**data["workload_profile"], **workload_profile}
    return BenchmarkConfig.from_mapping(data)


def make_context(config: BenchmarkConfig, root: Path) -> RunContext:
    raw_dir = root / "raw"
    logs_dir = root / "logs"
    outputs_dir = root / "outputs"
    for path in (raw_dir, logs_dir, outputs_dir):
        path.mkdir(parents=True)
    return RunContext(
        config=config,
        clock=FakeClock(start=1000.0),
        run_id="run-vllm-test",
        bundle_path=root,
        raw_dir=raw_dir,
        logs_dir=logs_dir,
        outputs_dir=outputs_dir,
        node_role=None,
    )


def task_result(
    *,
    ok: bool = True,
    reason: FailureReason | None = None,
    message: str = "ok",
    artifacts_path: Path | None = None,
    raw_status: dict[str, Any] | None = None,
    offset: float = 7.0,
) -> NodeTaskResult:
    status = "succeeded" if ok else ("unsupported" if reason == FailureReason.DID_NOT_FIT else "failed")
    return NodeTaskResult(
        ok=ok,
        status=status,
        failure_reason=reason,
        message=message,
        artifacts_path=artifacts_path,
        raw_status=raw_status,
        offset_estimate_s=offset,
        offset_bound_s=0.25,
        metadata={"clock_alignment": {"offset_estimate_s": offset, "offset_bound_s": 0.25}},
    )


def expected_prompt_token_hash(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256((PROMPT_TOKEN_DOMAIN + "\0" + canonical).encode("utf-8")).hexdigest()


def runtime_artifacts(root: Path) -> NodeTaskResult:
    root.mkdir(parents=True, exist_ok=True)
    events_text = "\n".join(
        [
            json.dumps(
                {
                    "timestamp_s": 100.0,
                    "event_type": "phase_start",
                    "phase": "prefill",
                    "message": "start",
                    "metadata": {"phase_boundary_method": "first_stream_chunk"},
                },
                sort_keys=True,
            ),
            json.dumps(
                {
                    "timestamp_s": 101.0,
                    "event_type": "phase_end",
                    "phase": "decode",
                    "message": "done",
                    "metadata": {"emitted_tokens": 2},
                },
                sort_keys=True,
            ),
        ]
    ) + "\n"
    tokens_text = (
        json.dumps({"index": 0, "text": "A", "timestamp_s": 100.25}, sort_keys=True) + "\n"
        + json.dumps({"index": 1, "text": "B", "timestamp_s": 100.50}, sort_keys=True) + "\n"
    )
    (root / "events.jsonl").write_text(events_text, encoding="utf-8")
    (root / "response.txt").write_text("AB", encoding="utf-8")
    (root / "tokens.jsonl").write_text(tokens_text, encoding="utf-8")
    return task_result(
        artifacts_path=root,
        raw_status={
            "status": "succeeded",
            "message": "ok",
            "artifacts": {
                "events_jsonl": "events.jsonl",
                "response_txt": "response.txt",
                "tokens_jsonl": "tokens.jsonl",
            },
            "metadata": {"prompt_token_ids": [101, 202, 303], "worker": "fake-vllm"},
        },
        offset=7.0,
    )


class FakeClient:
    def __init__(self, results: list[NodeTaskResult]):
        self.results = list(results)
        self.tasks: list[dict[str, Any]] = []

    def run_task(self, task: dict[str, Any], *, timeout_s: float) -> NodeTaskResult:
        self.tasks.append({"task": task, "timeout_s": timeout_s})
        if not self.results:
            raise AssertionError("fake client exhausted")
        return self.results.pop(0)


class VllmRuntimeAdapterTests(unittest.TestCase):
    def test_prepare_builds_runtime_task_and_surfaces_clock_alignment(self) -> None:
        alignment = {"method": "node_worker_clock_echo", "offset_estimate_s": 3.0}
        client = FakeClient(
            [
                task_result(
                    message="started",
                    offset=3.0,
                    raw_status={"metadata": {"pid": 1234}},
                )
            ]
        )
        client.results[0].metadata["clock_alignment"] = alignment
        adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]

        result = adapter.prepare(make_config())

        self.assertTrue(result.ok)
        self.assertEqual(result.message, "started")
        self.assertEqual(result.metadata["clock_alignment"], alignment)
        self.assertEqual(result.metadata["offset_estimate_s"], 3.0)
        task = client.tasks[0]["task"]
        self.assertEqual(task["task_type"], "runtime")
        self.assertEqual(task["operation"], "prepare")
        self.assertEqual(task["runtime"]["backend"], "vllm")
        self.assertEqual(task["runtime"]["model"]["source"], "/models/tinyllama")
        self.assertEqual(task["runtime"]["options"]["tensor_parallel_size"], 1)
        self.assertEqual(task["runtime"]["options"]["gpu_memory_utilization"], 0.82)
        self.assertEqual(
            task["runtime"]["options"]["served_model_name"],
            "tinyllama-tinyllama-1-1b-chat-v1-0-joulewise",
        )

    def test_lifecycle_failure_preserves_worker_failure_reason(self) -> None:
        adapter = VllmRuntimeAdapter(
            FakeClock(),
            FakeClient(
                [
                    task_result(
                        ok=False,
                        reason=FailureReason.RUNTIME_UNAVAILABLE,
                        message="vLLM launcher unavailable",
                    )
                ]
            ),
        )  # type: ignore[arg-type]

        result = adapter.prepare(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertIn("launcher unavailable", result.message)

    def test_transport_failure_is_not_recast(self) -> None:
        adapter = VllmRuntimeAdapter(
            FakeClock(),
            FakeClient(
                [
                    task_result(
                        ok=False,
                        reason=FailureReason.TRANSPORT_UNAVAILABLE,
                        message="ssh failed",
                    )
                ]
            ),
        )  # type: ignore[arg-type]

        result = adapter.warmup(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)

    def test_run_workload_converts_timestamps_and_preserves_raw_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = make_config()
            context = make_context(config, root)
            client = FakeClient([runtime_artifacts(root / "artifacts")])
            adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]

            result = adapter.run_workload(config, context)

            self.assertEqual(result.output_artifacts["response.txt"], "AB")
            self.assertEqual(result.output_token_count, 2)
            self.assertEqual(result.token_count, 5)
            self.assertEqual(result.metadata["token_count_source"], "stream_chunk_fallback")
            prompt = result.workload_provenance["prompt"]
            self.assertEqual(prompt["realized_token_count"], 3)
            self.assertEqual(
                prompt["token_ids_sha256"],
                expected_prompt_token_hash([101, 202, 303]),
            )
            self.assertEqual([event.timestamp_s for event in result.events], [93.0, 94.0])
            self.assertEqual(result.events[0].phase, "prefill")
            token_records = [
                json.loads(line)
                for line in result.output_artifacts["tokens.jsonl"].splitlines()
            ]
            self.assertEqual([record["timestamp_s"] for record in token_records], [93.25, 93.5])
            self.assertEqual((context.raw_dir / RAW_RESPONSE_NAME).read_text(encoding="utf-8"), "AB")
            self.assertIn('"timestamp_s": 100.0', (context.raw_dir / RAW_EVENTS_NAME).read_text(encoding="utf-8"))
            self.assertIn('"timestamp_s": 100.25', (context.raw_dir / RAW_TOKENS_NAME).read_text(encoding="utf-8"))

            task = client.tasks[0]["task"]
            self.assertEqual(task["operation"], "run_workload")
            self.assertNotIn("runtime", task)
            self.assertEqual(task["workload"]["prompt_text"], "alpha beta gamma")
            self.assertNotIn("prompt_tokens", task["workload"])
            self.assertNotIn("dataset_ref", task["workload"])
            self.assertEqual(task["workload"]["sampling_params"]["temperature"], 0.0)
            self.assertEqual(task["workload"]["sampling_params"]["top_p"], 1.0)
            self.assertEqual(task["workload"]["sampling_params"]["seed"], 0)
            self.assertEqual(task["workload"]["sampling_params"]["max_tokens"], 3)

    def test_server_usage_count_wins_over_coalesced_stream_chunk_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = runtime_artifacts(root / "artifacts")
            assert task.raw_status is not None
            task.raw_status["metadata"].update(
                {
                    "emitted_tokens": 3,
                    "stream_chunk_count": 2,
                    "token_count_source": "server_usage",
                }
            )
            adapter = VllmRuntimeAdapter(FakeClock(), FakeClient([task]))  # type: ignore[arg-type]

            result = adapter.run_workload(make_config())

            self.assertEqual(result.output_token_count, 3)
            self.assertEqual(result.token_count, 6)
            self.assertEqual(result.metadata["token_count_source"], "server_usage")
            self.assertEqual(result.metadata["stream_chunk_count"], 2)

    def test_run_workload_failure_raises_adapter_failure(self) -> None:
        adapter = VllmRuntimeAdapter(
            FakeClock(),
            FakeClient(
                [
                    task_result(
                        ok=False,
                        reason=FailureReason.DID_NOT_FIT,
                        message="CUDA out of memory",
                    )
                ]
            ),
        )  # type: ignore[arg-type]

        with self.assertRaises(AdapterFailure) as caught:
            adapter.run_workload(make_config())

        self.assertEqual(caught.exception.failure_reason, FailureReason.DID_NOT_FIT)

    def test_run_workload_records_structured_prompt_token_absence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = runtime_artifacts(root / "artifacts")
            assert result.raw_status is not None
            result.raw_status["metadata"] = {
                "prompt_token_ids_unavailable_reason": {
                    "source": "vllm_tokenize_endpoint",
                    "endpoint": "/tokenize",
                    "error_class": "VllmHttpError",
                    "message": "HTTP 404",
                }
            }
            adapter = VllmRuntimeAdapter(FakeClock(), FakeClient([result]))  # type: ignore[arg-type]

            runtime_result = adapter.run_workload(make_config())

            prompt = runtime_result.workload_provenance["prompt"]
            self.assertIsNone(prompt["realized_token_count"])
            self.assertIsNone(prompt["token_ids_sha256"])
            self.assertEqual(
                prompt["token_ids_unavailable_reason"],
                {
                    "source": "vllm_tokenize_endpoint",
                    "endpoint": "/tokenize",
                    "error_class": "VllmHttpError",
                    "message": "HTTP 404",
                },
            )

    def test_cleanup_uses_runtime_operation(self) -> None:
        client = FakeClient([task_result(message="stopped")])
        adapter = VllmRuntimeAdapter(FakeClock(), client)  # type: ignore[arg-type]

        result = adapter.cleanup(make_config())

        self.assertTrue(result.ok)
        self.assertEqual(result.message, "stopped")
        self.assertEqual(client.tasks[0]["task"]["operation"], "cleanup")
        self.assertIn("runtime", client.tasks[0]["task"])

    def test_token_timestamp_conversion_helper_is_exact(self) -> None:
        converted, count = convert_vllm_tokens_jsonl(
            json.dumps({"index": 0, "timestamp_s": 10.125}, sort_keys=True) + "\n",
            1.25,
        )

        self.assertEqual(count, 1)
        self.assertEqual(json.loads(converted)["timestamp_s"], 8.875)


if __name__ == "__main__":
    unittest.main()
