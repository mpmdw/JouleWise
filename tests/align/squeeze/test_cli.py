import contextlib
import io
import json
import unittest
from unittest import mock

from joulewise.align.squeeze.__main__ import main

try:
    import numpy as np
except ImportError:
    np = None


class CliTests(unittest.TestCase):
    def test_cohort_size_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(cm.exception.code, 2)

    def test_missing_numpy_reports_optional_extra(self):
        err = io.StringIO()
        with mock.patch.dict("sys.modules", {"numpy": None}), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                main(["--heldout-size", "2"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("optional NumPy extra", err.getvalue())

    @unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
    def test_minimal_synthetic_json(self):
        out = io.StringIO()
        args = ["--heldout-size", "4", "--m", "20", "39", "--hidden-tokens", "0", "256",
                "--residual-sd", "19", "--trials", "8", "--selection-size", "8"]
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(args), 0)
        result = json.loads(out.getvalue())
        self.assertEqual(result["status"], "DRAFT_SYNTHETIC_ONLY_NOT_REGISTERED")
        self.assertEqual(len(result["power"]), 16)
        self.assertEqual(len(result["frontiers"]), 4)
        self.assertEqual({r["heldout_size"] for r in result["power"]}, {4})
        self.assertEqual({r["m"] for r in result["power"]}, {20, 39})

    @unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
    def test_invalid_cohort_refused_before_output(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                main(["--heldout-size", "0", "--trials", "2"])
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
