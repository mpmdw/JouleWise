import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import harvest_b6_session as wrapper
from tests.b6.test_export_runs import archive_fixture


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive, self.reg, self.plan, self.record = archive_fixture(self.root)
        self.argv = ["--plan", str(self.root / "plan.json"), "--archive-root", str(self.archive),
                     "--registration-dir", str(self.reg), "--pack-records-root", str(self.root / "packs"),
                     "--export-dir", str(self.root / "export"), "--non-claim"]

    def test_harvest_fault_stops_before_acceptance_and_export(self):
        with patch.object(wrapper, "resolve_inputs"), patch.object(wrapper, "harvest", return_value={"verdict": "HARVEST_FAULT"}), \
             patch.object(wrapper, "accept_archive") as acceptance, patch.object(wrapper, "export") as exporter:
            self.assertEqual(wrapper.main(self.argv), 3)
        acceptance.assert_not_called()
        exporter.assert_not_called()

    def test_success_runs_archive_screen_acceptance_export_one_stdout_line(self):
        (self.archive / "derived/b6-acceptance.json").unlink()
        with patch.object(wrapper, "resolve_inputs") as resolve, patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wrapper.main(self.argv), 0)
        overrides = resolve.call_args.kwargs["overrides"]
        self.assertEqual(overrides["identity_pins_path"], self.reg / "identity_pins.json")
        self.assertEqual(overrides["catalog_path"], wrapper.ROOT / "configs/b6/flag_catalog_b6.json")
        self.assertEqual(len(out.getvalue().splitlines()), 1)
        result = json.loads(out.getvalue())
        self.assertEqual(result["session_id"], "desk-session")
        self.assertEqual(result["verdict"], "EXCLUDE")
        self.assertEqual(result["export"]["rows"], 9)
        self.assertTrue((self.archive / "withheld/b6-neg8.json").is_file())
        self.assertTrue((self.archive / "derived/b6-flags.jsonl").is_file())

    def test_acceptance_and_export_faults_have_distinct_exit_codes(self):
        for code in (4, 5):
            with patch.object(wrapper, "resolve_inputs"), patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}), \
                 patch.object(wrapper, "accept_archive", **({"side_effect": RuntimeError()} if code == 4 else
                     {"return_value": (type("Result", (), {"record": self.record})(), object())})), \
                 patch.object(wrapper, "export", side_effect=RuntimeError()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(wrapper.main(self.argv), code)
