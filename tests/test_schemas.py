import copy
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
import warnings
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.bundle_read import BundleReader
from joulewise.schemas import (
    BenchmarkConfig,
    EnergyEvidence,
    FailureReason,
    IdleBaseline,
    PromptTokenEvidencePolicy,
    RunStatus,
    SchemaError,
    SUMMARY_REDUCER_ID,
    SUMMARY_REDUCER_VERSION,
    SUMMARY_SCHEMA_VERSION,
    SummaryMetrics,
    TelemetryBackend,
    summary_validation_problems,
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
    "mock_axi_spec.json": "6fbc1e2c94e84a86e6322aefa06d8318af2454ca42b4e4a79651932bb1e41124",
}

OMITTED_OPTIONAL_KEYS = {
    "workload_profile": {
        "suite_manifest_ref",
        "suite_manifest_sha256",
        "generator_sidecar_ref",
        "prompt_token_evidence_policy",
    },
}
OMITTED_TOP_LEVEL_KEYS = {"schema_extensions", "batch_policy", "speculation"}


def valid_succeeded_summary(**changes: Any) -> SummaryMetrics:
    values = {
        "status": RunStatus.SUCCEEDED,
        "energy_request_j": 1.0,
        "gross_energy_j": 2.0,
        **changes,
    }
    return SummaryMetrics(**values)


def _fragment_matches(
    instance: Any,
    fragment: dict[str, Any],
    root: dict[str, Any] | None = None,
) -> bool:
    """Evaluate the exported schemas' semantic-condition subset in bare CI."""

    if root is None:
        root = fragment
    ref = fragment.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        return _fragment_matches(instance, root["$defs"][ref.split("/")[-1]], root)
    expected_type = fragment.get("type")
    if expected_type is not None:
        allowed = [expected_type] if isinstance(expected_type, str) else expected_type
        type_matches = {
            "null": instance is None,
            "object": isinstance(instance, dict),
            "string": isinstance(instance, str),
            "number": isinstance(instance, (int, float)) and not isinstance(instance, bool),
            "integer": isinstance(instance, int) and not isinstance(instance, bool),
            "array": isinstance(instance, list),
        }
        if not any(type_matches.get(name, True) for name in allowed):
            return False
    if "const" in fragment and instance != fragment["const"]:
        return False
    if "enum" in fragment and instance not in fragment["enum"]:
        return False
    if isinstance(instance, str):
        if len(instance) < fragment.get("minLength", 0):
            return False
        pattern = fragment.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            return False
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = fragment.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            return False
    if "required" in fragment:
        if not isinstance(instance, dict) or any(
            key not in instance for key in fragment["required"]
        ):
            return False
    if isinstance(instance, dict):
        for key, child in fragment.get("properties", {}).items():
            if key in instance and not _fragment_matches(instance[key], child, root):
                return False
    if isinstance(instance, list) and isinstance(fragment.get("items"), dict):
        if any(
            not _fragment_matches(item, fragment["items"], root)
            for item in instance
        ):
            return False
    if "not" in fragment and _fragment_matches(instance, fragment["not"], root):
        return False
    if "allOf" in fragment and not all(
        _fragment_matches(instance, child, root) for child in fragment["allOf"]
    ):
        return False
    if "oneOf" in fragment and sum(
        _fragment_matches(instance, child, root) for child in fragment["oneOf"]
    ) != 1:
        return False
    if "anyOf" in fragment and not any(
        _fragment_matches(instance, child, root) for child in fragment["anyOf"]
    ):
        return False
    if "contains" in fragment and not (
        isinstance(instance, list)
        and any(
            _fragment_matches(item, fragment["contains"], root) for item in instance
        )
    ):
        return False
    condition = fragment.get("if")
    if condition is not None and _fragment_matches(instance, condition, root):
        if not _fragment_matches(instance, fragment.get("then", {}), root):
            return False
    return True


def exported_config_semantics_accept(data: dict[str, Any]) -> bool:
    schema = BenchmarkConfig.json_schema()
    return _fragment_matches(data, schema, schema)


