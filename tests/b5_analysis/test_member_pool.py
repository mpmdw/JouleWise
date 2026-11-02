"""Ordered member pool for whole-window derivations (L9-SPEEDUP-R1 stage 4b).

The pool is used only inside an analysis run with workers > 1. Consumption at
each member's serial position must leave the caller's V2 read session exactly as
the serial loop leaves it; a task that raised is recomputed by the caller; worker
wall-deadline firings reach the run's observer; a worker without an observer marks
the run (the driver refuses the step).
"""
import dataclasses
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_member_pool as pool, analysis_run_cache as arc
from joulewise.authentication_io import (V2AuthenticationInputError, V2AuthenticationReadSession,
                                         read_authentication_input)
from joulewise.b5_analysis.deadline_observer import DeadlineObserver

def setUpModule():
    # "spawn" re-imports __main__ from its file; the hosted shard runner feeds the
    # test program on stdin (main path "<stdin>"), which kills every pool worker at
    # startup on Linux CI (as in PR #371). The analysis runner's __main__ is
    # scripts/run_b5_analysis.py, a real file, so only the test harness needs this.
    main = sys.modules['__main__']
    path = getattr(main, '__file__', None)
    if path is not None and not os.path.isfile(path):
        del main.__file__
        unittest.addModuleCleanup(setattr, main, '__file__', path)


def read_member(directory, name):
    """A member derivation: authenticated reads in a fixed order, a pure result."""
    root = Path(directory)
    meta = read_authentication_input(root / 'meta.json', grammar='json', label='meta')
    raw = read_authentication_input(root / name, grammar='raw', label='raw')
    again = read_authentication_input(root / name, grammar='raw', label='raw again')
    if raw.startswith(b'fail'):
        raise ValueError('member refused')
    return {'name': name, 'size': len(raw) + len(again), 'meta': len(meta)}


def firing_worker(task):
    return dataclasses.replace(pool.run_member(task), firings=2)


def blind_worker(task):
    return dataclasses.replace(pool.run_member(task), firings=None)


def records(session):
    return [(r.normalized_path, r.sha256, r.grammar, r.read_count, r.strict_parse_succeeded)
            for r in session.records.values()]


class MemberPoolTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='member-pool-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'meta.json').write_text('{"a": 1}')
        self.names = ['m3', 'm1', 'm2', 'm4']
        for index, name in enumerate(self.names):
            (self.root / name).write_bytes(b'x' * (index + 1))

    def serial(self, names):
        values = []
        for name in names:
            try:
                values.append(read_member(self.root, name))
            except ValueError as exc:
                values.append(('refused', str(exc)))
        return values

    def pooled(self, names, workers=3, worker=None, deadline=None):
        with arc.analysis_run_caches({}, workers=workers) as caches:
            caches.deadline = deadline
            outcomes = pool.member_map(read_member, [((str(self.root), n), {}) for n in names], worker=worker)
            values = []
            for name, outcome in zip(names, outcomes or [None] * len(names)):
                try:
                    values.append(pool.consume(outcome, lambda name=name: read_member(self.root, name)))
                except ValueError as exc:
                    values.append(('refused', str(exc)))
            return values, outcomes, caches.worker_observer_unavailable

    def test_inactive_outside_a_run_or_with_one_worker_or_one_call(self):
        calls = [((str(self.root), n), {}) for n in self.names]
        self.assertIsNone(pool.member_map(read_member, calls))
        with arc.analysis_run_caches({}, workers=1):
            self.assertIsNone(pool.member_map(read_member, calls))
        with arc.analysis_run_caches({}, workers=4):
            self.assertIsNone(pool.member_map(read_member, calls[:1]))
            self.assertIsNone(pool.member_map(lambda *a: None, calls), 'a non-module-level function stays serial')

    def test_session_census_and_values_equal_serial(self):
        with V2AuthenticationReadSession() as serial_session:
            read_authentication_input(self.root / 'meta.json', grammar='json', label='first')
            expected = self.serial(self.names)
        with V2AuthenticationReadSession() as pooled_session:
            read_authentication_input(self.root / 'meta.json', grammar='json', label='first')
            values, outcomes, _ = self.pooled(self.names)
        self.assertTrue(all(o.ok for o in outcomes))
        self.assertEqual(values, expected)
        self.assertEqual(records(pooled_session), records(serial_session))

    def test_without_a_session_nothing_is_registered(self):
        values, outcomes, _ = self.pooled(self.names)
        self.assertEqual(values, self.serial(self.names))
        self.assertTrue(all(o.records == () for o in outcomes))

    def test_a_raising_task_is_recomputed_by_the_caller(self):
        (self.root / 'm2').write_bytes(b'fail')
        with V2AuthenticationReadSession() as serial_session:
            expected = self.serial(self.names)
        with V2AuthenticationReadSession() as pooled_session:
            values, outcomes, _ = self.pooled(self.names)
        self.assertEqual([o.ok for o in outcomes], [True, True, False, True])
        self.assertEqual(values, expected)
        self.assertEqual(records(pooled_session), records(serial_session))

    def test_a_byte_changed_since_the_first_read_is_refused_at_consumption(self):
        with V2AuthenticationReadSession():
            read_authentication_input(self.root / 'm1', grammar='raw', label='first')
            (self.root / 'm1').write_bytes(b'changed')
            with self.assertRaises(V2AuthenticationInputError):
                self.pooled(self.names)

    def test_worker_firings_reach_the_run_observer(self):
        observer = DeadlineObserver()
        _, _, unavailable = self.pooled(self.names, worker=firing_worker, deadline=observer)
        self.assertEqual(observer.firings, 2 * len(self.names))
        self.assertFalse(unavailable)

    def test_a_worker_without_an_observer_marks_the_run(self):
        _, _, unavailable = self.pooled(self.names, worker=blind_worker, deadline=DeadlineObserver())
        self.assertTrue(unavailable)


