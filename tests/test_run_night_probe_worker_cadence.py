"""The calibration probe worker preserves failed cadence timing in its receipt."""

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise import night_gate
from joulewise.night_plan_writer import write_night_plan
from scripts import run_night
from tests.test_run_night import HEAD, make_probe_fixture


class ProbeWorkerCadenceTests(unittest.TestCase):
    @unittest.skipUnless(Path("/bin/zsh").is_file(), "zsh required for calibration fixture")
    def test_failed_cadence_receipt_includes_timing_and_frame_statistics(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            plan_path = root / "night_plan.json"
            plan = night_gate.NightPlan(
                plan_id="probe-fixture", receipt_class="DIAGNOSTIC_NO_PACK",
                t0_epoch_s=(int(time.time()) // 60 + 60) * 60,
                window_max_s=9000, authored_epoch_s=time.time(),
                repo_head=HEAD, measurement_root=str(root / "measurement"),
                measurement_head=HEAD, chain_path=str(root / "chain"),
                chain_sha256_path=str(root / "chain.sha256"),
                custody_root=str(root / "custody"),
                registration_path="fixture-registration",
            )
            write_night_plan(plan_path, plan)
            make_probe_fixture(root, plan_path)
            receipt_path = root / "night_probe_receipt.json"
            cadence = {
                "passed": False, "elapsed_s": 60.1, "bound_s": 55.0,
                "count": 220, "median_ms": 248, "p95_ms": 260,
                "max_ms": 312, "detail": "cadence bound exceeded",
            }
            with mock.patch.object(run_night, "_probe_cadence", return_value=cadence) as probe:
                code = run_night._probe_worker(
                    plan_path, receipt_path, root / "progress.json", time.monotonic() + 30,
                )

            self.assertEqual(2, code)
            probe.assert_called_once()
            receipt = json.loads(receipt_path.read_text())
            self.assertEqual("probe_cadence_failed", receipt["refusal_code"])
            self.assertEqual(cadence, receipt["cadence"])
            for fragment in ("elapsed_s=60.1", "bound_s=55.0", "median_ms=248", "max_ms=312"):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, receipt["detail"])


if __name__ == "__main__":
    unittest.main()
