"""R17 Sol2 review: synthetic controls and deliberately red contract witnesses.

No measurements, model weights, network or external user paths. The import guard
prevents the shared fixture's optional native decorators from probing an archive.
Run this module alone with a realpath TMPDIR and JW_WP22_FULL=1. Red assertions
describe the required behavior, not acceptance of the observed defect.
"""
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
from tests.align.v4_registration_fixtures import session_plan
from copy import deepcopy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock

from tests.align import synthetic_custody  # noqa: I001 (integration hygiene: synthetic custody by default)
from joulewise.adapters import powermetrics as pm
from joulewise.align.apple import harvest_offload as off, light_triage, turn_table
from joulewise.b5 import harvest as harvest
from scripts import align_v4_harvest_off as runner
from tests.align import test_v4_next_arm_packet as records

with mock.patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1'}):
    from tests import test_harvest_b5_window as window_fixture
    from tests.align import test_harvest_off as original

REAL_TMP = os.path.realpath(tempfile.gettempdir())


def setUpModule():
    synthetic_custody.setUpModule()


def tearDownModule():
    window_fixture.tearDownModule()
    synthetic_custody.tearDownModule()


class Scratch(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='hoff-sol2-', dir=REAL_TMP)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class CustodyTests(Scratch):
    def setUp(self):
        super().setUp()
        self.source = self.root / 'session'
        self.source.mkdir()
        (self.source / 'raw.txt').write_bytes(b'finalized raw record\n')
        self.checkout = self.root / 'checkout'
        (self.checkout / 'runs').mkdir(parents=True)
        self.ledger = self.checkout / 'runs/ledger.jsonl'
        self.ledger.write_bytes(b'{"row":1}\n')
        (self.source / 'measurement').symlink_to(self.checkout, target_is_directory=True)
        self.finalized = off.finalized_manifest(self.source)
        self.committed = off.manifest_sha256(self.finalized)
        self.transport = self.root / 'transport'

    def pack(self, **kwargs):
        return off.pack(self.source, self.transport, finalized=self.finalized, **kwargs)

    def unpack(self):
        return off.unpack(self.transport, finalized=self.finalized, finalized_sha256=self.committed)

    def edit_manifest(self, manifest):
        (self.transport / off.MANIFEST).write_text(json.dumps(manifest))

    def test_regular_file_changed_after_finalize_refuses(self):
        (self.source / 'raw.txt').write_bytes(b'changed\n')
        with self.assertRaisesRegex(off.OffloadRefused, 'finalized record manifest'):
            self.pack()
        self.assertFalse(self.transport.exists())

    def test_wrong_record_digest_refuses_before_publication(self):
        self.pack()
        self.source.rename(self.root / 'kept')
        with self.assertRaisesRegex(off.OffloadRefused, 'committed digest'):
            off.unpack(self.transport, finalized=self.finalized, finalized_sha256='0' * 64)
        self.assertFalse(self.source.exists())

    def test_external_ledger_change_after_finalize_must_refuse(self):
        # Real measurement views link runs/ to the checkout. This is synthetic.
        # The finalized digest sees the literal link, but never this ledger.
        self.ledger.write_bytes(b'{"row":9}\n')
        with self.assertRaises(off.OffloadRefused,
                               msg='the record-bound closure must bind external ledger bytes'):
            self.pack(external=(self.ledger,))

    def test_committed_manifest_must_bind_the_original_restore_namespace(self):
        manifest = self.pack()
        redirected = self.root / 'different-namespace'
        manifest['source_root'] = str(redirected)
        self.edit_manifest(manifest)
        with self.assertRaises(off.OffloadRefused,
                               msg='the payload cannot choose a new root outside the record binding'):
            self.unpack()

    def test_external_destination_must_not_be_retargeted_into_checkout_code(self):
        # REWRITTEN (both R17 delta seats ruled the original WRONG; coordinator 2026-11-08): it created
        # collector.py after finalizing a byte-bound checkout directory and required the restore to
        # SUCCEED. Refusal is the right outcome. Honest variant: finalize after the code exists, declare
        # the ledger, retarget the transport row into checkout code: refused, code unchanged; then the
        # honest manifest restores.
        code = self.checkout / 'collector.py'
        code.write_bytes(b'')
        finalized = off.finalized_manifest(self.source, inputs=(self.ledger,))
        committed = off.manifest_sha256(finalized)
        # Air-offload S1-04: the pack carries every byte-bound closure input (here also the checkout files).
        manifest = off.pack(self.source, self.transport, finalized=finalized,
                            external=tuple(off.byte_bound_inputs(finalized)))
        honest = (self.transport / off.MANIFEST).read_bytes()
        next(row for row in manifest['external'].values() if row['path'] == str(self.ledger))['path'] = str(code)
        self.edit_manifest(manifest)
        self.source.rename(self.root / 'kept')
        with self.assertRaises(off.OffloadRefused):
            off.unpack(self.transport, finalized=finalized, finalized_sha256=committed)
        self.assertEqual(code.read_bytes(), b'',
                         'unpack accepted a self-declared external destination and changed checkout code')
        self.assertFalse(self.source.exists())
        (self.transport / off.MANIFEST).write_bytes(honest)
        off.unpack(self.transport, finalized=finalized, finalized_sha256=committed)
        self.assertEqual(code.read_bytes(), b'')

    def test_refused_payload_must_not_write_through_measurement_view(self):
        manifest = self.pack()
        payload = self.transport / off.PAYLOAD
        raw_tar = subprocess.run([off.zstd_path(), '-q', '-d', '-c', str(payload)],
                                 check=True, capture_output=True).stdout
        # Keep all finalized entries exactly, then append one unmanifested file
        # below the restored absolute symlink. The final tree check must refuse
        # without first publishing that file into the checkout.
        stream = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(raw_tar)) as old, tarfile.open(fileobj=stream, mode='w') as new:
            for entry in old:
                new.addfile(entry, old.extractfile(entry) if entry.isfile() else None)
            data = b'unmanifested code\n'
            entry = tarfile.TarInfo('measurement/injected.py')
            entry.size = len(data)
            new.addfile(entry, io.BytesIO(data))
        payload.write_bytes(subprocess.run([off.zstd_path(), '-q', '-c'], input=stream.getvalue(),
                                            check=True, capture_output=True).stdout)
        manifest['payload'].update(sha256=hashlib.sha256(payload.read_bytes()).hexdigest(),
                                   size=payload.stat().st_size)
        self.edit_manifest(manifest)
        self.source.rename(self.root / 'kept')
        with self.assertRaisesRegex(off.OffloadRefused, 'differs from manifest'):
            self.unpack()
        self.assertFalse(self.source.exists())
        self.assertFalse((self.checkout / 'injected.py').exists(),
                         'unpack wrote outside staging before rejecting the unmanifested member')

    def test_operator_pack_cli_must_require_the_record_bound_manifest(self):
        custody = self.source / 'custody/night'
        custody.mkdir(parents=True)
        (custody / 'result.json').write_text('{}')
        plan = self.source / 'plan.json'
        plan.write_text(json.dumps({'custody_root': str(custody.parent)}))
        (self.source / 'session.json').write_text(json.dumps({
            'plan_path': str(plan), 'measurement_root': str(self.checkout)}))
        with mock.patch.object(runner, 'checkout_identity', return_value={}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = runner.main(['pack', '--session-root', str(self.source), '--out', str(self.transport)])
        self.assertNotEqual(code, 0, 'omitting --finalized-manifest silently disables record binding')


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class ArchiveEqualityTests(Scratch):
    def test_all_177_archive_files_match_without_projection_or_memo_on_reference(self):
        w = window_fixture.Window(self.root / 'canonical', catalog_overrides={
            'member.cooldown_evidence_unverified': 'DISCLOSE'})
        finalized = off.finalized_manifest(w.root)
        off.pack(w.root, self.root / 'transport', finalized=finalized)
        checkout = harvest.harvest_checkout(block_six=False)

        def seams(workers, io_workers):
            return harvest.Seams(group_alive=lambda _: False, exclusions_compute=window_fixture.EXCLUSIONS,
                now=lambda: 1786300000.0, monotonic_ns=lambda: 123, boot_session_uuid=lambda: 'SYNTHETIC',
                workers=workers, io_workers=io_workers, harvest_checkout=lambda **_: checkout)

        with mock.patch.object(harvest, 'document_memo', contextlib.nullcontext):
            reference = harvest.harvest(harvest.resolve_inputs(w.plan_path), w.archive,
                                        seams=seams(1, 1), prepare_desk=True)
        expected = {p.relative_to(w.archive).as_posix(): p.read_bytes()
                    for p in w.archive.rglob('*') if p.is_file()}
        self.assertEqual(reference['verdict'], 'COLLECTED')
        self.assertEqual(len(expected), 177)
        w.root.rename(self.root / 'original-kept')
        off.unpack(self.root / 'transport', w.root, finalized=finalized,
                   finalized_sha256=off.manifest_sha256(finalized))
        replay = harvest.harvest(harvest.resolve_inputs(w.plan_path), w.archive,
                                 seams=seams(3, 2), prepare_desk=True)
        observed = {p.relative_to(w.archive).as_posix(): p.read_bytes()
                    for p in w.archive.rglob('*') if p.is_file()}
        self.assertEqual(replay, reference)
        self.assertEqual(observed, expected)


class EligibilityTests(Scratch):
    def first(self):
        return records.Scenario(self.root, 'W1').finish()

    def test_only_the_previous_calibration_may_be_provisional(self):
        first = self.first()
        c1 = records.Scenario(self.root, 'C1', previous=first, provisional=True).finish()
        self.assertTrue(records.evaluate(c1, c1.build())['admitted'])
        c2 = records.Scenario(self.root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertFalse(records.evaluate(c2, packet)['admitted'])

    def test_code_change_cannot_arm_on_provisional_eligibility(self):
        c1 = records.Scenario(self.root, 'C1', previous=self.first(), provisional=True).finish()
        packet = c1.build(current='f' * 64)
        self.assertEqual(packet['checks']['member_eligibility']['status'], 'fail')
        self.assertFalse(packet['packet_preflight']['ready'])

    def test_finally_excluded_member_cannot_remain_in_pool(self):
        c1 = records.Scenario(self.root, 'C1', previous=self.first(), provisional=True)
        rid = c1.members[0]['run_id']
        c1.sources['exclusions']['members_excluded'] = [{'run_id': rid, 'codes': ['clock.step']}]
        c1.thermal['members'][0]['excluded'] = True
        c1.finish()
        c2 = records.Scenario(self.root, 'C2', previous=c1, previous_final=True)
        c2.series['pool_members'] = [rid]
        c2.finish()
        packet = c2.build()
        self.assertIn('finally excluded member', packet['calibration_error'])
        self.assertFalse(records.evaluate(c2, packet)['admitted'])

    def test_older_test_window_cannot_be_silently_labelled_final(self):
        from scripts import align_v4_series as series, align_v4_session as session, align_v4_kit as kit
        from tests.align.test_v4_cadence import write_battery_log
        # Complete chronological W1/C1..C8/T1/T2 history, with 40 final benign
        # members per pair and a threshold freeze; no calibration shortfall or
        # skipped frozen slot can explain the expected rejection at T3.
        previous = records.Scenario(self.root, 'W1')
        previous.write(series.MANIFEST.as_posix(), series.raw_json(series.candidate()))
        previous.finish()
        for number in range(1, 9):
            current = records.Scenario(self.root, f'C{number}', previous=previous)
            for index in range(1, 5):
                for planned, thermal in zip(list(current.members[:2]), list(current.thermal['members'][:2])):
                    new_id = planned['run_id'] + f'-{index}'
                    current.members.append({**planned, 'run_id': new_id})
                    current.thermal['members'].append({**deepcopy(thermal), 'id': new_id})
            previous = current.finish()
        t1 = records.Scenario(self.root, 'T1', previous=previous, provisional=True)
        t1.record['role'] = 'test'
        t1.finish()
        t2 = records.Scenario(self.root, 'T2', previous=t1)
        t2.record['role'] = 'test'
        t2.next_plan.update(window='T3', role='test')
        t2.finish()
        packet = t2.build()
        self.assertEqual(packet['calibration_decision']['decision'], 'calibration_complete')
        freeze = series.raw_json({'status': 'pass', 'manifest_sha256': packet['series_manifest_sha256'],
                                   'calibration_rows_sha256': series.sha(series.raw_json(packet['calibration_windows']))})
        t2.write(series.ADMISSION.as_posix(), {'evidence': {'test_threshold_freeze': {
            'path': 'SYNTHETIC-EMBEDDED', 'sha256': series.sha(freeze), 'pointer': '',
            'content_utf8': freeze.decode()}}})
        target = self.root / 'arm-T3'
        target.mkdir()
        log = write_battery_log(self.root / 'battery.jsonl', records.NOW)
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.root / 'host')}), \
             mock.patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True, 'observed': 0}), \
             mock.patch('joulewise.align.apple.external_volume.census', return_value={}), \
             mock.patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             mock.patch('joulewise.battery_float.observe', return_value=(good, b'synthetic')), \
             mock.patch.object(kit, 'arm_powermode_check'), \
             mock.patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
             mock.patch.object(session.pilot, 'install', return_value={}) as install:
            try:
                session._arm_and_install(target, session_plan(target, {'v4_series': {'window_id': 'T3'},
                    'source_measurement_root': str(self.root)}, now=records.NOW), self.root, t2.next_plan, None,
                    watchdog_check=_watchdog_acceptance, runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''), volume_runner=None,
                    now=lambda: records.NOW, w1_disk_config=None, disk_gate=None, battery_log=log,
                    next_arm_triage=packet, obc_off_attested_by='synthetic', meter_probe=lambda _: {'live': True})
            except ValueError:
                pass
            self.assertEqual(install.call_count, 0,
                             'real arm route reached installer at T3 while T1 remained provisional')


