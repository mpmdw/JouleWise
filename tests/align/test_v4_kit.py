"""WP16 acceptance on pinned repo configs and synthetic inputs; no study data."""
from collections import Counter
from copy import deepcopy
from contextlib import redirect_stderr
import hashlib
import io
import json
import os
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime
from joulewise.align.apple.workload import EpisodeSpec
from joulewise.b5 import chain
from joulewise.schemas import BenchmarkConfig
from joulewise.b6 import registration
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_session as session
from scripts import validate_align_v4_w1_plan as validator

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
        self.assertTrue(all('ac_powermode' in m for m in self.members))
        self.assertIn('ac_powermode', self.plan['runtime_requirements'])
        self.assertEqual(Counter(m['model_id'] for m in self.members),
                         {'qwen3-30b-a3b': 12, 'qwen3.8-27b': 6})
        self.assertEqual([(m['ordinal'], m['task_pair'], m['condition'], m['seed_index'])
                          for m in self.members if m['role'] == 'D'], [
            (5, 'spam_filter_update', 'benign', 1), (8, 'bank_transfer_2', 'benign', 1),
            (11, 'spam_filter_update', 'sabotage', 1), (14, 'bank_transfer_2', 'sabotage', 1),
            (17, 'spam_filter_update', 'benign', 1), (18, 'bank_transfer_2', 'benign', 93)])

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
            preserved = {k: v for k, v in m['spec'].items()
                         if k not in ('thermal', 'warmup_condition', 'max_turns', 'deadman_s')}
            self.assertEqual(preserved, {k: v for k, v in old_spec.items() if k not in ('max_turns', 'max_episode_seconds')})
            self.assertNotIn('max_episode_decode_tokens', m['spec'])
            self.assertEqual(m['spec']['deadman_s'], kit.CONTRAST_DEADMAN_S)
            # FD T_dead,m with the pilot-3 30B intercept: the member stays under
            # the runner's 1,800 s kill, and the deadman covers the planned
            # episode of its arm (S 850 s, G 1,150 s planning member_s).
            law = json.loads((ROOT / 'configs/campaigns/align_pilot_v3/registration/sizing_b5.json')
                             .read_text())['packs']['align-pilot-v3']['member_law']
            self.assertEqual(kit.CONTRAST_MEMBER_INTERCEPT_S, law['intercept_s'])
            self.assertLessEqual(law['intercept_s'] + 1.13544 * m['spec']['deadman_s'], 1750 + 1e-9)
            planned = {'S': 850, 'G': 1150}[m['role'][-1]]
            self.assertGreaterEqual(m['spec']['deadman_s'], (planned - law['intercept_s']) / 1.13544)
            # WP18 (filled from the committed fixtures): the recorded pilot-7
            # turn count of that arm's fixture, not a configured fallback.
            fixture = json.loads((ROOT / kit.WP18_FIXTURES[m['role'][0]]).read_text())
            self.assertEqual(m['spec']['max_turns'], kit.read_inputs(ROOT)['WP18'][m['role'][0]]['max_turns'])
            self.assertEqual(m['spec']['max_turns'], len(fixture['turns']))
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
        early, late = self.members[4], self.members[16]
        def without_reference(spec):
            value = json.loads(json.dumps(spec))
            value['thermal'].pop('window_reference')
            return value
        self.assertEqual(without_reference(early['spec']), without_reference(late['spec']))
        self.assertEqual(late['replay_of'], early['run_id'])
        self.assertEqual(early['window_reference_role'], 'capture_last_60s_idle_before_warmup')
        self.assertTrue(all(m['window_reference_role'] == 'consume_member_5_custody_via_WP15'
                            for m in self.members[5:]))
        self.assertEqual(early['spec']['thermal']['window_reference'], {'role': 'capture'})
        source_config = BenchmarkConfig.from_mapping(json.loads(self.files[Path(early['config_path'])]))
        digest = hashlib.sha256(kit.bundle_config_bytes(source_config)).hexdigest()
        for member in self.members[5:]:
            self.assertEqual(member['spec']['thermal']['window_reference'], {
                'role': 'consume', 'source_run_id': early['run_id'],
                'source_config_sha256': digest})

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

    def test_d_identity_and_legacy_pins_have_exact_rosters(self):
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
                # WP11 supplied: the folded sha of the pinned shards, no placeholder flag.
                wp11 = kit.read_inputs(ROOT)['WP11']
                self.assertEqual(unit['model_artifact_sha256'], wp11['identity_unit']['model_artifact_sha256'])
                self.assertEqual(inventory['artifacts'][uid], wp11['artifact_inventory'])
                self.assertEqual(unit['flags'], ['runtime_stack_unobserved'])
                self.assertEqual(unit['stack_identity'], {})
            else:
                self.assertRegex(unit['model_artifact_sha256'], r'^[0-9a-f]{64}$')

    def test_powermode_arm_refuses_and_desk_marks_any_member_mismatch(self):
        plan = json.loads(json.dumps(self.plan))
        plan['runtime_requirements']['ac_powermode'] = 0
        for member in plan['members']:
            member['ac_powermode'] = 0
        kit.arm_powermode_check(plan, 0)
        with self.assertRaisesRegex(ValueError, 'AC powermode mismatch'):
            kit.arm_powermode_check(plan, 2)
        observed = {m['run_id']: 0 for m in plan['members']}
        self.assertTrue(kit.validate_powermode_members(plan, observed)['instrument_ok'])
        observed[plan['members'][7]['run_id']] = 2
        verdict = kit.validate_powermode_members(plan, observed)
        self.assertFalse(verdict['instrument_ok'])
        self.assertEqual(verdict['powermode_mismatches'][0]['run_id'], plan['members'][7]['run_id'])

    def test_sizing_is_only_a_provisional_preview_until_r1_fills_the_w1_plan(self):
        self.assertNotIn(kit.W1_PLAN, self.files)
        self.assertNotIn(kit.KIT / 'registration/sizing_b5.json', self.files)
        preview = json.loads(self.files[kit.KIT / 'registration/sizing_preview.json'])
        self.assertEqual(preview['planning_span_s'], 26927)
        self.assertEqual(preview['planning_window_max_s'], 44640)
        self.assertEqual(preview['span_limit_s'] - preview['planning_span_s'], 13)
        self.assertTrue(self.tree['non_claim'])
        self.assertEqual(self.tree['draft_status'], 'PROVISIONAL_SKELETON')

    def test_placeholders_fail_check_and_cannot_be_hidden_by_status(self):
        with self.assertRaisesRegex(ValueError, 'BLOCKED.*R0.*R1'):
            kit.generate(ROOT, check=True)
        inputs = kit.read_inputs(ROOT)
        inputs['status'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'BLOCKED.*R0.reasoning_effort'):
            kit.require_ready(inputs)
        self.assertIn('R1.T_dead', self.plan['pending_inputs'])
        # WP18 is filled; an emptied WP18 leaf still blocks, whatever status says.
        inputs['WP18']['X']['max_turns'] = None
        with self.assertRaisesRegex(ValueError, 'BLOCKED.*WP18.X.max_turns'):
            kit.require_ready(inputs)
        with redirect_stderr(io.StringIO()) as err:
            self.assertEqual(kit.main(['--check']), 1)
        self.assertIn('BLOCKED by placeholders', err.getvalue())

    def test_each_missing_owner_is_independently_fail_closed(self):
        # Even if all other owners have supplied nonempty values, this owner
        # cannot disappear from the required-input check.
        pending_owners = {p.split('.')[0] for p in kit.pending_inputs(kit.read_inputs(ROOT))}
        # WP11 (W1-blockers lane) and WP15 (the R1 runtime argv) are supplied;
        # emptying either must still block on its own.
        # WP18 is filled from the committed fixtures; it is checked below with the supplied owners.
        self.assertEqual(pending_owners, {'R0', 'R1'})
        for owner, fields in kit.read_inputs(ROOT).items():
            if not isinstance(fields, dict) or owner not in pending_owners | {'WP11', 'WP15', 'WP18'}:
                continue
            candidate = {k: {name: 'supplied' for name in v} for k, v in kit.read_inputs(ROOT).items()
                         if isinstance(v, dict)}
            # Committed values may already be supplied (WP15's runtime argv is);
            # an owner whose leaves are emptied must still block on its own.
            candidate[owner] = {name: None for name in fields}
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

    def test_drop_18_before_any_budget_reduction(self):
        result = kit.fit_roster(8192, lambda i, b: self.cost(i, b) + (0 if kit.ROSTER[i - 1][0] == 'D' else 10))
        self.assertEqual(result['actions'], [{'drop_ordinal': 18}])
        self.assertEqual(result['B_D'], 8192)
        self.assertNotIn(18, result['ordinals'])

    def test_lower_budget_in_1024_steps_only_after_drop_and_preserve_5_17(self):
        def measured_cost(i, b):
            role = kit.ROSTER[i - 1][0]
            return (800 + (b - 6144) / 1024 * 100 if role == 'D'
                    else self.cost(i, b) if role == 'anchor' else 1800)
        result = kit.fit_roster(10240, measured_cost)
        self.assertEqual(result['actions'], [{'drop_ordinal': 18}, {'B_D': 9216},
                                            {'B_D': 8192}, {'B_D': 7168}, {'B_D': 6144}])
        self.assertEqual(result['ordinals'], [i for i in range(1, 19) if i != 18])
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


def ready_inputs(i_d=300.0, tail=20.0):
    """Synthetic, fully supplied inputs (no model, no study data); WP11 is the committed one."""
    t_dead = kit.l1_t_dead(i_d, tail)
    policy = {'sensors': {'s_fast': 'TC0P', 's_slow': 'TG0P', 'fan_keys': [], 'r0_sha256': 'a' * 64},
              'classification_sha256': 'b' * 64, 'g0_cap_s': 600, 'contrast_g0_cap_s': 600,
              'delta_fast_c': 8.0, 'delta_slow_c': 1.5, 'turn_cap_s': 120, 'chunk_tokens': 512,
              'heavy': True, 'per_turn': True}
    inputs = {
        'WP11': deepcopy(kit.read_inputs(ROOT)['WP11']),
        'WP18': {'X': {'max_turns': 12, 'token_fixture_sha256': 'c' * 64},
                 'Y': {'max_turns': 10, 'token_fixture_sha256': 'd' * 64}},
        'R0': {'reasoning_effort': 'xhigh'},
        'R1': {'B_D': 8192, 'I_D': i_d, 'T_dead': t_dead, 'thermal_policy': policy},
        'WP15': {'runtime_entrypoint': ['scripts/align_r1_runtime.py', '--config', 'configs/align/v4/r1_runtime.json']},
    }
    return inputs, r1_record(i_d, tail)


GATED_PHASES = {'G0': 120.0, 'G1': 150.0, 'H': 90.0, 'decode': 280.0, 'prefill': 120.0, 'tool': 6.0}
X_G_PHASES = {'G0': 120.0, 'G1': 60.0, 'H': 0.0, 'decode': 300.0, 'prefill': 60.0, 'tool': 6.0, 'tail': 0.0}


