"""R6-8 LOW regressions; synthetic evidence only, no hardware or model access."""
from copy import deepcopy
import json
from pathlib import Path
import signal
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_rehearsal as r1, align_v4_kit as kit
from scripts import align_v4_wp18_fixtures as fixtures
from tests.align import test_r1_runtime as runtime_tests
from tests.align import test_r1_rehearsal as rehearsal_tests
from tests.align import test_v4_kit as kit_tests
from tests.align import test_v4_wp18_fixtures as fixture_tests


def ready():
    inputs, record = kit_tests.ready_inputs()
    record['slots']['S5_fast'] = inputs['R1']['thermal_policy']['delta_fast_c']
    record['thermometry']['D'].update(s_fast='TC0P', s_slow='TG0P')
    record['duty_bar']['verdict'] = 'pass'
    for row in record['deadman_budget']:
        row['duty_bar'] = {'verdict': 'pass', 'pass': True}
    return inputs, record


class RuntimeLowTests(unittest.TestCase):
    def test_unreleased_leg_does_not_hide_other_incompleteness(self):
        segment = object.__new__(rt.Segment)
        segment.out, segment.kind = Path('/synthetic'), 'high-power-aba-b'
        for status, reason, extra in [('failed', 'telemetry_failed', []),
                                      ('failed', 'unknown_error', []),
                                      ('succeeded', None, ['thermal.custody_invalid']),
                                      ('succeeded', None, ['thermal.collector_failed']),
                                      ('succeeded', None, ['thermal.state_unobserved']),
                                      ('succeeded', None, ['episode.deadman:0'])]:
            ep = SimpleNamespace(turns=[], flags=['episode.g0_unreleased:0',
                                                  'thermal.start_gate_timeout', *extra],
                                 hardware={'thermal': {'intervals': [{'kind': 'G0', 'outcome': 'timeout'}]}})
            member = SimpleNamespace(ep=ep, status=status, failure_reason=reason,
                                     bundle=segment.out / 'member')
            segment.step_member = lambda *a, **kw: (member, {'slow_c': 38.0})
            with self.subTest(status=status, reason=reason, extra=extra), self.assertRaises(rt.RuntimeFailure):
                segment.k_step('d_spam', label='leg', leg=True)

    def test_g0_timeout_alone_remains_inconclusive(self):
        # Reuse the R5-3 production-path regression and its NoReleaseBackend.
        runtime_tests.Round5RuntimeTests(
            'test_aba_leg_without_its_own_g0_release_is_inconclusive_not_a_failure'
        ).test_aba_leg_without_its_own_g0_release_is_inconclusive_not_a_failure()

    def test_managed_closes_defer_a_signal_until_the_close_returns(self):
        # Exec LOW-3: a first TERM inside a session close (e.g. between the
        # powermetrics adapter dropping its handle and stopping the process)
        # is delivered only after the close has returned.
        for through_segment_close in (False, True):
            with self.subTest(segment_close=through_segment_close):
                segment = object.__new__(rt.Segment)
                segment.heaters, segment.inventory_readers, segment._stop_inventory = [], [], None
                segment._stop_ticker = None
                events = []

                class Managed:
                    def close(inner):
                        events.append('enter')
                        signal.raise_signal(signal.SIGTERM)
                        events.append('returned')
                managed = Managed()
                segment.open_sessions = [managed]

                def handler(*_args):
                    events.append('TERM')
                original = signal.signal(signal.SIGTERM, handler)
                try:
                    if through_segment_close:
                        self.assertEqual(segment.close(), [])
                    else:
                        segment.close_session(managed)
                    self.assertEqual(events, ['enter', 'returned', 'TERM'])
                    self.assertIs(signal.getsignal(signal.SIGTERM), handler)
                    self.assertEqual(segment.open_sessions, [])
                finally:
                    signal.signal(signal.SIGTERM, original)

    def test_a_deferred_term_still_reaches_a_raising_handler(self):
        segment = object.__new__(rt.Segment)
        events = []

        class Managed:
            def close(inner):
                signal.raise_signal(signal.SIGTERM)
                events.append('closed')
        managed = Managed()
        segment.open_sessions = [managed]

        def handler(signum, _frame):
            raise SystemExit(128 + signum)
        original = signal.signal(signal.SIGTERM, handler)
        try:
            with self.assertRaises(SystemExit):
                segment.close_session(managed)
            self.assertEqual(events, ['closed'])
            self.assertEqual(segment.open_sessions, [])   # closed, so never closed twice
        finally:
            signal.signal(signal.SIGTERM, original)

    def test_failed_normal_close_remains_available_for_teardown_retry(self):
        segment = object.__new__(rt.Segment)
        segment.heaters, segment.inventory_readers, segment._stop_inventory = [], [], None
        segment._stop_ticker = None
        attempts = []
        class Managed:
            def close(inner):
                attempts.append(len(attempts))
                if len(attempts) == 1:
                    raise RuntimeError('retry close')
        managed = Managed()
        segment.open_sessions = [managed]
        with self.assertRaises(RuntimeError):
            segment.close_session(managed)
        self.assertEqual(segment.open_sessions, [managed])
        self.assertEqual(segment.close(), [])
        self.assertEqual(len(attempts), 2)

    def test_step_d_records_and_driver_preserves_s5_fast(self):
        ns = rt.NS
        turn = SimpleNamespace(start_ns=100 * ns, first_token_ns=120 * ns, end_ns=520 * ns,
                               decode_tokens=4000, prefill_tokens=10000)
        ep = SimpleNamespace(start_ns=100 * ns, end_ns=525 * ns, hardware={})
        response = {'key': 'K', 'delta_t_c': 5.0, 't63_s': 3.0, 'tau_s': 80.0}
        slots, _ = rt.derive_step_d_slots(
            ep=ep, turn=turn, wall_s=800, responses={'s_fast': response, 's_slow': response},
            recovery_s=50, recovery_censored=False,
            bands={'delta_fast_c': 1.2, 'delta_slow_c': 1.5},
            t_decline_s=200, t_decline_status='declined', d_class='heavy')
        self.assertEqual(slots.get('S5_fast'), 1.2)
        self.assertEqual(r1.derive_slots({'slots': slots})['S5_fast'], 1.2)

    def test_idle_records_sensor_roles_for_the_soak_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = runtime_tests.rs.synthetic_config(root / 'config')
            code, result = runtime_tests.call(config, root / 'idle', 'idle', '--duration-s', '2')
            self.assertEqual(code, 0)
            self.assertEqual(result.get('sensor_roles'), json.loads(config.read_text())['sensors'])


