"""Synthetic boundary receipts; never discover or read measurement records."""
from contextlib import redirect_stderr, redirect_stdout
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import timing_receipts as timing
from joulewise.clock import FakeClock


def writer(rows, clock, **identity):
    return timing.Writer(rows.append, producer="synthetic", plan_id="W1", attempt=1,
        boot_session_id="synthetic-boot", stamp=lambda: timing.clock_stamp(clock),
        wall_resolution_s=0, monotonic_resolution_s=0, **identity)


def pinned_reader():
    # Read CODE only from the shared Git object store. No records, checkout,
    # network, external paths or imports of measurement/capture modules.
    name = "_timing_receipts_pinned_reader"
    if name not in sys.modules:
        source = subprocess.run(["git", "show", "dc684b308:joulewise/align/window_timing.py"],
            cwd=Path(__file__).resolve().parents[2], check=True, capture_output=True,
            env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                 "GIT_NO_LAZY_FETCH": "1"}).stdout
        module = ModuleType(name)
        sys.modules[name] = module
        exec(compile(source, "<pinned timing reader code>", "exec"), module.__dict__)
    return sys.modules[name]


class BoundaryTests(unittest.TestCase):
    def test_complete_nested_turnaround_parses_in_pinned_reader(self):
        rows, clock = [], FakeClock(100)
        with timing.bind(writer(rows, clock)):
            with timing.span("arm", "admission"):
                clock.sleep(2)
                with timing.span("dwell", "clean_dwell"):
                    clock.sleep(600)
                clock.sleep(1)
            for phase, activity, seconds in (("gates", "guard_wait", 2),
                    ("idle", "cooldown", 30), ("finalize", "finalize", 3)):
                with timing.span(phase, activity):
                    clock.sleep(seconds)
            with timing.span("offload", "harvest_handoff"):
                clock.sleep(4)
                with timing.span("offload", "push"):
                    clock.sleep(5)
        required = {"schema", "event", "phase", "activity", "sequence", "span_id", "parent_span_id",
                    "producer", "producer_id", "plan_id", "member", "stage", "attempt",
                    "epoch_ns", "monotonic_before_ns", "monotonic_after_ns", "wall_resolution_s",
                    "monotonic_resolution_s", "clock_domain", "boot_session_id"}
        self.assertLess(len(rows), 30)
        for row in rows:
            self.assertTrue(required <= row.keys())
            self.assertEqual(json.loads(json.dumps(row, allow_nan=False)), row)
            self.assertLessEqual(row["monotonic_before_ns"], row["monotonic_after_ns"])
        documents, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        reader = pinned_reader()
        raw_reader = reader._Reader(lambda _: b"")
        for document in documents:
            self.assertIsNotNone(raw_reader.timed(document, "synthetic_pair"))
        self.assertEqual(raw_reader.warnings, [])
        disjoint, warnings = timing.reader_projection(documents)
        self.assertEqual(warnings, [])
        blobs = {f"timing/{i}.json": json.dumps(row).encode() for i, row in enumerate(disjoint)}
        report = reader.read_window(blobs.__getitem__, spans=[(row['phase'], path)
                                   for path, row in zip(blobs, disjoint)])
        self.assertEqual(report['warnings'], [])
        self.assertEqual(report['phase_ns']['unattributed'], 0)
        self.assertEqual(report['wall_ns'], 647_000_000_000)
        self.assertEqual(sum(report['phase_ns'].values()), report['wall_ns'])
        self.assertEqual(report['phase_ns']['arm'], 3_000_000_000)
        self.assertEqual(report['phase_ns']['dwell'], 600_000_000_000)
        self.assertTrue(all(a['end_ns'] == b['start_ns'] for a, b in zip(report['ledger'], report['ledger'][1:])))

    def test_missing_invalid_and_cross_boot_pairs_stay_unmeasured(self):
        rows, clock = [], FakeClock()
        with timing.bind(writer(rows, clock)), timing.span("arm", "arm"):
            clock.sleep(1)
        for mutate in (lambda r: r.pop(),
                       lambda r: r[1].update(boot_session_id="reboot"),
                       lambda r: r[1].update(clock_domain="other"),
                       lambda r: r[1].update(monotonic_after_ns=False),
                       lambda r: r.insert(1, dict(r[0]))):
            broken = deepcopy(rows)
            mutate(broken)
            documents, warnings = timing.project(broken)
            self.assertEqual(documents, [], broken)
            self.assertTrue(warnings, broken)

    def test_failures_and_retries_retain_status_identity_and_requested_delay(self):
        rows, clock = [], FakeClock()
        with timing.bind(writer(rows, clock)):
            for error, status in ((TimeoutError(), "timeout"), (KeyboardInterrupt(), "interrupted"),
                                  (ValueError(), "error")):
                with self.assertRaises(type(error)):
                    with timing.span("gates", "wait", requested_s=600):
                        clock.sleep(1)
                        raise error
                self.assertEqual(rows[-1]['status'], status)
            with timing.span("gates", "wait", requested_s=600):
                clock.sleep(2)
        docs, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        self.assertEqual(len({r['start_boundary']['span_id'] for r in docs}), 4)
        self.assertEqual(sum(d['ended_ns'] - d['started_ns'] for d in docs), 5_000_000_000)
        self.assertEqual([r['requested_s'] for r in rows if r['event'] == 'start'], [600] * 4)

    def test_unrelated_overlap_is_not_filled_as_known_time(self):
        rows, clock = [], FakeClock()
        for _ in range(2):
            clock._now = 0
            with timing.bind(writer(rows, clock)), timing.span("arm", "arm"):
                clock.sleep(1)
        # Separate producers, even if their clocks/times happen to agree.
        for row in rows[2:]:
            row['producer_id'] += '-other'
            row['span_id'] += '-other'
        docs, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        projection, warnings = timing.reader_projection(docs)
        self.assertEqual(projection[0]['phase'], 'unattributed')
        self.assertTrue(warnings)

    def test_emission_failure_is_explicit_and_preserves_original_exception(self):
        clock = FakeClock()
        sink = writer([], clock)
        sink.append = lambda _: (_ for _ in ()).throw(OSError("synthetic disk error"))
        stderr = io.StringIO()
        with redirect_stderr(stderr), timing.bind(sink), self.assertRaisesRegex(ValueError, 'operation'):
            with timing.span("arm", "arm"):
                raise ValueError("operation")
        self.assertTrue(sink.failed)
        self.assertIn("timing receipt missing", stderr.getvalue())

    def test_existing_worker_inherits_receipts_without_unrelated_observers(self):
        rows, clock = [], FakeClock()
        unrelated = ContextVar('synthetic_unrelated_observer', default=False)
        observed = []
        def child():
            observed.append(unrelated.get())
            with timing.span('dwell', 'worker_dwell'):
                clock.sleep(1)
        with timing.bind(writer(rows, clock)), timing.span('arm', 'dispatch'):
            token = unrelated.set(True)
            try:
                thread = threading.Thread(target=timing.worker_target(child))
                thread.start()
                thread.join()
            finally:
                unrelated.reset(token)
        docs, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        self.assertEqual(observed, [False])
        parent = next(d for d in docs if d['activity'] == 'dispatch')
        child_span = next(d for d in docs if d['activity'] == 'worker_dwell')
        self.assertEqual(child_span['start_boundary']['parent_span_id'], parent['start_boundary']['span_id'])

    def test_measured_marker_uses_existing_bundle_handle_without_open_flush_or_fsync(self):
        from joulewise.bundle import RunBundleWriter
        from tests.test_bundle import load_example_config
        with tempfile.TemporaryDirectory() as tmp:
            config = load_example_config(run_id="synthetic")
            config = replace(config, workload_profile=replace(config.workload_profile, name='align_episode'))
            bundle = RunBundleWriter.create(Path(tmp), config, FakeClock())
            self.addCleanup(bundle._event_stream.close)
            # The spy delegates writes but fails on either flush or opening a
            # second file. No sync/thread/process is permitted by the marker.
            stream = bundle._event_stream
            spy = SimpleNamespace(write=stream.write,
                                  flush=lambda: self.fail('marker flushed during measurement'))
            bundle._event_stream = spy
            with patch('os.fsync', side_effect=AssertionError('marker fsync')), \
                 patch.object(Path, 'open', side_effect=AssertionError('marker opened a file')), \
                 patch('threading.Thread.start', side_effect=AssertionError('marker thread')), \
                 patch('subprocess.Popen', side_effect=AssertionError('marker subprocess')), \
                 timing.bind(bundle.timing), timing.span('gates', 'measured_boundary'):
                pass
            bundle._event_stream = stream
            stream.flush()  # existing owner's later stage boundary
            rows = [json.loads(line) for line in (bundle.path / 'events.jsonl').read_text().splitlines()]
            docs, warnings = timing.project(rows)
            self.assertEqual(warnings, [])
            self.assertEqual(len(docs), 1)


