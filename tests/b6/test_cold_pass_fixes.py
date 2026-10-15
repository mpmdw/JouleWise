"""Block-6 cold-pass regressions. All collection and pulses are synthetic."""
from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import patch

from joulewise.b5.harvest import build_roster, l4_exclusion_inputs
from joulewise.b6 import acceptance, calibration, precheck, queue, registration, survivor_screen
from joulewise.b6.driver_lane import metadata_path, read, write
from joulewise.b6.lanes import SessionLine
from tests.b6 import support
from tests.b6.round_support import Round
from tests.b6.support import DeskCase, ROOT, PACKS
from tests.test_b6_registration import registrations
from tests import test_harvest_b5_window as windows


def tearDownModule():
    windows.tearDownModule()
    windows._TEMPLATE = None


class ColdPassTests(DeskCase):
    def test_real_roles_counts_and_synthetic_reference_losses(self):
        for pack in PACKS:
            t = support.tree(pack)
            root = ROOT / 'configs/campaigns' / PACKS[pack]
            prep = support.prepared(self.root / pack, tree=t)
            roster, _ = l4_exclusion_inputs(build_roster(root, ROOT), {}, plan_id=None, attempt=None)
            prep = replace(prep, roster=roster)
            rows = [{'sequence': i, 'disposition': 'valid', 'exact_bound_lexeme_s': '0.028'} for i in range(24)]
            ev = precheck.synthetic_session(root, ROOT, rows, {})
            result = acceptance.ACCEPTANCE.evaluate(prep, ev)
            self.assertEqual(result.verdict, 'ACCEPT', result.reasons)
            self.assertTrue(result.record['cells'])
            self.assertTrue(all(n >= 5 for strata in result.record['cells'].values() for n in strata.values()))
            self.assertEqual(result.record['neg8']['survivors'], {'start': 3, 'midpoint': 1, 'end': 3})
            roles = acceptance._stage_roles(t)[1]
            self.assertEqual(sum(role == 'diagnostic_reference' for role in roles.values()), 2 if pack == 'gamma' else 0)
            for role in ('start', 'end', 'corpus'):
                stages = tuple(replace(s, members=tuple(replace(m, status='failed') if roles.get(m.run_id) == role else m
                                                       for m in s.members)) for s in ev.stages)
                result = acceptance.ACCEPTANCE.evaluate(prep, replace(ev, stages=stages))
                self.assertIn('neg8.survivor_screen_undefined', result.reasons)
                self.assertEqual(result.record['neg8']['reason'], 'references_insufficient')

    def test_calibration_path_file_is_absent_and_session_helpers_are_number_bearing(self):
        path = self.root / 'file'
        path.write_text('{}')
        self.assertEqual(calibration.read_own_capture(path), calibration.Capture(None, 'absent'))
        for name in ('idle_wait', 'agent_pause', 'sleep_guard'):
            self.assertIn(f'joulewise/b6/{name}.py', registration.NUMBER_BEARING_PATHS)

    def test_stop_kinds_physics_n1_and_structural(self):
        prep, ev = support.prepared(self.root), support.session()
        for stop, physical, structural in [('pre_calibration_screen_failed', False, False),
                ('pre_calibration_capture_failed', False, False), ('reservation_failed', False, True),
                *[(code, True, False) for code in acceptance.PHYSICS_STOP_REASONS]]:
            result = acceptance.ACCEPTANCE.evaluate(prep, replace(ev, stop_reason=stop, captures=()))
            self.assertEqual(result.verdict, 'EXCLUDE')
            self.assertFalse(result.counting)
            self.assertEqual(result.structural, structural, stop)
            self.assertEqual(result.record['physics_stop'], physical, stop)
            if not physical and not structural:
                self.assertIn('calibration.bracket_incomplete', result.reasons)

    def test_archive_spares_are_unplanned_and_unrun_reserves_are_silent(self):
        pack = ROOT / 'configs/campaigns' / PACKS['alpha']
        roster, _ = l4_exclusion_inputs(build_roster(pack, ROOT), {}, plan_id=None, attempt=None)
        archive = self.root / 'archive'
        write(archive / 'derived/roster.json', {'pack_id': PACKS['alpha'], **roster})
        (archive / 'derived/flags.jsonl').write_text('')
        write(archive / 'night/result.json', {'chain_exit_code': 0})
        plan = {'pack_id': PACKS['alpha'], 'pack_root': str(pack), 'spare_retries': False}
        for m in roster['members']:
            if not str(m['stage_id']).endswith('.spares'):
                write(archive / 'sources/claim-runs' / m['run_id'] / 'metadata.json', {'status': 'succeeded'})
        ev = acceptance.evidence_from_archive(archive, plan, self.root / 'absent')
        self.assertFalse(any(m.role == 'spare' for s in ev.stages for m in s.members))
        self.assertEqual(sum(len(s.members) for s in ev.stages), 125)
        self.assertNotIn('plan.spare_retry_present', acceptance.ACCEPTANCE.evaluate(support.prepared(self.root), ev).flags)
        enabled = acceptance.evidence_from_archive(archive, {**plan, 'spare_retries': True}, self.root / 'absent')
        self.assertIn('plan.spare_retry_present', acceptance.ACCEPTANCE.evaluate(support.prepared(self.root), enabled).flags)
        write(archive / 'sources/claim-runs/neg8-window-start-spare-1/metadata.json', {'status': 'succeeded'})
        ev = acceptance.evidence_from_archive(archive, plan, self.root / 'absent')
        spare_stage = next(s for s in ev.stages if s.stage_id.endswith('.spares'))
        self.assertEqual(spare_stage.kind, 'unplanned_collection')
        self.assertEqual(spare_stage.members[0].role, 'spare')
        result = acceptance.ACCEPTANCE.evaluate(support.prepared(self.root), ev)
        self.assertNotIn('structure.missing_stage_bundles', result.reasons)
        self.assertIn('plan.spare_retry_present', result.flags)

    def test_driver_terminal_vocabulary_without_chain_stop_and_missing_terminal(self):
        archive = self.root / 'archive'
        write(archive / 'derived/roster.json', {'members': [{'run_id': 's', 'stage_id': 'science'}]})
        (archive / 'derived/flags.jsonl').write_text('')
        prep = support.prepared(self.root)
        for name in ('hazard_result.json', 'result.json'):
            for code in acceptance.PHYSICS_STOP_REASONS - {'operative_bound_above_stop'}:
                terminal = archive / 'sources/night-custody/night' / name
                write(terminal, {'aborted_reason': code, 'chain_exit_code': -15})
                ev = acceptance.evidence_from_archive(archive, {'pack_id': 'desk-pack'}, self.root / 'absent')
                result = acceptance.ACCEPTANCE.evaluate(prep, ev)
                self.assertEqual(ev.stop_reason, code)
                self.assertTrue(result.record['physics_stop'])
                self.assertNotIn('structure.chain_crashed', result.reasons)
                terminal.unlink()
        ev = acceptance.evidence_from_archive(archive, {'pack_id': 'desk-pack'}, self.root / 'absent')
        self.assertIn('structure.chain_crashed', acceptance.ACCEPTANCE.evaluate(prep, ev).reasons)

    def test_gamma_diagnostics_enter_neither_midpoint_mean_nor_loss(self):
        t = support.tree('gamma')
        stages, roles = acceptance._stage_roles(t)
        members = [{'run_id': rid, 'role': role, 'stage_id': stages[rid],
                    'status': 'failed' if role == 'diagnostic_reference' else 'succeeded'} for rid, role in roles.items()]
        def energy(member):
            value = 1000 if member['role'] == 'diagnostic_reference' else 37
            return {'gross': value, 'idle_subtracted': value - 1}
        result = survivor_screen.screen({'members': members}, {}, energy, support.document())
        self.assertEqual(result.counts['midpoint'], 1)
        self.assertNotIn('neg8.midpoint_lost', result.flags)
        self.assertEqual(result.withheld['families']['gross']['means_j']['midpoint'], 37)
        from joulewise.b6.acceptance_interface import StageEvidence
        ev = support.session()
        midpoint = next(m for m in ev.stages[1].members if m.role == 'midpoint')
        absent = StageEvidence('midpoint', 'campaign_collection', 1,
            (replace(midpoint, stage_id='midpoint', status='failed', runtime={'bundle_present': False}),))
        other_refs = replace(ev.stages[1], members=tuple(m for m in ev.stages[1].members if m.role != 'midpoint'))
        result = acceptance.ACCEPTANCE.evaluate(support.prepared(self.root), replace(ev, stages=(absent, ev.stages[0], other_refs)))
        self.assertEqual(result.verdict, 'ACCEPT', result.reasons)
        self.assertNotIn('structure.missing_stage_bundles', result.reasons)

    def test_queue_uses_acceptance_and_families_and_next_launch_time(self):
        catalog = support.prepared(self.root).catalog
        reg = registrations()['alpha']
        for verdict, counting, expected in [('ACCEPT', True, 'counting'), ('EXCLUDE', False, 'not_counting'),
                                           ('HARVEST_RERUN', False, 'pending_harvest'), ('UNAVAILABLE', False, 'pending_registration')]:
            line = SessionLine('s', ('alpha',), acceptance_verdict=verdict, counting=counting,
                               excluding_reasons=('calibration.bracket_incomplete',), window_flags=('model.identity_mismatch',))
            outcome = queue.outcome(reg, line, catalog)
            self.assertEqual(outcome['status'], expected)
            if expected == 'not_counting':
                self.assertEqual(outcome['cause'], 'CALIBRATION')
        from datetime import datetime
        for p in PACKS:
            committed = __import__('joulewise.b6.pack_registration', fromlist=['load']).load(ROOT / f'configs/b6/packs/{p}/registration.json')
            self.assertEqual(committed.stopping['end_t0_before'], '2026-11-02T00:00:00-08:00')
            close = datetime.fromisoformat(committed.stopping['end_t0_before']).timestamp()
            self.assertIsNone(queue.done_reason({}, committed, close - 500))
            self.assertEqual(queue.done_reason({}, committed, close - 500, next_t0=close), 'short:0')

    def test_reharvest_restores_compressed_sources_before_using_fresh_root(self):
        from joulewise import desk_compress
        from joulewise.b6.desk_lane import DeskLane
        from joulewise.b6.lanes import Done, Prepared
        archive, custody, runs = (self.root / name for name in ('archive', 'custody', 'runs'))
        write(archive / 'harvest.json', {'verdict': 'COLLECTED'})
        write(custody / 'night/chain.exited', {'exit_code': 0})
        raw = runs / 'r/raw/powermetrics.plist'
        raw.parent.mkdir(parents=True)
        body = b'synthetic raw\n' * 100000
        raw.write_bytes(body)
        rc, _ = desk_compress.compress(archive=archive, custody=custody, runs_roots=[runs])
        self.assertEqual(rc, 0)
        self.assertFalse(raw.exists())
        prepared = Prepared('s', str(custody / 'night_plan.json'), str(custody / 'night/result.json'), 1)
        write(metadata_path(prepared), {'paths': {'archive': str(archive), 'export': str(self.root / 'export'),
             'staging': str(self.root / 'staging')}})
        lane = DeskLane(ROOT, self.root / 'loop')
        def after_restore(*args):
            self.assertEqual(raw.read_bytes(), body)
            fresh = read(metadata_path(prepared))['paths']['archive']
            self.assertNotEqual(fresh, str(archive))
            self.assertFalse(Path(fresh).exists())
            return 'desk-called'
        with patch.object(lane, 'session_desk', side_effect=after_restore):
            self.assertEqual(lane.reharvest(prepared, Done()), 'desk-called')
        self.assertTrue((archive / 'harvest.json').is_file())

    def test_pending_harvest_never_compresses_and_exclusions_are_public_codes_only(self):
        from types import SimpleNamespace
        from joulewise.b6.desk_lane import DeskLane
        from joulewise.b6.lanes import Done, Prepared
        from scripts import fixture_orphan_census
        command = "  12345 1 Thu Sep  3 10:20:30 2026 123 python -c import sys; sys.path.insert(0, '/tmp/test'); from scripts import harvest_b6_session as w\\012def fault(): raise RuntimeError('synthetic acceptance program fault')\n"
        self.assertEqual(fixture_orphan_census.census(command, fixture_orphan_census.load_signatures())[0]['signature'],
                         'b6-synthetic-acceptance-fault')
        prepared = Prepared('s', str(self.root / 'custody/night_plan.json'), str(self.root / 'custody/night/result.json'), 1)
        paths = {key: str(self.root / key) for key in ('archive', 'custody', 'staging', 'export')}
        paths['measurement'] = str(ROOT)
        Path(paths['staging']).mkdir()
        write(metadata_path(prepared), {'paths': paths, 'packs': ['alpha'], 'runs_roots': []})
        structure = {'verdict': 'STRUCTURE_OK', 'reasons': [], 'chain_stopped': None, 'physical_stop': None,
                     'harvest_verdict': 'COLLECTED', 'flags': {'STRUCTURE': {}}, 'per_roster_stage': [], 'chain_seconds': 0}
        catalog = support.prepared(self.root / 'reg').catalog
        restricted = next(code for code in catalog.codes if catalog.entry(code)['blinding'] == 'RESTRICTED')
        for rc, verdict in [(4, 'ACCEPT'), (5, 'ACCEPT'), (6, 'UNAVAILABLE'), (0, 'HARVEST_RERUN'), (0, 'ACCEPT')]:
            write(Path(paths['archive']) / 'derived/b6-acceptance.json', {'verdict': verdict, 'counting': verdict == 'ACCEPT',
                'excluding': [{'code': restricted, 'scope': 'window'}, {'code': 'calibration.bracket_incomplete', 'scope': 'window'}]})
            lane = DeskLane(ROOT, self.root / 'loop', lambda *a, **k: SimpleNamespace(returncode=rc, stdout='', stderr=''))
            with patch.object(lane, '_advance', return_value=[]), \
                 patch('joulewise.b6.desk_lane.session_structure.check', return_value=structure.copy()), \
                 patch('joulewise.b6.desk_lane.desk_compress.compress', return_value=(0, {})) as compress:
                line = lane.session_desk(prepared, Done())
            self.assertEqual(compress.call_count, int(rc == 0 and verdict == 'ACCEPT'))
            self.assertNotIn(restricted, line.excluding_reasons)


