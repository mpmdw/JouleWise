"""Deterministic worker pool for steps 1, 2 and 4 (L9-SPEEDUP-R1 stage 2).

Synthetic only: three committed S10 ALPHA members and one member whose reduce
refuses (its finalized summary names no reducer version) are extracted from the
committed archive. ``--workers 1`` is the serial path; any other count must
leave the same record, the same registered bytes, the same custody tree and the
same log counter, including when the step stops at a refusal.
"""
import contextlib
import dataclasses
import hashlib
import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_run_cache as arc, powermetrics_fiducial as pf, whole_window as ww
from joulewise.b5_analysis import dry_run as d, parallel
from joulewise.b5_analysis.deadline_observer import (CALIBRATION_WALL_DEADLINE, DeadlineObserver,
                                                       OBSERVER_UNAVAILABLE)
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, JumpingClock

RUNS = 'archive/sources/night-custody/runs_claim/'
GOOD = ('d117fq31p7-df-cmp-abba-ph-decode-b01-a2', 'd117fq31p7-df-cmp-abba-ph-decode-b01-b1', 'neg8-window-end-r1')
REFUSED = 'd117fq31p7-df-cmp-abba-ph-decode-b01-a1'


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


def firing_worker(task):
    """Spawned-worker wrapper: every calibration refit in this worker hits the wall deadline."""
    with mock.patch.object(pf, 'time', JumpingClock()):
        return parallel.run_child(task)


def blind_worker(task):
    """Spawned-worker wrapper: the worker could not install its deadline observer."""
    return dataclasses.replace(parallel.run_child(task), firings=None)


def late_firing_worker(task):
    """Spawned-worker wrapper: only the task after the refusal stop hits the wall deadline."""
    if any(GOOD[2] in arg for arg in task.argv):
        return firing_worker(task)
    return parallel.run_child(task)


def late_blind_worker(task):
    """Spawned-worker wrapper: only the task after the refusal stop could not observe."""
    if any(GOOD[2] in arg for arg in task.argv):
        return blind_worker(task)
    return parallel.run_child(task)


def tree(root):
    return sorted(p.relative_to(root).as_posix() + ('/' if p.is_dir() else '') for p in Path(root).rglob('*'))