def r1_record(i_d, tail, *, source=kit.R1_HARDWARE_SOURCE, ac_powermode=0):
    """The fields require_ready binds from an R1 driver r1_slots record."""
    return {'schema': kit.R1_SLOTS_SCHEMA, 'source': source, 'ac_powermode': ac_powermode,
            'slots_ac_powermode': ac_powermode,
            'thermometry': {'bar': 'pass', 'D': {'s_fast': 'TC0P', 's_slow': 'TG0P',
                                                 'die_candidates': ['TC0P'], 'heatsink_candidates': ['TG0P'],
                                                 'classification_sha256': 'b' * 64,
                                                 'alias_groups': [],
                                                 'sensor_pick_changed': False}},
            'max_r1_tail_s': tail,
            'slots': {'I_D': i_d, 'T_dead': 1451.0, 'B_D': 8192, 'N_chunk': 512, 'S5_fast': 8.0, 'S5': 1.5, 'S6': 1.5, 'S7': 120.0},
            'high_power': {'verdict': 'adopt' if ac_powermode == 2 else 'not_adopted'},
            'u5': {'verdict': 'pass', 'c': 1.0},
            # 14,000 tokens in 280 s = 50 tok/s; the 600 s G0 floor still fits 1(f).
            'deadman_budget': [{'run': name, 'g0_outcome': 'released',
                                'phases_s': dict(GATED_PHASES, tail=tail if i == 0 else tail / 2),
                                'decode_tokens': 14000, 'duty_bar': {'pass': True, 'verdict': 'pass'}}
                               for i, name in enumerate(kit.GATED_D_RUN_NAMES)],
            'budget_fit_inputs': {'r_decode_tok_per_s': 50.0, 'r_decode_step_d_tok_per_s': 50.0,
                                  'turn_cap_tokens': 4096},
            'external_volumes': [{'point': 't0', 'verdict': 'PASS'}], 'inconclusive_segments': {},
            # R10-4: X-G ran the complete WP18 X turns (12) with no deadman; 600 + 426 <= 1,086.3 s.
            'x_g': {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': 120.0,
                    'admitted_turns': 12, 'x7': False, 'phases_s': dict(X_G_PHASES)},
            'g0_cap_w1': {'authority': 'LEAD-RULINGS-2 R7-2, R7-12', 'r1_g0_timeout_s': 1200.0,
                          'floor_s': 600.0, 'factor': 1.25,
                          'waits_s': {**dict.fromkeys(kit.GATED_D_RUN_NAMES, 120.0), 'X_G_contrast': 120.0},
                          'censored': [], 'x_g_fallback': False, 'max_g0_s': 120.0, 'value_s': 600,
                          'rule': 'clamp(ceil(1.25 * max counted gated D and X-G G0 wait), 600, R1 g0_timeout_s)'},
            'duty_bar': {'pass': True, 'verdict': 'pass', 'schedule': R6_1_SCHEDULE}}


# LEAD-RULINGS-2 R6-1: the duty bar's schedule as the driver records it.
R6_1_SCHEDULE = {'authority': 'LEAD-RULINGS-2 R6-1', 'inter_member_idle_s': {'D': 300.0, 'X-G': 300.0}}


def set_decode_rate(slots, rate):
    """Step-d and every gated run decoding at ``rate`` tok/s (R6-3 re-derives the minimum)."""
    slots['budget_fit_inputs'].update(r_decode_tok_per_s=rate, r_decode_step_d_tok_per_s=rate)
    for row in slots['deadman_budget']:
        row['decode_tokens'] = round(rate * row['phases_s']['decode'])


class FakeArmHost:
    """launchctl, pmset, the narrow restore rule, mount and diskutil; nothing real runs."""

    def __init__(self, mode, ssd=False, *, marker=None, fail_high=False, night_job_loaded=False):
        self.mode, self.ssd, self.marker, self.fail_high = mode, ssd, marker, fail_high
        self.night_job_loaded = night_job_loaded
        self.calls = []

    def __call__(self, argv):
        import plistlib
        argv = tuple(argv)
        self.calls.append(argv)
        if argv == ('launchctl', 'print', f'gui/{os.getuid()}/com.joulewise.night'):
            absent = f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}'
            return subprocess.CompletedProcess(argv, 0 if self.night_job_loaded else 113, '',
                                               '' if self.night_job_loaded else absent + '\n')
        if argv == ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2'):
            # The marker must already exist when High Power is set (R5-6).
            if self.marker is not None and not self.marker.exists():
                raise AssertionError('High Power set before the marker was written')
            if self.fail_high:
                return subprocess.CompletedProcess(argv, 1, '', 'sudo: a password is required')
            self.mode = 2
            return subprocess.CompletedProcess(argv, 0, '', '')
        if argv == ('/usr/bin/pmset', '-g', 'custom'):
            out = f'Battery Power:\n powermode 0\nAC Power:\n lowpowermode 0\n powermode {self.mode}\n'
            return subprocess.CompletedProcess(argv, 0, out, '')
        if argv == ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '0'):
            self.mode = 0
            return subprocess.CompletedProcess(argv, 0, '', '')
        if argv == ('/sbin/mount',):
            out = '/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)\n'
            if self.ssd:
                out += '/dev/disk6s1 on /Volumes/JW-EXT (apfs, local, nodev, nosuid, journaled)\n'
            return subprocess.CompletedProcess(argv, 0, out, '')
        if argv[:3] == ('/usr/sbin/diskutil', 'info', '-plist'):
            external = argv[3].startswith('/dev/disk6')
            out = plistlib.dumps({'Internal': not external, 'BusProtocol': 'USB' if external else 'Apple Fabric',
                                  'FilesystemType': 'apfs', 'WritableVolume': True}).decode()
            return subprocess.CompletedProcess(argv, 0, out, '')
        raise AssertionError(f'unexpected command {argv}')


class R1EvidenceBindingTests(unittest.TestCase):
    """Executing review MEDIUM-3: r1_slots must be R1's own evidence."""

    def test_driver_shaped_hardware_record_admits(self):
        kit.require_ready(*ready_inputs())

    def test_synthetic_source_refuses_unless_the_harness_asks(self):
        inputs, slots = ready_inputs()
        for source in (kit.R1_SYNTHETIC_SOURCE, 'SYNTHETIC_WP22_DRY_RUN', 'PENDING_R1_REHEARSAL', None):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, 'source must be'):
                kit.require_ready(inputs, dict(slots, source=source))
        kit.require_ready(inputs, dict(slots, source=kit.R1_SYNTHETIC_SOURCE), synthetic=True)

    def test_wp22_stand_in_without_slots_refuses(self):
        inputs, _ = ready_inputs()
        with self.assertRaisesRegex(ValueError, 'r1_slots'):
            kit.require_ready(inputs, {'ac_powermode': 0, 'max_r1_tail_s': 20.0})

    def test_inputs_i_d_must_equal_the_r1_step_d_i_d(self):
        inputs, slots = ready_inputs(300.0)
        slots['slots']['I_D'] = 301.0
        with self.assertRaisesRegex(ValueError, 'differs from r1_slots.slots.I_D'):
            kit.require_ready(inputs, slots)

    def test_failed_duty_bar_needs_a_recorded_lead_fallback_step(self):
        inputs, slots = ready_inputs()
        slots['duty_bar'] = {'pass': False, 'verdict': 'fail', 'schedule': R6_1_SCHEDULE}
        slots['deadman_budget'][0]['duty_bar'] = {'pass': False, 'verdict': 'fail'}
        with self.assertRaisesRegex(ValueError, 'no lead fallback step'):
            kit.require_ready(inputs, slots)
        slots['duty_bar']['lead_fallback'] = {'step': 5, 'authority': 'x'}
        with self.assertRaisesRegex(ValueError, 'no lead fallback step'):
            kit.require_ready(inputs, slots)
        # Fable cold pass round 4 LOW-1: step 4 ("D screen-only") never admits W1.
        slots['duty_bar']['lead_fallback'] = {'step': 4, 'authority': 'LEAD-RULINGS-2 F4'}
        with self.assertRaisesRegex(ValueError, 'no lead fallback step'):
            kit.require_ready(inputs, slots)
        slots['duty_bar']['lead_fallback'] = {'step': 1, 'authority': 'LEAD-RULINGS-2 F1'}
        kit.require_ready(inputs, slots)

    def test_slots_must_come_from_the_adopted_series_mode_and_pass_the_thermometry_bar(self):
        # LEAD-RULINGS-2 R5-5: protocol v4 :243-251.
        inputs, slots = ready_inputs()
        for value in (None, 2):
            with self.subTest(slots_ac_powermode=value), self.assertRaisesRegex(ValueError, 'series AC powermode'):
                kit.require_ready(inputs, dict(slots, slots_ac_powermode=value))
        for value in (None, {'bar': 'fail'}, {}):
            with self.subTest(thermometry=value), self.assertRaisesRegex(ValueError, 'thermometry bar'):
                kit.require_ready(inputs, dict(slots, thermometry=value))
        # W1's gate keys must be in R1's lists; a changed pick needs the lead.
        for role, listing in (('s_fast', 'die'), ('s_slow', 'heatsink')):
            bad = deepcopy(inputs)
            bad['R1']['thermal_policy']['sensors'][role] = 'TX9Z'
            with self.subTest(role=role), self.assertRaisesRegex(ValueError, f'not in the R1 {listing} list'):
                kit.require_ready(bad, slots)
        changed = deepcopy(slots)
        changed['thermometry']['D']['sensor_pick_changed'] = True
        with self.assertRaisesRegex(ValueError, 'lead_verification'):
            kit.require_ready(inputs, changed)
        changed['thermometry']['lead_verification'] = {'authority': 'LEAD-RULINGS-3 S7 verified'}
        changed['thermometry']['D']['s7_for_r1_picks'] = {
            'S7': slots['slots']['S7'], 'band_c': {'s_fast': slots['slots']['S5_fast'], 's_slow': slots['slots']['S6']},
            'keys': {'s_fast': 'TC0P', 's_slow': 'TG0P'}, 'rule': r1_runtime.R1_PICK_S7_RULE,
            'noise_c': {'s_fast': slots['slots']['S5_fast'] / 3, 's_slow': slots['slots']['S6'] / 3},
            'recovery_s': slots['slots']['S7'] / 3}
        kit.require_ready(inputs, changed)

    def test_classification_digest_must_match_the_r1_record(self):
        inputs, slots = ready_inputs()
        kit.require_ready(inputs, slots)
        del inputs['R1']['thermal_policy']['classification_sha256']
        with self.assertRaisesRegex(ValueError, 'classification_sha256'):
            kit.check_r1_evidence(inputs, slots)
        for digest in (None, '', 'b' * 63, 'g' * 64, 'c' * 64):
            inputs['R1']['thermal_policy']['classification_sha256'] = digest
            with self.subTest(digest=digest), self.assertRaisesRegex(ValueError, 'classification_sha256'):
                kit.check_r1_evidence(inputs, slots)

    def test_classification_digest_is_not_installed_in_member_gate_policies(self):
        inputs, slots = ready_inputs()
        kit.require_ready(inputs, slots)
        with patch.object(kit, 'read_inputs', return_value=inputs), \
                patch.object(kit, 'read_r1_slots', return_value=slots):
            files = kit.build_files(ROOT)
        plan = json.loads(files[kit.KIT / 'collection_plan.json'])
        for member in plan['members']:
            config = json.loads(files[Path(member['config_path'])])
            spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
            with self.subTest(ordinal=member['ordinal']):
                if spec.thermal is not None:
                    self.assertNotIn('classification_sha256', spec.thermal)
        self.assertEqual(inputs['R1']['thermal_policy']['classification_sha256'], 'b' * 64)

    def test_plan_names_member_5_as_capture_and_no_r1_launcher(self):
        # Fable cold pass LOW-7 (LEAD-RULINGS-2 R5-7).
        plan = json.loads((ROOT / kit.KIT / 'collection_plan.json').read_text())
        block = plan['runtime_requirements']
        self.assertNotIn('launcher', block)
        self.assertEqual(block['window_reference']['capture_ordinal'], 5)
        self.assertEqual(block['r1_runtime_entrypoint'], kit.read_inputs(ROOT)['WP15']['runtime_entrypoint'])
        kit.check_window_reference_roles(plan)
        bad = deepcopy(plan)
        bad['members'][7]['spec']['thermal']['window_reference'] = {'role': 'capture'}
        with self.assertRaisesRegex(ValueError, 'member 8 window_reference'):
            kit.check_window_reference_roles(bad)
        bad = deepcopy(plan)
        bad['runtime_requirements']['launcher'] = block['r1_runtime_entrypoint']
        with self.assertRaisesRegex(ValueError, 'not the W1 launcher'):
            kit.check_window_reference_roles(bad)

    def test_powermode_must_follow_the_aba_verdict(self):
        inputs, slots = ready_inputs()
        slots['ac_powermode'] = 2  # but the A-B-A did not adopt
        with self.assertRaisesRegex(ValueError, 'disagrees with the A-B-A verdict'):
            kit.require_ready(inputs, slots)
        del slots['high_power']
        with self.assertRaisesRegex(ValueError, 'A-B-A verdict'):
            kit.require_ready(inputs, slots)

    def test_u5_tail_and_volume_fields_are_checked(self):
        inputs, slots = ready_inputs()
        for change, message in ((dict(u5={'verdict': 'pass', 'c': 2.0}), 'U5 verdict'),
                                (dict(u5=None), 'U5 verdict'),
                                (dict(deadman_budget=[{'phases_s': {'tail': 5.0}}]), 'largest gated-run tail'),
                                (dict(external_volumes=[{'verdict': 'REFUSE'}]), 'external-volume'),
                                (dict(external_volumes=[]), 'external-volume')):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message):
                kit.require_ready(inputs, dict(slots, **change))

    def test_powermode_members_refuse_an_unfrozen_series_value(self):
        # Cold pass LOW 1: expected None and observed None used to match.
        plan = {'members': [{'run_id': 'a', 'ac_powermode': None}, {'run_id': 'b', 'ac_powermode': 0}]}
        verdict = kit.validate_powermode_members(plan, {'a': None, 'b': 0})
        self.assertFalse(verdict['instrument_ok'])
        self.assertEqual([m['run_id'] for m in verdict['powermode_mismatches']], ['a'])
        with self.assertRaisesRegex(ValueError, 'freezes no series value'):
            kit.arm_powermode_check({'runtime_requirements': {'ac_powermode': None}}, None)


