"""Gate-prune round 2, lane P2-CTL, CLI items.

- J2 (PLAN2 section 3.2): ``validate_bundle(..., physics_cache=...)`` reaches
  the strict re-reduction; ``None`` keeps today's behaviour.
- Row 8: ``joulewise run`` on a HAZARD root turns SIGTERM into SystemExit, so
  the controller's interrupt salvage finalizes the bundle; the legacy path
  keeps the default disposition.
"""

from __future__ import annotations

import json
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise import cli, controller
from joulewise.schemas import RunStatus
from tests.test_controller import make_config
from tests import child_guard

REPO = Path(__file__).resolve().parents[1]



class StrictPhysicsCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        from joulewise.clock import FakeClock

        self.bundle, summary = controller.run_benchmark(
            make_config("j2-strict"), Path(tmp.name), FakeClock(start=1_700_000_000.0))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)

    def strict_reduce_caches(self, **kwargs: Any) -> list[Any]:
        seen: list[Any] = []
        real = cli.reduce_bundle

        def recording(path, **reduce_kwargs):
            seen.append(reduce_kwargs.get("_instrument_calibration_physics_cache", "absent"))
            return real(path, **reduce_kwargs)

        with patch.object(cli, "reduce_bundle", side_effect=recording):
            problems = cli.validate_bundle(self.bundle, strict=True, **kwargs)
        self.assertEqual(problems, [])
        return seen

    def test_an_explicit_cache_reaches_the_strict_reduce(self) -> None:
        cache: dict[str, float] = {}
        seen = self.strict_reduce_caches(physics_cache=cache)
        self.assertTrue(seen)
        self.assertTrue(all(value is cache for value in seen))

    def test_without_a_cache_the_reduce_gets_none_as_before(self) -> None:
        seen = self.strict_reduce_caches()
        self.assertTrue(seen)
        self.assertTrue(all(value is None for value in seen))


# ---------------------------------------------------------------------------
# Row 8: SIGTERM salvage in `joulewise run`


_SIGTERM_CHILD = r"""
import json, sys, time
sys.path.insert(0, {repo!r})
from pathlib import Path
from joulewise import cli, controller
from joulewise.flags import core as flags_core
from tests.test_controller import make_config

mode, runs_dir, config_path = sys.argv[1:4]
Path(config_path).write_text(json.dumps(make_config("sigterm-member").to_dict()))
if mode == "hazard":
    context = flags_core.HazardFlagContext(
        writer="core-controller", custody_root=None, plan_id=None, attempt=None,
        scope_resolved=False)
    flags_core.hazard_flag_context = lambda *args, **kwargs: context

def blocking_warmup(self):
    print("ready", flush=True)
    time.sleep(60)

controller._Execution._stage_warmup = blocking_warmup
sys.exit(cli.main(["run", config_path, "--runs-dir", runs_dir]))
"""


class SigtermSalvageTests(unittest.TestCase):
    def run_and_terminate(self, mode: str) -> tuple[int, Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        runs = Path(tmp.name) / "runs"
        script = Path(tmp.name) / "child.py"
        script.write_text(_SIGTERM_CHILD.format(repo=str(REPO)))
        child = subprocess.Popen(
            [sys.executable, str(script), mode, str(runs), str(Path(tmp.name) / "config.json")],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=str(REPO), text=True,
            # An ignored SIGTERM is inherited across exec; another module in the
            # same test process (night_agent_install's shield, via
            # test_gen_g2a_window) can leave SIGTERM ignored.  The member starts
            # with the default disposition, as the chain launches it.
            preexec_fn=lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL))
        try:
            self.assertEqual(child.stdout.readline().strip(), "ready")
            child.send_signal(signal.SIGTERM)
            returncode = child.wait(timeout=60)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
            child.stdout.close()
        return returncode, runs / "sigterm-member"

    def test_hazard_sigterm_finalizes_the_bundle_through_the_salvage(self) -> None:
        returncode, bundle = self.run_and_terminate("hazard")
        self.assertEqual(returncode, 128 + signal.SIGTERM)
        summary = json.loads((bundle / "summary_metrics.json").read_bytes())
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["failure_message"], f"SystemExit: {128 + signal.SIGTERM}")
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["event_type"], "run_finalized")

    def test_legacy_sigterm_keeps_the_default_disposition(self) -> None:
        returncode, bundle = self.run_and_terminate("legacy")
        self.assertEqual(returncode, -signal.SIGTERM)
        self.assertFalse((bundle / "summary_metrics.json").exists())

