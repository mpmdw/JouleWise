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

NOW = 1_900_000_000.0
PLAN = "cq-syn-02-s01-a1"
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "mbp-watch.yml"
PRIVATE = "ENERGY_J_123456_TOKEN_IDS_101_202_PRIVATE_TEXT"


class FakeApi:
    def __init__(self, issues=(), runs=(), drop_label=False):
        self.issues = list(issues)
        self.runs = list(runs)
        self.drop_label = drop_label
        self.calls = []

    def call(self, method, path, params=None, body=None, allow_422=False):
        self.calls.append((method, path, params, body))
        if method == "GET" and path == "/issues":
            rows = [i for i in self.issues if params.get("state") == "all" or i.get("state") == params.get("state")]
            return rows if params.get("page", 1) == 1 else []
        if method == "GET" and path.startswith("/actions/workflows/"):
            return {"workflow_runs": self.runs}
        if method == "GET" and path == "/labels/mbp-alarm":
            return {"name": "mbp-alarm"}
        if method == "POST" and path == "/issues":
            number = len(self.issues) + 1
            self.issues.append({"title": body["title"], "body": body["body"], "state": "open", "number": number})
            labels = [] if self.drop_label else [{"name": n} for n in body["labels"]]
            return {"number": number, "labels": labels, "assignees": [{"login": a} for a in body["assignees"]]}
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
            return w.close(self.ns(plan=plan, status=status, close_epoch=epoch))

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
    def transition(plan, status, t0):
        return json.dumps({"schema": w.TRANSITION_SCHEMA, "plan_id": plan, "status": status, "t0_epoch": t0,
                           "receipt_epoch": t0 + 10}).encode()

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
        with self.assertRaises(w.WatchError):
            self.arm(deadline=NOW - 100)  # a different arm for the same plan id (an identical one is a no-op)
        self.close("CLOSED_OK")
        with self.assertRaises(w.WatchError):
            self.close("STOPPED")
        with self.assertRaises(w.WatchError):
            self.close("CLOSED_OK", plan="cq-never-armed-a1")
        with self.assertRaises(w.WatchError):
            self.arm(plan="cq-bad-a1", t0=NOW, deadline=NOW - 1)

    def test_a_bound_bundle_resolves_and_a_stale_one_does_not(self):
        self.arm()
        self.push(f"refs/heads/desk-bundles/{PLAN}", {"transition.json": self.transition(PLAN, "CLOSED_OK", NOW - 7100)})
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.opened(api), [])
        other = "cq-syn-02-s03-a1"
        self.arm(plan=other)
        # A bundle from an earlier launch under the same name (t0 a day before this arm) is not this result.
        self.push(f"refs/heads/desk-bundles/{other}",
                  {"transition.json": self.transition(other, "CLOSED_OK", NOW - 90000)})
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm RESULT_UNREADABLE {other} TRANSITION_MISBOUND",
                                            f"mbp-alarm SPAN_SILENT {other} NO_RESULTS_REF"])

    def test_bundle_and_verdict_stops_without_an_arm_ref(self):
        self.push("refs/heads/desk-bundles/cq-syn-03-s01-a1",
                  {"transition.json": self.transition("cq-syn-03-s01-a1", "STOPPED", NOW - 5000)})
        self.push("refs/heads/cadence-desk-final/cq-syn-03-s02-a1",
                  {"desk_verdict.json": json.dumps({"plan_id": "cq-syn-03-s02-a1", "next_arm_hold": True,
                                                    "holds": [{"code": "INSTRUMENT_FAULT"}]}).encode()})
        self.push("refs/heads/desk-bundles/cq-syn-03-s03-a1", {"transition.json": b"not json"})
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), ["mbp-alarm DESK_HOLD cq-syn-03-s02-a1 INSTRUMENT_FAULT",
                                            "mbp-alarm RESULT_UNREADABLE cq-syn-03-s03-a1 TRANSITION",
                                            "mbp-alarm SPAN_STOP cq-syn-03-s01-a1 STOPPED"])

    # --- C.2 ----------------------------------------------------------------------------------

    def test_no_record_text_reaches_an_issue(self):
        self.push(f"refs/heads/cadence-desk-final/{PLAN}",
                  {"desk_verdict.json": json.dumps({"plan_id": PLAN, "next_arm_hold": True,
                                                    "holds": [{"code": PRIVATE}], "reasons": [PRIVATE]}).encode()})
        self.push("refs/heads/desk-bundles/cq-syn-04-s01-a1",
                  {"transition.json": json.dumps({"schema": w.TRANSITION_SCHEMA, "plan_id": "cq-syn-04-s01-a1",
                                                  "status": PRIVATE, "t0_epoch": 1}).encode()})
        api = FakeApi()
        self.watch(api)
        self.assertEqual(self.titles(api), [f"mbp-alarm DESK_HOLD {PLAN} UNKNOWN_HOLD",
                                            "mbp-alarm RESULT_UNREADABLE cq-syn-04-s01-a1 TRANSITION"])
        for issue in self.opened(api):
            self.assertNotIn("ENERGY", issue["title"] + issue["body"])
            for line in issue["body"].splitlines():
                self.assertRegex(line, r"^(|@mpmdw MBP span alarm.*|- [a-z_ ]+: .*|Closing this issue.*"
                                       r"|<!-- mbp-watch-key: .* -->)$")
        bad = w.event("SPAN_STOP", PRIVATE, PLAN, f"refs/heads/span-watch/{PLAN}", "a" * 40)
        with self.assertRaises(w.WatchError):
            w.body(bad, "mpmdw", None)

    # --- C.3 ----------------------------------------------------------------------------------

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
            self.assertEqual(w.main(["arm", "--plan", PLAN, "--t0", "1", "--deadline", "2",
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
    def wrun(number, started, conclusion="success"):
        stamp = w.dt.datetime.fromtimestamp(started, w.dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"id": 1000 + number, "run_number": number, "run_attempt": 1, "status": "completed",
                "conclusion": conclusion, "run_started_at": stamp}

    def test_read_exits(self):
        ok, older = self.wrun(2, NOW - 300), self.wrun(1, NOW - 900)
        self.assertEqual(self.read([older, ok])[0], w.EXIT["ok"])
        self.assertEqual(self.read([older, ok], after=NOW - 200)[0], w.EXIT["stale"])
        self.assertEqual(self.read([])[0], w.EXIT["stale"])
        self.assertEqual(self.read([older, self.wrun(2, NOW - 300, "failure")])[0], w.EXIT["failed_run"])
        self.assertEqual(self.read([self.wrun(3, NOW - 9000)], after=NOW - 10000)[0], w.EXIT["stale"])  # too old
        code, out, _ = self.read([ok], issues=[{"title": "x", "state": "open", "number": 7}])
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
