"""The driver's pre-launch lineage check agrees with what members verify.

Cooldown smoke runs 1 and 2 (2026-10-06) refused every real HAZARD_PACK window
with ``night_lineage_unpublished``: the driver read ``kern.bootsessionuuid`` in
sysctl's uppercase text and compared it with the lineage's canonical lowercase
id, and it required the locator to name the WINDOW plan id although the
lineage carries the PACK plan id, which is what members compare with the pack's
plan tree (``controller``: ``plan["plan_id"] != lineage["plan_id"]`` refuses).

The earlier unit tests could not see either defect: ``test_b5_driver_p2``'s F2
tests passed ``boot_session_uuid=None`` (so the boot comparison was skipped)
and a mock plan whose ``plan_id`` equalled the fixture lineage's plan id (the
fixture's pack plan id and window id are the same string); ``test_b5_driver``'s
adapter test replaced ``window_lineage`` with a fake and used the boot "BOOT".

These tests run the REAL ``_production_lineage`` publication and then the REAL
``_production_lineage_check`` on the production boot seam, for a window whose
plan id differs from its pack plan id, and then the members' own
authenticator on the same runs roots.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import arm_readiness, window_lineage
from joulewise.b5 import driver as b5_driver
from tests import test_window_lineage as fixture
from tests import child_guard

REPO_ROOT = Path(__file__).resolve().parents[1]
WINDOW_PLAN_ID = "REH-window-plan-differs-from-pack-20261006T0000Z"
UPPER_BOOT = "ABCDEF01-2345-4678-9ABC-DEF012345678"


def hazard_window(w: SimpleNamespace, *, bracket_session_id: str = fixture.SESSION_ID) -> dict:
    return {
        "pack": {"pack_root": str(w.pack), "pack_id": fixture.PACK_ID, "pack_plan_id": fixture.PLAN_ID,
                 "window_id": fixture.WINDOW_ID, "pack_sha256": "0" * 64},
        "bracket_session_id": bracket_session_id,
        "bindings": {"pre_attempt_id": fixture.PRE_ATTEMPT, "post_attempt_id": fixture.POST_ATTEMPT},
        "runs_roots": {"claim": str(w.claim), "bound": str(w.bound)},
    }


def lineage_request(w: SimpleNamespace, boot: str | None, window: dict | None = None) -> b5_driver.LineageRequest:
    window = hazard_window(w) if window is None else window
    return b5_driver.LineageRequest(
        plan=SimpleNamespace(plan_id=WINDOW_PLAN_ID), plan_path=w.base / "window_plan.json",
        custody_root=w.custody, night_dir=w.night, hazard_window=window,
        claim_runs_root=w.claim, bound_runs_root=w.bound, arm_record_path=None,
        arm_decision_path=w.arm_decision, boot_session_uuid=boot)


class _UppercaseSysctl:
    """``subprocess.run`` that answers ``sysctl -n kern.bootsessionuuid`` the way
    macOS does (uppercase, newline) and passes every other command through."""

    def __init__(self) -> None:
        self.real = subprocess.run
        self.calls = 0

    def __call__(self, argv, *args, **kwargs):
        if tuple(argv) == ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"):
            self.calls += 1
            text = UPPER_BOOT + "\n"
            stdout = text if (kwargs.get("text") or kwargs.get("universal_newlines")) else text.encode()
            return subprocess.CompletedProcess(list(argv), 0, stdout, "" if isinstance(stdout, str) else b"")
        return self.real(argv, *args, **kwargs)


class ProductionLineagePublishThenCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.w = fixture.build_window(Path(self.directory.name), publish=False)

    def publish_and_check(self) -> tuple[dict, dict]:
        boot = b5_driver.production_seams(REPO_ROOT).boot_session_uuid()
        published = b5_driver._production_lineage(lineage_request(self.w, boot))
        checks = b5_driver._production_lineage_check(lineage_request(self.w, boot))
        return published, checks

    def assert_members_accept(self, published: dict) -> None:
        lineage = published["launch_lineage"]
        tree_plan_id = fixture.json.loads((self.w.pack / "plan_tree.json").read_bytes())["plan"]["plan_id"]
        # controller._authenticated_g2b_pre_slot: plan["plan_id"] != lineage["plan_id"] refuses.
        self.assertEqual(tree_plan_id, lineage["plan_id"])
        self.assertNotEqual(WINDOW_PLAN_ID, lineage["plan_id"])
        for root in (self.w.claim, self.w.bound):
            context = arm_readiness.authenticate_campaign_launch_lineage(root)
            self.assertEqual(lineage, context["launch_lineage"])

    @unittest.skipUnless(sys.platform == "darwin", "the real kern.bootsessionuuid exists only on macOS")
    def test_real_boot_reader_publish_then_check_is_valid(self) -> None:
        raw = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"],
                             capture_output=True, text=True, check=True).stdout.strip()
        published, checks = self.publish_and_check()
        lineage = published["launch_lineage"]
        self.assertEqual(raw.lower(), lineage["collection_boot_session_id"])
        self.assertEqual((True, True), (checks["claim"]["valid"], checks["bound"]["valid"]),
                         {role: checks[role].get("error") for role in ("claim", "bound")})
        self.assert_members_accept(published)

    def test_uppercase_sysctl_publish_then_check_is_valid(self) -> None:
        sysctl = _UppercaseSysctl()
        with mock.patch("subprocess.run", sysctl):
            published, checks = self.publish_and_check()
            self.assertEqual(UPPER_BOOT.lower(), published["launch_lineage"]["collection_boot_session_id"])
            self.assertEqual((True, True), (checks["claim"]["valid"], checks["bound"]["valid"]),
                             {role: checks[role].get("error") for role in ("claim", "bound")})
            self.assert_members_accept(published)
        self.assertGreaterEqual(sysctl.calls, 2)

    def test_window_plan_id_differs_from_pack_plan_id_publish_then_check_is_valid(self) -> None:
        # Boot isolated: the request carries no boot, so publication records the
        # canonical reader's boot and the boot comparison cannot be what fails.
        published = b5_driver._production_lineage(lineage_request(self.w, None))
        checks = b5_driver._production_lineage_check(lineage_request(self.w, None))
        self.assertEqual(fixture.PLAN_ID, published["launch_lineage"]["plan_id"])
        self.assertEqual((True, True), (checks["claim"]["valid"], checks["bound"]["valid"]),
                         {role: checks[role].get("error") for role in ("claim", "bound")})
        self.assert_members_accept(published)

    def test_the_driver_boot_seam_is_the_canonical_reader(self) -> None:
        with mock.patch("subprocess.run", _UppercaseSysctl()):
            self.assertEqual(window_lineage.current_boot_session_id(),
                             b5_driver.production_seams(REPO_ROOT).boot_session_uuid())
            self.assertEqual(UPPER_BOOT.lower(), b5_driver._boot_session_uuid())

    def test_a_reboot_after_publication_is_judged_boot_changed(self) -> None:
        with mock.patch("subprocess.run", _UppercaseSysctl()):
            boot = b5_driver.production_seams(REPO_ROOT).boot_session_uuid()
            b5_driver._production_lineage(lineage_request(self.w, boot))
        other = "00000000-0000-4000-8000-000000000000"
        with mock.patch.object(window_lineage, "current_boot_session_id", return_value=other):
            checks = b5_driver._production_lineage_check(lineage_request(self.w, boot))
        self.assertEqual((False, False), (checks["claim"]["valid"], checks["bound"]["valid"]))
        self.assertEqual((True, True), (checks["claim"]["boot_changed"], checks["bound"]["boot_changed"]))
        self.assertEqual((UPPER_BOOT.lower(), other),
                         (checks["claim"]["recorded_boot_session_id"], checks["claim"]["current_boot_session_id"]))
        self.assertIn("collection boot differs", checks["claim"]["error"])

    def test_a_locator_published_for_another_window_is_not_valid(self) -> None:
        with mock.patch("subprocess.run", _UppercaseSysctl()):
            boot = b5_driver.production_seams(REPO_ROOT).boot_session_uuid()
            b5_driver._production_lineage(lineage_request(self.w, boot))
            later = hazard_window(self.w, bracket_session_id="a-later-window-calibration")
            checks = b5_driver._production_lineage_check(lineage_request(self.w, boot, later))
        self.assertEqual((False, False), (checks["claim"]["valid"], checks["bound"]["valid"]))
        self.assertIn("a-later-window-calibration", checks["bound"]["error"])


# Test hygiene (2026-10-07): a test or class in this module that leaves a child process running
# is reported as failed, and the child is stopped (tests/child_guard.py).
child_guard.guard_test_classes(globals())


if __name__ == "__main__":
    unittest.main()
