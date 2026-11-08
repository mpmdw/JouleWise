"""Delta4 review witnesses: synthetic roots, fake host and fixture-owned children.

Run this module alone. Open findings assert the required property and fail
normally. Cold-import witnesses use fresh interpreters so leaked defaults cannot
contaminate the other tests. No native meter, launchd or model command executes.
"""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

from joulewise.align import w1_smoke as smoke
from tests.align import test_smoke_delta_sol1 as previous
from tests.align import test_w1_smoke as fixtures


def _cold_import_observation(fail_prepare):
    """Exercise production lazy imports, intercepting every possible subprocess.

    Only the imports are real production behavior here: the prepare body and
    later meter command are synthetic. The latter never starts a meter reader.
    """
    fixture = previous.DeltaFixture()
    fixture.setUp()
    try:
        assert 'scripts.align_v4_session' not in sys.modules
        calls = []

        def inner(argv, **kw):
            calls.append((argv, kw))
            return subprocess.CompletedProcess(argv, 1, b'', b'synthetic')

        def prepare(measurement, session, keep, **kw):
            # prepare_smoke imports this module at exactly this point: after
            # _prepare_budget has taken its loaded-module snapshot.
            importlib.import_module('scripts.align_v4_session')
            if fail_prepare:
                raise ValueError('synthetic prepare failure after lazy import')
            return fixtures.fake_prepare(measurement, session, keep)

        runner = fixture.runner(prepare=prepare)
        runner.dir.mkdir()
        runner.make_tmp()
        runner.clone = runner.dir / 'measurement'
        runner.deadline = fixture.clock() + 120
        with mock.patch.object(subprocess, 'run', inner):
            try:
                runner.prepare_main()
            except ValueError:
                assert fail_prepare
            session = sys.modules['scripts.align_v4_session']
            pilot = sys.modules['scripts.align_pilot_session']
            observation = {
                'module_run_restored': subprocess.run is inner,
                'meter_default_restored': session._probe_meter_live.__kwdefaults__['runner'] is inner,
                'desk_default_restored': pilot.desk.__kwdefaults__['run'] is inner,
            }
            fixture.clock.sleep(121)
            try:
                session._probe_meter_live(runner.clone, seconds=0)
            except Exception as exc:  # record the property failure in the parent test
                observation['later_call_error'] = type(exc).__name__
            else:
                observation['later_call_error'] = None
            observation['later_command_calls'] = len(calls)
        print(json.dumps(observation, sort_keys=True))
    finally:
        fixture.doCleanups()


class ColdImportBudget(unittest.TestCase):
    def observation(self, fail_prepare):
        script = ('from tests.align.test_smoke_delta4_sol1 import _cold_import_observation; '
                  f'_cold_import_observation({fail_prepare!r})')
        done = subprocess.run([sys.executable, '-B', '-c', script], capture_output=True,
                              text=True, timeout=20, env={**os.environ, 'TMPDIR': '/private/tmp'})
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def test_lazily_imported_defaults_are_restored_after_success(self):
        row = self.observation(False)
        self.assertTrue(row['module_run_restored'], row)
        self.assertEqual(row['later_call_error'], None, row)
        self.assertTrue(row['meter_default_restored'] and row['desk_default_restored'], row)
        self.assertEqual(row['later_command_calls'], 1, row)

    def test_lazily_imported_defaults_are_restored_after_failure(self):
        row = self.observation(True)
        self.assertTrue(row['module_run_restored'], row)
        self.assertEqual(row['later_call_error'], None, row)
        self.assertTrue(row['meter_default_restored'] and row['desk_default_restored'], row)
        self.assertEqual(row['later_command_calls'], 1, row)


