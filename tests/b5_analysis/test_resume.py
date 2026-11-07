"""Lane b5-robust: step checkpoints, resume, step-level retries and the defect sweep.

Synthetic only. The driver runs with the S10 DriverDouble of test_dry_run (every
registered dispatch builds real argv; doubles write the wire skeletons). A
"crash" is a KeyboardInterrupt (it escapes the driver's ``except Exception``
like a kill escapes the process) raised at a step boundary or after a runner
invocation inside a step. Each resumed run must write the record of the
uninterrupted run byte for byte and leave the same restricted tree.

Retries are driven by real producers: a real calibration refit whose wall
deadline fires (powermetrics_fiducial's clock only, as test_deadline_observer)
seen by the run's real observer, and a child-pool worker that dies (a real
BrokenProcessPool out of parallel.dispatch).
"""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

from joulewise import powermetrics_fiducial as pf
from joulewise.b5_analysis import dry_run as d, parallel, phase_timing, resume as R
from joulewise.b5_analysis.deadline_observer import CALIBRATION_WALL_DEADLINE
from tests.b5_analysis import test_dry_run as base
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER, JumpingClock


def tree(restricted):
    """{relative: sha256} of the restricted tree, without resume/ and the live timer logs."""
    restricted = Path(restricted)
    found = {}
    for path in sorted(restricted.rglob('*')):
        name = path.relative_to(restricted).as_posix()
        if name == R.RESUME_DIR or name.startswith(R.RESUME_DIR + '/') or R.is_live(name):
            continue
        found[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else '/'
    return found


class CrashingDouble(base.DriverDouble):
    """Raise KeyboardInterrupt after the ``crash_at``-th runner invocation (1-based) returns."""
    crash_at = None
    count = 0

    def run(self, main, argv, *, step, window=None, stdout_path=None):
        result = super().run(main, argv, step=step, window=window, stdout_path=stdout_path)
        type(self).count += 1
        if type(self).count == type(self).crash_at:
            raise KeyboardInterrupt('synthetic crash after a runner invocation')
        return result


class FiringDouble(base.DriverDouble):
    """Step 2's first ``fire`` attempts run one real calibration refit whose wall deadline fires."""
    fire = 0
    attempts = 0
    evidence = None

    def run(self, main, argv, *, step, window=None, stdout_path=None):
        if step == '2' and argv and argv[0] == 'reduce':
            type(self).attempts += 1
            if type(self).attempts <= type(self).fire:
                evidence, raw, events = type(self).evidence
                with mock.patch.object(pf, 'time', JumpingClock()):
                    try:
                        pf.verify_stored_evidence_physics(evidence, raw, events)
                    except ValueError:
                        pass
        return super().run(main, argv, step=step, window=window, stdout_path=stdout_path)


class DefectDouble(base.DriverDouble):
    """Strict validation refuses the kept bundles of ``invalid`` packs; reduce refuses ``unreducible`` ones."""
    invalid = frozenset()
    unreducible = frozenset()

    def run(self, main, argv, *, step, window=None, stdout_path=None):
        if argv and argv[0] == 'validate-bundle' and window in self.invalid:
            type(self).calls.append((step, window, list(argv)))
            return d.StepRunner.run(self, lambda a: 1, argv, step=step, window=window)
        if argv and argv[0] == 'reduce' and window in self.unreducible:
            type(self).calls.append((step, window, list(argv)))

            def refuse(a):
                print('error: synthetic_reduce_refusal', file=sys.stderr)
                return 2
            return d.StepRunner.run(self, refuse, argv, step=step, window=window)
        return super().run(main, argv, step=step, window=window, stdout_path=stdout_path)


def setUpModule():
    # As test_parallel_steps: "spawn" re-imports __main__ from its file.
    main = sys.modules['__main__']
    path = getattr(main, '__file__', None)
    if path is not None and not os.path.isfile(path):
        del main.__file__
        unittest.addModuleCleanup(setattr, main, '__file__', path)


def dying_worker(task):
    """Spawned child-pool worker that dies: the driver sees a real BrokenProcessPool."""
    os._exit(3)


class ResumeTests(unittest.TestCase):
    setUpClass = classmethod(base.DriverAcceptanceTests.setUpClass.__func__)
    setUp = base.DriverAcceptanceTests.setUp
    serial = 0

    def execute(self, *, custody=None, runner=base.DriverDouble, git=None, **options):
        type(self).serial += 1
        custody = custody or self.root / ('custody-' + str(self.serial))
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = d.run('blind-dry-run', self.index, custody, _test_pack_table=self.table, _test_repo_root=self.repo,
                         _runner=runner, _git=git or (lambda repo: 'b' * 40), **options)
        path = custody / 'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
        return dict(code=code, custody=custody, path=path, raw=path.read_bytes() if path.exists() else None,
                    stdout=stdout.getvalue(), stderr=stderr.getvalue(), restricted=custody / 'dry-run/restricted')

    def crash(self, **options):
        custody = self.root / ('crashed-' + str(type(self).serial + 1))
        type(self).serial += 1
        with self.assertRaises(KeyboardInterrupt), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            d.run('blind-dry-run', self.index, custody, _test_pack_table=self.table, _test_repo_root=self.repo,
                  _git=lambda repo: 'b' * 40, **options)
        return custody

    def assertSameRun(self, reference, resumed):
        self.assertEqual(resumed['code'], reference['code'], resumed['stderr'])
        self.assertEqual(resumed['raw'], reference['raw'])
        self.assertEqual(resumed['stderr'], reference['stderr'])
        self.assertEqual(tree(resumed['restricted']), tree(reference['restricted']))
        self.assertFalse((resumed['restricted'] / R.RESUME_DIR / R.CHECKPOINT).exists())

    def baseline(self, runner=base.DriverDouble):
        reference = self.execute(runner=runner)
        self.assertIn(reference['code'], (0, 2, 3), reference['stderr'])
        self.assertFalse((reference['restricted'] / R.RESUME_DIR).exists(), 'a clean run leaves no resume/')
        return reference

    def test_happy_path_writes_no_recovery_files(self):
        reference = self.baseline()
        self.assertEqual(reference['code'], 0, reference['stderr'])

    def test_resume_after_every_step_boundary_is_byte_identical(self):
        reference = self.baseline()
        original = R.Checkpoints.write
        for position in range(len(d.STEPS) + 1):
            with self.subTest(position=position):
                def write(checkpoints, s, runner, *, position, stopped, ran, at=position):
                    original(checkpoints, s, runner, position=position, stopped=stopped, ran=ran)
                    if position == at:
                        raise KeyboardInterrupt('synthetic crash at a step boundary')
                with mock.patch.object(R.Checkpoints, 'write', write):
                    custody = self.crash(_runner=base.DriverDouble)
                self.assertSameRun(reference, self.execute(custody=custody, resume=True))

    def test_resume_after_the_record_write_reports_the_complete_run(self):
        reference = self.baseline()
        with mock.patch.object(R.Checkpoints, 'finish', side_effect=KeyboardInterrupt('after the record')):
            custody = self.crash(_runner=base.DriverDouble)
        resumed = self.execute(custody=custody, resume=True)
        self.assertEqual((resumed['code'], resumed['raw']), (reference['code'], reference['raw']))
        self.assertIn('resume: run already complete', resumed['stderr'])
        self.assertFalse((resumed['restricted'] / R.RESUME_DIR / R.CHECKPOINT).exists())

    def test_a_torn_record_is_set_aside_and_rewritten(self):
        reference = self.baseline()
        with mock.patch.object(R.Checkpoints, 'finish', side_effect=KeyboardInterrupt('after the record')):
            custody = self.crash(_runner=base.DriverDouble)
        record = custody / 'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
        record.write_bytes(record.read_bytes()[:100])
        resumed = self.execute(custody=custody, resume=True)
        self.assertSameRun(reference, resumed)
        abandoned = list((resumed['restricted'] / R.RESUME_DIR / R.ABANDONED).rglob('B5-BLIND-DRY-RUN-RECORD.json'))
        self.assertEqual(len(abandoned), 1)

    def test_resume_after_a_crash_inside_every_step_is_byte_identical(self):
        reference = self.baseline()
        calls = [step for step, _, _ in base.DriverDouble.calls]
        # The first and the last runner invocation of every step: partial
        # outputs of the crashed step are on disk (steps 5, 8, 11 write
        # several files across invocations).
        points = sorted({calls.index(step) + 1 for step in set(calls)}
                        | {len(calls) - calls[::-1].index(step) for step in set(calls)})
        self.assertEqual({calls[p - 1] for p in points}, set(d.STEP_IDS))
        for point in points:
            with self.subTest(step=calls[point - 1], invocation=point):
                CrashingDouble.count, CrashingDouble.crash_at = 0, point
                custody = self.crash(_runner=CrashingDouble)
                CrashingDouble.crash_at = None
                resumed = self.execute(custody=custody, resume=True, runner=CrashingDouble)
                self.assertSameRun(reference, resumed)

    def test_resume_refuses_a_different_commit_and_a_changed_committed_file(self):
        def stop_at_4(checkpoints, s, runner, *, position, stopped, ran, original=R.Checkpoints.write):
            original(checkpoints, s, runner, position=position, stopped=stopped, ran=ran)
            if position == 5:
                raise KeyboardInterrupt
        with mock.patch.object(R.Checkpoints, 'write', stop_at_4):
            custody = self.crash(_runner=base.DriverDouble)
        other = self.execute(custody=custody, resume=True, git=lambda repo: 'c' * 40)
        self.assertEqual(other['code'], 2)
        self.assertIn('resume refused: analysis_commit_differs', other['stderr'])
        census = next((custody / 'dry-run/restricted/supply-census').iterdir())
        census.write_bytes(census.read_bytes() + b' ')
        changed = self.execute(custody=custody, resume=True)
        self.assertEqual(changed['code'], 2)
        self.assertIn('resume refused: checkpointed_file_differs', changed['stderr'])
        self.assertIsNone(changed['raw'])
        fresh = self.execute(resume=True)
        self.assertIn('resume refused: run_directory_unavailable', fresh['stderr'])

    def test_a_resumed_run_still_refuses_where_the_uninterrupted_run_refuses(self):
        base.DriverDouble.refusal = ('6', 'closeout_input_malformed')
        reference = self.baseline()
        self.assertEqual(reference['code'], 2)
        original = R.Checkpoints.write

        def write(checkpoints, s, runner, *, position, stopped, ran):
            original(checkpoints, s, runner, position=position, stopped=stopped, ran=ran)
            if position == 6:
                raise KeyboardInterrupt
        with mock.patch.object(R.Checkpoints, 'write', write):
            custody = self.crash(_runner=base.DriverDouble)
        self.assertSameRun(reference, self.execute(custody=custody, resume=True))


class RetryTests(ResumeTests):
    """Step-level retries from real tooling-refusal producers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with tarfile.open(ARCHIVE) as blob:
            members = [m for m in blob.getmembers() if m.name.startswith(MEMBER)]
            blob.extractall(cls.root / 'member', members=members, filter='data')
        cal = cls.root / 'member' / MEMBER / 'instrument_calibration'
        FiringDouble.evidence = (json.loads((cal / 'instrument_evidence.json').read_bytes()),
                                 (cal / 'raw/powermetrics.plist').read_bytes(), (cal / 'events.jsonl').read_bytes())

    # The inherited resume tests run once, in ResumeTests.
    for name in [n for n in dir(ResumeTests) if n.startswith('test_')]:
        locals()[name] = None
    del name

    def retries(self, result):
        path = result['restricted'] / R.RESUME_DIR / R.RETRIES
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_a_real_wall_deadline_firing_is_retried_and_leaves_the_uninterrupted_record(self):
        reference = self.baseline()
        FiringDouble.fire, FiringDouble.attempts = 1, 0
        log = Path(tempfile.mkdtemp(dir=self.root)) / 'phases.jsonl'
        descriptor = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with phase_timing.session(descriptor, mode='blind-dry-run'):
            retried = self.execute(runner=FiringDouble)
        self.assertEqual(retried['code'], 0, retried['stderr'])
        self.assertEqual(retried['raw'], reference['raw'])
        self.assertEqual(retried['stderr'], reference['stderr'])
        self.assertEqual(tree(retried['restricted']), tree(reference['restricted']))
        rows = self.retries(retried)
        self.assertEqual([(r['event'], r['step'], r['attempt'], r['reason']) for r in rows],
                         [('step_retry', '2', 1, CALIBRATION_WALL_DEADLINE)])
        self.assertGreater(rows[0]['moved_files'], 0, 'the refused attempt left its logs, now set aside')
        lines = [phase_timing.validate_phase_line(line) for line in log.read_bytes().splitlines(keepends=True)]
        self.assertIn({'event': 'step_retry', 'step': '2', 'attempt': 1}, lines)

    def test_a_deadline_that_keeps_firing_stops_after_two_retries(self):
        FiringDouble.fire, FiringDouble.attempts = 99, 0
        result = self.execute(runner=FiringDouble)
        self.assertEqual(result['code'], 2)
        record = json.loads(result['raw'])
        step2 = next(row for row in record['steps'] if row['step'] == '2')
        self.assertEqual((step2['status'], step2['refusal']), ('tooling_refusal', CALIBRATION_WALL_DEADLINE))
        # One kept bundle per pack, so one step-2 attempt is len(PACKS) reduce invocations.
        self.assertEqual(FiringDouble.attempts, len(d.PACKS) * (1 + R.MAX_RETRIES))
        self.assertEqual([r['attempt'] for r in self.retries(result) if r['event'] == 'step_retry'], [1, 2])

    def test_a_data_refusal_is_never_retried(self):
        base.DriverDouble.refusal = ('5', 'mint_inputs_invalid')
        result = self.execute()
        self.assertEqual(result['code'], 2)
        self.assertEqual(self.retries(result), [])
        self.assertEqual(len([c for c in base.DriverDouble.calls if c[0] == '5']), 1)

    def test_a_dead_pool_worker_is_retried_serially(self):
        from tests.b5_analysis.test_parallel_steps import GOOD, RUNS
        root = Path(tempfile.mkdtemp(dir=self.root))
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(root, members=[m for m in blob.getmembers()
                                           if m.name.startswith(tuple(RUNS + n + '/' for n in GOOD[:2]))],
                            filter='data')
        bundles = [('alpha', name, root / RUNS / name) for name in GOOD[:2]]

        def step(s, r):
            s.kept_bundles = lambda: iter(bundles)
            return d.step_2(s, r)
        (root / 'repo').mkdir()
        index = root / 'index.json'
        index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        steps = [(name, (lambda s, r, name=name: [s.record(name)]) if name != '2' else step) for name in d.STEP_IDS]

        def go(custody, worker):
            with mock.patch.object(d, 'STEPS', steps), mock.patch.object(parallel, 'run_child', worker), \
                    mock.patch.object(d, 'validate_dry_run_record'), \
                    mock.patch.object(d, '_record_parts', return_value=([], [], [])), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = d.run('blind-dry-run', index, custody, workers=2, _test_repo_root=root / 'repo',
                             _git=lambda repo: 'b' * 40)
            path = custody / 'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
            return dict(code=code, raw=path.read_bytes(), restricted=custody / 'dry-run/restricted')
        reference = go(root / 'reference', parallel.run_child)
        died = go(root / 'died', dying_worker)
        self.assertEqual(reference['code'], 0)
        self.assertEqual((died['code'], died['raw']), (reference['code'], reference['raw']))
        # As test_parallel_steps: the same tree; every non-log byte the same.
        died_tree, reference_tree = tree(died['restricted']), tree(reference['restricted'])
        self.assertEqual(sorted(died_tree), sorted(reference_tree))
        self.assertEqual({k: v for k, v in died_tree.items() if not k.startswith('logs/')},
                         {k: v for k, v in reference_tree.items() if not k.startswith('logs/')})
        self.assertEqual([(r['event'], r['step'], r['reason']) for r in self.retries(died)],
                         [('step_retry', '2', 'BrokenProcessPool')])


class DefectSweepTests(ResumeTests):
    for name in [n for n in dir(ResumeTests) if n.startswith('test_')]:
        locals()[name] = None
    del name

    def setUp(self):
        super().setUp()
        DefectDouble.invalid, DefectDouble.unreducible = frozenset(), frozenset()

    def test_every_independent_bundle_defect_is_reported_in_one_pass(self):
        DefectDouble.invalid, DefectDouble.unreducible = frozenset({'alpha', 'gamma'}), frozenset({'beta'})
        with mock.patch.object(R, 'defect_sweep', return_value=None):
            unswept = self.execute(runner=DefectDouble)
        swept = self.execute(runner=DefectDouble)
        self.assertEqual(swept['code'], 2)
        self.assertEqual(swept['raw'], unswept['raw'], 'the sweep never changes the record')
        record = json.loads(swept['raw'])
        stop = next(row for row in record['steps'] if row['status'] != 'ok')
        self.assertEqual((stop['step'], stop['window']), ('1', 'alpha'))
        document = json.loads((swept['restricted'] / 'defects/DEFECTS.json').read_bytes())
        self.assertEqual(sorted((row['step'], row['window']) for row in document['defects']),
                         [('1', 'alpha'), ('1', 'gamma'), ('2', 'beta')])
        self.assertEqual(document['units'], 3)
        self.assertEqual(document['tooling_inconclusive'], [])
        for line in ('defects step 1 alpha 1', 'defects step 1 gamma 1', 'defects step 2 beta 1'):
            self.assertIn(line, swept['stderr'])
        self.assertNotIn(base.MARKER, swept['stderr'])
        self.assertEqual(swept['stderr'].replace(unswept['stderr'], ''), ''.join(
            line + '\n' for line in swept['stderr'].splitlines() if line.startswith('defect')))

    def test_no_sweep_after_a_refusal_outside_steps_1_and_2(self):
        base.DriverDouble.refusal = ('5', 'mint_inputs_invalid')
        result = self.execute()
        self.assertFalse((result['restricted'] / 'defects').exists())
        self.assertNotIn('defect', result['stderr'])


if __name__ == '__main__':
    unittest.main()
