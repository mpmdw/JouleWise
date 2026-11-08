"""Lead ruling R20: the two supplemental escalation sentinels (ordinals 23 and 24).

When a window's U4/U5 is inconclusive, the next window appends two sentinels after the late sentinel
(22) and before the closing reference/scaffold. Both replay the admitted W1:5 trajectory exactly and are
SUPPLEMENTAL diagnostics: U4's W and W-1 df are unchanged, no held-out seed is used, ceiling 62,400 s.
Synthetic only; the frozen manifest bytes are unchanged (the paired seed check is a MATCH).
"""
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as w1, align_v4_series as s, align_v4_session as session
from tests.align.test_v4_kit import ROOT


def stage_members(files, directory):
    plan = json.loads(files[Path(directory) / 'collection_plan.json'])
    return plan, plan['members']


class EscalationSentinelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = s.load(ROOT)
        cls.base = s.build_files(ROOT, cls.manifest, 'C3')
        cls.esc = s.build_files(ROOT, cls.manifest, 'C3', extra_sentinels=2)
        cls.directory = s.kit_path('C3')
        cls.base_plan, cls.base_members = stage_members(cls.base, cls.directory)
        cls.plan, cls.members = stage_members(cls.esc, cls.directory)

    def test_two_members_follow_the_late_sentinel_and_the_first_22_are_unchanged(self):
        self.assertEqual((len(self.base_members), len(self.members)), (22, 24))
        self.assertEqual([m['ordinal'] for m in self.members], list(range(1, 25)))
        self.assertEqual(self.members[:22], self.base_members)       # nothing before 23 moves
        self.assertEqual(self.plan['extra_sentinels'], 2)
        self.assertNotIn('extra_sentinels', self.base_plan)
        # the manifest itself is untouched: the paired seed check (MATCH) stays valid
        self.assertEqual((ROOT / s.MANIFEST).read_bytes(), s.raw_json(s.candidate()))
        self.assertEqual(len(self.manifest['windows'][3]['members']), 22)

    def test_they_replay_the_w1_5_trajectory_exactly_with_no_held_out_seed(self):
        five, late = self.members[4], self.members[21]
        for k, member in enumerate(self.members[22:], 1):
            with self.subTest(escalation_sentinel=k):
                self.assertEqual(member['escalation_sentinel'], k)
                self.assertEqual(member['pool_role'], 'sentinel')
                self.assertIs(member['supplemental'], True)
                self.assertEqual(member['counts_toward'], 'none')
                self.assertIs(member['held_out'], False)
                self.assertEqual(member['replay_of'], five['run_id'])
                self.assertEqual(member['repeat'], 2 + k)
                for key in ('model_id', 'task_pair', 'condition', 'seed_index', 'expected_episode_seed',
                            'expected_turn_seed_0', 'block', 'role', 'ac_powermode', 'stage_id'):
                    self.assertEqual(member[key], late[key], key)
                    if key != 'stage_id':
                        self.assertEqual(member[key], five[key], key)
                self.assertEqual((member['condition'], member['seed_index']), ('benign', 1))
                # the same D model template: sampler, budgets, cache policy and stack are inherited
                cfg = json.loads(self.esc[Path(member['config_path'])])
                src = json.loads(self.esc[Path(late['config_path'])])
                spec, src_spec = (json.loads(c['workload_profile']['prompt_text']) for c in (cfg, src))
                self.assertEqual(spec, src_spec)
                for c in (cfg, src):
                    c['run_id'] = 'x'
                    c['run_metadata'] = {k2: v for k2, v in c['run_metadata'].items() if k2 != 'tags'}
                    c['workload_profile'] = {k2: v for k2, v in c['workload_profile'].items() if k2 != 'prompt_text'}
                self.assertEqual(cfg, src)
        held_out = lambda members: sorted(m['seed_index'] for m in members if m['ordinal'] >= 6 and m['ordinal'] <= 21)
        self.assertEqual(held_out(self.members), held_out(self.base_members))     # no held-out seed used

    def test_stage_order_places_them_after_22_and_before_the_closing_scaffold(self):
        tree = json.loads(self.esc[self.directory / 'plan_tree.json'])
        base_tree = json.loads(self.base[self.directory / 'plan_tree.json'])
        second = [r for r in tree['science'] if r['stage_id'] == tree['science'][-1]['stage_id']]
        ids = [r['run_id'] for r in second]
        self.assertEqual(ids[-3:], [m['run_id'] for m in self.members[21:24]])        # 22, 23, 24 are the last D rows
        base_second = [r for r in base_tree['science'] if r['stage_id'] == base_tree['science'][-1]['stage_id']]
        self.assertEqual(len(second), len(base_second) + 2)
        # the closing reference/scaffold stages follow the science stage in the graph
        kinds = [st['kind'] for st in tree['stage_graph']]
        self.assertEqual(kinds, [st['kind'] for st in base_tree['stage_graph']])
        manifests = {p: json.loads(raw) for p, raw in self.esc.items() if p.name == 'order_manifest.json'}
        counts = sorted(m['planned_n_bundles'] for m in manifests.values())
        base_counts = sorted(json.loads(raw)['planned_n_bundles'] for p, raw in self.base.items()
                             if p.name == 'order_manifest.json')
        self.assertEqual(counts[0], base_counts[0])
        self.assertEqual(counts[-1], base_counts[-1] + 2)

    def test_ceiling_is_62400_and_an_ordinary_window_cannot_carry_them(self):
        sizing = json.loads(self.esc[self.directory / 'registration/sizing_b5.json'])
        pack = sizing['packs'][self.plan['plan_id']]
        self.assertEqual(pack['window_ceiling_s'], 62400)
        self.assertLessEqual(pack['window_max_s'], 62400)
        self.assertGreater(pack['window_max_s'], s.window_ceiling_s())     # only fits under the R15 ceiling
        self.assertEqual(pack['align_members'], 24)
        base_pack = json.loads(self.base[self.directory / 'registration/sizing_b5.json'])['packs'][self.base_plan['plan_id']]
        self.assertEqual(base_pack['window_ceiling_s'], 59520)
        with self.assertRaisesRegex(ValueError, 'exceeds the 59520 s ceiling'):
            s.derive_sizing(ROOT, self.manifest['windows'][3], json.loads(self.esc[self.directory / 'plan_tree.json']),
                            self.plan, extra_sentinels=0)

    def test_only_zero_or_two_and_never_in_w1(self):
        with self.assertRaisesRegex(ValueError, '0 or 2'):
            s.build_files(ROOT, self.manifest, 'C3', extra_sentinels=1)
        with self.assertRaisesRegex(ValueError, 'not evaluable in W1'):
            s.build_files(ROOT, self.manifest, 'W1', extra_sentinels=2)
        with patch.object(session, 'session_start_restore', return_value={'action': 'none'}), \
                patch.object(session.kit, 'generate'):
            for window in (None, 'W1'):
                with self.assertRaisesRegex(ValueError, 'escalation sentinels'):
                    session.prepare(ROOT, ROOT / 'unused-session', window_id=window, extra_sentinels=2)
            with self.assertRaisesRegex(ValueError, 'escalation sentinels'):
                session.prepare(ROOT, ROOT / 'unused-session', window_id='C3', extra_sentinels=3)


