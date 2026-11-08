"""Failing-first R11 review witnesses; synthetic inputs only, no native probes.

These assertions describe the adopted contract, not the current defects.
Product repairs and scientific choices belong to the lead.
"""
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import thermal_desk, v4_estimands, v4_registration
from tests.align.test_thermal_desk import member


class BatteryCompletionWitness(unittest.TestCase):
    def test_fresh_battery_state_does_not_prove_recent_completed_topup(self):
        observation = dict(passed=True, probe_error=False, external_connected=True,
                           is_charging=False, update_age_s=1,
                           current_capacity_pct=99, instant_amperage_ma=0)
        # There is no completion time/evidence at all. UpdateTime dates the
        # current observation, not the charging transition (protocol 4).
        self.assertFalse(v4_registration.battery_arm(observation, 'synthetic OBC attestor')['admitted'])


class U6DeskWitnesses(unittest.TestCase):
    def v4_u6(self, per_episode):
        benign = [dict(pair=pair, start_ns=i, residual_j=per_episode(i),
                       trajectory=f'{pair}-{i}')
                  for pair in ('spam', 'bank') for i in range(6)]
        part = dict(session_id='D1', u6_inputs={'synthetic': dict(
            benign=benign, mean_turn_j=100, mean_30b_turn_j=100,
            mean_episode_j=3000, split_rule='within_pair_episode_order')})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'PILOT.json'
            path.write_text(json.dumps({'v4_desk_evidence': part}))
            evidence = thermal_desk.session_desk_evidence([path])
        row = member()
        row['window'] = 'D1'
        report = thermal_desk.window_report([row], monitoring=evidence['monitoring'], v4=True)
        return report['model_windows']['synthetic/D1']['U6']

    def test_d_v4_desk_does_not_veto_on_removed_turn_index_slope(self):
        # Identical trajectory distributions in both halves: early/late
        # shift and its clustered SE are exactly zero. Every position has
        # twelve trajectories. Chair 6 removes the D turn-index slope veto.
        result = self.v4_u6(lambda i: [0., 100., 200.])
        self.assertNotEqual(result['status'], 'fail')

    def test_v4_desk_cannot_pass_without_registered_cell_scale(self):
        # No s_r or trajectory-clustered interval input is supplied. The
        # adopted +/-0.5*s_r check cannot pass from mean energy instead.
        # The old .0037 * 3000 = 11.1 J margin silently passes a 6 J shift.
        result = self.v4_u6(lambda i: [0., 0., 0.] if i < 3 else [2., 2., 2.])
        self.assertEqual(result['status'], 'inconclusive')


class HStarDoseWitnesses(unittest.TestCase):
    def test_h_star_does_not_relabel_fractional_actual_dose_as_grid_integer(self):
        with self.assertRaises(ValueError):
            v4_estimands.subturn_h_star([(128.9, 2.)], 1.)

    def test_h_star_does_not_silently_overwrite_duplicate_actual_doses(self):
        with self.assertRaises(ValueError):
            v4_estimands.subturn_h_star([(128, 2.), (128, 0.)], 1.)


if __name__ == '__main__':
    unittest.main()
