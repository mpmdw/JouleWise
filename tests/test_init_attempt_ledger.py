"""Synthetic RL-197c initialization against the two frozen launcher readers."""

from contextlib import redirect_stderr, redirect_stdout
import fcntl
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import init_attempt_ledger as init


PIN_B = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
CTL_PIN = "f45e22e4efa6b48dd05f099f39eb62246e324177"
SPAN = "synthetic-inaugural-a1"
CLOSE_NS = 1_795_000_000_000_000_001
READER = """
import sys
sys.path.insert(0, sys.argv.pop(1))
from scripts.launch_cadence_span import main
sys.exit(main(sys.argv[1:]))
"""


def sparse_checkout(pin, directory):
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", "--single-branch", "--no-tags",
                    init.ROOT, directory], check=True)
    subprocess.run(["git", "-C", directory, "sparse-checkout", "set", "--no-cone", "/joulewise/",
                    "/scripts/__init__.py", "/scripts/launch_align_r0.py", "/scripts/launch_cadence_span.py",
                    "/scripts/cadence_legs_runner.py"], check=True)
    subprocess.run(["git", "-C", directory, "checkout", "--quiet", "--detach", pin], check=True)
    return directory


class InitAttemptLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.checkouts = Path(temporary.name).resolve()
        cls.pin_b = sparse_checkout(PIN_B, cls.checkouts / "pin-b")
        cls.ctl = sparse_checkout(CTL_PIN, cls.checkouts / "ctl")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.desk = self.root / "desk"
        self.desk.mkdir()
        self.lock = self.desk / ".desk-fence.lock"
        self.lock.touch()
        self.receipt = self.root / "synthetic receipt.json"
        self.ledger = self.root / "attempts.json"
        self.sidecar = self.root / "attempts.json.first-row.json"
        self.close_record = {
            "schema": "joulewise.cadence_span_receipt.v1", "span_id": SPAN, "ended": {"epoch_ns": CLOSE_NS},
            "steps": [{"name": "restore", "rc": 0, "result": {"ok": True, "exit_code": 0, "observed": 0}}],
            "feeds": {},
        }
        for name in ("agents", "meter", "volumes"):
            self.close_record["steps"].append({"name": f"stop-{name}", "rc": 0, "result": {"proven_stopped": True}})
            self.close_record["feeds"][name] = {"stop": {"rc": 0, "proven_stopped": True}}
        self.write_receipt()
        self.enterContext(patch.dict(os.environ, {
            "CLOSE_PROOF_RECEIPT": str(self.receipt), "HOST_RESTORE_OK": "1", "FEEDS_STOPPED": "1",
            "GROUPS_ABSENT": "1", "FOREIGN_PROCESSES_ABSENT": "1",
        }))
        self.pid_alive = self.enterContext(patch.object(init.desk, "pid_alive", return_value=True))

    def write_receipt(self):
        self.receipt.write_text(json.dumps(self.close_record))

    def snapshot(self):
        return {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def run_initializer(self, **overrides):
        args = {"ledger": self.ledger, "custody-root": self.desk, "close-receipt": self.receipt,
                "ctl-checkout": self.ctl, "python-bin": sys.executable, "span-id": SPAN,
                "receipt-sha256": sha256(self.receipt.read_bytes()).hexdigest(),
                "close-ns": CLOSE_NS, "run-state-item": 123}
        args.update(overrides)
        argv = [token for name, value in args.items() for token in (f"--{name}", str(value))]
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            code = init.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_refusal(self, message, **overrides):
        before = self.snapshot()
        code, stdout, stderr = self.run_initializer(**overrides)
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn(message, stderr)
        self.assertEqual(self.snapshot(), before)

    def test_first_row_and_sidecar_are_accepted_by_both_pinned_readers(self):
        before = self.snapshot()
        code, stdout, stderr = self.run_initializer()
        self.assertEqual((code, stderr), (0, ""))
        # The append writers serialize with default json.dump and a trailing newline.
        expected = f'{{"attempts": [{{"span_id": "{SPAN}", "close_receipt": {json.dumps(str(self.receipt))}, "sequence": 1}}]}}\n'
        ledger = expected.encode()
        digest = sha256(ledger).hexdigest()
        proof = f"{SPAN}\n{CLOSE_NS}\n{self.receipt}\n"
        self.assertEqual(self.ledger.read_bytes(), ledger)
        self.assertEqual(stdout, digest + "\n")
        self.assertEqual(json.loads(self.sidecar.read_bytes()), {
            "ruling": "RL-197c", "run_state_item": 123, "span_id": SPAN, "close_receipt": str(self.receipt),
            "receipt_sha256": sha256(self.receipt.read_bytes()).hexdigest(), "close_ns": CLOSE_NS,
            "close_proof": proof, "ledger_sha256": digest,
            "initializer_commit": init.git(init.ROOT, "rev-parse", "HEAD"),
        })
        before[Path(self.ledger.name)] = ledger
        before[Path(self.sidecar.name)] = self.sidecar.read_bytes()
        for checkout in (self.pin_b, self.ctl):
            with self.subTest(checkout=checkout.name):
                result = subprocess.check_output([sys.executable, "-I", "-B", "-c", READER, checkout,
                                                  "close-proof", "--attempt-ledger", self.ledger], cwd=checkout)
                self.assertEqual(result, proof.encode())
                self.assertEqual(init.git(checkout, "status", "--porcelain", "--ignored"), "")
        self.assertEqual(self.snapshot(), before)
        self.assert_refusal("already exists")

    def test_existing_ledger_or_sidecar_refuses_without_overwrite(self):
        for path in (self.ledger, self.sidecar):
            with self.subTest(path=path.name):
                path.write_bytes(b"preexisting synthetic file")
                self.assert_refusal("already exists")
                path.unlink()
        self.ledger.symlink_to(self.root / "absent")
        self.assert_refusal("already exists")
        self.assertTrue(self.ledger.is_symlink())

    def test_active_desk_fence_refuses(self):
        (self.desk / init.desk.FENCE_NAME).write_text(json.dumps({
            "purpose": "synthetic", "pid": 12345, "deadline": time.time() + 300,
        }))
        self.assert_refusal("active desk fence")
        self.pid_alive.assert_called_once_with(12345)

    def test_lock_is_held_during_close_proof(self):
        check_output = subprocess.check_output
        audited = []

        def probe(command, **kwargs):
            if "close-proof" in command:
                with self.lock.open("r+b") as other:
                    with self.assertRaises(BlockingIOError):
                        fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.assertFalse(self.ledger.exists())
                self.assertFalse(self.sidecar.exists())
                audited.append(command)
            return check_output(command, **kwargs)

        with patch.object(init.subprocess, "check_output", side_effect=probe):
            self.assertEqual(self.run_initializer()[0], 0)
        self.assertEqual(len(audited), 1)

    def test_missing_lock_refuses_without_creating_one(self):
        self.lock.unlink()
        self.assert_refusal(".desk-fence.lock")

    def test_wrong_ctl_pin_refuses(self):
        self.assert_refusal("runner pin", **{"ctl-checkout": self.pin_b})

    def test_issued_receipt_path_and_digest_must_match(self):
        self.assert_refusal("SHA-256", **{"receipt-sha256": "0" * 64})
        self.assert_refusal("absolute path", **{"close-receipt": self.receipt.name})

    def test_missing_span_id_and_span_id_mismatch_refuse(self):
        self.assert_refusal("close-proof", **{"span-id": "synthetic-other-a1"})
        del self.close_record["span_id"]
        self.write_receipt()
        self.assert_refusal("close-proof")

    def test_close_ns_must_equal_close_proof_output(self):
        self.assert_refusal("close-proof output differs", **{"close-ns": CLOSE_NS + 1})
        self.assert_refusal("close-proof output differs", **{"close-ns": f"0{CLOSE_NS}"})

    def test_failed_close_proof_refuses(self):
        with patch.dict(os.environ, {"FEEDS_STOPPED": "0"}):
            self.assert_refusal("close-proof")

    def test_failed_sidecar_publish_rolls_back_ledger(self):
        link = os.link

        def fail_sidecar(source, target):
            if target == self.sidecar:
                self.assertTrue(self.ledger.exists())
                raise OSError("synthetic sidecar link failure")
            link(source, target)

        with patch.object(init.os, "link", side_effect=fail_sidecar):
            self.assert_refusal("synthetic sidecar link failure")
        self.assertEqual(self.run_initializer()[0], 0)

    def test_failed_final_directory_sync_rolls_back_both_outputs(self):
        sync_directory = init.desk.sync_directory

        def fail_final_sync(directory):
            if self.sidecar.exists():
                raise OSError("synthetic final sync failure")
            sync_directory(directory)

        with patch.object(init.desk, "sync_directory", side_effect=fail_final_sync):
            self.assert_refusal("synthetic final sync failure")


if __name__ == "__main__":
    unittest.main()
