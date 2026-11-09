"""Independent delta4 Sol seat 2: synthetic hosts, paths and tiny children only.

Open finding assertions describe the required property and fail without skips
or expectedFailure. Run this module alone; no hardware or measurements run.

Kit-owner adaptations (lead ruling 2026-11-08, delta4: the F6 monkeypatching is
DELETED; the production prepare runs in its own child process through
grouped_run, the remaining budget its hard wall timeout). Four PrepareBudget
tests named the deleted patch (``smoke_budgeted``, ``budgeted_subprocess``,
``_prepare_budget``); each now asserts the same property against the ruled design:
- test_loaded_defaults_and_environment_restore_on_normal_and_exceptional_exit:
  nothing is patched inside prepare; all exits leave run, defaults and temp state.
- test_setup_interruption_restores_already_patched_defaults: an interruption while
  the prepare child is being launched leaves run/defaults untouched (no setup exists
  to half-install) and closes the anchor pinned for that child.
- test_unrelated_thread_does_not_inherit_the_smoke_budget: the worker runs while
  prepare_main runs (there is no _prepare_budget scope any more).
- test_both_direct_and_default_commands_clip_timeout_and_check_tmp: a REAL prepare
  child whose direct command and 30 s capacity-style probe outlive the remaining
  budget is killed whole at that budget, proven gone, with TMPDIR checked before
  and after; it never waits out the probe's own timeout.
The cold-import, process, write and caller witnesses are unchanged.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest
from unittest import mock

from joulewise.align import w1_smoke as smoke
from tests.align import test_smoke_delta_sol1 as previous
from tests.align import test_w1_smoke as fixtures


class Fixture(previous.DeltaFixture):
    def staged(self, **kwargs):
        runner = self.runner(**kwargs)
        runner.dir.mkdir()
        runner.make_tmp()
        runner.clone = runner.dir / 'measurement'
        runner.clone.mkdir()
        runner.started = self.clock()
        runner.deadline = self.clock() + 120
        return runner


class PrepareBudget(Fixture):
    def test_loaded_defaults_and_environment_restore_on_normal_and_exceptional_exit(self):
        from scripts import bytes_h_session as h
        original = subprocess.run
        saved = {fn: dict(fn.__kwdefaults__) for fn in (h.prepare, h.important_capacity, h.install)}
        saved_env, saved_tempdir = os.environ.get('TMPDIR'), tempfile.tempdir
        for index, exception in enumerate((None, ValueError, smoke.BudgetExpired, KeyboardInterrupt)):
            with self.subTest(exception=exception):
                def prepare(measurement, session, keep, **kwargs):
                    # Adapted (delta4 ruling): nothing is patched while prepare runs.
                    self.assertIs(subprocess.run, original)
                    for fn, defaults in saved.items():
                        self.assertEqual(fn.__kwdefaults__, defaults)
                    if exception is not None:
                        raise exception('synthetic prepare interruption')
                    return fixtures.fake_prepare(measurement, session, keep)

                runner = self.staged(smoke_dir=self.tmp / f'smoke-{index}', prepare=prepare)
                if exception is None:
                    self.assertTrue(runner.prepare_main()[0])
                else:
                    with self.assertRaises(exception):
                        runner.prepare_main()
                self.assertIs(subprocess.run, original)
                for fn, defaults in saved.items():
                    self.assertEqual(fn.__kwdefaults__, defaults)
                self.assertEqual(os.environ.get('TMPDIR'), saved_env)
                self.assertEqual(tempfile.tempdir, saved_tempdir)

    def cold_import(self, fail):
        # A fresh interpreter reproduces the CLI's actual cold import order.
        # On the error path use the real prepare_smoke, stopping at its injected
        # prepare callback, after imports but before host/model/plan work.
        source = textwrap.dedent('''
            import functools, json, subprocess
            from joulewise.align import w1_smoke as smoke
            from tests.align.test_smoke_delta4_sol2 import Fixture
            from tests.align import test_w1_smoke as fixtures

            case = Fixture()
            case.setUp()
            try:
                original = subprocess.run
                def stop(*args, **kwargs):
                    raise ValueError('synthetic stop before production preparation')
                def prepare(measurement, session, keep, **kwargs):
                    from scripts import align_v4_session
                    return fixtures.fake_prepare(measurement, session, keep)
                callback = (functools.partial(smoke.prepare_smoke, prepare_fn=stop)
                            if FAIL else prepare)
                runner = case.staged(prepare=callback)
                try:
                    runner.prepare_main()
                except ValueError:
                    if not FAIL:
                        raise
                from scripts import align_v4_session as v4, align_pilot_session as pilot
                callbacks = [v4._probe_meter_live.__kwdefaults__['runner'],
                             pilot.desk.__kwdefaults__['run']]
                runner.deadline = runner.clock() - 1
                later = []
                for callback in callbacks:
                    try:
                        callback(['/usr/bin/true'], timeout=2)
                    except smoke.BudgetExpired:
                        later.append('stale smoke budget')
                    else:
                        later.append('ordinary subprocess')
                # Exercise the production consumer too. Its monitor path is a
                # tiny synthetic script, so a future repair cannot run hardware.
                scripts = runner.clone / 'scripts'
                scripts.mkdir()
                (scripts / 'km003c_monitor.py').write_text('raise SystemExit(0)\\n')
                try:
                    v4._probe_meter_live(runner.clone, seconds=.01)
                except smoke.BudgetExpired:
                    later_meter = 'stale smoke budget'
                else:
                    later_meter = 'ordinary subprocess'
                print(json.dumps({'global_restored': subprocess.run is original,
                                  'defaults_restored': [cb is original for cb in callbacks],
                                  'later_calls': later, 'later_meter_probe': later_meter}))
            finally:
                case.doCleanups()
        ''').replace('FAIL', repr(fail))
        result = subprocess.run([sys.executable, '-B', '-c', source], capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertTrue(observed['global_restored'], observed)
        self.assertEqual(observed['defaults_restored'], [True, True], observed)
        self.assertEqual(observed['later_calls'], ['ordinary subprocess'] * 2, observed)
        self.assertEqual(observed['later_meter_probe'], 'ordinary subprocess', observed)

    def test_cold_production_import_defaults_restore_after_success(self):
        self.cold_import(False)

    def test_cold_production_import_defaults_restore_after_prepare_failure(self):
        self.cold_import(True)

    def test_setup_interruption_restores_already_patched_defaults(self):
        # Adapted (delta4 ruling): interrupt the only setup left, the child launch.
        from scripts import bytes_h_session as h
        runner = self.staged(prepare=None)
        original = subprocess.run
        saved = dict(h.important_capacity.__kwdefaults__)
        anchors = []
        real_establish = smoke.Anchor.establish

        def establish(*args, **kwargs):
            anchors.append(real_establish(*args, **kwargs))
            return anchors[-1]

        with mock.patch.object(smoke.Anchor, 'establish', side_effect=establish), \
                mock.patch.object(smoke, 'grouped_run', side_effect=KeyboardInterrupt('operator interrupt')):
            with self.assertRaises(KeyboardInterrupt):
                runner.prepare_main()
        self.assertIs(subprocess.run, original)
        self.assertEqual(h.important_capacity.__kwdefaults__, saved)
        self.assertEqual(len(anchors), 1)
        self.assertIsNone(anchors[0].fd, 'the descriptor pinned for the child must be closed')

    def test_unrelated_thread_does_not_inherit_the_smoke_budget(self):
        # The report treats concurrency as advisory for the standalone CLI.
        # Keep the desired isolation property explicit rather than pinning the
        # process-wide interference as something a future fix must preserve.
        # Adapted (delta4 ruling): the worker runs during prepare_main itself.
        observed = []

        def unrelated():
            try:
                subprocess.run(['/usr/bin/true'], timeout=2)
            except smoke.BudgetExpired:
                observed.append('smoke budget')
            else:
                observed.append('ordinary subprocess')

        def prepare(measurement, session, keep, **kwargs):
            runner.deadline = self.clock() - 1          # the smoke budget is spent meanwhile
            worker = threading.Thread(target=unrelated)
            worker.start()
            worker.join(timeout=3)
            self.assertFalse(worker.is_alive())
            return fixtures.fake_prepare(measurement, session, keep)

        runner = self.staged(prepare=prepare)
        with self.assertRaises(smoke.BudgetExpired):    # the runner's own after-prepare check
            runner.prepare_main()
        self.assertEqual(observed, ['ordinary subprocess'])

    def test_both_direct_and_default_commands_clip_timeout_and_check_tmp(self):
        # Adapted (delta4 ruling): a real prepare child, its commands outliving the budget.
        import time
        runner = self.staged(prepare=None)
        runner.deadline = self.clock() + 1.5
        runner.config = dict(runner.config, prepare_reserve_s=1)  # below the 60 s entry reserve
        marker = self.tmp / 'probe.json'
        source = textwrap.dedent('''
            import json, os, subprocess, sys
            probe = subprocess.Popen(['/bin/sleep', '30'])            # a direct command
            with open(sys.argv[1], 'w') as handle:
                json.dump({'pgid': os.getpgrp(), 'probe': probe.pid}, handle)
            subprocess.run(['/bin/sleep', '30'], timeout=30)          # capacity-style 30 s probe
        ''')
        runner.prepare_child_argv = lambda session, result, fd: [sys.executable, '-B', '-c', source, str(marker)]
        checks = []
        real_verify = runner.verify_tmp
        runner.verify_tmp = lambda when: (checks.append(when), real_verify(when))
        started = time.monotonic()
        try:
            with self.assertRaises(smoke.BudgetExpired):
                runner.prepare_main()
            elapsed = time.monotonic() - started
            self.assertLess(elapsed, 6, 'the prepare child waited out its own command timeout')
            self.assertTrue(marker.is_file(), 'the child must have started its commands')
            self.assertFalse(smoke._group_alive(json.loads(marker.read_bytes())['pgid']))
            self.assertEqual(checks, ['before prepare child', 'after prepare child'])
        finally:
            if marker.is_file():
                self.assertTrue(smoke._kill_group(json.loads(marker.read_bytes())['pgid']))


class ProcessAndWrites(Fixture):
    def test_grouped_run_cleans_descendant_after_successful_leader(self):
        marker = self.tmp / 'owned-child.json'
        source = textwrap.dedent('''
            import json, os, sys, time
            from pathlib import Path
            marker = Path(sys.argv[1])
            if os.fork() == 0:
                os.close(1)
                os.close(2)
                pending = marker.with_suffix('.pending')
                pending.write_text(json.dumps({'pgid': os.getpgrp()}))
                pending.replace(marker)
                time.sleep(10)
            else:
                deadline = time.monotonic() + 2
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(.005)
                raise SystemExit(0 if marker.exists() else 2)
        ''')
        try:
            done = smoke.grouped_run([sys.executable, '-B', '-c', source, str(marker)],
                                     capture_output=True, text=True, timeout=3)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertTrue(marker.is_file(), 'the child must have started')
            group = json.loads(marker.read_bytes())['pgid']
            self.assertFalse(smoke._group_alive(group))
        finally:
            if marker.is_file():
                group = json.loads(marker.read_bytes())['pgid']
                self.assertTrue(smoke._kill_group(group), 'fixture-owned child must be gone')

    def test_grouped_run_reaps_success_failure_and_timeout_groups(self):
        for source, expected in (('pass', 0), ('raise SystemExit(7)', 7),
                                 ('import time; time.sleep(10)', None)):
            with self.subTest(source=source):
                groups = []
                real_kill = smoke._kill_group

                def kill(pgid):
                    groups.append(pgid)
                    return real_kill(pgid)

                with mock.patch.object(smoke, '_kill_group', side_effect=kill):
                    if expected is None:
                        with self.assertRaises(subprocess.TimeoutExpired):
                            smoke.grouped_run([sys.executable, '-B', '-c', source], timeout=.5)
                    else:
                        done = smoke.grouped_run([sys.executable, '-B', '-c', source], timeout=3)
                        self.assertEqual(done.returncode, expected)
                self.assertEqual(len(groups), 1)
                self.assertFalse(smoke._group_alive(groups[0]))

    def test_anchor_writes_regular_files_and_refuses_preexisting_links(self):
        base = self.tmp / 'anchored'
        anchor = smoke.Anchor.establish(base, create=True)
        self.addCleanup(anchor.close)
        smoke.safe_mkdir(anchor, base / 'evidence')
        path = base / 'evidence/record'
        real_write = os.write
        with mock.patch.object(smoke.os, 'write', side_effect=lambda fd, raw: real_write(fd, raw[:2])):
            smoke.safe_write(anchor, path, b'complete bytes')
        self.assertEqual(path.read_bytes(), b'complete bytes')
        with mock.patch.object(smoke.os, 'write', return_value=0):
            with self.assertRaisesRegex(OSError, 'no progress'):
                smoke.safe_write(anchor, path, b'bytes')
        victim = self.production / 'preserve'
        victim.write_bytes(b'unchanged')
        path.unlink()
        path.symlink_to(victim)
        with self.assertRaises(smoke.IsolationAbort):
            smoke.safe_write(anchor, path, b'overwrite')
        self.assertEqual(victim.read_bytes(), b'unchanged')


class Callers(Fixture):
    def test_failed_main_arm_returns_one(self):
        host = fixtures.FakeMBP(self, self.clock, main_rc=1)
        runner = self.runner(run=host)
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            self.assertEqual(runner.run(), 1)
        self.assertFalse(host.job_loaded)
        self.assertIsNone(runner.anchor)

    def test_cli_propagates_runner_failure(self):
        from scripts import align_v4_w1_smoke as cli
        packet = self.tmp / 'packet.json'
        packet.write_text('{}')
        argv = ['run', '--measurement-root', str(self.production), '--smoke-dir', str(self.tmp / 'smoke'),
                '--prequal-report', str(self.prequal), '--next-arm-triage', str(packet),
                '--w1-disk-config', str(self.tmp / 'disk'), '--obc-off-attested-by', 'synthetic',
                '--battery-log', str(self.tmp / 'battery')]
        with mock.patch.object(smoke, 'SmokeRunner') as factory, contextlib.redirect_stdout(io.StringIO()):
            factory.return_value.run.return_value = 1
            self.assertEqual(cli.main(argv), 1)
        factory.return_value.run.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
