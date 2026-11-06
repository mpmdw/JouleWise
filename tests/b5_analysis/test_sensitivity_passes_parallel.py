"""Small synthetic step-11 passes: ordered effects, refusals and nested budgets."""
from concurrent.futures import Future
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import pickle
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise.authentication_io import V2AuthenticationReadSession, read_authentication_input
from joulewise.b5_analysis import dry_run, pack_parallel as pp, sensitivity as sm
from joulewise.b5_analysis.archive import ArchiveHandle, CensusRow
from joulewise.b5_analysis.bracket import BMax
from joulewise.b5_analysis.context import _SourcesReplay
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from tests.b5_analysis.test_sensitivity import pass_fixture


def touch(archive, label, stage):
    relative = 'sources/' + label + '-' + stage + '.json'
    archive.source_bytes(relative)
    read_authentication_input(archive.window.archive_root / relative,
                              grammar='json', label='synthetic sensitivity input')


def pass_label(context, bound):
    return 'widened' if context.sensitivity_bound_s > bound else 'primary'


def project_fixture(spec, kept, *, context, **kwargs):
    label = pass_label(context, spec['bound'])
    touch(context.sources_replay.archive, label, 'project')
    if label == 'widened' and spec['mode'] in ('both_refuse', 'second_refuses'):
        raise sm.AnalysisRefusal('synthetic_second_pass_refused')
    result = deepcopy(spec['projection'])
    delta = context.sensitivity_bound_s - spec['bound']
    for cell in result['cells']:
        cell['interval']['B_j'] += delta
        cell['lower_j'] -= delta
        cell['upper_j'] += delta
        cell['attribution_floor']['value_j'] += delta
    return result


def extract_fixture(root, spec, *, archive_context, **kwargs):
    touch(archive_context.sources_replay.archive, pass_label(archive_context, spec['bound']), 'extract')
    result = deepcopy(spec['report'])
    for cell in result['cells']:
        cell['floor']['drift_widened_guarded_floor_j'] += archive_context.sensitivity_bound_s - spec['bound']
    return result


def contrasts_fixture(*, gamma_manifest_path, archive_contexts, gamma_archive, **kwargs):
    config = json.loads(read_authentication_input(Path(gamma_manifest_path),
        grammar='json', label='synthetic sensitivity contrasts'))
    gamma = archive_contexts[str(gamma_archive.window.claim_runs_root.resolve())]
    label = pass_label(gamma, config['bound'])
    # These effects occur after derive_pack returned its census. Include all
    # three replay archives and a distinct, explicitly supplied GAMMA handle.
    for context in archive_contexts.values():
        touch(context.sources_replay.archive, label, 'contrasts')
    touch(gamma_archive, label, 'gamma')
    if label == 'primary' and config['mode'] in ('both_refuse', 'first_refuses'):
        raise sm.AnalysisRefusal('synthetic_first_pass_refused')
    result = deepcopy(config['contrasts'])
    if label == 'widened':
        for row in result:
            row['deterministic_bounds']['total'] += .1
    return result


CONSUMERS = sm.SensitivityConsumers(project_fixture, extract_fixture, contrasts_fixture)
SERIAL_PASS = sm.sensitivity_pass
RUN_PACK = pp.run_pack


def fixture_pass(*args, **kwargs):
    # Exercise the genuine inner derive_pack scheduling guard with picklable
    # arithmetic consumers. Production defaults and the custody calls stay put.
    with mock.patch.object(sm, '_DEFAULT_CONSUMERS', CONSUMERS):
        return SERIAL_PASS(*args, **kwargs, consumers=CONSUMERS)


def fixture_worker(task):
    with mock.patch.object(sm, 'sensitivity_pass', fixture_pass):
        return RUN_PACK(task)


def failed_transport_worker(task):
    outcome = fixture_worker(task)
    if task.function.endswith(':sensitivity_pass_pack'):
        args, _ = pp.loads(task.payload)
        if args[4].value_s > 0:
            return replace(outcome, ok=False, value=None)
    return outcome


def unconsumed_deadline_worker(task):
    outcome = fixture_worker(task)
    if task.function.endswith(':sensitivity_pass_pack'):
        args, _ = pp.loads(task.payload)
        if args[4].value_s > 0:
            return replace(outcome, firings=3)
    return outcome


