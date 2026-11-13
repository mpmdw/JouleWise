"""B3 slot record desk (spec 2.3): synthetic r1_result.json from test_w1_rl122_kit.planning_slots.

No host or study data. The 11-12 regression (spec 2.3 item 7) runs only when
JW_SLOT_DESK_NIGHT_1112 (the 11-12 night dir .../night/align-r1) and
JW_SLOT_DESK_CUSTODY_1112 (its custody root $S) are set.
"""
from copy import deepcopy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts import align_r1_rehearsal as r1
from scripts import align_r1_slot_record_desk as desk
from tests.align.test_w1_rl122_kit import planning_slots

NIGHT = 'a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe'
PACKET = '8' * 64


def base_result(names=('planning_turn_R_plus_4C',)):
    _, slots = planning_slots(list(names))
    slots['thermometry']['D'].update(
        s_fast='TV0h', s_slow='TVh0', flags=[],
        night_confirmation={'ok': True, 'reasons': [], 's_fast': 'TV0h', 's_slow': 'TVh0', 'authority': 'RL-78'})
    for row in slots['deadman_budget']:
        row.update(T_dead_s=1000.0, duty_T_dead_s=1000.0, inconclusive_reason=None)
        row['duty_bar'] = {'verdict': 'pass', 'pass': True}
    slots['duty_bar'].update(duty_T_dead_s=1000.0)
    slots['high_power'] = {'verdict': 'not_adopted', 'reason': 'all legs infinite',
                           't_decline_s': {'A1': 98.665, 'B': 98.845, 'A2': 98.856},
                           'start_state_bars': {'pass': True}}
    slots['s6_tuning'] = {'G1_median_s': 80.0, 'H_median_s': 40.0, 'G1_waits': 3, 'H_waits': 3}
    slots['x_g'].update(x7=False, admitted_turns=4)
    slots['g0_waits'] = [{'segment': n, 'g0_outcome': 'released', 'g0_wait_s': 100.0}
                         for n in ('step_30b', 'step_D_prefill_10k_decode_4096')]
    slots['g0_waits'] += [{'segment': n, 'g0_outcome': 'timeout', 'g0_wait_s': 1200.0} for n in names]
    slots['skipped_segments'] = {}
    slots['calibration_precools'] = {'cooldown_after_D': True}
    slots['powermode'] = [{'point': 'restored', 'mode': 0}]
    return {**slots, 'status': 'complete', 'executed_commit': NIGHT, 'prepare_packet': {'sha256': PACKET},
            'phases': []}


class Night:
    """A synthetic RUN_DIR + custody root on disk."""

    def __init__(self, tmp, result, *, runtime=None, reaps=None, chain_exit=0, metadata=True):
        self.root = Path(tmp) / 'S'
        self.run = self.root / 'night' / 'align-r1'
        self.run.mkdir(parents=True)
        slots_raw = json.dumps({'schema': 'joulewise.align.r1_slots.v1', 'executed_commit': NIGHT}).encode()
        (self.run / 'r1_slots.json').write_bytes(slots_raw)
        result = dict(result)
        result.setdefault('registration_sha256', hashlib.sha256(slots_raw).hexdigest())
        (self.run / 'r1_result.json').write_text(json.dumps(result))
        (self.root / 'result.json').write_text(json.dumps({'chain_outcome': 'COMPLETE', 'chain_exit_code': chain_exit,
                                                           'fault': False, 'census_hits': []}))
        runtime = runtime if runtime is not None else {
            'X_G_contrast': {'episode_flags': [], 'admitted_turns': 4, 'gate_waits_s': {'G1': [50.0], 'H': []},
                             'cpu_busy_t_s': [0.0, 1.0, 2.0], 'census': []},
            'step_30b': {'episode_flags': [], 'cpu_busy_t_s': [0.0, 1.0, 1.2, 2.2], 'census': []}}
        for name, value in runtime.items():
            (self.run / name).mkdir(exist_ok=True)
            (self.run / name / 'runtime_result.json').write_text(json.dumps(value))
            bundle = self.run / name / 'runs' / 'r'
            (bundle / 'outputs').mkdir(parents=True)
            if metadata:
                device = {} if not (reaps or {}).get(name) else {'capture_reaps': reaps[name]}
                (bundle / 'metadata.json').write_text(json.dumps({'device': device}))
            (bundle / 'outputs' / 'align_thermal.jsonl').write_text('\n'.join(
                json.dumps({'kind': 'reading', 'started': {'monotonic_ns': int(t * 1e9)}}) for t in (0, 1, 2)) + '\n')

    def build(self, packet=PACKET):
        return desk.build(self.run, self.root, NIGHT, packet)