class R1BudgetBindingTests(unittest.TestCase):
    """Lead ruling R5-4: B_D, the thermal policy and ruling 1(f) bind to r1_slots."""

    def test_b_d_may_only_be_lowered_from_the_step_d_budget(self):
        inputs, slots = ready_inputs()
        inputs['R1']['B_D'] = 6144
        kit.require_ready(inputs, slots)
        inputs['R1']['B_D'] = 9216
        with self.assertRaisesRegex(ValueError, 'exceeds r1_slots.slots.B_D 8192'):
            kit.require_ready(inputs, slots)

    def test_r1_slots_without_an_admissible_step_d_budget_refuse(self):
        inputs, slots = ready_inputs()
        for bad in (0, None, 512, 8193, True):
            slots['slots']['B_D'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'slots.B_D must be the step-d'):
                kit.require_ready(inputs, slots)

    def test_thermal_policy_binds_n_chunk_s6_and_s7(self):
        for name, value in (('chunk_tokens', 768), ('delta_slow_c', 2.0), ('turn_cap_s', 90)):
            inputs, slots = ready_inputs()
            inputs['R1']['thermal_policy'][name] = value
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, f'thermal_policy.{name}'):
                kit.require_ready(inputs, slots)

    def test_s6_tuning_must_be_recorded_when_s6_leaves_s5(self):
        inputs, slots = ready_inputs()
        slots['slots']['S6'] = 2.0
        inputs['R1']['thermal_policy']['delta_slow_c'] = 2.0
        with self.assertRaisesRegex(ValueError, 'S6 differs from S5'):
            kit.require_ready(inputs, slots)
        for bad in ({}, {'authority': 'lead', 'from_c': 1.0, 'to_c': 2.0},
                    {'authority': ' ', 'from_c': 1.5, 'to_c': 2.0}, {'authority': 'lead', 'from_c': 1.5, 'to_c': 1.9}):
            slots['s6_tuning'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'S6 differs from S5'):
                kit.require_ready(inputs, slots)
        slots['s6_tuning'] = {'authority': 'lead, FD 2.6 S6 tuning', 'from_c': 1.5, 'to_c': 2.0}
        kit.require_ready(inputs, slots)
        slots['slots']['S6'] = inputs['R1']['thermal_policy']['delta_slow_c'] = 2.5
        slots['s6_tuning']['to_c'] = 2.5
        with self.assertRaisesRegex(ValueError, '2.0 C cap'):
            kit.require_ready(inputs, slots)

    def test_ruling_1f_refuses_a_budget_whose_worst_case_misses_t_dead(self):
        inputs, slots = ready_inputs()
        fit = kit.ruling_1f_fit(slots, 8192, inputs['R1']['T_dead'])
        self.assertAlmostEqual(fit['worst_s'], 600 + 240 + 126 + 12288 / 50)
        self.assertTrue(fit['fits'])
        set_decode_rate(slots, 11.0)   # FD:145's ~370 s per 4,096 tokens
        with self.assertRaisesRegex(ValueError, r'ruling 1\(f\): B_D 8192 does not fit.*largest fitting B_D is None'):
            kit.require_ready(inputs, slots)
        set_decode_rate(slots, 37.0)   # 966 + (B_D + 4096)/37 <= 1277.0
        self.assertEqual(kit.max_fitting_b_d(slots, inputs['R1']['T_dead']), 7168)
        with self.assertRaisesRegex(ValueError, 'largest fitting B_D is 7168'):
            kit.require_ready(inputs, slots)
        inputs['R1']['B_D'] = 7168
        kit.require_ready(inputs, slots)

    def test_ruling_1f_needs_the_measured_inputs(self):
        inputs, slots = ready_inputs()
        three = slots['deadman_budget']
        negative = deepcopy(three)
        negative[2]['phases_s']['H'] = -500.0
        for change in (dict(budget_fit_inputs=None), dict(budget_fit_inputs={'r_decode_tok_per_s': 20.0}),
                       dict(budget_fit_inputs={'r_decode_tok_per_s': 20.0, 'turn_cap_tokens': 4096}),
                       dict(deadman_budget=[{'phases_s': {'tail': 20.0}}]),
                       dict(deadman_budget=three[:2]),                       # the bank run left out
                       dict(deadman_budget=three[:2] + three[:1]),           # a run counted twice
                       dict(deadman_budget=negative),
                       dict(budget_fit_inputs={'r_decode_tok_per_s': 20.0, 'r_decode_step_d_tok_per_s': 20.0,
                                               'turn_cap_tokens': 1}),
                       dict(budget_fit_inputs={'r_decode_tok_per_s': 0.0, 'r_decode_step_d_tok_per_s': 0.0,
                                               'turn_cap_tokens': 4096}),
                       dict(budget_fit_inputs={'r_decode_tok_per_s': float('nan'),
                                               'r_decode_step_d_tok_per_s': float('nan'), 'turn_cap_tokens': 4096})):
            inputs, slots = ready_inputs()
            slots.update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, r'ruling 1\(f\)'):
                kit.require_ready(inputs, slots)


