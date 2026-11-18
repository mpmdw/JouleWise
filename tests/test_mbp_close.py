"""Interface and regression tests. All host commands and runtime inputs are synthetic."""

import builtins
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import mbp_close as closer
from scripts import mbp_sched as sched
from tests.test_mbp_sched import History, digest, head_for, probe_child


NOW = 1795039200
KIT = "a" * 64
ENTRY = "f0-part-c"
AUDIT_PIN = "f9b03c33d9996fcbb9c663201d519c5fe1ccbbad"
Q1_MISSING = tuple(
    f"docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/desk-cq-{span}-a1/"
    "legs/*/leg_summary.json"
    for span in ("dev-03-s02", "dev-04-s01", "dev-04-s02")
)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def census(argv, **kwargs):
    tool = Path(argv[0]).name
    if tool == "pmset" and argv[-1] == "-g":
        output = "System-wide power settings:\nCurrently in use:\n powermode 0\n"
    elif tool == "systemsetup":
        output = "Network Time: Off\n"
    elif tool == "pgrep":
        return subprocess.CompletedProcess(argv, 1, "", "")
    elif tool == "ps" and argv[-1] == "pid=,pgid=,stat=":
        output = "10 10 S\n11 10 S\n12 12 S\n"
    elif tool == "log":
        output = (
            "Timestamp                       Thread     Type        Activity             PID    TTL\n"
            "2026-11-18 13:46:00.000000-0800 0x1        Default     0x0                  42     0    dasd: one\n"
        )
    else:
        return probe_child(argv, **kwargs)
    return subprocess.CompletedProcess(argv, 0, output, "")


class CloseTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.custody = self.root / "desk"
        self.custody.mkdir()
        self.fence = self.custody / "desk_fence.json"
        self.out = self.root / "span"
        self.record = self.custody / "closes" / ENTRY / "close.json"
        self.ledger = self.custody / "mbp_ledger.jsonl"
        self.head = self.custody / "mbp_ledger.jsonl.head.json"
        self.decisions = self.custody / "mbp_decisions.jsonl"
        self.now = NOW
        self.marker = self.root / "high-power.marker"
        self.maintenance = self.root / "MAINTENANCE"
        self.receipt = self.out / "runner_receipt.json"
        self.config = self.root / "copy-config.json"
        self.queue = self.root / "queue.json"
        self.rules = self.root / "rules.json"
        self.facts = self.root / "supplied.json"
        self.started = NOW - 1000.75
        self.ended = NOW - 650.25
        self.write_fence()
        self.roster = [f"L{i:03d}" for i in range(1, 7)]
        self.legs = [self.out / "desk-bundle" / "legs" / leg / "leg_summary.json"
                     for leg in self.roster]
        for index, (leg, path) in enumerate(zip(self.roster, self.legs)):
            write(path, {"leg_id": leg, "attempts": 1, "admitted": True,
                         "g0_role": "consume" if index else "capture", "g0_outcome": "released",
                         "span_reference": {"leg_id": "L001", "attempt": 1,
                                            "redone": False, "excluded": False} if index else None,
                         "g0_s": 5, "wall_s": 60, "budget_s": 100, "contaminated_redos": 0,
                         "os_level_max": 0, "pm_nominal": True, "prefill_tokens": 80})
        write(self.receipt, {"entry_id": ENTRY, "span_id": ENTRY, "rc": 0, "error": None, "mock": False,
                             "roster": self.roster, "legs_planned": 6, "legs_finished": 6,
                             "started": {"epoch_s": self.started}, "ended": {"epoch_s": self.ended},
                             "span_result": {"outcome": "MEASURED_OK", "chain_outcome": "COMPLETE",
                                             "fault": False},
                             "steps": [{"name": "restore", "rc": 0}, {"name": "stop-fixture", "rc": 0}],
                             "feeds": {"fixture": {"stop": {"proven_stopped": True}}},
                             "kit": {"campaign_id": "synthetic", "sha256": KIT, "frozen_commit": "b" * 40},
                             "batch_windows": [], "runner_kind": "cadence-legs-v1"})
        rules = read(sched.DEFAULT_RULES)
        write(self.rules, rules)
        queue = read(sched.DEFAULT_QUEUE)
        entry = queue["entries"][0]
        entry.update(id=ENTRY, worktree=str(self.root), argv=["fixture-launch"],
                     plan_argv=["fixture-plan"], params={}, kit_sha256=KIT)
        queue["admitted"] = [dict(pin=entry["pin"], kit_sha256=KIT)]
        write(self.queue, queue)
        write(self.facts, {"clock_verified": True, "meter_ready": True, "collector_ready": True,
                           "owner_stop": False, "owner_veto": False, "upload_stopped": True,
                           "queue_commit": "fixture-commit"})
        write(self.config, {"argv": ["fixture-copy", "{out}", "{entry}"],
                            "pidfile": str(self.root / "copy.pid")})
        self.commands = self.enterContext(patch.object(subprocess, "run", side_effect=census))

    def call(self, command, *options, status=0):
        if command == "tick":
            main = sched.main
            args = ["tick", "--receipt-root", self.out, "--rules", self.rules, "--queue", self.queue,
                    "--caller-pid", 10, "--host-facts", self.facts, "--maintenance-marker", self.maintenance,
                    "--run-plans"]
        else:
            main = closer.main
            args = [command]
            if command == "close":
                args += ["--out", self.out, "--entry", ENTRY, "--high-power-marker", self.marker]
        if command == "tick":
            args += ["--high-power-marker", self.marker]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with patch.object(closer, "frequency_word", return_value=0), patch.object(
                closer.time, "time", side_effect=lambda: self.now
            ):
                rc = main([*map(str, args), "--custody", str(self.custody), *map(str, options)])
        self.assertEqual(rc, status, stderr.getvalue())
        return stdout.getvalue()

    def close(self, *options, status=0):
        return self.call("close", "--no-copy", *options, status=status)

    def rows(self):
        return [json.loads(line) for line in self.ledger.read_text().splitlines()] if self.ledger.exists() else []

    def seal(self, rows):
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        write(self.head, head_for(rows))

    def append(self, *events):
        rows = self.rows()
        if not rows:
            rows = [
                {"seq": 1, "event": "CONFIG", "legs": 0, "queue_commit": "fixture-commit",
                 "queue_digest": digest(read(self.queue)), "rules_digest": digest(read(self.rules))},
                {"seq": 2, "event": "GATE", "legs": 0, "id": "r1-post-close-check", "passed": False},
            ]
        for event in events:
            rows.append({"seq": len(rows) + 1, "legs": 0, **event})
        self.seal(rows)
        return rows

    def write_fence(self, **updates):
        write(self.fence, {"pid": 99, "pgid": 99, "entry_id": ENTRY, "span_id": ENTRY, "kit_sha256": KIT,
                           "t0_epoch": self.started, "out": str(self.out.resolve()), **updates})

    def launch(self, **updates):
        queue_entry = read(self.queue)["entries"][0]
        row = {"event": "LAUNCH", "entry_id": ENTRY, "span_id": ENTRY, "kit_sha256": KIT,
               "t0_epoch": self.started, "kind": "diagnostic_filler", "groups": [], "block": queue_entry.get("block"),
               "legs": 6, "pin": queue_entry["pin"], "boot_id": "boot-a", "campaign": "fixture-campaign",
               "queue_commit": "fixture-commit", **updates}
        row["registration"] = {key: row[key] for key in ("kind", "groups", "block", "legs")}
        return row

    def current_launch(self):
        return next(row for row in reversed(self.rows()) if row["event"] == "LAUNCH")

    def copy_event(self, event, launch=None):
        self.append({"event": event, **History().bind(launch or self.current_launch())})

    def tick(self, *options):
        output = self.call("tick", *options)
        return json.loads(output.splitlines()[-1])

    def test_clean_six_leg_summary(self):
        output = self.close()
        record = read(self.record)
        self.assertIs(record["clean"], True)
        self.assertIs(record["restore_proven"], True)
        self.assertEqual(record["legs"], 6)
        self.assertEqual(record["legs_admitted"], 6)
        self.assertEqual(len(output.splitlines()), 12)
        self.assertIn("L002 released", output)
        self.assertIn("L005 released", output)
        self.assertIn("L001", output)
        self.assertEqual(record["leg_table"][0]["attempts"], 1)
        self.assertIsNone(record["leg_table"][0]["leg_status"])
        self.assertIsNone(record["leg_table"][0]["decode_tokens"])
        self.assertIs(record["leg_table"][0]["admitted"], True)
        self.assertEqual(record["leg_table"][0]["g0_s"], 5)
        self.assertEqual(record["maintenance"]["status"], "observed")
        self.assertTrue((self.record.parent / "maintenance-log.txt").is_file())
        self.assertEqual(sum(row["dasd"] for row in record["maintenance"]["bins"].values()), 1)

    def test_blinding(self):
        sentinel = "SYNTHETIC-MUST-NOT-LEAK"
        for path in [self.receipt, *self.legs]:
            data = read(path)
            data["unknown_text"] = sentinel
            if path in self.legs[1:]:
                data["span_reference"]["unknown_text"] = sentinel
            if path == self.receipt:
                data["steps"][0]["detail"] = sentinel
                data["feeds"]["fixture"]["stop"]["detail"] = sentinel
                data["span_result"]["unknown_text"] = sentinel
            write(path, data)
        forbidden = [self.out / "desk-bundle" / "span" / name for name in ("result.json", "meter.json")]
        extra = [self.out / name for name in ("power_trace.csv", "stream-x.jsonl", "align_episode.json")]
        for path in [*forbidden, *extra]:
            write(path, {"unknown_text": sentinel})
        for path in extra:
            os.utime(path, (10, 20))
        atimes = {path: path.stat().st_atime_ns for path in extra}
        forbidden_names = {path.name for path in [*forbidden, *extra]}

        def guard(open_file):
            def checked_open(path, *args, **kwargs):
                if not isinstance(path, int):
                    self.assertNotIn(Path(path).name, forbidden_names)
                return open_file(path, *args, **kwargs)
            return checked_open

        with patch("os.open", side_effect=guard(os.open)), patch(
            "builtins.open", side_effect=guard(builtins.open)
        ), patch("io.open", side_effect=guard(io.open)):
            output = self.close()
        self.assertNotIn(sentinel, output)
        self.assertNotIn(sentinel, self.record.read_text())
        self.assertEqual(atimes, {path: path.stat().st_atime_ns for path in extra})

    def test_value_independence(self):
        def unlisted(number):
            receipt = read(self.receipt)
            receipt["unknown_sample"] = number
            receipt["steps"][0]["unknown_sample"] = number
            receipt["feeds"]["fixture"]["stop"]["unknown_sample"] = number
            receipt["span_result"]["unknown_sample"] = number
            write(self.receipt, receipt)
            for path in self.legs:
                leg = read(path)
                leg["unknown_sample"] = number
                if leg["span_reference"] is not None:
                    leg["span_reference"]["unknown_sample"] = number
                write(path, leg)
            for name in ("result.json", "meter.json"):
                write(self.out / "desk-bundle" / "span" / name, {"unlisted": number})

        unlisted(1)
        self.close()
        expected = self.record.read_bytes()
        self.record.unlink()
        unlisted(987654321)
        self.close()
        self.assertEqual(expected, self.record.read_bytes())

    def test_stranded_still_copies(self):
        self.receipt.unlink()
        with patch.object(closer, "start_copy", return_value=123) as copy:
            self.call("close", "--copy-config", self.config)
        copy.assert_called_once()
        record = read(self.record)
        self.assertFalse(record["clean"])
        self.assertIn("STRANDED", record["problems"])
        self.assertIs(record["restore_proven"], False)
        self.assertEqual(record["copy"]["pid"], 123)
        self.assertFalse(any(Path(call.args[0][0]).name == "log" for call in self.commands.call_args_list))
        self.assertEqual(self.tick("--no-copy")["decision"], "HALT")

    def test_live_fence_refuses_without_writing(self):
        self.write_fence(pid=10)
        self.close(status=4)
        self.assertEqual(list(self.custody.iterdir()), [self.fence])

    def test_live_group_refuses_without_writing(self):
        # The owner is absent and the remaining group members' commands omit OUT.
        self.write_fence(pgid=10)
        self.assert_group_refusal()

    def test_missing_pgid_refuses_before_any_close_or_copy(self):
        fence = read(self.fence)
        del fence["pgid"]
        write(self.fence, fence)
        self.assert_group_refusal()

    def test_pgid_from_different_attempt_cannot_prove_close(self):
        self.write_fence(t0_epoch=self.started - 1)
        self.assert_group_refusal()

    def test_process_census_failure_cannot_prove_close(self):
        def bad_census(argv, **kwargs):
            if argv[-1] == "pid=,pgid=,stat=":
                return subprocess.CompletedProcess(argv, 2, "", "fixture failed")
            return census(argv, **kwargs)

        self.commands.side_effect = bad_census
        self.assert_group_refusal()

    def assert_group_refusal(self):
        with patch.object(closer, "start_copy", return_value=123) as start:
            self.call("close", "--copy-config", self.config, status=4)
            self.assertEqual(list(self.custody.iterdir()), [self.fence])
            self.append(self.launch())
            decision = self.tick("--copy-config", self.config)
            self.assertEqual(decision["decision"], "HALT")
            self.assertEqual(decision["entry"], ENTRY)
            self.assertNotIn("argv", decision)
            self.assertFalse(self.record.parent.exists())
        start.assert_not_called()

    def test_high_power_mode_fails_restore(self):
        def power_mode(argv, **kwargs):
            if Path(argv[0]).name == "pmset" and argv[-1] == "-g":
                return subprocess.CompletedProcess(argv, 0, " powermode 2\n", "")
            return census(argv, **kwargs)

        self.commands.side_effect = power_mode
        self.close(status=5)
        self.assertIs(read(self.record)["restore_proven"], False)

    def test_a3_unproven_restore_halts_all_work(self):
        self.marker.touch()
        self.append(self.launch())
        self.assertEqual(self.tick("--no-copy"), {
            "decision": "HALT", "entry": ENTRY, "rule": "RESTORE_UNPROVEN",
            "detail": f"{ENTRY} failed no_high_power_marker",
        })
        record = read(self.record)
        self.assertIn("RESTORE_UNPROVEN", record["problems"])
        self.assertIs(record["restore_proven"], False)
        self.assertEqual(record["stops"], [])

    def test_consumer_not_released(self):
        write(self.legs[1], {**read(self.legs[1]), "g0_outcome": "timeout"})
        self.close()
        record = read(self.record)
        self.assertIs(record["clean"], False)
        self.assertIn("CONSUMER_NOT_RELEASED", record["problems"])

    def test_overtime_and_redo_limits(self):
        write(self.legs[0], {**read(self.legs[0]), "wall_s": 151, "contaminated_redos": 3})
        write(self.legs[1], {**read(self.legs[1]), "wall_s": 151})
        self.close()
        record = read(self.record)
        self.assertFalse(record["clean"])
        self.assertEqual(record["overtime_legs"], 2)
        self.assertEqual(record["load_redos"], 3)
        self.assertIn("LEG_OVERTIME", record["problems"])
        self.assertIn("CONTAMINATED_REDOS", record["problems"])

    def test_second_close_is_byte_identical(self):
        self.close()
        before = self.record.read_bytes()
        self.close()
        self.assertEqual(before, self.record.read_bytes())

    def test_post_uses_summary_body_and_closed_owner(self):
        post_calls = []

        def run(argv, **kwargs):
            if Path(argv[1]).name == "run_state_add.py":
                post_calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, "", "")
            return census(argv, **kwargs)

        self.commands.side_effect = run
        self.assertIn("RUN_STATE posted", self.close("--post"))
        self.assertEqual(len(post_calls), 1)
        argv = post_calls[0]
        self.assertEqual(argv[-4:], ["--status", "CLOSED", "--owner", "magistrate"])
        body = Path(argv[argv.index("--body") + 1])
        self.assertIn("Legs admitted 6", body.read_text())

    def test_interruption_before_link_allows_retry(self):
        link = os.link

        def interrupt(source, target, **kwargs):
            if Path(target) == self.record:
                raise KeyboardInterrupt
            return link(source, target, **kwargs)

        with patch("os.link", side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
            self.close()
        self.assertFalse(self.record.exists())
        self.close()
        self.assertTrue(self.record.is_file())

    def test_copy_stop_and_resume(self):
        # The fixture child implements Popen's sleeping/TERM states without signaling a process.
        child = Mock(pid=140)
        child.poll.side_effect = [None, -15]
        with patch("subprocess.Popen", return_value=child), patch.object(
            closer, "copy_stop_requested", side_effect=[False, True]
        ), patch.object(closer.time, "sleep"):
            closer.run_copy_child(self.custody / "control", ["fixture-copy"], lambda pid: None)
        child.terminate.assert_called_once_with()
        with patch.object(closer, "start_copy", side_effect=[140, 141]) as start:
            self.call("close", "--copy-config", self.config)
            self.assertEqual(start.call_count, 1)
            self.assertIn("141", self.call("copy-resume"))
            self.assertEqual(start.call_count, 2)

        with patch.object(closer, "active_copy", return_value={"pid": 141, "job": "fixture"}), patch.object(
            closer, "request_copy_stop", return_value=True
        ) as stop:
            self.call("copy-stop")
        stop.assert_called_once()
        self.assertLessEqual(stop.call_args.args[2], 60)

    def test_span_tree_is_immutable(self):
        def tree():
            return {path.relative_to(self.out): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.out.rglob("*") if path.is_file()}

        before = tree()
        self.close()
        self.assertEqual(before, tree())

    def test_tick_closes_and_records_next(self):
        self.append(self.launch())
        with patch.object(sched, "authorize_next", wraps=sched.authorize_next) as authorize:
            self.assertEqual(self.tick("--no-copy")["decision"], "LAUNCH")
        authorize.assert_called_once()
        self.assertIs(read(self.record)["restore_proven"], True)
        rows = self.rows()
        self.assertEqual([row["event"] for row in rows[-3:]], ["RECEIPT", "RESTORE", "CLOSE"])
        self.assertEqual(json.loads(self.decisions.read_text())["decision"], "LAUNCH")
        self.assertEqual(rows[-3]["receipt"]["started"]["epoch_s"], self.started)
        self.assertEqual(read(self.head), head_for(rows))

    def test_final_authorization_rechecks_committed_head(self):
        self.append(self.launch())
        probe = closer.probe_for_tick

        def change_head(*args):
            snapshot = probe(*args)
            self.append({"event": "GATE", "id": "other-writer", "passed": True})
            return snapshot

        with patch.object(closer, "probe_for_tick", side_effect=change_head):
            decision = self.tick("--no-copy")
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "LEDGER_HEAD_CHANGED"))
        self.assertNotIn("argv", decision)
        self.assertEqual(len(self.decisions.read_text().splitlines()), 1)

    def test_script_entry_point_records_config_refusal(self):
        write(self.queue, {})
        command = [sys.executable, sched.__file__, "tick", "--custody", str(self.custody),
                   "--receipt-root", str(self.out), "--queue", str(self.queue)]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as child:
            output, error = child.communicate(timeout=10)
        self.assertEqual(child.returncode, 0, error)
        self.assertEqual(json.loads(output)["rule"], "CONFIG_INVALID")
        self.assertEqual(len(self.decisions.read_text().splitlines()), 1)

    def test_a1_latest_attempt_missing_receipt_refuses(self):
        self.write_fence(entry_id="latest-missing", span_id="latest-missing", t0_epoch=self.started - 600)
        self.append(self.launch(entry_id="latest-missing", span_id="latest-missing", t0_epoch=self.started - 600))
        decision = self.tick("--no-copy")
        self.assertEqual(decision["decision"], "HALT")
        self.assertEqual(decision["entry"], "latest-missing")
        self.assertFalse(self.record.exists())

    def test_receipt_without_either_attempt_id_cannot_prove_close(self):
        receipt = read(self.receipt)
        receipt.pop("entry_id")
        receipt.pop("span_id")
        write(self.receipt, receipt)
        self.append(self.launch())
        decision = self.tick("--no-copy")
        self.assertEqual(decision["decision"], "HALT")
        self.assertEqual(decision["entry"], ENTRY)
        self.assertIn("receipt", decision["detail"])
        self.assertNotIn("argv", decision)
        self.assertFalse((self.custody / "closes").exists())

    def test_legacy_attempt_requires_kit_hash_on_both_sides(self):
        receipt = read(self.receipt)
        del receipt["span_id"]
        del receipt["kit"]["sha256"]
        write(self.receipt, receipt)
        fence = read(self.fence)
        del fence["span_id"]
        fence["kit_sha256"] = None
        write(self.fence, fence)
        self.close(status=4)
        self.assertFalse((self.custody / "closes").exists())

    def test_uncommitted_launch_rows_cannot_discard_a_prior_observation(self):
        self.append(self.launch())
        rows = self.rows()
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({**self.launch(span_id="uncommitted"), "seq": len(rows) + 1}) + "\n")
        head = self.head.read_bytes()
        decision = self.tick("--no-copy")
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "LEDGER_HEAD_MISMATCH"))
        self.assertEqual(self.head.read_bytes(), head)
        self.assertFalse(self.record.exists())

    def test_a1_clock_rollback_does_not_select_older_receipt(self):
        first = self.launch(entry_id="older", span_id="older", t0_epoch=self.started + 100)
        self.append(first)
        previous = self.current_launch()
        history = History()
        history.close(previous, self.ended + 1)
        self.append(*[{k: v for k, v in row.items() if k != "seq"} for row in history.rows])
        older = {**read(self.receipt), "entry_id": "older", "span_id": "older",
                 "started": {"epoch_s": self.started + 100}, "ended": {"epoch_s": self.ended + 1}}
        write(self.out / "older" / self.receipt.name, older)
        self.append(self.launch())
        self.tick("--no-copy")
        self.assertEqual(read(self.record)["ended_epoch"], self.ended)

    def test_a1_fractional_start_must_match_without_rounding(self):
        self.write_fence(t0_epoch=self.started + 0.125)
        self.append(self.launch(t0_epoch=self.started + 0.125))
        decision = self.tick("--no-copy")
        self.assertEqual(decision["decision"], "HALT")
        self.assertEqual(decision["entry"], ENTRY)
        self.assertFalse(self.record.exists())

    def test_reordered_sequence_refuses_even_with_matching_native_receipt(self):
        rows = self.append(self.launch())
        rows[-1]["seq"] += 1
        self.seal(rows)
        decision = self.tick("--no-copy")
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "LEDGER_SEQUENCE"))
        self.assertFalse(self.record.exists())

    def test_a1_repeated_entry_keeps_one_immutable_record_per_span(self):
        for attempt in (1, 2):
            started = self.started + (attempt - 1) * 500
            ended = self.ended + (attempt - 1) * 500
            self.now = NOW + (attempt - 1) * 500
            span = f"fixture-attempt-{attempt}"
            write(self.receipt, {**read(self.receipt), "span_id": span,
                                 "started": {"epoch_s": started}, "ended": {"epoch_s": ended}})
            self.write_fence(span_id=span, t0_epoch=started)
            self.append(self.launch(span_id=span, t0_epoch=started))
            self.assertEqual(self.tick("--no-copy")["decision"], "LAUNCH")
            record = self.custody / "closes" / span / "close.json"
            self.assertEqual(read(record)["span_id"], span)
            if attempt == 1:
                first, before = record, record.read_bytes()
        self.assertEqual(first.read_bytes(), before)

    def assert_copy_deadline(self, *, observed_stop, restart=False):
        close_time = NOW - 597
        receipt = read(self.receipt)
        write(self.receipt, {**receipt, "ended": {"epoch_s": close_time}})
        self.append(self.launch())
        self.tick("--no-copy")
        if restart:
            self.copy_event("COPY_STARTED")
            self.copy_event("COPY_VERIFIED")
        self.copy_event("COPY_STARTED")
        start_seq = self.rows()[-1]["seq"]
        launch = self.current_launch()
        events = []
        state = {"active": True}
        job = "a" * 32
        control = self.custody / "copy-control"
        worker = control / job
        write(control / "active.json", {"job": job, "attempt": {
            **History().bind(launch), "t0_epoch": launch["t0_epoch"], "copy_start_seq": start_seq,
        }})

        def sleep(seconds):
            self.now += seconds

        def stop(custody, active, timeout):
            events.append(("stop", self.now, timeout))
            state["active"] = False
            if observed_stop:
                write(worker / "ready.json", {"pid": 141})
                write(worker / "done.json", {"pgid": 141})
            return True

        probe = closer.probe_for_tick

        def probe_again(*args):
            events.append(("probe", self.now))
            return probe(*args)

        with patch.object(closer, "active_copy", side_effect=lambda custody: {"job": job} if state["active"] else None), patch.object(
            closer, "request_copy_stop", side_effect=stop
        ), patch.object(closer.time, "monotonic", side_effect=lambda: self.now - NOW), patch.object(
            closer.time, "sleep", side_effect=sleep
        ), patch.object(closer, "probe_for_tick", side_effect=probe_again):
            decision = self.tick()
        self.assertEqual(events, [("probe", NOW), ("stop", NOW + 3, 0), ("probe", NOW + 3)])
        history = sched.History(self.rows(), read(self.head))
        self.assertFalse(history.latest.copy_verified())
        self.assertEqual(len(history.copy_debts()), 1)
        if observed_stop:
            self.assertEqual(decision["decision"], "LAUNCH")
            self.assertGreater(history.latest.copy["UPLOAD_STOPPED"], start_seq)
        else:
            self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "UPLOAD_ACTIVE"))
            self.assertNotIn("argv", decision)

    def test_a2_deadline_reprobes_and_launches_with_observed_stop(self):
        self.assert_copy_deadline(observed_stop=True)

    def test_a2_stop_request_alone_cannot_authorize_launch(self):
        self.assert_copy_deadline(observed_stop=False)

    def test_a2_verification_before_restart_cannot_authorize_launch(self):
        self.assert_copy_deadline(observed_stop=False, restart=True)

    def test_a2_pages_once_for_overdue_copy(self):
        receipt = read(self.receipt)
        receipt.update(ended={"epoch_s": NOW - 7201}, started={"epoch_s": NOW - 8000})
        write(self.receipt, receipt)
        self.write_fence(t0_epoch=NOW - 8000)
        self.append(self.launch(t0_epoch=NOW - 8000))
        output = self.call("tick", "--no-copy")
        self.assertEqual([line for line in output.splitlines() if line.startswith("PAGE ")],
                         [f"PAGE uncopied {ENTRY} 2.00"])

    def test_copy_requires_config_and_honors_no_copy(self):
        with patch.object(closer, "start_copy", return_value=123) as start:
            for options in ((), ("--copy-config", self.config, "--no-copy")):
                self.record.unlink(missing_ok=True)
                self.call("close", *options)
                record = read(self.record)
                self.assertIsNone(record["copy"]["pid"])
                self.assertNotIn("config", record["copy"])
            self.assertEqual(self.call("copy-resume"), "")
        start.assert_not_called()

    def test_copy_start_is_committed_and_blocks_until_stop_evidence(self):
        self.append(self.launch())
        with patch.object(closer, "start_copy", return_value=141) as start:
            decision = self.tick("--copy-config", self.config)
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "UPLOAD_ACTIVE"))
        self.assertNotIn("argv", decision)
        row = self.rows()[-1]
        launch = self.current_launch()
        self.assertEqual(row, {"event": "COPY_STARTED", "legs": 0, "seq": row["seq"],
                               **History().bind(launch)})
        self.assertEqual(start.call_args.args[-1]["copy_start_seq"], row["seq"])
        self.assertEqual(read(self.head), head_for(self.rows()))
        before = self.ledger.read_bytes()
        self.tick("--copy-config", self.config)
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_startup_lock_prevents_launch_before_supervisor_lease(self):
        self.append(self.launch())
        control = self.custody / "copy-control"
        control.mkdir()
        with closer.lock(control / "start.lock"):
            decision = self.tick("--no-copy")
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "UPLOAD_ACTIVE"))
        self.assertNotIn("argv", decision)

    def test_only_matching_copy_event_clears_each_attempts_debt(self):
        for span, start, end in (("old", NOW - 9000, NOW - 8500), ("new", NOW - 8000, NOW - 7500)):
            write(self.receipt, {**read(self.receipt), "span_id": span,
                                 "started": {"epoch_s": start}, "ended": {"epoch_s": end}})
            self.write_fence(span_id=span, t0_epoch=start)
            self.append(self.launch(span_id=span, t0_epoch=start))
            self.tick()

        old = next(row for row in self.rows() if row.get("span_id") == "old" and row["event"] == "LAUNCH")
        self.copy_event("COPY_VERIFIED", old)
        self.assertIn(f"PAGE uncopied {ENTRY} 2.08", self.call("tick"))
        history = sched.History(self.rows(), read(self.head))
        record, run = closer.newest_uncopied(self.custody, history)
        self.assertEqual(record["span_id"], run.span)
        self.assertEqual(run.span, "new")

        self.copy_event("COPY_VERIFIED")
        self.assertNotIn("PAGE uncopied", self.call("tick"))
        self.assertEqual(closer.newest_uncopied(self.custody, sched.History(self.rows(), read(self.head))),
                         (None, None))

    def test_a3_scopes_match_scheduler_stops(self):
        queue = read(self.queue)
        queue["entries"].append({**queue["entries"][0], "id": "standing-filler"})
        queue["entries"][0]["block"] = "fixture-block"
        write(self.queue, queue)
        write(self.legs[0], {**read(self.legs[0]), "wall_s": 151, "contaminated_redos": 3})
        write(self.legs[1], {**read(self.legs[1]), "wall_s": 151, "g0_outcome": "timeout"})
        self.append(self.launch())
        self.tick("--no-copy")
        record = read(self.record)
        stops = {row["code"]: row for row in record["stops"]}
        self.assertEqual(stops["CONTAMINATED_REDOS"], {"code": "CONTAMINATED_REDOS", "epoch": self.ended})
        for code in ("LEG_OVERTIME", "NON_CLEAN_CLOSE", "CONSUMER_GATE"):
            self.assertEqual(stops[code]["kit_sha256"], KIT)
            self.assertEqual(stops[code]["block"], "fixture-block")
        history = sched.History(self.rows(), read(self.head))
        self.assertTrue(history.contaminated())
        self.assertEqual({row["code"] for row, _ in history.stops}, set(stops))
        for row, run in history.stops:
            self.assertEqual(row["open_seq"], run.launch["seq"])
            self.assertEqual(run.launch["block"], "fixture-block")

    def test_decision_log_alias_refused_without_mutation(self):
        self.append(self.launch())
        for source in (self.ledger, self.head):
            for kind in ("direct", "hardlink", "symlink"):
                with self.subTest(source=source.name, kind=kind):
                    alias = self.root / "alias"
                    alias.unlink(missing_ok=True)
                    if kind == "hardlink":
                        os.link(source, alias)
                    elif kind == "symlink":
                        alias.symlink_to(source)
                    else:
                        alias = source
                    before = self.ledger.read_bytes(), self.head.read_bytes()
                    decision = self.tick("--record", alias)
                    self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "RECORD_PATH"))
                    self.assertEqual(before, (self.ledger.read_bytes(), self.head.read_bytes()))

    def test_identical_close_replay_appends_zero_events(self):
        self.append(self.launch())
        self.tick("--no-copy")
        before = self.ledger.read_bytes(), self.head.read_bytes()
        self.tick("--no-copy")
        self.assertEqual(before, (self.ledger.read_bytes(), self.head.read_bytes()))
        self.assertEqual(len(self.decisions.read_text().splitlines()), 2)

    def test_stale_expected_head_cannot_launch(self):
        self.append(self.launch())
        append = closer.append_observed

        def stale(ledger, head, launch, events):
            self.append({"event": "GATE", "id": "other-writer", "passed": True})
            return append(ledger, head, launch, events)

        with patch.object(closer, "append_observed", side_effect=stale):
            self.assertEqual(self.tick("--no-copy")["decision"], "HALT")
        self.assertFalse(any(row["event"] == "CLOSE" for row in self.rows()))

    def test_conflicting_close_replay_cannot_launch(self):
        self.append(self.launch())
        self.tick("--no-copy")
        rows = self.rows()
        next(row for row in rows if row["event"] == "CLOSE")["clean"] = False
        self.seal(rows)
        before = self.ledger.read_bytes(), self.head.read_bytes()
        decision = self.tick("--no-copy")
        self.assertEqual(decision["decision"], "HALT")
        self.assertNotIn("argv", decision)
        self.assertEqual(before, (self.ledger.read_bytes(), self.head.read_bytes()))

    def test_interruption_before_head_publish_cannot_launch_or_repair(self):
        self.append(self.launch())
        head = self.head.read_bytes()
        with patch.object(closer, "publish_head", side_effect=OSError("fixture interruption")):
            self.assertEqual(self.tick("--no-copy")["decision"], "HALT")
        rows = self.ledger.read_bytes()
        self.assertIn(b'"CLOSE"', rows)
        self.assertEqual(self.tick("--no-copy")["decision"], "HALT")
        self.assertEqual((rows, head), (self.ledger.read_bytes(), self.head.read_bytes()))

    def test_tick_never_bootstraps_missing_head(self):
        self.append(self.launch())
        self.head.unlink()
        before = self.ledger.read_bytes()
        decision = self.tick("--no-copy")
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "LEDGER_HEAD_INVALID"))
        self.assertFalse(self.head.exists())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a4_committed_q1_consumer_and_reference_reproduction(self):
        self.skipTest(f"{AUDIT_PIN} lacks the required step 4 inputs: " + ", ".join(Q1_MISSING))

    def test_a5_maintenance_waits_even_with_close_owed(self):
        self.maintenance.touch()
        self.append(self.launch())
        decision = self.tick("--no-copy")
        self.assertEqual(decision["decision"], "WAIT")
        self.assertEqual(decision["reason"], "MAINTENANCE")
        self.assertNotIn("argv", decision)
        self.assertTrue(self.record.is_file())
