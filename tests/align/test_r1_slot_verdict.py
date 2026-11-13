"""B4 slot verdict (spec 2.4, section 3): one fixture per row that fires that row alone.

Synthetic desk outputs only; no host or study data.
"""
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts import align_r1_slot_verdict as v

FLAG = 'r1.g0_timeout_run'
GATED = ('D_bank_benign_s1_gated_held', 'D_spam_benign_s1_gated_held_a', 'D_spam_benign_s1_gated_held_b')
IDLE = ('member | idle_plist_MB | plist_mtime->warmup_start s | rich_idle_mtime->warmup_start s | '
        'idle_baseline stage s | idle_seconds | power_hz\n'
        'step_30b | 157.4 | 12.24 | 0.004 | 393.0 | 300.0 | 10.0\n'
        'X_G_contrast | 157.2 | 12.24 | 0.004 | 398.3 | 300.0 | 10.0\n')


def gate(member, kind='G0', outcome='released', attempt='final', **kw):
    base = v.base_name(member)
    return {'member': member, 'member_base': base, 'attempt': attempt, 'kind': kind, 'turn': 0 if kind == 'G0' else 1,
            'outcome': outcome, 'duration_s': 100.0, 'planning_turn': base in v.PLANNING_SEGMENTS,
            'gated_d': base in GATED, 'x_g': base == 'X_G_contrast', 't2_samples': 0, 'clause_last': 'slope_slow',
            **kw}


def clear():
    record = {'identity': {'ok': True, 'status': 'complete', 'chain_exit_code': 0},
              'thermometry': {'t4_fired': False, 't4_reasons': []},
              'duty': {'verdict': 'pass', 'runs': [{'run': r, 'verdict': 'pass'} for r in GATED]},
              'x_g': {'status': 'measured', 'x7': False},
              'flags': {'inconclusive_segments': {}, 'inadmissible_slots': {}, 'skipped_segments': {},
                        'g0_waits': []},
              'non_planning_g0_not_released': [], 'aba': {'ok': True},
              'rl91': {'ok': True, 'ticker': {'over_1pct_members': []}},
              'rl106_n': {'n_flag': 0, 'n_gate': None, 'N': 0},
              'implied_energy_band': 'not estimable on this session: planning temperature inconclusive (RL-20)',
              's6': {'G1_median_s': 60.0},
              'tool_checks': {'duty_recompute_mismatch': [], 'capture_reaps_unreadable': []}}
    gates = [gate(m) for m in ('step_30b', 'step_D_prefill_10k_decode_4096', 'planning_turn_R_plus_4C',
                               'X_G_contrast') + GATED]
    gates += [gate(m, 'G1') for m in GATED + ('X_G_contrast',)]
    gates += [gate('cooldown_after_D', attempt='auxiliary')]
    gate_desk = {'schema': 'joulewise.align_r1_slot_gate_desk.v1', 'validation': {'rows': [], 'all_agree': True},
                 'gates': gates, 's6': {'g1_median_s': 60.0, 's6_reachable_step_c': None},
                 'triggers': {'T1': {'fired': False, 'reasons': []}, 'T1p': {'fired': False, 'reasons': []},
                              'T2': {'fired': False, 'gates': []},
                              'T3': {'fired': False, 'u2_tv0h_c': 0.3}},
                 'tool_checks': {'slope_recompute_mismatch': [], 's6_median_agrees': True,
                                 'tf08_excess_agrees': True, 'member_journals_without_both_keys': [],
                                 'auxiliary_policy_defaulted': []}}
    three_a = {'rule': {'precool_fast': {'option': 'rl131', 'authority': 'RL-131 item 2.4'}},
               'reconciliation': {'mismatches': []},
               'g0_intervals': [{'phase': p, 'planning_turn': True, 'superseded': False, 'outcome': 'released',
                                 'classification': 'released', 'reasons': []} for p in v.PLANNING_SEGMENTS]}
    return {'record': record, 'gate': gate_desk, '3a': three_a, 'kit': {'members': []}, 'kit_rc': '0',
            'kit_stderr': '', 'idle': IDLE}