class WorkerCountTests(unittest.TestCase):
    def test_resolution(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(parallel.WORKERS_ENV, None)
            with mock.patch.object(parallel.os, 'cpu_count', return_value=10):
                self.assertEqual(parallel.resolve_workers(), 8)
            with mock.patch.object(parallel.os, 'cpu_count', return_value=4):
                self.assertEqual(parallel.resolve_workers(), 2)
            with mock.patch.object(parallel.os, 'cpu_count', return_value=None):
                self.assertEqual(parallel.resolve_workers(), 1)
            for value, expected in (('3', 3), (' 1 ', 1), ('0', None), ('x', None), ('-2', None)):
                with self.subTest(value=value), mock.patch.dict(os.environ, {parallel.WORKERS_ENV: value}):
                    self.assertEqual(parallel.resolve_workers(), expected or parallel.default_workers())
            self.assertEqual(parallel.resolve_workers(5), 5)
            for bad in (0, -1, True, 1.0, '2'):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    parallel.resolve_workers(bad)

    def test_cli_flag(self):
        from scripts import run_b5_analysis as script
        with mock.patch.object(script, 'run', return_value=0) as run:
            self.assertEqual(script.main(['--mode', 'release', '--index', 'i.json', '--custody', 'c', '--workers', '3']), 0)
        run.assert_called_once_with('release', Path('i.json'), Path('c'), workers=3)
        for bad in ('0', '-1', 'x', '1.5', ''):
            out, err = io.StringIO(), io.StringIO()
            with self.subTest(bad=bad), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                    mock.patch.object(script, 'run') as run:
                self.assertEqual(script.main(['--mode', 'release', '--index', 'i', '--custody', 'c', '--workers', bad]), 2)
                run.assert_not_called()
            self.assertEqual(err.getvalue(), 'step 0 - tooling_refusal\n')

    def test_run_refuses_an_invalid_explicit_count(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(d.run('blind-dry-run', 'index.json', '/nonexistent-custody', workers=0), 2)
        self.assertEqual(err.getvalue(), 'step 0 - tooling_refusal\n')

    def test_only_the_plain_runner_with_several_workers_is_parallel(self):
        class Overriding(d.StepRunner):
            def run(self, *args, **kwargs):
                return super().run(*args, **kwargs)
        with tempfile.TemporaryDirectory(prefix='par-gate-') as tmp:
            s = d.RunState('blind-dry-run', Path(tmp) / 'i.json', Path(tmp) / 'restricted', 'a' * 40)
            plain, other = d.StepRunner(s.restricted), Overriding(s.restricted)
            self.assertEqual(s.workers, 1)
            self.assertFalse(d._parallel(s, plain, 5))
            s.workers = 4
            self.assertTrue(d._parallel(s, plain, 2))
            self.assertFalse(d._parallel(s, plain, 1))
            self.assertFalse(d._parallel(s, other, 5))


class ParallelStepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='par-steps-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        wanted = tuple(RUNS + name + '/' for name in (*GOOD, REFUSED))
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(cls.root, members=[m for m in blob.getmembers() if m.name.startswith(wanted)],
                            filter='data')
        cls.bundles = {name: cls.root / RUNS / name for name in (*GOOD, REFUSED)}
        cls.serial = 0

    def state(self, workers, names):
        type(self).serial += 1
        custody = self.root / f'custody-{self.serial}'
        s = d.RunState('blind-dry-run', self.root / 'index.json', custody / 'restricted', 'a' * 40)
        s.workers, s.deadline, s.physics_store = workers, DeadlineObserver(), {}
        jobs = [('alpha', name, self.bundles[name]) for name in names]
        s.kept_bundles = lambda: iter(jobs)
        s.prepare_kept = lambda argv: 0
        return s, d.StepRunner(s.restricted)

    def execute(self, step, workers, names):
        s, r = self.state(workers, names)
        # As d.run: the run store is shared in the driver process.
        with ww.shared_instrument_calibration_physics_cache(s.physics_store), \
                arc.analysis_run_caches(s.physics_store), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                records = [x.as_dict() for x in step(s, r)]
            except AnalysisRefusal as exc:
                records = exc.code
        digests = {role: item for role, item in s.outputs.items()}
        files = {name: hashlib.sha256((s.restricted / name).read_bytes()).hexdigest()
                 for name in tree(s.restricted) if not name.endswith('/') and not name.startswith('logs/')}
        return dict(records=records, outputs=digests, tree=tree(s.restricted), files=files,
                    counter=r._counter, firings=s.deadline.firings, store=s.physics_store)

    def assertSameRun(self, serial, parallel_run):
        for key in ('records', 'outputs', 'tree', 'files', 'counter', 'firings'):
            self.assertEqual(serial[key], parallel_run[key], key)

    def test_step_2_workers_1_and_n_are_identical(self):
        names = GOOD
        serial = self.execute(d.step_2, 1, names)
        pooled = self.execute(d.step_2, 3, names)
        self.assertEqual(serial['records'][0]['status'], 'ok')
        self.assertEqual(len(serial['outputs']), len(names))
        self.assertSameRun(serial, pooled)
        self.assertEqual(serial['store'], pooled['store'], 'worker fits merge into the run store')

    def test_step_2_stop_at_a_refusal_leaves_serial_custody(self):
        names = (GOOD[0], GOOD[1], REFUSED, GOOD[2])
        serial = self.execute(d.step_2, 1, names)
        pooled = self.execute(d.step_2, 3, names)
        self.assertNotEqual(serial['records'][0]['status'], 'ok')
        self.assertEqual(len(serial['outputs']), 2)
        self.assertSameRun(serial, pooled)
        self.assertFalse(any(GOOD[2] in name for name in pooled['tree']), 'the later bundle left no file')

    def test_step_1_workers_1_and_n_are_identical(self):
        for names in (GOOD, (GOOD[0], REFUSED, GOOD[1])):
            with self.subTest(names=names):
                serial = self.execute(d.step_1, 1, names)
                pooled = self.execute(d.step_1, 2, names)
                self.assertSameRun(serial, pooled)

    def test_a_wall_deadline_in_a_worker_fails_the_step_closed(self):
        with mock.patch.object(parallel, 'run_child', firing_worker):
            pooled = self.execute(d.step_2, 2, GOOD[:2])
        self.assertGreater(pooled['firings'], 0, 'the driver observer counts the worker firing')
        self.assertEqual(pooled['store'], {}, 'nothing a firing worker fitted reaches the run store')

    def test_a_worker_without_an_observer_refuses(self):
        with mock.patch.object(parallel, 'run_child', blind_worker):
            pooled = self.execute(d.step_2, 2, GOOD[:2])
        self.assertEqual(pooled['records'], OBSERVER_UNAVAILABLE)

    def test_observations_after_the_stop_do_not_count(self):
        # A serial run never starts the task after the stop, so its firing (or
        # missing observer) must not turn the refusal into a tooling refusal.
        names = (GOOD[0], REFUSED, GOOD[2])
        serial = self.execute(d.step_2, 1, names)
        self.assertNotEqual(serial['records'][0]['status'], 'ok')
        for worker in (late_firing_worker, late_blind_worker):
            with self.subTest(worker=worker.__name__), mock.patch.object(parallel, 'run_child', worker):
                pooled = self.execute(d.step_2, 3, names)
                self.assertSameRun(serial, pooled)
                self.assertEqual(pooled['firings'], 0)

    def test_driver_records_a_worker_firing_as_calibration_wall_deadline(self):
        bundles = [('alpha', name, self.bundles[name]) for name in GOOD[:2]]

        def step(s, r):
            s.kept_bundles = lambda: iter(bundles)
            return d.step_2(s, r)
        root = self.root / 'driver'
        (root / 'repo').mkdir(parents=True)
        index = root / 'index.json'
        index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        steps = [(name, (lambda s, r, name=name: [s.record(name)]) if name != '2' else step) for name in d.STEP_IDS]
        with mock.patch.object(d, 'STEPS', steps), mock.patch.object(parallel, 'run_child', firing_worker), \
                mock.patch.object(d, 'validate_dry_run_record'), mock.patch.object(d, '_record_parts',
                                                                                  return_value=([], [], [])), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = d.run('blind-dry-run', index, root / 'custody', workers=2, _test_repo_root=root / 'repo',
                         _git=lambda repo: 'b' * 40)
        record = json.loads((root / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
        self.assertEqual(code, 2)
        step2 = next(row for row in record['steps'] if row['step'] == '2')
        self.assertEqual((step2['status'], step2['refusal']), ('tooling_refusal', CALIBRATION_WALL_DEADLINE))


if __name__ == '__main__':
    unittest.main()
