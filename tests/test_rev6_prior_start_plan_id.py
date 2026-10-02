"""Replay window C1's committed Revision 6 records through the prior-record check.

The C2 harvest (2026-10-01) refused on the C1 records: the issuer compared the
start-condition record's plan id (the night plan's, as run_night.py writes it)
with the ledger session's plan id (the calibration plan's). These are the real
C1 bytes as landed by PR #450; only the harvest record's custody root is
rewritten to the test's copy.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import issue_calibration_acceptance_generation as issuer

REPO_ROOT = Path(__file__).resolve().parents[1]
C1_SID = "d079-epoch-25g83-r6-20261001T0617Z"
C1_RECORDS = REPO_ROOT / "docs/process_traces/rev6-windows" / C1_SID
# The calibration plan id the ledger carries for every Revision 6 session.
LEDGER_PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3"


class PriorStartConditionPlanIdTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name).resolve()
        self.custody = base / "custody-root"
        for relative in ("night/start_conditions.json", "harvest/r9_window.json"):
            (self.custody / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(C1_RECORDS / relative, self.custody / relative)
        self.harvest = json.loads((C1_RECORDS / "harvest.json").read_bytes())
        self.harvest["custody_root"] = str(self.custody)
        self.harvest_path = base / "harvest.json"
        self.harvest_path.write_text(json.dumps(self.harvest, sort_keys=True))
        # Empty finalized_slots stops the check at record identity, before the
        # evidence files this replay does not carry.
        self.session = SimpleNamespace(session_id=C1_SID, plan_id=LEDGER_PLAN_ID, finalized_slots={})

    def records(self):
        return issuer.revision_six_records([self.harvest_path], [self.session], {},
                                           repo_root=REPO_ROOT, require_committed=False)

    def test_real_c1_start_record_names_the_night_plan_not_the_ledger_plan(self):
        start = json.loads((self.custody / "night/start_conditions.json").read_bytes())
        self.assertEqual(start["plan_id"], self.harvest["plan_id"])
        self.assertNotEqual(start["plan_id"], LEDGER_PLAN_ID)

    def test_real_c1_records_are_admitted_as_prior_window(self):
        records = self.records()
        self.assertEqual(list(records), [C1_SID])
        self.assertEqual(records[C1_SID]["start"]["result"], "admitted")

    def test_start_record_for_another_night_plan_is_refused(self):
        self.harvest["plan_id"] = "d079-epoch-25g83-r6-derivation-c1-20261001T0137Z"
        self.harvest_path.write_text(json.dumps(self.harvest, sort_keys=True))
        with self.assertRaisesRegex(issuer.PrepareRefusal, "start-condition identity"):
            self.records()


if __name__ == "__main__":
    unittest.main()
