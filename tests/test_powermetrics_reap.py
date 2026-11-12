"""RL-91/RL-96: a failed bounded capture's root powermetrics is reaped and proven absent.

``subprocess.run(timeout=...)`` SIGKILLs ``sudo``, which cannot relay SIGKILL, so
the root sampler it started is orphaned. These tests build that shape with no
real sudo: a fake ``sudo`` (a temp script) starts a fake ``powermetrics`` child
in the same process group that ignores its parent's death, and the privileged
kill is a fake ``sudo`` running a fake ``kill``.

Each test resolves the adapter class production uses
(``joulewise.adapters.resolve_telemetry``), so the tests apply wherever the
reap lives; at 22f438fd3 they fail because the orphan survives.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.adapters import resolve_telemetry
try:
    from joulewise.adapters import powermetrics_reap
except ImportError:  # pre-RL-91 tree: the process tests still run, and fail on the surviving orphan
    powermetrics_reap = SimpleNamespace(UNPROVEN_REAPS=[], PowermetricsOrphanRefusal=type(
        "PowermetricsOrphanRefusal", (Exception,), {}), CENSUS_ARGV=(), ReapingPowermetricsTelemetryAdapter=None)
from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.clock import FakeClock
from tests.test_powermetrics import FIXTURE, make_config

FAKE_SUDO = """#!{python}
import subprocess, sys
args = sys.argv[1:]
if args[:1] == ["-n"]:
    args = args[1:]
sys.exit(subprocess.call(args))
"""
# A root sampler that outlives its sudo; with STUBBORN it ignores INT and TERM too.
FAKE_SAMPLER = """#!{python}
import signal, sys, time
signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGPIPE, signal.SIG_IGN)
if {stubborn}:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
deadline = time.monotonic() + 120
while time.monotonic() < deadline:
    time.sleep(0.05)
