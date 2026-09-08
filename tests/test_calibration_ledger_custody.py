"""Bounded custody-state probes; all filesystem inputs are local or mocked."""

from contextvars import ContextVar
import os
import hashlib
from types import SimpleNamespace
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock

from joulewise import calibration_ledger as ledger


class CustodyProbeTests(unittest.TestCase):
    def test_production_budget_matches_paper_probe(self):
        self.assertEqual(ledger.CUSTODY_PROBE_TIMEOUT_S, 2.0)

    def test_blocked_operations_have_absent_state_within_one_budget(self):
        for operation in ("exists", "is_dir", "is_file", "read"):
            with self.subTest(operation=operation):
                entered = threading.Event()
                release = threading.Event()
                finished = threading.Event()
                workers = []

                def blocked(*args, **kwargs):
                    workers.append(threading.current_thread())
                    entered.set()
                    release.wait()
                    finished.set()
                    if operation == "read":
                        return {name: b"{}" for name in ledger.GOVERNED_ARTIFACTS}
                    return True

                try:
                    with (
                        mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                        mock.patch.object(Path, "exists", side_effect=blocked if operation == "exists" else None, return_value=True),
                        mock.patch.object(Path, "is_dir", side_effect=blocked if operation == "is_dir" else None, return_value=True),
                        mock.patch.object(Path, "is_file", side_effect=blocked if operation == "is_file" else None, return_value=True),
                        mock.patch.object(ledger, "_governed_raw_nofollow", side_effect=blocked if operation == "read" else None, return_value={name: b"{}" for name in ledger.GOVERNED_ARTIFACTS}),
                    ):
                        started = time.monotonic()
                        self.assertEqual(ledger._custody_state(Path("/mock/custody")), "absent")
                        elapsed = time.monotonic() - started
                        self.assertTrue(entered.is_set())
                        self.assertGreaterEqual(elapsed, 0.04)
                        self.assertLess(elapsed, 0.5)
                        self.assertTrue(workers[0].daemon)
                        release.set()
                        workers[0].join(1)
                        self.assertTrue(finished.is_set())
                        self.assertFalse(workers[0].is_alive())
                finally:
                    release.set()
                    for worker in workers:
                        worker.join(1)

    def test_empty_override_never_starts_probe_for_backup_locator(self):
        for override in ("", os.pathsep):
            with (
                self.subTest(override=override),
                mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": override}),
                mock.patch.object(threading.Thread, "start", side_effect=AssertionError("probe started")),
                mock.patch.object(Path, "exists", side_effect=AssertionError("filesystem probe")),
                mock.patch.object(Path, "resolve", side_effect=AssertionError("filesystem resolution")),
            ):
                for path in (ledger.BACKUP_ROOTS[0], ledger.BACKUP_ROOTS[0] / "runs/member"):
                    self.assertEqual(ledger._custody_state(path), "absent")

    def test_empty_override_preserves_local_states_and_path_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}
        ):
            root = Path(temporary).resolve()
            self.assertEqual(ledger._custody_state(root / "missing"), "absent")
            self.assertEqual(ledger._custody_state(root), "empty")
            (root / "manifest.json").write_text("{}")
            self.assertEqual(ledger._custody_state(root), "partial")
            self.assertEqual(ledger._custody_state(root / "manifest.json"), "unreadable")
            for name in ledger.GOVERNED_ARTIFACTS:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}")
            self.assertEqual(ledger._custody_state(root), "complete")
            sibling = Path(str(ledger.BACKUP_ROOTS[0]) + "-sibling")
            self.assertFalse(ledger._custody_backup_disabled(sibling))

    def test_worker_preserves_caller_context_and_errors(self):
        context_value = ContextVar("custody-test", default="missing")
        token = context_value.set("caller")
        try:
            with mock.patch.object(ledger, "_custody_state_unbounded", side_effect=lambda path: context_value.get()):
                self.assertEqual(ledger._custody_state(Path("/mock/custody")), "caller")
            with mock.patch.object(ledger, "_custody_state_unbounded", side_effect=ValueError("original")):
                with self.assertRaisesRegex(ValueError, "original"):
                    ledger._custody_state(Path("/mock/custody"))
        finally:
            context_value.reset(token)


