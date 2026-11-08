#!/usr/bin/env python3
"""B-unmount magistrate hooks. Native execution requires explicit CLI paths.

All command execution is injectable. The caller must serialize these hooks and
measurement launch with the same lease; a census alone is not mutual exclusion.
No collector runs inside a window. See SSD-B-UNMOUNT-OPERATOR.md for integration.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import stat
import subprocess
import sys
import time
import uuid
from xml.parsers.expat import ExpatError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

COUNTERS = ("Bytes (Read)", "Bytes (Write)", "Operations (Read)", "Operations (Write)")
DISK = re.compile(r"disk[0-9]+(?:s[0-9]+)*\Z")
SCHEMA = "joulewise.ssd_permanent.v1"
SNAPSHOT_SCHEMA = "joulewise.ssd_snapshot.v1"
LOG_PREDICATE = ('process == "diskarbitrationd" OR '
                 'subsystem BEGINSWITH "com.apple.DiskArbitration" OR '
                 '(process == "kernel" AND (subsystem CONTAINS[c] "IOStorage" OR '
                 'eventMessage CONTAINS[c] "IOUSB" OR '
                 'eventMessage CONTAINS[c] "disk" OR '
                 'eventMessage CONTAINS[c] "Thunderbolt"))')


class Refusal(ValueError):
    """Missing, ambiguous or unsafe evidence; callers must hold, not improvise."""


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def json_object(raw):
    try:
        result = json.loads(raw, object_pairs_hook=_unique_pairs,
                            parse_constant=lambda s: (_ for _ in ()).throw(Refusal(f"invalid number: {s}")))
    except (ValueError, UnicodeError) as exc:
        raise Refusal(f"invalid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise Refusal("JSON object required")
    return result


def _plist(raw, kind):
    try:
        result = plistlib.loads(raw)
    except (ValueError, TypeError, OverflowError, ExpatError) as exc:
        # plistlib exposes both XML parser and binary-plist exceptions.
        raise Refusal(f"invalid {kind} plist: {exc}") from exc
    if not isinstance(result, kind):
        raise Refusal("unexpected plist root type")
    return result


def _disk(value):
    if not isinstance(value, str) or not DISK.fullmatch(value):
        raise Refusal("invalid device identifier")
    return value


def _uuid(value):
    try:
        if not isinstance(value, str):
            raise ValueError("not a string")
        return str(uuid.UUID(value)).upper()
    except ValueError as exc:
        raise Refusal("missing or invalid UUID") from exc


def _number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def parse_diskutil_info(raw):
    result = _plist(raw, dict)
    _disk(result.get("DeviceIdentifier"))
    if "Mounted" in result and type(result["Mounted"]) is not bool:
        raise Refusal("invalid Mounted flag")
    if "MountPoint" in result and not isinstance(result["MountPoint"], str):
        raise Refusal("invalid MountPoint")
    return result


def parse_diskutil_list(raw):
    """Flatten physical partitions and synthesized APFS volumes, retaining links."""
    data = _plist(raw, dict)
    roots = data.get("AllDisksAndPartitions")
    if not isinstance(roots, list) or not roots:
        raise Refusal("missing disk census")
    nodes = {}

    def visit(node, parent=None):
        if not isinstance(node, dict):
            raise Refusal("invalid disk census node")
        name = _disk(node.get("DeviceIdentifier"))
        if name in nodes:
            raise Refusal("duplicate disk census node")
        nodes[name] = {**node, "_parent": parent}
        for field in ("Partitions", "APFSVolumes"):
            children = node.get(field, [])
            if not isinstance(children, list):
                raise Refusal("invalid disk census children")
            for child in children:
                visit(child, name)
    for root in roots:
        visit(root)
    all_disks = data.get("AllDisks")
    if (not isinstance(all_disks, list) or not all_disks or any(not isinstance(n, str) for n in all_disks)
            or len(set(all_disks)) != len(all_disks)):
        raise Refusal("missing or duplicate AllDisks census")
    for name in all_disks:
        name = _disk(name)
        # APFS snapshots may be listed without a nested APFSVolumes row. Read
        # info for every listed node, including any unexpected whole device.
        nodes.setdefault(name, {"DeviceIdentifier": name, "_parent": None})
    return nodes


def parse_mount(raw):
    """Parse mount's source/on/options form, including octal-escaped spaces."""
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise Refusal("invalid mount encoding") from exc
    rows = []
    for line in lines:
        match = re.fullmatch(r"(.+) on (/.*) \(([^\n]+)\)", line)
        if not match:
            raise Refusal("unparseable mount row")
        unescape = lambda v: re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), v)
        source, mountpoint, opts = match.groups()
        options = [part.strip() for part in opts.split(",")]
        rows.append({"source": unescape(source), "mountpoint": unescape(mountpoint),
                     "fstype": options[0], "options": options[1:]})
    if not rows:
        raise Refusal("empty mount census")
    return rows


