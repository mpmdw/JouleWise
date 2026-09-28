"""Test-side fence that refuses any real ``sudo`` or ``powermetrics`` start.

Why this exists.  The real sampler is started as ``sudo -n /usr/bin/powermetrics
...`` (``joulewise/adapters/powermetrics.py``: ``POWER_METRICS`` and the default
``privilege_prefix=("sudo", "-n")``).  Any test that reaches a production path
building the adapter from its defaults -- for example the campaign cooldown gate,
``scripts/run_campaign.py`` ``campaign_cooldown_before_member``, which calls
``joulewise.adapters.resolve_telemetry`` with a real ``SystemClock`` whenever the
preceding member's config names the ``powermetrics`` backend -- starts the real
sampler on the test host.  The production code catches the resulting failure
broadly and records the cooldown as ``unknown``, so such a test still passes and
the leak is silent.  This happened on 2026-09-28 (activation d528efb2, record
item 124): whole-module runs started repeated ``sudo -n /usr/bin/powermetrics
-n 2 -i 500`` captures.

What the fence does while it is held.

1. In this process it wraps ``subprocess.Popen.__init__`` (which covers
   ``subprocess.run``/``call``/``check_output`` and ``os.popen``), the
   ``os.exec*``, ``os.spawn*`` and ``os.posix_spawn*`` functions and
   ``os.system``.  An argv is refused when any of its shell-split tokens has the
   base name ``sudo`` or ``powermetrics``.  Refusal raises
   ``SamplerLaunchRefused`` before any process exists.  A token that merely
   contains the text (``fake_powermetrics_process.py``, a ``pgrep`` pattern) is
   not refused, so the repository's fake-sampler fixtures keep working.
2. For child processes, which do not inherit the in-process wrapper, it puts a
   directory at the front of ``PATH`` holding stand-in ``sudo`` and
   ``powermetrics`` programs.  Each stand-in appends a line to a log and exits
   with status 1.  The adapter names ``sudo`` without a path, so a child that
   builds the adapter from its defaults resolves ``sudo`` to the stand-in.
3. Every refusal and every stand-in start is recorded with the running test id.
   When the fence is released, any record not yet reported raises
   ``AssertionError``, so a refused launch that production code swallowed still
   fails the run loudly (as a module fixture error) instead of passing silently.

Use in a test module::

    from tests.sampler_launch_fence import fenced_load_tests, install_module_fence

    load_tests = fenced_load_tests   # whole-module runs, including imported classes

    def setUpModule():
        install_module_fence()       # runs that load single test ids
"""

from __future__ import annotations

import inspect
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


FENCED_PROGRAMS = frozenset({"sudo", "powermetrics"})

_POSITIONAL_ARGV = {
    # name: (index of the program path, index of the argv sequence)
    "execv": (0, 1),
    "execve": (0, 1),
    "execvp": (0, 1),
    "execvpe": (0, 1),
    "posix_spawn": (0, 1),
    "posix_spawnp": (0, 1),
    "spawnv": (1, 2),
    "spawnve": (1, 2),
    "spawnvp": (1, 2),
    "spawnvpe": (1, 2),
}

_STAND_IN = """#!/bin/sh
printf '%s\\t%s\\t%s\\n' "{name}" "${{JOULEWISE_FENCE_TEST_ID:-}}" "$*" >> "{log}"
echo "sampler launch fence: stand-in {name} refused (test-side fence)" >&2
exit 1
"""


class SamplerLaunchRefused(PermissionError):
    """Raised in place of starting ``sudo`` or ``powermetrics`` under the fence."""


def fenced_program(args, executable=None) -> str | None:
    """Return the first fenced token of a launch request, or ``None``."""

    if isinstance(args, (str, bytes, os.PathLike)):
        items = [os.fsdecode(args)]
    else:
        try:
            items = [
                os.fsdecode(item) if isinstance(item, (bytes, os.PathLike)) else str(item)
                for item in args
            ]
        except TypeError:
            items = [str(args)]
    if executable is not None:
        items.insert(0, os.fsdecode(executable))
    for item in items:
        try:
            tokens = shlex.split(item)
        except ValueError:
            tokens = item.split()
        for token in tokens:
            if os.path.basename(token) in FENCED_PROGRAMS:
                return token
    return None


def _running_test_id() -> str | None:
    frame = inspect.currentframe()
    try:
        while frame is not None:
            candidate = frame.f_locals.get("self")
            if isinstance(candidate, unittest.TestCase):
                return candidate.id()
            frame = frame.f_back
    finally:
        del frame
    return None