class R1ChangedPickBindingTests(unittest.TestCase):
    """R6-4: changed picks use the full-inventory R1 recovery and slow band."""

    def setUp(self):
        self.inputs, self.slots = ready_inputs()
        self.policy = self.inputs['R1']['thermal_policy']
        self.policy['sensors'].update(s_fast='TC1P', s_slow='TG1P')
        self.policy.update(delta_fast_c=1.0, delta_slow_c=1.25, turn_cap_s=60.0)
        self.slots['thermometry']['lead_verification'] = {'authority': 'lead, R6-4 verified'}
        self.slots['thermometry']['D'].update(
            sensor_pick_changed=True, s_fast='TC1P', s_slow='TG1P',
            die_candidates=['TC1P'], heatsink_candidates=['TG1P'],
            s7_for_r1_picks={'keys': {'s_fast': 'TC1P', 's_slow': 'TG1P'}, 'rule': r1_runtime.R1_PICK_S7_RULE,
                             'reference_c': {'s_fast': 40.0, 's_slow': 35.0},
                             'noise_c': {'s_fast': 0.1, 's_slow': 1.25 / 3},
                             'band_c': {'s_fast': 1.0, 's_slow': 1.25},
                             'recovery_s': 20.0, 'recovery_censored': False, 'S7': 60.0})

    def test_kit_rederives_the_r1_pick_bands_and_s7_with_the_runtime_functions(self):
        # LEAD-RULINGS-2 R9-2: one baseline (the classifier's D2) for the runtime
        # and the kit; the kit re-derives with r1_runtime.pick_band/pick_s7.
        kit.require_ready(self.inputs, self.slots)
        computed = self.slots['thermometry']['D']['s7_for_r1_picks']
        cases = {
            'pre-R9-2 rule': dict(rule='reference = quiet-window median; band = max(1.0, 3 SD); '
                                       'S7 = min(300, 3 x peak-to-band recovery)'),
            'rule missing': dict(rule=None),
            'noise missing': dict(noise_c=None),
            'noise not finite': dict(noise_c={'s_fast': 0.1, 's_slow': float('nan')}),
            'slow band not 3 x residual SD': dict(noise_c={'s_fast': 0.1, 's_slow': 0.5}),
            'fast band not the floor': dict(noise_c={'s_fast': 0.5, 's_slow': 1.25 / 3}),
            'recovery missing': dict(recovery_s=None),
            'S7 not 3 x recovery': dict(recovery_s=25.0),
        }
        for name, change in cases.items():
            slots = deepcopy(self.slots)
            slots['thermometry']['D']['s7_for_r1_picks'].update(change)
            with self.subTest(name), self.assertRaisesRegex(ValueError, r's7_for_r1_picks.*R9-2'):
                kit.require_ready(self.inputs, slots)
        # The runtime's own output on a synthetic step journal re-derives exactly.
        from tests.align.test_r1_inventory import PREFILL_NS, step_capture
        from tests.align.w1_synthetic import FAST, SLOW
        _, rows = step_capture()
        produced = r1_runtime.s7_for_picks(rows, {'s_fast': FAST, 's_slow': SLOW}, prefill_ns=PREFILL_NS, quiet_s=300)
        kit.rederive_r1_pick_s7(produced, 'r1_slots.thermometry.D.s7_for_r1_picks')
        self.assertEqual(computed['rule'], produced['rule'])

    def test_r1_pick_s6_and_s7_admit_with_lead_verification(self):
        kit.require_ready(self.inputs, self.slots)
        del self.slots['thermometry']['lead_verification']
        with self.assertRaisesRegex(ValueError, 'lead_verification'):
            kit.require_ready(self.inputs, self.slots)

    def test_r0_pick_s6_and_s7_refuse_when_different(self):
        for name, slot in (('turn_cap_s', 'S7'), ('delta_slow_c', 'S6')):
            inputs = deepcopy(self.inputs)
            inputs['R1']['thermal_policy'][name] = self.slots['slots'][slot]
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, r'thermometry\.D\.s7_for_r1_picks'):
                kit.require_ready(inputs, self.slots)

    def test_changed_picks_bind_delta_fast_to_the_r1_pick_fast_band(self):
        # Round-6 integration (cold LOW-1 x R6-4): S5_fast is R0's fast key's
        # soak band; with changed picks delta_fast_c binds the R1-pick band.
        self.assertNotEqual(self.slots['slots']['S5_fast'], 1.0)
        kit.require_ready(self.inputs, self.slots)
        self.policy['delta_fast_c'] = self.slots['slots']['S5_fast']
        with self.assertRaisesRegex(ValueError, r'delta_fast_c must equal .*s7_for_r1_picks\.band_c\.s_fast'):
            kit.require_ready(self.inputs, self.slots)
        self.policy['delta_fast_c'] = 1.0
        for value in (None, 0, -1, float('nan'), True):
            slots = deepcopy(self.slots)
            slots['thermometry']['D']['s7_for_r1_picks']['band_c']['s_fast'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'R1-pick fast band was not computed'):
                kit.require_ready(self.inputs, slots)

    def test_uncomputed_r1_pick_s6_or_s7_refuses(self):
        for name in ('S7', 's_slow'):
            for value in (None, 0, -1, float('nan'), float('inf'), True, '60'):
                slots = deepcopy(self.slots)
                computed = slots['thermometry']['D']['s7_for_r1_picks']
                (computed if name == 'S7' else computed['band_c'])[name] = value
                with self.subTest(name=name, value=value), self.assertRaisesRegex(
                        ValueError, r'thermometry\.D\.s7_for_r1_picks.*not computed'):
                    kit.require_ready(self.inputs, slots)
        del self.slots['thermometry']['D']['s7_for_r1_picks']
        with self.assertRaisesRegex(ValueError, r'thermometry\.D\.s7_for_r1_picks.*not computed'):
            kit.require_ready(self.inputs, self.slots)

    def test_policy_keys_must_be_the_keys_the_r1_pick_values_describe(self):
        # Sol critique of round 6: old keys still in the candidate lists, new numbers.
        self.slots['thermometry']['D'].update(die_candidates=['TC1P', 'TC0P'], heatsink_candidates=['TG1P', 'TG0P'])
        kit.require_ready(self.inputs, self.slots)
        self.policy['sensors'].update(s_fast='TC0P', s_slow='TG0P')
        # Round-6 integration: cold LOW-2 (policy sensors = the R1 picks) now
        # refuses this first; the R6-4 keys check still holds on its own when
        # the record's picks and the keys the values describe disagree.
        with self.assertRaisesRegex(ValueError, r'must equal the R1 thermometry\.D picks'):
            kit.require_ready(self.inputs, self.slots)
        self.slots['thermometry']['D'].update(s_fast='TC0P', s_slow='TG0P')
        with self.assertRaisesRegex(ValueError, r'not the keys .*s7_for_r1_picks\.keys'):
            kit.require_ready(self.inputs, self.slots)

    def test_s6_tuning_receipt_uses_the_r1_pick_base_and_cap(self):
        self.policy['delta_slow_c'] = 2.0
        self.slots['s6_tuning'] = {'authority': 'lead, FD 2.6', 'from_c': 1.25, 'to_c': 2.0}
        kit.require_ready(self.inputs, self.slots)
        self.slots['s6_tuning']['from_c'] = self.slots['slots']['S5']
        with self.assertRaisesRegex(ValueError, r'thermometry\.D\.s7_for_r1_picks'):
            kit.require_ready(self.inputs, self.slots)
        self.slots['s6_tuning']['from_c'] = 1.25
        self.slots['s6_tuning']['to_c'] = self.policy['delta_slow_c'] = 2.5
        with self.assertRaisesRegex(ValueError, r'thermometry\.D\.s7_for_r1_picks.*2.0 C cap'):
            kit.require_ready(self.inputs, self.slots)


class Round6KitTests(unittest.TestCase):
    """LEAD-RULINGS-2 R6-1, R6-2 and R6-3 in the kit."""

    def test_ruling_1f_uses_the_slowest_observed_decode_rate(self):
        inputs, slots = ready_inputs()
        # The bank run decoded at 10 tok/s (2,800 tokens in 280 s); step-d at 50.
        slots['deadman_budget'][2]['decode_tokens'] = 2800
        with self.assertRaisesRegex(ValueError, r'is not min\(step-d'):
            kit.require_ready(inputs, slots)       # the recorded 50 tok/s is stale
        slots['budget_fit_inputs']['r_decode_tok_per_s'] = 10.0
        fit = kit.ruling_1f_fit(slots, 8192, inputs['R1']['T_dead'])
        self.assertEqual(fit['r_decode_tok_per_s'], 10.0)
        self.assertAlmostEqual(fit['terms_s']['decode_s'], (8192 + 4096) / 10.0)
        # 966 + 12,288/10 > T_dead: step-d's rate alone would have admitted it.
        with self.assertRaisesRegex(ValueError, r'ruling 1\(f\): B_D 8192 does not fit'):
            kit.require_ready(inputs, slots)
        # A run that decoded nothing (G0 timeout) has no rate and does not lower it.
        inputs, slots = ready_inputs()
        slots['deadman_budget'][1]['decode_tokens'] = 0
        slots['deadman_budget'][1]['phases_s']['decode'] = 0.0
        kit.require_ready(inputs, slots)
        for bad in (None, -1, 1.5, True, '14000'):
            inputs, slots = ready_inputs()
            slots['deadman_budget'][0]['decode_tokens'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'decode_tokens'):
                kit.require_ready(inputs, slots)
        inputs, slots = ready_inputs()
        slots['deadman_budget'][0]['phases_s']['decode'] = 0.0      # tokens without decode seconds
        with self.assertRaisesRegex(ValueError, 'decode_tokens'):
            kit.require_ready(inputs, slots)

    def test_duty_bar_must_record_w1_s_schedule(self):
        self.assertEqual(kit.w1_inter_member_idle_s(), {'D': 300.0, 'X-G': 300.0})
        for schedule in (None, {}, {'authority': 'LEAD-RULINGS-2 R5-1', 'inter_member_idle_s': {'D': 300.0, 'X-G': 300.0}},
                         {'authority': 'LEAD-RULINGS-2 R6-1', 'inter_member_idle_s': {'D': 450.0, 'X-G': 300.0}}):
            inputs, slots = ready_inputs()
            slots['duty_bar']['schedule'] = schedule
            with self.subTest(schedule=schedule), self.assertRaisesRegex(ValueError, 'R6-1 schedule'):
                kit.require_ready(inputs, slots)

    def test_an_inconclusive_step_d_is_refused_by_name(self):
        inputs, slots = ready_inputs()
        slots['inconclusive_segments'] = {kit.STEP_D_SEGMENT: 'G0 did not release, twice'}
        with self.assertRaisesRegex(ValueError, 'step-d was INCONCLUSIVE'):
            kit.require_ready(inputs, slots)

    def test_an_inconclusive_designed_state_refuses_w1(self):
        # Sol critique of round 6: fail closed at the kit for every R6-2 segment.
        inputs, slots = ready_inputs()
        slots['inconclusive_segments'] = {'planning_turn_R_plus_2C': 'G0 did not release, twice'}
        with self.assertRaisesRegex(ValueError, r'INCONCLUSIVE \(R6-2\): planning_turn_R_plus_2C'):
            kit.require_ready(inputs, slots)
        del slots['inconclusive_segments']
        with self.assertRaisesRegex(ValueError, 'inconclusive_segments'):
            kit.require_ready(inputs, slots)


