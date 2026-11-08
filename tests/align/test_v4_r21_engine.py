"""R21 witnesses: synthetic evidence only, independent of recompute code."""
import copy
import math
import unittest

from joulewise.align.v4_analysis import analyze
from joulewise.align.v4_analysis import acceptance as ac
from joulewise.align.v4_analysis import engine as e
from joulewise.align.v4_analysis.synthetic import series
from joulewise.align.apple import v4_estimands as est


class R21Tests(unittest.TestCase):
    def test_owned_total_zero_width_and_unreachable_grid(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        fill, _ = analyze(p)
        score = fill['fits'][0]['scores'][0]
        member = next(m for m in p['windows'][0]['members'] if m['slot']['run_id'] == score['run_id'])
        self.assertEqual(score['measured_j'], math.fsum(r['energy_j'] for r in e._rows(member)))
        self.assertEqual(score['denominator_j'], score['prediction_sd_j'])
        self.assertNotIn('bound_read_as_sd', score['flags'])
        self.assertEqual(score['diagnostic_bounds']['gross_episode_half_width_j'], 2.)
        last = next(r for r in score['H_grid'] if r['nominal_H'] == 2048)
        self.assertEqual((last['H'], last['score'], last['status']), (None, None, 'dose_unreachable'))

    def test_owned_sum_mismatch_refuses(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        p['windows'][0]['members'][5]['thermal']['turn_owned_j'] += 1
        with self.assertRaisesRegex(ValueError, 'turn-owned'):
            analyze(p)

    def test_attribution_bounds_and_gross_total_are_diagnostic_only(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        a, _ = analyze(p)
        for m in p['windows'][0]['members']:
            m['summary']['energy'] = {}
            m['thermal'].update(turn_owned_half_width_j=None, gross_episode_half_width_j=None)
            for key in ('True','False'):
                for row in m['summary']['residual_rows'][key]:
                    row['energy_half_width_j'] = None
        b, _ = analyze(p)
        self.assertEqual(a['thresholds'], b['thresholds'])
        self.assertEqual([r['score'] for f in a['fits'] for r in f['scores']],
                         [r['score'] for f in b['fits'] for r in f['scores']])

    def test_u1_gate_entries_include_h_and_x4_sidecar(self):
        from tests.align.test_thermal_desk import member
        from joulewise.align.apple import thermal_desk as td
        m = member(); m['captured'] = True; m['sidecar_present'] = True
        m['flags'] = ['thermal.state_unobserved']
        m['intervals'] = [dict(kind='H',outcome='released') for _ in range(49)]+[dict(kind='H',outcome='timeout')]
        r = td.acceptance([m],v4=True)
        self.assertEqual(r['U1']['turn_admissions'],50)
        self.assertEqual(r['U1']['g1_h_timeouts'],1)

    def test_u2_no_releases_not_applicable_and_timed_out_g0_not_a_value(self):
        from tests.align.test_thermal_desk import member
        from joulewise.align.apple import thermal_desk as td
        a,b = member('a'),member('b',slow=99.)
        a['intervals'] = [dict(kind='G0',outcome='released')]; a['releases'] = []
        b['intervals'] = [dict(kind='G0',outcome='timeout')]; b['releases'] = []
        r = td.acceptance([a,b],v4=True)['U2']
        self.assertEqual(r['parts'],dict(a='pass',b='not_applicable'))
        self.assertEqual(r['g0_slow_range_c'],0.)

    def test_predeclared_contrast_still_fits_all_eight(self):
        from tests.align.test_thermal_desk import contrast
        from joulewise.align.apple import thermal_desk as td
        runs = contrast()
        for i,r in enumerate(runs):
            r.update(stage='a' if i<4 else 'b',admission_slow_c=42. if r['arm']=='S' else 40.,
                     g1_waited_by_turn=[True])
        r = td.deciding_experiment(runs,v4=True,delta_slow_c=1.,predeclared='INCONCLUSIVE: declared non-veto')
        self.assertEqual(r['df'],3)
        self.assertIn('arm_effect_j',r)
        self.assertEqual(r['consequence'],'non_veto')

    def test_inconclusive_pool_battery_missing_and_no_c6_fence(self):
        p = series(turns=4)
        p['u3_evidence'].pop('r1_d_screen')
        p['windows'][0]['members'][5]['thermal']['battery'] = {}
        p['windows'][0]['status'] = 'provisional'
        fill, _ = analyze(p)
        self.assertEqual(fill['windows'][0]['checks'][e.D_MODEL]['U3']['status'], 'inconclusive')
        self.assertTrue(fill['windows'][0]['pool_entry'])
        m = fill['windows'][0]['eligibility'][5]
        self.assertTrue(m['eligible'])
        self.assertIn('battery.unobserved', m['flags'])
        self.assertEqual(fill['windows'][0]['battery']['status'], 'unavailable')
        self.assertEqual(fill['calibration']['decision'], 'pending_final_eligibility')
        self.assertFalse(any(f['window'].startswith('T') for f in fill['fits']))

    def test_recorded_and_rederived_exclusion_classes_union(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        m = p['windows'][0]['members'][5]
        m['source_flags'] = ['X5']
        m['thermal']['registered_os_nonzero'] = True
        fill, _ = analyze(p)
        r = fill['windows'][0]['eligibility'][5]
        self.assertEqual(r['classes'], ['X1', 'X5'])
        self.assertTrue(r['class_mismatch'])

    def test_fixed_u3_pairs_and_identity_digest(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        m = p['windows'][0]['members'][21]['thermal']
        m['identity_sha256'] = 'f'*64
        fill, _ = analyze(p)
        pair = fill['windows'][0]['checks'][e.D_MODEL]['U3']['pairs'][0]
        self.assertEqual(pair['ordinals'], [5, 22])
        self.assertEqual(pair['status'], 'excluded')
        self.assertIn('X5', fill['windows'][0]['eligibility'][21]['classes'])

    def test_heavy_tail_leave_one_out(self):
        p = series(turns=3)['u3_evidence']
        for i, row in enumerate(p['pilot_pairs']):
            row['energies_j'] = [1000., 1100. if i == 0 else 1000.01]
        d = ac.u3_derivation(p)
        self.assertTrue(d['heavy_tail_rule_applied'])
        self.assertEqual(d['beta'], .025)

    def test_u4_skips_one_bad_window_and_includes_t(self):
        p = series(turns=4)
        for w in p['windows']:
            for m in w['members']:
                m['eligible'] = True
        p['windows'][0]['members'][4]['eligible'] = False
        r = ac.u4(p['reference'], p['windows'])
        self.assertEqual(r['window_count'], 11)  # W1 plus 10 admissible C/T
        self.assertTrue(r['per_window']['C1']['skipped'])
        self.assertEqual(r['per_window']['C2']['status'], 'unevaluable')
        self.assertEqual(r['per_window']['C3']['window_count'], 3)
        self.assertIn('T3', r['per_window'])

    def test_u5_intercept_three_points_df_one_and_no_escalation(self):
        evidence = dict(states=[dict(g0_slow_c=x, turn_owned_j=100+.1*x+z,
                                    token_identical=True, designed_target_c=x)
                               for x, z in ((50., -.1), (55., .2), (60., -.1))],
                        r1_replay_j=[100., 100.], delta_slow_c=1.)
        r = ac.u5(evidence)
        self.assertEqual(r['df'], 1)
        self.assertAlmostEqual(r['beta_T_j_per_c'], .1)
        self.assertFalse(r['triggers_R20'])

    def test_u6_pooled_full_fit_scale(self):
        records = [dict(trajectory=str(i), start_ns=i, residual_j=[10.*i, 10.*i+1]) for i in range(8)]
        r = ac.u6(records, 'within_pair_episode_order', pooled_rss=8., pooled_df=8)
        self.assertEqual(r['s_r_j'], 1.)
        self.assertEqual(r['margin_j'], .5)

    def test_cp_zero_and_all(self):
        r = e._test_summary([dict(alarm=False, window='T1') for _ in range(21)])
        self.assertAlmostEqual(r['fpr_upper_95'], 1-.05**(1/21))
        self.assertEqual(e._test_summary([dict(alarm=True, window='T1')])['fpr_upper_95'], 1.)

    def test_escalated_roster_supplemental_and_b_release_presence(self):
        p = series(turns=4); p['windows'] = p['windows'][:3]
        for w in p['windows']:
            for slot in e.roster(w['window'], escalated=True)[22:]:
                m = copy.deepcopy(w['members'][4]); m['slot'] = slot
                m['thermal'].update(id=slot['run_id'], identical_work_group=None)
                w['members'].append(m)
            w['members'][5]['thermal']['battery']['flags'] = ['battery.member_span']
        fill, _ = analyze(p)
        self.assertEqual(fill['windows'][2]['consecutive_B_failures'], 3)
        self.assertFalse(fill['windows'][2]['lead_release_present'])
        self.assertEqual(len(fill['windows'][0]['supplemental_sentinels']), 2)
        self.assertEqual(len(fill['windows'][0]['checks'][e.D_MODEL]['U3']['pairs']), 1)

    def test_carrier_prefix_crossing_and_type_one_interval(self):
        rows = [dict(pair='p', carrier=str(i), window=str(i//10), h=h, score=score)
                for i in range(40) for h, score in ((0, float(i)/100), (128, 2.), (256, 0.))]
        rows += [dict(pair='p', carrier=str(i), window=str(i//10), h=384, score=2.) for i in range(30)]
        r = est.benign_carrier_curve(rows)['pairs']['p']
        self.assertEqual(r['H50'], 128)
        self.assertEqual(r['H90'], 128)
        self.assertEqual(r['n_by_h'][384], 30)
        self.assertFalse(r['monotone'])
        self.assertEqual(r['window_cluster_bootstrap']['H50'], [128, 128])
        self.assertEqual(est._quantile([128, 256], .95), 256)


if __name__ == '__main__':
    unittest.main()
