import importlib.util
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('guard', Path(__file__).resolve().parents[1] / 'scripts/align_offload_disk_guard.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.device = mock.patch.object(g, 'device_id', return_value=123).start()
        # Mock supervisors do not hold the real pipe read end. Keep heartbeat
        # writes synthetic so unit checks reach their intended failure sites.
        mock.patch.object(g.os, 'write', return_value=1).start()
        self.addCleanup(mock.patch.stopall)

    def test_low_initial_space_never_starts_writer(self):
        with mock.patch.object(g, 'free_bytes', return_value=g.FLOOR - 1), mock.patch.object(g.subprocess, 'Popen') as spawn:
            with self.assertRaises(RuntimeError):
                g.run([Path('/synthetic')], ['writer'])
            spawn.assert_not_called()

    def test_low_or_unknown_space_stops_entire_new_group(self):
        for failure in (g.FLOOR - 1, OSError('unmounted')):
            child = mock.Mock(pid=31415)
            child.poll.return_value = None
            with mock.patch.object(g, 'free_bytes', side_effect=[g.FLOOR, failure]), mock.patch.object(g.subprocess, 'Popen', return_value=child) as spawn, mock.patch.object(g.os, 'killpg') as stop:
                self.assertEqual(g.run([Path('/synthetic')], ['writer']), 75)
                self.assertTrue(spawn.call_args.kwargs['start_new_session'])
                self.assertEqual(len(spawn.call_args.kwargs['pass_fds']), 1)
                self.assertEqual(spawn.call_args.args[0][-2:], ['--', 'writer'])
                stop.assert_called_once_with(31415, signal.SIGSTOP)

    def test_unmount_stops_writer_before_bare_mountpoint_write(self):
        child = mock.Mock(pid=31415)
        child.poll.return_value = None
        self.device.side_effect = [123, 123, 999]
        with mock.patch.object(g, 'free_bytes', return_value=g.FLOOR), mock.patch.object(g.subprocess, 'Popen', return_value=child), mock.patch.object(g.os, 'killpg') as stop:
            self.assertEqual(g.run([Path('/synthetic')], ['writer']), 75)
            stop.assert_called_once_with(31415, signal.SIGSTOP)

    def test_poll_is_five_seconds_and_checks_all_filesystems(self):
        child = mock.Mock(pid=31415)
        child.wait.side_effect = [subprocess.TimeoutExpired('writer', 5), 0]
        with mock.patch.object(g, 'free_bytes', return_value=g.FLOOR) as free, mock.patch.object(g.subprocess, 'Popen', return_value=child), mock.patch.object(g.os, 'killpg') as stop, mock.patch.object(g.os, 'write'):
            self.assertEqual(g.run([Path('/a'), Path('/b')], ['writer']), 0)
            self.assertEqual(free.call_count, 6)
            self.assertEqual(child.wait.call_args_list, [mock.call(timeout=5), mock.call(timeout=5)])
            stop.assert_not_called()

    def test_dead_supervisor_still_stops_surviving_group(self):
        child = mock.Mock(pid=31415)
        child.poll.return_value = -9
        child.wait.return_value = -9
        with mock.patch.object(g, 'free_bytes', return_value=g.FLOOR), \
             mock.patch.object(g.subprocess, 'Popen', return_value=child), \
             mock.patch.object(g.os, 'killpg') as stop:
            self.assertEqual(g.run([Path('/synthetic')], ['writer']), -9)
            stop.assert_called_once_with(31415, signal.SIGSTOP)

    def test_guard_death_stops_real_writer_for_hup_and_kill(self):
        # Only synthetic temp paths and lightweight Python sleepers, no data.
        for sig in (signal.SIGHUP, signal.SIGKILL):
            with self.subTest(signal=sig), tempfile.TemporaryDirectory() as d:
                root = Path(d).resolve()
                pidfile = root / 'writer.pid'
                ticks = root / 'ticks'
                writer = ('import os,time; from pathlib import Path; '
                          f'Path({str(pidfile)!r}).write_text(str(os.getpid())); '
                          f'f=open({str(ticks)!r}, "ab", buffering=0)\n'
                          'while True:\n f.write(b"."); time.sleep(0.02)')
                launch = (f'import runpy; g=runpy.run_path({g.__file__!r}); '
                          "g['run'].__globals__['FLOOR']=0; "
                          f"raise SystemExit(g['run']([__import__('pathlib').Path({str(root)!r})], "
                          f"[{sys.executable!r}, '-I', '-B', '-c', {writer!r}]))")
                guard = subprocess.Popen([sys.executable, '-I', '-B', '-c', launch],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         text=True)
                pgid = None
                try:
                    self.assertTrue(select.select([guard.stdout], [], [], 5)[0])
                    pgid = int(guard.stdout.readline().strip().split('=')[1])
                    deadline = time.monotonic() + 5
                    while (not ticks.exists() or ticks.stat().st_size < 3) and time.monotonic() < deadline:
                        time.sleep(0.02)
                    self.assertTrue(pidfile.exists(), 'writer did not start')
                    writer_pid = int(pidfile.read_text())
                    os.kill(guard.pid, sig)
                    guard.wait(timeout=5)
                    deadline = time.monotonic() + 5
                    stopped = False
                    while time.monotonic() < deadline:
                        count = ticks.stat().st_size
                        time.sleep(0.3)
                        os.kill(writer_pid, 0)  # alive, not terminated
                        if count == ticks.stat().st_size:
                            stopped = True
                            break
                    self.assertTrue(stopped, 'live writer kept executing after guard death')
                finally:
                    if pgid is not None:
                        try:
                            os.killpg(pgid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    if guard.poll() is None:
                        guard.kill()
                    guard.wait(timeout=5)
                    guard.stdout.close()
                    guard.stderr.close()

    def test_stale_heartbeat_stops_wrapper_group(self):
        with mock.patch.object(g.os, 'read', return_value=b'.'), \
             mock.patch.object(g.subprocess, 'Popen') as spawn, \
             mock.patch.object(g.select, 'select', return_value=([], [], [])), \
             mock.patch.object(g.time, 'monotonic', side_effect=[0, 16]), \
             mock.patch.object(g.signal, 'signal'), \
             mock.patch.object(g.os, 'killpg', side_effect=SystemExit) as stop:
            spawn.return_value.poll.return_value = None
            with self.assertRaises(SystemExit):
                g.writer_wrapper(123, ['writer'])
            self.assertEqual(stop.call_args, mock.call(os.getpgrp(), signal.SIGSTOP))
