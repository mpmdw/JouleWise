"""Offline prepare composition and refusal boundaries; no live arm evidence."""
import contextlib
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise import evidence_night as entry

ROOT = Path(__file__).resolve().parents[1]


class ArgumentsTests(unittest.TestCase):
    def test_t0_and_head_matrix(self):
        now = 1800000001
        self.assertEqual(entry.parse_t0("next", now), 1800002460)
        self.assertEqual(entry.parse_t0("1800000060", now), 1800000060)
        for value in ("__T0__", "tomorrow", "1.5", "-60", "1800000061", "1800000000"):
            with self.subTest(value=value), self.assertRaises(entry.Refused):
                entry.parse_t0(value, now)
        for value in ("main", "abcd1234", "g" * 40, "a" * 41, "__H__"):
            with self.subTest(value=value), self.assertRaisesRegex(entry.Refused, "full SHA"):
                entry.parse_head(value)
        self.assertEqual(entry.parse_head("A" * 40), "a" * 40)

    @unittest.skipUnless(hasattr(time, "tzset"), "local timezone support")
    def test_repeated_local_minute_and_next_skip(self):
        previous = os.environ.get("TZ")
        try:
            os.environ["TZ"] = "America/Los_Angeles"
            time.tzset()
            ambiguous = int(datetime(2030, 11, 3, 1, 30).timestamp())
            with self.assertRaisesRegex(entry.Refused, "ambiguous"):
                entry.parse_t0(str(ambiguous), ambiguous - 3600)
            chosen = entry.parse_t0("next", ambiguous - 2400)
            self.assertTrue(entry.unambiguous(chosen))
            self.assertGreater(chosen, ambiguous)
        finally:
            if previous is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = previous
            time.tzset()

    def test_cli_refusals_are_one_line_exit_two(self):
        for args in ([], ["prepare"], ["prepare", "--kind", "wrong", "--t0", "next"],
                     ["prepare", "--kind", entry.KIND, "--t0", "12"],
                     ["prepare", "--kind", entry.KIND, "--t0", "next", "--head", "main"]):
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(entry.main(args), 2)
            self.assertEqual(len(errors.getvalue().splitlines()), 1)
            self.assertTrue(errors.getvalue().startswith("REFUSED:"))

    def test_checkout_location_is_fenced(self):
        with self.assertRaisesRegex(entry.Refused, "fenced checkout"):
            entry.prepare(kind=entry.KIND, t0="next", head="a" * 40,
                          roots_under=ROOT, staging_under=ROOT / "staging")

    def test_real_lock_verifier_and_builder_recipe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "env").mkdir()
            (root / "env/mac-measurement-lock.txt").write_text("# lock\na==1\nb==2\n")
            with patch.object(entry, "run", return_value="b==2\na==1"):
                entry.verify_lock(root)
            with patch.object(entry, "run", return_value="a==1"):
                with self.assertRaisesRegex(entry.Refused, "lock mismatch"):
                    entry.verify_lock(root)
            with patch.object(entry, "run", return_value="" ) as run, patch.object(entry, "verify_lock") as verify:
                entry.build_venv(root)
            self.assertEqual(run.call_args_list[0].args[0], ["python3.13", "-m", "venv", ".venv"])
            self.assertIn(".[mac]", run.call_args_list[1].args[0])
            self.assertEqual(run.call_args_list[2].args[0][-3:], ["charset-normalizer", "requests", "urllib3"])
            verify.assert_called_once_with(root)


