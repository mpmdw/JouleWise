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
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_member_pool as member_pool, analysis_run_cache as arc
from joulewise import floor_extraction as fe, powermetrics_fiducial as pf, whole_window as ww
from joulewise.authentication_io import V2AuthenticationInputError
from joulewise.b5_analysis import bracket, dry_run as d, parallel
from joulewise.b5_analysis.archive import CensusRow
from joulewise.b5_analysis.deadline_observer import (CALIBRATION_WALL_DEADLINE, DeadlineObserver,
                                                       OBSERVER_UNAVAILABLE)
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, JumpingClock

RUNS = 'archive/sources/night-custody/runs_claim/'
GOOD = ('d117fq31p7-df-cmp-abba-ph-decode-b01-a2', 'd117fq31p7-df-cmp-abba-ph-decode-b01-b1', 'neg8-window-end-r1')
REFUSED = 'd117fq31p7-df-cmp-abba-ph-decode-b01-a1'
TAMPERED = 'r2-tampered-summary'


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


def late_firing_member(task):
    """Member-pool worker wrapper: only the member after the stop hits the wall deadline."""
    outcome = member_pool.run_member(task)
    if any(GOOD[2] in str(arg) for arg in task.args):
        return dataclasses.replace(outcome, firings=2)
    return outcome


def late_blind_member(task):
    """Member-pool worker wrapper: only the member after the stop could not observe."""
    outcome = member_pool.run_member(task)
    if any(GOOD[2] in str(arg) for arg in task.args):
        return dataclasses.replace(outcome, firings=None)
    return outcome


def raising_member(task):
    """Member-pool worker wrapper: every task 'raised' in the worker (the caller recomputes)."""
    return dataclasses.replace(member_pool.run_member(task), ok=False, value=None)


def blind_member(task):
    """Member-pool worker wrapper: no member worker could observe."""
    return dataclasses.replace(member_pool.run_member(task), firings=None)


def member_probe(path):
    """A member derivation for the nested-pool child program: its size and the computing process."""
    return {'size': len(Path(path).read_bytes()), 'pid': os.getpid()}


def nested_child_program(argv):
    """A step-4 child program: one ordered member pass, consumed in order; writes a probe file."""
    probe, mode, *paths = argv
    worker = {'blind': blind_member}.get(mode)
    outcomes = member_pool.member_map(member_probe, [((path,), {}) for path in paths], worker=worker)
    values = [member_pool.consume(outcome, lambda path=path: member_probe(path))
              for path, outcome in zip(paths, outcomes or [None] * len(paths))]
    for value in values:
        print(value['size'])
    Path(probe).write_text(json.dumps({'pooled': outcomes is not None, 'child': os.getpid(),
                                       'members': [value['pid'] for value in values]}))
    return 0


def member_workers_worker(task):
    """Spawned-worker stand-in: reports the member workers its task was given."""
    return parallel.ChildResult(task.member_workers, '', '', False, 0, {})


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



