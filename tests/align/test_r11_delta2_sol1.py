"""R11 delta2 Sol1 review witnesses; synthetic bytes only, no native probes.

Receipt/transition Witness tests intentionally fail at f993b784f. Controls
characterize the repaired strict-tier, DC-sealing and stage-adjustment paths.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import km003c, thermal_desk, v4_registration as reg
from joulewise.align.apple import v4_topup as topup
from joulewise.b5 import chain
from tests.align.test_r11_delta_sol1 import TemporaryCandidate
from tests.align.test_thermal_desk import contrast
from tests.align.test_v4_receipt_tiers import amendment
from tests.align.test_v4_topup import obs
from scripts import align_r1_rehearsal as r1, align_v4_w1_synthetic as dry

ROOT = Path(__file__).resolve().parents[2]
NOW = 100000.0


class ReceiptWitnesses(unittest.TestCase):
    def assert_drift_refused(self, relative):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            # Include the unbound dependency in the checkout before the later edit.
            candidate.write(relative, 'synthetic original dependency\n')
            candidate.commit('Synthetic dependency present before drift')
            reg.validate_receipt(candidate.receipt, candidate.root)
            candidate.write(relative, 'synthetic later dependency change\n')
            candidate.commit('Synthetic later clean dependency drift')
            self.assertEqual(candidate.git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg=f'executed dependency drift admitted: {relative}'):
                reg.validate_receipt(candidate.receipt, candidate.root)

    def test_configured_r1_runtime_script_drift_requires_review(self):
        inputs = ROOT / reg.REGISTRATION / 'inputs.json'
        argv = r1.runtime_argv_from_inputs(inputs)   # constructs argv; never launches it
        script = Path(argv[2]).relative_to(ROOT).as_posix()
        self.assertEqual(script, 'scripts/align_r1_runtime.py')
        self.assert_drift_refused(script)

    def test_r1_runtime_config_drift_requires_review(self):
        # This config is read by W1's w1_g0_cap as well as by the R1 runtime.
        self.assert_drift_refused('configs/align/v4/r1_runtime.json')

    def test_current_w1_stage_launch_tools_are_strict(self):
        tree = json.loads((ROOT / 'configs/campaigns/align_v4/plan_tree.json').read_bytes())
        tools = {c['argv_template']['tool_id'] for stage in tree['stage_graph']
                 if stage['kind'] in chain.IN_CHAIN_KINDS for c in stage['launch']['commands']}
        for tool in sorted(tools):
            path = chain.TOOLS[tool].program
            with self.subTest(path=path):
                self.assertIn(path, reg.ARTIFACTS)
                self.assertTrue(reg.is_strict(path), f'current W1 launch tool is amendable: {path}')

    def test_signed_amendment_cannot_waive_current_w1_fiducial_script_review(self):
        path = chain.TOOLS['fiducial_capture'].program
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            candidate.receipt['amendments'] = [amendment(candidate, path, 'changed fiducial capture\n')]
            with self.assertRaisesRegex(ValueError, 'strict-tier path'):
                reg.validate_receipt(candidate.receipt, candidate.root)


class TopupWitnesses(unittest.TestCase):
    def test_off_ac_during_completion_transition_cannot_be_filtered_away(self):
        # The battery was already full/not charging at -1900 s, outside
        # the 1800 s completion window. Reconnection at -1700 s must not
        # move the observed completion forward to that reconnection time.
        log = [obs(NOW-2000, charging=True, pct=97), obs(NOW-1900, ac=False)]
        log += [obs(NOW-1700+100*i) for i in range(18)]
        result = topup.derive(log, NOW)
        self.assertFalse(result['admissible'], result)

    def test_error_at_completion_observation_cannot_be_filtered_away(self):
        log = [obs(NOW-300, charging=True, pct=97), obs(NOW-200, error=True),
               obs(NOW-100), obs(NOW)]
        result = topup.derive(log, NOW)
        self.assertFalse(result['admissible'], result)


class Controls(unittest.TestCase):
    def test_dense_continuous_float_admits_at_99_percent_and_300_second_boundary(self):
        log = [obs(NOW-3600, charging=True, pct=97)]
        log += [obs(NOW-3300+300*i, pct=99) for i in range(11)]
        result = topup.derive(log, NOW)
        self.assertTrue(result['admissible'], result)
        self.assertEqual(result['basis'], 'continuous_float')
        self.assertFalse(topup.derive(log, NOW+.01)['admissible'])  # last sample now >300 s old

    def test_documented_between_window_sampling_strands_an_already_floating_battery(self):
        # A completed charge followed by an 11-hour measured window with no
        # between-window sampler. A fresh 30-minute log of float cannot repair
        # the gap. This is a passing characterization of the operational issue.
        old = [obs(NOW-42000, charging=True, pct=97), obs(NOW-41900)]
        fresh = [obs(NOW-1800+100*i) for i in range(19)]
        result = topup.derive(old+fresh, NOW)
        self.assertFalse(result['admissible'])
        self.assertIn('gap above', result['reasons'][0])
        self.assertFalse(topup.derive(fresh, NOW)['admissible'])

    def test_every_declared_strict_path_refuses_an_amendment_row(self):
        # Exercise the real row validator for every current strict artifact.
        with tempfile.TemporaryDirectory() as tmp:
            candidate = TemporaryCandidate(Path(tmp))
            for path in reg.ARTIFACTS:
                if reg.is_strict(path):
                    row = dict(path=path, old_sha256=candidate.receipt['artifacts'][path],
                               new_sha256='f'*64, reason='synthetic',
                               lead_signature='lead: synthetic-delta2 2026-11-08')
                    with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'strict-tier path'):
                        reg._amendment_chains({'amendments': [row]}, candidate.receipt['artifacts'])

    def test_dc_seal_removes_all_numeric_effect_fields_for_unknown_and_sabotage_conditions(self):
        secret = 987654.321
        hidden = dict(status='available', flags=[], dc_in_energy_j=secret, dc_in_residual_j=secret,
                      score=secret, turn_rows=[dict(energy_j=secret)])
        report = dict(members={'s': hidden, 'unknown': deepcopy(hidden), 'b': dict(hidden, dc_in_residual_j=2)})
        sealed = km003c.seal_non_benign(report, [dict(run_id='s', condition='sabotage'),
                                               dict(run_id='b', condition='benign')])
        for run_id in ('s', 'unknown'):
            self.assertNotIn(str(secret), json.dumps(sealed['members'][run_id]))
            self.assertTrue(sealed['members'][run_id]['sealed'])
        self.assertEqual(sealed['members']['b']['dc_in_residual_j'], 2)

    def test_registered_stage_fit_recovers_known_effect_without_point_one_joule_slack(self):
        runs = contrast(effect=12, noise=.1)
        for i, row in enumerate(runs):
            row.update(stage='a' if i < 4 else 'b', admission_slow_c=42 if row['arm']=='S' else 40,
                       g1_wait_s_by_turn=[1, 1])
            row['turn_owned_j'] += (25 if i >= 4 else 0)
        t0 = min(r['start_ns'] for r in runs)
        x = [[1., float(r['template']=='Y'), float(r['arm']=='S'),
              (r['start_ns']-t0)/3.6e12, float(r['stage']=='b')] for r in runs]
        beta, se, df = dry.ols(x, [r['turn_owned_j'] for r in runs])  # independent existing oracle solver
        result = thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)
        self.assertEqual(df, 3)
        self.assertEqual(result['df'], 3)
        self.assertAlmostEqual(result['arm_effect_j'], beta[2], places=8)
        for actual, want in zip(result['ci90_j'], (beta[2]-dry.T90[df]*se[2], beta[2]+dry.T90[df]*se[2])):
            self.assertAlmostEqual(actual, want, places=6)
        self.assertEqual(result['verdict'], 'T CONFIRMED')
        # A stage offset is a nuisance, so changing only it cannot change delta.
        for row in runs:
            if row['stage']=='b':
                row['turn_owned_j'] += 70
        shifted = thermal_desk.deciding_experiment(runs, v4=True, delta_slow_c=2)
        self.assertAlmostEqual(shifted['arm_effect_j'], result['arm_effect_j'], places=8)


if __name__ == '__main__':
    unittest.main()
