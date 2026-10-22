"""Synthetic entry-point coverage; never stage custody or run a campaign."""

from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import network_time_off
from scripts import bench_replay_start_drift as bench


class BenchReplayEntrypointTests(unittest.TestCase):
    def run_bench(self, error=None):
        original_argv = network_time_off.OFF_ARGV
        replay_env = bench.harness.REPLAY_ENV
        # Cover restoration of both overwritten and initially absent variables.
        environment = {replay_env: "synthetic-archive", "NIGHT_PLAN_ID": "bench-plan"}
        exports = {"EVIDENCE_CHAIN_SOURCE_SHA256": "chain", "EVIDENCE_MANIFEST_SHA256": "manifest"}
        protocol = {key: 1 for key in (
            "envelope_s", "slot_pitch_s", "settle_s", "envelopes", "interior_offset_s",
            "interior_s", "sample_interval_s", "power_interval_ms",
            "start_drift_abort_s", "start_drift_max_s", "window_max_s")}
        stub = str(bench.REPO_ROOT / bench.STUB)
        expected_argv = (stub, "-n", stub, "-setusingnetworktime", "off")

        def run_off(argv, **kwargs):
            self.assertEqual(tuple(argv), expected_argv)
            self.assertNotIn("/usr/bin/sudo", argv)
            self.assertNotIn("/usr/sbin/systemsetup", argv)
            return subprocess.CompletedProcess(argv, 0, network_time_off.EXPECTED_STDOUT, "")

        def execute(plan, passed_protocol, night_dir):
            self.assertEqual(passed_protocol, protocol)
            for key, value in environment.items():
                self.assertEqual(os.environ[key], value)
            # Exercise the current setter and its receipt admission, with only
            # process execution and boot identity mocked. No host command runs.
            path = bench.campaign.establish_network_time_off(night_dir, plan.plan_id)
            receipt = network_time_off.read_receipt(path)
            self.assertEqual(receipt["argv"], list(expected_argv))
            if error is not None:
                raise error
            return 2  # Replayed frames are correctly refused as evidence.

        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            args = SimpleNamespace(archive=tmp, expect_sha=None, smoke=True,
                                   label_shift="none", transaction_merge=None)
            stack.enter_context(mock.patch.dict(os.environ, {replay_env: "previous-archive"}))
            os.environ.pop("NIGHT_PLAN_ID", None)
            before = {key: os.environ.get(key) for key in environment}
            patches = {
                "BENCH_ROOT": root / "bench",
                "require_clean_head": mock.Mock(return_value="synthetic-head"),
                "require_no_night_agent": mock.Mock(),
                "protocol_for": mock.Mock(return_value=protocol),
                "build_plan": mock.Mock(return_value=SimpleNamespace(plan_id="bench-plan")),
                "stage_custody": mock.Mock(return_value=(root / "plan", root / "chain", exports)),
                "machine_state": mock.Mock(return_value={}),
                "bench_environment": mock.Mock(return_value=environment),
                "slot_rows": mock.Mock(return_value=[]),
                "verdict": mock.Mock(return_value={"status": "PASS"}),
            }
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(bench, name, value))
            runner = stack.enter_context(mock.patch.object(network_time_off.subprocess, "run",
                                                          side_effect=run_off))
            stack.enter_context(mock.patch.object(network_time_off, "boot_id", return_value="boot"))
            campaign_execute = stack.enter_context(mock.patch.object(bench.campaign, "execute",
                                                                    side_effect=execute))
            try:
                if error is None:
                    report = bench.execute_bench(args)
                    self.assertEqual(report["returncode"], 2)
                    self.assertEqual(report["kind"], "smoke")
                else:
                    with self.assertRaises(type(error)) as caught:
                        bench.execute_bench(args)
                    self.assertIs(caught.exception, error)
            finally:
                self.assertIs(network_time_off.OFF_ARGV, original_argv)
                self.assertEqual({key: os.environ.get(key) for key in environment}, before)
                self.assertNotIn("NIGHT_PLAN_ID", os.environ)
            campaign_execute.assert_called_once()
            runner.assert_called_once_with(expected_argv, capture_output=True, timeout=30, check=False)

    def test_entrypoint_uses_stub_and_restores_state_on_return(self):
        self.run_bench()

    def test_entrypoint_restores_state_when_campaign_raises(self):
        self.run_bench(RuntimeError("synthetic execution failure"))


if __name__ == "__main__":
    unittest.main()