def record_for(result, **kwargs):
    with tempfile.TemporaryDirectory() as tmp:
        return Night(tmp, result, **kwargs).build()


class IdentityTests(unittest.TestCase):
    def test_all_clear(self):
        rec = record_for(base_result())
        self.assertTrue(rec['identity']['ok'], rec['identity'])

    def test_each_failure_breaks_identity(self):
        cases = {'refused': (lambda r: r.update(status='refused'), {}),
                 'exit 3': (lambda r: None, {'chain_exit': 3}),
                 'commit': (lambda r: r.update(executed_commit='0' * 40), {}),
                 'slot hash': (lambda r: r.update(registration_sha256='f' * 64), {}),
                 'packet': (lambda r: r.update(prepare_packet={'sha256': '9' * 64}), {})}
        for label, (mutate, kw) in cases.items():
            result = base_result()
            mutate(result)
            with self.subTest(label):
                self.assertFalse(record_for(result, **kw)['identity']['ok'])


class ThermometryTests(unittest.TestCase):
    def test_not_fired_on_ok_confirmation(self):
        self.assertFalse(record_for(base_result())['thermometry']['t4_fired'])

    def test_each_arm_fires(self):
        def conf(r):
            return r['thermometry']['D']['night_confirmation']
        arms = {'bar': lambda r: r['thermometry'].update(bar='fail'),
                'ok false': lambda r: conf(r).update(ok=False),
                'ok missing': lambda r: conf(r).pop('ok'),
                'pair': lambda r: conf(r).update(s_slow='Th0C'),
                'inadmissible': lambda r: r['thermometry']['D']['flags'].append('r1.sensor_inadmissible'),
                'aliased': lambda r: r['thermometry'].setdefault('flags', []).append('r1.picks_aliased')}
        for label, mutate in arms.items():
            result = base_result()
            mutate(result)
            with self.subTest(label):
                self.assertTrue(record_for(result)['thermometry']['t4_fired'])


class DutyTests(unittest.TestCase):
    def duty(self, mutate):
        result = base_result()
        mutate(result)
        return record_for(result)['duty']

    def test_pass(self):
        d = self.duty(lambda r: None)
        self.assertEqual((d['verdict'], d['recomputed_overall'], d['recompute_mismatch']), ('pass', 'pass', []))
        self.assertEqual({r['run']: r['verdict'] for r in d['runs']},
                         dict.fromkeys(desk.GATED_D_RUNS, 'pass'))

    def _fail_run(self, r, change):
        row = r['deadman_budget'][0]
        change(row)
        row['duty_bar'] = {'verdict': 'fail', 'pass': False}
        r['duty_bar'].update(verdict='fail', **{'pass': False})

    def test_fail_on_each_check(self):
        for label, change in {'x7': lambda row: row.update(x7=True),
                              'turns': lambda row: row.update(admitted_turns=2),
                              'hold': lambda row: row['phases_s'].update(G0=400.0)}.items():
            with self.subTest(label):
                d = self.duty(lambda r: self._fail_run(r, change))
                self.assertEqual((d['verdict'], d['recomputed_overall'], d['recompute_mismatch']),
                                 ('fail', 'fail', []))

    def test_inconclusive(self):
        def mutate(r):
            r['deadman_budget'][1].update(inconclusive_reason='R6-1', duty_bar={'verdict': 'inconclusive'})
            r['duty_bar'].update(verdict='inconclusive')
        d = self.duty(mutate)
        self.assertEqual((d['verdict'], d['recompute_mismatch']), ('inconclusive', []))

    def test_hold_exactly_at_forty_percent_passes(self):
        # 0.40 x 1000 = 400 = G0 + G1 + H
        d = self.duty(lambda r: r['deadman_budget'][0]['phases_s'].update(G0=160.0, G1=150.0, H=90.0))
        self.assertEqual(d['runs'][0]['gate_hold_s'], 400.0)
        self.assertTrue(d['runs'][0]['checks']['gate_hold_le_40pct_T_dead'])
        self.assertEqual(d['runs'][0]['recomputed_verdict'], 'pass')

    def test_driver_disagreement_is_a_tool_check(self):
        result = base_result()
        result['deadman_budget'][0].update(x7=True)
        rec = record_for(result)
        self.assertEqual(rec['tool_checks']['duty_recompute_mismatch'], [result['deadman_budget'][0]['run']])

    def test_constants_match_the_driver(self):
        self.assertEqual(r1.DUTY_BAR, {'x7': False, 'min_admitted_turns': desk.DUTY_MIN_TURNS,
                                       'max_gate_hold_fraction_of_T_dead': desk.DUTY_MAX_FRACTION})
        self.assertEqual(tuple(n for n, _ in r1.GATED_D_RUNS), desk.GATED_D_RUNS)