class MaterializedEscalationSentinelTests(unittest.TestCase):
    """The two escalation sentinels survive a real on-disk materialization (write, then read back)."""

    @classmethod
    def setUpClass(cls):
        import hashlib
        import tempfile
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        manifest = s.load(ROOT)
        cls.files = s.build_files(ROOT, manifest, 'C5', extra_sentinels=2)
        for path, raw in cls.files.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        cls.root, cls.sha = root, hashlib.sha256
        cls.directory = s.kit_path('C5')
        cls.plan = json.loads((root / cls.directory / 'collection_plan.json').read_bytes())
        cls.members = {m['ordinal']: m for m in cls.plan['members']}

    def config(self, ordinal):
        return json.loads((self.root / self.members[ordinal]['config_path']).read_bytes())

    def test_both_are_supplemental_count_toward_nothing_and_are_flagged_in_the_plan_on_disk(self):
        self.assertEqual(sorted(self.members), list(range(1, 25)))
        self.assertEqual(self.plan['extra_sentinels'], 2)
        for ordinal in (23, 24):
            member = self.members[ordinal]
            self.assertIs(member['supplemental'], True)
            self.assertEqual(member['escalation_sentinel'], ordinal - 22)
            self.assertEqual((member['pool_role'], member['counts_toward']), ('sentinel', 'none'))
            self.assertIs(member['held_out'], False)
            self.assertEqual(member['replay_of'], self.members[5]['run_id'])
        for ordinal in range(1, 23):
            self.assertNotIn('supplemental', self.members[ordinal])             # the ordinary 22 are not supplemental
        self.assertEqual(sum(m.get('counts_toward') == 'calibration' for m in self.plan['members']), 14)

    def test_each_is_its_own_batch_1_member_with_the_normal_idle_and_thermal_gates(self):
        late = self.config(22)
        seen = set()
        for ordinal in (23, 24):
            member, config = self.members[ordinal], self.config(ordinal)
            self.assertNotIn(member['run_id'], seen | {self.members[o]['run_id'] for o in range(1, 23)})
            seen.add(member['run_id'])
            self.assertEqual(config['run_id'], member['run_id'])                  # a separate one-episode bundle
            self.assertEqual(self.sha(( self.root / member['config_path']).read_bytes()).hexdigest(),
                             member['config_sha256'])
            self.assertEqual(config['sampling'], late['sampling'])                # the normal idle (300 s), warmup, power rate
            spec, late_spec = (json.loads(c['workload_profile']['prompt_text']) for c in (config, late))
            self.assertEqual(spec, late_spec)                                     # same thermal gates, caps, seed, cache policy
            self.assertEqual((spec['thermal']['heavy'], spec['thermal']['per_turn']), (True, True))
            self.assertEqual(spec['thermal']['window_reference']['role'], 'consume')
            self.assertEqual(spec['seed'], 1)
        rows = {}
        for path in (self.root / self.directory / 'stages').rglob('order_manifest.json'):
            for row in json.loads(path.read_bytes())['executed_order']:
                rows.setdefault(row['run_id'], []).append(row)
        for ordinal in (23, 24):
            run_id = self.members[ordinal]['run_id']
            self.assertEqual(len(rows[run_id]), 1)                                # exactly one batch entry each
            self.assertEqual(rows[run_id][0]['rep'], ordinal - 20)
        ids_b = [r['run_id'] for path in (self.root / self.directory / 'stages' / 'episodes-b').rglob('order_manifest.json')
                 for r in json.loads(path.read_bytes())['executed_order']]
        self.assertEqual(ids_b[-3:], [self.members[o]['run_id'] for o in (22, 23, 24)])   # after the late sentinel

    def test_the_manifest_the_windows_are_derived_from_is_unchanged_by_materialization(self):
        self.assertEqual((ROOT / s.MANIFEST).read_bytes(), s.raw_json(s.candidate()))
        self.assertEqual(len(s.selected(s.load(ROOT), 'C5')['members']), 22)


