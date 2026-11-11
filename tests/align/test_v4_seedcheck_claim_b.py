"""Option-B seed check (RUN_STATE 251; claim contract B5/B6): the committed manifest against the text.

The checker (docs/align/v4/seedcheck-claim-b-opus/derive_and_check.py) imports nothing from JouleWise or
scripts; it re-derives all 436 members from the registered text. These tests run it on the committed bytes,
cross-check it against the generator's placement law, prove it catches synthetic tampering, and check that a
materialized kit follows the seeded placement. Synthetic only; no v4 data exists.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

from scripts import align_v4_series as series
from tests.align.v4_option_b import OPTION_B_MANIFEST_SHA256

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / 'docs/align/v4/seedcheck-claim-b-opus/derive_and_check.py'


def _checker():
    spec = importlib.util.spec_from_file_location('seedcheck_claim_b_opus', CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SeedCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.check = _checker()
        cls.raw = (ROOT / series.MANIFEST).read_bytes()
        cls.manifest = json.loads(cls.raw)

    def test_committed_manifest_matches_the_text_for_every_member(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), OPTION_B_MANIFEST_SHA256)
        self.assertEqual(self.raw, series.raw_json(series.candidate()))      # the generator's exact output
        diffs, summary = self.check.check(self.manifest)
        self.assertEqual(diffs, [])
        self.assertEqual((summary['windows'], summary['members']), (20, 18 + 19 * 22))
        for pair in series.PAIRS:
            self.assertEqual(summary['ranges'][pair], {'calibration': [2, 65, 64], 'test': [66, 89, 24],
                                                       'calibration_reserve': [100, 147, 48],
                                                       'test_reserve': [148, 163, 16]})

    def test_committed_receipt_records_the_match_on_these_bytes(self):
        receipt = json.loads((CHECKER.parent / 'comparison.json').read_bytes())
        self.assertEqual((receipt['verdict'], receipt['manifest_sha256'], receipt['differences']),
                         ('MATCH', OPTION_B_MANIFEST_SHA256, []))
        self.assertEqual(receipt['members'], 436)

    def test_two_implementations_of_the_placement_law_agree(self):
        for window in self.manifest['windows'][1:]:
            for pair in series.PAIRS:
                self.assertEqual(series.sabotage_slot(window['id'], pair), self.check.slot(window['id'], pair))
            self.assertEqual(series.sabotage_ordinals(window['id']), window['sabotage_ordinals'])
        # the law is the seed law's JSON digest: one hand-computed value pins the encoding
        raw = json.dumps(['align-v4-sabotage-slot-v1', 'C1', 'shade/spam_filter_update'],
                         separators=(',', ':'), ensure_ascii=True).encode()
        self.assertEqual(series.sabotage_slot('C1', 'spam_filter_update'),
                         int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big') % 8)
        for window, pair in (('C3#2', 'spam_filter_update'), ('C3', 'unknown_pair'), ('W1', 'spam_filter_update'),
                             ('C03', 'bank_transfer_2'), ('D3', 'bank_transfer_2')):
            with self.assertRaises(ValueError):
                series.sabotage_slot(window, pair)          # slot ids only: an attempt id never re-draws

    def test_zero_capture_retry_keeps_the_placement_and_w1_is_unchanged(self):
        # a re-arm (C3#2) runs the frozen C3 slot: same window id, so same seeds and placement
        self.assertEqual(series.selected(self.manifest, 'C3')['sabotage_ordinals'], series.sabotage_ordinals('C3'))
        w1 = series.selected(self.manifest, 'W1')
        self.assertNotIn('sabotage_ordinals', w1)
        self.assertEqual([m['ordinal'] for m in w1['members'] if m['condition'] == 'sabotage' and m['role'] == 'D'],
                         [11, 14])

    def test_the_checker_catches_tampering(self):
        def mutated(change):
            value = deepcopy(self.manifest)
            change({w['id']: w for w in value['windows']})
            return self.check.check(value)[0]

        def move_sabotage(ws):                    # swap a pair's sabotage-instructed member with a benign one
            members = ws['C2']['members']
            pair = members[5]['pair']
            fresh = [m for m in members if 6 <= m['ordinal'] <= 21 and m['pair'] == pair]
            sab = next(m for m in fresh if m['condition'] == 'sabotage')
            ben = next(m for m in fresh if m['condition'] == 'benign')
            sab['condition'], ben['condition'] = 'benign', 'sabotage'
            sab['pool'], ben['pool'] = ben['pool'], sab['pool']

        def second_sabotage(ws):
            m = next(m for m in ws['T1']['members'] if 6 <= m['ordinal'] <= 21 and m['condition'] == 'benign')
            m['condition'] = 'sabotage'

        def shift_seed(ws):
            m = ws['C5']['members'][10]
            m['seed_index'] += 1

        def reuse_test_index_in_reserve(ws):      # T4 reuses a T1 index, seeds recomputed consistently
            check = self.check
            t1 = next(m for m in ws['T1']['members'] if m['ordinal'] == 6)
            t4 = next(m for m in ws['T4']['members'] if 6 <= m['ordinal'] <= 21 and m['pair'] == t1['pair'])
            t4['seed_index'] = t1['seed_index']
            t4['episode_seed'] = check.episode_seed(t4['model_id'], t4['pair'], t4['seed_index'])
            t4['turn_seed_0'] = check.turn_seed_0(t4['episode_seed'])

        def forge_episode_seed(ws):
            ws['C9']['members'][12]['episode_seed'] ^= 1

        def wrong_placement_record(ws):
            ws['T5']['sabotage_ordinals'] = {p: o + 2 for p, o in ws['T5']['sabotage_ordinals'].items()}

        for change, expect in ((move_sabotage, 'condition'), (second_sabotage, 'sabotage-instructed members'),
                               (shift_seed, 'seed_index'), (reuse_test_index_in_reserve, 'share indices'),
                               (forge_episode_seed, 'seed law'), (wrong_placement_record, 'sabotage_ordinals')):
            with self.subTest(change.__name__):
                diffs = mutated(change)
                self.assertTrue(any(expect in d for d in diffs), diffs[:5])
        # a dropped test reserve is an order/window mismatch, not a silent pass
        value = deepcopy(self.manifest)
        value['windows'] = [w for w in value['windows'] if w['id'] != 'T5']
        value['order'] = [w for w in value['order'] if w != 'T5']
        self.assertTrue(self.check.check(value)[0])


class KitFollowsPlacementTests(unittest.TestCase):
    def test_materialized_configs_carry_the_seeded_condition_and_seed(self):
        manifest = series.load(ROOT)
        for name in ('C1', 'T4'):                      # a primary calibration window and a test reserve
            with self.subTest(name):
                window = series.selected(manifest, name)
                files = series.build_files(ROOT, manifest, name)
                plan = json.loads(files[series.kit_path(name) / 'collection_plan.json'])
                by_ordinal = {m['ordinal']: m for m in window['members']}
                for member in plan['members']:
                    want = by_ordinal[member['ordinal']]
                    self.assertEqual((member['condition'], member['seed_index'], member['task_pair'],
                                      member['expected_episode_seed']),
                                     (want['condition'], want['seed_index'], want['pair'], want['episode_seed']))
                    if member['ordinal'] > 4:
                        spec = member['spec']
                        self.assertEqual((spec['condition'], spec['seed'], spec['task_kwargs']['task_pair']),
                                         (want['condition'], want['seed_index'], want['pair']))
                    if 6 <= member['ordinal'] <= 21 and want['condition'] == 'sabotage':
                        self.assertEqual(member['counts_toward'], 'claim_s' if name.startswith('C') else 'test')


if __name__ == '__main__':
    unittest.main()
