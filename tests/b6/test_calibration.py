import dataclasses
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import calibration, registration
from tests.b6.support import document, registration_dir


class CalibrationTests(unittest.TestCase):
    def evaluate(self, pre, post, **kwargs):
        return calibration.evaluate(calibration.Capture(Decimal(pre), "valid"),
                                    calibration.Capture(Decimal(post), "valid"), document(),
                                    kwargs.get("rows", []), kwargs.get("own", ("own",)),
                                    kwargs.get("changed", False))

    def test_worked_40_30(self):
        result = self.evaluate(".0400", ".0300")
        self.assertEqual(Decimal(result["drift_s"]), Decimal(".0100"))
        self.assertEqual(Decimal(result["allowance_s"]), Decimal(".014531"))
        self.assertEqual(Decimal(result["operative_bound_s"]), Decimal(".054531"))
        self.assertEqual(sum(x["code"] == "calibration.alignment_above_reference" for x in result["flags"]), 1)
        self.assertEqual(result["excluding"], [])

    def test_worked_28_48(self):
        result = self.evaluate(".0280", ".0480")
        self.assertEqual(Decimal(result["operative_bound_s"]), Decimal(".0680"))
        self.assertEqual(Decimal(result["allowance_s"]), Decimal(".0200"))
        self.assertIn("calibration.drift_above_budget", [x["code"] for x in result["flags"]])
        self.assertEqual(result["excluding"], [])

    def test_strict_stop_line(self):
        self.assertEqual(self.evaluate(".060", ".028")["excluding"], [])
        result = self.evaluate(".060", ".0279")
        self.assertEqual(Decimal(result["operative_bound_s"]), Decimal(".0921"))
        self.assertEqual(result["excluding"], ["calibration.operative_bound_above_stop"])

    def test_post_absent_or_refit_failed_is_incomplete(self):
        for status in ("absent", "refit_failed"):
            result = calibration.evaluate(calibration.Capture(Decimal(".028"), "valid"),
                                          calibration.Capture(None, status), document(), [], (), False)
            self.assertIsNone(result["operative_bound_s"])
            self.assertEqual(result["excluding"], ["calibration.bracket_incomplete"])

    def test_other_sessions_and_doubling_never_change_bound(self):
        rows = [{"seq": i, "session_id": "other", "value_s": ".080", "disposition": "valid"}
                for i in range(48)]
        rows += [{"seq": 100, "session_id": "other", "disposition": "systematic-invalid"},
                 {"seq": 101, "session_id": "own", "disposition": "systematic-invalid"}]
        result = self.evaluate(".028", ".028", rows=rows, changed=True)
        self.assertEqual(result["operative_bound_s"], self.evaluate(".028", ".028")["operative_bound_s"])
        flags = {x["code"]: x for x in result["flags"]}
        self.assertEqual(flags["calibration.other_session_systematic"]["sequences"], [100])
        self.assertEqual(flags["calibration.corpus_doubling_reached"]["count"], 48)
        self.assertEqual(flags["calibration.corpus_doubling_reached"]["threshold"], 48)
        self.assertIn("calibration.other_session_range_expansion", flags)
        self.assertIn("calibration.estimator_code_changed", flags)
        self.assertEqual(result["excluding"], [])

    def test_null_stop_line_discloses(self):
        reg = document()
        reg["calibration"]["operative_bound_stop_s"] = None
        result = calibration.evaluate(calibration.Capture(Decimal("1"), "valid"),
                                      calibration.Capture(Decimal("1"), "valid"), reg, [], (), False)
        self.assertEqual(result["excluding"], [])
        self.assertIn("calibration.stop_line_unregistered", [x["code"] for x in result["flags"]])

    def test_read_own_capture_exact_lexeme_and_refit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "raw/powermetrics.plist").write_bytes(b"synthetic raw")
            (root / "events.jsonl").write_bytes(b"synthetic events")
            (root / "instrument_evidence.json").write_text('{"b_fiducial_s":0.028000000000000001,"status":"valid"}')
            with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics", return_value=.028) as refit:
                capture = calibration.read_own_capture(root)
            self.assertEqual(capture.value_s, Decimal(".028000000000000001"))
            self.assertEqual(refit.call_args.args[1:], (b"synthetic raw", b"synthetic events"))
            with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics", return_value=.030):
                self.assertEqual(calibration.read_own_capture(root).value_s, Decimal(".03"))
            with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics", side_effect=ValueError("refit failed")):
                self.assertEqual(calibration.read_own_capture(root).status, "refit_failed")
            self.assertEqual(calibration.read_own_capture(root / "absent").status, "absent")

    def test_registration_defaults_and_faults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = registration_dir(Path(tmp))
            value = json.loads((root / "acceptance.json").read_text())
            value.pop("neg8")
            (root / "acceptance.json").write_text(json.dumps(value))
            reg = registration.load(root)
            self.assertEqual(reg["neg8"], {"corpus_minimum": 6, "corpus_cap": 12,
                                           "planned": {"start": 3, "midpoint": 1, "end": 3}})
            self.assertIn("catalog", reg["defaults_used"])
            self.assertIn("neg8", reg["defaults_used"])
            self.assertEqual(reg["calibration"]["alignment_reference_s"], Decimal(".036462861644980"))
            (root / "acceptance.json").write_text("not JSON")
            with self.assertRaises(ValueError):
                registration.load(root)
