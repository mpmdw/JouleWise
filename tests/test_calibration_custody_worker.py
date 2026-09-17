"""Read-only worker protocol and whole-pass supervision regressions."""
import ast
from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise import calibration_ledger as ledger
from joulewise import calibration_custody_worker as worker


class BoundedBackupDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.root = ledger.BACKUP_ROOTS[0] / "runs/disabled-diagnostic"

    def _probe(self, operation):
        original_stat, original_open = Path.stat, Path.open

        def no_backup_io(original):
            def guarded(path, *args, **kwargs):
                self.assertFalse(path.is_relative_to(ledger.BACKUP_ROOTS[0]),
                                 f"disabled custody filesystem access: {path}")
                return original(path, *args, **kwargs)
            return guarded

        stderr = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}),
            mock.patch.object(ledger, "_bounded_custody_request",
                              side_effect=AssertionError("filesystem worker started")) as request,
            mock.patch.object(Path, "stat", no_backup_io(original_stat)),
            mock.patch.object(Path, "open", no_backup_io(original_open)),
            redirect_stderr(stderr),
        ):
            result = operation(ledger.CustodyDeadline(2))
        request.assert_not_called()
        self.assertEqual(stderr.getvalue(), f"custody_backup_roots_disabled: {self.root}\n")
        return result

    def test_bounded_state_emits_disabled_diagnostic_once_without_io(self):
        self.assertEqual(self._probe(lambda deadline: ledger._custody_state(
            self.root, custody_deadline=deadline)), "absent")

    def test_bounded_hashes_emit_disabled_diagnostic_once_without_io(self):
        self.assertEqual(self._probe(lambda deadline: ledger.artifact_hashes(
            self.root, custody_deadline=deadline)), {})

    def test_bounded_snapshot_emits_disabled_diagnostic_once_without_io(self):
        from tests import test_calibration_ledger as ledger_tests

        fixture = ledger_tests.CalibrationLedgerTests(methodName="runTest")
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        fixture._reserve("disabled-diagnostic", self.root)
        receipt = ledger.finalize_attempt_receipt(
            fixture.ledger, attempt_id="disabled-diagnostic", disposition="valid",
            custody_locator=str(self.root),
            artifact_sha256={name: "a" * 64 for name in ledger.GOVERNED_ARTIFACTS},
            identity_epoch=fixture.epoch, t1_bindings=fixture.t1,
            capture_wall_time_s="99.0", exact_bound_lexeme_s="0.025",
        )
        fixture._write_pin(ledger.head_pin_for_receipt(receipt))
        snapshot = self._probe(lambda deadline: ledger.load_calibration_ledger_snapshot(
            fixture.ledger, fixture.pin, require_committed_pin=False,
            verify_custody=True, mode="issuing", custody_deadline=deadline))
        self.assertEqual(len(snapshot.observations), 1)
        self.assertEqual(snapshot.refusal_reasons, (ledger.RefusalCode.LEDGER_CUSTODY_INVALID.value,))


