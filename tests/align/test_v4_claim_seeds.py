"""Synthetic Option-B placement and independent-check mutation witnesses."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import align_v4_series as series
from scripts.check_align_v4_claim_seeds import check


ROOT = Path(__file__).resolve().parents[2]


class ClaimSeedTests(unittest.TestCase):
    def setUp(self):
        self.manifest = series.candidate()

    def test_all_436_members_and_four_disjoint_seed_ranges(self):
        result = check(self.manifest)
        self.assertEqual(result['members_checked'], 436)
        self.assertEqual(result['status'], 'MATCH')
        self.assertEqual(result['index_ranges'], dict(calibration=[2, 65], test=[66, 89],
                         calibration_reserve=[100, 147], test_reserve=[200, 215]))
        self.assertEqual((ROOT / series.MANIFEST).read_bytes(), series.raw_json(self.manifest))

    def test_nonconstant_placement_is_reproducible_and_spans_both_halves(self):
        result = check(self.manifest)
        self.assertGreater(len({tuple(v) for v in result['placements'].values()}), 2)
        self.assertEqual(self.manifest, series.candidate())
        for window in self.manifest['windows'][1:]:
            fresh = window['members'][5:21]
            for pair in series.PAIRS:
                self.assertEqual(sum(r['pair'] == pair and r['condition'] == 'benign' for r in fresh), 7)
                self.assertEqual(sum(r['pair'] == pair and r['condition'] == 'sabotage' for r in fresh), 1)

    def test_materialized_configs_use_randomized_conditions_without_changing_episode_seeds(self):
        import json
        for name in ('C1', 'T2'):
            with self.subTest(window=name):
                files = series.build_files(ROOT, self.manifest, name)
                collection = json.loads(files[series.kit_path(name) / 'collection_plan.json'])
                allocated = series.selected(self.manifest, name)['members']
                for member, row in zip(collection['members'][5:21], allocated[5:21], strict=True):
                    config = json.loads(files[Path(member['config_path'])])
                    spec = json.loads(config['workload_profile']['prompt_text'])
                    self.assertEqual(spec['condition'], row['condition'])
                    self.assertEqual(spec['seed'], row['seed_index'])
                    self.assertEqual(member['expected_episode_seed'], row['episode_seed'])
                    self.assertEqual(member['expected_turn_seed_0'], row['turn_seed_0'])
                    self.assertEqual(member['pool_role'], row['pool'])

    def test_checker_rejects_seed_condition_order_and_draw_mutations(self):
        mutations = (
            lambda m: m['windows'][1]['members'][6].update(episode_seed=0),
            lambda m: m['windows'][-1]['members'][20].update(turn_seed_0=0),
            lambda m: m['windows'][1]['members'][6].update(condition='other'),
            lambda m: m['windows'][-1]['members'][6].update(seed_index=2),
            lambda m: m['windows'][1]['sabotage_placement'].update(draw_counter=99),
            lambda m: m['windows'].reverse(),
            lambda m: m['sabotage_order'].update(master_seed=0),
            lambda m: m['windows'][0]['members'][10].update(seed_index=93),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                bad = deepcopy(self.manifest)
                mutate(bad)
                with self.assertRaises(ValueError):
                    check(bad)

    def test_reserve_materialization_cannot_bypass_the_owed_u3_and_scheduler_gate(self):
        for name in ('T4', 'T5'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'round-2'):
                series.build_files(ROOT, self.manifest, name)

    def test_rejected_draw_advances_only_the_order_counter(self):
        import hashlib
        from types import SimpleNamespace
        real_sha256 = hashlib.sha256
        calls = []

        def once_rejected(raw):
            calls.append(raw)
            return SimpleNamespace(digest=lambda: b'\xff' * 32) if len(calls) == 1 else real_sha256(raw)

        with patch.object(series.hashlib, 'sha256', side_effect=once_rejected):
            placement = series.sabotage_placement('C1', series.PAIRS[0])
        self.assertEqual(placement['draw_counter'], 1)
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0].endswith(b',0]'))
        self.assertTrue(calls[1].endswith(b',1]'))

    def test_unchanged_w1_and_seed_consumption_independent_of_condition(self):
        import json
        import subprocess
        old = json.loads(subprocess.run(['git', 'show',
            '9abe6095f98da581e149bfd1fc2bc2d0a582b2a3:' + series.MANIFEST.as_posix()], cwd=ROOT,
            capture_output=True, check=True).stdout)
        self.assertEqual(old['windows'][0], self.manifest['windows'][0])
        for before, after in zip(old['windows'][1:], self.manifest['windows'][1:18], strict=True):
            self.assertEqual(before['id'], after['id'])
            for a, b in zip(before['members'], after['members'], strict=True):
                for key in ('ordinal', 'pair', 'model_id', 'seed_index', 'episode_seed', 'turn_seed_0'):
                    self.assertEqual(a[key], b[key])


if __name__ == '__main__':
    unittest.main()