def run(fx, *, decide=None, proofs=None, drop=()):
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        files = {'record': ('record.json', json.dumps(fx['record'])), 'gate': ('gate_desk.json', json.dumps(fx['gate'])),
                 '3a': ('3a.json', json.dumps(fx['3a'])), 'kit': ('kit_desk.json', json.dumps(fx['kit'])),
                 'kit_rc': ('kit_desk.rc', fx['kit_rc']), 'kit_stderr': ('kit_desk.stderr.txt', fx['kit_stderr']),
                 'idle': ('idle_parse_gap.txt', fx['idle'])}
        for key, (name, text) in files.items():
            if key not in drop:
                (t / name).write_text(text)
        argv = ['--record', str(t / 'record.json'), '--gate-desk', str(t / 'gate_desk.json'), '--3a', str(t / '3a.json'),
                '--kit-desk', str(t / 'kit_desk.json'), '--kit-desk-rc', str(t / 'kit_desk.rc'),
                '--kit-desk-stderr', str(t / 'kit_desk.stderr.txt'), '--idle-parse-gap', str(t / 'idle_parse_gap.txt'),
                '--json-out', str(t / 'verdict.json')]
        if decide is not None:
            (t / 'decide.json').write_text(json.dumps(decide))
            argv += ['--decide', str(t / 'decide.json')]
        if proofs is not None:
            (t / 'proofs.json').write_text(json.dumps(proofs))
            argv += ['--proofs', str(t / 'proofs.json')]
        with contextlib.redirect_stdout(io.StringIO()):
            assert v.main(argv) == 0
        return json.loads((t / 'verdict.json').read_text())


def by_row(out):
    return {r['row']: r for r in out['rows']}


