"""The helpers of tests/runner_isolation.py, each with the failure it removes shown first.

Every class here pairs a counterfactual (the hazard, injected on purpose, has
the effect the helper's docstring describes) with the cure (the same hazard
under the helper has none). A helper that stopped working would fail the cure;
a hazard that stopped existing would fail the counterfactual and tell the next
reader the helper is no longer needed.
"""

from __future__ import annotations

import contextlib
import multiprocessing
import multiprocessing.resource_tracker
import os
import signal
import subprocess
import sys
import time
import unittest
from unittest import mock

from tests import process_reaper
from tests import runner_isolation

SLEEPER_ARGUMENTS = "-c import time; time.sleep(60)"


@contextlib.contextmanager
def child_stderr_discarded():
    """Send file descriptor 2 to /dev/null for the block, so a child that is meant to die stays quiet.

    The resource tracker (a helper process ``multiprocessing`` starts once and
    keeps) is started first, so that it keeps the real standard error.
    """

    multiprocessing.resource_tracker.ensure_running()
    sys.stderr.flush()
    saved = os.dup(2)
    sink = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(sink, 2)
        yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)
        os.close(sink)


def spawned_child_exit_code() -> int | None:
    """Start one child by "spawn" whose whole job is ``time.sleep(0)``; return its exit code."""

    process = multiprocessing.get_context("spawn").Process(target=time.sleep, args=(0,))
    process.start()
    process.join(120)
    if process.is_alive():
        process.kill()
        process.join(30)
    return process.exitcode


@contextlib.contextmanager
def main_read_from_standard_input():
    """Make the main module look as it does under ``python - < runner.py`` (Python 3.13)."""

    main = sys.modules["__main__"]
    with mock.patch.object(main, "__spec__", None, create=True), \
            mock.patch.object(main, "__file__", "<stdin>", create=True):
        yield main


class SpawnedChildMainModuleTests(unittest.TestCase):
    def test_counterfactual_a_child_dies_re_importing_a_main_module_read_from_standard_input(self):
        with main_read_from_standard_input(), child_stderr_discarded():
            self.assertEqual(spawned_child_exit_code(), 1)

    def test_the_child_runs_when_the_main_module_is_hidden(self):
        with main_read_from_standard_input() as main:
            with runner_isolation.hide_main_from_spawned_children():
                self.assertIsNone(main.__spec__)
                self.assertIsNone(main.__file__)
                self.assertEqual(spawned_child_exit_code(), 0)
            self.assertEqual(main.__file__, "<stdin>", "the helper must put the main module back")

    def test_the_helper_leaves_an_ordinary_main_module_as_it_found_it(self):
        main = sys.modules["__main__"]
        missing = object()
        before = (getattr(main, "__spec__", missing), getattr(main, "__file__", missing))
        with runner_isolation.hide_main_from_spawned_children():
            self.assertEqual(spawned_child_exit_code(), 0)
        self.assertEqual((getattr(main, "__spec__", missing), getattr(main, "__file__", missing)), before)


def child_inherits_ignored_sigterm() -> bool:
    """Start a Python child and ask it whether its SIGTERM arrived already ignored."""

    result = subprocess.run(
        [sys.executable, "-B", "-c", "import signal; print(signal.getsignal(signal.SIGTERM) is signal.SIG_IGN)"],
        capture_output=True, text=True, timeout=120, check=True)
    return result.stdout.strip() == "True"


class SignalDispositionTests(unittest.TestCase):
    def setUp(self):
        # Whatever this class does to the dispositions ends with the test.
        self.enterContext(runner_isolation.signal_dispositions_restored())
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

    def test_counterfactual_an_ignored_sigterm_reaches_every_later_child(self):
        self.assertFalse(child_inherits_ignored_sigterm())
        signal.signal(signal.SIGTERM, signal.SIG_IGN)  # what the installer's shield leaves behind
        self.assertTrue(child_inherits_ignored_sigterm())

    def test_dispositions_changed_inside_the_block_are_put_back(self):
        def handler(_number, _frame):
            return None

        signal.signal(signal.SIGHUP, handler)
        with runner_isolation.signal_dispositions_restored() as before:
            self.assertEqual(set(before), set(runner_isolation.SHIELDED_SIGNALS))
            for number in runner_isolation.SHIELDED_SIGNALS:
                signal.signal(number, signal.SIG_IGN)
            self.assertTrue(child_inherits_ignored_sigterm())
        self.assertIs(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)
        self.assertIs(signal.getsignal(signal.SIGHUP), handler)
        self.assertEqual({number: signal.getsignal(number) for number in before}, before)
        self.assertFalse(child_inherits_ignored_sigterm())

    def test_dispositions_are_put_back_when_the_block_raises(self):
        with self.assertRaises(SystemExit):
            with runner_isolation.signal_dispositions_restored():
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
                raise SystemExit(2)
        self.assertIs(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)


class PsCommandLineWaitTests(unittest.TestCase):
    def sleeper(self) -> subprocess.Popen:
        process = subprocess.Popen([sys.executable, *SLEEPER_ARGUMENTS.split(" ", 1)], start_new_session=True)
        self.addCleanup(process_reaper.kill_and_wait, process)
        return process

    def test_the_wait_ends_when_ps_shows_the_childs_arguments(self):
        process = self.sleeper()
        waited = runner_isolation.wait_until_ps_shows(process.pid, SLEEPER_ARGUMENTS)
        self.assertGreaterEqual(waited, 0.0)
        self.assertIn(SLEEPER_ARGUMENTS, runner_isolation.ps_command(process.pid))
        self.assertIsNone(process.poll(), "waiting must not disturb the child")

    def test_counterfactual_a_child_that_never_shows_the_text_fails_at_the_cap(self):
        process = self.sleeper()
        started = time.monotonic()
        with self.assertRaisesRegex(AssertionError, "ps did not show 'no-such-argument'"):
            runner_isolation.wait_until_ps_shows(process.pid, "no-such-argument", cap_s=0.5)
        self.assertGreaterEqual(time.monotonic() - started, 0.5)

    def test_counterfactual_a_process_that_is_gone_fails_at_the_cap(self):
        process = self.sleeper()
        process_reaper.kill_and_wait(process)
        with self.assertRaisesRegex(AssertionError, "it showed ''"):
            runner_isolation.wait_until_ps_shows(process.pid, SLEEPER_ARGUMENTS, cap_s=0.3)

