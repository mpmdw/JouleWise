from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from joulewise.adapters.powermetrics import (
    STOP_PROCESS_GRACE_S,
    PowermetricsTelemetryAdapter,
)
from joulewise.clock import FakeClock
from joulewise.schemas import FailureReason
from tests.test_powermetrics import make_config


@unittest.skipUnless(os.name == "posix", "requires POSIX signal relay semantics")
class BoundedCaptureTimeoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pid_path = self.root / "sampler.pid"
        self.signals_path = self.root / "relay.signals"
        self.sampler_dead = False
        self.grace_s = STOP_PROCESS_GRACE_S
        # Any positive timeout below the sampler's lifetime gives the same
        # outcome once the pid handshake has completed; 10 ms keeps tests fast
        # without depending on interpreter startup speed.
        self.timeout_s = 0.01
        self.relay = self.root / "pm-orphan-test-sudo-relay.py"
        self.relay.write_text(
            """import signal
import subprocess
import sys
from pathlib import Path

signals_path = Path(sys.argv[1])
child = None

def relay(signum, frame):
    with signals_path.open("a") as log:
        log.write(signal.Signals(signum).name + "\\n")
    if child is not None:
        child.send_signal(signum)

for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(signum, relay)
child = subprocess.Popen([sys.executable, *sys.argv[2:]])
status = child.wait()
sys.exit(status if status >= 0 else 128 - status)
""",
            encoding="utf-8",
        )
        self.sampler = self.root / "pm-orphan-test-sampler.py"
        # Twice the existing stop grace keeps the sampler alive beyond both
        # the forced timeout and the entire allowed cleanup interval.
        self.sampler.write_text(
            "import os, time\nfrom pathlib import Path\n"
            f"Path({str(self.pid_path)!r}).write_text(str(os.getpid()))\n"
            f"time.sleep({2 * self.grace_s!r})\n",
            encoding="utf-8",
        )
        self.adapter = PowermetricsTelemetryAdapter(
            FakeClock(),
            executable=str(self.sampler),
            privilege_prefix=(sys.executable, str(self.relay), str(self.signals_path)),
        )
        self.addCleanup(self._cleanup_capture)

    def _cleanup_capture(self):
        for artifact in list(self.adapter._pending_captures):
            self.adapter._release_capture(artifact)
        # Even a regression that kills only the relay must not leak a fixture.
        if not self.sampler_dead and self.pid_path.exists():
            try:
                os.kill(int(self.pid_path.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass

    def _wait_for(self, predicate):
        # Reuse the stop grace as a generous fixture startup/disappearance
        # budget, not a measured startup limit or an acceptance threshold.
        deadline = time.monotonic() + self.grace_s
        while not predicate():
            if time.monotonic() >= deadline:
                self.fail("fixture condition not met within _stop_process grace")
            # This spacing affects observation latency only, not the result:
            # the capture timeout starts after the explicit pid handshake.
            time.sleep(self.timeout_s / 10)

    def _assert_sampler_dead(self):
        pid = int(self.pid_path.read_text())

        def dead():
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return True
            return False

        self._wait_for(dead)
        self.sampler_dead = True

    def _capture(self, *, interrupt=None, probe=False):
        real_popen = subprocess.Popen
        self.processes = []

        def launch(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            self.processes.append(process)
            self.addCleanup(self.adapter._stop_process, process)
            communicate = process.communicate
            first_wait = True

            def wait(*wait_args, **wait_kwargs):
                nonlocal first_wait
                if first_wait:
                    first_wait = False
                    self._wait_for(self.pid_path.exists)
                    if interrupt is not None:
                        raise interrupt
                    if probe:
                        self.assertEqual(wait_kwargs["timeout"], 15.0)
                        # Keep the production probe's 15 s request observable;
                        # only the real fixture wait uses the same scheduler
                        # timeout as the bounded-capture tests above.
                        wait_kwargs["timeout"] = self.timeout_s
                return communicate(*wait_args, **wait_kwargs)

            process.communicate = Mock(side_effect=wait)
            process.kill = Mock(wraps=process.kill)
            return process

        with (
            patch("joulewise.adapters.powermetrics.subprocess.Popen", side_effect=launch),
            patch.object(self.adapter, "_capture_timeout_s", return_value=self.timeout_s),
        ):
            if probe:
                return self.adapter._probe_capability()
            return self.adapter._run_bounded_capture(
                make_config(), count=1, artifact_name="bounded.plist", context=None
            )

    def test_timeout_reaches_caller_and_grandchild_is_dead(self):
        with self.assertRaises(subprocess.TimeoutExpired) as raised:
            self._capture()
        self.assertEqual(raised.exception.timeout, self.timeout_s)
        self._assert_sampler_dead()
        self.assertEqual(self.adapter._pending_captures, {})

    def test_timeout_relays_sigterm_without_killing_launcher(self):
        # SIGKILL cannot be caught or forwarded by this relay, just as with
        # sudo. Its child has default signal handlers and no parent-death hook.
        # A dead sampler plus this receipt therefore pins SIGTERM forwarding.
        with self.assertRaises(subprocess.TimeoutExpired):
            self._capture()
        self.processes[0].kill.assert_not_called()
        self.assertTrue(self.signals_path.exists(), "relay never received SIGTERM")
        self.assertEqual(self.signals_path.read_text().splitlines(), ["SIGTERM"])
        self._assert_sampler_dead()

    def test_stop_escalation_reaps_relay_without_waiting_for_sampler_pipes(self):
        # One grace is the helper's only timed wait. Allow one more grace for
        # scheduling, reaping the SIGKILLed relay, and closing pipes: wait() is
        # not a second wait for the sampler. Give the sampler twice that total
        # budget so an EOF wait cannot pass by reaching its natural exit.
        return_bound_s = 2 * self.grace_s
        sampler_lifetime_s = 2 * return_bound_s
        self.sampler.write_text(
            "import os, signal, time\nfrom pathlib import Path\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            f"Path({str(self.pid_path)!r}).write_text(str(os.getpid()))\n"
            f"time.sleep({sampler_lifetime_s!r})\n",
            encoding="utf-8",
        )
        process = subprocess.Popen(
            [sys.executable, str(self.relay), str(self.signals_path), str(self.sampler)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self._wait_for(self.pid_path.exists)
            started = time.monotonic()
            self.adapter._stop_process(process)
            elapsed_s = time.monotonic() - started
            self.assertGreaterEqual(elapsed_s, self.grace_s)
            self.assertLess(elapsed_s, return_bound_s)
            self.assertEqual(process.returncode, -signal.SIGKILL)
            self.assertTrue(process.stdout.closed)
            self.assertTrue(process.stderr.closed)
            self.assertEqual(self.signals_path.read_text().splitlines(), ["SIGTERM"])
            # The sampler is still alive well before its natural exit. A root
            # orphan on this double-failure path cannot be removed by Python
            # without a sudoers kill entry; this fixture is our unprivileged
            # process, so the finally block can safely SIGKILL it by known pid.
            os.kill(int(self.pid_path.read_text()), 0)
        finally:
            self._cleanup_capture()
            if process.poll() is None:
                process.kill()
            process.wait()
            for pipe in (process.stdout, process.stderr):
                if pipe is not None:
                    pipe.close()

    def test_stop_escalation_with_devnull_has_no_pipes_to_close(self):
        process = Mock(stdout=None, stderr=None)
        process.poll.return_value = None
        process.communicate.side_effect = subprocess.TimeoutExpired("sampler", self.grace_s)
        self.adapter._stop_process(process)
        process.terminate.assert_called_once_with()
        process.communicate.assert_called_once_with(timeout=self.grace_s)
        process.kill.assert_called_once_with()
        process.wait.assert_called_once_with()

    def test_keyboard_interrupt_also_stops_grandchild_and_releases_capture(self):
        interrupt = KeyboardInterrupt("interrupted wait")
        with self.assertRaises(KeyboardInterrupt) as raised:
            self._capture(interrupt=interrupt)
        self.assertIs(raised.exception, interrupt)
        self._assert_sampler_dead()
        self.assertEqual(self.adapter._pending_captures, {})

    def test_probe_timeout_stops_grandchild_and_preserves_structured_failure(self):
        result = self._capture(probe=True)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertTrue(result.message.startswith("powermetrics capability probe timed out: "))
        metadata = self.adapter.device_metadata(make_config())
        self.assertEqual(metadata["powermetrics"]["samplers_probe"],
                         {"ok": False, "reason": "timeout"})
        self.processes[0].kill.assert_not_called()
        self.assertEqual(self.signals_path.read_text().splitlines(), ["SIGTERM"])
        self._assert_sampler_dead()
        self.assertFalse(Path(self.processes[0].args[-1]).exists())

    def test_probe_keyboard_interrupt_stops_grandchild_and_reraises(self):
        interrupt = KeyboardInterrupt("interrupted probe")
        with self.assertRaises(KeyboardInterrupt) as raised:
            self._capture(probe=True, interrupt=interrupt)
        self.assertIs(raised.exception, interrupt)
        self._assert_sampler_dead()

    def test_success_returns_capture_bytes_unchanged(self):
        payload = b"\x00native capture\xff\n"
        self.sampler.write_text(
            "import sys\nfrom pathlib import Path\n"
            f"Path(sys.argv[sys.argv.index('-o') + 1]).write_bytes({payload!r})\n",
            encoding="utf-8",
        )
        # Success uses the production timeout, with no artificial timing bar.
        result = self.adapter._run_bounded_capture(
            make_config(), count=1, artifact_name="bounded.plist", context=None
        )
        self.assertEqual(result, payload)

    def test_nonzero_exit_preserves_error_text_and_releases_capture(self):
        self.sampler.write_text(
            "import sys\nsys.stderr.buffer.write(b'  bad capture\\xff \\n')\n"
            "sys.exit(7)\n",
            encoding="utf-8",
        )
        with self.assertRaises(RuntimeError) as raised:
            self.adapter._run_bounded_capture(
                make_config(), count=1, artifact_name="bounded.plist", context=None
            )
        self.assertEqual(str(raised.exception), "powermetrics capture failed: bad capture\ufffd")
        self.assertEqual(self.adapter._pending_captures, {})


if __name__ == "__main__":
    unittest.main()
