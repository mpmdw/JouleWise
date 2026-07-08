"""CI-safe tests for the MLX runtime adapter (Slice 2G)."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import (
    MlxRuntimeAdapter,
    _mlx_metal_memory,
    _process_rss_bytes,
)
from joulewise.clock import FakeClock
from joulewise.provenance import prompt_token_ids_sha256
from joulewise.schemas import BenchmarkConfig, FailureReason


def make_config(*, workload_profile: dict[str, Any] | None = None) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "model": {
            "name": "fake-mlx-model",
            "family": "fake",
            "source": "/tmp/fake-mlx-model",
            "weight_format": "mlx",
        },
        "quantization": {"name": "int4", "bits": 4},
        "hardware_target": {
            "id": "fake_mac",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "mock",
        },
        "workload_profile": {
            "name": "fake_mlx_smoke",
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


class FakeTokenizer:
    def __init__(self) -> None:
        self.eos_token_ids = {99}
        self.name_or_path = "fake-tokenizer"
        self.vocab_size = 12345

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        tokens = [index + 10 for index, _ in enumerate(text.split())]
        if add_special_tokens:
            return [1, *tokens]
        return tokens


class FakeMlxLm:
    def __init__(self, pieces: list[str]) -> None:
        self.pieces = pieces
        self.calls: list[dict[str, Any]] = []

    def stream_generate(
        self,
        model: object,
        tokenizer: FakeTokenizer,
        prompt: str | list[int],
        max_tokens: int = 256,
    ):
        self.calls.append(
            {
                "model": model,
                "tokenizer": tokenizer,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "eos_token_ids_during_call": set(tokenizer.eos_token_ids),
            }
        )
        for index, piece in enumerate(self.pieces[:max_tokens]):
            yield SimpleNamespace(text=piece, token=index, finish_reason=None)


class MlxRuntimeTests(unittest.TestCase):
    def prepared_adapter(self, pieces: list[str]) -> tuple[MlxRuntimeAdapter, FakeMlxLm]:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLm(pieces)
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()
        return adapter, fake_mlx

    def test_prepare_import_failure_is_structured_runtime_unavailable(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock())

        def raise_import_error() -> object:
            raise ImportError("no module named mlx_lm")

        adapter._import_mlx_lm = raise_import_error  # type: ignore[method-assign]
        result = adapter.prepare(make_config())
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertIn("[mac]", result.message)
        self.assertIn("not installed", result.message)

    def test_prompt_token_workload_synthesizes_deterministic_token_prompt(self) -> None:
        adapter, fake_mlx = self.prepared_adapter(["x", "y"])
        config = make_config(
            workload_profile={
                "prompt_text": None,
                "prompt_tokens": 5,
                "output_tokens": 2,
            }
        )

        result = adapter.run_workload(config)

        prompt = fake_mlx.calls[0]["prompt"]
        self.assertIsInstance(prompt, list)
        self.assertEqual(len(prompt), 5)
        self.assertEqual(fake_mlx.calls[0]["max_tokens"], 2)
        self.assertEqual(fake_mlx.calls[0]["eos_token_ids_during_call"], set())
        self.assertEqual(adapter._tokenizer.eos_token_ids, {99})
        self.assertEqual(result.token_count, 7)
        self.assertEqual(result.output_token_count, 2)
        self.assertEqual(result.output_artifacts["response.txt"], "xy")
        provenance = result.workload_provenance
        self.assertIsNotNone(provenance)
        assert provenance is not None
        self.assertEqual(provenance["prompt"]["realized_token_count"], 5)
        self.assertEqual(provenance["prompt"]["text_sha256"], None)
        self.assertEqual(provenance["tokenizer"]["identifier"], "fake-tokenizer")
        self.assertEqual(provenance["tokenizer"]["vocab_size"], 12345)
        self.assertEqual(provenance["output_policy"]["requested_tokens"], 2)
        self.assertEqual(provenance["output_policy"]["emitted_tokens"], 2)
        self.assertEqual(
            provenance["output_policy"]["stop_condition"],
            "requested_tokens_emitted",
        )

    def test_run_workload_event_shape_and_token_timeline(self) -> None:
        adapter, _ = self.prepared_adapter(["A", "B", "C"])
        result = adapter.run_workload(make_config())

        self.assertEqual(
            [(event.event_type, event.phase) for event in result.events],
            [
                ("phase_start", "tokenize"),
                ("phase_end", "tokenize"),
                ("phase_start", "generation_setup"),
                ("phase_end", "generation_setup"),
                ("phase_start", "prefill"),
                ("phase_end", "prefill"),
                ("phase_start", "decode"),
                ("token", "decode"),
                ("token", "decode"),
                ("token", "decode"),
                ("phase_end", "decode"),
            ],
        )
        timestamps = [event.timestamp_s for event in result.events]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(
            [event.metadata for event in result.events if event.event_type == "token"],
            [{"index": 0}, {"index": 1}, {"index": 2}],
        )
        self.assertEqual(result.events[1].metadata["prompt_tokens"], 4)
        self.assertEqual(
            result.events[4].metadata["phase_boundary_method"],
            "first_token",
        )
        self.assertEqual(result.events[6].metadata["phase_boundary_method"], "first_token")
        self.assertEqual(result.output_artifacts["response.txt"], "ABC")
        self.assertEqual(
            result.workload_provenance["prompt"]["realized_token_count"],
            4,
        )
        self.assertEqual(
            len(result.workload_provenance["prompt"]["token_ids_sha256"]),
            64,
        )
        self.assertEqual(result.workload_provenance["prompt"]["text_sha256"] is not None, True)

        lines = result.output_artifacts["tokens.jsonl"].splitlines()
        self.assertEqual(len(lines), 3)
        records = [json.loads(line) for line in lines]
        self.assertEqual([record["index"] for record in records], [0, 1, 2])
        self.assertEqual([record["timestamp_s"] for record in records], [1000.0] * 3)
        self.assertEqual(result.output_token_count, 3)

    def test_memory_snapshots_are_captured_at_lifecycle_boundaries(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLm(["A"])
        fake_tokenizer = FakeTokenizer()

        def fake_load(source, revision=None, return_config=True):
            return object(), fake_tokenizer, {"model_type": "fake"}

        fake_mlx.load = fake_load  # type: ignore[attr-defined]
        adapter._import_mlx_lm = lambda: fake_mlx  # type: ignore[method-assign]

        def fake_snapshot(label: str) -> dict[str, Any]:
            return {
                "label": label,
                "captured_at_s": 1000.0,
                "process_rss_bytes": 123456,
                "mlx_metal": {
                    "api_available": True,
                    "active_memory_bytes": 1,
                    "cache_memory_bytes": 2,
                    "peak_memory_bytes": 3,
                },
            }

        with patch.object(adapter, "_memory_snapshot", side_effect=fake_snapshot):
            prepare = adapter.prepare(make_config())
            result = adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))
            cleanup = adapter.cleanup(make_config())

        self.assertTrue(prepare.ok)
        self.assertEqual(
            prepare.metadata["memory_snapshots"][0]["label"], "prepare_end"
        )
        self.assertEqual(result.metadata, {})
        self.assertEqual(
            cleanup.metadata["memory_snapshots"][0]["label"], "cleanup_start"
        )

    def test_text_prompt_provenance_hashes_exact_generation_token_ids(self) -> None:
        adapter, fake_mlx = self.prepared_adapter(["A"])
        result = adapter.run_workload(make_config())

        generated_prompt = fake_mlx.calls[0]["prompt"]
        self.assertEqual(generated_prompt, [1, 10, 11, 12])
        self.assertEqual(
            result.workload_provenance["prompt"]["token_ids_sha256"],
            prompt_token_ids_sha256(generated_prompt),
        )


class MemoryProbeHelperTests(unittest.TestCase):
    def test_process_rss_bytes_success(self) -> None:
        errors: dict[str, str] = {}

        def fake_run(command, **kwargs):
            self.assertEqual(command[:3], ["ps", "-o", "rss="])
            return subprocess.CompletedProcess(command, 0, "123\n", "")

        with patch("joulewise.adapters.mlx_runtime.subprocess.run", side_effect=fake_run):
            self.assertEqual(_process_rss_bytes(errors), 123 * 1024)
        self.assertEqual(errors, {})

    def test_process_rss_bytes_timeout(self) -> None:
        errors: dict[str, str] = {}

        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

        with patch("joulewise.adapters.mlx_runtime.subprocess.run", side_effect=fake_run):
            self.assertIsNone(_process_rss_bytes(errors))
        self.assertEqual(errors, {"process_rss": "timeout"})

    def test_mlx_metal_memory_success(self) -> None:
        errors: dict[str, str] = {}
        fake_core = ModuleType("mlx.core")
        fake_core.metal = SimpleNamespace(
            get_active_memory=lambda: 10,
            get_cache_memory=lambda: 20,
            get_peak_memory=lambda: 30,
        )
        previous = sys.modules.get("mlx.core")
        sys.modules["mlx.core"] = fake_core
        try:
            self.assertEqual(
                _mlx_metal_memory(errors),
                {
                    "api_available": True,
                    "active_memory_bytes": 10,
                    "cache_memory_bytes": 20,
                    "peak_memory_bytes": 30,
                },
            )
        finally:
            if previous is None:
                sys.modules.pop("mlx.core", None)
            else:
                sys.modules["mlx.core"] = previous
        self.assertEqual(errors, {})

    def test_mlx_metal_memory_missing_api(self) -> None:
        errors: dict[str, str] = {}
        fake_core = ModuleType("mlx.core")
        previous = sys.modules.get("mlx.core")
        sys.modules["mlx.core"] = fake_core
        try:
            self.assertEqual(
                _mlx_metal_memory(errors),
                {
                    "api_available": False,
                    "active_memory_bytes": None,
                    "cache_memory_bytes": None,
                    "peak_memory_bytes": None,
                },
            )
        finally:
            if previous is None:
                sys.modules.pop("mlx.core", None)
            else:
                sys.modules["mlx.core"] = previous
        self.assertEqual(errors, {})

    def test_mlx_metal_memory_available_api_without_values_records_error(self) -> None:
        errors: dict[str, str] = {}
        fake_core = ModuleType("mlx.core")
        fake_core.metal = SimpleNamespace(
            get_active_memory=lambda: None,
            get_cache_memory=lambda: "unknown",
            get_peak_memory=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        previous = sys.modules.get("mlx.core")
        sys.modules["mlx.core"] = fake_core
        try:
            self.assertEqual(
                _mlx_metal_memory(errors),
                {
                    "api_available": True,
                    "active_memory_bytes": None,
                    "cache_memory_bytes": None,
                    "peak_memory_bytes": None,
                },
            )
        finally:
            if previous is None:
                sys.modules.pop("mlx.core", None)
            else:
                sys.modules["mlx.core"] = previous
        self.assertEqual(errors["mlx_metal"], "getters_unavailable")
        self.assertEqual(errors["mlx_metal.get_active_memory"], "non_numeric")
        self.assertEqual(errors["mlx_metal.get_cache_memory"], "non_numeric")
        self.assertIn("RuntimeError: boom", errors["mlx_metal.get_peak_memory"])


if __name__ == "__main__":
    unittest.main()