"""
# Writes the fixture to -o and exits: the normal path.
FAKE_WRITER = """#!{python}
import shutil, sys
shutil.copyfile({fixture!r}, sys.argv[sys.argv.index("-o") + 1])
"""
FAKE_KILL = """#!{python}
import os, signal, sys
os.kill(int(sys.argv[2]), getattr(signal, "SIG" + sys.argv[1].lstrip("-")))
"""
FAKE_KILL_NOOP = """#!{python}
import sys
sys.exit(0)
"""


def production_class():
    adapter, failure = resolve_telemetry(make_config(), FakeClock())
    assert failure is None and adapter is not None
    return type(adapter)


def write_script(directory: Path, name: str, text: str, **values) -> str:
    path = directory / name
    path.write_text(text.format(python=sys.executable, **values))
    path.chmod(0o755)
    return str(path)


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # A zombie of ours still answers kill(0); ps says whether it is gone.
    state = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True)
    return bool(state.stdout.strip()) and not state.stdout.strip().startswith("Z")


def sampler_pids(executable: str, output: Path | None = None) -> list[int]:
    rows = subprocess.run(["/bin/ps", "-axww", "-o", "pid=,command="], capture_output=True,
                          text=True, check=True).stdout.splitlines()
    found = []
    for row in rows:
        pid, _, command = row.strip().partition(" ")
        if executable in command and (output is None or f"-o {output}" in command):
            if alive(int(pid)):
                found.append(int(pid))
    return found


class ShortTimeout:
    """Test-only: a 1 s capture bound instead of the 15 s floor."""

    def _capture_timeout_s(self, config, count):
        return 1.0


def build(cls, clock, *, executable, sudo, kill=None, run=None):
    short = type("Short" + cls.__name__, (ShortTimeout, cls), {})
    reap = {"reap_grace_s": 1.0}
    if kill is not None:
        reap["kill_prefix"] = (sudo, "-n", kill)
    if run is not None:
        reap["reap_run"] = run
    try:
        return short(clock, executable=executable, privilege_prefix=(sudo, "-n"), **reap)
    except TypeError:  # an adapter with no reap seam (the pre-RL-91 class)
        return short(clock, executable=executable, privilege_prefix=(sudo, "-n"))


class ReapTestCase(unittest.TestCase):
    def setUp(self) -> None:
        powermetrics_reap.UNPROVEN_REAPS.clear()
        self.addCleanup(powermetrics_reap.UNPROVEN_REAPS.clear)
        self.tmp = Path(tempfile.mkdtemp(prefix="pmreap-"))
        self.sudo = write_script(self.tmp, "sudo", FAKE_SUDO)
        self.kill = write_script(self.tmp, "kill", FAKE_KILL)
        self.kill_noop = write_script(self.tmp, "kill-noop", FAKE_KILL_NOOP)
        self.sampler = write_script(self.tmp, "powermetrics", FAKE_SAMPLER, stubborn=False)
        self.stubborn = write_script(self.tmp, "powermetrics-stubborn", FAKE_SAMPLER, stubborn=True)
        self.writer = write_script(self.tmp, "powermetrics-writer", FAKE_WRITER, fixture=str(FIXTURE))
        self.addCleanup(self._kill_leftovers)

    def _kill_leftovers(self) -> None:
        for executable in (self.sampler, self.stubborn):
            for pid in sampler_pids(executable):
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

    def start_unrelated(self, executable: str) -> subprocess.Popen:
        """Another sampler (the night's sidecar, another member's capture): never touched."""

        other = self.tmp / "sidecar.plist"
        process = subprocess.Popen([executable, "-i", "100", "-o", str(other)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (process.kill(), process.wait()))
        time.sleep(0.3)
        return process

    def capture(self, adapter):
        return adapter._run_bounded_capture(make_config(), count=3, artifact_name="powermetrics_idle.plist",
                                            context=None)


class OrphanReapProcessTests(ReapTestCase):
    def test_timeout_reaps_root_child_and_proves_absence(self) -> None:
        adapter = build(production_class(), FakeClock(), executable=self.stubborn, sudo=self.sudo, kill=self.kill)
        sidecar = self.start_unrelated(self.stubborn)
        with self.assertRaises(subprocess.TimeoutExpired):  # the original exception propagates
            self.capture(adapter)
        self.assertEqual(sampler_pids(self.stubborn), [sidecar.pid], "orphan survived or sidecar killed")
        self.assertIsNone(sidecar.poll(), "an unrelated sampler was signalled")
        reaps = adapter.device_metadata(make_config())["capture_reaps"]
        self.assertEqual(len(reaps), 1)
        self.assertTrue(reaps[0]["absent"])
        self.assertEqual(reaps[0]["trigger"], "TimeoutExpired")
        self.assertEqual(len(reaps[0]["found"]), 1)
        self.assertNotIn(sidecar.pid, reaps[0]["found"])
        self.assertEqual([s["signal"] for s in reaps[0]["signals"]], ["INT", "TERM", "KILL"])
        self.assertEqual(powermetrics_reap.UNPROVEN_REAPS, [])

    def test_sampler_that_honours_int_needs_no_escalation(self) -> None:
        adapter = build(production_class(), FakeClock(), executable=self.sampler, sudo=self.sudo, kill=self.kill)
        with self.assertRaises(subprocess.TimeoutExpired):
            self.capture(adapter)
        self.assertEqual(sampler_pids(self.sampler), [])
        reap = adapter.device_metadata(make_config())["capture_reaps"][0]
        self.assertTrue(reap["absent"])
        self.assertEqual([s["signal"] for s in reap["signals"]], ["INT"])

    def test_unprovable_reap_refuses_loudly_and_poisons_later_captures(self) -> None:
        cls = production_class()
        adapter = build(cls, FakeClock(), executable=self.stubborn, sudo=self.sudo, kill=self.kill_noop)
        with self.assertRaises(powermetrics_reap.PowermetricsOrphanRefusal) as caught:
            self.capture(adapter)
        self.assertIsInstance(caught.exception.__cause__, subprocess.TimeoutExpired)
        self.assertIn("not proven absent", str(caught.exception))
        self.assertIn("RL-91", str(caught.exception))
        record = caught.exception.metadata["capture_reap"]
        self.assertFalse(record["absent"])
        self.assertEqual(record["reason"], "sampler still running after INT, TERM and KILL")
        self.assertEqual(len(record["remaining"]), 1)
        self.assertFalse(adapter.device_metadata(make_config())["capture_reaps"][0]["absent"])
        # Any later adapter in this process refuses before it starts a sampler.
        later = build(cls, FakeClock(), executable=self.writer, sudo=self.sudo, kill=self.kill)
        with self.assertRaises(powermetrics_reap.PowermetricsOrphanRefusal):
            self.capture(later)
        started = later.start_sampling(make_config())
        self.assertFalse(started.ok)
        self.assertIn("not proven absent", started.message)


class NormalPathTests(ReapTestCase):
    def test_successful_capture_is_identical_with_and_without_the_wrapper(self) -> None:
        cls = production_class()
        results = {}
        for name, klass in (("base", PowermetricsTelemetryAdapter), ("production", cls)):
            adapter = build(klass, FakeClock(start=100.0), executable=self.writer, sudo=self.sudo, kill=self.kill)
            data = self.capture(adapter)
            baseline = adapter.measure_idle(make_config())
            results[name] = (data, baseline, adapter.device_metadata(make_config()),
                             sorted(adapter._pending_captures))
        self.assertEqual(results["base"][0], FIXTURE.read_bytes())
        self.assertEqual(results["production"][0], results["base"][0])
        self.assertEqual(results["production"][1], results["base"][1])
        self.assertEqual(results["production"][2], results["base"][2])
        self.assertEqual(results["production"][3], results["base"][3])
        self.assertNotIn("capture_reaps", results["production"][2])

    def test_failed_capture_after_sudo_returned_is_unchanged(self) -> None:
        failing = write_script(self.tmp, "powermetrics-fails", "#!{python}\nimport sys\nsys.exit(3)\n")
        adapter = build(production_class(), FakeClock(), executable=failing, sudo=self.sudo, kill=self.kill)
        with self.assertRaisesRegex(RuntimeError, "powermetrics capture failed"):
            self.capture(adapter)
        reap = adapter.device_metadata(make_config())["capture_reaps"][0]
        self.assertTrue(reap["absent"])
        self.assertEqual(reap["signals"], [])


class StubbedTimeoutTests(unittest.TestCase):
    """No process at all: subprocess.run raises the timeout; the census and kill are scripted."""

    def setUp(self) -> None:
        powermetrics_reap.UNPROVEN_REAPS.clear()
        self.addCleanup(powermetrics_reap.UNPROVEN_REAPS.clear)

    def scripted(self, tables):
        calls = []
        own = os.getpid()

        def run(argv, timeout_s):
            calls.append(list(argv))
            if list(argv) == list(powermetrics_reap.CENSUS_ARGV):
                rows = tables.pop(0) if len(tables) > 1 else tables[0]
                text = "\n".join([f"{own} python -m unittest", *rows]) + "\n"
                return SimpleNamespace(returncode=0, stdout=text, stderr="")
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        return run, calls

    def adapter(self, run):
        return powermetrics_reap.ReapingPowermetricsTelemetryAdapter(
            FakeClock(), reap_run=run, reap_sleep=lambda s: None, reap_grace_s=0.0)

    def timeout_capture(self, adapter):
        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            return adapter._run_bounded_capture(make_config(), count=3, artifact_name="powermetrics_idle.plist",
                                                context=None)

    def test_kill_targets_only_this_captures_output_path(self) -> None:
        holder = {}
        tables = []

        def run(argv, timeout_s):
            path = holder["adapter"]._bounded_output_path
            mine = f"4242 /usr/bin/powermetrics -n 3 -b 0 -i 100 --samplers x --format plist -o {path}"
            sidecar = "5151 /usr/bin/powermetrics -i 100 --samplers x --format plist -o /tmp/sidecar.plist"
            byname = "6161 /usr/sbin/somethingelse powermetrics"
            tables.append(list(argv))
            if list(argv) == list(powermetrics_reap.CENSUS_ARGV):
                census = sum(1 for a in tables if a == list(powermetrics_reap.CENSUS_ARGV))
                rows = [mine, sidecar, byname] if census == 1 else [sidecar, byname]
                return SimpleNamespace(returncode=0, stdout="\n".join([f"{os.getpid()} py", *rows]), stderr="")
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        adapter = holder["adapter"] = self.adapter(run)
        with self.assertRaises(subprocess.TimeoutExpired):
            self.timeout_capture(adapter)
        kills = [argv for argv in tables if argv != list(powermetrics_reap.CENSUS_ARGV)]
        self.assertEqual(kills, [["sudo", "-n", "/bin/kill", "-INT", "4242"]])
        reap = adapter.device_metadata(make_config())["capture_reaps"][0]
        self.assertTrue(reap["absent"])
        self.assertEqual(reap["found"], [4242])

    def test_census_that_cannot_answer_refuses(self) -> None:
        for name, reply in (
            ("nonzero", SimpleNamespace(returncode=1, stdout="", stderr="ps: denied")),
            ("no_own_pid", SimpleNamespace(returncode=0, stdout="1 /sbin/launchd\n", stderr="")),
            ("empty", SimpleNamespace(returncode=0, stdout="", stderr="")),
        ):
            with self.subTest(name=name):
                powermetrics_reap.UNPROVEN_REAPS.clear()
                adapter = self.adapter(lambda argv, timeout_s, reply=reply: reply)
                with self.assertRaises(powermetrics_reap.PowermetricsOrphanRefusal) as caught:
                    self.timeout_capture(adapter)
                self.assertIsInstance(caught.exception.__cause__, subprocess.TimeoutExpired)
                self.assertIn("census", caught.exception.metadata["capture_reap"]["reason"])

    def test_census_exception_refuses(self) -> None:
        def run(argv, timeout_s):
            raise subprocess.TimeoutExpired(argv, timeout_s)

        adapter = self.adapter(run)
        with self.assertRaises(powermetrics_reap.PowermetricsOrphanRefusal):
            self.timeout_capture(adapter)
        self.assertEqual(len(powermetrics_reap.UNPROVEN_REAPS), 1)

    def test_probe_timeout_is_reaped_too(self) -> None:
        holder = {}
        tables = []

        def run(argv, timeout_s):
            tables.append(list(argv))
            path = holder["adapter"]._probe_output_path
            rows = [f"4343 /usr/bin/powermetrics -n 1 -b 0 -i 100 --samplers x --format plist -o {path}"]
            census = sum(1 for a in tables if a == list(powermetrics_reap.CENSUS_ARGV))
            return SimpleNamespace(returncode=0, stdout="\n".join(
                [f"{os.getpid()} py", *(rows if census == 1 else [])]), stderr="")

        adapter = holder["adapter"] = self.adapter(run)

        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())
        self.assertFalse(result.ok)
        self.assertIn("timed out", result.message)  # the parent's own probe result stands
        self.assertIn(["sudo", "-n", "/bin/kill", "-INT", "4343"], tables)
        self.assertTrue(adapter.device_metadata(make_config())["capture_reaps"][0]["absent"])


if __name__ == "__main__":
    unittest.main()
