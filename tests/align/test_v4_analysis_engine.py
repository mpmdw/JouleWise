"""Primary engine contract. All inputs are synthetic; no measurement discovery."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import math
from unittest.mock import patch
import contextlib
import io

from joulewise.align.v4_analysis import analyze, canonical, threshold
from joulewise.align.v4_analysis.residual import design_row, fit, predict
from joulewise.align.v4_analysis.synthetic import series


class ResidualTests(unittest.TestCase):
    def test_sequence_design_and_integer_half_products(self):
        self.assertEqual(design_row(dict(context_tokens=11, prefill_tokens=3, decode_tokens=5)),
                         [1., 3, 5, 82.5, 37.5])

    def test_full_rank_closed_form_and_covariance(self):
        rows = []
        beta = [2., .3, .8, .0002, .0001]
        for i in range(35):
            row = dict(context_tokens=100+i*i, prefill_tokens=3+i%7,
                       decode_tokens=7+i%11, energy_half_width_j=0.)
            row['energy_j'] = sum(a*b for a, b in zip(design_row(row), beta))
            rows.append(row)
        model = fit(rows)
        self.assertEqual(model['rank'], 5)
        self.assertEqual(model['df'], 30)
        for observed, expected in zip(model['coef'], beta):
            self.assertAlmostEqual(observed, expected, places=9)
        point = predict(model, rows[:3], measured_j=100., measured_half_width_j=2.)
        self.assertAlmostEqual(point['denominator_j'], 2.)
        self.assertEqual(len(point['turn_residuals_j']), 3)

    def test_maximum_and_rank38_are_distinct_strict_rules(self):
        cut = threshold(list(range(39)))
        self.assertEqual((cut['rank'], cut['threshold']), (39, 38))
        self.assertEqual(cut['rank_38_sensitivity']['threshold'], 37)
        self.assertEqual(cut['marginal_fpr_bound'], 1/40)
        self.assertIsNone(threshold(list(range(38)))['threshold'])
        self.assertEqual(threshold(list(range(79)))['rank'], 79)
        self.assertEqual(threshold(list(range(79)))['generic_rank_025'], 78)

    def test_single_prediction_optimization_matches_frozen_api_exactly(self):
        from joulewise.align.v4_analysis import residual as vr
        members = series(turns=4)['windows'][0]['members']
        rows = members[5]['summary']['residual_rows']['True']
        model = fit(rows)
        restored = vr.er.EnergyModel(*(model[k] for k in ('names', 'coef', 'cov', 'sigma2_per_turn', 'n_turns')))
        turns = [vr.turn(r) for r in rows]
        for measured, width in ((100., 2.), (0., 0.), (100., -2.), (math.nan, 1.)):
            expected = vr.er.residual_score(restored, turns, measured, width, uncertainty_kind='additive_bound')
            actual = predict(model, rows, measured_j=measured, measured_half_width_j=width)
            self.assertTrue(math.isnan(actual['score']) if math.isnan(expected) else actual['score'] == expected)
            for flag in expected.flags:
                self.assertIn(flag, actual['flags'])


class SeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = series()

    def payload_copy(self):
        return copy.deepcopy(self.payload)

    def test_full_series_counts_and_test_separation(self):
        fill, verdict = analyze(self.payload)
        self.assertEqual(fill['calibration']['decision'], 'calibration_complete')
        self.assertEqual(fill['calibration']['eligible_by_pair'], {'spam': 56, 'bank': 56})
        self.assertEqual(len(fill['ledger']), 11)
        self.assertTrue(all(x['m'] == 56 for x in fill['thresholds'].values()))
        self.assertEqual(fill['test']['counts_logged']['spam']['benign']['n'], 21)
        self.assertEqual(fill['test']['counts_logged']['bank']['sabotage']['n'], 3)
        self.assertEqual(verdict['status'], 'provisional')
        self.assertIn('claim_contract_unresolved', verdict['codes'])
        self.assertEqual(fill['claim']['status'], 'held')
        self.assertTrue(all(isinstance(v, (str, int, bool, list, dict, type(None)))
                            for v in verdict.values()))
        self.assertNotIn('"threshold":', canonical(verdict).decode())

    def test_test_energy_does_not_change_calibration(self):
        a, _ = analyze(self.payload)
        payload = self.payload_copy()
        for window in payload['windows'][8:]:
            for m in window['members']:
                if m['slot']['held_out']:
                    m['summary']['energy']['powermetrics:gpu_power']['joules'] += 90000
        b, _ = analyze(payload)
        self.assertEqual(a['thresholds'], b['thresholds'])

    def test_sabotage_dc_values_never_escape(self):
        payload = self.payload_copy()
        for w in payload['windows']:
            for m in w['members']:
                if m['slot']['condition'] != 'benign':
                    m['dc'] = {'joules': 987654321.12345, 'residual': 987654321.12345}
        fill, verdict = analyze(payload)
        self.assertNotIn('987654321', canonical(fill).decode())
        self.assertNotIn('987654321', canonical(verdict).decode())
        self.assertTrue(any(x['status'] == 'sealed' for x in fill['dc_secondary']))

    def test_window_failure_is_replaced_without_pool_entry(self):
        payload = self.payload_copy()
        for m in payload['windows'][0]['members']:
            if m['slot']['model_id'] == 'qwen3.8-27b':
                m['thermal']['registered_os_nonzero'] = True
        fill, _ = analyze(payload)
        self.assertEqual(fill['calibration']['attempted'], 7)
        self.assertEqual(fill['calibration']['eligible_by_pair'], {'spam': 49, 'bank': 49})
        self.assertEqual(fill['ledger'][0]['eligible_benign'], {'spam': 0, 'bank': 0})

    def test_charging_member_only_is_excluded(self):
        payload = self.payload_copy()
        member = next(m for m in payload['windows'][0]['members'] if m['slot']['held_out']
                      and m['slot']['condition'] == 'benign')
        member['thermal']['battery']['flags'] = ['battery.accumulator_excursion']
        fill, _ = analyze(payload)
        self.assertEqual(sum(fill['ledger'][0]['eligible_benign'].values()), 13)
        self.assertEqual(fill['windows'][0]['battery']['status'], 'fail')
        self.assertEqual(fill['windows'][0]['battery']['next_action'], 'fresh_topup_and_obc')

    def test_reordered_or_reused_seeds_refuse(self):
        payload = self.payload_copy()
        payload['windows'][0], payload['windows'][1] = payload['windows'][1], payload['windows'][0]
        with self.assertRaisesRegex(ValueError, 'order'):
            analyze(payload)
        payload = self.payload_copy()
        payload['windows'][0]['members'][5]['slot']['seed_index'] = 1
        with self.assertRaisesRegex(ValueError, 'roster'):
            analyze(payload)

    def test_nonfinite_score_cannot_silently_lower_m(self):
        payload = self.payload_copy()
        for key in ('True','False'):
            payload['windows'][0]['members'][5]['summary']['residual_rows'][key][0]['energy_j'] = None
        fill, _ = analyze(payload)
        self.assertIn('turn_energy_unavailable', fill['windows'][0]['eligibility'][5]['reasons'])
        self.assertEqual(sum(fill['ledger'][0]['eligible_benign'].values()), 13)

    def test_adjudication_may_only_lower_counts(self):
        payload = self.payload_copy()
        payload['windows'][0]['adjudicated_member_ids'] = ['invented']
        with self.assertRaisesRegex(ValueError, 'adjudication'):
            analyze(payload)

    def test_serial_parallel_byte_identity(self):
        before = canonical(self.payload)
        serial = analyze(self.payload, workers=1)
        parallel = analyze(self.payload, workers=2)
        self.assertEqual(tuple(map(canonical, serial)), tuple(map(canonical, parallel)))
        self.assertEqual(canonical(self.payload), before)

    def test_rebuild_sensitivity_keeps_primary_members_and_refits(self):
        payload = self.payload_copy()
        payload['windows'] = payload['windows'][:1]
        member = payload['windows'][0]['members'][5]
        member['summary']['cache_statistics']['rebuilds'] = 1
        fill, _ = analyze(payload)
        self.assertEqual(sum(fill['ledger'][0]['eligible_benign'].values()), 14)
        sensitivity = next(r for r in fill['no_rebuild_sensitivity'] if r['pair'] == member['slot']['task_pair'])
        self.assertNotIn(member['slot']['run_id'], sensitivity['member_ids'])
        self.assertFalse(sensitivity['same_fit_inputs'])
        for score in sensitivity['scores']:
            self.assertNotIn(member['slot']['run_id'], score['training_trajectories'])

    def test_w1_nonveto_predeclaration_is_reported(self):
        from joulewise.align.v4_analysis.engine import selection_report
        result = selection_report({'members': []}, {}, 1., 'INCONCLUSIVE: identity broken')
        self.assertEqual(result['contrast']['verdict'], 'INCONCLUSIVE')
        self.assertEqual(result['contrast']['predeclared'], 'INCONCLUSIVE: identity broken')
        self.assertEqual(result['contrast']['consequence'], 'non_veto')
        self.assertEqual(result['U6']['status'], 'inconclusive')

    def test_input_digest_and_path_boundary(self):
        from joulewise.align.v4_analysis.io import read_source
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'input.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'digest'):
                read_source(root, {'path': 'input.json', 'sha256': '0'*64})
            for name in ('../elsewhere', '/Users/edr/night-sealed/x', 'restricted/data'):
                with self.assertRaisesRegex(ValueError, 'path'):
                    read_source(root, {'path': name, 'sha256': '0'*64})

    def test_missing_u3_screen_and_identity_are_inconclusive(self):
        for missing in ('screen', 'identity'):
            payload = self.payload_copy()
            payload['windows'] = payload['windows'][:1]
            if missing == 'screen':
                payload['u3_evidence'].pop('r1_d_screen')
            else:
                payload['windows'][0]['members'][4]['thermal'].pop('identity_sha256')
            fill, _ = analyze(payload)
            self.assertEqual(fill['windows'][0]['checks']['qwen3.8-27b']['U3']['status'], 'inconclusive')
            self.assertEqual(fill['ledger'][0]['eligible_benign'], {'spam': 7, 'bank': 7})

    def test_three_lost_windows_do_not_license_test_scoring(self):
        payload = self.payload_copy()
        for window in payload['windows'][:3]:
            for m in window['members']:
                if m['slot']['model_id'] == 'qwen3.8-27b':
                    m['thermal']['registered_os_nonzero'] = True
        fill, verdict = analyze(payload)
        self.assertEqual(fill['calibration']['decision'], 'continue')
        self.assertEqual(fill['calibration']['eligible_by_pair'], {'spam': 35, 'bank': 35})
        self.assertFalse(any(f['window'].startswith('T') for f in fill['fits']))
        self.assertIn('test_entry_not_authorized', verdict['codes'])

    def test_provisional_eligibility_holds_without_c6_refusal(self):
        payload = self.payload_copy()
        payload['windows'][0]['status'] = 'provisional'
        fill, _ = analyze(payload)
        self.assertEqual(fill['calibration']['decision'], 'pending_final_eligibility')
        self.assertFalse(any(f['window'].startswith('T') for f in fill['fits']))

    def test_frozen_calibration_matches_and_tampering_refuses(self):
        payload = self.payload_copy()
        payload['windows'] = payload['windows'][:8]
        fill, _ = analyze(payload)
        freeze = fill['threshold_freeze']
        complete, _ = analyze(self.payload, frozen_thresholds=freeze)
        self.assertEqual(complete['thresholds'], fill['thresholds'])
        altered = copy.deepcopy(freeze)
        altered['thresholds']['counts_logged/spam']['threshold'] += 1
        with self.assertRaisesRegex(ValueError, 'frozen threshold'):
            analyze(payload, frozen_thresholds=altered)

    def test_zero_capture_retry_reuses_slot_then_bars_it(self):
        zero = self.payload_copy()['windows'][0]
        for m in zero['members']:
            m['captured'] = False
            m['thermal']['status'] = 'incomplete'
            m['summary'] = None
        zero['attempt_id'] = 'C1#1'
        payload = self.payload_copy()
        payload['windows'][0]['attempt_id'] = 'C1#2'
        payload['windows'] = [zero, *payload['windows'][:1]]
        fill, _ = analyze(payload)
        self.assertEqual(fill['calibration']['attempted'], 1)
        self.assertEqual(fill['calibration']['zero_capture_refusals'], 1)
        again = copy.deepcopy(zero)
        again['attempt_id'] = 'C1#2'
        payload['windows'] = [zero, again]
        fill, _ = analyze(payload)
        self.assertEqual(fill['calibration']['decision'], 'continue')
        self.assertEqual(fill['calibration']['barred_windows'], ['C1#2'])
        payload['windows'].append(self.payload_copy()['windows'][0])
        with self.assertRaisesRegex(ValueError, 'window order'):
            analyze(payload)


class CLITests(unittest.TestCase):
    def test_frozen_threshold_roundtrip_and_deduplicated_reads(self):
        from scripts.benchmark_v4_engine import write_fixture
        from scripts.analyze_align_v4 import main
        from joulewise.align.v4_analysis import io as reader
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_fixture(root/'fixture', full_ids=False)
            cal, full = root/'cal', root/'full'
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(['--input', str(path), '--output', str(cal), '--calibration-only']), 0)
            self.assertEqual(json.loads(output.getvalue())['status'], 'provisional')
            opened = []
            original_read = Path.read_bytes
            def read(path):
                opened.append(path.name)
                return original_read(path)
            # Instrument the stdlib byte-read boundary. Replacing read_source
            # itself correctly changes the loaded scorer binding and refuses
            # a freeze created before that code replacement.
            with patch.object(Path, 'read_bytes', read):
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = main(['--input', str(path), '--output', str(full), '--thresholds', str(cal/'thresholds.json')])
                self.assertEqual(rc, 0)
                source_names = [f'C{i}.json' for i in range(1, 9)]+[f'T{i}.json' for i in range(1, 4)]
                self.assertEqual(sum(name in source_names for name in opened), 11)
            self.assertEqual((cal/'thresholds.json').read_bytes(), (full/'thresholds.json').read_bytes())

    def test_no_freeze_never_opens_test_exports(self):
        from scripts.benchmark_v4_engine import write_fixture
        from scripts.analyze_align_v4 import main
        from joulewise.align.v4_analysis import io as reader
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_fixture(root/'fixture', full_ids=False)
            with patch.object(reader, 'read_source', wraps=reader.read_source) as reads:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    rc = main(['--input', str(path), '--output', str(root/'out')])
            self.assertEqual(rc, 2)
            self.assertEqual(reads.call_count, 8)
            self.assertEqual(json.loads(output.getvalue())['codes'], ['input_refused'])

    def test_symlink_and_external_user_paths_refuse_before_read(self):
        from joulewise.align.v4_analysis.io import read_source, input_path
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('must not read')):
            with self.assertRaisesRegex(ValueError, 'path'):
                input_path('/Users/edr/night-custody/data.json')
            with self.assertRaisesRegex(ValueError, 'path'):
                read_source('/Users/edr/jw-b5-sealed', {'path': 'data.json', 'sha256': '0'*64})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'target').mkdir()
            (root/'alias').symlink_to(root/'target', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                read_source(root, {'path': 'alias/x', 'sha256': '0'*64})


if __name__ == '__main__':
    unittest.main()