class Round7KitTests(unittest.TestCase):
    def test_r1_g0_timeout_is_read_from_config_and_validated(self):
        self.assertEqual(kit.r1_g0_timeout_s(), 1200.0)
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'configs/align/v4/r1_runtime.json'
            config.parent.mkdir(parents=True)
            for value in (600, 975.5, 1200):
                config.write_text(json.dumps({'g0_timeout_s': value}))
                self.assertEqual(kit.r1_g0_timeout_s(tmp), value)
            for value in (None, 599, 1201, True, float('nan'), '1200'):
                config.write_text(json.dumps({'g0_timeout_s': value}))
                with self.subTest(value=value), self.assertRaises(ValueError):
                    kit.r1_g0_timeout_s(tmp)

    def test_w1_g0_cap_released_waits_and_rounding(self):
        _, slots = ready_inputs()
        for row, wait in zip(slots['deadman_budget'], (120, 300, 500)):
            row['phases_s']['G0'] = wait
        slots['x_g']['g0_wait_s'] = 400
        cap = kit.w1_g0_cap(slots)
        self.assertEqual(cap['value_s'], 625)
        self.assertEqual(cap['max_g0_s'], 500)
        self.assertEqual(cap['waits_s'], dict(zip((*kit.GATED_D_RUN_NAMES, 'X_G_contrast'), (120, 300, 500, 400))))
        self.assertEqual(cap['censored'], [])
        self.assertIs(cap['x_g_fallback'], False)
        slots['x_g']['g0_wait_s'] = 500.1
        self.assertEqual(kit.w1_g0_cap(slots)['value_s'], 626)  # ceil, not truncation

    def test_w1_g0_cap_floor_and_ceiling(self):
        _, slots = ready_inputs()
        self.assertEqual(kit.w1_g0_cap(slots)['value_s'], 600)
        slots['deadman_budget'][0]['phases_s']['G0'] = 1000
        self.assertEqual(kit.w1_g0_cap(slots)['value_s'], 1200)

    def test_w1_g0_cap_counts_censored_d_at_full_r1_timeout(self):
        for outcome in ('timeout', 'deadman', 'unobserved'):
            _, slots = ready_inputs()
            row = slots['deadman_budget'][1]
            row['g0_outcome'] = outcome
            cap = kit.w1_g0_cap(slots)
            with self.subTest(outcome=outcome):
                self.assertEqual(cap['value_s'], 1200)
                self.assertEqual(cap['waits_s'][row['run']], 1200)
                self.assertEqual(cap['censored'], [row['run']])
                self.assertIs(cap['x_g_fallback'], False)

    def test_w1_g0_cap_refuses_bad_observations_and_run_sets(self):
        _, base = ready_inputs()
        for outcome in (None, '', 'unknown', True):
            for member in ('D', 'X-G'):
                slots = deepcopy(base)
                target = slots['deadman_budget'][0] if member == 'D' else slots['x_g']
                target['g0_outcome'] = outcome
                with self.subTest(outcome=outcome, member=member), self.assertRaisesRegex(ValueError, 'g0_outcome'):
                    kit.w1_g0_cap(slots)
        for wait in (None, -1, float('nan'), float('inf'), True, '12'):
            for member in ('D', 'X-G'):
                slots = deepcopy(base)
                if member == 'D':
                    slots['deadman_budget'][0]['phases_s']['G0'] = wait
                else:
                    slots['x_g']['g0_wait_s'] = wait
                with self.subTest(wait=wait, member=member), self.assertRaisesRegex(ValueError, 'wait'):
                    kit.w1_g0_cap(slots)
        for rows in (None, [], base['deadman_budget'][:2],
                     base['deadman_budget'][:2] + base['deadman_budget'][:1]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, 'exactly the three'):
                kit.w1_g0_cap(dict(base, deadman_budget=rows))

    def test_missing_or_stale_g0_cap_record_is_refused(self):
        for field, value in ((None, None), ('value_s', 601), ('x_g_fallback', True), ('r1_g0_timeout_s', 600),
                             ('max_g0_s', 130.0), ('censored', ['D_bank_benign_s1_gated_held']), ('censored', None),
                             ('waits_s', {}), ('floor_s', 500.0), ('factor', 1.5)):
            inputs, slots = ready_inputs()
            if field is None:
                del slots['g0_cap_w1']
            else:
                slots['g0_cap_w1'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, r'r1_slots\.g0_cap_w1.*missing or stale'):
                kit.require_ready(inputs, slots)

    def test_policy_g0_cap_must_bind_the_derived_slot(self):
        inputs, slots = ready_inputs()
        inputs['R1']['thermal_policy']['g0_cap_s'] = 625
        # R10-4: the D members' cap is the D-role derivation of R7-2's rule.
        with self.assertRaisesRegex(ValueError, r'g0_cap_s must equal the W1 D-role G0 cap.*R7-2, R10-4'):
            kit.require_ready(inputs, slots)

    def test_ruling_1f_uses_w1_cap_instead_of_measured_d_max(self):
        inputs, slots = ready_inputs()
        set_decode_rate(slots, 20.0)
        fit = kit.ruling_1f_fit(slots, 8192, inputs['R1']['T_dead'])
        self.assertEqual(fit['terms_s']['G0_s'], 600)
        self.assertEqual(fit['g0_cap_w1'], kit.w1_g0_cap(slots))
        old_worst = 120 + 240 + 126 + (8192 + 4096) / 20
        self.assertLess(old_worst, inputs['R1']['T_dead'])
        self.assertFalse(fit['fits'])
        with self.assertRaisesRegex(ValueError, r'ruling 1\(f\).*g0_cap_w1'):
            kit.require_ready(inputs, slots)

    def test_inconclusive_x_g_falls_back_and_is_refused_by_the_contrast_fit(self):
        # R7-12's fallback still sets the X-G (D-to-X) term to the R1 timeout,
        # but since LEAD-RULINGS-2 R10-4 that term is the contrast members'
        # own cap, not D's: 1(f) keeps D's 600 s cap, and the contrast cap of
        # 1,200 s cannot fit the 1,086.3 s contrast deadman, so W1 is refused
        # (R10-2(a)), where before R10 it was admitted.
        inputs, slots = ready_inputs(i_d=0)
        for row in slots['deadman_budget']:
            row['phases_s'].update(G1=0, H=0)
        set_decode_rate(slots, 80.0)
        slots['x_g'].update(status='inconclusive', g0_outcome='timeout', g0_wait_s=1200)
        cap = slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        self.assertIs(cap['x_g_fallback'], True)
        self.assertEqual(cap['waits_s']['X_G_contrast'], 1200)
        self.assertIn('X_G_contrast', cap['censored'])
        fit = kit.ruling_1f_fit(slots, 8192, inputs['R1']['T_dead'])
        self.assertEqual(fit['terms_s']['G0_s'], 600)
        self.assertTrue(fit['fits'])
        self.assertEqual(kit.w1_contrast_g0_cap(slots, 12)['value_s'], 1200)
        with self.assertRaisesRegex(ValueError, r'R10-2\(a\): the contrast members.*R7-12'):
            kit.require_ready(inputs, slots)
        # No G0 interval after a predecessor did no D work: still censored.
        slots['x_g']['g0_wait_s'] = None
        self.assertEqual(kit.w1_g0_cap(slots), cap)

    def test_missing_x_g_dict_is_refused(self):
        inputs, slots = ready_inputs()
        for value in (None, [], 'inconclusive', {}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, r'r1_slots\.x_g'):
                kit.require_ready(inputs, dict(slots, x_g=value))

    def test_inconclusive_calibration_refusals_name_rerun_and_magistrate(self):
        for segment in (kit.STEP_D_SEGMENT, 'planning_turn_R_plus_2C'):
            inputs, slots = ready_inputs()
            slots['inconclusive_segments'] = {segment: 'G0 timed out twice'}
            with self.subTest(segment=segment), self.assertRaises(ValueError) as raised:
                kit.require_ready(inputs, slots)
            message = str(raised.exception)
            for text in ('re-run', 'magistrate', 'no per-occurrence lead ruling', 'LEAD-RULINGS-2 R7-3'):
                self.assertIn(text, message)

    def test_missing_or_malformed_alias_groups_refuse(self):
        for value in (None, {}, ['TC0P', 'TG0P'], [[1, 2]], [['TC0P']], [['TG0P', 'TC0P']],
                      [['TC0P', 'TC0P']], [['TC0P', 'TG0P'], ['TG0P', 'Tm0P']]):
            inputs, slots = ready_inputs()
            if value is None:
                del slots['thermometry']['D']['alias_groups']
            else:
                slots['thermometry']['D']['alias_groups'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'alias_groups.*R7-13'):
                kit.require_ready(inputs, slots)

    def test_selected_aliases_or_same_key_refuse_as_one_thermometer(self):
        for same_key in (False, True):
            inputs, slots = ready_inputs()
            if same_key:
                inputs['R1']['thermal_policy']['sensors']['s_slow'] = 'TC0P'
            else:
                slots['thermometry']['D']['alias_groups'] = [['TC0P', 'TG0P']]
            with self.subTest(same_key=same_key), self.assertRaisesRegex(
                    ValueError, 'aliased keys are one thermometer.*LEAD-RULINGS-2 R7-13'):
                kit.require_ready(inputs, slots)

    def test_aliases_elsewhere_preserve_admission(self):
        inputs, slots = ready_inputs()
        slots['thermometry']['D']['alias_groups'] = [['TCMb', 'TVD0'], ['Tf24', 'Tf2D', 'Tf2E']]
        kit.require_ready(inputs, slots)
        # Prove this is admission through the independence check, not a bypass.
        slots['thermometry']['D']['alias_groups'].append(['TC0P', 'TG0P'])
        with self.assertRaisesRegex(ValueError, 'aliased keys are one thermometer'):
            kit.require_ready(inputs, slots)


class L1Tests(unittest.TestCase):
    """Lead ruling L1: restated council ruling 1(f)."""

    def test_runtime_entrypoint_must_be_an_argv_list(self):
        # Fable cold pass LOW-3: one shell string is not an argv.
        inputs, slots = ready_inputs(300.0, 20.0)
        kit.require_ready(inputs, slots)
        for bad in ('scripts/align_r1_runtime.py --config configs/align/v4/r1_runtime.json', [], ['']):
            inputs['WP15']['runtime_entrypoint'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'argv list|BLOCKED'):
                kit.require_ready(inputs, slots)

    def test_small_tail_keeps_the_original_t_dead(self):
        inputs, slots = ready_inputs(300.0, 20.0)
        self.assertAlmostEqual(inputs['R1']['T_dead'], (1750 - 300) / 1.13544)
        kit.require_ready(inputs, slots)

    def test_large_tail_lowers_t_dead_and_the_member_fits(self):
        inputs, slots = ready_inputs(300.0, 75.0)
        self.assertAlmostEqual(inputs['R1']['T_dead'], (1800 - 300 - 75 - 10) / 1.13544)
        kit.require_ready(inputs, slots)
        self.assertLessEqual(kit.check_l1_member_fit(300.0, inputs['R1']['T_dead'], 75.0), 1800 + 1e-6)
        # The pre-L1 rule (T_dead = (1750 - I_D)/1.13544) no longer passes with this tail.
        inputs['R1']['T_dead'] = (1750 - 300) / 1.13544
        with self.assertRaisesRegex(ValueError, 'lead ruling L1'):
            kit.require_ready(inputs, slots)
        with self.assertRaisesRegex(ValueError, 'exceeds the 1800 s member cap'):
            kit.check_l1_member_fit(300.0, (1750 - 300) / 1.13544, 75.0)

    def test_missing_or_invalid_r1_tail_is_refused(self):
        inputs, slots = ready_inputs()
        for tail in (None, -1.0, float('nan'), 'x'):
            with self.subTest(tail=tail), self.assertRaisesRegex(ValueError, 'max_r1_tail_s'):
                kit.require_ready(inputs, dict(slots, max_r1_tail_s=tail))

    def test_thermal_policy_must_carry_heavy_per_turn(self):
        inputs, slots = ready_inputs()
        del inputs['R1']['thermal_policy']['heavy']
        with self.assertRaisesRegex(ValueError, 'missing or unknown fields'):
            kit.require_ready(inputs, slots)