class DeskTests(unittest.TestCase):
    def test_supplemental_members_join_no_identical_work_group_and_are_reported_descriptively(self):
        regular = {}
        session.assign_work_group(regular, {'ordinal': 22, 'run_id': 'c-e22', 'replay_of': 'c-e05', 'role': 'D'})
        self.assertEqual(regular['identical_work_group'], 'c-e05')                # the late sentinel pairs with 5
        supplemental = {}
        session.assign_work_group(supplemental, {'ordinal': 23, 'run_id': 'c-e23', 'replay_of': 'c-e05', 'role': 'D',
                                                 'supplemental': True, 'escalation_sentinel': 1})
        self.assertNotIn('identical_work_group', supplemental)                     # U3 scope and U4 df unchanged
        self.assertTrue(supplemental['supplemental'])
        records = [{'id': 'c-e05', 'tokens': [1, 2], 'gross_episode_j': 100.0},
                   {'id': 'c-e23', 'tokens': [1, 2], 'gross_episode_j': 101.0, 'supplemental': True,
                    'escalation_sentinel': 1, 'replay_of': 'c-e05'},
                   {'id': 'c-e24', 'tokens': [1, 3], 'gross_episode_j': 99.0, 'supplemental': True,
                    'escalation_sentinel': 2, 'replay_of': 'c-e05', 'excluded': True}]
        report = session.supplemental_report(records)
        self.assertEqual(report['status'], 'descriptive_only')
        self.assertEqual([m['tokens_identical_to_replay_of'] for m in report['members']], [True, False])
        self.assertEqual(report['members'][0]['replay_of_gross_episode_j'], 100.0)
        self.assertTrue(report['members'][1]['excluded'])
        self.assertIsNone(session.supplemental_report(records[:1]))

    def test_supplemental_members_never_count_as_captured_window_members(self):
        manifest = s.load(ROOT)
        pack = s.pack_id('C3')
        window = s.selected(manifest, 'C3')
        rows = [{'run_id': f'{pack}-e{o:02}', 'captured': True, 'excluded': False} for o in range(5, 25)]
        rows += [{'run_id': f'anchor-{i}', 'captured': True, 'excluded': False} for i in range(4)]
        row = s.desk_row(manifest, 'C3', rows, True)
        self.assertEqual(row['captured_members'], 22)                              # 24 captured, 2 supplemental
        self.assertEqual(sum(row['desk_eligible_benign'].values()), 14)
        self.assertEqual(len(window['members']), 22)


if __name__ == '__main__':
    unittest.main()