class PrepareBudget(previous.DeltaFixture):
    def stage(self, **kw):
        runner = self.runner(**kw)
        runner.dir.mkdir()
        runner.make_tmp()
        runner.clone = runner.dir / 'measurement'
        runner.deadline = self.clock() + 120
        return runner

    def test_loaded_defaults_run_and_temp_environment_restore_on_all_body_exits(self):
        from scripts import bytes_h_session as h
        original = subprocess.run
        defaults = dict(h.important_capacity.__kwdefaults__)
        saved_env, saved_temp = os.environ.get('TMPDIR'), tempfile.tempdir
        for index, error in enumerate((None, ValueError, smoke.BudgetExpired, KeyboardInterrupt, SystemExit)):
            with self.subTest(error=error):
                def prepare(measurement, session, keep, **kw):
                    self.assertIsNot(subprocess.run, original)
                    self.assertIsNot(h.important_capacity.__kwdefaults__['run'], defaults['run'])
                    if error:
                        raise error('synthetic body exit')
                    return fixtures.fake_prepare(measurement, session, keep)

                runner = self.stage(smoke_dir=self.tmp / f'body-exit-{index}', prepare=prepare)
                if error:
                    with self.assertRaises(error):
                        runner.prepare_main()
                else:
                    self.assertTrue(runner.prepare_main()[0])
                self.assertIs(subprocess.run, original)
                self.assertEqual(h.important_capacity.__kwdefaults__, defaults)
                self.assertEqual(os.environ.get('TMPDIR'), saved_env)
                self.assertEqual(tempfile.tempdir, saved_temp)

    def test_budget_wrapper_clips_and_preserves_command_options(self):
        runner = self.stage()
        runner.deadline = self.clock() + 7.5
        calls = []

        def inner(argv, **kw):
            calls.append(kw)
            return subprocess.CompletedProcess(argv, 0, b'bytes', b'')

        bounded = runner.budgeted_subprocess(inner, 'prepare')
        for timeout, expected in ((60, 7.5), (None, 7.5), (2, 2)):
            with self.subTest(timeout=timeout):
                done = bounded(['synthetic'], timeout=timeout, capture_output=True, check=True,
                               cwd=str(runner.dir), env=runner.env)
                self.assertEqual(done.stdout, b'bytes')
                self.assertEqual(calls[-1]['timeout'], expected)
                self.assertTrue(calls[-1]['check'])
                self.assertTrue(calls[-1]['start_new_session'])
                self.assertEqual(calls[-1]['env'], runner.env)
        bounded(['synthetic'])
        self.assertEqual(calls[-1]['timeout'], 7.5)
        self.clock.sleep(8)
        with self.assertRaises(smoke.BudgetExpired):
            bounded(['must-not-execute'])
        self.assertEqual(len(calls), 4)

    def test_unrelated_thread_keeps_its_timeout_during_prepare(self):
        ready, finished = threading.Event(), threading.Event()
        observed, errors = [], []

        def inner(argv, **kw):
            observed.append(kw['timeout'])
            return subprocess.CompletedProcess(argv, 0, '', '')

        def worker():
            try:
                if not ready.wait(5):
                    raise RuntimeError('prepare did not release fixture worker')
                subprocess.run(['synthetic-unrelated-command'], timeout=600)
            except BaseException as exc:
                errors.append(type(exc).__name__)
            finally:
                finished.set()

        def prepare(measurement, session, keep, **kw):
            ready.set()
            if not finished.wait(5):
                raise RuntimeError('fixture worker did not finish')
            return fixtures.fake_prepare(measurement, session, keep)

        runner = self.stage(prepare=prepare)
        with mock.patch.object(subprocess, 'run', inner):
            thread = threading.Thread(target=worker)
            thread.start()
            try:
                self.assertTrue(runner.prepare_main()[0])
            finally:
                ready.set()
                thread.join(6)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(observed, [600], 'global smoke patch changed an unrelated thread command')

    def test_thread_callback_captured_during_prepare_outlives_the_scope(self):
        released = threading.Event()
        observed, errors, threads = [], [], []

        def inner(argv, **kw):
            observed.append(kw['timeout'])
            return subprocess.CompletedProcess(argv, 0, '', '')

        def worker(callback):
            try:
                if not released.wait(5):
                    raise RuntimeError('fixture callback was not released')
                callback(['synthetic-deferred-command'], timeout=600)
            except BaseException as exc:
                errors.append(type(exc).__name__)

        def prepare(measurement, session, keep, **kw):
            thread = threading.Thread(target=worker, args=(subprocess.run,))
            threads.append(thread)
            thread.start()
            return fixtures.fake_prepare(measurement, session, keep)

        runner = self.stage(prepare=prepare)
        with mock.patch.object(subprocess, 'run', inner):
            try:
                self.assertTrue(runner.prepare_main()[0])
                self.assertIs(subprocess.run, inner)
                self.clock.sleep(121)
            finally:
                released.set()
                for thread in threads:
                    thread.join(6)
        self.assertTrue(threads)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(errors, [], 'captured subprocess.run retained the ended smoke budget')
        self.assertEqual(observed, [600])


