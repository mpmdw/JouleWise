"""Independent R17 review: synthetic witnesses; failures identify open findings.

No models, hardware, network, or real custody are used. The stock B5 fixture
has historical absolute locators: fence them BEFORE importing/running it.
Run with TMPDIR=/private/tmp JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=1.
"""
from contextlib import contextmanager, nullcontext, redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.align import synthetic_custody  # noqa: I001 (integration hygiene: synthetic custody by default)
from joulewise.adapters import powermetrics as pm
from joulewise.b5 import harvest as h
from joulewise.align.apple import harvest_offload as off, light_triage as lt, thermal_desk as td
from scripts import align_v4_harvest_off as runner
from tests.align.test_v4_next_arm_packet import Scenario, evaluate

REPO = Path(__file__).absolute().parents[2]
setUpModule, tearDownModule = synthetic_custody.setUpModule, synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


@contextmanager
def synthetic_custody_only():
    """Never probe a historical /Users/edr locator, including metadata probes."""
    from joulewise import calibration_ledger as ledger
    original = ledger._custody_probe_paths

    def paths(path, **kwargs):
        absolute = Path(os.path.abspath(path))
        if absolute.is_relative_to('/Users/edr') and not absolute.is_relative_to(REPO):
            return ()
        return original(path, **kwargs)

    with patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1', 'JOULEWISE_BACKUP_ROOTS': '',
                                'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}), \
            patch.object(ledger, '_custody_probe_paths', side_effect=paths):
        yield


