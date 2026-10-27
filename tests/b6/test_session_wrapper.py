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
        with patch.object(wrapper, "resolve_inputs") as resolve, patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}) as harvester, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wrapper.main(self.argv), 0)
        overrides = resolve.call_args.kwargs["overrides"]
        self.assertEqual(overrides["identity_pins_path"], self.reg / "identity_pins.json")
        self.assertEqual(overrides["catalog_path"], wrapper.ROOT / "configs/b6/flag_catalog_b6.json")
        self.assertEqual(harvester.call_args.kwargs["registration_paths"],
                         [self.reg / "acceptance.json", self.reg / "identity_pins.json"])
        self.assertEqual(len(out.getvalue().splitlines()), 1)
        result = json.loads(out.getvalue())
        self.assertEqual(result["session_id"], "desk-session")
        self.assertEqual(result["verdict"], "EXCLUDE")
        self.assertEqual(result["export"]["rows"], 9)
        self.assertTrue((self.archive / "withheld/b6-neg8.json").is_file())
        self.assertTrue((self.archive / "derived/b6-flags.jsonl").is_file())
        self.assertTrue(wrapper.harvest is not None)

    def test_smoke_and_reentry_use_one_harvest_and_one_acceptance(self):
        (self.archive / "derived/b6-acceptance.json").unlink()
        with patch.object(wrapper, "resolve_inputs"), \
             patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}) as harvester, \
             patch.object(wrapper, "accept_archive", wraps=wrapper.accept_archive) as acceptance, \
             patch.object(wrapper, "export", wraps=wrapper.export) as exporter, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wrapper.main([*self.argv, "--smoke"]), 0)
            self.assertEqual(wrapper.main([*self.argv, "--smoke"]), 0)
        self.assertTrue(harvester.call_args.kwargs["prepare_desk"])
        self.assertTrue(acceptance.call_args.kwargs["smoke"])
        self.assertTrue(exporter.call_args.kwargs["non_claim"])

    def test_missing_registration_archives_numbers_then_remains_pending(self):
        (self.reg / "acceptance.json").unlink()
        reductions = self.archive / "withheld/reductions"
        before = {p.name: p.read_bytes() for p in reductions.glob('*')}
        with patch.object(wrapper, "resolve_inputs"), \
             patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}) as harvester, \
             patch.object(wrapper, "export", wraps=wrapper.export) as exporter, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(wrapper.main(self.argv), wrapper.PENDING_REGISTRATION)
        harvester.assert_called_once()
        exporter.assert_called_once()
        self.assertEqual(json.loads(output.getvalue())["export"]["rows"], 9)
        self.assertEqual(json.loads(output.getvalue())["verdict"], "UNAVAILABLE")
        record = json.loads((self.archive / 'derived/b6-acceptance.json').read_text())
        self.assertEqual(record['pending'], ['acceptance_registration'])
        self.assertEqual(record['flags'], ['precheck.acceptance_unavailable'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in reductions.glob('*')})

    def test_acceptance_and_export_faults_have_distinct_exit_codes(self):
        for code in (4, 5):
            with patch.object(wrapper, "resolve_inputs"), patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}), \
                 patch.object(wrapper, "accept_archive", **({"side_effect": RuntimeError()} if code == 4 else
                     {"return_value": (type("Result", (), {"record": self.record, "verdict": "ACCEPT"})(), object())})), \
                 patch.object(wrapper, "export", side_effect=RuntimeError()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(wrapper.main(self.argv), code)

    def test_export_key_fault_preserves_filename_without_factor(self):
        with patch.object(wrapper, "resolve_inputs"), patch.object(wrapper, "harvest", return_value={"verdict": "COLLECTED"}), \
             patch.object(wrapper, "accept_archive", return_value=(type("Result", (), {"record": self.record, "verdict": "ACCEPT"})(), object())), \
             patch.object(wrapper, "export", side_effect=ValueError("blinding key unreadable: /synthetic/pack.json")), \
             contextlib.redirect_stderr(io.StringIO()) as stderr, contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(wrapper.main(self.argv), 5)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("blinding key unreadable: /synthetic/pack.json", stderr.getvalue())
