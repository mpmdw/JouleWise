"""Delta review of ed65d9094: synthetic paths, fake host, tiny child processes.

These assert the required safety properties. Unfixed properties FAIL visibly;
no expectedFailure or opt-in hides them. Run this module alone with a realpath
TMPDIR. Never launch the native smoke or follow configured production paths.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

from joulewise import night_gate
from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from scripts import align_v4_session, align_v4_w1_smoke as cli
from tests.align.test_smoke_review_sol2 import ReviewFixture
from tests.align.test_w1_prequal import RebuildingArm
from tests.align.test_w1_smoke import FakeMBP, fake_prepare


class DeltaFixture(ReviewFixture):
    def setUp(self):
        super().setUp()
        home = self.tmp / 'synthetic-home'
        home.mkdir()
        patch = mock.patch.object(Path, 'home', return_value=home)
        patch.start()
        self.addCleanup(patch.stop)


class IsolationDelta(DeltaFixture):
    def test_literal_resolved_relative_private_and_tmpdir_controls(self):
        directory = self.tmp / 'smoke'
        directory.mkdir()
        alias = directory / 'alias'
        alias.symlink_to(self.production, target_is_directory=True)
        roots = smoke.production_roots(self.production, self.config)
        for path in (str(self.production / 'runs'), str(alias / 'runs'), '../production/runs'):
            with self.subTest(path=path):
                self.assertTrue(smoke.isolation_violations(
                    directory, {'custody_root': path}, roots))
        self.assertEqual(smoke._norm('/private/tmp/synthetic-custody'), '/tmp/synthetic-custody')
        self.assertTrue(smoke.isolation_violations(directory, {}, roots,
                                                 env={'TMPDIR': str(self.production / 'tmp')}))
        alias.unlink()  # Remove the deliberately forbidden link before the clean control.
        self.assertFalse(smoke.isolation_violations(directory, {}, roots,
                                                  env={'TMPDIR': str(directory / 'tmp')}))

    def test_installed_unloaded_night_and_deadman_plists_stop_the_run(self):
        for label in (smoke.NIGHT_LABEL, smoke.NIGHT_LABEL + '.deadman'):
            with self.subTest(label=label):
                plist = Path.home() / 'Library/LaunchAgents' / (label + '.plist')
                plist.parent.mkdir(parents=True, exist_ok=True)
                plist.write_text('synthetic published plan')
                mbp = FakeMBP(self, self.clock)
                runner = self.runner(mbp, directory=self.tmp / label)
                runner.dir.mkdir()
                admitted, _ = runner.guards()
                self.assertFalse(admitted)
                self.assertIsNone(mbp.main_state)
                plist.unlink()

    def test_detach_refuses_protected_destination_before_mkdir_or_spawn(self):
        destination = self.production / 'new-parent/smoke'
        config_path = self.production / 'packet.json'
        config_path.write_text('{}')
        argv = ['run', '--detach', '--measurement-root', str(self.production),
                '--smoke-dir', str(destination), '--prequal-report', str(self.prequal),
                '--next-arm-triage', str(config_path), '--w1-disk-config', str(config_path),
                '--obc-off-attested-by', 'synthetic', '--battery-log', str(config_path)]
        with mock.patch.object(smoke, 'detach', return_value=12345) as detach:
            try:
                rc = cli.main(argv)
            except SystemExit as exc:
                rc = exc.code
        self.assertFalse(destination.parent.exists(), 'detach created a protected production directory')
        detach.assert_not_called()
        self.assertNotEqual(rc, 0)

    def test_symlink_swap_after_final_check_cannot_redirect_packet_write(self):
        victim = self.production / 'runs/synthetic-victim'
        victim.mkdir(parents=True)
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp)
        original = runner.check_isolation

        def swap(state, step, **kwargs):
            original(state, step, **kwargs)
            if step == 'arm-main':
                staging = runner.dir / 'main/staging'
                staging.rename(staging.with_name('staging.saved'))
                staging.symlink_to(victim, target_is_directory=True)

        runner.check_isolation = swap
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            runner.run()
        self.assertFalse((victim / 'smoke-next-arm-triage.json').exists(),
                         'packet write followed a symlink installed after the last isolation check')

    def test_tmpdir_swap_after_final_check_cannot_reach_command(self):
        victim = self.production / 'synthetic-command-tmp'
        victim.mkdir()
        seen = []

        class TempWritingHost(FakeMBP):
            def __call__(host, argv, **kwargs):
                if 'install' in argv and '--session-root' in argv:
                    tmp = Path(kwargs['env']['TMPDIR'])
                    seen.append(tmp.resolve())
                    (tmp / 'synthetic-child-output').write_text('temporary command output')
                return super().__call__(argv, **kwargs)

        runner = self.runner(TempWritingHost(self, self.clock))
        original = runner.check_isolation

        def swap(state, step, **kwargs):
            original(state, step, **kwargs)
            if step == 'arm-main':
                tmp = runner.dir / 'tmp'
                tmp.rmdir()
                tmp.symlink_to(victim, target_is_directory=True)

        runner.check_isolation = swap
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            runner.run()
        self.assertNotIn(victim.resolve(), seen, 'install command received an escaped TMPDIR')
        self.assertFalse((victim / 'synthetic-child-output').exists())


class LifecycleDelta(DeltaFixture):
    def test_failed_teardown_and_exhausted_budget_stop_main_arm_controls(self):
        for mode in ('teardown', 'budget'):
            with self.subTest(mode=mode):
                mbp = FakeMBP(self, self.clock, still_mounted=mode == 'teardown')
                runner = self.runner(mbp, directory=self.tmp / mode)
                original = runner.arm_fault

                def slow(*args):
                    result = original(*args)
                    self.clock.sleep(self.config['budget_s'] + 1)
                    return result

                if mode == 'budget':
                    runner.arm_fault = slow
                self.assertNotEqual(runner.run(), 0)
                self.assertIsNone(mbp.main_state)

    def test_isolate_commands_use_remaining_budget_and_local_tmpdir(self):
        runner = self.runner(FakeMBP(self, self.clock))
        runner.dir.mkdir()
        runner.started, runner.deadline = self.clock(), self.clock() + 1
        runner.isolate_fn = smoke.isolate
        observed = []

        def command(argv, **kwargs):
            observed.append((list(argv), kwargs))
            raise RuntimeError('stop before any real command or filesystem mutation')

        with mock.patch.object(smoke.subprocess, 'run', command):
            with self.assertRaisesRegex(RuntimeError, 'stop before'):
                runner.isolate()
        self.assertTrue(observed)
        with self.subTest(property='timeout'):
            self.assertLessEqual(observed[0][1]['timeout'], 1,
                                 'isolation bypasses the single remaining-budget command runner')
        with self.subTest(property='TMPDIR'):
            self.assertEqual((observed[0][1].get('env') or {}).get('TMPDIR'), str(runner.dir / 'tmp'))

    def test_install_side_effect_is_cleaned_when_command_reports_surviving_group(self):
        class InstallsThenFails(FakeMBP):
            def install(host, argv):
                result = super().install(argv)
                host.job_loaded = True
                result.group_survived = True
                return result

        mbp = InstallsThenFails(self, self.clock)
        runner = self.runner(mbp)
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            self.assertNotEqual(runner.run(), 0)
        self.assertIsNotNone(mbp.main_state, 'fixture must install before reporting command failure')
        self.assertFalse(mbp.job_loaded, 'owned launchd job survived because ownership was recorded too late')

    def test_term_ignoring_descendant_with_closed_pipes_is_killed_control(self):
        # The descendant records its PID before closing inherited output pipes.
        # Signal only this fixture's process group, with a final cleanup guard.
        pidfile = self.tmp / 'descendant.pid'
        script = ('import os,signal,time\n'
                  'child=os.fork()\n'
                  'if child == 0:\n'
                  ' signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                  ' open(' + repr(str(pidfile)) + ',"w").write(str(os.getpid()))\n'
                  ' os.close(1); os.close(2)\n'
                  ' time.sleep(60)\n'
                  'else:\n'
                  ' time.sleep(60)\n')
        result = None
        try:
            result = smoke.bounded_run([sys.executable, '-B', '-c', script], timeout=2)
            self.assertEqual(result.returncode, 124)
            self.assertTrue(pidfile.is_file(), 'the descendant must reach its TERM-ignoring state')
            self.assertFalse(result.group_survived, result.stderr)
            with self.assertRaises(ProcessLookupError):
                os.killpg(result.pgid, 0)
        finally:
            if result is not None:
                try:
                    import signal
                    os.killpg(result.pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


class AdmissionDelta(DeltaFixture):
    def test_forged_installed_plan_is_refused(self):
        # A declaration with schema/receipt labels is still not an installed plan.
        forged = {'schema': night_gate.HAZARD_PLAN_SCHEMA, 'receipt_class': night_gate.HAZARD_PACK,
                  'plan_id': 'align-v4-forged', 'window_max_s': 20000,
                  'pack': {'programmed_span_s': 0}}
        with self.assertRaises(night_gate.PlanError):
            night_gate.NightPlan.from_mapping(forged)
        name = self.projection('forged-night_plan.json', forged)
        row = wp.probe('deadline', self.ctx(deadline_projection=name))
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_decoy_span_cannot_override_actual_hazard_span(self):
        forged = {'schema': night_gate.HAZARD_PLAN_SCHEMA, 'receipt_class': night_gate.HAZARD_PACK,
                  'plan_id': 'align-v4-forged', 'window_max_s': 20000,
                  'programmed_span_s': 0, 'hazard_window': {'programmed_span_s': 26927}}
        name = self.projection('decoy-night_plan.json', forged)
        row = wp.probe('deadline', self.ctx(deadline_projection=name))
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_series_hash_and_roster_controls(self):
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration', 'benign_per_pair': {'spam': 7, 'bank': 7}}
                      for i in range(1, 9)] + [{'window': 'T1', 'role': 'test'}])
        source = self.projection('source.json', {'windows': windows})
        projection = {'schema': wp.SERIES_SCHEMA, 'windows': copy.deepcopy(windows), 'source': {
            'path': source, 'sha256': hashlib.sha256((self.production / source).read_bytes()).hexdigest()}}
        name = self.projection('series.json', projection)
        self.assertEqual(wp.probe('series-manifest', self.ctx(series_projection=name))['status'], wp.PASS)
        projection['windows'][1]['benign_per_pair']['spam'] = 6
        self.projection('series.json', projection)
        self.assertEqual(wp.probe('series-manifest', self.ctx(series_projection=name))['status'], wp.FAIL)
        projection['windows'] = windows
        projection['source']['sha256'] = '0' * 64
        self.projection('series.json', projection)
        self.assertEqual(wp.probe('series-manifest', self.ctx(series_projection=name))['status'], wp.FAIL)

    def test_packet_probe_catches_nested_status_leniency_control(self):
        class LenientStatus(RebuildingArm):
            def __call__(arm, root, plan, *, next_arm_triage=None, **kwargs):
                value = json.loads(Path(next_arm_triage).read_text())
                if isinstance((value.get('checks') or {}).get('capture_faults'), dict):
                    value['checks']['capture_faults']['status'] = 'pass'
                path = Path(next_arm_triage).with_suffix('.normalized.json')
                path.write_text(json.dumps(value))
                return super().__call__(root, plan, next_arm_triage=path, **kwargs)

        ctx = self.ctx()
        with mock.patch.object(align_v4_session, 'arm_checks', LenientStatus()):
            row = wp.probe('packet-tamper', ctx)
        self.assertEqual(row['status'], wp.FAIL, row)
        self.assertTrue(any('status flipped' in label for label in row['evidence']['admitted_mutations']))

    def test_packet_probe_rejects_arm_ignoring_one_chain_elements_later_leaf(self):
        class LenientElement(RebuildingArm):
            def rebuild(arm, root):
                packet = super().rebuild(root)
                for entry in packet['calibration_windows']:
                    entry['status'] = 'final'
                return packet

            def __call__(arm, root, plan, *, next_arm_triage=None, **kwargs):
                value = json.loads(Path(next_arm_triage).read_text())
                rows = value.get('calibration_windows')
                if isinstance(rows, list) and len(rows) > 1 and isinstance(rows[1], dict):
                    rows[1]['status'] = 'final'
                path = Path(next_arm_triage).with_suffix('.normalized.json')
                path.write_text(json.dumps(value))
                return super().__call__(root, plan, next_arm_triage=path, **kwargs)

        arm, ctx = LenientElement(), self.ctx()
        with mock.patch.object(align_v4_session, 'arm_checks', arm):
            row = wp.probe('packet-tamper', ctx)
            root = next(ctx.work.glob('tamper-*'))
            packet = arm.rebuild(root)
            packet['calibration_windows'][1]['status'] = 'edited'
            direct = wp._arm_file(ctx, root, packet, now=packet['valid_until_epoch_s'] - 1)
        self.assertTrue(direct['admitted'], 'fixture must reproduce the single-element escape')
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_receipt_static_closure_covers_scripts_control(self):
        from joulewise.align.apple import v4_registration as reg
        root = Path(__file__).resolve().parents[2]
        closure = wp.executed_closure(root)
        self.assertTrue(any(p.startswith('scripts/') for p in closure))
        self.assertEqual(sorted(closure - set(reg.ARTIFACTS)), [])


if __name__ == '__main__':
    unittest.main()
