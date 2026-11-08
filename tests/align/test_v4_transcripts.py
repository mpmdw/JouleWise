"""Transcript custody with synthetic episodes only; no model or study-data reads."""
from __future__ import annotations

import base64
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.interfaces import ChatMessage
from joulewise.clock import FakeClock
from tests.align.test_apple_campaign import base_config


class TranscriptTests(unittest.TestCase):
    def test_endpoint_keeps_exact_raw_completion_in_turn_log(self):
        # Parsing/history formatting may normalise arguments or trim a call;
        # neither is a lossless source of the generated completion.
        raw = '  <think>private λ\n</think>\n<tool_call>{"name":"lookup", "arguments": { "step" : 0 }}</tool_call>  '
        clock = FakeClock()
        runtime = MockRuntimeAdapter(clock)
        config = base_config()
        runtime.prepare(config)
        endpoint = MlxEndpoint(runtime, config, clock, episode_domain='synthetic',
                               mock_turns=({'content': raw, 'completion_tokens': 100,
                                            'reasoning_tokens': 10},))
        result = endpoint.chat([ChatMessage('user', 'synthetic')], tools=(),
                               max_tokens=200, temperature=0, seed=1)
        self.assertEqual(result.raw_usage['raw_text'], raw)
        self.assertEqual(endpoint.turn_provenance[0]['raw_text'], raw)

    def fixture(self, root, *, pack_id='align-v4'):
        pack, runs, custody = root / 'pack', root / 'runs', root / 'custody'
        pack.mkdir()
        members = [{'run_id': name, 'ordinal': i + 1} for i, name in enumerate(
            ('anchor', 'D-benign', 'D-sabotage', 'not-run'))]
        (pack / 'collection_plan.json').write_text(json.dumps({'members': members}))
        for member in members[:-1]:
            out = runs / member['run_id'] / 'outputs'
            out.mkdir(parents=True)
            history = [dict(role='system', content='private task'), dict(role='user', content='query'),
                       dict(role='assistant', content='answer', reasoning_content='private λ',
                            tool_calls=[dict(name='lookup', arguments_json=' { "step" : 0 } ')]),
                       dict(role='tool', name='lookup', content='result\nλ')]
            (out / 'align_transcript.jsonl').write_bytes(
                ''.join(json.dumps(m, ensure_ascii=False) + '\r\n' for m in history).encode())
            (out / 'align_turns.jsonl').write_text(json.dumps(
                {'turn': 0, 'raw_text': '<think>private λ</think>answer', 'flags': []}) + '\n')
        plan = SimpleNamespace(plan_id='synthetic-window', custody_root=str(custody),
            hazard_window={'pack': {'pack_id': pack_id, 'pack_root': str(pack)},
                           'runs_roots': {'claim': str(runs)}})
        return plan, members, runs, custody

    def test_every_member_sealed_losslessly_and_public_receipt_has_no_text(self):
        from joulewise.align.apple.transcript_custody import seal_v4_window
        for pack_id in ('align-v4', 'align-v4-d1'):
            with self.subTest(pack=pack_id), tempfile.TemporaryDirectory() as d:
                plan, members, runs, custody = self.fixture(Path(d), pack_id=pack_id)
                record = seal_v4_window(plan)
                self.assertEqual([m['run_id'] for m in record['members']], [m['run_id'] for m in members])
                for row in record['members'][:-1]:
                    self.assertTrue(row['exists'])
                    self.assertTrue(row['complete'])
                    path = custody / row['path']
                    raw = path.read_bytes()
                    self.assertEqual(row['sha256'], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                    payload = json.loads(raw)
                    for name, encoded in payload['files'].items():
                        self.assertEqual(base64.b64decode(encoded), (runs / row['run_id'] / 'outputs' / name).read_bytes())
                missing = record['members'][-1]
                self.assertFalse(missing['exists'])
                self.assertIsNone(missing['sha256'])
                self.assertIn('transcript.missing', missing['flags'])
                self.assertEqual(record['release_after'], 'v5_registration')
                self.assertEqual(record['status'], 'sealed_unscored')
                self.assertNotIn('private', json.dumps(record))
                self.assertNotIn('arguments_json', json.dumps(record))
                self.assertEqual(seal_v4_window(plan), record)

    def test_missing_legacy_and_malformed_logs_are_flags_and_bytes_survive(self):
        from joulewise.align.apple.transcript_custody import seal_v4_window
        with tempfile.TemporaryDirectory() as d:
            plan, _, runs, custody = self.fixture(Path(d))
            (runs / 'anchor/outputs/align_turns.jsonl').unlink()
            (runs / 'D-benign/outputs/align_turns.jsonl').write_text('{"turn":0}\n')
            broken = b'not-json\xff'
            (runs / 'D-sabotage/outputs/align_transcript.jsonl').write_bytes(broken)
            rows = seal_v4_window(plan)['members']
            self.assertIn('transcript.turns_missing', rows[0]['flags'])
            self.assertIn('transcript.raw_completion_missing', rows[1]['flags'])
            self.assertIn('transcript.malformed', rows[2]['flags'])
            self.assertTrue(all(not row['complete'] for row in rows))
            payload = json.loads((custody / rows[2]['path']).read_bytes())
            self.assertEqual(base64.b64decode(payload['files']['align_transcript.jsonl']), broken)

    def test_changed_source_or_seal_cannot_overwrite_first_evidence(self):
        from joulewise.align.apple.transcript_custody import seal_v4_window
        with tempfile.TemporaryDirectory() as d:
            plan, _, runs, custody = self.fixture(Path(d))
            record = seal_v4_window(plan)
            sealed = custody / record['members'][0]['path']
            before = sealed.read_bytes()
            (runs / 'anchor/outputs/align_transcript.jsonl').write_text('changed')
            with self.assertRaises(ValueError):
                seal_v4_window(plan)
            self.assertEqual(sealed.read_bytes(), before)

    def test_other_packs_are_untouched_without_reading_their_paths(self):
        from joulewise.align.apple.transcript_custody import seal_v4_window
        plan = SimpleNamespace(hazard_window={'pack': {'pack_id': 'other'}})
        self.assertIsNone(seal_v4_window(plan))

    def test_v4_desk_attaches_receipt_without_gating_eligibility(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as d:
            plan, members, runs, custody = self.fixture(Path(d))
            plan_path = Path(d) / 'plan.json'
            plan_path.write_text(json.dumps(vars(plan)))
            state = {'plan_path': str(plan_path)}
            desk_members = [{'run_id': m['run_id']} for m in members]
            with patch.object(session.pilot, '_member_rows', return_value=members), \
                 patch.object(session, 'bundle_ac_powermode', return_value=0), \
                 patch.object(session.kit, 'validate_powermode_members', return_value={'instrument_ok': True}), \
                 patch.object(session, 'd_member_x2_report', return_value={}):
                checks, report = session.powermode_desk_check(
                    state=state, members=desk_members, runs_root=runs, kit_path=Path('unused'))
            self.assertEqual(checks, {'ac_powermode_members': True})
            self.assertEqual(report['transcript_custody']['status'], 'sealed_unscored')
            self.assertTrue(desk_members[0]['transcript']['exists'])
            self.assertIn('transcript.missing', desk_members[-1]['transcript']['flags'])


if __name__ == '__main__':
    unittest.main()
