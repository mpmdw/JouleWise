import json
from unittest.mock import patch
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from typing import Any

from joulewise import __version__
from joulewise.adapters import (
    LocalTransport,
    MockRuntimeAdapter,
    MockTelemetryAdapter,
    resolve_runtime,
    resolve_telemetry,
    resolve_transport,
)
from joulewise.adapters.mock_telemetry import (
    IDLE_POWER_W,
    MEASURED_POWER_W,
    WARMUP_POWER_W,
)
from joulewise.clock import FakeClock, SystemClock
from joulewise.interfaces import (
    PowerSample,
    RuntimeAdapter,
    RuntimeEvent,
    TelemetryAdapter,
    TransportAdapter,
)
from joulewise.provenance import (
    prompt_token_ids_sha256,
    sha256_hex,
    suite_prompt_rollup,
)
from joulewise.schemas import BenchmarkConfig, FailureReason, TelemetryBackend
from joulewise.suite import (
    BLOCK_END,
    BLOCK_START,
    ITEM_END,
    ITEM_START,
    LEVEL_END,
    LEVEL_START,
    MARKER_REQUIRED_METADATA_KEYS,
    SUITE_PHASE,
    SUITE_END,
    SUITE_START,
    SuiteManifest,
    load_suite_manifest,
)

EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}
ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"


def make_config(**overrides: Any) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "model": {"name": "mock-model"},
        "quantization": {"name": "none"},
        "hardware_target": {
            "id": "mock_target",
            "transport": "local",
            "runtime_backend": "mock",
            "telemetry_backend": "mock",
        },
        "workload_profile": {
            "name": "mock_smoke",
            "prompt_tokens": 32,
            "output_tokens": 8,
        },
        "sampling": {"power_hz": 2.0, "idle_seconds": 1.0},
    }
    for key, value in overrides.items():
        if isinstance(value, dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return BenchmarkConfig.from_mapping(data)


def make_suite_manifest() -> SuiteManifest:
    return SuiteManifest.from_mapping(
        {
            "schema_version": "suite_manifest.v1",
            "suite_id": "mock_suite",
            "suite_profile": "mock_suite_v1",
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
                "order_policy": "manifest_order",
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
            "items": [
                _suite_item("item_a", "block_a", "level_1", 3, 2, []),
                _suite_item("item_b", "block_a", "level_1", 2, 1, ["mock-malformed"]),
                _suite_item("item_c", "block_b", "level_2", 4, 2, ["mock-runtime-failed"]),
            ],
        }
    )


def _suite_item(
    item_id: str,
    block_id: str,
    level_id: str,
    prompt_tokens: int,
    output_tokens: int,
    tags: list[str],
) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "item_type": "synthetic_prompt",
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
        "source": {
            "source_item_id": item_id,
            "source_sha256": f"{item_id}-sha",
            "prompt_template_id": "synthetic",
            "license": "internal-test",
            "contamination_note": "synthetic",
        },
        "grouping": {
            "condition_id": item_id,
            "block_id": block_id,
            "level_id": level_id,
            "prefix_group_id": None,
        },
        "output_policy": "fixed_budget_exact",
        "status_policy": "none",
        "tags": tags,
    }


def serialize_events(events: list[RuntimeEvent]) -> str:
    return json.dumps([asdict(event) for event in events], sort_keys=True)


def serialize_samples(samples: list[PowerSample]) -> str:
    return json.dumps([asdict(sample) for sample in samples], sort_keys=True)


class ProtocolConformanceTests(unittest.TestCase):
    def test_mock_runtime_satisfies_protocol(self) -> None:
        self.assertIsInstance(MockRuntimeAdapter(FakeClock()), RuntimeAdapter)

    def test_mock_telemetry_satisfies_protocol(self) -> None:
        self.assertIsInstance(MockTelemetryAdapter(FakeClock()), TelemetryAdapter)

    def test_local_transport_satisfies_protocol(self) -> None:
        self.assertIsInstance(LocalTransport(), TransportAdapter)


class MockRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)
        self.runtime = MockRuntimeAdapter(self.clock)
        self.config = make_config()

    def test_prepare_reports_adapter_metadata(self) -> None:
        result = self.runtime.prepare(self.config)
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata["adapter"], "mock_runtime")
        self.assertEqual(result.metadata["version"], __version__)
        marker = {
            "adapter": "mock_runtime",
            "model_name": self.config.model.name,
            "model_source": self.config.model.source,
            "model_revision": self.config.model.revision,
        }
        expected_sha = sha256_hex(
            json.dumps(marker, separators=(",", ":"), sort_keys=True)
        )
        self.assertEqual(
            result.metadata["model_artifact_identity"],
            {
                "status": "ok",
                "kind": "mock_marker",
                "algorithm": "sha256",
                "sha256": expected_sha,
                "marker": marker,
            },
        )

    def test_prepare_mock_unsupported_returns_did_not_fit(self) -> None:
        config = make_config(model={"name": "mock-unsupported"})
        result = self.runtime.prepare(config)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.DID_NOT_FIT)
        self.assertIn("mock-unsupported", result.message)

    def test_warmup_advances_clock(self) -> None:
        result = self.runtime.warmup(self.config)
        self.assertTrue(result.ok)
        self.assertAlmostEqual(self.clock.now(), 1000.05, places=9)

    def test_run_workload_timeline_and_counts(self) -> None:
        result = self.runtime.run_workload(self.config)
        self.assertEqual(result.token_count, 40)
        self.assertEqual(result.output_token_count, 8)

        events = result.events
        self.assertEqual(len(events), 12)  # 4 phase events + 8 token events
        self.assertEqual(
            [(event.event_type, event.phase) for event in events],
            [("phase_start", "prefill"), ("phase_end", "prefill"), ("phase_start", "decode")]
            + [("token", "decode")] * 8
            + [("phase_end", "decode")],
        )

        self.assertEqual(events[0].timestamp_s, 1000.0)
        self.assertAlmostEqual(events[1].timestamp_s, 1000.032, places=9)  # 32 x 1 ms
        self.assertEqual(events[2].timestamp_s, events[1].timestamp_s)
        token_events = [event for event in events if event.event_type == "token"]
        for index, event in enumerate(token_events):
            self.assertEqual(event.metadata, {"index": index})
            self.assertAlmostEqual(
                event.timestamp_s, 1000.032 + (index + 1) * 0.010, places=9
            )
        self.assertEqual(events[-1].timestamp_s, token_events[-1].timestamp_s)
        # run end: 1000 + 32 ms prefill + 8 x 10 ms decode
        self.assertAlmostEqual(self.clock.now(), 1000.112, places=9)

    def test_event_records_have_exactly_the_contract_keys(self) -> None:
        result = self.runtime.run_workload(self.config)
        for event in result.events:
            self.assertEqual(set(asdict(event)), EVENT_KEYS)

    def test_run_workload_output_artifacts(self) -> None:
        result = self.runtime.run_workload(self.config)
        self.assertEqual(
            set(result.output_artifacts), {"response.txt", "tokens.jsonl"}
        )
        response = result.output_artifacts["response.txt"]
        self.assertIn("mock-model", response)
        self.assertIn("prompt_tokens=32", response)
        self.assertIn("output_tokens=8", response)

        lines = result.output_artifacts["tokens.jsonl"].splitlines()
        self.assertEqual(len(lines), 8)
        token_events = [e for e in result.events if e.event_type == "token"]
        for index, line in enumerate(lines):
            record = json.loads(line)
            self.assertEqual(set(record), {"index", "timestamp_s", "token_id"})
            self.assertEqual(record["index"], index)
            self.assertEqual(record["token_id"], index + 1)
            self.assertEqual(record["timestamp_s"], token_events[index].timestamp_s)
        self.assertEqual(
            result.workload_provenance["response"]["emitted_token_ids"],
            list(range(1, 9)),
        )

    def test_prompt_tokens_fall_back_to_prompt_text_word_count(self) -> None:
        config = make_config(
            workload_profile={
                "name": "text_only",
                "prompt_tokens": None,
                "output_tokens": None,
                "prompt_text": "five words in this prompt",
            }
        )
        result = self.runtime.run_workload(config)
        self.assertEqual(result.output_token_count, 8)  # default output tokens
        self.assertEqual(result.token_count, 5 + 8)

    def test_prompt_tokens_default_when_no_text_or_count(self) -> None:
        config = make_config(
            workload_profile={
                "name": "dataset_only",
                "prompt_tokens": None,
                "output_tokens": None,
                "dataset_ref": "mock-dataset",
            }
        )
        result = self.runtime.run_workload(config)
        self.assertEqual(result.token_count, 32 + 8)

    def test_cleanup_ok(self) -> None:
        self.assertTrue(self.runtime.cleanup(self.config).ok)

    def test_run_suite_timeline_markers_statuses_and_outputs(self) -> None:
        result = self.runtime.run_suite(
            self.config, make_suite_manifest(), order_seed="controller-seed"
        )
        self.assertEqual(result.token_count, 3 + 2 + 4 + 2)
        self.assertEqual(result.output_token_count, 2)
        self.assertEqual(set(result.output_artifacts), {"suite_items.jsonl"})

        event_types = [event.event_type for event in result.events]
        self.assertEqual(event_types[0], SUITE_START)
        self.assertEqual(event_types[-1], SUITE_END)
        self.assertEqual(event_types.count(BLOCK_START), 2)
        self.assertEqual(event_types.count(BLOCK_END), 2)
        self.assertEqual(event_types.count(LEVEL_START), 2)
        self.assertEqual(event_types.count(LEVEL_END), 2)
        self.assertEqual(event_types.count(ITEM_START), 3)
        self.assertEqual(event_types.count(ITEM_END), 3)
        self.assertEqual(event_types.count("token"), 2)

        self.assertEqual(result.events[0].metadata["item_count"], 3)
        self.assertEqual(
            result.events[-1].metadata["status_counts"],
            {"succeeded": 1, "malformed": 1, "runtime_failed": 1},
        )
        self.assertAlmostEqual(self.clock.now(), 1000.023, places=9)

        lines = result.output_artifacts["suite_items.jsonl"].splitlines()
        self.assertEqual(len(lines), 3)
        records = [json.loads(line) for line in lines]
        self.assertEqual([record["item_id"] for record in records], ["item_a", "item_b", "item_c"])
        self.assertEqual(
            [record["status"] for record in records],
            ["succeeded", "malformed", "runtime_failed"],
        )
        self.assertEqual(records[0]["prompt_tokens"], 3)
        self.assertEqual(records[0]["emitted_tokens"], 2)
        self.assertEqual(records[0]["emitted_token_ids"], [1, 2])
        self.assertEqual(len(records[0]["tokens"]), 2)
        self.assertEqual([token["token_id"] for token in records[0]["tokens"]], [1, 2])
        self.assertIn("token_ids_sha256", records[0]["prompt"])
        self.assertEqual(records[1]["status_reason"], "mock-malformed")
        self.assertEqual(records[2]["status_reason"], "mock-runtime-failed")
        self.assertEqual(result.workload_provenance["suite"]["item_count"], 3)
        self.assertEqual(
            result.workload_provenance["prompt"],
            suite_prompt_rollup(
                [record["prompt"]["token_ids_sha256"] for record in records],
                9,
            ),
        )
        self.assertEqual(
            result.workload_provenance["output_policy"],
            {
                "name": "fixed_budget_exact",
                "requested_tokens": 5,
                "emitted_tokens": 2,
                "stop_condition": "suite_completed",
            },
        )

    def test_run_suite_marker_sequence_and_metadata_contract(self) -> None:
        result = self.runtime.run_suite(
            self.config, make_suite_manifest(), order_seed="controller-seed"
        )
        marker_events = [
            event
            for event in result.events
            if event.event_type in MARKER_REQUIRED_METADATA_KEYS
        ]
        self.assertEqual(
            [event.event_type for event in marker_events],
            [
                SUITE_START,
                BLOCK_START,
                LEVEL_START,
                ITEM_START,
                ITEM_END,
                ITEM_START,
                ITEM_END,
                LEVEL_END,
                BLOCK_END,
                BLOCK_START,
                LEVEL_START,
                ITEM_START,
                ITEM_END,
                LEVEL_END,
                BLOCK_END,
                SUITE_END,
            ],
        )
        for event in result.events:
            self.assertEqual(set(asdict(event)), EVENT_KEYS)
        for event in marker_events:
            self.assertEqual(event.phase, SUITE_PHASE)
            self.assertLessEqual(
                MARKER_REQUIRED_METADATA_KEYS[event.event_type],
                set(event.metadata),
            )
        item_phase_events = [
            event
            for event in result.events
            if event.event_type in {"phase_start", "phase_end"}
            and event.phase in {"prefill", "decode"}
        ]
        for event in item_phase_events:
            self.assertLessEqual({"item_id", "item_index"}, set(event.metadata))

    def test_run_suite_prompt_sources_text_ids_and_synthetic(self) -> None:
        manifest = load_suite_manifest(MANIFEST_PATH)
        result = self.runtime.run_suite(
            self.config, manifest, order_seed="controller-seed"
        )
        records = [
            json.loads(line)
            for line in result.output_artifacts["suite_items.jsonl"].splitlines()
        ]
        records_by_id = {record["item_id"]: record for record in records[:3]}
        self.assertEqual(records_by_id["mock_item_001"]["prompt_tokens"], 4)
        self.assertEqual(records_by_id["mock_item_003"]["prompt_tokens"], 5)
        self.assertEqual(records_by_id["mock_item_002"]["prompt_tokens"], 4)
        self.assertEqual(records_by_id["mock_item_001"]["prompt_source"], "synthetic")
        self.assertEqual(records_by_id["mock_item_001"]["bos_present"], False)
        self.assertEqual(records_by_id["mock_item_002"]["prompt_source"], "token_ids")
        self.assertEqual(records_by_id["mock_item_002"]["bos_present"], False)
        self.assertEqual(records_by_id["mock_item_003"]["prompt_source"], "prompt_text")
        self.assertEqual(records_by_id["mock_item_003"]["bos_present"], True)
        self.assertEqual(
            records_by_id["mock_item_002"]["prompt"]["token_ids_sha256"],
            prompt_token_ids_sha256([9, 8, 7, 6]),
        )
        sentinel_records = [
            record for record in records if record["item_id"] == "mock_sentinel_repeat"
        ]
        self.assertEqual([record["item_index"] for record in sentinel_records], [3, 4])

    def test_run_suite_item_jsonl_full_contract(self) -> None:
        result = self.runtime.run_suite(
            self.config, make_suite_manifest(), order_seed="controller-seed"
        )
        records = [
            json.loads(line)
            for line in result.output_artifacts["suite_items.jsonl"].splitlines()
        ]
        base_keys = {
            "item_id",
            "item_index",
            "position",
            "status",
            "prompt_source",
            "bos_present",
            "prompt",
            "response_text",
            "response_sha256",
            "stop_reason",
            "prompt_tokens",
            "emitted_tokens",
            "tokens",
        }
        for record in records:
            expected_keys = (
                base_keys | {"emitted_token_ids"}
                if record["status"] == "succeeded"
                else base_keys | {"emitted_token_ids", "status_reason"}
            )
            self.assertEqual(set(record), expected_keys)
            self.assertEqual(record["response_sha256"], sha256_hex(record["response_text"]))
            if record["status"] == "succeeded":
                self.assertNotIn("status_reason", record)
            else:
                self.assertIn("status_reason", record)

        self.assertEqual(records[0]["status"], "succeeded")
        self.assertEqual(records[1]["status"], "malformed")
        self.assertEqual(records[2]["status"], "runtime_failed")
        self.assertEqual(
            records[0]["tokens"],
            [
                {"index": 0, "timestamp_s": 1000.013, "token_id": 1},
                {"index": 1, "timestamp_s": 1000.023, "token_id": 2},
            ],
        )
        self.assertEqual(records[1]["tokens"], [])
        self.assertEqual(records[2]["tokens"], [])

    def test_text_source_sha_mismatch_is_malformed(self) -> None:
        data = make_suite_manifest().to_dict()
        data["items"] = [
            _suite_item("bad_text_hash", "block_a", "level_1", 2, 1, [])
        ]
        data["items"][0]["source"]["prompt_text"] = "one two"
        data["items"][0]["source"]["source_sha256"] = ("0" * 64).upper()
        manifest = SuiteManifest.from_mapping(data)

        result = self.runtime.run_suite(self.config, manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "malformed")
        self.assertEqual(record["status_reason"], "prompt_ids_mismatch")
        self.assertEqual(record["emitted_tokens"], 0)

    def test_jw_mixed_text_prompt_token_count_mismatch_is_malformed(self) -> None:
        data = make_suite_manifest().to_dict()
        data["suite_id"] = "jw_mixed_v1"
        data["suite_profile"] = "jw_mixed_v1_common_512_256"
        data["source_manifest"]["source_id"] = "jw_mixed_v1:test"
        data["items"] = [
            _suite_item("budgeted_text", "block_a", "level_1", 5, 1, [])
        ]
        data["items"][0]["source"]["prompt_text"] = "one two"
        data["items"][0]["source"]["source_sha256"] = sha256_hex("one two")
        manifest = SuiteManifest.from_mapping(data)

        result = self.runtime.run_suite(self.config, manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "malformed")
        self.assertEqual(record["status_reason"], "planned_prompt_tokens_mismatch")
        self.assertEqual(record["annotations"][0]["severity"], "fatal")

    def test_affine_text_prompt_token_count_mismatch_is_advisory(self) -> None:
        data = make_suite_manifest().to_dict()
        data["suite_id"] = "affine_smoke_v1"
        data["suite_profile"] = "affine_mod_ladder_v1_smoke"
        data["source_manifest"]["source_id"] = "affine_mod_ladder_v1"
        data["items"] = [
            _suite_item("affine_text", "block_a", "level_1", 5, 1, [])
        ]
        data["items"][0]["source"]["prompt_text"] = "one two"
        data["items"][0]["source"]["source_sha256"] = sha256_hex("one two")
        manifest = SuiteManifest.from_mapping(data)

        result = self.runtime.run_suite(self.config, manifest, order_seed="controller-seed")
        record = json.loads(result.output_artifacts["suite_items.jsonl"])

        self.assertEqual(record["status"], "succeeded")
        self.assertEqual(record["annotations"][0]["severity"], "advisory")

    def test_run_suite_natural_eos_assigns_capped(self) -> None:
        data = make_suite_manifest().to_dict()
        data["items"] = [data["items"][0]]
        data["items"][0]["output_policy"] = "natural_eos"
        manifest = SuiteManifest.from_mapping(data)
        result = self.runtime.run_suite(
            self.config, manifest, order_seed="controller-seed"
        )
        record = json.loads(result.output_artifacts["suite_items.jsonl"])
        self.assertEqual(record["status"], "capped")
        self.assertEqual(record["stop_reason"], "length")
        self.assertEqual(result.events[-1].metadata["status_counts"], {"capped": 1})


class MockTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)
        self.telemetry = MockTelemetryAdapter(self.clock)
        self.config = make_config()

    def test_power_constants(self) -> None:
        self.assertEqual(IDLE_POWER_W, 5.0)
        self.assertEqual(WARMUP_POWER_W, 6.0)
        self.assertEqual(MEASURED_POWER_W, 7.5)

    def test_device_metadata_declares_rail_manifest(self) -> None:
        self.assertEqual(
            self.telemetry.device_metadata(self.config),
            {"device": "mock_target", "telemetry": "mock", "rail_manifest": ["mock"]},
        )

    def test_measure_idle_exact_constants_and_clock_advance(self) -> None:
        baseline = self.telemetry.measure_idle(self.config)
        self.assertEqual(self.clock.now(), 1001.0)  # advanced by idle_seconds
        self.assertEqual(baseline.power_w_mean, 5.0)
        self.assertEqual(baseline.power_w_stddev, 0.0)
        self.assertEqual(baseline.duration_s, 1.0)
        self.assertEqual(baseline.sample_count, 2)  # max(2, int(1.0 * 2.0))
        self.assertEqual(baseline.telemetry_backend, TelemetryBackend.MOCK)

    def test_measure_idle_sample_count_scales_with_window(self) -> None:
        config = make_config(sampling={"idle_seconds": 30.0, "power_hz": 2.0})
        baseline = self.telemetry.measure_idle(config)
        self.assertEqual(baseline.sample_count, 60)
        self.assertEqual(baseline.duration_s, 30.0)

    def test_measure_idle_sample_count_floor_is_two(self) -> None:
        config = make_config(sampling={"idle_seconds": 0.25, "power_hz": 2.0})
        baseline = self.telemetry.measure_idle(config)
        self.assertEqual(baseline.sample_count, 2)

    def test_stop_sampling_closed_form_short_window(self) -> None:
        # 0.112 s at 2.0 Hz: the nominal centered grid has fewer than two
        # samples, so the mock emits two evenly spaced interior samples.
        self.assertTrue(self.telemetry.start_sampling(self.config).ok)
        self.clock.sleep(0.112)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(len(samples), 2)
        self.assertAlmostEqual(samples[0].timestamp_s, 1000.0 + 0.112 / 3.0)
        self.assertAlmostEqual(samples[1].timestamp_s, 1000.0 + 2.0 * 0.112 / 3.0)
        for sample in samples:
            self.assertEqual(sample.power_w, 7.5)
            self.assertEqual(sample.source, "mock")
            self.assertEqual(sample.rail, "mock")

    def test_stop_sampling_centered_grid_samples(self) -> None:
        # 1.0 s at 2.0 Hz: centered nominal-period samples, no boundaries.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.75]
        )
        self.assertEqual({sample.power_w for sample in samples}, {7.5})

    def test_system_clock_short_window_samples_land_inside_marker_window(self) -> None:
        clock = SystemClock()
        telemetry = MockTelemetryAdapter(clock)
        config = make_config()

        self.assertTrue(telemetry.start_sampling(config).ok)
        marker_start_s = clock.now()
        clock.sleep(0.075)
        marker_stop_s = clock.now()
        samples = telemetry.stop_sampling(config)

        # The reducer's contract (joulewise/reduce.py _in_window_sample_count)
        # is >= 2 samples inclusively inside the marker window. Deliberately do
        # NOT assert that every sample is inside the markers: under sleep
        # overshoot the centered-grid path can legitimately stamp a sample in
        # the microsecond stop-latency gap between the marker read and the
        # adapter's own end read, which the reducer simply ignores.
        in_marker_window = [
            sample
            for sample in samples
            if marker_start_s <= sample.timestamp_s <= marker_stop_s
        ]
        self.assertGreaterEqual(len(in_marker_window), 2)

    def test_stop_sampling_one_grid_candidate_falls_back_to_thirds(self) -> None:
        # 0.5 s at 2.0 Hz: the centered grid has exactly one candidate
        # (1000.25; the next, 1000.75, is not < end), so the two-sample
        # thirds fallback applies. Same float expressions as the adapter.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.5)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples],
            [1000.0 + 0.5 / 3.0, 1000.0 + 2.0 * 0.5 / 3.0],
        )
        self.assertEqual({sample.power_w for sample in samples}, {7.5})

    def test_stop_sampling_grid_end_boundary_excluded(self) -> None:
        # 0.75 s at 2.0 Hz: grid candidates are 1000.25 and 1000.75, but the
        # loop condition is strictly < end, so 1000.75 (== end) is excluded,
        # leaving one candidate and forcing the thirds fallback. 0.75/3 and
        # 2*0.75/3 are exact in binary floats: [1000.25, 1000.5].
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.75)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.5]
        )

    def test_stop_sampling_two_grid_samples_no_fallback(self) -> None:
        # 0.8 s at 2.0 Hz: grid candidates 1000.25 and 1000.75 are both
        # strictly < end, so the grid path (not the fallback) is used. This
        # pins the fallback/grid boundary just above 1.5/power_hz.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.8)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.75]
        )

    def test_stop_sampling_zero_length_span_single_sample_degenerate(self) -> None:
        # start == end (no clock advance): degenerate single sample at end.
        # The reducer's zero-length-window path never reaches the >= 2 guard.
        self.telemetry.start_sampling(self.config)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual([sample.timestamp_s for sample in samples], [1000.0])
        self.assertEqual(samples[0].power_w, 7.5)

    def test_stop_sampling_interior_invariants_across_durations_and_hz(self) -> None:
        # The P2-008 guarantee, pinned as an invariant: for ANY nonzero span,
        # >= 2 samples, all strictly inside (start, end), strictly increasing,
        # constant 7.5 W, and no consecutive gap reaching the reducer's
        # dropped-sample threshold of 2x the nominal period (reduce.py
        # _dropped_samples).
        cases = [
            (0.1, 0.5),  # fallback: window far below one nominal period
            (0.3, 2.0),  # fallback: the original 2G live-smoke shape
            (1.4, 2.0),  # grid: three samples (offsets 0.25, 0.75, 1.25)
            (100.0, 2.0),  # grid: long window, many samples
            (0.5, 1000.0),  # grid: high rate, 500 samples
        ]
        for duration_s, power_hz in cases:
            with self.subTest(duration_s=duration_s, power_hz=power_hz):
                clock = FakeClock(start=1000.0)
                telemetry = MockTelemetryAdapter(clock)
                config = make_config(sampling={"power_hz": power_hz})
                telemetry.start_sampling(config)
                clock.sleep(duration_s)
                end = clock.now()
                samples = telemetry.stop_sampling(config)
                timestamps = [sample.timestamp_s for sample in samples]
                self.assertGreaterEqual(len(timestamps), 2)
                self.assertTrue(all(1000.0 < t < end for t in timestamps))
                self.assertEqual(timestamps, sorted(set(timestamps)))
                self.assertEqual({sample.power_w for sample in samples}, {7.5})
                nominal_period_s = 1.0 / power_hz
                for left, right in zip(timestamps, timestamps[1:]):
                    self.assertLess(right - left, 2.0 * nominal_period_s)

    def test_stop_sampling_without_start_returns_empty(self) -> None:
        self.assertEqual(self.telemetry.stop_sampling(self.config), [])

    def test_stop_sampling_twice_second_call_returns_empty(self) -> None:
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        self.assertEqual(len(self.telemetry.stop_sampling(self.config)), 2)
        self.assertEqual(self.telemetry.stop_sampling(self.config), [])

    def test_restarted_sampling_stamps_from_new_span(self) -> None:
        # A second start/stop cycle stamps relative to its own span, and a
        # preceding measure_idle (which advances the clock) shifts the span.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        self.telemetry.stop_sampling(self.config)

        self.telemetry.measure_idle(self.config)  # advances clock by 1.0 s
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1002.25, 1002.75]
        )

    def test_start_sampling_telemetry_denied(self) -> None:
        config = make_config(hardware_target={"notes": "telemetry-denied"})
        result = self.telemetry.start_sampling(config)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.PERMISSION_DENIED)
        self.assertIn("telemetry-denied", result.message)

    def test_thermal_state(self) -> None:
        self.clock.sleep(5.0)
        state = self.telemetry.thermal_state(self.config)
        self.assertEqual(state.timestamp_s, 1005.0)
        self.assertEqual(state.temperature_c, 42.0)
        self.assertEqual(state.thermal_pressure, "nominal")


