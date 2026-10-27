"""Production-shaped files with in-process clocks, Git, tools and children.

No subprocess is started by this module, including its disposable Git fixture.
"""
from contextlib import redirect_stdout
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from urllib.parse import unquote, urlparse
import zlib

from scripts import b6_machine_test as mt
from joulewise import agent_identity, calibration_ledger
# Import before Case.setUp patches subprocess.Popen: a first import inside that patch
# would build t0_rehearsal.ObservedProcess as a subclass of the mock.
from joulewise import t0_rehearsal as _t0_rehearsal  # noqa: F401
from joulewise.b5 import chain, plan
from joulewise.b6 import registration, smoke
from joulewise.hazards.base import Context
from tests.b6.support import ROOT, fp


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def append(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(value) + "\n")


def clock_row(event, run_id, second):
    return {"event": event, "run_id": run_id, "stage_dir": "synthetic-stage",
            "unit_key": run_id, "unit_run_ids": [run_id],
            "clock": {"monotonic_ns": second * 10**9, "wall_s": 1800000000 + second,
                      "sleep_offset_ns": 100, "read_skew_ns": 200}}


def fixture_commit(root):
    """Write ordinary loose Git objects in-process; no git child or maintenance."""
    git = root / ".git"
    (git / "objects").mkdir(parents=True, exist_ok=True)
    (git / "refs").mkdir(exist_ok=True)
    (git / "config").write_text("[core]\nrepositoryformatversion = 0\nbare = false\n"
                               "[maintenance]\nauto = false\nautoDetach = false\n"
                               "[gc]\nauto = 0\nautoDetach = false\n")

    def obj(kind, raw):
        data = kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw
        digest = hashlib.sha1(data).hexdigest()
        target = git / "objects" / digest[:2] / digest[2:]
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(zlib.compress(data))
        return digest

    def tree(directory):
        entries = []
        for path in sorted(directory.iterdir(), key=lambda p: p.name + ("/" if p.is_dir() else "")):
            if path.name in {".git", ".venv", "runs"}:
                continue
            if path.is_dir():
                mode, digest = "40000", tree(path)
            else:
                mode = "100755" if path.stat().st_mode & 0o111 else "100644"
                digest = obj("blob", path.read_bytes())
            entries.append(mode.encode() + b" " + path.name.encode() + b"\0" + bytes.fromhex(digest))
        return obj("tree", b"".join(entries))

    head = obj("commit", (f"tree {tree(root)}\nauthor Test <test@invalid> 1800000000 +0000\n"
                          "committer Test <test@invalid> 1800000000 +0000\n\nSynthetic machine smoke\n").encode())
    (git / "HEAD").write_text(head + "\n")
    return head


