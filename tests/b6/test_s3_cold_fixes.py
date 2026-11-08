"""Stage-3 regressions using synthetic records and injected desk seams."""
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.b5 import chain, plan
from joulewise.b6 import acceptance
from joulewise.b6.acceptance_interface import StageEvidence
from joulewise.b6.desk_lane import DeskLane
from joulewise.b6.driver_lane import metadata_path, write
from joulewise.b6.lanes import Done, Prepared
from tests.b6 import support
from tests.b6.support import DeskCase, ROOT


class StageThreeTests(DeskCase):
    def test_terminal_record_with_exit_takes_priority_over_empty_hazard(self):
        archive = self.root / 'archive'
        write(archive / 'derived/roster.json', {'members': []})
        write(archive / 'night/hazard_result.json', {'verdict': 'GO', 'arm': {'go': True}})
        write(archive / 'night/result.json', {'chain_exit_code': 0})
        ev = acceptance.evidence_from_archive(archive, {'pack_id': 'desk-pack'}, self.root / 'absent')
        self.assertEqual(ev.stop_reason, 'completed')
        write(archive / 'night/hazard_result.json', {'aborted_reason': 'night_stopped_disk_low'})
        ev = acceptance.evidence_from_archive(archive, {'pack_id': 'desk-pack'}, self.root / 'absent')
        self.assertEqual(ev.stop_reason, 'night_stopped_disk_low')

    def desk(self, record, reasons=(), *, done=Done(-15, 'disk'), physical='disk', chain_stopped=None):
        prepared = Prepared('s', str(self.root / 'custody/night_plan.json'),
                            str(self.root / 'custody/night/result.json'), 1)
        paths = {key: str(self.root / key) for key in ('archive', 'custody', 'staging', 'export')}
        paths['measurement'] = str(ROOT)
        Path(paths['staging']).mkdir(exist_ok=True)
        write(metadata_path(prepared), {'paths': paths, 'packs': ['alpha'], 'runs_roots': []})
        write(Path(paths['archive']) / 'derived/b6-acceptance.json', record)
        structure = {'verdict': 'STRUCTURE_DEFECT' if reasons else 'STRUCTURE_OK', 'reasons': list(reasons),
                     'chain_stopped': chain_stopped, 'physical_stop': physical, 'harvest_verdict': 'COLLECTED',
                     'flags': {'STRUCTURE': {}}, 'per_roster_stage': [], 'chain_seconds': 0}
        lane = DeskLane(ROOT, self.root / 'loop', lambda *a, **k: SimpleNamespace(returncode=0, stdout='', stderr=''))
        with patch.object(lane, '_advance', return_value=[]), \
             patch('joulewise.b6.desk_lane.session_structure.check', return_value=structure), \
             patch('joulewise.b6.desk_lane.desk_compress.compress', return_value=(0, {})):
            return lane.session_desk(prepared, done)

    def test_physical_stop_preserves_acceptance_structural_failure(self):
        prep, ev = support.prepared(self.root / 'reg'), support.session(5, synthetic=False)
        science = ev.stages[0]
        absent = StageEvidence('science-a', 'campaign_collection', 5, tuple(
            replace(m, stage_id='science-a', run_id='a' + m.run_id, status='failed',
                    runtime={'bundle_present': False}) for m in science.members))
        ev = replace(ev, stages=(absent,) + ev.stages, stop_reason='night_stopped_disk_low')
        result = acceptance.ACCEPTANCE.evaluate(prep, ev)
        self.assertIn('structure.missing_stage_bundles', result.record['structural_failures'])
        line = self.desk(result.record)
        self.assertEqual(line.physics_stop, 'disk')
        self.assertFalse(line.structure_ok)
        self.assertIn('structure.missing_stage_bundles', line.structure_defects)

    def test_physical_stop_preserves_no_roster_and_unexplained_structure(self):
        line = self.desk({'structural_failures': ['structure.no_roster'], 'physics_stop': True},
                         ('record_class_missing:derived/roster.json', 'member_files_missing:1', 'handover_missing'))
        self.assertEqual(set(line.structure_defects), {'structure.no_roster',
            'record_class_missing:derived/roster.json', 'member_files_missing:1', 'handover_missing'})

    def test_separate_screen_exits_classify_without_journal(self):
        self.assertEqual(chain.STOP_EXITS.get('operative_bound_above_stop'), 13)
        archive = self.root / 'archive'
        write(archive / 'derived/roster.json', {'members': [{'run_id': 's', 'stage_id': 'science'}]})
        for rc, stop, physical in ((13, 'operative_bound_above_stop', True),
                                   (12, 'pre_calibration_screen_failed', False)):
            for journal in (True, False):
                with self.subTest(rc=rc, journal=journal):
                    write(archive / 'night/result.json', {'chain_exit_code': rc})
                    journal_path = archive / 'night/chain-stages.jsonl'
                    if journal:
                        journal_path.write_text(json.dumps({'stage_id': 'chain.stop', 'kind': stop, 'rc': rc}) + '\n')
                    else:
                        journal_path.unlink(missing_ok=True)
                    ev = acceptance.evidence_from_archive(archive, {'pack_id': 'desk-pack'}, self.root / 'absent')
                    self.assertEqual(ev.stop_reason, stop)
                    result = acceptance.ACCEPTANCE.evaluate(support.prepared(self.root / str(rc)), ev)
                    self.assertEqual(result.record['physics_stop'], physical)
                    line = self.desk(result.record, done=Done(rc), physical=None, chain_stopped=stop)
                    self.assertEqual(bool(line.physics_stop), physical)
                    self.assertTrue(line.structure_ok, line.structure_defects)
                    if physical:
                        self.assertIn('calibration.operative_bound_above_stop', line.excluding_reasons)
                    else:
                        self.assertNotIn('calibration.operative_bound_above_stop', line.excluding_reasons)
                        self.assertIn('calibration.bracket_incomplete', line.excluding_reasons)

    def test_open_complete_slot_resumes_before_abort_and_pin(self):
        metadata = {'paths': {'measurement': str(self.root), 'custody': str(self.root / 'custody')},
                    'inputs': {'bracket_session_id': 's'},
                    'prepared': {'plan_path': str(self.root / 'night_plan.json')}}
        # The reservation's frozen plan is a different file from night_plan.
        write(self.root / 'night_plan.json', {'hazard_window': {'bindings': {},
              'pack': {'pack_root': str(self.root / 'pack')}}})
        write(self.root / 'pack/plan_tree.json', {})
        open_status = {'open_sessions': ['s'], 'open_session_next_slots': {
            's': {'next_slot': 'pre', 'custody_state': 'complete'}}}
        pending_status = {'open_sessions': ['s'], 'open_session_next_slots': {
            's': {'next_slot': 'post', 'custody_state': 'absent'}}}
        events = []
        def run(argv, **kwargs):
            events.append(('resume', argv))
            return SimpleNamespace(returncode=0, stdout='{"status":"FINALIZED"}', stderr='')
        lane = DeskLane(self.root, self.root / 'loop', run)
        with patch.object(plan, 'ledger_head_status', side_effect=[open_status, pending_status]), \
             patch.object(chain, 'stage_plan', return_value=[SimpleNamespace(kind='bracket_reservation')]), \
             patch.object(chain, 'stage_argv', return_value=['reserve', '--plan', str(self.root / 'frozen.json')]), \
             patch('joulewise.calibration_ledger.abort_bracket_session', side_effect=lambda *a, **k: events.append(('abort', k))), \
             patch.object(plan, 'advance_ledger_pin', side_effect=lambda *a, **k: events.append(('pin', k)) or {'status': 'ADVANCED'}):
            self.assertEqual(lane._advance(metadata), [])
        self.assertEqual([e[0] for e in events], ['resume', 'abort', 'pin'])
        self.assertIn(str(self.root / 'frozen.json'), events[0][1])
        self.assertNotIn(str(self.root / 'night_plan.json'), events[0][1])
        self.assertTrue(metadata['bracket_aborted'])
        self.assertEqual(metadata['bracket_resume'][0]['rc'], 0)

    def test_bracket_cleanup_failure_is_a_flag_and_still_attempts_pin(self):
        metadata = {'paths': {'measurement': str(self.root)}, 'inputs': {'bracket_session_id': 's'}}
        lane = DeskLane(self.root, self.root / 'loop')
        with patch.object(plan, 'ledger_head_status', return_value={'open_sessions': ['s']}), \
             patch('joulewise.calibration_ledger.abort_bracket_session', side_effect=ValueError('fixture')), \
             patch.object(plan, 'advance_ledger_pin', side_effect=plan.PinAdvanceError('fixture')) as advance:
            self.assertIn('records.pin_ledger', lane._advance(metadata))
        advance.assert_called_once()
        self.assertEqual(metadata['bracket_abort']['status'], 'FAILED')
