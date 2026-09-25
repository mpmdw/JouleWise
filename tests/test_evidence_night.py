"""Offline prepare composition and refusal boundaries; no live arm evidence."""
import contextlib
import fcntl
from datetime import datetime, timezone
import io
import inspect
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
from joulewise import corecaptured_loop
from joulewise import night_gate

ROOT = Path(__file__).resolve().parents[1]


class NoticeProtocolTextTests(unittest.TestCase):
    def state(self, protocol_path):
        raw = protocol_path.read_bytes()
        plan = self.addCleanup_path / "plan.json"
        plan.write_text(json.dumps({"authored_epoch_s": 1, "window_max_s": 9000}))
        return {
            "schedule": {"boundaries": {}, "install_spans_today": []},
            "plan_id": "fixture", "attempt": 1, "prior_candidates": [],
            "head": "a" * 40, "measurement_root": "/fixture/clone",
            "custody_root": "/fixture/custody", "plan_path": str(plan), "digests": {},
            "bindings": {"registration_path": str(protocol_path),
                         "registration_sha256": entry.digest(protocol_path),
                         "chain_source_path": "/fixture/chain",
                         "chain_source_sha256": "b" * 64},
        }

    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(temp.cleanup)
        self.addCleanup_path = Path(temp.name)
        self.protocols = ROOT / "configs/campaigns/quiet_predicate_evidence_01"

    def test_v3_notice_states_bound_schedule_and_all_refusal_rules(self):
        protocol_path = ROOT / night_gate.QPE01_PILOT_REGISTRATION_PATH
        protocol = json.loads(protocol_path.read_text())
        text = entry.render_notice(self.state(protocol_path))
        span = (protocol["settle_s"] + (protocol["envelopes"] - 1)
                * protocol["slot_pitch_s"] + protocol["envelope_s"])
        self.assertIn("This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.", text)
        self.assertIn(f'After {protocol["settle_s"]} seconds settling, twelve '
                      f'{protocol["envelope_s"]}-second idle envelopes start {protocol["slot_pitch_s"]} seconds apart '
                      f'and use {protocol["interior_s"]}-second interiors after {protocol["interior_offset_s"]}-second offsets.', text)
        self.assertIn("Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a journal of busy cores (the average number of CPU cores a process kept busy).", text)
        self.assertIn(f'The {span:,}-second program fits inside the {protocol["window_max_s"]:,}-second window; no top-up or automatic repeat.', text)
        self.assertIn(f'A process outside the measurement apparatus (the night\'s own measurement processes) at or above {protocol["t0_non_observer_share_max"]:g} busy cores refuses the night at the arm check (the pre-arm checks run before this notice is sent and before the night is installed) or at t0, the scheduled start.', text)
        rule = protocol["non_observer_process_busy"]
        self.assertIn(f'A process outside the measurement apparatus using {rule["bar_core_seconds"]:g} or more core-seconds (busy cores multiplied by seconds) inside an envelope excludes that envelope. Two such exclusions in a row end the night.', text)
        self.assertIn("At t0 the gate reads launchd's log for the previous ten minutes; when that read succeeds, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes. When the log cannot be read, the count is recorded as not measured and the night continues.", text)
        self.assertIn("During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.", text)
        self.assertNotIn("This first idle-variance", text)
        self.assertNotIn("exactly one read-only git show", text)

    def test_notice_registration_binding_and_relative_clone_root(self):
        registration = ROOT / night_gate.QPE01_PILOT_REGISTRATION_PATH
        state = self.state(registration)
        state["bindings"]["registration_sha256"] = "0" * 64
        with self.assertRaisesRegex(entry.Refused, "notice registration differs from sealed binding"):
            entry.render_notice(state)
        clone = self.addCleanup_path / "clone"
        relative = Path(night_gate.QPE01_PILOT_REGISTRATION_PATH)
        target = clone / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(registration.read_bytes())
        state = self.state(registration)
        state["measurement_root"] = str(clone)
        state["bindings"]["registration_path"] = str(relative)
        self.assertIn("This idle-variance evidence night sizes a later experiment", entry.render_notice(state))

    def test_notice_window_and_registered_counts_refuse_or_render(self):
        protocol = json.loads((ROOT / night_gate.QPE01_PILOT_REGISTRATION_PATH).read_text())
        path = self.addCleanup_path / "changed-registration.json"
        protocol["window_max_s"] = 8000
        path.write_text(json.dumps(protocol))
        with self.assertRaisesRegex(entry.Refused, "notice program exceeds registered window"):
            entry.render_notice(self.state(path))
        protocol["window_max_s"] = 9000
        protocol["settle_s"] = 601
        protocol["non_observer_process_busy"]["abort_after_consecutive"] = 3
        path.write_text(json.dumps(protocol))
        rendered = entry.render_notice(self.state(path))
        self.assertIn("After 601 seconds settling, twelve", rendered)
        self.assertIn("Three such exclusions in a row end the night.", rendered)


def quiet_machine():
    """THE shared fake observation every `check()` in this module injects.

    A clean 30.4 s observation: `launchd` at 0.008 cores (non-observer) and
    the measurement's own `powermetrics` at 0.114 cores, marked
    `observer: true`.  `check` otherwise spends thirty real seconds watching
    THIS machine, and its verdict would then depend on whatever else happens
    to be running (fix round 1, F12: at 16900e3d eighteen LifecycleTests
    checks did exactly that).
    """

    from tests.test_night_gate import QUIET_OBSERVATION

    return dict(QUIET_OBSERVATION)


class ProductionSamplerInvoked(AssertionError):
    """The production 30 s sampler was reached from this test module."""


def _production_sampler_forbidden(*args, **kwargs):
    raise ProductionSamplerInvoked(
        "night_gate.production_interval_observation was called from tests/test_evidence_night.py; "
        "inject quiet_observer=quiet_machine (or another fake) instead")


_SAMPLER_GUARD = None
_CORE_GUARD = None


def quiet_corecaptured_actuator():
    quiet = (ROOT / "tests/fixtures/corecaptured/quiet-header-only.log").read_text()
    return entry.CorecapturedActuator(
        lambda argv, timeout=None: subprocess.CompletedProcess(argv, 0, quiet, ""),
        lambda seconds: None, time.time)


class FakeCorecapturedActuator:
    def __init__(self, before, after, now, exit_codes=None, log_delay_s=0):
        self.logs = [before, after]
        self.now = now
        self.commands = []
        self.sleeps = []
        self.exit_codes = exit_codes or {}
        self.log_delay_s = log_delay_s
        self.timeouts = []

    def run(self, argv, *, timeout=None):
        argv = tuple(argv)
        self.commands.append(argv)
        self.timeouts.append(timeout)
        if argv == corecaptured_loop.LOG_ARGV:
            self.now += self.log_delay_s
            return subprocess.CompletedProcess(argv, 0, self.logs.pop(0), "")
        return subprocess.CompletedProcess(argv, self.exit_codes.get(argv[-1], 0), "", "")

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def clock(self):
        return self.now

    def actuator(self):
        return entry.CorecapturedActuator(self.run, self.sleep, self.clock)


def setUpModule():
    # For the whole module the production sampler RAISES instead of running
    # `top -l 2 -s 30`.  An AssertionError is outside the families
    # `machine_quiet_check` converts into a refusal, so a stray call fails its
    # test loudly rather than sampling the machine or passing quietly.
    global _SAMPLER_GUARD, _CORE_GUARD
    from joulewise import night_gate
    _SAMPLER_GUARD = patch.object(night_gate, "production_interval_observation",
                                  _production_sampler_forbidden)
    _SAMPLER_GUARD.start()
    _CORE_GUARD = patch.object(entry, "production_corecaptured_actuator",
                               quiet_corecaptured_actuator)
    _CORE_GUARD.start()


def tearDownModule():
    _SAMPLER_GUARD.stop()
    _CORE_GUARD.stop()


class ProductionSamplerGuardTests(unittest.TestCase):
    def test_the_production_sampler_is_never_reached_from_this_module(self):
        # F12 (fix round 1): the module-level guard is in force for every
        # test here; the default observer path raises instead of sampling.
        with self.assertRaises(ProductionSamplerInvoked):
            entry.machine_quiet_check()


