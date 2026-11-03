"""D-188 SHIP: moving verified-store entries between the driver, member pools and children.

Synthetic leaves and temporary trees only (plus the driver run with stub steps).
What is checked:

* the member-worker split (Sol #1: never 0 workers per child, leftover to the last);
* member pools: worker fills merge only from consumed, ok, firing-free outcomes;
  a pre-filtered hit is not dispatched and is applied (rows registered through
  the consumer session) only at its consumption, so an unconsumed hit leaves no
  trace (Sol #2); a shadow-sampled hit is dispatched and recomputed; a pool stays
  serial while a fill is recorded;
* the persistent defect channel (Sol #11): a defect of an unconsumed outcome or
  of a discarded child still reaches the run's store; a blind run only counts it;
* children: entries merge only from the consumed, firing-free prefix after the
  driver's serial stop; an unobservable child still refuses and merges nothing;
* step codes (Sol #12): restricted/decisions/step-codes.jsonl rows carry exactly
  the comparator's keys, the raw code before redaction and the caught exception
  class, and are bound in the record (the comparator authenticates them); the
  resolved store mode is bound as a fixed token.
"""
from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_member_pool as pool, analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise.authentication_io import V2AuthenticationReadSession, read_authentication_input
from joulewise.b5_analysis import dry_run as d, parallel
from joulewise.b5_analysis.deadline_observer import OBSERVER_UNAVAILABLE
from joulewise.b5_analysis.windows import AnalysisRefusal

MODULE = __name__
ROOT = Path(__file__).resolve().parents[2]
INSIDE_CALLS: list = []


def setUpModule():
    # As test_member_pool: spawn re-imports __main__ from its file.
    main = sys.modules['__main__']
    path = getattr(main, '__file__', None)
    if path is not None and not os.path.isfile(path):
        del main.__file__
        unittest.addModuleCleanup(setattr, main, '__file__', path)


def ship_leaf(path, factor):
    """A synthetic leaf: authenticated reads in a fixed order, a pure JSON-shaped value."""
    root = Path(path)
    meta = read_authentication_input(root / 'meta.json', grammar='json', label='ship meta')
    raw = read_authentication_input(root / 'data.bin', grammar='raw', label='ship data')
    return {'factor': factor, 'size': len(raw), 'meta': len(meta)}


def pool_inside_leaf(path, factor):
    """A leaf whose body asks for a member pool: it must stay serial (the fill records reads)."""
    return pool.member_map(ship_leaf, INSIDE_CALLS) is None


SPEC = vdl.LeafSpec('T_ship', (f'{MODULE}:ship_leaf',), (('path', vdl.TREE), ('factor', vdl.SCALAR)))
INSIDE_SPEC = vdl.LeafSpec('T_ship_inside', (f'{MODULE}:pool_inside_leaf',),
                           (('path', vdl.TREE), ('factor', vdl.SCALAR)))


def registering_worker(task):
    """Member-pool worker: the synthetic leaf is registered in the spawned process too."""
    with vdl._registered(SPEC):
        return pool.run_member(task)


def firing_registering_worker(task):
    with vdl._registered(SPEC):
        return dataclasses.replace(pool.run_member(task), firings=2)


def defect_on_last_worker(task):
    """Every task fills; the one for 'm3' also reports a store defect (as a shadow mismatch would)."""
    with vdl._registered(SPEC):
        outcome = pool.run_member(task)
    if str(task.args[0]).endswith('m3'):
        payload = dict(outcome.vdl_new)
        payload['defects'] = ['shadow_mismatch']
        outcome = dataclasses.replace(outcome, vdl_new=payload)
    return outcome


def blind_defect_on_last_worker(task):
    """A blind worker counts its defect instead of listing it."""
    with vdl._registered(SPEC):
        outcome = pool.run_member(task)
    if str(task.args[0]).endswith('m3'):
        payload = dict(outcome.vdl_new)
        payload['counters'] = {**payload.get('counters', {}), 'defect:shadow_mismatch': 1}
        outcome = dataclasses.replace(outcome, vdl_new=payload)
    return outcome