@unittest.skipUnless(Path('/bin/zsh').is_file(), 'real installer requires zsh')
class PrepareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="night-entry-", dir="/tmp")
        while any(token in cls.temp.name.lower() for token in ("codex", "claude", "t3")):
            cls.temp.cleanup()
            cls.temp = tempfile.TemporaryDirectory(prefix="night-entry-", dir="/tmp")
        cls.base = Path(cls.temp.name).resolve()
        cls.remote = cls.base / "remote.git"
        subprocess.run(["git", "clone", "--bare", "-q", "--no-hardlinks", str(ROOT), str(cls.remote)], check=True)
        cls.head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "--git-dir", str(cls.remote), "update-ref", "refs/heads/main", cls.head], check=True)
        cls.bin = cls.base / "bin"
        cls.bin.mkdir()
        courier = cls.bin / "claude"
        courier.write_text("#!/bin/sh\necho 'courier must not run' >&2\nexit 99\n")
        courier.chmod(0o755)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="case-", dir=self.base)
        self.addCleanup(self.tempdir.cleanup)
        self.base_dir = Path(self.tempdir.name)
        self.env = patch.dict(os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", "")})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.t0 = (int(time.time()) // 60 + 90) * 60
        self.kw = dict(kind=entry.KIND, t0=str(self.t0), head=self.head, remote=str(self.remote),
                       roots_under=self.base_dir / "roots", staging_under=self.base_dir / "staging",
                       builder=self.fake_builder, lock_verifier=lambda root: None)

    @staticmethod
    def fake_builder(root):
        (root / ".venv/bin").mkdir(parents=True)
        (root / ".venv/bin/python").symlink_to(sys.executable)

    def test_real_composition_idempotence_and_never_invokes(self):
        calls = []
        original = subprocess.run
        def spy(argv, **kwargs):
            calls.append(list(map(str, argv)))
            self.assertFalse(any(Path(str(arg)).name in ("launchctl", "mail", "sendmail", "claude", "chain.zsh", "powermetrics") for arg in argv))
            return original(argv, **kwargs)
        with patch.object(subprocess, "run", side_effect=spy):
            first = entry.prepare(**self.kw)
            state_path = Path(first["staging"]) / "prepare.json"
            files = [Path(p) for p in first["digests"]] + [state_path]
            before = {p: (entry.digest(p), p.stat().st_mtime_ns) for p in files}
            authored = json.loads(Path(first["plan_path"]).read_text())["authored_epoch_s"]
            second = entry.prepare(**self.kw)
        self.assertEqual(first, second)
        self.assertEqual(before, {p: (entry.digest(p), p.stat().st_mtime_ns) for p in files})
        self.assertEqual(authored, json.loads(Path(first["plan_path"]).read_text())["authored_epoch_s"])
        self.assertFalse((Path(first["custody_root"]) / "night_plan.json").exists())
        self.assertEqual(len(list((Path(first["staging"]) / "render").glob("*.plist"))), 3)
        self.assertTrue(any("scripts/gen_evidence_night.py" in c and "--render-only" in c for c in calls))
        self.assertTrue(any(c[0].endswith("/scripts/install_night_agent.sh") and "--render-only" in c for c in calls))
        self.assertIn("DRAFT — NOT SENT", first["notice_draft"])
        self.assertEqual(first["frozen_triple"], [first["plan_id"], first["measurement_root"], self.head])
        plan = json.loads(Path(first["plan_path"]).read_text())
        self.assertEqual(plan["schema"], "joulewise.night_plan.v2")
        self.assertNotIn("pack_night", plan)
        self.assertNotIn("quiet_admission", plan)
        # Every sealed output, including both sidecars and renderer output, refuses drift.
        for path in files[:-1]:
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            with self.subTest(path=path), self.assertRaisesRegex(entry.Refused, "sealed-byte drift|dirty clone"):
                entry.prepare(**self.kw)
            path.write_bytes(raw)
        (Path(first["custody_root"]) / "night_plan.json").write_bytes(Path(first["plan_path"]).read_bytes())
        with self.assertRaisesRegex(entry.Refused, "published, invoked"):
            entry.prepare(**self.kw)

    def test_default_selection_is_pinned_across_resume(self):
        self.kw.update(t0="next", head=None)
        first = entry.prepare(**self.kw)
        original = entry.run
        def no_resolution(argv, **kwargs):
            self.assertNotIn("ls-remote", argv)
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=no_resolution):
            self.assertEqual(first, entry.prepare(**self.kw))

    def test_same_day_distinct_roots_and_staging(self):
        first = entry.prepare(**self.kw)
        self.kw["t0"] = str(self.t0 + 60)
        second = entry.prepare(**self.kw)
        self.assertEqual(first["plan_id"], second["plan_id"])
        for key in ("staging", "measurement_root", "custody_root"):
            self.assertNotEqual(first[key], second[key])
        self.kw.update(t0="next", head=None)
        with self.assertRaisesRegex(entry.Refused, "ambiguous prior"):
            entry.prepare(**self.kw)

    def test_checkpoint_resume_and_foreign_partial_refusal(self):
        def interrupted(root):
            raise entry.Refused("injected interruption before venv")
        self.kw["builder"] = interrupted
        with self.assertRaisesRegex(entry.Refused, "injected interruption"):
            entry.prepare(**self.kw)
        self.kw["builder"] = self.fake_builder
        state = entry.prepare(**self.kw)
        self.assertEqual([v["step"] for v in state["steps"]], list(entry.STEPS))
        # An unknown existing root cannot be adopted even when its contents look empty.
        self.kw["t0"] = str(self.t0 + 120)
        paths = entry.locations(Path(self.kw["roots_under"]), Path(self.kw["staging_under"]), self.t0 + 120, self.head)
        Path(paths["measurement_root"]).mkdir()
        with self.assertRaisesRegex(entry.Refused, "existing foreign"):
            entry.prepare(**self.kw)

    def test_dirty_clone_interpreter_drift_and_unknown_remote_head(self):
        state = entry.prepare(**self.kw)
        root = Path(state["measurement_root"])
        (root / "untracked.txt").write_text("foreign")
        with self.assertRaisesRegex(entry.Refused, "dirty clone"):
            entry.prepare(**self.kw)
        (root / "untracked.txt").unlink()
        with patch.object(entry, "interpreter", return_value={}):
            with self.assertRaisesRegex(entry.Refused, "interpreter identity drift"):
                entry.prepare(**self.kw)
        self.kw.update(head="0" * 40, t0=str(self.t0 + 60))
        with self.assertRaisesRegex(entry.Refused, "git failed"):
            entry.prepare(**self.kw)

    def test_sealed_plan_survives_interrupted_generator(self):
        original = entry.run
        def interrupt(argv, **kwargs):
            if "scripts/gen_evidence_night.py" in argv:
                raise entry.Refused("interrupted before generator")
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=interrupt):
            with self.assertRaisesRegex(entry.Refused, "interrupted before generator"):
                entry.prepare(**self.kw)
        plan = next(Path(self.kw["staging_under"]).glob("*/night_plan.json"))
        before = (plan.read_bytes(), plan.stat().st_mtime_ns)
        state = entry.prepare(**self.kw)
        self.assertEqual(before, (plan.read_bytes(), plan.stat().st_mtime_ns))
        # Staging additions and unrecorded partial renderer output are not adopted.
        foreign = Path(state["staging"]) / "foreign"
        foreign.touch()
        with self.assertRaisesRegex(entry.Refused, "staging output"):
            entry.prepare(**self.kw)
        foreign.unlink()
        foreign = Path(state["staging"]) / "render/foreign.plist"
        foreign.touch()
        with self.assertRaisesRegex(entry.Refused, "render output"):
            entry.prepare(**self.kw)

    def test_foreign_staging_and_symlink_refusal(self):
        paths = entry.locations(Path(self.kw["roots_under"]), Path(self.kw["staging_under"]), self.t0, self.head)
        stage = Path(paths["staging"])
        stage.mkdir(parents=True)
        with self.assertRaisesRegex(entry.Refused, "existing foreign"):
            entry.prepare(**self.kw)
        stage.rmdir()
        stage.symlink_to(self.base_dir, target_is_directory=True)
        with self.assertRaisesRegex(entry.Refused, "symlink"):
            entry.prepare(**self.kw)


if __name__ == "__main__":
    unittest.main()