class SessionParameterTests(unittest.TestCase):

    def setUp(self):
        # Lead ruling R6-7: a private host-level High Power state per test.
        from joulewise.align.apple import powermode
        host = tempfile.TemporaryDirectory()
        self.addCleanup(host.cleanup)
        env = patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(Path(host.name) / 'host-power')})
        env.start()
        self.addCleanup(env.stop)

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
            with self.assertRaisesRegex(ValueError, 'BLOCKED.*R0.reasoning_effort'):
                session.prepare(ROOT, target)
            prepare.assert_not_called()
            self.assertFalse(target.exists())

    def test_v4_prepare_with_ready_inputs_refuses_on_missing_r1_sizing_before_shared_prepare(self):
        inputs, slots = ready_inputs()
        with tempfile.TemporaryDirectory() as tmp, patch.object(pilot, 'prepare') as prepare, \
                patch.object(kit, 'read_inputs', return_value=inputs), \
                patch.object(kit, 'read_r1_slots', return_value=slots), \
                patch.object(kit, 'build_files', return_value={}):
            target = Path(tmp) / 'new-session'
            with self.assertRaisesRegex(ValueError, r'BLOCKED: .*sizing_b5\.json is not derivable yet.*'
                                                    r'FINAL-DESIGN B8.*w1_plan\.json'):
                session.prepare(ROOT, target)
            prepare.assert_not_called()
            self.assertFalse(target.exists())

    def test_v4_install_refuses_before_shared_installer(self):
        with patch.object(pilot.h, 'read', return_value={'measurement_root': str(ROOT)}), patch.object(pilot, 'install') as install:
            with self.assertRaisesRegex(ValueError, 'BLOCKED.*R0.reasoning_effort'):
                session.install('synthetic-session', w1_disk_config='/x.json')
            install.assert_not_called()

    def _arm_fixture(self, tmp, mode_expected=2):
        measurement = Path(tmp) / 'measurement'
        session_root = Path(tmp) / 'session'
        session_root.mkdir()
        plan = json.loads((ROOT / kit.KIT / 'collection_plan.json').read_text())
        plan['runtime_requirements']['ac_powermode'] = mode_expected
        (measurement / kit.KIT / 'registration').mkdir(parents=True)
        (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(plan))
        (measurement / kit.R1_SLOTS).write_text(json.dumps({'ac_powermode': mode_expected}))
        pilot.h.write(session_root / 'session.json', {'measurement_root': str(measurement)})
        return measurement, session_root

    def test_v4_install_reads_measurement_r1_slots_and_refuses_powermode_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            measurement, session_root = self._arm_fixture(tmp)
            # The series froze 2 (R5-6: install sets it); a host that cannot be
            # set to High Power stays at 0 and the arm refuses the mismatch.
            host = FakeArmHost(mode=0, fail_high=True)
            seen = []
            with patch.object(kit, 'read_inputs', return_value={}), \
                    patch.object(kit, 'require_w1_ready', side_effect=seen.append), \
                    patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
                    patch.object(pilot, 'install', return_value={'exit_code': 0}) as install:
                with self.assertRaisesRegex(ValueError, 'set High Power failed.*AC powermode 0 != expected 2'):
                    session.install(session_root, runner=host, volume_runner=host)
                install.assert_not_called()
                self.assertEqual(seen, [str(measurement)])
                self.assertEqual(host.mode, 0)
                host.fail_high = False
                session.install(session_root, runner=host, volume_runner=host)
                install.assert_called_once()
                self.assertEqual(host.mode, 2)

    def test_v4_arm_records_observed_powermode_pmset_text_and_volume_census(self):
        # Cold pass MEDIUM-5 (ruling 7): every arm records the observed value.
        with tempfile.TemporaryDirectory() as tmp:
            measurement, session_root = self._arm_fixture(tmp, mode_expected=0)
            host = FakeArmHost(mode=0)
            with patch.object(kit, 'read_inputs', return_value={}), \
                    patch.object(kit, 'require_w1_ready'), \
                    patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
                    patch.object(pilot, 'install'):
                session.install(session_root, runner=host, volume_runner=host)
            record = json.loads((session_root / 'staging/v4-arm-001.json').read_text())
            self.assertTrue(record['admitted'])
            self.assertEqual(record['ac_powermode']['observed'], 0)
            self.assertIn('AC Power:', record['ac_powermode']['pmset_text'])
            self.assertEqual(record['external_volumes']['verdict'], 'PASS')
            self.assertIn('/', [m['mount_point'] for m in record['external_volumes']['mounts']])
            state = pilot.h.read(session_root / 'session.json')
            self.assertEqual(state['v4_arm_records'][0]['ac_powermode'], 0)

    def test_v4_arm_refuses_any_mounted_external_volume_and_records_it(self):
        # Ruling 20: no external volume mounted at W1/D arm (status "off").
        with tempfile.TemporaryDirectory() as tmp:
            measurement, session_root = self._arm_fixture(tmp, mode_expected=0)
            host = FakeArmHost(mode=0, ssd=True)
            with patch.object(kit, 'read_inputs', return_value={}), \
                    patch.object(kit, 'require_w1_ready'), \
                    patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
                    patch.object(pilot, 'install') as install:
                with self.assertRaisesRegex(ValueError, 'external_volume_mounted:/Volumes/JW-EXT'):
                    session.install(session_root, runner=host, volume_runner=host)
                install.assert_not_called()
            record = json.loads((session_root / 'staging/v4-arm-001.json').read_text())
            self.assertFalse(record['admitted'])
            self.assertEqual(record['external_volumes']['external'][0]['mount_point'], '/Volumes/JW-EXT')

    def test_v4_arm_restores_an_r1_high_power_marker_then_rechecks(self):
        # Lead ruling R6-7: the owed restore now runs at the session start
        # (before the arm), which reads the mode back; the arm then sees 0.
        with tempfile.TemporaryDirectory() as tmp:
            measurement, session_root = self._arm_fixture(tmp, mode_expected=0)
            marker = measurement / '.align-r1-high-power'
            marker.write_text('high-power restoration required\n')
            host = FakeArmHost(mode=2)
            with patch.object(kit, 'read_inputs', return_value={}), \
                    patch.object(kit, 'require_w1_ready'), \
                    patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
                    patch.object(pilot, 'install') as install:
                session.install(session_root, runner=host, volume_runner=host)
                install.assert_called_once()
            self.assertEqual(host.mode, 0)
            self.assertFalse(marker.exists())
            [start] = (session_root / 'staging').glob('v4-session-start-restore-*.json')
            start = json.loads(start.read_text())
            self.assertEqual((start['action'], start['restore']['observed']), ('restored', 0))
            record = json.loads((session_root / 'staging/v4-arm-001.json').read_text())
            self.assertEqual([o['value'] for o in record['ac_powermode']['observations']], [0])

    def test_every_member_spec_runs_its_roster_task_pair(self):
        files = kit.build_files(ROOT)
        for member in json.loads(files[kit.KIT / 'collection_plan.json'])['members']:
            self.assertEqual(member['spec']['task_kwargs']['task_pair'], member['task_pair'], member['run_id'])
            config = json.loads(files[Path(member['config_path'])])
            spec = json.loads(config['workload_profile']['prompt_text'])
            self.assertEqual(spec['task_kwargs']['task_pair'], member['task_pair'], member['run_id'])


def planning_member_s(member):
    """Amendment-1 planning member seconds (anchors 3131.27/4, D 1800, G 1150, S 850)."""
    role = member['role']
    return 1800 if role == 'D' else 3131.27 / 4 if role == 'anchor' else 1150 if role.endswith('G') else 850


def filled_w1_plan(inputs, slots, seconds=planning_member_s, collection_plan=None):
    """A synthetic R1-filled copy of the W1 template (validator arithmetic)."""
    plan = validator.build_template(collection_plan)
    block = plan['align_v4']
    r1 = inputs['R1']
    block.update(B_D=r1['B_D'], I_D=r1['I_D'], T_dead=r1['T_dead'], max_r1_tail_s=slots['max_r1_tail_s'],
                 effort=inputs['R0']['reasoning_effort'], thermal_policy=deepcopy(r1['thermal_policy']),
                 status='SYNTHETIC_FILLED')
    for member in block['members']:
        member['member_s'] = seconds(member)
    align_s = math.fsum(m['member_s'] for m in block['members'])
    span = math.ceil(block['arithmetic']['scaffold_s'] + align_s)
    block['arithmetic'].update(align_s=align_s, programmed_span_s=span)
    plan['window_max_s'] = 60 * math.ceil((span + validator.T0_STAGE_CAP_S + validator.PAUSE_LIMIT_S
                                           + validator.SESSION_WAIT_BUDGET_S) / 60)
    plan['plan_id'] = 'align-v4-w1-synthetic'
    return plan


class WP11IdentityTests(unittest.TestCase):
    """W1 blocker 3: the D artifact sha in the identity pins was null."""

    FOLDED = 'a8d1c5c963787dd9dc524912e05d409172124da773d196e8f5123820b4c36b30'

    def setUp(self):
        self.wp11 = deepcopy(kit.read_inputs(ROOT)['WP11'])
        self.pins = kit.read_d_pins(ROOT)

    def test_committed_wp11_is_not_pending_and_binds_the_folded_pins(self):
        self.assertFalse([p for p in kit.pending_inputs(kit.read_inputs(ROOT)) if p.startswith('WP11.')])
        raw = (ROOT / kit.D_PINS).read_bytes()
        self.assertEqual(kit.validate_d_identity(self.wp11, self.pins, pins_raw=raw), self.FOLDED)
        self.assertEqual(self.wp11['identity_unit']['model_artifact_sha256'], self.FOLDED)

    def test_wp11_receipt_pins_the_actual_hf_pin_document_bytes(self):
        # Sol w1rev (R5-9): the hf_pins receipt is bound to the pin file's bytes.
        raw = (ROOT / kit.D_PINS).read_bytes()
        bad = deepcopy(self.wp11)
        bad['local_file_verification']['hf_pins']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'committed pins bytes'):
            kit.validate_d_identity(bad, self.pins, pins_raw=raw)
        with self.assertRaisesRegex(ValueError, 'committed pins bytes'):
            kit.validate_d_identity(self.wp11, self.pins, pins_raw=raw + b' ')
        bad['local_file_verification']['hf_pins'] = {'path': 'elsewhere.json'}
        with self.assertRaisesRegex(ValueError, 'identify the D HF pins document'):
            kit.validate_d_identity(bad, self.pins)

    def test_w1_readiness_reads_the_pin_bytes(self):
        with patch.object(kit, 'require_ready'), patch.object(kit, 'require_sizing'), \
                patch.object(kit, 'validate_wp18_fixtures'), \
                patch.object(kit, 'validate_d_identity', wraps=kit.validate_d_identity) as validate:
            kit.require_w1_ready(ROOT)
        self.assertEqual(validate.call_args.kwargs['pins_raw'], (ROOT / kit.D_PINS).read_bytes())

    def test_kit_identity_pins_load_with_a_64_hex_d_sha(self):
        files = kit.build_files(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'identity_pins.json'
            target.write_bytes(files[kit.KIT / 'registration/identity_pins.json'])
            pins = registration.load_identity_pins(target)
        d_units = [u for u in pins['units'].values() if u['model_source'] == kit.D_SOURCE]
        self.assertEqual(len(d_units), 6)
        self.assertEqual({u['model_artifact_sha256'] for u in d_units}, {self.FOLDED})
        inventory = json.loads(files[kit.KIT / 'registration/model_artifact_inventory.json'])['artifacts']
        for uid, unit in pins['units'].items():
            if unit['model_source'] == kit.D_SOURCE:
                self.assertEqual(sorted(f['path'] for f in inventory[uid]['inventory']),
                                 sorted(n for n in self.pins['files'] if n.endswith('.safetensors')))

    def test_a_wrong_or_partial_d_copy_is_refused(self):
        def tamper(fn):
            wp11 = deepcopy(self.wp11)
            fn(wp11)
            return wp11
        first = 'model-00001-of-00006.safetensors'
        cases = {
            'shard hash': lambda w: w['artifact_inventory']['files'].update({first: '0' * 64}),
            'missing shard': lambda w: (w['artifact_inventory']['files'].pop(first),
                                        w['artifact_inventory']['inventory'].pop(0)),
            'row size': lambda w: w['artifact_inventory']['inventory'][0].update(size_bytes=1),
            'unit sha': lambda w: w['identity_unit'].update(model_artifact_sha256='f' * 64),
            'verification sha': lambda w: w['local_file_verification'].update(folded_sha256='f' * 64),
            'unverified': lambda w: w['local_file_verification'].update(status='pending'),
            'root': lambda w: w['artifact_inventory'].update(root='/elsewhere'),
            'revision': lambda w: w['identity_unit'].update(model_revision='0' * 40),
        }
        for name, fn in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                kit.validate_d_identity(tamper(fn), self.pins)
        pins = deepcopy(self.pins)
        pins['files'][first]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'HF LFS pins'):
            kit.validate_d_identity(self.wp11, pins)

    def test_require_w1_ready_checks_d_identity_before_other_pending_inputs(self):
        inputs = kit.read_inputs(ROOT)
        inputs['WP11']['artifact_inventory']['files']['model-00001-of-00006.safetensors'] = '0' * 64
        with patch.object(kit, 'read_inputs', return_value=inputs), \
                self.assertRaisesRegex(ValueError, 'HF LFS pins'):
            kit.require_w1_ready(ROOT)


