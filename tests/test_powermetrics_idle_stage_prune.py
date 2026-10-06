"""Gate-prune 2, lane P2-ADAPT (M4): idle-stage software time in the adapter.

The change, in the pinned ``joulewise/adapters/powermetrics.py``:

``measure_idle`` decodes the idle slice's plist frames once and builds the
   baseline records and the rich rows from that one decode.  The outputs must
   stay byte-identical: the archived-bundle test re-derives real stored
   ``rich_telemetry_idle.jsonl`` files and ``idle_baseline`` numbers.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise import window_lineage
from joulewise.adapters import powermetrics
from joulewise.adapters.powermetrics import (
    RICH_IDLE_NAME,
    SAMPLERS,
    PowermetricsTelemetryAdapter,
    decode_rich_telemetry,
    parse_powermetrics_records,
    rich_telemetry_jsonl_from_records,
    sudoers_line,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import AdapterResult, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "powermetrics_sample.plist"
READINESS_METHOD = "admission_stream_readiness_document"
# Archived real bundles (not in the repository; the test skips without them).
DEFAULT_ARCHIVE_ROOTS = (
    "/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/g2a-root",
    "/Users/edr/night-archive/gate-prune/rehearsal-real/alpha-1/runs-parent",
)


def make_config(**sampling: Any) -> BenchmarkConfig:
    return BenchmarkConfig.from_mapping(
        {
            "schema_version": "0.1",
            "model": {"name": "mock-model"},
            "quantization": {"name": "none"},
            "hardware_target": {
                "id": "macbook_m3_max",
                "transport": "local",
                "runtime_backend": "mock",
                "telemetry_backend": "powermetrics",
            },
            "workload_profile": {
                "name": "mock_smoke",
                "prompt_tokens": 32,
                "output_tokens": 8,
            },
            "sampling": {"power_hz": 1.0, "idle_seconds": 5.0, **sampling},
        }
    )


def completed(command: list[str], returncode: int = 0, stderr: bytes = b""):
    return subprocess.CompletedProcess(command, returncode, stdout=b"", stderr=stderr)


def make_context(bundle: Path, config: BenchmarkConfig, clock: FakeClock) -> RunContext:
    bundle.mkdir(parents=True, exist_ok=True)
    return RunContext(
        config=config,
        clock=clock,
        run_id=bundle.name,
        bundle_path=bundle,
        raw_dir=bundle / "raw",
        logs_dir=bundle / "logs",
        outputs_dir=bundle / "outputs",
    )


def write_hazard_locator(runs_root: Path) -> None:
    runs_root.mkdir(parents=True, exist_ok=True)
    (runs_root / window_lineage.LOCATOR_BASENAME).write_text(
        json.dumps({"schema_version": window_lineage.HAZARD_LOCATOR_SCHEMA})
    )


def bounded_capture_run(data: bytes, calls: list[list[str]]):
    def fake_run(command, **_kwargs):
        calls.append(list(command))
        Path(command[command.index("-o") + 1]).write_bytes(data)
        return completed(command)

    return fake_run


class IdleSliceSingleDecodeTests(unittest.TestCase):
    def _measure(self, data: bytes, *, anchor: float, bundle: Path):
        clock = FakeClock(start=anchor)
        adapter = PowermetricsTelemetryAdapter(clock)
        adapter._capability = AdapterResult(ok=True)
        config = make_config()
        context = make_context(bundle, config, clock)
        calls: list[list[str]] = []
        with patch(
            "joulewise.adapters.powermetrics.subprocess.run",
            side_effect=bounded_capture_run(data, calls),
        ):
            baseline = adapter.measure_idle(config, context)
        return adapter, baseline, context

    def test_measure_idle_decodes_the_idle_frames_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch(
            "joulewise.adapters.powermetrics._powermetrics_documents",
            wraps=powermetrics._powermetrics_documents,
        ) as documents:
            self._measure(FIXTURE.read_bytes(), anchor=200.0, bundle=Path(tmp) / "run-1")
        self.assertEqual(documents.call_count, 1)

    def test_single_decode_outputs_equal_the_two_separate_decodes(self) -> None:
        # The fixture plus a garbage final frame exercises the dropped-frame
        # diagnostic as well as the records and rich rows.
        data = FIXTURE.read_bytes() + b"\0<?xml version='1.0'?><plist><dict>"
        anchor = 1791124395.196985
        expected_records, expected_diagnostic = powermetrics._parse_powermetrics_records(
            data, timestamp_anchor_s=anchor
        )
        expected_rich = decode_rich_telemetry(data, timestamp_anchor_s=anchor)
        self.assertIsNotNone(expected_diagnostic)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "run-1"
            adapter, baseline, _context = self._measure(data, anchor=anchor, bundle=bundle)
            self.assertEqual(
                (bundle / RICH_IDLE_NAME).read_bytes(),
                rich_telemetry_jsonl_from_records(expected_rich).encode(),
            )
        self.assertEqual(adapter._pre_idle_records, expected_records)
        self.assertEqual(adapter._last_records, expected_records)
        self.assertEqual(
            adapter.idle_admission_records(run_id="run-1", attempt=1), expected_rich
        )
        self.assertEqual(
            adapter._device_metadata["parse_diagnostics"],
            [
                expected_diagnostic.to_metadata(
                    artifact="raw/powermetrics_idle.plist",
                    capture="idle_baseline_attempt_1",
                )
            ],
        )
        self.assertEqual(baseline.sample_count, len(expected_records))

    def test_mid_stream_corrupt_frame_still_raises_before_any_rich_row(self) -> None:
        frames = [frame for frame in FIXTURE.read_bytes().split(b"\0") if frame.strip()]
        data = b"\0".join([frames[0], b"<plist><dict>", *frames[1:]])
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "run-1"
            with self.assertRaisesRegex(ValueError, "document 1 is not a valid plist"):
                self._measure(data, anchor=200.0, bundle=bundle)
            self.assertFalse((bundle / RICH_IDLE_NAME).exists())


def _archived_single_attempt_bundles(limit_per_root: int) -> list[Path]:
    roots = os.environ.get("JOULEWISE_M4_ARCHIVE_ROOTS")
    candidates = roots.split(os.pathsep) if roots else list(DEFAULT_ARCHIVE_ROOTS)
    bundles: list[Path] = []
    for root in candidates:
        found = 0
        for raw in sorted(Path(root).glob("**/raw/powermetrics_idle.plist")):
            bundle = raw.parent.parent
            try:
                metadata = json.loads((bundle / "metadata.json").read_bytes())
            except (OSError, ValueError):
                continue
            attempts = (metadata.get("environment_admission") or {}).get("attempts")
            if not isinstance(attempts, list) or len(attempts) != 1:
                continue
            if not (bundle / RICH_IDLE_NAME).is_file():
                continue
            bundles.append(bundle)
            found += 1
            if found >= limit_per_root:
                break
    return bundles


def _recover_capture_anchor(stored_rich: bytes, data: bytes) -> float:
    """The capture anchor the run used, recovered from its stored rich rows."""

    first = json.loads(stored_rich.split(b"\n", 1)[0])
    estimate = first["timestamp_s"] - first["elapsed_ns"] / 1_000_000_000.0
    candidates = [estimate]
    for direction in (math.inf, -math.inf):
        value = estimate
        for _ in range(4):
            value = math.nextafter(value, direction)
            candidates.append(value)
    head = data.split(b"\0", 2)
    probe = b"\0".join(head[:2])
    first_line = stored_rich.split(b"\n", 1)[0] + b"\n"
    for candidate in candidates:
        rows = decode_rich_telemetry(probe, timestamp_anchor_s=candidate)
        if rich_telemetry_jsonl_from_records(rows[:1]).encode() == first_line:
            return candidate
    raise AssertionError("stored rich idle rows do not fix a capture anchor")


class ArchivedIdleByteIdentityTests(unittest.TestCase):
    """Real archived bundles: the single decode reproduces the stored bytes."""

    def test_measure_idle_reproduces_stored_rich_rows_and_baseline(self) -> None:
        limit = int(os.environ.get("JOULEWISE_M4_ARCHIVE_LIMIT", "2"))
        bundles = _archived_single_attempt_bundles(limit)
        if not bundles:
            self.skipTest("archived real idle plists are not present on this machine")
        for bundle in bundles:
            with self.subTest(bundle=str(bundle)):
                data = (bundle / "raw" / "powermetrics_idle.plist").read_bytes()
                stored_rich = (bundle / RICH_IDLE_NAME).read_bytes()
                stored_baseline = json.loads((bundle / "metadata.json").read_bytes())[
                    "idle_baseline"
                ]
                anchor = _recover_capture_anchor(stored_rich, data)
                with tempfile.TemporaryDirectory() as tmp:
                    out = Path(tmp) / bundle.name
                    clock = FakeClock(start=anchor)
                    adapter = PowermetricsTelemetryAdapter(clock)
                    adapter._capability = AdapterResult(ok=True)
                    config = make_config()
                    context = make_context(out, config, clock)
                    with patch(
                        "joulewise.adapters.powermetrics.subprocess.run",
                        side_effect=bounded_capture_run(data, []),
                    ):
                        baseline = adapter.measure_idle(config, context)
                    self.assertEqual((out / RICH_IDLE_NAME).read_bytes(), stored_rich)
                    self.assertEqual(
                        (out / "raw" / "powermetrics_idle.plist").read_bytes(), data
                    )
                for key in (
                    "power_w_mean",
                    "power_w_stddev",
                    "duration_s",
                    "sample_count",
                    "gpu_idle_ratio_mean",
                    "gpu_idle_ratio_min",
                    "gpu_freq_mhz_mean",
                    "gpu_freq_hz_mean",
                    "idle_window_suspect",
                ):
                    self.assertEqual(getattr(baseline, key), stored_baseline[key], key)
                self.assertEqual(
                    adapter._pre_idle_records,
                    parse_powermetrics_records(data, timestamp_anchor_s=anchor),
                )


if __name__ == "__main__":
    unittest.main()
