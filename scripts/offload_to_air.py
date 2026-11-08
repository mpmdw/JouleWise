#!/usr/bin/env python3
"""Push one closed record between windows; also provide the restricted Air receiver.

No discovery of custody roots, no measurement/analysis imports, no network at
import time. See docs/ops/AIR-OFFLOAD.md for the magistrate lease and SSH setup.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HEX = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
MANIFEST_SCHEMA = "joulewise.closed_record.v1"
RECEIPT_SCHEMA = "joulewise.air_receipt.v1"
GATE_SCHEMA = "joulewise.air_offload_gate.v1"


class Refusal(ValueError):
    """Fail closed, retaining local evidence."""


def require(condition, message):
    if not condition:
        raise Refusal(message)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def decode(raw):
    value = json.loads(raw, object_pairs_hook=_pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite JSON")))
    require(isinstance(value, dict), "JSON object required")
    return value


def relative(name):
    require(isinstance(name, str) and name and "\x00" not in name and "\\" not in name,
            "invalid relative path")
    parts = PurePosixPath(name).parts
    require(not name.startswith("/") and all(p not in {".", "..", ".git", "restricted"} for p in parts)
            and "/".join(parts) == name, "noncanonical or sealed relative path")
    return Path(*parts)


def plain_path(path):
    """Check lexical ancestors before opening anything; never resolve a symlink."""
    path = Path(os.path.abspath(path))
    for item in reversed((path, *path.parents)):
        try:
            require(not stat.S_ISLNK(item.lstat().st_mode), f"symlink path: {item}")
        except FileNotFoundError:
            continue
    return path


def read_json(path):
    return decode(read_bytes(path))


@contextmanager
def directory_fd(path):
    """Pin each component so a replacement symlink cannot redirect a read."""
    path = Path(os.path.abspath(path))
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def regular_fd(path):
    path = plain_path(path)
    with directory_fd(path.parent) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise Refusal("nonregular or hard-linked file")
    return fd


def read_bytes(path):
    with os.fdopen(regular_fd(path), "rb") as handle:
        return handle.read()


def fsync_dir(path):
    with directory_fd(path) as fd:
        os.fsync(fd)


def device_id(path):
    return str(plain_path(path).stat().st_dev)


def save(path, value):
    path = plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + secrets.token_hex(8))
    try:
        with temporary.open("xb") as handle:
            handle.write(encode(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        fsync_dir(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def lock(path):
    path = plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Refusal("loop/record lock busy") from error
        yield
    finally:
        os.close(fd)


@contextmanager
def budget_alarm(seconds):
    """Bound blocking Python I/O too; the caller must still await full exit."""
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0), "existing process timer")
    previous = signal.getsignal(signal.SIGALRM)
    previous_term = signal.getsignal(signal.SIGTERM)
    def expired(signum, frame):
        raise Refusal("cooldown process budget exceeded")
    signal.signal(signal.SIGALRM, expired)
    def interrupted(signum, frame):
        raise Refusal("offload interrupted")
    signal.signal(signal.SIGTERM, interrupted)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        signal.signal(signal.SIGTERM, previous_term)


def files(root, check=lambda: None):
    """Only the explicitly supplied tree; reject links, devices and hard links."""
    root = plain_path(root)
    require(root.is_dir(), "record directory absent")
    found = {}

    def walk(fd, prefix=""):
        check()
        with os.scandir(fd) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                check()
                name = prefix + entry.name
                relative(name)
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                    try:
                        walk(child, name + "/")
                    finally:
                        os.close(child)
                else:
                    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                            f"nonregular, symlink or hard-linked record member: {name}")
                    found[name] = info.st_size
    with directory_fd(root) as fd:
        walk(fd)
    return found


def file_sha(path, check=lambda: None, durable=False):
    digest = hashlib.sha256()
    fd = regular_fd(path)
    with os.fdopen(fd, "rb") as handle:
        before = os.fstat(handle.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "nonregular file")
        while True:
            check()
            chunk = handle.read(4 * 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(handle.fileno())
        require((before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_ino, after.st_size, after.st_mtime_ns), "record changed during hash")
        if durable:
            os.fsync(handle.fileno())
    return digest.hexdigest()


def remove_empty_record(root, check):
    def empty(fd):
        with os.scandir(fd) as entries:
            for entry in entries:
                check()
                require(entry.is_dir(follow_symlinks=False), "new or symlinked member during deletion")
                child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    empty(child)
                finally:
                    os.close(child)
                os.rmdir(entry.name, dir_fd=fd)
    with directory_fd(root.parent) as parent, directory_fd(root) as fd:
        empty(fd)
        check()
        current, pinned = os.stat(root.name, dir_fd=parent, follow_symlinks=False), os.fstat(fd)
        require((current.st_dev, current.st_ino) == (pinned.st_dev, pinned.st_ino), "record root replaced")
        os.rmdir(root.name, dir_fd=parent)


def manifest_entries(root, name, expected):
    require(HEX.fullmatch(expected or ""), "manifest SHA-256 required")
    relative(name)
    raw = read_bytes(root / name)
    require(sha(raw) == expected, "manifest digest mismatch")
    value = decode(raw)
    rows = {}
    if value.get("schema") == "joulewise.ssd_closed_record.v1":
        require(name == "ssd-closed.json" and value.get("state") == "closed"
                and isinstance(value.get("window_id"), str) and NAME.fullmatch(value["window_id"])
                and isinstance(value.get("files"), dict) and value["files"], "invalid SSD closed record")
        for key, digest in value["files"].items():
            relative(key)
            require(isinstance(digest, str), "invalid SSD manifest digest")
            with os.fdopen(regular_fd(root / key), "rb") as handle:
                rows[key] = {"sha256": digest, "size": os.fstat(handle.fileno()).st_size}
    elif value.get("schema") == MANIFEST_SCHEMA:
        require(value.get("closed") is True and isinstance(value.get("files"), dict),
                "manifest is not closed")
        rows = value["files"].copy()
    elif value.get("schema") == "joulewise.harvest_window.v1":
        # Existing archive manifest: only relative inventory names, never the
        # absolute custody_root or any other path reference in harvest.json.
        inventory = value.get("inventory")
        require(isinstance(inventory, dict) and inventory, "harvest lacks inventory")
        for prefix, members in inventory.items():
            relative(prefix)
            require(isinstance(members, dict), "malformed harvest inventory")
            for member, row in members.items():
                require(isinstance(row, dict) and type(row.get("mode")) is int, "bad inventory row")
                mode = row["mode"]
                require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), "inventory contains links/devices")
                if member != ".":
                    relative(member)
                if stat.S_ISREG(mode):
                    key = f"{prefix}/{member}"
                    require(key not in rows, "overlapping harvest inventory")
                    rows[key] = {"sha256": row.get("sha256"), "size": row.get("size")}
        # Revision 6 adds this file after the source inventory was taken.
        extra = value.get("r9_window")
        if extra is not None:
            require(isinstance(extra, dict), "bad R9 reference")
            key = "custody-root/" + str(extra.get("path", ""))
            relative(key)
            existing = rows.get(key)
            require(existing is None or existing["sha256"] == extra.get("sha256"), "R9 collision")
            with os.fdopen(regular_fd(root / key), "rb") as handle:
                rows[key] = {"sha256": extra.get("sha256"), "size": os.fstat(handle.fileno()).st_size}
    else:
        raise Refusal("unsupported closed-record manifest schema")
    require(name not in rows, "manifest must not digest itself")
    for key, row in rows.items():
        relative(key)
        require(isinstance(row, dict) and HEX.fullmatch(str(row.get("sha256", "")))
                and type(row.get("size")) is int and row["size"] >= 0, "invalid manifest member")
    rows[name] = {"sha256": expected, "size": len(raw)}
    return rows


def inspect_record(root, name, expected, *, check=lambda: None, durable=False):
    root = plain_path(root)
    sizes = files(root, check)
    rows = manifest_entries(root, name, expected)
    require(set(sizes) == set(rows),
            "record file inventory mismatch (missing or extra file)")
    for key, size in sizes.items():
        require(size == rows[key]["size"] and
                file_sha(root / key, check, durable) == rows[key]["sha256"], f"file digest mismatch: {key}")
    if durable:
        # Include directories so a power failure cannot turn a receipt into
        # acknowledgement of directory entries that were only in memory.
        directories = {root}
        for key in sizes:
            directories.update(p for p in (root / key).parents if p == root or root in p.parents)
        for directory in sorted(directories, key=lambda p: len(p.parts), reverse=True):
            fsync_dir(directory)
    check()
    return {"inventory_sha256": sha(encode(rows)), "files": len(rows),
            "bytes": sum(row["size"] for row in rows.values())}


def run_command(argv, *, timeout, check=lambda: None):
    """Cancellable process group, including rsync's ssh child; no shell."""
    check()
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    end = time.monotonic() + timeout
    try:
        while True:
            check()
            remaining = end - time.monotonic()
            require(remaining > 0, "command deadline exceeded")
            try:
                stdout, stderr = process.communicate(timeout=min(0.2, remaining))
                check()
                return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                continue
    finally:
        # A direct child can exit while its ssh grandchild still owns pipes.
        # Kill the group even when poll() already reports that parent's exit.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()