class KitLowTests(unittest.TestCase):
    def test_duty_aggregate_rederived_with_fail_then_inconclusive_priority(self):
        for verdicts, expected in [(('pass', 'inconclusive', 'fail'), 'fail'),
                                   (('pass', 'inconclusive', 'pass'), 'inconclusive')]:
            inputs, record = ready()
            for row, verdict in zip(record['deadman_budget'], verdicts):
                row['duty_bar'] = {'verdict': verdict, 'pass': verdict == 'pass'}
            with self.subTest(verdicts=verdicts), self.assertRaisesRegex(ValueError, 'duty'):
                kit.check_r1_evidence(inputs, record)
            record['duty_bar'] = {'verdict': expected, 'pass': False, 'schedule': kit_tests.R6_1_SCHEDULE,
                                  'lead_fallback': {'step': 1, 'authority': 'synthetic lead'}}
            # R11 Track 1 / R08 (7895b9e7e) removed the lead-fallback acceptance: a failed duty bar needs a
            # qualified remeasured R1 record, so the aggregate is rederived and the fallback alone refuses.
            with self.subTest(verdicts=verdicts, step='fallback'), \
                    self.assertRaisesRegex(ValueError, 'no lead fallback step alone qualifies'):
                kit.check_r1_evidence(inputs, record)

    def test_duty_pass_boolean_and_per_run_verdicts_are_checked(self):
        for change in ('boolean', 'missing', 'unknown'):
            inputs, record = ready()
            if change == 'boolean':
                record['duty_bar']['verdict'] = 'fail'
                # A false aggregate verdict must never keep pass=True.
                for row in record['deadman_budget']:
                    row['duty_bar'] = {'verdict': 'fail', 'pass': False}
            elif change == 'missing':
                del record['deadman_budget'][0]['duty_bar']
            else:
                record['deadman_budget'][0]['duty_bar']['verdict'] = 'unknown'
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'duty'):
                kit.check_r1_evidence(inputs, record)

    def test_fast_band_must_match_s5_fast(self):
        for value in (25.0, True, None):
            inputs, record = ready()
            inputs['R1']['thermal_policy']['delta_fast_c'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'S5_fast'):
                kit.check_r1_evidence(inputs, record)
        inputs, record = ready()
        del record['slots']['S5_fast']
        with self.assertRaisesRegex(ValueError, 'S5_fast'):
            kit.check_r1_evidence(inputs, record)

    def test_policy_sensor_must_be_the_pick_even_when_in_candidate_list(self):
        for role, listing in (('s_fast', 'die_candidates'), ('s_slow', 'heatsink_candidates')):
            inputs, record = ready()
            record['thermometry']['D'][listing].append('OTHER')
            inputs['R1']['thermal_policy']['sensors'][role] = 'OTHER'
            with self.subTest(role=role), self.assertRaisesRegex(ValueError, 'pick'):
                kit.check_r1_evidence(inputs, record)


