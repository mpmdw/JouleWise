import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SchemaError,
    SUMMARY_REDUCER_ID,
    SUMMARY_REDUCER_VERSION,
    SUMMARY_SCHEMA_VERSION,
    SummaryMetrics,
)


ROOT = Path(__file__).resolve().parents[1]

#: jsonschema is NOT a project dependency (D-009: CI runs bare Python); the
#: full-validator round-trip test is a bonus that runs only where it happens
#: to be installed. The field-level nullability checks below run everywhere.
HAS_JSONSCHEMA = importlib.util.find_spec("jsonschema") is not None

#: Pinned SHA-256 of each example config's normalized (sorted-key, 2-space,
#: trailing-newline) ``to_dict()`` JSON - the exact D-001/D-022 hash input.
#: A serialization change silently changes config hashes and therefore run
#: identity (D-022 suffixes, experiment grouping); this pin makes any such
#: change fail loudly so it can be decided deliberately (2N.5 / D-029).
PINNED_CONFIG_SHA256 = {
    "mock_local.json": "15a556a8ea5853f6aef1d5d6a814d97264f6bc0b9dd11274755c98a7ec686355",
    "mock_affine_smoke.json": "cd113411afe49a2047b7efd1cd1237fca3f48c1e31fe54c5f15f610ef6190592",
    "mac_mlx_local.json": "e9878c0ed7735eb48293581b0944c1f5e1d08e67c9b77f0fafd8c4c265020f3e",
    "mac_mlx_mock_telemetry.json": "4023dee935eb17d1a4da1f2bd90af9404de2eca33f1df9c41382e4750fd93eda",
    "mac_mlx_qwen35_122b.json": "100d76977dffab1ae841124c4708727ac45ab793bbe0061dd87a6d9f54dbb97a",
    "mock_suite_local.json": "e33e9587b37996e4c94767129eaae5575079821dc07ce5dbbe4331095a4ed58d",
    "nvidia_vllm_ssh.json": "a8a8ed0ca03e5d50247ef1f3b0520962660141f144107cef8e8b4bdb6e7e8f81",
}

OMITTED_OPTIONAL_KEYS = {
    "workload_profile": {
        "suite_manifest_ref",
        "suite_manifest_sha256",
        "generator_sidecar_ref",
    },
}


