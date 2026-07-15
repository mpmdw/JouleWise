"""Literal contract fixtures defending mock/MLX suite-control parity."""

from __future__ import annotations

import json
import unittest
from types import SimpleNamespace
from typing import Any

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
from joulewise.suite import MARKER_REQUIRED_METADATA_KEYS, SuiteManifest


CONFIG = {
    "schema_version": "0.1",
    "model": {
        "name": "literal-parity-model",
        "source": "/tmp/literal-parity-model",
        "weight_format": "mlx",
    },
    "quantization": {"name": "none"},
    "hardware_target": {
        "id": "literal-target",
        "transport": "local",
        "runtime_backend": "mock",
        "telemetry_backend": "mock",
    },
    "workload_profile": {
        "name": "literal-parity",
        "prompt_tokens": 2,
        "output_tokens": 2,
    },
    "sampling": {"power_hz": 2.0, "idle_seconds": 1.0},
}

SUITE = {
    "schema_version": "suite_manifest.v1",
    "suite_id": "literal_parity_suite",
    "suite_profile": "literal_parity_v1",
    "suite_revision": "fixture-1",
    "suite_seed": "literal-seed",
    "generator": {
        "name": "literal_fixture",
        "version": "1",
        "parameters_hash": "literal-parameters",
    },
    "analysis_contract": {
        "independent_unit": "bundle",
        "primary_window_class": "suite",
        "allowed_aggregation_levels": ["suite", "block", "level"],
    },
    "execution_policy": {
        "order_policy": "manifest_order",
        "within_bundle_repeats": 1,
        "cooldown_policy": "bundle_only",
        "cache_policy": "warm_cache",
        "warmup_policy": "adapter_default",
        "default_output_policy": "fixed_budget_exact",
    },
    "source_manifest": {
        "source_id": "literal-source",
        "source_kind": "synthetic",
        "revision": "fixture-1",
        "subset_id": "literal-subset",
        "subset_sha256": "literal-subset-sha",
        "license": "internal-test",
        "contamination_note": "literal contract fixture",
    },
    "items": [
        {
            "item_id": "success",
            "item_type": "unit",
            "category": "literal",
            "difficulty": {
                "axis": "literal",
                "value": 1.0,
                "scale": "ordinal",
                "label": "one",
                "source": "fixture",
                "quarantine_note": "not for claims",
            },
            "shape": {
                "planned_prompt_tokens": 2,
                "planned_output_tokens": 2,
                "prompt_level": "short",
                "decode_level": "short",
            },
            "source": {
                "source_item_id": "success",
                "source_sha256": "success-sha",
                "prompt_token_ids": [7, 8],
                "prompt_template_id": "literal",
                "license": "internal-test",
                "contamination_note": "literal",
            },
            "grouping": {
                "condition_id": "success",
                "block_id": "block-a",
                "level_id": "level-1",
                "prefix_group_id": None,
            },
            "output_policy": "fixed_budget_exact",
            "status_policy": "none",
            "tags": [],
        },
        {
            "item_id": "capped",
            "item_type": "unit",
            "category": "literal",
            "difficulty": {
                "axis": "literal",
                "value": 2.0,
                "scale": "ordinal",
                "label": "two",
                "source": "fixture",
                "quarantine_note": "not for claims",
            },
            "shape": {
                "planned_prompt_tokens": 3,
                "planned_output_tokens": 2,
                "prompt_level": "short",
                "decode_level": "short",
            },
            "source": {
                "source_item_id": "capped",
                "source_sha256": "capped-sha",
                "prompt_token_ids": [9, 10, 11],
                "prompt_template_id": "literal",
                "license": "internal-test",
                "contamination_note": "literal",
            },
            "grouping": {
                "condition_id": "capped",
                "block_id": "block-a",
                "level_id": "level-1",
                "prefix_group_id": None,
            },
            "output_policy": "natural_eos",
            "status_policy": "none",
            "tags": [],
        },
        {
            "item_id": "malformed",
            "item_type": "unit",
            "category": "literal",
            "difficulty": {
                "axis": "literal",
                "value": 3.0,
                "scale": "ordinal",
                "label": "three",
                "source": "fixture",
                "quarantine_note": "not for claims",
            },
            "shape": {
                "planned_prompt_tokens": 3,
                "planned_output_tokens": 1,
                "prompt_level": "short",
                "decode_level": "short",
            },
            "source": {
                "source_item_id": "malformed",
                "source_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                "prompt_text": "bad hash",
                "prompt_template_id": "literal",
                "license": "internal-test",
                "contamination_note": "literal",
            },
            "grouping": {
                "condition_id": "malformed",
                "block_id": "block-a",
                "level_id": "level-2",
                "prefix_group_id": "prefix-a",
            },
            "output_policy": "fixed_budget_exact",
            "status_policy": "none",
            "tags": [],
        },
        {
            "item_id": "runtime-failed",
            "item_type": "unit",
            "category": "literal",
            "difficulty": {
                "axis": "literal",
                "value": 4.0,
                "scale": "ordinal",
                "label": "four",
                "source": "fixture",
                "quarantine_note": "not for claims",
            },
            "shape": {
                "planned_prompt_tokens": 1,
                "planned_output_tokens": 1,
                "prompt_level": "short",
                "decode_level": "short",
            },
            "source": {
                "source_item_id": "runtime-failed",
                "source_sha256": "runtime-failed-sha",
                "prompt_token_ids": [12],
                "prompt_template_id": "literal",
                "license": "internal-test",
                "contamination_note": "literal",
            },
            "grouping": {
                "condition_id": "runtime-failed",
                "block_id": "block-b",
                "level_id": "level-3",
                "prefix_group_id": None,
            },
            "output_policy": "fixed_budget_exact",
            "status_policy": "none",
            "tags": ["mock-runtime-failed"],
        },
    ],
}