class ProducerTests(unittest.TestCase):
    def test_failed_push_then_retry_and_failed_finalize_keep_terminal_receipts_local(self):
        from scripts import run_night as driver
        rows, clock = [], FakeClock()
        plan = SimpleNamespace(plan_id='W1', receipt_class='DIAGNOSTIC_NO_PACK')
        pushes = []

        def run(argv, **kwargs):
            clock.sleep(1)
            if 'push' in argv:
                pushes.append(argv)
                if len(pushes) == 1:
                    raise subprocess.CalledProcessError(1, argv)
            return SimpleNamespace(stdout='synthetic-origin', returncode=0)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            night = root / 'night'
            night.mkdir()
            (root / 'results-clone').mkdir()
            with timing.bind(writer(rows, clock)), \
                 patch.object(driver.t0_rehearsal, 'observed_run', side_effect=run), \
                 patch.object(driver, '_artifact_list', return_value=[]), \
                 patch.object(driver, '_append_log'):
                self.assertIn('durable record failed', driver._durable_record(root, night, plan))
                self.assertIsNone(driver._durable_record(root, night, plan))
                with patch.object(driver, '_write_json', side_effect=OSError('synthetic write error')):
                    with self.assertRaises(OSError):
                        driver._write_result(root, night, plan, 'GO', 0, None, 0, 0, 'a'*64, 0)
            docs, warnings = timing.project(rows)
            self.assertEqual(warnings, [])
            push = [d for d in docs if d['activity'] == 'push']
            self.assertEqual([d['end_boundary']['status'] for d in push], ['error', 'complete'])
            self.assertEqual(push[0]['end_boundary']['rc'], 1)
            self.assertNotEqual(push[0]['start_boundary']['span_id'], push[1]['start_boundary']['span_id'])
            self.assertEqual([d['end_boundary']['status'] for d in docs if d['activity'] == 'night_result'], ['error'])
            self.assertEqual(len(pushes), 2)  # no recursive publish of completion
            self.assertFalse((root / 'results-clone/docs/process_traces/night-results/W1/chain-stages.jsonl').exists())

    def test_off_settle_counts_only_actual_residual_sleep_after_overlapping_dwell(self):
        from scripts import run_night as driver
        for dwell_s, expected_sleeps in ((450, [150]), (650, [])):
            rows, clock, sleeps = [], FakeClock(), []
            off = dict(epoch_s=100, monotonic_s=0, plan_id='W1', window_id='W1')
            plan = SimpleNamespace(plan_id='W1', receipt_class='DIAGNOSTIC_NO_PACK')

            def dwell():
                with timing.span('dwell', 'overlapping_dwell'):
                    clock.sleep(dwell_s)

            def sleep(seconds):
                sleeps.append(seconds)
                clock.sleep(seconds)

            with tempfile.TemporaryDirectory() as tmp, timing.bind(writer(rows, clock)), \
                 patch.object(driver.network_time_off, 'set_network_time_off', return_value=off), \
                 patch.object(driver.network_time_off, 'read_receipt', return_value=off), \
                 patch.object(driver.network_time_off, '_clock', side_effect=lambda: dict(epoch_s=100+clock.now(), monotonic_s=clock.now())), \
                 patch.object(driver.network_time_off, 'boot_id', return_value='synthetic-boot'), \
                 patch.object(driver.network_time_off, 'seconds_since_receipt'), \
                 patch.object(driver.time, 'sleep', side_effect=sleep):
                driver._admit_network_time_off(plan, Path(tmp), during_settle=dwell)
            self.assertEqual(sleeps, expected_sleeps)
            docs, warnings = timing.project(rows)
            self.assertEqual(warnings, [])
            self.assertEqual([d['start_boundary']['requested_s'] for d in docs
                              if d['activity'] == 'network_time_off_sleep'], expected_sleeps)

    def test_g0_timeout_and_fault_are_closed_without_changing_gate_record(self):
        from tests.align.test_thermal_gate import session, policy
        obj, clock = session(config=policy(g0_cap_s=600))
        self.addCleanup(obj.close)
        obj.reader._transport.values = lambda _: (45, 40)
        rows = []
        with timing.bind(writer(rows, clock)):
            gate = obj.wait('G0')
        self.assertEqual(gate['outcome'], 'timeout')
        self.assertEqual(rows[-1]['status'], 'timeout')
        self.assertEqual(timing.project(rows)[1], [])
        obj._collector_fault = lambda: 'synthetic collector failure'
        with timing.bind(writer(rows, clock)), self.assertRaises(Exception):
            obj.wait('G0')
        self.assertEqual(rows[-1]['status'], 'error')

    def test_hazard_arm_go_and_refusal_keep_the_original_record(self):
        from tests.hazards.test_arm import Rig
        from joulewise.hazards import arm, instrument
        for refused in (False, True):
            with self.subTest(refused=refused), tempfile.TemporaryDirectory() as tmp:
                rig = Rig(Path(tmp))
                if refused:
                    rig.census = (0, b'synthetic agent')
                rows = []
                clock = FakeClock()
                stamp = rig.clocks.stamp()
                capture = instrument.Measurement('instrument', 'instant', dict(
                    returncode=0, count_expected=300, frames=300, elapsed_s=30,
                    median_ms=100, max_ms=100, group_gone=True), (), stamp, stamp)
                # The sandbox cannot enumerate process groups (sysmond is
                # unavailable). This synthetic receipt test supplies the
                # cadence probe at its existing hardware boundary.
                with timing.bind(writer(rows, clock)), patch.object(arm.instrument, 'measure', return_value=capture):
                    result = rig.run()
                self.assertEqual(result.go, not refused, result.reasons)
                self.assertEqual(rows[-1]['status'], 'refused' if refused else 'complete')
                docs, warnings = timing.project(rows)
                self.assertEqual(warnings, [])
                self.assertEqual([d['activity'] for d in docs].count('hazard_clean_dwell'), int(not refused))

    def test_watchdog_reason_change_and_release_reuse_transition_sync(self):
        from scripts import magistrate_watchdog as wd
        import datetime
        with tempfile.TemporaryDirectory() as tmp:
            storage, state = wd.Storage(Path(tmp)), wd.initial_state()
            now = datetime.datetime(2026, 11, 8, tzinfo=datetime.timezone.utc)
            with patch('os.fsync') as fsync:
                wd.transition(storage, state, 'FENCED', 'first', now)
                self.assertEqual(fsync.call_count, 1)
                wd.transition(storage, state, 'FENCED', 'changed reason', now)
                wd.transition(storage, state, 'FENCED', 'changed reason', now)
                self.assertEqual(fsync.call_count, 1)  # reason-only boundaries add no fsync
                wd.transition(storage, state, 'LAUNCHING', 'released', now)
                self.assertEqual(fsync.call_count, 2)
            rows = [json.loads(line) for line in (Path(tmp) / 'events.jsonl').read_text().splitlines()]
            docs, warnings = timing.project(rows)
            self.assertEqual(warnings, [])
            self.assertEqual(len(docs), 2)
            self.assertEqual([d['start_boundary']['reason'] for d in docs], ['first', 'changed reason'])

    def test_watchdog_reboot_leaves_the_old_hold_open(self):
        from scripts import magistrate_watchdog as wd
        import datetime
        with tempfile.TemporaryDirectory() as tmp:
            storage, state = wd.Storage(Path(tmp)), wd.initial_state()
            now = datetime.datetime(2026, 11, 8, tzinfo=datetime.timezone.utc)
            state['backoff_boot_id'] = 'old-boot'
            wd.transition(storage, state, 'FENCED', 'same reason', now)
            state['backoff_boot_id'] = 'new-boot'
            wd.transition(storage, state, 'FENCED', 'same reason', now)
            wd.transition(storage, state, 'LAUNCHING', 'released', now)
            rows = [json.loads(line) for line in (Path(tmp) / 'events.jsonl').read_text().splitlines()]
            docs, warnings = timing.project(rows)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['start_boundary']['boot_session_id'], 'new-boot')
            self.assertTrue(any('open span' in warning for warning in warnings))


