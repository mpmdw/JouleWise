"""Synthetic ledger boundaries and read-only custody protocol regressions."""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import calibration_ledger as ledger
from joulewise.calibration_exits import RefusalCode
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS


class LedgerSessionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path, self.pin = self.root / "ledger.jsonl", self.root / "head.json"
        self.write_pin(0, ledger.GENESIS_DIGEST)
        self.epoch = {
            "os_build": "25G83", "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power", "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.bindings.update(self.epoch)

    def write_pin(self, sequence, digest):
        self.pin.write_text(json.dumps({"sequence": sequence, "head_digest": digest,
                                        "ledger_schema": ledger.LEDGER_SCHEMA}) + "\n")

    def open_session(self, count):
        slots = ledger.derivation_session_slots(count)
        return ledger.append_bracket_session_receipt(
            self.path, session_id="synthetic-night", window_id="synthetic-window",
            plan_id="synthetic-plan", plan_sha256="a" * 64,
            evidence_root_id="synthetic-root", runs_root=self.root / "runs",
            slots={slot: {
                "attempt_id": f"synthetic-night-{slot}",
                "custody_locator": str(self.root / "runs" / "instrument_validation"
                                       / f"synthetic-night-{slot}"),
                "identity_epoch": self.epoch, "t1_bindings": self.bindings,
            } for slot in slots},
            session_kind=ledger.SESSION_KIND_DERIVATION, declared_slots=slots,
            head_pin_path=self.pin, require_committed_pin=False,
        )

    def fill(self, slot):
        attempt = f"synthetic-night-{slot}"
        custody = self.root / "runs" / "instrument_validation" / attempt
        (custody / "raw").mkdir(parents=True)
        for name, raw in {
            "raw/powermetrics.plist": b"synthetic power " + attempt.encode(),
            "events.jsonl": b'{"timestamp_s":99.0}\n',
            "instrument_evidence.json": json.dumps({"b_fiducial_s": 0.025, "attempt": attempt}).encode(),
            "manifest.json": json.dumps({"attempt": attempt}).encode(),
        }.items():
            (custody / name).write_bytes(raw)
        ledger.claim_bracket_session_slot(self.path, session_id="synthetic-night",
                                         slot=slot, attempt_id=attempt)
        return ledger.finalize_bracket_session_slot(
            self.path, session_id="synthetic-night", slot=slot, disposition="valid",
            custody_locator=str(custody), artifact_sha256=ledger.artifact_hashes(custody),
            identity_epoch=self.epoch, t1_bindings=self.bindings,
            capture_wall_time_s="99.0", exact_bound_lexeme_s="0.025",
        )

    def snapshot(self):
        return ledger.load_calibration_ledger_snapshot(
            self.path, self.pin, baseline_sequence=0, baseline_digest=ledger.GENESIS_DIGEST,
            require_committed_pin=False, verify_custody=False,
        )

    def test_one_slot_derivation_session_is_admitted(self):
        """A derivation can reserve exactly one slot. Kills M03170 (minimum 1 -> 2)."""
        self.open_session(1)
        session = self.snapshot().bracket_session_by_id["synthetic-night"]
        self.assertEqual(session.declared_slots, ("d01",))
        self.assertEqual(session.next_slot, "d01")

    def test_claim_after_all_slots_finalized_has_typed_conflict(self):
        """An exhausted session's extra claim is a conflict, not an index error. Kills M03528."""
        self.open_session(2)
        self.fill("d01")
        self.fill("d02")
        rows = [json.loads(line) for line in self.path.read_text().splitlines()]
        # Legacy business-only chains are still admitted by the reader. Make
        # one with correct hashes but an extra claim after both finals, so
        # the public reader must reach semantic session validation.
        business = [row for row in rows if row["schema_version"] == ledger.BRACKET_SESSION_SCHEMA]
        extra_claim = dict(next(row for row in business
                                if row["event"] == ledger.BRACKET_SESSION_SLOT_CLAIM_EVENT))
        business.append(extra_claim)
        predecessor = ledger.GENESIS_DIGEST
        for sequence, row in enumerate(business, 1):
            row.update(sequence=sequence, predecessor_digest=predecessor)
            core = {key: value for key, value in row.items() if key != "receipt_digest"}
            # Independent canonical JSON/SHA-256 sealing of the synthetic chain.
            raw = json.dumps(core, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()
            predecessor = row["receipt_digest"] = hashlib.sha256(raw).hexdigest()
        self.path.write_text("".join(json.dumps(row) + "\n" for row in business))
        self.write_pin(len(business), predecessor)
        self.assertEqual(self.snapshot().refusal_reasons,
                         ("calibration_ledger_bracket_session_conflict",))


class JournalAndLeaseTests(unittest.TestCase):
    def test_full_tail_is_valid_and_longer_journal_retains_only_64_bytes(self):
        """Recovery accepts a full tail and retains its last 64 bytes. Kills M02866 and M03616."""
        for length in (64, 80):
            with self.subTest(length=length), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / "ledger.jsonl"
                # Use the established journal locator, independently deriving
                # its retained bytes and digest from the synthetic payload.
                journal = ledger._legacy_append_journal_path(path)
                raw = bytes(range(length))
                journal.write_bytes(raw)
                inspection = ledger.repair_calibration_ledger(path)
                self.assertEqual(inspection.state, "clean")
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                metadata = rows[-1]["legacy_journal"]
                expected_tail = bytes(range(length - 64, length))
                self.assertEqual(metadata["length"], length)
                self.assertEqual(bytes.fromhex(metadata["observed_tail_hex"]), expected_tail)
                self.assertEqual(metadata["observed_tail_sha256"],
                                 hashlib.sha256(expected_tail).hexdigest())

    def test_publication_refuses_replaced_leased_inode(self):
        """Publishing through a lease refuses a replaced inode. Kills M03363."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_bytes(b"original\n")
            with ledger.CalibrationWriterLease(path) as lease:
                replacement = Path(tmp) / "replacement"
                replacement.write_bytes(b"replacement\n")
                os.replace(replacement, path)
                with self.assertRaises(ledger.CalibrationLedgerError) as caught:
                    lease.publish_genesis_payload(b"new payload\n")
                self.assertEqual(caught.exception.code, RefusalCode.UNSAFE_LOCK_INODE)
                self.assertEqual(caught.exception.context["reason"], "leased_path_replaced")
                self.assertEqual(path.read_bytes(), b"replacement\n")


class CustodyProtocolTests(unittest.TestCase):
    def request(self, reasons, progress_bytes=0):
        # A read-only synthetic peer uses real pipes but never imports or
        # starts the instrument/capture worker.
        program = (
            "import json,sys; request=json.loads(sys.stdin.readline()); "
            f"print(json.dumps({{'request_id':request['request_id'],'progress':{{'locator':'x'*{progress_bytes}}}}})); "
            f"print(json.dumps({{'request_id':request['request_id'],'result':{{'observations':0,'elapsed_s':0.0,'reasons':{reasons!r}}}}}))"
        )
        popen = ledger.subprocess.Popen

        def spawn(_argv, **kwargs):
            return popen([sys.executable, "-B", "-c", program], **kwargs)

        deadline = ledger.CustodyDeadline(5.0, telemetry_stream=None)
        with patch.object(ledger.subprocess, "Popen", side_effect=spawn):
            return ledger.bounded_custody_reasons([], Path("/synthetic"), deadline)

    def test_valid_progress_frame_of_eight_kib_is_admitted(self):
        """A valid few-KiB progress frame fits the custody protocol. Kills M04101."""
        self.assertEqual(self.request([], progress_bytes=8192), set())

    def test_recognized_worker_refusal_passes_through(self):
        """The governed worker refusal passes through unchanged. Kills M03736."""
        reason = RefusalCode.LEDGER_CUSTODY_INVALID.value
        self.assertEqual(self.request([reason]), {reason})

    def test_unknown_worker_reason_is_a_protocol_refusal(self):
        """An unknown worker reason is rejected as a protocol error. Kills M03736."""
        with self.assertRaises(ledger.CalibrationLedgerError) as caught:
            self.request(["synthetic_unknown"])
        self.assertEqual(caught.exception.code, RefusalCode.LEDGER_CUSTODY_INVALID)
        self.assertEqual(caught.exception.context["reason"], "custody_worker_protocol")

    def test_live_worker_is_terminated_and_reaped(self):
        """Cleanup terminates and reaps a live worker. Kills M02715.

        This private teardown helper has no standalone public cleanup API;
        the observable contract here is process ownership, not a floor value.
        """
        class Process:
            def __init__(self):
                self.stdin, self.stdout = io.BytesIO(), io.BytesIO()
                self.terminated, self.reaped = False, False

            def poll(self):
                return None

            def terminate(self):
                self.terminated = True

            def wait(self, timeout=None):
                self.reaped = True
                return 0

        process = Process()
        ledger._stop_custody_worker(process)
        self.assertTrue(process.terminated)
        self.assertTrue(process.reaped)
        self.assertTrue(process.stdin.closed and process.stdout.closed)
