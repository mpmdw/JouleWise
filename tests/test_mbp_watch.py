"""MBP span watcher (RL-173 C). Synthetic refs in a local bare repository; a fake REST API."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import mbp_watch as w
from tests.git_fixture import init_git_fixture

NOW = 1_900_000_000.0
PLAN = "cq-syn-02-s01-a1"
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "mbp-watch.yml"


def git(repo, *args, input=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@example.invalid", GIT_AUTHOR_DATE=f"{int(NOW) - 600} +0000",
               GIT_COMMITTER_DATE=f"{int(NOW) - 600} +0000")
    return subprocess.run(["git", "-C", str(repo), *args], input=input, capture_output=True, check=True,
                          env=env).stdout


class Remote:
    """A bare 'origin' with parentless result commits, and a clone that the watcher runs in."""

    def __init__(self, root):
        self.origin = root / "origin.git"
        self.origin.mkdir()
        init_git_fixture(self.origin, "--bare", "-q")
        self.work = root / "work"
        self.work.mkdir()
        init_git_fixture(self.work, "-q")
        git(self.work, "remote", "add", "origin", str(self.origin))

    def push_tree(self, ref, files, date=None):
        index = self.work / ".git" / "tmp-index"
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        for path, data in files.items():
            blob = subprocess.run(["git", "-C", str(self.work), "hash-object", "-w", "--stdin"], input=data,
                                  capture_output=True, check=True).stdout.decode().strip()
            subprocess.run(["git", "-C", str(self.work), "update-index", "--add", "--cacheinfo", "100644", blob, path],
                           env=env, check=True, capture_output=True)
        tree = subprocess.run(["git", "-C", str(self.work), "write-tree"], env=env, capture_output=True,
                              check=True).stdout.decode().strip()
        index.unlink()
        stamp = f"{int(date or NOW - 600)} +0000"
        commit = subprocess.run(["git", "-C", str(self.work), "commit-tree", tree, "-m", "synthetic"],
                                env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e.invalid",
                                         GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e.invalid",
                                         GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp),
                                capture_output=True, check=True).stdout.decode().strip()
        git(self.work, "push", "-q", "origin", f"{commit}:{ref}")
        return commit


class FakeApi:
    def __init__(self, issues=(), runs=()):
        self.issues = list(issues)
        self.runs = list(runs)
        self.calls = []

    def call(self, method, path, params=None, body=None):
        self.calls.append((method, path, params, body))
        if method == "GET" and path == "/issues":
            rows = [i for i in self.issues if params.get("state") == "all" or i.get("state") == params.get("state")]
            return rows if params.get("page", 1) == 1 else []
        if method == "GET" and path.startswith("/actions/workflows/"):
            return {"workflow_runs": self.runs}
        if method == "POST" and path == "/issues":
            self.issues.append({"title": body["title"], "state": "open", "number": len(self.issues) + 1})
            return {"number": len(self.issues)}
        return None


def transition(plan, status):
    return json.dumps({"schema": "joulewise.cadence_controller_transition.v1", "plan_id": plan,
                       "status": status, "t0_epoch": 0, "receipt_epoch": 0}).encode()


class MbpWatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mbp-watch-"))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.tmp)])
        self.remote = Remote(self.tmp)
        self.current = self.tmp / "CURRENT.json"
        self.write_current(None)

    def write_current(self, armed, deadline=None):
        doc = {"schema": "joulewise.current_pointer.v1", "armed": None, "wait": None, "owner": "magistrate",
               "next_observable": "x", "source_item": "1", "source_item_heading_date": None}
        if armed:
            doc["armed"] = {"plan_id": armed, "host": "mbp", "t0_epoch_s": NOW - 7200,
                            "latest_end_epoch_s": deadline or NOW - 3600}
            doc["wait"] = {"observable": "results_branch_exists", "deadline_epoch_s": deadline or NOW - 3600,
                           "on_early_or_refused": "x"}
        self.current.write_text(json.dumps(doc))

    def args(self, **kw):
        base = dict(repo="mpmdw/JouleWise", owner="mpmdw", current=str(self.current), grace_s=1200.0,
                    lookback_s=172800.0, plan_prefix="cq-", run_url="https://github.com/mpmdw/JouleWise/actions/runs/1",
                    dry_run=False, after_epoch=NOW - 1000, max_age_s=None)
        base.update(kw)
        return argparse.Namespace(**base)

    def run_watch(self, api, now=NOW, **kw):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = w.watch(self.args(**kw), git=w.Git(self.remote.work), api=api, now=now)
        return code, out.getvalue()

    def opened(self, api):
        return [c[3] for c in api.calls if c[:2] == ("POST", "/issues")]

    def test_silence_alarms_once_after_deadline_plus_grace(self):
        self.write_current(PLAN, deadline=NOW - 1000)  # deadline + 1200 s grace is still ahead
        api = FakeApi()
        self.assertEqual(self.run_watch(api)[0], 0)
        self.assertEqual(self.opened(api), [])
        self.write_current(PLAN, deadline=NOW - 1300)
        code, out = self.run_watch(api)
        issues = self.opened(api)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["title"], f"mbp-alarm SPAN_SILENT {PLAN} NO_RESULTS_REF")
        self.assertEqual(issues[0]["labels"], ["mbp-alarm"])
        self.assertEqual(issues[0]["assignees"], ["mpmdw"])
        self.assertTrue(issues[0]["body"].startswith("@mpmdw "))
        self.assertIn("OPENED mbp-alarm SPAN_SILENT", out)
        self.run_watch(api)  # the same event is not opened twice (closed issues count too)
        self.assertEqual(len(self.opened(api)), 1)

    def test_a_results_ref_ends_the_silence(self):
        self.write_current(PLAN, deadline=NOW - 5000)
        self.remote.push_tree(f"refs/heads/desk-bundles/{PLAN}", {"transition.json": transition(PLAN, "CLOSED_OK")})
        api = FakeApi()
        self.run_watch(api)
        self.assertEqual(self.opened(api), [])

    def test_stop_codes(self):
        self.remote.push_tree("refs/heads/desk-bundles/cq-syn-02-s02-a1",
                              {"transition.json": transition("cq-syn-02-s02-a1", "REFUSED")})
        self.remote.push_tree("refs/heads/night-results/cq-syn-02-s03-a1",
                              {"docs/process_traces/night-results/cq-syn-02-s03-a1/result.json":
                               json.dumps({"chain_exit_code": 3, "fault": False, "chain_outcome": "REFUSED"}).encode()})
        self.remote.push_tree("refs/heads/cadence-desk-final/cq-syn-02-s04-a1",
                              {"desk_verdict.json": json.dumps({"plan_id": "cq-syn-02-s04-a1", "next_arm_hold": True,
                                                                "holds": [{"code": "INSTRUMENT_FAULT"}]}).encode()})
        self.remote.push_tree("refs/heads/desk-bundles/cq-syn-02-s05-a1", {"transition.json": b"not json"})
        # Outside the prefix and not armed: ignored. Older than the lookback: ignored.
        self.remote.push_tree("refs/heads/desk-bundles/r9-other", {"transition.json": transition("r9-other", "REFUSED")})
        self.remote.push_tree("refs/heads/desk-bundles/cq-syn-01-s09-a1",
                              {"transition.json": transition("cq-syn-01-s09-a1", "REFUSED")}, date=NOW - 200000)
        api = FakeApi()
        self.run_watch(api)
        titles = sorted(i["title"].rsplit(" ", 1)[0] for i in self.opened(api))
        self.assertEqual(titles, ["mbp-alarm DESK_HOLD cq-syn-02-s04-a1 INSTRUMENT_FAULT",
                                  "mbp-alarm RESULT_UNREADABLE cq-syn-02-s05-a1 TRANSITION",
                                  "mbp-alarm SPAN_STOP cq-syn-02-s02-a1 REFUSED",
                                  "mbp-alarm SPAN_STOP cq-syn-02-s03-a1 CHAIN_EXIT_3"])

    def test_issue_body_carries_codes_only(self):
        secret = b"energy_j 123.456 token_ids [1,2,3] text"
        self.remote.push_tree(f"refs/heads/desk-bundles/{PLAN}",
                              {"transition.json": transition(PLAN, "STOPPED"), "bundle/legs/L001/leg_summary.json": secret})
        api = FakeApi()
        self.run_watch(api)
        (issue,) = self.opened(api)
        self.assertNotIn("energy", issue["body"])
        self.assertNotIn("123.456", issue["body"])
        for line in issue["body"].splitlines():
            self.assertRegex(line, r"^(|@mpmdw MBP span alarm.*|- [a-z_ ]+: .*|Close this issue.*)$")
        with self.assertRaises(w.WatchError):
            w.body({"code": "SPAN_STOP", "detail": "free text!", "plan": PLAN, "ref": None, "sha": None,
                    "times": {}}, "mpmdw", None)

    def test_invalid_current_alarms_and_failed_git_fails_the_run(self):
        self.current.write_text("{")
        api = FakeApi()
        self.run_watch(api)
        (issue,) = self.opened(api)
        self.assertTrue(issue["title"].startswith("mbp-alarm CURRENT_INVALID current-pointer POINTER "))
        broken = w.Git(self.tmp / "missing")
        with self.assertRaises(w.WatchError):
            w.watch(self.args(), git=broken, api=FakeApi(), now=NOW)
        args = ["watch", "--repo", "mpmdw/JouleWise", "--owner", "mpmdw", "--current", str(self.current)]
        err = io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(w.main(args), w.EXIT["usage"])  # no git repository here: the run fails
        finally:
            os.chdir(cwd)
        self.assertIn("MBP_WATCH_ERROR", err.getvalue())

    # --- the arm's read (C.4) -----------------------------------------------------------------

    def read(self, api, after):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = w.read(self.args(after_epoch=after), api=api, now=NOW)
        return code, out.getvalue()

    def test_read(self):
        stamp = lambda e: w.dt.datetime.fromtimestamp(e, w.dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa
        ok = {"id": 2, "conclusion": "success", "run_started_at": stamp(NOW - 300)}
        older = {"id": 1, "conclusion": "success", "run_started_at": stamp(NOW - 900)}
        self.assertEqual(self.read(FakeApi(runs=[older, ok]), NOW - 600)[0], w.EXIT["ok"])
        self.assertEqual(self.read(FakeApi(runs=[older, ok]), NOW - 200)[0], w.EXIT["stale"])
        self.assertEqual(self.read(FakeApi(runs=[]), NOW - 600)[0], w.EXIT["stale"])
        failed = dict(ok, conclusion="failure")
        self.assertEqual(self.read(FakeApi(runs=[older, failed]), NOW - 600)[0], w.EXIT["failed_run"])
        alarm = {"title": "mbp-alarm SPAN_SILENT x", "state": "open", "number": 7}
        code, out = self.read(FakeApi(runs=[ok], issues=[alarm]), NOW - 600)
        self.assertEqual(code, w.EXIT["open_alarm"])
        self.assertIn("first=#7", out)
        api = FakeApi(runs=[ok])
        self.read(api, NOW - 600)
        (method, path, params, _), = [c for c in api.calls if c[1].startswith("/actions")]
        self.assertEqual(path, "/actions/workflows/mbp-watch.yml/runs")
        self.assertEqual((params["branch"], params["status"]), ("main", "completed"))

    def test_workflow_shape(self):
        text = WORKFLOW.read_text()
        self.assertIn('cron: "*/10 * * * *"', text)
        self.assertIn("issues: write", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("python3 scripts/mbp_watch.py watch", text)
        self.assertIn("--grace-s 1200", text)
        self.assertEqual(w.WORKFLOW, WORKFLOW.name)


if __name__ == "__main__":
    unittest.main()