class _SelectionArchive:
    """The parts of an ArchiveHandle and its _Inputs that bracket._window_inputs reads.

    The members are real committed S10 bundles; ``source`` records the archive
    census exactly as archive._read does, and can refuse one file.
    """

    claim = Path('/synthetic-claim-runs')

    def __init__(self, root, names, recorded, *, refuse=None):
        self.root, self.refuse = Path(root), refuse
        self.window = type('Window', (), {'claim_runs_root': self.claim,
                                          'custody_root': Path('/synthetic-custody')})()
        self._census = {}
        self.manifest = {}
        for name in names:
            for path in sorted((self.root / name).rglob('*')):
                if path.is_file():
                    relative = 'claim-runs/' + path.relative_to(self.root).as_posix()
                    self.manifest[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assessments = {'members': {name: {'bundle_path': str(self.claim / name), 'strict_valid': True,
                                               'status': 'succeeded', 'anchor_recorded': 'bounded'}
                                        for name in recorded}}
        self.roster = {'members': [{'run_id': name} for name in names]}

    def withheld_bytes(self, name):
        return json.dumps(self.assessments).encode()

    def output_bytes(self, name):
        return json.dumps(self.roster).encode()

    def source(self, relative, *, code='archive_source_unauthenticated'):
        if self.refuse is not None and self.refuse in relative:
            raise AnalysisRefusal(code)
        raw = (self.root / relative.removeprefix('sources/claim-runs/')).read_bytes()
        self._census[relative] = CensusRow(relative, hashlib.sha256(raw).hexdigest(), 'sources_sha256sums')
        return raw


class _StoppingReader(bracket.BundleReader):
    """The selection's own reader stops (an authentication failure) at one bundle."""

    def raw_metadata(self):
        if GOOD[1] in str(self.path):
            raise V2AuthenticationInputError('v2_authentication_input_changed', 'synthetic stop')
        return super().raw_metadata()


class StepThreeBSelectionTests(unittest.TestCase):
    """L9-SPEEDUP-R2 item 1: 3b's selection validations in the member pool, workers=1 vs N."""

    @classmethod
    def setUpClass(cls):
        ParallelStepTests.setUpClass.__func__(cls)
        cls.names = tuple(sorted((*GOOD, REFUSED)))

    def select(self, workers, *, recorded=GOOD, refuse=None, reader=None, worker=None):
        archive = _SelectionArchive(self.root / RUNS, self.names, recorded, refuse=refuse)
        store, observer = {}, DeadlineObserver()
        with contextlib.ExitStack() as stack:
            stack.enter_context(ww.shared_instrument_calibration_physics_cache(store))
            caches = stack.enter_context(arc.analysis_run_caches(store, workers=workers))
            caches.deadline = observer
            directory = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='sel-')))
            if reader is not None:
                stack.enter_context(mock.patch.object(bracket, 'BundleReader', reader))
            if worker is not None:
                stack.enter_context(mock.patch.object(member_pool, 'run_member', worker))
            try:
                result = [path.relative_to(directory).as_posix() for path in
                          bracket._window_inputs(archive, archive, directory)]
            except (AnalysisRefusal, V2AuthenticationInputError) as exc:
                result = (type(exc).__name__, getattr(exc, 'code', None) or exc.reason)
            pooled = caches.pool is not None
            unavailable = caches.worker_observer_unavailable
        return dict(result=result, census=list(archive._census.items()), firings=observer.firings,
                    unavailable=unavailable, store=store, pooled=pooled)

    def assertSameSelection(self, serial, pooled):
        for key in ('result', 'census', 'firings', 'unavailable'):
            self.assertEqual(serial[key], pooled[key], key)
        self.assertFalse(serial['pooled'])
        self.assertTrue(pooled['pooled'], 'the member pool ran')

    def test_selection_workers_1_and_n_are_identical(self):
        serial = self.select(1)
        pooled = self.select(2)
        self.assertEqual(serial['result'], sorted(GOOD), 'the strict-invalid member is not selected')
        self.assertSameSelection(serial, pooled)
        self.assertEqual(serial['store'], pooled['store'], 'worker fits merge into the run store')

    def test_a_selection_that_disagrees_with_the_harvest_refuses_identically(self):
        serial = self.select(1, recorded=self.names)
        pooled = self.select(2, recorded=self.names)
        self.assertEqual(serial['result'], ('AnalysisRefusal', 'window_bracket_not_passed'))
        self.assertSameSelection(serial, pooled)

    def test_a_raising_member_is_recomputed_serially(self):
        serial = self.select(1)
        pooled = self.select(2, worker=raising_member)
        self.assertSameSelection(serial, pooled)

    def test_a_stop_leaves_the_census_and_counts_no_later_observation(self):
        serial = self.select(1, reader=_StoppingReader)
        self.assertEqual(serial['result'], ('V2AuthenticationInputError', 'v2_authentication_input_changed'))
        self.assertFalse(any(GOOD[2] in path for path, _ in serial['census']), 'the serial loop stopped first')
        for worker in (late_firing_member, late_blind_member):
            with self.subTest(worker=worker.__name__):
                pooled = self.select(2, reader=_StoppingReader, worker=worker)
                self.assertSameSelection(serial, pooled)
                self.assertEqual((pooled['firings'], pooled['unavailable']), (0, False))

    def test_a_copy_out_refusal_follows_the_earlier_bundles(self):
        serial = self.select(1, refuse=GOOD[2] + '/summary_metrics.json')
        pooled = self.select(2, refuse=GOOD[2] + '/summary_metrics.json')
        self.assertEqual(serial['result'], ('AnalysisRefusal', 'archive_source_unauthenticated'))
        self.assertSameSelection(serial, pooled)
        self.assertEqual(serial['store'], pooled['store'], 'the earlier bundles were validated')

    def test_consumed_observations_fail_closed(self):
        for worker, key in ((late_firing_member, 'firings'), (late_blind_member, 'unavailable')):
            with self.subTest(worker=worker.__name__):
                pooled = self.select(2, worker=worker)
                self.assertTrue(pooled[key])

    def test_a_test_double_validator_keeps_the_serial_loop(self):
        from joulewise import cli
        with mock.patch.object(cli, 'validate_bundle', side_effect=cli.validate_bundle):
            pooled = self.select(2)
        self.assertFalse(pooled['pooled'])
        self.assertEqual(pooled['result'], sorted(GOOD))