class CustodyReadCoverageTests(unittest.TestCase):
    @staticmethod
    def observation(path):
        return SimpleNamespace(
            custody_locator=str(path), artifact_sha256={"manifest.json": "0" * 64},
            attempt_id="probe", disposition="valid",
        )

    @staticmethod
    def outcome(call):
        try:
            return call()
        except ledger.CalibrationLedgerError as exc:
            return (type(exc), str(exc))

    def test_remaining_reads_timeout_like_missing_custody(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "missing"
            observation = self.observation(root)
            plan = SimpleNamespace(receipts=[{
                "event": ledger.HISTORICAL_IMPORT_FINALIZATION_EVENT,
                "custody_locator": str(root), "artifact_sha256": {},
            }])
            cases = (
                (lambda: ledger.artifact_hashes(root), Path, "is_file"),
                (lambda: ledger._custody_reasons([observation], root.parent),
                 ledger, "read_authentication_input"),
                (lambda: ledger._assert_absolute_nonsymlink_directory(root), os, "lstat"),
                (lambda: ledger._read_contained_nofollow(root, "manifest.json"),
                 ledger, "read_authentication_input_nofollow"),
                (lambda: ledger._governed_raw_nofollow(root),
                 ledger, "read_authentication_input_nofollow"),
                (lambda: ledger._reauthenticate_historical_import_plan(plan),
                 ledger, "read_authentication_input_nofollow"),
            )
            for call, target, name in cases:
                with self.subTest(probe=name, call=call):
                    expected = self.outcome(call)
                    root.mkdir()
                    release = threading.Event()
                    entered = threading.Event()
                    workers = []

                    def blocked(*args, **kwargs):
                        workers.append(threading.current_thread())
                        entered.set()
                        release.wait()
                        raise FileNotFoundError("released synthetic probe")

                    try:
                        with (
                            mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                            mock.patch.object(target, name, side_effect=blocked),
                        ):
                            started = time.monotonic()
                            self.assertEqual(self.outcome(call), expected)
                            self.assertLess(time.monotonic() - started, 0.5)
                            self.assertTrue(entered.is_set())
                            self.assertTrue(workers[0].daemon)
                            release.set()
                            workers[0].join(1)
                    finally:
                        release.set()
                        for worker in workers:
                            worker.join(1)
                        root.rmdir()

    def test_empty_override_skips_all_read_entrypoints(self):
        root = ledger.BACKUP_ROOTS[0] / "runs/member"
        observation = self.observation(root)
        with (
            mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}),
            mock.patch.object(threading.Thread, "start", side_effect=AssertionError("probe")),
        ):
            self.assertEqual(ledger.artifact_hashes(root), {})
            self.assertEqual(ledger._custody_reasons([observation], Path("/")),
                             {"calibration_ledger_custody_invalid"})
            for call in (
                lambda: ledger._assert_absolute_nonsymlink_directory(root),
                lambda: ledger._read_contained_nofollow(root, "manifest.json"),
                lambda: ledger._governed_raw_nofollow(root),
            ):
                with self.assertRaisesRegex(ledger.CalibrationLedgerError, "custody locator is missing"):
                    call()

    def test_nonempty_override_reads_relocated_bytes_without_original_probe(self):
        with tempfile.TemporaryDirectory() as temporary:
            backup = Path(temporary).resolve()
            mapped = backup / "runs/member"
            mapped.mkdir(parents=True)
            for name in ledger.GOVERNED_ARTIFACTS:
                artifact = mapped / name
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(b"{}")
            original = ledger.BACKUP_ROOTS[0] / "runs/member"
            observation = self.observation(original)
            observation.artifact_sha256 = {"manifest.json": hashlib.sha256(b"{}").hexdigest()}
            real_exists = Path.exists

            def safe_exists(path):
                self.assertFalse(path.is_relative_to(ledger.BACKUP_ROOTS[0]))
                return real_exists(path)

            with (
                mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS":
                    str(backup / "missing") + os.pathsep + str(backup)}),
                mock.patch.object(Path, "exists", safe_exists),
            ):
                self.assertEqual(ledger._custody_state(original), "complete")
                self.assertEqual(ledger.artifact_hashes(original), ledger.artifact_hashes(mapped))
                self.assertEqual(ledger._custody_reasons([observation], backup), set())
                self.assertEqual(ledger._governed_raw_nofollow(original),
                                 {name: b"{}" for name in ledger.GOVERNED_ARTIFACTS})
                # A present but corrupt first root cannot be skipped for a good one.
                bad = backup / "bad/runs/member"
                bad.mkdir(parents=True)
                (bad / "manifest.json").write_bytes(b"corrupt")
                os.environ["JOULEWISE_BACKUP_ROOTS"] = str(backup / "bad") + os.pathsep + str(backup)
                self.assertEqual(ledger._custody_reasons([observation], backup),
                                 {"calibration_ledger_custody_invalid"})

    def test_governed_reads_share_one_worker_and_preserve_authentication_session(self):
        from joulewise.authentication_io import V2AuthenticationReadSession

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for name in ledger.GOVERNED_ARTIFACTS:
                artifact = root / name
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(b"{}")
            real_thread = threading.Thread
            with V2AuthenticationReadSession() as session, mock.patch.object(
                threading, "Thread", wraps=real_thread
            ) as thread:
                ledger._governed_raw_nofollow(root)
                self.assertEqual(thread.call_count, 1)
                self.assertEqual(len(session.records), len(ledger.GOVERNED_ARTIFACTS))


    def test_timed_out_authenticated_read_does_not_pin_session_lock(self):
        from joulewise.authentication_io import V2AuthenticationReadSession

        release = threading.Event()
        entered = threading.Event()
        workers = []

        def blocked(*args, **kwargs):
            workers.append(threading.current_thread())
            entered.set()
            release.wait()
            raise FileNotFoundError("released synthetic read")

        try:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                with (
                    V2AuthenticationReadSession() as session,
                    mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                    mock.patch("joulewise.authentication_io._read_nofollow_bytes",
                               side_effect=blocked),
                ):
                    with self.assertRaisesRegex(ledger.CalibrationLedgerError,
                                                "custody locator is missing"):
                        ledger._governed_raw_nofollow(root)
                    self.assertTrue(entered.is_set())
                    acquired = session._lock.acquire(blocking=False)
                    if acquired:
                        session._lock.release()
                    release.set()
                    workers[0].join(1)
                    self.assertTrue(acquired, "timed-out read pins the shared authentication lock")
        finally:
            release.set()
            for worker in workers:
                worker.join(1)
