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
import math
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
    if name.startswith('T'):
        spam = bank = 0
    row = dict(window_id=name, attempt_id=name + '-' + suffix, captured_members=captured,
               eligible_benign=dict(spam=spam, bank=bank), status=status)
    path = write(root, row['attempt_id'] + '.json', row)
    return dict(row, evidence=ref(path))


RECORD_COMMIT = 'a' * 40


def sources(root, *, first=False, full='pass'):
    statuses = {r['id']: ('recorded' if r.get('gating', True) is False else
                          'not_applicable' if first and r['first_window_na'] else 'pass')
                for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET}
    statuses['full_desk_gate'] = full
    path = write(root, 'triage-source.json', statuses)
    return {k: dict(status=v, basis='synthetic committed source receipt', evidence=ref(path, '/' + k))
            for k, v in statuses.items()}


def freeze_test(root, history):
    rows, _, _, _ = s.calibration_rows(s.load(root), history)
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
        # RUN_STATE 226 R15: D_k = C_k, distinct seeds in kit order, sabotage at 9/18, 3 tests.
        self.assertEqual((ROOT / s.MANIFEST).read_bytes(), s.raw_json(s.candidate()))
        m = self.manifest
        self.assertEqual(m['order'], ['W1'] + [f'C{i}' for i in range(1, 9)] + ['T1', 'T2', 'T3'])
        per_pair = {pair: [] for pair in s.PAIRS}
        ranges = {'calibration': set(), 'known_h': set(), 'test': set()}
        for number, window in enumerate(m['windows'][1:], 1):
            members = window['members']
            self.assertEqual(len(members), 22)
            self.assertEqual([r['pool'] for r in members[:5] + members[21:]], ['anchor'] * 4 + ['sentinel'] * 2)
            fresh = members[5:21]
            index_in_role = int(window['id'][1:])
            first = s.PAIRS[0] if index_in_role % 2 else s.PAIRS[1]
            self.assertEqual([r['pair'] for r in fresh[::2]], [first] * 8)
            self.assertTrue(all(fresh[i]['pair'] != fresh[i + 1]['pair'] for i in range(15)))
            self.assertEqual([r['ordinal'] for r in fresh if r['condition'] == 'sabotage'], [9, 18])
            sabotage_pool = 'known_h' if window['role'] == 'calibration' else 'test'
            for row in fresh:
                pool = window['role'] if row['condition'] == 'benign' else sabotage_pool
                self.assertEqual(row['pool'], pool)
                per_pair[row['pair']].append(row['seed_index'])
                ranges[pool].add(row['seed_index'])
            for row in members:
                raw = json.dumps(['align-p4-v1', row['model_id'], 'thinking_on',
                                 'shade/' + row['pair'], row['seed_index']], separators=(',', ':')).encode()
                self.assertEqual(row['episode_seed'], int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big'))
        for pair, seeds in per_pair.items():
            self.assertEqual(seeds, sorted(seeds))                      # kit order
            self.assertEqual(len(seeds), len(set(seeds)))               # distinct: no condition reuse
            self.assertEqual((seeds[0], seeds[-1]), (2, 89))
            self.assertFalse(set(seeds) & s.RESERVED_INDICES)
        self.assertEqual((min(ranges['calibration'] | ranges['known_h']), max(ranges['calibration'] | ranges['known_h'])), (2, 65))
        self.assertEqual((min(ranges['test']), max(ranges['test'])), (66, 89))

    def test_alias_mapping_three_tests_and_frozen_bytes(self):
        m = self.manifest
        for k in range(1, 9):
            self.assertEqual(s.selected(m, f'D{k}')['id'], f'C{k}')
        self.assertEqual(len([w for w in m['windows'] if w['role'] == 'calibration']), 8)
        self.assertEqual(len([w for w in m['windows'] if w['role'] == 'test']), 3)
        self.assertEqual((m['d_mapping'], m['test_windows']), ('alias_calibration', 3))
        bad = deepcopy(self.manifest)
        bad['windows'][4]['members'][6]['seed_index'] = 1
        with self.assertRaisesRegex(ValueError, 'frozen'):
            s.validate(bad)

    def test_ceilings_ordinary_and_escalated(self):
        from joulewise.b6.plan_inputs import window_max_s
        self.assertEqual((s.window_ceiling_s(), s.window_ceiling_s(2)), (59520, 62400))
        with self.assertRaises(ValueError):
            s.window_ceiling_s(1)
        span = lambda d: math.ceil(w1.SCAFFOLD_S + 3131.27 + d * 1800)
        ordinary, escalated = (window_max_s({'programmed_span_s': {'seconds': span(d)}}) for d in (18, 20))
        self.assertEqual((ordinary, escalated), (58260, 61860))
        self.assertLessEqual(ordinary, s.window_ceiling_s())
        self.assertGreater(escalated, s.window_ceiling_s())
        self.assertLessEqual(escalated, s.window_ceiling_s(2))

    def test_d_members_are_sized_at_the_largest_w1_d_member_time(self):
        plan = json.loads(self.files[s.kit_path('C1') / 'collection_plan.json'])
        rows = [{'ordinal': i, 'role': 'anchor' if i <= 4 else 'D', 'member_s': 700.0 + i if i <= 4 else 1500.0 + i}
                for i in range(1, 19)]
        with patch.object(w1, 'read_w1_plan_bytes', return_value=json.dumps({'align_v4': {'members': rows}}).encode()):
            seconds, flags, digest = s.member_seconds(ROOT, plan)
        self.assertEqual(flags, [])
        self.assertTrue(w1.valid_digest(digest))
        self.assertEqual([seconds[str(i)] for i in range(1, 5)], [701.0, 702.0, 703.0, 704.0])
        self.assertEqual({seconds[str(i)] for i in range(5, 23)}, {1518.0})

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
            self.assertEqual(sized['window_ceiling_s'], 59520)
            self.assertEqual(sized['flags'], ['sizing.planning_allowances_pending_r1_w1_plan'])
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
        self.fit = []      # RUN_STATE 226 R15: D_k = C_k, no separate fit windows

    def packet(self, name, history, *, desk_digest=None, **kw):
        if name.startswith('T'):
            freeze_test(self.root, history)
        from joulewise.align.apple import v4_registration
        return s.make_packet(self.root, name, history, sources(self.root, first=name == 'W1', **kw),
                             record_commit=RECORD_COMMIT, commit_check=lambda root, commit: True,
                             last_desk_passed_artifact_set_sha256=desk_digest or v4_registration.artifact_set_digest(self.root))

    def test_w1_fit_calibration_test_order_and_exact_fixed_eight(self):
        self.assertTrue(self.packet('W1', [])['previous_window'] == 'R1')
        self.assertEqual(self.packet('D1', [])['previous_window'], 'W1')
        self.assertEqual(self.packet('C1', self.fit)['calibration_windows'], [])
        cal = [attempt(self.root, f'C{i}') for i in range(1, 9)]
        for i in range(1, 9):
            self.packet(f'C{i}', self.fit + cal[:i-1])
        pkt = self.packet('T1', self.fit + cal)
        from joulewise.align.apple import v4_registration
        result = cad.next_arm_triage(pkt, dict.fromkeys(('series_powermode', 'external_volume', 'charging_battery'), True),
                                     {'artifact_set_sha256': v4_registration.artifact_set_digest(self.root),
                                      'record_commit_exists': True})
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

    def test_lead_release_resumes_after_escalation(self):
        cal = [attempt(self.root, f'C{i}') for i in range(1, 3)]
        z1 = attempt(self.root, 'C3', captured=0, spam=0, bank=0)
        z2 = attempt(self.root, 'C3', captured=0, spam=0, bank=0, suffix='a2')
        release = {'lead_release': dict(ruling_id='RUN_STATE 999', text_sha256='c' * 64,
                                        resets='zero_capture_escalation', after_window='C3-a2',
                                        lead_signature='lead: SYNTHETIC-ONLY 2026-11-08')}
        with self.assertRaisesRegex(ValueError, 'escalate_to_lead'):
            self.packet('C3', cal + [z1, z2])
        packet = self.packet('C3', cal + [z1, z2, release])
        self.assertEqual(packet['lead_rulings'], [release['lead_release']])
        # A release that names another attempt, or comes before an escalation, refuses.
        for bad in (dict(release['lead_release'], after_window='C3-a1'),):
            with self.assertRaisesRegex(ValueError, 'lead_release'):
                self.packet('C3', cal + [z1, z2, {'lead_release': bad}])
        with self.assertRaisesRegex(ValueError, 'lead_release'):
            self.packet('C3', cal + [z1, release])
        # The released series continues: C3 captured, then C4.
        self.packet('C4', cal + [z1, z2, release, attempt(self.root, 'C3', suffix='a3')])

    def test_final_counts_may_lower_never_raise_desk_counts(self):
        row = attempt(self.root, 'C1', spam=6, bank=7)
        self.packet('C2', [dict(row, desk_eligible_benign={'spam': 7, 'bank': 7})])
        with self.assertRaisesRegex(ValueError, 'never raise'):
            self.packet('C2', [dict(row, desk_eligible_benign={'spam': 5, 'bank': 7})])

    def test_desk_row_counts_and_u1_u3_pool_bar(self):
        m = s.load(ROOT)
        members = [{'run_id': (s.pack_id('C1') + f"-e{r['ordinal']:02}" if r['pool'] != 'anchor' else
                               f"align-pilot-v3-episodes-a-e{r['ordinal']:02}"),
                    'captured': True, 'excluded': r['ordinal'] in (6, 7, 9)} for r in s.selected(m, 'C1')['members']]
        row = s.desk_row(m, 'C1', members, True)    # 6 spam benign, 7 bank benign, 9 bank known-H
        self.assertEqual((row['captured_members'], row['desk_eligible_benign']), (22, {'spam': 6, 'bank': 6}))
        failed = s.desk_row(m, 'C1', members, False)
        self.assertEqual(failed['desk_eligible_benign'], {'spam': 0, 'bank': 0})
        self.assertIn('u1_u3_failed:pool_entry_barred', failed['flags'])
        none = s.desk_row(m, 'C1', [dict(r, captured=False) for r in members], None)
        self.assertEqual((none['captured_members'], none['desk_eligible_benign']), (0, {'spam': 0, 'bank': 0}))
        self.assertEqual(s.desk_row(m, 'T1', members, True)['desk_eligible_benign'], {'spam': 0, 'bank': 0})

    def test_w1_arm_requires_a_series_bound_packet(self):
        packet = self.packet('W1', [])
        s.bind_packet(self.root, 'W1', packet)
        with self.assertRaisesRegex(ValueError, 'does not bind'):
            s.bind_packet(self.root, 'W1', {k: v for k, v in packet.items() if k != 'series_manifest_sha256'})

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

    def battery_log(self, state):
        from tests.align.test_v4_cadence import write_battery_log
        return write_battery_log(self.root / 'battery.jsonl', state['t0_epoch_s'] - 1)

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
        from joulewise.align.apple import v4_registration
        packet = s.make_packet(m, self.name, history, checks, record_commit=RECORD_COMMIT,
                               last_desk_passed_artifact_set_sha256=v4_registration.artifact_set_digest(m),
                               commit_check=lambda root, commit: True)
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
                obc_off_attested_by='SYNTHETIC operator', battery_log=self.battery_log(state),
                commit_check=lambda root, commit: True)
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