class ReviewBase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='r17-sol1-', dir=REAL_TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def series(self, specs):
        previous = Scenario(self.root, 'W1').finish()
        for name, options in specs:
            previous = Scenario(self.root, name, previous=previous, **options).finish()
        return previous


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class CustodyWitnesses(ReviewBase):
    def test_regular_bytes_are_bound_and_restore_requires_the_same_path(self):
        source = self.root / 'session'
        source.mkdir()
        raw = source / 'raw'
        raw.write_bytes(b'MBP raw record')
        final = off.finalized_manifest(source)
        raw.write_bytes(b'late raw record')
        with self.assertRaises(off.OffloadRefused):
            off.pack(source, self.root / 'late', finalized=final)
        raw.write_bytes(b'MBP raw record')
        off.pack(source, self.root / 'bound', finalized=final)
        source.rename(self.root / 'kept')
        with self.assertRaisesRegex(off.OffloadRefused, 'differs from the recorded'):
            off.unpack(self.root / 'bound', self.root / 'relocated', finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
        off.unpack(self.root / 'bound', source, finalized=final,
                   finalized_sha256=off.manifest_sha256(final))
        self.assertEqual(raw.read_bytes(), b'MBP raw record')

    def test_changed_external_symlink_bytes_must_not_pass_record_bound_restore(self):
        # F1: literal symlink equality does not authenticate the bytes consumers open.
        source = self.root / 'session'
        source.mkdir()
        external = self.root / 'measurement-inputs'
        external.mkdir()
        target = external / 'journal.jsonl'
        target.write_bytes(b'MBP bytes\n')
        (source / 'measurement').symlink_to(external, target_is_directory=True)
        final = off.finalized_manifest(source)
        off.pack(source, self.root / 'bound', finalized=final)
        source.rename(self.root / 'kept')
        target.write_bytes(b'Air bytes\n')
        try:
            off.unpack(self.root / 'bound', source, finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
        except off.OffloadRefused:
            return
        self.assertEqual(off.verify_tree(source, json.loads((self.root / 'bound/MANIFEST.json').read_text())), [])
        self.assertEqual((source / 'measurement/journal.jsonl').read_bytes(), b'MBP bytes\n',
                         'record-bound verification passed changed external target content')

    def test_cli_must_require_record_bound_manifest_arguments(self):
        # F2: the documented native boundary currently accepts an unbound transfer.
        source = self.root / 'session'
        (source / 'custody/night').mkdir(parents=True)
        (source / 'custody/night/result.json').write_text('{}')
        (source / 'plan.json').write_text(json.dumps({'custody_root': str(source / 'custody')}))
        (source / 'session.json').write_text(json.dumps({'plan_path': str(source / 'plan.json'),
                                                       'measurement_root': str(self.root / 'checkout')}))
        identity = {'measurement_root': str(self.root / 'checkout'), 'head': 'a' * 40,
                    'tracked_clean': True, 'python': ['synthetic-python', 'synthetic-packages']}
        with patch.object(runner, 'checkout_identity', return_value=identity), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            packed = runner.main(['pack', '--session-root', str(source), '--out', str(self.root / 'offload')])
            if packed != 0:
                return
            source.rename(self.root / 'kept')
            restored = runner.main(['unpack', '--offload', str(self.root / 'offload')])
        self.assertNotEqual(restored, 0, 'CLI pack and unpack both succeeded with no record binding')

    def test_record_bound_serial_mbp_and_pooled_air_equal_all_177_files(self):
        with synthetic_custody_only(), redirect_stderr(io.StringIO()):
            from joulewise.b5 import harvest as h
            from tests import test_harvest_b5_window as fixture
            self.addCleanup(fixture.tearDownModule)
            window = fixture.Window(self.root / 'window', catalog_overrides={
                'member.cooldown_evidence_unverified': 'DISCLOSE'})
            final = off.finalized_manifest(window.root)
            off.pack(window.root, self.root / 'bound', finalized=final)
            checkout = h.harvest_checkout(block_six=False)

            def seams(workers):
                return h.Seams(group_alive=lambda _: False, exclusions_compute=fixture.EXCLUSIONS,
                    now=lambda: 1786300000.0, monotonic_ns=lambda: 123,
                    boot_session_uuid=lambda: 'SYNTHETIC', workers=workers, io_workers=2,
                    harvest_checkout=lambda **_: checkout)

            with patch.object(h, 'document_memo', nullcontext):
                mbp = h.harvest(h.resolve_inputs(window.plan_path), window.archive,
                                seams=seams(1), prepare_desk=True)
            before = {p.relative_to(window.archive).as_posix(): p.read_bytes()
                      for p in window.archive.rglob('*') if p.is_file()}
            window.root.rename(self.root / 'kept')
            off.unpack(self.root / 'bound', window.root, finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
            air = h.harvest(h.resolve_inputs(window.plan_path), window.archive,
                            seams=seams(3), prepare_desk=True)
            after = {p.relative_to(window.archive).as_posix(): p.read_bytes()
                     for p in window.archive.rglob('*') if p.is_file()}
            self.assertEqual(mbp['verdict'], h.COLLECTED)
            self.assertEqual(len(before), 177)
            self.assertEqual(air, mbp)
            self.assertEqual(after, before)


class EligibilityWitnesses(ReviewBase):
    def test_stale_calibration_provisional_and_changed_code_refuse(self):
        latest = self.series([('C1', {'provisional': True}), ('C2', {})])
        packet = latest.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertFalse(evaluate(latest, packet)['admitted'])

    def test_full_desk_due_refuses_previous_provisional(self):
        latest = self.series([('C1', {'provisional': True})])
        packet = latest.build(current='f' * 64)
        self.assertEqual(packet['checks']['member_eligibility']['status'], 'fail')
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'fail')

    def test_finally_excluded_old_member_cannot_remain_in_pool(self):
        w1 = Scenario(self.root, 'W1').finish()
        c1 = Scenario(self.root, 'C1', previous=w1, provisional=True)
        rid = c1.members[0]['run_id']
        c1.thermal['members'][0]['excluded'] = True
        c1.sources['exclusions']['members_excluded'] = [{'run_id': rid, 'codes': ['clock.step']}]
        c1.finish()
        c2 = Scenario(self.root, 'C2', previous=c1, previous_final=True)
        c2.series['pool_members'] = [rid]
        c2.finish()
        packet = c2.build()
        self.assertIn('finally excluded member of C1 is in the pool', packet['calibration_error'])
        self.assertFalse(evaluate(c2, packet)['admitted'])

    def calibration_complete(self):
        from scripts import align_v4_series as series
        manifest = self.root / series.MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes(series.raw_json(series.candidate()))
        previous = Scenario(self.root, 'W1').finish()
        for k in range(1, 9):
            s = Scenario(self.root, f'C{k}', previous=previous)
            members, thermal = [], []
            for planned, record in zip(s.members, s.thermal['members']):
                for index in range(7):
                    p, r = deepcopy(planned), deepcopy(record)
                    p['run_id'] += f'-{index}'
                    r['id'] = p['run_id']
                    members.append(p)
                    thermal.append(r)
            s.members[:] = members
            s.thermal['members'] = thermal
            s.sources['pilot']['extra_checks']['km003c']['members'] = {
                m['run_id']: {'status': 'available', 'flags': []} for m in members}
            s.next_plan.update(window=f'C{k+1}' if k < 8 else 'T1',
                               role='calibration' if k < 8 else 'test')
            previous = s.finish()
        return previous

    def test_test_window_k_must_be_final_before_arm_of_k_plus_2(self):
        # F3: only calibration records call eligibility() in the history loop.
        from scripts import align_v4_series as series
        c8 = self.calibration_complete()
        final_calibration = c8.build()
        freeze = c8.write('synthetic-threshold-freeze.json', {'status': 'pass',
            'manifest_sha256': final_calibration['series_manifest_sha256'],
            'calibration_rows_sha256': series.sha(series.raw_json(final_calibration['calibration_windows']))})
        freeze.update(path=str(self.root / freeze['path']), pointer='')
        c8.write(series.ADMISSION, {'evidence': {'test_threshold_freeze': freeze}})
        t1 = Scenario(self.root, 'T1', previous=c8, provisional=True)
        t1.record['role'] = 'test'
        t1.next_plan.update(window='T2', role='test')
        t1.finish()
        self.assertTrue(evaluate(t1, t1.build())['admitted'])  # allowed one-window delay
        t2 = Scenario(self.root, 'T2', previous=t1, provisional=True)
        t2.record['role'] = 'test'
        t2.next_plan.update(window='T3', role='test')
        t2.finish()  # no previous_final for T1: two unfinished desks
        packet = t2.build()
        self.assertNotIn('pilot', t1.record['sources'])
        self.assertNotIn('exclusions', t1.record['sources'])
        self.assertEqual(next(r for r in packet['series_history'] if r.get('window_id') == 'T1')['status'], 'final')
        self.assertIs(series.bind_packet(self.root, 'T3', packet, authenticated_by_rebuild=True), packet)
        self.assertFalse(evaluate(t2, packet)['admitted'],
                         'the arm rebuild admitted T3 while T1 and T2 are both provisional')

    def test_final_sources_must_prove_a_completed_harvest(self):
        # F4: stale PILOT/exclusions plus a running desk must not be called final.
        # REWRITTEN (both R17 delta seats ruled the original WRONG; coordinator 2026-11-08): the
        # original C1 had no light triage, so it had neither final nor provisional evidence and C2
        # correctly refused; it also demanded the series binder accept an unsafe C3. Honest variant:
        # C1 carries its light triage, releases C2, and C3 is refused by the arm rebuild AND the binder.
        from scripts import align_v4_next_arm_packet as builder
        from scripts import align_v4_series as series
        manifest = self.root / series.MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes(series.raw_json(series.candidate()))
        w1 = Scenario(self.root, 'W1').finish()
        c1 = Scenario(self.root, 'C1', previous=w1)
        light = deepcopy(c1.thermal)
        for m in light['members']:
            m['excluded'] = bool(m['calibration_exclusions'])
        c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C1', 'thermal': light,
            'checks': {'v4_B_bar': True}, 'km003c': c1.sources['pilot']['extra_checks']['km003c'],
            'series_desk_row': c1.sources['pilot']['extra_checks']['series_desk_row']}
        c1.sources['desk'] = {'plan_id': c1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
        c1.next_plan['window'] = 'C2'
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.passed_ref = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        first = c1.build()
        self.assertIs(series.bind_packet(self.root, 'C2', first, authenticated_by_rebuild=True), first)
        self.assertTrue(evaluate(c1, first)['admitted'])
        c2 = Scenario(self.root, 'C2', previous=c1)
        c2.next_plan['window'] = 'C3'
        c2.finish()
        packet = c2.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        with self.assertRaises(ValueError):
            series.bind_packet(self.root, 'C3', packet, authenticated_by_rebuild=True)
        self.assertFalse(evaluate(c2, packet)['admitted'],
                         'older eligibility is final although its desk never recorded a completed harvest')


class MemoAndSizingWitnesses(ReviewBase):
    def test_memo_content_changes_nested_members_and_refusals_are_isolated(self):
        a, b = plistlib.dumps({'x': [1]}), plistlib.dumps({'x': [2]})
        with patch.object(pm, '_powermetrics_documents', wraps=pm._powermetrics_documents) as parse:
            with h.document_memo():
                first, _ = pm._powermetrics_documents(a)
                first[0]['x'][0] = 99
                self.assertEqual(pm._powermetrics_documents(a)[0][0]['x'], [1])
                self.assertEqual(pm._powermetrics_documents(b)[0][0]['x'], [2])
                with h.document_memo():
                    self.assertEqual(pm._powermetrics_documents(a)[0][0]['x'], [1])
                self.assertEqual(parse.call_count, 3)
                for _ in range(2):
                    with self.assertRaises(ValueError):
                        pm._powermetrics_documents(b'broken first frame')
                self.assertEqual(parse.call_count, 5)
                self.assertEqual(len(h._DOCUMENT_MEMO.get()), 2)
            self.assertIsNone(h._DOCUMENT_MEMO.get())
            with h.document_memo():
                pm._powermetrics_documents(a)
            self.assertEqual(parse.call_count, 6)

    def test_auto_must_refuse_when_one_gigabyte_member_cannot_fit(self):
        # F5: max(1, ...) silently violates the memory budget even at one worker.
        gib = 1 << 30
        try:
            sizing = runner.auto_workers(peak_bytes=8*gib, memory=2*gib, cores=8)
        except ValueError:
            return
        self.assertLessEqual(sizing['workers'] * sizing['peak_bytes_per_worker'] + sizing['reserve_bytes'],
                             sizing['free_memory_bytes'], 'auto launched a worker that cannot fit')

    def test_failed_small_sweep_must_not_size_a_gigabyte_window(self):
        receipt = self.root / 'SWEEP.json'
        receipt.write_text(json.dumps({'runs': [{'workers': 10, 'exit': 1, 'peak_child_rss_bytes': 1 << 20}]}))
        with self.assertRaises((ValueError, KeyError), msg='failed/tiny sweep was accepted as a sizing basis'):
            runner._sweep_peak(receipt)


class ThermalWitnesses(unittest.TestCase):
    def test_adversarial_raw_thermal_journals_keep_light_and_full_equal(self):
        from tests.align.test_attribution import episode, turn, NS
        from tests.align.test_attribution_holds import gate
        from tests.align.test_thermal_gate import policy
        p = policy()
        ep = episode(turns=(turn(),), hardware={'thermal': {'policy': p,
            'intervals': [gate('G0', -NS, 0), gate('H', 4*NS, 7*NS)]}})
        journal = [{'kind': 'sample', 'monotonic_ns': i*NS,
                    'finished': {'monotonic_after_ns': i*NS},
                    'sensors': {key: 40. for key in td.temperature.keys(p['sensors'])}, 'errors': {}}
                   for i in range(-2, 12)]
        duplicate = deepcopy(journal) + [deepcopy(journal[9])]
        wrong_release = deepcopy(journal)
        wrong_release[9]['sensors'][p['sensors']['s_fast']] = 70.
        sparse = journal[::3]
        samples = [{'start_ns': i*NS, 'end_ns': (i+1)*NS, 'state': 'Nominal',
                    'active_ns': NS, 'clock_mhz': 1000.} for i in range(-2, 12)]
        for label, rows in [('empty', []), ('duplicate exit', duplicate),
                            ('wrong release', wrong_release), ('sparse', sparse), ('valid', journal)]:
            with self.subTest(journal=label):
                r = td.member_record(ep, rows, os_readings=[(-NS, 0), (12*NS, 0)],
                    registered_os_readings=[(0, 0)], pm_samples=samples, pm_period_s=1,
                    source='mock', channel='package', gate_journal=rows)
                r.update(window='C1', identical_work_group='replay')
                r['calibration_exclusions'] = td.calibration_exclusions(r)
                records = []
                for name in ('a', 'b'):
                    m = deepcopy(r)
                    m['id'] = name
                    records.append(m)
                light = [lt.apply_harvest_codes(deepcopy(m), []) for m in records]
                full = [lt.apply_harvest_codes(deepcopy(m), ['battery.member_span', 'clock.step'])
                        for m in records]
                a, b = td.window_report(light, v4=True), td.window_report(full, v4=True)
                self.assertEqual(lt.thermal_escalation(a), lt.thermal_escalation(b))
                self.assertEqual(lt.u_checks(a), lt.u_checks(b))
                if label in ('duplicate exit', 'wrong release'):
                    self.assertNotEqual(a['model_windows'][f'{r["model"]}/C1']['U2']['status'], 'pass')

    def test_adversarial_thermal_records_keep_light_and_full_u1_u3_equal(self):
        from tests.align.test_thermal_desk import member
        for flags in ([], ['thermal.start_gate_timeout'], ['thermal.os_level_nonzero'],
                      ['thermal.collector_thread_dead'], ['episode.deadman:1800']):
            for codes in ([], ['battery.member_span'], ['clock.step', 'member.strict_invalid']):
                with self.subTest(flags=flags, codes=codes):
                    records = [member('a'), member('b')]
                    for r in records:
                        r.update(window='C1', identical_work_group='replay', flags=list(flags))
                        r['calibration_exclusions'] = td.calibration_exclusions(r)
                    full = [lt.apply_harvest_codes(deepcopy(r), codes) for r in records]
                    light = [lt.apply_harvest_codes(deepcopy(r), []) for r in records]
                    a, b = td.window_report(light, v4=True), td.window_report(full, v4=True)
                    self.assertEqual(lt.thermal_escalation(a), lt.thermal_escalation(b))
                    self.assertEqual(lt.u_checks(a), lt.u_checks(b))

    def test_inconclusive_thermal_must_not_be_reported_as_pass(self):
        # F6: the arm correctly rejects this; the CLI's status currently says pass.
        thermal = {'model_windows': {'tiny/C1': {f'U{k}': {'status': 'inconclusive'} for k in (1, 2, 3)}}}
        self.assertNotEqual(lt.thermal_escalation(thermal)['status'], 'pass')


class DwellWitnesses(ReviewBase):
    def test_git_verification_must_finish_before_the_dwell_starts(self):
        # F7: the meter ordering test misses four Git commands after dwell_start.
        from scripts import align_v4_session as session
        from tests.align.test_v4_next_arm_packet import ArmRebuildTests
        s = Scenario(self.root, 'W1').finish()
        events = []

        def start():
            events.append('dwell')
            return 200

        def committed(root, commit):
            events.append('git commit check')
            return session._commit_exists(root, commit)

        def bound(root, packet):
            events.append('git record binding')
            return session._record_bound(root, packet)

        with patch('joulewise.align.apple.powermode.host_state_dir', return_value=str(self.root / 'host')), \
                patch('joulewise.align.apple.powermode.host_marker_path', return_value=str(self.root / 'marker')):
            result = ArmRebuildTests().arm(s, s.build(), commit_check=committed, record_check=bound,
                meter_probe=lambda _: {'live': True, 'probe_started_ns': 1, 'probe_ended_ns': 100},
                dwell_start=start)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(events[-1], 'dwell', 'Git verification ran after the recorded quiet dwell began: ' + str(events))


class TurnTableWitnesses(unittest.TestCase):
    def test_real_desk_equality_and_clock_evidence_input_binding(self):
        # F8: equality is proven, but metadata used for the clock/uncertainty
        # join is omitted from the table's advertised complete input binding.
        with synthetic_custody_only():
            from tests.align.test_harvest_off import SyntheticV4SessionE2ETests as Fixture
            Fixture.setUpClass()
            try:
                case = Fixture('test_triage_desk_final_reduce_end_to_end')
                case.test_triage_desk_final_reduce_end_to_end()
                for row in Fixture.rows:
                    table = json.loads((Fixture.root / 'reduced' / row['run_id'] / 'turns.json').read_text())
                    self.assertIn('metadata.json', table['inputs'],
                                  'clock/uncertainty metadata used by both energy readers is not digest-bound')
            finally:
                Fixture.tearDownClass()


if __name__ == '__main__':
    unittest.main()