EXPECTED_MARKER_TYPES = [
    "suite_start",
    "block_start",
    "level_start",
    "item_start",
    "item_end",
    "item_start",
    "item_end",
    "level_end",
    "level_start",
    "item_start",
    "item_end",
    "level_end",
    "block_end",
    "block_start",
    "level_start",
    "item_start",
    "item_end",
    "level_end",
    "block_end",
    "suite_end",
]
EXPECTED_ITEM_STARTS = [
    (
        "success", 0, 0, None, "block-a", "level-1", "success", None,
        "literal", "unit", "fixed_budget_exact", 2, 2,
    ),
    (
        "capped", 1, 1, "success", "block-a", "level-1", "capped", None,
        "literal", "unit", "natural_eos", 3, 2,
    ),
    (
        "malformed", 2, 2, "capped", "block-a", "level-2", "malformed",
        "prefix-a", "literal", "unit", "fixed_budget_exact", 3, 1,
    ),
    (
        "runtime-failed", 3, 3, "malformed", "block-b", "level-3",
        "runtime-failed", None, "literal", "unit", "fixed_budget_exact", 1, 1,
    ),
]
EXPECTED_ITEM_END_CORE = [
    ("success", 0, 0, "succeeded", 2, "requested_tokens_emitted"),
    ("capped", 1, 1, "capped", 2, "length"),
    ("malformed", 2, 2, "malformed", 0, "malformed"),
    ("runtime-failed", 3, 3, "runtime_failed", 0, "runtime_failed"),
]
EXPECTED_OUTPUT_POLICY = {
    "name": "fixed_budget_exact",
    "requested_tokens": 6,
    "emitted_tokens": 4,
    "stop_condition": "suite_completed",
}
EXPECTED_SUITE_PROVENANCE = {
    "suite_id": "literal_parity_suite",
    "manifest_sha256": "96dc4280db328c5baee0772af14ecaf5a16a58bd24a357c0b5dbc1b820d9a76a",
    "item_count": 4,
    "order_policy": "manifest_order",
    "order_seed": "literal-controller-seed",
    "order_row": None,
}
EXPECTED_SUITE_START = {
    "suite_id": "literal_parity_suite",
    "suite_profile": "literal_parity_v1",
    "suite_revision": "fixture-1",
    "suite_manifest_sha256": "96dc4280db328c5baee0772af14ecaf5a16a58bd24a357c0b5dbc1b820d9a76a",
    "item_count": 4,
    "order_policy": "manifest_order",
    "order_seed": "literal-controller-seed",
}
EXPECTED_GROUP_MARKERS = [
    ("block_start", "block-a", 0),
    ("level_start", "level-1", 0),
    ("level_end", "level-1", 0),
    ("level_start", "level-2", 1),
    ("level_end", "level-2", 1),
    ("block_end", "block-a", 0),
    ("block_start", "block-b", 1),
    ("level_start", "level-3", 2),
    ("level_end", "level-3", 2),
    ("block_end", "block-b", 1),
]
EXPECTED_MOCK_PROMPT_PROVENANCE = {
    "realized_token_count": 8,
    "token_hash_domain": "joulewise.suite_prompt_token_ids.v1",
    "token_ids_sha256": "9671acaa71b2d415c1cdcb0d2da657adb6205969e870abe0dddf46dabceef0ea",
    "text_sha256": None,
}
EXPECTED_MLX_PROMPT_PROVENANCE = {
    "realized_token_count": 9,
    "token_hash_domain": "joulewise.suite_prompt_token_ids.v1",
    "token_ids_sha256": "32d4c855f12ac899eebe502ab3e1626d8c8719c8082e69f18108940006ed1b28",
    "text_sha256": None,
}


