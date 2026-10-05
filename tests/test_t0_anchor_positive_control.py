"""Fixture-only physical-control plumbing; no privileged or hardware calls."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import importlib.util
import io
import itertools
import os
from pathlib import Path
import subprocess
import time
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, kernel_clock, network_time_off, t0_rehearsal, v5_qualification
from tests.test_kernel_clock import frequency_probe
from joulewise.clock_reference import ClockAnchor
from scripts import author_arm_evidence_t0 as author_cli, collect_clock_reference
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
        self.control = Path(self.temporary.name).resolve() / "isolated-control"
        self.movement = 5_000_001
        self.author_calls = []
        self.command_calls = []
        self.sequence = 0
        self.base_ns = SYNTHETIC_MONOTONIC_NS
        self.r0_ns = SYNTHETIC_MONOTONIC_NS - 600_000_000_980
        self.drift_word = 0
        self.frequency = frequency_probe()
        self.after_frequency = self.frequency
        patcher = mock.patch.object(kernel_clock, "read_kernel_frequency", side_effect=lambda: self.after_frequency)
        patcher.start()
        self.addCleanup(patcher.stop)
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
        # Anchor refusal is independent of plan/dispatch sizing replay. Keep
        # the binding in custody and inject only that separately tested seam.
        (self.inputs / "kernel-frequency-binding.json").write_bytes(
            readiness.render_json({"fixture": "sizing supplied by injected replay"}))

    def stamp(self):
        self.sequence += 1
        raw = self.base_ns + self.elapsed_ns + self.sequence * 1000
        from fractions import Fraction
        drift = round(Fraction(self.drift_word * (raw - self.r0_ns), 65536 * 10**6))
        return {"realtime_ns": raw + SYNTHETIC_REALTIME_OFFSET_NS + drift
                + (self.movement if "on" in self.command_calls
                   and self.elapsed_ns >= self.movement_after_s * 1e9 else 0),
                "monotonic_raw_ns": raw, "read_skew_ns": 1000,
                "monotonic_ns": self.base_ns + self.elapsed_ns, "boot_id": TEST_BOOT_SESSION_ID,
                "kernel_frequency": self.after_frequency if "on" in self.command_calls else self.frequency}

    def monotonic_ns(self):
        return self.base_ns + self.elapsed_ns

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.elapsed_ns += round(seconds * 1e9)

    def sample(self):
        # Preflight and ON each have two stamps, with before.json between.
        if self.command_calls == ["on"] and self.sequence >= 5:
            if self.poll_exception:
                raise self.poll_exception
            self.elapsed_ns += round(self.poll_duration_s * 1e9)
        return self.stamp()

    def runner(self, argv, *, timeout):
        if tuple(argv) == helper.preflight_argv(self.repository):
            self.assertEqual(timeout, 30)
            raw = itertools.count(self.base_ns + self.elapsed_ns + self.sequence * 1000 + 1)
            def clock(clock_id):
                return next(raw) + (SYNTHETIC_REALTIME_OFFSET_NS
                                    if clock_id == time.CLOCK_REALTIME else 0)
            def sntp(command):
                return subprocess.CompletedProcess(command, 0,
                    f"+0.020 +/- 0.001 {command[-1]} 192.0.2.1\n".encode(), b"")
            stream = io.BytesIO()
            collect_clock_reference.main([], runner=sntp, clock_gettime_ns=clock,
                boot_session_id_reader=lambda: TEST_BOOT_SESSION_ID, stdout=stream)
            return subprocess.CompletedProcess(argv, 0, stream.getvalue(), b"")
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
        from fractions import Fraction
        drift = round(Fraction(self.drift_word * (self.base_ns - self.r0_ns), 65536 * 10**6))
        endpoint = ClockAnchor(self.base_ns + SYNTHETIC_REALTIME_OFFSET_NS
                              + drift + self.movement, self.base_ns, 1000)
        with (author_environment(self.repository, sample_anchor=lambda: endpoint,
                                  now_monotonic_ns=self.base_ns, kernel_frequency=self.after_frequency),
              mock.patch.object(author_cli, "REPO_ROOT", self.repository),
              mock.patch.object(v5_qualification, "authenticated_clock_budget", return_value=(320., ())),
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
        with mock.patch.object(helper, "REPO_ROOT", self.repository):
            return helper.run_control(pack_root=self.pack, author_inputs=self.inputs,
                                      custody_root=self.control,
                                      resync_timeout_s=30, sample=self.sample,
                                      runner=self.runner, monotonic_ns=self.monotonic_ns,
                                      sleep=self.sleep)

    def assert_not_discharged(self, result, reason):
        self.assertEqual(result, {"status": "NOT-DISCHARGED", "reason": reason})
        self.assertFalse((self.control / "positive-control.json").exists())
        self.assertEqual(self.command_calls[-1], "off")

    def verify_custody(self):
        head = subprocess.check_output(["git", "-C", str(self.repository), "rev-parse", "HEAD"], text=True).strip()
        return helper.verify_g10_custody(self.control / "positive-control.json",
            self.control / "custody-manifest.json", code_root=self.repository, head=head,
            before_monotonic_ns=self.base_ns + self.elapsed_ns + 1_000_000_000,
            after_monotonic_ns=self.base_ns - 1,
            boot_id=TEST_BOOT_SESSION_ID)

    def test_custody_verifier_binds_supports_boot_code_and_order(self):
        self.assertEqual(self.run_control()["status"], "DISCHARGED")
        # The verifier and file census are real; only capture probes are synthetic.
        self.assertEqual(self.verify_custody()["performed_by"], "Ed")
        path = self.control / "before.json"
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        with self.assertRaisesRegex(ValueError, "g10_custody_hash_or_census"):
            self.verify_custody()
        path.write_bytes(raw)
        head = subprocess.check_output(["git", "-C", str(self.repository), "rev-parse", "HEAD"], text=True).strip()
        with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
            helper.verify_g10_custody(self.control / "positive-control.json", self.control / "custody-manifest.json",
                code_root=self.repository, head=head, before_monotonic_ns=SYNTHETIC_MONOTONIC_NS,
                boot_id=TEST_BOOT_SESSION_ID)

    def test_pre_on_span_guard_refuses_before_on_but_still_runs_off(self):
        self.elapsed_ns = 3500_000_000_000
        self.assert_not_discharged(self.run_control(), "pre_on_author_span_out_of_range")
        self.assertNotIn("on", self.command_calls)

    def test_sigterm_unwinds_through_off_and_restores_handler(self):
        import signal
        previous = signal.getsignal(signal.SIGTERM)
        original = self.runner
        def interrupted(argv, *, timeout):
            if tuple(argv) == ON_ARGV:
                signal.raise_signal(signal.SIGTERM)
            return original(argv, timeout=timeout)
        self.runner = interrupted
        result = self.run_control()
        self.assertEqual(result["status"], "NOT-DISCHARGED")
        self.assertEqual(self.command_calls[-1], "off")
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)

    def test_first_sigterm_during_off_cannot_interrupt_the_setter(self):
        import signal
        previous = signal.getsignal(signal.SIGTERM)
        original = self.runner
        def interrupted(argv, *, timeout):
            if tuple(argv) == network_time_off.OFF_ARGV:
                signal.raise_signal(signal.SIGTERM)
            return original(argv, timeout=timeout)
        self.runner = interrupted
        self.assertEqual(self.run_control()["status"], "DISCHARGED")
        self.assertEqual(self.command_calls[-1], "off")
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)
        self.verify_custody()

    def test_real_author_refusal_and_record_validate_under_evaluate_g10(self):
        result = self.run_control()
        self.assertEqual(result["status"], "DISCHARGED")
        self.assertEqual(len(self.author_calls), 1)
        record = helper.read_json(self.control / "positive-control.json")
        self.assertEqual(set(record), t0_rehearsal._POSITIVE_CONTROL_KEYS)
        receipt = network_time_off.read_receipt(self.control / "network_time_off.json")
        self.assertEqual(receipt["boot_id"], TEST_BOOT_SESSION_ID)
        bundle = fixture_bundle(FixtureBuilder(Path(self.temporary.name).resolve() / "rehearsal").build())
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

    def test_real_resync_shape_after_1600_seconds_of_drift_still_discharges(self):
        self.frequency = frequency_probe(-207749)
        self.after_frequency = frequency_probe(-190000)
        self.drift_word = -207749
        self.base_ns = self.r0_ns + 1600 * 10**9
        self.movement = 500_000_000
        capture_path = self.inputs / "clock-reference.json"
        capture = helper.read_json(capture_path)
        capture.update(kernel_frequency=self.frequency, t_stream_max_s=320.)
        capture_path.write_bytes(readiness.render_json(capture))
        result = self.run_control()
        self.assertEqual(result["status"], "DISCHARGED", result)
        self.assertEqual(helper.read_json(self.control / "author.stdout.json")["detail"], helper.ANCHOR_DETAIL)
        self.assertGreater(helper.read_json(self.control / "anchor-movement.json")["residual_movement_ns"], 5_000_000)
        self.assertEqual(helper.read_json(self.control / "kernel-frequency-after-off.json"), self.after_frequency)
        self.verify_custody()

    def test_pre_on_changed_word_refuses_without_spending_on(self):
        capture_path = self.inputs / "clock-reference.json"
        capture = helper.read_json(capture_path)
        capture["kernel_frequency"] = frequency_probe(1)
        capture_path.write_bytes(readiness.render_json(capture))
        self.assert_not_discharged(self.run_control(), "pre_on_kernel_frequency_changed")
        self.assertEqual(self.command_calls, ["off"])

    def test_residual_control_discharges_when_steady_drift_cancels_raw_movement(self):
        self.frequency = frequency_probe(-207749)
        self.after_frequency = frequency_probe(-190000)
        self.drift_word = -207749
        self.on_duration_s = 1
        capture_path = self.inputs / "clock-reference.json"
        capture = helper.read_json(capture_path)
        capture.update(kernel_frequency=self.frequency, t_stream_max_s=320.)
        capture_path.write_bytes(readiness.render_json(capture))
        result = self.run_control()
        self.assertEqual(result["status"], "DISCHARGED", result)
        movement = helper.read_json(self.control / "anchor-movement.json")
        self.assertLess(movement["absolute_movement_ns"], 5_000_000)
        self.assertGreater(movement["residual_movement_ns"], 5_000_000)
        self.verify_custody()
        bundle = fixture_bundle(FixtureBuilder(Path(self.temporary.name).resolve() / "rehearsal").build())
        old = bundle.record("positive_control")
        raw = (self.control / "positive-control.json").read_bytes()
        positive = replace(old, path=self.control / "positive-control.json", raw=raw,
            value=helper.read_json(self.control / "positive-control.json"), sha256=readiness.sha256_bytes(raw))
        support = []
        for name in ("before.json", "after.json", "anchor-movement.json"):
            path = self.control / name
            raw = path.read_bytes()
            support.append(t0_rehearsal.EvidenceArtifact("physical-control/" + name,
                path, raw, readiness.sha256_bytes(raw), helper.read_json(path)))
        bundle = replace(bundle, artifacts=tuple(positive if a == old else a for a in bundle.artifacts) + tuple(support))
        result = t0_rehearsal.evaluate_g10(bundle)
        self.assertEqual(result.status, t0_rehearsal.GateStatus.PASS, result.message)

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
        with mock.patch.object(helper, "REPO_ROOT", self.repository):
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
        # The first control probe follows the two preflight stamps. A failure
        # here must still unwind OFF after admission of the measured offset.
        original = self.sample
        def failed_control_probe():
            if self.sequence == 2:
                raise RuntimeError("initial control probe failed")
            return original()
        with mock.patch.object(self, "sample", side_effect=failed_control_probe):
            self.assert_not_discharged(self.run_control(), "control_evidence_invalid")
        self.assertEqual(self.command_calls, ["off"])
        receipt = network_time_off.read_receipt(self.control / "network_time_off.json")
        self.assertEqual(receipt["boot_id"], TEST_BOOT_SESSION_ID)

    def test_preflight_initial_probe_exception_is_non_spending(self):
        with mock.patch.object(self, "sample", side_effect=RuntimeError("preflight probe failed")):
            self.assertEqual(self.run_control(), {"status": "NOT-DISCHARGED",
                "reason": "control_evidence_invalid", "g10_attempt": False})
        self.assertEqual(self.command_calls, [])
        self.assertFalse((self.control / "positive-control.json").exists())
        self.assertFalse((self.control / "author-custody").exists())

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
            if len(argv) > 1 and Path(argv[1]).name == "author_arm_evidence_t0.py":
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
