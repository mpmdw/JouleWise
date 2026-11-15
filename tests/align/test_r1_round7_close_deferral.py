"""R7-8: real main-thread signals cannot wait indefinitely for a session close."""
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt


CHILD_CASE = 'JOULEWISE_TEST_CLOSE_DEFERRAL'
REPO = Path(__file__).resolve().parents[2]


class CloseDeferralTests(unittest.TestCase):
    def run_child(self, case):
        # The child inherits this test process's priority and temporary
        # JOULEWISE_HOST_STATE_DIR; it runs just one unittest, with no backend.
        child = subprocess.Popen(
            [sys.executable, '-B', '-m', 'unittest',
             'tests.align.test_r1_round7_close_deferral.CloseSignalChild.test_close'],
            cwd=REPO, env=dict(os.environ, **{CHILD_CASE: case}),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            readable, _, _ = select.select([child.stdout], [], [], 10)
            self.assertTrue(readable, 'child did not start its close')
            line = child.stdout.readline().strip()
            if line != 'close-started':
                _stdout, stderr = child.communicate(timeout=10)
                self.fail(f'child did not start its close: {line!r}; {stderr}')
            sent = time.monotonic()
            child.send_signal(signal.SIGTERM)
            # The quick close returns only after this line arrives, so the
            # TERM is always held during the close (round-7 Sol critique F8:
            # a fixed sleep raced the parent's scheduling).
            stdout, stderr = child.communicate(input='signalled\n', timeout=10)
            self.assertEqual(child.returncode, 0, stderr)
            return sent, [json.loads(line) for line in stdout.splitlines()]
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
            child.stdout.close()
            child.stderr.close()

    def test_blocked_close_delivers_term_within_the_bound(self):
        sent, events = self.run_child('blocked')
        self.assertEqual([row['event'] for row in events], ['TERM'])
        self.assertLess(events[0]['at'] - sent, 3.0)

    def test_quick_close_delivers_once_after_close_and_cancels_timer(self):
        _sent, events = self.run_child('quick')
        self.assertEqual([row['event'] for row in events], ['closed', 'after', 'TERM'])


@unittest.skipUnless(os.environ.get(CHILD_CASE), 'subprocess helper')
class CloseSignalChild(unittest.TestCase):
    def test_close(self):
        case = os.environ[CHILD_CASE]
        main_ident = threading.get_ident()
        timers = []
        real_timer = threading.Timer

        def timer_factory(*args, **kwargs):
            timer = real_timer(*args, **kwargs)
            timers.append(timer)
            return timer

        def record(event):
            print(json.dumps({'event': event, 'at': time.monotonic()}), flush=True)

        def handler(signum, _frame):
            self.assertEqual(threading.get_ident(), main_ident)
            self.assertEqual(signum, signal.SIGTERM)
            record('TERM')
            if case == 'blocked':
                raise SystemExit(128 + signum)

        class Managed:
            def close(self):
                print('close-started', flush=True)
                if case == 'blocked':
                    time.sleep(6.0)
                else:
                    sys.stdin.readline()
                record('closed')

        original = signal.signal(signal.SIGTERM, handler)
        try:
            with patch.object(rt, 'CLOSE_SIGNAL_DEFER_MAX_S', 1.0, create=True), \
                    patch.object(rt.threading, 'Timer', side_effect=timer_factory):
                if case == 'blocked':
                    with self.assertRaises(SystemExit):
                        rt.close_managed_session(Managed())
                else:
                    rt.close_managed_session(Managed(), after=lambda: record('after'))
                    # Wait beyond the patched bound to catch a stray timer delivery.
                    time.sleep(1.3)
                    self.assertEqual(len(timers), 1)
                    self.assertTrue(timers[0].daemon)
                    self.assertFalse(timers[0].is_alive())
            self.assertIs(signal.getsignal(signal.SIGTERM), handler)
        finally:
            signal.signal(signal.SIGTERM, original)