class RehearsalLowTests(unittest.TestCase):
    def test_soak_reference_checks_slow_role_only_and_records_roles(self):
        with tempfile.TemporaryDirectory() as td:
            row = {'name': 'idle_soak', 'output_dir': td, 'attempt': 0,
                   'result': {'sensor_roles': {'s_fast': 'FAST', 's_slow': 'SLOW'}},
                   'soak_detrended': {'FAST': {'mean_c': 45.0}, 'SLOW': {'mean_c': 40.0}}}
            path = r1.write_soak_reference(Path(td), row)
            # Supply roles for the pre-fix check too, so the refusal regression
            # exercises the existing any-sensor comparison.
            value = json.loads(path.read_text())
            value['sensor_roles'] = row['result']['sensor_roles']
            path.write_text(json.dumps(value))
            result = {'reference_source': 'r1_soak_reference', 'reference_c': 45.0}
            with self.assertRaisesRegex(r1.Refusal, 's_slow'):
                r1._check_soak_reference_consumed('gated', result, path)
            result['reference_c'] = 40.0
            r1._check_soak_reference_consumed('gated', result, path)
            value.pop('sensor_roles')
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(r1.Refusal, 's_slow'):
                r1._check_soak_reference_consumed('gated', result, path)
            path = r1.write_soak_reference(Path(td), row)
            self.assertEqual(json.loads(path.read_text())['sensor_roles'], row['result']['sensor_roles'])

    def test_recovery_curve_rejects_bad_rows_and_decreasing_times(self):
        bad = [[[0]], [[0, 40, 2]], [(0, 40)], [[True, 40]], [[0, False]],
               [['0', 40]], [[0, '40']], [[float('nan'), 40]], [[0, float('inf')]],
               [[1, 40], [0, 39]]]
        for curve in bad:
            with self.subTest(curve=curve), tempfile.TemporaryDirectory() as td:
                world = rehearsal_tests.FakeWorld()
                def run(argv, **kwargs):
                    answer = world(argv, **kwargs)
                    if '--r1-kind' in argv and argv[argv.index('--r1-kind') + 1] == 'idle-until-soak':
                        value = json.loads(answer.stdout)
                        value['recovery_curve'] = curve
                        # tuples become lists over JSON; exercise a non-list row
                        # with an object for that transport case.
                        if isinstance(curve[0], tuple):
                            value['recovery_curve'] = [{'t_s': 0, 'S_slow': 40}]
                        answer.stdout = json.dumps(value)
                    return answer
                args = rehearsal_tests.R1Tests().args(td, include_4bit=False)
                with patch.object(r1, '_run', run), patch.object(r1, '_now_local', lambda: rehearsal_tests.NOON_SAFE):
                    self.assertEqual(r1.run(args), 3)
                self.assertIn('recovery curve', json.loads((args.output / 'r1_result.json').read_text())['error'])


