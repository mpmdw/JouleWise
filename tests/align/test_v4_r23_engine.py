"""A37/R23 hand witnesses. Every observation is synthetic."""
from array import array
import copy
from dataclasses import asdict
import io
import json
import math
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import reduce_sol as sol, thermal_desk as td, v4_estimands as est
from joulewise.align.attribution import trace_energy
from joulewise.align.records import ClockMapping
from joulewise.align.apple.sampler import TRACE_DOMAIN
from joulewise.align.v4_analysis import analyze, acceptance as ac, dc, engine as e, raw
from joulewise.align.v4_analysis.io import canonical
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_attribution import episode, turn
from tests.align.v4_synthetic import synthetic_frames

NS = 1_000_000_000


def w1_window(payload):
    w = copy.deepcopy(payload['windows'][0])
    w.update(window='W1', attempt_id='W1#1')
    # Only anchors and the actual W1 sentinel pair are needed for this desk.
    w['members'] = w['members'][:5] + [w['members'][21]]
    w['members'][-1]['slot']['ordinal'] = 17
    for m in w['members']:
        m['thermal']['ordinal'] = m['slot']['ordinal']
    return w


class SeamTests(unittest.TestCase):
    def samples(self, seam):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(2))))
        samples.columns['elapsed_ns'] = array('q', [NS, NS])
        samples.columns['gpu_power'] = array('d', [10., 20.])
        samples.endpoint_seconds = lambda _: array('d', [1., (2*NS+seam)/NS])
        return samples

    def trace(self, seam):
        traces, _ = self.samples(seam).power_traces(1., nominal_interval_ns=NS)
        return next(t for t in traces if t.channel == 'gpu_power')

    def test_gap_and_overlap_at_1000_snap_and_1001_stay(self):
        for seam in (1000, -1000, 1001, -1001):
            with self.subTest(seam=seam):
                samples = self.samples(seam)
                expected = NS if abs(seam) <= 1000 else NS+seam
                self.assertEqual(json.loads(self.trace(seam).notes)['sample_support_ns'][1][0], expected)
                self.assertEqual(samples.native_pm_samples(1., 0)[1]['start_ns'], expected)
                mapped = samples.mapped_columns(1., 0)
                self.assertEqual(mapped['power_start_ns'][1], expected)
                self.assertEqual(mapped['thermal_start_ns'][1], expected)

    def test_snapped_overlap_has_exact_energy_and_no_overlap(self):
        samples = self.samples(-1000)
        end = 2*NS-1000
        ep = episode(start_ns=0, end_ns=end, turns=(turn(0, 0, end, 1),),
                     power_traces=(), clock_mappings=(ClockMapping(TRACE_DOMAIN, 'host', 0, 0, 'synthetic'),))
        r = sol.turn_energy_table(samples, ep, first_record_endpoint_s=1., nominal_interval_ns=NS)['gpu_power']
        self.assertEqual(r['turns'][0]['owned_j'], 29.99998)
        self.assertNotIn('window.overlap', r['attribution']['total']['flags'])

    def test_large_seams_keep_gap_and_overlap_diagnostics(self):
        for seam, flag in ((1001, 'duty.uncovered'), (-1001, 'window.overlap')):
            with self.subTest(seam=seam):
                r = trace_energy(self.trace(seam), 0, 2*NS+seam)
                self.assertIn(flag, r.flags)

    def test_tiny_edge_gaps_count_on_both_edges(self):
        trace = self.trace(0)
        for a, b in ((-100, 2*NS), (0, 2*NS+100)):
            with self.subTest(span=(a,b)):
                r = trace_energy(trace, a, b)
                self.assertIn('trace.partial_coverage', r.flags)

    def test_epoch_float_placement_seams_are_closed(self):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(40))))
        traces, _ = samples.power_traces(1767225600., nominal_interval_ns=100_000_000)
        for trace in traces:
            supports = json.loads(trace.notes)['sample_support_ns']
            self.assertTrue(all(a[1] == b[0] for a,b in zip(supports,supports[1:])))
        pm = samples.native_pm_samples(1767225600., -1767225500000000000)
        self.assertTrue(all(a['end_ns'] == b['start_ns'] for a,b in zip(pm,pm[1:])))

    def test_scanner_reference_and_observation_cache_remain_byte_identical(self):
        data = b''.join(synthetic_frames(40))
        a = sol.reduce_stream(io.BytesIO(data))
        b = sol.reduce_stream(io.BytesIO(data), reference=True)
        self.assertEqual(sol.encode_columns(a), sol.encode_columns(b))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = root/'synthetic.plist'; path.write_bytes(data)
            cold = sol.reduce_file(path, cache_dir=root/'cache')
            hit = sol.reduce_file(path, cache_dir=root/'cache')
            def trace_bytes(samples):
                traces, flags = samples.power_traces(1767225600., nominal_interval_ns=100_000_000)
                return canonical(dict(traces=[asdict(t) for t in traces],flags=flags))
            self.assertEqual(trace_bytes(cold), trace_bytes(hit))

    def test_fixed_tolerance_is_in_loaded_reducer_identity(self):
        before = sol.producer_sha256()
        with patch.object(sol, 'INTERIOR_SEAM_NS', 1001):
            self.assertNotEqual(before, sol.producer_sha256())


