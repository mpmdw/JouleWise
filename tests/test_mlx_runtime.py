"""CI-safe tests for the MLX runtime adapter (Slice 2G)."""

from __future__ import annotations

import json
import unittest
from types import SimpleNamespace
from typing import Any

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
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
        self.assertEqual(
            result.events[0].metadata["phase_boundary_method"],
            "first_token",
        )
        self.assertEqual(result.events[2].metadata["phase_boundary_method"], "first_token")
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

    def test_text_prompt_provenance_hashes_exact_generation_token_ids(self) -> None:
        adapter, fake_mlx = self.prepared_adapter(["A"])
        result = adapter.run_workload(make_config())

        generated_prompt = fake_mlx.calls[0]["prompt"]
        self.assertEqual(generated_prompt, [1, 10, 11, 12])
        self.assertEqual(
            result.workload_provenance["prompt"]["token_ids_sha256"],
            prompt_token_ids_sha256(generated_prompt),
        )


if __name__ == "__main__":
    unittest.main()