def side_channel_child(task):
    """Child stand-in: reports its store context and, for beta, a defect."""
    payload = {'schema': vdl.SCHEMA, 'entries': {}, 'poisoned': [],
               'defects': ['shadow_mismatch'] if task.window == 'beta' else [], 'counters': {'x:fill': 1}}
    return parallel.ChildResult(0, '', '', False, 0, {}, vdl_new=payload)


def context_child(task):
    """Child stand-in: echoes what it was shipped (mode token and entry count)."""
    context = task.vdl or {}
    mode = context.get('mode')
    entries = (context.get('entries') or {}).get('entries') or {}
    return parallel.ChildResult(len(entries), json.dumps(None if mode is None else d.vdl_mode_token(mode)), '',
                                False, 0, {})


def filling_child(task):
    """Child stand-in: one real fill of the synthetic leaf on its argv tree, exported as a child would."""
    with vdl._registered(SPEC), arc.analysis_run_caches({}, vdl_mode=task.vdl['mode']) as caches:
        caches.deadline = FakeDeadline()
        caches.vdl.call('T_ship', ship_leaf, task.argv[0], 3)
        payload = pool.export_new(caches, task.vdl, {})
    return parallel.ChildResult(0, '', '', False, 0, {}, vdl_new=payload)


class FakeDeadline:
    def __init__(self):
        self.firings = 0


@contextlib.contextmanager
def run_caches(mode=vdl.ON, workers=2):
    with arc.analysis_run_caches({}, workers=workers, vdl_mode=mode) as caches:
        caches.deadline = FakeDeadline()
        yield caches


def records(session):
    return [(r.normalized_path, r.sha256, r.grammar, r.read_count, r.strict_parse_succeeded)
            for r in session.records.values()]


