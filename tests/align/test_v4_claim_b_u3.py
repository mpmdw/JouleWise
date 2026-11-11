"""Agreement item 17: only registered constants and the manifest roster qualify."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from joulewise.align.apple import v4_u3
from tests.align.v4_registration_fixtures import export
from scripts.align_v4_u3_export import ROSTER


class RegisteredPolicyTests(unittest.TestCase):
    def test_registered_policy_and_manifest_window_order(self):
        policy = export()['policy']
        manifest = json.loads((Path(__file__).resolve().parents[2] /
                               'configs/campaigns/align_v4/series/series_manifest.json').read_bytes())
        self.assertEqual(list(ROSTER), manifest['order'])
        self.assertEqual(policy['checks_by_window'], ROSTER)
        self.assertEqual(v4_u3.policy_checks(policy), {'30B': 4, 'D': 20})

    def test_other_beta_is_not_an_installed_policy(self):
        for beta in (.025, .04, .06, True, float('nan')):
            policy = export()['policy']
            policy['series_alpha'] = beta
            with self.subTest(beta=beta), self.assertRaisesRegex(ValueError, 'registered'):
                v4_u3.policy_checks(policy)

    def test_other_transfer_factor_is_not_an_installed_policy(self):
        for factor in (1., 1.4, 1.6, 2., True, float('inf')):
            policy = export()['policy']
            policy['d_transfer_factor'] = factor
            with self.subTest(factor=factor), self.assertRaisesRegex(ValueError, 'registered'):
                v4_u3.policy_checks(policy)

    def test_missing_extra_and_same_total_changed_rosters_refuse(self):
        policy = export()['policy']
        for change in ('missing', 'extra', 'renamed', 'counts', 'populations'):
            bad = deepcopy(policy)
            roster = bad['checks_by_window']
            if change == 'missing':
                del roster['T5']
            elif change == 'extra':
                roster['T6'] = {'30B': 0, 'D': 1}
            elif change == 'renamed':
                roster['T6'] = roster.pop('T5')
            elif change == 'counts':
                roster['T4']['D'], roster['T5']['D'] = 2, 0
            else:
                roster['C1'] = {'30B': 1, 'D': 0}
            with self.subTest(change=change), self.assertRaises(ValueError):
                v4_u3.policy_checks(bad)


if __name__ == '__main__':
    unittest.main()
