"""Independent delta review of 6938c3733: synthetic witnesses, no native data.

Run this module alone. Red assertions state the required property, rather than
blessing the observed defect. No test invokes a harvest or a measurement job.
"""
from tests.git_fixture import init_git_fixture
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.align import synthetic_custody
from joulewise.align.apple import harvest_offload as off
from scripts import align_v4_harvest_off as runner
from scripts import align_v4_next_arm_packet as builder
from tests.align.test_v4_next_arm_packet import Scenario, evaluate

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


class Scratch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hoff-delta-sol1-', dir=REAL_TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def checkout(self):
        root = self.root / 'checkout'
        root.mkdir()
        (root / '.gitignore').write_text('.venv/\nruns/\n')
        (root / 'collector.py').write_text('VERSION = 1\n')
        # Only the installed interpreter; no model, dependency installation or download.
        (root / '.venv/bin').mkdir(parents=True)
        (root / '.venv/bin/python').symlink_to(sys.executable)
        init_git_fixture(root, '-q')
        for args in (('add', '.'), ('commit', '-qm', 'synthetic checkout')):
            subprocess.run(['git', '-c', 'user.name=Synthetic', '-c',
                            'user.email=synthetic@example.invalid', '-C', str(root), *args],
                           check=True, capture_output=True)
        return root