class PendingMessageTests(unittest.TestCase):
    """W1 blockers 4 and 5: each remaining placeholder names exactly what it waits for."""

    def message(self, **remove):
        inputs, _ = ready_inputs()
        for owner, keys in remove.items():
            for key in keys:
                inputs[owner][key] = None if owner != 'WP18' else {'max_turns': None, 'token_fixture_sha256': None}
        with self.assertRaises(ValueError) as caught:
            kit.require_ready(inputs, {'ac_powermode': 0, 'max_r1_tail_s': 20.0})
        return str(caught.exception)

    def test_r0_effort_placeholder_says_it_waits_for_r0_to_pass(self):
        text = self.message(R0=('reasoning_effort',))
        self.assertIn('BLOCKED by placeholders: R0.reasoning_effort |', text)
        self.assertIn('R0: R0.reasoning_effort stays a placeholder until R0 passes.', text)
        self.assertNotIn('WP18:', text)
        inputs, slots = ready_inputs()
        inputs['R0']['reasoning_effort'] = 'high'
        with self.assertRaisesRegex(ValueError, 'R0.reasoning_effort stays a placeholder until R0 passes'):
            kit.require_ready(inputs, slots)

    def test_wp18_placeholder_names_the_pilot7_members_turn_counts_and_fixture(self):
        text = self.message(WP18=('X', 'Y'))
        for needle in ('WP18.X.max_turns', 'WP18.Y.token_fixture_sha256', 'Mac-side',
                       'align-pilot-v3-episodes-b-e25', 'seed index 16', 'align-pilot-v3-episodes-b-e18',
                       'index 14', 'recorded pilot-7 turn count', 'never the configured 12-turn ceiling',
                       'align_turns.jsonl', 'p7-PILOT.json', 'CHAIR ruling 9(d)'):
            self.assertIn(needle, text)

    def test_committed_kit_check_states_every_remaining_owner_reason(self):
        with self.assertRaises(ValueError) as caught:
            kit.generate(ROOT, check=True)
        text = str(caught.exception)
        self.assertNotIn('WP11', text)
        self.assertNotIn('WP15', text)  # the R1 runtime argv is committed in inputs.json
        self.assertNotIn('WP18', text)  # filled from the committed X/Y token fixtures
        for owner in ('R0', 'R1'):
            self.assertIn(f'| {owner}: ' + kit.PENDING_REASONS[owner], text)


class W1SizingTests(unittest.TestCase):
    """W1 blocker 2: sizing_b5.json is derived from the R1-filled W1 plan."""

    @classmethod
    def setUpClass(cls):
        cls.inputs, cls.slots = ready_inputs()
        with patch.object(kit, 'read_inputs', return_value=deepcopy(cls.inputs)), \
                patch.object(kit, 'read_r1_slots', return_value=deepcopy(cls.slots)), \
                patch.object(kit, 'read_w1_plan_bytes', return_value=None):
            # D config bytes depend on the R1 inputs; bind the plan to that roster.
            cls.collection_plan = json.loads(kit.build_files(ROOT)[kit.KIT / 'collection_plan.json'])
        cls.plan = filled_w1_plan(cls.inputs, cls.slots, collection_plan=cls.collection_plan)
        cls.raw = (json.dumps(cls.plan, indent=2, sort_keys=True) + '\n').encode()
        with patch.object(kit, 'read_inputs', return_value=deepcopy(cls.inputs)), \
                patch.object(kit, 'read_r1_slots', return_value=deepcopy(cls.slots)), \
                patch.object(kit, 'read_w1_plan_bytes', return_value=cls.raw):
            cls.files = kit.build_files(ROOT)
        cls.sizing = json.loads(cls.files[kit.SIZING])

    def test_kit_derives_sizing_from_the_filled_plan_with_the_design_arithmetic(self):
        self.assertEqual(self.files[kit.W1_PLAN], self.raw)
        sized = self.sizing['packs'][kit.PACK_ID]
        # Amendment 1 W1 arithmetic at the planning member_s.
        self.assertEqual(sized['programmed_span_s'], 26927)
        self.assertEqual(sized['window_max_s'], 44640)
        self.assertAlmostEqual(sized['align_s'], 21931.27, places=6)
        self.assertEqual(sized['T_stream_max_s'], 1800)
        self.assertTrue(sized['fits_spent_cap'])
        self.assertEqual(round(sized['disk_derivation']['B_bytes'] / 1e9, 2), 18.71)
        self.assertEqual(sized['estimated_footprint_bytes'], 2 * sized['disk_derivation']['B_bytes'])
        tree = json.loads(self.files[kit.KIT / 'plan_tree.json'])
        collected = sum(s['expected_count'] for s in tree['stage_graph'] if s['kind'] == 'campaign_collection')
        self.assertEqual((sized['align_members'], sized['member_count']), (18, collected))
        self.assertEqual(self.sizing['sources']['w1_plan']['sha256'], hashlib.sha256(self.raw).hexdigest())

    def test_sizing_loads_through_the_prepare_and_plan_input_readers(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'sizing_b5.json').write_bytes(self.files[kit.SIZING])
            sized = registration.load_sizing(tmp)['packs'][kit.PACK_ID]
        from joulewise.b6 import plan_inputs
        self.assertEqual(plan_inputs.window_max_s({'programmed_span_s': {'seconds': sized['programmed_span_s']}}),
                         sized['window_max_s'])
        terms = sized['disk_derivation']
        for key in ('peak_copies', 'B_bytes', 'extra_wait_peak_bytes', 'fixed_retained_bytes'):
            self.assertIsInstance(terms[key], int)
        self.assertEqual(plan_inputs.sizing_label({'packs': {'x': sized}}, kit.PACK_ID), 'x')

    def test_invalid_filled_plan_refuses_generation(self):
        bad = deepcopy(self.plan)
        bad['align_v4']['members'][4]['member_s'] = 1801
        raw = json.dumps(bad).encode()
        with patch.object(kit, 'read_inputs', return_value=deepcopy(self.inputs)), \
                patch.object(kit, 'read_r1_slots', return_value=deepcopy(self.slots)), \
                patch.object(kit, 'read_w1_plan_bytes', return_value=raw), \
                self.assertRaisesRegex(ValueError, '1,800 s spent cap'):
            kit.build_files(ROOT)

    def test_require_sizing_needs_the_plan_then_the_derived_file(self):
        with self.assertRaisesRegex(ValueError, r'sizing_b5\.json is not derivable yet.*FINAL-DESIGN B8'):
            kit.require_sizing(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / kit.W1_PLAN).parent.mkdir(parents=True)
            (Path(tmp) / kit.W1_PLAN).write_bytes(self.raw)
            with self.assertRaisesRegex(ValueError, 'missing; regenerate'):
                kit.require_sizing(tmp)
            (Path(tmp) / kit.SIZING).write_bytes(self.files[kit.SIZING])
            kit.require_sizing(tmp)
            # Sol w1rev (R5-9): sizing_b5.json is bound to the W1 plan bytes it came from.
            (Path(tmp) / kit.W1_PLAN).write_bytes(self.raw + b' ')
            with self.assertRaisesRegex(ValueError, 'is stale'):
                kit.require_sizing(tmp)
            (Path(tmp) / kit.SIZING).write_text('{}')
            with self.assertRaisesRegex(ValueError, 'W1-plan provenance'):
                kit.require_sizing(tmp)


class WP18FixtureBindingTests(unittest.TestCase):
    """Lead ruling R5-8: the WP18 fixtures are a hard W1 prerequisite."""

    def write(self, root, inputs):
        from scripts import align_v4_wp18_fixtures as tool
        for name, (run_id, _, _, _) in tool.ARMS.items():
            fixture = {'schema': kit.WP18_FIXTURE_SCHEMA, 'arm': name, 'run_id': run_id,
                       'max_turns': inputs['WP18'][name]['max_turns'],
                       'turns': [{'turn': i, 'prompt_token_ids': [1], 'output_token_ids': [2]}
                                 for i in range(inputs['WP18'][name]['max_turns'])],
                       'sources': {'align_turns_jsonl_sha256': 'a' * 64, 'p7_pilot_json_sha256': 'b' * 64}}
            raw = (json.dumps(fixture, sort_keys=True) + '\n').encode()
            path = root / kit.WP18_FIXTURES[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            inputs['WP18'][name]['token_fixture_sha256'] = hashlib.sha256(raw).hexdigest()

    def test_filled_digests_must_bind_committed_fixture_bytes(self):
        inputs, _ = ready_inputs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'WP18.X token fixture is missing'):
                kit.validate_wp18_fixtures(inputs, root)
            self.write(root, inputs)
            kit.validate_wp18_fixtures(inputs, root)
            (root / kit.WP18_FIXTURES['Y']).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'WP18.Y.token_fixture_sha256 does not match'):
                kit.validate_wp18_fixtures(inputs, root)

    def test_fixture_must_be_the_arm_and_turn_count_inputs_name(self):
        inputs, _ = ready_inputs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, inputs)
            inputs['WP18']['X']['max_turns'] += 1
            with self.assertRaisesRegex(ValueError, 'not the WP18 X fixture'):
                kit.validate_wp18_fixtures(inputs, root)

    def test_committed_wp18_leaves_bind_the_committed_fixtures(self):
        # WP18 filled from the measurement Mac's fixtures (aaee4b2d2).
        inputs = kit.read_inputs(ROOT)
        kit.validate_wp18_fixtures(inputs, ROOT)
        self.assertEqual({arm: inputs['WP18'][arm]['token_fixture_sha256'] for arm in ('X', 'Y')},
                         {'X': '9dac183dc113275c799f339f827be3ab1e332f4685b2e4b6b0da9466d6dc658f',
                          'Y': 'f17a5a0f52921b52d67216e6b0bfa86cb3f96ebd143d6e39a4c210ba81420dac'})
        self.assertEqual({arm: inputs['WP18'][arm]['max_turns'] for arm in ('X', 'Y')}, {'X': 12, 'Y': 12})

    def test_w1_readiness_requires_the_fixtures(self):
        with patch.object(kit, 'require_ready'), patch.object(kit, 'require_sizing'), \
                patch.object(kit, 'read_inputs', return_value=ready_inputs()[0]), \
                self.assertRaisesRegex(ValueError, 'WP18.X.token_fixture_sha256 does not match'):
            kit.require_w1_ready(ROOT)


