"""Synthetic regressions for the Tier 2 custody audit."""

import errno
import fcntl
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("frozen_machine", ROOT / "tests/test_hp02_gate_machine.py")
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)
BASE = machine.BASE


class CustodyAudit(unittest.TestCase):
    def desk(self, root):
        desk = machine.Desk(Path(root))
        desk.args.queue_hold_root = Path(root) / "independent-queue-custody"
        return desk

    def prepare(self, desk, phase):
        if phase == "Issue":
            desk.publish("PROPOSED")
        else:
            desk.publish("ISSUED")
        if phase == "Run":
            self.assertTrue(machine.acceptable(desk.call("Start", BASE)))

    def queue_hold(self, desk):
        holds = desk.ledger()[0]
        queue_sha, queue_seq = machine.records.position(desk)
        queue_holds = {key: row for key, row in holds.items()
                       if (row.get("queue_sha"), row.get("queue_seq")) == (queue_sha, queue_seq)}
        self.assertEqual(len(queue_holds), 1, holds)
        hold = next(iter(queue_holds.values()))
        failed = hold["failed_read"]
        self.assertEqual(failed["ledger_sequence"], hold["ledger_sequence"])
        self.assertEqual(machine.digest(machine.records.canonical(failed)), hold["source_digest"])
        self.assertEqual(hold["decision"], "HOLD_UNKNOWN")
        return queue_holds

    def recover(self, desk, holds, variant="resampled-same-source"):
        self.assertEqual(desk.calls, [])
        row = desk.row("Start", BASE + 10, variant)
        row["hold_dispositions"] = machine.proof_rows(desk, holds, BASE + 10, "valid")
        first = desk.call("Start", BASE + 10, row)
        self.assertTrue(machine.acceptable(first), first)
        run = desk.call("Run", BASE + 11, desk.row("Run", BASE + 11, variant))
        self.assertTrue(machine.acceptable(run), run)
        self.assertEqual(len(desk.calls), 1)
        opened, closed, _ = desk.ledger()
        self.assertLessEqual(holds.keys(), closed.keys())
        self.assertTrue(holds.keys().isdisjoint(opened))

    def test_interrupted_read_survives_issue_replacement(self):
        class Interrupted(BaseException):
            pass

        cases = (("Start", "read_records", False), ("Start", "read_records", True),
                 ("Issue", "read_records", True), ("Run", "read_records", True),
                 ("Start", "remember", True))
        for phase, stage, primary_lost in cases:
            with self.subTest(phase=phase, stage=stage, primary_lost=primary_lost), TemporaryDirectory() as root, self.desk(root) as desk:
                self.prepare(desk, phase)
                with patch.object(machine.hp.GateInvocation, stage, side_effect=Interrupted):
                    with self.assertRaises(Interrupted):
                        desk.call(phase, BASE + 1)
                self.assertFalse(desk.calls)
                if primary_lost:
                    desk.args.custody.rename(desk.args.custody.with_name("lost-primary"))
                desk.issue["record"] += " replacement"
                desk.publish("ISSUED")
                row = desk.row("Start", BASE + 2)
                row["fence_clear"] = False  # The interrupted read must take precedence and be recorded.
                first = desk.call("Start", BASE + 2, row)
                self.assertEqual(first["decision"], "HOLD_UNKNOWN", first)
                holds = self.queue_hold(desk)
                self.assertIn("flight", next(iter(holds.values()))["failed_read"]["source"])
                self.assertTrue(machine.refused(desk.call("Start", BASE + 3)))
                self.assertLessEqual(holds.keys(), self.queue_hold(desk).keys())
                bad = desk.row("Start", BASE + 4)
                bad["hold_dispositions"] = machine.proof_rows(desk, holds, BASE + 4, "wrong-source")
                self.assertTrue(machine.refused(desk.call("Start", BASE + 4, bad)))
                self.assertLessEqual(holds.keys(), self.queue_hold(desk).keys())
                self.recover(desk, holds)

    def test_issue_lock_failures_use_queue_custody(self):
        for phase in ("Issue", "Start", "Run"):
            for fault in ("open", "acquire"):
                with self.subTest(phase=phase, fault=fault), TemporaryDirectory() as root, self.desk(root) as desk:
                    self.prepare(desk, phase)
                    original_open, original_flock = Path.open, fcntl.flock

                    def fail_open(path, *args, **kwargs):
                        if path.name == "arm.lock":
                            raise OSError(errno.EIO, "synthetic issue lock open error")
                        return original_open(path, *args, **kwargs)

                    def fail_acquire(handle, operation):
                        if Path(handle.name).name == "arm.lock":
                            raise OSError(errno.EIO, "synthetic issue lock acquisition error")
                        return original_flock(handle, operation)

                    injected = (patch.object(Path, "open", fail_open) if fault == "open"
                                else patch.object(fcntl, "flock", fail_acquire))
                    with injected:
                        first = desk.call(phase, BASE + 1)
                    self.assertEqual(first["decision"], "HOLD_UNKNOWN", first)
                    holds = self.queue_hold(desk)
                    failure = next(iter(holds.values()))["failed_read"]
                    self.assertEqual(failure["error_class"], "OSError")
                    self.assertIn("lock", failure["source"])
                    desk.issue["record"] += " replacement"
                    desk.publish("ISSUED")
                    self.assertTrue(machine.refused(desk.call("Start", BASE + 2)))
                    self.recover(desk, holds)

    def test_shared_close_refusals_latch_even_with_another_block(self):
        for fault in ("older", "same-time-different-receipt", "older-and-fence"):
            with self.subTest(fault=fault), TemporaryDirectory() as root, self.desk(root) as desk:
                desk.issue["latest_close_at_issue"] = "fixture-close-19"
                desk.publish("PROPOSED")
                first = desk.call("Issue", BASE, desk.row("Issue", BASE, "replacement-source"))
                self.assertTrue(machine.acceptable(first), first)
                desk.publish("ISSUED")
                row = desk.row("Start", BASE + 1)
                if fault == "same-time-different-receipt":
                    machine.close(row, "conflicting-close", BASE - 1195, "b" * 64)
                if fault == "older-and-fence":
                    row["fence_clear"] = False
                self.assertTrue(machine.refused(desk.call("Start", BASE + 1, row)))
                holds = desk.ledger()[0]
                self.assertTrue(any("issue_id" in h and h["decision"] == "WAIT_EVIDENCE"
                                    and h["source_digest"] == row["latest_close"]["receipt_sha256"]
                                    for h in holds.values()), holds)
                step = desk.call("Start", BASE + 2, desk.row("Start", BASE + 2, "replacement-source"))
                self.assertTrue(machine.refused(step), step)
                self.assertLessEqual(holds.keys(), desk.ledger()[0].keys())
                self.recover(desk, holds, "replacement-source")


if __name__ == "__main__":
    machine.DRAFTS = ROOT / machine.REL
    machine.ITEMS = json.loads((machine.DRAFTS / "hp-02/items.json").read_bytes())
    with TemporaryDirectory(prefix="hp02-audit-") as scratch:
        with ZipFile(machine.DRAFTS / "hp-02/fixtures/hp02-occupancy-fixture.zip") as bundle:
            bundle.extractall(scratch)
        machine.PIN = Path(scratch) / "tmp/pin"
        sys.path.insert(0, str(machine.PIN))
        machine.hp = machine.load_gate()
        sys.addaudithook(machine.native_guard)
        outcome = unittest.main(exit=False).result
        print(f"native command attempts: {len(machine.NATIVE)}")
        sys.exit(not outcome.wasSuccessful() or bool(machine.NATIVE))