class Rl106Tests(unittest.TestCase):
    def test_flag_in_three_places_counts_once_and_superseded_counts(self):
        flag = desk.G0_TIMEOUT_FLAG
        runtime = {'planning_turn_R_plus_4C': {'episode_flags': [flag], 'flags': [flag],
                                               'g0': {'flags': [flag]}},
                   'planning_turn_R_plus_2C.g0_timeout1': {'episode_flags': [flag]},
                   'planning_turn_R_plus_2C': {'episode_flags': []},
                   'X_G_contrast': {'episode_flags': []}}
        n = record_for(base_result(), runtime=runtime)['rl106_n']
        self.assertEqual((n['n_flag'], n['N'], n['n_gate']), (2, 2, None))
        self.assertEqual(n['members'], ['planning_turn_R_plus_2C.g0_timeout1', 'planning_turn_R_plus_4C'])


class Rl91Tests(unittest.TestCase):
    def rl91(self, **kw):
        return record_for(base_result(), **kw)['rl91']

    def test_zero_reaps_ok(self):
        r = self.rl91()
        self.assertTrue(r['ok'])
        self.assertEqual(r['capture_reaps'], [])
        # RL-138 item 9: "none recorded", not "none happened".
        self.assertEqual(r['capture_reaps_summary'], f"no reap record in {r['metadata_files_read']} metadata.json files")
        self.assertGreater(r['metadata_files_read'], 0)

    def test_absent_true_ok_and_listed(self):
        r = self.rl91(reaps={'step_30b': [{'absent': True}]})
        self.assertTrue(r['ok'])
        self.assertEqual(r['capture_reaps'], [{'bundle': 'step_30b/runs/r', 'absent': True, 'reason': None}])

    def test_absent_false_not_ok(self):
        self.assertFalse(self.rl91(reaps={'step_30b': [{'absent': False, 'reason': 'x'}]})['ok'])

    def test_powermetrics_in_census_not_ok(self):
        runtime = {'step_30b': {'census': [{'label': 'start', 'processes': [{'comm': '/usr/bin/powermetrics'}]}]}}
        r = self.rl91(runtime=runtime)
        self.assertFalse(r['ok'])
        self.assertEqual(r['root_powermetrics_in_census'], ['step_30b'])

    def test_ticker(self):
        r = self.rl91()
        self.assertEqual(r['ticker']['load_journal']['members']['step_30b'],
                         {'ticks': 4, 'short': 1, 'fraction': 0.25, 'over_1pct': True})
        self.assertEqual(r['ticker']['thermal_journal']['total'], {'ticks': 6, 'short': 0})

    def test_layout_self_check_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            night = Night(tmp, base_result(), metadata=False)
            with self.assertRaisesRegex(desk.DeskInputError, 'CAPTURE_REAPS_FILE.*confirm in step 0'):
                night.build()
            out = Path(tmp) / 'o.json'
            with contextlib.redirect_stderr(io.StringIO()):
                rc = desk.main([str(night.run), '--custody-root', str(night.root), '--night-commit', NIGHT,
                                '--packet-sha256', PACKET, '--json-out', str(out)])
            self.assertEqual(rc, 2)
            self.assertFalse(out.exists())


class AbaTests(unittest.TestCase):
    def test_ok_and_failures(self):
        self.assertTrue(record_for(base_result())['aba']['ok'])
        for label, mutate in {'adopt': lambda r: r['high_power'].update(verdict='adopt'),
                              'inconclusive': lambda r: r['high_power'].update(verdict='inconclusive'),
                              'powermode 2': lambda r: r.update(ac_powermode=2)}.items():
            result = base_result()
            mutate(result)
            with self.subTest(label):
                self.assertFalse(record_for(result)['aba']['ok'])


