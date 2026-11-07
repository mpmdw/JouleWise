"""End to end: R1 driver -> WP15 runtime (separate processes) on the synthetic world.

The driver runs in this process with only its ``sudo``/``pmset`` boundary
faked (FakeWorld); every runtime segment is a real subprocess of
``scripts/align_r1_runtime.py`` whose argv comes from an inputs file's
``WP15.runtime_entrypoint`` list, configured with the synthetic backend
(fake clock, SMC, PM status, powermetrics rail, native MLX stream, ps, pmset).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_rehearsal as r1
from tests.align import r1_synthetic as rs
from tests.align.test_r1_rehearsal import NOON_SAFE, FakeWorld

TMP = os.environ.get("TMPDIR")


class DriverRuntimeTests(unittest.TestCase):
    def setUp(self):
        clock = patch.object(r1, "_now_local", lambda: NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)

    def boundary(self, world, mode_file=None):
        real = r1._run

        def runner(argv):
            if "--r1-kind" in argv:
                return real(argv)          # the real runtime subprocess
            result = world(argv)           # sudo / pmset only
            if mode_file is not None:      # the host state the runtime's ruling 7 reader sees
                Path(mode_file).write_text(str(world.mode))
            return result
        return runner

    def inputs(self, root, config):
        path = root / "inputs.json"
        path.write_text(json.dumps({"WP15": {"runtime_entrypoint": [
            "scripts/align_r1_runtime.py", "--config", str(config)]}}))
        return path

    def test_full_rehearsal_through_the_runtime(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            mode_file = root / "ac_powermode"
            mode_file.write_text("0")
            config = rs.synthetic_config(root / "cfg", powermode_file=str(mode_file))
            world = FakeWorld()
            argv = ["--output", str(root / "align-r1"), "--registration", str(root / "r1_slots.json"),
                    "--power-marker", str(root / "marker"), "--runtime-entrypoint", str(self.inputs(root, config)),
                    "--synthetic"]
            with patch.object(r1, "_run", self.boundary(world, mode_file)):
                rc = r1.main(argv)
            result = json.loads((root / "align-r1/r1_result.json").read_text())
            self.assertEqual(rc, 0, result.get("error"))
            self.assertEqual(world.mode, 0)
            registration = json.loads((root / "r1_slots.json").read_text())
            self.assertEqual(registration["source"], "R1 synthetic rehearsal")
            step = json.loads((root / "align-r1" / rt.STEP_D_SEGMENT / rt.RESULT_NAME).read_text())
            self.assertEqual(registration["slots"], step["slots"])
            for row in registration["deadman_budget"]:
                self.assertAlmostEqual(row["T_dead_s"], step["slots"]["T_dead"])
            self.assertIn(registration["u5"]["verdict"], ("pass", "fail", "inconclusive"))
            self.assertEqual(registration["high_power"]["verdict"], "not_adopted")   # no synthetic decline
            self.assertGreater(registration["battery"]["drain_pct_per_h"]["D"], 0)
            self.assertGreater(registration["battery"]["drain_pct_per_h"]["30B"], 0)
            # Every accepted segment ran in its canonical directory and closed its custody.
            for phase in result["phases"]:
                record = json.loads((Path(phase.get("output_dir", root / "align-r1/harvest"))
                                     / rt.CUSTODY_NAME).read_text())
                self.assertEqual(record["status"], "complete", phase["name"])
            self.assertTrue(all(p.get("result", {}).get("backend") == "synthetic" for p in result["phases"]))
            # Ruling 7 through the real runtime: the B leg ran (and recorded) High Power.
            b_leg = [p for p in result["phases"] if p["name"] == "high_power_B"][0]
            self.assertEqual(b_leg["result"]["ac_powermode"]["value"], 2)
            self.assertEqual(registration["slots_ac_powermode"], 0)
            self.assertEqual(registration["thermometry"]["bar"], registration["thermometry"]["D"]["status"])

    def test_term_reaches_the_runtime_which_closes_its_custody_before_exit(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            world = FakeWorld()
            segment = root / "align-r1" / "step_30b"
            argv = ["--output", str(root / "align-r1"), "--registration", str(root / "r1_slots.json"),
                    "--power-marker", str(root / "marker"), "--runtime-entrypoint", str(self.inputs(root, config)),
                    "--synthetic"]

            def signal_in_step_30b():
                deadline = time.monotonic() + 300
                bundle = segment / "runs" / "align-v4-r1-step-30b" / "outputs" / "align_thermal.jsonl"
                while not bundle.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                os.kill(os.getpid(), signal.SIGTERM)
            thread = threading.Thread(target=signal_in_step_30b, daemon=True)
            thread.start()
            with patch.object(r1, "_run", self.boundary(world)):
                rc = r1.main(argv)
            thread.join()
            self.assertEqual(rc, 4)
            self.assertEqual(world.mode, 0)
            self.assertEqual(json.loads((root / "align-r1/r1_result.json").read_text())["status"], "aborted")
            record = json.loads((segment / rt.CUSTODY_NAME).read_text())
            self.assertEqual((record["status"], record["signal"]), ("aborted", signal.SIGTERM))
            bundle = segment / "runs" / "align-v4-r1-step-30b"
            self.assertTrue((bundle / "summary_metrics.json").exists())
            last = json.loads((bundle / "outputs/align_thermal.jsonl").read_text().splitlines()[-1])
            self.assertEqual(last["kind"], "session_end")


if __name__ == "__main__":
    unittest.main()
