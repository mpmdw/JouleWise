"""Synthetic WP18 extraction only; never opens pilot bundles or model files."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_wp18_fixtures as fixtures

ROOT = Path(__file__).resolve().parents[2]
IDENTITIES = {
    'X': ('align-pilot-v3-episodes-b-e25', 'sabotage', 16, 7655467588542005630),
    'Y': ('align-pilot-v3-episodes-b-e18', 'benign', 14, 8158640411307706161),
}


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


class WP18FixtureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='wp18-', dir=os.environ['TMPDIR'])
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / 'repo'
        self.registration = self.root / 'configs/campaigns/align_v4/registration'
        self.registration.mkdir(parents=True)
        self.inputs_path = self.registration / 'inputs.json'
        self.inputs_raw = (ROOT / 'configs/campaigns/align_v4/registration/inputs.json').read_bytes()
        self.inputs_path.write_bytes(self.inputs_raw)
        self.paths = {arm: self.directory / f'{arm}-align_turns.jsonl' for arm in IDENTITIES}
        self.pilot_path = self.directory / 'p7-PILOT.json'
        self.rows = {
            'X': [{'generation': {'prompt_token_ids': [1, 2], 'output_token_ids': [3, 4]}},
                  {'generation': {'prompt_token_ids': [1, 2, 3, 4], 'output_token_ids': [5]}}],
            'Y': [{'generation': {'prompt_token_ids': [6], 'output_token_ids': [7]}},
                  {'generation': {'prompt_token_ids': [6, 7], 'output_token_ids': [8, 9]}},
                  {'generation': {'prompt_token_ids': [6, 7, 8, 9], 'output_token_ids': [10]}}],
        }
        self.members = []
        for arm, (run_id, condition, seed_index, seed) in IDENTITIES.items():
            for index, row in enumerate(self.rows[arm]):
                # The endpoint's row shape: turn index, and the sampler's per-turn
                # seed from the member's episode seed (cold pass LOW-5, R6-8).
                row['turn'] = index
                row['generation']['sampler'] = {'kind': 'categorical',
                                                'per_turn_seed': fixtures.turn_seed(seed, index)}
            generations = [row['generation'] for row in self.rows[arm]]
            self.members.append({
                'run_id': run_id, 'task_pair': 'spam_filter_update', 'condition': condition,
                'excluded': False, 'exclusion_codes': [],
                'summary': {
                    'episode_id': f'synthetic-{arm}', 'seed': seed_index,   # the desk's Episode.seed
                    'task_pair': 'shade/spam_filter_update', 'condition': condition,
                    'per_turn_decode_tokens': [len(g['output_token_ids']) for g in generations],
                    'per_turn_output_token_ids': [g['output_token_ids'][:] for g in generations],
                    'per_turn_prompt_token_ids': [g['prompt_token_ids'][:] for g in generations],
                },
            })
        self.write_sources()

    def write_sources(self):
        for arm, path in self.paths.items():
            path.write_bytes(b''.join(json_bytes(row) for row in self.rows[arm]))
        self.pilot_path.write_bytes(json_bytes({'members': self.members}))

    def run_tool(self, *, check=False):
        return fixtures.write_fixtures(self.root, self.paths['X'], self.paths['Y'], self.pilot_path, check=check)

    def snapshot(self):
        return {path.name: path.read_bytes() for path in self.registration.iterdir()}

    def assert_refused(self, message):
        before = self.snapshot()
        sources = {p: p.read_bytes() for p in (*self.paths.values(), self.pilot_path)}
        with self.assertRaisesRegex(ValueError, message):
            self.run_tool()
        self.assertEqual(self.snapshot(), before, 'refusal must leave no outputs or temporary files')
        self.assertEqual({p: p.read_bytes() for p in sources}, sources)

    def cli_args(self):
        return ['--x-turns', str(self.paths['X']), '--y-turns', str(self.paths['Y']),
                '--pilot', str(self.pilot_path), '--root', str(self.root)]

    def test_writes_canonical_fixtures_and_ready_leaves(self):
        sources_before = {p: p.read_bytes() for p in (*self.paths.values(), self.pilot_path)}
        with patch.object(fixtures.os, 'replace', wraps=os.replace) as replace:
            results = self.run_tool()
        self.assertEqual(replace.call_count, 3)
        for call in replace.call_args_list:
            temporary, destination = call.args
            self.assertEqual(temporary.parent, destination.parent)
            self.assertFalse(temporary.exists())
        inputs = json.loads(self.inputs_path.read_bytes())
        for arm, (run_id, condition, seed_index, seed) in IDENTITIES.items():
            raw = (self.registration / f'wp18_{arm.lower()}_token_ids.json').read_bytes()
            fixture = json.loads(raw)
            count = len(self.rows[arm])
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(raw, json_bytes(fixture))
            self.assertEqual(results[arm], (raw, count, digest))
            self.assertEqual(fixture, {
                'schema': 'joulewise.align_v4.wp18_token_fixture.v1',
                'arm': arm, 'run_id': run_id, 'source': 'pilot-7',
                'task_pair': 'spam_filter_update', 'condition': condition,
                'seed_index': seed_index, 'episode_seed': seed, 'max_turns': count,
                'turns': [dict(turn=i, **{f: row['generation'][f] for f in fixtures.TOKEN_FIELDS})
                          for i, row in enumerate(self.rows[arm])],
                'sources': {
                    'align_turns_jsonl_sha256': hashlib.sha256(self.paths[arm].read_bytes()).hexdigest(),
                    'p7_pilot_json_sha256': hashlib.sha256(self.pilot_path.read_bytes()).hexdigest(),
                },
            })
            ref = inputs['WP18'][arm]
            self.assertEqual(ref, {'max_turns': count, 'token_fixture_sha256': digest})
            # The WP18 portion of align_v4_kit.require_ready; other owners stay pending.
            self.assertIs(type(ref['max_turns']), int)
            self.assertGreater(ref['max_turns'], 0)
            self.assertRegex(ref['token_fixture_sha256'], r'\A[0-9a-f]{64}\Z')
            self.assertEqual(fixtures.build_fixture(arm, self.paths[arm].read_bytes(),
                                                    self.pilot_path.read_bytes()), results[arm])
        original = json.loads(self.inputs_raw)
        for arm in IDENTITIES:
            for key in ('max_turns', 'token_fixture_sha256'):
                inputs['WP18'][arm][key] = original['WP18'][arm][key]
        self.assertEqual(inputs, original)
        self.assertEqual({p: p.read_bytes() for p in sources_before}, sources_before)

    def test_preserves_current_inputs_format_and_other_bytes(self):
        self.run_tool()
        text = self.inputs_path.read_text()
        text = re.sub(r'("max_turns"\s*:\s*)\d+', r'\g<1>null', text)
        text = re.sub(r'("token_fixture_sha256"\s*:\s*)"[0-9a-f]{64}"', r'\g<1>null', text)
        self.assertEqual(text.encode('utf-8'), self.inputs_raw)

    def test_preserves_kit_raw_json_format_and_extra_keys(self):
        inputs = json.loads(self.inputs_raw)
        inputs['WP18']['X']['operator_note'] = {'keep': ['é', 1, False]}
        inputs['WP18']['extra'] = {'max_turns': 12, 'token_fixture_sha256': 'unrelated'}
        inputs['other'] = {'X': {'max_turns': 999}}
        def kit_json(value):
            return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')
        self.inputs_path.write_bytes(kit_json(inputs))
        results = self.run_tool()
        for arm, (_, count, digest) in results.items():
            inputs['WP18'][arm].update(max_turns=count, token_fixture_sha256=digest)
        self.assertEqual(self.inputs_path.read_bytes(), kit_json(inputs))

    def test_optional_summary_ids_and_identity_fallbacks(self):
        for member in self.members:
            for key in ('per_turn_prompt_token_ids', 'per_turn_output_token_ids', 'task_pair', 'condition'):
                member['summary'].pop(key)
            member['task_pair'] = 'shade/spam_filter_update'
        self.write_sources()
        self.run_tool()
        self.run_tool(check=True)

    def test_cli_write_check_and_tamper_refusal_write_nothing(self):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(fixtures.main(self.cli_args()), 0)
        self.assertIn('max_turns=2', output.getvalue())
        self.assertIn('scripts/align_v4_kit.py', output.getvalue())
        self.assertIn('identity_pins.json', output.getvalue())
        before = self.snapshot()
        with patch.object(fixtures.os, 'replace', side_effect=AssertionError('check must not write')):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(fixtures.main(self.cli_args() + ['--check']), 0)
        self.assertEqual(self.snapshot(), before)
        path = self.registration / 'wp18_x_token_ids.json'
        path.write_bytes(path.read_bytes() + b' ')
        tampered = self.snapshot()
        with redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as refused:
                fixtures.main(self.cli_args() + ['--check'])
        self.assertEqual(refused.exception.code, 1)
        self.assertIn('fixture differs', error.getvalue())
        self.assertEqual(self.snapshot(), tampered)

    def test_check_refuses_missing_fixture_or_wrong_input_leaves(self):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'fixture differs or is missing'):
            self.run_tool(check=True)
        self.assertEqual(self.snapshot(), before)
        self.run_tool()
        valid_inputs = self.inputs_path.read_bytes()
        for key, value in (('max_turns', 12), ('max_turns', 2.0), ('token_fixture_sha256', '0' * 64)):
            with self.subTest(key=key, value=value):
                inputs = json.loads(valid_inputs)
                inputs['WP18']['X'][key] = value
                self.inputs_path.write_bytes(json_bytes(inputs))
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, f'WP18.X.{key} differs'):
                    self.run_tool(check=True)
                self.assertEqual(self.snapshot(), before)

    def test_refuses_invalid_rows_for_either_arm_without_writes(self):
        for arm in IDENTITIES:
            for raw, message in ((b'', 'at least one'), (b'{broken\n', 'invalid JSON'),
                                 (b'null\n', 'generation'), (b'{}\n', 'generation'),
                                 (b'{"generation":null}\n', 'generation'),
                                 (b'\n', 'invalid JSON')):
                with self.subTest(arm=arm, raw=raw):
                    self.write_sources()
                    self.paths[arm].write_bytes(raw)
                    self.assert_refused(message)
            for field in ('prompt_token_ids', 'output_token_ids'):
                for value in (None, [], [True], [1, False], [1.0], ['1'], 1, {}):
                    with self.subTest(arm=arm, field=field, value=value):
                        self.write_sources()
                        rows = deepcopy(self.rows[arm])
                        rows[-1]['generation'][field] = value
                        self.paths[arm].write_bytes(b''.join(json_bytes(row) for row in rows))
                        self.assert_refused(field)
                with self.subTest(arm=arm, missing=field):
                    self.write_sources()
                    rows = deepcopy(self.rows[arm])
                    rows[-1]['generation'].pop(field)
                    self.paths[arm].write_bytes(b''.join(json_bytes(row) for row in rows))
                    self.assert_refused(field)

    def test_refuses_invalid_pilot_members_without_writes(self):
        cases = [
            ('missing member', lambda ms, i: ms.pop(i), 'exactly one member'),
            ('duplicate run_id', lambda ms, i: ms.append(deepcopy(ms[i])), 'exactly one member'),
            ('excluded', lambda ms, i: ms[i].update(excluded=True), 'not excluded'),
            ('missing summary', lambda ms, i: ms[i].pop('summary'), 'have a summary'),
            ('null summary', lambda ms, i: ms[i].update(summary=None), 'have a summary'),
            ('wrong seed', lambda ms, i: ms[i]['summary'].update(seed=1), 'summary seed'),
            ('missing seed', lambda ms, i: ms[i]['summary'].pop('seed'), 'summary seed'),
            ('wrong pair', lambda ms, i: ms[i]['summary'].update(task_pair='shade/other'), 'task_pair'),
            ('wrong condition', lambda ms, i: ms[i]['summary'].update(condition='other'), 'condition'),
            ('member conflict', lambda ms, i: ms[i].update(task_pair='other'), 'task_pair'),
            ('no identity', lambda ms, i: (ms[i].pop('task_pair'), ms[i]['summary'].pop('task_pair')), 'task_pair'),
            ('summary excluded', lambda ms, i: ms[i]['summary'].update(excluded=True), 'summary is excluded'),
            ('turn count', lambda ms, i: ms[i]['summary']['per_turn_decode_tokens'].pop(), 'turn count'),
            ('no counts', lambda ms, i: ms[i]['summary'].pop('per_turn_decode_tokens'), 'turn count'),
            ('decode count', lambda ms, i: ms[i]['summary']['per_turn_decode_tokens'].__setitem__(0, 99), 'output count'),
            ('bool count', lambda ms, i: ms[i]['summary']['per_turn_decode_tokens'].__setitem__(0, True), 'output count'),
        ]
        for field in ('per_turn_output_token_ids', 'per_turn_prompt_token_ids'):
            cases.extend([
                (field, lambda ms, i, f=field: ms[i]['summary'][f][0].append(999), field),
                (field + ' length', lambda ms, i, f=field: ms[i]['summary'][f].pop(), field),
                (field + ' null', lambda ms, i, f=field: ms[i]['summary'].update({f: None}), field),
                (field + ' bool', lambda ms, i, f=field: ms[i]['summary'][f][0].__setitem__(0, True), field),
            ])
        valid = deepcopy(self.members)
        for index, arm in enumerate(IDENTITIES):
            for name, mutate, message in cases:
                with self.subTest(arm=arm, case=name):
                    self.members = deepcopy(valid)
                    mutate(self.members, index)
                    self.write_sources()
                    self.assert_refused(message)

    def test_refuses_malformed_pilot_json_without_writes(self):
        for raw in (b'{broken', b'null', b'{}', b'{"members":null}'):
            with self.subTest(raw=raw):
                self.pilot_path.write_bytes(raw)
                self.assert_refused('invalid JSON|members must be a list')

    def test_same_file_or_identical_bytes_refuse_without_writes(self):
        self.paths['Y'].write_bytes(self.paths['X'].read_bytes())
        self.assert_refused('different SHA-256')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'different SHA-256'):
            fixtures.write_fixtures(self.root, self.paths['X'], self.paths['X'], self.pilot_path)
        self.assertEqual(self.snapshot(), before)

    def test_refusal_preserves_existing_outputs(self):
        self.run_tool()
        self.members[1]['summary']['seed'] = 1
        self.write_sources()
        self.assert_refused('summary seed')


if __name__ == '__main__':
    unittest.main()