class FixtureLowTests(unittest.TestCase):
    def setUp(self):
        self.case = fixture_tests.WP18FixtureTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def test_turn_rows_must_be_this_members_turns(self):
        # Cold pass LOW-5: a row's own turn index and per-turn seed (the seed
        # law of the member's episode seed) must match; a row from another
        # member (another seed) or another turn is refused.
        other_seed = fixtures.ARMS['Y'][3]
        for arm in ('X', 'Y'):
            seed = fixtures.ARMS[arm][3]
            changes = {
                'turn_shifted': lambda r: r.update(turn=r['turn'] + 1),
                'turn_missing': lambda r: r.pop('turn'),
                'turn_bool': lambda r: r.update(turn=True) if r['turn'] == 1 else r.update(turn='x'),
                'other_member_seed': lambda r: r['generation']['sampler'].update(
                    per_turn_seed=fixtures.turn_seed(other_seed if arm == 'X' else fixtures.ARMS['X'][3], r['turn'])),
                'other_turn_seed': lambda r: r['generation']['sampler'].update(
                    per_turn_seed=fixtures.turn_seed(seed, r['turn'] + 1)),
                'seed_missing': lambda r: r['generation'].pop('sampler'),
                'seed_string': lambda r: r['generation']['sampler'].update(
                    per_turn_seed=str(r['generation']['sampler']['per_turn_seed'])),
            }
            for name, change in changes.items():
                rows = deepcopy(self.case.rows[arm])
                change(rows[-1])
                with self.subTest(arm=arm, change=name), self.assertRaisesRegex(ValueError, 'turn|per_turn_seed'):
                    fixtures.build_fixture(arm, b''.join(fixture_tests.json_bytes(row) for row in rows),
                                           self.case.pilot_path.read_bytes())

    def test_summary_seed_is_the_members_seed_index(self):
        # Round-6 Sol critique: the pilot desk records Episode.seed, the seed
        # index (16 / 14), not the derived 64-bit episode seed.
        for arm, other in (('X', 'Y'), ('Y', 'X')):
            for value, ok in ((fixtures.ARMS[arm][2], True), (fixtures.ARMS[arm][3], True),
                              (fixtures.ARMS[other][2], False), (fixtures.ARMS[other][3], False)):
                pilot = json.loads(self.case.pilot_path.read_bytes())
                for member in pilot['members']:
                    if member['run_id'] == fixtures.ARMS[arm][0]:
                        member['summary']['seed'] = value
                args = (arm, b''.join(fixture_tests.json_bytes(row) for row in self.case.rows[arm]),
                        fixture_tests.json_bytes(pilot))
                with self.subTest(arm=arm, value=value):
                    if ok:
                        fixtures.build_fixture(*args)
                    else:
                        with self.assertRaisesRegex(ValueError, 'summary seed'):
                            fixtures.build_fixture(*args)

    def test_extractor_and_kit_round_trip(self):
        self.case.run_tool()
        inputs = json.loads(self.case.inputs_path.read_bytes())
        kit.validate_wp18_fixtures(inputs, self.case.root)

    def test_kit_checks_turn_contents_and_exact_source_digests(self):
        self.case.run_tool()
        inputs = json.loads(self.case.inputs_path.read_bytes())
        path = self.case.root / kit.WP18_FIXTURES['X']
        good = json.loads(path.read_bytes())
        changes = [lambda v: v['turns'][0].update(turn=99),
                   lambda v: v['turns'][0].update(turn=False),
                   lambda v: v['turns'][0].pop('turn'),
                   lambda v: v.pop('sources'),
                   lambda v: v['sources'].update(extra='a' * 64),
                   lambda v: v['sources'].pop('align_turns_jsonl_sha256'),
                   lambda v: v['sources'].update(p7_pilot_json_sha256='invalid')]
        for field in fixtures.TOKEN_FIELDS:
            for value in ([], [-1], [True], [1.5], 'tokens', None):
                changes.append(lambda v, f=field, x=value: v['turns'][0].update({f: x}))
        for index, change in enumerate(changes):
            value = deepcopy(good)
            change(value)
            raw = fixture_tests.json_bytes(value)
            path.write_bytes(raw)
            inputs['WP18']['X']['token_fixture_sha256'] = kit.sha(raw)
            with self.subTest(change=index), self.assertRaises(ValueError):
                kit.validate_wp18_fixtures(inputs, self.case.root)

    def test_extractor_rejects_negative_token_ids(self):
        for field in fixtures.TOKEN_FIELDS:
            rows = deepcopy(self.case.rows['X'])
            rows[0]['generation'][field][0] = -1
            # No summary ID cross-check: token validation itself must refuse.
            members = deepcopy(self.case.members)
            for member in members:
                member['summary'].pop('per_turn_' + field)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                fixtures.build_fixture('X', b''.join(fixture_tests.json_bytes(row) for row in rows),
                                       fixture_tests.json_bytes({'members': members}))
