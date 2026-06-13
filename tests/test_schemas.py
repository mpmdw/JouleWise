import json
import unittest
from pathlib import Path

from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SchemaError,
    SummaryMetrics,
)


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