class FullRoundTests(DeskCase):
    def run_round(self, pack='alpha', *, registration_ready=True, **control):
        root = self.root / ('case-' + str(len(list(self.root.iterdir()))))
        root.mkdir()
        r = Round(root, full_pack=pack)
        r.until('SESSION_RUN')
        if registration_ready:
            r.register_acceptance()
        write(r.control, {**read(r.control), **control})
        r.until('ROTATE')
        print('E2E', pack, control or 'completed', r.state()['attempts'][0]['outcomes'][pack], flush=True)
        if not control.get('stop') and r.state()['attempts'][0]['line']['harvest_rc'] == 0:
            from joulewise.b6.lanes import Prepared
            metadata = read(metadata_path(Prepared(**r.state()['session']['prepared'])))
            record = read(Path(metadata['paths']['archive']) / 'derived/b6-acceptance.json')
            self.assertEqual(len(record['cells']), 2)
            self.assertTrue(all(n == 10 for strata in record['cells'].values() for n in strata.values()), record['cells'])
        return r, r.state()['attempts'][0]

    def test_completed_full_alpha(self):
        r, attempt = self.run_round()
        self.assertEqual(attempt['outcomes']['alpha'], {'status': 'counting', 'cause': None}, attempt['line'])
        self.assertTrue(attempt['line']['compressed'])

    def test_lost_start_reference_without_spare_counts(self):
        r, attempt = self.run_round(missing=['neg8-window-start-r1'])
        self.assertEqual(attempt['outcomes']['alpha'], {'status': 'counting', 'cause': None}, attempt['line'])
        self.assertNotIn('plan.spare_retry_present', attempt['line']['window_flags'])
        self.assertIn('neg8.reference_lost', attempt['line']['window_flags'])

    def test_gamma_lost_midpoint_counts_and_overrides_b5_claim(self):
        r, attempt = self.run_round('gamma', missing=['neg8-window-midpoint'])
        self.assertEqual(attempt['outcomes']['gamma'], {'status': 'counting', 'cause': None}, attempt['line'])
        from joulewise.b6.lanes import Prepared
        metadata = read(metadata_path(Prepared(**r.state()['session']['prepared'])))
        structure = read(Path(metadata['paths']['staging']) / 'structure.json')
        self.assertTrue(structure['counting'], structure)
        self.assertEqual(structure['counting_source'], 'b6_acceptance')
        self.assertIn('neg8.midpoint_lost', attempt['line']['window_flags'])

    def test_physical_and_opening_no_bound_stops_rotate(self):
        for stop, status, cause in [('night_aborted_agent_present', 'physics_stopped', 'agent'),
                ('operative_bound_above_stop', 'physics_stopped', 'calibration.operative_bound_above_stop'),
                ('pre_calibration_screen_failed', 'not_counting', 'CALIBRATION,NEG8,ROSTER')]:
            with self.subTest(stop=stop):
                r, attempt = self.run_round(stop=stop)
                self.assertEqual(attempt['outcomes']['alpha'], {'status': status, 'cause': cause}, attempt['line'])
                self.assertTrue(attempt['line']['structure_ok'])
                r.loop.tick()
                r.loop.tick()
                self.assertEqual(r.state()['session']['packs'], ['beta'])

    def test_exit4_and_acceptance_unavailable_reharvest_into_new_archive(self):
        from joulewise.b6.lanes import Prepared
        for rc in (4, 6):
            with self.subTest(rc=rc):
                r, attempt = self.run_round(registration_ready=rc == 4, **({'harvest_fault': 4} if rc == 4 else {}))
                line = attempt['line']
                self.assertEqual(line['harvest_rc'], rc, line)
                self.assertEqual(attempt['outcomes']['alpha']['status'], 'pending_harvest' if rc == 4 else 'pending_registration')
                self.assertFalse(line['compressed'])
                prepared = Prepared(**r.state()['session']['prepared'])
                old = Path(read(metadata_path(prepared))['paths']['archive'])
                before = (old / 'harvest.json').read_bytes()
                if rc == 6:
                    r.register_acceptance()
                r.loop.control('reharvested', session_id=attempt['session_id'])
                outcome = r.state()['reharvested'][attempt['session_id']]['alpha']
                self.assertEqual(outcome, {'status': 'counting', 'cause': None})
                print('E2E reharvest', rc, outcome, flush=True)
                current = Path(read(metadata_path(prepared))['paths']['archive'])
                self.assertNotEqual(current, old)
                self.assertEqual((old / 'harvest.json').read_bytes(), before)
                self.assertTrue((current / 'derived/b6-acceptance.json').is_file())