@dataclass
class Client:
    record: Path
    manifest: str
    manifest_sha256: str
    armed_state: Path
    watchdog_state: Path
    terminal: str
    loop_lock: Path
    state_dir: Path
    host: str
    identity: Path
    known_hosts: Path
    budget_s: float
    transfer_mbps: float
    hash_mbps: float = 100.0
    overhead_s: float = 30.0
    bwlimit_kib: int = 0
    delete_policy: str = "after-two"
    min_free_bytes: int = 0
    deadline_margin_s: float = 5.0


def estimate_seconds(size, config):
    rate = config.transfer_mbps * 1_000_000
    if config.bwlimit_kib:
        rate = min(rate, config.bwlimit_kib * 1024)
    # Full transfer + two local verification passes, server verification and
    # rsync's sender/receiver checksum passes in the worst resumed case.
    # No resume discount: partial files are not already verified evidence.
    return size / rate + 5 * size / (config.hash_mbps * 1_000_000) + config.overhead_s


class Gate:
    def __init__(self, config, *, wall=time.time, monotonic=time.monotonic):
        self.config, self.wall, self.monotonic = config, wall, monotonic
        self.started = monotonic()
        self.deadline = self.started + config.budget_s
        self.generation = None
        self.check()

    def check(self):
        c = self.config
        gate = read_json(c.armed_state)
        watch = read_json(c.watchdog_state)
        require(watch.get("fenced_checkouts") == [], "watchdog has armed or unknown plans")
        require(gate.get("schema") == GATE_SCHEMA and gate.get("phase") == "cooldown"
                and gate.get("armed") is False and gate.get("measuring") is False,
                "magistrate is armed, measuring, outside cooldown or indeterminate")
        require(gate.get("record_manifest_sha256") == c.manifest_sha256, "gate record mismatch")
        require(gate.get("record_committed") is True and gate.get("record_pushed") is True,
                "record must be finalized, committed and pushed before offload")
        generation = gate.get("generation")
        require(isinstance(generation, str) and generation, "gate generation absent")
        if self.generation is None:
            self.generation = generation
            for key in ("quiet_dwell_epoch_s", "expires_epoch_s"):
                require(type(gate.get(key)) in (int, float) and math.isfinite(gate[key]), "bad gate deadline")
            seconds = min(gate["quiet_dwell_epoch_s"], gate["expires_epoch_s"]) - self.wall()
            self.deadline = min(self.deadline, self.monotonic() + seconds - c.deadline_margin_s)
        require(generation == self.generation, "magistrate lease changed")
        require(self.wall() < min(gate["quiet_dwell_epoch_s"], gate["expires_epoch_s"])
                and self.monotonic() < self.deadline, "cooldown budget/dwell deadline exceeded")

    def remaining(self):
        self.check()
        return self.deadline - self.monotonic()


