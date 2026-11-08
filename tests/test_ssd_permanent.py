"""Synthetic-only B-unmount hooks; never execute diskutil, ioreg or log here."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import ssd_permanent as ssd

FIXTURES = Path(__file__).parent / "fixtures/ssd_permanent"
VOLUME = "33333333-3333-4333-8333-333333333333"


class FakeClock:
    def __init__(self):
        self.t = 100.0

    def monotonic(self):
        return self.t

    def time(self):
        return 1794139200.0 + self.t

    def sleep(self, seconds):
        self.t += seconds


class FakeMac:
    def __init__(self):
        self.calls = []
        self.infos = {p.stem.removeprefix("info-"): plistlib.loads(p.read_bytes())
                      for p in FIXTURES.glob("info-*.plist")}
        self.listing = plistlib.loads((FIXTURES / "list.plist").read_bytes())
        self.registry = plistlib.loads((FIXTURES / "ioreg.plist").read_bytes())
        self.service = plistlib.loads((FIXTURES / "ioreg-service.plist").read_bytes())
        self.mounts = (FIXTURES / "mount.txt").read_text()
        self.events = b""
        self.busy = False
        self.fail_log = False
        self.boot = b"SYNTHETIC-BOOT-A\n"
        self.mounted_at = None

    def runner(self, argv, **kwargs):
        self.calls.append(list(argv))
        assert kwargs["timeout"] > 0
        command = Path(argv[0]).name
        rc, out, err = 0, b"", b""
        if command == "diskutil":
            if argv[1:3] == ["list", "-plist"]:
                out = plistlib.dumps(self.listing)
            elif argv[1:3] == ["info", "-plist"]:
                node = next((v for k, v in self.infos.items()
                             if argv[3] == k or argv[3] in
                             [v.get("VolumeUUID"), v.get("DiskUUID")]), None)
                if node is None:
                    rc, err = 1, b"not found"
                else:
                    out = plistlib.dumps(node)
            elif argv[1] == "unmountDisk":
                if self.busy:
                    rc, err = 1, b"Unmount failed: dissented by PID 123 (synthetic reader)"
                else:
                    self.infos["disk5s1"].update(Mounted=False, MountPoint="")
                    self.mounts = (FIXTURES / "mount.txt").read_text()
            elif argv[1] == "mount":
                self.infos["disk5s1"].update(Mounted=True, MountPoint=str(self.mounted_at))
                self.mounts += f"/dev/disk5s1 on {self.mounted_at} (apfs, local, journaled)\n"
            else:
                raise AssertionError(argv)
        elif command == "ioreg":
            out = plistlib.dumps(self.service if "-p" in argv else self.registry)
        elif command == "mount":
            out = self.mounts.encode()
        elif command == "sysctl":
            out = self.boot
        elif command == "log":
            rc, out, err = (1, b"", b"unavailable") if self.fail_log else (0, self.events, b"")
        else:
            raise AssertionError(f"Unexpected native command: {argv}")
        return subprocess.CompletedProcess(argv, rc, out, err)


class ParserTests(unittest.TestCase):
    def test_documented_synthetic_shapes(self):
        info = ssd.parse_diskutil_info((FIXTURES / "info-disk5s1.plist").read_bytes())
        self.assertEqual(info["VolumeUUID"], VOLUME)
        listing = ssd.parse_diskutil_list((FIXTURES / "list.plist").read_bytes())
        self.assertIn("disk4", listing)
        self.assertIn("disk5s2", listing)
        registry = ssd.parse_ioreg((FIXTURES / "ioreg.plist").read_bytes())
        self.assertEqual(registry[0]["bsd_name"], "disk4")
        self.assertEqual(registry[0]["counters"]["Bytes (Read)"], 4096)
        mounts = ssd.parse_mount(b"//user@host/share on /Volumes/Team\\040Data (smbfs, nodev)\n")
        self.assertEqual(mounts[0]["mountpoint"], "/Volumes/Team Data")
        self.assertEqual(len(ssd.parse_log((FIXTURES / "events.ndjson").read_bytes())), 2)

    def test_malformed_evidence_refuses(self):
        for parser, payload in ((ssd.parse_diskutil_info, b"not plist"),
                                (ssd.parse_diskutil_list, plistlib.dumps({})),
                                (ssd.parse_mount, b"unparseable line"),
                                (ssd.parse_log, b'{"eventMessage": "mount"}\n')):
            with self.subTest(parser=parser.__name__), self.assertRaises(ssd.Refusal):
                parser(payload)
        mac = FakeMac()
        del mac.registry[0]["Statistics"]["Bytes (Read)"]
        with self.assertRaises(ssd.Refusal):
            ssd.parse_ioreg(plistlib.dumps(mac.registry))

    def test_malformed_config_refuses(self):
        config = json.loads((Path(__file__).parents[1] / "configs/ssd_permanent.json").read_bytes())
        for value in (None, [], "policy"):
            with self.subTest(value=value), self.assertRaises(ssd.Refusal):
                ssd.Hooks({**config, "policy": value})


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mac = FakeMac()
        self.clock = FakeClock()
        self.idle = True
        self.config = json.loads((Path(__file__).parents[1] / "configs/ssd_permanent.json").read_text())
        self.hooks = ssd.Hooks(self.config, runner=self.mac.runner, clock=self.clock,
                               idle_guard=lambda: self.idle)
        self.hooks.enroll("disk4", VOLUME)

    def baseline(self):
        baseline = self.hooks.unmount()
        self.clock.t += self.config["policy"]["q_seconds"]
        return baseline

    def reason(self, baseline, text):
        verdict = self.hooks.check_arm(baseline)
        self.assertFalse(verdict["ok"], verdict)
        self.assertIn(text, " ".join(verdict["reasons"]))

    def test_enrollment_pins_all_identity_fields(self):
        identity = self.config["identity"]
        for key in ("serial", "bus_path", "partition_uuids", "container_uuids", "volume_uuids"):
            self.assertTrue(identity[key], key)
        self.assertEqual(identity["ioreg_entry_id"], 9001)
        self.assertEqual(identity["disk_identifier_at_enrollment"], "disk4")

    def test_arm_and_q_boundary(self):
        baseline = self.hooks.unmount()
        self.reason(baseline, "q_not_elapsed")
        self.clock.t += self.config["policy"]["q_seconds"]
        verdict = self.hooks.check_arm(baseline)
        self.assertTrue(verdict["ok"], verdict)

    def test_missing_snapshot(self):
        self.reason(None, "missing_snapshot")

    def test_wrong_device(self):
        baseline = self.baseline()
        self.mac.registry[0]["Device Characteristics"]["Serial Number"] = "OTHER"
        self.reason(baseline, "identity_mismatch")

    def test_missing_and_extra_physical_device(self):
        baseline = self.baseline()
        self.mac.infos["disk4"]["Internal"] = True
        self.reason(baseline, "external_device_census")
        self.mac.infos["disk4"]["Internal"] = False
        self.mac.listing["AllDisksAndPartitions"].append(
            {"DeviceIdentifier": "disk9", "Content": "GUID_partition_scheme"})
        self.mac.infos["disk9"] = dict(self.mac.infos["disk4"], DeviceIdentifier="disk9")
        self.reason(baseline, "external_device_census")

    def test_device_only_in_flat_disk_census_is_not_ignored(self):
        baseline = self.baseline()
        self.mac.listing["AllDisks"].append("disk9")
        self.mac.infos["disk9"] = dict(self.mac.infos["disk4"], DeviceIdentifier="disk9")
        self.reason(baseline, "external_device_census")

    def test_external_network_disk_image_and_unknown_mounts(self):
        baseline = self.baseline()
        for row in ("//host/share on /Volumes/share (smbfs, nodev)",
                    "host:/export on /Volumes/export (nfs, nodev)",
                    "/dev/disk8s1 on /Volumes/image (hfs, local)",
                    "mystery on /Volumes/mystery (unknownfs, local)"):
            with self.subTest(row=row):
                self.mac.mounts = (FIXTURES / "mount.txt").read_text() + row + "\n"
                self.mac.infos["disk8s1"] = {"DeviceIdentifier": "disk8s1", "Internal": True,
                                             "VirtualOrPhysical": "Virtual", "BusProtocol": "Disk Image"}
                self.reason(baseline, "forbidden_mount")

    def test_enrolled_volume_mounted_in_either_census(self):
        baseline = self.baseline()
        self.mac.infos["disk5s2"].update(Mounted=True, MountPoint="/Volumes/Hidden")
        self.reason(baseline, "enrolled_volume_mounted")
        self.mac.infos["disk5s2"].update(Mounted=False, MountPoint="")
        self.mac.mounts += "/dev/disk5s2 on /Volumes/Hidden (apfs, local)\n"
        self.reason(baseline, "enrolled_volume_mounted")

    def test_counter_change_or_reset(self):
        baseline = self.baseline()
        for value in (4097, 0):
            self.mac.registry[0]["Statistics"]["Bytes (Read)"] = value
            self.reason(baseline, "counter_change")

    def test_reenumeration_entry_id_and_boot_change(self):
        baseline = self.baseline()
        self.mac.registry[0]["IORegistryEntryID"] += 1
        self.reason(baseline, "entry_id_change")
        self.mac.registry[0]["IORegistryEntryID"] -= 1
        self.mac.boot = b"SYNTHETIC-BOOT-B\n"
        self.reason(baseline, "boot_changed")

    def test_busy_unmount_is_bounded_and_never_forced(self):
        self.mac.busy = True
        with self.assertRaisesRegex(ssd.Refusal, "dissented"):
            self.hooks.unmount()
        unmounts = [c for c in self.mac.calls if "unmountDisk" in c]
        self.assertEqual(len(unmounts), 1 + self.config["policy"]["unmount_retries"])
        self.assertTrue(all(c == ["/usr/sbin/diskutil", "unmountDisk",
                                 self.config["identity"]["partition_uuids"][0]] for c in unmounts))
        self.assertNotIn("force", str(self.mac.calls).lower())

    def test_no_new_baseline_until_counters_are_quiescent(self):
        original = self.clock.sleep
        def change(seconds):
            original(seconds)
            self.mac.registry[0]["Statistics"]["Operations (Write)"] += 1
        self.clock.sleep = change
        with self.assertRaisesRegex(ssd.Refusal, "not_quiescent"):
            self.hooks.unmount()

    def test_snapshot_only_reads_ioreg_and_boot_identity(self):
        self.mac.calls.clear()
        snap = self.hooks.snapshot()
        self.assertEqual(snap["entry_id"], 9001)
        self.assertTrue(all(Path(c[0]).name in {"ioreg", "sysctl"} for c in self.mac.calls))

    def test_ioreg_ancestry_fallback(self):
        del self.mac.registry[0]["IORegistryEntryPath"]
        del self.mac.registry[0]["Device Characteristics"]
        # Re-enroll against the synthetic full-tree bus path.
        self.hooks.enroll("disk4", VOLUME)
        self.assertIn("IOService:/", self.config["identity"]["bus_path"])
        self.assertTrue(self.hooks.check_arm(self.baseline())["ok"])

    def test_policy_or_snapshot_corruption_refuses(self):
        baseline = self.baseline()
        self.config["policy"]["q_seconds"] += 1
        self.reason(baseline, "configuration_changed")
        self.config["policy"]["q_seconds"] -= 1
        for key, value in (("quiescent_monotonic_s", float("nan")),
                           ("schema", "unknown"), ("basis", "snapshot")):
            altered = dict(baseline, **{key: value})
            self.assertFalse(self.hooks.check_arm(altered)["ok"])

    def test_post_window_flags_events_counters_and_indeterminate_logs(self):
        arm = self.hooks.check_arm(self.baseline())["snapshot"]
        start = self.clock.time()
        self.clock.t += 10
        end = self.clock.time()
        result = self.hooks.post_window(arm, start, end)
        self.assertFalse(result["SSD_EVENT"], result)
        self.mac.registry[0]["Statistics"]["Bytes (Write)"] += 10
        result = self.hooks.post_window(arm, start, end)
        self.assertTrue(result["SSD_EVENT"])
        self.assertEqual(result["counter_diff"]["Bytes (Write)"], 10)
        self.mac.registry[0]["Statistics"]["Bytes (Write)"] -= 10
        self.mac.events = (FIXTURES / "events.ndjson").read_bytes()
        self.assertTrue(self.hooks.post_window(arm, start, end)["SSD_EVENT"])
        self.mac.events = b"bad json\n"
        self.assertTrue(self.hooks.post_window(arm, start, end)["SSD_EVENT"])
        self.mac.events = b""
        self.mac.fail_log = True
        self.assertTrue(self.hooks.post_window(arm, start, end)["SSD_EVENT"])

    def test_open_window_refuses_before_read_or_mount(self):
        self.idle = False
        self.mac.calls.clear()
        with self.assertRaisesRegex(ssd.Refusal, "window_may_be_alive"):
            self.hooks.offload(self.root / "does-not-exist")
        self.assertEqual(self.mac.calls, [])

    def closed_record(self):
        record = self.root / "record"
        record.mkdir()
        (record / "raw").mkdir()
        (record / "raw/bytes.bin").write_bytes(b"synthetic closed record\x00\xff")
        manifest = {"schema": "joulewise.ssd_closed_record.v1", "state": "closed", "window_id": "test-window",
                    "files": {"raw/bytes.bin": hashlib.sha256((record / "raw/bytes.bin").read_bytes()).hexdigest()}}
        (record / "ssd-closed.json").write_text(json.dumps(manifest))
        self.mac.mounted_at = self.root / "ssd"
        self.mac.mounted_at.mkdir()
        return record

    def test_offload_verified_bytes_and_uuid_mount(self):
        record = self.closed_record()
        # Synthetic directory isn't a real filesystem mount; only the native
        # st_dev mount check is substituted, all copy/digest code runs normally.
        with mock.patch.object(self.hooks, "_open_volume", return_value=os.open(self.mac.mounted_at, os.O_RDONLY)):
            receipt = self.hooks.offload(record)
        target = self.mac.mounted_at / "joulewise-offload/test-window"
        self.assertEqual((record / "raw/bytes.bin").read_bytes(), (target / "raw/bytes.bin").read_bytes())
        self.assertTrue(receipt["verified"])
        self.assertIn(["/usr/sbin/diskutil", "mount", VOLUME], self.mac.calls)

    def test_offload_refuses_missing_closure_digest_drift_and_symlink(self):
        record = self.closed_record()
        manifest = record / "ssd-closed.json"
        original = manifest.read_text()
        manifest.unlink()
        with self.assertRaises(ssd.Refusal):
            self.hooks.offload(record)
        manifest.write_text(original)
        (record / "raw/bytes.bin").write_bytes(b"changed")
        with self.assertRaisesRegex(ssd.Refusal, "digest"):
            self.hooks.offload(record)
        (record / "raw/bytes.bin").unlink()
        (record / "raw/bytes.bin").symlink_to(manifest)
        with self.assertRaises(ssd.Refusal):
            self.hooks.offload(record)
        self.assertFalse(any("mount" in c for c in self.mac.calls))

    def test_empty_mount_point_is_never_written(self):
        record = self.closed_record()
        with self.assertRaisesRegex(ssd.Refusal, "not_a_mountpoint"):
            self.hooks.offload(record)
        self.assertEqual(list(self.mac.mounted_at.iterdir()), [])

    def cli(self, *args):
        state = self.root / "state"
        state.mkdir(exist_ok=True)
        custody = self.root / "custody"
        custody.mkdir(exist_ok=True)
        config = self.root / "config.json"
        config.write_bytes(ssd.encoded(self.config))
        self.state = state
        real_hooks = ssd.Hooks
        factory = lambda config, **kw: real_hooks(config, runner=self.mac.runner, clock=self.clock, **kw)
        output = io.StringIO()
        with mock.patch.object(ssd, "Hooks", side_effect=factory), contextlib.redirect_stdout(output):
            rc = ssd.main(["--config", str(config), "--state-dir", str(state),
                           "--lease", str(self.root / "lease"), "--custody-parent", str(custody), *args])
        return rc, json.loads(output.getvalue())

    def test_cli_enroll_and_missing_snapshot_json(self):
        rc, result = self.cli("enroll", "--disk", "disk4", "--volume-uuid", VOLUME)
        self.assertEqual(rc, 0, result)
        self.assertEqual(json.loads((self.root / "config.json").read_bytes())["identity"], self.config["identity"])
        rc, result = self.cli("check-arm")
        self.assertEqual(rc, 3)
        self.assertIn("missing_snapshot", result["reasons"])
        self.assertFalse((self.state / "arm.json").exists())

    def test_cli_failed_transition_invalidates_baseline_and_arm(self):
        rc, result = self.cli("unmount")
        self.assertEqual(rc, 0, result)
        self.mac.busy = True
        rc, result = self.cli("unmount")
        self.assertEqual(rc, 3, result)
        self.assertFalse((self.state / "unmount.json").exists())
        self.assertFalse((self.state / "arm.json").exists())

    def test_cli_pending_arm_requires_post_before_remount_or_rearm(self):
        self.cli("unmount")
        self.clock.t += self.config["policy"]["q_seconds"]
        rc, result = self.cli("check-arm")
        self.assertEqual(rc, 0, result)
        arm_raw = (self.state / "arm.json").read_bytes()
        for args in (("offload", "--record", str(self.root / "absent")), ("unmount",), ("check-arm",)):
            self.mac.calls.clear()
            rc, result = self.cli(*args)
            self.assertEqual(rc, 3, result)
            self.assertIn("post_window_required", " ".join(result["reasons"]))
            self.assertEqual(self.mac.calls, [])
            self.assertEqual((self.state / "arm.json").read_bytes(), arm_raw)
        rc, result = self.cli("post-window", "--start-epoch", str(self.clock.time()),
                              "--end-epoch", str(self.clock.time()))
        self.assertEqual(rc, 0, result)
        self.assertFalse((self.state / "arm.json").exists())

    def test_cli_event_hold_persists_through_new_unmount(self):
        rc, result = self.cli("post-window", "--start-epoch", str(self.clock.time()),
                              "--end-epoch", str(self.clock.time()))
        self.assertEqual(rc, 3, result)
        self.assertTrue(result["SSD_EVENT"])
        self.assertTrue((self.state / "HOLD.json").exists())
        rc, result = self.cli("unmount")
        self.assertEqual(rc, 0, result)
        self.clock.t += self.config["policy"]["q_seconds"]
        rc, result = self.cli("check-arm")
        self.assertEqual(rc, 3, result)
        self.assertIn("lead_hold", result["reasons"])
        self.assertFalse((self.state / "arm.json").exists())

    def test_cli_busy_lease_never_touches_device_or_receipts(self):
        self.mac.calls.clear()
        with ssd.lease(self.root / "lease"):
            rc, result = self.cli("offload", "--record", str(self.root / "absent"))
        self.assertEqual(rc, 3, result)
        self.assertIn("lease busy", " ".join(result["reasons"]))
        self.assertEqual(self.mac.calls, [])

    def test_cli_census_live_window_never_reads_record_or_mounts(self):
        from joulewise.measurement_liveness import Census
        self.mac.calls.clear()
        with mock.patch("joulewise.measurement_liveness.census", return_value=Census(refusals=["synthetic live owner"])):
            rc, result = self.cli("offload", "--record", str(self.root / "absent"))
        self.assertEqual(rc, 3, result)
        self.assertIn("synthetic live owner", " ".join(result["reasons"]))
        self.assertEqual(self.mac.calls, [])

    def test_offload_digest_failure_keeps_partial_without_publication(self):
        record = self.closed_record()
        real_hash = self.hooks._hash_file
        count = 0
        def wrong_copy(fd, name, deadline):
            nonlocal count
            count += 1
            return "0" * 64 if count == 2 else real_hash(fd, name, deadline)
        with mock.patch.object(self.hooks, "_hash_file", side_effect=wrong_copy), mock.patch.object(
                self.hooks, "_open_volume", return_value=os.open(self.mac.mounted_at, os.O_RDONLY)):
            with self.assertRaisesRegex(ssd.Refusal, "copy digest mismatch"):
                self.hooks.offload(record)
        base = self.mac.mounted_at / "joulewise-offload"
        self.assertFalse((base / "test-window").exists())
        self.assertTrue(any(p.name.startswith(".partial-") for p in base.iterdir()))
        self.assertTrue((record / "raw/bytes.bin").exists())

    def test_synthetic_disk_renumbering_resolves_uuids_but_old_entry_refuses(self):
        baseline = self.baseline()
        def renumber(value):
            if isinstance(value, str):
                return value.replace("disk4", "disk7").replace("disk5", "disk8")
            if isinstance(value, dict):
                return {renumber(k): renumber(v) for k, v in value.items()}
            if isinstance(value, list):
                return [renumber(v) for v in value]
            return value
        self.mac.infos = renumber(self.mac.infos)
        self.mac.listing = renumber(self.mac.listing)
        self.mac.registry = renumber(self.mac.registry)
        self.mac.registry[0]["IORegistryEntryID"] += 1
        self.reason(baseline, "entry_id_change")
        # A new baseline after the between-window replug can resolve disk7/8;
        # a window's stored baseline can never silently inherit the new ID.
        self.mac.busy = True  # Stop before FakeMac's fixed synthetic unmount mutation.
        with self.assertRaisesRegex(ssd.Refusal, "dissented"):
            self.hooks.unmount()
        self.assertIn(["/usr/sbin/diskutil", "unmountDisk", self.config["identity"]["apfs_store_uuid"]], self.mac.calls)

    def test_timeout_and_unknown_census_are_machine_refusals(self):
        baseline = self.baseline()
        self.hooks.runner = mock.Mock(side_effect=subprocess.TimeoutExpired("synthetic diskutil", 1))
        self.reason(baseline, "command_failed")

    def test_post_window_with_live_owner_never_runs_commands(self):
        self.idle = False
        self.mac.calls.clear()
        result = self.hooks.post_window(None, self.clock.time(), self.clock.time())
        self.assertTrue(result["SSD_EVENT"])
        self.assertEqual(self.mac.calls, [])


if __name__ == "__main__":
    unittest.main()
