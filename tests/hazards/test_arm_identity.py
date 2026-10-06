"""ARM-OS (gate-prune core lane VPF): the arm reads ``kern.osversion`` and
``hw.model`` when it is given the acceptance's judged epochs, so an OS or
machine no acceptance judges refuses before the dwell instead of at the
pre-slot writer's kept epoch check after it.  A failed read is recorded and
never refuses; ``expected_epochs=None`` (every existing caller) reads nothing.

Also pins the driver seam: ``_production_arm`` fills ``expected_epochs`` from
the measurement checkout's acceptance and ledger, and passes ``None`` when they
cannot be loaded.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.hazards import arm
from tests.hazards.fakes import completed
from tests.hazards.test_arm import Rig

OS_BUILD_ARGV = ("/usr/sbin/sysctl", "-n", "kern.osversion")
HARDWARE_MODEL_ARGV = ("/usr/sbin/sysctl", "-n", "hw.model")
JUDGED = [{"os_build": "25G83", "hardware_model": "Mac15,9", "power_policy": "ac_high_power"}]


class ArmIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.os_build: tuple[int, bytes] | None = (0, b"25G83\n")
        self.rig = self._rig(Path(self.tmp.name))

    def _rig(self, directory: Path) -> Rig:
        rig = Rig(directory)
        rig.runner.handlers[OS_BUILD_ARGV] = self._os_build
        rig.runner.handlers[HARDWARE_MODEL_ARGV] = lambda argv: completed(argv, b"Mac15,9\n")
        return rig

    def _os_build(self, argv):
        if self.os_build is None:
            return completed(argv, error="FileNotFoundError: sysctl")
        returncode, stdout = self.os_build
        return completed(argv, stdout, returncode=returncode)

    def sysctl_calls(self):
        return [call for call in self.rig.runner.calls
                if call in (OS_BUILD_ARGV, HARDWARE_MODEL_ARGV)]

    def test_unjudged_os_build_refuses_at_identity_before_network_time(self):
        self.os_build = (0, b"99Z999\n")
        result = self.rig.run(expected_epochs=JUDGED)
        self.assertEqual((result.decision, result.refused_at), (arm.NULL, "identity"))
        self.assertIn("99Z999", result.reasons[0])
        self.assertNotIn(arm.NETWORK_TIME_OFF_ARGV, self.rig.runner.calls)
        record = json.loads(result.path.read_text())
        self.assertEqual(record["identity"]["measured"],
                         {"os_build": "99Z999", "hardware_model": "Mac15,9"})
        self.assertIs(record["identity"]["judged"], False)
        steps = [step["step"] for step in record["steps"]]
        self.assertEqual(steps[-2:], ["identity", "decision"])

    def test_judged_identity_proceeds_to_go(self):
        result = self.rig.run(expected_epochs=JUDGED)
        self.assertEqual(result.decision, arm.GO, result.reasons)
        self.assertEqual(len(self.sysctl_calls()), 2)
        self.assertIs(result.document["identity"]["judged"], True)
        steps = [step["step"] for step in result.document["steps"]]
        self.assertEqual(steps.index("identity") + 1, steps.index("network_time_off"))

    def test_failed_read_is_recorded_and_never_refuses(self):
        for label, value in (("spawn error", None), ("nonzero exit", (1, b"")),
                             ("empty output", (0, b"\n"))):
            with self.subTest(label):
                rig = self._rig(Path(tempfile.mkdtemp(dir=self.tmp.name)))
                self.os_build = value
                result = rig.run(expected_epochs=JUDGED)
                self.assertEqual(result.decision, arm.GO, result.reasons)
                self.assertIsNone(result.document["identity"]["judged"])
                self.assertIsNone(result.document["identity"]["measured"]["os_build"])

    def test_no_expected_epochs_reads_no_identity(self):
        result = self.rig.run()
        self.assertEqual(result.decision, arm.GO, result.reasons)
        self.assertEqual(self.sysctl_calls(), [])
        self.assertNotIn("identity", result.document)

    def test_empty_epoch_list_never_refuses(self):
        result = self.rig.run(expected_epochs=[])
        self.assertEqual(result.decision, arm.GO, result.reasons)
        self.assertIsNone(result.document["identity"]["judged"])


class ProductionArmEpochSeamTests(unittest.TestCase):
    """``b5.driver._production_arm`` passes the acceptance's judged epochs."""

    def _config(self, plan) -> dict:
        import types

        from joulewise.b5 import driver as b5_driver

        seen: dict = {}

        class Result:
            decision, document, refused_at, reasons = "GO", {}, None, ()
            path = Path("/fixture/hazards/arm.json")
            go = True

        fake = types.SimpleNamespace(ArmConfig=lambda **kw: seen.setdefault("config", kw),
                                     run=lambda config: Result())
        root = Path(self.tmp.name)
        context = b5_driver.ArmContext(
            plan=plan, plan_path=root / "plan.json", custody_root=root, night_dir=root / "night",
            record_root=root / "hazards", hazard_window={"bindings": {}},
            thresholds={}, t_stream_max_s=335.0, planned_bytes=7, disk_volumes=(),
            disk_targets=(), measurement_tree_pids=(), census={"clean": True},
            arm_deadline_epoch_s=0.0, dry_arm=False, record_only_argv=(),
            network_time_off=dict, record_only_collectors=dict, agent_census=dict)
        with mock.patch.dict("sys.modules", {"joulewise.hazards.arm": fake}), \
                mock.patch("joulewise.hazards.arm", fake, create=True):
            b5_driver._production_arm(context)
        return seen["config"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)

    def test_repository_acceptance_yields_its_identity_epoch(self):
        repo = Path(__file__).resolve().parents[2]
        config = self._config(SimpleNamespace(measurement_root=str(repo)))
        epochs = config["expected_epochs"]
        self.assertIsInstance(epochs, list)
        acceptance = json.loads((repo / "configs/calibration/"
                                 "calibration_acceptance_d079_v2_n24_25g83_r2.json").read_text())
        self.assertEqual(epochs[0], acceptance["identity_epoch"])

    def test_unloadable_acceptance_passes_none(self):
        config = self._config(SimpleNamespace(measurement_root=self.tmp.name))
        self.assertIsNone(config["expected_epochs"])


if __name__ == "__main__":
    unittest.main()
