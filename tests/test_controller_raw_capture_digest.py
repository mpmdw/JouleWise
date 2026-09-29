"""Writer-only raw capture custody; recomputation here adds no reader refusal."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.adapters.mock_telemetry import MockTelemetryAdapter, RAW_SAMPLES_NAME
from joulewise.bundle import write_raw_artifact
from joulewise.bundle_read import BundleReader
from joulewise.clock import FakeClock
from joulewise.cli import validate_bundle
from joulewise.controller import run_benchmark
from joulewise.interfaces import AdapterResult
from joulewise.publication_privacy import (
    audit_private_bundle,
    transform_public_bundle,
    verify_public_bundle,
)
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, RunStatus
from tests.test_publication_privacy import SOURCE_PROVENANCE


def recompute_raw_captures(bundle: Path) -> dict:
    """Independent test oracle over bytes, also usable after a tamper."""
    result = {}
    for path in (bundle / "raw").rglob("*"):
        if path.is_file():
            raw = path.read_bytes()
            result[path.relative_to(bundle).as_posix()] = {
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            }
    return result


class ControllerRawCaptureDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.runs_root = Path(temporary.name) / "runs"
        config_path = (
            Path(__file__).resolve().parents[1] / "configs/examples/mock_local.json"
        )
        self.config = BenchmarkConfig.from_mapping(json.loads(config_path.read_text()))
        self.clock = FakeClock(start=1_700_000_000.0)

    def test_mock_capture_map_is_written_before_reduction_and_detects_byte_flip(self) -> None:
        observed = {}

        def inspect_then_reduce(bundle):
            observed.update(json.loads((bundle / "metadata.json").read_text()))
            self.assertEqual(observed["raw_capture_sha256"], recompute_raw_captures(bundle))
            self.assertFalse((bundle / "summary_metrics.json").exists())
            return reduce_bundle(bundle)

        bundle, summary = run_benchmark(
            self.config, self.runs_root, self.clock, reducer=inspect_then_reduce
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        recorded = observed["raw_capture_sha256"]
        self.assertEqual(set(recorded), {f"raw/{RAW_SAMPLES_NAME}"})
        reader = BundleReader(bundle)
        self.assertEqual(reader.metadata()["raw_capture_sha256"], recorded)
        self.assertEqual(reader.raw_metadata()["raw_capture_sha256"], recorded)
        self.assertEqual(reader.problems(), [])
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        capture = bundle / "raw" / RAW_SAMPLES_NAME
        raw = bytearray(capture.read_bytes())
        raw[0] ^= 1
        capture.write_bytes(raw)
        recomputed = recompute_raw_captures(bundle)
        self.assertNotEqual(recomputed, recorded)
        self.assertEqual(
            recomputed[f"raw/{RAW_SAMPLES_NAME}"]["size_bytes"],
            recorded[f"raw/{RAW_SAMPLES_NAME}"]["size_bytes"],
        )
        self.assertEqual(
            json.loads((bundle / "metadata.json").read_text())["raw_capture_sha256"],
            recorded,
        )

    def test_all_captures_include_empty_binary_nested_and_late_cleanup_bytes(self) -> None:
        original_stop = MockTelemetryAdapter.stop_sampling

        def stop_with_captures(adapter, config, context=None):
            samples = original_stop(adapter, config, context)
            write_raw_artifact(context, "empty.bin", b"")
            write_raw_artifact(context, "workload.bin", b"\x00\xff\r\n" * 300_000)
            nested = context.raw_dir / "custody"
            nested.mkdir()
            (nested / "partial.bin").write_bytes(b"partial")
            return samples

        def late_cleanup(adapter, config, context=None):
            # Emulate final adapter custody arriving after sampler shutdown.
            (context.raw_dir / RAW_SAMPLES_NAME).write_bytes(b"late capture bytes\x00")
            return AdapterResult(ok=True)

        with (
            patch.object(MockTelemetryAdapter, "stop_sampling", stop_with_captures),
            patch.object(MockRuntimeAdapter, "cleanup", late_cleanup),
        ):
            bundle, summary = run_benchmark(self.config, self.runs_root, self.clock)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        recorded = json.loads((bundle / "metadata.json").read_text())["raw_capture_sha256"]
        self.assertEqual(recorded, recompute_raw_captures(bundle))
        self.assertEqual(
            set(recorded),
            {f"raw/{RAW_SAMPLES_NAME}", "raw/empty.bin",
             "raw/workload.bin", "raw/custody/partial.bin"},
        )
        self.assertEqual(recorded["raw/empty.bin"]["size_bytes"], 0)
        self.assertEqual(
            recorded[f"raw/{RAW_SAMPLES_NAME}"]["sha256"],
            hashlib.sha256(b"late capture bytes\x00").hexdigest(),
        )

    def test_failure_before_sampling_records_empty_map(self) -> None:
        data = self.config.to_dict()
        data["hardware_target"]["notes"] = "telemetry-denied"
        bundle, summary = run_benchmark(
            BenchmarkConfig.from_mapping(data), self.runs_root, self.clock
        )
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(
            json.loads((bundle / "metadata.json").read_text())["raw_capture_sha256"],
            {},
        )

    def test_privacy_audit_accepts_and_public_projection_retains_capture_map(self) -> None:
        # Publication requires clean source provenance; use the existing
        # privacy fixture rather than the implementation worktree's state.
        with patch("joulewise.bundle._capture_source_state",
                   return_value=dict(SOURCE_PROVENANCE["start"])):
            bundle, summary = run_benchmark(self.config, self.runs_root, self.clock)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        recorded = json.loads((bundle / "metadata.json").read_text())["raw_capture_sha256"]
        source_metadata = (bundle / "metadata.json").read_bytes()
        audit = audit_private_bundle(bundle)
        captured = next(item for item in audit.files
                        if item.path == f"raw/{RAW_SAMPLES_NAME}")
        self.assertEqual(recorded[captured.path], {
            "sha256": captured.sha256, "size_bytes": captured.size_bytes,
        })
        public = self.runs_root.parent / "public"
        transform_public_bundle(bundle, public)
        self.assertEqual(
            json.loads((public / "metadata.json").read_text())["raw_capture_sha256"],
            recorded,
        )
        self.assertEqual(verify_public_bundle(public), [])
        self.assertEqual((bundle / "metadata.json").read_bytes(), source_metadata)

    def test_failed_workload_records_salvaged_sampler_capture(self) -> None:
        original_run = MockRuntimeAdapter.run_workload

        def fail_after_workload(adapter, config, context=None):
            original_run(adapter, config, context)
            raise RuntimeError("injected failure after mock workload")

        with patch.object(MockRuntimeAdapter, "run_workload", fail_after_workload):
            bundle, summary = run_benchmark(self.config, self.runs_root, self.clock)
        self.assertEqual(summary.status, RunStatus.FAILED)
        recorded = json.loads((bundle / "metadata.json").read_text())["raw_capture_sha256"]
        self.assertEqual(set(recorded), {f"raw/{RAW_SAMPLES_NAME}"})
        self.assertEqual(recorded, recompute_raw_captures(bundle))


if __name__ == "__main__":
    unittest.main()
