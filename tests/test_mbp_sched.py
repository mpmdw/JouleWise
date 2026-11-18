"""Scheduler acceptance cases. Host commands and all receipt inputs are synthetic."""

import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts import mbp_sched as sched


FIXTURES = Path(__file__).parent / "fixtures" / "mbp_sched"
ZONE = ZoneInfo("America/Los_Angeles")


def epoch(day=18, hour=0, minute=0, second=0):
    return int(datetime(2026, 11, day, hour, minute, second, tzinfo=ZONE).timestamp())


def write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def close(entry_id, kind, ended, **updates):
    return {
        "entry_id": entry_id, "kind": kind, "ended_epoch": ended,
        "clean": True, "restore_proven": True, "t0_epoch": ended - 100, **updates,
    }


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.queue_path = self.directory / "queue.json"
        self.rules_path = self.directory / "rules.json"
        self.facts_path = self.directory / "facts.json"
        self.ledger = self.directory / "ledger.jsonl"
        self.queue = json.loads(sched.DEFAULT_QUEUE.read_text())
        self.rules = json.loads(sched.DEFAULT_RULES.read_text())
        self.facts = json.loads((FIXTURES / "facts.json").read_text())
        self.facts["now_epoch"] = epoch(hour=14)
        self.f0 = self.queue["entries"][0]

    def call(self, command, *options, status=0):
        write(self.queue_path, self.queue)
        write(self.rules_path, self.rules)
        write(self.facts_path, self.facts)
        args = [command]
        if command != "report":
            args += ["--queue", str(self.queue_path), "--rules", str(self.rules_path)]
        if command in {"next", "explain"}:
            args += ["--facts", str(self.facts_path)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = sched.main([*args, *map(str, options)])
        self.assertEqual(result, status, stderr.getvalue())
        return stdout.getvalue(), stderr.getvalue()

    def next(self, *options):
        return json.loads(self.call("next", *options)[0])

    def explain(self, entry_id):
        rows = json.loads(self.call("explain", "--json")[0])["entries"]
        return next(row for row in rows if row["id"] == entry_id)

    def add(self, entry_id, kind, requires=(), params=None, **updates):
        entry = {
            **self.f0, "id": entry_id, "kind": kind, "repeat": False,
            "requires": list(requires), "params": params or {}, **updates,
        }
        self.queue["entries"].append(entry)
        return entry

    def test_standing_filler_invariant(self):
        self.f0["requires"].append("registered-window")
        self.assertIn(": NO_STANDING_FILLER:", self.call("validate", status=2)[1])

    def test_class_is_closed_and_errors_are_aggregated(self):
        self.rules[0]["class"] = "PACING"
        self.f0["surprise"] = 1
        errors = self.call("validate", status=2)[1].splitlines()
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any(": BAD_CLASS:" in line for line in errors))
        self.assertTrue(any(": UNKNOWN_KEY:" in line for line in errors))

    def test_no_timed_close_gap(self):
        for age in (0, 1, 1201):
            with self.subTest(age=age):
                self.f0["close_gap_s"] = 1200
                self.facts["closes"] = [close("f0-part-c", "diagnostic_filler", epoch(hour=14) - age)]
                self.assertEqual(self.next()["entry"], "f0-part-c")

    def test_frozen_launch_window(self):
        self.facts["now_epoch"] = epoch(hour=23, minute=10)
        decision = self.next()
        self.assertEqual((decision["decision"], decision["rule"], decision["until_epoch"]),
                         ("WAIT", "launcher-admits", epoch(19, 2, 35)))

    def test_product_before_diagnostic_and_high_power_any_hour(self):
        self.facts["now_epoch"] = epoch(hour=23, minute=10)
        self.add("hp-02", "product_filler", ["launcher-admits"],
                 {"launch_window_local": ["02:35:00", "22:40:00"]})
        self.assertEqual(self.next()["entry"], "hp-02")

    def test_future_date_and_fit(self):
        self.facts["now_epoch"] = epoch(hour=21)
        self.add("span", "counted", ["registered-window"], {
            "window": {"earliest_epoch": epoch(19), "latest_epoch": epoch(19, 0, 10)},
        }, worst_case_s=1000, expected_s=900)
        self.assertEqual(self.explain("span")["rule"], "registered-window")
        self.assertEqual(self.explain("f0-part-c")["rule"], "counted-fits")
        self.f0.update(worst_case_s=11000, expected_s=10000)
        self.assertEqual(self.next()["entry"], "f0-part-c")
        self.assertEqual(self.next("--now", epoch(19))["entry"], "span")

    def test_latest_start_works_back_through_block_without_retired_gaps(self):
        day_end = epoch(18, 23, 59, 59)
        self.facts["now_epoch"] = day_end - 26000
        window = {"earliest_epoch": day_end - 25000, "latest_epoch": day_end}
        for entry_id in ("first", "second"):
            self.add(entry_id, "counted", ["registered-window"], {"window": window},
                     block="pair", worst_case_s=24750, expected_s=20000, close_gap_s=300)
        self.f0.update(worst_case_s=1250, expected_s=1000)
        self.assertEqual(self.explain("f0-part-c")["status"], "ELIGIBLE")
        self.f0["worst_case_s"] = 1251
        self.assertEqual(self.explain("f0-part-c")["rule"], "counted-fits")

    def test_day_caps_count_launch_and_close_once_and_bind_only_counted(self):
        self.add("previous", "counted", params={"group": "dev-mixed", "legs": 12}, done=True)
        self.facts["launches"] = [{"entry_id": "previous", "t0_epoch": epoch(hour=11)}]
        self.facts["closes"] = [close("previous", "counted", epoch(hour=12), t0_epoch=epoch(hour=11))]
        params = {"group": "dev-mixed", "legs": 6, "date_caps": [{"group": "dev-mixed", "max": 12}]}
        self.add("span", "counted", ["registered-window"], params)
        self.add("filler", "product_filler", ["registered-window"], params)
        self.assertEqual(self.explain("span")["rule"], "registered-window")
        self.assertEqual(self.explain("filler")["status"], "ELIGIBLE")
        params["date_caps"][0]["max"] = 18
        self.assertEqual(self.next()["entry"], "span")

    def test_batch_clearance(self):
        self.queue["entries"].clear()
        self.queue["entries"].append(self.f0)
        self.f0["done"] = True
        now = self.facts["now_epoch"]
        self.facts["boot_epoch"] = now + 2400 - 43248
        self.add("qual", "counted", ["registered-window"], {
            "batch_clear": True, "soak_end_s": 1950,
        }, expected_s=12262, worst_case_s=15000)
        result = self.next()
        self.assertEqual((result["decision"], result["rule"], result["until_epoch"]),
                         ("WAIT", "registered-window", now + 2400 + 1620))

    def test_block_atomicity(self):
        self.add("first", "counted", block="pair")
        self.add("second", "counted", block="pair")
        self.add("session", "v4_session", ["session-route"])
        self.facts["closes"] = [close("first", "counted", epoch(hour=13))]
        self.facts["ready"] = [{"entry_id": "session", "effective": True}]
        self.assertEqual(self.next()["entry"], "second")

    def test_ready_refusal_releases_ladder_and_commit_change_clears_refusal(self):
        self.add("session", "v4_session", ["session-route", "not-refused"])
        self.facts["ready"] = [{"entry_id": "session", "effective": True}]
        self.facts["refusals"] = [{
            "entry_id": "session", "queue_commit": "synthetic-a",
            "epoch": epoch(hour=12), "reason": "synthetic refusal",
        }]
        self.assertEqual(self.next()["entry"], "f0-part-c")
        self.facts["queue_commit"] = "synthetic-b"
        self.assertEqual(self.next()["entry"], "session")

    def test_unreadable_host_facts_stop(self):
        self.facts["disk_free_gib"] = None
        self.assertIn("disk_free_gib", self.next()["detail"])
        self.facts["disk_free_gib"] = 120
        self.facts["closes"] = [close("f0-part-c", "diagnostic_filler", epoch(hour=13),
                                      restore_proven=None)]
        self.assertEqual(self.next()["decision"], "HALT")

    def test_foreign_process(self):
        self.facts["foreign_processes"] = [{"pid": 123, "name": "fixture-agent"}]
        result = self.next()
        self.assertEqual((result["decision"], result["rule"]), ("WAIT", "host-quiet"))
        self.assertLessEqual(result["until_epoch"], self.facts["now_epoch"] + 300)

    def test_rule_expiry(self):
        self.facts["now_epoch"] = epoch(hour=23, minute=10)
        rule = next(row for row in self.rules if row["id"] == "launcher-admits")
        rule.update(owner="lead", review_by="2026-11-17")
        self.assertEqual(self.next()["decision"], "LAUNCH")
        self.assertIn("FLAG", self.call("explain")[0])
        rule["owner"] = "research_lead"
        self.assertEqual(self.next()["decision"], "WAIT")
        self.assertIn("OVERDUE", self.call("explain")[0])

    def test_copy_wait_is_bounded_and_old_debt_does_not_hold_counted(self):
        now = self.facts["now_epoch"]
        self.add("counted", "counted")
        self.facts["closes"] = [close("old", "counted", now - 10)]
        self.facts["uncopied"] = [{"entry_id": "old", "kind": "counted", "ended_epoch": now - 10}]
        self.assertEqual(self.next()["until_epoch"], now + 590)
        self.assertEqual(self.next("--now", now + 590)["entry"], "counted")
        self.facts["closes"][0]["ended_epoch"] = now - 86401
        self.facts["uncopied"][0]["ended_epoch"] = now - 86401
        self.assertEqual(self.next()["entry"], "counted")

    def test_expected_ready_prefers_short_filler(self):
        self.add("soon", "counted", ["dependency"], {"gates": ["fixture-gate"]},
                 expected_ready_by=self.facts["now_epoch"] + 4000)
        self.add("short", "diagnostic_filler", expected_s=3600)
        self.assertEqual(self.next()["entry"], "short")

    def test_ruling_filler_ladder(self):
        for name in ("hp-02", "f2-inst-02", "f2-stab-02", "f2-inst-01", "f2-stab-01"):
            self.add(name, "product_filler")
        self.assertEqual(self.next()["entry"], "f2-stab-02")
        self.facts["closes"] = [close("f2-stab-02", "product_filler", epoch(hour=13))]
        self.assertEqual(self.next()["entry"], "f2-inst-01")
        for entry in self.queue["entries"]:
            if entry["id"].startswith("f2-inst"):
                entry["done"] = True
        self.assertEqual(self.next()["entry"], "hp-02")

    def test_receipt_projection(self):
        root = self.directory / "receipts"
        receipt = root / "a" / "b" / "c" / "runner_receipt.json"
        receipt.parent.mkdir(parents=True)
        data = json.loads((FIXTURES / receipt.name).read_text())
        write(receipt, data)
        (receipt.parent / "other.json").write_text("SENTINEL", encoding="utf-8")
        outside = self.directory / "outside"
        outside.mkdir()
        (root / "symlink").symlink_to(outside, target_is_directory=True)
        (outside / receipt.name).write_text("bad JSON", encoding="utf-8")
        out = self.directory / "probe.json"
        responses = {
            "pmset": "Now drawing from 'AC Power'\n - 100%; charged",
            "df": "Filesystem 1G-blocks Used Available Capacity  Mounted on\nfixture 500 100 400 20% /",
            "launchctl": "PID\tStatus\tLabel\n-\t0\tfixture",
            "ps": "PID PPID COMM\n10 1 fixture-agent\n11 10 fixture-agent\n12 1 fixture-agent\n",
            "sysctl": "{ sec = 1794900000, usec = 0 }",
        }

        def run(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, stdout=responses[Path(argv[0]).name], stderr="")

        rule = next(row for row in self.rules if row["id"] == "host-quiet")
        rule["params"]["patterns"] = ["fixture-agent"]
        with patch.object(sched.subprocess, "run", side_effect=run), patch.object(sched.time, "time", return_value=epoch()):
            self.call("probe", "--out", out, "--receipt-root", root, "--caller-pid", 10)
            initial = out.read_bytes()
            self.assertNotIn(b"SENTINEL", initial)
            facts = json.loads(initial)
            self.assertEqual(facts["foreign_processes"], [{"pid": 12, "name": "fixture-agent"}])
            self.assertEqual(facts["receipts"][0]["span_result"]["steps"], [{"name": "fixture-step", "rc": 0}])
            for section in (data, data["started"], data["ended"], data["span_result"],
                            data["span_result"]["steps"][0]):
                section["unread"] += 100000
            write(receipt, data)
            self.call("probe", "--out", out, "--receipt-root", root, "--caller-pid", 10)
            self.assertEqual(out.read_bytes(), initial)

    def test_report_and_deterministic_output(self):
        rows = [
            {"now_epoch": epoch(), "decision": "WAIT", "rule": "host-quiet"},
            {"now_epoch": epoch(hour=1), "decision": "HALT", "rule": "host-disk"},
            {"now_epoch": epoch(hour=3), "decision": "LAUNCH", "entry": "fixture"},
        ]
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        report = self.call("report", "--ledger", self.ledger, "--since", "2026-11-18T00:00:00-08:00")[0]
        self.assertIn("WAIT 1.000000", report)
        self.assertIn("HALT 2.000000", report)
        self.assertIn("host-quiet 1.000000", report)
        self.assertIn("host-disk 2.000000", report)
        first = self.call("next", "--record", self.ledger)[0]
        self.assertEqual(first, self.call("next")[0])
        self.assertEqual(json.loads(self.ledger.read_text().splitlines()[-1]),
                         {**json.loads(first), "now_epoch": self.facts["now_epoch"]})
        self.assertEqual(self.call("next")[0], self.call("next")[0])

    def test_ledger_events_and_close_owed(self):
        launch = {"event": "LAUNCH", "entry_id": "f0-part-c", "kit_sha256": None,
                  "t0_epoch": epoch(hour=13)}
        self.ledger.write_text(json.dumps(launch) + "\n", encoding="utf-8")
        self.assertEqual(self.next("--ledger", self.ledger),
                         {"decision": "CLOSE_OWED", "entry": "f0-part-c"})
        record = {"event": "CLOSE", **close("f0-part-c", "diagnostic_filler", epoch(hour=14),
                                           t0_epoch=launch["t0_epoch"], kit_sha256=None,
                                           copy_verified=True)}
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")

    def test_redates_missed_counted_window_by_calendar_date(self):
        self.add("late", "counted", ["registered-window"], {
            "window": {"earliest_epoch": epoch(17), "latest_epoch": epoch(17, 23, 59, 59)},
        })
        self.assertEqual(self.next()["entry"], "late")

    def test_launch_placeholders_are_interpolated_without_shell(self):
        rule = next(row for row in self.rules if row["id"] == "launcher-admits")
        rule["params"]["output_root"] = "/synthetic root"
        self.f0["params"]["kill_margin_s"] = 30
        self.f0["argv"] = ["example", "--deadline={deadline_epoch}", "{out}", "{magistrate_pid}"]
        now = self.facts["now_epoch"]
        self.assertEqual(self.next("--caller-pid", 99)["argv"],
                         ["example", f"--deadline={now + 12210}", f"/synthetic root/f0-part-c-{now}", "99"])


if __name__ == "__main__":
    unittest.main()
