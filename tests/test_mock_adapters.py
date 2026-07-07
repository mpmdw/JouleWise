import json
from unittest.mock import patch
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from typing import Any

from joulewise import __version__
from joulewise.adapters import (
    LocalTransport,
    MockRuntimeAdapter,
    MockTelemetryAdapter,
    resolve_runtime,
    resolve_telemetry,
    resolve_transport,
)
from joulewise.adapters.mock_telemetry import (
    IDLE_POWER_W,
    MEASURED_POWER_W,
    WARMUP_POWER_W,
)
from joulewise.clock import FakeClock, SystemClock
from joulewise.interfaces import (
    PowerSample,
    RuntimeAdapter,
    RuntimeEvent,
    TelemetryAdapter,
    TransportAdapter,
)
from joulewise.schemas import BenchmarkConfig, FailureReason, TelemetryBackend

EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}


def make_config(**overrides: Any) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "model": {"name": "mock-model"},
        "quantization": {"name": "none"},
        "hardware_target": {
            "id": "mock_target",
            "transport": "local",
            "runtime_backend": "mock",
            "telemetry_backend": "mock",
        },
        "workload_profile": {
            "name": "mock_smoke",
            "prompt_tokens": 32,
            "output_tokens": 8,
        },
        "sampling": {"power_hz": 2.0, "idle_seconds": 1.0},
    }
    for key, value in overrides.items():
        if isinstance(value, dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return BenchmarkConfig.from_mapping(data)


def serialize_events(events: list[RuntimeEvent]) -> str:
    return json.dumps([asdict(event) for event in events], sort_keys=True)


def serialize_samples(samples: list[PowerSample]) -> str:
    return json.dumps([asdict(sample) for sample in samples], sort_keys=True)


class ProtocolConformanceTests(unittest.TestCase):
    def test_mock_runtime_satisfies_protocol(self) -> None:
        self.assertIsInstance(MockRuntimeAdapter(FakeClock()), RuntimeAdapter)

    def test_mock_telemetry_satisfies_protocol(self) -> None:
        self.assertIsInstance(MockTelemetryAdapter(FakeClock()), TelemetryAdapter)

    def test_local_transport_satisfies_protocol(self) -> None:
        self.assertIsInstance(LocalTransport(), TransportAdapter)


class MockRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)
        self.runtime = MockRuntimeAdapter(self.clock)
        self.config = make_config()

    def test_prepare_reports_adapter_metadata(self) -> None:
        result = self.runtime.prepare(self.config)
        self.assertTrue(result.ok)
        self.assertEqual(
            result.metadata, {"adapter": "mock_runtime", "version": __version__}
        )

    def test_prepare_mock_unsupported_returns_did_not_fit(self) -> None:
        config = make_config(model={"name": "mock-unsupported"})
        result = self.runtime.prepare(config)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.DID_NOT_FIT)
        self.assertIn("mock-unsupported", result.message)

    def test_warmup_advances_clock(self) -> None:
        result = self.runtime.warmup(self.config)
        self.assertTrue(result.ok)
        self.assertAlmostEqual(self.clock.now(), 1000.05, places=9)

    def test_run_workload_timeline_and_counts(self) -> None:
        result = self.runtime.run_workload(self.config)
        self.assertEqual(result.token_count, 40)
        self.assertEqual(result.output_token_count, 8)

        events = result.events
        self.assertEqual(len(events), 12)  # 4 phase events + 8 token events
        self.assertEqual(
            [(event.event_type, event.phase) for event in events],
            [("phase_start", "prefill"), ("phase_end", "prefill"), ("phase_start", "decode")]
            + [("token", "decode")] * 8
            + [("phase_end", "decode")],
        )

        self.assertEqual(events[0].timestamp_s, 1000.0)
        self.assertAlmostEqual(events[1].timestamp_s, 1000.032, places=9)  # 32 x 1 ms
        self.assertEqual(events[2].timestamp_s, events[1].timestamp_s)
        token_events = [event for event in events if event.event_type == "token"]
        for index, event in enumerate(token_events):
            self.assertEqual(event.metadata, {"index": index})
            self.assertAlmostEqual(
                event.timestamp_s, 1000.032 + (index + 1) * 0.010, places=9
            )
        self.assertEqual(events[-1].timestamp_s, token_events[-1].timestamp_s)
        # run end: 1000 + 32 ms prefill + 8 x 10 ms decode
        self.assertAlmostEqual(self.clock.now(), 1000.112, places=9)

    def test_event_records_have_exactly_the_contract_keys(self) -> None:
        result = self.runtime.run_workload(self.config)
        for event in result.events:
            self.assertEqual(set(asdict(event)), EVENT_KEYS)

    def test_run_workload_output_artifacts(self) -> None:
        result = self.runtime.run_workload(self.config)
        self.assertEqual(
            set(result.output_artifacts), {"response.txt", "tokens.jsonl"}
        )
        response = result.output_artifacts["response.txt"]
        self.assertIn("mock-model", response)
        self.assertIn("prompt_tokens=32", response)
        self.assertIn("output_tokens=8", response)

        lines = result.output_artifacts["tokens.jsonl"].splitlines()
        self.assertEqual(len(lines), 8)
        token_events = [e for e in result.events if e.event_type == "token"]
        for index, line in enumerate(lines):
            record = json.loads(line)
            self.assertEqual(set(record), {"index", "timestamp_s"})
            self.assertEqual(record["index"], index)
            self.assertEqual(record["timestamp_s"], token_events[index].timestamp_s)

    def test_prompt_tokens_fall_back_to_prompt_text_word_count(self) -> None:
        config = make_config(
            workload_profile={
                "name": "text_only",
                "prompt_tokens": None,
                "output_tokens": None,
                "prompt_text": "five words in this prompt",
            }
        )
        result = self.runtime.run_workload(config)
        self.assertEqual(result.output_token_count, 8)  # default output tokens
        self.assertEqual(result.token_count, 5 + 8)

    def test_prompt_tokens_default_when_no_text_or_count(self) -> None:
        config = make_config(
            workload_profile={
                "name": "dataset_only",
                "prompt_tokens": None,
                "output_tokens": None,
                "dataset_ref": "mock-dataset",
            }
        )
        result = self.runtime.run_workload(config)
        self.assertEqual(result.token_count, 32 + 8)

    def test_cleanup_ok(self) -> None:
        self.assertTrue(self.runtime.cleanup(self.config).ok)


class MockTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)
        self.telemetry = MockTelemetryAdapter(self.clock)
        self.config = make_config()

    def test_power_constants(self) -> None:
        self.assertEqual(IDLE_POWER_W, 5.0)
        self.assertEqual(WARMUP_POWER_W, 6.0)
        self.assertEqual(MEASURED_POWER_W, 7.5)

    def test_device_metadata_declares_rail_manifest(self) -> None:
        self.assertEqual(
            self.telemetry.device_metadata(self.config),
            {"device": "mock_target", "telemetry": "mock", "rail_manifest": ["mock"]},
        )

    def test_measure_idle_exact_constants_and_clock_advance(self) -> None:
        baseline = self.telemetry.measure_idle(self.config)
        self.assertEqual(self.clock.now(), 1001.0)  # advanced by idle_seconds
        self.assertEqual(baseline.power_w_mean, 5.0)
        self.assertEqual(baseline.power_w_stddev, 0.0)
        self.assertEqual(baseline.duration_s, 1.0)
        self.assertEqual(baseline.sample_count, 2)  # max(2, int(1.0 * 2.0))
        self.assertEqual(baseline.telemetry_backend, TelemetryBackend.MOCK)

    def test_measure_idle_sample_count_scales_with_window(self) -> None:
        config = make_config(sampling={"idle_seconds": 30.0, "power_hz": 2.0})
        baseline = self.telemetry.measure_idle(config)
        self.assertEqual(baseline.sample_count, 60)
        self.assertEqual(baseline.duration_s, 30.0)

    def test_measure_idle_sample_count_floor_is_two(self) -> None:
        config = make_config(sampling={"idle_seconds": 0.25, "power_hz": 2.0})
        baseline = self.telemetry.measure_idle(config)
        self.assertEqual(baseline.sample_count, 2)

    def test_stop_sampling_closed_form_short_window(self) -> None:
        # 0.112 s at 2.0 Hz: the nominal centered grid has fewer than two
        # samples, so the mock emits two evenly spaced interior samples.
        self.assertTrue(self.telemetry.start_sampling(self.config).ok)
        self.clock.sleep(0.112)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(len(samples), 2)
        self.assertAlmostEqual(samples[0].timestamp_s, 1000.0 + 0.112 / 3.0)
        self.assertAlmostEqual(samples[1].timestamp_s, 1000.0 + 2.0 * 0.112 / 3.0)
        for sample in samples:
            self.assertEqual(sample.power_w, 7.5)
            self.assertEqual(sample.source, "mock")
            self.assertEqual(sample.rail, "mock")

    def test_stop_sampling_centered_grid_samples(self) -> None:
        # 1.0 s at 2.0 Hz: centered nominal-period samples, no boundaries.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.75]
        )
        self.assertEqual({sample.power_w for sample in samples}, {7.5})

    def test_system_clock_short_window_samples_land_inside_marker_window(self) -> None:
        clock = SystemClock()
        telemetry = MockTelemetryAdapter(clock)
        config = make_config()

        self.assertTrue(telemetry.start_sampling(config).ok)
        marker_start_s = clock.now()
        clock.sleep(0.075)
        marker_stop_s = clock.now()
        samples = telemetry.stop_sampling(config)

        # The reducer's contract (joulewise/reduce.py _in_window_sample_count)
        # is >= 2 samples inclusively inside the marker window. Deliberately do
        # NOT assert that every sample is inside the markers: under sleep
        # overshoot the centered-grid path can legitimately stamp a sample in
        # the microsecond stop-latency gap between the marker read and the
        # adapter's own end read, which the reducer simply ignores.
        in_marker_window = [
            sample
            for sample in samples
            if marker_start_s <= sample.timestamp_s <= marker_stop_s
        ]
        self.assertGreaterEqual(len(in_marker_window), 2)

    def test_stop_sampling_one_grid_candidate_falls_back_to_thirds(self) -> None:
        # 0.5 s at 2.0 Hz: the centered grid has exactly one candidate
        # (1000.25; the next, 1000.75, is not < end), so the two-sample
        # thirds fallback applies. Same float expressions as the adapter.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.5)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples],
            [1000.0 + 0.5 / 3.0, 1000.0 + 2.0 * 0.5 / 3.0],
        )
        self.assertEqual({sample.power_w for sample in samples}, {7.5})

    def test_stop_sampling_grid_end_boundary_excluded(self) -> None:
        # 0.75 s at 2.0 Hz: grid candidates are 1000.25 and 1000.75, but the
        # loop condition is strictly < end, so 1000.75 (== end) is excluded,
        # leaving one candidate and forcing the thirds fallback. 0.75/3 and
        # 2*0.75/3 are exact in binary floats: [1000.25, 1000.5].
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.75)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.5]
        )

    def test_stop_sampling_two_grid_samples_no_fallback(self) -> None:
        # 0.8 s at 2.0 Hz: grid candidates 1000.25 and 1000.75 are both
        # strictly < end, so the grid path (not the fallback) is used. This
        # pins the fallback/grid boundary just above 1.5/power_hz.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(0.8)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1000.25, 1000.75]
        )

    def test_stop_sampling_zero_length_span_single_sample_degenerate(self) -> None:
        # start == end (no clock advance): degenerate single sample at end.
        # The reducer's zero-length-window path never reaches the >= 2 guard.
        self.telemetry.start_sampling(self.config)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual([sample.timestamp_s for sample in samples], [1000.0])
        self.assertEqual(samples[0].power_w, 7.5)

    def test_stop_sampling_interior_invariants_across_durations_and_hz(self) -> None:
        # The P2-008 guarantee, pinned as an invariant: for ANY nonzero span,
        # >= 2 samples, all strictly inside (start, end), strictly increasing,
        # constant 7.5 W, and no consecutive gap reaching the reducer's
        # dropped-sample threshold of 2x the nominal period (reduce.py
        # _dropped_samples).
        cases = [
            (0.1, 0.5),  # fallback: window far below one nominal period
            (0.3, 2.0),  # fallback: the original 2G live-smoke shape
            (1.4, 2.0),  # grid: three samples (offsets 0.25, 0.75, 1.25)
            (100.0, 2.0),  # grid: long window, many samples
            (0.5, 1000.0),  # grid: high rate, 500 samples
        ]
        for duration_s, power_hz in cases:
            with self.subTest(duration_s=duration_s, power_hz=power_hz):
                clock = FakeClock(start=1000.0)
                telemetry = MockTelemetryAdapter(clock)
                config = make_config(sampling={"power_hz": power_hz})
                telemetry.start_sampling(config)
                clock.sleep(duration_s)
                end = clock.now()
                samples = telemetry.stop_sampling(config)
                timestamps = [sample.timestamp_s for sample in samples]
                self.assertGreaterEqual(len(timestamps), 2)
                self.assertTrue(all(1000.0 < t < end for t in timestamps))
                self.assertEqual(timestamps, sorted(set(timestamps)))
                self.assertEqual({sample.power_w for sample in samples}, {7.5})
                nominal_period_s = 1.0 / power_hz
                for left, right in zip(timestamps, timestamps[1:]):
                    self.assertLess(right - left, 2.0 * nominal_period_s)

    def test_stop_sampling_without_start_returns_empty(self) -> None:
        self.assertEqual(self.telemetry.stop_sampling(self.config), [])

    def test_stop_sampling_twice_second_call_returns_empty(self) -> None:
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        self.assertEqual(len(self.telemetry.stop_sampling(self.config)), 2)
        self.assertEqual(self.telemetry.stop_sampling(self.config), [])

    def test_restarted_sampling_stamps_from_new_span(self) -> None:
        # A second start/stop cycle stamps relative to its own span, and a
        # preceding measure_idle (which advances the clock) shifts the span.
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        self.telemetry.stop_sampling(self.config)

        self.telemetry.measure_idle(self.config)  # advances clock by 1.0 s
        self.telemetry.start_sampling(self.config)
        self.clock.sleep(1.0)
        samples = self.telemetry.stop_sampling(self.config)
        self.assertEqual(
            [sample.timestamp_s for sample in samples], [1002.25, 1002.75]
        )

    def test_start_sampling_telemetry_denied(self) -> None:
        config = make_config(hardware_target={"notes": "telemetry-denied"})
        result = self.telemetry.start_sampling(config)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.PERMISSION_DENIED)
        self.assertIn("telemetry-denied", result.message)

    def test_thermal_state(self) -> None:
        self.clock.sleep(5.0)
        state = self.telemetry.thermal_state(self.config)
        self.assertEqual(state.timestamp_s, 1005.0)
        self.assertEqual(state.temperature_c, 42.0)
        self.assertEqual(state.thermal_pressure, "nominal")


