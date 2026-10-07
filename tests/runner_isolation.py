"""Keep a test independent of how the test runner was started and of what ran before it.

Test hygiene, 2026-10-07. Three failures were filed as "fails under machine
load, passes alone". Reproduced, each turned out to depend on the runner or on
an earlier test, not on load. The three helpers here remove those dependencies.

1. ``hide_main_from_spawned_children``. ``multiprocessing`` can start a child
   by "spawn": a fresh interpreter that first re-imports the parent's main
   module (the script Python was started with) and then runs the worker
   function. Spawn is the macOS default. The whole-suite method starts the
   runner in a way the child cannot re-import usefully:

   - fed on standard input (``python - < runner.py``), Python 3.13 sets
     ``__main__.__file__`` to the string ``<stdin>``; the child looks for a
     file of that name, raises ``FileNotFoundError`` and exits with code 1
     before it runs the worker;
   - run as a file with no ``if __name__ == "__main__"`` guard, the child
     re-runs the runner itself, that is, a whole shard of tests, and never
     reports to its parent.

   Under ``python -m unittest`` neither happens (``multiprocessing`` skips a
   main module named ``*.__main__``), which is why these tests passed alone.
   The workers these tests start live in importable modules, so the child
   needs nothing from the main module; the helper hides it for the duration.

2. ``signal_dispositions_restored``. A command-line entry point may end by
   setting signals to "ignore" for the rest of its process: the launchd
   installer (``joulewise.night_agent_install.main``) does this for SIGINT,
   SIGTERM and SIGHUP, which is right for a command about to exit. Called
   inside a test, it leaves the test process ignoring SIGTERM, and an ignored
   signal is inherited by every child process started afterwards (unlike a
   Python handler, which a new program image resets to the default action).
   A later test's child then survives the SIGTERM that test relies on. The
   helper puts the dispositions back when its block ends.

3. ``wait_until_ps_shows``. ``subprocess.Popen`` returns once the child has
   replaced its program image, but Homebrew's ``python3.13`` is a small
   launcher that immediately replaces itself again with the framework binary.
   While that second replacement is in progress ``ps`` cannot read the
   process's arguments and prints only ``(python3.13)``. A test that checks
   the child's command line through ``ps`` within milliseconds of the spawn
   can land in that gap; a busy machine widens it. The helper waits for the
   command line to be readable.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import time
from unittest import mock

# The dispositions the installer's shield takes over (its ``SIGNALS``).
SHIELDED_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)

PS_COMMAND_ARGV = ("/bin/ps", "-o", "command=", "-p")


@contextlib.contextmanager
def hide_main_from_spawned_children():
    """While the block runs, a spawned ``multiprocessing`` child skips the main module.

    ``multiprocessing.spawn.get_preparation_data`` tells the child to re-import
    the main module by ``__main__.__spec__.name`` when that is set, otherwise
    by ``__main__.__file__``. With both ``None`` it sends neither instruction
    and the child goes straight to unpickling the worker.

    Do not use it around a spawn whose worker function or ``Process`` subclass
    is defined in the main module itself (a test file run as a script): that
    child needs the main module to find them.
    """

    main = sys.modules["__main__"]
    with mock.patch.object(main, "__spec__", None, create=True), \
            mock.patch.object(main, "__file__", None, create=True):
        yield


@contextlib.contextmanager
def signal_dispositions_restored(signals=SHIELDED_SIGNALS):
    """Put each listed signal's disposition back as it was when the block began.

    Use it around a command-line entry point called in the test process. A
    disposition Python cannot read back (``signal.getsignal`` returns ``None``
    for a handler installed outside Python) is left alone.
    """

    saved = {number: signal.getsignal(number) for number in signals}
    try:
        yield saved
    finally:
        for number, handler in saved.items():
            if handler is not None and signal.getsignal(number) is not handler:
                signal.signal(number, handler)


def ps_command(pid: int) -> str:
    """The command line ``ps`` shows for ``pid`` now; empty when there is no such process."""

    try:
        result = subprocess.run([*PS_COMMAND_ARGV, str(pid)], capture_output=True, text=True, timeout=30,
                                check=False, env={**os.environ, "LC_ALL": "C", "LANG": "C"})
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def wait_until_ps_shows(pid: int, text: str, *, cap_s: float = 30.0, poll_s: float = 0.01) -> float:
    """Wait until ``ps`` shows ``text`` in the command line of ``pid``; return the seconds waited.

    The wait ends on the event, not on a fixed delay. ``cap_s`` is only the
    point at which a child that never shows its arguments is called a failure:
    ``AssertionError`` then names what ``ps`` showed last.
    """

    started = time.monotonic()
    while True:
        shown = ps_command(pid)
        waited = time.monotonic() - started
        if text in shown:
            return waited
        if waited >= cap_s:
            raise AssertionError(f"ps did not show {text!r} for pid {pid} within {cap_s} s; it showed {shown!r}")
        time.sleep(poll_s)