class FakeTools:
    def __init__(self, measurement):
        self.measurement = measurement
        self.calls = []
        self.dirty = "?? synthetic-note\n"
        self.identity_bytes = {name: json.dumps({"synthetic": name}, indent=2).encode() + b"\n"
                               for name in mt.EXPECTED}

    def __call__(self, argv, **kwargs):
        argv = list(map(str, argv))
        self.calls.append((argv, kwargs))
        stdout = ""
        if Path(argv[0]).name == "git":
            if argv[1] == "clone":
                source = Path(unquote(urlparse(argv[-2]).path))
                shutil.copytree(source, Path(argv[-1]))
            else:
                root = Path(argv[2]) if "-C" in argv else Path(kwargs["cwd"])
                args = argv[3:] if "-C" in argv else argv[1:]
                if "rev-parse" in args:
                    stdout = (root / ".git/HEAD").read_text()
                elif args[0] == "show":
                    stdout = (root / args[1].split(":", 1)[1]).read_text()
                elif "status" in args:
                    stdout = self.dirty if root == self.measurement else ""
                elif "commit" in args:
                    fixture_commit(root)
                elif not any(k in args for k in ("checkout", "remote", "config", "add")):
                    raise AssertionError(f"unexpected Git operation: {argv}")
        elif argv[0] == str(self.measurement / ".venv/bin/python") and "-c" in argv and "-I" not in argv:
            self.assert_identity_argv(argv)
            stdout = json.dumps({name: base64.b64encode(raw).decode() for name, raw in self.identity_bytes.items()})
        elif argv[:4] == [mt.PYTHON, "-m", "venv", "--without-pip"]:
            venv = Path(argv[-1])
            (venv / "lib/python3.13/site-packages").mkdir(parents=True, exist_ok=True)
            (venv / "bin").mkdir(parents=True, exist_ok=True)
            (venv / "bin/python3.13").write_text("synthetic interpreter\n")
            (venv / "bin/python").write_text("synthetic interpreter\n")
        elif argv[0].endswith("install_night_agent.sh"):
            if "--render-only" in argv:
                dest = Path(argv[-1])
                dest.mkdir(parents=True)
                # Actual installer renderer; its probes and publication remain
                # injected. The courier is the --courier-bin the harness passes
                # (the real installer's choice when the option is given), or
                # this fake's claude when a test sets self.courier_override.
                from joulewise import night_agent_install, night_gate
                from scripts import run_night
                parsed = night_gate.NightPlan.from_mapping(json.loads(Path(argv[2]).read_text()))
                courier = getattr(self, "courier_override", None) or (
                    argv[argv.index("--courier-bin") + 1] if "--courier-bin" in argv else "/synthetic/claude")
                prepared = night_agent_install.Prepared(parsed, Path(argv[2]), self.measurement, argv[4],
                    (ROOT / "configs/launchd/com.joulewise.night.plist.template").read_text(),
                    courier, str(Path(courier).parent) + ":/bin", run_night.schedule(parsed),
                    run_night.install_spans_for_day)
                for label, payload in prepared.render(night_agent_install.LABELS, require_published=False):
                    (dest / (label + ".plist")).write_bytes(payload)
            elif "--uninstall" not in argv:
                raise AssertionError("test attempted to install")
        elif argv[0] == str(self.measurement / ".venv/bin/python") and "-I" in argv:
            stdout = json.dumps({"python": "3.13", "packages": {"mlx": "test"}})
        elif argv[:2] == ["/usr/sbin/sysctl", "-n"]:
            stdout = "test-boot" if argv[-1] == "kern.bootsessionuuid" else "TEST"
        elif argv[0] == "/usr/sbin/ioreg":
            stdout = "no meter"
        elif argv[0] != "/bin/zsh":
            raise AssertionError(f"unexpected tool: {argv}")
        if not kwargs.get("text"):
            stdout = stdout.encode()
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="" if kwargs.get("text") else b"")

    def assert_identity_argv(self, argv):
        assert argv == [str(self.measurement / ".venv/bin/python"), "-B", "-c", mt.IDENTITY_SOURCE,
                        str(self.measurement / "scripts/write_derivation_night_inputs.py")]


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR", "/private/tmp"), prefix="b6mt-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Trap any accidentally un-injected hardware or process action.
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(mt.subprocess, "Popen", side_effect=AssertionError("real spawn forbidden")).start()
        mock.patch.object(mt.subprocess, "run", side_effect=AssertionError("real tool forbidden")).start()
        mock.patch.object(mt.time, "sleep", side_effect=AssertionError("real sleep forbidden")).start()

    def measurement(self):
        measurement = self.root / "measurement"
        campaigns = measurement / "configs/campaigns"
        tree = json.loads((ROOT / "configs/campaigns" / mt.PACK / "plan_tree.json").read_text())
        dirs = {mt.PACK, "v5_claim_25g83"}
        dirs.update(Path(d.config_dir).parts[2] for d in plan.resolve_stage_dispatches(tree, ROOT))
        for name in dirs:
            shutil.copytree(ROOT / "configs/campaigns" / name, campaigns / name)
        runbook = measurement / chain.RUNBOOK_RELATIVE
        runbook.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / chain.RUNBOOK_RELATIVE, runbook)
        (measurement / "scripts").mkdir()
        for name in ("b6_machine_test.py", "b6_courier.sh", "install_night_agent.sh", "write_derivation_night_inputs.py", "run_night.py"):
            shutil.copyfile(ROOT / "scripts" / name, measurement / "scripts" / name)
        venv = measurement / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "bin/python").write_text("#!/bin/sh\nexit 99\n")
        (venv / "bin/python").chmod(0o755)
        (venv / "lib/python3.13/site-packages").mkdir(parents=True)
        ledger = measurement / plan.DEFAULT_LEDGER_RELATIVE
        ledger.parent.mkdir()
        ledger.write_bytes(b"")
        put(measurement / plan.HEAD_PIN_RELATIVE, {"ledger_schema": calibration_ledger.LEDGER_SCHEMA,
                                                 "sequence": 0, "head_digest": calibration_ledger.GENESIS_DIGEST})
        fixture_commit(measurement)
        return measurement

    def prepared(self, *, install=False, real_fingerprint=False, courier_override=None):
        measurement = self.measurement()
        runner = FakeTools(measurement)
        runner.courier_override = courier_override
        self.addCleanup(mock.patch.stopall)
        # ledger_head_status uses the exact pin format and production parser;
        # its committed-Git read is supplied by the same in-process Git seam.
        mock.patch.object(calibration_ledger.subprocess, "run", side_effect=runner).start()
        now = 1800000001

        def smoke_prepare(*args, **kwargs):
            kwargs["plan_writer"] = lambda inputs: plan.write_window_plan(
                inputs, now=lambda: now, pack_digest=lambda path: "e" * 64)
            return smoke.prepare(*args, **kwargs)

        seams = mt.PrepareSeams(run=runner, now=lambda: now, ctx=Context(),
            model_files=mock.Mock(return_value=({"measured": {"synthetic-model": "b" * 64}}, [])),
            runtime_versions=mock.Mock(return_value={"python": "3.13", "packages": {}}),
            fingerprint_collect=mock.Mock(return_value=fp()), smoke_prepare=smoke_prepare)
        if real_fingerprint:
            from joulewise.b6 import fingerprint
            seams.ctx = None
            seams.runtime_versions = mt.precheck.runtime_versions
            seams.fingerprint_collect = lambda *a, **kw: fingerprint.collect(*a, **kw, read_bytes=lambda p: b"synthetic tool")
        before = {str(p.relative_to(measurement)): p.read_bytes() for p in measurement.rglob("*") if p.is_file()}
        state = mt.prepare(measurement, self.root / "output", seams=seams, install=install)
        after = {str(p.relative_to(measurement)): p.read_bytes() for p in measurement.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        return state, runner, seams


class PrepareTests(Case):
    def test_prepare_real_plan_smoke_wrapper_and_rendered_jobs(self):
        state, runner, seams = self.prepared()
        out, measurement = Path(state["out"]), Path(state["measurement_root"])
        acceptance = registration.load(out / "registration")
        self.assertEqual(acceptance["registered_commit"], state["measurement_head"])
        self.assertEqual(acceptance["pack_id"], mt.PACK)
        self.assertEqual(str(acceptance["calibration"]["alignment_reference_s"]), "0.036462861644980")
        self.assertIsNone(acceptance["calibration"]["operative_bound_stop_s"])
        self.assertEqual(acceptance["calibration"]["acceptance_corpus"], [])
        for name in ("identity_pins.json", "sizing_b5.json"):
            self.assertEqual((out / "registration" / name).read_bytes(), (measurement / mt.SEALED_DIR / name).read_bytes())
        for name, raw in runner.identity_bytes.items():
            self.assertEqual((out / "inputs" / name).read_bytes(), raw)
            self.assertFalse(state["identities"][name]["matches_block3"])
        self.assertIn("measurement_dirty", {n["kind"] for n in state["notes"]})
        inputs = json.loads((out / "plan-inputs.json").read_text())
        self.assertEqual(inputs["schema"], "joulewise.b5_window_plan_inputs.v2")
        self.assertEqual(inputs["t0_epoch_s"], 60 * ((1800000001 + 900 + 59) // 60))
        self.assertTrue(inputs["plan_id"].startswith("MT-ALPHA-"))
        self.assertFalse(inputs["g10"])
        self.assertEqual(inputs["bytes_per_member"], 182 * 1024 * 1024)
        expected = mt.registered_thresholds((measurement / mt.REGISTRATION).read_text())
        # Block-6 registration §8.6: the clock HOLD drops block 5's placement term (plan_inputs.CLOCK_THRESHOLDS).
        from joulewise.b6 import plan_inputs
        expected["clock"].update(plan_inputs.CLOCK_THRESHOLDS)
        self.assertEqual(inputs["thresholds"], expected)
        sizing = json.loads((measurement / mt.SIZING).read_text())["packs"]["ALPHA"]
        for key in ("programmed_span_s", "T_stream_max_s"):
            self.assertEqual(inputs[key]["seconds"], sizing[key])
            self.assertEqual(inputs[key]["source_pointer"], f"/packs/ALPHA/{key}")
        plan_json = json.loads(Path(state["plan_path"]).read_text())
        self.assertEqual(plan_json["hazard_window"]["member_count"], 4)
        bindings = plan_json["hazard_window"]["bindings"]
        self.assertEqual(bindings["capture_screen"], {
            "alignment_reference_s": "0.036462861644980", "bracket_screen_s": "0.014531",
            "operative_bound_stop_s": "0.139"})
        self.assertIs(bindings["spare_retries"], False)
        rendered = Path(plan_json["chain_path"]).read_text()
        self.assertIn("screen_b6_calibration()", rendered)
        self.assertNotIn("screen_pre_calibration()", rendered)
        self.assertNotIn("Spare-slot retry", rendered)
        smoke_state = json.loads(Path(state["smoke_state"]).read_text())
        self.assertEqual(smoke_state["registration_dir"], str(out / "registration"))
        self.assertEqual(smoke_state["driver_argv"], smoke.driver_argv(smoke.SmokePrepared.from_json(smoke_state)))
        self.assertTrue(smoke_state["driver_argv"][-1].endswith("/bin/smoke-courier"))
        self.assertNotEqual(smoke_state["measurement"], str(measurement))
        clone = Path(smoke_state["measurement"])
        self.assertEqual((clone / plan.DEFAULT_LEDGER_RELATIVE).read_bytes(), (measurement / plan.DEFAULT_LEDGER_RELATIVE).read_bytes())
        self.assertNotEqual((clone / plan.DEFAULT_LEDGER_RELATIVE).stat().st_ino, (measurement / plan.DEFAULT_LEDGER_RELATIVE).stat().st_ino)
        self.assertIn("run_campaign_reduced.py", (clone / ".venv/bin/python").read_text())
        injector = plistlib.loads(Path(state["injector_plist"]).read_bytes())
        self.assertEqual(injector["ProgramArguments"], [mt.PYTHON, "-B", str(measurement / "scripts/b6_machine_test.py"),
                                                     "inject", "--state", str(out / "machine-test.json")])
        self.assertTrue(injector["RunAtLoad"])
        self.assertEqual(injector["ProcessType"], "Standard")
        self.assertEqual(injector["StandardOutPath"], str(out / "inject.stdout"))
        self.assertEqual(injector["StandardErrorPath"], str(out / "inject.stderr"))
        self.assertTrue((out / "plists/com.joulewise.night.plist").exists())
        for label, mode in (("com.joulewise.night", "run"), ("com.joulewise.night.deadman", "dead-man")):
            payload = plistlib.loads((out / "plists" / (label + ".plist")).read_bytes())
            self.assertEqual(payload["ProcessType"], "Interactive")
            self.assertEqual(payload["ProgramArguments"], [str(measurement / ".venv/bin/python"),
                str(measurement / "scripts/run_night.py"), mode, "--plan", state["plan_path"],
                "--courier-bin", smoke_state["driver_argv"][-1]])
        self.assertNotIn("claude", json.dumps(payload))
        exact = mt.installer_argv(measurement, Path(state["plan_path"]), smoke_state["driver_argv"][-1])
        self.assertIn((exact + ["--render-only", str(out / "plists")]), [argv for argv, _ in runner.calls])
        script = Path(state["install_script"]).read_text()
        self.assertIn(mt.shlex.join(exact), script)
        self.assertNotIn("--render-only", script)
        self.assertIn("/bin/launchctl bootstrap gui/$(id -u) " + mt.shlex.quote(state["injector_plist"]), script)
        self.assertFalse(any(argv[0] == "/bin/zsh" for argv, _ in runner.calls))
        seams.model_files.assert_called_once()
        seams.runtime_versions.assert_called_once()
        seams.fingerprint_collect.assert_called_once()

    def test_an_agent_courier_in_the_rendered_job_refuses(self):
        # Design 3.1: the smoke sends no mail through an agent.
        with self.assertRaisesRegex(ValueError, "courier wrapper"):
            self.prepared(courier_override="/synthetic/claude")

    def test_install_is_last_and_uses_complete_script(self):
        state, runner, _ = self.prepared(install=True)
        self.assertEqual(runner.calls[-1][0], ["/bin/zsh", state["install_script"]])
        self.assertTrue(Path(state["out"], "machine-test.json").exists())

    def test_runtime_and_fingerprint_probes_use_injected_readonly_runner(self):
        state, runner, _ = self.prepared(real_fingerprint=True)
        value = json.loads(Path(state["fingerprint"]).read_text())
        self.assertEqual(value["code_commit"], state["measurement_head"])
        self.assertTrue(value["code_dirty"])
        self.assertIsNone(value["meter_device"])
        self.assertEqual(value["runtime_versions"]["python"], "3.13")
        for argv, kwargs in runner.calls:
            if "status" in argv:
                self.assertEqual(kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")

    def test_path_guards_existing_output_symlink_and_inside_measurement(self):
        for name in ("Claude-output", "nested/coDEX-output"):
            with self.assertRaisesRegex(ValueError, "agent-census"):
                mt.prepare(self.root / "measurement", self.root / name)
            self.assertFalse((self.root / name).exists())
        with self.assertRaisesRegex(ValueError, "agent-census"):
            mt.prepare(self.root / "claude-measurement", self.root / "out")
        with self.assertRaisesRegex(ValueError, "outside"):
            mt.prepare(self.root / "measurement", self.root / "measurement/out")
        with self.assertRaises(FileExistsError):
            mt.prepare(self.root / "measurement", self.root)
        alias = self.root / "alias"
        alias.symlink_to(self.root / "codex-output")
        with self.assertRaises(ValueError):
            mt.guard_path(alias)
        with self.assertRaises(FileExistsError):
            mt.prepare(self.root / "measurement", alias)


class FakeClock:
    def __init__(self, tick):
        self.second, self.tick = 0, tick

    def now(self):
        return 1800000000 + self.second

    def monotonic_ns(self):
        return self.second * 10**9

    def sleep(self, duration):
        assert duration == 1
        self.second += 1
        self.tick(self.second)


class Child:
    def __init__(self, pid):
        self.pid, self.returncode, self.waits, self.terminated, self.killed = pid, None, 0, False, False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = -15

    def wait(self, timeout=None):
        self.waits += 1
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


class InjectTests(Case):
    def environment(self, *, fail_at=None, later_start=False, terminal_at=14, cap=True):
        out, custody = self.root / "out", self.root / "out/custody"
        out.mkdir()
        state = {"out": str(out), "custody_root": str(custody), "t0_epoch_s": 1800000000,
                 "window_max_s": 50, "injection": {"agent_s": 2, "busy_s": 20, "busy_cores": 2}}
        state_path = out / "machine-test.json"
        put(state_path, state)
        starts = []
        children = []

        def tick(second):
            if fail_at == second:
                raise RuntimeError("synthetic interruption")
            if second == 2:
                append(custody / "collection/run_clock.jsonl", clock_row("start", "reference", 2))
            if second == 3:
                append(custody / "collection/run_clock.jsonl", clock_row("end", "reference", 3))
            if second == 4 and not later_start:
                put(custody / "collection/pause.json", {"driver_pid": 123})
                append(custody / "collection/agent_presence.jsonl", {"event": "sighting", "at": {"monotonic_ns": 4 * 10**9}})
            if second == 8:
                (custody / "collection/pause.json").unlink(missing_ok=True)
                append(custody / "collection/agent_presence.jsonl", {"event": "resume", "at": {"monotonic_ns": 8 * 10**9}})
                if later_start:
                    append(custody / "collection/run_clock.jsonl", clock_row("start", "decode", 8))
            if second == 10 and cap:
                append(custody / "collection/idle_wait.jsonl", {"run_id": "decode", "wait_s": 1425,
                                                               "outcome": "skipped", "budget_exhausted": False})
            if second == terminal_at:
                put(custody / "night/result.json", {"chain_exit_code": 0})

        clock = FakeClock(tick)

        def spawn(argv, **kwargs):
            child = Child(8000 + len(children))
            children.append(child)
            starts.append((clock.second, argv, kwargs))
            return child

        def run(argv, **kwargs):
            self.assertEqual(argv, list(mt.AGENT_CENSUS_ARGV))
            return SimpleNamespace(returncode=0, stdout=f"{children[0].pid} Python claude-b6-machine-test\n")

        seams = mt.InjectSeams(now=clock.now, monotonic_ns=clock.monotonic_ns, sleep=clock.sleep, spawn=spawn, run=run)
        return state_path, seams, clock, children, starts

    def test_sequence_no_children_during_arm_and_reap_on_cap_then_terminal(self):
        state, seams, clock, children, starts = self.environment()
        self.assertEqual(mt.inject(state, seams=seams), 0)
        self.assertEqual([t for t, _, _ in starts], [2, 8, 8])
        self.assertIn("claude-b6-machine-test", starts[0][1])
        self.assertEqual(starts[0][2]["executable"], "/bin/sleep")
        self.assertEqual(agent_identity.identify("/bin/sleep", tuple(starts[0][1])), "agent")
        self.assertEqual(agent_identity.identify(mt.PYTHON, (mt.PYTHON, "-c", "pass", "claude-b6-machine-test")), "not_agent")
        self.assertTrue(all(child.waits == 1 and child.terminated for child in children))
        events = mt.read_rows(state.parent / "injections.jsonl")
        self.assertEqual([e["event"] for e in events], ["waiting_first_run", "first_run_started", "agent_started",
            "agent_census", "agent_ended", "pause_ended", "busy_started", "busy_ended", "exit"])
        self.assertEqual(next(e for e in events if e["event"] == "busy_ended")["reason"], "idle_cap_skip")
        self.assertEqual(next(e for e in events if e["event"] == "busy_ended")["monotonic_ns"], 10 * 10**9)
        self.assertEqual(events[-1]["reason"], "night_result")
        self.assertEqual(clock.second, 14)
        self.assertTrue(all("wall_s" in e and "monotonic_ns" in e for e in events))

    def test_later_run_start_is_resume_fallback(self):
        state, seams, _, children, starts = self.environment(later_start=True)
        self.assertEqual(mt.inject(state, seams=seams), 0)
        self.assertEqual([t for t, _, _ in starts], [2, 8, 8])
        self.assertTrue(all(c.waits for c in children))

    def test_exception_reaps_every_child(self):
        for second in (4, 9):
            with self.subTest(second=second):
                base = self.root
                self.root = base / str(second)
                self.root.mkdir()
                state, seams, _, children, _ = self.environment(fail_at=second)
                self.assertEqual(mt.inject(state, seams=seams), 1)
                self.assertTrue(children)
                self.assertTrue(all(c.terminated and c.waits for c in children))
                self.assertIn("exception", [r["event"] for r in mt.read_rows(state.parent / "injections.jsonl")])
                self.root = base

    def test_sigterm_stops_injection_and_reaps_every_child(self):
        # Stage-3 review F2: SIGTERM (launchd bootout) left the agent and busy
        # children running. A recording handler stands in for the default action
        # so the old code cannot end the test process; it must be restored after.
        received = []

        def outer(signum, _frame):
            received.append(signum)

        previous = signal.signal(signal.SIGTERM, outer)
        self.addCleanup(signal.signal, signal.SIGTERM, previous)
        for second in (4, 9):  # mid-agent, mid-busy
            with self.subTest(second=second):
                base = self.root
                self.root = base / f"term-{second}"
                self.root.mkdir()
                state, seams, clock, children, _ = self.environment()
                tick = clock.tick

                def signalled(now, tick=tick, second=second):
                    tick(now)
                    if now == second:
                        os.kill(os.getpid(), signal.SIGTERM)

                clock.tick = signalled
                self.assertEqual(mt.inject(state, seams=seams), 1)
                self.assertEqual(clock.second, second)
                self.assertTrue(children)
                self.assertTrue(all(c.terminated and c.waits for c in children))
                events = mt.read_rows(state.parent / "injections.jsonl")
                self.assertIn("exception", [e["event"] for e in events])
                self.assertIs(signal.getsignal(signal.SIGTERM), outer)
                self.assertEqual(received, [])
                self.root = base

    def test_census_failure_reaps_agent_and_never_starts_busy(self):
        state, seams, _, children, starts = self.environment()
        seams.run = lambda *a, **kw: SimpleNamespace(returncode=1, stdout="")
        self.assertEqual(mt.inject(state, seams=seams), 1)
        self.assertEqual(len(starts), 1)
        self.assertTrue(children[0].waits)

    def test_partial_busy_spawn_failure_reaps_the_started_child(self):
        state, seams, _, children, starts = self.environment()
        original = seams.spawn

        def spawn(argv, **kwargs):
            if len(children) == 2:
                raise OSError("synthetic spawn failure")
            return original(argv, **kwargs)

        seams.spawn = spawn
        self.assertEqual(mt.inject(state, seams=seams), 1)
        self.assertEqual(len(children), 2)
        self.assertTrue(all(c.waits for c in children))

    def test_duration_hard_limit_and_early_terminal_cleanup(self):
        for name, terminal_at, window_max_s, reason in (("duration", 32, 50, "night_result"),
                ("hard", 100, 9, "hard_limit"), ("terminal", 9, 50, "night_result")):
            with self.subTest(name=name):
                base = self.root
                self.root = base / name
                self.root.mkdir()
                state, seams, clock, children, _ = self.environment(terminal_at=terminal_at, cap=False)
                value = json.loads(state.read_text())
                value["window_max_s"] = window_max_s
                put(state, value)
                self.assertEqual(mt.inject(state, seams=seams), 0)
                self.assertTrue(all(c.waits for c in children))
                rows = mt.read_rows(state.parent / "injections.jsonl")
                self.assertEqual(next(r for r in rows if r["event"] == "exit")["reason"], reason)
                if name == "terminal":
                    self.assertEqual(next(r for r in rows if r["event"] == "busy_ended")["reason"], "night_result")
                if name == "duration":
                    self.assertEqual(next(r for r in rows if r["event"] == "busy_ended")["reason"], "duration")
                self.root = base

    def test_injects_into_first_open_run_without_waiting_for_an_end(self):
        state, seams, _, children, _ = self.environment()
        custody = Path(json.loads(state.read_text())["custody_root"])
        append(custody / "collection/run_clock.jsonl", clock_row("start", "first", 0))
        append(custody / "collection/run_clock.jsonl", clock_row("start", "later", 1))
        append(custody / "collection/run_clock.jsonl", clock_row("end", "later", 2))
        self.assertEqual(mt.inject(state, seams=seams), 0)
        self.assertTrue(children)
        self.assertEqual(mt.read_rows(state.parent / "injections.jsonl")[1]["run_id"], "first")

    def test_budget_skip_is_not_a_cap_skip(self):
        rows = [{"run_id": "earlier", "wait_s": 6001, "outcome": "admitted"},
                {"run_id": "budget", "wait_s": 1200, "outcome": "skipped", "budget_exhausted": False}]
        self.assertEqual(mt.cap_skip_rows(rows), [])

    def test_incremental_journal_waits_for_complete_line(self):
        path = self.root / "journal.jsonl"
        journal = mt.Journal(path)
        self.assertEqual(journal.read(), [])
        path.write_bytes(b'{"event":"start"')
        self.assertEqual(journal.read(), [])
        with path.open("ab") as handle:
            handle.write(b'}\n{"event":"end"}\n')
        self.assertEqual([r["event"] for r in journal.read()], ["start", "end"])
        self.assertEqual(len(journal.read()), 2)

    def test_child_timeout_escalates_only_owned_child(self):
        child = Child(9999)
        child.wait = mock.Mock(side_effect=[subprocess.TimeoutExpired("synthetic", 5), 0])
        mt.stop_child(child)
        self.assertTrue(child.terminated and child.killed)
        self.assertEqual(child.wait.call_count, 2)


class ReportTests(Case):
    def custody_fixture(self):
        out = self.root / "out"
        custody, archive = out / "custody", out / "smoke/archive"
        prepared = smoke.SmokePrepared(out / "smoke", out / "measurement", out / "plan.json", custody,
                                      out / "state", mt.PACK, "SMOKE-test-calibration", fp(), {}, out / "registration")
        put(out / "smoke/smoke-state.json", prepared.to_json())
        put(out / "machine-test.json", {"out": str(out), "smoke_state": str(out / "smoke/smoke-state.json"),
            "installer_argv": mt.installer_argv(out / "measurement", out / "plan.json", out / "bin/smoke-courier"),
            "injector_plist": str(out / "inject.plist")})
        at = lambda s: {"monotonic_ns": s * 10**9, "wall_s": 1800000000 + s}
        episode = {"start": at(1), "end": at(40), "since": at(20), "last_sighting": at(20),
                   "pause_end": at(620), "basenames": ["Python"], "pause_s": 600}
        # Production night results carry chain_exit_code, not driver exit_code;
        # smoke.desk resolves the driver's courier outcome from its own records.
        put(custody / "night/result.json", {"chain_exit_code": 0, "verdict": "GO"})
        put(custody / "night/hazard_result.json", {"chain": {"exit_code": 0},
            "agent_pause": {"episodes": [episode], "stopped_by_limit": False},
            "keep_awake": {"verified_start": True, "verified_end": True}, "sleep": {"runs_excluded": []}})
        # Reuse the fixture's successful-member duration and the production
        # 60 s stage gap; the final reference has the first reference's span.
        prefill_start = 2121 + chain.SETTLE_S
        prefill_end = prefill_start + (2200 - 2122)
        reference_start = prefill_end + chain.SETTLE_S
        reference_end = reference_start + (50 - 1)
        for event, second, run_id in (("start", 1, "reference"), ("end", 50, "reference"),
                ("start", 621, "decode"), ("end", 2121, "decode"), ("start", prefill_start, "prefill"),
                ("end", prefill_end, "prefill"), ("start", reference_start, "end-reference"),
                ("end", reference_end, "end-reference")):
            append(custody / "collection/run_clock.jsonl", clock_row(event, run_id, second))
        append(custody / "collection/agent_presence.jsonl", {"event": "sighting", "at": at(20)})
        append(custody / "collection/agent_presence.jsonl", {"event": "resume", "at": at(620)})
        append(out / "injections.jsonl", {"event": "agent_census", "listed": True})
        append(custody / "collection/idle_wait.jsonl", {"run_id": "decode", "outcome": "skipped", "wait_s": 1425})
        append(custody / "collection/idle_wait.jsonl", {"run_id": "end-reference", "outcome": "admitted", "wait_s": 0})
        append(custody / "hazards/meter/stream-000.jsonl", {"k": "h", "status": "absent"})
        from joulewise.flags.schema import make_flag, make_scope, make_source
        from joulewise.flags.catalog import load_catalog
        from joulewise.flags.exclusions import compute
        catalog = load_catalog(smoke.CATALOG_PATH)
        produced_flags = []
        for code, run_id in (("agent.presence", None), ("agent.presence_overlap", "reference"), ("idle.wait_cap_skip", "decode"),
                             ("meter.absent", None)):
            spec = catalog.entry(code)
            flag = make_flag(code=code, family=spec["family"], klass=spec["klass"],
                scope=make_scope(level="member" if run_id else "window", run_id=run_id),
                source=make_source(stage="window", collector="b6-machine-test"),
                interval={"monotonic_ns": [1 * 10**9, 40 * 10**9], "monotonic_raw_ns": None,
                          "wall_s": [1800000001, 1800000040]} if code == "agent.presence" else None)
            produced_flags.append(flag)
            append(archive / "derived/flags.jsonl", flag)
        roster = {"members": [{"run_id": name, "units": []} for name in
                              ("reference", "decode", "prefill", "end-reference")], "cells": []}
        spans = {start["run_id"]: {"monotonic_ns": [start["clock"]["monotonic_ns"], end["clock"]["monotonic_ns"]]}
                 for start, end in mt.agent_pause.paired_run_clocks(mt.read_rows(custody / "collection/run_clock.jsonl"))}
        put(archive / "derived/exclusions.json", compute(produced_flags, roster, spans, catalog))
        proof = {"status": "clean", "spawn_observed": True, "leader_reaped": True, "census_completed": True,
                 "group_survivors": [], "escaped_candidates": []}
        put(archive / "sources/claim-runs/decode/metadata.json", {"environment_admission": {
            "skip_reason": "wait_cap_reached", "effective_wait_cap_s": 1500, "wait_s": 1425,
            "attempts": [{"sampler_start_s": 1800000621 + 75 * k, "start_s": 1800000622 + 75 * k,
                          "end_s": 1800000696 + 75 * k, "sampler_teardown": proof} for k in range(20)]}})
        for name in ("reference", "decode", "prefill", "end-reference"):
            put(archive / "sources/claim-runs" / name / "summary_metrics.json",
                {"status": "failed" if name == "decode" else "succeeded"})
        result = {"status": "physics", "errors": [], "harvest_exit": 0, "archive": str(archive),
                  "flags": ["agent.presence", "agent.presence_overlap", "idle.wait_cap_skip", "meter.absent"]}
        # The report checks every kept run against the reduced plan roster.
        tree = smoke.reduce_tree(json.loads((ROOT / "configs/campaigns" / mt.PACK / "plan_tree.json").read_text()),
                                 json.loads(smoke.KEEP_PATH.read_text())[mt.PACK])
        dispatches = plan.resolve_stage_dispatches(tree, ROOT)
        names = ("reference", "decode", "prefill", "end-reference")
        for dispatch, run_id in zip(dispatches, names):
            put(prepared.measurement / dispatch.config_dir / "order_manifest.json",
                {"executed_order": [{"run_id": run_id}]})
        put(prepared.measurement / "configs/campaigns" / mt.PACK / "plan_tree.json", tree)
        return out / "machine-test.json", custody, archive, result

    def run_report(self, state, result, **kwargs):
        desk = mock.Mock(return_value=result)
        value = mt.report(state, desk=desk, run=mock.Mock(), **kwargs)
        desk.assert_called_once()
        self.assertIsNone(desk.call_args.kwargs["driver_exit"])
        return {i["item"]: i for i in value["items"]}

    def test_all_records_observed_and_structure_only_print(self):
        state, custody, archive, result = self.custody_fixture()
        items = self.run_report(state, result)
        self.assertTrue(all(i["observed"] for i in items.values()), items)
        self.assertTrue(all(i["evidence"] for i in items.values()))
        self.assertTrue(items["collection ran"]["observed"])
        self.assertTrue(items["agent pause"]["detail"]["flags_written"])
        self.assertTrue((state.parent / "report.json").exists())
        with mock.patch.object(mt, "report", return_value={"items": list(items.values())}), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(mt.main(["report", "--state", str(state)]), 0)
        self.assertIn("agent pause: observed", output.getvalue())
        self.assertIn("flags_written=True", output.getvalue())
        self.assertNotRegex(output.getvalue(), r"\b\d+(?:\.\d+)?\s*(?:J|W|s|seconds|minutes)\b")
        self.assertNotIn("1425", output.getvalue())
        self.assertNotIn("1500", output.getvalue())

    def test_collection_rejects_missing_failed_or_unexpected_skip(self):
        state, custody, archive, result = self.custody_fixture()
        path = archive / 'sources/claim-runs/reference/summary_metrics.json'
        for status in (None, 'failed', 'skipped'):
            if status is None:
                path.unlink(missing_ok=True)
            else:
                put(path, {'status': status})
            self.assertFalse(self.run_report(state, result)['collection ran']['observed'])

    def test_collection_does_not_excuse_a_crash_with_only_a_cap_flag(self):
        state, custody, archive, result = self.custody_fixture()
        put(archive / 'sources/claim-runs/decode/metadata.json', {})
        self.assertFalse(self.run_report(state, result)['collection ran']['observed'])

    def test_collection_cap_skip_requires_failed_status_and_cap_reason(self):
        state, custody, archive, result = self.custody_fixture()
        put(archive / 'sources/claim-runs/decode/summary_metrics.json', {'status': 'succeeded'})
        item = self.run_report(state, result)['collection ran']
        self.assertFalse(item['observed'])
        self.assertEqual(item['detail']['unexpected_status'], {'decode': 'succeeded'})

    def test_collection_discloses_unexpected_exclusion_codes_and_rerun_guidance(self):
        from joulewise.flags.catalog import load_catalog
        from joulewise.flags.exclusions import compute
        from joulewise.flags.schema import make_flag, make_scope, make_source
        state, custody, archive, result = self.custody_fixture()
        catalog = load_catalog(smoke.CATALOG_PATH)
        original = mt.read_rows(archive / 'derived/flags.jsonl')
        roster = {'members': [{'run_id': name, 'units': []} for name in
                              ('reference', 'decode', 'prefill', 'end-reference')], 'cells': []}
        spans = {start['run_id']: {'monotonic_ns': [start['clock']['monotonic_ns'], end['clock']['monotonic_ns']]}
                 for start, end in mt.agent_pause.paired_run_clocks(mt.read_rows(custody / 'collection/run_clock.jsonl'))}
        # Exercise both physical causes and mixed codes; rerun advice
        # requires every unexpected exclusion's codes to be known physics.
        for codes, physical in ((['battery.member_span'], True),
                                (['thermal.os_level_nonzero'], True),
                                (['battery.member_span', 'member.bytes_missing'], False)):
            with self.subTest(codes=codes):
                flags = list(original)
                for code in codes:
                    spec = catalog.entry(code)
                    flags.append(make_flag(code=code, family=spec['family'], klass=spec['klass'],
                        scope=make_scope('member', run_id='prefill'),
                        source=make_source('window', 'b6-machine-test')))
                effects = compute(flags, roster, spans, catalog)
                put(archive / 'derived/exclusions.json', effects)
                item = self.run_report(state, result)['collection ran']
                self.assertFalse(item['observed'])
                self.assertEqual(item['detail'].get('unexpected_exclusions'), {'prefill': sorted(codes)})
                self.assertEqual(item['detail']['exclusion_detail'], effects['members_excluded'])
                guidance = 'physical exclusion: rerun the test'
                self.assertEqual(item['detail']['guidance'], guidance if physical else None)
                with mock.patch.object(mt, 'report', return_value={'items': [item]}), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(mt.main(['report', '--state', str(state)]), 0)
                self.assertIn('collection ran: not observed;', output.getvalue())
                for code in codes:
                    self.assertIn(code, output.getvalue())
                self.assertEqual(guidance in output.getvalue(), physical)

    def test_collection_rerun_guidance_withheld_when_a_code_problem_is_beside_it(self):
        # Delta review M1: a physical exclusion beside a failed member is not a rerun.
        from joulewise.flags.catalog import load_catalog
        from joulewise.flags.exclusions import compute
        from joulewise.flags.schema import make_flag, make_scope, make_source
        state, custody, archive, result = self.custody_fixture()
        catalog = load_catalog(smoke.CATALOG_PATH)
        roster = {'members': [{'run_id': name, 'units': []} for name in
                              ('reference', 'decode', 'prefill', 'end-reference')], 'cells': []}
        spans = {start['run_id']: {'monotonic_ns': [start['clock']['monotonic_ns'], end['clock']['monotonic_ns']]}
                 for start, end in mt.agent_pause.paired_run_clocks(mt.read_rows(custody / 'collection/run_clock.jsonl'))}
        flags = list(mt.read_rows(archive / 'derived/flags.jsonl'))
        spec = catalog.entry('thermal.os_level_nonzero')
        flags.append(make_flag(code='thermal.os_level_nonzero', family=spec['family'], klass=spec['klass'],
            scope=make_scope('member', run_id='prefill'), source=make_source('window', 'b6-machine-test')))
        put(archive / 'derived/exclusions.json', compute(flags, roster, spans, catalog))
        summary = archive / 'sources/claim-runs/end-reference/summary_metrics.json'
        put(summary, {**json.loads(summary.read_text()), 'status': 'failed'})
        item = self.run_report(state, result)['collection ran']
        self.assertFalse(item['observed'])
        self.assertEqual(item['detail']['unexpected_exclusions'], {'prefill': ['thermal.os_level_nonzero']})
        self.assertEqual(item['detail']['unexpected_status'], {'end-reference': 'failed'})
        self.assertIsNone(item['detail']['guidance'])

    def test_agent_detail_names_missing_presence_flag(self):
        state, custody, archive, result = self.custody_fixture()
        path = archive / 'derived/flags.jsonl'
        rows = [r for r in mt.read_rows(path) if r['code'] != 'agent.presence']
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        result['flags'].remove('agent.presence')
        item = self.run_report(state, result)['agent pause']
        self.assertFalse(item['observed'])
        self.assertFalse(item['detail']['flags_written'])

    def test_every_planned_run_requires_start_and_end_sleep_readings(self):
        for run_id in ("reference", "decode", "prefill", "end-reference"):
            for event in ("both", "start", "end"):
                with self.subTest(run_id=run_id, event=event):
                    base = self.root
                    self.root = base / (run_id + "-" + event)
                    self.root.mkdir()
                    try:
                        state, custody, archive, result = self.custody_fixture()
                        path = custody / "collection/run_clock.jsonl"
                        rows = [row for row in mt.read_rows(path)
                                if not (row["run_id"] == run_id and (event == "both" or row["event"] == event))]
                        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
                        item = self.run_report(state, result)["per-run sleep readings"]
                        self.assertFalse(item["observed"])
                        self.assertIn(run_id, item["detail"]["missing_or_incomplete_run_ids"])
                    finally:
                        self.root = base

    def test_each_item_missing_or_bad_is_not_observed(self):
        for name in ("agent pause", "agent census", "runner pause", "fresh idle admission", "idle cap", "sampler restarts", "sampler startup readings",
                     "sampler clean termination and no survivor", "meter unplugged", "keep-awake", "per-run sleep readings",
                     "chain exit", "smoke desk", "smoke errors absent", "harvest exit"):
            with self.subTest(item=name):
                base = self.root
                self.root = base / name.replace(" ", "-")
                self.root.mkdir()
                state, custody, archive, result = self.custody_fixture()
                hazard = json.loads((custody / "night/hazard_result.json").read_text())
                metadata_path = archive / "sources/claim-runs/decode/metadata.json"
                metadata = json.loads(metadata_path.read_text())
                if name == "agent pause":
                    hazard["agent_pause"]["episodes"][0]["pause_end"]["monotonic_ns"] -= 10**9
                elif name == "agent census":
                    (state.parent / "injections.jsonl").unlink()
                elif name == "runner pause":
                    (custody / "collection/agent_presence.jsonl").unlink()
                elif name == "fresh idle admission":
                    metadata["environment_admission"]["attempts"][0]["sampler_start_s"] = 1800000619
                elif name == "idle cap":
                    (custody / "collection/idle_wait.jsonl").unlink()
                elif name == "sampler restarts":
                    metadata["environment_admission"]["attempts"] = []
                elif name == "sampler startup readings":
                    del metadata["environment_admission"]["attempts"][0]["start_s"]
                elif name == "sampler clean termination and no survivor":
                    metadata["environment_admission"]["attempts"][0]["sampler_teardown"]["group_survivors"] = [123]
                elif name == "meter unplugged":
                    (custody / "hazards/meter/stream-000.jsonl").unlink()
                elif name == "keep-awake":
                    hazard["keep_awake"]["verified_end"] = False
                elif name == "per-run sleep readings":
                    path = custody / "collection/run_clock.jsonl"
                    rows = mt.read_rows(path)
                    del rows[0]["clock"]["sleep_offset_ns"]
                    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
                elif name == "chain exit":
                    hazard["chain"]["exit_code"] = 1
                elif name == "smoke desk":
                    result["status"] = "fail"
                elif name == "smoke errors absent":
                    result["errors"] = ["synthetic harvest fault"]
                elif name == "harvest exit":
                    result["harvest_exit"] = 1
                put(custody / "night/hazard_result.json", hazard)
                put(metadata_path, metadata)
                items = self.run_report(state, result)
                self.assertFalse(items[name]["observed"])
                with mock.patch.object(mt, "report", return_value={"items": list(items.values())}), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(mt.main(["report", "--state", str(state)]), 0)
                self.assertIn(name + ": not observed", output.getvalue())
                self.assertNotRegex(output.getvalue(), r"\b\d+(?:\.\d+)?\s*(?:J|W|s|seconds|minutes)\b")
                self.root = base

    def test_meter_present_not_exercised_and_no_exclusion_is_not_agent_success(self):
        state, custody, archive, result = self.custody_fixture()
        put(custody / "hazards/meter/stream-000.jsonl", {"k": "h", "status": "streaming"})
        put(archive / "derived/exclusions.json", {"members_excluded": []})
        items = self.run_report(state, result)
        self.assertFalse(items["meter unplugged"]["observed"])
        self.assertEqual(items["meter unplugged"]["detail"], "meter present: not exercised")
        self.assertFalse(items["agent pause"]["observed"])

    def test_duplicate_cap_skip_run_and_no_later_admission_fail(self):
        state, custody, archive, result = self.custody_fixture()
        append(archive / "derived/flags.jsonl", {"code": "idle.wait_cap_skip", "scope": {"run_id": "end-reference"}})
        items = self.run_report(state, result)
        self.assertFalse(items["idle cap"]["observed"])

    def test_raw_sleep_delta_cannot_pass_keep_awake_without_a_flag(self):
        state, custody, _, result = self.custody_fixture()
        path = custody / "collection/run_clock.jsonl"
        rows = mt.read_rows(path)
        rows[1]["clock"]["sleep_offset_ns"] += 2_000_000
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        self.assertFalse(self.run_report(state, result)["keep-awake"]["observed"])

    def test_uninstall_only_after_terminal_and_repeated_report_reuses_smoke(self):
        state, custody, archive, result = self.custody_fixture()
        run = mock.Mock()
        desk = mock.Mock(return_value=result)
        terminal = custody / "night/result.json"
        saved = terminal.read_text()
        terminal.unlink()
        with self.assertRaisesRegex(ValueError, "terminal"):
            mt.report(state, uninstall=True, desk=desk, run=run)
        run.assert_not_called()
        desk.assert_not_called()
        terminal.write_text(saved)
        mt.report(state, uninstall=True, desk=desk, run=run)
        expected = json.loads(state.read_text())
        self.assertEqual(run.call_args_list[0].args[0], expected["installer_argv"] + ["--uninstall"])
        self.assertEqual(run.call_args_list[1].args[0], ["/bin/launchctl", "bootout", f"gui/{os.getuid()}", expected["injector_plist"]])
        put(state.parent / "smoke/smoke-result.json", result)
        desk.reset_mock()
        mt.report(state, desk=desk, run=run)
        desk.assert_not_called()


if __name__ == "__main__":
    unittest.main()