class LiteralTokenizer:
    def __init__(self) -> None:
        self.eos_token_ids = {99}
        self.bos_token_id = 1
        self.name_or_path = "literal-tokenizer"
        self.vocab_size = 100

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        ids = [index + 10 for index, _ in enumerate(text.split())]
        return [1, *ids] if add_special_tokens else ids


class LiteralMlxLm:
    __version__ = "literal-mlx-1"

    def __init__(self) -> None:
        self.calls = 0

    def make_sampler(self, **kwargs: Any) -> dict[str, Any]:
        return {"sampler": kwargs}

    def stream_generate(
        self,
        model: object,
        tokenizer: LiteralTokenizer,
        prompt: list[int],
        max_tokens: int = 256,
        sampler: object | None = None,
    ):
        call_index = self.calls
        self.calls += 1
        if call_index == 2:
            raise RuntimeError("literal runtime failure")
        pieces = (["A", "B"], ["C", "D"])[call_index]
        for index, piece in enumerate(pieces[:max_tokens]):
            yield SimpleNamespace(
                text=piece,
                token=index + 1,
                finish_reason=None,
            )


def _records(result: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in result.output_artifacts["suite_items.jsonl"].splitlines()
    ]


def _marker_events(result: Any) -> list[Any]:
    return [
        event
        for event in result.events
        if event.event_type in MARKER_REQUIRED_METADATA_KEYS
    ]


def _item_start_projection(result: Any) -> list[tuple[Any, ...]]:
    return [
        (
            event.metadata["item_id"],
            event.metadata["item_index"],
            event.metadata["position"],
            event.metadata["prev_item"],
            event.metadata["block_id"],
            event.metadata["level_id"],
            event.metadata["condition_id"],
            event.metadata["prefix_group_id"],
            event.metadata["category"],
            event.metadata["item_type"],
            event.metadata["output_policy"],
            event.metadata["planned_prompt_tokens"],
            event.metadata["planned_output_tokens"],
        )
        for event in result.events
        if event.event_type == "item_start"
    ]


def _group_marker_projection(result: Any) -> list[tuple[Any, ...]]:
    projection = []
    for event in result.events:
        if event.event_type.startswith("block_"):
            projection.append(
                (
                    event.event_type,
                    event.metadata["block_id"],
                    event.metadata["block_index"],
                )
            )
        elif event.event_type.startswith("level_"):
            projection.append(
                (
                    event.event_type,
                    event.metadata["level_id"],
                    event.metadata["level_index"],
                )
            )
    return projection


def _item_end_projection(result: Any) -> list[tuple[Any, ...]]:
    return [
        (
            event.metadata["item_id"],
            event.metadata["item_index"],
            event.metadata["position"],
            event.metadata["status"],
            event.metadata["emitted_tokens"],
            event.metadata["stop_reason"],
        )
        for event in result.events
        if event.event_type == "item_end"
    ]


class SuiteControlParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig.from_mapping(CONFIG)
        self.manifest = SuiteManifest.from_mapping(SUITE)
        self.mock = MockRuntimeAdapter(FakeClock(start=1000.0))
        self.mlx = MlxRuntimeAdapter(FakeClock(start=1000.0))
        self.mlx._mlx_lm = LiteralMlxLm()
        self.mlx._model = object()
        self.mlx._tokenizer = LiteralTokenizer()

    def run_backends(self) -> tuple[Any, Any]:
        mock_result = self.mock.run_suite(
            self.config,
            self.manifest,
            order_seed="literal-controller-seed",
        )
        mlx_result = self.mlx.run_suite(
            self.config,
            self.manifest,
            order_seed="literal-controller-seed",
        )
        return mock_result, mlx_result

    def test_literal_marker_status_and_policy_contract(self) -> None:
        mock_result, mlx_result = self.run_backends()

        for result in (mock_result, mlx_result):
            self.assertEqual(
                [event.event_type for event in _marker_events(result)],
                EXPECTED_MARKER_TYPES,
            )
            self.assertEqual(result.events[0].metadata, EXPECTED_SUITE_START)
            self.assertEqual(_group_marker_projection(result), EXPECTED_GROUP_MARKERS)
            self.assertEqual(_item_start_projection(result), EXPECTED_ITEM_STARTS)
            self.assertEqual(_item_end_projection(result), EXPECTED_ITEM_END_CORE)
            self.assertEqual(
                result.events[-1].metadata,
                {
                    "suite_id": "literal_parity_suite",
                    "items_executed": 4,
                    "status_counts": {
                        "succeeded": 1,
                        "capped": 1,
                        "malformed": 1,
                        "runtime_failed": 1,
                    },
                },
            )
            self.assertEqual(
                result.workload_provenance["output_policy"],
                EXPECTED_OUTPUT_POLICY,
            )
            self.assertEqual(
                result.workload_provenance["suite"],
                EXPECTED_SUITE_PROVENANCE,
            )

        self.assertEqual(_item_start_projection(mock_result), _item_start_projection(mlx_result))
        self.assertEqual(_item_end_projection(mock_result), _item_end_projection(mlx_result))

    def test_backend_outcomes_are_independently_pinned(self) -> None:
        mock_result, mlx_result = self.run_backends()
        mock_records = _records(mock_result)
        mlx_records = _records(mlx_result)

        expected_statuses = ["succeeded", "capped", "malformed", "runtime_failed"]
        expected_stops = [
            "requested_tokens_emitted",
            "length",
            "malformed",
            "runtime_failed",
        ]
        for records in (mock_records, mlx_records):
            self.assertEqual([record["status"] for record in records], expected_statuses)
            self.assertEqual([record["stop_reason"] for record in records], expected_stops)
            self.assertEqual(
                [record["prompt_source"] for record in records],
                ["token_ids", "token_ids", "prompt_text", "token_ids"],
            )
            self.assertEqual([record["position"] for record in records], [0, 1, 2, 3])

        self.assertEqual(mock_records[2]["status_reason"], "prompt_ids_mismatch")
        self.assertEqual(mlx_records[2]["status_reason"], "prompt_ids_mismatch")
        self.assertEqual(mock_records[3]["status_reason"], "mock-runtime-failed")
        self.assertEqual(
            mlx_records[3]["status_reason"],
            "RuntimeError: literal runtime failure",
        )
        self.assertEqual(
            mock_result.workload_provenance["generator"],
            {"name": "mock_runtime", "version": "0.1.0"},
        )
        self.assertEqual(
            mlx_result.workload_provenance["generator"],
            {"name": "mlx_lm.stream_generate", "version": "literal-mlx-1"},
        )
        self.assertEqual(
            mock_result.workload_provenance["tokenizer"],
            {
                "backend": "mock",
                "identifier": "joulewise.mock_tokenizer.v1",
                "revision": "0.1.0",
                "class": "MockRuntimeAdapter",
                "vocab_size": None,
            },
        )
        self.assertEqual(
            mlx_result.workload_provenance["tokenizer"],
            {
                "backend": "mlx",
                "identifier": "literal-tokenizer",
                "revision": None,
                "class": "LiteralTokenizer",
                "vocab_size": 100,
            },
        )
        self.assertEqual(
            mock_result.workload_provenance["prompt"],
            EXPECTED_MOCK_PROMPT_PROVENANCE,
        )
        self.assertEqual(
            mlx_result.workload_provenance["prompt"],
            EXPECTED_MLX_PROMPT_PROVENANCE,
        )


if __name__ == "__main__":
    unittest.main()
