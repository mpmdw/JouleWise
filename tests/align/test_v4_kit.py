"""WP16 acceptance on pinned repo configs and synthetic inputs; no study data."""
from collections import Counter
from contextlib import redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple.workload import EpisodeSpec
from joulewise.b5 import chain
from joulewise.schemas import BenchmarkConfig
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_session as session

ROOT = Path(__file__).resolve().parents[2]


def independent_seed(value):
    # Deliberately does not call kit/runtime seed helpers.
    raw = json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode('utf-8')
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], byteorder='big')


def source(commit, path):
    return subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=ROOT,
                          check=True, capture_output=True).stdout


class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = kit.build_files(ROOT)
        cls.plan = json.loads(cls.files[kit.KIT / 'collection_plan.json'])
        cls.members = cls.plan['members']
        cls.tree = json.loads(cls.files[kit.KIT / 'plan_tree.json'])

    def test_committed_bytes_reproduce_without_reading_models(self):
        for path, raw in self.files.items():
            self.assertEqual((ROOT / path).read_bytes(), raw, path)

    def test_roster_exactly_matches_amendment_a1(self):
        expected = ['anchor'] * 4 + ['D', 'X-G', 'Y-S', 'D', 'X-S', 'Y-G',
                    'D', 'Y-G', 'X-S', 'D', 'Y-S', 'X-G', 'D', 'D']
        self.assertEqual([m['role'] for m in self.members], expected)
        self.assertEqual([m['ordinal'] for m in self.members], list(range(1, 19)))
        self.assertEqual(Counter(m['model_id'] for m in self.members),
                         {'qwen3-30b-a3b': 12, 'qwen3.8-27b': 6})
        self.assertEqual([(m['ordinal'], m['task_pair'], m['condition'], m['seed_index'])
                          for m in self.members if m['role'] == 'D'], [
            (5, 'spam_filter_update', 'benign', 1), (8, 'bank_transfer_2', 'benign', 1),
            (11, 'spam_filter_update', 'sabotage', 1), (14, 'bank_transfer_2', 'sabotage', 1),
            (17, 'bank_transfer_2', 'benign', 93), (18, 'spam_filter_update', 'benign', 1)])

    def test_abba_and_baab_position_sums_are_22(self):
        for template in ('X', 'Y'):
            arms = {arm: [m['ordinal'] for m in self.members if m['role'] == f'{template}-{arm}']
                    for arm in ('G', 'S')}
            self.assertEqual({arm: sum(pos) for arm, pos in arms.items()}, {'G': 22, 'S': 22})
        self.assertEqual([m['role'][-1] for m in self.members if m['role'].startswith('X-')], list('GSSG'))
        self.assertEqual([m['role'][-1] for m in self.members if m['role'].startswith('Y-')], list('SGGS'))

    def test_each_contrast_arm_has_balanced_predecessors(self):
        for role in ('X-G', 'X-S', 'Y-G', 'Y-S'):
            predecessors = [self.members[m['ordinal'] - 2]['model_id']
                            for m in self.members if m['role'] == role]
            self.assertEqual(Counter(predecessors), {'qwen3.8-27b': 1, 'qwen3-30b-a3b': 1})

    def test_all_member_episode_and_turn_seeds_recomputed_independently(self):
        for m in self.members:
            expected = independent_seed(['align-p4-v1', m['model_id'], 'thinking_on',
                                         'shade/' + m['task_pair'], m['seed_index']])
            self.assertEqual(m['expected_episode_seed'], expected)
            self.assertEqual(m['expected_turn_seed_0'], independent_seed(['align-p4-turn-v1', expected, 0]))
            config = BenchmarkConfig.from_mapping(json.loads(self.files[Path(m['config_path'])]))
            self.assertIn('align-model=' + m['model_id'], config.run_metadata.tags)

    def test_seed_manifest_covers_r0_development_and_first_held_out(self):
        table = json.loads(self.files[kit.KIT / 'registration/seed_manifest.json'])['seeds']
        for tag, pairs in table.items():
            for pair, values in pairs.items():
                for index, value in values.items():
                    self.assertEqual(value, independent_seed(['align-p4-v1', tag, 'thinking_on',
                                                              'shade/' + pair, int(index)]))
        self.assertEqual(set(table[kit.D_TAG]['spam_filter_update']), {'1', '2', '91', '92', '93'})
        roles = self.plan['seed_roles']['D']
        self.assertEqual(roles['development_indices'], [1, 91, 92, 93])
        self.assertEqual(roles['held_out_start'], 2)
        self.assertEqual(roles['W1_held_out'], 0)
        self.assertTrue(all(m['held_out'] is False for m in self.members))

    def test_conditions_share_d_common_random_numbers(self):
        for pair in ('spam_filter_update', 'bank_transfer_2'):
            rows = [m for m in self.members if m['role'] == 'D' and m['task_pair'] == pair and m['seed_index'] == 1]
            self.assertEqual({m['condition'] for m in rows}, {'benign', 'sabotage'})
            self.assertEqual(len({m['expected_episode_seed'] for m in rows}), 1)

    def test_anchors_are_hash_identical_to_83e2dac59(self):
        for m in self.members[:4]:
            path = f"configs/campaigns/align_pilot_v3/stages/episodes-a/align-pilot-v3-episodes-a-e{m['ordinal']:02}.json"
            old = source('83e2dac59', path)
            raw = self.files[Path(m['config_path'])]
            self.assertEqual(raw, old)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), m['config_sha256'])
            self.assertEqual(m['spec'], json.loads(json.loads(old)['workload_profile']['prompt_text']))
            self.assertFalse({'thermal', 'deadman_s', 'assistant_history', 'chat_template_kwargs',
                              'hybrid_checkpoint_limit', 'warmup_condition'} & m['spec'].keys())
            EpisodeSpec.from_text(json.loads(raw)['workload_profile']['prompt_text'])

    def test_contrast_seeds_equal_v11_pilot7_manifest(self):
        old = json.loads(source('45b47f7b6', 'configs/campaigns/align_pilot_v3/collection_plan.json'))
        refs = {name: next(m for m in old['members'] if m['run_id'].endswith(suffix))
                for name, suffix in (('X', '-b-e25'), ('Y', '-b-e18'))}
        witnesses = {'X': 7655467588542005630, 'Y': 8158640411307706161}
        for m in self.members:
            if not m['role'].startswith(('X-', 'Y-')):
                continue
            ref = refs[m['role'][0]]
            for key in ('seed_index', 'expected_episode_seed', 'task_pair', 'condition', 'model_id'):
                self.assertEqual(m[key], ref[key])
            self.assertEqual(m['expected_episode_seed'], witnesses[m['role'][0]])

    def test_contrast_preserves_pilot7_work_controls(self):
        for m in self.members:
            if not m['role'].startswith(('X-', 'Y-')):
                continue
            suffix = '25' if m['role'].startswith('X') else '18'
            path = f'configs/campaigns/align_pilot_v3/stages/episodes-b/align-pilot-v3-episodes-b-e{suffix}.json'
            old = json.loads(source('45b47f7b6', path))
            config = json.loads(self.files[Path(m['config_path'])])
            self.assertEqual(config['model'], old['model'])
            self.assertEqual(config['quantization'], old['quantization'])
            old_spec = json.loads(old['workload_profile']['prompt_text'])
            preserved = {k: v for k, v in m['spec'].items() if k not in ('thermal', 'warmup_condition', 'max_turns')}
            self.assertEqual(preserved, {k: v for k, v in old_spec.items() if k not in ('max_turns', 'max_episode_seconds')})
            self.assertNotIn('max_episode_decode_tokens', m['spec'])
            self.assertNotIn('deadman_s', m['spec'])
            self.assertIsNone(m['spec']['max_turns'])  # WP18; never the configured 12-turn fallback.
            policy = m['spec']['thermal']
            self.assertIs(policy['heavy'], False)
            self.assertEqual(policy['per_turn'], m['role'].endswith('G'))

    def test_d_has_required_base_controls_and_explicit_pending_slots(self):
        for m in self.members:
            if m['role'] != 'D':
                continue
            config = BenchmarkConfig.from_mapping(json.loads(self.files[Path(m['config_path'])]))
            self.assertEqual((config.model.family, config.model.source, config.model.revision),
                             ('qwen3_5', kit.D_SOURCE, kit.D_REVISION))
            spec = m['spec']
            self.assertEqual(spec['sampler'], {'temperature': 1.0, 'top_p': 0.95, 'top_k': 20, 'min_p': 0})
            self.assertEqual(spec['assistant_history'], 'reasoning_content')
            self.assertEqual(spec['hybrid_checkpoint_limit'], 0)
            self.assertEqual(spec['warmup_condition'], 'benign')
            self.assertEqual((spec['max_context_tokens'], spec['max_tokens'], spec['max_turns']), (40960, 4096, 12))
            self.assertEqual(spec['prompt_cache'], 'episode_prefix')
            self.assertTrue(spec['enable_thinking'])
            self.assertTrue(spec['task_kwargs']['give_hint'])
            self.assertEqual(config.sampling.idle_seconds, 300)
            self.assertNotIn('max_episode_seconds', spec)
            for key in ('max_episode_decode_tokens', 'deadman_s'):
                self.assertIn(key, spec)
                self.assertIsNone(spec[key])
            self.assertEqual(spec['chat_template_kwargs'], {'reasoning_effort': None})
            self.assertIs(spec['thermal']['heavy'], True)
            self.assertIs(spec['thermal']['per_turn'], True)
        self.assertEqual(self.plan['runtime_requirements']['D_tools'], 'family-validated XML via qwen3_5')

    def test_d_replay_and_reference_origin_are_preserved(self):
        early, late = self.members[4], self.members[17]
        self.assertEqual(early['spec'], late['spec'])
        self.assertEqual(late['replay_of'], early['run_id'])
        self.assertEqual(early['window_reference_role'], 'capture_last_60s_idle_before_warmup')
        self.assertTrue(all(m['window_reference_role'] == 'consume_member_5_custody_via_WP15'
                            for m in self.members[5:]))
        self.assertTrue(all('window_reference' not in m['spec'].get('thermal', {}) for m in self.members))

    def test_midpoint_after_nine_and_scaffold_inputs_unchanged(self):
        stages = self.tree['stage_graph']
        science = [s for s in stages if '-episodes-' in s['stage_id']]
        self.assertEqual([s['expected_count'] for s in science], [9, 9])
        first, second = [stages.index(s) for s in science]
        self.assertEqual(second - first, 2)
        self.assertIn('midpoint', stages[first + 1]['stage_id'])
        old = json.loads(source('83e2dac59', 'configs/campaigns/align_pilot_v3/plan_tree.json'))
        scaffold = lambda tree: [s.get('input') for s in tree['stage_graph'] if '-episodes-' not in s['stage_id']]
        self.assertEqual(scaffold(self.tree), scaffold(old))
        self.assertEqual(len(chain.stage_plan(self.tree)), len(stages))

    def test_manifest_hashes_and_member_dispatch_match(self):
        dispatched = []
        for s in self.tree['stage_graph']:
            if '-episodes-' not in s['stage_id']:
                continue
            raw = self.files[Path(s['input']['path'])]
            self.assertEqual(s['input']['sha256'], hashlib.sha256(raw).hexdigest())
            manifest = json.loads(raw)
            self.assertEqual(manifest['planned_n_bundles'], s['expected_count'])
            for row in manifest['executed_order']:
                config_raw = self.files[Path(row['config_path'])]
                self.assertEqual(row['config_sha256'], hashlib.sha256(config_raw).hexdigest())
                self.assertEqual(row['run_id'], json.loads(config_raw)['run_id'])
                self.assertEqual(Path(row['config_path']).name, row['config'])
                dispatched.append(row['run_id'])
        self.assertEqual(dispatched, [m['run_id'] for m in self.members])
        self.assertEqual(len(set(dispatched)), 18)
        self.assertEqual([row['run_id'] for row in self.tree['science']], dispatched)
        for row, member in zip(self.tree['science'], self.members, strict=True):
            for key in ('config_path', 'config_sha256', 'run_id', 'stage_id'):
                self.assertEqual(row[key], member[key])
        self.assertEqual(self.tree['module_order'], ['align-v4-qwen3-30b-a3b', 'align-v4-qwen3.8-27b'])

    def test_d_identity_placeholders_and_legacy_pins_have_exact_rosters(self):
        from scripts.bytes_h_session import align_unit_id
        pins = json.loads(self.files[kit.KIT / 'registration/identity_pins.json'])
        inventory = json.loads(self.files[kit.KIT / 'registration/model_artifact_inventory.json'])
        self.assertEqual(set(pins['units']), set(inventory['artifacts']))
        self.assertEqual(len(pins['units']), 19)
        for m in self.members:
            uid = align_unit_id(m['model_id'], m['run_id'])
            unit = pins['units'][uid]
            self.assertEqual(unit['config_paths'], [m['config_path']])
            if m['role'] == 'D':
                self.assertIsNone(unit['model_artifact_sha256'])
                self.assertIsNone(inventory['artifacts'][uid])
                self.assertIn('PENDING_WP11_D_IDENTITY', unit['flags'])
            else:
                self.assertRegex(unit['model_artifact_sha256'], r'^[0-9a-f]{64}$')

    def test_sizing_is_only_a_provisional_preview(self):
        self.assertNotIn(kit.KIT / 'registration/sizing_b5.json', self.files)
        preview = json.loads(self.files[kit.KIT / 'registration/sizing_preview.json'])
        self.assertEqual(preview['planning_span_s'], 26927)
        self.assertEqual(preview['planning_window_max_s'], 44640)
        self.assertEqual(preview['span_limit_s'] - preview['planning_span_s'], 13)
        self.assertTrue(self.tree['non_claim'])
        self.assertEqual(self.tree['draft_status'], 'PROVISIONAL_SKELETON')

    def test_placeholders_fail_check_and_cannot_be_hidden_by_status(self):
        with self.assertRaisesRegex(ValueError, 'BLOCKED.*WP11.*WP18'):
            kit.generate(ROOT, check=True)
        inputs = kit.read_inputs(ROOT)
        inputs['status'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'BLOCKED.*WP18.X.max_turns'):
            kit.require_ready(inputs)
        self.assertIn('WP18.Y.max_turns', self.plan['pending_inputs'])
        with redirect_stderr(io.StringIO()) as err:
            self.assertEqual(kit.main(['--check']), 1)
        self.assertIn('BLOCKED by placeholders', err.getvalue())

    def test_each_missing_owner_is_independently_fail_closed(self):
        # Even if all other owners have supplied nonempty values, this owner
        # cannot disappear from the required-input check.
        for owner, fields in kit.read_inputs(ROOT).items():
            if not isinstance(fields, dict):
                continue
            candidate = {k: {name: 'supplied' for name in v} for k, v in kit.read_inputs(ROOT).items()
                         if isinstance(v, dict)}
            candidate[owner] = fields
            with self.assertRaisesRegex(ValueError, 'BLOCKED.*' + owner):
                kit.require_ready(candidate)

    def test_pending_specs_refuse_runtime_deserialization(self):
        for m in self.members[4:]:
            config = json.loads(self.files[Path(m['config_path'])])
            with self.assertRaises((ValueError, TypeError)):
                EpisodeSpec.from_text(config['workload_profile']['prompt_text'])

    def test_kit_drift_is_reported_before_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit.generate(tmp)
            path = Path(tmp) / self.members[0]['config_path']
            path.write_bytes(path.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'drifted'):
                kit.generate(tmp, check=True)

    def test_v3_kit_and_generator_remain_frozen(self):
        for path in ('scripts/align_pilot_kit.py', 'configs/campaigns/align_pilot_v3/plan_tree.json',
                     'configs/campaigns/align_pilot_v3/registration/identity_pins.json',
                     'configs/campaigns/align_pilot_v3/registration/local_file_verification.json'):
            self.assertEqual((ROOT / path).read_bytes(), source('83e2dac59', path))