class ArgumentsTests(unittest.TestCase):
    def test_e3_boundary_check_documentation_agrees(self):
        clause = ("`publish-install` repeats the veto observation and the loaded-jobs probe "
                  "at the publication boundary and requires a fresh `check` record; "
                  "the lead re-runs `check` after any change.")
        for path in ("docs/contracts/evidence_night_entry.md", "docs/process/NIGHT_HANDBACK.md"):
            with self.subTest(path=path):
                self.assertIn(clause, (ROOT / path).read_text())

    def test_e4_contract_reserves_real_installed_outcome_for_bench(self):
        contract = " ".join((ROOT / "docs/contracts/evidence_night_entry.md").read_text().split())
        self.assertIn("A successful real-`launchctl` publication is exercised only at the bench's first live use", contract)
        self.assertIn("no fixture can prove `outcome: installed` with a real launchctl", contract)

    def test_lifecycle_contract_refusals_and_rehearsal_boundary(self):
        contract = (ROOT / "docs/contracts/evidence_night_entry.md").read_text()
        for refusal in ("unresolved raw census row", "malformed attempt journal",
                        "malformed attempt inventory", "installer ownership/rollback unknown"):
            self.assertIn(refusal, contract)
        definition = contract.split("`armable` means", 1)[1].split("Each successful subcommand", 1)[0]
        self.assertIn("rehearsal", definition)
        self.assertIn("`armable: false`", definition)

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
            # The bench step-1 probe lives in the builder (fix-forward after
            # PR #372: hosted 3.11 shards have no python3.13), so it is the
            # builder's first call, ahead of venv creation and the two installs.
            self.assertEqual(run.call_args_list[0].args[0], ["python3.13", "--version"])
            self.assertEqual(run.call_args_list[1].args[0], ["python3.13", "-m", "venv", ".venv"])
            self.assertEqual(run.call_args_list[2].args[0][-4:], ["-c", "env/mac-measurement-lock.txt", "-e", ".[mac]"])
            self.assertEqual(run.call_args_list[3].args[0][-3:], ["charset-normalizer", "requests", "urllib3"])
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
        transported = []
        original = subprocess.run
        def spy(argv, **kwargs):
            calls.append(list(map(str, argv)))
            if "-c" in argv and "write_night_plan" in argv[argv.index("-c") + 1]:
                self.assertEqual(len(argv), 4)
                transported.append(json.loads(kwargs["input"]))
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
        self.assertEqual(len(transported), 1)
        self.assertEqual(transported[0]["head"], first["head"])
        self.assertEqual(before, {p: (entry.digest(p), p.stat().st_mtime_ns) for p in files})
        self.assertEqual(authored, json.loads(Path(first["plan_path"]).read_text())["authored_epoch_s"])
        self.assertFalse((Path(first["custody_root"]) / "night_plan.json").exists())
        self.assertEqual(len(list((Path(first["staging"]) / "render").glob("*.plist"))), 3)
        self.assertTrue(any("scripts/gen_evidence_night.py" in c and "--render-only" in c for c in calls))
        self.assertTrue(any(c[0].endswith("/scripts/install_night_agent.sh") and "--render-only" in c for c in calls))
        self.assertIn("DRAFT — NOT SENT", first["notice_draft"])
        self.assertIn("At t0 the gate reads launchd's log for the previous ten minutes; when that read succeeds, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes. When the log cannot be read, the count is recorded as not measured and the night continues.", first["notice_draft"])
        self.assertIn("During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.", first["notice_draft"])
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

    def test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text(self):
        """QPE01-DAEMON-CONTAMINATION-01 regression 2, arm-check half.

        The 2026-09-22 arm passed every pre-arm check while `fseventsd` had
        already been at a full core for sixteen hours, because no check looked
        at what was running.  An arm that passes a machine t0 would refuse
        spends the whole three-hour span to learn it.  The bar, the text and
        the observation are the gate's, so the two can never drift apart.
        """

        from joulewise import night_gate
        from tests.test_night_gate import interval_observation
        from tests.test_arm_census import observation, row
        state = entry.prepare(**self.kw)
        resident = self.base_dir / "resident.json"
        entry.saved_json(resident, {"resident_session": None})

        def probes(argv, **kwargs):
            if Path(str(argv[0])).name == "pgrep":
                return subprocess.CompletedProcess(argv, 1, "", "")
            return entry.probe_command(argv, **kwargs)

        daemon = ("/System/Library/Frameworks/CoreServices.framework/Versions/A/"
                  "Frameworks/FSEvents.framework/Versions/A/Support/fseventsd", 341, 0.998)
        expected = ("non-observer process busy: fseventsd pid 341 at 0.998 busy cores "
                    "over 30.4 s (bar 0.5); observation in top_consumers_at_decision")
        absent = dict(jobs=[], plists=[], listing=dict(exit_code=0))
        for label, marked in (("the machine", False), ("the measurement itself", True)):
            with self.subTest(busy=label):
                busy = lambda: interval_observation(daemon + (marked,), interval_s=30.4)
                with patch.object(entry, "night_agents", return_value=absent, create=True):
                    if marked:
                        record = entry.check(
                            candidate=state["staging"], canonical=state["measurement_root"],
                            supervisor_state=resident, runner=probes, caller_pid=90,
                            census_observer=lambda **kw: observation(row(90, 1, "/bin/python3"), hits=()),
                            quiet_observer=busy, lock_verifier=lambda root: None)
                        self.assertEqual(record["checks"]["machine_quiet"]["verdict"], "pass")
                        self.assertEqual(
                            record["checks"]["machine_quiet"]["bar_busy_cores"],
                            night_gate.T0_NON_OBSERVER_SHARE_MAX)
                        continue
                    with self.assertRaises(entry.Refused) as refusal:
                        entry.check(
                            candidate=state["staging"], canonical=state["measurement_root"],
                            supervisor_state=resident, runner=probes, caller_pid=90,
                            census_observer=lambda **kw: observation(row(90, 1, "/bin/python3"), hits=()),
                            quiet_observer=busy, lock_verifier=lambda root: None)
                # The operator sees the finding itself, not "pre-arm checks failed".
                self.assertEqual(str(refusal.exception), expected)
                record = json.loads((Path(state["staging"]) / "lifecycle/check.json").read_text())
                self.assertFalse(record["armable"])
                self.assertFalse(record["rehearsal_ready"])
                # Fix round 1 (lens S4): the refusal text points at
                # top_consumers_at_decision, so the failing row carries it --
                # the observation the arm was refused on, naming the offender.
                failing = record["checks"]["machine_quiet"]
                self.assertEqual((failing["verdict"], failing["reason"]), ("fail", expected))
                self.assertEqual(failing["interval_s"], 30.4)
                self.assertEqual(failing["bar_busy_cores"], night_gate.T0_NON_OBSERVER_SHARE_MAX)
                self.assertEqual([(c["pid"], c["busy_cores"], c["observer"])
                                  for c in failing["top_consumers_at_decision"]],
                                 [(341, 0.998, False)])
                self.assertTrue(failing["top_consumers_at_decision"][0]["command"].endswith("/fseventsd"))

    def test_the_arm_check_records_an_unreadable_observation_as_not_armable(self):
        """Fix round 1 (lens S3): a failed or unreadable observation is a written refusal.

        At 16900e3d these three cases escaped `check()` as exceptions --
        `night_gate.ProbeError` is a RuntimeError, outside the families
        `inspect` records -- so check.json was never written and the operator
        got a traceback instead of `armable: false`.  The t0 gate already
        turns the same failures into `night_probe_error`.
        """

        from tests.test_night_gate import interval_observation
        from tests.test_arm_census import observation, row
        state = entry.prepare(**self.kw)
        resident = self.base_dir / "resident.json"
        entry.saved_json(resident, {"resident_session": None})

        def probes(argv, **kwargs):
            if Path(str(argv[0])).name == "pgrep":
                return subprocess.CompletedProcess(argv, 1, "", "")
            return entry.probe_command(argv, **kwargs)

        def sampler_died():
            raise RuntimeError("top died")

        cases = (
            ("malformed consumer", lambda: interval_observation(("/usr/libexec/somed", 77, 0.2, "yes")),
             "non-observer interval observation failed: ProbeError: "
             "malformed consumer in the non-observer observation"),
            ("sampler raises", sampler_died,
             "non-observer interval observation failed: RuntimeError: top died"),
            ("no metrics", lambda: {"interval_s": 30.4},
             "non-observer interval observation failed: ProbeError: "
             "non-observer observation carries no metrics"),
        )
        absent = dict(jobs=[], plists=[], listing=dict(exit_code=0))
        check_json = Path(state["staging"]) / "lifecycle/check.json"
        for label, observer, expected in cases:
            with self.subTest(case=label):
                if check_json.exists():
                    check_json.unlink()
                with patch.object(entry, "night_agents", return_value=absent, create=True):
                    with self.assertRaises(entry.Refused) as refusal:
                        entry.check(
                            candidate=state["staging"], canonical=state["measurement_root"],
                            supervisor_state=resident, runner=probes, caller_pid=90,
                            census_observer=lambda **kw: observation(row(90, 1, "/bin/python3"), hits=()),
                            quiet_observer=observer, lock_verifier=lambda root: None)
                self.assertEqual(str(refusal.exception), expected)
                record = json.loads(check_json.read_text())
                self.assertFalse(record["armable"])
                self.assertEqual(record["checks"]["machine_quiet"]["verdict"], "fail")
                self.assertEqual(record["checks"]["machine_quiet"]["reason"], expected)

    def test_b4_prepare_check_prepare(self):
        from tests.test_arm_census import observation, row
        state = entry.prepare(**self.kw)
        resident = self.base_dir / "resident.json"
        entry.saved_json(resident, {"resident_session": None})
        def probes(argv, **kwargs):
            if Path(str(argv[0])).name == "pgrep":
                return subprocess.CompletedProcess(argv, 1, "", "")
            return entry.probe_command(argv, **kwargs)
        absent = dict(jobs=[], plists=[], listing=dict(exit_code=0))
        with patch.object(entry, "night_agents", return_value=absent, create=True):
            entry.check(candidate=state["staging"], canonical=state["measurement_root"],
                supervisor_state=resident, runner=probes, caller_pid=90,
                census_observer=lambda **kw: observation(row(90, 1, "/bin/python3"), hits=()),
                quiet_observer=quiet_machine, lock_verifier=lambda root: None)
        self.assertEqual(entry.prepare(**self.kw), state)
        self.assertTrue((Path(state["staging"]) / "lifecycle/check.json").is_file())

    def test_prepare_refuses_root_attempt_output(self):
        state = entry.prepare(**self.kw)
        stage = Path(state["staging"])
        for name in ("attempts.json", "arm-attempts"):
            path = stage / name
            if name == "attempts.json":
                path.write_text("[]")
            else:
                path.mkdir()
            with self.subTest(name=name), self.assertRaisesRegex(
                    entry.Refused, "^unknown or uncheckpointed staging output$"):
                entry.prepare(**self.kw)
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()

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
        self.assertFalse(list(Path(self.kw["roots_under"]).glob("night-custody/measurement/JouleWise-measurement-*")))

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

    def test_sealed_registration_decisions_use_candidate_interpreter(self):
        state = entry.prepare(**self.kw)
        root = Path(state["measurement_root"])
        plan = Path(state["plan_path"])
        # The caller's import is intentionally wrong; H's interpreter still
        # accepts the current registration.
        with patch.object(night_gate, "armable_registration", return_value=None):
            self.assertEqual(entry.sealed_candidate(root, plan)["registration_sha256"],
                             night_gate.QPE01_PILOT_REGISTRATION_SHA256)

        original = json.loads(plan.read_text())
        altered = plan.with_name("registration-test-plan.json")
        cases = ((str(root / "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json"),
                  "registration current digest"),)
        for registration, refusal in cases:
            with self.subTest(refusal=refusal):
                altered.write_text(json.dumps(dict(original, registration_path=registration)))
                with self.assertRaisesRegex(entry.Refused, "sealed candidate failed " + refusal):
                    entry.sealed_candidate(root, altered)

        unknown = self.base_dir / "unruled.json"
        unknown.write_bytes((root / night_gate.QPE01_PILOT_REGISTRATION_PATH).read_bytes() + b" ")
        altered.write_text(json.dumps(dict(original, registration_path=str(unknown))))
        with self.assertRaisesRegex(entry.Refused, "sealed candidate failed registration ruled digest"):
            entry.sealed_candidate(root, altered)

        real_run = entry.run
        def H_with_superseded_current(argv, **kwargs):
            if len(argv) >= 4 and argv[2] == "-c" and "registration armability" in argv[3]:
                argv = list(argv)
                argv[3] = argv[3].replace(
                    "from joulewise import night_gate\n",
                    "from joulewise import night_gate\nnight_gate.armable_registration=lambda sha: None\n")
            return real_run(argv, **kwargs)
        with patch.object(entry, "run", side_effect=H_with_superseded_current):
            with self.assertRaisesRegex(entry.Refused, "sealed candidate failed registration armability"):
                entry.sealed_candidate(root, plan)

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

    def test_prepare_path_needs_no_python313_and_warns_on_short_runway(self):
        self.kw["t0"] = str((int(time.time()) // 60 + 30) * 60)
        calls = []; original = entry.run; errors = io.StringIO()
        def spy(argv, **kwargs):
            calls.append(list(map(str, argv)))
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=spy), contextlib.redirect_stderr(errors):
            entry.prepare(**self.kw)
        self.assertIn("WARNING: runway below the 40-minute planning default", errors.getvalue())
        # No python3.13 probe on the prepare path itself: with an injected
        # builder the host needs no python3.13 (hosted 3.11 shards have none).
        self.assertNotIn(["python3.13", "--version"], calls)
        fetch = next(i for i, c in enumerate(calls) if "fetch" in c)
        ancestry = next(i for i, c in enumerate(calls) if "merge-base" in c)
        self.assertLess(fetch, ancestry)
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


def enable_fake_list(fake):
    """Extend the existing fake only in this fixture; no real launchctl."""
    source = fake.executable.read_text()
    source = source.replace('action = args[0]', """action = args[0]
if action == 'list':
    print('PID\tStatus\tLabel')
    for marker in sorted(root.glob('*.loaded')):
        print('-\t0\t' + marker.name[:-7])
    sys.exit(0)""")
    fake.executable.write_text(source)


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
        (self.canonical / "joulewise").mkdir()
        (self.canonical / "joulewise/__init__.py").write_text("")
        for name in ("night_gate.py", "night_kinds.py", "corecaptured_loop.py", "arm_census.py", "arm_retry.py", "quiet_guard_process.py", "night_agent_install.py"):
            shutil.copy2(ROOT / "joulewise" / name, self.canonical / "joulewise" / name)
        clone_route = {"test_retry_uses_clone_retry_route": "retry",
                       "test_retry_uses_clone_cold_gate_route": "cold_gate"}.get(self._testMethodName)
        if clone_route:
            retry = self.canonical / "joulewise/arm_retry.py"
            retry.write_text(retry.read_text() + f"\ndef classify_abort(cause):\n    return {clone_route!r}\n")
        if self._testMethodName == "test_b6_clone_old_census_literal_is_reported":
            gate = self.canonical / "joulewise/night_gate.py"
            gate.write_text(gate.read_text().replace("[c]odex|[c]laude|[t]3", "codex|claude|t3"))
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
        PrepareTests.fake_builder(self.root)
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
        self.absent_agents = dict(jobs=[dict(label=label, liveness="ABSENT") for label in
            ("com.joulewise.night", "com.joulewise.night.deadman")], plists=[], listing=dict(exit_code=0))
        self.agent_probe = patch.object(entry, "night_agents", return_value=self.absent_agents, create=True)
        self.agent_probe.start()
        self.addCleanup(self.agent_probe.stop)
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
                       lock_verifier=lambda root: None, launchctl_bin="/fixture/launchctl",
                       quiet_observer=quiet_machine)
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

    def sibling_plan(self, root, *, t0=None, custody_root=None):
        # A parseable v2 plan for a sibling custody root; ten days old by default,
        # so the watchdog's span rule reads it as long over.
        t0 = (int(time.time()) // 60 - 60 * 24 * 10) * 60 if t0 is None else t0
        return dict(schema="joulewise.night_plan.v2", schema_version=2, plan_id=root.name,
                    receipt_class="DIAGNOSTIC_NO_PACK", t0_epoch_s=float(t0), window_max_s=9000,
                    authored_epoch_s=float(t0 - 3600), repo_head=self.head, chain_path="chain.zsh",
                    chain_sha256_path="chain.zsh.sha256",
                    custody_root=str(root) if custody_root is None else custody_root,
                    measurement_head=self.head, measurement_root=str(self.root),
                    registration_path="docs/registration.md")

    def sibling_root(self, name, *markers, t0=None, custody_root=None, plan_text=None):
        root = self.custody.parent / name
        (root / "night").mkdir(parents=True)
        for marker in markers:
            (root / "night" / marker).write_text("{}")
        if plan_text is None:
            plan_text = json.dumps(self.sibling_plan(root, t0=t0, custody_root=custody_root))
        (root / "night_plan.json").write_text(plan_text)
        return root

    def checked(self, fail=None):
        if fail:
            with self.assertRaisesRegex(entry.Refused, fail):
                entry.check(**self.kw)
            return json.loads((self.stage / "lifecycle/check.json").read_text())
        return entry.check(**self.kw)

    def test_check_passes_and_writes_only_check_json(self):
        def snapshot():
            return {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.base.rglob("*") if p.is_file()}
        before = snapshot()
        record = self.checked()
        after = snapshot()
        self.assertTrue(record["rehearsal_ready"])
        self.assertEqual(set(after) - set(before), {str(self.stage / "lifecycle/check.json"),
            str(self.stage.parent / ".locks" / (self.stage.name + ".lock"))})
        self.assertEqual(before, {p: after[p] for p in before})
        self.assertEqual(record["checks"]["census"]["argv"][-1], "[c]odex|[c]laude|[t]3")
        self.assertIn(20, record["checks"]["census"]["owned_helpers"])
        self.assertFalse(any("launchctl" in str(c) for c in self.calls))

    def test_corecaptured_arm_toggles_once_and_counts_only_post_toggle_spawns(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:11]) + "\n"  # five real spawn rows
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, before, now)
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            record = entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = record["checks"]["corecaptured"]
        self.assertEqual(row["last_10m_spawns"], 5)
        self.assertEqual(row["post_toggle_spawns"], 0)
        self.assertEqual(row["remediation"], "wifi_toggled_once")
        self.assertEqual(fake.sleeps, [8, 180])
        self.assertEqual(sum(argv[-1] == "off" for argv in fake.commands), 1)
        self.assertEqual(sum(argv[-1] == "on" for argv in fake.commands), 1)
        self.assertEqual(sum(argv[0] == "/usr/bin/sudo" for argv in fake.commands), 0)
        self.assertEqual(fake.commands.count(corecaptured_loop.LOG_ARGV), 2)

    def test_corecaptured_arm_zero_spawns_does_not_toggle(self):
        quiet = (ROOT / "tests/fixtures/corecaptured/quiet-header-only.log").read_text()
        fake = FakeCorecapturedActuator(quiet, quiet, time.time())
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            record = entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        self.assertEqual(record["checks"]["corecaptured"]["last_10m_spawns"], 0)
        self.assertEqual(fake.commands, [corecaptured_loop.LOG_ARGV])
        self.assertEqual(fake.sleeps, [])

    def test_corecaptured_arm_threshold_is_three_spawns(self):
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        raw = "Timestamp                       (process)[PID]\n"
        for i, offset in enumerate((-590, -300, -1), 1):
            stamp = datetime.fromtimestamp(now + offset).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z")
            raw += (f"{stamp}  localhost launchd[1]: [system/com.apple.corecaptured [{i}]:] "
                    f"Successfully spawned corecaptured[{i}] because xpc event\n")
            if i in (2, 3):
                fake = FakeCorecapturedActuator(raw, raw, now)
                with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
                    record = entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
                self.assertEqual(record["checks"]["corecaptured"]["last_10m_spawns"], i)
                self.assertEqual(sum(argv[-1] == "off" for argv in fake.commands), i == 3)

    def test_corecaptured_arm_window_anchors_before_slow_log_read(self):
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        raw = "Timestamp                       (process)[PID]\n"
        for i, offset in enumerate((-590, -300, 10), 1):
            stamp = datetime.fromtimestamp(now + offset).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z")
            raw += (f"{stamp}  localhost launchd[1]: [system/com.apple.corecaptured [{i}]:] "
                    f"Successfully spawned corecaptured[{i}] because xpc event\n")
        fake = FakeCorecapturedActuator(raw, raw, now, log_delay_s=30)
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            record = entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        self.assertEqual(record["checks"]["corecaptured"]["last_10m_spawns"], 3)
        self.assertEqual(sum(argv[-1] == "off" for argv in fake.commands), 1)

    def test_corecaptured_rehearsal_never_actuates_production_machine(self):
        # Counter-review S-1: a fixture launchctl decides "nothing loaded" in a
        # rehearsal, so the production actuator must stay read-only.
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        fake = FakeCorecapturedActuator(raw, raw, now)
        self.assertNotEqual(self.kw["launchctl_bin"], "launchctl")
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND), \
                patch.object(entry, "production_corecaptured_actuator", return_value=fake.actuator()):
            with self.assertRaisesRegex(entry.Refused, "not licensed"):
                entry.check(**self.kw)
        self.assertFalse(any(argv[0] in ("/usr/sbin/networksetup", "/usr/bin/sudo")
                             for argv in fake.commands))

    def test_corecaptured_arm_backward_clock_refuses_without_actuation(self):
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        fake = FakeCorecapturedActuator(raw, raw, now, log_delay_s=-3600)
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "backward"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        self.assertFalse(any(argv[0] in ("/usr/sbin/networksetup", "/usr/bin/sudo")
                             for argv in fake.commands))

    def test_corecaptured_timed_out_move_is_recorded_without_exit_code(self):
        # Delta re-audit A271 F2: a move that raised has no exit code; the
        # attempted command and its exception must still be on the record.
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator("\n".join(raw.splitlines()[:11]) + "\n", raw, now)
        original = fake.run

        def timeout_off(argv, *, timeout=None):
            if argv[-1] == "off":
                fake.commands.append(tuple(argv))
                raise subprocess.TimeoutExpired(argv, timeout)
            return original(argv, timeout=timeout)

        fake.run = timeout_off
        with self.assertRaises(entry.Refused) as caught:
            entry.corecaptured_arm_check(fake.actuator())
        errors = caught.exception.evidence["command_errors"]
        self.assertIn("TimeoutExpired", errors["Wi-Fi off"])
        self.assertNotIn("wifi_off_exit_code", caught.exception.evidence)
        self.assertEqual(caught.exception.evidence["wifi_on_exit_code"], 0)

    def test_corecaptured_arm_off_timeout_restores_wifi_and_refuses(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator("\n".join(raw.splitlines()[:11]) + "\n", raw, now)
        original = fake.run

        def timeout_off(argv, *, timeout=None):
            if argv[-1] == "off":
                fake.commands.append(tuple(argv))
                fake.timeouts.append(timeout)
                raise subprocess.TimeoutExpired(argv, timeout)
            return original(argv, timeout=timeout)

        fake.run = timeout_off
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "Wi-Fi toggle failed"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["verdict"], "fail")
        self.assertEqual([argv[-1] for argv in fake.commands if "networksetup" in argv[0]], ["off", "on"])
        self.assertEqual(fake.timeouts, [30, 30, 30])

    def test_corecaptured_arm_wait_timeout_restores_wifi(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator("\n".join(raw.splitlines()[:11]) + "\n", raw, now)

        def timeout_wait(seconds):
            raise subprocess.TimeoutExpired("Wi-Fi settle", seconds)

        actuator = entry.CorecapturedActuator(fake.run, timeout_wait, fake.clock)
        with self.assertRaisesRegex(entry.Refused, "Wi-Fi toggle failed"):
            entry.corecaptured_arm_check(actuator)
        self.assertEqual([argv[-1] for argv in fake.commands if "networksetup" in argv[0]], ["off", "on"])

    def test_corecaptured_arm_on_timeout_names_failed_restore(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator("\n".join(raw.splitlines()[:11]) + "\n", raw, now)
        original = fake.run

        def timeout_on(argv, *, timeout=None):
            if argv[-1] == "on":
                fake.commands.append(tuple(argv))
                fake.timeouts.append(timeout)
                raise subprocess.TimeoutExpired(argv, timeout)
            return original(argv, timeout=timeout)

        fake.run = timeout_on
        with self.assertRaisesRegex(entry.Refused, "Wi-Fi on failed: TimeoutExpired"):
            entry.corecaptured_arm_check(fake.actuator())
        self.assertEqual(fake.timeouts, [30, 30, 30])

    def test_corecaptured_arm_commands_have_bounded_timeouts(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator("\n".join(raw.splitlines()[:11]) + "\n", raw, now)
        with self.assertRaisesRegex(entry.Refused, "fseventsd restart exit"):
            entry.corecaptured_arm_check(fake.actuator())
        self.assertEqual(fake.timeouts, [30, 30, 30, 30, 60])

    def test_corecaptured_one_new_spawn_after_toggle_refuses(self):
        now = datetime.fromisoformat("2026-09-22 10:42:21-07:00").timestamp()
        raw = "Timestamp                       (process)[PID]\n"
        for i, offset in enumerate((-300, -150, -1), 1):
            stamp = datetime.fromtimestamp(now + offset).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z")
            raw += (f"{stamp}  localhost launchd[1]: [system/com.apple.corecaptured [{i}]:] "
                    f"Successfully spawned corecaptured[{i}] because xpc event\n")
        stamp = datetime.fromtimestamp(now + 95).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z")
        after = (raw + f"{stamp}  localhost launchd[1]: [system/com.apple.corecaptured [4]:] "
                 "Successfully spawned corecaptured[4] because xpc event\n")
        fake = FakeCorecapturedActuator(raw, after, now)
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "1 new spawns after toggle"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        self.assertEqual(sum(argv[0] == "/usr/bin/sudo" for argv in fake.commands), 1)

    def test_loaded_night_agent_makes_corecaptured_read_only(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:11]) + "\n"
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, before, now)
        loaded = dict(self.absent_agents, jobs=[dict(label="com.joulewise.night", liveness="LOADED")])
        with patch.object(entry, "night_agents", return_value=loaded), \
             patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "night agents already loaded"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["verdict"], "fail")
        self.assertEqual(row["last_10m_spawns"], 5)
        self.assertEqual(row["remediation"], "not_licensed")
        self.assertIn("earlier check failed", row["reason"])
        self.assertEqual(fake.commands, [corecaptured_loop.LOG_ARGV])

    def test_failed_census_makes_corecaptured_read_only(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:11]) + "\n"
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, before, now)
        with patch.object(entry, "census_check", side_effect=entry.Refused("census failed")), \
             patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "census failed"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["verdict"], "fail")
        self.assertEqual(row["last_10m_spawns"], 5)
        self.assertEqual(row["remediation"], "not_licensed")
        self.assertIn("earlier check failed", row["reason"])
        self.assertEqual(fake.commands, [corecaptured_loop.LOG_ARGV])

    def test_failed_census_read_only_count_of_two_passes_without_actuation(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:5]) + "\n"
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, before, now)
        with patch.object(entry, "census_check", side_effect=entry.Refused("census failed")), \
             patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "census failed"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["verdict"], "pass")
        self.assertEqual(row["last_10m_spawns"], 2)
        self.assertEqual(row["remediation"], "not_licensed")
        self.assertEqual(fake.commands, [corecaptured_loop.LOG_ARGV])

    def test_corecaptured_arm_persistence_restarts_once_and_refuses(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:11]) + "\n"
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, raw, now)
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "night_refused_not_quiet: corecaptured"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["post_toggle_spawns"], 2)
        self.assertEqual(row["fseventsd_restart_exit_code"], 0)
        self.assertEqual(sum("networksetup" in argv[0] and argv[-1] == "off"
                             for argv in fake.commands), 1)
        self.assertEqual(sum("networksetup" in argv[0] and argv[-1] == "on"
                             for argv in fake.commands), 1)
        self.assertEqual(sum(argv[0] == "/usr/bin/sudo" for argv in fake.commands), 1)

    def test_corecaptured_arm_restores_wifi_if_off_command_fails(self):
        raw = (ROOT / "tests/fixtures/corecaptured/loop-20260922-1022.log").read_text()
        before = "\n".join(raw.splitlines()[:11]) + "\n"
        now = datetime.fromisoformat("2026-09-22 10:29:00-07:00").timestamp()
        fake = FakeCorecapturedActuator(before, before, now, exit_codes={"off": 1})
        with patch.object(entry, "candidate_payload_kind", return_value=entry.KIND):
            with self.assertRaisesRegex(entry.Refused, "corecaptured: 5 spawns"):
                entry.check(**dict(self.kw, corecaptured_actuator=fake.actuator()))
        row = json.loads((self.stage / "lifecycle/check.json").read_text())["checks"]["corecaptured"]
        self.assertEqual(row["wifi_off_exit_code"], 1)
        self.assertEqual(row["wifi_on_exit_code"], 0)
        self.assertEqual(fake.sleeps, [])
        self.assertEqual(sum(argv[-1] == "off" for argv in fake.commands), 1)
        self.assertEqual(sum(argv[-1] == "on" for argv in fake.commands), 1)

    def test_sealed_bytes_checked_before_host_probes(self):
        self.plan.write_bytes(self.plan.read_bytes() + b" ")
        record = self.checked("sealed")
        self.assertEqual(list(record["checks"]), ["sealed"])
        self.assertFalse(self.calls)

    def test_canonical_must_contain_h_and_be_clean(self):
        (self.canonical / "tracked").write_text("dirty")
        self.assertFalse(self.checked("canonical")["armable"])
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        # Behind H with no upstream: the fast-forward attempt refuses, nothing moves.
        reason = self.checked("canonical")["checks"]["canonical"]["reason"]
        self.assertIn("fast-forward failed", reason)
        self.assertEqual(self.canonical_head(), self.old)
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.tip], check=True)
        (self.canonical / "untracked").write_text("irrelevant")
        self.assertTrue(self.checked()["rehearsal_ready"])
        self.assertTrue(any(c[-4:] == ["--no-optional-locks", "status", "--porcelain", "-uno"] for c in self.calls))

    def canonical_head(self):
        return subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "HEAD"], text=True).strip()

    def give_canonical_upstream(self):
        bare = self.base / "upstream.git"
        subprocess.run(["git", "clone", "-q", "--bare", str(self.canonical), str(bare)], check=True)
        branch = subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "--abbrev-ref", "HEAD"],
                                         text=True).strip()
        subprocess.run(["git", "-C", str(self.canonical), "remote", "add", "origin", str(bare)], check=True)
        subprocess.run(["git", "-C", str(self.canonical), "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", str(self.canonical), "branch", "-q", "--set-upstream-to=origin/" + branch],
                       check=True)
        return bare

    def test_canonical_fast_forwards_itself_when_nothing_is_loaded(self):
        # D-183: a clean canonical checkout behind H is moved by check itself.
        self.give_canonical_upstream()
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        record = self.checked()
        self.assertTrue(record["rehearsal_ready"])
        moved = record["checks"]["canonical"]["fast_forward"]
        self.assertEqual((moved["before"], moved["after"]), (self.old, self.tip))
        self.assertEqual(moved["pull"]["exit_code"], 0)
        self.assertEqual(self.canonical_head(), self.tip)
        self.assertTrue(any(c[-2:] == ["pull", "--ff-only"] and str(self.canonical) in c for c in self.calls))
        # Already containing H: no pull is attempted.
        self.calls.clear()
        self.assertIsNone(self.checked()["checks"]["canonical"]["fast_forward"])
        self.assertFalse(any("pull" in c for c in self.calls))

    def test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence(self):
        bare = self.give_canonical_upstream()
        # The upstream branch advances WITHOUT the fix: old -> other.
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        other = self.commit("other", self.arrival + 200)
        branch = subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "--abbrev-ref", "HEAD"],
                                         text=True).strip()
        subprocess.run(["git", "-C", str(self.canonical), "push", "-q", "-f", "origin", f"HEAD:{branch}"], check=True)
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        reason = self.checked("canonical")["checks"]["canonical"]["reason"]
        self.assertIn("canonical fast-forward failed: HEAD moved " + self.old + " -> " + other, reason)
        self.assertIn("still does not contain candidate H", reason)
        self.assertEqual(self.canonical_head(), other)
        self.assertIn(str(bare), subprocess.check_output(["git", "-C", str(self.canonical), "remote", "-v"], text=True))

    def test_canonical_fast_forward_is_bounded_and_prompt_free(self):
        self.give_canonical_upstream()
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        seen = {}

        def runner(argv, **kwargs):
            if list(map(str, argv))[-2:] == ["pull", "--ff-only"]:
                seen.update(kwargs)
                raise subprocess.TimeoutExpired(argv, kwargs.get("timeout"))
            return self.runner(argv, **kwargs)
        with patch.dict(self.kw, runner=runner):
            record = self.checked("canonical")
        self.assertEqual(seen, dict(timeout=entry.FAST_FORWARD_TIMEOUT_S, env={"GIT_TERMINAL_PROMPT": "0"}))
        self.assertEqual(self.canonical_head(), self.old)
        self.assertIn("timed out", record["checks"]["canonical"]["reason"])

    def test_fast_forward_makes_the_resident_supervisor_stale_and_says_so(self):
        # Records 19/21 after an in-check move: the session's own supervisor predates
        # the arrival of H and the refusal names the hand-off (D-183).
        self.give_canonical_upstream()
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        self.live_supervisor(self.arrival + 50)
        record = self.checked("stale resident supervisor pid 42")
        self.assertEqual(self.canonical_head(), self.tip)
        self.assertEqual(record["checks"]["canonical"]["verdict"], "pass")
        reason = record["checks"]["supervisor"]["reason"]
        self.assertIn("exit so the watchdog's successor arms", reason)
        self.assertGreaterEqual(record["checks"]["supervisor"].get("head_arrived_epoch_s", 0) or 0, 0)
        # A supervisor started after the move passes.
        self.live_supervisor(time.time() + 5)
        self.assertTrue(self.checked()["rehearsal_ready"])

    def test_canonical_fast_forward_refuses_dirty_tree_and_loaded_agents(self):
        self.give_canonical_upstream()
        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
        (self.canonical / "tracked").write_text("dirty")
        self.assertIn("dirty", self.checked("canonical")["checks"]["canonical"]["reason"])
        self.assertEqual(self.canonical_head(), self.old)
        subprocess.run(["git", "-C", str(self.canonical), "checkout", "-q", "--", "tracked"], check=True)
        loaded = dict(self.absent_agents, jobs=[dict(label="com.joulewise.night", liveness="LOADED"),
                                                dict(label="com.joulewise.night.deadman", liveness="ABSENT")])
        with patch.object(entry, "night_agents", return_value=loaded):
            record = self.checked("night agents already loaded")
        self.assertIn("not licensed while night agents are loaded", record["checks"]["canonical"]["reason"])
        self.assertEqual(self.canonical_head(), self.old)
        self.assertFalse(any("pull" in c for c in self.calls))

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
        self.assertTrue(self.checked()["rehearsal_ready"])
        self.ps = subprocess.CompletedProcess([], 1, "", "")
        self.assertTrue(self.checked()["rehearsal_ready"])
        self.ps = subprocess.CompletedProcess([], 2, "", "unreadable")
        self.checked("supervisor")
        entry.saved_json(self.resident, {"resident_session": {"supervisor_pid": True}})
        self.checked("supervisor")

    def test_courier_unavailable(self):
        with patch.object(entry.shutil, "which", return_value=None):
            self.checked("courier")

    def test_discovery_retains_every_harvested_root_and_refuses_unknown(self):
        markers = ("courier.sent", "result.json", "chain.exited", "refusal.json", "refusal-2.json",
                   "calibration-refusal.json", "calibration-refusal.json.1789617139.json", None)
        for i, marker in enumerate(markers):
            self.sibling_root(f"prior-{i}", *([marker] if marker else []))
        result = self.checked("retained_roots")["checks"]["retained_roots"]
        self.assertEqual([r["classification"] for r in result["inventory"]],
                         ["retained"] * (len(markers) - 1) + ["UNKNOWN"])
        self.assertEqual([r["evidence"] for r in result["inventory"]],
                         [[str(self.custody.parent / f"prior-{i}/night/{m}")] for i, m in enumerate(markers[:-1])] + [[]])
        self.assertEqual(result["inventory"][-1]["reason"], "no terminal night record")
        root = self.custody.parent / f"prior-{len(markers) - 1}"
        self.assertTrue((root / "night_plan.json").exists())
        (root / "night/result.json").write_text("{}")
        self.assertTrue(self.checked()["rehearsal_ready"])

    def test_discovery_refuses_an_open_chain_and_ignores_non_marker_records(self):
        # A refused night whose chain was killed: refusal.json + chain.started + chain.exited
        # (the 2026-09-16 root's shape) is retained; the same root before chain.exited is ACTIVE.
        root = self.sibling_root("refused", "refusal.json", "chain.started", "receipt.json", "censuses.jsonl")
        result = self.checked("retained_roots")["checks"]["retained_roots"]
        self.assertEqual([(r["classification"], r["reason"]) for r in result["inventory"]],
                         [("ACTIVE", "chain.started without chain.exited")])
        (root / "night/chain.exited").write_text('{"exit_code": -15}')
        result = self.checked()["checks"]["retained_roots"]
        self.assertEqual([(r["classification"], r["reason"]) for r in result["inventory"]],
                         [("retained", "terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)")])
        self.assertEqual(result["inventory"][0]["evidence"],
                         [str(root / "night/chain.exited"), str(root / "night/refusal.json")])
        # An open chain stays ACTIVE even when a courier marker exists.
        (root / "night/chain.exited").unlink()
        (root / "night/courier.sent").write_text("{}")
        self.assertEqual(self.checked("retained_roots")["checks"]["retained_roots"]["inventory"][0]["classification"], "ACTIVE")
        # Receipt-only and stray-file roots are unknown.
        for name in ("courier.sent", "chain.started", "refusal.json"):
            (root / "night" / name).unlink()
        self.assertEqual(self.checked("retained_roots")["checks"]["retained_roots"]["inventory"][0]["classification"], "UNKNOWN")

    def test_retained_root_classification_ruled_cases(self):
        # Cold-gate ruling 2026-09-21 (packet 05, Q4): active is tested before retained.
        cases = [
            (("refusal.json",), "retained"), (("chain.exited",), "retained"),
            (("refusal-3.json",), "retained"), (("calibration-refusal.json.2.json",), "retained"),
            (("chain.started",), "ACTIVE"),
            (("chain.started", "calibration-refusal.json"), "ACTIVE"),
            (("chain.started", "chain.exited"), "retained"),
            ((), "UNKNOWN"),
        ]
        state = {"roots_under": str(self.custody.parent.parent)}
        for i, (names, expected) in enumerate(cases):
            self.sibling_root(f"case-{i}", *names)
        # A refusal record that is a directory does not count.
        root = self.sibling_root("case-dir")
        (root / "night/refusal.json").mkdir()
        result = entry.retained_roots(state)
        by_name = {Path(r["plan"]).parent.name: r for r in result["inventory"]}
        for i, (names, expected) in enumerate(cases):
            with self.subTest(names=names):
                row = by_name[f"case-{i}"]
                self.assertEqual(row["classification"], expected)
                self.assertEqual(row["evidence"], [str(self.custody.parent / f"case-{i}/night/{n}")
                                                   for n in sorted(names) if n != "chain.started"])
        self.assertEqual((by_name["case-dir"]["classification"], by_name["case-dir"]["evidence"]), ("UNKNOWN", []))
        self.assertEqual(result["verdict"], "fail")
        # Through the check: an ACTIVE root alone refuses naming retained_roots.
        for name in list(by_name):
            if name != "case-4":
                shutil.rmtree(self.custody.parent / name)
        with self.assertRaisesRegex(entry.Refused, "retained_roots"):
            entry.check(**self.kw)
        # A refusal-only root alone passes, with the complete evidence path (ruled case 1).
        shutil.rmtree(self.custody.parent / "case-4")
        only = self.sibling_root("refusal-only", "refusal.json")
        record = self.checked()
        self.assertTrue(record["rehearsal_ready"])
        self.assertEqual(record["checks"]["retained_roots"]["inventory"],
                         [dict(plan=str(only / "night_plan.json"), classification="retained",
                               reason="terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)",
                               evidence=[str(only / "night/refusal.json")])])

    def test_a_root_recorded_under_the_superseded_v2_registration_stays_retained(self):
        """Brief 04 regression 4, third limb -- a GUARD, not defect-shaped.

        Superseding v2 by v3 must not orphan the nights already recorded
        under v2: their custody roots must still classify `retained`, or the
        next arm check would refuse on history.  This holds by construction
        today (`retained_roots` reads terminal markers, the custody path and
        the plan span, never the registration digest), so the test cannot
        fail on 16900e3d; it exists so a future change that makes retention
        read the registration cannot land silently (lens S6, fix round 1).
        """

        import hashlib
        from joulewise import night_gate
        state = {"roots_under": str(self.custody.parent.parent)}
        v2 = (ROOT / "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json").read_bytes()
        self.assertEqual(hashlib.sha256(v2).hexdigest(), night_gate.QPE01_PILOT_REGISTRATION_V2_SHA256)
        self.assertIsNone(night_gate.armable_registration(night_gate.QPE01_PILOT_REGISTRATION_V2_SHA256))
        root = self.custody.parent / "under-v2"
        (root / "night").mkdir(parents=True)
        (root / "registration.json").write_bytes(v2)
        plan = dict(self.sibling_plan(root), registration_path=str(root / "registration.json"))
        (root / "night_plan.json").write_text(json.dumps(plan))
        for marker in ("chain.started", "chain.exited", "refusal.json"):
            (root / "night" / marker).write_text("{}")
        (root / "night/receipt.json").write_text(json.dumps({"rows": [{"id": "C1", "measured": {
            "registration_sha256": night_gate.QPE01_PILOT_REGISTRATION_V2_SHA256}}]}))
        row = entry.retained_roots(state)["inventory"][0]
        self.assertEqual((row["plan"], row["classification"]),
                         (str(root / "night_plan.json"), "retained"))
        record = entry.check(**dict(self.kw, quiet_observer=quiet_machine))
        self.assertEqual(record["checks"]["retained_roots"]["verdict"], "pass")
        self.assertEqual([r["classification"] for r in record["checks"]["retained_roots"]["inventory"]],
                         ["retained"])

    def evidence_chain(self, text="#!/bin/zsh\nexport NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n"):
        """Re-seal the fixture's custody chain with `text` (digest updated)."""

        chain = self.custody / "chain.zsh"
        chain.write_text(text)
        self.state["digests"][str(chain)] = entry.digest(chain)
        entry.saved_json(self.stage / "prepare.json", self.state)

    def test_the_arm_check_spends_the_predicate_only_on_an_evidence_chain(self):
        """F12 (fix round 1): the arm check's scope mirrors the t0 gate's.

        The gate spends the 30 s observation only when the chain's payload
        kind is `quiet_predicate_evidence` (night_gate, the C5 payload_kind
        condition).  At 16900e3d the arm check spent it for every candidate.
        The fixture's sealed chain declares no payload kind, which the gate
        reads as calibration.
        """

        calls = []

        def spy():
            calls.append("observed")
            return quiet_machine()

        record = entry.check(**dict(self.kw, quiet_observer=spy))
        self.assertEqual(calls, [])
        self.assertEqual(record["checks"]["machine_quiet"],
                         dict(verdict="skipped", reason="not an evidence night", payload_kind="calibration"))
        self.assertTrue(record["rehearsal_ready"])
        written = json.loads((self.stage / "lifecycle/check.json").read_text())
        self.assertEqual(written["checks"]["machine_quiet"]["verdict"], "skipped")
        # The same candidate with an evidence chain: the observer is spent once.
        self.evidence_chain()
        record = entry.check(**dict(self.kw, quiet_observer=spy))
        self.assertEqual(calls, ["observed"])
        self.assertEqual(record["checks"]["machine_quiet"]["verdict"], "pass")
        self.assertTrue(record["rehearsal_ready"])
        # The module guard: with no injected observer, the check reaches the
        # production sampler, which raises here instead of sampling.
        with self.assertRaises(ProductionSamplerInvoked):
            entry.check(**{k: v for k, v in self.kw.items() if k != "quiet_observer"})

    def test_the_generic_refusal_names_only_failed_checks_never_a_skipped_one(self):
        """Fix round 2, delta re-audit N-b.

        A candidate whose chain is not an evidence night records
        `machine_quiet: skipped`, which `passed` already treats as no
        failure.  At 0e5578fb the generic refusal text listed every check
        whose verdict was not "pass", so when the courier failed the operator
        read "pre-arm checks failed: courier, machine_quiet" -- naming a check
        that never ran as failed.  Counterfactual: courier fails, machine
        quiet is skipped; the text must name the courier alone.
        """

        with patch.object(entry.shutil, "which", return_value=None):
            with self.assertRaises(entry.Refused) as refused:
                entry.check(**self.kw)
        written = json.loads((self.stage / "lifecycle/check.json").read_text())
        self.assertEqual(written["checks"]["machine_quiet"]["verdict"], "skipped")
        self.assertEqual(written["checks"]["courier"]["verdict"], "fail")
        message = str(refused.exception)
        self.assertTrue(message.startswith("pre-arm checks failed: courier; see "), message)
        self.assertNotIn("machine_quiet", message)

    def test_an_unreadable_payload_kind_fails_the_arm_check_closed(self):
        # Two declarations: the gate's probe calls the kind ambiguous; the
        # arm check refuses rather than guessing either scope.
        self.evidence_chain("export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n"
                            "export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n")
        record = self.checked("payload kind unreadable")
        self.assertEqual(record["checks"]["machine_quiet"]["verdict"], "fail")
        self.assertFalse(record["armable"])

    def test_discovery_span_fence_reuses_the_watchdog_rule(self):
        from scripts.magistrate_watchdog import COURIER_DEADLINE_S
        state = {"roots_under": str(self.custody.parent.parent)}
        t0 = 1_800_000_000
        root = self.sibling_root("span", "chain.started", "chain.exited", t0=t0)
        # Inside t0 + window + courier deadline: ACTIVE even though the chain exited.
        row = entry.retained_roots(state, now_epoch_s=t0 + 600)["inventory"][0]
        self.assertEqual((row["classification"], row["reason"]),
                         ("ACTIVE", "plan span active (scripts/magistrate_watchdog.plan_span_active)"))
        # Still inside the completion interval with courier.sent: the watchdog keeps the span active.
        (root / "night/courier.sent").write_text("{}")
        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S - 1)["inventory"][0]["classification"], "ACTIVE")
        # After the completion interval, courier.sent closes the span.
        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S + 1)["inventory"][0]["classification"], "retained")
        # Without courier.sent the span runs to the dead-man plus the courier-lock freshness window.
        (root / "night/courier.sent").unlink()
        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S + 1)["inventory"][0]["classification"], "ACTIVE")
        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 30 * 86400)["inventory"][0]["classification"], "retained")
        # A plan whose custody_root is not its own directory, or that cannot be parsed, is UNKNOWN.
        shutil.rmtree(root)
        self.sibling_root("moved", "courier.sent", custody_root="/Users/nobody/night-custody/moved")
        row = entry.retained_roots(state)["inventory"][0]
        self.assertEqual(row["classification"], "UNKNOWN"); self.assertIn("custody_root", row["reason"])
        shutil.rmtree(self.custody.parent / "moved")
        self.sibling_root("bare", "courier.sent", plan_text="{}")
        row = entry.retained_roots(state)["inventory"][0]
        self.assertEqual(row["classification"], "UNKNOWN"); self.assertTrue(row["reason"].startswith("plan unreadable: PlanError"))

    def test_retained_reason_names_the_span_rule_and_holds_before_the_span(self):
        # Cold gate 2026-09-21 (activation ce7c57a9, Q4): the watchdog rule reports a plan
        # inactive before t0 - PLAN_LEAD_S too, so a terminal record observed before the
        # span classifies retained with the rule named; an unparseable plan never
        # carries the retained reason.
        state = {"roots_under": str(self.custody.parent.parent)}
        t0 = 1_800_000_000
        self.sibling_root("early", "refusal.json", t0=t0)
        row = entry.retained_roots(state, now_epoch_s=t0 - 7200)["inventory"][0]
        self.assertEqual((row["classification"], row["reason"]), ("retained", "terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)"))
        shutil.rmtree(self.custody.parent / "early")
        self.sibling_root("bare", "refusal.json", plan_text="{}")
        row = entry.retained_roots(state, now_epoch_s=t0 - 7200)["inventory"][0]
        self.assertEqual(row["classification"], "UNKNOWN")
        self.assertNotEqual(row["reason"], "terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)")

    def test_deep_json_plan_is_unknown_and_the_failing_check_record_persists(self):
        # Cold gate 2026-09-21 (activation ce7c57a9, Q6 A1-F2): RecursionError from a deeply
        # nested plan is a RuntimeError, outside the ValueError family; interpreter-
        # independent via a patched parser (3.14's decoder converts it to JSONDecodeError).
        from unittest import mock
        from joulewise.night_gate import NightPlan
        state = {"roots_under": str(self.custody.parent.parent)}
        self.sibling_root("deep", "refusal.json")
        with mock.patch.object(NightPlan, "from_mapping", side_effect=RecursionError("maximum recursion depth exceeded")):
            row = entry.retained_roots(state)["inventory"][0]
            self.assertEqual(row["classification"], "UNKNOWN")
            self.assertTrue(row["reason"].startswith("plan unreadable: RecursionError"), row["reason"])
            record = self.checked(fail="retained_roots")
        self.assertIn("RecursionError", json.dumps(record))
        self.assertFalse(record["rehearsal_ready"])

    def test_custody_root_spellings_equal_under_realpath_classify_alike(self):
        # Cold gate 2026-09-21 (activation ce7c57a9, Q6 A1-F3): realpath-equal, string-unequal
        # spellings of custody_root classify exactly as the plain spelling (kills a
        # string comparison). Symlink spellings are refused by safe_path and are not used.
        state = {"roots_under": str(self.custody.parent.parent)}
        t0 = 1_800_000_000
        for name, suffix in (("slash", "/"), ("dots", "/night/..")):
            root = self.custody.parent / name
            self.sibling_root(name, "chain.started", "chain.exited", t0=t0, custody_root=str(root) + suffix)
            with self.subTest(spelling=suffix):
                self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 600)["inventory"][0]["classification"], "ACTIVE")
                self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 30 * 86400)["inventory"][0]["classification"], "retained")
            shutil.rmtree(root)

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
        (self.stage / "lifecycle").mkdir()
        for cause, passing in (("arm_transport", True), ("night_probe_error", False), ("invented", False)):
            entry.saved_json(self.stage / "lifecycle/attempts.json", [{"cause": cause}])
            record = self.checked(None if passing else "retry")
            self.assertEqual(record["checks"]["retry"]["inventory"][0]["route"], "retry" if passing else "cold_gate")

    def assert_clone_retry_route(self, cause, route):
        from joulewise.arm_retry import classify_abort
        self.assertNotEqual(classify_abort(cause), route)
        path = self.stage / "lifecycle/arm-attempts/000001/install.json"
        path.parent.mkdir(parents=True)
        entry.saved_json(path, {"cause": cause})
        original = entry.run
        executions = []
        def spy(argv, **kwargs):
            if "-c" in argv and "classify_abort" in str(argv[argv.index("-c") + 1]):
                executions.append((argv, kwargs))
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=spy):
            record = self.checked(None if route == "retry" else "retry")
        self.assertEqual(record["rehearsal_ready"], route == "retry")
        self.assertEqual(record["checks"]["retry"]["inventory"],
                         [dict(path=str(path), cause=cause, route=route)])
        self.assertTrue(executions)
        self.assertTrue(all(argv[:3] == [self.root / ".venv/bin/python", "-B", "-c"] and
                            kw["cwd"] == self.root for argv, kw in executions))

    def test_retry_uses_clone_retry_route(self):
        self.assert_clone_retry_route("night_probe_error", "retry")

    def test_retry_uses_clone_cold_gate_route(self):
        self.assert_clone_retry_route("arm_transport", "cold_gate")

    def test_retry_reads_lifecycle_attempt_inventories(self):
        for relative in ("attempts.json", "arm-attempts/000001/attempts.json"):
            path = self.stage / "lifecycle" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            entry.saved_json(path, [{"cause": "night_probe_error"}])
            with self.subTest(relative=relative):
                record = self.checked("retry")
                self.assertEqual(record["checks"]["retry"]["inventory"],
                                 [dict(path=str(path), cause="night_probe_error", route="cold_gate")])
            path.unlink()

    def test_retry_refuses_root_attempt_records(self):
        # Bench-style journals at the candidate root are neither read nor
        # ignored: check fails closed and names the lifecycle home.
        for relative in ("attempts.json", "arm-attempts/000001/attempts.json",
                         "arm-attempts/000001/install.json"):
            path = self.stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("malformed root record must not be read")
        with self.assertRaisesRegex(entry.Refused, "attempt records at the candidate root"):
            entry.retry_inventory(self.state, self.stage)
        # check wraps the sub-check into its own refusal; the cause is in check.json.
        report = self.checked(fail="pre-arm checks failed: retry")
        self.assertIn("attempt records at the candidate root", json.dumps(report["checks"]["retry"]))

    def test_notice_reuse_reads_only_lifecycle_records(self):
        for relative in ("attempts.json", "arm-attempts/000001/attempts.json",
                         "arm-attempts/000001/install.json"):
            for candidate in (self.stage, self.stage.with_name(self.stage.name + "-other")):
                root_path = candidate / relative
                root_path.parent.mkdir(parents=True, exist_ok=True)
                entry.saved_json(root_path, [{"notice_accepted": "same-id"}])
                with self.subTest(relative=relative, candidate=candidate):
                    # A root-level record refuses (fail closed) rather than being ignored.
                    with self.assertRaisesRegex(entry.Refused, "attempt records at the candidate root"):
                        entry.notice_unused(self.state, "same-id")
                    root_path.unlink()
                    if root_path.parent != candidate:
                        import shutil as _sh; _sh.rmtree(candidate / "arm-attempts", ignore_errors=True)
                    entry.notice_unused(self.state, "same-id")
                    lifecycle_path = candidate / "lifecycle" / relative
                    lifecycle_path.parent.mkdir(parents=True, exist_ok=True)
                    entry.saved_json(lifecycle_path, [{"notice_accepted": "same-id"}])
                    with self.assertRaisesRegex(entry.Refused, "notice id already used by attempt"):
                        entry.notice_unused(self.state, "same-id")
                    lifecycle_path.unlink()

    def vetoed(self, **kwargs):
        (self.base / "magistrate").mkdir(exist_ok=True)
        return entry.veto(candidate=self.stage, magistrate=self.base / "magistrate",
                          runner=kwargs.pop("runner", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, "[]", "")),
                          **kwargs)

    def publish(self, **kwargs):
        # B1 recovery tests supply B2's independent clear-veto prerequisite.
        self.vetoed()
        self.notice_fixture()
        installer = kwargs.pop("runner", lambda argv, **kw: self.fail("unexpected installer"))
        def runner(argv, **kw):
            if argv == list(entry.DIRECTIVES_ARGV):
                return subprocess.CompletedProcess(argv, 0, "[]", "")
            return installer(argv, **kw)
        return entry.publish_install(notice_accepted="message verbatim ", runner=runner,
                                     **dict(self.publication_kwargs(), **kwargs))

    def publication_kwargs(self):
        # Keep counterfactual replay on the pre-fix signature meaningful.
        kwargs = dict(candidate=self.stage, launchctl_bin="/fixture/launchctl",
                      lock_verifier=lambda root: None)
        if "magistrate" in inspect.signature(entry.publish_install).parameters:
            kwargs["magistrate"] = self.base / "magistrate"
        return kwargs

    def notice_fixture(self):
        entry.atomic_bytes(entry.lifecycle_dir(self.stage) / "notice.txt", b"fixture notice body\n")

    def test_publish_requires_check_armable_freshness_notice_and_sealed_bytes(self):
        with self.assertRaisesRegex(entry.Refused, "check.json"):
            self.publish()
        record = self.checked()
        record["rehearsal_ready"] = False
        entry.saved_json(self.stage / "lifecycle/check.json", record)
        with self.assertRaisesRegex(entry.Refused, "rehearsal_ready"):
            self.publish()
        self.checked()
        with self.assertRaisesRegex(entry.Refused, "notice acceptance"):
            entry.publish_install(**self.publication_kwargs())
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

    def test_probe_refusal_preserves_jobs_before_matching_byte_restore(self):
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
        self.assertEqual(len(calls), 1)
        self.assertNotIn("--uninstall", calls[0])
        self.assertEqual(self.plan.read_bytes(), raw)
        self.assertFalse((self.custody / "night_plan.json").exists())
        record = json.loads((self.stage / "lifecycle/install.json").read_text())
        self.assertEqual(record["outcome"], "restored_unpublished")
        self.assertEqual(record["notice_accepted"], "message verbatim ")
        self.assertEqual([c["exit_code"] for c in record["commands"]], [2])
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
                    if "--launchd-probe" in argv:
                        (self.custody / "night_probe_receipt.json").write_text("fixture receipt")
                    return subprocess.CompletedProcess(argv, 0, "", "")
                with patch.object(entry, "verify_state", side_effect=entry.Refused("verify failed")), self.assertRaisesRegex(entry.Refused, "retained state"):
                    self.publish(runner=failure)
                self.assertTrue((self.custody / "night_plan.json").exists())
                self.assertFalse(self.plan.exists())
                self.assertEqual(json.loads((self.stage / "lifecycle/install.json").read_text())["outcome"], "retained")
                # Fixture reset only, never a production remedy.
                (self.custody / "night_plan.json").unlink()
                attempt = next((self.stage / "lifecycle/arm-attempts").iterdir())
                self.plan.write_bytes((attempt / "plan.json").read_bytes())
                shutil.rmtree(self.stage / "lifecycle/arm-attempts")

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
                self.assertEqual(json.loads((self.stage / "lifecycle/install.json").read_text())["outcome"], "restored_unpublished")
                shutil.rmtree(self.stage / "lifecycle/arm-attempts")

    def test_exception_immediately_after_atomic_move_preserves_jobs(self):
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
        self.assertEqual(len(calls), 0)
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
        self.assertEqual(json.loads((self.stage / "lifecycle/uninstall.json").read_text())[0]["exit_code"], 7)

    def journal(self, name):
        """Find the actual layout, also when replaying against b678b1dc."""
        base = self.stage / "lifecycle" if (self.stage / "lifecycle").exists() else self.stage
        return base / name

    def test_b1_check_rejects_foreign_jobs_plists_and_unknown(self):
        for mode in ("LOADED", "UNKNOWN", "plists"):
            evidence = json.loads(json.dumps(self.absent_agents))
            if mode == "plists":
                evidence["plists"] = [str(self.base / (j["label"] + ".plist")) for j in evidence["jobs"]]
            else:
                for job in evidence["jobs"]:
                    job["liveness"] = mode
            with self.subTest(mode=mode), patch.object(entry, "night_agents", return_value=evidence, create=True):
                with self.assertRaisesRegex(entry.Refused, "^night agents already loaded or plists present:"):
                    entry.check(**self.kw)

    def test_night_agent_gate_uses_typed_fake_liveness_and_plist_paths(self):
        from tests.test_night_agent_install import FakeLaunchctl, LABELS
        self.agent_probe.stop()
        fake = FakeLaunchctl(self.base / "fake")
        enable_fake_list(fake)
        home = self.base / "home"
        plists = home / "Library/LaunchAgents"
        plists.mkdir(parents=True)
        for label in LABELS:
            fake.set_loaded(label, True)
            (plists / (label + ".plist")).write_text("foreign plist")
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in plists.iterdir()}
        with patch.dict(os.environ, HOME=str(home)):
            with self.assertRaisesRegex(entry.Refused, "night agents already loaded or plists present"):
                entry.check(**dict(self.kw, launchctl_bin=str(fake.executable)))
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in plists.iterdir()})
            self.assertTrue(all(fake.loaded(label) for label in LABELS))
            for label in LABELS:
                fake.set_loaded(label, False)
                (plists / (label + ".plist")).unlink()
            sidecar = plists / (LABELS[0] + ".plist.prior")
            sidecar.write_text("retained prior")
            with self.assertRaisesRegex(entry.Refused, "plist.prior"):
                entry.check(**dict(self.kw, launchctl_bin=str(fake.executable)))
            sidecar.unlink()
            probe = "com.joulewise.night-probe.foreign"
            fake.set_loaded(probe, True)
            with self.assertRaisesRegex(entry.Refused, probe):
                entry.check(**dict(self.kw, launchctl_bin=str(fake.executable)))
            fake.set_loaded(probe, False)
            fake.directive(LABELS[0], "print", fault=9)
            with self.assertRaisesRegex(entry.Refused, "UNKNOWN"):
                entry.check(**dict(self.kw, launchctl_bin=str(fake.executable)))
        self.assertTrue(all(c.startswith(("list", "print")) for c in fake.calls()))

    def test_b1_rechecks_before_publication(self):
        self.checked()
        evidence = dict(self.absent_agents, plists=["foreign.plist"])
        with patch.object(entry, "night_agents", return_value=evidence, create=True):
            with self.assertRaisesRegex(entry.Refused, "night agents already loaded or plists present"):
                self.publish(runner=lambda *a, **kw: self.fail("installer reached"))
        self.assertTrue(self.plan.exists())

    def test_b1_foreign_jobs_preserved_after_installer_refusal(self):
        self.checked()
        foreign = self.base / "foreign"
        foreign.mkdir()
        paths = []
        for job in self.absent_agents["jobs"]:
            for suffix in (".plist", ".loaded"):
                path = foreign / (job["label"] + suffix)
                path.write_bytes(b"foreign state")
                paths.append(path)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        calls = []
        def refused(argv, **kwargs):
            calls.append(argv)
            if "--uninstall" in argv:
                for path in paths:
                    path.unlink()
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "--launchd-probe" in argv:
                (self.custody / "night_probe_receipt.json").write_text("fixture receipt")
                return subprocess.CompletedProcess(argv, 0, "", "")
            return subprocess.CompletedProcess(argv, 3, "", "night_agent_already_loaded: fixture foreign job")
        # Force past both gates to reproduce the installer admission race.
        evidence = dict(jobs=[dict(j, liveness="LOADED") for j in self.absent_agents["jobs"]],
                        plists=[str(p) for p in paths if p.suffix == ".plist"], listing=dict(exit_code=0))
        with patch.object(entry, "night_agents", return_value=evidence, create=True), \
                patch.object(entry, "require_no_night_agents", create=True):
            with self.assertRaisesRegex(entry.Refused, "night_agent_already_loaded"):
                self.publish(runner=refused)
        self.assertFalse(any("--uninstall" in c for c in calls))
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})
        self.assertTrue(self.plan.exists())
        self.assertFalse((self.custody / "night_plan.json").exists())
        record = json.loads(self.journal("install.json").read_text())
        self.assertEqual(record["recovery"], "foreign_jobs_preserved")
        self.assertEqual(record["pre_publication"], evidence)
        self.assertEqual(record["cause"], "night_agent_already_loaded")

    def test_b2_malformed_uninstall_has_no_mutation(self):
        self.checked()
        path = self.journal("uninstall.json")
        for content in ("{", "{}", '[{"exit_code":0}]'):
            path.write_text(content)
            before = {p: p.read_bytes() for p in self.base.rglob("*") if p.is_file()}
            calls = []
            def runner(argv, **kwargs):
                calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, "", "")
            with self.subTest(content=content), self.assertRaisesRegex(entry.Refused, "^malformed uninstall journal$"):
                entry.uninstall(candidate=self.stage, runner=runner)
            self.assertEqual(calls, [])
            self.assertEqual(before, {p: p.read_bytes() for p in self.base.rglob("*") if p.is_file()})

    def test_b3_unresolved_raw_pid_reobserved_once(self):
        self.raw = subprocess.CompletedProcess([], 0, "456 /bin/claude foreign-session\n", "")
        with patch.dict(self.kw, census_observer=unittest.mock.Mock(return_value=self.fixture)):
            with self.assertRaisesRegex(entry.Refused, "^unresolved raw census hit pid 456$"):
                entry.check(**self.kw)
            self.assertEqual(self.kw["census_observer"].call_count, 2)

    def test_b5_atomic_json_preserves_previous_record_on_failure(self):
        path = self.stage / "record.json"
        path.write_text('{"old":true}\n')
        original = path.read_bytes()
        with patch.object(entry.json, "dump", side_effect=RuntimeError("encode")), \
                patch.object(entry.json, "dumps", side_effect=RuntimeError("encode")):
            with self.assertRaisesRegex(RuntimeError, "encode"):
                entry.saved_json(path, {"new": True})
        self.assertEqual(path.read_bytes(), original)

    def test_b5_publishing_journal_precedes_plan_move(self):
        self.checked()
        original = os.replace
        seen = []
        def replace(source, target):
            if source == self.plan:
                record = json.loads(self.journal("install.json").read_text())
                self.assertEqual(record["phase"], "publishing")
                self.assertEqual(json.loads((Path(record["attempt_path"]) / "install.json").read_text()), record)
                self.assertEqual((Path(record["attempt_path"]) / "plan.json").read_bytes(), self.plan.read_bytes())
                seen.append(record)
            return original(source, target)
        with patch.object(entry.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(entry.Refused, "installer --launchd-probe failed"):
                self.publish(runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 2, "", "refused"))
        self.assertEqual(len(seen), 1)

    def test_b6_clone_old_census_literal_is_reported(self):
        with patch.object(entry, "CENSUS_FIX", self.tip):
            with self.assertRaisesRegex(entry.Refused, "canonical"):
                entry.check(**self.kw)
        record = json.loads(self.journal("check.json").read_text())
        self.assertIn("census fix", record["checks"]["canonical"]["reason"])
        self.assertEqual(record["checks"]["census"]["argv"][-1], "codex|claude|t3")

    def test_b6_classification_runs_inside_clone(self):
        original = entry.run
        executions = []
        def spy(argv, **kwargs):
            if "-c" in argv and "classify_arm_census" in str(argv[argv.index("-c") + 1]):
                executions.append((argv, kwargs))
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=spy):
            record = self.checked()
        self.assertEqual(record["checks"]["census"]["argv"][-1], "[c]odex|[c]laude|[t]3")
        self.assertTrue(executions)
        self.assertTrue(all(argv[:3] == [self.root / ".venv/bin/python", "-B", "-c"] and
                            kw["cwd"] == self.root for argv, kw in executions))

    def test_b7_notice_reuse_across_same_day_candidates(self):
        self.checked()
        for base in (self.stage, self.stage.with_name(self.stage.name + "-other")):
            attempt = base / "lifecycle/arm-attempts/000001"
            attempt.mkdir(parents=True, exist_ok=True)
            entry.saved_json(attempt / "install.json", {"notice_accepted": "message verbatim "})
            with self.subTest(base=base), self.assertRaisesRegex(entry.Refused, "notice id already used by attempt"):
                self.publish(runner=lambda *a, **kw: self.fail("reused notice reached installer"))
            shutil.rmtree(base / "lifecycle/arm-attempts")

    def test_b8_fake_check_cannot_authorize_real_arm(self):
        # Calling through the CLI also proves check exposes the same fake seam.
        original = entry.check
        def checked(**kwargs):
            return original(**dict(self.kw, launchctl_bin=kwargs["launchctl_bin"]))
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(entry, "check", side_effect=checked), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(entry.main(["check", "--candidate", str(self.stage), "--launchctl-bin", "/fixture/fake"]), 0, errors.getvalue())
        record = json.loads(output.getvalue())
        self.assertFalse(record["armable"])
        self.assertTrue(record["fake_launchctl"])
        self.assertTrue(record["rehearsal_ready"])
        with self.assertRaisesRegex(entry.Refused, "not armable"):
            entry.publish_install(candidate=self.stage, notice_accepted="id",
                                  lock_verifier=lambda root: None,
                                  runner=lambda *a, **kw: self.fail("real installer invoked"))

    def test_b8_verify_records_launchctl_provenance(self):
        os.replace(self.plan, self.custody / "night_plan.json")
        original = entry.run
        def run(argv, **kwargs):
            if "-c" in argv and "LaunchctlAdapter" in str(argv[argv.index("-c") + 1]):
                return "[]"
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=run):
            record = entry.verify(candidate=self.stage, launchctl_bin="/fixture/fake", lock_verifier=lambda root: None)
        self.assertEqual(record["launchctl_bin"], "/fixture/fake")
        self.assertTrue(record["fake_launchctl"])

    def test_b9_second_publication_is_refusal_not_error(self):
        self.checked()
        os.replace(self.plan, self.custody / "night_plan.json")
        original = entry.publish_install
        with patch.object(entry, "publish_install", side_effect=lambda **kw: original(**kw, lock_verifier=lambda root: None)), \
                contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(entry.main(["publish-install", "--candidate", str(self.stage), "--notice-accepted", "new-id"]), 2)
        self.assertTrue(errors.getvalue().startswith("REFUSED:"))

    def test_b10_prepare_lock_excludes_lifecycle(self):
        with entry.staging_lock(self.stage.parent, self.stage.name):
            with self.assertRaisesRegex(entry.Refused, "concurrent"):
                entry.check(**self.kw)
        self.assertFalse(self.journal("check.json").exists())

    def test_b11_check_age_bound_and_cause_recorded(self):
        self.checked()
        path = self.journal("check.json")
        record = json.loads(path.read_text())
        record["finished_epoch_s"] = time.time() - 3601
        entry.saved_json(path, record)
        with self.assertRaisesRegex(entry.Refused, "older than 60 minutes"):
            self.publish(runner=lambda *a, **kw: self.fail("stale check reached installer"))
        self.checked()
        with self.assertRaisesRegex(entry.Refused, "install_span_closed"):
            self.publish(runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 2, "", "install_span_closed: fixture"))
        self.assertEqual(json.loads(self.journal("install.json").read_text())["cause"], "install_span_closed")

    def test_b12_retained_plan_must_be_regular(self):
        root = self.custody.parent / "retained"
        (root / "night").mkdir(parents=True)
        (root / "night/result.json").write_text("{}")
        (root / "night_plan.json").mkdir()
        with self.assertRaisesRegex(entry.Refused, "retained_roots"):
            entry.check(**self.kw)
        self.assertTrue((root / "night_plan.json").is_dir())

    def test_notice_refusal_matrix_preserves_preparation(self):
        original = (self.stage / "prepare.json").read_bytes()
        call = lambda: entry.notice(candidate=self.stage, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None)
        with self.assertRaisesRegex(entry.Refused, "check.json is required"):
            call()
        for change, reason in (({"rehearsal_ready": False}, "not rehearsal_ready"),
                               ({"prepare_sha256": "wrong"}, "bind prepare"),
                               ({"launchctl_bin": "/fake"}, "launchctl"),
                               ({"finished_epoch_s": time.time() - 3601}, "older"),
                               ({"finished_epoch_s": time.time() + 100}, "future")):
            with self.subTest(change=change):
                record = self.checked()
                entry.saved_json(self.journal("check.json"), dict(record, **change))
                with self.assertRaisesRegex(entry.Refused, reason):
                    call()
        self.checked()
        os.utime(self.plan, ns=(time.time_ns(), time.time_ns()))
        with self.assertRaisesRegex(entry.Refused, "newer"):
            call()
        self.checked()
        self.plan.write_bytes(self.plan.read_bytes() + b" ")
        with self.assertRaisesRegex(entry.Refused, "sealed-byte drift"):
            call()
        self.assertEqual((self.stage / "prepare.json").read_bytes(), original)
        self.assertFalse(self.journal("notice.txt").exists())

    def test_notice_refreshes_draft_and_prints_plain_text(self):
        plan = json.loads(self.plan.read_text())
        plan["authored_epoch_s"] = int(time.time())
        entry.saved_json(self.plan, plan)
        self.state["digests"][str(self.plan)] = entry.digest(self.plan)
        self.state.update(attempt=2, prior_candidates=["prior"], notice_draft="obsolete draft")
        entry.saved_json(self.stage / "prepare.json", self.state)
        self.checked()
        before = (self.stage / "prepare.json").read_bytes()
        registration = ROOT / night_gate.QPE01_PILOT_REGISTRATION_PATH
        bindings = dict(registration_path=str(registration),
                        registration_sha256=entry.digest(registration),
                        chain_source_path="source", chain_source_sha256="b" * 64)
        schedule = dict(self.schedule, install_spans_today=[(self.t0 - 3600, self.t0 - 1800)])
        original = entry.notice
        with patch.object(entry, "sealed_candidate", return_value=bindings), \
                patch.object(entry, "clone_schedule", return_value=schedule), \
                patch.object(entry, "notice", side_effect=lambda **kw: original(**dict(kw, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None))), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(entry.main(["notice", "--candidate", str(self.stage)]), 0)
        draft = output.getvalue()
        headers, body = draft.split("\n\n", 1)
        self.assertEqual(headers.splitlines(), ["To: claude2.glaring610@passmail.net",
                         "Subject: NIGHT NOTICE — " + self.state["plan_id"] +
                         " (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 2"])
        self.assertEqual(body, self.journal("notice.txt").read_text())
        self.assertIn("at or above 0.5 busy cores refuses the night", body)
        self.assertIn("A process outside the measurement apparatus using 30 or more core-seconds", body)
        checked = json.loads(self.journal("check.json").read_text())
        provenance = (f'Prepared candidate {self.state["plan_id"]}; pre-arm check '
                      f'{entry.digest(self.journal("check.json"))[:12]} at '
                      + datetime.fromtimestamp(checked["finished_epoch_s"], timezone.utc).isoformat())
        self.assertEqual(body.splitlines()[:3], [provenance, "", "Ed,"])
        self.assertFalse(any(line.startswith(("To:", "Subject:", "DRAFT — NOT SENT"))
                             for line in body.splitlines()))
        with patch.object(entry, "sealed_candidate", return_value=bindings), \
                patch.object(entry, "clone_schedule", return_value=schedule), \
                contextlib.redirect_stdout(io.StringIO()) as repeated:
            original(candidate=self.stage, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None)
        self.assertEqual(repeated.getvalue(), draft)
        self.assertEqual(self.journal("notice.txt").read_bytes(), body.encode())
        for text in (self.state["plan_id"], self.head, "attempt 2", "prior",
                     bindings["registration_sha256"], bindings["chain_source_sha256"],
                     "REQUEST / exit BEFORE", "install span 1 close EXCLUDED",
                     "To: claude2.glaring610@passmail.net", entry.digest(self.plan)):
            self.assertIn(text, draft)
        self.assertNotIn("obsolete draft", draft)
        self.assertNotIn("Cc:", draft)
        self.assertEqual(before, (self.stage / "prepare.json").read_bytes())
        with patch.object(entry, "clone_schedule", return_value=dict(schedule, install_close_epoch_s=0)):
            with self.assertRaisesRegex(entry.Refused, "exclusive install close"):
                original(candidate=self.stage, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None)

    def test_veto_clear_and_exact_directive_query(self):
        (self.base / "magistrate").mkdir()
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, "[]", "")
        record = self.vetoed(runner=runner)
        self.assertEqual(calls, [["gh", "issue", "list", "--repo", "mpmdw/JouleWise", "--label",
                                 "directive", "--state", "open", "--author", "mpmdw", "--json",
                                 "number,title,body,author"]])
        self.assertTrue(record["clear"])
        self.assertEqual(set(record["channels"]), {"directives", "standdown", "STOP", "NO"})
        self.assertTrue(all(c["clear"] for c in record["channels"].values()))

    def test_veto_directives_and_all_file_channels_are_observed(self):
        magistrate = self.base / "magistrate"
        magistrate.mkdir()
        (magistrate / "standdown.request").write_text("stop")
        (magistrate / "STOP").symlink_to(magistrate / "missing")
        entry.lifecycle_dir(self.stage)
        self.journal("NO").write_text("mailbox NO relayed manually")
        marker = self.base / "SHOULD_NOT_EXIST"
        issue = dict(number=99, title="Owner directive", body=f"$(touch {marker})", author={"login": "mpmdw"})
        with self.assertRaisesRegex(entry.Refused, "open owner directive #99 — the lead reads it before publication"):
            self.vetoed(runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, json.dumps([issue]), ""))
        record = json.loads(self.journal("veto.json").read_text())
        self.assertFalse(record["clear"])
        self.assertEqual(record["channels"]["directives"]["issues"], [issue])
        self.assertFalse(marker.exists())
        self.assertEqual(len(record["reasons"]), 4)
        for name in ("standdown", "STOP", "NO"):
            self.assertTrue(record["channels"][name]["present"])
            self.assertFalse(record["channels"][name]["clear"])

    def test_each_local_veto_refuses_independently(self):
        magistrate = self.base / "magistrate"
        magistrate.mkdir()
        entry.lifecycle_dir(self.stage)
        for path in (magistrate / "standdown.request", magistrate / "STOP", self.journal("NO")):
            with self.subTest(path=path):
                path.write_text("NO")
                with self.assertRaisesRegex(entry.Refused, "veto present"):
                    self.vetoed()
                self.assertFalse(json.loads(self.journal("veto.json").read_text())["clear"])
                path.unlink()

    def test_directive_failures_never_record_clear(self):
        def unavailable(argv, **kwargs):
            raise FileNotFoundError("gh unavailable")
        runners = [unavailable]
        for rc, raw in ((1, "[]"), (0, "not json"), (0, "{}"), (0, "[{}]")):
            runners.append(lambda argv, rc=rc, raw=raw, **kwargs: subprocess.CompletedProcess(argv, rc, raw, "failure"))
        for runner in runners:
            with self.subTest(runner=runner):
                self.vetoed()  # An old clear record must not survive failure.
                with self.assertRaisesRegex(entry.Refused, "cannot read directives"):
                    self.vetoed(runner=runner)
                record = json.loads(self.journal("veto.json").read_text())
                self.assertFalse(record["clear"])
                self.assertEqual(len(record["channels"]), 4)

    def test_publication_requires_fresh_clear_bound_veto(self):
        self.checked()
        def publish():
            return entry.publish_install(**self.publication_kwargs(), notice_accepted="new-id",
                runner=lambda *a, **kw: self.fail("installer reached"))
        with self.assertRaisesRegex(entry.Refused, "veto.json is required"):
            publish()
        for change, reason in (({"clear": False}, "not clear"),
                               ({"clear": 1}, "not clear"),
                               ({"prepare_sha256": "wrong"}, "bind prepare"),
                               ({"finished_epoch_s": time.time() - 3601}, "older"),
                               ({"finished_epoch_s": time.time() + 100}, "future")):
            with self.subTest(change=change):
                record = self.vetoed()
                entry.saved_json(self.journal("veto.json"), dict(record, **change))
                with self.assertRaisesRegex(entry.Refused, reason):
                    publish()
        for stamp, reason in ((time.time() - 3601, "older"), (time.time() + 100, "future"),
                              (self.plan.stat().st_mtime - 1, "newer")):
            self.vetoed()
            os.utime(self.journal("veto.json"), (stamp, stamp))
            with self.assertRaisesRegex(entry.Refused, reason):
                publish()
        self.journal("veto.json").write_text("broken")
        with self.assertRaisesRegex(entry.Refused, "malformed.*veto.json"):
            publish()
        self.assertTrue(self.plan.exists())
        self.assertFalse(self.journal("arm-attempts").exists())

    def test_d1_publication_observes_new_directive_and_each_stop(self):
        self.checked()
        self.notice_fixture()
        issues, calls = [], []
        def runner(argv, **kwargs):
            calls.append(list(argv))
            if argv == list(entry.DIRECTIVES_ARGV):
                return subprocess.CompletedProcess(argv, 0, json.dumps(issues), "")
            return subprocess.CompletedProcess(argv, 2, "", "installer must not be reached")
        channels = [(None, "open owner directive"),
                    (self.base / "magistrate/STOP", "veto present"),
                    (self.base / "magistrate/standdown.request", "veto present"),
                    (self.journal("NO"), "veto present")]
        for index, (path, reason) in enumerate(channels, 1):
            with self.subTest(channel=str(path)):
                self.vetoed(runner=runner)
                earlier = self.journal("veto.json").read_bytes()
                if path is None:
                    issues.append(dict(number=42, title="Stop", body="NO", author={"login": "mpmdw"}))
                else:
                    path.write_text("NO after the earlier veto")
                try:
                    with self.assertRaisesRegex(entry.Refused, reason):
                        entry.publish_install(**self.publication_kwargs(), notice_accepted=f"new-{index}", runner=runner)
                    boundary = self.journal(f"arm-attempts/{index:06d}/veto-at-publication.json")
                    record = json.loads(boundary.read_text())
                    self.assertFalse(record["clear"])
                    self.assertEqual(self.journal("veto.json").read_bytes(), earlier)
                    self.assertEqual(calls, [list(entry.DIRECTIVES_ARGV)] * (index * 2))
                    self.assertTrue(self.plan.is_file())
                    self.assertFalse((self.custody / "night_plan.json").exists())
                finally:
                    if path is None:
                        issues.clear()
                    else:
                        path.unlink()

    def test_d1_unreadable_publication_channels_refuse(self):
        self.checked()
        self.notice_fixture()
        self.vetoed()
        def unavailable(argv, **kwargs):
            if argv == list(entry.DIRECTIVES_ARGV):
                raise OSError("cannot observe gh")
            return subprocess.CompletedProcess(argv, 2, "", "unexpected installer")
        with self.assertRaisesRegex(entry.Refused, "cannot read directives"):
            entry.publish_install(**self.publication_kwargs(), notice_accepted="unreadable", runner=unavailable)
        self.assertFalse(json.loads(self.journal("arm-attempts/000001/veto-at-publication.json").read_text())["clear"])
        self.assertTrue(self.plan.exists())

    def test_d2_non_owner_is_recorded_without_veto(self):
        issue = dict(number=52, title="External directive", body="NO", author={"login": "someone-else"})
        record = self.vetoed(runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, json.dumps([issue]), ""))
        self.assertTrue(record["clear"])
        self.assertEqual(record["non_owner_directives"], [issue])
        self.assertEqual(json.loads(self.journal("veto.json").read_text()), record)
        self.assertTrue(record["channels"]["directives"]["clear"])
        for missing in ("number", "title", "body", "author"):
            broken = {key: value for key, value in issue.items() if key != missing}
            with self.subTest(missing=missing), self.assertRaisesRegex(entry.Refused, "cannot read directives"):
                self.vetoed(runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, json.dumps([broken]), ""))

    def test_d3_missing_nondirectory_and_symlink_magistrate_refuse(self):
        root = self.base / "invalid-magistrate"
        for kind in ("missing", "file", "symlink"):
            if kind == "file":
                root.write_text("not a directory")
            elif kind == "symlink":
                root.symlink_to(self.base, target_is_directory=True)
            with self.subTest(kind=kind), self.assertRaisesRegex(entry.Refused, "cannot read the magistrate root"):
                entry.veto(candidate=self.stage, magistrate=root,
                           runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, "[]", ""))
            record = json.loads(self.journal("veto.json").read_text())
            self.assertFalse(record["clear"])
            self.assertEqual(len(record["channels"]), 4)
            if kind != "missing":
                root.unlink()

    def test_d4_rehearsal_veto_cannot_authorize_real_launchctl(self):
        entry.check(**dict(self.kw, launchctl_bin="launchctl"))
        self.notice_fixture()
        self.vetoed()
        with self.assertRaisesRegex(entry.Refused, "rehearsal veto evidence cannot authorize a real arm"):
            entry.publish_install(**dict(self.publication_kwargs(), launchctl_bin="launchctl"),
                notice_accepted="real-arm-refused",
                runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 2, "", "unexpected installer"))
        self.assertIs(json.loads(self.journal("veto.json").read_text())["production"], False)
        self.assertFalse(self.journal("arm-attempts").exists())

    def test_e1_boundary_rehearsal_veto_cannot_authorize_real_launchctl(self):
        entry.check(**dict(self.kw, launchctl_bin="launchctl"))
        earlier = self.vetoed()
        # Only the earlier record is production-marked. The actual boundary
        # observer still uses the fixture root and injected directive runner.
        entry.saved_json(self.journal("veto.json"), dict(earlier, production=True))
        earlier_bytes = self.journal("veto.json").read_bytes()
        self.notice_fixture()
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            if argv == list(entry.DIRECTIVES_ARGV):
                return subprocess.CompletedProcess(argv, 0, "[]", "")
            self.fail("boundary rehearsal evidence reached the installer")
        with self.assertRaisesRegex(entry.Refused, "^rehearsal veto evidence cannot authorize a real arm$"):
            entry.publish_install(**dict(self.publication_kwargs(), launchctl_bin="launchctl"),
                                  notice_accepted="boundary-refused", runner=runner)
        self.assertEqual(calls, [list(entry.DIRECTIVES_ARGV)])
        self.assertEqual(self.journal("veto.json").read_bytes(), earlier_bytes)
        boundary = json.loads(self.journal("arm-attempts/000001/veto-at-publication.json").read_text())
        self.assertTrue(boundary["clear"])
        self.assertIs(boundary["production"], False)
        attempt = json.loads(self.journal("arm-attempts/000001/install.json").read_text())
        self.assertEqual(attempt["phase"], "observing-veto")
        self.assertEqual(attempt["outcome"], "not_published")
        self.assertEqual(attempt["commands"], [])
        self.assertTrue(self.plan.is_file())
        self.assertFalse((self.custody / "night_plan.json").exists())

    def test_e2_boundary_veto_phase_precedes_publishing(self):
        self.checked()
        phases = []
        save = entry.saved_json
        def journal(path, record):
            save(path, record)
            if path == self.journal("arm-attempts/000001/install.json"):
                phases.append(json.loads(path.read_text())["phase"])
        def runner(argv, **kwargs):
            attempt = json.loads(self.journal("arm-attempts/000001/install.json").read_text())
            if argv == list(entry.DIRECTIVES_ARGV):
                self.assertEqual(attempt["phase"], "observing-veto")
                self.assertNotIn("publishing", phases)
                self.assertTrue(self.plan.is_file())
                return subprocess.CompletedProcess(argv, 0, "[]", "")
            return subprocess.CompletedProcess(argv, 2, "", "fixture probe refusal")
        self.vetoed()
        self.notice_fixture()
        with patch.object(entry, "saved_json", side_effect=journal):
            with self.assertRaisesRegex(entry.Refused, "fixture probe refusal"):
                entry.publish_install(**self.publication_kwargs(), notice_accepted="phase-order", runner=runner)
        self.assertEqual(phases, ["prepared", "prepared", "observing-veto", "publishing",
                                 "published", "probing", "probe_finished", "recovering", "complete"])

    def test_e2_sleeping_directive_runner_times_out_before_publishing(self):
        self.checked()
        self.vetoed()
        self.notice_fixture()
        phases, timeouts = [], []
        save = entry.saved_json
        run = subprocess.run
        def journal(path, record):
            save(path, record)
            if path == self.journal("arm-attempts/000001/install.json"):
                phases.append(json.loads(path.read_text())["phase"])
        def short_deadline(argv, **kwargs):
            # Exercise a real sleeping subprocess with a shortened test
            # deadline, while pinning the production runner's 60-second budget.
            timeouts.append(kwargs.get("timeout"))
            if kwargs.get("timeout") is not None:
                kwargs["timeout"] = 0.05
            return run(argv, **kwargs)
        def runner(argv, **kwargs):
            if argv != list(entry.DIRECTIVES_ARGV):
                self.fail("timed-out directive query reached the installer")
            with patch.object(subprocess, "run", side_effect=short_deadline):
                return entry.probe_command([sys.executable, "-B", "-c",
                    "import time; time.sleep(0.2); print('[]')"], **kwargs)
        with patch.object(entry, "saved_json", side_effect=journal):
            with self.assertRaisesRegex(entry.Refused, "^cannot read directives: timeout$"):
                entry.publish_install(**self.publication_kwargs(), notice_accepted="timeout", runner=runner)
        self.assertEqual(timeouts, [60])
        self.assertEqual(phases, ["prepared", "prepared", "observing-veto", "observing-veto"])
        boundary = json.loads(self.journal("arm-attempts/000001/veto-at-publication.json").read_text())
        self.assertFalse(boundary["clear"])
        self.assertEqual(boundary["channels"]["directives"]["error"], "timeout")
        self.assertEqual(len(boundary["channels"]), 4)
        self.assertTrue(self.plan.is_file())
        self.assertFalse((self.custody / "night_plan.json").exists())

    def test_d6_publication_requires_notice_newer_than_all_inputs(self):
        self.checked()
        self.vetoed()
        kwargs = dict(self.publication_kwargs(), notice_accepted="notice-order",
                      runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 2, "", "unexpected installer"))
        with self.subTest(case="missing"), self.assertRaisesRegex(entry.Refused, "notice.txt is required"):
            entry.publish_install(**kwargs)
        inputs = [self.stage / "prepare.json", self.journal("check.json"),
                  *(Path(p) for p in self.state["digests"])]
        for path in inputs:
            with self.subTest(path=path):
                self.notice_fixture()
                kwargs["notice_accepted"] = "notice-order-" + str(path)
                stamp = path.stat().st_mtime_ns
                os.utime(self.journal("notice.txt"), ns=(stamp, stamp))
                with self.assertRaisesRegex(entry.Refused, "notice.txt is not newer"):
                    entry.publish_install(**kwargs)
        self.assertFalse(self.journal("arm-attempts").exists())

    def test_d7_new_attempt_ignores_malformed_earlier_baselines(self):
        self.checked()
        self.vetoed()
        self.notice_fixture()
        previous = self.journal("arm-attempts/000001")
        previous.mkdir(parents=True)
        (previous / "baseline.json").write_text("malformed earlier attempt")
        # Preserve legacy B2 baseline leftovers too; neither may authorize or
        # derail the current attempt's embedded verification.
        self.journal("baseline.json").write_text("malformed legacy baseline")
        original_run = entry.run
        def run(argv, **kwargs):
            if "-c" in argv and "LaunchctlAdapter" in str(argv[argv.index("-c") + 1]):
                return "[]"
            return original_run(argv, **kwargs)
        def runner(argv, **kwargs):
            if argv == list(entry.DIRECTIVES_ARGV):
                return subprocess.CompletedProcess(argv, 0, "[]", "")
            self.assertNotIn("--uninstall", argv, "earlier baseline must not enter recovery")
            if "--launchd-probe" in argv:
                (self.custody / "night_probe_receipt.json").write_text("fixture receipt")
            return subprocess.CompletedProcess(argv, 0, "", "")
        with patch.object(entry, "run", side_effect=run):
            installed = entry.publish_install(**self.publication_kwargs(), notice_accepted="attempt-two", runner=runner)
            attempt = self.journal("arm-attempts/000002")
            self.assertEqual(installed["baseline_path"], str(attempt / "baseline.json"))
            self.assertIsNone(installed["verification"]["baseline"])
            verified = entry.verify(candidate=self.stage, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None)
            self.assertEqual(verified["baseline"]["path"], str(attempt / "baseline.json"))
            self.assertFalse(verified["baseline"]["drift"])
            self.journal("arm-attempts/000003").mkdir()
            self.assertIsNone(entry.verify(candidate=self.stage, launchctl_bin="/fixture/launchctl",
                                          lock_verifier=lambda root: None)["baseline"])
        self.assertEqual((previous / "baseline.json").read_text(), "malformed earlier attempt")
        self.assertEqual(self.journal("baseline.json").read_text(), "malformed legacy baseline")

    def test_d8_missing_check_names_notice_command(self):
        with self.assertRaisesRegex(entry.Refused, "^check.json is required before notice$"):
            entry.notice(candidate=self.stage, launchctl_bin="/fixture/launchctl", lock_verifier=lambda root: None)

    def test_baseline_reports_added_removed_and_metadata_changes(self):
        entry.lifecycle_dir(self.stage)
        nested = self.custody / "night"
        nested.mkdir()
        changed = nested / "changed"
        removed = nested / "removed"
        changed.write_text("before")
        removed.write_text("gone")
        before = entry.custody_inventory(self.state)
        attempt = self.journal("arm-attempts/000001")
        attempt.mkdir(parents=True)
        path = attempt / "baseline.json"
        entry.saved_json(path, dict(schema="joulewise.evidence_baseline.v1",
                                  custody_root=str(self.custody), files=before))
        raw = path.read_bytes()
        changed.write_text("after with new size")
        removed.unlink()
        (nested / "added").write_text("new")
        drift = entry.baseline_drift(self.state)
        self.assertTrue(drift["drift"])
        self.assertEqual(drift["added"], ["night/added"])
        self.assertEqual(drift["removed"], ["night/removed"])
        self.assertEqual(list(drift["changed"]), ["night/changed"])
        self.assertEqual(drift["changed"]["night/changed"]["before"], before["night/changed"])
        self.assertEqual(path.read_bytes(), raw)

    def test_census_and_retry_json_travel_on_stdin(self):
        from dataclasses import replace
        original = entry.run
        seen = []
        def spy(argv, **kwargs):
            if "-c" in argv and any(token in argv[argv.index("-c") + 1]
                                    for token in ("classify_arm_census", "classify_abort")):
                self.assertEqual(len(argv), 4)
                self.assertEqual(kwargs["cwd"], self.root)
                seen.append(json.loads(kwargs["input"]))
            return original(argv, **kwargs)
        with patch.object(entry, "run", side_effect=spy):
            self.checked()
            # Exceeds macOS's argv budget: data must reach the actual clone
            # interpreter, rather than only satisfying a mocked call shape.
            large = replace(self.fixture, diagnostics=("x" * 300000,))
            result = entry.clone_census(self.state, 90, large)
            self.assertEqual(result["observation"]["diagnostics"], list(large.diagnostics))
        self.assertTrue(any(isinstance(value, dict) and value.get("observation") for value in seen))
        self.assertIn([], seen)

    def test_veto_cli_refusal_and_json_output(self):
        (self.base / "magistrate").mkdir()
        original = entry.veto
        def operation(**kwargs):
            return original(**kwargs, magistrate=self.base / "magistrate",
                            runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, "[]", ""))
        with patch.object(entry, "veto", side_effect=operation):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(entry.main(["veto", "--candidate", str(self.stage)]), 0)
            self.assertTrue(json.loads(output.getvalue())["clear"])
            self.journal("NO").write_text("mailbox veto")
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(entry.main(["veto", "--candidate", str(self.stage)]), 2)
            self.assertTrue(errors.getvalue().startswith("REFUSED: veto present:"))


    def released_predecessor(self, name="predecessor", *, ended_delta=61.0, reason="night_refused_not_quiet"):
        """Driver-shaped delivered refusal with a bare C5 and a real release key."""
        from scripts import magistrate_watchdog as wd
        now = time.time()
        root = self.sibling_root(name, "result.json", "receipt.json", "courier.sent",
                                 t0=now - 60)
        plan = self.sibling_plan(root, t0=now - 60)
        plan["chain_path"] = str(root / "chain.zsh")
        plan["chain_sha256_path"] = str(root / "chain.zsh.sha256")
        (root / "night_plan.json").write_text(json.dumps(plan))
        (root / "chain.zsh").write_text("export NIGHT_PAYLOAD_KIND='quiet_predicate_evidence'\n")
        result = dict(schema="joulewise.unattended_night_result.v1", plan_id=name,
                      receipt_class="DIAGNOSTIC_NO_PACK", verdict="REFUSED",
                      aborted_reason=reason, chain_exit_code=None, chain_sha256=None,
                      started_epoch_s=now - ended_delta - 1, ended_epoch_s=now - ended_delta,
                      census_count=0, census_hits=[], artifacts=[])
        receipt = dict(schema="joulewise.unattended_night_receipt.v2", plan_id=name,
                       receipt_class="DIAGNOSTIC_NO_PACK", verdict="REFUSED",
                       authored_monotonic_ns=0,
                       refusal=dict(reason=reason, detail="fixture machine refusal", evidence=[]),
                       conditions=[dict(condition_id="C5", status="REFUSED", basis=None,
                                        evidence=[], measured={})])
        (root / "night/result.json").write_text(json.dumps(result))
        (root / "night/receipt.json").write_text(json.dumps(receipt))
        (root / "night/courier.sent").write_text(json.dumps({
            "gmail_message_id": "delivered-message-id", "sent_epoch_s": now - 1,
            "verdict": "REFUSED"}) + "\n")
        parsed = wd.NightPlan.from_mapping(plan)
        key = wd._release_key(parsed, wd.Storage(root))
        magistrate = self.custody.parent / "magistrate"
        magistrate.mkdir(exist_ok=True)
        state = wd.initial_state()
        state["released_zero_capture_refusals"] = [key]
        (magistrate / "state.json").write_text(json.dumps(state))
        return root, parsed

    def test_a277_rehearsal_publication_does_not_create_successor_claim(self):
        root, _ = self.released_predecessor()
        report = self.checked()
        row = report["checks"]["successor"]
        self.assertEqual((row["verdict"], row["predecessor_plan_id"]), ("pass", "predecessor"))
        self.assertTrue(report["rehearsal_ready"])
        def fail_probe(argv, **kw):
            return subprocess.CompletedProcess(argv, 2, "", "fixture probe refusal")
        with self.assertRaisesRegex(entry.Refused, "installer --launchd-probe failed"):
            self.publish(runner=fail_probe)
        claim = self.custody.parent / "successor-claims/predecessor.json"
        self.assertFalse(claim.exists())

    def test_a277_missing_delivery_or_latch_never_licenses_bare_c5(self):
        root, _ = self.released_predecessor()
        (root / "night/courier.sent").unlink()
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")
        (root / "night/courier.sent").write_text("message-id\n")
        (self.custody.parent / "magistrate/state.json").write_text("{}")
        report = self.checked("retained_roots")
        self.assertEqual(report["checks"]["retained_roots"]["verdict"], "fail")

    def assert_post_release_fact_blocks(self, mutate):
        root, _ = self.released_predecessor()
        mutate(root)
        report = self.checked("successor")
        self.assertEqual(report["checks"]["successor"]["verdict"], "fail")

    def test_a277_chain_started_blocks(self):
        self.assert_post_release_fact_blocks(lambda r: (r / "night/chain.started").write_text("{}"))

    def test_a277_nested_reservation_blocks(self):
        def mutate(root):
            marker = root / "deep/nested/reservation.consumed.json"
            marker.parent.mkdir(parents=True)
            marker.write_text("{}")
        self.assert_post_release_fact_blocks(mutate)

    def test_a277_symlinked_evidence_blocks(self):
        self.assert_post_release_fact_blocks(
            lambda r: (r / "night/evidence").symlink_to(r / "missing"))

    def test_a277_nonempty_envelope_index_blocks(self):
        self.assert_post_release_fact_blocks(
            lambda r: (r / "night/evidence_envelopes.jsonl").write_text("{}\n"))

    def test_a277_symlinked_envelope_index_blocks(self):
        self.assert_post_release_fact_blocks(
            lambda r: (r / "night/evidence_envelopes.jsonl").symlink_to(r / "missing"))

    def test_a277_spacing_and_door_disjointness(self):
        root, _ = self.released_predecessor(ended_delta=59.99)
        ended = json.loads((root / "night/result.json").read_text())["ended_epoch_s"]
        with patch.object(entry.time, "time", return_value=ended + 59.99):
            self.assertIn("successor_spacing", self.checked("successor")["checks"]["successor"]["reason"])
        result = json.loads((root / "night/result.json").read_text())
        receipt = json.loads((root / "night/receipt.json").read_text())
        result["aborted_reason"] = receipt["refusal"]["reason"] = "non_observer_process_busy"
        (root / "night/result.json").write_text(json.dumps(result))
        (root / "night/receipt.json").write_text(json.dumps(receipt))
        from scripts import magistrate_watchdog as wd
        parsed = wd.NightPlan.from_mapping(json.loads((root / "night_plan.json").read_text()))
        state = wd.initial_state()
        state["released_zero_capture_refusals"] = [wd._release_key(parsed, wd.Storage(root))]
        (self.custody.parent / "magistrate/state.json").write_text(json.dumps(state))
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")

    def test_a277_existing_claim_and_removed_root_still_bound_count(self):
        root, _ = self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        entry._create_successor_claim(self.state, row)
        self.assertEqual(self.checked()["checks"]["successor"]["verdict"], "pass")
        claim = self.custody.parent / "successor-claims/predecessor.json"
        value = json.loads(claim.read_text())
        value["successor_plan_id"] = "different-plan"
        claim.write_text(json.dumps(value))
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")
        shutil.rmtree(root)
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")

    def test_a277_successor_refusal_cannot_license_third_plan(self):
        root, _ = self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        entry._create_successor_claim(self.state, row)
        shutil.rmtree(root)
        successor_root, _ = self.released_predecessor(name=row["candidate_plan_id"])
        self.assertTrue(successor_root.exists())
        # Give the candidate a third identity while preserving the fixture's
        # sealed bytes and allowing this deliberately renamed staging path.
        candidate = json.loads(self.plan.read_text())
        candidate["plan_id"] = "third-plan"
        self.plan.write_text(json.dumps(candidate))
        self.state["plan_id"] = "third-plan"
        self.state["digests"][str(self.plan)] = entry.digest(self.plan)
        entry.saved_json(self.stage / "prepare.json", self.state)
        expected = {key: self.state[key] for key in
                    ("plan_id", "measurement_root", "staging", "custody_root")}
        with patch.object(entry, "locations", return_value=expected):
            report = self.checked("successor")
        self.assertIn("successor_already_used", report["checks"]["successor"]["reason"])

    def test_a277_multiple_released_predecessors_refused(self):
        self.released_predecessor(name="first")
        self.released_predecessor(name="second")
        # Restore both release keys; the fixture helper writes one per call.
        from scripts import magistrate_watchdog as wd
        keys = []
        for name in ("first", "second"):
            root = self.custody.parent / name
            parsed = wd.NightPlan.from_mapping(json.loads((root / "night_plan.json").read_text()))
            keys.append(wd._release_key(parsed, wd.Storage(root)))
        state = wd.initial_state()
        state["released_zero_capture_refusals"] = keys
        (self.custody.parent / "magistrate/state.json").write_text(json.dumps(state))
        self.assertIn("more than one", self.checked("successor")["checks"]["successor"]["reason"])

    def calibration_predecessor(self):
        root, parsed = self.released_predecessor()
        runs = self.base / "calibration-runs"
        ledger = self.base / "calibration-ledger.jsonl"
        (root / "chain.zsh").write_text(
            f"export RUNS_ROOT='{runs}'\nexport CALIBRATION_LEDGER='{ledger}'\n")
        return root, parsed, runs, ledger

    def test_a277_calibration_capture_entry_blocks(self):
        _, _, runs, _ = self.calibration_predecessor()
        capture = runs / "instrument_validation" / "entry"
        capture.parent.mkdir(parents=True)
        capture.write_text("{}")
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")

    def test_a277_missing_custody_root_refused_while_release_is_recorded(self):
        root, _ = self.released_predecessor()
        shutil.rmtree(root)
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")
        (self.custody.parent / "magistrate/state.json").write_text("{}")
        self.assertEqual(self.checked()["checks"]["successor"]["verdict"], "pass")

    def test_a277_symlinked_custody_root_refused_while_release_is_recorded(self):
        root, _ = self.released_predecessor()
        shutil.rmtree(root)
        root.symlink_to(self.base / "missing-custody", target_is_directory=True)
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")

    def test_a277_resolved_released_key_root_detects_missing_custody(self):
        root, _ = self.released_predecessor()
        state_path = self.custody.parent / "magistrate/state.json"
        state = json.loads(state_path.read_text())
        key = state["released_zero_capture_refusals"][0]
        state["released_zero_capture_refusals"] = [key.replace(str(root), str(root.parent / "alias" / ".." / root.name))]
        state_path.write_text(json.dumps(state))
        shutil.rmtree(root)
        self.assertIn("released predecessor custody is missing",
                      self.checked("successor")["checks"]["successor"]["reason"])

    def test_a277_claim_temp_and_ds_store_ignored_but_malformed_final_refuses(self):
        self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        directory = self.custody.parent / "successor-claims"
        directory.mkdir()
        (directory / ".successor-claim-crash.tmp").write_text('{"torn"')
        (directory / ".DS_Store").write_bytes(b"Finder metadata")
        self.assertEqual(self.checked()["checks"]["successor"]["verdict"], "pass")
        entry._create_successor_claim(self.state, row)
        self.assertTrue((directory / "predecessor.json").is_file())
        self.assertEqual(sorted(path.name for path in directory.iterdir()),
                         [".DS_Store", ".successor-claim-crash.tmp", "predecessor.json"])
        (directory / "predecessor.json").write_text('{"torn"')
        self.assertIn("malformed successor claim",
                      self.checked("successor")["checks"]["successor"]["reason"])

    def test_a277_watchdog_and_check_read_same_facts(self):
        from scripts import magistrate_watchdog as wd
        root, plan = self.released_predecessor()
        now = time.time()
        self.assertTrue(wd._delivered_zero_capture_refusal(plan, now, wd.Storage(root)))
        self.assertEqual(self.checked()["checks"]["successor"]["verdict"], "pass")
        marker = root / "late" / "reservation.consumed.json"
        marker.parent.mkdir()
        marker.write_text("{}")
        self.assertFalse(wd._delivered_zero_capture_refusal(plan, now, wd.Storage(root)))
        self.assertEqual(self.checked("successor")["checks"]["successor"]["verdict"], "fail")

    def test_a277_publish_rereads_facts_before_claim(self):
        root, _ = self.released_predecessor()
        self.assertEqual(self.checked()["checks"]["successor"]["verdict"], "pass")
        marker = root / "late.consumed.json"
        marker.write_text("{}")
        with self.assertRaisesRegex(entry.Refused, "successor"):
            self.publish()
        self.assertFalse((self.custody.parent / "successor-claims/predecessor.json").exists())


    @unittest.skipUnless(shutil.which("launchctl"), "real launchctl required")
    def test_f1_real_launchctl_under_another_spelling_is_refused_not_rehearsed(self):
        real = shutil.which("launchctl")
        link = self.base / "launchctl-alias"
        link.symlink_to(real)
        self.released_predecessor()
        for spelling in (real, str(link), str(Path(real).resolve())):
            self.kw["launchctl_bin"] = spelling
            with self.assertRaisesRegex(entry.Refused, "real launchctl must be spelled exactly"):
                entry.check(**self.kw)
            self.assertFalse((self.stage / "lifecycle/check.json").exists())
        self.kw["launchctl_bin"] = "/fixture/launchctl"
        self.assertTrue(self.checked()["rehearsal_ready"])
        with self.assertRaisesRegex(entry.Refused, "real launchctl must be spelled exactly"):
            self.publish(runner=lambda argv, **kw: self.fail("installer ran under a real launchctl path"),
                         launchctl_bin=real)
        self.assertFalse((self.custody.parent / "successor-claims/predecessor.json").exists())
        self.assertFalse(entry.rehearsal_launchctl("launchctl"))
        self.assertTrue(entry.rehearsal_launchctl("/fixture/launchctl"))

    def test_f2_colon_in_plan_id_keeps_missing_custody_guard(self):
        root, _ = self.released_predecessor(name="pre:decessor")
        # A colon id can never name a claim file, so the check says so before publication.
        self.assertIn("cannot name a successor claim",
                      self.checked("successor")["checks"]["successor"]["reason"])
        shutil.rmtree(root)
        self.assertIn("released predecessor custody is missing",
                      self.checked("successor")["checks"]["successor"]["reason"])
        splits = entry._release_key_interpretations("a:b:/x/y:" + "0" * 64)
        self.assertEqual(splits, [("a", "b:/x/y"), ("a:b", "/x/y")])
        for bad in ("nocolon", "id:/root:notadigest", ":" + "0" * 64, 7):
            with self.assertRaisesRegex(entry.Refused, "malformed zero-capture release key"):
                entry._release_key_interpretations(bad)

    def test_f4_claim_directory_entry_is_fsynced_before_publication(self):
        self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        synced = []
        original = os.fsync
        def spy(fd):
            synced.append(os.fstat(fd).st_ino)
            return original(fd)
        with patch.object(os, "fsync", side_effect=spy):
            entry._create_successor_claim(self.state, row)
        directory = self.custody.parent / "successor-claims"
        self.assertIn(directory.stat().st_ino, synced)
        self.assertIn((directory / "predecessor.json").stat().st_ino, synced)

    def test_f5_active_foreign_claim_binds_after_root_removal_and_key_forgotten(self):
        root, _ = self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        entry._create_successor_claim(self.state, dict(row, candidate_plan_id="other-plan",
                                                       candidate_sha256="f" * 64))
        shutil.rmtree(root)
        # The watchdog forgets the release key once the custody is gone (S3 steady state).
        (self.custody.parent / "magistrate/state.json").write_text("{}")
        self.assertIn("successor claim remains active after predecessor removal",
                      self.checked("successor")["checks"]["successor"]["reason"])

    def test_f5_claim_creation_never_overwrites_a_foreign_final_claim(self):
        self.released_predecessor()
        row = self.checked()["checks"]["successor"]
        directory = self.custody.parent / "successor-claims"
        directory.mkdir()
        foreign = directory / "predecessor.json"
        other = dict(row, candidate_plan_id="other-plan", candidate_sha256="f" * 64)
        entry._create_successor_claim(self.state, other)
        before = foreign.read_bytes()
        with self.assertRaisesRegex(entry.Refused, "successor already claimed by another candidate"):
            entry._create_successor_claim(self.state, row)
        self.assertEqual(foreign.read_bytes(), before)
        # A claim that appears between the read and the link is a lost race, not an overwrite.
        with patch.object(entry, "_successor_claims", return_value=({}, directory)):
            with self.assertRaisesRegex(entry.Refused, "concurrent successor claim"):
                entry._create_successor_claim(self.state, row)
        self.assertEqual(foreign.read_bytes(), before)
        self.assertEqual([p.name for p in directory.iterdir()], ["predecessor.json"])


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
        enable_fake_list(fake)
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
                launchctl_bin=str(fake.executable), runner=probes, caller_pid=90, census_observer=lambda **kw: observation(
                    row(20, 1, "/bin/claude"), row(90, 20, "/bin/python3"), hits=(20,)),
                quiet_observer=quiet_machine, lock_verifier=lambda root: None)
            self.assertFalse(checked["armable"])
            self.assertTrue(checked["rehearsal_ready"])
            self.assertTrue(all(c.startswith(("list", "print")) for c in fake.calls()))
            self.assertFalse(any("--launchctl-bin" in c for c in calls))
            with contextlib.redirect_stdout(io.StringIO()) as notice_output:
                draft = entry.notice(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
            self.assertTrue(notice_output.getvalue().endswith(draft))
            self.assertEqual(draft, (stage / "lifecycle/notice.txt").read_text())
            self.assertIn(state["plan_id"], draft)
            (base / "magistrate").mkdir()
            entry.veto(candidate=stage, magistrate=base / "magistrate",
                       runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, "[]", ""))
            published = custody / "night_plan.json"
            raw = (stage / "night_plan.json").read_bytes()
            inode = (stage / "night_plan.json").stat().st_ino
            def real_installer(argv, **kwargs):
                if argv == list(entry.DIRECTIVES_ARGV):
                    return subprocess.CompletedProcess(argv, 0, "[]", "")
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
                launchctl_bin=str(fake.executable), runner=real_installer, magistrate=base / "magistrate",
                lock_verifier=lambda root: None)
            self.assertEqual(installed["outcome"], "rehearsal_installed")
            self.assertFalse(installed["installed"])
            self.assertTrue(installed["fake_launchctl"])
            self.assertEqual(installed["launchctl_bin"], str(fake.executable))
            self.assertEqual([c["exit_code"] for c in installed["commands"]], [0, 0])
            self.assertEqual(installed["probe_receipt_sha256"], entry.digest(custody / "night_probe_receipt.json"))
            self.assertEqual(installed["verification"]["request_epoch_s"], state["schedule"]["boundaries"]["REQUEST / exit BEFORE"])
            self.assertTrue(all(fake.loaded(label) for label in LABELS))
            verified = entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
            self.assertFalse(verified["baseline"]["drift"])
            attempt = Path(installed["attempt_path"])
            boundary_veto = json.loads((attempt / "veto-at-publication.json").read_text())
            self.assertTrue(boundary_veto["clear"])
            self.assertFalse(boundary_veto["production"])
            self.assertGreater(boundary_veto["finished_epoch_s"],
                               json.loads((stage / "lifecycle/veto.json").read_text())["finished_epoch_s"])
            baseline_path = attempt / "baseline.json"
            self.assertEqual(installed["baseline_path"], str(baseline_path))
            baseline_raw = baseline_path.read_bytes()
            baseline = json.loads(baseline_raw)
            self.assertEqual(baseline["files"], entry.custody_inventory(state))
            (custody / "night").mkdir(exist_ok=True)
            (custody / "night/new.json").write_text("{}")
            drift = entry.verify(candidate=stage, launchctl_bin=str(fake.executable), lock_verifier=lambda root: None)
            self.assertEqual(drift["baseline"]["added"], ["night/new.json"])
            self.assertTrue(drift["baseline"]["drift"])
            self.assertEqual(baseline_path.read_bytes(), baseline_raw)
            self.assertTrue(verified["fake_launchctl"])
            self.assertEqual(verified["launchctl_bin"], str(fake.executable))
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



