"""Main reads lane plans but cannot admit High Power mode before enforcement merges."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
import unittest
from unittest import mock

from tests import test_night_agent_install as install_tests
from tests import test_run_night as driver_tests
from tests.fixtures.b5_plan import fake_window


REASON = "night_ac_powermode_unenforced_on_this_head"


class NightACPowermodeTests(unittest.TestCase):
    def driver_fixture(self, *, hazard=False, mode=None):
        fixture = driver_tests.NightDriverTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.addCleanup(fixture.tearDown)
        if hazard:
            mapping = fake_window.hazard_plan_mapping(
                fixture.root, plan_id="synthetic-high-power", custody_root=fixture.custody,
                t0_epoch_s=fixture.t0_epoch_s, authored_epoch_s=fixture.t0_epoch_s - 1)
        else:
            mapping = json.loads(fixture.plan_path.read_text())
        if mode is not None:
            mapping["ac_powermode"] = mode
        fixture.plan_path.write_text(json.dumps(mapping))
        return fixture

    def test_preflight_refuses_two_but_keeps_absent_and_zero_for_legacy_and_hazard(self):
        for hazard in (False, True):
            for mode in (None, 0, 2):
                with self.subTest(hazard=hazard, mode=mode):
                    fixture = self.driver_fixture(hazard=hazard, mode=mode)
                    # Reader compatibility is independent of execution admission.
                    self.assertEqual(mode, fixture.driver._load_plan(fixture.plan_path).ac_powermode)
                    result = subprocess.run(
                        [sys.executable, "-B", str(driver_tests.SCRIPT_PATH), "preflight",
                         "--plan", str(fixture.plan_path)], capture_output=True, text=True,
                        env={"HOME": str(fixture.root), "PYTHONNOUSERSITE": "1", "PATH": "/usr/bin:/bin"},
                        timeout=15)
                    self.assertEqual(3 if mode == 2 else 0, result.returncode, result.stderr)
                    if mode == 2:
                        self.assertIn(REASON, result.stderr)
                        self.assertNotIn('"preflight": "ok"', result.stdout)
                    else:
                        self.assertEqual("ok", json.loads(result.stdout)["preflight"])
                    self.assertFalse((fixture.custody / "night").exists())

    def test_run_refuses_two_with_a_registered_record_before_any_chain_or_hazard_arm(self):
        from joulewise.b5 import driver as hazard_driver
        for hazard in (False, True):
            with self.subTest(hazard=hazard):
                fixture = self.driver_fixture(hazard=hazard, mode=2)
                with mock.patch.object(fixture.driver.subprocess, "Popen") as popen, \
                        mock.patch.object(hazard_driver, "run_hazard_night") as run_hazard:
                    code = fixture.driver.run_night(fixture.plan_path)
                self.assertEqual(fixture.driver.EXIT_REFUSED, code)
                popen.assert_not_called()
                run_hazard.assert_not_called()
                night = fixture.custody / "night"
                refusal = json.loads((night / "refusal.json").read_bytes())
                self.assertEqual(REASON, refusal["refusal"]["reason"])
                self.assertEqual([], fixture.driver.validate_refusal(refusal))
                self.assertEqual(REASON, json.loads((night / "result.json").read_bytes())["aborted_reason"])
                self.assertFalse((night / "chain.started").exists())
                fixture.driver.run_courier.assert_called_once()

    def test_dry_arm_refuses_two_without_creating_a_night_record(self):
        from joulewise.b5 import driver as hazard_driver
        fixture = self.driver_fixture(hazard=True, mode=2)
        error = io.StringIO()
        with mock.patch.object(hazard_driver, "dry_arm") as arm, \
                mock.patch("sys.stderr", error):
            code = fixture.driver.run_night(fixture.plan_path, dry_arm=True)
        self.assertEqual(fixture.driver.EXIT_REFUSED, code)
        self.assertIn(REASON, error.getvalue())
        arm.assert_not_called()
        self.assertFalse((fixture.custody / "night").exists())

    def test_run_absent_and_zero_still_launch_the_admitted_chain(self):
        for mode in (None, 0):
            with self.subTest(mode=mode):
                fixture = self.driver_fixture()
                mapping = json.loads(fixture.plan_path.read_bytes())
                if mode is not None:
                    mapping["ac_powermode"] = mode
                fixture.plan_path.write_text(json.dumps(mapping))
                code, calls = fixture._run_night()
                self.assertEqual(fixture.driver.EXIT_GO, code)
                self.assertEqual([["/bin/zsh", str(fixture.chain)]], calls)
                result = json.loads((fixture.custody / "night/result.json").read_bytes())
                self.assertEqual("GO", result["verdict"])

    def test_installer_validation_refuses_two_before_commands_or_rendering(self):
        from types import SimpleNamespace
        from joulewise import night_agent_install as installer
        for hazard in (False, True):
            with self.subTest(hazard=hazard):
                fixture = self.driver_fixture(hazard=hazard, mode=2)
                # Keep the otherwise valid plan fresh so the mode guard is reached.
                mapping = json.loads(fixture.plan_path.read_bytes())
                mapping["authored_epoch_s"] = time.time() - 1
                fixture.plan_path.write_text(json.dumps(mapping))
                args = SimpleNamespace(plan=fixture.plan_path)
                with mock.patch.object(installer.subprocess, "run") as run, \
                        self.assertRaises(installer.Refused) as caught:
                    installer.validate_install(args, driver_tests.REPO_ROOT)
                self.assertIn(REASON, str(caught.exception))
                run.assert_not_called()
                self.assertFalse((fixture.custody / "night").exists())

    def test_installer_entry_point_renders_absent_and_zero_but_refuses_two(self):
        for mode in (None, 0, 2):
            with self.subTest(mode=mode):
                fixture = install_tests.HazardPackInstallTests()
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                mapping = json.loads(fixture.plan_path.read_bytes())
                if mode is not None:
                    mapping["ac_powermode"] = mode
                fixture.plan_path.write_text(json.dumps(mapping))
                rendered = fixture.root / "rendered"
                with mock.patch.dict(os.environ, {"HOME": str(fixture.root)}):
                    code, _, error, calls = fixture.install("--render-only", str(rendered))
                if mode == 2:
                    self.assertEqual(3, code, error)
                    self.assertIn(REASON, error)
                    self.assertEqual([], calls)
                    self.assertFalse(rendered.exists())
                    continue
                self.assertEqual(0, code, error)
                self.assertTrue(all((rendered / (label + ".plist")).is_file()
                                    for label in install_tests.LABELS))


if __name__ == "__main__":
    unittest.main()