class BenchmarkConfigTests(unittest.TestCase):
    def test_example_configs_validate(self) -> None:
        for path in sorted((ROOT / "configs" / "examples").glob("*.json")):
            with self.subTest(path=path.name):
                data = json.loads(path.read_text())
                config = BenchmarkConfig.from_mapping(data)
                self.assertEqual(config.schema_version, "0.1")
                self.assertEqual(config.to_dict()["schema_version"], "0.1")

    def test_ssh_target_requires_host(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        data["hardware_target"]["transport"] = "ssh"
        with self.assertRaisesRegex(SchemaError, "host is required"):
            BenchmarkConfig.from_mapping(data)

    def test_workload_requires_prompt_source(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        data["workload_profile"].pop("prompt_tokens")
        data["workload_profile"].pop("prompt_text", None)
        data["workload_profile"].pop("dataset_ref", None)
        with self.assertRaisesRegex(SchemaError, "prompt_text, prompt_tokens, or dataset_ref"):
            BenchmarkConfig.from_mapping(data)

    def test_suite_manifest_ref_and_sha256_are_required_together(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        data["workload_profile"].pop("prompt_tokens")
        data["workload_profile"]["suite_manifest_ref"] = "suite.json"
        with self.assertRaisesRegex(SchemaError, "required together"):
            BenchmarkConfig.from_mapping(data)

    def test_suite_manifest_ref_is_fourth_prompt_source(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        data["workload_profile"]["suite_manifest_ref"] = "suite.json"
        data["workload_profile"]["suite_manifest_sha256"] = "abc"
        data["workload_profile"]["generator_sidecar_ref"] = "suite_annotations.json"
        with self.assertRaisesRegex(SchemaError, "mutually exclusive"):
            BenchmarkConfig.from_mapping(data)
        data["workload_profile"].pop("prompt_tokens")
        config = BenchmarkConfig.from_mapping(data)
        self.assertEqual(config.workload_profile.suite_manifest_ref, "suite.json")
        self.assertEqual(config.workload_profile.suite_manifest_sha256, "abc")
        self.assertEqual(config.workload_profile.generator_sidecar_ref, "suite_annotations.json")
        self.assertEqual(
            config.to_dict()["workload_profile"]["generator_sidecar_ref"],
            "suite_annotations.json",
        )

    def test_json_schema_has_required_contract_fields(self) -> None:
        schema = BenchmarkConfig.json_schema()
        self.assertIn("model", schema["required"])
        self.assertIn("quantization", schema["required"])
        self.assertIn("hardware_target", schema["required"])
        self.assertIn("workload_profile", schema["required"])
        self.assertIn("mlx", schema["$defs"]["hardware_target"]["properties"]["runtime_backend"]["enum"])


class SummaryMetricsTests(unittest.TestCase):
    def test_failed_summary_requires_reason(self) -> None:
        summary = SummaryMetrics(status=RunStatus.FAILED)
        with self.assertRaisesRegex(SchemaError, "failure_reason"):
            summary.to_dict()

    def test_succeeded_summary_rejects_reason(self) -> None:
        summary = SummaryMetrics(
            status=RunStatus.SUCCEEDED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
        )
        with self.assertRaisesRegex(SchemaError, "must not include"):
            summary.to_dict()

    def test_unsupported_summary_serializes_reason(self) -> None:
        summary = SummaryMetrics(
            status=RunStatus.UNSUPPORTED,
            failure_reason=FailureReason.UNSUPPORTED_WORKLOAD,
            failure_message="mock unsupported workload",
        )
        payload = summary.to_dict()
        self.assertEqual(payload["status"], "unsupported")
        self.assertEqual(payload["failure_reason"], "unsupported_workload")

    def test_summary_metrics_schema_has_failure_contract(self) -> None:
        schema = SummaryMetrics.json_schema()
        self.assertIn("status", schema["required"])
        self.assertIn("failure_reason", schema["properties"])

    def test_summary_metrics_schema_has_phase_energy_field(self) -> None:
        # Additive Phase 2 (Slice 2D) output field per R-015.
        schema = SummaryMetrics.json_schema()
        self.assertEqual(
            schema["properties"]["phase_energy_j"], {"type": ["object", "null"]}
        )
        self.assertNotIn("phase_energy_j", schema["required"])
        payload = SummaryMetrics(
            status=RunStatus.SUCCEEDED, phase_energy_j={"prefill": 1.0, "decode": 2.0}
        ).to_dict()
        self.assertEqual(payload["phase_energy_j"], {"prefill": 1.0, "decode": 2.0})

    def test_summary_metrics_has_additive_suite_metrics_field(self) -> None:
        schema = SummaryMetrics.json_schema()
        self.assertIn("suite_metrics", schema["properties"])
        self.assertNotIn("suite_metrics", schema["required"])
        suite_summary = schema["$defs"]["suite_summary"]
        self.assertIn("floor_abs_j", suite_summary["required"])
        self.assertIn("floor_cmp_j", suite_summary["required"])
        self.assertEqual(suite_summary["properties"]["floor_abs_j"], {"type": ["number", "null"]})
        self.assertEqual(suite_summary["properties"]["floor_cmp_j"], {"type": ["number", "null"]})
        payload = SummaryMetrics(status=RunStatus.SUCCEEDED).to_dict()
        self.assertIsNone(payload["suite_metrics"])
        self.assertEqual(payload["summary_provenance"]["reducer_version"], "0.4.1")

    def test_idle_mean_uncertainty_schema_freezes_shape_and_reasons(self) -> None:
        schema = SummaryMetrics.json_schema()
        self.assertIn("idle_mean_uncertainty", schema["properties"])
        idle = schema["$defs"]["idle_mean_uncertainty"]
        self.assertEqual(
            set(idle["required"]),
            set(idle["properties"]),
        )
        self.assertEqual(
            idle["properties"]["method"]["const"],
            "newey_west_bartlett_10s_iid_floor_v1",
        )
        self.assertEqual(idle["properties"]["bandwidth_s"]["const"], 10.0)
        self.assertEqual(
            idle["properties"]["correlation_scope"]["const"],
            "independent_run",
        )
        self.assertEqual(
            idle["properties"]["reason_codes"]["items"]["enum"],
            [
                "raw_idle_trace_unavailable",
                "raw_idle_trace_invalid",
                "nonfinite_idle_power",
                "insufficient_idle_samples",
                "idle_trace_span_below_three_bandwidths",
                "idle_cadence_irregular",
                "idle_metadata_mismatch",
                "backend_policy_not_frozen",
            ],
        )

    def test_measurement_quality_cleanup_fields_are_additive_nullable(self) -> None:
        schema = SummaryMetrics.json_schema()
        quality = schema["$defs"]["measurement_quality"]
        self.assertEqual(
            quality["properties"]["runtime_cleanup_ok"],
            {"type": ["boolean", "null"]},
        )
        self.assertEqual(
            quality["properties"]["remote_cleanup_failed"],
            {"type": ["array", "null"], "items": {"type": "string"}},
        )
        self.assertNotIn("runtime_cleanup_ok", quality["required"])
        self.assertNotIn("remote_cleanup_failed", quality["required"])
        self.assertIn("window_evidence_precheck", schema["properties"])
        self.assertNotIn("claim_eligibility", schema["properties"])

    def test_summary_metrics_schema_has_idle_gpu_quality_fields(self) -> None:
        schema = SummaryMetrics.json_schema()
        idle_props = schema["$defs"]["idle_baseline"]["properties"]
        quality_schema = schema["$defs"]["measurement_quality"]
        quality_props = quality_schema["properties"]
        self.assertEqual(idle_props["gpu_idle_ratio_mean"], {"type": ["number", "null"]})
        self.assertEqual(idle_props["gpu_idle_ratio_min"], {"type": ["number", "null"]})
        self.assertEqual(idle_props["gpu_freq_hz_mean"], {"type": ["number", "null"]})
        self.assertEqual(idle_props["idle_window_suspect"], {"type": ["boolean", "null"]})
        self.assertEqual(quality_schema["required"], ["requested_sampling_hz"])
        self.assertEqual(quality_props["idle_window_suspect"], {"type": ["boolean", "null"]})
        self.assertEqual(quality_props["token_counts_source"], {"type": ["string", "null"]})
        self.assertEqual(quality_props["phase_identifiability"], {"type": ["object", "null"]})

    def test_summary_metrics_emit_summary_provenance(self) -> None:
        payload = SummaryMetrics(status=RunStatus.SUCCEEDED).to_dict()
        self.assertEqual(
            payload["summary_provenance"],
            {
                "summary_schema_version": SUMMARY_SCHEMA_VERSION,
                "reducer_id": SUMMARY_REDUCER_ID,
                "reducer_version": SUMMARY_REDUCER_VERSION,
                "config_schema_version": "0.1",
            },
        )
        schema = SummaryMetrics.json_schema()
        self.assertIn("summary_provenance", schema["properties"])
        self.assertNotIn("summary_provenance", schema["required"])


def _resolve_ref(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    """Resolve a local ``#/$defs/...`` $ref one level deep (all this schema has)."""
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        return schema["$defs"][ref.split("/")[-1]]
    return node


class EmittedConfigRoundTripTests(unittest.TestCase):
    """Slice 2N.5 (D-029): a bundle's normalized ``config.json`` (the
    ``to_dict()`` form, which emits ``null`` for absent optionals) must
    validate against the exported ``print-config-schema`` schema."""

    def emitted_examples(self) -> list[tuple[str, dict[str, Any]]]:
        emitted = []
        for path in sorted((ROOT / "configs" / "examples").glob("*.json")):
            config = BenchmarkConfig.from_mapping(json.loads(path.read_text()))
            emitted.append((path.name, config.to_dict()))
        return emitted

    def test_every_null_valued_field_is_nullable_in_the_schema(self) -> None:
        # Bare-Python nullability check (CI installs no jsonschema, D-009):
        # every key that to_dict() emits as null must be declared nullable.
        schema = BenchmarkConfig.json_schema()
        for name, emitted in self.emitted_examples():
            for section_key, section_value in emitted.items():
                section_schema = _resolve_ref(
                    schema, schema["properties"][section_key]
                )
                if section_value is None:
                    with self.subTest(config=name, field=section_key):
                        self.assertIn("null", section_schema.get("type", []))
                    continue
                if not isinstance(section_value, dict):
                    continue
                for key, value in section_value.items():
                    if value is not None:
                        continue
                    with self.subTest(config=name, field=f"{section_key}.{key}"):
                        field_schema = section_schema["properties"][key]
                        self.assertIn(
                            "null",
                            field_schema.get("type", []),
                            f"{section_key}.{key} is emitted as null but the "
                            "schema does not allow null",
                        )

    def test_emitted_sections_carry_no_unknown_keys(self) -> None:
        # The schema must know every key to_dict() emits, or the round-trip
        # guarantee is vacuous for those keys.
        schema = BenchmarkConfig.json_schema()
        for name, emitted in self.emitted_examples():
            self.assertEqual(
                set(emitted), set(schema["properties"]), f"top-level keys ({name})"
            )
            for section_key, section_value in emitted.items():
                if not isinstance(section_value, dict):
                    continue
                section_schema = _resolve_ref(schema, schema["properties"][section_key])
                with self.subTest(config=name, section=section_key):
                    allowed_omissions = OMITTED_OPTIONAL_KEYS.get(section_key, set())
                    self.assertEqual(
                        set(section_value) | allowed_omissions,
                        set(section_schema["properties"]),
                    )

    def test_workload_to_dict_omits_suite_fields_only_when_none(self) -> None:
        self.assertEqual(
            OMITTED_OPTIONAL_KEYS,
            {
                "workload_profile": {
                    "suite_manifest_ref",
                    "suite_manifest_sha256",
                    "generator_sidecar_ref",
                }
            },
        )
        schema = BenchmarkConfig.json_schema()
        for name, emitted in self.emitted_examples():
            for section_key, section_value in emitted.items():
                if not isinstance(section_value, dict):
                    continue
                section_schema = _resolve_ref(schema, schema["properties"][section_key])
                omitted = set(section_schema["properties"]) - set(section_value)
                if section_key == "workload_profile":
                    suite_ref = section_value.get("suite_manifest_ref")
                    suite_sha = section_value.get("suite_manifest_sha256")
                    expected = {"generator_sidecar_ref"}
                    if suite_ref is None and suite_sha is None:
                        expected.update({"suite_manifest_ref", "suite_manifest_sha256"})
                else:
                    expected = set()
                with self.subTest(config=name, section=section_key):
                    self.assertEqual(omitted, expected)

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema not installed (optional)")
    def test_full_validator_round_trip(self) -> None:
        import jsonschema

        schema = BenchmarkConfig.json_schema()
        for name, emitted in self.emitted_examples():
            with self.subTest(config=name):
                jsonschema.validate(emitted, schema)

    def test_config_hash_is_pinned(self) -> None:
        # D-022/D-001: the config hash is identity. Any serialization change
        # must fail here and be decided deliberately, not slip in.
        for path in sorted((ROOT / "configs" / "examples").glob("*.json")):
            config = BenchmarkConfig.from_mapping(json.loads(path.read_text()))
            config_bytes = (
                json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            with self.subTest(config=path.name):
                self.assertEqual(
                    hashlib.sha256(config_bytes).hexdigest(),
                    PINNED_CONFIG_SHA256[path.name],
                )


if __name__ == "__main__":
    unittest.main()
