"""R11 delta2 Sol2 review witnesses. Synthetic inputs and temporary Git only.

The negative witnesses intentionally remain red at f993b784f for the lead's
repairs. No model, real custody, measurement, host probe, or network is used.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import km003c, thermal_desk
from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple import v4_topup as topup
from scripts import align_v4_w1_synthetic as dry
from tests.align.test_r11_delta_sol1 import TemporaryCandidate
from tests.align.test_thermal_desk import contrast
from tests.align.test_v4_cadence import window
from tests.align.test_v4_topup import NOW, obs

ROOT = Path(__file__).resolve().parents[2]
SIGNATURE = 'lead: synthetic-delta2-sol2 2026-11-08'


class ExecutionBindingWitnesses(unittest.TestCase):
    def assert_unreviewed_drift_refused(self, path):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.write(path, 'synthetic reviewed entry point\n')
            candidate.receipt['commit'] = candidate.commit('Synthetic original entry point')
            if path in candidate.receipt['artifacts']:
                candidate.receipt['artifacts'][path] = candidate.digest(path)
            registration.validate_receipt(candidate.receipt, candidate.root)
            candidate.write(path, 'synthetic later entry point\n')
            candidate.commit('Synthetic clean unreviewed execution change')
            self.assertEqual(candidate.git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg=f'executed bytes remain unbound: {path}'):
                registration.validate_receipt(candidate.receipt, candidate.root)

    def test_configured_r1_runtime_entrypoint_is_receipt_bound(self):
        inputs = json.loads((ROOT / registration.REGISTRATION / 'inputs.json').read_text())
        path = inputs['WP15']['runtime_entrypoint'][0]
        self.assertEqual(path, 'scripts/align_r1_runtime.py')
        # runtime_argv_from_inputs launches precisely this file; no native runtime is run.
        self.assert_unreviewed_drift_refused(path)

    def test_campaign_python_m_entrypoint_is_receipt_bound(self):
        from scripts.run_campaign import command_for
        argv = command_for(Path('synthetic.json'), Path('synthetic-runs'), None)
        self.assertEqual(argv[1:3], ['-m', 'joulewise'])
        self.assert_unreviewed_drift_refused('joulewise/__main__.py')


class StrictLaunchTierWitnesses(unittest.TestCase):
    def test_launched_calibration_scripts_cannot_use_an_amendment(self):
        from joulewise.b5.chain import TOOLS, WINDOW_CALIBRATION_VERDICT_PROGRAM
        paths = [TOOLS['bracket_reserver'].program, TOOLS['fiducial_capture'].program,
                 WINDOW_CALIBRATION_VERDICT_PROGRAM]
        for path in paths:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                candidate = TemporaryCandidate(Path(tmp))
                candidate.write(path, 'synthetic changed calibration implementation\n')
                candidate.commit('Synthetic calibration change')
                candidate.receipt['amendments'] = [{
                    'path': path, 'old_sha256': candidate.receipt['artifacts'][path],
                    'new_sha256': candidate.digest(path), 'reason': 'synthetic fix',
                    'lead_signature': SIGNATURE,
                }]
                with self.assertRaises(ValueError, msg=f'launched calibration spine must be strict: {path}'):
                    registration.validate_receipt(candidate.receipt, candidate.root)

    def test_an_actually_classified_strict_path_always_refuses_amendments(self):
        # Passing control: the amendment validator itself does not override is_strict.
        path = 'scripts/launch_window.py'
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.write(path, 'synthetic changed strict implementation\n')
            candidate.commit('Synthetic strict change')
            candidate.receipt['amendments'] = [{
                'path': path, 'old_sha256': candidate.receipt['artifacts'][path],
                'new_sha256': candidate.digest(path), 'reason': 'synthetic fix',
                'lead_signature': SIGNATURE,
            }]
            with self.assertRaisesRegex(ValueError, 'strict-tier path'):
                registration.validate_receipt(candidate.receipt, candidate.root)


class CalibrationRosterWitnesses(unittest.TestCase):
    def test_two_additional_registered_sentinels_do_not_make_capture_counts_impossible(self):
        # Protocol U4/U5 inconclusive: add two sentinels to remaining windows.
        # R20 (superseding the delta2 reading): they are supplemental, count toward nothing and do not enter
        # the benign calibration pool: still 7/pair and at most 22 counted captures.
        rows = [window(f'C{i}', 7, 7, captured=22) for i in range(1, 9)]
        self.assertEqual(cadence.calibration_stop(rows)['decision'], 'calibration_complete')


class TopupWitnesses(unittest.TestCase):
    def test_unknown_timestamp_row_cannot_disappear_from_continuous_float_evidence(self):
        rows = [obs(NOW-3000, charging=True, pct=97)]
        rows += [obs(NOW-2900+100*i) for i in range(30)]
        rows.insert(12, {'schema': topup.SCHEMA, 'probe_error': True, 'wall_time_s': None})
        self.assertFalse(topup.derive(rows, NOW)['admissible'],
                         'an untimed probe failure cannot establish continuous float')

    def test_recent_completion_basis_does_not_require_the_continuous_float_gap_rule(self):
        # Basis (a) in the protocol: completion within 1800 s; basis (b) is
        # separately the old completion plus continuous <=300 s log gaps.
        rows = [obs(NOW-1300, charging=True, pct=97), obs(NOW-1200), obs(NOW-100)]
        result = topup.derive(rows, NOW)
        self.assertTrue(result['admissible'], result['reasons'])
        self.assertEqual(result['basis'], 'completed_charge')

    def test_old_completion_with_dense_float_and_the_1800_second_boundary(self):
        for age, basis in ((1800, 'completed_charge'), (3600, 'continuous_float')):
            rows = [obs(NOW-age-100, charging=True, pct=97)]
            rows += [obs(NOW-age+100*i, pct=99) for i in range(age//100+1)]
            result = topup.derive(rows, NOW)
            self.assertTrue(result['admissible'], result['reasons'])
            self.assertEqual(result['basis'], basis)


class IndependentControls(unittest.TestCase):
    def test_stage_adjusted_contrast_matches_independent_five_column_ols(self):
        runs = contrast(effect=12, noise=.15)
        for i, row in enumerate(runs):
            stage = int(i >= 4)
            row.update(stage='b' if stage else 'a', admission_slow_c=40 if row['arm']=='G' else 42,
                       g1_wait_s_by_turn=[1, 1] if row['arm']=='G' else [0, 0])
            row['turn_owned_j'] += 7*stage
        result = thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)
        t0 = min(r['start_ns'] for r in runs)
        x = [[1., float(r['template']=='Y'), float(r['arm']=='S'),
              (r['start_ns']-t0)/(3600*1e9), float(r['stage']=='b')] for r in runs]
        coef, se, df = dry.ols(x, [r['turn_owned_j'] for r in runs])
        self.assertEqual(result['df'], 3)
        self.assertEqual(df, 3)
        self.assertAlmostEqual(result['arm_effect_j'], coef[2], places=8)
        half = dry.T90[df]*se[2]
        for actual, expected in zip(result['ci90_j'], (coef[2]-half, coef[2]+half)):
            self.assertAlmostEqual(actual, expected, delta=1e-6)

    def test_dc_sealing_removes_nested_non_benign_values_and_keeps_benign_fit(self):
        secret = 987654.321
        report = {'members': {'b': {'dc_in_residual_j': 4.},
                              's': {'status': 'available', 'flags': [], 'dc_in_residual_j': secret,
                                    'turn_rows': [{'energy_j': secret}]}},
                  'models': [{'training_run_ids': ['b'], 'model': {'coefficient': 4.}}]}
        original = deepcopy(report)
        sealed = km003c.seal_non_benign(report, [{'run_id': 'b', 'condition': 'benign'},
                                               {'run_id': 's', 'condition': 'sabotage'}])
        self.assertNotIn(str(secret), json.dumps(sealed))
        self.assertEqual(sealed['models'], report['models'])
        self.assertEqual(report, original)


if __name__ == '__main__':
    unittest.main()