class ClosureWitnesses(Scratch):
    def test_finalize_cost_on_22_tiny_members_and_shared_external_input(self):
        source = self.root / 'session'
        source.mkdir()
        external = self.root / 'shared-input'
        external.write_bytes(b'x' * (64 << 10))
        for index in range(22):
            member = source / f'member-{index:02d}'
            member.mkdir()
            (member / 'raw').write_bytes(b'r' * (64 << 10))
            (member / 'shared').symlink_to(external)
        # _tree_rows is the previous finalizer's inventory algorithm. Compare
        # only that common output; the new closure deliberately adds binding.
        started = time.perf_counter()
        before = off._tree_rows(source)
        baseline_s = time.perf_counter() - started
        with mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashed:
            started = time.perf_counter()
            final = off.finalized_manifest(source)
            finalize_s = time.perf_counter() - started
        self.assertEqual(final['entries'], before)
        self.assertEqual(sum(call.args[0] == external for call in hashed.call_args_list), 1)
        self.assertEqual(len(hashed.call_args_list), 23)
        print(json.dumps({'synthetic_finalize_cost': {'members': 22, 'raw_bytes': 22 * (64 << 10),
            'external_bytes': 64 << 10, 'hash_calls': 23,
            'inventory_s': baseline_s, 'finalize_s': finalize_s}}), file=sys.stderr)

    def test_link_to_link_must_refuse_before_reading_the_ultimate_target(self):
        source = self.root / 'session'
        source.mkdir()
        target = self.root / 'journal'
        target.write_bytes(b'synthetic journal\n')
        alias = self.root / 'alias'
        alias.symlink_to(target)
        (source / 'journal').symlink_to(alias)
        # A further link inside a directory already refuses; a direct target
        # that is itself a link must have the same rule, before hashing it.
        with mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashed:
            with self.assertRaisesRegex(off.OffloadRefused, 'link'):
                off.finalized_manifest(source)
            hashed.assert_not_called()

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_ignored_checkout_input_must_not_change_under_an_equal_mirror_identity(self):
        checkout = self.checkout()
        evidence = checkout / 'runs/ignored-evidence.jsonl'
        evidence.parent.mkdir()
        evidence.write_bytes(b'MBP input\n')
        source = self.root / 'session'
        source.mkdir()
        (source / 'measurement').symlink_to(checkout, target_is_directory=True)
        identity = runner.checkout_identity(checkout)
        self.assertTrue(runner._usable_identity(identity), identity)
        final = off.finalized_manifest(source, mirror={'root': str(checkout), 'identity': identity})
        off.pack(source, self.root / 'offload', finalized=final, mirror_identity=identity)
        source.rename(self.root / 'kept')
        evidence.write_bytes(b'Air input\n')
        here = runner.checkout_identity(checkout)
        self.assertEqual(here, identity)  # real Git and real interpreter identity
        try:
            off.unpack(self.root / 'offload', finalized=final,
                       finalized_sha256=off.manifest_sha256(final), mirror_identity=here)
        except off.OffloadRefused:
            self.assertFalse(source.exists())
            return
        self.assertEqual((source / 'measurement/runs/ignored-evidence.jsonl').read_bytes(), b'MBP input\n',
                         'record-bound restore admitted different ignored input bytes')

    def test_external_count_byte_and_per_file_limits_refuse_before_an_over_limit_hash(self):
        source = self.root / 'session'
        source.mkdir()
        external = self.root / 'external'
        external.mkdir()
        (external / 'a').write_bytes(b'abc')
        (external / 'b').write_bytes(b'def')
        (source / 'external').symlink_to(external, target_is_directory=True)
        for field, limit in (('CLOSURE_MAX_FILES', 1), ('CLOSURE_MAX_BYTES', 5),
                             ('CLOSURE_MAX_FILE_BYTES', 2)):
            with self.subTest(field), mock.patch.object(off, field, limit), \
                    mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashed:
                with self.assertRaises(off.OffloadRefused):
                    off.finalized_manifest(source)
                self.assertEqual(len(hashed.call_args_list), 0 if field == 'CLOSURE_MAX_FILE_BYTES' else 1)

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_retarget_refusal_preserves_checkout_code_with_an_honest_control(self):
        source = self.root / 'session'
        source.mkdir()
        (source / 'raw').write_bytes(b'raw\n')
        ledger = self.root / 'ledger'
        ledger.write_bytes(b'{"row":1}\n')
        code = self.root / 'collector.py'
        code.write_bytes(b'')
        final = off.finalized_manifest(source, inputs=(ledger,))
        transport = self.root / 'offload'
        manifest = off.pack(source, transport, finalized=final, external=(ledger,))
        source.rename(self.root / 'kept')
        manifest_path = transport / off.MANIFEST
        honest = manifest_path.read_bytes()
        next(iter(manifest['external'].values()))['path'] = str(code)
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(off.OffloadRefused, 'not bound'):
            off.unpack(transport, finalized=final, finalized_sha256=off.manifest_sha256(final))
        self.assertEqual(code.read_bytes(), b'')
        self.assertFalse(source.exists())
        manifest_path.write_bytes(honest)
        off.unpack(transport, finalized=final, finalized_sha256=off.manifest_sha256(final))
        self.assertEqual((source / 'raw').read_bytes(), b'raw\n')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_external_destination_parent_must_not_be_retargeted_into_checkout(self):
        source = self.root / 'session'
        source.mkdir()
        (source / 'raw').write_bytes(b'raw\n')
        original = self.root / 'ledger-directory'
        original.mkdir()
        (original / 'collector.py').write_bytes(b'ledger bytes\n')
        checkout = self.root / 'checkout'
        checkout.mkdir()
        code = checkout / 'collector.py'
        code.write_bytes(b'')  # valid append-only prefix, as in the seat-2 attack
        alias = self.root / 'ledger-location'
        alias.symlink_to(original, target_is_directory=True)
        ledger = alias / 'collector.py'
        final = off.finalized_manifest(source, inputs=(ledger,))
        off.pack(source, self.root / 'offload', finalized=final, external=(ledger,))
        source.rename(self.root / 'kept')
        alias.unlink()
        alias.symlink_to(checkout, target_is_directory=True)
        try:
            off.unpack(self.root / 'offload', finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
        except off.OffloadRefused:
            self.assertFalse(source.exists())
        self.assertEqual(code.read_bytes(), b'', 'bound path text allowed a write through a retargeted parent')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_external_staging_must_not_write_through_a_restored_link_on_refusal(self):
        source = self.root / 'session'
        source.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (source / '.external-staged').symlink_to(outside, target_is_directory=True)
        ledger = self.root / 'ledger'
        ledger.write_bytes(b'ledger bytes\n')
        try:
            final = off.finalized_manifest(source, inputs=(ledger,))
            off.pack(source, self.root / 'offload', finalized=final, external=(ledger,))
        except off.OffloadRefused:
            self.assertEqual(list(outside.iterdir()), [])
            return
        source.rename(self.root / 'kept')
        with self.assertRaises(off.OffloadRefused):
            off.unpack(self.root / 'offload', finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
        self.assertFalse(source.exists())
        self.assertEqual(list(outside.iterdir()), [],
                         'external staging wrote through the restored .external-staged link before refusal')


class SweepWitnesses(Scratch):
    def receipt(self, code):
        path = self.root / 'SWEEP.json'
        path.write_text(json.dumps({'schema': runner.SWEEP_SCHEMA, 'code': code,
            'largest_plist_bytes': 100, 'runs': [{'workers': 2, 'exit': 0, 'peak_child_rss_bytes': 1000}]}))
        return path

    def test_dirty_harvest_code_must_invalidate_a_previous_sweep(self):
        checkout = self.checkout()
        session = self.root / 'session'
        session.mkdir()
        (session / 'plan.json').write_text('{}')
        (session / 'session.json').write_text(json.dumps({'measurement_root': str(checkout),
            'plan_path': str(session / 'plan.json')}))
        code = runner.sweep_code_identity(session)
        receipt = self.receipt(code)
        with mock.patch.object(runner, 'largest_plist_bytes', return_value=100):
            self.assertEqual(runner.sweep_basis(receipt, session)[0], 1000)
            (checkout / 'collector.py').write_text('VERSION = 2\n')
            self.assertFalse(runner.checkout_identity(checkout)['tracked_clean'])
            try:
                peak, _ = runner.sweep_basis(receipt, session)
            except ValueError:
                return
            self.assertIsNone(peak, 'same HEAD and package versions do not bind dirty harvest code')

    def test_an_unidentified_interpreter_must_not_supply_a_bound_peak(self):
        code = {'head': 'a' * 40, 'python': None}
        with mock.patch.object(runner, 'sweep_code_identity', return_value=code), \
                mock.patch.object(runner, 'largest_plist_bytes', return_value=100):
            peak, _ = runner.sweep_basis(self.receipt(code), self.root)
        self.assertIsNone(peak, 'a missing interpreter is not an identified harvest program')

    def test_sweep_scales_up_with_ceiling_and_never_down(self):
        code = {'head': 'a' * 40, 'python': ['synthetic', 'packages']}
        receipt = self.receipt(code)
        value = json.loads(receipt.read_bytes())
        value['runs'][0]['peak_child_rss_bytes'] = 1001
        receipt.write_text(json.dumps(value))
        with mock.patch.object(runner, 'sweep_code_identity', return_value=code):
            for size, expected in ((101, 1012), (99, 1001), (1000, 10010)):
                with self.subTest(size), mock.patch.object(runner, 'largest_plist_bytes', return_value=size):
                    self.assertEqual(runner.sweep_basis(receipt, self.root)[0], expected)


class FinalityWitnesses(Scratch):
    def record(self, scenario):
        return builder.WindowRecord(builder.GitEvidence(self.root), scenario.record_commit, scenario.record_path)

    def test_completed_nonpassing_and_zero_capture_records_are_final_but_a_fault_with_capture_is_not(self):
        w1 = Scenario(self.root, 'W1').finish()
        zero = Scenario(self.root, 'C1', previous=w1, captured=False)
        zero.sources['desk'].update(harvest_status='not_run', pilot_status='instrument_incomplete')
        zero.sources['pilot']['status'] = 'instrument_incomplete'
        zero.finish()
        self.assertTrue(self.record(zero).is_final())
        fault = Scenario(self.root, 'C1#2', previous=zero)
        fault.sources['desk']['harvest_status'] = 'program_fault'
        fault.finish()
        self.assertFalse(self.record(fault).is_final())

    def test_corrected_seat1_witness_allows_light_then_refuses_k_plus_2(self):
        w1 = Scenario(self.root, 'W1').finish()
        c1 = Scenario(self.root, 'C1', previous=w1)
        c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C1',
            'thermal': copy.deepcopy(c1.thermal), 'checks': {'v4_B_bar': True},
            'km003c': c1.sources['pilot']['extra_checks']['km003c'],
            'series_desk_row': c1.sources['pilot']['extra_checks']['series_desk_row']}
        c1.sources['desk'] = {'plan_id': c1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
        c1.next_plan['window'] = 'C2'
        c1.finish()
        c1.passed_ref = dict(w1.passed_ref)
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        self.assertTrue(evaluate(c1, c1.build())['admitted'])
        c2 = Scenario(self.root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertFalse(evaluate(c2, packet)['admitted'])

    def test_zero_capture_light_only_attempt_must_stay_final_after_its_retry(self):
        w1 = Scenario(self.root, 'W1').finish()
        zero = Scenario(self.root, 'C1', previous=w1, captured=False, provisional=True)
        zero.next_plan['window'] = 'C1#2'
        zero.finish()
        first = zero.build()
        self.assertEqual(first['calibration_windows'][-1]['status'], 'final')
        self.assertEqual(first['calibration_windows'][-1]['captured_members'], 0)
        self.assertTrue(evaluate(zero, first)['admitted'])
        retry = Scenario(self.root, 'C1#2', previous=zero).finish()
        packet = retry.build()
        self.assertIsNone(packet.get('calibration_error'),
                          'a zero-capture row previously final at once became unfinished history')

    def final_session(self, *, captured=True, status='instrument_ok', harvest='ok'):
        (self.root / 'plan.json').write_text('{}')
        (self.root / 'session.json').write_text(json.dumps({'session_id': 'tiny',
            'plan_path': str(self.root / 'plan.json'), 'runs_roots': {'claim': str(self.root / 'runs')}}))
        if captured:
            (self.root / 'runs/member').mkdir(parents=True)
        (self.root / 'desk.json').write_text(json.dumps({'plan_id': 'tiny', 'harvest_status': harvest}))
        (self.root / 'PILOT.json').write_text(json.dumps({'plan_id': 'tiny', 'status': status,
            'extra_checks': {'thermal': {'model_windows': {'tiny/C1': {
                'U1': {'status': 'pass'}, 'U2': {'status': 'pass'}, 'U3': {'status': 'pass'}}},
                'members': [{'id': 'member', 'excluded': False, 'calibration_exclusions': []}]}}}))
        return SimpleNamespace(session_root=self.root, pilot=None, window_id='C1')

    def test_final_command_must_refuse_an_incomplete_pilot_adjudication(self):
        args = self.final_session(status='running_off_mbp')
        with mock.patch.object(runner, '_plan_rows', return_value=[{'run_id': 'member'}]):
            with self.assertRaises(ValueError):
                runner.cmd_final(args)

    def test_final_command_must_honor_the_zero_capture_no_harvest_exception(self):
        args = self.final_session(captured=False, status='instrument_incomplete', harvest='not_run')
        with mock.patch.object(runner, '_plan_rows', return_value=[{'run_id': 'member'}]):
            try:
                result = runner.cmd_final(args)
            except ValueError as exc:
                self.fail('the packet finality rule exempts zero captures, but cmd_final refused: ' + str(exc))
        self.assertEqual(result['calibration_row']['status'], 'final')
        self.assertEqual(result['calibration_row']['captured_members'], 0)


class FenceWitnesses(Scratch):
    def test_fence_must_reach_fresh_interpreters_before_any_filesystem_probe(self):
        # Text only: the child calls the path selector, never exists/stat/open.
        locator = str(synthetic_custody.HOME / 'night-custody/synthetic-never-probed')
        program = ('import json, sys; from pathlib import Path; '
                   'from joulewise import calibration_ledger as ledger; '
                   'print(json.dumps([str(p) for p in ledger._custody_probe_paths(Path(sys.argv[1]))]))')
        with synthetic_custody.fence():
            from joulewise import calibration_ledger as ledger
            self.assertEqual(ledger._custody_probe_paths(Path(locator)), ())
            child = subprocess.run([sys.executable, '-B', '-c', program, locator],
                                   check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(child.stdout), [], 'the parent patch is absent in spawned interpreters')

    # Lead ruling 2026-11-08 (D8 as built: record, then FAIL at teardown; RUN_STATE 240 on main: "seat-1's raise-in-hook
    # test ... is ruled wrong (D8)"; HARVEST-OFF-MERGED.md item 1): this raise-in-hook form is WRONG. It contradicts seat 2's
    # test_audit_must_report_filesystem_bytes_paths, so it stays an expected failure rather than a silent red.
    @unittest.expectedFailure
    def test_a_forbidden_open_audit_event_must_fail_the_test_not_only_log(self):
        # Deliver a fabricated event directly: no path is touched. Keep the
        # module's real audit counters separate from this simulated violation.
        locator = str(synthetic_custody.HOME / 'night-custody/synthetic-never-opened')
        with mock.patch.object(synthetic_custody, 'OPENED', []):
            with self.assertRaises((AssertionError, PermissionError)):
                synthetic_custody._audit('open', (locator, 'r', 0))


if __name__ == '__main__':
    unittest.main()
