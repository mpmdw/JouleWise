"""Worker lifecycle failures use fake processes and never import MLX."""
import signal
import unittest
from pathlib import Path
from unittest import mock

from joulewise.align.apple import smc_enumeration as r0


class WorkerTests(unittest.TestCase):
    def test_exiting_group_eperm_is_repolled_and_pipes_close(self):
        load = r0.GpuLoad(5)
        child = mock.Mock(pid=424242)
        child.poll.side_effect = [None, 0]
        load.process = child
        with mock.patch.object(r0.os, "killpg", side_effect=PermissionError("exiting")):
            load.stop()
        child.stdin.close.assert_called_once()
        child.stdout.close.assert_called_once()
        self.assertGreaterEqual(child.poll.call_count, 2)

    def test_readiness_error_remains_primary_if_cleanup_also_fails(self):
        load = r0.GpuLoad(5)
        with mock.patch.object(r0.subprocess, "Popen"), mock.patch("selectors.DefaultSelector") as selector:
            selector.return_value.__enter__.return_value.select.return_value = []
            with mock.patch.object(load, "stop", side_effect=PermissionError("cleanup failed")):
                with self.assertRaisesRegex(RuntimeError, "MLX worker failed readiness") as caught:
                    load.start()
        self.assertIn("cleanup failed", " ".join(caught.exception.__notes__))

    def test_worker_import_has_checkout_cwd_even_from_elsewhere(self):
        load = r0.GpuLoad(5)
        child = mock.Mock()
        child.stdout.readline.return_value = b"READY\n"
        with mock.patch.object(r0.subprocess, "Popen", return_value=child) as launch, mock.patch("selectors.DefaultSelector"):
            load.start()
        self.assertEqual(launch.call_args.kwargs["cwd"], Path(r0.__file__).resolve().parents[3])
        self.assertIn("joulewise.align.apple.smc_enumeration", launch.call_args.args[0][3])

    def test_eperm_on_live_group_falls_back_to_direct_child_signal(self):
        load = r0.GpuLoad(5)
        child = mock.Mock(pid=424242)
        child.poll.return_value = None
        load.process = child
        with mock.patch.object(r0.os, "killpg", side_effect=PermissionError("group")):
            load.stop()
        child.send_signal.assert_called_once_with(signal.SIGTERM)
