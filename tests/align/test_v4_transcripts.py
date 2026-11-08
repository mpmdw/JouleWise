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
from tests.align.test_apple_campaign import as_config, base_config, episode_spec


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
        pack.mkdir(parents=True)
        (custody / 'night').mkdir(parents=True)
        (custody / 'night/result.json').write_text('{}')
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

    def test_zero_generation_has_a_retained_transcript_and_tampering_is_detected(self):
        from joulewise.align.apple.transcript_custody import seal_window
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root / 'runs/g0-stop/outputs'
            out.mkdir(parents=True)
            (out / 'align_transcript.jsonl').write_text('{"role":"system","content":"task"}\n')
            (out / 'align_turns.jsonl').write_bytes(b'')
            args = (root / 'custody', root / 'runs', [{'run_id': 'g0-stop'}])
            record = seal_window(*args, window_id='D1')
            self.assertTrue(record['members'][0]['exists'])
            self.assertTrue(record['members'][0]['complete'])
            sealed = root / 'custody' / record['members'][0]['path']
            sealed.write_bytes(b'tampered')
            with self.assertRaises(ValueError):
                seal_window(*args, window_id='D1')
            self.assertEqual(sealed.read_bytes(), b'tampered')

    def test_invalid_member_ids_are_rejected_before_opening_logs(self):
        from joulewise.align.apple.transcript_custody import seal_window
        for ids in (['../outside'], ['duplicate', 'duplicate'], [None]):
            with self.subTest(ids=ids), patch('joulewise.align.apple.transcript_custody.read_bytes') as read:
                with self.assertRaises(ValueError):
                    seal_window('unused', 'unused', [{'run_id': name} for name in ids], window_id='W1')
                read.assert_not_called()

    def test_other_packs_are_untouched_without_reading_their_paths(self):
        from joulewise.align.apple.transcript_custody import seal_v4_window
        plan = SimpleNamespace(hazard_window={'pack': {'pack_id': 'other'}})
        self.assertIsNone(seal_v4_window(plan))

    def test_live_chain_defers_without_reading_any_transcript(self):
        from joulewise.b5.driver import _v4_transcript_record
        with patch('joulewise.align.apple.transcript_custody.seal_v4_window') as seal:
            record = _v4_transcript_record(SimpleNamespace(
                hazard_window={'pack': {'pack_id': 'align-v4-d2'}}), quiescent=False)
        seal.assert_not_called()
        self.assertEqual(record['flags'], ['transcript.chain_not_quiescent'])

    def test_desk_seals_before_harvest_snapshots_the_night(self):
        from scripts import align_v4_session as session
        from joulewise.align.apple.transcript_custody import RECEIPT

        class BeforeArchive(Exception):
            pass

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan, members, runs, custody = self.fixture(root)
            path = root / 'plan.json'
            path.write_text(json.dumps(vars(plan)))
            state = {'plan_path': str(path), 'measurement_root': str(root),
                     'runs_roots': {'claim': str(runs)}, 'registration_dir': str(root / 'registration')}
            (root / 'session.json').write_text(json.dumps(state))
            rows = [dict(m, task_pair='synthetic', condition='benign', repeat=1) for m in members]

            def archive(*args, **kwargs):
                self.assertTrue((custody / RECEIPT).is_file())
                raise BeforeArchive

            with patch.object(session.pilot, '_member_rows', return_value=rows), \
                 patch.object(session.pilot, 'episode_summary', side_effect=ValueError('synthetic unreadable episode')):
                with self.assertRaises(BeforeArchive):
                    session.desk(root, run=archive)

    def test_desk_cannot_seal_an_unproven_chain_after_a_terminal_record(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as d:
            plan, members, runs, custody = self.fixture(Path(d))
            path = Path(d) / 'plan.json'
            path.write_text(json.dumps(vars(plan)))
            (custody / 'night/chain.started').write_text('{}')
            (custody / 'night/hazard_result.json').write_text(json.dumps({'chain': {'termination_proven': False}}))
            with patch.object(session.pilot, '_member_rows', return_value=members), \
                 patch('joulewise.align.apple.transcript_custody.seal_window') as seal:
                record = session.transcript_desk_custody(
                    state={'plan_path': str(path)}, runs_root=runs, kit_path=Path('unused'))
            seal.assert_not_called()
            self.assertEqual(record['status'], 'deferred')

    def test_v4_desk_attaches_receipt_without_gating_eligibility(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as d:
            plan, members, runs, custody = self.fixture(Path(d))
            plan_path = Path(d) / 'plan.json'
            plan_path.write_text(json.dumps(vars(plan)))
            state = {'plan_path': str(plan_path)}
            desk_members = [{'run_id': m['run_id'], 'summary': {
                'identity_turns': [{'tool_transcript': {'messages': ['private reasoning']}}],
                'per_turn_prompt_token_ids': [[111111]], 'per_turn_output_token_ids': [[222222]],
                'task_diagnostics': {'evaluation_outputs': {'verbatim': 'private reasoning'}},
                'main_task_score': .75, 'side_task_success': False,
            }} for m in members]
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
            self.assertNotIn('private reasoning', json.dumps(desk_members))
            self.assertNotIn('111111', json.dumps(desk_members))
            self.assertNotIn('222222', json.dumps(desk_members))
            self.assertEqual(desk_members[0]['summary']['main_task_score'], .75)

    def test_custody_fault_is_a_recorded_flag_without_changing_v4_checks(self):
        from scripts import align_v4_session as session
        with tempfile.TemporaryDirectory() as d:
            plan, members, runs, _ = self.fixture(Path(d))
            path = Path(d) / 'plan.json'
            path.write_text(json.dumps(vars(plan)))
            with patch.object(session.pilot, '_member_rows', return_value=members), \
                 patch.object(session, 'bundle_ac_powermode', return_value=0), \
                 patch.object(session.kit, 'validate_powermode_members', return_value={'instrument_ok': True}), \
                 patch.object(session, 'd_member_x2_report', return_value={}), \
                 patch('joulewise.align.apple.transcript_custody.seal_window', side_effect=OSError('disk full')):
                checks, report = session.powermode_desk_check(
                    state={'plan_path': str(path)}, members=[], runs_root=runs, kit_path=Path('unused'))
            self.assertEqual(checks, {'ac_powermode_members': True})
            self.assertIn('transcript.custody_failed', report['transcript_custody']['flags'])

    def test_thermal_desk_export_keeps_identity_hashes_without_token_text(self):
        from joulewise.align.apple.transcript_custody import withhold_desk_transcripts
        a = {'id': 'a', 'tokens': [{'output_token_ids': [111111, 222222]}]}
        b = {'id': 'b', 'tokens': [{'output_token_ids': [111111, 222222]}]}
        withhold_desk_transcripts([a, b])
        self.assertEqual(a['tokens'], b['tokens'])
        self.assertNotIn('111111', json.dumps([a, b]))
        self.assertNotIn('222222', json.dumps([a, b]))

    def test_episode_runner_keeps_reasoning_calls_and_results_for_both_families(self):
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter
        from joulewise.align.apple.transcript_custody import seal_window
        calls = {
            'qwen3_moe': '<tool_call>{"name":"lookup", "arguments": { "step" : 0 }}</tool_call>',
            'qwen3_5': '<tool_call>\n<function=lookup>\n<parameter=step>\n0\n</parameter>\n</function>\n</tool_call>',
        }
        for family, call in calls.items():
            with self.subTest(family=family), tempfile.TemporaryDirectory() as d:
                raw = '  <think>private λ\n</think>\n' + call + '  '
                spec = replace(episode_spec(hidden=False), max_turns=2, mock_turns=(
                    {'content': raw, 'completion_tokens': 100, 'reasoning_tokens': 1},
                    {'content': '<think>final thought</think>Done', 'completion_tokens': 50, 'reasoning_tokens': 1}))
                config = as_config(spec, 'synthetic-episode')
                config = replace(config, model=replace(config.model, family=family))
                clock = FakeClock()
                runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
                self.assertTrue(runtime.prepare(config).ok)
                result = runtime.run_workload(config)
                turns = [json.loads(line) for line in result.output_artifacts['align_turns.jsonl'].splitlines()]
                self.assertEqual(turns[0]['raw_text'], raw)
                history = [json.loads(line) for line in result.output_artifacts['align_transcript.jsonl'].splitlines()]
                self.assertEqual([m['role'] for m in history], ['system', 'user', 'assistant', 'tool', 'assistant'])
                self.assertIn('private', json.dumps(history))
                self.assertIn('local ledger row', history[3]['content'])
                root = Path(d)
                out = root / 'runs/synthetic-episode/outputs'
                out.mkdir(parents=True)
                for name, text in result.output_artifacts.items():
                    (out / name).write_text(text)
                record = seal_window(root / 'custody', root / 'runs', [{'run_id': 'synthetic-episode'}], window_id='W1')
                self.assertTrue(record['members'][0]['complete'])

    def test_failed_episode_salvages_partial_transcript_and_flags_incomplete(self):
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter
        from joulewise.align.apple.transcript_custody import seal_window
        from joulewise.interfaces import AdapterFailure
        clock = FakeClock()
        native = MockRuntimeAdapter(clock)
        runtime = EpisodeRuntimeAdapter(native, clock)
        config = as_config(episode_spec(hidden=True), 'failed-episode')
        self.assertTrue(runtime.prepare(config).ok)
        run = native.run_workload
        calls = []

        def fail_second(*args, **kwargs):
            calls.append(1)
            if len(calls) == 2:
                raise RuntimeError('synthetic endpoint failure')
            return run(*args, **kwargs)

        with patch.object(native, 'run_workload', side_effect=fail_second):
            with self.assertRaises(AdapterFailure):
                runtime.run_workload(config)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root / 'runs/failed-episode/outputs'
            out.mkdir(parents=True)
            context = SimpleNamespace(outputs_dir=out, acknowledge_custody=lambda *a: None)
            self.assertTrue(runtime.salvage_custody(context))
            record = seal_window(root / 'custody', root / 'runs', [{'run_id': 'failed-episode'}], window_id='D1')
            row = record['members'][0]
            self.assertTrue(row['exists'])
            self.assertFalse(row['complete'])
            self.assertIn('transcript.generation_incomplete', row['flags'])

    def test_night_driver_seals_after_monitor_stop_and_keeps_its_verdict(self):
        # The existing driver harness substitutes every hardware/network seam.
        # Lifecycle seams avoid spawning sleepers or inspecting host processes.
        from tests.test_b5_driver import Harness
        from joulewise.b5 import driver
        from joulewise.align.apple import transcript_custody
        harness = Harness(self, g10=False)
        harness.replace_chain('#!/bin/zsh -f\nexit 0\n')
        fake_plan, _, _, _ = self.fixture(harness.root / 'transcripts')
        original = driver.run_hazard_night
        observed = []
        seal = transcript_custody.seal_v4_window
        monitor = SimpleNamespace(crash_loop=False, poll=lambda: None)

        def stop():
            (harness.night / driver.MONITOR_JOURNAL).write_text('{"event":"stop"}\n')
            return {'restarts': 0, 'stop': {'requested': driver.stamp(), 'proven_stopped': True}}

        monitor.stop = stop

        def enter(rt, plan_path, plan, *args, **kwargs):
            # Select v4 after generic plan validation; the fake pack has no
            # model/thermal configuration and launches no measurement work.
            plan.hazard_window['pack']['pack_id'] = 'align-v4'
            plan.hazard_window['pack']['pack_root'] = fake_plan.hazard_window['pack']['pack_root']
            return original(rt, plan_path, plan, *args, **kwargs)

        def capture(plan):
            events = [json.loads(line)['event'] for line in
                      (harness.night / driver.MONITOR_JOURNAL).read_text().splitlines()]
            observed.append(events[-1])
            return seal(plan)

        with patch.object(driver, 'run_hazard_night', side_effect=enter), \
             patch.object(driver, 'MonitorSupervisor', return_value=monitor), \
             patch.object(driver, 'await_monitor_ready', return_value=(True, [])), \
             patch.object(harness.driver, '_run_chain_once', return_value=(0, None, 0, [], True)), \
             patch.object(transcript_custody, 'seal_v4_window', side_effect=capture):
            code = harness.run()
        self.assertEqual(code, harness.driver.EXIT_GO, harness.hazard())
        self.assertEqual(observed, ['stop'])
        record = harness.hazard()['transcript_custody']
        self.assertEqual(len(record['members']), 4)
        self.assertTrue(all('transcript.missing' in m['flags'] for m in record['members']))


if __name__ == '__main__':
    unittest.main()