class _Fence:
    """Process-wide fence with nested acquisition (one install, many holders)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._depth = 0
        self._originals: dict[str, object] = {}
        self._shim_dir: Path | None = None
        self._shim_log: Path | None = None
        self._shim_lines_reported = 0
        self._unreported: list[str] = []

    @property
    def installed(self) -> bool:
        return self._depth > 0

    @property
    def shim_dir(self) -> Path | None:
        return self._shim_dir

    def acquire(self) -> None:
        with self._lock:
            if self._depth == 0:
                self._install()
            self._depth += 1

    def release(self) -> None:
        """Drop one hold; raise ``AssertionError`` for unreported refusals."""

        with self._lock:
            if self._depth == 0:
                raise RuntimeError("sampler launch fence released more often than acquired")
            findings = self._collect_unreported()
            self._depth -= 1
            if self._depth == 0:
                self._uninstall()
        if findings:
            raise AssertionError(
                "sampler launch fence refused real sampler/sudo starts "
                "(a test reached a production launch path unmocked):\n  "
                + "\n  ".join(findings)
            )

    def _refuse(self, api: str, args, executable=None) -> None:
        token = fenced_program(args, executable)
        if token is None:
            return
        test_id = _running_test_id()
        detail = f"{test_id or '<no test>'}: {api} {args!r}"
        with self._lock:
            self._unreported.append(detail)
        raise SamplerLaunchRefused(
            f"sampler launch fence: refused to start {token!r} via {api} "
            f"in {test_id or '<no test>'}: {args!r}"
        )

    def _collect_unreported(self) -> list[str]:
        findings, self._unreported = self._unreported, []
        if self._shim_log is not None and self._shim_log.exists():
            lines = self._shim_log.read_text(encoding="utf-8").splitlines()
            for line in lines[self._shim_lines_reported:]:
                name, _, rest = line.partition("\t")
                test_id, _, argv = rest.partition("\t")
                findings.append(
                    f"{test_id or '<child without test id>'}: child process ran "
                    f"stand-in {name} {argv}"
                )
            self._shim_lines_reported = len(lines)
        return findings

    def _install(self) -> None:
        fence = self
        original_init = subprocess.Popen.__init__

        def fenced_init(popen_self, args, *a, **k):
            fence._refuse("subprocess.Popen", args, k.get("executable"))
            return original_init(popen_self, args, *a, **k)

        self._originals["Popen.__init__"] = original_init
        subprocess.Popen.__init__ = fenced_init

        for name, (program_index, argv_index) in _POSITIONAL_ARGV.items():
            original = getattr(os, name, None)
            if original is None:
                continue
            self._originals[f"os.{name}"] = original

            def fenced(*a, _name=name, _original=original,
                       _program=program_index, _argv=argv_index, **k):
                argv = a[_argv] if len(a) > _argv else k.get("argv", ())
                program = a[_program] if len(a) > _program else k.get("path")
                fence._refuse(f"os.{_name}", argv, program)
                return _original(*a, **k)

            setattr(os, name, fenced)

        original_system = os.system
        self._originals["os.system"] = original_system

        def fenced_system(command):
            fence._refuse("os.system", command)
            return original_system(command)

        os.system = fenced_system

        self._shim_dir = Path(tempfile.mkdtemp(prefix="joulewise-sampler-fence-"))
        self._shim_log = self._shim_dir / "stand-in-starts.log"
        self._shim_lines_reported = 0
        for name in sorted(FENCED_PROGRAMS):
            stand_in = self._shim_dir / name
            stand_in.write_text(
                _STAND_IN.format(name=name, log=self._shim_log), encoding="utf-8"
            )
            stand_in.chmod(0o755)
        path = os.environ.get("PATH", "")
        os.environ["PATH"] = (
            str(self._shim_dir) + (os.pathsep + path if path else "")
        )
        self._previous_test_id_hook = _install_test_id_export()
        running = _running_test_id()
        if running is not None:  # acquired inside a test (the fence's own tests)
            os.environ["JOULEWISE_FENCE_TEST_ID"] = running

    def _uninstall(self) -> None:
        subprocess.Popen.__init__ = self._originals.pop("Popen.__init__")
        os.system = self._originals.pop("os.system")
        for key in list(self._originals):
            setattr(os, key.removeprefix("os."), self._originals.pop(key))
        _remove_test_id_export(self._previous_test_id_hook)
        shim_dir, self._shim_dir, self._shim_log = self._shim_dir, None, None
        if shim_dir is not None:
            entries = os.environ.get("PATH", "").split(os.pathsep)
            os.environ["PATH"] = os.pathsep.join(
                entry for entry in entries if entry != str(shim_dir)
            )
            shutil.rmtree(shim_dir, ignore_errors=True)


def _install_test_id_export():
    """Export the running test id to children so stand-in records name it."""

    original_run = unittest.TestCase.run

    def run(self, result=None):
        previous = os.environ.get("JOULEWISE_FENCE_TEST_ID")
        os.environ["JOULEWISE_FENCE_TEST_ID"] = self.id()
        try:
            return original_run(self, result)
        finally:
            if previous is None:
                os.environ.pop("JOULEWISE_FENCE_TEST_ID", None)
            else:
                os.environ["JOULEWISE_FENCE_TEST_ID"] = previous

    unittest.TestCase.run = run
    return original_run


def _remove_test_id_export(original_run) -> None:
    unittest.TestCase.run = original_run
    os.environ.pop("JOULEWISE_FENCE_TEST_ID", None)


FENCE = _Fence()


def install_module_fence() -> None:
    """Hold the fence for the calling module; release it at module cleanup."""

    FENCE.acquire()
    unittest.addModuleCleanup(FENCE.release)


class FencedSuite(unittest.TestSuite):
    """A module suite that holds the fence while every one of its tests runs."""

    def run(self, result, debug=False):
        FENCE.acquire()
        try:
            return super().run(result, debug)
        finally:
            try:
                FENCE.release()
            except AssertionError:
                result.addError(
                    unittest.suite._ErrorHolder("sampler_launch_fence"),
                    sys.exc_info(),
                )


def fenced_load_tests(loader, standard_tests, pattern):
    """``load_tests`` hook: run the module's own suite under the fence."""

    return FencedSuite([standard_tests])