def parse_ioreg(raw):
    """Read driver statistics and whole-media BSD association, with ancestry.

    The -r driver view may omit serial/port ancestry. Those fields remain None
    so the caller can require the full IOService archive rather than guess.
    """
    roots = _plist(raw, list)
    result = []

    def prop(nodes, keys):
        for node in reversed(nodes):
            for values in (node, node.get("Device Characteristics", {}),
                           node.get("Protocol Characteristics", {})):
                if isinstance(values, dict):
                    for key in keys:
                        if isinstance(values.get(key), str) and values[key].strip():
                            return values[key].strip()
        return None

    def media(node):
        if not isinstance(node, dict) or not isinstance(node.get("IORegistryEntryChildren", []), list):
            raise Refusal("invalid IORegistry media tree")
        found = []
        if node.get("Whole") is True and "BSD Name" in node:
            found.append(_disk(node["BSD Name"]))
        for child in node.get("IORegistryEntryChildren", []):
            found.extend(media(child))
        return found

    def visit(node, parents):
        if not isinstance(node, dict) or not isinstance(node.get("IORegistryEntryChildren", []), list):
            raise Refusal("invalid IORegistry tree")
        lineage = parents + [node]
        if node.get("IOObjectClass") == "IOBlockStorageDriver":
            entry = node.get("IORegistryEntryID")
            stats = node.get("Statistics")
            if type(entry) is not int or entry <= 0 or not isinstance(stats, dict):
                raise Refusal("missing driver entry ID or statistics")
            if any(type(stats.get(k)) is not int or stats[k] < 0 for k in COUNTERS):
                raise Refusal("missing or invalid I/O counter")
            disks = media(node)
            if len(disks) != 1:
                raise Refusal("ambiguous driver whole-media association")
            path = node.get("IORegistryEntryPath") or node.get("IOPathMatch")
            if not isinstance(path, str) or not path:
                names = [n.get("IORegistryEntryName") for n in lineage]
                path = ("IOService:/" + "/".join(names)) if parents and all(isinstance(n, str) and n for n in names) else None
            result.append({"bsd_name": disks[0], "entry_id": entry,
                           "serial": prop(lineage, ("Serial Number", "USB Serial Number")),
                           "bus_path": path, "counters": {k: stats[k] for k in COUNTERS}})
        for child in node.get("IORegistryEntryChildren", []):
            visit(child, lineage)
    for node in roots:
        visit(node, [])
    if not result:
        raise Refusal("no block storage drivers")
    return result


def parse_log(raw):
    events = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        row = json_object(line)
        if not isinstance(row.get("eventMessage"), str) or not isinstance(row.get("timestamp"), str):
            raise Refusal("unparseable unified-log event (or log gap notice)")
        try:
            stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("timestamp lacks timezone")
        except ValueError as exc:
            raise Refusal("invalid log timestamp") from exc
        events.append(row)
    return events


def validate_config(config):
    if not isinstance(config, dict) or config.get("schema") != SCHEMA or config.get("mode") != "B-unmount":
        raise Refusal("unsupported configuration")
    policy = config.get("policy", {})
    if not isinstance(policy, dict):
        raise Refusal("invalid policy object")
    keys = ("q_seconds", "quiescence_sample_seconds", "command_timeout_seconds",
            "log_timeout_seconds", "copy_timeout_seconds", "retry_delay_seconds")
    if any(not _number(policy.get(k)) or policy[k] <= 0 for k in keys):
        raise Refusal("invalid policy threshold")
    if type(policy.get("unmount_retries")) is not int or policy["unmount_retries"] < 0:
        raise Refusal("invalid retry policy")
    _relative(config.get("offload_directory"))
    # Ensure configuration digests cannot contain NaN or unserializable values.
    encoded(config)


def _relative(value):
    if (not isinstance(value, str) or not value or "\\" in value or "\x00" in value
            or any(part in ("", ".", "..") for part in value.split("/"))
            or value.startswith("/")):
        raise Refusal("unsafe relative path")
    return value.split("/")


@contextmanager
def directory_fd(path):
    """Open every path component without following symlinks."""
    path = Path(os.path.abspath(path))
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd
    finally:
        os.close(fd)


