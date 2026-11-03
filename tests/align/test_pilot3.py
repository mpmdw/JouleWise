"""Pilot-3 kit and complete read-only desk on production-shaped synthetic bundles."""
from contextlib import redirect_stdout
from dataclasses import replace
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple.diagnostics import action_diagnostics, phase_reason_counts
from joulewise.align.records import Episode, ToolCall, Turn
from joulewise.clock import FakeClock
from scripts import align_pilot_kit as kit, align_pilot_session as desk, bytes_h_session as h
from tests.align.test_apple_endpoint import run_native_review
from tests.align.test_pilot3_cache import CacheAPI

ROOT = Path(__file__).resolve().parents[2]


class KitTests(unittest.TestCase):
    def test_specs_only_add_cache_control_and_order_is_matched(self):
        old = h.read(ROOT / 'configs/campaigns/align_pilot_v1/collection_plan.json')
        previous = {(m['block'], m['task_pair'], m['condition']): m['spec'] for m in old['members']}
        members = kit.ordered_members()
        self.assertEqual(len(members), 24)
        for member in members:
            spec = json.loads(member['spec'].to_text())
            self.assertEqual(spec.pop('prompt_cache'), 'episode_prefix')
            self.assertEqual(spec, previous[(member['block'], spec['task_kwargs']['task_pair'], spec['condition'])])
        self.assertEqual([m['block'] for m in members], ['A'] * 12 + ['C'] * 12)
        for chunk in (members[:12], members[12:]):
            pairs = [chunk[i]['spec'].task_kwargs['task_pair'] for i in range(0, 12, 2)]
            self.assertEqual(pairs, ['spam_filter_update', 'bank_transfer_2', 'bank_transfer_2',
                                     'spam_filter_update', 'spam_filter_update', 'bank_transfer_2'])
            for pair in set(pairs):
                first = [chunk[i]['spec'].condition for i in range(0, 12, 2) if pairs[i // 2] == pair]
                self.assertNotEqual(first[0], first[1])
                self.assertEqual(first[0], first[2])

    def test_fresh_mac_identity_pins_survive_generate_and_check(self):
        files = kit.build_files(ROOT)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # The composer authenticates resolved paths against this root.
            # Copy its 49 MiB config inputs instead of escaping through symlinks.
            shutil.copytree(ROOT / 'configs', root / 'configs')
            for path, raw in files.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            reg = root / kit.KIT / 'registration'
            pins = h.read(reg / 'identity_pins.json')
            pins['runtime_versions']['mac_observation_preserved'] = 'synthetic receipt sentinel'
            h.write(reg / 'identity_pins.json', pins)
            receipt = h.read(reg / 'local_file_verification.json')
            receipt.pop('inherited_from')
            receipt.pop('inherited_sha256')
            receipt['identity_pins_sha256'] = kit.sha((reg / 'identity_pins.json').read_bytes())
            h.write(reg / 'local_file_verification.json', receipt)
            before = {p.name: p.read_bytes() for p in (reg / 'identity_pins.json', reg / 'model_artifact_inventory.json', reg / 'local_file_verification.json')}
            kit.generate(root, source_root=root)
            kit.generate(root, source_root=root, check=True)
            self.assertEqual(before, {name: (reg / name).read_bytes() for name in before})

    def test_sizing_receipts_replay_exactly_from_the_named_sources(self):
        path = ROOT / kit.KIT / 'registration/derive_sizing.py'
        spec = importlib.util.spec_from_file_location('pilot3_derive_sizing', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        evidence = h.read(path.with_name('sizing_evidence.json'))
        session = Path(evidence['source_session'])
        if not session.is_dir():
            self.skipTest('immutable pilot2 source session is not installed on this host')
        self.assertEqual(module.derive(session), evidence)


class DeskTests(unittest.TestCase):
    def test_i4_requires_two_exact_id_sequences_even_when_counts_match(self):
        summary = {'per_turn_decode_tokens': [2], 'per_turn_context_tokens': [0],
                   'per_turn_prefill_tokens': [3], 'per_turn_hidden_tokens': [0],
                   'per_turn_output_token_ids': [[1, 2]], 'per_turn_prompt_token_ids': [[3, 4, 5]],
                   'flags': [], 'energy': {}}
        member = {'block': 'A', 'task_pair': 'p', 'condition': 'benign', 'summary': summary}
        self.assertEqual(desk.instrument_checks([member])[0]['I4_greedy_repeats_identical_tokens'], 'not_evaluated')
        self.assertTrue(desk.instrument_checks([member, dict(member)])[0]['I4_greedy_repeats_identical_tokens'])
        other = {**member, 'summary': {**summary, 'per_turn_output_token_ids': [[1, 9]]}}
        self.assertFalse(desk.instrument_checks([member, other])[0]['I4_greedy_repeats_identical_tokens'])
        missing = {**member, 'summary': {**summary, 'per_turn_output_token_ids': [None]}}
        self.assertEqual(desk.instrument_checks([member, missing])[0]['I4_greedy_repeats_identical_tokens'], 'not_evaluated')

    def test_read_marking_and_bank_stage_are_separate_observations(self):
        calls = tuple(ToolCall(name, 0, 1, 0, 0, state_changed=changed) for name, changed in (
            ('get_unread_emails', True), ('add_venmo_contact', True), ('add_venmo_contact', False),
            ('send_money_venmo', False), ('send_email', True)))
        episode = Episode('e', 'bank_transfer_2', 'benign', 'm', 'e', 1, 'c', 0, 1,
                          turns=(Turn(0, 0, 1, 0, 0, 0, tool_calls=calls),))
        result = action_diagnostics(episode)
        self.assertEqual(result['state_changing_calls'], 3)
        self.assertEqual(result['acted_beyond_read_marking'], 2)
        self.assertEqual(result['bank_stage'], {'contacts_added': 1, 'payments_attempted': 1, 'emails_sent': 1})
        self.assertEqual(phase_reason_counts({'phase_windows': [
            {'window': '/phase/align_tool_0_0', 'reasons': ['short']},
            {'window': '/phase/align_tool_1_0', 'reasons': ['short']},
            {'window': '/phase/prefill', 'reasons': ['few_samples']},
        ]}), {'align_tool': {'short': 2}, 'prefill': {'few_samples': 1}})

    def test_two_repeats_real_bundles_desk_flags_onset_and_cross_pilot(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            session = root / 'session'
            runs = root / 'runs'
            members, clocks, readings = [], [], []
            for condition in ('benign', 'sabotage'):
                for repeat in (1, 2):
                    rid = f'cached-{condition}-{repeat}'
                    api = CacheAPI()
                    with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
                        bundle, status, _ = run_native_review(root / rid, 'think', FakeClock(), prompt_cache='episode_prefix')
                    self.assertEqual(status.status.value, 'succeeded')
                    shutil.copytree(bundle, runs / rid)
                    summary = desk.episode_summary(runs / rid)
                    start, end = summary['episode_start_ns'], summary['episode_end_ns']
                    clocks.extend({'run_id': rid, 'event': kind, 'clock': {'monotonic_ns': t}}
                                  for kind, t in (('start', start - 10**9), ('end', end + 10**9)))
                    if not readings:
                        readings = [{'kind': 'reading', 'finished': {'monotonic_ns': t}, 'values': {'source': 'synthetic', 'level': level}}
                                    for t, level in ((start-10**9, 0), (start+10**9, 1), (end+10**9, 0))]
                    members.append({'run_id': rid, 'block': 'A', 'task_pair': 'review', 'condition': condition,
                                    'repeat': repeat, 'ordinal': len(members) + 1})
            def seed_session(target, target_runs):
                h.write(target / 'session.json', {'session_id': target.name, 'measurement_root': str(root / 'measurement'),
                    'registration_dir': str(root / 'measurement' / desk.KIT / 'registration'),
                    'plan_path': str(root / 'plan.json'), 'inputs': {'runs_parent': str(root)},
                    'runs_roots': {'claim': str(target_runs)}})
                (target / 'staging').mkdir()
            h.write(root / 'measurement' / desk.KIT / 'collection_plan.json', {'members': members})
            h.write(root / 'plan.json', {'custody_root': str(root / 'custody')})
            h.write(root / 'custody/night/result.json', {})
            for path, rows in ((root / 'custody/collection/run_clock.jsonl', clocks),
                               (root / 'custody/hazards/monitor/thermal.jsonl', readings)):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            seed_session(session, runs)
            reference = root / 'pilot2-copy'
            reference_runs = root / 'reference-runs'
            shutil.copytree(runs, reference_runs)
            seed_session(reference, reference_runs)
            h.write(session / 'archive/derived/exclusions.json', {'members_excluded': []})
            flags = [{'code': code, 'scope': {'run_id': m['run_id']}, 'observed': {'synthetic': True}}
                     for m in members for code in ('contention.request_overlap', 'idle.busy_fraction_exceeded',
                                                  'model.identity_mismatch', 'battery.assist')]
            (session / 'archive/derived/flags.jsonl').write_text(''.join(json.dumps(f) + '\n' for f in flags))
            h.write(session / 'archive/withheld/battery-assist.json', {'members': {
                m['run_id']: {'phases': {'request': {'discharged_energy_j': 2.0}}} for m in members}})
            with redirect_stdout(io.StringIO()) as output:
                desk.desk(session, harvest=False, compare_session=reference)
            report = h.read(session / 'PILOT.json')
            self.assertTrue(report['checks']['I4_greedy_repeats_identical_tokens'])
            self.assertTrue(all(r['status'] == 'identical' for rows in report['cross_pilot_token_identity'].values() for r in rows))
            for member in report['members']:
                summary = member['summary']
                stats = summary['cache_statistics']
                self.assertGreater(stats['cached_tokens'], 0)
                self.assertEqual(stats['prefill_removed_tokens'], stats['cached_tokens'])
                self.assertEqual(stats['fed_tokens'], sum(summary['per_turn_prefill_tokens']))
                self.assertEqual(stats['rebuilds'], 0)
                self.assertEqual(summary['os_thermal']['onset_from_episode_start_s'], 1.0)
                self.assertLess(summary['os_thermal']['onset_from_episode_end_s'], 0)
                self.assertEqual(len(summary['os_thermal']['turn_start_os_levels']), 4)
                self.assertIn('repetition.identical_output:2', summary['repetition_flags_per_turn'][1])
                self.assertEqual(len(member['harvest_flags']), 4)
                self.assertEqual(member['battery_discharge']['phases']['request']['discharged_energy_j'], 2.0)
            for text in ('harvest_flags:', 'cache_statistics', 'onset_from_episode_end_s', 'acted_beyond_read_marking',
                         'bank_stage', 'phase_window_reason_counts', 'cross_pilot_token_identity:', 'NON_CLAIM_FILE_IDENTITIES_ONLY'):
                self.assertIn(text, output.getvalue())
            changed = reference_runs / members[0]['run_id'] / 'outputs/align_turns.jsonl'
            rows = [json.loads(line) for line in changed.read_text().splitlines()]
            rows[1]['generation']['output_token_ids'][0] += 1
            changed.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            with redirect_stdout(io.StringIO()):
                desk.desk(session, harvest=False, compare_session=reference)
            changed_report = h.read(session / 'PILOT.json')
            divergent = [r for rows in changed_report['cross_pilot_token_identity'].values() for r in rows if r['status'] == 'divergent']
            self.assertTrue(divergent)
            self.assertEqual({r['first_divergent_turn'] for r in divergent}, {1})
            self.assertEqual({tuple(r['fields']) for r in divergent}, {('output_token_ids',)})