def exported_summary_semantics_accept(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    schema = SummaryMetrics.json_schema()
    return _fragment_matches(data, schema, schema)


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

    def test_prompt_token_evidence_policy_is_validated_and_exported(self) -> None:
        data = json.loads(
            (ROOT / "configs" / "examples" / "mock_suite_local.json").read_text()
        )
        data["workload_profile"]["prompt_token_evidence_policy"] = (
            "exempt_affine_generated_text"
        )

        config = BenchmarkConfig.from_mapping(data)

        self.assertEqual(
            config.workload_profile.prompt_token_evidence_policy,
            PromptTokenEvidencePolicy.EXEMPT_AFFINE_GENERATED_TEXT,
        )
        self.assertEqual(
            config.to_dict()["workload_profile"]["prompt_token_evidence_policy"],
            "exempt_affine_generated_text",
        )
        policy_schema = BenchmarkConfig.json_schema()["$defs"]["workload_profile"][
            "properties"
        ]["prompt_token_evidence_policy"]
        self.assertEqual(
            policy_schema["enum"],
            ["required", "exempt_affine_generated_text", None],
        )

    def test_unknown_prompt_token_evidence_policy_is_rejected(self) -> None:
        data = json.loads(
            (ROOT / "configs" / "examples" / "mock_suite_local.json").read_text()
        )
        data["workload_profile"]["prompt_token_evidence_policy"] = "trust_neighbor"

        with self.assertRaisesRegex(
            SchemaError, "prompt_token_evidence_policy must be one of"
        ):
            BenchmarkConfig.from_mapping(data)

    def test_json_schema_has_required_contract_fields(self) -> None:
        schema = BenchmarkConfig.json_schema()
        self.assertIn("model", schema["required"])
        self.assertIn("quantization", schema["required"])
        self.assertIn("hardware_target", schema["required"])
        self.assertIn("workload_profile", schema["required"])
        self.assertIn("mlx", schema["$defs"]["hardware_target"]["properties"]["runtime_backend"]["enum"])

    def test_config_validate_and_exported_schema_semantic_parity_matrix(self) -> None:
        base = json.loads(
            (ROOT / "configs" / "examples" / "mock_local.json").read_text()
        )
        cases: list[tuple[str, dict[str, Any], bool]] = []

        def add(label: str, mutate, accepted: bool) -> None:
            data = copy.deepcopy(base)
            mutate(data)
            cases.append((label, data, accepted))

        add("valid", lambda data: None, True)
        add(
            "multiple-prompt-sources",
            lambda data: data["workload_profile"].update(prompt_text="hello"),
            False,
        )
        add(
            "no-prompt-source",
            lambda data: data["workload_profile"].pop("prompt_tokens"),
            False,
        )
        add(
            "suite-ref-without-hash",
            lambda data: (
                data["workload_profile"].pop("prompt_tokens"),
                data["workload_profile"].update(suite_manifest_ref="suite.json"),
            ),
            False,
        )
        add(
            "suite-pair",
            lambda data: (
                data["workload_profile"].pop("prompt_tokens"),
                data["workload_profile"].update(
                    suite_manifest_ref="suite.json", suite_manifest_sha256="abc"
                ),
            ),
            True,
        )
        add(
            "ssh-without-host",
            lambda data: data["hardware_target"].update(transport="ssh"),
            False,
        )
        add(
            "ssh-with-host",
            lambda data: data["hardware_target"].update(
                transport="ssh", host="benchmark-host"
            ),
            True,
        )
        add(
            "additive-unknown",
            lambda data: data["workload_profile"].update(additive_optional=True),
            True,
        )
        add(
            "whitespace-only-model-name",
            lambda data: data["model"].update(name=" \t"),
            False,
        )

        for label, data, accepted in cases:
            with self.subTest(label=label):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        BenchmarkConfig.from_mapping(data)
                except SchemaError:
                    validator_accepted = False
                else:
                    validator_accepted = True
                self.assertEqual(validator_accepted, accepted)
                self.assertEqual(exported_config_semantics_accept(data), accepted)


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

    def test_writer_schema_and_bundle_reader_summary_parity_matrix(self) -> None:
        available = valid_succeeded_summary().to_dict()
        absent = valid_succeeded_summary(
            energy_request_j=None,
            window_evidence_precheck={
                "idle_subtracted_request": {
                    "energy_evidence": EnergyEvidence.ABSENT.value,
                    "eligible": False,
                    "reasons": ["idle_baseline_unrecorded"],
                }
            },
        ).to_dict()
        additive = {**available, "future_optional_evidence": {"version": 1}}
        cases: list[tuple[str, Any, bool]] = [
            ("succeeded", available, True),
            ("succeeded-no-idle-baseline", absent, True),
            ("legacy-v0.1-succeeded", available, True),
            ("failed-salvage", {"status": "failed", "failure_reason": "unknown_error"}, True),
            (
                "unsupported-salvage",
                {"status": "unsupported", "failure_reason": "unsupported_workload"},
                True,
            ),
            ("additive-optional", additive, True),
            ("json-null", None, False),
            ("status-only-succeeded", {"status": "succeeded"}, False),
            (
                "legacy-null-request-energy",
                {**available, "energy_request_j": None},
                False,
            ),
            (
                "absent-state-with-request-energy",
                {**absent, "energy_request_j": 1.0},
                False,
            ),
            ("failed-without-reason", {"status": "failed"}, False),
            (
                "malformed-nested-idle-baseline",
                {
                    **available,
                    "idle_baseline": {
                        "power_w_mean": 1.0,
                        "power_w_stddev": 0.1,
                        "duration_s": 5.0,
                        "sample_count": "two",
                        "telemetry_backend": "mock",
                    },
                },
                False,
            ),
        ]

        # This is deliberately the full status x energy-field x validity
        # product. A failed or unsupported summary may omit/null energy, but
        # no status may carry a non-numeric value through the writer, reader,
        # or exported schema boundary.
        status_bases = {
            "succeeded": available,
            "failed": {"status": "failed", "failure_reason": "unknown_error"},
            "unsupported": {
                "status": "unsupported",
                "failure_reason": "unsupported_workload",
            },
        }
        energy_fields = (
            "energy_request_j",
            "energy_token_j",
            "energy_output_token_j",
            "gross_energy_j",
            "idle_subtracted_energy_j",
        )
        field_validities = {
            "absent": object(),
            "null": None,
            "number": 1.0,
            "non-numeric-string": "bad",
            "non-numeric-bool": True,
        }
        for status, base in status_bases.items():
            for field in energy_fields:
                for validity, value in field_validities.items():
                    payload = copy.deepcopy(base)
                    if validity == "absent":
                        payload.pop(field, None)
                    else:
                        payload[field] = value

                    accepted = True
                    if validity in {"non-numeric-string", "non-numeric-bool"}:
                        accepted = False
                    elif status == "succeeded" and validity == "absent":
                        accepted = False
                    elif status == "succeeded" and validity == "null":
                        accepted = field not in {
                            "energy_request_j",
                            "gross_energy_j",
                        }
                    cases.append(
                        (f"{status}-{field}-{validity}", payload, accepted)
                    )

        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / "summary_metrics.json"
            for label, payload, accepted in cases:
                summary_path.write_text(json.dumps(payload) + "\n")
                with self.subTest(label=label):
                    # Feed the exact serialized cell to the writer validator.
                    # Constructing from ``payload`` would normalize omitted
                    # dataclass fields to None before validate() sees them.
                    with patch.object(SummaryMetrics, "_payload", return_value=payload):
                        try:
                            SummaryMetrics(status=RunStatus.SUCCEEDED).validate()
                        except SchemaError:
                            writer_accepted = False
                        else:
                            writer_accepted = True

                    surfaces = {
                        "summary_validation_problems": not summary_validation_problems(payload),
                        "SummaryMetrics.validate": writer_accepted,
                        "SummaryMetrics.json_schema": exported_summary_semantics_accept(payload),
                        "BundleReader.is_complete": BundleReader(Path(tmp)).is_complete(),
                    }
                    for surface, observed in surfaces.items():
                        self.assertEqual(
                            observed,
                            accepted,
                            f"{label}: {surface} acceptance diverged",
                        )

    def test_summary_metrics_writer_uses_canonical_succeeded_predicate(self) -> None:
        valid_succeeded_summary().validate()
        valid_succeeded_summary(
            energy_request_j=None,
            window_evidence_precheck={
                "idle_subtracted_request": {
                    "energy_evidence": EnergyEvidence.ABSENT.value,
                    "eligible": False,
                    "reasons": ["idle_baseline_unrecorded"],
                }
            },
        ).validate()
        with self.assertRaisesRegex(SchemaError, "gross_energy_j"):
            SummaryMetrics(
                status=RunStatus.SUCCEEDED,
                energy_request_j=1.0,
            ).validate()

    def test_summary_metrics_schema_has_phase_energy_field(self) -> None:
        # Additive Phase 2 (Slice 2D) output field per R-015.
        schema = SummaryMetrics.json_schema()
        self.assertEqual(
            schema["properties"]["phase_energy_j"], {"type": ["object", "null"]}
        )
        self.assertNotIn("phase_energy_j", schema["required"])
        payload = valid_succeeded_summary(
            phase_energy_j={"prefill": 1.0, "decode": 2.0}
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
        payload = valid_succeeded_summary().to_dict()
        self.assertIsNone(payload["suite_metrics"])
        self.assertEqual(payload["summary_provenance"]["reducer_version"], "0.5.0")

    def test_inter_token_throughput_is_additive_nullable_metric(self) -> None:
        schema = SummaryMetrics.json_schema()
        self.assertEqual(
            schema["properties"]["inter_token_throughput_tokens_s"],
            {"type": ["number", "null"]},
        )
        self.assertNotIn("inter_token_throughput_tokens_s", schema["required"])
        payload = valid_succeeded_summary().to_dict()
        self.assertIn("inter_token_throughput_tokens_s", payload)
        self.assertIsNone(payload["inter_token_throughput_tokens_s"])

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
            "duration_weighted_newey_west_bartlett_10s_iid_floor_v2",
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
        self.assertEqual(idle_props["gpu_freq_mhz_mean"]["x-unit"], "MHz")
        self.assertIn("megahertz", idle_props["gpu_freq_mhz_mean"]["description"])
        self.assertEqual(idle_props["gpu_freq_hz_mean"]["x-unit"], "MHz")
        self.assertIs(idle_props["gpu_freq_hz_mean"]["deprecated"], True)
        self.assertIn("legacy alias", idle_props["gpu_freq_hz_mean"]["description"])
        self.assertEqual(idle_props["idle_window_suspect"], {"type": ["boolean", "null"]})
        self.assertEqual(quality_schema["required"], ["requested_sampling_hz"])
        self.assertEqual(quality_props["idle_window_suspect"], {"type": ["boolean", "null"]})
        self.assertEqual(quality_props["token_counts_source"], {"type": ["string", "null"]})
        self.assertEqual(quality_props["phase_identifiability"], {"type": ["object", "null"]})

    def test_idle_gpu_frequency_alias_serializes_additively_cross_backend(self) -> None:
        for backend in TelemetryBackend:
            value = 325.9148 if backend == TelemetryBackend.POWERMETRICS else None
            with self.subTest(backend=backend.value):
                idle = IdleBaseline(
                    power_w_mean=1.0,
                    power_w_stddev=0.0,
                    duration_s=5.0,
                    sample_count=5,
                    telemetry_backend=backend,
                    gpu_freq_mhz_mean=value,
                    gpu_freq_hz_mean=value,
                )
                payload = valid_succeeded_summary(idle_baseline=idle).to_dict()
                self.assertIn("gpu_freq_mhz_mean", payload["idle_baseline"])
                self.assertIn("gpu_freq_hz_mean", payload["idle_baseline"])
                self.assertEqual(payload["idle_baseline"]["gpu_freq_mhz_mean"], value)
                self.assertEqual(payload["idle_baseline"]["gpu_freq_hz_mean"], value)

    def test_summary_metrics_emit_summary_provenance(self) -> None:
        payload = valid_succeeded_summary().to_dict()
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
                set(emitted) | OMITTED_TOP_LEVEL_KEYS,
                set(schema["properties"]),
                f"top-level keys ({name})",
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
                    "prompt_token_evidence_policy",
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
                    expected = {
                        "generator_sidecar_ref",
                        "prompt_token_evidence_policy",
                    }
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
