"""Stop the child processes a test starts, and fail a test that leaves one running.

Why this exists (test hygiene, 2026-10-07). A measurement window is 27 hours of
collection, and before it starts the machine is checked for other processes
using the CPU. A child process that a test run left behind is such a process:
on 2026-10-06, 46 of them were found and killed by hand. This module gives the
tests one way to stop their children on every way out of a test, and one check
that turns a child left running into a test failure instead of a surprise found
days later.

Words used below, built from what the operating system does:

* A *child* is a process this test process started. A *descendant* is a child,
  or a child of a descendant. The system records, for each process, the id of
  its parent; following those parent ids upward from a process reaches this
  test process exactly when it is a descendant.
* A process is *running* until it exits. After it exits, the system keeps a
  one-line record of it (a "zombie", state ``Z`` in ``ps``) until its parent
  collects the exit status. A zombie uses no CPU, so it is not counted here.
* A *process group* is a set of processes that one ``kill`` call can signal
  together. A child started with ``start_new_session=True`` (or
  ``process_group=0``) *leads* a new group whose id equals the child's own
  process id; processes it then starts join that group. When the leader exits,
  the members stay alive and their parent becomes process 1, so the parent ids
  no longer lead back here. They are found through the group id instead.

The three parts:

``own(test, process)``
    Call it on the line after a test starts a child. It registers
    ``stop(process)`` as a cleanup of the test, so the child is stopped when
    the test passes, fails, or raises (a timed-out wait raises). ``stop`` sends
    SIGTERM, waits ``grace_s`` seconds for the exit, then sends SIGKILL and
    waits again; when the child leads a process group, both signals go to the
    whole group, and members still alive after the leader has exited are
    stopped the same way.

``fails_on_leftover_children``
    A class decorator. After each test's own cleanups it looks at every child
    the test started through ``subprocess.Popen``: one still running, or one
    whose process group still has members, is stopped, and the test is reported
    as an error that names the test, the process id and the command line. After
    the class's last cleanup it lists every process on the machine once
    (``ps``) and does the same for any running descendant of this process that
    did not exist when the class began; that covers children started by other
    means (``multiprocessing``, ``os.fork``, a child of a child).

The exit sweep
    unittest does not run a test's cleanups when the run is interrupted with
    Ctrl-C (KeyboardInterrupt): measured on Python 3.13.1, 2026-10-07, a child
    registered with ``addCleanup(child.kill)`` was still alive after the
    interrupted run exited. So importing this module registers an ``atexit``
    function that stops every child registered with ``own`` and every running
    descendant when the interpreter exits. It cannot run when the test process
    itself is killed by a signal it does not handle (SIGTERM, SIGKILL).

Not covered, by construction: a process that left this process's family (its
parent exited, so its parent id is 1) and is not in a group led by a child
started through ``subprocess.Popen``. The block-5 driver tests cover their own
such processes by name with ``tests/process_reaper.py``.
"""

from __future__ import annotations

import atexit
import contextlib
import dataclasses
import functools
import os
import signal
import subprocess
import sys
import threading
import time
import weakref
from typing import Iterable, Iterator

# The real system calls, taken at import. Tests replace ``time.sleep``, ``time.monotonic`` or
# ``os.kill`` with fakes (some for a whole class); the checks below must not run on a fake clock
# or signal through a fake ``kill``.
_monotonic, _sleep = time.monotonic, time.sleep
_kill, _killpg, _getpgid, _waitpid, _getpid = os.kill, os.killpg, os.getpgid, os.waitpid, os.getpid

PS_ARGV = ("/bin/ps", "-A", "-ww", "-o", "pid=,ppid=,pgid=,uid=,stat=,etime=,command=")
PS_TIMEOUT_S = 20.0
DEFAULT_GRACE_S = 2.0   # stop(): seconds between SIGTERM and SIGKILL
KILL_WAIT_S = 5.0       # stop(): seconds to wait for the exit after SIGKILL
SETTLE_S = 3.0          # the checks: seconds a child may take to finish exiting before it counts as left behind


class ProcessTableUnavailable(RuntimeError):
    """``ps`` could not be run or printed nothing (some sandboxes deny it)."""


@dataclasses.dataclass(frozen=True)
class Row:
    """One line of ``ps``: a process, its parent, its group, and its command line."""

    pid: int
    ppid: int
    pgid: int
    uid: int
    stat: str
    elapsed_s: float | None
    command: str

    @property
    def zombie(self) -> bool:
        return self.stat.startswith("Z")

    def describe(self) -> str:
        age = "?" if self.elapsed_s is None else f"{self.elapsed_s:.0f}"
        return f"pid {self.pid} (parent {self.ppid}, group {self.pgid}, running {age} s): {self.command[:300]}"


