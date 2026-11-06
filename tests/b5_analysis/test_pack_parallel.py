"""Synthetic pack scheduling: frozen transport, read replay and serial refusals."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from joulewise import analysis_run_cache as arc
from joulewise.authentication_io import V2AuthenticationReadSession, read_authentication_input
from joulewise.b5_analysis import pack_parallel as pp
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.b5_analysis.windows import AnalysisRefusal


def read_pack(path, refuse=False):
    value = read_authentication_input(Path(path), grammar='json', label='synthetic pack')
    if refuse:
        raise AnalysisRefusal('refusal_' + Path(path).stem)
    return json.loads(value)


def bad_later_deadline(task):
    result = pp.run_pack(task)
    args, _ = pp.loads(task.payload)
    return replace(result, firings=3 if Path(args[0]).stem == 'beta' else 0)


def bracket_fixture_worker(task):
    from tests.b5_analysis import fixtures_s2 as fx
    args, _ = pp.loads(task.payload)
    fx._ROOTS.add(args[0].window.claim_runs_root.parent)
    with fx.capture_adapter():
        return pp.run_pack(task)


class PackTransportTests(unittest.TestCase):
    def test_operator_switch_keeps_the_serial_path(self):
        with arc.analysis_run_caches({}, workers=3):
            calls = [(('a',), {}), (('b',), {})]
            for value, expected in (('off', False), ('read_pack', True), ('bracket_pack, derive_pack', False),
                                    ('on', True)):
                with patch.dict('os.environ', {pp.PACK_PARALLEL_ENV: value}):
                    self.assertIs(pp.pack_scheduling_enabled(read_pack), expected)
                    if not expected:
                        self.assertIsNone(pp.pack_map(read_pack, calls))
        with patch.dict('os.environ', {}, clear=False):
            import os
            os.environ.pop(pp.PACK_PARALLEL_ENV, None)
            self.assertTrue(pp.pack_scheduling_enabled(read_pack))

    def test_opaque_caller_argument_keeps_the_serial_path(self):
        with arc.analysis_run_caches({}, workers=3):
            self.assertIsNone(pp.pack_map(read_pack, [((lambda: None,), {}), ((lambda: None,), {})]))

    def test_frozen_mapping_transport_is_local_and_preserves_types(self):
        value = MappingProxyType({'frozen': (MappingProxyType({'n': 1}),), 'mutable': [2]})
        restored = pp.loads(pp.dumps(value))
        self.assertIsInstance(restored, MappingProxyType)
        self.assertIsInstance(restored['frozen'], tuple)
        self.assertIsInstance(restored['frozen'][0], MappingProxyType)
        self.assertIsInstance(restored['mutable'], list)
        self.assertEqual(value, restored)

    def test_first_pack_refusal_and_partial_reads_match_serial(self):
        with tempfile.TemporaryDirectory(prefix='pack-order-') as tmp:
            paths = [Path(tmp) / (p + '.json') for p in ('alpha', 'beta', 'gamma')]
            for path in paths:
                path.write_text('{}')
            for bad in ((True, True, False), (False, True, True), (False, False, True)):
                results = []
                for workers in (1, 3):
                    calls = [((str(path), refuses), {}) for path, refuses in zip(paths, bad)]
                    with arc.analysis_run_caches({}, workers=workers) as caches, \
                            V2AuthenticationReadSession() as session, \
                            patch.object(pp, 'run_pack', bad_later_deadline):
                        caches.deadline = DeadlineObserver()
                        outcomes = pp.pack_map(read_pack, calls)
                        try:
                            for (args, kwargs), outcome in zip(calls, outcomes or [None] * len(calls)):
                                pp.consume(outcome, lambda: read_pack(*args, **kwargs))
                        except AnalysisRefusal as exc:
                            results.append((exc.code, tuple(session.records)))
                        if bad[0]:
                            self.assertEqual(caches.deadline.firings, 0)
                self.assertEqual(*results)

    def test_success_replays_every_authentication_read_in_order(self):
        with tempfile.TemporaryDirectory(prefix='pack-reads-') as tmp:
            paths = [Path(tmp) / (p + '.json') for p in ('alpha', 'beta', 'gamma')]
            for path in paths:
                path.write_text('{"n": 3}')
            rows = []
            for workers in (1, 3):
                calls = [((str(path),), {}) for path in paths]
                with arc.analysis_run_caches({}, workers=workers) as caches, \
                        V2AuthenticationReadSession() as session:
                    caches.deadline = DeadlineObserver()
                    outcomes = pp.pack_map(read_pack, calls)
                    if workers == 3:
                        self.assertIsNotNone(outcomes)
                        self.assertTrue(all(outcome.ok for outcome in outcomes))
                    values = [pp.consume(o, lambda args=args: read_pack(*args))
                              for (args, _), o in zip(calls, outcomes or [None] * len(calls))]
                    rows.append((values, tuple(vars(r) for r in session.records.values()),
                                 dict(arc.memo('authentication_io.grammar_ok'))))
            self.assertEqual(*rows)


class BracketPackTests(unittest.TestCase):
    def test_roundtrip_preserves_selected_window_and_authenticated_roster_capabilities(self):
        from joulewise.b5_analysis import context as ctx
        from joulewise.b5_analysis.windows import _SELECTION_TOKEN
        from tests.b5_analysis import fixtures_s3b as fx

        case = fx.Case()
        self.addCleanup(case.close)
        archive, units = case.inputs()
        context = ctx.build_context(archive, units, case.assessment, case.row,
                                    test_only_allow_synthetic_binding=True)
        # S0 is deliberately not a hazard collection. Exercise the builder's
        # callable with a genuinely issued roster and preserve its refusal;
        # do not pretend this fixture satisfies the hazard admission gate.
        context = replace(context, sources_replay=ctx._SourcesReplay(archive, ctx.rebuilt_roster(archive, case.row)))
        restored = pp.loads(pp.dumps(context))
        self.assertIsNotNone(restored.sources_replay)
        replay = restored.sources_replay
        self.assertIs(replay.archive.window._selection_token[0], _SELECTION_TOKEN)
        self.assertTrue(ctx._bound_roster(replay.archive, replay.roster))
        self.assertEqual(context.sources_replay(case.row, archive.window.claim_runs_root),
                         replay(case.row, replay.archive.window.claim_runs_root))
        self.assertEqual(archive.census(), replay.archive.census())

    def test_refusing_alpha_precedes_beta_and_keeps_serial_census_and_record(self):
        from joulewise.b5_analysis import bracket, dry_run as d
        from tests.b5_analysis import fixtures_s2 as fx

        built = {pack: fx.build_named(pack.upper() + '_STD') for pack in ('alpha', 'beta', 'gamma')}
        originals, results = {}, []
        try:
            for workers in (1, 3):
                with tempfile.TemporaryDirectory(prefix='bracket-order-') as tmp:
                    state = d.RunState('blind-dry-run', Path(tmp) / 'index.json', Path(tmp), '0' * 40)
                    state.archives = {pack: fx.handle(window) for pack, window in built.items()}
                    # Distinct failures: alpha has an unauthenticated acceptance,
                    # beta has a bad terminal pin. Alpha must decide the row.
                    for pack, relative in (('alpha', 'sources/inputs/acceptance.json'),
                                           ('beta', bracket.TERMINAL_PIN)):
                        path = built[pack].archive / relative
                        originals.setdefault(path, path.read_bytes())
                        path.write_bytes(b'{}')
                    runner = d.StepRunner(Path(tmp))
                    with arc.analysis_run_caches({}, workers=workers) as caches, fx.capture_adapter(), \
                            patch.object(pp, 'run_pack', bracket_fixture_worker):
                        caches.deadline = DeadlineObserver()
                        rows = d.step_3b(state, runner)
                    results.append(([row.as_dict() for row in rows],
                                    {p: a.census() for p, a in state.archives.items()}, state.brackets,
                                    runner._counter))
                for path, raw in originals.items():
                    path.write_bytes(raw)
            self.assertEqual(*results)
            self.assertEqual(results[0][0][0]['status'], 'tooling_refusal')
            self.assertEqual(results[0][0][0]['refusal'], 'archive_source_unauthenticated')
        finally:
            for path, raw in originals.items():
                path.write_bytes(raw)


if __name__ == '__main__':
    unittest.main()
