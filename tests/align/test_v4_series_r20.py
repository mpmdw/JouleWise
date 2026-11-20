"""Lead ruling R20: the two supplemental escalation sentinels (ordinals 23 and 24).

When a window's U4/U5 is inconclusive, the next window appends two sentinels after the late sentinel
(22) and before the closing reference/scaffold. Both replay the admitted W1:5 trajectory exactly and are
SUPPLEMENTAL diagnostics: U4's W and W-1 df are unchanged, no held-out seed is used, ceiling 62,400 s.
Synthetic only; the frozen manifest bytes are unchanged (the paired seed check is a MATCH).
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.b5.chain import TOOLS
from joulewise.schemas import BenchmarkConfig, CONFIG_SCHEMA_VERSION
from scripts import align_v4_kit as w1, align_v4_series as s, align_v4_session as session
from tests.align.test_v4_kit import ROOT
from tests.git_fixture import init_git_fixture


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


class C1FilledPlanSizingTests(unittest.TestCase):
    """Rehearse C1 materialization and filled-W1 sizing in an invented repo."""

    pending_flag = 'sizing.planning_allowances_pending_r1_w1_plan'

    def setUp(self):
        tmp = TemporaryDirectory(prefix='synthetic-c1-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.directory = self.root / s.kit_path('C1')
        init_git_fixture(self.root, '-q', '--template=')
        self.seed_materializer()

    def git(self, *args):
        subprocess.run(
            ['git', '-C', str(self.root), '-c', 'user.name=Synthetic',
             '-c', 'user.email=synthetic@example.invalid', '-c', 'commit.gpgSign=false',
             '-c', 'tag.gpgSign=false', '-c', f'core.hooksPath={self.root / ".git/no-hooks"}',
             *args],
            check=True, capture_output=True,
        )

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def seed_materializer(self):
        layout = [
            ('reservation', 'bracket_reservation', 'bracket_reserver', ['fixture']),
            ('pre', 'calibration_capture', 'fiducial_capture', ['--slot', 'pre']),
            ('episodes-a', 'campaign_collection', 'campaign_runner', ['fixture']),
            ('episodes-b', 'campaign_collection', 'campaign_runner', ['fixture']),
            ('derive', 'bound_derivation', 'campaign_runner', ['fixture']),
            ('post', 'calibration_capture', 'fiducial_capture', ['--slot', 'post']),
        ]
        stage_ids = ['align-pilot-v3-' + suffix for suffix, *_ in layout]
        graph = []
        for index, (_, kind, tool, args) in enumerate(layout):
            stage_id = stage_ids[index]
            graph.append(dict(
                stage_id=stage_id, kind=kind, ordinal=index + 1, expected_count=1,
                predecessor=stage_ids[index - 1] if index else None,
                successor=stage_ids[index + 1] if index + 1 < len(stage_ids) else None,
                launch=dict(schema_version='joulewise.stage_launch.v1', commands=[dict(
                    command_id=stage_id, cwd=dict(kind='binding', value='repo_root'), success_exit_codes=[0],
                    argv_template=dict(tool_id=tool, interface_id=TOOLS[tool].interface_id,
                                       arguments=[dict(kind='literal', value=arg) for arg in args]))]),
            ))
        self.write(w1.SOURCE_KIT / 'plan_tree.json', s.raw_json({'stage_graph': graph}))
        for half, indices in (('a', (1, 2, 3, 4)), ('b', (18, 25))):
            for index in indices:
                run_id = f'align-pilot-v3-episodes-{half}-e{index:02}'
                config = BenchmarkConfig.from_mapping(dict(
                    schema_version=CONFIG_SCHEMA_VERSION, run_id=run_id,
                    model=dict(name='synthetic-anchor'), quantization=dict(name='fixture'),
                    hardware_target=dict(id='fixture', transport='local', runtime_backend='mock',
                                         telemetry_backend='mock'),
                    workload_profile=dict(name='fixture', prompt_text=json.dumps(
                        dict(max_turns=12, task_kwargs={}))),
                ))
                path = w1.SOURCE_KIT / 'stages' / f'episodes-{half}' / f'{run_id}.json'
                self.write(path, w1.bundle_config_bytes(config))
        registration = w1.SOURCE_KIT / 'registration'
        self.write(registration / 'identity_pins.json', s.raw_json(
            dict(units=dict(neg8_reference={}, mock={}), runtime_versions={})))
        self.write(registration / 'model_artifact_inventory.json', s.raw_json(
            dict(artifacts=dict(neg8_reference={}, mock={}))))
        self.write(registration / 'sizing_b5.json', s.raw_json({'packs': {'align-pilot-v3': dict(
            disk_member_law=dict(intercept=1, slope=1, largest_positive_residual=0),
            disk_derivation=dict(scaffold_bytes=1))}}))
        self.git('add', '--', str(w1.SOURCE_KIT))
        self.git('commit', '-qm', 'Invented C1 scaffold and disk law')
        for pin in (w1.ANCHOR_COMMIT, w1.CONTRAST_COMMIT):
            self.git('tag', pin)

        sensors = dict(s_fast='T001', s_slow='T002', fan_keys=[], r0_sha256='1' * 64, record_keys=['T002'])
        self.write(Path('configs/align/v4/r1_runtime.json'), s.raw_json(
            dict(sensors=sensors, r0_picks=dict(s_slow='T002'))))
        self.write(w1.R1_SLOTS, s.raw_json(dict(ac_powermode=0)))
        self.write(w1.INPUTS, s.raw_json(dict(
            R0=dict(reasoning_effort=None), R1=dict(B_D=None, T_dead=None, thermal_policy=None),
            WP11=dict(identity_unit=dict(model_source='fixture'), artifact_inventory={}, local_file_verification=None),
            WP15=dict(runtime_entrypoint=None), WP18=dict(X=dict(max_turns=12), Y=dict(max_turns=12)),
        )))
        (self.root / s.MANIFEST).parent.mkdir(parents=True, exist_ok=True)
        self.assertEqual(s.main(['candidate', '--out', str(self.root / s.MANIFEST)]), 0)

    def materialize(self, extra_sentinels=0, *, check=False):
        argv = ['materialize', '--window-id', 'C1', '--extra-sentinels', str(extra_sentinels),
                '--root', str(self.root)]
        if check:
            argv.append('--check')
        self.assertEqual(s.main(argv), 0)

    def read_kit(self, path):
        return json.loads((self.directory / path).read_bytes())

    def write_w1_plan(self, d_max):
        anchors = [dict(role='anchor', ordinal=i, member_s=value)
                   for i, value in enumerate((100, 110, 120, 130), 1)]
        # Put the larger D row first so selecting the last row cannot pass.
        rows = anchors + [dict(role='D', ordinal=5, member_s=d_max),
                          dict(role='D', ordinal=6, member_s=400)]
        raw = (json.dumps({'align_v4': {'members': rows}}, indent=2) + '\n').encode('utf-8')
        self.write(w1.W1_PLAN, raw)
        return raw

    def derive_from_kit(self):
        window = s.selected(s.load(self.root), 'C1')
        plan = self.read_kit('collection_plan.json')
        tree = self.read_kit('plan_tree.json')
        return s.derive_sizing(self.root, window, tree, plan, extra_sentinels=plan.get('extra_sentinels', 0))

    def test_materialize_replays_w1_five_and_refuses_byte_drift(self):
        manifest = (self.root / s.MANIFEST).read_bytes()
        self.materialize()
        ordinary = self.read_kit('collection_plan.json')
        self.materialize(2)
        self.materialize(2, check=True)

        plan = self.read_kit('collection_plan.json')
        members = plan['members']
        self.assertEqual([m['ordinal'] for m in members], list(range(1, 25)))
        self.assertEqual(members[:22], ordinary['members'])
        self.assertEqual((self.root / s.MANIFEST).read_bytes(), manifest)
        self.assertEqual(plan['midpoint_after_ordinal'], 11)
        tree = self.read_kit('plan_tree.json')
        stages = [stage for stage in tree['stage_graph'] if stage['kind'] == 'campaign_collection']
        self.assertEqual([stage['expected_count'] for stage in stages], [11, 13])
        self.assertEqual([row['run_id'] for row in tree['science']], [m['run_id'] for m in members])
        self.assertEqual([m['ordinal'] for m in members if m['pool_role'] == 'anchor'], [1, 2, 3, 4])
        sentinels = [m for m in members if m['pool_role'] == 'sentinel']
        self.assertEqual([m['ordinal'] for m in sentinels], [5, 22, 23, 24])
        fresh = [m for m in members if m['held_out']]
        self.assertEqual([m['ordinal'] for m in fresh], list(range(6, 22)))
        for pair, instructed_ordinal in (('spam_filter_update', 6), ('bank_transfer_2', 11)):
            with self.subTest(pair=pair):
                pair_members = [m for m in fresh if m['task_pair'] == pair]
                self.assertEqual(Counter(m['condition'] for m in pair_members), {'benign': 7, 'sabotage': 1})
                self.assertEqual([m['ordinal'] for m in pair_members if m['condition'] == 'sabotage'],
                                 [instructed_ordinal])

        w1_five = stage_members(w1.build_files(self.root), w1.KIT)[1][4]
        for index, member in enumerate(sentinels[2:], 1):
            with self.subTest(ordinal=member['ordinal']):
                self.assertIs(member['supplemental'], True)
                self.assertIs(member['held_out'], False)
                self.assertEqual(member['escalation_sentinel'], index)
                self.assertEqual(member['counts_toward'], 'none')
                self.assertEqual(member['replay_of'], sentinels[0]['run_id'])
                for key in ('model_id', 'task_pair', 'condition', 'seed_index',
                            'expected_episode_seed', 'expected_turn_seed_0'):
                    self.assertEqual(member[key], w1_five[key], key)
                self.assertEqual(member['spec'], sentinels[1]['spec'])

        path = self.directory / 'registration/sizing_b5.json'
        raw = path.read_bytes()
        drifted = bytes([raw[0] ^ 1]) + raw[1:]
        path.write_bytes(drifted)
        with self.assertRaisesRegex(ValueError, r'series kit drifted: .*registration/sizing_b5\.json'):
            self.materialize(2, check=True)
        self.assertEqual(path.read_bytes(), drifted)

    def assert_filled_sizing(self, sizing, raw, d_max, member_count, ceiling):
        self.assertEqual(sizing['sources']['w1_plan_sha256'], hashlib.sha256(raw).hexdigest())
        pack = sizing['packs'][s.pack_id('C1')]
        self.assertNotIn(self.pending_flag, pack['flags'])
        self.assertEqual(pack['align_members'], member_count)
        expected_seconds = {'1': 100, '2': 110, '3': 120, '4': 130}
        expected_seconds.update({str(i): d_max for i in range(5, member_count + 1)})
        self.assertEqual(pack['member_seconds'], expected_seconds)
        self.assertEqual(pack['T_stream_max_s'], d_max)
        self.assertEqual(pack['disk_member_law'], dict(intercept=1, slope=1, largest_positive_residual=0))
        upper = {ordinal: math.ceil(1 + seconds) for ordinal, seconds in expected_seconds.items()}
        self.assertEqual(pack['member_upper_bytes'], upper)
        self.assertEqual(pack['estimated_footprint_bytes'], 2 * (sum(upper.values()) + 1))
        self.assertEqual(pack['window_ceiling_s'], ceiling)
        self.assertLessEqual(pack['window_max_s'], ceiling)
        return pack

    def test_filled_plan_binds_exact_bytes_and_recomputes_member_disk_and_window_bounds(self):
        self.materialize()
        raw = self.write_w1_plan(600)
        ordinary = self.derive_from_kit()
        self.assert_filled_sizing(ordinary, raw, 600, 22, 59520)

        (self.root / w1.W1_PLAN).unlink()
        self.materialize(2)
        self.write_w1_plan(600)
        escalated = self.derive_from_kit()
        before = self.assert_filled_sizing(escalated, raw, 600, 24, 62400)
        self.assertEqual(s.raw_json(self.derive_from_kit()), s.raw_json(escalated))

        changed_raw = self.write_w1_plan(700)
        changed = self.derive_from_kit()
        after = self.assert_filled_sizing(changed, changed_raw, 700, 24, 62400)
        self.assertNotEqual(changed['sources']['w1_plan_sha256'], escalated['sources']['w1_plan_sha256'])
        self.assertGreater(after['window_max_s'], before['window_max_s'])
        self.assertGreater(after['estimated_footprint_bytes'], before['estimated_footprint_bytes'])

    def test_missing_plan_uses_pending_allowances_and_member_over_cap_refuses(self):
        self.assertFalse((self.root / w1.W1_PLAN).exists())
        self.materialize(2)
        pending = self.read_kit('registration/sizing_b5.json')
        self.assertIsNone(pending['sources']['w1_plan_sha256'])
        pack = pending['packs'][s.pack_id('C1')]
        self.assertEqual(pack['flags'], [self.pending_flag])
        self.assertEqual(pack['member_seconds'], {
            str(i): 3131.27 / 4 if i <= 4 else 1800 for i in range(1, 25)
        })

        self.write_w1_plan(1801)
        with self.assertRaisesRegex(ValueError, 'a member exceeds 1,800 s'):
            self.derive_from_kit()


if __name__ == '__main__':
    unittest.main()
