"""Synthetic R0 tests; no retained capture or live hardware is used here."""

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import powermetrics_fiducial as production
from scripts import cap_replay_harness as harness
from tests.test_reduce import self_consistent_calibration


class BlindOutputAssertions:
    def assert_blind_output(self, output, *, report):
        rows = [json.loads(line) for line in output.splitlines()]
        allowed = {
            "capture", "mode", "cells", "need", "median_frame_ms", "ratio",
            "disposition", "trigger", "reason", "replay_failed", "rule_refused",
            "elapsed_s",
        }
        if report:
            allowed.add("stored B reproduced")
        self.assertTrue(rows)
        for row in rows:
            self.assertLessEqual(set(row), allowed)
            # A bound or statistic field fails regardless of its spelling or
            # numeric value: only the explicitly enumerated work data pass.
            self.assertNotIn("b_fiducial_s", row)
            if report:
                self.assertIs(type(row["stored B reproduced"]), bool)


class CapReplayHarnessTests(BlindOutputAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence, cls.raw, cls.events = self_consistent_calibration(
            protocol_id=production.PROTOCOL_ID
        )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.capture = Path(self.temporary.name) / "synthetic-v3"
        (self.capture / "raw").mkdir(parents=True)
        (self.capture / "raw/powermetrics.plist").write_bytes(self.raw)
        (self.capture / "events.jsonl").write_bytes(self.events)
        (self.capture / "instrument_evidence.json").write_text(
            json.dumps(self.evidence), encoding="utf-8"
        )

    def cli(self, mode):
        output = io.StringIO()
        with redirect_stdout(output):
            code = harness.main([mode, str(self.capture)])
        self.assert_blind_output(output.getvalue(), report=mode == "REPORT")
        return code, json.loads(output.getvalue())

    def test_sizing_runs_production_with_only_two_limit_changes(self):
        detector = production.detect_pulses
        calls = []

        def spy(*args, **kwargs):
            calls.append(dict(kwargs))
            return detector(*args, **kwargs)

        with patch.object(production, "detect_pulses", spy):
            code, result = self.cli("SIZING")
            self.assertIs(production.detect_pulses, spy)
        self.assertIs(production.detect_pulses, detector)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["projection_cell_budget"], 5_000_000)
        self.assertEqual(calls[0]["projection_wall_budget_s"], 3_600)
        self.assertEqual(set(calls[0]), {
            "trace_anchor_bound_s", "projection_cell_budget", "projection_wall_budget_s"
        })
        self.assertEqual(result["need"], result["cells"])
        self.assertGreater(result["need"], 0)
        self.assertEqual(result["median_frame_ms"], 100)
        self.assertEqual(result["ratio"], result["cells"] /
                         production.DETECTION_PROJECTION_CELL_BUDGET)
        self.assertEqual(result["disposition"], "valid")

    def test_report_uses_unchanged_defaults_and_boolean_equality(self):
        with patch.object(production, "detect_pulses", wraps=production.detect_pulses) as spy:
            code, result = self.cli("REPORT")
        self.assertEqual(set(spy.call_args.kwargs), {"trace_anchor_bound_s"})
        self.assertEqual(code, 0)
        self.assertTrue(result["stored B reproduced"])
        # R0 defines need only at the raised SIZING limits, never at the
        # production limits used for a harvest report.
        self.assertIsNone(result["need"])
        evidence = dict(self.evidence, b_fiducial_s=123456789.12345)
        (self.capture / "instrument_evidence.json").write_text(json.dumps(evidence))
        code, result = self.cli("REPORT")
        self.assertEqual(code, 0)
        self.assertFalse(result["stored B reproduced"])

    def fake_detection(self, **overrides):
        class NoBoundRead(SimpleNamespace):
            @property
            def b_fiducial_s(self):
                raise AssertionError("SIZING must never access the bound")
        defaults = dict(
            fits=tuple(SimpleNamespace(detected=True) for _ in range(59)),
            all_pulses_detected=True, reasons=(), projection_evaluated_cell_count=101,
            projection_disposition=None, projection_budget_trigger=None,
        )
        defaults.update(overrides)
        return NoBoundRead(**defaults)

    def test_sizing_does_not_decode_stored_bound_or_access_derived_bound(self):
        evidence = dict(self.evidence, b_fiducial_s={"opaque": ["}", "escaped\\\""]},
                        screen_basis={"not_read": "B-derived"})
        (self.capture / "instrument_evidence.json").write_text(json.dumps(evidence))
        inputs = harness._evidence_inputs(json.dumps(evidence).encode(), "SIZING")
        self.assertEqual(set(inputs), {"protocol_id", "clock_anchor", "artifact_sha256"})
        with patch.object(production, "rederive_detection_from_artifacts",
                          return_value=self.fake_detection()):
            code, result = self.cli("SIZING")
        self.assertEqual(code, 0)
        self.assertEqual(result["need"], 101)

    def test_clock_refusal_has_no_need_and_reports_native_median(self):
        with patch.object(production, "rederive_detection_from_artifacts",
                          side_effect=ValueError("calibration trace anchor is unresolved")):
            code, result = self.cli("SIZING")
        self.assertEqual(code, 0)
        self.assertEqual(result["cells"], 0)
        self.assertIsNone(result["need"])
        self.assertEqual(result["disposition"], "clock_anchor_unresolved")
        self.assertEqual(result["median_frame_ms"], 100)

    def test_incomplete_fit_never_supplies_zero_need(self):
        incomplete = self.fake_detection(fits=(), all_pulses_detected=False,
                                         reasons=("pulse_detection_incomplete",))
        with patch.object(production, "rederive_detection_from_artifacts", return_value=incomplete):
            code, result = self.cli("SIZING")
        self.assertEqual(code, 0)
        self.assertIsNone(result["need"])
        self.assertEqual(result["reason"], "pulse_detection_incomplete")

    def test_sizing_limit_refuses_rule_and_deadline_is_failed_replay(self):
        for trigger, count in (("evaluated_cell_budget", 5_000_000), ("wall_deadline", 75)):
            with self.subTest(trigger=trigger):
                stopped = self.fake_detection(
                    fits=(), all_pulses_detected=False,
                    projection_evaluated_cell_count=count,
                    projection_disposition="detection_nonconvergent",
                    projection_budget_trigger=trigger,
                )
                with patch.object(production, "rederive_detection_from_artifacts", return_value=stopped):
                    code, result = self.cli("SIZING")
                self.assertEqual(code, 1)
                self.assertTrue(result["rule_refused"])
                self.assertEqual(result["replay_failed"], trigger == "wall_deadline")
                self.assertIsNone(result["need"])

    def test_raw_tamper_refuses_before_production(self):
        (self.capture / "raw/powermetrics.plist").write_bytes(self.raw + b"tampered")
        with patch.object(production, "rederive_detection_from_artifacts") as spy:
            code, result = self.cli("SIZING")
        spy.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "artifact_hash_mismatch")

    def test_raw_override_keeps_metadata_capture_and_hash_authentication(self):
        external = Path(self.temporary.name) / "retained.plist"
        (self.capture / "raw/powermetrics.plist").rename(external)
        with patch.object(production, "rederive_detection_from_artifacts",
                          return_value=self.fake_detection()):
            result = harness.replay_capture(self.capture, "SIZING", raw_path=external)
        self.assertEqual(result["need"], 101)
        self.assertEqual(result["capture"], str(self.capture))

    def test_dataless_metadata_is_checked_without_reading(self):
        file = SimpleNamespace(
            stat=lambda: SimpleNamespace(st_flags=harness.SF_DATALESS, st_size=100),
            read_bytes=lambda: self.fail("dataless file must not be hydrated"),
        )
        with self.assertRaisesRegex(harness.ReplayInputError, "dataless_file_not_read"):
            harness.retained_bytes(file)

    def test_missing_raw_is_explicit_not_a_zero_need(self):
        (self.capture / "raw/powermetrics.plist").unlink()
        code, result = self.cli("SIZING")
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "bytes_not_retained")
        self.assertIsNone(result["need"])

    def test_exception_text_cannot_leak_an_outcome(self):
        with patch.object(production, "rederive_detection_from_artifacts",
                          side_effect=ValueError("b_fiducial_s=123456789.12345")):
            code, result = self.cli("REPORT")
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "invalid_replay_inputs")

    def test_counterfactual_harness_printing_bound_fails_output_guard(self):
        # Execute a deliberately leaky harness variant through the same CLI
        # path; the output assertion must reject it, not merely search source.
        leaked = {"b_fiducial_s": 123456789.12345, "stored B reproduced": True,
                  "replay_failed": False}
        for mode in ("SIZING", "REPORT"):
            with self.subTest(mode=mode):
                with patch.object(harness, "replay_capture", return_value=leaked):
                    with self.assertRaises(AssertionError):
                        self.cli(mode)


if __name__ == "__main__":
    unittest.main()
