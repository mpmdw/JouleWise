"""Controller lifecycle with a LABELLED stub ioreg runner and mock adapters.

No hardware is sampled. The shared battery reader authenticates the emitted
raw pair, independently of the writer's stored predicate.
"""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise import adapters, battery_float, controller
from joulewise.clock import FakeClock
from joulewise.schemas import FailureReason, RunStatus, TelemetryBackend
from tests import battery_float_fixture
from tests.test_controller import make_config


class RecordingTelemetry:
    """Mock telemetry with explicit sampler and anchor boundaries in the trace."""
    name = 'stub-telemetry'

    def __init__(self, inner, clock, trace, *, stop_error=False):
        self.inner, self.clock, self.trace = inner, clock, trace
        self.live = False
        self.stop_error = stop_error

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def start_sampling(self, config, context=None):
        self.trace.append(('sampler_start', self.clock.now()))
        self.live = True
        return self.inner.start_sampling(config, context)

    def stop_sampling(self, config, context=None):
        self.trace.append(('sampler_stop', self.clock.now()))
        if self.stop_error:
            raise RuntimeError('labelled sampler teardown failure')
        result = self.inner.stop_sampling(config, context)
        self.live = False
        return result

    def clock_alignments(self):
        if self.live:
            self.trace.append(('anchor', self.clock.now()))
        return []

    def measure_post_run_idle(self, config, baseline, context=None):
        self.trace.append(('sentinel_start', self.clock.now()))
        self.live = True
        self.clock.sleep(1)
        self.live = False
        self.trace.append(('sentinel_stop', self.clock.now()))
        return {'idle_drift': {'status': 'unknown', 'reason': 'labelled synthetic sentinel'}}


class BatteryControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runs = Path(self.tmp.name) / 'runs'
        self.trace = []
        self.clock = FakeClock(start=1700000000)
        self.telemetry = None
        self.raw = []

    def run_member(self, *, probe_error=None, failure=False, stop_error=False, mock=False, sentinel=True, write_error=False):
        config = make_config('battery-member')
        if not mock:
            config = replace(config, hardware_target=replace(config.hardware_target, telemetry_backend=TelemetryBackend.POWERMETRICS))
        config = replace(config, sampling=replace(config.sampling, power_hz=1000))
        case = self
        class StubRegistry:
            def resolve_runtime(inner, config, clock):
                runtime, err = adapters.resolve_runtime(make_config(config.run_id), clock)
                if failure:
                    runtime.run_workload = lambda *args: (_ for _ in ()).throw(RuntimeError('labelled workload failure'))
                return runtime, err
            def resolve_transport(inner, config):
                return adapters.resolve_transport(make_config(config.run_id))
            def resolve_telemetry(inner, config, clock):
                telemetry, err = adapters.resolve_telemetry(make_config(config.run_id), clock)
                if sentinel:
                    case.telemetry = RecordingTelemetry(telemetry, clock, case.trace, stop_error=stop_error)
                else:
                    # An adapter lacking the drift protocol still gets the end
                    # stage required by authenticate_bundle, marked unavailable.
                    case.telemetry = telemetry
                return case.telemetry, err
        def labelled_ioreg_stub(argv):
            self.assertEqual(tuple(argv), battery_float.IOREG_BATTERY_ARGV)
            self.assertFalse(getattr(self.telemetry, 'live', False), 'battery observation inside sampler lifetime')
            self.trace.append(('ioreg', self.clock.now()))
            self.clock.sleep(0.25)
            if probe_error is not None:
                raise probe_error
            raw = battery_float_fixture.fresh_ioreg(now_s=self.clock.now())
            self.raw.append(raw)
            return subprocess.CompletedProcess(list(argv), 0, raw, b'')
        begin = controller._Execution._begin_stage
        complete = controller._Execution._complete_stage
        def record_begin(execution, name):
            self.trace.append(('begin_' + name, self.clock.now()))
            return begin(execution, name)
        def record_complete(execution, name, metadata=None):
            self.trace.append(('end_' + name, self.clock.now()))
            return complete(execution, name, metadata)
        raw_writer = controller.RunBundleWriter.write_raw
        def write_raw(writer, name, data):
            if write_error and name.startswith('battery_float.'):
                raise OSError('labelled raw custody failure')
            return raw_writer(writer, name, data)
        with patch.object(controller._Execution, '_begin_stage', record_begin), \
             patch.object(controller._Execution, '_complete_stage', record_complete), \
             patch.object(controller.RunBundleWriter, 'write_raw', write_raw):
            path, summary = controller.run_benchmark(config, self.runs, self.clock, registry=StubRegistry(),
                environment_snapshot=None, battery_runner=labelled_ioreg_stub)
        metadata = json.loads((path / 'metadata.json').read_bytes())
        events = [json.loads(line) for line in (path / 'events.jsonl').read_text().splitlines()]
        return path, summary, metadata, events

    def test_stub_pair_surrounds_sampler_anchor_stamps_and_reader_accepts(self):
        path, summary, metadata, events = self.run_member()
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        probes = [index for index, (name, _) in enumerate(self.trace) if name == 'ioreg']
        first, last = probes
        inside = [index for index, (name, _) in enumerate(self.trace) if name in ('anchor', 'sampler_start', 'sampler_stop', 'sentinel_start', 'sentinel_stop')]
        self.assertTrue(inside)
        self.assertTrue(all(first < index < last for index in inside), self.trace)
        self.assertLess(first, next(i for i, row in enumerate(self.trace) if row[0] == 'begin_idle_baseline'))
        self.assertGreater(last, next(i for i, row in enumerate(self.trace) if row[0] == 'end_idle_drift_sentinel'))
        pair = metadata['battery_float']
        for phase, raw in zip(('pre', 'post'), self.raw):
            self.assertEqual(pair[phase]['phase'], 'bundle_' + phase)
            self.assertEqual(pair[phase]['session_id'], metadata['run_id'])
            self.assertEqual((path / pair[phase]['raw_path']).read_bytes(), raw)
            self.assertTrue(pair[phase]['passed'])
        start = next(row for row in events if row['event_type'] == 'stage_started' and row['phase'] == 'idle_baseline')['metadata']['monotonic_ns']
        end = next(row for row in events if row['event_type'] == 'stage_completed' and row['phase'] == 'idle_drift_sentinel')['metadata']['monotonic_ns']
        self.assertLessEqual(pair['pre']['monotonic_after_ns'], start)
        self.assertGreaterEqual(pair['post']['monotonic_before_ns'], end)
        markers = [row for row in events if row['event_type'] in ('sampling_started', 'sampling_stopped')]
        self.assertEqual(len(markers), 2)
        self.assertLess(pair['pre']['wall_time_s'], markers[0]['timestamp_s'])
        self.assertGreaterEqual(pair['post']['wall_time_s'], markers[1]['timestamp_s'])
        self.assertEqual(battery_float.authenticate_bundle(path).status, 'pass')

    def test_probe_exception_recorded_without_crashing_member(self):
        path, summary, metadata, _ = self.run_member(probe_error=OSError('labelled ioreg failure'))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        for record in metadata['battery_float'].values():
            self.assertTrue(record['probe_error'])
            self.assertFalse(record['passed'])
            self.assertIn('labelled ioreg failure', record['reasons'][0])
            self.assertEqual((path / record['raw_path']).read_bytes(), b'')
        self.assertEqual(battery_float.authenticate_bundle(path).status, 'battery_float_evidence_missing')

    def test_probe_timeout_is_recorded(self):
        _, summary, metadata, _ = self.run_member(probe_error=subprocess.TimeoutExpired(battery_float.IOREG_BATTERY_ARGV, 2))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertTrue(metadata['battery_float']['pre']['timed_out'])
        self.assertTrue(metadata['battery_float']['post']['timed_out'])

    def test_raw_write_failure_recorded_without_crashing_member(self):
        _, summary, metadata, _ = self.run_member(write_error=True)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        for record in metadata['battery_float'].values():
            self.assertTrue(record['probe_error'])
            self.assertIn('labelled raw custody failure', record['reasons'][-1])

    def test_failure_post_is_salvaged_after_sampler_stop(self):
        path, summary, metadata, _ = self.run_member(failure=True)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        probes = [i for i, row in enumerate(self.trace) if row[0] == 'ioreg']
        self.assertEqual(len(probes), 2)
        self.assertGreater(probes[-1], next(i for i, row in enumerate(self.trace) if row[0] == 'sampler_stop'))
        self.assertIsNotNone(metadata['battery_float']['post'])
        # Failed members have no completed sentinel; salvage must not invent it.
        self.assertEqual(battery_float.authenticate_bundle(path).status, 'battery_float_evidence_missing')

    def test_failed_teardown_never_observes_post_with_live_sampler(self):
        _, summary, metadata, _ = self.run_member(failure=True, stop_error=True)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(sum(row[0] == 'ioreg' for row in self.trace), 1)
        self.assertIsNone(metadata['battery_float']['post'])

    def test_adapter_without_sentinel_still_emits_readable_pair(self):
        path, summary, _, events = self.run_member(sentinel=False)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        end = next(row for row in events if row['event_type'] == 'stage_completed' and row['phase'] == 'idle_drift_sentinel')
        self.assertEqual(end['metadata']['status'], 'unavailable')
        self.assertEqual(battery_float.authenticate_bundle(path).status, 'pass')

    def test_mock_skips_ioreg(self):
        _, summary, metadata, _ = self.run_member(mock=True)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertFalse(any(row[0] == 'ioreg' for row in self.trace))
        self.assertEqual(metadata['battery_float'], {'pre': None, 'post': None, 'not_applicable': 'mock'})


if __name__ == '__main__':
    unittest.main()