def _elapsed_s(text: str) -> float | None:
    """``ps`` etime, written [[days-]hours:]minutes:seconds, in seconds."""

    try:
        days, _, clock = text.rpartition("-")
        parts = [int(part) for part in clock.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        return int(days or 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]
    except ValueError:
        return None


def table() -> list[Row]:
    """Every process on the machine, except the ``ps`` that produced the list."""

    try:
        lister = _POPEN(PS_ARGV, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                        env={**os.environ, "LC_ALL": "C"})
    except OSError as error:
        raise ProcessTableUnavailable(f"cannot start ps: {error}") from error
    try:
        raw, _ = lister.communicate(timeout=PS_TIMEOUT_S)
    except subprocess.TimeoutExpired as error:
        lister.kill()
        lister.communicate()
        raise ProcessTableUnavailable(f"ps gave no answer in {PS_TIMEOUT_S:.0f} s") from error
    rows = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        fields = line.split(None, 6)
        if len(fields) < 6:
            continue
        try:
            pid, ppid, pgid, uid = (int(field) for field in fields[:4])
        except ValueError:
            continue
        if pid != lister.pid:
            rows.append(Row(pid, ppid, pgid, uid, fields[4], _elapsed_s(fields[5]),
                            fields[6] if len(fields) > 6 else ""))
    if lister.returncode != 0 or not rows:
        raise ProcessTableUnavailable(f"ps exited {lister.returncode} with {len(rows)} readable lines")
    return rows


def descendants(rows: Iterable[Row], root: int) -> list[Row]:
    """The rows whose chain of parent ids reaches ``root`` (``root`` itself excluded)."""

    children: dict[int, list[Row]] = {}
    for row in rows:
        children.setdefault(row.ppid, []).append(row)
    found, queue, seen = [], [root], {root}
    while queue:
        for row in children.get(queue.pop(), ()):
            if row.pid not in seen:
                seen.add(row.pid)
                found.append(row)
                queue.append(row.pid)
    return found


def _standing_helpers() -> set[int]:
    """Children the standard library keeps until this process exits.

    ``multiprocessing`` starts one resource tracker (and, when asked, one fork
    server) per process and never stops it; each exits by itself when this
    process does, because the pipe it reads from closes.
    """

    pids = set()
    for module, holder, field in (("multiprocessing.resource_tracker", "_resource_tracker", "_pid"),
                                  ("multiprocessing.forkserver", "_forkserver", "_forkserver_pid")):
        pid = getattr(getattr(sys.modules.get(module), holder, None), field, None)
        if isinstance(pid, int):
            pids.add(pid)
    return pids


def running_descendants(*, known: Iterable[int] = ()) -> list[Row]:
    """Running descendants of this process, without ``known`` pids and the standing helpers."""

    skip = set(known) | _standing_helpers()
    return [row for row in descendants(table(), _getpid()) if row.pid not in skip and not row.zombie]


# --------------------------------------------------------------------------
# Stopping one child


def _signal(pid: int, number: int, group: bool) -> None:
    try:
        if group:
            _killpg(pid, number)
        else:
            _kill(pid, number)
    except (ProcessLookupError, PermissionError):
        pass


def _process_exists(pid: int) -> bool:
    """True until the process has exited and its exit status has been collected."""

    try:
        _kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _group_has_member(pgid: int) -> bool:
    """True while the process group has a member that can be signalled.

    Signal 0 delivers nothing; the call only reports whether delivery would
    work. No such group: ProcessLookupError. A group holding only zombies:
    PermissionError on macOS (measured 2026-10-07, macOS 26.6), and both mean
    nothing in the group is running.
    """

    try:
        _killpg(pgid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _leads_group(pid: int) -> bool:
    """Whether a child whose exit status has not been collected yet leads a process group.

    Until the status is collected the system keeps the child's process id, so
    a group with that id is the child's own. A running leader answers
    ``getpgid`` with its own id. A leader that has exited but is not collected
    answers "no such process" on macOS; then the group itself is asked, and it
    answers only if a member is still running.
    """

    try:
        if _getpgid(pid) == pid:
            return True
    except (ProcessLookupError, PermissionError):
        pass
    return _group_has_member(pid)


def _wait(process, timeout_s: float) -> bool:
    try:
        process.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return False
    return True


def _wait_until(gone, timeout_s: float) -> bool:
    deadline = _monotonic() + timeout_s
    while not gone():
        if _monotonic() >= deadline:
            return False
        _sleep(0.02)
    return True


def _stop_group(pgid: int, grace_s: float) -> None:
    """Terminate, wait, then kill what remains of a group whose leader has exited.

    The system does not give a group id to a new group while the old group
    still has a member, so a group found here is the one the leader created.
    """

    if not _group_has_member(pgid):
        return
    _signal(pgid, signal.SIGTERM, True)
    if not _wait_until(lambda: not _group_has_member(pgid), grace_s):
        _signal(pgid, signal.SIGKILL, True)
        _wait_until(lambda: not _group_has_member(pgid), KILL_WAIT_S)


@dataclasses.dataclass
class _Owned:
    process: subprocess.Popen
    leads_group: bool
    grace_s: float
    tree: bool


_LOCK = threading.Lock()
_OWNED: dict[int, _Owned] = {}
_HOME_PID = _getpid()


def stop(process, *, grace_s: float | None = None, tree: bool | None = None) -> None:
    """Terminate, wait, then kill one child, and the process group it leads.

    ``process`` is a ``subprocess.Popen``. Safe to call twice, and on a child
    that has already exited: then only what remains of a group it led is
    stopped (known when the child was registered with ``own``, or when this
    call is the one that collects its exit status).

    ``tree=True`` is for a child that starts processes of its own without
    leading a group: they would outlive it with parent 1 and no group to find
    them by. The child's descendants are listed (one ``ps``) before it is
    signalled, and stopped after it.
    """

    with _LOCK:
        entry = _OWNED.pop(id(process), None)
    leads = entry.leads_group if entry is not None else False
    if grace_s is None:
        grace_s = entry.grace_s if entry is not None else DEFAULT_GRACE_S
    if tree is None:
        tree = entry.tree if entry is not None else False
    pid = process.pid
    if process.returncode is None:
        # Not yet collected, so the process id (and the id of a group it leads) is still its own.
        leads = leads or _leads_group(pid)
        below = []
        if tree:
            with contextlib.suppress(ProcessTableUnavailable):
                below = [row for row in descendants(table(), pid) if not row.zombie]
        _signal(pid, signal.SIGTERM, leads)
        if not _wait(process, grace_s):
            _signal(pid, signal.SIGKILL, leads)
            _wait(process, KILL_WAIT_S)
        if below:
            stop_rows(below, grace_s=grace_s)
    if leads:
        _stop_group(pid, grace_s)


def own(test, process, *, grace_s: float = DEFAULT_GRACE_S, tree: bool = False):
    """Have ``process`` stopped when ``test`` ends, however it ends; returns ``process``.

    Call it on the line after the child is started. ``test`` is a
    ``unittest.TestCase`` instance (the child is stopped among the test's
    cleanups), a ``TestCase`` class (among the class cleanups), or None (only
    an explicit ``stop`` and the exit sweep apply). ``grace_s`` and ``tree``
    are passed to ``stop``.
    """

    entry = _Owned(process, process.returncode is None and _leads_group(process.pid), grace_s, tree)
    with _LOCK:
        _OWNED[id(process)] = entry
    if test is not None:
        register = test.addClassCleanup if isinstance(test, type) else test.addCleanup
        register(stop, process)
    return process


@contextlib.contextmanager
def owned(process, *, grace_s: float = DEFAULT_GRACE_S, tree: bool = False) -> Iterator:
    """``with owned(Popen(...)) as child:`` stops the child on every way out of the block."""

    own(None, process, grace_s=grace_s, tree=tree)
    try:
        yield process
    finally:
        stop(process)


def stop_rows(rows: Iterable[Row], *, grace_s: float = DEFAULT_GRACE_S) -> None:
    """Terminate, wait, then kill the listed processes (a whole group where a row leads one)."""

    own_group = _getpgid(0)
    targets = [(row.pid, row.pgid == row.pid and row.pgid != own_group) for row in rows]

    def gone(pid: int) -> bool:
        with contextlib.suppress(ChildProcessError, OSError):
            _waitpid(pid, os.WNOHANG)   # collects the exit status when the process is our own child
        return not _process_exists(pid)

    for pid, group in targets:
        _signal(pid, signal.SIGTERM, group)
    deadline = _monotonic() + grace_s
    for pid, group in targets:
        if not _wait_until(lambda: gone(pid), max(0.0, deadline - _monotonic())):
            _signal(pid, signal.SIGKILL, group)
    deadline = _monotonic() + KILL_WAIT_S
    for pid, _group in targets:
        _wait_until(lambda: gone(pid), max(0.0, deadline - _monotonic()))


def _exit_sweep() -> None:
    """At interpreter exit: stop every owned child, then every running descendant."""

    if _getpid() != _HOME_PID:
        return   # a forked copy of the test process owns nothing
    with _LOCK:
        entries = list(_OWNED.values())
    for entry in entries:
        with contextlib.suppress(Exception):
            stop(entry.process)
    with contextlib.suppress(Exception):
        stop_rows(running_descendants())


atexit.register(_exit_sweep)


# --------------------------------------------------------------------------
# The check: children started through subprocess.Popen are recorded as they start


@dataclasses.dataclass
class Spawn:
    """One child started through ``subprocess.Popen`` while a recorder was open."""

    pid: int
    leads_group: bool
    args: str
    reference: "weakref.ReferenceType"

    def process(self):
        """The Popen object, also when the test dropped it while the child still ran."""

        process = self.reference()
        if process is None:
            # subprocess parks a dropped Popen whose child is still running in this list.
            for parked in list(getattr(subprocess, "_active", None) or ()):
                if parked.pid == self.pid:
                    return parked
        return process

    def running(self) -> bool:
        process = self.process()
        return process is not None and process.poll() is None

    def group_remains(self) -> bool:
        return self.leads_group and not self.running() and _group_has_member(self.pid)

    def describe(self) -> str:
        what = "is still running" if self.running() else "has exited, but the process group it led still has members"
        return f"pid {self.pid} {what}: {self.args[:300]}"


_RECORDERS: list[list[Spawn]] = []
# The class itself, taken at import. Production code swaps the name ``subprocess.Popen`` for a
# function while a sampler starts (joulewise/sampler_teardown.py), and tests replace it with
# mocks; the recorder must never be installed on one of those.
_POPEN = subprocess.Popen
_POPEN_INIT = _POPEN.__init__
_INSTALLED = False


@functools.wraps(_POPEN_INIT)
def _recording_init(self, *args, **kwargs):
    _POPEN_INIT(self, *args, **kwargs)
    if _RECORDERS and _getpid() == _HOME_PID:
        leads = bool(kwargs.get("start_new_session")) or kwargs.get("process_group") == 0 or _leads_group(self.pid)
        # The innermost open recorder takes it: a test's own, else the class's.
        _RECORDERS[-1].append(Spawn(self.pid, leads, repr(self.args), weakref.ref(self)))


def start_recording() -> list[Spawn]:
    """Open a recorder: the returned list gains one ``Spawn`` per child started from now on."""

    global _INSTALLED
    if not _INSTALLED:
        # Once, and never again: a test that wraps Popen.__init__ for its own purpose wraps this
        # function and puts it back afterwards; installing a second time would undo its wrapper.
        _POPEN.__init__ = _recording_init
        _INSTALLED = True
    spawns: list[Spawn] = []
    _RECORDERS.append(spawns)
    return spawns


def stop_recording(spawns: list[Spawn]) -> None:
    """Close a recorder (a second call does nothing)."""

    for index, recorder in enumerate(_RECORDERS):
        if recorder is spawns:
            del _RECORDERS[index]
            return


def left_spawns(spawns: Iterable[Spawn], settle_s: float = SETTLE_S) -> list[Spawn]:
    """The recorded children still running, or whose group still has members, after ``settle_s``."""

    spawns = list(spawns)
    deadline = _monotonic() + settle_s
    while True:
        left = [spawn for spawn in spawns if spawn.running() or spawn.group_remains()]
        if not left or _monotonic() >= deadline:
            return left
        _sleep(0.05)


def left_descendants(known: Iterable[int], settle_s: float = SETTLE_S) -> list[Row]:
    """Running descendants of this process that are not in ``known``, after ``settle_s``."""

    known = set(known)
    deadline = _monotonic() + settle_s
    left = running_descendants(known=known)
    while left and _monotonic() < deadline:
        _sleep(0.1)
        left = running_descendants(known=known)
    return left


def stop_spawn(spawn: Spawn) -> None:
    """Stop a recorded child, the processes it started, and what remains of a group it led."""

    process = spawn.process()
    if process is not None and process.returncode is None:
        stop(process, tree=True)
    if spawn.leads_group:
        _stop_group(spawn.pid, DEFAULT_GRACE_S)


class LeftoverChildren(AssertionError):
    """A test or a test class ended with a child process still running."""


def check_spawns(label: str, spawns: Iterable[Spawn], *, settle_s: float = SETTLE_S) -> None:
    """Stop and report the recorded children that outlived ``label``."""

    left = left_spawns(spawns, settle_s)
    if not left:
        return
    lines = [spawn.describe() for spawn in left]
    for spawn in left:
        stop_spawn(spawn)
    raise LeftoverChildren(
        f"{label} left {len(left)} child process(es) behind; they have now been stopped. "
        "Stop each one in a cleanup, with tests.child_guard.own(self, process):\n  " + "\n  ".join(lines))


def check_descendants(label: str, known: Iterable[int], *, settle_s: float = SETTLE_S) -> None:
    """Stop and report running descendants of this process that are not in ``known``."""

    try:
        left = left_descendants(known, settle_s)
    except ProcessTableUnavailable:
        return   # no process list here (a sandbox that denies ps); the per-test check has still run
    if not left:
        return
    lines = [row.describe() for row in left]
    stop_rows(left)
    raise LeftoverChildren(
        f"{label} left {len(left)} descendant process(es) running after its last cleanup; they have now "
        "been stopped. Find the test that starts each one and stop it in a cleanup, with "
        "tests.child_guard.own(self, process):\n  " + "\n  ".join(lines))


_GUARDED_CLASSES: set[type] = set()   # classes whose class-level check is pending


def fails_on_leftover_children(cls=None, *, settle_s: float = SETTLE_S):
    """Class decorator: a test, or the class, that leaves a child running is reported as failed.

    ``settle_s`` is how long a child that is already on its way out may take to
    finish exiting before it counts as left behind. Decorating a class and also
    a class it inherits from checks each test and each class once, not twice.
    """

    def decorate(klass):
        class_setup = klass.setUpClass.__func__
        test_run = klass.run

        @classmethod
        def setUpClass(inner):   # noqa: N802 (unittest hook)
            if inner in _GUARDED_CLASSES:   # an outer decoration already watches this class
                return class_setup(inner)
            label = f"{inner.__module__}.{inner.__qualname__}"
            try:
                known = {row.pid for row in running_descendants()}
            except ProcessTableUnavailable:
                known = None
            spawns = start_recording()
            _GUARDED_CLASSES.add(inner)

            def after_class():
                _GUARDED_CLASSES.discard(inner)
                stop_recording(spawns)
                problems = []
                for check in ((lambda: check_spawns(f"The class fixtures of {label}", spawns, settle_s=settle_s)),
                              (lambda: known is None or check_descendants(label, known, settle_s=settle_s))):
                    try:
                        check()
                    except LeftoverChildren as problem:
                        problems.append(str(problem))
                if problems:
                    raise LeftoverChildren("\n".join(problems))

            # Registered first, so it runs after every cleanup the class itself registers.
            inner.addClassCleanup(after_class)
            class_setup(inner)

        @functools.wraps(test_run)
        def run(self, result=None):
            if getattr(self, "_child_guard_watching", False):   # an outer decoration already watches this test
                return test_run(self, result)
            self._child_guard_watching = True
            spawns = start_recording()

            def after_test():
                stop_recording(spawns)
                check_spawns(self.id(), spawns, settle_s=settle_s)

            # Registered before the test's own setUp, so it runs after every cleanup the test registers.
            self.addCleanup(after_test)
            try:
                return test_run(self, result)
            finally:
                stop_recording(spawns)   # a skipped test runs no cleanups
                self._child_guard_watching = False

        klass.setUpClass = setUpClass
        klass.run = run
        return klass

    return decorate(cls) if cls is not None else decorate


def guard_test_classes(namespace: dict, *, settle_s: float = SETTLE_S) -> list[type]:
    """Apply ``fails_on_leftover_children`` to every test class a module defines.

    Call it once at the bottom of a test module, as
    ``child_guard.guard_test_classes(globals())``. Classes the module only
    imported from elsewhere are left to their own module. Returns the classes
    it decorated.
    """

    import unittest

    module = namespace.get("__name__")
    decorated = []
    for value in list(namespace.values()):
        if isinstance(value, type) and issubclass(value, unittest.TestCase) and value.__module__ == module:
            decorated.append(fails_on_leftover_children(value, settle_s=settle_s))
    return decorated
