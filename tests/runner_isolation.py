"""Keep a test independent of how the test runner was started and of what ran before it.

Test hygiene, 2026-10-07. Three failures were filed as "fails under machine
load, passes alone". Reproduced, the first depends on how the runner was
started, the second on a test that ran earlier in the same process, and the
third on a start-up race that load only widens. The three helpers here remove
those dependencies.

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

3. ``wait_until_child_reports_ready``. ``subprocess.Popen`` returns once the
   child has replaced its program image, but Homebrew's ``python3.13`` is a
   small launcher that immediately replaces itself again with the framework
   binary. ``ps`` reads a process's arguments from its current image, so right
   after the spawn it shows, in turn: the launcher with the arguments; then,
   while the second replacement is in progress, only ``(python3.13)``; then
   the framework binary with the arguments. A test that checks the child's
   command line through ``ps`` within milliseconds of the spawn can land in
   the middle state; a busy machine widens it. Polling ``ps`` until the
   arguments appear is not enough, because they also appear in the first
   state (measured: 7 of 600 polls returned there). The one event that cannot
   precede the final image is the child's own Python code running, so the
   child prints a line and the test waits for it.
"""

from __future__ import annotations

import contextlib
import os
import select
import signal
import subprocess
import sys
import time
from unittest import mock

# The dispositions the installer's shield takes over (its ``SIGNALS``).
SHIELDED_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)

PS_COMMAND_ARGV = ("/bin/ps", "-o", "command=", "-p")

# Code for ``python -c``: print one line as soon as the interpreter runs it, then stay alive.
READY_LINE = b"ready"
READY_SLEEPER = 'import time; print("ready", flush=True); time.sleep(60)'


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


def wait_until_child_reports_ready(process: subprocess.Popen, *, cap_s: float = 60.0) -> float:
    """Wait for the ``ready`` line of a child started from ``READY_SLEEPER``; return the seconds waited.

    The child must have been started with ``stdout=subprocess.PIPE``. The wait
    ends on the event (the line arriving), not on a fixed delay. ``cap_s`` is
    only the point at which a child that never runs its code is called a
    failure: the child is then killed and ``AssertionError`` raised. The same
    happens when the child exits without printing the line. The pipe is closed
    afterwards; the child does not write again.
    """

    started = time.monotonic()
    try:
        readable, _, _ = select.select([process.stdout], [], [], cap_s)
        line = process.stdout.readline() if readable else b""
    finally:
        waited = time.monotonic() - started
    if line.strip() != READY_LINE:
        process.kill()
        process.wait()
        process.stdout.close()
        raise AssertionError(f"child {process.pid} did not report ready within {cap_s} s "
                             f"(waited {waited:.2f} s, read {line!r})")
    process.stdout.close()
    return waited
