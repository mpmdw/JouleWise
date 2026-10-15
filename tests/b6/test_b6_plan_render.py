"""Production plan preparation and launch, with desk identity and installer fakes."""
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace
from unittest import mock

from joulewise import calibration_ledger as ledger, night_agent_install, night_gate
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.b5 import driver, plan
from joulewise.b6 import archive, compose, plan_inputs, queue
from joulewise.b6.driver_lane import DriverLane, read
from joulewise.b6.pack_registration import Registration
from tests.b6.support import DeskCase, ROOT, document, write_json
from tests import battery_float_fixture


class ProductionPlanRenderTests(DeskCase):
    def setUp(self):
        super().setUp()
        self.measurement = self.root / "measurement"
        self.git("clone", "--quiet", "--no-hardlinks", str(ROOT), str(self.measurement))
        # The portable issued-ledger fixture supplies a matching committed pin;
        # no host measurement/custody tree is read by this regression test.
        seed = ROOT / "tests/fixtures/d117_v2_production/issued"
        target = self.measurement / plan.DEFAULT_LEDGER_RELATIVE
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(seed / "calibration_observation_ledger.jsonl", target)
        shutil.copyfile(seed / "calibration_ledger_head.json", self.measurement / plan.HEAD_PIN_RELATIVE)
        self.git("-C", str(self.measurement), "add", plan.HEAD_PIN_RELATIVE)
        self.git("-C", str(self.measurement), "-c", "user.name=B6 Desk", "-c", "user.email=desk@invalid",
                 "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Synthetic ledger fixture pin")
        # Child plan readers must exercise the same uncommitted implementation
        # as this process, rather than the clone's HEAD-only source.
        for relative in ("joulewise/b5/chain.py", "joulewise/b5/plan.py", "joulewise/night_gate.py",
                         "joulewise/b6/plan_inputs.py", "joulewise/b6/capture_screen.py",
                         "scripts/check_b5_chain.py"):
            shutil.copyfile(ROOT / relative, self.measurement / relative)

    def git(self, *args, **kwargs):
        return subprocess.run(["git", "-c", "maintenance.auto=false", "-c", "gc.auto=0", *args],
                              check=True, capture_output=True, text=True, **kwargs)

    def runner(self, argv, **kwargs):
        argv = list(map(str, argv))
        if "-c" in argv and "base64" in argv[argv.index("-c") + 1]:
            epoch = dict(zip(ledger.IDENTITY_EPOCH_FIELDS,
                             ("TEST", "Mac15,9", "ac_high_power", 100, "estimator-v1", "pulse-v3")))
            t1 = {**{key: "value-" + key for key in V2_BINDING_FIELDS}, **epoch}
            return SimpleNamespace(returncode=0, stdout=json.dumps({
                name: base64.b64encode(json.dumps(value).encode()).decode()
                for name, value in (("identity-epoch.json", epoch), ("t1-bindings.json", t1))}), stderr="")
        if argv[0].endswith("install_night_agent.sh"):
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if argv[0] == "git":
            return subprocess.run(argv, **kwargs)
        raise AssertionError("unexpected production-plan subprocess: " + repr(argv))

    def render(self, pack, registered):
        reg = self.measurement / "configs/b6/registration/acceptance.json"
        if registered:
            write_json(reg, document())
        else:
            reg.unlink(missing_ok=True)
        loop = self.root / (pack + ("-registered" if registered else "-pending")) / "loop"
        lane = DriverLane(self.measurement, loop, self.runner, block_root=loop.parent,
                          launchctl_bin="/usr/bin/false")
        value = read(self.measurement / f"configs/b6/packs/{pack}/registration.json")
        value["status"] = "registered"
        layout = compose.layout(queue.Selection((pack,), 1),
                                {pack: Registration(value, commit_time=0)}, self.measurement)
        prepared = lane.prepare_session(layout, compose.render(layout), smoke=False, keep={},
                                        staging_root=loop / "staging" / layout.session_id)
        lane.launch(prepared)
        written = read(prepared.plan_path)
        return prepared, written, Path(written["chain_path"]).read_text()

    def screen(self, rendered, bound):
        scratch = self.root / "screen"
        scratch.mkdir(exist_ok=True)
        write_json(scratch / "instrument_evidence.json", {"b_fiducial_s": bound})
        source = rendered[rendered.index("B6_ALIGNMENT_REFERENCE_S="):rendered.index('cd "$REPO"')]
        script = scratch / "screen.zsh"
        script.write_text('CLAIM_RUNS_ROOT=fixture\nflag() { print -r -- "flag $1"; }\n'
                          'stop_chain() { print -r -- "chain.stop $1 $2"; exit $2; }\n' + source +
                          '\nscreen_b6_calibration "$1"\n')
        return subprocess.run(["/bin/zsh", "-f", str(script), str(scratch)],
                              capture_output=True, text=True, timeout=10)

    def check_plan(self, prepared):
        return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/check_b5_chain.py"),
                               "--plan", prepared.plan_path, "--no-live-identity"],
                              capture_output=True, text=True, timeout=60)

    def check_readers(self, prepared, written):
        parsed = night_gate.NightPlan.from_mapping(read(prepared.plan_path))
        self.assertEqual(driver.yield_plan(parsed)["planned"], written["hazard_window"]["member_count"])
        self.assertEqual(len(driver.disk_targets(parsed.hazard_window, arm=True)), 5)
        preflight = subprocess.run([sys.executable, "-B", str(self.measurement / "scripts/run_night.py"),
                                    "preflight", "--plan", prepared.plan_path],
                                   capture_output=True, text=True, timeout=30)
        self.assertEqual(preflight.returncode, 0, preflight.stdout + preflight.stderr)
        self.assertEqual(json.loads(preflight.stdout)["preflight"], "ok")

        args = SimpleNamespace(plan=Path(prepared.plan_path), python=sys.executable,
                               courier_bin="/usr/bin/true", render_only=self.root / "render-only")
        real_run = subprocess.run

        def desk_run(argv, **kwargs):
            if "preflight" not in argv and Path(argv[0]).name != "git":
                raise AssertionError("unexpected installer subprocess: " + repr(argv))
            kwargs["env"] = {**os.environ, **kwargs.get("env", {}), "JW_B5_SYNTHETIC_ONLY": "1",
                             "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": os.environ["TMPDIR"]}
            return real_run(argv, **kwargs)

        # Admission's wall-clock install span is independent of binding shape.
        # The installer itself parses the written plan and runs its real child
        # preflight, with a fixture battery reading and no launchd calls.
        def install(courier_bin):
            with mock.patch.object(night_agent_install, "BATTERY_PROBE_RUNNER", battery_float_fixture.runner()), \
                    mock.patch.object(night_agent_install.Prepared, "admit"), \
                    mock.patch.object(night_agent_install.subprocess, "run", side_effect=desk_run), \
                    contextlib.redirect_stdout(io.StringIO()):
                return night_agent_install.validate_install(
                    SimpleNamespace(**{**vars(args), "courier_bin": courier_bin}), self.measurement)

        installed = install("/usr/bin/true")
        self.assertEqual(installed.plan.hazard_window["bindings"], written["hazard_window"]["bindings"])
        # Stage-3 review F1/F4: a block-6 plan never renders an agent courier, by
        # default or by name, and the courier's directory never leads the job's PATH.
        system_path = "/usr/bin:/bin:/usr/sbin:/sbin"
        self.assertEqual(installed.courier_path, system_path)
        default = install(None)
        self.assertEqual(Path(default.courier), self.measurement / "scripts/b6_courier.sh")
        self.assertEqual(default.courier_path, system_path)
        agents = self.root / "agent-couriers"
        agents.mkdir(exist_ok=True)
        named = agents / "claude"
        named.write_text("#!/bin/sh\nexit 0\n")
        named.chmod(0o755)
        linked = agents / "courier-link"
        if not linked.is_symlink():
            linked.symlink_to(named)
        for agent in (named, linked):
            with self.subTest(courier=agent.name), self.assertRaises(night_agent_install.Refused) as refused:
                install(str(agent))
            self.assertEqual(refused.exception.code, 2)
            self.assertIn("must be a program, not an agent", str(refused.exception))

    def test_each_production_pack_uses_b6_screen_and_no_spares(self):
        for pack, maximum, members in (("alpha", 124620, 125), ("beta", 127020, 125),
                                       ("gamma", 113460, 107)):
            for registered in (False, True):
                with self.subTest(pack=pack, registered=registered):
                    prepared, written, rendered = self.render(pack, registered)
                    self.assertIn("screen_b6_calibration()", rendered)
                    self.assertNotIn("screen_pre_calibration()", rendered)
                    self.assertEqual(rendered.count("Spare-slot retry"), 0)
                    bindings = archive.bindings(written)
                    expected = {key: value if registered else None for key, value in (
                        ("alignment_reference_s", "0.036462861644980"),
                        ("bracket_screen_s", "0.014531"), ("operative_bound_stop_s", "0.092"))}
                    self.assertEqual(bindings["capture_screen"], expected)
                    self.assertIs(bindings["spare_retries"], False)
                    self.assertEqual((written["window_max_s"], prepared.max_s), (maximum, maximum))
                    self.assertEqual(written["hazard_window"]["planned_bytes"], members * plan_inputs.BYTES_PER_MEMBER)
                    for ms in (30.6, 36.5, 40.14, 48.01):
                        ran = self.screen(rendered, ms / 1000)
                        self.assertEqual(ran.returncode, 0, ran.stderr)
                        self.assertEqual("flag calibration.alignment_above_reference" in ran.stdout,
                                         registered and ms > 36.462861644980)
                    missing = self.screen(rendered, None)
                    self.assertEqual(missing.returncode, 1, missing.stderr)
                    self.assertIn("flag calibration.bracket_incomplete", missing.stdout)
                    if registered:
                        stopped = self.screen(rendered, .080)
                        self.assertEqual(stopped.returncode, 12, stopped.stderr)
                        self.assertIn("chain.stop operative_bound_above_stop 12", stopped.stdout)
                    checked = self.check_plan(prepared)
                    self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                    self.check_readers(prepared, written)


class ScreenInputsTests(DeskCase):
    def test_acceptance_values_preserve_decimals_and_open_slots(self):
        reg = self.root / "registration"
        reg.mkdir()
        keys = ("alignment_reference_s", "bracket_screen_s", "operative_bound_stop_s")
        self.assertEqual(plan_inputs.capture_screen(reg), dict.fromkeys(keys))
        value = document()
        write_json(reg / "acceptance.json", value)
        self.assertEqual(plan_inputs.capture_screen(reg), {key: value["calibration"][key] for key in keys})
        del value["calibration"]["operative_bound_stop_s"]
        write_json(reg / "acceptance.json", value)
        self.assertIsNone(plan_inputs.capture_screen(reg)["operative_bound_stop_s"])
        del value["calibration"]["alignment_reference_s"]
        write_json(reg / "acceptance.json", value)
        self.assertEqual(plan_inputs.capture_screen(reg), dict.fromkeys(keys))
