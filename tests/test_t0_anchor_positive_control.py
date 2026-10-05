"""Fixture-only physical-control plumbing; no privileged or hardware calls."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, network_time_off, t0_rehearsal
from joulewise.clock_reference import ClockAnchor
from scripts import author_arm_evidence_t0 as author_cli
from tests.test_arm_readiness_evidence_t0 import (
    make_t0_fixture, author_environment, SYNTHETIC_MONOTONIC_NS,
    SYNTHETIC_REALTIME_OFFSET_NS,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID
from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("g10_helper", os.environ.get(
    "G10_HELPER_PATH", str(ROOT / "scripts/ed_session/capture_t0_anchor_positive_control.py")))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
helper.REPO_ROOT = ROOT
ON_ARGV = (*network_time_off.OFF_ARGV[:-1], "on")


class PositiveControlTests(unittest.TestCase):
    def setUp(self):
        self.temporary, self.repository, self.pack, self.custody, _, self.inputs = make_t0_fixture()
        self.addCleanup(self.temporary.cleanup)
        self.control = Path(self.temporary.name) / "isolated-control"
        self.movement = 5_000_001
        self.author_calls = []
        self.command_calls = []
        self.sequence = 0
        self.namespace_defect = False
        self.refusal_defect = None
        self.off_defect = False
        self.on_defect = False
        self.on_exit = 0
        self.elapsed_ns = 0
        self.sleeps = []
        self.movement_after_s = 0
        self.injected_exception = None
        self.poll_exception = None
        self.on_duration_s = 0
        self.poll_duration_s = 0
        self.command_argv = []

    def stamp(self):
        self.sequence += 1
        raw = SYNTHETIC_MONOTONIC_NS + self.sequence * 1000
        return {"realtime_ns": raw + SYNTHETIC_REALTIME_OFFSET_NS
                + (self.movement if "on" in self.command_calls
                   and self.elapsed_ns >= self.movement_after_s * 1e9 else 0),
                "monotonic_raw_ns": raw, "read_skew_ns": 1000,
                "monotonic_ns": raw, "boot_id": TEST_BOOT_SESSION_ID}

    def monotonic_ns(self):
        return self.elapsed_ns

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.elapsed_ns += round(seconds * 1e9)

    def sample(self):
        # ON has two command stamps; the next sample is the first poll.
        if self.command_calls == ["on"] and self.sequence >= 3:
            if self.poll_exception:
                raise self.poll_exception
            self.elapsed_ns += round(self.poll_duration_s * 1e9)
        return self.stamp()

    def runner(self, argv, *, timeout):
        if tuple(argv) == network_time_off.BOOT_ARGV:
            return subprocess.CompletedProcess(argv, 0, TEST_BOOT_SESSION_ID.encode(), b"")
        if tuple(argv) in (ON_ARGV, network_time_off.OFF_ARGV):
            label = "on" if tuple(argv) == ON_ARGV else "off"
            self.command_calls.append(label)
            self.command_argv.append((tuple(argv), timeout))
            if label == "on":
                self.elapsed_ns += round(self.on_duration_s * 1e9)
                if self.injected_exception:
                    raise self.injected_exception
                stdout = ("You need administrator access to run this tool... exiting!\n"
                          if self.on_defect else "setUsingNetworkTime: On\n")
                return subprocess.CompletedProcess(argv, self.on_exit, stdout.encode(), b"")
            if self.off_defect:
                raise FileNotFoundError("OFF command failed")
            return subprocess.CompletedProcess(argv, 0, b"Network Time is already off.\n", b"")
        if self.injected_exception:
            raise self.injected_exception
        self.author_calls.append(argv)
        stdout, stderr = io.BytesIO(), io.StringIO()
        # CLI writes canonical JSON to sys.stdout.buffer. Everything below
        # executes the actual author; only ambient probes/clocks are fixtures.
        sink = io.TextIOWrapper(stdout, encoding="utf-8", write_through=True)
        endpoint = ClockAnchor(SYNTHETIC_MONOTONIC_NS + SYNTHETIC_REALTIME_OFFSET_NS
                              + self.movement, SYNTHETIC_MONOTONIC_NS, 1000)
        with (author_environment(self.repository, sample_anchor=lambda: endpoint),
              mock.patch.object(author_cli, "REPO_ROOT", self.repository),
              redirect_stdout(sink), redirect_stderr(stderr)):
            rc = author_cli.main(argv[2:])
        raw = stdout.getvalue()
        sink.detach()
        if self.refusal_defect:
            value = readiness.parse_json_bytes(raw)
            if self.refusal_defect == "other_cause_same_code":
                value["detail"] = "T-0 RAW anchor span is below 600000000000 ns"
            else:
                value["reason_codes"] = ["evidence_author_t0_clock_probe_underivable"]
            raw = readiness.render_json(value)
        if self.namespace_defect:
            (self.control / "author-custody" / self.pack.name / "arm_readiness.evidence").mkdir()
        return subprocess.CompletedProcess(argv, rc, raw, stderr.getvalue().encode())

    def run_control(self):
        return helper.run_control(pack_root=self.pack, author_inputs=self.inputs,
                                  custody_root=self.control,
                                  resync_timeout_s=30, sample=self.sample,
                                  runner=self.runner, monotonic_ns=self.monotonic_ns,
                                  sleep=self.sleep)

    def assert_not_discharged(self, result, reason):
        self.assertEqual(result, {"status": "NOT-DISCHARGED", "reason": reason})
        self.assertFalse((self.control / "positive-control.json").exists())
        self.assertEqual(self.command_calls[-1], "off")

    def test_real_author_refusal_and_record_validate_under_evaluate_g10(self):
        result = self.run_control()
        self.assertEqual(result["status"], "DISCHARGED")
        self.assertEqual(len(self.author_calls), 1)
        record = helper.read_json(self.control / "positive-control.json")
        self.assertEqual(set(record), t0_rehearsal._POSITIVE_CONTROL_KEYS)
        receipt = network_time_off.read_receipt(self.control / "network_time_off.json")
        self.assertEqual(receipt["boot_id"], TEST_BOOT_SESSION_ID)
        bundle = fixture_bundle(FixtureBuilder(Path(self.temporary.name) / "rehearsal").build())
        old = bundle.record("positive_control")
        raw = (self.control / "positive-control.json").read_bytes()
        artifact = replace(old, raw=raw, value=record, sha256=readiness.sha256_bytes(raw))
        bundle = replace(bundle, artifacts=tuple(artifact if a == old else a for a in bundle.artifacts))
        self.assertEqual(t0_rehearsal.evaluate_g10(bundle).status, t0_rehearsal.GateStatus.PASS)
        manifest = helper.read_json(self.control / "custody-manifest.json")["files"]
        for path, digest in manifest.items():
            self.assertEqual(readiness.sha256_bytes((self.control / path).read_bytes()), digest)
        self.assertIn("author.stdout.json", manifest)
        self.assertIn("author-execution.json", manifest)
        for path in self.inputs.rglob("*"):
            if path.is_file():
                copy = self.control / "author-custody" / self.pack.name / "arm_readiness.t0.inputs" / path.relative_to(self.inputs)
                self.assertEqual(copy.read_bytes(), path.read_bytes())

    def test_at_or_below_5ms_does_not_discharge_or_run_author(self):
        path = self.inputs / "clock-reference.json"
        capture = helper.read_json(path)
        r0 = readiness.parse_json_bytes(capture["stdout"].encode())
        original = r0["anchor_realtime_ns"]
        for movement in (0, 4_999_999, 5_000_000, -5_000_000):
            with self.subTest(movement=movement):
                # At exactly 5 ms the preserved author's baseline differs by
                # 1 ns: its refusal alone must not discharge the physical step.
                r0["anchor_realtime_ns"] = original + (1 if movement < 0 else -1)
                capture["stdout"] = readiness.render_json(r0).decode()
                path.write_bytes(readiness.render_json(capture))
                self.control = Path(self.temporary.name) / f"control-{movement}"
                self.command_calls.clear()
                self.elapsed_ns = 0
                self.movement = movement
                self.assert_not_discharged(self.run_control(), "anchor_movement_at_or_below_5ms")
                self.assertEqual(self.author_calls, [])

    def test_negative_step_above_bound_also_discharges(self):
        self.movement = -5_000_001
        self.assertEqual(self.run_control()["status"], "DISCHARGED")

    def test_movement_must_also_move_real_author_sequence_above_bound(self):
        path = self.inputs / "clock-reference.json"
        capture = helper.read_json(path)
        r0 = readiness.parse_json_bytes(capture["stdout"].encode())
        r0["anchor_realtime_ns"] -= 4_000_000
        capture["stdout"] = readiness.render_json(r0).decode()
        path.write_bytes(readiness.render_json(capture))
        self.movement = -6_000_000
        self.assert_not_discharged(self.run_control(), "changed_author_sequence_not_above_bound")
        self.assertEqual(self.author_calls, [])

    def test_wrong_refusal_code_fails(self):
        self.refusal_defect = "wrong_code"
        self.assert_not_discharged(self.run_control(), "author_exact_anchor_refusal_missing")

    def test_same_code_for_different_clock_defect_fails(self):
        self.refusal_defect = "other_cause_same_code"
        self.assert_not_discharged(self.run_control(), "author_exact_anchor_refusal_missing")

    def test_pass_namespace_present_fails_even_with_exact_refusal(self):
        self.namespace_defect = True
        self.assert_not_discharged(self.run_control(), "author_pass_namespace_present")

    def test_missing_off_receipt_fails(self):
        self.off_defect = True
        self.assert_not_discharged(self.run_control(), "off_receipt_missing_or_invalid")

    def test_zero_exit_administrator_refusal_does_not_prove_on(self):
        self.on_defect = True
        self.assert_not_discharged(self.run_control(), "network_time_on_not_observed")
        self.assertEqual(self.command_calls, ["on", "off"])

    def test_reused_custody_is_not_overwritten(self):
        self.run_control()
        before = (self.control / "custody-manifest.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.run_control()
        self.assertEqual((self.control / "custody-manifest.json").read_bytes(), before)

    def test_imported_on_vector_and_single_off_through_shared_producer(self):
        with mock.patch.object(network_time_off, "set_network_time_off",
                               wraps=network_time_off.set_network_time_off) as off:
            self.assertEqual(self.run_control()["status"], "DISCHARGED")
        self.assertEqual(helper.ON_ARGV, ON_ARGV)
        self.assertEqual(self.command_argv, [(ON_ARGV, 30), (network_time_off.OFF_ARGV, 30)])
        self.assertEqual(self.command_calls, ["on", "off"])
        off.assert_called_once()
        record = helper.read_json(self.control / "positive-control.json")
        self.assertIs(record["forced_resync"], True)
        self.assertEqual(record["performed_by"], "Ed")
        self.assertGreater(abs(record["anchor_after_ns"] - record["anchor_before_ns"]), 5_000_000)

    def test_nonzero_on_exit_never_discharges_even_if_anchor_moves(self):
        self.on_exit = 1
        self.assert_not_discharged(self.run_control(), "on_command_not_admitted")
        self.assertEqual(self.author_calls, [])
        self.assertEqual(self.command_calls, ["on", "off"])

    def test_polling_waits_for_movement_without_repeating_on(self):
        self.movement_after_s = 10
        self.assertEqual(self.run_control()["status"], "DISCHARGED")
        self.assertEqual(self.sleeps, [5, 5])
        self.assertEqual(self.command_calls, ["on", "off"])
        polls = sorted((self.control / "polls").glob("*.json"))
        self.assertEqual(len(polls), 3)
        before = helper.read_json(self.control / "before.json")
        self.assertEqual([abs(helper.anchor(helper.read_json(p)) - helper.anchor(before))
                          for p in polls], [0, 0, 5_000_001])

    def test_deadline_stops_polling_and_rejects_later_movement(self):
        self.movement_after_s = 31
        self.assert_not_discharged(self.run_control(), "anchor_movement_at_or_below_5ms")
        self.assertEqual(self.elapsed_ns, 30_000_000_000)
        self.assertEqual(self.sleeps, [5] * 6)
        self.assertEqual(len(list((self.control / "polls").glob("*.json"))), 6)
        self.assertEqual(self.author_calls, [])

    def test_on_execution_counts_against_deadline(self):
        self.on_duration_s = 28
        self.movement = 0
        self.assert_not_discharged(self.run_control(), "anchor_movement_at_or_below_5ms")
        self.assertEqual(self.sleeps, [2])
        self.assertEqual(self.elapsed_ns, 30_000_000_000)

    def test_on_uses_remaining_short_timeout_and_cannot_overrun(self):
        self.on_duration_s = 4
        result = helper.run_control(pack_root=self.pack, author_inputs=self.inputs,
                                   custody_root=self.control, resync_timeout_s=3,
                                   sample=self.sample, runner=self.runner,
                                   monotonic_ns=self.monotonic_ns, sleep=self.sleep)
        self.assert_not_discharged(result, "anchor_movement_at_or_below_5ms")
        self.assertEqual(self.command_argv[0], (ON_ARGV, 3))
        self.assertEqual(self.author_calls, [])

    def test_sample_past_deadline_cannot_discharge(self):
        self.poll_duration_s = 31
        self.assert_not_discharged(self.run_control(), "resync_deadline_exceeded")
        self.assertEqual(self.author_calls, [])

    def test_off_after_on_exceptions_and_interrupt(self):
        for error in (OSError("on failed"), subprocess.TimeoutExpired(ON_ARGV, 30),
                      RuntimeError("injected runner failure"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                self.control = Path(self.temporary.name) / type(error).__name__
                self.command_calls.clear()
                self.injected_exception = error
                self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
                self.assertEqual(self.command_calls, ["on", "off"])

    def test_off_after_anchor_probe_exception(self):
        self.poll_exception = RuntimeError("anchor probe failed")
        self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
        self.assertEqual(self.author_calls, [])

    def test_off_after_initial_probe_exception(self):
        with mock.patch.object(self, "sample", side_effect=RuntimeError("initial probe failed")):
            self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
        self.assertEqual(self.command_calls, ["off"])
        receipt = network_time_off.read_receipt(self.control / "network_time_off.json")
        self.assertEqual(receipt["boot_id"], TEST_BOOT_SESSION_ID)

    def test_off_runner_exception_clears_positive_record(self):
        original = self.runner
        def failed_off(argv, *, timeout):
            if tuple(argv) == network_time_off.OFF_ARGV:
                self.command_calls.append("off")
                raise RuntimeError("OFF runner failed")
            return original(argv, timeout=timeout)
        with mock.patch.object(self, "runner", side_effect=failed_off):
            self.assert_not_discharged(self.run_control(), "off_receipt_missing_or_invalid")
        self.assertEqual(self.command_calls, ["on", "off"])

    def test_off_after_author_exception(self):
        original = self.runner
        def failing_author(argv, *, timeout):
            if tuple(argv) not in (ON_ARGV, network_time_off.OFF_ARGV, network_time_off.BOOT_ARGV):
                raise RuntimeError("author failed")
            return original(argv, timeout=timeout)
        with mock.patch.object(self, "runner", side_effect=failing_author):
            self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
        self.assertEqual(self.command_calls, ["on", "off"])

    def test_off_even_when_pre_on_evidence_is_invalid(self):
        (self.inputs / "clock-reference.json").write_text("invalid")
        self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
        self.assertEqual(self.command_calls, ["off"])

    def test_resync_timeout_default_maximum_and_cli_vector_closed(self):
        for timeout in (0, 301, True, 1.5):
            with self.subTest(timeout=timeout):
                with self.assertRaisesRegex(helper.NotDischarged, "resync_timeout_out_of_range"):
                    helper.run_control(pack_root=self.pack, author_inputs=self.inputs,
                                       custody_root=self.control, resync_timeout_s=timeout)
        self.assertFalse(self.control.exists())
        args = ["run", "--pack-root", str(self.pack), "--author-inputs", str(self.inputs),
                "--custody-root", str(self.control)]
        for extra, expected_timeout in (([], 120), (["--resync-timeout-s", "300"], 300)):
            with (mock.patch("builtins.input", return_value="OUTSIDE"),
                  mock.patch.object(helper, "run_control", return_value={"status": "DISCHARGED"}) as run,
                  redirect_stdout(io.StringIO())):
                self.assertEqual(helper.main(args + extra), 0)
                self.assertEqual(run.call_args.kwargs["resync_timeout_s"], expected_timeout)
                self.assertNotIn("resync_argv", run.call_args.kwargs)
        for extra in (["--reviewed-resync-argv", "[]"], ["--resync-timeout-s", "301"]):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                helper.main(args + extra)
            self.assertEqual(caught.exception.code, 2)

    def test_main_reports_exit_two_for_not_discharged(self):
        args = ["run", "--pack-root", str(self.pack), "--author-inputs", str(self.inputs),
                "--custody-root", str(self.control)]
        result = {"status": "NOT-DISCHARGED", "reason": "anchor_movement_at_or_below_5ms"}
        with (mock.patch("builtins.input", return_value="OUTSIDE"),
              mock.patch.object(helper, "run_control", return_value=result),
              redirect_stdout(io.StringIO()) as output):
            self.assertEqual(helper.main(args), 2)
        self.assertEqual(readiness.parse_json_bytes(output.getvalue().encode()), result)


if __name__ == "__main__":
    unittest.main()
