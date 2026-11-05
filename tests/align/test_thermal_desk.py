"""U1–U6 and the deciding rule, derived entirely from synthetic records."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import thermal_desk as desk
from tests.align.test_attribution import episode, turn, NS
from tests.align.test_attribution_holds import gate
from tests.align.test_thermal_gate import policy


def member(name='one', energy=1000, slow=40.):
    return {'id': name, 'model': 'synthetic', 'pair': 'spam', 'condition': 'benign', 'gated': True,
            'start_ns': 0, 'flags': [], 'coverage': [{'sample_fraction': 1., 'gaps_ns': []}],
            'registered_os_observed': True,
            'turn_observation': [{'os_nominal': True, 'pm_nominal': True, 'pm_max_gap_s': 0}],
            'pm_period_s': .1, 'turn_admissions': 1, 'intervals': [],
            'releases': [{'journal_verified': True}], 'g0_slow_c': slow,
            'tokens': [[1, 2, 3]], 'turn_owned_j': energy, 'decode_clocks_mhz': [1000.], 'decode_clock_mhz': 1000.}


def contrast(effect=12, noise=0):
    slots = [('X', 'G', 6), ('Y', 'S', 8), ('X', 'S', 10), ('Y', 'G', 11),
             ('Y', 'G', 13), ('X', 'S', 14), ('Y', 'S', 16), ('X', 'G', 18)]
    runs = []
    for i, (t, arm, position) in enumerate(slots):
        r = member(str(i), 1000 + (100 if t == 'Y' else 0) + (effect if arm == 'S' else 0) + position*.3 + (-1)**i*noise)
        r.update(template=t, arm=arm, start_ns=position*3600*NS, pilot7_token_identical=True)
        runs.append(r)
    return runs


class DeskTests(unittest.TestCase):
    def test_student_t90_critical_values_are_not_normal_intervals(self):
        for df, expected in ((1, 6.3137515148), (2, 2.9199855804), (4, 2.1318467863), (30, 1.6972608866)):
            self.assertAlmostEqual(desk.t90(df), expected, places=8)

    def test_contrast_all_three_branches_and_four_df(self):
        result = desk.deciding_experiment(contrast())
        self.assertEqual(result['verdict'], 'T CONFIRMED')
        self.assertAlmostEqual(result['arm_effect_j'], 12)
        self.assertEqual(result['df'], 4)
        for value in result['d_template_j'].values():
            self.assertAlmostEqual(value, 12.)
        self.assertEqual(desk.deciding_experiment(contrast(0))['verdict'], 'T REJECTED')
        self.assertEqual(desk.deciding_experiment(contrast(8))['verdict'], 'INCONCLUSIVE')
        self.assertEqual(desk.deciding_experiment(contrast()[:-1])['verdict'], 'INCONCLUSIVE')
        runs = contrast()
        runs[0]['pilot7_token_identical'] = False
        self.assertEqual(desk.deciding_experiment(runs)['verdict'], 'INCONCLUSIVE')

    def test_u1_exact_boundaries_and_mutations(self):
        m = member()
        result = desk.acceptance([m], pairs=[(m, m)])
        self.assertEqual([result[k]['status'] for k in ('U1', 'U2', 'U3')], ['pass']*3)
        cases = [('coverage', [{'sample_fraction': .989, 'gaps_ns': []}]),
                 ('coverage', [{'sample_fraction': .99, 'gaps_ns': [[0, 2*NS+1]]}]),
                 ('turn_observation', [{'os_nominal': False, 'pm_nominal': True, 'pm_max_gap_s': 0}]),
                 ('turn_observation', [{'os_nominal': True, 'pm_nominal': False, 'pm_max_gap_s': 0}]),
                 ('turn_observation', [{'os_nominal': True, 'pm_nominal': True, 'pm_max_gap_s': 1.001}])]
        for key, value in cases:
            changed = deepcopy(m)
            changed[key] = value
            with self.subTest(key=key):
                self.assertEqual(desk.acceptance([changed])['U1']['status'], 'fail')
        m['coverage'] = [{'sample_fraction': .99, 'gaps_ns': [[0, 2*NS]]}]
        self.assertEqual(desk.acceptance([m])['U1']['status'], 'pass')
        m['intervals'] = [{'kind': 'H', 'outcome': 'timeout'}]
        m['turn_admissions'] = 50
        self.assertEqual(desk.acceptance([m])['U1']['status'], 'pass')
        m['turn_admissions'] = 49
        self.assertEqual(desk.acceptance([m])['U1']['status'], 'fail')

    def test_unobserved_is_not_pass_and_exclusions_count_members_once(self):
        m = member()
        m['flags'] = ['thermal.state_unobserved', 'thermal.start_gate_timeout']
        result = desk.acceptance([m])
        self.assertEqual(result['U1']['status'], 'inconclusive')
        self.assertEqual(result['U1']['thermal_excluded_members'], 1)
        self.assertEqual(result['U2']['status'], 'inconclusive')
        self.assertEqual(desk.acceptance([m, deepcopy(m)])['U1']['status'], 'fail')

    def test_u2_range_and_u3_energy_clock_token_bars(self):
        a, b = member(), member('two', slow=43)
        self.assertEqual(desk.acceptance([a, b])['U2']['status'], 'pass')
        b['g0_slow_c'] = 43.001
        self.assertEqual(desk.acceptance([a, b])['U2']['status'], 'fail')
        b = member('two', energy=1008.91)
        self.assertEqual(desk.identical_pair(a, b)['status'], 'pass')
        b['turn_owned_j'] = 1009
        self.assertEqual(desk.identical_pair(a, b)['status'], 'fail')
        b = member('two')
        b['decode_clocks_mhz'] = [1006.]
        b['decode_clock_mhz'] = 1006.
        self.assertEqual(desk.identical_pair(a, b)['status'], 'fail')
        b['tokens'] = [[1, 2, 4]]
        self.assertEqual(desk.identical_pair(a, b)['exclusion'], 'X5')

    def test_u4_windows_are_clusters_and_inconclusive_is_distinct(self):
        result = desk.cross_window({'a': [1000, 1000], 'b': [1001], 'c': [999]}, 1000)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['df'], 2)
        self.assertEqual(desk.cross_window({'a': [1000], 'b': [1000]}, 1000)['status'], 'inconclusive')
        self.assertEqual(desk.cross_window({'a': [960], 'b': [1000], 'c': [1040]}, 1000)['status'], 'inconclusive')
        self.assertEqual(desk.cross_window({'a': [1003], 'b': [1003], 'c': [1003]}, 1000)['status'], 'fail')
        def anchors(offsets):
            return {str(i): {str(j): 1000+j*100+v for j in range(4)} for i, v in enumerate(offsets)}
        self.assertEqual(desk.cross_window({}, None, anchor_sessions=anchors([-6, 0, 6]))['status'], 'pass')
        self.assertEqual(desk.cross_window({}, None, anchor_sessions=anchors([-7, 0, 7]))['status'], 'fail')

    def test_u5_light_bound_scaling_and_heavy_pairs_only(self):
        light = desk.state_sensitivity(heavy=False, smaller_pair_sr_j=400, mean_energy_j=2000,
                                      mean_30b_energy_j=1000, contrast=desk.deciding_experiment(contrast(12)))
        self.assertEqual(light['status'], 'pass')
        self.assertAlmostEqual(light['point_shift_j'], 24)
        pairs = [(member('a', 1000, 40), member('b', 1002, 41)),
                 (member('c', 1000, 40), member('d', 1004, 42)),
                 (member('e', 1000, 40), member('f', 1006, 43))]
        heavy = desk.state_sensitivity(heavy=True, smaller_pair_sr_j=100, mean_energy_j=1000,
                                      pairs=pairs, release_range_c=3)
        self.assertEqual(heavy['status'], 'pass')
        self.assertAlmostEqual(heavy['beta_j_per_c'], 2)
        self.assertAlmostEqual(heavy['upper90_shift_j'], 6)
        for a, b in pairs:
            b['tokens'] = None
        self.assertEqual(desk.state_sensitivity(heavy=True, smaller_pair_sr_j=100, mean_energy_j=1000,
                                               pairs=pairs, release_range_c=3)['status'], 'inconclusive')

    def test_u6_margins_and_diagnostics_do_not_decide(self):
        benign = [{'pair': p, 'start_ns': i, 'residual_j': [0., 0., 0.],
                   'release_slow_c': i, 'mean_clock_mhz': i} for p in ('spam', 'bank') for i in range(6)]
        kw = {'mean_turn_j': 100, 'mean_30b_turn_j': 100, 'mean_episode_j': 3000,
              'split_rule': 'within_pair_episode_order'}
        self.assertEqual(desk.monitoring_stability(benign, **kw)['status'], 'pass')
        self.assertEqual(desk.monitoring_stability(benign[:-1], **kw)['status'], 'inconclusive')
        for r in benign:
            r['residual_j'] = [0, 2, 4]
        self.assertEqual(desk.monitoring_stability(benign, **kw)['status'], 'fail')
        for r in benign:
            r['residual_j'] = [100 if r['start_ns'] >= 3 else 0]*3
        self.assertEqual(desk.monitoring_stability(benign, **kw)['status'], 'fail')

    def test_journal_release_verification_and_energy_are_recomputed(self):
        p = policy()
        intervals = [gate('G0', -10*NS, 0), gate('H', 4*NS, 6*NS)]
        intervals[0]['exit_sample_ns'] = 0
        intervals[1]['exit_sample_ns'] = 6*NS
        ep = episode(turns=(turn(),), hardware={'thermal': {'policy': p, 'intervals': intervals}})
        journal = [{'kind': 'sample', 'monotonic_ns': i*NS, 'finished': {'monotonic_after_ns': i*NS},
                    'sensors': {'Tfak': 40., 'Tslw': 40.}, 'errors': {}} for i in range(-10, 11)]
        pm = [{'start_ns': i*NS, 'end_ns': (i+1)*NS, 'state': 'Nominal', 'active_ns': NS, 'clock_mhz': 1000}
              for i in range(-10, 10)]
        def read():
            return desk.member_record(ep, journal, os_readings=[(i*NS, 0) for i in range(11)],
                                      registered_os_readings=[(i*NS, 0) for i in range(11)],
                                      pm_samples=pm, pm_period_s=1, source='mock', channel='package',
                                      turn_rows=[{'generation': {'output_token_ids': [1, 2, 3]}}])
        record = read()
        self.assertEqual(record['gross_episode_j'], 1000)
        self.assertEqual(record['turn_owned_j'], 600)
        self.assertEqual(record['exclusion_intervals'][1]['entry_stamp']['epoch_ns'], 127*NS)
        self.assertTrue(all(r['journal_verified'] for r in record['releases']))
        self.assertEqual(desk.acceptance([record])['U1']['status'], 'pass')
        journal[16]['sensors']['Tslw'] = 42
        self.assertEqual(desk.acceptance([read()])['U2']['status'], 'fail')
        # A claimed previous-release reference cannot legitimize ratcheting.
        journal[16]['sensors']['Tslw'] = 40
        intervals[1]['reference'] = {'fast_c': 41., 'slow_c': 41.}
        self.assertEqual(desk.acceptance([read()])['U2']['status'], 'fail')

    def test_missing_registered_span_and_unfrozen_u6_are_inconclusive(self):
        m = member()
        del m['registered_os_observed']
        self.assertEqual(desk.acceptance([m])['U1']['status'], 'inconclusive')
        self.assertEqual(desk.monitoring_stability([], mean_turn_j=100, mean_30b_turn_j=100,
                                                   mean_episode_j=1000)['status'], 'inconclusive')

    def test_w1_report_cannot_claim_u4_u6_control_and_prints_exact_rule(self):
        runs = contrast(12)
        for i, run in enumerate(runs):
            run['window'] = 'W1'
            run['identical_work_group'] = run['template']+run['arm']
            run['per_turn'] = [{'owned_j': run['turn_owned_j'], 'decode_clock_mhz': 1000, 'slow_c': 40}]
        report = desk.window_report(runs, cross_windows={'synthetic': {'status': 'pass'}},
                                    sensitivity={'synthetic': {'status': 'pass'}}, monitoring={'synthetic': {'status': 'pass'}})
        for k in (4, 5, 6):
            self.assertEqual(report['model_windows']['synthetic/W1'][f'U{k}']['status'], 'inconclusive')
        text = desk.markdown_report(report)
        self.assertIn('T CONFIRMED', text)
        self.assertIn('same sign', text)
        self.assertIn('df=4', text)
        self.assertIn('Δdecode MHz', text)

    def test_cli_reads_synthetic_bundle_and_writes_reviewable_tables(self):
        from tests.align.test_thermal_gate import NativeIntegrationTests
        from scripts.align_v4_thermal_desk import main
        helper = NativeIntegrationTests('test_real_workload_endpoint_budget_and_held_stream_keep_exact_tokens')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle, status, _ = helper.held_run(root/'fake-member')
            self.assertEqual(status.status.value, 'succeeded')
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps({'members': [{'bundle': str(bundle), 'window': 'W1',
                                                        'turn_owned_j': 123456}]}))
            output = root/'desk'
            self.assertEqual(main(['--manifest', str(manifest), '--output', str(output)]), 0)
            report = json.loads((output/'PILOT.json').read_text())
            self.assertNotEqual(report['members'][0]['turn_owned_j'], 123456)
            # This mock runtime has no GPU meter/PM evidence. Never call it live.
            self.assertIn('trace.missing', report['members'][0]['energy_flags'])
            self.assertNotEqual(next(iter(report['model_windows'].values()))['U1']['status'], 'pass')
            self.assertIn('Exact exclusion intervals', (output/'THERMAL.md').read_text())


if __name__ == '__main__':
    unittest.main()
