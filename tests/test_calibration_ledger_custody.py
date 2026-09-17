"""Bounded custody-state probes; all filesystem inputs are local or mocked."""

from contextvars import ContextVar
import os
import io
from contextlib import contextmanager, redirect_stderr
import hashlib
import inspect
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
            lambda: ledger.abort_calibration_session(None, None, session_id="s",
                reason="test", plan_path=None),
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
                                  slot_attempt_ids={"pre": "attempt"},
                                  session_kind=ledger.SESSION_KIND_BRACKET,
                                  declared_slots=ledger.BRACKET_SESSION_SLOTS,
                                  next_slot="pre")
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
                state.assert_called_once_with(Path("/mock/original"), mode=mode, custody_deadline=None)

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
                self.assertEqual(ledger._custody_reasons([observation], backup, mode="read_replay"), set())
                # A present but corrupt first root cannot be skipped for a good one.
                bad = backup / "bad/runs/member"
                bad.mkdir(parents=True)
                (bad / "manifest.json").write_bytes(b"corrupt")
                os.environ["JOULEWISE_BACKUP_ROOTS"] = str(backup / "bad") + os.pathsep + str(backup)
                self.assertEqual(ledger._custody_reasons([observation], backup, mode="read_replay"),
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


@contextmanager
def planted_replacement():
    """A real hash-chained observation whose original custody was removed."""
    from tests.test_calibration_ledger import CalibrationLedgerTests

    fixture = CalibrationLedgerTests()
    fixture.setUp()
    try:
        with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}):
            original = fixture._custody("planted")
            fixture._reserve("planted", original)
            receipt = fixture._finalize("planted", original)
            fixture._write_pin({
                "sequence": receipt["sequence"],
                "head_digest": receipt["receipt_digest"],
                "ledger_schema": ledger.LEDGER_SCHEMA,
            })
            assert fixture._snapshot().valid
        original_root = fixture.root / "another-root"
        replacement_root = fixture.root / "replacement"
        original_root.rename(replacement_root)
        assert not original.exists()
        with (
            mock.patch.object(ledger, "BACKUP_ROOTS", (original_root,)),
            mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": str(replacement_root)}),
        ):
            yield fixture, original, replacement_root
    finally:
        fixture.tearDown()


@contextmanager
def replacement_opens(root):
    opened = []

    def track(operation):
        def wrapped(path, *args, **kwargs):
            if isinstance(path, (str, os.PathLike)) and Path(path).is_relative_to(root):
                opened.append(str(path))
            return operation(path, *args, **kwargs)
        return wrapped

    with (
        mock.patch.object(Path, "open", track(Path.open)),
        mock.patch.object(os, "open", track(os.open)),
    ):
        yield opened


