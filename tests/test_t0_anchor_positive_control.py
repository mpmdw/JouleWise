"""Fixture-only physical-control plumbing; no privileged or hardware calls."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
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
RESYNC = ["/usr/bin/sudo", "/usr/bin/sntp", "-sS", "time.apple.com"]


class PositiveControlTests(unittest.TestCase):
    def setUp(self):
        self.temporary, self.repository, self.pack, self.custody, _, self.inputs = make_t0_fixture()
        self.addCleanup(self.temporary.cleanup)
        self.control = Path(self.temporary.name) / "isolated-control"
        self.movement = 5_000_001
        self.author_calls = []
        self.owner_calls = []
        self.sequence = 0
        self.namespace_defect = False
        self.refusal_defect = None
        self.off_defect = False
        self.on_defect = False

    def stamp(self):
        self.sequence += 1
        raw = SYNTHETIC_MONOTONIC_NS + self.sequence * 1000
        return {"realtime_ns": raw + SYNTHETIC_REALTIME_OFFSET_NS
                + (self.movement if "resync" in self.owner_calls else 0),
                "monotonic_raw_ns": raw, "read_skew_ns": 1000,
                "monotonic_ns": raw, "boot_id": TEST_BOOT_SESSION_ID}

    def owner(self, root, label, argv, timeout):
        self.owner_calls.append(label)
        if label == "off" and self.off_defect:
            raise FileNotFoundError("OFF transcript absent")
        stdout = {"on": "setUsingNetworkTime: On\n", "resync": "resynchronized\n",
                  "off": "Network Time is already off.\n"}[label]
        if label == "on" and self.on_defect:
            stdout = "You need administrator access to run this tool... exiting!\n"
        return {"argv": list(argv), "exit_code": 0, "stdout": stdout, "stderr": "",
                "started": self.stamp(), "finished": self.stamp()}

    def runner(self, argv, *, timeout):
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
                                  custody_root=self.control, resync_argv=RESYNC,
                                  resync_timeout_s=30, sample=self.stamp,
                                  runner=self.runner, owner=self.owner)

    def assert_not_discharged(self, result, reason):
        self.assertEqual(result, {"status": "NOT-DISCHARGED", "reason": reason})
        self.assertFalse((self.control / "positive-control.json").exists())
        self.assertEqual(self.owner_calls[-1], "off")

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
                self.owner_calls.clear()
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
        self.assertEqual(self.owner_calls, ["on", "off"])

    def test_reused_custody_is_not_overwritten(self):
        self.run_control()
        before = (self.control / "custody-manifest.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.run_control()
        self.assertEqual((self.control / "custody-manifest.json").read_bytes(), before)

    def test_resync_vector_is_required_and_closed(self):
        with self.assertRaisesRegex(helper.NotDischarged, "reviewed_resync_recipe_required"):
            helper.run_control(pack_root=self.pack, author_inputs=self.inputs,
                               custody_root=self.control, resync_argv=["/bin/date"], resync_timeout_s=30)
        self.assertFalse(self.control.exists())


if __name__ == "__main__":
    unittest.main()
