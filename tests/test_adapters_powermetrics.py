from __future__ import annotations

import plistlib
import tempfile
import unittest
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from joulewise.adapters import powermetrics
from joulewise.adapters.powermetrics import (
    RAW_SAMPLES_NAME,
    PowermetricsTelemetryAdapter,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import AdapterResult, RunContext
from joulewise.schemas import BenchmarkConfig


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "powermetrics_sample.plist"


def make_config() -> BenchmarkConfig:
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
            "sampling": {"power_hz": 10.0, "idle_seconds": 0.3},
        }
    )


class PowermetricsIncrementalSliceTests(unittest.TestCase):
    def test_large_stream_realized_cadence_avoids_full_reads_and_parses_in_slices(
        self,
    ) -> None:
        documents = [
            plistlib.loads(frame)
            for frame in FIXTURE.read_bytes().split(b"\0")
            if frame.strip()
        ]
        template = deepcopy(documents[0])
        template["test_padding"] = "x" * (64 * 1024)
        first = plistlib.dumps(template)
        rollover = deepcopy(template)
        rollover["timestamp"] = template["timestamp"] + timedelta(seconds=1)
        second = plistlib.dumps(rollover)
        initial_stream = b"\0".join([first, second, *([second] * 268)])
        self.assertGreater(len(initial_stream), 17_000_000)

        clock = FakeClock(start=100.0)
        operational_now = [0.0]
        support_active = [False]
        parse_delay_pending = [False]
        full_reads_during_support: list[float] = []
        parses_during_support: list[float] = []
        readiness_parse_sizes: list[int] = []
        processes = []

        def appended_frame(sequence: int) -> bytes:
            document = deepcopy(rollover)
            document["test_sequence"] = sequence
            return plistlib.dumps(document)

        class GrowingPopen:
            command: list[str] | None = None

            def __init__(self, command, **_kwargs):
                type(self).command = list(command)
                processes.append(self)
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(initial_stream)
                self.returncode = None
                self.next_endpoint_s = 0.12
                self.sequence = 0

            def append_through(self, endpoint_s: float) -> None:
                with self.path.open("ab", buffering=0) as handle:
                    while self.next_endpoint_s <= endpoint_s + 1e-12:
                        handle.write(b"\0" + appended_frame(self.sequence))
                        self.sequence += 1
                        self.next_endpoint_s += 0.12

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def kill(self):
                self.returncode = -9

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        def advance(seconds: float) -> None:
            operational_now[0] += seconds
            clock.sleep(seconds)
            processes[0].append_through(operational_now[0])

        class TrackingAdapter(PowermetricsTelemetryAdapter):
            def __init__(self) -> None:
                super().__init__(clock, privilege_prefix=())
                self.captured_slices: list[bytes] = []

            def _capture_idle_slice(self, *args, **kwargs):
                support_active[0] = True
                try:
                    result = super()._capture_idle_slice(*args, **kwargs)
                finally:
                    support_active[0] = False
                self.captured_slices.append(result[0])
                parse_delay_pending[0] = True
                return result

        original_read_bytes = Path.read_bytes
        original_parse = powermetrics._parse_powermetrics_records
        original_plist_loads = plistlib.loads
        phase = ["readiness"]

        def tracking_read_bytes(path: Path) -> bytes:
            if (
                processes
                and path == processes[0].path
                and support_active[0]
            ):
                full_reads_during_support.append(operational_now[0])
            return original_read_bytes(path)

        def tracking_parse(data: bytes, *args, **kwargs):
            if phase[0] == "readiness":
                readiness_parse_sizes.append(len(data))
            if support_active[0]:
                parses_during_support.append(operational_now[0])
            result = original_parse(data, *args, **kwargs)
            if parse_delay_pending[0]:
                parse_delay_pending[0] = False
                advance(0.65)
            return result

        def tracking_plist_loads(data: bytes, *args, **kwargs):
            if support_active[0]:
                parses_during_support.append(operational_now[0])
            return original_plist_loads(data, *args, **kwargs)

        adapter = TrackingAdapter()
        adapter._capability = AdapterResult(ok=True)
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=clock,
                run_id="cursor-regression",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch(
                    "joulewise.adapters.powermetrics.subprocess.Popen",
                    GrowingPopen,
                ),
                patch(
                    "joulewise.adapters.powermetrics.time.monotonic",
                    side_effect=lambda: operational_now[0],
                ),
                patch(
                    "joulewise.adapters.powermetrics.time.sleep",
                    side_effect=advance,
                ),
                patch.object(Path, "read_bytes", tracking_read_bytes),
                patch(
                    "joulewise.adapters.powermetrics._parse_powermetrics_records",
                    side_effect=tracking_parse,
                ),
                patch(
                    "joulewise.adapters.powermetrics.plistlib.loads",
                    side_effect=tracking_plist_loads,
                ),
            ):
                self.assertTrue(
                    adapter.begin_admission_window_sampling(config, context).ok
                )
                phase[0] = "capture"
                adapter.measure_idle(config, context)
                adapter.measure_idle(config, context)
                adapter.stop_sampling(config, context)

            self.assertEqual(len(processes), 1)
            command = GrowingPopen.command
            assert command is not None
            self.assertNotIn("-n", command)
            self.assertEqual(command[command.index("-i") + 1], "100")
            self.assertEqual(command[command.index("-b") + 1], "0")
            self.assertEqual(full_reads_during_support, [])
            self.assertEqual(parses_during_support, [])
            self.assertTrue(readiness_parse_sizes)
            self.assertLess(max(readiness_parse_sizes), len(initial_stream) // 100)

            stream_frames = [
                frame
                for frame in (root / "raw" / RAW_SAMPLES_NAME)
                .read_bytes()
                .split(b"\0")
                if frame
            ]
            self.assertEqual(len(adapter.captured_slices), 2)
            for logical_slice in adapter.captured_slices:
                slice_frames = logical_slice.split(b"\0")
                self.assertEqual(len(slice_frames), 3)
                self.assertTrue(
                    any(
                        stream_frames[index : index + len(slice_frames)]
                        == slice_frames
                        for index in range(
                            len(stream_frames) - len(slice_frames) + 1
                        )
                    )
                )


if __name__ == "__main__":
    unittest.main()
