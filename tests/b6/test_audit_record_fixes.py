"""Audit F8/F11/F15/F17: synthetic production-shaped records only."""
import copy
import csv
import dataclasses
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import desk_compress as desk
from joulewise.b5 import harvest as h
from joulewise.b6 import acceptance, archive, code_check, export_runs, precheck
from tests.b6 import support
from tests.b6.test_export_runs import archive_fixture
from tests import test_harvest_b5_window as windows


class AuditRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_cli_harvest_records_the_selected_registration_inputs(self):
        # Primary-byte synthetic bundles pass through the actual CLI, harvester,
        # acceptance and export; no harvest or registration reader is replaced.
        window = windows.Window(self.root / 'cli-window')
        plan = json.loads(window.plan_path.read_bytes())
        plan['hazard_window']['bindings']['capture_screen'] = {}
        support.write_json(window.plan_path, plan)
        reg = support.registration_dir(self.root / 'selected-cli-inputs')
        registration_paths = [reg / 'acceptance.json', reg / 'identity_pins.json']
        digests = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in registration_paths}
        child_tmp = self.root / 'cli-tmp'
        child_tmp.mkdir()
        result = subprocess.run([
            sys.executable, '-B', str(support.ROOT / 'scripts/harvest_b6_session.py'),
            '--plan', str(window.plan_path), '--archive-root', str(window.archive),
            '--registration-dir', str(reg), '--pack-records-root', str(self.root / 'packs'),
            '--export-dir', str(self.root / 'exports'), '--non-claim', '--workers', '1'],
            cwd=support.ROOT, env={**os.environ, 'TMPDIR': str(child_tmp)},
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((window.archive / 'harvest.json').read_bytes())
        self.assertEqual(record['verdict'], h.COLLECTED)
        for path, digest in digests.items():
            # Exact identity: digests describe the bytes selected by CLI paths.
            self.assertEqual(record['registration_files'][path], {'sha256': digest})
        checkout = record['harvest_checkout']
        self.assertEqual(checkout['head'], subprocess.check_output([
            'git', '-C', str(support.ROOT), 'rev-parse', 'HEAD'], text=True).strip())
        self.assertIsInstance(checkout['status_clean'], bool)
        for name in h.B6_HARVEST_PROGRAM_FILES:
            self.assertEqual(checkout['files'][name], hashlib.sha256((support.ROOT / name).read_bytes()).hexdigest())
        self.assertEqual(window.exclusions()['harvest_checkout'], checkout)
        exported = json.loads(result.stdout)['export']
        self.assertTrue(Path(exported['csv']).is_file())
        self.assertTrue(Path(exported['session']).is_file())

    def test_review_rows_are_append_only_and_load_in_the_code_check(self):
        path = support.ROOT / 'configs/b6/executing_reviews.json'
        rows = json.loads(path.read_bytes())
        before = json.loads(subprocess.check_output([
            'git', '-C', str(support.ROOT), 'show', '9bdcf6c95:configs/b6/executing_reviews.json']))
        # Exact identity of the existing records is the append-only property.
        self.assertEqual(rows[:len(before)], before)
        self.assertEqual(len({row['commit'] for row in rows}), len(rows))
        for row in rows[len(before):]:
            self.assertTrue(row['executing_reviews'])
            self.assertTrue(all(review['paper'].startswith('/Users/edr/night-archive/')
                                for review in row['executing_reviews']))
        registered = json.loads((support.ROOT / 'configs/b6/registration/acceptance.json').read_bytes())
        self.assertEqual(len(registered['number_bearing_paths']), 16)
        # F8's verdict/calibration list is broader than registration's 16
        # acquisition paths. Enumerate its historical coverage independently
        # of code_check; G7's production path expansion remains a separate gate.
        verdict_calibration_paths = (
            'joulewise/b6/acceptance.py', 'joulewise/b6/calibration.py',
            'joulewise/b6/capture_screen.py', 'joulewise/b5/harvest.py',
            'joulewise/whole_window.py', 'joulewise/calibration_ledger.py',
            'joulewise/flags/', 'joulewise/tolerances.py',
            'joulewise/hazards/clock.py', 'joulewise/uncertainty_evidence.py',
        )
        reviewed = {row['commit'] for row in rows}
        commits = subprocess.check_output([
            'git', '-C', str(support.ROOT), 'log', '--format=%H',
            registered['registered_commit'] + '..f31aca19f', '--',
            *verdict_calibration_paths], text=True).splitlines()
        self.assertTrue(commits, 'empty F8 history cannot prove review coverage')
        self.assertEqual(sorted(set(commits) - reviewed), [])
        # Also cover every registered-path commit on this PR, including later
        # fix commits, and execute the actual check at the current lane head.
        head = subprocess.check_output(['git', '-C', str(support.ROOT),
                                        'rev-parse', 'HEAD'], text=True).strip()
        commits = subprocess.check_output([
            'git', '-C', str(support.ROOT), 'log', '--format=%H',
            'fda9b380d..' + head, '--', *registered['number_bearing_paths']], text=True).splitlines()
        self.assertEqual(sorted(set(commits) - reviewed), [])
        result = code_check.check(support.ROOT, registered['registered_commit'], head,
                                  registered['number_bearing_paths'], rows, '')
        self.assertEqual(result['unreviewed'], [])
        self.assertNotIn('code.identity_unmeasured', result['flags'])

    @unittest.skipUnless(Path(desk.zstd_path()).is_file(), 'zstd CLI required')
    def test_truncated_compressed_hazard_journal_finishes_with_flags(self):
        window = windows.Window(self.root / 'damaged-journal')
        path = window.custody / 'hazards/monitor/battery.jsonl'
        compressed = Path(str(path) + '.zst')
        # Reproduce the historically compressed hazard layout, despite today's
        # compressor exemption, then truncate a real zstd frame at its midpoint.
        subprocess.run([desk.zstd_path(), '-q', str(path), '-o', str(compressed)], check=True)
        frame = compressed.read_bytes()
        compressed.write_bytes(frame[:len(frame) // 2])
        path.unlink()
        record = window.harvest(prepare_desk=False, run_g3=False)
        self.assertEqual(record['verdict'], h.COLLECTED)
        self.assertEqual(window.window_flags()['collector_errors'], [])
        self.assertIn('records.monitor_journal_absent', window.codes())
        self.assertIn('battery.unmeasured', window.codes())

    @unittest.skipUnless(Path(desk.zstd_path()).is_file(), 'zstd CLI required')
    def test_historical_compressed_arm_and_flags_are_present_to_harvest(self):
        window = windows.Window(self.root / 'compressed-arm')
        flags = window.custody / 'flags'
        flags.mkdir(parents=True, exist_ok=True)
        flag = windows.l4_flag_line('records.collector_failed', stage='arm', collector='synthetic')
        (flags / 'arm.jsonl').write_text(json.dumps(flag) + '\n')
        before = window.harvest(prepare_desk=False, run_g3=False)
        self.assertEqual(before['verdict'], h.COLLECTED)
        plain_codes = window.codes()
        inputs = h.resolve_inputs(window.plan_path)
        paths = [inputs.arm_record_path, *inputs.flags_dir.glob('*.jsonl')]
        self.assertTrue(inputs.arm_record_path.is_file())
        for path in paths:
            subprocess.run([desk.zstd_path(), '-q', str(path), '-o', str(path) + '.zst'], check=True)
            path.unlink()
        window.archive = self.root / 'compressed-arm-reharvest'
        after = window.harvest(prepare_desk=False, run_g3=False)
        self.assertEqual(after['verdict'], h.COLLECTED)
        self.assertEqual(window.window_flags()['collector_errors'], [])
        self.assertEqual(window.codes(), plain_codes)
        self.assertNotIn('records.arm_record_absent', window.codes())

    def test_gamma_midpoint_loss_harvest_writers_and_acceptance_use_block_six_rule(self):
        pack_id = support.PACKS['gamma']
        pack = support.ROOT / 'configs/campaigns' / pack_id
        # Use the shipped 107-member GAMMA stage walk and its actual cell units.
        roster = h.build_roster(pack, support.ROOT)
        document, spans = h.l4_exclusion_inputs(roster, {}, plan_id='synthetic-gamma', attempt=1)
        rows = [{'sequence': i, 'disposition': 'valid', 'exact_bound_lexeme_s': '0.028'}
                for i in range(1, 25)]
        evidence = precheck.synthetic_session(pack, support.ROOT, rows, {})
        _, roles = acceptance._stage_roles(json.loads((pack / 'plan_tree.json').read_bytes()))
        evidence = dataclasses.replace(evidence, stages=tuple(dataclasses.replace(stage, members=tuple(
            dataclasses.replace(member, role=roles.get(member.run_id, 'science'))
            for member in stage.members)) for stage in evidence.stages))
        planned_ids = {member.run_id for stage in evidence.stages for member in stage.members}
        document['members'] = [member for member in document['members'] if member['run_id'] in planned_ids]
        lost = next(m.run_id for stage in evidence.stages for m in stage.members if m.role == 'midpoint')
        stages = tuple(dataclasses.replace(stage, members=tuple(
            dataclasses.replace(member, status='failed', flags=('member.status_not_succeeded',))
            if member.run_id == lost else member for member in stage.members)) for stage in evidence.stages)
        evidence = dataclasses.replace(evidence, stages=stages, window_flags=('neg8.midpoint_lost',))
        reg = support.registration_dir(self.root)
        prepared = acceptance.ACCEPTANCE.prepare(ledger_path=self.root / 'ledger', ledger_rows=rows,
            plan_tree=json.loads((pack / 'plan_tree.json').read_bytes()), pack_root=pack,
            registration_dir=reg, code_identity={})
        result = acceptance.ACCEPTANCE.evaluate(prepared, evidence)
        self.assertTrue(result.counting, result.reasons)
        for block_six in (False, True):
            with self.subTest(block_six=block_six):
                target = self.root / ('b6' if block_six else 'b5')
                plan = {'plan_id': 'synthetic-gamma', 'attempt': 1, 'measurement_root': str(support.ROOT),
                        'pack_root': str(pack), 'pack_id': pack_id, 'claim_runs_root': str(target / 'runs'),
                        'custody_root': str(target / 'custody'), 'hazard_window': {'bindings': {}}}
                if block_six:
                    # The production plan's explicit lane marker, independent of pack_id.
                    plan['hazard_window']['bindings']['capture_screen'] = {}
                support.write_json(target / 'plan.json', plan)
                inputs = h.resolve_inputs(target / 'plan.json', {'catalog_path': support.ROOT / 'configs/b6/flag_catalog_b6.json'})
                writer = h._Harvest(inputs, target / 'archive', h.Seams(), prepare_desk=False, run_g3=False)
                writer.exclusion_roster, writer.exclusion_spans = document, spans
                writer.emit('neg8.midpoint_lost', level='window', collector='synthetic')
                writer.emit('member.status_not_succeeded', level='member', run_id=lost, collector='synthetic')
                record = writer.finish(h.COLLECTED)
                self.assertIs(record['claim_usable'], block_six)
                for name, keys in [('derived/exclusions.json', ()),
                                   ('derived/window_flags.json', ('exclusions',))]:
                    value = json.loads((target / 'archive' / name).read_bytes())
                    for key in keys:
                        value = value[key]
                    self.assertIs(value['claim_usable'], block_six)
                self.assertEqual(record['exclude_window_reasons'], [] if block_six else ['neg8.midpoint_lost_primary'])

    def test_unresolved_export_nulls_energies_and_preserves_kept_members(self):
        root, reg, plan, record = archive_fixture(self.root)
        # member.anchor_not_bounded already excludes this member; counting is unchanged.
        record.update(verdict='ACCEPT', counting=True)
        record['excluding'].append({'scope': 'member', 'run_id': 'gamma-a', 'code': archive.CLOCK_ANCHOR_STATUS})
        original = export_runs.export(root, plan, reg, self.root / 'keys', self.root / 'before',
                                      acceptance_record=record, non_claim=True)
        cases = [
            {'uncertainty_evidence': {'clock_anchor': {'detail': 'effective_clock_anchor_bound_exceeded'}}},
            {'uncertainty_evidence': {'clock_anchor': {'status': 'unbounded',
                'trace_fallback_method': 'legacy_spawn_bracket_midpoint_v1'}}},
            {},
        ]
        summary_path = root / 'withheld/reductions/gamma-a.summary_metrics.rereduced.json'
        summary = json.loads(summary_path.read_bytes())
        for index, metadata in enumerate(cases):
            with self.subTest(index=index):
                changed = copy.deepcopy(summary)
                if index == 2:
                    changed['window_evidence_precheck'] = {'phase': {
                        phase: {'eligible': False, 'reasons': ['clock_anchor_unresolved']}
                        for phase in export_runs.PHASES}}
                support.write_json(summary_path, changed)
                support.write_json(root / 'sources/claim-runs/gamma-a/metadata.json', metadata)
                after = export_runs.export(root, plan, reg, self.root / 'keys', self.root / f'after-{index}',
                                           acceptance_record=record, non_claim=True)
                def read_rows(path):
                    with path.open() as stream:
                        return list(csv.DictReader(stream))
                before_rows, after_rows = read_rows(original.csv_path), read_rows(after.csv_path)
                # Exact identity: counts, ids and exclusion labels are the protected property.
                self.assertEqual(after.row_count, original.row_count)
                self.assertEqual([r['run_id'] for r in after_rows if r['excluded'] == 'False'],
                                 [r['run_id'] for r in before_rows if r['excluded'] == 'False'])
                self.assertEqual(json.loads(after.sidecar_path.read_bytes())['counting'], record['counting'])
                marked = next(row for row in after_rows if row['run_id'] == 'gamma-a')
                self.assertEqual(marked['status'], archive.CLOCK_ANCHOR_STATUS)
                self.assertTrue(all(marked[key] == '' for key in export_runs.ENERGIES))
                self.assertEqual([r for r in after_rows if r['run_id'] != 'gamma-a'],
                                 [r for r in before_rows if r['run_id'] != 'gamma-a'])

    def test_real_harvest_records_checkout_and_digests_and_marks_clock_summary(self):
        # Actual strict validation, reducer, copy, flags and output writers on primary-byte fixtures.
        window = windows.Window(self.root / 'window')
        plan = json.loads(window.plan_path.read_bytes())
        plan['hazard_window']['bindings']['capture_screen'] = {}
        support.write_json(window.plan_path, plan)
        run_id = windows.MEMBERS[0][0]
        bundle = window.claim / run_id
        metadata = json.loads((bundle / 'metadata.json').read_bytes())
        metadata['uncertainty_evidence']['clock_anchor'].update(
            status='unbounded', detail='effective_clock_anchor_bound_exceeded',
            trace_fallback_method='legacy_spawn_bracket_midpoint_v1')
        support.write_json(bundle / 'metadata.json', metadata)
        source = {path.relative_to(bundle).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in bundle.rglob('*') if path.is_file()}
        reg = support.registration_dir(self.root)
        inputs = h.resolve_inputs(window.plan_path)
        record = h.harvest(inputs, window.archive,
                           seams=h.Seams(group_alive=lambda _pgid: False), run_g3=False,
                           registration_paths=[reg / 'acceptance.json', reg / 'identity_pins.json'])
        self.assertEqual(record['verdict'], h.COLLECTED)
        checkout = record['harvest_checkout']
        self.assertEqual(checkout['head'], subprocess.check_output([
            'git', '-C', str(support.ROOT), 'rev-parse', 'HEAD'], text=True).strip())
        self.assertIsInstance(checkout['status_clean'], bool)
        for name in h.HARVEST_PROGRAM_FILES:
            self.assertEqual(checkout['files'][name], hashlib.sha256((support.ROOT / name).read_bytes()).hexdigest())
        self.assertEqual(window.exclusions()['harvest_checkout'], checkout)
        for path in (reg / 'acceptance.json', reg / 'identity_pins.json'):
            self.assertEqual(record['registration_files'][str(path)]['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        summary = json.loads((window.archive / f'withheld/reductions/{run_id}.summary_metrics.rereduced.json').read_bytes())
        self.assertEqual(summary['energy_status'], archive.CLOCK_ANCHOR_STATUS)
        self.assertTrue(all(value is None for value in summary['phase_energy_j'].values()))
        self.assertIsNone(summary['gross_energy_j'])
        assessment = json.loads((window.archive / 'withheld/member-assessments.json').read_bytes())['members'][run_id]['rereduced']
        self.assertEqual(assessment['energy_status'], archive.CLOCK_ANCHOR_STATUS)
        self.assertFalse(assessment['archived_identical_to_stored'])
        self.assertEqual(source, {path.relative_to(bundle).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in bundle.rglob('*') if path.is_file()})


def tearDownModule():
    windows.tearDownModule()
    windows._TEMPLATE = None