class VerdictTests(unittest.TestCase):
    def assert_alone(self, mutate, row, route, **kw):
        fx = clear()
        mutate(fx)
        out = run(fx, **kw)
        self.assertEqual(out['fired_rows'], [row], json.dumps(by_row(out).get('X2'), indent=1))
        self.assertEqual(out['route'], route)
        return out

    def test_all_clear(self):
        out = run(clear())
        self.assertEqual((out['route'], out['fired_rows']), ('SLOTS-AND-SIGNING', []))
        rows = by_row(out)
        self.assertTrue(rows['P1']['status'].startswith('applies'))
        self.assertTrue(rows['S6a']['status'].startswith('applies'))
        self.assertIn('median G1 wait 60.0 s; S6 rule not engaged', rows['S6a']['status'])
        self.assertEqual(rows['B1x']['status'], 'not evaluated (step 8)')
        self.assertIsNone(rows['S1']['fired'])
        self.assertEqual(out['rl106_n']['n_gate'], 0)

    def test_x1(self):
        self.assert_alone(lambda f: f['record']['identity'].update(ok=False, status='refused'), 'X1', v.TRL)
        out = self.assert_alone(lambda f: f['record']['identity'].update(ok=False), 'X1', v.TOOL)
        self.assertIn('copy error', by_row(out)['X1']['evidence']['note'])

    def test_x2_each_cause(self):
        causes = {
            'validation': lambda f: f['gate']['validation'].update(all_agree=False),
            'slope': lambda f: f['gate']['tool_checks'].update(slope_recompute_mismatch=[{'member': 'x'}]),
            's6 agrees': lambda f: f['gate']['tool_checks'].update(s6_median_agrees=False),
            'tf08': lambda f: f['gate']['tool_checks'].update(tf08_excess_agrees=False),
            'tf08 unchecked with kit rc 0': lambda f: f['gate']['tool_checks'].update(tf08_excess_agrees=None),
            '3a rc 2': lambda f: f['3a']['reconciliation'].update(mismatches=['x']),
            '3a without rl131': lambda f: f['3a'].update(rule={}),
            'n_flag != n_gate': lambda f: f['record']['rl106_n'].update(n_flag=1),
            'duty recompute': lambda f: f['record']['tool_checks'].update(duty_recompute_mismatch=['overall']),
            'reaps unreadable': lambda f: f['record']['tool_checks'].update(capture_reaps_unreadable=['a/runs/r']),
            'kit rc other': lambda f: f.update(kit_rc='1', kit_stderr='Traceback: KeyError'),
            'idle unparseable': lambda f: f.update(idle='garbage\n'),
            'T1 None': lambda f: f['gate']['triggers']['T1'].update(fired=None),
            'T3 None': lambda f: f['gate']['triggers']['T3'].update(fired=None),
        }
        for label, mutate in causes.items():
            with self.subTest(label):
                fx = clear()
                mutate(fx)
                out = run(fx)
                self.assertIn('X2', out['fired_rows'])
                self.assertEqual(out['route'], v.TOOL, out['fired_rows'])
                if label not in ('T1 None', 'T3 None'):
                    self.assertEqual(out['fired_rows'], ['X2'])

    def test_d1_both_arms(self):
        self.assert_alone(lambda f: f['record']['thermometry'].update(t4_fired=True), 'D1', v.TRL)
        out = self.assert_alone(lambda f: f.update(kit_rc='rc=1', kit_stderr='Refused("RL-78: picked sensors")'),
                                'D1', v.TRL)
        self.assertTrue(by_row(out)['D1']['evidence']['kit_desk_refused_rl78'])

    def test_duty_rows(self):
        self.assert_alone(lambda f: f['record']['duty'].update(verdict='fail'), 'D2', v.TRL)
        self.assert_alone(lambda f: f['record']['duty'].update(verdict='inconclusive'), 'D2i', v.TRL)

    def test_g1h(self):
        def mutate(f):
            next(g for g in f['gate']['gates'] if g['kind'] == 'G1' and g['x_g']).update(outcome='timeout')
        self.assert_alone(mutate, 'G1H', v.TRL)

        def deadman(f):
            next(g for g in f['gate']['gates'] if g['kind'] == 'G1' and g['gated_d']).update(outcome='deadman')
        self.assert_alone(deadman, 'G1H', v.TRL)

    def test_xg(self):
        self.assert_alone(lambda f: f['record']['x_g'].update(status='inconclusive'), 'XG', v.TRL)
        self.assert_alone(lambda f: f['record']['x_g'].update(x7=True), 'XG', v.TRL)

    def test_p2(self):
        def mutate(f):
            f['3a']['g0_intervals'][0].update(outcome='timeout', classification='to-research-lead',
                                              reasons=['RL-131 2.4'])
        self.assert_alone(mutate, 'P2', v.TRL)

    def test_p3_is_not_fired_and_its_flags_are_released(self):
        def mutate(f):
            name = 'planning_turn_R_plus_4C'
            row = next(r for r in f['3a']['g0_intervals'] if r['phase'] == name)
            row.update(outcome='timeout', classification='planning-release-3a')
            f['record']['flags']['inconclusive_segments'] = {name: FLAG}
            f['record']['flags']['inadmissible_slots'] = {'planning_temperature': [FLAG],
                                                          'U5': [FLAG, 'r1.u5_inconclusive']}
            f['record']['rl106_n'].update(n_flag=1)
            next(g for g in f['gate']['gates'] if g['member'] == name).update(outcome='timeout', t2_samples=3)
            f['gate']['triggers']['T2'] = {'fired': True, 'gates': [
                {'member': name, 'member_base': name, 'attempt': 'final', 'kind': 'G0', 'turn': 0,
                 'outcome': 'timeout', 't2_samples': 3, 'duty_verdict': None, 'planning_turn': True}]}
        fx = clear()
        mutate(fx)
        out = run(fx)
        self.assertEqual((out['route'], out['fired_rows']), ('SLOTS-AND-SIGNING', []), out['fired_rows'])
        rows = by_row(out)
        self.assertTrue(rows['P3']['status'].startswith('applies'))
        self.assertEqual(len(rows['T2']['evidence']['excluded_3a']), 1)
        self.assertEqual(out['rl106_n']['n_gate'], 1)
        # The same flags without P3 (the planning row classed to the research lead) fire F1 and P2.
        fx['3a']['g0_intervals'][2].update(classification='to-research-lead')
        out = run(fx)
        self.assertIn('F1', out['fired_rows'])
        self.assertIn('P2', out['fired_rows'])
        self.assertIn('T2', out['fired_rows'])

    def test_planning_inconclusive_for_another_reason_is_p2(self):
        def mutate(f):
            f['record']['flags']['inconclusive_segments'] = {'planning_turn_R_plus_0C': 'r1.preheat_cap_reached'}
        out = run((lambda fx: (mutate(fx), fx)[1])(clear()))
        self.assertIn('P2', out['fired_rows'])

    def test_g0x(self):
        self.assert_alone(lambda f: f['record'].update(non_planning_g0_not_released=[{'segment': 'step_30b'}]),
                          'G0x', v.TRL)
        self.assert_alone(lambda f: f['gate']['gates'][-1].update(outcome='timeout'), 'G0x', v.TRL)

    def test_a1(self):
        self.assert_alone(lambda f: f['record']['aba'].update(ok=False), 'A1', v.TRL)

    def test_triggers(self):
        self.assert_alone(lambda f: f['gate']['triggers']['T1'].update(fired=True), 'T1', v.TRL)
        self.assert_alone(lambda f: f['gate']['triggers']['T3'].update(fired=True), 'T3', v.TRL)
        cand = {'member': 'D_bank_benign_s1_gated_held', 'member_base': 'D_bank_benign_s1_gated_held',
                'attempt': 'final', 'kind': 'G1', 'turn': 1, 'outcome': 'released', 't2_samples': 2,
                'duty_verdict': 'fail', 'planning_turn': False}
        self.assert_alone(lambda f: f['gate']['triggers'].update(T2={'fired': True, 'gates': [cand]}), 'T2', v.TRL)

    def test_f1(self):
        self.assert_alone(lambda f: f['record']['flags'].update(
            inconclusive_segments={'thermometry.D': 'r1.thermometry_failed'}), 'F1', v.TRL)
        self.assert_alone(lambda f: f['record']['flags'].update(
            inadmissible_slots={'S6': ['r1.gated_timeout_or_hold_suppression']}), 'F1', v.TRL)

    def test_c1(self):
        out = self.assert_alone(lambda f: f.update(idle=IDLE + 'D_bank | 157.2 | 30.00 | 0.004 | 397.8 | 300.0 | 10.0\n'),
                                'C1', v.HOLD)                      # RL-138 item 7 (review fix 6)
        self.assertEqual(by_row(out)['C1']['evidence']['max_span_s'], 30.0)

    def test_r1(self):
        self.assert_alone(lambda f: f['record']['rl91'].update(ok=False), 'R1', v.TRL)

    def test_s6(self):
        out = self.assert_alone(lambda f: f['gate']['s6'].update(g1_median_s=120.0, s6_reachable_step_c=1.5),
                                'S6c', v.HOLD)
        fx = clear()
        fx['gate']['s6'].update(g1_median_s=300.03, s6_reachable_step_c=None)
        out = run(fx)
        self.assertEqual(out['route'], v.GO)
        self.assertIn('not reachable by δ_slow', by_row(out)['S6b']['status'])
        self.assertIn('implied energy band', by_row(out)['S6b']['status'])
        self.assertEqual(by_row(out)['S6b']['evidence']['implied_energy_band'][:14], 'not estimable ')

    def test_b1x_and_s1(self):
        self.assert_alone(lambda f: None, 'B1x', v.TRL, decide={'step': 'R1-RERUN'})
        out = run(clear(), decide={'step': 'R10-2(a)'})
        self.assertIs(by_row(out)['B1x']['fired'], False)
        ten = [{'path': f'p{i}', 'sha256': 'a' * 64, 'equals_night': True} for i in range(10)]
        ok = {'head': 'h', 'proofs': [{'id': '1', 'ok': True}], 'ten_paths': ten}
        self.assertIs(by_row(run(clear(), proofs=ok))['S1']['fired'], False)
        bad = deepcopy(ok)
        bad['ten_paths'][3]['equals_night'] = False
        self.assert_alone(lambda f: None, 'S1', v.HOLD, proofs=bad)

    def test_two_rows_together(self):
        def mutate(f):
            f['record']['duty'].update(verdict='fail')
            f['gate']['triggers']['T3'].update(fired=True)
        fx = clear()
        mutate(fx)
        out = run(fx)
        self.assertEqual(out['fired_rows'], ['D2', 'T3'])
        self.assertEqual(out['route'], v.TRL)
        self.assertEqual(sorted(out['packets']), ['D2', 'T3'])

    def test_missing_input_is_a_tool_defect_never_a_pass(self):
        for drop in ('record', 'gate', '3a', 'kit_rc', 'idle'):
            with self.subTest(drop):
                out = run(clear(), drop=(drop,))
                self.assertIn('X2', out['fired_rows'])
                self.assertEqual(out['route'], v.TOOL)
        out = run(clear(), drop=('kit',))            # rc 0 but no kit desk JSON
        self.assertEqual(out['route'], v.TOOL)

    def test_research_lead_dominates_and_notes_open_tool_defect(self):
        fx = clear()
        fx['record']['aba'].update(ok=False)
        fx['gate']['validation'].update(all_agree=False)
        out = run(fx)
        self.assertEqual(out['route'], v.TRL)
        self.assertIsNotNone(out['note'])