class W1HighPowerTests(unittest.TestCase):
    """Lead ruling R5-6: W1 under an adopted High Power, end to end with fake sudo/pmset."""

    def setUp(self):
        # Lead ruling R6-7: the marker is host-level; a private host per test.
        from joulewise.align.apple import powermode
        host = tempfile.TemporaryDirectory()
        self.addCleanup(host.cleanup)
        env = patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(Path(host.name) / 'host-power')})
        env.start()
        self.addCleanup(env.stop)

    def install(self, tmp, ac_powermode, *, gate_status='pass', start_mode=0):
        from joulewise.align.apple import powermode
        measurement = Path(tmp) / 'm'
        (measurement / kit.KIT).mkdir(parents=True, exist_ok=True)
        (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(
            {'runtime_requirements': {'ac_powermode': ac_powermode}}))
        session_root = Path(tmp) / 's'
        (session_root / 'staging').mkdir(parents=True, exist_ok=True)
        (session_root / 'session.json').write_text(json.dumps(
            {'measurement_root': str(measurement), 'inputs': {'custody_root': str(Path(tmp) / 'custody')},
             'plan_path': str(Path(tmp) / 'custody/night_plan.json')}))
        self.marker = Path(powermode.host_marker_path())
        self.host = FakeArmHost(mode=start_mode, marker=self.marker)
        config = W1DiskGateTests.config(self, tmp)
        with patch.object(kit, 'require_w1_ready'), \
                patch.object(pilot, 'install', return_value={'exit_code': 0}) as install:
            try:
                session.install(session_root, runner=self.host, volume_runner=self.host, w1_disk_config=config,
                                disk_gate=lambda c: {'status': gate_status, 'offloads': []})
            finally:
                self.called = install.called
        return session_root

    def test_adopted_high_power_is_set_with_the_marker_and_the_arm_admits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.install(tmp, 2)
            self.assertTrue(self.called)
            self.assertEqual(self.host.mode, 2)
            self.assertTrue(self.marker.exists())        # owed to the night's close
            record = json.loads((root / 'staging/v4-arm-001.json').read_text())
            self.assertTrue(record['admitted'])
            self.assertEqual(record['ac_powermode']['observed'], 2)
            self.assertTrue(record['high_power_enter']['ok'])
            self.assertNotIn(('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '0'), self.host.calls)

    def test_a_refused_high_power_arm_restores_automatic_and_removes_the_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'W1 disk gate refused'):
                root = self.install(tmp, 2, gate_status='fail')
            self.assertFalse(self.called)
            self.assertEqual(self.host.mode, 0)
            self.assertFalse(self.marker.exists())
            [path] = (Path(tmp) / 's/staging').glob('v4-arm-restore-*.json')
            self.assertTrue(json.loads(path.read_text())['ok'])

    def test_a_failure_writing_the_arm_record_still_restores_automatic(self):
        # Sol critique of R5-6: the mode change is protected up to the handoff.
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(session, 'arm_checks', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError, 'disk full'):
                self.install(tmp, 2)
            self.assertEqual(self.host.mode, 0)
            self.assertFalse(self.marker.exists())

    def test_a_signal_inside_the_high_power_entry_still_restores_automatic(self):
        # Round-5 executing review (Sol critic F4): enter_high_power ran before
        # the restoring try, so a first SIGINT after pmset applied 2 (here at
        # the read-back) escaped with the host at 2 and the W1 marker kept.
        with tempfile.TemporaryDirectory() as tmp:
            original = FakeArmHost.__call__
            state = {'armed': False}

            def interrupted(host, argv):
                result = original(host, argv)
                if tuple(argv) == ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2'):
                    state['armed'] = True
                elif state['armed'] and tuple(argv)[:3] == ('/usr/bin/pmset', '-g', 'custom'):
                    state['armed'] = False
                    raise KeyboardInterrupt('SIGINT during the High Power read-back')
                return result
            with patch.object(FakeArmHost, '__call__', interrupted), self.assertRaises(KeyboardInterrupt):
                self.install(tmp, 2)
            self.assertFalse(self.called)
            self.assertEqual(self.host.mode, 0)
            self.assertFalse(self.marker.exists())

    def test_a_terminal_or_installed_session_never_sets_high_power(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.install(tmp, 2)                       # first arm: host at 2, marker present
            state = json.loads((Path(tmp) / 's/session.json').read_text())
            state['install'] = {'exit_code': 0}
            (Path(tmp) / 's/session.json').write_text(json.dumps(state))
            sets = self.host.calls.count(('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2'))
            host = self.host
            measurement = Path(tmp) / 'm'
            with patch.object(kit, 'require_w1_ready'), patch.object(pilot, 'install'):
                session.install(Path(tmp) / 's', runner=host, volume_runner=host,
                                w1_disk_config=W1DiskGateTests.config(self, tmp),
                                disk_gate=lambda c: {'status': 'pass', 'offloads': []})
            self.assertEqual(host.calls.count(('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2')), sets)
            custody = Path(tmp) / 'custody'
            (custody / 'night').mkdir(parents=True)
            (custody / 'night/result.json').write_text('{}')
            state['inputs'] = {'custody_root': str(custody)}
            (Path(tmp) / 's/session.json').write_text(json.dumps(state))
            with patch.object(kit, 'require_w1_ready'), self.assertRaisesRegex(ValueError, 'session is terminal'):
                session.install(Path(tmp) / 's', runner=host, volume_runner=host)
            self.assertEqual(host.calls.count(('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2')), sets)

    def test_an_r1_crash_marker_is_never_taken_for_the_w1_marker(self):
        from joulewise.align.apple import powermode
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / '.align-r1-high-power'
            marker.write_text('high-power restoration required\n')      # the R1 chain's text
            host = FakeArmHost(mode=2)
            refused = powermode.admit_ac_powermode(2, marker=marker, runner=host)
            self.assertFalse(refused['admitted'])                        # restored, then 0 != 2
            self.assertFalse(marker.exists())
            marker.write_text('high-power restoration required\n')
            host = FakeArmHost(mode=2, marker=marker)
            entered = powermode.enter_high_power(marker, runner=host)
            self.assertTrue(entered['ok'])
            self.assertTrue(entered['prior_marker_restore']['ok'])       # the owed restore ran first
            self.assertTrue(powermode.w1_marker(marker))

    def test_automatic_series_never_sets_high_power(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.install(tmp, 0)
            self.assertTrue(self.called)
            self.assertNotIn(('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2'), self.host.calls)
            self.assertFalse(self.marker.exists())

    def test_admission_keeps_the_marker_only_when_the_plan_declares_two(self):
        from joulewise.align.apple import powermode
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / '.align-r1-high-power'
            marker.write_text(powermode.W1_MARKER_TAG + '\n')
            host = FakeArmHost(mode=2)
            admitted = powermode.admit_ac_powermode(2, marker=marker, runner=host)
            self.assertTrue(admitted['admitted'])
            self.assertTrue(marker.exists())
            self.assertEqual(host.mode, 2)
            refused = powermode.admit_ac_powermode(0, marker=None, runner=host)
            self.assertFalse(refused['admitted'])        # 2 is never admitted under a plan of 0
            restored = powermode.admit_ac_powermode(0, marker=marker, runner=host)
            self.assertTrue(restored['admitted'])
            self.assertFalse(marker.exists())
            self.assertEqual(host.mode, 0)
            self.assertFalse(powermode.admit_ac_powermode(2, marker=None, runner=host)['admitted'])

    def test_prepare_declares_the_series_powermode_in_the_night_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            measurement = Path(tmp)
            (measurement / kit.KIT).mkdir(parents=True)
            (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(
                {'runtime_requirements': {'ac_powermode': 2}}))
            with patch.object(kit, 'generate'), patch.object(pilot.h, 'prepare', return_value='ok') as prepare:
                session.prepare(measurement, Path(tmp) / 'session')
            self.assertEqual(prepare.call_args.kwargs['ac_powermode'], 2)


class W1DiskGateTests(unittest.TestCase):
    """W1 blocker 1: w1_disk_gate was never called on the W1 arm path."""

    def install(self, tmp, **kwargs):
        measurement = Path(tmp) / 'm'
        plan = {'runtime_requirements': {'ac_powermode': 0}}
        (measurement / kit.KIT).mkdir(parents=True, exist_ok=True)
        (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(plan))
        session_root = Path(tmp) / 's'
        (session_root / 'staging').mkdir(parents=True, exist_ok=True)
        (session_root / 'session.json').write_text(json.dumps({'measurement_root': str(measurement)}))
        with patch.object(kit, 'require_w1_ready'), patch.object(pilot, 'install') as install:
            try:
                host = FakeArmHost(mode=0)
                session.install(session_root, runner=host, volume_runner=host, **kwargs)
            finally:
                self.called = install.called
        return session_root

    def config(self, tmp):
        path = Path(tmp) / 'r0.json'
        config = json.loads((ROOT / 'configs/align/v4/r0_desk.json').read_text())
        config['disk_path'] = str(Path(tmp).resolve())   # Sol w1rev: never stat the home directory
        config['offloads'] = [{'label': 'pilot10', 'inventory': '/x/pilot10.json', 'destination': '/x/pilot10'}]
        path.write_text(json.dumps(config))
        return path

    def test_arm_without_a_disk_config_is_refused_before_the_installer(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'W1 arm requires --w1-disk-config'):
                self.install(tmp)
            self.assertFalse(self.called)

    def test_a_failing_gate_refuses_the_arm_and_the_real_gate_is_the_default(self):
        seen = []
        def failing(config):
            seen.append(config)
            return {'status': 'fail', 'free_bytes_after_present_weights': 70_000_000_000,
                    'required_free_bytes_after_r0': 80_000_000_000,
                    'offloads': [{'label': 'pilot10', 'pass': False, 'error': 'FileNotFoundError'}]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'W1 disk gate refused the arm.*pilot10'):
                self.install(tmp, w1_disk_config=self.config(tmp), disk_gate=failing)
            self.assertFalse(self.called)
            self.assertEqual(seen[0]['offloads'][0]['label'], 'pilot10')
            # Without an injected gate the real r0_host.w1_disk_gate runs: the
            # configured offload does not exist here, so the arm is refused.
            with self.assertRaisesRegex(ValueError, 'W1 disk gate refused the arm'):
                self.install(tmp, w1_disk_config=self.config(tmp))
            self.assertFalse(self.called)

    def test_a_passing_gate_is_recorded_and_the_installer_runs(self):
        receipt = {'status': 'pass', 'purpose': 'w1_arm_gate', 'offloads': []}
        with tempfile.TemporaryDirectory() as tmp:
            session_root = self.install(tmp, w1_disk_config=self.config(tmp), disk_gate=lambda c: receipt)
            self.assertTrue(self.called)
            self.assertEqual(json.loads((session_root / 'staging/w1_disk_gate.json').read_text()), receipt)

    def test_cli_install_requires_and_forwards_the_disk_config(self):
        with patch.object(session, 'install') as install, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                session.main(['install', '--session-root', 's'])
            install.assert_not_called()
        seen = {}
        def fake(session_root, **kwargs):
            seen.update(kwargs, session_root=session_root)
        with patch.object(session, 'install', fake):
            self.assertEqual(pilot.main(['install', '--session-root', 's', '--w1-disk-config', '/c.json'],
                                        install_fn=session.install, install_options=(
                                            ('--w1-disk-config', dict(type=Path, required=True)),)), 0)
        self.assertEqual(seen, {'session_root': Path('s'), 'w1_disk_config': Path('/c.json')})
        seen.clear()
        with patch.object(session, 'install', fake):
            self.assertEqual(session.main(['install', '--session-root', 's', '--w1-disk-config', '/c.json']), 0)
        self.assertEqual(seen, {'session_root': Path('s'), 'w1_disk_config': Path('/c.json')})


if __name__ == '__main__':
    unittest.main()
