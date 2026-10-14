import hashlib
import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.b6 import capture_list


def row(seq=1):
    return {"seq": seq, "session_id": "synthetic-session", "slot": "pre", "attempt_id": f"a{seq}",
            "value_s": "0.028000000000000001", "disposition": "valid", "captured_utc": "2026-10-14T00:00:00Z",
            "evidence_path": "/synthetic/evidence", "evidence_sha256": "a" * 64}


def append_child(path, seq, queue):
    queue.put(capture_list.append(path, row(seq)))


class CaptureListTests(unittest.TestCase):
    def test_append_contention_whole_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.jsonl"
            ctx = multiprocessing.get_context("spawn")
            queue = ctx.Queue()
            processes = [ctx.Process(target=append_child, args=(path, n, queue)) for n in (1, 2)]
            try:
                for process in processes:
                    process.start()
                for process in processes:
                    process.join(15)
                    self.assertEqual(process.exitcode, 0)
                self.assertIsNone(queue.get(timeout=2))
                self.assertIsNone(queue.get(timeout=2))
                rows, problems = capture_list.read(path)
                self.assertEqual({r["seq"] for r in rows}, {1, 2})
                self.assertEqual(len(path.read_bytes().splitlines()), 2)
                self.assertEqual(problems, [])
            finally:
                for process in processes:
                    if process.is_alive():
                        process.kill()
                    process.join()
                queue.close()
                queue.join_thread()

    def test_malformed_line_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.jsonl"
            self.assertIsNone(capture_list.append(path, row()))
            with path.open("ab") as stream:
                stream.write(b'{torn\n\xff\n')
                stream.write((json.dumps({"schema": capture_list.SCHEMA, **row(), "value_s": "bad"}) + "\n").encode())
            rows, problems = capture_list.read(path)
            self.assertEqual(rows[0]["value_s"], "0.028000000000000001")
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(problems), 3)
            self.assertTrue(all(p.startswith("calibration.capture_list_line_unreadable") for p in problems))

    def test_lock_timeout_and_write_error_return_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.jsonl"
            with patch.object(capture_list, "LOCK_TIMEOUT_S", 0), patch.object(capture_list.fcntl, "flock", side_effect=BlockingIOError):
                self.assertIn("lock_timeout", capture_list.append(path, row()))
            with patch.object(capture_list.os, "write", side_effect=OSError("write")):
                self.assertIn("write_error", capture_list.append(path, row()))
            self.assertIn("write_error", capture_list.append(path, {**row(), "value_s": "NaN"}))

    def test_dataless_never_reads_and_changed_bytes(self):
        value = row()
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_flags=capture_list.DATALESS)), \
             patch.object(Path, "read_bytes", side_effect=AssertionError("must not hydrate")):
            self.assertEqual(capture_list.check_bytes(value), "evicted")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_bytes(b"first")
            value.update(evidence_path=str(path), evidence_sha256=hashlib.sha256(b"first").hexdigest())
            self.assertEqual(capture_list.check_bytes(value), "ok")
            path.write_bytes(b"changed")
            self.assertEqual(capture_list.check_bytes(value), "changed")
            path.unlink()
            self.assertEqual(capture_list.check_bytes(value), "missing")

    def test_legacy_finalized_observations_only(self):
        receipt = {"sequence": 2, "event": "bracket-session-slot-finalization", "session_id": "session",
                   "slot": "pre", "attempt_id": "attempt", "exact_bound_lexeme_s": ".028000000000000001",
                   "disposition": "valid", "custody_locator": "/synthetic/capture",
                   "artifact_sha256": {"instrument_evidence.json": "b" * 64}, "capture_wall_time_s": "123"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.jsonl"
            records = [{**receipt, "event": "reservation"}, receipt,
                       {**receipt, "sequence": 3, "event": "historical-import-v1-finalization"}]
            path.write_text("\n".join(json.dumps(r) for r in records) + "\n{torn\n")
            rows = capture_list.import_custody_ledger(path)
            self.assertEqual([r["seq"] for r in rows], [2, 3])
            self.assertEqual(rows[0]["value_s"], ".028000000000000001")
            self.assertEqual(rows[0]["evidence_sha256"], "b" * 64)