class ReviewFixTests(unittest.TestCase):
    """Closing tests of the cold review (fable-rev-slot-desk.md) for B4, and RL-138 items 1, 4, 7, 8, 9."""
    assert_alone = VerdictTests.assert_alone

    def test_fix5_x1_any_status_but_complete_is_the_research_leads(self):
        for status, code in (('running', 0), ('refused', 0), ('aborted', 0), ('complete', 3)):
            with self.subTest(status=status, code=code):
                fx = clear()
                fx['record']['identity'].update(ok=False, status=status, chain_exit_code=code)
                out = run(fx)
                self.assertEqual(out['fired_rows'], ['X1'])
                self.assertEqual(out['route'], v.TRL)
        fx = clear()
        fx['record']['identity'].update(ok=False)                   # complete, exit 0, a hash mismatch
        self.assertEqual(run(fx)['route'], v.TOOL)

    def test_fix6_c1_alone_holds_signing(self):
        fx = clear()
        fx['idle'] = IDLE + 'D_bank | 157.2 | 31.00 | 0.004 | 397.8 | 300.0 | 10.0\n'
        out = run(fx)
        self.assertEqual((out['fired_rows'], out['route']), (['C1'], v.HOLD))
        self.assertEqual(out['packets'], {})

    def test_fix3_t1p_row(self):
        out = self.assert_alone(lambda f: f['gate']['triggers']['T1p'].update(fired=True), 'T1p', v.HOLD)
        self.assertIn('3a.txt', by_row(out)['T1p']['packet'])
        fx = clear()
        fx['gate']['triggers']['T1p'].update(fired=None)            # stratum not computable
        out = run(fx)
        self.assertEqual(out['route'], v.TOOL)
        self.assertTrue(any('T1p' in r for r in by_row(out)['X2']['evidence']['reasons']))

    def test_item4_member_journal_without_both_keys_is_x2(self):
        fx = clear()
        fx['gate']['tool_checks']['member_journals_without_both_keys'] = ['step_30b']
        self.assertEqual(run(fx)['route'], v.TOOL)

    def test_item1_defaulted_auxiliary_band_is_x2(self):
        fx = clear()
        fx['gate']['tool_checks']['auxiliary_policy_defaulted'] = ['idle_soak.g0_release1/g0']
        out = run(fx)
        self.assertEqual((out['fired_rows'], out['route']), (['X2'], v.TOOL))

    def test_item9_ticker_print_owed_holds_signing(self):
        fx = clear()
        fx['record']['rl91']['ticker']['over_1pct_members'] = ['D_bank_benign_s1_gated_held']
        out = run(fx)
        self.assertEqual((out['fired_rows'], out['route']), (['R1p'], v.HOLD))

    def test_item7_send_now_and_citable(self):
        fx = clear()
        fx['record']['aba'].update(ok=False)                        # A1: record-only, may be sent at once
        fx['gate']['triggers']['T3'].update(fired=True)             # T3: read from the gate desk
        fx['gate']['validation'].update(all_agree=False)            # X2 beside them
        out = run(fx)
        self.assertEqual(out['route'], v.TRL)
        self.assertEqual(out['send_now'], ['A1'])
        self.assertEqual(out['hold_until_x2_fixed'], ['T3'])
        out = run(clear())
        self.assertEqual(out['route'], v.GO)
        self.assertFalse(out['citable_for_signing'])
        self.assertIn('NOT CITABLE FOR SIGNING', v.render(out))
        ten = [{'path': f'p{i}', 'sha256': 'a' * 64, 'equals_night': True} for i in range(10)]
        out = run(clear(), decide={'step': 'CURRENT-RULE'}, proofs={'head': 'h', 'proofs': [{'id': '1', 'ok': True}],
                                                                    'ten_paths': ten})
        self.assertEqual(out['route'], v.GO)
        self.assertTrue(out['citable_for_signing'])


if __name__ == '__main__':
    unittest.main()
