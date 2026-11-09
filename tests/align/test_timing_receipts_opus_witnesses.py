"""Opus cross-family cold review witnesses for the timing receipts (docs/perf/timing-receipts-opus-review.md).

Each test states a property the receipts change must keep and FAILS on
perf/2026-11-08-timing-receipts @ 5fc873136 (and on its merge into
align/2026-11-08-v4-r11 @ 1a2574b49). Witness 1 passes on the pre-receipts v4
head. Synthetic records only: fake clock, temporary directories, no
measurement, custody or restricted record is read.
"""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest


class MemberBundleWitnesses(unittest.TestCase):
    def test_align_member_events_pass_the_bundle_structural_check(self):
        # HIGH-1: every ALIGN member's events.jsonl must still pass the D-025
        # structural events check that validate_bundle (and thus the harvest's
        # strict_problems) applies. Receipts land before the buffered
        # run_started (G0 markers bypass the controller's event buffer) and
        # after run_finalized (the finalize end marker), so both the
        # non-decreasing-timestamp and last-event-is-run_finalized checks fail.
        from joulewise.bundle_read import _check_events
        from scripts import align_v4_w1_synthetic as dry
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'synthetic'
            root.mkdir()
            with redirect_stdout(io.StringIO()):
                dry.collect(SimpleNamespace(variant='kit', inject='all', leak=0.004, members='5'), root)
            bundles = sorted(p.parent for p in (root / 'runs').glob('*/metadata.json'))
            self.assertTrue(bundles)
            for bundle in bundles:
                with self.subTest(bundle=bundle.name):
                    self.assertEqual(_check_events(bundle / 'events.jsonl'), [])


class StageJournalWitnesses(unittest.TestCase):
    def _night(self, tmp):
        custody = Path(tmp) / 'custody'
        night = custody / 'night'
        night.mkdir(parents=True)
        return custody, night, SimpleNamespace(plan_id='W1', hazard_window=None)

    def test_driver_creates_no_stage_journal_before_the_chain(self):
        # HIGH-2a: chain-stages.jsonl is the CHILD chain's journal (chain.py
        # ``>> "$STAGE_JOURNAL"``); the parent never had it open. Opening it
        # before admission creates a new file on every pre-chain refusal
        # (SPEED-TOOLBOX: "Create no new files"), which flips the harvest's
        # "None when the chain wrote no journal" (harvest.py stage_journal),
        # collection_presence and session_structure's required-record check.
        from joulewise import timing_receipts as timing
        from scripts import run_night as driver
        with tempfile.TemporaryDirectory() as tmp:
            _, night, plan = self._night(tmp)
            with driver._timing_journal(night, plan), timing.span('arm', 'refused_admission'):
                pass
            self.assertFalse((night / 'chain-stages.jsonl').exists(),
                             'the driver created the chain stage journal although no chain ran')

    def test_structure_record_stages_carry_no_timing_markers(self):
        # HIGH-2b: session_structure.check (registered for v4) turns every
        # journal row into a public ``stages`` entry. Driver markers in
        # chain-stages.jsonl appear there as null stages.
        from joulewise import session_structure
        from joulewise import timing_receipts as timing
        from scripts import run_night as driver
        with tempfile.TemporaryDirectory() as tmp:
            custody, night, plan = self._night(tmp)
            stage = {"stage_id": "s1", "kind": "campaign_collection", "rc": 0,
                     "started_epoch_s": 1, "ended_epoch_s": 2}
            (night / 'chain-stages.jsonl').write_text(json.dumps(stage) + '\n')  # the chain ran
            with driver._timing_journal(night, plan), timing.span('finalize', 'night_result'):
                pass
            archive = Path(tmp) / 'archive'
            archive.mkdir()
            record = session_structure.check(archive=archive, custody=custody, registration={})
            self.assertEqual([row['stage_id'] for row in record['stages']], ['s1'])


if __name__ == '__main__':
    unittest.main()