class SensitivityPassesParallelTests(unittest.TestCase):
    def state(self, root, mode='ok', *, shared_gamma=False):
        base = pass_fixture()
        windows, contexts, archives = {}, {}, {}
        kept, brackets, specs = {}, {}, deepcopy(base.specs)
        for pack, old in base.windows.items():
            window = replace(old, archive_root=root / pack / 'archive',
                             claim_runs_root=root / pack / 'runs', custody_root=root)
            windows[pack] = window
            archive = ArchiveHandle(window, {}, {})
            archives[pack] = archive
            contexts[pack] = replace(base.contexts[pack], neg8_harvest_archive=window.archive_root,
                                     sources_replay=_SourcesReplay(archive, None))
            kept[pack] = replace(base.kept[pack], window=window)
            brackets[pack] = replace(base.brackets[pack], window=window)
            sources = window.archive_root / 'sources'
            sources.mkdir(parents=True, exist_ok=True)
            names = [label + '-' + stage + '.json' for label in ('primary', 'widened')
                     for stage in ('project', 'extract', 'contrasts', 'gamma')]
            for name in names:
                (sources / name).write_text('{}')
            digest = hashlib.sha256(b'{}').hexdigest()
            (sources / 'SHA256SUMS').write_text(''.join(digest + '  ' + name + '\n' for name in names))
            if pack != 'gamma':
                specs[pack].update(bound=brackets[pack].b_fiducial_s, mode=mode,
                                   projection=base.projections[pack], report=base.reports[pack])
        if not shared_gamma:
            archives['gamma'] = ArchiveHandle(windows['gamma'], {}, {})
        # Pre-existing rows must survive merges on both distinct handles.
        for pack, context in contexts.items():
            row = CensusRow('initial/' + pack, 'a' * 64, 'input_census')
            context.sources_replay.archive._census[row.path] = row
        row = CensusRow('initial/explicit-gamma', 'b' * 64, 'input_census')
        archives['gamma']._census[row.path] = row
        verdicts = {'schema_version': 'joulewise.claim_verdicts.v1', 'contrasts': [{
            'contrast_id': 'synthetic', 'floor': {'status': 'resolved', 'floor_abs_j': 1.1,
                'floor_cmp_j': 1.25, 'active_floor_j': 1.25,
                'resolutions': [{'status': 'exact', 'source_cell_ids': ['minted-alpha', 'minted-beta']}]},
            'estimator': {'estimate': 3.}, 'multiplicity': {'rejected': True},
            'deterministic_bounds': {'total': 2.6}, 'claim_evaluation': {'outcome': 'direction_supported'}}]}
        manifest = root / 'manifest.json'
        manifest.write_text(json.dumps(dict(verdicts, mode=mode, bound=brackets['gamma'].b_fiducial_s)))
        values = {'projection_' + p: v for p, v in base.projections.items()}
        values.update({'extraction_' + p: v for p, v in base.reports.items()})
        values.update(floor_artifact=base.artifact, claim_verdicts=verdicts)
        paths = {'finalized_manifest': manifest, 'floor_artifact': root / 'floor.json'}
        writes = []
        return SimpleNamespace(windows=windows, contexts=contexts, archives=archives, kept=kept,
            brackets=brackets, specs=specs, b_max=BMax(.05, 456, 500), read=values.__getitem__,
            output=paths.__getitem__, evidence_roots=lambda: {
                'root-' + p: windows[p].claim_runs_root for p in ('alpha', 'beta')},
            write=lambda *args, **kwargs: writes.append((args, kwargs)), writes=writes)

    def run_case(self, root, workers, mode='ok', *, switch='on', worker=fixture_worker,
                 shared_gamma=False):
        state = self.state(root, mode, shared_gamma=shared_gamma)
        batches = []
        pack_map = pp.pack_map

        def schedule(function, calls):
            outcomes = pack_map(function, calls)
            batches.append((function.__name__, outcomes))
            return outcomes

        with arc.analysis_run_caches({}, workers=workers) as caches, \
                V2AuthenticationReadSession() as session, \
                mock.patch.dict('os.environ', {pp.PACK_PARALLEL_ENV: switch}), \
                mock.patch.object(pp, 'run_pack', worker), \
                mock.patch.object(pp, 'pack_map', side_effect=schedule), \
                mock.patch.object(sm, 'sensitivity_pass', fixture_pass), \
                mock.patch.object(dry_run, '_step_results', return_value={'synthetic': True}):
            caches.deadline = DeadlineObserver()
            try:
                status = dry_run._sensitivity(state, [])
            except sm.AnalysisRefusal as exc:
                status = exc.code
            result = (status, state.writes,
                      {p: a.census() for p, a in state.archives.items()},
                      {p: c.sources_replay.archive.census() for p, c in state.contexts.items()},
                      tuple(vars(row) for row in session.records.values()),
                      caches.deadline.firings, caches.worker_observer_unavailable)
        outer = next(outcomes for name, outcomes in batches if name == 'sensitivity_pass_pack')
        return result, outer

    def test_parallel_records_and_all_archive_and_read_censuses_equal_serial(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-passes-') as tmp:
            for shared in (False, True):
                root = Path(tmp)
                serial, _ = self.run_case(root, 1, shared_gamma=shared)
                parallel, outcomes = self.run_case(root, 3, shared_gamma=shared)
                self.assertEqual(serial, parallel)
                self.assertEqual(json.dumps(serial[1], sort_keys=True),
                                 json.dumps(parallel[1], sort_keys=True))
                self.assertTrue(all(outcome.ok for outcome in outcomes))
                self.assertEqual(parallel[0], 0)
                self.assertEqual([args[0] for args, _ in parallel[1]], ['sensitivity', 'step_results'])
                self.assertEqual(parallel[1][0][0][2]['b_max']['value_s'], .05)
                for census in parallel[3].values():
                    self.assertTrue(any(row.path == 'sources/primary-contrasts.json' for row in census))
                    self.assertTrue(any(row.path == 'sources/widened-contrasts.json' for row in census))

    def test_first_refusal_wins_with_identical_partial_state(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-pass-refusal-') as tmp:
            for mode in ('both_refuse', 'first_refuses'):
                serial, _ = self.run_case(Path(tmp), 1, mode)
                parallel, outcomes = self.run_case(Path(tmp), 3, mode, worker=unconsumed_deadline_worker)
                self.assertEqual(serial, parallel)
                self.assertEqual(parallel[0], 'synthetic_first_pass_refused')
                self.assertFalse(outcomes[0].ok)
                self.assertEqual(outcomes[1].ok, mode == 'first_refuses')
                self.assertEqual(outcomes[1].firings, 3)
                self.assertEqual(parallel[5], 0)
                self.assertEqual(parallel[1], [])
                self.assertFalse(any('widened' in row['normalized_path'] for row in parallel[4]))

    def test_second_refusal_retains_consumed_first_pass(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-second-refusal-') as tmp:
            serial, _ = self.run_case(Path(tmp), 1, 'second_refuses')
            parallel, outcomes = self.run_case(Path(tmp), 3, 'second_refuses')
            self.assertEqual(serial, parallel)
            self.assertEqual(parallel[0], 'synthetic_second_pass_refused')
            self.assertTrue(outcomes[0].ok)
            self.assertFalse(outcomes[1].ok)
            self.assertEqual(parallel[1], [])

    def test_failed_worker_transport_recomputes_at_its_position(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-pass-transport-') as tmp:
            serial, _ = self.run_case(Path(tmp), 1)
            fallback, outcomes = self.run_case(Path(tmp), 3, worker=failed_transport_worker)
            self.assertEqual(serial, fallback)
            self.assertTrue(outcomes[0].ok)
            self.assertFalse(outcomes[1].ok)
            with mock.patch.object(pp, 'dumps', side_effect=pickle.PicklingError('synthetic transport')):
                fallback, outcomes = self.run_case(Path(tmp), 3)
            self.assertIsNone(outcomes)
            self.assertEqual(serial, fallback)

    def test_operator_switch_preserves_serial_fallback(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-pass-switch-') as tmp:
            serial, _ = self.run_case(Path(tmp), 1)
            for switch in ('off', 'derive_pack', 'sensitivity_pass_pack'):
                actual, outcomes = self.run_case(Path(tmp), 3, switch=switch)
                self.assertEqual(serial, actual)
                self.assertEqual(outcomes is None, switch != 'sensitivity_pass_pack')

    def test_nested_derivations_subdivide_each_pass_worker_share(self):
        tasks = []

        class InlinePool:
            def __init__(self, **kwargs):
                pass

            def submit(self, function, task):
                tasks.append(task)
                future = Future()
                future.set_result(function(task))
                return future

            def shutdown(self, **kwargs):
                pass

        with tempfile.TemporaryDirectory(prefix='sensitivity-pass-budget-') as tmp, \
                mock.patch('concurrent.futures.ProcessPoolExecutor', InlinePool):
            result, outcomes = self.run_case(Path(tmp), 7)
        self.assertEqual(result[0], 0)
        self.assertTrue(all(outcome.ok for outcome in outcomes))
        self.assertEqual([t.workers for t in tasks if t.function.endswith(':sensitivity_pass_pack')], [3, 4])
        self.assertEqual([t.workers for t in tasks if t.function.endswith(':derive_pack')], [1, 2, 2, 2])


if __name__ == '__main__':
    unittest.main()