@contextmanager
def descendant_fd(root_fd, parts, *, create=False):
    fd = os.dup(root_fd)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd
    finally:
        os.close(fd)


def read_at(fd, name):
    try:
        with os.fdopen(os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd), "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise Refusal("not a regular file")
            return handle.read()
    except OSError as exc:
        raise Refusal(f"record unavailable: {name}: {exc}") from exc


class Hooks:
    def __init__(self, config, *, runner=None, clock=time, idle_guard=None):
        validate_config(config)
        self.config, self.runner, self.clock = config, runner or subprocess.run, clock
        self.idle_guard = idle_guard

    @property
    def policy(self):
        return self.config["policy"]

    def command(self, *argv, timeout=None):
        try:
            result = self.runner(list(argv), capture_output=True, check=False,
                                 timeout=timeout or self.policy["command_timeout_seconds"],
                                 env={**os.environ, "LC_ALL": "C", "LANG": "C", "TZ": "UTC"})
        except (OSError, subprocess.SubprocessError) as exc:
            raise Refusal(f"command_failed: {argv[0]}: {exc}") from exc
        if result.returncode != 0 or result.stderr.strip():
            err = result.stderr.decode(errors="replace") if isinstance(result.stderr, bytes) else result.stderr
            raise Refusal(f"command_failed: {' '.join(argv)}: {err.strip()}")
        return result.stdout

    def idle(self):
        if self.idle_guard is None or self.idle_guard() is not True:
            raise Refusal("window_may_be_alive: idle census unavailable or refused")

    def info(self, identifier):
        return parse_diskutil_info(self.command("/usr/sbin/diskutil", "info", "-plist", identifier))

    def registry(self):
        rows = parse_ioreg(self.command("/usr/sbin/ioreg", "-r", "-c", "IOBlockStorageDriver", "-l", "-a"))
        if any(not row["serial"] or not row["bus_path"] for row in rows):
            # Class-rooted archives omit ancestors on some macOS builds. Keep
            # matching by entry ID and BSD association; never infer a serial.
            full = parse_ioreg(self.command("/usr/sbin/ioreg", "-p", "IOService", "-l", "-a"))
            by_id = {row["entry_id"]: row for row in full}
            for index, row in enumerate(rows):
                if not row["serial"] or not row["bus_path"]:
                    other = by_id.get(row["entry_id"])
                    if not other or other["bsd_name"] != row["bsd_name"]:
                        raise Refusal("IORegistry changed during census")
                    rows[index] = other
        return rows

    def inventory(self):
        listing = parse_diskutil_list(self.command("/usr/sbin/diskutil", "list", "-plist"))
        nodes = {}
        for name, row in listing.items():
            info = self.info(name)
            if info["DeviceIdentifier"] != name or any(type(info.get(k)) is not bool for k in ("Whole", "Internal")):
                raise Refusal("indeterminate disk info census")
            nodes[name] = {**row, **info}
        external = []
        for name, row in nodes.items():
            if row.get("Whole") is True and row.get("Internal") is False:
                kind = row.get("VirtualOrPhysical")
                if kind == "Physical":
                    external.append(name)
                elif kind != "Virtual":
                    raise Refusal("indeterminate physical device census")
            if row.get("Whole") is True and type(row.get("Internal")) is not bool:
                raise Refusal("indeterminate external device census")
        return nodes, external, parse_mount(self.command("/sbin/mount"))

    def identity(self, nodes, disk, driver, volume_uuid):
        physical = nodes[disk]
        partitions = {n: r for n, r in nodes.items()
                      if r.get("_parent") == disk or r.get("ParentWholeDisk") == disk}
        stores = {n: r for n, r in partitions.items() if r.get("Content") == "Apple_APFS"}
        if len(stores) != 1:
            raise Refusal("unsupported topology: require one APFS physical store")
        store, store_info = next(iter(stores.items()))
        containers = {}
        for name, row in nodes.items():
            refs = row.get("APFSPhysicalStores", [])
            if not isinstance(refs, list) or any(not isinstance(r, dict) for r in refs):
                raise Refusal("invalid APFS store links")
            if (name == store_info.get("APFSContainerReference")
                    or any(r.get("DeviceIdentifier") == store for r in refs)):
                if refs and {r.get("DeviceIdentifier") for r in refs} != {store}:
                    raise Refusal("unsupported multi-store APFS container")
                containers[name] = row
        if len(containers) != 1:
            raise Refusal("missing or ambiguous APFS container")
        volumes = {n: r for n, r in nodes.items() if n not in containers and
                   (r.get("_parent") in containers or r.get("ParentWholeDisk") in containers
                    or (n != store and r.get("APFSContainerReference") in containers))}
        if not volumes or not driver["serial"] or not driver["bus_path"]:
            raise Refusal("incomplete enrolled identity")
        if any(type(row.get("Mounted")) is not bool for row in volumes.values()):
            raise Refusal("missing APFS volume mount state")
        volume_uuids = sorted(_uuid(r.get("APFSVolumeUUID") or r.get("VolumeUUID")) for r in volumes.values())
        if len(volume_uuids) != len(set(volume_uuids)) or _uuid(volume_uuid) not in volume_uuids:
            raise Refusal("offload volume is not uniquely on enrolled device")
        identity = {"disk_identifier_at_enrollment": disk,
                    "disk_uuid": _uuid(physical["DiskUUID"]) if physical.get("DiskUUID") else None,
                    "partition_uuids": sorted(_uuid(r.get("DiskUUID") or r.get("PartitionUUID")) for r in partitions.values()),
                    "apfs_store_uuid": _uuid(store_info.get("DiskUUID") or store_info.get("PartitionUUID")),
                    "container_uuids": sorted(_uuid(r.get("APFSContainerUUID")) for r in containers.values()),
                    "volume_uuids": volume_uuids, "offload_volume_uuid": _uuid(volume_uuid),
                    "serial": driver["serial"], "bus_path": driver["bus_path"],
                    "ioreg_entry_id": driver["entry_id"]}
        return identity, set(partitions) | set(containers) | set(volumes) | {disk}

    def enroll(self, disk, volume_uuid):
        self.idle()
        _disk(disk)
        nodes, external, _ = self.inventory()
        if external != [disk]:
            raise Refusal("external_device_census: enroll exactly one external physical device")
        registry = self.registry()
        if any(row["bsd_name"] not in nodes for row in registry):
            raise Refusal("external_device_census: IORegistry/disk census disagreement")
        drivers = [r for r in registry if r["bsd_name"] == disk]
        if len(drivers) != 1:
            raise Refusal("ambiguous enrolled IORegistry driver")
        identity, _ = self.identity(nodes, disk, drivers[0], volume_uuid)
        self.config["identity"] = identity
        return identity

    def enrolled(self):
        identity = self.config.get("identity")
        if not isinstance(identity, dict):
            raise Refusal("device_not_enrolled")
        return identity

    def census(self, *, allow_enrolled_mounts=False):
        expected = self.enrolled()
        nodes, external, mounts = self.inventory()
        if len(external) != 1:
            raise Refusal("external_device_census: expected exactly one device")
        disk = external[0]
        registry = self.registry()
        if any(row["bsd_name"] not in nodes for row in registry):
            raise Refusal("external_device_census: IORegistry/disk census disagreement")
        drivers = [r for r in registry if r["bsd_name"] == disk]
        if len(drivers) != 1:
            raise Refusal("identity_mismatch: ambiguous driver")
        identity, members = self.identity(nodes, disk, drivers[0], expected["offload_volume_uuid"])
        for key, value in expected.items():
            if key not in ("disk_identifier_at_enrollment", "ioreg_entry_id") and identity.get(key) != value:
                raise Refusal(f"identity_mismatch: {key}")
        if not allow_enrolled_mounts and any(nodes[n].get("Mounted") is True or nodes[n].get("MountPoint")
                                             for n in members):
            raise Refusal("enrolled_volume_mounted")
        for mount in mounts:
            source = mount["source"]
            if source.startswith("/dev/"):
                name = _disk(source.removeprefix("/dev/"))
                if name in members:
                    if not allow_enrolled_mounts:
                        raise Refusal("enrolled_volume_mounted")
                    continue
                if mount["fstype"] not in ("apfs", "hfs") or not self._internal_physical_backing(name, nodes):
                    raise Refusal(f"forbidden_mount: {source}")
            elif not ((mount["fstype"] == "devfs" and source == "devfs") or
                      (mount["fstype"] == "autofs" and source.startswith("map "))):
                raise Refusal(f"forbidden_mount: {source}")
        return drivers[0]

    def _internal_physical_backing(self, name, nodes, seen=None):
        """An Internal flag on a virtual APFS volume alone cannot clear an image."""
        seen = set() if seen is None else set(seen)
        if name in seen:
            return False
        seen.add(name)
        row = nodes.get(name) or self.info(name)
        if row.get("Internal") is not True or "image" in str(row.get("BusProtocol", "")).lower():
            return False
        if row.get("Whole") is True and row.get("VirtualOrPhysical") == "Physical":
            return True
        stores = row.get("APFSPhysicalStores")
        if stores:
            if not isinstance(stores, list):
                return False
            names = [_disk(s.get("DeviceIdentifier") if isinstance(s, dict) else s) for s in stores]
            return all(self._internal_physical_backing(n, nodes, seen) for n in names)
        parent = row.get("ParentWholeDisk") or row.get("_parent") or row.get("APFSContainerReference")
        return bool(parent and self._internal_physical_backing(_disk(parent), nodes, seen))

    def snapshot(self):
        expected = self.enrolled()
        rows = [r for r in self.registry() if r["serial"] == expected["serial"]
                and r["bus_path"] == expected["bus_path"]]
        if len(rows) != 1:
            raise Refusal("identity_mismatch: enrolled IORegistry entry missing or duplicated")
        boot = self.command("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid").decode().strip()
        if not boot:
            raise Refusal("boot identity missing")
        return {"schema": SNAPSHOT_SCHEMA, "basis": "snapshot", "config_sha256": sha(encoded(self.config)),
                **rows[0], "boot_id": boot, "monotonic_s": self.clock.monotonic(), "epoch_s": self.clock.time()}

    def unmount(self):
        self.idle()
        self.census(allow_enrolled_mounts=True)
        for attempt in range(self.policy["unmount_retries"] + 1):
            self.idle()
            try:
                self.command("/usr/sbin/diskutil", "unmountDisk", self.enrolled()["apfs_store_uuid"])
                break
            except Refusal:
                if attempt == self.policy["unmount_retries"]:
                    raise
                self.clock.sleep(self.policy["retry_delay_seconds"])
        self.census()
        first = self.snapshot()
        self.clock.sleep(self.policy["quiescence_sample_seconds"])
        self.idle()
        self.census()
        second = self.snapshot()
        if any(first[key] != second[key] for key in ("boot_id", "entry_id", "counters")):
            raise Refusal("not_quiescent: no baseline recorded; wait and retry unmount")
        return {**second, "basis": "verified_unmount", "quiescent_monotonic_s": second["monotonic_s"],
                "quiescence_first_sample": first}

    def _validate_snapshot(self, snapshot, basis):
        if not isinstance(snapshot, dict):
            raise Refusal("missing_snapshot")
        if snapshot.get("schema") != SNAPSHOT_SCHEMA or snapshot.get("basis") != basis:
            raise Refusal("invalid_snapshot")
        if snapshot.get("config_sha256") != sha(encoded(self.config)):
            raise Refusal("configuration_changed")
        if (type(snapshot.get("entry_id")) is not int or not snapshot.get("boot_id")
                or not _number(snapshot.get("monotonic_s")) or not _number(snapshot.get("epoch_s"))
                or not isinstance(snapshot.get("counters"), dict)
                or set(snapshot["counters"]) != set(COUNTERS)
                or any(type(v) is not int or v < 0 for v in snapshot["counters"].values())):
            raise Refusal("invalid_snapshot")

    @staticmethod
    def changes(before, after):
        reasons = []
        for field, code in (("boot_id", "boot_changed"), ("entry_id", "entry_id_change"),
                            ("counters", "counter_change"), ("serial", "identity_mismatch"),
                            ("bus_path", "identity_mismatch")):
            if before.get(field) != after.get(field):
                reasons.append(code)
        return reasons

    def check_arm(self, baseline):
        try:
            self.idle()
            self._validate_snapshot(baseline, "verified_unmount")
            quiescent = baseline.get("quiescent_monotonic_s")
            if not _number(quiescent) or quiescent != baseline["monotonic_s"]:
                raise Refusal("invalid_quiescence_time")
            first = baseline.get("quiescence_first_sample")
            self._validate_snapshot(first, "snapshot")
            if (self.changes(first, baseline) or first["monotonic_s"] > quiescent
                    or quiescent - first["monotonic_s"] < self.policy["quiescence_sample_seconds"]):
                raise Refusal("invalid_quiescence_evidence")
            self.census()
            current = self.snapshot()
            reasons = self.changes(baseline, current)
            elapsed = current["monotonic_s"] - quiescent
            if elapsed < self.policy["q_seconds"]:
                reasons.append("q_not_elapsed")
            return {"schema": "joulewise.arm_ssd.v1", "ok": not reasons, "reasons": reasons,
                    "elapsed_quiescent_s": elapsed, "snapshot": {**current, "basis": "arm"}}
        except (Refusal, OSError, KeyError, TypeError, ValueError) as exc:
            return {"schema": "joulewise.arm_ssd.v1", "ok": False, "reasons": [str(exc)]}

    def post_window(self, arm, start, end):
        reasons, diff, events = [], None, []
        try:
            self.idle()
        except (Refusal, OSError, ValueError) as exc:
            return {"schema": "joulewise.ssd_post_window.v1", "SSD_EVENT": True,
                    "hold_next_arm": True, "reasons": [str(exc)], "counter_diff": None,
                    "log_sha256": None, "events": [], "start_epoch_s": start, "end_epoch_s": end}
        try:
            self._validate_snapshot(arm, "arm")
            if not _number(start) or not _number(end) or not arm["epoch_s"] <= start <= end <= self.clock.time():
                raise Refusal("invalid_window_span")
            self.census()
            current = self.snapshot()
            reasons.extend(self.changes(arm, current))
            diff = {key: current["counters"][key] - arm["counters"][key] for key in COUNTERS}
        except (Refusal, OSError, KeyError, TypeError, ValueError) as exc:
            reasons.append(str(exc))
        log_sha = None
        try:
            if not _number(start) or not _number(end) or start > end:
                raise Refusal("invalid_window_span")
            # Whole-second enclosing bounds include the native log boundaries.
            fmt = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d %H:%M:%S+0000")
            raw = self.command("/usr/bin/log", "show", "--style", "ndjson", "--info", "--debug",
                               "--start", fmt(math.floor(start)), "--end", fmt(math.ceil(end)),
                               "--predicate", LOG_PREDICATE, timeout=self.policy["log_timeout_seconds"])
            log_sha = sha(raw)
            events = parse_log(raw)
            if events:
                reasons.append("disk_arbitration_or_storage_log_event")
        except (Refusal, OSError, ValueError, OverflowError) as exc:
            reasons.append(f"log_indeterminate: {exc}")
        return {"schema": "joulewise.ssd_post_window.v1", "SSD_EVENT": bool(reasons),
                "hold_next_arm": bool(reasons), "reasons": reasons, "counter_diff": diff,
                "log_sha256": log_sha, "events": events, "start_epoch_s": start, "end_epoch_s": end}

    def _deadline(self, deadline):
        if self.clock.monotonic() > deadline:
            raise Refusal("copy_timeout")

    def _files(self, fd, deadline, prefix=""):
        files = set()
        for name in os.listdir(fd):
            self._deadline(deadline)
            st = os.stat(name, dir_fd=fd, follow_symlinks=False)
            path = prefix + name
            _relative(path)
            if stat.S_ISDIR(st.st_mode):
                with descendant_fd(fd, [name]) as child:
                    files.update(self._files(child, deadline, path + "/"))
            elif stat.S_ISREG(st.st_mode):
                if st.st_nlink != 1:
                    raise Refusal("hardlinked record file")
                files.add(path)
            else:
                raise Refusal("symlink or special record file")
        return files

    def _hash_file(self, fd, name, deadline):
        digest = hashlib.sha256()
        with os.fdopen(os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd), "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise Refusal("not a regular file")
            while chunk := handle.read(1024 * 1024):
                self._deadline(deadline)
                digest.update(chunk)
        return digest.hexdigest()

    def _verify_record(self, fd, manifest, manifest_raw, deadline):
        if (manifest.get("schema") != "joulewise.ssd_closed_record.v1"
                or manifest.get("state") != "closed"
                or not isinstance(manifest.get("window_id"), str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", manifest["window_id"])
                or not isinstance(manifest.get("files"), dict) or not manifest["files"]):
            raise Refusal("missing closed-record manifest")
        if self._files(fd, deadline) != set(manifest["files"]) | {"ssd-closed.json"}:
            raise Refusal("closed-record file inventory mismatch")
        for path, expected in manifest["files"].items():
            parts = _relative(path)
            if path == "ssd-closed.json" or not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
                raise Refusal("invalid file digest")
            with descendant_fd(fd, parts[:-1]) as parent:
                if self._hash_file(parent, parts[-1], deadline) != expected:
                    raise Refusal(f"source digest mismatch: {path}")
        if read_at(fd, "ssd-closed.json") != manifest_raw:
            raise Refusal("closed-record manifest changed")

    def _mounted_volume(self):
        expected = self.enrolled()["offload_volume_uuid"]
        row = self.info(expected)
        if _uuid(row.get("APFSVolumeUUID") or row.get("VolumeUUID")) != expected or row.get("Mounted") is not True:
            raise Refusal("mount UUID verification failed")
        mountpoint = row.get("MountPoint")
        if not isinstance(mountpoint, str) or not mountpoint.startswith("/") or mountpoint == "/":
            raise Refusal("invalid mountpoint")
        mounts = parse_mount(self.command("/sbin/mount"))
        matches = [m for m in mounts if m["mountpoint"] == mountpoint]
        if len(matches) != 1 or matches[0]["source"] != "/dev/" + row["DeviceIdentifier"] or matches[0]["fstype"] != "apfs":
            raise Refusal("mount table UUID association failed")
        return Path(mountpoint)

    def _open_volume(self, mountpoint):
        with directory_fd(mountpoint) as fd:
            if os.fstat(fd).st_dev == mountpoint.parent.stat().st_dev:
                raise Refusal("not_a_mountpoint: refusing empty mountpoint")
            if self._mounted_volume() != mountpoint or os.fstat(fd).st_dev != mountpoint.stat().st_dev:
                raise Refusal("mount changed while opening volume")
            return os.dup(fd)

    def offload(self, record):
        self.idle()  # Before touching even the source; never read an open window.
        deadline = self.clock.monotonic() + self.policy["copy_timeout_seconds"]
        with directory_fd(record) as source:
            raw = read_at(source, "ssd-closed.json")
            manifest = json_object(raw)
            self._verify_record(source, manifest, raw, deadline)
            self.census(allow_enrolled_mounts=True)
            self.idle()
            self.command("/usr/sbin/diskutil", "mount", self.enrolled()["offload_volume_uuid"])
            self.census(allow_enrolled_mounts=True)
            mountpoint = self._mounted_volume()
            source_path = Path(os.path.abspath(record))
            if source_path == mountpoint or mountpoint in source_path.parents:
                raise Refusal("source record must be on the local disk, outside the offload volume")
            volume_fd = self._open_volume(mountpoint)
            try:
                # Every write is relative to a pinned filesystem descriptor. A
                # disappearing mount cannot redirect a write into an empty dir.
                with descendant_fd(volume_fd, _relative(self.config["offload_directory"]), create=True) as base:
                    target = manifest["window_id"]
                    try:
                        os.stat(target, dir_fd=base, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        raise Refusal("offload destination already exists; preserve it")
                    stage = ".partial-" + uuid.uuid4().hex
                    os.mkdir(stage, dir_fd=base)
                    with descendant_fd(base, [stage]) as dest:
                        for path, expected in {**manifest["files"], "ssd-closed.json": sha(raw)}.items():
                            self.idle()
                            self._deadline(deadline)
                            parts = _relative(path)
                            with descendant_fd(source, parts[:-1]) as src_parent, descendant_fd(dest, parts[:-1], create=True) as dst_parent:
                                src_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=src_parent)
                                with os.fdopen(src_fd, "rb") as src:
                                    if not stat.S_ISREG(os.fstat(src.fileno()).st_mode):
                                        raise Refusal("source changed to special file")
                                    dst_fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dst_parent)
                                    with os.fdopen(dst_fd, "wb") as dst:
                                        digest = hashlib.sha256()
                                        while chunk := src.read(1024 * 1024):
                                            self._deadline(deadline)
                                            digest.update(chunk)
                                            dst.write(chunk)
                                        dst.flush()
                                        os.fsync(dst.fileno())
                                    if digest.hexdigest() != expected or self._hash_file(dst_parent, parts[-1], deadline) != expected:
                                        raise Refusal(f"copy digest mismatch: {path}")
                                os.fsync(dst_parent)
                        self._verify_record(source, manifest, raw, deadline)
                        os.fsync(dest)
                    self.idle()
                    os.rename(stage, target, src_dir_fd=base, dst_dir_fd=base)
                    os.fsync(base)
            finally:
                os.close(volume_fd)
        return {"schema": "joulewise.ssd_offload.v1", "verified": True, "window_id": target,
                "manifest_sha256": sha(raw), "files": manifest["files"],
                "destination": str(mountpoint / self.config["offload_directory"] / target)}