class CustodyWorkerTests(unittest.TestCase):
    def test_worker_cannot_append_even_when_request_names_writable_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            original = b"writable ledger bytes\n"
            path.write_bytes(original)
            request = {"request_id": "read-only", "remaining_budget_s": 2,
                       "ledger_path": str(path), "operation": "verify",
                       "observations": [{"observation_id": "a", "locator": tmp,
                                         "disposition": "valid", "artifact_sha256": {
                                             "ledger.jsonl": hashlib.sha256(original).hexdigest()}}]}
            code = (
                "import runpy,sys; "
                "from joulewise.calibration_custody_worker import main; "
                "rc=main(); "
                "assert 'joulewise.calibration_ledger' not in sys.modules; "
                "raise SystemExit(rc)"
            )
            completed = subprocess.run([sys.executable, "-B", "-c", code],
                                       input=json.dumps(request), text=True,
                                       capture_output=True, timeout=3)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            response = json.loads(completed.stdout.splitlines()[-1])
            self.assertEqual(response["request_id"], "read-only")
            self.assertEqual(response["result"]["reasons"], [])
            self.assertEqual(response["result"]["observations"], 1)
            self.assertEqual(path.read_bytes(), original)
            tree = ast.parse(Path(worker.__file__).read_text())
            imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            self.assertNotIn("joulewise.calibration_ledger", imports)

    def test_worker_shares_the_exact_byte_comparison_core(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact"
            path.write_bytes(b"good")
            request = {"request_id": "hash", "remaining_budget_s": 2,
                       "observations": [{"observation_id": "a", "locator": tmp,
                                         "disposition": "valid", "artifact_sha256": {
                                             "artifact": hashlib.sha256(b"bad").hexdigest()}}]}
            progress = []
            result = worker.run_request(request, progress.append)
            self.assertEqual(result["result"]["reasons"], [ledger.RefusalCode.LEDGER_CUSTODY_INVALID.value])
            self.assertEqual(progress[0]["progress"]["stage"], "metadata_probe")
            self.assertEqual(progress[1]["progress"]["artifact"], "artifact")

    def test_bounded_route_preserves_empty_backup_override_without_io(self):
        from types import SimpleNamespace
        root = ledger.BACKUP_ROOTS[0] / "runs/disabled"
        with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}), mock.patch.object(ledger, "_bounded_custody_request", side_effect=AssertionError("filesystem worker started")):
            deadline = ledger.CustodyDeadline(2)
            self.assertEqual(ledger._custody_state(root, custody_deadline=deadline), "absent")
            self.assertEqual(ledger.artifact_hashes(root, custody_deadline=deadline), {})
            observation = SimpleNamespace(custody_locator=str(root), attempt_id="a",
                                          disposition="valid", artifact_sha256={"events.jsonl": "a" * 64})
            self.assertEqual(ledger.bounded_custody_reasons([observation], root, deadline),
                             {"calibration_ledger_custody_invalid"})

    def test_deadline_clip_and_expired_window_keep_distinct_codes(self):
        deadline = ledger.CustodyDeadline(30, time.time() + 0.1)
        self.assertLess(deadline.budget_s, 0.2)
        with mock.patch.object(ledger.time, "time", return_value=time.time() - 3600):
            renewed = deadline.next_operation()
        self.assertEqual(renewed.window_deadline, deadline.window_deadline)
        self.assertEqual(renewed.deadline, deadline.deadline)
        with mock.patch.object(ledger.time, "monotonic", return_value=deadline.deadline + 1):
            with self.assertRaises(ledger.CalibrationLedgerError) as raised:
                deadline.check()
        self.assertEqual(raised.exception.code, ledger.RefusalCode.LEDGER_CUSTODY_TIMEOUT)
        with self.assertRaises(ledger.CalibrationLedgerError) as raised:
            ledger.CustodyDeadline(30, time.time() - 1)
        self.assertEqual(raised.exception.code, ledger.RefusalCode.WINDOW_EXHAUSTED)
        for budget in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                ledger.CustodyDeadline(budget)

    def test_protocol_requires_exact_request_complete_response_and_normal_exit(self):
        # Exercise the real parent IPC with a deliberately non-conforming child.
        real_popen = subprocess.Popen
        cases = (
            "print('[]')",
            "print(json.dumps({'request_id':q['request_id'],'progress':[]}))",
            "print(json.dumps({'request_id':'wrong','result':r}))",
            "print(json.dumps({'request_id':q['request_id'],'result':r}));sys.exit(9)",
            "print(json.dumps({'request_id':q['request_id'],'result':dict(r,observations=9)}))",
            "print(json.dumps({'request_id':q['request_id'],'progress':{}}))",
            "r.pop('elapsed_s');print(json.dumps({'request_id':q['request_id'],'result':r}))",
        )
        for response in cases:
            with self.subTest(response=response):
                code = "import json,sys;q=json.load(sys.stdin);r={'reasons':[],'observations':0,'elapsed_s':0.0};" + response
                launches = []
                def spawn(_args, **kwargs):
                    launches.append(dict(kwargs))
                    return real_popen([sys.executable, "-B", "-c", code], **kwargs)
                with mock.patch.object(ledger.subprocess, "Popen", side_effect=spawn), redirect_stderr(io.StringIO()):
                    with self.assertRaises(ledger.CalibrationLedgerError) as raised:
                        ledger._bounded_custody_request({"observations": []}, ledger.CustodyDeadline(2))
                self.assertEqual(raised.exception.code, ledger.RefusalCode.LEDGER_CUSTODY_INVALID)
                # Spawn catches exceptions: assertions there can masquerade as
                # the protocol refusal this test expects. Assert on this thread.
                self.assertEqual(len(launches), 1)
                self.assertIs(launches[0]["close_fds"], True)
                self.assertIs(launches[0]["start_new_session"], False)
                self.assertEqual(launches[0].get("pass_fds", ()), ())

    def test_valid_worker_cannot_inherit_parent_writable_descriptor(self):
        import fcntl

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scratch = root / "parent-writable"
            scratch.write_bytes(b"parent-only bytes")
            evidence = root / "evidence"
            evidence.write_bytes(b"authenticated bytes")
            with scratch.open("r+b") as handle:
                descriptor = fcntl.fcntl(handle.fileno(), fcntl.F_DUPFD, 64)
            try:
                # Python defaults descriptors to non-inheritable. Explicitly
                # defeat that default so only close_fds protects this file.
                os.set_inheritable(descriptor, True)
                real_popen = subprocess.Popen
                launches = []
                # This bootstrap always attempts the write before invoking the
                # real worker main. A complete valid response proves it ran;
                # unchanged scratch bytes prove the writable fd was closed.
                # A high fd avoids accidental reuse by the child's stdio pipes.
                probe = (
                    "import errno,os\n"
                    f"try: os.write({descriptor}, b'CHILD INHERITED WRITER FD')\n"
                    "except OSError as exc:\n"
                    " if exc.errno != errno.EBADF: raise\n"
                    "from joulewise.calibration_custody_worker import main\n"
                    "raise SystemExit(main())\n"
                )
                def spawn(args, **kwargs):
                    launches.append((list(args), dict(kwargs)))
                    return real_popen([sys.executable, "-B", "-c", probe], **kwargs)

                with mock.patch.object(ledger.subprocess, "Popen", side_effect=spawn), redirect_stderr(io.StringIO()):
                    result = ledger._bounded_custody_request({"observations": [{
                        "observation_id": "descriptor-probe", "locator": str(root),
                        "disposition": "valid", "artifact_sha256": {
                            "evidence": hashlib.sha256(evidence.read_bytes()).hexdigest()},
                    }]}, ledger.CustodyDeadline(3))
                self.assertEqual(result["reasons"], [])
                self.assertEqual(result["observations"], 1)
                self.assertEqual(scratch.read_bytes(), b"parent-only bytes",
                                 "real worker inherited the parent's writable descriptor")
                self.assertEqual(len(launches), 1)
                args, kwargs = launches[0]
                self.assertEqual(args[-2:], ["-m", "joulewise.calibration_custody_worker"])
                self.assertIs(kwargs["close_fds"], True)
                self.assertEqual(kwargs.get("pass_fds", ()), ())
            finally:
                os.close(descriptor)

    def test_complete_result_with_stalled_exit_is_still_timeout_and_killed(self):
        real_popen = subprocess.Popen
        children = []
        code = ("import json,sys,time,signal;signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                "q=json.load(sys.stdin);print(json.dumps({'request_id':q['request_id'],"
                "'result':{'reasons':[],'observations':0,'elapsed_s':0.0}}),flush=True);time.sleep(30)")
        def spawn(_args, **kwargs):
            child = real_popen([sys.executable, "-B", "-c", code], **kwargs)
            children.append(child)
            return child
        started = time.monotonic()
        with mock.patch.object(ledger.subprocess, "Popen", side_effect=spawn), redirect_stderr(io.StringIO()):
            with self.assertRaises(ledger.CalibrationLedgerError) as raised:
                ledger._bounded_custody_request({"observations": []}, ledger.CustodyDeadline(0.2))
        self.assertEqual(raised.exception.code, ledger.RefusalCode.LEDGER_CUSTODY_TIMEOUT)
        self.assertLess(time.monotonic() - started, 2)
        self.assertTrue(all(child.poll() is not None for child in children))

    def test_expiry_during_spawn_start_still_assigns_child_cleanup(self):
        real_start = ledger.threading.Thread.start
        children = []
        real_popen = subprocess.Popen
        def start(thread):
            real_start(thread)
            time.sleep(0.03)
        def spawn(_args, **kwargs):
            child = real_popen([sys.executable, "-B", "-c", "import time;time.sleep(30)"], **kwargs)
            children.append(child)
            return child
        with mock.patch.object(ledger.threading.Thread, "start", side_effect=start, autospec=True), mock.patch.object(ledger.subprocess, "Popen", side_effect=spawn):
            with self.assertRaises(ledger.CalibrationLedgerError) as raised:
                ledger._bounded_custody_request({"observations": []}, ledger.CustodyDeadline(0.01))
        self.assertEqual(raised.exception.code, ledger.RefusalCode.LEDGER_CUSTODY_TIMEOUT)
        self.assertEqual(len(children), 1)
        children[0].wait(timeout=2)
        self.assertIsNotNone(children[0].returncode)

    def test_spawn_wait_is_bounded_and_late_child_is_reaped(self):
        import threading
        real_popen = subprocess.Popen
        children = []
        entered = threading.Event()
        release = threading.Event()
        finished = threading.Event()
        def spawn(_args, **kwargs):
            entered.set()
            # A finite backstop keeps a broken parent from hanging the suite.
            # The successful path releases this barrier only after refusal.
            release.wait(5)
            child = real_popen([sys.executable, "-B", "-c", "import time;time.sleep(30)"], **kwargs)
            children.append(child)
            finished.set()
            return child
        started = time.monotonic()
        try:
            with mock.patch.object(ledger.subprocess, "Popen", side_effect=spawn):
                with self.assertRaises(ledger.CalibrationLedgerError) as raised:
                    ledger._bounded_custody_request({"observations": []}, ledger.CustodyDeadline(0.05))
            self.assertEqual(raised.exception.code, ledger.RefusalCode.LEDGER_CUSTODY_TIMEOUT)
            self.assertLess(time.monotonic() - started, 2)
            self.assertTrue(entered.wait(2))
            self.assertFalse(finished.is_set(), "parent waited for the blocked launch")
        finally:
            release.set()
            self.assertTrue(finished.wait(2))
            try:
                children[0].wait(timeout=2)
            finally:
                if children[0].poll() is None:
                    children[0].kill()
                    children[0].wait(timeout=2)
        self.assertIsNotNone(children[0].returncode)


if __name__ == "__main__":
    unittest.main()
