from __future__ import annotations

import errno
import os
import signal
import subprocess
import sys
import unittest
from unittest.mock import call, patch

from joulewise.sampler_teardown import SamplerTeardown


class FakeProcess:
    def __init__(self, pid: int = 123456) -> None:
        self.pid = pid
        self.returncode: int | None = None
        self.terminate_calls = 0
        self.kill_calls = 0
        self.wait_calls = 0

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminate_calls += 1

    def kill(self) -> None:
        self.kill_calls += 1
        self.returncode = -signal.SIGKILL

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        if self.returncode is None:
            self.returncode = -signal.SIGTERM
        return self.returncode

    def communicate(self, *args, **kwargs):
        return b"", b""


class SamplerTeardownTests(unittest.TestCase):
    def _isolated_custodian(self, process: FakeProcess) -> SamplerTeardown:
        custodian = SamplerTeardown(termination_grace_s=0.0, census_timeout_s=0.0)
        with (
            patch("joulewise.sampler_teardown.subprocess.Popen", return_value=process),
            patch("joulewise.sampler_teardown.os.setpgid"),
        ):
            with custodian.intercept_popen():
                proxy = subprocess.Popen(["sampler", "--stream", "-o", "capture"])
        self.assertEqual(proxy.pid, process.pid)
        self.assertEqual(custodian._isolation_mode, "isolated_group")
        return custodian

    def test_parent_adoption_pins_isolated_and_direct_child_modes(self) -> None:
        isolated = FakeProcess(101)
        isolated_custodian = SamplerTeardown()
        with (
            patch("joulewise.sampler_teardown.subprocess.Popen", return_value=isolated),
            patch("joulewise.sampler_teardown.os.setpgid") as setpgid,
        ):
            with isolated_custodian.intercept_popen():
                subprocess.Popen(
                    ["sudo", "-n", "/usr/bin/powermetrics", "-o", "capture"]
                )
        setpgid.assert_called_once_with(101, 101)
        self.assertEqual(isolated_custodian._isolation_mode, "isolated_group")
        self.assertEqual(isolated_custodian._process_group_id, 101)
        self.assertEqual(
            isolated_custodian._spawn_argv,
            ["sudo", "-n", "/usr/bin/powermetrics", "-o", "capture"],
        )
        self.assertEqual(
            isolated_custodian._sampler_argv,
            ["/usr/bin/powermetrics", "-o", "capture"],
        )

        fallback = FakeProcess(202)
        fallback_custodian = SamplerTeardown()
        error = OSError(errno.EPERM, "child already exec'd")
        with (
            patch("joulewise.sampler_teardown.subprocess.Popen", return_value=fallback),
            patch("joulewise.sampler_teardown.os.setpgid", side_effect=error),
        ):
            with fallback_custodian.intercept_popen():
                subprocess.Popen(["sampler", "--stream", "-o", "capture"])
        self.assertEqual(fallback_custodian._isolation_mode, "none_direct_child")
        self.assertIsNone(fallback_custodian._process_group_id)

    def test_sigterm_ignoring_direct_child_is_killed(self) -> None:
        code = (
            "import signal,sys,time; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            "print('ready', flush=True); time.sleep(60)"
        )
        custodian = SamplerTeardown(termination_grace_s=0.05, census_timeout_s=0.2)
        with patch(
            "joulewise.sampler_teardown.os.setpgid",
            side_effect=OSError(errno.EPERM, "forced direct-child fallback"),
        ):
            with custodian.intercept_popen():
                process = subprocess.Popen(
                    [sys.executable, "-c", code, "-o", "capture"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
        assert process.stdout is not None
        self.assertEqual(process.stdout.readline().strip(), "ready")
        process.stdout.close()
        process.terminate()
        report = custodian.report
        assert report is not None
        self.assertEqual(report["status"], "clean")
        self.assertEqual(report["isolation_mode"], "none_direct_child")
        self.assertTrue(report["kill_escalated"])
        self.assertTrue(report["leader_reaped"])
        self.assertEqual(process.returncode, -signal.SIGKILL)

    def test_group_sigterm_then_sigkill_kills_before_reaping(self) -> None:
        process = FakeProcess(303)
        custodian = self._isolated_custodian(process)
        with (
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._process_group_members",
                side_effect=[
                    [{"pid": 304, "state": "S"}],
                    [{"pid": 304, "state": "S"}],
                    [],
                ],
            ),
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._wide_argv_census",
                return_value=[],
            ),
            patch("joulewise.sampler_teardown.os.killpg") as killpg,
        ):
            report = custodian.teardown(process)
        self.assertEqual(
            killpg.call_args_list,
            [call(303, signal.SIGTERM), call(303, signal.SIGKILL)],
        )
        self.assertTrue(report["kill_escalated"])
        self.assertTrue(report["leader_reaped"])
        self.assertEqual(report["status"], "clean")

    def test_well_behaved_group_exits_during_sigterm_grace(self) -> None:
        process = FakeProcess(404)
        custodian = self._isolated_custodian(process)
        with (
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._process_group_members",
                side_effect=[[], [], []],
            ),
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._wide_argv_census",
                return_value=[],
            ),
            patch("joulewise.sampler_teardown.os.killpg") as killpg,
        ):
            report = custodian.teardown(process)
        killpg.assert_called_once_with(404, signal.SIGTERM)
        self.assertFalse(report["kill_escalated"])
        self.assertEqual(report["status"], "clean")

    def test_escaped_argv_candidate_is_reported_and_never_signaled(self) -> None:
        process = FakeProcess(505)
        custodian = self._isolated_custodian(process)
        escaped = {
            "pid": 999999,
            "argv": ["sampler", "--stream", "-o", "capture"],
        }
        with (
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._process_group_members",
                side_effect=[[], [], []],
            ),
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._wide_argv_census",
                return_value=[escaped],
            ),
            patch("joulewise.sampler_teardown.os.killpg") as killpg,
            patch("joulewise.sampler_teardown.os.kill") as direct_kill,
        ):
            report = custodian.teardown(process)
        killpg.assert_called_once_with(505, signal.SIGTERM)
        direct_kill.assert_not_called()
        self.assertEqual(report["status"], "contaminated")
        self.assertEqual(report["escaped_candidates"], [escaped])
        self.assertTrue(report["survivors_detected"])

    def test_census_exception_is_fail_closed_as_contamination_unknown(self) -> None:
        process = FakeProcess(606)
        custodian = self._isolated_custodian(process)
        with (
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._process_group_members",
                side_effect=[[], [], []],
            ),
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._wide_argv_census",
                side_effect=OSError("injected census failure"),
            ),
            patch("joulewise.sampler_teardown.os.killpg"),
        ):
            report = custodian.teardown(process)
        self.assertEqual(report["status"], "contamination_unknown")
        self.assertEqual(report["exception_class"], "OSError")
        self.assertFalse(report["census_completed"])
        self.assertIn("injected census failure", report["errors"][-1])

    def test_post_reap_group_signal_is_refused_and_recorded(self) -> None:
        process = FakeProcess(707)
        custodian = self._isolated_custodian(process)
        process.returncode = 0
        with patch("joulewise.sampler_teardown.os.killpg") as killpg:
            report = custodian.teardown(process)
        killpg.assert_not_called()
        self.assertEqual(report["status"], "contamination_unknown")
        self.assertTrue(report["leader_reaped"])
        self.assertEqual(
            report["signal_attempts"],
            [
                {
                    "signal": "SIGTERM",
                    "target": "process_group",
                    "outcome": "refused_leader_reaped",
                }
            ],
        )

    def test_custody_report_schema_is_stable(self) -> None:
        process = FakeProcess(808)
        custodian = self._isolated_custodian(process)
        with (
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._process_group_members",
                side_effect=[[], [], []],
            ),
            patch(
                "joulewise.sampler_teardown.SamplerTeardown._wide_argv_census",
                return_value=[],
            ),
            patch("joulewise.sampler_teardown.os.killpg"),
        ):
            report = custodian.teardown(process)
        self.assertEqual(
            set(report),
            {
                "status",
                "isolation_mode",
                "direct_child_pid",
                "process_group_id",
                "spawn_argv",
                "sampler_argv",
                "termination_signal",
                "termination_grace_s",
                "kill_escalated",
                "census_method",
                "census_timeout_s",
                "census_completed",
                "survivors_detected",
                "group_survivors",
                "escaped_candidates",
                "signal_attempts",
                "leader_reaped",
                "exception_class",
                "errors",
            },
        )


if __name__ == "__main__":
    unittest.main()