class MeasurementRootLocationTests(unittest.TestCase):
    """Record 29: measurement clones live under the Spotlight-excluded custody tree."""

    def test_measurement_root_is_under_night_custody_measurement(self):
        roots = Path("/Users/example")
        paths = entry.locations(roots, roots / "night-plan-staging", 1790172000, "a" * 40)
        root = Path(paths["measurement_root"])
        self.assertEqual(root.parent, roots / "night-custody" / entry.MEASUREMENT_SUBDIR)
        self.assertTrue(root.name.startswith("JouleWise-measurement-"))
        custody = Path(paths["custody_root"])
        self.assertNotIn(root, custody.parents)
        self.assertNotIn(custody, root.parents)
        self.assertNotEqual(root, custody)

    def test_measurement_subdir_never_matches_plan_prefix(self):
        prefix = entry.kind_row(entry.KIND).plan_id_prefix
        self.assertFalse(entry.MEASUREMENT_SUBDIR.startswith(prefix))

    def test_one_level_plan_glob_never_reaches_a_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            custody = Path(tmp) / "night-custody"
            clone = custody / entry.MEASUREMENT_SUBDIR / "JouleWise-measurement-x"
            clone.mkdir(parents=True)
            (clone / "night_plan.json").write_text("{}")
            self.assertEqual(list(custody.glob("*/night_plan.json")), [])


if __name__ == "__main__":
    unittest.main()