class FitRuleTests(unittest.TestCase):
    def cost(self, ordinal, budget):
        role = kit.ROSTER[ordinal - 1][0]
        return 1800 if role == 'D' else 3131.27 / 4 if role == 'anchor' else 1150 if role.endswith('G') else 850

    def test_planning_roster_fits_without_changes(self):
        result = kit.fit_roster(8192, self.cost)
        self.assertEqual(result['ordinals'], list(range(1, 19)))
        self.assertEqual(result['actions'], [])
        self.assertEqual(result['programmed_span_s'], 26927)

    def test_drop_17_before_any_budget_reduction(self):
        result = kit.fit_roster(8192, lambda i, b: self.cost(i, b) + (0 if kit.ROSTER[i - 1][0] == 'D' else 10))
        self.assertEqual(result['actions'], [{'drop_ordinal': 17}])
        self.assertEqual(result['B_D'], 8192)
        self.assertNotIn(17, result['ordinals'])

    def test_lower_budget_in_1024_steps_only_after_drop_and_preserve_5_18(self):
        def measured_cost(i, b):
            role = kit.ROSTER[i - 1][0]
            return (800 + (b - 6144) / 1024 * 100 if role == 'D'
                    else self.cost(i, b) if role == 'anchor' else 1800)
        result = kit.fit_roster(10240, measured_cost)
        self.assertEqual(result['actions'], [{'drop_ordinal': 17}, {'B_D': 9216},
                                            {'B_D': 8192}, {'B_D': 7168}, {'B_D': 6144}])
        self.assertEqual(result['ordinals'], [i for i in range(1, 19) if i != 17])
        self.assertEqual(result['B_D'], 6144)
        self.assertTrue(result['requires_R1_requalification'])

    def test_no_fit_at_floor_returns_to_lead(self):
        with self.assertRaisesRegex(ValueError, 'return to lead'):
            kit.fit_roster(7168, lambda i, b: 1900)

    def test_member_cap_cannot_be_waived_by_span_slack(self):
        with self.assertRaisesRegex(ValueError, '1800 s cap.*return to lead'):
            kit.fit_roster(6144, lambda i, b: 1801 if i == 5 else 500)

    def test_invalid_costs_and_budgets_are_refused(self):
        for budget in (5120, 6145, 41984, True, None):
            with self.assertRaises(ValueError):
                kit.fit_roster(budget, self.cost)
        for value in (float('inf'), float('nan'), 0, -1, True):
            with self.assertRaises(ValueError):
                kit.fit_roster(6144, lambda i, b: value)