class IssuingBoundaryTests(unittest.TestCase):
    def test_signature_defaults_are_issuing(self):
        for name in ("load_calibration_ledger_snapshot", "_custody_reasons",
                     "probe_custody", "_custody_probe_paths", "_custody_state"):
            with self.subTest(function=name):
                self.assertEqual(inspect.signature(getattr(ledger, name)).parameters["mode"].default,
                                 "issuing")

    def test_bare_snapshot_rejects_planted_replacement_without_opening_it(self):
        with planted_replacement() as (fixture, original, replacement):
            with replacement_opens(replacement) as opened:
                snapshot = ledger.load_calibration_ledger_snapshot(
                    fixture.ledger, fixture.pin, require_committed_pin=False,
                    verify_custody=True,
                )
                self.assertFalse(snapshot.valid)
                self.assertEqual(snapshot.refusal_reasons, ("calibration_ledger_custody_invalid",))
                self.assertEqual(opened, [])
                replay = ledger.load_calibration_ledger_snapshot(
                    fixture.ledger, fixture.pin, require_committed_pin=False,
                    verify_custody=True, mode="read_replay",
                )
                self.assertTrue(replay.valid, replay.refusal_reasons)
                self.assertTrue(opened, "replay must authenticate actual replacement bytes")
                self.assertFalse(original.exists())

    def _assert_entry_guard(self, entry, first_seam, *args, **kwargs):
        with planted_replacement() as (_, original, replacement):
            with (
                replacement_opens(replacement) as opened,
                mock.patch.object(ledger, "probe_custody", side_effect=AssertionError("probe attempted")) as probe,
                mock.patch.object(Path, "exists", side_effect=AssertionError("path probe attempted")),
                mock.patch.object(Path, "resolve", side_effect=AssertionError("path resolution attempted")),
                mock.patch.object(threading.Thread, "start", side_effect=AssertionError("worker started")),
                mock.patch.object(*first_seam, side_effect=AssertionError("entry work before guard")) as seam,
            ):
                with self.assertRaisesRegex(ledger.CalibrationLedgerError,
                                            "custody_locator_override_mint_forbidden"):
                    entry(*args, **kwargs)
                probe.assert_not_called()
                seam.assert_not_called()
                self.assertEqual(opened, [])

    def test_runtime_dictionary_replay_cannot_bypass_mint_guard(self):
        from scripts import mint_floor_artifact as mint

        with planted_replacement() as (fixture, _, replacement):
            # Mutations via arbitrary helpers are beyond the AST census.
            options = {}
            def populate(target):
                target["".join(("mo", "de"))] = "read_replay"
            populate(options)
            snapshot = ledger.load_calibration_ledger_snapshot(
                fixture.ledger, fixture.pin, require_committed_pin=False, **options)
            self.assertTrue(snapshot.valid, snapshot.refusal_reasons)
            arguments = {name: None for name, parameter in
                         inspect.signature(mint.mint_floor_artifact).parameters.items()
                         if parameter.default is inspect.Parameter.empty}
            with (
                replacement_opens(replacement) as opened,
                mock.patch.object(mint, "_load_json_object", side_effect=AssertionError("input read")),
                self.assertRaisesRegex(ledger.CalibrationLedgerError,
                                       "custody_locator_override_mint_forbidden"),
            ):
                mint.mint_floor_artifact(**arguments)
            self.assertEqual(opened, [])

    def test_abort_entry_refuses_override_before_lease_status_or_append(self):
        self._assert_entry_guard(ledger.abort_calibration_session,
            (ledger, "CalibrationWriterLease"), None, None,
            session_id="session", reason="test", plan_path=None)

    def test_mint_entry_refuses_planted_replacement_before_probe(self):
        from scripts import mint_floor_artifact as mint
        self._assert_entry_guard(mint.mint_floor_artifact, (mint, "_load_json_object"),
            artifact_id="planted", floor_path=None, statement_path=None,
            calibration_plan_path=None, calibration_plan_relative_path="plan.json",
            absolute_paths=None, comparative_paths=None, project_commit="",
            project_tree_state="", strict_validator=None)

    def test_multi_cell_entry_refuses_planted_replacement_before_probe(self):
        from scripts import mint_floor_artifact_generalized as mint
        self._assert_entry_guard(mint.mint_multi_cell_floor_artifact,
            (mint, "active_v2_authentication_session"), pinset_path=None,
            pinset_sha256="", input_manifest_path=None, floor_path=None,
            statement_path=None, project_commit="", project_tree_state="",
            strict_validator=None)

    def test_binding_entry_refuses_planted_replacement_before_probe(self):
        from scripts import build_bracket_binding as binding
        self._assert_entry_guard(binding.main, (binding, "build_parser"), [])

    def test_finalization_entry_refuses_planted_replacement_before_probe(self):
        from joulewise import analysis_manifest_v3 as manifest
        self._assert_entry_guard(manifest.finalize_prospective_analysis_manifest_v3,
            (manifest, "_path_under_root"), Path("/unused/prospective.json"),
            plan_tree_path=None, custody_root=Path("/unused"), runs_root=None,
            whole_window_verdict_path=None, bracket_binding_path=None,
            calibration_ledger_path=None, aggregate_floor_artifact_path=None,
            output_dir=Path("/unused"))

    def test_empty_override_diagnostic_is_one_line_only_for_issuing_shortcut(self):
        original = ledger.BACKUP_ROOTS[0] / "runs/member"
        for override, mode in ((value, mode) for value in ("", ":", "::")
                               for mode in ("issuing", "read_replay")):
            stderr = io.StringIO()
            with (
                self.subTest(mode=mode, override=override),
                redirect_stderr(stderr),
                mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": override}),
                mock.patch.object(threading.Thread, "start", side_effect=AssertionError("probe")),
            ):
                self.assertEqual(ledger._custody_state(original, mode=mode), "absent")
            self.assertEqual(stderr.getvalue(),
                f"custody_backup_roots_disabled: {original}\n" if mode == "issuing" else "")


