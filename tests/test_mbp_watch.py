"""MBP span watcher (RL-173 C). Synthetic refs in a local bare repository; a fake REST API."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts import mbp_watch as w
from tests.git_fixture import init_git_fixture

NOW = 1_800_000_000.0
PLAN = "cq-syn-02-s01-a1"
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "mbp-watch.yml"
PRIVATE = "ENERGY_J_123456_TOKEN_IDS_101_202_PRIVATE_TEXT"


class FakeApi:
    def __init__(self, issues=(), runs=(), drop_label=False, rules=("deletion", "non_fast_forward"),
                 drop_assignee=False):
        self.issues = list(issues)
        self.runs = list(runs)
        self.drop_label = drop_label
        self.drop_assignee = drop_assignee
        self.rules = rules
        self.calls = []

    def call(self, method, path, params=None, body=None, allow_422=False):
        self.calls.append((method, path, params, body))
        if method == "GET" and path == "/issues":
            rows = [i for i in self.issues if params.get("state") == "all" or i.get("state") == params.get("state")]
            if "labels" in params:
                rows = [i for i in rows if params["labels"] in [l.get("name") for l in i.get("labels") or []]]
            if "creator" in params:
                rows = [i for i in rows if i.get("creator", w.BOT) == params["creator"]]
            page = params.get("page", 1)
            return rows[(page - 1) * 100: page * 100]
        if method == "GET" and path.startswith("/actions/workflows/"):
            page = params.get("page", 1)
            chunk = self.runs[(page - 1) * 100: page * 100]
            return {"workflow_runs": chunk, "total_count": len(self.runs)}
        if method == "GET" and path == "/labels/mbp-alarm":
            return {"name": "mbp-alarm"}
        if method == "GET" and path.startswith("/rules/branches/"):
            return [{"type": t} for t in self.rules]
        if method == "POST" and path == "/issues":
            number = len(self.issues) + 1
            issue = {"title": body["title"], "body": body["body"], "state": "open", "number": number,
                     "labels": [] if self.drop_label else [{"name": n} for n in body["labels"]],
                     "assignees": [] if self.drop_assignee else [{"login": a} for a in body["assignees"]]}
            self.issues.append(issue)
            return dict(issue)
        if method == "PATCH" and path.startswith("/issues/"):
            issue = self.issues[int(path.rsplit("/", 1)[1]) - 1]
            issue["labels"] = [{"name": n} for n in body["labels"]]
            issue["assignees"] = [{"login": a} for a in body["assignees"]]
            return dict(issue)
        return None


class MbpWatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mbp-watch-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.origin = self.tmp / "origin.git"
        self.origin.mkdir()
        init_git_fixture(self.origin, "--bare", "-q")
        self.work = self.tmp / "work"
        self.work.mkdir()
        init_git_fixture(self.work, "-q")
        subprocess.run(["git", "-C", str(self.work), "remote", "add", "origin", str(self.origin)], check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            w.init_log(self.ns())

    # --- helpers ------------------------------------------------------------------------------

    def ns(self, **kw):
        base = dict(repo="mpmdw/JouleWise", owner="mpmdw", grace_s=1200.0,
                    run_url="https://github.com/mpmdw/JouleWise/actions/runs/1", dry_run=False,
                    after_epoch=NOW - 1000, max_age_s=7200.0, remote=str(self.origin), repo_dir=str(self.work))
        base.update(kw)
        return argparse.Namespace(**base)

    def arm(self, plan=PLAN, t0=NOW - 7200, deadline=NOW - 3600):
        with contextlib.redirect_stdout(io.StringIO()):
            return w.arm(self.ns(plan=plan, t0=t0, deadline=deadline))

    def close(self, status="CLOSED_OK", plan=PLAN, epoch=NOW - 3000):
        with contextlib.redirect_stdout(io.StringIO()):
            return w.close(self.ns(plan=plan, status=status, close_epoch=epoch), now=NOW)

    def push(self, ref, files):
        """A parentless commit straight into the bare origin (the controller's and the desk's refs)."""
        git = w.Git(self.origin)
        entries = b""
        for name, data in sorted(files.items()):
            blob = git.run("hash-object", "-w", "--stdin", input=data).decode().strip()
            entries += f"100644 blob {blob}\t{name}\n".encode()
        tree = git.run("mktree", input=entries).decode().strip()
        commit = git.run("commit-tree", tree, input=b"synthetic\n", env=w.IDENT).decode().strip()
        git.run("update-ref", ref, commit)

    def watch(self, api, now=NOW):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = w.watch(self.ns(), git=w.Git(self.work), api=api, now=now)
        return code, out.getvalue()

    @staticmethod
    def opened(api):
        return [c[3] for c in api.calls if c[:2] == ("POST", "/issues")]

    def titles(self, api):
        return sorted(i["title"].rsplit(" ", 1)[0] for i in self.opened(api))

    @staticmethod
    def transition(plan, status, t0, receipt=None, attempt=1):
        return json.dumps({"schema": w.TRANSITION_SCHEMA, "plan_id": plan, "attempt": attempt, "status": status,
                           "t0_epoch": t0, "receipt_epoch": t0 + 600 if receipt is None else receipt}).encode()

    # --- C.1 ----------------------------------------------------------------------------------

    def test_silence_after_deadline_plus_grace_and_once_per_arm(self):
        self.arm(deadline=NOW - 1000)  # deadline + 1200 s is still ahead
        api = FakeApi()
        self.assertEqual(self.watch(api)[0], 0)
        self.assertEqual(self.opened(api), [])
        code, out = self.watch(api, now=NOW + 300)
        (issue,) = self.opened(api)
        self.assertEqual(issue["title"].rsplit(" ", 1)[0], f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF")
        self.assertEqual((issue["labels"], issue["assignees"]), (["mbp-alarm"], ["mpmdw"]))
        self.assertTrue(issue["body"].startswith("@mpmdw "))
        self.assertIn("OPENED mbp-alarm SPAN_SILENT", out)
        api.issues[0]["state"] = "closed"
        self.watch(api, now=NOW + 900)  # the same arm commit is never re-filed, open or closed
        self.assertEqual(len(self.opened(api)), 1)

    def test_close_record_resolves_or_stops(self):
        self.arm()
        self.close("CLOSED_OK")
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.opened(api), [])
        other = "cq-syn-02-s02-a1"
        self.arm(plan=other)
        self.close("REFUSED", plan=other)
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm SPAN_STOP {other} REFUSED"])

    def test_arm_is_create_only_and_close_happens_once(self):
        self.arm()
        self.arm()  # the identical record again (a retry after a lost acknowledgement) is a no-op
        with self.assertRaises(w.WatchError):
            self.arm(deadline=NOW - 100)  # a different arm for the same plan id
        self.close("CLOSED_OK")
        with self.assertRaises(w.WatchError):
            self.close("STOPPED")
        with self.assertRaises(w.WatchError):
            self.close("CLOSED_OK", plan="cq-never-armed-a1")
        with self.assertRaises(w.WatchError):
            self.arm(plan="cq-bad-a1", t0=NOW, deadline=NOW - 1)

    def test_no_record_text_reaches_an_issue(self):
        self.arm(deadline=NOW - 5000)
        extra = json.dumps({"schema": w.CLOSE_SCHEMA, "plan_id": PLAN, "status": PRIVATE, "close_epoch_s": NOW - 6000,
                            "note": PRIVATE}).encode()
        self.log_commit(f"closes/{PLAN}.json", extra)
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm RESULT_UNREADABLE {PLAN} CLOSE_RECORD",
                                            f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF"])
        for issue in self.opened(api):
            self.assertNotIn("ENERGY", issue["title"] + issue["body"])
            for line in issue["body"].splitlines():
                self.assertRegex(line, r"^(|@mpmdw MBP span alarm.*|- [a-z0-9_ ]+: .*|Closing this issue.*"
                                       r"|<!-- mbp-watch-key: .* -->)$")
        bad = w.event("SPAN_STOP", PRIVATE, PLAN, w.LOG_REF, "a" * 40)
        with self.assertRaises(w.WatchError):
            w.body(bad, "mpmdw", None)

    def test_new_commit_is_a_new_episode_and_delivery_is_verified(self):
        self.arm(deadline=NOW - 5000)
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF"])
        api.issues[0]["state"] = "closed"
        self.close("STOPPED")
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF",
                                            f"mbp-alarm SPAN_STOP {PLAN} STOPPED"])
        self.arm(plan="cq-syn-05-s01-a1", deadline=NOW - 5000)
        with self.assertRaises(w.WatchError):
            self.watch(FakeApi(drop_label=True))

    def test_a_failed_git_read_fails_the_run(self):
        with self.assertRaises(w.WatchError):
            w.watch(self.ns(), git=w.Git(self.tmp / "missing"), api=FakeApi(), now=NOW)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(w.main(["arm", "--plan", PLAN, "--t0", str(NOW), "--deadline", str(NOW + 60),
                                     "--remote", str(self.tmp / "nowhere.git")]), w.EXIT["usage"])
        self.assertIn("MBP_WATCH_ERROR", err.getvalue())

    # --- C.4 ----------------------------------------------------------------------------------

    def read(self, runs, issues=(), after=NOW - 600, **kw):
        out = io.StringIO()
        api = FakeApi(runs=runs, issues=issues)
        with contextlib.redirect_stdout(out):
            code = w.read(self.ns(after_epoch=after, **kw), api=api, now=NOW)
        return code, out.getvalue(), api

    @staticmethod
    def wrun(number, started, conclusion="success", attempt=1):
        stamp = w.dt.datetime.fromtimestamp(started, w.dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"id": 1000 + number, "run_number": number, "run_attempt": attempt, "status": "completed",
                "conclusion": conclusion, "run_started_at": stamp}

    def test_read_exits(self):
        ok, older = self.wrun(2, NOW - 300), self.wrun(1, NOW - 900)
        self.assertEqual(self.read([older, ok])[0], w.EXIT["ok"])
        self.assertEqual(self.read([older, ok], after=NOW - 200)[0], w.EXIT["stale"])
        self.assertEqual(self.read([])[0], w.EXIT["stale"])
        self.assertEqual(self.read([older, self.wrun(2, NOW - 300, "failure")])[0], w.EXIT["failed_run"])
        self.assertEqual(self.read([self.wrun(3, NOW - 9000)], after=NOW - 10000)[0], w.EXIT["stale"])  # too old
        code, out, _ = self.read([ok], issues=[{"title": "x", "state": "open", "number": 7, "labels": [{"name": "mbp-alarm"}]}])
        self.assertEqual(code, w.EXIT["open_alarm"])
        self.assertIn("first=#7", out)
        _, _, api = self.read([ok])
        ((_, path, params, _),) = [c for c in api.calls if c[1].startswith("/actions")]
        self.assertEqual(path, "/actions/workflows/mbp-watch.yml/runs")
        self.assertEqual((params["branch"], params["status"]), ("main", "completed"))

    def test_read_refuses_malformed_answers(self):
        ok = self.wrun(1, NOW - 300)
        broken = dict(self.wrun(2, NOW - 200, "failure"), run_started_at=None)
        with self.assertRaises(w.WatchError):
            self.read([ok, broken])  # a malformed newer run is never skipped in favour of an older success
        with self.assertRaises(w.WatchError):
            self.read([self.wrun(1, NOW + 3600)])
        api = FakeApi(runs=[ok])
        api.call = lambda method, path, params=None, body=None, allow_422=False: (
            {"workflow_runs": [ok]} if path.startswith("/actions") else {})
        with self.assertRaises(w.WatchError), contextlib.redirect_stdout(io.StringIO()):
            w.read(self.ns(), api=api, now=NOW)

    # --- round-2 regressions (Sol r2 findings 1-7, 10) -----------------------------------------

    def test_unprotected_refs_fail_the_run(self):
        with self.assertRaises(w.WatchError) as caught:
            self.watch(FakeApi(rules=("deletion",)))
        self.assertIn("RULESET_MISSING", str(caught.exception))

    def test_a_silence_that_ended_between_polls_is_still_filed(self):
        self.arm(deadline=NOW - 3600)
        self.close("CLOSED_OK", epoch=NOW - 300)  # after deadline + grace: a silence nobody saw
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF"])

    def test_an_unconfirmed_delivery_is_repaired_on_the_next_run(self):
        self.arm(deadline=NOW - 5000)
        api = FakeApi(drop_assignee=True)
        with self.assertRaises(w.WatchError):
            self.watch(api)
        api.drop_assignee = False
        self.watch(api)
        (issue,) = api.issues
        self.assertEqual(issue["assignees"], [{"login": "mpmdw"}])
        self.assertTrue(any(c[0] == "PATCH" for c in api.calls))

    def test_close_chronology_is_checked_before_publishing(self):
        self.arm()
        with self.assertRaises(w.WatchError):
            self.close("CLOSED_OK", epoch=NOW - 9000)  # before the arm
        with self.assertRaises(w.WatchError):
            self.close("CLOSED_OK", epoch=NOW + 86400)  # in the future
        self.close("CLOSED_OK")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            w.parser().parse_args(["read", "--repo", "a/b", "--after-epoch", str(NOW), "--max-age-s", "nan"])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            w.parser().parse_args(["watch", "--repo", "a/b", "--owner", "o", "--grace-s", "-1"])

    def test_read_counts_a_later_failed_rerun(self):
        newer_failure = self.wrun(1, NOW - 100, "failure", attempt=2)
        self.assertEqual(self.read([newer_failure, self.wrun(2, NOW - 200)])[0], w.EXIT["failed_run"])
        self.assertEqual(self.read([self.wrun(1, NOW + 200)])[0], w.EXIT["ok"])  # within the 300 s clock slack

    def test_alarm_poll_acknowledges_only_confirmed_notifications(self):
        self.arm(deadline=NOW - 5000)
        api = FakeApi()
        self.watch(api)
        state = self.tmp / "poll.json"
        failed = []
        w.alarm_poll(state, lambda line: failed.append(line) and False, api)  # the banner failed
        sent = []
        w.alarm_poll(state, lambda line: sent.append(line) or True, api)  # retried, and confirmed
        w.alarm_poll(state, lambda line: sent.append(line) or True, api)  # then quiet
        self.assertEqual(len(failed), 1)
        self.assertEqual(len(sent), 1)
        self.assertTrue(sent[0].endswith(f"ALARM MBP_ALARM issue-1/SPAN_SILENT/{PLAN}"))

    def test_alarm_poll_reads_every_page(self):
        issues = [{"number": n, "state": "open", "body": "", "labels": [{"name": "mbp-alarm"}]} for n in range(1, 102)]
        sent = []
        w.alarm_poll(self.tmp / "poll.json", lambda line: sent.append(line) or True, FakeApi(issues=issues))
        self.assertEqual(len(sent), 101)

    # --- round-3 regressions (Sol r3 findings 1-7) -----------------------------------------------

    def log_commit(self, path, data, date=None):
        """A fast-forward commit on the log by hand (a mistaken edit, not via arm/close)."""
        git = w.Git(self.origin)
        tip = git.run("rev-parse", w.LOG_REF).decode().strip()
        index = self.tmp / "idx"
        env = {"GIT_INDEX_FILE": str(index)}
        git.run("read-tree", tip, env=env)
        blob = git.run("hash-object", "-w", "--stdin", input=data).decode().strip()
        git.run("update-index", "--add", "--cacheinfo", "100644", blob, path, env=env)
        tree = git.run("write-tree", env=env).decode().strip()
        index.unlink()
        stamp = {} if date is None else {"GIT_COMMITTER_DATE": f"{int(date)} +0000", "GIT_AUTHOR_DATE": f"{int(date)} +0000"}
        commit = git.run("commit-tree", tree, "-p", tip, input=b"edit\n", env={**w.IDENT, **stamp}).decode().strip()
        git.run("update-ref", w.LOG_REF, commit)

    def test_a_fast_forward_rewrite_of_the_log_alarms(self):
        self.arm(deadline=NOW - 5000)
        later = json.dumps({"schema": w.ARM_SCHEMA, "plan_id": PLAN, "attempt": 1, "t0_epoch_s": NOW,
                            "deadline_epoch_s": NOW + 3600}).encode()
        self.log_commit(f"arms/{PLAN}.json", later)  # postpones the deadline by editing the arm in place
        api = FakeApi()
        self.watch(api)
        titles = self.titles(api)
        self.assertIn("mbp-alarm RESULT_UNREADABLE span-watch-log LOG_REWRITTEN", titles)
        self.assertIn(f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF", titles)  # the original arm still counts

    def test_a_result_published_after_the_limit_is_a_silence(self):
        self.arm(deadline=NOW - 3600)
        record = json.dumps({"schema": w.CLOSE_SCHEMA, "plan_id": PLAN, "status": "CLOSED_OK",
                             "close_epoch_s": NOW - 3600}).encode() + b"\n"
        self.log_commit(f"closes/{PLAN}.json", record, date=NOW)  # finished on time, visible only now
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF"])

    def test_a_missing_log_fails_the_run(self):
        w.Git(self.origin).run("update-ref", "-d", w.LOG_REF)
        with self.assertRaises(w.WatchError) as caught:
            self.watch(FakeApi())
        self.assertIn("LOG_MISSING", str(caught.exception))

    def test_read_enumerates_every_page_of_the_window(self):
        runs = [self.wrun(n, NOW - 400 - n) for n in range(2, 140)]
        runs.append(self.wrun(1, NOW - 100, "failure", attempt=2))  # an old run's newer failed re-run, page two
        self.assertEqual(self.read(runs)[0], w.EXIT["failed_run"])

    def test_the_lead_banner_keeps_span_and_issue(self):
        from scripts.air import air_watch_agent as agent
        long_plan = "cq-" + "x" * 120 + "-a1"
        line = f"2026-11-15 00:00:00 ALARM MBP_ALARM issue-7/SPAN_SILENT/{long_plan}"
        self.assertTrue(agent.structural_text(line)[1].startswith("ALARM MBP_ALARM issue-7/SPAN_SILENT/cq-"))

    # --- round-4 regressions (Sol r4 findings 5-7) -----------------------------------------------

    def test_an_issue_created_without_its_label_is_found_and_repaired(self):
        self.arm(deadline=NOW - 5000)
        api = FakeApi(drop_label=True)
        with self.assertRaises(w.WatchError):
            self.watch(api)
        api.drop_label = False
        self.watch(api)
        self.assertEqual(len(api.issues), 1)  # repaired, not filed twice
        self.assertEqual(api.issues[0]["labels"], [{"name": "mbp-alarm"}])

    def test_a_full_window_of_healthy_runs_is_read_to_its_total(self):
        runs = [self.wrun(n, NOW - 5 * n) for n in range(1, 1001)]
        self.assertEqual(self.read(runs, after=NOW - 600)[0], w.EXIT["ok"])

    def test_workflow_shape(self):
        text = WORKFLOW.read_text()
        self.assertIn('cron: "3-59/10 * * * *"', text)
        self.assertIn("issues: write", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("python3 scripts/mbp_watch.py watch", text)
        self.assertIn("--grace-s 1200", text)
        self.assertEqual(w.WORKFLOW, WORKFLOW.name)


if __name__ == "__main__":
    unittest.main()
