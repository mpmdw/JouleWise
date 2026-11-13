"""B-2, the Block 6 real-run launcher, on a synthetic checkout with a stub program. No custody, no pinned program.

No test signals a process: the stop test replaces the launcher's one signalling function with a recorder, and the
stub exits on its own.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import b6_real_run as rr  # noqa: E402

STUB = r'''
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
mode = args[args.index("--stub-mode") + 1]
def opt(name):
    return args[args.index(name) + 1]
def write_outputs():
    Path(opt("--restricted-out")).write_text('{"r": 1}\n')
    Path(opt("--public-out")).write_text('{"p": 1}\n')
if mode == "ok":
    write_outputs()
    print("recompute sessions=1 flags=0 comparison_stopped=false restricted_sha256=" + "ab" * 32)
    print("tmpdir=" + os.environ.get("TMPDIR", ""), file=sys.stderr)
    print("env=" + ",".join(sorted(os.environ)), file=sys.stderr)
    sys.exit(0)
if mode == "ok_bad_line":
    print("recompute sessions=1 value=12.5")
    sys.exit(0)
if mode == "hold":
    write_outputs()
    print("recompute sessions=1 flags=2 comparison_stopped=true restricted_sha256=" + "cd" * 32)
    sys.exit(3)
if mode.startswith("refuse:"):
    print("refused: " + mode.split(":", 1)[1], file=sys.stderr)
    sys.exit(4)
if mode == "refuse_value":
    print("refused: value 12.5 is out of range!", file=sys.stderr)
    sys.exit(4)
if mode == "traceback":
    def read_value():
        raise ValueError("12.5")
    read_value()
if mode == "traceback_multiline":
    raise KeyError("first line\nsecret 12.5\nNameError")
if mode == "usage":
    print("usage: independent_recompute_b6.py ...", file=sys.stderr)
    sys.exit(2)
if mode == "sleep":
    time.sleep(float(opt("--stub-seconds")))
    sys.exit(0)
if mode == "abort":
    os.abort()
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-real-run-", dir=os.environ.get("TMPDIR")))
        self.checkout = self.tmp / "checkout"
        (self.checkout / "scripts").mkdir(parents=True)
        (self.checkout / "configs").mkdir()
        (self.checkout / rr.PROGRAM).write_text(STUB)
        (self.checkout / "configs/table.json").write_text("{}\n")
        git(self.checkout, "init", "-q")
        git(self.checkout, "add", "-A")
        git(self.checkout, "commit", "-q", "-m", "fixture")
        self.commit = subprocess.run(["git", "-C", str(self.checkout), "rev-parse", "HEAD"], capture_output=True,
                                     text=True, check=True).stdout.strip()
        self.table = {rr.PROGRAM: sha(self.checkout / rr.PROGRAM),
                      "configs/table.json": sha(self.checkout / "configs/table.json")}
        self.run_root = self.tmp / "run"
        self.run_root.mkdir(mode=0o700)
        os.chmod(self.run_root, 0o700)
        patch = mock.patch.object(rr, "PIN_TABLE", self.table)
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def launch(self, mode, stem="dry", limit=60.0, extra=(), out=None, sessions=None):
        out = self.run_root / stem if out is None else out
        sessions = [str(self.tmp / "custody/r1-alpha/archive")] if sessions is None else sessions
        program = ["block", *[x for s in sessions for x in ("--session", s)], "--stub-mode", mode, *extra,
                   "--restricted-out", str(out / "restricted.json"), "--public-out", str(out / "public.json")]
        argv = ["--checkout", str(self.checkout), "--expect-commit", self.commit, "--stem", stem,
                "--limit-s", str(limit), "--out-dir", str(out), "--", *program]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            rc = rr.main(argv)
        return rc, buffer.getvalue().splitlines(), out

    def ledger(self):
        return [json.loads(line) for line in (self.run_root / "attempts.jsonl").read_text().splitlines()]

    def record(self, out):
        return json.loads((out / "record.json").read_text())

    # ------------------------------------------------------------ exit map

    def test_exit_0_prints_complete_and_the_stdout_line(self):
        rc, lines, out = self.launch("ok")
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ["complete", "recompute sessions=1 flags=0 comparison_stopped=false restricted_sha256="
                                 + "ab" * 32])
        record = self.record(out)
        self.assertEqual((record["exit_code"], record["status"]), (0, "complete"))
        self.assertEqual(set(record["outputs_sha256"]), {"stdout", "stderr", "restricted", "public"})
        self.assertEqual(record["outputs_sha256"]["restricted"], sha(out / "restricted.json"))
        self.assertTrue(record["closure_unchanged"])
        self.assertIsInstance(record["time_wrapper_exit"], int)
        self.assertIsNotNone(record["peak_rss"])
        self.assertEqual(record["argv"][:3], [sys.executable, "-B", str(self.checkout.resolve() / rr.PROGRAM)])

    def test_files_are_private_tmpdir_is_inside_and_removed_environment_is_fixed(self):
        rc, _, out = self.launch("ok")
        self.assertEqual(rc, 0)
        self.assertEqual(out.stat().st_mode & 0o777, 0o700)
        for name in ("stdout", "stderr", "record.json", "restricted.json", "public.json", "time"):
            self.assertEqual((out / name).stat().st_mode & 0o777, 0o600, name)
        self.assertEqual((self.run_root / "attempts.jsonl").stat().st_mode & 0o777, 0o600)
        stderr = (out / "stderr").read_text()
        self.assertIn("tmpdir=" + str(out / "analysis-tmp"), stderr)
        self.assertFalse((out / "analysis-tmp").exists())
        env = set(next(line for line in stderr.splitlines() if line.startswith("env=")).split("=", 1)[1].split(","))
        self.assertLessEqual({"PATH", "PYTHONNOUSERSITE", "PYTHONDONTWRITEBYTECODE", "TMPDIR"}, env)
        self.assertFalse(env & {"PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME", "JW_B5_SYNTHETIC_ONLY"})

    def test_exit_0_with_an_unexpected_stdout_line_is_not_relayed(self):
        rc, lines, _ = self.launch("ok_bad_line")
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ["complete", "stdout line not in the expected form"])
        self.assertNotIn("12.5", "\n".join(lines))

    def test_exit_3_is_a_hold(self):
        rc, lines, out = self.launch("hold")
        self.assertEqual((rc, lines), (3, ["hold: comparison_stopped"]))
        self.assertIn("restricted", self.record(out)["outputs_sha256"])

    def test_exit_4_prints_the_refusal_with_its_class(self):
        for code, cls in (("session_input_unsupplied", "A"), ("registration_digest_mismatch", "B"),
                          ("input_digest_mismatch", "C"), ("comparison_session_coverage_mismatch", "E"),
                          ("KeyError", "E"), ("TypeError", "C/E"), ("never_heard_of_it", "E")):
            with self.subTest(code=code):
                rc, lines, out = self.launch("refuse:" + code, stem="r-" + code)
                self.assertEqual((rc, lines), (4, ["refused: " + code + " class=" + cls]))
                self.assertEqual((self.record(out)["code"], self.record(out)["class"]), (code, cls))

    def test_exit_4_synthetic_only_sentence_is_class_a(self):
        rc, lines, _ = self.launch("refuse:" + rr.SYNTHETIC_REFUSAL)
        self.assertEqual(lines, ["refused: " + rr.SYNTHETIC_REFUSAL + " class=A"])

    def test_exit_4_line_outside_the_refusal_form_is_not_copied(self):
        rc, lines, _ = self.launch("refuse_value")
        self.assertEqual((rc, lines), (4, ["refused: unparsed class=E"]))

    def test_traceback_prints_frames_and_type_never_the_message(self):
        rc, lines, out = self.launch("traceback")
        self.assertEqual(rc, 1)
        self.assertEqual(lines[0], "refused: traceback class=E")
        self.assertEqual(lines[-1], "ValueError")
        self.assertTrue(all(line.startswith('  File "') for line in lines[1:-1]), lines)
        self.assertTrue(any(line.endswith("in read_value") for line in lines), lines)
        self.assertNotIn("12.5", "\n".join(lines))
        self.assertNotIn("12.5", json.dumps(self.record(out)))

    def test_traceback_with_a_multiline_message_prints_only_the_type(self):
        rc, lines, out = self.launch("traceback_multiline")
        self.assertEqual((rc, lines[-1]), (1, "KeyError"))
        text = "\n".join(lines) + json.dumps(self.record(out))
        for secret in ("12.5", "secret", "first line", "NameError"):
            self.assertNotIn(secret, text)

    def test_traceback_classes(self):
        hazards = [{"file": "/w/joulewise/b6_analysis_hazards.py", "line": 58, "function": "desk_hazards"}]
        self.assertEqual(rr.traceback_class(hazards, "AttributeError"), "C")
        self.assertEqual(rr.traceback_class(hazards, "KeyError"), "E")
        self.assertEqual(rr.traceback_class([], "RuntimeError"), "D")
        self.assertEqual(rr.traceback_class([], "ZeroDivisionError"), "E")

    def test_exit_2_is_usage(self):
        rc, lines, _ = self.launch("usage")
        self.assertEqual((rc, lines), (2, ["refused: usage class=A"]))

    def test_a_signal_is_reported_by_number(self):
        rc, lines, out = self.launch("abort")
        self.assertEqual(lines, ["killed: signal " + str(int(signal.SIGABRT))])
        self.assertEqual(rc, 128 + int(signal.SIGABRT))
        self.assertEqual(self.record(out)["class"], "D")

    # ------------------------------------------------------------ the stop

    def test_stop_signals_only_its_own_child_group_and_exits_124(self):
        calls = []

        def recorder(group, sig):
            # Recorded, never sent. The group must be the launcher's own child, leading its own group.
            self.assertNotEqual(group, os.getpgrp())
            self.assertEqual(os.getpgid(group), group)
            calls.append((group, sig))
        with mock.patch.object(rr, "signal_group", recorder), mock.patch.object(rr, "KILL_GRACE_S", 0.3), \
                mock.patch.object(rr, "SAMPLE_S", 0.4):
            rc, lines, out = self.launch("sleep", limit=1.0, extra=("--stub-seconds", "2.5"))
        self.assertEqual((rc, lines), (124, ["stopped_profile_required"]))
        self.assertEqual([s for _, s in calls], [signal.SIGTERM, signal.SIGKILL])
        self.assertEqual(len({g for g, _ in calls}), 1)
        record = self.record(out)
        self.assertEqual((record["exit_code"], record["status"]), (124, "stopped_profile_required"))
        samples = [json.loads(line) for line in (out / "samples.jsonl").read_text().splitlines()]
        self.assertGreaterEqual(len(samples), 1)
        self.assertLessEqual({"elapsed_s", "cpu_s", "rss_kib", "nice", "pri", "open_sessions", "busiest_other"},
                             set(samples[0]))
        self.assertEqual(self.ledger()[-1]["exit_code"], 124)

    def test_sampler_names_the_session_directory_not_files(self):
        archive = self.tmp / "custody/r3-gamma/archive"
        archive.mkdir(parents=True)
        roots = rr.session_roots(["--session", str(archive)])
        self.assertEqual(roots, {str(archive) + "/": "r3-gamma"})
        with open(archive / "harvest.json", "w") as held:
            found = rr.open_sessions([os.getpid()], roots)
            held.write("{}")
        self.assertEqual(found, ["r3-gamma"])

    # ------------------------------------------------------------ before launch

    def test_dirty_checkout_refuses_before_launch_and_is_ledgered(self):
        (self.checkout / "scripts/extra.py").write_text("x = 1\n")
        rc, lines, out = self.launch("ok")
        self.assertEqual((rc, lines), (9, ["launch refused: checkout_dirty"]))
        self.assertFalse(out.exists())
        row = self.ledger()[-1]
        self.assertEqual((row["status"], row["code"], row["exit_code"]), ("launch_refused", "checkout_dirty", 9))

    def test_wrong_hash_refuses_before_launch(self):
        with mock.patch.dict(rr.PIN_TABLE, {"configs/table.json": "0" * 64}):
            rc, lines, out = self.launch("ok")
        self.assertEqual((rc, lines), (9, ["launch refused: closure_hash_mismatch"]))
        self.assertFalse(out.exists())
        self.assertEqual(self.ledger()[-1]["code"], "closure_hash_mismatch")

    def test_other_preconditions_refuse(self):
        cases = []
        cases.append(("checkout_commit_mismatch", dict(commit="0" * 40)))
        existing = self.run_root / "exists"
        existing.mkdir()
        cases.append(("out_dir_exists", dict(out=existing)))
        loose = self.tmp / "loose"
        loose.mkdir(mode=0o755)
        os.chmod(loose, 0o755)
        cases.append(("out_dir_parent_not_0700", dict(out=loose / "dry")))
        cases.append(("session_path_not_absolute", dict(sessions=["r1-alpha/archive"])))
        for code, kw in cases:
            with self.subTest(code=code):
                commit = self.commit
                if "commit" in kw:
                    self.commit = kw.pop("commit")
                try:
                    rc, lines, _ = self.launch("ok", stem="p-" + code, **kw)
                finally:
                    self.commit = commit
                self.assertEqual((rc, lines), (9, ["launch refused: " + code]))

    def test_outputs_outside_the_out_dir_refuse(self):
        out = self.run_root / "dry"
        argv = ["--checkout", str(self.checkout), "--expect-commit", self.commit, "--stem", "dry", "--limit-s", "60",
                "--out-dir", str(out), "--", "block", "--session", "/abs/r1-alpha/archive", "--stub-mode", "ok",
                "--restricted-out", str(self.tmp / "restricted.json"), "--public-out", str(out / "public.json")]
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = rr.main(argv)
        self.assertEqual((rc, buffer.getvalue().strip()), (9, "launch refused: output_outside_out_dir"))

    def test_synthetic_only_variable_refuses(self):
        with mock.patch.dict(os.environ, {"JW_B5_SYNTHETIC_ONLY": "1"}):
            rc, lines, _ = self.launch("ok")
        self.assertEqual((rc, lines), (9, ["launch refused: synthetic_only_set"]))

    def test_every_attempt_is_ledgered(self):
        self.launch("refuse:session_input_unsupplied", stem="gate")
        self.launch("ok", stem="gate-2")
        rows = self.ledger()
        self.assertEqual([r["stem"] for r in rows], ["gate", "gate-2"])
        self.assertEqual([r["exit_code"] for r in rows], [4, 0])
        self.assertEqual(rows[0]["code"], "session_input_unsupplied")
        self.assertEqual(rows[1]["outputs_sha256"]["public"], sha(self.run_root / "gate-2/public.json"))
        self.assertTrue(all(len(r["argv_sha256"]) == 64 for r in rows))


class EmbeddedTable(unittest.TestCase):
    def test_twenty_four_rows_and_the_three_changed_program_rows(self):
        self.assertEqual(len(rr.PIN_TABLE), 24)
        self.assertEqual(rr.PIN_TABLE["scripts/independent_recompute_b6.py"][:8], "90e22603")
        self.assertEqual(rr.PIN_TABLE["joulewise/b6_analysis_check.py"][:8], "634c991c")
        self.assertEqual(rr.PIN_TABLE["joulewise/b6_analysis_inputs.py"][:8], "283dfc78")

    def test_table_equals_this_checkout_when_it_is_the_pin_line(self):
        # On the S-14 line (this branch is cut from it) the 24 files are unchanged.
        self.assertEqual(rr.closure_hashes(ROOT), rr.PIN_TABLE)


if __name__ == "__main__":
    unittest.main()