class ReservationCustodyDeadlineTests(unittest.TestCase):
    """Real CLI, committed historical ledger, successful stat then blocked read."""

    def test_successful_custody_then_expiry_at_reservation_append_boundary(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, install_reservation_append_expiry

        with CustodyFixture() as f:
            marker = install_reservation_append_expiry(f)
            before = f.bytes()
            completed, _ = f.reservation(budget=2)
            boundary = json.loads(marker.read_text())
            self.assertEqual(boundary["observations"], 3)
            self.assertLess(boundary["elapsed_before_pause"], boundary["budget_s"])
            self.assertGreater(boundary["elapsed_after_pause"], boundary["budget_s"])
            completed_passes = [json.loads(line) for line in completed.stderr.splitlines()
                                if line.startswith('{"event": "calibration_custody_complete"')]
            self.assertEqual(len(completed_passes), 1)
            self.assertEqual(completed_passes[0]["observations"], 3)
            appended = [json.loads(line)["event"] for line in
                        f.bytes()[0][len(before[0]):].splitlines()]
            self.assertEqual(completed.returncode, 2,
                             f"late expiry returned {completed.returncode}; appended_events={appended}")
            self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
            self.assertEqual(f.bytes(), before)
            self.assertEqual(appended, [])
            self.assertEqual(json.loads(f.refusal.read_text())["code"],
                             "calibration_ledger_custody_timeout")
            f.assert_lease_reacquirable()
            f.assert_workers_gone(completed)

    def test_blocked_read_refuses_before_any_append(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, BlockedArtifact
        with CustodyFixture() as f:
            before = f.bytes()
            with BlockedArtifact(f.custodies[0] / "events.jsonl") as fifo:
                try:
                    completed, elapsed = f.reservation()
                except AssertionError as exc:
                    self.assertTrue(fifo.entered.is_set(), "counterfactual must enter the actual read")
                    raise AssertionError(f"{exc}; FIFO_READ_ENTERED=1") from exc
                self.assertTrue(fifo.entered.is_set(), "FIFO writer proves artifact open was entered")
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
                self.assertLess(elapsed, 5.0, "3s budget plus 2s observed cleanup tolerance")
                self.assertEqual(f.bytes(), before)
                f.assert_lease_reacquirable()
                f.assert_workers_gone(completed)
                record = json.loads(f.refusal.read_text())
                self.assertEqual(set(record), {"schema", "code", "exit_code", "phase", "plan_id", "session_id", "existing_session", "ledger", "budget_s", "elapsed_s", "last_observation", "written_epoch_s", "pid", "detail"})
                self.assertEqual(record["schema"], "joulewise.calibration_refusal.v1")
                self.assertEqual(record["code"], "calibration_ledger_custody_timeout")
                self.assertEqual(record["phase"], "reservation")
                self.assertEqual(record["plan_id"], "custody-hang-plan")
                self.assertFalse(record["existing_session"])
                self.assertIsNone(record["session_id"])
                self.assertEqual(record["exit_code"], 2)
                self.assertEqual(record["budget_s"], 3.0)
                self.assertGreaterEqual(record["elapsed_s"], 3.0)
                self.assertEqual(record["ledger"]["head_sha256"], json.loads(before[1])["head_digest"])
                self.assertEqual(record["last_observation"]["artifact"], "events.jsonl")
                self.assertEqual(record["last_observation"]["locator"], str(f.custodies[0]))
            self.assertEqual(f.bytes(), before, "late FIFO release cannot append")
            completed, _ = f.reservation()
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "reserved")

    def test_one_budget_is_shared_by_several_observations(self):
        from contextlib import ExitStack
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, BlockedArtifact
        with CustodyFixture() as f, ExitStack() as stack:
            before = f.bytes()
            fifos = [stack.enter_context(BlockedArtifact(root / "events.jsonl", delay=1.2)) for root in f.custodies]
            completed, elapsed = f.reservation()
            self.assertTrue(all(fifo.entered.is_set() for fifo in fifos), completed.stderr)
            self.assertTrue(fifos[0].finished.is_set() and fifos[1].finished.is_set())
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
            self.assertLess(elapsed, 5)
            self.assertEqual(f.bytes(), before)
            f.assert_workers_gone(completed)

    def test_slow_success_and_corrupt_byte_keep_full_hash_comparison(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, BlockedArtifact
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt), CustodyFixture() as f:
                before = f.bytes()
                with BlockedArtifact(f.custodies[0] / "events.jsonl", delay=0.4) as fifo:
                    if corrupt:
                        # The FIFO thread takes these bytes only once a reader opens it.
                        fifo.original += b"corrupted"
                    completed, _ = f.reservation()
                    self.assertTrue(fifo.entered.is_set())
                    if corrupt:
                        self.assertEqual(completed.returncode, 2, completed.stderr)
                        self.assertIn('"code": "calibration_ledger_custody_invalid"', completed.stderr)
                        self.assertEqual(f.bytes(), before)
                    else:
                        self.assertEqual(completed.returncode, 0, completed.stderr)
                        self.assertNotEqual(f.bytes()[0], before[0])

    def test_existing_session_timeout_preserves_recovery_evidence(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, BlockedArtifact
        with CustodyFixture() as f:
            f.witness._open_session("session-new")
            # A torn later write must remain byte-identical, including residue.
            with f.ledger.open("ab") as handle:
                handle.write(b'{"torn-recovery-evidence":')
            before = f.bytes()
            with BlockedArtifact(f.custodies[0] / "events.jsonl") as fifo:
                completed, _ = f.reservation()
                self.assertTrue(fifo.entered.is_set())
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
                self.assertEqual(f.bytes(), before)
                record = json.loads(f.refusal.read_text())
                self.assertTrue(record["existing_session"])
                self.assertEqual(record["session_id"], "session-new")
                f.assert_lease_reacquirable()
                f.assert_workers_gone(completed)

    def test_verify_only_success_stall_and_mutual_exclusion(self):
        import json
        import sys
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, BlockedArtifact
        with CustodyFixture() as f:
            before = f.bytes()
            completed, _ = f.reservation(mode="--verify-only")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(len(completed.stdout.splitlines()), 2)
            readiness, receipt = map(json.loads, completed.stdout.splitlines())
            self.assertEqual(readiness["pre_reserve_readiness"], "ready")
            self.assertEqual(receipt["verify_only"], "ok")
            self.assertEqual(receipt["observations"], 3)
            self.assertEqual(receipt["ledger_head_sha256"], json.loads(before[1])["head_digest"])
            self.assertEqual(receipt["python"], sys.executable)
            self.assertEqual(set(receipt["code_digests"]), {"scripts/reserve_calibration_window_bracket.py", "joulewise/calibration_ledger.py", "joulewise/calibration_custody_worker.py"})
            for name, digest in receipt["code_digests"].items():
                self.assertEqual(digest, "sha256:" + hashlib.sha256((f.repo / name).read_bytes()).hexdigest())
            self.assertEqual(f.bytes(), before)
            completed, _ = f.reservation(mode="--verify-only", extra=("--execute",))
            self.assertEqual(completed.returncode, 2)
            self.assertIn("not allowed with argument", completed.stderr)
            with BlockedArtifact(f.custodies[0] / "events.jsonl"):
                completed, _ = f.reservation(mode="--verify-only")
                self.assertEqual(completed.returncode, 2)
                self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
            self.assertEqual(f.bytes(), before)

    def test_existing_session_never_turns_invalid_custody_into_success(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            f.witness._open_session("session-new")
            artifact = f.custodies[0] / "events.jsonl"
            artifact.write_bytes(b"corrupted")
            before = f.bytes()
            for mode in ("--verify-only", "--execute"):
                completed, _ = f.reservation(mode=mode)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertIn('"code": "calibration_ledger_custody_invalid"', completed.stderr)
                self.assertNotIn('"verify_only": "ok"', completed.stdout)
                self.assertEqual(f.bytes(), before)

    def test_refusal_document_unset_and_collision_preserve_original(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            env = dict(f.env)
            env.pop("JOULEWISE_CALIBRATION_REFUSAL_PATH")
            completed, _ = f.reservation(budget=0.000000001, env=env)
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(f.refusal.exists())
            f.refusal.write_bytes(b"original refusal\n")
            completed, _ = f.reservation(budget=0.000000001)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(f.refusal.read_bytes(), b"original refusal\n")
            siblings = list(f.repo.glob("calibration-refusal.json.*.json"))
            self.assertEqual(len(siblings), 1)
            payload = json.loads(siblings[0].read_text())
            self.assertEqual(siblings[0].name, f"calibration-refusal.json.{payload['pid']}.json")
            self.assertIn(str(siblings[0]), completed.stderr)

    def test_metadata_stall_uses_same_timeout_code(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, install_read_barrier
        with CustodyFixture() as f:
            before = f.bytes()
            marker = install_read_barrier(f, metadata=True)
            completed, _ = f.reservation(budget=0.8)
            self.assertTrue(marker.exists())
            self.assertEqual(completed.returncode, 2)
            self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
            self.assertEqual(f.bytes(), before)
            f.assert_workers_gone(completed)


class StrictReservationReadinessTests(unittest.TestCase):
    def _strict_execute(self, fixture):
        # A base-copy counterfactual must reach the old retry, not stop at an
        # argparse unknown-flag error. Current code always receives the flag.
        flags = (("--pre-reserve-strict",)
                 if "--pre-reserve-strict" in fixture.witness.reserve_script.read_text()
                 else ())
        return fixture.reservation(extra=flags)

    def _open(self, fixture):
        completed, _ = fixture.reservation()
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def _interrupt_claim(self, fixture):
        def interrupt(boundary):
            if boundary == "intent-fsynced":
                raise OSError("fixture interrupted claim")

        with self.assertRaisesRegex(OSError, "fixture interrupted claim"):
            ledger.claim_bracket_session_slot(
                fixture.ledger, session_id=fixture.state["session_id"],
                slot="pre", attempt_id=fixture.state["attempt_id"],
                _stage_boundary=interrupt,
            )

    def _assert_refusal(self, fixture, completed, before, code):
        import json
        changed = fixture.bytes() != before
        self.assertEqual(completed.returncode, 2,
                         f"strict refusal missing: exit={completed.returncode}, ledger_changed={changed}")
        self.assertIn(f'"code": "{code}"', completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(fixture.bytes(), before)
        documents = [json.loads(path.read_text()) for path in
                     fixture.refusal.parent.glob(fixture.refusal.name + "*")]
        matching = [document for document in documents if document["code"] == code]
        self.assertEqual(len(matching), 1)
        refusal = matching[0]
        self.assertEqual(refusal["phase"], "reservation")
        self.assertEqual(refusal["exit_code"], 2)
        self.assertEqual(refusal["session_id"], fixture.state["session_id"])
        self.assertTrue(refusal["existing_session"])
        passes = [json.loads(line) for line in completed.stderr.splitlines()
                  if line.startswith('{"event": "calibration_custody_complete"')]
        self.assertEqual(len(passes), 1, "strict readiness must not retry custody")
        fixture.assert_lease_reacquirable()
        fixture.assert_workers_gone(completed)

    def _read_success(self, fixture, completed):
        import json
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lines = completed.stdout.splitlines()
        self.assertIn('"pre_reserve_readiness": "ready"', lines[0],
                      "strict success omitted its readiness diagnostic")
        readiness = json.loads(lines[0])
        self.assertEqual(set(readiness), {"pre_reserve_readiness", "frozen_plan", "custody_elapsed_s"})
        self.assertEqual(readiness["frozen_plan"], {
            "path": str(fixture.state["plan"]), "plan_id": "plan-new",
            "sha256": fixture.state["plan_sha"],
            "proposed_session_id": fixture.state["session_id"],
        })
        self.assertGreaterEqual(readiness["custody_elapsed_s"], 0)
        self.assertLess(readiness["custody_elapsed_s"], 3)
        return json.loads("\n".join(lines[1:]))

    def test_interrupted_claim_strict_refuses_but_legacy_retry_recovers(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            self._open(f)
            self._interrupt_claim(f)
            before = f.bytes()
            self.assertEqual(json.loads(before[0].splitlines()[-1])["event"], "append-intent")
            completed, _ = self._strict_execute(f)
            self._assert_refusal(f, completed, before, "calibration_ledger_recovery_required")
            # Deliberately retain the G2-a retry behavior outside the night gate.
            completed, _ = f.reservation()
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "reserved")
            self.assertNotEqual(f.bytes()[0], before[0])
            self.assertEqual(f.bytes()[1], before[1])
            self.assertEqual(ledger.inspect_calibration_ledger(f.ledger).state, "clean")

    def test_open_session_strict_refuses_without_append(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            self._open(f)
            before = f.bytes()
            completed, _ = self._strict_execute(f)
            self._assert_refusal(f, completed, before, "calibration_pre_reserve_not_ready")

    def test_healthy_strict_reservation_emits_frozen_plan_and_reserves(self):
        import json
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            before = f.bytes()
            completed, _ = self._strict_execute(f)
            receipt = self._read_success(f, completed)
            self.assertEqual(receipt["status"], "reserved")
            appended = [json.loads(line)["event"] for line in
                        f.bytes()[0][len(before[0]):].splitlines()]
            self.assertEqual(appended, ["append-intent", ledger.BRACKET_SESSION_OPEN_EVENT])
            self.assertEqual(f.bytes()[1], before[1])
            self.assertEqual(completed.stderr.count('"event": "calibration_custody_complete"'), 1)

    def test_verify_only_implies_strict_gate_for_healthy_open_and_interrupted(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as f:
            before = f.bytes()
            completed, _ = f.reservation(mode="--verify-only")
            receipt = self._read_success(f, completed)
            self.assertEqual(receipt["verify_only"], "ok")
            self.assertEqual(len(completed.stdout.splitlines()), 2)
            self.assertEqual(f.bytes(), before)
            self._open(f)
            before = f.bytes()
            completed, _ = f.reservation(mode="--verify-only")
            self._assert_refusal(f, completed, before, "calibration_pre_reserve_not_ready")
            self._interrupt_claim(f)
            before = f.bytes()
            completed, _ = f.reservation(mode="--verify-only")
            self._assert_refusal(f, completed, before, "calibration_ledger_recovery_required")


if __name__ == "__main__":
    unittest.main()