class CaptureEqualityTests(unittest.TestCase):
    def test_synthetic_capture_bytes_equal_with_and_without_markers(self):
        from scripts import align_v4_w1_synthetic as dry
        full = os.environ.get('JW_WP22_FULL') == '1'
        args = SimpleNamespace(variant='kit', inject='all', leak=0.004,
                               members='all' if full else '5,6')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'synthetic'
            root.mkdir()
            with redirect_stdout(io.StringIO()), patch.object(timing.Writer, 'emit', return_value=None):
                dry.collect(args, root)
            baseline = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            shutil.rmtree(root)  # only this test's synthetic TemporaryDirectory
            root.mkdir()
            with redirect_stdout(io.StringIO()):
                dry.collect(args, root)
            marked = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(baseline.keys(), marked.keys())
            marker_count = 0
            for path in baseline:
                raw = marked[path]
                if path.name == 'events.jsonl':
                    lines = raw.splitlines(keepends=True)
                    marker_count += sum(json.loads(line).get('event_type') == 'timing_boundary' for line in lines)
                    raw = b''.join(line for line in lines if json.loads(line).get('event_type') != 'timing_boundary')
                self.assertEqual(baseline[path], raw, str(path))
            self.assertGreater(marker_count, 0)
            self.assertLess(marker_count, 100)  # boundaries only, never sample rate


if __name__ == '__main__':
    unittest.main()
