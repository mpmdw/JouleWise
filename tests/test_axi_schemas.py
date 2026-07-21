from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from joulewise.axi_decode_config import (
    AXI_CONFIG_EXTENSION,
    AxiSchemaError,
    BatchPolicy,
    RequestRoster,
    SpeculationPolicy,
    TargetTokenizerIdentity,
    normalized_json_bytes,
    request_prompt_sha256,
    validate_request_row,
    validate_request_token_row,
    validate_v2_event,
    validate_v2_metadata,
)
from joulewise.schemas import (
    BenchmarkConfig,
    DecodeCounterRollup,
    IdleBaseline,
    MeasurementQuality,
    RequestDecodeMetric,
    RunStatus,
    SchemaError,
    SummaryMetricsV060,
    TelemetryBackend,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "axi_ap_spec"
GOLDEN = ROOT / "tests" / "goldens"
HAS_JSONSCHEMA = importlib.util.find_spec("jsonschema") is not None


def load(path: Path) -> dict:
    return json.loads(path.read_bytes())


def draft_config() -> BenchmarkConfig:
    return BenchmarkConfig.from_mapping(load(FIXTURE / "draft_spec_on.json"))


def v060_summary() -> SummaryMetricsV060:
    rollup = DecodeCounterRollup(
        emitted_count=3,
        tokens_proposed=4,
        tokens_accepted=2,
        target_emitted_count=1,
        acceptance_rate=0.5,
    )
    request = RequestDecodeMetric(
        request_id="request-000",
        request_ordinal=0,
        terminal_status="succeeded",
        output_token_count=3,
        decode_duration_s=2.0,
        ttft_s=0.5,
        decode_phase_output_throughput_tokens_s=1.5,
        decode_emission_event_count=2,
        decode_counter_rollup=rollup,
        burst_size_mean_tokens=1.5,
        burst_size_p50_tokens=1.5,
        burst_size_p95_tokens=1.95,
        burst_size_max_tokens=2,
    )
    return SummaryMetricsV060(
        status=RunStatus.SUCCEEDED,
        energy_request_j=8.0,
        energy_token_j=2.0,
        energy_output_token_j=8.0 / 3.0,
        gross_energy_j=10.0,
        idle_subtracted_energy_j=8.0,
        ttft_s=0.5,
        decode_latency_s=2.0,
        throughput_tokens_s=1.5,
        inter_token_throughput_tokens_s=None,
        idle_baseline=IdleBaseline(
            power_w_mean=2.0,
            power_w_stddev=0.0,
            duration_s=1.0,
            sample_count=2,
            telemetry_backend=TelemetryBackend.MOCK,
        ),
        uncertainty=None,
        measurement_quality=MeasurementQuality(
            requested_sampling_hz=2.0,
            observed_sampling_hz=2.0,
            telemetry_source="mock:target",
            token_counts_source="runtime_observed",
            phase_identifiability={
                "decode": "identifiable",
                "group_phase_windows_overlap": False,
            },
        ),
        phase_energy_j={"decode": 6.0},
        energy_uncertainty_status="not_estimable",
        decode_counter_rollup=rollup,
        batch_group_gross_energy_j=None,
        gross_energy_per_committed_output_token_j=10.0 / 3.0,
        gross_energy_per_accepted_draft_token_j=5.0,
        decode_phase_output_throughput_tokens_s=1.5,
        decode_emission_event_rate_events_s=1.0,
        decode_emission_burst_size_mean_tokens=1.5,
        decode_emission_burst_size_p50_tokens=1.5,
        decode_emission_burst_size_p95_tokens=1.95,
        decode_emission_burst_size_max_tokens=2,
        request_decode_metrics=[request],
    )


class AxiConfigSchemaTests(unittest.TestCase):
    def test_non_axi_normalized_config_bytes_remain_pinned(self) -> None:
        raw = load(ROOT / "configs" / "examples" / "mock_local.json")
        emitted = normalized_json_bytes(BenchmarkConfig.from_mapping(raw).to_dict())
        self.assertEqual(
            hashlib.sha256(emitted).hexdigest(),
            "15a556a8ea5853f6aef1d5d6a814d97264f6bc0b9dd11274755c98a7ec686355",
        )
        self.assertNotIn("schema_extensions", json.loads(emitted))
        self.assertNotIn("batch_policy", json.loads(emitted))
        self.assertNotIn("speculation", json.loads(emitted))

    def test_axi_config_golden_is_normalized_and_extension_is_identity(self) -> None:
        for name in ("draft_spec_off", "draft_spec_on", "native_spec_off", "native_spec_on"):
            with self.subTest(name=name):
                path = FIXTURE / f"{name}.json"
                config = BenchmarkConfig.from_mapping(load(path))
                self.assertEqual(normalized_json_bytes(config.to_dict()), path.read_bytes())
                self.assertEqual(config.schema_extensions, [AXI_CONFIG_EXTENSION])

    def test_every_batch_and_speculation_identity_field_changes_hash_input(self) -> None:
        source = load(FIXTURE / "draft_spec_on.json")
        original = hashlib.sha256(normalized_json_bytes(source)).hexdigest()
        mutations = [
            ("batch.mode", lambda v: v["batch_policy"].__setitem__("mode", "static_batch")),
            ("batch.size", lambda v: v["batch_policy"].__setitem__("requested_batch_size", 2)),
            ("batch.admit", lambda v: v["batch_policy"].__setitem__("admission_policy", "admit_roster_together")),
            ("batch.sync", lambda v: v["batch_policy"].__setitem__("synchronization_policy", "barrier_before_prefill")),
            ("batch.dispatch", lambda v: v["batch_policy"].__setitem__("dispatch_policy", "one_native_batch_call")),
            ("batch.roster_ref", lambda v: v["batch_policy"].__setitem__("request_roster_ref", "other.json")),
            ("batch.roster_hash", lambda v: v["batch_policy"].__setitem__("request_roster_sha256", "d" * 64)),
            ("spec.mode", lambda v: v["speculation"].__setitem__("mode", "native_mtp")),
            ("spec.cap", lambda v: v["speculation"].__setitem__("max_proposed_tokens", 5)),
            ("draft.name", lambda v: v["speculation"]["draft_model_identity"].__setitem__("model_name", "other")),
            ("draft.revision", lambda v: v["speculation"]["draft_model_identity"].__setitem__("model_revision", "other")),
            ("draft.hash", lambda v: v["speculation"]["draft_model_identity"].__setitem__("model_artifact_sha256", "d" * 64)),
            ("draft.format", lambda v: v["speculation"]["draft_model_identity"].__setitem__("weight_format", "other")),
            ("draft.quant", lambda v: v["speculation"]["draft_model_identity"].__setitem__("quantization", "q4")),
            ("draft.backend", lambda v: v["speculation"]["draft_model_identity"].__setitem__("runtime_backend", "other")),
            ("draft.runtime", lambda v: v["speculation"]["draft_model_identity"].__setitem__("runtime_version", "2")),
            ("tokenizer", lambda v: v["speculation"]["draft_model_identity"]["tokenizer"].__setitem__("revision", "other")),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                changed = copy.deepcopy(source)
                mutate(changed)
                self.assertNotEqual(hashlib.sha256(normalized_json_bytes(changed)).hexdigest(), original)

    def test_mode_null_rules_unknown_extension_and_config_v02_refuse(self) -> None:
        source = load(FIXTURE / "draft_spec_on.json")
        cases = []
        missing_draft = copy.deepcopy(source)
        missing_draft["speculation"]["draft_model_identity"] = None
        cases.append(missing_draft)
        off_with_zero = copy.deepcopy(source)
        off_with_zero["speculation"] = {"mode": "off", "max_proposed_tokens": 0, "draft_model_identity": None, "native_mtp_identity": None}
        cases.append(off_with_zero)
        unknown = copy.deepcopy(source)
        unknown["schema_extensions"] = ["example.unknown.v1"]
        cases.append(unknown)
        partial = copy.deepcopy(source)
        partial.pop("batch_policy")
        cases.append(partial)
        v02 = copy.deepcopy(source)
        v02["schema_version"] = "0.2"
        cases.append(v02)
        for case in cases:
            with self.assertRaises(SchemaError):
                BenchmarkConfig.from_mapping(case)

    def test_request_roster_hash_domains_and_boolean_integer_refusal(self) -> None:
        roster_path = FIXTURE / "request_roster.json"
        roster = RequestRoster.from_mapping(load(roster_path))
        self.assertEqual(roster.to_bytes(), roster_path.read_bytes())
        self.assertEqual(roster.sha256, "502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9")
        self.assertEqual(request_prompt_sha256("prompt_text", "Hello"), roster.requests[0].prompt_sha256)
        self.assertNotEqual(request_prompt_sha256("token_ids", [1, 2]), request_prompt_sha256("prompt_text", "[1,2]"))
        bad = load(roster_path)
        bad["requests"][0]["request_ordinal"] = False
        with self.assertRaises(AxiSchemaError):
            RequestRoster.from_mapping(bad)

    def test_exported_config_schema_has_exact_axi_surfaces(self) -> None:
        schema = BenchmarkConfig.json_schema()
        self.assertEqual(schema["properties"]["schema_extensions"]["maxItems"], 1)
        self.assertFalse(schema["$defs"]["axi_batch_policy"]["additionalProperties"])
        self.assertEqual(set(schema["$defs"]["axi_batch_policy"]["required"]), BatchPolicy.KEYS)
        self.assertEqual(set(schema["$defs"]["axi_speculation_policy"]["required"]), SpeculationPolicy.KEYS)

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema not installed")
    def test_exported_config_schema_accepts_emitted_and_rejects_extra(self) -> None:
        import jsonschema

        schema = BenchmarkConfig.json_schema()
        emitted = draft_config().to_dict()
        jsonschema.validate(emitted, schema)
        emitted["batch_policy"]["extra"] = 1
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(emitted, schema)


class AxiWireSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = draft_config()
        self.speculation = self.config.speculation
        self.batch = self.config.batch_policy

    def test_metadata_event_request_and_token_goldens(self) -> None:
        metadata_path = GOLDEN / "axi_metadata_draft.json"
        metadata = load(metadata_path)
        self.assertEqual(normalized_json_bytes(metadata), metadata_path.read_bytes())
        validate_v2_metadata(metadata, self.batch, self.speculation)

        emission_path = GOLDEN / "axi_decode_emission.json"
        emission = load(emission_path)
        self.assertEqual(normalized_json_bytes(emission), emission_path.read_bytes())
        validate_v2_event(emission, self.speculation)

        cancellation_path = GOLDEN / "axi_cancelled_terminal.json"
        cancellation = load(cancellation_path)
        self.assertEqual(normalized_json_bytes(cancellation), cancellation_path.read_bytes())
        validate_v2_event(cancellation, self.speculation)

        request_path = GOLDEN / "axi_request_row.json"
        validate_request_row(load(request_path), self.speculation)
        self.assertEqual(normalized_json_bytes(load(request_path)), request_path.read_bytes())

        token_path = GOLDEN / "axi_request_token_row.json"
        validate_request_token_row(load(token_path))
        self.assertEqual(normalized_json_bytes(load(token_path)), token_path.read_bytes())

    def test_event_top_level_is_exact_five_keys_and_token_is_singleton(self) -> None:
        event = load(GOLDEN / "axi_decode_emission.json")
        event["request_id"] = "illegal-top-level"
        with self.assertRaises(AxiSchemaError):
            validate_v2_event(event, self.speculation)
        token = load(GOLDEN / "axi_request_token_row.json")
        event = load(GOLDEN / "axi_decode_emission.json")
        event["event_type"] = "token"
        event["metadata"] = {
            key: event["metadata"][key]
            for key in (
                "request_id", "request_ordinal", "request_input_id", "request_event_ordinal",
                "request_roster_sha256", "source_identity", "batch_group_id",
                "scheduler_step_id", "decode_step_ordinal",
            )
        }
        event["metadata"].update(
            output_token_ordinal=token["output_token_ordinal"],
            token_id=token["token_id"],
            timestamp_provenance=token["timestamp_provenance"],
        )
        validate_v2_event(event, self.speculation)
        event["metadata"]["emitted_count"] = 2
        with self.assertRaises(AxiSchemaError):
            validate_v2_event(event, self.speculation)

    def test_required_nullable_keys_reject_omission(self) -> None:
        event = load(GOLDEN / "axi_decode_emission.json")
        for key in ("batch_group_id", "scheduler_step_id", "emitted_token_ids", "emitted_token_ids_sha256"):
            with self.subTest(key=key):
                changed = copy.deepcopy(event)
                changed["metadata"].pop(key)
                with self.assertRaises(AxiSchemaError):
                    validate_v2_event(changed, self.speculation)
        changed = copy.deepcopy(event)
        changed["metadata"]["scheduler_step_id"] = None
        changed["metadata"]["emitted_token_ids"] = None
        changed["metadata"]["emitted_token_ids_sha256"] = None
        validate_v2_event(changed, self.speculation)

    def test_target_tokenizer_is_exact_runtime_identity(self) -> None:
        value = load(GOLDEN / "axi_metadata_draft.json")["runtime"]["target_tokenizer_identity"]
        TargetTokenizerIdentity.from_mapping(value)
        for changed in (
            {**value, "extra": 1},
            {**value, "revision": "unknown"},
            {"name": value["name"], "revision": value["revision"]},
        ):
            with self.assertRaises(AxiSchemaError):
                TargetTokenizerIdentity.from_mapping(changed)

    def test_terminal_cancellation_retains_positive_counter_and_cap(self) -> None:
        event = load(GOLDEN / "axi_cancelled_terminal.json")
        event["metadata"]["cancelled_proposal_counters"]["tokens_proposed"] = 0
        with self.assertRaises(AxiSchemaError):
            validate_v2_event(event, self.speculation)
        event = load(GOLDEN / "axi_cancelled_terminal.json")
        event["metadata"]["cancelled_proposal_counters"]["tokens_proposed"] = 5
        with self.assertRaisesRegex(AxiSchemaError, "proposal_count_exceeds_configured_cap"):
            validate_v2_event(event, self.speculation)


class AxiSummarySchemaTests(unittest.TestCase):
    def test_summary_v060_hand_authored_canonical_golden(self) -> None:
        path = GOLDEN / "axi_summary_v060.json"
        summary = v060_summary()
        self.assertEqual(summary.canonical_bytes(), path.read_bytes())
        self.assertEqual(summary.to_dict(), load(path))

    def test_summary_v060_rejects_null_zero_and_missing_overlap_semantics(self) -> None:
        summary = v060_summary()
        changed = copy.deepcopy(summary)
        object.__setattr__(changed.decode_counter_rollup, "acceptance_rate", 0.0)
        with self.assertRaises(SchemaError):
            changed.validate()
        changed = v060_summary()
        changed.measurement_quality.phase_identifiability.pop("group_phase_windows_overlap")
        with self.assertRaises(SchemaError):
            changed.validate()

    def test_summary_schema_is_separate_and_exact_for_new_objects(self) -> None:
        schema = SummaryMetricsV060.json_schema()
        self.assertEqual(schema["title"], "JouleWise SummaryMetricsV060")
        self.assertFalse(schema["$defs"]["decode_counter_rollup"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["request_decode_metric"]["additionalProperties"])
        self.assertEqual(
            schema["$defs"]["summary_provenance"]["properties"]["reducer_version"],
            {"enum": ["0.6.0", "0.6.1", "0.6.2"]},
        )

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema not installed")
    def test_summary_schema_accepts_golden_and_rejects_extra_counter_key(self) -> None:
        import jsonschema

        schema = SummaryMetricsV060.json_schema()
        payload = load(GOLDEN / "axi_summary_v060.json")
        jsonschema.validate(payload, schema)
        payload["decode_counter_rollup"]["mean_rate"] = 0.5
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)


if __name__ == "__main__":
    unittest.main()