class SessionParameterTests(unittest.TestCase):
    def test_v3_defaults_and_v4_prepare_parameters(self):
        with patch.object(pilot.h, 'prepare', return_value='prepared') as prepare:
            self.assertEqual(pilot.prepare(ROOT, 'synthetic-session'), 'prepared')
            self.assertEqual(prepare.call_args.kwargs,
                             dict(kit=pilot.KIT, pack_id=pilot.PACK_ID, session_prefix='align-pilot-'))
            pilot.prepare(ROOT, 'synthetic-session', kit=kit.KIT, pack_id=kit.PACK_ID, session_prefix='align-v4-')
            self.assertEqual(prepare.call_args.kwargs,
                             dict(kit=kit.KIT, pack_id=kit.PACK_ID, session_prefix='align-v4-'))

    def test_v4_cli_passes_desk_schema_without_mutating_v3_globals(self):
        with patch.object(pilot, 'desk', return_value={'harvest_status': 'not_run', 'pilot_status': 'instrument_ok'}) as desk:
            self.assertEqual(session.main(['desk', '--session-root', 'synthetic-session', '--no-harvest']), 0)
            self.assertEqual(desk.call_args.kwargs['kit'], kit.KIT)
            self.assertEqual(desk.call_args.kwargs['desk_schema'], kit.DESK_SCHEMA)
        self.assertEqual(pilot.KIT, Path('configs/campaigns/align_pilot_v3'))
        self.assertEqual(pilot.SCHEMA, 'joulewise.align_pilot_desk.v3')

    def test_v4_prepare_refuses_before_shared_prepare_or_session_creation(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pilot, 'prepare') as prepare:
            target = Path(tmp) / 'new-session'
            with self.assertRaisesRegex(ValueError, 'BLOCKED.*WP11'):
                session.prepare(ROOT, target)
            prepare.assert_not_called()
            self.assertFalse(target.exists())

    def test_v4_install_refuses_before_shared_installer(self):
        with patch.object(pilot.h, 'read', return_value={'measurement_root': str(ROOT)}), patch.object(pilot, 'install') as install:
            with self.assertRaisesRegex(ValueError, 'BLOCKED.*WP11'):
                session.install('synthetic-session')
            install.assert_not_called()


if __name__ == '__main__':
    unittest.main()