class SigtermHandlerShapeTests(unittest.TestCase):
    """Review F5: the handler is one-shot, restored, and main-thread only."""

    @staticmethod
    def context() -> Any:
        from joulewise.flags.core import HazardFlagContext

        return HazardFlagContext(writer="core-controller", custody_root=None,
                                 plan_id=None, attempt=None, scope_resolved=False)

    def test_a_second_sigterm_does_not_interrupt_the_salvage(self) -> None:
        prior = signal.getsignal(signal.SIGTERM)
        try:
            with patch("joulewise.flags.core.hazard_flag_context", return_value=self.context()):
                with cli._hazard_sigterm_salvage(Path("/synthetic")):
                    handler = signal.getsignal(signal.SIGTERM)
                    with self.assertRaises(SystemExit):
                        handler(signal.SIGTERM, None)
                    handler(signal.SIGTERM, None)  # ignored, no raise
        finally:
            signal.signal(signal.SIGTERM, prior)

    def test_the_previous_handler_is_restored(self) -> None:
        prior = signal.getsignal(signal.SIGTERM)
        try:
            with patch("joulewise.flags.core.hazard_flag_context", return_value=self.context()):
                with cli._hazard_sigterm_salvage(Path("/synthetic")):
                    self.assertIsNot(signal.getsignal(signal.SIGTERM), prior)
            self.assertIs(signal.getsignal(signal.SIGTERM), prior)
        finally:
            signal.signal(signal.SIGTERM, prior)

    def test_a_worker_thread_installs_nothing(self) -> None:
        errors: list[BaseException] = []

        def worker() -> None:
            try:
                with cli._hazard_sigterm_salvage(Path("/synthetic")):
                    pass
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)

        import threading

        with patch("joulewise.flags.core.hazard_flag_context", return_value=self.context()):
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
        self.assertEqual(errors, [])


class SigtermDuringInstallTests(unittest.TestCase):
    """Review F3: a SIGTERM after bundle creation but before the lifecycle
    (the calibration attachment install) is salvaged and finalized."""

    def test_sigterm_during_the_attachment_install_finalizes_the_bundle(self) -> None:
        import os

        from joulewise.clock import FakeClock
        from joulewise.flags.core import HazardFlagContext

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = HazardFlagContext(writer="core-controller", custody_root=root,
                                        plan_id=None, attempt=None, scope_resolved=False)
            attachment = controller._InstrumentCalibrationAttachment(files={}, metadata={})

            def terminate_install(_self, _bundle):
                os.kill(os.getpid(), signal.SIGTERM)

            prior = signal.getsignal(signal.SIGTERM)
            try:
                with patch("joulewise.flags.core.hazard_flag_context", return_value=context), \
                        patch.object(controller, "_load_instrument_calibration_attachment",
                                     return_value=attachment), \
                        patch.object(controller._InstrumentCalibrationAttachment, "install",
                                     terminate_install):
                    with self.assertRaises(SystemExit) as caught:
                        with cli._hazard_sigterm_salvage(root):
                            controller.run_benchmark(make_config("term-install"), root, FakeClock())
            finally:
                signal.signal(signal.SIGTERM, prior)
            self.assertEqual(caught.exception.code, 128 + signal.SIGTERM)
            bundle = root / "term-install"
            summary = json.loads((bundle / "summary_metrics.json").read_bytes())
            self.assertEqual(summary["status"], "failed")
            self.assertEqual(summary["failure_message"], f"SystemExit: {128 + signal.SIGTERM}")
            events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["event_type"], "run_finalized")


# Test hygiene (2026-10-07): a test or class in this module that leaves a child process running
# is reported as failed, and the child is stopped (tests/child_guard.py).
child_guard.guard_test_classes(globals())


if __name__ == "__main__":
    unittest.main()
