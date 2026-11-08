"""Synthetic series allocation, production session/writer/HAZARD_PACK replay.

FakeWorld supplies ONLY native prerequisites, model presence, OS/launchd,
identity producer, hazard probes, collector processes and measurement tools.
No weights, measurement data, hardware commands or network are accessed.
"""
from contextlib import ExitStack, redirect_stdout
from copy import deepcopy
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as w1, align_v4_series as s, align_v4_session as session
from scripts import bytes_h_session as h
from joulewise import night_gate
from joulewise.align.apple import v4_cadence as cad
from joulewise.b5 import plan
from joulewise.b6 import registration
from tests.test_b5_driver import Harness, fake_monitor_argv
from tests.align.test_v4_kit import ROOT, FakeArmHost


def write(root, path, value):
    target = Path(root) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(value if isinstance(value, bytes) else s.raw_json(value))
    return target


def ref(path, pointer=''):
    return dict(path=str(path), sha256=s.sha(path.read_bytes()), pointer=pointer)


def attempt(root, name, *, captured=22, spam=7, bank=7, status='final', suffix='a1'):
    if name.startswith(('D', 'T')):
        spam = bank = 0
    row = dict(window_id=name, attempt_id=name + '-' + suffix, captured_members=captured,
               eligible_benign=dict(spam=spam, bank=bank), status=status)
    path = write(root, row['attempt_id'] + '.json', row)
    return dict(row, evidence=ref(path))


def sources(root, *, first=False, full='pass'):
    statuses = {r['id']: ('not_applicable' if first and r['first_window_na'] else 'pass')
                for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET}
    statuses['full_desk_gate'] = full
    path = write(root, 'triage-source.json', statuses)
    return {k: dict(status=v, basis='synthetic committed source receipt', evidence=ref(path, '/' + k))
            for k, v in statuses.items()}