class StepFourMemberTests(unittest.TestCase):
    """L9-SPEEDUP-R2 item 2: a step-4 child's strict validations and nested member pool."""

    @classmethod
    def setUpClass(cls):
        ParallelStepTests.setUpClass.__func__(cls)

    def extract(self, workers, *, worker=None):
        from tests.test_floor_extraction import install_synthetic_recovered_manifest
        from joulewise.whole_window import WholeWindowDriftAllowanceResult
        runs_root = Path(tempfile.mkdtemp(prefix='fe-', dir=self.root))
        ids = (*GOOD, REFUSED, TAMPERED)
        for name in ids[:-1]:
            shutil.copytree(self.bundles[name], runs_root / name)
        # A readable summary that no longer follows from its evidence: strict-invalid.
        shutil.copytree(self.bundles[GOOD[1]], runs_root / TAMPERED)
        summary = json.loads((runs_root / TAMPERED / 'summary_metrics.json').read_bytes())
        summary['decode_latency_s'] += 1.0
        (runs_root / TAMPERED / 'summary_metrics.json').write_text(json.dumps(summary))
        install_synthetic_recovered_manifest(runs_root, list(ids))
        cell = lambda cell_id, members: {'cell_id': cell_id, 'kind': 'absolute', 'metric': 'gross_energy_j',
                                         'window_class': 'request',
                                         'members': [{'slot': m, 'bundle_id': m} for m in members]}
        spec = {'schema_version': fe.EXTRACTION_SPEC_SCHEMA_VERSION,
                'cells': [cell('R2-A', (GOOD[0], GOOD[1], TAMPERED)), cell('R2-B', (GOOD[0], REFUSED, GOOD[2]))]}
        store, observer = {}, DeadlineObserver()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(fe, '_whole_window_extraction_refusals', lambda *a, **k: ()))
            stack.enter_context(mock.patch.object(
                fe, 'whole_window_drift_allowances',
                lambda *a, **k: WholeWindowDriftAllowanceResult('legacy', {})))
            stack.enter_context(ww.shared_instrument_calibration_physics_cache(store))
            caches = stack.enter_context(arc.analysis_run_caches(store, workers=workers))
            caches.deadline = observer
            if worker is not None:
                stack.enter_context(mock.patch.object(member_pool, 'run_member', worker))
            report = fe.extract_cells(runs_root, spec)
            pooled = caches.pool is not None
        report['runs_root'] = '<runs-root>'
        text = json.dumps(report, sort_keys=True).replace(str(runs_root), '<runs-root>')
        return dict(report=text, firings=observer.firings, store=store, pooled=pooled)

    def test_extract_cells_workers_1_and_n_are_identical(self):
        serial = self.extract(1)
        pooled = self.extract(2)
        self.assertEqual((serial['pooled'], pooled['pooled']), (False, True))
        self.assertEqual(serial['report'], pooled['report'])
        self.assertIn('bundle_strict_invalid', serial['report'], 'the tampered member is strict-invalid')
        self.assertEqual((serial['firings'], pooled['firings']), (0, 0))
        self.assertEqual(serial['store'], pooled['store'])
        self.assertEqual(self.extract(2, worker=raising_member)['report'], serial['report'])

    def test_served_validations_count_only_consumed_members(self):
        paths = [self.bundles[name] for name in GOOD]
        with arc.analysis_run_caches({}, workers=2) as caches, \
                mock.patch.object(member_pool, 'run_member', late_firing_member):
            caches.deadline = observer = DeadlineObserver()
            served = fe._served_strict_validator(self.root / RUNS, list(GOOD))
            self.assertIsNotNone(served)
            first = [list(served(path, True)) for path in paths[:2]]
            again = list(served(paths[0], True))
            self.assertEqual(observer.firings, 0, 'the stop: the third bundle was never consumed')
            self.assertEqual(first, [list(fe._default_strict_validator(path, True)) for path in paths[:2]])
            self.assertEqual(again, first[0])
            served(paths[2], True)
            self.assertEqual(observer.firings, 2)
            served(paths[2], True)
            self.assertEqual(observer.firings, 2, 'an outcome is reported once')

    def test_the_schedule_skips_removed_units_and_keeps_first_use_order(self):
        cells = [{'cell_id': 'A', 'kind': 'absolute', 'members': [{'bundle_id': 'b'}, {'bundle_id': 'a'}]},
                 {'cell_id': 'C', 'kind': 'comparative', 'blocks': [
                     {'block_id': 'k1', 'members': {'A1': 'c', 'B1': 'a', 'B2': 'd', 'A2': 'e'}},
                     {'block_id': 'k2', 'members': {'A1': 'x', 'B1': 'y', 'B2': 'z', 'A2': 'w'}}]}]
        self.assertEqual(fe._scheduled_strict_bundle_ids(cells, {'C': {'removed_unit_ids': ['k2']}}),
                         ['b', 'a', 'c', 'd', 'e'])
        self.assertEqual(fe._scheduled_strict_bundle_ids([{'cell_id': 'A'}], {}), [])

    def test_children_get_their_share_of_the_workers(self):
        tasks = [('m:main', [], '4', pack) for pack in ('alpha', 'beta')]
        for workers, expected in ((1, 1), (3, 1), (4, 2), (7, 3)):
            with self.subTest(workers=workers):
                results, _ = parallel.dispatch(tasks, restricted=self.root, first_counter=1, workers=workers,
                                               physics_store={}, worker=member_workers_worker)
                self.assertEqual([r.exit_status for r in results], [expected, expected])
        results, _ = parallel.dispatch([('m:main', [], '1', 'alpha')] * 5, restricted=self.root, first_counter=1,
                                       workers=3, physics_store={}, worker=member_workers_worker)
        self.assertEqual({r.exit_status for r in results}, {1})

    def nested(self, workers, mode='plain'):
        root = Path(tempfile.mkdtemp(prefix='nested-', dir=self.root))
        restricted = root / 'restricted'
        paths = [str(self.bundles[name] / 'metadata.json') for name in GOOD]
        tasks = [('tests.b5_analysis.test_parallel_steps:nested_child_program',
                  [str(root / f'probe-{pack}.json'), mode, *paths], '4', pack) for pack in ('alpha', 'beta')]
        results, state = parallel.dispatch(tasks, restricted=restricted, first_counter=1, workers=workers,
                                           physics_store={})
        probes = [json.loads((root / f'probe-{pack}.json').read_bytes()) for pack in ('alpha', 'beta')]
        logs = [Path(r.stdout_path).read_text() for r in results]
        return results, probes, logs

    def test_a_step_4_child_runs_a_nested_spawn_pool(self):
        # Python 3.13 spawn pools nest: a pool worker (the child) owns its own pool.
        serial, serial_probes, serial_logs = self.nested(1)
        pooled, pooled_probes, pooled_logs = self.nested(4)
        self.assertEqual([p['pooled'] for p in serial_probes], [False, False])
        self.assertEqual([p['pooled'] for p in pooled_probes], [True, True])
        for probe in pooled_probes:
            self.assertNotIn(probe['child'], probe['members'], 'members ran in grandchild processes')
        self.assertEqual(serial_logs, pooled_logs)
        self.assertEqual([(r.exit_status, r.exception, r.firings) for r in serial],
                         [(r.exit_status, r.exception, r.firings) for r in pooled])
        self.assertEqual([r.firings for r in pooled], [0, 0])

    def test_a_child_whose_member_worker_cannot_observe_reports_none(self):
        results, probes, _ = self.nested(4, mode='blind')
        self.assertEqual([p['pooled'] for p in probes], [True, True])
        self.assertEqual([r.firings for r in results], [None, None], 'the driver refuses the step')


if __name__ == '__main__':
    unittest.main()
