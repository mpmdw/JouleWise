from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.bundle import BundleError, RunBundleWriter
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.cli import validate_bundle
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"


def load_config(run_id: str) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG.read_text())
    data["run_id"] = run_id
    return BenchmarkConfig.from_mapping(data)


class BundleAuditCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.clock = FakeClock(start=0.0)

    def make_complete_bundle(self, run_id: str) -> Path:
        writer = RunBundleWriter.create(self.runs_root, load_config(run_id), self.clock)
        writer.append_event(RuntimeEvent(0.0, "stage_started", "measured_run", "start"))
        writer.append_event(RuntimeEvent(2.0, "stage_completed", "measured_run", "end"))
        writer.write_power_trace(
            [
                PowerSample(0.0, 7.0, "mock", "mock"),
                PowerSample(1.0, 7.0, "mock", "mock"),
                PowerSample(2.0, 7.0, "mock", "mock"),
            ]
        )
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": "mock"}},
                "idle_baseline": {
                    "power_w_mean": 5.0,
                    "power_w_stddev": 0.0,
                    "duration_s": 1.0,
                    "sample_count": 2,
                    "telemetry_backend": "mock",
                },
            }
        )
        writer.write_summary(reduce_bundle(writer.path))
        self.clock.sleep(3.0)
        return writer.finalize()


