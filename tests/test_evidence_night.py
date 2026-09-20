"""Offline prepare composition and refusal boundaries; no live arm evidence."""
import contextlib
import fcntl
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
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


class LifecycleTests(unittest.TestCase):
    """Real fixture Git/reflog and sealed bytes; no host process observation."""

    def setUp(self):
        from tests.git_fixture import init_git_fixture
        from tests.test_arm_census import observation, row
        temporary = _census_clean_tempdir(prefix="lifecycle-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.canonical = self.base / "canonical"
        self.canonical.mkdir()
        init_git_fixture(self.canonical, "-q")
        (self.canonical / ".gitignore").write_text(".venv/\n")
        (self.canonical / "env").mkdir()
        (self.canonical / "env/mac-measurement-lock.txt").write_text("fixture==1\n")
        self.arrival = int(time.time()) - 1000
        self.old = self.commit("old", self.arrival - 100)
        self.head = self.commit("fix", self.arrival)
        self.tip = self.commit("later", self.arrival + 100)
        self.t0 = (int(time.time()) // 60 + 90) * 60
        paths = entry.locations(self.base / "roots", self.base / "staging", self.t0, self.head)
        self.stage = Path(paths["staging"])
        self.custody = Path(paths["custody_root"])
        self.root = Path(paths["measurement_root"])
        self.root.parent.mkdir(parents=True)
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(self.canonical), str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "checkout", "-q", "--detach", self.head], check=True)
        self.stage.mkdir(parents=True)
        self.custody.mkdir(parents=True)
        (self.stage / "render").mkdir()
        self.plan = self.stage / "night_plan.json"
        self.plan.write_text(json.dumps(dict(plan_id=paths["plan_id"], repo_head=self.head,
            measurement_head=self.head, measurement_root=str(self.root), custody_root=str(self.custody),
            t0_epoch_s=self.t0)))
        files = [self.plan, self.root / "env/mac-measurement-lock.txt"]
        for name in ("chain.zsh", "chain.zsh.sha256", "chain.zsh.chain-source.sha256", "evidence_manifest.json"):
            path = self.custody / name
            path.write_text("sealed " + name)
            files.append(path)
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            path = self.stage / "render" / (label + ".plist")
            path.write_text("rendered fixture")
            files.append(path)
        self.state = dict(schema=entry.SCHEMA, kind=entry.KIND, head=self.head, t0=self.t0,
            roots_under=str(self.base / "roots"), **paths, plan_path=str(self.plan),
            interpreter={"fixture": True}, steps=[dict(step=s) for s in entry.STEPS],
            digests={str(p): entry.digest(p) for p in files})
        entry.saved_json(self.stage / "prepare.json", self.state)
        self.resident = self.base / "state.json"
        entry.saved_json(self.resident, {"resident_session": None})
        self.fixture = observation(row(20, 1, "/bin/claude"), row(90, 20, "/bin/python3"), hits=(20,))
        self.courier = self.base / "bin/claude"
        self.courier.parent.mkdir()
        self.courier.write_text("#!/bin/sh\nexit 99\n")
        self.courier.chmod(0o755)
        self.calls = []
        self.ps = subprocess.CompletedProcess([], 1, "", "")
        self.raw = subprocess.CompletedProcess([], 1, "", "")
        self.kw = dict(candidate=self.stage, canonical=self.canonical, supervisor_state=self.resident,
                       runner=self.runner, caller_pid=90, census_observer=lambda **kw: self.fixture,
                       lock_verifier=lambda root: None)
        self.schedule = dict(install_close_epoch_s=self.t0 - 1800,
                             boundaries={"REQUEST / exit BEFORE": self.t0 - 900})
        for p in (patch.object(entry, "CENSUS_FIX", self.head),
                  patch.object(entry, "interpreter", return_value=self.state["interpreter"]),
                  patch.object(entry, "sealed_candidate", return_value={}),
                  patch.object(entry, "clone_schedule", return_value=self.schedule),
                  patch.dict(os.environ, {"PATH": str(self.courier.parent) + ":" + os.environ["PATH"]})):
            p.start()
            self.addCleanup(p.stop)

    def commit(self, text, epoch):
        (self.canonical / "tracked").write_text(text)
        subprocess.run(["git", "-C", str(self.canonical), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.canonical), "-c", "user.name=Fixture",
                        "-c", "user.email=fixture@example.invalid", "commit", "-qm", text],
                       env=dict(os.environ, GIT_COMMITTER_DATE=f"{epoch} +0000", GIT_AUTHOR_DATE=f"{epoch} +0000"), check=True)
        return subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "HEAD"], text=True).strip()

    def runner(self, argv, **kwargs):
        self.calls.append(list(map(str, argv)))
        if str(argv[0]) == "ps":
            return self.ps
        if Path(str(argv[0])).name == "pgrep":
            return self.raw
        self.assertEqual(str(argv[0]), "git", "unexpected process: " + repr(argv))
        self.assertNotIn(entry.CANONICAL, list(map(str, argv)))
        return entry.probe_command(argv, **kwargs)

    def checked(self, fail=None):
        if fail:
            with self.assertRaisesRegex(entry.Refused, fail):
                entry.check(**self.kw)
            return json.loads((self.stage / "check.json").read_text())
        return entry.check(**self.kw)

    def test_check_passes_and_writes_only_check_json(self):
        def snapshot():
            return {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.base.rglob("*") if p.is_file()}
        before = snapshot()
        record = self.checked()
        after = snapshot()
        self.assertTrue(record["armable"])
        self.assertEqual(set(after) - set(before), {str(self.stage / "check.json")})
        self.assertEqual(before, {p: after[p] for p in before})
        self.assertEqual(record["checks"]["census"]["argv"][-1], "[c]odex|[c]laude|[t]3")
        self.assertIn(20, record["checks"]["census"]["owned_helpers"])
        self.assertFalse(any("launchctl" in str(c) for c in self.calls))

    def test_sealed_bytes_checked_before_host_probes(self):
        self.plan.write_bytes(self.plan.read_bytes() + b" ")
        record = self.checked("sealed")
        self.assertEqual(list(record["checks"]), ["sealed"])
        self.assertFalse(self.calls)

    def test_canonical_must_contain_h_and_be_clean(self):
        (self.canonical / "tracked").write_text("dirty")
        self.assertFalse(self.checked("canonical")["armable"])
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        self.checked("canonical")
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.tip], check=True)
        (self.canonical / "untracked").write_text("irrelevant")
        self.assertTrue(self.checked()["armable"])
        self.assertTrue(any(c[-4:] == ["--no-optional-locks", "status", "--porcelain", "-uno"] for c in self.calls))

    def test_candidate_must_contain_census_fix(self):
        with patch.object(entry, "CENSUS_FIX", self.tip):
            self.assertIn("census fix", self.checked("canonical")["checks"]["canonical"]["reason"])

    def live_supervisor(self, start, command="python scripts/magistrate_watchdog.py"):
        entry.saved_json(self.resident, {"resident_session": {"supervisor_pid": 42}})
        text = datetime.fromtimestamp(start).strftime("%a %b %d %H:%M:%S %Y")
        self.ps = subprocess.CompletedProcess([], 0, f"42 {text} {command}\n", "")

    def test_supervisor_uses_oldest_continuous_entry_not_latest(self):
        self.live_supervisor(self.arrival + 50)
        result = self.checked()["checks"]["supervisor"]
        self.assertEqual(result["head_arrived_epoch_s"], self.arrival)
        for started in (self.arrival - 1, self.arrival):
            self.live_supervisor(started)
            self.checked("supervisor")

    def test_supervisor_rewind_readd_and_missing_reflog_fail_closed(self):
        for sha, epoch in ((self.old, self.arrival + 200), (self.tip, self.arrival + 300)):
            subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", sha],
                           env=dict(os.environ, GIT_COMMITTER_DATE=f"{epoch} +0000"), check=True)
        self.live_supervisor(self.arrival + 250)
        self.checked("supervisor")
        self.live_supervisor(self.arrival + 350)
        self.assertEqual(self.checked()["checks"]["supervisor"]["head_arrived_epoch_s"], self.arrival + 300)
        for path in (self.canonical / ".git/logs").rglob("*"):
            if path.is_file():
                path.write_text("")
        self.checked("supervisor")

    def test_supervisor_pid_reuse_absence_and_observation_errors(self):
        self.live_supervisor(self.arrival - 100, command="/bin/sleep 10")
        self.assertTrue(self.checked()["armable"])
        self.ps = subprocess.CompletedProcess([], 1, "", "")
        self.assertTrue(self.checked()["armable"])
        self.ps = subprocess.CompletedProcess([], 2, "", "unreadable")
        self.checked("supervisor")
        entry.saved_json(self.resident, {"resident_session": {"supervisor_pid": True}})
        self.checked("supervisor")

    def test_courier_unavailable(self):
        with patch.object(entry.shutil, "which", return_value=None):
            self.checked("courier")

    def test_discovery_retains_every_harvested_root_and_refuses_unknown(self):
        for i, marker in enumerate(("courier.sent", "result.json", None)):
            root = self.custody.parent / f"prior-{i}"
            (root / "night").mkdir(parents=True)
            (root / "night_plan.json").write_text("{}")
            if marker:
                (root / "night" / marker).write_text("{}")
        result = self.checked("retained_roots")["checks"]["retained_roots"]
        self.assertEqual([r["classification"] for r in result["inventory"]], ["retained", "retained", "UNKNOWN"])
        self.assertTrue((root / "night_plan.json").exists())
        (root / "night/result.json").write_text("{}")
        self.assertTrue(self.checked()["armable"])

    def test_census_foreign_workload_and_unknown_refuse(self):
        from dataclasses import replace
        from tests.test_arm_census import observation, row
        self.fixture = observation(row(20, 1, "/bin/claude"), row(90, 1, "/bin/python3"), hits=(20,))
        result = self.checked("census")
        self.assertEqual(result["checks"]["census"]["classification"]["foreign_pids"], [20])
        self.fixture = observation(row(20, 1, "/bin/claude"), row(90, 20, "/bin/python3"),
                                   row(91, 20, "/bin/python3", "-m", "pytest"), hits=(20,))
        self.checked("census")
        self.fixture = replace(self.fixture, records=(), diagnostics=("inventory unknown",))
        self.checked("census")

    def test_raw_census_failure_and_missing_supervisor_state_refuse(self):
        self.raw = subprocess.CompletedProcess([], 3, "", "probe failed")
        self.checked("census")
        self.raw = subprocess.CompletedProcess([], 1, "", "")
        self.resident.unlink()
        self.checked("supervisor")

    def test_retry_routes_exact_causes_and_unknown_stops(self):
        for cause, passing in (("arm_transport", True), ("night_probe_error", False), ("invented", False)):
            entry.saved_json(self.stage / "attempts.json", [{"cause": cause}])
            record = self.checked(None if passing else "retry")
            self.assertEqual(record["checks"]["retry"]["inventory"][0]["route"], "retry" if passing else "cold_gate")

    def publish(self, **kwargs):
        return entry.publish_install(candidate=self.stage, notice_accepted="message verbatim ",
                                     launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None, **kwargs)

    def test_publish_requires_check_armable_freshness_notice_and_sealed_bytes(self):
        with self.assertRaisesRegex(entry.Refused, "check.json"):
            self.publish()
        record = self.checked()
        record["armable"] = False
        entry.saved_json(self.stage / "check.json", record)
        with self.assertRaisesRegex(entry.Refused, "armable"):
            self.publish()
        self.checked()
        with self.assertRaisesRegex(entry.Refused, "notice acceptance"):
            entry.publish_install(candidate=self.stage)
        os.utime(self.plan, ns=(time.time_ns(), time.time_ns()))
        with self.assertRaisesRegex(entry.Refused, "newer"):
            self.publish()
        self.checked()
        raw = self.plan.read_bytes()
        stamp = self.plan.stat().st_mtime_ns
        self.plan.write_bytes(raw + b" ")
        os.utime(self.plan, ns=(stamp, stamp))
        with self.assertRaisesRegex(entry.Refused, "sealed-byte drift"):
            self.publish()
        self.assertFalse((self.custody / "night_plan.json").exists())

    def test_post_publication_failure_uninstalls_before_matching_byte_restore(self):
        self.checked()
        raw = self.plan.read_bytes()
        calls = []
        def fail(argv, **kw):
            calls.append(list(map(str, argv)))
            self.assertTrue((self.custody / "night_plan.json").exists())
            self.assertFalse(self.plan.exists())
            return subprocess.CompletedProcess(argv, 0 if "--uninstall" in argv else 2, "", "fixture refusal")
        with self.assertRaisesRegex(entry.Refused, "installer --launchd-probe failed"):
            self.publish(runner=fail)
        self.assertIn("--uninstall", calls[-1])
        self.assertEqual(self.plan.read_bytes(), raw)
        self.assertFalse((self.custody / "night_plan.json").exists())
        record = json.loads((self.stage / "install.json").read_text())
        self.assertEqual(record["outcome"], "restored_unpublished")
        self.assertEqual(record["notice_accepted"], "message verbatim ")
        self.assertEqual([c["exit_code"] for c in record["commands"]], [2, 0])
        self.checked("retry")  # Bare nonzero is never silently arm_transport.

    def test_nonzero_cleanup_or_changed_bytes_preserves_published_state(self):
        for mode in ("nonzero", "changed"):
            with self.subTest(mode=mode):
                self.checked()
                def failure(argv, **kw):
                    if "--uninstall" in argv:
                        if mode == "changed":
                            (self.custody / "night_plan.json").write_text("changed")
                        return subprocess.CompletedProcess(argv, 1 if mode == "nonzero" else 0, "", "")
                    return subprocess.CompletedProcess(argv, 2, "", "failed")
                with self.assertRaisesRegex(entry.Refused, "retained state"):
                    self.publish(runner=failure)
                self.assertTrue((self.custody / "night_plan.json").exists())
                self.assertFalse(self.plan.exists())
                self.assertEqual(json.loads((self.stage / "install.json").read_text())["outcome"], "retained")
                # Fixture reset only, never a production remedy.
                (self.custody / "night_plan.json").unlink()
                attempt = next((self.stage / "arm-attempts").iterdir())
                self.plan.write_bytes((attempt / "plan.json").read_bytes())
                shutil.rmtree(self.stage / "arm-attempts")

    def test_verify_failure_and_unexpected_defect_both_recover(self):
        for exception in (entry.Refused("calendar differs"), RuntimeError("defect")):
            with self.subTest(exception=type(exception).__name__):
                self.checked()
                calls = []
                def success(argv, **kw):
                    calls.append(list(map(str, argv)))
                    if "--launchd-probe" in argv:
                        (self.custody / "night_probe_receipt.json").write_text("fixture receipt")
                    return subprocess.CompletedProcess(argv, 0, "", "")
                with patch.object(entry, "verify_state", side_effect=exception):
                    with self.assertRaises(type(exception)):
                        self.publish(runner=success)
                self.assertEqual(len(calls), 3)
                self.assertIn("--launchd-probe", calls[0])
                self.assertNotIn("--launchd-probe", calls[1])
                self.assertIn("--uninstall", calls[2])
                self.assertEqual(json.loads((self.stage / "install.json").read_text())["outcome"], "restored_unpublished")
                shutil.rmtree(self.stage / "arm-attempts")

    def test_exception_immediately_after_atomic_move_still_uninstalls(self):
        self.checked()
        original = os.replace
        calls = []
        def interrupted(source, destination):
            original(source, destination)
            if source == self.plan:
                raise RuntimeError("lost publication acknowledgement")
        def cleanup(argv, **kwargs):
            calls.append(argv)
            self.assertIn("--uninstall", argv)
            self.assertTrue((self.custody / "night_plan.json").exists())
            return subprocess.CompletedProcess(argv, 0, "", "")
        with patch.object(entry.os, "replace", side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, "lost publication"):
                self.publish(runner=cleanup)
        self.assertEqual(len(calls), 1)
        self.assertTrue(self.plan.exists())
        self.assertFalse((self.custody / "night_plan.json").exists())

    def test_existing_publication_and_cross_device_refuse_without_installer(self):
        self.checked()
        published = self.custody / "night_plan.json"
        published.write_text("foreign")
        with self.assertRaisesRegex(entry.Refused, "existing foreign"):
            self.publish(runner=lambda *a, **kw: self.fail("installer invoked"))
        self.assertEqual(published.read_text(), "foreign")
        published.unlink()
        original = Path.stat
        def stat(path, *a, **kw):
            result = original(path, *a, **kw)
            if path == self.custody:
                fields = list(result); fields[2] += 1
                return os.stat_result(fields)
            return result
        with patch.object(Path, "stat", stat), self.assertRaisesRegex(entry.Refused, "one filesystem"):
            self.publish(runner=lambda *a, **kw: self.fail("installer invoked"))

    def test_cli_success_refusal_and_defect_split(self):
        for operation, args in (("check", []), ("publish_install", ["--notice-accepted", "id"]),
                                ("verify", []), ("uninstall", [])):
            argv = [operation.replace("_", "-"), "--candidate", str(self.stage), *args]
            with patch.object(entry, operation, return_value={"ok": True}), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(entry.main(argv), 0)
                self.assertEqual(json.loads(output.getvalue()), {"ok": True})
            for error, code, prefix in ((entry.Refused("stopped"), 2, "REFUSED:"),
                                        (RuntimeError("defect"), 1, "ERROR:")):
                with patch.object(entry, operation, side_effect=error), contextlib.redirect_stderr(io.StringIO()) as errors:
                    self.assertEqual(entry.main(argv), code)
                    self.assertTrue(errors.getvalue().startswith(prefix))

    def test_uninstall_records_nonzero_and_does_nothing_else(self):
        published = self.custody / "night_plan.json"
        published.write_text("malformed retired plan")
        before = published.read_bytes()
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 7, "", "cleanup failed")
        with self.assertRaisesRegex(entry.Refused, r"uninstall failed \(7\)"):
            entry.uninstall(candidate=self.stage, runner=runner, launchctl_bin="/fixture/launchctl")
        self.assertEqual(len(calls), 1)
        self.assertIn("--uninstall", calls[0])
        self.assertNotIn("--python", calls[0])
        self.assertEqual(published.read_bytes(), before)
        self.assertEqual(json.loads((self.stage / "uninstall.json").read_text())[0]["exit_code"], 7)


