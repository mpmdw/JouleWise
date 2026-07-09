"""CI-safe tests for the MLX runtime adapter (Slice 2G)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import (
    MlxRuntimeAdapter,
    _mlx_metal_memory,
    _process_rss_bytes,
    model_artifact_identity,
)
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.clock import FakeClock
from joulewise.interfaces import AdapterFailure
from joulewise.provenance import (
    prompt_token_ids_sha256,
    sha256_hex,
    suite_prompt_rollup,
)
from joulewise.schemas import BenchmarkConfig, FailureReason
from joulewise.suite import (
    ITEM_END,
    ITEM_START,
    MARKER_REQUIRED_METADATA_KEYS,
    SUITE_END,
    SUITE_PHASE,
    SUITE_START,
    SuiteManifest,
    suite_manifest_sha256,
)


def make_config(
    *,
    workload_profile: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> BenchmarkConfig:
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
    if run_id is not None:
        data["run_id"] = run_id
    return BenchmarkConfig.from_mapping(data)


class FakeTokenizer:
    def __init__(self) -> None:
        self.eos_token_ids = {99}
        self.bos_token_id = 1
        self.name_or_path = "fake-tokenizer"
        self.vocab_size = 12345

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        tokens = [index + 10 for index, _ in enumerate(text.split())]
        if add_special_tokens:
            return [1, *tokens]
        return tokens


class FakeMlxLm:
    def __init__(
        self,
        pieces: list[str],
        *,
        fail_call_indices: set[int] | None = None,
    ) -> None:
        self.pieces = pieces
        self.calls: list[dict[str, Any]] = []
        self.fail_call_indices = fail_call_indices or set()
        self.samplers_built: list[dict[str, Any]] = []

    def make_sampler(self, **kwargs):
        self.samplers_built.append(kwargs)
        return {"sampler": kwargs}

    def stream_generate(
        self,
        model: object,
        tokenizer: FakeTokenizer,
        prompt: str | list[int],
        max_tokens: int = 256,
        sampler: object | None = None,
    ):
        call_index = len(self.calls)
        self.calls.append(
            {
                "model": model,
                "tokenizer": tokenizer,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "sampler": sampler,
                "eos_token_ids_during_call": set(tokenizer.eos_token_ids),
            }
        )
        if call_index in self.fail_call_indices:
            raise RuntimeError(f"boom on call {call_index}")
        for index, piece in enumerate(self.pieces[:max_tokens]):
            yield SimpleNamespace(text=piece, token=index, finish_reason=None)


class FakeMlxLmWithSampler(FakeMlxLm):
    def __init__(self, pieces: list[str]) -> None:
        super().__init__(pieces)
        self.samplers_built: list[dict[str, Any]] = []

    def stream_generate(
        self,
        model: object,
        tokenizer: FakeTokenizer,
        prompt: str | list[int],
        max_tokens: int = 256,
        sampler: object | None = None,
    ):
        call_index = len(self.calls)
        self.calls.append(
            {
                "model": model,
                "tokenizer": tokenizer,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "sampler": sampler,
                "eos_token_ids_during_call": set(tokenizer.eos_token_ids),
            }
        )
        if call_index in self.fail_call_indices:
            raise RuntimeError(f"boom on call {call_index}")
        for index, piece in enumerate(self.pieces[:max_tokens]):
            yield SimpleNamespace(text=piece, token=index, finish_reason=None)


def suite_item(
    item_id: str,
    *,
    prompt_tokens: int,
    output_tokens: int,
    block_id: str = "block",
    level_id: str = "level",
    prompt_text: str | None = None,
    prompt_token_ids: list[int] | None = None,
    output_policy: str = "fixed_budget_exact",
) -> dict[str, Any]:
    source: dict[str, Any] = {
        "source_item_id": item_id,
        "source_sha256": f"{item_id}-sha",
        "prompt_template_id": "unit",
        "license": "internal-test",
        "contamination_note": "synthetic",
    }
    if prompt_text is not None:
        source["prompt_text"] = prompt_text
    if prompt_token_ids is not None:
        source["prompt_token_ids"] = prompt_token_ids
    return {
        "item_id": item_id,
        "item_type": "unit",
        "category": "unit",
        "difficulty": {
            "axis": "unit",
            "value": 1.0,
            "scale": "ordinal",
            "label": "unit",
            "source": "unit",
            "quarantine_note": "not for claims",
        },
        "shape": {
            "planned_prompt_tokens": prompt_tokens,
            "planned_output_tokens": output_tokens,
            "prompt_level": "short",
            "decode_level": "short",
        },
        "source": source,
        "grouping": {
            "condition_id": item_id,
            "block_id": block_id,
            "level_id": level_id,
            "prefix_group_id": None,
        },
        "output_policy": output_policy,
        "status_policy": "none",
        "tags": [],
    }


def make_suite_manifest(
    items: list[dict[str, Any]] | None = None,
    *,
    order_policy: str = "manifest_order",
) -> SuiteManifest:
    return SuiteManifest.from_mapping(
        {
            "schema_version": "suite_manifest.v1",
            "suite_id": "mlx_suite",
            "suite_profile": "mlx_suite_v1",
            "suite_revision": "test",
            "suite_seed": "seed",
            "generator": {
                "name": "unit_test",
                "version": "1",
                "parameters_hash": "params",
            },
            "analysis_contract": {
                "independent_unit": "bundle",
                "primary_window_class": "suite",
                "allowed_aggregation_levels": ["suite", "block", "level"],
            },
            "execution_policy": {
                "order_policy": order_policy,
                "within_bundle_repeats": 1,
                "cooldown_policy": "bundle_only",
                "cache_policy": "warm_cache",
                "warmup_policy": "adapter_default",
                "default_output_policy": "fixed_budget_exact",
            },
            "source_manifest": {
                "source_id": "unit",
                "source_kind": "synthetic",
                "revision": "test",
                "subset_id": "subset",
                "subset_sha256": "subset-sha",
                "license": "internal-test",
                "contamination_note": "synthetic",
            },
            "items": items
            or [
                suite_item("ids_item", prompt_tokens=3, output_tokens=2, prompt_token_ids=[7, 8, 9]),
                suite_item("text_item", prompt_tokens=3, output_tokens=2, prompt_text="alpha beta", output_policy="natural_eos"),
                suite_item("synthetic_item", prompt_tokens=4, output_tokens=1, block_id="block2", level_id="level2"),
            ],
        }
    )


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
        self.assertEqual([record["token_id"] for record in records], [0, 1, 2])
        self.assertEqual([record["timestamp_s"] for record in records], [1000.0] * 3)
        self.assertEqual(result.output_token_count, 3)
        self.assertEqual(
            result.workload_provenance["response"]["emitted_token_ids"],
            [0, 1, 2],
        )

    def test_run_workload_event_stream_is_byte_identical_after_generate_refactor(self) -> None:
        adapter, _ = self.prepared_adapter(["A", "B", "C"])
        result = adapter.run_workload(make_config())

        self.assertEqual(
            [asdict(event) for event in result.events],
            [
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_start",
                    "phase": "tokenize",
                    "message": "mlx tokenization started",
                    "metadata": {},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_end",
                    "phase": "tokenize",
                    "message": "mlx tokenization completed",
                    "metadata": {"prompt_tokens": 4},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_start",
                    "phase": "generation_setup",
                    "message": "mlx generation setup started",
                    "metadata": {},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_end",
                    "phase": "generation_setup",
                    "message": "mlx generation setup completed",
                    "metadata": {
                        "requested_output_tokens": 3,
                        "eos_suppressed": True,
                    },
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_start",
                    "phase": "prefill",
                    "message": "mlx prefill started",
                    "metadata": {
                        "phase_boundary_method": "first_token",
                        "prompt_tokens": 4,
                        "requested_output_tokens": 3,
                        "eos_suppressed": True,
                    },
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_end",
                    "phase": "prefill",
                    "message": "mlx prefill completed",
                    "metadata": {"phase_boundary_method": "first_token"},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_start",
                    "phase": "decode",
                    "message": "mlx decode started",
                    "metadata": {
                        "phase_boundary_method": "first_token",
                        "max_tokens": 3,
                        "eos_suppressed": True,
                        "original_eos_token_ids": [99],
                    },
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "token",
                    "phase": "decode",
                    "message": "mlx token 0",
                    "metadata": {"index": 0},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "token",
                    "phase": "decode",
                    "message": "mlx token 1",
                    "metadata": {"index": 1},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "token",
                    "phase": "decode",
                    "message": "mlx token 2",
                    "metadata": {"index": 2},
                },
                {
                    "timestamp_s": 1000.0,
                    "event_type": "phase_end",
                    "phase": "decode",
                    "message": "mlx decode completed",
                    "metadata": {
                        "phase_boundary_method": "first_token",
                        "emitted_tokens": 3,
                        "requested_output_tokens": 3,
                    },
                },
            ],
        )

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

    def test_model_artifact_identity_hashes_weight_file_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "model.safetensors").write_bytes(b"abc")
            (root / "ignore.json").write_text("{}", encoding="utf-8")

            identity = model_artifact_identity(str(root))

        self.assertEqual(identity["status"], "ok")
        self.assertEqual(identity["kind"], "file_set")
        self.assertEqual(
            identity["files"],
            {
                "model.safetensors": (
                    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
                )
            },
        )
        self.assertEqual(
            identity["folded_sha256"],
            "9b3acfda60512c060fbf440d17a47bac3ff9cbd1afb8e8ff2c1bcedbf58b4bc7",
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

    def test_suite_run_markers_hashes_statuses_and_prompt_sources(self) -> None:
        adapter, fake_mlx = self.prepared_adapter(["A", "B"])
        config = make_config(run_id="suite-test__r2")
        manifest = make_suite_manifest()

        result = adapter.run_suite(config, manifest, order_seed="controller-seed")

        self.assertEqual(set(result.output_artifacts), {"suite_items.jsonl"})
        self.assertEqual(result.events[0].event_type, SUITE_START)
        self.assertEqual(result.events[0].phase, SUITE_PHASE)
        self.assertEqual(result.events[-1].event_type, SUITE_END)
        self.assertEqual(
            result.events[0].metadata["suite_manifest_sha256"],
            suite_manifest_sha256(manifest.to_dict()),
        )
        self.assertEqual(
            result.events[0].metadata["order_seed"],
            "controller-seed",
        )
        marker_events = [
            event
            for event in result.events
            if event.event_type in MARKER_REQUIRED_METADATA_KEYS
        ]
        for event in marker_events:
            self.assertLessEqual(
                MARKER_REQUIRED_METADATA_KEYS[event.event_type],
                set(event.metadata),
            )
        self.assertEqual(
            result.events[-1].metadata["status_counts"],
            {"succeeded": 2, "capped": 1},
        )

        records = [
            json.loads(line)
            for line in result.output_artifacts["suite_items.jsonl"].splitlines()
        ]
        self.assertEqual([record["item_id"] for record in records], ["ids_item", "text_item", "synthetic_item"])
        self.assertEqual([record["status"] for record in records], ["succeeded", "capped", "succeeded"])
        self.assertEqual([record["prompt_source"] for record in records], ["token_ids", "prompt_text", "synthetic"])
        self.assertEqual([record["bos_present"] for record in records], [False, True, False])
        self.assertEqual(records[0]["prompt"]["token_ids_sha256"], prompt_token_ids_sha256([7, 8, 9]))
        self.assertEqual(records[0]["prompt_tokens"], 3)
        self.assertEqual(records[1]["prompt_tokens"], 3)
        self.assertEqual(records[2]["prompt_tokens"], 4)
        self.assertEqual(records[1]["stop_reason"], "length")
        self.assertEqual(records[1]["response_sha256"], sha256_hex("AB"))
        self.assertEqual(records[0]["emitted_token_ids"], [0, 1])
        self.assertEqual([token["token_id"] for token in records[0]["tokens"]], [0, 1])
        self.assertEqual(fake_mlx.calls[0]["prompt"], [7, 8, 9])
        self.assertEqual(fake_mlx.calls[1]["prompt"], [1, 10, 11])
        self.assertEqual(len(fake_mlx.calls[2]["prompt"]), 4)
        self.assertEqual(fake_mlx.calls[0]["eos_token_ids_during_call"], set())
        self.assertEqual(fake_mlx.calls[1]["eos_token_ids_during_call"], {99})
        self.assertEqual(fake_mlx.calls[2]["eos_token_ids_during_call"], set())
        self.assertEqual(result.workload_provenance["suite"]["order_seed"], "controller-seed")
        self.assertEqual(
            result.workload_provenance["prompt"],
            suite_prompt_rollup(
                [record["prompt"]["token_ids_sha256"] for record in records],
                10,
            ),
        )
        self.assertEqual(
            result.workload_provenance["output_policy"],
            {
                "name": "fixed_budget_exact",
                "requested_tokens": 5,
                "emitted_tokens": 5,
                "stop_condition": "suite_completed",
            },
        )

    def test_mock_and_mlx_suite_realized_plans_match_under_rotation(self) -> None:
        items = [
            suite_item("a", prompt_tokens=3, output_tokens=1, block_id="A", level_id="A"),
            suite_item("b", prompt_tokens=3, output_tokens=1, block_id="B", level_id="B"),
            suite_item("c", prompt_tokens=3, output_tokens=1, block_id="C", level_id="C"),
        ]
        manifest = make_suite_manifest(items, order_policy="block_latin_square_v1")
        config = make_config()
        mlx_adapter, _ = self.prepared_adapter(["A", "B", "C"])
        mock_adapter = MockRuntimeAdapter(FakeClock(start=1000.0))

        mlx_result = mlx_adapter.run_suite(
            config,
            manifest,
            order_seed="seed",
            order_row=2,
        )
        mock_result = mock_adapter.run_suite(
            config,
            manifest,
            order_seed="seed",
            order_row=2,
        )

        def item_start_indices(result) -> list[int]:
            return [
                event.metadata["item_index"]
                for event in result.events
                if event.event_type == ITEM_START
            ]

        mlx_item_indices = item_start_indices(mlx_result)
        self.assertEqual(mlx_item_indices, item_start_indices(mock_result))

        mlx_records = [
            json.loads(line)
            for line in mlx_result.output_artifacts["suite_items.jsonl"].splitlines()
        ]
        self.assertTrue(all("position" in record for record in mlx_records))
        self.assertEqual([record["item_index"] for record in mlx_records], mlx_item_indices)
        self.assertEqual([record["position"] for record in mlx_records], [0, 1, 2])

    def test_suite_per_item_generation_exception_runtime_failed_and_continues(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLm(["A"], fail_call_indices={1})
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()
        manifest = make_suite_manifest(
            [
                suite_item("first", prompt_tokens=2, output_tokens=1),
                suite_item("fails", prompt_tokens=2, output_tokens=1),
                suite_item("third", prompt_tokens=2, output_tokens=1),
            ]
        )

        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        records = [
            json.loads(line)
            for line in result.output_artifacts["suite_items.jsonl"].splitlines()
        ]

        self.assertEqual([record["status"] for record in records], ["succeeded", "runtime_failed", "succeeded"])
        self.assertIn("RuntimeError: boom on call 1", records[1]["status_reason"])
        self.assertEqual(records[2]["item_id"], "third")
        self.assertEqual(result.events[-1].metadata["status_counts"], {"succeeded": 2, "runtime_failed": 1})
        self.assertEqual([event.metadata["item_id"] for event in result.events if event.event_type == ITEM_END], ["first", "fails", "third"])

    def test_suite_fixed_budget_underrun_is_malformed(self) -> None:
        adapter, _ = self.prepared_adapter(["A"])
        manifest = make_suite_manifest(
            [suite_item("underrun", prompt_tokens=2, output_tokens=2)]
        )

        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "malformed")
        self.assertEqual(record["status_reason"], "fixed_budget_underrun")
        self.assertEqual(record["stop_reason"], "stream_exhausted")
        self.assertEqual(result.events[-1].metadata["status_counts"], {"malformed": 1})

    def test_suite_natural_eos_budget_exhaustion_is_capped(self) -> None:
        adapter, _ = self.prepared_adapter(["A", "B"])
        manifest = make_suite_manifest(
            [
                suite_item(
                    "natural",
                    prompt_tokens=2,
                    output_tokens=2,
                    output_policy="natural_eos",
                )
            ]
        )

        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "capped")
        self.assertEqual(record["stop_reason"], "length")
        self.assertEqual(result.events[-1].metadata["status_counts"], {"capped": 1})

    def test_jw_mixed_text_prompt_token_count_mismatch_is_malformed(self) -> None:
        adapter, _ = self.prepared_adapter(["A"])
        manifest = make_suite_manifest(
            [
                suite_item(
                    "budgeted_text",
                    prompt_tokens=5,
                    output_tokens=1,
                    prompt_text="one two",
                )
            ]
        )
        data = manifest.to_dict()
        data["suite_id"] = "jw_mixed_v1"
        data["suite_profile"] = "jw_mixed_v1_common_512_256"
        data["source_manifest"]["source_id"] = "jw_mixed_v1:test"
        data["items"][0]["source"]["source_sha256"] = sha256_hex("one two")
        manifest = SuiteManifest.from_mapping(data)

        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "malformed")
        self.assertEqual(record["status_reason"], "planned_prompt_tokens_mismatch")
        self.assertEqual(record["annotations"][0]["code"], "planned_prompt_tokens_mismatch")
        self.assertEqual(record["annotations"][0]["planned_prompt_tokens"], 5)
        self.assertEqual(record["annotations"][0]["realized_prompt_tokens"], 3)
        self.assertEqual(record["annotations"][0]["severity"], "fatal")

    def test_affine_text_prompt_token_count_mismatch_is_advisory(self) -> None:
        adapter, _ = self.prepared_adapter(["A"])
        manifest = make_suite_manifest(
            [
                suite_item(
                    "affine_text",
                    prompt_tokens=5,
                    output_tokens=1,
                    prompt_text="one two",
                )
            ]
        )
        data = manifest.to_dict()
        data["suite_id"] = "affine_smoke_v1"
        data["suite_profile"] = "affine_mod_ladder_v1_smoke"
        data["source_manifest"]["source_id"] = "affine_mod_ladder_v1"
        data["items"][0]["source"]["source_sha256"] = sha256_hex("one two")
        manifest = SuiteManifest.from_mapping(data)

        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "succeeded")
        self.assertNotIn("status_reason", record)
        self.assertEqual(record["annotations"][0]["code"], "planned_prompt_tokens_mismatch")
        self.assertEqual(record["annotations"][0]["planned_prompt_tokens"], 5)
        self.assertEqual(record["annotations"][0]["realized_prompt_tokens"], 3)
        self.assertEqual(record["annotations"][0]["severity"], "advisory")

    def test_sampler_provenance_api_absent_refuses_workload_and_suite(self) -> None:
        class NoSamplerMlx(FakeMlxLm):
            make_sampler = None  # type: ignore[assignment]

            def stream_generate(
                self,
                model: object,
                tokenizer: FakeTokenizer,
                prompt: str | list[int],
                max_tokens: int = 256,
            ):
                yield from ()

        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        adapter._mlx_lm = NoSamplerMlx(["A"])
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        with self.assertRaisesRegex(Exception, "sampler_pin_unverified"):
            adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))
        with self.assertRaisesRegex(Exception, "sampler_pin_unverified"):
            adapter.run_suite(
                make_config(),
                make_suite_manifest([suite_item("one", prompt_tokens=2, output_tokens=1)]),
                order_seed="controller-seed",
            )

    def test_sampler_pin_refuses_missing_top_level_and_sample_utils_api(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLm(["A"])
        fake_mlx.make_sampler = None  # type: ignore[assignment]
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        with self.assertRaises(AdapterFailure) as ctx:
            adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))

        self.assertEqual(ctx.exception.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertEqual(
            ctx.exception.metadata,
            {
                "error": "sampler_pin_unverified",
                "kind": "greedy",
                "temperature": 0.0,
                "pinned": False,
                "reason": "mlx_lm sampler API unavailable",
            },
        )

    def test_sampler_pin_refuses_missing_sample_utils_make_sampler(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLm(["A"])
        fake_mlx.make_sampler = None  # type: ignore[assignment]
        fake_mlx.sample_utils = SimpleNamespace(make_sampler=None)
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        with self.assertRaises(AdapterFailure) as ctx:
            adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))

        self.assertEqual(ctx.exception.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertEqual(
            ctx.exception.metadata,
            {
                "error": "sampler_pin_unverified",
                "kind": "greedy",
                "temperature": 0.0,
                "pinned": False,
                "reason": "mlx_lm sampler API unavailable",
            },
        )

    def test_sampler_pin_refuses_when_all_constructor_forms_fail(self) -> None:
        class BadSamplerMlx(FakeMlxLm):
            def make_sampler(self, *args, **kwargs):
                raise TypeError("unsupported sampler form")

        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        adapter._mlx_lm = BadSamplerMlx(["A"])
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        with self.assertRaises(AdapterFailure) as ctx:
            adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))

        self.assertEqual(ctx.exception.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertEqual(
            ctx.exception.metadata,
            {
                "error": "sampler_pin_unverified",
                "kind": "greedy",
                "temperature": 0.0,
                "pinned": False,
                "reason": "mlx_lm sampler API unavailable",
                "errors": [
                    "temp: unsupported sampler form",
                    "temperature: unsupported sampler form",
                    "positional_temp: unsupported sampler form",
                ],
            },
        )

    def test_sampler_provenance_api_present_for_workload_and_suite(self) -> None:
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLmWithSampler(["A"])
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        workload = adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))
        suite = adapter.run_suite(
            make_config(),
            make_suite_manifest([suite_item("one", prompt_tokens=2, output_tokens=1)]),
            order_seed="controller-seed",
        )

        self.assertEqual(workload.workload_provenance["sampler"]["pinned"], True)
        self.assertEqual(workload.workload_provenance["sampler"]["kind"], "greedy")
        self.assertEqual(workload.workload_provenance["sampler"]["temperature"], 0.0)
        self.assertEqual(suite.workload_provenance["sampler"]["pinned"], True)
        self.assertEqual(
            fake_mlx.samplers_built,
            [{"temp": 0.0}, {"temp": 0.0}, {"temp": 0.0}],
        )
        self.assertIsNotNone(fake_mlx.calls[0]["sampler"])
        self.assertIsNotNone(fake_mlx.calls[1]["sampler"])

    def test_sampler_api_under_sample_utils_namespace_is_detected(self) -> None:
        # Installed mlx_lm exposes make_sampler under sample_utils, not
        # top-level (verified live 2026-07-08) - detection must find it there.
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLmWithSampler(["A"])
        fake_mlx.sample_utils = SimpleNamespace(make_sampler=fake_mlx.make_sampler)
        fake_mlx.make_sampler = None  # type: ignore[assignment]
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        adapter._tokenizer = FakeTokenizer()

        workload = adapter.run_workload(make_config(workload_profile={"output_tokens": 1}))
        sampler = workload.workload_provenance["sampler"]
        self.assertEqual(sampler["pinned"], True)
        self.assertEqual(sampler["api"], "mlx_lm.sample_utils.make_sampler")

    def test_tokenize_window_brackets_prompt_encode_on_live_clock(self) -> None:
        # Opus review finding 1: the encode must happen INSIDE the tokenize
        # phase window. A FakeClock-advancing tokenizer makes the capture
        # points observable: start < end iff the encode ran between them.
        clock = FakeClock(start=1000.0)
        adapter = MlxRuntimeAdapter(clock)
        fake_mlx = FakeMlxLm(["A"])
        adapter._mlx_lm = fake_mlx
        adapter._model = object()

        class SlowEncodeTokenizer(FakeTokenizer):
            def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
                clock.sleep(0.5)  # simulated tokenization latency
                return super().encode(text, add_special_tokens=add_special_tokens)

        adapter._tokenizer = SlowEncodeTokenizer()
        result = adapter.run_workload(
            make_config(workload_profile={"prompt_text": "alpha beta", "output_tokens": 1})
        )
        tokenize = {
            (event.event_type): event.timestamp_s
            for event in result.events
            if event.phase == "tokenize"
        }
        self.assertEqual(
            tokenize["phase_end"] - tokenize["phase_start"], 0.5,
            "prompt encode latency must land inside the tokenize window",
        )
        prefill_start = next(
            event.timestamp_s
            for event in result.events
            if event.phase == "prefill" and event.event_type == "phase_start"
        )
        self.assertGreaterEqual(prefill_start, tokenize["phase_end"])

    def test_natural_eos_underrun_is_succeeded(self) -> None:
        # D-045: natural_eos with emitted < planned budget is a plain success
        # (the model stopped naturally); only emitted == budget is capped.
        adapter, _ = self.prepared_adapter(["A"])  # 1 emitted token
        manifest = make_suite_manifest(
            [
                suite_item(
                    "eos_item",
                    prompt_tokens=2,
                    output_tokens=3,
                    output_policy="natural_eos",
                )
            ]
        )
        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        line = json.loads(result.output_artifacts["suite_items.jsonl"].strip())
        self.assertEqual(line["status"], "succeeded")
        self.assertNotIn("status_reason", line)
        self.assertEqual(line["emitted_tokens"], 1)

    def test_suite_sampler_provenance_first_real_record_wins(self) -> None:
        # Opus review finding 3: a final item whose generation never starts
        # must not overwrite earlier pinned sampler provenance.
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        fake_mlx = FakeMlxLmWithSampler(["A"])
        adapter._mlx_lm = fake_mlx
        adapter._model = object()
        tokenizer = FakeTokenizer()
        original_encode = tokenizer.encode

        def failing_second_encode(text: str, *, add_special_tokens: bool = True) -> list[int]:
            if text == "boom prompt":
                raise RuntimeError("encode failed")
            return original_encode(text, add_special_tokens=add_special_tokens)

        tokenizer.encode = failing_second_encode  # type: ignore[method-assign]
        adapter._tokenizer = tokenizer
        manifest = make_suite_manifest(
            [
                suite_item("good", prompt_tokens=2, output_tokens=1),
                suite_item(
                    "bad",
                    prompt_tokens=2,
                    output_tokens=1,
                    prompt_text="boom prompt",
                ),
            ]
        )
        result = adapter.run_suite(make_config(), manifest, order_seed="controller-seed")
        statuses = [
            json.loads(line)["status"]
            for line in result.output_artifacts["suite_items.jsonl"].strip().split("\n")
        ]
        self.assertEqual(statuses, ["succeeded", "runtime_failed"])
        self.assertEqual(result.workload_provenance["sampler"]["pinned"], True)


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
