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


def probe_child(argv, **kwargs):
    responses = {
        "pmset": "Now drawing from 'AC Power'\n - 100%; charged",
        "df": "Filesystem 1G-blocks Used Available Capacity  Mounted on\nfixture 500 100 400 20% /",
        "launchctl": "PID\tStatus\tLabel\n-\t0\tfixture",
        "ps": "PID PPID COMM\n10 1 fixture-agent\n11 10 fixture-agent\n12 1 fixture-agent\n",
        "sysctl": "{ sec = 1794900000, usec = 0 }",
    }
    return subprocess.CompletedProcess(argv, 0, stdout=responses[Path(argv[0]).name], stderr="")


def launch(entry_id, started, **updates):
    return {"event": "LAUNCH", "entry_id": entry_id, "kit_sha256": None,
            "t0_epoch": started, **updates}


def ledger_close(attempt, ended, **updates):
    readbacks = dict.fromkeys(sched.RESTORE_READBACKS, True)
    return {
        "kind": "diagnostic_filler", **attempt, "event": "CLOSE", "ended_epoch": ended,
        "clean": True, "restore_readbacks": readbacks, "copy_verified": True, **updates,
    }


def receipt(attempt, ended, **updates):
    identity = {key: attempt[key] for key in ("entry_id", "kit_sha256", "span_id") if key in attempt}
    return sched.project_receipt({
        **identity, "mock": False, "rc": 0, "started": {"epoch_s": attempt["t0_epoch"]},
        "ended": {"epoch_s": ended}, **updates,
    })


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
        owner = next(row for row in self.rules if row["test"] == "owner_stop")
        owner["params"]["maintenance_marker"] = str(self.directory / "maintenance-marker")
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

    def snapshot_closes(self, *closes):
        self.facts["closes"] = list(closes)
        self.facts["launches"] = [
            {"entry_id": row["entry_id"], "t0_epoch": row["t0_epoch"]} for row in reversed(closes)
        ]
        self.facts["receipts"] = [
            receipt(launch(row["entry_id"], row["t0_epoch"]), row["ended_epoch"]) for row in closes
        ]

    def explain(self, entry_id):
        rows = json.loads(self.call("explain", "--json")[0])["entries"]
        return next(row for row in rows if row["id"] == entry_id)

    def add(self, entry_id, kind, requires=(), params=None, **updates):
        entry = {
            **{key: value for key, value in self.f0.items() if key != "done"},
            "id": entry_id, "kind": kind, "repeat": False,
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
                self.snapshot_closes(close("f0-part-c", "diagnostic_filler", epoch(hour=14) - age))
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
        self.snapshot_closes(close("previous", "counted", epoch(hour=12), t0_epoch=epoch(hour=11)))
        params = {"group": "dev-mixed", "legs": 6, "date_caps": [{"group": "dev-mixed", "max": 12}]}
        self.add("span", "counted", ["registered-window"], params)
        self.add("filler", "product_filler", ["registered-window"], params)
        self.assertEqual(self.explain("span")["rule"], "registered-window")
        self.assertEqual(self.explain("filler")["status"], "ELIGIBLE")
        params["date_caps"][0]["max"] = 18
        self.assertEqual(self.next()["entry"], "span")

    def test_batch_clearance(self):
        now = self.facts["now_epoch"]
        self.facts["refusals"] = [{"entry_id": self.f0["id"], "queue_commit": self.facts["queue_commit"],
                                   "epoch": now, "reason": "synthetic refusal"}]
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
        self.snapshot_closes(close("first", "counted", epoch(hour=13)))
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
        self.snapshot_closes(close("f0-part-c", "diagnostic_filler", epoch(hour=13),
                                   restore_proven=None))
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
        self.snapshot_closes(close("old", "counted", now - 10))
        self.facts["uncopied"] = [{"entry_id": "old", "kind": "counted", "ended_epoch": now - 10}]
        self.assertEqual(self.next()["until_epoch"], now + 590)
        self.assertEqual(self.next("--now", now + 590)["entry"], "counted")
        self.snapshot_closes(close("old", "counted", now - 86401))
        self.facts["uncopied"][0]["ended_epoch"] = now - 86401
        self.assertEqual(self.next()["entry"], "counted")

    def test_expected_ready_prefers_short_filler(self):
        self.add("soon", "counted", ["block-dependency"], {"gates": ["fixture-gate"]},
                 expected_ready_by=self.facts["now_epoch"] + 4000)
        self.add("short", "diagnostic_filler", expected_s=3600)
        self.assertEqual(self.next()["entry"], "short")

    def test_ruling_filler_ladder(self):
        for name in ("hp-02", "f2-inst-02", "f2-stab-02", "f2-inst-01", "f2-stab-01"):
            self.add(name, "product_filler")
        self.assertEqual(self.next()["entry"], "f2-stab-02")
        self.snapshot_closes(close("f2-stab-02", "product_filler", epoch(hour=13)))
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
        rule = next(row for row in self.rules if row["id"] == "host-quiet")
        rule["params"]["patterns"] = ["fixture-agent"]
        with patch.object(sched.subprocess, "run", side_effect=probe_child) as run, patch.object(
                sched.time, "time", return_value=epoch()):
            self.call("probe", "--out", out, "--receipt-root", root, "--caller-pid", 10)
            self.assertEqual([call.args[0] for call in run.call_args_list], [
                ["/usr/bin/pmset", "-g", "batt"],
                ["/bin/df", "-g", "/"],
                ["/bin/launchctl", "list"],
                ["/bin/ps", "-axo", "pid,ppid,comm"],
                ["/usr/sbin/sysctl", "-n", "kern.boottime"],
            ])
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
        attempt = launch("f0-part-c", epoch(hour=13))
        self.ledger.write_text(json.dumps(attempt) + "\n", encoding="utf-8")
        self.assertEqual(self.next("--ledger", self.ledger),
                         {"decision": "CLOSE_OWED", "entry": "f0-part-c"})
        record = {"event": "CLOSE", **close("f0-part-c", "diagnostic_filler", epoch(hour=14),
                                           t0_epoch=attempt["t0_epoch"], kit_sha256=None,
                                           copy_verified=True)}
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
        self.assertEqual(self.next("--ledger", self.ledger)["rule"], "host-clean")
        record["restore_readbacks"] = dict.fromkeys(sched.RESTORE_READBACKS, True)
        self.facts["receipts"] = [receipt(attempt, record["ended_epoch"])]
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in (attempt, record)),
                               encoding="utf-8")
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")

    def test_probe_command_failure_writes_a_null_fact(self):
        out = self.directory / "probe.json"

        def run(argv, **kwargs):
            if Path(argv[0]).name == "df":
                return subprocess.CompletedProcess(argv, 1, stdout="", stderr="fixture")
            return probe_child(argv, **kwargs)

        with patch.object(sched.subprocess, "run", side_effect=run):
            self.call("probe", "--out", out, "--caller-pid", 10, "--host-facts", self.facts_path,
                      status=3)
        result = json.loads(out.read_text())
        self.assertIsNone(result["disk_free_gib"])
        self.assertIn("df exited 1", result["errors"]["disk_free_gib"])

    def test_probe_matches_close_to_receipt_identity(self):
        root = self.directory / "receipts"
        root.mkdir()
        receipt = json.loads((FIXTURES / "runner_receipt.json").read_text())
        now = self.facts["now_epoch"]
        recorded = close("f0-part-c", "diagnostic_filler", now - 1)
        recorded.update(event="CLOSE", kit_sha256=None, copy_verified=True,
                        restore_readbacks=dict.fromkeys(sched.RESTORE_READBACKS, True))
        self.write_events(launch(recorded["entry_id"], recorded["t0_epoch"]), recorded)
        receipt.update(entry_id=recorded["entry_id"], mock=False,
                       started={"epoch_s": recorded["t0_epoch"]},
                       ended={"epoch_s": recorded["ended_epoch"]})
        receipt_path = root / "runner_receipt.json"
        write(receipt_path, receipt)
        out = self.directory / "probe.json"
        args = ("--out", out, "--caller-pid", 10, "--host-facts", self.facts_path,
                "--receipt-root", root, "--ledger", self.ledger)
        with patch.object(sched.subprocess, "run", side_effect=probe_child):
            self.call("probe", *args)
            self.assertIs(json.loads(out.read_text())["closes"][0]["restore_proven"], True)
            receipt["entry_id"] = "different-entry"
            write(receipt_path, receipt)
            self.call("probe", *args)
            self.assertIsNone(json.loads(out.read_text())["closes"][0]["restore_proven"])

    def test_dry_run_executes_only_in_opted_in_probe_and_is_bound_to_inputs(self):
        self.f0["plan_argv"] = ["fixture-plan", "--check"]
        out = self.directory / "probe.json"

        def run(argv, **kwargs):
            if argv == self.f0["plan_argv"]:
                self.assertEqual(kwargs["timeout"], 120)
                self.assertEqual(kwargs["cwd"], self.f0["worktree"])
                return subprocess.CompletedProcess(argv, 0)
            return probe_child(argv, **kwargs)

        with patch.object(sched.subprocess, "run", side_effect=run) as called, patch.object(
                sched.time, "time", return_value=self.facts["now_epoch"]):
            self.assertEqual(self.next()["entry"], "f0-part-c")
            self.assertEqual(called.call_count, 0)
            self.call("probe", "--out", out, "--caller-pid", 10, "--host-facts", self.facts_path)
            self.assertEqual(called.call_count, 5)
            self.call("probe", "--out", out, "--caller-pid", 10, "--host-facts", self.facts_path,
                      "--run-plans")
            self.assertEqual(called.call_count, 11)
            self.facts = json.loads(out.read_text())
            self.assertEqual(self.next()["entry"], "f0-part-c")
            self.facts["queue_commit"] = "other"
            self.assertEqual(self.explain("f0-part-c")["rule"], "launcher-admits")
            self.assertEqual(called.call_count, 11)

    def test_named_fault_scopes_and_contamination_clearance(self):
        self.add("counted", "counted")
        self.add("affected", "product_filler")
        now = self.facts["now_epoch"]
        self.facts["stops"] = [
            {"code": "LEG_OVERTIME", "epoch": now - 100, "entry_id": "affected"},
            {"code": "CONTAMINATED_REDOS", "epoch": now - 100},
        ]
        self.assertEqual(self.explain("affected")["rule"], "not-refused")
        self.assertEqual(self.explain("counted")["rule"], "contaminated-redos")
        self.assertEqual(self.next()["entry"], "f0-part-c")
        self.snapshot_closes(close("f0-part-c", "diagnostic_filler", now - 1,
                                   load_redos=0, load_flag=False))
        self.assertEqual(self.next()["entry"], "counted")

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

    def write_events(self, *events):
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in events), encoding="utf-8")

    def test_latest_attempt_by_append_order_survives_clock_rollback(self):
        now = self.facts["now_epoch"]
        a, b = launch("a", now - 100), launch("b", now - 200)
        ac = ledger_close(a, now - 99)
        self.facts["receipts"] = [receipt(a, now - 99), receipt(b, now - 199)]
        self.write_events(a, ac, b)
        self.assertEqual(self.next("--ledger", self.ledger), {"decision": "CLOSE_OWED", "entry": "b"})
        bc = ledger_close(b, now - 199, restore_proven=False)
        self.write_events(a, ac, b, bc)
        decision = self.next("--ledger", self.ledger)
        self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "host-clean"))
        self.assertIn("b", decision["detail"])

    def test_reused_legacy_timestamp_does_not_borrow_first_attempt_close(self):
        attempt = launch("same-entry", self.facts["now_epoch"] - 100)
        self.facts["receipts"] = [receipt(attempt, attempt["t0_epoch"] + 1)]
        self.write_events(attempt, ledger_close(attempt, attempt["t0_epoch"] + 1), attempt)
        self.assertEqual(self.next("--ledger", self.ledger)["decision"], "CLOSE_OWED")
        a, b = ({**attempt, "sequence": sequence} for sequence in (1, 2))
        self.write_events(a, ledger_close(a, a["t0_epoch"] + 1), b, ledger_close(b, b["t0_epoch"] + 2))
        self.assertEqual(self.next("--ledger", self.ledger)["rule"], "host-clean")

    def test_sequence_takes_precedence_and_monotonic_orders_within_the_latest_boot(self):
        now = self.facts["now_epoch"]
        for a_fields, b_fields in (
                ({"sequence": 4}, {"sequence": 5}),
                ({"boot_id": "boot", "monotonic_ns": 4}, {"boot_id": "boot", "monotonic_ns": 5}),
                ({"boot_id": "old-z", "boot_order": 4}, {"boot_id": "new-a", "boot_order": 5}),
                ({"boot_order": 4}, {"boot_order": 5})):
            with self.subTest(a_fields=a_fields, b_fields=b_fields):
                a = launch("a", now - 100, span_id="span-a", **a_fields)
                b = launch("b", now - 200, span_id="span-b", **b_fields)
                self.write_events(b, a, ledger_close(a, now - 99))
                self.facts["receipts"] = [receipt(a, now - 99)]
                result = self.next("--ledger", self.ledger)
                self.assertEqual((result["decision"], result["entry"]), ("CLOSE_OWED", "span-b"))

    def test_latest_attempt_requires_its_own_receipt_in_both_input_paths(self):
        start = self.facts["now_epoch"] - 100
        a = launch("same-kit", start, span_id="span-a", sequence=1)
        b = launch("same-kit", start, span_id="span-b", sequence=2)
        ac, bc = ledger_close(a, start + 2), ledger_close(b, start + 1)
        self.write_events(a, ac, b, bc)
        self.facts["launches"] = [{k: v for k, v in row.items() if k != "event"} for row in (a, b)]
        self.facts["closes"] = [
            {**{k: v for k, v in row.items() if k not in ("event", "restore_readbacks")}, "restore_proven": True}
            for row in (bc, ac)
        ]
        for receipts in (None, [], [receipt(a, start + 2)]):
            self.facts["receipts"] = receipts
            for options in ((), ("--ledger", self.ledger)):
                with self.subTest(receipts=receipts, options=options):
                    decision = self.next(*options)
                    self.assertEqual((decision["decision"], decision["rule"]), ("HALT", "host-clean"))
                    self.assertIn("span-b", decision["detail"])
        self.facts["receipts"] = [receipt(a, start + 2), receipt(b, start + 1)]
        self.assertEqual(self.next("--ledger", self.ledger)["decision"], "LAUNCH")
        self.facts["launches"] = []
        result = self.next()
        self.assertEqual(result["rule"], "host-clean")
        self.assertIn("launch attempt history", result["detail"])

    def test_subsecond_close_comparison(self):
        second = self.facts["now_epoch"]
        attempt = launch("a", second - 1.25, span_id="span-a", sequence=1)
        self.write_events(attempt, ledger_close(attempt, second + 0.125))
        self.facts["receipts"] = [receipt(attempt, second + 0.125)]
        self.assertEqual(self.next("--ledger", self.ledger, "--now", second + 0.750)["decision"], "LAUNCH")
        decision = self.next("--ledger", self.ledger, "--now", second + 0.100)
        self.assertEqual(decision["rule"], "host-clean")

    def test_date_cap_uses_matching_close_metadata_when_launch_omits_legs(self):
        now = self.facts["now_epoch"]
        attempt = launch("prior-dev", now - 100, kind="counted", group="dev-mixed")
        self.write_events(attempt, ledger_close(attempt, now - 99, legs=12))
        self.facts["receipts"] = [receipt(attempt, now - 99)]
        self.add("next-dev", "counted", ["registered-window"], {
            "group": "dev-mixed", "legs": 6, "date_caps": [{"group": "dev-mixed", "max": 12}],
        })
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")
        self.write_events({**attempt, "legs": 1}, ledger_close(attempt, now - 99, legs=12))
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")

    def test_counted_date_constraints_require_a_live_window_rule(self):
        self.add("dev-tomorrow", "counted", params={
            "window": {"earliest_epoch": epoch(19), "latest_epoch": epoch(19, 23, 59, 59)},
        })
        for command in ("validate", "next"):
            self.assertIn(": UNBOUND_DATE_RULE:", self.call(command, status=2)[1])

    def test_started_filler_block_does_not_displace_ready_counted_or_v4(self):
        self.facts["now_epoch"] = epoch(hour=23)
        started = self.facts["now_epoch"] - 100
        a = launch("fill-1", started)
        self.write_events(a, ledger_close(a, started + 1, kind="product_filler"),
                          {"event": "READY", "entry_id": "ready", "effective": True})
        self.facts["receipts"] = [receipt(a, started + 1)]
        self.add("fill-1", "product_filler", block="fill-pair")
        self.add("fill-2", "product_filler", block="fill-pair")
        candidate = self.add("ready", "counted", ["registered-window", "session-route"], {
            "window": {"earliest_epoch": epoch(18), "latest_epoch": epoch(18, 23, 59, 59)},
        })
        for kind in ("counted", "v4_session"):
            with self.subTest(kind=kind):
                candidate["kind"] = kind
                self.assertEqual(self.next("--ledger", self.ledger)["entry"], "ready")

    def test_registered_maintenance_marker_cannot_be_overridden_or_clear_unknown_stop(self):
        marker = self.directory / "registered-marker"
        rule = next(row for row in self.rules if row["test"] == "owner_stop")
        rule["params"]["maintenance_marker"] = str(marker)
        out = self.directory / "probe.json"
        extra = self.directory / "absent-alternate"
        self.facts.pop("owner_stop")
        with patch.object(sched.subprocess, "run", side_effect=probe_child), patch.object(
                sched.time, "time", return_value=self.facts["now_epoch"]):
            self.call("probe", "--out", out, "--self-pid", 10, "--host-facts", self.facts_path)
            old_facts = self.facts
            self.facts = json.loads(out.read_text())
            self.assertIsNone(self.facts["owner_stop"])
            self.assertEqual(self.next()["rule"], "owner-stop")
            self.facts = old_facts
            marker.touch()
            self.facts["owner_stop"] = False
            self.call("probe", "--out", out, "--self-pid", 10, "--host-facts", self.facts_path,
                      "--maintenance-marker", extra)
        self.facts = json.loads(out.read_text())
        decision = self.next()
        self.assertEqual((decision["decision"], decision["rule"]), ("WAIT", "owner-stop"))

    def test_false_or_unknown_ac_stops_launch(self):
        for power in ({"ac": False, "charging": False}, {"ac": None}, None):
            with self.subTest(power=power):
                self.facts["power"] = power
                self.assertEqual(self.next()["rule"], "host-power")

    def test_active_repeating_filler_required(self):
        for changes in ({"kind": "maintenance"}, {"done": True}):
            with self.subTest(changes=changes):
                self.queue["entries"] = [{**self.f0, **changes}]
                self.assertIn(": NO_STANDING_FILLER:", self.call("validate", status=2)[1])

    def test_known_calendar_opening_beyond_ten_days(self):
        opening = epoch(30)
        self.add("dev-later", "counted", ["registered-window"], {
            "window": {"earliest_epoch": opening, "latest_epoch": opening + 36000},
        })
        self.facts["refusals"] = [{
            "entry_id": "f0-part-c", "queue_commit": self.facts["queue_commit"],
            "epoch": self.facts["now_epoch"], "reason": "synthetic refusal",
        }]
        result = self.next()
        self.assertEqual((result["decision"], result.get("until_epoch")), ("WAIT", opening))

    def test_partial_boot_metadata_does_not_hide_an_attempt(self):
        now = self.facts["now_epoch"]
        a = launch("A", now - 90, span_id="span-A")
        b = launch("B", now - 60, span_id="span-B", boot_id="boot-1", monotonic_ns=600)
        c = launch("C", now - 30, span_id="span-C")
        ac, bc, cc = [ledger_close(row, row["t0_epoch"] + 1) for row in (a, b, c)]
        cc["restore_readbacks"]["feeds_stopped"] = False
        self.facts["receipts"] = [receipt(row, row["t0_epoch"] + 1) for row in (a, b, c)]
        self.write_events(a, ac, b, bc, c)
        result = self.next("--ledger", self.ledger)
        self.assertEqual(result, {"decision": "CLOSE_OWED", "entry": "span-C"})
        self.write_events(a, ac, b, bc, c, cc)
        result = self.next("--ledger", self.ledger)
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "host-clean"))
        self.assertIn("span-C", result["detail"])

    def test_ledger_cannot_discard_observed_attempt_or_failed_close(self):
        now = self.facts["now_epoch"]
        b = launch("B", now - 60, sequence=2, span_id="span-B")
        c = launch("C", now - 30, sequence=3, span_id="span-C")
        bc, cc = [ledger_close(row, row["t0_epoch"] + 1) for row in (b, c)]
        cc["restore_readbacks"]["feeds_stopped"] = False
        self.facts["launches"] = [{k: v for k, v in row.items() if k != "event"} for row in (b, c)]
        self.facts["closes"] = [
            {**{k: v for k, v in row.items() if k not in ("event", "restore_readbacks")},
             "restore_proven": all(row["restore_readbacks"].values())} for row in (cc, bc)
        ]
        self.facts["receipts"] = [receipt(row, row["t0_epoch"] + 1) for row in (b, c)]
        for events in ((b, bc), (b, bc, c), (b, bc, c, ledger_close(c, now - 29)), (b, bc, c, cc)):
            with self.subTest(events=events):
                self.write_events(*events)
                result = self.next("--ledger", self.ledger)
                self.assertEqual((result["decision"], result["rule"]), ("HALT", "host-clean"))
                self.assertIn("span-C", result["detail"])

        self.write_events(b, bc)
        out = self.directory / "reconciled-probe.json"
        with patch.object(sched.subprocess, "run", side_effect=probe_child):
            self.call("probe", "--out", out, "--self-pid", 10, "--host-facts", self.facts_path,
                      "--ledger", self.ledger, status=3)
        self.assertIn("span-C", json.loads(out.read_text())["errors"]["attempt_history"])

        # A later correction is usable when the append-only log retains the failed readback.
        self.write_events(b, bc, c, cc, ledger_close(c, now - 28))
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")

    def test_ledger_cannot_reorder_observed_legacy_attempts(self):
        now = self.facts["now_epoch"]
        a, b = launch("A", now - 60), launch("B", now - 30)
        self.facts["launches"] = [{k: v for k, v in row.items() if k != "event"} for row in (a, b)]
        self.facts["receipts"] = [receipt(a, now - 59)]
        self.write_events(b, a, ledger_close(a, now - 59))
        self.assertEqual(self.next("--ledger", self.ledger)["rule"], "host-clean")

    def test_counted_date_caps_require_an_explicit_positive_candidate_leg_count(self):
        now = self.facts["now_epoch"]
        prior = launch("previous", now - 600, span_id="prior-span", kind="counted",
                       group="dev-mixed", legs=11)
        self.write_events(prior, ledger_close(prior, now - 590))
        self.facts["receipts"] = [receipt(prior, now - 590)]
        candidate = self.add("dev-next", "counted", ["registered-window"], {
            "group": "dev-mixed", "legs": 6, "date_caps": [{"group": "dev-mixed", "max": 12}],
        }, argv=["synthetic-counted", "--legs", "6"])
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")
        prior.pop("group")
        self.write_events(prior, ledger_close(prior, now - 590))
        self.assertEqual(self.next("--ledger", self.ledger)["entry"], "f0-part-c")
        for legs in (None, 0):
            with self.subTest(legs=legs):
                if legs is None:
                    candidate["params"].pop("legs")
                else:
                    candidate["params"]["legs"] = legs
                for command in ("validate", "next"):
                    self.assertIn("legs", self.call(command, status=2)[1])
        candidate["params"]["legs"] = 6
        candidate["params"].pop("group")
        self.assertIn("group", self.call("validate", status=2)[1])

    def test_filler_group_and_legs_do_not_displace_ready_counted_work(self):
        now = self.facts["now_epoch"] = epoch(hour=22, minute=39)
        candidate = self.add("dev-next", "counted", ["registered-window", "launcher-admits"], {
            "window": {"earliest_epoch": epoch(18), "latest_epoch": epoch(18, 23, 59, 59)},
            "group": "dev-mixed", "legs": 6, "date_caps": [{"group": "dev-mixed", "max": 12}],
            "not_on_dates_of": ["instrument"],
        }, plan_argv=["synthetic-plan"])
        self.facts["plans"] = {candidate["id"]: {
            "rc": 0, "signature": sched.plan_signature(candidate, self.facts["queue_commit"]),
        }}
        ready = {"event": "READY", "entry_id": candidate["id"], "effective": True}
        for kind in ("product_filler", "diagnostic_filler", "counted"):
            for group in ("dev-mixed", "instrument"):
                with self.subTest(kind=kind, group=group):
                    prior = launch("previous", now - 300, span_id="prior-span",
                                   kind=kind, group=group, legs=12)
                    self.write_events(prior, ledger_close(prior, now - 290), ready)
                    self.facts["receipts"] = [receipt(prior, now - 290)]
                    expected = "f0-part-c" if kind == "counted" else "dev-next"
                    self.assertEqual(self.next("--ledger", self.ledger)["entry"], expected)

    def test_registered_maintenance_observation_must_be_explicit(self):
        marker = self.directory / "active-maintenance"
        rule = next(row for row in self.rules if row["test"] == "owner_stop")
        rule["params"]["maintenance_marker"] = str(marker)
        out = self.directory / "probe.json"
        marker.touch()
        with patch.object(sched.subprocess, "run", side_effect=probe_child), patch.object(
                sched.time, "time", return_value=self.facts["now_epoch"]):
            self.call("probe", "--out", out, "--self-pid", 10, "--host-facts", self.facts_path)
        self.facts = json.loads(out.read_text())
        self.assertEqual(self.next()["decision"], "WAIT")
        self.facts["maintenance_active"] = None
        self.assertEqual(self.next()["rule"], "owner-stop")
        self.facts.pop("maintenance_active")
        result = self.next()
        self.assertEqual((result["decision"], result["rule"]), ("HALT", "owner-stop"))


if __name__ == "__main__":
    unittest.main()
