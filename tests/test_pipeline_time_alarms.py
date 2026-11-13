"""Alarm dedupe, delivery channels, the watcher's one-poll flow, and the weekly report. No network, no live process."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.pipeline_time import alarms, detect, report, runstate
from joulewise.pipeline_time.alarms import Alarm
from scripts import pipeline_watch
from tests.test_pipeline_time_detect import ARM_PENDING, HEADER, POINTER_ARMED, at, item

HOUR = 3600.0


def alarm(key="k1", severity="alarm", repeat=True):
    return Alarm(key, "CODE", severity, "summary text", detail="detail", repeat=repeat)


def kinds(actions):
    return [(a.kind, a.key, a.issue) for a in actions]


class PlanTests(unittest.TestCase):
    def test_new_alarm_raises_once_then_repeats_on_schedule(self):
        state = {}
        self.assertEqual(kinds(alarms.plan([alarm()], state, 0.0)), [("raise", "k1", True)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 0.5 * HOUR)), [("quiet", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 1.0 * HOUR)), [("repeat", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 5.0 * HOUR)), [("repeat", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 5.5 * HOUR)), [("quiet", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 6.0 * HOUR)), [("repeat", "k1", True)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 6.5 * HOUR)), [("quiet", "k1", False)])

    def test_issue_posts_at_most_once_per_six_hours_per_key(self):
        state, posts = {}, 0
        for step in range(0, 49):  # 24 h of 30-min polls
            posts += sum(1 for a in alarms.plan([alarm()], state, step * 0.5 * HOUR) if a.issue)
        self.assertEqual(posts, 5)  # 0, 6, 12, 18, 24 h

    def test_warn_never_uses_issues_and_repeats_every_six_hours(self):
        state = {}
        self.assertEqual(kinds(alarms.plan([alarm(severity="warn")], state, 0.0)), [("raise", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm(severity="warn")], state, 2 * HOUR)), [("quiet", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm(severity="warn")], state, 6 * HOUR)), [("repeat", "k1", False)])

    def test_resolve_and_flap_suppression(self):
        state = {}
        alarms.plan([alarm()], state, 0.0)
        state["alarms"]["k1"]["issue"] = 12
        self.assertEqual(kinds(alarms.plan([], state, 0.2 * HOUR)), [("resolve", "k1", True)])
        self.assertEqual(alarms.plan([], state, 0.3 * HOUR), [])
        # Back within the repeat interval: active again, nothing posted.
        self.assertEqual(kinds(alarms.plan([alarm()], state, 0.4 * HOUR)), [("quiet", "k1", False)])
        self.assertEqual(kinds(alarms.plan([alarm()], state, 1.0 * HOUR)), [("repeat", "k1", False)])

    def test_once_alarm_never_repeats(self):
        state = {}
        self.assertEqual(kinds(alarms.plan([alarm(repeat=False)], state, 0.0)), [("raise", "k1", True)])
        for t in (2 * HOUR, 7 * HOUR, 30 * HOUR):
            self.assertEqual(kinds(alarms.plan([alarm(repeat=False)], state, t)), [("quiet", "k1", False)])

    def test_resolved_records_are_pruned_after_a_week(self):
        state = {}
        alarms.plan([alarm()], state, 0.0)
        alarms.plan([], state, 1.0)
        alarms.plan([], state, 8 * 86400)
        self.assertEqual(state["alarms"], {})

    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s" / "state.json"
            self.assertEqual(alarms.load_state(path), {"alarms": {}})
            alarms.save_state(path, {"alarms": {"a": {"active": True}}})
            self.assertEqual(alarms.load_state(path)["alarms"]["a"]["active"], True)
            path.write_text("garbage")
            self.assertEqual(alarms.load_state(path), {"alarms": {}})


class Recorder:
    def __init__(self, replies=()):
        self.calls = []
        self.replies = list(replies)

    def __call__(self, argv, timeout=60, input_text=None):
        self.calls.append(list(argv))
        for match, reply in self.replies:
            if all(token in argv for token in match):
                return reply
        return (0, "", "")


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.jsonl = Path(self.tmp.name) / "ledger" / "alarms.jsonl"
        self.jsonl.parent.mkdir()

    def lines(self):
        return [json.loads(line) for line in self.jsonl.read_text().splitlines()]

    def test_raise_goes_to_every_channel(self):
        runner = Recorder([(["issue", "create"], (0, "https://github.com/o/r/issues/77\n", ""))])
        state = {}
        actions = alarms.plan([alarm()], state, 100.0)
        log = alarms.deliver(actions, 100.0, self.jsonl, {}, issues=alarms.IssueChannel("o/r", runner=runner),
                             runner=runner, host="air")
        self.assertEqual(self.lines()[0]["event"], "raise")
        self.assertEqual(self.lines()[0]["key"], "k1")
        osa = [c for c in runner.calls if c[0] == "/usr/bin/osascript"]
        self.assertEqual(len(osa), 1)
        self.assertIn("display notification", osa[0][2])
        create = [c for c in runner.calls if c[:3] == ["gh", "issue", "create"]][0]
        self.assertIn("pipeline-alarm", create)
        self.assertIn("pipeline-alarm-key: k1", create[create.index("--body") + 1])
        self.assertEqual(state["alarms"]["k1"]["issue"], 77)
        self.assertTrue(all("ok" in line for line in log))

    def test_existing_open_issue_is_reused_by_marker(self):
        listing = json.dumps([{"number": 5, "body": "x\n<!-- pipeline-alarm-key: k1 -->\n"}])
        runner = Recorder([(["issue", "list"], (0, listing, ""))])
        state = {}
        alarms.deliver(alarms.plan([alarm()], state, 0.0), 0.0, self.jsonl, {},
                       issues=alarms.IssueChannel("o/r", runner=runner), runner=runner)
        self.assertTrue(any(c[:4] == ["gh", "issue", "comment", "5"] for c in runner.calls))
        self.assertFalse(any(c[:3] == ["gh", "issue", "create"] for c in runner.calls))

    def test_resolve_closes_the_issue_and_logs(self):
        runner = Recorder()
        state = {}
        alarms.plan([alarm()], state, 0.0)
        state["alarms"]["k1"]["issue"] = 9
        alarms.deliver(alarms.plan([], state, 60.0), 60.0, self.jsonl, {},
                       issues=alarms.IssueChannel("o/r", runner=runner), runner=runner)
        self.assertTrue(any(c[:4] == ["gh", "issue", "close", "9"] for c in runner.calls))
        self.assertEqual(self.lines()[-1]["event"], "resolve")
        self.assertIsNone(state["alarms"]["k1"]["issue"])

    def test_channels_can_be_disabled_and_mail_is_optional(self):
        runner = Recorder()
        alarms.deliver(alarms.plan([alarm()], {}, 0.0), 0.0, self.jsonl,
                       {"notification": False, "issue": False, "mail_cmd": ["/opt/mailer", "--to", "lead"]},
                       issues=alarms.IssueChannel("o/r", runner=runner), runner=runner)
        self.assertEqual([c[0] for c in runner.calls], ["/opt/mailer"])

    def test_applescript_quoting(self):
        self.assertEqual(alarms.applescript_quote('a "b" \\ c'), '"a \\"b\\" \\\\ c"')


class WatchOnceTests(unittest.TestCase):
    """scripts/pipeline_watch.py once, offline, with a recording runner standing in for every tool."""

    def run_once(self, tmp, now, run_state, dry_run=False):
        path = Path(tmp) / "RUN_STATE.md"
        path.write_text(run_state)
        args = argparse.Namespace(now=now, state_dir=str(Path(tmp) / "state"), ledger_dir=str(Path(tmp) / "ledger"),
                                  run_state=str(path), offline=True, dry_run=dry_run)
        runner = Recorder([(["/bin/ps"], (0, "", "")),
                           (["issue", "create"], (0, "https://github.com/o/r/issues/3\n", ""))])
        config = dict(detect.DEFAULT_CONFIG, channels={}, profile={"use_sample": False})
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline_watch.once(args, config, runner=runner)
        return runner

    def test_poll_alarms_once_then_stays_quiet(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ledger").mkdir()
            first = self.run_once(tmp, at("2026-11-13 19:40"), ARM_PENDING)
            self.assertTrue(any(c[:3] == ["gh", "issue", "create"] for c in first.calls))
            jsonl = (Path(tmp) / "ledger" / "alarms.jsonl").read_text().splitlines()
            self.assertEqual([json.loads(line)["code"] for line in jsonl], ["ARM_MISSING"])
            second = self.run_once(tmp, at("2026-11-13 19:42"), ARM_PENDING)
            self.assertFalse(any(c[:2] == ["gh", "issue"] for c in second.calls))
            heartbeat = json.loads((Path(tmp) / "ledger" / "watch-heartbeat.json").read_text())
            self.assertIn("arm_missing:309", heartbeat["active_alarms"])
            self.assertFalse(any("ssh" in c for c in first.calls + second.calls))

    def test_dry_run_sends_and_saves_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ledger").mkdir()
            runner = self.run_once(tmp, at("2026-11-13 19:40"), ARM_PENDING, dry_run=True)
            self.assertEqual([c[0] for c in runner.calls], ["/bin/ps"])
            self.assertFalse((Path(tmp) / "state" / "state.json").exists())
            self.assertFalse((Path(tmp) / "ledger" / "alarms.jsonl").exists())


class ReportTests(unittest.TestCase):
    def test_build_covers_ledger_ci_prs_and_mbp(self):
        start, end = at("2026-11-12 00:00"), at("2026-11-15 00:00")
        closed = HEADER + item(305, "magistrate", "2026-11-12 22:27", "the NIGHT IS CLOSED") + POINTER_ARMED[len(HEADER):]
        rows = [
            {"schema": "joulewise.timing_ledger.v1", "run_id": "a", "event": "end", "stage": "block-analysis",
             "start_epoch_s": at("2026-11-13 00:00"), "end_epoch_s": at("2026-11-13 02:00"), "wall_s": 7200.0,
             "budget_s": 3600.0, "exit": 0, "host": "air", "cpu_s": 5000.0},
            {"schema": "joulewise.timing_ledger.v1", "run_id": "b", "event": "end", "stage": "quick",
             "start_epoch_s": at("2026-11-13 03:00"), "end_epoch_s": at("2026-11-13 03:02"), "wall_s": 120.0,
             "budget_s": 300.0, "exit": 0, "host": "air"},
        ]
        ci = [{"workflowName": "ci", "event": "pull_request", "status": "completed", "conclusion": "success",
               "createdAt": "2026-11-13T10:00:00Z", "startedAt": "2026-11-13T10:00:00Z",
               "updatedAt": "2026-11-13T11:00:00Z", "attempt": 1, "headSha": "x"},
              {"workflowName": "ci", "event": "push", "status": "completed", "conclusion": "cancelled",
               "createdAt": "2026-11-13T12:00:00Z", "startedAt": "2026-11-13T12:00:00Z",
               "updatedAt": "2026-11-13T12:20:00Z", "attempt": 2, "headSha": "y"}]
        prs = [{"number": 1, "createdAt": "2026-11-13T00:00:00Z", "mergedAt": "2026-11-13T04:00:00Z"}]
        markdown, summary = report.build(report.Inputs(start, end, rows, ci, prs, runstate.read(closed), {"y": True}))
        self.assertIn("| block-analysis | 1 | 2.00 |", markdown)
        self.assertIn("2.0x budget", markdown)
        self.assertIn("| ci | pull_request | 1 | 60.0 |", markdown)
        self.assertIn("State-only pushes to main: 1 of 1", markdown)
        self.assertIn("open-to-merge median 4.00 h", markdown)
        self.assertIn("Armed session", markdown)
        self.assertIn("| 305 | (none yet) |", markdown)
        self.assertTrue(any(line.startswith("MBP: session") for line in summary))
        # Session 11-12 14:51 to 22:27 inside a 72 h window.
        self.assertIn("| Armed session (to its close or refusal item) | 7.60 |", markdown)

    def test_unavailable_sources_are_reported_not_fatal(self):
        markdown, summary = report.build(report.Inputs(0.0, 86400.0, [], None, None, None, {}))
        self.assertIn("CI run list unavailable", markdown)
        self.assertIn("RUN_STATE unavailable", markdown)
        self.assertIn("ledger: no rows in window", summary)


class ReviewFixTests(unittest.TestCase):
    """PR #759 cold-review fixes F2, F3, F5 and L3."""

    def poll(self, tmp, now, run_state, runner=None, offline=True):
        path = Path(tmp) / "RUN_STATE.md"
        if run_state is not None:
            path.write_text(run_state)
        args = argparse.Namespace(now=now, state_dir=str(Path(tmp) / "state"), ledger_dir=str(Path(tmp) / "ledger"),
                                  run_state=str(path) if run_state is not None else None, offline=offline,
                                  dry_run=False)
        runner = runner or Recorder([(["/bin/ps"], (0, "", "")),
                                     (["issue", "create"], (0, "https://github.com/o/r/issues/3\n", ""))])
        config = dict(detect.DEFAULT_CONFIG, channels={}, profile={"use_sample": False})
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline_watch.once(args, config, runner=runner)
        return runner

    def test_f2_state_is_saved_before_delivery_and_a_failed_save_skips_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ledger").mkdir()
            order = []
            real_save = alarms.save_state

            class OrderRunner(Recorder):
                def __call__(self, argv, timeout=60, input_text=None):
                    if argv[:2] == ["gh", "issue"]:
                        order.append(("issue", (Path(tmp) / "state" / "state.json").exists()))
                    return super().__call__(argv, timeout, input_text)

            self.poll(tmp, at("2026-11-13 19:40"), ARM_PENDING,
                      runner=OrderRunner([(["issue", "create"], (0, "https://github.com/o/r/issues/3\n", ""))]))
            self.assertTrue(order and all(saved for _, saved in order))
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ledger").mkdir()
            with mock.patch.object(alarms, "save_state", side_effect=OSError("disk full")):
                runner = self.poll(tmp, at("2026-11-13 19:40"), ARM_PENDING)
                again = self.poll(tmp, at("2026-11-13 19:42"), ARM_PENDING)
            self.assertFalse(any(c[:2] == ["gh", "issue"] for c in runner.calls + again.calls))
            self.assertTrue((Path(tmp) / "ledger" / "alarms.jsonl").exists())
        self.assertIs(alarms.save_state, real_save)

    def test_f3_blind_run_state_never_resolves_its_alarms(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ledger").mkdir()
            self.poll(tmp, at("2026-11-13 19:40"), ARM_PENDING)
            blind = Recorder([(["/bin/ps"], (0, "", "")), (["git"], (128, "", "")), (["gh"], (1, "", ""))])
            self.poll(tmp, at("2026-11-13 19:42"), None, runner=blind, offline=False)
            self.assertFalse(any(c[:3] == ["gh", "issue", "close"] for c in blind.calls))
            state = alarms.load_state(Path(tmp) / "state" / "state.json")
            self.assertTrue(state["alarms"]["arm_missing:309"]["active"])
            events = [json.loads(line)["event"] for line in
                      (Path(tmp) / "ledger" / "alarms.jsonl").read_text().splitlines()]
            self.assertNotIn("resolve", events)

    def test_f3_plan_hold(self):
        state = {}
        alarms.plan([alarm("session_overdue:p")], state, 0.0)
        self.assertEqual(alarms.plan([], state, 60.0, hold=("session_overdue:",)), [])
        self.assertTrue(state["alarms"]["session_overdue:p"]["active"])
        self.assertEqual(kinds(alarms.plan([], state, 120.0)), [("resolve", "session_overdue:p", False)])

    def test_f5_crash_guard_posts_a_rate_limited_local_alarm(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_dir = Path(tmp) / "ledger"
            ledger_dir.mkdir()
            argv = ["--state-dir", str(Path(tmp) / "state"), "--ledger-dir", str(ledger_dir), "once"]
            runner = Recorder()
            with mock.patch.object(pipeline_watch, "once", side_effect=KeyError("pattern")), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(pipeline_watch.main(argv, runner=runner), 0)
                self.assertEqual(pipeline_watch.main(argv, runner=runner), 0)
            notes = [c for c in runner.calls if c[0] == "/usr/bin/osascript"]
            self.assertEqual(len(notes), 1)
            self.assertIn("PIPELINE_WATCH_CRASH", notes[0][2])
            self.assertFalse(any(c[0] == "gh" for c in runner.calls))
            lines = (ledger_dir / "alarms.jsonl").read_text().splitlines()
            self.assertEqual([json.loads(line)["code"] for line in lines], ["PIPELINE_WATCH_CRASH"])

    def test_l3_issue_text_carries_no_local_detail(self):
        from joulewise.pipeline_time import sources
        procs = sources.parse_ps("  901     1    09:00:00   9:00.00 /Users/edr/venv/bin/python3 -B "
                                 "scripts/independent_recompute_b6.py block --session /Users/edr/secret/s1\n")
        found = detect.run_all(detect.Snapshot(now=0.0, host="Edrs-MacBook-Air", processes=procs))
        self.assertEqual([a.code for a in found], ["LOCAL_JOB_OVER"])
        job = found[0]
        job.public += "; profile ledger/profiles/20261113T090000-block-analysis-901.txt"
        runner = Recorder([(["issue", "create"], (0, "https://github.com/o/r/issues/4\n", ""))])
        channel = alarms.IssueChannel("o/r", runner=runner)
        channel.raise_or_comment(job, {}, 0.0)
        create = [c for c in runner.calls if c[:3] == ["gh", "issue", "create"]][0]
        text = create[create.index("--title") + 1] + create[create.index("--body") + 1]
        for secret in ("/Users/", "edr", "secret", "Edrs-MacBook-Air", "--session", "python3", "cmd:"):
            self.assertNotIn(secret, text)
        self.assertIn("stage `block-analysis`", text)
        self.assertIn("budget 1.0 h", text)
        self.assertIn("ledger/profiles/20261113T090000-block-analysis-901.txt", text)
        self.assertIn(job.key, text)
        ledger_alarm = Alarm("ledger:r1", "LEDGER_OVER", "alarm", "reader on Edrs-MacBook-Air running 2 h",
                             detail="cmd: x\ncwd: /Users/edr/w", public="")
        body = channel.body(ledger_alarm, 0.0)
        self.assertNotIn("Edrs", body)
        self.assertNotIn("/Users", body)

    def test_l3_scrub(self):
        self.assertEqual(alarms.scrub("at /Users/edr/x and /Volumes/JW-EXT/y on host-a by bob", ["host-a", "bob"]),
                         "at <local path> and <local path> on <local> by <local>")


if __name__ == "__main__":
    unittest.main()
