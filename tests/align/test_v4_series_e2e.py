"""Synthetic end-to-end cadence: W1 -> C1..C8 -> T1..T3 through the real v4 arm route.

Opus scenario suite ported onto the merged series (RUN_STATE 226 R15). The
HAZARD_PACK chain itself is replayed by ``test_v4_series.ProductionPathTests``;
this suite drives the cadence and its refusals cheaply.

Real code: the series builder/admission/--check on a mirror measurement root,
``prepare --window-id`` selection, the shared ``bytes_h_session.measurement_view``
staging each kit, ``install`` with the series binding (W1 included), the real
``arm_checks`` (powermode, external-volume census, battery log, R12 triage with
the arm-derived identity) and the packet producer. Synthetic boundaries: host
commands (FakeArmHost), the shared prepare's model-presence/identity/plan-writer
step, the W1 registration ``--check`` (needs the lead-signed receipt), the disk
gate, the launchd installer, and the window outcomes. No model, data or hardware.
"""
from contextlib import ExitStack
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cad, v4_registration
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_series as s
from scripts import align_v4_session as session, bytes_h_session as h
from tests.align.test_v4_cadence import arm_seams, write_battery_log
from tests.align.test_v4_kit import FakeArmHost, ready_inputs

ROOT = Path(__file__).resolve().parents[2]
COMMIT = 'a' * 40
SIGNATURE = 'lead: SYNTHETIC-ONLY 2026-11-08'


def write(root, path, value):
    target = Path(root) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(value if isinstance(value, bytes) else s.raw_json(value))
    return target


def ref(path, pointer=''):
    return dict(path=str(path), sha256=s.sha(Path(path).read_bytes()), pointer=pointer)


def mirror(target):
    """A measurement root: the checkout linked; the W1 kit and series directories real."""
    target.mkdir()
    for p in ROOT.iterdir():
        if p.name != 'configs':
            (target / p.name).symlink_to(p, target_is_directory=p.is_dir())
    for relative, omitted in (('configs', {'campaigns'}), ('configs/campaigns', {'align_v4'})):
        (target / relative).mkdir()
        for p in (ROOT / relative).iterdir():
            if p.name not in omitted and not p.name.startswith('align_v4_'):
                (target / relative / p.name).symlink_to(p, target_is_directory=p.is_dir())
    shutil.copytree(ROOT / kit.KIT, target / kit.KIT)


class SeriesCadenceEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.shared = Path(tmp.name).resolve()
        cls.inputs, cls.slots = ready_inputs()
        cls.measurement = m = cls.shared / 'm'
        mirror(m)
        with cls.synthetic_inputs():
            kit.generate(m, source_root=m)                       # synthetic-ready W1 kit (ac_powermode 0)
            for window in s.load(m)['windows'][1:]:
                if window.get('armable') is not False:           # C11/C12 hold reserve seeds only (cap C10)
                    s.generate(m, window['id'])                  # materialize every armable C/T kit
        passed = write(cls.shared, 'synthetic-clearance.json', 'pass')
        manifest = s.load(m)
        write(m, s.ADMISSION, dict(
            schema=s.ADMISSION_SCHEMA, manifest_sha256=s.sha((m / s.MANIFEST).read_bytes()),
            w1_collection_sha256=s.sha((m / kit.KIT / 'collection_plan.json').read_bytes()),
            lead_signature=SIGNATURE,
            choices={k: manifest[k] for k in ('d_mapping', 'test_windows', 'test_shape', 'sentinel')},
            evidence={k: ref(passed) for k in ('scorer_fit_contract', 'seed_allocation', 'r13_r14_gate',
                                               'paired_build_agreement', 'w1_clearance')}))
        cls.admission = (m / s.ADMISSION).read_bytes()

    @classmethod
    def synthetic_inputs(cls):
        stack = ExitStack()
        stack.enter_context(patch.object(kit, 'read_inputs', side_effect=lambda root=None: deepcopy(cls.inputs)))
        stack.enter_context(patch.object(kit, 'read_r1_slots', side_effect=lambda root=None: deepcopy(cls.slots)))
        return stack

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        (self.measurement / s.ADMISSION).write_bytes(self.admission)     # undo any threshold freeze
        stack = self.synthetic_inputs()
        self.addCleanup(stack.close)
        stack.enter_context(patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.tmp / 'host'),
                                                    'HOME': str(self.tmp / 'home')}))
        self.w1_checks = []
        # Series/cadence witnesses isolate the OS clock preflight; round-3
        # reliability tests exercise it with preserved synthetic timex bytes.
        stack.enter_context(patch.object(session, 'frequency_word_preflight',
                                        return_value={'ok': True, 'synthetic': True}))
        stack.enter_context(patch.object(session, 'frequency_word_pre_t0',
                                        return_value={'ok': True, 'synthetic': True}))
        stack.enter_context(patch.object(kit, 'generate', side_effect=lambda root, **kw: self.w1_checks.append(root)))
        stack.enter_context(patch.object(pilot.h, 'prepare', side_effect=self.shared_prepare))
        stack.enter_context(patch.object(session, '_prepare_weight_digests',
                                        return_value={'ok': True, 'synthetic': True}))
        stack.enter_context(patch.object(session, 'runtime_stack_preflight',
            return_value={'ok': True, 'reasons': [], 'synthetic': True}))
        stack.enter_context(patch.object(session, 'held_window_check',
            return_value={'ok': True, 'reasons': [], 'synthetic': True}))
        self.installed = []
        stack.enter_context(patch.object(pilot, 'install', side_effect=self.shared_install))
        self.manifest = s.load(self.measurement)
        self.history = []
        self.disk_config = self.tmp / 'r0-desk.json'
        config = json.loads((ROOT / 'configs/align/v4/r0_desk.json').read_text())
        config.update(disk_path=str(self.tmp), offloads=[], offloads_owed='none')
        self.disk_config.write_text(json.dumps(config))
        self.views = {}

    # -- synthetic boundaries ------------------------------------------------
    def shared_prepare(self, measurement_root, session_root, *, kit, pack_id, session_prefix,
                       ac_powermode=None, **_):
        """The shared prepare minus model presence, identity collection and the plan
        writer: the REAL measurement view stages the selected kit."""
        source, target = Path(measurement_root).resolve(), Path(session_root).resolve()
        target.mkdir(parents=True)
        view, pack = h.measurement_view(source, target, kit=kit, pack_id=pack_id)
        self.views[pack_id] = (view, pack)
        state = {'schema_version': 'joulewise.bytes_h_session.v1', 'non_claim': True,
                 'session_id': session_prefix + 'synthetic', 'source_measurement_root': str(source),
                 'measurement_root': str(view), 'registration_dir': str(view / kit / 'registration'),
                 'session_root': str(target), 'preparation_status': 'STAGED',
                 'plan_path': str(target / 'custody/night_plan.json'), 'plan_sha256': None,
                 'inputs': {'custody_root': str(target / 'custody'), 'ac_powermode': ac_powermode,
                            'pack_root': str(pack)},
                 'pack_id': pack_id, 't0_epoch_s': time.time() + 600}
        (target / 'staging').mkdir(exist_ok=True)
        h.write(target / 'session.json', state)
        return state

    def shared_install(self, session_root, **_):
        self.installed.append(Path(session_root))
        return {'exit_code': 0, 'synthetic_installer': True}

    # -- ledger and packets -----------------------------------------------------
    def outcome(self, window, *, captured=22, excluded=0, u_pass=True, status='final', desk=None):
        if window == 'W1':
            return None        # the series history starts after W1 (W1 is the previous window of C1)
        n = sum(1 for a in self.history if a.get('window_id') == window) + 1
        spam = bank = 0
        if s.selected(self.manifest, window)['role'] == 'calibration' and captured:
            spam = bank = 0 if u_pass is False else 7     # U1-U3 FAIL bars pool entry (R15)
            spam = max(0, spam - excluded)
        row = dict(window_id=window, attempt_id=window if n == 1 else f'{window}#{n}', captured_members=captured,
                   eligible_benign=dict(spam=spam, bank=bank), status=status)
        if s.selected(self.manifest, window)['role'] == 'calibration' and captured and u_pass is False:
            row['barred'] = 'u1_u3_fail'           # R22-2: a U1-U3 FAIL is a structural bar, replaced not counted
        path = write(self.tmp / 'receipts', row['attempt_id'].replace('#', '-') + '.json', row)
        entry = dict(row, evidence=ref(path))
        if desk is not None:
            entry['desk_eligible_benign'] = desk
        self.history.append(entry)
        return entry

    def checks(self, *, first=False, **overrides):
        statuses = {r['id']: ('recorded' if r.get('gating', True) is False else
                              'not_applicable' if first and r['first_window_na'] else 'pass')
                    for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET}
        statuses.update(overrides)
        path = write(self.tmp, f'triage-{time.time_ns()}.json', statuses)
        return {k: dict(status=v, basis='synthetic committed source receipt', evidence=ref(path, '/' + k))
                for k, v in statuses.items()}

    def packet(self, window, **checks):
        return s.make_packet(self.measurement, window, self.history,
                             self.checks(first=window == 'W1', **checks), record_commit=COMMIT,
                             last_desk_passed_artifact_set_sha256=v4_registration.artifact_set_digest(self.measurement),
                             valid_until_epoch_s=1000.0, now_epoch_s=500.0, commit_check=lambda root, commit: True)

    def next_window(self):
        rows, nxt, _, _ = s.calibration_rows(self.manifest, self.history)
        return nxt

    def freeze(self):
        rows, _, _, _ = s.calibration_rows(self.manifest, self.history)
        freeze = write(self.tmp, 'threshold-freeze.json', dict(
            status='pass', manifest_sha256=s.sha((self.measurement / s.MANIFEST).read_bytes()),
            calibration_rows_sha256=s.sha(s.raw_json(rows))))
        admission = json.loads((self.measurement / s.ADMISSION).read_bytes())
        admission['evidence']['test_threshold_freeze'] = ref(freeze)
        write(self.measurement, s.ADMISSION, admission)

    # -- one arm ---------------------------------------------------------------
    def arm(self, window, packet, *, n):
        root = self.tmp / f'session-{window}-{n}'
        session.prepare(self.measurement, root, window_id=window)
        path = self.tmp / f'packet-{window}-{n}.json'
        path.write_text(json.dumps(packet))
        host = FakeArmHost(mode=0)
        log = write_battery_log(self.tmp / f'battery-{window}-{n}.jsonl', time.time())
        before = len(self.installed)
        try:
            session.install(root, runner=host, volume_runner=host, obc_off_attested_by='synthetic',
                            battery_log=log, next_arm_triage=path, w1_disk_config=self.disk_config,
                            **arm_seams(),
                            disk_gate=lambda config: {'status': 'pass', 'offloads': []})
            error = None
        except ValueError as exc:
            error = str(exc)
        record = json.loads(sorted((root / 'staging').glob('v4-arm-*.json'))[-1].read_text())
        return root, record, error, len(self.installed) - before

    def assert_armed(self, window, record, error, calls, root):
        self.assertIsNone(error, record['reasons'])
        self.assertTrue(record['admitted'])
        self.assertEqual((record['series_window'], record['series_binding']), (window, []))
        self.assertEqual(calls, 1)
        state = json.loads((root / 'session.json').read_text())
        self.assertEqual(state['v4_series']['window_id'], window)
        if window == 'W1':
            return
        spec = s.selected(self.manifest, window)
        view, pack = self.views[s.pack_id(window)]
        staged = []
        for stage in ('episodes-a', 'episodes-b'):
            order = json.loads((pack / 'members' / f'{s.pack_id(window)}-{stage}' / 'order_manifest.json').read_text())
            staged += [row['run_id'] for row in order['executed_order']]
        self.assertEqual(len(staged), len(spec['members']))
        tree = json.loads((pack / 'plan_tree.json').read_text())
        units = [u['identity_unit_id'] for u in tree['arm_attachments']['identity_pin_projection']['identity_units']]
        self.assertEqual(sum(u.startswith(kit.D_TAG + '-') for u in units), 18)   # measurement_view fix

    def advance(self, through):
        self.outcome('W1', captured=18)
        for i in range(1, through + 1):
            self.outcome(f'C{i}')

    # -- scenarios ---------------------------------------------------------------
    def test_full_series_w1_c1_to_c8_t1_to_t3(self):
        trace, n = [], 0
        root, record, error, calls = self.arm('W1', self.packet('W1'), n=n)
        self.assert_armed('W1', record, error, calls, root)
        trace.append('W1-a1')
        self.outcome('W1', captured=18)
        while (window := self.next_window()) is not None:
            n += 1
            if window == 'T1':
                self.freeze()
            root, record, error, calls = self.arm(window, self.packet(window), n=n)
            self.assert_armed(window, record, error, calls, root)
            attempt = sum(1 for a in self.history if a.get('window_id') == window) + 1
            trace.append(f'{window}-a{attempt}')
            if window == 'C3' and attempt == 1:
                self.outcome(window, captured=0)                 # zero-capture: same window, same seeds
            elif window == 'C5':
                self.outcome(window, excluded=2)                 # attrition
            else:
                self.outcome(window)
        self.assertEqual(trace, ['W1-a1', 'C1-a1', 'C2-a1', 'C3-a1', 'C3-a2', 'C4-a1', 'C5-a1', 'C6-a1', 'C7-a1',
                                 'C8-a1', 'T1-a1', 'T2-a1', 'T3-a1'])
        rows, _, _, _ = s.calibration_rows(self.manifest, self.history)
        stop = cad.calibration_stop(rows)
        self.assertEqual((stop['decision'], stop['eligible_by_pair'], stop['zero_capture_refusals']),
                         ('calibration_complete', {'spam': 54, 'bank': 56}, 1))
        self.assertTrue(self.w1_checks)
        print('SERIES_E2E ' + json.dumps({'armed': trace, 'eligible_by_pair': stop['eligible_by_pair']}))

    def test_deferred_desk_after_w1_is_refused(self):
        self.outcome('W1', captured=18)
        with self.assertRaisesRegex(ValueError, 'full desk must pass'):
            self.packet('C1', full_desk_gate='deferred')
        forged = self.packet('C1')
        forged['checks']['full_desk_gate'] = self.checks(full_desk_gate='deferred')['full_desk_gate']
        root, record, error, calls = self.arm('C1', forged, n=1)
        self.assertEqual(calls, 0)
        self.assertTrue(any('full desk must pass' in r for r in record['reasons']))

    def test_a_packet_for_another_window_is_refused_before_the_installer(self):
        self.advance(2)
        root, record, error, calls = self.arm('C4', self.packet('C3'), n=1)
        self.assertFalse(record['admitted'])
        self.assertEqual(calls, 0)
        self.assertTrue(any(r.startswith('series_binding: C4') for r in record['reasons']))

    def test_an_unbound_packet_cannot_arm_w1_or_a_series_window(self):
        for window in ('W1', 'C1'):
            if window == 'C1':
                self.outcome('W1', captured=18)
            bare = {k: v for k, v in self.packet(window).items()
                    if k not in ('series_manifest_sha256', 'next_window_id', 'series_history')}
            root, record, error, calls = self.arm(window, bare, n=1)
            self.assertEqual(calls, 0, window)
            self.assertTrue(any(r.startswith(f'series_binding: {window}') for r in record['reasons']))

    def test_escalation_refuses_until_a_lead_release(self):
        # R22-2 / R24: a zero-capture refusal beyond the retry is a structural bar replaced by C9-C14, not an
        # escalation, until all six replacements are owed; the seventh bar escalates.
        self.outcome('W1', captured=18)
        for window in ('C1', 'C2'):
            self.outcome(window, captured=0)
            self.packet(window)                           # the retry is still allowed
            self.outcome(window, captured=0)              # barred, replacement owed
        valid = self.packet('C3')
        for window in ('C3', 'C4', 'C5', 'C6', 'C7'):
            self.outcome(window, captured=0)
            self.packet(window)
            self.outcome(window, captured=0)              # the seventh bar exhausts all six replacements
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            self.packet('C8')
        forged = deepcopy(valid)
        forged.update(series_history=deepcopy(self.history), next_window_id='C8')
        root, record, error, calls = self.arm('C8', forged, n=1)
        self.assertEqual(calls, 0)
        self.assertTrue(any('escalate_to_lead' in r for r in record['reasons']))
        self.history.append({'lead_release': dict(
            ruling_id='RUN_STATE synthetic', text_sha256='c' * 64, resets='zero_capture_escalation',
            after_window='C7#2', lead_signature=SIGNATURE)})
        with self.assertRaisesRegex(ValueError, 'insufficient_calibration'):     # a release cannot repair 8 windows
            self.packet('C8')

    def test_replacement_windows_arm_only_after_a_structural_bar(self):
        self.advance(8)
        self.assertEqual(self.next_window(), 'T1')              # nothing barred: C9/C10 are never armed
        with self.assertRaisesRegex(ValueError, 'does not arm the next frozen window'):
            self.packet('C9')
        self.history.clear()
        self.outcome('W1', captured=18)
        self.outcome('C1', u_pass=False)                         # U1-U3 FAIL: barred, replaced, not counted
        for i in range(2, 9):
            self.outcome(f'C{i}')
        self.assertEqual(self.next_window(), 'C9')
        with self.assertRaisesRegex(ValueError, 'does not arm the next frozen window|calibration_stop'):
            self.packet('T1')                                    # only 7 counted windows
        root, record, error, calls = self.arm('C9', self.packet('C9'), n=1)
        self.assert_armed('C9', record, error, calls, root)
        self.outcome('C9')
        self.assertEqual(self.next_window(), 'T1')
        self.freeze()
        root, record, error, calls = self.arm('T1', self.packet('T1'), n=2)
        self.assert_armed('T1', record, error, calls, root)

    def test_t1_refuses_on_pending_or_insufficient_calibration(self):
        self.advance(7)
        self.outcome('C8', status='provisional')
        with self.assertRaisesRegex(ValueError, 'pending_final_eligibility'):
            self.packet('T1')
        self.history[-1] = dict(self.history[-1])
        self.history.pop()
        self.outcome('C8')
        self.freeze()
        root, record, error, calls = self.arm('T1', self.packet('T1'), n=1)
        self.assert_armed('T1', record, error, calls, root)

    def test_insufficient_calibration_is_terminal(self):
        self.outcome('W1', captured=18)
        for i in range(1, 8):
            self.outcome(f'C{i}', u_pass=False)          # seven U1-U3 FAIL windows: more than six bars, 8 admitted unreachable
        with self.assertRaisesRegex(ValueError, 'insufficient_calibration'):
            self.packet('T1')
        with self.assertRaisesRegex(ValueError, 'insufficient_calibration'):
            self.packet('C8')

    def test_r17_k_plus_2_finality_and_d_alias(self):
        self.outcome('W1', captured=18)
        root, record, error, calls = self.arm('D1', self.packet('C1'), n=1)    # D1 is C1
        self.assert_armed('C1', record, error, calls, root)
        self.outcome('C1', status='provisional')
        self.packet('C2')                       # R17: the previous window may be provisional
        self.outcome('C2')
        with self.assertRaisesRegex(ValueError, 'R17: window k final'):
            self.packet('C3')                   # C1 is still provisional at the arm of C1+2

    def test_desk_routes_the_window_kit(self):
        root = self.tmp / 'session-desk'
        session.prepare(self.measurement, root, window_id='T2')
        with patch.object(pilot, 'desk', return_value={'harvest_status': 'not_run'}) as desk:
            session.desk(root, harvest=False)
        self.assertEqual(desk.call_args.kwargs['kit'], s.kit_path('T2'))
        self.assertIs(desk.call_args.kwargs['extra_checks'], session.powermode_desk_check)


if __name__ == '__main__':
    unittest.main()
