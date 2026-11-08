"""Failing-first witnesses for Opus review finding P-H1 (eng-prearm).

Run against origin/perf/2026-11-08-eng-prearm (348c4a70b) by copying this file
to tests/ and running, one module per process, with an unsymlinked TMPDIR:

    TMPDIR=<real dir> python3.13 -B -m unittest tests.test_prearm_packet_witness

Synthetic data only. Each test first proves that the ORIGINAL validator would
now refuse (run_checks raises), then asserts that packet verification refuses
too. On 348c4a70b every test fails at the second assertion: verify() returns
the stale PASS results, so the packet vouches for a check that no longer holds.
"""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from tests.git_fixture import init_git_fixture


class PrearmPacketBindsLessThanValidatorsRead(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / "air-checkout"
        self.root.mkdir()
        init_git_fixture(self.root, "-q")
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Synthetic",
                        "-c", "user.email=synthetic@example.invalid", "commit",
                        "--allow-empty", "-qm", "fixture"], check=True, capture_output=True)
        head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                       text=True).strip()
        (self.root / "scripts").mkdir()
        (self.root / "lib").mkdir()  # imported by the validator, NOT inventoried
        (self.root / "lib/helper.py").write_text("PINNED = 'v1'\n")
        self.outside = self.base / "host-state.json"  # outside root: a host observation
        self.outside.write_text('{"battery_percent": 100}\n')
        (self.root / "scripts/check.py").write_text(
            "import json, os, sys\n"
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))\n"
            "import helper\n"
            "name = sys.argv[1]\n"
            "if name == 'static_config':\n"
            "    assert os.environ.get('JW_WITNESS_PIN') == '1.0', 'environment pin'\n"
            "if name == 'kit_regeneration':\n"
            "    assert helper.PINNED == 'v1', 'imported module pin'\n"
            "if name == 'receipt_validation':\n"
            "    state = json.load(open(os.environ['JW_WITNESS_HOST_STATE']))\n"
            "    assert state['battery_percent'] >= 80, 'host observation'\n"
            "print(name + ':ok')\n")
        self.plan = {"plan_id": "synthetic-plan", "repo_head": head,
                     "measurement_head": head, "authored_epoch_s": 90}
        (self.root / "plan.json").write_text(json.dumps(self.plan))
        (self.root / "receipt.json").write_text('{"valid_until_epoch_s": 200}')
        self.recipe = {
            "schema": "joulewise.prearm_recipe.v1", "plan": "plan.json",
            "identity": {k: self.plan[k] for k in ("plan_id", "repo_head", "measurement_head")},
            "files": ["plan.json", "receipt.json"], "trees": ["scripts"],
            "receipts": [{"path": "receipt.json", "expires_field": "valid_until_epoch_s"}],
            "not_after_epoch_s": 190,
            "checks": [{"name": n, "argv": ["{python}", "-B", "{root}/scripts/check.py", n],
                        "timeout_s": 10}
                       for n in ("kit_regeneration", "plan_identity",
                                 "receipt_validation", "static_config")]}
        self.packet = self.base / "packet.json"
        self.env = {"JW_WITNESS_PIN": "1.0", "JW_WITNESS_HOST_STATE": str(self.outside)}
        from joulewise.prearm_packet import build
        with mock.patch.dict(os.environ, self.env):
            self.digest = build(self.root, self.recipe, self.packet, now=100)

    def _assert_original_refuses_and_packet_refuses(self, env):
        from joulewise.prearm_packet import PacketError, run_checks, verify
        with mock.patch.dict(os.environ, env):
            with self.assertRaises(PacketError, msg="precondition: original check now refuses"):
                run_checks(self.root, self.recipe)
            with self.assertRaises(PacketError, msg="packet vouched for a check that now refuses"):
                verify(self.root, self.recipe, self.packet, self.digest, now=101)

    def test_verify_refuses_when_execution_environment_differs_from_build_host(self):
        # Air built with pin 1.0; the MBP interpreter/env carries 2.0.
        self._assert_original_refuses_and_packet_refuses({**self.env, "JW_WITNESS_PIN": "2.0"})

    def test_verify_refuses_when_an_uninventoried_imported_module_changes(self):
        # Uncommitted edit: HEAD is unchanged, lib/ is outside the inventory.
        (self.root / "lib/helper.py").write_text("PINNED = 'v2'\n")
        self._assert_original_refuses_and_packet_refuses(self.env)

    def test_verify_refuses_to_carry_a_host_observation_across_hosts(self):
        # A recipe may label any bound script 'receipt_validation'; the packet
        # then carries the BUILD host's physical state to the arming host.
        self.outside.write_text('{"battery_percent": 40}\n')
        self._assert_original_refuses_and_packet_refuses(self.env)


if __name__ == "__main__":
    unittest.main()
