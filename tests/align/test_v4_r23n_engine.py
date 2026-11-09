"""R23n hand witnesses (lead rulings on the Opus review of r23m). All inputs synthetic."""
import copy
import json
import unittest

from joulewise.align.v4_analysis import analyze, engine as e
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23m_engine import capture, stream
from tests.align.test_attribution import episode, turn

MS = 1_000_000


def drop_g0(member):
    member['thermal']['intervals'] = [i for i in member['thermal']['intervals'] if i['kind'] != 'G0']


class PlannedG0Tests(unittest.TestCase):
    def c1(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        return p

    def test_one_missing_planned_g0_excludes_that_member_and_u2a_uses_the_rest(self):
        p = self.c1()
        target = p['windows'][0]['members'][6]
        target['thermal']['g0_slow_c'] = 99.         # would break the U2 range if it entered
        drop_g0(target)
        fill, _ = analyze(p)
        row = fill['windows'][0]['eligibility'][6]
        self.assertFalse(row['eligible'])
        self.assertIn('g0_missing', row['reasons'])
        self.assertEqual(row['classes'], ['g0_missing'])
        u2 = fill['windows'][0]['checks'][e.D_MODEL]['U2']
        self.assertEqual(u2['parts']['a'], 'pass')
        # C windows seal the all-member range (A27); the benign-only range is printed.
        self.assertLess(u2['benign_only']['g0_slow_range_c'], 1.)
        pair = e.KEYS[target['slot']['task_pair']]
        self.assertEqual(fill['ledger'][0]['eligible_benign'][pair], 6)
        for f in fill['fits']:
            self.assertNotIn(target['slot']['run_id'], [r['run_id'] for r in f['scores']])

    def test_no_planned_g0_present_makes_u2a_inconclusive(self):
        p = self.c1()
        for member in p['windows'][0]['members'][4:]:
            drop_g0(member)
        fill, _ = analyze(p)
        u2 = fill['windows'][0]['checks'][e.D_MODEL]['U2']
        self.assertEqual(u2['parts']['a'], 'inconclusive')
        self.assertTrue(all('g0_missing' in r['reasons'] for r in fill['windows'][0]['eligibility'][4:]
                            if r.get('status') != 'sealed'))

    def test_unplanned_anchor_g0_is_not_required(self):
        p = self.c1()
        for member in p['windows'][0]['members'][:4]:
            drop_g0(member)
        fill, _ = analyze(p)
        for row in fill['windows'][0]['eligibility'][:4]:
            self.assertNotIn('g0_missing', row.get('reasons', []))

    def test_not_captured_member_keeps_only_not_captured(self):
        from pathlib import Path
        from joulewise.align.v4_analysis import raw
        p = self.c1()
        m = p['windows'][0]['members'][6]
        p['windows'][0]['members'][6] = raw.member(Path.cwd(), m['slot'], {'captured': False})
        fill, _ = analyze(p)
        self.assertEqual(fill['windows'][0]['eligibility'][6]['classes'], ['not_captured'])


class PrefixTestRowsTests(unittest.TestCase):
    def test_by_window_lists_only_present_t_windows(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:9]               # C1-C8 + T1
        fill, _ = analyze(p)
        for convention in e.CONVENTIONS:
            for pair in fill['test'][convention].values():
                for condition in pair.values():
                    self.assertEqual(sorted(condition['by_window']), ['T1'])
        p = series(turns=4)
        fill, _ = analyze(p)
        self.assertEqual(sorted(fill['test']['counts_logged']['spam']['benign']['by_window']), ['T1', 'T2', 'T3'])


class WholeMemberDCTests(unittest.TestCase):
    def test_span_defect_prints_null_whole_member_with_flag(self):
        ep = episode(turns=(turn(start=100*MS, first=125*MS, end=200*MS),), start_ns=0, end_ns=900*MS)
        # The member span runs past the last sample: no extrapolated whole value.
        result = capture(ep, stream([0, 100, 200, 300, 400], [10.]*5))
        self.assertEqual(result['status'], 'available')
        self.assertIsNone(result['whole_member_j'])
        self.assertIn('meter.member_uncovered_or_gap', result['flags'])
        self.assertAlmostEqual(result['turn_owned_j'], 1.)

    def test_covered_span_keeps_the_production_integral(self):
        ep = episode(turns=(turn(start=100*MS, first=125*MS, end=200*MS),), start_ns=0, end_ns=300*MS)
        result = capture(ep, stream([0, 100, 200, 300], [10.]*4))
        self.assertNotIn('meter.member_uncovered_or_gap', result['flags'])
        self.assertAlmostEqual(result['whole_member_j'], 3.)



class PreCompletionPrintTests(unittest.TestCase):
    """R27: before calibration_complete every threshold-dependent leaf is null under one word."""
    WITHHELD = 'withheld_until_calibration_complete'

    def prefix(self):
        from tests.align.test_v4_r23_engine import w1_window
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        p['windows'].insert(0, w1_window(p))
        fill, _ = analyze(p)
        self.assertEqual(fill['calibration']['decision'], 'continue')
        return fill

    def test_thresholds_withheld_with_counts_kept(self):
        for key, cut in self.prefix()['thresholds'].items():
            with self.subTest(threshold=key):
                self.assertEqual(cut['status'], self.WITHHELD)
                for leaf in ('rank', 'threshold', 'marginal_fpr_bound', 'iid_continuous_fpr_upper90',
                             'generic_rank_025', 'generic_rank_05'):
                    self.assertIsNone(cut[leaf], leaf)
                for block in ('rank_38_sensitivity', 'rank_05_sensitivity'):
                    self.assertIsNone(cut[block]['rank'])
                    self.assertIsNone(cut[block]['threshold'])
                self.assertEqual(cut['m'], 7)
                self.assertEqual(len(cut['calibration_members']), 7)

    def test_h_star_blocks_present_and_withheld_while_dose_strips_print(self):
        fill = self.prefix()
        rows = [r for f in fill['fits'] if f['convention'] == 'counts_logged'
                for r in f['scores'] if r['condition'] == 'benign']
        self.assertTrue(rows)
        for r in rows:
            h = r['H_star']
            self.assertEqual(h['status'], self.WITHHELD)
            self.assertIsNone(h['h_star']); self.assertIsNone(h['bounded_above'])
            self.assertIsNone(h['undefined_missing_grid_doses'])
            self.assertIn(300, h['off_grid_doses'])
            self.assertTrue(any(v['score'] is not None for v in r['H_grid']))
            self.assertTrue(all(v['above_threshold'] is None for v in r['H_grid']))

    def test_carrier_curve_counts_print_and_everything_else_is_null(self):
        for pair in self.prefix()['benign_carriers']['pairs'].values():
            self.assertEqual(pair['status'], self.WITHHELD)
            self.assertTrue(all(p is None for _, p in pair['curve']))
            self.assertEqual(pair['n_by_h']['0'], 7)
            for leaf in ('H50', 'H90', 'level_reached_at_h0', 'all_carrier_prefix', 'monotone',
                         'window_cluster_bootstrap'):
                self.assertIsNone(pair[leaf], leaf)
            self.assertNotIn('bootstrap_undefined_replicates', pair)
            self.assertEqual((pair['full_cell']['status'], pair['full_cell']['fraction']), (self.WITHHELD, None))
            self.assertEqual(pair['full_cell']['n'], 7)

    def test_u6_imprecise_only_with_an_interval(self):
        from joulewise.align.v4_analysis import acceptance as ac
        one = [dict(pair='p', start_ns=0, trajectory='C1/a', residual_j=[1., 2.])]
        self.assertIsNone(ac.u6(one, 'within_pair_episode_order', pooled_rss=1., pooled_df=1)['imprecise'])
        self.assertEqual(ac.u6(one, 'within_pair_episode_order')['reason'], 'insufficient trajectories')
        for u6 in self.prefix()['U6'].values():
            if 'ci90_j' in u6:
                self.assertIn(u6['imprecise'], (True, False))
            else:
                self.assertIsNone(u6['imprecise'])

    def test_complete_series_prints_nothing_withheld(self):
        fill, _ = analyze(series(turns=4))
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')
        self.assertNotIn(self.WITHHELD, json.dumps(fill))
        for cut in fill['thresholds'].values():
            self.assertEqual(cut['status'], 'available')
            self.assertIsNotNone(cut['threshold']); self.assertIsNotNone(cut['rank'])
        for pair in fill['benign_carriers']['pairs'].values():
            self.assertEqual(pair['status'], 'ok')
            self.assertIn('bootstrap_undefined_replicates', pair)
            self.assertIsNotNone(pair['curve'][0][1])
        self.assertTrue(all(r['H_star']['status'] == 'registered_secondary'
                            for f in fill['fits'] if f['convention'] == 'counts_logged'
                            for r in f['scores'] if 'H_star' in r))

if __name__ == '__main__':
    unittest.main()