def atomic_json(path, value):
    """Internal receipts only, never measurement records; caller holds lease."""
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        with directory_fd(path.parent) as fd:
            os.fsync(fd)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def copy_alarm(seconds):
    """CLI wall budget includes read/write/fsync, not just chunk boundaries.

    The magistrate must also supervise the process: no user-space timeout can
    guarantee interruption of a kernel I/O call stuck in an uninterruptible wait.
    """
    if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
        raise Refusal("existing alarm: caller must supply a separate process budget")
    previous = signal.getsignal(signal.SIGALRM)

    def expired(signum, frame):
        raise Refusal("copy_timeout")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


@contextmanager
def lease(path):
    with open(path, "a+b") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Refusal("window_may_be_alive: magistrate lease busy") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--state-dir", required=True, type=Path, help="existing local receipt directory, off SSD")
    parser.add_argument("--lease", required=True, type=Path, help="shared with launch/prepare/finalize")
    parser.add_argument("--custody-parent", required=True, action="append", type=Path,
                        help="explicit liveness census root; repeat for all roots, no implicit defaults")
    sub = parser.add_subparsers(dest="action", required=True)
    enroll = sub.add_parser("enroll")
    enroll.add_argument("--disk", required=True)
    enroll.add_argument("--volume-uuid", required=True)
    offload = sub.add_parser("offload")
    offload.add_argument("--record", required=True, type=Path)
    sub.add_parser("unmount")
    sub.add_parser("snapshot")
    sub.add_parser("check-arm")
    post = sub.add_parser("post-window")
    post.add_argument("--start-epoch", required=True, type=float)
    post.add_argument("--end-epoch", required=True, type=float)
    args = parser.parse_args(argv)
    acquired = False
    try:
        from joulewise.measurement_liveness import census

        def idle_guard():
            # Do not use the module's default custody parent or environment.
            if any(not p.is_dir() or p.is_symlink() for p in args.custody_parent):
                raise Refusal("idle census root missing or symlinked")
            result = census(parents=args.custody_parent)
            if not result.clear:
                raise Refusal("window_may_be_alive: " + "; ".join(result.refusals))
            return True

        with lease(args.lease):
            acquired = True
            config = json_object(args.config.read_bytes())
            hooks = Hooks(config, idle_guard=idle_guard)
            baseline_path, arm_path = args.state_dir / "unmount.json", args.state_dir / "arm.json"
            if not args.state_dir.is_dir() or args.state_dir.is_symlink():
                raise Refusal("state-dir must already exist locally")
            if args.action in ("enroll", "offload", "unmount", "check-arm") and arm_path.exists():
                raise Refusal("post_window_required: preserve pending arm receipt before any new transition")
            if args.action in ("enroll", "offload", "unmount"):
                hooks.idle()
                # A failed transition cannot leave an old usable arm/baseline.
                baseline_path.unlink(missing_ok=True)
                arm_path.unlink(missing_ok=True)
            if args.action == "enroll":
                result = hooks.enroll(args.disk, args.volume_uuid)
                atomic_json(args.config, config)
            elif args.action == "offload":
                with copy_alarm(hooks.policy["copy_timeout_seconds"]):
                    result = hooks.offload(args.record)
                atomic_json(args.state_dir / "offload.json", result)
            elif args.action == "unmount":
                result = hooks.unmount()
                atomic_json(baseline_path, result)
            elif args.action == "snapshot":
                result = hooks.snapshot()
            elif args.action == "check-arm":
                if (args.state_dir / "HOLD.json").exists():
                    result = {"schema": "joulewise.arm_ssd.v1", "ok": False, "reasons": ["lead_hold"]}
                else:
                    baseline = json_object(baseline_path.read_bytes()) if baseline_path.exists() else None
                    result = hooks.check_arm(baseline)
                    if result["ok"]:
                        atomic_json(arm_path, result["snapshot"])
            else:
                arm = json_object(arm_path.read_bytes()) if arm_path.exists() else None
                result = hooks.post_window(arm, args.start_epoch, args.end_epoch)
                atomic_json(args.state_dir / "post-window.json", result)
                if result["SSD_EVENT"]:
                    atomic_json(args.state_dir / "HOLD.json", result)
                    baseline_path.unlink(missing_ok=True)
                arm_path.unlink(missing_ok=True)
            print(encoded(result).decode(), end="")
            return 3 if result.get("ok") is False or result.get("SSD_EVENT") else 0
    except (Refusal, OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        result = {"ok": False, "reasons": [str(exc)]}
        if args.action == "post-window":
            result.update(SSD_EVENT=True, hold_next_arm=True)
            # Preserve a hold even for malformed receipts/read failures.
            if acquired:
                try:
                    with lease(args.lease):
                        atomic_json(args.state_dir / "HOLD.json", result)
                except (OSError, Refusal):
                    pass
        print(encoded(result).decode(), end="")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
