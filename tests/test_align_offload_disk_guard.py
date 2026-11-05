import importlib.util
from pathlib import Path
import signal
import subprocess
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('guard', Path(__file__).resolve().parents[1] / 'scripts/align_offload_disk_guard.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class GuardTests(unittest.TestCase):
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
                spawn.assert_called_once_with(['writer'], start_new_session=True)
                stop.assert_called_once_with(31415, signal.SIGSTOP)

    def test_poll_is_five_seconds_and_checks_all_filesystems(self):
        child = mock.Mock(pid=31415)
        child.wait.side_effect = [subprocess.TimeoutExpired('writer', 5), 0]
        with mock.patch.object(g, 'free_bytes', return_value=g.FLOOR) as free, mock.patch.object(g.subprocess, 'Popen', return_value=child), mock.patch.object(g.os, 'killpg') as stop:
            self.assertEqual(g.run([Path('/a'), Path('/b')], ['writer']), 0)
            self.assertEqual(free.call_count, 6)
            self.assertEqual(child.wait.call_args_list, [mock.call(timeout=5), mock.call(timeout=5)])
            stop.assert_not_called()