def freeze_test(root, history):
    rows, _, _ = s.calibration_rows(s.load(root), history)
    freeze = write(root, 'synthetic-threshold-freeze.json', dict(status='pass',
        manifest_sha256=s.sha((Path(root) / s.MANIFEST).read_bytes()), calibration_rows_sha256=s.sha(s.raw_json(rows))))
    path = Path(root) / s.ADMISSION
    admission = json.loads(path.read_bytes()) if path.exists() else {}
    admission.setdefault('evidence', {})['test_threshold_freeze'] = ref(freeze)
    write(root, s.ADMISSION, admission)


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = s.load(ROOT)
        cls.files = s.build_files(ROOT, cls.manifest, 'C1')

    def test_candidate_is_reproducible_and_roles_seeds_are_disjoint(self):
        self.assertEqual((ROOT / s.MANIFEST).read_bytes(), s.raw_json(s.candidate()))
        m = self.manifest
        self.assertEqual(m['order'], ['W1', 'D1', 'D2', 'D3'] + [f'C{i}' for i in range(1, 9)] + ['T1', 'T2', 'T3'])
        pools = {role: set() for role in ('fit', 'calibration', 'test')}
        for window in m['windows'][1:]:
            self.assertEqual(len(window['members']), 22)
            rows = [r for r in window['members'] if r['pool'] == window['role']]
            self.assertEqual(sum(r['condition'] == 'benign' for r in rows), 14)
            self.assertEqual(sum(r['condition'] == 'sabotage' for r in rows), 2)
            for row in rows:
                pools[window['role']].add(row['seed_index'])
                raw = json.dumps(['align-p4-v1', row['model_id'], 'thinking_on',
                                 'shade/' + row['pair'], row['seed_index']], separators=(',', ':')).encode()
                self.assertEqual(row['episode_seed'], int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big'))
        self.assertEqual([len(pools[k]) for k in ('fit', 'calibration', 'test')], [21, 56, 21])
        self.assertTrue(pools['fit'].isdisjoint(pools['calibration'] | pools['test']))
        self.assertTrue(pools['calibration'].isdisjoint(pools['test']))
        self.assertFalse(set.union(*pools.values()) & {1, 91, 92, 93})

    def test_both_mapping_and_test_count_options_are_executable_and_explicit(self):
        for mapping in ('separate_fit', 'alias_calibration'):
            for count in (3, 6):
                m = s.validate(s.candidate(d_mapping=mapping, test_windows=count))
                self.assertEqual(s.selected(m, 'D1')['id'], 'C1' if mapping == 'alias_calibration' else 'D1')
                self.assertEqual(len([w for w in m['windows'] if w['role'] == 'calibration']), 8)
                self.assertEqual(len([w for w in m['windows'] if w['role'] == 'test']), count)
        bad = deepcopy(self.manifest)
        bad['windows'][4]['members'][6]['seed_index'] = 1
        with self.assertRaisesRegex(ValueError, 'frozen'):
            s.validate(bad)

    def test_kit_has_real_scaffold_configs_reference_custody_identity_and_sizing(self):
        f = self.files
        directory = s.kit_path('C1')
        collection = json.loads(f[directory / 'collection_plan.json'])
        tree = json.loads(f[directory / 'plan_tree.json'])
        w1.check_window_reference_roles(collection)
        self.assertEqual(len(s.chain.stage_plan(tree)), 12)
        from joulewise.schemas import BenchmarkConfig
        for member in collection['members']:
            raw = f[Path(member['config_path'])]
            self.assertEqual(s.sha(raw), member['config_sha256'])
            typed = BenchmarkConfig.from_mapping(json.loads(raw))
            if member['ordinal'] <= 4:
                old = json.loads((ROOT / w1.KIT / 'collection_plan.json').read_bytes())['members'][member['ordinal'] - 1]
                self.assertEqual(raw, (ROOT / old['config_path']).read_bytes())
            else:
                self.assertEqual(typed.sampling.idle_seconds, 300)
                self.assertTrue(member['spec']['thermal']['heavy'])
                self.assertEqual(member['spec']['hybrid_checkpoint_limit'], 0)
                self.assertEqual(member['spec']['max_turns'], 12)
        with tempfile.TemporaryDirectory() as td:
            for path, raw in f.items():
                write(td, path, raw)
            reg = Path(td) / directory / 'registration'
            sized = registration.load_sizing(reg)['packs']['align-v4-c1']
            self.assertEqual((sized['align_members'], sized['member_count'], sized['programmed_span_s']), (22, 47, 40527))
            self.assertEqual(sized['estimated_footprint_bytes'], 52889269446)
            self.assertLessEqual(sized['window_max_s'], 59520)
            pins = registration.load_identity_pins(reg)
            self.assertEqual(len(pins['units']), 23)

    def test_pending_native_registration_still_blocks_prepare(self):
        # A manifest is not a way around U3/R1/W1 registration.
        with tempfile.TemporaryDirectory() as td, patch.object(session, 'session_start_restore', return_value={'action': 'none'}):
            with self.assertRaises((ValueError, FileNotFoundError)):
                session.prepare(ROOT, Path(td) / 'session', window_id='C1')
            self.assertFalse((Path(td) / 'session').exists())

    def test_desk_selects_window_kit_from_stored_session(self):
        with tempfile.TemporaryDirectory() as td:
            write(td, 'session.json', dict(v4_series=dict(window_id='T2')))
            with patch.object(session.pilot, 'desk', return_value={'status': 'synthetic'}) as desk:
                session.desk(td, harvest=False)
            self.assertEqual(desk.call_args.kwargs['kit'], s.kit_path('T2'))
            self.assertIs(desk.call_args.kwargs['extra_checks'], session.powermode_desk_check)

    def test_admission_needs_exact_manifest_configuration_and_bound_rulings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root, s.MANIFEST, self.manifest)
            write(root, w1.KIT / 'collection_plan.json', {})
            passed = write(root, 'ruling.json', 'pass')
            receipt = dict(schema=s.ADMISSION_SCHEMA, manifest_sha256=s.sha((root / s.MANIFEST).read_bytes()),
                w1_collection_sha256=s.sha((root / w1.KIT / 'collection_plan.json').read_bytes()),
                lead_signature='lead: SYNTHETIC-ONLY 2026-11-08',
                choices={k: self.manifest[k] for k in ('d_mapping', 'test_windows', 'test_shape', 'sentinel')},
                evidence={k: ref(passed) for k in ('scorer_fit_contract', 'seed_allocation', 'r13_r14_gate',
                                                'paired_build_agreement', 'w1_clearance')})
            write(root, s.ADMISSION, receipt)
            s.require_admission(root, self.manifest)
            receipt['choices']['test_windows'] = 6
            write(root, s.ADMISSION, receipt)
            with self.assertRaisesRegex(ValueError, 'explicitly accept'):
                s.require_admission(root, self.manifest)
            receipt['choices']['test_windows'] = 3
            write(root, s.ADMISSION, receipt)
            passed.write_bytes(s.raw_json('fail'))
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                s.require_admission(root, self.manifest)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        write(self.root, s.MANIFEST, s.candidate())
        self.fit = [attempt(self.root, f'D{i}') for i in range(1, 4)]

    def packet(self, name, history, **kw):
        if name.startswith('T'):
            freeze_test(self.root, history)
        return s.make_packet(self.root, name, history, sources(self.root, first=name == 'W1', **kw),
                             code_or_config_changed=False)

    def test_w1_fit_calibration_test_order_and_exact_fixed_eight(self):
        self.assertTrue(self.packet('W1', [])['previous_window'] == 'R1')
        self.assertTrue(self.packet('D1', [])['previous_window_is_w1'])
        self.assertEqual(self.packet('D2', self.fit[:1])['calibration_windows'], [])
        self.assertEqual(self.packet('C1', self.fit)['calibration_windows'], [])
        cal = [attempt(self.root, f'C{i}') for i in range(1, 9)]
        for i in range(1, 9):
            self.packet(f'C{i}', self.fit + cal[:i-1])
        pkt = self.packet('T1', self.fit + cal)
        result = cad.next_arm_triage(pkt, dict.fromkeys(('series_powermode', 'external_volume', 'charging_battery'), True))
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(result['checks']['calibration_stop']['decision'], 'calibration_complete')
        self.packet('T2', self.fit + cal + [attempt(self.root, 'T1')])
        for name, history in [('T1', self.fit + cal[:7]), ('C8', self.fit + cal), ('C2', self.fit)]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.packet(name, history)

    def test_insufficient_provisional_zero_capture_and_fence(self):
        cal = [attempt(self.root, f'C{i}', spam=4, bank=7) for i in range(1, 9)]
        with self.assertRaisesRegex(ValueError, 'insufficient_calibration'):
            self.packet('T1', self.fit + cal)
        cal = [attempt(self.root, f'C{i}', status='provisional' if i == 1 else 'final') for i in range(1, 9)]
        self.packet('C5', self.fit + cal[:4])
        with self.assertRaisesRegex(ValueError, 'C6 onward'):
            self.packet('C6', self.fit + cal[:5])
        with self.assertRaisesRegex(ValueError, 'pending_final_eligibility'):
            self.packet('T1', self.fit + cal)
        zero = attempt(self.root, 'C1', captured=0, spam=0, bank=0)
        self.packet('C1', self.fit + [zero])
        zero2 = attempt(self.root, 'C1', captured=0, spam=0, bank=0, suffix='a2')
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            self.packet('C1', self.fit + [zero, zero2])
        final = attempt(self.root, 'C1', suffix='a2')
        self.packet('C2', self.fit + [zero, final])

    def test_bound_evidence_cannot_change_or_be_forged_in_packet(self):
        packet = self.packet('C1', self.fit)
        bad = deepcopy(packet)
        bad['series_manifest_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            s.bind_packet(self.root, 'C1', bad)
        path = Path(packet['checks']['terminal_completion']['evidence']['path'])
        path.write_text('{}')
        # Immutable transported bytes survive removal of Air-only sources.
        s.bind_packet(self.root, 'C1', packet)
        packet['checks']['terminal_completion']['evidence']['content_utf8'] = '{}'
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            s.bind_packet(self.root, 'C1', packet)
        with self.assertRaisesRegex(ValueError, 'full desk'):
            self.packet('D1', [], full='deferred')


class FakeWorld:
    """Native prerequisites and external processes; series/session/driver stay real."""
    def __init__(self, test, name, files):
        self.harness = harness = Harness(test)
        # This sandbox denies native process census/signals. A short-lived
        # synthetic monitor exits naturally; census is an OS seam, never native
        # teardown evidence. The actual chain and its tools still run/reap.
        harness.monitor_argv = lambda request: fake_monitor_argv(request.custody_root, life=3)
        harness.driver._group_census = lambda *a, **kw: (True, [])
        self.root, self.measurement = harness.root, harness.measurement
        m = self.measurement
        # Only safe, repository-owned config directories are linked. No model locator is followed.
        for path in (ROOT / 'configs').iterdir():
            target = m / 'configs' / path.name
            if path.name != 'campaigns' and not target.exists():
                target.symlink_to(path, target_is_directory=path.is_dir())
        for path in (ROOT / 'configs/campaigns').iterdir():
            target = m / 'configs/campaigns' / path.name
            if path.name != 'align_v4' and not target.exists():
                target.symlink_to(path, target_is_directory=path.is_dir())
        # This existing policy directory needs an additional safe repo fixture.
        target = m / 'configs/campaign_policies/quiet_mac_p2_b5.json'
        target.symlink_to(ROOT / 'configs/campaign_policies/quiet_mac_p2_b5.json')
        base = w1.build_files(ROOT)
        for path, raw in {**base, **files}.items():
            write(m, path, raw)
        write(m, s.MANIFEST, s.candidate())
        # Pending native power/R1 readiness is a labelled fixture seam.
        for directory in (w1.KIT, s.kit_path(name)) if name != 'W1' else (w1.KIT,):
            path = m / directory / 'collection_plan.json'
            collection = json.loads(path.read_bytes())
            collection['runtime_requirements']['ac_powermode'] = 0
            for member in collection['members']:
                member['ac_powermode'] = 0
            write(m, directory / 'collection_plan.json', collection)
            tree = json.loads((m / directory / 'plan_tree.json').read_bytes())
            tree['plan'].update(actual_sha256=s.sha(s.raw_json(collection)), declared_sha256=s.sha(s.raw_json(collection)))
            write(m, directory / 'plan_tree.json', tree)
        if name == 'W1':
            sizing = deepcopy(json.loads(files[s.kit_path('C1') / 'registration/sizing_b5.json']))
            sized = sizing['packs'].pop('align-v4-c1')
            sized.update(pack_id=w1.PACK_ID, member_count=43, align_members=18, programmed_span_s=26927)
            sizing['packs'][w1.PACK_ID] = sized
            write(m, w1.SIZING, sizing)
        passed = write(m, 'synthetic-native-clearance.json', 'pass')
        manifest = s.load(m)
        write(m, s.ADMISSION, dict(schema=s.ADMISSION_SCHEMA, manifest_sha256=s.sha((m / s.MANIFEST).read_bytes()),
            w1_collection_sha256=s.sha((m / w1.KIT / 'collection_plan.json').read_bytes()),
            lead_signature='lead: SYNTHETIC-ONLY 2026-11-08',
            choices={k: manifest[k] for k in ('d_mapping', 'test_windows', 'test_shape', 'sentinel')},
            evidence={k: ref(passed) for k in ('scorer_fit_contract', 'seed_allocation', 'r13_r14_gate',
                                            'paired_build_agreement', 'w1_clearance')}))
        self.name = name
        self.session = self.root / 'selected-session'
        self.model = self.root / 'tiny-model'
        self.model.mkdir()
        (self.model / 'weight').write_bytes(b'synthetic')
        self.installer_calls = []

    def run_process(self, argv, **kwargs):
        if argv[0] == 'launchctl':
            return SimpleNamespace(returncode=113, stdout='', stderr=
                f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}\n')
        if '-c' in argv:
            payload = base64.b64encode(b'{"synthetic":true}\n').decode()
            return SimpleNamespace(returncode=0, stdout=json.dumps({k: payload for k in h.desk_identity.EXPECTED}), stderr='')
        if str(argv[0]).endswith('install_night_agent.sh'):
            self.installer_calls.append(argv)
        return SimpleNamespace(returncode=0, stdout='a' * 40 if 'rev-parse' in argv else '', stderr='')

    def replay(self, test, history):
        harness, m = self.harness, self.measurement
        if self.name.startswith('T'):
            freeze_test(m, history)
        checks = sources(self.root, first=self.name == 'W1')
        packet = s.make_packet(m, self.name, history, checks, code_or_config_changed=False)
        # The source builder is separately checked against its exact output;
        # synthetic model/power readiness intentionally differs from a native kit.
        with ExitStack() as stack, redirect_stdout(io.StringIO()):
            stack.enter_context(patch.object(w1, 'generate', return_value={}))
            stack.enter_context(patch.object(s, 'generate', return_value=s.selected(s.load(m), self.name)))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(plan, 'ledger_head_status', return_value={'blocking': []}))
            # The real writer exposes this mock-runtime timing seam. Keep
            # chain generation/dispatch unchanged, omit only synthetic sleeps.
            writer = plan.write_window_plan
            stack.enter_context(patch.object(plan, 'write_window_plan',
                side_effect=lambda *a, **kw: writer(*a, settle_s=0, **kw)))
            original_pins, original_read = registration.load_identity_pins, h.read
            def physical_pins(path):
                pins = original_pins(path)
                for unit in pins['units'].values():
                    unit['model_source'] = str(self.model)
                return pins
            def physical_inventory(path, *args):
                if Path(path).name == 'model_artifact_inventory.json':
                    pins = original_pins(Path(path).parent)
                    return {'artifacts': {uid: {'inventory': [{'path': 'weight'}]} for uid in pins['units']}}
                return original_read(path, *args)
            stack.enter_context(patch.object(registration, 'load_identity_pins', side_effect=physical_pins))
            stack.enter_context(patch.object(h, 'read', side_effect=physical_inventory))
            state = session.prepare(m, self.session, window_id=self.name, run=self.run_process,
                now=lambda: time.time() - 480, statvfs=lambda _: SimpleNamespace(f_bavail=10**12, f_frsize=1),
                capacity=lambda _: None)
            test.assertEqual(state['preparation_status'], 'STAGED')
            tree = h.read(Path(state['inputs']['pack_root']) / 'plan_tree.json')
            units = tree['arm_attachments']['identity_pin_projection']['identity_units']
            if self.name != 'W1':
                test.assertEqual(sum(u['identity_unit_id'].startswith(w1.D_TAG + '-') for u in units), 18)
            # Real arm_checks (powermode, volume, battery, R12); only OS command
            # answers are fake. No host command executes.
            host = FakeArmHost(0)
            stack.enter_context(patch.object(session, 'w1_disk_check', return_value={'admitted': True}))
            stack.enter_context(patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.root / 'host-state')}))
            installed = session.install(self.session, run=self.run_process, runner=host, volume_runner=host,
                now=lambda: state['t0_epoch_s'] - 1, next_arm_triage=packet,
                obc_off_attested_by='SYNTHETIC operator', topup_completed_at=state['t0_epoch_s'] - 61,
                topup_source='SYNTHETIC completion')
            test.assertEqual(installed['exit_code'], 0)
            test.assertEqual(len(self.installer_calls), 1)
            harness.plan_path = Path(state['plan_path'])
            harness.plan = night_gate.NightPlan.from_mapping(json.loads(harness.plan_path.read_bytes()))
            harness.measurement = Path(state['measurement_root'])
            harness.custody = Path(harness.plan.custody_root)
            harness.night = harness.custody / 'night'
            # Real plan writer, actual rendered zsh, actual run_night HAZARD_PACK.
            code = harness.run()
        test.assertEqual(code, harness.driver.EXIT_GO, harness.result())
        test.assertEqual(harness.result()['chain_exit_code'], 0)
        hazard = harness.hazard()
        test.assertTrue(hazard['monitor']['stop']['proven_stopped'])
        test.assertTrue(hazard['chain']['matches_sidecar'])
        test.assertTrue(harness.result()['courier']['sent'] if 'courier' in harness.result() else harness.sent['sent'])
        test.assertEqual(harness.plan.receipt_class, 'HAZARD_PACK')
        for role, ids in __import__('tests.fixtures.b5_plan.fake_window', fromlist=['expected_bundles']).expected_bundles(harness.plan).items():
            runs = Path(harness.plan.hazard_window['runs_roots'][role])
            test.assertTrue(all((runs / rid / 'summary_metrics.json').is_file() for rid in ids))
        return state


class ProductionPathTests(unittest.TestCase):
    def test_frozen_series_through_production_session_writer_and_hazard_driver(self):
        manifest = s.load(ROOT)
        history = []
        with tempfile.TemporaryDirectory() as receipts:
            for window in manifest['windows']:
                name = window['id']
                with self.subTest(window=name):
                    files = s.build_files(ROOT, manifest, 'C1' if name == 'W1' else name)
                    world = FakeWorld(self, name, files)
                    state = world.replay(self, history)
                    self.assertEqual(state['v4_series']['window_id'], name)
                    if name != 'W1':
                        history.append(attempt(receipts, name))


if __name__ == '__main__':
    unittest.main()