class DeterminismTests(unittest.TestCase):
    """Identical config + clock seed => byte-identical artifacts (D-019)."""

    @staticmethod
    def _complete_run(config: BenchmarkConfig) -> tuple[str, str, dict[str, str]]:
        clock = FakeClock(start=1000.0)
        runtime, runtime_failure = resolve_runtime(config, clock)
        telemetry, telemetry_failure = resolve_telemetry(config, clock)
        assert runtime_failure is None and telemetry_failure is None

        assert runtime.prepare(config).ok
        assert runtime.warmup(config).ok
        telemetry.measure_idle(config)
        assert telemetry.start_sampling(config).ok
        result = runtime.run_workload(config)
        samples = telemetry.stop_sampling(config)
        assert runtime.cleanup(config).ok
        return (
            serialize_events(result.events),
            serialize_samples(samples),
            result.output_artifacts,
        )

    def test_two_runs_are_byte_identical(self) -> None:
        first = self._complete_run(make_config())
        second = self._complete_run(make_config())
        self.assertEqual(first[0], second[0])  # events.jsonl content
        self.assertEqual(first[1], second[1])  # power samples
        self.assertEqual(first[2], second[2])  # response.txt + tokens.jsonl


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock(start=1000.0)

    def assert_exactly_one(self, pair: tuple[object, object]) -> None:
        self.assertEqual(sum(1 for item in pair if item is not None), 1)

    def test_resolves_mock_runtime(self) -> None:
        adapter, failure = resolve_runtime(make_config(), self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, RuntimeAdapter)
        self.assertEqual(adapter.name, "mock")

    def test_resolves_mock_telemetry(self) -> None:
        adapter, failure = resolve_telemetry(make_config(), self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TelemetryAdapter)
        self.assertEqual(adapter.name, "mock")

    def test_resolves_powermetrics_telemetry_adapter(self) -> None:
        config = make_config(hardware_target={"telemetry_backend": "powermetrics"})
        adapter, failure = resolve_telemetry(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TelemetryAdapter)
        self.assertEqual(adapter.name, "powermetrics")

    def test_powermetrics_import_failure_is_telemetry_unavailable(self) -> None:
        config = make_config(hardware_target={"telemetry_backend": "powermetrics"})
        with patch(
            "joulewise.adapters.importlib.import_module",
            side_effect=ImportError("injected missing adapter"),
        ):
            adapter, failure = resolve_telemetry(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsNone(adapter)
        self.assertFalse(failure.ok)
        self.assertEqual(failure.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)
        self.assertIn("powermetrics", failure.message)

    def test_resolves_local_transport(self) -> None:
        adapter, failure = resolve_transport(make_config())
        self.assert_exactly_one((adapter, failure))
        self.assertIsInstance(adapter, TransportAdapter)
        self.assertEqual(adapter.name, "local")

    def test_mlx_runtime_failure_names_backend_and_mac_extra(self) -> None:
        config = make_config(hardware_target={"runtime_backend": "mlx"})
        with patch(
            "joulewise.adapters.importlib.import_module",
            side_effect=ImportError("injected missing adapter"),
        ):
            adapter, failure = resolve_runtime(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertIsNone(adapter)
        self.assertFalse(failure.ok)
        self.assertEqual(failure.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertIn("mlx", failure.message)
        self.assertIn("[mac]", failure.message)

    def test_resolves_mlx_runtime_adapter_without_importing_mlx_lm(self) -> None:
        config = make_config(hardware_target={"runtime_backend": "mlx"})
        adapter, failure = resolve_runtime(config, self.clock)
        self.assert_exactly_one((adapter, failure))
        self.assertEqual(adapter.name, "mlx")

    def test_unimplemented_runtimes_fail_structurally(self) -> None:
        for backend in ("vllm", "llama_cpp", "hailo"):
            with self.subTest(backend=backend):
                config = make_config(hardware_target={"runtime_backend": backend})
                adapter, failure = resolve_runtime(config, self.clock)
                self.assert_exactly_one((adapter, failure))
                self.assertIsNone(adapter)
                self.assertEqual(
                    failure.failure_reason, FailureReason.RUNTIME_UNAVAILABLE
                )
                self.assertIn(backend, failure.message)

    def test_unimplemented_telemetry_fails_structurally(self) -> None:
        for backend in ("nvidia_smi", "jetson_rails", "wall_meter"):
            with self.subTest(backend=backend):
                config = make_config(hardware_target={"telemetry_backend": backend})
                adapter, failure = resolve_telemetry(config, self.clock)
                self.assert_exactly_one((adapter, failure))
                self.assertIsNone(adapter)
                self.assertEqual(
                    failure.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE
                )
                self.assertIn(backend, failure.message)

    def test_ssh_transport_fails_structurally(self) -> None:
        config = make_config(
            hardware_target={"transport": "ssh", "host": "node.example"}
        )
        adapter, failure = resolve_transport(config)
        self.assert_exactly_one((adapter, failure))
        self.assertIsNone(adapter)
        self.assertEqual(failure.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        self.assertIn("ssh", failure.message)


class LocalTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = LocalTransport()
        self.config = make_config()

    def test_connection_metadata(self) -> None:
        self.assertEqual(
            self.transport.connection_metadata(self.config),
            {"transport": "local", "host": "localhost"},
        )

    def test_run_command_success(self) -> None:
        result = self.transport.run_command(self.config, [sys.executable, "-c", "pass"])
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata, {"returncode": 0})

    def test_run_command_nonzero_exit_reports_stderr_tail(self) -> None:
        result = self.transport.run_command(
            self.config,
            [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"],
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("boom", result.message)

    def test_run_command_missing_binary_is_transport_unavailable(self) -> None:
        result = self.transport.run_command(
            self.config, ["/nonexistent/joulewise-no-such-binary"]
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)

    def test_collect_artifact_copies_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            destination = Path(tmp) / "collected.txt"
            source.write_text("artifact body")
            result = self.transport.collect_artifact(
                self.config, str(source), str(destination)
            )
            self.assertTrue(result.ok)
            self.assertEqual(destination.read_text(), "artifact body")

    def test_collect_artifact_missing_source_is_transport_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.transport.collect_artifact(
                self.config,
                str(Path(tmp) / "missing.txt"),
                str(Path(tmp) / "out.txt"),
            )
            self.assertFalse(result.ok)
            self.assertEqual(
                result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE
            )


if __name__ == "__main__":
    unittest.main()
