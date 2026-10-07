"""Gate-prune integration: the block-5 driver's production seams against the real lanes.

Each lane's own tests fake its neighbours. These tests join them in one tree:

- a window plan written by L2's plan writer for each real block-5 pack, with
  L1's real threshold contract (no injected defaults);
- that plan's thresholds through the driver's production arm adapter into
  L1's real ``hazards.arm.run`` (hardware faked only at L1's own seams, with
  L1's test rig), and the arm's record read back as the driver reads it;
- the monitor config the driver writes, through L1's real ``validate_config``;
- the collector and G10 command lines the driver builds, through L4's and
  L8's real argument parsers;
- the bracket ids the driver publishes into the lineage (L3) equal the ids the
  rendered chain reserves the bracket session under.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import os
import shlex
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise import night_gate
from joulewise.b5 import driver as b5_driver
from joulewise.b5 import plan as b5_plan
from joulewise.hazards import arm as hazard_arm
from joulewise.hazards import base as hazard_base
from joulewise.hazards import monitor as hazard_monitor
from tests.fixtures.b5_plan import fake_window
from tests.hazards.fakes import FAKE_POWERMETRICS
from tests.hazards.test_arm import DRIVER, Rig

REPO_ROOT = Path(__file__).resolve().parents[1]
SIX = ("clock", "battery", "thermal", "contention", "disk", "instrument")


def load_script(name: str):
    module_name = f"{name}_under_integration"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses resolve their module by name
    spec.loader.exec_module(module)
    return module


class WrittenPlans(unittest.TestCase):
    """One real window plan per block-5 pack, written once for the class."""

    @classmethod
    def setUpClass(cls) -> None:
        directory = tempfile.TemporaryDirectory(prefix="gp-int-")
        cls.addClassCleanup(directory.cleanup)
        cls.root = Path(directory.name).resolve()
        cls.measurement = fake_window.build_checkout(cls.root)
        t0 = (int(time.time()) // 60 + 60) * 60
        cls.records, cls.plans = {}, {}
        # GAMMA plans again since lane L10 removed its duplicate midpoint dispatch.
        for pack in ("alpha", "beta", "gamma"):
            root = cls.root / pack
            root.mkdir()
            inputs = fake_window.inputs(root, cls.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=t0)
            # The production threshold contract: lane L1's default_thresholds().
            record = b5_plan.write_window_plan(inputs, pack_digest=lambda _root: "e" * 64)
            cls.records[pack] = record
            cls.plans[pack] = night_gate.NightPlan.from_mapping(json.loads(Path(record["plan"]["path"]).read_text()))


class PlanThresholdsReachTheRealArm(WrittenPlans):
    def context(self, plan, custody: Path) -> b5_driver.ArmContext:
        window = plan.hazard_window
        unused = lambda: {}  # noqa: E731 - the adapter runs OFF and the collectors through the arm itself
        return b5_driver.ArmContext(
            plan=plan, plan_path=custody / "plan.json", custody_root=custody, night_dir=custody / "night",
            record_root=custody / "hazards", hazard_window=window, thresholds=window["thresholds"],
            t_stream_max_s=float(window["T_stream_max_s"]), planned_bytes=int(window["planned_bytes"]),
            disk_volumes=(), disk_targets=({"path": "/Volumes/x/runs", "copies": 1},
                                           {"path": "/Volumes/backup", "copies": 1}),
            measurement_tree_pids=(DRIVER,), census={"clean": True}, arm_deadline_epoch_s=0.0, dry_arm=False,
            record_only_argv=("/usr/bin/good-collector",), network_time_off=unused,
            record_only_collectors=unused, agent_census=unused)

    def arm(self, plan, rig: Rig) -> dict:
        real_run = hazard_arm.run

        def run_on_rig(config, seams=None):
            self.assertIsNone(seams)  # the driver runs the production arm
            config = dataclasses.replace(config, powermetrics_executable=str(FAKE_POWERMETRICS), privilege_prefix=())
            self.seen_config = config
            rig_seams = hazard_arm.Seams(ctx=hazard_base.Context(run=rig.runner, clocks=rig.clocks),
                                         frequency_reader=rig.reader, statvfs=rig.statvfs, stat=rig.stat,
                                         host_cpu=rig.table.host_cpu, smc_read=rig.smc)
            with mock.patch.dict(os.environ, {"FAKE_PM_FIXTURE": str(rig.cadence_fixture)}):
                return real_run(config, rig_seams)

        with mock.patch.object(hazard_arm, "run", run_on_rig):
            return b5_driver._production_arm(self.context(plan, rig.custody))

    def test_each_plan_arms_go_on_a_quiet_mac(self) -> None:
        for pack, plan in self.plans.items():
            with self.subTest(pack=pack), tempfile.TemporaryDirectory(dir=self.root) as directory:
                rig = Rig(Path(directory))
                decision = self.arm(plan, rig)
                self.assertTrue(decision["go"], decision["reasons"])
                self.assertEqual({name: "PASS" for name in SIX}, decision["verdicts"])
                self.assertEqual(str(rig.custody / "hazards" / "arm.json"), decision["record_path"])
                self.assertEqual(["flags.arm"], [entry["name"] for entry in decision["record_only"]])
                # The window's own sizing reached the arm, not a copied threshold.
                record = json.loads((rig.custody / "hazards" / "arm.json").read_text())
                self.assertEqual(plan.hazard_window["planned_bytes"], record["thresholds"]["disk"]["planned_bytes"])
                self.assertEqual(plan.hazard_window["T_stream_max_s"],
                                 record["thresholds"]["clock"]["t_stream_max_s"])
                normalized = b5_driver.normalize_decision(decision)
                self.assertTrue(normalized["go"])

    def test_refusals_and_unmeasured_reads_reach_the_driver_as_no_go(self) -> None:
        plan = self.plans["alpha"]
        for label, change, module, status in (
                ("thermal level 1", lambda rig: setattr(rig, "thermal_level", 1), "thermal", "REFUSE"),
                ("disk unreadable", lambda rig: rig.fail.add("disk"), "disk", "UNMEASURED"),
                ("agent alive", lambda rig: setattr(rig, "census", (0, b"9 claude\n")), None, None)):
            with self.subTest(label), tempfile.TemporaryDirectory(dir=self.root) as directory:
                rig = Rig(Path(directory))
                change(rig)
                decision = self.arm(plan, rig)
                normalized = b5_driver.normalize_decision(decision)
                self.assertFalse(decision["go"])
                self.assertFalse(normalized["go"])
                if module is not None:
                    self.assertEqual(status, decision["verdicts"][module])
                    self.assertIn(module, normalized["not_pass"])
                else:
                    self.assertEqual("census", decision["refused_at"])


class DriverCommandLinesMeetTheirTools(WrittenPlans):
    def test_monitor_config_is_valid_for_the_real_monitor(self) -> None:
        plan = self.plans["alpha"]
        seams = b5_driver.production_seams(REPO_ROOT)
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            custody = Path(directory)
            argv = seams.monitor_argv(b5_driver.MonitorRequest(plan, custody / "plan.json", custody,
                                                               custody / "night", 4242))
            config_path = Path(argv[argv.index("--config") + 1])
            config = hazard_monitor.validate_config(json.loads(config_path.read_text()))
            self.assertEqual([4242], config["tree_roots"])
            thresholds = plan.hazard_window["thresholds"]
            self.assertEqual(thresholds["disk"]["low_bytes"], config["low_bytes"])
            self.assertEqual(thresholds["contention"]["cpu_limit_s_per_s"], config["cpu_limit_s_per_s"])
            self.assertEqual(str(REPO_ROOT / "scripts/hazard_monitor.py"), argv[argv.index("-B") + 1])
            self.assertEqual(list(hazard_monitor.TASKPOLICY_PREFIX), argv[:2])

    def test_collector_argv_parses_and_carries_the_sealed_pins_when_present(self) -> None:
        collect = load_script("collect_window_flags")
        seams = b5_driver.production_seams(REPO_ROOT)
        plan = self.plans["alpha"]
        sealed = Path(plan.measurement_root) / "configs/campaigns/v5_claim_25g83"
        pins = sealed / "identity_pins.json"
        self.assertFalse(sealed.exists())
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            custody = Path(directory)
            argv = seams.collectors_argv(b5_driver.CollectorRequest(plan, custody / "plan.json", custody, "arm"))
            self.assertEqual(str(REPO_ROOT / "scripts/collect_window_flags.py"), argv[2])
            specs = dict(collect.build_specs(collect.build_parser().parse_args(argv[3:]), None))
            self.assertEqual({"pack_identity", "checkout_identity", "executed_code", "model_identity",
                              "ledger_readiness"}, set(specs))
            self.assertIsNone(specs["model_identity"]["identity_pins_path"])
            self.assertEqual(plan.measurement_head, specs["checkout_identity"]["h_claim"])
            self.assertEqual(plan.hazard_window["bracket_session_id"], specs["ledger_readiness"]["session_id"])
            sealed.mkdir(parents=True)
            try:
                pins.write_text("{}\n")
                argv = seams.collectors_argv(b5_driver.CollectorRequest(plan, custody / "plan.json", custody, "arm"))
                specs = dict(collect.build_specs(collect.build_parser().parse_args(argv[3:]), None))
                self.assertEqual(str(pins), specs["model_identity"]["identity_pins_path"])
            finally:
                pins.unlink()
                sealed.rmdir()

    def test_g10_argv_parses_with_the_control_script(self) -> None:
        g10 = load_script("g10_clock_step_control")
        seams = b5_driver.production_seams(REPO_ROOT)
        plan = self.plans["alpha"]
        night = Path(plan.custody_root) / "night"
        argv = seams.g10_argv(night, float(plan.hazard_window["T_stream_max_s"]))
        self.assertEqual(str(REPO_ROOT / "scripts/g10_clock_step_control.py"), argv[2])
        args = g10.build_parser().parse_args(argv[3:])
        self.assertEqual(night, args.night_dir)
        self.assertEqual(float(plan.hazard_window["T_stream_max_s"]), args.t_stream_max_s)

    def test_lineage_ids_are_the_ids_the_chain_reserves(self) -> None:
        for pack, plan in self.plans.items():
            with self.subTest(pack=pack):
                window = plan.hazard_window
                chain = Path(plan.chain_path).read_text().replace("\\\n", " ")  # join continued lines
                reserve = next(line for line in chain.splitlines() if "--session-id" in line and "--plan-id" in line)
                words = shlex.split(reserve)
                self.assertEqual(window["pack"]["pack_plan_id"], words[words.index("--plan-id") + 1])
                self.assertEqual(window["pack"]["window_id"], words[words.index("--window-id") + 1])
                self.assertEqual(window["bracket_session_id"], words[words.index("--session-id") + 1])
                seen = {}
                fake = mock.Mock(publish_window_lineage=lambda **kw: seen.update(kw) or {"ok": True})
                with mock.patch.dict(sys.modules, {"joulewise.window_lineage": fake}), \
                        mock.patch("joulewise.window_lineage", fake, create=True):
                    request = b5_driver.LineageRequest(
                        plan=plan, plan_path=Path("/p"), custody_root=Path("/c"), night_dir=Path("/c/night"),
                        hazard_window=window, claim_runs_root=Path(window["runs_roots"]["claim"]),
                        bound_runs_root=Path(window["runs_roots"]["bound"]), arm_record_path=None,
                        arm_decision_path=None, boot_session_uuid=None)
                    b5_driver._production_lineage(request)
                self.assertEqual((window["pack"]["pack_plan_id"], window["pack"]["window_id"],
                                  window["bracket_session_id"]),
                                 (seen["plan_id"], seen["window_id"], seen["bracket_session_id"]))
                from joulewise import window_lineage
                import inspect
                self.assertEqual(set(inspect.signature(window_lineage.publish_window_lineage).parameters), set(seen))


if __name__ == "__main__":
    unittest.main()