class CaptureAndAnchorTests(unittest.TestCase):
    def test_c3_zero_capture_then_retry_runs_full_series_with_eight_counted(self):
        p = series(turns=4)
        zero = copy.deepcopy(p['windows'][2])
        zero['members'] = [raw.member(Path.cwd(), m['slot'], {'captured': False}) for m in zero['members']]
        p['windows'][2]['attempt_id'] = 'C3#2'
        p['windows'].insert(2, zero)
        fill, verdict = analyze(p)
        self.assertEqual(verdict['counted_windows'], 8)
        self.assertEqual(fill['calibration']['zero_capture_refusals'], 1)
        self.assertEqual(fill['ledger'][2]['status'], 'final')
        self.assertEqual(fill['ledger'][2]['eligible_total'], 0)
        self.assertFalse(fill['windows'][2]['pool_entry'])
        self.assertEqual(fill['windows'][2]['checks'], {})
        self.assertEqual(sum(f['window'] == 'C3' for f in fill['fits']), 4)
        self.assertTrue(any(f['window'] == 'T3' for f in fill['fits']))
        for pair in fill['benign_carriers']['pairs'].values():
            self.assertEqual(pair['status'], 'ok')
            self.assertGreater(pair['curve'][0][1], 0.)

    def test_not_captured_stale_payload_cannot_enter_acceptance_or_u4(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        a, _ = analyze(p)
        m = copy.deepcopy(p['windows'][0]['members'][4])
        m['captured'] = False
        m['thermal'].update(captured=False, pm_period_s=None, pm_max_gap_s=999., identity_sha256='f'*64)
        m['summary']['residual_rows'] = {'True': [{}], 'False': [{}]}
        p['windows'][0]['members'][4] = m
        b, _ = analyze(p)
        u1a = a['windows'][0]['checks'][e.D_MODEL]['U1']
        u1b = b['windows'][0]['checks'][e.D_MODEL]['U1']
        self.assertEqual(u1a['status'], u1b['status'])
        self.assertEqual(u1b['turn_admissions'], u1a['turn_admissions']-3)
        self.assertEqual(b['U4']['per_window']['C1']['skipped'], True)
        self.assertEqual(td.acceptance([m['thermal']], v4=True)['U1']['turn_admissions'], 0)

    def test_w1_is_twelfth_anchor_window_and_selection_export_also_works(self):
        p = series(turns=4)
        w1 = w1_window(p); p['windows'].insert(0, w1)
        fill, _ = analyze(p)
        self.assertEqual(fill['U4']['window_count'], 12)
        self.assertEqual(fill['anchor_sigma_w']['K'], 12)
        self.assertEqual(fill['anchor_sigma_w']['status'], 'print_only')
        p['windows'].pop(0)
        p['selection_desk'] = dict(members=[m['thermal'] for m in w1['members']])
        fill, _ = analyze(p)
        self.assertEqual(fill['anchor_sigma_w']['K'], 12)

    def test_negative_moment_and_clamped_variance_both_print_and_k_minimum(self):
        windows = []
        for i, values in enumerate(((99.,101.,99.,101.), (101.,99.,101.,99.), (100.,100.,100.,100.))):
            windows.append(dict(window='C'+str(i+1), members=[dict(captured=True, eligible=True,
                slot=dict(series_role='anchor',ordinal=j), thermal=dict(turn_owned_j=value))
                for j,value in enumerate(values,1)]))
        r = ac.anchor_diagnostic(windows)
        self.assertEqual(r['sigma_w2_raw_j2'], -1/3)
        self.assertEqual(r['sigma_w2_reported_j2'], 0.)
        self.assertEqual(r['anchor_sigma_j'], 0.)
        self.assertIn('K >= 3', ac.anchor_diagnostic(windows[:2])['reason'])
        for i,w in enumerate(windows):
            for m in w['members']:
                m['thermal']['turn_owned_j'] = 100.+i
        r = ac.anchor_diagnostic(windows)
        self.assertEqual(r['sigma_w2_raw_j2'], 1.)
        self.assertEqual(r['sigma_w2_reported_j2'], 1.)
        self.assertEqual(r['anchor_sigma_j'], 1.)


class CarrierTests(unittest.TestCase):
    def rows(self, count=40):
        return [dict(pair='p',carrier=str(i),window='W'+str(i//10),h=h,score=score)
                for i in range(count) for h,score in ((0,float(i)),(128,100.))]

    def test_h0_is_honest_strict_leave_one_out_fraction(self):
        r = est.benign_carrier_curve(self.rows(),bootstrap_replicates=0)['pairs']['p']
        self.assertEqual(r['curve'], [(0,1/40),(128,1.)])
        self.assertEqual(r['status'], 'ok')
        self.assertEqual((r['H50'],r['H90']), (128,128))
        rows = self.rows()
        for row in rows:
            if row['h'] == 0:
                row['score'] = 1.
        r = est.benign_carrier_curve(rows,bootstrap_replicates=0)['pairs']['p']
        self.assertEqual(r['curve'][0], (0,0.))  # ties never alarm

    def test_unreachable_dose_is_crossing_status_not_pair_calibration(self):
        rows = [r for r in self.rows() if r['h'] == 0 or int(r['carrier']) < 10]
        r = est.benign_carrier_curve(rows,grid=(0,128,256),bootstrap_replicates=20)['pairs']['p']
        self.assertEqual(r['status'],'ok')
        self.assertIsNone(r['H50'])
        self.assertEqual(r['H50_status'],'undefined: dose unreachable')
        self.assertEqual(r['H90_status'],'undefined: dose unreachable')
        self.assertEqual(r['bootstrap_undefined_replicates']['H50'],20)
        few = est.benign_carrier_curve(self.rows(39),bootstrap_replicates=0)['pairs']['p']
        self.assertEqual(few['status'],'insufficient_calibration')

    def test_level_reached_at_h0_stays_undefined_even_with_later_positive_crossing(self):
        # The ordinary .025 rank cannot reach .5 at H=0 in a full sample.
        # Exercise the explicit guard with a synthetic low threshold.
        with patch.object(est,'calibration_cutoff',return_value=dict(threshold=-1.)):
            r = est.benign_carrier_curve(self.rows(),bootstrap_replicates=10)['pairs']['p']
        self.assertIsNone(r['H50']); self.assertIsNone(r['H90'])
        self.assertEqual(r['level_reached_at_h0'],dict(H50=True,H90=True))
        self.assertEqual(r['H50_status'],'level_reached_at_h0')
        self.assertEqual(r['bootstrap_undefined_replicates']['H90'],10)

    def test_bootstrap_h0_guard_uses_honest_rate_with_fixed_original_thresholds(self):
        rows = self.rows()
        for row in rows:
            row['window'] = 'peak' if row['carrier'] == '39' else 'rest'
        r = est.benign_carrier_curve(rows,bootstrap_replicates=20)['pairs']['p']
        rng = random.Random(0)
        expected = sum(rng.choices(['peak','rest'],k=2) == ['peak','peak'] for _ in range(20))
        self.assertGreater(expected,0)
        self.assertEqual(r['curve'][0],(0,1/40))
        self.assertEqual(r['bootstrap_undefined_replicates']['H50'],expected)
        self.assertEqual(r['window_cluster_bootstrap']['H50'],[128,128])


class DCRowTests(unittest.TestCase):
    def capture(self, _streams, member, _span):
        rows = [{**r, 'energy_j': r['energy_j']*2., 'energy_half_width_j': 0.,
                 'uncertainty_kind':'standard_uncertainty'} for r in e._rows(member)]
        return dict(status='available', turn_rows=rows, turn_owned_j=math.fsum(r['energy_j'] for r in rows),
                    whole_member_j=1., battery_assist=dict(status='unavailable',joules=None))

    def payload(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        p['windows'].insert(0,w1_window(p))
        for w in p['windows']:
            for m in w['members']:
                if m['slot']['condition'] == 'benign':
                    m['dc_evidence'] = dict(streams=[],episode=copy.deepcopy(m),member_span_ns=[])
        return p

    def test_dc_residual_rows_and_training_sets_equal_gpu_logged_benign(self):
        with patch.object(dc,'capture',side_effect=self.capture):
            fill, _ = analyze(self.payload())
        gpu = {(f['window'],f['pair'],r['run_id']):r for f in fill['fits']
               if f['convention'] == 'counts_logged' for r in f['scores'] if r['condition']=='benign'}
        rows = [r for r in fill['dc_secondary'] if r.get('residual_status') == 'available']
        self.assertEqual({(r['window'],r['pair'],r['run_id']) for r in rows},set(gpu))
        self.assertFalse(any(r['window']=='W1' and r.get('residual_status')=='available' for r in fill['dc_secondary']))
        for r in rows:
            g = gpu[r['window'],r['pair'],r['run_id']]
            self.assertEqual(r['training_run_ids'],g['training_trajectories'])
            self.assertAlmostEqual(r['prediction_j'],2*g['predicted_j'])
            self.assertAlmostEqual(r['residual_j'],2*g['residual_j'])

    def test_missing_dc_trainer_never_silently_changes_gpu_training_set(self):
        p = self.payload()
        missing = p['windows'][1]['members'][5]
        missing.pop('dc_evidence')
        with patch.object(dc,'capture',side_effect=self.capture):
            fill, _ = analyze(p)
        pair = missing['slot']['task_pair']
        rows = [r for r in fill['dc_secondary'] if r.get('pair')==pair and not r.get('sealed')]
        self.assertTrue(rows)
        for r in rows:
            if r['run_id'] == missing['slot']['run_id']:
                self.assertEqual(r['residual_status'],'dc_unavailable')
            else:
                self.assertEqual(r['residual_status'],'dc_training_unavailable')
                self.assertIn(missing['slot']['run_id'],r['training_run_ids'])

    def test_dc_never_adds_ineligible_members_or_barred_window_rows(self):
        p = self.payload()
        excluded = p['windows'][1]['members'][5]
        excluded['source_flags'] = ['X5']
        called = []
        def capture(streams, member, span):
            called.append(member['slot']['run_id'])
            return self.capture(streams, member, span)
        with patch.object(dc,'capture',side_effect=capture):
            fill, _ = analyze(p)
        self.assertNotIn(excluded['slot']['run_id'],called)
        gpu_ids = {r['run_id'] for f in fill['fits'] if f['convention']=='counts_logged'
                   for r in f['scores'] if r['condition']=='benign'}
        self.assertEqual(set(called),gpu_ids)
        for m in p['windows'][1]['members']:
            if m['slot']['model_id']==e.D_MODEL:
                m['thermal']['registered_os_nonzero'] = True
        with patch.object(dc,'capture',side_effect=AssertionError('barred window has no DC residuals')):
            fill, _ = analyze(p)
        self.assertFalse(any(r.get('residual_status') for r in fill['dc_secondary']))


if __name__ == '__main__':
    unittest.main()
