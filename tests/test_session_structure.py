"""Synthetic structure checks, including the file-open and output firewall."""
import builtins
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise import session_structure as structure


class SessionStructureTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.archive, self.custody, self.records = [self.root / name for name in ('archive', 'custody', 'records')]
        self.runs = self.archive / 'sources/claim-runs'
        self.registration = {'pack_id': 'ALPHA', 'structure': {'excluding_flags': ['clock.overlap']}}
        self.registration_path = self.root / 'registration.json'
        self.put(self.registration_path, self.registration)
        self.put(self.archive / 'harvest.json', {'verdict': 'COLLECTED', 'claim_usable': True,
                                                'pack_id': 'ALPHA', 'plan_id': 'session-1', 'attempt': 1})
        self.yielded = {'planned': 2, 'present': 2, 'raw_valid': 2, 'succeeded': 1,
                        'per_roster_stage': [{'stage_id': 'science', 'planned': 2, 'present': 2,
                                              'raw_valid': 2, 'succeeded': 1}], 'unresolved_collection_stages': []}
        self.put(self.archive / 'derived/yield.json', self.yielded)
        self.put(self.archive / 'derived/roster.json', {'members': [{'run_id': 'r1', 'stage_id': 'science'},
                                                                  {'run_id': 'r2', 'stage_id': 'science'}]})
        self.put(self.archive / 'derived/exclusions.json', {'members_excluded': []})
        self.put(self.archive / 'derived/flags.jsonl', '')
        self.put(self.custody / 'night/chain-stages.jsonl', json.dumps({'stage_id': 'science', 'kind': 'campaign_collection',
                                                                       'rc': 0, 'started_epoch_s': 10, 'ended_epoch_s': 40}) + '\n')
        self.put(self.custody / 'night/result.json', {'aborted_reason': None})
        self.put(self.custody / 'night/chain.started', {'epoch_s': 5})
        self.put(self.custody / 'night/chain.exited', {'rc': 0, 'epoch_s': 45})
        for role in ('opening', 'closing'):
            (self.runs / 'instrument_validation' / role).mkdir(parents=True)
        for member in ('r1', 'r2'):
            for name in (*structure.REQUIRED_MEMBER_FILES, 'summary_metrics.json'):
                self.put(self.runs / member / name, 'unread member bytes')

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value))

    def check(self, **kwargs):
        return structure.check(archive=self.archive, custody=self.custody, registration=self.registration, **kwargs)

    def flag(self, code='clock.overlap', blinding='STRUCTURE', klass='PHYSICS'):
        return {'code': code, 'blinding': blinding, 'klass': klass, 'scope': {'level': 'member', 'run_id': 'r1'},
                'observed': 98765.4321, 'detail': 'secret 98765.4321'}

    def test_clean_counts_durations_and_first_session(self):
        record = self.check()
        self.assertEqual(record['verdict'], 'STRUCTURE_OK')
        self.assertTrue(record['counting'])
        self.assertEqual(record['per_roster_stage'], self.yielded['per_roster_stage'])
        self.assertEqual(record['counts'], {key: self.yielded[key] for key in structure.COUNT_FIELDS})
        self.assertEqual(record['chain_seconds'], 40)
        self.assertEqual(record['stages'][0]['seconds'], 30)
        self.assertTrue(record['first_session_of_pack'])
        previous = self.root / 'previous.json'
        self.put(previous, record)
        self.assertFalse(self.check(previous=[previous])['first_session_of_pack'])

    def test_nonzero_stage_is_recorded_but_chain_crash_holds_loop(self):
        journal = self.custody / 'night/chain-stages.jsonl'
        self.put(journal, json.dumps({'stage_id': 'science', 'rc': 7}) + '\n')
        record = self.check()
        self.assertEqual((record['verdict'], record['action']), ('STRUCTURE_OK', 'CONTINUE'))
        self.assertEqual(record['stages_rc_nonzero'], 1)
        self.assertTrue(record['counting'])
        self.put(journal, '')
        self.put(self.custody / 'night/chain.exited', {'exit_code': 7, 'epoch_s': 45})
        self.assertIn('chain_crashed', self.check()['reasons'])

    def test_physical_stops_are_not_crash_defects(self):
        self.put(self.custody / 'night/chain-stages.jsonl', '{"rc":7}\n')
        self.yielded['unresolved_collection_stages'] = ['science']
        self.put(self.archive / 'derived/yield.json', self.yielded)
        for word in structure.PHYSICS_STOP_REASONS:
            with self.subTest(word=word):
                self.put(self.custody / 'night/result.json', {'aborted_reason': word + '_emergency'})
                record = self.check()
                self.assertEqual(record['verdict'], 'STRUCTURE_OK')
                self.assertFalse(record['counting'])
                self.assertIn('physical_stop:' + word, record['counting_reasons'])
        self.put(self.custody / 'night/result.json', {'aborted_reason': 'thermalish'})
        self.put(self.custody / 'night/chain.exited', {'rc': 7})
        self.assertEqual(self.check()['verdict'], 'STRUCTURE_DEFECT')

    def test_each_required_record_missing(self):
        for name in structure.REQUIRED_RECORDS:
            with self.subTest(name=name):
                path = (self.runs / name if name.startswith('instrument_validation/') else
                        (self.custody if name.startswith('night/') else self.archive) / name)
                if path.is_dir():
                    path.rmdir()
                    saved = None
                else:
                    saved = path.read_bytes()
                    path.unlink()
                record = self.check()
                if name == 'night/result.json':
                    self.assertEqual(record['verdict'], 'STRUCTURE_OK')
                    self.assertIn('terminal_record_missing', record['counting_reasons'])
                else:
                    self.assertIn('record_class_missing:' + name, record['reasons'])
                if saved is None:
                    path.mkdir()
                else:
                    path.write_bytes(saved)

    def test_member_plain_or_compressed_file_existence(self):
        plain = self.runs / 'r1/raw/powermetrics.plist'
        compressed = Path(str(plain) + '.zst')
        plain.rename(compressed)
        self.assertEqual(self.check()['verdict'], 'STRUCTURE_OK')
        compressed.unlink()
        self.assertIn('member_files_missing:1', self.check()['reasons'])

    def test_review_s1_and_s1b_nonzero_stage_codes(self):
        for codes in ((1,), (2, 1), (75, 124)):
            with self.subTest(codes=codes):
                kinds = ('campaign_collection',) if len(codes) == 1 else ('bound_derivation', 'calibration_capture')
                rows = [{'stage_id': str(i), 'kind': kind, 'rc': rc} for i, (kind, rc) in enumerate(zip(kinds, codes))]
                self.put(self.custody / 'night/chain-stages.jsonl', ''.join(json.dumps(row) + '\n' for row in rows))
                self.put(self.custody / 'night/result.json', {'verdict': 'GO', 'chain_exit_code': 0})
                record = self.check()
                self.assertEqual((record['verdict'], record['action'], record['counting']),
                                 ('STRUCTURE_OK', 'CONTINUE', True))
                self.assertEqual(record['stages_rc_nonzero'], len(codes))

    def test_physical_code_map_tracks_registered_vocabulary(self):
        from joulewise.night_gate import NIGHT_DRIVER_REASON_CODES, HAZARD_DRIVER_REASON_CODES, NIGHT_GATE_REASON_CODES
        registered = NIGHT_DRIVER_REASON_CODES | HAZARD_DRIVER_REASON_CODES | NIGHT_GATE_REASON_CODES | {"operative_bound_above_stop"}
        self.assertLessEqual(set(structure.PHYSICAL_STOP_CODES), registered)
        self.assertIsNone(structure._physical('night_stopped_census_unmeasured'))
        for code, kind in structure.PHYSICAL_STOP_CODES.items():
            self.assertEqual(structure._physical(code), kind)
        from joulewise.b5.chain import STOP_EXITS
        self.assertEqual(structure.CHAIN_STOP_EXITS, {value: key for key, value in STOP_EXITS.items()})

    def test_review_s2_and_s3_physical_stop_without_captures(self):
        for role in ('opening', 'closing'):
            (self.runs / 'instrument_validation' / role).rmdir()
        self.put(self.custody / 'night/chain-stages.jsonl', '{"rc":-15}\n')
        self.put(self.custody / 'night/chain.exited', {'exit_code': -15})
        for reason, kind in (('night_stopped_disk_low', 'disk'), ('night_stopped_monitor_outage', 'sampler'),
                             ('night_aborted_agent_present', 'agent'), ('disk_low', 'disk')):
            with self.subTest(reason=reason):
                self.put(self.custody / 'night/result.json', {'verdict': 'ABORTED', 'aborted_reason': reason})
                record = self.check()
                self.assertEqual((record['verdict'], record['action'], record['counting']),
                                 ('STRUCTURE_OK', 'CONTINUE', False))
                self.assertIn('physical_stop:' + kind, record['counting_reasons'])

    def test_b6_acceptance_owns_counting_with_b5_claim_labelled(self):
        self.put(self.archive / 'harvest.json', {'verdict': 'COLLECTED', 'claim_usable': False})
        self.put(self.archive / 'derived/b6-acceptance.json', {'verdict': 'ACCEPT', 'counting': True})
        record = self.check()
        self.assertTrue(record['counting'], record)
        self.assertIs(record['b5_harvest_claim_usable'], False)
        self.assertEqual(record['counting_source'], 'b6_acceptance')
        self.put(self.custody / 'night/chain-stages.jsonl', '{"stage_id":"chain.stop","kind":"operative_bound_above_stop","rc":12}\n')
        self.put(self.custody / 'night/chain.exited', {'exit_code': 12})
        self.put(self.archive / 'derived/b6-acceptance.json', {'verdict': 'EXCLUDE', 'counting': False})
        record = self.check()
        self.assertEqual(record['chain_stopped'], 'operative_bound_above_stop')
        self.assertEqual(record['physical_stop'], 'calibration.operative_bound_above_stop')
        self.assertFalse(record['counting'])

    def test_review_s5_terminal_missing_and_nonphysical_abort(self):
        (self.custody / 'night/result.json').unlink()
        record = self.check()
        self.assertEqual((record['verdict'], record['action'], record['counting']),
                         ('STRUCTURE_OK', 'CONTINUE', False))
        self.assertTrue(record['terminal_record_missing'])
        self.put(self.custody / 'night/chain.exited', {'exit_code': 1})
        self.assertIn('chain_crashed', self.check()['reasons'])
        self.assertEqual(self.check()['action'], 'HOLD_LOOP')
        self.put(self.custody / 'night/chain.exited', {'exit_code': 0})
        self.put(self.custody / 'night/result.json', {'verdict': 'ABORTED', 'aborted_reason': 'night_probe_error'})
        self.assertIn('chain_crashed', self.check()['reasons'])
        self.assertEqual(self.check()['action'], 'HOLD_LOOP')

    def test_chain_stops_and_result_without_exit_are_terminal(self):
        for role in ('opening', 'closing'):
            (self.runs / 'instrument_validation' / role).rmdir()
        for rc, kind in structure.CHAIN_STOP_EXITS.items():
            with self.subTest(rc=rc):
                self.put(self.custody / 'night/chain.exited', {'exit_code': rc})
                self.put(self.custody / 'night/result.json', {'verdict': 'CHAIN_STOPPED', 'chain_exit_code': rc})
                record = self.check()
                self.assertEqual((record['verdict'], record['action'], record['counting']),
                                 ('STRUCTURE_OK', 'CONTINUE', False))
                self.assertIn('chain_stopped:' + kind, record['counting_reasons'])
        (self.custody / 'night/chain.exited').unlink()
        self.assertEqual(self.check()['verdict'], 'STRUCTURE_OK')
        self.put(self.custody / 'night/result.json', {'verdict': 'REFUSED', 'aborted_reason': 'night_refused_battery_float'})
        self.assertEqual(self.check()['verdict'], 'STRUCTURE_OK')
        self.put(self.custody / 'night/result.json', {'verdict': 'ABORTED', 'chain_exit_code': 1})
        self.assertIn('chain_crashed', self.check()['reasons'])

    def test_review_s4_excluded_member_and_missing_summary(self):
        summary = self.runs / 'r2/summary_metrics.json'
        summary.unlink()
        record = self.check()
        self.assertEqual((record['verdict'], record['counting'], record['member_summary_missing']),
                         ('STRUCTURE_OK', True, 1))
        self.put(self.archive / 'derived/exclusions.json', {'members_excluded': [{'run_id': 'r2', 'codes': ['member.timeout']}]})
        (self.runs / 'r2/raw/powermetrics.plist').unlink()
        self.assertEqual(self.check()['verdict'], 'STRUCTURE_OK')
        self.assertEqual(self.check()['member_summary_missing'], 0)
        self.put(self.archive / 'derived/exclusions.json', {'members_excluded': []})
        self.assertIn('member_files_missing:1', self.check()['reasons'])

    def test_review_f4_torn_lines_keep_valid_rows_and_count_damage(self):
        self.put(self.archive / 'derived/flags.jsonl', json.dumps(self.flag('safe.record')) + '\n{"code":"clock.st')
        self.put(self.custody / 'night/chain.started', '{')
        self.put(self.custody / 'night/chain-stages.jsonl', '{"rc":1}\n{')
        handover = self.root / 'handover.jsonl'
        self.put(handover, '{"transition":"chain-exit-to-desk"}\n{')
        record = self.check(handover_record=handover)
        self.assertEqual((record['verdict'], record['action'], record['counting']),
                         ('STRUCTURE_OK', 'CONTINUE', True))
        self.assertEqual(record['damaged_lines'], {'flags.jsonl': 1, 'chain-stages.jsonl': 1, 'handover.jsonl': 1})
        self.assertEqual(record['damaged_records'], ['chain.started'])
        self.assertEqual(record['flags']['STRUCTURE'], {'safe.record': 1})
        self.assertEqual(record['stages_rc_nonzero'], 1)
        self.put(self.custody / 'night/result.json', '{')
        self.put(self.custody / 'night/chain.exited', '{')
        record = self.check()
        self.assertEqual(record['verdict'], 'STRUCTURE_OK')
        self.assertFalse(record['counting'])
        self.assertTrue(record['terminal_record_missing'])

    def test_torn_harvest_objects_require_reharvest(self):
        for name in ('harvest.json', 'derived/yield.json', 'derived/roster.json', 'derived/exclusions.json'):
            with self.subTest(name=name):
                path = self.archive / name
                saved = path.read_text()
                self.put(path, '{')
                record = self.check()
                self.assertEqual((record['verdict'], record['action'], record['counting']),
                                 ('HARVEST_FAULT', 'REHARVEST', False))
                self.assertIn(path.name, record['damaged_records'])
                self.put(path, saved)

    def test_damaged_utf8_line_keeps_valid_flag_rows(self):
        path = self.archive / 'derived/flags.jsonl'
        path.write_bytes((json.dumps(self.flag('safe.record')) + '\n').encode() + b'\xff\n')
        record = self.check()
        self.assertTrue(record['counting'])
        self.assertEqual(record['flags']['STRUCTURE'], {'safe.record': 1})
        self.assertEqual(record['damaged_lines'], {'flags.jsonl': 1})

    def test_harvest_fault_and_not_ready(self):
        self.assertEqual((self.check(harvest_rc=2)['verdict'], self.check(harvest_rc=2)['action']),
                         ('HARVEST_FAULT', 'REHARVEST'))
        self.put(self.archive / 'harvest.json', {'verdict': 'HARVEST_FAULT'})
        self.assertEqual(self.check()['verdict'], 'HARVEST_FAULT')
        (self.custody / 'night/chain.exited').unlink()
        (self.custody / 'night/result.json').unlink()
        self.assertEqual(self.check()['verdict'], 'NOT_READY')

    def test_missing_harvest_preserves_explicit_session_identity(self):
        (self.archive / 'harvest.json').unlink()
        record = self.check(harvest_rc=3, attempt=4, session_id='session-4')
        self.assertEqual(record['verdict'], 'HARVEST_FAULT')
        self.assertFalse(record['counting'])
        self.assertEqual((record['pack_id'], record['attempt'], record['plan_id']), ('ALPHA', 4, 'session-4'))

    def test_excluding_flag_classification_and_counts(self):
        self.put(self.archive / 'derived/flags.jsonl', json.dumps(self.flag()) + '\n')
        self.put(self.archive / 'derived/exclusions.json', {'members_excluded': [{'run_id': 'r1', 'codes': ['clock.overlap', 'unknown.code']}]})
        record = self.check()
        self.assertFalse(record['counting'])
        self.assertIn('excluding_flag:clock.overlap', record['counting_reasons'])
        self.assertEqual(record['flags'], {'STRUCTURE': {'clock.overlap': 1}, 'RESTRICTED': 0})
        self.assertEqual(record['exclusions'], {'STRUCTURE': {'clock.overlap': 1}, 'RESTRICTED': 1})

    def test_unresolved_handover_and_malformed_record(self):
        self.yielded['unresolved_collection_stages'] = ['science']
        self.put(self.archive / 'derived/yield.json', self.yielded)
        self.assertIn('stage_unresolved:1', self.check()['reasons'])
        handover = self.root / 'handover.jsonl'
        self.put(handover, '{"transition":"other"}\n')
        self.assertIn('handover_missing', self.check(handover_record=handover)['reasons'])
        self.put(handover, '{"transition":"chain-exit-to-desk"}\n')
        self.assertNotIn('handover_missing', self.check(handover_record=handover)['reasons'])
        self.put(self.archive / 'derived/roster.json', 'bad-json')
        self.assertEqual((self.check()['verdict'], self.check()['action']), ('HARVEST_FAULT', 'REHARVEST'))
        self.assertIn('roster.json', self.check()['damaged_records'])

    def test_energy_firewall_checks_every_open_and_public_output(self):
        restricted_code = 'sentinel.restricted_secret'
        self.registration['structure']['excluding_flags'].append(restricted_code)
        self.put(self.registration_path, self.registration)
        for name in ('withheld/energy.json', 'derived/neg8-bound.json', 'derived/bracket-private.json'):
            self.put(self.archive / name, {'secret': 98765.4321})
        flags = [self.flag('safe.structural', klass='REPRESENTATION'), self.flag(restricted_code, 'RESTRICTED', 'NUMBER')]
        self.put(self.archive / 'derived/flags.jsonl', ''.join(json.dumps(flag) + '\n' for flag in flags))
        self.put(self.archive / 'derived/exclusions.json', {'members_excluded': [{'run_id': 'r1', 'codes': [restricted_code]}]})
        whitelist = {self.registration_path, self.archive / 'harvest.json',
                     *(self.archive / 'derived' / name for name in ('yield.json', 'roster.json', 'exclusions.json', 'flags.jsonl')),
                     *(self.custody / 'night' / name for name in ('chain-stages.jsonl', 'result.json', 'chain.started', 'chain.exited'))}
        opened = set()
        original_open, original_io = builtins.open, io.open
        original_read_text = Path.read_text
        def read_text(path, *args, **kwargs):
            self.assertIn(path, whitelist)
            return original_read_text(path, *args, **kwargs)
        def tracking(function):
            def wrapped(path, mode='r', *args, **kwargs):
                if isinstance(path, (str, Path)) and 'r' in mode:
                    opened.add(Path(path))
                return function(path, mode, *args, **kwargs)
            return wrapped
        output = io.StringIO()
        with patch('builtins.open', tracking(original_open)), patch('io.open', tracking(original_io)), \
             patch.object(Path, 'read_bytes', side_effect=AssertionError('read_bytes forbidden')), \
             patch.object(Path, 'read_text', read_text), redirect_stdout(output):
            self.assertEqual(structure.main(['--archive', str(self.archive), '--custody', str(self.custody),
                                             '--registration', str(self.registration_path), '--record-dir', str(self.records)]), 0)
        self.assertEqual(opened, whitelist)
        public = (self.records / 'structure.json').read_text() + output.getvalue()
        self.assertNotIn('98765.4321', public)
        self.assertNotIn(restricted_code, public)
        self.assertIn('excluding_flag:RESTRICTED', public)

    def test_cli_emits_record_even_for_defect_and_usage_is_two(self):
        (self.runs / 'r1/raw/powermetrics.plist').unlink()
        result = subprocess.run([sys.executable, 'scripts/session_structure_check.py', '--archive', str(self.archive),
                                 '--custody', str(self.custody), '--registration', str(self.registration_path),
                                 '--record-dir', str(self.records)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('action=HOLD_LOOP', result.stdout)
        self.assertTrue((self.records / 'structure.json').exists())
        bad = subprocess.run([sys.executable, 'scripts/session_structure_check.py'], capture_output=True)
        self.assertEqual(bad.returncode, 2)
