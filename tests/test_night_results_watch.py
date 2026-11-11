"""Synthetic records only. The transport integration uses a local bare repo."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock

from scripts.air import night_results_watch as w
from tests.git_fixture import init_git_fixture


REF = w.PREFIX + "synthetic"
A, B, C = "a" * 40, "b" * 40, "c" * 40
WORDS = types.SimpleNamespace(PLAN_WORDS={"complete", "refused", "failed", "stopped", "usage", "hold", "aborted"})


def encoded(doc):
    return json.dumps(doc).encode()


def records(*, verdict="GO", rc=0, fault=False, reasons=None, prefix="night/", started=True):
    doc = {"verdict": verdict, "chain_exit_code": rc, "fault": fault,
           "fault_reasons": reasons or [], "ended_epoch_s": 1000}
    files = {prefix + "result.json": encoded(doc)}
    if started:
        files[prefix + "chain.started"] = b"{}"
        files[prefix + "chain.exited"] = encoded({"exit_code": rc})
    return files


class FakeGit:
    def __init__(self, files=None):
        self.refs = {REF: A}
        self.files = files if files is not None else records()
        self.shown, self.fetched = [], []
        self.fail_ls = self.fail_fetch = False

    def ls_remote(self, pattern):
        assert pattern == w.PREFIX + "*"
        if self.fail_ls:
            raise w.WatchError("secret transport detail")
        return dict(self.refs)

    def fetch(self, ref):
        self.fetched.append(ref)
        if self.fail_fetch:
            raise w.WatchError("secret fetch detail")

    def list_tree(self, ref):
        return set(self.files)

    def show(self, ref, path):
        self.shown.append(path)
        return self.files[path]


def running(git=None, **kwargs):
    git = git or FakeGit()
    watcher = w.Watcher(git, w.empty_state(), **kwargs)
    watcher.poll(1000)  # baseline
    git.refs[REF] = B
    return watcher, git


def codes(events, level=None):
    return {e.code for e in events if level is None or e.level == level}


class ResultsTests(unittest.TestCase):
    def test_outcome_branches_and_historical_failures(self):
        cases = [
            ({}, "MEASURED_OK", False, False),
            ({"rc": 3}, "CHAIN_FAILED", True, False),  # historical GO + exit 3
            ({"verdict": "REFUSED", "rc": None, "started": False}, "REFUSED_PRE_CHAIN", True, False),
            ({"verdict": "ABORTED", "rc": None, "started": False}, "ABORTED", True, False),
            ({"verdict": "unrecognised"}, "UNKNOWN", True, False),
            ({"fault": True, "reasons": ["synthetic"]}, "MEASURED_WITH_FLAGS", False, True),
        ]
        for args, outcome, alarm, notice in cases:
            with self.subTest(args=args):
                watcher, _ = running(FakeGit(records(**args)))
                events = watcher.poll(1001)
                self.assertIn("outcome=" + outcome, events[0].fields)
                self.assertEqual("RESULT_NOT_MEASURED" in codes(events), alarm)
                self.assertEqual("RESULT_WITH_FLAGS" in codes(events), notice)

    def test_invariants_positive_and_negative(self):
        cases = [
            (records(started=False), "GO_WITHOUT_CHAIN_STARTED"),
            ({"night/chain.exited": b'{"exit_code": 0}'}, "CHAIN_EXITED_WITHOUT_CHAIN_STARTED"),
            (records(rc=3), "NONZERO_EXIT_WITHOUT_FAULT"),
            (records() | {"night/r1_result.json": b'{"status":"refused"}', "night/r1_slots.json": b"secret"}, "PAYLOAD_EXIT_MISMATCH"),
            (records() | {"night/r1_slots.json": b"secret"}, None),
            (records(rc=3, fault=True) | {"night/r1_slots.json": b"secret"}, "PAYLOAD_SLOTS_MISMATCH"),
            (records() | {"night/courier.sent": b"secret"}, "COURIER_SENT_WITHOUT_DELIVERY"),
        ]
        for files, code in cases:
            with self.subTest(code=code):
                watcher, _ = running(FakeGit(files))
                actual = codes(watcher.poll(1001))
                if code:
                    self.assertIn("INVARIANT_VIOLATED:" + code, actual)
        watcher, _ = running()
        self.assertFalse(any(c.startswith("INVARIANT_VIOLATED:") for c in codes(watcher.poll(1001))))

    def test_missing_result_and_malformed_record_are_unknown(self):
        for files in ({}, {"night/chain.started": b"{}"},
                      {"night/result.json": b"private malformed record"},
                      {"night/result.json": b"[]"},
                      records() | {"night/chain.exited": b"invalid"}):
            with self.subTest(files=list(files)):
                watcher, _ = running(FakeGit(files))
                events = watcher.poll(1001)
                self.assertIn("RESULT_NOT_MEASURED", codes(events))
                self.assertIn("outcome=UNKNOWN", events[0].fields)

    def test_all_layouts_and_no_mixing(self):
        for prefix in ("synthetic/", "night/", ""):
            with self.subTest(prefix=prefix):
                summary = w.inspect_ref(FakeGit(records(prefix=prefix)), REF, A, 1001)
                self.assertEqual(summary.outcome, "MEASURED_OK")
        files = records(prefix="synthetic/", started=False) | records()
        self.assertEqual(w.inspect_ref(FakeGit(files), REF, A, 1001).outcome, "UNKNOWN")

    def test_both_payload_locations_and_courier_generations(self):
        for payload in w.PAYLOADS:
            files = records() | {"night/" + payload: b'{"status":"complete"}',
                                 "night/" + payload.replace("result", "slots"): b"SEALED"}
            self.assertEqual(w.inspect_ref(FakeGit(files), REF, A, 1001).outcome, "MEASURED_OK")
        for delivery in (
            {"night/courier.json": encoded({"sent": True, "message_id": "private-id"})},
            {"night/courier.delivery.json": encoded({"transport": "git-push", "commit": A,
                                                      "result_sha256": "b" * 64, "ref": REF})},
            {"night_plan.json": encoded({"t0_epoch_s": 1000, "window_max_s": 1, "courier_mode": "file-only"})},
        ):
            with self.subTest(delivery=list(delivery)):
                summary = w.inspect_ref(FakeGit(records() | delivery | {"night/courier.sent": b"secret"}), REF, A, 1001)
                self.assertNotIn("COURIER_SENT_WITHOUT_DELIVERY", summary.invariants)
                self.assertEqual(summary.state, "Delivered")

    def test_hazard_nested_fault_count_and_chain_exit(self):
        files = records() | {"night/hazard_result.json": encoded({"verdict": "GO", "chain": {"exit_code": 0},
                                                                 "faults": {"reasons": ["one", "two"]}})}
        summary = w.inspect_ref(FakeGit(files), REF, A, 1001)
        self.assertEqual((summary.outcome, summary.fault_reason_count), ("MEASURED_WITH_FLAGS", 2))

    def test_blinding_at_show_temp_and_stdout_boundaries(self):
        secret = "PRIVATE_OUTCOME_TOKEN_" * 10000
        files = records(reasons=[secret]) | {
            "night/outcomes.json": encoded({"accuracy": secret}),
            "night/align-r1/r1_slots.json": secret.encode(),
            "night/receipt.json": secret.encode(),
            "night/result.json": encoded({"verdict": "GO", "chain_exit_code": 0, "fault": True,
                                           "fault_reasons": [secret], "payload": secret, "plan_id": secret}),
            "night/r1_result.json": encoded({"status": "complete", "outcome": secret}),
            "night/r1_slots.json": secret.encode(),
            "night_plan.json": encoded({"t0_epoch_s": 1000, "window_max_s": 100, "custody_root": secret}),
        }
        git = FakeGit(files)
        observe = w.ws.observe_night_dir
        checked = []

        def inspect_temp(path, **kwargs):
            all_files = {str(p.relative_to(path)): p.read_bytes() for p in Path(path).rglob("*") if p.is_file()}
            self.assertFalse(any(b"PRIVATE_OUTCOME_TOKEN" in v for v in all_files.values()))
            self.assertNotIn("night/outcomes.json", all_files)
            prefix = "" if kwargs.get("_night_only") else "night/"
            self.assertEqual(all_files[prefix + "r1_slots.json"], b"")
            self.assertEqual(all_files[prefix + "receipt.json"], b"")
            checked.append(True)
            return observe(path, **kwargs)

        with mock.patch.object(w.ws, "observe_night_dir", side_effect=inspect_temp):
            summary = w.inspect_ref(git, REF, A, 1001)
        output = "\n".join(e.line(1001) for e in w.result_events(REF, A, summary))
        self.assertTrue(checked)
        self.assertNotIn("PRIVATE_OUTCOME_TOKEN", output)
        self.assertEqual(summary.fault_reason_count, 1)
        self.assertEqual(set(git.shown), {"night_plan.json", "night/result.json", "night/chain.started",
                                          "night/chain.exited", "night/r1_result.json"})
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(w, "Git", return_value=git), \
             mock.patch.object(w, "optional_exit_module", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = w.main(["--once", "--since-epoch", "0", "--state", str(Path(d) / "state"),
                         "--current", str(Path(d) / "absent")])
        # The deliberately orphaned second slots record is incomplete evidence.
        self.assertEqual(rc, 20)
        self.assertNotIn("PRIVATE_OUTCOME_TOKEN", stdout.getvalue())

    def test_invalid_strings_are_not_copied_or_successful(self):
        files = records(verdict="SECRET" * 10000)
        summary = w.inspect_ref(FakeGit(files), REF, A, 1001)
        self.assertEqual(summary.outcome, "UNKNOWN")
        self.assertNotIn("SECRET", summary.fields())

    def test_plan_errors_cannot_become_success_and_time_invariants(self):
        files = records() | {"night_plan.json": encoded({"t0_epoch_s": "secret", "window_max_s": 1})}
        self.assertEqual(w.inspect_ref(FakeGit(files), REF, A, 1001).outcome, "UNKNOWN")
        plan = {"night_plan.json": encoded({"t0_epoch_s": 1000, "window_max_s": 1})}
        for files, now, expected in (
            (plan, 1901, "NO_NIGHT_RECORD_AFTER_T0"),
            (plan | {"night/chain.started": b"{}"}, 1302, "CHAIN_OPEN_PAST_COMPLETION"),
            ({"night/courier.sent": b"secret"}, 1001, "COURIER_SENT_WITHOUT_RESULT"),
            (records() | {"night/hazard_result.json": encoded({"verdict": "GO", "chain_outcome": "CHAIN_FAILED"})},
             1001, "RECORDED_OUTCOME_DISAGREES"),
        ):
            with self.subTest(expected=expected):
                summary = w.inspect_ref(FakeGit(files), REF, A, now)
                self.assertIn("INVARIANT_VIOLATED:" + expected, codes(w.result_events(REF, A, summary)))
        for files, now in ((plan, 1900), (plan | {"night/chain.started": b"{}"}, 1301)):
            summary = w.inspect_ref(FakeGit(files), REF, A, now)
            self.assertNotIn("NO_NIGHT_RECORD_AFTER_T0", summary.invariants)
            self.assertNotIn("CHAIN_OPEN_PAST_COMPLETION", summary.invariants)
        # Unknown remote plist facts can never establish stranded/uninstalled.
        summary = w.inspect_ref(FakeGit(records()), REF, A, 99999)
        self.assertNotIn(summary.state, {"Stranded", "Uninstalled"})

    def test_plan_contract_adapter_uses_plan_words(self):
        declaration = {"exit_contract": {"0": "complete", "3": "refused", "8": "aborted"}}
        self.assertEqual(w.declared_contract(declaration, WORDS), {0: "complete", 3: "refused", 8: "aborted"})
        self.assertEqual(w.declared_contract(declaration, None), {0: "complete", 3: "refused", 8: "aborted"})
        self.assertIsNone(w.declared_contract({}, WORDS))
        for bad in ([], {"bad": "complete"}, {"00": "complete"}, {"-1": "failed"},
                    {"0": "MEASURED_OK"}, {"0": []}):
            with self.subTest(bad=bad), self.assertRaises(w.WatchError):
                w.declared_contract({"exit_contract": bad}, WORDS)

    def test_optional_module_file_guard_and_import_error(self):
        with mock.patch.object(Path, "is_file", return_value=False), mock.patch.object(w.importlib, "import_module") as imp:
            self.assertIsNone(w.optional_exit_module())
            imp.assert_not_called()
        with mock.patch.object(Path, "is_file", return_value=True), mock.patch.object(w.importlib, "import_module", return_value=WORDS):
            self.assertIs(w.optional_exit_module(), WORDS)
        with mock.patch.object(Path, "is_file", return_value=True), mock.patch.object(w.importlib, "import_module", side_effect=ImportError):
            self.assertIsNone(w.optional_exit_module())

    def test_contract_passed_to_window_outcome_and_changes_classification(self):
        for raw, expected in (({"0": "complete"}, "MEASURED_OK"), ({}, "CHAIN_FAILED"),
                              ({"0": "failed"}, "CHAIN_FAILED"), ({"0": "aborted"}, "ABORTED")):
            with self.subTest(raw=raw):
                files = records() | {"night_plan.json": encoded({"t0_epoch_s": 1000, "window_max_s": 100, "exit_contract": raw})}
                with mock.patch.object(w.ws, "window_outcome", wraps=w.ws.window_outcome) as classify:
                    report = w.inspect_ref(FakeGit(files), REF, A, 1001, WORDS)
                self.assertEqual(classify.call_args.kwargs["exit_contract"], {int(k): v for k, v in raw.items()})
                self.assertEqual(report.outcome, expected)
        files = records() | {"night_plan.json": encoded({"t0_epoch_s": 1000, "window_max_s": 100,
                                                         "exit_contract": {"0": "failed"}})}
        self.assertEqual(w.inspect_ref(FakeGit(files), REF, A, 1001).outcome, "CHAIN_FAILED")


class TimingTests(unittest.TestCase):
    def context(self, refs=None, results=None, now=1001, **current):
        return w.context_events(refs or {}, results or {}, current, now, 100, 10)

    def test_early_boundaries_and_unarmed(self):
        armed = {"plan_id": "synthetic", "t0_epoch_s": 1000}
        self.assertIn("RESULT_EARLY", codes(self.context(refs={REF: A}, armed=armed)))
        for now in (1100, 1101):
            self.assertNotIn("RESULT_EARLY", codes(self.context(refs={REF: A}, now=now, armed=armed)))
        self.assertNotIn("RESULT_EARLY", codes(self.context(refs={REF: A})))
        self.assertNotIn("RESULT_EARLY", codes(self.context(armed=armed)))

    def test_latest_end_boundaries_and_presence(self):
        armed = {"plan_id": "synthetic", "latest_end_epoch_s": 990}
        self.assertIn("ARMED_NO_RESULT_PAST_LATEST_END", codes(self.context(armed=armed)))
        for kw in ({"now": 1000}, {"refs": {REF: A}}):
            self.assertNotIn("ARMED_NO_RESULT_PAST_LATEST_END", codes(self.context(armed=armed, **kw)))
        self.assertEqual(self.context(), [])

    def test_deadlines_observables_positive_negative_and_boundary(self):
        for observable in ("results_branch_exists", "result_json_exists"):
            wait = {"observable": observable, "plan_id": "synthetic", "deadline_epoch_s": 1000}
            self.assertIn("DEADLINE_PASSED", codes(self.context(wait=wait)))
            self.assertEqual(self.context(wait=wait, now=1000), [])
            self.assertEqual(self.context(wait=wait, refs={REF: A}, results={REF: True}), [])
            if observable == "result_json_exists":
                self.assertIn("DEADLINE_PASSED", codes(self.context(wait=wait, refs={REF: A}, results={REF: False})))
        wait = {"observable": {"kind": "result_json_exists", "plan_id": "synthetic"}, "deadline_epoch_s": 1000}
        self.assertEqual(self.context(wait=wait, results={REF: True}), [])

    def test_unchecked_observable_and_missing_target(self):
        for observable, expected in (("mail_received", "mail_received"), ("SECRET\ntext", "UNKNOWN"),
                                     (None, "UNKNOWN"), ("result_json_exists", "result_json_exists")):
            with self.subTest(observable=observable):
                wait = {"observable": observable, "deadline_epoch_s": 1000}
                events = self.context(wait=wait)
                self.assertEqual(codes(events), {"DEADLINE_PASSED_UNCHECKED:" + expected})
                self.assertEqual(self.context(wait=wait, now=1000), [])

    def test_current_present_absent_and_no_generator_import(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "CURRENT.json"
            self.assertEqual(w.read_current(path), {})
            doc = {"armed": {"plan_id": "synthetic", "t0": 1000},
                   "wait": {"observable": "result_json_exists", "deadline_epoch_s": 1000}}
            path.write_bytes(encoded(doc))
            with mock.patch.object(w.importlib, "import_module", side_effect=AssertionError("no generator import")):
                self.assertEqual(w.read_current(path), doc)
            path.write_bytes(encoded({"armed": []}))
            with self.assertRaises(w.WatchError):
                w.read_current(path)
            for doc in ({"armed": {"t0": "bad"}}, {"wait": {"observable": "mail_received"}}):
                path.write_bytes(encoded(doc))
                with self.assertRaises(w.WatchError):
                    w.read_current(path)


class PollStateTests(unittest.TestCase):
    def test_first_baseline_quiet_and_since_filter(self):
        git = FakeGit()
        watcher = w.Watcher(git, w.empty_state())
        self.assertEqual(watcher.poll(1001), [])
        self.assertEqual(git.shown, [])
        for since, expected in ((999, True), (1000, True), (1001, False)):
            watcher = w.Watcher(git, w.empty_state(), since=since)
            self.assertEqual(bool(watcher.poll(1002)), expected)
        watcher = w.Watcher(FakeGit({}), w.empty_state(), since=1001)
        self.assertIn("RESULT_NOT_MEASURED", codes(watcher.poll(1002)))

    def test_new_moved_twice_and_restart_deduplication(self):
        watcher, git = running(FakeGit(records(rc=3)))
        self.assertIn("RESULT_NOT_MEASURED", codes(watcher.poll(1001)))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "state.json"
            w.save_state(path, watcher.state)
            restored = w.Watcher(git, w.load_state(path))
            self.assertEqual(restored.poll(1002), [])
            git.refs[REF] = C
            self.assertIn("RESULT_NOT_MEASURED", codes(restored.poll(1003)))
            # A different plan appeared during downtime.
            git.refs[w.PREFIX + "another"] = A
            again = w.Watcher(git, w.load_state(path))
            events = again.poll(1004)
            self.assertTrue(any(e.subject.endswith("another") for e in events))

    def test_deletion_and_reappearance(self):
        watcher, git = running()
        watcher.poll(1001)
        git.refs = {}
        watcher.poll(1002)
        self.assertEqual(watcher.state["refs"], {})
        git.refs = {REF: C}
        self.assertIn("RESULT", codes(watcher.poll(1003)))

    def test_incomplete_branch_later_moves_to_result(self):
        watcher, git = running(FakeGit({}))
        self.assertIn("RESULT_NOT_MEASURED", codes(watcher.poll(1001)))
        git.files, git.refs[REF] = records(), C
        events = watcher.poll(1002)
        self.assertIn("RESULT", codes(events))
        self.assertNotIn("RESULT_NOT_MEASURED", codes(events))

    def test_fetch_failure_is_alarm_and_retry_survives_restart(self):
        watcher, git = running()
        git.fail_fetch = True
        self.assertIn("REF_READ_FAILED", codes(watcher.poll(1001)))
        self.assertEqual(watcher.state["refs"][REF], A)
        git.fail_fetch = False
        restarted = w.Watcher(git, json.loads(json.dumps(watcher.state)))
        self.assertIn("RESULT", codes(restarted.poll(1002)))

    def test_ls_failure_count_time_silence_and_recovery(self):
        watcher, git = running(silence_s=100, failure_limit=3)
        git.fail_ls = True
        self.assertEqual(codes(watcher.poll(1001)), {"LS_REMOTE_FAILED"})
        self.assertEqual(codes(watcher.poll(1002)), {"LS_REMOTE_FAILED"})
        self.assertIn("SILENCE", codes(watcher.poll(1003)))
        self.assertNotIn("SILENCE", codes(watcher.poll(1004)))
        git.fail_ls = False
        watcher.poll(1005)
        self.assertEqual(watcher.state["failures"], 0)
        git.fail_ls = True
        self.assertIn("SILENCE", codes(watcher.poll(1105)))
        self.assertNotIn("secret", " ".join(e.line(1105) for e in watcher.poll(1106)))

    def test_initial_outage_and_no_false_absence_claims(self):
        git = FakeGit()
        git.fail_ls = True
        watcher = w.Watcher(git, w.empty_state(), failure_limit=9, silence_s=10)
        current = {"armed": {"plan_id": "synthetic", "latest_end_epoch_s": 1}}
        self.assertNotIn("SILENCE", codes(watcher.poll(1000, current)))
        self.assertEqual(codes(watcher.poll(1010, current)), {"LS_REMOTE_FAILED", "SILENCE"})
        self.assertFalse(watcher.state["initialized"])

    def test_baseline_can_satisfy_result_deadline_without_reading_blobs(self):
        git = FakeGit()
        current = {"armed": {"plan_id": "synthetic"},
                   "wait": {"observable": "result_json_exists", "deadline_epoch_s": 1000}}
        watcher = w.Watcher(git, w.empty_state())
        self.assertEqual(watcher.poll(1001, current), [])
        self.assertEqual(git.shown, [])
        git.files = {}
        self.assertIn("DEADLINE_PASSED", codes(watcher.poll(1002, current)))

    def test_state_atomic_round_trip_and_invalid_state(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "nested/state.json"
            self.assertEqual(w.load_state(path), w.empty_state())
            state = w.empty_state()
            w.save_state(path, state)
            self.assertEqual(w.load_state(path), state)
            with mock.patch.object(w.os, "replace", side_effect=OSError):
                with self.assertRaises(OSError):
                    w.save_state(path, dict(state, initialized=True))
            self.assertEqual(w.load_state(path), state)
            self.assertEqual(list(path.parent.iterdir()), [path])
            for bad in ({}, dict(state, version=2), dict(state, refs={REF: "bad"}),
                        dict(state, failures=-1), dict(state, active=["bad"]),
                        dict(state, raised=[{}]), dict(state, last_success="bad")):
                path.write_bytes(encoded(bad))
                with self.subTest(bad=bad), self.assertRaises(w.WatchError):
                    w.load_state(path)


class EdgesTests(unittest.TestCase):
    def test_invalid_json_duplicate_nonfinite_oversize_not_object(self):
        for raw in (b"{", b"[]", b'{"x":1,"x":2}', b'{"x":NaN}', b"\xff", b" " * (w.MAX_RECORD + 1)):
            with self.subTest(raw=raw[:30]), self.assertRaises(w.WatchError):
                w.parse_object(raw)

    def test_projection_preserves_invalid_fields_and_scrubs_identifiers(self):
        self.assertEqual(w.project({"message_id": "private", "mail_message_id": " "}),
                         {"message_id": "recorded", "mail_message_id": []})
        self.assertEqual(w.project({"chain": False, "faults": [], "fault_reasons": [""]}),
                         {"chain": False, "faults": False, "fault_reasons": False})
        for key in ("verdict", "fault", "status", "transport", "commit", "result_sha256", "ref",
                    "chain_exit_code", "ended_epoch_s", "courier_mode", "window_max_s"):
            with self.subTest(key=key):
                self.assertEqual(w.project({key: "PRIVATE"})[key], [])

    def test_ref_validation(self):
        for value in ("../secret", "bad\nline", "a.lock", "a.", "a..b", "", "/x"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                w.plan_id(value)
        self.assertEqual(w.plan_id("night-2026_11.11"), "night-2026_11.11")

    def test_git_transport_controls_timeout_and_errors(self):
        proc = mock.Mock(returncode=0)
        proc.communicate.return_value = (b"", None)
        with mock.patch.object(w.subprocess, "Popen", return_value=proc) as popen:
            w.Git("/synthetic").ls_remote(w.PREFIX + "*")
        argv = popen.call_args.args[0]
        env = popen.call_args.kwargs["env"]
        for setting in ("gc.auto=0", "protocol.allow=never", "protocol.https.allow=always"):
            self.assertIn(setting, argv)
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(env["GIT_SSH_COMMAND"], "/usr/bin/false")
        self.assertEqual(env["GIT_ALLOW_PROTOCOL"], "file:https")
        proc.communicate.side_effect = [subprocess.TimeoutExpired("git", 25), (b"", None)]
        with mock.patch.object(w.subprocess, "Popen", return_value=proc), mock.patch.object(w.os, "killpg") as kill:
            with self.assertRaisesRegex(w.WatchError, "GIT_TIMEOUT"):
                w.Git("/synthetic").fetch(REF)
            kill.assert_called_once_with(proc.pid, w.signal.SIGKILL)
        for failure in (OSError(),):
            with mock.patch.object(w.subprocess, "Popen", side_effect=failure), self.assertRaises(w.WatchError):
                w.Git("/synthetic").fetch(REF)
        proc.returncode, proc.communicate.side_effect = 1, None
        with mock.patch.object(w.subprocess, "Popen", return_value=proc), self.assertRaises(w.WatchError):
            w.Git("/synthetic").fetch(REF)

    def test_git_parsers_and_guards(self):
        git = w.Git("/synthetic")
        with mock.patch.object(git, "_run", return_value=f"{A}\t{REF}\n".encode()):
            self.assertEqual(git.ls_remote("*"), {REF: A})
        for raw in (b"bad", f"bad\t{REF}".encode(), f"{A}\trefs/heads/other".encode(), b"\xff"):
            with mock.patch.object(git, "_run", return_value=raw), self.assertRaises(w.WatchError):
                git.ls_remote("*")
        raw = f"100644 blob {A}\tnight/result.json\0".encode() + f"120000 blob {A}\tnight/chain.started\0".encode()
        with mock.patch.object(git, "_run", return_value=raw):
            self.assertEqual(git.list_tree(A), {"night/result.json"})
        for method, args in ((git.fetch, ("bad",)), (git.list_tree, ("bad",)), (git.show, ("bad", "x"))):
            with self.assertRaises(w.WatchError):
                method(*args)

    def test_event_format_and_all_exit_codes(self):
        event = w.Event("ALARM", "RESULT_NOT_MEASURED", REF, "outcome=UNKNOWN")
        self.assertEqual(event.line(0), "1970-01-01 00:00:00 ALARM RESULT_NOT_MEASURED " + REF + " outcome=UNKNOWN")
        self.assertEqual(w.EXIT_CODES, {"quiet": 0, "notice": 10, "alarm": 20, "error": 2})
        for events, expected in (([], 0), ([w.Event("INFO", "x", "-")], 0),
                                 ([w.Event("NOTICE", "x", "-")], 10), ([event], 20)):
            self.assertEqual(w.event_exit(events), expected)

    def test_local_bare_repo_end_to_end_no_network(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bare, source, air = (root / n for n in ("origin", "source", "air"))
            for path in (bare, source, air):
                path.mkdir()
                init_git_fixture(path, *(('--bare',) if path == bare else ()))

            def git(path, *args):
                return subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True).stdout

            for path in (source, air):
                git(path, "remote", "add", "origin", str(bare))
            for name, data in records(rc=3).items():
                p = source / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            # Planted symlink and outcome file must never be materialised.
            (source / "night/receipt.json").symlink_to("does-not-exist")
            (source / "night/outcomes.json").write_text("PRIVATE")
            git(source, "add", ".")
            git(source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "synthetic")
            git(source, "push", "origin", "HEAD:" + REF)
            transport = w.Git(air)
            self.assertEqual(set(transport.ls_remote(w.PREFIX + "*")), {REF})
            watcher = w.Watcher(transport, w.empty_state(), since=0)
            events = watcher.poll(1001)
            self.assertIn("RESULT_NOT_MEASURED", codes(events))
            self.assertFalse((air / "night").exists())
            self.assertFalse((air / ".git/FETCH_HEAD").exists())


class CliTests(unittest.TestCase):
    def invoke(self, extra=None, git=None, state=None):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            output = io.StringIO()
            if state is not None:
                w.save_state(path / "state", state)
            with mock.patch.object(w, "Git", return_value=git or FakeGit()), \
                 mock.patch.object(w, "optional_exit_module", return_value=None), \
                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                rc = w.main(["--state", str(path / "state"), "--current", str(path / "absent"), *(extra or ["--once"])])
            return rc, output.getvalue()

    def test_once_quiet_notice_alarm_usage_internal(self):
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(self.invoke(["--once", "--since-epoch", "0"], FakeGit(records(fault=True)))[0], 10)
        self.assertEqual(self.invoke(["--once", "--since-epoch", "0"], FakeGit(records(rc=3)))[0], 20)
        for extra in ([], ["--once", "--loop"], ["--once", "--interval", "0"],
                      ["--once", "--hours", "nan"], ["--once", "--t0", "1"],
                      ["--once", "--failure-limit", "1"], ["--once", "--notify-cmd"]):
            with self.subTest(extra=extra):
                # [] must stay empty, rather than invoke's convenience default.
                if not extra:
                    with contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(w.main([]), 2)
                else:
                    self.assertEqual(self.invoke(extra)[0], 2)
        with mock.patch.object(w, "load_state", side_effect=w.WatchError("PRIVATE")):
            rc, output = self.invoke()
        self.assertEqual(rc, 2)
        self.assertIn("WATCH_ERROR", output)
        self.assertNotIn("PRIVATE", output)

    def test_cli_armed_overrides_current(self):
        with mock.patch.object(w, "read_current", return_value={"armed": {"plan_id": "different"}}), \
             mock.patch.object(w.time, "time", return_value=1001):
            rc, output = self.invoke(["--once", "--plan-id", "synthetic", "--t0", "1000", "--min-expected-s", "100"])
        self.assertEqual(rc, 20)
        self.assertIn("RESULT_EARLY synthetic", output)

    def test_loop_alarm_stops_and_keep_going_expires(self):
        with mock.patch.object(w.time, "sleep") as sleep:
            self.assertEqual(self.invoke(["--loop", "--since-epoch", "0"], FakeGit(records(rc=3)))[0], 20)
            sleep.assert_not_called()
        for git, expected in ((FakeGit(records(rc=3)), 20), (FakeGit(records(fault=True)), 10), (FakeGit(), 0)):
            with mock.patch.object(w.time, "monotonic", side_effect=[0, 0, 3601]), mock.patch.object(w.time, "sleep") as sleep:
                rc, _ = self.invoke(["--loop", "--hours", "1", "--keep-going", "--since-epoch", "0"], git)
            self.assertEqual(rc, expected)
            sleep.assert_called_once_with(120)

    def test_notify_argv_no_shell_and_failure_not_persisted(self):
        with mock.patch.object(w.subprocess, "run", return_value=mock.Mock(returncode=0)) as run:
            rc, output = self.invoke(["--once", "--since-epoch", "0", "--notify-cmd", "/synthetic/notifier", "fixed argument"])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_args.args[0], ["/synthetic/notifier", "fixed argument", output.strip()])
        self.assertNotIn("shell", run.call_args.kwargs)
        with mock.patch.object(w.subprocess, "run", side_effect=subprocess.TimeoutExpired("notify", 10)):
            self.assertEqual(self.invoke(["--once", "--since-epoch", "0", "--notify-cmd", "/synthetic"])[0], 2)


if __name__ == "__main__":
    unittest.main()
