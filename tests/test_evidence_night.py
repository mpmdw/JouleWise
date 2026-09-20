"""Offline prepare composition and refusal boundaries; no live arm evidence."""
import contextlib
import fcntl
from datetime import datetime, timezone
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

# The generator refuses any path carrying a census substring ("codex", "claude",
# "t3"); a random tempfile suffix can contain "t3" (seen once: case-qa4uqbt3),
# so every fixture directory is re-drawn until its name is census-clean.
try:  # the generator's own guard list is the source of truth
    from scripts.gen_derivation_night import CENSUS_SUBSTRINGS as _CENSUS_SUBSTRINGS
except ImportError:  # pragma: no cover - defensive fallback for a moved module
    _CENSUS_SUBSTRINGS = ("codex", "claude", "t3")


def _census_clean_tempdir(**kwargs):
    for _ in range(64):
        candidate = tempfile.TemporaryDirectory(**kwargs)
        if not any(s in candidate.name.lower() for s in _CENSUS_SUBSTRINGS):
            return candidate
        candidate.cleanup()
    raise RuntimeError("could not draw a census-clean temporary directory name")


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
        with _census_clean_tempdir(prefix="recipe-", dir="/tmp") as tmp:
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
            self.assertEqual(run.call_args_list[1].args[0][-4:], ["-c", "env/mac-measurement-lock.txt", "-e", ".[mac]"])
            self.assertEqual(run.call_args_list[2].args[0][-3:], ["charset-normalizer", "requests", "urllib3"])
            verify.assert_called_once_with(root)