def jumping_worker(task):
    """A spawned worker whose calibration refits all hit the wall deadline."""
    from joulewise import powermetrics_fiducial as pf
    from tests.b5_analysis.test_shared_physics_cache import JumpingClock
    with mock.patch.object(pf, 'time', JumpingClock()):
        return pool.run_member(task)


class RealMemberTests(unittest.TestCase):
    """The session's real pool entry point on committed S10 members."""

    @classmethod
    def setUpClass(cls):
        import tarfile
        from tests.b5_analysis.test_shared_physics_cache import ARCHIVE
        cls.tmp = tempfile.TemporaryDirectory(prefix='member-pool-real-')
        cls.addClassCleanup(cls.tmp.cleanup)
        runs = 'archive/sources/night-custody/runs_claim/'
        names = ('neg8-window-end-r1', 'd117fq31p7-df-cmp-abba-ph-decode-b01-a2')
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(cls.tmp.name, members=[m for m in blob.getmembers()
                                                   if m.name.startswith(tuple(runs + n + '/' for n in names))],
                            filter='data')
        cls.members = [Path(cls.tmp.name) / runs / n for n in names]

    def calls(self):
        import json
        from joulewise import whole_window as ww
        out = []
        for member in self.members:
            metadata = json.loads((member / 'metadata.json').read_bytes())
            bound = 2 * metadata['instrument_calibration']['verified_effective_b_fiducial_s']
            out.append(((ww._rederive_operative_summary, member, bound, metadata), {}))
        return out

    def test_pooled_operative_summaries_equal_serial_and_census(self):
        from joulewise import whole_window as ww
        calls = self.calls()
        store = {}
        with V2AuthenticationReadSession() as serial_session, \
                ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store):
            expected = [ww._member_operative_summary(*args) for args, _ in calls]
        pooled_store = {}
        with V2AuthenticationReadSession() as pooled_session, \
                ww.shared_instrument_calibration_physics_cache(pooled_store), \
                arc.analysis_run_caches(pooled_store, workers=2) as caches:
            caches.deadline = DeadlineObserver()
            outcomes = pool.member_map(ww._member_operative_summary, calls)
            values = [pool.consume(o, lambda: None) for o in outcomes]
            self.assertEqual(caches.deadline.firings, 0)
        self.assertTrue(all(o.ok for o in outcomes))
        self.assertEqual(values, expected)
        self.assertEqual(records(pooled_session), records(serial_session))
        self.assertEqual(pooled_store, store, 'worker fits merge into the run store')

    def test_a_real_wall_deadline_in_a_member_worker_reaches_the_observer_and_is_not_stored(self):
        from joulewise import whole_window as ww
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), \
                arc.analysis_run_caches(store, workers=2) as caches:
            caches.deadline = DeadlineObserver()
            pool.member_map(ww._member_operative_summary, self.calls(), worker=jumping_worker)
            self.assertGreater(caches.deadline.firings, 0)
        self.assertEqual(store, {})


class DriverObserverTests(unittest.TestCase):
    def test_driver_refuses_a_step_whose_member_pool_could_not_observe(self):
        import contextlib
        import io
        import json
        from joulewise.b5_analysis import dry_run as d
        from joulewise.b5_analysis.deadline_observer import OBSERVER_UNAVAILABLE

        def step(s, r):
            arc.current().worker_observer_unavailable = True
            return [s.record('5')]
        with tempfile.TemporaryDirectory(prefix='member-pool-driver-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            steps = [(n, step if n == '5' else (lambda s, r, n=n: [s.record(n)])) for n in d.STEP_IDS]
            with mock.patch.object(d, 'STEPS', steps), mock.patch.object(d, 'validate_dry_run_record'), \
                    mock.patch.object(d, '_record_parts', return_value=([], [], [])), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = d.run('blind-dry-run', index, root / 'custody', workers=2, _test_repo_root=root / 'repo',
                             _git=lambda repo: 'b' * 40)
            record = json.loads((root / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
        self.assertEqual(code, 2)
        row = next(row for row in record['steps'] if row['step'] == '5')
        self.assertEqual((row['status'], row['refusal']), ('tooling_refusal', OBSERVER_UNAVAILABLE))


if __name__ == '__main__':
    unittest.main()
