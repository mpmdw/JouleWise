"""Shared disk scanner fixtures; every path stays under TemporaryDirectory."""
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.zero_capture_facts import zero_capture_facts


class ZeroCaptureFactsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.custody = self.root / "night-custody" / "predecessor"
        night = self.custody / "night"
        night.mkdir(parents=True)
        self.chain = self.custody / "chain.zsh"
        self.chain.write_text("export NIGHT_PAYLOAD_KIND='quiet_predicate_evidence'\n")
        (night / "courier.sent").write_text("message-id\n")
        (night / "result.json").write_text(json.dumps({"verdict": "REFUSED"}))
        (night / "receipt.json").write_text(json.dumps({"verdict": "REFUSED"}))
        self.plan = SimpleNamespace(custody_root=str(self.custody), chain_path=str(self.chain),
                                    plan_id="predecessor")

    def test_clean_record_is_immutable_and_missing_root_refuses(self):
        facts = zero_capture_facts(self.plan)
        self.assertTrue(facts.clean)
        self.assertEqual((facts.envelopes_captured, facts.reservation_markers_found), (0, 0))
        with self.assertRaises(FrozenInstanceError):
            facts.chain_started = 1
        self.assertFalse(zero_capture_facts(SimpleNamespace(custody_root=str(self.root / "missing"),
            chain_path=str(self.chain), plan_id="predecessor")).clean)

    def test_f5_missing_courier_marker_is_a_false_fact_never_clean(self):
        (self.custody / "night" / "courier.sent").unlink()
        facts = zero_capture_facts(self.plan)
        self.assertFalse(facts.courier_sent)
        self.assertFalse(facts.scan_complete)
        self.assertFalse(facts.clean)

    def test_nested_marker_and_symlinked_directory_are_present(self):
        marker = self.custody / "deep" / "nested" / "one.consumed.json"
        marker.parent.mkdir(parents=True)
        marker.write_text("{}")
        self.assertEqual(zero_capture_facts(self.plan).reservation_markers_found, 1)
        marker.unlink()
        (self.custody / "deep" / "link").symlink_to(self.root / "missing")
        self.assertFalse(zero_capture_facts(self.plan).clean)

    def test_index_and_capture_entries(self):
        index = self.custody / "night" / "evidence_envelopes.jsonl"
        index.write_text('{"index": 1, "collector_exit": 0}\n')
        self.assertEqual(zero_capture_facts(self.plan).envelopes_captured, 1)
        index.write_text("")
        (self.custody / "night" / "evidence").symlink_to(self.root / "missing")
        self.assertEqual(zero_capture_facts(self.plan).capture_entries_found, 1)

    def test_calibration_shared_ledger_does_not_change_clean_facts(self):
        ledger = self.root / "ledger.jsonl"
        runs = self.root / "runs"
        self.chain.write_text(f"export RUNS_ROOT='{runs}'\nexport CALIBRATION_LEDGER='{ledger}'\n")
        ledger.write_text(json.dumps({"plan_id": "frozen-calibration-plan"}) + "\n" + "{torn\n")
        self.assertTrue(zero_capture_facts(self.plan).clean)
        (self.custody / "night/chain.started").write_text("{}")
        self.assertFalse(zero_capture_facts(self.plan).clean)


if __name__ == "__main__":
    unittest.main()