class MemoTests(unittest.TestCase):
    def data(self, value):
        return plistlib.dumps({'value': value, 'nested': {'items': [1, 2]}})

    def test_changed_bytes_are_a_miss_and_callers_are_isolated(self):
        with mock.patch.object(pm, '_powermetrics_documents', wraps=pm._powermetrics_documents) as parse:
            with harvest.document_memo():
                first = pm._powermetrics_documents(self.data(1))
                first[0][0]['nested']['items'].append(3)
                self.assertEqual(pm._powermetrics_documents(self.data(1))[0][0]['nested']['items'], [1, 2])
                self.assertEqual(pm._powermetrics_documents(self.data(2))[0][0]['value'], 2)
            with harvest.document_memo():
                pm._powermetrics_documents(self.data(1))
        self.assertEqual(parse.call_count, 3)
        self.assertIsNone(harvest._DOCUMENT_MEMO.get())

    def test_failed_parse_is_retried_and_exception_drops_member_scope(self):
        with mock.patch.object(pm, '_powermetrics_documents', wraps=pm._powermetrics_documents) as parse:
            with self.assertRaises(RuntimeError):
                with harvest.document_memo():
                    for _ in range(2):
                        with self.assertRaises(ValueError):
                            pm._powermetrics_documents(b'not a plist')
                    self.assertEqual(harvest._DOCUMENT_MEMO.get(), {})
                    raise RuntimeError('synthetic worker fault')
        self.assertEqual(parse.call_count, 2)
        self.assertIsNone(harvest._DOCUMENT_MEMO.get())

    def test_each_assessed_member_gets_a_fresh_memo(self):
        with tempfile.TemporaryDirectory(dir=REAL_TMP) as d:
            def assess(task, readable):
                self.assertEqual(harvest._DOCUMENT_MEMO.get(), {})
                pm._powermetrics_documents(self.data(1))
                return {'run_id': task['run_id']}
            with mock.patch.object(harvest, '_assess_plain_member', side_effect=assess):
                for rid in ('first', 'second'):
                    harvest.assess_member({'bundle_path': d, 'run_id': rid})
                    self.assertIsNone(harvest._DOCUMENT_MEMO.get())