class OtherBlockTests(unittest.TestCase):
    def test_non_planning_g0_and_flags(self):
        result = base_result()
        result['g0_waits'].append({'segment': 'step_30b', 'g0_outcome': 'timeout'})
        result['g0_waits'].append({'segment': 'planning_turn_R_plus_2C', 'g0_outcome': 'timeout'})
        rec = record_for(result)
        self.assertEqual([r['segment'] for r in rec['non_planning_g0_not_released']], ['step_30b'])
        self.assertTrue(all(v for v in rec['flags']['inadmissible_slots'].values()))
        self.assertIn('planning_turn_R_plus_4C', rec['flags']['inconclusive_segments'])

    def test_implied_energy_band(self):
        self.assertEqual(record_for(base_result())['implied_energy_band'], desk.NOT_ESTIMABLE)
        result = base_result()
        result['planning_temperature'] = {'beta_T_j_per_c': -2.0, 'abs_beta_T_90_j_per_c': 5.0, 'delta_slow_c': 1.0}
        band = record_for(result)['implied_energy_band']
        self.assertEqual((band['point_j'], band['bound90_j']), (2.0, 5.0))

    def test_deterministic_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            night = Night(tmp, base_result())
            self.assertEqual(json.dumps(night.build(), sort_keys=True), json.dumps(night.build(), sort_keys=True))
            out = Path(tmp) / 'record.json'
            with contextlib.redirect_stdout(io.StringIO()) as text:
                rc = desk.main([str(night.run), '--custody-root', str(night.root), '--night-commit', NIGHT,
                                '--packet-sha256', PACKET, '--json-out', str(out)])
            self.assertEqual(rc, 0)
            rec = json.loads(out.read_text())
            self.assertIn('identity ok=True', text.getvalue())
            self.assertIn('RUN_DIR/r1_result.json', [i['path'] for i in rec['inputs']])
            self.assertIn('CUSTODY/result.json', [i['path'] for i in rec['inputs']])
            self.assertEqual(rec['s6']['G1_median_s'], 80.0)


@unittest.skipUnless(os.environ.get('JW_SLOT_DESK_NIGHT_1112') and os.environ.get('JW_SLOT_DESK_CUSTODY_1112'),
                     'opt-in 11-12 regression (step 0): set JW_SLOT_DESK_NIGHT_1112 and JW_SLOT_DESK_CUSTODY_1112')
class Regression1112(unittest.TestCase):
    """Spec 2.3 item 7 on the 11-12 copy (executed 99622e96c)."""

    @classmethod
    def setUpClass(cls):
        run = Path(os.environ['JW_SLOT_DESK_NIGHT_1112'])
        result = json.loads((run / 'r1_result.json').read_text())
        cls.commit = result.get('executed_commit')
        packet = (result.get('prepare_packet') or {}).get('sha256')
        cls.rec = desk.build(run, Path(os.environ['JW_SLOT_DESK_CUSTODY_1112']), cls.commit, packet)

    def test_identity_and_bars(self):
        rec = self.rec
        self.assertEqual(rec['identity']['status'], 'complete')
        self.assertTrue(self.commit.startswith('99622e96c'))
        self.assertTrue(rec['thermometry']['t4_fired'])
        self.assertIn('Th0C', json.dumps(rec['thermometry']['night_confirmation']))
        self.assertEqual(rec['duty']['verdict'], 'fail')
        self.assertEqual(rec['duty']['recompute_mismatch'], [])
        self.assertEqual(rec['aba']['verdict'], 'not_adopted')
        t = rec['aba']['t_decline_s']
        self.assertEqual([round(t[k], 3) for k in ('A1', 'B', 'A2')], [98.665, 98.845, 98.856])

    def test_flags_n_reaps_ticker(self):
        rec = self.rec
        inc = rec['flags']['inconclusive_segments']
        self.assertEqual(sorted(inc), ['planning_turn_R_plus_2C', 'planning_turn_R_plus_4C', 'thermometry.D'])
        self.assertIn('r1.g0_timeout_run', inc['planning_turn_R_plus_2C'])
        self.assertIn('r1.g0_timeout_run', inc['planning_turn_R_plus_4C'])
        self.assertIn('r1.thermometry_failed', inc['thermometry.D'])
        self.assertEqual(rec['rl106_n']['N'], 2)
        self.assertEqual(rec['rl91']['capture_reaps'], [])
        self.assertEqual(rec['rl91']['capture_reaps_unreadable'], [])
        # RL-120 item 5: "one short gap in 2,413". Which journal the 2,413 counts is not stated; record both.
        load = rec['rl91']['ticker']['load_journal']
        members = load['members'].values()
        print('\n11-12 ticker load total', load['total'], 'thermal total',
              rec['rl91']['ticker']['thermal_journal']['total'])
        self.assertTrue(load['total']['short'] == 1 and (
            load['total']['ticks'] == 2413 or any(m['ticks'] == 2413 and m['short'] == 1 for m in members)),
            load)


if __name__ == '__main__':
    unittest.main()
