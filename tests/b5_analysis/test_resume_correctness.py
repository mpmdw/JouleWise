"""Bounded synthetic regressions from the executing review of bd4e141a9 (local Sol 6.1, reviewed by the lead)."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import powermetrics_fiducial as pf
from joulewise.b5_analysis import dry_run as d, parallel, resume as R
from tests.b5_analysis import test_dry_run as base, test_resume as recovery
from tests.b5_analysis.test_shared_physics_cache import JumpingClock


def synthetic_reduce(argv):
    """Tiny deterministic reducer wire; all control/registration code stays real."""
    Path(argv[argv.index('--output') + 1]).write_bytes(b'{}\n')
    return 0


def synthetic_worker(task):
    runner = d.StepRunner(Path(task.restricted))
    runner._counter = task.counter - 1
    result = runner.run(synthetic_reduce, list(task.argv), step=task.step, window=task.window)
    return parallel.ChildResult(result.exit_status, str(result.stdout_path), str(result.stderr_path),
                                result.exception, 0, {})


def unavailable_worker(task):
    if task.window != 'alpha':
        return synthetic_worker(task)
    runner = d.StepRunner(Path(task.restricted))
    runner._counter = task.counter - 1
    result = runner.run(lambda argv: 2, list(task.argv), step=task.step, window=task.window)
    return parallel.ChildResult(result.exit_status, str(result.stdout_path), str(result.stderr_path),
                                result.exception, None, {})


class RebuildRefusalDouble(base.DriverDouble):
    def run(self, main, argv, *, step, window=None, stdout_path=None):
        if (getattr(main, '_operation', None) == 'prepare_brackets'
                and self.restricted.name == 'rebuild'):
            return d.StepRunner.run(self, lambda argv: 2, argv, step=step, window=window)
        return super().run(main, argv, step=step, window=window, stdout_path=stdout_path)


class OutcomeFiringDouble(base.DriverDouble):
    attempts = 0

    def run(self, main, argv, *, step, window=None, stdout_path=None):
        if step == '6':
            type(self).attempts += 1
            if type(self).attempts == 1:
                evidence, raw, events = recovery.FiringDouble.evidence
                with mock.patch.object(pf, 'time', JumpingClock()):
                    try:
                        pf.verify_stored_evidence_physics(evidence, raw, events)
                    except ValueError:
                        pass
        return super().run(main, argv, step=step, window=window, stdout_path=stdout_path)


class RecoveryCorrectnessTests(recovery.ResumeTests):
    for name in [n for n in dir(recovery.ResumeTests) if n.startswith('test_')]:
        locals()[name] = None
    del name

    def crash_boundary(self, position, *, runner=base.DriverDouble):
        original = R.Checkpoints.write

        def write(checkpoints, s, r, **kwargs):
            original(checkpoints, s, r, **kwargs)
            if kwargs['position'] == position:
                raise KeyboardInterrupt('synthetic boundary crash')
        with mock.patch.object(R.Checkpoints, 'write', write):
            return self.crash(_runner=runner, workers=1)

    def test_complete_record_still_rehashes_checkpointed_files(self):
        with mock.patch.object(R.Checkpoints, 'finish', side_effect=KeyboardInterrupt):
            custody = self.crash(_runner=base.DriverDouble, workers=1)
        restricted = custody / 'dry-run/restricted'
        checkpoint = json.loads((restricted / R.RESUME_DIR / R.CHECKPOINT).read_bytes())
        name = next(name for name in checkpoint['files'] if not name.startswith('logs/'))
        (restricted / name).write_bytes(b'changed synthetic file\n')
        resumed = self.execute(custody=custody, resume=True, workers=1)
        self.assertEqual(resumed['code'], 2)
        self.assertIn('resume refused: checkpointed_file_differs', resumed['stderr'])

    def test_resume_after_checkpoint_cleanup_reports_the_complete_run(self):
        reference = self.execute(workers=1)
        resumed = self.execute(custody=reference['custody'], resume=True, workers=1)
        self.assertEqual((resumed['code'], resumed['raw']), (reference['code'], reference['raw']))
        self.assertIn('resume: run already complete', resumed['stderr'])
        self.assertEqual(recovery.tree(resumed['restricted']), recovery.tree(reference['restricted']))

    def test_a_refused_rebuild_cannot_restore_a_successful_checkpoint(self):
        custody = self.crash_boundary(5)
        resumed = self.execute(custody=custody, resume=True, runner=RebuildRefusalDouble, workers=1)
        self.assertEqual(resumed['code'], 2)
        self.assertIsNone(resumed['raw'])
        self.assertIn('resume refused: rebuilt_builder_refused', resumed['stderr'])

    def test_release_resume_at_each_boundary_is_byte_identical(self):
        def release(custody, **options):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = d.run('release', self.index, custody, workers=1,
                             _test_pack_table=self.table, _test_repo_root=self.repo,
                             _runner=base.DriverDouble, _git=lambda repo: 'b' * 40, **options)
            output = custody / 'release/B5-RELEASE-RECORD.json'
            return code, output.read_bytes() if output.exists() else None

        dry = self.execute(workers=1)
        reference = release(dry['custody'])
        self.assertEqual(reference[0], 0)
        original = R.Checkpoints.write
        for boundary in (0, 1, 5, 8, len(d.STEPS)):
            with self.subTest(boundary=boundary):
                fresh = self.execute(workers=1)

                def write(checkpoints, s, runner, **kwargs):
                    original(checkpoints, s, runner, **kwargs)
                    if kwargs['position'] == boundary:
                        raise KeyboardInterrupt
                with mock.patch.object(R.Checkpoints, 'write', write), self.assertRaises(KeyboardInterrupt):
                    release(fresh['custody'])
                self.assertEqual(release(fresh['custody'], resume=True), reference)
                self.assertEqual(recovery.tree(fresh['custody'] / 'release/restricted'),
                                 recovery.tree(dry['custody'] / 'release/restricted'))

    def test_release_resume_cannot_bypass_a_failed_dry_run_preamble(self):
        dry = self.execute(workers=1)
        original = R.Checkpoints.write

        def release(**options):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                return d.run('release', self.index, dry['custody'], workers=1,
                             _test_pack_table=self.table, _test_repo_root=self.repo,
                             _runner=base.DriverDouble, _git=lambda repo: 'b' * 40, **options)

        def write(checkpoints, s, runner, **kwargs):
            original(checkpoints, s, runner, **kwargs)
            if kwargs['position'] == 1:
                raise KeyboardInterrupt
        with mock.patch.object(R.Checkpoints, 'write', write), self.assertRaises(KeyboardInterrupt):
            release()
        record = json.loads(dry['raw'])
        record['schema_version'] = 'invalid_synthetic_record'
        dry['path'].write_bytes(d._canonical(record))
        self.assertEqual(release(resume=True), 2)
        self.assertFalse((dry['custody'] / 'release/B5-RELEASE-RECORD.json').exists())

    def test_skipped_checkpoint_then_resume_uses_the_last_durable_boundary(self):
        reference = self.execute(workers=1)
        original = R._atomic

        def atomic(path, raw):
            if json.loads(raw)['position'] == 5:
                raise OSError('synthetic checkpoint write failure')
            original(path, raw)

        recovery.CrashingDouble.count = 0
        # Crash during step 4, after the checkpoint after step 3b was skipped.
        recovery.CrashingDouble.crash_at = next(
            i for i, row in enumerate(base.DriverDouble.calls, 1) if row[0] == '4')
        with mock.patch.object(R, '_atomic', atomic):
            custody = self.crash(_runner=recovery.CrashingDouble, workers=1)
        recovery.CrashingDouble.crash_at = None
        self.assertSameRun(reference, self.execute(custody=custody, resume=True, workers=1))


class OutcomeRetryTests(recovery.RetryTests):
    for name in [n for n in dir(recovery.RetryTests) if n.startswith('test_')]:
        locals()[name] = None
    del name

    def test_a_firing_is_retried_whatever_the_attempt_would_have_decided(self):
        # Lead ruling (review of the executing critique): the retry decision reads only
        # the host signal. Not retrying when the masked attempt held an outcome would
        # make retry-or-not (visible as a structure-tier step_retry event) reveal it.
        base.DriverDouble.outcome = True
        reference = self.execute(workers=1)
        self.assertEqual(reference['code'], 3)
        OutcomeFiringDouble.attempts = 0
        result = self.execute(runner=OutcomeFiringDouble, workers=1)
        self.assertEqual(OutcomeFiringDouble.attempts, 2)
        self.assertEqual((result['code'], result['raw']), (reference['code'], reference['raw']))
        self.assertEqual([(row['step'], row['attempt']) for row in self.retries(result) if row['event'] == 'step_retry'],
                         [('6', 1)])

    def test_a_skipped_checkpoint_disables_retry_from_an_older_boundary(self):
        original = R._atomic

        def atomic(path, raw):
            if json.loads(raw)['position'] == 2:
                raise OSError('synthetic checkpoint write failure')
            original(path, raw)
        recovery.FiringDouble.fire, recovery.FiringDouble.attempts = 1, 0
        with mock.patch.object(R, '_atomic', atomic):
            result = self.execute(runner=recovery.FiringDouble, workers=1)
        self.assertEqual(result['code'], 2)
        self.assertEqual(recovery.FiringDouble.attempts, len(d.PACKS))
        events = self.retries(result)
        self.assertTrue(any(row['event'] == 'checkpoint_skipped' for row in events))
        self.assertFalse(any(row['event'] == 'step_retry' for row in events))


class ParallelRecoveryTests(unittest.TestCase):
    def test_plain_runner_stop_cleanup_and_counter_survive_retry_and_resume(self):
        with tempfile.TemporaryDirectory(prefix='solc-parallel-') as tmp:
            root = Path(tmp)
            repo = root / 'repo'
            repo.mkdir()
            index = root / 'index.json'
            index.write_bytes(b'{}\n')
            bundles = []
            for pack in ('alpha', 'beta'):
                bundle = root / pack
                bundle.mkdir()
                (bundle / 'summary_metrics.json').write_bytes(b'{}\n')
                bundles.append((pack, 'kept', bundle))
            steps = [(step, d.step_2 if step == '2' else
                      (lambda s, r, step=step: [s.record(step)])) for step in d.STEP_IDS]

            def go(name, worker, *, resume=False, crash=False):
                def reduce_step(s, r):
                    rows = d.step_2(s, r)
                    if crash:
                        raise KeyboardInterrupt
                    return rows
                selected = [(step, reduce_step if step == '2' else fn) for step, fn in steps]
                with mock.patch.object(d, 'STEPS', selected), \
                        mock.patch.object(d.RunState, 'prepare_initial', lambda s, argv: 0), \
                        mock.patch.object(d.RunState, 'prepare_kept', lambda s, argv: 0), \
                        mock.patch.object(d.RunState, 'kept_bundles', lambda s: iter(bundles)), \
                        mock.patch.object(d, 'validate_dry_run_record'), \
                        mock.patch.object(d, '_record_parts', return_value=([], [], [])), \
                        mock.patch.object(parallel, 'run_child', worker), \
                        mock.patch('joulewise.cli.main', synthetic_reduce), \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    code = d.run('blind-dry-run', index, root / name, workers=2, resume=resume,
                                 _test_repo_root=repo, _git=lambda repo: 'b' * 40)
                output = root / name / 'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
                restricted = output.parent / 'restricted'
                return code, output.read_bytes(), recovery.tree(restricted)

            reference = go('reference', synthetic_worker)
            retried = go('retried', unavailable_worker)
            self.assertEqual(reference[0], 0)
            self.assertEqual(retried, reference)
            with self.assertRaises(KeyboardInterrupt):
                go('resumed', synthetic_worker, crash=True)
            self.assertEqual(go('resumed', synthetic_worker, resume=True), reference)

    def test_merged_census_uses_the_record_key_and_order(self):
        old = [{'window': 'beta', 'path': 'derived/b.json', 'sha256': 'b' * 64, 'check': 'harvest_outputs'},
               {'window': 'alpha', 'path': 'derived/a.json', 'sha256': 'a' * 64, 'check': 'harvest_outputs'}]
        current = [dict(old[1]), {'window': 'gamma', 'path': 'sources/a.json',
                                'sha256': 'c' * 64, 'check': 'sources_sha256sums'}]
        self.assertEqual(R.merged_census(current, {'parts': {'census': old}}),
                         [old[1], old[0], current[1]])

    def test_step11_roster_cache_changes_without_changing_record_parts(self):
        from joulewise import whole_window as ww
        from joulewise.b5_analysis import context as ctx
        from joulewise.b5_analysis.archive import ArchiveHandle
        with tempfile.TemporaryDirectory(prefix='solc-state-') as tmp:
            root = Path(tmp)
            window = SimpleNamespace(pack='gamma', pack_id='synthetic', plan_id='synthetic-plan', attempt=1,
                                     archive_root=root, claim_runs_root=root / 'runs',
                                     harvest_record_sha256='a' * 64, harvest_pin='a' * 40,
                                     record=SimpleNamespace(record_shape='pin4',
                                                            entry=SimpleNamespace(superseded_archive_roots=())))
            roster = {'schema': 'joulewise.b5_harvest_roster.v1', 'pack_id': window.pack_id,
                      'plan_id': window.plan_id, 'attempt': 1, 'members': []}
            tree_name = 'repo/configs/campaigns/synthetic/plan_tree.json'
            tree = root / 'sources' / tree_name
            tree.parent.mkdir(parents=True)
            tree.write_bytes(b'{}\n')
            (root / 'sources/SHA256SUMS').write_text(d._sha(tree) + '  ' + tree_name + '\n')
            (root / 'derived').mkdir()
            roster_path = root / 'derived/roster.json'
            roster_path.write_bytes(d._canonical(roster))
            archive = ArchiveHandle(window, {'outputs': {'derived/roster.json': d._sha(roster_path)}}, {},
                                    synthetic_plan_tree_sha256=d._sha(tree))
            archive.source_bytes('sources/' + tree_name)
            archive.output_bytes('derived/roster.json')
            s = d.RunState('blind-dry-run', root / 'index.json', root / 'restricted', 'a' * 40)
            s.windows, s.archives = {'gamma': window}, {'gamma': archive}
            s.rows = {'gamma': {'idle_admission_core': {'conditions': []}, 'evaluation_basis': {'sha256': 'a' * 64},
                                'status': 'passed', 'excluded_bundles': []}}
            s.kept = {'gamma': SimpleNamespace(cells={})}
            s.contexts = {'gamma': SimpleNamespace(removed_bundle_ids=frozenset(), sources_replay=None)}
            before = R.state_parts(s)
            self.assertFalse(hasattr(archive, '_rebuilt_roster_bindings'))
            with mock.patch.object(ctx.harvest, 'build_roster', return_value=roster), \
                    mock.patch.object(ctx.harvest, 'l4_exclusion_inputs', return_value=(roster, {})), \
                    mock.patch.object(ww, '_validated_evaluation_basis', return_value={'member_occurrences': []}), \
                    mock.patch.object(ctx, 'read_screen_record', return_value={'rescreen': {'survivors': {}}}), \
                    mock.patch.object(ctx, '_excluded', return_value={}), \
                    mock.patch.object(ctx, 'survivor_set', return_value=SimpleNamespace(bundle_ids=frozenset())), \
                    mock.patch.object(d, 'require_primary_context'), \
                    mock.patch.object(ww, 'AuthenticatedConsumptionSession'), \
                    mock.patch('joulewise.analysis_engine.inputs.archive_snapshot', return_value={}), \
                    mock.patch.object(ww, 'validate_whole_window_verdict_row',
                                      return_value=SimpleNamespace(admitted=True, answered_conditions=())):
                first = d._step_results(s)
                second = d._step_results(s)
            self.assertEqual(first, second)
            self.assertEqual(len(archive._rebuilt_roster_bindings), 2)
            self.assertEqual(R.state_parts(s), before)
