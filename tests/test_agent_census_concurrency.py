"""Native peer-pgrep regressions for night_gate.AGENT_CENSUS_ARGV.

These are process-list checks, not quiet-machine measurements. Assert owned
PIDs only: an interactive agent may legitimately be present at the bench.
"""

from __future__ import annotations

import ctypes
import multiprocessing
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from joulewise.night_gate import AGENT_CENSUS_ARGV


def _pids(stdout):
    # A foreign agent's argv may contain newlines; continuation text is not
    # a PID record. Other agents are allowed at this read-only native bench.
    return {int(match.group(1)) for match in re.finditer(r"(?m)^([0-9]+)(?:\s|$)", stdout)}


def _overlap_worker(argv, barrier, connection, count):
    """Each worker owns/reaps its probe, including on timeout or broken barrier."""
    try:
        for _ in range(count):
            barrier.wait(timeout=20)
            with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, env={**os.environ, "LC_ALL": "C"}) as probe:
                try:
                    stdout, stderr = probe.communicate(timeout=10)
                except BaseException:
                    probe.kill()
                    probe.communicate()
                    raise
                connection.send((probe.pid, probe.returncode, stdout, stderr))
    except Exception as error:
        connection.send((None, None, "", repr(error)))
    finally:
        connection.close()


def _darwin_spawn_suspended(argv):
    """Exec pgrep already stopped (Darwin spawn.h), without a pre-exec race."""
    libc = ctypes.CDLL(None)
    attr, actions, pid = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_int()
    pointer = ctypes.POINTER(ctypes.c_void_p)
    for name in ("posix_spawnattr_init", "posix_spawnattr_destroy",
                 "posix_spawn_file_actions_init", "posix_spawn_file_actions_destroy"):
        getattr(libc, name).argtypes = [pointer]
    libc.posix_spawnattr_setflags.argtypes = [pointer, ctypes.c_short]
    libc.posix_spawn_file_actions_addopen.argtypes = [
        pointer, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_uint16]
    libc.posix_spawn.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,
                                pointer, pointer, ctypes.POINTER(ctypes.c_char_p),
                                ctypes.POINTER(ctypes.c_char_p)]

    def check(code):
        if code:
            raise OSError(code, os.strerror(code))

    def strings(values):
        return (ctypes.c_char_p * (len(values) + 1))(
            *(os.fsencode(value) for value in values), None)

    check(libc.posix_spawnattr_init(ctypes.byref(attr)))
    try:
        check(libc.posix_spawnattr_setflags(ctypes.byref(attr), 0x0080))  # START_SUSPENDED
        check(libc.posix_spawn_file_actions_init(ctypes.byref(actions)))
        try:
            for fd in (1, 2):
                check(libc.posix_spawn_file_actions_addopen(
                    ctypes.byref(actions), fd, b"/dev/null", os.O_WRONLY, 0))
            check(libc.posix_spawn(ctypes.byref(pid), os.fsencode(argv[0]),
                                  ctypes.byref(actions), ctypes.byref(attr), strings(argv),
                                  strings([f"{key}={value}" for key, value in os.environ.items()])))
        finally:
            libc.posix_spawn_file_actions_destroy(ctypes.byref(actions))
    finally:
        libc.posix_spawnattr_destroy(ctypes.byref(attr))
    return pid.value


class AgentCensusConcurrencyTests(unittest.TestCase):
    def setUp(self):
        # Every native test checks access before spawning owned peers/markers.
        self._probe(AGENT_CENSUS_ARGV)

    def _check_result(self, returncode, stderr):
        if returncode == 3 and "Cannot get process list" in stderr:
            self.skipTest("/usr/bin/pgrep unavailable in sandbox: exit 3, Cannot get process list")
        self.assertIn(returncode, (0, 1), f"pgrep exit {returncode}: {stderr}")

    def _probe(self, argv):
        try:
            result = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                                    env={**os.environ, "LC_ALL": "C"})
        except OSError as error:
            self.skipTest(f"/usr/bin/pgrep unavailable: {error}")
        self._check_result(result.returncode, result.stderr)
        return _pids(result.stdout)

    def _overlap_hits(self, argv):
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(2)
        readers, workers = [], []
        records = [[], []]
        try:
            for _ in range(2):
                reader, writer = context.Pipe(duplex=False)
                worker = context.Process(target=_overlap_worker,
                                         args=(argv, barrier, writer, 1000))
                readers.append(reader)
                workers.append(worker)
                worker.start()
                writer.close()
            for _ in range(1000):
                for index, reader in enumerate(readers):
                    self.assertTrue(reader.poll(30), "synchronized pgrep worker stalled")
                    pid, returncode, stdout, stderr = reader.recv()
                    self.assertIsNotNone(pid, stderr)
                    self._check_result(returncode, stderr)
                    records[index].append((pid, _pids(stdout)))
            for worker in workers:
                worker.join(timeout=10)
                self.assertEqual(0, worker.exitcode)
        finally:
            barrier.abort()
            for worker in workers:
                if worker.pid is not None:
                    worker.join(timeout=15)  # let communicate timeout reap its child
                    if worker.is_alive():
                        worker.terminate()
                        worker.join(timeout=5)
            for reader in readers:
                reader.close()
        # Save both invocations' owned PIDs for every synchronized iteration.
        return [(left[0], right[0]) for left, right in zip(*records)
                if right[0] in left[1] or left[0] in right[1]]

    def test_synchronized_peer_censuses_do_not_match(self):
        """Old literal at agent_census's exec site detects sibling pgrep PIDs."""
        self.assertEqual([], self._overlap_hits(AGENT_CENSUS_ARGV))
        old_argv = (*AGENT_CENSUS_ARGV[:2], "|".join(("codex", "claude", "t3")))
        control_hits = self._overlap_hits(old_argv)
        if not control_hits:
            self.skipTest("INCONCLUSIVE: 2 x 1,000 old-pattern probes had zero peer hits; scheduler did not expose overlap")
        self.assertGreaterEqual(len(control_hits), 1)

    def test_stopped_peer_is_excluded_after_exec(self):
        """Old production argv matches even a stopped, already-execed sibling."""
        if sys.platform != "darwin":
            self.skipTest("stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED")
        pid = _darwin_spawn_suspended(AGENT_CENSUS_ARGV)
        try:
            os.kill(pid, signal.SIGSTOP)
            state = subprocess.run(("/bin/ps", "-p", str(pid), "-o", "state=", "-o", "command="),
                                   capture_output=True, text=True, timeout=5, check=True)
            self.assertIn("T", state.stdout.split()[0], state.stdout)
            self.assertIn(" ".join(AGENT_CENSUS_ARGV), state.stdout)
            self.assertNotIn(pid, self._probe(AGENT_CENSUS_ARGV))
        finally:
            os.kill(pid, signal.SIGCONT)
            deadline = time.monotonic() + 10
            while True:
                reaped, _ = os.waitpid(pid, os.WNOHANG)
                if reaped:
                    break
                if time.monotonic() >= deadline:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                    break
                time.sleep(0.01)

    def test_owned_agent_markers_are_still_listed(self):
        """Foreign agent-name argv must remain visible at agent_census's exec site."""
        with tempfile.TemporaryDirectory(prefix="census-markers-") as directory:
            for name in ("codex", "claude", "t3"):
                with self.subTest(agent=name):
                    marker = Path(directory) / name
                    marker.symlink_to("/bin/sleep")
                    with subprocess.Popen((str(marker), "30")) as process:
                        try:
                            self.assertIn(process.pid, self._probe(AGENT_CENSUS_ARGV))
                        finally:
                            process.terminate()
                            process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