class SizingTests(unittest.TestCase):
    def test_one_gib_member_limits_to_three_workers_with_28_gib_free(self):
        with mock.patch.object(runner, 'largest_plist_bytes', return_value=1 << 30):
            result = runner.auto_workers(session_root='synthetic', memory=28 << 30, cores=10)
        self.assertEqual(result['peak_bytes_per_worker'], 8 << 30)
        self.assertEqual(result['workers'], 3)

    def test_insufficient_memory_must_not_launch_a_worker_that_cannot_fit(self):
        with self.assertRaises(ValueError, msg='8 GiB worker cannot fit after the 4 GiB reserve'):
            runner.auto_workers(peak_bytes=8 << 30, memory=6 << 30, cores=10)

    def test_sweep_failure_cannot_supply_a_tiny_peak(self):
        with tempfile.TemporaryDirectory(dir=REAL_TMP) as d:
            path = Path(d) / 'sweep.json'
            path.write_text(json.dumps({'runs': [{'exit': 1, 'peak_child_rss_bytes': 1}]}))
            with self.assertRaises(ValueError, msg='failed sweep is not a measured successful worker peak'):
                runner._sweep_peak(path)

    def test_small_fixture_sweep_cannot_override_one_gib_member_budget(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory(dir=REAL_TMP) as d:
            path = Path(d) / 'sweep.json'
            path.write_text(json.dumps({'schema': 'joulewise.align_v4.harvest_sweep.v1',
                'session_id': 'other-small-fixture', 'runs': [{'exit': 0, 'peak_child_rss_bytes': 200 << 20}]}))
            with mock.patch.object(runner, 'largest_plist_bytes', return_value=1 << 30), \
                 mock.patch.object(runner, 'free_memory_bytes', return_value=28 << 30), \
                 mock.patch.object(runner, 'free_cores', return_value=10):
                result = runner.cmd_desk(SimpleNamespace(workers='auto', sweep=path, session_root=d),
                    run=lambda argv, **_: subprocess.CompletedProcess(argv, 0))
            self.assertLessEqual(result['workers'], 3,
                                 'unbound 200 MiB fixture peak launches ten ~8 GiB workers')


class ThermalAndTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tiny fake-MLX endpoint bundles only. No MLX import, weights or hardware.
        cls.fixture = original.SyntheticV4SessionE2ETests
        cls.fixture.setUpClass()
        from tests.align.test_thermal_gate import NativeIntegrationTests
        helper = NativeIntegrationTests('test_real_workload_endpoint_budget_and_held_stream_keep_exact_tokens')
        held, status, _ = helper.held_run(cls.fixture.root / 'held-source')
        assert status.status.value == 'succeeded'
        rid = cls.fixture.rows[0]['run_id']
        bundle = cls.fixture.runs / rid
        shutil.rmtree(bundle)
        shutil.copytree(held, bundle)
        path = bundle / 'outputs/align_episode.json'
        episode = json.loads(path.read_bytes())
        episode['episode_id'] = rid
        episode.setdefault('hardware', {})['ac_powermode'] = {'value': 0}
        path.write_text(json.dumps(episode))

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def test_adversarial_thermal_journals_preserve_light_full_u1_u3(self):
        from scripts import align_v4_session as v4, align_v4_kit as kit
        fixture = self.fixture
        path = fixture.runs / fixture.rows[0]['run_id'] / 'outputs/align_thermal.jsonl'
        original_bytes = path.read_bytes()
        journal = [json.loads(line) for line in original_bytes.splitlines() if line.strip()]
        poisoned = deepcopy(journal)
        for row in poisoned:
            status = row.get('status') or row.get('values', {}).get('status')
            if isinstance(status, dict):
                status['os_level'] = 1
        self.assertTrue(poisoned != journal, 'OS-pressure mutation must change the journal')
        mutations = [original_bytes, b'', b'{malformed\n',
                     b'\n'.join(json.dumps(r).encode() for r in journal[::-1]),
                     b'\n'.join(json.dumps(r).encode() for r in poisoned),
                     b'\n'.join(json.dumps(r).encode() for r in journal[::10]),
                     b'\n'.join(json.dumps(r).encode() for r in journal + journal[-1:])]
        state = json.loads((fixture.session / 'session.json').read_bytes())
        try:
            for index, data in enumerate(mutations):
                with self.subTest(mutation=index), contextlib.redirect_stdout(io.StringIO()):
                    path.write_bytes(data)
                    _, light = v4.powermode_desk_check(state=state, members=[], runs_root=fixture.runs, kit_path=kit.KIT)
                    if index == 4:
                        self.assertTrue(any(t.get('os_nominal') is False for r in light['thermal']['members']
                                            for t in r['turn_observation']))
                    full_members = [{'run_id': row['run_id'], 'exclusion_codes': ['battery.member_span', 'clock.step']}
                                    for row in fixture.rows]
                    _, full = v4.powermode_desk_check(state=state, members=full_members,
                                                     runs_root=fixture.runs, kit_path=kit.KIT)
                    self.assertEqual(light_triage.thermal_escalation(light['thermal']),
                                     light_triage.thermal_escalation(full['thermal']))
                    for key in light['thermal']['model_windows']:
                        for n in (1, 2, 3):
                            self.assertEqual(light['thermal']['model_windows'][key][f'U{n}'],
                                             full['thermal']['model_windows'][key][f'U{n}'])
        finally:
            path.write_bytes(original_bytes)

    def test_turn_table_binding_covers_metadata_used_by_attribution(self):
        rid = self.fixture.rows[0]['run_id']
        bundle = self.fixture.runs / rid
        path = bundle / 'metadata.json'
        raw = path.read_bytes()
        before = turn_table.member_table(bundle, rid)
        try:
            metadata = json.loads(raw)
            episode = json.loads((bundle / 'outputs/align_episode.json').read_bytes())
            stamp = episode['hardware']['paired_clock_stamps_ns'][0]
            offset = (stamp['epoch_ns'] - stamp['monotonic_before_ns']) / 1e9
            metadata['uncertainty_evidence'] = {'clock_anchor': {
                'status': 'bounded', 'wall_minus_monotonic_lower_s': offset,
                'wall_minus_monotonic_upper_s': offset, 'effective_clock_anchor_bound_s': 1.,
                'method': 'synthetic review perturbation'}}
            path.write_text(json.dumps(metadata))
            after = turn_table.member_table(bundle, rid)
        finally:
            path.write_bytes(raw)
        self.assertNotEqual(before['channels'], after['channels'], 'mutation must affect the energy table')
        self.assertNotEqual(before['inputs'], after['inputs'],
                            'metadata.json is read by attribution but omitted from the input digest set')

    def test_held_member_turn_table_matches_the_full_desk_fields(self):
        from scripts import align_pilot_session as pilot, align_v4_session as v4, align_v4_kit as kit
        fixture = self.fixture
        state = json.loads((fixture.session / 'session.json').read_bytes())
        with contextlib.redirect_stdout(io.StringIO()):
            _, report = v4.powermode_desk_check(state=state, members=[], runs_root=fixture.runs, kit_path=kit.KIT)
        rid = fixture.rows[0]['run_id']
        summary = pilot.episode_summary(fixture.runs / rid)
        pilot_json = {'members': [{'run_id': rid, 'summary': summary}], 'extra_checks': report}
        table = turn_table.member_table(fixture.runs / rid, rid)
        self.assertTrue(turn_table.equal_to_pilot(table, pilot_json))
        self.assertTrue(table['thermal']['per_turn'])
        pilot_json['members'][0]['summary']['energy']['mock:mock']['per_turn_j'][0] += 1
        self.assertFalse(turn_table.equal_to_pilot(table, pilot_json))


if __name__ == '__main__':
    unittest.main()
