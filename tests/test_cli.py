import io
import json
import math
import plistlib
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from joulewise.adapters.powermetrics import duration_weighted_mean_and_sample_variance
from joulewise.clock import FakeClock
from joulewise.cli import main, validate_bundle
from joulewise.controller import run_benchmark
from joulewise.idle_dependence import estimate_newey_west_bartlett
from joulewise.reduce import reduce_bundle
from joulewise.schemas import (
    BenchmarkConfig,
    EnergyEvidence,
    FailureReason,
    RunStatus,
    SUMMARY_REDUCER_VERSION,
    SummaryMetrics,
)


def _idle_powermetrics_stream(
    powers_w: list[float], intervals_s: list[float]
) -> bytes:
    documents = []
    for power_w, interval_s in zip(powers_w, intervals_s, strict=True):
        documents.append(
            {
                "timestamp": datetime(2026, 7, 14, tzinfo=timezone.utc),
                "elapsed_ns": int(interval_s * 1_000_000_000),
                "processor": {
                    "cpu_power": power_w * 1000.0,
                    "gpu_power": 0.0,
                    "ane_power": 0.0,
                    "cpu_energy": 0,
                    "gpu_energy": 0,
                    "ane_energy": 0,
                },
            }
        )
    return b"\0".join(plistlib.dumps(document) for document in documents)


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

    def test_strict_reducer_version_acceptance_matrix(self) -> None:
        config_data = json.loads(Path("configs/examples/mock_local.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)

            # Frozen provenance-less legacy summaries retain their exact
            # compatibility arm. Patch only the identity table so this
            # production-path fixture does not depend on the retained corpus.
            config_data["run_id"] = "strict-frozen-legacy-replay"
            legacy_bundle, _ = run_benchmark(
                BenchmarkConfig.from_mapping(config_data), runs_root, FakeClock()
            )
            legacy_metadata = json.loads((legacy_bundle / "metadata.json").read_text())
            legacy_identity = (
                legacy_metadata["run_id"],
                legacy_metadata["config_sha256"],
            )
            legacy_summary_path = legacy_bundle / "summary_metrics.json"
            legacy_summary = json.loads(legacy_summary_path.read_text())
            del legacy_summary["summary_provenance"]
            legacy_summary_path.write_text(
                json.dumps(legacy_summary, indent=2, sort_keys=True) + "\n"
            )
            with mock.patch(
                "joulewise.cli._STRICT_LEGACY_BUNDLE_IDENTITIES",
                frozenset({legacy_identity}),
            ):
                self.assertEqual(validate_bundle(legacy_bundle, strict=True), [])

            # A fresh bundle cannot opt into a superseded reducer by relabeling
            # its declared version and deleting the discriminating new field.
            config_data["run_id"] = "strict-current-0.4.1-field-deleted"
            adversarial_bundle, _ = run_benchmark(
                BenchmarkConfig.from_mapping(config_data), runs_root, FakeClock()
            )
            adversarial_summary_path = adversarial_bundle / "summary_metrics.json"
            adversarial_summary = json.loads(adversarial_summary_path.read_text())
            adversarial_summary["summary_provenance"]["reducer_version"] = "0.4.1"
            del adversarial_summary["inter_token_throughput_tokens_s"]
            adversarial_summary_path.write_text(
                json.dumps(adversarial_summary, indent=2, sort_keys=True) + "\n"
            )
            self.assertIn(
                "strict: unsupported reducer version "
                "'0.4.1' for current-era bundle; superseded versions "
                "cannot claim the current inter_token_throughput_tokens_s "
                f"reduction shape and explicit re-reduction with {SUMMARY_REDUCER_VERSION} is "
                "required",
                validate_bundle(adversarial_bundle, strict=True),
            )

            for version in ("0.4.1", "0.4.2"):
                with self.subTest(version=version):
                    config_data["run_id"] = f"strict-current-{version}"
                    bundle, _ = run_benchmark(
                        BenchmarkConfig.from_mapping(config_data),
                        runs_root,
                        FakeClock(),
                    )
                    summary_path = bundle / "summary_metrics.json"
                    summary = json.loads(summary_path.read_text())
                    summary["summary_provenance"]["reducer_version"] = version
                    summary_path.write_text(
                        json.dumps(summary, indent=2, sort_keys=True) + "\n"
                    )

                    self.assertIn(
                        "strict: unsupported reducer version "
                        f"'{version}' for current-era bundle; superseded versions "
                        "cannot claim the current inter_token_throughput_tokens_s "
                        "reduction shape and explicit re-reduction with "
                        f"{SUMMARY_REDUCER_VERSION} is "
                        "required",
                        validate_bundle(bundle, strict=True),
                    )

            config_data["run_id"] = "strict-current-default"
            current_bundle, _ = run_benchmark(
                BenchmarkConfig.from_mapping(config_data), runs_root, FakeClock()
            )
            current_summary = json.loads(
                (current_bundle / "summary_metrics.json").read_text()
            )
            self.assertEqual(
                current_summary["summary_provenance"]["reducer_version"],
                SUMMARY_REDUCER_VERSION,
            )
            self.assertEqual(SUMMARY_REDUCER_VERSION, "0.5.1")
            self.assertEqual(validate_bundle(current_bundle, strict=True), [])

    def test_weighted_idle_drift_flips_strict_verdict_from_legacy_counterfactual(
        self,
    ) -> None:
        config_data = json.loads(Path("configs/examples/mock_local.json").read_text())
        config_data["run_id"] = "strict-weighted-idle-drift"
        powers_w = [4.0] * 27 + [10.0] * 6
        intervals_s = [1.0] * 27 + [1.2] * 6
        weighted_mean_w, weighted_variance_w2 = (
            duration_weighted_mean_and_sample_variance(powers_w, intervals_s)
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, _ = run_benchmark(
                BenchmarkConfig.from_mapping(config_data), Path(tmp), FakeClock()
            )
            raw_idle = _idle_powermetrics_stream(powers_w, intervals_s)
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(raw_idle)
            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["idle_baseline"] = {
                "power_w_mean": weighted_mean_w,
                "power_w_stddev": math.sqrt(weighted_variance_w2),
                "duration_s": math.fsum(intervals_s),
                "sample_count": len(powers_w),
                "telemetry_backend": "powermetrics",
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            weighted_summary = reduce_bundle(bundle).to_dict()
            (bundle / "summary_metrics.json").write_text(
                json.dumps(weighted_summary, indent=2, sort_keys=True) + "\n"
            )

            self.assertEqual(
                weighted_summary["summary_provenance"]["reducer_version"],
                SUMMARY_REDUCER_VERSION,
            )
            self.assertEqual(weighted_summary["idle_mean_uncertainty"]["status"], "estimated")
            self.assertEqual(validate_bundle(bundle, strict=True), [])

            # Counterfactual only: omitting durations invokes the frozen
            # arithmetic v1 arm. With drift concentrated in the long records,
            # its baseline disagrees with the raw interval-supported evidence
            # and must lose the strict verdict under the 0.5.0 reducer.
            legacy_unweighted_counterfactual = estimate_newey_west_bartlett(
                powers_w,
                weighted_summary["idle_mean_uncertainty"]["lag_count"],
            )
            arithmetic_mean_w = math.fsum(powers_w) / len(powers_w)
            self.assertGreater(weighted_mean_w - arithmetic_mean_w, 0.15)
            metadata["idle_baseline"].update(
                {
                    "power_w_mean": arithmetic_mean_w,
                    "power_w_stddev": math.sqrt(
                        legacy_unweighted_counterfactual.sample_variance_w2
                    ),
                }
            )
            metadata_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            counterfactual_summary = reduce_bundle(bundle).to_dict()
            (bundle / "summary_metrics.json").write_text(
                json.dumps(counterfactual_summary, indent=2, sort_keys=True) + "\n"
            )

            self.assertEqual(
                counterfactual_summary["idle_mean_uncertainty"]["status"],
                "not_estimable",
            )
            self.assertEqual(
                counterfactual_summary["idle_mean_uncertainty"]["reason_codes"],
                ["idle_metadata_mismatch"],
            )
            self.assertIn(
                "strict: raw idle trace does not match metadata.idle_baseline "
                "(idle_metadata_mismatch)",
                validate_bundle(bundle, strict=True),
            )

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