class _Trees(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='vdl-ship-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        registration = vdl._registered(SPEC, INSIDE_SPEC)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.trees = []
        for index, name in enumerate(('m1', 'm2', 'm3')):
            root = self.tmp / name
            root.mkdir()
            (root / 'meta.json').write_text('{"m": %d}' % index)
            (root / 'data.bin').write_bytes(b'x' * (index + 1))
            self.trees.append(root)
        self.calls = [((str(tree), 3), {}) for tree in self.trees]

    def serial(self, trees):
        session = V2AuthenticationReadSession()
        with session:
            values = [ship_leaf(str(tree), 3) for tree in trees]
        return values, records(session)

    def pooled(self, worker=registering_worker, *, limit=None, dispatch=True):
        """As a whole-window caller: map inside the session, consume (and account) in order."""
        session = V2AuthenticationReadSession()
        with session:
            if dispatch:
                outcomes = pool.member_map(ship_leaf, self.calls, worker=worker, account=False)
            else:
                with mock.patch.object(pool, '_pool', side_effect=AssertionError('a hit was dispatched')):
                    outcomes = pool.member_map(ship_leaf, self.calls, worker=worker, account=False)
            values = [pool.consume(outcome, lambda tree=tree: ship_leaf(str(tree), 3), account=True)
                      for outcome, tree in list(zip(outcomes, self.trees))[:limit]]
        return outcomes, values, records(session)

    def entries(self, caches):
        return caches.vdl.export_entries()['entries']


class WorkerShareTests(unittest.TestCase):
    def test_leftover_goes_to_the_last_child_and_no_child_gets_zero(self):
        self.assertEqual(parallel.member_worker_shares(3, 2), [1, 2])
        self.assertEqual(parallel.member_worker_shares(4, 2), [2, 2])
        self.assertEqual(parallel.member_worker_shares(7, 2), [3, 4])
        self.assertEqual(parallel.member_worker_shares(1, 2), [1, 1])
        self.assertEqual(parallel.member_worker_shares(3, 5), [1] * 5)
        self.assertEqual(parallel.member_worker_shares(7, 262), [1] * 262)  # Sol #1: step 1's 262 bundles
        for workers in range(1, 10):
            for count in (1, 2, 3, 7, 262):
                shares = parallel.member_worker_shares(workers, count)
                self.assertEqual(len(shares), count)
                self.assertTrue(all(share >= 1 for share in shares))
                self.assertEqual(sum(shares), max(workers, count) if count <= workers else count)

    def test_every_share_is_a_valid_run_cache_worker_count(self):
        for share in parallel.member_worker_shares(7, 262) + parallel.member_worker_shares(7, 2):
            with arc.analysis_run_caches({}, workers=share):
                pass


class MemberPoolShippingTests(_Trees):
    def test_off_ships_nothing_and_merges_nothing(self):
        with arc.analysis_run_caches({}, workers=2) as caches:
            caches.deadline = FakeDeadline()
            self.assertEqual(pool.vdl_context(caches), {})
            seen = []

            def spy(task):
                seen.append(task)
                return pool.MemberOutcome(True, task.args[0], (), 0, {})
            with mock.patch.object(pool, '_pool') as fake:
                fake.return_value.submit.side_effect = lambda fn, task: _Done(spy(task))
                outcomes = pool.member_map(ship_leaf, self.calls)
        self.assertEqual([task.vdl for task in seen], [{}, {}, {}])
        self.assertTrue(all(outcome.hit is None for outcome in outcomes))

    def test_fills_merge_from_consumed_outcomes_and_then_serve_as_hits(self):
        expected_values, expected_records = self.serial(self.trees)
        with run_caches() as caches:
            first, values, census = self.pooled()
            self.assertTrue(all(outcome.hit is None and outcome.ok for outcome in first))
            self.assertEqual((values, census), (expected_values, expected_records))
            self.assertEqual(len(self.entries(caches)), 3, 'every consumed worker fill reached the run store')
            # Second pass: every member is a pre-filtered hit, none is dispatched.
            second, values, census = self.pooled(dispatch=False)
            self.assertTrue(all(outcome.hit is not None for outcome in second))
            self.assertTrue(all(outcome.records == () for outcome in second), 'rows come from hit.apply()')
            self.assertEqual(values, expected_values)
            self.assertEqual(census, expected_records, 'hit rows registered in serial order')
            self.assertGreaterEqual(caches.vdl.restricted_counters().get('ship:prefilter_hit', 0), 3)

    def test_unconsumed_outcomes_merge_no_entries_and_an_unconsumed_hit_leaves_no_trace(self):
        with run_caches() as caches:
            self.pooled(limit=1)
            self.assertEqual(len(self.entries(caches)), 1, 'only the consumed member fill is merged')
            # The store now serves m1 only: probe every member, consume none.
            second, values, census = self.pooled(limit=0)
            self.assertIsNotNone(second[0].hit)
            self.assertEqual((values, census), ([], []), 'probing registered nothing')
            self.assertEqual(caches.vdl._served, {}, 'an unconsumed hit was never applied')

    def test_a_failed_hit_application_computes_at_its_position(self):
        expected_values, expected_records = self.serial(self.trees)
        with run_caches() as caches:
            self.pooled()
            session = V2AuthenticationReadSession()
            with session:
                second = pool.member_map(ship_leaf, self.calls, worker=registering_worker, account=False)
                self.assertTrue(all(outcome.hit is not None for outcome in second))
                # A byte changes between the probe and the consumption: apply() refuses, the leaf runs.
                (self.trees[1] / 'data.bin').write_bytes(b'yyyy')
                values = [pool.consume(outcome, lambda tree=tree: ship_leaf(str(tree), 3), account=True)
                          for outcome, tree in zip(second, self.trees)]
            census = records(session)
        changed_values, changed_records = self.serial(self.trees)
        self.assertEqual((values, census), (changed_values, changed_records))
        self.assertNotEqual(changed_values, expected_values)
        self.assertGreaterEqual(caches.vdl.restricted_counters().get('ship:prefilter_hit_discarded', 0), 1)

    def test_a_fired_member_contributes_no_entry(self):
        with run_caches() as caches:
            outcomes = pool.member_map(ship_leaf, self.calls, worker=firing_registering_worker)
            self.assertEqual(caches.deadline.firings, 6)
            self.assertEqual(self.entries(caches), {})
            self.assertTrue(all(outcome.vdl_new.get('entries') for outcome in outcomes), 'the worker did fill')

    def test_shadow_sampled_hits_are_dispatched_and_recomputed(self):
        with run_caches(mode=vdl.Mode('shadow', 1000)) as caches:
            self.pooled()
            second, _, _ = self.pooled()
            self.assertTrue(all(outcome.hit is None for outcome in second), 'a sampled hit is never pre-served')
            counters = caches.vdl.restricted_counters()
            self.assertGreaterEqual(counters.get('T_ship:shadow', 0), 3, 'the workers recomputed and compared')
            self.assertFalse(caches.vdl.defect_pending())
            caches.vdl.check_defects()

    def test_a_pool_stays_serial_while_a_fill_is_recorded(self):
        INSIDE_CALLS[:] = self.calls
        self.addCleanup(INSIDE_CALLS.clear)
        with run_caches() as caches:
            self.assertTrue(caches.vdl.call('T_ship_inside', pool_inside_leaf, str(self.trees[0]), 1))
            outcomes = pool.member_map(ship_leaf, self.calls, worker=registering_worker)
            self.assertIsNotNone(outcomes, 'outside a fill the pool is used')


class DefectChannelTests(_Trees):
    def test_a_defect_of_an_unconsumed_member_reaches_the_store(self):
        with run_caches() as caches:
            self.pooled(defect_on_last_worker, limit=1)
            self.assertTrue(caches.vdl.defect_pending())
            with self.assertRaises(vdl.VerifiedStoreDefect):
                caches.vdl.check_defects()
            self.assertEqual(len(self.entries(caches)), 1)

    def test_a_blind_run_counts_a_worker_defect_and_stops_serving(self):
        with run_caches(mode=vdl.BLIND_ON) as caches:
            pool.member_map(ship_leaf, self.calls, worker=blind_defect_on_last_worker, account=False)
            caches.vdl.check_defects()  # never raises on a blind run
            self.assertEqual(caches.vdl.restricted_counters().get('defect:shadow_mismatch'), 1)
            self.assertTrue(caches.vdl._serving_disabled)

    def test_a_discarded_childs_defect_reaches_the_store(self):
        tasks = [('m:main', [], '4', pack) for pack in ('alpha', 'beta')]
        with run_caches() as caches:
            results, _ = parallel.dispatch(tasks, restricted=self.tmp, first_counter=1, workers=2,
                                           physics_store={}, worker=side_channel_child,
                                           vdl=[pool.vdl_context(caches)] * 2)
            self.assertTrue(caches.vdl.defect_pending(), 'beta is never consumed, its defect still counts')
            self.assertEqual(caches.vdl.restricted_counters().get('x:fill'), 2)


class _State:
    """The parts of RunState that _account_deadlines reads."""

    def __init__(self, store):
        self.vdl_store, self.deadline = store, FakeDeadline()


class ChildMergeTests(_Trees):
    def payloads(self):
        """Three children's exports, each holding one real fill."""
        exports = []
        for tree in self.trees:
            with run_caches() as caches:
                caches.vdl.call('T_ship', ship_leaf, str(tree), 3)
                exports.append(pool.export_new(caches, {}, {}))
        self.assertTrue(all(len(payload['entries']) == 1 for payload in exports))
        return exports

    def results(self, exports, firings=(0, 0, 0), exception=(False, False, False)):
        return [parallel.ChildResult(0, '', '', raised, fired, {}, vdl_new=payload)
                for payload, fired, raised in zip(exports, firings, exception)]

    def test_only_the_consumed_prefix_merges(self):
        exports = self.payloads()
        with run_caches() as caches:
            s = _State(caches.vdl)
            results = self.results(exports)
            d._account_deadlines(s, results[:2])  # a serial stop at task 1: task 2 was discarded
            self.assertEqual(len(self.entries(caches)), 2)
            self.assertEqual(set(self.entries(caches)), set(exports[0]['entries']) | set(exports[1]['entries']))

    def test_a_fired_child_or_a_raising_child_contributes_nothing(self):
        exports = self.payloads()
        with run_caches() as caches:
            s = _State(caches.vdl)
            d._account_deadlines(s, self.results(exports, firings=(0, 1, 0)))
            self.assertEqual(s.deadline.firings, 1)
            self.assertEqual(self.entries(caches), {}, 'a firing in the consumed prefix merges no entry')
            d._account_deadlines(s, self.results(exports, exception=(False, True, False)))
            self.assertEqual(set(self.entries(caches)), set(exports[0]['entries']) | set(exports[2]['entries']))

    def test_an_unobservable_child_still_refuses_and_merges_nothing(self):
        exports = self.payloads()
        with run_caches() as caches:
            s = _State(caches.vdl)
            with self.assertRaisesRegex(AnalysisRefusal, '^' + OBSERVER_UNAVAILABLE + '$'):
                d._account_deadlines(s, self.results(exports, firings=(0, None, 0)))
            self.assertEqual(self.entries(caches), {})

    def test_dispatch_merges_no_entry_before_the_serial_stop(self):
        tasks = [('m:main', [str(tree)], '2', 'alpha') for tree in self.trees]
        with run_caches() as caches:
            results, _ = parallel.dispatch(tasks, restricted=self.tmp, first_counter=1, workers=2,
                                           physics_store={}, worker=filling_child,
                                           vdl=[pool.vdl_context(caches)] * 3)
            self.assertTrue(all(len(r.vdl_new['entries']) == 1 for r in results))
            self.assertEqual(self.entries(caches), {}, 'dispatch itself merges no entry')
            d._account_deadlines(_State(caches.vdl), results[:1])
            self.assertEqual(set(self.entries(caches)), set(results[0].vdl_new['entries']))

    def test_step_contexts_select_the_bundle_and_pack(self):
        exports = self.payloads()
        with run_caches() as caches:
            for payload in exports:
                caches.vdl.merge_entries(payload)
            s = _State(caches.vdl)
            s.windows = {'alpha': type('W', (), {'claim_runs_root': self.tmp, 'archive_root': None})()}
            context = d._store_for(s, '1', 'alpha', self.trees[0])
            self.assertEqual(context['mode'], vdl.ON)
            self.assertIsNone(context['entries'], 'step 1 ships no entries')
            self.assertEqual(d._store_for(s, '2', 'alpha', self.trees[0])['entries']['entries'], {},
                             'step 2 ships only L3 entries')
            with mock.patch.object(d, 'STEP_2_LEAVES', frozenset({'T_ship'})):
                shipped = d._store_for(s, '2', 'alpha', self.trees[0])['entries']
            self.assertEqual(list(shipped['entries']), list(exports[0]['entries']), "only the bundle's own entry")
            self.assertEqual(shipped['defects'], [], 'defects are never shipped down')
            with mock.patch.object(d, 'STEP_4_LEAVES', frozenset({'T_ship'})):
                self.assertEqual(len(d._store_for(s, '4', 'alpha')['entries']['entries']), 3, "the pack's entries")
                s.windows['alpha'].claim_runs_root = self.tmp / 'elsewhere'
                self.assertEqual(d._store_for(s, '4', 'alpha')['entries']['entries'], {}, 'another pack: none')
        self.assertEqual(d._store_for(_State(None), '4', 'alpha'), {}, 'no store: nothing shipped')

    def test_dispatch_ships_each_task_its_context(self):
        tasks = [('m:main', [], '4', pack) for pack in ('alpha', 'beta')]
        with run_caches() as caches:
            contexts = [pool.vdl_context(caches, caches.vdl.export_entries()), {}]
            results, _ = parallel.dispatch(tasks, restricted=self.tmp, first_counter=1, workers=2,
                                           physics_store={}, worker=context_child, vdl=contexts)
        self.assertEqual([r.stdout_path for r in results], ['"on"', 'null'])


def timed_child(task):
    """Child stand-in: returns a child timer table when asked for one."""
    table = {'wall_ns': 7, 'cpu_ns': 5, 'phases': {}, 'member': {}, 'programs': [], 'pool': {}} if task.timing else None
    return parallel.ChildResult(0, '', '', False, 0, {}, timing=table)


def scope_probe(argv):
    """A program: whether it runs inside a D-188 program verification scope."""
    print('scoped' if vdl._PROGRAM_SCOPE.get() is not None else 'unscoped')
    return 0


class ProgramScopeAndTimerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='vdl-ship-scope-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_step_runner_enters_a_program_scope_only_with_a_store(self):
        runner = d.StepRunner(self.tmp / 'restricted')
        self.assertIs(type(runner).run, d.StepRunner.run)
        with arc.analysis_run_caches({}, vdl_mode=vdl.ON):
            result = runner.run(scope_probe, [], step='4', window='alpha')
        self.assertEqual(result.stdout_path.read_text().strip(), 'scoped')
        with arc.analysis_run_caches({}):
            result = runner.run(scope_probe, [], step='4', window='beta')
        self.assertEqual(result.stdout_path.read_text().strip(), 'unscoped')
        self.assertIsNone(vdl._PROGRAM_SCOPE.get())

    def test_escaped_exception_class_is_kept_at_the_catch_site(self):
        runner = d.StepRunner(self.tmp / 'restricted')
        result = runner.run(lambda argv: (_ for _ in ()).throw(KeyError('detail')), [], step='4', window='alpha')
        self.assertEqual((result.exception, result.exception_class, runner.last_exception_class),
                         (True, 'KeyError', 'KeyError'))
        result = runner.run(lambda argv: 0, [], step='4', window='beta')
        self.assertEqual((result.exception_class, runner.last_exception_class), (None, None))

    def test_child_timer_tables_merge_into_the_driver_timer(self):
        from joulewise.b5_analysis import phase_timing
        tasks = [('m:main', [], '4', pack) for pack in ('alpha', 'beta')]
        with phase_timing.session(start_sampler=False) as timer:
            self.assertTrue(phase_timing.enabled())
            parallel.dispatch(tasks, restricted=self.tmp, first_counter=1, workers=2, physics_store={},
                              worker=timed_child, timing=True)
            self.assertEqual(timer.acc.children[:2], [2, 14])
        results, _ = parallel.dispatch(tasks, restricted=self.tmp, first_counter=1, workers=2, physics_store={},
                                       worker=timed_child)
        self.assertEqual([r.timing for r in results], [None, None], 'no timer: no table requested')


class _Done:
    def __init__(self, value):
        self._value = value

    def result(self):
        return self._value


def _load_comparator():
    path = ROOT / 'tools/b5_equivalence/compare_b5_results.py'
    spec = importlib.util.spec_from_file_location('jw_b5_ship_comparator', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StepCodesTests(unittest.TestCase):
    """The driver with stub steps (no program, no custody input), as test_parallel_steps' driver test."""

    @classmethod
    def setUpClass(cls):
        cls.cmp = _load_comparator()
        cls.cfg = cls.cmp.load_config()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='vdl-ship-run-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / 'repo').mkdir()
        self.index = self.tmp / 'index.json'
        self.index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        self.serial = 0

    def execute(self, overrides, *, environ=None):
        self.serial += 1
        custody = self.tmp / f'custody-{self.serial}'
        steps = [(name, overrides.get(name, lambda s, r, name=name: [s.record(name)])) for name in d.STEP_IDS]
        validate = lambda record, **kwargs: d._validate_dry_run_record(record)  # noqa: E731 - no index
        with mock.patch.object(d, 'STEPS', steps), mock.patch.object(d, 'validate_dry_run_record', validate), \
                mock.patch.object(d, '_record_parts', return_value=([], [], [])), \
                mock.patch.dict(os.environ, environ or {}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = d.run('blind-dry-run', self.index, custody, workers=1, _test_repo_root=self.tmp / 'repo',
                         _git=lambda repo: 'b' * 40)
        run = custody / 'dry-run'
        record = json.loads((run / 'B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
        rows = [json.loads(line) for line in (run / 'restricted' / d.STEP_CODES_NAME).read_text().splitlines()]
        return code, custody, record, rows

    def assertBound(self, custody, record, rows):
        ran = [row for row in record['steps'] if row['status'] != 'not_run']
        names = [output['name'] for output in ran[-1]['outputs']]
        self.assertEqual(names[-2:], [d.STEP_CODES_NAME, d.VDL_MODE_NAME], 'bound in the last step that ran')
        self.assertFalse(any(d.STEP_CODES_NAME in [o['name'] for o in row['outputs']] for row in ran[:-1]))
        self.assertEqual(len(rows), len(record['steps']))
        for position, (row, step) in enumerate(zip(rows, record['steps'])):
            self.assertEqual(set(row), set(d.STEP_CODES_KEYS))
            self.assertEqual((row['pos'], row['step'], row['window'], row['exit_status']),
                             (position, step['step'], step['window'], step['exit_status']))
            if step['status'] == 'tooling_refusal':
                self.assertEqual(row['raw_code'], step['refusal'])
            if step['status'] in ('ok', 'not_run'):
                self.assertIsNone(row['raw_code'])
                self.assertIsNone(row['exception_class'])
        # The comparator authenticates the committed rows and accepts them.
        side = self.cmp.load_side(custody, 'blind-dry-run', 'cand', self.cfg)
        try:
            parsed, authenticated = self.cmp.read_step_codes(side)
        finally:
            os.close(side.restricted_fd)
        self.assertTrue(authenticated)
        self.assertEqual(len(parsed), len(rows))

    def test_ok_run_binds_codes_and_the_mode_token(self):
        code, custody, record, rows = self.execute({}, environ={vdl.ENV_VARIABLE: 'off'})
        self.assertEqual(code, 0)
        self.assertBound(custody, record, rows)
        self.assertTrue(all(row['raw_code'] is None for row in rows))
        mode = json.loads((custody / 'dry-run/restricted' / d.VDL_MODE_NAME).read_bytes())
        self.assertEqual(mode, {'schema_version': d.VDL_MODE_SCHEMA, 'vdl_mode': 'off'})
        self.assertFalse((custody / 'dry-run/restricted' / d.VDL_COUNTERS_NAME).exists(), 'no store, no counters')

    def test_synthetic_default_is_shadow_and_counters_stay_restricted(self):
        environ = {key: value for key, value in os.environ.items() if key != vdl.ENV_VARIABLE}
        with mock.patch.dict(os.environ, environ, clear=True):
            code, custody, record, rows = self.execute({})
        self.assertEqual(code, 0)
        mode = json.loads((custody / 'dry-run/restricted' / d.VDL_MODE_NAME).read_bytes())
        self.assertEqual(mode['vdl_mode'], 'shadow_1000')
        self.assertTrue((custody / 'dry-run/restricted' / d.VDL_COUNTERS_NAME).is_file())
        self.assertNotIn('counters', json.dumps(record))

    def test_raw_code_before_redaction_and_later_steps_not_run(self):
        code, custody, record, rows = self.execute(
            {'5': lambda s, r: [s.record('5', exit_status=2, code='unlisted_code_q')]},
            environ={vdl.ENV_VARIABLE: 'off'})
        self.assertEqual(code, 2)
        five = record['steps'][d.STEP_IDS.index('5')]
        self.assertEqual((five['status'], five['refusal']), ('unclassified_refusal', 'unclassified refusal at step 5'))
        self.assertNotIn('unlisted_code_q', json.dumps(record))
        self.assertEqual(rows[d.STEP_IDS.index('5')]['raw_code'], 'unlisted_code_q')
        self.assertBound(custody, record, rows)

    def test_tooling_and_exception_classes_at_their_catch_sites(self):
        def escaping(s, r):
            r.run(lambda argv: (_ for _ in ()).throw(ValueError('detail')), [], step='2')
            return [s.record('2', exit_status=2)]

        def raising(s, r):
            raise RuntimeError('detail')

        def refusing(s, r):
            raise AnalysisRefusal('custody_path_invalid')

        cases = (('2', escaping, 'ValueError', None, 'unclassified_refusal'),
                 ('3', raising, 'RuntimeError', None, 'unclassified_refusal'),
                 ('1', refusing, 'AnalysisRefusal', 'custody_path_invalid', 'tooling_refusal'))
        for step, function, exception, raw, status in cases:
            with self.subTest(step=step):
                code, custody, record, rows = self.execute({step: function}, environ={vdl.ENV_VARIABLE: 'off'})
                position = d.STEP_IDS.index(step)
                self.assertEqual(record['steps'][position]['status'], status)
                self.assertEqual((rows[position]['raw_code'], rows[position]['exception_class']), (raw, exception))
                self.assertNotIn('detail', (custody / 'dry-run/restricted' / d.STEP_CODES_NAME).read_text())
                self.assertBound(custody, record, rows)

    def test_a_store_defect_stops_the_run_at_its_step_boundary(self):
        def defective(s, r):
            s.vdl_store._defect('shadow_mismatch')
            return [s.record('4', window='alpha'), s.record('4', window='beta')]

        code, custody, record, rows = self.execute({'4': defective}, environ={vdl.ENV_VARIABLE: 'on'})
        self.assertEqual(code, 2)
        four = [row for row in record['steps'] if row['step'] == '4']
        self.assertEqual([(row['window'], row['status']) for row in four], [(None, 'unclassified_refusal')])
        position = record['steps'].index(four[0])
        self.assertEqual((rows[position]['raw_code'], rows[position]['exception_class']),
                         (d.VDL_DEFECT, 'VerifiedStoreDefect'))
        self.assertTrue(all(row['status'] == 'not_run' for row in record['steps'][position + 1:]))

    def test_release_comparison_ignores_the_sidecars(self):
        before = {'input_census': [], 'steps': [{'step': '0', 'outputs': [
            {'name': 'outputs/a.json', 'sha256': '1' * 64}, {'name': d.STEP_CODES_NAME, 'sha256': '2' * 64}]}]}
        after = {'input_census': [], 'steps': [{'step': '0', 'outputs': [
            {'name': 'outputs/a.json', 'sha256': '1' * 64}]}]}
        self.assertIsNone(d.release_difference(before, after))


class LeafWrapperTests(unittest.TestCase):
    def test_wrapper_adapters_call_the_leaf_as_the_wrappers_do(self):
        from joulewise import cli, floor_extraction
        from joulewise.b5_analysis import bracket
        calls = []

        def fake(path, strict=False, *, physics_cache=None):
            calls.append((type(path).__name__, str(path), strict, physics_cache))
            return ['p']
        for reference, wrapper, args in (
                ('joulewise.floor_extraction:_default_strict_validator', floor_extraction._default_strict_validator,
                 (Path('/x/b'), True)),
                ('joulewise.b5_analysis.bracket:_strict_problems', bracket._strict_problems, ('/x/b',))):
            with self.subTest(reference=reference):
                calls.clear()
                with mock.patch.object(cli, 'validate_bundle', fake):
                    direct = wrapper(*args)
                    leaf_id, leaf_ref, adapt, post = pool._WRAPPED_LEAVES[reference]
                    leaf_args, leaf_kwargs = adapt(*args)
                    value = fake(*leaf_args, **leaf_kwargs)
                    adapted = value if post is None else post(value)
                self.assertEqual(calls[0], calls[1])
                self.assertEqual((type(direct), direct), (type(adapted), adapted))
                self.assertEqual((leaf_id, leaf_ref), ('L1_strict_validation', 'joulewise.cli:validate_bundle'))
                self.assertIn(leaf_id, {spec.leaf_id for spec in vdl.LEAVES})


if __name__ == '__main__':
    unittest.main()
