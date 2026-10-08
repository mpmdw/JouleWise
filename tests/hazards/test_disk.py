"""Disk hazard: statvfs free space against planned bytes x copies + 20 GiB."""
from __future__ import annotations

import os
import tempfile
import unittest
from types import SimpleNamespace

from joulewise.hazards import base, disk
from tests.hazards.fakes import FakeClocks

GIB = disk.GIB
LIMITS = {"planned_bytes": int(21.2 * GIB), "headroom_bytes": 20 * GIB, "low_bytes": 10 * GIB}


def fake_fs(volumes):
    """volumes: {path: (device, free_bytes)}"""

    def statvfs(path):
        if path not in volumes:
            raise FileNotFoundError(2, "No such file or directory", path)
        return SimpleNamespace(f_bavail=volumes[path][1] // 4096, f_frsize=4096,
                               f_blocks=10**9)

    def stat(path):
        return SimpleNamespace(st_dev=volumes[path][0])

    return statvfs, stat


def measure(targets, volumes):
    statvfs, stat = fake_fs(volumes)
    return disk.measure(base.Context(clocks=FakeClocks()), targets=targets, statvfs=statvfs, stat=stat)


class DiskJudgeTests(unittest.TestCase):
    def test_264_gib_free_passes_alpha(self):
        verdict = disk.judge(measure([disk.planned_target("/runs"), disk.planned_target("/backup")],
                                     {"/runs": (1, 264 * GIB), "/backup": (2, 900 * GIB)}), LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)

    def test_free_space_below_the_requirement_refuses(self):
        verdict = disk.judge(measure([disk.planned_target("/runs")], {"/runs": (1, 40 * GIB)}), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("41.2 GiB required", verdict.reasons[0])

    def test_copies_on_one_volume_add_up(self):
        targets = [disk.planned_target("/runs"), disk.planned_target("/runs-backup")]
        volumes = {"/runs": (1, 55 * GIB), "/runs-backup": (1, 55 * GIB)}
        verdict = disk.judge(measure(targets, volumes), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)  # 2 x 21.2 + 20 = 62.4 GiB on one volume
        self.assertEqual(verdict.observed["volumes"][0]["copies"], 2)

    def test_a_volume_is_judged_on_its_smallest_free_reading(self):
        # Two paths on one volume read a moment apart: the lower reading binds.
        targets = [disk.planned_target("/runs"), {"path": "/runs/archive", "copies": 0}]
        volumes = {"/runs": (1, 45 * GIB), "/runs/archive": (1, 40 * GIB)}
        verdict = disk.judge(measure(targets, volumes), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertEqual(verdict.observed["volumes"][0]["free_bytes"], 40 * GIB)

    def test_backup_destination_needs_its_own_headroom(self):
        targets = [disk.planned_target("/runs"), disk.planned_target("/backup")]
        verdict = disk.judge(measure(targets, {"/runs": (1, 264 * GIB), "/backup": (2, 30 * GIB)}),
                             LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("/backup", verdict.reasons[0])

    def test_missing_target_is_unmeasured(self):
        verdict = disk.judge(measure([disk.planned_target("/absent")], {}), LIMITS)
        self.assertEqual(verdict.status, base.UNMEASURED)

    def test_in_window_low_marker_threshold(self):
        measurement = measure([disk.planned_target("/runs")], {"/runs": (1, 9 * GIB)})
        self.assertEqual(disk.low(measurement, LIMITS["low_bytes"])[0]["path"], "/runs")
        measurement = measure([disk.planned_target("/runs")], {"/runs": (1, 11 * GIB)})
        self.assertEqual(disk.low(measurement, LIMITS["low_bytes"]), [])

    def test_real_statvfs_reads(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            measurement = disk.measure(base.Context(), targets=[disk.planned_target(directory)])
            self.assertIsNone(measurement.error)
            self.assertGreater(measurement.values["targets"][0]["free_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