class GroupedCommands(previous.DeltaFixture):
    def test_subprocess_results_and_exceptions_are_preserved(self):
        done = smoke.grouped_run([sys.executable, '-B', '-c', 'print("synthetic")'],
                                 capture_output=True, timeout=3)
        self.assertEqual(done.stdout, b'synthetic\n')
        with self.assertRaises(subprocess.CalledProcessError) as error:
            smoke.grouped_run([sys.executable, '-B', '-c', 'raise SystemExit(7)'],
                              check=True, timeout=3)
        self.assertEqual(error.exception.returncode, 7)
        with self.assertRaises(subprocess.TimeoutExpired):
            smoke.grouped_run([sys.executable, '-B', '-c', 'import time; time.sleep(10)'], timeout=.2)

    def test_normal_and_error_exits_kill_descendants_with_closed_pipes(self):
        for rc in (0, 7):
            with self.subTest(rc=rc):
                marker = self.tmp / f'group-{rc}.json'
                script = ('import json,os,sys,time\n'
                          'child=os.fork()\n'
                          'if child == 0:\n'
                          ' os.close(1); os.close(2)\n'
                          ' with open(sys.argv[1],"w") as f: json.dump(os.getpgrp(),f)\n'
                          ' time.sleep(10)\n'
                          'else:\n'
                          ' while not os.path.exists(sys.argv[1]) or not os.path.getsize(sys.argv[1]): time.sleep(.01)\n'
                          ' sys.exit(int(sys.argv[2]))\n')
                try:
                    argv = [sys.executable, '-B', '-c', script, str(marker), str(rc)]
                    if rc:
                        with self.assertRaises(subprocess.CalledProcessError):
                            smoke.grouped_run(argv, capture_output=True, check=True, timeout=3)
                    else:
                        self.assertEqual(smoke.grouped_run(argv, capture_output=True, timeout=3).returncode, 0)
                    self.assertTrue(marker.is_file())
                    self.assertFalse(smoke._group_alive(json.loads(marker.read_bytes())))
                finally:
                    if marker.is_file():
                        pgid = json.loads(marker.read_bytes())
                        self.assertNotEqual(pgid, os.getpgrp())
                        try:
                            os.killpg(pgid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass


class FixControls(previous.DeltaFixture):
    def test_anchor_survives_parent_move_without_redirecting_writes(self):
        parent = self.tmp / 'parent'
        parent.mkdir()
        base = parent / 'smoke'
        anchor = smoke.Anchor.establish(base, create=True)
        try:
            parent.rename(self.tmp / 'parent-moved')
            base.mkdir(parents=True)
            smoke.safe_write(anchor, base / 'evidence', b'complete')
            self.assertFalse((base / 'evidence').exists())
            self.assertEqual((self.tmp / 'parent-moved/smoke/evidence').read_bytes(), b'complete')
        finally:
            anchor.close()

    def test_no_progress_write_raises_instead_of_spinning(self):
        base = self.tmp / 'base'
        base.mkdir()
        with mock.patch.object(smoke.os, 'write', return_value=0):
            with self.assertRaises(OSError):
                smoke.safe_write(base, base / 'evidence', b'complete')

    def test_plan_option_refuses_stale_or_ambiguous_option_shapes(self):
        for argv in ([], ['--plan'], ['--plan', '--courier-bin'], ['--plan=x'],
                     ['--plan', 'x', '--plan', 'x'], ['--plan', 'wrong', '--courier-bin', 'right']):
            with self.subTest(argv=argv):
                self.assertNotEqual(smoke.plan_option(argv), 'right')
        self.assertEqual(smoke.plan_option(['program', '--plan', 'right']), 'right')

    def test_failed_main_arm_reaches_the_cli_as_exit_one(self):
        from scripts import align_v4_w1_smoke as cli
        self.mbp = fixtures.FakeMBP(self, self.clock, main_rc=1)
        runner = self.runner()
        packet = self.tmp / 'packet.json'
        packet.write_text('{}')
        argv = ['run', '--measurement-root', str(self.production), '--smoke-dir', str(runner.dir),
                '--prequal-report', str(self.prequal), '--next-arm-triage', str(packet),
                '--w1-disk-config', str(self.tmp / 'disk'), '--obc-off-attested-by', 'synthetic',
                '--battery-log', str(self.tmp / 'battery')]
        with mock.patch.object(cli.smoke, 'SmokeRunner', return_value=runner), \
                mock.patch.object(smoke, 'ARM_FAULTS', []):
            self.assertEqual(cli.main(argv), 1)
        rows = [json.loads(line) for line in (runner.dir / smoke.LOG).read_text().splitlines()]
        self.assertEqual(next(row['outcome'] for row in rows if row['step'] == 'arm-main'), 'fail')
        self.assertEqual(rows[-1]['code'], 1)
        self.assertIsNone(runner.anchor)


if __name__ == '__main__':
    unittest.main()