@unittest.skipUnless(Path('/bin/zsh').is_file(), 'real installer requires zsh')
class LifecycleCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PrepareTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        PrepareTests.tearDownClass.__func__(cls)

    def test_prepare_check_real_installer_fake_launchctl_verify_and_uninstall(self):
        from joulewise import night_agent_install as installer, night_gate
        from joulewise.quiet_predicate_campaign import RECEIPT_SCHEMA
        from tests.test_night_agent_install import FakeLaunchctl, LABELS
        from tests.test_arm_census import observation, row
        temp = _census_clean_tempdir(prefix="composed-", dir=self.base)
        self.addCleanup(temp.cleanup)
        base = Path(temp.name).resolve()
        home = base / "home"
        fake = FakeLaunchctl(base / "fake")
        canonical = base / "canonical"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(self.remote), str(canonical)], check=True)
        resident = base / "resident.json"
        entry.saved_json(resident, {"resident_session": None})
        env = {"HOME": str(home), "PATH": str(self.bin) + ":" + os.environ["PATH"]}
        calls = []
        original_run, original_popen = subprocess.run, subprocess.Popen
        def spy(operation):
            def wrapped(argv, *args, **kwargs):
                text = list(map(str, argv))
                calls.append(text)
                self.assertFalse(any(Path(arg).name in ("launchctl", "claude", "mail", "powermetrics") for arg in text), text)
                return operation(argv, *args, **kwargs)
            return wrapped
        def probes(argv, **kwargs):
            if tuple(argv) == night_gate.AGENT_CENSUS_ARGV:
                return subprocess.CompletedProcess(argv, 1, "", "")
            self.assertNotIn(entry.CANONICAL, list(map(str, argv)))
            return entry.probe_command(argv, **kwargs)
        def builder(root):
            # Installer's real shell still dispatches its actual module. Only
            # its host process census is injected, as in the arm-sequence
            # fixture; sysmon/pgrep is unavailable inside the test sandbox.
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text(f"#!{sys.executable}\n" + """import os,sys
from pathlib import Path
sys.dont_write_bytecode=True
args=sys.argv[1:]
if args[:3]==['-B','-m','joulewise.night_agent_install']:
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
    from joulewise import night_agent_install
    from unittest.mock import patch
    with patch.object(night_agent_install,'probe_process_census'):
        raise SystemExit(night_agent_install.main(args[3:]))
os.execv(sys.executable,[sys.executable,*args])
""")
            python.chmod(0o755)
        with patch.dict(os.environ, env), patch.object(subprocess, "run", side_effect=spy(original_run)), \
                patch.object(subprocess, "Popen", side_effect=spy(original_popen)):
            state = entry.prepare(kind=entry.KIND, t0=str((int(time.time()) // 60 + 90) * 60),
                head=self.head, remote=str(self.remote), roots_under=base / "roots", staging_under=base / "staging",
                builder=builder, lock_verifier=lambda root: None)
            stage, custody = Path(state["staging"]), Path(state["custody_root"])
            checked = entry.check(candidate=stage, canonical=canonical, supervisor_state=resident,
                runner=probes, caller_pid=90, census_observer=lambda **kw: observation(
                    row(20, 1, "/bin/claude"), row(90, 20, "/bin/python3"), hits=(20,)),
                lock_verifier=lambda root: None)
            self.assertTrue(checked["armable"])
            self.assertFalse(fake.calls(), "prepare + check invoked launchctl")
            self.assertFalse(any("--launchctl-bin" in c for c in calls))
            published = custody / "night_plan.json"
            raw = (stage / "night_plan.json").read_bytes()
            inode = (stage / "night_plan.json").stat().st_ino
            def real_installer(argv, **kwargs):
                if "--launchd-probe" in argv:
                    self.assertFalse((stage / "night_plan.json").exists())
                    self.assertEqual(published.stat().st_ino, inode, "publication must be a rename")
                    self.assertEqual(published.read_bytes(), raw)
                    plan = night_gate.NightPlan.from_mapping(json.loads(raw))
                    bindings = installer.evidence_probe_bindings(plan, published, str(Path(state["measurement_root"]) / ".venv/bin/python"))
                    label = installer.probe_label(plan.plan_id)
                    now = time.time()
                    receipt = dict(bindings, schema=RECEIPT_SCHEMA, outcome="ok", refusal_code=None,
                        started_epoch_s=now, finished_epoch_s=now, launchd_label=label,
                        verify_only=True, collect_started=False, load_started=False, cleanup_proven=True,
                        driver_pid=999998, chain_pgid=999999,
                        verify_stdout=["VERIFY_ONLY_OK manifest=" + bindings["manifest_sha256"]])
                    # Same subprocess FakeLaunchctl receipt seam as installer
                    # tests. No chain, sampler, courier or real launchd runs.
                    fake.directive(label, "bootstrap", probe_receipt=receipt,
                                   receipt_path=str(custody / "night_probe_receipt.pending.json"))
                return entry.probe_command(argv, **kwargs)
            installed = entry.publish_install(candidate=stage, notice_accepted="gmail-fixture-id",
                launchctl_bin=str(fake.executable), runner=real_installer, lock_verifier=lambda root: None)
            self.assertEqual(installed["outcome"], "installed")
            self.assertEqual([c["exit_code"] for c in installed["commands"]], [0, 0])
            self.assertEqual(installed["probe_receipt_sha256"], entry.digest(custody / "night_probe_receipt.json"))
            self.assertEqual(installed["verification"]["request_epoch_s"], state["schedule"]["boundaries"]["REQUEST / exit BEFORE"])
            self.assertTrue(all(fake.loaded(label) for label in LABELS))
            verified = entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
            self.assertEqual([j["calendar"] for j in verified["jobs"]],
                             [state["schedule"]["night_calendar"], state["schedule"]["deadman_calendar"]])
            self.assertEqual([j["label"] for j in verified["jobs"]], list(LABELS))
            self.assertEqual(verified["schedule"]["boundaries"], state["schedule"]["boundaries"])
            for job in verified["jobs"]:
                label = job["label"]
                self.assertEqual(job["liveness"], "LOADED")
                self.assertEqual(job["exit_code"], 0)
                # The fake returns liveness only, with no calendar text.
                self.assertEqual(job["stdout"], f"gui/{os.getuid()}/{label} = {{\n}}\n")
                plist_path = home / "Library/LaunchAgents" / (label + ".plist")
                render_path = stage / "render" / (label + ".plist")
                self.assertEqual(job["plist"], str(plist_path))
                self.assertEqual(job["rendered_plist"], str(render_path))
                self.assertEqual(job["plist_sha256"], entry.digest(plist_path))
                self.assertEqual(job["render_sha256"], entry.digest(render_path))
                original = plist_path.read_bytes()
                self.assertEqual(original, render_path.read_bytes())
                argv = plistlib.loads(original)["ProgramArguments"]
                wrong_plan = list(argv); wrong_plan[wrong_plan.index("--plan") + 1] = "/wrong/plan.json"
                wrong_python = list(argv); wrong_python[0] = "/wrong/python"
                mutations = (
                    ("Label", "com.wrong.label", "plist Label differs"),
                    ("StartCalendarInterval", {"Hour": 3}, "calendar differs"),
                    ("ProgramArguments", argv + ["--unexpected"], "arguments differ"),
                    ("ProgramArguments", wrong_plan, "arguments differ"),
                    ("ProgramArguments", wrong_python, "arguments differ"),
                    ("WorkingDirectory", "/wrong", "working directory differs"),
                    ("RunAtLoad", True, "RunAtLoad differs"),
                    ("KeepAlive", True, "installed plist bytes differ from render"),
                )
                for key, value, message in mutations:
                    with self.subTest(label=label, key=key, value=value):
                        plist = plistlib.loads(original); plist[key] = value
                        plist_path.write_bytes(plistlib.dumps(plist))
                        with self.assertRaisesRegex(entry.Refused, message):
                            entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
                # Same parsed values, different bytes must still refuse (30a).
                with self.subTest(label=label, change="binary serialization"):
                    equivalent = plistlib.dumps(plistlib.loads(original), fmt=plistlib.FMT_BINARY)
                    self.assertEqual(plistlib.loads(equivalent), plistlib.loads(original))
                    self.assertNotEqual(equivalent, original)
                    plist_path.write_bytes(equivalent)
                    with self.assertRaisesRegex(entry.Refused, "installed plist bytes differ from render"):
                        entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
                plist_path.write_bytes(original)
                with self.subTest(label=label, liveness="ABSENT"):
                    fake.set_loaded(label, False)
                    with self.assertRaisesRegex(entry.Refused, "ABSENT"):
                        entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
                    fake.set_loaded(label, True)
                with self.subTest(label=label, liveness="UNKNOWN"):
                    fake.directive(label, "print", fault=64)
                    with self.assertRaisesRegex(entry.Refused, "UNKNOWN"):
                        entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
                    fake.directive(label, "print")
            result = entry.uninstall(candidate=stage, launchctl_bin=str(fake.executable))
            self.assertEqual(result["exit_code"], 0)
            self.assertFalse(any(fake.loaded(label) for label in LABELS))
            self.assertEqual(published.read_bytes(), raw, "uninstall must not unpublish")
            self.assertTrue(any("--launchd-probe" in c for c in calls))
            self.assertTrue(any(c[0].endswith("install_night_agent.sh") and "--uninstall" in c for c in calls))


if __name__ == "__main__":
    unittest.main()