def terminal_check(record, name):
    path = record / relative(name)
    result = read_json(path)
    require(isinstance(result.get("plan_id"), str) and result["plan_id"], "terminal plan absent")
    require(result.get("verdict") in {"GO", "ABORTED", "COLLECTED", "CHAIN_STOPPED", "REFUSED"}
            and type(result.get("ended_epoch_s")) in (int, float)
            and math.isfinite(result["ended_epoch_s"]) and result["ended_epoch_s"] <= time.time(),
            "record is not terminal")
    with directory_fd(path.parent) as night:
        def present(name):
            try:
                info = os.stat(name, dir_fd=night, follow_symlinks=False)
            except FileNotFoundError:
                return False
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "nonregular terminal marker")
            return True
        # A chain without a proven exit, or an unkillable child, always refuses.
        require(not present("chain.unkilled"), "terminal chain has unproven survivors")
        started, exited = present("chain.started"), present("chain.exited")
        require((started and exited) or (not started and not exited and result["verdict"] == "REFUSED"
                and result.get("chain_exit_code") is None and result.get("chain_sha256") is None),
                "terminal chain is open or ambiguous")
        require(present("courier.sent"), "terminal courier not completed")


def ssh_args(c):
    require(re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]*", c.host or ""), "invalid SSH host alias")
    for path in (c.identity, c.known_hosts):
        require(plain_path(path).is_file(), "SSH identity/known_hosts absent")
    return ["ssh", "-F", "/dev/null", "-i", str(c.identity), "-o", "IdentitiesOnly=yes",
            "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o",
            f"UserKnownHostsFile={c.known_hosts}", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=2"]


def validate_receipt(value, c, challenge, summary=None):
    require(set(value) == {"receipt", "sha256"}, "partial receipt envelope")
    receipt = value["receipt"]
    require(isinstance(receipt, dict) and sha(encode(receipt)) == value["sha256"], "receipt hash mismatch")
    require(receipt.get("schema") == RECEIPT_SCHEMA and receipt.get("record_id") == c.manifest_sha256
            and receipt.get("manifest") == c.manifest and receipt.get("challenge") == challenge,
            "receipt identity/challenge mismatch")
    require(type(receipt.get("verified_epoch_s")) in (int, float)
            and math.isfinite(receipt["verified_epoch_s"]), "receipt verification time absent")
    if summary is not None:
        require(receipt.get("summary") == summary, "receipt inventory mismatch")
    copies = receipt.get("copies")
    require(isinstance(copies, list) and 1 <= len(copies) <= 2, "receipt has no verified copy")
    devices = set()
    for copy in copies:
        require(isinstance(copy, dict) and copy.get("verified") is True
                and isinstance(copy.get("device"), str) and copy["device"]
                and copy.get("inventory_sha256") == receipt["summary"]["inventory_sha256"],
                "partial/unverified copy receipt")
        require(copy["device"] not in devices, "copies share a device")
        devices.add(copy["device"])
    require(receipt.get("backup_status") == ("confirmed" if len(copies) == 2 else "queued"),
            "backup status does not match verified copies")
    return receipt


def offload(c, *, runner=run_command, wall=time.time, monotonic=time.monotonic,
            disk_usage=shutil.disk_usage):
    start = monotonic()
    require(all(math.isfinite(v) and v > 0 for v in (c.budget_s, c.transfer_mbps, c.hash_mbps))
            and math.isfinite(c.overhead_s) and c.overhead_s >= 0 and c.bwlimit_kib >= 0,
            "invalid budget/rate")
    require(c.delete_policy in {"after-two", "pressure", "never"}
            and c.min_free_bytes >= 0 and math.isfinite(c.deadline_margin_s)
            and c.deadline_margin_s >= 0, "invalid deletion policy/margin")
    require(HEX.fullmatch(c.manifest_sha256 or "") and NAME.fullmatch(c.manifest or ""), "bad manifest identity")
    c.record = plain_path(c.record)
    c.state_dir = plain_path(c.state_dir)
    require(c.state_dir != c.record and c.record not in c.state_dir.parents,
            "state directory must be outside record")
    require(plain_path(c.loop_lock) != c.record and c.record not in plain_path(c.loop_lock).parents,
            "loop lock must be outside record")
    gate = Gate(c, wall=wall, monotonic=monotonic)
    with lock(c.loop_lock), lock(c.state_dir / (c.manifest_sha256 + ".lock")), budget_alarm(gate.remaining()):
        gate.check()
        journal_path = c.state_dir / (c.manifest_sha256 + ".json")
        journal = read_json(journal_path) if journal_path.exists() else {}
        require(not journal or (journal.get("record") == str(c.record) and
                journal.get("manifest_sha256") == c.manifest_sha256 and journal.get("host") == c.host),
                "journal identity mismatch")
        if not c.record.exists():
            require(journal.get("action") in {"deleting", "deleted"}, "record absent without deletion journal")
            return {"status": "already-deleted", "elapsed_s": monotonic() - start,
                    "hold_next_window": disk_usage(c.record.parent).free < c.min_free_bytes}
        resuming_delete = journal.get("action") == "deleting"
        sizes = files(c.record, gate.check)
        size = sum(sizes.values()) if not resuming_delete else journal["summary"]["bytes"]
        estimated = estimate_seconds(size, c)
        require(estimated < gate.remaining(), f"estimated {estimated:.1f}s exceeds cooldown budget")
        if resuming_delete:
            # The journal's authenticated inventory survives even if the
            # manifest was removed by an interrupted deletion.
            rows = journal["entries"]
            require(set(sizes) <= set(rows), "new files during deletion recovery")
            for key, length in sizes.items():
                require(length == rows[key]["size"] and file_sha(c.record / key, gate.check) == rows[key]["sha256"],
                        "changed file during deletion recovery")
            summary = journal["summary"]
        else:
            terminal_check(c.record, c.terminal)
            summary = inspect_record(c.record, c.manifest, c.manifest_sha256, check=gate.check)
        ssh = ssh_args(c)

        def remote(verb):
            challenge = secrets.token_hex(16)
            command = f"jw-air {verb} {c.manifest_sha256} {c.manifest} {challenge}"
            result = runner([*ssh, c.host, command], timeout=gate.remaining(), check=gate.check)
            require(result.returncode == 0, "Air verification/transport failed")
            value = decode(result.stdout)
            if value == {"status": "absent"}:
                return None
            return validate_receipt(value, c, challenge, summary)

        receipt = remote("status")
        if receipt is None:
            require(not resuming_delete, "Air copy missing during deletion recovery")
            require(estimated - size / (c.hash_mbps * 1_000_000) < gate.remaining(),
                    "remaining transfer estimate exceeds cooldown budget")
            command = ["rsync", "-rt", "--checksum", "--partial", "--partial-dir=.rsync-partial",
                       "--no-links", "--timeout=15"]
            if c.bwlimit_kib:
                command += [f"--bwlimit={c.bwlimit_kib}"]
            command += ["-e", shlex.join(ssh), "--", str(c.record) + "/",
                        f"{c.host}:{c.manifest_sha256}/"]
            result = runner(command, timeout=gate.remaining(), check=gate.check)
            require(result.returncode == 0, "copy interrupted/failed; local record retained")
            receipt = remote("verify")
            require(receipt is not None, "Air did not publish a verified receipt")
        gate.check()
        if not resuming_delete:
            require(inspect_record(c.record, c.manifest, c.manifest_sha256, check=gate.check) == summary,
                    "local record changed after copy")
        may_delete = len(receipt["copies"]) == 2 and c.delete_policy != "never"
        if c.delete_policy == "pressure":
            may_delete = may_delete and disk_usage(c.record.parent).free < c.min_free_bytes
        require(not resuming_delete or may_delete, "deletion recovery needs two copies and deletion policy")
        journal = {"record": str(c.record), "manifest_sha256": c.manifest_sha256, "host": c.host,
                   "summary": summary, "receipt": receipt,
                   "action": "deleting" if may_delete else "retained",
                   "entries": journal["entries"] if resuming_delete else manifest_entries(c.record, c.manifest, c.manifest_sha256)}
        save(journal_path, journal)
        if may_delete:
            # Validate all remaining bytes BEFORE removing any. Never rmtree
            # another root, and never follow even an in-record symlink.
            gate.check()
            for name in files(c.record, gate.check):
                gate.check()
                target = c.record / name
                with directory_fd(target.parent) as parent:
                    os.unlink(target.name, dir_fd=parent)
            remove_empty_record(c.record, gate.check)
            fsync_dir(c.record.parent)
            journal["action"] = "deleted"
            save(journal_path, journal)
        pressure = disk_usage(c.record.parent).free < c.min_free_bytes
        return {"status": journal["action"], "copies": len(receipt["copies"]),
                "hold_next_window": pressure,
                "estimated_s": estimated, "elapsed_s": monotonic() - start,
                "receipt": receipt}


def layout(root):
    root = plain_path(root)
    require(root.is_dir(), "Air root absent (is SSD mounted?)")
    for name in ("incoming", "records", "receipts", "jobs", "locks"):
        path = plain_path(root / name)
        path.mkdir(exist_ok=True)
    return root


def envelope(receipt):
    return {"receipt": receipt, "sha256": sha(encode(receipt))}


def air_verify(root, record_id, manifest, challenge, *, backup_root=None, status_only=False):
    root = layout(root)
    require(HEX.fullmatch(record_id or "") and NAME.fullmatch(manifest or "")
            and re.fullmatch(r"[0-9a-f]{32}", challenge or ""), "invalid receiver request")
    with lock(root / "locks" / (record_id + ".lock")):
        destination = root / "records" / record_id
        if not destination.exists():
            if status_only:
                return {"status": "absent"}
            stage = plain_path(root / "incoming" / record_id)
            summary = inspect_record(stage, manifest, record_id, durable=True)
            stage.rename(destination)
            fsync_dir(destination.parent)
            fsync_dir(stage.parent)
        else:
            summary = inspect_record(destination, manifest, record_id, durable=True)
        copies = [{"device": device_id(destination), "verified": True,
                   "inventory_sha256": summary["inventory_sha256"]}]
        job = root / "jobs" / (record_id + ".json")
        confirmed = False
        if backup_root is not None:
            backup_root = plain_path(backup_root)
            backup = plain_path(backup_root / "records" / record_id)
            # A queued job or a local iCloud placeholder is never confirmation.
            if job.exists() and read_json(job).get("status") == "confirmed":
                require(backup_root.is_dir() and device_id(backup_root) != device_id(root),
                        "second copy is not on an independent mounted filesystem")
                require(inspect_record(backup, manifest, record_id, durable=True) == summary,
                        "second copy digest mismatch")
                copies.append({"device": device_id(backup), "verified": True,
                               "inventory_sha256": summary["inventory_sha256"]})
                confirmed = True
        if not confirmed:
            save(job, {"record_id": record_id, "manifest": manifest, "status": "queued"})
        receipt = {"schema": RECEIPT_SCHEMA, "record_id": record_id, "manifest": manifest,
                   "summary": summary, "copies": copies,
                   "backup_status": "confirmed" if confirmed else "queued",
                   "challenge": challenge, "verified_epoch_s": time.time()}
        result = envelope(receipt)
        save(root / "receipts" / (record_id + ".json"), result)
        return result


def backup_once(root, backup_root, *, runner=run_command, timeout_s=3600):
    """Air-only background worker. A different filesystem is mandatory."""
    root, backup_root = layout(root), layout(backup_root)
    require(device_id(root) != device_id(backup_root),
            "backup must be on an independent mounted filesystem")
    completed = []
    for job_path in sorted((root / "jobs").iterdir()):
        if job_path.suffix != ".json":
            continue  # an interrupted atomic save's temporary is not a job
        require(NAME.fullmatch(job_path.name), "invalid job name")
        job = read_json(job_path)
        record_id, manifest = job.get("record_id"), job.get("manifest")
        require(HEX.fullmatch(record_id or "") and job_path.name == record_id + ".json"
                and NAME.fullmatch(manifest or ""), "invalid backup job")
        if job.get("status") == "confirmed":
            continue
        with lock(root / "locks" / (record_id + ".lock")):
            source = plain_path(root / "records" / record_id)
            summary = inspect_record(source, manifest, record_id)
            target = plain_path(backup_root / "records" / record_id)
            if not target.exists():
                stage = plain_path(backup_root / "incoming" / record_id)
                stage.mkdir(exist_ok=True)
                result = runner(["rsync", "-rt", "--checksum", "--partial", "--no-links",
                                 "--", str(source) + "/", str(stage) + "/"], timeout=timeout_s)
                require(result.returncode == 0, "second-disk copy interrupted")
                require(inspect_record(stage, manifest, record_id, durable=True) == summary,
                        "second-disk copy mismatch")
                stage.rename(target)
                fsync_dir(stage.parent)
                fsync_dir(target.parent)
            require(inspect_record(target, manifest, record_id, durable=True) == summary,
                    "second-disk digest mismatch")
            save(job_path, {**job, "status": "confirmed", "summary": summary,
                            "confirmed_epoch_s": time.time()})
            completed.append(record_id)
    return completed


def serve(root, backup_root, rrsync, original, *, exec_fn=os.execv):
    """Forced-command dispatcher. No arbitrary executable or shell evaluation."""
    words = shlex.split(original)
    if words[:2] == ["rsync", "--server"]:
        root = layout(root)
        # rrsync validates the entire rsync server grammar and confines writes
        # to incoming/. It cannot touch records/, receipts/, jobs/ or backups.
        executable = str(plain_path(rrsync))
        # Inherit stdin/stdout: these carry the bidirectional rsync protocol.
        # Capturing output through run_command would deadlock the transport.
        exec_fn(executable, [executable, "-wo", "-no-del", str(root / "incoming")])
        return 0, None  # only reached by an injected test exec
    require(len(words) == 5 and words[:1] == ["jw-air"] and words[1] in {"verify", "status"},
            "forced command refused")
    return 0, air_verify(root, words[2], words[3], words[4], backup_root=backup_root,
                         status_only=words[1] == "status")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    push = sub.add_parser("push")
    for flag in ("record", "armed-state", "watchdog-state", "loop-lock", "state-dir", "identity", "known-hosts"):
        push.add_argument("--" + flag, type=Path, required=True)
    push.add_argument("--manifest", default="ssd-closed.json")
    for flag in ("manifest-sha256", "terminal", "host"):
        push.add_argument("--" + flag, required=True)
    for flag in ("budget-s", "transfer-mbps"):
        push.add_argument("--" + flag, type=float, required=True)
    push.add_argument("--hash-mbps", type=float, default=100)
    push.add_argument("--overhead-s", type=float, default=30)
    push.add_argument("--bwlimit-kib", type=int, default=0)
    push.add_argument("--delete-policy", choices=("after-two", "pressure", "never"), default="after-two")
    push.add_argument("--min-free-bytes", type=int, default=0)
    push.add_argument("--deadline-margin-s", type=float, default=5)
    for mode in ("serve", "backup-once"):
        child = sub.add_parser(mode)
        child.add_argument("--root", type=Path, required=True)
        child.add_argument("--backup-root", type=Path, required=mode == "backup-once")
        if mode == "serve":
            child.add_argument("--rrsync", type=Path, required=True)
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        if args.mode == "push":
            values = vars(args).copy()
            values.pop("mode")
            result = offload(Client(**values))
        elif args.mode == "backup-once":
            result = {"confirmed": backup_once(args.root, args.backup_root)}
        else:
            code, result = serve(args.root, args.backup_root, args.rrsync,
                                 os.environ.get("SSH_ORIGINAL_COMMAND", ""))
            if result is None:
                return code
        print(encode(result).decode(), end="")
        return 0
    except (Refusal, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(encode({"status": "refused", "reason": str(error),
                      "elapsed_s": time.monotonic() - started}).decode(), file=sys.stderr, end="")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
