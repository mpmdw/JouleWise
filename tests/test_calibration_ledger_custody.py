"""Bounded custody-state probes; all filesystem inputs are local or mocked."""

from contextvars import ContextVar
import os
import io
from contextlib import redirect_stderr
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
    def test_probe_is_exported(self):
        self.assertIn("probe_custody", ledger.__all__)

    def test_unreachable_diagnostics_distinguish_absence(self):
        for reason in ("timeout", "exception", "absent"):
            with self.subTest(reason=reason):
                stderr = io.StringIO()
                with (
                    redirect_stderr(stderr),
                    mock.patch.object(Path, "exists", side_effect=OSError("offline") if reason == "exception" else None, return_value=False),
                    mock.patch.object(threading.Thread, "is_alive", return_value=reason == "timeout"),
                ):
                    self.assertEqual(ledger._custody_state(Path("/mock/custody")), "absent")
                if reason == "absent":
                    self.assertEqual(stderr.getvalue(), "")
                else:
                    self.assertEqual(stderr.getvalue(),
                        f"custody_locator_unreachable reason={reason} locator=/mock/custody budget_s=2.0\n")

    def test_mint_hashes_refuse_override_before_any_probe_or_read(self):
        with (
            mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": "/mock/relocated"}),
            mock.patch.object(ledger, "probe_custody", side_effect=AssertionError("probe attempted")),
            mock.patch.object(ledger, "_artifact_hashes_unbounded", side_effect=AssertionError("hash attempted")),
        ):
            with self.assertRaisesRegex(ledger.CalibrationLedgerError, "custody_locator_override_mint_forbidden"):
                ledger.artifact_hashes(Path("/mock/original"))

    def test_issuance_refuses_override_before_input_access(self):
        calls = (
            lambda: ledger.generate_historical_custody_manifest(roots=(),
                checkout_root=None, disposition_table_raw=b"",
                expected_disposition_table_sha256=""),
            lambda: ledger.bootstrap_historical_import(None, head_pin_path=None,
                disposition_table_raw=b"", expected_disposition_table_sha256="",
                custody_manifest_raw=b"", expected_custody_manifest_sha256=""),
            lambda: ledger.resume_finalize_bracket_session(None, None,
                session_id="s", slot="pre", plan_path=None, systematic_screen_s=None),
            lambda: ledger.finalize_attempt_receipt(None, attempt_id="a",
                disposition="valid", custody_locator="/mock/original"),
            lambda: ledger.finalize_bracket_session_slot(None, session_id="s",
                slot="pre", disposition="valid", custody_locator="/mock/original"),
            lambda: ledger.prepare_historical_import(disposition_table_raw=b"",
                expected_disposition_table_sha256="", custody_manifest_raw=b"",
                expected_custody_manifest_sha256=""),
        )
        with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": "/mock/relocated"}):
            for call in calls:
                with self.subTest(call=call), self.assertRaisesRegex(
                    ledger.CalibrationLedgerError, "custody_locator_override_mint_forbidden"
                ):
                    call()

    def test_issuing_helpers_ignore_planted_replacement(self):
        # The guard is tested separately. Disable only that defence in depth
        # here to prove artifact_hashes itself cannot bind relocated bytes.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original_root, mapped_root = root / "original", root / "mapped"
            original, mapped = original_root / "runs/member", mapped_root / "runs/member"
            for directory, raw in ((original, b"{}"), (mapped, b'{"planted":true}')):
                for name in ledger.GOVERNED_ARTIFACTS:
                    artifact = directory / name
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    artifact.write_bytes(raw)
            hashes = {name: hashlib.sha256(b"{}").hexdigest() for name in ledger.GOVERNED_ARTIFACTS}
            plan = SimpleNamespace(receipts=[{
                "event": ledger.HISTORICAL_IMPORT_FINALIZATION_EVENT,
                "custody_locator": str(original), "artifact_sha256": hashes,
            }])
            cases = {
                "probe_default": lambda: ledger.probe_custody(original, str, lambda: "absent"),
                "hashes": lambda: ledger.artifact_hashes(original),
                "directory": lambda: ledger._assert_absolute_nonsymlink_directory(original),
                "read": lambda: ledger._read_contained_nofollow(original, "manifest.json"),
                "governed": lambda: ledger._governed_raw_nofollow(original),
                "reauthenticate": lambda: ledger._reauthenticate_historical_import_plan(plan),
                "historical": lambda: ledger._inspect_historical_candidate(original, checkout_root=root, expected_epoch={}),
                "state": lambda: ledger._custody_state(original),
                "custody_validation_issuing": lambda: ledger._custody_reasons(
                    [SimpleNamespace(custody_locator=str(original), artifact_sha256=hashes,
                                     attempt_id="a", disposition="valid")], root, mode="issuing"),
            }
            def outcome(call):
                try:
                    return call()
                except ledger.CalibrationLedgerError as exc:
                    return type(exc), str(exc)

            for present in (True, False):
                if not present:
                    original.rename(original.with_name("removed"))
                with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}):
                    expected = {name: outcome(call) for name, call in cases.items()}
                touched = []
                def track(operation):
                    def checked(path, *args, **kwargs):
                        if isinstance(path, (str, os.PathLike)) and Path(path).is_relative_to(mapped_root):
                            touched.append(str(path))
                            raise AssertionError("issuing touched replacement")
                        return operation(path, *args, **kwargs)
                    return checked
                with (
                    mock.patch.object(ledger, "BACKUP_ROOTS", (original_root,)),
                    mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": str(mapped_root)}),
                    mock.patch.object(ledger, "_refuse_custody_override_mint"),
                    mock.patch.object(Path, "exists", track(Path.exists)),
                    mock.patch.object(Path, "is_dir", track(Path.is_dir)),
                    mock.patch.object(Path, "open", track(Path.open)),
                    mock.patch.object(os, "open", track(os.open)),
                ):
                    for name, call in cases.items():
                        with self.subTest(helper=name, original_present=present):
                            self.assertEqual(outcome(call), expected[name])
                            self.assertEqual(touched, [])
                if present:
                    self.assertEqual(expected["hashes"], hashes)
                    self.assertEqual(expected["read"], b"{}")
                else:
                    self.assertEqual(expected["hashes"], {})
                    self.assertEqual(expected["state"], "absent")

    def test_readiness_forwards_resolution_mode_to_snapshot_and_state(self):
        class ReachedState(Exception):
            pass

        session = SimpleNamespace(state="open", finalized_slots=(),
                                  slot_attempt_ids={"pre": "attempt"})
        snapshot = SimpleNamespace(bracket_session_by_id={"session": session})
        inspection = SimpleNamespace(state="clean", legacy_journal_path=None)
        reserved = {"slots": {"pre": {"custody_locator": "/mock/original"}}}
        for enforcing, mode in ((True, "issuing"), (False, "read_replay")):
            with (
                self.subTest(enforcing=enforcing),
                mock.patch.object(ledger, "_current_writer_lease", return_value=object()),
                mock.patch.object(ledger, "inspect_calibration_ledger", return_value=inspection),
                mock.patch.object(ledger, "load_calibration_ledger_snapshot", return_value=snapshot) as load,
                mock.patch.object(ledger, "_pin_relation", return_value=ledger.PinRelation.EXACT),
                mock.patch.object(ledger, "writer_lease_is_live", return_value=False),
                mock.patch.object(ledger, "_session_open_receipt", return_value=reserved),
                mock.patch.object(ledger, "_custody_state", side_effect=ReachedState) as state,
            ):
                with self.assertRaises(ReachedState):
                    ledger.calibration_readiness(Path("/mock/ledger"), Path("/mock/pin"),
                        phase="pre-slot", session_id="session", enforcing_under_lease=enforcing)
                self.assertEqual(load.call_args.kwargs.get("mode"), mode)
                self.assertEqual(load.call_args.kwargs["verify_custody"], enforcing)
                state.assert_called_once_with(Path("/mock/original"), mode=mode)

    def test_head_pin_advancement_forwards_issuing_mode(self):
        class ReachedSnapshot(Exception):
            pass

        with (
            mock.patch.object(ledger, "CalibrationWriterLease"),
            mock.patch.object(ledger, "_authenticated_head_pin", return_value={}),
            mock.patch.object(ledger, "inspect_calibration_ledger",
                              return_value=SimpleNamespace(state="clean", legacy_journal_path=None)),
            mock.patch.object(ledger, "load_calibration_ledger_snapshot", side_effect=ReachedSnapshot) as load,
        ):
            with self.assertRaises(ReachedSnapshot):
                ledger.advance_calibration_head_pin(Path("/mock/ledger"), Path("/mock/pin"),
                    session_id=None, expected_sequence=1, expected_digest="0" * 64,
                    operator_identity="test", attestation_reason="routing test")
            self.assertEqual(load.call_args.kwargs.get("mode"), "issuing")
            self.assertTrue(load.call_args.kwargs["verify_custody"])

    def test_lifecycle_slot_validator_forwards_issuing_mode(self):
        from scripts import validate_powermetrics_fiducial as writer

        class ReachedSnapshot(Exception):
            pass

        with mock.patch.object(writer, "load_calibration_ledger_snapshot", side_effect=ReachedSnapshot) as load:
            with self.assertRaises(ReachedSnapshot):
                writer._validate_reserved_bracket_slot(Path("/mock/ledger"), Path("/mock/pin"),
                    session_id="session", slot="pre", attempt_id="attempt",
                    custody_locator="/mock/original", identity_epoch={}, t1_bindings={})
            self.assertEqual(load.call_args.kwargs.get("mode"), "issuing")
            self.assertTrue(load.call_args.kwargs["verify_custody"])

    def test_unknown_resolution_mode_refuses_before_probe(self):
        with mock.patch.object(threading.Thread, "start", side_effect=AssertionError("probe")):
            with self.assertRaisesRegex(ValueError, "invalid custody resolution mode"):
                ledger.probe_custody(Path("/mock/custody"), str, dict, mode="typo")

    def test_empty_override_preserves_local_mint_hashes(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}
        ):
            root = Path(temporary)
            (root / "manifest.json").write_bytes(b"{}")
            self.assertEqual(ledger.artifact_hashes(root),
                {"manifest.json": hashlib.sha256(b"{}").hexdigest()})

    def test_blocked_operations_have_absent_state_within_one_budget(self):
        for operation in ("exists", "is_dir"):
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
                    return True

                try:
                    with (
                        mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                        mock.patch.object(Path, "exists", side_effect=blocked if operation == "exists" else None, return_value=True),
                        mock.patch.object(Path, "is_dir", side_effect=blocked if operation == "is_dir" else None, return_value=True),
                        mock.patch.object(Path, "is_file", side_effect=AssertionError("inspection attempted")),
                        mock.patch.object(ledger, "_governed_raw_nofollow_unbounded", side_effect=AssertionError("read attempted")),
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

    def test_inspection_runs_on_caller_with_original_context_and_errors(self):
        context_value = ContextVar("custody-test", default="missing")
        token = context_value.set("caller")
        caller = threading.current_thread()

        def inspect(path):
            self.assertIs(threading.current_thread(), caller)
            return context_value.get()

        try:
            with mock.patch.object(Path, "exists", return_value=True), mock.patch.object(Path, "is_dir", return_value=True), mock.patch.object(ledger, "_custody_state_unbounded", side_effect=inspect):
                self.assertEqual(ledger._custody_state(Path("/mock/custody")), "caller")
            with mock.patch.object(Path, "exists", return_value=True), mock.patch.object(Path, "is_dir", return_value=True), mock.patch.object(ledger, "_custody_state_unbounded", side_effect=ValueError("original")):
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

    def test_path_probe_timeouts_match_each_entrypoints_missing_outcome(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "missing"
            observation = self.observation(root)
            plan = SimpleNamespace(receipts=[{
                "event": ledger.HISTORICAL_IMPORT_FINALIZATION_EVENT,
                "custody_locator": str(root), "artifact_sha256": {},
            }])
            cases = (
                lambda: ledger.artifact_hashes(root),
                lambda: ledger._custody_reasons([observation], root.parent),
                lambda: ledger._assert_absolute_nonsymlink_directory(root),
                lambda: ledger._read_contained_nofollow(root, "manifest.json"),
                lambda: ledger._governed_raw_nofollow(root),
                lambda: ledger._reauthenticate_historical_import_plan(plan),
            )
            for call in cases:
                expected = self.outcome(call)
                for operation in ("exists", "is_dir"):
                    with self.subTest(call=call, operation=operation):
                        release = threading.Event()
                        entered = threading.Event()
                        workers = []

                        def blocked(*args, **kwargs):
                            workers.append(threading.current_thread())
                            entered.set()
                            release.wait()
                            return True

                        try:
                            with (
                                mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                                mock.patch.object(Path, "exists", return_value=True),
                                mock.patch.object(Path, operation, side_effect=blocked),
                                mock.patch.object(ledger, "read_authentication_input", side_effect=AssertionError("read attempted")) as read,
                                mock.patch.object(ledger, "read_authentication_input_nofollow", side_effect=AssertionError("read attempted")) as nofollow,
                            ):
                                started = time.monotonic()
                                self.assertEqual(self.outcome(call), expected)
                                self.assertLess(time.monotonic() - started, 0.5)
                                self.assertTrue(entered.is_set())
                                self.assertTrue(workers[0].daemon)
                                read.assert_not_called()
                                nofollow.assert_not_called()
                                release.set()
                                workers[0].join(1)
                                read.assert_not_called()
                                nofollow.assert_not_called()
                        finally:
                            release.set()
                            for worker in workers:
                                worker.join(1)

    def test_probe_exceptions_are_absent_without_authentication(self):
        for operation in ("exists", "is_dir"):
            for error in (OSError("mount"), ValueError("path"), RuntimeError("probe")):
                with (
                    self.subTest(operation=operation, error=error),
                    mock.patch.object(Path, "exists", return_value=True),
                    mock.patch.object(Path, operation, side_effect=error),
                ):
                    inspect = mock.Mock(side_effect=AssertionError("inspection attempted"))
                    self.assertEqual(ledger.probe_custody(Path("/mock/custody"), inspect, lambda: "absent"), "absent")
                    inspect.assert_not_called()

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
                self.assertEqual(ledger._custody_state(original, mode="read_replay"), "complete")
                with self.assertRaisesRegex(ledger.CalibrationLedgerError, "custody_locator_override_mint_forbidden"):
                    ledger.artifact_hashes(original)
                self.assertEqual(ledger._custody_reasons([observation], backup), set())
                # A present but corrupt first root cannot be skipped for a good one.
                bad = backup / "bad/runs/member"
                bad.mkdir(parents=True)
                (bad / "manifest.json").write_bytes(b"corrupt")
                os.environ["JOULEWISE_BACKUP_ROOTS"] = str(backup / "bad") + os.pathsep + str(backup)
                self.assertEqual(ledger._custody_reasons([observation], backup),
                                 {"calibration_ledger_custody_invalid"})

    def test_governed_reads_run_on_caller_and_preserve_authentication_session(self):
        from joulewise.authentication_io import V2AuthenticationReadSession

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for name in ledger.GOVERNED_ARTIFACTS:
                artifact = root / name
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(b"{}")
            caller = threading.current_thread()
            real_read = ledger.read_authentication_input_nofollow

            def read(*args, **kwargs):
                self.assertIs(threading.current_thread(), caller)
                return real_read(*args, **kwargs)

            with V2AuthenticationReadSession() as session, mock.patch.object(
                ledger, "read_authentication_input_nofollow", side_effect=read
            ) as authenticated_read:
                ledger._governed_raw_nofollow(root)
                self.assertEqual(authenticated_read.call_count, len(ledger.GOVERNED_ARTIFACTS))
                self.assertEqual(len(session.records), len(ledger.GOVERNED_ARTIFACTS))


    def test_timed_out_probe_leaves_authentication_available_before_worker_exits(self):
        from joulewise.authentication_io import (
            V2AuthenticationReadSession, active_v2_authentication_session,
        )

        release = threading.Event()
        entered = threading.Event()
        workers = []
        worker_sessions = []
        real_exists = Path.exists

        try:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                blocked_root = root / "blocked"
                other = root / "other"
                other.mkdir()
                (other / "manifest.json").write_bytes(b"{}")

                def blocked(path):
                    if path != blocked_root:
                        return real_exists(path)
                    workers.append(threading.current_thread())
                    worker_sessions.append(active_v2_authentication_session())
                    entered.set()
                    release.wait()
                    return True

                with (
                    V2AuthenticationReadSession() as session,
                    mock.patch.object(ledger, "CUSTODY_PROBE_TIMEOUT_S", 0.05),
                    mock.patch.object(Path, "exists", blocked),
                    mock.patch.object(ledger, "read_authentication_input_nofollow",
                                      wraps=ledger.read_authentication_input_nofollow) as read,
                ):
                    with self.assertRaisesRegex(ledger.CalibrationLedgerError,
                                                "custody locator is missing"):
                        ledger._governed_raw_nofollow(blocked_root)
                    self.assertTrue(entered.is_set())
                    self.assertEqual(worker_sessions, [None])
                    read.assert_not_called()
                    self.assertTrue(workers[0].is_alive())
                    acquired = session._lock.acquire(blocking=False)
                    self.assertTrue(acquired, "timed-out probe retained authentication lock")
                    if acquired:
                        session._lock.release()
                    self.assertEqual(ledger._read_contained_nofollow(other, "manifest.json"), b"{}")
                    self.assertEqual(len(session.records), 1)
                    read.assert_called_once()
                # A subsequent session also authenticates another locator before
                # the timed-out path probe is allowed to finish.
                with V2AuthenticationReadSession() as subsequent:
                    self.assertEqual(ledger._read_contained_nofollow(other, "manifest.json"), b"{}")
                    self.assertEqual(len(subsequent.records), 1)
                self.assertTrue(workers[0].is_alive())
                release.set()
                workers[0].join(1)
                read.assert_called_once()
        finally:
            release.set()
            for worker in workers:
                worker.join(1)
