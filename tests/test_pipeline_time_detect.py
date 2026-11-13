"""Pipeline watcher detectors over fixture RUN_STATE text, fixture ledgers and fixture ps output.

Pure: no network, no git, no live process. Sources are exercised with a fake runner only.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import tempfile
import time
import unittest
from pathlib import Path

from joulewise.pipeline_time import detect, ledger, runstate, sources
from joulewise.pipeline_time.detect import Proc, Snapshot

PST = timezone(timedelta(hours=-8))


def at(text: str) -> float:
    return datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=PST).timestamp()


def item(number, author, stamp, heading, pointer=None):
    who = {"magistrate": "Magistrate abcd1234 (headless, Opus 5.5)",
           "lead": "Laptop lead (interactive, Opus 5.5)"}[author]
    text = f"{number}. **{who}, {stamp} PST (`date`): {heading}**\n\n"
    if pointer:
        text += "```pointer\n" + "\n".join(f"{k}: {v}" for k, v in pointer.items()) + "\n```\n\n"
    return text + "- body line that is never read for state.\n\n"


HEADER = "# JouleWise Run State\n\nPreamble.\n\n"

ARMED_SESSION = HEADER + "".join([
    item(310, "magistrate", "2026-11-13 06:50",
         "Part A PASSED; the night is ARMED on `abc`. Plan `align-r1-20261113T1508Z`, t0 Fri 13 Nov 07:08 PST, "
         "latest end Sat 14 Nov 18:21 PST",
         {"owner": "magistrate", "wait": "chain.exited of align-r1-20261113T1508Z (latest end 2026-11-14T18:21:00-08:00)",
          "deadline": "2026-11-14T19:21:00-08:00", "on_early_or_refused": "mail Ed",
          "next_observable": "after chain.exited, the close"}),
    item(309, "lead", "2026-11-13 05:30", "MAGISTRATE: arm the night. Nothing is armed yet",
         {"owner": "magistrate", "wait": "none", "next_observable": "activation 2: plan, notice and install"}),
])

ARM_PENDING = HEADER + "".join([
    item(309, "magistrate", "2026-11-13 05:42", "ACTIVATION 1 DONE. PART A IS LAUNCHED. Nothing is armed.",
         {"owner": "magistrate", "wait": "Part A smoke's desk fence", "deadline": "2026-11-13T19:26:00-08:00",
          "on_early_or_refused": "nothing arms", "next_observable": "activation 2: checklist, plan, notice and install"}),
    item(308, "lead", "2026-11-13 05:30", "MAGISTRATE: the slot-producing night", None),
])

POINTER_ARMED = HEADER + "".join([
    item(300, "magistrate", "2026-11-12 14:33", "R1 FOLLOW-UP NIGHT ARMED: plan `align-r1-20261112T2251Z`",
         {"owner": "magistrate", "armed": "align-r1-20261112T2251Z", "host": "mbp",
          "t0": "2026-11-12T14:51:00-08:00", "latest_end": "2026-11-14T02:04:00-08:00",
          "wait": "result_json_exists", "deadline": "2026-11-14T03:04:00-08:00",
          "on_early_or_refused": "restore", "next_observable": "branch night-results/align-r1-20261112T2251Z"}),
])


def snap(text, now, **kw):
    return Snapshot(now=now, host="air", run_state=runstate.read(text) if text is not None else None, **kw)


def codes(alarms):
    return sorted(a.code for a in alarms)


CONFIG = dict(detect.DEFAULT_CONFIG)


class RunStateParsingTests(unittest.TestCase):
    def test_headings_classes_and_negation(self):
        rs = runstate.read(ARMED_SESSION)
        by = {i.label: i for i in rs.items}
        self.assertEqual(by["310"].classes, frozenset({"armed"}))
        self.assertEqual(by["309"].classes, frozenset())  # "Nothing is armed" is prose
        self.assertEqual(by["310"].author, "magistrate")
        self.assertEqual(by["309"].author, "lead")
        self.assertEqual(by["310"].stamp, at("2026-11-13 06:50"))

    def test_code_spans_do_not_classify(self):
        classes = runstate.classify("the magistrate was right (`MAGISTRATE-REFUSAL-aa.md`) and `FAILED` is a name")
        self.assertEqual(classes, frozenset())
        self.assertEqual(runstate.classify("RE-ARM REFUSED at 13:49"), frozenset({"refused"}))
        self.assertEqual(runstate.classify("FAULT: no Gmail tool"), frozenset({"fault"}))
        self.assertEqual(runstate.classify("the NIGHT IS CLOSED. Chain COMPLETE"), frozenset({"closed"}))
        self.assertEqual(runstate.classify("R1 is NOT ARMED"), frozenset())

    def test_stamp_formats(self):
        self.assertEqual(runstate.parse_stamp("x, 2026-11-13 05:42 PST (`date`)"), at("2026-11-13 05:42"))
        self.assertEqual(runstate.parse_stamp("2026-10-29 20:37-20:42Z"),
                         datetime(2026, 10, 29, 20, 37, tzinfo=timezone.utc).timestamp())
        self.assertEqual(runstate.parse_stamp("2026-10-28 ~23:10 PDT"),
                         datetime(2026, 10, 28, 23, 10, tzinfo=timezone(timedelta(hours=-7))).timestamp())
        self.assertIsNone(runstate.parse_stamp("no stamp here"))

    def test_pointer_inside_other_fence_is_ignored(self):
        text = HEADER + "````markdown\n262. **Laptop lead (x), 2026-11-11 04:10 PST: example**\n\n```pointer\nowner: lead\n```\n````\n\n" \
            + item(5, "lead", "2026-11-11 05:00", "real item")
        rs = runstate.read(text)
        self.assertEqual([i.label for i in rs.items], ["5"])
        self.assertIsNone(rs.pointer_item())

    def test_session_from_prose_when_pointer_lacks_armed(self):
        session = runstate.read(ARMED_SESSION).session()
        self.assertEqual(session.plan_id, "align-r1-20261113T1508Z")
        self.assertEqual(session.t0, at("2026-11-13 07:08"))
        self.assertEqual(session.latest_end, at("2026-11-14 18:21"))
        self.assertEqual(session.deadline, at("2026-11-14 19:21"))
        self.assertIsNone(session.closed_by)

    def test_session_from_pointer_keys(self):
        session = runstate.read(POINTER_ARMED).session()
        self.assertEqual(session.plan_id, "align-r1-20261112T2251Z")
        self.assertEqual(session.t0, at("2026-11-12 14:51"))
        self.assertEqual(session.latest_end, at("2026-11-14 02:04"))

    def test_time_only_t0_rolls_to_next_day(self):
        value = runstate._phrase_time("00:30 PST", at("2026-11-12 23:50"))
        self.assertEqual(value, at("2026-11-13 00:30"))
        self.assertEqual(runstate._phrase_time("Thu 11-12 03:25 PST", at("2026-11-10 20:00")), at("2026-11-12 03:25"))


class RunStateDetectorTests(unittest.TestCase):
    def test_arm_missing_after_deadline_only(self):
        self.assertEqual(detect.arm_missing(snap(ARM_PENDING, at("2026-11-13 19:00")), CONFIG), [])
        alarms = detect.arm_missing(snap(ARM_PENDING, at("2026-11-13 19:40")), CONFIG)
        self.assertEqual(codes(alarms), ["ARM_MISSING"])
        self.assertEqual(alarms[0].key, "arm_missing:309")

    def test_arm_missing_cleared_by_armed_or_refused_item(self):
        armed = ARM_PENDING.replace(HEADER, HEADER + item(310, "magistrate", "2026-11-13 19:00", "night ARMED"))
        self.assertEqual(detect.arm_missing(snap(armed, at("2026-11-13 20:00")), CONFIG), [])
        refused = ARM_PENDING.replace(HEADER, HEADER + item(310, "magistrate", "2026-11-13 19:00", "Part A FAILED"))
        self.assertEqual(detect.arm_missing(snap(refused, at("2026-11-13 20:00")), CONFIG), [])

    def test_arm_missing_from_directive_notice_issue(self):
        notices = [{"number": 900, "createdAt": "2026-11-13T20:00:00Z", "state": "OPEN"}]
        quiet = snap(ARM_PENDING.replace("install", "close"), at("2026-11-13 12:30"), notices=notices)
        self.assertEqual(detect.arm_missing(quiet, CONFIG), [])
        late = snap(ARM_PENDING.replace("install", "close"), at("2026-11-13 13:30"), notices=notices)
        self.assertEqual([a.key for a in detect.arm_missing(late, CONFIG)], ["arm_missing:notice-900"])
        armed = ARM_PENDING.replace("install", "close").replace(
            HEADER, HEADER + item(310, "magistrate", "2026-11-13 12:10", "night ARMED"))
        self.assertEqual(detect.arm_missing(snap(armed, at("2026-11-13 13:30"), notices=notices), CONFIG), [])

    def test_session_overdue_and_close(self):
        before = snap(ARMED_SESSION, at("2026-11-14 18:00"))
        self.assertEqual(detect.session_checks(before, CONFIG), [])
        after = snap(ARMED_SESSION, at("2026-11-14 18:30"), results_branch={"align-r1-20261113T1508Z": False})
        alarms = detect.session_checks(after, CONFIG)
        self.assertEqual(codes(alarms), ["SESSION_OVERDUE"])
        self.assertIn("results branch absent", alarms[0].summary)
        closed = ARMED_SESSION.replace(HEADER, HEADER + item(311, "magistrate", "2026-11-14 18:25",
                                                            "the NIGHT IS CLOSED: `align-r1-20261113T1508Z`"))
        self.assertEqual(detect.session_checks(snap(closed, at("2026-11-14 18:30")), CONFIG), [])

    def test_close_item_missing_after_30_min_of_results_branch(self):
        plan = "align-r1-20261113T1508Z"
        early = snap(ARMED_SESSION, at("2026-11-13 09:00"), results_branch={plan: True},
                     results_first_seen={plan: at("2026-11-13 08:40")})
        self.assertEqual(detect.session_checks(early, CONFIG), [])
        late = snap(ARMED_SESSION, at("2026-11-13 09:20"), results_branch={plan: True},
                    results_first_seen={plan: at("2026-11-13 08:40")})
        self.assertEqual(codes(detect.session_checks(late, CONFIG)), ["CLOSE_ITEM_MISSING"])

    def test_refused_or_fault_item_until_a_lead_item(self):
        text = HEADER + item(320, "magistrate", "2026-11-13 10:00", "R1 RE-ARM REFUSED at t0") + ARM_PENDING[len(HEADER):]
        alarms = detect.refused_items(snap(text, at("2026-11-13 10:05")), CONFIG)
        self.assertEqual([(a.code, a.key) for a in alarms], [("REFUSED_ITEM", "item:320")])
        answered = HEADER + item(321, "lead", "2026-11-13 10:20", "the refusal is diagnosed") + text[len(HEADER):]
        self.assertEqual(detect.refused_items(snap(answered, at("2026-11-13 10:25")), CONFIG), [])
        self.assertEqual(detect.refused_items(snap(text, at("2026-11-17 10:05")), CONFIG), [])
        lead_says = HEADER + item(320, "lead", "2026-11-13 10:00", "item 319's arm REFUSED")
        self.assertEqual(detect.refused_items(snap(lead_says, at("2026-11-13 10:05")), CONFIG), [])
        fault = HEADER + item(320, "magistrate", "2026-11-13 10:00", "FAULT: no Gmail tool")
        self.assertEqual(codes(detect.refused_items(snap(fault, at("2026-11-13 10:05")), CONFIG)), ["FAULT_ITEM"])

    def test_mbp_idle(self):
        lead_pointer = HEADER + item(330, "lead", "2026-11-13 10:00", "the lead runs verify on the Air",
                                     {"owner": "lead", "wait": "none", "next_observable": "the lead's verify"})
        self.assertEqual(detect.mbp_idle(snap(lead_pointer, at("2026-11-13 10:25")), CONFIG), [])
        alarms = detect.mbp_idle(snap(lead_pointer, at("2026-11-13 10:40")), CONFIG)
        self.assertEqual(codes(alarms), ["MBP_IDLE"])
        self.assertEqual(alarms[0].key, f"mbp_idle:{int(at('2026-11-13 10:00'))}")
        queued = snap(lead_pointer, at("2026-11-13 10:40"),
                      mbp_queue=[{"name": "r12-alpha", "started_epoch_s": at("2026-11-13 10:05"),
                                  "expected_end_epoch_s": at("2026-11-13 12:00")}])
        self.assertEqual(detect.mbp_idle(queued, CONFIG), [])
        finished = snap(lead_pointer, at("2026-11-13 12:20"),
                        mbp_queue=[{"name": "r12-alpha", "started_epoch_s": at("2026-11-13 10:05"),
                                    "expected_end_epoch_s": at("2026-11-13 12:00")}])
        self.assertEqual(detect.mbp_idle(finished, CONFIG), [])  # idle since 12:00, 20 min
        self.assertEqual(detect.mbp_state(snap(ARM_PENDING, at("2026-11-13 12:00")), CONFIG)[0], "magistrate")
        self.assertEqual(detect.mbp_state(snap(ARMED_SESSION, at("2026-11-13 12:00")), CONFIG)[0], "armed")
        past = detect.mbp_idle(snap(ARM_PENDING, at("2026-11-13 20:00")), CONFIG)
        self.assertEqual(codes(past), ["MBP_IDLE"])  # the magistrate's deadline passed 34 min ago

    def test_session_gap_budgets(self):
        closed = HEADER + item(340, "magistrate", "2026-11-13 00:00", "the NIGHT IS CLOSED (`align-r1-20261112T2251Z`)") \
            + POINTER_ARMED[len(HEADER):]
        self.assertEqual(detect.session_gap(snap(closed, at("2026-11-13 02:59")), CONFIG), [])
        alarms = detect.session_gap(snap(closed, at("2026-11-13 03:01")), CONFIG)
        self.assertEqual([(a.code, a.severity, a.stage) for a in alarms], [("SESSION_GAP", "warn", "session-gap")])
        changed = HEADER + item(341, "lead", "2026-11-13 01:00", "PR #800 merged: the kit fix") + closed[len(HEADER):]
        self.assertEqual(detect.session_gap(snap(changed, at("2026-11-13 05:00")), CONFIG), [])
        self.assertEqual(codes(detect.session_gap(snap(changed, at("2026-11-13 06:01")), CONFIG)), ["SESSION_GAP"])
        rearmed = HEADER + item(342, "magistrate", "2026-11-13 02:00", "night ARMED") + closed[len(HEADER):]
        self.assertEqual(detect.session_gap(snap(rearmed, at("2026-11-13 09:00")), CONFIG), [])


def row(run_id, event, stage, start, budget, **extra):
    base = {"schema": ledger.SCHEMA, "run_id": run_id, "event": event, "stage": stage, "kind": "run",
            "start_epoch_s": start, "budget_s": budget, "host": "air"}
    base.update(extra)
    return base


class LedgerDetectorTests(unittest.TestCase):
    def test_open_row_over_budget_is_profiled(self):
        now = 10_000.0
        rows = [row("a", "start", "block-analysis", now - 5500, 3600, child_pid=77, cmd="reader")]
        procs = [Proc(77, 1, 5500, 100, "python reader")]
        alarms = detect.ledger_checks(Snapshot(now=now, host="air", ledger_rows=rows, processes=procs), CONFIG)
        self.assertEqual([(a.code, a.profile_pid) for a in alarms], [("LEDGER_OVER", 77)])
        under = [row("b", "start", "block-analysis", now - 5300, 3600, child_pid=77)]
        self.assertEqual(detect.ledger_checks(Snapshot(now=now, host="air", ledger_rows=under, processes=procs), CONFIG), [])

    def test_remote_open_row_is_not_profiled_and_gone_pid_is_orphan(self):
        now = 10_000.0
        remote = [row("a", "start", "quick", now - 1000, 300, child_pid=77, host="mbp")]
        alarms = detect.ledger_checks(Snapshot(now=now, host="air", ledger_rows=remote, processes=[]), CONFIG)
        self.assertEqual([(a.code, a.profile_pid) for a in alarms], [("LEDGER_OVER", None)])
        local = [row("c", "start", "quick", now - 1000, 300, child_pid=78)]
        alarms = detect.ledger_checks(Snapshot(now=now, host="air", ledger_rows=local, processes=[]), CONFIG)
        self.assertEqual([(a.code, a.repeat) for a in alarms], [("LEDGER_ORPHAN", False)])

    def test_finished_overrun_is_a_one_shot_warning(self):
        now = 100_000.0
        rows = [row("d", "start", "test-unit", now - 2000, 600),
                row("d", "end", "test-unit", now - 2000, 600, end_epoch_s=now - 1000, wall_s=1000, exit=0),
                row("e", "end", "test-unit", now - 900, 600, end_epoch_s=now - 400, wall_s=500, exit=0),
                row("f", "end", "test-unit", now - 99_000, 600, end_epoch_s=now - 90_000, wall_s=9000, exit=0)]
        alarms = detect.ledger_checks(Snapshot(now=now, host="air", ledger_rows=rows), CONFIG)
        self.assertEqual([(a.code, a.key, a.repeat) for a in alarms], [("LEDGER_OVERRAN", "ledger_done:d", False)])


PS_TEXT = """\
  100     1    05:00:00   1:00.00 /bin/zsh launch-other.zsh
  101   100    05:00:00  10:00.00 /usr/bin/python3 scripts/independent_recompute_b6.py block --session x
  102   101    04:59:00  20:00.00 /usr/bin/python3 scripts/independent_recompute_b6.py worker
  200     1 01-02:00:00   0:01.00 zsh launch-closed-25.zsh
  201   200 01-01:59:00   3:00.00 /usr/bin/python3 scripts/b6_r12_courier_set.py --out r12-r3-closed-air-25
  300     1       20:00   0:10.00 /usr/bin/python3 -m unittest tests.test_x
  400     1    03:00:00   0:10.00 /usr/bin/python3 scripts/shard_tests.py --workers 4
  401   400    03:00:00   0:10.00 /usr/bin/python3 -m unittest tests.test_y
  500     1    09:00:00   0:00.10 /usr/bin/python3 -m unittest wrapped
