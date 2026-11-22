"""Explicit failed-first cases for the controls print revision 3 freeze."""

from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from . import ctl_v2_adapter as adapter
from . import test_ctl_print as fixtures
from .frozen_v3_1 import test_ctl01_hand_vectors as active


ACTIVE_V2_DIGEST = "1a0f8ab045e56d614b2872082ee02ecd7e4b356c6ec9ba54b04c6a5d4f1359e6"


def invented_windows(kit, sd_w):
    member = (kit, sha256(kit.encode()).hexdigest(), "L001")
    return tuple(adapter.analysis.HoldWindow(member, channel, width, 3, sd_w)
                 for channel in ("gpu_rail", "rail_sum", "dc_in")
                 for width in adapter.analysis.FLOOR_WINDOWS)


def run_floor_fixture(directory, mode):
    """Supply the audit's invented hold bytes and exercise the actual worker."""
    pinned_rows = invented_windows("instrument-kit-A", 0.5)
    pinned_hold = adapter.synthetic_hold()
    read_artifacts = adapter.freeze_artifacts

    def artifacts():
        return {**read_artifacts(), "hold": pinned_hold}

    def supplied_pool():
        rows = pinned_rows if mode == "current" else invented_windows("instrument-kit-B", 2.0)
        return adapter.analysis.pool_hold_windows(rows, {row.member for row in rows},
                                                  reason_enum={"synthetic_floor_unavailable"})

    with (patch.object(adapter, "freeze_artifacts", artifacts),
          patch.object(adapter, "_positive_pool", supplied_pool)):
        fixtures.worker_fixture(directory, "ok", synthetic_path=True)


class TestControlsReleaseFreeze(unittest.TestCase):
    def test_stage2_floor_units_depend_on_pinned_hold(self):
        publications = []
        floor_values = []
        for mode in ("current", "stale"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as temporary:
                root = Path(temporary)
                for side in ("public", "private"):
                    (root / side / "lm-ctl-01").mkdir(parents=True)
                launcher = ("import sys; from pathlib import Path; from tests.contracts.cadence_looks."
                            "ctl_print_release_acceptance import run_floor_fixture; "
                            "run_floor_fixture(Path(sys.argv[1]), sys.argv[2])")
                result = subprocess.run([sys.executable, "-B", "-c", launcher, temporary, mode],
                                        cwd=fixtures.ROOT, capture_output=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
                self.assertTrue((root / "first-read").exists())
                public = (root / "public" / "lm-ctl-01" / "PUBLIC.json").read_bytes()
                self.assertEqual(set(json.loads(public)), {"commit", "look_id", "manifest_sha256", "n_legs",
                                                              "stage1_sha256"})
                publications.append(public)
                output = root / "private" / "lm-ctl-01" / "synthetic-output" / "controls.json"
                printed = json.loads(output.read_bytes())
                floor = printed["legs"][1]["channels"]["gpu_rail"]["hidden"]["floor"]
                floor_values.append((floor["joules"], floor["floor_j"], floor["units"]))
        self.assertEqual(len(publications), 2)
        self.assertEqual(publications[0], publications[1])
        self.assertEqual(floor_values, [(14.0, 2.0, 7.0), (14.0, 2.0, 7.0)])

    def test_recovery_acceptance_selects_the_authorized_v31_case(self):
        fixtures.TestControlsRelease("test_v3_and_v31_have_independent_verified_inventories").debug()
        module = "tests.contracts.cadence_looks"
        case = "test_A_06_incomplete_recovery"
        with active.frozen_kernel():
            historical = import_module(f"{module}.frozen_v3.test_ctl01_print_v2")
            approved = import_module(f"{module}.frozen_v3_1.test_ctl01_print_v2")
            historical_result = historical.Suite(case).run()
            self.assertFalse(historical_result.errors)
            self.assertEqual(len(historical_result.failures), 1)
            detail = historical_result.failures[0][1]
            self.assertIn("(None, 'recovery_incomplete')", detail)
            self.assertIn("(None, 'incomplete_recovery')", detail)
            approved.Suite(case).debug()
            with patch.object(active, "V2_DIGEST", ACTIVE_V2_DIGEST), patch.object(active, "v2", approved, create=True):
                active.TestIndependentHandVectors.setUpClass()
                active.TestIndependentHandVectors("test_V6_recovery_and_reason_precedence").debug()