class BundleValidationBugPins(BundleAuditCase):
    # B2/S5: BundleReader.problems() never recomputes config.json sha256 against metadata.config_sha256.
    def test_validate_bundle_rejects_config_sha256_mismatch(self) -> None:
        bundle = self.make_complete_bundle("audit-sha")
        config = json.loads((bundle / "config.json").read_text())
        config["run_metadata"]["notes"] = "tampered after metadata hash"
        (bundle / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")

        problems = validate_bundle(bundle)
        self.assertTrue(any("config_sha256" in problem for problem in problems), problems)

    def test_validate_bundle_requires_metadata_config_sha256(self) -> None:
        bundle = self.make_complete_bundle("audit-sha-missing")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("config_sha256")
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

        problems = validate_bundle(bundle)
        self.assertIn("metadata.config_sha256 is missing", problems)

    # B1/rank 7: summary validation accepts a status-only succeeded summary with no metrics.
    def test_status_only_succeeded_summary_is_not_complete_or_valid(self) -> None:
        bundle = self.make_complete_bundle("audit-status-only")
        (bundle / "summary_metrics.json").write_text('{"status": "succeeded"}\n')

        self.assertFalse(BundleReader(bundle).is_complete())
        problems = validate_bundle(bundle)
        self.assertTrue(any("energy_request_j" in problem for problem in problems), problems)

    def test_is_complete_false_for_status_only_succeeded_summary(self) -> None:
        bundle = self.make_complete_bundle("audit-status-only-complete")
        (bundle / "summary_metrics.json").write_text('{"status": "succeeded"}\n')

        self.assertFalse(BundleReader(bundle).is_complete())

    def test_summary_validator_consistency_for_completion(self) -> None:
        cases = [
            ("valid-writer-success", None, True),
            ("status-only-success", {"status": "succeeded"}, False),
            (
                "nullable-token-success",
                {
                    **json.loads(
                        (self.make_complete_bundle("audit-summary-template") / "summary_metrics.json")
                        .read_text()
                    ),
                    "energy_token_j": None,
                    "energy_output_token_j": None,
                    "idle_subtracted_energy_j": None,
                },
                True,
            ),
            (
                "minimal-failed",
                {"status": "failed", "failure_reason": "unknown_error"},
                True,
            ),
        ]
        for label, summary, should_be_complete in cases:
            bundle = self.make_complete_bundle(f"audit-summary-{label}")
            if summary is not None:
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
            reader = BundleReader(bundle)
            summary_problems = [
                problem
                for problem in validate_bundle(bundle)
                if problem.startswith("summary ")
                or problem == "summary_metrics.json is not a JSON object"
            ]
            with self.subTest(label=label):
                self.assertEqual(reader.is_complete(), should_be_complete)
                self.assertEqual(summary_problems == [], should_be_complete, summary_problems)

    # B3: default bundle validation parses metadata.json but never requires it to be an object.
    def test_validate_bundle_rejects_metadata_non_object(self) -> None:
        bundle = self.make_complete_bundle("audit-metadata-list")
        (bundle / "metadata.json").write_text("[]\n")

        problems = validate_bundle(bundle)
        self.assertIn("metadata.json is not a JSON object", problems)

    # B4/ranks 2-3: power_trace.csv NaN/Infinity rows parse as floats and are not rejected.
    def test_summed_curve_rejects_non_finite_trace_numbers(self) -> None:
        bundle = self.make_complete_bundle("audit-nan-curve")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n"
            "0.0,nan,mock,mock\n"
            "1.0,7.0,mock,mock\n"
        )

        with self.assertRaisesRegex(BundleReadError, "finite"):
            BundleReader(bundle).summed_curve()

    # B4/ranks 2-3: validate-bundle only checks the power trace header, not row values.
    def test_validate_bundle_rejects_non_finite_trace_rows(self) -> None:
        bundle = self.make_complete_bundle("audit-nan-validate")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n"
            "0.0,nan,mock,mock\n"
            "1.0,7.0,mock,mock\n"
        )

        problems = validate_bundle(bundle)
        self.assertTrue(any("power_trace.csv row 2" in problem for problem in problems), problems)

    # B5: duplicate rail rows at one timestamp are silently summed, double-counting energy.
    def test_summed_curve_rejects_duplicate_rail_at_timestamp(self) -> None:
        bundle = self.make_complete_bundle("audit-duplicate-rail")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n"
            "0.0,7.0,mock,mock\n"
            "0.0,7.0,mock,mock\n"
            "1.0,7.0,mock,mock\n"
        )

        with self.assertRaisesRegex(BundleReadError, "duplicate"):
            BundleReader(bundle).summed_curve()

    def test_validate_bundle_rejects_duplicate_rail_at_timestamp(self) -> None:
        bundle = self.make_complete_bundle("audit-duplicate-rail-validate")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n"
            "0.0,7.0,mock,mock\n"
            "0.0,7.0,mock,mock\n"
            "1.0,7.0,mock,mock\n"
        )

        problems = validate_bundle(bundle)
        self.assertTrue(any("duplicate rail row" in problem for problem in problems), problems)

    def test_single_rail_duplicate_timestamp_is_rejected(self) -> None:
        bundle = self.make_complete_bundle("audit-single-rail-duplicate")
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail\n"
            "0.0,7.0,mock,mock\n"
            "0.0,8.0,mock,mock\n"
        )

        with self.assertRaisesRegex(BundleReadError, "duplicate"):
            BundleReader(bundle).summed_curve()
        problems = validate_bundle(bundle)
        self.assertTrue(any("duplicate rail row" in problem for problem in problems), problems)

    # Rank 1: write_output() accepts traversal out of outputs/.
    def test_write_output_rejects_path_traversal_name(self) -> None:
        writer = RunBundleWriter.create(self.runs_root, load_config("audit-output-traversal"), self.clock)
        with self.assertRaisesRegex(BundleError, "plain file name"):
            writer.write_output("../escape.txt", "nope")

    # Rank 1: log_path() accepts traversal out of logs/.
    def test_log_path_rejects_path_traversal_name(self) -> None:
        writer = RunBundleWriter.create(self.runs_root, load_config("audit-log-traversal"), self.clock)
        with self.assertRaisesRegex(BundleError, "plain file name"):
            writer.log_path("../escape.log")

    # Rank 11: rail_manifest() coerces non-string rails with str() instead of rejecting metadata.
    def test_rail_manifest_rejects_non_string_entries(self) -> None:
        bundle = self.make_complete_bundle("audit-rail-manifest")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["device"]["rail_manifest"] = [1, None]
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

        with self.assertRaisesRegex(BundleReadError, "rail_manifest"):
            BundleReader(bundle).rail_manifest()

    # Rank 12: strict events() accepts missing/extra keys that validate-bundle rejects.
    def test_strict_events_rejects_non_contract_key_set(self) -> None:
        bundle = self.make_complete_bundle("audit-event-keys")
        records = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        records[0].pop("phase")
        (bundle / "events.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))

        with self.assertRaisesRegex(BundleReadError, "keys"):
            BundleReader(bundle).events()

    # Rank 24: experiment IDs like "..." sanitize to punctuation-only run IDs instead of failing.
    def test_punctuation_only_run_id_sanitizes_to_allowed_nonempty_value(self) -> None:
        writer = RunBundleWriter.create(self.runs_root, load_config("..."), self.clock)

        self.assertEqual(writer.run_id, "---")
        self.assertEqual(writer.path.name, "---")
        self.assertRegex(writer.run_id, r"^[a-z0-9_-]+$")

    # B8: write_raw() can leave a partial raw artifact that blocks retry.
    def test_write_raw_partial_failure_does_not_poison_retry(self) -> None:
        writer = RunBundleWriter.create(self.runs_root, load_config("audit-raw-retry"), self.clock)
        original_write_bytes = Path.write_bytes
        failed_once = False

        def flaky_write_bytes(path: Path, data: bytes):
            nonlocal failed_once
            if path.parent == writer.path / "raw" and path.name.startswith(".capture.bin.") and not failed_once:
                failed_once = True
                original_write_bytes(path, data[:2])
                raise OSError("simulated crash during raw write")
            return original_write_bytes(path, data)

        with mock.patch.object(Path, "write_bytes", flaky_write_bytes):
            with self.assertRaises(OSError):
                writer.write_raw("capture.bin", b"abcdef")

        try:
            path = writer.write_raw("capture.bin", b"abcdef")
        except BundleError as exc:
            self.assertIn("raw artifact already exists", str(exc))
            self.fail(f"B8: retry blocked by partial raw artifact: {exc}")
        except Exception as exc:
            self.fail(f"B8: retry raised raw {type(exc).__name__} instead of rewriting capture.bin")
        self.assertEqual(path.read_bytes(), b"abcdef")


if __name__ == "__main__":
    unittest.main()


class StrictValidateZeroWindowTests(BundleAuditCase):
    """P2-040 FIX-1 (ARC-3): strict admission of succeeded zero-window bundles."""

    def make_succeeded_zero_window_bundle(self, run_id: str) -> Path:
        from joulewise.schemas import RunStatus, SummaryMetrics

        writer = RunBundleWriter.create(self.runs_root, load_config(run_id), self.clock)
        writer.append_event(RuntimeEvent(2.0, "stage_started", "measured_run", "start"))
        writer.append_event(RuntimeEvent(2.0, "stage_completed", "measured_run", "end"))
        writer.write_power_trace(
            [
                PowerSample(0.0, 7.0, "mock", "mock"),
                PowerSample(1.0, 7.0, "mock", "mock"),
                PowerSample(2.0, 7.0, "mock", "mock"),
            ]
        )
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": "mock"}},
            }
        )
        # A (wrongly) succeeded stored summary over the zero window.
        writer.write_summary(
            SummaryMetrics(status=RunStatus.SUCCEEDED, gross_energy_j=0.0)
        )
        self.clock.sleep(3.0)
        return writer.finalize()

    def test_succeeded_zero_window_is_rejected_even_when_fresh_summary_comparison_is_stubbed_equal(
        self,
    ) -> None:
        bundle = self.make_succeeded_zero_window_bundle("strict-zero-window")
        with mock.patch(
            "joulewise.cli._strict_summary_differences", return_value=[]
        ):
            problems = validate_bundle(bundle, strict=True)
        self.assertIn(
            "strict: succeeded bundle measured window duration must be > 0 s; "
            "got 0.0",
            problems,
        )
