from __future__ import annotations

import math
import statistics
import unittest

from joulewise.quiet_kit import analysis as a


def segment(kind, values, **fields):
    return {'id': kind, 'kind': kind, 'records': [{'total': v, 'gpu_power': v, 'cpu_power': v,
            'ane_power': 0., 'meter': 2*v+1} for v in values], **fields}


class AnalysisTests(unittest.TestCase):
    def test_m4_watts_and_propagated_record_scatter(self):
        before = segment('idle', [.04, .05, .06])
        load = segment('cpu', [.29, .30, .31], cpu_seconds=3., elapsed_s=60., duty=.05)
        after = segment('idle', [.04, .05, .06])
        result = a.m4({'segments': [before, load, after]})['arms'][0]
        self.assertAlmostEqual(result['watts_per_cpu_rate']['value'], .25/.05)
        se = math.sqrt((.01/math.sqrt(3))**2*1.5)/.05
        self.assertAlmostEqual(result['watts_per_cpu_rate']['uncertainty']['value'], se)

    def test_m4_burst_energy_and_idle_scatter(self):
        before = segment('idle', [.04, .06])
        after = segment('idle', [.04, .06])
        burst = {'id': 'burst', 'kind': 'burst', 'burst_s': .62, 'burst_on_s': 1., 'burst_off_s': 1.62,
                 'records': [{'start_s': 1., 'end_s': 1.62, 'total': 4.05}], 'accounting_intervals': [{'cpu_s_per_s': .062}]}
        out = a.m4({'segments': [before, burst, after]})['bursts'][0]['added_energy']
        self.assertAlmostEqual(out['value'], 4*.62)
        # Four idle observations [.04,.06,.04,.06], sample variance .0004/3.
        self.assertAlmostEqual(out['uncertainty']['value'], math.sqrt(.0004/3)*(.62+.5+1))

    def test_m4_permitted_phase_work_accounts_for_two_ticks(self):
        before=segment('idle',[.05,.05])
        burst={'kind':'burst','burst_s':2.,'placement_s':9.4,'cpu_seconds':2.,
               'burst_on_s':9.4,'burst_off_s':11.4,
               'records':[{'start_s':9.4,'end_s':11.4,'total':4.05}]}
        out=a.m4({'segments':[before,burst,before]})['bursts'][0]
        # A 2 s phase across a tick can use .5 CPU-s from each interval.
        self.assertEqual(out['permitted_cpu_seconds_inside_phase'],1.)
        self.assertAlmostEqual(out['phase_energy_below_census_limit']['value'],4.)

    def test_m5_gpu_step_and_floor_formula(self):
        data = {'segments': [segment('idle', [1., 1.]), segment('gpu', [6., 6.], duty=.05,
                    cpu_seconds=.1, elapsed_s=10.), segment('idle', [1., 1.])]}
        out = a.m5(data)
        self.assertEqual(out['levels'][0]['added_power']['gpu_power']['value'], 5.)
        self.assertEqual(out['levels'][0]['contender_cpu_rate']['value'], .01)
        self.assertIn('F_min_J / 4', out['excluding_power_formula'])
        self.assertAlmostEqual(out['non_claim_illustration']['power_W'], 2.1/(4*.62))

    def test_m1_pairs_screen_and_exact_binomial_interval(self):
        out = a.m1({'captures': [{'id': 'q1', 'condition': 'quiet', 'bound_s': .028},
            {'id': 'q2', 'condition': 'quiet', 'bound_s': .030},
            {'id': 'u', 'condition': 'utility', 'bound_s': .124}]})
        qmax = .030+.014531
        dmin = .124+(.124-.030)
        self.assertAlmostEqual(out['separation']['utility']['value'], (dmin-qmax)*1000)
        self.assertEqual(len(out['quiet_ordered_pairs']), 2)
        interval = out['quiet_fraction_above_screen']['uncertainty']['value']
        self.assertEqual(interval[0], 0.)
        self.assertAlmostEqual(interval[1], 1-math.sqrt(.025))
        self.assertEqual(a.clopper_pearson(2, 2)[1], 1.)
        self.assertAlmostEqual(a.clopper_pearson(2, 2)[0], math.sqrt(.025))

    def test_m2_quads_and_specified_t_interval(self):
        differences = [.1, .2, .3, .4, .5]
        runs = []
        for q, difference in enumerate(differences):
            for i, arm in enumerate(('N', 'L', 'L', 'N')):
                runs.append({'id': f'{q}-{i}', 'quad': q, 'arm': arm,
                             'phase_energy_j': {'prefill': 10+(difference if arm == 'L' else 0)}})
        out = a.m2({'runs': runs})['phases']['prefill']
        expected_se = math.sqrt(sum((d-.3)**2 for d in differences)/4)/math.sqrt(5)
        self.assertAlmostEqual(out['long_minus_ordinary']['value'], .3)
        interval = out['long_minus_ordinary']['uncertainty']['value']
        self.assertAlmostEqual(interval[0], .3-2.776*expected_se)
        self.assertAlmostEqual(interval[1], .3+2.776*expected_se)
        self.assertAlmostEqual(out['percent']['value'], 3.)

    def test_m1_missing_bound_remains_in_pairs_and_does_not_shrink_binomial_denominator(self):
        out=a.m1({'captures':[{'id':'q1','condition':'quiet','bound_s':.028},
            {'id':'q2','condition':'quiet','bound_s':None},{'id':'u','condition':'utility','bound_s':.124}]})
        self.assertEqual(len(out['quiet_ordered_pairs']),2)
        self.assertTrue(all(p['operative_bound']['value'] is None for p in out['quiet_ordered_pairs']))
        self.assertIsNone(out['quiet_fraction_above_screen']['value'])
        self.assertIsNone(out['separation']['utility']['value'])

    def test_m3_clock_rate_slope_uncertainty_and_budget(self):
        # Residual vector is orthogonal to 1 and x, giving an independent
        # residual sum of squares and therefore an exact slope SE.
        noise = [1., -2., 2., -2., 1.]
        rows = []
        for i, residual in enumerate(noise):
            x_ns = i*10_000_000_000
            rows.append({'boot_session_uuid': 'boot', 'anchor': {'monotonic_raw_ns': x_ns,
                'realtime_ns': 10**18+x_ns+round(2.72e-6*x_ns)+int(residual*1000)},
                'frequency': {'frequency_ppm': 2.72}})
        out = a.m3({'clock': rows, 'longest_sampler_s': 2000})['segments'][0]
        self.assertAlmostEqual(out['rate']['value'], 2.72)
        expected_se = math.sqrt(14e-12/3)/math.sqrt(1000)*1e6
        self.assertAlmostEqual(out['rate']['uncertainty']['value'], expected_se)
        self.assertAlmostEqual(out['budgets'][0]['budget']['value'], .010/2000*1e6)
        self.assertAlmostEqual(out['budgets'][1]['budget']['value'], .010/1835*1e6)
        self.assertAlmostEqual(out['residual_max']['value'], .002)

    def test_m3_boot_and_gap_split(self):
        rows = [{'boot_session_uuid': b, 'anchor': {'monotonic_raw_ns': t*10**9, 'realtime_ns': t*10**9}}
                for t, b in [(0,'a'), (10,'a'), (20,'a'), (100,'a'), (110,'b'), (120,'b')]]
        self.assertEqual(len(a.m3({'clock': rows})['segments']), 3)

    def test_m3_frequency_probe_failure_does_not_discard_measured_anchors(self):
        rows=[{'boot_session_uuid':'a','anchor':{'monotonic_raw_ns':i*10**10,
               'realtime_ns':i*10**10+27200*i},'frequency':None,'error':'frequency probe failed'} for i in range(3)]
        out=a.m3({'clock':rows})
        self.assertAlmostEqual(out['segments'][0]['rate']['value'],2.72)
        self.assertIsNone(out['segments'][0]['stored_correction']['value'])

    def test_m9_detrended_scatter_and_reference_chi_square(self):
        queries = []
        residuals = [1., -2., 2., -2., 1.]
        for i, r in enumerate(residuals):
            for server, offset in (('time.apple.com', .1), ('time.cloudflare.com', .09)):
                queries.append({'query': i, 'server': server, 'time_s': i*60., 'offset_s': offset+i*.001+r*.001})
        out = a.m9({'queries': queries})
        scatter = out['servers']['time.apple.com']['one_query_scatter']
        self.assertAlmostEqual(scatter['value'], math.sqrt(14/3))
        self.assertAlmostEqual(out['apple_minus_cloudflare']['value'], 10.)
        self.assertAlmostEqual(a.chi2_quantile(.025, 3), .2157952826, places=8)
        self.assertAlmostEqual(a.chi2_quantile(.975, 3), 9.348403604, places=8)
        self.assertAlmostEqual(scatter['uncertainty']['value'][0], math.sqrt(14/9.348403604))

    def test_m14_meter_steps_noise_and_battery_flag(self):
        before, after = segment('idle', [1., 2., 3.]), segment('idle', [1., 2., 3.])
        load = segment('gpu', [3., 4., 5.], duty=.2, battery_current_ma=[201])
        out = a.m14({'segments': [before, load, after]})
        self.assertEqual(out['levels'][0]['meter_step']['value'], 4.)
        self.assertEqual(out['levels'][0]['rail_step']['value'], 2.)
        self.assertEqual(out['levels'][0]['rails_over_meter']['value'], .5)
        self.assertEqual(out['idle_noise'][0]['noise']['value'], 2.)
        self.assertTrue(out['levels'][0]['battery_flag'])

    def test_m10_affine_wall_fit_and_battery_exclusion(self):
        rows = [segment('cpu', [v,v], battery_current_ma=[0]) for v in (1., 2., 3., 4.)]
        bad = segment('gpu', [10.,10.], battery_current_ma=[250])
        for r in bad['records']:
            r['meter'] = 100.
        out = a.m10({'segments': rows+[bad]})
        self.assertAlmostEqual(out['charger_supplied_fit']['slope']['value'], 2.)
        self.assertAlmostEqual(out['charger_supplied_fit']['intercept']['value'], 1.)
        self.assertEqual(out['charger_supplied_fit']['slope']['uncertainty']['value'], [2., 2.])
        self.assertNotAlmostEqual(out['all_levels_fit']['slope']['value'], 2.)
        self.assertAlmostEqual(a.t975(4), 2.776445105, places=7)

    def test_m13_independent_edges_lag_and_uncertainty(self):
        lags = [.010, .012, .014]
        data = {'edges': [{'command_s': i, 'meter_s': i+lag, 'sampler_s': i+.030}
                          for i, lag in enumerate(lags)]}
        out = a.m13(data)
        self.assertAlmostEqual(out['meter_lag_mean']['value'], 12.)
        self.assertAlmostEqual(out['meter_lag_sd']['value'], 2.)
        self.assertAlmostEqual(out['meter_mean_lag_pooled_se']['value'], 2/math.sqrt(3))

    def test_m15_drift_difference_ratio_and_uncertainty(self):
        runs = []
        for w, energy, drift in [('R', 10., .1), ('A', 20., .3), ('B', 40., .5)]:
            for block, delta in [('start',0), ('end',drift)]:
                for residual in (-.1, .1):
                    runs.append({'workload': w, 'block': block, 'phase_energy_j': {'decode': energy+delta+residual}})
        out = a.m15({'runs': runs})
        self.assertAlmostEqual(out['drift_differences']['decode']['B-R']['value'], .4)
        # Every two-point block mean SE is .1; each drift SE sqrt(2)*.1.
        self.assertAlmostEqual(out['drift_differences']['decode']['B-R']['uncertainty']['value'], .2)
        self.assertAlmostEqual(out['energy_ratios']['decode']['B']['value'], 40.25/10.05)

    def test_empty_and_single_record_inputs_never_lose_attempt(self):
        for fn in a.FUNCTIONS.values():
            with self.subTest(fn=fn.__name__):
                result = fn({})
                self.assertIsInstance(result, dict)
                result = fn({'segments': [segment('idle', [1.])], 'clock': [], 'captures': [], 'runs': [], 'queries': []})
                self.assertIsInstance(result, dict)
        self.assertIsNone(a.mean([1.], 'W')['uncertainty']['value'])
        self.assertIsNone(a.sd([1.], 'W')['value'])
