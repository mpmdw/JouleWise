"""Synthetic end-to-end: W1 -> C1..C8 -> T1..T3 through the real v4 arm route.

Real: the series generator and its --check on a mirror measurement root, the
session ``prepare --window`` selection, the shared ``bytes_h_session.measurement_view``
staging of each window kit, the session ``install`` with the real ``arm_checks``
(powermode, external-volume census, battery), the real R12 triage
(``v4_cadence.next_arm_triage``, fixed-8 ``calibration_stop``), the series binding
and the off-MBP packet producer. Synthetic boundaries only: host commands
(FakeArmHost), the shared prepare's model-presence/identity/plan-writer step,
the W1 registration check (needs the lead-signed receipt), the window sizing
(needs R1's W1 plan), the disk gate and the shared launchd installer, plus the
window outcomes (captures and eligible counts). No model, data or hardware.
"""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cad, v4_series as series
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_series as gen
from scripts import align_v4_session as session, bytes_h_session as h
from tests.align.test_v4_kit import FakeArmHost, ready_inputs

ROOT = Path(__file__).resolve().parents[2]
SPAM = series.SPAM


def mirror(target):
    """A measurement root: the checkout linked, the series kit generated fresh."""
    target.mkdir()
    for p in ROOT.iterdir():
        if p.name != 'configs':
            (target / p.name).symlink_to(p, target_is_directory=p.is_dir())
    for relative, omitted in (('configs', {'campaigns'}), ('configs/campaigns', {'align_v4_series'})):
        (target / relative).mkdir()
        for p in (ROOT / relative).iterdir():
            if p.name not in omitted:
                (target / relative / p.name).symlink_to(p, target_is_directory=p.is_dir())


def evidence(**overrides):
    rows = {row['id']: {'status': 'pass', 'basis': 'synthetic Air desk extract', 'evidence_sha256': 'e' * 64}
            for row in cad.NEXT_ARM_TRIAGE if row['source'] == cad.PACKET}
    rows.update(overrides)
    return rows


def w1_evidence():
    rows = evidence()
    for row in cad.NEXT_ARM_TRIAGE:
        if row['first_window_na'] and row['source'] == cad.PACKET:
            rows[row['id']] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
    return rows


class SeriesEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.shared = Path(tmp.name).resolve()
        cls.inputs, cls.slots = ready_inputs()
        cls.measurement = cls.shared / 'm'
        mirror(cls.measurement)
        with cls.synthetic_inputs():
            gen.generate(cls.measurement, source_root=cls.measurement)

    @classmethod
    def synthetic_inputs(cls):
        stack = ExitStack()
        stack.enter_context(patch.object(kit, 'read_inputs', side_effect=lambda root=None: json.loads(
            json.dumps(cls.inputs))))
        stack.enter_context(patch.object(kit, 'read_r1_slots', side_effect=lambda root=None: json.loads(
            json.dumps(cls.slots))))
        return stack

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        stack = self.synthetic_inputs()
        self.addCleanup(stack.close)
        stack.enter_context(patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.tmp / 'host'),
                                                    'HOME': str(self.tmp / 'home')}))
        # Synthetic boundaries (see module docstring).
        self.w1_checks = []
        stack.enter_context(patch.object(kit, 'generate', side_effect=lambda root, **kw: self.w1_checks.append(root)))
        stack.enter_context(patch.object(gen, 'require_sizing', return_value=None))
        stack.enter_context(patch.object(pilot.h, 'prepare', side_effect=self.shared_prepare))
        self.installed = []
        stack.enter_context(patch.object(pilot, 'install', side_effect=self.shared_install))
        self.manifest = gen.read_manifest(self.measurement)
        self.ledger = {'schema': series.LEDGER_SCHEMA, 'manifest_sha256': series.manifest_sha256(self.manifest),
                       'attempts': []}
        self.disk_config = self.tmp / 'r0-desk.json'
        config = json.loads((ROOT / 'configs/align/v4/r0_desk.json').read_text())
        config.update(disk_path=str(self.tmp), offloads=[], offloads_owed='none')
        self.disk_config.write_text(json.dumps(config))
        self.views = {}

    # -- synthetic boundaries ------------------------------------------------
    def shared_prepare(self, measurement_root, session_root, *, kit, pack_id, session_prefix,
                       ac_powermode=None, **_):
        """The shared prepare minus model presence, identity collection and the plan
        writer: the REAL measurement view stages the window kit."""
        source, target = Path(measurement_root).resolve(), Path(session_root).resolve()
        target.mkdir(parents=True)
        view, pack = h.measurement_view(source, target, kit=kit, pack_id=pack_id)
        self.views[pack_id] = (view, pack)
        state = {'schema_version': 'joulewise.bytes_h_session.v1', 'non_claim': True,
                 'session_id': session_prefix + 'synthetic', 'source_measurement_root': str(source),
                 'measurement_root': str(view), 'registration_dir': str(view / kit / 'registration'),
                 'session_root': str(target), 'preparation_status': 'SYNTHETIC_VIEW_ONLY',
                 'plan_path': str(target / 'custody/night_plan.json'), 'plan_sha256': None,
                 'inputs': {'custody_root': str(target / 'custody'), 'ac_powermode': ac_powermode},
                 'kit': str(kit), 'pack_id': pack_id}
        (target / 'staging').mkdir(exist_ok=True)
        h.write(target / 'session.json', state)
        return state

    def shared_install(self, session_root, **_):
        self.installed.append(Path(session_root))
        return {'exit_code': 0, 'synthetic_installer': True}

    # -- one arm --------------------------------------------------------------
    def arm(self, window, packet, *, n):
        root = self.tmp / f'session-{window}-{n}'
        session.prepare(self.measurement, root, window=window)
        path = self.tmp / f'packet-{window}-{n}.json'
        path.write_text(json.dumps(packet))
        host = FakeArmHost(mode=0)
        before = len(self.installed)
        try:
            session.install(root, runner=host, volume_runner=host, obc_off_attested_by='synthetic',
                            topup_completed_at=time.time() - 60, topup_source='synthetic',
                            next_arm_triage=path, w1_disk_config=self.disk_config,
                            disk_gate=lambda config: {'status': 'pass', 'offloads': []})
            error = None
        except ValueError as exc:
            error = str(exc)
        record = json.loads(sorted((root / 'staging').glob('v4-arm-*.json'))[-1].read_text())
        return root, record, error, len(self.installed) - before

    def outcome(self, window, attempt, *, captured=None, excluded=(), u_pass=True, final=True):
        if window == 'W1':
            row = {'attempt': f'W1#{attempt}', 'window': 'W1', 'record_sha256': 'a' * 64,
                   'captured_members': 18 if captured is None else len(captured), 'status': 'final'}
        else:
            members = series.window(self.manifest, window)['members']
            row = series.ledger_row_from_desk(
                self.manifest, window, attempt, record_sha256='a' * 64, u_pass=u_pass,
                members=[{'run_id': m['run_id'], 'captured': captured is None or m['ordinal'] in captured,
                          'excluded': m['ordinal'] in excluded} for m in members])
            row.pop('flags')
        self.ledger['attempts'].append(row)
        if final and row['status'] == 'provisional':
            self.ledger = series.finalize_attempt(self.ledger, row['attempt'], eligibility_sha256='b' * 64)

    def packet(self, **kw):
        kw.setdefault('code_or_config_changed', False)
        kw.setdefault('checks', evidence())
        return series.build_packet(self.manifest, self.ledger, **kw)

    def assert_armed(self, window, record, error, calls, root):
        self.assertIsNone(error, record['reasons'])
        self.assertTrue(record['admitted'])
        self.assertEqual(record['series_window'], window)
        self.assertEqual(record['series_binding'], [])
        self.assertEqual(calls, 1)
        state = json.loads((root / 'session.json').read_text())
        spec = series.window(self.manifest, window)
        self.assertEqual(state['series']['window'], window)
        self.assertEqual(state['pack_id'], spec['pack_id'])
        # The real measurement view staged this window's 22 members (two stages of 11).
        view, pack = self.views[spec['pack_id']]
        staged = []
        for stage in ('episodes-a', 'episodes-b'):
            manifest = json.loads((pack / 'members' / f'{spec["pack_id"]}-{stage}' / 'order_manifest.json').read_text())
            staged += [row['run_id'] for row in manifest['executed_order']]
        self.assertEqual(staged, [m['run_id'] for m in spec['members']])

    # -- scenarios ------------------------------------------------------------
    def test_full_series_w1_c1_to_c8_t1_to_t3(self):
        trace = []
        # W1 itself arms through the W1 kit; its packet is built by the same producer.
        w1 = self.packet(checks=w1_evidence())
        self.assertEqual((w1['series']['window'], w1['previous_window']), ('W1', 'R1'))
        self.assertTrue(cad.next_arm_triage(w1, {'series_powermode': True, 'external_volume': True,
                                                 'charging_battery': True})['admitted'])
        self.outcome('W1', 1)
        # After W1 the full desk must pass before C1: a deferred desk refuses the arm.
        root, record, error, calls = self.arm('C1', self.packet(checks=evidence(full_desk_gate={
            'status': 'deferred', 'basis': 'desk running on the Air', 'evidence_sha256': 'e' * 64})), n=0)
        self.assertIn('full desk must pass', error)
        self.assertEqual(calls, 0)
        n = 1
        while True:
            nxt = series.plan_next(self.manifest, self.ledger)
            if nxt['decision'] != 'arm':
                break
            window, attempt = nxt['window'], nxt['attempt']
            root, record, error, calls = self.arm(window, self.packet(), n=n)
            n += 1
            self.assert_armed(window, record, error, calls, root)
            self.assertEqual(json.loads((root / 'session.json').read_text())['series_attempt'], attempt)
            trace.append(f'{window}#{attempt}')
            if window == 'C3' and attempt == 1:
                self.outcome(window, attempt, captured=())          # zero-capture refusal: same seeds again
            elif window == 'C5':
                self.outcome(window, attempt, excluded=(6, 7, 8))   # attrition: 5/6 eligible
            else:
                self.outcome(window, attempt)
        self.assertEqual(trace, ['C1#1', 'C2#1', 'C3#1', 'C3#2', 'C4#1', 'C5#1', 'C6#1', 'C7#1', 'C8#1',
                                 'T1#1', 'T2#1', 'T3#1'])
        self.assertEqual((nxt['decision'], nxt['reason']), ('stop', 'series_complete'))
        self.assertEqual(nxt['calibration']['eligible_by_pair'], {'spam': 54, 'bank': 55})
        self.assertEqual(nxt['calibration']['zero_capture_refusals'], 1)
        self.assertTrue(self.w1_checks)            # every series prepare/install re-checked the W1 kit
        print('SERIES_E2E ' + json.dumps({'armed': trace, 'final': nxt['reason'],
                                          'eligible_by_pair': nxt['calibration']['eligible_by_pair']}))

    def advance(self, through):
        self.outcome('W1', 1)
        for window in [f'C{i}' for i in range(1, through + 1)]:
            self.outcome(window, 1)

    def test_a_packet_for_another_window_is_refused_before_the_installer(self):
        self.advance(2)
        root, record, error, calls = self.arm('C4', self.packet(), n=1)    # the packet is for C3
        self.assertFalse(record['admitted'])
        self.assertEqual(calls, 0)
        self.assertTrue(any('series packet is for' in r and 'C3' in r for r in record['reasons']))

    def test_an_unbound_packet_cannot_arm_a_series_window(self):
        self.advance(1)
        bare = self.packet()
        del bare['series']
        root, record, error, calls = self.arm('C2', bare, n=1)
        self.assertEqual(calls, 0)
        self.assertIn('series_binding: series binding missing from the next-arm packet', record['reasons'])

    def test_two_zero_capture_attempts_escalate_and_refuse(self):
        self.advance(4)
        self.outcome('C5', 1, captured=())
        self.outcome('C5', 2, captured=())
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            self.packet()
        root, record, error, calls = self.arm('C5', self.packet(window='C5'), n=3)
        self.assertEqual(calls, 0)
        self.assertTrue(any('escalate_to_lead' in r for r in record['reasons']))

    def test_t1_refuses_on_pending_or_insufficient_calibration(self):
        self.advance(7)
        self.outcome('C8', 1, final=False)
        root, record, error, calls = self.arm('T1', self.packet(window='T1'), n=1)
        self.assertEqual(calls, 0)
        self.assertTrue(any('pending_final_eligibility' in r for r in record['reasons']))
        self.ledger = series.finalize_attempt(self.ledger, 'C8#1', eligibility_sha256='b' * 64,
                                              eligible_benign={'spam': 7, 'bank': 7})
        root, record, error, calls = self.arm('T1', self.packet(), n=2)
        self.assertEqual(calls, 1)

    def test_insufficient_calibration_is_terminal(self):
        self.outcome('W1', 1)
        for i in range(1, 9):
            # U1-U3 failure bars pool entry: four such windows leave 28 < 39 per pair.
            self.outcome(f'C{i}', 1, u_pass=(i % 2 == 0))
        self.assertEqual(series.plan_next(self.manifest, self.ledger)['reason'], 'insufficient_calibration')
        root, record, error, calls = self.arm('T1', self.packet(window='T1'), n=1)
        self.assertEqual(calls, 0)
        self.assertTrue(any('insufficient_calibration' in r for r in record['reasons']))

    def test_d_alias_selects_the_calibration_kit(self):
        self.advance(0)
        root, record, error, calls = self.arm('D1', self.packet(), n=1)
        self.assert_armed('C1', record, error, calls, root)

    def test_desk_routes_the_window_kit(self):
        root = self.tmp / 'session-desk'
        session.prepare(self.measurement, root, window='T2')
        with patch.object(pilot, 'desk', return_value={'harvest_status': 'not_run'}) as desk:
            session.desk(root, harvest=False)
        self.assertEqual(desk.call_args.kwargs['kit'], Path(series.window(self.manifest, 'T2')['kit']))
        self.assertIs(desk.call_args.kwargs['extra_checks'], session.powermode_desk_check)


if __name__ == '__main__':
    unittest.main()