class DeterminismTests(unittest.TestCase):
    """Identical config + clock seed => byte-identical artifacts (D-019)."""

    @staticmethod
    def _complete_run(config: BenchmarkConfig) -> tuple[str, str, dict[str, str]]:
        clock = FakeClock(start=1000.0)
        runtime, runtime_failure = resolve_runtime(config, clock)
        telemetry, telemetry_failure = resolve_telemetry(config, clock)
        assert runtime_failure is None and telemetry_failure is None

        assert runtime.prepare(config).ok
        assert runtime.warmup(config).ok
        telemetry.measure_idle(config)
        assert telemetry.start_sampling(config).ok
        result = runtime.run_workload(config)
        samples = telemetry.stop_sampling(config)
        assert runtime.cleanup(config).ok
        return (
            serialize_events(result.events),
            serialize_samples(samples),
            result.output_artifacts,
        )

    def test_two_runs_are_byte_identical(self) -> None:
        first = self._complete_run(make_config())
        second = self._complete_run(make_config())
        self.assertEqual(first[0], second[0])  # events.jsonl content
        self.assertEqual(first[1], second[1])  # power samples
        self.assertEqual(first[2], second[2])  # response.txt + tokens.jsonl


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)

    def assert_exactly_one(self, pair: tuple[object, object]) -> None:
        self.assertEqual(sum(1 for item in pair if item is not None), 1)

    def test_resolves_mock_runtime(self) -> None:
        adapter, failure = resolve_runtime(make_config(), self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, RuntimeAdapter)
        self.assertEqual(adapter.name, "mock")

    def test_resolves_mock_telemetry(self) -> None:
        adapter, failure = resolve_telemetry(make_config(), self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TelemetryAdapter)
        self.assertEqual(adapter.name, "mock")

    def test_resolves_powermetrics_telemetry_adapter(self) -> None:
        config = make_config(hardware_target={"telemetry_backend": "powermetrics"})
        adapter, failure = resolve_telemetry(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TelemetryAdapter)
        self.assertEqual(adapter.name, "powermetrics")

    def test_powermetrics_import_failure_is_telemetry_unavailable(self) -> None:
        config = make_config(hardware_target={"telemetry_backend": "powermetrics"})
        with patch(
            "joulewise.adapters.importlib.import_module",
            side_effect=ImportError("injected missing adapter"),
        ):
            adapter, failure = resolve_telemetry(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsNone(adapter)
        self.assertFalse(failure.ok)
        self.assertEqual(failure.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)
        self.assertIn("powermetrics", failure.message)

    def test_resolves_local_transport(self) -> None:
        adapter, failure = resolve_transport(make_config())
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TransportAdapter)
        self.assertEqual(adapter.name, "local")

    def test_mlx_runtime_failure_names_backend_and_mac_extra(self) -> None:
        config = make_config(hardware_target={"runtime_backend": "mlx"})
        with patch(
            "joulewise.adapters.importlib.import_module",
            side_effect=ImportError("injected missing adapter"),
        ):
            adapter, failure = resolve_runtime(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsNone(adapter)
        self.assertFalse(failure.ok)
        self.assertEqual(failure.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertIn("mlx", failure.message)
        self.assertIn("[mac]", failure.message)

    def test_resolves_mlx_runtime_adapter_without_importing_mlx_lm(self) -> None:
        config = make_config(hardware_target={"runtime_backend": "mlx"})
        adapter, failure = resolve_runtime(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertEqual(adapter.name, "mlx")

    def test_resolves_vllm_runtime_adapter(self) -> None:
        config = make_config(
            hardware_target={
                "transport": "ssh",
                "host": "node.example",
                "runtime_backend": "vllm",
            }
        )
        adapter, failure = resolve_runtime(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertEqual(adapter.name, "vllm")

    def test_unimplemented_runtimes_fail_structurally(self) -> None:
        for backend in ("llama_cpp", "hailo"):
            with self.subTest(backend=backend):
                config = make_config(hardware_target={"runtime_backend": backend})
                adapter, failure = resolve_runtime(config, self.clock)
                self.assert_exactly_one((adapter, failure))
                self.assertIsNone(adapter)
                self.assertEqual(
                    failure.failure_reason, FailureReason.RUNTIME_UNAVAILABLE
                )
                self.assertIn(backend, failure.message)

    def test_resolves_nvidia_smi_telemetry_adapter(self) -> None:
        config = make_config(
            hardware_target={
                "transport": "ssh",
                "host": "node.example",
                "telemetry_backend": "nvidia_smi",
            }
        )
        adapter, failure = resolve_telemetry(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertEqual(adapter.name, "nvidia_smi")

    def test_unimplemented_telemetry_fails_structurally(self) -> None:
        for backend in ("jetson_rails", "wall_meter"):
            with self.subTest(backend=backend):
                config = make_config(hardware_target={"telemetry_backend": backend})
                adapter, failure = resolve_telemetry(config, self.clock)
                self.assert_exactly_one((adapter, failure))
                self.assertIsNone(adapter)
                self.assertEqual(
                    failure.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE
                )
                self.assertIn(backend, failure.message)

    def test_resolves_ssh_transport(self) -> None:
        config = make_config(
            hardware_target={"transport": "ssh", "host": "node.example"}
        )
        adapter, failure = resolve_transport(config)
        self.assert_exactly_one((adapter, failure))
        self.assertEqual(adapter.name, "ssh")


class LocalTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = LocalTransport()
        self.config = make_config()

    def test_connection_metadata(self) -> None:
        self.assertEqual(
            self.transport.connection_metadata(self.config),
            {"transport": "local", "host": "localhost"},
        )

    def test_run_command_success(self) -> None:
        result = self.transport.run_command(self.config, [sys.executable, "-c", "pass"])
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata, {"returncode": 0})

    def test_run_command_nonzero_exit_reports_stderr_tail(self) -> None:
        result = self.transport.run_command(
            self.config,
            [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"],
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("boom", result.message)

    def test_run_command_missing_binary_is_transport_unavailable(self) -> None:
        result = self.transport.run_command(
            self.config, ["/nonexistent/joulewise-no-such-binary"]
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)

    def test_collect_artifact_copies_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            destination = Path(tmp) / "collected.txt"
            source.write_text("artifact body")
            result = self.transport.collect_artifact(
                self.config, str(source), str(destination)
            )
            self.assertTrue(result.ok)
            self.assertEqual(destination.read_text(), "artifact body")

    def test_collect_artifact_missing_source_is_transport_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.transport.collect_artifact(
                self.config,
                str(Path(tmp) / "missing.txt"),
                str(Path(tmp) / "out.txt"),
            )
            self.assertFalse(result.ok)
            self.assertEqual(
                result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE
            )


if __name__ == "__main__":
    unittest.main()