"""


class LocalJobTests(unittest.TestCase):
    def setUp(self):
        self.procs = sources.parse_ps(PS_TEXT)
        self.config = dict(CONFIG, exempt=[{"pattern": "launch-closed-25\\.zsh", "reason": "RL-127 term 3"}])

    def test_parse_ps_and_etime(self):
        self.assertEqual(len(self.procs), 9)
        self.assertEqual(sources.parse_etime("01-02:00:00"), 26 * 3600)
        self.assertEqual(sources.parse_etime("20:00"), 1200)
        self.assertEqual(sources.parse_etime("1:00.00"), 60)
        self.assertIsNone(sources.parse_etime("junk"))

    def test_top_level_jobs_over_budget_exempt_and_wrapped(self):
        rows = [row("w", "start", "quick", 0.0, 300, pid=499, child_pid=500)]
        snapshot = Snapshot(now=50_000.0, host="air", processes=self.procs, ledger_rows=rows)
        alarms = detect.local_jobs(snapshot, self.config)
        found = sorted((a.profile_pid, a.stage) for a in alarms)
        # 101 is the block-analysis job (102 folds into it); 400 is a suite past 45 min; 300 is under;
        # 201 is exempt through its ancestor; 500 is under an open ledger run.
        self.assertEqual(found, [(101, "block-analysis"), (400, "pr-ci")])
        statuses = {proc.pid: status for proc, _rule, status in detect.local_job_candidates(snapshot, self.config)}
        self.assertEqual(statuses[201], "exempt")
        self.assertEqual(statuses[500], "wrapped")
        self.assertNotIn(102, statuses)
        self.assertNotIn(401, statuses)

    def test_watcher_never_reports_itself(self):
        snapshot = Snapshot(now=0.0, host="air", processes=self.procs, self_pid=400)
        self.assertNotIn(400, [a.profile_pid for a in detect.local_jobs(snapshot, self.config)])


class CiAndSourceTests(unittest.TestCase):
    def run_row(self, minutes, event="pull_request", workflow="ci", sha="s1"):
        start = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
        return {"databaseId": 1, "workflowName": workflow, "event": event, "headBranch": "b", "headSha": sha,
                "status": "in_progress", "startedAt": start.isoformat().replace("+00:00", "Z")}, \
            (start + timedelta(minutes=minutes)).timestamp()

    def test_ci_run_budgets(self):
        run, now = self.run_row(50)
        self.assertEqual(codes(detect.ci_runs(Snapshot(now=now, ci_runs=[run]), CONFIG)), ["CI_RUN_SLOW"])
        run, now = self.run_row(40)
        self.assertEqual(detect.ci_runs(Snapshot(now=now, ci_runs=[run]), CONFIG), [])
        run, now = self.run_row(8, event="push")
        self.assertEqual(codes(detect.ci_runs(Snapshot(now=now, ci_runs=[run], ci_state_only={"s1": True}), CONFIG)),
                         ["CI_RUN_SLOW"])
        run, now = self.run_row(8, event="pull_request")
        self.assertEqual(detect.ci_runs(Snapshot(now=now, ci_runs=[run], ci_state_only={"s1": True}), CONFIG), [])
        run, now = self.run_row(90, workflow="nightly-optin")
        self.assertEqual(detect.ci_runs(Snapshot(now=now, ci_runs=[run]), CONFIG), [])

    def test_source_failures(self):
        self.assertEqual(detect.source_failures(Snapshot(now=0, source_failures={"ps": 2}), CONFIG), [])
        self.assertEqual(codes(detect.source_failures(Snapshot(now=0, source_failures={"ps": 3}), CONFIG)),
                         ["WATCH_SOURCE_FAILED"])

    def test_run_all_on_unavailable_state_is_quiet(self):
        self.assertEqual(detect.run_all(Snapshot(now=0.0)), [])
        self.assertIn("RUN_STATE: unavailable", detect.status_lines(Snapshot(now=0.0)))


class FakeRunner:
    def __init__(self, replies):
        self.replies = replies
        self.calls = []

    def __call__(self, argv, timeout=60, input_text=None):
        self.calls.append(list(argv))
        for prefix, reply in self.replies:
            if argv[:len(prefix)] == prefix or (prefix and prefix[0] in argv and all(p in argv for p in prefix)):
                return reply
        return (0, "", "")


class SourcesTests(unittest.TestCase):
    def test_gather_uses_git_gh_ps_and_never_ssh(self):
        runner = FakeRunner([
            (["show"], (0, ARMED_SESSION, "")),
            (["issue", "list"], (0, '[{"number": 1, "createdAt": "2026-11-13T00:00:00Z", "state": "CLOSED"}]', "")),
            (["run", "list"], (0, "[]", "")),
            (["ls-remote"], (0, "abc\trefs/heads/night-results/align-r1-20261113T1508Z\n", "")),
            (["/bin/ps"], (0, PS_TEXT, "")),
        ])
        state = {}
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = sources.gather(Path(tmp), dict(CONFIG), state, now=at("2026-11-13 09:00"), runner=runner,
                                      ledger_file=Path(tmp) / "none.jsonl", queue_file=Path(tmp) / "q.json")
        self.assertEqual(snapshot.run_state.latest().label, "310")
        self.assertTrue(snapshot.results_branch["align-r1-20261113T1508Z"])
        self.assertEqual(state["results_first_seen"]["align-r1-20261113T1508Z"], at("2026-11-13 09:00"))
        self.assertEqual(len(snapshot.processes), 9)
        flat = [" ".join(call) for call in runner.calls]
        self.assertFalse(any("ssh" in call.split() for call in flat))
        self.assertTrue(any("refs/pipeline-watch/main" in call for call in flat))
        self.assertEqual(snapshot.source_failures, {})

    def test_gather_counts_failures(self):
        runner = FakeRunner([(["git"], (1, "", "offline")), (["gh"], (1, "", "offline")), (["/bin/ps"], (1, "", ""))])
        state = {"sources": {"run_state": 2}}
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = sources.gather(Path(tmp), dict(CONFIG), state, now=0.0, runner=runner,
                                      ledger_file=Path(tmp) / "none.jsonl", queue_file=Path(tmp) / "q.json")
        self.assertEqual(snapshot.source_failures["run_state"], 3)
        self.assertEqual(codes(detect.source_failures(snapshot, CONFIG)), ["WATCH_SOURCE_FAILED"])

    def test_state_only_commit(self):
        yes = FakeRunner([(["diff-tree"], (0, "RUN_STATE.md\ndocs/x.md\n", ""))])
        self.assertTrue(sources.state_only_commit(Path("."), "abc", yes))
        no = FakeRunner([(["diff-tree"], (0, "RUN_STATE.md\njoulewise/x.py\n", ""))])
        self.assertFalse(sources.state_only_commit(Path("."), "abc", no))
        self.assertIsNone(sources.state_only_commit(Path("."), "abc", FakeRunner([(["diff-tree"], (128, "", ""))])))

    def test_profile_signals_nothing_and_writes_a_file(self):
        procs = sources.parse_ps(PS_TEXT)
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "work"
            (work / "out").mkdir(parents=True)
            (work / "out" / "a.json").write_text("{}")
            runner = FakeRunner([
                (["/bin/ps"], (0, "  PID  PPID STAT ELAPSED TIME %CPU RSS COMMAND\n  101 100 R 1 1 95.0 10 x\n  102 101 R 1 1 50.0 10 y\n", "")),
                (["/usr/sbin/lsof"], (0, f"p101\nfcwd\nn{work}\n", "")),
            ])
            sleeps = []
            path = sources.capture_profile(101, "block-analysis", Path(tmp) / "profiles", procs, runner=runner,
                                           sleep=sleeps.append, now=time.time, use_sample=False)
            text = Path(path).read_text()
        self.assertEqual(sleeps, [10.0, 10.0])
        self.assertIn("cores in use 1.45", text)
        self.assertIn(f"     1  {work / 'out'}", text)
        tools = {call[0] for call in runner.calls}
        self.assertEqual(tools, {"/bin/ps", "/usr/sbin/lsof"})
        ps_calls = [call for call in runner.calls if call[0] == "/bin/ps"]
        self.assertEqual(len(ps_calls), 3)
        self.assertEqual(ps_calls[0][-1], "101,102")

    def test_rl128_probe_is_disabled(self):
        self.assertFalse(sources.RL128_PROBE_ENABLED)
        runner = FakeRunner([])
        result = sources.rl128_probe({}, 0.0, deadline_fired=True, runner=runner)
        self.assertFalse(result["ran"])
        self.assertEqual(runner.calls, [])


class ReviewFixTests(unittest.TestCase):
    """PR #759 cold-review fixes F1, F3, F4, F6, L1 and RL-132."""

    def test_f1_fetch_never_updates_the_shared_remote_tracking_ref(self):
        argv = sources.fetch_argv(Path("/repo"))
        self.assertIn("--refmap=", argv)
        self.assertIn("--no-write-fetch-head", argv)
        self.assertEqual(argv[-1], "+refs/heads/main:refs/pipeline-watch/main")
        self.assertFalse(any("refs/remotes" in token for token in argv))
        runner = FakeRunner([(["show"], (0, ARMED_SESSION, ""))])
        with tempfile.TemporaryDirectory() as tmp:
            sources.gather(Path(tmp), dict(CONFIG), {}, now=0.0, runner=runner,
                           ledger_file=Path(tmp) / "l.jsonl", queue_file=Path(tmp) / "q.json")
        fetches = [call for call in runner.calls if "fetch" in call]
        self.assertEqual(fetches, [sources.fetch_argv(Path(tmp))])

    def test_f1_report_fetch_uses_the_same_argv(self):
        from scripts import pipeline_time_report as rep
        runner = FakeRunner([(["show"], (0, ARMED_SESSION, "")), (["gh"], (0, "[]", ""))])
        args = type("A", (), {"end": None, "days": 7, "run_state": None, "repo": "o/r", "run_limit": 5,
                              "ledger": "/nonexistent/l.jsonl"})()
        rep.gather(args, runner=runner)
        fetches = [call for call in runner.calls if "fetch" in call]
        self.assertEqual(fetches, [sources.fetch_argv(rep.REPO)])

    def test_f3_failed_fetch_reads_the_last_fetched_copy_and_counts_the_failure(self):
        runner = FakeRunner([(["fetch"], (128, "", "timeout")), (["show"], (0, ARMED_SESSION, ""))])
        state = {}
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = sources.gather(Path(tmp), dict(CONFIG), state, now=0.0, runner=runner,
                                      ledger_file=Path(tmp) / "l.jsonl", queue_file=Path(tmp) / "q.json")
        self.assertIsNotNone(snapshot.run_state)
        self.assertTrue(snapshot.run_state_stale)
        self.assertEqual(state["sources"]["run_state"], 1)

    def test_f3_blind_sources_hold_their_keys(self):
        self.assertIn("session_overdue:", detect.held_prefixes(Snapshot(now=0.0)))
        held = detect.held_prefixes(Snapshot(now=0.0, run_state=runstate.read(ARMED_SESSION), ci_runs=[], processes=[]))
        self.assertEqual(held, ())

    def test_f4_nothing_armed_is_not_an_arm(self):
        self.assertEqual(runstate.classify("Part A FAILED; NOTHING ARMED"), frozenset({"fault"}))
        self.assertEqual(runstate.classify("so NOTHING WAS ARMED"), frozenset())
        self.assertEqual(runstate.classify("R1 is NOT YET ARMED"), frozenset())
        self.assertEqual(runstate.classify("the night WAS NOT ARMED"), frozenset())
        self.assertEqual(runstate.classify("R1 RE-ARMED, t0 13:46 PST"), frozenset({"armed"}))
        text = HEADER + item(320, "magistrate", "2026-11-13 10:00", "Part A FAILED; NOTHING ARMED") \
            + item(319, "lead", "2026-11-13 09:00", "the lead runs verify",
                   {"owner": "lead", "wait": "none", "next_observable": "verify"})
        self.assertIsNone(runstate.read(text).session())

    def test_l1_only_an_item_naming_the_plan_closes_the_session(self):
        plan = "align-r1-20261113T1508Z"
        generic = ARMED_SESSION.replace(HEADER, HEADER + item(311, "lead", "2026-11-13 12:00", "R12 nine COMPLETE"))
        self.assertIsNone(runstate.read(generic).session().closed_by)
        named = ARMED_SESSION.replace(HEADER, HEADER + item(311, "lead", "2026-11-14 01:00",
                                                            f"the night CLOSED: `night-results/{plan}` reports GO"))
        self.assertEqual(runstate.read(named).session().closed_by.label, "311")
        other_author = ARMED_SESSION.replace(HEADER, HEADER + item(311, "magistrate", "2026-11-14 01:00",
                                                                   f"night CLOSED `{plan}`").replace(
            "Magistrate abcd1234 (headless, Opus 5.5)", "Research lead"))
        self.assertIsNone(runstate.read(other_author).session().closed_by)
        planless = HEADER + item(252, "lead", "2026-11-10 19:15", "item 251's R1 re-arm REFUSED at 19:05") \
            + item(251, "magistrate", "2026-11-10 17:26", "R1 RE-ARMED, t0 18:08 PST 11-10")
        self.assertEqual(runstate.read(planless).session().closed_by.label, "252")

    def test_f6_rules_match_the_executable_and_script_only(self):
        self.assertEqual(detect.job_signature("/usr/bin/python3 -B -X importtime scripts/a.py --x b6_r12_"),
                         "/usr/bin/python3 scripts/a.py")
        self.assertEqual(detect.job_signature("Python -B -m unittest tests.x"), "Python -m unittest")
        self.assertEqual(detect.job_signature("zsh -c until ! pgrep -f independent_recompute_b6; do sleep 60; done"),
                         "zsh -c")
        self.assertEqual(detect.job_signature("codex exec rehearsal b6_r12_ unittest"), "codex exec")
        procs = sources.parse_ps(
            "  700     1    09:00:00   0:01.00 /bin/zsh -c until ! pgrep -f independent_recompute_b6; do sleep 60; done\n"
            "  701     1    09:00:00   0:01.00 /opt/bin/codex exec write the rehearsal fixture b6_r12_ -m unittest\n"
            "  702     1    09:00:00   0:01.00 /usr/bin/env -u X python3 scripts/independent_recompute_b6.py block\n"
            "  703   702    09:00:00   9:00.00 /usr/bin/python3 -B scripts/independent_recompute_b6.py block\n")
        alarms = detect.local_jobs(Snapshot(now=0.0, host="air", processes=procs), CONFIG)
        self.assertEqual([a.profile_pid for a in alarms], [703])

    def test_rl132_rehearsal_budget(self):
        import json as _json
        from joulewise.pipeline_time import budgets
        self.assertEqual(budgets.BUDGETS_S["rehearsal"], 6000)
        self.assertEqual(budgets.rehearsal_budget_s(25 * 60), 6000)
        rules = {r["name"]: r["budget_s"] for r in detect.DEFAULT_LOCAL_JOBS}
        self.assertEqual(rules["rehearsal"], 6000)
        config = _json.loads((Path(__file__).resolve().parents[1] / "scripts/air/pipeline_watch_config.json").read_text())
        self.assertEqual({r["name"]: r["budget_s"] for r in config["local_jobs"]}["rehearsal"], 6000)


if __name__ == "__main__":
    unittest.main()
