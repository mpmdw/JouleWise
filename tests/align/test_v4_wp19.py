"""Exercise the WP19 writer and registration path with synthetic inputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import DEFAULT, patch

from joulewise.align.apple import thermal_desk, v4_registration as reg
from joulewise.align.apple.sampling import episode_seed, turn_seed
from scripts import align_v4_kit as kit, align_v4_thermal_desk as desk, align_v4_wp19 as writer
from tests.git_fixture import init_git_fixture


class WP19Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.directory = self.root / reg.REGISTRATION
        self.output = self.directory / 'wp19_receipt.json'
        self.live = self.root / 'turns.jsonl'
        self.tokenizer = self.root / 'tokenizer'
        self.tokenizer.mkdir()
        for filename in ('tokenizer.json', 'tokenizer_config.json'):
            self.write_json(self.tokenizer / filename, {})
        self.turns = [{'turn': i, 'prompt_token_ids': [i + 1], 'output_token_ids': [i + 2]}
                      for i in range(12)]
        fixture = {'turns': self.turns,
                   'sources': {'align_turns_jsonl_sha256': 'a' * 64, 'p7_pilot_json_sha256': 'b' * 64}}
        for path in kit.WP18_FIXTURES.values():
            self.write_json(self.root / path, fixture)
        self.write_json(self.root / 'config.json', {})
        self.write_json(self.root / kit.KIT / 'collection_plan.json', {
            'runtime_requirements': {'km003c': kit.km003c.REQUIREMENT},
            'members': [{'role': arm + '-G', 'config_path': 'config.json'} for arm in ('X', 'Y')],
        })
        self.argv = ['--root', str(self.root), '--tokenizer', str(self.tokenizer),
                     '--x-g-turns', str(self.live), '--output', str(self.output)]
        self.enterContext(patch.dict(sys.modules, {
            'transformers': SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *a, **k: object())),
        }))
        config = SimpleNamespace(workload_profile=SimpleNamespace(prompt_text='synthetic'))
        self.enterContext(patch('joulewise.schemas.BenchmarkConfig.from_mapping', return_value=config))
        spec = SimpleNamespace(task_factory='types:SimpleNamespace', task_kwargs={}, condition='benign', seed=16,
                               enable_thinking=True, assistant_history=None, chat_template_kwargs={})
        self.enterContext(patch('joulewise.align.apple.workload.EpisodeSpec.from_text', return_value=spec))
        self.enterContext(patch('joulewise.align.apple.endpoint.MlxEndpoint'))
        self.render = self.enterContext(patch.object(
            writer, 'render_fixture', return_value=[row['prompt_token_ids'] for row in self.turns]))

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def live_rows(self, mismatches=()):
        registered = episode_seed('qwen3-30b-a3b', 'thinking_on', 'shade/spam_filter_update', 16)
        fallback = episode_seed('Qwen3-30B-A3B-4bit', 'thinking_on', 'shade/spam_filter_update', 16)
        return [{'turn': i, 'generation': {
            'prompt_token_ids': row['prompt_token_ids'], 'output_token_ids': row['output_token_ids'],
            'sampler': {'per_turn_seed': turn_seed(fallback if i in mismatches else registered, i)},
        }} for i, row in enumerate(self.turns)]

    def write_turns(self, rows):
        self.live.write_text(''.join(json.dumps(row) + '\n' for row in rows))

    def receipt(self, rows):
        self.write_turns(rows)
        self.assertEqual(writer.main(self.argv), 0)
        return reg.validate_wp19(json.loads(self.output.read_text()))

    def test_registered_seed_preserves_pass(self):
        receipt = self.receipt(self.live_rows())
        self.assertEqual(receipt['verdict'], 'pass')
        self.assertIsNone(receipt['contrast_predeclared'])
        self.assertNotIn('seed_binding', receipt)

    def test_fallback_seed_is_inconclusive_and_nonveto_through_kit_and_desk(self):
        receipt = self.receipt(self.live_rows(range(12)))
        self.assertEqual(receipt['verdict'], 'fail')
        self.assertIs(receipt['live_x_identical'], False)
        self.assertEqual(receipt['seed_binding'], {
            'reason_code': 'wp19.live_xg_seed_binding', 'turns_checked': 12, 'turns_mismatched': 12,
        })
        self.assertEqual(set(receipt), {
            'schema', 'verdict', 'render_all_turns', 'live_x_identical', 'live_x_turns_compared',
            'live_x_complete', 'live_source_sha256', 'contrast_predeclared', 'static_proof',
            'source_sha256', 'tokenizer_files_sha256', 'seed_binding',
        })
        self.assertEqual(receipt['live_source_sha256'], reg.digest(self.live.read_bytes()))

        # Keep the real Git binding and readiness/desk consumers for WP19.
        # Unrelated registration artifacts and checks use synthetic stand-ins.
        relative = self.output.relative_to(self.root).as_posix()
        self.assertIn(relative, reg.ARTIFACTS)
        gates = {}
        for stage in ('A', 'B'):
            path = f'docs/align/v4/stage-{stage}.md'
            self.write_json(self.root / path, 'synthetic gate')
            gates[stage] = {'verdict': 'ADMIT', 'path': path, 'sha256': reg.digest((self.root / path).read_bytes())}
        init_git_fixture(self.root, '-q')

        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

        git('add', '--', relative, *(gate['path'] for gate in gates.values()))
        git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
            'commit', '-qm', 'Bind synthetic WP19 receipt')
        self.write_json(self.directory / 'registration_receipt.json', {
            'schema': reg.RECEIPT_SCHEMA, 'status': 'registered', 'commit': git('rev-parse', 'HEAD'),
            'artifacts': {relative: reg.digest(self.output.read_bytes())},
            'rulings': {str(n): 'installed' for n in reg.RULINGS}, 'gates': gates,
            'lead_signature': 'lead: synthetic-test 2026-11-27',
        })
        self.write_json(self.directory / 'r1_slots.json', {})
        self.write_json(self.directory / 'u3_bar.json', {})
        self.write_json(self.directory / 'battery_window_policy.json', {})
        with patch.object(reg, 'ARTIFACTS', (relative,)), \
             patch.multiple(reg, verify_r1_executed_sources=DEFAULT, validate_u3=DEFAULT), \
             patch('joulewise.align.apple.v4_battery.validate_policy'), \
             patch.multiple(kit, check_w1_record_keys=DEFAULT, read_inputs=DEFAULT, pending_inputs=DEFAULT,
                            require_ready=DEFAULT, read_r1_slots=DEFAULT, read_r1_planning_release=DEFAULT,
                            require_sizing=DEFAULT, validate_wp18_fixtures=DEFAULT) as kit_gates:
            kit_gates['pending_inputs'].return_value = ['WP11.identity_unit']
            kit.require_w1_ready(self.root)
            _, desk_receipt = desk.registration_evidence(self.directory)
            self.assertEqual(desk_receipt, receipt)
            reason = desk.contrast_predeclaration(desk_receipt, {})
            result = thermal_desk.deciding_experiment([], v4=True, predeclared=reason)
            self.assertEqual(result['verdict'], 'INCONCLUSIVE')
            self.assertEqual(result['reason'], 'INCONCLUSIVE: identity broken')
            self.output.write_bytes(self.output.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                kit.require_w1_ready(self.root)

    def test_partial_seed_mismatch_counts_and_validates_diagnostics(self):
        receipt = self.receipt(self.live_rows((1, 11)))
        self.assertEqual(receipt['verdict'], 'fail')
        diagnostic = receipt['seed_binding']
        self.assertEqual(diagnostic['turns_checked'], 12)
        self.assertEqual(diagnostic['turns_mismatched'], 2)
        for invalid in ({'reason_code': 'other'}, {'turns_checked': 11}, {'turns_mismatched': True},
                        {'turns_mismatched': 0}, {'turns_mismatched': 13}, {'per_turn_seed': 1}):
            with self.subTest(fields=tuple(invalid)), self.assertRaises(ValueError):
                reg.validate_wp19({**receipt, 'seed_binding': {**diagnostic, **invalid}})
        for invalid in ({'verdict': 'pass'}, {'live_x_complete': False}, {'live_x_identical': True},
                        {'render_all_turns': {'X': True, 'Y': False}}):
            with self.subTest(fields=tuple(invalid)), self.assertRaises(ValueError):
                reg.validate_wp19({**receipt, **invalid})

    def test_missing_tokenizer_and_unreadable_turns_refuse_without_receipt(self):
        argv = self.argv.copy()
        argv[3] = str(self.root / 'missing-tokenizer')
        with self.assertRaisesRegex(ValueError, 'tokenizer must be a local directory'):
            writer.main(argv)
        with self.assertRaises(FileNotFoundError):
            writer.main(self.argv)
        self.live.write_text('{')
        with self.assertRaises(json.JSONDecodeError):
            writer.main(self.argv)
        rows = self.live_rows((0,))
        rows[-1]['turn'] = 0
        self.write_turns(rows)
        with self.assertRaisesRegex(ValueError, 'turn/seed binding failed'):
            writer.main(self.argv)
        rows = self.live_rows((0,))
        rows[-1]['generation']['sampler'].clear()
        self.write_turns(rows)
        with self.assertRaises(KeyError):
            writer.main(self.argv)
        self.assertFalse(self.output.exists())

    def test_incomplete_coverage_and_render_failures_keep_existing_dispositions(self):
        self.write_turns(self.live_rows((0,))[:-1])
        with self.assertRaisesRegex(ValueError, 'turn/seed binding failed'):
            writer.main(self.argv)
        self.assertFalse(self.output.exists())
        receipt = self.receipt(self.live_rows()[:-1])
        self.assertEqual(receipt['verdict'], 'fail')
        self.assertFalse(receipt['live_x_complete'])
        self.assertNotIn('seed_binding', receipt)
        self.output.unlink()

        self.write_turns(self.live_rows((0,)))
        self.render.return_value = []
        with self.assertRaisesRegex(ValueError, 'turn/seed binding failed'):
            writer.main(self.argv)
        self.render.side_effect = RuntimeError('synthetic render failure')
        with self.assertRaisesRegex(RuntimeError, 'synthetic render failure'):
            writer.main(self.argv)
        self.assertFalse(self.output.exists())
        self.render.side_effect = None
        receipt = self.receipt(self.live_rows())
        self.assertEqual(receipt['verdict'], 'fail')
        self.assertEqual(receipt['render_all_turns'], {'X': False, 'Y': False})
        self.assertNotIn('seed_binding', receipt)
