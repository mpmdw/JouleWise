"""Tests for the shared bundle read layer (Slice 2N.8; D-025, D-026, D-027).

The reader owns bundle parsing and interpretation policy for every consumer
(reducer, report, validate-bundle). Fixtures are assembled with the real
``RunBundleWriter`` under a ``FakeClock`` plus hand-authored artifacts, the
same way the reducer suite builds its bundles.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import BenchmarkConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"


def load_config(**overrides) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    for key, value in overrides.items():
        data[key] = value
    return BenchmarkConfig.from_mapping(data)


class ReaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.clock = FakeClock(start=0.0)

    def make_bundle(self, run_id: str) -> RunBundleWriter:
        return RunBundleWriter.create(
            self.runs_root, load_config(run_id=run_id), self.clock
        )

    def add_event(
        self,
        writer: RunBundleWriter,
        event_type: str,
        phase: str,
        timestamp_s: float,
    ) -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=timestamp_s,
                event_type=event_type,
                phase=phase,
                message=f"{event_type} {phase}",
            )
        )

    def write_metadata(self, writer: RunBundleWriter, rail_manifest: list[str]) -> None:
        writer.write_metadata(
            {"device": {"telemetry": "mock", "rail_manifest": rail_manifest}}
        )


class StrictAccessorTests(ReaderTestCase):
    def test_missing_config_is_structured_read_error(self) -> None:
        reader = BundleReader(self.runs_root / "does-not-exist")
        with self.assertRaises(BundleReadError) as ctx:
            reader.config()
        self.assertIn("config.json", str(ctx.exception))

    def test_corrupt_config_is_structured_read_error(self) -> None:
        writer = self.make_bundle("corrupt-config")
        (writer.path / "config.json").write_text("{not json")
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).config()
        self.assertIn("not valid JSON", str(ctx.exception))

    def test_schema_invalid_config_is_structured_read_error(self) -> None:
        writer = self.make_bundle("schema-invalid-config")
        (writer.path / "config.json").write_text(json.dumps({"schema_version": "x"}))
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).config()
        self.assertIn("does not re-validate", str(ctx.exception))

    def test_missing_metadata_is_structured_read_error(self) -> None:
        writer = self.make_bundle("no-metadata")
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).metadata()
        self.assertIn("metadata.json", str(ctx.exception))

    def test_malformed_event_line_is_structured_read_error(self) -> None:
        writer = self.make_bundle("bad-events")
        (writer.path / "events.jsonl").write_text('{"ok": 1}\nnot json\n')
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).events()
        self.assertIn("line 2", str(ctx.exception))

    def test_valid_bundle_parses_config_and_metadata(self) -> None:
        writer = self.make_bundle("valid")
        self.write_metadata(writer, ["mock"])
        reader = BundleReader(writer.path)
        self.assertEqual(reader.config().run_id, "valid")
        self.assertEqual(reader.rail_manifest(), ["mock"])


class CompletionStateTests(ReaderTestCase):
    def test_bundle_without_summary_is_incomplete(self) -> None:
        writer = self.make_bundle("incomplete")
        self.assertFalse(BundleReader(writer.path).is_complete())

    def test_bundle_with_summary_is_complete(self) -> None:
        writer = self.make_bundle("complete")
        (writer.path / "summary_metrics.json").write_text('{"status": "succeeded"}')
        self.assertTrue(BundleReader(writer.path).is_complete())

    def test_corrupt_summary_is_incomplete_and_tolerant_none(self) -> None:
        writer = self.make_bundle("corrupt-summary")
        (writer.path / "summary_metrics.json").write_text("{broken")
        reader = BundleReader(writer.path)
        self.assertFalse(reader.is_complete())
        self.assertIsNone(reader.raw_summary())


class MeasuredWindowTests(ReaderTestCase):
    def test_markers_preferred_over_stage_boundaries(self) -> None:
        writer = self.make_bundle("markers")
        self.add_event(writer, "stage_started", "measured_run", 10.0)
        self.add_event(writer, "sampling_started", "measured_run", 13.0)
        self.add_event(writer, "sampling_stopped", "measured_run", 20.0)
        self.add_event(writer, "stage_completed", "measured_run", 22.0)
        window = BundleReader(writer.path).measured_window()
        self.assertEqual((window.start_s, window.end_s), (13.0, 20.0))

    def test_stage_boundaries_are_the_pre_2n_fallback(self) -> None:
        writer = self.make_bundle("stage-fallback")
        self.add_event(writer, "stage_started", "measured_run", 10.0)
        self.add_event(writer, "stage_completed", "measured_run", 22.0)
        window = BundleReader(writer.path).measured_window()
        self.assertEqual((window.start_s, window.end_s), (10.0, 22.0))

    def test_no_window_when_events_missing(self) -> None:
        writer = self.make_bundle("no-window")
        self.assertIsNone(BundleReader(writer.path).measured_window())


class RailAlignmentTests(ReaderTestCase):
    """D-027: per-rail rows for one sample instant must share one timestamp."""

    def _write_trace(self, writer: RunBundleWriter, samples: list[PowerSample]) -> None:
        writer.write_power_trace(samples)

    def test_aligned_multi_rail_sums_exactly(self) -> None:
        writer = self.make_bundle("aligned")
        self.write_metadata(writer, ["a", "b"])
        samples = []
        for t in (0.0, 1.0, 2.0):
            samples.append(PowerSample(timestamp_s=t, power_w=3.0, source="m", rail="a"))
            samples.append(PowerSample(timestamp_s=t, power_w=4.0, source="m", rail="b"))
        self._write_trace(writer, samples)
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual([point.t for point in curve], [0.0, 1.0, 2.0])
        for point in curve:
            self.assertAlmostEqual(point.power_w, 7.0, places=9)

    def test_skewed_multi_rail_is_structured_failure_naming_the_gap(self) -> None:
        writer = self.make_bundle("skewed")
        self.write_metadata(writer, ["a", "b"])
        samples = [
            PowerSample(timestamp_s=0.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=0.001, power_w=4.0, source="m", rail="b"),
            PowerSample(timestamp_s=1.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=1.001, power_w=4.0, source="m", rail="b"),
        ]
        self._write_trace(writer, samples)
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).summed_curve()
        message = str(ctx.exception)
        self.assertIn("misaligned", message)
        self.assertIn("D-027", message)
        self.assertIn("'b'", message)  # the missing rail at the first timestamp

    def test_single_rail_never_misaligns(self) -> None:
        writer = self.make_bundle("single-rail")
        self.write_metadata(writer, ["mock"])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=5.0, source="m", rail="mock"),
                PowerSample(timestamp_s=1.0, power_w=5.0, source="m", rail="mock"),
            ],
        )
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual(len(curve), 2)

    def test_empty_manifest_yields_empty_curve_no_fallback(self) -> None:
        # 2N.7: no consumer may invent a fallback summation policy.
        writer = self.make_bundle("empty-manifest")
        self.write_metadata(writer, [])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=5.0, source="m", rail="mock"),
                PowerSample(timestamp_s=1.0, power_w=5.0, source="m", rail="mock"),
            ],
        )
        self.assertEqual(BundleReader(writer.path).summed_curve(), [])

    def test_non_manifest_rail_ignored(self) -> None:
        writer = self.make_bundle("extra-rail")
        self.write_metadata(writer, ["a"])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=3.0, source="m", rail="a"),
                PowerSample(timestamp_s=0.5, power_w=99.0, source="m", rail="c"),
                PowerSample(timestamp_s=1.0, power_w=3.0, source="m", rail="a"),
            ],
        )
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual([point.t for point in curve], [0.0, 1.0])


class ProblemsParityTests(ReaderTestCase):
    """BundleReader.problems is the validate-bundle policy (one home, D-025)."""

    def test_problems_matches_cli_validate_bundle(self) -> None:
        from joulewise.cli import validate_bundle

        writer = self.make_bundle("parity")
        # Structurally broken on purpose: no metadata/summary yet.
        reader_problems = BundleReader(writer.path).problems()
        self.assertEqual(reader_problems, validate_bundle(writer.path))
        self.assertTrue(
            any("metadata.json" in problem for problem in reader_problems)
        )


if __name__ == "__main__":
    unittest.main()
