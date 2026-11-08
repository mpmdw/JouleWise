"""The committed ALIGN v4 series kit (Opus build): no drift, W1-identical D work, sizing.

Default CI (no opt-in): repository files and synthetic inputs only.
"""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_registration as registration, v4_series as series
from scripts import align_v4_kit as kit, align_v4_series as gen, align_v4_session as session

ROOT = Path(__file__).resolve().parents[2]
VARYING = ('condition', 'seed', 'task_kwargs', 'thermal')


def spec(config_path):
    config = json.loads((ROOT / config_path).read_text())
    return json.loads(config['workload_profile']['prompt_text'])


class CommittedSeriesKitTests(unittest.TestCase):
    def test_committed_series_kit_matches_the_generator(self):
        gen.generate(ROOT, check=True)
        self.assertEqual(gen.read_manifest(ROOT), series.MANIFEST)

    def test_window_kits_follow_the_manifest_and_w1_d_work(self):
        w1 = json.loads((ROOT / kit.KIT / 'collection_plan.json').read_text())
        w1_d = spec(next(m for m in w1['members'] if m['ordinal'] == 5)['config_path'])
        for row in series.MANIFEST['windows'][1:]:
            plan = json.loads((ROOT / row['kit'] / 'collection_plan.json').read_text())
            self.assertEqual((plan['plan_id'], plan['series_window'], plan['series_role']),
                             (row['pack_id'], row['window'], row['role']))
            self.assertEqual(plan['series_manifest_sha256'], series.manifest_sha256(series.MANIFEST))
            kit.check_window_reference_roles(plan)
            for member, frozen in zip(plan['members'], row['members'], strict=True):
                for key in ('ordinal', 'run_id', 'task_pair', 'condition', 'seed_index', 'held_out',
                            'counts_toward', 'expected_episode_seed'):
                    self.assertEqual(member[key], frozen[key], (row['window'], member['ordinal'], key))
                got = spec(member['config_path'])
                if member['series_role'] == 'anchor':
                    w1_anchor = next(m for m in w1['members'] if m['ordinal'] == member['ordinal'])
                    self.assertEqual(member['config_sha256'], w1_anchor['config_sha256'])
                    continue
                # Only pair, condition, seed and the window-reference role may differ from W1's D.
                self.assertEqual({k: v for k, v in got.items() if k not in VARYING},
                                 {k: v for k, v in w1_d.items() if k not in VARYING})
                self.assertEqual((got['condition'], got['seed'], got['task_kwargs']['task_pair']),
                                 (member['condition'], member['seed_index'], member['task_pair']))
                self.assertEqual({k: v for k, v in got['thermal'].items() if k != 'window_reference'},
                                 {k: v for k, v in w1_d['thermal'].items() if k != 'window_reference'})
                if member['series_role'] == 'sentinel':
                    self.assertEqual({k: v for k, v in got.items() if k != 'thermal'},
                                     {k: v for k, v in w1_d.items() if k != 'thermal'})

    def test_registration_binds_the_series(self):
        for path in ('joulewise/align/apple/v4_series.py', 'scripts/align_v4_series.py',
                     'configs/campaigns/align_v4_series/series_manifest.json'):
            self.assertIn(path, registration.ARTIFACTS)


class SeriesSizingTests(unittest.TestCase):
    def test_window_sizing_from_a_w1_plan(self):
        rows = [{'ordinal': i, 'role': 'anchor' if i <= 4 else 'D', 'member_s': 3131.27 / 4 if i <= 4 else 1800}
                for i in range(1, 19)]
        plan = json.loads((ROOT / 'configs/campaigns/align_v4_series/c1/collection_plan.json').read_text())
        tree = json.loads((ROOT / 'configs/campaigns/align_v4_series/c1/plan_tree.json').read_text())
        from scripts import validate_align_v4_w1_plan as validator
        with patch.object(validator, 'validate', return_value={}):
            sized = gen.derive_window_sizing(ROOT, {'align_v4': {'members': rows}}, b'{}', {'R1': {'B_D': 8192}},
                                             {}, tree, plan)
        pack = sized['packs']['align-v4-c1']
        self.assertEqual((pack['programmed_span_s'], pack['window_max_s'], pack['align_members']), (40527, 58260, 22))
        rows[5]['member_s'] = 1900
        with patch.object(validator, 'validate', return_value={}), self.assertRaisesRegex(ValueError, 'return to lead'):
            gen.derive_window_sizing(ROOT, {'align_v4': {'members': rows}}, b'{}', {'R1': {'B_D': 8192}}, {}, tree, plan)

    def test_prepare_refuses_a_series_window_until_r1_fills_the_w1_plan(self):
        with patch.object(kit, 'generate'), self.assertRaisesRegex(ValueError, 'BLOCKED.*sizing_b5.json'):
            gen.require_window_ready(ROOT, 'C1')
        with self.assertRaisesRegex(ValueError, 'W1 arms through the W1 kit'):
            gen.require_window_ready(ROOT, 'W1')


class SessionCliTests(unittest.TestCase):
    def test_prepare_window_flag_reaches_the_session(self):
        with patch.object(session, 'prepare') as prepare:
            self.assertEqual(session.main(['prepare', '--measurement-root', 'm', '--session-root', 's',
                                           '--window', 'D2']), 0)
        self.assertEqual(prepare.call_args.kwargs['window'], 'D2')
        with patch.object(session, 'prepare') as prepare:
            session.main(['prepare', '--measurement-root', 'm', '--session-root', 's'])
        self.assertIsNone(prepare.call_args.kwargs['window'])


if __name__ == '__main__':
    unittest.main()