@unittest.skipUnless(Path('/bin/zsh').is_file(), 'real installer requires zsh')
class PrepareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = _census_clean_tempdir(prefix="night-entry-", dir="/tmp")
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
        self.tempdir = _census_clean_tempdir(prefix="case-", dir=self.base)
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

    def test_cross_device_refused_before_clone(self):
        original = Path.stat
        custody_parent = Path(self.kw["roots_under"]) / "night-custody"
        def different_device(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == custody_parent:
                values = list(result); values[2] += 1
                return os.stat_result(values)
            return result
        calls = []
        original_run = entry.run
        def spy(argv, **kwargs):
            calls.append(argv)
            return original_run(argv, **kwargs)
        with patch.object(Path, "stat", different_device), patch.object(entry, "run", side_effect=spy):
            with self.assertRaisesRegex(entry.Refused, "staging and custody are not on one filesystem"):
                entry.prepare(**self.kw)
        self.assertFalse(any("clone" in argv for argv in calls))

    def test_t0_beyond_max_age_refused_before_clone(self):
        self.kw["t0"] = str(self.t0 + 130020)
        now = int(self.kw["t0"]) - 130000
        calls = []
        original = entry.run
        def spy(argv, **kwargs):
            calls.append(argv)
            return original(argv, **kwargs)
        with patch.object(entry.time, "time", return_value=now), patch.object(entry, "run", side_effect=spy):
            with self.assertRaisesRegex(entry.Refused, "^t0 is beyond the plan's maximum age at authoring$"):
                entry.prepare(**self.kw)
        self.assertFalse(any("clone" in argv for argv in calls))
        self.assertFalse(list(Path(self.kw["roots_under"]).glob("JouleWise-measurement-*")))

    def test_clone_authoring_max_age_binds_before_plan_write(self):
        original = entry.run
        authoring_calls = []
        def tighter_clone_limit(argv, **kwargs):
            if "-c" in argv and "write_night_plan" in str(argv[argv.index("-c") + 1]):
                authoring_calls.append((list(argv), kwargs))
                argv = list(argv)
                index = argv.index("-c") + 1
                argv[index] = ("from joulewise import night_gate; night_gate.PLAN_MAX_AGE_S=1\n"
                               + argv[index])
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=tighter_clone_limit):
            with self.assertRaisesRegex(entry.Refused, "^t0 is beyond the plan's maximum age at authoring$"):
                entry.prepare(**self.kw)
        self.assertEqual(len(authoring_calls), 1)
        argv, kwargs = authoring_calls[0]
        root = Path(kwargs["cwd"])
        self.assertEqual(argv[:3], [root / ".venv/bin/python", "-B", "-c"])
        record = json.loads(next(Path(self.kw["staging_under"]).glob("*/prepare.json")).read_text())
        self.assertEqual([s["step"] for s in record["steps"]], ["clone", "venv"])
        self.assertFalse(Path(record["plan_path"]).exists())
        self.assertFalse(Path(record["custody_root"]).exists())

    def test_orphan_next_refused_before_resolution(self):
        self.kw.update(t0="next", head=None)
        first = entry.prepare(**self.kw)
        (Path(first["staging"]) / "prepare.json").unlink()
        with patch.object(entry, "run") as run:
            with self.assertRaisesRegex(entry.Refused, "unidentified prior preparation output: " + first["staging"]):
                entry.prepare(**self.kw)
        run.assert_not_called()

    def test_orphan_custody_refused(self):
        orphan = Path(self.kw["roots_under"]) / "night-custody/qpe01-pilot-n1-orphan"
        orphan.mkdir(parents=True)
        with self.assertRaisesRegex(entry.Refused, "unidentified prior preparation output: " + str(orphan)):
            entry.prepare(**self.kw)

    def corrupt_candidate(self, state, mode):
        custody = Path(state["custody_root"])
        wrapper = custody / "chain.zsh"
        if mode == "manifest":
            path = custody / "evidence_manifest.json"
            value = json.loads(path.read_text()); value["plan_id"] = "flipped"
            path.write_text(json.dumps(value))
        else:
            raw = wrapper.read_text()
            if mode == "zsh -n":
                raw += ")\n"
            else:
                raw = raw.replace(str(custody / "night_plan.json"), state["plan_path"])
            wrapper.write_text(raw)
            (custody / "chain.zsh.sha256").write_text(entry.digest(wrapper) + "  chain.zsh\n")

    def test_sealed_candidate_checks_before_checkpoint(self):
        original = entry.run
        for mode in ("zsh -n", "manifest", "published plan path"):
            with self.subTest(check=mode):
                self.kw["t0"] = str(int(self.kw["t0"]) + 60)
                def corrupt(argv, **kwargs):
                    result = original(argv, **kwargs)
                    if "scripts/gen_evidence_night.py" in argv:
                        plan = Path(argv[argv.index("--plan") + 1])
                        state = json.loads((plan.parent / "prepare.json").read_text())
                        self.corrupt_candidate(state, mode)
                    return result
                with patch.object(entry, "run", side_effect=corrupt):
                    with self.assertRaisesRegex(entry.Refused, "sealed candidate failed " + mode):
                        entry.prepare(**self.kw)

    def test_sealed_candidate_checks_on_resume(self):
        state = entry.prepare(**self.kw)
        for mode in ("zsh -n", "manifest", "published plan path"):
            with self.subTest(check=mode):
                originals = {p: Path(p).read_bytes() for p in state["digests"]}
                self.corrupt_candidate(state, mode)
                record = dict(state, digests={p: entry.digest(p) for p in state["digests"]})
                state_path = Path(state["staging"]) / "prepare.json"
                state_path.write_text(json.dumps(record))
                with self.assertRaisesRegex(entry.Refused, "sealed candidate failed " + mode):
                    entry.prepare(**self.kw)
                for path, raw in originals.items():
                    Path(path).write_bytes(raw)
                state_path.write_text(json.dumps(state))

    def test_lock_precedes_first_staging_write(self):
        paths = entry.locations(Path(self.kw["roots_under"]), Path(self.kw["staging_under"]), self.t0, self.head)
        stage = Path(paths["staging"])
        locks = stage.parent / ".locks"; locks.mkdir(parents=True)
        with (locks / (stage.name + ".lock")).open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(entry.Refused, "concurrent preparation"):
                entry.prepare(**self.kw)
            self.assertFalse(stage.exists())

    def test_notice_bindings_and_spans(self):
        from joulewise.quiet_predicate_campaign import CHAIN_PATH, PROTOCOL_PATH
        state = entry.prepare(**self.kw); draft = state["notice_draft"]
        root = Path(state["measurement_root"])
        for relative in (CHAIN_PATH, PROTOCOL_PATH):
            self.assertIn(str(root / relative), draft)
            self.assertIn(entry.digest(root / relative), draft)
        for index, (start, end) in enumerate(state["schedule"]["install_spans_today"], 1):
            for boundary, epoch in (("open", start), ("close EXCLUDED", end)):
                self.assertIn(f"install span {index} {boundary}: "
                              f"{datetime.fromtimestamp(epoch).astimezone().isoformat()} "
                              f"{datetime.fromtimestamp(epoch, timezone.utc).isoformat()} epoch {epoch}", draft)
        self.assertIn("attempt 1; prior candidates for this date: none", draft)
        self.assertNotIn("earlier abort", draft)

    def test_preclone_recipe_and_runway_warning(self):
        self.kw["t0"] = str((int(time.time()) // 60 + 30) * 60)
        calls = []; original = entry.run; errors = io.StringIO()
        def spy(argv, **kwargs):
            calls.append(list(map(str, argv)))
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=spy), contextlib.redirect_stderr(errors):
            entry.prepare(**self.kw)
        self.assertIn("WARNING: runway below the 40-minute planning default", errors.getvalue())
        version = calls.index(["python3.13", "--version"])
        clone = next(i for i, c in enumerate(calls) if "clone" in c)
        fetch = next(i for i, c in enumerate(calls) if "fetch" in c)
        ancestry = next(i for i, c in enumerate(calls) if "merge-base" in c)
        self.assertLess(version, clone); self.assertLess(fetch, ancestry)
        self.assertTrue(any("interpreter_identity" in " ".join(c) for c in calls))

    def test_unexpected_builder_is_error_exit_one(self):
        original = entry.prepare
        def broken(root):
            raise RuntimeError("unexpected builder defect")
        self.kw["builder"] = broken
        errors = io.StringIO()
        with patch.object(entry, "prepare", side_effect=lambda **kwargs: original(**self.kw)):
            with contextlib.redirect_stderr(errors):
                result = entry.main(["prepare", "--kind", entry.KIND, "--t0", "next"])
        self.assertEqual(result, 1)
        self.assertIn("ERROR: RuntimeError: unexpected builder defect", errors.getvalue())
        self.assertIn("Traceback (most recent call last)", errors.getvalue())


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
        from joulewise.night_agent_install import probe_label
        from joulewise.night_gate import NightPlan
        self.assertNotEqual(first["plan_id"], second["plan_id"])
        self.assertNotEqual("night-results/" + first["plan_id"], "night-results/" + second["plan_id"])
        self.assertNotEqual(probe_label(first["plan_id"]), probe_label(second["plan_id"]))
        for state in (first, second):
            self.assertEqual(state["plan_id"], "qpe01-pilot-n1-" + datetime.fromtimestamp(state["t0"]).strftime("%Y%m%d-%H%M"))
            NightPlan.from_mapping(json.loads(Path(state["plan_path"]).read_text()))
        self.assertIn("attempt 2", second["notice_draft"])
        self.assertIn(first["plan_id"], second["notice_draft"])
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
        with self.assertRaisesRegex(entry.Refused, "unidentified prior preparation output"):
            entry.prepare(**self.kw)
        stage.rmdir()
        stage.symlink_to(self.base_dir, target_is_directory=True)
        with self.assertRaisesRegex(entry.Refused, "symlink"):
            entry.prepare(**self.kw)


if __name__ == "__main__":
    unittest.main()
