"""Erratum 3 section D gates; synthetic bytes only, no claim custody reads."""
from __future__ import annotations

import base64
import contextlib
import copy
from dataclasses import replace
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock
import zlib

from joulewise import calibration_bracketing as br
from joulewise import calibration_ledger as cl
from joulewise.b5 import harvest as h
from tests import test_calibration_bracketing as old_tests
from tests import test_harvest_b5_sources as source_tests
from tests import test_harvest_b5_window as window_tests

BASE = '0699abbb0881ce64b39c46ba07de568cc3848260'
REPO = Path(__file__).resolve().parents[1]
DOUBLE = 'corpus_doubles_from_24_to_48'
RANGE = 'new_valid_same_identity_capture_expands_observed_range'
SYSTEMATIC = 'new_systematic_failure_challenges_preflight_screen'
BYTE = 'protocol_or_estimator_byte_change'
NEW_KEYS = {'trigger_scope', 'recorded_only_triggers', 'corpus_doubling',
            'other_session_systematic_sequences'}


def pinned_brackets():
    raw = subprocess.run(['git', 'show', f'{BASE}:joulewise/calibration_bracketing.py'],
                         cwd=REPO, check=True, capture_output=True).stdout
    module = types.ModuleType('joulewise._erratum3_pinned_brackets')
    module.__file__ = br.__file__
    sys.modules[module.__name__] = module
    exec(compile(raw, br.__file__, 'exec'), module.__dict__)
    return module


def under_current_seams(module, name):
    # The original function bodies run against the SAME fixture/patch inputs.
    # Rebinding the globals keeps each existing test's explicit seams in force.
    env = dict(vars(br))
    evaluator = module.evaluate_calibration_bracket
    env['evaluate_calibration_bracket'] = types.FunctionType(
        evaluator.__code__, env, evaluator.__name__, evaluator.__defaults__)
    env['evaluate_calibration_bracket'].__kwdefaults__ = evaluator.__kwdefaults__
    function = getattr(module, name)
    rebound = types.FunctionType(function.__code__, env, name, function.__defaults__)
    rebound.__kwdefaults__ = function.__kwdefaults__
    return rebound


class SealedIdentityTests(unittest.TestCase):
    def test_every_existing_bracket_fixture_equals_the_pinned_functions(self):
        pinned = pinned_brackets()
        originals = {name: getattr(br, name) for name in (
            'evaluate_calibration_bracket', 'calibration_bracket_for_bundles')}
        counts = dict.fromkeys(originals, 0)
        statuses = set()
        busy = False

        def spy(name):
            def compare(*args, **kwargs):
                nonlocal busy
                actual = originals[name](*args, **kwargs)
                if busy:
                    return actual
                counts[name] += 1
                statuses.add(actual[0]['status'])
                # Replay calls must not change a fixture's mock call assertions.
                mocks = {id(value): value for value in vars(br).values()
                         if isinstance(value, mock.Mock)}
                states = [(value, {key: (list(item) if isinstance(item, list) else item) for key, item in vars(value).items()
                                  if key.startswith('_mock_call') or key == '_mock_mock_calls'})
                          for value in mocks.values()]
                busy = True
                try:
                    baseline_kwargs = dict(kwargs)
                    baseline_kwargs.pop('trigger_scope', None)
                    if 'diagnostics' in baseline_kwargs:
                        baseline_kwargs['diagnostics'] = []
                    baseline = under_current_seams(pinned, name)(*args, **baseline_kwargs)
                    explicit_kwargs = dict(kwargs, trigger_scope='sealed')
                    if 'diagnostics' in explicit_kwargs:
                        explicit_kwargs['diagnostics'] = []
                    explicit = originals[name](*args, **explicit_kwargs)
                    self.assertEqual(actual, baseline, name)
                    self.assertEqual(explicit, baseline, name)
                    self.assertEqual(json.dumps(actual, sort_keys=True),
                                     json.dumps(baseline, sort_keys=True), name)
                    prospective = (actual[0].get('acceptance') or {}).get('prospective_rederivation', {})
                    self.assertFalse(NEW_KEYS & prospective.keys())
                finally:
                    for value, state in states:
                        vars(value).update(state)
                    busy = False
                return actual
            return compare

        with mock.patch.object(old_tests, '_evaluate_calibration_bracket',
                               side_effect=spy('evaluate_calibration_bracket')), \
             mock.patch.object(br, 'evaluate_calibration_bracket',
                               side_effect=spy('evaluate_calibration_bracket')), \
             mock.patch.object(old_tests, 'calibration_bracket_for_bundles',
                               side_effect=spy('calibration_bracket_for_bundles')):
            suite = unittest.defaultTestLoader.loadTestsFromModule(old_tests)
            outcome = unittest.TestResult()
            suite.run(outcome)
        self.assertEqual([(test.id(), traceback[-1500:]) for test, traceback in outcome.errors], [])
        self.assertEqual([(test.id(), traceback[-1500:]) for test, traceback in outcome.failures], [])
        self.assertGreater(counts['evaluate_calibration_bracket'], 50)
        self.assertGreater(counts['calibration_bracket_for_bundles'], 5)
        self.assertIn('failed', statuses)
        self.assertIn('passed', statuses)


class WindowEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.helper = old_tests.CalibrationBracketingTests()
        self.helper.setUp()
        self.helper.bindings['os_build'] = '25G83'
        self.artifact = br.load_calibration_acceptance_bound()
        cutoff = self.artifact['ledger_cutoff']
        with tempfile.TemporaryDirectory(prefix='erratum3-prefix-') as directory:
            ledger, pin = Path(directory) / 'ledger.jsonl', Path(directory) / 'pin.json'
            ledger.write_bytes(zlib.decompress(base64.b85decode(window_tests.PREFIX.read_bytes())))
            pin.write_text(json.dumps({'sequence': cutoff['sequence'], 'head_digest': cutoff['head_digest'],
                                       'ledger_schema': cl.LEDGER_SCHEMA}))
            self.prefix = cl.load_calibration_ledger_snapshot(
                ledger, pin, require_committed_pin=False, verify_custody=False,
                baseline_sequence=cutoff['sequence'], baseline_digest=cutoff['head_digest'])
        self.assertEqual(self.prefix.refusal_reasons, ())

    def fixture(self, p='0.028', q='0.03050', *, count=43, systematics=(456,),
                systematic_session='another-session', disposition='systematic-invalid'):
        snapshot, candidates, _ = self.helper._bound_session_fixture()
        sequence_map = {2: 380, 4: 382, 6: 480, 8: 482, 10: 484}
        receipts = tuple(dict(row, sequence=sequence_map.get(row['sequence'],
                              sequence_map[row['sequence'] + 1] - 1))
                         if row['sequence'] % 2 else dict(row, sequence=sequence_map[row['sequence']])
                         for row in snapshot.receipts)
        observations = []
        for observation in snapshot.observations:
            bound = p if observation.bracket_slot == 'pre' else q if observation.bracket_slot == 'post' \
                else observation.exact_bound_lexeme_s
            observations.append(replace(observation, sequence=sequence_map[observation.sequence],
                                        exact_bound_lexeme_s=bound))
        candidates = [replace(candidate, b_fiducial_s=Decimal(p) if candidate.bracket_slot == 'pre'
                              else Decimal(q) if candidate.bracket_slot == 'post'
                              else candidate.b_fiducial_s) for candidate in candidates]
        session = replace(snapshot.bracket_sessions[0], capability_sequence=480,
                          finalized_slots=types.MappingProxyType(
                              {row.bracket_slot: row for row in observations if row.bracket_slot}))
        # The released prefix contains the 24 retained corpus rows plus the
        # decision-set-aside rows. Add enough live valid captures to count N.
        for index in range(count - 28):
            token = f'extra-{index}'
            hashes = {key: hashlib.sha256(f'{token}:{key}'.encode()).hexdigest()
                      for key in ('manifest.json', 'instrument_evidence.json')}
            row = replace(observations[0], sequence=384 + index * 2,
                          attempt_id=token, content_id=cl.content_id_from_artifact_hashes(hashes),
                          receipt_digest=hashlib.sha256(token.encode()).hexdigest(),
                          artifact_sha256=types.MappingProxyType(hashes))
            observations.append(row)
            candidates.append(replace(candidates[0], attempt_id=token, content_id=row.content_id,
                                      ledger_receipt_digest=row.receipt_digest,
                                      manifest_sha256=hashes['manifest.json'],
                                      evidence_sha256=hashes['instrument_evidence.json']))
        for sequence in systematics:
            observations.append(replace(observations[0], sequence=sequence,
                attempt_id=f'systematic-{sequence}', content_id=None,
                receipt_digest=hashlib.sha256(f'systematic-{sequence}'.encode()).hexdigest(),
                disposition=disposition, exact_bound_lexeme_s='0.04437677892168357',
                bracket_session_id=systematic_session))
        physical = [*self.prefix.receipts, *({'sequence': n, 'event': 'synthetic-noop'}
                    for n in range(377, 485))]
        for receipt in receipts:
            physical[receipt['sequence'] - 1] = receipt
        snapshot = replace(snapshot, head_sequence=484, baseline_sequence=376,
                           baseline_digest=self.artifact['ledger_cutoff']['head_digest'],
                           observations=(*self.prefix.observations, *observations),
                           receipts=tuple(physical), bracket_sessions=(*self.prefix.bracket_sessions, session))
        binding = br.build_calibration_bracket_binding(
            snapshot, session_id='session-alpha', window_id='window-alpha', plan_id='plan-alpha',
            plan_sha256='a' * 64, evidence_root_id='evidence-alpha', runs_root='/synthetic/root-alpha')
        return snapshot, candidates, binding

    def kwargs(self, snapshot, binding):
        return dict(window_start_s=100.0, window_end_s=110.0, bindings=self.helper.bindings,
                    policy=self.helper.policy, ledger_snapshot=snapshot, bracket_binding=binding,
                    bracket_window_id='window-alpha', bracket_plan_id='plan-alpha',
                    bracket_plan_sha256='a' * 64, bracket_evidence_root_id='evidence-alpha',
                    bracket_runs_root='/synthetic/root-alpha')

    def evaluate(self, fixture=None, scope='window_evidence', **overrides):
        snapshot, candidates, binding = fixture or self.fixture()
        kwargs = self.kwargs(snapshot, binding)
        kwargs.update(overrides)
        return br.evaluate_calibration_bracket(candidates, trigger_scope=scope, **kwargs)

    def prospective(self, result):
        return result['acceptance']['prospective_rederivation']

    def test_item2_other_session_and_no_session_are_recorded_at_both_sites(self):
        for session in ('another-session', None):
            with self.subTest(session=session):
                fixture = self.fixture(systematic_session=session)
                sealed, reasons = self.evaluate(fixture, scope='sealed')
                self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
                self.assertIsNone(sealed['pre'])
                result, reasons = self.evaluate(fixture)
                self.assertEqual((result['status'], reasons), ('passed', ()))
                self.assertIsNotNone(result['pre'])
                self.assertEqual(self.prospective(result)['other_session_systematic_sequences'], [456])
                self.assertEqual(self.prospective(result)['recorded_only_triggers'], [SYSTEMATIC])
                self.assertEqual(result['acceptance']['freshness']['status'], 'fresh')

    def test_item2_unbound_uses_sealed_decisions_whatever_scope(self):
        for p, systematics, count in (('0.028', (456,), 43), ('0.021', (), 43), ('0.028', (), 48)):
            snapshot, candidates, _ = self.fixture(p=p, systematics=systematics, count=count)
            candidates = [replace(c, bracket_session_id=None, bracket_slot=None,
                bracket_window_id=None, bracket_plan_id=None, bracket_plan_sha256=None,
                bracket_evidence_root_id=None, bracket_runs_root=None) for c in candidates]
            snapshot = replace(snapshot, bracket_sessions=self.prefix.bracket_sessions, observations=tuple(
                replace(o, bracket_session_id=None, bracket_slot=None, bracket_window_id=None,
                        bracket_plan_id=None, bracket_plan_sha256=None, bracket_evidence_root_id=None,
                        bracket_runs_root=None) if o.sequence > 376 else o for o in snapshot.observations))
            kwargs = self.kwargs(snapshot, None)
            sealed, sealed_reasons = br.evaluate_calibration_bracket(candidates, **kwargs)
            amended, amended_reasons = br.evaluate_calibration_bracket(candidates, trigger_scope='window_evidence',
                                                                       **kwargs)
            prospective = self.prospective(amended)
            self.assertEqual(prospective['recorded_only_triggers'], [])
            for key in NEW_KEYS:
                prospective.pop(key)
            self.assertEqual((amended, amended_reasons), (sealed, sealed_reasons))

    def test_item3_own_systematic_event_keeps_the_early_return(self):
        fixture = self.fixture(systematic_session='session-alpha')
        result, reasons = self.evaluate(fixture)
        self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
        self.assertIsNone(result['pre'])
        self.assertEqual(self.prospective(result)['recorded_only_triggers'], [])
        self.assertEqual(self.prospective(result)['other_session_systematic_sequences'], [])

    def test_item3_doubling_at_and_above_48_records_and_passes(self):
        for count in (48, 49):
            with self.subTest(count=count):
                result, reasons = self.evaluate(self.fixture(count=count, systematics=()))
                self.assertEqual((result['status'], reasons), ('passed', ()))
                self.assertEqual(self.prospective(result)['recorded_only_triggers'], [DOUBLE])
                self.assertEqual(self.prospective(result)['corpus_doubling'], {'count': count, 'threshold': 48})

    def test_item4_byte_change_remains_the_only_failing_name_at_second_site(self):
        with mock.patch.object(br, '_current_estimator_code_sha256', return_value={}):
            result, reasons = self.evaluate(self.fixture(p='0.021', count=48))
        self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
        self.assertIsNotNone(result['pre'])
        self.assertEqual(result['acceptance']['freshness']['stale_triggers'], [BYTE])
        self.assertEqual(self.prospective(result)['recorded_only_triggers'], [DOUBLE, RANGE, SYSTEMATIC])

    def test_item4_identity_change_still_fails_first(self):
        result, reasons = self.evaluate(bindings=dict(self.helper.bindings, hardware_model='another-model'))
        self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
        self.assertIsNone(result['bracket_binding'])
        self.assertEqual(result['acceptance']['freshness']['stale_fields'], ['hardware_model'])

    def test_item4_unchanged_refusals_and_order(self):
        snapshot, candidates, binding = self.fixture()
        cases = [
            ('missing_ledger', dict(ledger_snapshot=None), 'calibration_ledger_snapshot_required'),
            ('refused_ledger', dict(ledger_snapshot=replace(snapshot, refusal_reasons=('calibration_ledger_invalid',))),
             'calibration_ledger_invalid'),
            ('baseline', dict(ledger_snapshot=replace(snapshot, baseline_sequence=0)),
             'calibration_ledger_baseline_missing'),
            ('binding_missing', dict(bracket_binding=None), 'calibration_bracket_binding_missing'),
            ('binding_invalid', dict(bracket_binding={}), 'calibration_bracket_binding_invalid'),
        ]
        for name, overrides, reason in cases:
            with self.subTest(name=name):
                result, reasons = self.evaluate((snapshot, candidates, binding), **overrides)
                self.assertEqual(reasons, (reason,))
                self.assertEqual(result['status'], 'failed')
                self.assertEqual(self.prospective(result)['corpus_doubling'],
                    {'count': 43, 'threshold': 48} if name.startswith('binding_') else None)
                self.assertEqual(result['acceptance']['freshness']['status'], 'stale')
        for artifact in (None, old_tests._current_estimator_acceptance_fixture()):
            with mock.patch.object(br, 'load_calibration_acceptance_bound', return_value=artifact):
                _, reasons = self.evaluate((snapshot, candidates, binding))
            self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
        _, reasons = self.evaluate((snapshot, candidates[:-1], binding))
        self.assertEqual(reasons, ('calibration_ledger_off_ledger_artifact',))
        _, reasons = self.evaluate(self.fixture(disposition='abandoned'))
        self.assertEqual(reasons, ('calibration_observation_unclassifiable',))
        with mock.patch.object(br, 'disposed_content_ids_for', return_value=None):
            _, reasons = self.evaluate()
        self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
        with mock.patch.object(br, 'validate_calibration_bracket_binding', return_value=(
                snapshot.observations[-3], snapshot.observations[-2])):
            _, reasons = self.evaluate((snapshot, candidates, binding), window_start_s=200000.0,
                                        window_end_s=200010.0)
        self.assertEqual(reasons, ('instrument_calibration_stale',))
        invalid = [replace(candidates[0], b_fiducial_s=Decimal('NaN')), *candidates[1:]]
        _, reasons = self.evaluate((snapshot, invalid, binding))
        self.assertEqual(reasons, ('instrument_calibration_invalid',))

    def test_item5_own_preflight_failure_branch_stays_as_sealed(self):
        snapshot, candidates, binding = self.fixture(p='0.037', systematics=())
        # This specified branch is unreachable with a genuine validated binding;
        # retain a test seam to prove the preflight path itself remains operative.
        result, reasons = self.evaluate((snapshot, candidates, binding))
        self.assertEqual(reasons, ('instrument_calibration_mismatch',))
        self.assertEqual(result['acceptance']['preflight']['status'], 'failed')

    def test_item5_post_above_screen_binding_rejected(self):
        snapshot, _, _ = self.fixture(systematics=())
        session = snapshot.bracket_session_by_id['session-alpha']
        post = replace(session.finalized_slots['post'], disposition='systematic-invalid',
                       exact_bound_lexeme_s='0.037')
        snapshot = replace(snapshot, observations=tuple(post if o.attempt_id == post.attempt_id else o
            for o in snapshot.observations), bracket_sessions=(*self.prefix.bracket_sessions, replace(session, finalized_slots={
                **session.finalized_slots, 'post': post})))
        with self.assertRaises(ValueError):
            br.build_calibration_bracket_binding(snapshot, session_id=session.session_id,
                window_id=session.window_id, plan_id=session.plan_id, plan_sha256=session.plan_sha256,
                evidence_root_id=session.evidence_root_id, runs_root=session.runs_root)

    def test_item5_own_low_capture_records_and_passes_in_both_slots(self):
        for p, q in (('0.021', '0.024'), ('0.024', '0.021'), ('0.0205', '0.021')):
            with self.subTest(p=p, q=q):
                fixture = self.fixture(p=p, q=q, systematics=())
                result, reasons = self.evaluate(fixture)
                self.assertEqual((result['status'], reasons), ('passed', ()))
                self.assertEqual(self.prospective(result)['recorded_only_triggers'], [RANGE])
                _, sealed_reasons = self.evaluate(fixture, scope='sealed')
                self.assertEqual(sealed_reasons, ('calibration_acceptance_bound_stale',))
        self.assertLess(result['b_fiducial_s'], .036462861644980)

    def test_item5_low_capture_drift_ceiling_still_fails(self):
        result, reasons = self.evaluate(self.fixture(p='0.0205', q='0.0364', systematics=()))
        self.assertEqual(reasons, ('instrument_calibration_mismatch',))
        self.assertEqual(result['drift_s'], .0159)
        self.assertEqual(result['acceptance']['freshness']['status'], 'stale')
        self.assertEqual(self.prospective(result)['recorded_only_triggers'], [RANGE])

    def test_item5_rounding_gap_is_valid_recorded_and_passed(self):
        for p, q in (('0.03646286164497998', '0.0305'), ('0.028', '0.036462861644980')):
            with self.subTest(p=p, q=q):
                result, reasons = self.evaluate(self.fixture(p=p, q=q, systematics=()))
                self.assertEqual((result['status'], reasons), ('passed', ()))
                self.assertEqual(self.prospective(result)['recorded_only_triggers'], [RANGE])

    def test_item5_inside_range_has_no_own_event(self):
        result, reasons = self.evaluate(self.fixture(systematics=()))
        self.assertEqual((result['status'], reasons), ('passed', ()))
        self.assertEqual(self.prospective(result)['observed_triggers'], [])
        self.assertEqual(self.prospective(result)['recorded_only_triggers'], [])

    def test_item6_keys_fixed_order_and_ascending_sequences(self):
        result, reasons = self.evaluate(self.fixture(p='0.021', count=48, systematics=(458, 456)))
        self.assertEqual((result['status'], reasons), ('passed', ()))
        prospective = self.prospective(result)
        self.assertTrue(NEW_KEYS <= prospective.keys())
        self.assertEqual(prospective['trigger_scope'], 'window_evidence')
        self.assertEqual(prospective['observed_triggers'], [DOUBLE, RANGE, SYSTEMATIC])
        self.assertEqual(prospective['recorded_only_triggers'], [DOUBLE, RANGE, SYSTEMATIC])
        self.assertEqual(prospective['other_session_systematic_sequences'], [456, 458])
        self.assertEqual(result['acceptance']['freshness']['status'], 'fresh')

    def test_item1_invalid_scope_raises_at_both_entry_points(self):
        for value in ('', 'window', None, False, [], {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.evaluate(scope=value)
                with self.assertRaises(ValueError):
                    br.calibration_bracket_for_bundles(Path('.'), [], self.helper.policy, trigger_scope=value)

    def test_worked_example_exact_operative_and_summary_inputs(self):
        result, reasons = self.evaluate()
        self.assertEqual((result['status'], reasons), ('passed', ()))
        self.assertEqual(result['b_fiducial_s'], .045031)
        self.assertEqual(result['drift_s'], .0025)
        self.assertEqual(result['calibration_drift_allowance_s'], .014531)
        self.assertEqual(self.prospective(result)['corpus_doubling'], {'count': 43, 'threshold': 48})
        self.assertEqual(self.prospective(result)['observed_triggers'], [SYSTEMATIC])
        self.assertEqual(self.prospective(result)['other_session_systematic_sequences'], [456])

    def test_item1_wrapper_passes_scope_at_every_call_site(self):
        snapshot, candidates, binding = self.fixture()
        class Reader:
            def __init__(reader, path):
                reader.path = path
            def measured_window(reader):
                return types.SimpleNamespace(start_s=100.0, end_s=110.0)
            def metadata(reader):
                bindings = dict(self.helper.bindings)
                if reader.path.name == 'mismatch':
                    bindings['hardware_model'] = 'another-model'
                return {'instrument_calibration': {'bindings': bindings}}
        cases = (('empty', [], None), ('bad_reader', [Path('member')], OSError()),
                 ('mismatch', [Path('member'), Path('mismatch')], None),
                 ('custody', [Path('member')], None), ('success', [Path('member')], None))
        for name, paths, error in cases:
            with self.subTest(name=name), \
                 mock.patch.object(br, 'BundleReader', side_effect=error or Reader), \
                 mock.patch.object(br, 'discover_calibration_candidates',
                                   return_value=() if name == 'custody' else tuple(candidates)), \
                 mock.patch.object(br, 'evaluate_calibration_bracket',
                                   wraps=br.evaluate_calibration_bracket) as evaluate:
                result, reasons = br.calibration_bracket_for_bundles(
                    Path('/synthetic/root-alpha'), paths, self.helper.policy, ledger_snapshot=snapshot,
                    bracket_binding=binding, bracket_window_id='window-alpha', bracket_plan_id='plan-alpha',
                    bracket_plan_sha256='a' * 64, bracket_evidence_root_id='evidence-alpha',
                    trigger_scope='window_evidence')
                self.assertEqual(len(evaluate.call_args_list), 1)
                self.assertEqual(evaluate.call_args.kwargs['trigger_scope'], 'window_evidence')
                if name == 'success':
                    self.assertEqual((result['status'], reasons), ('passed', ()))
                if name == 'custody':
                    self.assertEqual(reasons, ('calibration_ledger_custody_invalid',))


class HarvestScopeTests(window_tests.WindowTestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = WindowEvidenceTests()
        self.evaluator.setUp()

    def governed_window(self, name='w', t0=h.ERRATUM_3_ADMITTED_AT_EPOCH_S + 1):
        window = window_tests.Window(self.tmp / name, prefix_ledger=True, catalog_overrides=self.ISOLATE)
        plan = h.read_json(window.plan_path)
        plan['t0_epoch_s'] = t0
        window_tests.put(window.plan_path, plan)
        return window

    def harvest_with_bracket(self, window, *, fixture=None, **kwargs):
        scopes = []
        def evaluate(*args, **call):
            scopes.append(call['trigger_scope'])
            return self.evaluator.evaluate(fixture, scope=call['trigger_scope'])
        with mock.patch.object(br, 'calibration_bracket_for_bundles', side_effect=evaluate):
            record = window.harvest(**kwargs)
        return record, scopes

    def test_item0_admission_is_finite_numeric_nonbool_and_strict(self):
        inputs = h.resolve_inputs(self.governed_window().plan_path)
        for t0, governed in ((1791671820, False), (1791704340, False),
            (h.ERRATUM_3_ADMITTED_AT_EPOCH_S, False),
            (h.ERRATUM_3_ADMITTED_AT_EPOCH_S + 1, True),
            (h.ERRATUM_3_ADMITTED_AT_EPOCH_S + .5, True),
            (None, False), ('1791738001', False), (True, False),
            (float('inf'), False), (float('-inf'), False), (float('nan'), False), ([], False)):
            with self.subTest(t0=t0):
                run = h._Harvest(replace(inputs, plan={'t0_epoch_s': t0}), self.tmp / 'record',
                    h.Seams(harvest_checkout=lambda: {}), prepare_desk=False, run_g3=False)
                self.assertEqual(run.calibration_bracket['erratum_3_governed'], governed)
                self.assertEqual(run.calibration_bracket['trigger_scope'],
                                 'window_evidence' if governed else 'sealed')
        self.assertEqual(h.ERRATUM_3_ADMITTED_AT_EPOCH_S, 1791738000)

    def test_items1_7_8_governed_worked_example_summary_and_output_digest(self):
        window = self.governed_window()
        record, scopes = self.harvest_with_bracket(window)
        expected = {'erratum_3_governed': True, 'trigger_scope': 'window_evidence', 'evaluated': True,
            'status': 'passed', 'reasons': [], 'freshness': 'fresh',
            'observed_triggers': [SYSTEMATIC], 'recorded_only_triggers': [SYSTEMATIC],
            'corpus_doubling': {'count': 43, 'threshold': 48}, 'other_session_systematic_sequences': [456]}
        self.assertEqual(scopes, ['window_evidence'])
        self.assertEqual(record['calibration_bracket'], expected)
        self.assertEqual(h.read_json(window.archive / 'harvest.json')['calibration_bracket'], expected)
        self.assertNotIn('calibration.bracket_acceptance_failed', window.codes())
        evaluation = window.archive / 'withheld/bracket-evaluation.json'
        self.assertEqual(record['outputs']['withheld/bracket-evaluation.json'], window_tests.sha(evaluation))
        self.assertEqual(h.read_json(evaluation)['assessment']['b_fiducial_s'], .045031)
        self.assertEqual(record['harvest_checkout']['files']['joulewise/calibration_bracketing.py'],
                         window_tests.sha(REPO / 'joulewise/calibration_bracketing.py'))

    def test_items1_7_8_ungoverned_stale_window_emits_unchanged_flag(self):
        window = self.governed_window(t0=h.ERRATUM_3_ADMITTED_AT_EPOCH_S)
        record, scopes = self.harvest_with_bracket(window)
        self.assertEqual(scopes, ['sealed'])
        self.assertIn('calibration.bracket_acceptance_failed', window.codes())
        self.assertEqual(record['calibration_bracket'], {
            'erratum_3_governed': False, 'trigger_scope': 'sealed', 'evaluated': True,
            'status': 'failed', 'reasons': ['calibration_acceptance_bound_stale'], 'freshness': 'stale',
            'observed_triggers': [SYSTEMATIC], 'recorded_only_triggers': [], 'corpus_doubling': None,
            'other_session_systematic_sequences': []})
        path = window.archive / 'withheld/bracket-evaluation.json'
        self.assertEqual(record['outputs'][path.relative_to(window.archive).as_posix()], window_tests.sha(path))

    def test_item8_not_evaluated_nulls_empty_lists_and_scope(self):
        for governed in (False, True):
            window = self.governed_window(str(governed),
                h.ERRATUM_3_ADMITTED_AT_EPOCH_S + int(governed))
            plan = h.read_json(window.plan_path)
            plan['hazard_window']['bracket_session_id'] = None
            window_tests.put(window.plan_path, plan)
            with mock.patch.object(br, 'calibration_bracket_for_bundles') as evaluate:
                record = window.harvest()
            evaluate.assert_not_called()
            self.assertEqual(record['calibration_bracket'], {
                'erratum_3_governed': governed, 'trigger_scope': 'window_evidence' if governed else 'sealed',
                'evaluated': False, 'status': None, 'reasons': [], 'freshness': None,
                'observed_triggers': [], 'recorded_only_triggers': [], 'corpus_doubling': None,
                'other_session_systematic_sequences': []})
            self.assertIn('calibration.no_bracket', window.codes())
            self.assertNotIn('withheld/bracket-evaluation.json', record['outputs'])

    def test_item5_own_post_systematic_emits_both_codes_and_is_not_evaluated(self):
        window = self.governed_window()
        prefix = zlib.decompress(base64.b85decode(window_tests.PREFIX.read_bytes()))
        window.ledger.write_bytes(prefix)
        cutoff = self.evaluator.artifact['ledger_cutoff']
        window_tests.put(window.pin, {'sequence': cutoff['sequence'], 'head_digest': cutoff['head_digest'],
                                      'ledger_schema': cl.LEDGER_SCHEMA})
        old_snapshot = self.evaluator.fixture(systematics=())[0]
        epoch = dict(old_snapshot.bracket_session_by_id['session-alpha'].finalized_slots['pre'].identity_epoch)
        t1 = dict(self.evaluator.helper.bindings)
        slots = {slot: {'attempt_id': f'{window_tests.SESSION_ID}-{slot}',
            'custody_locator': str(window.claim / 'instrument_validation' / f'{window_tests.SESSION_ID}-{slot}'),
            'identity_epoch': epoch, 't1_bindings': t1} for slot in ('pre', 'post')}
        cl.append_bracket_session_receipt(window.ledger, session_id=window_tests.SESSION_ID,
            window_id=window_tests.PLAN_ID, plan_id=window_tests.PLAN_ID,
            plan_sha256=window_tests.sha(window.pack / 'calibration_plan.json'),
            evidence_root_id=window_tests.EVIDENCE_ROOT_ID, runs_root=window.claim, slots=slots,
            head_pin_path=window.pin, require_committed_pin=False)
        for slot in ('pre', 'post'):
            capture = Path(slots[slot]['custody_locator'])
            cl.finalize_bracket_session_slot(window.ledger, session_id=window_tests.SESSION_ID, slot=slot,
                disposition='valid' if slot == 'pre' else 'systematic-invalid', custody_locator=str(capture),
                artifact_sha256=cl.artifact_hashes(capture), identity_epoch=epoch, t1_bindings=t1,
                capture_wall_time_s='99.0' if slot == 'pre' else '111.0',
                exact_bound_lexeme_s='0.028' if slot == 'pre' else '0.037')
        with mock.patch.object(br, 'calibration_bracket_for_bundles') as evaluate:
            record = window.harvest()
        evaluate.assert_not_called()
        self.assertTrue({'calibration.capture_invalid', 'calibration.binding_failed'} <= window.codes())
        self.assertFalse(record['calibration_bracket']['evaluated'])

    def test_gate_gamma_shaped_stale_window_removing_codes(self):
        window = self.governed_window('gamma')
        # The existing GAMMA helper shape is science with an analysis manifest
        # and claim-root references without one. G3's process seam is explicit.
        manifest = {}
        window_tests.put(window.pack / 'analysis_manifest_v3.json', manifest)
        stored, reasons = self.evaluator.evaluate(scope='sealed')
        row = {'status': 'failed', 'member_failures': [], 'bundle_ids': [],
               'idle_admission_core': {'conditions': list(reasons), 'instrument_calibration_bracket': stored},
               'calibration_bracket': stored}
        window_tests.put(window.claim / 'whole-window-verdict.json', row)
        (window.claim / 'bracket-binding.json').write_text('{}\n')
        observed = []
        def g3_runner(argv, **kwargs):
            observed.append(argv)
            # Execute the sealed recomputation, then deliver the checker row
            # through the same subprocess seam the existing G3 tests use.
            result, reasons = self.evaluator.evaluate(scope='sealed')
            self.assertEqual(reasons, ('calibration_acceptance_bound_stale',))
            window_tests.put(Path(argv[argv.index('--report-json') + 1]),
                {'assertions': [{'id': 'F5-2', 'status': 'FAIL'}]})
            return types.SimpleNamespace(returncode=1, stdout='', stderr='')
        record, _ = self.harvest_with_bracket(window, seams=h.Seams(
            group_alive=lambda pgid: False, exclusions_compute=window_tests.EXCLUSIONS,
            runner=g3_runner, boot_session_uuid=lambda: 'B5-TEST-BOOT'))
        self.assertEqual(len(observed), 1)
        self.assertIn('--full-window', observed[0])
        self.assertIn('g3.recompute_failed', window.codes())
        self.assertIn('whole_window.not_passed', window.codes())
        # Fixture limitations produce independent removals; pin the FULL list.
        self.assertEqual(record['exclude_window_reasons'], ['calibration.capture_battery_unmeasured',
                         'neg8.bound_not_derived', 'neg8.screen_failed'])
        self.assertNotIn('calibration.bracket_acceptance_failed', record['exclude_window_reasons'])
        control = self.governed_window('gamma-fresh')
        window_tests.put(control.pack / 'analysis_manifest_v3.json', {})
        fresh_fixture = self.evaluator.fixture(systematics=())
        fresh_bracket, fresh_reasons = self.evaluator.evaluate(fresh_fixture, scope='sealed')
        self.assertEqual((fresh_bracket['status'], fresh_reasons), ('passed', ()))
        fresh_row = copy.deepcopy(row)
        fresh_row['idle_admission_core']['conditions'] = []
        fresh_row['calibration_bracket'] = fresh_bracket
        fresh_row['idle_admission_core']['instrument_calibration_bracket'] = fresh_bracket
        window_tests.put(control.claim / 'whole-window-verdict.json', fresh_row)
        (control.claim / 'bracket-binding.json').write_text('{}\n')
        def fresh_g3(argv, **kwargs):
            result, reasons = self.evaluator.evaluate(fresh_fixture, scope='sealed')
            self.assertEqual((result['status'], reasons), ('passed', ()))
            window_tests.put(Path(argv[argv.index('--report-json') + 1]),
                             {'assertions': [{'id': 'F5-2', 'status': 'PASS'}]})
            return types.SimpleNamespace(returncode=0, stdout='', stderr='')
        control_record, _ = self.harvest_with_bracket(control, fixture=fresh_fixture, seams=h.Seams(
            group_alive=lambda pgid: False, exclusions_compute=window_tests.EXCLUSIONS,
            runner=fresh_g3, boot_session_uuid=lambda: 'B5-TEST-BOOT'))
        self.assertEqual(control_record['exclude_window_reasons'], record['exclude_window_reasons'])
        self.assertNotIn('g3.recompute_failed', control.codes())

    def test_item5_pre_systematic_abort_has_no_bracket_and_no_evaluation(self):
        # The harvest gate of the sealed exit-12 path: the synthetic ledger
        # holds a failed pre, no post, and the session's terminal abort.
        with tempfile.TemporaryDirectory(prefix='erratum3-aborted-pre-') as directory:
            window = window_tests.Window(Path(directory), prefix_ledger=True)
            window.ledger.write_bytes(zlib.decompress(base64.b85decode(window_tests.PREFIX.read_bytes())))
            cutoff = self.evaluator.artifact['ledger_cutoff']
            window_tests.put(window.pin, {'sequence': cutoff['sequence'], 'head_digest': cutoff['head_digest'],
                                          'ledger_schema': cl.LEDGER_SCHEMA})
            plan = h.read_json(window.plan_path)
            plan['t0_epoch_s'] = h.ERRATUM_3_ADMITTED_AT_EPOCH_S + 1
            window_tests.put(window.plan_path, plan)
            epoch, t1 = self.evaluator.artifact['identity_epoch'], self.evaluator.helper.bindings
            slots = {slot: {'attempt_id': f'{window_tests.SESSION_ID}-{slot}',
                'custody_locator': str(window.claim / 'instrument_validation' / f'{window_tests.SESSION_ID}-{slot}'),
                'identity_epoch': epoch, 't1_bindings': t1} for slot in ('pre', 'post')}
            cl.append_bracket_session_receipt(window.ledger, session_id=window_tests.SESSION_ID,
                window_id=window_tests.PLAN_ID, plan_id=window_tests.PLAN_ID,
                plan_sha256=window_tests.sha(window.pack / 'calibration_plan.json'),
                evidence_root_id=window_tests.EVIDENCE_ROOT_ID, runs_root=window.claim, slots=slots,
                head_pin_path=window.pin, require_committed_pin=False)
            capture = Path(slots['pre']['custody_locator'])
            cl.finalize_bracket_session_slot(window.ledger, session_id=window_tests.SESSION_ID, slot='pre',
                disposition='systematic-invalid', custody_locator=str(capture),
                artifact_sha256=cl.artifact_hashes(capture), identity_epoch=epoch, t1_bindings=t1,
                capture_wall_time_s='99.0', exact_bound_lexeme_s='0.037')
            cl.abort_bracket_session(window.ledger, session_id=window_tests.SESSION_ID,
                                     reason='pre_calibration_above_screen')
            window_tests.put(window.custody / 'night/chain.exited', {'epoch_s': 1.0, 'exit_code': 12})
            inputs = h.resolve_inputs(window.plan_path)
            run = h._Harvest(inputs, window.archive, h.Seams(harvest_checkout=lambda: {}),
                             prepare_desk=False, run_g3=False)
            run.archive_inputs()
            run.roster = h.build_roster(window.pack, window.measurement)
            run.pack_copy, run.repo_root_copy = window.pack, window.measurement
            with mock.patch.object(br, 'calibration_bracket_for_bundles') as evaluate:
                run.calibration()
            evaluate.assert_not_called()
            self.assertIn('calibration.no_bracket', {flag['code'] for flag in run.flags.records})
            self.assertFalse(run.calibration_bracket['evaluated'])


class RecoveryStaleGateTests(unittest.TestCase):
    def setUp(self):
        self.sources = source_tests.SourceRecoveryTests()
        self.sources.setUp()
        self.addCleanup(self.sources.doCleanups)
        self.sources.stack.enter_context(mock.patch.object(h, 'sha256_file', side_effect=lambda path:
            hashlib.sha256(Path(path).read_bytes()).hexdigest()))
        real_lstat = Path.lstat
        def lstat(path, **kwargs):
            if path != self.sources.root and self.sources.root not in path.parents:
                return real_lstat(path, **kwargs)
            if path in self.sources.files:
                return types.SimpleNamespace(st_mode=stat.S_IFREG)
            if any(path in item.parents for item in self.sources.files):
                return types.SimpleNamespace(st_mode=stat.S_IFDIR)
            raise FileNotFoundError(str(path))
        self.sources.stack.enter_context(mock.patch.object(Path, 'lstat', lstat))
        self.evaluator = WindowEvidenceTests()
        self.evaluator.setUp()

    def test_gate_governed_stale_bracket_and_source_less_recovery(self):
        fixture = self.evaluator.fixture()
        sealed, reasons = self.evaluator.evaluate(fixture, scope='sealed')
        self.assertIsNone(sealed['pre'])
        self.sources.plan['t0_epoch_s'] = h.ERRATUM_3_ADMITTED_AT_EPOCH_S + 1
        self.sources.add_bundleless_spare()
        self.sources.row.update(status='failed', member_failures=[], calibration_bracket=sealed)
        self.sources.row['idle_admission_core']['conditions'].extend(reasons)
        self.sources.row['idle_admission_core']['instrument_calibration_bracket'] = sealed
        self.sources.basis()
        self.sources.row['evaluation_basis'] = source_tests.ww.build_evaluation_basis(
            policy_sha256=self.sources.policy_sha,
            member_occurrences=self.sources.row['evaluation_basis']['member_occurrences'],
            calibration_bracket=sealed)
        self.assertIsNotNone(source_tests.ww._validated_evaluation_basis(self.sources.row, self.sources.runs))
        self.assertNotIn('launch_lineage', self.sources.row['evaluation_basis'])
        self.assertEqual(self.sources.row['evaluation_basis']['calibration_bracket_set']['pre'], None)
        run = self.sources.harvest()
        root = self.sources.root
        run.inputs.bracket_session_id = 'session-alpha'
        run.inputs.measurement_root = root / 'measurement'
        run.inputs.ledger_path = root / 'ledger.jsonl'
        run.pack_copy, run.repo_root_copy = root / 'pack', root / 'measurement'
        run.roster.update(plan={'path': 'calibration_plan.json', 'plan_id': 'plan-alpha'},
            window_identity={'window_id': 'window-alpha', 'evidence_root_id': 'evidence-alpha'},
            campaign_policy={'path': window_tests.POLICY},
            acceptance_policy={'issued_artifact_sha256': br._acceptance_artifact_sha256(self.evaluator.artifact)})
        self.sources.put(run.pack_copy / 'calibration_plan.json', {'plan_id': 'plan-alpha'})
        self.sources.files[root / 'sources/inputs/acceptance.json'] = br.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()
        self.sources.put(root / 'sources/ledger/calibration_observation_ledger.jsonl', {})
        self.sources.put(root / 'sources/ledger/calibration_ledger_head.json', {})
        self.sources.put(run.repo_root_copy / window_tests.POLICY,
                         h.read_json(REPO / window_tests.POLICY))
        snapshot, candidates, binding = fixture
        session = snapshot.bracket_session_by_id['session-alpha']
        updated_slots = {}
        for slot, observation in session.finalized_slots.items():
            capture = root / 'captures' / slot
            for name in observation.artifact_sha256:
                self.sources.put(capture / name, {})
            hashes = {name: h.sha256_file(capture / name) for name in observation.artifact_sha256}
            updated_slots[slot] = replace(observation, custody_locator=str(capture), artifact_sha256=hashes)
        snapshot = replace(snapshot, bracket_sessions=(*self.evaluator.prefix.bracket_sessions,
            replace(session, runs_root=str(run.inputs.claim_runs_root), finalized_slots=updated_slots,
                    plan_sha256=h.sha256_file(run.pack_copy / 'calibration_plan.json'))))
        for run_id, member in run.members.items():
            member.update(bundle_path=str(run.inputs.claim_runs_root / run_id), anchor_recorded='bounded')
        initial = h._Harvest(types.SimpleNamespace(plan=self.sources.plan, plan_id='synthetic-gate',
            attempt=1, h_claim='a' * 40, catalog_path=window_tests.FIXTURES / 'flag_catalog.json'),
            root, h.Seams(harvest_checkout=lambda: {}), prepare_desk=False, run_g3=False)
        run.calibration_bracket = initial.calibration_bracket
        run.capture_assessments = {}
        scopes = []
        def bracket(*args, **kwargs):
            scopes.append(kwargs['trigger_scope'])
            return self.evaluator.evaluate(fixture, scope=kwargs['trigger_scope'])
        terminal = {'sequence': 484, 'head_digest': snapshot.head_digest, 'ledger_schema': cl.LEDGER_SCHEMA}
        with mock.patch.object(cl, 'terminal_head_pin_for_session', return_value=terminal), \
             mock.patch.object(cl, 'load_calibration_ledger_snapshot', return_value=snapshot), \
             mock.patch.object(br, 'load_calibration_acceptance_bound', return_value=self.evaluator.artifact), \
             mock.patch.object(br, 'build_calibration_bracket_binding', return_value=binding), \
             mock.patch.object(br, 'calibration_bracket_for_bundles', side_effect=bracket), \
             mock.patch.object(h, 'write_once', side_effect=lambda path, raw: (
                 self.sources.files.__setitem__(path, raw), hashlib.sha256(raw).hexdigest())[1]):
            run.calibration()
        self.sources.put(run.inputs.claim_runs_root / 'whole-window-verdict.json', self.sources.row)
        run.whole_window()
        source, screen = self.sources.screen(run)
        self.assertEqual(source, 'survivor_rescreen')
        self.assertTrue(screen['rescreen']['evaluated'])
        self.assertEqual(screen['rescreen']['reference_source']['source'],
                         'claim_campaign_manifests_authenticated')
        self.assertEqual(scopes, ['window_evidence'])
        self.assertEqual(run.calibration_bracket['status'], 'passed')
        codes = sorted({flag['code'] for flag in run.flags.records})
        removing = [code for code in codes if initial.catalog.effect(code) == 'EXCLUDE_WINDOW']
        self.assertEqual(removing, [], [flag for flag in run.flags.records if flag['code'] in removing])
        self.assertIn('whole_window.not_passed', codes)
        self.assertNotIn('calibration.bracket_acceptance_failed', codes)
        self.assertEqual(self.sources.row['row_provenance']['source_campaign_manifests'], [])

