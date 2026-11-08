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

    def test_measured_marker_only_appends_to_the_controller_memory_buffer(self):
        from joulewise.controller import _Execution
        execution = _Execution.__new__(_Execution)
        execution._events = []
        clock = FakeClock(100.123456789)
        sink = writer([], clock)
        sink.append = execution._buffer_timing_boundary
        with patch('os.fsync', side_effect=AssertionError('marker fsync')), \
             patch.object(Path, 'open', side_effect=AssertionError('marker opened a file')), \
             patch('threading.Thread.start', side_effect=AssertionError('marker thread')), \
             patch('subprocess.Popen', side_effect=AssertionError('marker subprocess')), \
             timing.bind(sink), timing.span('gates', 'measured_boundary'):
            clock.sleep(1)
        rows = [dict(metadata=event.metadata) for event in execution._events]
        docs, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        self.assertEqual(len(docs), 1)
        self.assertEqual(execution._events[0].timestamp_s, 100.123456789)


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

    def test_driver_log_appends_preserve_interleaved_owner_messages_and_parse_offline(self):
        from scripts import run_night as driver
        from joulewise.align.window_timing import read_window
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            night = root/'night'
            night.mkdir()
            plan = SimpleNamespace(plan_id='W1', hazard_window=None)
            driver._append_log(root, 'synthetic first message')
            with driver._timing_journal(night, plan), timing.span('arm', 'synthetic admission'):
                driver._append_log(root, 'synthetic interleaved message')
            raw = (root/'night.log').read_bytes()
            self.assertIn(b'synthetic first message', raw)
            self.assertIn(b'synthetic interleaved message', raw)
            self.assertFalse((night/'chain-stages.jsonl').exists())
            report = read_window(lambda path: raw, night_log='night.log')
            self.assertEqual(report['warnings'], [])
            self.assertEqual(report['phase_ns']['unattributed'], 0)
            self.assertGreater(report['phase_ns']['arm'], 0)

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

    def test_v4_arm_probe_and_packet_markers_precede_the_dwell_landmark(self):
        from tests.align.test_v4_next_arm_packet import ArmRebuildTests
        rig = ArmRebuildTests()
        rig.setUp()
        self.addCleanup(rig.doCleanups)
        scenario = rig.scenario().finish()
        rows, clock = [], FakeClock()
        def dwell_start():
            activities = [(row['activity'], row['event']) for row in rows]
            self.assertIn(('v4_meter_probe', 'end'), activities)
            self.assertIn(('v4_packet_rebuild', 'end'), activities)
            return 10**30
        with timing.bind(writer(rows, clock)):
            record = rig.arm(scenario, scenario.build(), dwell_start=dwell_start)
        self.assertTrue(record['admitted'], record['reasons'])
        documents, warnings = timing.project(rows)
        self.assertEqual(warnings, [])
        self.assertEqual({d['activity'] for d in documents},
                         {'v4_arm_checks', 'v4_packet_rebuild', 'v4_meter_probe'})

    def test_v4_disk_gate_and_installer_handoff_close_on_success_and_refusal(self):
        from scripts import align_v4_session as session
        for refused in (False, True):
            with self.subTest(refused=refused), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                rows, clock = [], FakeClock()
                record = dict(admitted=True, reasons=[], ac_powermode=dict(observed=0))
                def gate(*args, **kwargs):
                    clock.sleep(2)
                    if refused:
                        raise ValueError('synthetic disk refusal')
                    return {'status': 'pass'}
                with timing.bind(writer(rows, clock)), \
                     patch.object(session, 'arm_checks', return_value=record), \
                     patch.object(session, 'w1_disk_check', side_effect=gate), \
                     patch.object(session.kit, 'arm_powermode_check'), \
                     patch.object(session.pilot, 'install', return_value={'exit_code': 0}):
                    call = lambda: session._arm_and_install(root, {}, root, {}, None,
                        runner=None, volume_runner=None, now=lambda: 100, w1_disk_config=None, disk_gate=None)
                    if refused:
                        with self.assertRaisesRegex(ValueError, 'synthetic disk refusal'):
                            call()
                    else:
                        self.assertEqual(call(), {'exit_code': 0})
                documents, warnings = timing.project(rows)
                self.assertEqual(warnings, [])
                self.assertEqual([d['activity'] for d in documents],
                    ['v4_disk_gate'] if refused else ['v4_disk_gate', 'v4_installer_handoff'])
                self.assertEqual(documents[0]['end_boundary']['status'], 'error' if refused else 'complete')

    def test_chain_settle_uses_one_sleep_process_and_the_existing_chain_log(self):
        from joulewise.b5.chain import SETTLE_HELPER, _PRELUDE_FUNCTIONS
        self.assertNotIn('/bin/sleep', _PRELUDE_FUNCTIONS)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'window-chain.log'
            missing = subprocess.run([sys.executable, '-B', '-c', SETTLE_HELPER, str(path), '0'],
                capture_output=True, text=True)
            self.assertEqual(missing.returncode, 0, missing.stderr)
            self.assertFalse(path.exists())
            path.write_text('synthetic chain start\n')
            subprocess.run([sys.executable, '-B', '-c', SETTLE_HELPER, str(path), '0'], check=True)
            rows = [json.loads(line) for line in path.read_text().splitlines()[1:]]
            documents, warnings = timing.project(rows)
            self.assertEqual(warnings, [])
            self.assertEqual([d['activity'] for d in documents], ['chain_settle'])
            self.assertEqual(documents[0]['start_boundary']['requested_s'], 0)

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
    @classmethod
    def setUpClass(cls):
        import tarfile
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        cls.base = root / 'base'
        cls.base.mkdir()
        cls.repo = Path(__file__).resolve().parents[2]
        env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
               'GIT_NO_LAZY_FETCH': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
        # Export code/config only. No worktree operation, data path or fetch.
        names = subprocess.run(['git', 'ls-tree', '-r', '--name-only', '1a2574b49',
                                '--', 'joulewise', 'scripts', 'tests', 'configs'],
                               cwd=cls.repo, env=env, check=True, capture_output=True, text=True).stdout.splitlines()
        names = [p for p in names if p.endswith('.py') or p.startswith('configs/')]
        archive = subprocess.run(['git', 'archive', '1a2574b49', '--', *names],
                                 cwd=cls.repo, env=env, check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(cls.base, members=[m for m in tar.getmembers() if m.isfile()], filter='data')
        helper = cls.repo / 'tests/align/timing_receipts_capture.py'
        cls.captures, cls.desks = [], []
        for tree in (cls.base, cls.repo):
            child_env = {**env, 'PYTHONPATH': str(tree), 'GIT_DIR': str(cls.repo/'.git'),
                         'GIT_WORK_TREE': str(tree)}
            for operation, target in (('capture', cls.captures), ('desk', cls.desks)):
                output = root / operation
                code = 'import runpy; runpy.run_path('+repr(str(helper))+', run_name="__main__")'
                done = subprocess.run([sys.executable, '-B', '-c', code, operation, str(output)],
                                      cwd=tree, env=child_env, capture_output=True, text=True, timeout=240)
                if done.returncode:
                    raise AssertionError(done.stderr)
                target.append(json.loads(Path(str(output)+'.json').read_text()))
                normalized = Path(str(output)+'.normalized')
                if normalized.exists():
                    normalized.rename(root / ('base-bytes' if tree == cls.base else 'head-bytes'))
                if output.exists():
                    shutil.rmtree(output)  # this class's own synthetic output

    def test_full_w1_capture_bytes_equal_the_pinned_pre_receipts_tree(self):
        base, marked = self.captures
        self.assertEqual(base['manifest'].keys(), marked['manifest'].keys())
        unequal = [name for name in base['manifest'] if base['manifest'][name] != marked['manifest'][name]]
        if unequal:
            import difflib
            diagnostics = []
            for name in unequal[:4]:
                before = (Path(self.tmp.name)/'base-bytes'/name).read_text().splitlines()
                after = (Path(self.tmp.name)/'head-bytes'/name).read_text().splitlines()
                diagnostics.extend(line[:300] for line in list(difflib.unified_diff(before, after, fromfile='base/'+name, tofile='head/'+name))[:45])
            self.fail('\n'.join(diagnostics))
        self.assertEqual(base['markers'], 0)
        self.assertGreater(marked['markers'], 0)
        self.assertLess(marked['markers'], 100)

    def test_all_twenty_bundles_validate_without_any_structural_problem(self):
        for capture in self.captures:
            self.assertEqual(len(capture['problems']), 20)
            self.assertEqual(capture['problems'], {name: [] for name in capture['problems']})

    def test_real_w1_producer_output_has_negligible_unattributed_member_time(self):
        reader = self.captures[1]['reader']
        self.assertLessEqual(reader['unattributed_in_member_ns'], 1_000_000, reader)

    def test_happy_and_pre_chain_refusal_desk_bytes_equal_the_base_tree(self):
        self.assertEqual(self.desks[0], self.desks[1])
        for desk in self.desks:
            self.assertTrue(desk['False']['journal_exists'])
            self.assertFalse(desk['True']['journal_exists'])
            self.assertIsNone(desk['True']['stage_journal'])
            self.assertTrue(desk['True']['presence'])


if __name__ == '__main__':
    unittest.main()
