"""Desk-only cloud-suite acceptance: bounded fakes and disposable local remotes."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import cloud_suite as suite
from tests.git_fixture import init_git_fixture


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "cloud_suite_fixtures"
SCRIPT = ROOT / "scripts" / "cloud_suite.py"
BAD_ARG = re.compile(r"(?i)claude|codex")
REAL_POPEN = subprocess.Popen


def guarded_popen(argv, *args, **kwargs):
    """Catch unsafe argv in every subprocess started by the acceptance tests."""
    if isinstance(argv, (str, bytes)) or kwargs.get("shell"):
        raise AssertionError("tests require explicit argv without a shell")
    for value in argv:
        if BAD_ARG.search(os.fsdecode(value)):
            raise AssertionError(f"unsafe argv element: {value}")
    return REAL_POPEN(argv, *args, **kwargs)


def synthetic_ci(body=None):
    body = body or (
        'import os\n'
        'index = os.environ["SHARD_INDEX"]\n'
        'count = os.environ["SHARD_COUNT"]\n'
        'print(f"SHARD SUMMARY index={index}/{count} modules=1 tests=2 '
        'failures=0 errors=0 skipped=0 result=PASS")\n'
    )
    indented = "\n".join("          " + line for line in body.splitlines())
    return (
        "jobs:\n"
        "  test:\n"
        f"      - name: {suite.STEPS['test']}\n"
        "        run: |\n"
        "          python - <<'PY'\n" + indented + "\n          PY\n"
        "  calibration-exits-exclusive:\n"
        f"      - name: {suite.STEPS['calibration-exits-exclusive']}\n"
        "        run: python -m unittest -v tests.test_calibration_exits\n"
        "  calibration-writer-crash-matrix-exclusive:\n"
        "    strategy:\n"
        "      matrix:\n"
        "        shard: [1, 2]\n"
        f"      - name: {suite.STEPS['calibration-writer-crash-matrix-exclusive']}\n"
        "        run: |\n"
        "          python - <<'PY'\n" + indented + "\n          PY\n"
    )


class CloudSuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="b6-suite-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "work"
        self.bare = self.root / "remote.git"
        self.out = self.root / "out"
        self.out.mkdir()
        self.fake_cli = FIXTURES / "fake_cc_cli.py"
        self.fake_pty = FIXTURES / "fake_pty.py"
        self.guard = patch("subprocess.Popen", guarded_popen)
        self.guard.start()
        self.addCleanup(self.guard.stop)
        self.env = patch.dict(os.environ, {
            "CLOUD_SUITE_TEST_CREATED_TIMEOUT": "2",
            "CLOUD_SUITE_TEST_POST_CREATE_WAIT": "0.02",
            "CLOUD_SUITE_TEST_KILL_GRACE": "0.1",
            "CLOUD_SUITE_TEST_WATCH_POLL": "0.01",
            "CLOUD_SUITE_TEST_PUSH_BACKOFF": "0,0,0",
            "CLOUD_SUITE_TEST_TMP_ROOT": str(self.root / "worker-tmp"),
            "FAKE_CC_MODE": "created",
            "FAKE_CC_RECORD": str(self.root / "fake-record"),
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def git(self, *argv, repo=None):
        return subprocess.run(["git", "-C", str(repo or self.repo), *argv],
                              capture_output=True, text=True, check=True).stdout.strip()

    def make_repo(self, body=None):
        self.repo.mkdir()
        self.bare.mkdir()
        init_git_fixture(self.repo)
        init_git_fixture(self.bare, "--bare")
        self.git("config", "user.name", "suite-test")
        self.git("config", "user.email", "suite-test@invalid")
        (self.repo / ".github" / "workflows").mkdir(parents=True)
        (self.repo / ".github" / "workflows" / "ci.yml").write_text(synthetic_ci(body))
        (self.repo / "scripts").mkdir()
        shutil.copy2(SCRIPT, self.repo / "scripts" / "cloud_suite.py")
        for package in ("tests", "joulewise"):
            (self.repo / package).mkdir()
            (self.repo / package / "__init__.py").write_text("")
        (self.repo / "tests" / "test_calibration_exits.py").write_text(
            "import unittest\nclass Tiny(unittest.TestCase):\n"
            "    def test_ok(self): self.assertEqual(2 + 2, 4)\n")
        self.git("add", ".")
        self.git("commit", "-m", "fixture base")
        self.git("branch", "-M", "fixture-main")
        self.git("remote", "add", "origin", str(self.bare))
        self.git("push", "-u", "origin", "fixture-main")
        return self.git("rev-parse", "HEAD")

    def remote(self, sha, *, run="R1", job="ord-1", detach=True, timeout="0.2"):
        argv = [sys.executable, "-B", str(self.repo / "scripts" / "cloud_suite.py"),
                "remote-shard", "--run", run, "--job", job, "--shards", "12",
                "--sha", sha, "--branch-prefix", "x-suite", "--zsh-path", "/nonexistent",
                "--no-install", "--job-timeout-min", timeout]
        if detach:
            argv.append("--detach")
        result = subprocess.run(argv, cwd=self.repo, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        wait = subprocess.run([sys.executable, "-B", str(self.repo / "scripts" / "cloud_suite.py"),
                               "remote-wait", "--run", run, "--job", job,
                               "--max-wait", "12", "--poll", "0.02"],
                              cwd=self.repo, capture_output=True, text=True, timeout=15)
        self.assertEqual(wait.returncode, 0, wait.stderr)
        self.assertEqual(wait.stdout.strip(), "DONE pushed")
        branch = f"x-suite-{run}-{job}"
        raw = self.git("show", f"{branch}:suite/{run}/{job}.json", repo=self.bare)
        log = self.git("show", f"{branch}:suite/{run}/{job}.log", repo=self.bare)
        return json.loads(raw), log

    def state(self, sha, *, run="R1", jobs=("ord-1",), deadline=0.01):
        return {"repo": str(self.repo), "out_dir": str(self.out), "run": run, "sha": sha,
                "branch_prefix": "x-suite", "jobs": {job: {"url": "https://example.invalid/session"}
                                                       for job in jobs},
                "poll": 0.02, "deadline_min": deadline, "last_launch": time.time(),
                "branches": [], "keep_branches": True}

    def report(self, state):
        output = io.StringIO()
        with redirect_stdout(output):
            rc = suite.write_report(state)
        return rc, output.getvalue(), json.loads((self.out / "report.json").read_text())

    def launch(self, *, trust=False, wrapper=None):
        return suite.launch("ord-1", repo=str(self.root), out_dir=str(self.out), run="R1",
                            shards=12, sha="a" * 40, branch_prefix="x-suite",
                            cli=str(self.fake_cli), pty_wrapper=str(wrapper or self.fake_pty),
                            accept_trust=trust)

    def test_A1_real_ci_and_drift(self):
        text = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        ci = suite.parse_ci_jobs(text)
        self.assertEqual(set(ci), set(suite.STEPS))
        compile(ci["test"]["body"], "ordinary", "exec")
        self.assertIn('os.environ["SHARD_COUNT"]', ci["test"]["body"])
        self.assertIn('os.environ["SHARD_INDEX"]', ci["test"]["body"])
        self.assertEqual(ci["calibration-writer-crash-matrix-exclusive"]["shards"], [1, 2])
        self.assertEqual(ci["calibration-exits-exclusive"]["command"],
                         "python -m unittest -v tests.test_calibration_exits")
        self.make_repo()
        path = self.repo / ".github" / "workflows" / "ci.yml"
        path.write_text(text.replace(suite.STEPS["test"], "Renamed unit step"))
        self.git("add", ".")
        self.git("commit", "-m", "CI drift")
        self.git("push", "origin", "fixture-main")
        error = io.StringIO()
        with redirect_stderr(error):
            rc = suite.main(["run", "--repo", str(self.repo), "--out-dir", str(self.out),
                             "--branch-prefix", "x-suite", "--cli", str(self.fake_cli),
                             "--pty-wrapper", str(self.fake_pty)])
        self.assertEqual(rc, 2)
        self.assertIn(suite.STEPS["test"], error.getvalue())
        for old, new, expected in (("  test:", "  changed:", "missing CI job test"),
                                   ("python - <<'PY'", "python -", "missing python heredoc"),
                                   ("shard: [1, 2]", "shard: []", "missing shard matrix")):
            with self.subTest(expected=expected), self.assertRaisesRegex(suite.SuiteError, expected):
                suite.parse_ci_jobs(text.replace(old, new))

    def test_A2_job_table(self):
        ci = suite.parse_ci_jobs((ROOT / ".github" / "workflows" / "ci.yml").read_text())
        table = suite.job_table(ci, 12)
        self.assertEqual(len(table), 15)
        self.assertEqual(table["ord-12"]["shards"], 12)
        self.assertEqual(table["excl-crash-2"]["shards"], 2)
        self.assertEqual(list(suite.job_table(ci, 12, "ord-3,excl-exits")), ["ord-3", "excl-exits"])
        with self.assertRaisesRegex(suite.SuiteError, "unknown jobs"):
            suite.job_table(ci, 12, "ord-13")

    def test_A3_exact_prompt(self):
        expected = ("Do not edit, fix, investigate or open a pull request. Run exactly: "
                    "`python3.13 scripts/cloud_suite.py remote-shard --run R1 --job ord-3 "
                    "--shards 12 --sha abcdef --branch-prefix x-suite --detach`. Then run "
                    "`python3.13 scripts/cloud_suite.py remote-wait --run R1 --job ord-3 "
                    "--max-wait 540` repeatedly until it prints `DONE`. Then stop.")
        prompt = suite.build_prompt("R1", "ord-3", 12, "abcdef", "x-suite")
        self.assertEqual(prompt, expected)
        self.assertNotIn("@", prompt)
        self.assertNotIn("--force", prompt)
        guarded = list(("fake", "--cloud", prompt))
        self.assertFalse(any(BAD_ARG.search(value) for value in guarded))

    def test_A4_created_trust_retry_and_kill(self):
        self.assertIsNone(suite.parse_created("Created cloud session: session_A123"))
        result = self.launch()
        self.assertEqual(result.status, "LAUNCHED")
        self.assertEqual(result.session_id, "session_A123")
        self.assertTrue(result.url.endswith("/session_A123"))
        record = self.root / "fake-record"
        pid = int(record.read_text().splitlines()[0].split()[1])
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if f"terminated {pid}" in record.read_text():
                break
            time.sleep(0.02)
        else:
            self.fail("fake still executing after launch returned")
        record.unlink()
        with patch.dict(os.environ, {"FAKE_CC_MODE": "trust"}):
            accepted = self.launch(trust=True)
            self.assertEqual(accepted.status, "LAUNCHED")
            self.assertIn("trust 1b5b420d", record.read_text())
            record.unlink()
            refused = self.launch()
            self.assertEqual(refused.status, "LAUNCH_FAILED")
            self.assertIn("--accept-trust", refused.error)
            self.assertEqual(refused.attempts, 1)
        record.unlink()
        with patch.dict(os.environ, {"FAKE_CC_MODE": "silent", "CLOUD_SUITE_TEST_CREATED_TIMEOUT": "1.5"}):
            retry = self.launch()
        self.assertEqual(retry.status, "LAUNCH_FAILED")
        self.assertEqual(retry.attempts, 2)
        self.assertEqual(sum(line.startswith("started ") for line in record.read_text().splitlines()), 2)
        self.assertTrue((self.out / "launch" / "ord-1.attempt1.typescript").exists())

    def test_A5_detached_remote_pass_fail_sha_and_environment(self):
        sha = self.make_repo()
        data, log = self.remote(sha)
        self.assertEqual(self.git("rev-parse", "x-suite-R1-ord-1^", repo=self.bare), sha)
        self.assertEqual(data["run"], "R1")
        self.assertEqual(data["job"], "ord-1")
        self.assertEqual(data["sha"], sha)
        self.assertEqual(data["zsh"], "missing")
        self.assertEqual(data["rc"], 0)
        self.assertFalse(data["timed_out"])
        self.assertEqual(data["tests"], 2)
        self.assertEqual(data["failed_modules"], [])
        self.assertEqual(data["result"], "PASS")
        self.assertEqual(data["python"], sys.version)
        self.assertIsInstance(data["user_site"], bool)
        self.assertLessEqual(data["started"], data["finished"])
        self.assertIn("SHARD SUMMARY index=1/12", log)
        self.git("checkout", "fixture-main")
        exits, log = self.remote(sha, run="R2", job="excl-exits")
        self.assertEqual(exits["tests"], 1)
        self.assertEqual(exits["result"], "PASS")
        self.assertIn("Ran 1 test", log)
        self.git("checkout", "fixture-main")
        mismatch, _ = self.remote("0" * 40, run="R3")
        self.assertEqual(mismatch["status"], "SHA_MISMATCH")
        self.assertEqual(suite.classify(mismatch, sha), "SHA_MISMATCH")
        self.assertEqual(self.git("rev-parse", "x-suite-R3-ord-1^", repo=self.bare), sha)

    def test_A5_remote_failure_timeout_and_log_blocks(self):
        body = ('import os\n'
                'print("MODULE FAIL tests.fake tests=2 failures=1 errors=0 skipped=0 seconds=0.001")\n'
                'print("SHARD SUMMARY index=1/12 modules=1 tests=2 failures=1 errors=0 skipped=0 result=FAIL")\n'
                'raise SystemExit(1)\n')
        sha = self.make_repo(body)
        data, log = self.remote(sha)
        self.assertEqual(data["failed_modules"], ["tests.fake"])
        self.assertEqual(suite.classify(data, sha), "FAIL")
        self.assertIn("MODULE FAIL", log)
        self.git("checkout", "fixture-main")
        path = self.repo / ".github" / "workflows" / "ci.yml"
        path.write_text(synthetic_ci("import time\ntime.sleep(2)\n"))
        self.git("add", ".")
        self.git("commit", "-m", "timeout body")
        timeout_sha = self.git("rev-parse", "HEAD")
        data, _ = self.remote(timeout_sha, run="R2", timeout="0.003")
        self.assertTrue(data["timed_out"])
        self.assertEqual(suite.classify(data, timeout_sha), "TIMEOUT")
        path = self.root / "large.log"
        path.write_text("head\n" + "noise\n" * 100 + "FAIL: sample\ntraceback\nAssertionError\n"
                        "MODULE START next\n" + "noise\n" * 100 + "tail\n")
        with patch.dict(os.environ, {"CLOUD_SUITE_TEST_LOG_LIMIT": "160"}):
            suite._trim_log(path)
        trimmed = path.read_text()
        self.assertIn("truncated", trimmed)
        self.assertTrue(trimmed.startswith("head\n"))
        self.assertIn("FAIL: sample\ntraceback\nAssertionError", trimmed)
        self.assertTrue(trimmed.endswith("tail\n"))

    def test_A6_collect_pass_cleanup_exact_and_resume(self):
        sha = self.make_repo()
        self.remote(sha)
        self.git("push", "origin", "fixture-main:refs/heads/x-suite-other")
        self.git("push", "origin", "fixture-main:refs/heads/x-suite-R1-ord-2")
        self.git("update-ref", "-d", "refs/remotes/origin/x-suite-R1-ord-1")
        state = self.state(sha)
        before = self.git("for-each-ref", "--format=%(refname)")
        suite.collect(state)
        self.assertEqual(self.git("for-each-ref", "--format=%(refname)"), before)
        rc, output, report = self.report(state)
        self.assertEqual(rc, 0)
        self.assertRegex(output, rf"^CLOUD SUITE R1 sha={sha} jobs=1 pass=1 fail=0 incomplete=0 result=PASS\n$")
        self.assertEqual(report["jobs"][0]["environment_notes"], ["zsh=missing"])
        self.assertEqual(report["jobs"][0]["session_url"], "https://example.invalid/session")
        state["jobs"]["ord-1"]["data"]["user_site"] = False
        self.assertIn("user_site=false", self.report(state)[2]["jobs"][0]["environment_notes"])
        self.assertTrue((self.out / "ord-1.log").exists())
        self.assertTrue((self.out / "ord-1.json").exists())
        saved = self.out / "run.json"
        self.assertEqual(json.loads(saved.read_text())["jobs"]["ord-1"]["status"], "PASS")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(suite.main(["collect", "--state", str(saved)]), 0)
        self.assertEqual(suite.main(["cleanup", "--state", str(saved)]), 0)
        refs = self.git("for-each-ref", "--format=%(refname)", repo=self.bare)
        self.assertNotIn("x-suite-R1-ord-1", refs)
        self.assertIn("x-suite-other", refs)
        self.assertIn("x-suite-R1-ord-2", refs)

    def test_A6_collect_fail_missing_and_wrong_parent(self):
        body = ('print("MODULE FAIL tests.bad tests=1 failures=1 errors=0 skipped=0 seconds=0.001")\n'
                'print("SHARD SUMMARY index=1/12 modules=1 tests=1 failures=1 errors=0 skipped=0 result=FAIL")\n'
                'raise SystemExit(1)\n')
        sha = self.make_repo(body)
        self.remote(sha)
        state = self.state(sha)
        suite.collect(state)
        rc, _, report = self.report(state)
        self.assertEqual(rc, 1)
        self.assertEqual(report["jobs"][0]["failed_modules"], ["tests.bad"])
        self.assertIn("tests.bad", (self.out / "report.md").read_text())
        missing = self.state(sha, run="never-pushed")
        suite.collect(missing)
        self.assertEqual(missing["jobs"]["ord-1"]["status"], "MISSING")
        self.assertEqual(self.report(missing)[0], 3)
        # A matching JSON payload under a different parent cannot pass.
        self.git("checkout", "fixture-main")
        (self.repo / "extra").write_text("new parent")
        self.git("add", "extra")
        self.git("commit", "-m", "wrong parent")
        wrong = self.git("rev-parse", "HEAD")
        self.remote(wrong, run="bad-parent")
        data_path = self.repo / "suite" / "bad-parent" / "ord-1.json"
        data = json.loads(data_path.read_text())
        log = data_path.with_suffix(".log").read_text()
        data.update(sha=sha, rc=0, result="PASS", failures=0, failed_modules=[])
        # Rebuild an unpublished result commit on the wrong parent, then push
        # to a fresh run/job branch; no rewrite of a remote branch is needed.
        self.git("checkout", "-b", "repacked", wrong)
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(data))
        data_path.with_suffix(".log").write_text(log)
        self.git("add", "-f", "suite/bad-parent/ord-1.json", "suite/bad-parent/ord-1.log")
        self.git("commit", "-m", "mismatched result")
        # The result's run also needs to match: use the same exact branch name
        # by selecting a new prefix, without rewriting any existing remote.
        self.git("push", "origin", "repacked:refs/heads/y-suite-bad-parent-ord-1")
        bad = self.state(sha, run="bad-parent")
        bad["branch_prefix"] = "y-suite"
        suite.collect(bad)
        self.assertEqual(bad["jobs"]["ord-1"]["status"], "SHA_MISMATCH")
        self.assertEqual(self.report(bad)[0], 1)

    @unittest.skipUnless(sys.platform == "darwin", "BSD script acceptance is Darwin-only")
    def test_A7_real_bsd_pty(self):
        with patch.dict(os.environ, {"CLOUD_SUITE_TEST_CREATED_TIMEOUT": "3"}):
            result = self.launch(wrapper="/usr/bin/script")
        self.assertEqual(result.status, "LAUNCHED", result.error)
        self.assertEqual(result.session_id, "session_A123")

    def test_argv_guard(self):
        for value in ("claude", "CODEX", "/tmp/some-claude-dir/file"):
            with self.subTest(value=value), self.assertRaisesRegex(AssertionError, "unsafe argv"):
                guarded_popen([sys.executable, value])
        self.assertFalse(BAD_ARG.search(str(self.root)))

    def test_preflight_and_full_run_using_fakes(self):
        sha = self.make_repo()
        argv = ["run", "--repo", str(self.repo), "--only", "ord-1", "--shards", "12",
                "--out-dir", str(self.out), "--cli", str(self.fake_cli),
                "--pty-wrapper", str(self.fake_pty), "--branch-prefix", "x-suite",
                "--deadline-min", "0", "--poll", "0.01"]
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(suite.main(argv), 3)
        self.assertTrue(output.getvalue().splitlines()[-1].endswith("result=INCOMPLETE"))
        saved = json.loads((self.out / "run.json").read_text())
        self.assertEqual(saved["sha"], sha)
        self.assertEqual(saved["jobs"]["ord-1"]["session_id"], "session_A123")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(suite.main([*argv, "--ref", "not-current"]), 2)
            inside = self.repo / "result"
            index = argv.index("--out-dir") + 1
            changed = argv.copy()
            changed[index] = str(inside)
            self.assertEqual(suite.main(changed), 2)
            (self.repo / "new").write_text("unpushed")
            self.git("add", "new")
            self.git("commit", "-m", "unpushed")
            self.assertEqual(suite.main(argv), 2)


if __name__ == "__main__":
    unittest.main()
