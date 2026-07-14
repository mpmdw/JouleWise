import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.clock import FakeClock
from joulewise.cli import main, validate_bundle
from joulewise.controller import run_benchmark
from joulewise.schemas import (
    BenchmarkConfig,
    EnergyEvidence,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)


class CliTests(unittest.TestCase):
    def test_dirty_source_bundle_still_completes_and_remains_structurally_valid(self) -> None:
        config_data = json.loads(Path("configs/examples/mock_local.json").read_text())
        config_data["run_id"] = "dirty-source-completes"
        config = BenchmarkConfig.from_mapping(config_data)
        dirty = {
            "git_commit": "1" * 40,
            "tracked": "dirty",
            "staged": "clean",
            "untracked": "clean",
            "diff_sha256": "2" * 64,
        }
        with tempfile.TemporaryDirectory() as tmp, mock.patch(
            "joulewise.bundle._capture_source_state", return_value=dirty
        ):
            bundle, _ = run_benchmark(config, Path(tmp), FakeClock())
            self.assertTrue((bundle / "summary_metrics.json").is_file())
            self.assertEqual(validate_bundle(bundle, strict=False), [])
            metadata = json.loads((bundle / "metadata.json").read_text())
            self.assertIs(metadata["source_provenance"]["claim_eligible"], False)

    def test_strict_cli_rejects_single_fixed_budget_realized_output_mismatch(self) -> None:
        config_data = json.loads(Path("configs/examples/mock_local.json").read_text())
        config_data["run_id"] = "strict-realized-output"
        config = BenchmarkConfig.from_mapping(config_data)
        with tempfile.TemporaryDirectory() as tmp:
            bundle, _ = run_benchmark(config, Path(tmp), FakeClock())
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(["validate-bundle", str(bundle), "--strict"]), 0)

            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["workload_provenance"]["generator"]["name"] = (
                "mlx_lm.stream_generate"
            )
            policy = metadata["workload_provenance"]["output_policy"]
            policy["emitted_tokens"] -= 1
            metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate-bundle", str(bundle), "--strict"])
            self.assertEqual(exit_code, 2)
            output = stdout.getvalue()
            self.assertIn("output_token_count does not match", output)
            self.assertIn("row count 8 does not equal emitted_tokens 7", output)
            self.assertIn("decode token-event count 8 does not equal emitted_tokens 7", output)

    def test_validate_config_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["validate-config", "configs/examples/mock_local.json"])
        self.assertEqual(exit_code, 0)
        self.assertIn("valid config", stdout.getvalue())
        self.assertIn("runtime=mock", stdout.getvalue())

    def test_print_config_schema_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["print-config-schema"])
        self.assertEqual(exit_code, 0)
        self.assertIn("JouleWise BenchmarkConfig", stdout.getvalue())

    def test_print_output_schema_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["print-output-schema"])
        self.assertEqual(exit_code, 0)
        self.assertIn("JouleWise SummaryMetrics", stdout.getvalue())

    def test_reducer_output_and_cli_admission_parity_matrix(self) -> None:
        cases = (
            (
                "succeeded-with-energy",
                SummaryMetrics(
                    status=RunStatus.SUCCEEDED,
                    energy_request_j=1.0,
                    gross_energy_j=2.0,
                ),
                0,
            ),
            (
                "succeeded-without-request-energy",
                SummaryMetrics(
                    status=RunStatus.SUCCEEDED,
                    gross_energy_j=2.0,
                    window_evidence_precheck={
                        "idle_subtracted_request": {
                            "energy_evidence": EnergyEvidence.ABSENT.value,
                            "eligible": False,
                            "reasons": ["idle_baseline_unrecorded"],
                        }
                    },
                ),
                0,
            ),
            (
                "failed",
                SummaryMetrics(
                    status=RunStatus.FAILED,
                    failure_reason=FailureReason.UNKNOWN_ERROR,
                ),
                3,
            ),
            (
                "unsupported",
                SummaryMetrics(
                    status=RunStatus.UNSUPPORTED,
                    failure_reason=FailureReason.UNSUPPORTED_WORKLOAD,
                ),
                3,
            ),
            (
                "invalid-succeeded",
                SummaryMetrics(
                    status=RunStatus.SUCCEEDED,
                    energy_request_j=1.0,
                ),
                3,
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            bundle.mkdir()
            (bundle / "config.json").write_text(json.dumps({}) + "\n")
            for label, summary, expected in cases:
                (bundle / "summary_metrics.json").unlink(missing_ok=True)
                with self.subTest(label=label), mock.patch(
                    "joulewise.cli.reduce_bundle", return_value=summary
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(main(["reduce", str(bundle)]), expected)
                    self.assertEqual(
                        (bundle / "summary_metrics.json").is_file(),
                        label != "invalid-succeeded",
                    )


if __name__ == "__main__":
    unittest.main()
