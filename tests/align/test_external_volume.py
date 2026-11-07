"""External log volume rule: census, arm check, routing, guard, preparation printer.

Every system call is faked; no volume, diskutil, mdutil or tmutil is touched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from joulewise.align.apple import external_volume as ev

UUID = "6B1C1E2A-0F3D-4C5B-9A8E-7D6C5B4A3F21"
OTHER = "11111111-2222-3333-4444-555555555555"
ROOT = Path(__file__).resolve().parents[2]

BASE_MOUNT = """/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)
devfs on /dev (devfs, local, nobrowse)
/dev/disk3s6 on /System/Volumes/VM (apfs, local, noexec, journaled, noatime, nobrowse)
/dev/disk3s5 on /System/Volumes/Data (apfs, local, journaled, nobrowse, protect, root data)
map auto_home on /System/Volumes/Data/home (autofs, automounted, nobrowse)
"""
EXT_LINE = "/dev/disk6s1 on /Volumes/JW-EXT (apfs, local, nodev, nosuid, journaled)\n"


def info(*, internal, uuid=None, fs="apfs", bus="PCI-Express", writable=True, name="x"):
    value = {"Internal": internal, "FilesystemType": fs, "BusProtocol": bus, "WritableVolume": writable,
             "VolumeName": name}
    if uuid is not None:
        value["VolumeUUID"] = uuid
    return plistlib.dumps(value).decode()


class FakeRun:
    def __init__(self, mount_text, infos, *, mdutil="/Volumes/JW-EXT:\n\tIndexing disabled.\n",
                 tmutil="[Excluded]\t/Volumes/JW-EXT\n"):
        self.mount_text, self.infos, self.mdutil, self.tmutil = mount_text, infos, mdutil, tmutil
        self.calls = []

    def __call__(self, argv):
        argv = list(argv)
        self.calls.append(argv)
        if argv[0] == "/sbin/mount":
            return subprocess.CompletedProcess(argv, 0, self.mount_text, "")
        if argv[:3] == [ev.DISKUTIL, "info", "-plist"]:
            text = self.infos.get(argv[3])
            if text is None:
                return subprocess.CompletedProcess(argv, 1, "", "no such disk")
            return subprocess.CompletedProcess(argv, 0, text, "")
        if argv[0] == ev.MDUTIL:
            return subprocess.CompletedProcess(argv, 0, self.mdutil, "")
        if argv[0] == ev.TMUTIL:
            return subprocess.CompletedProcess(argv, 0, self.tmutil, "")
        raise AssertionError(argv)


INTERNAL_INFOS = {"/dev/disk3s1s1": info(internal=True, uuid=OTHER), "/dev/disk3s6": info(internal=True),
                  "/dev/disk3s5": info(internal=True)}


def qualification_config(**overrides):
    value = {"schema": ev.SCHEMA, "status": "qualification", "amendment": "DRAFT", "allowlist": [UUID],
             "mount_point": "/Volumes/JW-EXT", "log_mode": "internal"}
    value.update(overrides)
    return ev.validate_config(value)


def attached_run(**kwargs):
    infos = dict(INTERNAL_INFOS)
    infos["/dev/disk6s1"] = info(internal=False, uuid=kwargs.pop("uuid", UUID), fs=kwargs.pop("fs", "apfs"))
    return FakeRun(BASE_MOUNT + kwargs.pop("ext_line", EXT_LINE), infos, **kwargs)


def all_present(_path):
    return True


class ConfigTests(unittest.TestCase):
    def test_default_and_committed_config_are_off(self):
        self.assertEqual(ev.validate_config(None)["status"], "off")
        committed = ev.load_config(ROOT / "configs/align/v4/external_log_volume.json")
        self.assertEqual(committed["status"], "off")
        self.assertEqual(committed["allowlist"], [])
        example = ev.load_config(ROOT / "configs/align/v4/external_log_volume.qualification.example.json")
        self.assertEqual(example["status"], "qualification")

    def test_non_off_status_requires_amendment_uuid_and_mount_point(self):
        bad = [
            {"amendment": None},
            {"allowlist": []},
            {"allowlist": [UUID, OTHER]},
            {"allowlist": [UUID.lower()]},
            {"mount_point": "/tmp/JW-EXT"},
            {"mount_point": "/Volumes/a/b"},
            {"log_mode": "everything"},
            {"status": "on"},
        ]
        for change in bad:
            with self.subTest(change=change), self.assertRaises(ev.ConfigError):
                qualification_config(**change)

    def test_unknown_key_and_unreadable_file_refuse(self):
        with self.assertRaises(ev.ConfigError):
            ev.validate_config({"schema": ev.SCHEMA, "status": "off", "spotlight": "whatever"})
        with self.assertRaises(ev.ConfigError):
            ev.load_config("/nonexistent/external_log_volume.json")


class CensusTests(unittest.TestCase):
    def test_internal_only_census(self):
        result = ev.census(FakeRun(BASE_MOUNT, INTERNAL_INFOS))
        self.assertEqual(result["external"], [])
        self.assertEqual(result["errors"], [])

    def test_network_share_and_disk_image_are_external(self):
        text = BASE_MOUNT + "//ed@nas/share on /Volumes/share (smbfs, nodev, nosuid, mounted by ed)\n" \
            + "/dev/disk7s1 on /Volumes/Installer (hfs, local, nodev, nosuid, read-only)\n"
        infos = dict(INTERNAL_INFOS, **{"/dev/disk7s1": info(internal=True, fs="hfs", bus="Disk Image")})
        result = ev.census(FakeRun(text, infos))
        self.assertEqual(sorted(r["mount_point"] for r in result["external"]), ["/Volumes/Installer", "/Volumes/share"])

    def test_diskutil_failure_is_an_error(self):
        infos = dict(INTERNAL_INFOS)
        del infos["/dev/disk3s6"]
        result = ev.census(FakeRun(BASE_MOUNT, infos))
        self.assertTrue(result["errors"])

    def test_one_transient_diskutil_failure_is_retried(self):
        # Executing review round 4 LOW-3: one failed read must not refuse R1.
        class Flaky(FakeRun):
            failed = set()

            def __call__(self, argv):
                argv = list(argv)
                if argv[:3] == [ev.DISKUTIL, "info", "-plist"] and argv[3] not in self.failed:
                    self.failed.add(argv[3])
                    self.calls.append(argv)
                    return subprocess.CompletedProcess(argv, 1, "", "transient")
                return super().__call__(argv)
        run = Flaky(BASE_MOUNT, INTERNAL_INFOS)
        result = ev.census(run)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["external"], [])
        retried = [r for r in result["mounts"] if r.get("diskutil_failures")]
        self.assertTrue(retried)
        self.assertTrue(all(r["class"] == "internal" for r in retried))
        # Two failures on the same mount still refuse.
        infos = dict(INTERNAL_INFOS)
        del infos["/dev/disk3s6"]
        run = FakeRun(BASE_MOUNT, infos)
        self.assertTrue(ev.census(run)["errors"])
        self.assertEqual(sum(1 for c in run.calls if c[-1] == "/dev/disk3s6"), 2)


class ArmCheckTests(unittest.TestCase):
    def test_off_refuses_any_external_volume_like_today(self):
        run = attached_run()
        verdict = ev.arm_check(ev.validate_config(None), ev.census(run), run=run, exists=all_present)
        self.assertEqual(verdict["verdict"], ev.REFUSE)
        self.assertIn("external_volume_mounted:/Volumes/JW-EXT", verdict["reasons"])
        self.assertFalse(verdict["claim_eligible"])

    def test_off_passes_without_external_volumes(self):
        run = FakeRun(BASE_MOUNT, INTERNAL_INFOS)
        verdict = ev.arm_check(ev.validate_config(None), ev.census(run), run=run)
        self.assertEqual(verdict["verdict"], ev.PASS)

    def test_prepared_allowlisted_volume_passes_in_qualification_not_claim(self):
        run = attached_run()
        verdict = ev.arm_check(qualification_config(), ev.census(run), run=run, exists=all_present)
        self.assertEqual(verdict["verdict"], ev.PASS, verdict["reasons"])
        self.assertFalse(verdict["claim_eligible"])
        active = ev.arm_check(qualification_config(status="active"), ev.census(run), run=run, exists=all_present)
        self.assertTrue(active["claim_eligible"])

    def test_each_preparation_failure_refuses(self):
        cases = {
            "spotlight_indexing_off": dict(mdutil="/Volumes/JW-EXT:\n\tIndexing enabled.\n"),
            "time_machine_excluded": dict(tmutil="[Included]\t/Volumes/JW-EXT\n"),
            "apfs": dict(fs="exfat", ext_line="/dev/disk6s1 on /Volumes/JW-EXT (exfat, local, nodev)\n"),
            "ownership_enabled": dict(ext_line="/dev/disk6s1 on /Volumes/JW-EXT (apfs, local, noowners)\n"),
        }
        for check, kwargs in cases.items():
            with self.subTest(check=check):
                run = attached_run(**kwargs)
                verdict = ev.arm_check(qualification_config(), ev.census(run), run=run, exists=all_present)
                self.assertEqual(verdict["verdict"], ev.REFUSE)
                self.assertIn(f"volume_check_failed:{check}", verdict["reasons"])

    def test_fseventsd_logging_on_refuses(self):
        run = attached_run()
        verdict = ev.arm_check(qualification_config(), ev.census(run), run=run,
                               exists=lambda path: not path.endswith("no_log"))
        self.assertIn("volume_check_failed:fseventsd_no_log", verdict["reasons"])

    def test_unlisted_second_volume_and_absence_refuse(self):
        run = attached_run(uuid=OTHER)
        verdict = ev.arm_check(qualification_config(), ev.census(run), run=run, exists=all_present)
        self.assertIn("external_volume_not_allowlisted:/Volumes/JW-EXT", verdict["reasons"])
        self.assertIn("allowlisted_volume_absent", verdict["reasons"])
        run = FakeRun(BASE_MOUNT, INTERNAL_INFOS)
        verdict = ev.arm_check(qualification_config(), ev.census(run), run=run)
        self.assertEqual(verdict["reasons"], ["allowlisted_volume_absent"])

    def test_census_error_refuses_in_every_status(self):
        for config in (ev.validate_config(None), qualification_config()):
            verdict = ev.arm_check(config, {"external": [], "errors": ["mount exit 1"]})
            self.assertEqual(verdict["verdict"], ev.REFUSE)


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.passed = {"verdict": ev.PASS}

    def test_custody_and_tmpdir_never_external(self):
        for mode in ev.LOG_MODES:
            routed = ev.route(qualification_config(log_mode=mode), self.passed,
                              internal_session_root="/Users/edr/night-x/s", session_id="align-v4-1")
            self.assertFalse(routed["paths"]["custody_root"].startswith("/Volumes/"))
            self.assertFalse(routed["paths"]["tmpdir"].startswith("/Volumes/"))

    def test_modes(self):
        backup = ev.route(qualification_config(log_mode="backup"), self.passed,
                          internal_session_root="/i/s", session_id="sid")
        self.assertEqual(backup["paths"]["runs_parent"], "/i/s/runs-parent")
        self.assertEqual(backup["paths"]["claim_backup"], "/Volumes/JW-EXT/JouleWise/sid/backup-claim")
        direct = ev.route(qualification_config(log_mode="direct"), self.passed,
                          internal_session_root="/i/s", session_id="sid")
        self.assertEqual(direct["paths"]["runs_parent"], "/Volumes/JW-EXT/JouleWise/sid/runs-parent")
        internal = ev.route(qualification_config(log_mode="internal"), self.passed,
                            internal_session_root="/i/s", session_id="sid")
        self.assertFalse(internal["external_used"])

    def test_refused_or_off_routes_internal(self):
        refused = ev.route(qualification_config(log_mode="direct"), {"verdict": ev.REFUSE},
                           internal_session_root="/i/s", session_id="sid")
        self.assertEqual(refused["fallback"], "arm_check_refused")
        self.assertEqual(refused["paths"]["runs_parent"], "/i/s/runs-parent")
        off = ev.route(ev.validate_config(None), self.passed, internal_session_root="/i/s", session_id="sid")
        self.assertEqual(off["fallback"], "status_off")

    def test_session_id_must_be_one_component(self):
        with self.assertRaises(ev.ConfigError):
            ev.route(qualification_config(), self.passed, internal_session_root="/i", session_id="../x")


class GuardTests(unittest.TestCase):
    def test_loss_switches_internal_for_good_and_journals_once(self):
        devices = {"/Volumes/JW-EXT": 9, "/Volumes": 1}
        stat = lambda path: SimpleNamespace(st_dev=devices[path])  # noqa: E731
        routed = ev.route(qualification_config(log_mode="direct"), {"verdict": ev.PASS},
                          internal_session_root="/i/s", session_id="sid")
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / "volume.jsonl"
            guard = ev.RouteGuard(routed, journal_path=journal, stat=stat, now=lambda: 1.0)
            self.assertEqual(guard.target("runs_parent"), "/Volumes/JW-EXT/JouleWise/sid/runs-parent")
            devices["/Volumes/JW-EXT"] = 1  # unmounted: the mount point is a plain directory again
            self.assertEqual(guard.target("runs_parent"), "/i/s/runs-parent")
            devices["/Volumes/JW-EXT"] = 12  # remounted (new device): still internal
            self.assertEqual(guard.target("claim_backup"), "/i/s/backup-claim")
            lines = journal.read_text().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["kind"], "external_volume.lost")

    def test_unmounted_at_bind_is_lost(self):
        stat = lambda path: SimpleNamespace(st_dev=1)  # noqa: E731
        routed = ev.route(qualification_config(log_mode="backup"), {"verdict": ev.PASS},
                          internal_session_root="/i/s", session_id="sid")
        with tempfile.TemporaryDirectory() as tmp:
            guard = ev.RouteGuard(routed, journal_path=Path(tmp) / "j.jsonl", stat=stat)
            self.assertEqual(guard.target("claim_backup"), "/i/s/backup-claim")

    def test_journal_on_external_volume_refused(self):
        routed = ev.route(qualification_config(log_mode="backup"), {"verdict": ev.PASS},
                          internal_session_root="/i/s", session_id="sid")
        with self.assertRaises(ev.ConfigError):
            ev.RouteGuard(routed, journal_path="/Volumes/JW-EXT/j.jsonl",
                          stat=lambda p: SimpleNamespace(st_dev=2 if p.endswith("EXT") else 1))


class PreparePlanTests(unittest.TestCase):
    def test_plan_is_print_only_and_guards_internal_disks(self):
        lines = ev.prepare_plan("disk6")
        text = "\n".join(lines)
        self.assertIn("sudo mdutil -i off /Volumes/JW-EXT", text)
        self.assertIn(".fseventsd/no_log", text)
        self.assertIn("tmutil addexclusion", text)
        self.assertIn("enableOwnership", text)
        erase = [line for line in lines if "eraseDisk" in line]
        self.assertTrue(erase and all(line.lstrip().startswith("#") for line in erase))
        for device in ("disk0", "disk3", "disk6s1", "/dev/disk6", "disk6; rm -rf /"):
            with self.subTest(device=device), self.assertRaises(ev.ConfigError):
                ev.prepare_plan(device)

    def test_cli_prepare_plan_executes_nothing(self):
        import contextlib
        import io
        from scripts import align_external_volume as cli
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["prepare-plan", "--device", "disk6"]), 0)
        self.assertIn("DRY RUN", out.getvalue())


if __name__ == "__main__":
    unittest.main()
